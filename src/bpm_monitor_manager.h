#ifndef BPM_MONITOR_MANAGER_H
#define BPM_MONITOR_MANAGER_H

#include "interfaces/IBpmMonitor.h"
#include "bpm_detector.h"
#include <unordered_map>
#include <memory>
#include <vector>
#include <mutex>

namespace BpmMonitor {

/**
 * @brief BPM data provider implementation using BPM detector
 */
class BpmDataProvider : public IBpmDataProvider {
public:
    explicit BpmDataProvider(BPMDetector& detector);
    ~BpmDataProvider() override = default;

    BpmMonitorData getCurrentData() override;
    bool isDataAvailable() const override;

private:
    BPMDetector& detector_;
};

/**
 * @brief BPM monitor implementation
 */
class BpmMonitor : public IBpmMonitor {
public:
    BpmMonitor(uint32_t id, const std::vector<MonitorParameter>& parameters,
               IBpmDataProvider& dataProvider);
    ~BpmMonitor() override = default;

    uint32_t getId() const override;
    std::vector<BpmMonitorData> getCurrentValues() override;
    bool isActive() const override;
    void stop() override;

private:
    uint32_t id_;
    std::vector<MonitorParameter> parameters_;
    IBpmDataProvider& data_provider_;
    bool active_;
};

/**
 * @brief BPM monitor manager implementation
 */
class BpmMonitorManager : public IBpmMonitorManager {
public:
    explicit BpmMonitorManager(BPMDetector& detector);
    ~BpmMonitorManager() override = default;

    uint32_t startMonitor(const std::vector<MonitorParameter>& parameters) override;
    std::vector<BpmMonitorData> getMonitorValues(uint32_t monitorId) override;
    bool stopMonitor(uint32_t monitorId) override;
    size_t stopAllMonitors() override;
    size_t getActiveMonitorCount() const override;

private:
    std::unique_ptr<BpmDataProvider> data_provider_;
    std::unordered_map<uint32_t, std::unique_ptr<BpmMonitor>> monitors_;
    uint32_t next_monitor_id_;
    mutable std::mutex mutex_;
};

} // namespace BpmMonitor

#endif // BPM_MONITOR_MANAGER_H
