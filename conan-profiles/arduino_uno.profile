# Arduino Uno Conan Profile
# Uses host system for building Conan dependencies (FlatBuffers compiler, etc.)
# Cross-compilation for Arduino is handled by PlatformIO
# Note: FlatBuffers generation is disabled for Arduino Uno due to memory constraints

[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
compiler.cppstd=17
build_type=Release

[options]
sparetools-bpm-detector/*:target_board=arduino_uno
sparetools-bpm-detector/*:with_display=False
sparetools-bpm-detector/*:with_networking=False
sparetools-bpm-detector/*:with_websocket=False
sparetools-bpm-detector/*:with_audio_calibration=False
