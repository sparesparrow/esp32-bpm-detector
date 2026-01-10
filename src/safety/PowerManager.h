#pragma once

#include <cstdint>
#include "interfaces/ITimer.h"

namespace sparetools {
namespace bpm {

/**
 * @brief Power management system for embedded devices
 *
 * Provides intelligent power optimization based on system state,
 * workload, and battery status. Designed for ESP32 but extensible
 * to other platforms.
 */
class PowerManager {
public:
    /**
     * @brief Power management modes
     */
    enum class PowerMode {
        PERFORMANCE = 0,    // Maximum performance, ignore power consumption
        BALANCED = 1,       // Balance performance and power consumption
        POWERSAVE = 2,      // Minimize power consumption
        ULTRA_LOW_POWER = 3 // Extreme power saving (minimal functionality)
    };

    /**
     * @brief System activity levels
     */
    enum class ActivityLevel {
        IDLE = 0,           // System is idle
        ACTIVITY_LOW = 1,   // Low activity (occasional operations)
        MODERATE = 2,       // Moderate activity (frequent operations)
        ACTIVITY_HIGH = 3,  // High activity (continuous operations)
        CRITICAL = 4        // Critical operations (must maintain performance)
    };

    /**
     * @brief Power management configuration
     */
    struct Config {
        PowerMode default_mode = PowerMode::BALANCED;
        uint32_t idle_timeout_ms = 30000;      // Enter idle after 30 seconds
        uint32_t sleep_timeout_ms = 300000;    // Enter sleep after 5 minutes
        bool enable_dynamic_frequency = true;
        bool enable_peripheral_powerdown = true;
        bool enable_wifi_power_management = true;
    };

    /**
     * @brief Initialize power manager
     * @param timer Timer interface for timing operations
     * @param config Power management configuration
     * @return true if initialization successful
     */
    bool initialize(ITimer* timer, const Config& config);

    /**
     * @brief Update system activity level
     * @param level Current activity level
     */
    void updateActivity(ActivityLevel level);

    /**
     * @brief Set power management mode
     * @param mode New power mode
     */
    void setPowerMode(PowerMode mode);

    /**
     * @brief Get current power mode
     */
    PowerMode getCurrentPowerMode() const;

    /**
     * @brief Execute power management tasks (call regularly)
     */
    void executePowerManagement();

    /**
     * @brief Get power consumption statistics
     */
    struct PowerStats {
        PowerMode current_mode;
        ActivityLevel current_activity;
        uint32_t uptime_ms;
        uint32_t idle_time_ms;
        uint32_t sleep_time_ms;
        float average_power_consumption_ma;  // If available
        bool wifi_enabled;
        bool bluetooth_enabled;
        uint32_t cpu_frequency_mhz;
    };

    PowerStats getPowerStats() const;

    /**
     * @brief Force immediate sleep (for critical power saving)
     * @param sleep_duration_ms Duration to sleep
     */
    void forceSleep(uint32_t sleep_duration_ms);

    /**
     * @brief Wake up from sleep
     */
    void wakeUp();

    /**
     * @brief Check if system should enter low power mode
     */
    bool shouldEnterLowPowerMode() const;

private:
    Config config_;
    ITimer* timer_;
    PowerMode current_mode_;
    ActivityLevel current_activity_;
    uint32_t last_activity_time_;
    uint32_t uptime_start_;
    uint32_t idle_time_accumulated_;
    uint32_t sleep_time_accumulated_;
    bool initialized_;

    /**
     * @brief Apply power mode settings
     */
    void applyPowerMode(PowerMode mode);

    /**
     * @brief ESP32-specific power management functions
     */
    void setESP32CPUSpeed(uint32_t frequency_mhz);
    void enableESP32PeripheralPowerDown();
    void disableESP32PeripheralPowerDown();
    void setESP32WiFiPowerMode(bool low_power);
    void enterESP32LightSleep(uint32_t duration_ms);

    /**
     * @brief Check for inactivity timeout
     */
    bool isInactivityTimeout() const;

    /**
     * @brief Calculate optimal power mode based on activity
     */
    PowerMode calculateOptimalPowerMode(ActivityLevel activity) const;
};

} // namespace bpm
} // namespace sparetools