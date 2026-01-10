#!/bin/bash
# Wrapper script to ensure bundled CPython is used
# Usage: ./run_with_bundled_python.sh <script> [args...]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Try to use bundled CPython wrapper
if [ -f "$SCRIPT_DIR/ensure_bundled_python.py" ]; then
    exec python3 "$SCRIPT_DIR/ensure_bundled_python.py" "$@"
else
    # Fallback: try sparetools command
    if command -v sparetools >/dev/null 2>&1; then
        exec sparetools python "$@"
    else
        # Last resort: system Python with warning
        echo "⚠ Warning: sparetools bundled CPython not found, using system Python"
        exec python3 "$@"
    fi
fi
