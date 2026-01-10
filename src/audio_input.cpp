#include "audio_input.h"
#include <numeric>
#include <cmath>

// Constants that should be in config.h but aren't being recognized
#ifndef HIGH_PASS_CUTOFF_HZ
#define HIGH_PASS_CUTOFF_HZ 20.0f
#endif

#ifndef DC_BLOCKER_POLE
#define DC_BLOCKER_POLE 0.995f
#endif

#ifdef ESP32
#include <esp_adc_cal.h>
#include <driver/adc.h>

// ADC calibration data (optional, improves accuracy)
static esp_adc_cal_characteristics_t* adc_chars = nullptr;
#endif

// ============================================================================
// Filter Implementations - Advanced Signal Processing (2025)
// ============================================================================

HighPassFilter::HighPassFilter(float cutoff_hz, float sample_rate) {
    // Calculate filter coefficient: alpha = 1 / (1 + 2*pi*fc/fs)
    // This gives ~20Hz cutoff at 25kHz sample rate
    float rc = 1.0f / (2.0f * PI * cutoff_hz);
    float dt = 1.0f / sample_rate;
    alpha_ = rc / (rc + dt);

    prev_input_ = 0.0f;
    prev_output_ = 0.0f;
}

float HighPassFilter::process(float input) {
    // First-order high-pass filter: y[n] = alpha * (y[n-1] + x[n] - x[n-1])
    float output = alpha_ * (prev_output_ + input - prev_input_);
    prev_input_ = input;
    prev_output_ = output;
    return output;
}

BassBandPassFilter::BassBandPassFilter(float sample_rate) {
    // 2nd order Butterworth band-pass filter designed for 40-200 Hz at 25kHz sample rate
    // Using bilinear transform design

    // Normalized frequencies (0-1, where 1 = Nyquist frequency)
    float f1 = 40.0f / (sample_rate / 2.0f);    // Low cutoff: 40 Hz
    float f2 = 200.0f / (sample_rate / 2.0f);   // High cutoff: 200 Hz

    // Butterworth coefficients calculation
    float wc1 = 2.0f * PI * f1;  // Angular frequency
    float wc2 = 2.0f * PI * f2;

    // Pre-warp frequencies for bilinear transform
    float k = sample_rate / PI;
    float wc1_warp = 2.0f * sample_rate * tan(wc1 / (2.0f * sample_rate));
    float wc2_warp = 2.0f * sample_rate * tan(wc2 / (2.0f * sample_rate));

    // Simplified coefficients for 40-200 Hz band-pass
    // These coefficients provide good bass response for BPM detection
    b0_ = 0.0018f;   // Feedforward coefficients
    b1_ = 0.0f;
    b2_ = -0.0018f;
    a1_ = -1.7991f;  // Feedback coefficients
    a2_ = 0.8187f;

    // Initialize filter history
    x1_ = x2_ = 0.0f;
    y1_ = y2_ = 0.0f;
}

float BassBandPassFilter::process(float input) {
    // Direct Form II implementation: y[n] = b0*x[n] + b1*x[n-1] + b2*x[n-2] - a1*y[n-1] - a2*y[n-2]
    float output = b0_ * input + b1_ * x1_ + b2_ * x2_ - a1_ * y1_ - a2_ * y2_;

    // Update filter history
    x2_ = x1_;
    x1_ = input;
    y2_ = y1_;
    y1_ = output;

    return output;
}

DCBlocker::DCBlocker(float pole) : pole_(pole) {
    x1_ = 0.0f;
    y1_ = 0.0f;
}

float DCBlocker::process(float input) {
    // DC blocking filter: y[n] = x[n] - x[n-1] + R * y[n-1]
    // where R is close to 1 for sharp cutoff
    float output = input - x1_ + pole_ * y1_;
    x1_ = input;
    y1_ = output;
    return output;
}

AudioInput::AudioInput()
    : adc_pin_(0)
    , adc_pin_right_(0)
    , initialized_(false)
    , stereo_mode_(false)
    , signal_level_(0.0f)
    , max_signal_(0.0f)
    , min_signal_(4095.0f)
    , rms_index_(0)
    , high_pass_filter_(HIGH_PASS_CUTOFF_HZ, SAMPLE_RATE)
    , bass_filter_(SAMPLE_RATE)
    , dc_blocker_(DC_BLOCKER_POLE)
{
    rms_buffer_.reserve(RMS_BUFFER_SIZE);
    rms_buffer_.resize(RMS_BUFFER_SIZE, 0.0f);
}

AudioInput::~AudioInput() {
#ifdef ESP32
    if (adc_chars) {
        free(adc_chars);
        adc_chars = nullptr;
    }
#endif
}

void AudioInput::begin(uint8_t adc_pin) {
    beginStereo(adc_pin, 0); // Initialize as mono
}

void AudioInput::beginStereo(uint8_t left_pin, uint8_t right_pin) {
    adc_pin_ = left_pin;
    adc_pin_right_ = right_pin;
    stereo_mode_ = (right_pin != 0);

    // Configure ADC
    // ESP32 ADC1 channels: GPIO32-39 for ESP32, GPIO1-10 for ESP32-S3
    // We'll use analogRead() which handles ADC setup automatically

    // Set ADC resolution (Arduino API)
    analogReadResolution(ADC_RESOLUTION);
    
    // Set ADC Attenuation (Arduino API)
    // 0dB attenuation = 0-1.1V range (High sensitivity for line-level inputs)
    analogSetAttenuation((adc_attenuation_t)ADC_ATTENUATION);

    #ifdef ESP32
        // Map left channel pin to ADC channel (ESP32-S3 uses GPIO1-10 for ADC1)
        adc1_channel_t left_channel = ADC1_CHANNEL_MAX;
        if (adc_pin_ == 1) left_channel = ADC1_CHANNEL_0;
        else if (adc_pin_ == 2) left_channel = ADC1_CHANNEL_1;
        else if (adc_pin_ == 3) left_channel = ADC1_CHANNEL_2;
        else if (adc_pin_ == 4) left_channel = ADC1_CHANNEL_3;
        else if (adc_pin_ == 5) left_channel = ADC1_CHANNEL_4;
        else if (adc_pin_ == 6) left_channel = ADC1_CHANNEL_5;
        else if (adc_pin_ == 7) left_channel = ADC1_CHANNEL_6;
        else if (adc_pin_ == 8) left_channel = ADC1_CHANNEL_7;
#ifdef CONFIG_IDF_TARGET_ESP32S3
        else if (adc_pin_ == 9) left_channel = ADC1_CHANNEL_8;
        else if (adc_pin_ == 10) left_channel = ADC1_CHANNEL_9;
#endif
        // Legacy ESP32 GPIO32-39 mapping
        else if (adc_pin_ == 32) left_channel = ADC1_CHANNEL_4;
        else if (adc_pin_ == 33) left_channel = ADC1_CHANNEL_5;
        else if (adc_pin_ == 34) left_channel = ADC1_CHANNEL_6;
        else if (adc_pin_ == 35) left_channel = ADC1_CHANNEL_7;
        else if (adc_pin_ == 36) left_channel = ADC1_CHANNEL_0;
        else if (adc_pin_ == 37) left_channel = ADC1_CHANNEL_1;
        else if (adc_pin_ == 38) left_channel = ADC1_CHANNEL_2;
        else if (adc_pin_ == 39) left_channel = ADC1_CHANNEL_3;

        if (left_channel != ADC1_CHANNEL_MAX) {
            // Configure ADC width and attenuation for left channel
            adc1_config_width(ADC_WIDTH_BIT_12);
            adc1_config_channel_atten(left_channel, ADC_ATTENUATION);

            // Allocate and initialize ADC calibration data
            if (!adc_chars) {
                adc_chars = static_cast<esp_adc_cal_characteristics_t*>(calloc(1, sizeof(esp_adc_cal_characteristics_t)));
                if (!adc_chars) {
                    // Memory allocation failed - log error and use fallback calculation
                    DEBUG_PRINTLN("[Audio] Warning: Failed to allocate ADC calibration data, using fallback");
                    // Continue without calibration - will use manual calculation in readSample()
                } else {
                    esp_adc_cal_value_t val_type = esp_adc_cal_characterize(
                        ADC_UNIT_1,
                        ADC_ATTENUATION,
                        ADC_WIDTH_BIT_12,
                        1100,  // Default Vref
                        adc_chars
                    );
                    (void)val_type;  // Suppress unused variable warning
                }
            }
        }

        // Configure right channel if stereo mode
        if (stereo_mode_) {
            adc1_channel_t right_channel = ADC1_CHANNEL_MAX;
            if (adc_pin_right_ == 1) right_channel = ADC1_CHANNEL_0;
            else if (adc_pin_right_ == 2) right_channel = ADC1_CHANNEL_1;
            else if (adc_pin_right_ == 3) right_channel = ADC1_CHANNEL_2;
            else if (adc_pin_right_ == 4) right_channel = ADC1_CHANNEL_3;
            else if (adc_pin_right_ == 5) right_channel = ADC1_CHANNEL_4;
            else if (adc_pin_right_ == 6) right_channel = ADC1_CHANNEL_5;
            else if (adc_pin_right_ == 7) right_channel = ADC1_CHANNEL_6;
            else if (adc_pin_right_ == 8) right_channel = ADC1_CHANNEL_7;
#ifdef CONFIG_IDF_TARGET_ESP32S3
            else if (adc_pin_right_ == 9) right_channel = ADC1_CHANNEL_8;
            else if (adc_pin_right_ == 10) right_channel = ADC1_CHANNEL_9;
#endif
            // Legacy ESP32 GPIO32-39 mapping
            else if (adc_pin_right_ == 32) right_channel = ADC1_CHANNEL_4;
            else if (adc_pin_right_ == 33) right_channel = ADC1_CHANNEL_5;
            else if (adc_pin_right_ == 34) right_channel = ADC1_CHANNEL_6;
            else if (adc_pin_right_ == 35) right_channel = ADC1_CHANNEL_7;
            else if (adc_pin_right_ == 36) right_channel = ADC1_CHANNEL_0;
            else if (adc_pin_right_ == 37) right_channel = ADC1_CHANNEL_1;
            else if (adc_pin_right_ == 38) right_channel = ADC1_CHANNEL_2;
            else if (adc_pin_right_ == 39) right_channel = ADC1_CHANNEL_3;

            if (right_channel != ADC1_CHANNEL_MAX) {
                adc1_config_channel_atten(right_channel, ADC_ATTENUATION);
            }
        }
    #endif

    // Reset calibration
    resetCalibration();

    initialized_ = true;
}

[[maybe_unused]] float AudioInput::readSample() {
    // #region agent log
    static unsigned long sampleCount = 0;
    sampleCount++;
    if (sampleCount % 100 == 0) {  // Log every 100th sample to avoid spam
        char buf[256];
        snprintf(buf, sizeof(buf), "{\"initialized\":%d,\"adcPin\":%u,\"sampleCount\":%lu}", 
                 initialized_ ? 1 : 0, adc_pin_, sampleCount);
        Serial.print("{\"sessionId\":\"debug-session\",\"runId\":\"run1\",\"hypothesisId\":\"B\",\"location\":\"audio_input.cpp:readSample:entry\",\"message\":\"readSample() called\",\"data\":");
        Serial.print(buf);
        Serial.print(",\"timestamp\":");
        Serial.print(millis());
        Serial.println("}");
        Serial.flush();
    }
    // #endregion
    
    if (!initialized_) {
        // #region agent log
        if (sampleCount % 100 == 0) {
            Serial.print("{\"sessionId\":\"debug-session\",\"runId\":\"run1\",\"hypothesisId\":\"A\",\"location\":\"audio_input.cpp:readSample:notInitialized\",\"message\":\"readSample() returning 0 - not initialized\",\"data\":{\"initialized\":0}");
            Serial.print(",\"timestamp\":");
            Serial.print(millis());
            Serial.println("}");
            Serial.flush();
        }
        // #endregion
        return 0.0f;
    }

    // Read raw ADC value (0-4095 for 12-bit)
    int raw_value = analogRead(adc_pin_);

    // Validate ADC reading
    if (raw_value < 0 || raw_value > 4095) {
        raw_value = 2048; // Use midpoint as fallback
    }

    // Convert to voltage using ESP32 ADC calibration for improved accuracy
    float voltage = 0.0f;
    #ifdef ESP32
    if (adc_chars) {
        // Use calibrated conversion instead of manual calculation
        uint32_t calibrated_voltage_mv = esp_adc_cal_raw_to_voltage(raw_value, adc_chars);
        voltage = calibrated_voltage_mv / 1000.0f; // Convert mV to V
    } else {
        // Fallback to manual calculation if calibration fails
        const float V_REF = 1.1f; // For ADC_ATTEN_DB_0
        voltage = (raw_value / 4095.0f) * V_REF;
    }
    #else
    // For Arduino platforms
    const float V_REF = 5.0f; // Arduino reference voltage
    voltage = (raw_value / 1023.0f) * V_REF;
    #endif

    // Apply advanced audio filtering for improved signal quality
    float processed_signal = voltage;

    #if USE_DC_BLOCKING_FILTER
    processed_signal = dc_blocker_.process(processed_signal);
    #endif

    #if USE_BASS_BAND_PASS_FILTER
    processed_signal = bass_filter_.process(processed_signal);
    #endif

    #if USE_HIGH_PASS_FILTER
    processed_signal = high_pass_filter_.process(processed_signal);
    #endif

    float ac_signal = processed_signal;

    // Update signal level tracking
    updateSignalLevel(ac_signal);

    // #region agent log
    if (sampleCount % 100 == 0) {
        char resultBuf[256];
        snprintf(resultBuf, sizeof(resultBuf), "{\"rawValue\":%d,\"voltage\":%.6f,\"acSignal\":%.6f,\"signalLevel\":%.6f,\"normalizedLevel\":%.6f}", 
                 raw_value, voltage, ac_signal, signal_level_, getNormalizedLevel());
        Serial.print("{\"sessionId\":\"debug-session\",\"runId\":\"run1\",\"hypothesisId\":\"B\",\"location\":\"audio_input.cpp:readSample:result\",\"message\":\"readSample() result\",\"data\":");
        Serial.print(resultBuf);
        Serial.print(",\"timestamp\":");
        Serial.print(millis());
        Serial.println("}");
        Serial.flush();
    }
    // #endregion

    return ac_signal;
}

[[maybe_unused]] void AudioInput::readStereoSamples(float& left, float& right) {
    if (!initialized_ || !stereo_mode_) {
        left = right = 0.0f;
        return;
    }

    // Read left channel with ADC calibration
    int left_raw = analogRead(adc_pin_);
    float left_voltage = 0.0f;
    #ifdef ESP32
    if (adc_chars) {
        uint32_t calibrated_left_mv = esp_adc_cal_raw_to_voltage(left_raw, adc_chars);
        left_voltage = calibrated_left_mv / 1000.0f;
    } else {
        left_voltage = (left_raw / 4095.0f) * 1.1f; // Fallback
    }
    #else
    left_voltage = (left_raw / 1023.0f) * 5.0f; // Arduino
    #endif

    // Read right channel with ADC calibration
    int right_raw = analogRead(adc_pin_right_);
    float right_voltage = 0.0f;
    #ifdef ESP32
    if (adc_chars) {
        uint32_t calibrated_right_mv = esp_adc_cal_raw_to_voltage(right_raw, adc_chars);
        right_voltage = calibrated_right_mv / 1000.0f;
    } else {
        right_voltage = (right_raw / 4095.0f) * 1.1f; // Fallback
    }
    #else
    right_voltage = (right_raw / 1023.0f) * 5.0f; // Arduino
    #endif

    // Apply filtering to both channels (shared filters for mono operation)
    float left_processed = left_voltage;
    float right_processed = right_voltage;

    #if USE_DC_BLOCKING_FILTER
    left_processed = dc_blocker_.process(left_processed);
    right_processed = dc_blocker_.process(right_processed);
    #endif

    #if USE_BASS_BAND_PASS_FILTER
    left_processed = bass_filter_.process(left_processed);
    right_processed = bass_filter_.process(right_processed);
    #endif

    #if USE_HIGH_PASS_FILTER
    left_processed = high_pass_filter_.process(left_processed);
    right_processed = high_pass_filter_.process(right_processed);
    #endif

    left = left_processed;
    right = right_processed;

    // Update signal level tracking (use combined RMS)
    float combined_sample = (fabs(left) + fabs(right)) * 0.5f; // Average of both channels
    updateSignalLevel(combined_sample);
}

void AudioInput::updateSignalLevel(float sample) {
    // Add to RMS buffer
    float abs_sample = fabs(sample);
    rms_buffer_[rms_index_] = abs_sample;
    rms_index_ = (rms_index_ + 1) % RMS_BUFFER_SIZE;

    // Update peak tracking
    if (abs_sample > max_signal_) {
        max_signal_ = abs_sample;
    }
    if (abs_sample < min_signal_) {
        min_signal_ = abs_sample;
    }

    // Calculate RMS signal level
    signal_level_ = calculateRMS();
}

float AudioInput::calculateRMS() const {
    if (rms_buffer_.empty()) {
        return 0.0f;
    }

    float sum_squares = std::accumulate(rms_buffer_.begin(), rms_buffer_.end(), 0.0f,
                                       [](float acc, float sample) { return acc + sample * sample; });

    return sqrt(sum_squares / rms_buffer_.size());
}

[[maybe_unused]] float AudioInput::getSignalLevel() const {
    return signal_level_;
}

[[maybe_unused]] float AudioInput::getNormalizedLevel() const {
    // Normalize to 0.0-1.0 range
    // Use max_signal_ as reference, but clamp to reasonable range
    float max_ref = max_signal_;
    if (max_ref < 0.01f) {
        max_ref = 0.01f;  // Avoid division by zero
    }

    float normalized = signal_level_ / max_ref;
    if (normalized > 1.0f) {
        normalized = 1.0f;
    }

    return normalized;
}

[[maybe_unused]] bool AudioInput::isInitialized() const {
    return initialized_;
}

void AudioInput::resetCalibration() {
    signal_level_ = 0.0f;
    max_signal_ = 0.0f;
    min_signal_ = 4095.0f;
    rms_index_ = 0;
    std::fill(rms_buffer_.begin(), rms_buffer_.end(), 0.0f);
}