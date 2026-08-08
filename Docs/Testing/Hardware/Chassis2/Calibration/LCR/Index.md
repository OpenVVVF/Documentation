---
doctype: Test Report
doc_id: OV-TEST-HW-C2-LCR-CAL
title: Motor LCR Reference Calibration
product_line: openvvvf
applies_to:
  - chassis-size-2
version: "0.1"
date: "2026-08-08"
status: draft
description: Reference LCR measurements of the motor before running the inverter self-commissioning / calibration routine.
nav_order: 511
normative_refs:
  - OV-TEST-HW-INDEX
---

# Motor LCR Reference Calibration

These are reference measurements of the motor taken with a BK Precision 894 LCR meter before running the inverter's self-commissioning / calibration routine. The same motor parameters will be estimated by the calibration routine and compared against these instrument readings.

## Test setup

The motor is mounted on the Sierra CP Engineering test fixture with phase leads accessible for direct LCR measurement.

![Motor mounted on the Sierra CP Engineering test fixture](IMG_20260807_203502.jpg)

![Side view of the motor and fixture](IMG_20260807_203510.jpg)

## Instrument

- **Instrument:** BK Precision 894 20 Hz - 500 kHz LCR Meter
- **Test frequency:** 1.000 kHz (for Ls-Rs measurements)
- **Test level:** 2.000 V
- **Bias:** 0.00 mV
- **Range:** AUTO

## Measurements

### Phase resistance (DCR)

| Parameter | Value | Instrument settings |
|-----------|-------|---------------------|
| Rd | 15.293 mΩ | FUNC: DCR, RANGE: AUTO, SPEED: MED |

![LCR meter DCR reading: Rd = 15.293 mΩ](IMG_20260807_210344.jpg)

### Phase inductance and series resistance (Ls-Rs)

Two Ls-Rs readings were captured at 1.000 kHz.

| Reading | Ls | Rs | Instrument settings |
|---------|----|----|---------------------|
| 1 | 71.2980 µH | 0.02817 Ω | FUNC: Ls-Rs, FREQ: 1.000 kHz, LEVEL: 2.000 V, RANGE: AUTO, SPEED: FAST |
| 2 | 34.6583 µH | 0.00974 Ω | FUNC: Ls-Rs, FREQ: 1.000 kHz, LEVEL: 2.000 V, RANGE: AUTO, SPEED: FAST |

![LCR meter Ls-Rs reading 1: Ls = 71.2980 µH, Rs = 0.02817 Ω](IMG_20260807_212055.jpg)

![LCR meter Ls-Rs reading 2: Ls = 34.6583 µH, Rs = 0.00974 Ω](IMG_20260807_212115.jpg)

## Notes

- The DCR reading is the DC resistance measured directly by the meter.
- The Ls-Rs readings are series inductance and resistance at 1 kHz.
- Which phase pair or winding configuration each Ls-Rs reading corresponds to should be recorded when the calibration routine results are compared against these reference values.
