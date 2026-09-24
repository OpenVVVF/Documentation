---
doctype: Test Plan
doc_id: OV-TEST-HW-THERMAL-FSR08-THRESHOLDS
title: Thermal Derate and SSO Threshold Verification (FSR-08)
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.2"
date: "2026-09-24"
description: Verifies the FSR-08 temperature chain with applied heat — derate at 90 °C and safe state at 105 °C on the capacitor channel — reconciling the ~80 °C trip seen in earlier firmware builds.
nav_order: 385
placeholder: true
normative_refs:
  - OV-TEST-METHODOLOGY
  - OV-TEST-COVERAGE
  - OV-TEST-FAULT-INJECTION
  - OV-TEST-THERMAL-PLAN
---

# Thermal Derate and SSO Threshold Verification (FSR-08)

This plan follows Thermal Test Plan T-06 in [OV-TEST-THERMAL-PLAN](../../Thermal-Test-Plan/Index.md); here the stimulus is real applied heat (hot plate / controlled heat source) rather than chamber air, so each NTC channel can be swept through its configured threshold independently and without power conversion. It applies the standard definitions of [OV-TEST-METHODOLOGY](../../Test-Methodology/Index.md) and follows the status vocabulary and evidence framework of [OV-TEST-FAULT-INJECTION](../../Fault-Injection-Test-Plan/Index.md). Methodology archetype: **D — protection validation** (one protection chain exercised deliberately; the DUT must respond; a non-response is a fail).

**Existing evidence claimed (no reheating of the actuation path):** the over-temperature *actuation chain* — IGBT baseplate NTC → firmware detection → `OvertemperatureInverter` FAULT → immediate gate cut — is already demonstrated in-circuit while switching, at full phase current, by [OV-TEST-HW-THERMAL-OTP-200A-GEN7-SIZE2](../Thermal-OTP-200A-Gen7-Size2/Index.md) (test 14) and [OV-TEST-HW-REGEN-450A-GEN7-SIZE2](../Low-Power-Regen-450A-Gen7-Size2/Index.md) (test 16). Those reports are claimed as the actuation artifact in [OV-TEST-COVERAGE](../../Test-Coverage-Checklist/Index.md). This run therefore uses **no power switching and does not re-verify actuation under load**; external heat exists only to reach the temperatures and channels power testing cannot reach without damaging the DUT — the 90 °C derate region (tripped straight through it), the 105 °C capacitor-channel SSO (cap bank peaked at ~63 °C in the power runs), and the 100 °C module hard cap.

## Purpose & safety traceability

Validates safety goal **SG-07 (ASIL B, hazard H-07)** via **FSR-08**, whose quantified budgets this test verifies against the firmware under test:

- Two IGBT NTCs with **1oo2 voting**, plus one DC-link capacitor NTC, form the temperature chain.
- **Derate at 90 °C** — a logged derating action, not a shutdown.
- **SSO (safe state off) at 105 °C on the capacitor channel** — the capacitor rating limit; SSO entry must be immediate and latched.
- **100 °C hard cap on the module-sited IGBT NTC** (per the thermal design document); thresholds are stored in ECC configuration and must match read-back.

This test **complements and reconciles** earlier evidence: firmware builds under tests 14/16 ([OV-TEST-HW-THERMAL-OTP-200A-GEN7-SIZE2](../Thermal-OTP-200A-Gen7-Size2/Index.md), [OV-TEST-HW-REGEN-450A-GEN7-SIZE2](../Low-Power-Regen-450A-Gen7-Size2/Index.md)) tripped at **~80 °C** on the baseplate channel — behavior consistent with the old 80 °C OTP threshold but not with the FSR-08 threshold set above. This run establishes which thresholds the current firmware actually implements.

**Blocked-on-firmware caveat:** the FSR-08 1oo2 IGBT temperature voter is marked "Planned / not yet implemented (Phase 2)" in OV-SAF-HARA-CORE. If the firmware under test does not implement the voter (or implements different threshold values), the affected items are recorded as **blocked, not failed**, with the measured values filed for ratification against FSR-08.

## Scope

- **DUT:** Gen7 control module + C2 power stage, [FILL: DUT variant — hardware revision, thermal interface state (paste lot/thickness or "dry"), firmware graph + hash].
- **Coverage:** the chassis/bus-class variants of the methodology variant matrix ([OV-TEST-METHODOLOGY](../../Test-Methodology/Index.md) §6); execution-specific parameters are placeholders pending campaign definition — [FILL: per-channel configured thresholds from ECC read-back].
- **Out of scope:** power-run thermal characterization (covered by the power/thermal hold series), **SSO actuation under load (covered by tests 14/16, claimed in OV-TEST-COVERAGE — this run does not rehearse it)**, NTC accuracy correlation (T-01 through T-03 in OV-TEST-THERMAL-PLAN), and any endurance claim — this test validates protection thresholds only.

## Bench setup & preconditions

Per methodology §1, adapted for a no-power-conversion protection run:

- **DUT** powered on the bench at low voltage (control and telemetry alive; no gate switching, no machine required). Firmware graph + hash logged.
- **Heating fixture:** [FILL: heating fixture — hot plate / controlled heat source, mounting, and insulation of the baseplate], with local heating capacity at each NTC sensing point (module-sited IGBT NTC, capacitor can NTC) so channels can be swept independently.
- **Reference probes:** calibrated probes co-located with each NTC sensing point (P-IGBT at the module NTC area, P-CAP at the capacitor can top), logged time-synchronized with telemetry; absolute accuracy ±1–2 °C is sufficient.
- **Thermal supervision:** TI250-class imager per the thermal plan, watching the DUT throughout the sweep.
- **Preconditions:** all NTC telemetry channels agree with their co-located reference probes within ±3 °C at ambient before heating starts (methodology CLM-5 correlation); the operator confirms which thresholds the firmware build implements (ECC read-back) before asserting pass/fail.

**Safety notes:** the baseplate and heating fixture run at burn-hazard temperatures (target 105 °C+ at the sensing point) — hot-surface gloves, guarded fixture, no unattended operation, and an independent over-temperature cutout on the heat source. If the DUT is bus-powered for any segment, treat the DC link as hazardous energy: [FILL: 200 V vs 450 V class — discharge and verify <50 V before touching the assembly]. The imager pass is the personnel-safe alternative to touch checks.

## Procedure

1. Power up the DUT, start telemetry logging (all NTC channels, derate state, fault/SSO status), and log the firmware graph + hash. Read back every per-channel threshold from ECC configuration and record it.
2. Verify at ambient: each firmware NTC channel reads within ±3 °C of its co-located reference probe. Capture this as the baseline.
3. Mount the DUT on the heating fixture; confirm probe placement and imager framing; record ambient.
4. Ramp the IGBT NTC channel(s) through the configured 90 °C derate point in controlled steps, dwelling at each step until locally steady (per the methodology §2 steady-state definition, |dT/dt| ≤ 0.1 °C over any 5-minute window, applied at the sensing point). **Expect a logged derate action at 90 °C** — capture the exact temperature at derate entry, the derate flag/state word, and the telemetry frame.
5. Continue the capacitor-channel ramp through 90 °C toward 105 °C. **Expect SSO at 105 °C with the flag word** — capture the flag word, gate/PWM status, trip temperature (reference probe + firmware channel), and time-from-threshold-to-SSO. SSO entry must be immediate (no torque ramp-down behavior) and latched.
6. On the module-sited IGBT NTC, verify behavior at the 100 °C hard cap: record whether it derates, trips, or logs anything, and reconcile against the design claim.
7. Verify the threshold values read back from the firmware match the ECC configuration recorded in step 1; note any discrepancy explicitly.
8. Cool below the thresholds (controlled down-ramp or natural cooldown) and **characterize hysteresis if any**: record the recovery/reset temperature and behavior, and re-cross each threshold downward if recovery does not occur, to bound any hysteresis band.
9. Repeat steps 4–8 on the second IGBT NTC channel. Exercise the 1oo2 voter if implemented (fault one channel; the voter should act on the remaining channel) — if the voter is not implemented in this build, record the affected items as **blocked, not failed**, per the caveat above.
10. Log ≥ 5 min of cooldown telemetry after the final threshold event; capture the imager pass at the highest point reached.

## Measurements & acceptance criteria

| # | Criterion | Pass condition |
|---|-----------|----------------|
| 1 | Derate entry (IGBT channels) | Derating action logged at **90 ±3 °C** on the IGBT channels (reference-probe temperature at entry) |
| 2 | SSO entry (capacitor channel) | SSO at **105 ±3 °C** on the capacitor channel, immediate and latched, with flag word captured. If the firmware thresholds differ from FSR-08, the test **records the measured values and files a discrepancy against FSR-08 for ratification** rather than asserting a fail |
| 3 | Module-sited IGBT NTC | 100 °C hard-cap behavior recorded and reconciled against the design claim; deviation filed if behavior differs |
| 4 | ECC consistency | All per-channel threshold values read back from firmware match the ECC configuration (exact match; no undocumented offsets) |
| 5 | Probe correlation | Firmware NTC channels agree with co-located reference probes within ±3 °C at every recorded crossing point (methodology CLM-5) |
| 6 | Voter status | 1oo2 voter behavior documented as **implemented** (with trip-on-single-channel evidence) or **blocked** (not implemented in this build) — either is an acceptable recorded outcome; undocumented is not |

## Evidence package

Per methodology §5 and the evidence framework of OV-TEST-FAULT-INJECTION:

- Sibling **Test Report** with sections: Test setup, Test conditions (table), Procedure, Electrical results, Thermal results, Telemetry overview, Observations, Conclusion, Artifacts.
- Conditions table: hardware + firmware hash, DUT variant and thermal interface state, heating fixture, per-channel configured thresholds (ECC read-back), ambient (recorded, or *inferred* per methodology), measured event temperatures.
- **Telemetry overview plot**, standard 5-panel layout (Iq; DC-link power; machine-terminal P and Q; baseplate NTCs with ambient reference; bus voltage) — for this no-power-conversion run the power panels may be empty; the NTC panel carries the evidence, annotated with event markers at each threshold crossing.
- Full-rate session log + 1 Hz decimated log, decimated log linked in the Telemetry Viewer; reference-probe logger export time-synchronized with the telemetry log.
- Photos: bench and fixture setup, probe placement at each sensing point, imager pass at the highest temperature, and the threshold crossings as displayed in telemetry.

## Execution record

To be filed as a sibling Test Report under `Docs/Safety-and-Compliance/Testing/Hardware/` referencing this plan (OV-TEST-HW-THERMAL-FSR08-THRESHOLDS) by doc_id; test ID assigned at execution.
