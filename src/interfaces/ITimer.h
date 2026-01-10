#ifndef ITIMER_H
#define ITIMER_H

/**
 * @brief Interface for timer operations
 *
 * This interface defines the contract for timer implementations
 * used by the BPM detector system for timing and scheduling operations.
 */
class ITimer {
public:
    /**
     * @brief Virtual destructor for proper cleanup
     */
    virtual ~ITimer() = default;

    /**
     * @brief Get the current time in milliseconds
     * @return Current time in milliseconds
     */
    virtual unsigned long millis() const = 0;

    /**
     * @brief Get the current time in microseconds
     * @return Current time in microseconds
     */
    virtual unsigned long micros() const = 0;

    /**
     * @brief Delay execution for specified milliseconds
     * @param ms Milliseconds to delay
     */
    virtual void delay(unsigned long ms) = 0;

    /**
     * @brief Delay execution for specified microseconds
     * @param us Microseconds to delay
     */
    virtual void delayMicroseconds(unsigned int us) = 0;
};

#endif // ITIMER_H
