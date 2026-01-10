#!/usr/bin/env python3
"""Get mcp-debugging-prompt from mcp-prompts"""
import sys
import json
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

try:
    from mcp_prompts_integration import get_prompt_mcp
except ImportError as e:
    print(f"Error importing mcp_prompts_integration: {e}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    name = "mcp-debugging-prompt"
    arguments = {
        "issue_description": "API returning 500 errors",
        "error_message": "Internal Server Error: Database connection failed",
        "environment": "production",
        "language": "Python",
        "urgency": "critical",
        "include_logs": "true",
        "include_solutions": "true"
    }
    
    print(f"Retrieving prompt: {name}")
    print(f"Arguments: {json.dumps(arguments, indent=2)}")
    print("\n" + "="*80 + "\n")
    
    result = get_prompt_mcp(name, arguments)
    if result:
        print(result)
    else:
        print(f"Prompt '{name}' not found", file=sys.stderr)
        print("\nAvailable debugging-related prompts:")
        print("- select-debugging-strategy")
        print("- embedded-debugging-strategy-selection")
        print("- esp32-debugging-workflow")
        sys.exit(1)
