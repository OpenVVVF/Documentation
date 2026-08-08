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
description: Validation of the inverter motor-resistance calibration routine against bench LCR reference measurements on multiple motors.
nav_order: 512
normative_refs:
  - OV-TEST-HW-MOTOR-CAL-INDEX
  - OV-TEST-HW-INDEX
---

# Motor Resistance Calibration Validation

This report validates the inverter's `cal Motor.Resistance` routine by comparing its estimate against direct bench LCR measurements of several test motors. The tests are run on the C2 chassis test fixture, but the routine itself is shared across all OpenVVVF chassis; motor-specific validation is only needed when a different motor or harness is used.

Inductance reference measurements are kept in the [Motor Inductance Calibration Validation](Inductance.html) report.

A separate high-resistance load sanity check is documented in [Power Resistor Sanity Check](Resistor-Sanity-Check.html).

## Motor 1 - Sierra CP Engineering test fixture motor

### Test setup

The first motor is mounted on the Sierra CP Engineering test fixture with phase leads accessible for direct LCR measurement.

![Motor mounted on the Sierra CP Engineering test fixture](IMG_20260807_203502.jpg)

![Side view of the motor and fixture](IMG_20260807_203510.jpg)

### Instrument

- **Instrument:** BK Precision 894 20 Hz - 500 kHz LCR Meter
- **Function:** DCR
- **Range:** AUTO

### Measurements

| Parameter | Value | Instrument settings |
|-----------|-------|---------------------|
| Rd | 15.293 mΩ | FUNC: DCR, RANGE: AUTO, SPEED: MED |

![LCR meter DCR reading: Rd = 15.293 mΩ](IMG_20260807_210344.jpg)

### Inverter-calibrated resistance

The inverter's `cal Motor.Resistance` routine was run to estimate the motor resistance and compare it against the LCR reference. Two runs were made at different DC-link voltages to check consistency.

#### Summary

| Run | Vdc | UV Rll | UW Rll | VW Rll | Average Rll | Per-phase (avg) |
|-----|-----|--------|--------|--------|-------------|-----------------|
| 1 | ~50 V | 15.2301 mΩ | 15.5424 mΩ | 15.6386 mΩ | **15.4704 mΩ** | 7.7352 mΩ |
| 2 | ~120 V | 13.5548 mΩ | 13.7229 mΩ | 15.6423 mΩ | **14.3067 mΩ** | 7.1534 mΩ |
| LCR reference | - | - | - | - | **15.293 mΩ** | 7.6465 mΩ |

- Run 1 at ~50 V is within **+1.2 %** of the LCR reference (15.4704 mΩ vs 15.293 mΩ).
- Run 2 at ~120 V reads lower on UV and UW, pulling the average **-6.5 %** below the LCR reference. The VW pair is consistent with run 1 and the reference.
- The raw command log is available: [Resistance-Command-Log.txt](Resistance-Command-Log.txt).

#### Calibration graph

The plot below shows phase currents, DC bus voltage, and the per-phase resistance estimate for both bus voltages.

![Resistance calibration: 50 V vs 120 V bus](ResistanceCalResult_50v_vs_120v.png)

From the plotted telemetry:

- **50 V run:** R_phase_avg = **7.74 mΩ**
- **120 V run:** R_phase_avg = **7.15 mΩ**
- **ΔR between runs:** 0.58 mΩ

#### Observations

- The 50 V result (7.74 mΩ average phase) is within **+1.2 %** of the LCR reference (7.6465 mΩ per phase).
- The 120 V result reads lower by **-6.5 %**. The per-phase traces in the plot are stable and consistent with each other, so the shift appears to be a systematic offset between the two runs rather than a noisy measurement.
- Possible causes for the 120 V offset:
  - current-sensor offset or scaling drift at the higher DC-link voltage,
  - connection/cable resistance differences between setups,
  - temperature or settling differences between runs.
- The raw telemetry log is available for further analysis: [ResistanceCalResult.jsonl](ResistanceCalResult.jsonl).

## Motor 2 - TECO MAX-IE3 7.5 kW induction motor

### Test setup

The second motor is a TECO Westinghouse MAX-IE3 3-phase induction motor. The phase leads are accessed at the conduit box for direct LCR measurement.

![TECO MAX-IE3 motor on the test bench](Motor2-Test-Setup.jpg)

### Nameplate data

| Parameter | Value |
|-----------|-------|
| Manufacturer | TECO Westinghouse |
| Model | MAX-IE3 3-phase induction motor |
| Power | 10 HP / 7.5 kW |
| Frequency | 60 Hz base |
| Voltage | 208 V network |
| Current | 26.3 A |
| Enclosure | TEFC |

![TECO MAX-IE3 nameplate](Motor2-Nameplate.jpg)

### Instrument

- **Instrument:** BK Precision 894 20 Hz - 500 kHz LCR Meter
- **Function:** DCR
- **Range:** AUTO

### Measurements

| Parameter | Value | Instrument settings |
|-----------|-------|---------------------|
| Rd (line-to-line) | 415.730 mΩ | FUNC: DCR, RANGE: AUTO, SPEED: FAST |
| Rd (per-phase, estimated) | ~207.9 mΩ | - |

![LCR meter DCR reading: Rd = 415.730 mΩ](Motor2-LCR-DCR.jpg)

### Inverter-calibrated resistance

The inverter calibration routine has not yet been run on this motor. Once it is run, the estimate will be compared against the 415.730 mΩ line-to-line reference above.

## Notes

- The DCR reading is the DC resistance measured directly by the meter.
- The line-to-line resistance is twice the per-phase value reported by the calibration routine.
- The Ls-Rs `Rs` value measured at 1 kHz is not the same as DCR; it includes AC effects such as skin and proximity losses and is recorded in the inductance report instead.
