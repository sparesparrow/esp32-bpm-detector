#!/bin/bash
# Verification script for BPM detection fixes
# Captures serial output and analyzes for expected behavior

SERIAL_PORT="${1:-/dev/ttyACM0}"
BAUD_RATE="${2:-115200}"
LOG_FILE="/home/sparrow/projects/.cursor/debug.log"
VERIFY_DURATION="${3:-30}"  # seconds

echo "=========================================="
echo "BPM Detection Fixes Verification"
echo "=========================================="
echo ""
echo "This script will:"
echo "1. Capture serial output for ${VERIFY_DURATION} seconds"
echo "2. Analyze for correct sampling rate (25000 Hz)"
echo "3. Check for buffer fill events"
echo "4. Verify BPM detection is working"
echo ""
echo "Make sure:"
echo "- ESP32 is connected to ${SERIAL_PORT}"
echo "- Music is playing with clear beat (60-200 BPM)"
echo ""
read -p "Press Enter to start verification..."

# Clear log file
> "$LOG_FILE"

echo ""
echo "Starting capture for ${VERIFY_DURATION} seconds..."
echo "Playing music now..."
echo ""

# Capture serial output
timeout ${VERIFY_DURATION} pio device monitor --port "$SERIAL_PORT" --baud "$BAUD_RATE" 2>&1 | \
    tee /tmp/esp32_serial_output.txt | \
    grep -E '(sessionId|sample|buffer|BPM|beat|detect)' | \
    tee -a "$LOG_FILE"

echo ""
echo "=========================================="
echo "Verification Results"
echo "=========================================="
echo ""

# Analyze results
if [ -s "$LOG_FILE" ]; then
    echo "✓ Log file contains data"
    
    SAMPLE_COUNT=$(grep -c "Taking audio sample" "$LOG_FILE" 2>/dev/null || echo "0")
    BUFFER_READY=$(grep -c "buffer ready" "$LOG_FILE" 2>/dev/null || echo "0")
    BPM_DETECTED=$(grep -c "BPM detection" "$LOG_FILE" 2>/dev/null || echo "0")
    BEAT_DETECTED=$(grep -c "beat detected" "$LOG_FILE" 2>/dev/null || echo "0")
    
    echo "Samples taken: ${SAMPLE_COUNT}"
    echo "Buffer ready events: ${BUFFER_READY}"
    echo "BPM detection events: ${BPM_DETECTED}"
    echo "Beat detection events: ${BEAT_DETECTED}"
    echo ""
    
    # Check sampling rate
    if [ "$SAMPLE_COUNT" -gt 100 ]; then
        echo "✓ Sampling appears to be working (${SAMPLE_COUNT} samples captured)"
    else
        echo "⚠ Low sample count - may indicate sampling issue"
    fi
    
    # Check buffer fill
    if [ "$BUFFER_READY" -gt 0 ]; then
        echo "✓ Buffer is filling (${BUFFER_READY} ready events)"
    else
        echo "⚠ No buffer ready events - buffer may not be filling"
    fi
    
    # Check BPM detection
    if [ "$BPM_DETECTED" -gt 0 ] || [ "$BEAT_DETECTED" -gt 0 ]; then
        echo "✓ BPM/Beat detection is working"
    else
        echo "⚠ No BPM/Beat detection events"
    fi
    
    echo ""
    echo "Full log saved to: $LOG_FILE"
    echo "Serial output saved to: /tmp/esp32_serial_output.txt"
else
    echo "⚠ Log file is empty - no data captured"
    echo "Check:"
    echo "  - Serial port is correct: $SERIAL_PORT"
    echo "  - Device is connected and powered"
    echo "  - Firmware is uploaded"
fi

echo ""
echo "=========================================="


