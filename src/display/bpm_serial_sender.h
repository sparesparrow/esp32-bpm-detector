/**
 * BPM Serial Sender for ESP32
 * 
 * Sends BPM data to Arduino display client via serial
 */

#ifndef BPM_SERIAL_SENDER_H
#define BPM_SERIAL_SENDER_H

#ifdef PLATFORM_ESP32

#include <Arduino.h>

class BPMSerialSender {
public:
    /**
     * Constructor
     * @param serial Hardware serial port (typically Serial or Serial2)
     * @param baudRate Baud rate (default 115200)
     */
    BPMSerialSender(HardwareSerial& serial, uint32_t baudRate = 115200);
    
    /**
     * Initialize serial communication
     */
    void begin();
    
    /**
     * Send BPM value to Arduino
     * @param bpm Detected BPM value
     * @param confidence Confidence level (0.0-1.0), or -1 to omit
     */
    void sendBPM(float bpm, float confidence = -1.0);
    
    /**
     * Send status message
     * @param status Status string (e.g., "detecting", "low_signal", "error")
     */
    void sendStatus(const char* status);
    
    /**
     * Set minimum interval between sends (rate limiting)
     * @param intervalMs Interval in milliseconds (default 500ms)
     */
    void setSendInterval(uint32_t intervalMs);
    
private:
    HardwareSerial& serial_;
    uint32_t baudRate_;
    unsigned long lastSendTime_;
    uint32_t sendInterval_;
};

#endif // PLATFORM_ESP32

#endif // BPM_SERIAL_SENDER_H
