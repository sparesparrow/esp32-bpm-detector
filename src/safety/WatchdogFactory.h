#pragma once

#include "Watchdog.h"

namespace sparetools {
namespace bpm {

/**
 * @brief Factory for creating platform-appropriate watchdog implementations
 */
class WatchdogFactory {
public:
    /**
     * @brief Create the best available watchdog for the current platform
     * @param timer Timer interface (required for software watchdog fallback)
     * @return Pointer to watchdog implementation, nullptr if none available
     */
    static IWatchdog* createWatchdog(ITimer* timer);

    /**
     * @brief Create ESP32 hardware watchdog
     * @return Pointer to ESP32 watchdog, nullptr if not ESP32 platform
     */
    static IWatchdog* createESP32Watchdog();

    /**
     * @brief Create software watchdog (fallback for any platform)
     * @param timer Timer interface
     * @return Pointer to software watchdog
     */
    static IWatchdog* createSoftwareWatchdog(ITimer* timer);
};

} // namespace bpm
} // namespace sparetools