#!/usr/bin/env python3
"""
PlatformIO pre-build script to install Conan dependencies for ESP32 BPM Detector.

This script runs `conan install` to set up the FlatBuffers and other dependencies
from the SpareTools ecosystem before the PlatformIO build process.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import SpareTools utilities
from sparetools_utils import (
    setup_logging,
    run_command,
    get_project_root,
    Conan
)

# Set up logging
logger = setup_logging(__name__)

def run_conan_install(profile=None):
    """Run conan install to set up dependencies using SpareTools utilities."""

    # Get the project root directory using SpareTools utilities
    project_dir = get_project_root(Path(__file__).parent)

    logger.info(f"Installing Conan dependencies for profile: {profile or 'default'}...")

    # Use SpareTools Conan utilities
    success = Conan.install_dependencies(
        profile=profile,
        build_missing=True,
        remote="sparetools"
    )

    if success:
        logger.info("Conan dependencies installed successfully!")

        # Copy headers to local include directory for PlatformIO
        logger.info("Setting up headers for PlatformIO...")
        setup_platformio_headers(str(project_dir), profile=profile)
        return True
    else:
        logger.error("Failed to install Conan dependencies")
        return False

def setup_platformio_headers(project_dir, profile=None):
    """Copy Conan-generated headers to a location PlatformIO can find."""
    import shutil

    # Create profile-specific header directory
    profile_suffix = f"-{profile}" if profile else ""
    headers_dir = os.path.join(project_dir, f"conan-headers{profile_suffix}")
    if os.path.exists(headers_dir):
        shutil.rmtree(headers_dir)
    os.makedirs(headers_dir, exist_ok=True)
    
    print(f"Headers directory: {headers_dir}")

    # Create firmware directory for ESP32-Bus-Pirate binaries
    firmware_dir = os.path.join(project_dir, "firmware")
    if os.path.exists(firmware_dir):
        shutil.rmtree(firmware_dir)
    os.makedirs(firmware_dir, exist_ok=True)

    # Find and copy sparesparrow-protocols headers
    try:
        # Get package binary location (with hash)
        result = subprocess.run(["conan", "cache", "path", "sparesparrow-protocols/1.0.0:da39a3ee5e6b4b0d3255bfef95601890afd80709"], capture_output=True, text=True, check=True)
        package_path = result.stdout.strip()

        # Copy headers
        package_include = os.path.join(package_path, "include")
        if os.path.exists(package_include):
            for root, dirs, files in os.walk(package_include):
                for file in files:
                    if file.endswith('.h') or file.endswith('.hpp'):
                        src_path = os.path.join(root, file)
                        dst_path = os.path.join(headers_dir, file)
                        shutil.copy2(src_path, dst_path)
                        print(f"Copied {file} to conan-headers/")

        # Copy all FlatBuffers headers to maintain include structure
        try:
            fb_result = subprocess.run(["conan", "cache", "path", "flatbuffers/24.3.25:ceee6f52859bf4ffff875565704211b59af2886f"], capture_output=True, text=True, check=True)
            fb_path = fb_result.stdout.strip()
            fb_include = os.path.join(fb_path, "include", "flatbuffers")
            if os.path.exists(fb_include):
                fb_headers_dir = os.path.join(headers_dir, "flatbuffers")
                if os.path.exists(fb_headers_dir):
                    shutil.rmtree(fb_headers_dir)
                os.makedirs(fb_headers_dir, exist_ok=True)
                # Copy all files from flatbuffers include directory
                for item in os.listdir(fb_include):
                    src_path = os.path.join(fb_include, item)
                    dst_path = os.path.join(fb_headers_dir, item)
                    if os.path.isdir(src_path):
                        shutil.copytree(src_path, dst_path)
                    else:
                        shutil.copy2(src_path, dst_path)
                print("Copied all FlatBuffers headers to conan-headers/flatbuffers/")
        except subprocess.CalledProcessError:
            print("Warning: Could not copy FlatBuffers headers")

        # Extract ESP32-Bus-Pirate firmware binaries
        try:
            bp_result = subprocess.run(["conan", "cache", "path", "esp32-bus-pirate/1.0.0"], capture_output=True, text=True, check=True)
            bp_path = bp_result.stdout.strip()
            bp_firmware_src = os.path.join(bp_path, "firmware")

            if os.path.exists(bp_firmware_src):
                print("Extracting ESP32-Bus-Pirate firmware binaries...")
                for item in os.listdir(bp_firmware_src):
                    src_path = os.path.join(bp_firmware_src, item)
                    dst_path = os.path.join(firmware_dir, item)
                    if os.path.isfile(src_path):
                        shutil.copy2(src_path, dst_path)
                        print(f"Extracted firmware: {item}")
                print(f"ESP32-Bus-Pirate firmware binaries available in {firmware_dir}/")
            else:
                print("Warning: ESP32-Bus-Pirate firmware directory not found")
        except subprocess.CalledProcessError:
            print("Warning: Could not extract ESP32-Bus-Pirate firmware binaries")

        print(f"Headers set up in {headers_dir}/")
        print(f"Firmware binaries available in {firmware_dir}/")

    except subprocess.CalledProcessError:
        print("Warning: Could not copy Conan headers, build may fail")
    except Exception as e:
        print(f"Warning: Error setting up headers: {e}")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Install Conan dependencies")
    parser.add_argument("--profile", help="Conan profile to use (esp32s3, esp32, arduino_uno)", default=None)
    args = parser.parse_args()
    
    print("ESP32 BPM Detector - Conan Dependency Setup")
    print("=" * 50)

    success = run_conan_install(profile=args.profile)

    if success:
        print("✅ Conan dependencies ready for PlatformIO build")
        sys.exit(0)
    else:
        print("❌ Failed to install Conan dependencies")
        print("Please check your Conan installation and network connectivity")
        sys.exit(1)

if __name__ == "__main__":
    main()
