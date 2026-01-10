#!/usr/bin/env python3
"""
ESP32 Serial Monitor for WiFi/BPM Detection
Monitors serial output and extracts connection status and IP address
"""

import asyncio
import re
import time
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("Please install pyserial: pip install pyserial")
    raise


@dataclass
class SerialMonitorResult:
    wifi_connected: bool = False
    esp32_ip: Optional[str] = None
    server_started: bool = False
    bpm_values: List[float] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    raw_log: str = ""
    duration: float = 0.0

    def is_success(self) -> bool:
        return self.wifi_connected and self.esp32_ip is not None and self.server_started


class SerialMonitor:
    """Monitor ESP32 serial output for WiFi connection status"""

    # Patterns to detect in serial output
    WIFI_CONNECTED_PATTERNS = [
        r"WiFi connected",
        r"WiFi connected successfully",
        r"Connected to WiFi",
    ]

    IP_ADDRESS_PATTERN = r"IP address:\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    SERVER_STARTED_PATTERN = r"HTTP server started"
    BPM_PATTERN = r"BPM[:\s]+(\d+\.?\d*)"
    ERROR_PATTERNS = [
        r"Error",
        r"FAILED",
        r"Exception",
        r"Guru Meditation",
        r"Backtrace:",
        r"assert failed",
    ]

    def __init__(self, port: str = "/dev/ttyACM0", baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate

    @staticmethod
    def find_esp32_port() -> Optional[str]:
        """Auto-detect ESP32 serial port"""
        esp32_vids = [0x303A, 0x10C4, 0x1A86]  # Common ESP32 USB VIDs

        for port in serial.tools.list_ports.comports():
            if port.vid in esp32_vids:
                return port.device

            # Also check for ACM ports on Linux
            if "ttyACM" in port.device or "ttyUSB" in port.device:
                return port.device

        return None

    def monitor_sync(self, duration: int = 30) -> SerialMonitorResult:
        """Synchronous version of monitor (for non-async contexts)"""
        result = SerialMonitorResult()
        start_time = time.time()

        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=1)
            ser.reset_input_buffer()

            while (time.time() - start_time) < duration:
                if ser.in_waiting:
                    try:
                        line = ser.readline().decode('utf-8', errors='replace')
                        result.raw_log += line
                        self._parse_line(line, result)

                        # Early exit if all criteria met
                        if result.is_success():
                            break

                    except Exception as e:
                        result.errors.append(f"Read error: {e}")

                time.sleep(0.05)

            ser.close()

        except serial.SerialException as e:
            result.errors.append(f"Serial error: {e}")

        result.duration = time.time() - start_time
        return result

    async def monitor(self, duration: int = 30) -> SerialMonitorResult:
        """Monitor serial port for specified duration (async version)"""
        result = SerialMonitorResult()
        start_time = asyncio.get_event_loop().time()

        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=0.1)
            ser.reset_input_buffer()

            while (asyncio.get_event_loop().time() - start_time) < duration:
                if ser.in_waiting:
                    try:
                        line = ser.readline().decode('utf-8', errors='replace')
                        result.raw_log += line
                        self._parse_line(line, result)

                        # Early exit if all criteria met
                        if result.is_success():
                            break

                    except Exception as e:
                        result.errors.append(f"Read error: {e}")

                await asyncio.sleep(0.05)

            ser.close()

        except serial.SerialException as e:
            result.errors.append(f"Serial error: {e}")

        result.duration = asyncio.get_event_loop().time() - start_time
        return result

    def _parse_line(self, line: str, result: SerialMonitorResult):
        """Parse a single line of serial output"""
        # Check for WiFi connection
        for pattern in self.WIFI_CONNECTED_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                result.wifi_connected = True
                break

        # Extract IP address
        ip_match = re.search(self.IP_ADDRESS_PATTERN, line)
        if ip_match:
            result.esp32_ip = ip_match.group(1)

        # Check for server start
        if re.search(self.SERVER_STARTED_PATTERN, line, re.IGNORECASE):
            result.server_started = True

        # Extract BPM values
        bpm_match = re.search(self.BPM_PATTERN, line)
        if bpm_match:
            bpm = float(bpm_match.group(1))
            if 60 <= bpm <= 200:  # Valid BPM range
                result.bpm_values.append(bpm)

        # Check for errors
        for pattern in self.ERROR_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                result.errors.append(line.strip())
                break


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="ESP32 Serial Monitor")
    parser.add_argument("-p", "--port", help="Serial port", default=None)
    parser.add_argument("-b", "--baud", type=int, default=115200, help="Baud rate")
    parser.add_argument("-d", "--duration", type=int, default=30, help="Monitor duration (seconds)")
    args = parser.parse_args()

    port = args.port
    if not port:
        port = SerialMonitor.find_esp32_port()
        if not port:
            print("ERROR: No ESP32 device found")
            return 1

    print(f"Monitoring {port} at {args.baud} baud for {args.duration}s...")

    monitor = SerialMonitor(port, args.baud)
    result = await monitor.monitor(args.duration)

    print()
    print("=" * 60)
    print("Serial Monitor Results")
    print("=" * 60)
    print(f"WiFi Connected:  {'Yes' if result.wifi_connected else 'No'}")
    print(f"ESP32 IP:        {result.esp32_ip or 'Not found'}")
    print(f"Server Started:  {'Yes' if result.server_started else 'No'}")
    print(f"BPM Values:      {len(result.bpm_values)} samples")
    print(f"Errors:          {len(result.errors)}")
    print(f"Duration:        {result.duration:.1f}s")
    print()

    if result.errors:
        print("Errors detected:")
        for err in result.errors[:5]:  # Show first 5 errors
            print(f"  - {err[:80]}")

    if result.is_success():
        print("SUCCESS: ESP32 WiFi and HTTP server operational")
        return 0
    else:
        print("FAILED: ESP32 not fully operational")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
