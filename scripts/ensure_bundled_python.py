#!/usr/bin/env python3
"""
Ensure Bundled CPython Script
This script ensures that sparetools bundled CPython is used when executing Python scripts.

Usage:
    python3 scripts/ensure_bundled_python.py <script> [args...]
    
Or use as a wrapper:
    ./scripts/ensure_bundled_python.py scripts/learning_loop_workflow.py --cycle 1
"""

import os
import sys
import subprocess
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sparetools_utils import get_python_command, is_using_bundled_python

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: ensure_bundled_python.py <script> [args...]")
        print("\nEnsures sparetools bundled CPython is used when executing Python scripts.")
        sys.exit(1)
    
    script = sys.argv[1]
    script_args = sys.argv[2:]
    
    # Check if script exists
    script_path = Path(script)
    if not script_path.exists():
        print(f"Error: Script not found: {script}")
        sys.exit(1)
    
    # Get Python command (prefers bundled CPython)
    python_cmd = get_python_command()
    
    # Check if we're already using bundled Python
    if is_using_bundled_python():
        print(f"✓ Already using sparetools bundled CPython: {sys.executable}")
    else:
        print(f"⚠ Using system Python, switching to bundled CPython: {python_cmd}")
    
    # Execute script with bundled CPython
    cmd = python_cmd + [str(script_path)] + script_args
    
    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Error executing script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
