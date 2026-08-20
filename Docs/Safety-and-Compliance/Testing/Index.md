---
doctype: Index
doc_id: OV-TEST-INDEX
title: Testing and Validation
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.2"
date: "2026-08-13"
description: Formal test reports and validation evidence for OpenVVVF hardware, firmware, and integration.
nav_order: 340
---

# Testing and Validation

This section contains formal test records and validation evidence. Each document is evidence that a specific feature, requirement, or hazard mitigation was exercised.

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

These reports validate the calibration routines on the C2 test fixture. The same routines are used on all OpenVVVF chassis; add a new report only when a different motor or harness is introduced.

### Safety-mechanism validation

| Test ID | Name | Scope | Status | Trace | Plan |
|---------|------|-------|--------|-------|------|
| - | Fault-Injection Test Plan | component / system / integration / environmental fault injection (control module + power stage) | planned | HARA safety goals, FSRs, hazards | [Plan](Fault-Injection-Test-Plan/Index.md) |
| - | Vibration Test Plan | mechanical/environmental random vibration (control module + C2 power stage assembly) | planned | HARA failure modes relying on connectors/harness; fault-injection E-01 | [Plan](Vibration-Test-Plan/Index.md) |
| - | Thermal Test Plan (DIY Chamber) | hardware thermal characterization + firmware thermal behavior (FSR-08 derate/SSO), C2 power stage | planned | OV-C2-DD-THERMAL, OV-C2-DD-DCLINK-THERMAL, FSR-08 | [Plan](Thermal-Test-Plan/Index.md) |

The fault-injection plan spans all test domains, so it is filed directly under Testing. Execution campaigns produce dated test reports filed as siblings of the plan, referencing it by test ID.

## Domains

Documents are filed by **what is being tested**, not by what equipment the bench uses:

- **Hardware** - The DUT is physical hardware: power-stage bring-up, thermal, and bench characterization. Firmware-routine validations whose error budget is power-stage physics (e.g. motor self-commissioning calibrated against instruments) also live here.
- **Firmware** - The DUT is control-module firmware logic: unit tests and host- or bench-based tests that do not inject physical faults.
- **Integration** - System-level tests combining control module and power stage.
