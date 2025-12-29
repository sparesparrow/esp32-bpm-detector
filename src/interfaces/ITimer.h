#ifndef ITIMER_H
#define ITIMER_H

#include <cstdint>

//! @brief Pure virtual interface for timing functionality
//! @details Defines the contract for time-related operations across different microcontroller platforms.
//! Abstracts millis(), micros(), and delay() functions.
class ITimer
{
public:
    virtual ~ITimer() = default;

    //! @brief Get milliseconds since program start
    virtual uint32_t millis() = 0;

    //! @brief Get microseconds since program start
    virtual uint32_t micros() = 0;

    //! @brief Delay execution for specified milliseconds
    virtual void delay(uint32_t milliseconds) = 0;

    //! @brief Delay execution for specified microseconds
    virtual void delayMicroseconds(uint32_t microseconds) = 0;
};

#endif // ITIMER_H
