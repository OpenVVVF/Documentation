---
doctype: Test Plan
doc_id: OV-TEST-COVERAGE
title: HARA Test Coverage Checklist
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.8"
date: "2026-09-27"
description: Maps every HARA safety goal (OV-SAF-HARA-CORE v5.10, motorcycle profile v1.8) to its validation evidence and gaps. Completed power/thermal tests (7–19) are indexed by safety goal; every remaining gap names the required test and, where a plan stub exists, its doc_id. The working checklist for deciding what to test next.
nav_order: 381
normative_refs:
  - OV-TEST-INDEX
  - OV-TEST-METHODOLOGY
  - OV-SAF-HARA-CORE
  - OV-SAF-HARA-PROF-MOTO
  - OV-TEST-FAULT-INJECTION
  - OV-TEST-THERMAL-PLAN
placeholder: true
---

# HARA Test Coverage Checklist

Status of each safety goal in [OV-SAF-HARA-CORE](../../HARA/Core/Index.md) v5.10 (motorcycle profile [OV-SAF-HARA-PROF-MOTO](../../HARA/Application-Profiles/Motorcycle/Index.md) v1.8 ASIL targets) against the completed hardware tests (test IDs 7–19) and the fault-injection / thermal plans. Methods referenced throughout are defined in [OV-TEST-METHODOLOGY](../Test-Methodology/Index.md).

**Statuses:** ✅ covered · ◐ partial evidence · ○ open · ⛔ blocked on unimplemented firmware.

**SG numbering note:** H-11/SG-11 were removed in HARA v5.4 (HV contactor is BMS/OEM domain); goals run SG-01…SG-10, SG-12…SG-15.

## Coverage matrix

| SG | ASIL | Mechanisms (FSRs) | Existing evidence | Status | Required action |
|----|------|-------------------|-------------------|--------|-----------------|
| SG-01 Unintended positive torque | D | FSR-01 dual throttle 1oo2 (>5 % → SSO), FSR-18 limit switch <50 ms, FSR-03 rate limit 500 Nm/s, FSR-02 plausibility, FSR-17 CAN heartbeat, FSR-19 boot CRC | None | ○ | Fault-injection campaign C-01–C-06, C-13, C-14, C-20, C-23–C-25, C-39, C-41, S-01/S-02, I-01–I-03, I-06–I-08, I-11, I-15–I-17 (per [OV-TEST-FAULT-INJECTION](../Fault-Injection-Test-Plan/Index.md)). ⛔ Several FSRs still Planned (below) |
| SG-02 Unintended reverse torque | B | FSR-04 reverse interlock (>100 rpm → clamp) | None | ⛔ | FSR-04 firmware Planned → implement, then FI tests S-02, S-14, C-13, I-13 |
| SG-03 Loss of torque → safe state ≤200 ms | C | FSR-05: six SSO pathways (TIM1_BKIN <100 ns; 1oo2 power kill ~10 µs; rail-loss passive; GATE_DRIVE_RESET <1 µs; watchdog ~100 ms; coprocessor trigger <10 µs) | ◐ OTP trips (tests 14, 16) via firmware FAULT state. **Test 20** (2026-09-26, [report](../Hardware/SSO-Latency-Gen7-Size2/Index.md)): gate-driver fault → SSO ≤10 ms telemetry-bound; ADC watchdog (TIM1_BKIN) → SSO with ISR-immediate break, bounded 30.3 A, correct flags, re-enable blocked. **Test 21** (2026-09-26, [report](../Hardware/SSO-GateKill-Gen7-Size2/Index.md)): Path 2a gate-power kill and Path 4 GATE_DRIVE_RESET exercised through the real enable/reset lines — as-found empty flag word, fixed (gate-loss + TorqueLoss detectors), retested to pass with single-bit flags in ≤0.3 s; 4 of 6 pathways now have low-bus evidence | ◐ | Still open: Path 2b + Paths 5/6 (coprocessor firmware in progress), Path 3 3.3 V rail (needs rig) per [OV-TEST-HW-SSO-LATENCY](../Hardware/SSO-Latency/Index.md); then FI C-13/C-14/C-22, S-03/S-04, S-10–S-13, S-16–S-19 |
| SG-04 Loss of regen detection | A | Monitoring + CAN indication (GAP-TEST-01: no dedicated test exists) | None — regen runs prove regen works, not its loss | ○ | [OV-TEST-HW-LOSS-OF-REGEN](../Hardware/Loss-Of-Regen/Index.md) stub |
| SG-05 Unintended regen → safe state | C | FSR-06 uncommanded-regen monitor | None | ⛔ | FSR-06 firmware Planned → implement, then FI S-05, S-08, S-17, I-14 |
| SG-06 Over-torque limit (>110 % → SSO <100 ms) | C | FSR-07 torque-limit LUT cross-check; analog watchdog OCP **10 µs**; DESAT <2 µs | ◐ Tests 15/16 show clean commanded current to 470 A (no false trips). **Test 22** (2026-09-26, [report](../Hardware/Overcurrent-Watchdog-55A-Gen7-Size2/Index.md)): over-torque chain implemented fix-forward (calibrated `Motor.MaxTorqueCurrentA`, 110 % monitor with ISR break + derived AWD backstop) — trip at 55.0 A vs 50 A max, repeatable 3×, SSO ≈0.6 ms, latched flags, clean recovery, locked rotor at 49 V; main-MCU element done, coproc dual-MCU element open | ◐ | Coprocessor dual-MCU half of FSR-07 (colleague's firmware); ratify production calibrated max from power series then re-set config; FI C-06/C-07/C-41, S-09, S-15; DESAT <2 µs via [OV-TEST-HW-DESAT-SHORT](../Hardware/Desat-Short-Circuit/Index.md) |
| SG-07 Over-temperature derate + safe state | B | FSR-08: 2 IGBT NTC 1oo2 + 1 cap NTC; **derate 90 °C; SSO 105 °C cap channel**; 100 °C IGBT-module hard cap; thresholds in ECC | ◐ **Actuation chain proven in-circuit** by tests 14/16 (IGBT baseplate NTC → FAULT `0x04000000` (`OvertemperatureInverter`) → immediate gate cut at full phase current — claimed as actuation evidence). Tests 12, 13, 17–19: steady-state thermal data below derate. Caveats: trip was ~80 °C on the IGBT channel (≠ FSR-08 thresholds), latency never measured, derate never crossed, cap channel never heated | ○ | Actuation artifact: **claimed from tests 14/16** (no reheating needed). Remaining: [OV-TEST-HW-THERMAL-FSR08-THRESHOLDS](../Hardware/Thermal-FSR08-Thresholds/Index.md) stub — externally heated run for the 90 °C derate, 105 °C cap-channel SSO, 100 °C module cap, ECC read-back, and ~80 °C reconciliation (per Thermal plan T-06). ⛔ 1oo2 voter Planned |
| SG-08 Rotor feedback loss → safe state <100 ms | C | FSR-09 encoder-loss detection (<50 ms target per LIMIT-04) | **Test 23** (2026-09-26, [report](../Hardware/Encoder-Loss-Gen7-Size2/Index.md)): hard sin/cos disconnect at −2190 RPM → SSO in µs–10 ms via all-channel AWD (ISR break), encoder flag latched, blocked re-enable; as-found blind-start defect fixed (start refusal on invalid feedback) + Critical EncoderLoss chain (bit 33) for in-window degradation; TorqueLoss net validated live | ◐ | FI C-09, C-28–C-30 (partial/degraded feedback); amplitude-collapse debounce (~250 ms) tightening for the 100 ms budget on that mode; optional scope-timed latency capture |
| SG-09 HV isolation >500 Ω/V | A | HVIL <50 ms (FSR-10); >5 kVrms reinforced per gate-driver channel | None | ○ | FI C-50 (1 kV applied-leakage method), I-04 — external-lab territory; bench keeps clear |
| SG-10 DC-link OV/UV | B | FSR-11 isolated ADC bus monitor; OV → regen disable; critical OV → SSO <50 ms; FSR-21 UV (thresholds undefined) | **Test 24** (2026-09-26, [report](../Hardware/DCLink-OVUV-Gen7-Size2/Index.md)): all four transitions validated at 49 V by threshold injection — OV warning regen-disable + UV derate implemented fix-forward (bits 34/35), critical OV/UV comparator path SSO ≪50 ms, candidate FSR-21 thresholds recorded (derate 40 V, critical 30 V); 450 V-class + bus dynamics open | ◐ | 450 V-class execution with bus controller (load-bank ramp, OV overshoot/UV ride-through vs link capacitance); FSR-21 ratification of candidate thresholds |
| SG-12 Shoot-through prevention <10 µs | C | FSR-12 complementary inputs (no ASIL credit); FSR-13 DESAT 6.5 V <2 µs, soft turn-off, Miller clamp, UVLO 12.2/11.3 V | **Test 25** (2026-09-27, [report](../Hardware/Desat-Short-Circuit-Gen7-Size2/Index.md)): full-duty winding pulses at 50/100 V — 50 V ≥800 A no DESAT (below 6.5 V knee, negative bound); 100 V 2/5 ms → driver /FLT; hardware BKIN path proven (MOE drop + BIF at hardware speed) after fixing missing BIE/NVIC plumbing; soft turn-off/Miller/UVLO and scope-measured figures open | ◐ | Scope-measured <2 µs/<10 µs, soft turn-off + Miller clamp + UVLO 12.2/11.3 V characterization; bolted-short µs-regime fixture; FI C-15–C-17, C-26, C-27, C-31–C-34 |
| SG-13 Safe state ≤200 ms, independent of control loop | D | Six SSO pathways; FSR-14 breakpoint <10 µs; FSR-15 watchdog ≤50 ms + challenge/response; FSR-16 POST; FSR-19 boot CRC; FSR-22 codegen FFI | ◐ Same OTP-trip note as SG-03. **Test 20** (2026-09-26, [report](../Hardware/SSO-Latency-Gen7-Size2/Index.md)): ADC-watchdog SSO asserts the TIM1 break in the watchdog ISR, independent of the main control loop; gate-driver fault path SSO ≤10 ms telemetry-bound. **Test 21** (2026-09-26, [report](../Hardware/SSO-GateKill-Gen7-Size2/Index.md)): gate-power kill + reset assertion detected via supervisor-independent observables (/RDY pin, torque-loss signature) with latched single-bit flags; control loop cannot prevent the safe state (both cuts are passive at the gate end) | ◐ | Coprocessor independence paths (5/6, FSR-15 challenge/response) still open per [OV-TEST-HW-SSO-LATENCY](../Hardware/SSO-Latency/Index.md); then FI C-13–C-17, C-19–C-25, C-43, S-01–S-03, S-10–S-12, I-04. ⛔ FSR-16/19/22 incomplete |
| SG-14 Gate-driver fault (DESAT/UVLO/TSD) → safe state | C | OR'd FLT to both MCUs (TIM1_BKIN + coprocessor GPIO cross-check) | **Test 25** (2026-09-27, [report](../Hardware/Desat-Short-Circuit-Gen7-Size2/Index.md)): as-found FLT→main-MCU chain fully blind (BIE + NVIC never enabled, no GPIO poll) despite a correctly wired BKIN path; fixed — latched Critical PwmBreak `0x00000002` + SSO on real 100 V DESAT events, recovery verified; coproc FLT path open (colleague) | ◐ | Coprocessor /FLT cross-check (colleague's firmware); FI C-15–C-17, C-26, C-27, C-31–C-34 |
| SG-15 Deadtime / stuck-on detection >100 µs → safe state | C | Coprocessor PWM-pair monitor; FSR-20 ECC (mapped here in Core Table 8) | None | ○ | FI C-15, C-16, C-49 (coprocessor bench); no dedicated hardware stub yet |

## Chassis-variant coverage

Continuous-duty thermal validation exists only for the **200 V class** (tests 17–19; variant matrix in OV-TEST-METHODOLOGY §6). The **450 V class** column is empty: [OV-TEST-HW-STEADY-STATE-450V](../Hardware/Steady-State-450V/Index.md) is the fill-in stub for the equivalent staircase/hold campaign. Ceiling/floor variants (voltage, temperature, switching frequency) are reserved per the methodology scope note.

## Firmware implementation gaps blocking test (FSRs not implemented)

These cannot be *verified* until implemented; they are the gating items for the ⛔ rows above.

| FSR | Item | Status |
|-----|------|--------|
| FSR-02 | Command-vs-measured current plausibility (>20 % / >100 ms) | Planned |
| FSR-04 | Reverse interlock (>100 rpm clamp) | Planned |
| FSR-06 | Uncommanded-regen monitor | Planned |
| FSR-08 voter | 1oo2 temperature voting | Planned |
| FSR-16 | POST before PWM enable | Partial |
| FSR-17 | CAN safe defaults on heartbeat loss | Planned |
| FSR-19 | Boot CRC-32 (GAP-SW-01, P1) | To implement |
| FSR-21 | UV thresholds (SG-10) | Planned |
| FSR-22 | Generated-code fault cases (GAP-SW-04, P1) | Planned |

## Other explicit HARA open items (not bench stubs)

- **DFA (LIMIT-08, P0)** — no dependent-failure analysis; blocks any ASIL D claim on SG-01/SG-13.
- **LIMIT-01 / H-03a** — track characterization of abrupt torque-loss controllability (accepted residual risk).
- **EMC pre-compliance (LIMIT-09, P1)** — CISPR 25 pre-scan; E-08/E-09 external lab.
- **E-series environmental type tests (E-01…E-12)** — deferred; vibration/shock/thermal-soak/humidity/ESD/ingress (see [Vibration Test Plan](../Vibration-Test-Plan/Index.md) and [Thermal Test Plan](../Thermal-Test-Plan/Index.md)).
- **Hardware architectural metrics** — no FMEDA/SPFM/LFM yet; decomposition remains design-stage.
- **FI plan v1.1 execution** — all 80 C/S/I tests Defined, none Executed; this checklist's stub column is the hardware-executable priority subset.

## How to use this checklist

1. Pick the highest-ASIL open row with an unblocked mechanism (SG-13/SG-03 SSO latency is the natural next hardware test).
2. Open the referenced stub (or FI-plan entry), fill the `[FILL]` execution parameters for the chassis variant under test (200 V / 450 V), run per [OV-TEST-METHODOLOGY](../Test-Methodology/Index.md).
3. Execute, file the dated Test Report as a sibling of the stub, link it here and in the [test evidence dashboard](../Index.md), and flip the row status.
4. A row may only be marked ✅ when the quantified budget in its mechanisms column is demonstrated in the report (e.g. SSO ≤200 ms measured, not assumed).
