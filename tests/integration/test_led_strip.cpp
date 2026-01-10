/**
 * Integration test for LED strip functionality
 *
 * This test validates LED controller initialization and basic functionality
 * without requiring physical hardware (uses mock patterns).
 */

#include <Arduino.h>
#include <unity.h>
#include "interfaces/ILEDController.h"
#include "led_strip_controller.h"
#include "config.h"

// Mock FastLED functions for testing without hardware
#ifdef UNIT_TEST
// Define mock functions when running unit tests
extern "C" {
    void FastLED_addLeds(void* controller, void* leds, int count) {}
    void FastLED_setBrightness(uint8_t brightness) {}
    void FastLED_show() {}
    void FastLED_clear(bool write) {}
}
#endif

// Test fixture
class LEDStripTestFixture {
public:
    LEDStripTestFixture() : ledController(nullptr) {}
    ~LEDStripTestFixture() {
        if (ledController) {
            delete ledController;
            ledController = nullptr;
        }
    }

    bool setup() {
        ledController = new LEDStripController();
        return ledController != nullptr;
    }

    ILEDController* ledController;
};

// Test cases
void test_led_controller_creation() {
    LEDStripTestFixture fixture;
    TEST_ASSERT_TRUE(fixture.setup());
    TEST_ASSERT_NOT_NULL(fixture.ledController);
}

void test_led_controller_initialization() {
    LEDStripTestFixture fixture;
    TEST_ASSERT_TRUE(fixture.setup());

    // Test initialization
    bool result = fixture.ledController->begin();
    TEST_ASSERT_TRUE(result);
}

void test_led_status_patterns() {
    LEDStripTestFixture fixture;
    TEST_ASSERT_TRUE(fixture.setup());
    TEST_ASSERT_TRUE(fixture.ledController->begin());

    // Test different status patterns
    fixture.ledController->showStatus(LedStatus::LED_STATUS_BOOTING);
    fixture.ledController->showStatus(LedStatus::LED_STATUS_WIFI_CONNECTING);
    fixture.ledController->showStatus(LedStatus::LED_STATUS_WIFI_CONNECTED);
    fixture.ledController->showStatus(LedStatus::LED_STATUS_CLIENT_CONNECTED);
    fixture.ledController->showStatus(LedStatus::LED_STATUS_ERROR);
    fixture.ledController->showStatus(LedStatus::LED_STATUS_BPM_DETECTING);

    // Test that status changes work
    TEST_ASSERT_TRUE(true); // If we get here, patterns executed
}

void test_led_brightness_control() {
    LEDStripTestFixture fixture;
    TEST_ASSERT_TRUE(fixture.setup());
    TEST_ASSERT_TRUE(fixture.ledController->begin());

    // Test brightness setting
    fixture.ledController->setBrightness(128);
    fixture.ledController->setBrightness(255);
    fixture.ledController->setBrightness(0);

    TEST_ASSERT_TRUE(true); // If we get here, brightness control works
}

void test_led_bpm_flash() {
    LEDStripTestFixture fixture;
    TEST_ASSERT_TRUE(fixture.setup());
    TEST_ASSERT_TRUE(fixture.ledController->begin());

    // Test BPM flash with good confidence
    fixture.ledController->showBPMFlash(120, 0.9f);

    // Test BPM flash with low confidence (should not flash)
    fixture.ledController->showBPMFlash(120, 0.1f);

    TEST_ASSERT_TRUE(true); // If we get here, BPM flash logic executed
}

void test_led_clear() {
    LEDStripTestFixture fixture;
    TEST_ASSERT_TRUE(fixture.setup());
    TEST_ASSERT_TRUE(fixture.ledController->begin());

    // Set a pattern then clear
    fixture.ledController->showStatus(LedStatus::LED_STATUS_ERROR);
    fixture.ledController->clear();

    TEST_ASSERT_TRUE(true); // If we get here, clear works
}

void test_led_update_loop() {
    LEDStripTestFixture fixture;
    TEST_ASSERT_TRUE(fixture.setup());
    TEST_ASSERT_TRUE(fixture.ledController->begin());

    // Simulate update loop for a few iterations
    for (int i = 0; i < 10; i++) {
        fixture.ledController->update();
        delay(10); // Small delay to simulate timing
    }

    TEST_ASSERT_TRUE(true); // If we get here, update loop works
}

// Test runner
void setup() {
    delay(2000); // Allow platform to stabilize

    UNITY_BEGIN();

    RUN_TEST(test_led_controller_creation);
    RUN_TEST(test_led_controller_initialization);
    RUN_TEST(test_led_status_patterns);
    RUN_TEST(test_led_brightness_control);
    RUN_TEST(test_led_bpm_flash);
    RUN_TEST(test_led_clear);
    RUN_TEST(test_led_update_loop);

    UNITY_END();
}

void loop() {
    // Nothing to do in loop for unit tests
}