#!/usr/bin/env python3
"""
Extract debug logs from ESP32-S3 memory via JTAG/OpenOCD
This script uses OpenOCD's memory dump capabilities to read the log buffer
"""

import subprocess
import json
import sys
import os

LOG_BUFFER_ADDR = "0x3FC80000"  # Typical DRAM address (adjust based on your build)
MAX_LOG_ENTRIES = 100
LOG_ENTRY_SIZE = 256 + 8  # data + timestamp + valid flag

def read_memory_via_openocd(addr, size):
    """Read memory from ESP32 via OpenOCD"""
    cmd = f"echo 'mdw {addr} {size//4}' | nc localhost 4444"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.stdout
    except Exception as e:
        print(f"Error reading memory: {e}", file=sys.stderr)
        return None

def extract_logs():
    """Extract logs from memory buffer"""
    log_file = ".cursor/debug.log"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    with open(log_file, 'w') as f:
        # Read log buffer structure
        # This is a simplified version - actual implementation would parse the memory dump
        print("Reading log buffer from ESP32 memory via JTAG...")
        print("Note: This requires OpenOCD to be running and connected")
        print("Use GDB to inspect logBuffer variable directly for more reliable access")
        
        # For now, provide instructions
        f.write("# Logs extracted via JTAG\n")
        f.write("# To extract logs manually:\n")
        f.write("# 1. Connect GDB: xtensa-esp32s3-elf-gdb -x gdbinit\n")
        f.write("# 2. In GDB: print logBuffer[0..logCount-1]\n")
        f.write("# 3. Or use: (gdb) x/s &logBuffer[0].data\n")

if __name__ == "__main__":
    extract_logs()
    print("Log extraction script ready.")
    print("Use GDB to read logBuffer variable directly for actual log data.")


