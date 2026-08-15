---
doctype: Index
doc_id: OV-DOCS-INDEX
title: OpenVVVF Documentation Index
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-08-08"
description: Portal to OpenVVVF product documentation, hardware manuals, software targets, safety analyses, and validation evidence.
nav_order: 0
---

> **Draft v0.1**
> This documentation site is a work in progress. Pages that are still empty or under revision are marked with a **WIP** badge in the sidebar and on the index cards below.

# OpenVVVF Documentation

OpenVVVF is an open-source Variable Voltage Variable Frequency (VVVF) traction inverter platform. A single control module runs the motor-control firmware and talks to one of several power-stage chassis. The same hardware can serve very different applications - motorcycle, passenger car, industrial drive, or rail - by selecting the right power stage and configuring the safety profile.

This site is the single source of truth for OpenVVVF hardware manuals, software documentation, safety analyses, and validation evidence.

<div class="card">
<h3>Getting Started</h3>
<ul>
<li><strong>New users</strong> - read the overview, architecture, and glossary sections on this page first.</li>
<li><strong>Installers / Technicians</strong> - start with <a href="Hardware/Power-Stages/Index.md">Power Stages</a> to choose the correct chassis, then open its integration or assembly guide.</li>
<li><strong>Developers</strong> - see the <a href="Hardware/Control-Assembly/Index.md">Control Assembly</a> and <a href="Software/Index.md">Software</a> sections.</li>
<li><strong>Safety / Compliance Reviewers</strong> - begin with the <a href="Safety-and-Compliance/HARA/Core/Index.md">HARA Core</a>, <a href="Safety-and-Compliance/Compliance/Index.md">Compliance</a>, and <a href="Safety-and-Compliance/Testing/Index.md">Testing & Validation</a> docs.</li>
</ul>
</div>

## Documentation sections

<div class="landing-grid">

<div class="card">
<h3><a href="Hardware/Index.md">Hardware</a></h3>
<p>Physical OpenVVVF hardware: the reusable control module and the power-stage chassis families.</p>
<ul>
<li><a href="Hardware/Control-Assembly/Index.md">Control Assembly</a></li>
<li><a href="Hardware/Power-Stages/Index.md">Power Stages</a></li>
</ul>
</div>

<div class="card">
<h3><a href="Software/Index.md">Software</a></h3>
<p>Firmware targets and host software.</p>
<ul>
<li><a href="Software/Main-MCU/Index.md">Main MCU</a></li>
<li><a href="Software/Safety-Coprocessor/Index.md">Safety Coprocessor</a></li>
<li><a href="Software/RTE-Studio/Index.md">RTE Studio</a></li>
<li><a href="Software/Codegen/Index.md">Codegen</a> <span class="status-badge status-draft">WIP</span></li>
</ul>
</div>

<div class="card">
<h3><a href="Safety-and-Compliance/Index.md">Safety and Compliance</a></h3>
<p>Hazard analyses, threat analyses, standards mappings, and validation evidence.</p>
<ul>
<li><a href="Safety-and-Compliance/HARA/Core/Index.md">HARA Core</a></li>
<li><a href="Safety-and-Compliance/HARA/Application-Profiles/Motorcycle/Index.md">Motorcycle Application Profile</a></li>
<li><a href="Safety-and-Compliance/TARA/Index.md">TARA</a></li>
<li><a href="Safety-and-Compliance/Compliance/Index.md">Compliance</a></li>
<li><a href="Safety-and-Compliance/Testing/Index.md">Testing &amp; Validation</a></li>
</ul>
</div>

<div class="card">
<h3><a href="Tools/Index.md">Tools</a></h3>
<p>Support tools and widgets for working with OpenVVVF.</p>
<ul>
<li><a href="Tools/OpenVVVF-Telemetry-Viewer/Index.md">Telemetry Viewer</a></li>
</ul>
</div>

</div>

## System architecture

### Major blocks

- **Control module / control assembly** - The reusable dual-MCU control board that runs OpenVVVF firmware. It handles field-oriented motor control, state estimation, diagnostics, and safety monitoring.
- **Power stage** - The physical inverter assembly that contains the IGBTs, DC-link capacitors, gate drivers, current sensors, and thermal hardware.
  - **C2** - mid-size, 140 V nominal / up to 450 V class, ~600 A.
- **Main MCU software** - The primary microcontroller firmware; runs the real-time motor-control loop, PWM generation, ADC sampling, communication stacks, and application logic.
- **Safety coprocessor software** - A separate microcontroller that independently monitors safety-critical outputs and can bring the system to a safe state.
- **RTE Studio** - The host-side Real-Time Examiner and tuning tool. It connects to the inverter over CAN or Ethernet to log variables, adjust parameters, and run calibration routines.
- **Codegen tools** - Code and parameter generation tools that keep firmware data structures in sync with the hardware model.

### Data flow at a glance

```
RTE Studio / Codegen
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

## Glossary

### General terms

- **OpenVVVF** - Open-source Variable Voltage Variable Frequency traction inverter platform.
- **VVVF** - Variable Voltage Variable Frequency. A method for controlling AC motors by adjusting voltage and frequency.
- **Traction inverter** - A power-electronics converter that turns a DC bus into variable-frequency AC to drive a motor.
- **Chassis** - A mechanical/electrical form-factor family for power stages (currently C2).

### Software terms

- **MCU** - Microcontroller Unit. The main processor running the motor-control firmware.
- **Main MCU** - The primary microcontroller on the control module; runs the motor-control loop.
- **Safety coprocessor** - A separate microcontroller that independently monitors safety-critical outputs.
- **RTE** - Real-Time Examiner. The host-side tool for logging, tuning, and calibrating the inverter over CAN or Ethernet.
- **Codegen** - Code/parameter generation tools that keep firmware data structures in sync with the hardware model.
- **FOC** - Field-Oriented Control. The motor-control algorithm used to drive AC machines.
- **PWM** - Pulse-Width Modulation. The technique used to synthesize variable voltages from a fixed DC bus.
- **VCU** - Vehicle Control Unit. A higher-level controller that commands the inverter in a vehicle.

### Safety and compliance terms

- **HARA** - Hazard Analysis and Risk Assessment. A process for identifying hazardous events and assigning safety goals.
- **TARA** - Threat Analysis and Risk Assessment. The cybersecurity counterpart to HARA.
- **FMEA** - Failure Mode and Effects Analysis. A bottom-up method for analyzing how component failures affect the system.
- **ISO 26262** - Automotive functional-safety standard.
- **IEC 61800-5-2** - Industrial-drive safety standard.
- **ASIL** - Automotive Safety Integrity Level. A risk classification from A (lowest) to D (highest).
- **HVIL** - High-Voltage Interlock Loop. A safety circuit that detects when HV connectors are unmated.
- **Safe state** - A defined low-risk state the system enters after a fault.

### Electrical / mechanical terms

- **DC link** - The DC bus capacitors and connections between the battery/supply and the inverter bridge.
- **IGBT** - Insulated-Gate Bipolar Transistor. The power switch used in the inverter bridge.
- **Vdc** - DC-link voltage.
- **Vll** - Line-to-line AC voltage.
- **DCR** - DC Resistance. The resistance measured at DC, typically used for motor phase resistance.
- **LCR meter** - Instrument for measuring inductance, capacitance, and resistance.
- **Heatsink / baseplate** - The metal surface that conducts heat away from the IGBT modules.

