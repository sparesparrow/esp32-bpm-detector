#!/usr/bin/env python3
"""
Run Tests with Learning Loop Integration
Integrates dev-intelligence-orchestrator, mcp-prompts, learning loop, and unified-deployment MCP server.
"""

import os
import sys
import json
import subprocess
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from learning_loop_integration import ToolExecutionRecorder, SmartToolSelector
from self_improving_learning_loop import SelfImprovingLearningLoop
from mcp_prompts_integration import list_prompts_mcp, get_prompt_mcp, discover_relevant_prompts

def detect_test_framework(project_root: Path) -> str:
    """Detect test framework based on project files."""
    if (project_root / "platformio.ini").exists() and (project_root / "test").exists():
        return "platformio"
    elif list(project_root.glob("**/test_*.py")) or list(project_root.glob("**/*_test.py")):
        return "pytest"
    elif list(project_root.glob("**/*_test.cpp")) or list(project_root.glob("**/*Test.cpp")):
        return "gtest"
    elif (project_root / "build.gradle").exists() or (project_root / "build.gradle.kts").exists():
        return "gradle"
    else:
        return "unknown"

def query_mcp_prompts_for_test_config(framework: str, project_type: str) -> Optional[Dict[str, Any]]:
    """Query mcp-prompts for learned test configurations."""
    try:
        # Search for test-related prompts
        prompts = list_prompts_mcp(tags=["test", framework, "tool-config"], limit=10)
        
        if prompts:
            # Find the most relevant prompt
            for prompt in prompts:
                prompt_data = prompt.get('template', {}) or prompt.get('content', {})
                if isinstance(prompt_data, str):
                    try:
                        prompt_data = json.loads(prompt_data)
                    except:
                        continue
                
                if prompt_data.get('framework') == framework and prompt_data.get('project_type') == project_type:
                    return prompt_data
        
        # Try to discover relevant prompts
        discovered = discover_relevant_prompts(f"test configuration {framework} {project_type}")
        if discovered:
            return discovered[0].get('template', {})
    except Exception as e:
        print(f"⚠️  Could not query mcp-prompts: {e}", file=sys.stderr)
    
    return None

def run_tests_with_dev_intelligence_orchestrator(
    project_root: Path,
    test_path: Optional[str] = None,
    coverage: bool = False
) -> Dict[str, Any]:
    """Run tests using dev-intelligence-orchestrator skill."""
    script_path = Path(__file__).parent.parent / ".claude" / "skills" / "dev-intelligence-orchestrator" / "scripts" / "run_tests.sh"
    
    if not script_path.exists():
        raise FileNotFoundError(f"run_tests.sh not found at {script_path}")
    
    cmd = [
        "bash",
        str(script_path),
        str(project_root),
        test_path or "",
        "true" if coverage else "false"
    ]
    
    print(f"🔧 Running tests with dev-intelligence-orchestrator...", file=sys.stderr)
    print(f"   Command: {' '.join(cmd)}", file=sys.stderr)
    
    start_time = time.time()
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=project_root
    )
    execution_time_ms = (time.time() - start_time) * 1000
    
    # Parse JSON output from script
    try:
        test_results = json.loads(result.stdout)
    except json.JSONDecodeError:
        # If JSON parsing fails, create a basic result structure
        test_results = {
            "framework": "unknown",
            "summary": {
                "passed": 0,
                "failed": 0,
                "total": 0
            },
            "success": result.returncode == 0,
            "raw_output": result.stdout,
            "error": result.stderr
        }
    
    test_results["execution_time_ms"] = execution_time_ms
    test_results["exit_code"] = result.returncode
    
    return test_results

def run_docker_tests_with_unified_deployment(project_root: Path) -> Dict[str, Any]:
    """Run Docker tests using unified-deployment MCP server."""
    try:
        # Use docker_test_runner.py script
        script_path = project_root / "scripts" / "docker_test_runner.py"
        
        if not script_path.exists():
            print("⚠️  docker_test_runner.py not found, skipping Docker tests", file=sys.stderr)
            return {"success": False, "error": "docker_test_runner.py not found"}
        
        cmd = ["python3", str(script_path), "--suite", "all"]
        
        print(f"🐳 Running Docker tests...", file=sys.stderr)
        print(f"   Command: {' '.join(cmd)}", file=sys.stderr)
        
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=project_root
        )
        execution_time_ms = (time.time() - start_time) * 1000
        
        # Parse results
        docker_results = {
            "framework": "docker",
            "summary": {
                "passed": 0,
                "failed": 0,
                "total": 0
            },
            "success": result.returncode == 0,
            "execution_time_ms": execution_time_ms,
            "raw_output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None
        }
        
        # Try to parse test results from output
        if "passed" in result.stdout.lower():
            # Simple parsing - could be improved
            import re
            passed_match = re.search(r'(\d+)\s+passed', result.stdout, re.IGNORECASE)
            failed_match = re.search(r'(\d+)\s+failed', result.stdout, re.IGNORECASE)
            
            if passed_match:
                docker_results["summary"]["passed"] = int(passed_match.group(1))
            if failed_match:
                docker_results["summary"]["failed"] = int(failed_match.group(1))
            
            docker_results["summary"]["total"] = (
                docker_results["summary"]["passed"] + docker_results["summary"]["failed"]
            )
        
        return docker_results
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "framework": "docker"
        }

def main():
    parser = argparse.ArgumentParser(description="Run tests with learning loop integration")
    parser.add_argument("--test-path", help="Specific test file or directory")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--docker", action="store_true", help="Also run Docker tests")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--no-learning", action="store_true", help="Skip learning loop recording")
    
    args = parser.parse_args()
    
    project_root = Path(args.project_root).resolve()
    project_type = project_root.name
    
    # Initialize learning loop
    prompts_dir = "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts"
    db_path = "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/learning.db"
    
    loop = SelfImprovingLearningLoop(prompts_dir, db_path)
    recorder = ToolExecutionRecorder(loop)
    selector = SmartToolSelector(loop)
    
    # Detect test framework
    framework = detect_test_framework(project_root)
    print(f"🔍 Detected test framework: {framework}", file=sys.stderr)
    
    # Query mcp-prompts for learned configurations
    learned_config = query_mcp_prompts_for_test_config(framework, project_type)
    if learned_config:
        print(f"✓ Found learned configuration from mcp-prompts", file=sys.stderr)
        print(f"  Framework: {learned_config.get('framework', 'unknown')}", file=sys.stderr)
        print(f"  Confidence: {learned_config.get('confidence', 'unknown')}", file=sys.stderr)
    else:
        print(f"ℹ️  No learned configuration found, using defaults", file=sys.stderr)
    
    # Get best config from learning loop
    best_config = selector.get_best_config("test", framework, project_type)
    if best_config:
        print(selector.display_selection_info(best_config), file=sys.stderr)
    
    # Run tests
    all_results = {}
    
    # Run main tests
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"Running {framework} tests...", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    
    test_results = run_tests_with_dev_intelligence_orchestrator(
        project_root,
        args.test_path,
        args.coverage
    )
    all_results["main_tests"] = test_results
    
    # Run Docker tests if requested
    if args.docker:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"Running Docker tests...", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        
        docker_results = run_docker_tests_with_unified_deployment(project_root)
        all_results["docker_tests"] = docker_results
    
    # Record in learning loop
    if not args.no_learning:
        print(f"\n💾 Recording test execution in learning loop...", file=sys.stderr)
        
        interaction_id = recorder.record_test_execution(
            framework=framework,
            project=project_type,
            result=test_results,
            execution_time_ms=test_results.get("execution_time_ms", 0)
        )
        
        print(f"✓ Recorded interaction: {interaction_id}", file=sys.stderr)
        
        # Show learning status
        print(f"\n{recorder.get_learning_status()}", file=sys.stderr)
    
    # Output results as JSON
    print("\n" + json.dumps(all_results, indent=2))
    
    # Exit with appropriate code
    main_success = test_results.get("success", False)
    docker_success = all_results.get("docker_tests", {}).get("success", True) if args.docker else True
    
    sys.exit(0 if (main_success and docker_success) else 1)

if __name__ == "__main__":
    main()
