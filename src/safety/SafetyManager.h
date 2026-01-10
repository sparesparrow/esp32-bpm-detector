#pragma once

#include "ErrorHandling.h"
#include "Watchdog.h"
#include "MemorySafety.h"
#include "interfaces/ITimer.h"
#include "logging/LogManager.h"
// #include <memory> // Temporarily removed for compilation

namespace sparetools {
namespace bpm {

/**
 * @brief Central safety manager coordinating all safety-critical features
 *
 * Integrates error handling, watchdog management, memory monitoring,
 * and health checks into a cohesive safety system.
 */
class SafetyManager {
public:
    /**
     * @brief Safety manager configuration
     */
    struct Config {
        uint32_t watchdog_timeout_ms = 30000;  // 30 seconds
        uint32_t health_check_interval_ms = 5000;  // 5 seconds
        uint32_t memory_check_interval_ms = 10000;  // 10 seconds
        bool enable_fail_safe_mode = true;
        bool enable_memory_monitoring = true;
        bool enable_stack_monitoring = true;
    };

    /**
     * @brief Initialize safety manager
     * @param timer Timer interface for timing operations
     * @param log_manager Logging interface
     * @param config Safety configuration
     * @return true if initialization successful
     */
    bool initialize(ITimer* timer, LogManager* log_manager, const Config& config);

    /**
     * @brief Execute periodic safety checks
     * @return true if all checks pass
     */
    bool executeSafetyChecks();

    /**
     * @brief Report an error through the safety system
     */
    bool reportError(ErrorHandling::ErrorCode code,
                    ErrorHandling::ErrorSeverity severity,
                    const char* message,
                    const char* file = nullptr,
                    int line = 0);

    /**
     * @brief Check if system is in fail-safe mode
     */
    bool isInFailSafeMode() const;

    /**
     * @brief Attempt to recover from fail-safe mode
     */
    bool attemptRecovery();

    /**
     * @brief Get comprehensive safety status
     */
    struct SafetyStatus {
        bool watchdog_active;
        bool memory_ok;
        bool stack_ok;
        bool in_fail_safe_mode;
        uint32_t error_count;
        uint32_t free_heap;
        float fragmentation_ratio;
        WatchdogManager::Status watchdog_status;
    };

    SafetyStatus getSafetyStatus() const;

    /**
     * @brief Register a custom health check function
     */
    void registerHealthCheck(bool (*check_function)());

    /**
     * @brief Manual watchdog feeding (for critical sections)
     */
    void feedWatchdog();

    /**
     * @brief Create a critical section guard
     */
    CriticalSectionGuard createCriticalSectionGuard();

private:
    Config config_;
    ITimer* timer_;  // Non-owning pointer - managed externally
    LogManager* log_manager_;  // Non-owning pointer - managed externally
    ErrorHandling::DefaultErrorHandler* error_handler_;
    WatchdogManager* watchdog_manager_;
    IWatchdog* watchdog_;  // Non-owning pointer - created by factory, may need custom deleter

    uint32_t last_health_check_time_;
    uint32_t last_memory_check_time_;
    bool initialized_;
    bool fail_safe_mode_;

    // Health check function
    bool (*custom_health_check_)() = nullptr;

    /**
     * @brief Perform comprehensive health check
     */
    bool performHealthCheck();

    /**
     * @brief Perform memory safety checks
     */
    bool performMemoryChecks();

    /**
     * @brief Initialize watchdog system
     */
    bool initializeWatchdog();
};

} // namespace bpm
} // namespace sparetools