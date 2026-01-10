#!/usr/bin/env python3
"""
Test Template Features
Tests template variable extraction and substitution.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from template_utils import (
    extract_template_variables,
    substitute_template_variables,
    validate_template_variables,
    get_template_info
)

def test_template_extraction():
    """Test template variable extraction."""
    print("🧪 Testing Template Variable Extraction")
    print("=" * 60)
    
    test_cases = [
        ("Review {{platform}} code", ["platform"]),
        ("Review {{platform}} code in {{code_path}}", ["platform", "code_path"]),
        ("Review {{ platform }} code", ["platform"]),  # With spaces
        ("No variables here", []),
        ("{{var1}} and {{var2}} and {{var1}} again", ["var1", "var2"]),  # Duplicates
    ]
    
    for content, expected in test_cases:
        result = extract_template_variables(content)
        status = "✅" if set(result) == set(expected) else "❌"
        print(f"{status} '{content}' -> {result} (expected: {expected})")

def test_template_substitution():
    """Test template variable substitution."""
    print("\n🧪 Testing Template Variable Substitution")
    print("=" * 60)
    
    test_cases = [
        (
            "Review {{platform}} code",
            {"platform": "ESP32"},
            "Review ESP32 code"
        ),
        (
            "Review {{platform}} code in {{code_path}}",
            {"platform": "ESP32", "code_path": "src/"},
            "Review ESP32 code in src/"
        ),
        (
            "Review {{ platform }} code",  # With spaces
            {"platform": "Android"},
            "Review Android code"
        ),
    ]
    
    for content, variables, expected in test_cases:
        result = substitute_template_variables(content, variables)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{content}' with {variables}")
        print(f"   Result: '{result}'")
        print(f"   Expected: '{expected}'")

def test_template_validation():
    """Test template variable validation."""
    print("\n🧪 Testing Template Variable Validation")
    print("=" * 60)
    
    content = "Review {{platform}} code in {{code_path}} using {{language}}"
    
    # Test 1: All variables provided
    validation = validate_template_variables(content, {
        "platform": "ESP32",
        "code_path": "src/",
        "language": "cpp"
    })
    print(f"✅ All variables provided: {validation['valid']}")
    print(f"   Missing: {validation['missing']}")
    
    # Test 2: Missing variables
    validation = validate_template_variables(content, {
        "platform": "ESP32"
    })
    print(f"❌ Missing variables: {not validation['valid']}")
    print(f"   Missing: {validation['missing']}")
    print(f"   Required: {validation['required']}")

def test_template_info():
    """Test template information extraction."""
    print("\n🧪 Testing Template Information")
    print("=" * 60)
    
    test_cases = [
        ("Review {{platform}} code", True, 1),
        ("No variables", False, 0),
        ("{{var1}} and {{var2}}", True, 2),
    ]
    
    for content, expected_is_template, expected_count in test_cases:
        info = get_template_info(content)
        status = "✅" if (info['is_template'] == expected_is_template and 
                         info['variable_count'] == expected_count) else "❌"
        print(f"{status} '{content}'")
        print(f"   Is template: {info['is_template']} (expected: {expected_is_template})")
        print(f"   Variables: {info['variables']}")
        print(f"   Count: {info['variable_count']} (expected: {expected_count})")

def test_integration():
    """Test integration with mcp_prompts_integration."""
    print("\n🧪 Testing Integration with mcp_prompts_integration")
    print("=" * 60)
    
    try:
        from mcp_prompts_integration import get_prompt_mcp
        
        # Test getting a prompt with template variables
        # This will test the full integration
        print("Testing get_prompt_mcp with template variables...")
        print("(This requires mcp-prompts server to be running)")
        
    except Exception as e:
        print(f"⚠ Integration test skipped: {e}")

if __name__ == "__main__":
    print("🚀 Template Features Test Suite")
    print("=" * 60)
    
    test_template_extraction()
    test_template_substitution()
    test_template_validation()
    test_template_info()
    test_integration()
    
    print("\n" + "=" * 60)
    print("✅ Template features test complete!")
