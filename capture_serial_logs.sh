#!/bin/bash
# Script to capture ESP32 Serial output and write to debug.log
# Usage: ./capture_serial_logs.sh

LOG_FILE=".cursor/debug.log"
SERIAL_PORT=$(pio device list | grep -oP '/dev/tty\w+' | head -n1)
BAUD_RATE=115200

if [ -z "$SERIAL_PORT" ]; then
    echo "Error: No serial port found. Make sure ESP32 is connected."
    exit 1
fi

echo "Capturing Serial output from $SERIAL_PORT at $BAUD_RATE baud..."
echo "Writing to $LOG_FILE"
echo "Press Ctrl+C to stop after a few loop iterations"
echo ""

# Clear/create log file
mkdir -p .cursor
> "$LOG_FILE"

# Capture serial output and filter for JSON lines (our log format)
pio device monitor --port "$SERIAL_PORT" --baud "$BAUD_RATE" 2>/dev/null | while IFS= read -r line; do
    # Check if line is a JSON log entry (starts with { and contains sessionId)
    if [[ "$line" =~ ^\{.*\"sessionId\" ]]; then
        echo "$line" >> "$LOG_FILE"
    fi
    # Also display on screen
    echo "$line"
done


