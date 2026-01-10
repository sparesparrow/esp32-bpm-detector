# Android-ESP32 Connection Testing Checklist

## Pre-Testing Setup

- [ ] ESP32 device is powered on
- [ ] ESP32 firmware is running (check serial output)
- [ ] ESP32 WiFi AP is active (SSID: "ESP32-BPM-Detector")
- [ ] Android device has location permissions granted
- [ ] Android device WiFi is enabled
- [ ] Android app APK is installed on device

## Test 1: WiFi Discovery ✓

**Steps:**
1. Open Android app
2. Grant location permissions if prompted
3. Observe auto-discovery starting

**Expected Results:**
- [ ] App logs show: "Starting WiFi scan for ESP32 network"
- [ ] App logs show: "ESP32 WiFi network found: true"
- [ ] WiFi scan results include "ESP32-BPM-Detector"

**Verification:**
```bash
adb logcat | grep -E "(WiFi|ESP32|scan)" | grep -i "ESP32-BPM-Detector"
```

## Test 2: WiFi Connection ✓

**Steps:**
1. After discovery, app should attempt connection automatically
2. Check Android WiFi settings

**Expected Results:**
- [ ] App logs show: "ESP32 WiFi network found, attempting connection"
- [ ] App logs show: "Successfully connected to ESP32 WiFi network"
- [ ] Android WiFi settings show connected to "ESP32-BPM-Detector"
- [ ] Connection uses password "bpm12345"

**Verification:**
```bash
adb logcat | grep -E "(connected|WiFi|ESP32)" | grep -i "connected"
```

## Test 3: HTTP Communication ✓

**Steps:**
1. After WiFi connection, app should attempt HTTP connection
2. Check connection status in app UI

**Expected Results:**
- [ ] App logs show: "Auto-discovery successful - device found at 192.168.4.1"
- [ ] Connection status shows "CONNECTED"
- [ ] BPM data is received from ESP32
- [ ] Health endpoint responds successfully

**Verification:**
```bash
# From computer connected to ESP32 WiFi:
curl http://192.168.4.1/api/health
curl http://192.168.4.1/api/bpm
```

## Test 4: Manual IP Entry ✓

**Steps:**
1. Go to Settings screen
2. Enter IP address: 192.168.4.1
3. Save settings
4. Start monitoring

**Expected Results:**
- [ ] IP address is saved correctly
- [ ] Connection succeeds with manual IP
- [ ] BPM data is received

## Troubleshooting

### WiFi Network Not Found
- Check ESP32 serial output for AP status
- Verify SSID matches exactly: "ESP32-BPM-Detector"
- Check Android location permissions
- Try manual WiFi scan in Android settings

### Connection Fails
- Verify password is "bpm12345"
- Check WiFi authentication method (should be WPA_PSK)
- Check Android WiFi logs: `adb logcat | grep WifiManager`

### HTTP Requests Fail
- Verify IP address is 192.168.4.1
- Check ESP32 serial output for HTTP requests
- Test from computer: `curl http://192.168.4.1/api/health`
- Check Android network connectivity

## Success Criteria

All tests pass when:
- ✅ WiFi discovery finds ESP32 network
- ✅ WiFi connection succeeds
- ✅ HTTP communication works
- ✅ BPM data is received
- ✅ Connection status shows "CONNECTED"
