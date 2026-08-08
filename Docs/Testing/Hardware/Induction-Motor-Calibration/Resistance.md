> **TODO** - Run `cal Motor.Resistance` on this motor and compare the inverter estimate against the LCR reference below.

---
doctype: Test Report
doc_id: OV-TEST-HW-INDUCTION-RES-CAL
title: Induction Motor Resistance Calibration Validation
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-08-08"
status: draft
description: Validation of the inverter motor-resistance calibration routine on a TECO MAX-IE3 induction motor.
nav_order: 521
normative_refs:
  - OV-TEST-HW-INDUCTION-CAL-INDEX
  - OV-TEST-HW-INDEX
---

# Induction Motor Resistance Calibration Validation

This report validates the inverter's `cal Motor.Resistance` routine on a TECO MAX-IE3 7.5 kW induction motor. The test is run on the C2 chassis test fixture; the routine itself is shared across all OpenVVVF chassis.

## Test setup

The motor is a TECO Westinghouse MAX-IE3 3-phase induction motor. Phase leads are accessed at the conduit box for direct LCR measurement.

![TECO MAX-IE3 motor on the test bench](Motor-Test-Setup.jpg)

## Nameplate data

| Parameter | Value |
|-----------|-------|
| Manufacturer | TECO Westinghouse |
| Model | MAX-IE3 3-phase induction motor |
| Power | 10 HP / 7.5 kW |
| Frequency | 60 Hz base |
| Voltage | 208 V network |
| Current | 26.3 A |
| Enclosure | TEFC |

![TECO MAX-IE3 nameplate](Motor-Nameplate.jpg)

## Instrument

- **Instrument:** BK Precision 894 20 Hz - 500 kHz LCR Meter
- **Function:** DCR
- **Range:** AUTO

## Measurements

| Parameter | Value | Instrument settings |
|-----------|-------|---------------------|
| Rd (line-to-line) | 415.730 mΩ | FUNC: DCR, RANGE: AUTO, SPEED: FAST |
| Rd (per-phase, estimated) | ~207.9 mΩ | - |

![LCR meter DCR reading: Rd = 415.730 mΩ](Motor-LCR-DCR.jpg)

## Inverter-calibrated resistance

The inverter calibration routine has not yet been run on this motor. Once it is run, the estimate will be compared against the 415.730 mΩ line-to-line reference above.

## Notes

- The DCR reading is the DC resistance measured directly by the meter.
- The line-to-line resistance is twice the per-phase value reported by the calibration routine.
- This motor is an induction machine, not a PMSM, so it is tracked separately from the PMSM calibration report.
