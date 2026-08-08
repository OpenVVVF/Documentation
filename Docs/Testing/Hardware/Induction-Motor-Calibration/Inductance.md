---
doctype: Test Report
doc_id: OV-TEST-HW-INDUCTION-IND-CAL
title: Inductance Calibration Validation
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-08-08"
status: draft
description: Validation of the inverter motor-inductance calibration routine on a TECO MAX-IE3 induction motor.
nav_order: 522
placeholder: true
normative_refs:
  - OV-TEST-HW-INDUCTION-CAL-INDEX
  - OV-TEST-HW-INDEX
---

# Inductance Calibration Validation

> **Placeholder** — the inverter inductance calibration routine has not yet been run on this motor. This page captures the LCR reference measurement and will be updated with the inverter estimate once the test is run.
>
> **Raw telemetry:** [Open the test-session log in the Telemetry Viewer](../../../Tools/Telemetry-Viewer/telemetry-viewer.html?file=../../Testing/Hardware/Induction-Motor-Calibration/induction-cal.jsonl#s=cg_iu_a:left)

This report will validate the inverter's `cal Motor.Inductance` routine on a TECO MAX-IE3 7.5 kW induction motor.

## Instrument

- **Instrument:** BK Precision 894 20 Hz - 500 kHz LCR Meter
- **Function:** Ls-Rs
- **Test frequency:** 1.000 kHz
- **Test level:** 2.000 V
- **Bias:** 0.00 mV
- **Range:** AUTO

## Reference measurement

| Parameter | Value | Instrument settings |
|-----------|-------|---------------------|
| Ls | 17.8565 mH | FUNC: Ls-Rs, FREQ: 1.000 kHz, LEVEL: 2.000 V, RANGE: AUTO, SPEED: FAST |
| Rs | 55.4948 Ω | FUNC: Ls-Rs, FREQ: 1.000 kHz, LEVEL: 2.000 V, RANGE: AUTO, SPEED: FAST |

![LCR meter Ls-Rs reading: Ls = 17.8565 mH, Rs = 55.4948 Ω](Motor-LCR-Inductance.jpg)

## Inverter-calibrated inductance

The inverter calibration routine has not yet been run on this motor. Once it is run, the estimate will be compared against the 17.8565 mH reference above.

## Artifacts

- [Telemetry log (JSONL)](induction-cal.jsonl) — [open in Telemetry Viewer](../../../Tools/Telemetry-Viewer/telemetry-viewer.html?file=../../Testing/Hardware/Induction-Motor-Calibration/induction-cal.jsonl#s=cg_iu_a:left)
- [Static inductance reference photo (JPG)](Motor-LCR-Inductance.jpg)

## Notes

- The Ls-Rs reading is the series inductance and resistance at 1 kHz.
- The `Rs` value at 1 kHz is the AC series resistance; it is not the same as the DC resistance recorded in the resistance calibration report.
