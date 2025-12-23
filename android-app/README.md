# ESP32 BPM Detector - Android App

A modern Android application for displaying real-time BPM (Beats Per Minute) data from an ESP32 microcontroller. Built with Jetpack Compose and MVVM architecture.

## Features

- **Real-time BPM Display**: Large, easy-to-read BPM values with visual indicators
- **Live Confidence & Signal Monitoring**: Circular progress indicators showing detection quality
- **Connection Status**: Visual feedback for ESP32 connection state
- **Configurable Settings**: Server IP and polling interval customization
- **Connection Testing**: Built-in connectivity verification
- **Background Monitoring**: Persistent BPM polling service
- **Material Design 3**: Modern UI with dark/light theme support

## Architecture

The app follows MVVM (Model-View-ViewModel) architecture:

- **Models**: `BPMData`, `BPMSettings`, `BPMHealth` - Data structures for API responses
- **Network**: `BPMApiClient` - Retrofit-based HTTP client with retry logic
- **Services**: `BPMService` - Background service for continuous polling
- **ViewModels**: `BPMViewModel` - Business logic and state management
- **UI**: Jetpack Compose screens with navigation

## API Integration

Communicates with ESP32 via REST API:

```http
GET /api/bpm     # Get current BPM data
GET /api/settings # Get firmware configuration
GET /api/health  # Health check
```

Response format:
```json
{
  "bpm": 128.5,
  "confidence": 0.87,
  "signal_level": 0.72,
  "status": "detecting",
  "timestamp": 1671545123456
}
```

## Getting Started

### Prerequisites

- **Android Studio**: Arctic Fox or later
- **Minimum SDK**: API 24 (Android 7.0)
- **Target SDK**: API 34 (Android 14)
- **Kotlin**: 1.9.0+

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/sparesparrow/esp32-bpm-detector.git
   cd esp32-bpm-detector/android-app
   ```

2. **Open in Android Studio**
   - Launch Android Studio
   - Select "Open an existing Android Studio project"
   - Navigate to the `android-app` directory

3. **Configure ESP32 IP**
   - Open the app settings
   - Enter your ESP32's IP address (default: 192.168.1.100)
   - Test the connection

4. **Build and Run**
   - Connect an Android device or start an emulator
   - Click "Run" (green play button)
   - Grant internet permissions when prompted

## Usage

### BPM Display Screen

- **Large BPM Display**: Shows current BPM value (or "--" if not detected)
- **Confidence Indicator**: Circular progress showing detection confidence (0-100%)
- **Signal Level**: Audio signal strength indicator
- **Status Text**: Current detection state (Detecting, Low Signal, etc.)
- **Connection Status**: Top bar showing ESP32 connection state

### Settings Screen

- **Server IP**: Configure ESP32 IP address
- **Polling Interval**: Set update frequency (100-2000ms)
- **Connection Test**: Verify ESP32 connectivity
- **Real-time Status**: Current connection and BPM data

### Background Service

The app uses a bound service for continuous monitoring:

- Automatically starts when app opens
- Continues running when app is backgrounded
- Shows persistent notification (future enhancement)
- Handles network reconnection automatically

## Technical Details

### Dependencies

```gradle
// Core Android
implementation 'androidx.core:core-ktx:1.12.0'
implementation 'androidx.appcompat:appcompat:1.6.1'

// Jetpack Compose
implementation 'androidx.activity:activity-compose:1.8.0'
implementation 'androidx.compose.material3:material3:1.1.1'

// Networking
implementation 'com.squareup.retrofit2:retrofit:2.10.0'
implementation 'com.squareup.retrofit2:converter-gson:2.10.0'

// Lifecycle & ViewModel
implementation 'androidx.lifecycle:lifecycle-viewmodel-ktx:2.6.1'

// Logging
implementation 'com.jakewharton.timber:timber:5.0.1'
```

### Permissions

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

### Network Security

For development, cleartext traffic is allowed. For production:

```xml
<!-- android:usesCleartextTraffic="false" -->
<domain-config cleartextTrafficPermitted="false">
    <domain includeSubdomains="true">your-domain.com</domain>
</domain-config>
```

## Development

### Code Structure

```
app/src/main/java/com/sparesparrow/bpmdetector/
├── models/           # Data classes
├── network/          # API client & services
├── services/         # Background service
├── ui/               # Compose UI components
│   ├── screens/      # Screen composables
│   └── theme/        # App theming
├── viewmodels/       # MVVM ViewModels
├── MainActivity.kt   # App entry point
└── BPMApplication.kt # Application class
```

### Testing

Run unit tests:
```bash
# Unix/Mac
./gradlew test

# Windows
.\gradlew.bat test
```

Run instrumentation tests:
```bash
# Unix/Mac
./gradlew connectedAndroidTest

# Windows
.\gradlew.bat connectedAndroidTest
```

### Project Structure

```
android-app/
├── app/
│   ├── build.gradle          # App-level build configuration
│   ├── proguard-rules.pro    # ProGuard rules for release builds
│   └── src/
│       └── main/
│           ├── AndroidManifest.xml
│           ├── java/          # Kotlin source code
│           └── res/           # Resources (layouts, strings, etc.)
├── build.gradle              # Root-level build configuration
├── settings.gradle           # Project settings and modules
├── gradle.properties        # Project-wide Gradle properties
├── gradlew / gradlew.bat     # Gradle wrapper scripts
├── build-debug.sh / .bat     # Convenience scripts for building
├── build-release.sh / .bat
└── gradle/wrapper/           # Gradle wrapper files
```

### Debugging

- **Network Logs**: Enable Retrofit logging in debug builds
- **Timber Logs**: Use `adb logcat` to view Timber debug output
- **Connection Issues**: Check ESP32 IP and network connectivity

## Troubleshooting

### Cannot Connect to ESP32

1. **Verify ESP32 is running**: Check serial output for WiFi connection
2. **Check IP address**: Ensure ESP32 and Android device are on same network
3. **Firewall settings**: Some networks block device-to-device communication
4. **ESP32 WiFi mode**: Ensure ESP32 is in station mode with correct credentials

### BPM Not Updating

1. **Check microphone**: Verify MAX9814 is connected and powered
2. **Audio signal**: Ensure sufficient audio volume for detection
3. **ESP32 logs**: Check for BPM detection in serial monitor
4. **Polling interval**: Try increasing polling frequency

### App Crashes

1. **Permissions**: Grant internet permission in app settings
2. **Memory**: Check device has sufficient free RAM
3. **API level**: Ensure device meets minimum SDK requirements

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

MIT License - See LICENSE file for details.

## sparetools Integration

This project integrates with the [sparetools](https://github.com/sparesparrow/sparetools) repository for shared components and workflows.

**Integration Status:** ✅ Complete - See `build/SPARETOOLS_INTEGRATION_COMPLETE.md` for details.

**Integrated Components:**
- Updated dependency versions (Compose BOM 2024.02.00, Lifecycle 2.7.0, Coroutines 1.7.3)
- Added buildConfig feature support
- CI/CD workflow adapted from sparetools (`.github/workflows/android-build.yml`)
- Enhanced ProGuard rules with source file attributes

For integration details and future updates, see:
- `build/SPARETOOLS_INTEGRATION_COMPLETE.md` - What was integrated
- `build/SPARETOOLS_INTEGRATION.md` - Integration guide

## Related Projects

- **ESP32 Firmware**: Real-time audio processing and BPM detection
- **Hardware Setup**: MAX9814 microphone integration guide
- **API Documentation**: Complete REST API specification
- **sparetools**: Shared Android build patterns and CI/CD workflows

