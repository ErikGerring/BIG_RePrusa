#!/usr/bin/env python3

"""Bench test helper.

Sends one line to the ESP32 Duet UART bridge (over a USB-serial adapter connected
to the same UART pins) and prints the 2-byte ACK.

Example:
  ./tools/bench_send.py /dev/cu.usbserial-XXXX "PUMP 1 ARM key=1234"
"""

import sys
import time

import serial


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: bench_send.py <PORT> <LINE>")
        return 2

    port = sys.argv[1]
    line = " ".join(sys.argv[2:])
    if not line.endswith("\n"):
        line += "\n"

    with serial.Serial(port, 115200, timeout=1) as ser:
        time.sleep(0.05)
        ser.reset_input_buffer()
        ser.write(line.encode("ascii", "strict"))
        ser.flush()
        ack = ser.read(2)

    print(f"ACK: {ack!r}")
    return 0 if ack in (b"OK", b"ER") else 1


if __name__ == "__main__":
    raise SystemExit(main())
