#ifndef IAUDIOINPUT_H
#define IAUDIOINPUT_H

/**
 * @brief Interface for audio input operations
 *
 * This interface defines the contract for audio input implementations
 * used by the BPM detector system. It supports both mono and stereo
 * audio input with ADC sampling capabilities.
 */
class IAudioInput {
public:
    /**
     * @brief Virtual destructor for proper cleanup
     */
    virtual ~IAudioInput() = default;

    /**
     * @brief Initialize ADC with specified pin (mono mode)
     * @param adc_pin The ADC pin to use for audio input
     */
    virtual void begin(uint8_t adc_pin) = 0;

    /**
     * @brief Initialize ADC with stereo pins
     * @param left_pin The ADC pin for left channel
     * @param right_pin The ADC pin for right channel
     */
    virtual void beginStereo(uint8_t left_pin, uint8_t right_pin) = 0;

    /**
     * @brief Read a single audio sample
     * @return The audio sample value
     */
    virtual float readSample() = 0;

    /**
     * @brief Read stereo samples
     * @param left Reference to store left channel sample
     * @param right Reference to store right channel sample
     */
    virtual void readStereoSamples(float& left, float& right) = 0;

    /**
     * @brief Get current signal level
     * @return The current RMS signal level
     */
    virtual float getSignalLevel() const = 0;

    /**
     * @brief Get normalized signal level (0.0-1.0)
     * @return The normalized signal level
     */
    virtual float getNormalizedLevel() const = 0;

    /**
     * @brief Check if audio input is initialized
     * @return true if initialized, false otherwise
     */
    virtual bool isInitialized() const = 0;

    /**
     * @brief Reset signal level calibration
     */
    virtual void resetCalibration() = 0;
};

#endif // IAUDIOINPUT_H
