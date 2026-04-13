# RePrusa

RePrusa is a modular precision gantry platform developed by repurposing a Prusa MINI+ 3D printer and integrating it with a Duet 3 Mini 5+ controller running RepRapFirmware.

The project was developed during my work with the Biomedical Innovation Group (BIG) at the University of Sydney. Many experimental workflows in biomedical research rely on shared laboratory equipment, which can be difficult to access, schedule, or configure for specialised experiments.

RePrusa explores an alternative approach: using a programmable precision gantry system as a general-purpose experimental automation platform.

By combining an open motion-control architecture with modular tool integration, the system allows different experimental tools to be mounted and controlled using the same underlying platform. This enables researchers to rapidly prototype automated experimental workflows while maintaining precise motion control and repeatability.

The project demonstrates how consumer hardware and open firmware can be repurposed to create flexible experimental infrastructure for research environments.

![RePrusa Prototype at BIG Lab](docs/images/reprusa_prototype.jpg)

Prototype RePrusa system installed at the Biomedical Innovation Group laboratory at the University of Sydney.

## Project Overview

RePrusa is built around a modular architecture consisting of four main layers:

1. **Mechanical Platform**  
   A modified Prusa MINI+ gantry provides precise and repeatable XYZ motion.

2. **Control Hardware**  
   A Duet 3 Mini 5+ controller replaces the original printer electronics, providing open configuration, wireless connectivity, and flexible I/O.

3. **Firmware and Motion Logic**  
   The system runs RepRapFirmware, enabling programmable motion control and integration with external hardware.

4. **Modular Tool Systems**  
   Experimental tools can be mounted to the gantry depending on the research application. Each tool defines its own control macros and workflow.

This layered design allows the motion platform to remain constant while different experimental systems can be integrated on top of it.


**Design Notes**

The current implementation uses a modified Prusa MINI+ as the motion platform due to its compact footprint, reliability, and readily available hardware. However, the architecture of RePrusa is not tied to this specific gantry system. Any motion platform could be used in its place if higher precision, larger working volumes, or different kinematic configurations are required. The control architecture and firmware configuration are designed to remain adaptable to different gantry systems.

The Duet 3 Mini 5+ WiFi controller was selected primarily for its open configuration environment and its integration with RepRapFirmware. This combination allows full control over motion parameters, programmable macro logic, and flexible hardware I/O. These capabilities make it well suited for experimental automation where external devices, sensors, or custom control routines may need to be integrated into the system.
## System Architecture

The RePrusa platform follows a layered architecture that separates motion, control, and experimental tooling. This allows the motion platform and controller to remain constant while different experimental systems can be integrated as interchangeable tools.

![RePrusa System Architecture](docs/images/system_architecture.png)

The system consists of five primary layers:

**Mechanical Layer**  
A Prusa MINI+ gantry provides precise and repeatable XYZ positioning and physically interacts with the mounted experimental tool.

**Control Layer**  
A Duet 3 Mini 5+ WiFi controller manages motion control, stepper drivers, and hardware I/O, acting as the central interface between the gantry and external devices.

**Firmware Layer**  
RepRapFirmware (RRF) runs on the controller and provides configurable motion control and a programmable interface for system operation.

**Software Layer**  
Experimental workflows are implemented using G-code macros and control logic, defining motion routines, tool activation, and automated experimental sequences.

**Tool Layer**  
Experimental systems are mounted as interchangeable modules. These tools act as a black-box subsystem that interacts with the platform through mechanical positioning and controller I/O communication.

This separation allows new experimental tools to be integrated without modifying the underlying motion platform.

## Platform Setup

The RePrusa platform is designed so that a Cartesian gantry system can be paired with a Duet controller and configured as a programmable experimental motion platform. While this project uses a modified Prusa MINI+ gantry, the same general setup process applies to other compatible motion systems.

### 1. Motion Platform

Begin with a functioning gantry system capable of precise XYZ positioning. This provides the mechanical foundation of the platform.

The gantry should include:

- stepper-driven axes
- endstop or probing sensors
- a stable frame and carriage for tool mounting

Although a Prusa MINI+ was used for this implementation, other gantry systems can be used depending on required working area, rigidity, or positioning precision.

### 2. Controller Integration

Replace or interface the existing motion controller with a **Duet 3 Mini 5+ WiFi** (or other compatible Duet board).

The controller manages:

- stepper motor drivers
- axis motion control
- endstop inputs
- hardware I/O for external devices

Motor wiring, endstops, and power connections should be connected according to the Duet documentation.

Duet controller documentation:  
https://docs.duet3d.com/

### 3. Firmware Configuration

Duet controllers run **RepRapFirmware (RRF)**, which defines the behaviour of the motion system through configuration files.

The main configuration file (`config.g`) defines:

- axis directions and steps per mm
- motor currents
- endstop behaviour
- travel limits
- homing procedures

A convenient way to generate an initial configuration is the RepRapFirmware configuration tool: https://configtool.reprapfirmware.org/

This tool allows the motion system, kinematics, and hardware options to be configured before generating a working `config.g` file.

### 4. Motion System Verification

After uploading the configuration to the controller, basic system checks should be performed:

- verify correct motor directions
- test homing routines
- confirm axis limits and travel ranges
- validate stepper currents and motion smoothness

Once the motion platform is operating reliably, experimental tools can be mounted and controlled through the firmware macro system.

Further details on RepRapFirmware configuration and motion tuning can be found in the official documentation:

https://docs.duet3d.com/User_manual/RepRapFirmware


## Experiment Workflow and Tool Integration

The RePrusa platform executes experiments through a macro-driven workflow built on RepRapFirmware. Experimental tools are integrated as modular subsystems while motion control and automation logic remain managed by the platform.

Each experiment is executed through a sequence of G-code macros that define device setup, motion routines, and experiment execution.

### Tool Integration

Experimental tools are mounted to the gantry as interchangeable modules. Each tool interacts with the platform through two primary interfaces:

**Mechanical interaction**  
The gantry positions the tool with precise XYZ motion relative to the experimental workspace.

**Control interface**  
The Duet controller communicates with the tool using hardware I/O, allowing external devices such as pumps, plasma generators, or sensors to be triggered or monitored during an experiment.

Each tool typically requires:

- a mounting interface on the gantry carriage
- optional controller I/O connections
- a set of control macros defining tool behaviour

This approach treats tools as modular subsystems while the motion platform and automation framework remain unchanged.

### Experiment Workflow

Experiments follow a general workflow consisting of three stages:

1. **System Preparation**  
   - home the motion platform  
   - load or select the required tool  
   - initialise external devices if required  

2. **Experiment Execution**  
   - activate the experimental tool through macros  
   - execute predefined motion paths  
   - coordinate motion with device control signals  

3. **Completion and Reset**  
   - stop tool operation  
   - return the gantry to a safe position  
   - prepare the system for the next experiment  

### Macro-Based Control

RepRapFirmware allows reusable G-code macros to define experiment behaviour. These macros encapsulate common actions such as tool activation, device control, and motion routines.

Typical macro categories include:

- **setup macros** – prepare the system or initialise devices  
- **tool macros** – control specific experimental hardware  
- **motion macros** – execute experimental motion paths  
- **shutdown macros** – safely stop the experiment

By organising experiments into reusable macros, new workflows can be developed without modifying the underlying platform configuration.