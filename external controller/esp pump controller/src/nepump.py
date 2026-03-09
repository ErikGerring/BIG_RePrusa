"""nepump.py

New Era NE-1000 pump helper (UART).

This module sends Basic-mode ASCII commands terminated by CR and can stream a
simple multi-line "program" from `nepump_programs/`.
"""

from machine import UART, Pin
import time

FAILURE = 0
SUCCESS = 1

STX = 0x02
ETX = 0x03

class NEPump:
    """Single pump interface bound to one UART (current design)."""
    def __init__(self, uart_no, baud, tx_pin, rx_pin, address=None, debug=False):
        self.uart = UART(uart_no, baud, tx=Pin(tx_pin), rx=Pin(rx_pin), timeout=100)
        self.uart.init(baudrate=baud, bits=8, parity=None, stop=1)

        self.debug = debug
        self.address = address
        self._rx = bytearray()  # Buffer for incoming data
        self._rx_i = 0  # Index for processing the buffer

        self.uart.read()  # Flush any existing input

        self.force_basic_mode()

    def send_command(self, cmd: str, all=False):
        """Send one Basic-mode command (CR-terminated)."""
        # Build full command
        if all:
            full = "* " + cmd
        elif self.address is not None:
            full = self.address + " " + cmd
        else:
            full = cmd

        self.uart.write((full + "\r").encode("ascii"))
        
        if self.debug:
            target = "ALL" if all else (("pump" + self.address) if self.address is not None else "pump")
            print("Sent to {}: {}".format(target, full))

        time.sleep_ms(100)  # Give pump time to respond; empirically seems to help with reliability

        if self.debug:
            response = self.read_one_frame(timeout_ms=300)
            if response:
                print("Received:", response.decode())

    def force_basic_mode(self):
        """Attempt to exit Safe mode and disable Safe mode (best-effort)."""
        # 1) If pump is in SAFE mode, this packet forces it back to BASIC
        self.uart.write(b"\x02\x08SAF0\x55\x43\x03")

        # 2) In BASIC mode, explicitly disable SAFE mode
        # Standalone attempt (works if not networked)
        self.send_command("SAF 0", all=False)

        # Network broadcast attempt (works if networked)
        self.send_command("SAF 0", all=True)

    def start(self, all=False):
        self.send_command("RUN", all=all)

    def start_specific(self, phase, all=False):
        self.send_command("RUN " + phase, all=all)

    def stop(self, all=False):
        self.send_command("STP", all=all)

    def reset(self, all=False):
        self.send_command("RESET", all=all)

    def program_pump(self, filename, all=False):
        """Stream a text program file to the pump line-by-line."""
        # NOTE: This sends program lines to the targeted pump/broadcast.
        # For networked use, it's safer to target one address at a time.
        with open("nepump_programs/" + filename, "r") as fs:
            for line in fs:
                line = line.strip()
                if not line:
                    continue
                self.send_command(line, all=all)

    def execute_command(self, pump_cmd, pump_args):
        """Dispatch a high-level pump command used by main.py."""
        pc = pump_cmd.upper()

        if pc in ("START", "RUN"):
            if len(pump_args) == 1:
                self.start_specific(pump_args[0])
            else:  
                self.start(all = (pump_args and pump_args[0].upper() == "ALL"))
            return SUCCESS

        if pc in ("STOP", "STP"):
            self.stop(all = (pump_args and pump_args[0].upper() == "ALL"))
            return SUCCESS

        if pc == "PROG" and len(pump_args) == 1:
            self.program_pump(pump_args[0])
            return SUCCESS
        
        if pc == "RESET":
            self.reset(all = (pump_args and pump_args[0].upper() == "ALL"))
            return SUCCESS

        return FAILURE

    def read_one_frame(self, timeout_ms=100):
        """Read one STX..ETX framed response (best-effort)."""
        start = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start) < timeout_ms:
            if self.uart.any():
                chunk = self.uart.read(64)
                if chunk:
                    self._rx.extend(chunk)

            # try extract one STX..ETX frame
            s = self._rx.find(b"\x02")
            if s != -1:
                e = self._rx.find(b"\x03", s + 1)
                if e != -1:
                    frame = bytes(self._rx[s:e+1])
                    # remove up to end of frame
                    self._rx = self._rx[e+1:]
                    return frame

            time.sleep_ms(5)

        return None
    
    def read_response(self):
        """Legacy helper: read up to 64 bytes if available."""
        if self.uart.any() == 0:
            return "Nothing to read"
        return self.uart.read(64)