#ifndef IDISPLAY_HANDLER_H
#define IDISPLAY_HANDLER_H

#include <cstdint>

//! @brief Pure virtual interface for display output functionality
//! @details Defines the contract for display operations across different microcontroller platforms.
//! Follows oms-dev pattern with 'I' prefix for interfaces.
class IDisplayHandler
{
public:
    virtual ~IDisplayHandler() = default;

    //! @brief Initialize the display (stub implementation for platforms without displays)
    virtual void begin() = 0;

    //! @brief Show status message
    virtual void showStatus(const char* status) = 0;

    //! @brief Show BPM value and confidence
    virtual void showBPM(int bpm, float confidence) = 0;
};

#endif // IDISPLAY_HANDLER_H

