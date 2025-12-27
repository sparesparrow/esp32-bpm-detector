#!/bin/bash
# Script to start JTAG debugging session for ESP32-S3

LOG_FILE=".cursor/debug.log"
OPENOCD_CFG="openocd.cfg"

echo "Starting OpenOCD for ESP32-S3 JTAG debugging..."
echo "Log file: $LOG_FILE"

# Clear log file
mkdir -p .cursor
> "$LOG_FILE"

# Start OpenOCD in background
openocd -f "$OPENOCD_CFG" > openocd.log 2>&1 &
OPENOCD_PID=$!

echo "OpenOCD started with PID: $OPENOCD_PID"
echo "Waiting for OpenOCD to initialize..."
sleep 2

# Check if OpenOCD is running
if ! kill -0 $OPENOCD_PID 2>/dev/null; then
    echo "Error: OpenOCD failed to start. Check openocd.log"
    cat openocd.log
    exit 1
fi

echo "OpenOCD is running. You can now:"
echo "1. Connect GDB: xtensa-esp32s3-elf-gdb -x gdbinit"
echo "2. Or use PlatformIO debugger"
echo ""
echo "Monitoring log file: $LOG_FILE"
echo "Press Ctrl+C to stop"

# Monitor log file for new entries
tail -f "$LOG_FILE" 2>/dev/null &
TAIL_PID=$!

# Wait for user interrupt
trap "kill $OPENOCD_PID $TAIL_PID 2>/dev/null; exit" INT TERM
wait


