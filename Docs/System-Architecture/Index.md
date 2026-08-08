---
doctype: Index
doc_id: OV-SYS-ARCH-INDEX
title: System Architecture
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-1
  - chassis-size-2
  - chassis-size-3
version: "0.1"
date: "2026-08-08"
status: draft
description: High-level map of the OpenVVVF ecosystem - control module, power stages, software targets, and application profiles.
nav_order: 10
normative_refs:
  - OV-DOCS-INDEX
---

# System Architecture

OpenVVVF is a modular traction inverter platform. A single control module runs the motor-control firmware and talks to one of several power-stage chassis. The same hardware can serve very different applications - motorcycle, passenger car, industrial drive, or rail - by selecting the right power stage and configuring the safety profile.

## Major blocks

### Control Module

The [Control Assembly](../Control-Assembly/index.html) is the reusable inverter brain. It is a dual-MCU board that handles field-oriented motor control, state estimation, diagnostics, and safety monitoring. It mounts onto a power stage through a standardized interface and is designed to work with any OpenVVVF chassis.

### Power Stages

[Power Stages](../Power-Stages/index.html) are the physical inverter assemblies. They contain the IGBT modules, DC-link capacitors, gate drivers, current sensors, and thermal hardware. Three chassis families are planned:

- **C1** - compact, low-power form factor.
- **C2** - mid-size, 140 V nominal / up to 450 V class, ~600 A.
- **C3** - large, up to 1200 V / 1400 A.

### Main MCU Software

The [Main MCU](../Software/Main-MCU/index.html) firmware implements the real-time motor-control loop, PWM generation, ADC sampling, communication stacks, and application logic. It is the primary compute target on the control module.

### Safety Coprocessor Software

The [Safety Coprocessor](../Software/Safety-Coprocessor/index.html) runs a separate safety monitor that cross-checks critical outputs and can bring the system to a safe state independently of the main MCU.

### RTE Host

The [RTE Host](../Software/RTE-Host/index.html) is the host-side real-time examiner and tuning tool. It connects to the inverter over CAN or Ethernet to log variables, adjust parameters, and run calibration routines.

### Codegen Tools

The [Codegen](../Software/Codegen/index.html) tools generate parameter files, lookup tables, and boilerplate from a shared hardware and application model so that the firmware stays in sync with the physical design.

### Application Profiles

Application profiles define the safety goals and compliance target for a given use case. The platform supports motorcycle, passenger-car, industrial-drive, and rail profiles. See the [HARA Core](../Safety-and-Compliance/HARA/Core/index.html) and [Compliance](../Safety-and-Compliance/Compliance/index.html) sections for details.

## Data flow at a glance

```
RTE Host / Codegen
       |
       | CAN / parameter files
       v
Control Module (Main MCU + Safety Coprocessor)
       |
       | PWM / gate-drive / sensor signals
       v
    Power Stage
       |
       | Three-phase output
       v
     Motor
```

## Where to go next

- [Control Assembly](../Control-Assembly/index.html) - hardware and software manuals for the control module.
- [Power Stages](../Power-Stages/index.html) - choose and build a chassis.
- [Software](../Software/index.html) - firmware targets and tools.
- [Safety and Compliance](../Safety-and-Compliance/index.html) - HARA, TARA, and standards mappings.
