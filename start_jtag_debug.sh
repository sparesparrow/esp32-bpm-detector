#!/bin/bash
# Start JTAG debugging session for ESP32-S3 using built-in USB JTAG

LOG_FILE=".cursor/debug.log"
OPENOCD_CFG="openocd.cfg"

echo "Starting JTAG debugging for ESP32-S3..."
echo "USB JTAG device: 303a:1001 (Espressif USB JTAG/serial debug unit)"

# Find OpenOCD
OPENOCD_BIN=$(which openocd)
if [ -z "$OPENOCD_BIN" ]; then
    # Try PlatformIO's OpenOCD
    OPENOCD_BIN=$(find ~/.platformio -name "openocd" -type f 2>/dev/null | head -1)
    if [ -z "$OPENOCD_BIN" ]; then
        echo "Error: OpenOCD not found. Installing..."
        echo "Please install OpenOCD: sudo apt-get install openocd"
        exit 1
    fi
fi

echo "Using OpenOCD: $OPENOCD_BIN"

# Clear log file
mkdir -p .cursor
> "$LOG_FILE"

# Check if ESP32-S3 JTAG is connected
if ! lsusb | grep -q "303a:1001"; then
    echo "Warning: ESP32-S3 USB JTAG not detected. Make sure device is connected."
    echo "Expected: Bus XXX Device XXX: ID 303a:1001 Espressif USB JTAG/serial debug unit"
fi

# Start OpenOCD
echo "Starting OpenOCD..."
"$OPENOCD_BIN" -f "$OPENOCD_CFG" > openocd.log 2>&1 &
OPENOCD_PID=$!

sleep 2

# Check if OpenOCD started
if ! kill -0 $OPENOCD_PID 2>/dev/null; then
    echo "Error: OpenOCD failed to start. Check openocd.log:"
    cat openocd.log
    exit 1
fi

echo "OpenOCD started (PID: $OPENOCD_PID)"
echo ""
echo "Next steps:"
echo "1. Connect GDB:"
echo "   xtensa-esp32s3-elf-gdb -x gdbinit .pio/build/esp32-s3/firmware.elf"
echo ""
echo "2. Or use PlatformIO debugger (if configured)"
echo ""
echo "3. In GDB, use 'dumplogs' command to extract logs from memory buffer"
echo ""
echo "OpenOCD is running. Press Ctrl+C to stop."

# Wait for interrupt
trap "kill $OPENOCD_PID 2>/dev/null; echo 'Stopped OpenOCD'; exit" INT TERM
wait


