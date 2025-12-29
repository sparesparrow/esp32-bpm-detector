#ifndef ISERIAL_H
#define ISERIAL_H

#include <cstdint>
#include <cstddef>

//! @brief Pure virtual interface for serial communication
//! @details Defines the contract for serial I/O operations across different microcontroller platforms.
//! Abstracts the Serial object and printf functionality.
class ISerial
{
public:
    virtual ~ISerial() = default;

    //! @brief Initialize serial communication at specified baud rate
    virtual void begin(uint32_t baud_rate) = 0;

    //! @brief Print a string without newline
    virtual void print(const char* str) = 0;

    //! @brief Print a string with newline
    virtual void println(const char* str) = 0;

    //! @brief Print an integer
    virtual void print(int value) = 0;

    //! @brief Print an integer with newline
    virtual void println(int value) = 0;

    //! @brief Print an unsigned 32-bit integer
    virtual void print(uint32_t value) = 0;

    //! @brief Print an unsigned 32-bit integer with newline
    virtual void println(uint32_t value) = 0;

    //! @brief Print a float
    virtual void print(float value) = 0;

    //! @brief Print a float with newline
    virtual void println(float value) = 0;

    //! @brief Print formatted string (like printf)
    virtual void printf(const char* format, ...) = 0;

    //! @brief Check if data is available to read
    virtual int available() = 0;

    //! @brief Read a single character
    virtual int read() = 0;

    //! @brief Flush output buffer
    virtual void flush() = 0;
};

#endif // ISERIAL_H
