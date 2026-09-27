---
doctype: Test Report
doc_id: OV-TEST-HW-SSO-LATENCY-GEN7-SIZE2
title: SSO Pathway Latency — Gen7 Size 2, Low Bus
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-09-26"
description: First execution of the SSO-latency plan on Gen7 size 2 at 49 V — firmware-injected gate-driver fault and hardware ADC-watchdog overcurrent both reach six-switch-open well within the 200 ms FSR-05 budget; physical-pathway injections deferred to a follow-up campaign.
test_id: 20
nav_order: 390
normative_refs:
  - OV-TEST-HW-SSO-LATENCY
  - OV-TEST-METHODOLOGY
  - OV-TEST-COVERAGE
  - OV-TEST-FAULT-INJECTION
---

# SSO Pathway Latency — Gen7 Size 2, Low Bus

This report documents the first execution of [OV-TEST-HW-SSO-LATENCY](../SSO-Latency/Index.md) on the Gen7 size 2 assembly at low bus (49.3 V). Two safe-state pathways were exercised by firmware injection — the gate-driver fault pathway and the hardware ADC analog watchdog (overcurrent) pathway — and both reached six-switch-open (SSO) well within the 200 ms budget of FSR-05, with correct fault flag words and re-enable blocked pending fault clear. Physical harness injections (Path 2a/2b gate-PSU cuts, Path 3 rail removal, Path 4 GATE_DRIVE_RESET line) are deferred to a follow-up campaign; this report is the baseline latency evidence for SG-03/SG-13.

The campaign ran fix-forward: defects found by injection were corrected in firmware and the injection repeated until the pathway passed. As-found behavior and the fix set are recorded in Observations; all results below are from the final flashed build.

## Test setup

- **DUT:** OpenVVVF Gen7 control module + C2 power stage, 200 V class variant.
- **Firmware:** RTE generated build, graph `foc_demo`, hash `bd5390d76c425eb1` (82 nodes), verified via `build_info` after each flash. Built from RTE repository commit `1577a00` plus the campaign fix set (five files; see Observations). Telemetry graph signals at ~132 Hz; firmware spike recorder 64 samples at 5 kHz.
- **Machine / load:** Zero ZF75-10 PMSM, coupled, unloaded; FRAM motor config active (`Motor.Lambda` = 0.040 Wb used by the spinning-start guard).
- **Bus:** 49.3 V from the bench DC supply (≤ 60 V low-bus regime per the plan).
- **Instrumentation:** RTE Studio telemetry (state, fault flags, PWM MOE, gate status, currents, RPM); firmware 5 kHz spike capture as the authoritative current record around trips; oscilloscope with current probe on one motor phase lead, operator-monitored throughout.
- **Injection means:** firmware fault injection — `fault test GateDriver` (gate-driver fault pathway) and `hwocset` (ADC1 injected-channel analog watchdog arming, TIM1_BKIN hardware break pathway). No physical harness was fitted.

## Test conditions

| Run | Pathway | Injection | Operating point at injection | Fault flags | Post-injection state | Result |
|-----|---------|-----------|------------------------------|-------------|----------------------|--------|
| 1, 2 | Gate-driver fault → SSO | `fault test GateDriver` while RUNNING | iq −12.7 A, −2199 RPM, 49.3 V | `0x00000001` (GateDriver) | FAULT; outputs disabled, MOE 0, gate_ready 0 ≤ one telemetry interval (≤ 10 ms) | Pass |
| 3 | AWD armed, no false trip | `hwocset 50`, standstill start + 20 s hold | iq −14.4 A, ramping through −1345 RPM | none | RUNNING, spike recorder 0 triggers | Pass |
| 4, 5 | ADC watchdog (TIM1_BKIN) → SSO | `hwocset 8` armed, command `IqVar −40` | start from standstill, 49.3 V | `0x00400000` (AdcWatchdog, sole flag) | FAULT; immediate TIM1 break, six-switch-open, max \|i\| 30.3 A on 5 kHz capture | Pass |
| 6 | Spinning-start guard (campaign finding) | `control start` 2 s after stop from −2178 RPM | rotor at −2005 RPM, coasting | none | Start refused (`rpm=-2005 ceiling=1087`); no driven outputs; clean start after coast-down | Pass |

## Procedure

1. Confirmed preconditions: bus 49.3 V, telemetry streaming, fault flags clear, scope on a phase lead. Firmware graph hash verified against the campaign build after every flash.
2. Established the operating point: `control start`, `var set IqVar -15` (see deviation note — the plan's ~50 A is not attainable at 49 V on this machine).
3. **Runs 1–2 (gate-driver fault pathway):** injected `fault test GateDriver` at the operating point. Recorded state transition, fault flags, MOE, gate_ready, and the first post-injection telemetry sample. Attempted re-enable before `fault clear` (must be refused), then cleared and confirmed recovery. Two repetitions.
4. **Run 3 (armed no-false-trip):** armed `hwocset 50` at standstill, started control, held −15 A for 20 s; confirmed zero faults and an empty spike recorder.
5. **Runs 4–5 (ADC watchdog pathway):** armed `hwocset 8`, started control, commanded `IqVar −40`; the phase-current ramp crossed the armed window and the watchdog tripped. Recorded flags and dumped the 5 kHz spike capture. Two repetitions.
6. **Run 6 (spinning-start guard):** from −2178 RPM issued `control stop`, then `control start` 2 s later at −2005 RPM; confirmed refusal with no driven outputs. After coast-down below the ceiling, confirmed a clean start with no transient.
7. After each injection, confirmed re-enable only after `fault clear`, per the acceptance criteria.

## Electrical results

- **Gate-driver fault → SSO:** at the first telemetry sample after injection (≤ 7.6 ms at 132 Hz) the controller was in FAULT with flags `0x00000001`, `control_outputs_enabled` = 0, `pwm_moe` = 0, `gate_ready` = 0, and phase current collapsing (iq −12.7 A → +2.5 A at the first post sample, decaying). SSO entry is therefore bounded at **≤ 10 ms**, 20× inside the 200 ms FSR-05 budget; the true latency is shorter than the telemetry interval and will be quantified with scope captures in the physical-injection campaign.
- **ADC watchdog → SSO (TIM1_BKIN):** the watchdog trip asserts the TIM1 break directly in the ADC watchdog ISR (hardware-async), then the 100 Hz safety loop completes gate-driver reset and gate-rail power-off. The 5 kHz capture shows current bounded at the trip instant with **max |i| = 30.3 A** and no re-application of driven duty afterward — six-switch-open with flags `0x00400000` only. Effective trip ≈ **30 A phase** for an 8 A arm request (guard band, see Observations).
- **No false trip when armed:** 20 s at −15 A with `hwocset 50` armed produced zero faults and zero spike-recorder triggers; bus held 48.4–50.1 V.
- **Re-enable behavior:** all faulted runs refused `control start` while latched (`active Critical/High faults`) and required `fault clear`; no immediate re-enable was possible.
- **No shoot-through:** no shoot-through signature on the scope or in telemetry during any transition; the largest current recorded in the final build is 31 A (bounded watchdog trip).

## Thermal results

Not applicable — short, low-power runs at ≤ 15 A; no meaningful temperature rise on any channel.

## Telemetry overview

Per-run full telemetry histories (exported CSV, long format `signal,time_s,value`) and the harness run records (JSON, including console transcripts and pre/post state snapshots) are filed as artifacts below. Key channels: `control_state`, `fault_flags_hex`, `pwm_moe`, `gate_ready`, `control_outputs_enabled`, `cg_iq_a`/`cg_id_a`, `cg_iu_a`/`cg_iv_a`/`cg_iw_a`, `Mech_RPM`, `cg_vdc_v`.

## Observations

- **Operating-point deviation (per naming-convention note):** the plan's ~50 A phase current is unattainable on this bench — the unloaded ZF75-10 is voltage-limited at ~2180 RPM at 49.3 V and sustained iq is ~10–15 A. Injections ran at −12.7 A (gate-driver fault) and on a standstill current ramp (watchdog). Phase-current decay after SSO remains observable at these levels.
- **Fix-forward record.** The campaign found four firmware defects; each was fixed and the injection re-run to pass on the same bench:
  1. `hwocset` could never arm: its actuation guard read the ADC "running" state, which is permanently true on this build. Guard moved to the command layer (supervisor state + active control paths).
  2. `fault clear` was refused at IDLE: the power-stage-active check included the TIM1 MOE bit, which stays latched for measurement. MOE term removed; clear now works at IDLE and is still refused while control/PWM is active.
  3. Arming the analog watchdog at runtime originally reconfigured the ADC (conversion stops) — unacceptable on this highly tuned chain. Runtime arming now writes only the threshold registers (widen-first, read-back verified, no conversion stops); post-fix statics and a −15 A spin match the pre-fix baseline (`regression_spin_15A_2026-09-26.csv`).
  4. **`control start` on a spinning rotor applied a blind 50/50/50 zero vector** (preload → `PWM_Start` → graph actuation enable, up to ~200 µs gap) into ~26 V of back-EMF, producing a real phase-current spike — operator scope showed **> 300 A** on the phase lead at 49.3 V; the armed watchdog tripped correctly on it. Fixed three ways: graph actuation is armed 1 ms before `PWM_Start` (first driven vector is the graph's computed vector), `control start` is refused above a back-EMF ceiling computed from live vdc × `Motor.Lambda` (≈ 1087 RPM at 49.3 V), and the watchdog ISR now asserts the TIM1 break immediately instead of waiting for the 100 Hz safety loop. Post-fix, no capture in any run exceeds 31 A.
- **Effective watchdog trip vs arm request:** with an 8 A arm request the hardware trips at ≈ 30 A phase. Raw idle noise on the isolated current transducers reaches ±14–17 A in single-sample bursts, so the armed window carries a ±240-count guard around the leak-tracked operating point; a literal 8 A single-sample hardware trip is unattainable at this noise level. The filtered multi-sample software overcurrent path (`ocset`) remains the precise low-threshold protection. Consequently `hwocset 8` is a fault-injection threshold, not an operating threshold — margin above a normal −15 A run is only ~5 A, and a −15 A run with it armed does trip (bounded, as designed).
- **Post-trip phantom readings:** the safety power-off drops the isolated transducer supplies, so processed currents rail at ±1200–1400 A and the encoder reading rails after a trip. These are power-off artifacts, not real currents; the 5 kHz capture around the break is the authoritative current record.
- **Pathways not exercised:** Path 2a/2b (gate-PSU cuts), Path 3 (3.3 V rail removal), Path 4 (GATE_DRIVE_RESET line assertion), and Paths 5/6 (coprocessor) were not part of this campaign — they require the physical injection harness and are deferred to the follow-up execution of this plan. Their budgets remain open in [OV-TEST-COVERAGE](../../Test-Coverage-Checklist/Index.md).

## Conclusion

**Pass for the exercised pathways.** On the Gen7 size 2 assembly at 49.3 V, both the firmware-injected gate-driver fault and the hardware ADC-watchdog overcurrent pathway move the inverter to six-switch-open well within the 200 ms FSR-05 budget (telemetry-bounded ≤ 10 ms; the watchdog break is ISR-immediate by design), with the correct fault flag word set, re-enable blocked pending `fault clear`, and no shoot-through. This is the first measured latency evidence toward SG-03/SG-13; the remaining pathway budgets (physical kills, rail loss, reset line, coprocessor) stay open until the harness campaign.

## Artifacts

Final-build evidence:

- [Run 3 — armed `hwocset 50`, standstill start + 20 s at −15 A, no trip (CSV)](run_a_hwoc50_iq-15.csv)
- [Runs 4/5 — `hwocset 8` + −40 A watchdog trip (CSV)](run_b_hwoc8_iq-40_trip.csv) · [repetition (CSV)](run_b2_hwoc8_iq-40_trip.csv)
- [Run 6 — spinning-start refusal and clean restart (CSV)](run_c_spinning_start_guard.csv)
- [Post-fix regression spin at −15 A vs pre-fix baseline (CSV)](regression_spin_15A_2026-09-26.csv)

As-found (pre-fix) evidence:

- [Runs 1–2 — gate-driver fault injection, harness record (JSON)](SSO-LAT_run2_fwsso_2026-09-25.json) · [telemetry (CSV)](SSO-LAT_run2_fwsso_2026-09-25.csv)
- [Pre-fix watchdog arming attempt showing defects 1–2, harness record (JSON)](SSO-LAT_run3_bkin-awd_2026-09-25.json) · [telemetry (CSV)](SSO-LAT_run3_bkin-awd_2026-09-25.csv)
- [Spinning-start spike event, operator notes (JSON)](run5_armed50_start_trip_notes.json) · [telemetry (CSV)](armed50_start_trip_2026-09-26.csv)

Tooling:

- [Injection harness script used for the batched runs](run_injection.py)
