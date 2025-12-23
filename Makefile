# Cross-platform Makefile for ESP32 BPM Detector Tests
# Works on Linux, macOS, and Windows (with make installed)

# Compiler settings
CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -I.
LDFLAGS = -lm

# Test executables
TEST_TARGETS = comprehensive_tests final_test simple_validation fft_logic_test

# Default target
all: $(TEST_TARGETS)

# Comprehensive test suite
comprehensive_tests: comprehensive_tests.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

# Final test suite
final_test: final_test.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

# Simple validation test
simple_validation: simple_validation.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

# FFT logic test
fft_logic_test: fft_logic_test.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

# Run all tests
test: all
	@echo "Running comprehensive tests..."
	@./comprehensive_tests || true
	@echo ""
	@echo "Running final test suite..."
	@./final_test || true
	@echo ""
	@echo "Running simple validation..."
	@./simple_validation || true
	@echo ""
	@echo "Running FFT logic test..."
	@./fft_logic_test || true

# Clean build artifacts
clean:
	rm -f $(TEST_TARGETS) *.o
	@echo "Cleaned build artifacts"

# Clean test results
clean-results:
	rm -f test_results.txt final_test_output.txt

# Full clean
distclean: clean clean-results

# Help target
help:
	@echo "ESP32 BPM Detector - Cross-platform Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  all              - Build all test executables"
	@echo "  test             - Build and run all tests"
	@echo "  clean            - Remove compiled executables"
	@echo "  clean-results    - Remove test result files"
	@echo "  distclean        - Remove all generated files"
	@echo "  help             - Show this help message"
	@echo ""
	@echo "Individual test targets:"
	@echo "  comprehensive_tests"
	@echo "  final_test"
	@echo "  simple_validation"
	@echo "  fft_logic_test"

.PHONY: all test clean clean-results distclean help
