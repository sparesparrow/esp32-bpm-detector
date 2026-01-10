# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ESP32 BPM Detector - A real-time BPM (Beats Per Minute) detection system using ESP32 microcontroller with FlatBuffers protocol, cross-platform deployment support, and companion Android app.

**Key Technologies:**
- ESP32-S3/ESP32 firmware (C++17, Arduino framework)
- FlatBuffers for protocol definitions
- PlatformIO for embedded builds
- Conan package management with Cloudsmith integration
- Android app (Kotlin, Gradle)
- Hardware emulation and Docker-based testing

## Build System

### Firmware Build (PlatformIO)

**ESP32-S3 (default):**
```bash
pio run --environment esp32s3
pio run --environment esp32s3 --target upload --upload-port /dev/ttyACM0
pio device monitor --port /dev/ttyACM0
```

**ESP32 (generic):**
```bash
pio run --environment esp32dev-release
pio run --environment esp32dev-debug  # With debug symbols
```

**Arduino Uno (display client only):**
```bash
pio run --environment arduino_uno_display
```

### Multi-Device Deployment

Deploy to multiple devices simultaneously:
```bash
# Detect all connected devices
python3 scripts/detect_devices.py

# Deploy to all devices with monitoring
python3 scripts/deploy_all_devices.py --mode sequential --monitor

# Deploy to specific device types only
python3 scripts/deploy_all_devices.py --filter esp32s3 esp32

# Dry run to preview
python3 scripts/deploy_all_devices.py --dry-run
```

### Conan Package Management

```bash
# Install dependencies (with Cloudsmith remote)
conan install . --build=missing -r sparetools

# Generate FlatBuffers headers via Conan
python scripts/generate_flatbuffers.py

# Build with specific profile
python3 scripts/conan_install.py --profile esp32s3
```

### Testing

**Native C++ Tests:**
```bash
make test              # Build and run all tests
python3 run_tests.py   # Cross-platform test runner
```

**Hardware Emulation Tests (no physical devices):**
```bash
python3 run_tests.py --emulator
python3 run_tests.py --emulator --emulator-host 127.0.0.1 --emulator-port 12345
```

**Docker-based Integration Tests:**
```bash
python3 run_tests.py --docker
python3 scripts/docker_test_runner.py --suite all
docker-compose up integration-tests
```

**Android App Tests:**
```bash
cd android-app
./gradlew test                     # Unit tests
./gradlew connectedAndroidTest     # Integration tests
```

## Architecture

### OMS Application Framework

The firmware uses a custom OMS (Object Management System) application framework with initialization steps:

**Core Components:**
- `BpmApplication` - Main application orchestrator
- `Application` base class - Framework foundation
- `InitStep` - Component initialization pattern
- `LogManager` - Structured logging system
- `ApplicationStateManager` - State machine management
- `JobWorker` - Background job processing

**Initialization Steps (order matters):**
1. `LogManagerInitStep` - Initialize logging subsystem
2. `ApplicationStateManagerInitStep` - State management setup
3. `JobWorkerInitStep` - Background job processing
4. `PlatformInitStep` - Platform abstraction layer (ESP32/Arduino)
5. `SerialInitStep` - Serial communication
6. `BpmDetectorInitStep` - BPM detection algorithm
7. `MonitorManagerInitStep` - Monitor management
8. `MessageProcessorInitStep` - FlatBuffers message processing

### Platform Abstraction

**Interface Layer (`src/interfaces/`):**
- `IPlatform` - Platform abstraction
- `IAudioInput` - Audio sampling interface
- `IDisplayHandler` - Display output
- `ISerial` - Serial communication
- `ITimer` - Timing functions
- `IBpmMonitor` - BPM monitoring

**Platform Implementations (`src/platforms/`):**
- `ESP32Platform` - ESP32-specific implementation
- `ESP32AudioInput` - I2S/ADC audio input
- `ESP32DisplayHandler` - OLED display support
- `ESP32Serial` / `ESP32Timer` - Hardware abstractions
- `ArduinoPlatform` - Arduino Uno support (limited)
- `PlatformFactory` - Factory pattern for platform creation

### FlatBuffers Protocol

**Schema Files (`schemas/`):**
- `BpmCommon.fbs` - Shared types, enums (DetectionStatus, RequestType, MonitorParameterType)
- `BpmRequests.fbs` - Request messages
- `BpmResponses.fbs` - Response messages
- `BpmConfig.fbs` - Configuration messages
- `BpmSystem.fbs` - System messages
- `BpmAudio.fbs` - Audio data structures
- `BpmCore.fbs` - Core protocol definitions
- `BpmProtocol.fbs` - Top-level protocol

**Generated Headers (`include/`):**
- `*_generated.h` - FlatBuffers-generated C++ headers
- `*_extracted.h` - Extracted enums for cross-file usage

**Protocol Implementation:**
- `bpm_flatbuffers.cpp/.h` - FlatBuffers helpers
- `bpm_monitor_flatbuffers.cpp/.h` - Monitor-specific FlatBuffers
- `bpm_monitor_msg_processor.cpp/.h` - Message processing logic

### BPM Detection Algorithm

**Key Files:**
- `src/bpm_detector.cpp/.h` - Core BPM detection using FFT/envelope analysis
- `src/audio_input.cpp/.h` - Audio sampling and preprocessing
- `src/bpm_detector_adapter.cpp/.h` - Adapter pattern for BPM detector
- `src/config.h` - Detection parameters (SAMPLE_RATE, FFT_SIZE, MIN_BPM, MAX_BPM)

**Detection Parameters:**
- Sample rate: 25kHz (configurable)
- FFT size: 1024 samples
- BPM range: 60-200 BPM
- Uses envelope-based detection with adaptive threshold

### Directory Structure

```
esp32-bpm-detector/
├── src/                          # Firmware source
│   ├── main.cpp                  # Entry point (FreeRTOS task setup)
│   ├── BpmApplication.cpp/.h     # OMS application
│   ├── config.h                  # Configuration constants
│   ├── bpm_detector.*            # BPM detection algorithm
│   ├── bpm_monitor_*             # Monitor management
│   ├── interfaces/               # Platform abstraction interfaces
│   ├── platforms/                # Platform implementations
│   │   ├── esp32/               # ESP32 platform
│   │   ├── arduino/             # Arduino platform
│   │   └── factory/             # Factory pattern
│   ├── shared/                   # OMS framework shared code
│   ├── initialization/           # Init steps
│   ├── logging/                  # Logging system
│   └── job/                      # Background job processing
├── include/                      # Generated FlatBuffers headers
├── schemas/                      # FlatBuffers schema definitions
├── scripts/                      # Python automation tools
├── tests/                        # Test files
│   └── integration/              # Integration tests
├── android-app/                  # Companion Android app
├── docs/                         # Documentation
└── platformio.ini                # PlatformIO configuration
```

## Development Workflow

### Typical Development Cycle

1. **Modify firmware code** in `src/`
2. **Regenerate FlatBuffers if schemas changed:**
   ```bash
   python scripts/generate_flatbuffers.py
   ```
3. **Build for target platform:**
   ```bash
   pio run --environment esp32s3
   ```
4. **Upload to device:**
   ```bash
   pio run --environment esp32s3 --target upload --upload-port /dev/ttyACM0
   ```
5. **Monitor serial output:**
   ```bash
   pio device monitor --port /dev/ttyACM0
   ```

### Testing Workflow

1. **Run native C++ tests first:**
   ```bash
   make test
   ```
2. **Test with hardware emulation:**
   ```bash
   python3 run_tests.py --emulator
   ```
3. **Run Docker integration tests:**
   ```bash
   python3 scripts/docker_test_runner.py --suite all
   ```
4. **Deploy to physical device and test:**
   ```bash
   python3 scripts/deploy_all_devices.py --mode sequential --monitor
   ```

### Debugging

**JTAG Debugging (ESP32-S3):**
```bash
./scripts/deploy_with_jtag.py
./start_jtag_debug.sh
```

**Serial Debugging:**
```bash
pio device monitor --port /dev/ttyACM0 --baud 115200
./capture_serial_logs.sh  # Capture logs to file
```

**Hardware Emulation Debugging:**
```bash
# Start emulator in separate terminal
python3 scripts/start_emulator.py

# Run tests against emulator
python3 run_tests.py --emulator
```

## Code Style and Patterns

### C++ Firmware

- **C++17 standard** (C++20 for ESP32)
- **RAII** for resource management (no manual memory cleanup)
- **Interface segregation** - Use interface classes (`I*` prefix)
- **Platform abstraction** - Never use platform-specific code outside `platforms/`
- **Initialization pattern** - Use `InitStep` subclasses for component initialization
- **FlatBuffers** for all protocol serialization (no hand-written serialization)
- **Namespace** - All code in `sparetools::bpm` namespace

**Naming Conventions:**
- Classes: `PascalCase` (e.g., `BpmDetector`)
- Interfaces: `IPascalCase` (e.g., `IAudioInput`)
- Member variables: `camelCase_` with trailing underscore (e.g., `audioInput_`)
- Functions: `camelCase` (e.g., `getBpmDetector()`)
- Constants: `SCREAMING_SNAKE_CASE` (e.g., `SAMPLE_RATE`)

### Python Scripts

- **Python 3.10+**
- **Type hints required**
- **asyncio** for concurrent operations
- **pytest** for testing

## Important Implementation Notes

### FlatBuffers Regeneration

When modifying schemas, always regenerate headers:
```bash
python scripts/generate_flatbuffers.py
```

This updates both `*_generated.h` and `*_extracted.h` files. The extracted headers contain only enums for cross-file usage.

### Platform-Specific Build Filters

PlatformIO uses source filters to exclude platform-specific code:
- ESP32 builds: exclude `src/platforms/arduino/`
- Arduino builds: exclude `src/platforms/esp32/` and disable FlatBuffers

### FreeRTOS Task Management

ESP32 firmware uses FreeRTOS tasks:
- `audioSamplingTask` - High-priority audio sampling (runs in `main.cpp`)
- Main loop - HTTP server, display updates, message processing

Always use `vTaskDelay(pdMS_TO_TICKS(ms))` instead of `delay()` in tasks.

### Conan Integration

This project integrates with SpareTools ecosystem:
- Packages published to Cloudsmith (`sparetools` remote)
- Conan profiles for different targets (`esp32`, `esp32s3`, `arduino_uno`)
- FlatBuffers generation happens in Conan `generate()` step

## MCP Server Integration

This project is configured for MCP (Model Context Protocol) servers:

**.cursor/mcp.json** contains MCP server configurations:
- `esp32-serial-monitor` - Device detection, serial I/O, log capture
- `android-dev-tools` - APK building, ADB operations
- `conan-cloudsmith` - Package management
- `unified-deployment` - Multi-device deployment
- `composed-embedded` - Combined embedded capabilities

Use MCP tools in development workflows instead of manual commands.

## Common Development Tasks

### Adding a New FlatBuffers Message Type

1. Edit schema in `schemas/*.fbs`
2. Run `python scripts/generate_flatbuffers.py`
3. Implement serialization/deserialization in `bpm_flatbuffers.cpp` or `bpm_monitor_flatbuffers.cpp`
4. Add message handling to `bpm_monitor_msg_processor.cpp`

### Adding a New Platform

1. Create platform implementation in `src/platforms/<platform_name>/`
2. Implement all `I*` interfaces
3. Add platform to `PlatformFactory`
4. Add PlatformIO environment in `platformio.ini`
5. Update Conan options in `conanfile.py`

### Adding a New Component

1. Create component class implementing required interfaces
2. Create `*InitStep` class in `src/initialization/`
3. Add init step to `BpmApplication` constructor
4. Wire component dependencies through init steps

### Modifying BPM Detection Algorithm

Edit `src/bpm_detector.cpp` - key methods:
- `sample()` - Called at SAMPLE_RATE Hz for audio sampling
- `detect()` - BPM detection logic (FFT or envelope-based)
- Configuration in `src/config.h` (SAMPLE_RATE, FFT_SIZE, MIN_BPM, MAX_BPM)

## Key Configuration Files

- `platformio.ini` - Build environments, board configs, library dependencies
- `conanfile.py` - Conan package definition, FlatBuffers generation
- `src/config.h` - Firmware configuration constants
- `docker-compose.yml` - Docker test environment
- `.cursor/rules/embedded-dev.mdc` - Cursor IDE rules (MCP servers, workflows)
