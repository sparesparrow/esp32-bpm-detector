#include "ArduinoPlatform.h"

ArduinoPlatform::ArduinoPlatform()
{
}

uint32_t ArduinoPlatform::getFreeHeap()
{
    // Arduino doesn't have a direct equivalent to ESP.getFreeHeap()
    // Return a conservative estimate (2KB free RAM typical for Arduino Uno)
    return 2048;
}

uint32_t ArduinoPlatform::getTotalHeap()
{
    // Arduino Uno has 2KB SRAM total
    return 2048;
}

uint64_t ArduinoPlatform::getChipId()
{
    // Arduino doesn't have a unique chip ID like ESP32
    // Return a constant value based on platform
    return 0xARDUINO;
}

const char* ArduinoPlatform::getPlatformName()
{
    return "Arduino";
}

uint32_t ArduinoPlatform::getCpuFrequencyMHz()
{
    // Arduino Uno runs at 16MHz
    return 16;
}

void ArduinoPlatform::restart()
{
    // Arduino doesn't have a software restart function
    // Just print a message - user will need to manually reset
    Serial.println("Arduino restart requested - please manually reset the board");
    while (true) {
        // Infinite loop until manual reset
        delay(1000);
    }
}
