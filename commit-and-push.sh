#!/bin/bash
# Script to commit and push Android project setup changes

echo "Staging all changes..."
git add -A

echo "Committing changes..."
git commit -m "Implement BPM Protocol Conan Package with Cloudsmith Integration

- Migrate conanfile.py to Conan 2.x API (tools.cmake, exports_sources)
- Add automated FlatBuffers header generation and enum extraction
- Create modular schema structure (BpmCommon, BpmCore, BpmAudio, etc.)
- Implement OMS-style ExtEnum namespace for extracted enums
- Fix BpmCore.fbs enum reference (DetectionStatus.INITIALIZING)
- Generate and package 14 header files (7 generated + 7 extracted)
- Upload bpm-protocol/0.1.0 package to Cloudsmith sparetools remote
- Verify package functionality with CMake integration test
- Package contains BPM detection protocol with FlatBuffers serialization"

echo "Pushing to remote..."
git push

echo "Done!"

