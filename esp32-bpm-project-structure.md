# ESP32 BPM Detector - Project Structure & Implementation Plan

## Project Overview
Real-time BPM detection from audio signals using ESP32/Arduino as backend server with WiFi API, displaying BPM on Android app or numeric display.

---

## Directory Structure

```
esp32-bpm-detector/
├── firmware/
│   ├── platformio.ini
│   ├── src/
│   │   ├── main.cpp
│   │   ├── bpm_detector.h
│   │   ├── bpm_detector.cpp
│   │   ├── wifi_server.h
│   │   ├── wifi_server.cpp
│   │   ├── audio_input.h
│   │   ├── audio_input.cpp
│   │   ├── display_handler.h
│   │   └── display_handler.cpp
│   ├── include/
│   │   └── config.h
│   └── lib/
│       └── (third-party libraries)
│
├── android-app/
│   ├── app/
│   │   ├── src/
│   │   │   └── main/
│   │   │       ├── java/com/sparesparrow/bpmdetector/
│   │   │       │   ├── MainActivity.kt
│   │   │       │   ├── BPMService.kt
│   │   │       │   ├── models/
│   │   │       │   │   └── BPMData.kt
│   │   │       │   ├── ui/
│   │   │       │   │   ├── BPMDisplayFragment.kt
│   │   │       │   │   └── SettingsFragment.kt
│   │   │       │   └── network/
│   │   │       │       └── APIClient.kt
│   │   │       └── res/
│   │   │           ├── layout/
│   │   │           │   ├── activity_main.xml
│   │   │           │   └── fragment_bpm_display.xml
│   │   │           ├── values/
│   │   │           │   └── strings.xml
│   │   │           └── drawable/
│   │   └── AndroidManifest.xml
│   ├── build.gradle
│   └── settings.gradle
│
├── docs/
│   ├── HARDWARE_SETUP.md
│   ├── FIRMWARE_GUIDE.md
│   ├── ANDROID_APP_GUIDE.md
│   ├── API_DOCUMENTATION.md
│   └── TROUBLESHOOTING.md
│
├── README.md
├── LICENSE (MIT)
└── .gitignore
```

---

## Phase 1: Firmware Development (ESP32)

### 1.1 Hardware Components
- **Microcontroller**: ESP32-WROOM-32
- **Microphone Module**: MAX9814 (or I2S MEMS microphone)
- **Display** (optional): SSD1306 OLED (128x64) or 7-segment display (TM1637)
- **Connections**: 
  - Microphone → ESP32 ADC pin (GPIO 32 or 35)
  - OLED → I2C (GPIO 21 SDA, GPIO 22 SCL)
  - 7-segment → GPIO pins for digital output

### 1.2 Key Libraries
- `arduinoFFT` - FFT for frequency analysis
- `ESPAsyncWebServer` - HTTP API server
- `WiFi.h` - WiFi connectivity
- `Adafruit_SSD1306` / `TM1637Display` - Display drivers

### 1.3 Core Features
- **Audio input reading** (ADC with 25 kHz sampling rate)
- **Beat detection** using FFT or envelope detection
- **BPM calculation** (adaptive threshold, 60-200 BPM range)
- **WiFi API server** (REST endpoint: `/api/bpm`)
- **Optional display output** (OLED or 7-segment)
- **Error handling & robustness**

---

## Phase 2: Android App Development

### 2.1 Architecture
- **MVVM** pattern with LiveData
- **Kotlin Coroutines** for async networking
- **Retrofit** or **OkHttp** for HTTP requests
- **Jetpack Compose** (recommended) or XML layouts

### 2.2 Key Features
- **Settings screen**: Enter ESP32 server IP/hostname
- **BPM display**: Large numeric display with visual indicator (bar, gauge)
- **Auto-refresh**: Periodic API polling every 500-1000ms
- **Connection status**: Show WiFi connection state
- **Error handling**: Display when connection fails

### 2.3 Permissions Required
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.CHANGE_NETWORK_STATE" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

---

## Phase 3: API Specification

### Endpoint: GET /api/bpm
**Response (JSON)**:
```json
{
  "bpm": 128,
  "confidence": 0.85,
  "timestamp": 1671545123456,
  "status": "detecting",
  "signal_level": 0.72
}
```

**Status values**: `"detecting"`, `"low_signal"`, `"error"`

### Endpoint: GET /api/settings
**Response**:
```json
{
  "min_bpm": 60,
  "max_bpm": 200,
  "sample_rate": 25000,
  "fft_size": 1024,
  "version": "1.0.0"
}
```

### Endpoint: POST /api/settings (optional)
Allow configuration adjustments from client.

---

## Implementation Roadmap

### Week 1: Firmware Foundation
- [ ] Set up PlatformIO project
- [ ] Implement audio input reading (ADC)
- [ ] Implement basic FFT-based beat detection
- [ ] Implement WiFi connection & basic HTTP server
- [ ] Test with serial monitor output

### Week 2: Firmware Polish & Display
- [ ] Integrate numeric display (OLED or 7-segment)
- [ ] Implement `/api/bpm` endpoint
- [ ] Add error handling & connection recovery
- [ ] Optimize FFT parameters for different audio sources
- [ ] Test with real DJ audio (various BPM ranges)

### Week 3: Android App Development
- [ ] Set up Android project structure
- [ ] Create UI layout (BPM display screen)
- [ ] Implement network client (APIClient)
- [ ] Implement settings screen (server IP input)
- [ ] Connect UI to API calls

### Week 4: Integration & Testing
- [ ] Full system integration testing
- [ ] Test WiFi stability & latency
- [ ] Multi-device testing
- [ ] Documentation & README update
- [ ] Optional: Extend with MIDI clock support

---

## Configuration Files

### platformio.ini
```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
lib_deps =
    https://github.com/kosme/arduinoFFT.git
    https://github.com/me-no-dev/ESPAsyncWebServer.git
    https://github.com/me-no-dev/AsyncTCP.git
    adafruit/Adafruit SSD1306
monitor_speed = 115200
build_flags =
    -D CORE_DEBUG_LEVEL=2
```

### build.gradle (Android)
```gradle
dependencies {
    // Networking
    implementation 'com.squareup.retrofit2:retrofit:2.10.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.10.0'
    
    // Coroutines
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1'
    
    // Jetpack
    implementation 'androidx.lifecycle:lifecycle-viewmodel-ktx:2.6.1'
    implementation 'androidx.lifecycle:lifecycle-runtime-ktx:2.6.1'
    
    // Compose (optional)
    implementation 'androidx.compose.ui:ui:1.5.4'
    implementation 'androidx.compose.material3:material3:1.1.1'
}
```

---

## Testing Checklist

- [ ] **Firmware**: Audio input reading at various levels
- [ ] **Firmware**: FFT processing & beat detection accuracy
- [ ] **Firmware**: WiFi connection stability
- [ ] **Firmware**: Display output (numeric values)
- [ ] **Android**: App connects to ESP32 via IP
- [ ] **Android**: BPM display updates in real-time
- [ ] **Android**: Reconnection after WiFi loss
- [ ] **Integration**: Multiple Android clients receive same BPM
- [ ] **Integration**: Low latency (< 1 second)
- [ ] **Edge cases**: Very loud/quiet audio sources
- [ ] **Edge cases**: Different music genres (60-180+ BPM)

---

## Optional Enhancements

1. **MQTT Support**: Use MQTT broker for multi-device sync
2. **MIDI Clock Output**: Generate MIDI clock from detected BPM
3. **Web Dashboard**: Browser-based monitoring interface
4. **Bluetooth**: BLE support for Android devices without WiFi
5. **Energy Optimization**: Sleep modes for low-power operation
6. **Data Logging**: Save BPM history for analysis
7. **Multiple Audio Sources**: Support multiple microphones/MIDI inputs
8. **DMX Integration**: Send DMX commands synchronized with BPM

---

## References & Resources

- **ESP32 Audio**: https://docs.espressif.com/projects/esp-idf/
- **ArduinoFFT**: https://github.com/kosme/arduinoFFT
- **ESPAsyncWebServer**: https://github.com/me-no-dev/ESPAsyncWebServer
- **Android Networking**: https://developer.android.com/training/volley
- **Kotlin Coroutines**: https://kotlinlang.org/docs/coroutines-overview.html

---

## Key Design Decisions

1. **FFT vs Envelope Detection**: FFT provides better frequency resolution; envelope detection is lighter (choose based on ESP32 performance)
2. **BPM Range**: 60-200 BPM covers most DJ/music scenarios
3. **Polling vs WebSocket**: Polling simpler for initial implementation; WebSocket for real-time streaming later
4. **Display Types**: OLED for best visual feedback; 7-segment for minimal power consumption
5. **Android Target**: Min API 24 (Android 7.0) for broad compatibility

---

## Success Metrics

- ✅ BPM detection accuracy ±2% for 60-180 BPM range
- ✅ API response time < 500ms
- ✅ WiFi reconnection < 5 seconds
- ✅ Android app smooth at 60 FPS display refresh
- ✅ Display shows BPM update every 100-200ms
