#include "ESP32Timer.h"

ESP32Timer::ESP32Timer()
{
}

uint32_t ESP32Timer::millis()
{
    return ::millis();
}

uint32_t ESP32Timer::micros()
{
    return ::micros();
}

void ESP32Timer::delay(uint32_t milliseconds)
{
    ::delay(milliseconds);
}

void ESP32Timer::delayMicroseconds(uint32_t microseconds)
{
    ::delayMicroseconds(microseconds);
}

