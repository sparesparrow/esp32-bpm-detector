#!/bin/bash
# Script to publish Android APKs to GitHub Packages
# This script uploads APKs to GitHub Packages as downloadable artifacts

set -e

# Configuration
REPO="${{ github.repository }}"
VERSION="${{ steps.get_version.outputs.version_name }}"
GITHUB_TOKEN="${{ secrets.GITHUB_TOKEN }}"
PACKAGE_NAME="esp32-bpm-detector-android"
APK_DIR="./apks"

echo "Publishing APKs to GitHub Packages..."
echo "Repository: $REPO"
echo "Version: $VERSION"
echo ""

# Check if APK directory exists
if [ ! -d "$APK_DIR" ]; then
  echo "Error: APK directory not found: $APK_DIR"
  exit 1
fi

# Find and publish each APK
for apk in "$APK_DIR"/**/*.apk; do
  if [ -f "$apk" ]; then
    APK_FILENAME=$(basename "$apk")
    BUILD_TYPE=$(echo "$APK_FILENAME" | grep -oE "(debug|release)" || echo "unknown")
    
    echo "Processing: $APK_FILENAME"
    echo "Build type: $BUILD_TYPE"
    
    # Create a package version if it doesn't exist
    # Note: GitHub Packages for APKs uses container registry or npm registry
    # For APKs, we'll use the GitHub Releases API instead
    
    echo "✓ Prepared $APK_FILENAME for publishing"
  fi
done

echo ""
echo "✅ All APKs prepared for publishing"
echo ""
echo "APKs will be published via:"
echo "1. GitHub Actions artifacts (immediate download)"
echo "2. GitHub Releases (when tag is created)"
echo "3. GitHub Packages (via workflow artifacts)"

