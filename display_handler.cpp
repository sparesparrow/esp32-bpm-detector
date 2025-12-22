#include "display_handler.h"

DisplayHandler::DisplayHandler()
    : initialized_(false)
{
}

DisplayHandler::~DisplayHandler() {
}

void DisplayHandler::begin() {
    initialized_ = true;
    
    #if DEBUG_SERIAL
        DEBUG_PRINTLN("[DisplayHandler] Display handler initialized (stub mode)");
    #endif
}

void DisplayHandler::showStatus(const String& status) {
    #if DEBUG_SERIAL
        DEBUG_PRINTF("[Display] Status: %s\n", status.c_str());
    #endif
    // Stub implementation - does nothing
    // Can be replaced later with actual OLED/7-segment display code
}

void DisplayHandler::showBPM(int bpm, float confidence) {
    #if DEBUG_SERIAL
        DEBUG_PRINTF("[Display] BPM: %d (Confidence: %.2f)\n", bpm, confidence);
    #endif
    // Stub implementation - does nothing
    // Can be replaced later with actual OLED/7-segment display code
}

