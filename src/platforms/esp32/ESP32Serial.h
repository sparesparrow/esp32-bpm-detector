#ifndef ESP32_SERIAL_H
#define ESP32_SERIAL_H

#include "../../interfaces/ISerial.h"
#include <Arduino.h>

//! @brief ESP32-S3 implementation of serial interface
//! @details Wraps the Arduino Serial object for ESP32 serial communication
class ESP32Serial : public ISerial
{
public:
    ESP32Serial();
    ~ESP32Serial() override = default;

    void begin(uint32_t baud_rate) override;
    void print(const char* str) override;
    void println(const char* str) override;
    void print(int value) override;
    void println(int value) override;
    void print(uint32_t value) override;
    void println(uint32_t value) override;
    void print(float value) override;
    void println(float value) override;
    void printf(const char* format, ...) override;
    int available() override;
    int read() override;
    void flush() override;
};

#endif // ESP32_SERIAL_H
