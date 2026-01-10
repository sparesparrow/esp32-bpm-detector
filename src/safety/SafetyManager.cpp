#include "SafetyManager.h"
#include "WatchdogFactory.h"
#include <new>

namespace sparetools {
namespace bpm {

bool SafetyManager::initialize(ITimer* timer, LogManager* log_manager, const Config& config) {
    config_ = config;
    timer_ = timer;
    log_manager_ = log_manager;
    initialized_ = false;
    fail_safe_mode_ = false;
    last_health_check_time_ = 0;
    last_memory_check_time_ = 0;

    // Create error handler
    error_handler_ = new (std::nothrow) ErrorHandling::DefaultErrorHandler(log_manager_);
    if (!error_handler_) {
        return false;
    }

    // Initialize watchdog
    if (!initializeWatchdog()) {
        // Watchdog initialization failed - continue without it but log error
        reportError(ErrorHandling::ErrorCode::UNKNOWN_ERROR,
                   ErrorHandling::ErrorSeverity::WARNING,
                   "Watchdog initialization failed - continuing without watchdog protection");
    }

    // Create watchdog manager
    watchdog_manager_ = new (std::nothrow) WatchdogManager(watchdog_);
    if (watchdog_manager_) {
        if (!watchdog_manager_->initialize(config_.watchdog_timeout_ms)) {
            reportError(ErrorHandling::ErrorCode::UNKNOWN_ERROR,
                       ErrorHandling::ErrorSeverity::ERROR,
                       "Watchdog manager initialization failed");
            delete watchdog_manager_;
            watchdog_manager_ = nullptr;
        }
    }

    initialized_ = true;

    if (log_manager_) {
        log_manager_->log(ComponentLoggingId::ApplicationLoggingId,
                         SeverityLevel::info,
                         "Safety manager initialized successfully");
    }

    return true;
}

bool SafetyManager::initializeWatchdog() {
    watchdog_ = WatchdogFactory::createWatchdog(timer_);
    return watchdog_ != nullptr;
}

bool SafetyManager::executeSafetyChecks() {
    if (!initialized_) return false;

    uint32_t current_time = timer_ ? timer_->millis() : 0;
    bool all_checks_passed = true;

    // Perform periodic health checks
    if (current_time - last_health_check_time_ >= config_.health_check_interval_ms) {
        all_checks_passed &= performHealthCheck();
        last_health_check_time_ = current_time;
    }

    // Perform periodic memory checks
    if (config_.enable_memory_monitoring &&
        current_time - last_memory_check_time_ >= config_.memory_check_interval_ms) {
        all_checks_passed &= performMemoryChecks();
        last_memory_check_time_ = current_time;
    }

    // Feed watchdog if health checks pass and we have a watchdog manager
    if (all_checks_passed && watchdog_manager_) {
        watchdog_manager_->checkHealthAndFeed();
    }

    return all_checks_passed;
}

bool SafetyManager::reportError(ErrorHandling::ErrorCode code,
                               ErrorHandling::ErrorSeverity severity,
                               const char* message,
                               const char* file, int line) {
    if (!error_handler_) {
        return false;
    }

    ErrorHandling::ErrorContext context{
        code, severity, message, file, line,
        timer_ ? timer_->millis() : 0,
        nullptr
    };

    bool handled = error_handler_->handleError(context);

    // If this is a critical error, enter fail-safe mode
    if (severity >= ErrorHandling::ErrorSeverity::CRITICAL) {
        fail_safe_mode_ = true;
    }

    return handled;
}

bool SafetyManager::isInFailSafeMode() const {
    return fail_safe_mode_ || (error_handler_ && !error_handler_->attemptRecovery());
}

bool SafetyManager::attemptRecovery() {
    if (!fail_safe_mode_) return true;

    // Check if error handler allows recovery
    if (error_handler_ && !error_handler_->attemptRecovery()) {
        return false;
    }

    // Check watchdog manager recovery
    if (watchdog_manager_ && !watchdog_manager_->attemptRecovery()) {
        return false;
    }

    // Perform health check to ensure system is stable
    if (!performHealthCheck()) {
        return false;
    }

    fail_safe_mode_ = false;

    if (log_manager_) {
        log_manager_->log(ComponentLoggingId::ApplicationLoggingId,
                         SeverityLevel::info,
                         "Safety manager recovery successful");
    }

    return true;
}

SafetyManager::SafetyStatus SafetyManager::getSafetyStatus() const {
    SafetyStatus status{};
    status.watchdog_active = (watchdog_ && watchdog_->isActive());
    status.memory_ok = !MemorySafety::MemoryMonitor::isLowMemory();
    status.stack_ok = !MemorySafety::MemoryMonitor::StackGuard::isStackOverflowRisk();
    status.in_fail_safe_mode = isInFailSafeMode();
    status.error_count = 0;  // Would need to track this
    status.free_heap = MemorySafety::MemoryMonitor::getFreeHeap();
    status.fragmentation_ratio = MemorySafety::MemoryMonitor::getFragmentationRatio();

    // Initialize watchdog_status with default values
    status.watchdog_status = WatchdogManager::Status{
        false,  // active
        0,      // time_remaining_ms
        false,  // last_health_check_passed
        0       // consecutive_failures
    };

    if (watchdog_manager_) {
        status.watchdog_status = watchdog_manager_->getStatus();
    }

    return status;
}

void SafetyManager::registerHealthCheck(bool (*check_function)()) {
    custom_health_check_ = check_function;
    if (watchdog_manager_) {
        watchdog_manager_->registerHealthCheck(check_function);
    }
}

void SafetyManager::feedWatchdog() {
    if (watchdog_manager_) {
        watchdog_manager_->feed();
    }
}

CriticalSectionGuard SafetyManager::createCriticalSectionGuard() {
    return CriticalSectionGuard(watchdog_manager_);
}

bool SafetyManager::performHealthCheck() {
    bool healthy = true;

    // Memory health check
    if (config_.enable_memory_monitoring) {
        if (MemorySafety::MemoryMonitor::isLowMemory()) {
            reportError(ErrorHandling::ErrorCode::MEMORY_ALLOCATION_FAILED,
                       ErrorHandling::ErrorSeverity::ERROR,
                       "Low memory condition detected");
            healthy = false;
        }
    }

    // Stack health check
    if (config_.enable_stack_monitoring) {
        if (MemorySafety::MemoryMonitor::StackGuard::isStackOverflowRisk()) {
            reportError(ErrorHandling::ErrorCode::STACK_OVERFLOW,
                       ErrorHandling::ErrorSeverity::CRITICAL,
                       "Stack overflow risk detected");
            healthy = false;
        }
    }

    // Custom health check
    if (custom_health_check_ && !custom_health_check_()) {
        reportError(ErrorHandling::ErrorCode::HEALTH_CHECK_FAILED,
                   ErrorHandling::ErrorSeverity::ERROR,
                   "Custom health check failed");
        healthy = false;
    }

    return healthy;
}

bool SafetyManager::performMemoryChecks() {
    bool memory_ok = true;

    // Check for memory corruption indicators
    uint32_t free_heap = MemorySafety::MemoryMonitor::getFreeHeap();
    uint32_t total_heap = MemorySafety::MemoryMonitor::getTotalHeap();

    // Warn if heap usage is too high (>90%)
    if (total_heap > 0 && (free_heap * 100 / total_heap) < 10) {
        reportError(ErrorHandling::ErrorCode::MEMORY_ALLOCATION_FAILED,
                   ErrorHandling::ErrorSeverity::WARNING,
                   "High memory usage detected (>90% heap used)");
    }

    // Check fragmentation
    float fragmentation = MemorySafety::MemoryMonitor::getFragmentationRatio();
    if (fragmentation > 0.5f) {  // More than 50% fragmentation
        reportError(ErrorHandling::ErrorCode::HEAP_CORRUPTION,
                   ErrorHandling::ErrorSeverity::WARNING,
                   "High heap fragmentation detected");
    }

    return memory_ok;
}

} // namespace bpm
} // namespace sparetools