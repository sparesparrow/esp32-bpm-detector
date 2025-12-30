#!/usr/bin/env python3
"""
JTAG-Based Deployment Script for ESP32-S3

This script deploys firmware to ESP32-S3 via JTAG interface using OpenOCD.
It enables debug symbols and provides options for starting GDB debugging sessions.

Features:
- Flash firmware via JTAG (faster than serial for repeated uploads)
- Enable debug symbols for GDB debugging
- Automatic OpenOCD connection to ESP32-S3 built-in USB JTAG
- Optional GDB remote debugging session
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import time

def check_openocd():
    """Check if OpenOCD is installed and has ESP32 support."""
    try:
        result = subprocess.run(
            ["openocd", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ OpenOCD found: {result.stdout.split()[3]}")
            return True
        else:
            print("❌ OpenOCD not found or not working")
            return False
    except FileNotFoundError:
        print("❌ OpenOCD not installed")
        print("Install with: sudo apt install openocd")
        return False
    except subprocess.TimeoutExpired:
        print("❌ OpenOCD check timed out")
        return False

def check_jtag_device():
    """Check if ESP32-S3 JTAG device is connected."""
    try:
        result = subprocess.run(
            ["lsusb"],
            capture_output=True,
            text=True
        )
        # ESP32-S3 USB JTAG VID:PID = 303a:1001
        if "303a:1001" in result.stdout:
            print("✅ ESP32-S3 JTAG device detected")
            return True
        else:
            print("❌ ESP32-S3 JTAG device not found")
            print("Make sure ESP32-S3 is connected via USB")
            return False
    except FileNotFoundError:
        print("⚠️  lsusb not found, skipping JTAG device check")
        return True  # Assume device is present

def build_debug_firmware(project_dir, env="esp32s3"):
    """Build firmware with debug symbols enabled."""
    print(f"\n{'='*60}")
    print(f"Building debug firmware for {env}")
    print(f"{'='*60}")
    
    # Build with debug flags
    cmd = [
        "pio", "run",
        "--environment", env,
        "--target", "clean"
    ]
    subprocess.run(cmd, cwd=project_dir)
    
    cmd = [
        "pio", "run",
        "--environment", env,
        "-v"  # Verbose output
    ]
    
    result = subprocess.run(cmd, cwd=project_dir)
    
    if result.returncode == 0:
        print(f"✅ Debug firmware built successfully")
        return True
    else:
        print(f"❌ Debug firmware build failed")
        return False

def flash_via_jtag(project_dir, env="esp32s3"):
    """Flash firmware to ESP32-S3 via JTAG using OpenOCD."""
    print(f"\n{'='*60}")
    print(f"Flashing firmware via JTAG")
    print(f"{'='*60}")
    
    # Find the firmware binary
    firmware_path = project_dir / ".pio" / "build" / env / "firmware.bin"
    
    if not firmware_path.exists():
        print(f"❌ Firmware binary not found: {firmware_path}")
        return False
    
    print(f"Firmware binary: {firmware_path}")
    
    # OpenOCD configuration file
    openocd_cfg = project_dir / "openocd.cfg"
    
    if not openocd_cfg.exists():
        print(f"❌ OpenOCD configuration not found: {openocd_cfg}")
        return False
    
    # Flash command for ESP32-S3
    # Note: ESP32-S3 flash starts at 0x0 for bootloader, 0x10000 for app
    openocd_cmd = [
        "openocd",
        "-f", str(openocd_cfg),
        "-c", f"program_esp {firmware_path} 0x10000 verify reset exit"
    ]
    
    print(f"Running: {' '.join(openocd_cmd)}")
    
    result = subprocess.run(openocd_cmd, cwd=project_dir)
    
    if result.returncode == 0:
        print(f"✅ Firmware flashed successfully via JTAG")
        return True
    else:
        print(f"❌ JTAG flash failed")
        return False

def start_openocd_server(project_dir):
    """Start OpenOCD server in background for GDB connection."""
    print(f"\n{'='*60}")
    print("Starting OpenOCD server for GDB")
    print(f"{'='*60}")
    
    openocd_cfg = project_dir / "openocd.cfg"
    
    openocd_cmd = [
        "openocd",
        "-f", str(openocd_cfg)
    ]
    
    print(f"Running: {' '.join(openocd_cmd)}")
    print("OpenOCD will listen on localhost:3333 for GDB connections")
    print("Press Ctrl+C to stop OpenOCD server")
    print("")
    
    try:
        subprocess.run(openocd_cmd, cwd=project_dir)
    except KeyboardInterrupt:
        print("\n✅ OpenOCD server stopped")

def start_gdb_session(project_dir, env="esp32s3"):
    """Start GDB debugging session."""
    print(f"\n{'='*60}")
    print("Starting GDB debugging session")
    print(f"{'='*60}")
    
    # Find the ELF file with debug symbols
    elf_path = project_dir / ".pio" / "build" / env / "firmware.elf"
    
    if not elf_path.exists():
        print(f"❌ ELF file not found: {elf_path}")
        return False
    
    print(f"ELF file: {elf_path}")
    
    # Start GDB
    gdb_cmd = [
        "xtensa-esp32s3-elf-gdb",
        str(elf_path),
        "-ex", "target remote :3333",
        "-ex", "monitor reset halt",
        "-ex", "flushregs",
        "-ex", "thb app_main",
        "-ex", "continue"
    ]
    
    print(f"Running: {' '.join(gdb_cmd)}")
    print("")
    
    try:
        subprocess.run(gdb_cmd, cwd=project_dir)
    except KeyboardInterrupt:
        print("\n✅ GDB session ended")
    except FileNotFoundError:
        print("❌ GDB not found. Install ESP32 toolchain:")
        print("   pio platform install espressif32")

def main():
    """Main entry point for JTAG deployment."""
    parser = argparse.ArgumentParser(
        description="Deploy ESP32-S3 firmware via JTAG with debugging support"
    )
    parser.add_argument(
        "--device",
        default="esp32s3",
        help="Device type (default: esp32s3)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Start GDB debugging session after flashing"
    )
    parser.add_argument(
        "--openocd-only",
        action="store_true",
        help="Start OpenOCD server only (no flashing)"
    )
    parser.add_argument(
        "--gdb-only",
        action="store_true",
        help="Start GDB session only (assume firmware already flashed)"
    )
    parser.add_argument(
        "--build-only",
        action="store_true",
        help="Build debug firmware only (no flashing)"
    )
    
    args = parser.parse_args()
    
    # Get project directory
    project_dir = Path(__file__).parent.parent
    
    print("ESP32 BPM Detector - JTAG Deployment")
    print("=" * 60)
    
    # Check prerequisites
    if not args.gdb_only:
        if not check_openocd():
            sys.exit(1)
        
        if not check_jtag_device():
            sys.exit(1)
    
    # OpenOCD-only mode
    if args.openocd_only:
        start_openocd_server(project_dir)
        sys.exit(0)
    
    # GDB-only mode
    if args.gdb_only:
        start_gdb_session(project_dir, env=args.device)
        sys.exit(0)
    
    # Build debug firmware
    if not build_debug_firmware(project_dir, env=args.device):
        print("❌ Build failed, aborting")
        sys.exit(1)
    
    if args.build_only:
        print("✅ Build complete (build-only mode)")
        sys.exit(0)
    
    # Flash via JTAG
    if not flash_via_jtag(project_dir, env=args.device):
        print("❌ Flash failed, aborting")
        sys.exit(1)
    
    # Start debugging session if requested
    if args.debug:
        print("\nStarting OpenOCD server in 3 seconds...")
        time.sleep(3)
        
        # Start OpenOCD in background
        import threading
        openocd_thread = threading.Thread(
            target=start_openocd_server,
            args=(project_dir,),
            daemon=True
        )
        openocd_thread.start()
        
        # Wait for OpenOCD to start
        time.sleep(2)
        
        # Start GDB
        start_gdb_session(project_dir, env=args.device)
    
    print("\n✅ JTAG deployment complete")
    sys.exit(0)

if __name__ == "__main__":
    main()
