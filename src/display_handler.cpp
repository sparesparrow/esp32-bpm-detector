#include "display_handler.h"

DisplayHandler::DisplayHandler()
    : initialized_(false) {
}

DisplayHandler::~DisplayHandler() {
}

void DisplayHandler::begin() {
    initialized_ = true;
    DEBUG_PRINTLN("[DisplayHandler] Display handler initialized (stub mode)");
}

[[maybe_unused]] void DisplayHandler::showStatus(const String& status) {
    if (!initialized_) return;

    // Debug output for stub mode
    #if DEBUG_SERIAL
        DEBUG_PRINTF("[Display] Status: %s\n", status.c_str());
    #endif
}

[[maybe_unused]] void DisplayHandler::showBPM(int bpm, float confidence) {
    if (!initialized_) return;

    // Debug output for stub mode
    #if DEBUG_SERIAL
        DEBUG_PRINTF("[Display] BPM: %d (Confidence: %.2f)\n", bpm, confidence);
    #endif
}