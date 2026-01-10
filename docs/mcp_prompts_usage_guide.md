# MCP Prompts Usage Guide for ESP32 BPM Detector

## Overview

This guide demonstrates how to use the `mcp-prompts` MCP server to enhance ESP32 BPM detector development through prompt engineering as a service.

## Available Prompts for This Project

### ESP32-Specific Prompts

Based on the prompt catalog, the following prompts are relevant to this project:

1. **`esp32-bpm-audio-calibration`**
   - Calibrate microphone input for optimal BPM detection
   - Variables: `mic_type`, `gain_level`, `threshold`

2. **`esp32-bpm-api-endpoint`**
   - Create WiFi API endpoints for streaming BPM data
   - Variables: `endpoint_path`, `data_format`, `update_rate`

3. **`esp32-bpm-android-integration`**
   - Integrate Android app with ESP32 API
   - Variables: `api_url`, `polling_interval`, `ui_components`

### General Development Prompts

1. **`code-review-assistant`** - `/code-review`, `/development`, `/quality-assurance`, `/security`
   - Comprehensive code review with best practices
   - Variables: `language`, `code`, `context`

2. **`code-refactoring-assistant`** - `/refactoring`, `/optimization`
   - Source code refactoring assistance
   - Tags: refactoring, programming, optimization

3. **`architecture-design-assistant`** - `/architecture`, `/design`, `/programming`
   - Software architecture design assistance
   - Tags: architecture, design, programming

4. **`analysis-assistant`** - `/analysis`, `/insights`, `/ai-assistant`
   - Data analysis and transformation assistant
   - Tags: analysis, insights

### Conan & Build System Prompts

1. **`automate-cpython-orchestration`** - `/conan`, `/cpython`, `/zero-copy`, `/build-system`
   - Conan package management automation
   - Cross-compilation setup

2. **`conan-toolchain-package-creation`**
   - Create Conan packages for cross-compilation toolchains

## Workflow: Discovery First

### Step 1: Discover Available Prompts

Before performing a task, always discover what prompts are available:

```python
# List prompts by category
mcp_mcp-prompts_list_prompts(category="general", limit=20)

# Search for specific topics
mcp_mcp-prompts_search_prompts(query="ESP32 audio processing")

# List slash commands
mcp_mcp-prompts_list_slash_commands(limit=30)
```

### Step 2: Get and Apply Prompts

Once you've identified a relevant prompt:

```python
# Get a specific prompt
mcp_mcp-prompts_get_prompt(id="code-review-assistant")

# Apply template with variables
mcp_mcp-prompts_apply_template(
    promptId="code-review-assistant",
    variables={
        "language": "C++",
        "code": "ESP32 BPM detector implementation",
        "context": "Real-time audio processing on ESP32-S3"
    }
)
```

### Step 3: Use Slash Commands (Cursor IDE)

In Cursor's chat interface, you can use slash commands:

- `/code-review` - Request code review assistance
- `/refactoring` - Get refactoring suggestions
- `/architecture` - Architecture design guidance
- `/analysis` - Data analysis assistance
- `/conan` - Conan package management help

## Practical Examples

### Example 1: Code Review for BPM Detector

**Scenario**: Review the BPM detection algorithm for performance and memory issues.

**Workflow**:
1. Discover: `list_prompts(tags=["code-review", "c++"])`
2. Apply: Use `code-review-assistant` with:
   ```json
   {
     "language": "C++",
     "code": "BPM detector FFT implementation",
     "context": "ESP32-S3 with memory constraints, real-time audio processing"
   }
   ```
3. Review: Focus on memory usage, FFT optimization, and real-time constraints

### Example 2: Audio Calibration

**Scenario**: Calibrate microphone for better BPM detection accuracy.

**Workflow**:
1. Get prompt: `get_prompt("esp32-bpm-audio-calibration")`
2. Apply with hardware context:
   ```json
   {
     "mic_type": "I2S MEMS microphone",
     "gain_level": "auto",
     "threshold": "adaptive"
   }
   ```
3. Follow calibration steps from the prompt

### Example 3: Architecture Design

**Scenario**: Design a modular audio processing pipeline.

**Workflow**:
1. Use slash command: `/architecture`
2. Or get prompt: `get_prompt("architecture-design-assistant")`
3. Provide context about ESP32 constraints and requirements

### Example 4: Conan Package Management

**Scenario**: Optimize Conan profile for ESP32 cross-compilation.

**Workflow**:
1. Use slash command: `/conan`
2. Or get prompt: `get_prompt("automate-cpython-orchestration")`
3. Apply with ESP32-specific settings

## Integration with Project Skills

The mcp-prompts server integrates with project Claude skills:

### embedded-audio-analyzer
- Use prompts for FFT optimization guidance
- Apply audio calibration prompts
- Query knowledge base for ESP32 audio patterns

### dev-intelligence-orchestrator
- Use code review prompts for static analysis results
- Apply architecture prompts for project structure
- Query for build error solutions

### oms-cpp-style
- Use refactoring prompts to apply OMS patterns
- Apply code review prompts for style compliance

## Creating Custom Prompts

You can create project-specific prompts:

```python
mcp_mcp-prompts_create_prompt(
    name="esp32-bpm-fft-optimization",
    content="Optimize FFT configuration for ESP32 BPM detection...",
    category="embedded",
    tags=["esp32", "fft", "optimization", "bpm"],
    isTemplate=True,
    variables=["fft_size", "sample_rate", "window_type"]
)
```

## Best Practices

1. **Discovery First**: Always list/search prompts before creating new ones
2. **Template Variables**: Use templates with variables for reusable prompts
3. **Tag Organization**: Tag prompts appropriately for easy discovery
4. **Version Control**: Prompts are versioned - update existing prompts rather than creating duplicates
5. **Context Matters**: Always provide relevant context when applying templates

## Troubleshooting

### Prompt Not Found
- Check spelling and case sensitivity
- Use `list_prompts` to see available prompts
- Search with different keywords

### Template Application Fails
- Verify all required variables are provided
- Check variable names match template definition
- Review prompt metadata for requirements

### Slash Commands Not Working
- Verify prompt ID matches command definition
- Check MCP server is running and configured
- Review `.claude/mcp.json` configuration

## Related Documentation

- [MCP Prompts Server Documentation](https://github.com/sparesparrow/mcp-prompts)
- [Unified Dev Tools Integration](./unified_dev_tools_demo.md)
- [Claude Skills Configuration](../.cursor/rules/claude-skills.mdc)
- [MCP Slash Commands](../.cursor/rules/mcp-prompts-slash-commands.mdc)

## Example Prompt Catalog

### Available Slash Commands

| Command | Prompt ID | Description |
|---------|-----------|-------------|
| `/analysis` | `analysis-assistant` | Data analysis and insights |
| `/architecture` | `architecture-design-assistant` | Architecture design |
| `/refactoring` | `code-refactoring-assistant` | Code refactoring |
| `/code-review` | `code-review-assistant` | Code review |
| `/conan` | `automate-cpython-orchestration` | Conan automation |
| `/optimization` | `code-refactoring-assistant` | Code optimization |

### ESP32 BPM Project Prompts

| Prompt ID | Purpose | Variables |
|-----------|---------|-----------|
| `esp32-bpm-audio-calibration` | Microphone calibration | `mic_type`, `gain_level`, `threshold` |
| `esp32-bpm-api-endpoint` | WiFi API creation | `endpoint_path`, `data_format`, `update_rate` |
| `esp32-bpm-android-integration` | Android app integration | `api_url`, `polling_interval`, `ui_components` |

## Next Steps

1. **Explore Available Prompts**: Use `list_prompts()` to discover all available prompts
2. **Try Slash Commands**: Use `/code-review` or `/architecture` in Cursor chat
3. **Create Project Prompts**: Add ESP32-specific prompts for your workflow
4. **Integrate with Skills**: Combine prompts with Claude skills for enhanced workflows


