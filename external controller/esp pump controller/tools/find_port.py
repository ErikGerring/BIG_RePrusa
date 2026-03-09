#!/usr/bin/env python3

import glob
import sys


def main() -> int:
    patterns = [
        "/dev/cu.usbserial*",
        "/dev/cu.SLAB_USBtoUART",
        "/dev/cu.wchusbserial*",
        "/dev/cu.usbmodem*",
        "/dev/tty.usbserial*",
        "/dev/tty.SLAB_USBtoUART",
        "/dev/tty.wchusbserial*",
        "/dev/tty.usbmodem*",
    ]

    ports = []
    for pat in patterns:
        ports.extend(glob.glob(pat))

    ports = sorted(set(ports))

    if not ports:
        print("No likely ESP serial ports found.")
        print("Try: ls /dev/cu.*")
        return 2

    print("Likely serial ports:")
    for p in ports:
        print(f"- {p}")

    # Suggest cu.* first for macOS
    cu = [p for p in ports if p.startswith("/dev/cu.")]
    suggestion = (cu[0] if cu else ports[0])
    print("\nSuggested PORT:")
    print(suggestion)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
