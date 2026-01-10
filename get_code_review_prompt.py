#!/usr/bin/env python3
"""Get code-review-assistant prompt from mcp-prompts"""
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts")))

from mcp_prompts_integration import get_prompt_mcp

if __name__ == "__main__":
    arguments = {
        "platform": "esp32",
        "language": "cpp",
        "code_path": "src/"
    }
    
    prompt_content = get_prompt_mcp("code-review-assistant", arguments)
    
    if prompt_content:
        print("=" * 80)
        print("CODE REVIEW ASSISTANT PROMPT")
        print("=" * 80)
        print(prompt_content)
        print("=" * 80)
    else:
        print("Error: Could not retrieve prompt 'code-review-assistant'")
        sys.exit(1)
