#ifndef BPM_DETECTOR_H
#define BPM_DETECTOR_H

// Configuration must be included FIRST to define platform macros and constants
#include "config.h"

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

    explicit BPMDetector(uint16_t sample_rate = SAMPLE_RATE, uint16_t fft_size = FFT_SIZE);
    explicit BPMDetector(IAudioInput* audio_input, ITimer* timer, uint16_t sample_rate = SAMPLE_RATE, uint16_t fft_size = FFT_SIZE);
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

    // Performance monitoring (2025 optimization)
    #if ENABLE_PERFORMANCE_MONITORING
    struct PerformanceMetrics {
        unsigned long fft_compute_time_us;
        unsigned long total_detect_time_us;
        float average_fft_time_ms;
        size_t peak_memory_usage;
        uint32_t performance_sample_count;
    };
    PerformanceMetrics getPerformanceMetrics() const;
    #endif
    
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

    // Pre-allocated FFT working buffers for optimal performance
    #if FFT_PREALLOCATE_BUFFERS
    std::vector<double> fft_real_buffer_;
    std::vector<double> fft_imag_buffer_;
    #endif
#endif
#ifdef PLATFORM_ARDUINO
    // Arduino Uno has limited RAM (2KB), so use smaller fixed-size arrays
    static constexpr uint16_t MAX_SAMPLE_BUFFER = 512;  // Optimized to match ESP32 FFT_SIZE
    static constexpr uint16_t MAX_FFT_BUFFER = 256;     // Half size for magnitude data
    static constexpr uint16_t MAX_BEAT_TIMES = 16;      // Smaller history for Arduino
    float sample_buffer_[MAX_SAMPLE_BUFFER];
    float fft_buffer_[MAX_FFT_BUFFER];
    unsigned long beat_times_[MAX_BEAT_TIMES];
    uint8_t beat_times_count_;
#endif

    float envelope_value_;
    float envelope_threshold_;

    // Enhanced beat detection state (2025 optimization)
    float envelope_attack_rate_;        // Adaptive attack rate for envelope
    float envelope_release_rate_;       // Adaptive release rate for envelope
    unsigned long last_beat_time_;      // Last beat timestamp for adaptive debounce
    float current_tempo_estimate_;      // Running tempo estimate for adaptive behavior
    float beat_quality_history_;        // Running average of beat quality scores

    // Performance monitoring (2025 optimization)
    #if ENABLE_PERFORMANCE_MONITORING
    unsigned long fft_compute_time_us_;     // Last FFT computation time
    unsigned long total_detect_time_us_;    // Last full detect() call time
    size_t peak_memory_usage_;             // Peak memory usage tracking
    float average_fft_time_ms_;            // Running average FFT time
    uint32_t performance_sample_count_;    // Number of performance samples
    #endif

    // Buffer fill tracking
    uint32_t samples_added_;  // Track how many samples have been added (buffer pre-allocated with zeros)

    // Audio input management
    IAudioInput* audio_input_;
    ITimer* timer_;
    bool owns_audio_input_;
    
    // Internal helper methods
    void performFFT();
    void detectBeatEnvelope();
    void detectBeatBasic();              // Original beat detection
    void detectBeatAdvanced();           // Enhanced multi-criteria beat detection
    float calculateBPM();
    float calculateConfidence();

    // Spectral analysis methods (2025 optimization)
    float estimateBPMFromSpectrum();
    std::vector<std::pair<float, float>> findSpectralPeaks(float min_freq, float max_freq);
    float selectBestBPMCandidate(const std::vector<float>& candidates);
    float calculateHybridBPM(float temporal_bpm, float spectral_bpm, float temporal_confidence, float spectral_confidence);

    // Enhanced beat detection helpers (2025 optimization)
    unsigned long calculateAdaptiveDebounce();
    void updateTempoEstimate();
    
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
