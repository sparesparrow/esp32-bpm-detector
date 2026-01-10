#!/usr/bin/env python3
"""Query mcp-prompts with specific parameters"""
import sys
import json
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from mcp_prompts_integration import list_prompts_mcp

if __name__ == "__main__":
    tags = ["code-review", "development", "cpp", "esp32"]
    limit = 10
    
    results = list_prompts_mcp(tags=tags, limit=limit)
    
    print(json.dumps(results, indent=2))
