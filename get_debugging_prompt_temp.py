#!/usr/bin/env python3
"""Temporary script to get mcp-debugging-prompt"""
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from mcp_prompts_integration import get_prompt_mcp
import json

arguments = {
    "issue_description": "Tests failing locally",
    "error_message": "AssertionError: Expected 5, got 3",
    "environment": "development",
    "language": "Python",
    "urgency": "medium",
    "include_logs": "false",
    "include_solutions": "true"
}

print("Retrieving mcp-debugging-prompt...")
print(f"Arguments: {json.dumps(arguments, indent=2)}")
print("\n" + "="*80 + "\n")

result = get_prompt_mcp("mcp-debugging-prompt", arguments)

if result:
    print(result)
else:
    print("ERROR: Prompt 'mcp-debugging-prompt' not found or error occurred.")
    print("\nNote: This prompt may not exist in the mcp-prompts database.")
    print("Available debugging-related prompts:")
    print("  - select-debugging-strategy (in cognitive/metacognitive/)")
