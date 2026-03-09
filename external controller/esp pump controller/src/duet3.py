"""duet3.py

Duet 3 UART helper.

- Reads newline-terminated commands from the Duet.
- Writes 2-byte ACK responses (OK/ER/BD) back.
"""

from machine import UART, Pin
import time

FINISH_COMMAND = "FN" # Command sent by the pump to indicate it has finished a RUNPROG action (e.g. completed the volume/rate/duration specified in a RUNPROG command)
OK_COMMAND = "OK" # Response from the Duet 3 when a command is successfully received and processed
ERROR_COMMAND = "ER" # Response from the Duet 3 when a command is received but cannot be processed due to an error
BAD_COMMAND = "BD" # Response from the Duet 3 when a command is received but is not recognized as a valid command

class duet:
    """Small wrapper around a UART link to the Duet."""
    def __init__(self, uart_no, baud, tx_pin, rx_pin, debug=False):
        self.uart = UART(uart_no, baud, tx=Pin(tx_pin), rx=Pin(rx_pin), timeout=100)
        self.uart.init(baudrate=baud, bits=8, parity=None, stop=1)
        self.debug = debug

        self.flush_input()

    def write(self, cmd):
        self.uart.write(str(cmd))
        if self.debug:
            print(f"Sent to Duet: {cmd}")
    
    def flush_input(self):
        self.uart.read()
    
    def __del__(self):
        self.uart.deinit()

    def read_line(self, max_bytes):
        """Read one line from UART (truncated to max_bytes)."""
        if self.uart.any() == 0: # No data available to read
            return None

        data = self.uart.readline() # Read a line of data from the UART. This will read until a newline character is encountered or until the timeout is reached.
        if data is None:
            return None

        if len(data) > max_bytes: # If the received data exceeds the maximum allowed bytes, truncate it to prevent buffer overflow.
            data = data[:max_bytes]

        if self.debug:
            print("Received from Duet:", data)

        return data
    
    def ping_response(self):
        """Reply to Duet PING."""
        self.ok_response()

    def finish_response(self):
        self.write(FINISH_COMMAND)

    def ok_response(self):
        self.write(OK_COMMAND)  

    def error_response(self):
        self.write(ERROR_COMMAND)

    def bad_command_response(self):
        self.write(BAD_COMMAND)