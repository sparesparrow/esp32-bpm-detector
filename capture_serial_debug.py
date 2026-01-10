#!/usr/bin/env python3
"""
Capture Serial output from ESP32 and extract NDJSON debug logs
"""
import serial
import sys
import re
from datetime import datetime

LOG_FILE = "/home/sparrow/projects/.cursor/debug.log"
SERIAL_PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
BAUD_RATE = int(sys.argv[2]) if len(sys.argv) > 2 else 115200

# Pattern to match NDJSON log lines
NDJSON_PATTERN = re.compile(r'^\{"sessionId":"debug-session".*?\}$', re.MULTILINE)

def main():
    print(f"Capturing Serial output from {SERIAL_PORT} at {BAUD_RATE} baud")
    print(f"Writing NDJSON logs to {LOG_FILE}")
    print("Press Ctrl+C to stop")
    print("")
    
    # Clear the log file
    with open(LOG_FILE, 'w') as f:
        f.write("")
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to {SERIAL_PORT}")
        print("")
        
        buffer = ""
        log_count = 0
        
        with open(LOG_FILE, 'a') as log_file:
            while True:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                    buffer += data
                    
                    # Print all output to console for visibility
                    print(data, end='', flush=True)
                    
                    # Extract complete NDJSON lines
                    lines = buffer.split('\n')
                    buffer = lines[-1]  # Keep incomplete line in buffer
                    
                    for line in lines[:-1]:
                        line = line.strip()
                        if line:
                            # Check if it's an NDJSON log line
                            if NDJSON_PATTERN.match(line):
                                log_file.write(line + '\n')
                                log_file.flush()
                                log_count += 1
                                if log_count % 10 == 0:
                                    print(f"\n[Captured {log_count} log entries]", flush=True)
                else:
                    import time
                    time.sleep(0.01)  # Small delay to avoid busy waiting
                    
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        print(f"Available ports:")
        import serial.tools.list_ports
        for port in serial.tools.list_ports.comports():
            print(f"  {port.device}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n\nCapture stopped. Total log entries: {log_count}")
        print(f"Logs written to: {LOG_FILE}")
    finally:
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    main()


