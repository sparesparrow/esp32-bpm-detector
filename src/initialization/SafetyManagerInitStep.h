#pragma once

#include "shared/InitStep.h"
#include "safety/SafetyManager.h"
#include "interfaces/ITimer.h"
#include "logging/LogManager.h"
// #include <memory> // Temporarily removed for compilation

namespace sparetools {
namespace bpm {

/**
 * @brief Initialization step for the safety manager
 *
 * Sets up comprehensive safety monitoring including watchdog,
 * error handling, and health checks.
 */
class SafetyManagerInitStep : public InitStep {
public:
    SafetyManagerInitStep(ITimer* timer, LogManager* log_manager);
    ~SafetyManagerInitStep() override = default;

    SafetyManager* getSafetyManager() { return safety_manager_; }

private:
    ITimer* timer_;  // Non-owning pointer - managed externally
    LogManager* log_manager_;  // Non-owning pointer - managed externally
    SafetyManager* safety_manager_;
};

} // namespace bpm
} // namespace sparetools