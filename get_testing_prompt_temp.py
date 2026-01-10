#!/usr/bin/env python3
"""Temporary script to get mcp-testing-prompt"""

import sys
import json
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from mcp_prompts_integration import get_prompt_mcp

arguments = {
    "test_type": "integration tests",
    "code_to_test": "API endpoints",
    "testing_framework": "pytest",
    "language": "Python",
    "coverage_target": "80",
    "include_edge_cases": "true",
    "include_performance_tests": "true"
}

print("Fetching mcp-testing-prompt with arguments:")
print(json.dumps(arguments, indent=2))
print("\n" + "=" * 80 + "\n")

prompt = get_prompt_mcp("mcp-testing-prompt", arguments=arguments)

if prompt:
    print("PROMPT CONTENT:")
    print("=" * 80)
    print(prompt)
    print("=" * 80)
else:
    print("ERROR: Could not retrieve prompt")
