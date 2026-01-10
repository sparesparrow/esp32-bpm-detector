#!/bin/bash

# BPM Detector Android UI Test Runner
# Runs UI Automator tests on connected Android device

set -e

echo "🎯 BPM Detector UI Test Runner"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if device is connected
echo "📱 Checking for connected Android device..."
if ! adb devices | grep -q "device$"; then
    echo -e "${RED}❌ No Android device connected!${NC}"
    echo "Please connect an Android device or start an emulator:"
    echo "  - Physical device: Connect via USB"
    echo "  - Emulator: Run 'emulator -avd <avd_name>'"
    exit 1
fi

echo -e "${GREEN}✅ Android device detected${NC}"

# Get device info
DEVICE_INFO=$(adb shell getprop ro.product.model)
echo "📱 Device: $DEVICE_INFO"

ANDROID_VERSION=$(adb shell getprop ro.build.version.release)
echo "🤖 Android Version: $ANDROID_VERSION"

# Check if app is installed, install if needed
echo "📦 Checking if BPM Detector app is installed..."
PACKAGE_NAME="com.sparesparrow.bpmdetector.debug"

if ! adb shell pm list packages | grep -q "$PACKAGE_NAME"; then
    echo -e "${YELLOW}⚠️  App not installed, building and installing...${NC}"

    # Build the app
    echo "🔨 Building debug APK..."
    ./gradlew assembleDebug

    # Install the app
    echo "📲 Installing APK..."
    adb install -r app/build/outputs/apk/debug/app-debug.apk

    echo -e "${GREEN}✅ App installed successfully${NC}"
else
    echo -e "${GREEN}✅ App already installed${NC}"
fi

# Grant necessary permissions
echo "🔐 Granting permissions..."
adb shell pm grant $PACKAGE_NAME android.permission.RECORD_AUDIO 2>/dev/null || true
adb shell pm grant $PACKAGE_NAME android.permission.ACCESS_FINE_LOCATION 2>/dev/null || true
adb shell pm grant $PACKAGE_NAME android.permission.ACCESS_COARSE_LOCATION 2>/dev/null || true

# Run UI tests
echo "🧪 Running UI Automator tests..."
echo "=================================="

# Run the tests
if ./gradlew connectedDebugAndroidTest --continue; then
    echo -e "${GREEN}✅ UI Tests completed successfully!${NC}"
else
    echo -e "${RED}❌ Some UI tests failed${NC}"
    echo "Check the test reports for details:"
    echo "  - HTML Report: app/build/reports/androidTests/connected/index.html"
    echo "  - Test Results: app/build/outputs/androidTest-results/connected/"
    exit 1
fi

# Generate test report
echo "📊 Generating test report..."
if [ -d "app/build/reports/androidTests/connected" ]; then
    echo "📋 Test report available at: app/build/reports/androidTests/connected/index.html"
fi

echo ""
echo -e "${GREEN}🎉 UI Testing Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Review test results and screenshots"
echo "2. Fix any failing tests"
echo "3. Run manual testing on device"
echo "4. Prepare for production deployment"