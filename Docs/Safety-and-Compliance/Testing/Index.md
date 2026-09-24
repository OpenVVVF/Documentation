---
doctype: Index
doc_id: OV-TEST-INDEX
title: Testing and Validation
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.5"
date: "2026-09-24"
description: Formal test reports and validation evidence for OpenVVVF hardware, firmware, and integration.
nav_order: 340
---

# Testing and Validation

This section contains formal test records and validation evidence. Each document is evidence that a specific feature, requirement, or hazard mitigation was exercised.

All hardware power tests follow the shared definitions and evidence requirements of the [Hardware Test Methodology](Test-Methodology/Index.md) — steady-state criteria, calculated quantities (P/Q/PF/efficiency), reconciliation rules, and naming.

## Test evidence dashboard

### Hardware

| Test ID | Name | Motor class | Status | Trace | Report |
|---------|------|-------------|--------|-------|--------|
| 1 | PMSM Resistance Calibration Validation | PMSM | draft | motor self-commissioning / calibration routine | [Report](Hardware/PMSM-Motor-Calibration/Resistance/Index.md) |
| 2 | PMSM Inductance Calibration Validation | PMSM | draft | motor self-commissioning / calibration routine | [Report](Hardware/PMSM-Motor-Calibration/Inductance/Index.md) |
| 3 | Power Resistor Sanity Check | - | draft | motor self-commissioning / calibration routine | [Report](Hardware/PMSM-Motor-Calibration/Resistor-Sanity-Check/Index.md) |
| 4 | Induction Motor Testbed | Induction | draft | motor self-commissioning / calibration routine | [Report](Hardware/Induction-Motor-Calibration/Testbed/Index.md) |
| 5 | Induction Motor Resistance Calibration Validation | Induction | draft | motor self-commissioning / calibration routine | [Report](Hardware/Induction-Motor-Calibration/Resistance/Index.md) |
| 6 | Inductance Calibration Validation | Induction | draft | motor self-commissioning / calibration routine | [Report](Hardware/Induction-Motor-Calibration/Inductance/Index.md) |
| 7 | Induction Motor 1-Hour No-Load Test | Induction | draft | gate-driver switching / thermal baseline | [Report](Hardware/Induction-Motor-No-Load-Test/Index.md) |
| 8 | Induction Motor 180 V Power Stage Bring-up | Induction | draft | power-stage bring-up at elevated bus voltage | [Report](Hardware/Induction-Motor-180V-Bringup/Index.md) |
| 9 | Induction Motor 180 V 20-Minute Reversal Test | Induction | draft | direction-change sequencing / current control | [Report](Hardware/Induction-Motor-180V-Reversal/Index.md) |
| 10 | Motor Self-Commissioning Accuracy Report | PMSM + Induction | draft | motor self-commissioning / calibration routine | [Report](Hardware/Motor-Self-Commissioning-Accuracy/Index.md) |
| 11 | Gen7 Board Temperature Sensor Validation | - | draft | board temperature sensing / ADC measurement chain (OV-TEST-HW-GEN7-TEMP-NTC-VALIDATION) | [Report](Hardware/Gen7-Temp-Sensor-Validation/Index.md) |
| 12 | Low-Power Regen 100 A Phase-Current Endurance (No Cooling) | Induction | draft | high-current regen endurance / phase-current capability at low DC-bus voltage (no cooling) | [Report](Hardware/Low-Power-Regen-100A-No-Cooling/Index.md) |
| 13 | 200 A Regen to 79 °C — Gen7 Size 2 | Induction | draft | high-current regen staircase; thermal rise with dry heatsink interface | [Report](Hardware/Low-Power-Regen-200A-Gen7-Size2/Index.md) |
| 14 | Thermal OTP Trip — 200 A Regen, Gen7 Size 2 | Induction | draft | overtemperature protection chain validation (trip at ~80 °C baseplate) | [Report](Hardware/Thermal-OTP-200A-Gen7-Size2/Index.md) |
| 15 | Initial 400 A Regen Test — Gen7 Size 2 | Induction | draft | 400 A phase-current capability with bus clamp; current-clamp saturation identified as measurement artifact | [Report](Hardware/Low-Power-Regen-400A-Gen7-Size2/Index.md) |
| 16 | 450 A / 13 kW Regen — Gen7 Size 2 | Induction | draft | 450 A phase-current capability at ~150 V clamp; OT trip reproduced | [Report](Hardware/Low-Power-Regen-450A-Gen7-Size2/Index.md) |
| 17 | 200 A Regen Steady-State Thermal Test — Gen7 Size 2 | PMSM | draft | continuous-duty validation of the thermally-pasted interface (54.7 min, plateau 44.4/44.0 °C) | [Report](Hardware/Low-Power-Regen-200A-Steady-State-Gen7-Size2/Index.md) |
| 18 | 200 A Motoring Steady-State Thermal Test — Gen7 Size 2 | PMSM | draft | motoring-direction counterpart of test 17 (42 min, plateau 43.6/43.5 °C) | [Report](Hardware/Low-Power-Motoring-200A-Steady-State-Gen7-Size2/Index.md) |
| 19 | 300 A Regen Steady-State Thermal Test — Gen7 Size 2 | PMSM | draft | 300 A continuous regen at ~2,600 RPM (22.9 min, 11.7 kW, plateau 63.2/61.7 °C; stopped on machine limit) | [Report](Hardware/Low-Power-Regen-300A-Steady-State-Gen7-Size2/Index.md) |

These reports validate the calibration routines on the C2 test fixture. The same routines are used on all OpenVVVF chassis; add a new report only when a different motor or harness is introduced.

### Safety-mechanism validation

| Test ID | Name | Scope | Status | Trace | Plan |
|---------|------|-------|--------|-------|------|
| - | Fault-Injection Test Plan | component / system / integration / environmental fault injection (control module + power stage) | planned | HARA safety goals, FSRs, hazards | [Plan](Fault-Injection-Test-Plan/Index.md) |
| - | Vibration Test Plan | mechanical/environmental random vibration (control module + C2 power stage assembly) | planned | HARA failure modes relying on connectors/harness; fault-injection E-01 | [Plan](Vibration-Test-Plan/Index.md) |
| - | Thermal Test Plan | hardware thermal characterization + firmware thermal behavior (FSR-08 derate/SSO), C2 power stage | planned | OV-C2-DD-THERMAL, OV-C2-DD-DCLINK-THERMAL, FSR-08 | [Plan](Thermal-Test-Plan/Index.md) |

The fault-injection plan spans all test domains, so it is filed directly under Testing. Execution campaigns produce dated test reports filed as siblings of the plan, referencing it by test ID.

## Domains

Documents are filed by **what is being tested**, not by what equipment the bench uses:

- **Hardware** - The DUT is physical hardware: power-stage bring-up, thermal, and bench characterization. Firmware-routine validations whose error budget is power-stage physics (e.g. motor self-commissioning calibrated against instruments) also live here.
- **Firmware** - The DUT is control-module firmware logic: unit tests and host- or bench-based tests that do not inject physical faults.
- **Integration** - System-level tests combining control module and power stage.
