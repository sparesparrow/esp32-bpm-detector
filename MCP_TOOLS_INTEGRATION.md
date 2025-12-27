# ESP32 BPM Detector - MCP Tools Integration

*Main entry point for MCP (Model Context Protocol) tools usage in the ESP32 BPM detector project*

## Quick Start

MCP tools enable AI assistants to interact with external systems, providing specialized capabilities for ESP32 embedded development, code review, architecture design, and performance analysis.

### Available MCP Servers

1. **MCP-Prompts** - Reusable prompt templates and specialized ESP32-BPM prompts
2. **Sequential Thinking** - Complex problem-solving and multi-step analysis
3. **Memory Server** - Knowledge persistence and retrieval
4. **GitHub MCP** - Repository management and collaboration
5. **Fetch MCP** - Web content retrieval

## MCP-Prompts Server

### Configuration

The MCP-Prompts server is configured in `~/.cursor/mcp.json`:

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

### ESP32-BPM-Specific Prompts

Use these prompts directly in Cursor chat with slash commands:

#### `/esp32-bpm-fft-configuration`
Optimize FFT parameters for BPM detection:
```
/esp32-bpm-fft-configuration
sample_rate: 25000
fft_size: 1024
window_type: hamming
```

#### `/esp32-bpm-api-endpoint`
Generate WiFi API endpoints for BPM data streaming:
```
/esp32-bpm-api-endpoint
endpoint_path: /api/v1/bpm
data_format: flatbuffers
update_rate: 10
```

#### `/esp32-bpm-audio-calibration`
Calibrate microphone input for optimal detection:
```
/esp32-bpm-audio-calibration
mic_type: analog
gain_level: 2.5
threshold: -30
```

#### `/esp32-bpm-android-integration`
Integrate Android app with ESP32 API:
```
/esp32-bpm-android-integration
api_url: http://192.168.1.100:80
polling_interval: 100
ui_components: bpm_display,spectrum_analyzer
```

#### `/esp32-bpm-display-integration`
Integrate OLED/7-segment displays:
```
/esp32-bpm-display-integration
display_type: oled
i2c_address: 0x3C
refresh_rate: 10
```

#### `/esp32-bpm-testing-strategy`
Generate testing strategies for BPM accuracy:
```
/esp32-bpm-testing-strategy
test_bpm_range: 60-200
audio_sources: sine_wave,real_music,white_noise
validation_method: statistical
```

### General Development Prompts

- `/code-review-assistant` - Comprehensive code review (language: cpp/java)
- `/architecture` or `/architecture-design-assistant` - System architecture design
- `/debugging-assistant` - Debugging assistance for audio/algorithm issues
- `/refactoring` - Code refactoring guidance
- `/analysis` - Performance analysis and metrics

## Sequential Thinking Server

For complex problem-solving and multi-step analysis:

**Use Cases**:
- Performance optimization analysis
- Architecture decision making
- Debugging complex issues
- Multi-step problem solving

**Example**: Analyze ESP32 BPM detector performance bottlenecks:
```javascript
mcp_server-sequential-thinking_sequentialthinking({
  thought: "FFT computation takes 15ms which is 60% of our 25ms real-time budget...",
  thoughtNumber: 1,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

## Memory Server

Store and retrieve project knowledge:

**Create Entities**:
```javascript
mcp_server-memory_create_entities({
  entities: [{
    name: "ESP32 BPM Detector",
    entityType: "project",
    observations: [
      "Real-time audio processing at 25kHz",
      "1024-point FFT for frequency analysis",
      "BPM detection range: 60-200 BPM"
    ]
  }]
})
```

**Search Knowledge**:
```javascript
mcp_server-memory_search_nodes({
  query: "ESP32 performance optimization"
})
```

## GitHub MCP Server

Repository management and collaboration:

- Create/update files in repositories
- Create issues and pull requests
- Search code and repositories
- Manage branches and commits

**Example**: Create an issue:
```javascript
mcp_github_create_issue({
  owner: "sparrow",
  repo: "esp32-bpm-detector",
  title: "Optimize FFT computation",
  body: "FFT takes 15ms, need to optimize for real-time processing"
})
```

## Development Workflow Integration

### Phase 1: BUILD
1. Use `/code-review-assistant` for code quality check
2. Use `/architecture` for system validation
3. Use `/esp32-bpm-fft-configuration` for parameter optimization

### Phase 2: DEPLOY
1. Use `/esp32-bpm-api-endpoint` for API generation
2. Use `/esp32-bpm-display-integration` for display setup
3. Deploy firmware: `pio run -e esp32-s3-release -t upload`

### Phase 3: TEST
1. Use `/esp32-bpm-testing-strategy` for test planning
2. Use `/esp32-bpm-audio-calibration` for hardware validation
3. Use `/analysis` for performance metrics

### Phase 4: REVIEW
1. Use `/code-review-assistant` for quality check
2. Use `/architecture` for architecture assessment
3. Use `/debugging-assistant` for issue resolution

## Performance Optimization Insights

Using MCP Sequential Thinking, we identified key optimizations:

### 1. FFT Computation
- **Current**: 15ms per FFT window
- **Solutions**: ARM CMSIS DSP library, fixed-point FFT, optimized window functions

### 2. Memory Management
- **Current**: 67% RAM utilization
- **Solutions**: Static allocation, memory pool allocator, reduce FlatBuffers builder size

### 3. Task Scheduling
- **Current**: Single-core utilization
- **Solutions**: Pin audio to core 0, WiFi to core 1, use task notifications

### 4. Power Optimization
- **Current**: ~180mA active consumption
- **Solutions**: Light sleep between samples, dynamic frequency scaling, batch network transmissions

## Best Practices

1. **Use Prompts Early**: Run code review before committing, validate architecture before major changes
2. **Iterative Improvement**: Apply MCP-Prompts feedback, re-run prompts after fixes
3. **Context Matters**: Provide detailed context, include relevant code snippets, specify hardware constraints
4. **Combine Tools**: Use sequential thinking for analysis, store results in memory, apply prompts for documentation
5. **Store Knowledge**: Create entities for key concepts, link related entities, search memory before starting new tasks

## Troubleshooting

### MCP Server Not Responding
```bash
# Check server status
ps aux | grep mcp-prompts

# Verify configuration
cat ~/.cursor/mcp.json | grep mcp-prompts

# Check logs
tail -f ~/.cursor/logs/mcp.log
```

### Prompt Not Found
- Verify prompt exists: Use `list_prompts` in Cursor
- Check prompt directory: `ls /home/sparrow/mcp/data/prompts/`
- Ensure correct prompt ID spelling

### Context Not Recognized
- Ensure you're in the correct workspace directory
- Check that repository-specific prompts are installed
- Verify MCP server configuration in Cursor settings

## Related Documentation

- **[docs/MCP_TOOLS_INTEGRATION.md](docs/MCP_TOOLS_INTEGRATION.md)** - Detailed MCP tools guide
- **[docs/mcp_workflow_guide.md](docs/mcp_workflow_guide.md)** - Complete workflow integration
- **[docs/MCP_PROMPTS_USAGE.md](docs/MCP_PROMPTS_USAGE.md)** - MCP-Prompts usage examples
- **[.cursor/rules/esp32-bpm-mcp-config.mdc](.cursor/rules/esp32-bpm-mcp-config.mdc)** - MCP configuration reference
- **[MCP_TOOLS_INTEGRATION_COMPLETE.md](MCP_TOOLS_INTEGRATION_COMPLETE.md)** - Integration status

## Quick Reference

### Slash Commands
- `/code-review` - Code review assistance
- `/architecture` - Architecture design
- `/refactoring` - Code refactoring
- `/analysis` - Data analysis
- `/optimization` - Performance optimization
- `/esp32-bpm-fft-configuration` - FFT optimization
- `/esp32-bpm-api-endpoint` - API endpoint generation
- `/esp32-bpm-audio-calibration` - Audio calibration
- `/esp32-bpm-android-integration` - Android integration
- `/esp32-bpm-display-integration` - Display integration
- `/esp32-bpm-testing-strategy` - Testing strategy

## Benefits

MCP tools integration provides:

- **Faster Development**: Automated code review and architecture validation
- **Higher Quality**: Comprehensive security and performance analysis
- **Better Documentation**: Auto-generated guides and API references
- **Knowledge Retention**: Persistent memory of project decisions and patterns
- **Expert Guidance**: Specialized ESP32-BPM prompts for domain expertise

## MCP Server Management Procedures

### Adding New ESP32-BPM Prompts

1. **Create Prompt File**: Add new `.json` file to `/home/sparrow/mcp/data/prompts/`
2. **Format Requirements**:
   ```json
   {
     "id": "esp32-bpm-your-prompt",
     "name": "ESP32-BPM Your Prompt",
     "description": "Brief description of what the prompt does",
     "content": "Prompt template with {{variables}}",
     "isTemplate": true,
     "variables": ["var1", "var2"],
     "tags": ["esp32-bpm-detector", "relevant-tags"],
     "createdAt": "2025-01-01T00:00:00.000Z",
     "updatedAt": "2025-01-01T00:00:00.000Z",
     "version": 1
   }
   ```
3. **Convert to Container Format**: Run conversion script to update `sample-prompts.json`
4. **Restart Container**: Kill and restart Docker container to load new prompts

### Troubleshooting MCP Issues

#### Server Not Responding
```bash
# Check running servers
ps aux | grep mcp

# Check Docker containers
docker ps | grep mcp

# Restart MCP services
docker kill $(docker ps -q --filter ancestor=sparesparrow/mcp-prompts)
```

#### Prompts Not Loading
```bash
# Check prompt files exist
ls -la /home/sparrow/mcp/data/prompts/

# Verify Docker volume mount
docker exec $(docker ps -q --filter ancestor=sparesparrow/mcp-prompts) ls -la /app/data/prompts/

# Reconvert prompts
python3 -c "conversion script here"
docker cp /tmp/sample-prompts.json CONTAINER_ID:/app/data/sample-prompts.json
docker kill CONTAINER_ID
```

#### Multiple Servers Running
```bash
# Kill conflicting servers
pkill -f "mcp-prompts-server"
pkill -f "node.*mcp-prompts"

# Keep only Docker container running
docker ps | grep mcp  # Should show only Docker container
```

### Performance Optimization

- **Memory Usage**: Monitor with `docker stats` during heavy usage
- **Restart Frequency**: Containers auto-restart; manual restart only needed for prompt updates
- **Concurrent Sessions**: Multiple containers may run for different Cursor sessions

### Backup and Recovery

```bash
# Backup prompts directory
cp -r /home/sparrow/mcp/data/prompts /home/sparrow/mcp/data/prompts.backup

# Restore from backup
cp -r /home/sparrow/mcp/data/prompts.backup /home/sparrow/mcp/data/prompts
```

---

*This guide provides a quick reference for MCP tools integration. For detailed usage, see the [docs](docs/) directory.*

