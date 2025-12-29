#include "ArduinoSerial.h"
#include <cstdarg>

ArduinoSerial::ArduinoSerial()
{
}

void ArduinoSerial::begin(uint32_t baud_rate)
{
    Serial.begin(baud_rate);
    // Arduino may need a small delay after Serial.begin()
    delay(100);
}

void ArduinoSerial::print(const char* str)
{
    Serial.print(str);
}

void ArduinoSerial::println(const char* str)
{
    Serial.println(str);
}

void ArduinoSerial::print(int value)
{
    Serial.print(value);
}

void ArduinoSerial::println(int value)
{
    Serial.println(value);
}

void ArduinoSerial::print(uint32_t value)
{
    Serial.print(value);
}

void ArduinoSerial::println(uint32_t value)
{
    Serial.println(value);
}

void ArduinoSerial::print(float value)
{
    Serial.print(value);
}

void ArduinoSerial::println(float value)
{
    Serial.println(value);
}

void ArduinoSerial::printf(const char* format, ...)
{
    va_list args;
    va_start(args, format);
    char buffer[256];
    vsnprintf(buffer, sizeof(buffer), format, args);
    Serial.print(buffer);
    va_end(args);
}

int ArduinoSerial::available()
{
    return Serial.available();
}

int ArduinoSerial::read()
{
    return Serial.read();
}

void ArduinoSerial::flush()
{
    Serial.flush();
}
