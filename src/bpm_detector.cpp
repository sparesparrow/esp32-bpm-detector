#include "bpm_detector.h"
#include "config.h"
#include "audio_input.h"
#include <arduinoFFT.h>
#include <cmath>
#include <algorithm>
#include <cstdlib>

// Global audio input instance (will be initialized by begin())
static AudioInput* audio_input = nullptr;

BPMDetector::BPMDetector(uint16_t sample_rate, uint16_t fft_size)
    : sample_rate_(sample_rate)
    , fft_size_(fft_size)
    , adc_pin_(0)
    , adc_pin_right_(0)
    , min_bpm_(MIN_BPM)
    , max_bpm_(MAX_BPM)
    , detection_threshold_(DETECTION_THRESHOLD)
    , envelope_value_(0.0f)
    , envelope_threshold_(0.0f)
    , test_mode_(false)
    , test_frequency_(0.0f)
    , test_phase_(0.0f)
    , audio_input_(nullptr)
    , owns_audio_input_(false)
{
    // Pre-allocate buffers
    sample_buffer_.reserve(fft_size_);
    sample_buffer_.resize(fft_size_, 0.0f);

    // FFT buffer only needs half size for magnitude data
    fft_buffer_.reserve(fft_size_ / 2);
    fft_buffer_.resize(fft_size_ / 2, 0.0f);

    beat_times_.reserve(BEAT_HISTORY_SIZE);

    // Initialize envelope threshold
    envelope_threshold_ = detection_threshold_;
}

BPMDetector::~BPMDetector() {
    if (owns_audio_input_ && audio_input_) {
        delete audio_input_;
        audio_input_ = nullptr;
    }
}

void BPMDetector::begin(uint8_t adc_pin) {
    adc_pin_ = adc_pin;

    // Create audio input instance if not provided
    if (!audio_input_) {
        audio_input_ = new AudioInput();
        audio_input_->begin(adc_pin);
        owns_audio_input_ = true;
    } else {
        // If audio input was injected, initialize it with the pin
        audio_input_->begin(adc_pin);
    }
}

void BPMDetector::beginStereo(uint8_t left_pin, uint8_t right_pin) {
    adc_pin_ = left_pin;
    adc_pin_right_ = right_pin;

    // Create audio input instance if not provided
    if (!audio_input_) {
        audio_input_ = new AudioInput();
        audio_input_->beginStereo(left_pin, right_pin);
        owns_audio_input_ = true;
    } else {
        // If audio input was injected, initialize it with the pins
        audio_input_->beginStereo(left_pin, right_pin);
    }
}

void BPMDetector::begin(AudioInput* audio_input, uint8_t adc_pin) {
    audio_input_ = audio_input;
    owns_audio_input_ = false;
    adc_pin_ = adc_pin;

    if (audio_input_) {
        audio_input_->begin(adc_pin);
    }
}

void BPMDetector::sample() {
    if (!audio_input_ || !audio_input_->isInitialized()) {
        return;
    }

    // Read audio sample
    float sample = audio_input_->readSample();

    // Add to buffer
    addSample(sample);
}

void BPMDetector::addSample(float value) {
    // Shift buffer (FIFO)
    for (size_t i = 1; i < sample_buffer_.size(); ++i) {
        sample_buffer_[i - 1] = sample_buffer_[i];
    }
    sample_buffer_.back() = value;

    // Update envelope
    detectBeatEnvelope();
}

bool BPMDetector::isBufferReady() const {
    // Check if we have enough samples
    return sample_buffer_.size() >= fft_size_;
}

BPMDetector::BPMData BPMDetector::detect() {
    BPMData result;
    result.bpm = 0.0f;
    result.confidence = 0.0f;
    result.signal_level = audio_input_ ? audio_input_->getSignalLevel() : 0.0f;
    result.timestamp = millis();

    if (!isBufferReady()) {
        result.status = "Buffer not ready";
        return result;
    }

    // Perform FFT analysis
    performFFT();

    // Calculate BPM from spectral peaks
    result.bpm = calculateBPM();
    result.confidence = calculateConfidence();

    // Determine status
    if (result.confidence > 0.5f) {
        result.status = "Good detection";
    } else if (result.confidence > 0.2f) {
        result.status = "Weak signal";
    } else {
        result.status = "No reliable detection";
    }

    return result;
}

void BPMDetector::performFFT() {
    // Prepare data for FFT
    double* vReal = new double[fft_size_];
    double* vImag = new double[fft_size_];

    for (size_t i = 0; i < fft_size_; ++i) {
        vReal[i] = sample_buffer_[i];
        vImag[i] = 0.0;
    }

    // Create FFT object
    arduinoFFT FFT = arduinoFFT(vReal, vImag, fft_size_, sample_rate_);

    // Perform FFT
    FFT.Windowing(FFT_WIN_TYP_HAMMING, FFT_FORWARD);
    FFT.Compute(FFT_FORWARD);
    FFT.ComplexToMagnitude();

    // Extract magnitude data (only first half is useful)
    size_t half_size = fft_size_ / 2;
    fft_buffer_.resize(half_size);
    for (size_t i = 0; i < half_size; ++i) {
        fft_buffer_[i] = vReal[i];
    }

    // Clean up
    delete[] vReal;
    delete[] vImag;
}

void BPMDetector::detectBeatEnvelope() {
    // Simple envelope detection using RMS
    float current_level = audio_input_ ? audio_input_->getSignalLevel() : 0.0f;

    // Update envelope with smoothing
    envelope_value_ = envelope_value_ * 0.9f + current_level * 0.1f;

    // Check for beat (envelope exceeds threshold)
    if (envelope_value_ > envelope_threshold_) {
        unsigned long now = millis();

        // Add beat timestamp
        if (beat_times_.size() >= BEAT_HISTORY_SIZE) {
            beat_times_.erase(beat_times_.begin());
        }
        beat_times_.push_back(now);

        // Update threshold (adaptive)
        envelope_threshold_ = envelope_value_ * 0.7f;
    } else {
        // Gradually lower threshold when no beat detected
        envelope_threshold_ *= 0.999f;
    }
}

float BPMDetector::calculateBPM() {
    if (beat_times_.size() < 2) {
        return 0.0f;
    }

    // Calculate intervals between beats
    std::vector<float> intervals;
    for (size_t i = 1; i < beat_times_.size(); ++i) {
        float interval_ms = beat_times_[i] - beat_times_[i - 1];
        intervals.push_back(interval_ms);
    }

    if (intervals.empty()) {
        return 0.0f;
    }

    // Calculate median interval
    std::sort(intervals.begin(), intervals.end());
    float median_interval = intervals[intervals.size() / 2];

    // Convert to BPM: BPM = 60000 / interval_ms
    float bpm = 60000.0f / median_interval;

    // Clamp to valid range
    if (bpm < min_bpm_) bpm = min_bpm_;
    if (bpm > max_bpm_) bpm = max_bpm_;

    return bpm;
}

float BPMDetector::calculateConfidence() {
    if (beat_times_.size() < 3) {
        return 0.0f;
    }

    // Calculate variance in beat intervals
    std::vector<float> intervals;
    for (size_t i = 1; i < beat_times_.size(); ++i) {
        intervals.push_back(beat_times_[i] - beat_times_[i - 1]);
    }

    // Calculate mean
    float mean = 0.0f;
    for (float interval : intervals) {
        mean += interval;
    }
    mean /= intervals.size();

    // Calculate variance
    float variance = 0.0f;
    for (float interval : intervals) {
        float diff = interval - mean;
        variance += diff * diff;
    }
    variance /= intervals.size();

    // Calculate standard deviation
    float std_dev = sqrt(variance);

    // Confidence is inversely related to coefficient of variation
    float cv = std_dev / mean;
    float confidence = 1.0f / (1.0f + cv);

    return confidence;
}

void BPMDetector::setMinBPM(float min_bpm) {
    min_bpm_ = min_bpm;
}

void BPMDetector::setMaxBPM(float max_bpm) {
    max_bpm_ = max_bpm;
}

void BPMDetector::setThreshold(float threshold) {
    detection_threshold_ = threshold;
}

float BPMDetector::getMinBPM() const {
    return min_bpm_;
}

float BPMDetector::getMaxBPM() const {
    return max_bpm_;
}

void BPMDetector::enableTestMode(float frequency_hz) {
    test_mode_ = true;
    test_frequency_ = frequency_hz;
    test_phase_ = 0.0f;
}

void BPMDetector::disableTestMode() {
    test_mode_ = false;
}

float BPMDetector::generateTestSample() {
    if (!test_mode_) {
        return 0.0f;
    }

    // Generate sine wave at test frequency
    float sample = sin(test_phase_);
    test_phase_ += 2.0f * PI * test_frequency_ / sample_rate_;

    // Keep phase in reasonable range
    if (test_phase_ > 2.0f * PI) {
        test_phase_ -= 2.0f * PI;
    }

    return sample;
}