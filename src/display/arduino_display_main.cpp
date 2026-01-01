/**
 * Arduino Uno BPM Display Client
 * 
 * Receives BPM data from ESP32 BPM Detector via SoftwareSerial
 * and displays it on a 128x64 I2C OLED display (SSD1306)
 * 
 * This implementation uses SoftwareSerial to receive data from ESP32,
 * keeping the hardware serial (USB) free for debugging via Serial Monitor.
 * 
 * Hardware Connections:
 * =====================
 * OLED Display (I2C):
 *   SCL → A5 (Arduino SCL)
 *   SDA → A4 (Arduino SDA)
 *   VCC → 3.3V or 5V
 *   GND → GND
 * 
 * ESP32 Communication (SoftwareSerial):
 *   ESP32 GPIO17 (TX2) → Arduino D2 (SoftwareSerial RX)
 *   ESP32 GPIO16 (RX2) ← Arduino D3 (SoftwareSerial TX) [optional]
 *   GND ← → GND (common ground required!)
 * 
 * USB Serial:
 *   Still available for debugging via Serial Monitor at 9600 baud
 * 
 * Serial Protocol:
 * ================
 * ESP32 sends ASCII strings at 9600 baud:
 *   "BPM:120.5\n" - BPM value only
 *   "BPM:120.5,CONF:0.85\n" - BPM with confidence
 *   "STATUS:detecting\n" - Status message
 */

#ifdef ARDUINO_BPM_DISPLAY_CLIENT

#include <Arduino.h>
#include <Wire.h>
#include <SoftwareSerial.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ============================================================================
// SoftwareSerial Configuration (ESP32 Communication)
// ============================================================================
// Using SoftwareSerial frees up hardware serial for USB debugging
#define ESP32_RX_PIN 2   // Arduino D2 receives from ESP32 TX2 (GPIO17)
#define ESP32_TX_PIN 3   // Arduino D3 sends to ESP32 RX2 (GPIO16) - optional

SoftwareSerial esp32Serial(ESP32_RX_PIN, ESP32_TX_PIN);

// ============================================================================
// OLED Display Configuration
// ============================================================================
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1           // Reset pin (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C     // I2C address (0x3C for most 128x64 OLEDs)

// Create display object
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// ============================================================================
// BPM Data Storage
// ============================================================================
float currentBPM = 0.0;
float confidence = 0.0;
unsigned long lastUpdate = 0;
const unsigned long TIMEOUT_MS = 5000;  // 5 seconds without data = connection lost

// ============================================================================
// Serial Input Buffer
// ============================================================================
String inputBuffer = "";
const int MAX_BUFFER_SIZE = 64;  // Reduced for Arduino memory constraints

// ============================================================================
// Display State Machine
// ============================================================================
enum DisplayMode {
  MODE_SPLASH,
  MODE_WAITING,
  MODE_ACTIVE,
  MODE_TIMEOUT
};

DisplayMode currentMode = MODE_SPLASH;
unsigned long modeStartTime = 0;

// ============================================================================
// Function Prototypes
// ============================================================================
void showSplashScreen();
void showWaitingScreen();
void showBPMScreen();
void showTimeoutScreen();
void processBPMData(String data);
void updateDisplay();
void drawConfidenceBar(float conf);

// ============================================================================
// Setup
// ============================================================================
void setup() {
  // Initialize hardware serial for USB debugging
  Serial.begin(115200);
  Serial.println(F("BPM Display Starting..."));
  Serial.println(F("USB Serial: Debug output"));
  Serial.println(F("SoftwareSerial D2/D3: ESP32 data"));
  
  // Initialize SoftwareSerial for ESP32 communication
  esp32Serial.begin(115200);
  
  // Reserve buffer space (important for String on Arduino)
  inputBuffer.reserve(MAX_BUFFER_SIZE);
  
  // Initialize I2C for display
  Wire.begin();
  
  // Initialize OLED display
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("Display init failed!"));
    // If display init fails, blink LED forever
    pinMode(LED_BUILTIN, OUTPUT);
    while (1) {
      digitalWrite(LED_BUILTIN, HIGH);
      delay(200);
      digitalWrite(LED_BUILTIN, LOW);
      delay(200);
    }
  }
  
  Serial.println(F("Display initialized"));
  
  // Display initialized successfully
  display.clearDisplay();
  display.display();
  
  // Show splash screen
  currentMode = MODE_SPLASH;
  modeStartTime = millis();
  showSplashScreen();
  
  // Wait a moment on splash
  delay(2000);
  
  // Switch to waiting mode
  currentMode = MODE_WAITING;
  modeStartTime = millis();
  showWaitingScreen();
  
  Serial.println(F("Ready - waiting for ESP32 data on D2"));
}

// ============================================================================
// Main Loop
// ============================================================================
void loop() {
  // Read serial data from ESP32 via SoftwareSerial
  while (esp32Serial.available() > 0) {
    char inChar = (char)esp32Serial.read();
    
    if (inChar == '\n' || inChar == '\r') {
      // Complete line received
      if (inputBuffer.length() > 0) {
        processBPMData(inputBuffer);
        inputBuffer = "";
      }
    } else if (inputBuffer.length() < MAX_BUFFER_SIZE - 1) {
      inputBuffer += inChar;
    }
  }
  
  // Check for timeout
  unsigned long timeSinceUpdate = millis() - lastUpdate;
  
  if (currentMode == MODE_ACTIVE && timeSinceUpdate > TIMEOUT_MS) {
    currentMode = MODE_TIMEOUT;
    Serial.println(F("Connection timeout"));
    showTimeoutScreen();
  } else if (currentMode == MODE_TIMEOUT && timeSinceUpdate <= TIMEOUT_MS) {
    currentMode = MODE_ACTIVE;
    Serial.println(F("Connection restored"));
  }
  
  // Update display periodically (2Hz refresh rate)
  static unsigned long lastDisplayUpdate = 0;
  if (millis() - lastDisplayUpdate >= 500) {
    updateDisplay();
    lastDisplayUpdate = millis();
  }
  
  delay(10);  // Small delay for stability
}

// ============================================================================
// Process BPM Data from ESP32
// ============================================================================
void processBPMData(String data) {
  data.trim();
  
  // Debug output to USB serial
  Serial.print(F("RX: "));
  Serial.println(data);
  
  // Parse BPM value: "BPM:120.5" or "BPM:120.5,CONF:0.85"
  if (data.startsWith("BPM:")) {
    int colonPos = data.indexOf(':');
    int commaPos = data.indexOf(',');
    
    // Extract BPM
    String bpmStr;
    if (commaPos > 0) {
      bpmStr = data.substring(colonPos + 1, commaPos);
      
      // Extract confidence if present
      int confColonPos = data.indexOf(':', commaPos);
      if (confColonPos > 0) {
        String confStr = data.substring(confColonPos + 1);
        confidence = confStr.toFloat();
      }
    } else {
      bpmStr = data.substring(colonPos + 1);
      confidence = 0.0;  // No confidence data
    }
    
    currentBPM = bpmStr.toFloat();
    lastUpdate = millis();
    
    // Switch to active mode if not already
    if (currentMode != MODE_ACTIVE) {
      currentMode = MODE_ACTIVE;
      modeStartTime = millis();
      Serial.println(F("Connection active"));
    }
  }
  // Handle status messages
  else if (data.startsWith("STATUS:")) {
    String status = data.substring(7);
    Serial.print(F("Status: "));
    Serial.println(status);
  }
}

// ============================================================================
// Update Display Based on Current Mode
// ============================================================================
void updateDisplay() {
  switch (currentMode) {
    case MODE_ACTIVE:
      showBPMScreen();
      break;
    case MODE_TIMEOUT:
      showTimeoutScreen();
      break;
    case MODE_WAITING:
      showWaitingScreen();
      break;
    default:
      break;
  }
}

// ============================================================================
// Splash Screen
// ============================================================================
void showSplashScreen() {
  display.clearDisplay();
  
  // Title
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(30, 5);
  display.println(F("BPM"));
  
  display.setCursor(10, 25);
  display.println(F("Display"));
  
  // Subtitle
  display.setTextSize(1);
  display.setCursor(15, 50);
  display.print(F("Arduino Client v2"));
  
  display.display();
}

// ============================================================================
// Waiting Screen (animated)
// ============================================================================
void showWaitingScreen() {
  display.clearDisplay();
  
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  
  display.setCursor(15, 10);
  display.println(F("Waiting for"));
  display.setCursor(25, 25);
  display.println(F("ESP32 Data"));
  
  // Animated dots
  int dotCount = (millis() / 500) % 4;
  display.setCursor(50, 40);
  for (int i = 0; i < dotCount; i++) {
    display.print(F("."));
  }
  
  // Connection info
  display.setCursor(5, 55);
  display.print(F("RX:D2 @9600 baud"));
  
  display.display();
}

// ============================================================================
// BPM Display Screen
// ============================================================================
void showBPMScreen() {
  display.clearDisplay();
  
  // Large BPM value in center
  display.setTextSize(3);
  display.setTextColor(SSD1306_WHITE);
  
  // Format BPM with 1 decimal place
  char bpmStr[10];
  dtostrf(currentBPM, 5, 1, bpmStr);
  
  // Center the text
  int16_t x1, y1;
  uint16_t w, h;
  display.getTextBounds(bpmStr, 0, 0, &x1, &y1, &w, &h);
  int x = (SCREEN_WIDTH - w) / 2;
  
  display.setCursor(x, 8);
  display.print(bpmStr);
  
  // "BPM" label
  display.setTextSize(1);
  display.setCursor(52, 35);
  display.print(F("BPM"));
  
  // Confidence bar (if confidence data available)
  if (confidence > 0.0) {
    drawConfidenceBar(confidence);
  }
  
  // Activity indicator (blinking dot for recent updates)
  unsigned long timeSinceUpdate = millis() - lastUpdate;
  if (timeSinceUpdate < 500) {
    display.fillCircle(120, 5, 3, SSD1306_WHITE);
  } else {
    display.drawCircle(120, 5, 3, SSD1306_WHITE);
  }
  
  // Time since last update
  display.setTextSize(1);
  display.setCursor(0, 56);
  display.print(F("Updated: "));
  display.print(timeSinceUpdate / 1000);
  display.print(F("s"));
  
  // Show confidence percentage if available
  if (confidence > 0.0) {
    display.setCursor(80, 56);
    display.print((int)(confidence * 100));
    display.print(F("%"));
  }
  
  display.display();
}

// ============================================================================
// Draw Confidence Bar
// ============================================================================
void drawConfidenceBar(float conf) {
  // Draw confidence bar at bottom of BPM area
  int barWidth = (int)(conf * 100);  // Max 100 pixels
  int barX = (SCREEN_WIDTH - 100) / 2;  // Center the bar
  int barY = 46;
  int barHeight = 6;
  
  // Draw outline
  display.drawRect(barX, barY, 100, barHeight, SSD1306_WHITE);
  
  // Fill based on confidence
  if (barWidth > 0) {
    display.fillRect(barX + 1, barY + 1, barWidth - 2, barHeight - 2, SSD1306_WHITE);
  }
}

// ============================================================================
// Timeout Screen
// ============================================================================
void showTimeoutScreen() {
  display.clearDisplay();
  
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  
  display.setCursor(20, 15);
  display.println(F("Connection"));
  display.setCursor(35, 28);
  display.println(F("Lost!"));
  
  // Last known BPM
  if (currentBPM > 0) {
    display.setCursor(10, 45);
    display.print(F("Last: "));
    display.print((int)currentBPM);
    display.print(F(" BPM"));
  }
  
  // Reconnection hint
  display.setCursor(5, 56);
  display.print(F("Check ESP32 conn."));
  
  display.display();
}

#endif // ARDUINO_BPM_DISPLAY_CLIENT
