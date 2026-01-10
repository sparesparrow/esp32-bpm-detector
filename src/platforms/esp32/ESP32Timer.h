#ifndef ESP32_TIMER_H
#define ESP32_TIMER_H

#include "../../interfaces/ITimer.h"
#include <Arduino.h>

/**
 * @brief ESP32-S3 implementation of timer interface
 * @details Wraps Arduino timing functions for ESP32
 */
class ESP32Timer : public ITimer {
public:
    ESP32Timer() = default;
    ~ESP32Timer() override = default;

    unsigned long millis() const override;
    unsigned long micros() const override;
    void delay(unsigned long ms) override;
    void delayMicroseconds(unsigned int us) override;
};

#endif // ESP32_TIMER_H
