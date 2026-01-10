# MCP Debugging Prompt - Created ✅

## Summary

The `mcp-debugging-prompt` has been successfully created in the mcp-prompts system for systematic debugging and issue resolution.

---

## ✅ Status

- **Prompt Created**: ✅ `mcp-debugging-prompt`
- **Template Variables**: ✅ Working
- **Template Substitution**: ✅ Verified
- **Multiple Scenarios**: ✅ Tested (critical, performance, development)

---

## 📋 Prompt Details

### Name
`mcp-debugging-prompt`

### Description
Generate debugging prompts for troubleshooting and issue resolution using MCP prompts

### Category
`debugging`

### Tags
- `debugging`
- `troubleshooting`
- `issue-resolution`
- `error-handling`
- `diagnostics`

### Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `issue_description` | Description of the problem | `"API returning 500 errors"` |
| `error_message` | Error message or symptoms | `"Internal Server Error: Database connection failed"` |
| `environment` | Environment | `"development"`, `"staging"`, `"production"` |
| `language` | Programming language | `"Python"`, `"JavaScript"`, `"Java"` |
| `urgency` | Urgency level | `"low"`, `"medium"`, `"high"`, `"critical"` |
| `include_logs` | Include log analysis | `"true"` or `"false"` |
| `include_solutions` | Include solution recommendations | `"true"` or `"false"` |

---

## 🚀 Usage

### Via Python Scripts

```python
from scripts.mcp_prompts_integration import get_prompt_mcp

# Get prompt with template variables
prompt = get_prompt_mcp("mcp-debugging-prompt", arguments={
    "issue_description": "API returning 500 errors",
    "error_message": "Internal Server Error: Database connection failed",
    "environment": "production",
    "language": "Python",
    "urgency": "critical",
    "include_logs": "true",
    "include_solutions": "true"
})

print(prompt)
```

### Via cursor-agent CLI

```bash
cursor-agent --print --approve-mcps \
  "Use mcp-prompts get_prompt name=mcp-debugging-prompt arguments={\"issue_description\":\"API returning 500 errors\",\"error_message\":\"Internal Server Error\",\"environment\":\"production\",\"language\":\"Python\",\"urgency\":\"critical\",\"include_logs\":\"true\",\"include_solutions\":\"true\"}"
```

### Via MCP Tools (in Cursor)

The prompt is available through the mcp-prompts MCP server configured in `~/.cursor/mcp.json`.

---

## 📝 Example Scenarios

### 1. Critical Production Bug

```python
args = {
    "issue_description": "API returning 500 errors",
    "error_message": "Internal Server Error: Database connection failed",
    "environment": "production",
    "language": "Python",
    "urgency": "critical",
    "include_logs": "true",
    "include_solutions": "true"
}
```

**Result**: Generates comprehensive debugging guide with log analysis and solution recommendations for critical production issues.

### 2. Performance Issue

```python
args = {
    "issue_description": "Slow response times",
    "error_message": "API responses taking 10+ seconds",
    "environment": "production",
    "language": "Python",
    "urgency": "high",
    "include_logs": "true",
    "include_solutions": "true"
}
```

**Result**: Generates performance debugging guide with log analysis and optimization recommendations.

### 3. Development Issue

```python
args = {
    "issue_description": "Tests failing locally",
    "error_message": "AssertionError: Expected 5, got 3",
    "environment": "development",
    "language": "Python",
    "urgency": "medium",
    "include_logs": "false",
    "include_solutions": "true"
}
```

**Result**: Generates development debugging guide focused on code analysis without log review.

---

## 🔧 Template Features

### Supported Syntax

1. **Simple Variables**: `{{variable}}`
   - Substituted with provided values

2. **Conditionals**: `{{#if variable}}...{{/if}}`
   - Handled by mcp-prompts server
   - Shows/hides sections based on variable values
   - Used for optional sections (logs, solutions)

### Conditional Logic

The prompt uses handlebars-style conditionals:
- `{{#if include_logs}}` - Shows log analysis section if enabled
- `{{#if include_solutions}}` - Shows solution recommendations if enabled

These are processed by the mcp-prompts server, which supports full handlebars syntax.

---

## 🧪 Debugging Process

The prompt guides through a systematic debugging process:

1. **Problem Analysis** - Understand the issue
2. **Root Cause Investigation** - Initial checks and code analysis
3. **Log Analysis** (if enabled) - Review logs and patterns
4. **Diagnostic Steps** - Systematic debugging approach
5. **Solution Recommendations** (if enabled) - Fix and prevention
6. **Documentation** - Document findings and solutions

---

## 📊 Integration Status

### ✅ Working

- Prompt creation in mcp-prompts system
- Template variable substitution
- Multiple debugging scenarios
- Integration with Python scripts
- Integration with cursor-agent CLI
- MCP server integration
- Conditional sections (logs, solutions)

### ⚠️ Notes

- Postgres adapter falls back to MCP tools if database unavailable
- Conditionals are handled by mcp-prompts server, not Python utilities
- Simple variable substitution works in both Postgres and MCP paths
- MCP connection errors are handled gracefully

---

## 🔗 Related

- **Template Utilities**: `scripts/template_utils.py`
- **MCP Integration**: `scripts/mcp_prompts_integration.py`
- **Postgres Adapter**: `scripts/postgres_prompts_adapter.py`
- **Test Script**: `scripts/test_debugging_prompt.py`
- **Create Script**: `scripts/create_debugging_prompt.py`
- **Related Prompts**:
  - `mcp-testing-prompt`: Test generation
  - `mcp-analysis-prompt`: Code analysis
  - `mcp-code-generator`: Code generation

---

## 🐛 Troubleshooting

### MCP Connection Errors

If you see "Connection closed" errors:

1. **Check MCP Server Status**:
   ```bash
   # Check if mcp-prompts server is running
   ps aux | grep mcp-prompts
   ```

2. **Restart MCP Server**:
   - Restart Cursor to reload MCP servers
   - Or restart the mcp-prompts server manually

3. **Use Postgres Adapter**:
   - Set up Postgres: `scripts/setup_postgres_mcp_prompts.sh`
   - The adapter will use Postgres directly

4. **Fallback to cursor-agent**:
   - The integration automatically falls back to cursor-agent
   - Prompts will still work, just via different path

### Template Variables Not Substituting

1. **Check Variable Names**: Ensure they match exactly (case-sensitive)
2. **Check Template Syntax**: Use `{{variable}}` not `{{{variable}}}`
3. **Verify MCP Server**: Ensure mcp-prompts server supports handlebars

---

**Created**: 2026-01-01  
**Status**: ✅ Ready for use  
**Version**: 1.0.0
