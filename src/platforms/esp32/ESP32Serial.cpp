#include "ESP32Serial.h"
#include <cstdarg>

ESP32Serial::ESP32Serial()
{
}

void ESP32Serial::begin(uint32_t baud_rate)
{
    Serial.begin(baud_rate);
}

void ESP32Serial::print(const char* str)
{
    Serial.print(str);
}

void ESP32Serial::println(const char* str)
{
    Serial.println(str);
}

void ESP32Serial::print(int value)
{
    Serial.print(value);
}

void ESP32Serial::println(int value)
{
    Serial.println(value);
}

void ESP32Serial::print(uint32_t value)
{
    Serial.print(value);
}

void ESP32Serial::println(uint32_t value)
{
    Serial.println(value);
}

void ESP32Serial::print(float value)
{
    Serial.print(value);
}

void ESP32Serial::println(float value)
{
    Serial.println(value);
}

void ESP32Serial::printf(const char* format, ...)
{
    va_list args;
    va_start(args, format);
    char buffer[256];
    vsnprintf(buffer, sizeof(buffer), format, args);
    Serial.print(buffer);
    va_end(args);
}

int ESP32Serial::available()
{
    return Serial.available();
}

int ESP32Serial::read()
{
    return Serial.read();
}

void ESP32Serial::flush()
{
    Serial.flush();
}
