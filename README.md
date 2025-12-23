# ESP32 BPM Detector

A real-time BPM (Beats Per Minute) detection system using ESP32 microcontroller as backend server with Android app for wireless BPM display.

## Overview

This project captures audio signals from a microphone (analog or digital MIDI), performs real-time BPM detection using FFT or envelope-based analysis, and exposes the BPM value via a REST API over WiFi. An Android application (or other client devices) can connect wirelessly to display the live BPM value.

**Key Features:**
- ✅ Real-time BPM detection from audio input (60-200 BPM range)
- ✅ WiFi API server (`GET /api/bpm`) for wireless access
- ✅ Optional numeric display support (OLED or 7-segment)
- ✅ Adaptive threshold detection for various audio levels
- ✅ Android app client for visualization
- ✅ MQTT support (optional)
- ✅ MIDI clock output (optional)

## Hardware Requirements

### Core Components
- **Microcontroller**: ESP32-WROOM-32 (with built-in WiFi)
- **Microphone**: MAX9814 (recommended) or I2S MEMS microphone
- **Power Supply**: 5V USB or 3.3V (with voltage regulator for microphone)
- **WiFi Network**: 2.4 GHz WiFi router

### Optional Components
- **Display**: SSD1306 OLED (I2C) or TM1637 7-segment display
- **MIDI Input**: DIN connector with optoisolator (for MIDI clock sync)
- **USB Cable**: For programming and power

## Quick Start

### 1. Firmware Setup

#### Prerequisites
- PlatformIO CLI or VS Code with PlatformIO extension
- Arduino IDE (optional alternative)

#### Installation
```bash
# Clone the repository
git clone https://github.com/sparesparrow/esp32-bpm-detector.git
cd esp32-bpm-detector/firmware

# Build and upload
pio run -t upload

# Monitor serial output
pio device monitor
```

#### Configuration
Edit `include/config.h`:
```cpp
#define WIFI_SSID "Your_WiFi_SSID"
#define WIFI_PASSWORD "Your_WiFi_Password"
#define MICROPHONE_PIN 32          // ADC pin connected to microphone
#define MIN_BPM 60
#define MAX_BPM 200
#define SAMPLE_RATE 25000
#define FFT_SIZE 1024
```

### 2. Android App Setup

#### Prerequisites
- Android Studio (2023.1+)
- Kotlin 1.8+
- Android SDK level 24+

#### Installation
```bash
cd android-app
./gradlew build
./gradlew installDebug
```

#### App Configuration
1. Open the app on your Android device
2. Go to **Settings** tab
3. Enter ESP32 IP address (e.g., `192.168.1.100`)
4. Tap **Connect**

## API Documentation

### GET /api/bpm

Returns current BPM detection data.

**Response:**
```json
{
  "bpm": 128.5,
  "confidence": 0.87,
  "signal_level": 0.72,
  "status": "detecting",
  "timestamp": 1671545123456
}
```

**Fields:**
- `bpm` (float): Detected beats per minute
- `confidence` (float): 0.0-1.0 confidence level of detection
- `signal_level` (float): 0.0-1.0 normalized audio signal strength
- `status` (string): `"detecting"` | `"low_signal"` | `"error"`
- `timestamp` (long): Unix timestamp in milliseconds

### GET /api/settings

Returns firmware configuration.

**Response:**
```json
{
  "min_bpm": 60,
  "max_bpm": 200,
  "sample_rate": 25000,
  "fft_size": 1024,
  "version": "1.0.0"
}
```

## Architecture

### Firmware (ESP32)
1. **Audio Input Module** (`audio_input.*`): Reads analog samples from ADC
2. **BPM Detector Module** (`bpm_detector.*`): Performs FFT/envelope detection
3. **WiFi Server** (`wifi_server.*`): Exposes REST API
4. **Display Handler** (`display_handler.*`): Optional numeric display output
5. **Main Loop**: Coordinates sampling, detection, and API serving

### Android App
1. **MainActivity**: Hosts fragment navigation
2. **BPMDisplayFragment**: Shows live BPM with gauges/charts
3. **SettingsFragment**: WiFi connection configuration
4. **BPMService**: Background service for periodic API polling
5. **APIClient**: Retrofit HTTP client for ESP32 communication

## Wiring Diagram

```
ESP32 Pinout (relevant pins):
┌─────────────┐
│   ESP32     │
├─────────────┤
│ GPIO32 ─────┼─── Microphone OUT (MAX9814)
│ GPIO21 ─────┼─── OLED SDA
│ GPIO22 ─────┼─── OLED SCL
│ GND  ───────┼─── GND (Microphone, OLED)
│ 3.3V ───────┼─── 3.3V (OLED, Optional microphone)
│ 5V   ───────┼─── 5V (MAX9814)
└─────────────┘

MAX9814 Microphone:
- VCC  → 5V
- GND  → GND
- OUT  → ESP32 GPIO32 (ADC1_CH4)
- GAIN (optional) → GND (for AGC off)

SSD1306 OLED (optional):
- VCC  → 3.3V
- GND  → GND
- SDA  → ESP32 GPIO21
- SCL  → ESP32 GPIO22
```

## Building & Deploying

### Option 1: PlatformIO (Recommended)
```bash
cd firmware
pio run              # Build
pio run -t upload    # Upload to ESP32
pio device monitor   # View serial output
```

### Option 2: Arduino IDE
1. Install ESP32 board support
2. Open `firmware/src/main.cpp` in Arduino IDE
3. Select board: "ESP32 Dev Module"
4. Set upload speed: 921600
5. Click Upload

## Testing

### C++ Firmware Tests (Cross-platform)

**Using Makefile (Recommended):**
```bash
make test          # Build and run all tests
make clean         # Clean build artifacts
```

**Using Python script:**
```bash
python3 run_tests.py
```

**Using shell script (Linux/macOS/Git Bash):**
```bash
chmod +x run_tests.sh
./run_tests.sh
```

**Manual compilation:**
```bash
g++ -std=c++17 -I. comprehensive_tests.cpp -o comprehensive_tests -lm
./comprehensive_tests
```

### ESP32 Firmware Testing
```bash
# Build test firmware with serial debugging
pio run -e esp32dev --verbose

# Monitor BPM output at various volumes
# Play music at different BPMs (80, 120, 140 BPM)
```

### Android App Testing
```bash
cd android-app
./gradlew test                    # Unit tests (Linux/macOS)
.\gradlew.bat test               # Unit tests (Windows)
./gradlew connectedAndroidTest    # Integration tests (Linux/macOS)
.\gradlew.bat connectedAndroidTest  # Integration tests (Windows)
```

**Manual testing:**
1. Connect Android device to same WiFi as ESP32
2. Open app and enter ESP32 IP
3. Verify BPM updates in real-time
4. Test reconnection after WiFi dropout

## Troubleshooting

### No BPM Detection
- Verify microphone is connected correctly
- Check audio signal level (should be 0.5-2.5V for MAX9814)
- Try adjusting `DETECTION_THRESHOLD` in config.h

### WiFi Connection Fails
- Verify ESP32 and Android device are on same network
- Check WiFi credentials in config.h
- Try restarting ESP32

### Low Confidence Values
- Audio signal too quiet or loud (adjust microphone gain)
- Try different audio source or frequency range
- Increase FFT_SIZE for better frequency resolution

### Android App Crashes
- Ensure minimum API level 24
- Grant internet permission in app settings
- Check logcat for detailed error messages

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for more solutions.

## Advanced Features

### MIDI Clock Support
Enable in config.h and connect MIDI input to ESP32 GPIO for MIDI-based BPM sync.

### MQTT Pub/Sub
Publish detected BPM to MQTT broker for integration with home automation.

### Multi-Source Sync
Connect multiple microphones or MIDI inputs for synchronized multi-room BPM detection.

### DMX Integration
Synchronize stage lighting (DMX) with detected BPM.

## Performance

- **BPM Detection Latency**: < 500ms
- **API Response Time**: < 200ms
- **CPU Usage**: ~30-40% at 100 FPS FFT
- **Memory**: ~50KB for buffers + code
- **WiFi Throughput**: ~1-2 requests/second recommended

## Contributing

Contributions welcome! Please follow the existing code style and add tests for new features.

## License

MIT License - See [LICENSE](LICENSE) file

## References

- [ESP32 Official Documentation](https://docs.espressif.com/projects/esp-idf/)
- [ArduinoFFT Library](https://github.com/kosme/arduinoFFT)
- [ESPAsyncWebServer](https://github.com/me-no-dev/ESPAsyncWebServer)
- [Kotlin Coroutines](https://kotlinlang.org/docs/coroutines-overview.html)
- [Android Networking Best Practices](https://developer.android.com/training/volley)

## Support

For issues, questions, or suggestions:
- GitHub Issues: [esp32-bpm-detector/issues](https://github.com/sparesparrow/esp32-bpm-detector/issues)
- Documentation: See `/docs` folder

---

**Version**: 1.0.0  
**Last Updated**: December 2025  
**Author**: sparesparrow  
**Status**: Active Development
