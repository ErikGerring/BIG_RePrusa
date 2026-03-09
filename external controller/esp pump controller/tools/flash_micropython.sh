#!/usr/bin/env sh
set -eu
. "$(dirname "$0")/_env.sh"

if [ ! -f "$FIRMWARE_BIN" ]; then
  echo "Firmware bin not found at: $FIRMWARE_BIN" >&2
  echo "Download from https://micropython.org/download/ESP32/ and put it there." >&2
  exit 2
fi

# Most ESP32 boards use 0x1000; keep it default.
"$PYTHON" -m esptool --chip "$CHIP" --port "$PORT" --baud "$BAUD" --before default-reset --after hard-reset write-flash -z 0x1000 "$FIRMWARE_BIN"
