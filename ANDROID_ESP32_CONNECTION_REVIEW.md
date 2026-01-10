# Android App Cannot See ESP32 - Connection Issues Review

## Executive Summary

The Android app cannot discover or connect to the ESP32 device due to **three critical mismatches** between the Android app configuration and the ESP32 firmware:

1. **SSID Case Mismatch** - Android looks for wrong network name
2. **IP Address Mismatch** - Service uses wrong default IP
3. **Password Mismatch** - Android expects open network, ESP32 uses password

## Critical Issues

### 1. SSID Case Mismatch 🔴 **CRITICAL**

**ESP32 Firmware** (`src/main.cpp:335`):
```cpp
bool apStarted = WiFi.softAP("ESP32-BPM-Detector", "bpm12345");
```
- Creates AP with SSID: `"ESP32-BPM-Detector"` (capital D in Detector)

**Android App** (`WiFiManager.kt:27`):
```kotlin
const val ESP32_SSID = "ESP32-BPM-DETECTOR"  // All caps DETECTOR
```
- Looks for SSID: `"ESP32-BPM-DETECTOR"` (all caps DETECTOR)

**Impact**: Android WiFi scan will **never find** the ESP32 network because the SSID doesn't match.

**Fix**: Update Android app to match ESP32:
```kotlin
const val ESP32_SSID = "ESP32-BPM-Detector"  // Match ESP32 exactly
```

---

### 2. IP Address Mismatch 🔴 **CRITICAL**

**BPMService.kt** (line 38):
```kotlin
private var serverIp: String = "192.168.1.100" // Wrong IP!
```

**BPMViewModel.kt** (line 52):
```kotlin
private val _serverIp = MutableStateFlow("192.168.4.1") // Correct IP
```

**ESP32 AP Mode**: Uses standard AP gateway IP `192.168.4.1`

**Impact**: 
- Service starts with wrong IP (`192.168.1.100`)
- Even if WiFi connects, HTTP requests go to wrong IP
- Connection will always fail

**Fix**: Update BPMService default:
```kotlin
private var serverIp: String = "192.168.4.1" // Match ViewModel and ESP32 AP IP
```

---

### 3. Password Mismatch 🔴 **CRITICAL**

**ESP32 Firmware** (`src/main.cpp:335`):
```cpp
WiFi.softAP("ESP32-BPM-Detector", "bpm12345");  // Has password!
```

**Android WiFiManager** (`WiFiManager.kt:28, 149-152`):
```kotlin
const val ESP32_DEFAULT_PASSWORD = "" // Open network

val wifiConfig = WifiConfiguration().apply {
    SSID = "\"$ESP32_SSID\""
    allowedKeyManagement.set(WifiConfiguration.KeyMgmt.NONE)  // No password!
}
```

**Impact**: 
- Android tries to connect as open network
- ESP32 requires password "bpm12345"
- Connection will fail even if SSID matches

**Fix**: Update WiFiManager to use password:
```kotlin
const val ESP32_DEFAULT_PASSWORD = "bpm12345"

val wifiConfig = WifiConfiguration().apply {
    SSID = "\"$ESP32_SSID\""
    preSharedKey = "\"$ESP32_DEFAULT_PASSWORD\""
    allowedKeyManagement.set(WifiConfiguration.KeyMgmt.WPA_PSK)
    allowedAuthAlgorithms.set(WifiConfiguration.AuthAlgorithm.OPEN)
}
```

---

## Additional Issues

### 4. Auto-Discovery Timing Issues 🟠 **HIGH**

**BPMViewModel.kt** (lines 488-542):
- Uses fixed delays (`delay(2000)`) which may not be sufficient
- No retry logic if initial scan fails
- Runs immediately on ViewModel init (line 119) - may run before permissions granted

**Issues**:
- WiFi scan may take longer than 2 seconds
- Network connection may take longer than 2 seconds to stabilize
- No exponential backoff or retry mechanism

**Recommendation**: 
- Add retry logic with exponential backoff
- Wait for WiFi connection state before attempting HTTP connection
- Check permissions before starting auto-discovery

---

### 5. Service IP Not Updated from ViewModel 🟠 **MEDIUM**

**BPMService.kt** (lines 49-52):
```kotlin
intent?.getStringExtra(EXTRA_SERVER_IP)?.let { ip ->
    setServerIp(ip)
}
```

**Issue**: Service only updates IP from Intent extra, but ViewModel may have different IP set.

**Impact**: If user changes IP in ViewModel, service may still use old IP.

**Fix**: Ensure service gets IP from ViewModel when starting:
```kotlin
// In BPMViewModel.startMonitoring()
val intent = Intent(context, BPMService::class.java).apply {
    putExtra(BPMService.EXTRA_SERVER_IP, _serverIp.value)
}
context.startService(intent)
```

---

### 6. No Network State Monitoring 🟡 **MEDIUM**

**Issue**: App doesn't monitor WiFi connection state changes.

**Impact**: 
- If WiFi disconnects, app continues polling (wasting battery)
- No automatic reconnection when WiFi reconnects
- User must manually reconnect

**Recommendation**: Add `ConnectivityManager` network state monitoring.

---

## Connection Flow Analysis

### Current Flow (Broken):
1. ✅ ViewModel initializes with IP `192.168.4.1`
2. ❌ Service initializes with IP `192.168.1.100` (WRONG)
3. ❌ Auto-discovery scans for `"ESP32-BPM-DETECTOR"` (WRONG SSID)
4. ❌ ESP32 broadcasts `"ESP32-BPM-Detector"` (different case)
5. ❌ Scan finds nothing (SSID mismatch)
6. ❌ Even if found, connection fails (password mismatch)
7. ❌ Even if connected, HTTP requests go to wrong IP

### Expected Flow (Fixed):
1. ✅ ViewModel and Service both use IP `192.168.4.1`
2. ✅ Auto-discovery scans for `"ESP32-BPM-Detector"` (correct SSID)
3. ✅ ESP32 network found in scan
4. ✅ Connect with password `"bpm12345"`
5. ✅ Wait for connection to stabilize
6. ✅ HTTP requests to `192.168.4.1` succeed
7. ✅ BPM data received

---

## Recommended Fixes (Priority Order)

### Priority 1: Fix SSID Match
```kotlin
// WiFiManager.kt:27
const val ESP32_SSID = "ESP32-BPM-Detector"  // Match ESP32 exactly
```

### Priority 2: Fix IP Address
```kotlin
// BPMService.kt:38
private var serverIp: String = "192.168.4.1" // Match ViewModel default
```

### Priority 3: Fix Password
```kotlin
// WiFiManager.kt:28
const val ESP32_DEFAULT_PASSWORD = "bpm12345"

// WiFiManager.kt:149-152
val wifiConfig = WifiConfiguration().apply {
    SSID = "\"$ESP32_SSID\""
    preSharedKey = "\"$ESP32_DEFAULT_PASSWORD\""
    allowedKeyManagement.set(WifiConfiguration.KeyMgmt.WPA_PSK)
    allowedAuthAlgorithms.set(WifiConfiguration.AuthAlgorithm.OPEN)
    allowedProtocols.set(WifiConfiguration.Protocol.WPA)
}
```

### Priority 4: Improve Auto-Discovery
- Add retry logic
- Monitor WiFi connection state
- Wait for stable connection before HTTP requests
- Check permissions before scanning

---

## Testing Checklist

After fixes, verify:
- [ ] WiFi scan finds "ESP32-BPM-Detector" network
- [ ] App can connect to ESP32 WiFi network
- [ ] HTTP requests reach ESP32 at `192.168.4.1`
- [ ] BPM data is received from ESP32
- [ ] Connection status updates correctly
- [ ] Auto-discovery works on app start
- [ ] Manual IP entry works
- [ ] Reconnection works after WiFi disconnect

---

## Related Files

- `android-app/app/src/main/java/com/sparesparrow/bpmdetector/network/WiFiManager.kt`
- `android-app/app/src/main/java/com/sparesparrow/bpmdetector/services/BPMService.kt`
- `android-app/app/src/main/java/com/sparesparrow/bpmdetector/viewmodels/BPMViewModel.kt`
- `src/main.cpp` (ESP32 firmware)
