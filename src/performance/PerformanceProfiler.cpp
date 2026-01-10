#include "PerformanceProfiler.h"
#include <algorithm>
#include <sstream>
#include <cstring>

namespace sparetools {
namespace bpm {

// Global instance
PerformanceProfiler* g_performance_profiler = nullptr;

// ScopeTimer implementation
PerformanceProfiler::ScopeTimer::ScopeTimer(PerformanceProfiler* profiler, const char* scope_name)
    : profiler_(profiler), scope_name_(scope_name), start_time_(0) {
    if (profiler_ && profiler_->timer_) {
        start_time_ = profiler_->timer_->micros();
        if (profiler_->isMonitoringEnabled()) {
            profiler_->startMonitoring(scope_name);
        }
    }
}

PerformanceProfiler::ScopeTimer::~ScopeTimer() {
    if (profiler_ && profiler_->isMonitoringEnabled()) {
        auto metrics = profiler_->stopMonitoring();
        PERFORMANCE_EVENT(scope_name_, metrics.execution_time_us);
    }
}

void PerformanceProfiler::ScopeTimer::addCheckpoint(const char* checkpoint_name) {
    if (profiler_ && profiler_->timer_) {
        uint32_t checkpoint_time = profiler_->timer_->micros() - start_time_;
        checkpoints_.emplace_back(checkpoint_name, checkpoint_time);
    }
}

// PerformanceProfiler implementation
bool PerformanceProfiler::initialize(ITimer* timer) {
    timer_ = timer;
    monitoring_enabled_ = true;
    currently_monitoring_ = false;
    monitoring_start_time_ = 0;

    // Initialize performance data
    performance_data_ = {0};
    execution_times_.fill(0);
    execution_time_index_ = 0;

    // Set global instance
    g_performance_profiler = this;

    return true;
}

void PerformanceProfiler::startMonitoring(const char* operation_name) {
    if (!monitoring_enabled_ || currently_monitoring_) return;

    currently_monitoring_ = true;
    current_operation_ = operation_name ? operation_name : "unnamed_operation";

    if (timer_) {
        monitoring_start_time_ = timer_->micros();
    }
}

PerformanceProfiler::Metrics PerformanceProfiler::stopMonitoring() {
    if (!currently_monitoring_) {
        return {0};  // Return empty metrics
    }

    Metrics metrics = {0};
    uint32_t end_time = timer_ ? timer_->micros() : 0;

    if (end_time >= monitoring_start_time_) {
        metrics.execution_time_us = end_time - monitoring_start_time_;
    }

    // Update statistics
    performance_data_.total_operations++;
    performance_data_.total_time_us += metrics.execution_time_us;

    if (performance_data_.total_operations == 1 ||
        metrics.execution_time_us < performance_data_.min_time_us) {
        performance_data_.min_time_us = metrics.execution_time_us;
    }

    if (metrics.execution_time_us > performance_data_.max_time_us) {
        performance_data_.max_time_us = metrics.execution_time_us;
    }

    // Update moving average
    updateMovingAverage(metrics.execution_time_us);

    // Calculate CPU utilization (simplified)
    metrics.cpu_utilization = calculateCpuUtilization();

    currently_monitoring_ = false;
    return metrics;
}

void PerformanceProfiler::recordEvent(const char* event_name, uint32_t value) {
    if (!monitoring_enabled_) return;

    // Record event in performance data
    // This is a simplified implementation - in practice, you'd want to
    // store events in a buffer for later analysis

    if (strcmp(event_name, "memory_allocation") == 0) {
        performance_data_.memory_operations++;
    } else if (strcmp(event_name, "io_operation") == 0) {
        performance_data_.io_operations++;
    }
}

PerformanceProfiler::Metrics PerformanceProfiler::getCurrentMetrics() const {
    Metrics metrics = {0};

    if (performance_data_.total_operations > 0) {
        metrics.execution_time_us = performance_data_.total_time_us / performance_data_.total_operations;
        metrics.cpu_utilization = calculateCpuUtilization();
    }

    return metrics;
}

std::vector<PerformanceProfiler::BottleneckAnalysis> PerformanceProfiler::analyzeBottlenecks() {
    std::vector<BottleneckAnalysis> bottlenecks;

    // Analyze CPU bottlenecks
    auto cpu_bottleneck = detectCpuBottleneck();
    if (cpu_bottleneck.severity > 0) {
        bottlenecks.push_back(cpu_bottleneck);
    }

    // Analyze memory bottlenecks
    auto memory_bottleneck = detectMemoryBottleneck();
    if (memory_bottleneck.severity > 0) {
        bottlenecks.push_back(memory_bottleneck);
    }

    // Analyze I/O bottlenecks
    auto io_bottleneck = detectIoBottleneck();
    if (io_bottleneck.severity > 0) {
        bottlenecks.push_back(io_bottleneck);
    }

    return bottlenecks;
}

std::vector<std::string> PerformanceProfiler::getOptimizationRecommendations() {
    std::vector<std::string> recommendations;

    auto bottlenecks = analyzeBottlenecks();

    for (const auto& bottleneck : bottlenecks) {
        if (bottleneck.severity >= 7) {
            recommendations.push_back(bottleneck.recommendation);
        }
    }

    // General recommendations
    if (performance_data_.total_operations > 100) {
        uint32_t avg_time = performance_data_.total_time_us / performance_data_.total_operations;
        if (avg_time > 10000) {  // 10ms average
            recommendations.push_back("Consider optimizing main processing loop - average execution time is high");
        }
    }

    return recommendations;
}

void PerformanceProfiler::setMonitoringEnabled(bool enabled) {
    monitoring_enabled_ = enabled;
}

bool PerformanceProfiler::isMonitoringEnabled() const {
    return monitoring_enabled_;
}

void PerformanceProfiler::resetStatistics() {
    performance_data_ = {0};
    execution_times_.fill(0);
    execution_time_index_ = 0;
}

std::string PerformanceProfiler::getPerformanceReport() {
    std::stringstream report;

    report << "=== Performance Report ===\n";
    report << "Total operations: " << performance_data_.total_operations << "\n";

    if (performance_data_.total_operations > 0) {
        uint32_t avg_time = performance_data_.total_time_us / performance_data_.total_operations;
        report << "Average execution time: " << avg_time << " us\n";
        report << "Min execution time: " << performance_data_.min_time_us << " us\n";
        report << "Max execution time: " << performance_data_.max_time_us << " us\n";
        report << "Memory operations: " << performance_data_.memory_operations << "\n";
        report << "I/O operations: " << performance_data_.io_operations << "\n";
    }

    auto bottlenecks = analyzeBottlenecks();
    if (!bottlenecks.empty()) {
        report << "\nBottlenecks detected:\n";
        for (const auto& bottleneck : bottlenecks) {
            report << "- " << bottleneck.bottleneck_location << " (" << bottleneck.bottleneck_type
                   << "): severity " << bottleneck.severity << "/10\n";
            report << "  Recommendation: " << bottleneck.recommendation << "\n";
        }
    }

    auto recommendations = getOptimizationRecommendations();
    if (!recommendations.empty()) {
        report << "\nOptimization recommendations:\n";
        for (const auto& rec : recommendations) {
            report << "- " << rec << "\n";
        }
    }

    return report.str();
}

void PerformanceProfiler::updateMovingAverage(uint32_t value) {
    execution_times_[execution_time_index_] = value;
    execution_time_index_ = (execution_time_index_ + 1) % MOVING_AVERAGE_SIZE;
}

PerformanceProfiler::BottleneckAnalysis PerformanceProfiler::detectCpuBottleneck() const {
    BottleneckAnalysis analysis{"", "cpu", 0, "", 0};

    if (performance_data_.total_operations < 10) return analysis;

    uint32_t avg_time = performance_data_.total_time_us / performance_data_.total_operations;

    // High CPU usage detection (simple heuristic)
    if (avg_time > 50000) {  // 50ms average
        analysis.bottleneck_location = "Main processing loop";
        analysis.severity = 8;
        analysis.recommendation = "Optimize main processing loop - consider FFT optimization or reduced sample rate";
        analysis.estimated_improvement = 40;
    } else if (avg_time > 25000) {  // 25ms average
        analysis.bottleneck_location = "Audio processing";
        analysis.severity = 6;
        analysis.recommendation = "Review audio processing pipeline for optimization opportunities";
        analysis.estimated_improvement = 25;
    }

    return analysis;
}

PerformanceProfiler::BottleneckAnalysis PerformanceProfiler::detectMemoryBottleneck() const {
    BottleneckAnalysis analysis{"", "memory", 0, "", 0};

    if (performance_data_.memory_operations > performance_data_.total_operations / 2) {
        analysis.bottleneck_location = "Memory management";
        analysis.severity = 7;
        analysis.recommendation = "Reduce dynamic memory allocations - use static buffers where possible";
        analysis.estimated_improvement = 30;
    }

    return analysis;
}

PerformanceProfiler::BottleneckAnalysis PerformanceProfiler::detectIoBottleneck() const {
    BottleneckAnalysis analysis{"", "io", 0, "", 0};

    if (performance_data_.io_operations > performance_data_.total_operations / 4) {
        analysis.bottleneck_location = "I/O operations";
        analysis.severity = 5;
        analysis.recommendation = "Batch I/O operations and consider asynchronous processing";
        analysis.estimated_improvement = 20;
    }

    return analysis;
}

float PerformanceProfiler::calculateCpuUtilization() const {
    // Simplified CPU utilization calculation
    // In a real implementation, this would use ESP32-specific APIs
    if (performance_data_.total_operations == 0) return 0.0f;

    uint32_t avg_time = performance_data_.total_time_us / performance_data_.total_operations;

    // Assume 1000us = 100% CPU for this core (very simplified)
    float utilization = (static_cast<float>(avg_time) / 1000.0f) * 100.0f;
    return std::min(utilization, 100.0f);
}

} // namespace bpm
} // namespace sparetools