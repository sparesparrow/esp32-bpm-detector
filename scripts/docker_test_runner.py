#!/usr/bin/env python3
"""
Docker-based Test Runner for ESP32 BPM Detector

Orchestrates Docker container startup, runs tests against emulated hardware,
collects and reports test results, and handles container cleanup.
"""

import os
import sys
import subprocess
import time
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('docker-test-runner')

class DockerTestRunner:
    """Manages Docker-based testing infrastructure."""

    def __init__(self, project_dir: str = None):
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.test_results_dir = self.project_dir / "test_results"
        self.logs_dir = self.project_dir / "logs"
        self.compose_file = self.project_dir / "docker-compose.yml"

        # Ensure directories exist
        self.test_results_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

        # Test run tracking
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.containers_started = []

    def run_command(self, cmd: List[str], cwd: Path = None, timeout: int = 300) -> subprocess.CompletedProcess:
        """Run a shell command with logging."""
        cmd_str = " ".join(cmd)
        logger.info(f"Running: {cmd_str}")

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.project_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode != 0:
                logger.error(f"Command failed: {cmd_str}")
                logger.error(f"STDOUT: {result.stdout}")
                logger.error(f"STDERR: {result.stderr}")
            else:
                logger.debug(f"Command succeeded: {cmd_str}")

            return result
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout}s: {cmd_str}")
            raise

    def build_test_containers(self) -> bool:
        """Build Docker test containers."""
        logger.info("Building test containers...")

        try:
            result = self.run_command([
                "docker-compose", "-f", str(self.compose_file), "build",
                "esp32-emulator", "integration-tests", "mock-services"
            ])

            if result.returncode == 0:
                logger.info("✅ Test containers built successfully")
                return True
            else:
                logger.error("❌ Failed to build test containers")
                return False
        except Exception as e:
            logger.error(f"Error building containers: {e}")
            return False

    def start_test_environment(self) -> bool:
        """Start the test environment (emulator and mock services)."""
        logger.info("Starting test environment...")

        try:
            # Start emulator and mock services
            result = self.run_command([
                "docker-compose", "-f", str(self.compose_file), "up", "-d",
                "esp32-emulator", "mock-services"
            ])

            if result.returncode != 0:
                logger.error("❌ Failed to start test environment")
                return False

            # Wait for services to be ready
            logger.info("Waiting for services to be ready...")
            time.sleep(5)

            # Check if emulator is responding
            if not self.wait_for_service("esp32-emulator", 12345, timeout=30):
                logger.error("❌ Emulator service not ready")
                return False

            if not self.wait_for_service("mock-services", 8080, timeout=30):
                logger.error("❌ Mock API service not ready")
                return False

            logger.info("✅ Test environment started successfully")
            return True

        except Exception as e:
            logger.error(f"Error starting test environment: {e}")
            return False

    def wait_for_service(self, container_name: str, port: int, timeout: int = 30) -> bool:
        """Wait for a container service to be ready on specified port."""
        import socket

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Get container IP
                result = self.run_command([
                    "docker", "inspect", "-f",
                    "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}",
                    container_name
                ])

                if result.returncode == 0:
                    ip = result.stdout.strip()
                    if ip:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(1)
                        try:
                            sock.connect((ip, port))
                            sock.close()
                            logger.info(f"✅ Service {container_name}:{port} is ready")
                            return True
                        except:
                            sock.close()

            except Exception as e:
                logger.debug(f"Service check failed: {e}")

            time.sleep(1)

        logger.warning(f"⏳ Service {container_name}:{port} not ready after {timeout}s")
        return False

    def run_integration_tests(self, test_suite: str = "all") -> Dict[str, Any]:
        """Run integration tests in Docker containers."""
        logger.info(f"Running integration tests (suite: {test_suite})...")

        results = {
            "test_run_id": self.test_run_id,
            "test_suite": test_suite,
            "start_time": datetime.now().isoformat(),
            "tests": {},
            "overall_status": "running"
        }

        try:
            # Run the integration tests container
            cmd = [
                "docker-compose", "-f", str(self.compose_file), "run", "--rm",
                "-e", f"TEST_RUN_ID={self.test_run_id}",
                "integration-tests"
            ]

            result = self.run_command(cmd, timeout=600)  # 10 minute timeout

            results["end_time"] = datetime.now().isoformat()
            results["return_code"] = result.returncode
            results["stdout"] = result.stdout
            results["stderr"] = result.stderr

            if result.returncode == 0:
                results["overall_status"] = "passed"
                logger.info("✅ Integration tests passed")
            else:
                results["overall_status"] = "failed"
                logger.error("❌ Integration tests failed")

            # Parse test results if available
            self._parse_test_results(results)

        except subprocess.TimeoutExpired:
            results["overall_status"] = "timeout"
            results["error"] = "Tests timed out"
            logger.error("❌ Integration tests timed out")
        except Exception as e:
            results["overall_status"] = "error"
            results["error"] = str(e)
            logger.error(f"Error running integration tests: {e}")

        return results

    def _parse_test_results(self, results: Dict[str, Any]):
        """Parse test result files and update results dict."""
        # Look for JUnit XML files
        junit_files = list(self.test_results_dir.glob("*.xml"))
        for junit_file in junit_files:
            logger.info(f"Found test results: {junit_file}")
            # Basic parsing - could be enhanced with xml parsing library
            try:
                with open(junit_file, 'r') as f:
                    content = f.read()
                    results["tests"][junit_file.name] = {
                        "content": content,
                        "file": str(junit_file)
                    }
            except Exception as e:
                logger.warning(f"Could not read test results file {junit_file}: {e}")

    def collect_logs(self) -> Dict[str, str]:
        """Collect logs from test containers."""
        logger.info("Collecting container logs...")

        logs = {}
        containers = ["esp32-emulator", "integration-tests", "mock-services"]

        for container in containers:
            try:
                result = self.run_command([
                    "docker-compose", "-f", str(self.compose_file), "logs", container
                ])

                if result.returncode == 0:
                    logs[container] = result.stdout
                    # Save to file
                    log_file = self.logs_dir / f"{container}_{self.test_run_id}.log"
                    with open(log_file, 'w') as f:
                        f.write(result.stdout)
                    logger.info(f"✅ Logs collected for {container}")
                else:
                    logs[container] = f"Error collecting logs: {result.stderr}"

            except Exception as e:
                logs[container] = f"Error: {e}"
                logger.warning(f"Could not collect logs for {container}: {e}")

        return logs

    def stop_test_environment(self):
        """Stop the test environment and clean up containers."""
        logger.info("Stopping test environment...")

        try:
            result = self.run_command([
                "docker-compose", "-f", str(self.compose_file), "down", "-v"
            ])

            if result.returncode == 0:
                logger.info("✅ Test environment stopped and cleaned up")
            else:
                logger.warning("⚠️ Some issues stopping test environment")

        except Exception as e:
            logger.error(f"Error stopping test environment: {e}")

    def generate_report(self, test_results: Dict[str, Any], logs: Dict[str, str]) -> str:
        """Generate a comprehensive test report."""
        report_file = self.test_results_dir / f"test_report_{self.test_run_id}.json"

        report = {
            "test_run_id": self.test_run_id,
            "timestamp": datetime.now().isoformat(),
            "project_dir": str(self.project_dir),
            "test_results": test_results,
            "container_logs": logs,
            "environment_info": {
                "docker_version": self._get_docker_version(),
                "compose_version": self._get_compose_version(),
                "python_version": sys.version,
                "platform": sys.platform
            }
        }

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"📊 Test report generated: {report_file}")
        return str(report_file)

    def _get_docker_version(self) -> str:
        """Get Docker version."""
        try:
            result = self.run_command(["docker", "--version"])
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"

    def _get_compose_version(self) -> str:
        """Get Docker Compose version."""
        try:
            result = self.run_command(["docker-compose", "--version"])
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"

    def run_full_test_suite(self, test_suite: str = "all") -> Dict[str, Any]:
        """Run the complete test suite with setup and teardown."""
        logger.info(f"🚀 Starting full test suite: {test_suite}")

        success = True
        results = {}
        logs = {}

        try:
            # Phase 1: Build containers
            if not self.build_test_containers():
                success = False

            # Phase 2: Start test environment
            if success and not self.start_test_environment():
                success = False

            # Phase 3: Run tests
            if success:
                results = self.run_integration_tests(test_suite)

            # Phase 4: Collect logs
            logs = self.collect_logs()

        finally:
            # Phase 5: Cleanup
            self.stop_test_environment()

        # Phase 6: Generate report
        report_file = self.generate_report(results, logs)

        final_status = "passed" if success and results.get("overall_status") == "passed" else "failed"

        summary = {
            "status": final_status,
            "test_run_id": self.test_run_id,
            "report_file": report_file,
            "test_results": results,
            "logs_collected": list(logs.keys())
        }

        logger.info(f"🏁 Test suite completed with status: {final_status}")
        return summary


def main():
    parser = argparse.ArgumentParser(description="Docker-based Test Runner for ESP32 BPM Detector")
    parser.add_argument(
        "--suite", "-s",
        default="all",
        choices=["all", "hardware_emulation", "docker_integration"],
        help="Test suite to run"
    )
    parser.add_argument(
        "--project-dir",
        default=None,
        help="Project directory (defaults to current directory)"
    )
    parser.add_argument(
        "--keep-containers",
        action="store_true",
        help="Keep containers running after tests (for debugging)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    runner = DockerTestRunner(args.project_dir)
    results = runner.run_full_test_suite(args.suite)

    # Print summary
    print("\n" + "="*60)
    print("TEST SUITE SUMMARY")
    print("="*60)
    print(f"Status: {results['status'].upper()}")
    print(f"Test Run ID: {results['test_run_id']}")
    print(f"Report File: {results['report_file']}")
    print(f"Tests Run: {len(results.get('test_results', {}).get('tests', {}))}")
    print(f"Logs Collected: {', '.join(results['logs_collected'])}")
    print("="*60)

    # Exit with appropriate code
    sys.exit(0 if results["status"] == "passed" else 1)


if __name__ == "__main__":
    main()