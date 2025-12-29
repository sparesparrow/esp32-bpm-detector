#ifndef PLATFORM_FACTORY_H
#define PLATFORM_FACTORY_H

#include "../../interfaces/IAudioInput.h"
#include "../../interfaces/IDisplayHandler.h"
#include "../../interfaces/ISerial.h"
#include "../../interfaces/ITimer.h"
#include "../../interfaces/IPlatform.h"

//! @brief Factory class for creating platform-specific implementations
//! @details Uses compile-time defines to instantiate appropriate platform implementations
//! Follows oms-dev pattern for platform abstraction
class PlatformFactory
{
public:
    PlatformFactory() = delete;  // Static factory only
    ~PlatformFactory() = delete;

    //! @brief Create audio input implementation for current platform
    static IAudioInput* createAudioInput();

    //! @brief Create display handler implementation for current platform
    static IDisplayHandler* createDisplayHandler();

    //! @brief Create serial implementation for current platform
    static ISerial* createSerial();

    //! @brief Create timer implementation for current platform
    static ITimer* createTimer();

    //! @brief Create platform implementation for current platform
    static IPlatform* createPlatform();

    //! @brief Get platform name string
    static const char* getPlatformName();
};

#endif // PLATFORM_FACTORY_H
