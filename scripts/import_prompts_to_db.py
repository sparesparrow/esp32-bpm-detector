#!/usr/bin/env python3
"""
Import all prompts and templates from file system into PostgreSQL database.

This script reads all prompt files from the mcp-prompts directory and imports
them into the PostgreSQL database using the postgres_prompts_adapter.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from postgres_prompts_adapter import PostgresPromptsAdapter, get_postgres_adapter
from sparetools_utils import setup_logging

logger = setup_logging(__name__)

# Default prompts directories
DEFAULT_PROMPTS_DIRS = [
    "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts",
    "/home/sparrow/mcp/data/prompts",
    "/home/sparrow/projects/dev-tools/sparetools/templates/prompts",
    "/home/sparrow/projects/dev-tools/sparetools/templates/docs/prompts"
]


def load_prompt_file(file_path: Path) -> Dict[str, Any]:
    """
    Load a prompt from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary with prompt data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.error(f"Failed to load prompt file {file_path}: {e}")
        return None


def extract_category_from_path(file_path: Path, prompts_dir: Path) -> str:
    """
    Extract category from file path.
    
    Args:
        file_path: Path to the prompt file
        prompts_dir: Base prompts directory
        
    Returns:
        Category string (e.g., 'esp32', 'cognitive', 'embedded')
    """
    try:
        # Get relative path from prompts directory
        rel_path = file_path.relative_to(prompts_dir)
        # Get parent directory (category)
        if len(rel_path.parts) > 1:
            return rel_path.parts[0]
        return 'general'
    except Exception:
        return 'general'


def normalize_prompt_data(prompt_data: Dict[str, Any], file_path: Path, prompts_dir: Path) -> Dict[str, Any]:
    """
    Normalize prompt data to match database schema.
    
    Args:
        prompt_data: Raw prompt data from JSON file
        file_path: Path to the prompt file
        prompts_dir: Base prompts directory
        
    Returns:
        Normalized prompt data
    """
    # Extract category from path
    category = extract_category_from_path(file_path, prompts_dir)
    
    # Normalize field names
    normalized = {
        'name': prompt_data.get('name') or prompt_data.get('id', ''),
        'description': prompt_data.get('description', ''),
        'content': prompt_data.get('content', ''),
        'is_template': prompt_data.get('isTemplate', prompt_data.get('is_template', False)),
        'tags': prompt_data.get('tags', []),
        'variables': prompt_data.get('variables', []),
        'category': category,
        'metadata': prompt_data.get('metadata', {})
    }
    
    # Use id as name if name is missing
    if not normalized['name'] and 'id' in prompt_data:
        normalized['name'] = prompt_data['id']
    
    return normalized


def import_prompt(adapter: PostgresPromptsAdapter, prompt_data: Dict[str, Any]) -> bool:
    """
    Import a single prompt into the database.
    
    Args:
        adapter: Postgres adapter instance
        prompt_data: Normalized prompt data
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if prompt already exists
        existing = adapter.get_prompt(prompt_data['name'])
        
        if existing:
            # Update existing prompt
            logger.info(f"Updating existing prompt: {prompt_data['name']}")
            updates = {
                'description': prompt_data['description'],
                'content': prompt_data['content'],
                'is_template': prompt_data['is_template'],
                'tags': prompt_data['tags'],
                'category': prompt_data['category'],
                'metadata': prompt_data['metadata']
            }
            return adapter.update_prompt(prompt_data['name'], updates)
        else:
            # Create new prompt
            logger.info(f"Creating new prompt: {prompt_data['name']}")
            return adapter.create_prompt(
                name=prompt_data['name'],
                description=prompt_data['description'],
                content=prompt_data['content'],
                tags=prompt_data['tags'],
                category=prompt_data['category'],
                is_template=prompt_data['is_template']
            )
    except Exception as e:
        logger.error(f"Failed to import prompt {prompt_data.get('name', 'unknown')}: {e}")
        return False


def find_prompt_files(prompts_dir: Path) -> List[Path]:
    """
    Find all prompt JSON files in the prompts directory.
    
    Args:
        prompts_dir: Base prompts directory
        
    Returns:
        List of prompt file paths
    """
    prompt_files = []
    
    # Find all JSON files
    for json_file in prompts_dir.rglob("*.json"):
        # Skip index.json
        if json_file.name == "index.json":
            continue
        prompt_files.append(json_file)
    
    # Also find MD files (these might be templates)
    for md_file in prompts_dir.rglob("*.md"):
        prompt_files.append(md_file)
    
    # Find .prompt files (SpareTools template format)
    for prompt_file in prompts_dir.rglob("*.prompt"):
        prompt_files.append(prompt_file)
    
    return sorted(prompt_files)


def load_prompt_text_file(file_path: Path) -> Dict[str, Any]:
    """
    Load a .prompt text file as a prompt.
    Supports YAML frontmatter format.
    
    Args:
        file_path: Path to the .prompt file
        
    Returns:
        Dictionary with prompt data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract name from filename
        name = file_path.stem.replace('_', '-')
        
        # Try to parse as JSON first (some .prompt files might be JSON)
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Try to parse YAML frontmatter
        frontmatter = {}
        prompt_content = content
        
        if content.startswith('---'):
            try:
                import yaml
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    prompt_content = parts[2].strip()
            except ImportError:
                logger.warning("PyYAML not available, skipping YAML frontmatter parsing")
            except Exception as e:
                logger.debug(f"Could not parse YAML frontmatter: {e}")
        
        # Extract variables from frontmatter if present
        variables = []
        if 'variables' in frontmatter:
            if isinstance(frontmatter['variables'], dict):
                variables = list(frontmatter['variables'].keys())
            elif isinstance(frontmatter['variables'], list):
                variables = frontmatter['variables']
        
        # Build prompt data
        return {
            'id': frontmatter.get('template_name', name),
            'name': frontmatter.get('template_name', name),
            'description': frontmatter.get('description', f'Prompt template: {name}'),
            'content': prompt_content,
            'isTemplate': True,
            'tags': frontmatter.get('tags', ['sparetools', 'template', frontmatter.get('category', 'general')]),
            'variables': variables,
            'metadata': {k: v for k, v in frontmatter.items() if k not in ['template_name', 'description', 'tags', 'variables', 'category']}
        }
    except Exception as e:
        logger.error(f"Failed to load .prompt file {file_path}: {e}")
        return None


def load_md_file(file_path: Path) -> Dict[str, Any]:
    """
    Load a markdown file as a prompt.
    
    Args:
        file_path: Path to the MD file
        
    Returns:
        Dictionary with prompt data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract name from filename
        name = file_path.stem
        
        # Try to extract frontmatter if present
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    frontmatter = json.loads(parts[1]) if parts[1].strip().startswith('{') else {}
                    content = parts[2].strip()
                except:
                    frontmatter = {}
        else:
            frontmatter = {}
        
        return {
            'id': name,
            'name': frontmatter.get('name', name),
            'description': frontmatter.get('description', f'Prompt from {name}'),
            'content': content,
            'isTemplate': frontmatter.get('isTemplate', False),
            'tags': frontmatter.get('tags', []),
            'variables': frontmatter.get('variables', []),
            'metadata': frontmatter.get('metadata', {})
        }
    except Exception as e:
        logger.error(f"Failed to load MD file {file_path}: {e}")
        return None


def main():
    """Main import function."""
    # Get prompts directories from environment or use defaults
    prompts_paths = os.getenv("MCP_PROMPTS_PATH", "").split(":") if os.getenv("MCP_PROMPTS_PATH") else []
    prompts_dirs = [Path(p) for p in prompts_paths if p] if prompts_paths else [Path(d) for d in DEFAULT_PROMPTS_DIRS]
    
    # Filter to only existing directories
    existing_dirs = [d for d in prompts_dirs if d.exists()]
    
    if not existing_dirs:
        logger.error(f"No valid prompts directories found. Checked: {prompts_dirs}")
        sys.exit(1)
    
    logger.info(f"Importing prompts from {len(existing_dirs)} directory(ies):")
    for d in existing_dirs:
        logger.info(f"  - {d}")
    
    # Get database adapter
    adapter = get_postgres_adapter()
    if not adapter:
        logger.error("Failed to get Postgres adapter. Check database connection.")
        sys.exit(1)
    
    # Find all prompt files from all directories
    all_prompt_files = []
    for prompts_dir in existing_dirs:
        prompt_files = find_prompt_files(prompts_dir)
        all_prompt_files.extend(prompt_files)
        logger.info(f"Found {len(prompt_files)} prompt files in {prompts_dir}")
    
    logger.info(f"Total prompt files to import: {len(all_prompt_files)}")
    
    # Import each prompt
    imported = 0
    failed = 0
    skipped = 0
    
    for file_path in all_prompt_files:
        try:
            # Find which directory this file belongs to
            file_prompts_dir = None
            for prompts_dir in existing_dirs:
                try:
                    file_path.relative_to(prompts_dir)
                    file_prompts_dir = prompts_dir
                    break
                except ValueError:
                    continue
            
            if not file_prompts_dir:
                file_prompts_dir = existing_dirs[0]  # Fallback
            
            # Load prompt data
            if file_path.suffix == '.json':
                prompt_data = load_prompt_file(file_path)
            elif file_path.suffix == '.md':
                prompt_data = load_md_file(file_path)
            elif file_path.suffix == '.prompt':
                prompt_data = load_prompt_file(file_path)  # Try JSON first
                if not prompt_data:
                    prompt_data = load_prompt_text_file(file_path)
            else:
                logger.warning(f"Skipping unsupported file type: {file_path}")
                skipped += 1
                continue
            
            if not prompt_data:
                failed += 1
                continue
            
            # Normalize data
            normalized = normalize_prompt_data(prompt_data, file_path, file_prompts_dir)
            
            # Import into database
            if import_prompt(adapter, normalized):
                imported += 1
                logger.debug(f"✓ Imported: {normalized['name']}")
            else:
                failed += 1
                logger.warning(f"✗ Failed to import: {normalized['name']}")
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            failed += 1
    
    # Summary
    logger.info("=" * 60)
    logger.info("Import Summary:")
    logger.info(f"  Total files: {len(all_prompt_files)}")
    logger.info(f"  Imported: {imported}")
    logger.info(f"  Failed: {failed}")
    logger.info(f"  Skipped: {skipped}")
    logger.info("=" * 60)
    
    # Disconnect
    adapter.disconnect()


if __name__ == "__main__":
    main()
