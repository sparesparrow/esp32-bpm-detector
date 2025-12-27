#include <Arduino.h>
#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include "config.h"
#include "bpm_detector.h"
#include "display_handler.h"
#include "bpm_generated.h"

// FreeRTOS includes
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

// Global instances
AsyncWebServer server(80);
BPMDetector bpm_detector(SAMPLE_RATE, FFT_SIZE);
DisplayHandler display;

// WiFi credentials (from config.h)
const char* ssid = WIFI_SSID;
const char* password = WIFI_PASSWORD;

// Global state
struct {
    float current_bpm = 0;
    float confidence = 0;
    float signal_level = 0;
    String status = "initializing";
    unsigned long last_update = 0;
} bpm_state;

// Task for continuous audio sampling
void audioSamplingTask(void* parameter) {
    const TickType_t sampleDelay = pdMS_TO_TICKS(1000 / SAMPLE_RATE);

    while (true) {
        // Sample audio at regular intervals
        bpm_detector.sample();

        // Use FreeRTOS delay to allow other tasks to run
        vTaskDelay(sampleDelay);
    }
}

// Setup WiFi connection
void setupWiFi() {
    Serial.println("\n[WiFi] Connecting to WiFi...");
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n[WiFi] Connected!");
        Serial.print("[WiFi] IP address: ");
        Serial.println(WiFi.localIP());
        display.showStatus("WiFi OK");
    } else {
        Serial.println("\n[WiFi] Connection failed!");
        display.showStatus("WiFi Failed");
    }
}

// Setup REST API endpoints
void setupWebServer() {
    // GET /api/bpm - returns current BPM data as FlatBuffers
    server.on("/api/bpm", HTTP_GET, [](AsyncWebServerRequest* request) {
        // Create FlatBuffers builder
        flatbuffers::FlatBufferBuilder builder(256);

        // Create BPMData
        auto status_str = builder.CreateString(bpm_state.status.c_str());
        auto bpm_data = sparetools::bpm::CreateBPMData(
            builder,
            bpm_state.current_bpm,
            bpm_state.confidence,
            bpm_state.signal_level,
            status_str,
            static_cast<uint64_t>(millis())
        );

        // Create envelope
        auto source_str = builder.CreateString("esp32-bpm-detector");
        auto envelope = sparetools::bpm::CreateBPMEnvelope(
            builder,
            sparetools::bpm::BPMMessage::BPMData,
            bpm_data.Union(),
            1, // message_id
            source_str
        );

        builder.Finish(envelope);

        // Send binary response using callback
        request->send_P(200, "application/octet-stream", builder.GetBufferPointer(), builder.GetSize());
    });

    // GET /api/settings - returns configuration as FlatBuffers
    server.on("/api/settings", HTTP_GET, [](AsyncWebServerRequest* request) {
        // Create FlatBuffers builder
        flatbuffers::FlatBufferBuilder builder(256);

        // Create BPMSettings
        auto version_str = builder.CreateString("1.0.0");
        auto bpm_settings = sparetools::bpm::CreateBPMSettings(
            builder,
            MIN_BPM,
            MAX_BPM,
            SAMPLE_RATE,
            FFT_SIZE,
            version_str
        );

        // Create envelope
        auto source_str = builder.CreateString("esp32-bpm-detector");
        auto envelope = sparetools::bpm::CreateBPMEnvelope(
            builder,
            sparetools::bpm::BPMMessage::BPMSettings,
            bpm_settings.Union(),
            2, // message_id
            source_str
        );

        builder.Finish(envelope);

        // Send binary response using callback
        request->send_P(200, "application/octet-stream", builder.GetBufferPointer(), builder.GetSize());
    });

    // Health check endpoint
    server.on("/api/health", HTTP_GET, [](AsyncWebServerRequest* request) {
        // Create FlatBuffers builder
        flatbuffers::FlatBufferBuilder builder(128);

        // Create BPMHealth
        auto status_str = builder.CreateString("ok");
        auto bpm_health = sparetools::bpm::CreateBPMHealth(
            builder,
            status_str,
            static_cast<uint64_t>(millis()),
            static_cast<uint64_t>(ESP.getFreeHeap())
        );

        // Create envelope
        auto source_str = builder.CreateString("esp32-bpm-detector");
        auto envelope = sparetools::bpm::CreateBPMEnvelope(
            builder,
            sparetools::bpm::BPMMessage::BPMHealth,
            bpm_health.Union(),
            3, // message_id
            source_str
        );

        builder.Finish(envelope);

        // Send binary response using callback
        request->send_P(200, "application/octet-stream", builder.GetBufferPointer(), builder.GetSize());
    });

    // Catch-all 404
    server.onNotFound([](AsyncWebServerRequest* request) {
        // Create FlatBuffers builder for error response
        flatbuffers::FlatBufferBuilder builder(128);

        // Create BPMHealth with error status (reusing health structure)
        auto error_str = builder.CreateString("endpoint not found");
        auto error_response = sparetools::bpm::CreateBPMHealth(
            builder,
            error_str,
            static_cast<uint64_t>(millis()),
            static_cast<uint64_t>(ESP.getFreeHeap())
        );

        // Create envelope
        auto source_str = builder.CreateString("esp32-bpm-detector");
        auto envelope = sparetools::bpm::CreateBPMEnvelope(
            builder,
            sparetools::bpm::BPMMessage::BPMHealth,
            error_response.Union(),
            404, // message_id = error code
            source_str
        );

        builder.Finish(envelope);

        // Send binary error response
        request->send_P(404, "application/octet-stream", builder.GetBufferPointer(), builder.GetSize());
    });

    server.begin();
    Serial.println("[Server] Web server started on port 80");
}

void setup() {
    Serial.begin(115200);
    delay(100);
    
    Serial.println("\n\n[System] ESP32 BPM Detector v1.0.0");
    Serial.println("[System] Starting initialization...");

    // Initialize display (if available)
    display.begin();
    display.showStatus("Init...");

    // Initialize BPM detector with stereo input
    Serial.println("[BPM] Initializing BPM detector with stereo input...");
    bpm_detector.beginStereo(MICROPHONE_LEFT_PIN, MICROPHONE_RIGHT_PIN);
    bpm_detector.setMinBPM(MIN_BPM);
    bpm_detector.setMaxBPM(MAX_BPM);

    // Setup WiFi
    setupWiFi();

    // Setup Web Server
    setupWebServer();

    // Create audio sampling task (runs on core 1 with lower priority)
    xTaskCreatePinnedToCore(
        audioSamplingTask,
        "AudioSamplingTask",
        4096,
        NULL,
        1,
        NULL,
        1
    );

    Serial.println("[System] Initialization complete!");
    display.showStatus("Ready");
}

void loop() {
    // Detect BPM every 100ms
    static unsigned long last_detection = 0;
    if (millis() - last_detection > 100) {
        BPMDetector::BPMData data = bpm_detector.detect();
        
        // Update global state
        bpm_state.current_bpm = data.bpm;
        bpm_state.confidence = data.confidence;
        bpm_state.signal_level = data.signal_level;
        bpm_state.status = data.status;
        bpm_state.last_update = millis();

        // Display BPM on local display (if available)
        if (data.status == "detecting") {
            display.showBPM((int)data.bpm, data.confidence);
        } else if (data.status == "low_signal") {
            display.showStatus("Low Signal");
        } else if (data.status == "error") {
            display.showStatus("Error");
        }

        // Debug output to serial
        Serial.printf("[BPM] %.1f BPM | Confidence: %.2f | Level: %.2f | Status: %s\n",
                      data.bpm, data.confidence, data.signal_level, data.status.c_str());

        last_detection = millis();
    }

    // Check WiFi connection periodically
    static unsigned long last_wifi_check = 0;
    if (millis() - last_wifi_check > 5000) {
        if (WiFi.status() != WL_CONNECTED) {
            Serial.println("[WiFi] Connection lost, attempting reconnect...");
            WiFi.reconnect();
        }
        last_wifi_check = millis();
    }

    // Periodic memory check
    static unsigned long last_memory_check = 0;
    if (millis() - last_memory_check > 30000) {
        Serial.printf("[Memory] Heap free: %d bytes, min: %d bytes\n",
                      ESP.getFreeHeap(), ESP.getMinFreeHeap());
        last_memory_check = millis();
    }

    delay(10);
}
