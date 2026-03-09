"""config.py

Hardware/config constants for the ESP32 UART bridge.

- Duet UART: where the Duet sends line-based commands.
- Pump UART(s): where NE-1000 pump commands are sent.
"""

# Configuration for UART between the Duet 3 and the ESP32
DUET_UART_ID = 1
DUET_UART_BAUD = 115200
DUET_UART_TX_PIN = 17
DUET_UART_RX_PIN = 16

# Configuration for UART between the NE-1000 pumps and the ESP32
NUMBER_OF_PUMPS = 1

# Pump 0
PUMP0_UART_ID = 2
PUMP0_UART_BAUD = 19200
PUMP0_TX_PIN = 25
PUMP0_RX_PIN = 26

# Pump 1
# PUMP0_UART_ID = 2
# PUMP0_UART_BAUD = 19200
# PUMP0_TX_PIN = 25
# PUMP0_RX_PIN = 26

# Buffer size for reading lines from the UART
UART_BUFFER_SIZE = 256

# Debug mode for verbose output
DEBUG_MODE = True

# Radio disable
DISABLE_WIFI = True
DISABLE_BLUETOOTH = True
