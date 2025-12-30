# Arduino Uno BPM Display Wiring Guide

This guide explains how to wire an Arduino Uno with an SSD1306 OLED display to receive and display BPM data from the ESP32 BPM Detector.

## Overview

The Arduino Uno acts as a dedicated BPM display client:
- Receives BPM data from ESP32 via SoftwareSerial (on pins D2/D3)
- Displays BPM on a 128x64 I2C OLED
- USB serial remains available for debugging

## Components Required

| Component | Description |
|-----------|-------------|
| Arduino Uno | Main display controller |
| SSD1306 OLED Display | 128x64 I2C display (0.96" typical) |
| ESP32-S3 DevKit | BPM detector (or other ESP32) |
| Jumper wires | 5-6 wires for connections |
| USB cables | For programming and power |

## Wiring Diagram

```
                    ESP32-S3                          Arduino Uno
                   ┌─────────┐                       ┌─────────┐
                   │         │                       │         │
    [Audio In] ──> │ GPIO5   │                       │ D2  ◄───┼── SoftwareSerial RX
                   │ GPIO6   │                       │ D3  ───>│   SoftwareSerial TX (opt)
                   │         │                       │         │
                   │ GPIO17  ├───────────────────────┤ D2      │   BPM Data
                   │  (TX2)  │                       │         │
                   │         │                       │ A4  ────┼── I2C SDA ──> OLED SDA
                   │ GPIO16  │<──────────────────────┤ D3      │   (optional)
                   │  (RX2)  │                       │ A5  ────┼── I2C SCL ──> OLED SCL
                   │         │                       │         │
                   │   GND   ├───────────────────────┤ GND     │   Common Ground
                   │         │                       │ 3.3V/5V─┼──────────────> OLED VCC
                   └─────────┘                       └─────────┘
```

## Connection Tables

### OLED Display (SSD1306) to Arduino Uno

| OLED Pin | Arduino Pin | Description |
|----------|-------------|-------------|
| VCC | 3.3V or 5V | Power supply (check your display's voltage tolerance) |
| GND | GND | Ground |
| SCL | A5 | I2C Clock |
| SDA | A4 | I2C Data |

> **Note:** Most SSD1306 displays work with both 3.3V and 5V. Check your specific display's documentation.

### ESP32 to Arduino Uno (Serial Communication)

| ESP32 Pin | Arduino Pin | Description |
|-----------|-------------|-------------|
| GPIO17 (TX2) | D2 | BPM data from ESP32 (SoftwareSerial RX) |
| GND | GND | Common ground (**REQUIRED!**) |

### Optional: Bidirectional Communication

| ESP32 Pin | Arduino Pin | Description |
|-----------|-------------|-------------|
| GPIO16 (RX2) | D3 | Commands to ESP32 (SoftwareSerial TX) - future use |

## Important Notes

### 1. Common Ground is Essential
Always connect ESP32 GND to Arduino GND. Without a common ground reference, serial communication will fail or be unreliable.

### 2. Logic Levels
- ESP32 is 3.3V logic
- Arduino Uno is 5V tolerant but outputs 5V

For **ESP32 TX → Arduino RX**: Safe. Arduino can read 3.3V as HIGH.

For **Arduino TX → ESP32 RX** (optional bidirectional): The ESP32 GPIO pins are **not** 5V tolerant. Use a level shifter or voltage divider if bidirectional communication is needed:

```
Arduino D3 ──[1kΩ]──┬──[2kΩ]── GND
                    │
                    └───────── ESP32 GPIO16 (RX2)
```

### 3. USB Debugging
Using SoftwareSerial for ESP32 communication keeps the hardware serial (USB) free:
- Arduino Serial Monitor: Debug output at 9600 baud
- View received BPM data and connection status

### 4. Baud Rate
Both devices communicate at **9600 baud** for reliable SoftwareSerial operation. Higher baud rates (like 115200) can cause data corruption with SoftwareSerial on Arduino Uno.

## Serial Protocol

ESP32 sends ASCII text messages at 9600 baud:

| Message Format | Example | Description |
|----------------|---------|-------------|
| `BPM:<value>\n` | `BPM:120.5\n` | BPM value only |
| `BPM:<value>,CONF:<confidence>\n` | `BPM:120.5,CONF:0.85\n` | BPM with confidence (0.0-1.0) |
| `STATUS:<status>\n` | `STATUS:detecting\n` | Status message |

## Building and Uploading

### PlatformIO

```bash
# Build and upload ESP32 firmware
pio run -e esp32s3 -t upload

# Build and upload Arduino display client
pio run -e arduino_uno_display -t upload

# Monitor ESP32 (debug output)
pio device monitor -p /dev/ttyACM0 -b 115200

# Monitor Arduino (debug output)
pio device monitor -p /dev/ttyUSB0 -b 9600
```

### Arduino IDE

1. Open `arduino_bpm_display/arduino_bpm_display.ino`
2. Install required libraries via Library Manager:
   - Adafruit SSD1306
   - Adafruit GFX Library
   - Adafruit BusIO
3. Select Board: "Arduino Uno"
4. Select correct COM port
5. Upload

## Display Features

The Arduino display shows:

1. **Splash Screen** (2 seconds at startup)
2. **Waiting Screen** - Animated while waiting for ESP32 data
3. **BPM Screen** - Shows:
   - Large BPM value (centered)
   - "BPM" label
   - Confidence bar (if confidence data received)
   - Activity indicator (blinking dot)
   - Time since last update
   - Confidence percentage
4. **Timeout Screen** - Shows when connection is lost (5+ seconds without data)

## Troubleshooting

### No Display Output
- Check I2C connections (A4/A5)
- Verify display I2C address (most are 0x3C, some are 0x3D)
- Ensure display is powered (VCC/GND)

### No BPM Data Received
- Verify GND connection between ESP32 and Arduino
- Check ESP32 TX2 (GPIO17) → Arduino D2 connection
- Open Arduino Serial Monitor at 9600 baud to see debug output
- Verify ESP32 is running and detecting BPM

### Display Shows "Connection Lost"
- ESP32 may not be sending data (check ESP32 serial output)
- Wire disconnected
- Baud rate mismatch (both should be 9600)

### Garbled Data in Serial Monitor
- Baud rate mismatch
- Missing or poor ground connection
- Interference on signal lines (use shorter wires)

## Configuration Options

### ESP32 Side (`src/config.h`)

```cpp
#define ARDUINO_DISPLAY_TX_PIN 17    // GPIO17 (Serial2 TX)
#define ARDUINO_DISPLAY_RX_PIN 16    // GPIO16 (Serial2 RX)
#define ARDUINO_DISPLAY_BAUD 9600    // Baud rate
#define ARDUINO_DISPLAY_ENABLED 1    // Enable/disable (1/0)
```

### Arduino Side (`arduino_display_main.cpp`)

```cpp
#define ESP32_RX_PIN 2   // D2 receives from ESP32
#define ESP32_TX_PIN 3   // D3 sends to ESP32 (optional)
#define SCREEN_ADDRESS 0x3C  // OLED I2C address
#define TIMEOUT_MS 5000  // Connection timeout (ms)
```

## Power Considerations

| Component | Typical Current |
|-----------|-----------------|
| Arduino Uno | 40-50 mA |
| SSD1306 OLED | 10-20 mA |
| **Total** | ~60-70 mA |

Both can be powered via USB. If using external power, ensure adequate current capacity.
