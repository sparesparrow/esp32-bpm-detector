#include "bpm_monitor_manager.h"
#include <algorithm>

namespace BpmMonitor {

// BpmDataProvider implementation
BpmDataProvider::BpmDataProvider(BPMDetector& detector)
    : detector_(detector) {
}

BpmMonitorData BpmDataProvider::getCurrentData() {
    BpmMonitorData data;

    // Get current BPM data from detector by calling detect()
    if (detector_.isBufferReady()) {
        auto bpmData = detector_.detect();

        data.bpm = bpmData.bpm;
        data.confidence = bpmData.confidence;
        data.signal_level = bpmData.signal_level;
        data.status = static_cast<int8_t>(0); // Default status
        data.timestamp = bpmData.timestamp;
    }

    return data;
}

bool BpmDataProvider::isDataAvailable() const {
    return detector_.isBufferReady();
}

// BpmMonitor implementation
BpmMonitor::BpmMonitor(uint32_t id, const std::vector<MonitorParameter>& parameters,
                       IBpmDataProvider& dataProvider)
    : id_(id), parameters_(parameters), data_provider_(dataProvider), active_(true) {
}

uint32_t BpmMonitor::getId() const {
    return id_;
}

std::vector<BpmMonitorData> BpmMonitor::getCurrentValues() {
    if (!active_ || !data_provider_.isDataAvailable()) {
        return {};
    }

    BpmMonitorData currentData = data_provider_.getCurrentData();
    std::vector<BpmMonitorData> result;

    // Filter data based on requested parameters
    for (auto param : parameters_) {
        if (param == MonitorParameter::ALL) {
            result.push_back(currentData);
            break; // ALL includes everything
        }
    }

    if (parameters_.empty() ||
        std::find(parameters_.begin(), parameters_.end(), MonitorParameter::ALL) != parameters_.end()) {
        result.push_back(currentData);
    } else {
        // Create filtered data based on parameters
        BpmMonitorData filteredData;
        filteredData.timestamp = currentData.timestamp;

        for (auto param : parameters_) {
            switch (param) {
                case MonitorParameter::BPM_VALUE:
                    filteredData.bpm = currentData.bpm;
                    break;
                case MonitorParameter::CONFIDENCE:
                    filteredData.confidence = currentData.confidence;
                    break;
                case MonitorParameter::SIGNAL_LEVEL:
                    filteredData.signal_level = currentData.signal_level;
                    break;
                case MonitorParameter::DETECTION_STATUS:
                    filteredData.status = currentData.status;
                    break;
                case MonitorParameter::ALL:
                    // Already handled above
                    break;
            }
        }
        result.push_back(filteredData);
    }

    return result;
}

bool BpmMonitor::isActive() const {
    return active_;
}

void BpmMonitor::stop() {
    active_ = false;
}

// BpmMonitorManager implementation
BpmMonitorManager::BpmMonitorManager(BPMDetector& detector)
    : data_provider_(new BpmDataProvider(detector)),
      next_monitor_id_(1) {
}

uint32_t BpmMonitorManager::startMonitor(const std::vector<MonitorParameter>& parameters) {
    std::lock_guard<std::mutex> lock(mutex_);

    if (parameters.empty()) {
        return 0; // Invalid request
    }

    uint32_t monitorId = next_monitor_id_++;
    monitors_[monitorId] = std::unique_ptr<BpmMonitor>(new BpmMonitor(monitorId, parameters, *data_provider_));

    return monitorId;
}

std::vector<BpmMonitorData> BpmMonitorManager::getMonitorValues(uint32_t monitorId) {
    std::lock_guard<std::mutex> lock(mutex_);

    auto it = monitors_.find(monitorId);
    if (it == monitors_.end()) {
        return {}; // Monitor not found
    }

    return it->second->getCurrentValues();
}

bool BpmMonitorManager::stopMonitor(uint32_t monitorId) {
    std::lock_guard<std::mutex> lock(mutex_);

    auto it = monitors_.find(monitorId);
    if (it == monitors_.end()) {
        return false; // Monitor not found
    }

    it->second->stop();
    monitors_.erase(it);
    return true;
}

size_t BpmMonitorManager::stopAllMonitors() {
    std::lock_guard<std::mutex> lock(mutex_);

    size_t count = monitors_.size();
    for (auto& pair : monitors_) {
        pair.second->stop();
    }
    monitors_.clear();

    return count;
}

size_t BpmMonitorManager::getActiveMonitorCount() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return monitors_.size();
}

} // namespace BpmMonitor
