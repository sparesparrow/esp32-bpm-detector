#ifndef LED_STRIP_CONTROLLER_H
#define LED_STRIP_CONTROLLER_H

#include "interfaces/ILEDController.h"
#include "config.h"
#include <FastLED.h>

// ============================================================================
// LED Strip Controller Implementation
// ============================================================================

class LEDStripController : public ILEDController {
public:
    LEDStripController();
    virtual ~LEDStripController();

    /**
     * Initialize the LED controller
     * @return true if initialization successful, false otherwise
     */
    bool begin() override;

    /**
     * Show system status using LED patterns
     * @param status The current system status
     */
    void showStatus(LedStatus status) override;

    /**
     * Flash LEDs to BPM rhythm
     * @param bpm Current BPM value
     * @param confidence Detection confidence (0.0-1.0)
     */
    void showBPMFlash(int bpm, float confidence) override;

    /**
     * Set LED strip brightness
     * @param brightness Brightness level (0-255)
     */
    void setBrightness(uint8_t brightness) override;

    /**
     * Clear all LEDs (turn off)
     */
    void clear() override;

    /**
     * Update LED patterns (call regularly in main loop)
     */
    void update() override;

private:
    // LED strip data
    CRGB leds_[LED_STRIP_NUM_LEDS];

    // Current state
    LedStatus currentStatus_;
    uint8_t currentBrightness_;
    unsigned long lastUpdateTime_;
    unsigned long patternStartTime_;

    // BPM flash state
    int currentBpm_;
    float currentConfidence_;
    bool bpmFlashActive_;
    unsigned long lastBpmFlashTime_;

    // Pattern animation state
    uint8_t rainbowHue_;
    bool blinkState_;

    // Private helper methods
    void updateBootingPattern();
    void updateWiFiConnectingPattern();
    void updateWiFiConnectedPattern();
    void updateClientConnectedPattern();
    void updateErrorPattern();
    void updateBPMFlashPattern();
    void applyBrightness();
    uint8_t scaleBrightness(uint8_t value) const;
};

#endif // LED_STRIP_CONTROLLER_H