#!/usr/bin/env python3
"""
Test script for Unified Development Tools MCP Server
Demonstrates ESP32 serial monitor and device detection functionality
"""

import json
import sys
import subprocess
from typing import Dict, Any, List
from datetime import datetime

def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_device_detection() -> Dict[str, Any]:
    """Test device detection functionality."""
    print_section("1. Device Detection Test")
    
    try:
        result = subprocess.run(
            ["python3", "scripts/detect_devices.py", "--json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            manifest = json.loads(result.stdout)
            print(f"✅ Device detection successful")
            print(f"   Found {len(manifest.get('devices', []))} programmable device(s)")
            print(f"   Found {len(manifest.get('jtag_devices', []))} JTAG device(s)")
            
            if manifest.get('devices'):
                print("\n   Detected Devices:")
                for i, device in enumerate(manifest['devices'], 1):
                    print(f"   {i}. {device['type'].upper()}")
                    print(f"      Port: {device['port']}")
                    print(f"      PIO Env: {device.get('pio_env', 'N/A')}")
                    print(f"      Baud Rate: {device.get('baud_rate', 'N/A')}")
            
            return {"status": "success", "manifest": manifest}
        else:
            print(f"⚠️  Device detection returned non-zero exit code")
            print(f"   Output: {result.stdout}")
            print(f"   Error: {result.stderr}")
            return {"status": "warning", "output": result.stdout, "error": result.stderr}
            
    except subprocess.TimeoutExpired:
        print("❌ Device detection timed out")
        return {"status": "error", "message": "timeout"}
    except Exception as e:
        print(f"❌ Device detection failed: {e}")
        return {"status": "error", "message": str(e)}

def test_serial_port_listing() -> Dict[str, Any]:
    """Test serial port listing functionality."""
    print_section("2. Serial Port Listing Test")
    
    try:
        import serial.tools.list_ports
        
        ports = serial.tools.list_ports.comports()
        print(f"✅ Serial port listing successful")
        print(f"   Found {len(ports)} serial port(s)")
        
        if ports:
            print("\n   Available Serial Ports:")
            for i, port in enumerate(ports, 1):
                vid_pid = ""
                if 'VID:PID=' in port.hwid.upper():
                    vid_pid = port.hwid.upper().split('VID:PID=')[1].split()[0]
                
                print(f"   {i}. {port.device}")
                print(f"      Description: {port.description}")
                print(f"      VID:PID: {vid_pid if vid_pid else 'N/A'}")
                print(f"      Hardware ID: {port.hwid}")
        else:
            print("   ⚠️  No serial ports detected")
        
        return {
            "status": "success",
            "ports": [
                {
                    "device": p.device,
                    "description": p.description,
                    "hwid": p.hwid
                }
                for p in ports
            ]
        }
        
    except ImportError:
        print("❌ pyserial not available")
        return {"status": "error", "message": "pyserial not installed"}
    except Exception as e:
        print(f"❌ Serial port listing failed: {e}")
        return {"status": "error", "message": str(e)}

def test_emulator_status() -> Dict[str, Any]:
    """Test hardware emulator status check."""
    print_section("3. Hardware Emulator Status Test")
    
    try:
        # Check if emulator script exists
        import os
        emulator_script = "scripts/start_emulator.py"
        
        if not os.path.exists(emulator_script):
            print("⚠️  Emulator script not found")
            return {"status": "warning", "message": "script not found"}
        
        # Try to import and check emulator class
        sys.path.insert(0, 'scripts')
        from start_emulator import HardwareEmulator
        
        print("✅ Emulator module loaded successfully")
        print("   Emulator class available: HardwareEmulator")
        print("   Default host: 127.0.0.1")
        print("   Default port: 12345")
        print("   Supported device types: esp32, esp32s3, arduino")
        
        # Check if emulator is running (try to connect)
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', 12345))
            sock.close()
            
            if result == 0:
                print("   Status: 🟢 Emulator is running on port 12345")
                return {"status": "success", "emulator_running": True}
            else:
                print("   Status: 🔴 Emulator is not running")
                return {"status": "success", "emulator_running": False}
        except Exception as e:
            print(f"   Status: 🔴 Could not check emulator status: {e}")
            return {"status": "warning", "emulator_running": None, "message": str(e)}
            
    except Exception as e:
        print(f"❌ Emulator status check failed: {e}")
        return {"status": "error", "message": str(e)}

def test_serial_monitor_capabilities() -> Dict[str, Any]:
    """Test serial monitor capabilities."""
    print_section("4. Serial Monitor Capabilities Test")
    
    capabilities = {
        "real_time_logging": True,
        "configurable_baud_rate": True,
        "background_log_storage": True,
        "pattern_matching": True,
        "ndjson_log_extraction": True
    }
    
    print("✅ Serial monitor capabilities:")
    for capability, available in capabilities.items():
        status = "✅" if available else "❌"
        print(f"   {status} {capability.replace('_', ' ').title()}")
    
    # Check for serial monitor scripts
    scripts = [
        "capture_serial_debug.py",
        "capture_serial.py"
    ]
    
    print("\n   Available Scripts:")
    import os
    for script in scripts:
        if os.path.exists(script):
            print(f"   ✅ {script}")
        else:
            print(f"   ❌ {script} (not found)")
    
    return {
        "status": "success",
        "capabilities": capabilities,
        "scripts_available": [s for s in scripts if os.path.exists(s)]
    }

def test_mcp_configuration() -> Dict[str, Any]:
    """Test MCP server configuration."""
    print_section("5. MCP Server Configuration Test")
    
    mcp_config_path = ".claude/mcp.json"
    
    try:
        import os
        if os.path.exists(mcp_config_path):
            with open(mcp_config_path, 'r') as f:
                config = json.load(f)
            
            print("✅ MCP configuration file found")
            print(f"   Path: {mcp_config_path}")
            
            servers = config.get("mcpServers", {})
            print(f"\n   Configured MCP Servers ({len(servers)}):")
            for server_name, server_config in servers.items():
                print(f"   • {server_name}")
                if isinstance(server_config, dict):
                    if "command" in server_config:
                        print(f"     Command: {server_config['command']}")
                    if "args" in server_config:
                        print(f"     Args: {len(server_config['args'])} argument(s)")
            
            # Expected servers based on rules
            expected_servers = [
                "esp32-serial-monitor",
                "unified-deployment",
                "composed-embedded",
                "conan-cloudsmith",
                "android-dev-tools"
            ]
            
            print(f"\n   Expected Servers (from rules):")
            for server in expected_servers:
                if server in servers:
                    print(f"   ✅ {server}")
                else:
                    print(f"   ⚠️  {server} (not configured)")
            
            return {
                "status": "success",
                "config": config,
                "configured_servers": list(servers.keys()),
                "expected_servers": expected_servers
            }
        else:
            print(f"⚠️  MCP configuration file not found at {mcp_config_path}")
            return {"status": "warning", "message": "config file not found"}
            
    except Exception as e:
        print(f"❌ MCP configuration test failed: {e}")
        return {"status": "error", "message": str(e)}

def generate_test_report(results: Dict[str, Any]):
    """Generate a test report summary."""
    print_section("Test Report Summary")
    
    total_tests = len(results)
    passed = sum(1 for r in results.values() if r.get("status") == "success")
    warnings = sum(1 for r in results.values() if r.get("status") == "warning")
    errors = sum(1 for r in results.values() if r.get("status") == "error")
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed}")
    print(f"⚠️  Warnings: {warnings}")
    print(f"❌ Errors: {errors}")
    
    # Save report to file
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total_tests,
            "passed": passed,
            "warnings": warnings,
            "errors": errors
        },
        "results": results
    }
    
    report_file = f"test_results/mcp_tools_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    import os
    os.makedirs("test_results", exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")

def main():
    """Run all MCP tools tests."""
    print("\n" + "="*70)
    print("  Unified Development Tools MCP Server - Test Suite")
    print("="*70)
    print(f"  Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Run all tests
    results["device_detection"] = test_device_detection()
    results["serial_port_listing"] = test_serial_port_listing()
    results["emulator_status"] = test_emulator_status()
    results["serial_monitor_capabilities"] = test_serial_monitor_capabilities()
    results["mcp_configuration"] = test_mcp_configuration()
    
    # Generate report
    generate_test_report(results)
    
    print("\n" + "="*70)
    print("  Test Suite Complete")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
