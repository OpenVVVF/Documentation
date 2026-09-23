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
- [200 A Regen to 79 °C — Gen7 Size 2](Low-Power-Regen-200A-Gen7-Size2/Index.md) - 200 A q-axis regen staircase on Gen7 size 2, 3.14 kW average returned to the DC link, split at the first 79 °C inverter NTC reading; heatsink fitted without thermal interface material.
- [Thermal OTP Trip — 200 A Regen, Gen7 Size 2](Thermal-OTP-200A-Gen7-Size2/Index.md) - continuation of the same recording past 79 °C through the intended thermal over-temperature protection trip and cooldown.
- [Initial 400 A Regen Test — Gen7 Size 2](Low-Power-Regen-400A-Gen7-Size2/Index.md) - first 400 A q-axis regen run with a Chroma load bank clamping the bus at 150 V (Sorensen regen sink ~50 A); 8.78 kW peak, passed but stopped after unexplained phase-current spikes observed on the oscilloscope.

## Cross-cutting

- [Motor Self-Commissioning Accuracy Report](Motor-Self-Commissioning-Accuracy/Index.md) - aggregates the calibration-validation measurements into a single accuracy record for the self-commissioning routine.
