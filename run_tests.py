#!/usr/bin/env python3
"""
Cross-platform test runner for ESP32 BPM Detector
Works on Linux, macOS, and Windows

Supports:
- Native C++ compilation and testing
- Hardware emulation testing (--emulator)
- Docker-based testing (--docker)
- Parallel test execution
- Result reporting and logging
"""

import os
import sys
import subprocess
import platform
import argparse
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

def detect_compiler():
    """Detect available C++ compiler"""
    compilers = ['g++', 'clang++', 'c++']
    for compiler in compilers:
        try:
            result = subprocess.run(
                [compiler, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return compiler, result.stdout.split('\n')[0]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return None, None

def compile_test(source_file, executable):
    """Compile a test file"""
    compiler, version = detect_compiler()
    if not compiler:
        print(f"Error: No C++ compiler found (tried: g++, clang++, c++)")
        return False
    
    cxxflags = ['-std=c++17', '-Wall', '-Wextra', '-I.']
    ldflags = ['-lm']
    
    # Windows-specific adjustments
    if platform.system() == 'Windows':
        executable = executable + '.exe'
    
    cmd = [compiler] + cxxflags + ['-o', executable, source_file] + ldflags
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return True
        else:
            print(f"Compilation error:\n{result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"Compilation timeout for {source_file}")
        return False

def run_test(executable):
    """Run a test executable"""
    if platform.system() == 'Windows':
        executable = executable + '.exe'
    
    if not os.path.exists(executable):
        return False, "Executable not found"
    
    try:
        result = subprocess.run(
            [executable] if platform.system() != 'Windows' else [executable],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Test timeout"

def run_emulator_tests(emulator_host: str = "127.0.0.1", emulator_port: int = 12345) -> Dict[str, Any]:
    """Run hardware emulation tests."""
    print("🧪 Running Hardware Emulation Tests")
    print("-" * 40)

    results = {
        "test_type": "emulator",
        "passed": 0,
        "failed": 0,
        "total": 0,
        "details": []
    }

    try:
        # Import the test module
        import subprocess
        import sys
        import os

        # Set environment variables for the emulator tests
        env = os.environ.copy()
        env["HARDWARE_EMULATOR_HOST"] = emulator_host
        env["HARDWARE_EMULATOR_PORT"] = str(emulator_port)
        env["PYTHONPATH"] = f"/home/sparrow/mcp/servers/python/unified_deployment:{os.environ.get('PYTHONPATH', '')}"

        # Run pytest on hardware emulation tests
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/integration/test_hardware_emulation.py",
            "-v", "--tb=short"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
            env=env
        )

        results["return_code"] = result.returncode
        results["stdout"] = result.stdout
        results["stderr"] = result.stderr

        if result.returncode == 0:
            results["status"] = "passed"
            print("✅ Hardware emulation tests passed")
        else:
            results["status"] = "failed"
            print("❌ Hardware emulation tests failed")
            print(result.stdout)
            print(result.stderr)

    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
        print(f"❌ Error running emulator tests: {e}")

    return results


def run_docker_tests(test_suite: str = "all") -> Dict[str, Any]:
    """Run Docker-based tests."""
    print("🐳 Running Docker-based Tests")
    print("-" * 40)

    results = {
        "test_type": "docker",
        "passed": 0,
        "failed": 0,
        "total": 0,
        "details": []
    }

    try:
        # Run the Docker test runner script
        cmd = [
            sys.executable,
            "scripts/docker_test_runner.py",
            "--suite", test_suite,
            "--project-dir", str(Path(__file__).parent)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )

        results["return_code"] = result.returncode
        results["stdout"] = result.stdout
        results["stderr"] = result.stderr

        if result.returncode == 0:
            results["status"] = "passed"
            print("✅ Docker tests passed")
        else:
            results["status"] = "failed"
            print("❌ Docker tests failed")
            print(result.stdout)
            print(result.stderr)

    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
        print(f"❌ Error running Docker tests: {e}")

    return results


def run_native_tests(parallel: bool = False) -> Dict[str, Any]:
    """Run native C++ tests."""
    print("🔧 Running Native C++ Tests")
    print("-" * 40)

    results = {
        "test_type": "native",
        "passed": 0,
        "failed": 0,
        "total": 0,
        "details": []
    }

    compiler, version = detect_compiler()
    if not compiler:
        results["status"] = "error"
        results["error"] = "No C++ compiler found"
        return results

    print(f"Compiler: {version}")

    # Test files
    tests = [
        ("comprehensive_tests.cpp", "comprehensive_tests"),
        ("final_test.cpp", "final_test"),
        ("simple_validation.cpp", "simple_validation"),
        ("fft_logic_test.cpp", "fft_logic_test"),
    ]

    passed = 0
    failed = 0
    total = 0

    for source_file, executable in tests:
        if not os.path.exists(source_file):
            print(f"⚠️  Skipping {source_file} (not found)")
            continue

        total += 1
        print(f"Building {source_file}...")

        if compile_test(source_file, executable):
            print("✓ Compiled successfully")
            print(f"Running {executable}...")
            print("-" * 50)

            success, output = run_test(executable)
            print(output)
            print("-" * 50)

            test_detail = {
                "test": source_file,
                "compiled": True,
                "passed": success,
                "output": output
            }

            if success:
                print(f"✓ {executable} PASSED")
                passed += 1
            else:
                print(f"✗ {executable} FAILED")
                failed += 1

            results["details"].append(test_detail)
            print()
        else:
            print(f"✗ Compilation failed for {source_file}")
            failed += 1
            results["details"].append({
                "test": source_file,
                "compiled": False,
                "passed": False,
                "error": "Compilation failed"
            })
            print()

    results["passed"] = passed
    results["failed"] = failed
    results["total"] = total
    results["status"] = "passed" if failed == 0 else "failed"

    return results


def generate_test_report(all_results: Dict[str, Dict[str, Any]], output_file: Optional[str] = None) -> str:
    """Generate a comprehensive test report."""
    if not output_file:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = f"test_report_{timestamp}.json"

    report = {
        "timestamp": time.time(),
        "platform": f"{platform.system()} {platform.machine()}",
        "python_version": sys.version,
        "results": all_results,
        "summary": {
            "total_suites": len(all_results),
            "passed_suites": sum(1 for r in all_results.values() if r.get("status") == "passed"),
            "failed_suites": sum(1 for r in all_results.values() if r.get("status") == "failed"),
            "error_suites": sum(1 for r in all_results.values() if r.get("status") == "error")
        }
    }

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="ESP32 BPM Detector - Enhanced Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all native C++ tests
  python3 run_tests.py

  # Run hardware emulation tests
  python3 run_tests.py --emulator

  # Run Docker-based tests
  python3 run_tests.py --docker

  # Run all test types
  python3 run_tests.py --all

  # Run with parallel execution
  python3 run_tests.py --parallel

  # Generate detailed report
  python3 run_tests.py --all --report test_results.json
        """
    )

    parser.add_argument(
        "--emulator", "-e",
        action="store_true",
        help="Run hardware emulation tests"
    )

    parser.add_argument(
        "--docker", "-d",
        action="store_true",
        help="Run Docker-based integration tests"
    )

    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Run all test types (native, emulator, docker)"
    )

    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Run tests in parallel where possible"
    )

    parser.add_argument(
        "--emulator-host",
        default="127.0.0.1",
        help="Hardware emulator host (default: 127.0.0.1)"
    )

    parser.add_argument(
        "--emulator-port",
        type=int,
        default=12345,
        help="Hardware emulator port (default: 12345)"
    )

    parser.add_argument(
        "--report", "-r",
        help="Generate JSON report file"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    print("ESP32 BPM Detector - Enhanced Test Runner")
    print("=" * 60)
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Python: {sys.version.split()[0]}")
    print()

    # Determine which tests to run
    run_native = not (args.emulator or args.docker or args.all)
    run_emulator = args.emulator or args.all
    run_docker = args.docker or args.all

    all_results = {}

    # Run native tests
    if run_native:
        native_results = run_native_tests(parallel=args.parallel)
        all_results["native"] = native_results

    # Run emulator tests
    if run_emulator:
        emulator_results = run_emulator_tests(args.emulator_host, args.emulator_port)
        all_results["emulator"] = emulator_results

    # Run Docker tests
    if run_docker:
        docker_results = run_docker_tests("all")
        all_results["docker"] = docker_results

    # Generate report if requested
    if args.report:
        report_file = generate_test_report(all_results, args.report)
        print(f"📊 Test report generated: {report_file}")

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    total_passed = 0
    total_failed = 0
    total_errors = 0

    for test_type, results in all_results.items():
        status = results.get("status", "unknown")
        print(f"{test_type.upper()} Tests: {status.upper()}")

        if test_type == "native":
            passed = results.get("passed", 0)
            failed = results.get("failed", 0)
            total = results.get("total", 0)
            print(f"  Passed: {passed}/{total}")
            total_passed += passed
            total_failed += failed

        elif status == "passed":
            total_passed += 1
        elif status == "failed":
            total_failed += 1
        elif status == "error":
            total_errors += 1

        if status == "error" and "error" in results:
            print(f"  Error: {results['error']}")

    print()
    print(f"Test Suites: {len(all_results)}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Errors: {total_errors}")

    if total_failed == 0 and total_errors == 0:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed or had errors")
        sys.exit(1)

if __name__ == "__main__":
    main()
