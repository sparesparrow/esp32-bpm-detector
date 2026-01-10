# Android-ESP32 Connection Testing Guide

## ✅ All Fixes Applied and Verified

### Configuration Status
- ✅ **SSID Match**: `ESP32-BPM-Detector` (Android ↔ ESP32)
- ✅ **Password Match**: `bpm12345` (Android ↔ ESP32)
- ✅ **IP Address Match**: `192.168.4.1` (Android ↔ ESP32)
- ✅ **Authentication**: WPA_PSK (Android ↔ ESP32)
- ✅ **Android App Built**: APK ready at `android-app/app/build/outputs/apk/debug/app-debug.apk`

## Quick Start Testing

### When Android Device is Connected:

```bash
# 1. Install APK
adb install -r android-app/app/build/outputs/apk/debug/app-debug.apk

# 2. Run automated test script
./scripts/test_connection.sh

# 3. Monitor logs manually
adb logcat | grep -E "(BPM|WiFi|ESP32|Connection)"
```

## Manual Testing Steps

### Prerequisites Checklist
- [ ] ESP32 device powered on
- [ ] ESP32 firmware running (check serial: `pio device monitor`)
- [ ] ESP32 WiFi AP active (SSID: "ESP32-BPM-Detector")
- [ ] Android device connected via USB
- [ ] USB debugging enabled on Android
- [ ] Location permissions will be requested by app

### Test 1: Install and Launch App

```bash
# Install APK
adb install -r android-app/app/build/outputs/apk/debug/app-debug.apk

# Launch app
adb shell am start -n com.sparesparrow.bpmdetector/.ui.MainActivity

# Monitor logs
adb logcat | grep -E "(BPM|WiFi|ESP32)"
```

**Expected**: App launches, requests location permissions, starts auto-discovery

### Test 2: WiFi Discovery

**What to look for in logs:**
```
Starting WiFi scan for ESP32 network
WiFi scan completed. ESP32 network found: true
Found network: ESP32-BPM-Detector
```

**Verification:**
```bash
adb logcat | grep -i "ESP32-BPM-Detector"
```

**Expected**: App finds "ESP32-BPM-Detector" network in scan results

### Test 3: WiFi Connection

**What to look for in logs:**
```
ESP32 WiFi network found, attempting connection
WiFi connection attempt - disconnect: true, enable: true, reconnect: true
Successfully connected to ESP32 WiFi network
```

**Verification:**
```bash
# Check WiFi connection
adb shell "dumpsys wifi | grep -A 10 'mWifiInfo'"

# Or check in Android Settings > WiFi
```

**Expected**: Android device connects to "ESP32-BPM-Detector network

### Test 4: HTTP Communication

**What to look for in logs:**
```
Auto-discovery successful - device found at 192.168.4.1
Connection status: CONNECTED
```

**Verification:**
```bash
# Test from computer (if connected to ESP32 WiFi)
curl http://192.168.4.1/api/health
curl http://192.168.4.1/api/bpm
```

**Expected**: HTTP requests succeed, BPM data received

## Troubleshooting

### Issue: "No devices/emulators found"
**Solution**: 
- Connect Android device via USB
- Enable USB debugging: Settings > Developer Options > USB Debugging
- Accept USB debugging prompt on device
- Verify: `adb devices`

### Issue: "WiFi network not found"
**Check**:
1. ESP32 serial output shows: "WiFi Access Point Started"
2. SSID exactly matches: "ESP32-BPM-Detector" (case-sensitive)
3. Android location permissions granted
4. WiFi scanning enabled on Android

**Debug**:
```bash
# Check Android WiFi scan results
adb logcat | grep -i "scan.*result"

# Check ESP32 serial output
pio device monitor --port /dev/ttyUSB0
```

### Issue: "Connection failed"
**Check**:
1. Password matches: "bpm12345"
2. Authentication method: WPA_PSK
3. Android WiFi logs: `adb logcat | grep WifiManager`

**Debug**:
```bash
# Check WiFi connection attempt
adb logcat | grep -E "(connect|WiFi|WPA)"

# Check Android WiFi state
adb shell "dumpsys wifi"
```

### Issue: "HTTP requests fail"
**Check**:
1. IP address: 192.168.4.1
2. ESP32 is responding: `curl http://192.168.4.1/api/health`
3. Android is connected to ESP32 WiFi
4. ESP32 HTTP server is running

**Debug**:
```bash
# Test connectivity from Android device
adb shell "ping -c 3 192.168.4.1"

# Check ESP32 HTTP server logs (serial output)
```

## Verification Scripts

### Verify Configuration
```bash
./scripts/verify_esp32_config.sh
```

### Test Connection (when device connected)
```bash
./scripts/test_connection.sh
```

## Expected Log Flow

When everything works correctly, you should see this sequence in logs:

```
1. App Launch
   → "BPMService created"
   → "Starting auto-discovery for ESP32 device"

2. WiFi Discovery
   → "Starting WiFi scan for ESP32 network"
   → "WiFi scan completed. Found X networks"
   → "ESP32 WiFi network found: true"

3. WiFi Connection
   → "ESP32 WiFi network found, attempting connection"
   → "WiFi connection attempt - disconnect: true, enable: true, reconnect: true"
   → "Successfully connected to ESP32 WiFi network"

4. HTTP Connection
   → "Auto-discovery successful - device found at 192.168.4.1"
   → "Connection status: CONNECTED"
   → "BPM data received"
```

## Success Indicators

✅ **WiFi Discovery**: App finds "ESP32-BPM-Detector" network
✅ **WiFi Connection**: Android connects to ESP32 WiFi
✅ **HTTP Communication**: App receives BPM data from ESP32
✅ **UI Status**: Connection status shows "CONNECTED"
✅ **Data Flow**: BPM values update in real-time

## Files Modified

All fixes have been applied to:
- `android-app/app/src/main/java/com/sparesparrow/bpmdetector/network/WiFiManager.kt`
- `android-app/app/src/main/java/com/sparesparrow/bpmdetector/services/BPMService.kt`
- `android-app/app/src/main/java/com/sparesparrow/bpmdetector/viewmodels/BPMViewModel.kt`

## Next Steps

1. **Connect Android device** via USB
2. **Enable USB debugging** on device
3. **Run test script**: `./scripts/test_connection.sh`
4. **Monitor logs** for connection progress
5. **Verify** BPM data is received

The app is ready for testing! 🚀
