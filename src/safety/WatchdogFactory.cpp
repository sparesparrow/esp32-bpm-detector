#include "WatchdogFactory.h"

#ifdef PLATFORM_ESP32
#include "platforms/esp32/ESP32Watchdog.h"
#endif

namespace sparetools {
namespace bpm {

IWatchdog* WatchdogFactory::createWatchdog(ITimer* timer) {
#ifdef PLATFORM_ESP32
    // Try hardware watchdog first for ESP32
    IWatchdog* hw_watchdog = createESP32Watchdog();
    if (hw_watchdog) {
        return hw_watchdog;
    }
#endif

    // Fallback to software watchdog
    return createSoftwareWatchdog(timer);
}

IWatchdog* WatchdogFactory::createESP32Watchdog() {
#ifdef PLATFORM_ESP32
    return new (std::nothrow) ESP32Watchdog();
#else
    return nullptr;
#endif
}

IWatchdog* WatchdogFactory::createSoftwareWatchdog(ITimer* timer) {
    if (!timer) return nullptr;
    return new (std::nothrow) SoftwareWatchdog(timer);
}

} // namespace bpm
} // namespace sparetools