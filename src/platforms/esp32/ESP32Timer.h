#ifndef ESP32_TIMER_H
#define ESP32_TIMER_H

#include "../../interfaces/ITimer.h"
#include <Arduino.h>

//! @brief ESP32-S3 implementation of timer interface
//! @details Wraps Arduino timing functions for ESP32
class ESP32Timer : public ITimer
{
public:
    ESP32Timer();
    ~ESP32Timer() override = default;

    uint32_t millis() override;
    uint32_t micros() override;
    void delay(uint32_t milliseconds) override;
    void delayMicroseconds(uint32_t microseconds) override;
};

#endif // ESP32_TIMER_H
