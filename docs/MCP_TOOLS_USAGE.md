# ESP32 BPM Detector - MCP Tools Usage Guide

*Practical guide for using MCP-Prompts tools with the ESP32 BPM detector project*

## MCP-Prompts Server Configuration

Your MCP-Prompts server is configured in `~/.cursor/mcp.json`:

```json
{
  "mcp-prompts": {
    "command": "mcp-prompts-server",
    "args": [],
    "env": {
      "MODE": "mcp",
      "STORAGE_TYPE": "file",
      "PROMPTS_DIR": "/home/sparrow/mcp/data/prompts"
    }
  }
}
```

## Available Prompts for ESP32 BPM Detector

### ESP32-BPM-Specific Prompts (Already Available!)

Your MCP-Prompts server already includes specialized ESP32-BPM prompts:

#### 1. ESP32-BPM FFT Configuration
**File**: `/home/sparrow/mcp/data/prompts/esp32-bpm-fft-configuration.json`

**Usage**:
```
/esp32-bpm-fft-configuration

Variables:
- sample_rate: 25000 (Hz)
- fft_size: 1024 (points)
- window_type: hamming
```

**Use Case**: Optimize FFT parameters for ESP32-S3 constraints

#### 2. ESP32-BPM API Endpoint
**File**: `/home/sparrow/mcp/data/prompts/esp32-bpm-api-endpoint.json`

**Usage**:
```
/esp32-bpm-api-endpoint

Variables:
- endpoint_path: /api/v1/bpm
- data_format: flatbuffers
- update_rate: 10 (Hz)
```

**Use Case**: Generate WiFi API endpoints for BPM data streaming

#### 3. ESP32-BPM Audio Calibration
**File**: `/home/sparrow/mcp/data/prompts/esp32-bpm-audio-calibration.json`

**Usage**:
```
/esp32-bpm-audio-calibration

Variables:
- mic_type: analog
- gain_level: 2.5
- threshold: -30 (dB)
```

**Use Case**: Calibrate microphone for optimal BPM detection

#### 4. ESP32-BPM Android Integration
**File**: `/home/sparrow/mcp/data/prompts/esp32-bpm-android-integration.json`

**Usage**:
```
/esp32-bpm-android-integration

Variables:
- api_url: http://192.168.1.100:80
- polling_interval: 100 (ms)
- ui_components: bpm_display,spectrum_analyzer
```

**Use Case**: Integrate Android app with ESP32 API

#### 5. ESP32-BPM Display Integration
**File**: `/home/sparrow/mcp/data/prompts/esp32-bpm-display-integration.json`

**Usage**:
```
/esp32-bpm-display-integration

Variables:
- display_type: oled_i2c
- i2c_address: 0x3C
- refresh_rate: 10 (Hz)
```

**Use Case**: Integrate OLED/7-segment displays

#### 6. ESP32-BPM Testing Strategy
**File**: `/home/sparrow/mcp/data/prompts/esp32-bpm-testing-strategy.json`

**Usage**:
```
/esp32-bpm-testing-strategy

Variables:
- test_bpm_range: 60-200
- audio_sources: sine_wave,real_music,white_noise
- validation_method: statistical
```

**Use Case**: Create comprehensive testing strategies

### General Development Prompts

#### 1. Code Review Assistant
**File**: `/home/sparrow/mcp/data/prompts/code-review-assistant.json`

**Usage in Cursor**:
```
/code-review-assistant

Variables:
- language: cpp
- code: [your code snippet or file path]
- context: ESP32 embedded BPM detector with real-time audio processing
```

**Example**:
```
Review the BPM detector implementation:
/code-review-assistant
language: cpp
code: src/bpm_detector.cpp
context: ESP32-S3 embedded system with FFT analysis and beat detection
```

#### 2. Architecture Design Assistant
**File**: `/home/sparrow/mcp/data/prompts/architecture-design-assistant.json`

**Usage**:
```
/architecture

Context: ESP32 BPM detector with FlatBuffers serialization, FreeRTOS tasks, and WiFi streaming
```

**Use Cases**:
- System architecture validation
- Component interaction analysis
- Memory and performance optimization
- Thread safety assessment

#### 3. Code Refactoring Assistant
**File**: `/home/sparrow/mcp/data/prompts/code-refactoring-assistant.json`

**Usage**:
```
/refactoring

Context: Refactor ESP32 BPM detector to use SpareTools module and reduce Arduino dependencies
```

**Use Cases**:
- Decouple Arduino dependencies
- Improve code modularity
- Optimize memory usage
- Enhance testability

#### 4. Debugging Assistant
**File**: `/home/sparrow/mcp/data/prompts/debugging-assistant.json`

**Usage**:
```
/debugging-assistant

Context: ESP32 BPM detector debugging - audio processing issues, BPM detection accuracy problems
```

**Use Cases**:
- Troubleshoot audio sampling issues
- Debug FFT computation problems
- Resolve WiFi connectivity issues
- Fix memory leaks

### Specialized Prompts

#### 5. Analysis Assistant
**File**: `/home/sparrow/mcp/data/prompts/analysis-assistant.json`

**Usage**:
```
/analysis

Data Type: performance_metrics
Analysis Goals: CPU_usage,memory_usage,latency,throughput
```

**Use Cases**:
- Performance profiling
- Memory usage analysis
- Latency measurement
- Throughput optimization

## Creating ESP32-BPM-Specific Prompts

You can create custom prompts for ESP32 BPM detector development:

### Example: ESP32-BPM FFT Configuration Prompt

Create `/home/sparrow/mcp/data/prompts/esp32-bpm-fft-configuration.json`:

```json
{
  "id": "esp32-bpm-fft-configuration",
  "name": "ESP32-BPM FFT Configuration",
  "description": "Configure FFT parameters for optimal BPM detection on ESP32",
  "template": "You are an ESP32 audio processing expert. Configure FFT parameters:\n- Sample Rate: {{sample_rate}} Hz\n- FFT Size: {{fft_size}} points\n- Window Type: {{window_type}}\n\nProvide recommendations for ESP32-S3 constraints.",
  "category": "embedded",
  "tags": ["esp32", "bpm", "fft", "audio"],
  "variables": [
    {
      "name": "sample_rate",
      "type": "number",
      "required": true,
      "description": "Audio sample rate in Hz"
    },
    {
      "name": "fft_size",
      "type": "number",
      "required": true,
      "description": "FFT size (power of 2)"
    },
    {
      "name": "window_type",
      "type": "string",
      "required": true,
      "description": "Window function type"
    }
  ]
}
```

### Example: ESP32-BPM API Endpoint Prompt

Create `/home/sparrow/mcp/data/prompts/esp32-bpm-api-endpoint.json`:

```json
{
  "id": "esp32-bpm-api-endpoint",
  "name": "ESP32-BPM API Endpoint",
  "description": "Generate WiFi API endpoints for BPM data streaming",
  "template": "Generate REST API endpoint for ESP32 BPM detector:\n- Path: {{endpoint_path}}\n- Format: {{data_format}}\n- Update Rate: {{update_rate}} Hz\n\nInclude FlatBuffers serialization and error handling.",
  "category": "embedded",
  "tags": ["esp32", "bpm", "api", "wifi"],
  "variables": [
    {
      "name": "endpoint_path",
      "type": "string",
      "required": true,
      "description": "API endpoint path"
    },
    {
      "name": "data_format",
      "type": "string",
      "required": true,
      "description": "Data format (json, flatbuffers, websocket)"
    },
    {
      "name": "update_rate",
      "type": "number",
      "required": true,
      "description": "Update rate in Hz"
    }
  ]
}
```

## Using MCP-Prompts in Development Workflow

### 1. Before Coding
```bash
# Review architecture
/architecture
# Context: ESP32 BPM detector system design

# Get code review guidelines
/code-review-assistant
# language: cpp
# context: ESP32 embedded development best practices
```

### 2. During Development
```bash
# Get refactoring suggestions
/refactoring
# Context: Improve ESP32 BPM detector code structure

# Debug issues
/debugging-assistant
# Context: BPM detection accuracy problems
```

### 3. After Implementation
```bash
# Performance analysis
/analysis
# Data Type: performance_metrics
# Analysis Goals: CPU_usage,memory_usage

# Code review
/code-review-assistant
# language: cpp
# code: src/bpm_detector.cpp
```

## MCP-Prompts Integration with ESP32 Project

### Automated Code Review

Add to your development workflow:

```bash
#!/bin/bash
# scripts/mcp-code-review.sh

# Review all source files
for file in src/*.cpp; do
  echo "Reviewing $file..."
  # Use MCP-Prompts code-review-assistant
  # (Integration with Cursor MCP interface)
done
```

### Architecture Validation

Before major changes:

```bash
# Validate architecture changes
/architecture
# Context: ESP32 BPM detector with new SpareTools integration
```

### Performance Monitoring

Regular performance checks:

```bash
# Analyze performance metrics
/analysis
# Data Type: performance_metrics
# Analysis Goals: CPU_usage,memory_usage,latency
```

## Troubleshooting MCP-Prompts

### Server Not Responding

1. **Check Server Status**:
```bash
ps aux | grep mcp-prompts-server
```

2. **Verify Configuration**:
```bash
cat ~/.cursor/mcp.json | grep -A 10 mcp-prompts
```

3. **Check Prompts Directory**:
```bash
ls -la /home/sparrow/mcp/data/prompts/
```

4. **Restart Cursor**: Sometimes MCP servers need a restart

### Prompts Not Found

1. **Verify Prompt Files Exist**:
```bash
ls /home/sparrow/mcp/data/prompts/*.json
```

2. **Check File Permissions**:
```bash
chmod 644 /home/sparrow/mcp/data/prompts/*.json
```

3. **Validate JSON Syntax**:
```bash
for file in /home/sparrow/mcp/data/prompts/*.json; do
  python3 -m json.tool "$file" > /dev/null || echo "Invalid: $file"
done
```

### Connection Issues

1. **Test MCP Server Directly**:
```bash
mcp-prompts-server --help
```

2. **Check Environment Variables**:
```bash
echo $MODE
echo $STORAGE_TYPE
echo $PROMPTS_DIR
```

3. **Review Cursor Logs**:
Check Cursor's MCP server logs for connection errors

## Best Practices

### 1. Use Specific Context
Always provide detailed context when using prompts:
- Hardware constraints (ESP32-S3, 512KB RAM)
- Performance requirements (real-time audio processing)
- Integration points (FlatBuffers, WiFi, Display)

### 2. Iterate on Results
- Use prompt outputs as starting points
- Refine based on ESP32-specific constraints
- Validate with actual hardware testing

### 3. Combine Multiple Prompts
- Architecture + Code Review for major changes
- Debugging + Analysis for performance issues
- Refactoring + Code Review for improvements

### 4. Document Prompt Usage
Keep track of which prompts were used for each feature:
```markdown
## Feature: API Endpoints
- Prompt: esp32-bpm-api-endpoint
- Variables: endpoint_path=/api/v1/bpm, data_format=flatbuffers
- Result: Generated src/api_endpoints.cpp
```

## Example Workflow

### Complete Feature Development with MCP-Prompts

1. **Planning Phase**:
```
/architecture
Context: Add WebSocket support to ESP32 BPM detector
```

2. **Implementation Phase**:
```
/code-review-assistant
language: cpp
code: src/websocket_handler.cpp
context: ESP32 WebSocket implementation for real-time BPM streaming
```

3. **Testing Phase**:
```
/debugging-assistant
Context: WebSocket connection issues on ESP32
```

4. **Review Phase**:
```
/analysis
Data Type: performance_metrics
Analysis Goals: network_latency,memory_usage
```

## Resources

- **MCP-Prompts Documentation**: Check `/home/sparrow/mcp/data/prompts/` for available prompts
- **Cursor MCP Integration**: See Cursor documentation for MCP server usage
- **ESP32 BPM Detector Docs**: See `docs/` directory for project-specific documentation

---

*This guide demonstrates practical usage of MCP-Prompts tools with the ESP32 BPM detector project. For more information, see `docs/mcp_workflow_guide.md`.*

