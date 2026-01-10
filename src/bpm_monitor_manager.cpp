#include "bpm_monitor_manager.h"
#include "audio_input.h"
#include "config.h"
#include <Arduino.h>

namespace sparetools {
namespace bpm {

BPMMonitorManager::BPMMonitorManager()
    : nextMonitorId_(1) {
}

BPMMonitorManager::~BPMMonitorManager() {
    monitors_.clear();
}

uint32_t BPMMonitorManager::spawnMonitor(const String& name) {
    // Generate monitor ID
    uint32_t monitorId = nextMonitorId_++;
    
    // Generate name if not provided
    String monitorName = name.length() > 0 ? name : generateMonitorName(monitorId);
    
    // Create monitor instance
    auto monitor = std::unique_ptr<MonitorInstance>(new MonitorInstance(monitorId, monitorName));
    
    // Create audio input for this monitor
    monitor->audioInput = std::unique_ptr<AudioInput>(new AudioInput());
    if (monitor->audioInput) {
        monitor->audioInput->begin(MICROPHONE_PIN);
    }

    // Create BPM detector for this monitor
    // BPMDetector constructor: BPMDetector(uint16_t sample_rate, uint16_t fft_size)
    monitor->detector = std::unique_ptr<BPMDetector>(new BPMDetector(SAMPLE_RATE, FFT_SIZE));

    // Initialize detector with audio input (begin() returns void, so no boolean check)
    if (monitor->detector) {
        monitor->detector->begin(MICROPHONE_PIN);
    }
    
    // Set as active
    monitor->isActive = true;
    monitor->lastUpdateTime = millis();
    
    // Initialize last data
    BPMDetector::BPMData initData;
    initData.bpm = 0.0f;
    initData.confidence = 0.0f;
    initData.signal_level = 0.0f;
    initData.quality = 0.0f;
    initData.status = "initializing";
    initData.timestamp = 0;
    monitor->lastData = initData;
    
    // Add to monitors list
    monitors_.push_back(std::move(monitor));
    
    DEBUG_PRINTLN("[MonitorManager] Spawned monitor " + String(monitorId) + " (" + monitorName + ")");
    
    return monitorId;
}

bool BPMMonitorManager::removeMonitor(uint32_t monitorId) {
    auto it = monitors_.begin();
    while (it != monitors_.end()) {
        if ((*it)->id == monitorId) {
            DEBUG_PRINTLN("[MonitorManager] Removing monitor " + String(monitorId));
            monitors_.erase(it);
            return true;
        }
        ++it;
    }
    
    DEBUG_PRINTLN("[MonitorManager] Monitor " + String(monitorId) + " not found");
    return false;
}

BPMMonitorManager::MonitorInstance* BPMMonitorManager::getMonitor(uint32_t monitorId) {
    return findMonitor(monitorId);
}

void BPMMonitorManager::updateAllMonitors() {
    unsigned long currentTime = millis();
    
    for (auto& monitor : monitors_) {
        if (monitor->isActive) {
            // Update monitor
            auto data = monitor->detector->detect();
            monitor->lastData = data;
            monitor->lastUpdateTime = currentTime;
            
            // Call callback if set
            if (updateCallback_) {
                updateCallback_(monitor->id, data);
            }
        }
    }
}

bool BPMMonitorManager::updateMonitor(uint32_t monitorId) {
    auto* monitor = findMonitor(monitorId);
    if (!monitor || !monitor->isActive) {
        return false;
    }
    
    unsigned long currentTime = millis();
    auto data = monitor->detector->detect();
    monitor->lastData = data;
    monitor->lastUpdateTime = currentTime;
    
    // Call callback if set
    if (updateCallback_) {
        updateCallback_(monitor->id, data);
    }
    
    return true;
}

BPMDetector::BPMData BPMMonitorManager::getMonitorData(uint32_t monitorId) {
    auto* monitor = findMonitor(monitorId);
    if (monitor) {
        return monitor->lastData;
    }
    
    // Return empty data
    BPMDetector::BPMData emptyData;
    emptyData.bpm = 0.0f;
    emptyData.confidence = 0.0f;
    emptyData.signal_level = 0.0f;
    emptyData.quality = 0.0f;
    emptyData.status = String("not_found");
    emptyData.timestamp = 0;
    return emptyData;
}

std::vector<uint32_t> BPMMonitorManager::getMonitorIds() const {
    std::vector<uint32_t> ids;
    for (const auto& monitor : monitors_) {
        ids.push_back(monitor->id);
    }
    return ids;
}

size_t BPMMonitorManager::getMonitorCount() const {
    return monitors_.size();
}

void BPMMonitorManager::setUpdateCallback(MonitorUpdateCallback callback) {
    updateCallback_ = callback;
}

bool BPMMonitorManager::setMonitorActive(uint32_t monitorId, bool active) {
    auto* monitor = findMonitor(monitorId);
    if (!monitor) {
        return false;
    }
    
    monitor->isActive = active;
    return true;
}

bool BPMMonitorManager::isMonitorActive(uint32_t monitorId) const {
    for (const auto& monitor : monitors_) {
        if (monitor->id == monitorId) {
            return monitor->isActive;
        }
    }
    return false;
}

String BPMMonitorManager::getMonitorName(uint32_t monitorId) const {
    for (const auto& monitor : monitors_) {
        if (monitor->id == monitorId) {
            return monitor->name;
        }
    }
    return "";
}

bool BPMMonitorManager::setMonitorName(uint32_t monitorId, const String& name) {
    auto* monitor = findMonitor(monitorId);
    if (!monitor) {
        return false;
    }
    
    monitor->name = name;
    return true;
}

BPMMonitorManager::MonitorInstance* BPMMonitorManager::findMonitor(uint32_t monitorId) {
    for (auto& monitor : monitors_) {
        if (monitor->id == monitorId) {
            return monitor.get();
        }
    }
    return nullptr;
}

String BPMMonitorManager::generateMonitorName(uint32_t id) const {
    return "Monitor_" + String(id);
}

} // namespace bpm
} // namespace sparetools
