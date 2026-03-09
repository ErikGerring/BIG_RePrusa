# pump_esp (MicroPython + ESP32)

## Outline

This project runs MicroPython on an ESP32 to act as a small UART “bridge + dispatcher” between:

- A Duet 3 (sending simple line-based commands over UART)
- One or more New Era NE-1000 syringe pumps (controlled over UART)

The ESP32 receives a single ASCII line from the Duet, parses it, executes the requested pump action, then sends a 2-byte ACK back to the Duet:

- `OK` = command accepted
- `ER` = malformed command / internal error
- `BD` = unrecognized command

Project layout:

- `src/` → files copied to the ESP32 filesystem
  - `boot.py` runs first (radio disable)
  - `main.py` runs on boot and handles the Duet command protocol
  - `config.py` defines UART pins/baud + number of pumps
  - `duet3.py` Duet UART helper (line read + ACK responses)
  - `nepump.py` NE-1000 UART helper (Basic-mode commands + program upload)
  - `nepump_programs/` simple text programs sent line-by-line to pumps
- `tools/` → host-side scripts for erase/flash/deploy/REPL (via `esptool` + `mpremote`)

## Functionality

### Boot behavior

- `src/boot.py` disables Wi‑Fi and Bluetooth by default (controlled via `DISABLE_WIFI` and `DISABLE_BLUETOOTH` in `src/config.py`).

### UART links (defaults)

Defaults are in `src/config.py`:

- Duet 3 ↔ ESP32: UART1 @ 115200
  - ESP32 TX = GPIO17
  - ESP32 RX = GPIO16
- Pump 0 ↔ ESP32: UART2 @ 19200
  - ESP32 TX = GPIO25
  - ESP32 RX = GPIO26

### Duet → ESP32 command protocol

`src/main.py` reads one line from the Duet UART and expects one of:

- `PING`
- `PUMP <pump_id> <cmd> [args...]`

Where:

- `pump_id` is `0..NUMBER_OF_PUMPS-1`
- `cmd` is dispatched by `NEPump.execute_command()` in `src/nepump.py`

Current implemented pump commands:

- `PUMP <id> START [ALL]` (alias: `RUN`) → sends `RUN\r`
- `PUMP <id> STOP [ALL]` (alias: `STP`) → sends `STP\r`
- `PUMP <id> RESET [ALL]` → sends `RESET\r`
- `PUMP <id> PROG <filename>` → streams `nepump_programs/<filename>` to the pump line-by-line

Notes:

- `ALL` is intended for pump networks (broadcast `* <cmd>`). It’s wired through in `nepump.py`, but multi-pump addressing is not fully plumbed through `main.py` yet.
- On boot, each pump instance is forced into Basic mode by attempting to disable Safe mode (`SAF 0`) and sending one raw “exit-safe” packet.

### Pump programs

Files in `src/nepump_programs/` are plain text lines sent as-is (with `\r` appended) to the pump. Example files:

- `beep.txt` (simple beep/stop)
- `stdy_inf_1.txt` (steady infuse settings)
- `test_1.txt` (basic test program)

## Requirements

### Hardware

- ESP32 board capable of running MicroPython
- Duet 3 UART connection to the ESP32 (3.3V TTL UART)
- NE-1000 pump UART connection to the ESP32
- Correct common ground between Duet, ESP32, and pump

If you’re using external USB↔UART adapters for bench testing, ensure voltage levels match (3.3V TTL vs RS-232). NE-1000 pumps are often documented with RS-232 framing terminology; your specific wiring/interface must convert levels appropriately.

### Host software (macOS)

- Python 3
- A USB data cable for the ESP32

Install tools (recommended: venv):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

This repo uses:

- `esptool` (erase/flash)
- `mpremote` (deploy files, REPL, reset)

### Firmware binary

Download an ESP32 MicroPython `.bin` from:

- https://micropython.org/download/ESP32/

Place it at:

- `firmware/micropython-esp32.bin`

### Flash / deploy / REPL

Find the ESP32 serial port (typical on macOS):

```bash
ls /dev/cu.*
python tools/find_port.py
```

Then (examples):

```bash
PORT=/dev/cu.SLAB_USBtoUART make erase
PORT=/dev/cu.SLAB_USBtoUART make flash
PORT=/dev/cu.SLAB_USBtoUART make deploy
PORT=/dev/cu.SLAB_USBtoUART make repl
```

If you have a variant (e.g. ESP32-S3), set `CHIP` for flashing:

```bash
PORT=/dev/cu.usbmodem123 CHIP=esp32s3 ./tools/flash_micropython.sh
```

If deploy fails with `could not enter raw repl`:

- Make sure you’re using `/dev/cu.*` (not `/dev/tty.*`).
- Temporarily stop the running `main.py`: open REPL (`make repl`), press `Ctrl-C`, then exit (`Ctrl-]`). Retry deploy.

## How to add more pump functionality

The simplest path is to add a new high-level command in `NEPump.execute_command()` and (optionally) a helper method.

1) Add a method (optional) in `src/nepump.py` that emits the pump command you want.
   - Example: add `set_rate(...)` that sends `RAT ...`.

2) Extend `NEPump.execute_command(pump_cmd, pump_args)` to recognize a new keyword.
   - Keep the interface in the style of existing commands: `PUMP <id> <CMD> [args...]`.

3) If the pump action is naturally a multi-line sequence, add a new text file under `src/nepump_programs/` and invoke it via:

```text
PUMP 0 PROG your_program.txt
```
Implementation notes:

- The current implementation mostly “fire-and-forget” writes commands and ACKs the Duet immediately.
- There is a `read_one_frame()` helper in `NEPump` you can use to start validating pump responses (STX..ETX framed) before ACKing.

## Future implementation

### Pump status + stronger ACK semantics

- Parse pump responses and only return `OK` to the Duet once a command is confirmed (or return `ER` with reason).
- Add timeouts/retries and expose meaningful error telemetry (stall, timeout, out-of-range).

### Safe-mode comms

- Implement NE-1000 Safe mode framing (STX, length, CRC16, ETX) for robustness against corruption.

### Making a network of pumps work

The code already has the concept of an address and broadcast (`*`) in `src/nepump.py`, but `src/main.py` currently constructs pumps without setting per-pump addresses.

To support a real multi-drop pump network:

- Give each physical pump a unique network address (0..99) per the NE-1000 manual.
- Plumb addresses into the ESP32 pump objects (e.g. set `address=str(i)` when creating `NEPump(...)` instances).
- Decide whether multiple pumps share one UART (multi-drop) or each pump has its own UART:
  - Shared UART: one `UART` object, multiple logical pumps differentiated by address; you’ll also need request/response correlation.
  - Separate UARTs: keep the current “one pump per UART” pattern, but still use addressing if needed.
- Define a Duet-facing command convention for addressing/broadcast (e.g. `PUMP 3 START` and `PUMP 0 START ALL`).

Once addressing is in place, you can:

- Broadcast commands with `ALL` (currently supported by `nepump.py` as `* <cmd>`).
- Target commands to a specific pump with `<address> <cmd>`.

