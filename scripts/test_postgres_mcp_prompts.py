#!/usr/bin/env python3
"""
Test Postgres mcp-prompts Integration
Tests the Postgres storage integration with mcp-prompts server.
"""

import sys
import os
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sparetools_utils import setup_logging
from mcp_prompts_integration import (
    list_prompts_mcp,
    get_prompt_mcp,
    discover_relevant_prompts
)

logger = setup_logging(__name__)

def test_list_prompts():
    """Test listing prompts via MCP."""
    print("\n" + "="*70)
    print("Test 1: List Prompts via MCP (Postgres)")
    print("="*70)
    
    try:
        prompts = list_prompts_mcp(tags=["code-review"], limit=5)
        print(f"✅ Found {len(prompts)} prompts")
        for prompt in prompts[:3]:
            print(f"  - {prompt.get('name', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_get_prompt():
    """Test getting a prompt via MCP."""
    print("\n" + "="*70)
    print("Test 2: Get Prompt via MCP (Postgres)")
    print("="*70)
    
    try:
        prompt = get_prompt_mcp("code-review-assistant", arguments={"platform": "esp32"})
        if prompt:
            print(f"✅ Retrieved prompt (length: {len(prompt)} chars)")
            return True
        else:
            print("⚠️  Prompt not found")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_discover_prompts():
    """Test prompt discovery."""
    print("\n" + "="*70)
    print("Test 3: Discover Prompts (Postgres)")
    print("="*70)
    
    try:
        prompts = discover_relevant_prompts(
            "code-review",
            {"platform": "esp32", "language": "cpp"}
        )
        print(f"✅ Discovered {len(prompts)} relevant prompts")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Postgres mcp-prompts Integration")
    print("="*70)
    
    results = []
    
    # Test 1: List prompts
    results.append(("List Prompts", test_list_prompts()))
    
    # Test 2: Get prompt
    results.append(("Get Prompt", test_get_prompt()))
    
    # Test 3: Discover prompts
    results.append(("Discover Prompts", test_discover_prompts()))
    
    # Summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
