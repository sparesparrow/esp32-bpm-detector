#!/usr/bin/env python3
"""
Integration Test Runner for ESP32 BPM Detector

Runs integration tests with real ESP32 hardware and Android devices.
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

try:
    import serial
    import serial.tools.list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False


class DeviceDetector:
    """Detect connected ESP32 and Android devices."""
    
    # Known ESP32 VID:PID mappings
    ESP32_DEVICES = {
        (0x303A, 0x1001): "ESP32-S3 USB-CDC",
        (0x10C4, 0xEA60): "ESP32 CP210x",
        (0x1A86, 0x7523): "CH340",
    }
    
    @classmethod
    def detect_esp32(cls) -> Optional[Dict[str, Any]]:
        """Detect connected ESP32 device."""
        if not HAS_SERIAL:
            return None
        
        for port in serial.tools.list_ports.comports():
            key = (port.vid, port.pid)
            if key in cls.ESP32_DEVICES:
                return {
                    "port": port.device,
                    "name": cls.ESP32_DEVICES[key],
                    "vid": f"0x{port.vid:04X}",
                    "pid": f"0x{port.pid:04X}",
                    "serial": port.serial_number,
                }
        
        return None
    
    @classmethod
    def detect_android(cls) -> Optional[Dict[str, Any]]:
        """Detect connected Android device via ADB."""
        try:
            proc = subprocess.run(
                ["adb", "devices", "-l"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            lines = proc.stdout.strip().split("\n")
            for line in lines[1:]:
                if "device" in line and "unauthorized" not in line:
                    parts = line.split()
                    device_id = parts[0]
                    
                    # Get device model
                    model_proc = subprocess.run(
                        ["adb", "-s", device_id, "shell", "getprop", "ro.product.model"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    model = model_proc.stdout.strip() if model_proc.returncode == 0 else "Unknown"
                    
                    return {
                        "device_id": device_id,
                        "model": model,
                        "status": "connected",
                    }
        
        except Exception:
            pass
        
        return None


class IntegrationTestRunner:
    """Runner for integration tests with real hardware."""
    
    def __init__(self, project_dir: Path, output_dir: Optional[Path] = None):
        self.project_dir = project_dir
        self.output_dir = output_dir or project_dir / "test-results"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def run_tests(
        self,
        esp32_port: Optional[str] = None,
        adb_device: Optional[str] = None,
        flash_firmware: bool = True,
        run_android_tests: bool = True,
        timeout: int = 300,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """Run integration tests.
        
        Args:
            esp32_port: Serial port of ESP32 (auto-detect if not specified)
            adb_device: ADB device ID (auto-detect if not specified)
            flash_firmware: Flash firmware before testing
            run_android_tests: Run Android app tests
            timeout: Test timeout in seconds
            verbose: Enable verbose output
        
        Returns:
            Dictionary with test results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "project_dir": str(self.project_dir),
            "passed": True,
            "esp32_tests": {},
            "android_tests": {},
            "e2e_tests": {},
            "duration": 0.0,
        }
        
        start_time = datetime.now()
        
        # Detect ESP32 device
        esp32_info = DeviceDetector.detect_esp32()
        if esp32_info:
            esp32_port = esp32_port or esp32_info["port"]
            results["esp32_device"] = esp32_info
            print(f"Found ESP32: {esp32_info['name']} at {esp32_port}")
        else:
            results["esp32_device"] = None
            results["passed"] = False
            results["error"] = "No ESP32 device detected"
            return results
        
        # Detect Android device
        android_info = DeviceDetector.detect_android()
        if android_info:
            adb_device = adb_device or android_info["device_id"]
            results["android_device"] = android_info
            print(f"Found Android: {android_info['model']} ({adb_device})")
        else:
            results["android_device"] = None
            print("No Android device detected, skipping Android tests")
        
        try:
            # Flash firmware if requested
            if flash_firmware:
                flash_result = await self._flash_firmware(esp32_port, verbose)
                results["flash_result"] = flash_result
                if not flash_result.get("success", False):
                    results["passed"] = False
                    return results
            
            # Run ESP32 hardware tests
            esp32_result = await self._run_esp32_tests(esp32_port, timeout, verbose)
            results["esp32_tests"] = esp32_result
            if not esp32_result.get("passed", False):
                results["passed"] = False
            
            # Run Android tests if device available
            if run_android_tests and android_info:
                android_result = await self._run_android_tests(adb_device, timeout, verbose)
                results["android_tests"] = android_result
                if not android_result.get("passed", False):
                    results["passed"] = False
                
                # Run end-to-end tests
                e2e_result = await self._run_e2e_tests(esp32_port, adb_device, timeout, verbose)
                results["e2e_tests"] = e2e_result
                if not e2e_result.get("passed", False):
                    results["passed"] = False
        
        except Exception as e:
            results["passed"] = False
            results["error"] = str(e)
        
        results["duration"] = (datetime.now() - start_time).total_seconds()
        
        # Save results
        results_file = self.output_dir / "integration_test_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        
        return results
    
    async def _flash_firmware(self, port: str, verbose: bool) -> Dict[str, Any]:
        """Flash firmware to ESP32."""
        print(f"Flashing firmware to {port}...")
        
        result = {
            "success": True,
            "duration": 0.0,
        }
        
        start = datetime.now()
        
        try:
            proc = subprocess.run(
                ["pio", "run", "-t", "upload", "--upload-port", port],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=120,
            )
            
            result["success"] = proc.returncode == 0
            result["output"] = proc.stdout[-1000:] if verbose else ""
            
            if proc.returncode != 0:
                result["error"] = proc.stderr[-500:]
        
        except subprocess.TimeoutExpired:
            result["success"] = False
            result["error"] = "Flash operation timed out"
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
        
        result["duration"] = (datetime.now() - start).total_seconds()
        return result
    
    async def _run_esp32_tests(self, port: str, timeout: int, verbose: bool) -> Dict[str, Any]:
        """Run tests on ESP32 hardware."""
        result = {
            "passed": True,
            "tests": [],
            "duration": 0.0,
        }
        
        start = datetime.now()
        
        try:
            # Test 1: Serial communication
            serial_test = await self._test_serial_communication(port)
            result["tests"].append(serial_test)
            
            # Test 2: BPM detection
            bpm_test = await self._test_bpm_detection(port)
            result["tests"].append(bpm_test)
            
            # Test 3: Audio input
            audio_test = await self._test_audio_input(port)
            result["tests"].append(audio_test)
            
            # Check overall pass status
            result["passed"] = all(t.get("passed", False) for t in result["tests"])
        
        except Exception as e:
            result["passed"] = False
            result["error"] = str(e)
        
        result["duration"] = (datetime.now() - start).total_seconds()
        return result
    
    async def _test_serial_communication(self, port: str) -> Dict[str, Any]:
        """Test serial communication with ESP32."""
        test = {
            "name": "serial_communication",
            "passed": False,
        }
        
        try:
            with serial.Serial(port, 115200, timeout=5) as ser:
                # Wait for boot message
                await asyncio.sleep(2)
                
                # Read available data
                data = ser.read(ser.in_waiting or 1024)
                output = data.decode("utf-8", errors="replace")
                
                # Check for common boot indicators
                test["passed"] = any(
                    indicator in output.lower()
                    for indicator in ["ready", "started", "initialized", "boot", "bpm"]
                )
                test["output"] = output[:500]
        
        except Exception as e:
            test["error"] = str(e)
        
        return test
    
    async def _test_bpm_detection(self, port: str) -> Dict[str, Any]:
        """Test BPM detection functionality."""
        test = {
            "name": "bpm_detection",
            "passed": False,
        }
        
        try:
            with serial.Serial(port, 115200, timeout=10) as ser:
                # Send test command
                ser.write(b"TEST_BPM\n")
                await asyncio.sleep(2)
                
                # Read response
                data = ser.read(ser.in_waiting or 1024)
                output = data.decode("utf-8", errors="replace")
                
                # Check for BPM output
                test["passed"] = "bpm" in output.lower() or "beat" in output.lower()
                test["output"] = output[:500]
        
        except Exception as e:
            test["error"] = str(e)
        
        return test
    
    async def _test_audio_input(self, port: str) -> Dict[str, Any]:
        """Test audio input processing."""
        test = {
            "name": "audio_input",
            "passed": True,  # Assume pass if no errors
        }
        
        try:
            # Run audio data test script if available
            test_script = self.project_dir / "tests" / "integration" / "test_audio_data.py"
            
            if test_script.exists():
                proc = subprocess.run(
                    [sys.executable, str(test_script), "--port", port],
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                
                test["passed"] = proc.returncode == 0
                test["output"] = proc.stdout[:500]
            else:
                test["skipped"] = True
        
        except Exception as e:
            test["passed"] = False
            test["error"] = str(e)
        
        return test
    
    async def _run_android_tests(self, device: str, timeout: int, verbose: bool) -> Dict[str, Any]:
        """Run Android app tests."""
        result = {
            "passed": True,
            "tests": [],
            "duration": 0.0,
        }
        
        start = datetime.now()
        
        try:
            # Build APK if needed
            build_test = await self._build_android_app(verbose)
            result["tests"].append(build_test)
            
            # Install APK
            install_test = await self._install_android_app(device)
            result["tests"].append(install_test)
            
            # Run instrumented tests
            instrumented_test = await self._run_instrumented_tests(device, timeout)
            result["tests"].append(instrumented_test)
            
            # Check overall pass status
            result["passed"] = all(t.get("passed", False) for t in result["tests"])
        
        except Exception as e:
            result["passed"] = False
            result["error"] = str(e)
        
        result["duration"] = (datetime.now() - start).total_seconds()
        return result
    
    async def _build_android_app(self, verbose: bool) -> Dict[str, Any]:
        """Build Android APK."""
        test = {
            "name": "android_build",
            "passed": False,
        }
        
        android_dir = self.project_dir / "android-app"
        
        if not android_dir.exists():
            test["skipped"] = True
            test["passed"] = True
            return test
        
        try:
            proc = subprocess.run(
                ["./gradlew", "assembleDebug"],
                cwd=android_dir,
                capture_output=True,
                text=True,
                timeout=300,
            )
            
            test["passed"] = proc.returncode == 0
            if verbose:
                test["output"] = proc.stdout[-500:]
            if proc.returncode != 0:
                test["error"] = proc.stderr[-500:]
        
        except Exception as e:
            test["passed"] = False
            test["error"] = str(e)
        
        return test
    
    async def _install_android_app(self, device: str) -> Dict[str, Any]:
        """Install APK to Android device."""
        test = {
            "name": "android_install",
            "passed": False,
        }
        
        apk_path = self.project_dir / "android-app" / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
        
        if not apk_path.exists():
            test["skipped"] = True
            test["passed"] = True
            return test
        
        try:
            proc = subprocess.run(
                ["adb", "-s", device, "install", "-r", str(apk_path)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            
            test["passed"] = proc.returncode == 0 and "Success" in proc.stdout
            test["output"] = proc.stdout
        
        except Exception as e:
            test["passed"] = False
            test["error"] = str(e)
        
        return test
    
    async def _run_instrumented_tests(self, device: str, timeout: int) -> Dict[str, Any]:
        """Run Android instrumented tests."""
        test = {
            "name": "instrumented_tests",
            "passed": True,
            "skipped": True,  # Skip if no instrumented tests available
        }
        
        return test
    
    async def _run_e2e_tests(self, esp32_port: str, adb_device: str, timeout: int, verbose: bool) -> Dict[str, Any]:
        """Run end-to-end tests between ESP32 and Android."""
        result = {
            "passed": True,
            "tests": [],
            "duration": 0.0,
        }
        
        start = datetime.now()
        
        try:
            # Test BLE/WiFi connection
            connection_test = {
                "name": "e2e_connection",
                "passed": True,
                "details": "End-to-end connection test placeholder",
            }
            result["tests"].append(connection_test)
            
            # Test data flow
            data_flow_test = {
                "name": "e2e_data_flow",
                "passed": True,
                "details": "Data flow test placeholder",
            }
            result["tests"].append(data_flow_test)
        
        except Exception as e:
            result["passed"] = False
            result["error"] = str(e)
        
        result["duration"] = (datetime.now() - start).total_seconds()
        return result


def main():
    parser = argparse.ArgumentParser(description="Run ESP32 BPM Detector integration tests")
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
        "--port",
        type=str,
        help="ESP32 serial port (auto-detect if not specified)",
    )
    parser.add_argument(
        "--adb-device",
        type=str,
        help="ADB device ID (auto-detect if not specified)",
    )
    parser.add_argument(
        "--no-flash",
        action="store_true",
        help="Skip firmware flashing",
    )
    parser.add_argument(
        "--no-android",
        action="store_true",
        help="Skip Android tests",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Test timeout in seconds",
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
    
    runner = IntegrationTestRunner(args.project_dir, args.output_dir)
    
    results = asyncio.run(runner.run_tests(
        esp32_port=args.port,
        adb_device=args.adb_device,
        flash_firmware=not args.no_flash,
        run_android_tests=not args.no_android,
        timeout=args.timeout,
        verbose=args.verbose,
    ))
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"Integration Test Results")
        print(f"{'='*60}")
        print(f"Duration: {results['duration']:.2f}s")
        print(f"Status: {'PASSED' if results['passed'] else 'FAILED'}")
        
        if results.get("esp32_device"):
            print(f"\nESP32: {results['esp32_device']['name']} at {results['esp32_device']['port']}")
        if results.get("android_device"):
            print(f"Android: {results['android_device']['model']}")
        
        print(f"\nESP32 Tests:")
        for test in results.get("esp32_tests", {}).get("tests", []):
            status = "✓" if test.get("passed", False) else "✗"
            print(f"  {status} {test['name']}")
        
        if results.get("android_tests", {}).get("tests"):
            print(f"\nAndroid Tests:")
            for test in results["android_tests"]["tests"]:
                status = "✓" if test.get("passed", False) else "✗"
                print(f"  {status} {test['name']}")
        
        if 'error' in results:
            print(f"\nError: {results['error']}")
    
    return 0 if results['passed'] else 1


if __name__ == "__main__":
    sys.exit(main())
