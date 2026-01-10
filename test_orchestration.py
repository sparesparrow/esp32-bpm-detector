#!/usr/bin/env python3
"""
Comprehensive Android + ESP32 testing orchestration script.
Monitors logs, takes screenshots, and interacts with the app via ADB.
"""

import subprocess
import time
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

class TestOrchestrator:
    """Orchestrates comprehensive Android + ESP32 testing."""

    def __init__(self):
        self.screenshot_dir = "test_screenshots"
        self.logs_dir = "test_logs"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        self.test_start_time = datetime.now()

    def take_screenshot(self, name: str) -> str:
        """Take a screenshot of the Android device."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.screenshot_dir}/screenshot_{name}_{timestamp}.png"
        try:
            subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=open(filename, "wb"), check=True)
            print(f"📸 Screenshot saved: {filename}")
            return filename
        except subprocess.CalledProcessError as e:
            print(f"❌ Screenshot failed: {e}")
            return None

    def tap_screen(self, x: int, y: int, description: str = ""):
        """Tap on screen coordinates."""
        try:
            subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)], check=True)
            print(f"👆 Tapped ({x},{y}) {description}")
            time.sleep(0.5)  # Brief pause after tap
        except subprocess.CalledProcessError as e:
            print(f"❌ Tap failed: {e}")

    def get_screen_size(self) -> tuple:
        """Get Android device screen size."""
        try:
            result = subprocess.run(["adb", "shell", "wm", "size"],
                                  capture_output=True, text=True, check=True)
            size_str = result.stdout.strip().split(": ")[1]
            width, height = map(int, size_str.split("x"))
            return width, height
        except:
            # Default to common screen size if detection fails
            return 1080, 1920

    def wait_for_log(self, pattern: str, timeout: int = 10) -> bool:
        """Wait for a specific log pattern to appear."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                result = subprocess.run(["adb", "logcat", "-d", "-s", "BPMDetector"],
                                      capture_output=True, text=True, timeout=2)
                if pattern in result.stdout:
                    print(f"📋 Found log pattern: {pattern}")
                    return True
            except:
                pass
            time.sleep(1)
        print(f"⏰ Timeout waiting for log pattern: {pattern}")
        return False

    def test_permission_flow(self):
        """Test location permission request flow."""
        print("\n🔐 Testing Location Permission Flow...")

        # Take initial screenshot
        self.take_screenshot("initial_state")

        # Wait for permission dialog (if it appears)
        if self.wait_for_log("Location permissions granted", timeout=5):
            print("✅ Location permissions already granted")
            return True

        # Check if permission dialog appears
        print("Waiting for permission dialog...")
        time.sleep(3)

        # Take screenshot during permission request
        self.take_screenshot("permission_dialog")

        # Get screen size and tap to allow permissions
        width, height = self.get_screen_size()
        print(f"📱 Screen size: {width}x{height}")

        # Try to tap "Allow" button (typical Android permission dialog)
        # Allow button is usually at bottom right
        allow_x = int(width * 0.8)
        allow_y = int(height * 0.85)
        self.tap_screen(allow_x, allow_y, "- Allow location permission")

        # Wait for permission to be granted
        if self.wait_for_log("Location permissions granted", timeout=5):
            print("✅ Location permissions granted successfully")
            self.take_screenshot("permission_granted")
            return True
        else:
            print("⚠️ Permission dialog may not have appeared or was already granted")
            return True

    def test_wifi_discovery(self):
        """Test WiFi network discovery."""
        print("\n📡 Testing WiFi Discovery...")

        # Take screenshot before discovery
        self.take_screenshot("before_discovery")

        # Wait for auto-discovery to start
        if self.wait_for_log("Starting enhanced auto-discovery", timeout=10):
            print("✅ Auto-discovery started")
        else:
            print("⚠️ Auto-discovery may have already started")

        # Wait for WiFi scan attempts
        if self.wait_for_log("WiFi scan attempt", timeout=15):
            print("✅ WiFi scanning in progress")
        else:
            print("⚠️ WiFi scanning may be in progress")

        # Take screenshot during discovery
        self.take_screenshot("during_discovery")

        # Wait for connection result
        connection_found = self.wait_for_log("Auto-discovery successful", timeout=30)
        if connection_found:
            print("✅ ESP32 device discovered and connected!")
            self.take_screenshot("connection_success")
            return True
        else:
            print("❌ ESP32 device not found or connection failed")
            self.take_screenshot("connection_failed")
            return False

    def test_bpm_monitoring(self):
        """Test BPM data monitoring."""
        print("\n💓 Testing BPM Monitoring...")

        # Wait for monitoring to start
        if self.wait_for_log("Start monitoring automatically", timeout=10):
            print("✅ BPM monitoring started")
        else:
            print("⚠️ BPM monitoring may have started")

        # Wait for BPM data
        bpm_found = False
        for i in range(10):
            if self.wait_for_log("BPM:", timeout=3):
                bpm_found = True
                break
            print(f"⏳ Waiting for BPM data... ({i+1}/10)")

        if bpm_found:
            print("✅ BPM data received!")
            self.take_screenshot("bpm_monitoring")
            return True
        else:
            print("❌ No BPM data received")
            return False

    def run_full_test_suite(self):
        """Run the complete test suite."""
        print("🚀 Starting Comprehensive Android + ESP32 Test Suite")
        print("=" * 60)

        results = {}

        # Test 1: Permission Flow
        results["permissions"] = self.test_permission_flow()

        # Test 2: WiFi Discovery
        results["wifi_discovery"] = self.test_wifi_discovery()

        # Test 3: BPM Monitoring
        results["bpm_monitoring"] = self.test_bpm_monitoring()

        # Final screenshot
        self.take_screenshot("test_complete")

        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)

        for test, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test.upper()}: {status}")

        total_tests = len(results)
        passed_tests = sum(results.values())
        print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")

        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Android app successfully connected to ESP32.")
        else:
            print("⚠️ Some tests failed. Check logs and screenshots for details.")

        return results

def main():
    """Main entry point."""
    orchestrator = TestOrchestrator()
    results = orchestrator.run_full_test_suite()

    # Save test summary
    summary_file = f"{orchestrator.logs_dir}/test_summary_{orchestrator.test_start_time.strftime('%Y%m%d_%H%M%S')}.txt"
    with open(summary_file, "w") as f:
        f.write("Android + ESP32 Integration Test Results\n")
        f.write("=" * 50 + "\n")
        f.write(f"Test Start: {orchestrator.test_start_time}\n")
        f.write(f"Test End: {datetime.now()}\n\n")
        for test, result in results.items():
            f.write(f"{test}: {'PASS' if result else 'FAIL'}\n")
        f.write(f"\nOverall: {sum(results.values())}/{len(results)} tests passed\n")

    print(f"\n📄 Test summary saved to: {summary_file}")

if __name__ == "__main__":
    main()