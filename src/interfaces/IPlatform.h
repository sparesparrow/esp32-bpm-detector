#ifndef IPLATFORM_H
#define IPLATFORM_H

#include <cstdint>

//! @brief Pure virtual interface for platform-specific functionality
//! @details Defines the contract for platform-specific system operations.
//! Abstracts ESP.getFreeHeap(), chip identification, and other platform-specific calls.
class IPlatform
{
public:
    virtual ~IPlatform() = default;

    //! @brief Get available free heap memory in bytes
    virtual uint32_t getFreeHeap() = 0;

    //! @brief Get total heap size in bytes
    virtual uint32_t getTotalHeap() = 0;

    //! @brief Get a unique chip identifier
    virtual uint64_t getChipId() = 0;

    //! @brief Get platform name string
    virtual const char* getPlatformName() = 0;

    //! @brief Get CPU frequency in MHz
    virtual uint32_t getCpuFrequencyMHz() = 0;

    //! @brief Restart the system
    virtual void restart() = 0;
};

#endif // IPLATFORM_H
