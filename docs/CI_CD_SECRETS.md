# CI/CD Secrets Configuration

This document describes the GitHub secrets required for the SpareTools CI/CD pipeline.

## Required Secrets

### CLOUDSMITH_API_KEY

**Purpose:** Authenticate with Cloudsmith for package uploads and downloads.

**How to obtain:**
1. Log in to [Cloudsmith](https://cloudsmith.io)
2. Go to Settings → API Keys
3. Create a new API key with read/write permissions

**Usage:** Used by Conan to upload packages and download dependencies.

### CONAN_TOKEN (Optional)

**Purpose:** Conan remote authentication token for private packages.

**How to obtain:**
1. Generate from Cloudsmith or your Conan remote
2. Use the same value as CLOUDSMITH_API_KEY for Cloudsmith remotes

**Usage:** Alternative authentication for Conan commands.

### HARDWARE_TEST_DEVICES (Optional)

**Purpose:** JSON configuration for hardware test devices on self-hosted runners.

**Format:**
```json
{
  "esp32": {
    "port": "/dev/ttyUSB0",
    "type": "esp32s3",
    "baud_rate": 115200
  },
  "android": {
    "device_id": "DEVICE_SERIAL_NUMBER",
    "package": "com.sparesparrow.bpmdetector"
  }
}
```

**Usage:** Used by integration tests to locate connected hardware.

## Setting Up Secrets

### Via GitHub UI

1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Enter the secret name and value
5. Click "Add secret"

### Via GitHub CLI

```bash
# Set CLOUDSMITH_API_KEY
gh secret set CLOUDSMITH_API_KEY --body "your-api-key-here"

# Set HARDWARE_TEST_DEVICES
gh secret set HARDWARE_TEST_DEVICES --body '{"esp32":{"port":"/dev/ttyUSB0","type":"esp32s3"}}'
```

## Environment Variables

The CI/CD workflow also uses these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `CLOUDSMITH_ORG` | sparesparrow-conan | Cloudsmith organization name |
| `CLOUDSMITH_REPO` | sparetools | Cloudsmith repository name |
| `PIO_ENV` | esp32-s3-release | PlatformIO build environment |

## Self-Hosted Runner Setup

For integration tests with real hardware:

1. Install GitHub Actions runner on a machine with connected devices
2. Configure the runner with label: `self-hosted`
3. Ensure device permissions:
   ```bash
   # ESP32 serial access
   sudo usermod -a -G dialout $USER
   
   # Android ADB access
   sudo usermod -a -G plugdev $USER
   ```

4. Set up udev rules for ESP32:
   ```bash
   # /etc/udev/rules.d/99-esp32.rules
   SUBSYSTEM=="tty", ATTRS{idVendor}=="303a", ATTRS{idProduct}=="1001", MODE="0666"
   SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666"
   SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="0666"
   ```

5. Reload udev rules:
   ```bash
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

## Workflow Dispatch

To manually trigger integration tests:

```bash
# Via GitHub CLI
gh workflow run mcp-integrated-ci.yml \
  --field run_integration_tests=true

# Or use the GitHub UI:
# Actions → SpareTools CI/CD → Run workflow → Check "Run integration tests"
```

## Troubleshooting

### Cloudsmith Authentication Failed

1. Verify API key is valid and not expired
2. Check Cloudsmith organization and repository names
3. Ensure API key has correct permissions

### Integration Tests Not Running

1. Verify self-hosted runner is online
2. Check device connections
3. Verify HARDWARE_TEST_DEVICES secret format

### Build Cache Issues

Clear the cache by:
1. Go to Actions → Caches
2. Delete cache entries starting with `conan-` or `pio-`
