#!/bin/bash
# ESP32 API Testing Script
# Tests ESP32 API endpoints once IP is discovered

IP_FILE="/tmp/esp32_ip.txt"
MAX_WAIT=60
WAITED=0

echo "Waiting for ESP32 IP address..."
while [ ! -f "$IP_FILE" ] && [ $WAITED -lt $MAX_WAIT ]; do
    sleep 1
    WAITED=$((WAITED + 1))
    if [ $((WAITED % 5)) -eq 0 ]; then
        echo "Still waiting for ESP32 IP... ($WAITED/$MAX_WAIT seconds)"
    fi
done

if [ ! -f "$IP_FILE" ]; then
    echo "ERROR: ESP32 IP not found after $MAX_WAIT seconds"
    echo "Trying common IPs..."
    for ip in 192.168.200.{100..150} 192.168.1.{100..150}; do
        if curl -s --connect-timeout 1 "http://$ip/api/health" > /dev/null 2>&1; then
            echo "$ip" > "$IP_FILE"
            echo "Found ESP32 at: $ip"
            break
        fi
    done
fi

if [ ! -f "$IP_FILE" ]; then
    echo "ERROR: Could not find ESP32 IP address"
    exit 1
fi

ESP32_IP=$(cat "$IP_FILE")
echo "Testing ESP32 API at: $ESP32_IP"
echo ""

# Test /api/health
echo "1. Testing /api/health..."
HEALTH=$(curl -s --connect-timeout 5 "http://$ESP32_IP/api/health")
if [ $? -eq 0 ] && [ ! -z "$HEALTH" ]; then
    echo "✅ /api/health: OK"
    echo "   Response: $HEALTH"
else
    echo "❌ /api/health: FAILED"
fi
echo ""

# Test /api/settings
echo "2. Testing /api/settings..."
SETTINGS=$(curl -s --connect-timeout 5 "http://$ESP32_IP/api/settings")
if [ $? -eq 0 ] && [ ! -z "$SETTINGS" ]; then
    echo "✅ /api/settings: OK"
    echo "   Response: $SETTINGS"
else
    echo "❌ /api/settings: FAILED"
fi
echo ""

# Test /api/bpm
echo "3. Testing /api/bpm..."
BPM=$(curl -s --connect-timeout 5 "http://$ESP32_IP/api/bpm")
if [ $? -eq 0 ] && [ ! -z "$BPM" ]; then
    echo "✅ /api/bpm: OK"
    echo "   Response: $BPM"
else
    echo "❌ /api/bpm: FAILED"
fi
echo ""

echo "ESP32 API testing complete. IP: $ESP32_IP"


