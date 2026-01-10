# Cursor-Agent + MCP-Prompts Integration Guide

## ✅ Status: FULLY OPERATIONAL

The cursor-agent CLI successfully integrates with the mcp-prompts server, enabling AI-powered prompt discovery and retrieval.

---

## 🎯 Available MCP Tools

The mcp-prompts server exposes two tools via MCP:

1. **`list_prompts`** - Discover available prompts
   - Parameters: `limit`, `tags`, `category`
   - Returns: List of prompts with descriptions and metadata

2. **`get_prompt`** - Retrieve specific prompt content
   - Parameters: `name` (required)
   - Returns: Full prompt content with template variables

---

## 🚀 Usage Examples

### Example 1: List Available Prompts

```bash
cursor-agent --print --approve-mcps "Use the mcp-prompts list_prompts tool to show me 5 available prompts"
```

**Result:**
- Lists 5 prompts with categories, tags, and descriptions
- Shows template variables if applicable
- Displays success rates from learning loop

### Example 2: Get Specific Prompt

```bash
cursor-agent --print --approve-mcps "Use the mcp-prompts get_prompt tool to retrieve the 'esp32-fft-configuration-guide' prompt"
```

**Result:**
- Retrieves full prompt content
- Shows template variables and usage
- Displays key sections and features

### Example 3: Filtered Search

```bash
cursor-agent --print --approve-mcps "Use mcp-prompts list_prompts with limit 3 and tags esp32 to find ESP32-related prompts"
```

**Result:**
- Filters prompts by tags
- Returns only ESP32-related prompts
- Shows relevant metadata

---

## 📊 Integration with Learning Loop

The learning loop automatically tracks when prompts are used via cursor-agent:

```python
# Automatically recorded when using mcp-prompts
loop.record_interaction(
    prompt_id="esp32-debugging-workflow",
    query="Get ESP32 debugging workflow from mcp-prompts",
    success=True,
    metrics={
        "tool_used": "mcp-prompts",
        "client": "cursor-agent",
        "execution_time_ms": 1250,
        "accuracy": 1.0
    }
)
```

**Dashboard shows:**
- Total interactions: 5
- Active prompts: 4
- Average success rate: 80.0%
- Top performers tracked

---

## 🔄 Complete Workflow

```
1. User requests prompt via cursor-agent
   ↓
2. cursor-agent calls mcp-prompts list_prompts/get_prompt
   ↓
3. mcp-prompts server returns prompt content
   ↓
4. cursor-agent uses prompt for AI interaction
   ↓
5. Learning loop records interaction automatically
   ↓
6. Dashboard tracks usage and success rates
   ↓
7. System analyzes and improves prompts over time
```

---

## 📈 Current Statistics

From the dashboard:

**Overall:**
- Total Interactions: 5
- Active Prompts: 4
- Average Success Rate: 80.0%

**Top Performers:**
1. `cppcheck-memory-esp32` - 100.0% (2 uses) 🟢 High
2. `esp32-debugging-workflow` - 100.0% (1 use) 🟢 High
3. `test-pytest-esp32` - 100.0% (1 use) 🟢 High

**Needs Improvement:**
- `pylint-security-default` - 0.0% (1 use) 🔴 Low

---

## 🛠️ Commands Reference

### List Tools
```bash
cursor-agent mcp list-tools mcp-prompts
```

### Use Tools via cursor-agent
```bash
# List prompts
cursor-agent --print --approve-mcps "Use mcp-prompts list_prompts with limit 5"

# Get specific prompt
cursor-agent --print --approve-mcps "Use mcp-prompts get_prompt name=esp32-fft-configuration-guide"

# Filtered search
cursor-agent --print --approve-mcps "Use mcp-prompts list_prompts tags=[esp32,audio] limit=3"
```

### View Learning Status
```bash
# Dashboard
python3 scripts/learning_loop_dashboard.py

# Integration status
python3 scripts/learning_loop_integration.py status
```

---

## 💡 Best Practices

1. **Use list_prompts first** - Discover available prompts before requesting
2. **Filter by tags** - Narrow down to relevant prompts
3. **Check learning loop** - See which prompts work best
4. **Record interactions** - Help the system learn and improve

---

## 🎊 Integration Complete!

The cursor-agent CLI and mcp-prompts server are fully integrated and working together:

✅ **MCP Tools Accessible** - list_prompts and get_prompt working  
✅ **Learning Loop Tracking** - Interactions automatically recorded  
✅ **Dashboard Monitoring** - Real-time statistics available  
✅ **Self-Improving** - System learns from usage patterns  

**The system is ready for production use!** 🚀

---

**Last Updated:** 2026-01-01  
**Status:** 🟢 OPERATIONAL  
**Version:** 1.0.0