# ESP32 BPM Detector - Development Loop Prompt

Execute the complete development pipeline for the ESP32 BPM Detector project. Follow these steps in order:

## 1. Build Phase

Build the ESP32 firmware using PlatformIO:
- Run `pio run` to compile the firmware
- Verify all source files compile without errors
- Check for compiler warnings and address critical ones
- Ensure all dependencies (FlatBuffers, etc.) are properly linked

## 2. Deploy Phase

Deploy the compiled firmware to the connected ESP32-S3:
- Detect connected ESP32-S3 device using the esp32-serial-monitor MCP server
- Flash the firmware using `pio run -t upload`
- Verify successful upload
- Wait for device to boot and stabilize

## 3. Unit Tests

Run C++ unit tests with gtest:
- Execute tests from `tests/test_bpm_accuracy.cpp`
- Execute tests from `tests/test_display_handler.cpp`
- Execute tests from `tests/test_wifi_handler.cpp`
- Generate JUnit XML report in `test-results/` directory
- Report pass/fail status for each test suite

## 4. Component Tests with Mocks

Run component-level tests with mocked dependencies:
- Start mock ESP32 server from `tests/integration/mock_esp32_server.py`
- Test serial communication with mocked device
- Test Android app client with mock server
- Verify FlatBuffers serialization/deserialization
- Test network protocol handling

## 5. Integration Tests with Real Hardware

Run integration tests with actual ESP32-S3 hardware:
- Verify serial communication with real device
- Test BPM detection with audio input
- Validate performance metrics (CPU usage, memory, latency)

If Android device is connected via ADB:
- Build Android APK with Gradle
- Install APK to Android device
- Run instrumented tests
- Test communication between ESP32 and Android app
- Verify BPM data reception on Android

## 6. Analysis and Reporting

After running all tests:
- Collect and aggregate test results
- Calculate overall pass rate
- Identify failing tests
- Analyze error messages and stack traces

## 7. Fix Failures (if any)

If tests failed:
- Identify root cause of each failure
- Propose and implement fixes
- Re-run affected tests to verify fixes
- Document changes made

## 8. Report Results

Generate a detailed report including:
- Build status and duration
- Deployment status
- Test results summary:
  - Unit tests: X/Y passed
  - Component tests: X/Y passed
  - Integration tests: X/Y passed
- Performance metrics
- Any issues found and fixes applied
- Recommendations for further improvement

If all tests pass, output "All tests passed" at the end of the report.

---

## MCP Tools Available

Use these MCP servers for the workflow:
- `esp32-serial-monitor`: Device detection and serial communication
- `android-dev-tools`: Android app building and ADB operations
- `conan-cloudsmith`: Conan package management
- `unified-deployment`: Deployment orchestration
- `dev-automation`: Full pipeline automation

## Expected Outcomes

1. Firmware compiles successfully
2. Firmware deploys to ESP32-S3
3. All unit tests pass
4. All component tests with mocks pass
5. Integration tests with real hardware pass
6. Android integration tests pass (if device available)
7. Clear report of results generated

## Error Handling

If any step fails:
1. Log the error details
2. Attempt automatic fix if possible
3. If fix applied, re-run the failed step
4. If unable to fix, report the issue with recommendations
