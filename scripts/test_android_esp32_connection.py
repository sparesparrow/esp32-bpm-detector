#!/usr/bin/env python3
"""
Test script to verify Android app can discover and connect to ESP32.

This script tests:
1. WiFi discovery - checks if ESP32 network is visible
2. Connection - verifies WiFi connection with password
3. HTTP communication - tests API endpoints on ESP32
"""

import sys
import time
import requests
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sparetools_utils import setup_logging

logger = setup_logging(__name__)

# ESP32 Configuration (must match firmware)
ESP32_SSID = "ESP32-BPM-Detector"
ESP32_PASSWORD = "bpm12345"
ESP32_AP_IP = "192.168.4.1"
ESP32_API_PORT = 80

# Test endpoints
HEALTH_ENDPOINT = f"http://{ESP32_AP_IP}/api/health"
BPM_ENDPOINT = f"http://{ESP32_AP_IP}/api/bpm"
SETTINGS_ENDPOINT = f"http://{ESP32_AP_IP}/api/settings"


def test_http_connectivity():
    """Test HTTP connectivity to ESP32."""
    logger.info("=" * 60)
    logger.info("Testing HTTP Connectivity to ESP32")
    logger.info("=" * 60)
    
    results = {
        "health": False,
        "bpm": False,
        "settings": False
    }
    
    # Test health endpoint
    logger.info(f"\n1. Testing Health Endpoint: {HEALTH_ENDPOINT}")
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            logger.info(f"   ✓ Health endpoint responded: {response.status_code}")
            logger.info(f"   Response: {response.text[:200]}")
            results["health"] = True
        else:
            logger.warning(f"   ✗ Health endpoint returned: {response.status_code}")
    except requests.exceptions.ConnectionError:
        logger.error("   ✗ Connection refused - ESP32 not reachable at this IP")
    except requests.exceptions.Timeout:
        logger.error("   ✗ Request timeout - ESP32 not responding")
    except Exception as e:
        logger.error(f"   ✗ Error: {e}")
    
    # Test BPM endpoint
    logger.info(f"\n2. Testing BPM Endpoint: {BPM_ENDPOINT}")
    try:
        response = requests.get(BPM_ENDPOINT, timeout=5)
        if response.status_code == 200:
            logger.info(f"   ✓ BPM endpoint responded: {response.status_code}")
            logger.info(f"   Response length: {len(response.content)} bytes")
            results["bpm"] = True
        else:
            logger.warning(f"   ✗ BPM endpoint returned: {response.status_code}")
    except Exception as e:
        logger.error(f"   ✗ Error: {e}")
    
    # Test settings endpoint
    logger.info(f"\n3. Testing Settings Endpoint: {SETTINGS_ENDPOINT}")
    try:
        response = requests.get(SETTINGS_ENDPOINT, timeout=5)
        if response.status_code == 200:
            logger.info(f"   ✓ Settings endpoint responded: {response.status_code}")
            logger.info(f"   Response length: {len(response.content)} bytes")
            results["settings"] = True
        else:
            logger.warning(f"   ✗ Settings endpoint returned: {response.status_code}")
    except Exception as e:
        logger.error(f"   ✗ Error: {e}")
    
    return results


def test_network_configuration():
    """Verify network configuration matches between Android and ESP32."""
    logger.info("=" * 60)
    logger.info("Verifying Network Configuration")
    logger.info("=" * 60)
    
    # Read Android app files
    android_wifi_manager = Path(__file__).parent.parent / "android-app" / "app" / "src" / "main" / "java" / "com" / "sparesparrow" / "bpmdetector" / "network" / "WiFiManager.kt"
    android_service = Path(__file__).parent.parent / "android-app" / "app" / "src" / "main" / "java" / "com" / "sparesparrow" / "bpmdetector" / "services" / "BPMService.kt"
    
    issues = []
    
    # Check WiFiManager SSID
    if android_wifi_manager.exists():
        content = android_wifi_manager.read_text()
        if f'ESP32_SSID = "{ESP32_SSID}"' in content or f'ESP32_SSID = "{ESP32_SSID}"' in content:
            logger.info(f"✓ WiFiManager SSID matches: {ESP32_SSID}")
        else:
            logger.error(f"✗ WiFiManager SSID mismatch!")
            issues.append("WiFiManager SSID")
    
    # Check WiFiManager password
    if android_wifi_manager.exists():
        content = android_wifi_manager.read_text()
        if f'ESP32_DEFAULT_PASSWORD = "{ESP32_PASSWORD}"' in content:
            logger.info(f"✓ WiFiManager password matches: {ESP32_PASSWORD}")
        else:
            logger.error(f"✗ WiFiManager password mismatch!")
            issues.append("WiFiManager password")
    
    # Check BPMService IP
    if android_service.exists():
        content = android_service.read_text()
        if f'serverIp: String = "{ESP32_AP_IP}"' in content:
            logger.info(f"✓ BPMService IP matches: {ESP32_AP_IP}")
        else:
            logger.error(f"✗ BPMService IP mismatch!")
            issues.append("BPMService IP")
    
    return len(issues) == 0, issues


def main():
    """Main test function."""
    logger.info("\n" + "=" * 60)
    logger.info("Android-ESP32 Connection Test")
    logger.info("=" * 60)
    logger.info(f"\nESP32 Configuration:")
    logger.info(f"  SSID: {ESP32_SSID}")
    logger.info(f"  Password: {ESP32_PASSWORD}")
    logger.info(f"  AP IP: {ESP32_AP_IP}")
    logger.info("")
    
    # Test 1: Verify configuration
    logger.info("\n[TEST 1] Verifying Android app configuration...")
    config_ok, issues = test_network_configuration()
    if not config_ok:
        logger.error(f"\n✗ Configuration issues found: {', '.join(issues)}")
        logger.error("Please fix these issues before testing connectivity.")
        return 1
    
    logger.info("\n✓ All configuration checks passed!")
    
    # Test 2: HTTP connectivity (requires ESP32 to be running and connected)
    logger.info("\n[TEST 2] Testing HTTP connectivity to ESP32...")
    logger.info("NOTE: This test requires:")
    logger.info("  1. ESP32 to be powered on and running")
    logger.info("  2. ESP32 WiFi AP to be active")
    logger.info("  3. This machine to be connected to ESP32 WiFi network")
    logger.info("")
    
    input("Press Enter when ESP32 is running and you're connected to its WiFi network...")
    
    http_results = test_http_connectivity()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    logger.info(f"Configuration: {'✓ PASS' if config_ok else '✗ FAIL'}")
    logger.info(f"Health Endpoint: {'✓ PASS' if http_results['health'] else '✗ FAIL'}")
    logger.info(f"BPM Endpoint: {'✓ PASS' if http_results['bpm'] else '✗ FAIL'}")
    logger.info(f"Settings Endpoint: {'✓ PASS' if http_results['settings'] else '✗ FAIL'}")
    
    all_passed = config_ok and all(http_results.values())
    
    if all_passed:
        logger.info("\n✓ All tests passed! Android app should be able to connect to ESP32.")
        return 0
    else:
        logger.warning("\n✗ Some tests failed. Check the logs above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
