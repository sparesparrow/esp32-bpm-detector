#!/bin/bash
# Android Logcat Monitor Script
# Monitors BPM detector app logs for connection status and API calls

DEVICE="${1:-HT36TW903516}"
PACKAGE="com.sparesparrow.bpmdetector.debug"

echo "Starting Android logcat monitor for device $DEVICE..."
echo "Monitoring package: $PACKAGE"
echo "Press Ctrl+C to stop"
echo ""

adb -s $DEVICE logcat -c  # Clear log buffer

adb -s $DEVICE logcat | grep --line-buffered -E "($PACKAGE|BPM|Connection|API|192\.168)" | while IFS= read -r line; do
    echo "[Android] $line"
    
    # Capture connection status changes
    if echo "$line" | grep -q "Connection status"; then
        STATUS=$(echo "$line" | grep -oE "(CONNECTED|DISCONNECTED|CONNECTING)")
        if [ ! -z "$STATUS" ]; then
            echo "$STATUS" > /tmp/android_connection_status.txt
            echo "[Android] Connection status: $STATUS"
        fi
    fi
    
    # Capture API errors
    if echo "$line" | grep -qi "error\|exception\|failed"; then
        echo "[Android] ERROR detected: $line"
    fi
done


