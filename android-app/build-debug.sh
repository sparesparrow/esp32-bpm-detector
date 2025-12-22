#!/bin/bash
# Build debug APK for ESP32 BPM Detector

cd "$(dirname "$0")"

echo "Building debug APK..."
./gradlew assembleDebug

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Debug APK built successfully!"
    echo "Location: app/build/outputs/apk/debug/app-debug.apk"
else
    echo ""
    echo "✗ Build failed. Check the error messages above."
    exit 1
fi
