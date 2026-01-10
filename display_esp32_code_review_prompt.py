#!/usr/bin/env python3
"""Display esp32-code-review prompt with substituted variables."""

import sys
import json
from pathlib import Path

# Add scripts to path
scripts_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(scripts_dir))

try:
    from template_utils import substitute_template_variables, extract_template_variables
    
    # Read the prompt file
    prompt_file = Path("/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts/esp32/esp32-code-review.json")
    
    with open(prompt_file, 'r') as f:
        prompt_data = json.load(f)
    
    content = prompt_data['content']
    
    # Provided arguments
    arguments = {
        "platform": "esp32s3",
        "language": "cpp",
        "code_path": "src/"
    }
    
    # Extract all template variables
    all_variables = extract_template_variables(content)
    print("Template variables found:", all_variables)
    print("\nProvided arguments:", json.dumps(arguments, indent=2))
    
    # Check for missing variables
    missing = [v for v in all_variables if v not in arguments]
    if missing:
        print(f"\n⚠️  Missing variables (will remain as placeholders): {missing}")
        print("   These should be provided when using the prompt:\n")
        for var in missing:
            print(f"   - {var}")
        print()
    
    # Substitute provided variables
    substituted_content = substitute_template_variables(content, arguments)
    
    print("=" * 80)
    print("ESP32 CODE REVIEW PROMPT (with substituted variables)")
    print("=" * 80)
    print()
    print(substituted_content)
    print()
    print("=" * 80)
    
    # Also show the prompt metadata
    print("\nPrompt Metadata:")
    print(f"  Name: {prompt_data['name']}")
    print(f"  Description: {prompt_data['description']}")
    print(f"  Category: {prompt_data['category']}")
    print(f"  Tags: {', '.join(prompt_data['tags'])}")
    print(f"  Is Template: {prompt_data['isTemplate']}")
    print(f"  Version: {prompt_data.get('version', 'N/A')}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
