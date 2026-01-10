#!/usr/bin/env python3
import sys
import json
sys.path.insert(0, 'scripts')
from template_utils import substitute_template_variables

# Read the prompt
with open('/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts/public/code-review-assistant.json', 'r') as f:
    prompt_data = json.load(f)

# Get the template content
template_content = prompt_data['content']

# User provided arguments
arguments = {
    'platform': 'esp32',
    'language': 'cpp',
    'code_path': 'src/'
}

# Build context from provided arguments
context_parts = []
if 'platform' in arguments:
    context_parts.append(f"Platform: {arguments['platform']}")
if 'code_path' in arguments:
    context_parts.append(f"Code Path: {arguments['code_path']}")

# Prepare variables for substitution
substitution_vars = {
    'language': arguments.get('language', 'cpp'),
    'code': '{{code}}',  # Keep as placeholder
    'context': '\n'.join(context_parts) if context_parts else 'No additional context provided'
}

# Substitute variables
rendered = substitute_template_variables(template_content, substitution_vars)

print("=" * 80)
print("RENDERED CODE REVIEW ASSISTANT PROMPT")
print("=" * 80)
print()
print(rendered)
print()
print("=" * 80)
print("Template Variables:")
print(f"  - language: {substitution_vars['language']}")
print(f"  - code: (placeholder - provide actual code to review)")
print(f"  - context: {substitution_vars['context']}")
print("=" * 80)
