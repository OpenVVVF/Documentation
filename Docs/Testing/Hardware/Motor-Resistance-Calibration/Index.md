---
doctype: Test Report
doc_id: OV-TEST-HW-MOTOR-RES-CAL
title: Motor Resistance Calibration Validation
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-08-08"
status: draft
description: Validation of the inverter motor-resistance calibration routine against a bench LCR reference.
nav_order: 511
normative_refs:
  - OV-TEST-HW-INDEX
---

# Motor Resistance Calibration Validation

This report validates the inverter's `cal Motor.Resistance` routine by comparing its estimate against a direct bench LCR measurement of the test motor. The test was run on the C2 chassis test fixture, but the routine itself is shared across all OpenVVVF chassis; motor-specific validation is only needed when a different motor or harness is used.

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

## Inverter-calibrated resistance

The inverter's `cal Motor.Resistance` routine was run to estimate the motor resistance and compare it against the LCR reference. Two runs were made at different DC-link voltages to check consistency.

### Summary

| Run | Vdc | UV Rll | UW Rll | VW Rll | Average Rll | Per-phase (avg) |
|-----|-----|--------|--------|--------|-------------|-----------------|
| 1 | ~50 V | 15.2301 mΩ | 15.5424 mΩ | 15.6386 mΩ | **15.4704 mΩ** | 7.7352 mΩ |
| 2 | ~120 V | 13.5548 mΩ | 13.7229 mΩ | 15.6423 mΩ | **14.3067 mΩ** | 7.1534 mΩ |
| LCR reference | - | - | - | - | **15.293 mΩ** | 7.6465 mΩ |

- Run 1 at ~50 V is within **+1.2 %** of the LCR reference (15.4704 mΩ vs 15.293 mΩ).
- Run 2 at ~120 V reads lower on UV and UW, pulling the average **-6.5 %** below the LCR reference. The VW pair is consistent with run 1 and the reference.
- The raw command log is available: [Resistance-Command-Log.txt](Resistance-Command-Log.txt).

### Calibration graph

The plot below shows phase currents, DC bus voltage, and the per-phase resistance estimate for both bus voltages.

![Resistance calibration: 50 V vs 120 V bus](ResistanceCalResult_50v_vs_120v.png)

From the plotted telemetry:

- **50 V run:** R_phase_avg = **7.74 mΩ**
- **120 V run:** R_phase_avg = **7.15 mΩ**
- **ΔR between runs:** 0.58 mΩ

### Observations

- The 50 V result (7.74 mΩ average phase) is within **+1.2 %** of the LCR reference (7.6465 mΩ per phase).
- The 120 V result reads lower by **-6.5 %**. The per-phase traces in the plot are stable and consistent with each other, so the shift appears to be a systematic offset between the two runs rather than a noisy measurement.
- Possible causes for the 120 V offset:
  - current-sensor offset or scaling drift at the higher DC-link voltage,
  - connection/cable resistance differences between setups,
  - temperature or settling differences between runs.
- The raw telemetry log is available for further analysis: [ResistanceCalResult.jsonl](ResistanceCalResult.jsonl).

## Notes

- The DCR reading is the DC resistance measured directly by the meter.
- The Ls-Rs readings are series inductance and resistance at 1 kHz.
- Which phase pair or winding configuration each Ls-Rs reading corresponds to should be recorded when the calibration routine results are compared against these reference values.
