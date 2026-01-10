#!/usr/bin/env python3
"""Render mcp-testing-prompt with provided arguments"""

import sys
import re
sys.path.insert(0, 'scripts')
from template_utils import substitute_template_variables

# Prompt template from create_mcp_testing_prompt.py
template = """# Testing Prompt Generator

Generate comprehensive {{test_type}} for {{code_to_test}} using {{testing_framework}}.

## Test Requirements

**Language**: {{language}}
**Framework**: {{testing_framework}}
**Coverage Target**: {{coverage_target}}%
**Code to Test**: {{code_to_test}}

## Test Categories

### 1. Basic Functionality Tests
- Test normal operation paths
- Verify expected outputs
- Check return values and state changes

### 2. Error Handling Tests
- Test invalid inputs
- Test error conditions
- Verify error messages and exceptions

### 3. Edge Cases ({{include_edge_cases}})
{{#if include_edge_cases}}
- Boundary conditions
- Empty/null inputs
- Maximum/minimum values
- Special characters and encoding
{{/if}}
{{#unless include_edge_cases}}
- Edge case testing is disabled for this test suite
{{/unless}}

### 4. Performance Tests ({{include_performance_tests}})
{{#if include_performance_tests}}
- Response time benchmarks
- Memory usage
- Scalability tests
- Load testing scenarios
{{/if}}
{{#unless include_performance_tests}}
- Performance testing is disabled for this test suite
{{/unless}}

## Test Structure

Use {{testing_framework}} best practices:
- Clear test names describing what is being tested
- Arrange-Act-Assert pattern
- Isolated test cases
- Proper setup and teardown

## Coverage Goals

Aim for {{coverage_target}}% code coverage, focusing on:
- All public methods/functions
- Critical business logic
- Error handling paths
- Edge cases (if enabled)

## Output Format

Provide:
1. Test file structure
2. Individual test cases with descriptions
3. Test data and fixtures
4. Mock objects (if needed)
5. Assertions and expected outcomes

Generate {{test_type}} that are maintainable, readable, and provide confidence in the code quality.
"""

# Arguments provided
arguments = {
    "test_type": "e2e tests",
    "code_to_test": "User registration flow",
    "testing_framework": "Selenium",
    "language": "Python",
    "coverage_target": "70",
    "include_edge_cases": "true",
    "include_performance_tests": "false"
}

# First, substitute simple variables
result = substitute_template_variables(template, arguments)

# Handle Handlebars conditionals {{#if}} and {{#unless}}
# For {{#if include_edge_cases}}
if arguments.get("include_edge_cases") == "true":
    # Keep the content between {{#if include_edge_cases}} and {{/if}}
    result = re.sub(
        r'\{\{#if include_edge_cases\}\}\n(.*?)\n\{\{/if\}\}',
        r'\1',
        result,
        flags=re.DOTALL
    )
    # Remove the {{#unless}} block
    result = re.sub(
        r'\{\{#unless include_edge_cases\}\}\n.*?\n\{\{/unless\}\}',
        '',
        result,
        flags=re.DOTALL
    )
else:
    # Remove the {{#if}} block
    result = re.sub(
        r'\{\{#if include_edge_cases\}\}\n.*?\n\{\{/if\}\}',
        '',
        result,
        flags=re.DOTALL
    )
    # Keep the {{#unless}} content
    result = re.sub(
        r'\{\{#unless include_edge_cases\}\}\n(.*?)\n\{\{/unless\}\}',
        r'\1',
        result,
        flags=re.DOTALL
    )

# For {{#if include_performance_tests}}
if arguments.get("include_performance_tests") == "true":
    # Keep the content between {{#if include_performance_tests}} and {{/if}}
    result = re.sub(
        r'\{\{#if include_performance_tests\}\}\n(.*?)\n\{\{/if\}\}',
        r'\1',
        result,
        flags=re.DOTALL
    )
    # Remove the {{#unless}} block
    result = re.sub(
        r'\{\{#unless include_performance_tests\}\}\n.*?\n\{\{/unless\}\}',
        '',
        result,
        flags=re.DOTALL
    )
else:
    # Remove the {{#if}} block
    result = re.sub(
        r'\{\{#if include_performance_tests\}\}\n.*?\n\{\{/if\}\}',
        '',
        result,
        flags=re.DOTALL
    )
    # Keep the {{#unless}} content
    result = re.sub(
        r'\{\{#unless include_performance_tests\}\}\n(.*?)\n\{\{/unless\}\}',
        r'\1',
        result,
        flags=re.DOTALL
    )

# Clean up any remaining template syntax
result = re.sub(r'\{\{[^}]+\}\}', '', result)

# Clean up extra blank lines
result = re.sub(r'\n{3,}', '\n\n', result)

print(result)
