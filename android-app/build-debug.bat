@echo off
REM Build debug APK for ESP32 BPM Detector

cd /d "%~dp0"

echo Building debug APK...
call gradlew.bat assembleDebug

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Debug APK built successfully!
    echo Location: app\build\outputs\apk\debug\app-debug.apk
) else (
    echo.
    echo Build failed. Check the error messages above.
    exit /b 1
)

