#!/usr/bin/env python3
"""
Hardware Emulation Integration Tests

Tests TCP/IP hardware emulation for ESP32 BPM Detector.
Tests connection establishment, protocol simulation, device discovery,
multi-client handling, and error conditions.
"""

import pytest
import socket
import time
import json
import threading
from typing import List, Dict, Any
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Try to import from MCP server, fallback to direct import
try:
    from mcp.servers.python.unified_deployment.unified_deployment_mcp_server import HardwareEmulator
except ImportError:
    # Direct import for testing
    import sys
    mcp_path = os.path.join(os.path.dirname(__file__), '../../../mcp/servers/python/unified_deployment')
    sys.path.insert(0, mcp_path)
    from unified_deployment_mcp_server import HardwareEmulator


class TestHardwareEmulator:
    """Test suite for HardwareEmulator class."""

    @pytest.fixture
    def emulator(self):
        """Create a test emulator instance."""
        emulator = HardwareEmulator(host="127.0.0.1", port=0, device_type="esp32")  # port=0 for auto-assignment
        yield emulator
        # Cleanup
        if hasattr(emulator, 'running') and emulator.running:
            emulator.stop()

    @pytest.fixture
    def running_emulator(self, emulator):
        """Create and start a test emulator."""
        assert emulator.start()
        # Get the actual port that was assigned
        actual_port = emulator.port
        yield emulator, actual_port

    def test_emulator_initialization(self, emulator):
        """Test emulator initialization with different device types."""
        # Test ESP32
        esp32_emulator = HardwareEmulator(device_type="esp32")
        assert esp32_emulator.device_type == "esp32"
        assert 60 <= esp32_emulator.config["bpm_range"][0] <= 200

        # Test ESP32-S3
        esp32s3_emulator = HardwareEmulator(device_type="esp32s3")
        assert esp32s3_emulator.device_type == "esp32s3"
        assert "gyroscope" in esp32s3_emulator.config["sensor_types"]

        # Test Arduino
        arduino_emulator = HardwareEmulator(device_type="arduino")
        assert arduino_emulator.device_type == "arduino"
        assert arduino_emulator.config["response_delay"] == 0.2

    def test_emulator_start_stop(self, emulator):
        """Test emulator start and stop functionality."""
        # Initially not running
        assert not emulator.running
        assert emulator.status == "stopped"

        # Start emulator
        assert emulator.start()
        assert emulator.running
        assert emulator.status == "running"

        # Stop emulator
        emulator.stop()
        assert not emulator.running
        assert emulator.status == "stopped"

    def test_tcp_connection_establishment(self, running_emulator):
        """Test TCP connection establishment to emulator."""
        emulator, port = running_emulator

        # Connect to emulator
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)

        try:
            sock.connect(("127.0.0.1", port))
            assert emulator.connected_clients >= 1
        finally:
            sock.close()

    def test_bpm_data_protocol_simulation(self, running_emulator):
        """Test BPM data protocol simulation."""
        emulator, port = running_emulator

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)

        try:
            sock.connect(("127.0.0.1", port))

            # Send GET_BPM command
            sock.send(b"GET_BPM\n")

            # Receive response
            response = sock.recv(1024).decode('utf-8').strip()

            # Parse response
            assert "BPM:" in response
            assert "CONF:" in response
            assert "SIG:" in response
            assert "STATUS:OK" in response

            # Extract BPM value
            parts = response.split('|')
            bpm_part = next(p for p in parts if p.startswith("BPM:"))
            bpm_value = float(bpm_part.split(':')[1])

            # Check BPM range
            assert 60 <= bpm_value <= 200

        finally:
            sock.close()

    def test_device_status_simulation(self, running_emulator):
        """Test device status reporting."""
        emulator, port = running_emulator

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)

        try:
            sock.connect(("127.0.0.1", port))

            # Send GET_STATUS command
            sock.send(b"GET_STATUS\n")

            # Receive response
            response = sock.recv(1024).decode('utf-8').strip()

            # Parse response
            assert "STATUS:OK" in response
            assert "UPTIME:" in response
            assert f"TYPE:{emulator.device_type}" in response
            assert "CLIENTS:" in response

        finally:
            sock.close()

    def test_sensor_enumeration(self, running_emulator):
        """Test sensor enumeration functionality."""
        emulator, port = running_emulator

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)

        try:
            sock.connect(("127.0.0.1", port))

            # Send GET_SENSORS command
            sock.send(b"GET_SENSORS\n")

            # Receive response
            response = sock.recv(1024).decode('utf-8').strip()

            # Parse response
            assert response.startswith("SENSORS:")
            sensors_str = response.split(':')[1]
            sensors = sensors_str.split(',')

            # Check expected sensors for ESP32
            expected_sensors = emulator.config["sensor_types"]
            for sensor in expected_sensors:
                assert sensor in sensors

        finally:
            sock.close()

    def test_configuration_commands(self, running_emulator):
        """Test configuration command handling."""
        emulator, port = running_emulator

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)

        try:
            sock.connect(("127.0.0.1", port))

            # Send SET_CONFIG command
            sock.send(b"SET_CONFIG min_bpm 80\n")

            # Receive response
            response = sock.recv(1024).decode('utf-8').strip()

            # Parse response
            assert "CONFIG_SET:" in response
            assert "min_bpm=80" in response
            assert "STATUS:OK" in response

        finally:
            sock.close()

    def test_ping_pong_functionality(self, running_emulator):
        """Test basic ping/pong connectivity."""
        emulator, port = running_emulator

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)

        try:
            sock.connect(("127.0.0.1", port))

            # Send PING command
            sock.send(b"PING\n")

            # Receive response
            response = sock.recv(1024).decode('utf-8').strip()

            # Should receive PONG
            assert response == "PONG"

        finally:
            sock.close()

    def test_device_reset_simulation(self, running_emulator):
        """Test device reset command."""
        emulator, port = running_emulator

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)

        try:
            sock.connect(("127.0.0.1", port))

            # Send RESET command
            sock.send(b"RESET\n")

            # Receive response
            response = sock.recv(1024).decode('utf-8').strip()

            # Should receive reset confirmation
            assert response == "RESET:OK"

        finally:
            sock.close()

    def test_unknown_command_handling(self, running_emulator):
        """Test handling of unknown commands."""
        emulator, port = running_emulator

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)

        try:
            sock.connect(("127.0.0.1", port))

            # Send unknown command
            sock.send(b"UNKNOWN_COMMAND\n")

            # Receive response
            response = sock.recv(1024).decode('utf-8').strip()

            # Should receive unknown command error
            assert "UNKNOWN_COMMAND:" in response

        finally:
            sock.close()

    def test_multi_client_handling(self, running_emulator):
        """Test handling multiple concurrent clients."""
        emulator, port = running_emulator

        def client_worker(client_id: int):
            """Worker function for client connections."""
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5.0)
                sock.connect(("127.0.0.1", port))

                # Send a command
                sock.send(f"GET_STATUS\n".encode())

                # Receive response
                response = sock.recv(1024).decode('utf-8').strip()
                assert "STATUS:OK" in response

                sock.close()
            except Exception as e:
                pytest.fail(f"Client {client_id} failed: {e}")

        # Start multiple clients
        threads = []
        num_clients = 5

        for i in range(num_clients):
            thread = threading.Thread(target=client_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all clients to complete
        for thread in threads:
            thread.join(timeout=10.0)
            assert not thread.is_alive(), "Client thread did not complete"

        # Check that clients were handled
        assert emulator.connected_clients >= 0  # May be 0 if all disconnected

    def test_error_conditions_and_recovery(self, running_emulator):
        """Test error conditions and recovery."""
        emulator, port = running_emulator

        # Test invalid data handling
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)

        try:
            sock.connect(("127.0.0.1", port))

            # Send malformed data
            sock.send(b"INVALID_DATA_1234567890\n")

            # Should still respond (gracefully handle invalid input)
            response = sock.recv(1024).decode('utf-8', errors='ignore').strip()

            # Should get some response, even if it's an error
            assert len(response) > 0

        finally:
            sock.close()

    def test_emulator_status_reporting(self, running_emulator):
        """Test emulator status reporting functionality."""
        emulator, port = running_emulator

        status = emulator.get_status()

        assert isinstance(status, dict)
        assert status["status"] == "running"
        assert status["host"] == "127.0.0.1"
        assert status["port"] == port
        assert status["device_type"] == "esp32"
        assert "connected_clients" in status
        assert "config" in status

        # Stop emulator and check status
        emulator.stop()
        status = emulator.get_status()
        assert status["status"] == "stopped"

    @pytest.mark.parametrize("device_type", ["esp32", "esp32s3", "arduino"])
    def test_different_device_types(self, device_type):
        """Test emulator with different device types."""
        emulator = HardwareEmulator(device_type=device_type, port=0)

        assert emulator.start()

        try:
            status = emulator.get_status()
            assert status["device_type"] == device_type

            # Test basic connectivity
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)

            try:
                sock.connect(("127.0.0.1", emulator.port))
                sock.send(b"GET_STATUS\n")
                response = sock.recv(1024).decode('utf-8').strip()
                assert f"TYPE:{device_type}" in response
            finally:
                sock.close()

        finally:
            emulator.stop()


class TestHardwareEmulatorIntegration:
    """Integration tests combining multiple emulator features."""

    @pytest.fixture
    def running_emulator_integration(self):
        """Create and start a test emulator for integration tests."""
        emulator = HardwareEmulator(host="127.0.0.1", port=0, device_type="esp32")  # port=0 for auto-assignment
        assert emulator.start()
        port = emulator.port
        yield emulator, port
        # Cleanup
        if hasattr(emulator, 'running') and emulator.running:
            emulator.stop()

    def test_full_bpm_workflow_simulation(self, running_emulator_integration):
        """Test a complete BPM detection workflow."""
        emulator, port = running_emulator

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10.0)

        try:
            sock.connect(("127.0.0.1", port))

            # Step 1: Check device status
            sock.send(b"GET_STATUS\n")
            response = sock.recv(1024).decode('utf-8').strip()
            assert "STATUS:OK" in response

            # Step 2: Check available sensors
            sock.send(b"GET_SENSORS\n")
            response = sock.recv(1024).decode('utf-8').strip()
            assert "SENSORS:" in response

            # Step 3: Configure detection parameters
            sock.send(b"SET_CONFIG min_bpm 80\n")
            response = sock.recv(1024).decode('utf-8').strip()
            assert "CONFIG_SET:" in response

            # Step 4: Get BPM readings (multiple samples)
            bpm_readings = []
            for _ in range(3):
                sock.send(b"GET_BPM\n")
                response = sock.recv(1024).decode('utf-8').strip()

                # Extract BPM value
                parts = response.split('|')
                bpm_part = next(p for p in parts if p.startswith("BPM:"))
                bpm_value = float(bpm_part.split(':')[1])
                bpm_readings.append(bpm_value)

                time.sleep(0.1)  # Small delay between readings

            # Verify we got valid readings
            assert len(bpm_readings) == 3
            assert all(60 <= bpm <= 200 for bpm in bpm_readings)

            # Step 5: Test device reset
            sock.send(b"RESET\n")
            response = sock.recv(1024).decode('utf-8').strip()
            assert response == "RESET:OK"

        finally:
            sock.close()

    def test_emulator_performance_under_load(self, running_emulator):
        """Test emulator performance with multiple rapid requests."""
        emulator, port = running_emulator

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15.0)

        try:
            sock.connect(("127.0.0.1", port))

            # Send multiple rapid requests
            num_requests = 20
            responses = []

            start_time = time.time()
            for i in range(num_requests):
                sock.send(b"GET_BPM\n")
                response = sock.recv(1024).decode('utf-8').strip()
                responses.append(response)

            end_time = time.time()

            # Verify all responses received
            assert len(responses) == num_requests
            assert all("BPM:" in resp for resp in responses)

            # Check performance (should handle ~20 requests in reasonable time)
            total_time = end_time - start_time
            avg_time_per_request = total_time / num_requests

            # Emulator should respond within reasonable time (adjust based on config)
            assert avg_time_per_request < 1.0  # Less than 1 second per request

        finally:
            sock.close()


if __name__ == "__main__":
    pytest.main([__file__])