#!/bin/bash
# Thin POSIX wrapper around skills/setup.py for backward compatibility.
# See skills/setup.py for the actual implementation.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "Error: Python is required but was not found in PATH." >&2
    exit 1
fi

exec "$PYTHON" "$SCRIPT_DIR/setup.py" "$@"
