#!/usr/bin/env python3
"""
Multi-Device Deployment Script for ESP32 BPM Detector

This script:
1. Detects all connected devices
2. Builds firmware for each device type using appropriate Conan profiles
3. Deploys firmware to all devices sequentially or in parallel
4. Monitors deployment status and provides detailed logs
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import device detection
sys.path.insert(0, str(Path(__file__).parent))
from detect_devices import detect_all_devices

def build_for_profile(profile_name, project_dir):
    """Build firmware using specified Conan profile."""
    print(f"\n{'='*60}")
    print(f"Building for profile: {profile_name}")
    print(f"{'='*60}")
    
    # Step 1: Run Conan install with profile
    conan_cmd = [
        sys.executable,
        str(project_dir / "scripts" / "conan_install.py"),
        "--profile", profile_name
    ]
    
    result = subprocess.run(conan_cmd, cwd=project_dir)
    if result.returncode != 0:
        print(f"❌ Conan install failed for profile: {profile_name}")
        return False
    
    # Step 2: Run PlatformIO build for corresponding environment
    # Map profile to PlatformIO environment
    profile_to_env = {
        "esp32s3": "esp32s3",
        "esp32": "esp32dev-release",
        "arduino_uno": "arduino_uno"
    }
    
    pio_env = profile_to_env.get(profile_name)
    if not pio_env:
        print(f"❌ Unknown profile: {profile_name}")
        return False
    
    pio_cmd = ["pio", "run", "--environment", pio_env]
    result = subprocess.run(pio_cmd, cwd=project_dir)
    
    if result.returncode == 0:
        print(f"✅ Build successful for {profile_name}")
        return True
    else:
        print(f"❌ Build failed for {profile_name}")
        return False

def upload_to_device(device_info, project_dir):
    """Upload firmware to a specific device."""
    print(f"\n{'='*60}")
    print(f"Uploading to {device_info['type']} on {device_info['port']}")
    print(f"{'='*60}")
    
    pio_cmd = [
        "pio", "run",
        "--environment", device_info["pio_env"],
        "--target", "upload",
        "--upload-port", device_info["port"]
    ]
    
    result = subprocess.run(pio_cmd, cwd=project_dir)
    
    if result.returncode == 0:
        print(f"✅ Upload successful to {device_info['port']}")
        return True
    else:
        print(f"❌ Upload failed to {device_info['port']}")
        return False

def monitor_device(device_info, duration=10):
    """Monitor serial output from device for specified duration."""
    print(f"\n{'='*60}")
    print(f"Monitoring {device_info['type']} on {device_info['port']} for {duration}s")
    print(f"{'='*60}")
    
    pio_cmd = [
        "pio", "device", "monitor",
        "--port", device_info["port"],
        "--baud", str(device_info["baud_rate"]),
        "--filter", "default",
        "--echo"
    ]
    
    try:
        subprocess.run(pio_cmd, timeout=duration)
    except subprocess.TimeoutExpired:
        pass  # Expected - we're just sampling output

def deploy_sequential(devices, project_dir, args):
    """Deploy to all devices sequentially."""
    print(f"\n🚀 Starting SEQUENTIAL deployment to {len(devices)} device(s)")
    
    # Build firmware for each unique profile
    unique_profiles = list(set(d["conan_profile"] for d in devices))
    build_results = {}
    
    for profile in unique_profiles:
        build_results[profile] = build_for_profile(profile, project_dir)
    
    # Upload to each device
    upload_results = []
    for device in devices:
        if not build_results[device["conan_profile"]]:
            print(f"⏭️  Skipping {device['port']} - build failed")
            upload_results.append(False)
            continue
        
        success = upload_to_device(device, project_dir)
        upload_results.append(success)
        
        if success and args.monitor:
            monitor_device(device, duration=args.monitor_duration)
    
    return upload_results

def deploy_parallel(devices, project_dir, args):
    """Deploy to all devices in parallel."""
    print(f"\n🚀 Starting PARALLEL deployment to {len(devices)} device(s)")
    
    # Build firmware for each unique profile (still sequential - shared resources)
    unique_profiles = list(set(d["conan_profile"] for d in devices))
    build_results = {}
    
    for profile in unique_profiles:
        build_results[profile] = build_for_profile(profile, project_dir)
    
    # Upload to devices in parallel
    upload_results = []
    with ThreadPoolExecutor(max_workers=len(devices)) as executor:
        futures = []
        for device in devices:
            if not build_results[device["conan_profile"]]:
                print(f"⏭️  Skipping {device['port']} - build failed")
                upload_results.append(False)
                continue
            
            future = executor.submit(upload_to_device, device, project_dir)
            futures.append((future, device))
        
        for future, device in futures:
            success = future.result()
            upload_results.append(success)
    
    return upload_results

def main():
    """Main deployment orchestration."""
    parser = argparse.ArgumentParser(
        description="Deploy BPM detector firmware to multiple devices"
    )
    parser.add_argument(
        "--mode",
        choices=["sequential", "parallel"],
        default="sequential",
        help="Deployment mode (default: sequential)"
    )
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Monitor serial output after upload"
    )
    parser.add_argument(
        "--monitor-duration",
        type=int,
        default=10,
        help="Duration to monitor each device in seconds (default: 10)"
    )
    parser.add_argument(
        "--filter",
        nargs="+",
        help="Filter devices by type (e.g., esp32s3 arduino_uno)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deployed without actually deploying"
    )
    
    args = parser.parse_args()
    
    # Get project directory
    project_dir = Path(__file__).parent.parent
    
    print("ESP32 BPM Detector - Multi-Device Deployment")
    print("=" * 60)
    
    # Detect all devices
    print("\n🔍 Detecting connected devices...")
    device_manifest = detect_all_devices()
    
    if not device_manifest or not device_manifest.get("devices"):
        print("❌ No devices detected. Please connect devices and try again.")
        sys.exit(1)
    
    devices = device_manifest["devices"]
    
    # Apply filters if specified
    if args.filter:
        devices = [d for d in devices if d["type"] in args.filter]
        print(f"\n🔍 Filtered to {len(devices)} device(s): {args.filter}")
    
    # Display detected devices
    print(f"\n📱 Found {len(devices)} device(s):")
    for i, device in enumerate(devices, 1):
        print(f"  {i}. {device['type']} on {device['port']}")
        print(f"     PIO env: {device['pio_env']}, Conan profile: {device['conan_profile']}")
    
    if device_manifest.get("jtag_devices"):
        print(f"\n🔧 Found {len(device_manifest['jtag_devices'])} JTAG device(s):")
        for jtag in device_manifest["jtag_devices"]:
            print(f"  - {jtag['type']} on {jtag['port']}")
    
    if args.dry_run:
        print("\n🔍 DRY RUN - No actual deployment will occur")
        sys.exit(0)
    
    # Confirm deployment
    response = input("\n⚠️  Proceed with deployment? (yes/no): ")
    if response.lower() not in ["yes", "y"]:
        print("Deployment cancelled.")
        sys.exit(0)
    
    # Deploy based on mode
    if args.mode == "parallel":
        results = deploy_parallel(devices, project_dir, args)
    else:
        results = deploy_sequential(devices, project_dir, args)
    
    # Summary
    print(f"\n{'='*60}")
    print("DEPLOYMENT SUMMARY")
    print(f"{'='*60}")
    
    success_count = sum(1 for r in results if r)
    total_count = len(results)
    
    for i, (device, result) in enumerate(zip(devices, results), 1):
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"{i}. {device['type']} ({device['port']}): {status}")
    
    print(f"\n{success_count}/{total_count} devices deployed successfully")
    
    if success_count == total_count:
        print("✅ All devices deployed successfully!")
        sys.exit(0)
    else:
        print("⚠️  Some devices failed to deploy")
        sys.exit(1)

if __name__ == "__main__":
    main()
