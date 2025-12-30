#ifndef ESP32_PLATFORM_H
#define ESP32_PLATFORM_H

#include "../../interfaces/IPlatform.h"
#include <Arduino.h>

//! @brief ESP32-S3 implementation of platform interface
//! @details Provides ESP32-specific system information and operations
class ESP32Platform : public IPlatform
{
public:
    ESP32Platform();
    ~ESP32Platform() override = default;

    uint32_t getFreeHeap() override;
    uint32_t getTotalHeap() override;
    uint64_t getChipId() override;
    const char* getPlatformName() override;
    uint32_t getCpuFrequencyMHz() override;
    void restart() override;
};

#endif // ESP32_PLATFORM_H

