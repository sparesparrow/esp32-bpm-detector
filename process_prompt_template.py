#!/usr/bin/env python3
"""Process mcp-testing-prompt template with provided arguments"""

import sys
import json
import re
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from template_utils import substitute_template_variables

def process_jinja2_conditionals(content: str, variables: dict) -> str:
    """Process Jinja2-style {% if %} conditionals"""
    result = content
    
    # Process {% if %} blocks
    pattern = r'\{%\s*if\s+([^%]+)\s*%\}(.*?)\{%\s*endif\s*%\}'
    
    def evaluate_condition(match):
        condition = match.group(1).strip()
        block_content = match.group(2)
        
        # Simple condition evaluation
        # Handle: include_edge_cases == "true" or include_edge_cases == true
        if '==' in condition:
            parts = condition.split('==')
            var_name = parts[0].strip()
            value = parts[1].strip().strip('"').strip("'")
            
            # Get variable value
            var_value = variables.get(var_name)
            
            # Check if condition is true
            if str(var_value).lower() == value.lower() or (value.lower() == 'true' and str(var_value).lower() in ('true', '1', 'yes')):
                return block_content
            else:
                return ''
        else:
            # Default: check if variable is truthy
            var_name = condition.strip()
            var_value = variables.get(var_name)
            if var_value and str(var_value).lower() not in ('false', '0', 'no', ''):
                return block_content
            else:
                return ''
    
    # Replace all {% if %} blocks
    result = re.sub(pattern, evaluate_condition, result, flags=re.DOTALL)
    
    return result

def main():
    # Load prompt
    prompt_file = Path(__file__).parent / "mcp-testing-prompt.json"
    with open(prompt_file) as f:
        prompt_data = json.load(f)
    
    content = prompt_data['content']
    
    # Arguments
    arguments = {
        "test_type": "integration tests",
        "code_to_test": "API endpoints",
        "testing_framework": "pytest",
        "language": "Python",
        "coverage_target": "80",
        "include_edge_cases": "true",
        "include_performance_tests": "true"
    }
    
    print("Processing template with arguments:")
    print(json.dumps(arguments, indent=2))
    print("\n" + "=" * 80 + "\n")
    
    # Process Jinja2 conditionals first
    content = process_jinja2_conditionals(content, arguments)
    
    # Then substitute handlebars variables
    result = substitute_template_variables(content, arguments)
    
    print("PROCESSED PROMPT:")
    print("=" * 80)
    print(result)
    print("=" * 80)

if __name__ == "__main__":
    main()
