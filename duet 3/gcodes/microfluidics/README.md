# Microfluidics G-codes

This folder contains ready-to-run G-code programs for microfluidics workflows (e.g., pumping/dispensing lines or spirals).

Most files follow the same pattern:

1. **(Optional) Program pump**
2. **Home and select tool**
3. **Move to a target location (well/feature)**
4. **Start pump and wait for a button prompt**
5. **Run the motion pattern (line/spiral) at a defined feed rate**
6. **Stop pump and retract**

## Files

- `continuous_spiral.g` — Spiral using `G1` segments and pump macros.

## Pump macros (start/stop)

Programs that use the pump rely on macros stored on the Duet SD card, typically:

- `0:/macros/tools/pump/pump_prog_droplet.g`
- `0:/macros/tools/pump/pump_run.g`
- `0:/macros/tools/pump/pump_stop.g`
- `0:/macros/io/wait_button.g`

If your system uses a different tool number or different macro names, update the macro paths and/or the `T` command in the G-code.

## Changing pump flow rate (important)

**Changing the pump flow rate is not done by editing these G-code files.**

To change pump flow rate you must access the files on the **ESP32 bridge** and change the files there **according to the NE pump rules**.

If you update pump behavior on the ESP32, keep the G-code motion (`feed`, `diameter`, etc.) consistent with the new flow rate to maintain stable line width and droplet spacing.
