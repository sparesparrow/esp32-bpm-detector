#include "ESP32DisplayHandler.h"

ESP32DisplayHandler::ESP32DisplayHandler()
    : display_handler_(nullptr)
{
}

ESP32DisplayHandler::~ESP32DisplayHandler()
{
    delete display_handler_;
    display_handler_ = nullptr;
}

void ESP32DisplayHandler::begin()
{
    if (!display_handler_)
    {
        display_handler_ = new DisplayHandler();
    }
    display_handler_->begin();
}

void ESP32DisplayHandler::showStatus(const char* status)
{
    if (display_handler_)
    {
        display_handler_->showStatus(String(status));
    }
}

void ESP32DisplayHandler::showBPM(int bpm, float confidence)
{
    if (display_handler_)
    {
        display_handler_->showBPM(bpm, confidence);
    }
}

