# RePrusa Control

Desktop control application for the **RePrusa microfluidics platform**.

This application provides a user interface for controlling:

- Duet 3 motion controller
- ESP32 pump controller
- microfluidic dispensing experiments

Built with:

- Tauri (Rust backend)
- React + TypeScript frontend
- HTTP interface to Duet RepRapFirmware

## Current features

- Connect to Duet controller
- Query machine status
- Send G-code commands
- Basic motion control
- Homing routines

Future work:

- Pump controller integration
- Experiment protocol builder
- Logging and run history
- Camera monitoring