/**
 * BPM Serial Sender for ESP32
 * 
 * Sends BPM data to Arduino display client via serial
 * Can be used alongside WiFi/REST API functionality
 */

#include "bpm_serial_sender.h"

#ifdef PLATFORM_ESP32

#include <Arduino.h>

BPMSerialSender::BPMSerialSender(HardwareSerial& serial, uint32_t baudRate)
    : serial_(serial), baudRate_(baudRate), lastSendTime_(0), sendInterval_(500) {
}

void BPMSerialSender::begin() {
    // Serial is already initialized in main.cpp for debug output
    // We'll use the same Serial object
}

void BPMSerialSender::sendBPM(float bpm, float confidence) {
    unsigned long currentTime = millis();
    
    // Rate limiting - don't send too frequently
    if (currentTime - lastSendTime_ < sendInterval_) {
        return;
    }
    
    // Format: "BPM:120.5,CONF:0.85\n"
    serial_.print("BPM:");
    serial_.print(bpm, 1);  // 1 decimal place
    
    if (confidence >= 0) {
        serial_.print(",CONF:");
        serial_.print(confidence, 2);  // 2 decimal places
    }
    
    serial_.println();  // End with newline
    
    lastSendTime_ = currentTime;
}

void BPMSerialSender::sendStatus(const char* status) {
    serial_.print("STATUS:");
    serial_.println(status);
}

void BPMSerialSender::setSendInterval(uint32_t intervalMs) {
    sendInterval_ = intervalMs;
}

#endif // PLATFORM_ESP32
