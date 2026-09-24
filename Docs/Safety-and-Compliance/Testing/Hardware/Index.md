---
doctype: Index
doc_id: OV-TEST-HW-INDEX
title: Hardware Tests
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.4"
date: "2026-09-24"
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
- [Initial 400 A Regen Test — Gen7 Size 2](Low-Power-Regen-400A-Gen7-Size2/Index.md) - first 400 A q-axis regen run with a Chroma load bank clamping the bus at 150 V (Sorensen regen sink ~50 A); 8.78 kW peak; apparent phase-current spikes later attributed to 150 A-rated Tektronix current clamps saturating (measurement artifact).
- [450 A / 13 kW Regen — Gen7 Size 2](Low-Power-Regen-450A-Gen7-Size2/Index.md) - 450 A q-axis regen at 2,000 RPM shaft speed, 12.8 kW average returned to the DC link, sustained 78 s until the inverter overtemperature protection tripped at ~80 °C baseplate as designed.
- [200 A Regen Steady-State Thermal Test — Gen7 Size 2](Low-Power-Regen-200A-Steady-State-Gen7-Size2/Index.md) - 54.7-minute continuous 200 A regen on the thermally-pasted assembly; baseplate plateaued at 44.4 / 44.0 °C against 22.5 °C ambient, validating the interface rework.
- [200 A Motoring Steady-State Thermal Test — Gen7 Size 2](Low-Power-Motoring-200A-Steady-State-Gen7-Size2/Index.md) - motoring-direction counterpart: 42-minute 200 A positive-torque hold drawing 2.46 kW, baseplate plateau 43.6 / 43.5 °C in cooler night ambient — same rise over ambient as regen, completing bidirectional 200 A continuous-duty validation.
- [300 A Regen Steady-State Thermal Test — Gen7 Size 2](Low-Power-Regen-300A-Steady-State-Gen7-Size2/Index.md) - 22.9-minute continuous 300 A regen at ~2,600 RPM returning 11.7 kW to a 150 V-clamped bus; baseplate reached effective steady state at 63.2 / 61.7 °C (~39 K over ambient). Stopped because the Zero ZF75-10 machine hit 86 °C on the thermal imager, not due to any inverter limit or fault.

## Cross-cutting

- [Motor Self-Commissioning Accuracy Report](Motor-Self-Commissioning-Accuracy/Index.md) - aggregates the calibration-validation measurements into a single accuracy record for the self-commissioning routine.
