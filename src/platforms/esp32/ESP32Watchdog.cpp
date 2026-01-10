#include "ESP32Watchdog.h"

#ifdef PLATFORM_ESP32
#include <esp_task_wdt.h>
#endif

namespace sparetools {
namespace bpm {

ESP32Watchdog::ESP32Watchdog() : initialized_(false), timeout_ms_(0) {
}

ESP32Watchdog::~ESP32Watchdog() {
#ifdef PLATFORM_ESP32
    if (initialized_) {
        esp_task_wdt_delete(nullptr);
        initialized_ = false;
    }
#endif
}

bool ESP32Watchdog::initialize(uint32_t timeout_ms) {
#ifdef PLATFORM_ESP32
    // Convert milliseconds to seconds for ESP32 TWDT
    uint32_t timeout_seconds = timeout_ms / 1000;
    if (timeout_seconds == 0) timeout_seconds = 1;  // Minimum 1 second

    esp_err_t err = esp_task_wdt_init(timeout_seconds, true);
    if (err == ESP_OK) {
        err = esp_task_wdt_add(nullptr);  // Add current task to WDT
        if (err == ESP_OK) {
            initialized_ = true;
            timeout_ms_ = timeout_ms;
            return true;
        }
    }

    // Fallback to software watchdog if hardware WDT fails
    initialized_ = false;
    return false;
#else
    // Not ESP32 platform
    return false;
#endif
}

void ESP32Watchdog::feed() {
#ifdef PLATFORM_ESP32
    if (initialized_) {
        esp_task_wdt_reset();
    }
#endif
}

void ESP32Watchdog::forceReset() {
#ifdef PLATFORM_ESP32
    // Force immediate reset via TWDT
    esp_task_wdt_init(1, true);  // 1 second timeout
    esp_task_wdt_add(nullptr);
    vTaskDelay(pdMS_TO_TICKS(2000));  // Wait longer than timeout
#endif
}

uint32_t ESP32Watchdog::getTimeRemaining() const {
    // ESP32 TWDT doesn't provide remaining time API
    // Return approximate based on timeout setting
    return initialized_ ? timeout_ms_ : 0;
}

bool ESP32Watchdog::isActive() const {
    return initialized_;
}

} // namespace bpm
} // namespace sparetools