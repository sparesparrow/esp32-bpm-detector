#include "PowerManagerInitStep.h"
#include <new>

namespace sparetools {
namespace bpm {

PowerManagerInitStep::PowerManagerInitStep(ITimer* timer)
    : timer_(timer), power_manager_(nullptr) {
    // Initialize power manager immediately
    power_manager_ = new (std::nothrow) PowerManager();

    if (power_manager_) {
        PowerManager::Config config;
        config.default_mode = PowerManager::PowerMode::BALANCED;
        config.idle_timeout_ms = 30000;      // 30 seconds
        config.sleep_timeout_ms = 300000;    // 5 minutes
        config.enable_dynamic_frequency = true;
        config.enable_peripheral_powerdown = true;
        config.enable_wifi_power_management = false;  // WiFi disabled in this project

        if (power_manager_->initialize(timer_, config)) {
            finished = true;
        } else {
            // Power manager initialization failed
            finished = false;
        }
    } else {
        // Failed to allocate power manager
        finished = false;
    }
}

} // namespace bpm
} // namespace sparetools