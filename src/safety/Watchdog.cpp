#include "Watchdog.h"
#include "interfaces/IPlatform.h"
#include "platforms/factory/PlatformFactory.h"

#ifdef PLATFORM_ESP32
#include <esp_task_wdt.h>
#endif

namespace sparetools {
namespace bpm {

// Software Watchdog Implementation
SoftwareWatchdog::SoftwareWatchdog(ITimer* timer)
    : timer_(timer), timeout_ms_(0), last_feed_time_(0), active_(false) {
}

SoftwareWatchdog::~SoftwareWatchdog() {
    active_ = false;
}

bool SoftwareWatchdog::initialize(uint32_t timeout_ms) {
    if (!timer_) return false;

    timeout_ms_ = timeout_ms;
    last_feed_time_ = timer_->millis();
    active_ = true;
    return true;
}

void SoftwareWatchdog::feed() {
    if (active_ && timer_) {
        last_feed_time_ = timer_->millis();
    }
}

void SoftwareWatchdog::forceReset() {
    // Force system reset through platform abstraction
    auto platform = PlatformFactory::getPlatform();
    if (platform) {
        platform->restart();
    }
}

uint32_t SoftwareWatchdog::getTimeRemaining() const {
    if (!active_ || !timer_) return 0;

    uint32_t current_time = timer_->millis();
    uint32_t elapsed = current_time - last_feed_time_;

    if (elapsed >= timeout_ms_) {
        return 0;  // Already timed out
    }

    return timeout_ms_ - elapsed;
}

bool SoftwareWatchdog::isActive() const {
    return active_;
}

void SoftwareWatchdog::watchdogTimerCallback(void* context) {
    auto* watchdog = static_cast<SoftwareWatchdog*>(context);
    if (watchdog && watchdog->getTimeRemaining() == 0) {
        // Watchdog timeout - force reset
        watchdog->forceReset();
    }
}

// Watchdog Manager Implementation
WatchdogManager::WatchdogManager(IWatchdog* watchdog)
    : watchdog_(watchdog), health_check_(nullptr), last_feed_time_(0),
      consecutive_failures_(0), in_fail_safe_mode_(false) {
}

WatchdogManager::~WatchdogManager() {
    // Ensure watchdog is fed before destruction
    if (watchdog_) {
        watchdog_->feed();
    }
}

bool WatchdogManager::initialize(uint32_t timeout_ms) {
    if (!watchdog_) return false;

    bool success = watchdog_->initialize(timeout_ms);
    if (success) {
        last_feed_time_ = 0;  // Will be set on first feed
        consecutive_failures_ = 0;
        in_fail_safe_mode_ = false;
    }
    return success;
}

void WatchdogManager::registerHealthCheck(bool (*check_function)()) {
    health_check_ = check_function;
}

void WatchdogManager::feed() {
    if (watchdog_) {
        watchdog_->feed();
        consecutive_failures_ = 0;  // Reset failure count on successful feed
    }
}

bool WatchdogManager::checkHealthAndFeed() {
    bool healthy = true;

    // Perform health check if registered
    if (health_check_) {
        healthy = health_check_();
    }

    // Additional basic health checks
    healthy &= !MemorySafety::MemoryMonitor::isLowMemory();

    if (healthy) {
        feed();
        return true;
    } else {
        consecutive_failures_++;
        if (consecutive_failures_ >= MAX_CONSECUTIVE_FAILURES) {
            enterFailSafeMode();
        }
        return false;
    }
}

WatchdogManager::Status WatchdogManager::getStatus() const {
    Status status;
    status.active = watchdog_ ? watchdog_->isActive() : false;
    status.time_remaining_ms = watchdog_ ? watchdog_->getTimeRemaining() : 0;
    status.last_health_check_passed = (consecutive_failures_ == 0);
    status.consecutive_failures = consecutive_failures_;
    return status;
}

void WatchdogManager::enterFailSafeMode() {
    if (in_fail_safe_mode_) return;

    in_fail_safe_mode_ = true;
    // In fail-safe mode, we still feed the watchdog but reduce functionality
    // The application should detect this state and operate in degraded mode
    feed();  // Keep system alive but mark as fail-safe
}

bool WatchdogManager::attemptRecovery() {
    if (!in_fail_safe_mode_) return true;

    // Perform recovery checks
    bool can_recover = true;
    can_recover &= !MemorySafety::MemoryMonitor::isLowMemory();
    can_recover &= (consecutive_failures_ == 0);

    if (can_recover) {
        in_fail_safe_mode_ = false;
        consecutive_failures_ = 0;
        return true;
    }

    return false;
}

// Critical Section Guard Implementation
CriticalSectionGuard::CriticalSectionGuard(WatchdogManager* watchdog_manager)
    : watchdog_manager_(watchdog_manager), original_timeout_(0) {
    if (watchdog_manager_) {
        // Store original timeout and extend it for critical section
        auto status = watchdog_manager_->getStatus();
        original_timeout_ = status.time_remaining_ms;
        extendTimeout(5000);  // Add 5 seconds for critical section
    }
}

CriticalSectionGuard::~CriticalSectionGuard() {
    if (watchdog_manager_) {
        // Restore original timeout behavior
        watchdog_manager_->feed();
    }
}

void CriticalSectionGuard::extendTimeout(uint32_t additional_ms) {
    if (watchdog_manager_) {
        // Feed watchdog to extend timeout
        watchdog_manager_->feed();
    }
}

} // namespace bpm
} // namespace sparetools