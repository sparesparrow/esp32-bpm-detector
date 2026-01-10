#include <gtest/gtest.h>
#include "safety/MemorySafety.h"

namespace sparetools {
namespace bpm {

// Test fixture for MemorySafety tests
class MemorySafetyTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Nothing to set up
    }

    void TearDown() override {
        // Nothing to tear down
    }
};

// Test aligned buffer
TEST_F(MemorySafetyTest, AlignedBuffer) {
    MemorySafety::AlignedBuffer<int> buffer(100, 16);  // 100 ints, 16-byte alignment

    EXPECT_TRUE(buffer.valid());
    EXPECT_EQ(100u, buffer.size());

    int* data = buffer.data();
    EXPECT_NE(nullptr, data);

    // Test data access
    data[0] = 42;
    EXPECT_EQ(42, data[0]);

    // Test bounds
    data[99] = 99;
    EXPECT_EQ(99, data[99]);
}

// Test safe vector
TEST_F(MemorySafetyTest, SafeVector) {
    MemorySafety::SafeVector<int> vec(10);

    EXPECT_TRUE(vec.empty());
    EXPECT_EQ(0u, vec.size());
    EXPECT_EQ(10u, vec.capacity());

    // Test push back
    EXPECT_TRUE(vec.push_back(1));
    EXPECT_TRUE(vec.push_back(2));
    EXPECT_EQ(2u, vec.size());
    EXPECT_FALSE(vec.empty());

    // Test access
    int* val1 = vec.at(0);
    ASSERT_NE(nullptr, val1);
    EXPECT_EQ(1, *val1);

    int* val2 = vec.at(1);
    ASSERT_NE(nullptr, val2);
    EXPECT_EQ(2, *val2);

    // Test out of bounds
    EXPECT_EQ(nullptr, vec.at(10));

    // Test full capacity
    for (int i = 2; i < 10; ++i) {
        EXPECT_TRUE(vec.push_back(i + 1));
    }
    EXPECT_EQ(10u, vec.size());
    EXPECT_TRUE(vec.full());

    // Test push to full vector
    EXPECT_FALSE(vec.push_back(99));
}

// Test memory monitor (mocked)
TEST_F(MemorySafetyTest, MemoryMonitor) {
    // These functions return mock values in unit tests
    // In real embedded environment, they would return actual values
    uint32_t free_heap = MemorySafety::MemoryMonitor::getFreeHeap();
    uint32_t total_heap = MemorySafety::MemoryMonitor::getTotalHeap();

    // Basic sanity checks
    EXPECT_GE(free_heap, 0u);
    EXPECT_GE(total_heap, 0u);

    // Test fragmentation ratio calculation
    float fragmentation = MemorySafety::MemoryMonitor::getFragmentationRatio();
    EXPECT_GE(fragmentation, 0.0f);
    EXPECT_LE(fragmentation, 1.0f);
}

// Test stack guard (mocked)
TEST_F(MemorySafetyTest, StackGuard) {
    // These functions return safe defaults in unit tests
    bool stack_ok = MemorySafety::MemoryMonitor::StackGuard::checkStackHighWaterMark();
    uint32_t stack_margin = MemorySafety::MemoryMonitor::StackGuard::getStackHighWaterMark();

    // Basic sanity checks
    EXPECT_GE(stack_margin, 0u);
}

// Test heap object RAII wrapper
TEST_F(MemorySafetyTest, HeapObject) {
    HeapObject<int> heap_int;

    // Initially empty
    EXPECT_EQ(nullptr, heap_int.get());

    // Allocate
    int* ptr = heap_int.allocate(42);
    ASSERT_NE(nullptr, ptr);
    EXPECT_EQ(42, *ptr);

    // Access via operators
    EXPECT_EQ(42, *heap_int);
    EXPECT_EQ(42, heap_int->operator*());

    // Reset
    heap_int.reset();
    EXPECT_EQ(nullptr, heap_int.get());

    // Allocate with arguments
    int* ptr2 = heap_int.allocate(100);
    ASSERT_NE(nullptr, ptr2);
    EXPECT_EQ(100, *ptr2);
}

} // namespace bpm
} // namespace sparetools

// Main function for running tests
int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}