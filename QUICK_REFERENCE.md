# ESP32 BPM Detector - Quick Reference

## 🎯 System at a Glance

**What it does:** Real-time BPM detection from audio input with wireless Android display

**Key specs:**
- BPM Range: 60-200 BPM
- Sample Rate: 25kHz
- FFT Size: 1024 points
- Latency: <500ms
- CPU Usage: ~55%

## 🏗️ Architecture Quick View

```
Audio Input → ESP32 → BPM Detection → WiFi API → Android App
     ↑           ↑           ↑            ↑           ↑
  MAX9814    ADC+FFT    Envelope+Beat   REST/JSON   Jetpack UI
```

## 📋 Quick Setup

### ESP32 Firmware
```bash
git clone <repo>
cd esp32-bpm-detector
# Edit config.h for WiFi
pio run -t upload
```

### Android App
```bash
cd android-app
./gradlew installDebug
# Open app, enter ESP32 IP, connect
```

## 🔧 Configuration Cheat Sheet

### Essential Settings (`config.h`)
```cpp
#define WIFI_SSID "YourNetwork"
#define WIFI_PASSWORD "YourPassword"
#define MICROPHONE_PIN 32          // ADC pin
#define SAMPLE_RATE 25000          // 25kHz optimal
#define MIN_BPM 60                 // Detection range
#define MAX_BPM 200
#define DETECTION_THRESHOLD 0.5    // Beat sensitivity
```

### Wiring (MAX9814 Microphone)
```
ESP32 GPIO32 ── MAX9814 OUT
ESP32 GND ───── MAX9814 GND
ESP32 5V ────── MAX9814 VCC
ESP32 GND ───── MAX9814 GAIN
```

## 🚀 API Endpoints

### Get BPM Data
```bash
curl http://192.168.1.100/api/bpm
```
```json
{
  "bpm": 128.5,
  "confidence": 0.87,
  "signal_level": 0.72,
  "status": "detecting",
  "timestamp": 1671545123456
}
```

### Health Check
```bash
curl http://192.168.1.100/api/health
```
```json
{"status": "ok", "uptime": 3600, "heap_free": 245760}
```

### Settings
```bash
curl http://192.168.1.100/api/settings
```
```json
{
  "min_bpm": 60, "max_bpm": 200,
  "sample_rate": 25000, "fft_size": 1024,
  "version": "1.0.0"
}
```

## 📊 Status Indicators

### BPM Values
- **120.5**: Detected BPM (1 decimal precision)
- **--**: No detection (dash displayed)

### Confidence Levels
- **90-100%**: Excellent detection
- **70-89%**: Good detection
- **30-69%**: Fair detection
- **0-29%**: Poor/unreliable

### Status Messages
- **"Detecting BPM"**: Active detection
- **"Low Audio Signal"**: Signal too weak
- **"Analyzing..."**: Calculating BPM
- **"Connection Error"**: Network issue

### Signal Levels
- **0.8-1.0**: Strong signal
- **0.5-0.8**: Good signal
- **0.2-0.5**: Weak signal
- **0.0-0.2**: Very weak/no signal

## 🧪 Testing Commands

### Run All C++ Tests (Cross-platform)

**Using Makefile (Recommended):**
```bash
make test          # Build and run all tests
make clean         # Clean build artifacts
```

**Using Python script:**
```bash
python3 run_tests.py
# or
python run_tests.py
```

**Using shell script (Linux/macOS/Git Bash):**
```bash
chmod +x run_tests.sh
./run_tests.sh
```

**Manual compilation:**
```bash
# Compile and run comprehensive tests
g++ -std=c++17 -I. comprehensive_tests.cpp -o comprehensive_tests -lm
./comprehensive_tests

# Run final validation
g++ -std=c++17 -I. final_test.cpp -o final_test -lm
./final_test

# Run simple validation
g++ -std=c++17 -I. simple_validation.cpp -o simple_validation -lm
./simple_validation
```

### Android Tests
```bash
cd android-app
./gradlew test                    # Unit tests
./gradlew connectedAndroidTest   # Integration tests
```

## 🔍 Debugging Checklist

### No BPM Detection
- [ ] Microphone connected correctly?
- [ ] Audio source playing and audible?
- [ ] Signal level > 0.2 in serial output?
- [ ] BPM within 60-200 range?

### WiFi Issues
- [ ] ESP32 shows "WiFi Connected" in serial?
- [ ] Same network as Android device?
- [ ] IP address correct in Android app?
- [ ] Firewall blocking port 80?

### Android App Problems
- [ ] API level 24+ (Android 7.0+) ?
- [ ] Internet permission granted?
- [ ] App has location permission (for WiFi)?

## 📈 Performance Benchmarks

### Expected Performance
| Metric | Value | Status |
|--------|-------|--------|
| BPM Accuracy | ±2 BPM | Target |
| Detection Latency | <500ms | Target |
| API Response | <200ms | Target |
| CPU Usage | <70% | Target |
| Memory Usage | <100KB | Target |

### Real-World Results
| Scenario | BPM Detected | Confidence | Notes |
|----------|--------------|------------|-------|
| Steady 120 BPM beat | 120.2 | 91% | Excellent |
| Live drums | 145.8 | 78% | Good |
| Complex music | 132.5 | 65% | Fair |
| Low volume | 0.0 | 0% | Low signal |

## 🛠️ Common Fixes

### Quick Fixes
```cpp
// Increase sensitivity (config.h)
#define DETECTION_THRESHOLD 0.3  // Lower = more sensitive

// Adjust BPM range
#define MIN_BPM 40   // Lower minimum
#define MAX_BPM 250  // Higher maximum

// Change sample rate
#define SAMPLE_RATE 44100  // Higher quality
```

### Android App Fixes
```kotlin
// Change polling interval (BPMService.kt)
private const val POLLING_INTERVAL_MS = 250L  // Faster updates

// Change default IP
private const val DEFAULT_ESP32_IP = "192.168.0.100"
```

## 📱 Android App Features

### Main Screen
- **Large BPM Display**: Current detected BPM
- **Confidence Bar**: Visual confidence indicator
- **Status Text**: Current detection status
- **Connection Indicator**: WiFi connection status

### Settings Screen
- **IP Address**: ESP32 server IP
- **Polling Interval**: API poll frequency (100-2000ms)
- **Connect/Disconnect**: Manual connection control

### Background Service
- **Auto-reconnect**: Handles network interruptions
- **Battery optimized**: Efficient polling
- **Error handling**: Graceful failure recovery

## 🔄 Update Process

### Firmware Updates
```bash
# Pull latest changes
git pull

# Edit config if needed
code config.h

# Build and upload
pio run -t upload
```

### Android App Updates
```bash
cd android-app
git pull
./gradlew installDebug
```

## 🎵 Audio Source Tips

### Best Results
- **Clear beat patterns**: Electronic music, metronomes
- **Consistent tempo**: Avoid tempo changes
- **Good signal level**: Keep microphone close to source
- **Bass frequencies**: Kick drum, bass guitar work best

### Challenging Sources
- **Complex arrangements**: Orchestral music, vocals
- **Irregular rhythms**: Jazz, progressive rock
- **Low frequencies**: May need amplifier
- **Background noise**: Can interfere with detection

## 📞 Support Resources

### Documentation
- `README.md`: Main project documentation
- `IMPLEMENTATION_GUIDE.md`: Technical deep dive
- `DEMO_GUIDE.md`: Step-by-step setup
- `config.h`: All configuration options

### Debug Output
```cpp
// Enable debug output (config.h)
#define DEBUG_SERIAL 1
#define DEBUG_FFT 0
#define DEBUG_BEATS 0
#define DEBUG_MEMORY 1
```

### Log Analysis
```
[BPM] 128.5 BPM | Confidence: 0.87 | Level: 0.72 | Status: detecting
     ↑ BPM value    ↑ Reliability    ↑ Signal      ↑ State
                    (0.0-1.0)       (0.0-1.0)     (text)
```

## 🚀 Advanced Configuration

### Performance Tuning
```cpp
// Higher quality (more CPU)
#define SAMPLE_RATE 44100
#define FFT_SIZE 2048

// Lower latency (faster response)
#define API_POLL_INTERVAL 50

// Battery saving (Android)
#define POLLING_INTERVAL_MS 1000
```

### Optional Features
```cpp
// Enable OLED display
#define USE_OLED_DISPLAY 1
#define OLED_SDA_PIN 21
#define OLED_SCL_PIN 22

// Enable MQTT publishing
#define ENABLE_MQTT 1
#define MQTT_BROKER "192.168.1.10"
```

This quick reference covers the essential information needed to operate and troubleshoot the ESP32 BPM detector system effectively.
