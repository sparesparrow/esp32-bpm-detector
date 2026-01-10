#include <gtest/gtest.h>
#include "safety/ErrorHandling.h"

namespace sparetools {
namespace bpm {

// Test fixture for ErrorHandling tests
class ErrorHandlingTest : public ::testing::Test {
protected:
    void SetUp() override {
        error_handler_ = new ErrorHandling::DefaultErrorHandler(nullptr);
    }

    void TearDown() override {
        delete error_handler_;
    }

    ErrorHandling::DefaultErrorHandler* error_handler_;
};

// Test error code to string conversion
TEST_F(ErrorHandlingTest, ErrorCodeToString) {
    EXPECT_STREQ("SUCCESS",
                 ErrorHandling::errorCodeToString(ErrorHandling::ErrorCode::SUCCESS));
    EXPECT_STREQ("MEMORY_ALLOCATION_FAILED",
                 ErrorHandling::errorCodeToString(ErrorHandling::ErrorCode::MEMORY_ALLOCATION_FAILED));
    EXPECT_STREQ("WATCHDOG_TIMEOUT",
                 ErrorHandling::errorCodeToString(ErrorHandling::ErrorCode::WATCHDOG_TIMEOUT));
}

// Test severity to string conversion
TEST_F(ErrorHandlingTest, SeverityToString) {
    EXPECT_STREQ("DEBUG",
                 ErrorHandling::severityToString(ErrorHandling::ErrorSeverity::DEBUG));
    EXPECT_STREQ("CRITICAL",
                 ErrorHandling::severityToString(ErrorHandling::ErrorSeverity::CRITICAL));
    EXPECT_STREQ("FATAL",
                 ErrorHandling::severityToString(ErrorHandling::ErrorSeverity::FATAL));
}

// Test severity for error codes
TEST_F(ErrorHandlingTest, GetSeverityForCode) {
    EXPECT_EQ(ErrorHandling::ErrorSeverity::DEBUG,
              ErrorHandling::getSeverityForCode(ErrorHandling::ErrorCode::SUCCESS));
    EXPECT_EQ(ErrorHandling::ErrorSeverity::ERROR,
              ErrorHandling::getSeverityForCode(ErrorHandling::ErrorCode::MEMORY_ALLOCATION_FAILED));
    EXPECT_EQ(ErrorHandling::ErrorSeverity::CRITICAL,
              ErrorHandling::getSeverityForCode(ErrorHandling::ErrorCode::MEMORY_CORRUPTION));
    EXPECT_EQ(ErrorHandling::ErrorSeverity::FATAL,
              ErrorHandling::getSeverityForCode(ErrorHandling::ErrorCode::SYSTEM_RESET_REQUIRED));
}

// Test error context
TEST_F(ErrorHandlingTest, ErrorContext) {
    ErrorHandling::ErrorContext context{
        ErrorHandling::ErrorCode::INVALID_PARAMETER,
        ErrorHandling::ErrorSeverity::WARNING,
        "Test error message",
        "test_file.cpp",
        42,
        12345,
        nullptr
    };

    EXPECT_EQ(ErrorHandling::ErrorCode::INVALID_PARAMETER, context.code);
    EXPECT_EQ(ErrorHandling::ErrorSeverity::WARNING, context.severity);
    EXPECT_STREQ("Test error message", context.message);
    EXPECT_STREQ("test_file.cpp", context.file);
    EXPECT_EQ(42, context.line);
    EXPECT_EQ(12345u, context.timestamp);
}

// Test error handler
TEST_F(ErrorHandlingTest, ErrorHandler) {
    ErrorHandling::ErrorContext context{
        ErrorHandling::ErrorCode::TIMEOUT,
        ErrorHandling::ErrorSeverity::ERROR,
        "Test timeout error",
        "test_file.cpp",
        100,
        0,
        nullptr
    };

    // Error handler should handle the error without crashing
    bool handled = error_handler_->handleError(context);
    EXPECT_TRUE(handled);
}

// Test recovery action
TEST_F(ErrorHandlingTest, RecoveryAction) {
    auto action = error_handler_->getRecoveryAction(ErrorHandling::ErrorCode::MEMORY_ALLOCATION_FAILED);

    EXPECT_EQ(ErrorHandling::RecoveryStrategy::RESET_COMPONENT, action.strategy);
    EXPECT_EQ(3u, action.max_retries);
    EXPECT_EQ(1000u, action.retry_delay_ms);
}

// Test different recovery strategies
TEST_F(ErrorHandlingTest, RecoveryStrategies) {
    // Test retry strategy
    auto retry_action = error_handler_->getRecoveryAction(ErrorHandling::ErrorCode::TIMEOUT);
    EXPECT_EQ(ErrorHandling::RecoveryStrategy::RETRY, retry_action.strategy);
    EXPECT_EQ(5u, retry_action.max_retries);

    // Test system reset strategy
    auto reset_action = error_handler_->getRecoveryAction(ErrorHandling::ErrorCode::SYSTEM_RESET_REQUIRED);
    EXPECT_EQ(ErrorHandling::RecoveryStrategy::SYSTEM_RESET, reset_action.strategy);
}

// Test fail-safe mode
TEST_F(ErrorHandlingTest, FailSafeMode) {
    // Initially not in fail-safe mode
    EXPECT_FALSE(error_handler_->attemptRecovery());

    // Enter fail-safe mode
    error_handler_->enterFailSafeMode();

    // Should now be in fail-safe mode
    EXPECT_FALSE(error_handler_->attemptRecovery());
}

} // namespace bpm
} // namespace sparetools

// Main function for running tests
int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}