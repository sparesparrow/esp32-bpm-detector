#ifndef ARDUINO_SERIAL_H
#define ARDUINO_SERIAL_H

#include "../../interfaces/ISerial.h"
#include <Arduino.h>

//! @brief Arduino implementation of serial interface
//! @details Wraps the Arduino Serial object for serial communication
class ArduinoSerial : public ISerial
{
public:
    ArduinoSerial();
    ~ArduinoSerial() override = default;

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

#endif // ARDUINO_SERIAL_H
