#!/usr/bin/env python3
"""
Test the mcp-testing-prompt with various scenarios.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp_prompts_integration import get_prompt_mcp

def test_unit_tests():
    """Test unit tests scenario."""
    print("=" * 60)
    print("Test 1: Unit Tests")
    print("=" * 60)
    
    args = {
        "test_type": "unit tests",
        "code_to_test": "Authentication service",
        "testing_framework": "pytest",
        "language": "Python",
        "coverage_target": "95",
        "include_edge_cases": "true",
        "include_performance_tests": "false"
    }
    
    prompt = get_prompt_mcp("mcp-testing-prompt", arguments=args)
    
    if prompt:
        print("✅ Prompt retrieved")
        if "unit tests" in prompt and "Authentication service" in prompt:
            print("✅ Template values substituted correctly")
        if "{{" not in prompt:
            print("✅ No remaining template variables")
        print(f"\nPreview:\n{prompt[:400]}...\n")
    else:
        print("❌ Failed to retrieve prompt")
        return False
    
    return True

def test_integration_tests():
    """Test integration tests scenario."""
    print("=" * 60)
    print("Test 2: Integration Tests")
    print("=" * 60)
    
    args = {
        "test_type": "integration tests",
        "code_to_test": "API endpoints",
        "testing_framework": "pytest",
        "language": "Python",
        "coverage_target": "80",
        "include_edge_cases": "true",
        "include_performance_tests": "true"
    }
    
    prompt = get_prompt_mcp("mcp-testing-prompt", arguments=args)
    
    if prompt:
        print("✅ Prompt retrieved")
        if "integration tests" in prompt and "API endpoints" in prompt:
            print("✅ Template values substituted correctly")
        if "{{" not in prompt:
            print("✅ No remaining template variables")
        print(f"\nPreview:\n{prompt[:400]}...\n")
    else:
        print("❌ Failed to retrieve prompt")
        return False
    
    return True

def test_e2e_tests():
    """Test e2e tests scenario."""
    print("=" * 60)
    print("Test 3: E2E Tests")
    print("=" * 60)
    
    args = {
        "test_type": "e2e tests",
        "code_to_test": "User registration flow",
        "testing_framework": "Selenium",
        "language": "Python",
        "coverage_target": "70",
        "include_edge_cases": "true",
        "include_performance_tests": "false"
    }
    
    prompt = get_prompt_mcp("mcp-testing-prompt", arguments=args)
    
    if prompt:
        print("✅ Prompt retrieved")
        if "e2e tests" in prompt and "User registration flow" in prompt:
            print("✅ Template values substituted correctly")
        if "{{" not in prompt:
            print("✅ No remaining template variables")
        print(f"\nPreview:\n{prompt[:400]}...\n")
    else:
        print("❌ Failed to retrieve prompt")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🧪 Testing mcp-testing-prompt\n")
    
    results = []
    results.append(test_unit_tests())
    results.append(test_integration_tests())
    results.append(test_e2e_tests())
    
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
