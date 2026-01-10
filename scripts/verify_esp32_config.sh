#!/bin/bash
# Verify ESP32 firmware configuration matches Android app expectations

echo "============================================================"
echo "ESP32 Firmware Configuration Verification"
echo "============================================================"
echo ""

# Check ESP32 source files
ESP32_MAIN="src/main.cpp"
ESP32_WIFI="src/wifi_handler.cpp"

# Expected values
EXPECTED_SSID="ESP32-BPM-Detector"
EXPECTED_PASSWORD="bpm12345"
EXPECTED_IP="192.168.4.1"

echo "Checking ESP32 firmware configuration..."
echo ""

# Check SSID
if grep -q "ESP32-BPM-Detector" "$ESP32_MAIN" 2>/dev/null; then
    echo "✓ SSID: ESP32-BPM-Detector (CORRECT)"
else
    echo "✗ SSID mismatch in $ESP32_MAIN"
fi

# Check password
if grep -q "bpm12345" "$ESP32_MAIN" 2>/dev/null; then
    echo "✓ Password: bpm12345 (CORRECT)"
else
    echo "✗ Password mismatch in $ESP32_MAIN"
fi

# Check AP mode
if grep -q "WiFi.mode(WIFI_AP)" "$ESP32_MAIN" 2>/dev/null || grep -q "WIFI_AP" "$ESP32_MAIN" 2>/dev/null; then
    echo "✓ WiFi mode: AP (Access Point) (CORRECT)"
else
    echo "⚠ WiFi mode not clearly set to AP"
fi

# Check softAP call
if grep -q "softAP.*ESP32-BPM-Detector.*bpm12345" "$ESP32_MAIN" 2>/dev/null; then
    echo "✓ softAP configured correctly (CORRECT)"
else
    echo "⚠ softAP configuration may need verification"
fi

echo ""
echo "============================================================"
echo "Android App Configuration Verification"
echo "============================================================"
echo ""

ANDROID_WIFI="android-app/app/src/main/java/com/sparesparrow/bpmdetector/network/WiFiManager.kt"
ANDROID_SERVICE="android-app/app/src/main/java/com/sparesparrow/bpmdetector/services/BPMService.kt"

# Check Android SSID
if grep -q 'ESP32_SSID = "ESP32-BPM-Detector"' "$ANDROID_WIFI" 2>/dev/null; then
    echo "✓ Android SSID: ESP32-BPM-Detector (CORRECT)"
else
    echo "✗ Android SSID mismatch"
fi

# Check Android password
if grep -q 'ESP32_DEFAULT_PASSWORD = "bpm12345"' "$ANDROID_WIFI" 2>/dev/null; then
    echo "✓ Android Password: bpm12345 (CORRECT)"
else
    echo "✗ Android password mismatch"
fi

# Check Android IP
if grep -q 'serverIp: String = "192.168.4.1"' "$ANDROID_SERVICE" 2>/dev/null; then
    echo "✓ Android IP: 192.168.4.1 (CORRECT)"
else
    echo "✗ Android IP mismatch"
fi

# Check WPA_PSK
if grep -q "WPA_PSK" "$ANDROID_WIFI" 2>/dev/null; then
    echo "✓ Android uses WPA_PSK authentication (CORRECT)"
else
    echo "✗ Android authentication method incorrect"
fi

echo ""
echo "============================================================"
echo "Configuration Summary"
echo "============================================================"
echo ""
echo "ESP32 Firmware:"
echo "  SSID: $EXPECTED_SSID"
echo "  Password: $EXPECTED_PASSWORD"
echo "  AP IP: $EXPECTED_IP (standard ESP32 AP gateway)"
echo ""
echo "Android App:"
echo "  SSID: $EXPECTED_SSID"
echo "  Password: $EXPECTED_PASSWORD"
echo "  Server IP: $EXPECTED_IP"
echo ""
echo "✅ All configurations should match!"
echo ""
