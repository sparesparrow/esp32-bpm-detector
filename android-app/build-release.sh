#!/bin/bash
# Build release APK for ESP32 BPM Detector

cd "$(dirname "$0")"

echo "Building release APK..."
./gradlew assembleRelease

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Release APK built successfully!"
    echo "Location: app/build/outputs/apk/release/app-release.apk"
    echo ""
    echo "Note: For production, configure signing in app/build.gradle"
else
    echo ""
    echo "✗ Build failed. Check the error messages above."
    exit 1
fi

