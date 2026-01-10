#ifndef MAIN_SETUP_HELPERS_H
#define MAIN_SETUP_HELPERS_H

#include "config.h"
#include "bpm_detector.h"
#include "audio_input.h"
#include "bpm_monitor_manager.h"
#include "interfaces/ITimer.h"
#include "interfaces/ILEDController.h"
#include "led_strip_controller.h"
#include <WebServer.h>
#include <WiFi.h>
#include <memory>

// Forward declarations
class ITimer;
class ILEDController;
class BPMDetector;
class AudioInput;
class WebServer;
namespace sparetools { namespace bpm { class BPMMonitorManager; } }

/**
 * Setup helper functions following OMS C++ patterns
 * Breaks down large setup() function into manageable, testable units
 */
namespace BpmSetupHelpers {

/**
 * Initialize serial communication
 * @return true if successful
 */
bool initializeSerial();

/**
 * Initialize WiFi Access Point
 * @param ssid Access point SSID
 * @param password Access point password
 * @return true if AP started successfully
 */
bool initializeWiFiAP(const char* ssid, const char* password);

/**
 * Initialize LED controller
 * @param ledController Reference to LED controller unique_ptr
 * @return true if initialization successful
 */
bool initializeLEDController(std::unique_ptr<ILEDController>& ledController);

/**
 * Initialize audio input
 * @param audioInput Reference to AudioInput unique_ptr
 * @param micPin Microphone pin number
 * @return true if initialization successful
 */
bool initializeAudioInput(std::unique_ptr<AudioInput>& audioInput, uint8_t micPin);

/**
 * Initialize BPM detector
 * @param bpmDetector Reference to BPMDetector unique_ptr
 * @param micPin Microphone pin number
 * @return true if initialization successful
 */
bool initializeBPMDetector(std::unique_ptr<BPMDetector>& bpmDetector, uint8_t micPin);

/**
 * Initialize monitor manager
 * @param monitorManager Reference to BPMMonitorManager unique_ptr
 * @param defaultMonitorName Name for default monitor instance
 * @return Monitor ID of default monitor, or 0 if failed
 */
uint32_t initializeMonitorManager(
    std::unique_ptr<sparetools::bpm::BPMMonitorManager>& monitorManager,
    const char* defaultMonitorName = "Default Monitor"
);

/**
 * Initialize HTTP server with API endpoints
 * @param apiServer Reference to WebServer unique_ptr
 * @param bpmDetector BPM detector instance (raw pointer for API setup)
 * @param monitorManager Monitor manager instance (raw pointer for API setup)
 * @return true if server started successfully
 */
bool initializeHTTPServer(
    std::unique_ptr<WebServer>& apiServer,
    BPMDetector* bpmDetector,
    sparetools::bpm::BPMMonitorManager* monitorManager
);

/**
 * Update RGB LED status (ESP32-S3 specific)
 * @param r Red component (0-255)
 * @param g Green component (0-255)
 * @param b Blue component (0-255)
 */
void updateRGBLED(uint8_t r, uint8_t g, uint8_t b);

} // namespace BpmSetupHelpers

#endif // MAIN_SETUP_HELPERS_H
