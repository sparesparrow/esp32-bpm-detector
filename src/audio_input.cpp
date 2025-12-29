#include "audio_input.h"
#include <numeric>

#ifdef ESP32
#include <esp_adc_cal.h>
#include <driver/adc.h>

// ADC calibration data (optional, improves accuracy)
static esp_adc_cal_characteristics_t* adc_chars = nullptr;
#endif

AudioInput::AudioInput()
    : adc_pin_(0)
    , adc_pin_right_(0)
    , initialized_(false)
    , stereo_mode_(false)
    , signal_level_(0.0f)
    , max_signal_(0.0f)
    , min_signal_(4095.0f)
    , rms_index_(0)
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
        else if (adc_pin_ == 9) left_channel = ADC1_CHANNEL_8;
        else if (adc_pin_ == 10) left_channel = ADC1_CHANNEL_9;
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
            else if (adc_pin_right_ == 9) right_channel = ADC1_CHANNEL_8;
            else if (adc_pin_right_ == 10) right_channel = ADC1_CHANNEL_9;
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
    if (!initialized_) {
        return 0.0f;
    }

    // Read raw ADC value (0-4095 for 12-bit)
    int raw_value = analogRead(adc_pin_);

    // Validate ADC reading
    if (raw_value < 0 || raw_value > 4095) {
        raw_value = 2048; // Use midpoint as fallback
    }

    // Convert to voltage (0.0-3.6V for ADC_ATTEN_DB_11)
    float voltage = (raw_value / 4095.0f) * 3.6f;

    // Center around 0 (AC coupling - remove DC offset)
    static float dc_offset = 1.5f;  // Will adapt over time
    float ac_signal = voltage - dc_offset;

    // Update DC offset estimation (slow adaptation)
    dc_offset = dc_offset * 0.999f + voltage * 0.001f;

    // Update signal level tracking
    updateSignalLevel(ac_signal);

    return ac_signal;
}

[[maybe_unused]] void AudioInput::readStereoSamples(float& left, float& right) {
    if (!initialized_ || !stereo_mode_) {
        left = right = 0.0f;
        return;
    }

    // Read left channel
    int left_raw = analogRead(adc_pin_);
    float left_voltage = (left_raw / 4095.0f) * 3.6f;

    // Read right channel
    int right_raw = analogRead(adc_pin_right_);
    float right_voltage = (right_raw / 4095.0f) * 3.6f;

    // Apply DC offset removal (separate for each channel)
    static float left_dc_offset = 1.5f;
    static float right_dc_offset = 1.5f;

    left = left_voltage - left_dc_offset;
    right = right_voltage - right_dc_offset;

    // Update DC offset estimation
    left_dc_offset = left_dc_offset * 0.999f + left_voltage * 0.001f;
    right_dc_offset = right_dc_offset * 0.999f + right_voltage * 0.001f;

    // Update signal level tracking (use combined RMS for now)
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