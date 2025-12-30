#ifndef ESP32_DISPLAY_HANDLER_H
#define ESP32_DISPLAY_HANDLER_H

#include "../../interfaces/IDisplayHandler.h"
#include "../../display_handler.h"

//! @brief ESP32-S3 implementation of display handler interface
//! @details Wraps the existing DisplayHandler class for ESP32 display functionality
class ESP32DisplayHandler : public IDisplayHandler
{
public:
    ESP32DisplayHandler();
    ~ESP32DisplayHandler() override;

    void begin() override;
    void showStatus(const char* status) override;
    void showBPM(int bpm, float confidence) override;

private:
    DisplayHandler* display_handler_;  //!< Wrapped DisplayHandler instance
};

#endif // ESP32_DISPLAY_HANDLER_H

