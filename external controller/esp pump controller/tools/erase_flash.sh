#!/usr/bin/env sh
set -eu
. "$(dirname "$0")/_env.sh"

"$PYTHON" -m esptool --chip "$CHIP" --port "$PORT" --before default-reset --after hard-reset erase-flash
