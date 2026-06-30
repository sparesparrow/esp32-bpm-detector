#!/bin/bash
# Start JTAG debugging session for ESP32-S3 using built-in USB JTAG

LOG_FILE=".cursor/debug.log"
OPENOCD_CFG="openocd.cfg"

echo "Starting JTAG debugging for ESP32-S3..."
echo "USB JTAG device: 303a:1001 (Espressif USB JTAG/serial debug unit)"

# Find OpenOCD - prioritize PlatformIO's ESP32 version
OPENOCD_BIN=""
OPENOCD_SCRIPTS=""

# Try PlatformIO's tool-openocd-esp32 first
if [ -d "$HOME/.platformio/packages/tool-openocd-esp32" ]; then
   OPENOCD_BIN="$HOME/.platformio/packages/tool-openocd-esp32/bin/openocd"
   OPENOCD_SCRIPTS="$HOME/.platformio/packages/tool-openocd-esp32/share/openocd/scripts"
fi

# Fallback to system openocd (will likely fail with ESP32-S3)
if [ -z "$OPENOCD_BIN" ] || [ ! -f "$OPENOCD_BIN" ]; then
   OPENOCD_BIN=$(which openocd)
fi

if [ -z "$OPENOCD_BIN" ] || [ ! -f "$OPENOCD_BIN" ]; then
   echo "Error: OpenOCD not found."
   echo "Please install via: pio pkg install --global --tool tool-openocd-esp32"
   exit 1
fi

echo "Using OpenOCD: $OPENOCD_BIN"

# Set OPENOCD_SCRIPTS environment variable if found
if [ -n "$OPENOCD_SCRIPTS" ]; then
   export OPENOCD_SCRIPTS
   echo "Using scripts from: $OPENOCD_SCRIPTS"
fi

# Clear log file
mkdir -p .cursor
> "$LOG_FILE"

# Check if ESP32-S3 JTAG is connected
if ! lsusb | grep -q "303a:1001"; then
   echo "Warning: ESP32-S3 USB JTAG not detected."
   echo "Expected: ID 303a:1001 Espressif USB JTAG/serial debug unit"
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
echo "   xtensa-esp32s3-elf-gdb -x gdbinit .pio/build/esp32s3/firmware.elf"
echo ""
echo "OpenOCD is running. Press Ctrl+C to stop."

# Wait for interrupt
trap "kill $OPENOCD_PID 2>/dev/null; echo 'Stopped OpenOCD'; exit" INT TERM
wait
