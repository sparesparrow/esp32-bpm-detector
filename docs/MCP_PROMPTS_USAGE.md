# ESP32 BPM Detector - MCP-Prompts Usage Guide

*Direct integration with MCP-Prompts server configured in `~/.cursor/mcp.json`*

## MCP-Prompts Server Configuration

The project uses the MCP-Prompts server configured as:

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

## Available ESP32-BPM Prompts

### 1. `esp32-bpm-api-endpoint`

**Purpose**: Create WiFi API endpoints for streaming BPM data and audio spectrum analysis

**Location**: `/home/sparrow/mcp/data/prompts/esp32-bpm-api-endpoint.json`

**Variables**:
- `endpoint_path` (required): API endpoint path (e.g., "/api/v1/bpm")
- `data_format` (required): Data format - "json", "binary", "websocket"
- `update_rate` (required): Update rate in Hz (e.g., 10, 30, 60)

**Usage Example**:
```bash
# In Cursor chat, use MCP-Prompts apply_template:
mcp_mcp-prompts_apply_template(
  promptId: "esp32-bpm-api-endpoint",
  variables: {
    endpoint_path: "/api/v1/bpm",
    data_format: "flatbuffers",
    update_rate: 10
  }
)
```

**Current Implementation**: 
- ✅ Implemented in `src/api_endpoints.cpp`
- ✅ Endpoints: `/api/v1/bpm/current`, `/api/v1/system/status`
- ✅ Format: JSON (FlatBuffers planned)

---

### 2. `esp32-bpm-audio-calibration`

**Purpose**: Calibrate microphone input for optimal BPM detection accuracy and noise reduction

**Location**: `/home/sparrow/mcp/data/prompts/esp32-bpm-audio-calibration.json`

**Variables**:
- `mic_type` (required): Microphone type - "analog", "digital", "i2s"
- `gain_level` (required): Pre-amplifier gain level (e.g., 1.0, 2.5, 5.0)
- `threshold` (required): Detection threshold in dB (e.g., -30, -40, -50)

**Usage Example**:
```bash
mcp_mcp-prompts_apply_template(
  promptId: "esp32-bpm-audio-calibration",
  variables: {
    mic_type: "analog",
    gain_level: 2.5,
    threshold: -30
  }
)
```

**Current Implementation**:
- ✅ Calibration guide in `docs/calibration_guide.md`
- ✅ Optimal settings documented
- ✅ Automated calibration script planned

---

### 3. `esp32-bpm-fft-configuration`

**Purpose**: Configure FFT parameters for optimal BPM detection accuracy and performance on ESP32

**Location**: `/home/sparrow/mcp/data/prompts/esp32-bpm-fft-configuration.json`

**Variables**:
- `sample_rate` (required): Audio sample rate in Hz (e.g., 44100, 22050, 25000)
- `fft_size` (required): FFT size - power of 2 (e.g., 512, 1024, 2048)
- `window_type` (required): Window function - "hamming", "hann", "blackman", "rectangular"

**Usage Example**:
```bash
mcp_mcp-prompts_apply_template(
  promptId: "esp32-bpm-fft-configuration",
  variables: {
    sample_rate: 25000,
    fft_size: 1024,
    window_type: "hamming"
  }
)
```

**Current Implementation**:
- ✅ Configured in `src/config.h` with MCP-optimized values
- ✅ Documentation in `docs/fft_configuration.md`
- ✅ Validated for ESP32-S3 constraints

---

### 4. `esp32-bpm-display-integration`

**Purpose**: Integrate OLED/7-segment displays for BPM display with ESP32 GPIO control

**Location**: `/home/sparrow/mcp/data/prompts/esp32-bpm-display-integration.json`

**Variables**:
- `display_type` (required): Display type - "oled_i2c", "oled_spi", "7segment", "lcd_i2c"
- `i2c_address` (optional): I2C address for I2C displays (e.g., "0x3C", "0x27")
- `refresh_rate` (required): Display refresh rate in Hz (e.g., 10, 30)

**Current Implementation**:
- ✅ Display handler in `src/display_handler.cpp`
- ✅ Optimized to 10 Hz refresh rate
- ✅ Rate limiting implemented

---

### 5. `esp32-bpm-testing-strategy`

**Purpose**: Create testing strategies for BPM detection accuracy with various audio sources

**Location**: `/home/sparrow/mcp/data/prompts/esp32-bpm-testing-strategy.json`

**Variables**:
- `test_bpm_range` (required): BPM range to test (e.g., "60-180", "80-160")
- `audio_sources` (required): Comma-separated test audio sources (e.g., "sine_wave,real_music,white_noise")
- `validation_method` (required): Validation approach - "manual", "automated", "statistical"

**Current Implementation**:
- ✅ Test suite in `tests/test_bpm_accuracy.cpp`
- ✅ Automated test runner in `scripts/run_bpm_tests.py`
- ✅ Statistical validation implemented

---

### 6. `esp32-bpm-android-integration`

**Purpose**: Integrate Android app with ESP32 API for real-time BPM display and audio visualization

**Location**: `/home/sparrow/mcp/data/prompts/esp32-bpm-android-integration.json`

**Variables**:
- `api_url` (required): ESP32 API base URL (e.g., "http://192.168.1.100:80")
- `polling_interval` (required): Polling interval in milliseconds (e.g., 100, 200)
- `ui_components` (required): Comma-separated UI components (e.g., "bpm_display,spectrum_analyzer,waveform")

**Current Implementation**:
- 📋 Planned for future Android app development
- ✅ API endpoints ready for integration
- ✅ Documentation in `docs/API.md`

---

## Using MCP-Prompts in Cursor

### Method 1: Direct MCP Tool Calls

```python
# In Cursor chat, you can use MCP tools directly:
from mcp import mcp_prompts

# Apply a template
result = mcp_prompts.apply_template(
    prompt_id="esp32-bpm-api-endpoint",
    variables={
        "endpoint_path": "/api/v1/bpm",
        "data_format": "flatbuffers",
        "update_rate": 10
    }
)
```

### Method 2: Via Cursor Chat Commands

In Cursor chat, you can reference prompts:

```
@mcp-prompts Apply esp32-bpm-fft-configuration with:
- sample_rate: 25000
- fft_size: 1024
- window_type: hamming
```

### Method 3: Programmatic Access

```bash
# List all prompts
curl http://localhost:8000/api/prompts

# Get specific prompt
curl http://localhost:8000/api/prompts/esp32-bpm-api-endpoint

# Apply template
curl -X POST http://localhost:8000/api/prompts/esp32-bpm-api-endpoint/apply \
  -H "Content-Type: application/json" \
  -d '{
    "variables": {
      "endpoint_path": "/api/v1/bpm",
      "data_format": "flatbuffers",
      "update_rate": 10
    }
  }'
```

## Integration Workflow

### Step 1: Configure Prompt Variables

Before using a prompt, determine the appropriate variables:

```javascript
// Example: FFT Configuration
const fftConfig = {
  sample_rate: 25000,  // Based on ESP32-S3 capabilities
  fft_size: 1024,      // Balance of accuracy vs performance
  window_type: "hamming" // Best for BPM detection
};
```

### Step 2: Apply Template

Use the MCP-Prompts tool to generate code/documentation:

```bash
# This generates optimized configuration
mcp-prompts apply esp32-bpm-fft-configuration \
  --sample_rate=25000 \
  --fft_size=1024 \
  --window_type=hamming
```

### Step 3: Review Generated Output

The prompt will generate:
- Optimized configuration values
- Performance recommendations
- Hardware constraint validations
- Documentation snippets

### Step 4: Integrate into Project

Copy the generated recommendations into your codebase:
- Update `src/config.h` with optimized values
- Add documentation to `docs/`
- Update test cases if needed

## Prompt Enhancement Workflow

### Adding New Variables

To enhance an existing prompt:

1. Edit the prompt JSON file:
```json
{
  "id": "esp32-bpm-api-endpoint",
  "variables": [
    "endpoint_path",
    "data_format",
    "update_rate",
    "authentication"  // New variable
  ]
}
```

2. Update the prompt content template:
```json
{
  "content": "API Endpoint: {{endpoint_path}} with {{data_format}} format at {{update_rate}}Hz with {{authentication}}"
}
```

3. Reload MCP server or restart Cursor

### Creating New Prompts

1. Create new JSON file in `/home/sparrow/mcp/data/prompts/`:
```json
{
  "id": "esp32-bpm-new-feature",
  "name": "ESP32-BPM New Feature",
  "description": "Description of the new feature",
  "content": "Template with {{variable1}} and {{variable2}}",
  "isTemplate": true,
  "variables": ["variable1", "variable2"],
  "tags": ["esp32-bpm-detector", "new-feature"],
  "version": 1
}
```

2. The prompt will be automatically available via MCP-Prompts tools

## Best Practices

### 1. Use Prompts for Configuration
- ✅ FFT parameters → `esp32-bpm-fft-configuration`
- ✅ API endpoints → `esp32-bpm-api-endpoint`
- ✅ Display settings → `esp32-bpm-display-integration`

### 2. Validate Before Applying
- Check hardware constraints
- Verify memory limitations
- Test performance impact

### 3. Document Changes
- Update `docs/` with prompt-generated recommendations
- Track which prompts were used
- Note any manual adjustments

### 4. Iterate and Improve
- Re-run prompts after hardware changes
- Update prompts based on experience
- Share improvements with team

## Troubleshooting

### Prompt Not Found
```bash
# Verify prompt file exists
ls -la /home/sparrow/mcp/data/prompts/esp32-bpm-*.json

# Check MCP server is running
ps aux | grep mcp-prompts-server

# Verify Cursor MCP configuration
cat ~/.cursor/mcp.json | grep mcp-prompts
```

### Variables Not Working
- Check variable names match exactly (case-sensitive)
- Ensure all required variables are provided
- Verify variable values match expected formats

### Template Not Applying
- Check MCP server logs
- Verify prompt JSON syntax is valid
- Restart Cursor if needed

## Future Enhancements

### Planned Prompt Additions
1. **esp32-bpm-performance-optimization**: CPU and memory optimization
2. **esp32-bpm-security-hardening**: Security best practices
3. **esp32-bpm-ota-updates**: Over-the-air update procedures
4. **esp32-bpm-power-management**: Battery optimization

### Integration Improvements
- Automated prompt application in CI/CD
- Prompt versioning and rollback
- Collaborative prompt sharing
- Prompt usage analytics

---

*This guide demonstrates the practical use of MCP-Prompts tools for ESP32 BPM detector development. All prompts are stored in `/home/sparrow/mcp/data/prompts/` and accessible via the MCP-Prompts server configured in Cursor.*

