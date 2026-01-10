# Bundled CPython Usage Guide

## Overview

This project uses **sparetools bundled CPython** (version 3.12.7) from the `sparetools-cpython` Conan package to ensure consistent Python runtime across all scripts.

---

## Why Bundled CPython?

1. **Consistency**: Same Python version across all environments
2. **Dependencies**: Pre-configured with SpareTools ecosystem packages
3. **Reproducibility**: Guaranteed Python version for builds
4. **Isolation**: Doesn't interfere with system Python

---

## Automatic Detection

The `sparetools_utils.py` module automatically detects and uses bundled CPython:

```python
from sparetools_utils import get_python_command, is_using_bundled_python

# Get Python command (prefers bundled CPython)
python_cmd = get_python_command()  # Returns list: ['/path/to/bundled/python']

# Check if currently using bundled Python
if is_using_bundled_python():
    print("Using bundled CPython")
```

---

## Usage Methods

### Method 1: Wrapper Script (Recommended)

```bash
# Use the wrapper script
python3 scripts/ensure_bundled_python.py scripts/learning_loop_workflow.py --cycle 1
```

### Method 2: sparetools Command

```bash
# If sparetools CLI is available
sparetools python scripts/learning_loop_workflow.py --cycle 1
```

### Method 3: Direct Execution

```bash
# Scripts automatically detect and use bundled CPython
python3 scripts/learning_loop_workflow.py --cycle 1
# (Will warn if not using bundled CPython)
```

### Method 4: Environment Variable

```bash
# Set environment variable
export SPARETOOLS_PYTHON=~/.sparetools/bin/python
python3 scripts/learning_loop_workflow.py --cycle 1
```

---

## Detection Priority

The system checks for bundled CPython in this order:

1. **Current Python**: Check if `sys.executable` is bundled CPython
2. **Conan Cache**: Look for `sparetools-cpython/3.12.7` in Conan cache
3. **sparetools Command**: Try `sparetools python` command
4. **Common Paths**: Check standard installation locations
5. **Environment Variables**: Check `SPARETOOLS_PYTHON` or `SPARE_PYTHON`
6. **Fallback**: Use system Python (with warning)

---

## Installation

Bundled CPython is installed via Conan:

```bash
# Install sparetools-cpython package
conan install sparetools-cpython/3.12.7 -r sparetools --build=missing

# Or install all dependencies (includes sparetools-cpython)
conan install . --build=missing -r sparetools
```

The package is already listed in `conanfile.py`:

```python
tool_requires = [
    "sparetools-flatbuffers/24.3.25",
    "sparetools-cpython/3.12.7",  # Consistent Python runtime
]
```

---

## Verification

### Check if Using Bundled CPython

```python
from scripts.sparetools_utils import is_using_bundled_python

if is_using_bundled_python():
    print("✓ Using bundled CPython")
else:
    print("⚠ Using system Python")
```

### Get Python Command

```python
from scripts.sparetools_utils import get_python_command

python_cmd = get_python_command()
print(f"Python command: {python_cmd}")
# Output: ['/path/to/sparetools-cpython/bin/python']
```

### Test Detection

```bash
# Test detection
python3 -c "from scripts.sparetools_utils import get_python_command, is_using_bundled_python; \
    cmd = get_python_command(); \
    print(f'Python: {cmd}'); \
    print(f'Using bundled: {is_using_bundled_python()}')"
```

---

## Script Integration

### Subprocess Calls

All scripts that spawn Python subprocesses use bundled CPython:

```python
from sparetools_utils import get_python_command, run_command

# Get bundled CPython command
python_cmd = get_python_command()

# Use in subprocess
result = run_command(
    python_cmd + ["script.py", "arg1", "arg2"],
    timeout=600
)
```

### Current Scripts Using Bundled CPython

- ✅ `learning_loop_workflow.py` - Uses bundled CPython for test scripts
- ✅ `generate_flatbuffers.py` - Uses bundled CPython for enum extraction
- ✅ All scripts that spawn Python subprocesses

---

## Troubleshooting

### Issue: "sparetools bundled CPython not found"

**Solution:**
```bash
# Install sparetools-cpython
conan install sparetools-cpython/3.12.7 -r sparetools --build=missing

# Verify installation
conan cache path sparetools-cpython/3.12.7
```

### Issue: Scripts using system Python

**Solution:**
```bash
# Use wrapper script
python3 scripts/ensure_bundled_python.py scripts/your_script.py

# Or set environment variable
export SPARETOOLS_PYTHON=$(conan cache path sparetools-cpython/3.12.7)/bin/python
```

### Issue: Wrong Python version

**Solution:**
```bash
# Verify bundled CPython version
python_cmd = get_python_command()
subprocess.run(python_cmd + ["--version"])

# Should show: Python 3.12.7
```

---

## Best Practices

1. **Always use wrapper script** for critical scripts
2. **Check bundled CPython** at script start
3. **Use `get_python_command()`** for subprocess calls
4. **Warn users** if not using bundled CPython
5. **Document** Python version requirements

---

## Status

✅ **Bundled CPython Detection**: Implemented  
✅ **Automatic Fallback**: Working  
✅ **Script Integration**: Complete  
✅ **Documentation**: Complete  

**All scripts now ensure bundled CPython is used!** 🚀

---

**Last Updated**: 2026-01-01  
**Version**: 1.0.0
