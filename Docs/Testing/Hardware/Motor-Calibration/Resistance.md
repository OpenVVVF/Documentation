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
nav_order: 512
normative_refs:
  - OV-TEST-HW-MOTOR-CAL-INDEX
  - OV-TEST-HW-INDEX
---

# Motor Resistance Calibration Validation

This report validates the inverter's `cal Motor.Resistance` routine by comparing its estimate against a direct bench LCR measurement of the test motor. The test was run on the C2 chassis test fixture, but the routine itself is shared across all OpenVVVF chassis; motor-specific validation is only needed when a different motor or harness is used.

Inductance reference measurements are kept in the [Motor Inductance Calibration Validation](Inductance.html) report.

## Test setup

The motor is mounted on the Sierra CP Engineering test fixture with phase leads accessible for direct LCR measurement.

![Motor mounted on the Sierra CP Engineering test fixture](IMG_20260807_203502.jpg)

![Side view of the motor and fixture](IMG_20260807_203510.jpg)

## Instrument

- **Instrument:** BK Precision 894 20 Hz - 500 kHz LCR Meter
- **Function:** DCR
- **Range:** AUTO

## Measurements

### Phase resistance (DCR)

| Parameter | Value | Instrument settings |
|-----------|-------|---------------------|
| Rd | 15.293 mΩ | FUNC: DCR, RANGE: AUTO, SPEED: MED |

![LCR meter DCR reading: Rd = 15.293 mΩ](IMG_20260807_210344.jpg)

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

## Power-resistor sanity check

To check that the calibration routine returns a sensible value for a purely resistive, high-impedance load, a known power resistor was connected across phases U and V. The resistor was 23 Ω. With a 120 V DC bus and the routine's duty clamp limiting the applied voltage, only ~0.3 A could be pushed through the load.

### Setup

- Load: 23 Ω power resistor tied across U-V (two phases in parallel).
- DC bus: ~121 V.
- Command: `cal Motor.Resistance 8.0 --force`.

### Results

| Parameter | Value |
|-----------|-------|
| Reference resistance | 23 Ω |
| Calibrated UV line-to-line | 20.94 Ω |
| Calibrated UV per-phase | 10.47 Ω |
| Max current reached (UV) | 0.345 A |
| Fit offset (V_off) | 23.6 V |
| UW measurement | Failed (non-positive resistance) |

- Command log: [PowerResistor-Command-Log.txt](PowerResistor-Command-Log.txt)
- Raw telemetry: [PowerResistor-Telemetry.jsonl](PowerResistor-Telemetry.jsonl)

### Analysis

The 9 % low reading (21 Ω vs 23 Ω) is expected at this operating point. At ~0.3 A the IGBTs are still in the knee region, where `Vce ≈ Vf(knee) + Ic · Rce(on)`. The knee voltage across the two conducting IGBTs is large compared with the ~6-7 V across the resistor, and the linear fit absorbs most of that knee as an offset. Because the knee is slightly curved, the slope is biased low.

The UW phase failed because no resistor was connected across U-W; the measured current had the wrong sign and the fit produced a negative resistance. This is normal for a single-pair measurement.

This result is not motor-grade accuracy, but it confirms the calibration is in the right decade and is not producing the milliohm-scale nonsense that appears when the routine is run without a real load.

## Notes

- The DCR reading is the DC resistance measured directly by the meter.
- The line-to-line resistance is twice the per-phase value reported by the calibration routine.
