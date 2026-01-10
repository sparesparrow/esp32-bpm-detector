#!/usr/bin/env python3
"""
Template Utilities
Handles template variable extraction, substitution, and validation for handlebars-style templates.
"""

import re
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

def extract_template_variables(content: str) -> List[str]:
    """
    Extract template variables from handlebars-style template.
    
    Args:
        content: Template content with {{variable}} placeholders
        
    Returns:
        List of variable names found in template
    """
    # Match {{variable}} or {{variable:default}} patterns
    pattern = r'\{\{([^}]+)\}\}'
    matches = re.findall(pattern, content)
    
    variables = []
    for match in matches:
        # Handle default values: {{var:default}}
        var_name = match.split(':')[0].strip()
        if var_name and var_name not in variables:
            variables.append(var_name)
    
    return variables

def substitute_template_variables(content: str, variables: Dict[str, Any]) -> str:
    """
    Substitute template variables with actual values.
    
    Args:
        content: Template content
        variables: Dictionary of variable names to values
        
    Returns:
        Content with variables substituted
    """
    result = content
    
    # Substitute each variable
    for var_name, var_value in variables.items():
        # Match {{var}} or {{var:default}}
        pattern = rf'\{{\{{{var_name}(?::[^}}]+)?\}}\}}'
        result = re.sub(pattern, str(var_value), result)
    
    return result

def get_template_info(content: str) -> Dict[str, Any]:
    """
    Get information about template variables in content.
    
    Args:
        content: Template content
        
    Returns:
        Dictionary with template information:
        - is_template: Whether content contains template variables
        - variables: List of variable names
        - has_defaults: Whether any variables have default values
    """
    variables = extract_template_variables(content)
    
    # Check for default values
    has_defaults = bool(re.search(r'\{\{[^}]+:[^}]+\}\}', content))
    
    return {
        "is_template": len(variables) > 0,
        "variables": variables,
        "has_defaults": has_defaults,
        "variable_count": len(variables)
    }

def validate_template_variables(content: str, provided_variables: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that all required template variables are provided.
    
    Args:
        content: Template content
        provided_variables: Variables provided by user
        
    Returns:
        Dictionary with validation results:
        - valid: Whether all required variables are provided
        - missing: List of missing variable names
        - extra: List of provided but unused variable names
    """
    required_vars = extract_template_variables(content)
    provided_vars = set(provided_variables.keys())
    required_vars_set = set(required_vars)
    
    missing = list(required_vars_set - provided_vars)
    extra = list(provided_vars - required_vars_set)
    
    return {
        "valid": len(missing) == 0,
        "missing": missing,
        "extra": extra,
        "required": required_vars,
        "provided": list(provided_vars)
    }
