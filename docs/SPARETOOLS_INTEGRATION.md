# SpareTools Utilities Integration

## Overview

This project integrates shared utilities from the **SpareTools** ecosystem, available via Conan2 from Cloudsmith. This provides consistent tooling, logging, subprocess handling, and configuration management across all SpareTools projects.

---

## Available Utilities

### 1. Logging (`SpareToolsLogger`)

**Standardized logging** for all SpareTools projects:

```python
from sparetools_utils import setup_logging

logger = setup_logging(__name__, level=logging.INFO, log_file="app.log")
logger.info("Application started")
logger.error("Error occurred")
```

**Features:**
- Consistent log format across projects
- Console and file handlers
- Standardized timestamps and log levels

### 2. Subprocess (`SpareToolsSubprocess`)

**Standardized subprocess execution** with error handling:

```python
from sparetools_utils import run_command

result = run_command(
    ["pio", "run", "--environment", "esp32-s3"],
    cwd=project_root,
    timeout=900,
    check=False
)

if result.returncode == 0:
    print("Build successful")
else:
    print(f"Build failed: {result.stderr}")
```

**Features:**
- Automatic timeout handling
- Standardized error messages
- Consistent return value format

### 3. Path Utilities (`SpareToolsPaths`)

**Project path management**:

```python
from sparetools_utils import get_project_root

# Automatically finds project root (conanfile.py or .git)
project_root = get_project_root(Path(__file__).parent)
```

**Features:**
- Automatic project root detection
- Directory creation utilities
- Cross-platform path handling

### 4. Configuration (`SpareToolsConfig`)

**JSON configuration management**:

```python
from sparetools_utils import load_config, save_config

# Load configuration
config = load_config(Path("config.json"))

# Save configuration
save_config(Path("config.json"), {"key": "value"})
```

### 5. Conan Utilities (`SpareToolsConan`)

**Conan package management**:

```python
from sparetools_utils import Conan

# Get package path
package_path = Conan.get_package_path("sparetools-base/2.0.3")

# Install dependencies
success = Conan.install_dependencies(
    profile="esp32s3",
    build_missing=True,
    remote="sparetools"
)
```

---

## Integration Status

### ✅ Integrated Scripts

1. **learning_loop_workflow.py**
   - ✅ Uses `setup_logging()` for standardized logging
   - ✅ Uses `run_command()` for subprocess execution
   - ✅ Uses `get_project_root()` for path resolution

2. **conan_install.py**
   - ✅ Uses `setup_logging()` for logging
   - ✅ Uses `Conan.install_dependencies()` for Conan operations
   - ✅ Uses `get_project_root()` for path resolution

3. **generate_flatbuffers.py**
   - ✅ Uses `setup_logging()` for logging
   - ✅ Uses `run_command()` for flatc execution
   - ✅ Uses `get_project_root()` for path resolution

### 🔄 Scripts to Update

4. **detect_devices.py** - Can use logging and path utilities
5. **deploy_all_devices.py** - Can use subprocess and logging utilities
6. **docker_test_runner.py** - Can use subprocess and logging utilities
7. **test_e2e.py** - Can use subprocess and logging utilities
8. **All other Python scripts** - Can benefit from standardized utilities

---

## Usage Examples

### Example 1: Standardized Logging

**Before:**
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

**After:**
```python
from sparetools_utils import setup_logging
logger = setup_logging(__name__)
```

### Example 2: Subprocess Execution

**Before:**
```python
result = subprocess.run(
    ["pio", "run"],
    capture_output=True,
    text=True,
    timeout=600
)
```

**After:**
```python
from sparetools_utils import run_command
result = run_command(
    ["pio", "run"],
    timeout=600,
    check=False
)
```

### Example 3: Project Root Detection

**Before:**
```python
project_root = Path(__file__).parent.parent
```

**After:**
```python
from sparetools_utils import get_project_root
project_root = get_project_root(Path(__file__).parent)
```

---

## Benefits

1. **Consistency**: All SpareTools projects use the same utilities
2. **Maintainability**: Centralized improvements benefit all projects
3. **Error Handling**: Standardized error handling across projects
4. **Logging**: Consistent log format for easier debugging
5. **Path Management**: Automatic project root detection

---

## Fallback Behavior

If `sparetools-base` package is not available in the Conan cache, the module provides **fallback implementations** that work identically:

- ✅ All utilities work without sparetools-base
- ✅ Same API and behavior
- ✅ Automatic detection and loading if available

---

## Configuration

### Conan Package

The `sparetools-base` package is already included in `conanfile.py`:

```python
python_requires = [
    "sparetools-base/2.0.3",
    # ... other packages
]
```

### Installation

```bash
# Install dependencies (sparetools-base will be included)
conan install . --build=missing -r sparetools
```

---

## Integration Checklist

- [x] Create `sparetools_utils.py` integration module
- [x] Integrate into `learning_loop_workflow.py`
- [x] Integrate into `conan_install.py`
- [x] Integrate into `generate_flatbuffers.py`
- [ ] Integrate into `detect_devices.py`
- [ ] Integrate into `deploy_all_devices.py`
- [ ] Integrate into `docker_test_runner.py`
- [ ] Integrate into `test_e2e.py`
- [ ] Integrate into remaining Python scripts
- [x] Create documentation

---

## Next Steps

1. **Continue Integration**: Update remaining Python scripts to use SpareTools utilities
2. **Test**: Verify all scripts work with SpareTools utilities
3. **Document**: Update script-specific documentation
4. **Optimize**: Identify additional utility opportunities

---

**Status**: 🟢 PARTIALLY INTEGRATED  
**Last Updated**: 2026-01-01  
**Version**: 1.0.0
