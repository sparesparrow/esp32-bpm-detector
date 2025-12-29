#ifndef IAUDIO_INPUT_H
#define IAUDIO_INPUT_H

#include <cstdint>

//! @brief Pure virtual interface for audio input functionality
//! @details Defines the contract for audio sampling across different microcontroller platforms.
//! Follows oms-dev pattern with 'I' prefix for interfaces.
class IAudioInput
{
public:
    virtual ~IAudioInput() = default;

    //! @brief Initialize the audio input with specified pin
    virtual void begin(uint8_t adc_pin) = 0;

    //! @brief Initialize stereo audio input
    virtual void beginStereo(uint8_t left_pin, uint8_t right_pin) = 0;

    //! @brief Read a single audio sample (mono or combined stereo)
    virtual float readSample() = 0;

    //! @brief Read separate stereo samples
    virtual void readStereoSamples(float& left, float& right) = 0;

    //! @brief Get current signal level (RMS or peak)
    virtual float getSignalLevel() const = 0;

    //! @brief Get normalized signal level (0.0-1.0)
    virtual float getNormalizedLevel() const = 0;

    //! @brief Check if audio input is initialized
    virtual bool isInitialized() const = 0;

    //! @brief Reset signal level calibration
    virtual void resetCalibration() = 0;
};

#endif // IAUDIO_INPUT_H
