#pragma once

#include <cstdint>
#include <cstdlib>
#include <memory>
#include <vector>
#include <array>
#include "../config.h"

#ifdef PLATFORM_ESP32
#include <esp_heap_caps.h>
#endif

namespace sparetools {
namespace bpm {

/**
 * @brief Memory safety utilities for embedded systems
 *
 * Provides RAII wrappers and safe memory management practices
 * to prevent memory leaks and corruption in resource-constrained environments.
 */
class MemorySafety {
public:
    /**
     * @brief RAII wrapper for aligned memory allocation
     *
     * Ensures proper alignment for cache performance and DMA operations.
     */
    template<typename T>
    class AlignedBuffer {
    public:
        explicit AlignedBuffer(size_t count, size_t alignment = MEMORY_ALIGNMENT)
            : data_(nullptr), count_(count), alignment_(alignment) {
            allocate();
        }

        ~AlignedBuffer() {
            deallocate();
        }

        // Disable copy operations
        AlignedBuffer(const AlignedBuffer&) = delete;
        AlignedBuffer& operator=(const AlignedBuffer&) = delete;

        // Enable move operations
        AlignedBuffer(AlignedBuffer&& other) noexcept
            : data_(other.data_), count_(other.count_), alignment_(other.alignment_) {
            other.data_ = nullptr;
            other.count_ = 0;
        }

        AlignedBuffer& operator=(AlignedBuffer&& other) noexcept {
            if (this != &other) {
                deallocate();
                data_ = other.data_;
                count_ = other.count_;
                alignment_ = other.alignment_;
                other.data_ = nullptr;
                other.count_ = 0;
            }
            return *this;
        }

        T* data() { return data_; }
        const T* data() const { return data_; }
        size_t size() const { return count_; }
        bool valid() const { return data_ != nullptr; }

    private:
        void allocate() {
            if (count_ == 0) return;

#ifdef PLATFORM_ESP32
            // Use ESP32 aligned allocation for better cache performance
            data_ = static_cast<T*>(heap_caps_aligned_alloc(alignment_,
                count_ * sizeof(T), MALLOC_CAP_DEFAULT));
#else
            // Standard aligned allocation for other platforms
            data_ = static_cast<T*>(aligned_alloc(alignment_, count_ * sizeof(T)));
#endif

            if (!data_) {
                // Allocation failed - this is critical in embedded systems
                // In a real system, this would trigger fail-safe mode
                count_ = 0;
            }
        }

        void deallocate() {
            if (data_) {
                free(data_);
                data_ = nullptr;
            }
            count_ = 0;
        }

        T* data_;
        size_t count_;
        size_t alignment_;
    };

    /**
     * @brief Safe vector with bounds checking for embedded systems
     */
    template<typename T>
    class SafeVector {
    public:
        explicit SafeVector(size_t capacity = 0) : data_(capacity), size_(0) {}

        bool push_back(const T& value) {
            if (size_ >= data_.size()) {
                return false; // Capacity exceeded
            }
            data_[size_++] = value;
            return true;
        }

        bool push_back(T&& value) {
            if (size_ >= data_.size()) {
                return false; // Capacity exceeded
            }
            data_[size_++] = std::move(value);
            return true;
        }

        T* at(size_t index) {
            return (index < size_) ? &data_[index] : nullptr;
        }

        const T* at(size_t index) const {
            return (index < size_) ? &data_[index] : nullptr;
        }

        void clear() { size_ = 0; }
        size_t size() const { return size_; }
        size_t capacity() const { return data_.size(); }
        bool empty() const { return size_ == 0; }
        bool full() const { return size_ >= data_.size(); }

        T* data() { return data_.data(); }
        const T* data() const { return data_.data(); }

    private:
        std::vector<T> data_;
        size_t size_;
    };

    /**
     * @brief Memory usage monitor for embedded systems
     */
    class MemoryMonitor {
    public:
        static uint32_t getFreeHeap();
        static uint32_t getTotalHeap();
        static uint32_t getPeakUsage();
        static float getFragmentationRatio();
        static bool isLowMemory();

        // Memory pressure thresholds
        static constexpr uint32_t LOW_MEMORY_THRESHOLD = 8192;  // 8KB
        static constexpr uint32_t CRITICAL_MEMORY_THRESHOLD = 4096;  // 4KB

    private:
        static uint32_t peak_usage_;
    };

    /**
     * @brief Stack overflow protection for FreeRTOS tasks
     */
    class StackGuard {
    public:
        static bool checkStackHighWaterMark();
        static uint32_t getStackHighWaterMark();
        static bool isStackOverflowRisk();

        static constexpr uint32_t MIN_STACK_MARGIN = 512;  // 512 bytes minimum free stack
    };
};

/**
 * @brief RAII wrapper for heap allocation with automatic cleanup
 */
template<typename T>
class HeapObject {
public:
    explicit HeapObject() : ptr_(nullptr) {}

    ~HeapObject() {
        reset();
    }

    // Disable copy
    HeapObject(const HeapObject&) = delete;
    HeapObject& operator=(const HeapObject&) = delete;

    // Enable move
    HeapObject(HeapObject&& other) noexcept : ptr_(other.ptr_) {
        other.ptr_ = nullptr;
    }

    HeapObject& operator=(HeapObject&& other) noexcept {
        if (this != &other) {
            reset();
            ptr_ = other.ptr_;
            other.ptr_ = nullptr;
        }
        return *this;
    }

    T* allocate() {
        reset();
        ptr_ = new (std::nothrow) T();
        return ptr_;
    }

    template<typename... Args>
    T* allocate(Args&&... args) {
        reset();
        ptr_ = new (std::nothrow) T(std::forward<Args>(args)...);
        return ptr_;
    }

    void reset() {
        if (ptr_) {
            delete ptr_;
            ptr_ = nullptr;
        }
    }

    T* get() { return ptr_; }
    const T* get() const { return ptr_; }
    T* operator->() { return ptr_; }
    const T* operator->() const { return ptr_; }
    T& operator*() { return *ptr_; }
    const T& operator*() const { return *ptr_; }

    explicit operator bool() const { return ptr_ != nullptr; }

private:
    T* ptr_;
};

} // namespace bpm
} // namespace sparetools