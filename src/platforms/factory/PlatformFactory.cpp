#include "PlatformFactory.h"

// ESP32 platform implementations
#ifdef PLATFORM_ESP32
#include "../esp32/ESP32AudioInput.h"
#include "../esp32/ESP32DisplayHandler.h"
#include "../esp32/ESP32Serial.h"
#include "../esp32/ESP32Timer.h"
#include "../esp32/ESP32Platform.h"
#endif

// Arduino platform implementations
#ifdef PLATFORM_ARDUINO
#include "../arduino/ArduinoAudioInput.h"
#include "../arduino/ArduinoDisplayHandler.h"
#include "../arduino/ArduinoSerial.h"
#include "../arduino/ArduinoTimer.h"
#include "../arduino/ArduinoPlatform.h"
#endif

IAudioInput* PlatformFactory::createAudioInput()
{
#ifdef PLATFORM_ESP32
    return new ESP32AudioInput();
#elif defined(PLATFORM_ARDUINO)
    return new ArduinoAudioInput();
#else
    #error "PLATFORM_TYPE not defined. Define PLATFORM_ESP32 or PLATFORM_ARDUINO"
    return nullptr;
#endif
}

IDisplayHandler* PlatformFactory::createDisplayHandler()
{
#ifdef PLATFORM_ESP32
    return new ESP32DisplayHandler();
#elif defined(PLATFORM_ARDUINO)
    return new ArduinoDisplayHandler();
#else
    #error "PLATFORM_TYPE not defined. Define PLATFORM_ESP32 or PLATFORM_ARDUINO"
    return nullptr;
#endif
}

ISerial* PlatformFactory::createSerial()
{
#ifdef PLATFORM_ESP32
    return new ESP32Serial();
#elif defined(PLATFORM_ARDUINO)
    return new ArduinoSerial();
#else
    #error "PLATFORM_TYPE not defined. Define PLATFORM_ESP32 or PLATFORM_ARDUINO"
    return nullptr;
#endif
}

ITimer* PlatformFactory::createTimer()
{
#ifdef PLATFORM_ESP32
    return new ESP32Timer();
#elif defined(PLATFORM_ARDUINO)
    return new ArduinoTimer();
#else
    #error "PLATFORM_TYPE not defined. Define PLATFORM_ESP32 or PLATFORM_ARDUINO"
    return nullptr;
#endif
}

IPlatform* PlatformFactory::createPlatform()
{
#ifdef PLATFORM_ESP32
    return new ESP32Platform();
#elif defined(PLATFORM_ARDUINO)
    return new ArduinoPlatform();
#else
    #error "PLATFORM_TYPE not defined. Define PLATFORM_ESP32 or PLATFORM_ARDUINO"
    return nullptr;
#endif
}

const char* PlatformFactory::getPlatformName()
{
#ifdef PLATFORM_ESP32
    return "ESP32-S3";
#elif defined(PLATFORM_ARDUINO)
    return "Arduino";
#else
    return "Unknown";
#endif
}
