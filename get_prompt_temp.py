#!/usr/bin/env python3
"""Temporary script to get prompt from mcp-prompts"""
import sys
import json
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from mcp_prompts_integration import get_prompt_mcp

if __name__ == "__main__":
    name = "code-review-assistant"
    arguments = {
        "platform": "android",
        "language": "kotlin",
        "code_path": "android-app/app/src/main/"
    }
    
    result = get_prompt_mcp(name, arguments)
    if result:
        print(result)
    else:
        print("Prompt not found", file=sys.stderr)
        sys.exit(1)
