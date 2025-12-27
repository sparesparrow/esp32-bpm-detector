# Repository Restructuring Plan: ESP32 BPM Detector Ecosystem

**Date:** 2024  
**Status:** Planning  
**Author:** AI Assistant

---

## Executive Summary

This document outlines a comprehensive plan to restructure the ESP32 BPM Detector monorepo into a modular, maintainable ecosystem of three separate repositories with proper dependency management via Conan. The plan includes multiple alternative approaches and considers integration with existing projects (mia/, sparetools/).

---

## Current State Analysis

### Current Repository Structure

```
esp32-bpm-detector/
├── src/                    # ESP32 firmware (C++)
├── include/                # ESP32 headers
├── android-app/            # Android consumer app (Kotlin)
├── schemas/                # FlatBuffers schemas (.fbs)
│   └── bpm_protocol.fbs
├── scripts/                # Python scripts
│   ├── generate_flatbuffers.py
│   └── run_bpm_tests.py
├── tests/                  # Python tests
├── platformio.ini          # ESP32 build config
└── docs/                   # Documentation
```

### Related Projects

1. **mia/** - Contains:
   - Android app (`android/`)
   - Multiple FlatBuffers schemas (`schemas/mia.fbs`, `protos/vehicle.fbs`)
   - Conan recipes (`conan-recipes/`)

2. **sparetools/** - Contains:
   - Templates (`templates/esp32/`, `templates/android/`)
   - Python packages and scripts
   - Conan profiles (`conan_profiles/`)
   - Shared testing infrastructure

---

## Proposed Structure

### Option A: Three Separate Repositories (Baseline)

#### 1. `sparetools-bpm-schemas` (Shared Schema Repository)
**Purpose:** Centralized FlatBuffers schema definitions for BPM protocol

**Contents:**
```
sparetools-bpm-schemas/
├── schemas/
│   ├── bpm_protocol.fbs          # From esp32-bpm-detector
│   └── README.md
├── conanfile.py                  # Conan package definition
├── CMakeLists.txt                # For C++ consumers
├── build.gradle.kts             # For Android consumers
├── .github/
│   └── workflows/
│       └── publish-conan.yml     # Auto-publish on version tags
├── README.md
└── CHANGELOG.md
```

**Conan Package:**
- **Name:** `sparetools-bpm-schemas`
- **Version:** Semantic versioning (1.0.0+)
- **Provides:** Generated C++ headers, Java/Kotlin classes, Python bindings
- **Dependencies:** `flatbuffers/[>=2.0.0]`

**Benefits:**
- Single source of truth for protocol definitions
- Versioned schema changes
- Easy to consume via Conan
- Supports multiple languages (C++, Java/Kotlin, Python)

---

#### 2. `esp32-bpm-provider` (ESP32 Firmware Repository)
**Purpose:** ESP32 firmware that detects BPM and provides data via FlatBuffers

**Contents:**
```
esp32-bpm-provider/
├── src/                         # ESP32 firmware source
│   ├── bpm_detector.cpp
│   ├── audio_input.cpp
│   ├── api_endpoints.cpp
│   └── main.cpp
├── include/                     # Headers
├── schemas/                     # Symlink or submodule to sparetools-bpm-schemas
├── platformio.ini               # ESP32 build config
├── conanfile.py                 # Consumer of sparetools-bpm-schemas
├── .github/
│   └── workflows/
│       └── ci.yml               # Build and test firmware
├── README.md
└── docs/
    ├── API.md
    └── CALIBRATION.md
```

**Dependencies:**
- `sparetools-bpm-schemas/[>=1.0.0]@sparetools/stable` (via Conan)
- PlatformIO libraries (arduinoFFT, ArduinoJson, flatbuffers)

**Build Process:**
1. Conan installs `sparetools-bpm-schemas` package
2. Generated headers copied to `include/` or linked
3. PlatformIO builds firmware with generated code

---

#### 3. `android-bpm-consumer` (Android App Repository)
**Purpose:** Android application that consumes BPM data from ESP32 provider

**Contents:**
```
android-bpm-consumer/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/            # Kotlin source
│   │   │   └── res/              # Android resources
│   │   └── test/                # Unit tests
│   └── build.gradle.kts
├── build.gradle.kts
├── settings.gradle.kts
├── conanfile.py                 # Consumer of sparetools-bpm-schemas
├── .github/
│   └── workflows/
│       └── android-build.yml    # Build and test Android app
├── README.md
└── docs/
    └── USER_GUIDE.md
```

**Dependencies:**
- `sparetools-bpm-schemas/[>=1.0.0]@sparetools/stable` (via Conan)
- Android libraries (Compose, Retrofit, etc.)

**Build Process:**
1. Conan installs `sparetools-bpm-schemas` package
2. Generated Java/Kotlin classes integrated into Android build
3. Gradle builds APK

**Future Integration:**
- Could merge with `mia/android/` if both apps share common functionality
- Or create `android-mia-consumer` monorepo for multiple Android apps

---

### Option B: Schema Repository as Part of SpareTools

#### Structure:
```
sparetools/
├── packages/
│   ├── schemas/
│   │   ├── bpm/
│   │   │   ├── bpm_protocol.fbs
│   │   │   └── conanfile.py
│   │   ├── mia/
│   │   │   ├── mia.fbs
│   │   │   ├── vehicle.fbs
│   │   │   └── conanfile.py
│   │   └── README.md
│   └── ... (other packages)
├── templates/
│   ├── esp32/
│   │   ├── platformio.ini.template
│   │   └── conanfile.py.template
│   └── android/
│       └── build.gradle.kts.template
└── scripts/
    └── generate_flatbuffers.py  # Shared script
```

**Benefits:**
- Centralized schema management
- Shared templates and scripts
- Unified versioning
- Single Conan remote

**Drawbacks:**
- Larger repository
- More complex dependency management
- Coupling between schemas and tools

---

### Option C: Hybrid Approach (Recommended - Best Balance)

**⭐ RECOMMENDED APPROACH**

This option provides the best balance of modularity, maintainability, and scalability.

#### Structure:
1. **`sparetools-schemas`** - Standalone repository for all schemas
   - Contains: `bpm/`, `mia/`, `vehicle/`, etc.
   - Managed by SpareTools team
   - Published to Conan

2. **`sparetools`** - Tools and templates repository
   - Contains: Templates, scripts, shared tests
   - References schemas via Conan
   - Provides templates for consumers

3. **`esp32-bpm-provider`** - ESP32 firmware (as in Option A)

4. **`android-bpm-consumer`** - Android app (as in Option A)
   - Or merged into `android-mia-consumer` monorepo

**Benefits:**
- Clear separation of concerns
- Schemas versioned independently
- Tools can evolve separately
- Consumers remain lightweight

---

## Detailed Migration Plan

### Phase 1: Schema Repository Setup

#### Step 1.1: Create `sparetools-bpm-schemas` Repository

**Actions:**
1. Create new repository: `sparetools-bpm-schemas`
2. Copy `schemas/bpm_protocol.fbs` from `esp32-bpm-detector`
3. Create `conanfile.py`:

```python
from conan import ConanFile
from conan.tools.files import copy, save
from conan.tools.cmake import CMakeToolchain, CMakeDeps
from conan.tools.scm import Git
import os
import subprocess
from pathlib import Path

class SparetoolsBpmSchemasConan(ConanFile):
    name = "sparetools-bpm-schemas"
    version = "1.0.0"
    description = "FlatBuffers schemas for BPM detection protocol"
    license = "MIT"
    url = "https://github.com/sparetools/sparetools-bpm-schemas"
    homepage = "https://github.com/sparetools/sparetools-bpm-schemas"
    
    # Package metadata
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "schemas/*"
    
    def requirements(self):
        # FlatBuffers is a build tool, not a runtime dependency
        self.tool_requires("flatbuffers/[>=2.0.0]")
    
    def build_requirements(self):
        self.tool_requires("flatbuffers/[>=2.0.0]")
    
    def build(self):
        # Generate code from FlatBuffers schemas
        self._generate_cpp_code()
        self._generate_java_code()
        self._generate_python_code()
    
    def _generate_cpp_code(self):
        """Generate C++ headers from .fbs files"""
        flatc = self.dependencies.build["flatbuffers"].cpp_info.bindirs[0] + "/flatc"
        schema_dir = Path(self.source_folder) / "schemas"
        output_dir = Path(self.build_folder) / "generated" / "cpp"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for fbs_file in schema_dir.glob("*.fbs"):
            cmd = [
                flatc,
                "--cpp",
                "--gen-object-api",
                "--gen-mutable",
                "--scoped-enums",
                "--cpp-std", "c++17",
                "-o", str(output_dir),
                str(fbs_file)
            ]
            self.output.info(f"Generating C++ code from {fbs_file.name}...")
            subprocess.run(cmd, check=True)
    
    def _generate_java_code(self):
        """Generate Java classes from .fbs files"""
        flatc = self.dependencies.build["flatbuffers"].cpp_info.bindirs[0] + "/flatc"
        schema_dir = Path(self.source_folder) / "schemas"
        output_dir = Path(self.build_folder) / "generated" / "java"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for fbs_file in schema_dir.glob("*.fbs"):
            cmd = [
                flatc,
                "--java",
                "--gen-mutable",
                "-o", str(output_dir),
                str(fbs_file)
            ]
            self.output.info(f"Generating Java code from {fbs_file.name}...")
            subprocess.run(cmd, check=True)
    
    def _generate_python_code(self):
        """Generate Python modules from .fbs files"""
        flatc = self.dependencies.build["flatbuffers"].cpp_info.bindirs[0] + "/flatc"
        schema_dir = Path(self.source_folder) / "schemas"
        output_dir = Path(self.build_folder) / "generated" / "python"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for fbs_file in schema_dir.glob("*.fbs"):
            cmd = [
                flatc,
                "--python",
                "-o", str(output_dir),
                str(fbs_file)
            ]
            self.output.info(f"Generating Python code from {fbs_file.name}...")
            subprocess.run(cmd, check=True)
    
    def package(self):
        # Copy schema files
        copy(self, "*.fbs", 
             src=Path(self.source_folder) / "schemas",
             dst=Path(self.package_folder) / "schemas")
        
        # Copy generated C++ headers
        copy(self, "*.h", 
             src=Path(self.build_folder) / "generated" / "cpp",
             dst=Path(self.package_folder) / "include")
        
        # Copy generated Java classes
        copy(self, "*.java", 
             src=Path(self.build_folder) / "generated" / "java",
             dst=Path(self.package_folder) / "java")
        
        # Copy generated Python modules
        copy(self, "*.py", 
             src=Path(self.build_folder) / "generated" / "python",
             dst=Path(self.package_folder) / "python")
        
        # Create package_info file for consumers
        self._create_package_info()
    
    def _create_package_info(self):
        """Create metadata file for package consumers"""
        info = {
            "schema_version": self.version,
            "schemas": [f.name for f in Path(self.source_folder).glob("schemas/*.fbs")],
            "generated_languages": ["cpp", "java", "python"]
        }
        save(self, Path(self.package_folder) / "package_info.json", str(info))
    
    def package_info(self):
        # C++ consumers
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = []  # Headers only, no libraries
        
        # Java consumers (via Conan imports)
        self.java_info.classdirs = ["java"]
        
        # Python consumers
        self.python_info.requires = ["flatbuffers"]
        
        # Package metadata
        self.cpp_info.set_property("cmake_target_name", "sparetools::bpm-schemas")
        self.cpp_info.set_property("pkg_config_name", "sparetools-bpm-schemas")
```

4. Set up GitHub Actions for auto-publishing to Conan
5. Create README with usage instructions

**Timeline:** 1-2 days

---

#### Step 1.2: Migrate MIA Schemas (Optional)

**Actions:**
1. Review `mia/schemas/` and `mia/protos/`
2. Decide if schemas should be merged or kept separate
3. If merged: Add to `sparetools-bpm-schemas` or create `sparetools-mia-schemas`
4. If separate: Create `sparetools-schemas` monorepo with subdirectories

**Decision Points:**
- Are MIA schemas related to BPM? (Probably not)
- Should they share versioning? (Probably not)
- **Recommendation:** Keep separate or create `sparetools-schemas` monorepo

**Timeline:** 1 day (if separate)

---

### Phase 2: ESP32 Provider Repository

#### Step 2.1: Create `esp32-bpm-provider` Repository

**Actions:**
1. Create new repository: `esp32-bpm-provider`
2. Copy ESP32 firmware files:
   ```
   - src/ → esp32-bpm-provider/src/
   - include/ → esp32-bpm-provider/include/
   - platformio.ini → esp32-bpm-provider/
   - docs/ → esp32-bpm-provider/docs/
   ```
3. Create `conanfile.py`:

```python
from conan import ConanFile
from conan.tools.files import copy, save
from conan.tools.cmake import CMakeToolchain, CMakeDeps
from pathlib import Path

class Esp32BpmProviderConan(ConanFile):
    name = "esp32-bpm-provider"
    version = "1.0.0"
    description = "ESP32 firmware for BPM detection"
    license = "MIT"
    
    settings = "os", "arch", "compiler", "build_type"
    
    # Dependencies
    requires = (
        "sparetools-bpm-schemas/[>=1.0.0 <2.0.0]@sparetools/stable",
        "flatbuffers/[>=2.0.0]",  # Runtime dependency
    )
    
    # Build tool requirements
    tool_requires = (
        "platformio/[>=6.0.0]",  # If using PlatformIO via Conan
    )
    
    def configure(self):
        # ESP32-specific settings
        self.settings.os = "FreeRTOS"  # Or "Linux" for ESP-IDF
        self.settings.arch = "armv7"   # ESP32 architecture
    
    def generate(self):
        # Generate CMake toolchain (if using CMake)
        tc = CMakeToolchain(self)
        tc.generate()
        
        # Generate CMake dependencies
        deps = CMakeDeps(self)
        deps.generate()
        
        # Copy schema headers to PlatformIO include directory
        self._copy_schema_headers()
    
    def _copy_schema_headers(self):
        """Copy generated headers to PlatformIO include directory"""
        schema_pkg = self.dependencies["sparetools-bpm-schemas"]
        
        # Get include directory from schema package
        include_src = Path(schema_pkg.package_folder) / "include"
        include_dst = Path(self.build_folder) / "include" / "bpm_schemas"
        include_dst.mkdir(parents=True, exist_ok=True)
        
        # Copy all header files
        if include_src.exists():
            copy(self, "*.h", 
                 src=include_src,
                 dst=include_dst)
            self.output.info(f"Copied schema headers to {include_dst}")
    
    def imports(self):
        """Copy dependencies to build directory (for PlatformIO)"""
        # Copy schema headers
        self.copy("*.h", 
                  dst="include/bpm_schemas",
                  src="include",
                  root_package="sparetools-bpm-schemas")
        
        # Copy schema source files if needed
        self.copy("*.cpp", 
                  dst="src/bpm_schemas",
                  src="src",
                  root_package="sparetools-bpm-schemas",
                  keep_path=False)
    
    def package_info(self):
        # Provide include directories for consumers
        self.cpp_info.includedirs = ["include"]
        
        # PlatformIO-specific information
        self.cpp_info.set_property("pkg_config_name", "esp32-bpm-provider")
```

4. Update `platformio.ini` to use Conan dependencies
5. Update includes in source files to use Conan-provided headers
6. Set up CI/CD for firmware builds

**Timeline:** 2-3 days

---

#### Step 2.2: Migrate Python Scripts and Tests

**Decision:** Where should Python scripts go?

**Option 2.2A: Keep in Provider Repository**
- `esp32-bpm-provider/scripts/` - Provider-specific scripts
- `esp32-bpm-provider/tests/` - Provider-specific tests

**Option 2.2B: Move to SpareTools** (Recommended)
- `sparetools/scripts/bpm/` - Shared scripts
- `sparetools/test/bpm/` - Shared tests
- Provider repo references via Conan or git submodule

**Recommendation:** Option 2.2B - Keep shared scripts in SpareTools

**Actions:**
1. Move `scripts/generate_flatbuffers.py` → `sparetools/scripts/bpm/`
2. Move `scripts/run_bpm_tests.py` → `sparetools/test/bpm/`
3. Update paths and imports
4. Update documentation

**Timeline:** 1 day

---

### Phase 3: Android Consumer Repository

#### Step 3.1: Create `android-bpm-consumer` Repository

**Actions:**
1. Create new repository: `android-bpm-consumer`
2. Copy Android app files:
   ```
   - android-app/app/ → android-bpm-consumer/app/
   - android-app/build.gradle → android-bpm-consumer/
   - android-app/settings.gradle → android-bpm-consumer/
   ```
3. Create `conanfile.py` for Android:

```python
from conans import ConanFile

class AndroidBpmConsumerConan(ConanFile):
    name = "android-bpm-consumer"
    version = "1.0.0"
    requires = "sparetools-bpm-schemas/[>=1.0.0]@sparetools/stable"
    
    def imports(self):
        # Copy generated Java/Kotlin classes
        self.copy("*.java", dst="app/src/main/java", root_package="sparetools-bpm-schemas")
        self.copy("*.kt", dst="app/src/main/java", root_package="sparetools-bpm-schemas")
```

4. Update Gradle build to use Conan-generated classes
5. Set up CI/CD for Android builds

**Timeline:** 2-3 days

---

#### Step 3.2: Consider MIA Android App Integration

**Decision:** Should `mia/android/` be merged?

**Option 3.2A: Separate Repositories**
- `android-bpm-consumer/` - BPM app only
- `android-mia-consumer/` - MIA app only
- Both consume `sparetools-bpm-schemas` or `sparetools-mia-schemas`

**Option 3.2B: Unified Android Consumer**
- `android-mia-consumer/` - Monorepo with multiple apps
  ```
  android-mia-consumer/
  ├── apps/
  │   ├── bpm/              # BPM app
  │   └── mia/              # MIA app
  ├── shared/               # Shared Android code
  └── build.gradle.kts      # Multi-module build
  ```

**Option 3.2C: Keep Separate, Share Common Library**
- `android-bpm-consumer/` - BPM app
- `android-mia-consumer/` - MIA app
- `android-mia-shared/` - Shared Android library (if needed)
- Both consume respective schema packages

**Recommendation:** Option 3.2A or 3.2C - Keep separate unless there's significant code sharing

**Timeline:** 1-2 days (if merging)

---

### Phase 4: SpareTools Integration

#### Step 4.1: Move Shared Scripts to SpareTools

**Actions:**
1. Create `sparetools/scripts/bpm/`:
   ```
   sparetools/scripts/bpm/
   ├── generate_flatbuffers.py    # From esp32-bpm-detector
   ├── run_bpm_tests.py           # From esp32-bpm-detector
   └── README.md
   ```

2. Create `sparetools/test/bpm/`:
   ```
   sparetools/test/bpm/
   ├── test_bpm_accuracy.py
   ├── test_network_client.py
   └── README.md
   ```

3. Update scripts to work from SpareTools location
4. Add documentation

**Timeline:** 1 day

---

#### Step 4.2: Enhance Templates

**Actions:**
1. Update `sparetools/templates/esp32/`:
   - Add `conanfile.py.template` with schema dependency example
   - Update `platformio.ini.template` with Conan integration
   - Add README with usage

2. Update `sparetools/templates/android/`:
   - Add `conanfile.py.template` for Android
   - Update `build.gradle.kts.template` with Conan integration
   - Add README with usage

3. Create example projects using templates

**Timeline:** 2 days

---

## Alternative Approaches

### Alternative 1: Monorepo with Submodules

**Structure:**
```
esp32-bpm-ecosystem/          # Monorepo
├── schemas/                  # Git submodule → sparetools-bpm-schemas
├── esp32-provider/           # ESP32 firmware
├── android-consumer/          # Android app
└── scripts/                  # Shared scripts (or submodule to sparetools)
```

**Pros:**
- Single repository for related code
- Easier cross-repo changes
- Simplified CI/CD

**Cons:**
- Still need to manage submodules
- Doesn't solve dependency management
- Less modular

**Recommendation:** Not recommended - defeats purpose of separation

---

### Alternative 2: Git Submodules for Schemas

**Structure:**
```
esp32-bpm-provider/
├── schemas/                  # Git submodule → sparetools-bpm-schemas
└── ...

android-bpm-consumer/
├── schemas/                  # Git submodule → sparetools-bpm-schemas
└── ...
```

**Pros:**
- Simple to set up
- No Conan required
- Direct access to schema files

**Cons:**
- No versioning control
- Manual updates required
- Doesn't provide generated code
- Submodule management complexity

**Recommendation:** Not recommended - Conan is better for dependency management

---

### Alternative 3: Schema in SpareTools Packages

**Structure:**
```
sparetools/
├── packages/
│   └── schemas/
│       └── bpm/
│           ├── bpm_protocol.fbs
│           └── conanfile.py
```

**Pros:**
- Centralized with other SpareTools packages
- Unified versioning
- Shared infrastructure

**Cons:**
- Couples schemas to SpareTools
- Less flexible for external consumers
- Larger repository

**Recommendation:** Consider if schemas are SpareTools-specific only

---

### Alternative 4: Unified Schema Monorepo (NEW PROPOSAL)

**Structure:**
```
sparetools-schemas/              # Single repository for all schemas
├── bpm/
│   ├── bpm_protocol.fbs
│   ├── conanfile.py
│   └── README.md
├── mia/
│   ├── mia.fbs
│   ├── vehicle.fbs
│   ├── conanfile.py
│   └── README.md
├── common/                      # Shared schema components
│   ├── headers.fbs
│   └── errors.fbs
├── .github/
│   └── workflows/
│       └── publish-all.yml     # Publish all schema packages
├── scripts/
│   └── generate-all.sh         # Generate code for all schemas
└── README.md
```

**Conan Packages:**
- `sparetools-bpm-schemas/[>=1.0.0]@sparetools/stable`
- `sparetools-mia-schemas/[>=1.0.0]@sparetools/stable`
- `sparetools-common-schemas/[>=1.0.0]@sparetools/stable` (if needed)

**Benefits:**
- Single repository for all schemas
- Shared common components (headers, errors)
- Unified CI/CD for all schema packages
- Easier cross-schema dependencies
- Single place to manage schema versions

**Drawbacks:**
- Larger repository
- More complex Conan package structure
- Requires careful namespace management

**Recommendation:** **STRONGLY RECOMMENDED** if you have multiple schema projects (BPM, MIA, etc.)

**Implementation:**
- Each subdirectory (`bpm/`, `mia/`) is a separate Conan package
- Common schemas can be shared via Conan dependencies
- GitHub Actions can publish all packages on version tags

---

### Alternative 5: Bazel Monorepo (NEW PROPOSAL)

**Structure:**
```
esp32-bpm-ecosystem/            # Bazel monorepo
├── WORKSPACE
├── schemas/
│   ├── bpm/
│   │   ├── BUILD.bazel
│   │   └── bpm_protocol.fbs
│   └── BUILD.bazel
├── providers/
│   └── esp32/
│       ├── BUILD.bazel
│       └── src/
├── consumers/
│   └── android/
│       ├── BUILD.bazel
│       └── app/
└── tools/
    └── BUILD.bazel
```

**Benefits:**
- Single repository with proper dependency management
- Bazel handles code generation and builds
- Excellent caching and parallel builds
- Cross-language support (C++, Java/Kotlin, Python)

**Drawbacks:**
- Requires Bazel expertise
- Different build system than PlatformIO/Gradle
- May require significant refactoring

**Recommendation:** Consider if you're already using Bazel or planning to adopt it

---

### Alternative 6: Nx Monorepo (NEW PROPOSAL)

**Structure:**
```
esp32-bpm-ecosystem/            # Nx monorepo
├── nx.json
├── packages/
│   ├── schemas-bpm/
│   ├── provider-esp32/
│   └── consumer-android/
└── tools/
    └── generate-schemas/
```

**Benefits:**
- Excellent dependency graph management
- Built-in code generation support
- Task orchestration
- Good for TypeScript/JavaScript ecosystems

**Drawbacks:**
- Primarily for JavaScript/TypeScript
- Less suitable for C++/embedded systems
- Requires Nx setup

**Recommendation:** Not recommended for this C++/embedded project

---

## Dependency Management Strategy

### Conan Configuration

#### Conan Remote Setup

```bash
# Add SpareTools Conan remote
conan remote add sparetools https://conan.sparetools.io

# Or use GitHub Packages
conan remote add sparetools https://maven.pkg.github.com/sparetools
```

#### Version Management

**Schema Versions:**
- Semantic versioning: `1.0.0`, `1.1.0`, `2.0.0`
- Breaking changes increment major version
- Consumers pin to compatible versions

**Consumer Versions:**
- Independent versioning
- Can update schema dependency independently
- Use version ranges: `sparetools-bpm-schemas/[>=1.0.0 <2.0.0]`

---

### Build Integration

#### ESP32 (PlatformIO + Conan)

**platformio.ini:**
```ini
[env:esp32-s3]
platform = espressif32@6.4.0
board = esp32-s3-devkitc-1
framework = arduino
extra_scripts = 
    pre:scripts/conan_install.py
build_flags = 
    -I${PROJECT_DIR}/.conan/include
lib_deps = 
    kosme/arduinoFFT@^1.6.2
```

**scripts/conan_install.py:**
```python
Import("env")
import subprocess
import os
from pathlib import Path

def conan_install():
    """Install Conan dependencies before PlatformIO build"""
    project_dir = Path(env["PROJECT_DIR"])
    conanfile = project_dir / "conanfile.py"
    
    if not conanfile.exists():
        print("⚠️  No conanfile.py found, skipping Conan install")
        return
    
    print("📦 Installing Conan dependencies...")
    
    # Conan install command
    cmd = [
        "conan", "install", ".",
        "--build=missing",
        "--output-folder", str(project_dir / ".conan"),
        "--settings", "os=FreeRTOS",
        "--settings", "arch=armv7",
    ]
    
    # Add remote if configured
    remote = os.environ.get("CONAN_REMOTE", "sparetools")
    if remote:
        cmd.extend(["--remote", remote])
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(project_dir),
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ Conan dependencies installed successfully")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Conan install failed: {e}")
        print(e.stderr)
        env.Exit(1)
    except FileNotFoundError:
        print("⚠️  Conan not found in PATH. Install Conan: pip install conan")
        print("   Skipping Conan install - using PlatformIO libraries only")
        return

# Run Conan install before build
conan_install()

# Add Conan include directories to build flags
conan_include = Path(env["PROJECT_DIR"]) / ".conan" / "include"
if conan_include.exists():
    env.Append(CPPPATH=[str(conan_include)])
    print(f"✅ Added Conan include path: {conan_include}")
```

#### Android (Gradle + Conan)

**build.gradle.kts:**
```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

// Conan integration task
tasks.register<Exec>("conanInstall") {
    group = "build"
    description = "Install Conan dependencies"
    
    commandLine(
        "conan", "install", ".",
        "--build=missing",
        "--output-folder", ".conan",
        "--settings", "os=Android",
        "--settings", "arch=armv8",  // or armv7 for 32-bit
    )
    
    // Add remote if configured
    val conanRemote = project.findProperty("conan.remote") as String? ?: "sparetools"
    args("--remote", conanRemote)
    
    doFirst {
        println("📦 Installing Conan dependencies...")
    }
    
    doLast {
        println("✅ Conan dependencies installed")
    }
}

// Copy generated Java/Kotlin classes to source directory
tasks.register<Copy>("copyConanGeneratedClasses") {
    group = "build"
    description = "Copy Conan-generated Java/Kotlin classes to source directory"
    
    dependsOn("conanInstall")
    
    from(".conan/java") {
        include("**/*.java")
    }
    into("app/src/main/java/com/sparetools/bpm/schemas")
    
    doFirst {
        println("📋 Copying Conan-generated classes...")
    }
    
    doLast {
        println("✅ Classes copied to source directory")
    }
}

// Make preBuild depend on Conan tasks
tasks.named("preBuild") {
    dependsOn("conanInstall", "copyConanGeneratedClasses")
}

// Android configuration
android {
    namespace = "com.sparesparrow.bpmdetector"
    compileSdk = 34
    
    defaultConfig {
        applicationId = "com.sparesparrow.bpmdetector"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
    }
    
    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    
    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    // Conan-provided dependencies (via imports)
    implementation(fileTree(mapOf("dir" to ".conan/lib", "include" to listOf("*.jar"))))
    
    // Android dependencies
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.compose.ui:ui:1.5.4")
    // ... other dependencies
}
```

**Alternative: Conan Gradle Plugin**

For better integration, consider using a Conan Gradle plugin:

```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("io.github.conan-gradle-plugin") version "1.0.0"  // If available
}

conan {
    profile = "android"
    remote = "sparetools"
    requires = listOf("sparetools-bpm-schemas/[>=1.0.0]@sparetools/stable")
}
```

---

## Migration Checklist

### Pre-Migration

- [ ] Review all FlatBuffers schemas across projects
- [ ] Identify shared vs. project-specific schemas
- [ ] Decide on schema repository structure (separate vs. monorepo)
- [ ] Set up Conan remote/registry
- [ ] Create migration branch in esp32-bpm-detector

### Schema Repository

- [ ] Create `sparetools-bpm-schemas` repository
- [ ] Copy `bpm_protocol.fbs`
- [ ] Create `conanfile.py`
- [ ] Set up code generation (C++, Java/Kotlin, Python)
- [ ] Create GitHub Actions for publishing
- [ ] Publish initial version (1.0.0)
- [ ] Write README and usage docs

### ESP32 Provider

- [ ] Create `esp32-bpm-provider` repository
- [ ] Copy ESP32 firmware files
- [ ] Create `conanfile.py`
- [ ] Update includes to use Conan-provided headers
- [ ] Update `platformio.ini` for Conan integration
- [ ] Test build with Conan dependency
- [ ] Set up CI/CD
- [ ] Update documentation

### Android Consumer

- [ ] Create `android-bpm-consumer` repository
- [ ] Copy Android app files
- [ ] Create `conanfile.py`
- [ ] Update Gradle build for Conan
- [ ] Test build with Conan dependency
- [ ] Set up CI/CD
- [ ] Update documentation

### SpareTools Integration

- [ ] Move Python scripts to `sparetools/scripts/bpm/`
- [ ] Move tests to `sparetools/test/bpm/`
- [ ] Update templates with Conan examples
- [ ] Create example projects
- [ ] Update SpareTools documentation

### Post-Migration

- [ ] Archive old `esp32-bpm-detector` repository (or mark as deprecated)
- [ ] Update all documentation links
- [ ] Notify team members
- [ ] Create migration guide for users
- [ ] Monitor for issues

---

## Risk Assessment

### High Risk

1. **Breaking Changes During Migration**
   - **Mitigation:** Maintain backward compatibility, use feature flags
   - **Rollback:** Keep old repo as backup

2. **Conan Integration Complexity**
   - **Mitigation:** Start simple, add complexity gradually
   - **Testing:** Test builds in CI before migration

3. **Lost Functionality**
   - **Mitigation:** Comprehensive migration checklist
   - **Testing:** Run full test suite after migration

### Medium Risk

1. **Version Mismatches**
   - **Mitigation:** Pin versions initially, use ranges later
   - **Monitoring:** CI checks for version compatibility

2. **Build Time Increases**
   - **Mitigation:** Cache Conan packages, use pre-built binaries
   - **Optimization:** Parallel builds, incremental compilation

### Low Risk

1. **Documentation Gaps**
   - **Mitigation:** Update docs as part of migration
   - **Review:** Peer review of documentation

---

## Timeline Estimate

### Phase 1: Schema Repository (Week 1)
- Day 1-2: Create repository, set up Conan package
- Day 3-4: Set up CI/CD, publish first version
- Day 5: Documentation and testing

### Phase 2: ESP32 Provider (Week 2)
- Day 1-2: Create repository, migrate code
- Day 3: Conan integration, build fixes
- Day 4-5: CI/CD setup, testing

### Phase 3: Android Consumer (Week 2-3)
- Day 1-2: Create repository, migrate code
- Day 3: Conan integration, Gradle setup
- Day 4-5: CI/CD setup, testing

### Phase 4: SpareTools Integration (Week 3)
- Day 1: Move scripts and tests
- Day 2-3: Update templates
- Day 4-5: Documentation and examples

### Phase 5: Cleanup and Documentation (Week 4)
- Day 1-2: Final testing, bug fixes
- Day 3-4: Documentation updates
- Day 5: Migration announcement, deprecation notices

**Total Estimated Time:** 4 weeks

---

## Decision Matrix

### Schema Repository Options

| Option | Modularity | Maintainability | Scalability | Complexity | Recommendation |
|--------|------------|------------------|-------------|------------|----------------|
| **Option A: Separate Repos** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Good baseline |
| **Option B: In SpareTools** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | Good for tight coupling |
| **Option C: Hybrid** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **⭐ BEST** |
| **Alt 4: Unified Monorepo** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | **⭐ BEST for multiple schemas** |
| **Alt 5: Bazel Monorepo** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | Good if using Bazel |
| **Alt 6: Nx Monorepo** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Not suitable for C++ |

### Android App Integration Options

| Option | Code Sharing | Maintainability | CI/CD Complexity | Recommendation |
|--------|--------------|-----------------|-------------------|----------------|
| **Separate Repos** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **⭐ BEST** - Start here |
| **Unified Monorepo** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Good if >50% code shared |
| **Shared Library** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Good middle ground |

---

## Recommendations Summary

### 🏆 Primary Recommendation: **Option C (Hybrid) with Alternative 4 Consideration**

**For Single Schema Project (BPM only):**
- Use **Option C (Hybrid)** - Three separate repositories
- Best balance of modularity and simplicity

**For Multiple Schema Projects (BPM + MIA + others):**
- Use **Alternative 4 (Unified Schema Monorepo)** - Single schema repository
- Better for managing multiple related schemas
- Easier to maintain common components

1. **Create `sparetools-bpm-schemas`** as standalone repository
   - Independent versioning
   - Published to Conan
   - Supports multiple consumers

2. **Create `esp32-bpm-provider`** repository
   - Consumes schemas via Conan
   - Focused on ESP32 firmware
   - Independent CI/CD

3. **Create `android-bpm-consumer`** repository
   - Consumes schemas via Conan
   - Focused on Android app
   - Independent CI/CD

4. **Move shared scripts to `sparetools`**
   - `sparetools/scripts/bpm/` - Scripts
   - `sparetools/test/bpm/` - Tests
   - Shared infrastructure

5. **Enhance SpareTools templates**
   - Add Conan integration examples
   - Provide templates for new consumers

### Future Considerations

1. **MIA Integration:**
   - Keep MIA schemas separate (`sparetools-mia-schemas`)
   - Or create `sparetools-schemas` monorepo with subdirectories
   - Android apps remain separate unless significant code sharing

2. **Other Projects:**
   - Scan for other projects using FlatBuffers
   - Consider unified schema repository if patterns emerge
   - Keep provider/consumer separation

3. **Template Evolution:**
   - SpareTools templates should evolve based on consumer needs
   - Regular updates as best practices emerge
   - Version templates alongside schemas

---

## Next Steps

1. **Review this plan** with team
2. **Decide on schema repository structure** (separate vs. monorepo)
3. **Set up Conan infrastructure** (remote, CI/CD)
4. **Create migration branch** in esp32-bpm-detector
5. **Start with Phase 1** (Schema repository)
6. **Iterate and adjust** based on learnings

---

## Enhanced Implementation Details

### Schema Repository CI/CD (GitHub Actions)

**`.github/workflows/publish-conan.yml`:**
```yaml
name: Publish Schema Package

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to publish'
        required: true

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Conan
        run: |
          pip install conan
          conan profile detect --force
      
      - name: Configure Conan remote
        run: |
          conan remote add sparetools ${{ secrets.CONAN_REMOTE_URL }} || true
          conan user -p ${{ secrets.CONAN_PASSWORD }} -r sparetools ${{ secrets.CONAN_USERNAME }}
      
      - name: Extract version from tag
        id: version
        if: startsWith(github.ref, 'refs/tags/')
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          echo "version=$VERSION" >> $GITHUB_OUTPUT
      
      - name: Update conanfile.py version
        run: |
          sed -i "s/version = \".*\"/version = \"${{ steps.version.outputs.version || github.event.inputs.version }}\"/" conanfile.py
      
      - name: Create Conan package
        run: |
          conan create . --user sparetools --channel stable
      
      - name: Upload to Conan remote
        run: |
          conan upload "sparetools-bpm-schemas/${{ steps.version.outputs.version || github.event.inputs.version }}@sparetools/stable" \
            --remote sparetools --all --confirm
```

### Migration Scripts

**`scripts/migrate-to-provider.sh`:**
```bash
#!/bin/bash
# Migration script: esp32-bpm-detector → esp32-bpm-provider

set -e

SOURCE_REPO="../esp32-bpm-detector"
TARGET_REPO="../esp32-bpm-provider"

echo "🚀 Starting migration to esp32-bpm-provider..."

# Create target repository structure
mkdir -p "$TARGET_REPO"/{src,include,docs,.github/workflows}

# Copy ESP32 firmware files
echo "📋 Copying ESP32 firmware files..."
cp -r "$SOURCE_REPO/src"/* "$TARGET_REPO/src/"
cp -r "$SOURCE_REPO/include"/* "$TARGET_REPO/include/"
cp "$SOURCE_REPO/platformio.ini" "$TARGET_REPO/"

# Copy documentation
echo "📚 Copying documentation..."
cp -r "$SOURCE_REPO/docs"/* "$TARGET_REPO/docs/"

# Create conanfile.py
echo "📦 Creating conanfile.py..."
cat > "$TARGET_REPO/conanfile.py" << 'EOF'
# Generated during migration - update as needed
from conan import ConanFile
# ... (use template from plan)
EOF

# Update platformio.ini for Conan
echo "🔧 Updating platformio.ini..."
# Add Conan integration script reference

# Create .gitignore
echo "📝 Creating .gitignore..."
cat > "$TARGET_REPO/.gitignore" << 'EOF'
.conan/
.pio/
*.bin
*.elf
EOF

echo "✅ Migration complete!"
echo "Next steps:"
echo "1. Review and update conanfile.py"
echo "2. Test build: cd $TARGET_REPO && pio run"
echo "3. Commit and push to new repository"
```

**`scripts/migrate-to-consumer.sh`:**
```bash
#!/bin/bash
# Migration script: esp32-bpm-detector/android-app → android-bpm-consumer

set -e

SOURCE_REPO="../esp32-bpm-detector/android-app"
TARGET_REPO="../android-bpm-consumer"

echo "🚀 Starting migration to android-bpm-consumer..."

# Copy Android app
echo "📋 Copying Android app files..."
cp -r "$SOURCE_REPO"/* "$TARGET_REPO/"

# Create conanfile.py
echo "📦 Creating conanfile.py..."
# ... (similar to above)

echo "✅ Migration complete!"
```

### Versioning Strategy

**Semantic Versioning:**
- **Major (X.0.0):** Breaking schema changes, incompatible API changes
- **Minor (0.X.0):** New schema fields (backward compatible), new features
- **Patch (0.0.X):** Bug fixes, documentation updates

**Version Compatibility Matrix:**

| Schema Version | ESP32 Provider | Android Consumer | Compatibility |
|----------------|----------------|------------------|---------------|
| 1.0.0          | 1.0.0+         | 1.0.0+           | ✅ Full       |
| 1.1.0          | 1.0.0+         | 1.0.0+           | ✅ Compatible |
| 2.0.0          | 1.x.x          | 1.x.x            | ❌ Breaking   |
| 2.0.0          | 2.0.0+         | 2.0.0+           | ✅ Full       |

**Conan Version Ranges:**
```python
# Conservative (recommended for production)
requires = "sparetools-bpm-schemas/[>=1.0.0 <2.0.0]@sparetools/stable"

# Latest minor (for development)
requires = "sparetools-bpm-schemas/[>=1.0.0 <1.1.0]@sparetools/stable"

# Latest patch (most restrictive)
requires = "sparetools-bpm-schemas/1.0.0@sparetools/stable"
```

---

## Questions for Discussion

1. **Schema Repository Structure:**
   - Should MIA schemas be in the same repository as BPM schemas? → **Recommendation: Use Alternative 4 (Unified Monorepo) if multiple schemas**
   - Should we create `sparetools-schemas` monorepo or keep separate? → **Recommendation: Monorepo if >2 schema projects**

2. **Android App Integration:**
   - Should Android apps be merged or kept separate? → **Recommendation: Keep separate initially, merge if >50% code shared**
   - Should we create shared Android library? → **Recommendation: Yes, if common UI/network code emerges**

3. **Conan Infrastructure:**
   - What Conan remote/registry should we use? → **Options:**
     - GitHub Packages (easiest, free for public repos)
     - JFrog Artifactory (enterprise, better for private)
     - ConanCenter (public, but requires approval)
     - **Recommendation: Start with GitHub Packages**

4. **Versioning Strategy:**
   - How should we handle versioning across repositories? → **Recommendation: Independent versioning with compatibility matrix**
   - Should schemas and consumers share version numbers? → **Recommendation: No, independent versioning**

5. **Migration Strategy:**
   - Should we maintain backward compatibility during migration? → **Recommendation: Yes, use feature flags**
   - What's the priority: speed or thoroughness? → **Recommendation: Thoroughness - 4 weeks is acceptable**

6. **Build System Integration:**
   - Should we use Conan exclusively or hybrid with PlatformIO/Gradle? → **Recommendation: Hybrid - Conan for schemas, native tools for builds**
   - Should we migrate to Bazel/CMake? → **Recommendation: Not initially, consider if complexity grows**

---

---

## Additional Resources

### Conan Best Practices

1. **Profile Management:**
   ```bash
   # Create ESP32 profile
   conan profile new esp32 --detect
   conan profile update settings.os=FreeRTOS esp32
   conan profile update settings.arch=armv7 esp32
   
   # Create Android profile
   conan profile new android --detect
   conan profile update settings.os=Android android
   conan profile update settings.arch=armv8 android
   ```

2. **Lock Files for Reproducible Builds:**
   ```bash
   # Generate lock file
   conan lock create conanfile.py --lockfile conan.lock
   
   # Use lock file in CI/CD
   conan install . --lockfile conan.lock
   ```

3. **Cache Management:**
   ```bash
   # Clear cache if needed
   conan remove "*" -f
   
   # List installed packages
   conan search "*" -r sparetools
   ```

### Testing Strategy

1. **Schema Package Testing:**
   - Unit tests for generated code (C++, Java, Python)
   - Schema validation tests
   - Compatibility tests across versions

2. **Provider Testing:**
   - Hardware-in-the-loop tests
   - Mock schema data tests
   - Integration tests with actual ESP32

3. **Consumer Testing:**
   - Unit tests for Android app
   - Integration tests with mock provider
   - End-to-end tests with real hardware

### Rollback Plan

If migration fails:

1. **Immediate Rollback:**
   - Keep old repository active
   - Revert Conan dependencies
   - Use git submodules as temporary solution

2. **Partial Rollback:**
   - Keep schemas in old repo
   - Migrate only provider/consumer
   - Use git submodules for schemas

3. **Full Rollback:**
   - Archive new repositories
   - Restore old repository
   - Document lessons learned

---

**Document Status:** Enhanced with Proposals and Alternatives  
**Last Updated:** 2024  
**Version:** 2.0
