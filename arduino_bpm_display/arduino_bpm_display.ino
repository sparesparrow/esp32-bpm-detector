/**
 * Arduino Uno BPM Display Client
 * 
 * Receives BPM data from ESP32 BPM Detector via SoftwareSerial
 * and displays it on a 128x64 I2C OLED display (SSD1306)
 * 
 * This sketch is for use with Arduino IDE. For PlatformIO users,
 * see src/arduino_display_main.cpp in the main project.
 * 
 * Required Libraries (install via Arduino Library Manager):
 * - Adafruit SSD1306
 * - Adafruit GFX Library
 * - Adafruit BusIO
 * - SoftwareSerial (built-in)
 * 
 * Hardware Connections:
 * =====================
 * OLED Display (I2C):
 *   SCL → A5 (Arduino SCL)
 *   SDA → A4 (Arduino SDA)
 *   VCC → 3.3V or 5V (check your display)
 *   GND → GND
 * 
 * ESP32 Communication (SoftwareSerial):
 *   ESP32 GPIO17 (TX2) → Arduino D2 (SoftwareSerial RX)
 *   ESP32 GPIO16 (RX2) ← Arduino D3 (SoftwareSerial TX) [optional]
 *   GND ← → GND (common ground REQUIRED!)
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

#include <Wire.h>
#include <SoftwareSerial.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ============================================================================
// SoftwareSerial Configuration (ESP32 Communication)
// ============================================================================
// Using SoftwareSerial frees up hardware serial (USB) for debugging
#define ESP32_RX_PIN 2   // Arduino D2 receives from ESP32 TX2 (GPIO17)
#define ESP32_TX_PIN 3   // Arduino D3 sends to ESP32 RX2 (GPIO16) - optional

SoftwareSerial esp32Serial(ESP32_RX_PIN, ESP32_TX_PIN);

// ============================================================================
// OLED Display Configuration
// ============================================================================
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1           // Reset pin (-1 if sharing Arduino reset)
#define SCREEN_ADDRESS 0x3C     // I2C address (0x3C for most 128x64 OLEDs)

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// ============================================================================
// BPM Data Storage
// ============================================================================
float currentBPM = 0.0;
float confidence = 0.0;
unsigned long lastUpdate = 0;
const unsigned long TIMEOUT_MS = 5000;  // 5 seconds = connection lost

// ============================================================================
// Serial Input Buffer
// ============================================================================
String inputBuffer = "";
const int MAX_BUFFER_SIZE = 64;

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
  
  // Reserve buffer space
  inputBuffer.reserve(MAX_BUFFER_SIZE);
  
  // Initialize I2C for display
  Wire.begin();
  
  // Initialize OLED display
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("Display init failed!"));
    pinMode(LED_BUILTIN, OUTPUT);
    while (1) {
      digitalWrite(LED_BUILTIN, HIGH);
      delay(200);
      digitalWrite(LED_BUILTIN, LOW);
      delay(200);
    }
  }
  
  Serial.println(F("Display initialized"));
  
  display.clearDisplay();
  display.display();
  
  // Show splash screen
  currentMode = MODE_SPLASH;
  modeStartTime = millis();
  showSplashScreen();
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
  
  // Update display periodically (2Hz refresh)
  static unsigned long lastDisplayUpdate = 0;
  if (millis() - lastDisplayUpdate >= 500) {
    updateDisplay();
    lastDisplayUpdate = millis();
  }
  
  delay(10);
}

// ============================================================================
// Process BPM Data from ESP32
// ============================================================================
void processBPMData(String data) {
  data.trim();
  
  // Debug output
  Serial.print(F("RX: "));
  Serial.println(data);
  
  // Parse: "BPM:120.5" or "BPM:120.5,CONF:0.85"
  if (data.startsWith("BPM:")) {
    int colonPos = data.indexOf(':');
    int commaPos = data.indexOf(',');
    
    String bpmStr;
    if (commaPos > 0) {
      bpmStr = data.substring(colonPos + 1, commaPos);
      
      // Extract confidence
      int confColonPos = data.indexOf(':', commaPos);
      if (confColonPos > 0) {
        String confStr = data.substring(confColonPos + 1);
        confidence = confStr.toFloat();
      }
    } else {
      bpmStr = data.substring(colonPos + 1);
      confidence = 0.0;
    }
    
    currentBPM = bpmStr.toFloat();
    lastUpdate = millis();
    
    if (currentMode != MODE_ACTIVE) {
      currentMode = MODE_ACTIVE;
      modeStartTime = millis();
      Serial.println(F("Connection active"));
    }
  }
  else if (data.startsWith("STATUS:")) {
    String status = data.substring(7);
    Serial.print(F("Status: "));
    Serial.println(status);
  }
}

// ============================================================================
// Display Update
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
  
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(30, 5);
  display.println(F("BPM"));
  
  display.setCursor(10, 25);
  display.println(F("Display"));
  
  display.setTextSize(1);
  display.setCursor(15, 50);
  display.print(F("Arduino Client v2"));
  
  display.display();
}

// ============================================================================
// Waiting Screen
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
  
  display.setCursor(5, 55);
  display.print(F("RX:D2 @9600 baud"));
  
  display.display();
}

// ============================================================================
// BPM Display Screen
// ============================================================================
void showBPMScreen() {
  display.clearDisplay();
  
  // Large BPM value
  display.setTextSize(3);
  display.setTextColor(SSD1306_WHITE);
  
  char bpmStr[10];
  dtostrf(currentBPM, 5, 1, bpmStr);
  
  // Center text
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
  
  // Confidence bar
  if (confidence > 0.0) {
    drawConfidenceBar(confidence);
  }
  
  // Activity indicator
  unsigned long timeSinceUpdate = millis() - lastUpdate;
  if (timeSinceUpdate < 500) {
    display.fillCircle(120, 5, 3, SSD1306_WHITE);
  } else {
    display.drawCircle(120, 5, 3, SSD1306_WHITE);
  }
  
  // Update time
  display.setTextSize(1);
  display.setCursor(0, 56);
  display.print(F("Updated: "));
  display.print(timeSinceUpdate / 1000);
  display.print(F("s"));
  
  // Confidence percentage
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
  int barWidth = (int)(conf * 100);
  int barX = (SCREEN_WIDTH - 100) / 2;
  int barY = 46;
  int barHeight = 6;
  
  display.drawRect(barX, barY, 100, barHeight, SSD1306_WHITE);
  
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
  
  if (currentBPM > 0) {
    display.setCursor(10, 45);
    display.print(F("Last: "));
    display.print((int)currentBPM);
    display.print(F(" BPM"));
  }
  
  display.setCursor(5, 56);
  display.print(F("Check ESP32 conn."));
  
  display.display();
}
