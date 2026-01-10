#!/bin/bash
# Capture Serial output from ESP32 and write NDJSON lines to debug.log
# Filters for NDJSON lines (starting with {"sessionId":"debug-session")

LOG_FILE="/home/sparrow/projects/.cursor/debug.log"
SERIAL_PORT="${1:-/dev/ttyACM0}"
BAUD_RATE="${2:-115200}"

echo "Capturing Serial output from $SERIAL_PORT at $BAUD_RATE baud"
echo "Writing NDJSON logs to $LOG_FILE"
echo "Press Ctrl+C to stop"
echo ""

# Clear the log file
> "$LOG_FILE"

# Use picocom, minicom, or screen to capture serial output
# Filter for NDJSON lines and append to log file
if command -v picocom &> /dev/null; then
    picocom -b "$BAUD_RATE" "$SERIAL_PORT" 2>&1 | grep --line-buffered '^{"sessionId":"debug-session' >> "$LOG_FILE" &
elif command -v screen &> /dev/null; then
    screen "$SERIAL_PORT" "$BAUD_RATE" 2>&1 | grep --line-buffered '^{"sessionId":"debug-session' >> "$LOG_FILE" &
else
    echo "Error: Need picocom or screen installed"
    echo "Install with: sudo apt-get install picocom"
    exit 1
fi

CAPTURE_PID=$!
echo "Capture process PID: $CAPTURE_PID"
echo "Logs are being written to $LOG_FILE"
echo ""

# Wait for user interrupt
trap "kill $CAPTURE_PID 2>/dev/null; exit" INT TERM
wait $CAPTURE_PID


