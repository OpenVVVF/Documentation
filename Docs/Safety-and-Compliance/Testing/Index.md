---
doctype: Index
doc_id: OV-TEST-INDEX
title: Testing and Validation
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
  - chassis-size-3
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

### Firmware

| Test ID | Name | Scope | Status | Trace | Report |
|---------|------|-------|--------|-------|--------|
| - | Fault-Injection Test Plan | fault injection / safety mechanisms | planned | safety-mechanism validation | [Plan](Firmware/Fault-Injection-Test-Plan/Index.md) |

## Domains

- **Hardware** - Electrical, thermal, mechanical, and environmental tests.
- **Firmware** - Unit tests, integration tests, fault-injection tests, and safety-mechanism tests.
- **Integration** - System-level tests combining control module and power stage.
