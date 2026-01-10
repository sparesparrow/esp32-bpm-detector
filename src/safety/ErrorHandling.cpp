#include "ErrorHandling.h"
#include <cstring>

namespace sparetools {
namespace bpm {

// Error Handler Implementation
ErrorHandling::DefaultErrorHandler::DefaultErrorHandler(LogManager* log_manager)
    : log_manager_(log_manager), in_fail_safe_mode_(false),
      error_count_(0), last_error_time_(0) {
}

bool ErrorHandling::DefaultErrorHandler::handleError(const ErrorHandling::ErrorContext& error) {
    if (!log_manager_) return false;

    // Map error severity to log level
    SeverityLevel log_level = SeverityLevel::info;
    switch (error.severity) {
        case ErrorSeverity::DEBUG:
            log_level = SeverityLevel::debug;
            break;
        case ErrorSeverity::INFO:
            log_level = SeverityLevel::info;
            break;
        case ErrorSeverity::WARNING:
            log_level = SeverityLevel::warning;
            break;
        case ErrorSeverity::ERROR:
        case ErrorSeverity::CRITICAL:
            log_level = SeverityLevel::error;
            break;
        case ErrorSeverity::FATAL:
            log_level = SeverityLevel::critical;
            break;
    }

    // Create detailed error message
    char error_msg[256];
    snprintf(error_msg, sizeof(error_msg),
             "Error [%s] %s: %s (file: %s, line: %d)",
             ErrorHandling::severityToString(error.severity),
             ErrorHandling::errorCodeToString(error.code),
             error.message,
             error.file ? error.file : "unknown",
             error.line);

    log_manager_->log(ComponentLoggingId::ApplicationLoggingId, log_level, error_msg);

    // Update error statistics
    error_count_++;
    last_error_time_ = error.timestamp;

    // Handle critical errors
    if (error.severity >= ErrorSeverity::CRITICAL) {
        enterFailSafeMode();
        return false;  // Critical error - recovery needed
    }

    return true;  // Error handled
}

ErrorHandling::RecoveryAction ErrorHandling::DefaultErrorHandler::getRecoveryAction(ErrorHandling::ErrorCode code) {
    ErrorHandling::RecoveryAction action;
    action.max_retries = 3;
    action.retry_delay_ms = 1000;

    switch (code) {
        case ErrorHandling::ErrorCode::MEMORY_ALLOCATION_FAILED:
            action.strategy = RecoveryStrategy::RESET_COMPONENT;
            action.recovery_function = []() {
                // Force garbage collection if available
                return true;  // Placeholder - implement platform-specific cleanup
            };
            break;

        case ErrorCode::AUDIO_INIT_FAILED:
        case ErrorCode::PLATFORM_INIT_FAILED:
            action.strategy = RecoveryStrategy::RESET_SUBSYSTEM;
            action.recovery_function = []() {
                // Reinitialize audio/platform subsystem
                return true;  // Placeholder
            };
            break;

        case ErrorCode::TIMEOUT:
        case ErrorCode::SERIAL_TRANSMIT_FAILED:
            action.strategy = RecoveryStrategy::RETRY;
            action.max_retries = 5;
            action.retry_delay_ms = 500;
            break;

        case ErrorCode::WATCHDOG_TIMEOUT:
        case ErrorCode::SYSTEM_RESET_REQUIRED:
            action.strategy = RecoveryStrategy::SYSTEM_RESET;
            action.recovery_function = []() {
                // Trigger system reset
                return false;  // Reset will happen
            };
            break;

        default:
            action.strategy = RecoveryStrategy::FAIL_SAFE;
            action.recovery_function = [this]() {
                enterFailSafeMode();
                return true;
            };
            break;
    }

    return action;
}

void ErrorHandling::DefaultErrorHandler::enterFailSafeMode() {
    if (in_fail_safe_mode_) return;

    in_fail_safe_mode_ = true;

    if (log_manager_) {
        log_manager_->log(ComponentLoggingId::ApplicationLoggingId,
                         SeverityLevel::critical,
                         "Entering fail-safe mode due to critical errors");
    }

    // In fail-safe mode:
    // - Disable non-essential features
    // - Reduce sampling rate
    // - Use minimal processing
    // - Continue basic monitoring
}

bool ErrorHandling::DefaultErrorHandler::attemptRecovery() {
    if (!in_fail_safe_mode_) return true;

    // Check if conditions are safe for recovery
    bool can_recover = (error_count_ < 10);  // Don't recover if too many errors

    if (can_recover) {
        in_fail_safe_mode_ = false;
        error_count_ = 0;

        if (log_manager_) {
            log_manager_->log(ComponentLoggingId::ApplicationLoggingId,
                             SeverityLevel::info,
                             "Recovery from fail-safe mode successful");
        }
        return true;
    }

    return false;
}

// Error Scope Implementation
ErrorHandling::ErrorScope::ErrorScope(IErrorHandler* handler, const char* scope_name)
    : handler_(handler), scope_name_(scope_name), has_error_(false), last_error_(ErrorCode::SUCCESS) {
}

ErrorHandling::ErrorScope::~ErrorScope() {
    if (has_error_) {
        // Log scope exit with error
        // This would be improved with actual logging integration
    }
}

bool ErrorHandling::ErrorScope::reportError(ErrorCode code, ErrorSeverity severity,
                                           const char* message, const char* file, int line) {
    if (!handler_) return false;

    ErrorContext context{
        code, severity, message, file, line,
        0,  // timestamp - would be filled by timer
        nullptr  // context_data
    };

    has_error_ = true;
    last_error_ = code;

    return handler_->handleError(context);
}

bool ErrorHandling::ErrorScope::hasError() const {
    return has_error_;
}

void ErrorHandling::ErrorScope::clearError() {
    has_error_ = false;
    last_error_ = ErrorCode::SUCCESS;
}

// Utility Functions
const char* ErrorHandling::errorCodeToString(ErrorCode code) {
    switch (code) {
        case ErrorCode::SUCCESS: return "SUCCESS";
        case ErrorCode::UNKNOWN_ERROR: return "UNKNOWN_ERROR";
        case ErrorCode::INVALID_PARAMETER: return "INVALID_PARAMETER";
        case ErrorCode::TIMEOUT: return "TIMEOUT";
        case ErrorCode::RESOURCE_UNAVAILABLE: return "RESOURCE_UNAVAILABLE";
        case ErrorCode::MEMORY_ALLOCATION_FAILED: return "MEMORY_ALLOCATION_FAILED";
        case ErrorCode::MEMORY_CORRUPTION: return "MEMORY_CORRUPTION";
        case ErrorCode::STACK_OVERFLOW: return "STACK_OVERFLOW";
        case ErrorCode::HEAP_CORRUPTION: return "HEAP_CORRUPTION";
        case ErrorCode::AUDIO_INIT_FAILED: return "AUDIO_INIT_FAILED";
        case ErrorCode::AUDIO_BUFFER_OVERFLOW: return "AUDIO_BUFFER_OVERFLOW";
        case ErrorCode::FFT_COMPUTATION_ERROR: return "FFT_COMPUTATION_ERROR";
        case ErrorCode::BPM_DETECTION_FAILED: return "BPM_DETECTION_FAILED";
        case ErrorCode::PLATFORM_INIT_FAILED: return "PLATFORM_INIT_FAILED";
        case ErrorCode::SERIAL_INIT_FAILED: return "SERIAL_INIT_FAILED";
        case ErrorCode::TIMER_INIT_FAILED: return "TIMER_INIT_FAILED";
        case ErrorCode::GPIO_INIT_FAILED: return "GPIO_INIT_FAILED";
        case ErrorCode::SERIAL_TRANSMIT_FAILED: return "SERIAL_TRANSMIT_FAILED";
        case ErrorCode::SERIAL_RECEIVE_FAILED: return "SERIAL_RECEIVE_FAILED";
        case ErrorCode::PROTOCOL_ERROR: return "PROTOCOL_ERROR";
        case ErrorCode::BUFFER_OVERFLOW: return "BUFFER_OVERFLOW";
        case ErrorCode::TASK_CREATION_FAILED: return "TASK_CREATION_FAILED";
        case ErrorCode::TASK_STACK_OVERFLOW: return "TASK_STACK_OVERFLOW";
        case ErrorCode::QUEUE_FULL: return "QUEUE_FULL";
        case ErrorCode::MUTEX_TIMEOUT: return "MUTEX_TIMEOUT";
        case ErrorCode::WATCHDOG_TIMEOUT: return "WATCHDOG_TIMEOUT";
        case ErrorCode::HEALTH_CHECK_FAILED: return "HEALTH_CHECK_FAILED";
        case ErrorCode::FAIL_SAFE_MODE: return "FAIL_SAFE_MODE";
        case ErrorCode::SYSTEM_RESET_REQUIRED: return "SYSTEM_RESET_REQUIRED";
        default: return "UNKNOWN_ERROR_CODE";
    }
}

const char* ErrorHandling::severityToString(ErrorSeverity severity) {
    switch (severity) {
        case ErrorSeverity::DEBUG: return "DEBUG";
        case ErrorSeverity::INFO: return "INFO";
        case ErrorSeverity::WARNING: return "WARNING";
        case ErrorSeverity::ERROR: return "ERROR";
        case ErrorSeverity::CRITICAL: return "CRITICAL";
        case ErrorSeverity::FATAL: return "FATAL";
        default: return "UNKNOWN";
    }
}

ErrorHandling::ErrorSeverity ErrorHandling::getSeverityForCode(ErrorCode code) {
    switch (code) {
        case ErrorCode::SUCCESS:
            return ErrorSeverity::DEBUG;

        case ErrorCode::TIMEOUT:
        case ErrorCode::RESOURCE_UNAVAILABLE:
            return ErrorSeverity::WARNING;

        case ErrorCode::MEMORY_ALLOCATION_FAILED:
        case ErrorCode::AUDIO_INIT_FAILED:
        case ErrorCode::PLATFORM_INIT_FAILED:
        case ErrorCode::SERIAL_TRANSMIT_FAILED:
            return ErrorSeverity::ERROR;

        case ErrorCode::MEMORY_CORRUPTION:
        case ErrorCode::STACK_OVERFLOW:
        case ErrorCode::HEAP_CORRUPTION:
        case ErrorCode::TASK_STACK_OVERFLOW:
        case ErrorCode::WATCHDOG_TIMEOUT:
            return ErrorSeverity::CRITICAL;

        case ErrorCode::SYSTEM_RESET_REQUIRED:
            return ErrorSeverity::FATAL;

        default:
            return ErrorSeverity::ERROR;
    }
}

} // namespace bpm
} // namespace sparetools