/**
 * ESP32 BPM Detector - FlatBuffers Integration Example
 *
 * This example demonstrates how to integrate FlatBuffers binary protocol
 * alongside the existing JSON REST API for improved performance.
 */

#include <Arduino.h>
#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>
#include <flatbuffers/flatbuffers.h>
#include "bpm_flatbuffers.h"
#include "bpm_detector.h"
#include "display_handler.h"

// Include generated FlatBuffers header
#include "bpm_protocol_generated.h"

// Global instances (same as original)
AsyncWebServer server(80);
BPMDetector bpm_detector(SAMPLE_RATE, FFT_SIZE);
DisplayHandler display;

// FlatBuffers builder for creating messages
flatbuffers::FlatBufferBuilder builder(1024);

// Message ID counter for request/response correlation
uint32_t message_id_counter = 0;

// WiFi credentials
const char* ssid = WIFI_SSID;
const char* password = WIFI_PASSWORD;

// Global BPM state
struct {
    float current_bpm = 0;
    float confidence = 0;
    float signal_level = 0;
    String status = "initializing";
    unsigned long last_update = 0;
} bpm_state;

// Audio sampling task (unchanged)
void audioSamplingTask(void* parameter) {
    while (true) {
        bpm_detector.sample();
        delayMicroseconds(1000000 / SAMPLE_RATE);
    }
}

// WiFi setup (unchanged)
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

// Setup enhanced web server with both JSON and FlatBuffers endpoints
void setupWebServer() {
    // ==========================================
    // ORIGINAL JSON ENDPOINTS (maintained for compatibility)
    // ==========================================

    // GET /api/bpm - JSON format (existing)
    server.on("/api/bpm", HTTP_GET, [](AsyncWebServerRequest* request) {
        StaticJsonDocument<256> doc;
        doc["bpm"] = bpm_state.current_bpm;
        doc["confidence"] = bpm_state.confidence;
        doc["signal_level"] = bpm_state.signal_level;
        doc["status"] = bpm_state.status;
        doc["timestamp"] = millis();

        String response;
        serializeJson(doc, response);

        AsyncWebServerResponse* res = request->beginResponse(200, "application/json", response);
        res->addHeader("Access-Control-Allow-Origin", "*");
        request->send(res);
    });

    // GET /api/settings - JSON format (existing)
    server.on("/api/settings", HTTP_GET, [](AsyncWebServerRequest* request) {
        StaticJsonDocument<256> doc;
        doc["min_bpm"] = MIN_BPM;
        doc["max_bpm"] = MAX_BPM;
        doc["sample_rate"] = SAMPLE_RATE;
        doc["fft_size"] = FFT_SIZE;
        doc["version"] = "1.0.0";

        String response;
        serializeJson(doc, response);

        AsyncWebServerResponse* res = request->beginResponse(200, "application/json", response);
        res->addHeader("Access-Control-Allow-Origin", "*");
        request->send(res);
    });

    // ==========================================
    // NEW FLATBUFFERS BINARY ENDPOINTS
    // ==========================================

    // GET /api/bpm/fb - FlatBuffers binary format
    server.on("/api/bpm/fb", HTTP_GET, [](AsyncWebServerRequest* request) {
        // Clear the builder for a fresh message
        builder.Clear();

        // Determine detection status
        bpm::protocol::DetectionStatus fb_status;
        if (bpm_state.status == "detecting") {
            fb_status = bpm::protocol::DetectionStatus::DETECTING;
        } else if (bpm_state.status == "low_signal") {
            fb_status = bpm::protocol::DetectionStatus::LOW_SIGNAL;
        } else if (bpm_state.status == "error") {
            fb_status = bpm::protocol::DetectionStatus::ERROR;
        } else {
            fb_status = bpm::protocol::DetectionStatus::INITIALIZING;
        }

        // Create BPM update message
        auto bpm_update_offset = BPMFlatBuffers::createBPMUpdate(
            bpm_state.current_bpm,
            bpm_state.confidence,
            bpm_state.signal_level,
            fb_status,
            builder
        );

        // Create message envelope
        auto envelope_offset = BPMFlatBuffers::createMessageEnvelope(
            bpm::protocol::MessageType::BPM_UPDATE,
            bpm_update_offset.Union(),
            ++message_id_counter,
            builder
        );

        // Serialize to binary
        auto binary_data = BPMFlatBuffers::serializeMessage(envelope_offset, builder);

        // Send binary response
        AsyncWebServerResponse* res = request->beginResponse(200, "application/octet-stream",
            (const char*)binary_data.data(), binary_data.size());
        res->addHeader("Access-Control-Allow-Origin", "*");
        res->addHeader("X-Message-Type", "BPM_UPDATE");
        res->addHeader("X-Protocol", "FlatBuffers");
        request->send(res);
    });

    // GET /api/status/fb - Device status in FlatBuffers format
    server.on("/api/status/fb", HTTP_GET, [](AsyncWebServerRequest* request) {
        builder.Clear();

        // Create status update message
        auto status_update_offset = BPMFlatBuffers::createStatusUpdate(
            millis() / 1000,        // uptime_seconds
            ESP.getFreeHeap(),      // free_heap_bytes
            35,                     // cpu_usage_percent (estimated)
            WiFi.RSSI(),            // wifi_rssi
            builder
        );

        // Create message envelope
        auto envelope_offset = BPMFlatBuffers::createMessageEnvelope(
            bpm::protocol::MessageType::STATUS_UPDATE,
            status_update_offset.Union(),
            ++message_id_counter,
            builder
        );

        // Serialize and send
        auto binary_data = BPMFlatBuffers::serializeMessage(envelope_offset, builder);

        AsyncWebServerResponse* res = request->beginResponse(200, "application/octet-stream",
            (const char*)binary_data.data(), binary_data.size());
        res->addHeader("Access-Control-Allow-Origin", "*");
        res->addHeader("X-Message-Type", "STATUS_UPDATE");
        res->addHeader("X-Protocol", "FlatBuffers");
        request->send(res);
    });

    // POST /api/bpm/fb - Accept FlatBuffers BPM data (for testing)
    server.on("/api/bpm/fb", HTTP_POST, [](AsyncWebServerRequest* request) {
        // In a real implementation, you'd parse the binary FlatBuffers data
        // For now, just acknowledge receipt
        request->send(200, "application/json", "{\"status\":\"ok\",\"message\":\"FlatBuffers data received\"}");
    }, nullptr, [](AsyncWebServerRequest* request, uint8_t* data, size_t len, size_t index, size_t total) {
        // Handle incoming binary data
        if (len > 0 && len < 2048) { // Reasonable size limit
            Serial.printf("[FlatBuffers] Received %d bytes of binary data\n", len);

            // In a real implementation, you'd deserialize and process the data:
            // auto envelope = bpm::protocol::GetMessageEnvelope(data);
            // auto bpm_update = BPMFlatBuffers::extractBPMUpdate(envelope);
            // if (bpm_update) {
            //     Serial.printf("Received BPM: %.1f\n", bpm_update->bpm());
            // }
        }
    });

    // Health check endpoint (unchanged)
    server.on("/api/health", HTTP_GET, [](AsyncWebServerRequest* request) {
        StaticJsonDocument<128> doc;
        doc["status"] = "ok";
        doc["uptime"] = millis() / 1000;
        doc["heap_free"] = ESP.getFreeHeap();

        String response;
        serializeJson(doc, response);
        request->send(200, "application/json", response);
    });

    // Catch-all 404 (unchanged)
    server.onNotFound([](AsyncWebServerRequest* request) {
        request->send(404, "application/json", "{\"error\": \"endpoint not found\"}");
    });

    server.begin();
    Serial.println("[Server] Enhanced web server started on port 80");
    Serial.println("[Server] Supports both JSON and FlatBuffers protocols");
}

void setup() {
    Serial.begin(115200);
    delay(100);

    Serial.println("\n\n[System] ESP32 BPM Detector v1.0.0 - FlatBuffers Enhanced");
    Serial.println("[System] Starting initialization...");

    // Initialize display
    display.begin();
    display.showStatus("Init...");

    // Initialize BPM detector
    Serial.println("[BPM] Initializing BPM detector...");
    bpm_detector.begin(MICROPHONE_PIN);
    bpm_detector.setMinBPM(MIN_BPM);
    bpm_detector.setMaxBPM(MAX_BPM);

    // Setup WiFi
    setupWiFi();

    // Setup enhanced web server
    setupWebServer();

    // Create audio sampling task
    xTaskCreatePinnedToCore(
        audioSamplingTask,
        "AudioSamplingTask",
        4096,
        NULL,
        1,
        NULL,
        0
    );

    Serial.println("[System] Initialization complete!");
    display.showStatus("Ready");
}

void loop() {
    // Detect BPM every 100ms (unchanged)
    static unsigned long last_detection = 0;
    if (millis() - last_detection > 100) {
        BPMDetector::BPMData data = bpm_detector.detect();

        // Update global state
        bpm_state.current_bpm = data.bpm;
        bpm_state.confidence = data.confidence;
        bpm_state.signal_level = data.signal_level;
        bpm_state.status = data.status;
        bpm_state.last_update = millis();

        // Display BPM on local display
        if (data.status == "detecting") {
            display.showBPM((int)data.bpm, data.confidence);
        } else if (data.status == "low_signal") {
            display.showStatus("Low Signal");
        } else if (data.status == "error") {
            display.showStatus("Error");
        }

        // Debug output
        Serial.printf("[BPM] %.1f BPM | Confidence: %.2f | Level: %.2f | Status: %s\n",
                      data.bpm, data.confidence, data.signal_level, data.status.c_str());

        last_detection = millis();
    }

    // Check WiFi connection (unchanged)
    static unsigned long last_wifi_check = 0;
    if (millis() - last_wifi_check > 5000) {
        if (WiFi.status() != WL_CONNECTED) {
            Serial.println("[WiFi] Connection lost, attempting reconnect...");
            WiFi.reconnect();
        }
        last_wifi_check = millis();
    }

    // Periodic memory check (unchanged)
    static unsigned long last_memory_check = 0;
    if (millis() - last_memory_check > 30000) {
        Serial.printf("[Memory] Heap free: %d bytes, min: %d bytes\n",
                      ESP.getFreeHeap(), ESP.getMinFreeHeap());
        last_memory_check = millis();
    }

    delay(10);
}