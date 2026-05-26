#!/usr/bin/env bash
set -euo pipefail

PYTHON_EXE="/c/Users/olivi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$PYTHON_EXE" "$SCRIPT_DIR/update-telemetry-from-excel.py"
