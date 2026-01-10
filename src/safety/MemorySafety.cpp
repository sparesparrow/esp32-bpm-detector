#include "MemorySafety.h"
#include "interfaces/IPlatform.h"
#include "platforms/factory/PlatformFactory.h"

#ifdef PLATFORM_ESP32
#include <Arduino.h>
#include <esp_heap_caps.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#endif

namespace sparetools {
namespace bpm {

uint32_t MemorySafety::MemoryMonitor::peak_usage_ = 0;

uint32_t MemorySafety::MemoryMonitor::getFreeHeap() {
#ifdef PLATFORM_ESP32
    return ESP.getFreeHeap();
#else
    // For Arduino/other platforms, return a conservative estimate
    return 1024;  // 1KB conservative estimate
#endif
}

uint32_t MemorySafety::MemoryMonitor::getTotalHeap() {
#ifdef PLATFORM_ESP32
    return ESP.getHeapSize();
#else
    return 2048;  // 2KB conservative estimate
#endif
}

uint32_t MemorySafety::MemoryMonitor::getPeakUsage() {
    uint32_t current_free = getFreeHeap();
    uint32_t total = getTotalHeap();
    uint32_t current_usage = total - current_free;

    if (current_usage > peak_usage_) {
        peak_usage_ = current_usage;
    }

    return peak_usage_;
}

float MemorySafety::MemoryMonitor::getFragmentationRatio() {
#ifdef PLATFORM_ESP32
    // Get heap info for fragmentation analysis
    multi_heap_info_t heap_info;
    heap_caps_get_info(&heap_info, MALLOC_CAP_DEFAULT);

    if (heap_info.total_allocated_bytes > 0) {
        return static_cast<float>(heap_info.total_free_bytes -
                                heap_info.largest_free_block) /
               heap_info.total_free_bytes;
    }
#endif
    return 0.0f;  // No fragmentation data available
}

bool MemorySafety::MemoryMonitor::isLowMemory() {
    return getFreeHeap() < LOW_MEMORY_THRESHOLD;
}

bool MemorySafety::StackGuard::checkStackHighWaterMark() {
#ifdef PLATFORM_ESP32
    UBaseType_t high_water_mark = uxTaskGetStackHighWaterMark(nullptr);
    return high_water_mark >= MIN_STACK_MARGIN;
#else
    // For non-FreeRTOS platforms, assume stack is OK
    return true;
#endif
}

uint32_t MemorySafety::StackGuard::getStackHighWaterMark() {
#ifdef PLATFORM_ESP32
    return uxTaskGetStackHighWaterMark(nullptr);
#else
    return MIN_STACK_MARGIN;  // Conservative estimate
#endif
}

bool MemorySafety::StackGuard::isStackOverflowRisk() {
    return !checkStackHighWaterMark();
}

} // namespace bpm
} // namespace sparetools