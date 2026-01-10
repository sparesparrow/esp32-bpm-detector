#!/bin/bash
# ESP32 Serial Monitor Script
# Monitors serial output and captures WiFi connection info

PORT="${1:-/dev/ttyACM0}"
BAUD="${2:-115200}"

echo "Starting ESP32 serial monitor on $PORT at $BAUD baud..."
echo "Press Ctrl+C to stop"
echo ""

# Use screen for serial monitoring
screen -dmS esp32-monitor minicom -D $PORT -b $BAUD -C /tmp/esp32_serial.log

# Wait a moment for screen to start
sleep 2

# Monitor the log file for WiFi connection info
tail -f /tmp/esp32_serial.log 2>/dev/null | while IFS= read -r line; do
    echo "[ESP32] $line"
    
    # Capture IP address
    if echo "$line" | grep -q "IP address"; then
        IP=$(echo "$line" | grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | head -1)
        if [ ! -z "$IP" ]; then
            echo "$IP" > /tmp/esp32_ip.txt
            echo "[ESP32] IP address captured: $IP"
        fi
    fi
    
    # Check for WiFi connection
    if echo "$line" | grep -qi "connected\|wifi"; then
        echo "[ESP32] WiFi status detected in output"
    fi
done


