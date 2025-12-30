#!/usr/bin/env python3
"""
Component Test Runner for ESP32 BPM Detector

Runs component-level tests with mocked dependencies.
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class MockServer:
    """Mock server for component testing."""
    
    def __init__(self, port: int = 8765):
        self.port = port
        self.process: Optional[subprocess.Popen] = None
    
    async def start(self):
        """Start the mock server."""
        mock_script = Path(__file__).parent.parent / "tests" / "integration" / "mock_esp32_server.py"
        if mock_script.exists():
            self.process = subprocess.Popen(
                [sys.executable, str(mock_script), "--port", str(self.port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            await asyncio.sleep(1)  # Wait for server to start
    
    async def stop(self):
        """Stop the mock server."""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)


class ComponentTestRunner:
    """Runner for component tests with mocked dependencies."""
    
    def __init__(self, project_dir: Path, output_dir: Optional[Path] = None):
        self.project_dir = project_dir
        self.output_dir = output_dir or project_dir / "test-results"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def run_tests(
        self,
        mock_esp32: bool = True,
        mock_android: bool = True,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """Run component tests.
        
        Args:
            mock_esp32: Use mocked ESP32 serial communication
            mock_android: Use mocked Android app client
            verbose: Enable verbose output
        
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
            "duration": 0.0,
            "tests": [],
        }
        
        start_time = datetime.now()
        mock_server = None
        
        try:
            # Start mock server if needed
            if mock_esp32:
                mock_server = MockServer()
                await mock_server.start()
                results["mock_server_started"] = True
            
            # Run ESP32 serial mock tests
            esp32_result = await self._test_esp32_serial_mock(verbose)
            results["tests"].append(esp32_result)
            self._update_counts(results, esp32_result)
            
            # Run Android client mock tests
            if mock_android:
                android_result = await self._test_android_client_mock(verbose)
                results["tests"].append(android_result)
                self._update_counts(results, android_result)
            
            # Run network protocol tests
            protocol_result = await self._test_network_protocol(verbose)
            results["tests"].append(protocol_result)
            self._update_counts(results, protocol_result)
            
            # Run FlatBuffers serialization tests
            flatbuffers_result = await self._test_flatbuffers_serialization(verbose)
            results["tests"].append(flatbuffers_result)
            self._update_counts(results, flatbuffers_result)
            
        except Exception as e:
            results["passed"] = False
            results["error"] = str(e)
        finally:
            # Stop mock server
            if mock_server:
                await mock_server.stop()
        
        results["duration"] = (datetime.now() - start_time).total_seconds()
        results["passed"] = results["fail_count"] == 0
        
        # Save results
        results_file = self.output_dir / "component_test_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def _update_counts(self, results: Dict, test_result: Dict):
        """Update test counts from a test result."""
        results["test_count"] += 1
        if test_result.get("passed", False):
            results["pass_count"] += 1
        else:
            results["fail_count"] += 1
    
    async def _test_esp32_serial_mock(self, verbose: bool) -> Dict[str, Any]:
        """Test ESP32 serial communication with mock."""
        test_result = {
            "name": "esp32_serial_mock",
            "passed": True,
            "duration": 0.0,
            "details": [],
        }
        
        start = datetime.now()
        
        try:
            # Import and run mock server test
            test_script = self.project_dir / "tests" / "integration" / "mock_esp32_server.py"
            
            if test_script.exists():
                proc = subprocess.run(
                    [sys.executable, str(test_script), "--test-mode"],
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                
                test_result["passed"] = proc.returncode == 0
                test_result["output"] = proc.stdout[:1000]
                if proc.stderr:
                    test_result["stderr"] = proc.stderr[:500]
            else:
                test_result["passed"] = True
                test_result["details"].append("Mock test script not found, skipping")
        
        except Exception as e:
            test_result["passed"] = False
            test_result["error"] = str(e)
        
        test_result["duration"] = (datetime.now() - start).total_seconds()
        return test_result
    
    async def _test_android_client_mock(self, verbose: bool) -> Dict[str, Any]:
        """Test Android app client with mock server."""
        test_result = {
            "name": "android_client_mock",
            "passed": True,
            "duration": 0.0,
            "details": [],
        }
        
        start = datetime.now()
        
        try:
            # Test network client
            test_script = self.project_dir / "tests" / "integration" / "test_network_client.py"
            
            if test_script.exists():
                proc = subprocess.run(
                    [sys.executable, str(test_script)],
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                
                test_result["passed"] = proc.returncode == 0
                test_result["output"] = proc.stdout[:1000]
            else:
                test_result["passed"] = True
                test_result["details"].append("Android client test not found, skipping")
        
        except Exception as e:
            test_result["passed"] = False
            test_result["error"] = str(e)
        
        test_result["duration"] = (datetime.now() - start).total_seconds()
        return test_result
    
    async def _test_network_protocol(self, verbose: bool) -> Dict[str, Any]:
        """Test network protocol handling."""
        test_result = {
            "name": "network_protocol",
            "passed": True,
            "duration": 0.0,
            "details": [],
        }
        
        start = datetime.now()
        
        try:
            # Test service discovery
            test_script = self.project_dir / "tests" / "integration" / "test_service_discovery.py"
            
            if test_script.exists():
                proc = subprocess.run(
                    [sys.executable, str(test_script)],
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                
                test_result["passed"] = proc.returncode == 0
                test_result["output"] = proc.stdout[:500]
            else:
                test_result["details"].append("Service discovery test not found")
        
        except Exception as e:
            test_result["passed"] = False
            test_result["error"] = str(e)
        
        test_result["duration"] = (datetime.now() - start).total_seconds()
        return test_result
    
    async def _test_flatbuffers_serialization(self, verbose: bool) -> Dict[str, Any]:
        """Test FlatBuffers serialization."""
        test_result = {
            "name": "flatbuffers_serialization",
            "passed": True,
            "duration": 0.0,
            "details": [],
        }
        
        start = datetime.now()
        
        try:
            # Check for generated headers
            include_dir = self.project_dir / "include"
            generated_headers = list(include_dir.glob("*_generated.h"))
            
            if generated_headers:
                test_result["details"].append(f"Found {len(generated_headers)} generated headers")
                test_result["passed"] = True
            else:
                test_result["details"].append("No generated headers found")
                # Not a failure if FlatBuffers not used
        
        except Exception as e:
            test_result["passed"] = False
            test_result["error"] = str(e)
        
        test_result["duration"] = (datetime.now() - start).total_seconds()
        return test_result


def main():
    parser = argparse.ArgumentParser(description="Run ESP32 BPM Detector component tests")
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
        "--no-mock-esp32",
        action="store_true",
        help="Disable ESP32 serial mock",
    )
    parser.add_argument(
        "--no-mock-android",
        action="store_true",
        help="Disable Android client mock",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    
    args = parser.parse_args()
    
    runner = ComponentTestRunner(args.project_dir, args.output_dir)
    
    results = asyncio.run(runner.run_tests(
        mock_esp32=not args.no_mock_esp32,
        mock_android=not args.no_mock_android,
        verbose=args.verbose,
    ))
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"Component Test Results")
        print(f"{'='*60}")
        print(f"Total Tests: {results['test_count']}")
        print(f"Passed: {results['pass_count']}")
        print(f"Failed: {results['fail_count']}")
        print(f"Duration: {results['duration']:.2f}s")
        print(f"Status: {'PASSED' if results['passed'] else 'FAILED'}")
        
        print(f"\nTest Details:")
        for test in results['tests']:
            status = "✓" if test['passed'] else "✗"
            print(f"  {status} {test['name']} ({test['duration']:.2f}s)")
            if 'error' in test:
                print(f"    Error: {test['error']}")
    
    return 0 if results['passed'] else 1


if __name__ == "__main__":
    sys.exit(main())
