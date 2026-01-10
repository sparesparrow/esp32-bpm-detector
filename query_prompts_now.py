#!/usr/bin/env python3
"""List prompts from mcp-prompts with specific tags"""
import json
from pathlib import Path

def list_prompts_by_tags(prompts_dir, tags, limit=10):
    """List prompts matching any of the specified tags"""
    prompts_dir = Path(prompts_dir)
    matching_prompts = []
    
    # Search through all JSON files
    for json_file in prompts_dir.rglob("*.json"):
        if json_file.name == "index.json":
            continue
            
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                prompt_data = json.load(f)
                
            # Check if prompt has any of the specified tags
            prompt_tags = prompt_data.get('tags', [])
            if any(tag.lower() in [t.lower() for t in prompt_tags] for tag in tags):
                matching_prompts.append({
                    'name': prompt_data.get('name', ''),
                    'description': prompt_data.get('description', ''),
                    'tags': prompt_tags,
                    'category': prompt_data.get('category', ''),
                    'path': str(json_file.relative_to(prompts_dir))
                })
        except Exception as e:
            continue
    
    # Sort by name and limit results
    matching_prompts.sort(key=lambda x: x['name'])
    return matching_prompts[:limit]

if __name__ == "__main__":
    prompts_dir = "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts"
    tags = ["code-review", "development", "kotlin", "android"]
    limit = 10
    
    results = list_prompts_by_tags(prompts_dir, tags, limit)
    print(json.dumps(results, indent=2))
