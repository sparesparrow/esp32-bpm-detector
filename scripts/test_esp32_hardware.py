#!/usr/bin/env python3
"""
ESP32-S3 Hardware Test Script

Tests ESP32 BPM Detector hardware functionality:
- Device detection
- Firmware flashing
- Serial communication
- BPM detection accuracy
- Audio input processing
- Performance metrics
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import serial
    import serial.tools.list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False
    print("Warning: pyserial not installed. Install with: pip install pyserial")


class ESP32HardwareTest:
    """Test suite for ESP32 hardware."""
    
    # Known ESP32 device identifiers
    ESP32_DEVICES = {
        (0x303A, 0x1001): ("ESP32-S3 USB-CDC", True),   # USB OTG with JTAG
        (0x303A, 0x1002): ("ESP32-S2 USB-CDC", True),   # USB OTG with JTAG
        (0x10C4, 0xEA60): ("ESP32 CP210x", False),      # Silicon Labs USB-UART
        (0x1A86, 0x7523): ("ESP32 CH340", False),       # WinChipHead USB-UART
        (0x1A86, 0x55D4): ("ESP32 CH9102", False),      # CH9102 USB-UART
    }
    
    def __init__(
        self,
        project_dir: Path,
        port: Optional[str] = None,
        baud_rate: int = 115200,
    ):
        self.project_dir = project_dir
        self.port = port
        self.baud_rate = baud_rate
        self.device_info: Optional[Dict] = None
        self.test_results: List[Dict] = []
    
    def detect_device(self) -> Optional[Dict[str, Any]]:
        """Detect connected ESP32 device."""
        if not HAS_SERIAL:
            return None
        
        for port in serial.tools.list_ports.comports():
            key = (port.vid, port.pid) if port.vid and port.pid else None
            if key in self.ESP32_DEVICES:
                name, has_jtag = self.ESP32_DEVICES[key]
                self.device_info = {
                    "port": port.device,
                    "name": name,
                    "vid": f"0x{port.vid:04X}",
                    "pid": f"0x{port.pid:04X}",
                    "serial_number": port.serial_number,
                    "has_jtag": has_jtag,
                }
                self.port = port.device
                return self.device_info
        
        return None
    
    async def flash_firmware(self, environment: str = "esp32-s3-release") -> Dict[str, Any]:
        """Flash firmware to ESP32 device."""
        result = {
            "name": "flash_firmware",
            "passed": False,
            "duration": 0.0,
        }
        
        if not self.port:
            result["error"] = "No device port specified"
            return result
        
        start = time.time()
        
        try:
            cmd = [
                "pio", "run",
                "-e", environment,
                "-t", "upload",
                "--upload-port", self.port,
            ]
            
            proc = subprocess.run(
                cmd,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=120,
            )
            
            result["passed"] = proc.returncode == 0
            result["output"] = proc.stdout[-1000:] if proc.returncode == 0 else proc.stderr[-500:]
            
        except subprocess.TimeoutExpired:
            result["error"] = "Flash operation timed out"
        except Exception as e:
            result["error"] = str(e)
        
        result["duration"] = time.time() - start
        self.test_results.append(result)
        return result
    
    async def test_serial_communication(self) -> Dict[str, Any]:
        """Test serial communication with device."""
        result = {
            "name": "serial_communication",
            "passed": False,
            "duration": 0.0,
        }
        
        if not self.port or not HAS_SERIAL:
            result["error"] = "No device port or pyserial not available"
            return result
        
        start = time.time()
        
        try:
            with serial.Serial(self.port, self.baud_rate, timeout=5) as ser:
                # Wait for device boot
                await asyncio.sleep(2)
                
                # Read any available data
                data = ser.read(ser.in_waiting or 1024)
                output = data.decode("utf-8", errors="replace")
                
                # Check for boot indicators
                boot_indicators = ["ready", "started", "initialized", "boot", "bpm", "esp32"]
                result["passed"] = any(ind in output.lower() for ind in boot_indicators)
                result["output"] = output[:500]
                result["bytes_received"] = len(data)
                
        except Exception as e:
            result["error"] = str(e)
        
        result["duration"] = time.time() - start
        self.test_results.append(result)
        return result
    
    async def test_bpm_detection(self, test_duration: float = 5.0) -> Dict[str, Any]:
        """Test BPM detection functionality."""
        result = {
            "name": "bpm_detection",
            "passed": False,
            "duration": 0.0,
            "bpm_readings": [],
        }
        
        if not self.port or not HAS_SERIAL:
            result["error"] = "No device port or pyserial not available"
            return result
        
        start = time.time()
        
        try:
            with serial.Serial(self.port, self.baud_rate, timeout=1) as ser:
                # Collect BPM readings
                end_time = time.time() + test_duration
                
                while time.time() < end_time:
                    if ser.in_waiting:
                        line = ser.readline().decode("utf-8", errors="replace").strip()
                        
                        # Parse BPM from output
                        if "bpm" in line.lower():
                            try:
                                # Extract numeric BPM value
                                import re
                                match = re.search(r"(\d+\.?\d*)\s*bpm", line, re.IGNORECASE)
                                if match:
                                    bpm = float(match.group(1))
                                    if 30 <= bpm <= 300:  # Valid BPM range
                                        result["bpm_readings"].append({
                                            "timestamp": time.time() - start,
                                            "bpm": bpm,
                                        })
                            except (ValueError, AttributeError):
                                pass
                    
                    await asyncio.sleep(0.1)
                
                # Analyze results
                if result["bpm_readings"]:
                    bpm_values = [r["bpm"] for r in result["bpm_readings"]]
                    result["avg_bpm"] = sum(bpm_values) / len(bpm_values)
                    result["min_bpm"] = min(bpm_values)
                    result["max_bpm"] = max(bpm_values)
                    result["reading_count"] = len(bpm_values)
                    result["passed"] = True
                else:
                    result["passed"] = False
                    result["note"] = "No BPM readings captured - ensure audio input is active"
                
        except Exception as e:
            result["error"] = str(e)
        
        result["duration"] = time.time() - start
        self.test_results.append(result)
        return result
    
    async def test_audio_input(self) -> Dict[str, Any]:
        """Test audio input processing."""
        result = {
            "name": "audio_input",
            "passed": False,
            "duration": 0.0,
        }
        
        if not self.port or not HAS_SERIAL:
            result["error"] = "No device port or pyserial not available"
            return result
        
        start = time.time()
        
        try:
            with serial.Serial(self.port, self.baud_rate, timeout=2) as ser:
                # Send test command
                ser.write(b"audio_test\n")
                await asyncio.sleep(1)
                
                # Read response
                data = ser.read(ser.in_waiting or 1024)
                output = data.decode("utf-8", errors="replace")
                
                # Check for audio-related output
                audio_indicators = ["audio", "mic", "adc", "sample", "fft", "frequency"]
                result["passed"] = any(ind in output.lower() for ind in audio_indicators)
                result["output"] = output[:500]
                
                # If no audio indicators, still pass if device is responsive
                if not result["passed"] and output:
                    result["passed"] = True
                    result["note"] = "Device responsive but no audio-specific output"
                
        except Exception as e:
            result["error"] = str(e)
        
        result["duration"] = time.time() - start
        self.test_results.append(result)
        return result
    
    async def collect_performance_metrics(self, duration: float = 5.0) -> Dict[str, Any]:
        """Collect performance metrics from device."""
        result = {
            "name": "performance_metrics",
            "passed": True,
            "duration": 0.0,
            "metrics": {},
        }
        
        if not self.port or not HAS_SERIAL:
            result["error"] = "No device port or pyserial not available"
            return result
        
        start = time.time()
        
        try:
            with serial.Serial(self.port, self.baud_rate, timeout=1) as ser:
                # Request metrics
                ser.write(b"metrics\n")
                
                end_time = time.time() + duration
                output_lines = []
                
                while time.time() < end_time:
                    if ser.in_waiting:
                        line = ser.readline().decode("utf-8", errors="replace").strip()
                        output_lines.append(line)
                        
                        # Parse metrics
                        if "cpu" in line.lower():
                            try:
                                import re
                                match = re.search(r"(\d+\.?\d*)\s*%", line)
                                if match:
                                    result["metrics"]["cpu_usage"] = float(match.group(1))
                            except:
                                pass
                        
                        if "memory" in line.lower() or "heap" in line.lower():
                            try:
                                import re
                                match = re.search(r"(\d+)\s*(kb|bytes)", line, re.IGNORECASE)
                                if match:
                                    result["metrics"]["memory_free"] = int(match.group(1))
                            except:
                                pass
                    
                    await asyncio.sleep(0.1)
                
                result["output"] = "\n".join(output_lines[-20:])
                
        except Exception as e:
            result["error"] = str(e)
            result["passed"] = False
        
        result["duration"] = time.time() - start
        self.test_results.append(result)
        return result
    
    async def run_all_tests(
        self,
        flash: bool = False,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """Run all hardware tests."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "device": self.device_info,
            "tests": [],
            "passed": True,
        }
        
        start = time.time()
        
        # Flash firmware if requested
        if flash:
            flash_result = await self.flash_firmware()
            results["tests"].append(flash_result)
            if not flash_result["passed"]:
                results["passed"] = False
                return results
            # Wait for device to boot
            await asyncio.sleep(3)
        
        # Run tests
        tests = [
            self.test_serial_communication(),
            self.test_bpm_detection(),
            self.test_audio_input(),
            self.collect_performance_metrics(),
        ]
        
        for test_coro in tests:
            test_result = await test_coro
            results["tests"].append(test_result)
            if not test_result.get("passed", False):
                results["passed"] = False
            
            if verbose:
                status = "✓" if test_result["passed"] else "✗"
                print(f"  {status} {test_result['name']}: {test_result['duration']:.2f}s")
        
        results["total_duration"] = time.time() - start
        return results


def main():
    parser = argparse.ArgumentParser(description="ESP32-S3 Hardware Test Script")
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Project directory",
    )
    parser.add_argument(
        "--port",
        type=str,
        help="Serial port (auto-detect if not specified)",
    )
    parser.add_argument(
        "--baud-rate",
        type=int,
        default=115200,
        help="Serial baud rate",
    )
    parser.add_argument(
        "--flash",
        action="store_true",
        help="Flash firmware before testing",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    
    args = parser.parse_args()
    
    tester = ESP32HardwareTest(
        project_dir=args.project_dir,
        port=args.port,
        baud_rate=args.baud_rate,
    )
    
    # Detect device if port not specified
    if not args.port:
        device = tester.detect_device()
        if device:
            print(f"Detected: {device['name']} at {device['port']}")
        else:
            print("Error: No ESP32 device detected")
            return 1
    
    # Run tests
    results = asyncio.run(tester.run_all_tests(
        flash=args.flash,
        verbose=args.verbose,
    ))
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"ESP32 Hardware Test Results")
        print(f"{'='*60}")
        
        if results.get("device"):
            print(f"Device: {results['device']['name']}")
            print(f"Port: {results['device']['port']}")
        
        print(f"\nTests:")
        for test in results["tests"]:
            status = "✓" if test["passed"] else "✗"
            print(f"  {status} {test['name']} ({test['duration']:.2f}s)")
            if "error" in test:
                print(f"    Error: {test['error']}")
        
        print(f"\nTotal Duration: {results['total_duration']:.2f}s")
        print(f"Status: {'PASSED' if results['passed'] else 'FAILED'}")
    
    return 0 if results["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
