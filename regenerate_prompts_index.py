#!/usr/bin/env python3
"""
Script to regenerate the index.json file for mcp-prompts storage.
This ensures all prompt files are properly indexed with consistent metadata.
"""

import json
import os
from pathlib import Path
from datetime import datetime
import sys

def validate_prompt_file(filepath):
    """Validate a prompt file has required fields and proper structure."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Required fields
        required_fields = ['id', 'name', 'description', 'content', 'isTemplate', 'tags', 'createdAt', 'updatedAt', 'version']
        for field in required_fields:
            if field not in data:
                print(f"WARNING: Missing required field '{field}' in {filepath}")
                return None

        # Validate types
        if not isinstance(data['id'], str):
            print(f"WARNING: 'id' field must be string in {filepath}")
            return None
        if not isinstance(data['name'], str):
            print(f"WARNING: 'name' field must be string in {filepath}")
            return None
        if not isinstance(data['description'], str):
            print(f"WARNING: 'description' field must be string in {filepath}")
            return None
        if not isinstance(data['content'], str):
            print(f"WARNING: 'content' field must be string in {filepath}")
            return None
        if not isinstance(data['isTemplate'], bool):
            print(f"WARNING: 'isTemplate' field must be boolean in {filepath}")
            return None
        if not isinstance(data['tags'], list):
            print(f"WARNING: 'tags' field must be array in {filepath}")
            return None
        if not isinstance(data['version'], (int, float)):
            print(f"WARNING: 'version' field must be number in {filepath}")
            return None

        # Optional fields validation
        if 'variables' in data and not isinstance(data['variables'], list):
            print(f"WARNING: 'variables' field must be array in {filepath}")
            return None

        return data

    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {filepath}: {e}")
        return None
    except Exception as e:
        print(f"ERROR: Failed to read {filepath}: {e}")
        return None

def extract_index_entry(filepath, data, base_path):
    """Extract the index entry for a prompt file."""
    # Calculate relative path from storage root
    rel_path = os.path.relpath(filepath, base_path)

    # Create index entry
    entry = {
        'id': data['id'],
        'name': data['name'],
        'description': data['description'],
        'tags': data['tags'],
        'isTemplate': data['isTemplate'],
        'metadata': {}
    }

    # Add optional metadata
    if 'category' in data:
        entry['metadata']['category'] = data['category']
    if 'variables' in data:
        entry['metadata']['variables'] = data['variables']
    if 'version' in data:
        entry['metadata']['version'] = data['version']

    # Add layer/domain/abstractionLevel if present (for cognitive prompts)
    for field in ['layer', 'domain', 'abstractionLevel']:
        if field in data:
            entry['metadata'][field] = data[field]
        elif 'metadata' in data and field in data['metadata']:
            entry['metadata'][field] = data['metadata'][field]

    return entry

def main():
    """Main function to regenerate the prompts index."""
    # Define the prompts storage directory
    prompts_dir = Path('/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts')

    if not prompts_dir.exists():
        print(f"ERROR: Prompts directory not found: {prompts_dir}")
        sys.exit(1)

    print(f"Scanning prompts directory: {prompts_dir}")

    # Find all JSON files (excluding index.json)
    prompt_files = []
    for json_file in prompts_dir.rglob('*.json'):
        if json_file.name != 'index.json':
            prompt_files.append(json_file)

    print(f"Found {len(prompt_files)} prompt files")

    # Process each prompt file
    valid_prompts = []
    invalid_files = []

    for filepath in prompt_files:
        print(f"Processing: {filepath}")
        data = validate_prompt_file(filepath)
        if data:
            entry = extract_index_entry(filepath, data, prompts_dir)
            valid_prompts.append(entry)
        else:
            invalid_files.append(str(filepath))

    # Report results
    print(f"\nProcessing complete:")
    print(f"- Valid prompts: {len(valid_prompts)}")
    print(f"- Invalid files: {len(invalid_files)}")

    if invalid_files:
        print("\nInvalid files:")
        for f in invalid_files:
            print(f"  - {f}")
        print("\nThese files will be excluded from the index.")

    # Sort prompts by ID for consistency
    valid_prompts.sort(key=lambda x: x['id'])

    # Create new index.json
    index_data = {
        'prompts': valid_prompts,
        'metadata': {
            'totalPrompts': len(valid_prompts),
            'lastUpdated': datetime.utcnow().isoformat() + 'Z',
            'version': '1.0'
        }
    }

    # Write the new index.json
    index_path = prompts_dir / 'index.json'
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)

    print(f"\nSuccessfully regenerated index.json at: {index_path}")
    print(f"Indexed {len(valid_prompts)} prompts")

    # Summary
    template_count = sum(1 for p in valid_prompts if p['isTemplate'])
    non_template_count = len(valid_prompts) - template_count

    print(f"- Templates: {template_count}")
    print(f"- Static prompts: {non_template_count}")

    # Show sample of indexed prompts
    if valid_prompts:
        print("\nSample of indexed prompts:")
        for i, prompt in enumerate(valid_prompts[:5]):
            print(f"  {i+1}. {prompt['id']} - {prompt['description'][:60]}{'...' if len(prompt['description']) > 60 else ''}")

if __name__ == '__main__':
    main()