#pragma once

#include <cstdint>
#include "interfaces/ITimer.h"

namespace sparetools {
namespace bpm {

/**
 * @brief Hardware-independent watchdog timer interface
 *
 * Provides a consistent watchdog API across different platforms
 * with configurable timeout and recovery mechanisms.
 */
class IWatchdog {
public:
    virtual ~IWatchdog() = default;

    /**
     * @brief Initialize the watchdog with specified timeout
     * @param timeout_ms Timeout in milliseconds
     * @return true if initialization successful
     */
    virtual bool initialize(uint32_t timeout_ms) = 0;

    /**
     * @brief Reset/restart the watchdog timer
     */
    virtual void feed() = 0;

    /**
     * @brief Force a system reset via watchdog
     */
    virtual void forceReset() = 0;

    /**
     * @brief Get remaining time before watchdog triggers
     * @return milliseconds remaining, or 0 if not supported
     */
    virtual uint32_t getTimeRemaining() const = 0;

    /**
     * @brief Check if watchdog is enabled and active
     * @return true if watchdog is active
     */
    virtual bool isActive() const = 0;
};

/**
 * @brief Software watchdog implementation for platforms without hardware watchdog
 *
 * Uses timer interrupts to simulate watchdog behavior.
 * Less reliable than hardware watchdog but provides basic protection.
 */
class SoftwareWatchdog : public IWatchdog {
public:
    explicit SoftwareWatchdog(ITimer* timer);
    ~SoftwareWatchdog() override;

    bool initialize(uint32_t timeout_ms) override;
    void feed() override;
    void forceReset() override;
    uint32_t getTimeRemaining() const override;
    bool isActive() const override;

private:
    static void watchdogTimerCallback(void* context);

    ITimer* timer_;
    uint32_t timeout_ms_;
    uint32_t last_feed_time_;
    bool active_;
};

/**
 * @brief Watchdog manager with automatic feeding and health monitoring
 *
 * Provides high-level watchdog management with health checks
 * and automatic feeding for critical tasks.
 */
class WatchdogManager {
public:
    explicit WatchdogManager(IWatchdog* watchdog);
    ~WatchdogManager();

    /**
     * @brief Initialize with specified timeout
     */
    bool initialize(uint32_t timeout_ms = DEFAULT_WATCHDOG_TIMEOUT_MS);

    /**
     * @brief Register a health check function
     * @param check_function Function that returns true if system is healthy
     */
    void registerHealthCheck(bool (*check_function)());

    /**
     * @brief Manual watchdog feeding
     */
    void feed();

    /**
     * @brief Check system health and feed watchdog if healthy
     * @return true if system is healthy
     */
    bool checkHealthAndFeed();

    /**
     * @brief Get watchdog status information
     */
    struct Status {
        bool active;
        uint32_t time_remaining_ms;
        bool last_health_check_passed;
        uint32_t consecutive_failures;
    };

    Status getStatus() const;

    /**
     * @brief Enter fail-safe mode (reduced functionality)
     */
    void enterFailSafeMode();

    /**
     * @brief Attempt recovery from fail-safe mode
     * @return true if recovery successful
     */
    bool attemptRecovery();

    // Default watchdog timeout (30 seconds for ESP32)
    static constexpr uint32_t DEFAULT_WATCHDOG_TIMEOUT_MS = 30000;

    // Maximum consecutive health check failures before fail-safe
    static constexpr uint32_t MAX_CONSECUTIVE_FAILURES = 3;

private:
    IWatchdog* watchdog_;
    bool (*health_check_)();
    uint32_t last_feed_time_;
    uint32_t consecutive_failures_;
    bool in_fail_safe_mode_;
    Status last_status_;
};

/**
 * @brief RAII helper for critical sections that need watchdog management
 */
class CriticalSectionGuard {
public:
    explicit CriticalSectionGuard(WatchdogManager* watchdog_manager);
    ~CriticalSectionGuard();

    /**
     * @brief Extend the critical section timeout temporarily
     * @param additional_ms Additional milliseconds to add
     */
    void extendTimeout(uint32_t additional_ms);

private:
    WatchdogManager* watchdog_manager_;
    uint32_t original_timeout_;
};

} // namespace bpm
} // namespace sparetools