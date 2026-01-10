#ifndef BPM_MONITOR_MANAGER_H
#define BPM_MONITOR_MANAGER_H

#include "bpm_detector.h"
#include "bpm_flatbuffers.h"
#include "audio_input.h"
#include <vector>
#include <memory>
#include <functional>

namespace sparetools {
namespace bpm {

/**
 * BPM Monitor Manager
 * 
 * Manages multiple BPM monitor instances for multi-device support.
 * Generated from ESP32-BPM monitor spawning prompt template.
 */
class BPMMonitorManager {
public:
    /**
     * Monitor instance data structure
     */
    struct MonitorInstance {
        uint32_t id;
        std::unique_ptr<BPMDetector> detector;
        std::unique_ptr<AudioInput> audioInput;
        BPMDetector::BPMData lastData;
        unsigned long lastUpdateTime;
        bool isActive;
        String name;  // Human-readable name
        
        MonitorInstance(uint32_t monitorId, const String& monitorName)
            : id(monitorId), lastUpdateTime(0), isActive(false), name(monitorName) {}
    };

    /**
     * Callback type for monitor updates
     */
    using MonitorUpdateCallback = std::function<void(uint32_t monitorId, const BPMDetector::BPMData& data)>;

    /**
     * Constructor
     */
    BPMMonitorManager();

    /**
     * Destructor
     */
    ~BPMMonitorManager();

    /**
     * Spawn a new monitor instance
     * @param name Human-readable name for the monitor
     * @return Monitor ID if successful, 0 if failed
     */
    uint32_t spawnMonitor(const String& name = "");

    /**
     * Remove a monitor instance
     * @param monitorId ID of monitor to remove
     * @return true if successful
     */
    bool removeMonitor(uint32_t monitorId);

    /**
     * Get monitor instance by ID
     * @param monitorId Monitor ID
     * @return Pointer to monitor instance, or nullptr if not found
     */
    MonitorInstance* getMonitor(uint32_t monitorId);

    /**
     * Update all active monitors (call this in main loop)
     */
    void updateAllMonitors();

    /**
     * Update a specific monitor
     * @param monitorId Monitor ID
     * @return true if update successful
     */
    bool updateMonitor(uint32_t monitorId);

    /**
     * Get BPM data for a specific monitor
     * @param monitorId Monitor ID
     * @return BPM data, or empty data if monitor not found
     */
    BPMDetector::BPMData getMonitorData(uint32_t monitorId);

    /**
     * Get all monitor IDs
     * @return Vector of active monitor IDs
     */
    std::vector<uint32_t> getMonitorIds() const;

    /**
     * Get number of active monitors
     */
    size_t getMonitorCount() const;

    /**
     * Set update callback for monitor data
     */
    void setUpdateCallback(MonitorUpdateCallback callback);

    /**
     * Enable/disable a monitor
     */
    bool setMonitorActive(uint32_t monitorId, bool active);

    /**
     * Check if monitor is active
     */
    bool isMonitorActive(uint32_t monitorId) const;

    /**
     * Get monitor name
     */
    String getMonitorName(uint32_t monitorId) const;

    /**
     * Set monitor name
     */
    bool setMonitorName(uint32_t monitorId, const String& name);

private:
    std::vector<std::unique_ptr<MonitorInstance>> monitors_;
    uint32_t nextMonitorId_;
    MonitorUpdateCallback updateCallback_;

    /**
     * Find monitor by ID (internal helper)
     */
    MonitorInstance* findMonitor(uint32_t monitorId);

    /**
     * Generate default monitor name
     */
    String generateMonitorName(uint32_t id) const;
};

} // namespace bpm
} // namespace sparetools

#endif // BPM_MONITOR_MANAGER_H
