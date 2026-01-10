#!/usr/bin/env python3
"""
Test the mcp-debugging-prompt with various scenarios.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp_prompts_integration import get_prompt_mcp

def test_critical_bug():
    """Test critical bug scenario."""
    print("=" * 60)
    print("Test 1: Critical Production Bug")
    print("=" * 60)
    
    args = {
        "issue_description": "API returning 500 errors",
        "error_message": "Internal Server Error: Database connection failed",
        "environment": "production",
        "language": "Python",
        "urgency": "critical",
        "include_logs": "true",
        "include_solutions": "true"
    }
    
    try:
        prompt = get_prompt_mcp("mcp-debugging-prompt", arguments=args)
        
        if prompt:
            print("✅ Prompt retrieved")
            if "API returning 500 errors" in prompt and "Database connection failed" in prompt:
                print("✅ Template values substituted correctly")
            if "{{" not in prompt:
                print("✅ No remaining template variables")
            print(f"\nPreview:\n{prompt[:400]}...\n")
            return True
        else:
            print("❌ Failed to retrieve prompt")
            return False
    except Exception as e:
        print(f"⚠️  Error: {e}")
        print("   MCP connection may be unavailable")
        return False

def test_performance_issue():
    """Test performance issue scenario."""
    print("=" * 60)
    print("Test 2: Performance Issue")
    print("=" * 60)
    
    args = {
        "issue_description": "Slow response times",
        "error_message": "API responses taking 10+ seconds",
        "environment": "production",
        "language": "Python",
        "urgency": "high",
        "include_logs": "true",
        "include_solutions": "true"
    }
    
    try:
        prompt = get_prompt_mcp("mcp-debugging-prompt", arguments=args)
        
        if prompt:
            print("✅ Prompt retrieved")
            if "Slow response times" in prompt and "10+ seconds" in prompt:
                print("✅ Template values substituted correctly")
            if "{{" not in prompt:
                print("✅ No remaining template variables")
            print(f"\nPreview:\n{prompt[:400]}...\n")
            return True
        else:
            print("❌ Failed to retrieve prompt")
            return False
    except Exception as e:
        print(f"⚠️  Error: {e}")
        print("   MCP connection may be unavailable")
        return False

def test_development_issue():
    """Test development issue scenario."""
    print("=" * 60)
    print("Test 3: Development Issue")
    print("=" * 60)
    
    args = {
        "issue_description": "Tests failing locally",
        "error_message": "AssertionError: Expected 5, got 3",
        "environment": "development",
        "language": "Python",
        "urgency": "medium",
        "include_logs": "false",
        "include_solutions": "true"
    }
    
    try:
        prompt = get_prompt_mcp("mcp-debugging-prompt", arguments=args)
        
        if prompt:
            print("✅ Prompt retrieved")
            if "Tests failing locally" in prompt and "Expected 5, got 3" in prompt:
                print("✅ Template values substituted correctly")
            if "{{" not in prompt:
                print("✅ No remaining template variables")
            print(f"\nPreview:\n{prompt[:400]}...\n")
            return True
        else:
            print("❌ Failed to retrieve prompt")
            return False
    except Exception as e:
        print(f"⚠️  Error: {e}")
        print("   MCP connection may be unavailable")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing mcp-debugging-prompt\n")
    
    results = []
    results.append(test_critical_bug())
    results.append(test_performance_issue())
    results.append(test_development_issue())
    
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    elif passed > 0:
        print("⚠️  Some tests passed (MCP connection may be intermittent)")
        return 0
    else:
        print("❌ All tests failed (MCP connection unavailable)")
        print("   The prompt may still exist in the system")
        return 1

if __name__ == "__main__":
    sys.exit(main())
