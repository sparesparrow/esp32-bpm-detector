#ifndef LED_CONTROLLER_FACTORY_H
#define LED_CONTROLLER_FACTORY_H

#include "interfaces/ILEDController.h"

// ============================================================================
// LED Controller Factory
// ============================================================================

class LEDControllerFactory {
public:
    /**
     * Create the appropriate LED controller for the current platform
     * @return Pointer to the created LED controller, or nullptr if creation failed
     */
    static ILEDController* createLEDController();

    /**
     * Destroy an LED controller instance
     * @param controller The controller to destroy
     */
    static void destroyLEDController(ILEDController* controller);

private:
    LEDControllerFactory() = delete;  // Static only class
    ~LEDControllerFactory() = delete;
};

#endif // LED_CONTROLLER_FACTORY_H