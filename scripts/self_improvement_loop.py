#!/usr/bin/env python3
"""
Self-Improvement Loop for ESP32-Android WiFi Connectivity
Orchestrates: DETECT -> FIX -> BUILD -> DEPLOY -> TEST -> ANALYZE
Iterates until success or max iterations reached
"""

import asyncio
import subprocess
import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from detect_build_state import BuildStateDetector
from serial_monitor import SerialMonitor
from network_scanner import NetworkScanner
from integration_tester import IntegrationTester, IntegrationTestResult


@dataclass
class IterationResult:
    iteration: int
    phase: str
    success: bool
    duration: float = 0.0
    build_success: bool = False
    deploy_success: bool = False
    wifi_connected: bool = False
    api_healthy: bool = False
    android_connected: bool = False
    bpm_received: bool = False
    esp32_ip: Optional[str] = None
    errors: List[str] = field(default_factory=list)


@dataclass
class LoopReport:
    timestamp: str
    iterations: int
    success: bool
    total_duration: float
    final_esp32_ip: Optional[str] = None
    history: List[Dict] = field(default_factory=list)


class BuildManager:
    """Handle firmware build and deployment"""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir

    async def build_firmware(self, env: str = "esp32-s3") -> Dict:
        """Build firmware using PlatformIO"""
        result = {"success": False, "duration": 0.0, "logs": ""}
        start_time = time.time()

        try:
            proc = await asyncio.create_subprocess_exec(
                "pio", "run", "-e", env,
                cwd=self.project_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )

            stdout, _ = await proc.communicate()
            result["logs"] = stdout.decode('utf-8', errors='replace')
            result["success"] = proc.returncode == 0
            result["returncode"] = proc.returncode

        except Exception as e:
            result["error"] = str(e)

        result["duration"] = time.time() - start_time
        return result

    async def deploy_firmware(self, port: str, env: str = "esp32-s3") -> Dict:
        """Deploy firmware to ESP32"""
        result = {"success": False, "duration": 0.0, "logs": ""}
        start_time = time.time()

        try:
            proc = await asyncio.create_subprocess_exec(
                "pio", "run", "-e", env, "-t", "upload", "--upload-port", port,
                cwd=self.project_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )

            stdout, _ = await proc.communicate()
            result["logs"] = stdout.decode('utf-8', errors='replace')
            result["success"] = proc.returncode == 0

            if result["success"]:
                # Wait for device to reset
                await asyncio.sleep(3)

        except Exception as e:
            result["error"] = str(e)

        result["duration"] = time.time() - start_time
        return result


class SelfImprovementLoop:
    """Main orchestrator for the self-improvement loop"""

    MAX_ITERATIONS = 10
    BUILD_ENV = "esp32-s3"

    def __init__(self, project_dir: Path = None):
        self.project_dir = project_dir or Path(__file__).parent.parent
        self.detector = BuildStateDetector(self.project_dir)
        self.builder = BuildManager(self.project_dir)
        self.tester = IntegrationTester(self.project_dir)
        self.history: List[IterationResult] = []

    async def run(self) -> LoopReport:
        """Execute the self-improvement loop"""
        start_time = time.time()
        final_ip = None

        for iteration in range(1, self.MAX_ITERATIONS + 1):
            print()
            print("=" * 60)
            print(f"  ITERATION {iteration}/{self.MAX_ITERATIONS}")
            print("=" * 60)

            iter_result = IterationResult(iteration=iteration, phase="INIT", success=False)
            iter_start = time.time()

            # Phase 1: Detect current state
            print("\n[DETECT] Analyzing build state...")
            state = self.detector.analyze()

            if not state.is_ready():
                print(f"  Build state not ready: {len(state.required_changes)} changes needed")
                for change in state.required_changes:
                    print(f"    - {change.description}")

                # Note: Code fixes were already applied before running this script
                # If changes still needed, something is wrong
                iter_result.phase = "DETECT"
                iter_result.errors.append("Build state not ready after code fixes")
                self.history.append(iter_result)
                continue
            else:
                print("  Build state is ready for WiFi connectivity")

            # Phase 2: Build firmware
            print("\n[BUILD] Compiling firmware...")
            build_result = await self.builder.build_firmware(self.BUILD_ENV)
            iter_result.build_success = build_result["success"]

            if not build_result["success"]:
                print(f"  Build FAILED (exit code: {build_result.get('returncode', 'unknown')})")
                iter_result.phase = "BUILD"
                iter_result.errors.append("Firmware build failed")

                # Extract error lines from build log
                for line in build_result["logs"].split('\n'):
                    if "error:" in line.lower():
                        iter_result.errors.append(line[:100])
                        print(f"    {line[:80]}")

                self.history.append(iter_result)
                continue
            else:
                print(f"  Build successful ({build_result['duration']:.1f}s)")

            # Phase 3: Find and deploy to ESP32
            print("\n[DEPLOY] Finding ESP32...")
            esp32_port = SerialMonitor.find_esp32_port()

            if not esp32_port:
                print("  ERROR: No ESP32 device found")
                iter_result.phase = "DEPLOY"
                iter_result.errors.append("ESP32 not found")
                self.history.append(iter_result)
                continue

            print(f"  Found ESP32 at {esp32_port}")
            print("  Uploading firmware...")

            deploy_result = await self.builder.deploy_firmware(esp32_port, self.BUILD_ENV)
            iter_result.deploy_success = deploy_result["success"]

            if not deploy_result["success"]:
                print("  Deploy FAILED")
                iter_result.phase = "DEPLOY"
                iter_result.errors.append("Firmware upload failed")
                self.history.append(iter_result)
                continue
            else:
                print(f"  Deploy successful ({deploy_result['duration']:.1f}s)")

            # Phase 4: Run integration test
            print("\n[TEST] Running integration test...")
            test_result = await self.tester.run_full_test(
                esp32_port=esp32_port,
                serial_timeout=30,
                android_timeout=15
            )

            iter_result.wifi_connected = test_result.wifi_connected
            iter_result.api_healthy = test_result.api_healthy
            iter_result.esp32_ip = test_result.esp32_ip

            if test_result.android_result:
                iter_result.android_connected = test_result.android_result.connected_to_esp32
                iter_result.bpm_received = test_result.android_result.bpm_received

            iter_result.errors.extend(test_result.errors)

            # Phase 5: Analyze results
            print("\n[ANALYZE] Results:")
            print(f"  WiFi Connected:    {'YES' if iter_result.wifi_connected else 'NO'}")
            print(f"  ESP32 IP:          {iter_result.esp32_ip or 'N/A'}")
            print(f"  API Healthy:       {'YES' if iter_result.api_healthy else 'NO'}")
            print(f"  Android Connected: {'YES' if iter_result.android_connected else 'NO'}")
            print(f"  BPM Received:      {'YES' if iter_result.bpm_received else 'NO'}")

            # Determine success
            iter_result.success = test_result.success
            iter_result.duration = time.time() - iter_start
            iter_result.phase = "COMPLETE"
            self.history.append(iter_result)

            if iter_result.success:
                final_ip = iter_result.esp32_ip
                print()
                print("=" * 60)
                print("  SUCCESS! All criteria met.")
                print(f"  ESP32 IP: {final_ip}")
                print("=" * 60)
                break
            else:
                print()
                print("  Iteration failed - will retry...")
                if iter_result.errors:
                    print("  Errors:")
                    for err in iter_result.errors[:3]:
                        print(f"    - {err[:60]}")

        # Generate report
        total_duration = time.time() - start_time
        success = self.history[-1].success if self.history else False

        report = LoopReport(
            timestamp=datetime.now().isoformat(),
            iterations=len(self.history),
            success=success,
            total_duration=total_duration,
            final_esp32_ip=final_ip,
            history=[asdict(r) for r in self.history]
        )

        # Save report
        self._save_report(report)

        return report

    def _save_report(self, report: LoopReport):
        """Save report to file"""
        report_dir = self.project_dir / "test-results" / "self-improvement"
        report_dir.mkdir(parents=True, exist_ok=True)

        report_file = report_dir / f"loop_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(report_file, 'w') as f:
            json.dump(asdict(report), f, indent=2)

        print(f"\nReport saved to: {report_file}")


def notify_user(success: bool, message: str):
    """Notify user via espeak and kdeconnect"""
    try:
        subprocess.run(["espeak", message], timeout=10, capture_output=True)
    except:
        pass

    try:
        icon = "dialog-ok" if success else "dialog-error"
        subprocess.run(
            ["kdeconnect-cli", "--ping-msg", message],
            timeout=10, capture_output=True
        )
    except:
        pass


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="ESP32-Android Self-Improvement Loop")
    parser.add_argument("--max-iter", type=int, default=10, help="Maximum iterations")
    parser.add_argument("--no-notify", action="store_true", help="Disable user notifications")
    args = parser.parse_args()

    print()
    print("=" * 60)
    print("  ESP32-Android Self-Improvement Loop")
    print("=" * 60)
    print(f"  Max Iterations: {args.max_iter}")
    print(f"  Project: {Path(__file__).parent.parent}")
    print()

    loop = SelfImprovementLoop()
    loop.MAX_ITERATIONS = args.max_iter

    report = await loop.run()

    print()
    print("=" * 60)
    print("  FINAL SUMMARY")
    print("=" * 60)
    print(f"  Success:        {'YES' if report.success else 'NO'}")
    print(f"  Iterations:     {report.iterations}")
    print(f"  Total Duration: {report.total_duration:.1f}s")
    if report.final_esp32_ip:
        print(f"  ESP32 IP:       {report.final_esp32_ip}")
    print()

    # Notify user
    if not args.no_notify:
        if report.success:
            notify_user(True, "ESP32 Android connectivity test passed!")
        else:
            notify_user(False, "ESP32 Android connectivity test failed.")

    return 0 if report.success else 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
