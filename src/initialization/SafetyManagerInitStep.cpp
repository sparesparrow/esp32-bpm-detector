#include "SafetyManagerInitStep.h"
#include <new>

namespace sparetools {
namespace bpm {

SafetyManagerInitStep::SafetyManagerInitStep(ITimer* timer, LogManager* log_manager)
    : timer_(timer), log_manager_(log_manager) {
    // Safety manager initialization is critical - do it immediately
    safety_manager_ = new (std::nothrow) SafetyManager();

    if (safety_manager_) {
        SafetyManager::Config config;
        config.watchdog_timeout_ms = 30000;  // 30 seconds
        config.health_check_interval_ms = 5000;  // 5 seconds
        config.memory_check_interval_ms = 10000;  // 10 seconds
        config.enable_fail_safe_mode = true;
        config.enable_memory_monitoring = true;
        config.enable_stack_monitoring = true;

        if (safety_manager_->initialize(timer_, log_manager_, config)) {
            finished = true;
        } else {
            // Safety manager failed to initialize - this is critical
            if (log_manager_) {
                log_manager_->log(ComponentLoggingId::ApplicationLoggingId,
                                 SeverityLevel::critical,
                                 "CRITICAL: Safety manager initialization failed");
            }
            finished = false;
        }
    } else {
        // Failed to allocate safety manager - critical error
        if (log_manager_) {
            log_manager_->log(ComponentLoggingId::ApplicationLoggingId,
                             SeverityLevel::critical,
                             "CRITICAL: Failed to allocate safety manager");
        }
        finished = false;
    }
}

} // namespace bpm
} // namespace sparetools