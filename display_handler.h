#ifndef DISPLAY_HANDLER_H
#define DISPLAY_HANDLER_H

#include <Arduino.h>
#include "config.h"

class DisplayHandler {
public:
    DisplayHandler();
    ~DisplayHandler();

    // Initialize display (stub - does nothing)
    void begin();

    // Show status message (stub - prints to serial if DEBUG enabled)
    void showStatus(const String& status);

    // Show BPM value and confidence (stub - prints to serial if DEBUG enabled)
    void showBPM(int bpm, float confidence);

private:
    bool initialized_;
};

#endif // DISPLAY_HANDLER_H


