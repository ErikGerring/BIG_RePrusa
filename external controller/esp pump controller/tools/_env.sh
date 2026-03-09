#!/usr/bin/env sh
set -eu

# Shared helpers for scripts

if [ -z "${PORT:-}" ]; then
  echo "PORT is not set. Example: PORT=/dev/cu.SLAB_USBtoUART $0" >&2
  exit 2
fi

BAUD="${BAUD:-460800}"
CHIP="${CHIP:-esp32}"
FIRMWARE_BIN="${FIRMWARE_BIN:-firmware/micropython-esp32.bin}"

# Prefer the local venv if present
if [ -x ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python3"
fi
