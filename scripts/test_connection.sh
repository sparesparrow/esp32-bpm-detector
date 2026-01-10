#!/bin/bash
# Test script for Android-ESP32 connection
# Run this script when Android device is connected via ADB

set -e

echo "============================================================"
echo "Android-ESP32 Connection Test Script"
echo "============================================================"
echo ""

# Check if device is connected
if ! adb devices | grep -q "device$"; then
    echo "❌ No Android device connected via ADB"
    echo ""
    echo "Please:"
    echo "  1. Connect Android device via USB"
    echo "  2. Enable USB debugging on device"
    echo "  3. Accept USB debugging prompt on device"
    echo "  4. Run: adb devices (to verify connection)"
    echo ""
    exit 1
fi

echo "✓ Android device connected"
echo ""

# Install APK
echo "============================================================"
echo "Step 1: Installing APK"
echo "============================================================"
adb install -r android-app/app/build/outputs/apk/debug/app-debug.apk
echo "✓ APK installed"
echo ""

# Clear logcat
echo "============================================================"
echo "Step 2: Clearing logcat"
echo "============================================================"
adb logcat -c
echo "✓ Logcat cleared"
echo ""

# Launch app
echo "============================================================"
echo "Step 3: Launching app"
echo "============================================================"
adb shell am start -n com.sparesparrow.bpmdetector/.ui.MainActivity
echo "✓ App launched"
echo ""

# Wait a moment for app to initialize
sleep 2

# Monitor logs for WiFi discovery
echo "============================================================"
echo "Step 4: Monitoring WiFi Discovery (10 seconds)"
echo "============================================================"
echo "Looking for:"
echo "  - WiFi scan starting"
echo "  - ESP32-BPM-Detector network found"
echo "  - Connection attempts"
echo ""
timeout 10 adb logcat | grep -E "(WiFi|ESP32|scan|Discovery|BPM)" --line-buffered || true
echo ""

# Check connection status
echo "============================================================"
echo "Step 5: Checking Connection Status"
echo "============================================================"
echo "Recent connection-related logs:"
adb logcat -d | grep -E "(Connection|connected|ESP32|192.168.4.1)" | tail -10 || echo "No connection logs found"
echo ""

# Check if app is running
echo "============================================================"
echo "Step 6: App Status"
echo "============================================================"
if adb shell "dumpsys activity activities | grep -A 5 'bpmdetector'" | grep -q "bpmdetector"; then
    echo "✓ App is running"
else
    echo "⚠ App may not be running"
fi
echo ""

# WiFi status check
echo "============================================================"
echo "Step 7: WiFi Status Check"
echo "============================================================"
echo "Current WiFi connection:"
adb shell "dumpsys wifi | grep -A 5 'mWifiInfo'" | head -5 || echo "Could not get WiFi info"
echo ""

echo "============================================================"
echo "Test Complete"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Check app UI for connection status"
echo "  2. Monitor logs: adb logcat | grep -E '(BPM|WiFi|ESP32)'"
echo "  3. Verify ESP32 is powered on and broadcasting WiFi"
echo "  4. Check Android WiFi settings for 'ESP32-BPM-Detector' network"
echo ""
