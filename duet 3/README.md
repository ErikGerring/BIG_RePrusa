# Duet 3 Configuration Files

This folder contains some of the **core configuration and macro files** used to operate the RePrusa platform with the **Duet 3 Mini 5+ controller running RepRapFirmware (RRF)**.

These files represent the **current working configuration of the machine**, including motion setup, homing behaviour, and example G-code macros used during development and experimentation.

## Purpose of This Folder

The contents of this directory document the **machine configuration required to run the platform**. This typically includes:

- Controller configuration files (`config.g`)
- Homing macros (`home*.g`)
- Tool or experiment macros
- Example G-code programs used to test motion and experimental workflows

Together these files define how the motion platform behaves when operated through **Duet Web Control (DWC)**.

## Important Notes

The files in this folder reflect the **specific configuration of the current RePrusa platform**, including:

- Mechanical layout of the repurposed **Prusa MINI+ gantry**
- Stepper driver assignments and tuning
- Homing and probing behaviour
- Offsets and coordinate conventions used during experiments

Because the system is intended as a **modular research platform**, some files may contain **demo routines or experimental macros** used to verify machine behaviour.

These scripts were developed for the **current hardware configuration**, and may require modification if:

- the mechanical setup changes  
- different tools are installed  
- axis limits or offsets are adjusted  
- additional hardware is connected to the Duet controller  

## Example Programs

Some of the included G-code files are **demonstration programs** used during development. Examples may include:

- boundary tracing routines  
- motion verification paths  
- simple drawing or pattern programs  
- experiment-specific movement macros  

These programs are primarily intended to:

- verify correct machine motion
- demonstrate macro usage
- assist with debugging and calibration

They should be treated as **reference examples rather than production scripts**.

## Relationship to the Overall System

Within the broader RePrusa architecture:

- **Duet firmware and macros** control the motion system
- **External controllers (e.g., ESP32 modules)** handle specialised peripherals such as syringe pumps
- **Experiments are orchestrated through G-code macros** that coordinate motion and external devices

This folder therefore represents the **motion-control layer of the system**.

## Future Improvements

Planned improvements include:

- clearer separation between configuration files and experiment macros  
- additional documentation of macro workflows  
- example experiment pipelines demonstrating coordinated motion and device control  

As the platform evolves, these files will continue to be updated to reflect the **current operational configuration of the RePrusa system**.