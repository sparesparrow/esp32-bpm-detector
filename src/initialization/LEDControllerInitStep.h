#pragma once

#include "shared/InitStep.h"
#include "interfaces/ILEDController.h"
#include "logging/LogManager.h"

namespace sparetools {
namespace bpm {

/**
 * @brief Initialization step for the LED controller
 *
 * Sets up the LED strip controller for visual feedback during system operation.
 */
class LEDControllerInitStep : public InitStep {
public:
    LEDControllerInitStep(LogManager* log_manager);
    ~LEDControllerInitStep() override;

    ILEDController* getLEDController() { return led_controller_; }

    bool execute() override;
    const char* getName() const override { return "LEDControllerInitStep"; }

private:
    LogManager* log_manager_;  // Non-owning pointer - managed externally
    ILEDController* led_controller_;
};

} // namespace bpm
} // namespace sparetools