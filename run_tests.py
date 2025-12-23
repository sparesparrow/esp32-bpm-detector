#!/usr/bin/env python3
"""
Cross-platform test runner for ESP32 BPM Detector
Works on Linux, macOS, and Windows
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def detect_compiler():
    """Detect available C++ compiler"""
    compilers = ['g++', 'clang++', 'c++']
    for compiler in compilers:
        try:
            result = subprocess.run(
                [compiler, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return compiler, result.stdout.split('\n')[0]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return None, None

def compile_test(source_file, executable):
    """Compile a test file"""
    compiler, version = detect_compiler()
    if not compiler:
        print(f"Error: No C++ compiler found (tried: g++, clang++, c++)")
        return False
    
    cxxflags = ['-std=c++17', '-Wall', '-Wextra', '-I.']
    ldflags = ['-lm']
    
    # Windows-specific adjustments
    if platform.system() == 'Windows':
        executable = executable + '.exe'
    
    cmd = [compiler] + cxxflags + ['-o', executable, source_file] + ldflags
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return True
        else:
            print(f"Compilation error:\n{result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"Compilation timeout for {source_file}")
        return False

def run_test(executable):
    """Run a test executable"""
    if platform.system() == 'Windows':
        executable = executable + '.exe'
    
    if not os.path.exists(executable):
        return False, "Executable not found"
    
    try:
        result = subprocess.run(
            [executable] if platform.system() != 'Windows' else [executable],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Test timeout"

def main():
    print("ESP32 BPM Detector - Cross-platform Test Runner")
    print("=" * 50)
    print(f"Platform: {platform.system()} {platform.machine()}")
    
    compiler, version = detect_compiler()
    if compiler:
        print(f"Compiler: {version}")
    else:
        print("Error: No C++ compiler found")
        sys.exit(1)
    
    print()
    
    # Test files
    tests = [
        ("comprehensive_tests.cpp", "comprehensive_tests"),
        ("final_test.cpp", "final_test"),
        ("simple_validation.cpp", "simple_validation"),
        ("fft_logic_test.cpp", "fft_logic_test"),
    ]
    
    passed = 0
    failed = 0
    total = 0
    
    for source_file, executable in tests:
        if not os.path.exists(source_file):
            print(f"⚠️  Skipping {source_file} (not found)")
            continue
        
        total += 1
        print(f"Building {source_file}...")
        
        if compile_test(source_file, executable):
            print(f"✓ Compiled successfully")
            print(f"Running {executable}...")
            print("-" * 50)
            
            success, output = run_test(executable)
            print(output)
            print("-" * 50)
            
            if success:
                print(f"✓ {executable} PASSED")
                passed += 1
            else:
                print(f"✗ {executable} FAILED")
                failed += 1
            print()
        else:
            print(f"✗ Compilation failed for {source_file}")
            failed += 1
            print()
    
    # Summary
    print("=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"Total: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()
    
    if failed == 0:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
