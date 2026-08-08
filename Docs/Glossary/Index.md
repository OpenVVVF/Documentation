---
doctype: Index
doc_id: OV-GLOSSARY-INDEX
title: Glossary
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-1
  - chassis-size-2
  - chassis-size-3
version: "0.1"
date: "2026-08-08"
status: draft
description: Common terms and acronyms used across OpenVVVF documentation.
nav_order: 5
normative_refs:
  - OV-DOCS-INDEX
---

# Glossary

This page defines terms and acronyms that appear throughout the OpenVVVF documentation. It is intended for both newcomers and engineers crossing over from other domains.

## General terms

- **OpenVVVF** - Open-source Variable Voltage Variable Frequency traction inverter platform.
- **VVVF** - Variable Voltage Variable Frequency. A method for controlling AC motors by adjusting voltage and frequency.
- **Traction inverter** - A power-electronics converter that turns a DC bus into variable-frequency AC to drive a motor.
- **Control module / control assembly** - The reusable dual-MCU control board that runs OpenVVVF firmware.
- **Power stage** - The physical inverter assembly that contains the IGBTs, capacitors, gate drivers, and sensors.
- **Chassis** - A mechanical/electrical form-factor family for power stages (C1, C2, C3).

## Software terms

- **MCU** - Microcontroller Unit. The main processor running the motor-control firmware.
- **Main MCU** - The primary microcontroller on the control module; runs the motor-control loop.
- **Safety coprocessor** - A separate microcontroller that independently monitors safety-critical outputs.
- **RTE** - Real-Time Examiner. The host-side tool for logging, tuning, and calibrating the inverter over CAN or Ethernet.
- **Codegen** - Code/parameter generation tools that keep firmware data structures in sync with the hardware model.
- **FOC** - Field-Oriented Control. The motor-control algorithm used to drive AC machines.
- **PWM** - Pulse-Width Modulation. The technique used to synthesize variable voltages from a fixed DC bus.
- **VCU** - Vehicle Control Unit. A higher-level controller that commands the inverter in a vehicle.

## Safety and compliance terms

- **HARA** - Hazard Analysis and Risk Assessment. A process for identifying hazardous events and assigning safety goals.
- **TARA** - Threat Analysis and Risk Assessment. The cybersecurity counterpart to HARA.
- **FMEA** - Failure Mode and Effects Analysis. A bottom-up method for analyzing how component failures affect the system.
- **ISO 26262** - Automotive functional-safety standard.
- **IEC 61800-5-2** - Industrial-drive safety standard.
- **ASIL** - Automotive Safety Integrity Level. A risk classification from A (lowest) to D (highest).
- **HVIL** - High-Voltage Interlock Loop. A safety circuit that detects when HV connectors are unmated.
- **Safe state** - A defined low-risk state the system enters after a fault.

## Electrical / mechanical terms

- **DC link** - The DC bus capacitors and connections between the battery/supply and the inverter bridge.
- **IGBT** - Insulated-Gate Bipolar Transistor. The power switch used in the inverter bridge.
- **Vdc** - DC-link voltage.
- **Vll** - Line-to-line AC voltage.
- **DCR** - DC Resistance. The resistance measured at DC, typically used for motor phase resistance.
- **LCR meter** - Instrument for measuring inductance, capacitance, and resistance.
- **Heatsink / baseplate** - The metal surface that conducts heat away from the IGBT modules.
