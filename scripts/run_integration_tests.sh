#!/bin/bash
set -e

echo "🧪 Running Integration Tests..."

# Wait for emulator to be ready
echo "Waiting for emulator..."
timeout 30 bash -c 'until nc -z esp32-emulator 12345; do sleep 1; done'
echo "✅ Emulator ready"

# Run hardware emulation tests
python3 -m pytest tests/integration/test_hardware_emulation.py -v --tb=short --junitxml=/workspace/test_results/integration-tests.xml

# Run Docker integration tests
python3 -m pytest tests/integration/test_docker_integration.py -v --tb=short --junitxml=/workspace/test_results/docker-integration-tests.xml

echo "✅ All integration tests completed"