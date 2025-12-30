#!/usr/bin/env python3
"""
Start hardware emulator for Docker container.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, "/workspace")

from mcp.servers.python.unified_deployment.unified_deployment_mcp_server import HardwareEmulator
import time

def main():
    print("🧪 Starting ESP32 Hardware Emulator...")

    emulator = HardwareEmulator(host="0.0.0.0", port=12345, device_type="esp32")
    if emulator.start():
        print("✅ Hardware emulator started on port 12345")
        try:
            while emulator.running:
                time.sleep(1)
        except KeyboardInterrupt:
            emulator.stop()
    else:
        print("❌ Failed to start hardware emulator")
        sys.exit(1)

if __name__ == "__main__":
    main()