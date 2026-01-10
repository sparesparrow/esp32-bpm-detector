# BPM Detector Android Testing Guide

This guide covers all testing aspects for the Android BPM Detector app, including unit tests, integration tests, and UI tests.

## 🧪 Test Categories

### 1. Unit Tests
Local tests that run on JVM without Android dependencies.

**Location**: `app/src/test/java/`
**Framework**: JUnit 4 + Mockito + Kotlin Coroutines Test

### 2. Integration Tests
Tests that run on Android device/emulator with full Android framework.

**Location**: `app/src/androidTest/java/`
**Framework**: JUnit 4 + Espresso + UI Automator

### 3. Hardware Emulation Tests
Tests for ESP32 communication protocol simulation.

**Location**: `tests/integration/`
**Framework**: pytest (Python)

## 🚀 Running Tests

### Unit Tests Only
```bash
./gradlew testDebugUnitTest
```

### Integration Tests Only
```bash
./gradlew connectedDebugAndroidTest
```

### All Android Tests
```bash
./gradlew test connectedDebugAndroidTest
```

### UI Automator Tests (Recommended)
```bash
./run_ui_tests.sh
```

### Hardware Emulation Tests
```bash
cd ../  # Go to project root
python3 run_tests.py --emulator
```

## 📱 Device Setup for Testing

### Physical Device
1. Enable Developer Options
2. Enable USB Debugging
3. Connect via USB
4. Grant permissions when prompted

### Emulator
```bash
# Create AVD
avdmanager create avd -n test_avd -k "system-images;android-34;google_apis;x86_64"

# Start emulator
emulator -avd test_avd
```

### Verify Device Connection
```bash
adb devices
adb shell getprop ro.product.model
```

## 🔧 Test Configuration

### Build Variants
- **Debug**: `assembleDebug` - Includes test APK
- **Release**: `assembleRelease` - Excludes test code

### Test Orchestrator
Enabled in `build.gradle` for better test isolation:
```gradle
testOptions {
    execution 'ANDROIDX_TEST_ORCHESTRATOR'
}
```

## 📊 Test Results

### HTML Reports
- **Unit Tests**: `app/build/reports/tests/testDebugUnitTest/index.html`
- **Integration Tests**: `app/build/reports/androidTests/connected/index.html`

### Test Screenshots
- **Location**: `app/build/outputs/managed_device_android_test_additional_output/`
- **Format**: PNG screenshots of test failures

### Coverage Reports
```bash
./gradlew createDebugCoverageReport
# Report: app/build/reports/coverage/debug/index.html
```

## 🐛 Debugging Test Failures

### Common Issues

#### 1. Permission Denied
```bash
# Grant permissions manually
adb shell pm grant com.sparesparrow.bpmdetector.debug android.permission.RECORD_AUDIO
adb shell pm grant com.sparesparrow.bpmdetector.debug android.permission.ACCESS_FINE_LOCATION
```

#### 2. Device Not Found
```bash
# Check device connection
adb devices
adb kill-server && adb start-server
```

#### 3. Test Timeout
```bash
# Increase timeout in test
@Test(timeout = 30000)
fun testLongRunningOperation() { ... }
```

#### 4. UI Element Not Found
```bash
# Take screenshot for debugging
adb shell screencap /sdcard/screen.png
adb pull /sdcard/screen.png
```

## 📝 Writing Tests

### Unit Test Example
```kotlin
@Test
fun `calculate BPM should return valid range`() {
    // Given
    val detector = LocalBPMDetector()

    // When
    val result = detector.calculateBPM(audioData)

    // Then
    assertTrue(result in 60..200)
}
```

### UI Test Example
```kotlin
@Test
fun testBPMDisplay() {
    // Start main activity
    val scenario = ActivityScenario.launch(MainActivity::class.java)

    // Verify UI elements
    onView(withId(R.id.bpm_display))
        .check(matches(isDisplayed()))

    // Perform actions
    onView(withId(R.id.start_button))
        .perform(click())

    // Verify results
    onView(withText("120 BPM"))
        .check(matches(isDisplayed()))
}
```

### UI Automator Test Example
```kotlin
@Test
fun testDeviceRotation() {
    val device = UiDevice.getInstance(getInstrumentation())

    // Rotate device
    device.setOrientationLeft()
    Thread.sleep(1000)

    // Check app handles rotation
    device.setOrientationNatural()

    // Verify app still works
    onView(withId(R.id.main_screen))
        .check(matches(isDisplayed()))
}
```

## 🎯 Test Strategy

### Test Pyramid
```
UI Tests (10%)     - End-to-end user workflows
Integration Tests (20%) - Component interactions
Unit Tests (70%)   - Individual functions/classes
```

### Coverage Goals
- **Unit Tests**: >80% coverage
- **Integration Tests**: Key user journeys
- **UI Tests**: Critical user workflows

### Continuous Integration
```yaml
# Example GitHub Actions
- name: Run Unit Tests
  run: ./gradlew testDebugUnitTest

- name: Run Integration Tests
  run: ./gradlew connectedDebugAndroidTest
```

## 🔍 Troubleshooting

### Test Flakiness
- Use `IdlingResource` for async operations
- Add proper waits with `Thread.sleep()` or `Espresso.onIdle()`
- Avoid timing-dependent tests

### Memory Issues
- Clear test data between tests
- Use `@After` methods for cleanup
- Monitor memory usage with Android Profiler

### Device-Specific Issues
- Test on multiple device sizes
- Handle different Android versions
- Consider device capabilities (camera, sensors)

## 📚 Resources

- [Android Testing Documentation](https://developer.android.com/training/testing)
- [Espresso Guide](https://developer.android.com/training/testing/espresso)
- [UI Automator](https://developer.android.com/training/testing/ui-automator)
- [JUnit 4](https://junit.org/junit4/)

## 🎉 Best Practices

✅ **Do's:**
- Test business logic thoroughly
- Use descriptive test names
- Keep tests independent
- Mock external dependencies
- Run tests on CI/CD

❌ **Don'ts:**
- Test implementation details
- Write slow tests
- Skip test cleanup
- Hardcode device-specific values
- Ignore flaky tests

---

**Ready to test?** Run `./run_ui_tests.sh` for comprehensive UI testing! 🚀