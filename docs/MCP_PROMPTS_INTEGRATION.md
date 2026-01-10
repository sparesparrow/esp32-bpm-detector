# MCP Prompts Integration with Learning Loop

## Overview

The learning loop workflow now integrates with the **mcp-prompts** MCP server to leverage a centralized, version-controlled prompt library. This enables:

1. **Discovery-First Approach**: Before performing tasks, the system discovers relevant prompts
2. **Template Hydration**: Dynamic prompts with context-specific variables
3. **Self-Improvement**: Prompts can be created/updated based on learning loop results
4. **Standardization**: Consistent prompt usage across all development phases

---

## Available MCP Tools

### 1. `list_prompts`
**Purpose**: Discover available prompts matching criteria

**Usage in Learning Loop:**
```python
from mcp_prompts_integration import discover_relevant_prompts

# Discover prompts for ESP32 code review
prompts = discover_relevant_prompts(
    task_type="code-review",
    context={"platform": "esp32", "language": "cpp", "embedded": True}
)
```

**Parameters:**
- `tags`: Filter by tags (e.g., `["esp32", "embedded", "code-review"]`)
- `category`: Filter by category (e.g., `"coding"`, `"embedded"`)
- `search`: Fuzzy search against names/descriptions
- `limit`: Maximum results to return

### 2. `get_prompt`
**Purpose**: Retrieve specific prompt with optional template variables

**Usage in Learning Loop:**
```python
from mcp_prompts_integration import get_prompt_mcp

# Get code review prompt with ESP32 context
prompt = get_prompt_mcp(
    name="code-review-assistant",
    arguments={
        "platform": "esp32",
        "language": "cpp",
        "code_path": "src/"
    }
)
```

**Parameters:**
- `name`: Prompt identifier (required)
- `arguments`: Template variables for handlebars-style `{{variables}}`

### 3. `create_prompt`
**Purpose**: Save new prompts discovered during learning

**Usage in Learning Loop:**
```python
from mcp_prompts_integration import create_prompt_mcp

# Create a new prompt based on successful learning loop results
create_prompt_mcp(
    name="esp32-bpm-detector-review",
    description="Specialized code review for ESP32 BPM detector firmware",
    content="Review ESP32 firmware for BPM detection...",
    tags=["esp32", "audio", "bpm", "embedded"],
    category="embedded",
    is_template=True
)
```

### 4. `update_prompt`
**Purpose**: Refine existing prompts based on learning loop analysis

**Usage in Learning Loop:**
```python
from mcp_prompts_integration import update_prompt_mcp

# Update prompt based on improvement suggestions
update_prompt_mcp(
    name="code-review-assistant",
    updates={
        "content": "Enhanced content based on learning loop analysis...",
        "tags": ["code-review", "enhanced", "learning-optimized"]
    }
)
```

---

## Integration Points

### Code Review Phase

**Before (Hardcoded):**
```python
review_query = "Review ESP32 firmware code for bugs..."
```

**After (MCP-Prompts):**
```python
# Discover relevant prompts
prompts = discover_relevant_prompts("code-review", {"platform": "esp32"})

# Get best matching prompt
prompt = get_prompt_mcp(
    name=prompts[0]["name"],
    arguments={"platform": "esp32", "code_path": "src/"}
)

# Use prompt in review
review_query = f"{prompt}\n\nReview code in src/ using the above guidelines."
```

### Refactoring Phase

**Integration:**
```python
# Get refactoring prompt
refactor_prompt = get_prompt_mcp(
    name="code-refactoring-assistant",
    arguments={
        "language": "cpp",
        "target": "esp32",
        "constraints": "memory-constrained, real-time"
    }
)
```

### Architecture Analysis

**Integration:**
```python
# Get architecture prompt
arch_prompt = get_prompt_mcp(
    name="architecture-design-assistant",
    arguments={
        "domain": "embedded-systems",
        "constraints": "ESP32, real-time audio processing"
    }
)
```

---

## Prompt Discovery Workflow

```
Task Requested
    ↓
Discover Relevant Prompts
    ├─ list_prompts(tags=[task_type, platform, language])
    └─ Filter by relevance score
    ↓
Select Best Prompt
    ├─ Match tags
    ├─ Check category
    └─ Verify template compatibility
    ↓
Hydrate Template
    ├─ get_prompt(name, arguments={context})
    └─ Fill {{variables}} with actual values
    ↓
Execute Task
    ├─ Use prompt in cursor-agent command
    └─ Record results in learning loop
    ↓
Learn & Improve
    ├─ Analyze prompt effectiveness
    ├─ Create new prompts for successful patterns
    └─ Update existing prompts based on failures
```

---

## Available Prompts for ESP32/Android Workflow

### Code Review
- **code-review-assistant**: Comprehensive code review template
- **code-refactoring-assistant**: Refactoring guidance
- **architecture-design-assistant**: Architecture analysis

### Embedded Development
- **esp32-architecture-knowledge**: ESP32-specific knowledge
- **embedded-memory-constrained-analysis**: Memory analysis for embedded
- **static-analysis-tools-knowledge**: Static analysis guidance

### Development Workflows
- **cpp-static-analysis-workflow**: C++ analysis workflow
- **performance-regression-diagnosis**: Performance debugging
- **debugging-assistant**: General debugging guidance

### Android Development
- **code-review-assistant**: (works for Android with Kotlin context)
- **architecture-design-assistant**: (works for Android architecture)

---

## Self-Improving Prompt Creation

The learning loop can automatically create new prompts based on successful patterns:

```python
# After successful code review cycle
if review_success and issues_found > 0:
    # Create specialized prompt for this project
    create_prompt_mcp(
        name=f"esp32-bpm-{cycle_num}-review",
        description=f"ESP32 BPM detector review pattern from cycle {cycle_num}",
        content=refined_review_instructions,
        tags=["esp32", "bpm", "cycle-optimized"],
        category="embedded"
    )
```

---

## Prompt Update Based on Learning

When the learning loop identifies improvements:

```python
# Analyze prompt performance
analysis = loop.analyze_prompt("code-review-assistant")

if analysis.improvement_opportunities:
    # Update prompt with improvements
    improved_content = apply_improvements(
        original_content,
        analysis.improvement_opportunities
    )
    
    update_prompt_mcp(
        name="code-review-assistant",
        updates={
            "content": improved_content,
            "version": increment_version(),
            "tags": analysis.improvement_opportunities
        }
    )
```

---

## Configuration

### MCP Server Setup

The mcp-prompts server should be configured in `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "mcp-prompts": {
      "command": "mcp-prompts",
      "args": ["--storage", "file", "--path", "/path/to/prompts"]
    }
  }
}
```

### Integration Module

The `mcp_prompts_integration.py` module provides:
- Wrapper functions for MCP tools
- Fallback to cursor-agent if MCP unavailable
- Prompt discovery helpers
- Template hydration utilities

---

## Benefits

1. **Centralized Management**: All prompts in one version-controlled location
2. **Reusability**: Prompts shared across projects and team members
3. **Self-Improvement**: Learning loop can refine prompts automatically
4. **Context-Aware**: Templates adapt to specific platforms/languages
5. **Discovery**: Never miss relevant prompts - system discovers them automatically

---

## Example: Complete Workflow

```python
# 1. Discover prompts for ESP32 code review
prompts = discover_relevant_prompts(
    "code-review",
    {"platform": "esp32", "language": "cpp"}
)

# 2. Get best matching prompt with context
prompt = get_prompt_mcp(
    name=prompts[0]["name"],
    arguments={
        "platform": "esp32",
        "language": "cpp",
        "code_path": "src/",
        "constraints": "memory-constrained, real-time"
    }
)

# 3. Use in code review
review_result = review_code_with_prompt(prompt, "src/")

# 4. Record in learning loop
loop.record_interaction(
    prompt_id=prompts[0]["name"],
    query="ESP32 code review",
    success=review_result["success"],
    metrics=review_result["metrics"]
)

# 5. If successful pattern, create specialized prompt
if review_result["success"] and review_result["issues_found"] > 5:
    create_prompt_mcp(
        name="esp32-bpm-specialized-review",
        description="Specialized review for ESP32 BPM detector",
        content=refine_prompt(prompt, review_result),
        tags=["esp32", "bpm", "specialized"]
    )
```

---

## Status

✅ **MCP Prompts Integration**: Complete  
✅ **Discovery Workflow**: Implemented  
✅ **Template Hydration**: Supported  
✅ **Self-Improvement**: Enabled  
✅ **Learning Loop Integration**: Active  

**The learning loop now leverages the full power of mcp-prompts for intelligent, context-aware prompt management!** 🚀

---

**Created**: 2026-01-01  
**Status**: 🟢 OPERATIONAL  
**Version**: 1.0.0
