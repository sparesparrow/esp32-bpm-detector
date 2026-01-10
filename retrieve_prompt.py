#!/usr/bin/env python3
"""Retrieve and format code-review-assistant prompt"""
import json
import sys
from pathlib import Path

# Read the prompt file
prompt_file = Path("/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts/public/code-review-assistant.json")
with open(prompt_file, 'r') as f:
    prompt_data = json.load(f)

# Get template content
template_content = prompt_data['content']

# User-provided arguments
arguments = {
    "platform": "android",
    "language": "kotlin",
    "code_path": "android-app/app/src/main/"
}

# Substitute template variables
# The template expects: language, code, context
# We have: platform, language, code_path

# Map user arguments to template variables
substitutions = {
    "language": arguments["language"],
    "code": f"Code located at: {arguments['code_path']}\n\nReview all Kotlin files in the android-app/app/src/main/ directory including:\n- ViewModels (BPMViewModel.kt)\n- Services (BPMService.kt)\n- Network layer (BPMApiClient.kt, BPMApiService.kt, WiFiManager.kt)\n- UI components (BPMDisplayScreen.kt, SettingsScreen.kt, DeviceInfoScreen.kt)\n- Application structure (BPMApplication.kt, MainActivity.kt)\n- Models and data classes (BPMData.kt)\n- Audio processing (LocalBPMDetector.kt)",
    "context": f"Platform: {arguments['platform']}\nCode Path: {arguments['code_path']}\n\nThis is an Android application written in Kotlin that communicates with an ESP32 BPM detector device. The app includes network communication, real-time BPM display, device management, and audio processing capabilities."
}

# Simple template substitution
result = template_content
for var_name, var_value in substitutions.items():
    result = result.replace(f"{{{{{var_name}}}}}}", str(var_value))

# Output the formatted prompt
print("=" * 80)
print("CODE REVIEW ASSISTANT PROMPT")
print("=" * 80)
print()
print(result)
print()
print("=" * 80)
print("PROMPT METADATA")
print("=" * 80)
print(f"Name: {prompt_data['name']}")
print(f"Description: {prompt_data['description']}")
print(f"Tags: {', '.join(prompt_data['tags'])}")
print(f"Template Variables: {', '.join(prompt_data.get('variables', []))}")
print("=" * 80)
