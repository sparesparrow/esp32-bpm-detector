# ESP32 BPM Detector - Complete Integration Guide

This guide covers the complete integration of the ESP32 firmware and Android app for real-time BPM detection and wireless display.

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    WiFi Network (LAN)                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐              ┌────────────────────┐  │
│  │   ESP32 Server   │              │   Android Phone 1  │  │
│  ├──────────────────┤              ├────────────────────┤  │
│  │ • WiFi Access    │◄─────────────►│ • Polling Service  │  │
│  │   Point 192.x.x.x│   HTTP API    │ • BPM Display      │  │
│  │ • Audio Input    │   /api/bpm    │ • Settings UI      │  │
│  │   (GPIO32)       │               │                    │  │
│  │ • BPM Detection  │               │                    │  │
│  │   (FFT/ADC)      │               │ ┌────────────────┐│  │
│  │ • Display Output │               │ │ BPM: 128.5 BPM ││  │
│  │   (OLED/7-seg)   │               │ │ Conf: 87%      ││  │
│  └──────────────────┘               │ └────────────────┘│  │
│         ▲                           └────────────────────┘  │
│         │                           ┌────────────────────┐   │
│    Audio Input                     │   Android Phone 2  │   │
│   from DJ Mixer                    │   (Optional)       │   │
│    (Microphone)                    │                    │   │
│                                    │ Same BPM display   │   │
│                                    └────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Hardware Requirements

### Core Components
- **ESP32-WROOM-32** development board
- **MAX9814** microphone amplifier module
- **Android device** (API 24+, Android 7.0+)
- **WiFi router** (2.4 GHz support)

### Optional Components
- **SSD1306 OLED display** (128x64, I2C)
- **USB power supply** (5V for ESP32 + microphone)

### Wiring Diagram

```
ESP32          MAX9814         OLED (Optional)
──────         ───────         ─────────────
3.3V  ──────── VCC             VCC  ─────── 3.3V
GND   ──────── GND             GND  ─────── GND
GPIO32 ────── OUT              SDA  ─────── GPIO21
                              SCL  ─────── GPIO22
```

## Software Setup

### 1. ESP32 Firmware

#### PlatformIO Setup
```bash
# Install PlatformIO (if not already installed)
# Follow: https://platformio.org/installation

# Navigate to firmware directory
cd esp32-bpm-detector

# Configure WiFi in config.h
#define WIFI_SSID "Your_WiFi_Name"
#define WIFI_PASSWORD "Your_WiFi_Password"

# Build and upload
pio run -t upload

# Monitor serial output
pio device monitor
```

#### Expected Serial Output
```
[System] ESP32 BPM Detector v1.0.0
[WiFi] Connected! IP address: 192.168.1.100
[BPM] Initializing BPM detector...
[System] Initialization complete!
[BPM] 128.5 BPM | Confidence: 0.87 | Level: 0.72 | Status: detecting
```

### 2. Android App Setup

#### Android Studio Setup
```bash
# Open Android Studio
# Select "Open an existing project"
# Navigate to: esp32-bpm-detector/android-app

# Configure ESP32 IP in app settings
# Build APK or run on device/emulator
```

#### App Configuration
1. **Open the app** on your Android device
2. **Navigate to Settings** (bottom tab)
3. **Enter ESP32 IP**: `192.168.1.100` (or your ESP32's IP)
4. **Test Connection** to verify connectivity
5. **Save Settings** and return to BPM display

## API Communication

### REST Endpoints

#### GET /api/bpm
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

**Status Values:**
- `"detecting"` - Actively detecting BPM
- `"low_signal"` - Audio signal too weak
- `"low_confidence"` - Analyzing but uncertain
- `"error"` - Detection error occurred

#### GET /api/settings
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

#### GET /api/health
Health check with system information.

**Response:**
```json
{
  "status": "ok",
  "uptime": 3600,
  "heap_free": 245760
}
```

### Connection Flow

```
Android App          ESP32 Firmware
     │                     │
     ├─ Start Service ───► │
     │                     │
     ├─ Bind Service ─────►│
     │                     │
     ├─ GET /api/health ──►│
     │ ◄── 200 OK ──────────┤
     │                     │
     ├─ GET /api/bpm ─────►│ (every 500ms)
     │ ◄── BPM Data ───────┤
     │                     │
     ├─ Update UI ────────►│ (display BPM)
     │                     │
```

## Testing & Verification

### ESP32 Firmware Testing

#### 1. WiFi Connection
```bash
# Monitor serial output
pio device monitor

# Expected: "WiFi Connected! IP address: 192.168.1.xxx"
```

#### 2. HTTP API Testing
```bash
# Test health endpoint
curl http://192.168.1.100/api/health

# Test BPM endpoint
curl http://192.168.1.100/api/bpm

# Test settings endpoint
curl http://192.168.1.100/api/settings
```

#### 3. Audio Input Testing
- Connect microphone to GPIO32
- Play music at known BPM (120 BPM recommended)
- Check serial output for BPM detection
- Verify confidence values increase with stronger signals

### Android App Testing

#### 1. Connection Testing
- Enter ESP32 IP in settings
- Use "Test Connection" button
- Verify "Connection successful!" message

#### 2. BPM Display Testing
- Start monitoring from BPM display screen
- Play audio through microphone
- Verify BPM values update in real-time
- Check confidence and signal indicators

#### 3. Multi-Device Testing
- Connect multiple Android devices
- Verify same BPM displayed on all devices
- Test connection stability with WiFi changes

## Performance Optimization

### ESP32 Firmware

#### Memory Optimization
- **FFT Buffer**: ~8KB for 1024-point FFT
- **Sample Buffer**: ~8KB for audio samples
- **Beat History**: ~128 bytes for 32 recent beats
- **Total**: ~16KB heap usage (well within ESP32 limits)

#### CPU Optimization
- **Sample Rate**: 25kHz (balance between accuracy and performance)
- **FFT Size**: 1024 points (good frequency resolution)
- **Processing Time**: ~6ms per detection cycle
- **Real-time**: 500ms polling interval allows 200ms processing budget

#### Power Optimization
- **Deep Sleep**: Possible for battery-powered operation
- **WiFi Power**: Can be optimized for low-power modes
- **ADC**: 12-bit resolution provides good accuracy vs power balance

### Android App

#### Network Optimization
- **Retry Logic**: 3 attempts with exponential backoff
- **Timeout**: 5-second connection timeout
- **Connection Pooling**: Retrofit handles connection reuse
- **Background Service**: Efficient polling without UI blocking

#### UI Performance
- **Jetpack Compose**: Optimized rendering
- **StateFlow**: Efficient reactive updates
- **ViewModel**: Survives configuration changes
- **60 FPS**: Smooth animations and updates

## Troubleshooting

### ESP32 Issues

#### WiFi Connection Problems
```bash
# Check serial output
pio device monitor

# Verify WiFi credentials in config.h
# Try different WiFi channels (ESP32 prefers 2.4GHz)
# Check router settings for device isolation
```

#### BPM Detection Issues
```bash
# Verify microphone connection
# Check MAX9814 power (needs 5V)
# Adjust audio gain potentiometer
# Test with different audio sources
# Check FFT debug output (enable DEBUG_FFT)
```

#### Memory Issues
```bash
# Monitor heap usage
pio device monitor

# Check for memory leaks
# Reduce FFT_SIZE if needed (512 instead of 1024)
# Monitor ESP.getFreeHeap() in serial output
```

### Android Issues

#### Connection Problems
- **IP Address**: Verify ESP32 IP in Android settings
- **Network**: Ensure devices on same WiFi network
- **Firewall**: Some networks block device communication
- **ESP32**: Check ESP32 is running and connected

#### App Performance
- **Memory**: Check device has sufficient RAM
- **Permissions**: Grant internet permission
- **Background**: Ensure app can run background services
- **Battery**: Some devices limit background network activity

## Advanced Configuration

### ESP32 Firmware Tuning

#### Audio Processing Parameters (`config.h`)
```cpp
// Adjust for different audio sources
#define SAMPLE_RATE 25000      // Higher = better resolution, more CPU
#define FFT_SIZE 1024          // Larger = better frequency resolution
#define MIN_BPM 60            // Adjust for music genre
#define MAX_BPM 200           // Upper BPM limit
#define DETECTION_THRESHOLD 0.5 // Lower = more sensitive, more false positives
```

#### WiFi Optimization
```cpp
// For better stability
#define WIFI_POWER WIFI_POWER_19_5dBm  // Maximum power
#define WIFI_MODE WIFI_MODE_STA       // Station mode only
```

### Android App Tuning

#### Network Configuration
```kotlin
// In BPMApiClient
const val DEFAULT_TIMEOUT_MS = 3000L     // Faster for real-time
const val DEFAULT_RETRY_ATTEMPTS = 2     // Fewer retries
```

#### UI Customization
```kotlin
// In BPMViewModel
private val _pollingInterval = MutableStateFlow(250L)  // Faster updates
```

## Future Enhancements

### ESP32 Firmware
- **MQTT Support**: Publish BPM data to MQTT broker
- **MIDI Clock Output**: Generate MIDI clock signals
- **Multiple Microphones**: Support for multiple audio inputs
- **OTA Updates**: Over-the-air firmware updates

### Android App
- **Charts & Graphs**: Historical BPM visualization
- **Multiple ESP32s**: Support multiple BPM detectors
- **Notifications**: BPM alerts and notifications
- **Themes**: Customizable color schemes

### System-Wide
- **Web Dashboard**: Browser-based monitoring interface
- **Data Logging**: Save BPM history to database
- **Mobile App**: iOS version of the Android app

## Support & Resources

### Documentation
- **ESP32 Firmware**: Complete firmware guide
- **Android App**: App architecture and usage
- **API Documentation**: REST API specification
- **Hardware Setup**: Wiring diagrams and component guides

### Community
- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Q&A and general discussion
- **Wiki**: Extended documentation and tutorials

### Development
- **Contributing Guide**: How to contribute to the project
- **Code Standards**: Coding guidelines and best practices
- **Testing Guide**: Comprehensive testing procedures

---

**Ready to start?** Follow the setup instructions above and you'll have a working real-time BPM detection system in minutes! 🎵
