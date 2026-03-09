#!/usr/bin/env sh
set -eu
. "$(dirname "$0")/_env.sh"

# Copy all files from src/ to the board filesystem.
# --no-verbose to keep output readable; remove if you want details.
"$PYTHON" -m mpremote connect "$PORT" fs cp -r src/. :/

# Soft reset so new main.py runs
"$PYTHON" -m mpremote connect "$PORT" reset
