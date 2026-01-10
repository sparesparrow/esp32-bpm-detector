#!/usr/bin/env python3
"""
Create the mcp-testing-prompt in mcp-prompts system.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp_prompts_integration import create_prompt_mcp

# Define the testing prompt template
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

### 3. Edge Cases
{{#if include_edge_cases}}
- Boundary conditions
- Empty/null inputs
- Maximum/minimum values
- Special characters and encoding
{{/if}}

### 4. Performance Tests
{{#if include_performance_tests}}
- Response time benchmarks
- Memory usage
- Scalability tests
- Load testing scenarios
{{/if}}

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

def main():
    """Create the mcp-testing-prompt."""
    print("Creating mcp-testing-prompt in mcp-prompts system...")
    
    success = create_prompt_mcp(
        name="mcp-testing-prompt",
        description="Generate testing prompts for test case generation and quality assurance using MCP prompts",
        content=prompt_content,
        tags=["testing", "qa", "test-generation", "quality-assurance", "test-cases"],
        category="testing",
        is_template=True
    )
    
    if success:
        print("✅ Successfully created mcp-testing-prompt")
        
        # Test retrieval with template variables
        print("\nTesting template substitution...")
        from mcp_prompts_integration import get_prompt_mcp
        
        test_args = {
            "test_type": "unit tests",
            "code_to_test": "Authentication service",
            "testing_framework": "pytest",
            "language": "Python",
            "coverage_target": "95",
            "include_edge_cases": "true",
            "include_performance_tests": "false"
        }
        
        prompt = get_prompt_mcp("mcp-testing-prompt", arguments=test_args)
        
        if prompt:
            print("✅ Prompt retrieved successfully")
            
            # Check if template variables were substituted
            if "{{" in prompt:
                print("⚠️  Warning: Some template variables may not have been substituted")
                import re
                remaining = re.findall(r'\{\{[^}]+\}\}', prompt)
                print(f"   Remaining: {remaining}")
            else:
                print("✅ All template variables substituted")
            
            # Check if values are present
            if "unit tests" in prompt and "Authentication service" in prompt and "pytest" in prompt:
                print("✅ Template values found in output")
            else:
                print("⚠️  Template values may not be in output")
            
            print(f"\nPrompt preview (first 500 chars):\n{prompt[:500]}...")
        else:
            print("❌ Failed to retrieve prompt")
            return 1
    else:
        print("❌ Failed to create mcp-testing-prompt")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
