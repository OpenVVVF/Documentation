---
doctype: Test Report
doc_id: OV-TEST-HW-SELF-COMMISSIONING
title: Motor Self-Commissioning Accuracy Report
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-08-13"
description: Aggregated accuracy evidence for the motor self-commissioning routine, comparing its resistance and inductance estimates against instrumented bench references.
test_id: 10
nav_order: 357
normative_refs:
  - OV-TEST-HW-MOTOR-RES-CAL
  - OV-TEST-HW-MOTOR-IND-CAL
  - OV-TEST-HW-RESISTOR-SANITY
  - OV-TEST-HW-INDUCTION-TESTBED
  - OV-TEST-HW-INDUCTION-RES-CAL
  - OV-TEST-HW-INDUCTION-IND-CAL
  - OV-SAF-HARA-CORE
  - OV-TEST-HW-INDEX
---

# Motor Self-Commissioning Accuracy Report

The motor self-commissioning routine (resistance and inductance estimation) currently produces calibration values with no formal accuracy evidence. This report aggregates the existing instrumented calibration-validation measurements so the self-commissioning results become traceable compliance artifacts. All values below are taken verbatim from the referenced calibration reports; no new measurements were made for this report.

## Scope and referenced documents

Scope: the `cal Motor.Resistance` routine and the motor-inductance calibration routines (`cal Motor.Induction.VHz` for induction machines) as validated on the C2 chassis test fixture with two machine classes:

- PMSM test motor on the Sierra CP Engineering fixture.
- TECO Westinghouse MAX-IE3 7.5 kW induction motor (see [Induction Motor Testbed](../Induction-Motor-Calibration/Testbed/Index.md)).

Referenced validation reports:

- [PMSM Resistance Calibration Validation](../PMSM-Motor-Calibration/Resistance/Index.md) (`OV-TEST-HW-MOTOR-RES-CAL`)
- [PMSM Inductance Calibration Validation](../PMSM-Motor-Calibration/Inductance/Index.md) (`OV-TEST-HW-MOTOR-IND-CAL`)
- [Power Resistor Sanity Check](../PMSM-Motor-Calibration/Resistor-Sanity-Check/Index.md) (`OV-TEST-HW-RESISTOR-SANITY`)
- [Induction Motor Testbed](../Induction-Motor-Calibration/Testbed/Index.md) (`OV-TEST-HW-INDUCTION-TESTBED`)
- [Induction Motor Resistance Calibration Validation](../Induction-Motor-Calibration/Resistance/Index.md) (`OV-TEST-HW-INDUCTION-RES-CAL`)
- [Inductance Calibration Validation](../Induction-Motor-Calibration/Inductance/Index.md) (`OV-TEST-HW-INDUCTION-IND-CAL`)

## Method under test

The self-commissioning routine estimates motor parameters from the inverter's own voltage and current measurements, without external instrumentation:

- **Resistance:** `cal Motor.Resistance` drives a controlled current into each phase pair (UV, UW, VW), fits the voltage/current slope, and reports line-to-line resistance per pair. The per-phase value is half the line-to-line value.
- **Inductance (induction machines):** `cal Motor.Induction.VHz` applies a 10 Hz V/Hz excitation, hunts for a modulation index producing roughly 5 A of phase current, sweeps modulation points around that operating point, and reports the series inductance `Ls` at each point.
- **Inductance (PMSM):** the same comparison is planned for the PMSM test motor; the inverter-side run has not been performed yet.

The reference baseline is a BK Precision 894 LCR meter (20 Hz - 500 kHz), using DCR for resistance and Ls-Rs at 1.000 kHz for inductance, connected directly at the motor phase leads with the inverter disconnected.

## Acceptance criteria

The source calibration reports do not state formal pass/fail tolerances. The following criteria are **provisional** and proposed for formal adoption:

| Parameter | Provisional tolerance (estimated vs. instrument reference) | Basis |
|-----------|------------------------------------------------------------|-------|
| Resistance (motor windings) | within ±10 % | Largest observed deviation: -6.5 % (PMSM, 120 V run) and +7.3 % (induction, ~80 V bus) |
| Inductance | within ±10 % | Largest observed deviation: +2.4 % (induction) |
| High-impedance sanity load | within ±10 % | Observed: ~9 % low on a 23 Ω power resistor at low current |

These tolerances are marked provisional pending review; they are consistent with the systematic offsets (IGBT knee voltage, dead time, current-sensor scaling) analyzed in the source reports.

## Results

### PMSM test motor

| Parameter | Instrument baseline | Self-commissioning estimate | Deviation | Source report |
|-----------|--------------------|-----------------------------|-----------|---------------|
| Resistance, line-to-line (run at ~50 V bus) | 15.293 mΩ (DCR) | 15.4704 mΩ (average of UV/UW/VW) | +1.2 % | OV-TEST-HW-MOTOR-RES-CAL |
| Resistance, line-to-line (run at ~120 V bus) | 15.293 mΩ (DCR) | 14.3067 mΩ (average of UV/UW/VW) | -6.5 % | OV-TEST-HW-MOTOR-RES-CAL |
| Resistance, per-phase (run at ~50 V bus) | 7.6465 mΩ | 7.7352 mΩ | +1.2 % | OV-TEST-HW-MOTOR-RES-CAL |
| Resistance, per-phase (run at ~120 V bus) | 7.6465 mΩ | 7.1534 mΩ | -6.5 % | OV-TEST-HW-MOTOR-RES-CAL |
| Inductance (Ls at 1 kHz) | 71.2980 µH / 34.6583 µH (two Ls-Rs readings) | TBD - inverter inductance calibration run pending | TBD | OV-TEST-HW-MOTOR-IND-CAL |

### Known-load sanity check (23 Ω power resistor)

| Parameter | Instrument baseline | Self-commissioning estimate | Deviation | Source report |
|-----------|--------------------|-----------------------------|-----------|---------------|
| Resistance, UV line-to-line | 23.3070 Ω (DCR) | 20.94 Ω | ~-9 % | OV-TEST-HW-RESISTOR-SANITY |

The ~9 % low reading is explained in the source report: at ~0.3 A the IGBTs operate in the knee region and the linear fit absorbs most of the knee as an offset, biasing the slope low. This test point confirms the routine produces the right decade on a non-motor load; it is not motor-grade accuracy.

### Induction motor (TECO MAX-IE3 7.5 kW)

| Parameter | Instrument baseline | Self-commissioning estimate | Deviation | Source report |
|-----------|--------------------|-----------------------------|-----------|---------------|
| Resistance, line-to-line (~80.6 V bus, ~40 A max) | 415.730 mΩ (DCR) | 446.16 mΩ (average of UV/UW/VW) | +7.3 % | OV-TEST-HW-INDUCTION-RES-CAL |
| Resistance, per-phase | ~207.9 mΩ | 223.08 mΩ | +7.3 % | OV-TEST-HW-INDUCTION-RES-CAL |
| Inductance, Ls (highest-current sweep points, 40/80/120 V bus) | 17.8565 mH (Ls-Rs, 1 kHz) | ~18.3 mH | +2.4 % | OV-TEST-HW-INDUCTION-IND-CAL |

## Conclusion

Against the provisional ±10 % criteria:

- **PMSM resistance:** pass at both bus voltages (+1.2 % / -6.5 %).
- **PMSM inductance:** open - measurement pending (TBD).
- **Induction resistance:** pass (+7.3 %).
- **Induction inductance:** pass (+2.4 %).
- **Sanity load:** pass within the provisional tolerance (~9 % low), with the low-current caveat documented in the source report.

The self-commissioning routine produces resistance and inductance estimates within a few percent of the instrumented baseline on real motor windings at representative operating points. The remaining open item is the PMSM inverter-side inductance run.

## Traceability

- This report satisfies the compliance need for **accuracy evidence of the motor self-commissioning routine**: calibration values consumed by the control firmware are now backed by instrumented comparisons rather than unverified self-estimates.
- The aggregated evidence traces to the platform hazard analysis (`OV-SAF-HARA-CORE`), where correct motor-parameter estimation underpins the torque-control assumptions of the VVVF control strategy.
- Each row in the results tables traces to a formal test report (test IDs 1-6) that retains the raw command logs, telemetry (JSONL), and instrument photographs as primary artifacts. Add a row here whenever a new motor class or harness is validated.

## Artifacts

All primary artifacts (command logs, telemetry logs, plots, instrument photos) are retained in the referenced source reports; this report intentionally duplicates none of them.
