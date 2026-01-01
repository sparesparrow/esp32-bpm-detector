#ifndef DISPLAY_HANDLER_H
#define DISPLAY_HANDLER_H

#include <Arduino.h>
#include "config.h"

#if USE_OLED_DISPLAY
class Adafruit_SSD1306;
#endif

#if USE_7SEGMENT_DISPLAY
class TM1637Display;
#endif

// Display type enumeration
enum DisplayType {
    DISPLAY_NONE = 0,
    DISPLAY_OLED_SSD1306,
    DISPLAY_7SEGMENT_TM1637
};

// Display configuration
struct DisplayConfig {
    DisplayType type;
    uint8_t sda_pin;
    uint8_t scl_pin;
    uint8_t clk_pin;
    uint8_t dio_pin;
    uint8_t i2c_address;
};

class DisplayHandler {
public:
    DisplayHandler();
    ~DisplayHandler();

    // Initialize display with specific configuration
    bool begin(DisplayType type, uint8_t sda_pin = OLED_SDA_PIN, uint8_t scl_pin = OLED_SCL_PIN,
               uint8_t clk_pin = SEGMENT_CLK_PIN, uint8_t dio_pin = SEGMENT_DIO_PIN,
               uint8_t i2c_address = OLED_I2C_ADDRESS);

    // Legacy initialization using config.h settings
    void begin();

    // Show status message
    void showStatus(const String& status);

    // Show BPM value and confidence
    void showBPM(int bpm, float confidence);

    // Clear display
    void clear();

    // Set brightness (7-segment only)
    void setBrightness(uint8_t brightness);

private:
    bool initialized_;
    DisplayConfig config_;
    unsigned long last_update_time_;
    unsigned long update_interval_ms_;

#if USE_OLED_DISPLAY
    Adafruit_SSD1306* oled_;
    bool initOLED();
    void showStatusOLED(const String& status);
    void showBPMOLED(int bpm, float confidence);
#endif

#if USE_7SEGMENT_DISPLAY
    TM1637Display* seven_segment_;
    bool initSevenSegment();
    void showStatusSevenSegment(const String& status);
    void showBPMSevenSegment(int bpm, float confidence);
#endif
};

#endif // DISPLAY_HANDLER_H
