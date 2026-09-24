#!/usr/bin/env python3
"""Verify ESP32 device is running and responsive."""
import serial
import time
import sys

try:
    # Open serial connection to ESP32
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=2)
    print("✓ Serial connection established on /dev/ttyACM0")
    
    # Clear any existing data
    ser.reset_input_buffer()
    time.sleep(0.5)
    
    # Read startup messages
    print("\n--- Capturing startup messages (5 seconds) ---")
    start_time = time.time()
    startup_msgs = []
    
    while time.time() - start_time < 5:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(line)
                startup_msgs.append(line)
    
    # Verify device is responsive
    if startup_msgs:
        print("\n✓ Device is responsive and producing output")
        if any('BPM' in msg or 'detect' in msg.lower() for msg in startup_msgs):
            print("✓ BPM detection system is active")
        if any('ERROR' in msg or 'FAIL' in msg for msg in startup_msgs):
            print("⚠ Warnings/Errors detected in startup")
        else:
            print("✓ No errors in startup sequence")
    else:
        print("\n⚠ No startup messages received")
    
    ser.close()
    print("\n✓ Device verification complete")
    sys.exit(0)
    
except serial.SerialException as e:
    print(f"✗ Serial error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
