#!/bin/bash
# Test script to help diagnose WiFi scanning issues

echo "=== ESP32 BPM Detector WiFi Diagnostics ==="
echo ""

# Check if ESP32 is running and broadcasting WiFi
echo "1. Checking if ESP32 WiFi network is visible..."
echo "   Please run this command on your computer/laptop:"
echo "   nmcli device wifi list | grep -i esp32"
echo ""
echo "   Or on Windows:"
echo "   netsh wlan show networks | findstr /i esp32"
echo ""

# Check Android device connection
echo "2. Checking Android device connection..."
adb devices
echo ""

# Check current app logs
echo "3. Checking current app logs (if device is connected)..."
adb logcat -d | grep -i "WiFi\|wifi\|BPM" | tail -20
echo ""

echo "4. Manual WiFi scanning test (if device is connected):"
echo "   - Open the BPM Detector app"
echo "   - Go to Settings"
echo "   - Grant location permissions when prompted"
echo "   - Tap 'Scan WiFi' button"
echo "   - Check 'Show Debug Info' to see scanning results"
echo ""

echo "5. ESP32 WiFi Configuration Check:"
echo "   Make sure your ESP32 is configured to broadcast 'ESP32-BPM-DETECTOR' SSID"
echo "   Check the ESP32 serial output for WiFi status"
echo ""

echo "6. Common Issues:"
echo "   - Location permissions not granted"
echo "   - ESP32 not broadcasting correct SSID"
echo "   - WiFi scanning disabled on Android device"
echo "   - Android device location services disabled"
echo "   - ESP32 WiFi signal too weak"
echo ""

echo "Run 'adb logcat | grep WiFiManager' to monitor WiFi scanning in real-time"