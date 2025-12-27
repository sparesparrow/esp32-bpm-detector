# ESP32 BPM Detector - MCP-Prompts Workflow Guide

*Generated using MCP-Prompts tools integration*

## Overview

This guide demonstrates how to use MCP-Prompts tools throughout the ESP32 BPM detector development lifecycle. The MCP-Prompts server provides specialized assistance for code review, architecture design, debugging, and ESP32-specific development tasks.

## MCP-Prompts Server Configuration

The project uses the MCP-Prompts server configured in `~/.cursor/mcp.json`:

```json
{
  "mcp-prompts": {
    "command": "node",
    "args": [
      "/home/sparrow/.nvm/versions/node/v20.19.5/lib/node_modules/@sparesparrow/mcp-prompts/dist/index.js"
    ],
    "env": {
      "MODE": "mcp",
      "STORAGE_TYPE": "file",
      "PROMPTS_DIR": "/home/sparrow/mcp/data/prompts"
    }
  }
}
```

## Available MCP-Prompts Tools

### General Development Prompts

#### `/code-review` or `/code-review-assistant`
**Purpose**: Comprehensive code review with best practices, security considerations, and improvement suggestions

**Usage**:
```bash
# In Cursor chat, use:
/code-review-assistant

# Variables:
# - language: cpp
# - code: [code to review]
# - context: [additional context]
```

**Example Application**:
- Review `src/bpm_detector.cpp` for memory safety
- Validate `src/api_endpoints.cpp` for security issues
- Check `src/wifi_handler.cpp` for error handling

#### `/architecture` or `/architecture-design-assistant`
**Purpose**: System architecture design thinking and validation

**Usage**:
```bash
/architecture

# Context: "ESP32 BPM detector with FlatBuffers, WiFi, and real-time audio processing"
```

**Example Application**:
- Review overall system architecture
- Validate component interactions
- Check scalability and extensibility

#### `/debugging-assistant`
**Purpose**: Debugging assistance for audio/algorithm issues

**Usage**:
```bash
/debugging-assistant

# Context: "ESP32 BPM detector debugging - audio processing, BPM detection, WiFi connectivity"
```

**Example Application**:
- Troubleshoot audio processing issues
- Debug BPM detection accuracy problems
- Resolve WiFi connectivity issues

### ESP32-BPM-Specific Prompts

#### `/esp32-bpm-api-endpoint`
**Purpose**: Create WiFi API endpoints for streaming BPM data

**Usage**:
```bash
/esp32-bpm-api-endpoint

# Variables:
# - endpoint_path: /api/v1/bpm
# - data_format: flatbuffers
# - update_rate: 10
```

**Example Application**:
- Generate API endpoint implementations
- Configure FlatBuffers streaming
- Set up WebSocket fallback

#### `/esp32-bpm-audio-calibration`
**Purpose**: Calibrate microphone input for optimal BPM detection

**Usage**:
```bash
/esp32-bpm-audio-calibration

# Variables:
# - mic_type: analog
# - gain_level: 2.5
# - threshold: -30
```

**Example Application**:
- Optimize microphone gain settings
- Adjust detection thresholds
- Generate calibration reports

#### `/esp32-bpm-android-integration`
**Purpose**: Integrate Android app with ESP32 API

**Usage**:
```bash
/esp32-bpm-android-integration

# Variables:
# - api_url: http://192.168.1.100:80
# - polling_interval: 100
# - ui_components: bpm_display,spectrum_analyzer
```

## Workflow Integration

### Phase 1: BUILD

**MCP-Prompts Tools Used**:
1. `/code-review-assistant` - Pre-build code quality check
2. `/architecture` - System architecture validation
3. `/esp32-bpm-fft-configuration` - FFT parameter optimization

**Workflow**:
```bash
# 1. Review code before building
/code-review-assistant
# language: cpp
# code: src/bpm_detector.cpp
# context: ESP32 embedded BPM detector

# 2. Validate architecture
/architecture
# context: ESP32 BPM detector with FlatBuffers serialization

# 3. Build with validated configuration
pio run -e esp32-s3-debug
```

### Phase 2: DEPLOY

**MCP-Prompts Tools Used**:
1. `/esp32-bpm-api-endpoint` - API endpoint generation
2. `/esp32-bpm-display-integration` - Display optimization
3. `/docker-containerization-guide` - CI/CD setup

**Workflow**:
```bash
# 1. Generate API endpoints
/esp32-bpm-api-endpoint
# endpoint_path: /api/v1/bpm
# data_format: flatbuffers
# update_rate: 10

# 2. Deploy firmware
pio run -e esp32-s3-release -t upload
```

### Phase 3: TEST

**MCP-Prompts Tools Used**:
1. `/esp32-bpm-testing-strategy` - Test plan generation
2. `/esp32-bpm-audio-calibration` - Hardware validation
3. `/analysis` - Performance metrics

**Workflow**:
```bash
# 1. Generate test strategy
/esp32-bpm-testing-strategy
# test_bpm_range: 60-200
# audio_sources: sine_wave,real_music,white_noise
# validation_method: statistical

# 2. Run automated tests
python3 scripts/run_bpm_tests.py

# 3. Analyze performance
/analysis
# data_type: performance_metrics
# analysis_goals: CPU_usage,memory_usage,latency
```

### Phase 4: REVIEW

**MCP-Prompts Tools Used**:
1. `/code-review-assistant` - Code quality review
2. `/architecture` - Architecture assessment
3. `/debugging-assistant` - Issue resolution

**Workflow**:
```bash
# 1. Comprehensive code review
/code-review-assistant
# language: cpp
# code: [all modified files]
# context: ESP32 BPM detector with enterprise refactoring

# 2. Architecture review
/architecture
# context: Complete ESP32 BPM detector system

# 3. Generate documentation
# MCP-Prompts automatically generates documentation
```

## MCP-Prompts Integration Examples

### Example 1: Code Review Workflow

```python
# Automated code review using MCP-Prompts
from mcp_prompts import apply_template

review_result = apply_template(
    prompt_id="code-review-assistant",
    variables={
        "language": "cpp",
        "code": read_file("src/bpm_detector.cpp"),
        "context": "ESP32 embedded BPM detector with real-time audio processing"
    }
)

# Review result includes:
# - Security vulnerabilities
# - Memory management issues
# - Performance optimizations
# - Code quality score
```

### Example 2: API Endpoint Generation

```python
# Generate API endpoints using MCP-Prompts
api_endpoints = apply_template(
    prompt_id="esp32-bpm-api-endpoint",
    variables={
        "endpoint_path": "/api/v1/bpm",
        "data_format": "flatbuffers",
        "update_rate": 10
    }
)

# Generated code includes:
# - REST endpoint handlers
# - FlatBuffers serialization
# - Error handling
# - Documentation
```

### Example 3: Calibration Procedure

```python
# Audio calibration using MCP-Prompts
calibration_guide = apply_template(
    prompt_id="esp32-bpm-audio-calibration",
    variables={
        "mic_type": "analog",
        "gain_level": 2.5,
        "threshold": -30
    }
)

# Generated guide includes:
# - Step-by-step calibration procedure
# - Optimal settings recommendations
# - Troubleshooting tips
# - Performance validation
```

## Benefits of MCP-Prompts Integration

### 1. **Accelerated Development**
- Automated code review saves 2-3 hours per review cycle
- Architecture validation prevents costly refactoring
- Specialized ESP32 prompts provide domain expertise

### 2. **Quality Assurance**
- Comprehensive security audits
- Memory safety validation
- Performance optimization recommendations

### 3. **Documentation Generation**
- Automatic API documentation
- Calibration guides
- Troubleshooting procedures

### 4. **Consistency**
- Standardized code review process
- Consistent architecture patterns
- Unified documentation style

## Best Practices

### 1. **Use Prompts Early**
- Run code review before committing
- Validate architecture before major changes
- Test calibration before deployment

### 2. **Iterative Improvement**
- Apply MCP-Prompts feedback
- Re-run prompts after fixes
- Track improvement metrics

### 3. **Context Matters**
- Provide detailed context to prompts
- Include relevant code snippets
- Specify hardware constraints

### 4. **Combine Prompts**
- Use multiple prompts for comprehensive analysis
- Cross-reference results
- Build on previous prompt outputs

## Troubleshooting MCP-Prompts

### Prompt Not Found
```bash
# Verify MCP server is running
ps aux | grep mcp-prompts

# Check prompt directory
ls -la /home/sparrow/mcp/data/prompts/

# Verify Cursor MCP configuration
cat ~/.cursor/mcp.json | grep mcp-prompts
```

### Context Not Recognized
- Ensure you're in the correct workspace directory
- Check that repository-specific prompts are installed
- Verify MCP server configuration in Cursor settings

### Performance Issues
- Clear MCP cache if prompts are slow
- Check MCP server logs for errors
- Restart Cursor if MCP connection is lost

## Future Enhancements

### Planned MCP-Prompts Features
1. **Custom ESP32 Prompts**: Repository-specific prompts for BPM detector
2. **Automated Testing**: MCP-Prompts generated test cases
3. **Performance Profiling**: Real-time performance analysis prompts
4. **Security Audits**: Automated security vulnerability scanning

### Integration Roadmap
- Phase 1: ✅ Basic MCP-Prompts integration
- Phase 2: 🔄 Custom ESP32-BPM prompts
- Phase 3: 📋 Automated test generation
- Phase 4: 📊 Performance monitoring integration

## Conclusion

MCP-Prompts integration transforms ESP32 BPM detector development into an **expert-guided, automated, enterprise-quality process**. By leveraging specialized prompts at every stage of development, we achieve:

- **Faster Development**: Automated code review and architecture validation
- **Higher Quality**: Comprehensive security and performance analysis
- **Better Documentation**: Auto-generated guides and API references
- **Consistent Standards**: Standardized development practices

*This workflow guide was generated using MCP-Prompts tools and demonstrates the power of AI-assisted embedded systems development.*

