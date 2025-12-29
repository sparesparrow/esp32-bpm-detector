#include "ESP32AudioInput.h"

ESP32AudioInput::ESP32AudioInput()
    : audio_input_(nullptr)
{
}

ESP32AudioInput::~ESP32AudioInput()
{
    delete audio_input_;
    audio_input_ = nullptr;
}

void ESP32AudioInput::begin(uint8_t adc_pin)
{
    if (!audio_input_)
    {
        audio_input_ = new AudioInput();
    }
    audio_input_->begin(adc_pin);
}

void ESP32AudioInput::beginStereo(uint8_t left_pin, uint8_t right_pin)
{
    if (!audio_input_)
    {
        audio_input_ = new AudioInput();
    }
    audio_input_->beginStereo(left_pin, right_pin);
}

float ESP32AudioInput::readSample()
{
    if (!audio_input_)
    {
        return 0.0f;
    }
    return audio_input_->readSample();
}

void ESP32AudioInput::readStereoSamples(float& left, float& right)
{
    if (!audio_input_)
    {
        left = 0.0f;
        right = 0.0f;
        return;
    }
    audio_input_->readStereoSamples(left, right);
}

float ESP32AudioInput::getSignalLevel() const
{
    if (!audio_input_)
    {
        return 0.0f;
    }
    return audio_input_->getSignalLevel();
}

float ESP32AudioInput::getNormalizedLevel() const
{
    if (!audio_input_)
    {
        return 0.0f;
    }
    return audio_input_->getNormalizedLevel();
}

bool ESP32AudioInput::isInitialized() const
{
    if (!audio_input_)
    {
        return false;
    }
    return audio_input_->isInitialized();
}

void ESP32AudioInput::resetCalibration()
{
    if (audio_input_)
    {
        audio_input_->resetCalibration();
    }
}
