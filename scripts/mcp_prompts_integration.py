#!/usr/bin/env python3
"""
MCP Prompts Integration Helper
Provides functions to interact with mcp-prompts server using MCP tools.
Supports both file-based and Postgres storage backends.
"""

import os
import sys
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sparetools_utils import setup_logging

logger = setup_logging(__name__)

# Try to import Postgres adapter
POSTGRES_AVAILABLE = False
PostgresPromptsAdapter = None
get_postgres_adapter = None
PostgresMCPIntegration = None

try:
    from postgres_prompts_adapter import PostgresPromptsAdapter, get_postgres_adapter
    from postgres_mcp_integration import PostgresMCPIntegration, get_postgres_mcp_integration
    POSTGRES_AVAILABLE = True
except ImportError as e:
    POSTGRES_AVAILABLE = False
    logger.debug(f"Postgres adapter not available: {e}")

def list_prompts_mcp(tags: List[str] = None, category: str = None, search: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    List prompts from mcp-prompts server using MCP tools, Postgres MCP server, or direct Postgres adapter.
    
    Args:
        tags: Filter by tags
        category: Filter by category
        search: Search query
        limit: Maximum number of results
        
    Returns:
        List of prompt dictionaries
    """
    # Try Postgres MCP server first (if available)
    try:
        import subprocess
        result = subprocess.run(
            ["cursor-agent", "--print", "--approve-mcps", 
             f"Use postgres MCP server to query prompts table. SELECT * FROM prompts WHERE 1=1 LIMIT {limit}"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0 and result.stdout:
            logger.debug("Using Postgres MCP server for list_prompts")
            # Parse results from Postgres MCP server
            # This would need to be adapted based on actual MCP server response format
            pass
    except Exception as e:
        logger.debug(f"Postgres MCP server not available: {e}")
    
    # Try Postgres adapter (direct database access)
    if POSTGRES_AVAILABLE:
        postgres_adapter = get_postgres_adapter()
        if postgres_adapter:
            try:
                logger.debug("Using Postgres adapter for list_prompts")
                return postgres_adapter.list_prompts(tags=tags, category=category, search=search, limit=limit)
            except Exception as e:
                logger.warning(f"Postgres adapter failed, falling back to MCP: {e}")
    
    # Fallback to mcp-prompts MCP tools via cursor-agent
    try:
        import subprocess
        import json
        
        # Build command
        cmd = ["cursor-agent", "--print", "--approve-mcps"]
        
        # Build query
        query_parts = ["Use mcp-prompts list_prompts"]
        if limit:
            query_parts.append(f"limit={limit}")
        if tags:
            tags_str = ",".join(tags)
            query_parts.append(f"tags=[{tags_str}]")
        if category:
            query_parts.append(f"category={category}")
        if search:
            query_parts.append(f"search={search}")
        
        query = " ".join(query_parts)
        cmd.append(query)
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)  # Increased timeout
        
        if result.returncode == 0:
            # Parse output (would need to extract JSON from cursor-agent output)
            # For now, return empty list and log
            logger.info(f"Listed prompts via cursor-agent: {query}")
            return []
        else:
            logger.warning(f"Failed to list prompts: {result.stderr}")
            return []
            
    except Exception as e:
        logger.error(f"Error listing prompts: {e}")
        return []

def get_prompt_mcp(name: str, arguments: Dict[str, Any] = None) -> Optional[str]:
    """
    Get a prompt from mcp-prompts server using MCP tools or Postgres.
    
    Args:
        name: Prompt name/ID
        arguments: Template variables (if prompt is a template)
        
    Returns:
        Prompt content as string, or None if not found
    """
    # Try Postgres adapter first if available
    if POSTGRES_AVAILABLE:
        postgres_adapter = get_postgres_adapter()
        if postgres_adapter:
            try:
                logger.debug(f"Using Postgres adapter for get_prompt: {name}")
                prompt = postgres_adapter.get_prompt(name, arguments)
                if prompt:
                    content = prompt.get('content', '')
                    # Validate template variables if provided
                    if arguments:
                        from template_utils import validate_template_variables
                        validation = validate_template_variables(content, arguments)
                        if not validation['valid']:
                            logger.warning(f"Missing template variables for {name}: {validation['missing']}")
                    return content
            except ConnectionError as e:
                logger.warning(f"Postgres connection failed, falling back to MCP: {e}")
            except Exception as e:
                logger.warning(f"Postgres adapter failed, falling back to MCP: {e}")
                # Don't re-raise - fall through to MCP fallback
    
    # Fallback to MCP tools via cursor-agent
    try:
        import subprocess
        import json
        
        # Build command
        cmd = ["cursor-agent", "--print", "--approve-mcps"]
        
        # Build query
        query = f"Use mcp-prompts get_prompt name={name}"
        if arguments:
            args_json = json.dumps(arguments)
            query += f" arguments={args_json}"
        
        cmd.append(query)
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)  # Increased timeout
        
        if result.returncode == 0:
            # Extract prompt content from output
            output = result.stdout.strip()
            
            # If arguments provided and output contains template variables, substitute them
            if arguments:
                try:
                    from template_utils import substitute_template_variables, extract_template_variables
                    
                    # Check if output is a template
                    template_vars = extract_template_variables(output)
                    if template_vars:
                        # Substitute variables
                        output = substitute_template_variables(output, arguments)
                        logger.debug(f"Substituted template variables: {list(arguments.keys())}")
                    else:
                        logger.debug(f"No template variables found in prompt '{name}', returning as-is")
                except ImportError:
                    logger.warning("template_utils not available, skipping template substitution")
                except Exception as e:
                    logger.warning(f"Template substitution failed: {e}, returning original output")
            
            return output
        else:
            logger.warning(f"Failed to get prompt {name}: {result.stderr}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting prompt {name}: {e}")
        return None

def create_prompt_mcp(
    name: str,
    description: str,
    content: str,
    tags: List[str] = None,
    category: str = None,
    is_template: bool = False
) -> bool:
    """
    Create a new prompt in mcp-prompts server using MCP tools or Postgres.
    
    Args:
        name: Unique prompt identifier
        description: Human-readable description
        content: Prompt content (can include {{variables}})
        tags: List of tags
        category: Category
        is_template: Whether prompt is a template
        
    Returns:
        True if successful, False otherwise
    """
    # Try Postgres adapter first if available
    if POSTGRES_AVAILABLE:
        postgres_adapter = get_postgres_adapter()
        if postgres_adapter:
            try:
                logger.debug(f"Using Postgres adapter for create_prompt: {name}")
                return postgres_adapter.create_prompt(
                    name=name,
                    description=description,
                    content=content,
                    tags=tags,
                    category=category,
                    is_template=is_template
                )
            except ConnectionError as e:
                logger.warning(f"Postgres connection failed, falling back to MCP: {e}")
            except Exception as e:
                logger.warning(f"Postgres adapter failed, falling back to MCP: {e}")
                # Don't re-raise - fall through to MCP fallback
    
    # Fallback to MCP tools via cursor-agent
    try:
        import subprocess
        import json
        
        # Build command
        cmd = ["cursor-agent", "--print", "--approve-mcps"]
        
        # Build query with prompt data
        prompt_data = {
            "name": name,
            "description": description,
            "content": content,
            "tags": tags or [],
            "category": category,
            "isTemplate": is_template
        }
        
        query = f"Use mcp-prompts create_prompt with data: {json.dumps(prompt_data)}"
        cmd.append(query)
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)  # Increased timeout
        
        if result.returncode == 0:
            logger.info(f"Created prompt: {name}")
            return True
        else:
            logger.warning(f"Failed to create prompt {name}: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error creating prompt {name}: {e}")
        return False

def update_prompt_mcp(name: str, updates: Dict[str, Any]) -> bool:
    """
    Update an existing prompt in mcp-prompts server using MCP tools or Postgres.
    
    Args:
        name: Prompt name/ID
        updates: Dictionary of fields to update
        
    Returns:
        True if successful, False otherwise
    """
    # Try Postgres adapter first if available
    if POSTGRES_AVAILABLE:
        postgres_adapter = get_postgres_adapter()
        if postgres_adapter:
            try:
                logger.debug(f"Using Postgres adapter for update_prompt: {name}")
                return postgres_adapter.update_prompt(name, updates)
            except Exception as e:
                logger.warning(f"Postgres adapter failed, falling back to MCP: {e}")
    
    # Fallback to MCP tools via cursor-agent
    try:
        import subprocess
        import json
        
        # Build command
        cmd = ["cursor-agent", "--print", "--approve-mcps"]
        
        # Build query
        query = f"Use mcp-prompts update_prompt name={name} with updates: {json.dumps(updates)}"
        cmd.append(query)
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)  # Increased timeout
        
        if result.returncode == 0:
            logger.info(f"Updated prompt: {name}")
            return True
        else:
            logger.warning(f"Failed to update prompt {name}: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error updating prompt {name}: {e}")
        return False

def discover_relevant_prompts(task_type: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Discover relevant prompts for a given task type.
    
    Args:
        task_type: Type of task (e.g., "code-review", "refactoring", "debugging")
        context: Additional context (e.g., {"language": "cpp", "platform": "esp32"})
        
    Returns:
        List of relevant prompts
    """
    context = context or {}
    
    # Map task types to tags
    tag_mapping = {
        "code-review": ["code-review", "development"],
        "refactoring": ["refactoring", "optimization"],
        "debugging": ["debugging", "troubleshooting"],
        "architecture": ["architecture", "design"],
        "testing": ["testing", "quality-assurance"],
        "embedded": ["embedded", "esp32", "arduino"],
        "android": ["android", "mobile"]
    }
    
    tags = tag_mapping.get(task_type, [task_type])
    
    # Add context-specific tags
    if context.get("language"):
        tags.append(context["language"])
    if context.get("platform"):
        tags.append(context["platform"])
    
    # Search for prompts
    prompts = list_prompts_mcp(tags=tags, limit=10)
    
    return prompts
