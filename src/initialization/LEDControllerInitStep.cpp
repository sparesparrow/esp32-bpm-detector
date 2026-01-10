#include "LEDControllerInitStep.h"
#include "platforms/factory/LEDControllerFactory.h"
#include <new>

namespace sparetools {
namespace bpm {

LEDControllerInitStep::LEDControllerInitStep(LogManager* log_manager)
    : log_manager_(log_manager) {
    // LED controller initialization
    led_controller_ = LEDControllerFactory::createLEDController();

    if (led_controller_) {
        if (led_controller_->begin()) {
            // Set initial status to booting
            led_controller_->showStatus(LedStatus::LED_STATUS_BOOTING);

            if (log_manager_) {
                log_manager_->log(ComponentLoggingId::ApplicationLoggingId,
                                 SeverityLevel::info,
                                 "LED controller initialized successfully");
            }
            finished = true;
        } else {
            // LED controller failed to initialize
            if (log_manager_) {
                log_manager_->log(ComponentLoggingId::ApplicationLoggingId,
                                 SeverityLevel::error,
                                 "LED controller begin() failed");
            }
            LEDControllerFactory::destroyLEDController(led_controller_);
            led_controller_ = nullptr;
            finished = false;
        }
    } else {
        // Failed to create LED controller
        if (log_manager_) {
            log_manager_->log(ComponentLoggingId::ApplicationLoggingId,
                             SeverityLevel::error,
                             "Failed to create LED controller");
        }
        finished = false;
    }
}

LEDControllerInitStep::~LEDControllerInitStep() {
    if (led_controller_) {
        LEDControllerFactory::destroyLEDController(led_controller_);
        led_controller_ = nullptr;
    }
}

bool LEDControllerInitStep::execute() {
    // Initialization happens in constructor, just return finished status
    return finished;
}

} // namespace bpm
} // namespace sparetools