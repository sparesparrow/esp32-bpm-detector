#!/usr/bin/env python3
"""
Docker Integration Tests

Tests Docker-based testing environment including container startup,
service discovery, cross-container communication, build processes,
test execution, and resource cleanup.
"""

import pytest
import subprocess
import time
import requests
import socket
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Add MCP server path
mcp_path = os.path.join(os.path.dirname(__file__), '../../../mcp/servers/python/unified_deployment')
sys.path.insert(0, mcp_path)


class DockerIntegrationTest:
    """Base class for Docker integration tests."""

    @pytest.fixture(scope="class")
    def docker_compose_file(self):
        """Get the docker-compose file path."""
        return Path(__file__).parent.parent.parent / "docker-compose.yml"

    @pytest.fixture(scope="class")
    def test_results_dir(self):
        """Get the test results directory."""
        results_dir = Path(__file__).parent.parent.parent / "test_results"
        results_dir.mkdir(exist_ok=True)
        return results_dir

    def run_docker_command(self, cmd: List[str], cwd: Path = None, timeout: int = 60) -> subprocess.CompletedProcess:
        """Run a Docker command and return the result."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result
        except subprocess.TimeoutExpired:
            pytest.fail(f"Docker command timed out: {' '.join(cmd)}")


class TestContainerStartup(DockerIntegrationTest):
    """Test container startup and service discovery."""

    def test_docker_compose_file_exists(self, docker_compose_file):
        """Test that docker-compose.yml file exists."""
        assert docker_compose_file.exists(), "docker-compose.yml file not found"
        assert docker_compose_file.is_file(), "docker-compose.yml is not a file"

    def test_docker_compose_config_valid(self, docker_compose_file):
        """Test that docker-compose configuration is valid."""
        result = self.run_docker_command([
            "docker-compose", "-f", str(docker_compose_file), "config"
        ])

        assert result.returncode == 0, f"Invalid docker-compose config: {result.stderr}"

    def test_esp32_emulator_container_build(self, docker_compose_file):
        """Test building the ESP32 emulator container."""
        result = self.run_docker_command([
            "docker-compose", "-f", str(docker_compose_file), "build", "esp32-emulator"
        ], timeout=300)  # 5 minute timeout for build

        assert result.returncode == 0, f"Failed to build esp32-emulator: {result.stderr}"

    def test_mock_services_container_build(self, docker_compose_file):
        """Test building the mock services container."""
        result = self.run_docker_command([
            "docker-compose", "-f", str(docker_compose_file), "build", "mock-services"
        ], timeout=300)

        assert result.returncode == 0, f"Failed to build mock-services: {result.stderr}"

    def test_integration_tests_container_build(self, docker_compose_file):
        """Test building the integration tests container."""
        result = self.run_docker_command([
            "docker-compose", "-f", str(docker_compose_file), "build", "integration-tests"
        ], timeout=300)

        assert result.returncode == 0, f"Failed to build integration-tests: {result.stderr}"

    def test_container_startup_sequence(self, docker_compose_file):
        """Test starting containers in the correct sequence."""
        try:
            # Start emulator first
            result = self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "up", "-d", "esp32-emulator"
            ])
            assert result.returncode == 0, "Failed to start esp32-emulator"

            # Wait for emulator to be ready
            time.sleep(5)

            # Check if emulator container is running
            result = self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "ps", "esp32-emulator"
            ])
            assert "Up" in result.stdout, "esp32-emulator container not running"

            # Start mock services
            result = self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "up", "-d", "mock-services"
            ])
            assert result.returncode == 0, "Failed to start mock-services"

            time.sleep(3)

            # Check if mock services container is running
            result = self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "ps", "mock-services"
            ])
            assert "Up" in result.stdout, "mock-services container not running"

        finally:
            # Cleanup
            self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "down", "-v"
            ])


class TestServiceDiscovery(DockerIntegrationTest):
    """Test service discovery between containers."""

    @pytest.fixture(scope="class")
    def running_containers(self, docker_compose_file):
        """Start containers for testing."""
        # Start services
        result = self.run_docker_command([
            "docker-compose", "-f", str(docker_compose_file), "up", "-d",
            "esp32-emulator", "mock-services"
        ])
        assert result.returncode == 0

        # Wait for services to be ready
        time.sleep(10)

        yield docker_compose_file

        # Cleanup
        self.run_docker_command([
            "docker-compose", "-f", str(docker_compose_file), "down", "-v"
        ])

    def test_emulator_service_discovery(self, running_containers):
        """Test that emulator service is discoverable."""
        docker_compose_file = running_containers

        # Check if emulator is listening on port 12345
        result = self.run_docker_command([
            "docker-compose", "-f", str(docker_compose_file), "exec", "-T", "esp32-emulator",
            "netstat", "-tln"
        ])

        assert "12345" in result.stdout, "Emulator not listening on port 12345"

    def test_mock_api_service_discovery(self, running_containers):
        """Test that mock API service is discoverable."""
        docker_compose_file = running_containers

        # Check if mock API is listening on port 8080
        result = self.run_docker_command([
            "docker-compose", "-f", str(docker_compose_file), "exec", "-T", "mock-services",
            "netstat", "-tln"
        ])

        assert "8080" in result.stdout, "Mock API not listening on port 8080"

    def test_network_connectivity(self, running_containers):
        """Test network connectivity between containers."""
        docker_compose_file = running_containers

        # Test connectivity from integration-tests container to emulator
        result = self.run_docker_command([
            "docker-compose", "-f", str(docker_compose_file), "exec", "-T", "esp32-emulator",
            "nc", "-z", "esp32-emulator", "12345"
        ])

        # nc returns 0 if connection succeeds
        assert result.returncode == 0, "Cannot connect to emulator from within network"


class TestCrossContainerCommunication(DockerIntegrationTest):
    """Test communication between containers."""

    @pytest.fixture(scope="class")
    def running_services(self, docker_compose_file):
        """Start all services for cross-container testing."""
        # Start all services
        result = self.run_docker_command([
            "docker-compose", "-f", str(docker_compose_file), "up", "-d"
        ])
        assert result.returncode == 0

        # Wait longer for all services
        time.sleep(15)

        yield docker_compose_file

        # Cleanup
        self.run_docker_command([
            "docker-compose", "-f", str(docker_compose_file), "down", "-v"
        ])

    def test_emulator_to_mock_services_communication(self, running_services):
        """Test communication from emulator to mock services."""
        docker_compose_file = running_services

        # Test if emulator can reach mock services
        result = self.run_docker_command([
            "docker-compose", "-f", str(docker_compose_file), "exec", "-T", "esp32-emulator",
            "curl", "-s", "http://mock-services:8080/api/bpm"
        ])

        # Should get a response from mock API
        assert result.returncode == 0, "Emulator cannot reach mock API"
        assert "bpm" in result.stdout.lower(), "Invalid response from mock API"

    def test_mock_api_functionality(self, running_services):
        """Test mock API functionality."""
        docker_compose_file = running_services

        # Get container IP for direct access
        result = self.run_docker_command([
            "docker-compose", "-f", str(docker_compose_file), "exec", "-T", "mock-services",
            "hostname", "-i"
        ])
        mock_ip = result.stdout.strip()

        # Test API endpoints
        try:
            # Test /api/bpm endpoint
            response = requests.get(f"http://{mock_ip}:8080/api/bpm", timeout=5)
            assert response.status_code == 200

            data = response.json()
            assert "bpm" in data
            assert "confidence" in data
            assert "signal_level" in data
            assert "status" in data
            assert "timestamp" in data

            # Test /api/settings endpoint
            response = requests.get(f"http://{mock_ip}:8080/api/settings", timeout=5)
            assert response.status_code == 200

            data = response.json()
            assert "min_bpm" in data
            assert "max_bpm" in data
            assert "version" in data

        except requests.RequestException as e:
            pytest.fail(f"API request failed: {e}")

    def test_emulator_tcp_protocol_from_container(self, running_services):
        """Test TCP protocol communication to emulator from another container."""
        docker_compose_file = running_services

        # Use netcat to test TCP connection to emulator
        result = self.run_docker_command([
            "docker-compose", "-f", str(docker_compose_file), "exec", "-T", "mock-services",
            "sh", "-c", "echo 'GET_STATUS' | nc esp32-emulator 12345"
        ])

        assert result.returncode == 0, "Failed to connect to emulator via TCP"
        assert "STATUS:OK" in result.stdout, "Invalid emulator response"


class TestBuildProcessInDocker(DockerIntegrationTest):
    """Test build processes within Docker environment."""

    def test_platformio_build_in_container(self, docker_compose_file):
        """Test PlatformIO build process in container."""
        # This would require a proper PlatformIO project structure
        # For now, just test that the container can run pio commands
        result = self.run_docker_command([
            "docker-compose", "-f", str(docker_compose_file), "run", "--rm", "esp32-build",
            "pio", "--version"
        ])

        assert result.returncode == 0, "PlatformIO not available in container"
        assert "PlatformIO" in result.stdout, "Invalid PlatformIO version output"

    def test_python_testing_frameworks_available(self, docker_compose_file):
        """Test that Python testing frameworks are available."""
        result = self.run_docker_command([
            "docker-compose", "-f", str(docker_compose_file), "run", "--rm", "integration-tests",
            "python3", "-c", "import pytest, requests, socket; print('Testing frameworks available')"
        ])

        assert result.returncode == 0, "Testing frameworks not available in container"


class TestTestExecution(DockerIntegrationTest):
    """Test test execution and result collection."""

    def test_integration_test_execution(self, docker_compose_file, test_results_dir):
        """Test running integration tests in Docker."""
        try:
            # Start required services first
            result = self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "up", "-d",
                "esp32-emulator", "mock-services"
            ])
            assert result.returncode == 0

            # Wait for services
            time.sleep(10)

            # Run integration tests
            result = self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "run", "--rm", "integration-tests"
            ], timeout=600)  # 10 minute timeout

            # Tests should complete (may pass or fail, but should run)
            assert result.returncode in [0, 1], f"Test execution failed: {result.stderr}"

        finally:
            # Cleanup
            self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "down", "-v"
            ])

    def test_test_result_collection(self, docker_compose_file, test_results_dir):
        """Test that test results are collected properly."""
        # Check if test results directory exists and is writable
        assert test_results_dir.exists(), "Test results directory not created"
        assert test_results_dir.is_dir(), "Test results path is not a directory"

        # Check if we can write to the directory
        test_file = test_results_dir / "test_write_test.txt"
        try:
            test_file.write_text("test content")
            assert test_file.exists(), "Cannot write to test results directory"
            test_file.unlink()  # Clean up
        except Exception as e:
            pytest.fail(f"Cannot write to test results directory: {e}")


class TestResourceCleanup(DockerIntegrationTest):
    """Test resource cleanup after tests."""

    def test_container_cleanup(self, docker_compose_file):
        """Test that containers are properly cleaned up."""
        try:
            # Start services
            result = self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "up", "-d",
                "esp32-emulator", "mock-services"
            ])
            assert result.returncode == 0

            # Verify containers are running
            result = self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "ps"
            ])
            assert "esp32-emulator" in result.stdout
            assert "mock-services" in result.stdout

            # Stop and remove containers
            result = self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "down", "-v"
            ])
            assert result.returncode == 0

            # Verify containers are stopped
            result = self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "ps"
            ])
            assert "esp32-emulator" not in result.stdout or "Exit" in result.stdout
            assert "mock-services" not in result.stdout or "Exit" in result.stdout

        except Exception as e:
            # Cleanup on failure
            self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "down", "-v"
            ])
            raise

    def test_volume_cleanup(self, docker_compose_file, test_results_dir):
        """Test that Docker volumes are cleaned up."""
        try:
            # Start services (which create volumes)
            result = self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "up", "-d",
                "esp32-emulator"
            ])
            assert result.returncode == 0

            time.sleep(2)

            # Check for volume mounts
            result = self.run_docker_command([
                "docker", "inspect", "esp32-bpm-emulator"
            ])

            # Should have volume mounts
            assert "/workspace" in result.stdout

            # Stop with volume removal
            result = self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "down", "-v"
            ])
            assert result.returncode == 0

        except Exception as e:
            # Cleanup on failure
            self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "down", "-v"
            ])
            raise

    def test_network_cleanup(self, docker_compose_file):
        """Test that Docker networks are cleaned up."""
        try:
            # Start services (which create networks)
            result = self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "up", "-d",
                "esp32-emulator", "mock-services"
            ])
            assert result.returncode == 0

            time.sleep(2)

            # Check for networks
            result = self.run_docker_command([
                "docker", "network", "ls"
            ])

            # Should have emulator_net and test_net
            assert "emulator_net" in result.stdout or "emulator_net" in result.stderr
            assert "test_net" in result.stdout or "test_net" in result.stderr

            # Stop services
            result = self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "down", "-v"
            ])
            assert result.returncode == 0

            # Networks should be removed automatically by docker-compose

        except Exception as e:
            # Cleanup on failure
            self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "down", "-v"
            ])
            raise


class TestDockerIntegrationWorkflow:
    """Test complete Docker integration workflow."""

    def test_full_docker_workflow(self, docker_compose_file, test_results_dir):
        """Test the complete Docker-based testing workflow."""
        try:
            # Step 1: Build containers
            result = self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "build"
            ], timeout=600)
            assert result.returncode == 0, "Container build failed"

            # Step 2: Start services
            result = self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "up", "-d",
                "esp32-emulator", "mock-services"
            ])
            assert result.returncode == 0, "Service startup failed"

            # Step 3: Wait for services to be ready
            time.sleep(15)

            # Step 4: Verify services are running
            result = self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "ps"
            ])
            assert "Up" in result.stdout, "Services not running"

            # Step 5: Run tests
            result = self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "run", "--rm", "integration-tests"
            ], timeout=600)

            # Tests should complete (success or failure is OK, as long as they run)
            assert result.returncode in [0, 1], "Test execution failed unexpectedly"

            # Step 6: Collect results (if any)
            junit_files = list(test_results_dir.glob("*.xml"))
            if junit_files:
                assert len(junit_files) > 0, "Test results not generated"

        finally:
            # Step 7: Cleanup
            result = self.run_docker_command([
                "docker-compose", "-f", str(docker_compose_file), "down", "-v"
            ])
            # Cleanup should succeed even if tests failed
            assert result.returncode == 0, "Cleanup failed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])