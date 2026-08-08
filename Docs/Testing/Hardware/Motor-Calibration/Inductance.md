---
doctype: Test Report
doc_id: OV-TEST-HW-MOTOR-IND-CAL
title: Motor Inductance Calibration Validation
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-08-08"
status: draft
placeholder: true
description: Placeholder for validation of the inverter motor-inductance calibration routine against a bench LCR reference.
nav_order: 513
normative_refs:
  - OV-TEST-HW-MOTOR-CAL-INDEX
---

# Motor Inductance Calibration Validation

This report will validate the inverter's motor-inductance calibration routine by comparing its estimate against a direct bench LCR measurement of the same motor.

## Test setup

The same motor and Sierra CP Engineering fixture used for the resistance validation will be used here.

![Motor mounted on the Sierra CP Engineering test fixture](IMG_20260807_203502.jpg)

![Side view of the motor and fixture](IMG_20260807_203510.jpg)

## Instrument

- **Instrument:** BK Precision 894 20 Hz - 500 kHz LCR Meter
- **Planned test frequency:** 1.000 kHz (or the frequency used by the calibration routine)
- **Test level:** 2.000 V
- **Bias:** 0.00 mV
- **Range:** AUTO

## Planned measurements

### Phase inductance (Ls-Rs)

Reference Ls-Rs measurements will be captured for each phase pair and compared against the inverter's calibrated inductance.

### Inverter-calibrated inductance

The inverter's inductance calibration routine will be run and its output compared against the LCR reference.

## Notes

- Add the LCR meter photos and readings here.
- Add the inverter calibration command log / telemetry log when available.
- The calibration routine itself is shared across OpenVVVF chassis; this report validates it on the C2 test motor.
