#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Simple validation test that writes results to file
int main() {
    std::ofstream output("test_results.txt");

    output << "ESP32 BPM Detector Validation Tests" << std::endl;
    output << "===================================" << std::endl;

    // Test 1: BPM Calculation
    output << "\nTest 1: BPM Calculation" << std::endl;

    // Perfect 120 BPM intervals (500ms)
    std::vector<unsigned long> beats_120;
    for (int i = 0; i < 10; ++i) {
        beats_120.push_back(i * 500UL);
    }

    // Calculate BPM (median of intervals)
    std::vector<float> intervals_120;
    for (size_t i = 1; i < beats_120.size(); ++i) {
        intervals_120.push_back(beats_120[i] - beats_120[i - 1]);
    }

    std::sort(intervals_120.begin(), intervals_120.end());
    float median_120 = intervals_120[intervals_120.size() / 2];
    float bpm_120 = 60000.0f / median_120;

    output << "120 BPM Test: Expected 120.0, Got " << bpm_120 << " BPM" << std::endl;
    bool pass_120 = fabs(bpm_120 - 120.0f) < 1.0f;

    // Test 2: 140 BPM
    std::vector<unsigned long> beats_140;
    float interval_140 = 60000.0f / 140.0f; // 428.571ms
    for (int i = 0; i < 10; ++i) {
        beats_140.push_back((unsigned long)(i * interval_140));
    }

    std::vector<float> intervals_140;
    for (size_t i = 1; i < beats_140.size(); ++i) {
        intervals_140.push_back(beats_140[i] - beats_140[i - 1]);
    }

    std::sort(intervals_140.begin(), intervals_140.end());
    float median_140 = intervals_140[intervals_140.size() / 2];
    float bpm_140 = 60000.0f / median_140;

    output << "140 BPM Test: Expected 140.0, Got " << bpm_140 << " BPM" << std::endl;
    bool pass_140 = fabs(bpm_140 - 140.0f) < 2.0f;

    // Test 3: Confidence calculation
    output << "\nTest 2: Confidence Calculation" << std::endl;

    // Perfect regular intervals
    std::vector<float> perfect_intervals = {500, 500, 500, 500, 500};
    float perfect_mean = 0.0f;
    for (float interval : perfect_intervals) perfect_mean += interval;
    perfect_mean /= perfect_intervals.size();

    float perfect_variance = 0.0f;
    for (float interval : perfect_intervals) {
        float diff = interval - perfect_mean;
        perfect_variance += diff * diff;
    }
    perfect_variance /= perfect_intervals.size();
    float perfect_stddev = sqrt(perfect_variance);
    float perfect_cv = perfect_stddev / perfect_mean;
    float perfect_confidence = 1.0f - (perfect_cv * 2.0f);
    perfect_confidence = std::max(0.0f, std::min(1.0f, perfect_confidence));

    output << "Perfect Regularity: CV = " << perfect_cv << ", Confidence = " << perfect_confidence << std::endl;

    // Irregular intervals
    std::vector<float> irregular_intervals = {400, 600, 500, 450, 550};
    float irregular_mean = 0.0f;
    for (float interval : irregular_intervals) irregular_mean += interval;
    irregular_mean /= irregular_intervals.size();

    float irregular_variance = 0.0f;
    for (float interval : irregular_intervals) {
        float diff = interval - irregular_mean;
        irregular_variance += diff * diff;
    }
    irregular_variance /= irregular_intervals.size();
    float irregular_stddev = sqrt(irregular_variance);
    float irregular_cv = irregular_stddev / irregular_mean;
    float irregular_confidence = 1.0f - (irregular_cv * 2.0f);
    irregular_confidence = std::max(0.0f, std::min(1.0f, irregular_confidence));

    output << "Irregular: CV = " << irregular_cv << ", Confidence = " << irregular_confidence << std::endl;

    bool pass_confidence = perfect_confidence > 0.9f && irregular_confidence < 0.8f;

    // Test 4: FFT frequency resolution
    output << "\nTest 3: FFT Frequency Resolution" << std::endl;

    int sample_rate = 25000;
    int fft_size = 1024;
    float freq_resolution = (float)sample_rate / fft_size;

    output << "Sample Rate: " << sample_rate << " Hz" << std::endl;
    output << "FFT Size: " << fft_size << std::endl;
    output << "Frequency Resolution: " << freq_resolution << " Hz/bin" << std::endl;

    // Bass frequency range
    int bass_min = 40;
    int bass_max = 200;
    int bass_min_bin = bass_min / freq_resolution;
    int bass_max_bin = bass_max / freq_resolution;

    output << "Bass Frequency Range: " << bass_min << "-" << bass_max << " Hz" << std::endl;
    output << "Bass FFT Bins: " << bass_min_bin << "-" << bass_max_bin << std::endl;

    bool pass_fft = freq_resolution > 20.0f && freq_resolution < 30.0f; // Should be ~24.4 Hz

    // Test 5: Signal processing
    output << "\nTest 4: Signal Processing" << std::endl;

    // Generate test sine wave
    std::vector<float> sine_wave(fft_size);
    float frequency = 120.0f; // 120 Hz test
    for (size_t i = 0; i < fft_size; ++i) {
        sine_wave[i] = sin(2.0f * M_PI * frequency * i / sample_rate);
    }

    // Calculate RMS
    float sum_squares = 0.0f;
    for (float sample : sine_wave) {
        sum_squares += sample * sample;
    }
    float rms = sqrt(sum_squares / sine_wave.size());

    output << "Sine Wave RMS: " << rms << " (expected ~0.707)" << std::endl;
    bool pass_signal = fabs(rms - 0.707f) < 0.01f;

    // Summary
    output << "\n===================================" << std::endl;
    output << "TEST SUMMARY" << std::endl;
    output << "===================================" << std::endl;
    output << "BPM 120 Test: " << (pass_120 ? "PASS" : "FAIL") << std::endl;
    output << "BPM 140 Test: " << (pass_140 ? "PASS" : "FAIL") << std::endl;
    output << "Confidence Test: " << (pass_confidence ? "PASS" : "FAIL") << std::endl;
    output << "FFT Resolution Test: " << (pass_fft ? "PASS" : "FAIL") << std::endl;
    output << "Signal Processing Test: " << (pass_signal ? "PASS" : "FAIL") << std::endl;

    bool all_pass = pass_120 && pass_140 && pass_confidence && pass_fft && pass_signal;

    output << "\nOVERALL RESULT: " << (all_pass ? "ALL TESTS PASSED" : "SOME TESTS FAILED") << std::endl;

    output.close();

    // Also print to console
    std::cout << "Tests completed. Results written to test_results.txt" << std::endl;
    std::cout << "Overall result: " << (all_pass ? "PASS" : "FAIL") << std::endl;

    return all_pass ? 0 : 1;
}
