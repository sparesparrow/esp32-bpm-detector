#!/usr/bin/env python3
"""
Learning Loop Workflow: ESP32 + Android Code Review, Build, Deploy, Test

This script orchestrates a complete learning loop that:
1. Uses cursor-agent with mcp-prompts for code review
2. Fixes issues found
3. Builds ESP32 firmware separately
4. Builds Android app separately
5. Deploys and tests separately
6. Tests together (end-to-end)
7. Analyzes results
8. Records in learning loop
9. Repeats the cycle

Note: This script should be run with sparetools bundled CPython.
Use: python3 scripts/ensure_bundled_python.py scripts/learning_loop_workflow.py [args...]
Or: sparetools python scripts/learning_loop_workflow.py [args...]
"""

import os
import sys
import json
import subprocess
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import tempfile

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import SpareTools utilities
from sparetools_utils import (
    setup_logging,
    run_command,
    get_project_root,
    load_config,
    save_config,
    get_python_command,
    is_using_bundled_python
)

# Configure logging using SpareTools utilities
logger = setup_logging(__name__)

# Check and warn if not using bundled CPython
if not is_using_bundled_python():
    logger.warning("Not using sparetools bundled CPython. For best results, use:")
    logger.warning("  python3 scripts/ensure_bundled_python.py scripts/learning_loop_workflow.py [args...]")
    logger.warning("  or: sparetools python scripts/learning_loop_workflow.py [args...]")

from self_improving_learning_loop import SelfImprovingLearningLoop
from notification_manager import NotificationManager
from mcp_prompts_integration import (
    list_prompts_mcp,
    get_prompt_mcp,
    discover_relevant_prompts
)

class LearningLoopWorkflow:
    """Orchestrates the complete learning loop workflow."""
    
    def __init__(
        self,
        project_root: str = None,
        prompts_dir: str = None,
        db_path: str = None
    ):
        if project_root is None:
            # Use SpareTools path utilities
            project_root = get_project_root(Path(__file__).parent)
        self.project_root = Path(project_root)
        
        if prompts_dir is None:
            prompts_dir = "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts"
        self.prompts_dir = prompts_dir
        
        if db_path is None:
            db_path = "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/learning.db"
        self.db_path = db_path
        
        self.loop = SelfImprovingLearningLoop(self.prompts_dir, self.db_path)
        self.results = {
            "cycle": 0,
            "timestamp": None,
            "code_review": {},
            "esp32_build": {},
            "android_build": {},
            "esp32_test": {},
            "android_test": {},
            "e2e_test": {},
            "improvements": []
        }
        
        # Initialize notification manager
        self.notify = NotificationManager(
            enable_mqtt=True,
            enable_serial=False  # Use MQTT by default, serial as fallback
        )
    
    def run_cursor_agent_command(self, command: str, timeout: int = 1800) -> Tuple[bool, str, Dict]:
        """Execute cursor-agent command and capture results."""
        print(f"\n{'='*70}")
        print(f"🔧 Executing: {command}")
        print(f"{'='*70}")
        
        start_time = time.time()
        try:
            # Use SpareTools subprocess utilities
            result = run_command(
                ["cursor-agent", "--print", "--approve-mcps", command],
                cwd=self.project_root,
                timeout=timeout,
                check=False
            )
            elapsed = time.time() - start_time
            
            success = result.returncode == 0
            output = (result.stdout or "") + (result.stderr or "")
            
            metrics = {
                "execution_time_ms": elapsed * 1000,
                "exit_code": result.returncode,
                "output_length": len(output)
            }
            
            return success, output, metrics
            
        except subprocess.TimeoutExpired:
            elapsed = time.time() - start_time
            logger.warning(f"Command timed out after {elapsed:.1f}s")
            return False, f"Command timed out after {elapsed:.1f}s", {
                "execution_time_ms": elapsed * 1000,
                "timeout": True
            }
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Error running cursor-agent command: {e}")
            return False, str(e), {
                "execution_time_ms": elapsed * 1000,
                "error": str(e)
            }
    
    def get_prompt_for_review(self, target: str) -> Optional[str]:
        """Get appropriate prompt from mcp-prompts for code review using MCP tools."""
        try:
            # Discover relevant prompts for the target
            context = {"platform": target}
            if target == "esp32":
                context["language"] = "cpp"
                context["embedded"] = True
                context["code_path"] = "src/"
            elif target == "android":
                context["language"] = "kotlin"
                context["code_path"] = "android-app/app/src/main/"
            
            prompts = discover_relevant_prompts("code-review", context)
            
            # Select best prompt
            if prompts:
                # Prefer prompts with matching tags
                prompt_name = prompts[0].get("name", "code-review-assistant")
            else:
                # Fallback to standard prompts
                prompt_name = "code-review-assistant"
            
            # Prepare template arguments for the prompt
            template_args = {
                "platform": target,
                "language": "cpp" if target == "esp32" else "kotlin",
                "code_path": context.get("code_path", "src/")
            }
            
            # Get the prompt using MCP integration with template variables
            prompt = get_prompt_mcp(prompt_name, arguments=template_args)
            
            if prompt:
                logger.info(f"Retrieved prompt '{prompt_name}' for {target} review with template variables")
                return prompt
            
        except Exception as e:
            logger.warning(f"Failed to get prompt via MCP integration: {e}, falling back to cursor-agent")
        
        # Fallback to cursor-agent
        if target == "esp32":
            prompt_name = "code-review-assistant"
        elif target == "android":
            prompt_name = "code-review-assistant"
        else:
            prompt_name = "analysis-assistant"
        
        command = f"Use mcp-prompts get_prompt name={prompt_name}"
        success, output, metrics = self.run_cursor_agent_command(command)
        
        if success:
            return output
        return None
    
    def review_code(self, target: str) -> Dict:
        """Review code using cursor-agent and mcp-prompts."""
        print(f"\n{'='*70}")
        print(f"📋 Code Review: {target.upper()}")
        print(f"{'='*70}")
        
        # Notify phase start
        self.notify.notify_phase_start(f"{target} code review")
        
        # Get appropriate prompt
        prompt_content = self.get_prompt_for_review(target)
        
        if target == "esp32":
            code_path = "src/"
            review_query = f"Review ESP32 firmware code in {code_path} for bugs, performance issues, and best practices. Use the esp32-debugging-workflow prompt from mcp-prompts."
        else:  # android
            code_path = "android-app/app/src/main/"
            review_query = f"Review Android app code in {code_path} for bugs, performance issues, and best practices."
        
        command = f"{review_query}"
        success, output, metrics = self.run_cursor_agent_command(command)
        
        # Extract issues from output
        issues = []
        if "error" in output.lower() or "bug" in output.lower() or "issue" in output.lower():
            # Simple heuristic - in production, use more sophisticated parsing
            issues.append("Potential issues found in code review")
        
        result = {
            "success": success,
            "output": output,
            "metrics": metrics,
            "issues_found": len(issues),
            "issues": issues
        }
        
        # Record in learning loop
        self.loop.record_interaction(
            prompt_id=f"{target}-code-review",
            query=review_query,
            success=success,
            metrics={
                **metrics,
                "issues_found": len(issues),
                "target": target
            },
            metadata={
                "code_path": code_path,
                "output": output[:500]  # Truncate for storage
            }
        )
        
        # Notify result
        if success:
            if len(issues) > 0:
                self.notify.notify_warning(f"{target} review found {len(issues)} issues")
            else:
                self.notify.notify_success(f"{target} code review complete")
        else:
            self.notify.notify_failure(f"{target} code review failed")
        
        return result
    
    def build_esp32(self, environment: str = "esp32-s3") -> Dict:
        """Build ESP32 firmware."""
        print(f"\n{'='*70}")
        print(f"🔨 Building ESP32 ({environment})")
        print(f"{'='*70}")
        
        # Notify phase start
        self.notify.notify_phase_start(f"ESP32 build ({environment})")
        
        # Spawn build log monitor
        build_log = self.project_root / ".pio" / "build" / environment / "build.log"
        if build_log.exists():
            self.notify.monitor_logs(str(build_log), "ESP32 Build Log")
        
        start_time = time.time()
        try:
            # Use SpareTools subprocess utilities
            result = run_command(
                ["pio", "run", "--environment", environment],
                cwd=self.project_root,
                timeout=900  # Increased timeout for builds
            )
            elapsed = time.time() - start_time
            
            success = result.returncode == 0
            output = (result.stdout or "") + (result.stderr or "")
            
            # Extract build info
            build_size = None
            if "RAM" in output and "Flash" in output:
                # Parse PlatformIO build output
                for line in output.split('\n'):
                    if "RAM" in line and "Flash" in line:
                        build_size = line.strip()
                        break
            
            metrics = {
                "execution_time_ms": elapsed * 1000,
                "exit_code": result.returncode,
                "build_size": build_size
            }
            
            result_dict = {
                "success": success,
                "output": output,
                "metrics": metrics,
                "environment": environment
            }
            
            # Record in learning loop
            self.loop.record_interaction(
                prompt_id="esp32-build",
                query=f"Build ESP32 firmware for {environment}",
                success=success,
                metrics=metrics,
                metadata={
                    "environment": environment,
                    "build_size": build_size
                }
            )
            
            # Notify result
            if success:
                self.notify.notify_success(f"ESP32 build complete ({environment})")
            else:
                self.notify.notify_failure(f"ESP32 build failed ({environment})")
            
            return result_dict
            
        except subprocess.TimeoutExpired:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "output": "Build timed out",
                "metrics": {"execution_time_ms": elapsed * 1000, "timeout": True},
                "environment": environment
            }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "output": str(e),
                "metrics": {"execution_time_ms": elapsed * 1000, "error": str(e)},
                "environment": environment
            }
    
    def build_android(self, build_type: str = "debug") -> Dict:
        """Build Android app."""
        print(f"\n{'='*70}")
        print(f"🔨 Building Android ({build_type})")
        print(f"{'='*70}")
        
        # Notify phase start
        self.notify.notify_phase_start(f"Android build ({build_type})")
        
        # Start scrcpy for Android device monitoring
        self.notify.start_scrcpy(window_title="Android Build Monitor")
        
        android_dir = self.project_root / "android-app"
        if not android_dir.exists():
            self.notify.notify_failure("Android app directory not found")
            return {
                "success": False,
                "output": "Android app directory not found",
                "metrics": {},
                "build_type": build_type
            }
        
        # Spawn build log monitor
        build_log = android_dir / "build" / "outputs" / "logs" / "build.log"
        if not build_log.exists():
            build_log = android_dir / "build.log"
        if build_log.exists():
            self.notify.monitor_logs(str(build_log), "Android Build Log")
        
        start_time = time.time()
        try:
            # Use SpareTools subprocess utilities
            if build_type == "debug":
                result = run_command(
                    ["./gradlew", "assembleDebug"],
                    cwd=android_dir,
                    timeout=900  # Increased timeout for Android builds
                )
            else:
                result = run_command(
                    ["./gradlew", "assembleRelease"],
                    cwd=android_dir,
                    timeout=900  # Increased timeout for Android builds
                )
            
            elapsed = time.time() - start_time
            success = result.returncode == 0
            output = (result.stdout or "") + (result.stderr or "")
            
            # Extract APK path
            apk_path = None
            if success:
                if build_type == "debug":
                    apk_path = android_dir / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
                else:
                    apk_path = android_dir / "app" / "build" / "outputs" / "apk" / "release" / "app-release.apk"
            
            metrics = {
                "execution_time_ms": elapsed * 1000,
                "exit_code": result.returncode,
                "apk_path": str(apk_path) if apk_path and apk_path.exists() else None
            }
            
            result_dict = {
                "success": success,
                "output": output,
                "metrics": metrics,
                "build_type": build_type
            }
            
            # Record in learning loop
            self.loop.record_interaction(
                prompt_id="android-build",
                query=f"Build Android app ({build_type})",
                success=success,
                metrics=metrics,
                metadata={
                    "build_type": build_type,
                    "apk_path": str(apk_path) if apk_path else None
                }
            )
            
            # Notify result
            if success:
                self.notify.notify_success(f"Android build complete ({build_type})")
            else:
                self.notify.notify_failure(f"Android build failed ({build_type})")
            
            return result_dict
            
        except subprocess.TimeoutExpired:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "output": "Build timed out",
                "metrics": {"execution_time_ms": elapsed * 1000, "timeout": True},
                "build_type": build_type
            }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "output": str(e),
                "metrics": {"execution_time_ms": elapsed * 1000, "error": str(e)},
                "build_type": build_type
            }
    
    def test_esp32(self, device_port: str = None) -> Dict:
        """Test ESP32 firmware (hardware emulation or physical device)."""
        print(f"\n{'='*70}")
        print(f"🧪 Testing ESP32")
        print(f"{'='*70}")
        
        # Notify phase start
        self.notify.notify_phase_start("ESP32 testing")
        
        # Use hardware emulator if no device port specified
        if device_port is None:
            # Run emulator tests
            test_script = self.project_root / "run_tests.py"
            if test_script.exists():
                start_time = time.time()
                try:
                    # Use SpareTools subprocess utilities with bundled CPython
                    python_cmd = get_python_command()
                    result = run_command(
                        python_cmd + [str(test_script), "--emulator"],
                        cwd=self.project_root,
                        timeout=600  # Increased timeout for tests
                    )
                    elapsed = time.time() - start_time
                    success = result.returncode == 0
                    
                    result_dict = {
                        "success": success,
                        "output": (result.stdout or "") + (result.stderr or ""),
                        "metrics": {
                            "execution_time_ms": elapsed * 1000,
                            "test_type": "emulator"
                        },
                        "device_port": None
                    }
                    
                    # Notify result
                    if success:
                        self.notify.notify_success("ESP32 tests passed")
                    else:
                        self.notify.notify_failure("ESP32 tests failed")
                    
                    return result_dict
                except Exception as e:
                    return {
                        "success": False,
                        "output": str(e),
                        "metrics": {"error": str(e)},
                        "device_port": None
                    }
        
        # Physical device testing would go here
        return {
            "success": False,
            "output": "Physical device testing not implemented",
            "metrics": {},
            "device_port": device_port
        }
    
    def test_android(self) -> Dict:
        """Test Android app."""
        print(f"\n{'='*70}")
        print(f"🧪 Testing Android")
        print(f"{'='*70}")
        
        # Notify phase start
        self.notify.notify_phase_start("Android testing")
        
        # Ensure scrcpy is running for test monitoring
        self.notify.start_scrcpy(window_title="Android Test Monitor")
        
        android_dir = self.project_root / "android-app"
        if not android_dir.exists():
            self.notify.notify_failure("Android app directory not found")
            return {
                "success": False,
                "output": "Android app directory not found",
                "metrics": {}
            }
        
        # Spawn test log monitor
        test_log = android_dir / "build" / "reports" / "tests" / "test" / "index.html"
        if test_log.exists():
            python_cmd = " ".join(get_python_command())
            self.notify.spawn_terminal(
                f"cd {android_dir} && {python_cmd} -m http.server 8080",
                "Android Test Report"
            )
        
        start_time = time.time()
        try:
            # Use SpareTools subprocess utilities
            result = run_command(
                ["./gradlew", "test"],
                cwd=android_dir,
                timeout=600  # Increased timeout for Android tests
            )
            elapsed = time.time() - start_time
            success = result.returncode == 0
            
            # Parse test results
            test_count = 0
            passed = 0
            failed = 0
            stdout = result.stdout or ""
            for line in stdout.split('\n'):
                if "tests completed" in line.lower():
                    # Extract test counts
                    pass
            
            result_dict = {
                "success": success,
                "output": (result.stdout or "") + (result.stderr or ""),
                "metrics": {
                    "execution_time_ms": elapsed * 1000,
                    "test_count": test_count,
                    "passed": passed,
                    "failed": failed
                }
            }
            
            # Notify result
            if success:
                self.notify.notify_success(f"Android tests passed ({passed}/{test_count})")
            else:
                self.notify.notify_failure(f"Android tests failed ({failed}/{test_count})")
            
            return result_dict
            
        except Exception as e:
            return {
                "success": False,
                "output": str(e),
                "metrics": {"error": str(e)}
            }
    
    def test_e2e(self) -> Dict:
        """End-to-end test: ESP32 + Android together."""
        print(f"\n{'='*70}")
        print(f"🔗 End-to-End Testing (ESP32 + Android)")
        print(f"{'='*70}")
        
        # Notify phase start
        self.notify.notify_phase_start("End-to-end testing")
        
        # Ensure scrcpy is running
        self.notify.start_scrcpy(window_title="E2E Test Monitor")
        
        # Run integration tests
        test_script = self.project_root / "scripts" / "test_e2e.py"
        if test_script.exists():
            start_time = time.time()
            try:
                # Use SpareTools subprocess utilities with bundled CPython
                python_cmd = get_python_command()
                result = run_command(
                    python_cmd + [str(test_script)],
                    cwd=self.project_root,
                    timeout=900  # Increased timeout for E2E tests
                )
                elapsed = time.time() - start_time
                success = result.returncode == 0
                
                return {
                    "success": success,
                    "output": (result.stdout or "") + (result.stderr or ""),
                    "metrics": {
                        "execution_time_ms": elapsed * 1000
                    }
                }
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"E2E test error: {e}")
                return {
                    "success": False,
                    "output": str(e),
                    "metrics": {"error": str(e), "execution_time_ms": elapsed * 1000}
                }
        
        return {
            "success": False,
            "output": "E2E test script not found",
            "metrics": {}
        }
    
    def analyze_results(self) -> Dict:
        """Analyze all results and generate improvements."""
        print(f"\n{'='*70}")
        print(f"📊 Analyzing Results")
        print(f"{'='*70}")
        
        analysis = {
            "overall_success": True,
            "issues": [],
            "improvements": [],
            "metrics": {}
        }
        
        # Check each phase
        phases = [
            ("code_review", "Code Review"),
            ("esp32_build", "ESP32 Build"),
            ("android_build", "Android Build"),
            ("esp32_test", "ESP32 Test"),
            ("android_test", "Android Test"),
            ("e2e_test", "E2E Test")
        ]
        
        for phase_key, phase_name in phases:
            phase_result = self.results.get(phase_key, {})
            if not phase_result.get("success", False):
                analysis["overall_success"] = False
                analysis["issues"].append(f"{phase_name} failed")
        
        # Generate improvement suggestions
        if not analysis["overall_success"]:
            analysis["improvements"].append("Fix failing phases before next cycle")
        
        # Calculate overall metrics
        total_time = sum(
            r.get("metrics", {}).get("execution_time_ms", 0)
            for r in self.results.values()
            if isinstance(r, dict)
        )
        analysis["metrics"]["total_time_ms"] = total_time
        
        return analysis
    
    def run_cycle(self, cycle_num: int = 1) -> Dict:
        """Run a complete learning loop cycle."""
        print(f"\n{'#'*70}")
        print(f"# Learning Loop Cycle {cycle_num}")
        print(f"{'#'*70}")
        
        # Notify cycle start
        self.notify.notify_cycle_start(cycle_num)
        
        cycle_start_time = time.time()
        self.results["cycle"] = cycle_num
        self.results["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Phase 1: Code Review (run in parallel - independent operations)
        print("\n📋 PHASE 1: Code Review")
        self.notify.notify_phase_start("Code Review")
        self.notify.notify_learning_progress("Code Review", 0, 2)
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        # Run ESP32 and Android reviews in parallel (they don't interfere)
        with ThreadPoolExecutor(max_workers=2) as executor:
            esp32_future = executor.submit(self.review_code, "esp32")
            android_future = executor.submit(self.review_code, "android")
            
            esp32_result = esp32_future.result(timeout=600)  # Increased timeout
            android_result = android_future.result(timeout=600)
            
            self.results["code_review"] = {
                "esp32": esp32_result,
                "android": android_result
            }
        
        self.notify.notify_learning_progress("Code Review", 2, 2)
        
        # Phase 2: Build Separately (run in parallel - independent builds)
        print("\n🔨 PHASE 2: Build Separately")
        self.notify.notify_phase_start("Build Phase")
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        # Run ESP32 and Android builds in parallel (they don't interfere)
        with ThreadPoolExecutor(max_workers=2) as executor:
            esp32_build_future = executor.submit(self.build_esp32)
            android_build_future = executor.submit(self.build_android)
            
            esp32_build_result = esp32_build_future.result(timeout=900)  # Increased timeout for builds
            android_build_result = android_build_future.result(timeout=900)
            
            self.results["esp32_build"] = esp32_build_result
            self.results["android_build"] = android_build_result
        
        # Phase 3: Test Separately (run in parallel - independent tests)
        print("\n🧪 PHASE 3: Test Separately")
        self.notify.notify_phase_start("Test Phase")
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        # Run ESP32 and Android tests in parallel (they don't interfere)
        with ThreadPoolExecutor(max_workers=2) as executor:
            esp32_test_future = executor.submit(self.test_esp32)
            android_test_future = executor.submit(self.test_android)
            
            esp32_test_result = esp32_test_future.result(timeout=600)  # Increased timeout for tests
            android_test_result = android_test_future.result(timeout=600)
            
            self.results["esp32_test"] = esp32_test_result
            self.results["android_test"] = android_test_result
        
        # Phase 4: Test Together
        print("\n🔗 PHASE 4: Test Together (E2E)")
        self.results["e2e_test"] = self.test_e2e()
        
        # Phase 5: Analyze Results
        print("\n📊 PHASE 5: Analyze Results")
        analysis = self.analyze_results()
        self.results["analysis"] = analysis
        
        # Phase 6: Record in Learning Loop
        print("\n💾 PHASE 6: Recording in Learning Loop")
        self.loop.record_interaction(
            prompt_id="learning-loop-cycle",
            query=f"Complete learning loop cycle {cycle_num}",
            success=analysis["overall_success"],
            metrics={
                "cycle": cycle_num,
                "total_time_ms": analysis["metrics"]["total_time_ms"],
                "phases_passed": sum(
                    1 for phase in ["code_review", "esp32_build", "android_build", 
                                   "esp32_test", "android_test", "e2e_test"]
                    if self.results.get(phase, {}).get("success", False)
                )
            },
            metadata={
                "results": json.dumps(self.results, default=str)[:1000]  # Truncate
            }
        )
        
        # Notify cycle complete
        cycle_duration = time.time() - cycle_start_time
        self.notify.notify_cycle_complete(cycle_num, analysis["overall_success"], cycle_duration)
        
        return self.results
    
    def run_continuous(self, max_cycles: int = 5, delay_seconds: int = 60):
        """Run continuous learning loop cycles."""
        print(f"\n{'#'*70}")
        print(f"# Starting Continuous Learning Loop")
        print(f"# Max Cycles: {max_cycles}")
        print(f"# Delay Between Cycles: {delay_seconds}s")
        print(f"{'#'*70}")
        
        self.notify.speak(f"Starting continuous learning loop with {max_cycles} cycles")
        self.notify.set_light_color("blue", blink=True)
        
        for cycle in range(1, max_cycles + 1):
            results = self.run_cycle(cycle)
            
            # Save results
            results_file = self.project_root / "test_results" / f"learning_loop_cycle_{cycle}.json"
            results_file.parent.mkdir(parents=True, exist_ok=True)
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"\n✅ Cycle {cycle} complete. Results saved to {results_file}")
            
            if cycle < max_cycles:
                print(f"\n⏳ Waiting {delay_seconds}s before next cycle...")
                self.notify.notify_learning_progress("Continuous Loop", cycle, max_cycles)
                time.sleep(delay_seconds)
        
        print(f"\n{'#'*70}")
        print(f"# Learning Loop Complete")
        print(f"{'#'*70}")
        
        # Show final statistics
        stats = self.loop.db.get_statistics()
        print(f"\n📊 Final Statistics:")
        print(f"  Total Interactions: {stats['total_interactions']}")
        print(f"  Active Prompts: {stats['total_prompts']}")
        print(f"  Average Success Rate: {stats['avg_success_rate']:.1f}%")
        
        # Final notification
        self.notify.speak(f"Continuous learning loop complete. {stats['total_interactions']} interactions recorded")
        self.notify.set_light_color("green")

def main():
    """CLI interface."""
    parser = argparse.ArgumentParser(
        description="Learning Loop Workflow: ESP32 + Android"
    )
    parser.add_argument(
        "--cycle", type=int, default=1,
        help="Run a single cycle (default: 1)"
    )
    parser.add_argument(
        "--continuous", type=int, metavar="N",
        help="Run N continuous cycles"
    )
    parser.add_argument(
        "--delay", type=int, default=60,
        help="Delay between cycles in seconds (default: 60)"
    )
    parser.add_argument(
        "--project-root", type=str,
        help="Project root directory"
    )
    
    args = parser.parse_args()
    
    workflow = LearningLoopWorkflow(project_root=args.project_root)
    
    if args.continuous:
        workflow.run_continuous(
            max_cycles=args.continuous,
            delay_seconds=args.delay
        )
    else:
        results = workflow.run_cycle(args.cycle)
        print("\n✅ Cycle complete!")
        print(f"\nResults: {json.dumps(results, indent=2, default=str)}")

if __name__ == "__main__":
    main()
