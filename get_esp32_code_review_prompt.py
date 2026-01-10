#!/usr/bin/env python3
"""Retrieve esp32-code-review prompt with specified arguments."""

import sys
import json
from pathlib import Path

# Add scripts to path
scripts_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(scripts_dir))

try:
    from mcp_prompts_integration import get_prompt_mcp
    
    arguments = {
        "platform": "esp32s3",
        "language": "cpp",
        "code_path": "src/"
    }
    
    print("Retrieving esp32-code-review prompt...")
    print(f"Arguments: {json.dumps(arguments, indent=2)}\n")
    
    prompt = get_prompt_mcp("esp32-code-review", arguments=arguments)
    
    if prompt:
        print("=" * 80)
        print("PROMPT RETRIEVED SUCCESSFULLY")
        print("=" * 80)
        print()
        print(prompt)
        print()
        print("=" * 80)
    else:
        print("❌ Failed to retrieve prompt")
        sys.exit(1)
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
