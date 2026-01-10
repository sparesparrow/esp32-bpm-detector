#include "ESP32Timer.h"

unsigned long ESP32Timer::millis() const {
    return ::millis();
}

unsigned long ESP32Timer::micros() const {
    return ::micros();
}

void ESP32Timer::delay(unsigned long ms) {
    ::delay(ms);
}

void ESP32Timer::delayMicroseconds(unsigned int us) {
    ::delayMicroseconds(us);
}
