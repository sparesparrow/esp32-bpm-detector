#!/usr/bin/env python3
"""
Simple ESP32 Port Detection Script

For advanced device detection with JSON output, see scripts/detect_devices.py
"""
import serial.tools.list_ports
import sys
import json
import argparse

def detect_ports(json_output=False):
    """Detect ESP32-compatible ports."""
    ports = serial.tools.list_ports.comports()
    
    if not json_output:
        print("Detecting ESP32 ports...")
        print()
        print(f"Found {len(ports)} serial ports:")
        for port in ports:
            print(f"  {port.device}: {port.description} [{port.hwid}]")
        print()
        print("ESP32-compatible ports (based on description):")
    
    esp32_ports = []
    for port in ports:
        if any(keyword in port.description.upper() for keyword in ['USB', 'SERIAL', 'CH340', 'CP210', 'FTDI', 'SILABS', 'ESP32']):
            esp32_ports.append(port)
            if not json_output:
                print(f"  ✓ {port.device}: {port.description}")
    
    if not esp32_ports and not json_output:
        print("  No ESP32-compatible ports found by description")
        print()
        print("Trying common ESP32 port names:")
        
        # Try common ports
        common_ports = ['/dev/ttyUSB0', '/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyS0']
        for port_name in common_ports:
            try:
                s = serial.Serial(port_name, 115200, timeout=1)
                s.close()
                print(f"  ✓ {port_name}: Available and responsive")
            except:
                print(f"  ✗ {port_name}: Not available")
    
    if json_output:
        # Output structured JSON
        devices = []
        for port in esp32_ports:
            devices.append({
                "device": port.device,
                "description": port.description,
                "hwid": port.hwid
            })
        print(json.dumps({"ports": devices}, indent=2))
    else:
        print()
        if esp32_ports:
            print(f"Recommended ESP32 port(s): {', '.join([p.device for p in esp32_ports])}")
        else:
            print("No ESP32 ports detected. Make sure your ESP32 is connected and drivers are installed.")
    
    return esp32_ports

def main():
    parser = argparse.ArgumentParser(description="Detect ESP32-compatible serial ports")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()
    
    ports = detect_ports(json_output=args.json)
    sys.exit(0 if ports else 1)

if __name__ == "__main__":
    main()