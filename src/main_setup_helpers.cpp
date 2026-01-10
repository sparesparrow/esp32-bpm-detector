#include "main_setup_helpers.h"
#include "api_endpoints.h"
#include "config.h"
#include <Arduino.h>

// RGB functionality disabled to avoid dependency issues
// #ifdef RGB_BUILTIN
// #include <Adafruit_NeoPixel.h>
// #endif

namespace BpmSetupHelpers {

bool initializeSerial() {
    Serial.begin(115200);
    delay(1000); // Allow serial port to stabilize

    Serial.println("\n\n========================================");
    Serial.println("ESP32-S3 BPM Detector Starting...");
    Serial.println("========================================");
    Serial.flush();

    return true;
}

bool initializeWiFiAP(const char* ssid, const char* password) {
    Serial.println("Setting up WiFi Access Point...");

    WiFi.mode(WIFI_AP);
    WiFi.begin(); // Initialize WiFi even in AP mode
    bool apStarted = WiFi.softAP(ssid, password);

    if (apStarted) {
        delay(1000); // Wait for AP to be fully established

        IPAddress apIP = WiFi.softAPIP();
        Serial.println("\n=== WiFi Access Point Started ===");
        Serial.print("SSID: ");
        Serial.print(ssid);
        Serial.print(" | Password: ");
        Serial.print(password);
        Serial.print(" | IP Address: ");
        Serial.println(apIP);

        updateRGBLED(0, 128, 0); // Green = AP started
        return true;
    } else {
        Serial.println("Failed to start Access Point!");
        updateRGBLED(128, 0, 0); // Red = error
        return false;
    }
}

bool initializeLEDController(std::unique_ptr<ILEDController>& ledController) {
    Serial.println("Initializing LED controller...");
    ledController = std::unique_ptr<ILEDController>(new LEDStripController());
    
    if (ledController->begin()) {
        Serial.println("LED controller initialized successfully!");
        ledController->showStatus(LedStatus::LED_STATUS_BOOTING);
        return true;
    } else {
        Serial.println("LED controller initialization failed");
        return false;
    }
}

bool initializeAudioInput(std::unique_ptr<AudioInput>& audioInput, uint8_t micPin) {
    Serial.println("Initializing audio input...");
    audioInput = std::unique_ptr<AudioInput>(new AudioInput());
    audioInput->begin(micPin);
    return true;
}

bool initializeBPMDetector(std::unique_ptr<BPMDetector>& bpmDetector, uint8_t micPin) {
    Serial.println("Initializing BPM detector...");
    bpmDetector = std::unique_ptr<BPMDetector>(new BPMDetector(SAMPLE_RATE, FFT_SIZE));
    bpmDetector->begin(micPin);
    return true;
}

uint32_t initializeMonitorManager(
    std::unique_ptr<sparetools::bpm::BPMMonitorManager>& monitorManager,
    const char* defaultMonitorName) {
    
    Serial.println("Initializing BPM monitor manager...");
    monitorManager = std::unique_ptr<sparetools::bpm::BPMMonitorManager>(
        new sparetools::bpm::BPMMonitorManager()
    );
    
    uint32_t defaultMonitorId = monitorManager->spawnMonitor(defaultMonitorName);
    if (defaultMonitorId > 0) {
        Serial.print("Default monitor spawned with ID: ");
        Serial.println(defaultMonitorId);
    } else {
        Serial.println("Warning: Failed to spawn default monitor");
    }
    
    return defaultMonitorId;
}

bool initializeHTTPServer(
    std::unique_ptr<WebServer>& apiServer,
    BPMDetector* bpmDetector,
    sparetools::bpm::BPMMonitorManager* monitorManager) {
    
    Serial.println("Initializing HTTP server...");
    
    apiServer = std::unique_ptr<WebServer>(new WebServer(80));
    
    // Setup API endpoints with monitor manager support
    setupApiEndpoints(apiServer.get(), bpmDetector, monitorManager);
    
    // Add simple root endpoint (capture apiServer by reference in lambda)
    WebServer* serverPtr = apiServer.get();
    apiServer->on("/", HTTP_GET, [serverPtr]() {
        Serial.println("HTTP request received on /");
        if (serverPtr) {
            serverPtr->send(200, "text/plain", "ESP32 BPM Detector - AP Mode OK");
        }
    });
    
    // Note: Legacy /api/bpm endpoint is handled by setupApiEndpoints()
    // which sets up proper lambda captures for apiServer and bpmDetector
    
    // Start server
    apiServer->begin();
    Serial.println("HTTP server started on port 80");
    
    // Verify server started successfully
    delay(100); // Brief delay for server initialization
    if (WiFi.status() == WL_CONNECTED || WiFi.getMode() == WIFI_AP) {
        Serial.println("HTTP server initialization successful");
        return true;
    } else {
        Serial.println("WARNING: HTTP server may not be fully initialized");
        return false;
    }
}

void updateRGBLED(uint8_t r, uint8_t g, uint8_t b) {
#ifdef RGB_BUILTIN
    neopixelWrite(RGB_BUILTIN, r, g, b);
#endif
}

} // namespace BpmSetupHelpers
