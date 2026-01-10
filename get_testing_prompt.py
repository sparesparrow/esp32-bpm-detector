#!/usr/bin/env python3
"""Get mcp-testing-prompt with arguments"""

import sys
import json
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from mcp_prompts_integration import get_prompt_mcp
from template_utils import substitute_template_variables, extract_template_variables

# Arguments provided by user
arguments = {
    "test_type": "e2e tests",
    "code_to_test": "User registration flow",
    "testing_framework": "Selenium",
    "language": "Python",
    "coverage_target": "70",
    "include_edge_cases": "true",
    "include_performance_tests": "false"
}

# Get the prompt
print("Retrieving prompt 'mcp-testing-prompt' with arguments...", file=sys.stderr)
result = get_prompt_mcp("mcp-testing-prompt", arguments)

if result:
    print("\n" + "="*80)
    print("GENERATED TESTING PROMPT")
    print("="*80 + "\n")
    print(result)
    print("\n" + "="*80)
else:
    print("ERROR: Failed to retrieve prompt 'mcp-testing-prompt'", file=sys.stderr)
    print("Attempting to create prompt first...", file=sys.stderr)
    
    # Try to create the prompt if it doesn't exist
    from mcp_prompts_integration import create_prompt_mcp
    
    prompt_content = """# Testing Prompt Generator

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
{% if include_edge_cases == "true" %}
- Boundary conditions
- Empty/null inputs
- Maximum/minimum values
- Special characters and encoding
{% else %}
- Edge case testing is disabled for this test suite
{% endif %}

### 4. Performance Tests ({{include_performance_tests}})
{% if include_performance_tests == "true" %}
- Response time benchmarks
- Memory usage
- Scalability tests
- Load testing scenarios
{% else %}
- Performance testing is disabled for this test suite
{% endif %}

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
    
    created = create_prompt_mcp(
        name="mcp-testing-prompt",
        description="Generate testing prompts for test case generation and quality assurance using MCP prompts",
        content=prompt_content,
        tags=["testing", "qa", "test-generation", "quality-assurance", "test-cases"],
        category="testing",
        is_template=True
    )
    
    if created:
        print("Prompt created successfully. Retrieving...", file=sys.stderr)
        result = get_prompt_mcp("mcp-testing-prompt", arguments)
        if result:
            print("\n" + "="*80)
            print("GENERATED TESTING PROMPT")
            print("="*80 + "\n")
            print(result)
            print("\n" + "="*80)
        else:
            print("ERROR: Still failed to retrieve prompt after creation", file=sys.stderr)
            sys.exit(1)
    else:
        print("ERROR: Failed to create prompt", file=sys.stderr)
        sys.exit(1)
