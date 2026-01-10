#include "LEDControllerFactory.h"
#include "led_strip_controller.h"

// ============================================================================
// LED Controller Factory Implementation
// ============================================================================

ILEDController* LEDControllerFactory::createLEDController() {
    // For now, always create LEDStripController
    // In the future, this could check platform type and create appropriate controller
    return new LEDStripController();
}

void LEDControllerFactory::destroyLEDController(ILEDController* controller) {
    if (controller) {
        delete controller;
    }
}