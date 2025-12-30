# Generic ESP32 Conan Profile
# Uses host system for building Conan dependencies (FlatBuffers compiler, etc.)
# Cross-compilation for ESP32 is handled by PlatformIO

[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
compiler.cppstd=17
build_type=Release

[options]
sparetools-bpm-detector/*:target_board=esp32
sparetools-bpm-detector/*:with_display=False
sparetools-bpm-detector/*:with_networking=True
sparetools-bpm-detector/*:with_websocket=True
sparetools-bpm-detector/*:with_audio_calibration=False
