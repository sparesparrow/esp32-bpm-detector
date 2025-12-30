#!/usr/bin/env python3
"""
Unit Test Runner for ESP32 BPM Detector

Runs C++ gtest unit tests and generates JUnit XML reports.
"""

import argparse
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class UnitTestRunner:
    """Runner for C++ unit tests using PlatformIO/gtest."""
    
    def __init__(self, project_dir: Path, output_dir: Optional[Path] = None):
        self.project_dir = project_dir
        self.output_dir = output_dir or project_dir / "test-results"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.test_files = [
            "tests/test_bpm_accuracy.cpp",
            "tests/test_display_handler.cpp",
            "tests/test_wifi_handler.cpp",
        ]
    
    def run_tests(
        self,
        filter_pattern: Optional[str] = None,
        verbose: bool = False,
        junit_output: bool = True,
    ) -> Dict[str, Any]:
        """Run unit tests and return results.
        
        Args:
            filter_pattern: Filter tests by name pattern
            verbose: Enable verbose output
            junit_output: Generate JUnit XML report
        
        Returns:
            Dictionary with test results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "project_dir": str(self.project_dir),
            "passed": True,
            "test_count": 0,
            "pass_count": 0,
            "fail_count": 0,
            "skip_count": 0,
            "duration": 0.0,
            "tests": [],
        }
        
        # Build test command
        cmd = ["pio", "test", "-e", "native"]
        
        if filter_pattern:
            cmd.extend(["--filter", filter_pattern])
        
        if verbose:
            cmd.append("-v")
        
        # Generate JUnit XML output
        junit_file = self.output_dir / "junit_unit_tests.xml"
        cmd.extend(["--junit-output", str(junit_file)])
        
        print(f"Running: {' '.join(cmd)}")
        print(f"Working directory: {self.project_dir}")
        
        start_time = datetime.now()
        
        try:
            proc = subprocess.run(
                cmd,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=300,
            )
            
            results["duration"] = (datetime.now() - start_time).total_seconds()
            results["output"] = proc.stdout
            results["stderr"] = proc.stderr
            results["return_code"] = proc.returncode
            results["passed"] = proc.returncode == 0
            
            # Parse JUnit XML if available
            if junit_output and junit_file.exists():
                junit_results = self._parse_junit_xml(junit_file)
                results.update(junit_results)
            else:
                # Parse from output
                results.update(self._parse_output(proc.stdout))
            
        except subprocess.TimeoutExpired:
            results["passed"] = False
            results["error"] = "Test execution timed out after 300 seconds"
        except FileNotFoundError:
            results["passed"] = False
            results["error"] = "PlatformIO not found. Please install with: pip install platformio"
        except Exception as e:
            results["passed"] = False
            results["error"] = str(e)
        
        # Save results
        results_file = self.output_dir / "unit_test_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def _parse_junit_xml(self, junit_file: Path) -> Dict[str, Any]:
        """Parse JUnit XML file for test results."""
        results = {
            "test_count": 0,
            "pass_count": 0,
            "fail_count": 0,
            "skip_count": 0,
            "tests": [],
        }
        
        try:
            tree = ET.parse(junit_file)
            root = tree.getroot()
            
            for testcase in root.findall(".//testcase"):
                test = {
                    "name": testcase.get("name"),
                    "classname": testcase.get("classname"),
                    "time": float(testcase.get("time", 0)),
                    "status": "passed",
                }
                
                failure = testcase.find("failure")
                if failure is not None:
                    test["status"] = "failed"
                    test["message"] = failure.get("message")
                    test["details"] = failure.text
                    results["fail_count"] += 1
                else:
                    results["pass_count"] += 1
                
                skipped = testcase.find("skipped")
                if skipped is not None:
                    test["status"] = "skipped"
                    results["skip_count"] += 1
                    results["pass_count"] -= 1
                
                results["tests"].append(test)
                results["test_count"] += 1
            
        except Exception as e:
            results["parse_error"] = str(e)
        
        return results
    
    def _parse_output(self, output: str) -> Dict[str, Any]:
        """Parse test results from output text."""
        import re
        
        results = {
            "test_count": 0,
            "pass_count": 0,
            "fail_count": 0,
            "tests": [],
        }
        
        # Look for common test result patterns
        patterns = {
            "passed": r"(\d+)\s+(?:tests?|assertions?)\s+passed",
            "failed": r"(\d+)\s+(?:tests?|assertions?)\s+failed",
            "total": r"(?:Ran|Total:?)\s+(\d+)\s+tests?",
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                count = int(match.group(1))
                if key == "passed":
                    results["pass_count"] = count
                elif key == "failed":
                    results["fail_count"] = count
                elif key == "total":
                    results["test_count"] = count
        
        if results["test_count"] == 0:
            results["test_count"] = results["pass_count"] + results["fail_count"]
        
        return results
    
    def list_tests(self) -> List[str]:
        """List available test files."""
        tests = []
        for test_file in self.test_files:
            full_path = self.project_dir / test_file
            if full_path.exists():
                tests.append(str(test_file))
        return tests


def main():
    parser = argparse.ArgumentParser(description="Run ESP32 BPM Detector unit tests")
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Project directory",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for test results",
    )
    parser.add_argument(
        "--filter",
        type=str,
        help="Filter tests by name pattern",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--no-junit",
        action="store_true",
        help="Disable JUnit XML output",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available test files",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    
    args = parser.parse_args()
    
    runner = UnitTestRunner(args.project_dir, args.output_dir)
    
    if args.list:
        tests = runner.list_tests()
        for test in tests:
            print(test)
        return 0
    
    results = runner.run_tests(
        filter_pattern=args.filter,
        verbose=args.verbose,
        junit_output=not args.no_junit,
    )
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"Unit Test Results")
        print(f"{'='*60}")
        print(f"Total Tests: {results['test_count']}")
        print(f"Passed: {results['pass_count']}")
        print(f"Failed: {results['fail_count']}")
        print(f"Duration: {results['duration']:.2f}s")
        print(f"Status: {'PASSED' if results['passed'] else 'FAILED'}")
        
        if not results['passed'] and 'error' in results:
            print(f"\nError: {results['error']}")
    
    return 0 if results['passed'] else 1


if __name__ == "__main__":
    sys.exit(main())
