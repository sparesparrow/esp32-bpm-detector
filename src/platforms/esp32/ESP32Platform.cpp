#include "ESP32Platform.h"

ESP32Platform::ESP32Platform()
{
}

uint32_t ESP32Platform::getFreeHeap()
{
    return ESP.getFreeHeap();
}

uint32_t ESP32Platform::getTotalHeap()
{
    return ESP.getHeapSize();
}

uint64_t ESP32Platform::getChipId()
{
    return ESP.getEfuseMac();
}

const char* ESP32Platform::getPlatformName()
{
    return "ESP32-S3";
}

uint32_t ESP32Platform::getCpuFrequencyMHz()
{
    return ESP.getCpuFreqMHz();
}

void ESP32Platform::restart()
{
    ESP.restart();
}

