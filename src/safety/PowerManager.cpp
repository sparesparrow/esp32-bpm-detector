#include "PowerManager.h"

#ifdef PLATFORM_ESP32
#include <Arduino.h>
#include <esp_sleep.h>
#include <esp_wifi.h>
#include <esp_pm.h>
#endif

namespace sparetools {
namespace bpm {

bool PowerManager::initialize(ITimer* timer, const Config& config) {
    config_ = config;
    timer_ = timer;
    current_mode_ = config.default_mode;
    current_activity_ = ActivityLevel::MODERATE;
    last_activity_time_ = timer_ ? timer_->millis() : 0;
    uptime_start_ = last_activity_time_;
    idle_time_accumulated_ = 0;
    sleep_time_accumulated_ = 0;
    initialized_ = true;

    // Apply initial power mode
    applyPowerMode(current_mode_);

    return true;
}

void PowerManager::updateActivity(ActivityLevel level) {
    if (!initialized_ || !timer_) return;

    current_activity_ = level;
    last_activity_time_ = timer_->millis();

    // Dynamically adjust power mode based on activity
    if (config_.enable_dynamic_frequency) {
        PowerMode optimal_mode = calculateOptimalPowerMode(level);
        if (optimal_mode != current_mode_) {
            setPowerMode(optimal_mode);
        }
    }
}

void PowerManager::setPowerMode(PowerMode mode) {
    if (!initialized_) return;

    current_mode_ = mode;
    applyPowerMode(mode);
}

PowerManager::PowerMode PowerManager::getCurrentPowerMode() const {
    return current_mode_;
}

void PowerManager::executePowerManagement() {
    if (!initialized_ || !timer_) return;

    uint32_t current_time = timer_->millis();

    // Check for inactivity
    if (isInactivityTimeout()) {
        // Accumulate idle time
        uint32_t idle_duration = current_time - last_activity_time_;
        idle_time_accumulated_ += idle_duration;

        // Consider entering low power mode
        if (shouldEnterLowPowerMode()) {
            setPowerMode(PowerMode::POWERSAVE);
        }
    }

    // Periodic power optimization based on current mode
    applyPowerMode(current_mode_);
}

PowerManager::PowerStats PowerManager::getPowerStats() const {
    PowerStats stats;
    stats.current_mode = current_mode_;
    stats.current_activity = current_activity_;
    stats.uptime_ms = timer_ ? (timer_->millis() - uptime_start_) : 0;
    stats.idle_time_ms = idle_time_accumulated_;
    stats.sleep_time_ms = sleep_time_accumulated_;
    stats.average_power_consumption_ma = 0.0f;  // Not implemented yet
    stats.wifi_enabled = true;  // Assume enabled by default
    stats.bluetooth_enabled = false;  // ESP32 typically doesn't have BT
    stats.cpu_frequency_mhz = 240;  // Default ESP32 frequency

#ifdef PLATFORM_ESP32
    // Get actual ESP32 stats
    stats.cpu_frequency_mhz = ESP.getCpuFreqMHz();
#endif

    return stats;
}

void PowerManager::forceSleep(uint32_t sleep_duration_ms) {
#ifdef PLATFORM_ESP32
    enterESP32LightSleep(sleep_duration_ms);
    sleep_time_accumulated_ += sleep_duration_ms;
#endif
}

void PowerManager::wakeUp() {
    // Wake up is typically handled by ESP32 hardware
    // Reset activity timer
    if (timer_) {
        last_activity_time_ = timer_->millis();
    }
}

bool PowerManager::shouldEnterLowPowerMode() const {
    if (!timer_) return false;

    uint32_t current_time = timer_->millis();
    uint32_t idle_duration = current_time - last_activity_time_;

    return idle_duration > config_.idle_timeout_ms;
}

void PowerManager::applyPowerMode(PowerMode mode) {
    switch (mode) {
        case PowerMode::PERFORMANCE:
            setESP32CPUSpeed(240);  // Maximum frequency
            disableESP32PeripheralPowerDown();
            setESP32WiFiPowerMode(false);
            break;

        case PowerMode::BALANCED:
            setESP32CPUSpeed(160);  // Balanced frequency
            enableESP32PeripheralPowerDown();
            setESP32WiFiPowerMode(false);
            break;

        case PowerMode::POWERSAVE:
            setESP32CPUSpeed(80);   // Low frequency
            enableESP32PeripheralPowerDown();
            setESP32WiFiPowerMode(true);
            break;

        case PowerMode::ULTRA_LOW_POWER:
            setESP32CPUSpeed(40);   // Minimum frequency
            enableESP32PeripheralPowerDown();
            setESP32WiFiPowerMode(true);
            // Could add light sleep here for very low power
            break;
    }
}

void PowerManager::setESP32CPUSpeed(uint32_t frequency_mhz) {
#ifdef PLATFORM_ESP32
    // ESP32 frequency options: 240, 160, 80, 40, 20, 10 MHz
    if (frequency_mhz >= 240) {
        setCpuFrequencyMhz(240);
    } else if (frequency_mhz >= 160) {
        setCpuFrequencyMhz(160);
    } else if (frequency_mhz >= 80) {
        setCpuFrequencyMhz(80);
    } else if (frequency_mhz >= 40) {
        setCpuFrequencyMhz(40);
    } else {
        setCpuFrequencyMhz(40);  // Minimum
    }
#endif
}

void PowerManager::enableESP32PeripheralPowerDown() {
#ifdef PLATFORM_ESP32
    // Disable unused peripherals to save power
    // This is a simplified implementation - real implementation would
    // be more sophisticated based on system needs
#endif
}

void PowerManager::disableESP32PeripheralPowerDown() {
#ifdef PLATFORM_ESP32
    // Re-enable peripherals
#endif
}

void PowerManager::setESP32WiFiPowerMode(bool low_power) {
#ifdef PLATFORM_ESP32
    if (config_.enable_wifi_power_management) {
        if (low_power) {
            esp_wifi_set_ps(WIFI_PS_MIN_MODEM);
        } else {
            esp_wifi_set_ps(WIFI_PS_NONE);
        }
    }
#endif
}

void PowerManager::enterESP32LightSleep(uint32_t duration_ms) {
#ifdef PLATFORM_ESP32
    // Configure wake up timer
    esp_sleep_enable_timer_wakeup(duration_ms * 1000);  // Convert to microseconds

    // Enter light sleep
    esp_light_sleep_start();
#endif
}

bool PowerManager::isInactivityTimeout() const {
    if (!timer_) return false;

    uint32_t current_time = timer_->millis();
    uint32_t idle_duration = current_time - last_activity_time_;

    return idle_duration > config_.idle_timeout_ms;
}

PowerManager::PowerMode PowerManager::calculateOptimalPowerMode(ActivityLevel activity) const {
    switch (activity) {
        case ActivityLevel::IDLE:
        case ActivityLevel::ACTIVITY_LOW:
            return PowerMode::POWERSAVE;

        case ActivityLevel::MODERATE:
            return PowerMode::BALANCED;

        case ActivityLevel::ACTIVITY_HIGH:
        case ActivityLevel::CRITICAL:
            return PowerMode::PERFORMANCE;

        default:
            return PowerMode::BALANCED;
    }
}

} // namespace bpm
} // namespace sparetools