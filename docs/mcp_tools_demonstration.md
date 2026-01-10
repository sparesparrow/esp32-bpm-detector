# Unified Development Tools MCP Server - Demonstration

## Overview

This document demonstrates the capabilities of the Unified Development Tools MCP server for ESP32 BPM Detector development, including ESP32 serial monitor functionality and device detection.

## Available MCP Servers

Based on the project configuration, the following MCP servers should be available:

### 1. `esp32-serial-monitor`
**Purpose**: Device detection, serial I/O, log capture

**Key Tools**:
- `start_serial_monitor` - Start real-time serial monitoring
  - Parameters: `port`, `baud_rate` (default: 115200)
  - Features: Background log storage, pattern matching for errors

### 2. `unified-deployment`
**Purpose**: Multi-device deployment coordination and device detection

**Key Tools**:
- `detect_devices` - Identify connected platforms (ESP32, Arduino)
  - Returns: Device manifest with ports, types, PIO environments, Conan profiles
- `deploy` - Deploy firmware to devices
  - Parameters: Device selection, build environment
- `list_profiles` - Manage Conan profiles
- `start_hardware_emulator` - Start TCP/IP hardware emulator
  - Parameters: `host` (default: 127.0.0.1), `port` (default: 12345), `device_type`
- `get_emulator_status` - Check if emulator is running
- `send_emulator_command` - Send commands to emulator (GET_BPM, GET_STATUS, etc.)
- `run_docker_tests` - Execute Docker-based integration tests
- `build_test_containers` - Build Docker test containers
- `start_test_environment` - Start Docker test environment

### 3. `composed-embedded`
**Purpose**: Combined embedded development capabilities

### 4. `conan-cloudsmith`
**Purpose**: Package management with Cloudsmith

### 5. `android-dev-tools`
**Purpose**: APK building, ADB operations, device management

## ESP32 Serial Monitor Functionality

### Device Detection

The device detection system identifies connected USB serial devices and maps them to:
- Device types (ESP32, ESP32-S3, Arduino Uno)
- PlatformIO environments
- Conan profiles
- Recommended baud rates

**Example Device Manifest**:
```json
{
  "devices": [
    {
      "port": "/dev/ttyACM0",
      "type": "esp32s3",
      "description": "USB JTAG/serial debug unit",
      "pio_env": "esp32s3",
      "conan_profile": "esp32s3",
      "baud_rate": 115200
    }
  ],
  "jtag_devices": []
}
```

### Serial Monitor Features

1. **Real-time Logging**
   - Continuous serial output capture
   - Configurable baud rate (typically 115200 for ESP32)
   - UTF-8 decoding with error handling

2. **Background Log Storage**
   - Logs written to file while monitoring
   - NDJSON format for structured logs
   - Pattern matching for debug entries

3. **Error Pattern Matching**
   - Automatic detection of error messages
   - Highlighting of critical issues
   - Log filtering capabilities

### Serial Monitor Scripts

**`capture_serial_debug.py`**:
- Captures serial output from ESP32
- Extracts NDJSON debug logs
- Writes to `/home/sparrow/projects/.cursor/debug.log`
- Usage: `python3 capture_serial_debug.py [PORT] [BAUD_RATE]`

**`capture_serial.py`**:
- General-purpose serial capture
- Configurable output destination

## Hardware Emulator

The hardware emulator provides TCP/IP-based device simulation for testing without physical hardware.

### Emulator Commands

- `GET_BPM` - Get current BPM reading with confidence/signal data
- `GET_STATUS` - Device status, uptime, connection info
- `GET_SENSORS` - Available sensors (microphone, accelerometer, etc.)
- `SET_CONFIG` - Configure detection parameters
- `PING` - Basic connectivity test
- `RESET` - Device reset simulation

### Emulator Usage

```bash
# Start emulator via MCP
unified-deployment.start_hardware_emulator

# Check emulator status
unified-deployment.get_emulator_status

# Send custom commands
unified-deployment.send_emulator_command GET_STATUS
```

## Testing Workflow

### 1. Device Detection
```python
# Via MCP tool
devices = unified-deployment.detect_devices()

# Or via script
python3 scripts/detect_devices.py --json
```

### 2. Serial Monitoring
```python
# Via MCP tool
esp32-serial-monitor.start_serial_monitor(
    port="/dev/ttyACM0",
    baud_rate=115200
)

# Or via script
python3 capture_serial_debug.py /dev/ttyACM0 115200
```

### 3. Hardware Emulation Testing
```python
# Start emulator
unified-deployment.start_hardware_emulator(
    host="127.0.0.1",
    port=12345,
    device_type="esp32s3"
)

# Run tests against emulator
python3 run_tests.py --emulator
```

## Current MCP Configuration

The MCP configuration is located at `.claude/mcp.json`. Currently configured:

```json
{
  "mcpServers": {
    "prompts": {
      "command": "mcp-prompts",
      "args": ["--storage", "file", "--path", "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts"]
    }
  }
}
```

**Note**: The following servers are expected but may need to be added to the configuration:
- `esp32-serial-monitor`
- `unified-deployment`
- `composed-embedded`
- `conan-cloudsmith`
- `android-dev-tools`

## Test Script

A comprehensive test script (`test_mcp_tools.py`) has been created to demonstrate:

1. ✅ Device detection functionality
2. ✅ Serial port listing
3. ✅ Hardware emulator status checking
4. ✅ Serial monitor capabilities verification
5. ✅ MCP configuration validation

Run the test script:
```bash
python3 test_mcp_tools.py
```

## Expected Output

The test script generates:
- Console output with test results
- JSON test report in `test_results/mcp_tools_test_*.json`
- Summary of available capabilities
- Status of MCP server configuration

## Next Steps

1. **Configure MCP Servers**: Add the unified-deployment and esp32-serial-monitor servers to `.claude/mcp.json`
2. **Test Device Detection**: Run device detection with physical devices connected
3. **Test Serial Monitor**: Start serial monitoring on a connected ESP32 device
4. **Test Emulator**: Start hardware emulator and run tests against it
5. **Integration**: Integrate MCP tools into development workflow

## References

- Project rules: `.cursor/rules/embedded-dev.mdc`
- Device detection script: `scripts/detect_devices.py`
- Serial capture script: `capture_serial_debug.py`
- Hardware emulator: `scripts/start_emulator.py`
- Docker test runner: `scripts/docker_test_runner.py`
