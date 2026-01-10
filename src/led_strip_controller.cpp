#include "led_strip_controller.h"
#include <Arduino.h>
#include <cmath>

// ============================================================================
// LED Strip Controller Implementation
// ============================================================================

LEDStripController::LEDStripController()
    : currentStatus_(LedStatus::LED_STATUS_BOOTING)
    , currentBrightness_(LED_STRIP_BRIGHTNESS)
    , lastUpdateTime_(0)
    , patternStartTime_(0)
    , currentBpm_(0)
    , currentConfidence_(0.0f)
    , bpmFlashActive_(false)
    , lastBpmFlashTime_(0)
    , rainbowHue_(0)
    , blinkState_(false) {
}

LEDStripController::~LEDStripController() {
    // FastLED cleanup is handled automatically
}

bool LEDStripController::begin() {
    // Initialize FastLED with the configured parameters
    FastLED.addLeds<LED_STRIP_TYPE, LED_STRIP_DATA_PIN, GRB>(leds_, LED_STRIP_NUM_LEDS);
    FastLED.setBrightness(currentBrightness_);
    FastLED.clear(true);

    patternStartTime_ = millis();
    lastUpdateTime_ = millis();

    return true;
}

void LEDStripController::showStatus(LedStatus status) {
    if (currentStatus_ != status) {
        currentStatus_ = status;
        patternStartTime_ = millis();
        blinkState_ = false;
        bpmFlashActive_ = false; // Clear BPM flash when status changes
    }
}

void LEDStripController::showBPMFlash(int bpm, float confidence) {
    currentBpm_ = bpm;
    currentConfidence_ = confidence;

    // Only flash if confidence is above threshold
    if (confidence >= CONFIDENCE_THRESHOLD) {
        bpmFlashActive_ = true;
    } else {
        bpmFlashActive_ = false;
    }
}

void LEDStripController::setBrightness(uint8_t brightness) {
    currentBrightness_ = brightness;
    FastLED.setBrightness(brightness);
    FastLED.show();
}

void LEDStripController::clear() {
    FastLED.clear(true);
    bpmFlashActive_ = false;
}

void LEDStripController::update() {
    unsigned long currentTime = millis();

    // Only update if enough time has passed
    if (currentTime - lastUpdateTime_ < LED_STRIP_UPDATE_INTERVAL) {
        return;
    }

    lastUpdateTime_ = currentTime;

    // Handle BPM flash if active (takes priority)
    if (bpmFlashActive_ && currentBpm_ > 0) {
        updateBPMFlashPattern();
    } else {
        // Handle status patterns
        switch (currentStatus_) {
            case LedStatus::LED_STATUS_BOOTING:
                updateBootingPattern();
                break;
            case LedStatus::LED_STATUS_WIFI_CONNECTING:
                updateWiFiConnectingPattern();
                break;
            case LedStatus::LED_STATUS_WIFI_CONNECTED:
                updateWiFiConnectedPattern();
                break;
            case LedStatus::LED_STATUS_CLIENT_CONNECTED:
                updateClientConnectedPattern();
                break;
            case LedStatus::LED_STATUS_ERROR:
                updateErrorPattern();
                break;
            case LedStatus::LED_STATUS_BPM_DETECTING:
                // For BPM detecting, show a subtle pattern or just clear
                clear();
                break;
        }
    }

    FastLED.show();
}

void LEDStripController::updateBootingPattern() {
    // Rainbow cycle through all LEDs
    unsigned long timeSinceStart = millis() - patternStartTime_;
    rainbowHue_ = (timeSinceStart / 10) % 255; // Slow rainbow cycle

    for (int i = 0; i < LED_STRIP_NUM_LEDS; i++) {
        leds_[i] = CHSV(rainbowHue_ + (i * 255 / LED_STRIP_NUM_LEDS), 255, scaleBrightness(255));
    }
}

void LEDStripController::updateWiFiConnectingPattern() {
    // Blue pulsing on first LED
    unsigned long timeSinceStart = millis() - patternStartTime_;
    uint8_t brightness = (sin(timeSinceStart * 0.01) + 1) * 127; // Pulse between 0-255

    // Clear all LEDs first
    FastLED.clear(false);

    // Blue pulsing on first LED
    leds_[0] = CRGB(0, 0, scaleBrightness(brightness));
}

void LEDStripController::updateWiFiConnectedPattern() {
    // Solid blue on first LED
    FastLED.clear(false);
    leds_[0] = CRGB(0, 0, scaleBrightness(255));
}

void LEDStripController::updateClientConnectedPattern() {
    // Green pulsing on second LED
    unsigned long timeSinceStart = millis() - patternStartTime_;
    uint8_t brightness = (sin(timeSinceStart * 0.01) + 1) * 127; // Pulse between 0-255

    // Clear all LEDs first
    FastLED.clear(false);

    // Green pulsing on second LED
    leds_[1] = CRGB(0, scaleBrightness(brightness), 0);
}

void LEDStripController::updateErrorPattern() {
    // Red blinking on all LEDs
    unsigned long timeSinceStart = millis() - patternStartTime_;
    bool shouldBlink = (timeSinceStart / LED_ERROR_BLINK_INTERVAL) % 2 == 0;

    if (shouldBlink) {
        for (int i = 0; i < LED_STRIP_NUM_LEDS; i++) {
            leds_[i] = CRGB(scaleBrightness(255), 0, 0); // Red
        }
    } else {
        FastLED.clear(false);
    }
}

void LEDStripController::updateBPMFlashPattern() {
    if (currentBpm_ <= 0 || currentConfidence_ < CONFIDENCE_THRESHOLD) {
        bpmFlashActive_ = false;
        return;
    }

    // Calculate BPM interval in milliseconds
    unsigned long bpmInterval = 60000UL / currentBpm_; // 60 seconds * 1000ms / BPM
    unsigned long timeSinceLastFlash = millis() - lastBpmFlashTime_;

    // Flash white when it's time for the beat
    if (timeSinceLastFlash >= bpmInterval) {
        // Quick white flash
        for (int i = 0; i < LED_STRIP_NUM_LEDS; i++) {
            leds_[i] = CRGB(scaleBrightness(255), scaleBrightness(255), scaleBrightness(255));
        }
        lastBpmFlashTime_ = millis();
    } else if (timeSinceLastFlash < 100) { // Flash duration: 100ms
        // Keep white during flash
        for (int i = 0; i < LED_STRIP_NUM_LEDS; i++) {
            leds_[i] = CRGB(scaleBrightness(255), scaleBrightness(255), scaleBrightness(255));
        }
    } else {
        // Clear LEDs between flashes
        FastLED.clear(false);
    }
}

uint8_t LEDStripController::scaleBrightness(uint8_t value) const {
    // Scale the value by the current brightness setting
    return (value * currentBrightness_) / 255;
}