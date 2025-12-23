@echo off
REM Build release APK for ESP32 BPM Detector

cd /d "%~dp0"

echo Building release APK...
call gradlew.bat assembleRelease

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Release APK built successfully!
    echo Location: app\build\outputs\apk\release\app-release.apk
    echo.
    echo Note: For production, configure signing in app\build.gradle
) else (
    echo.
    echo Build failed. Check the error messages above.
    exit /b 1
)

