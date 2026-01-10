#include "PerformanceProfilerInitStep.h"
#include <new>

namespace sparetools {
namespace bpm {

PerformanceProfilerInitStep::PerformanceProfilerInitStep(ITimer* timer)
    : timer_(timer), performance_profiler_(nullptr) {
    // Initialize performance profiler immediately
    performance_profiler_ = new (std::nothrow) PerformanceProfiler();

    if (performance_profiler_) {
        if (performance_profiler_->initialize(timer_)) {
            finished = true;
        } else {
            // Performance profiler initialization failed
            finished = false;
        }
    } else {
        // Failed to allocate performance profiler
        finished = false;
    }
}

} // namespace bpm
} // namespace sparetools