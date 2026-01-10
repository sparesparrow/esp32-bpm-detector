# MCP Testing Prompt - Created ✅

## Summary

The `mcp-testing-prompt` has been successfully created in the mcp-prompts system and is ready for use.

---

## ✅ Status

- **Prompt Created**: ✅ `mcp-testing-prompt`
- **Template Variables**: ✅ Working
- **Template Substitution**: ✅ Verified
- **Multiple Scenarios**: ✅ Tested (unit, integration, e2e)

---

## 📋 Prompt Details

### Name
`mcp-testing-prompt`

### Description
Generate testing prompts for test case generation and quality assurance using MCP prompts

### Category
`testing`

### Tags
- `testing`
- `qa`
- `test-generation`
- `quality-assurance`
- `test-cases`

### Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `test_type` | Type of tests | `"unit tests"`, `"integration tests"`, `"e2e tests"` |
| `code_to_test` | Code or component to test | `"Authentication service"`, `"API endpoints"` |
| `testing_framework` | Testing framework | `"pytest"`, `"Jest"`, `"JUnit"`, `"Selenium"` |
| `language` | Programming language | `"Python"`, `"JavaScript"`, `"Java"` |
| `coverage_target` | Target code coverage (0-100) | `"95"`, `"80"`, `"70"` |
| `include_edge_cases` | Include edge case tests | `"true"` or `"false"` |
| `include_performance_tests` | Include performance tests | `"true"` or `"false"` |

---

## 🚀 Usage

### Via Python Scripts

```python
from scripts.mcp_prompts_integration import get_prompt_mcp

# Get prompt with template variables
prompt = get_prompt_mcp("mcp-testing-prompt", arguments={
    "test_type": "unit tests",
    "code_to_test": "Authentication service",
    "testing_framework": "pytest",
    "language": "Python",
    "coverage_target": "95",
    "include_edge_cases": "true",
    "include_performance_tests": "false"
})

print(prompt)
```

### Via cursor-agent CLI

```bash
cursor-agent --print --approve-mcps \
  "Use mcp-prompts get_prompt name=mcp-testing-prompt arguments={\"test_type\":\"unit tests\",\"code_to_test\":\"Authentication service\",\"testing_framework\":\"pytest\",\"language\":\"Python\",\"coverage_target\":\"95\",\"include_edge_cases\":\"true\",\"include_performance_tests\":\"false\"}"
```

### Via MCP Tools (in Cursor)

The prompt is available through the mcp-prompts MCP server configured in `~/.cursor/mcp.json`.

---

## 📝 Example Scenarios

### 1. Unit Tests

```python
args = {
    "test_type": "unit tests",
    "code_to_test": "Authentication service",
    "testing_framework": "pytest",
    "language": "Python",
    "coverage_target": "95",
    "include_edge_cases": "true",
    "include_performance_tests": "false"
}
```

**Result**: Generates comprehensive unit test prompts with edge cases, focusing on pytest best practices.

### 2. Integration Tests

```python
args = {
    "test_type": "integration tests",
    "code_to_test": "API endpoints",
    "testing_framework": "pytest",
    "language": "Python",
    "coverage_target": "80",
    "include_edge_cases": "true",
    "include_performance_tests": "true"
}
```

**Result**: Generates integration test prompts including performance tests and edge cases.

### 3. E2E Tests

```python
args = {
    "test_type": "e2e tests",
    "code_to_test": "User registration flow",
    "testing_framework": "Selenium",
    "language": "Python",
    "coverage_target": "70",
    "include_edge_cases": "true",
    "include_performance_tests": "false"
}
```

**Result**: Generates end-to-end test prompts using Selenium framework.

---

## 🧪 Verification

All tests passing:

```bash
python3 scripts/test_testing_prompt.py
```

**Results**:
- ✅ Unit tests scenario: Template variables substituted correctly
- ✅ Integration tests scenario: Template variables substituted correctly
- ✅ E2E tests scenario: Template variables substituted correctly

---

## 🔧 Template Features

### Supported Syntax

1. **Simple Variables**: `{{variable}}`
   - Substituted with provided values

2. **Conditionals**: `{{#if variable}}...{{/if}}`
   - Handled by mcp-prompts server
   - Shows/hides sections based on variable values

3. **Default Values**: `{{variable:default}}`
   - Supported by template_utils
   - Uses default if variable not provided

### Conditional Logic

The prompt uses handlebars-style conditionals:
- `{{#if include_edge_cases}}` - Shows edge cases section if enabled
- `{{#if include_performance_tests}}` - Shows performance tests section if enabled

These are processed by the mcp-prompts server, which supports full handlebars syntax.

---

## 📊 Integration Status

### ✅ Working

- Prompt creation in mcp-prompts system
- Template variable substitution
- Multiple test scenarios
- Integration with Python scripts
- Integration with cursor-agent CLI
- MCP server integration

### ⚠️ Notes

- Postgres adapter falls back to MCP tools if database unavailable
- Conditionals are handled by mcp-prompts server, not Python utilities
- Simple variable substitution works in both Postgres and MCP paths

---

## 🔗 Related

- **Template Utilities**: `scripts/template_utils.py`
- **MCP Integration**: `scripts/mcp_prompts_integration.py`
- **Postgres Adapter**: `scripts/postgres_prompts_adapter.py`
- **Test Script**: `scripts/test_testing_prompt.py`
- **Create Script**: `scripts/create_testing_prompt.py`

---

**Created**: 2026-01-01  
**Status**: ✅ Ready for use  
**Version**: 1.0.0
