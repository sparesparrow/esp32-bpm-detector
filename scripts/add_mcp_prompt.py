#!/usr/bin/env python3
"""Script to add a prompt to mcp-prompts directory using mcp-prompts create_prompt format"""

import json
from datetime import datetime
from pathlib import Path

# Prompt data as specified by user (using Handlebars syntax)
prompt_data = {
    "name": "mcp-testing-prompt",
    "description": "Generate testing prompts for test case generation and quality assurance using MCP prompts",
    "content": "# Testing Prompt Generator\n\nGenerate comprehensive {{test_type}} for {{code_to_test}} using {{testing_framework}}.\n\n## Test Requirements\n\n**Language**: {{language}}\n**Framework**: {{testing_framework}}\n**Coverage Target**: {{coverage_target}}%\n**Code to Test**: {{code_to_test}}\n\n## Test Categories\n\n### 1. Basic Functionality Tests\n- Test normal operation paths\n- Verify expected outputs\n- Check return values and state changes\n\n### 2. Error Handling Tests\n- Test invalid inputs\n- Test error conditions\n- Verify error messages and exceptions\n\n{{#if include_edge_cases}}\n### 3. Edge Cases\n- Boundary conditions\n- Empty/null inputs\n- Maximum/minimum values\n- Special characters and encoding\n{{/if}}\n\n{{#if include_performance_tests}}\n### 4. Performance Tests\n- Response time benchmarks\n- Memory usage\n- Scalability tests\n- Load testing scenarios\n{{/if}}\n\n## Test Structure\n\nUse {{testing_framework}} best practices:\n- Clear test names describing what is being tested\n- Arrange-Act-Assert pattern\n- Isolated test cases\n- Proper setup and teardown\n\n## Coverage Goals\n\nAim for {{coverage_target}}% code coverage, focusing on:\n- All public methods/functions\n- Critical business logic\n- Error handling paths\n- Edge cases (if enabled)\n\n## Output Format\n\nProvide:\n1. Test file structure\n2. Individual test cases with descriptions\n3. Test data and fixtures\n4. Mock objects (if needed)\n5. Assertions and expected outcomes\n\nGenerate {{test_type}} that are maintainable, readable, and provide confidence in the code quality.\n",
    "tags": [
        "testing",
        "qa",
        "test-generation",
        "quality-assurance",
        "test-cases"
    ],
    "category": "testing",
    "isTemplate": True
}

# Target directory
target_dir = Path("/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts/testing")
target_file = target_dir / "mcp-testing-prompt.json"

# Create directory if it doesn't exist
target_dir.mkdir(parents=True, exist_ok=True)

# Write the prompt file
with open(target_file, 'w') as f:
    json.dump(prompt_data, f, indent=2)

print(f"✓ Created prompt file: {target_file}")
print(f"  Prompt ID: {prompt_data['id']}")
print(f"  Category: {prompt_data['category']}")
print(f"  Tags: {', '.join(prompt_data['tags'])}")
