#ifndef I_BPM_MONITOR_H
#define I_BPM_MONITOR_H

#include <cstdint>
#include <vector>
#include <memory>

namespace BpmMonitor {

/**
 * @brief BPM monitoring parameter types
 */
enum class MonitorParameter {
    BPM_VALUE,
    CONFIDENCE,
    SIGNAL_LEVEL,
    DETECTION_STATUS,
    ALL
};

/**
 * @brief BPM monitor data structure
 */
struct BpmMonitorData {
    float bpm = 0.0f;
    float confidence = 0.0f;
    float signal_level = 0.0f;
    int8_t status = 0;  // DetectionStatus enum value
    uint64_t timestamp = 0;
};

/**
 * @brief Interface for BPM data providers
 */
class IBpmDataProvider {
public:
    virtual ~IBpmDataProvider() = default;

    /**
     * @brief Get current BPM data
     * @return Current BPM monitor data
     */
    virtual BpmMonitorData getCurrentData() = 0;

    /**
     * @brief Check if BPM data is available
     * @return true if data is available
     */
    virtual bool isDataAvailable() const = 0;
};

/**
 * @brief Interface for BPM monitors
 */
class IBpmMonitor {
public:
    virtual ~IBpmMonitor() = default;

    /**
     * @brief Get monitor ID
     * @return Unique monitor identifier
     */
    virtual uint32_t getId() const = 0;

    /**
     * @brief Get current monitored values
     * @return Vector of current BPM monitor data
     */
    virtual std::vector<BpmMonitorData> getCurrentValues() = 0;

    /**
     * @brief Check if monitor is active
     * @return true if monitor is active
     */
    virtual bool isActive() const = 0;

    /**
     * @brief Stop monitoring
     */
    virtual void stop() = 0;
};

/**
 * @brief Interface for BPM monitor management
 */
class IBpmMonitorManager {
public:
    virtual ~IBpmMonitorManager() = default;

    /**
     * @brief Start a new BPM monitor
     * @param parameters Parameters to monitor
     * @return Monitor ID if successful, 0 if failed
     */
    virtual uint32_t startMonitor(const std::vector<MonitorParameter>& parameters) = 0;

    /**
     * @brief Get current values from a monitor
     * @param monitorId Monitor identifier
     * @return Current monitor data
     */
    virtual std::vector<BpmMonitorData> getMonitorValues(uint32_t monitorId) = 0;

    /**
     * @brief Stop a specific monitor
     * @param monitorId Monitor identifier
     * @return true if monitor was stopped
     */
    virtual bool stopMonitor(uint32_t monitorId) = 0;

    /**
     * @brief Stop all monitors
     * @return Number of monitors stopped
     */
    virtual size_t stopAllMonitors() = 0;

    /**
     * @brief Get number of active monitors
     * @return Number of active monitors
     */
    virtual size_t getActiveMonitorCount() const = 0;
};

} // namespace BpmMonitor

#endif // I_BPM_MONITOR_H
