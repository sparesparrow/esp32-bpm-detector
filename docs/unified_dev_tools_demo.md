# Unified Dev Tools MCP Server - Live Demonstration

## Status: ✅ Operational

The unified-dev-tools MCP server is now properly configured and functional.

## Configuration

**Location**: `.claude/mcp.json`

```json
{
  "mcpServers": {
    "unified-dev-tools": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "/home/sparrow/mcp/servers/python/unified_dev_tools",
        "python",
        "unified_dev_tools_mcp_server.py"
      ],
      "env": {
        "LOG_LEVEL": "INFO",
        "MCP_PROMPTS_PATH": "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts",
        "ESP32_LOG_DIR": "/home/sparrow/esp32_logs",
        "ANDROID_LOG_DIR": "/home/sparrow/android_logs",
        "CONAN_SESSION_STORAGE": "/home/sparrow/.mcp/conan_sessions.json",
        "PROJECT_DIR": "/home/sparrow/projects/embedded-systems/esp32-bpm-detector"
      }
    }
  }
}
```

## Available Tools Demonstrated

### 1. ESP32 Serial Monitor ✅
**Tool**: `esp32_serial_monitor_start`

**Status**: Active on `/dev/ttyACM0` at 115200 baud

**Usage**:
- Real-time serial output monitoring
- Background log storage to `/home/sparrow/esp32_logs`
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- Pattern matching for error detection

**Example**:
```python
mcp_unified-dev-tools_esp32_serial_monitor_start(
    port="/dev/ttyACM0",
    baud_rate=115200,
    log_level="INFO"
)
```

### 2. Android Device Management ✅
**Tool**: `android_device_list`

**Status**: Available (no devices currently connected)

**Capabilities**:
- List connected Android devices
- Device information retrieval
- APK installation and management
- Logcat monitoring

### 3. Conan Package Management ✅
**Tool**: `conan_search_packages`

**Status**: Connected to `sparetools` remote

**Usage**:
- Search for packages in Cloudsmith
- Package creation and upload
- Dependency management

**Example Search**:
- ESP32 packages
- FlatBuffers packages

### 4. Repository Cleanup ✅
**Tool**: `repo_cleanup_scan`

**Status**: Scanned project repository

**Capabilities**:
- Quick scan for cleanup opportunities
- Full repository analysis
- Custom scan patterns
- Cleanup execution

### 5. Composed Embedded Workflow ✅
**Tool**: `composed_embedded_workflow`

**Status**: Executed build workflow for ESP32

**Workflow Types**:
- `build` - Build firmware
- `test` - Run tests
- `deploy` - Deploy to devices
- `monitor` - Monitor device output

**Example**:
```python
mcp_unified-dev-tools_composed_embedded_workflow(
    workflow_type="build",
    target_platform="esp32",
    config={"environment": "esp32s3", "clean": False, "verbose": True}
)
```

### 6. Development Knowledge Query ✅
**Tool**: `query_development_knowledge`

**Status**: Queried mcp-prompts knowledge base

**Capabilities**:
- Query domain-specific knowledge (ESP32, Android, Conan, etc.)
- Context-aware guidance
- Best practices retrieval
- Pattern matching from learned configurations

**Example**:
```python
mcp_unified-dev-tools_query_development_knowledge(
    domain="esp32",
    topic="audio processing optimization",
    context={"project": "esp32-bpm-detector", "focus": "FFT configuration"}
)
```

### 7. Development Learning Capture ✅
**Tool**: `capture_development_learning`

**Status**: Available for capturing successful patterns

**Usage**:
- Capture successful development patterns
- Store optimizations for future use
- Cross-device learning
- Pattern documentation

## Connected Devices

**Detected Serial Devices**:
- `/dev/ttyACM0` - Active serial monitor
- `/dev/ttyUSB0` - Available for monitoring

## Integration with Project Skills

The unified-dev-tools server integrates with:

1. **embedded-audio-analyzer** skill
   - FFT optimization
   - Beat detection accuracy
   - Signal processing refinement

2. **dev-intelligence-orchestrator** skill
   - Build error analysis
   - Static code analysis
   - Test execution

3. **oms-cpp-style** skill
   - Code style compliance
   - OMS pattern application
   - Refactoring guidance

## Next Steps

### Recommended Workflows

1. **ESP32 Development**:
   ```bash
   # Start serial monitoring
   # Build firmware
   # Deploy to device
   # Monitor output
   ```

2. **Audio Optimization**:
   ```bash
   # Query knowledge for FFT optimization
   # Apply optimizations
   # Capture successful patterns
   ```

3. **Multi-Device Deployment**:
   ```bash
   # Detect all devices
   # Build for each platform
   # Deploy sequentially or in parallel
   ```

4. **Repository Maintenance**:
   ```bash
   # Scan for cleanup opportunities
   # Execute cleanup plan
   # Verify improvements
   ```

## Troubleshooting

### Serial Monitor Issues
- Check device permissions: `sudo chmod 666 /dev/ttyACM0`
- Verify baud rate matches firmware configuration
- Check log directory permissions

### Conan Package Issues
- Verify remote configuration: `conan remote list`
- Check authentication: `conan user -r sparetools`
- Review package search results

### Workflow Execution
- Check environment variables in MCP config
- Verify project directory path
- Review log files in configured directories

## Log Locations

- **ESP32 Logs**: `/home/sparrow/esp32_logs`
- **Android Logs**: `/home/sparrow/android_logs`
- **Conan Sessions**: `/home/sparrow/.mcp/conan_sessions.json`
- **MCP Prompts**: `/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts`

## References

- [Unified Dev Tools README](../UNIFIED_DEV_TOOLS_README.md)
- [MCP Tools Integration](../MCP_TOOLS_INTEGRATION.md)
- [Embedded Development Rules](../.cursor/rules/embedded-dev.mdc)
- [Claude Skills Configuration](../.cursor/rules/claude-skills.mdc)


