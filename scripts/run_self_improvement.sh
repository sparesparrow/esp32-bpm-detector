#!/bin/bash
#
# ESP32-Android Self-Improvement Loop Entry Point
# Runs the automated fix-build-deploy-test-analyze cycle
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "============================================================"
echo "  ESP32-Android Self-Improvement Loop"
echo "============================================================"
echo "  Project: $PROJECT_DIR"
echo "  Time:    $(date)"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v pio &> /dev/null; then
    echo "ERROR: PlatformIO not found"
    echo "Install with: pip install platformio"
    exit 1
fi
echo "  ✓ PlatformIO installed"

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found"
    exit 1
fi
echo "  ✓ Python3 installed"

if ! command -v adb &> /dev/null; then
    echo "WARNING: ADB not found - Android testing will be skipped"
else
    echo "  ✓ ADB installed"
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install -q pyserial aiohttp 2>/dev/null || true

# Check for ESP32 device
echo ""
echo "Checking for ESP32 device..."
ESP32_PORT=$(ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null | head -1 || echo "")
if [ -z "$ESP32_PORT" ]; then
    echo "WARNING: No ESP32 device detected"
    echo "  Please connect ESP32 via USB"
else
    echo "  ✓ ESP32 detected at $ESP32_PORT"
fi

# Check for Android device
echo ""
echo "Checking for Android device..."
ANDROID_DEVICE=$(adb devices 2>/dev/null | grep -w "device" | head -1 | cut -f1 || echo "")
if [ -z "$ANDROID_DEVICE" ]; then
    echo "WARNING: No Android device detected"
    echo "  Android testing will be skipped"
else
    echo "  ✓ Android device: $ANDROID_DEVICE"
fi

# Run build state detector first
echo ""
echo "Analyzing build state..."
cd "$PROJECT_DIR"
python3 scripts/detect_build_state.py

# Run the self-improvement loop
echo ""
echo "Starting self-improvement loop..."
echo ""

cd "$SCRIPT_DIR"
python3 self_improvement_loop.py "$@"
EXIT_CODE=$?

# Notify user of result
echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "============================================================"
    echo "  SUCCESS: ESP32-Android connectivity established!"
    echo "============================================================"

    # Voice notification
    espeak "ESP32 Android connectivity test completed successfully" 2>/dev/null &

    # Phone notification
    kdeconnect-cli --ping-msg "ESP32-Android: SUCCESS ✅" 2>/dev/null || true
else
    echo "============================================================"
    echo "  FAILED: ESP32-Android connectivity not established"
    echo "============================================================"

    # Voice notification
    espeak "ESP32 Android connectivity test failed" 2>/dev/null &

    # Phone notification
    kdeconnect-cli --ping-msg "ESP32-Android: FAILED ❌" 2>/dev/null || true
fi

exit $EXIT_CODE
