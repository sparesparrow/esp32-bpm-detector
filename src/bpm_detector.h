#ifndef BPM_DETECTOR_H
#define BPM_DETECTOR_H

#include <Arduino.h>
#ifdef PLATFORM_ESP32
#include <vector>
#endif
#ifdef PLATFORM_ARDUINO
#include <stdint.h>  // For Arduino compatibility
#endif

// Interface includes
#include "interfaces/IAudioInput.h"
#include "interfaces/ITimer.h"

class BPMDetector {
public:
    struct BPMData {
        float bpm;
        float confidence;
        float signal_level;
        float quality;        //!< Signal quality indicator (0.0-1.0)
        String status;
        unsigned long timestamp;
    };

    explicit BPMDetector(uint16_t sample_rate = 25000, uint16_t fft_size = 1024);
    explicit BPMDetector(IAudioInput* audio_input, ITimer* timer, uint16_t sample_rate = 25000, uint16_t fft_size = 1024);
    ~BPMDetector();

    // Initialize audio sampling
    void begin(uint8_t adc_pin);
    void beginStereo(uint8_t left_pin, uint8_t right_pin);
    void begin(IAudioInput* audio_input, ITimer* timer, uint8_t adc_pin);
    
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
    
#ifdef PLATFORM_ESP32
    std::vector<float> sample_buffer_;
    std::vector<float> fft_buffer_;
    std::vector<unsigned long> beat_times_;
#endif
#ifdef PLATFORM_ARDUINO
    // Arduino Uno has limited RAM (2KB), so use smaller fixed-size arrays
    static constexpr uint16_t MAX_SAMPLE_BUFFER = 512;  // Smaller than ESP32's 1024
    static constexpr uint16_t MAX_FFT_BUFFER = 256;     // Half size for magnitude data
    static constexpr uint16_t MAX_BEAT_TIMES = 16;      // Smaller history
    float sample_buffer_[MAX_SAMPLE_BUFFER];
    float fft_buffer_[MAX_FFT_BUFFER];
    unsigned long beat_times_[MAX_BEAT_TIMES];
    uint8_t beat_times_count_;
#endif

    float envelope_value_;
    float envelope_threshold_;

    // Audio input management
    IAudioInput* audio_input_;
    ITimer* timer_;
    bool owns_audio_input_;
    
    // Internal helper methods
    void performFFT();
    void detectBeatEnvelope();
    float calculateBPM();
    float calculateConfidence();
    
    // Circular buffer management
    void addSample(float value);
public:
    bool isBufferReady() const;
    
    // Test mode
    bool test_mode_;
    float test_frequency_;
    float test_phase_;
    [[maybe_unused]] float generateTestSample();
};

#endif // BPM_DETECTOR_H
