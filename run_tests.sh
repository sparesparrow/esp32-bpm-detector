#!/bin/bash
# Cross-platform test runner for ESP32 BPM Detector
# Works on Linux, macOS, and Windows (with Git Bash or WSL)

set -e

echo "ESP32 BPM Detector - Test Runner"
echo "=================================="
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Windows;;
    MINGW*)     MACHINE=Windows;;
    MSYS*)      MACHINE=Windows;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "Detected OS: $MACHINE"
echo ""

# Check for compiler
if ! command -v g++ &> /dev/null; then
    echo "Error: g++ compiler not found"
    echo "Please install GCC or Clang compiler"
    exit 1
fi

echo "Compiler: $(g++ --version | head -n1)"
echo ""

# Build flags
CXXFLAGS="-std=c++17 -Wall -Wextra -I."
LDFLAGS="-lm"

# Test files
TESTS=(
    "comprehensive_tests.cpp:comprehensive_tests"
    "final_test.cpp:final_test"
    "simple_validation.cpp:simple_validation"
    "fft_logic_test.cpp:fft_logic_test"
)

# Build and run tests
PASSED=0
FAILED=0
TOTAL=0

for test_spec in "${TESTS[@]}"; do
    IFS=':' read -r source_file executable <<< "$test_spec"
    
    if [ ! -f "$source_file" ]; then
        echo "⚠️  Skipping $source_file (not found)"
        continue
    fi
    
    TOTAL=$((TOTAL + 1))
    echo "Building $source_file..."
    
    if g++ $CXXFLAGS -o "$executable" "$source_file" $LDFLAGS 2>&1; then
        echo "✓ Compiled successfully"
        echo "Running $executable..."
        echo "----------------------------------------"
        
        if ./"$executable" 2>&1; then
            echo "----------------------------------------"
            echo "✓ $executable PASSED"
            PASSED=$((PASSED + 1))
        else
            echo "----------------------------------------"
            echo "✗ $executable FAILED"
            FAILED=$((FAILED + 1))
        fi
        echo ""
    else
        echo "✗ Compilation failed for $source_file"
        FAILED=$((FAILED + 1))
        echo ""
    fi
done

# Summary
echo "=================================="
echo "Test Summary"
echo "=================================="
echo "Total: $TOTAL"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ Some tests failed"
    exit 1
fi
