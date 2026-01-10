#!/usr/bin/env python3
"""Render code-review-assistant prompt with user arguments"""
import json
import sys
from pathlib import Path

# Read the prompt file
prompt_file = Path("/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts/public/code-review-assistant.json")
with open(prompt_file, 'r') as f:
    prompt_data = json.load(f)

# User arguments
arguments = {
    "platform": "esp32",
    "language": "cpp",
    "code_path": "src/"
}

# Get the template content
content = prompt_data.get('content', '')

# Render template variables
# The template uses: {{language}}, {{code}}, {{context}}
# We'll substitute what we have and note what's missing

rendered = content
rendered = rendered.replace('{{language}}', arguments.get('language', '{{language}}'))
rendered = rendered.replace('{{code}}', f"Code from {arguments.get('code_path', '{{code}}')}")
rendered = rendered.replace('{{context}}', f"Platform: {arguments.get('platform', '{{context}}')}, Code path: {arguments.get('code_path', '')}")

print("=" * 80)
print("CODE REVIEW ASSISTANT PROMPT (Rendered)")
print("=" * 80)
print(rendered)
print("=" * 80)
print("\nNote: The template expects {{code}} to contain actual code content.")
print("You may need to provide the code separately or read from the code_path.")
