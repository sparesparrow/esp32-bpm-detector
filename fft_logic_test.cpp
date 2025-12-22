// Simplified FFT Logic Test
// This demonstrates the core BPM detection logic without ESP32 dependencies

#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <numeric>

// Define M_PI if not available
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define SAMPLE_RATE 25000
#define FFT_SIZE 1024
#define MIN_BPM 60
#define MAX_BPM 200
#define BASS_FREQ_MIN 40
#define BASS_FREQ_MAX 200
#define ENVELOPE_DECAY 0.9
#define DETECTION_THRESHOLD 0.5

// Simplified FFT implementation (just for testing the logic)
class SimpleFFT {
private:
    std::vector<double> vReal;
    std::vector<double> vImag;

public:
    SimpleFFT(size_t size) {
        vReal.resize(size, 0.0);
        vImag.resize(size, 0.0);
    }

    void setReal(size_t index, double value) {
        if (index < vReal.size()) {
            vReal[index] = value;
        }
    }

    // Simplified FFT - just copy real to magnitude for testing
    void computeMagnitude(std::vector<float>& magnitude) {
        magnitude.resize(vReal.size() / 2);
        for (size_t i = 0; i < magnitude.size(); ++i) {
            // Simulate FFT magnitude (in reality this would be sqrt(real^2 + imag^2))
            magnitude[i] = std::abs(vReal[i]);
        }
    }
};

// Simplified BPM Detector for testing
class TestBPMDetector {
private:
    size_t sample_rate_;
    size_t fft_size_;
    std::vector<float> sample_buffer_;
    std::vector<float> fft_buffer_;
    float envelope_value_;
    float envelope_threshold_;
    std::vector<unsigned long> beat_times_;

public:
    TestBPMDetector(size_t sample_rate = SAMPLE_RATE, size_t fft_size = FFT_SIZE)
        : sample_rate_(sample_rate), fft_size_(fft_size),
          envelope_value_(0.0f), envelope_threshold_(DETECTION_THRESHOLD)
    {
        sample_buffer_.resize(fft_size_, 0.0f);
        fft_buffer_.resize(fft_size_ / 2, 0.0f);
        beat_times_.reserve(32);
    }

    void addSample(float value) {
        // Circular buffer: shift left and add new value at end
        for (size_t i = 0; i < fft_size_ - 1; ++i) {
            sample_buffer_[i] = sample_buffer_[i + 1];
        }
        sample_buffer_[fft_size_ - 1] = value;
    }

    bool isBufferReady() const {
        return true; // Assume buffer is always ready for testing
    }

    void performFFT() {
        SimpleFFT fft(fft_size_);

        // Copy samples to FFT
        for (size_t i = 0; i < fft_size_; ++i) {
            fft.setReal(i, sample_buffer_[i]);
        }

        // Compute magnitude
        fft.computeMagnitude(fft_buffer_);
    }

    void detectBeatEnvelope() {
        // Calculate bass energy from FFT
        float bass_energy = 0.0f;

        // Frequency resolution: sample_rate / fft_size
        float freq_resolution = (float)sample_rate_ / fft_size_;

        // Find FFT bins corresponding to bass frequencies (40-200 Hz)
        size_t min_bin = (size_t)(BASS_FREQ_MIN / freq_resolution);
        size_t max_bin = (size_t)(BASS_FREQ_MAX / freq_resolution);

        // Clamp to valid range
        if (min_bin >= fft_size_ / 2) min_bin = 0;
        if (max_bin >= fft_size_ / 2) max_bin = fft_size_ / 2 - 1;

        // Sum energy in bass frequency range
        for (size_t i = min_bin; i <= max_bin; ++i) {
            bass_energy += fft_buffer_[i];
        }

        // Normalize by number of bins
        bass_energy /= (max_bin - min_bin + 1);

        // Update envelope with decay/release
        if (bass_energy > envelope_value_) {
            // Attack: fast rise
            envelope_value_ = bass_energy;
        } else {
            // Decay/Release: exponential decay
            envelope_value_ = envelope_value_ * ENVELOPE_DECAY + bass_energy * (1.0f - ENVELOPE_DECAY);
        }

        // Adaptive threshold
        envelope_threshold_ = DETECTION_THRESHOLD * 0.5f;

        // Detect beat (rising edge crossing threshold)
        static float prev_envelope = 0.0f;

        if (envelope_value_ > envelope_threshold_ && prev_envelope <= envelope_threshold_) {
            // Check minimum beat interval (300ms)
            if (beat_times_.empty() || (simulated_time_ms - beat_times_.back()) >= 300) {
                beat_times_.push_back(simulated_time_ms);

                // Keep only recent beats
                if (beat_times_.size() > 32) {
                    beat_times_.erase(beat_times_.begin());
                }

                // Only print first few beats to avoid spam
                if (beat_times_.size() <= 3) {
                    std::cout << "Beat detected at " << simulated_time_ms
                             << "ms, envelope: " << envelope_value_ << std::endl;
                }
            }
        }

        prev_envelope = envelope_value_;
    }

    float calculateBPM() {
        if (beat_times_.size() < 2) {
            return 0.0f;
        }

        // Calculate intervals between beats
        std::vector<float> intervals;
        intervals.reserve(beat_times_.size() - 1);

        for (size_t i = 1; i < beat_times_.size(); ++i) {
            float interval_ms = beat_times_[i] - beat_times_[i - 1];
            if (interval_ms >= 300 && interval_ms <= 1000) { // 60-200 BPM range
                intervals.push_back(interval_ms);
            }
        }

        if (intervals.empty()) {
            return 0.0f;
        }

        // Calculate median interval
        std::sort(intervals.begin(), intervals.end());
        float median_interval;
        if (intervals.size() % 2 == 0) {
            median_interval = (intervals[intervals.size() / 2 - 1] + intervals[intervals.size() / 2]) / 2.0f;
        } else {
            median_interval = intervals[intervals.size() / 2];
        }

        // Convert interval (ms) to BPM: BPM = 60000 / interval_ms
        float bpm = 60000.0f / median_interval;

        // Clamp to valid range
        if (bpm < MIN_BPM) bpm = 0.0f;
        if (bpm > MAX_BPM) bpm = 0.0f;

        return bpm;
    }

    float calculateConfidence() {
        if (beat_times_.size() < 3) {
            return 0.0f;
        }

        // Calculate intervals
        std::vector<float> intervals;
        intervals.reserve(beat_times_.size() - 1);

        for (size_t i = 1; i < beat_times_.size(); ++i) {
            float interval_ms = beat_times_[i] - beat_times_[i - 1];
            if (interval_ms >= 300 && interval_ms <= 1000) {
                intervals.push_back(interval_ms);
            }
        }

        if (intervals.empty()) {
            return 0.0f;
        }

        // Calculate coefficient of variation (std dev / mean)
        float sum = 0.0f;
        for (float interval : intervals) {
            sum += interval;
        }
        float mean = sum / intervals.size();

        if (mean < 1.0f) {
            return 0.0f;
        }

        float variance = 0.0f;
        for (float interval : intervals) {
            float diff = interval - mean;
            variance += diff * diff;
        }
        variance /= intervals.size();
        float std_dev = sqrtf(variance);

        // Coefficient of variation
        float cv = std_dev / mean;

        // Convert to confidence (0.0-1.0)
        float confidence = 1.0f - (cv * 2.0f);
        if (confidence < 0.0f) confidence = 0.0f;
        if (confidence > 1.0f) confidence = 1.0f;

        return confidence;
    }

    // Generate test signal - discrete beats at specified BPM
    void generateTestBeats(float bpm, size_t total_samples) {
        // Convert BPM to interval in samples
        float beats_per_second = bpm / 60.0f;
        float interval_samples = sample_rate_ / beats_per_second;

        size_t current_sample = 0;

        while (current_sample < total_samples) {
            // Generate a beat (short pulse)
            if (fmod(current_sample, interval_samples) < sample_rate_ * 0.01f) { // 10ms pulse
                addSample(1.0f); // High amplitude for beat
            } else {
                addSample(0.0f); // Silence between beats
            }
            current_sample++;
        }
    }

    // Generate continuous sine wave (for frequency testing)
    void generateTestSignal(float frequency_hz, size_t num_samples) {
        float phase = 0.0f;
        float phase_increment = 2.0f * (float)M_PI * frequency_hz / sample_rate_;

        for (size_t i = 0; i < num_samples; ++i) {
            float sample = sinf(phase);
            addSample(sample);
            phase += phase_increment;

            if (phase > 2.0f * (float)M_PI) {
                phase -= 2.0f * (float)M_PI;
            }
        }
    }

    // Simulate time for beat detection
    unsigned long simulated_time_ms = 0;

    // Test the BPM calculation directly with known beat intervals
    void testBPMCalculation() {
        std::cout << "Testing BPM Calculation Logic" << std::endl;
        std::cout << "==============================" << std::endl;

        // Test Case 1: Perfect 120 BPM (500ms intervals)
        std::cout << "Test Case 1: Perfect 120 BPM (500ms intervals)" << std::endl;
        beat_times_.clear();
        for (int i = 0; i < 10; ++i) {
            beat_times_.push_back(i * 500); // 500ms intervals = 120 BPM
        }

        float bpm1 = calculateBPM();
        float confidence1 = calculateConfidence();
        std::cout << "Expected: 120 BPM, Detected: " << bpm1 << " BPM, Confidence: " << confidence1 << std::endl;

        // Test Case 2: 140 BPM (428.57ms intervals)
        std::cout << "Test Case 2: 140 BPM (428.57ms intervals)" << std::endl;
        beat_times_.clear();
        for (int i = 0; i < 10; ++i) {
            beat_times_.push_back((unsigned long)(i * 428.57f)); // 140 BPM intervals
        }

        float bpm2 = calculateBPM();
        float confidence2 = calculateConfidence();
        std::cout << "Expected: 140 BPM, Detected: " << bpm2 << " BPM, Confidence: " << confidence2 << std::endl;

        // Test Case 3: Irregular intervals (mixed 120 and 140 BPM)
        std::cout << "Test Case 3: Irregular intervals (mixed BPM)" << std::endl;
        beat_times_.clear();
        beat_times_.push_back(0);
        beat_times_.push_back(500);   // 120 BPM
        beat_times_.push_back(928);   // 140 BPM
        beat_times_.push_back(1428);  // 140 BPM
        beat_times_.push_back(1928);  // 140 BPM

        float bpm3 = calculateBPM();
        float confidence3 = calculateConfidence();
        std::cout << "Expected: ~133 BPM, Detected: " << bpm3 << " BPM, Confidence: " << confidence3 << std::endl;

        // Evaluate results
        std::cout << std::endl << "Results Summary:" << std::endl;
        bool test1_pass = std::abs(bpm1 - 120.0f) < 5.0f && confidence1 > 0.8f;
        bool test2_pass = std::abs(bpm2 - 140.0f) < 5.0f && confidence2 > 0.8f;
        bool test3_pass = bpm3 > 125.0f && bpm3 < 145.0f && confidence3 > 0.3f; // Lower confidence for irregular

        std::cout << "Test 1 (120 BPM): " << (test1_pass ? "PASS" : "FAIL") << std::endl;
        std::cout << "Test 2 (140 BPM): " << (test2_pass ? "PASS" : "FAIL") << std::endl;
        std::cout << "Test 3 (Mixed): " << (test3_pass ? "PASS" : "FAIL") << std::endl;

        if (test1_pass && test2_pass && test3_pass) {
            std::cout << std::endl << "RESULT: ALL TESTS PASS - BPM calculation logic is working correctly!" << std::endl;
        } else {
            std::cout << std::endl << "RESULT: SOME TESTS FAILED - BPM calculation needs debugging" << std::endl;
        }
    }

    // Test the detector (simplified version)
    void testDetector() {
        std::cout << "Testing BPM Detector Logic" << std::endl;
        std::cout << "==========================" << std::endl;
        std::cout << "Sample Rate: " << sample_rate_ << " Hz" << std::endl;
        std::cout << "FFT Size: " << fft_size_ << std::endl;
        std::cout << "BPM Range: " << MIN_BPM << " - " << MAX_BPM << " BPM" << std::endl;
        std::cout << std::endl;

        testBPMCalculation();
    }
};

int main() {
    std::cout << "FFT Logic Test for ESP32 BPM Detector" << std::endl;
    std::cout << "=====================================" << std::endl;

    TestBPMDetector detector;
    detector.testDetector();

    std::cout << std::endl;
    std::cout << "Test completed." << std::endl;

    return 0;
}
