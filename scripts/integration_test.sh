#!/bin/bash
# ESP32-Android Integration Test Script
# Monitors both devices and tests WiFi connectivity

set -e

ESP32_PORT="${1:-/dev/ttyACM0}"
ANDROID_DEVICE="${2:-HT36TW903516}"
APP_PACKAGE="com.sparesparrow.bpmdetector.debug"
MAX_WAIT=120

echo "=========================================="
echo "ESP32-Android Integration Test"
echo "=========================================="
echo "ESP32 Port: $ESP32_PORT"
echo "Android Device: $ANDROID_DEVICE"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "Cleaning up..."
    kill $MONITOR_PID 2>/dev/null || true
}

trap cleanup EXIT

# Step 1: Start serial monitoring
echo "Step 1: Starting ESP32 serial monitor..."
stty -F $ESP32_PORT 115200 cs8 -cstopb -parenb raw -echo 2>/dev/null
(cat $ESP32_PORT > /tmp/esp32_serial.log 2>&1) &
MONITOR_PID=$!
sleep 2

# Step 2: Monitor serial output for WiFi connection
echo "Step 2: Waiting for ESP32 WiFi connection (max $MAX_WAIT seconds)..."
ESP32_IP=""
WAITED=0

while [ -z "$ESP32_IP" ] && [ $WAITED -lt $MAX_WAIT ]; do
    sleep 2
    WAITED=$((WAITED + 2))
    
    # Check serial log for IP address
    if [ -f /tmp/esp32_serial.log ]; then
        IP=$(grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' /tmp/esp32_serial.log | tail -1)
        if [ ! -z "$IP" ] && [[ "$IP" =~ ^192\.168\. ]]; then
            ESP32_IP="$IP"
            echo "✅ ESP32 IP found in serial output: $ESP32_IP"
            break
        fi
    fi
    
    # Also scan network periodically
    if [ $((WAITED % 10)) -eq 0 ]; then
        echo "  Scanning network... (waited $WAITED seconds)"
        for ip in 192.168.200.{100..200} 192.168.200.{2..99}; do
            RESPONSE=$(timeout 0.2 curl -s "http://$ip/api/health" 2>/dev/null)
            if echo "$RESPONSE" | grep -qE '"(status|uptime|heap)"' && [ ${#RESPONSE} -lt 500 ]; then
                ESP32_IP="$ip"
                echo "✅ ESP32 found on network: $ESP32_IP"
                break
            fi
        done
        [ ! -z "$ESP32_IP" ] && break
    fi
done

if [ -z "$ESP32_IP" ]; then
    echo "❌ ESP32 not found after $MAX_WAIT seconds"
    echo "   Please check:"
    echo "   - ESP32 is powered on"
    echo "   - Firmware is uploaded"
    echo "   - WiFi credentials in config.h are correct"
    exit 1
fi

echo "$ESP32_IP" > /tmp/esp32_ip.txt
echo ""

# Step 3: Test ESP32 API endpoints
echo "Step 3: Testing ESP32 API endpoints..."
echo ""

echo "Testing /api/health:"
HEALTH=$(curl -s --connect-timeout 5 "http://$ESP32_IP/api/health")
if [ $? -eq 0 ] && [ ! -z "$HEALTH" ]; then
    echo "✅ /api/health: OK"
    echo "$HEALTH" | jq . 2>/dev/null || echo "$HEALTH"
else
    echo "❌ /api/health: FAILED"
fi
echo ""

echo "Testing /api/settings:"
SETTINGS=$(curl -s --connect-timeout 5 "http://$ESP32_IP/api/settings")
if [ $? -eq 0 ] && [ ! -z "$SETTINGS" ]; then
    echo "✅ /api/settings: OK"
    echo "$SETTINGS" | jq . 2>/dev/null || echo "$SETTINGS"
else
    echo "❌ /api/settings: FAILED"
fi
echo ""

echo "Testing /api/bpm:"
BPM=$(curl -s --connect-timeout 5 "http://$ESP32_IP/api/bpm")
if [ $? -eq 0 ] && [ ! -z "$BPM" ]; then
    echo "✅ /api/bpm: OK"
    echo "$BPM" | jq . 2>/dev/null || echo "$BPM"
else
    echo "❌ /api/bpm: FAILED"
fi
echo ""

# Step 4: Verify Android WiFi connection
echo "Step 4: Verifying Android WiFi connection..."
ANDROID_SSID=$(adb -s $ANDROID_DEVICE shell dumpsys wifi | grep -i "SSID:" | head -1 | grep -oE "SSID: [^ ]+" | cut -d' ' -f2 || echo "")
if [ ! -z "$ANDROID_SSID" ]; then
    echo "✅ Android connected to: $ANDROID_SSID"
else
    echo "⚠️  Could not determine Android WiFi SSID"
fi

# Get Android IP
ANDROID_IP=$(adb -s $ANDROID_DEVICE shell getprop dhcp.wlan0.ipaddress 2>/dev/null || echo "")
if [ -z "$ANDROID_IP" ]; then
    # Try alternative method
    ANDROID_IP=$(adb -s $ANDROID_DEVICE shell ip route get 8.8.8.8 2>/dev/null | grep -oP 'src \K\S+' || echo "")
fi

if [ ! -z "$ANDROID_IP" ]; then
    echo "✅ Android IP: $ANDROID_IP"
    # Check if same subnet
    ESP32_SUBNET=$(echo "$ESP32_IP" | cut -d'.' -f1-3)
    ANDROID_SUBNET=$(echo "$ANDROID_IP" | cut -d'.' -f1-3)
    if [ "$ESP32_SUBNET" = "$ANDROID_SUBNET" ]; then
        echo "✅ Both devices on same subnet: $ESP32_SUBNET.x"
    else
        echo "⚠️  Devices on different subnets (ESP32: $ESP32_SUBNET.x, Android: $ANDROID_SUBNET.x)"
    fi
else
    echo "⚠️  Could not determine Android IP"
fi
echo ""

# Step 5: Launch and configure Android app
echo "Step 5: Configuring Android app..."
adb -s $ANDROID_DEVICE shell am start -n $APP_PACKAGE/com.sparesparrow.bpmdetector.MainActivity >/dev/null 2>&1
sleep 2

# Navigate to Settings
adb -s $ANDROID_DEVICE shell input tap 540 1850
sleep 1

# Clear and enter ESP32 IP
adb -s $ANDROID_DEVICE shell input tap 540 1000
sleep 0.5
adb -s $ANDROID_DEVICE shell input keyevent KEYCODE_CTRL_A
adb -s $ANDROID_DEVICE shell input keyevent KEYCODE_DEL
adb -s $ANDROID_DEVICE shell input text "$ESP32_IP"
sleep 0.5

# Tap Connect button (assuming it's around y=1200)
adb -s $ANDROID_DEVICE shell input tap 540 1200
sleep 2

echo "✅ Android app configured with ESP32 IP: $ESP32_IP"
echo ""

# Step 6: Monitor connection status
echo "Step 6: Monitoring connection status..."
sleep 5

CONNECTION_STATUS=$(adb -s $ANDROID_DEVICE logcat -d | grep "Connection status" | tail -1 | grep -oE "(CONNECTED|DISCONNECTED|CONNECTING)" || echo "UNKNOWN")

if [ "$CONNECTION_STATUS" = "CONNECTED" ]; then
    echo "✅ Android app connected to ESP32!"
elif [ "$CONNECTION_STATUS" = "CONNECTING" ]; then
    echo "⏳ Android app is connecting..."
elif [ "$CONNECTION_STATUS" = "DISCONNECTED" ]; then
    echo "❌ Android app disconnected"
else
    echo "⚠️  Connection status: $CONNECTION_STATUS"
fi

# Check for BPM data
BPM_DATA=$(adb -s $ANDROID_DEVICE logcat -d | grep -i "bpm\|BPM" | tail -3)
if [ ! -z "$BPM_DATA" ]; then
    echo ""
    echo "Recent BPM data from logs:"
    echo "$BPM_DATA"
fi

echo ""
echo "=========================================="
echo "Integration Test Complete"
echo "=========================================="
echo "ESP32 IP: $ESP32_IP"
echo "Android Device: $ANDROID_DEVICE"
echo "Connection Status: $CONNECTION_STATUS"
echo ""

