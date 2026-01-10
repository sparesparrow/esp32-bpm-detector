#pragma once

#include <cstdint>
#include <functional>
#include "interfaces/ITimer.h"

#ifdef PLATFORM_ESP32
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#endif

namespace sparetools {
namespace bpm {

/**
 * @brief FreeRTOS task management utilities for embedded systems
 *
 * Provides safer task creation, monitoring, and synchronization
 * with automatic cleanup and error handling.
 */
class FreeRTOSTaskManager {
public:
    /**
     * @brief Task creation result
     */
    enum class TaskResult {
        SUCCESS = 0,
        ERROR_INVALID_PARAMETERS = -1,
        ERROR_INSUFFICIENT_MEMORY = -2,
        ERROR_TASK_CREATION_FAILED = -3,
        ERROR_NOT_SUPPORTED = -4
    };

    /**
     * @brief Task priority levels (embedded-safe)
     */
    enum class TaskPriority {
        PRIORITY_LOW = 1,      // Background tasks
        PRIORITY_NORMAL = 2,   // Normal priority tasks
        PRIORITY_HIGH = 3,     // High priority tasks (audio sampling)
        PRIORITY_CRITICAL = 4  // Critical system tasks
    };

    /**
     * @brief Task configuration
     */
    struct TaskConfig {
        const char* name;
        uint32_t stack_size;
        TaskPriority priority;
        uint8_t core_affinity;  // 0x01 = core 0, 0x02 = core 1, 0x03 = both
        uint32_t watchdog_timeout_ms;
    };

    /**
     * @brief Task handle wrapper with automatic cleanup
     */
    class TaskHandle {
    public:
        explicit TaskHandle(TaskHandle_t handle = nullptr);
        ~TaskHandle();

        // Disable copy
        TaskHandle(const TaskHandle&) = delete;
        TaskHandle& operator=(const TaskHandle&) = delete;

        // Enable move
        TaskHandle(TaskHandle&& other) noexcept;
        TaskHandle& operator=(TaskHandle&& other) noexcept;

        /**
         * @brief Check if task is valid
         */
        bool isValid() const;

        /**
         * @brief Get underlying FreeRTOS handle
         */
        TaskHandle_t get() const;

        /**
         * @brief Delete the task
         */
        void deleteTask();

        /**
         * @brief Get task name
         */
        const char* getName() const;

        /**
         * @brief Get stack high water mark
         */
        uint32_t getStackHighWaterMark() const;

    private:
        TaskHandle_t handle_;
    };

    /**
     * @brief Create a new FreeRTOS task with safety features
     * @param config Task configuration
     * @param task_function Task function to execute
     * @param parameter Parameter to pass to task function
     * @return TaskHandle on success, invalid handle on failure
     */
    static TaskHandle createTask(const TaskConfig& config,
                                void (*task_function)(void*),
                                void* parameter = nullptr);

    /**
     * @brief Create a task with C++ lambda/function object
     * @param config Task configuration
     * @param task_function Function to execute (will be copied)
     * @return TaskHandle on success, invalid handle on failure
     */
    static TaskHandle createTask(const TaskConfig& config,
                                std::function<void()> task_function);

    /**
     * @brief Get system task statistics
     */
    struct TaskStats {
        uint32_t total_tasks;
        uint32_t running_tasks;
        uint32_t suspended_tasks;
        uint32_t ready_tasks;
        uint32_t blocked_tasks;
        uint32_t total_runtime;
        uint32_t idle_time;
    };

    static TaskStats getTaskStats();

    /**
     * @brief Monitor task health
     */
    static bool isTaskHealthy(TaskHandle_t task);

    /**
     * @brief Get recommended stack size for common tasks
     */
    static uint32_t getRecommendedStackSize(const char* task_type);

    /**
     * @brief Default task configurations for common use cases
     */
    static const TaskConfig AUDIO_SAMPLING_TASK_CONFIG;
    static const TaskConfig NETWORK_TASK_CONFIG;
    static const TaskConfig MONITORING_TASK_CONFIG;
    static const TaskConfig BACKGROUND_TASK_CONFIG;

private:
    /**
     * @brief Internal task wrapper for C++ functions
     */
    struct TaskWrapper {
        std::function<void()> function;
        static void taskFunction(void* parameter);
    };

    /**
     * @brief Convert priority enum to FreeRTOS priority
     */
    static UBaseType_t priorityToFreeRTOS(TaskPriority priority);
};

/**
 * @brief RAII task monitor for critical sections
 */
class TaskMonitor {
public:
    explicit TaskMonitor(const char* task_name, uint32_t timeout_ms = 30000);
    ~TaskMonitor();

    /**
     * @brief Report task activity (resets timeout)
     */
    void reportActivity();

    /**
     * @brief Check if task is still responsive
     */
    bool isResponsive() const;

private:
    const char* task_name_;
    uint32_t timeout_ms_;
    uint32_t last_activity_;
    ITimer* timer_;
};

} // namespace bpm
} // namespace sparetools