# Learning Loop Workflow: ESP32 + Android

## Overview

The learning loop workflow orchestrates a complete development cycle that:
1. Uses **cursor-agent CLI** with **mcp-prompts server** for intelligent code review
2. Fixes issues found during review
3. Builds ESP32 firmware separately
4. Builds Android app separately
5. Deploys and tests separately
6. Tests together (end-to-end)
7. Analyzes results
8. Records everything in the learning loop
9. Repeats the cycle to continuously improve

### Multi-Sensory Notifications

The workflow includes comprehensive notification support:
- **Audio**: eSpeak text-to-speech announcements
- **Visual**: Zigbee light color changes and blinking patterns
- **Terminal Windows**: Automatic log monitoring windows
- **Android Mirroring**: scrcpy integration for device monitoring

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Learning Loop Workflow                    │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ cursor-agent │   │  mcp-prompts  │   │ Learning Loop │
│     CLI      │◄──►│    Server     │◄──►│   Database    │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  ESP32 Build  │   │ Android Build │   │  E2E Testing  │
│   & Deploy    │   │   & Deploy    │   │   & Analysis  │
└───────────────┘   └───────────────┘   └───────────────┘
```

---

## Workflow Phases

### Phase 1: Code Review
- **ESP32 Review**: Uses `esp32-debugging-workflow` prompt from mcp-prompts
- **Android Review**: Uses code review prompts for Android best practices
- **Tool**: cursor-agent + mcp-prompts `get_prompt` and `list_prompts`
- **Output**: Issues found, recommendations, priority rankings

### Phase 2: Build Separately
- **ESP32**: PlatformIO build for `esp32-s3` environment
- **Android**: Gradle build for debug/release
- **Metrics**: Build time, binary size, success/failure

### Phase 3: Test Separately
- **ESP32**: Hardware emulator tests or physical device tests
- **Android**: Unit tests via Gradle
- **Metrics**: Test count, pass/fail rates, execution time

### Phase 4: Test Together (E2E)
- **Integration**: Full system test with ESP32 + Android
- **Protocol**: FlatBuffers communication testing
- **Metrics**: End-to-end success rate, latency, data accuracy

### Phase 5: Analyze Results
- **Success Rate**: Overall cycle success
- **Issues**: Compilation of all issues found
- **Improvements**: Suggestions for next cycle
- **Metrics**: Total time, phase breakdown

### Phase 6: Record in Learning Loop
- **Interaction Recording**: All phases recorded with metrics
- **Prompt Tracking**: Which prompts were used and their effectiveness
- **Success Metrics**: Success rates, execution times, issues found

---

## Usage

### Single Cycle

```bash
python3 scripts/learning_loop_workflow.py --cycle 1
```

### Continuous Cycles

```bash
# Run 5 cycles with 60s delay between each
python3 scripts/learning_loop_workflow.py --continuous 5 --delay 60
```

### Custom Project Root

```bash
python3 scripts/learning_loop_workflow.py --cycle 1 --project-root /path/to/project
```

---

## Example Output

```
######################################################################
# Learning Loop Cycle 1
######################################################################

📋 PHASE 1: Code Review
  ✅ ESP32 Review: Found 15 critical bugs, 12 performance issues
  ✅ Android Review: Found 23 issues across 8 files

🔨 PHASE 2: Build Separately
  ✅ ESP32 Build: Success (2.3MB Flash, 45KB RAM)
  ✅ Android Build: Success (app-debug.apk generated)

🧪 PHASE 3: Test Separately
  ✅ ESP32 Test: 12/12 tests passed (emulator)
  ✅ Android Test: 45/45 tests passed

🔗 PHASE 4: Test Together (E2E)
  ✅ E2E Test: All integration tests passed

📊 PHASE 5: Analyze Results
  ✅ Overall Success: True
  📈 Total Time: 125.3s

💾 PHASE 6: Recording in Learning Loop
  ✅ Recorded interaction for learning-loop-cycle
```

---

## Integration with MCP-Prompts

The workflow automatically:
1. **Discovers prompts** using `mcp-prompts list_prompts`
2. **Retrieves prompts** using `mcp-prompts get_prompt`
3. **Uses prompts** via cursor-agent for code review
4. **Records usage** in learning loop database
5. **Tracks effectiveness** of each prompt

### Available Prompts

- `esp32-debugging-workflow` - ESP32 code review and debugging
- `esp32-fft-configuration-guide` - FFT optimization
- `cpp-memory-management-principles` - C++ memory best practices
- `analysis-assistant` - General code analysis

---

## Learning Loop Database

All interactions are recorded in:
```
/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/learning.db
```

### Recorded Data

- **Prompt ID**: Which prompt was used
- **Query**: What was asked
- **Success**: Whether the operation succeeded
- **Metrics**: Execution time, issues found, test results
- **Metadata**: Build sizes, test counts, error messages

### Viewing Results

```bash
# Dashboard
python3 scripts/learning_loop_dashboard.py

# Statistics
python3 scripts/mcp_learning_integration.py --analyze esp32-debugging-workflow
```

---

## Results Storage

Each cycle saves results to:
```
test_results/learning_loop_cycle_{N}.json
```

### Result Structure

```json
{
  "cycle": 1,
  "timestamp": "2026-01-01T02:36:48.162225+00:00",
  "code_review": {
    "esp32": {
      "success": true,
      "output": "...",
      "metrics": {...},
      "issues_found": 15
    },
    "android": {...}
  },
  "esp32_build": {...},
  "android_build": {...},
  "esp32_test": {...},
  "android_test": {...},
  "e2e_test": {...},
  "analysis": {
    "overall_success": true,
    "issues": [],
    "improvements": [],
    "metrics": {
      "total_time_ms": 125300
    }
  }
}
```

---

## Continuous Improvement

The learning loop:
1. **Tracks** which prompts work best
2. **Identifies** patterns in failures
3. **Suggests** improvements to prompts
4. **Refines** prompts based on results
5. **Optimizes** workflow phases

### Improvement Cycle

```
Run Cycle → Record Results → Analyze Patterns → Improve Prompts → Repeat
```

---

## Best Practices

1. **Start with single cycle** to verify setup
2. **Review results** before running continuous cycles
3. **Fix critical issues** between cycles
4. **Monitor dashboard** for prompt effectiveness
5. **Adjust delays** based on build/test times

---

## Notification Features

### Audio Notifications (eSpeak)
- **Phase Start**: Announces when each phase begins
- **Success/Failure**: Audio feedback for operation results
- **Cycle Complete**: Announces cycle completion with statistics

### Visual Notifications (Zigbee Lights)
- **Blue (Blinking)**: Phase in progress / Cycle starting
- **Green**: Success / Operation completed successfully
- **Red (Blinking)**: Failure / Error occurred
- **Yellow**: Warning / Needs attention
- **Purple (Blinking)**: Analysis / Improvement in progress
- **Cyan**: Progress update

### Terminal Windows
- **Build Logs**: Automatic terminal windows for ESP32 and Android build logs
- **Test Logs**: Terminal windows for test output monitoring
- **Serial Monitor**: ESP32 serial port monitoring
- **Learning Logs**: Dashboard log monitoring

### Android Device Mirroring (scrcpy)
- **Automatic Start**: scrcpy launches during Android build/test phases
- **Window Title**: Custom titles for different phases
- **No Audio**: Audio disabled to reduce resource usage

### Notification Integration Points

**Learning Loop Workflow:**
- Cycle start/complete notifications
- Phase start notifications with progress tracking
- Build success/failure notifications
- Test result notifications
- Analysis complete notifications

**Demo Script:**
- Simulation start/complete
- Interaction progress tracking
- Analysis notifications
- Prompt improvement notifications

**MCP Integration:**
- Interaction recording notifications
- Prompt analysis notifications
- Improvement cycle notifications

**Dashboard:**
- Dashboard refresh notifications
- Success rate-based light colors
- Continuous monitoring notifications

---

## Dependencies

### Required Packages
```bash
# Python packages
pip install pyserial paho-mqtt

# System packages (Ubuntu/Debian)
sudo apt install espeak scrcpy gnome-terminal

# System packages (macOS)
brew install espeak scrcpy
```

### Zigbee Setup

**MQTT (Recommended):**
1. Install and configure Zigbee2MQTT
2. Start MQTT broker (Mosquitto)
3. Configure `NotificationManager` with MQTT broker address

**Serial (Fallback):**
1. Connect Zigbee gateway to `/dev/ttyACM1`
2. Add user to `dialout` group: `sudo usermod -a -G dialout $USER`
3. Enable serial in `NotificationManager`: `enable_serial=True`

### Permissions
```bash
# Serial port access
sudo usermod -a -G dialout $USER
# Log out and back in for changes to take effect

# ADB for scrcpy
# Ensure ADB is in PATH and devices are authorized
```

---

## Troubleshooting

### cursor-agent Not Found
```bash
# Install cursor-agent
npm install -g @cursor/agent
```

### mcp-prompts Server Not Responding
```bash
# Check MCP configuration
cat ~/.cursor/mcp.json

# Test mcp-prompts
cursor-agent mcp list-tools mcp-prompts
```

### Notification Issues

**eSpeak Not Working:**
```bash
# Check installation
which espeak
espeak "test"

# Install if missing
sudo apt install espeak  # Ubuntu/Debian
brew install espeak       # macOS
```

**Zigbee Lights Not Responding:**
```bash
# Check MQTT connection
mosquitto_pub -h localhost -t test -m "test"

# Check Zigbee2MQTT status
# Verify lights are paired and accessible

# Test serial connection (if using serial fallback)
python3 -c "import serial; s = serial.Serial('/dev/ttyACM1', 115200); s.write(b'TEST\n')"
```

**scrcpy Not Starting:**
```bash
# Check ADB connection
adb devices

# Check scrcpy installation
which scrcpy
scrcpy --version

# Install if missing
sudo apt install scrcpy  # Ubuntu/Debian
brew install scrcpy       # macOS
```

**Terminal Windows Not Spawning:**
```bash
# Check for terminal emulator
which gnome-terminal xterm x-terminal-emulator

# Install if missing
sudo apt install gnome-terminal  # Ubuntu
sudo apt install xterm          # Generic
```

### Build Failures
- Check PlatformIO installation: `pio --version`
- Check Gradle installation: `./android-app/gradlew --version`
- Review build logs in cycle results JSON

### Test Failures
- Verify hardware emulator is running (if using)
- Check device connections (if using physical devices)
- Review test output in cycle results

---

## Next Steps

1. **Run first cycle**: `python3 scripts/learning_loop_workflow.py --cycle 1`
2. **Review results**: Check `test_results/learning_loop_cycle_1.json`
3. **Fix issues**: Address critical bugs found
4. **Run continuous**: `python3 scripts/learning_loop_workflow.py --continuous 5`
5. **Monitor dashboard**: `python3 scripts/learning_loop_dashboard.py`

---

**Status**: 🟢 OPERATIONAL  
**Last Updated**: 2026-01-01  
**Version**: 1.0.0
