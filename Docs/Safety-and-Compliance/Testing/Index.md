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
date: "2026-08-07"
status: draft
description: Formal test reports and validation evidence for OpenVVVF hardware, firmware, and integration.
nav_order: 340
---

# Testing and Validation

This section contains formal test records and validation evidence. Each document is evidence that a specific feature, requirement, or hazard mitigation was exercised.

## Test evidence dashboard

### Hardware

| Test ID | Name | Motor class | Status | Trace | Report |
|---------|------|-------------|--------|-------|--------|
| 1 | PMSM Resistance Calibration Validation | PMSM | draft | motor self-commissioning / calibration routine | [Report](Hardware/Motor-Calibration/Resistance.html) |
| 2 | PMSM Inductance Calibration Validation | PMSM | draft | motor self-commissioning / calibration routine | [Report](Hardware/Motor-Calibration/Inductance.html) |
| 3 | Power Resistor Sanity Check | - | draft | motor self-commissioning / calibration routine | [Report](Hardware/Motor-Calibration/Resistor-Sanity-Check.html) |
| 4 | Induction Motor Testbed | Induction | draft | motor self-commissioning / calibration routine | [Report](Hardware/Induction-Motor-Calibration/Testbed.html) |
| 5 | Induction Motor Resistance Calibration Validation | Induction | draft | motor self-commissioning / calibration routine | [Report](Hardware/Induction-Motor-Calibration/Resistance.html) |
| 6 | Inductance Calibration Validation | Induction | draft | motor self-commissioning / calibration routine | [Report](Hardware/Induction-Motor-Calibration/Inductance.html) |

These reports validate the calibration routines on the C2 test fixture. The same routines are used on all OpenVVVF chassis; add a new report only when a different motor or harness is introduced.

## Domains

- **Hardware** - Electrical, thermal, mechanical, and environmental tests.
- **Firmware** - Unit tests, integration tests, fault-injection tests, and safety-mechanism tests.
- **Integration** - System-level tests combining control module and power stage.
