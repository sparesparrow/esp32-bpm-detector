#include <gtest/gtest.h>
#include "safety/SafetyManager.h"
#include "safety/ErrorHandling.h"
#include "interfaces/ITimer.h"

// Mock timer for testing
class MockTimer : public sparetools::bpm::ITimer {
public:
    uint32_t millis() override { return current_time_; }
    uint32_t micros() override { return current_time_ * 1000; }
    void delay(uint32_t ms) override { current_time_ += ms; }

    void setTime(uint32_t time) { current_time_ = time; }
    void advanceTime(uint32_t ms) { current_time_ += ms; }

private:
    uint32_t current_time_ = 0;
};

namespace sparetools {
namespace bpm {

// Test fixture for SafetyManager tests
class SafetyManagerTest : public ::testing::Test {
protected:
    void SetUp() override {
        timer_ = new MockTimer();
        safety_manager_ = new SafetyManager();
    }

    void TearDown() override {
        delete safety_manager_;
        delete timer_;
    }

    MockTimer* timer_;
    SafetyManager* safety_manager_;
};

// Test initialization
TEST_F(SafetyManagerTest, Initialization) {
    SafetyManager::Config config;
    config.watchdog_timeout_ms = 10000;

    EXPECT_TRUE(safety_manager_->initialize(timer_, nullptr, config));
}

// Test error reporting
TEST_F(SafetyManagerTest, ErrorReporting) {
    SafetyManager::Config config;
    safety_manager_->initialize(timer_, nullptr, config);

    // Test error reporting
    bool result = safety_manager_->reportError(
        ErrorHandling::ErrorCode::MEMORY_ALLOCATION_FAILED,
        ErrorHandling::ErrorSeverity::ERROR,
        "Test memory allocation failure"
    );

    EXPECT_TRUE(result);
}

// Test health checks
TEST_F(SafetyManagerTest, HealthChecks) {
    SafetyManager::Config config;
    safety_manager_->initialize(timer_, nullptr, config);

    // Test health check execution
    bool healthy = safety_manager_->executeSafetyChecks();
    EXPECT_TRUE(healthy);
}

// Test fail-safe mode
TEST_F(SafetyManagerTest, FailSafeMode) {
    SafetyManager::Config config;
    safety_manager_->initialize(timer_, nullptr, config);

    // Initially not in fail-safe mode
    EXPECT_FALSE(safety_manager_->isInFailSafeMode());

    // Report critical error to trigger fail-safe
    safety_manager_->reportError(
        ErrorHandling::ErrorCode::SYSTEM_RESET_REQUIRED,
        ErrorHandling::ErrorSeverity::CRITICAL,
        "Critical system error"
    );

    // Should now be in fail-safe mode
    EXPECT_TRUE(safety_manager_->isInFailSafeMode());
}

// Test safety status
TEST_F(SafetyManagerTest, SafetyStatus) {
    SafetyManager::Config config;
    safety_manager_->initialize(timer_, nullptr, config);

    auto status = safety_manager_->getSafetyStatus();

    EXPECT_FALSE(status.in_fail_safe_mode);
    EXPECT_TRUE(status.memory_ok);  // Mock environment
    EXPECT_TRUE(status.stack_ok);   // Mock environment
}

// Test watchdog feeding
TEST_F(SafetyManagerTest, WatchdogFeeding) {
    SafetyManager::Config config;
    safety_manager_->initialize(timer_, nullptr, config);

    // This should not crash
    safety_manager_->feedWatchdog();

    auto status = safety_manager_->getSafetyStatus();
    EXPECT_FALSE(status.watchdog_status.consecutive_failures > 0);
}

} // namespace bpm
} // namespace sparetools

// Main function for running tests
int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}