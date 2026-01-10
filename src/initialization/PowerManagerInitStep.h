#pragma once

#include "shared/InitStep.h"
#include "safety/PowerManager.h"
#include "interfaces/ITimer.h"
// #include <memory> // Temporarily removed for compilation

namespace sparetools {
namespace bpm {

/**
 * @brief Initialization step for the power manager
 *
 * Sets up intelligent power management based on system activity
 * and workload requirements.
 */
class PowerManagerInitStep : public InitStep {
public:
    explicit PowerManagerInitStep(ITimer* timer);
    ~PowerManagerInitStep() override = default;

    PowerManager* getPowerManager() { return power_manager_; }

private:
    ITimer* timer_;  // Non-owning pointer - managed externally
    PowerManager* power_manager_;
};

} // namespace bpm
} // namespace sparetools