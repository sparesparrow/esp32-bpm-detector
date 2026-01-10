#!/usr/bin/env python3
"""
FlatBuffers Code Generation Script for ESP32 BPM Detector

This script generates C++ code from FlatBuffers schema files
for efficient binary serialization in the ESP32 firmware.

Uses sparetools bundled CPython if available, otherwise falls back to system Python.

Usage:
    # With sparetools bundled CPython (preferred):
    sparetools python scripts/generate_flatbuffers.py
    
    # Or set environment variable:
    export SPARETOOLS_PYTHON=~/.sparetools/bin/python
    python3 scripts/generate_flatbuffers.py
    
    # Or use system Python (fallback):
    python3 scripts/generate_flatbuffers.py
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
    get_python_command,
    is_using_bundled_python
)

# Set up logging
logger = setup_logging(__name__)

def find_python():
    """Find Python interpreter, preferring sparetools bundled CPython."""
    # Use SpareTools utilities to ensure bundled CPython
    python_cmd = get_python_command()
    
    if is_using_bundled_python():
        logger.info(f"Already using sparetools bundled CPython: {sys.executable}")
    elif python_cmd != [sys.executable]:
        logger.info(f"Using sparetools bundled CPython: {python_cmd}")
    else:
        logger.warning("Using system Python (sparetools bundled CPython not found)")
        logger.warning("To use bundled CPython: conan install sparetools-cpython/3.12.7 -r sparetools")
    
    return python_cmd

def find_flatc():
    """Find the flatc (FlatBuffers compiler) executable using SpareTools utilities"""
    # Prefer SpareTools flatc (guaranteed consistent version)
    sparetools_flatc = "flatc"

    try:
        result = run_command([sparetools_flatc, "--version"], timeout=5, check=False)
        if result.returncode == 0:
            logger.info(f"Using SpareTools flatc: {result.stdout.strip()}")
            return sparetools_flatc
    except Exception:
        pass

    # Fallback to system flatc (for compatibility)
    logger.warning("SpareTools flatc not found, falling back to system flatc")
    possible_paths = [
        "/usr/local/bin/flatc",
        "/usr/bin/flatc",
        "/opt/homebrew/bin/flatc",  # macOS
        "./flatc"  # Local directory
    ]

    for path in possible_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path

    # Try to find in PATH
    try:
        result = run_command(["which", "flatc"], check=False)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    return None

def download_flatc(python_cmd=None):
    """Download and setup flatc if not found"""
    print("flatc not found. Attempting to download...")
    
    if python_cmd is None:
        python_cmd = find_python()

    system = platform.system().lower()
    machine = platform.machine().lower()

    # Determine download URL based on platform
    if system == "linux":
        if "x86_64" in machine or "amd64" in machine:
            url = "https://github.com/google/flatbuffers/releases/latest/download/Linux.flatc.binary.clang++17.zip"
        elif "aarch64" in machine or "arm64" in machine:
            url = "https://github.com/google/flatbuffers/releases/latest/download/Linux.flatc.binary.clang++17.zip"
        else:
            print(f"Unsupported Linux architecture: {machine}")
            return False
    elif system == "darwin":  # macOS
        url = "https://github.com/google/flatbuffers/releases/latest/download/Mac.flatc.binary.zip"
    elif system == "windows":
        url = "https://github.com/google/flatbuffers/releases/latest/download/Windows.flatc.binary.zip"
    else:
        print(f"Unsupported platform: {system}")
        return False

    try:
        # Use sparetools Python if available for downloads
        import urllib.request
        import zipfile
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "flatc.zip")
            urllib.request.urlretrieve(url, zip_path)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Find the flatc binary
            for root, dirs, files in os.walk(temp_dir):
                if "flatc" in files:
                    flatc_path = os.path.join(root, "flatc")
                    # Make executable and copy to local directory
                    os.chmod(flatc_path, 0o755)
                    local_flatc = "./flatc"
                    import shutil
                    shutil.copy2(flatc_path, local_flatc)
                    os.chmod(local_flatc, 0o755)
                    print(f"Downloaded flatc to {local_flatc}")
                    return local_flatc

    except Exception as e:
        print(f"Failed to download flatc: {e}")
        return False

    return False

def generate_cpp_code(schema_file, output_dir, flatc_path):
    """Generate C++ code from FlatBuffers schema using SpareTools utilities"""
    logger.info(f"Generating C++ code from {schema_file}...")

    cmd = [
        flatc_path,
        "--cpp",
        "--gen-mutable",
        "-o", output_dir,
        schema_file
    ]

    try:
        result = run_command(cmd, check=False)
        if result.returncode == 0:
            logger.info(f"✅ Successfully generated C++ code in {output_dir}")
            return True
        else:
            logger.error(f"❌ Failed to generate code: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ Error running flatc: {e}")
        return False

def main():
    """Main code generation function"""
    # Find and use appropriate Python interpreter
    python_cmd = find_python()
    
    script_dir = Path(__file__).parent
    # Use SpareTools path utilities
    project_root = get_project_root(script_dir)

    # Schema and output directories
    schema_dir = project_root / "schemas"
    include_dir = project_root / "include"
    src_dir = project_root / "src"

    # Create output directories
    include_dir.mkdir(exist_ok=True)
    src_dir.mkdir(exist_ok=True)

    # Find flatc
    flatc_path = find_flatc()
    if not flatc_path:
        print("flatc not found, attempting to download...")
        flatc_path = download_flatc(python_cmd)
        if not flatc_path:
            print("❌ Could not obtain flatc. Please install FlatBuffers compiler manually.")
            print("Visit: https://google.github.io/flatbuffers/flatbuffers_guide_building.html")
            sys.exit(1)

    print(f"Using flatc: {flatc_path}")

    # Check schema file
    schema_file = schema_dir / "BpmProtocol.fbs"
    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        sys.exit(1)

    # Generate C++ code
    success = generate_cpp_code(str(schema_file), str(include_dir), flatc_path)

    if success:
        # Extract enums from generated headers
        print("\n🔧 Extracting enums from generated headers...")
        extract_script = script_dir / "extract_flatbuffers_enums.py"

        # python_cmd is always a list from get_python_command()
        extract_cmd = python_cmd + [str(extract_script)]

        try:
            result = subprocess.run(extract_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Enum extraction completed successfully!")
            else:
                print(f"❌ Enum extraction failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error running enum extraction: {e}")
            return False

        # List generated files
        print("\n📁 Generated files:")
        for file in include_dir.glob("*.h"):
            print(f"  Header: {file.name}")
        for file in src_dir.glob("*.cpp"):
            print(f"  Source: {file.name}")

        print("\n✅ FlatBuffers code generation and enum extraction completed successfully!")
        print("\nNext steps:")
        print("1. Add generated headers to your ESP32 project includes")
        print("2. Include flatbuffers library in your PlatformIO project")
        print("3. Use extracted enums in your source files (e.g., #include \"BpmCommon_extracted.h\")")
        print("4. Implement BPM detector message serialization")
        print("5. Update REST API to support binary FlatBuffers format")
    else:
        print("❌ Code generation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()