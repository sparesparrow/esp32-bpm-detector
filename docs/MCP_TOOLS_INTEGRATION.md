# ESP32 BPM Detector - MCP Tools Integration Guide

*Demonstrating practical MCP (Model Context Protocol) tools usage*

## Overview

This guide demonstrates how to use MCP tools to enhance ESP32 BPM detector development. MCP enables LLMs to interact with external systems through Resources, Prompts, Tools, and Sampling capabilities.

## MCP Server Configuration

The project uses the `mcp-prompts` server configured in `~/.cursor/mcp.json`:

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

## Available MCP Tools

### 1. MCP-Prompts Server

#### List Available Prompts
```javascript
// List all prompts
mcp_mcp-prompts_list_prompts({ limit: 50 })

// Search for specific prompts
mcp_mcp-prompts_search_prompts({ query: "esp32 bpm" })

// Get specific prompt
mcp_mcp-prompts_get_prompt({ id: "code-review-assistant" })
```

#### Apply Prompt Templates
```javascript
// Apply code review template
mcp_mcp-prompts_apply_template({
  promptId: "code-review-assistant",
  variables: {
    language: "cpp",
    code: "ESP32 BPM detector implementation",
    context: "Real-time audio processing on ESP32-S3"
}
})
```

#### Use Slash Commands
Available slash commands for quick access:
- `/code-review` - Code review assistance
- `/architecture` - Architecture design
- `/refactoring` - Code refactoring
- `/analysis` - Data analysis
- `/optimization` - Performance optimization

### 2. Sequential Thinking Server

For complex problem-solving and analysis:

```javascript
mcp_server-sequential-thinking_sequentialthinking({
  thought: "Analyze ESP32 BPM detector performance bottlenecks",
  thoughtNumber: 1,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

**Use Cases**:
- Performance optimization analysis
- Architecture decision making
- Debugging complex issues
- Multi-step problem solving

### 3. Memory Server

Store and retrieve project knowledge:

```javascript
// Create entities for project knowledge
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

// Search for stored knowledge
mcp_server-memory_search_nodes({
  query: "ESP32 performance optimization"
})
```

## Practical Examples

### Example 1: Performance Analysis with Sequential Thinking

```javascript
// Step 1: Identify bottlenecks
mcp_server-sequential-thinking_sequentialthinking({
  thought: "FFT computation takes 15ms which is 60% of our 25ms real-time budget. The ESP32-S3 has a hardware FPU, so floating-point operations are fast. However, the arduinoFFT library might not be fully optimized.",
  thoughtNumber: 1,
  totalThoughts: 5,
  nextThoughtNeeded: true
})

// Step 2: Memory analysis
mcp_server-sequential-thinking_sequentialthinking({
  thought: "Memory usage at 67% is concerning. The FFT buffers use 8KB, audio ring buffer 16KB, network buffers 16KB. We could move large buffers to PSRAM but ESP32-S3 doesn't have PSRAM in this config.",
  thoughtNumber: 2,
  totalThoughts: 5,
  nextThoughtNeeded: true
})

// Continue analysis...
```

### Example 2: Code Review with MCP-Prompts

```javascript
// Get code review prompt
const reviewPrompt = mcp_mcp-prompts_get_prompt({
  id: "code-review-assistant"
})

// Apply with project context
mcp_mcp-prompts_apply_template({
  promptId: "code-review-assistant",
  variables: {
    language: "cpp",
    code: readFile("src/bpm_detector.cpp"),
    context: "ESP32-S3 embedded system with real-time audio processing"
  }
})
```

### Example 3: Architecture Design

```javascript
// Use architecture design assistant
mcp_mcp-prompts_slash_command({
  command: "/architecture",
  variables: {
    context: "ESP32 BPM detector with FlatBuffers, WiFi, and real-time audio processing"
  }
})
```

## MCP Tools Workflow Integration

### Development Workflow

1. **Planning Phase**
   - Use `/architecture` for system design
   - Use sequential thinking for complex decisions
   - Store decisions in memory server

2. **Implementation Phase**
   - Use `/code-review` before committing
   - Use `/refactoring` for code improvements
   - Store implementation patterns in memory

3. **Testing Phase**
   - Use `/analysis` for test results
   - Use sequential thinking for debugging
   - Document findings in memory

4. **Review Phase**
   - Use `/code-review-assistant` for quality check
   - Use `/optimization` for performance tuning
   - Update memory with lessons learned

## Performance Optimization Analysis

Using MCP Sequential Thinking, we identified:

### 1. FFT Computation Optimization
- **Current**: 15ms per FFT window
- **Bottleneck**: arduinoFFT library not fully optimized
- **Solutions**:
  - Use ARM CMSIS DSP library (optimized for ESP32)
  - Implement fixed-point FFT (30-40% faster)
  - Optimize window function computation
  - Use FFT overlap more efficiently

### 2. Memory Management
- **Current**: 67% RAM utilization
- **Bottleneck**: Dynamic allocation causing fragmentation
- **Solutions**:
  - Use static allocation for fixed-size buffers
  - Implement memory pool allocator
  - Reduce FlatBuffers builder size
  - Optimize buffer sizes (512 vs 1024 FFT)

### 3. Task Scheduling
- **Current**: Single-core utilization
- **Bottleneck**: All tasks on same core
- **Solutions**:
  - Pin audio task to core 0, WiFi to core 1
  - Use task notifications instead of queues
  - Implement tickless idle mode
  - Use FreeRTOS timers for periodic tasks

### 4. Power Optimization
- **Current**: ~180mA active consumption
- **Bottleneck**: No power management
- **Solutions**:
  - Implement light sleep between samples (50-70% savings)
  - Use dynamic frequency scaling
  - Disable unused peripherals
  - Optimize WiFi power management
  - Batch network transmissions

## MCP Tools Best Practices

### 1. Use Sequential Thinking for Complex Problems
- Break down complex issues into steps
- Allow the tool to explore different approaches
- Review thought history for insights

### 2. Store Knowledge in Memory Server
- Create entities for key concepts
- Link related entities with relations
- Search memory before starting new tasks

### 3. Leverage Prompt Templates
- Use existing prompts for common tasks
- Create custom prompts for project-specific needs
- Apply templates with proper context

### 4. Combine Multiple MCP Tools
- Use sequential thinking for analysis
- Store results in memory server
- Apply prompts for documentation
- Use tools for automation

## Integration with ESP32 BPM Detector

### Current MCP Integration

1. **Code Review**: Automated code quality checks
2. **Architecture**: System design validation
3. **Performance Analysis**: Bottleneck identification
4. **Documentation**: Auto-generated guides

### Future Enhancements

1. **Custom ESP32 Prompts**: Project-specific prompts
2. **Automated Testing**: MCP-generated test cases
3. **Performance Monitoring**: Real-time metrics
4. **Debugging Assistant**: Issue resolution guidance

## MCP Tools API Reference

### MCP-Prompts Commands

```javascript
// List prompts
list_prompts({ limit: 50, category: "general" })

// Search prompts
search_prompts({ query: "esp32", category: "embedded" })

// Get prompt
get_prompt({ id: "code-review-assistant", version: "latest" })

// Apply template
apply_template({
  promptId: "code-review-assistant",
  variables: { language: "cpp", code: "...", context: "..." }
})

// Slash command
slash_command({
  command: "/code-review",
  variables: { language: "cpp", code: "..." }
})

// List slash commands
list_slash_commands({ limit: 20, category: "general" })
```

### Sequential Thinking Commands

```javascript
sequentialthinking({
  thought: "Analysis step",
  thoughtNumber: 1,
  totalThoughts: 5,
  nextThoughtNeeded: true,
  isRevision: false
})
```

### Memory Server Commands

```javascript
// Create entities
create_entities({
  entities: [{
    name: "Entity Name",
    entityType: "type",
    observations: ["observation1", "observation2"]
  }]
})

// Search nodes
search_nodes({ query: "search term" })

// Open nodes
open_nodes({ names: ["Entity Name"] })

// Add observations
add_observations({
  observations: [{
    entityName: "Entity Name",
    contents: ["new observation"]
  }]
})
```

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
- Verify prompt exists: `list_prompts({ query: "prompt-name" })`
- Check prompt directory: `ls /home/sparrow/mcp/data/prompts/`
- Ensure correct prompt ID spelling

### Sequential Thinking Errors
- Ensure `nextThoughtNeeded` is set correctly
- Don't exceed `totalThoughts` limit
- Use `isRevision` flag for corrections

## Conclusion

MCP tools provide powerful capabilities for ESP32 BPM detector development:

- **MCP-Prompts**: Reusable prompt templates for common tasks
- **Sequential Thinking**: Complex problem analysis
- **Memory Server**: Knowledge persistence and retrieval
- **Integration**: Seamless workflow enhancement

By leveraging these tools, we achieve:
- Faster development cycles
- Better code quality
- Comprehensive documentation
- Knowledge retention

*This guide demonstrates practical MCP tools usage for embedded systems development.*

