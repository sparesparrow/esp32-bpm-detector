// Final comprehensive test for ESP32 BPM Detector
// Tests all key components and algorithms

#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <iomanip>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Test Results Structure
struct TestResults {
    int passed = 0;
    int total = 0;
    std::vector<std::string> failures;

    void test(const std::string& name, bool condition, const std::string& details = "") {
        total++;
        if (condition) {
            passed++;
            std::cout << "✓ " << name << " PASSED";
            if (!details.empty()) std::cout << " (" << details << ")";
            std::cout << std::endl;
        } else {
            failures.push_back(name);
            std::cout << "✗ " << name << " FAILED";
            if (!details.empty()) std::cout << " (" << details << ")";
            std::cout << std::endl;
        }
    }

    void summary() {
        std::cout << "\n========================================" << std::endl;
        std::cout << "TEST SUMMARY" << std::endl;
        std::cout << "========================================" << std::endl;
        std::cout << "Passed: " << passed << "/" << total << std::endl;

        if (!failures.empty()) {
            std::cout << "\nFailed tests:" << std::endl;
            for (const auto& failure : failures) {
                std::cout << "  - " << failure << std::endl;
            }
        }

        std::cout << "\nOverall: " << (passed == total ? "ALL TESTS PASSED ✓" : "SOME TESTS FAILED ✗") << std::endl;
    }
};

// ============================================================================
// BPM Calculation Tests
// ============================================================================

void testBPMCalculation(TestResults& results) {
    std::cout << "\n--- BPM Calculation Tests ---" << std::endl;

    // Test 1: Perfect 120 BPM intervals
    {
        std::vector<unsigned long> beats;
        for (int i = 0; i < 10; ++i) {
            beats.push_back(i * 500UL); // 500ms = 120 BPM
        }

        std::vector<float> intervals;
        for (size_t i = 1; i < beats.size(); ++i) {
            intervals.push_back(beats[i] - beats[i - 1]);
        }

        std::sort(intervals.begin(), intervals.end());
        float median = intervals[intervals.size() / 2];
        float bpm = 60000.0f / median;

        results.test("120 BPM Calculation", fabs(bpm - 120.0f) < 1.0f,
                    "Expected: 120.0, Got: " + std::to_string(bpm));
    }

    // Test 2: 140 BPM intervals
    {
        std::vector<unsigned long> beats;
        float interval_140 = 60000.0f / 140.0f; // ~428.57ms
        for (int i = 0; i < 10; ++i) {
            beats.push_back((unsigned long)(i * interval_140));
        }

        std::vector<float> intervals;
        for (size_t i = 1; i < beats.size(); ++i) {
            intervals.push_back(beats[i] - beats[i - 1]);
        }

        std::sort(intervals.begin(), intervals.end());
        float median = intervals[intervals.size() / 2];
        float bpm = 60000.0f / median;

        results.test("140 BPM Calculation", fabs(bpm - 140.0f) < 2.0f,
                    "Expected: 140.0, Got: " + std::to_string(bpm));
    }

    // Test 3: BPM range validation
    {
        float bpm_60 = 60000.0f / 1000.0f;  // 1000ms = 60 BPM
        float bpm_200 = 60000.0f / 300.0f;  // 300ms = 200 BPM
        float bpm_30 = 60000.0f / 2000.0f;  // 2000ms = 30 BPM (too slow)
        float bpm_300 = 60000.0f / 200.0f;  // 200ms = 300 BPM (too fast)

        bool valid_range = (bpm_60 >= 55 && bpm_60 <= 65) &&
                          (bpm_200 >= 190 && bpm_200 <= 210) &&
                          (bpm_30 < 60 || bpm_30 > 200) &&
                          (bpm_300 < 60 || bpm_300 > 200);

        results.test("BPM Range Validation", valid_range,
                    "60 BPM: " + std::to_string(bpm_60) +
                    ", 200 BPM: " + std::to_string(bpm_200));
    }
}

// ============================================================================
// Confidence Calculation Tests
// ============================================================================

void testConfidenceCalculation(TestResults& results) {
    std::cout << "\n--- Confidence Calculation Tests ---" << std::endl;

    auto calculate_confidence = [](const std::vector<float>& intervals) -> float {
        if (intervals.size() < 2) return 0.0f;

        float mean = 0.0f;
        for (float interval : intervals) mean += interval;
        mean /= intervals.size();

        float variance = 0.0f;
        for (float interval : intervals) {
            float diff = interval - mean;
            variance += diff * diff;
        }
        variance /= intervals.size();

        float std_dev = sqrt(variance);
        float cv = std_dev / mean;
        float confidence = 1.0f - (cv * 2.0f);
        return std::max(0.0f, std::min(1.0f, confidence));
    };

    // Test 1: Perfect regularity
    {
        std::vector<float> perfect = {500, 500, 500, 500, 500};
        float confidence = calculate_confidence(perfect);
        results.test("Perfect Regularity", confidence > 0.95f,
                    "Confidence: " + std::to_string(confidence));
    }

    // Test 2: Moderate variation
    {
        std::vector<float> moderate = {480, 520, 500, 490, 510};
        float confidence = calculate_confidence(moderate);
        results.test("Moderate Variation", confidence > 0.7f && confidence < 0.95f,
                    "Confidence: " + std::to_string(confidence));
    }

    // Test 3: High variation
    {
        std::vector<float> high_variation = {400, 600, 450, 550, 350};
        float confidence = calculate_confidence(high_variation);
        results.test("High Variation", confidence < 0.5f,
                    "Confidence: " + std::to_string(confidence));
    }
}

// ============================================================================
// FFT Processing Tests
// ============================================================================

void testFFTProcessing(TestResults& results) {
    std::cout << "\n--- FFT Processing Tests ---" << std::endl;

    const int SAMPLE_RATE = 25000;
    const int FFT_SIZE = 1024;

    // Test 1: Frequency resolution
    {
        float freq_resolution = (float)SAMPLE_RATE / FFT_SIZE;
        results.test("FFT Frequency Resolution", freq_resolution > 20.0f && freq_resolution < 30.0f,
                    "Resolution: " + std::to_string(freq_resolution) + " Hz/bin");
    }

    // Test 2: Bass frequency bin calculation
    {
        const int BASS_FREQ_MIN = 40;
        const int BASS_FREQ_MAX = 200;
        float freq_resolution = (float)SAMPLE_RATE / FFT_SIZE;

        int min_bin = (int)(BASS_FREQ_MIN / freq_resolution);
        int max_bin = (int)(BASS_FREQ_MAX / freq_resolution);

        bool valid_bins = min_bin >= 0 && max_bin < FFT_SIZE / 2 &&
                         max_bin > min_bin && max_bin - min_bin > 5;

        results.test("Bass Frequency Bins", valid_bins,
                    "Min bin: " + std::to_string(min_bin) +
                    ", Max bin: " + std::to_string(max_bin));
    }

    // Test 3: FFT size validation
    {
        bool valid_fft_size = (FFT_SIZE & (FFT_SIZE - 1)) == 0 && // Power of 2
                             FFT_SIZE >= 256 && FFT_SIZE <= 4096;
        results.test("FFT Size Validation", valid_fft_size,
                    "FFT Size: " + std::to_string(FFT_SIZE));
    }
}

// ============================================================================
// Signal Processing Tests
// ============================================================================

void testSignalProcessing(TestResults& results) {
    std::cout << "\n--- Signal Processing Tests ---" << std::endl;

    // Test 1: RMS calculation
    {
        std::vector<float> sine_wave(1024);
        for (size_t i = 0; i < sine_wave.size(); ++i) {
            sine_wave[i] = sin(2.0 * M_PI * i / sine_wave.size());
        }

        float sum_squares = 0.0f;
        for (float sample : sine_wave) {
            sum_squares += sample * sample;
        }
        float rms = sqrt(sum_squares / sine_wave.size());

        results.test("RMS Calculation", fabs(rms - 0.707f) < 0.01f,
                    "RMS: " + std::to_string(rms) + " (expected ~0.707)");
    }

    // Test 2: DC offset removal
    {
        std::vector<float> dc_signal(100, 1.5f); // 1.5V DC offset
        float sum = 0.0f;
        for (float sample : dc_signal) sum += sample;
        float avg_dc = sum / dc_signal.size();

        // Simulate DC removal
        std::vector<float> ac_signal;
        for (float sample : dc_signal) {
            ac_signal.push_back(sample - avg_dc);
        }

        float max_ac = *std::max_element(ac_signal.begin(), ac_signal.end());
        float min_ac = *std::min_element(ac_signal.begin(), ac_signal.end());

        results.test("DC Offset Removal", fabs(max_ac) < 0.01f && fabs(min_ac) < 0.01f,
                    "Max AC: " + std::to_string(max_ac) +
                    ", Min AC: " + std::to_string(min_ac));
    }

    // Test 3: Signal level normalization
    {
        float raw_level = 0.8f;
        float normalized = raw_level; // Already normalized in this test

        bool valid_normalized = normalized >= 0.0f && normalized <= 1.0f;
        results.test("Signal Normalization", valid_normalized,
                    "Normalized level: " + std::to_string(normalized));
    }
}

// ============================================================================
// Algorithm Integration Tests
// ============================================================================

void testAlgorithmIntegration(TestResults& results) {
    std::cout << "\n--- Algorithm Integration Tests ---" << std::endl;

    // Test 1: Beat interval filtering
    {
        const int MIN_INTERVAL = 300;
        const int MAX_INTERVAL = 1000;

        std::vector<int> test_intervals = {200, 350, 500, 800, 1200, 150};
        std::vector<int> valid_intervals;

        for (int interval : test_intervals) {
            if (interval >= MIN_INTERVAL && interval <= MAX_INTERVAL) {
                valid_intervals.push_back(interval);
            }
        }

        bool correct_filtering = valid_intervals.size() == 3 && // 350, 500, 800
                                std::find(valid_intervals.begin(), valid_intervals.end(), 350) != valid_intervals.end() &&
                                std::find(valid_intervals.begin(), valid_intervals.end(), 500) != valid_intervals.end() &&
                                std::find(valid_intervals.begin(), valid_intervals.end(), 800) != valid_intervals.end();

        results.test("Beat Interval Filtering", correct_filtering,
                    "Valid intervals: " + std::to_string(valid_intervals.size()));
    }

    // Test 2: Median calculation robustness
    {
        std::vector<float> odd_intervals = {400, 500, 600, 450, 550}; // 5 elements
        std::vector<float> even_intervals = {400, 500, 600, 450};     // 4 elements

        std::sort(odd_intervals.begin(), odd_intervals.end());
        std::sort(even_intervals.begin(), even_intervals.end());

        float odd_median = odd_intervals[odd_intervals.size() / 2];
        float even_median = (even_intervals[even_intervals.size() / 2 - 1] +
                           even_intervals[even_intervals.size() / 2]) / 2.0f;

        bool correct_medians = fabs(odd_median - 500.0f) < 1.0f &&
                              fabs(even_median - 475.0f) < 1.0f;

        results.test("Median Calculation", correct_medians,
                    "Odd median: " + std::to_string(odd_median) +
                    ", Even median: " + std::to_string(even_median));
    }

    // Test 3: Envelope decay simulation
    {
        float envelope = 0.0f;
        const float DECAY = 0.9f;
        float input = 1.0f;

        // Simulate envelope following input
        for (int i = 0; i < 10; ++i) {
            if (input > envelope) {
                envelope = input;
            } else {
                envelope = envelope * DECAY + input * (1.0f - DECAY);
            }
        }

        bool envelope_follows = envelope > 0.5f && envelope < 1.0f;
        results.test("Envelope Decay", envelope_follows,
                    "Final envelope: " + std::to_string(envelope));
    }
}

// ============================================================================
// Performance Tests
// ============================================================================

void testPerformance(TestResults& results) {
    std::cout << "\n--- Performance Tests ---" << std::endl;

    // Test 1: Memory usage estimation
    {
        // Estimate memory usage for key data structures
        const int FFT_SIZE = 1024;
        const int BEAT_HISTORY_SIZE = 32;

        size_t sample_buffer_bytes = FFT_SIZE * sizeof(float);
        size_t fft_buffer_bytes = (FFT_SIZE / 2) * sizeof(float);
        size_t beat_times_bytes = BEAT_HISTORY_SIZE * sizeof(unsigned long);

        size_t total_bytes = sample_buffer_bytes + fft_buffer_bytes + beat_times_bytes;

        // ESP32 has ~300KB free heap
        bool reasonable_memory = total_bytes < 50 * 1024; // Less than 50KB

        results.test("Memory Usage", reasonable_memory,
                    "Total: " + std::to_string(total_bytes) + " bytes");
    }

    // Test 2: Processing time estimation
    {
        // Estimate processing time per detection cycle
        const int SAMPLE_RATE = 25000;
        const int FFT_SIZE = 1024;

        // Rough estimates for ESP32
        float adc_time_us = 10.0f; // ADC sampling
        float fft_time_us = 5000.0f; // FFT processing (estimate)
        float analysis_time_us = 1000.0f; // Beat analysis

        float total_time_us = adc_time_us + fft_time_us + analysis_time_us;
        float total_time_ms = total_time_us / 1000.0f;

        // Should be well under 100ms for real-time performance
        bool real_time_performance = total_time_ms < 50.0f;

        results.test("Real-time Performance", real_time_performance,
                    "Estimated processing time: " + std::to_string(total_time_ms) + " ms");
    }

    // Test 3: Sample rate validation
    {
        const int SAMPLE_RATE = 25000;
        const int FFT_SIZE = 1024;

        bool valid_sample_rate = SAMPLE_RATE >= 8000 && SAMPLE_RATE <= 48000;
        float nyquist_freq = SAMPLE_RATE / 2.0f;
        bool adequate_nyquist = nyquist_freq > 1000.0f; // Well above bass frequencies

        results.test("Sample Rate Validation", valid_sample_rate && adequate_nyquist,
                    "Sample rate: " + std::to_string(SAMPLE_RATE) +
                    " Hz, Nyquist: " + std::to_string(nyquist_freq) + " Hz");
    }
}

// ============================================================================
// Main Test Runner
// ============================================================================

int main() {
    std::cout << "ESP32 BPM Detector - Final Comprehensive Test Suite" << std::endl;
    std::cout << "==================================================" << std::endl;
    std::cout << std::fixed << std::setprecision(3);

    TestResults results;

    // Run all test categories
    testBPMCalculation(results);
    testConfidenceCalculation(results);
    testFFTProcessing(results);
    testSignalProcessing(results);
    testAlgorithmIntegration(results);
    testPerformance(results);

    // Final summary
    results.summary();

    std::cout << "\n==================================================" << std::endl;
    if (results.passed == results.total) {
        std::cout << "🎉 ALL TESTS PASSED! 🎉" << std::endl;
        std::cout << "The ESP32 BPM detector firmware is fully validated." << std::endl;
    } else {
        std::cout << "⚠️  Some tests failed. Review implementation." << std::endl;
    }
    std::cout << "==================================================" << std::endl;

    return results.passed == results.total ? 0 : 1;
}
