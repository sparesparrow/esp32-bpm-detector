#pragma once

#include "shared/InitStep.h"
#include "performance/PerformanceProfiler.h"
#include "interfaces/ITimer.h"
// #include <memory> // Temporarily removed for compilation

namespace sparetools {
namespace bpm {

/**
 * @brief Initialization step for the performance profiler
 *
 * Sets up comprehensive performance monitoring and optimization
 * tracking for the embedded system.
 */
class PerformanceProfilerInitStep : public InitStep {
public:
    explicit PerformanceProfilerInitStep(ITimer* timer);
    ~PerformanceProfilerInitStep() override = default;

    PerformanceProfiler* getPerformanceProfiler() { return performance_profiler_; }

private:
    ITimer* timer_;  // Non-owning pointer - managed externally
    PerformanceProfiler* performance_profiler_;
};

} // namespace bpm
} // namespace sparetools