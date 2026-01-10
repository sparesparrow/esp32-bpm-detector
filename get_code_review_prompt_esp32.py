#!/usr/bin/env python3
"""Get code-review-assistant prompt from mcp-prompts with ESP32 C++ arguments"""
import json
import re
from pathlib import Path

# Read the prompt template
prompt_file = Path('/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts/public/code-review-assistant.json')
with open(prompt_file) as f:
    prompt_data = json.load(f)

# Get template content
template_content = prompt_data['content']

# User arguments
arguments = {
    'platform': 'esp32',
    'language': 'cpp',
    'code_path': 'src/'
}

# Prepare template variables
# The template expects: language, code, context
# For 'code', we'll provide a placeholder since the actual code would be inserted during review
template_vars = {
    'language': arguments['language'],
    'code': f'[ESP32 BPM Detector C++ code from {arguments["code_path"]} directory - code will be inserted here during review]',
    'context': f'Platform: {arguments["platform"]} (ESP32 microcontroller)\nCode Path: {arguments["code_path"]}\nLanguage: {arguments["language"]} (C++)\nProject: ESP32 BPM Detector firmware'
}

# Substitute template variables using handlebars-style {{variable}} syntax
result = template_content
for var_name, var_value in template_vars.items():
    # Match {{var}} or {{var:default}} patterns
    pattern = rf'\{{{{{var_name}(?::[^}}]+)?\}}\}}'
    result = re.sub(pattern, str(var_value), result)

# Print the final prompt
print('=' * 80)
print('CODE REVIEW ASSISTANT PROMPT')
print('=' * 80)
print(result)
print('=' * 80)
