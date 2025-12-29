#!/usr/bin/env python3
import serial.tools.list_ports
import sys

print("Detecting ESP32 ports...")
print()

# List all available ports
ports = serial.tools.list_ports.comports()

print(f"Found {len(ports)} serial ports:")
for port in ports:
    print(f"  {port.device}: {port.description} [{port.hwid}]")

print()
print("ESP32-compatible ports (based on description):")

esp32_ports = []
for port in ports:
    if any(keyword in port.description.upper() for keyword in ['USB', 'SERIAL', 'CH340', 'CP210', 'FTDI', 'SILABS']):
        esp32_ports.append(port)
        print(f"  ✓ {port.device}: {port.description}")

if not esp32_ports:
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

print()
if esp32_ports:
    print(f"Recommended ESP32 port(s): {', '.join([p.device for p in esp32_ports])}")
else:
    print("No ESP32 ports detected. Make sure your ESP32 is connected and drivers are installed.")