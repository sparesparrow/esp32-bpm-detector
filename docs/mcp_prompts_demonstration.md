# MCP Prompts Demonstration - ESP32 BPM Detector

## Status: ✅ MCP Prompts Server Operational

The mcp-prompts MCP server is configured and ready to use. This document demonstrates practical usage with the ESP32 BPM detector project.

## Configuration

**Location**: `.claude/mcp.json`

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

## Discovery Results

### Available Prompts (Sample)

From the prompt catalog, we found **79+ prompts** organized into categories:

#### ESP32 BPM Project-Specific Prompts
- ✅ `esp32-bpm-audio-calibration` - Microphone calibration
- ✅ `esp32-bpm-api-endpoint` - WiFi API creation
- ✅ `esp32-bpm-android-integration` - Android app integration

#### General Development Prompts
- ✅ `code-review-assistant` - Comprehensive code review
- ✅ `code-refactoring-assistant` - Code refactoring
- ✅ `architecture-design-assistant` - Architecture design
- ✅ `analysis-assistant` - Data analysis

#### Conan & Build System
- ✅ `automate-cpython-orchestration` - Conan automation
- ✅ `conan-toolchain-package-creation` - Toolchain packages

### Available Slash Commands

| Command | Purpose | Example Usage |
|---------|---------|---------------|
| `/code-review` | Code review assistance | `/code-review Review the BPM detector algorithm` |
| `/refactoring` | Refactoring suggestions | `/refactoring Refactor FFT implementation` |
| `/architecture` | Architecture design | `/architecture Design audio processing pipeline` |
| `/analysis` | Data analysis | `/analysis Analyze BPM detection accuracy` |
| `/conan` | Conan package management | `/conan Optimize ESP32 Conan profile` |
| `/optimization` | Code optimization | `/optimization Optimize FFT for ESP32 memory` |

## Practical Workflow Examples

### Example 1: Code Review Workflow

**Goal**: Review the BPM detector implementation for performance and memory issues.

**Steps**:

1. **Discover relevant prompts**:
   ```python
   mcp_mcp-prompts_list_prompts(tags=["code-review", "c++"])
   ```

2. **Get the prompt**:
   ```python
   mcp_mcp-prompts_get_prompt(id="code-review-assistant")
   ```

3. **Apply with context**:
   ```python
   mcp_mcp-prompts_apply_template(
       promptId="code-review-assistant",
       variables={
           "language": "C++",
           "code": "ESP32 BPM detector with FFT-based beat detection",
           "context": "Real-time audio processing on ESP32-S3, memory-constrained environment"
       }
   )
   ```

4. **Or use slash command in Cursor**:
   ```
   /code-review Review the BPM detector FFT implementation for memory efficiency
   ```

### Example 2: Audio Calibration Workflow

**Goal**: Calibrate microphone for optimal BPM detection.

**Steps**:

1. **Get ESP32-specific prompt**:
   ```python
   mcp_mcp-prompts_get_prompt(id="esp32-bpm-audio-calibration")
   ```

2. **Apply with hardware context**:
   ```python
   mcp_mcp-prompts_apply_template(
       promptId="esp32-bpm-audio-calibration",
       variables={
           "mic_type": "I2S MEMS microphone",
           "gain_level": "adaptive",
           "threshold": "auto-calibrated"
       }
   )
   ```

### Example 3: Architecture Design Workflow

**Goal**: Design a modular audio processing pipeline.

**Steps**:

1. **Use slash command**:
   ```
   /architecture Design a modular audio processing pipeline for ESP32 BPM detection
   ```

2. **Or get prompt directly**:
   ```python
   mcp_mcp-prompts_get_prompt(id="architecture-design-assistant")
   ```

### Example 4: Conan Profile Optimization

**Goal**: Optimize Conan profile for ESP32 cross-compilation.

**Steps**:

1. **Use slash command**:
   ```
   /conan Optimize Conan profile for ESP32-S3 cross-compilation
   ```

2. **Or search for Conan prompts**:
   ```python
   mcp_mcp-prompts_search_prompts(query="conan cross-compilation")
   ```

## Integration with Project Code

### BPM Detector Code Context

The project's BPM detector (`src/bpm_detector.cpp`, `src/bpm_detector.h`) includes:

- **FFT-based beat detection** using `arduinoFFT`
- **Memory-constrained implementation** for ESP32
- **Performance monitoring** with metrics
- **Hybrid detection** combining temporal and spectral analysis
- **Real-time processing** at 25kHz sample rate

### Applying Prompts to This Code

#### Code Review Focus Areas

When using `/code-review` or `code-review-assistant`:

1. **Memory Management**:
   - Buffer pre-allocation patterns
   - FFT buffer optimization
   - Circular buffer implementation

2. **Performance**:
   - FFT computation time
   - Real-time constraints
   - Sample rate handling

3. **Algorithm Quality**:
   - Beat detection accuracy
   - Confidence calculation
   - Signal quality metrics

#### Refactoring Opportunities

When using `/refactoring` or `code-refactoring-assistant`:

1. **Extract FFT Configuration**:
   - Move FFT parameters to config
   - Make window functions configurable
   - Allow runtime FFT size adjustment

2. **Improve Modularity**:
   - Separate temporal and spectral detection
   - Extract confidence calculation
   - Create detection strategy pattern

3. **Optimize Memory**:
   - Reduce buffer sizes where possible
   - Use fixed-point arithmetic
   - Implement memory pooling

## Creating Project-Specific Prompts

### Example: ESP32 FFT Optimization Prompt

You can create custom prompts for project-specific needs:

```python
mcp_mcp-prompts_create_prompt(
    name="esp32-bpm-fft-optimization",
    content="""
    Optimize FFT configuration for ESP32 BPM detection:
    
    - Current: FFT_SIZE={fft_size}, SAMPLE_RATE={sample_rate}
    - Target: Reduce memory usage while maintaining accuracy
    - Constraints: ESP32-S3 has {memory_limit}KB RAM
    - Window: {window_type}
    
    Provide recommendations for:
    1. Optimal FFT size for memory/accuracy tradeoff
    2. Window function selection
    3. Overlap strategy
    4. Buffer management
    """,
    category="embedded",
    tags=["esp32", "fft", "optimization", "bpm", "memory"],
    isTemplate=True,
    variables=["fft_size", "sample_rate", "memory_limit", "window_type"]
)
```

## Workflow Best Practices

### 1. Discovery First Pattern

**Always discover before creating**:

```python
# Step 1: Search for existing prompts
results = mcp_mcp-prompts_search_prompts(query="esp32 fft")

# Step 2: If found, use existing prompt
if results:
    prompt = results[0]
    # Apply with variables
else:
    # Step 3: Create new prompt if needed
    mcp_mcp-prompts_create_prompt(...)
```

### 2. Template Variable Mapping

**Map project context to template variables**:

| Template Variable | Project Context |
|-------------------|--------------|
| `language` | `"C++"` |
| `code` | `"BPM detector FFT implementation"` |
| `context` | `"ESP32-S3, 25kHz sample rate, memory-constrained"` |
| `mic_type` | `"I2S MEMS microphone"` |
| `fft_size` | `1024` |
| `sample_rate` | `25000` |

### 3. Iterative Refinement

**Update prompts based on results**:

```python
# After using a prompt and getting good results, update it
mcp_mcp-prompts_update_prompt(
    id="esp32-bpm-fft-optimization",
    content="Updated content with new insights...",
    tags=["esp32", "fft", "optimization", "bpm", "memory", "validated"]
)
```

## Integration with Unified Dev Tools

The mcp-prompts server integrates with unified-dev-tools:

```python
# Query development knowledge using mcp-prompts
mcp_unified-dev-tools_query_development_knowledge(
    domain="esp32",
    topic="audio processing optimization",
    context={
        "project": "esp32-bpm-detector",
        "focus": "FFT configuration and beat detection accuracy"
    }
)
```

This queries the mcp-prompts knowledge base for ESP32-specific patterns and solutions.

## Troubleshooting

### Issue: Template Application Fails

**Symptoms**: `Internal server error` when calling `get_prompt` or `apply_template`

**Possible Causes**:
- Prompt doesn't have template content
- Server configuration issue
- Missing required variables

**Solutions**:
1. Check prompt exists: `list_prompts()` to verify
2. Use slash commands instead (they may work when direct calls don't)
3. Create a new prompt with the content you need

### Issue: Slash Commands Not Available

**Symptoms**: Slash commands don't appear in Cursor

**Solutions**:
1. Verify MCP server is running
2. Check `.claude/mcp.json` configuration
3. Restart Cursor IDE
4. Review MCP server logs

## Next Steps

1. **Try Slash Commands**: Use `/code-review` or `/architecture` in Cursor chat
2. **Explore Prompts**: Use `list_prompts()` to discover all available prompts
3. **Create Custom Prompts**: Add ESP32-specific prompts for your workflow
4. **Integrate with Skills**: Combine prompts with Claude skills for enhanced workflows
5. **Document Patterns**: Save successful prompt applications for future use

## References

- [MCP Prompts Usage Guide](./mcp_prompts_usage_guide.md)
- [Unified Dev Tools Demo](./unified_dev_tools_demo.md)
- [Claude Skills Configuration](../.cursor/rules/claude-skills.mdc)
- [MCP Slash Commands](../.cursor/rules/mcp-prompts-slash-commands.mdc)
- [MCP Prompts GitHub](https://github.com/sparesparrow/mcp-prompts)


