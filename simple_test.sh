#!/bin/bash

echo "=== Simple ESP32-Android Connectivity Test ==="

# Check Android hotspot
echo "1. Android hotspot status:"
adb -s HT36TW903516 shell dumpsys wifi | grep -A 2 -B 2 "hotspot" | head -5

# Check if ESP32 is on network
echo ""
echo "2. Scanning for ESP32 on network:"
for ip in 192.168.43.{100..120}; do
    if adb -s HT36TW903516 shell timeout 0.3 curl -s "http://$ip/api/health" 2>/dev/null | grep -q "status"; then
        echo "✅ FOUND ESP32 at $ip"
        ESP32_IP=$ip
        break
    fi
done

if [ ! -z "$ESP32_IP" ]; then
    echo ""
    echo "3. Testing ESP32 API at $ESP32_IP:"
    echo "Health:"
    adb -s HT36TW903516 shell curl -s "http://$ESP32_IP/api/health"
    echo ""
    echo "Settings:"
    adb -s HT36TW903516 shell curl -s "http://$ESP32_IP/api/settings"
    echo ""
    echo "BPM:"
    adb -s HT36TW903516 shell curl -s "http://$ESP32_IP/api/bpm"
    echo ""
    echo "4. Testing Android app connection:"
    adb -s HT36TW903516 shell am start -n com.sparesparrow.bpmdetector.debug/.MainActivity >/dev/null 2>&1
    sleep 2
    adb -s HT36TW903516 shell input tap 540 1850
    sleep 1
    adb -s HT36TW903516 shell input tap 540 1000
    adb -s HT36TW903516 shell input keyevent KEYCODE_CTRL_A
    adb -s HT36TW903516 shell input keyevent KEYCODE_DEL
    adb -s HT36TW903516 shell input text "$ESP32_IP"
    sleep 1
    adb -s HT36TW903516 shell input tap 540 1300
    sleep 3
    CONNECTION=$(adb -s HT36TW903516 logcat -d | grep "Connection status" | tail -1 | grep -o "CONNECTED\|DISCONNECTED")
    echo "App connection status: $CONNECTION"
    if [ "$CONNECTION" = "CONNECTED" ]; then
        echo ""
        echo "🎉 SUCCESS! ESP32 and Android are communicating!"
    fi
else
    echo "ESP32 not found on network"
fi
