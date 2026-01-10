#pragma once

#include "safety/Watchdog.h"

namespace sparetools {
namespace bpm {

/**
 * @brief ESP32 hardware watchdog implementation
 *
 * Uses ESP32's Task Watchdog Timer (TWDT) for reliable watchdog functionality.
 * More reliable than software watchdog for critical applications.
 */
class ESP32Watchdog : public IWatchdog {
public:
    ESP32Watchdog();
    ~ESP32Watchdog() override;

    bool initialize(uint32_t timeout_ms) override;
    void feed() override;
    void forceReset() override;
    uint32_t getTimeRemaining() const override;
    bool isActive() const override;

private:
    bool initialized_;
    uint32_t timeout_ms_;
};

} // namespace bpm
} // namespace sparetools