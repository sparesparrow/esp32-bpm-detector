#include <Arduino.h>
#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>
#include "config.h"
#include "bpm_detector.h"
#include "display_handler.h"

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
    while (true) {
        // Sample audio at regular intervals
        bpm_detector.sample();
        delayMicroseconds(1000000 / SAMPLE_RATE);
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
    // GET /api/bpm - returns current BPM data
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

    // GET /api/settings - returns configuration
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

    // Health check endpoint
    server.on("/api/health", HTTP_GET, [](AsyncWebServerRequest* request) {
        StaticJsonDocument<128> doc;
        doc["status"] = "ok";
        doc["uptime"] = millis() / 1000;
        doc["heap_free"] = ESP.getFreeHeap();

        String response;
        serializeJson(doc, response);
        request->send(200, "application/json", response);
    });

    // Catch-all 404
    server.onNotFound([](AsyncWebServerRequest* request) {
        request->send(404, "application/json", "{\"error\": \"endpoint not found\"}");
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

    // Initialize BPM detector
    Serial.println("[BPM] Initializing BPM detector...");
    bpm_detector.begin(MICROPHONE_PIN);
    bpm_detector.setMinBPM(MIN_BPM);
    bpm_detector.setMaxBPM(MAX_BPM);

    // Setup WiFi
    setupWiFi();

    // Setup Web Server
    setupWebServer();

    // Create audio sampling task (runs on core 0)
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
