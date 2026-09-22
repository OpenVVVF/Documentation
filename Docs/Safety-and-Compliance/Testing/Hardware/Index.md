---
doctype: Index
doc_id: OV-TEST-HW-INDEX
title: Hardware Tests
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.3"
date: "2026-09-22"
description: Hardware test reports and validation evidence.
nav_order: 341
---

# Hardware Tests

Electrical, thermal, mechanical, and environmental test records.

## PMSM motor

- [PMSM Resistance Calibration Validation](PMSM-Motor-Calibration/Resistance/Index.md)
- [Power Resistor Sanity Check](PMSM-Motor-Calibration/Resistor-Sanity-Check/Index.md)
- [PMSM Inductance Calibration Validation](PMSM-Motor-Calibration/Inductance/Index.md)

## Induction motor

- [Induction Motor Testbed](Induction-Motor-Calibration/Testbed/Index.md)
- [Induction Motor Resistance Calibration Validation](Induction-Motor-Calibration/Resistance/Index.md)
- [Inductance Calibration Validation](Induction-Motor-Calibration/Inductance/Index.md)
- [Induction Motor 1-Hour No-Load Test](Induction-Motor-No-Load-Test/Index.md)
- [Induction Motor 180 V Power Stage Bring-up](Induction-Motor-180V-Bringup/Index.md)
- [Induction Motor 180 V 20-Minute Reversal Test](Induction-Motor-180V-Reversal/Index.md)

## Gen7 hardware

- [Gen7 Board Temperature Sensor Validation](Gen7-Temp-Sensor-Validation/Index.md) - first Gen7 test record; validates the three board NTC temperature channels against a thermal imager under a torch-applied gradient.
- [Low-Power Regen 100 A Phase-Current Endurance (No Cooling)](Low-Power-Regen-100A-No-Cooling/Index.md) - 22-minute continuous regen at −100 A q-axis current on a dynamometer-spun induction machine with the bare power stage (no heatsink, no fan); peak board temp 80.4 °C.

## Cross-cutting

- [Motor Self-Commissioning Accuracy Report](Motor-Self-Commissioning-Accuracy/Index.md) - aggregates the calibration-validation measurements into a single accuracy record for the self-commissioning routine.
