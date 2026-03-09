#!/usr/bin/env sh
set -eu
. "$(dirname "$0")/_env.sh"

"$PYTHON" -m mpremote connect "$PORT" repl
