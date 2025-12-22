/*
 * FFT Test Program for ESP32 BPM Detector
 * 
 * This file can be used to test FFT functionality with known signals.
 * To use this test:
 * 1. Comment out main.cpp's setup() and loop()
 * 2. Include this file and call testFFT() from setup()
 * 3. Or compile separately as a test program
 * 
 * Test cases:
 * - Pure sine waves at various frequencies
 * - Beat patterns at known BPMs
 * - Frequency resolution verification
 */

#include <Arduino.h>
#include "config.h"
#include "bpm_detector.h"
#include <ArduinoFFT.h>
#include <cmath>

// Test configuration
#define TEST_DURATION_MS 5000  // Run tests for 5 seconds
#define TEST_FREQUENCIES_COUNT 5

// Test frequencies (Hz) - corresponding to different BPMs
// 60 BPM = 1 beat/sec = 60 Hz fundamental (or 120 Hz for kick drum)
// 120 BPM = 2 beats/sec = 120 Hz fundamental
const float test_frequencies[TEST_FREQUENCIES_COUNT] = {
    60.0f,   // 60 BPM
    80.0f,   // 80 BPM
    120.0f,  // 120 BPM
    140.0f,  // 140 BPM
    180.0f   // 180 BPM
};

// Global test state
BPMDetector* test_detector = nullptr;
unsigned long test_start_time = 0;
int current_test_index = 0;

void printTestHeader(const char* test_name) {
    Serial.println("\n========================================");
    Serial.print("TEST: ");
    Serial.println(test_name);
    Serial.println("========================================");
}

void testFFTWithSineWave(float frequency_hz) {
    printTestHeader("FFT Frequency Resolution Test");
    
    Serial.print("Testing with sine wave at ");
    Serial.print(frequency_hz);
    Serial.println(" Hz");
    
    // Create detector
    BPMDetector detector(SAMPLE_RATE, FFT_SIZE);
    detector.enableTestMode(frequency_hz);
    
    // Fill buffer with test samples
    Serial.println("Generating test samples...");
    for (int i = 0; i < FFT_SIZE; ++i) {
        detector.sample();
        delayMicroseconds(1000000 / SAMPLE_RATE);
    }
    
    // Perform detection
    Serial.println("Performing FFT analysis...");
    BPMDetector::BPMData result = detector.detect();
    
    // Expected frequency bin
    float freq_resolution = (float)SAMPLE_RATE / FFT_SIZE;
    int expected_bin = (int)(frequency_hz / freq_resolution);
    
    Serial.print("Expected FFT bin: ");
    Serial.println(expected_bin);
    Serial.print("Frequency resolution: ");
    Serial.print(freq_resolution);
    Serial.println(" Hz/bin");
    
    Serial.println("\nTest completed.");
}

void testBPMDetection(float target_bpm) {
    printTestHeader("BPM Detection Test");
    
    Serial.print("Testing BPM detection for target: ");
    Serial.print(target_bpm);
    Serial.println(" BPM");
    
    // Convert BPM to frequency (assuming kick drum at 2x BPM)
    // 120 BPM = 2 beats/sec, kick drum typically 60-100 Hz
    float test_freq = target_bpm / 60.0f * 60.0f;  // Simplified: 1 Hz per BPM
    
    Serial.print("Using test frequency: ");
    Serial.print(test_freq);
    Serial.println(" Hz");
    
    // Create detector
    BPMDetector detector(SAMPLE_RATE, FFT_SIZE);
    detector.begin(0);  // Dummy pin for test mode
    detector.setMinBPM(MIN_BPM);
    detector.setMaxBPM(MAX_BPM);
    detector.enableTestMode(test_freq);
    
    Serial.println("Running detection for 10 seconds...");
    Serial.println("Time\tDetected BPM\tConfidence\tStatus");
    
    unsigned long start_time = millis();
    int detection_count = 0;
    float bpm_sum = 0.0f;
    float confidence_sum = 0.0f;
    
    while (millis() - start_time < 10000) {
        // Sample continuously
        detector.sample();
        
        // Detect every 100ms
        static unsigned long last_detection = 0;
        if (millis() - last_detection >= 100) {
            BPMDetector::BPMData result = detector.detect();
            
            Serial.print((millis() - start_time) / 1000);
            Serial.print("\t");
            Serial.print(result.bpm);
            Serial.print("\t\t");
            Serial.print(result.confidence, 3);
            Serial.print("\t\t");
            Serial.println(result.status);
            
            if (result.bpm > 0.0f && result.status == "detecting") {
                bpm_sum += result.bpm;
                confidence_sum += result.confidence;
                detection_count++;
            }
            
            last_detection = millis();
        }
        
        delayMicroseconds(1000000 / SAMPLE_RATE);
    }
    
    // Calculate statistics
    if (detection_count > 0) {
        float avg_bpm = bpm_sum / detection_count;
        float avg_confidence = confidence_sum / detection_count;
        float error = fabs(avg_bpm - target_bpm);
        float error_percent = (error / target_bpm) * 100.0f;
        
        Serial.println("\n--- Results ---");
        Serial.print("Target BPM: ");
        Serial.println(target_bpm);
        Serial.print("Average Detected BPM: ");
        Serial.println(avg_bpm);
        Serial.print("Error: ");
        Serial.print(error);
        Serial.print(" BPM (");
        Serial.print(error_percent);
        Serial.println("%)");
        Serial.print("Average Confidence: ");
        Serial.println(avg_confidence, 3);
        Serial.print("Valid Detections: ");
        Serial.print(detection_count);
        Serial.print(" / ");
        Serial.println(100);  // 10 seconds / 100ms = 100 detections
        
        // Pass/fail criteria
        if (error_percent < 5.0f && avg_confidence > 0.5f) {
            Serial.println("RESULT: PASS");
        } else {
            Serial.println("RESULT: FAIL");
        }
    } else {
        Serial.println("RESULT: FAIL - No valid detections");
    }
}

void testMultipleFrequencies() {
    printTestHeader("Multiple Frequency Test");
    
    Serial.println("Testing FFT with multiple frequencies:");
    for (int i = 0; i < TEST_FREQUENCIES_COUNT; ++i) {
        Serial.print("  ");
        Serial.print(i + 1);
        Serial.print(". ");
        Serial.print(test_frequencies[i]);
        Serial.println(" Hz");
    }
    
    for (int i = 0; i < TEST_FREQUENCIES_COUNT; ++i) {
        Serial.print("\n--- Test ");
        Serial.print(i + 1);
        Serial.print(" of ");
        Serial.print(TEST_FREQUENCIES_COUNT);
        Serial.println(" ---");
        testFFTWithSineWave(test_frequencies[i]);
        delay(1000);
    }
}

void testBeatPattern() {
    printTestHeader("Beat Pattern Test");
    
    Serial.println("Testing with synthetic beat pattern (120 BPM)");
    Serial.println("Using test mode with 2 Hz frequency (120 BPM equivalent)");
    
    // Create detector
    BPMDetector detector(SAMPLE_RATE, FFT_SIZE);
    detector.begin(0);
    detector.setMinBPM(60);
    detector.setMaxBPM(200);
    
    // Use test mode with frequency that corresponds to 120 BPM
    // 120 BPM = 2 beats/sec, so use 2 Hz test frequency
    detector.enableTestMode(2.0f);
    
    Serial.println("Sampling for 5 seconds...");
    Serial.println("Time\tDetected BPM\tConfidence\tStatus");
    
    unsigned long start_time = millis();
    
    while (millis() - start_time < 5000) {
        // Sample using test mode
        detector.sample();
        
        // Detect every 100ms
        static unsigned long last_detection = 0;
        if (millis() - last_detection >= 100) {
            BPMDetector::BPMData result = detector.detect();
            
            Serial.print((millis() - start_time) / 1000);
            Serial.print("\t");
            Serial.print(result.bpm);
            Serial.print("\t\t");
            Serial.print(result.confidence, 3);
            Serial.print("\t\t");
            Serial.println(result.status);
            
            last_detection = millis();
        }
        
        delayMicroseconds(1000000 / SAMPLE_RATE);
    }
    
    detector.disableTestMode();
}

void runAllTests() {
    Serial.println("\n\n");
    Serial.println("========================================");
    Serial.println("ESP32 BPM Detector - FFT Test Suite");
    Serial.println("========================================");
    Serial.print("Sample Rate: ");
    Serial.print(SAMPLE_RATE);
    Serial.println(" Hz");
    Serial.print("FFT Size: ");
    Serial.println(FFT_SIZE);
    Serial.print("Frequency Resolution: ");
    Serial.print((float)SAMPLE_RATE / FFT_SIZE);
    Serial.println(" Hz/bin");
    Serial.println("\nStarting tests...\n");
    
    delay(2000);
    
    // Run tests
    testFFTWithSineWave(60.0f);
    delay(2000);
    
    testFFTWithSineWave(120.0f);
    delay(2000);
    
    testBPMDetection(120.0f);
    delay(2000);
    
    testBPMDetection(140.0f);
    delay(2000);
    
    testBeatPattern();
    
    Serial.println("\n\n========================================");
    Serial.println("All tests completed!");
    Serial.println("========================================");
}

// Uncomment to use as standalone test program
/*
void setup() {
    Serial.begin(115200);
    delay(2000);
    
    runAllTests();
}

void loop() {
    // Tests run once in setup()
    delay(1000);
}
*/

