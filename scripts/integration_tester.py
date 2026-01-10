#!/usr/bin/env python3
"""
Integration Tester for ESP32-Android BPM Communication
Tests full connectivity: ESP32 WiFi -> HTTP API -> Android App -> BPM Display
"""

import asyncio
import subprocess
import re
import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from pathlib import Path

from serial_monitor import SerialMonitor, SerialMonitorResult
from network_scanner import NetworkScanner, ScanResult


@dataclass
class AndroidTestResult:
    device_id: Optional[str] = None
    app_installed: bool = False
    app_launched: bool = False
    connected_to_esp32: bool = False
    bpm_received: bool = False
    bpm_values: List[float] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class IntegrationTestResult:
    success: bool = False
    esp32_port: Optional[str] = None
    esp32_ip: Optional[str] = None
    wifi_connected: bool = False
    api_healthy: bool = False
    android_result: Optional[AndroidTestResult] = None
    serial_result: Optional[SerialMonitorResult] = None
    network_result: Optional[ScanResult] = None
    duration: float = 0.0
    errors: List[str] = field(default_factory=list)

    def summarize(self) -> str:
        lines = [
            "=" * 60,
            "Integration Test Results",
            "=" * 60,
            f"Overall Success:  {'YES' if self.success else 'NO'}",
            f"ESP32 Port:       {self.esp32_port or 'Not found'}",
            f"ESP32 IP:         {self.esp32_ip or 'Not found'}",
            f"WiFi Connected:   {'Yes' if self.wifi_connected else 'No'}",
            f"API Healthy:      {'Yes' if self.api_healthy else 'No'}",
            f"Duration:         {self.duration:.1f}s",
            "",
        ]

        if self.android_result:
            lines.extend([
                "Android Results:",
                f"  Device ID:      {self.android_result.device_id or 'Not found'}",
                f"  App Installed:  {'Yes' if self.android_result.app_installed else 'No'}",
                f"  Connected:      {'Yes' if self.android_result.connected_to_esp32 else 'No'}",
                f"  BPM Received:   {'Yes' if self.android_result.bpm_received else 'No'} ({len(self.android_result.bpm_values)} values)",
                "",
            ])

        if self.errors:
            lines.append("Errors:")
            for err in self.errors[:5]:
                lines.append(f"  - {err[:80]}")

        return "\n".join(lines)


class AndroidTester:
    """Test Android app connectivity to ESP32"""

    APP_PACKAGE = "com.sparesparrow.bpmdetector.debug"
    MAIN_ACTIVITY = "com.sparesparrow.bpmdetector.MainActivity"

    def __init__(self):
        self.device_id = None

    def detect_device(self) -> Optional[str]:
        """Detect connected Android device via ADB"""
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:
                    if '\tdevice' in line:
                        self.device_id = line.split('\t')[0]
                        return self.device_id
        except Exception as e:
            pass
        return None

    def is_app_installed(self) -> bool:
        """Check if BPM app is installed"""
        if not self.device_id:
            return False

        try:
            result = subprocess.run(
                ["adb", "-s", self.device_id, "shell", "pm", "list", "packages", self.APP_PACKAGE],
                capture_output=True, text=True, timeout=10
            )
            return self.APP_PACKAGE in result.stdout
        except:
            return False

    def launch_app(self) -> bool:
        """Launch the BPM detector app"""
        if not self.device_id:
            return False

        try:
            result = subprocess.run(
                ["adb", "-s", self.device_id, "shell", "am", "start", "-n",
                 f"{self.APP_PACKAGE}/{self.MAIN_ACTIVITY}"],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except:
            return False

    def configure_esp32_ip(self, ip: str) -> bool:
        """Configure ESP32 IP in app settings via ADB"""
        if not self.device_id:
            return False

        try:
            # Navigate to settings (tap bottom nav - approximate coordinates)
            subprocess.run(
                ["adb", "-s", self.device_id, "shell", "input", "tap", "540", "1850"],
                timeout=5
            )
            time.sleep(1)

            # Clear and enter IP
            subprocess.run(
                ["adb", "-s", self.device_id, "shell", "input", "tap", "540", "500"],
                timeout=5
            )
            time.sleep(0.5)

            # Select all and delete
            subprocess.run(
                ["adb", "-s", self.device_id, "shell", "input", "keyevent", "KEYCODE_CTRL_A"],
                timeout=5
            )
            subprocess.run(
                ["adb", "-s", self.device_id, "shell", "input", "keyevent", "KEYCODE_DEL"],
                timeout=5
            )

            # Enter IP
            subprocess.run(
                ["adb", "-s", self.device_id, "shell", "input", "text", ip],
                timeout=5
            )
            time.sleep(0.5)

            # Tap connect button
            subprocess.run(
                ["adb", "-s", self.device_id, "shell", "input", "tap", "540", "700"],
                timeout=5
            )

            return True
        except:
            return False

    def monitor_logcat(self, duration: int = 15) -> AndroidTestResult:
        """Monitor logcat for BPM data and connection status"""
        result = AndroidTestResult()
        result.device_id = self.device_id

        if not self.device_id:
            result.errors.append("No Android device connected")
            return result

        result.app_installed = self.is_app_installed()
        if not result.app_installed:
            result.errors.append("BPM app not installed")
            return result

        # Clear logcat
        subprocess.run(
            ["adb", "-s", self.device_id, "logcat", "-c"],
            timeout=5
        )

        # Launch app
        result.app_launched = self.launch_app()
        time.sleep(2)

        # Monitor logcat
        try:
            proc = subprocess.Popen(
                ["adb", "-s", self.device_id, "logcat", "-v", "time"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            end_time = time.time() + duration
            while time.time() < end_time:
                line = proc.stdout.readline().decode('utf-8', errors='replace')
                if not line:
                    break

                # Check for connection
                if "Connected to ESP32" in line or "Connection status: CONNECTED" in line:
                    result.connected_to_esp32 = True

                # Check for BPM data
                bpm_match = re.search(r'BPM[:\s]+(\d+\.?\d*)', line)
                if bpm_match:
                    bpm = float(bpm_match.group(1))
                    if 60 <= bpm <= 200:
                        result.bpm_values.append(bpm)
                        result.bpm_received = True

                # Check for errors
                if "Error" in line or "Exception" in line:
                    if self.APP_PACKAGE in line:
                        result.errors.append(line.strip()[:100])

            proc.terminate()

        except Exception as e:
            result.errors.append(f"Logcat error: {e}")

        return result


class IntegrationTester:
    """Full integration test: ESP32 WiFi -> API -> Android"""

    def __init__(self, project_dir: Path = None):
        self.project_dir = project_dir or Path(__file__).parent.parent
        self.serial_monitor = None
        self.network_scanner = NetworkScanner()
        self.android_tester = AndroidTester()

    async def run_full_test(
        self,
        esp32_port: str = None,
        serial_timeout: int = 30,
        android_timeout: int = 15
    ) -> IntegrationTestResult:
        """Run complete integration test"""
        result = IntegrationTestResult()
        start_time = time.time()

        # Phase 1: Find ESP32 port
        if esp32_port:
            result.esp32_port = esp32_port
        else:
            result.esp32_port = SerialMonitor.find_esp32_port()

        if not result.esp32_port:
            result.errors.append("ESP32 serial port not found")
            result.duration = time.time() - start_time
            return result

        # Phase 2: Monitor ESP32 serial for WiFi connection
        print(f"[1/4] Monitoring ESP32 serial ({result.esp32_port})...")
        self.serial_monitor = SerialMonitor(result.esp32_port)
        result.serial_result = await self.serial_monitor.monitor(serial_timeout)

        result.wifi_connected = result.serial_result.wifi_connected
        result.esp32_ip = result.serial_result.esp32_ip

        if not result.wifi_connected:
            result.errors.append("ESP32 WiFi connection failed")
            result.errors.extend(result.serial_result.errors)

        # Phase 3: If no IP from serial, scan network
        if not result.esp32_ip and result.wifi_connected:
            print("[2/4] Scanning network for ESP32...")
            result.network_result = await self.network_scanner.scan_for_esp32()
            result.esp32_ip = result.network_result.esp32_ip

        if result.esp32_ip:
            # Verify API endpoints
            print(f"[3/4] Verifying API endpoints at {result.esp32_ip}...")
            result.network_result = await self.network_scanner.scan_for_esp32()
            if result.network_result.esp32_ip:
                endpoint_status = await self.network_scanner.verify_endpoints(result.esp32_ip)
                result.api_healthy = all(endpoint_status.values())
            else:
                # Direct verification
                scan_result = self.network_scanner.scan_known_ip(result.esp32_ip)
                result.api_healthy = scan_result.is_success()

        # Phase 4: Test Android app
        print("[4/4] Testing Android app...")
        self.android_tester.detect_device()

        if self.android_tester.device_id:
            if result.esp32_ip:
                self.android_tester.configure_esp32_ip(result.esp32_ip)
                time.sleep(2)

            result.android_result = self.android_tester.monitor_logcat(android_timeout)
        else:
            result.android_result = AndroidTestResult()
            result.android_result.errors.append("No Android device detected")

        # Determine overall success
        result.success = (
            result.wifi_connected and
            result.api_healthy and
            (result.android_result.bpm_received if result.android_result else False)
        )

        result.duration = time.time() - start_time
        return result


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="ESP32-Android Integration Tester")
    parser.add_argument("-p", "--port", help="ESP32 serial port")
    parser.add_argument("-t", "--timeout", type=int, default=30, help="Serial monitor timeout")
    parser.add_argument("--android-timeout", type=int, default=15, help="Android logcat timeout")
    args = parser.parse_args()

    tester = IntegrationTester()
    result = await tester.run_full_test(
        esp32_port=args.port,
        serial_timeout=args.timeout,
        android_timeout=args.android_timeout
    )

    print()
    print(result.summarize())

    return 0 if result.success else 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
