# ESP32 BPM Detector - Cross-platform Testing Guide

## Overview

This guide provides cross-platform instructions for running all tests in the ESP32 BPM detector project. All test runners work on Linux, macOS, and Windows.

## Prerequisites

### Required Tools

**C++ Compiler:**
- **Linux**: `g++` (usually pre-installed) or `clang++`
- **macOS**: `g++` or `clang++` (via Xcode Command Line Tools)
- **Windows**: MinGW-w64, MSYS2, or WSL

**Python (Optional):**
- Python 3.6+ for Python-based test runner

**Make (Optional):**
- `make` for Makefile-based builds (usually pre-installed on Linux/macOS)
- Windows: Use WSL, MSYS2, or install via Chocolatey

## Quick Start

### Method 1: Using Makefile (Recommended)

```bash
# Build and run all tests
make test

# Build only (no execution)
make

# Clean build artifacts
make clean

# Clean everything including test results
make distclean

# Show help
make help
```

### Method 2: Using Python Script

```bash
# Run all tests
python3 run_tests.py

# On Windows
python run_tests.py
```

### Method 3: Using Shell Script (Linux/macOS/Git Bash)

```bash
# Make executable
chmod +x run_tests.sh

# Run tests
./run_tests.sh
```

### Method 4: Manual Compilation

```bash
# Compile individual tests
g++ -std=c++17 -I. comprehensive_tests.cpp -o comprehensive_tests -lm
g++ -std=c++17 -I. final_test.cpp -o final_test -lm
g++ -std=c++17 -I. simple_validation.cpp -o simple_validation -lm
g++ -std=c++17 -I. fft_logic_test.cpp -o fft_logic_test -lm

# Run tests
./comprehensive_tests
./final_test
./simple_validation
./fft_logic_test
```

## Test Suites

### 1. Comprehensive Tests (`comprehensive_tests.cpp`)

**Purpose**: Full algorithm validation including BPM calculation, signal processing, edge cases, FFT processing, memory usage, and real-time simulation.

**Expected Output:**
```
ESP32 BPM Detector - Comprehensive Test Suite
===========================================
✓ BPM calculation accuracy tests passed!
✓ Signal processing tests passed!
✓ Edge case tests passed!
✓ FFT processing tests passed!
✓ Memory usage test passed
```

### 2. Final Test Suite (`final_test.cpp`)

**Purpose**: Final validation of all core components with detailed test results.

**Expected Output:**
```
ESP32 BPM Detector - Final Comprehensive Test Suite
==================================================
--- BPM Calculation Tests ---
✓ 120 BPM Calculation PASSED
✓ 140 BPM Calculation PASSED
✓ BPM Range Validation PASSED

TEST SUMMARY
Passed: 16/18
```

### 3. Simple Validation (`simple_validation.cpp`)

**Purpose**: Quick validation of core BPM calculation and confidence algorithms.

**Expected Output:**
```
ESP32 BPM Detector Validation Tests
===================================
OVERALL RESULT: ALL TESTS PASSED
```

### 4. FFT Logic Test (`fft_logic_test.cpp`)

**Purpose**: Validates FFT processing and frequency analysis logic.

**Expected Output:**
```
FFT Logic Test for ESP32 BPM Detector
=====================================
✓ FFT computation test passed
✓ Envelope detection test passed
```

## Platform-Specific Instructions

### Linux

```bash
# Install build tools (if needed)
sudo apt-get update
sudo apt-get install build-essential

# Run tests
make test
```

### macOS

```bash
# Install Xcode Command Line Tools (if needed)
xcode-select --install

# Run tests
make test
```

### Windows

**Option 1: Using WSL (Windows Subsystem for Linux)**
```bash
# Install WSL and Ubuntu
wsl --install

# In WSL terminal
make test
```

**Option 2: Using MSYS2**
```bash
# Install MSYS2 from https://www.msys2.org/
# Install GCC
pacman -S mingw-w64-x86_64-gcc make

# Run tests
make test
```

**Option 3: Using Git Bash**
```bash
# Install Git for Windows (includes Git Bash)
# Install MinGW-w64 compiler

# Run Python script
python run_tests.py
```

**Option 4: Using Visual Studio**
```bash
# Install Visual Studio with C++ support
# Use Developer Command Prompt
cl /EHsc /std:c++17 comprehensive_tests.cpp /Fe:comprehensive_tests.exe
comprehensive_tests.exe
```

## Android Tests

### Unit Tests

```bash
cd android-app

# Linux/macOS
./gradlew test

# Windows
.\gradlew.bat test
```

### Integration Tests

```bash
cd android-app

# Linux/macOS
./gradlew connectedAndroidTest

# Windows
.\gradlew.bat connectedAndroidTest
```

## Continuous Integration

The project includes GitHub Actions workflows that run tests automatically:

- **C++ Tests**: Run via Makefile in CI environment
- **Android Tests**: Run via Gradle in CI environment
- **Cross-platform**: CI runs on Ubuntu (Linux), ensuring cross-platform compatibility

## Troubleshooting

### Compiler Not Found

**Error**: `g++: command not found`

**Solution**:
- **Linux**: `sudo apt-get install build-essential`
- **macOS**: `xcode-select --install`
- **Windows**: Install MinGW-w64 or use WSL

### Make Not Found

**Error**: `make: command not found`

**Solution**:
- **Linux**: Usually pre-installed
- **macOS**: Install Xcode Command Line Tools
- **Windows**: Use WSL, MSYS2, or Python script instead

### Permission Denied

**Error**: `Permission denied` when running scripts

**Solution**:
```bash
chmod +x run_tests.sh
./run_tests.sh
```

### Test Failures

If tests fail:
1. Check compiler version (C++17 support required)
2. Verify all source files are present
3. Check for platform-specific math library linking (`-lm` flag)
4. Review test output for specific error messages

## Test Coverage

The test suite covers:
- ✅ BPM calculation accuracy (±1-2 BPM)
- ✅ Confidence scoring algorithm
- ✅ Signal processing and filtering
- ✅ Edge case handling (no beats, single beat, out of range)
- ✅ FFT processing pipeline
- ✅ Memory management
- ✅ Real-time simulation
- ✅ Android ViewModel logic
- ✅ Android API client
- ✅ Android data models

## Contributing

When adding new tests:
1. Follow existing test structure
2. Use cross-platform C++ standard library only
3. Avoid platform-specific code
4. Update this documentation
5. Ensure tests pass on all platforms

## Additional Resources

- [C++ Standard Library Reference](https://en.cppreference.com/)
- [GCC Documentation](https://gcc.gnu.org/onlinedocs/)
- [Clang Documentation](https://clang.llvm.org/docs/)
- [CMake Cross-platform Guide](https://cmake.org/cmake/help/latest/manual/cmake-toolchains.7.html)
