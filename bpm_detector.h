#ifndef BPM_DETECTOR_H
#define BPM_DETECTOR_H

#include <Arduino.h>
#include <vector>

class BPMDetector {
public:
    struct BPMData {
        float bpm;
        float confidence;
        float signal_level;
        String status;
        unsigned long timestamp;
    };

    BPMDetector(uint16_t sample_rate = 25000, uint16_t fft_size = 1024);
    ~BPMDetector();

    // Initialize audio sampling
    void begin(uint8_t adc_pin);
    void beginStereo(uint8_t left_pin, uint8_t right_pin);
    
    // Read audio sample from ADC
    void sample();
    
    // Process samples and detect BPM
    BPMData detect();
    
    // Set BPM detection parameters
    void setMinBPM(float min_bpm);
    void setMaxBPM(float max_bpm);
    void setThreshold(float threshold);
    
    // Get current settings
    float getMinBPM() const;
    float getMaxBPM() const;
    
    // Test mode methods
    void enableTestMode(float frequency_hz);
    void disableTestMode();
    
private:
    uint16_t sample_rate_;
    uint16_t fft_size_;
    uint8_t adc_pin_;
    uint8_t adc_pin_right_;

    float min_bpm_;
    float max_bpm_;
    float detection_threshold_;
    
    std::vector<float> sample_buffer_;
    std::vector<float> fft_buffer_;
    
    float envelope_value_;
    float envelope_threshold_;
    std::vector<unsigned long> beat_times_;
    
    // Internal helper methods
    void performFFT();
    void detectBeatEnvelope();
    float calculateBPM();
    float calculateConfidence();
    
    // Circular buffer management
    void addSample(float value);
    bool isBufferReady() const;
    
    // Test mode
    bool test_mode_;
    float test_frequency_;
    float test_phase_;
    float generateTestSample();
};

#endif // BPM_DETECTOR_H
