# GitHub Packages Publishing Guide

## Overview

The ESP32 BPM Detector Android app is automatically built and published to GitHub Packages on every push to `main` or `release/*` branches, and when tags are created.

## Accessing Published APKs

### Method 1: Workflow Artifacts (Recommended)

1. Go to the [Actions](https://github.com/sparesparrow/esp32-bpm-detector/actions) tab
2. Click on the latest successful workflow run
3. Scroll down to the "Artifacts" section
4. Download the `bpm-detector-package-*` artifact
5. Extract the ZIP file to get the APK files

**Retention**: 90 days

### Method 2: GitHub Releases

When a tag is created (e.g., `v1.0.0`), the workflow automatically creates a GitHub Release with APKs attached.

1. Go to the [Releases](https://github.com/sparesparrow/esp32-bpm-detector/releases) page
2. Click on the latest release
3. Download the APK files from the "Assets" section

**Benefits**:
- Permanent storage
- Release notes included
- Easy to share with users

### Method 3: Direct Download from Workflow

1. Navigate to the workflow run
2. Click on the "publish-packages" job
3. Download artifacts from the job summary

## Package Information

### Version Format

- **Version Name**: From `app/build.gradle` (e.g., `1.0.0`)
- **Build Number**: From `app/build.gradle` (e.g., `1`)
- **Package Version**: `{version_name}-{run_number}` (e.g., `1.0.0-123`)

### APK Types

- **Debug APK**: For testing and development
  - Includes debug symbols
  - Allows debugging
  - Larger file size
  
- **Release APK**: Production-ready build
  - Optimized and minified
  - Smaller file size
  - Recommended for end users

## Installation Instructions

### For End Users

1. **Download the APK** from GitHub Releases or workflow artifacts
2. **Enable Unknown Sources**:
   - Go to Settings → Security (or Apps)
   - Enable "Install from unknown sources" or "Allow from this source"
3. **Install the APK**:
   - Tap the downloaded APK file
   - Follow the installation prompts
   - Grant necessary permissions

### For Developers

1. Download the debug APK for testing
2. Install via ADB:
   ```bash
   adb install app-debug.apk
   ```
3. Or use Android Studio to install directly

## Package Metadata

Each build includes metadata in `package-info.json`:

```json
{
  "name": "esp32-bpm-detector-android",
  "version": "1.0.0-123",
  "description": "ESP32 BPM Detector Android Application",
  "repository": "sparesparrow/esp32-bpm-detector",
  "package_type": "android-apk",
  "build_number": "1",
  "commit_sha": "abc123...",
  "branch": "main",
  "build_date": "2025-01-23T12:00:00Z",
  "workflow_run": "123456789"
}
```

## Workflow Triggers

The publishing workflow runs automatically on:

- ✅ Push to `main` branch
- ✅ Push to `release/*` branches
- ✅ Tag creation (creates GitHub Release)
- ✅ Manual workflow dispatch
- ❌ Pull requests (builds only, no publishing)

## CI/CD Pipeline

```
┌─────────────────┐
│  Code Push      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Build APKs     │
│  (Debug/Release)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Run Tests      │
│  Security Scan  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Publish to     │
│  GitHub Packages│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Create Release │
│  (if tagged)    │
└─────────────────┘
```

## Troubleshooting

### APK Not Available

- Check if the workflow completed successfully
- Verify you're looking at the correct branch/tag
- Check artifact retention period (90 days)

### Installation Fails

- Ensure "Unknown sources" is enabled
- Check Android version compatibility (API 24+)
- Verify APK file integrity (re-download if needed)

### Can't Find Release

- Releases are only created when tags are pushed
- Check the [Releases](https://github.com/sparesparrow/esp32-bpm-detector/releases) page
- Verify the tag format (e.g., `v1.0.0`)

## Security

- All APKs are built in a clean CI environment
- Security scans are performed on each build
- No sensitive data is included in APKs
- Signing keys are managed securely (when configured)

## Permissions Required

The workflow requires the following GitHub permissions:
- `contents: write` - To create releases
- `packages: write` - To publish packages
- `security-events: write` - To upload security scan results

## Related Documentation

- [GitHub Packages Documentation](https://docs.github.com/en/packages)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Android App Documentation](../android-app/README.md)
- [Main Project README](../README.md)
