#include "FreeRTOSTaskManager.h"
#include <cstring>

#ifdef PLATFORM_ESP32
#include <freertos/task.h>
#include <esp_task_wdt.h>
#endif

namespace sparetools {
namespace bpm {

// Default task configurations
const FreeRTOSTaskManager::TaskConfig FreeRTOSTaskManager::AUDIO_SAMPLING_TASK_CONFIG = {
    "AudioSampling",
    4096,  // 4KB stack
    TaskPriority::PRIORITY_HIGH,
    0x01,  // Core 0
    1000   // 1 second watchdog timeout
};

const FreeRTOSTaskManager::TaskConfig FreeRTOSTaskManager::NETWORK_TASK_CONFIG = {
    "NetworkTask",
    8192,  // 8KB stack
    TaskPriority::PRIORITY_NORMAL,
    0x03,  // Both cores
    5000   // 5 second watchdog timeout
};

const FreeRTOSTaskManager::TaskConfig FreeRTOSTaskManager::MONITORING_TASK_CONFIG = {
    "MonitoringTask",
    4096,  // 4KB stack
    TaskPriority::PRIORITY_NORMAL,
    0x02,  // Core 1
    10000  // 10 second watchdog timeout
};

const FreeRTOSTaskManager::TaskConfig FreeRTOSTaskManager::BACKGROUND_TASK_CONFIG = {
    "BackgroundTask",
    3072,  // 3KB stack
    TaskPriority::PRIORITY_LOW,
    0x03,  // Both cores
    30000  // 30 second watchdog timeout
};

// TaskHandle implementation
FreeRTOSTaskManager::TaskHandle::TaskHandle(TaskHandle_t handle)
    : handle_(handle) {
}

FreeRTOSTaskManager::TaskHandle::~TaskHandle() {
    if (handle_) {
        vTaskDelete(handle_);
        handle_ = nullptr;
    }
}

FreeRTOSTaskManager::TaskHandle::TaskHandle(TaskHandle&& other) noexcept
    : handle_(other.handle_) {
    other.handle_ = nullptr;
}

FreeRTOSTaskManager::TaskHandle& FreeRTOSTaskManager::TaskHandle::operator=(TaskHandle&& other) noexcept {
    if (this != &other) {
        if (handle_) {
            vTaskDelete(handle_);
        }
        handle_ = other.handle_;
        other.handle_ = nullptr;
    }
    return *this;
}

bool FreeRTOSTaskManager::TaskHandle::isValid() const {
    return handle_ != nullptr;
}

TaskHandle_t FreeRTOSTaskManager::TaskHandle::get() const {
    return handle_;
}

void FreeRTOSTaskManager::TaskHandle::deleteTask() {
    if (handle_) {
        vTaskDelete(handle_);
        handle_ = nullptr;
    }
}

const char* FreeRTOSTaskManager::TaskHandle::getName() const {
#ifdef PLATFORM_ESP32
    if (handle_) {
        return pcTaskGetName(handle_);
    }
#endif
    return "Unknown";
}

uint32_t FreeRTOSTaskManager::TaskHandle::getStackHighWaterMark() const {
#ifdef PLATFORM_ESP32
    if (handle_) {
        return uxTaskGetStackHighWaterMark(handle_);
    }
#endif
    return 0;
}

// FreeRTOSTaskManager implementation
FreeRTOSTaskManager::TaskHandle FreeRTOSTaskManager::createTask(
    const TaskConfig& config,
    void (*task_function)(void*),
    void* parameter) {

#ifdef PLATFORM_ESP32
    TaskHandle_t handle = nullptr;

    // Convert priority
    UBaseType_t freertos_priority = priorityToFreeRTOS(config.priority);

    // Create task
    BaseType_t result = xTaskCreatePinnedToCore(
        task_function,
        config.name,
        config.stack_size / sizeof(StackType_t),  // FreeRTOS expects stack size in words
        parameter,
        freertos_priority,
        &handle,
        config.core_affinity == 0x01 ? 0 : 1  // Map core affinity to core ID
    );

    if (result == pdPASS && handle) {
        return TaskHandle(handle);
    }
#endif

    // Return invalid handle on failure
    return TaskHandle(nullptr);
}

FreeRTOSTaskManager::TaskHandle FreeRTOSTaskManager::createTask(
    const TaskConfig& config,
    std::function<void()> task_function) {

    // Create wrapper for C++ function
    auto* wrapper = new TaskWrapper{std::move(task_function)};

    auto handle = createTask(config, TaskWrapper::taskFunction, wrapper);

    if (!handle.isValid()) {
        delete wrapper;  // Clean up on failure
    }

    return handle;
}

void FreeRTOSTaskManager::TaskWrapper::taskFunction(void* parameter) {
    auto* wrapper = static_cast<TaskWrapper*>(parameter);
    if (wrapper && wrapper->function) {
        try {
            wrapper->function();
        } catch (...) {
            // Handle exceptions in task
            // In embedded systems, we typically don't want to propagate exceptions
        }
    }
    delete wrapper;  // Clean up wrapper
    vTaskDelete(nullptr);  // Delete this task
}

FreeRTOSTaskManager::TaskStats FreeRTOSTaskManager::getTaskStats() {
    TaskStats stats = {0};

#ifdef PLATFORM_ESP32
    TaskStatus_t* task_status_array;
    UBaseType_t task_count;

    task_count = uxTaskGetNumberOfTasks();
    task_status_array = static_cast<TaskStatus_t*>(pvPortMalloc(task_count * sizeof(TaskStatus_t)));

    if (task_status_array) {
        task_count = uxTaskGetSystemState(task_status_array, task_count, nullptr);

        stats.total_tasks = task_count;

        for (UBaseType_t i = 0; i < task_count; i++) {
            switch (task_status_array[i].eCurrentState) {
                case eRunning:
                    stats.running_tasks++;
                    break;
                case eReady:
                    stats.ready_tasks++;
                    break;
                case eBlocked:
                    stats.blocked_tasks++;
                    break;
                case eSuspended:
                    stats.suspended_tasks++;
                    break;
                default:
                    break;
            }
        }

        vPortFree(task_status_array);
    }
#endif

    return stats;
}

bool FreeRTOSTaskManager::isTaskHealthy(TaskHandle_t task) {
#ifdef PLATFORM_ESP32
    if (!task) return false;

    // Check if task is still valid and has sufficient stack
    UBaseType_t stack_watermark = uxTaskGetStackHighWaterMark(task);
    return stack_watermark > 512;  // At least 512 bytes free stack
#endif

    return false;
}

uint32_t FreeRTOSTaskManager::getRecommendedStackSize(const char* task_type) {
    if (strcmp(task_type, "audio") == 0) {
        return 4096;
    } else if (strcmp(task_type, "network") == 0) {
        return 8192;
    } else if (strcmp(task_type, "monitoring") == 0) {
        return 4096;
    } else if (strcmp(task_type, "background") == 0) {
        return 3072;
    }

    return 4096;  // Default
}

UBaseType_t FreeRTOSTaskManager::priorityToFreeRTOS(TaskPriority priority) {
    switch (priority) {
        case TaskPriority::PRIORITY_LOW: return 1;
        case TaskPriority::PRIORITY_NORMAL: return 2;
        case TaskPriority::PRIORITY_HIGH: return 3;
        case TaskPriority::PRIORITY_CRITICAL: return 4;
        default: return 2;  // Default to normal
    }
}

// TaskMonitor implementation
TaskMonitor::TaskMonitor(const char* task_name, uint32_t timeout_ms)
    : task_name_(task_name), timeout_ms_(timeout_ms), last_activity_(0), timer_(nullptr) {
    // Get timer from platform factory
    // This is a simplified implementation - in real code, timer should be injected
}

TaskMonitor::~TaskMonitor() {
    // Cleanup if needed
}

void TaskMonitor::reportActivity() {
    if (timer_) {
        last_activity_ = timer_->millis();
    }
}

bool TaskMonitor::isResponsive() const {
    if (!timer_) return true;  // Can't monitor without timer

    uint32_t current_time = timer_->millis();
    uint32_t elapsed = current_time - last_activity_;

    return elapsed < timeout_ms_;
}

} // namespace bpm
} // namespace sparetools