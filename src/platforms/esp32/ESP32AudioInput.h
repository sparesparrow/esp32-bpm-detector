#ifndef ESP32_AUDIO_INPUT_H
#define ESP32_AUDIO_INPUT_H

#include "../../interfaces/IAudioInput.h"
#include "../../audio_input.h"

//! @brief ESP32-S3 implementation of audio input interface
//! @details Wraps the existing AudioInput class for ESP32 ADC functionality
class ESP32AudioInput : public IAudioInput
{
public:
    ESP32AudioInput();
    ~ESP32AudioInput() override;

    void begin(uint8_t adc_pin) override;
    void beginStereo(uint8_t left_pin, uint8_t right_pin) override;
    float readSample() override;
    void readStereoSamples(float& left, float& right) override;
    float getSignalLevel() const override;
    float getNormalizedLevel() const override;
    bool isInitialized() const override;
    void resetCalibration() override;

private:
    AudioInput* audio_input_;  //!< Wrapped AudioInput instance
};

#endif // ESP32_AUDIO_INPUT_H
