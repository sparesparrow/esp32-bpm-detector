#!/usr/bin/env python3
"""
Enhanced Device Detection Script for ESP32 BPM Detector

This script:
1. Detects all connected USB serial devices
2. Identifies device types by USB VID:PID and descriptions
3. Maps devices to PlatformIO environments and Conan profiles
4. Generates device manifest JSON for multi-device deployment
"""

import serial.tools.list_ports
import json
import sys
from typing import List, Dict, Any

# USB VID:PID mappings for common USB-serial chips
USB_CHIP_PATTERNS = {
    'CH340': ['1A86:7523', '1A86:5523'],  # CH340/CH341 USB-Serial
    'CP210x': ['10C4:EA60'],  # Silicon Labs CP2102/CP2104
    'FTDI': ['0403:6001', '0403:6015'],  # FTDI FT232/FT231X
    'CDC_ACM': []  # Native USB CDC ACM (ESP32-S3 USB OTG)
}

# Keywords to identify device types from descriptions
ESP32_S3_KEYWORDS = ['ESP32-S3', 'ESP32S3', 'USB JTAG', 'JTAG/serial debug']
ESP32_KEYWORDS = ['CH340', 'CH341', 'CP210', 'UART', 'USB-SERIAL']
ARDUINO_KEYWORDS = ['ARDUINO', 'UNO', 'NANO', 'FT232', 'FTDI']

def get_vid_pid(port) -> str:
    """Extract VID:PID from port hardware ID."""
    hwid = port.hwid
    if 'VID:PID=' in hwid.upper():
        # Format: USB VID:PID=1A86:7523
        parts = hwid.upper().split('VID:PID=')
        if len(parts) > 1:
            vid_pid = parts[1].split()[0]
            return vid_pid
    return ""

def identify_device_type(port) -> Dict[str, Any]:
    """Identify device type and configuration based on port information."""
    description = port.description.upper()
    vid_pid = get_vid_pid(port)
    
    # Check for ESP32-S3 (usually CDC ACM or JTAG)
    if any(keyword in description for keyword in ESP32_S3_KEYWORDS):
        if 'JTAG' in description:
            return {
                "port": port.device,
                "type": "esp32s3_jtag",
                "description": port.description,
                "vid_pid": vid_pid,
                "is_jtag": True
            }
        else:
            return {
                "port": port.device,
                "type": "esp32s3",
                "description": port.description,
                "pio_env": "esp32s3",
                "conan_profile": "esp32s3",
                "baud_rate": 115200,
                "vid_pid": vid_pid,
                "is_jtag": False
            }
    
    # Check for generic ESP32 (usually CH340 or CP210x)
    if any(keyword in description for keyword in ESP32_KEYWORDS) or \
       any(vid_pid in patterns for patterns in [USB_CHIP_PATTERNS['CH340'], USB_CHIP_PATTERNS['CP210x']] for vid_pid_pattern in patterns if vid_pid == vid_pid_pattern):
        return {
            "port": port.device,
            "type": "esp32",
            "description": port.description,
            "pio_env": "esp32dev-release",
            "conan_profile": "esp32",
            "baud_rate": 115200,
            "vid_pid": vid_pid,
            "is_jtag": False
        }
    
    # Check for Arduino Uno
    if any(keyword in description for keyword in ARDUINO_KEYWORDS):
        return {
            "port": port.device,
            "type": "arduino_uno",
            "description": port.description,
            "pio_env": "arduino_uno",
            "conan_profile": "arduino_uno",
            "baud_rate": 9600,
            "vid_pid": vid_pid,
            "is_jtag": False
        }
    
    # Unknown device
    return {
        "port": port.device,
        "type": "unknown",
        "description": port.description,
        "vid_pid": vid_pid,
        "is_jtag": False
    }

def detect_all_devices() -> Dict[str, Any]:
    """Detect all connected devices and generate device manifest."""
    ports = serial.tools.list_ports.comports()
    
    devices = []
    jtag_devices = []
    
    for port in ports:
        device_info = identify_device_type(port)
        
        if device_info.get("is_jtag"):
            # JTAG device
            jtag_devices.append({
                "port": device_info["port"],
                "type": device_info["type"],
                "description": device_info["description"]
            })
        elif device_info["type"] != "unknown":
            # Regular programmable device
            devices.append({
                "port": device_info["port"],
                "type": device_info["type"],
                "description": device_info["description"],
                "pio_env": device_info.get("pio_env", ""),
                "conan_profile": device_info.get("conan_profile", ""),
                "baud_rate": device_info.get("baud_rate", 115200)
            })
    
    manifest = {
        "devices": devices,
        "jtag_devices": jtag_devices
    }
    
    return manifest

def print_manifest(manifest: Dict[str, Any]):
    """Print device manifest in human-readable format."""
    print("\n" + "="*60)
    print("ESP32 BPM Detector - Device Detection")
    print("="*60)
    
    devices = manifest.get("devices", [])
    jtag_devices = manifest.get("jtag_devices", [])
    
    if devices:
        print(f"\n📱 Found {len(devices)} programmable device(s):")
        for i, device in enumerate(devices, 1):
            print(f"\n  {i}. {device['type'].upper()}")
            print(f"     Port: {device['port']}")
            print(f"     Description: {device['description']}")
            print(f"     PIO Environment: {device['pio_env']}")
            print(f"     Conan Profile: {device['conan_profile']}")
            print(f"     Baud Rate: {device['baud_rate']}")
    else:
        print("\n❌ No programmable devices detected")
    
    if jtag_devices:
        print(f"\n🔧 Found {len(jtag_devices)} JTAG device(s):")
        for i, device in enumerate(jtag_devices, 1):
            print(f"\n  {i}. {device['type'].upper()}")
            print(f"     Port: {device['port']}")
            print(f"     Description: {device['description']}")
    
    print("\n" + "="*60)

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Detect connected devices for ESP32 BPM Detector deployment"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output only JSON (no human-readable format)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Write JSON output to file"
    )
    
    args = parser.parse_args()
    
    # Detect devices
    manifest = detect_all_devices()
    
    # Print human-readable output (unless --json is specified)
    if not args.json:
        print_manifest(manifest)
    
    # Print or save JSON output
    json_output = json.dumps(manifest, indent=2)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(json_output)
        if not args.json:
            print(f"\n✅ Device manifest saved to: {args.output}")
    else:
        if args.json:
            print(json_output)
        else:
            print("\nJSON Output:")
            print(json_output)
    
    # Exit with status
    if not manifest.get("devices"):
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
