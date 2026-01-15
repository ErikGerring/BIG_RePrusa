# Modular Multi-Tool XYZ Gantry Platform  
*(Prusa MINI+ mechanics + Duet 3 + RepRapFirmware)*

## Project Overview
This project repurposes the **Prusa MINI+ XYZ gantry and SuperPINDA probe** into a **modular automation platform** for biomedical workflow prototyping. The stock controller is replaced with a **Duet 3 running RepRapFirmware (RRF)** to support deterministic process control and flexible I/O.

It is designed to support **stepwise automation of membrane-disc preparation workflows** (e.g. plasma activation, coating, UV treatment) in a lab setting. The initial focus is on enabling precise control of an **Atmospheric Pressure Plasma Jet (APPJ)** for disc surface treatment, with scope for future modules like coating or inspection heads.

---

## Core Concept
- Reuse the **mechanically robust Prusa MINI+ gantry** for reliable XYZ motion
- Replace the Buddy board with a **Duet 3 + RepRapFirmware** for rich control
- Leverage **RRF macros** as a readable, flexible automation logic layer
- Integrate external process tools (e.g. plasma jet) via digital I/O handshake
- Build a safe, inspectable, extendable platform for lab process automation

---

## Hardware Architecture

### Motion System
- X, Y, Z stepper motors and mechanics from Prusa MINI+
- Support for up to two extra steppers (e.g. rotary axis or tool actuator)
- Homing via endstops and/or SuperPINDA inductive probe

### Sensing
- **SuperPINDA** used for:
  - Z-homing and surface probing
  - Pre-process surface validation
  - Safety interlock preconditions

### Controller
- **Duet 3 with RepRapFirmware**
- Benefits:
  - Text-based config and macros (no firmware compiling)
  - Built-in logic: conditionals, loops, variables, aborts
  - Rich I/O for tool signalling and state feedback
  - Expansion via CAN boards (for head-mounted sensors, etc.)

### Tooling (Phase 1)
- **APPJ (Atmospheric Pressure Plasma Jet)** mounted on toolhead
- Digital handshake protocol:
  - Outputs: ENABLE, ARM
  - Inputs: READY, FAULT, VALIDATION

---

## Software & Control Logic

### Firmware
- **RepRapFirmware (RRF)**
- All logic written in plain-text G-code macros

### Control Model
- Standard motion commands (`G0`, `G1`, `G28`, etc.)
- Macros encapsulate process steps, safety checks, state handling:
  - `plasma_enable.g` – safety conditions + tool arm
  - `wait_ready.g` – wait on READY line
  - `plasma_raster.g` – perform controlled plasma scan
  - `failsafe_check.g` – monitor FAULT during motion
  - `plasma_disable.g` – clean shutdown or abort

---

## Process Control & Safety Philosophy

### Software-Level Controls
- All tool actions gated by validation logic
- FAULT input monitored continuously
- Macros structured with frequent condition checks and abort logic

### Hardware-Level Reality
- Software alone cannot ensure total safety
- Design encourages **hardware interlocks**, gas shutoffs, and physical safeguards outside the Duet system
- This layered control strategy is explicitly documented

---

## Example Workflow (Phase 1 Use Case)
1. Home XYZ with SuperPINDA or endstops  
2. Probe disc surface for position validation  
3. Check plasma tool READY status  
4. Enable and arm APPJ  
5. Execute a raster scan over disc surface  
6. Continuously monitor for FAULT or interruption  
7. Shutdown or abort process safely

---

## Why Duet 3 + RepRapFirmware
- Zero firmware compilation – changes made in config or macros
- Macros serve as **modular process logic**
- Scales well to multi-step workflows and multiple tools
- Enables clear system state handling and traceability – ideal for engineering documentation
- Supports future expansion (e.g. coating, UV, vision)

---

## Project Intent
This repo provides:
- A reusable automation platform based on standard open hardware
- A framework for safe, inspectable control of lab-based material processing
- A foundation for tools including:
  - Plasma nozzles
  - Coating/spraying units
  - Light/UV curing heads
  - Inspection modules or sensors

---

## Project Status
- ✅ Architecture selected
- ✅ Motion subsystem defined
- 🔜 Process logic macros in development
- 🔜 I/O wiring + plasma validation
- 🔜 Safety supervision and full process integration

---

## Dev Quickstart (UI)

This repo includes a small PySide6 UI scaffold under `src/reprusa/ui`.

### Recommended Python version (macOS)

Use Python **3.13.x** (see `.python-version`). PySide6 does not reliably ship macOS Qt plugins for bleeding-edge Python releases (e.g. Python 3.14), which can cause errors like:

"Could not find the Qt platform plugin \"cocoa\"".

### Run

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
python run.py
```

---

## Disclaimer
This platform is **not safety-certified**.  
Any use with high-voltage tools, plasma devices, or pressurised gases **must include independent safety interlocks and validated risk controls** beyond what firmware logic provides.
