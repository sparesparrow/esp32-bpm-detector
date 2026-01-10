#!/usr/bin/env python3
"""
Integration Test for MCP Prompts Integration
Tests the mcp-prompts MCP server integration with the learning loop workflow.
"""

import sys
import os
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_prompts_integration import (
    list_prompts_mcp,
    get_prompt_mcp,
    discover_relevant_prompts,
    create_prompt_mcp,
    update_prompt_mcp
)

def test_list_prompts():
    """Test listing prompts."""
    print("\n" + "="*70)
    print("TEST 1: List Prompts")
    print("="*70)
    
    start_time = time.time()
    
    # Test different query patterns in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(list_prompts_mcp, tags=["code-review"], limit=5): "code-review",
            executor.submit(list_prompts_mcp, tags=["esp32", "embedded"], limit=5): "esp32",
            executor.submit(list_prompts_mcp, tags=["android"], limit=5): "android",
            executor.submit(list_prompts_mcp, search="refactoring", limit=5): "refactoring"
        }
        
        results = {}
        for future in as_completed(futures):
            query_type = futures[future]
            try:
                prompts = future.result(timeout=60)  # Increased timeout
                results[query_type] = prompts
                print(f"  ✅ {query_type}: Found {len(prompts)} prompts")
            except Exception as e:
                results[query_type] = []
                print(f"  ❌ {query_type}: Error - {e}")
    
    elapsed = time.time() - start_time
    print(f"\n  ⏱️  Total time: {elapsed:.2f}s (parallel execution)")
    
    return results

def test_get_prompts():
    """Test getting specific prompts."""
    print("\n" + "="*70)
    print("TEST 2: Get Prompts")
    print("="*70)
    
    prompt_names = [
        "code-review-assistant",
        "code-refactoring-assistant",
        "architecture-design-assistant",
        "analysis-assistant"
    ]
    
    start_time = time.time()
    
    # Get prompts in parallel (they don't depend on each other)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(get_prompt_mcp, name=name): name
            for name in prompt_names
        }
        
        results = {}
        for future in as_completed(futures):
            prompt_name = futures[future]
            try:
                prompt = future.result(timeout=60)  # Increased timeout
                if prompt:
                    results[prompt_name] = len(prompt)
                    print(f"  ✅ {prompt_name}: Retrieved ({len(prompt)} chars)")
                else:
                    results[prompt_name] = None
                    print(f"  ⚠️  {prompt_name}: Not found")
            except Exception as e:
                results[prompt_name] = None
                print(f"  ❌ {prompt_name}: Error - {e}")
    
    elapsed = time.time() - start_time
    print(f"\n  ⏱️  Total time: {elapsed:.2f}s (parallel execution)")
    
    return results

def test_discover_prompts():
    """Test prompt discovery."""
    print("\n" + "="*70)
    print("TEST 3: Discover Relevant Prompts")
    print("="*70)
    
    test_cases = [
        ("code-review", {"platform": "esp32", "language": "cpp"}),
        ("code-review", {"platform": "android", "language": "kotlin"}),
        ("refactoring", {"language": "cpp", "target": "esp32"}),
        ("debugging", {"platform": "esp32", "embedded": True})
    ]
    
    start_time = time.time()
    
    # Discover prompts in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(discover_relevant_prompts, task_type, context): (task_type, context)
            for task_type, context in test_cases
        }
        
        results = {}
        for future in as_completed(futures):
            task_type, context = futures[future]
            try:
                prompts = future.result(timeout=60)  # Increased timeout
                results[f"{task_type}_{context.get('platform', 'generic')}"] = len(prompts)
                print(f"  ✅ {task_type} ({context.get('platform', 'generic')}): Found {len(prompts)} prompts")
            except Exception as e:
                results[f"{task_type}_{context.get('platform', 'generic')}"] = 0
                print(f"  ❌ {task_type} ({context.get('platform', 'generic')}): Error - {e}")
    
    elapsed = time.time() - start_time
    print(f"\n  ⏱️  Total time: {elapsed:.2f}s (parallel execution)")
    
    return results

def test_get_prompts_with_arguments():
    """Test getting prompts with template arguments."""
    print("\n" + "="*70)
    print("TEST 4: Get Prompts with Template Arguments")
    print("="*70)
    
    test_cases = [
        ("code-review-assistant", {"platform": "esp32", "language": "cpp", "code_path": "src/"}),
        ("code-review-assistant", {"platform": "android", "language": "kotlin", "code_path": "app/src/main/"}),
        ("code-refactoring-assistant", {"language": "cpp", "target": "esp32", "constraints": "memory-constrained"}),
        ("architecture-design-assistant", {"domain": "embedded-systems", "platform": "esp32"})
    ]
    
    start_time = time.time()
    
    # Get prompts with arguments in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(get_prompt_mcp, name=name, arguments=args): (name, args)
            for name, args in test_cases
        }
        
        results = {}
        for future in as_completed(futures):
            name, args = futures[future]
            try:
                prompt = future.result(timeout=90)  # Increased timeout for template processing
                if prompt:
                    results[f"{name}_{args.get('platform', 'generic')}"] = len(prompt)
                    print(f"  ✅ {name} ({args.get('platform', 'generic')}): Retrieved with args ({len(prompt)} chars)")
                else:
                    results[f"{name}_{args.get('platform', 'generic')}"] = None
                    print(f"  ⚠️  {name} ({args.get('platform', 'generic')}): Not found")
            except Exception as e:
                results[f"{name}_{args.get('platform', 'generic')}"] = None
                print(f"  ❌ {name} ({args.get('platform', 'generic')}): Error - {e}")
    
    elapsed = time.time() - start_time
    print(f"\n  ⏱️  Total time: {elapsed:.2f}s (parallel execution)")
    
    return results

def test_workflow_integration():
    """Test integration with learning loop workflow."""
    print("\n" + "="*70)
    print("TEST 5: Workflow Integration")
    print("="*70)
    
    from learning_loop_workflow import LearningLoopWorkflow
    
    workflow = LearningLoopWorkflow()
    
    # Test getting prompts for ESP32 and Android in parallel
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        esp32_future = executor.submit(workflow.get_prompt_for_review, "esp32")
        android_future = executor.submit(workflow.get_prompt_for_review, "android")
        
        results = {}
        try:
            esp32_prompt = esp32_future.result(timeout=90)
            results["esp32"] = len(esp32_prompt) if esp32_prompt else 0
            print(f"  ✅ ESP32 prompt: Retrieved ({len(esp32_prompt) if esp32_prompt else 0} chars)")
        except Exception as e:
            results["esp32"] = 0
            print(f"  ❌ ESP32 prompt: Error - {e}")
        
        try:
            android_prompt = android_future.result(timeout=90)
            results["android"] = len(android_prompt) if android_prompt else 0
            print(f"  ✅ Android prompt: Retrieved ({len(android_prompt) if android_prompt else 0} chars)")
        except Exception as e:
            results["android"] = 0
            print(f"  ❌ Android prompt: Error - {e}")
    
    elapsed = time.time() - start_time
    print(f"\n  ⏱️  Total time: {elapsed:.2f}s (parallel execution)")
    
    return results

def run_all_tests():
    """Run all integration tests."""
    print("\n" + "#"*70)
    print("# MCP Prompts Integration Test Suite")
    print("#"*70)
    
    all_results = {}
    
    try:
        # Test 1: List prompts
        all_results["list_prompts"] = test_list_prompts()
        
        # Test 2: Get prompts
        all_results["get_prompts"] = test_get_prompts()
        
        # Test 3: Discover prompts
        all_results["discover_prompts"] = test_discover_prompts()
        
        # Test 4: Get prompts with arguments
        all_results["get_with_args"] = test_get_prompts_with_arguments()
        
        # Test 5: Workflow integration
        all_results["workflow"] = test_workflow_integration()
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return all_results
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        return all_results
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    total_tests = 0
    passed_tests = 0
    
    for test_name, results in all_results.items():
        if isinstance(results, dict):
            for key, value in results.items():
                total_tests += 1
                if value and value != 0:
                    passed_tests += 1
    
    print(f"\n  Total Tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {total_tests - passed_tests}")
    print(f"  Success Rate: {(passed_tests/total_tests*100) if total_tests > 0 else 0:.1f}%")
    
    if passed_tests == total_tests:
        print("\n  ✅ All tests passed!")
    else:
        print(f"\n  ⚠️  {total_tests - passed_tests} test(s) failed")
    
    return all_results

if __name__ == "__main__":
    results = run_all_tests()
    sys.exit(0 if all(
        isinstance(r, dict) and any(v and v != 0 for v in r.values())
        for r in results.values()
    ) else 1)
