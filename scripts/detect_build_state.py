#!/usr/bin/env python3
"""
Build State Detector for ESP32 BPM Detector
Analyzes firmware code to determine if WiFi/HTTP server are enabled
"""

import re
from dataclasses import dataclass, field
from typing import List
from pathlib import Path


@dataclass
class CodeChange:
    file: str
    line_start: int
    line_end: int
    change_type: str
    description: str


@dataclass
class BuildState:
    wifi_enabled: bool = False
    http_server_enabled: bool = False
    flatbuffers_included: bool = False
    cpp_standard: str = "c++11"
    required_changes: List[CodeChange] = field(default_factory=list)

    def requires_changes(self) -> bool:
        return len(self.required_changes) > 0

    def is_ready(self) -> bool:
        return self.wifi_enabled and self.http_server_enabled and self.flatbuffers_included


class BuildStateDetector:
    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir)

    def analyze(self) -> BuildState:
        state = BuildState()

        # Analyze main.cpp
        self._analyze_main_cpp(state)

        # Analyze platformio.ini
        self._analyze_platformio_ini(state)

        return state

    def _analyze_main_cpp(self, state: BuildState):
        main_cpp = self.project_dir / "src" / "main.cpp"
        if not main_cpp.exists():
            return

        content = main_cpp.read_text()
        lines = content.split('\n')

        # Check for WiFi disabled message
        if "WiFi disabled - focusing on BPM detection" in content:
            state.wifi_enabled = False
            for i, line in enumerate(lines, 1):
                if "WiFi disabled" in line:
                    state.required_changes.append(CodeChange(
                        file="src/main.cpp",
                        line_start=i,
                        line_end=i + 5,
                        change_type="ENABLE_WIFI_INIT",
                        description="Enable WiFi initialization"
                    ))
                    break
        else:
            # Check if WiFi handler is actually initialized
            if "wifiHandler->begin" in content or "wifiHandler->connect" in content:
                state.wifi_enabled = True

        # Check for web server disabled message
        if "Web server disabled - no WiFi" in content:
            state.http_server_enabled = False
            for i, line in enumerate(lines, 1):
                if "Web server disabled" in line:
                    state.required_changes.append(CodeChange(
                        file="src/main.cpp",
                        line_start=i,
                        line_end=i,
                        change_type="ENABLE_WEB_SERVER",
                        description="Enable HTTP server"
                    ))
                    break
        else:
            # Check if HTTP server is actually initialized
            if "httpServer->begin" in content or "setupApiEndpoints" in content:
                state.http_server_enabled = True

        # Check for wifi_handler.h include
        if '#include "wifi_handler.h"' not in content:
            state.required_changes.append(CodeChange(
                file="src/main.cpp",
                line_start=1,
                line_end=1,
                change_type="ADD_WIFI_INCLUDE",
                description="Add wifi_handler.h include"
            ))

    def _analyze_platformio_ini(self, state: BuildState):
        platformio_ini = self.project_dir / "platformio.ini"
        if not platformio_ini.exists():
            return

        content = platformio_ini.read_text()
        lines = content.split('\n')

        # Check if FlatBuffers is excluded from build
        if "-<**/bpm_flatbuffers.*>" in content:
            state.flatbuffers_included = False
            for i, line in enumerate(lines, 1):
                if "-<**/bpm_flatbuffers.*>" in line:
                    state.required_changes.append(CodeChange(
                        file="platformio.ini",
                        line_start=i,
                        line_end=i,
                        change_type="INCLUDE_FLATBUFFERS",
                        description="Include FlatBuffers in build"
                    ))
                    break
        else:
            state.flatbuffers_included = True

        # Check C++ standard
        cpp_match = re.search(r'-std=c\+\+(\d+)', content)
        if cpp_match:
            state.cpp_standard = f"c++{cpp_match.group(1)}"
            if state.cpp_standard != "c++17":
                for i, line in enumerate(lines, 1):
                    if "-std=c++" in line:
                        state.required_changes.append(CodeChange(
                            file="platformio.ini",
                            line_start=i,
                            line_end=i,
                            change_type="UPDATE_CPP_STANDARD",
                            description="Update C++ standard to C++17"
                        ))
                        break


def main():
    import sys

    project_dir = Path(__file__).parent.parent
    detector = BuildStateDetector(project_dir)
    state = detector.analyze()

    print("=" * 60)
    print("ESP32 BPM Detector - Build State Analysis")
    print("=" * 60)
    print(f"WiFi Enabled:       {'Yes' if state.wifi_enabled else 'No'}")
    print(f"HTTP Server:        {'Yes' if state.http_server_enabled else 'No'}")
    print(f"FlatBuffers:        {'Included' if state.flatbuffers_included else 'Excluded'}")
    print(f"C++ Standard:       {state.cpp_standard}")
    print(f"Ready for WiFi:     {'Yes' if state.is_ready() else 'No'}")
    print()

    if state.required_changes:
        print(f"Required Changes ({len(state.required_changes)}):")
        for change in state.required_changes:
            print(f"  - {change.file}:{change.line_start} - {change.description}")
    else:
        print("No changes required - firmware is ready for WiFi connectivity")

    return 0 if state.is_ready() else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
