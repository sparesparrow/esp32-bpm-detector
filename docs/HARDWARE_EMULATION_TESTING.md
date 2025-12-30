# Hardware Emulation and Docker-based Testing

This document provides comprehensive guidance for testing the ESP32 BPM Detector using hardware emulation and Docker-based environments.

## Table of Contents

- [Overview](#overview)
- [Hardware Emulation](#hardware-emulation)
- [Docker-based Testing](#docker-based-testing)
- [MCP Integration](#mcp-integration)
- [Test Results and Reporting](#test-results-and-reporting)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

The ESP32 BPM Detector now supports two advanced testing methodologies:

1. **Hardware Emulation**: TCP/IP-based simulation of embedded hardware for testing without physical devices
2. **Docker-based Testing**: Containerized testing environment for automated, isolated test execution

These approaches enable:
- Development and testing without physical hardware
- Automated CI/CD pipelines
- Cross-platform testing consistency
- Multi-device scenario simulation
- Rapid prototyping and iteration

## Hardware Emulation

### Architecture

The hardware emulator provides a TCP/IP server that simulates ESP32 and Arduino devices with realistic behavior:

```
┌─────────────────┐    TCP/IP    ┌──────────────────┐
│   Test Client   │◄────────────►│ Hardware Emulator│
│                 │              │ - ESP32 Logic    │
│ - Python Tests  │              │ - Sensor Data    │
│ - MCP Tools     │              │ - Device Status  │
│ - Custom Apps   │              │ - Error Simulation│
└─────────────────┘              └──────────────────┘
```

### Supported Device Types

| Device Type | BPM Range | Sensors | Response Delay | Error Rate |
|-------------|-----------|---------|----------------|------------|
| ESP32      | 60-200    | Microphone, Accelerometer, Temperature | 100ms | 2% |
| ESP32-S3   | 60-200    | Microphone, Accelerometer, Temperature, Gyroscope | 80ms | 1% |
| Arduino    | 60-180    | Microphone | 200ms | 5% |

### Protocol Specification

The emulator uses a simple text-based protocol over TCP sockets:

#### Commands

**GET_BPM**
- **Description**: Get current BPM detection data
- **Response**: `BPM:128.5|CONF:0.87|SIG:0.72|STATUS:OK`
- **Fields**:
  - `BPM`: Beats per minute (float)
  - `CONF`: Confidence level 0.0-1.0 (float)
  - `SIG`: Signal strength 0.0-1.0 (float)
  - `STATUS`: Detection status (string)

**GET_STATUS**
- **Description**: Get device status information
- **Response**: `STATUS:OK|UPTIME:3600|TYPE:esp32|CLIENTS:1`
- **Fields**:
  - `STATUS`: Device status
  - `UPTIME`: Seconds since startup (int)
  - `TYPE`: Device type (string)
  - `CLIENTS`: Connected clients (int)

**GET_SENSORS**
- **Description**: List available sensors
- **Response**: `SENSORS:microphone,accelerometer,temperature`

**SET_CONFIG**
- **Description**: Configure device parameters
- **Usage**: `SET_CONFIG min_bpm 80`
- **Response**: `CONFIG_SET:min_bpm=80|STATUS:OK`

**PING**
- **Description**: Connectivity test
- **Response**: `PONG`

**RESET**
- **Description**: Simulate device reset
- **Response**: `RESET:OK`

### Starting the Emulator

#### Via MCP Tools

```python
# Start emulator
result = await unified_deployment.start_hardware_emulator(
    host="127.0.0.1",
    port=12345,
    device_type="esp32"
)

# Check status
status = await unified_deployment.get_emulator_status()

# Send commands
response = await unified_deployment.send_emulator_command("GET_BPM")
```

#### Via Direct Python

```python
from mcp.servers.python.unified_deployment.unified_deployment_mcp_server import HardwareEmulator

emulator = HardwareEmulator(host="127.0.0.1", port=12345, device_type="esp32")
emulator.start()

# Use emulator...

emulator.stop()
```

#### Via Docker

```bash
# Start emulator in container
docker-compose up -d esp32-emulator

# Check logs
docker-compose logs esp32-emulator
```

### Testing with Emulator

#### Basic Connectivity Test

```python
import socket

def test_emulator_connection():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 12345))

    # Test ping
    sock.send(b"PING\n")
    response = sock.recv(1024).decode().strip()
    assert response == "PONG"

    # Test status
    sock.send(b"GET_STATUS\n")
    response = sock.recv(1024).decode().strip()
    assert "STATUS:OK" in response

    sock.close()
```

#### BPM Detection Simulation

```python
def test_bpm_detection():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 12345))

    # Get multiple BPM readings
    readings = []
    for _ in range(10):
        sock.send(b"GET_BPM\n")
        response = sock.recv(1024).decode().strip()

        # Parse response
        parts = dict(item.split(':') for item in response.split('|'))
        bpm = float(parts['BPM'])
        confidence = float(parts['CONF'])

        readings.append((bpm, confidence))

    # Validate readings
    assert all(60 <= bpm <= 200 for bpm, _ in readings)
    assert all(0.0 <= conf <= 1.0 for _, conf in readings)

    sock.close()
```

## Docker-based Testing

### Architecture

The Docker testing environment consists of multiple containers working together:

```
┌─────────────────┐    emulator_net    ┌──────────────────┐
│  esp32-emulator │◄──────────────────►│ integration-    │
│  (port 12345)   │                    │ tests            │
└─────────────────┘                    └──────────────────┘
         │                                      │
         └────────────── test_net ──────────────┘
                        │
               ┌──────────────────┐
               │  mock-services   │
               │  API (8080)      │
               │  WS (8000)       │
               └──────────────────┘
```

### Container Specifications

#### esp32-emulator
- **Purpose**: Hardware emulation server
- **Base Image**: Custom test image with Python
- **Ports**: 12345 (TCP)
- **Networks**: emulator_net
- **Environment**: Emulator configuration

#### mock-services
- **Purpose**: Mock ESP32 API and WebSocket servers
- **Base Image**: Custom test image
- **Ports**: 8080 (HTTP API), 8000 (WebSocket)
- **Networks**: test_net
- **Simulates**: REST API responses, real-time data streaming

#### integration-tests
- **Purpose**: Test execution container
- **Base Image**: Custom test image with test frameworks
- **Networks**: emulator_net, test_net
- **Mounts**: Source code, test results, logs
- **Runs**: pytest suites against emulated environment

### Running Docker Tests

#### Full Test Suite

```bash
# Run complete test suite
python3 scripts/docker_test_runner.py --suite all

# Or via MCP
unified-deployment.run_docker_tests test_suite="all"
```

#### Individual Test Types

```bash
# Hardware emulation tests only
python3 scripts/docker_test_runner.py --suite hardware_emulation

# Docker integration tests only
python3 scripts/docker_test_runner.py --suite docker_integration
```

#### Custom Configuration

```bash
# With specific project directory
python3 scripts/docker_test_runner.py \
    --suite all \
    --project-dir /path/to/project

# Generate detailed report
python3 scripts/docker_test_runner.py \
    --suite all \
    --report custom_report.json
```

### Docker Test Results

#### Result Files

```
test_results/
├── test_report_20241230_143022.json    # Comprehensive report
├── integration-tests.xml               # JUnit XML (hardware emulation)
└── docker-integration-tests.xml        # JUnit XML (Docker tests)

logs/
├── esp32-emulator_20241230_143022.log   # Emulator logs
├── integration-tests_20241230_143022.log # Test execution logs
└── mock-services_20241230_143022.log    # Mock service logs
```

#### Report Structure

```json
{
  "test_run_id": "20241230_143022",
  "timestamp": 1735583422.123,
  "platform": "Linux x86_64",
  "results": {
    "hardware_emulation": {
      "status": "passed",
      "passed": 15,
      "failed": 0,
      "total": 15
    },
    "docker_integration": {
      "status": "passed",
      "passed": 8,
      "failed": 0,
      "total": 8
    }
  },
  "container_logs": {
    "esp32-emulator": "...",
    "mock-services": "...",
    "integration-tests": "..."
  }
}
```

## MCP Integration

### Available Tools

#### Hardware Emulation Tools

- `start_hardware_emulator(host, port, device_type)` - Start emulator server
- `stop_hardware_emulator()` - Stop emulator server
- `get_emulator_status()` - Get current emulator state
- `send_emulator_command(command, data)` - Send commands to emulator

#### Docker Testing Tools

- `run_docker_tests(test_suite, emulator_enabled)` - Run Docker test suite
- `build_test_containers()` - Build test container images
- `start_test_environment()` - Start test services
- `stop_test_environment()` - Stop and cleanup test environment
- `get_test_results(test_run_id)` - Retrieve test results

### Example MCP Workflow

```python
# Setup test environment
await unified_deployment.build_test_containers()
await unified_deployment.start_test_environment()

# Start hardware emulator
await unified_deployment.start_hardware_emulator(
    device_type="esp32",
    port=12345
)

# Run tests
test_results = await unified_deployment.run_docker_tests(
    test_suite="all",
    emulator_enabled=True
)

# Get detailed results
results = await unified_deployment.get_test_results()

# Cleanup
await unified_deployment.stop_test_environment()
await unified_deployment.stop_hardware_emulator()
```

## Test Results and Reporting

### Result Analysis

#### Test Status Interpretation

- **PASSED**: All tests in suite completed successfully
- **FAILED**: One or more tests failed with assertion errors
- **ERROR**: Test execution failed due to infrastructure issues
- **TIMEOUT**: Tests exceeded configured time limits

#### Performance Metrics

Monitor these key metrics from test reports:

- **Test Execution Time**: Total time for test suite completion
- **Emulator Response Time**: Average latency for emulator commands
- **Container Startup Time**: Time to initialize test environment
- **Resource Usage**: CPU, memory usage during tests

### Continuous Integration

#### GitHub Actions Example

```yaml
name: ESP32 BPM Detector Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Docker
      run: |
        sudo apt-get update
        sudo apt-get install -y docker.io docker-compose

    - name: Run Docker Tests
      run: |
        python3 scripts/docker_test_runner.py --suite all

    - name: Upload Test Results
      uses: actions/upload-artifact@v3
      with:
        name: test-results
        path: |
          test_results/
          logs/
```

#### Local CI Simulation

```bash
# Run tests with reporting
python3 scripts/docker_test_runner.py \
    --suite all \
    --report ci_report.json

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ All tests passed"
else
    echo "❌ Tests failed"
    cat ci_report.json
fi
```

## Troubleshooting

### Common Issues

#### Emulator Connection Refused

**Symptoms**: `ConnectionError: [Errno 111] Connection refused`

**Solutions**:
```bash
# Check if emulator is running
docker-compose ps esp32-emulator

# Check emulator logs
docker-compose logs esp32-emulator

# Verify port availability
netstat -tln | grep 12345

# Restart emulator
unified-deployment.stop_hardware_emulator
unified-deployment.start_hardware_emulator
```

#### Docker Container Failures

**Symptoms**: `docker-compose up` fails with container errors

**Solutions**:
```bash
# Clean up failed containers
docker-compose down -v

# Rebuild without cache
docker-compose build --no-cache

# Check system resources
docker system df

# Increase Docker resources if needed
```

#### Test Timeouts

**Symptoms**: Tests fail with timeout errors

**Solutions**:
```bash
# Check container logs
docker-compose logs integration-tests

# Monitor resource usage
docker stats

# Increase timeout values in test configuration
# Check for network latency between containers
```

#### Port Conflicts

**Symptoms**: `Port already in use` errors

**Solutions**:
```bash
# Find conflicting process
lsof -i :12345

# Use different ports
export HARDWARE_EMULATOR_PORT=12346

# Stop conflicting services
sudo systemctl stop conflicting-service
```

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
# Set environment variables
export LOG_LEVEL=DEBUG
export DOCKER_TEST_ENABLED=true

# Run with verbose output
python3 scripts/docker_test_runner.py --suite all
```

### Log Analysis

Key log files to examine:

- `logs/esp32-emulator_*.log` - Emulator startup and connection logs
- `logs/integration-tests_*.log` - Test execution details
- `logs/mock-services_*.log` - Mock service interactions
- `docker-compose logs` - Container orchestration logs

## Best Practices

### Development Workflow

1. **Local Testing First**: Run native tests before Docker tests
2. **Incremental Testing**: Test individual components before full suite
3. **Clean Environment**: Always cleanup between test runs
4. **Resource Monitoring**: Watch for resource constraints
5. **Log Analysis**: Regularly review logs for issues

### Test Organization

1. **Test Isolation**: Each test should be independent
2. **Realistic Scenarios**: Test with production-like data
3. **Error Conditions**: Include failure case testing
4. **Performance Baselines**: Establish expected performance metrics
5. **Cross-platform**: Test on different host systems

### CI/CD Integration

1. **Fast Feedback**: Run critical tests first
2. **Parallel Execution**: Use multiple runners when possible
3. **Artifact Collection**: Preserve test artifacts
4. **Notification**: Alert on test failures
5. **Trend Analysis**: Track test performance over time

### Maintenance

1. **Regular Updates**: Keep Docker images updated
2. **Dependency Checks**: Monitor for security vulnerabilities
3. **Performance Tuning**: Optimize resource usage
4. **Documentation**: Keep test documentation current
5. **Backup**: Preserve important test artifacts

---

## Quick Reference

### Start Full Test Environment
```bash
# Build and start everything
unified-deployment.build_test_containers
unified-deployment.start_test_environment
unified-deployment.start_hardware_emulator

# Run tests
unified-deployment.run_docker_tests

# Cleanup
unified-deployment.stop_test_environment
unified-deployment.stop_hardware_emulator
```

### Check System Status
```bash
# Emulator status
unified-deployment.get_emulator_status

# Test results
unified-deployment.get_test_results

# Container status
docker-compose ps
```

### Emergency Cleanup
```bash
# Force cleanup
docker-compose down -v --remove-orphans
docker system prune -f

# Reset emulator
unified-deployment.stop_hardware_emulator
```