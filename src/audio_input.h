#ifndef AUDIO_INPUT_H
#define AUDIO_INPUT_H

#include <Arduino.h>
#include <vector>
#include "config.h"

// ============================================================================
// Audio Filter Classes - Advanced Signal Processing (2025)
// ============================================================================

// High-pass filter for DC blocking and bass frequency focus
class HighPassFilter {
public:
    HighPassFilter(float cutoff_hz = 20.0f, float sample_rate = SAMPLE_RATE);
    float process(float input);

private:
    float alpha_;      // Filter coefficient
    float prev_input_; // Previous input sample
    float prev_output_; // Previous output sample
};

// Band-pass filter for bass frequency range (40-200 Hz for BPM detection)
class BassBandPassFilter {
public:
    BassBandPassFilter(float sample_rate = SAMPLE_RATE);
    float process(float input);

private:
    // 2nd order Butterworth band-pass coefficients for 40-200 Hz at 25kHz
    float b0_, b1_, b2_; // Feedforward coefficients
    float a1_, a2_;      // Feedback coefficients
    float x1_, x2_;      // Input history
    float y1_, y2_;      // Output history
};

// DC blocker using proper IIR filter (better than simple high-pass)
class DCBlocker {
public:
    DCBlocker(float pole = 0.995f);
    float process(float input);

private:
    float pole_;     // Filter pole (closer to 1 = sharper cutoff)
    float x1_;       // Previous input
    float y1_;       // Previous output
};

class AudioInput {
public:
    AudioInput();
    ~AudioInput();

    // Initialize ADC with specified pin (mono)
    void begin(uint8_t adc_pin);

    // Initialize ADC with stereo pins
    void beginStereo(uint8_t left_pin, uint8_t right_pin);

    // Read a single sample from ADC (mono or combined stereo)
    float readSample();

    // Read separate stereo samples
    void readStereoSamples(float& left, float& right);

    // Get current signal level (RMS or peak)
    float getSignalLevel() const;

    // Get normalized signal level (0.0-1.0)
    float getNormalizedLevel() const;

    // Check if audio input is initialized
    bool isInitialized() const;

    // Reset signal level calibration
    void resetCalibration();

private:
    uint8_t adc_pin_;
    uint8_t adc_pin_right_;
    bool initialized_;
    bool stereo_mode_;
    
    // Signal level tracking
    float signal_level_;
    float max_signal_;
    float min_signal_;
    
    // RMS calculation
    static constexpr size_t RMS_BUFFER_SIZE = 100;
    std::vector<float> rms_buffer_;
    size_t rms_index_;

    // Audio filters for signal conditioning
    HighPassFilter high_pass_filter_;
    BassBandPassFilter bass_filter_;
    DCBlocker dc_blocker_;

    // Internal methods
    void updateSignalLevel(float sample);
    float calculateRMS() const;
};

#endif // AUDIO_INPUT_H


