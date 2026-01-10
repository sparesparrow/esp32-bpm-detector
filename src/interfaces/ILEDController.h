#ifndef I_LED_CONTROLLER_H
#define I_LED_CONTROLLER_H

#include <cstdint>

// ============================================================================
// LED Status Enum
// ============================================================================

enum class LedStatus {
    LED_STATUS_BOOTING,        // Rainbow cycle during boot
    LED_STATUS_WIFI_CONNECTING, // Blue pulsing during WiFi connection
    LED_STATUS_WIFI_CONNECTED,  // Solid blue when WiFi connected
    LED_STATUS_CLIENT_CONNECTED, // Green pulsing when client connected
    LED_STATUS_ERROR,          // Red blinking on error
    LED_STATUS_BPM_DETECTING   // Normal operation, ready for BPM flash
};

// ============================================================================
// LED Controller Interface
// ============================================================================

class ILEDController {
public:
    virtual ~ILEDController() = default;

    /**
     * Initialize the LED controller
     * @return true if initialization successful, false otherwise
     */
    virtual bool begin() = 0;

    /**
     * Show system status using LED patterns
     * @param status The current system status
     */
    virtual void showStatus(LedStatus status) = 0;

    /**
     * Flash LEDs to BPM rhythm
     * @param bpm Current BPM value
     * @param confidence Detection confidence (0.0-1.0)
     */
    virtual void showBPMFlash(int bpm, float confidence) = 0;

    /**
     * Set LED strip brightness
     * @param brightness Brightness level (0-255)
     */
    virtual void setBrightness(uint8_t brightness) = 0;

    /**
     * Clear all LEDs (turn off)
     */
    virtual void clear() = 0;

    /**
     * Update LED patterns (call regularly in main loop)
     */
    virtual void update() = 0;
};

#endif // I_LED_CONTROLLER_H