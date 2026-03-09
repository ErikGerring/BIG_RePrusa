"""main.py

Runtime entrypoint.

Listens for ASCII line commands from the Duet over UART, dispatches pump actions,
then sends a 2-byte ACK back to the Duet.

Supported Duet commands:
- PING
- PUMP <pump_id> <cmd> [args...]
"""

import utime
import config

import duet3
import nepump

FAILURE = 0
SUCCESS = 1

def handle_command(command, args, duet, pumps, debug=False):
    """Parse one Duet command and apply it.

    ACK behavior:
    - OK: command accepted
    - ER: malformed/invalid args
    - BD: unknown command
    """
    if command == "PING":
        duet.ping_response()
        return

    if command != "PUMP":
        if debug:
            print(f"Unrecognized command: \"{command}\" with args: {args}")
        duet.bad_command_response()
        return

    if len(args) < 2:
        duet.error_response()
        return

    pump_id = int(args[0])
    pump_cmd = args[1].upper()
    pump_args = args[2:]

    if pump_id < 0 or pump_id >= len(pumps):
        if debug:
            print(f"Invalid pump ID: {pump_id}. Valid range is 0 to {len(pumps) - 1}.")
        duet.error_response()
        return

    rc = pumps[pump_id].execute_command(pump_cmd, pump_args)

    if rc == FAILURE:
        if debug:
            print(f"Unrecognized/failed pump command: \"{pump_cmd}\" args={pump_args} pump_id={pump_id}")
        duet.bad_command_response()
        return

    # ACK immediately (RUNPROG has only been validated/opened here; actual execution is in pump.service())
    duet.ok_response()

def main():
    """Initialize UART links and run the command loop forever."""
    utime.sleep(1)

    debug = bool(getattr(config, "DEBUG_MODE", False))
    if debug:
        print("Debug mode is enabled.\n")

    duet = duet3.duet(
        uart_no=int(getattr(config, "DUET_UART_ID")),
        baud=int(getattr(config, "DUET_UART_BAUD")),
        tx_pin=int(getattr(config, "DUET_UART_TX_PIN")),
        rx_pin=int(getattr(config, "DUET_UART_RX_PIN")),
        debug=debug,
    )

    pumps = []
    for i in range(0, int(getattr(config, "NUMBER_OF_PUMPS", 1))):
        pumps.append(nepump.NEPump(
            uart_no=int(getattr(config, f"PUMP{i}_UART_ID")),
            baud=int(getattr(config, f"PUMP{i}_UART_BAUD")),
            tx_pin=int(getattr(config, f"PUMP{i}_TX_PIN")),
            rx_pin=int(getattr(config, f"PUMP{i}_RX_PIN")),
            # address=str(i) if int(getattr(config, "NUMBER_OF_PUMPS", 1)) > 1 else None,
            debug=debug,
        ))

    max_line = int(getattr(config, "UART_BUFFER_SIZE"))

    if debug:
        print("Setup complete. Entering main loop. Waiting for commands from the Duet 3...\n")

    while True:
        data = duet.read_line(max_line)

        if not data:
            utime.sleep_ms(5)
            continue

        try:
            parts = data.decode().strip().split()
        except UnicodeError:
            if debug:
                print("Received invalid UTF-8 data from Duet. Ignoring.")
            continue

        if not parts:
            continue

        command = parts[0].upper()
        args = parts[1:]
        handle_command(command, args, duet, pumps, debug=debug)




main()