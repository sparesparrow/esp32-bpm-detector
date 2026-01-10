#!/usr/bin/env python3
"""List prompts from mcp-prompts with specific tags"""
import sys
import json
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from mcp_prompts_integration import list_prompts_mcp

if __name__ == "__main__":
    tags = ["code-review", "development", "kotlin", "android"]
    limit = 10
    
    print(f"Querying mcp-prompts with tags={tags}, limit={limit}...")
    results = list_prompts_mcp(tags=tags, limit=limit)
    
    print(f"\nFound {len(results)} prompts:")
    print(json.dumps(results, indent=2))
