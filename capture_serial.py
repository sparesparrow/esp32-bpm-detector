#!/usr/bin/env python3
import serial
import serial.tools.list_ports
import time
import json
import sys
import os

LOG_FILE = ".cursor/debug.log"

# Find ESP32 port
ports = serial.tools.list_ports.comports()
esp32_port = None
for port in ports:
    if 'USB' in port.description or 'Serial' in port.description or 'CH340' in port.description or 'CP210' in port.description:
        esp32_port = port.device
        break

if not esp32_port:
    # Try common ports
    for port_name in ['/dev/ttyUSB0', '/dev/ttyACM0', '/dev/ttyS0']:
        try:
            s = serial.Serial(port_name, 115200, timeout=1)
            s.close()
            esp32_port = port_name
            break
        except:
            pass

if not esp32_port:
    print("Error: Could not find ESP32 serial port", file=sys.stderr)
    sys.exit(1)

print(f"Reading from {esp32_port}...", file=sys.stderr)
print(f"Writing logs to {LOG_FILE}...", file=sys.stderr)

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
with open(LOG_FILE, 'w') as log_file:
    try:
        ser = serial.Serial(esp32_port, 115200, timeout=1)
        start_time = time.time()
        while time.time() - start_time < 10:  # Run for 10 seconds
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(line)  # Also print to stdout
                    # Check if it's a JSON log entry
                    if line.startswith('{') and 'sessionId' in line:
                        log_file.write(line + '\n')
                        log_file.flush()
            time.sleep(0.01)
        ser.close()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

print(f"\nCapture complete. Check {LOG_FILE}", file=sys.stderr)


