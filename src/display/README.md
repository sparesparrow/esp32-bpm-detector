# Display Implementation (Postponed)

This directory contains display-related code that has been separated from the main production codebase.

## Status: Postponed

The display features in this directory are **currently disabled** and **excluded from production builds**. They represent a future enhancement that was planned but not yet implemented.

## Configuration

Display features are disabled in `src/config.h`:
- `USE_OLED_DISPLAY=0`
- `USE_7SEGMENT_DISPLAY=0`

## Build System

This directory is excluded from all PlatformIO builds via `build_src_filter` in `platformio.ini`:
```
build_src_filter = +<*> -<**/display/**> ...
```

## Files

- **`display_handler.cpp/h`** - OLED display handler implementation
- **`arduino_display_main.cpp`** - Arduino display client main function
- **`bpm_serial_sender.cpp/h`** - Serial communication for BPM data to displays

## Future Re-enablement

When ready to implement display features:

1. Move files back to main `src/` directory (or keep them organized here)
2. Update `src/config.h` to enable display features:
   ```cpp
   #define USE_OLED_DISPLAY 1
   #define USE_7SEGMENT_DISPLAY 1
   ```
3. Remove `display/` exclusion from `platformio.ini` build filters
4. Integrate display initialization into main application setup flow
5. Update any dependent code that referenced these files

## Notes

- This code was preserved for future use rather than deleted
- The separation makes the production codebase cleaner
- All display functionality is currently handled by the Android app and LED strip