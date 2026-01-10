#pragma once

#include <cstdint>
#include <string>
#include <vector>
#include <array>
#include "interfaces/ITimer.h"

namespace sparetools {
namespace bpm {

/**
 * @brief Performance profiling and optimization system
 *
 * Provides comprehensive performance monitoring, bottleneck detection,
 * and optimization recommendations for embedded systems.
 */
class PerformanceProfiler {
public:
    /**
     * @brief Performance metrics
     */
    struct Metrics {
        uint32_t execution_time_us;      // Total execution time in microseconds
        uint32_t cpu_cycles;             // CPU cycles used (if available)
        uint32_t memory_used;            // Memory used during operation
        uint32_t peak_memory_usage;      // Peak memory usage
        float cpu_utilization;           // CPU utilization percentage
        uint32_t context_switches;       // Number of context switches
    };

    /**
     * @brief Performance scope for automatic timing
     */
    class ScopeTimer {
    public:
        explicit ScopeTimer(PerformanceProfiler* profiler, const char* scope_name);
        ~ScopeTimer();

        void addCheckpoint(const char* checkpoint_name);

    private:
        PerformanceProfiler* profiler_;
        const char* scope_name_;
        uint32_t start_time_;
        std::vector<std::pair<std::string, uint32_t>> checkpoints_;
    };

    /**
     * @brief Bottleneck analysis result
     */
    struct BottleneckAnalysis {
        std::string bottleneck_location;
        std::string bottleneck_type;     // "cpu", "memory", "io", "contention"
        uint32_t severity;               // 1-10 scale
        std::string recommendation;
        uint32_t estimated_improvement;  // Percentage improvement possible
    };

    /**
     * @brief Initialize performance profiler
     */
    bool initialize(ITimer* timer);

    /**
     * @brief Start performance monitoring
     */
    void startMonitoring(const char* operation_name = nullptr);

    /**
     * @brief Stop performance monitoring and get metrics
     */
    Metrics stopMonitoring();

    /**
     * @brief Record a performance event
     */
    void recordEvent(const char* event_name, uint32_t value = 0);

    /**
     * @brief Get current performance metrics
     */
    Metrics getCurrentMetrics() const;

    /**
     * @brief Analyze performance bottlenecks
     */
    std::vector<BottleneckAnalysis> analyzeBottlenecks();

    /**
     * @brief Get performance recommendations
     */
    std::vector<std::string> getOptimizationRecommendations();

    /**
     * @brief Enable/disable performance monitoring
     */
    void setMonitoringEnabled(bool enabled);

    /**
     * @brief Check if monitoring is enabled
     */
    bool isMonitoringEnabled() const;

    /**
     * @brief Reset performance statistics
     */
    void resetStatistics();

    /**
     * @brief Get performance summary report
     */
    std::string getPerformanceReport();

private:
    ITimer* timer_;
    bool monitoring_enabled_;
    bool currently_monitoring_;
    uint32_t monitoring_start_time_;
    std::string current_operation_;

    // Performance data storage
    struct PerformanceData {
        uint32_t total_operations;
        uint32_t total_time_us;
        uint32_t min_time_us;
        uint32_t max_time_us;
        uint32_t memory_operations;
        uint32_t io_operations;
    };

    PerformanceData performance_data_;

    // Moving averages for trend analysis
    static constexpr size_t MOVING_AVERAGE_SIZE = 10;
    std::array<uint32_t, MOVING_AVERAGE_SIZE> execution_times_;
    size_t execution_time_index_;

    /**
     * @brief Update moving average
     */
    void updateMovingAverage(uint32_t value);

    /**
     * @brief Detect CPU bottlenecks
     */
    BottleneckAnalysis detectCpuBottleneck() const;

    /**
     * @brief Detect memory bottlenecks
     */
    BottleneckAnalysis detectMemoryBottleneck() const;

    /**
     * @brief Detect I/O bottlenecks
     */
    BottleneckAnalysis detectIoBottleneck() const;

    /**
     * @brief Calculate CPU utilization
     */
    float calculateCpuUtilization() const;
};

// Global performance profiler instance
extern PerformanceProfiler* g_performance_profiler;

/**
 * @brief Convenience macro for performance timing
 */
#define PERFORMANCE_SCOPE(name) \
    PerformanceProfiler::ScopeTimer scope_timer(g_performance_profiler, name)

/**
 * @brief Convenience macro for performance events
 */
#define PERFORMANCE_EVENT(name, value) \
    if (g_performance_profiler) g_performance_profiler->recordEvent(name, value)

} // namespace bpm
} // namespace sparetools