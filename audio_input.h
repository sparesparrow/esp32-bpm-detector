#ifndef AUDIO_INPUT_H
#define AUDIO_INPUT_H

#include <Arduino.h>
#include <vector>
#include "config.h"

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
    
    // Internal methods
    void updateSignalLevel(float sample);
    float calculateRMS() const;
};

#endif // AUDIO_INPUT_H


