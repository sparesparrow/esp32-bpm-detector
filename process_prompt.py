#!/usr/bin/env python3
import json
import re

# Read the prompt file
with open('mcp-testing-prompt.json', 'r') as f:
    prompt_data = json.load(f)

content = prompt_data['content']

# Arguments provided
arguments = {
    'test_type': 'unit tests',
    'code_to_test': 'Authentication service',
    'testing_framework': 'pytest',
    'language': 'Python',
    'coverage_target': '95',
    'include_edge_cases': 'true',
    'include_performance_tests': 'false'
}

# Substitute handlebars variables {{variable}}
for var_name, var_value in arguments.items():
    pattern = rf'\{{\{{{var_name}\}}\}}'
    content = re.sub(pattern, str(var_value), content)

# Process Jinja2 conditionals
# Handle {% if include_edge_cases == "true" or include_edge_cases == true %}
if arguments.get('include_edge_cases') == 'true' or arguments.get('include_edge_cases') is True:
    # Keep the edge cases section
    content = re.sub(
        r'\{%\s*if\s+include_edge_cases\s*==\s*["\']true["\']\s+or\s+include_edge_cases\s*==\s*true\s*%\}(.*?)\{%\s*endif\s*%\}',
        r'\1',
        content,
        flags=re.DOTALL
    )
else:
    # Remove the edge cases section
    content = re.sub(
        r'\{%\s*if\s+include_edge_cases\s*==\s*["\']true["\']\s+or\s+include_edge_cases\s*==\s*true\s*%\}.*?\{%\s*endif\s*%\}',
        '',
        content,
        flags=re.DOTALL
    )

# Handle {% if include_performance_tests == "true" or include_performance_tests == true %}
if arguments.get('include_performance_tests') == 'true' or arguments.get('include_performance_tests') is True:
    # Keep the performance tests section
    content = re.sub(
        r'\{%\s*if\s+include_performance_tests\s*==\s*["\']true["\']\s+or\s+include_performance_tests\s*==\s*true\s*%\}(.*?)\{%\s*endif\s*%\}',
        r'\1',
        content,
        flags=re.DOTALL
    )
else:
    # Remove the performance tests section
    content = re.sub(
        r'\{%\s*if\s+include_performance_tests\s*==\s*["\']true["\']\s+or\s+include_performance_tests\s*==\s*true\s*%\}.*?\{%\s*endif\s*%\}',
        '',
        content,
        flags=re.DOTALL
    )

print(content)
