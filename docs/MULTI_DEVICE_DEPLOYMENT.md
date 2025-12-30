# Multi-Device Deployment Guide

## Overview

The ESP32 BPM Detector supports simultaneous deployment to multiple heterogeneous embedded devices using Conan profiles for cross-platform build management. This guide covers deploying firmware to:

- **ESP32-S3 DevKitC** (with USB CDC and JTAG debugging)
- **Generic ESP32** (ESP32-WROOM-32 with CH340/CP210x USB-Serial)
- **Arduino Uno** (with limited features due to memory constraints)

## Architecture

### Device Detection

The system uses `scripts/detect_devices.py` to automatically detect all connected devices by analyzing:

- USB VID:PID identifiers
- Device descriptions
- Port names and hardware IDs

Supported USB-serial chips:
- **CH340/CH341**: Common on ESP32 and Arduino boards
- **CP210x**: Silicon Labs USB-to-UART (some ESP32 boards)
- **FTDI**: Common Arduino converters
- **Native CDC ACM**: ESP32-S3 USB OTG

### Conan Profiles

Each target device has a dedicated Conan profile in `conan-profiles/`:

1. **esp32s3.profile**: ESP32-S3 with full features (display, networking, FlatBuffers)
2. **esp32.profile**: Generic ESP32 with networking but no display
3. **arduino_uno.profile**: Arduino Uno with minimal features (no FlatBuffers, no networking)

Profiles configure:
- Cross-compilation toolchains
- Target-specific compiler flags
- Feature toggles (display, networking, websocket, etc.)
- Build types and optimizations

### Build & Deployment Pipeline

1. **Device Detection**: Scan USB ports and identify connected devices
2. **Profile Selection**: Map each device to its Conan profile
3. **Dependency Installation**: Run `conan install` with target profile
4. **Firmware Build**: Use PlatformIO to build for each environment
5. **Upload**: Flash firmware to each device via serial port
6. **Monitoring**: (Optional) Monitor serial output to verify operation

## Quick Start

### 1. Detect Connected Devices

```bash
cd /home/sparrow/projects/embedded-systems/esp32-bpm-detector
python3 scripts/detect_devices.py
```

**Example output:**
```
============================================================
ESP32 BPM Detector - Device Detection
============================================================

📱 Found 2 programmable device(s):

  1. ESP32S3
     Port: /dev/ttyACM0
     Description: ESP32-S3 USB CDC
     PIO Environment: esp32s3
     Conan Profile: esp32s3
     Baud Rate: 115200

  2. ESP32
     Port: /dev/ttyUSB0
     Description: USB2.0-Serial
     PIO Environment: esp32dev-release
     Conan Profile: esp32
     Baud Rate: 115200

🔧 Found 1 JTAG device(s):
  - esp32s3_jtag on /dev/ttyACM1

============================================================
```

### 2. Deploy to All Devices

**Sequential deployment (recommended for first-time setup):**
```bash
python3 scripts/deploy_all_devices.py --mode sequential --monitor --monitor-duration 15
```

**Parallel deployment (faster for multiple devices):**
```bash
python3 scripts/deploy_all_devices.py --mode parallel
```

### 3. Dry Run (Test without deploying)

```bash
python3 scripts/deploy_all_devices.py --dry-run
```

## Command-Line Options

### deploy_all_devices.py

| Option | Description | Default |
|--------|-------------|---------|
| `--mode sequential` | Deploy to devices one at a time | sequential |
| `--mode parallel` | Deploy to devices simultaneously | - |
| `--monitor` | Monitor serial output after upload | false |
| `--monitor-duration N` | Monitor each device for N seconds | 10 |
| `--filter TYPE [TYPE...]` | Deploy only to specific device types | all |
| `--dry-run` | Show what would be deployed without deploying | false |

**Examples:**

```bash
# Deploy only to ESP32 devices (skip Arduino)
python3 scripts/deploy_all_devices.py --filter esp32s3 esp32

# Deploy to Arduino Uno only
python3 scripts/deploy_all_devices.py --filter arduino_uno

# Monitor all devices for 30 seconds after upload
python3 scripts/deploy_all_devices.py --monitor --monitor-duration 30
```

## Single-Device Deployment

### Using Conan Profile

```bash
# Install dependencies for ESP32-S3
python3 scripts/conan_install.py --profile esp32s3

# Build firmware
pio run --environment esp32s3

# Upload to specific port
pio run --environment esp32s3 --target upload --upload-port /dev/ttyACM0
```

### Without Conan (PlatformIO only)

```bash
# Build and upload in one command
pio run --environment esp32s3 --target upload --upload-port /dev/ttyACM0

# Monitor serial output
pio device monitor --port /dev/ttyACM0 --baud 115200
```

## Device-Specific Configurations

### ESP32-S3

**Features:**
- ✅ Full FlatBuffers protocol support
- ✅ WiFi networking and REST API
- ✅ WebSocket support
- ✅ OLED display (SSD1306)
- ✅ Audio calibration
- ✅ JTAG debugging via USB

**Conan Profile:** `conan-profiles/esp32s3.profile`

**PlatformIO Environment:** `esp32s3`

**Upload Port:** Typically `/dev/ttyACM0` (Linux) or `COM3` (Windows)

**Baud Rate:** 115200

### Generic ESP32 (ESP32-WROOM-32)

**Features:**
- ✅ FlatBuffers protocol support
- ✅ WiFi networking and REST API
- ✅ WebSocket support
- ❌ No display (disabled to save memory)
- ❌ No audio calibration

**Conan Profile:** `conan-profiles/esp32.profile`

**PlatformIO Environment:** `esp32dev-release`

**Upload Port:** Typically `/dev/ttyUSB0` (Linux with CH340) or `COM4` (Windows)

**Baud Rate:** 115200

### Arduino Uno

**Features:**
- ❌ No FlatBuffers (exceeds 32KB flash limit)
- ❌ No WiFi networking
- ❌ No WebSocket
- ❌ No display
- ✅ Basic BPM detection only

**Conan Profile:** `conan-profiles/arduino_uno.profile`

**PlatformIO Environment:** `arduino_uno`

**Upload Port:** Typically `/dev/ttyUSB1` or `/dev/ttyACM1` (Linux with FTDI) or `COM5` (Windows)

**Baud Rate:** 9600

**Memory Constraints:**
- Flash: 32KB (30KB usable after bootloader)
- RAM: 2KB (1.5KB available after Arduino framework)

## Troubleshooting

### Device Not Detected

**Symptoms:**
- `scripts/detect_devices.py` reports "No devices detected"

**Solutions:**
1. Check USB cable connection (data cables, not just power)
2. Verify drivers are installed:
   - **CH340**: Install CH340 driver for Windows/macOS
   - **CP210x**: Install Silicon Labs driver
   - **FTDI**: Usually auto-detected on modern systems
3. Check device permissions on Linux:
   ```bash
   sudo usermod -a -G dialout $USER
   # Log out and log back in
   ```
4. Try a different USB port or hub

### Build Fails for Specific Profile

**Symptoms:**
- Conan install succeeds but PlatformIO build fails

**Solutions:**
1. Verify toolchain is installed:
   - **ESP32**: PlatformIO automatically installs `espressif32` platform
   - **Arduino**: PlatformIO automatically installs `atmelavr` platform
2. Check profile-specific headers:
   ```bash
   ls conan-headers-esp32s3/  # Should contain generated headers
   ```
3. Clean and rebuild:
   ```bash
   pio run --target clean
   python3 scripts/conan_install.py --profile esp32s3
   pio run --environment esp32s3
   ```

### Upload Fails

**Symptoms:**
- Build succeeds but upload to device fails

**Solutions:**
1. Verify correct port:
   ```bash
   python3 scripts/detect_devices.py
   ```
2. Check device is not in use by another process:
   ```bash
   # Linux
   lsof | grep ttyUSB0
   
   # Kill any monitoring processes
   pkill -f "pio device monitor"
   ```
3. Try manual upload with explicit port:
   ```bash
   pio run --environment esp32s3 --target upload --upload-port /dev/ttyACM0
   ```
4. Reset device manually before upload (press reset button)

### Arduino Uno: Sketch Too Big

**Symptoms:**
- Error: "Sketch too big" or "text section exceeds available space"

**Solutions:**
1. Verify Arduino profile is being used:
   ```bash
   python3 scripts/conan_install.py --profile arduino_uno
   ```
2. Ensure FlatBuffers generation is skipped (automatic in `conanfile.py`)
3. Reduce code size:
   - Remove debug prints
   - Disable unused features in `config.h`
   - Use `PROGMEM` for constant strings

### Parallel Upload Conflicts

**Symptoms:**
- Some devices upload successfully, others fail randomly

**Solutions:**
1. Use sequential mode instead:
   ```bash
   python3 scripts/deploy_all_devices.py --mode sequential
   ```
2. Check USB hub bandwidth (use powered hub for 3+ devices)
3. Avoid uploading to devices on same USB controller simultaneously

### JTAG Connection Issues (ESP32-S3)

**Symptoms:**
- JTAG device detected but OpenOCD connection fails

**Solutions:**
1. Verify ESP32-S3 USB bridge is in JTAG mode (not just serial CDC)
2. Install OpenOCD ESP32 support:
   ```bash
   # Linux
   sudo apt install openocd
   
   # Verify ESP32 support
   openocd -f board/esp32s3-builtin.cfg
   ```
3. Use dedicated JTAG deployment script:
   ```bash
   python3 scripts/deploy_with_jtag.py --device esp32s3 --debug
   ```

## Advanced Usage

### Custom Conan Profiles

Create custom profiles for specific hardware configurations:

```bash
# Copy existing profile
cp conan-profiles/esp32s3.profile conan-profiles/esp32s3-custom.profile

# Edit profile
nano conan-profiles/esp32s3-custom.profile
```

Example customization:
```ini
[options]
sparetools-bpm-detector/*:target_board=esp32s3
sparetools-bpm-detector/*:with_display=True
sparetools-bpm-detector/*:with_networking=True
sparetools-bpm-detector/*:with_websocket=False  # Disable WebSocket
sparetools-bpm-detector/*:with_audio_calibration=True
```

Use custom profile:
```bash
python3 scripts/conan_install.py --profile esp32s3-custom
pio run --environment esp32s3
```

### Automated CI/CD Deployment

Integrate multi-device deployment into CI/CD pipelines:

```yaml
# .github/workflows/deploy-devices.yml
name: Deploy to Devices

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: self-hosted  # Runner with connected devices
    steps:
      - uses: actions/checkout@v3
      
      - name: Detect devices
        run: python3 scripts/detect_devices.py --output device_manifest.json
      
      - name: Deploy firmware
        run: python3 scripts/deploy_all_devices.py --mode sequential
      
      - name: Upload deployment logs
        uses: actions/upload-artifact@v3
        with:
          name: deployment-logs
          path: |
            device_manifest.json
            .pio/build/*/output.log
```

### Monitoring Multiple Devices

Monitor all devices simultaneously using GNU Screen or tmux:

```bash
# Create screen session with multiple windows
screen -dmS bpm-monitor

# Attach to ESP32-S3
screen -S bpm-monitor -X screen -t esp32s3 pio device monitor --port /dev/ttyACM0 --baud 115200

# Attach to ESP32
screen -S bpm-monitor -X screen -t esp32 pio device monitor --port /dev/ttyUSB0 --baud 115200

# Attach to Arduino
screen -S bpm-monitor -X screen -t arduino pio device monitor --port /dev/ttyUSB1 --baud 9600

# Connect to session
screen -r bpm-monitor
# Use Ctrl+A then number to switch between windows
```

## Best Practices

1. **Sequential First, Parallel Later**: Use sequential mode for initial deployment to verify each device works independently

2. **Powered USB Hub**: Use a powered USB hub when deploying to 3+ devices to avoid power issues

3. **Unique Labels**: Label each device with its type and port for easy identification

4. **Version Control**: Keep device manifests in version control to track hardware inventory

5. **Incremental Deployment**: For large fleets, deploy to a subset first (using `--filter`) before full deployment

6. **Monitor After Upload**: Always use `--monitor` flag for first deployment to verify boot messages

7. **Clean Builds**: Run `pio run --target clean` between profile switches to avoid cross-contamination

## Adding New Device Types

To add support for a new device type (e.g., ESP32-C3):

### 1. Create Conan Profile

```bash
# Create profile
cat > conan-profiles/esp32c3.profile << 'EOF'
[settings]
os=Linux
arch=riscv32
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
build_type=Release

[buildenv]
CC=riscv32-esp-elf-gcc
CXX=riscv32-esp-elf-g++
AR=riscv32-esp-elf-ar
RANLIB=riscv32-esp-elf-ranlib

[conf]
tools.build:compiler_executables={"c": "riscv32-esp-elf-gcc", "cpp": "riscv32-esp-elf-g++"}
tools.cmake.cmaketoolchain:generator=Ninja

[options]
sparetools-bpm-detector/*:target_board=esp32c3
sparetools-bpm-detector/*:with_display=False
sparetools-bpm-detector/*:with_networking=True
sparetools-bpm-detector/*:with_websocket=True
sparetools-bpm-detector/*:with_audio_calibration=False
EOF
```

### 2. Update Device Detection

Edit `scripts/detect_devices.py`:

```python
# Add detection keywords
ESP32_C3_KEYWORDS = ['ESP32-C3', 'ESP32C3', 'RISC-V']

# Update identify_device_type() function
def identify_device_type(port):
    description = port.description.upper()
    
    # Add ESP32-C3 detection
    if any(keyword in description for keyword in ESP32_C3_KEYWORDS):
        return {
            "port": port.device,
            "type": "esp32c3",
            "description": port.description,
            "pio_env": "esp32c3",
            "conan_profile": "esp32c3",
            "baud_rate": 115200,
            "vid_pid": get_vid_pid(port),
            "is_jtag": False
        }
    # ... rest of function
```

### 3. Update PlatformIO Configuration

Add environment to `platformio.ini`:

```ini
[env:esp32c3]
platform = espressif32@6.4.0
board = esp32-c3-devkitm-1
framework = arduino
monitor_speed = 115200
upload_speed = 921600
; upload_port can be specified via CLI
build_flags =
    -D CORE_DEBUG_LEVEL=2
    -D PLATFORM_ESP32
    -std=c++17
```

### 4. Update Deployment Script

Edit `scripts/deploy_all_devices.py`:

```python
# Add profile mapping
profile_to_env = {
    "esp32s3": "esp32s3",
    "esp32": "esp32dev-release",
    "esp32c3": "esp32c3",  # Add this line
    "arduino_uno": "arduino_uno"
}
```

### 5. Test New Device

```bash
# Detect new device
python3 scripts/detect_devices.py

# Deploy to new device type
python3 scripts/deploy_all_devices.py --filter esp32c3 --monitor
```

## Performance Optimization

### Build Time

- **Parallel builds**: Use `pio run -j4` for multi-core builds
- **Incremental builds**: Avoid `clean` unless necessary
- **Conan cache**: Reuse dependencies across profiles when possible

### Upload Time

- **Baud rate**: Increase `upload_speed` in `platformio.ini` for faster uploads (ESP32 supports up to 921600)
- **Parallel uploads**: Use `--mode parallel` for non-shared USB controllers
- **Skip verification**: Add `--upload-flags --no-verify` (not recommended for production)

## Security Considerations

1. **WiFi Credentials**: Never hardcode WiFi passwords in firmware
2. **Serial Access**: Restrict physical access to device serial ports
3. **Firmware Signing**: Consider enabling ESP32 secure boot for production
4. **Update Mechanism**: Implement OTA (Over-The-Air) updates for deployed devices

## Support

For issues with multi-device deployment:

1. Check this documentation
2. Review [TROUBLESHOOTING.md](troubleshooting_guide.md)
3. Open an issue on [GitHub](https://github.com/sparesparrow/esp32-bpm-detector/issues)

## References

- [Conan Documentation](https://docs.conan.io/)
- [PlatformIO Multi-Environment Builds](https://docs.platformio.org/en/latest/projectconf/section_platformio.html)
- [ESP32 USB Serial/JTAG](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-guides/usb-serial-jtag-console.html)

---

**Last Updated**: December 2025  
**Version**: 1.0.0
