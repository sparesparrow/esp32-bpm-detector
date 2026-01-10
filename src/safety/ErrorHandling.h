#pragma once

#include <cstdint>
#include <string>
#include <functional>
#include "logging/LogManager.h"

namespace sparetools {
namespace bpm {

/**
 * @brief Comprehensive error handling system for embedded systems
 *
 * Provides structured error codes, recovery strategies, and fail-safe mechanisms
 * designed for resource-constrained embedded environments.
 */
class ErrorHandling {
public:
    /**
     * @brief Error codes for different subsystems
     */
    enum class ErrorCode : uint16_t {
        // General errors
        SUCCESS = 0,
        UNKNOWN_ERROR = 1,
        INVALID_PARAMETER = 2,
        TIMEOUT = 3,
        RESOURCE_UNAVAILABLE = 4,

        // Memory errors
        MEMORY_ALLOCATION_FAILED = 100,
        MEMORY_CORRUPTION = 101,
        STACK_OVERFLOW = 102,
        HEAP_CORRUPTION = 103,

        // Audio/BPM detection errors
        AUDIO_INIT_FAILED = 200,
        AUDIO_BUFFER_OVERFLOW = 201,
        FFT_COMPUTATION_ERROR = 202,
        BPM_DETECTION_FAILED = 203,

        // Platform/HAL errors
        PLATFORM_INIT_FAILED = 300,
        SERIAL_INIT_FAILED = 301,
        TIMER_INIT_FAILED = 302,
        GPIO_INIT_FAILED = 303,

        // Communication errors
        SERIAL_TRANSMIT_FAILED = 400,
        SERIAL_RECEIVE_FAILED = 401,
        PROTOCOL_ERROR = 402,
        BUFFER_OVERFLOW = 403,

        // FreeRTOS/Task errors
        TASK_CREATION_FAILED = 500,
        TASK_STACK_OVERFLOW = 501,
        QUEUE_FULL = 502,
        MUTEX_TIMEOUT = 503,

        // Safety/Critical errors
        WATCHDOG_TIMEOUT = 600,
        HEALTH_CHECK_FAILED = 601,
        FAIL_SAFE_MODE = 602,
        SYSTEM_RESET_REQUIRED = 603
    };

    /**
     * @brief Error severity levels
     */
    enum class ErrorSeverity : uint8_t {
        DEBUG = 0,      // Debug information, no action needed
        INFO = 1,       // Informational, log and continue
        WARNING = 2,    // Warning, may need attention but continue
        ERROR = 3,      // Error, attempt recovery
        CRITICAL = 4,   // Critical, enter fail-safe mode
        FATAL = 5       // Fatal, system reset required
    };

    /**
     * @brief Recovery strategy enumeration
     */
    enum class RecoveryStrategy : uint8_t {
        NONE = 0,           // No recovery possible
        RETRY = 1,          // Retry operation
        RESET_COMPONENT = 2, // Reset affected component
        RESET_SUBSYSTEM = 3, // Reset entire subsystem
        FAIL_SAFE = 4,      // Enter fail-safe mode
        SYSTEM_RESET = 5    // Full system reset
    };

    /**
     * @brief Error context structure
     */
    struct ErrorContext {
        ErrorCode code;
        ErrorSeverity severity;
        const char* message;
        const char* file;
        int line;
        uint32_t timestamp;
        void* context_data;
    };

    /**
     * @brief Recovery action structure
     */
    struct RecoveryAction {
        RecoveryStrategy strategy;
        std::function<bool()> recovery_function;
        uint32_t max_retries;
        uint32_t retry_delay_ms;
    };

    /**
     * @brief Error handler interface
     */
    class IErrorHandler {
    public:
        virtual ~IErrorHandler() = default;
        virtual bool handleError(const ErrorContext& error) = 0;
        virtual RecoveryAction getRecoveryAction(ErrorCode code) = 0;
        virtual void enterFailSafeMode() = 0;
        virtual bool attemptRecovery() = 0;
    };

    /**
     * @brief Default error handler implementation
     */
    class DefaultErrorHandler : public IErrorHandler {
    public:
        explicit DefaultErrorHandler(LogManager* log_manager);
        ~DefaultErrorHandler() override = default;

        bool handleError(const ErrorContext& error) override;
        RecoveryAction getRecoveryAction(ErrorCode code) override;
        void enterFailSafeMode() override;
        bool attemptRecovery() override;

    private:
        LogManager* log_manager_;
        bool in_fail_safe_mode_;
        uint32_t error_count_;
        uint32_t last_error_time_;
    };

    /**
     * @brief RAII error context manager
     */
    class ErrorScope {
    public:
        ErrorScope(IErrorHandler* handler, const char* scope_name);
        ~ErrorScope();

        /**
         * @brief Report an error in this scope
         */
        bool reportError(ErrorCode code, ErrorSeverity severity,
                        const char* message, const char* file = nullptr, int line = 0);

        /**
         * @brief Check if scope is in error state
         */
        bool hasError() const;

        /**
         * @brief Clear error state
         */
        void clearError();

    private:
        IErrorHandler* handler_;
        const char* scope_name_;
        bool has_error_;
        ErrorCode last_error_;
    };

    /**
     * @brief Utility functions for error handling
     */
    static const char* errorCodeToString(ErrorCode code);
    static const char* severityToString(ErrorSeverity severity);
    static ErrorSeverity getSeverityForCode(ErrorCode code);

    /**
     * @brief Error reporting macros for convenient use
     */
#define REPORT_ERROR(handler, code, severity, message) \
    (handler)->reportError(code, severity, message, __FILE__, __LINE__)

#define REPORT_ERROR_IF(condition, handler, code, severity, message) \
    if (condition) { REPORT_ERROR(handler, code, severity, message); }

#define CHECK_NULL_RETURN(ptr, handler, message) \
    if (!(ptr)) { \
        REPORT_ERROR(handler, ErrorHandling::ErrorCode::INVALID_PARAMETER, \
                    ErrorHandling::ErrorSeverity::ERROR, message); \
        return false; \
    }

#define CHECK_SUCCESS_RETURN(result, handler, message) \
    if (!(result)) { \
        REPORT_ERROR(handler, ErrorHandling::ErrorCode::UNKNOWN_ERROR, \
                    ErrorHandling::ErrorSeverity::ERROR, message); \
        return false; \
    }
};

} // namespace bpm
} // namespace sparetools