---
doctype: Test Report
doc_id: OV-TEST-HW-ENCODER-LOSS-GEN7-SIZE2
title: Rotor Feedback Loss Detection — Gen7 Size 2, Low Bus
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-09-26"
description: First execution of the SG-08 encoder-loss plan on Gen7 size 2 at 49 V — hard disconnects reach SSO in microseconds via the all-channel ADC watchdog; fix-forward added start refusal on invalid feedback and a Critical EncoderLoss chain for in-window degradation; layered detection validated stationary and at speed.
test_id: 23
nav_order: 393
normative_refs:
  - OV-TEST-HW-ENCODER-LOSS
  - OV-TEST-METHODOLOGY
  - OV-TEST-COVERAGE
  - OV-TEST-FAULT-INJECTION
---

# Rotor Feedback Loss Detection — Gen7 Size 2, Low Bus

This report documents the first execution of [OV-TEST-HW-ENCODER-LOSS](../Encoder-Loss/Index.md) on the Gen7 size 2 assembly at 49.3 V, injecting **hard loss of the sin/cos rotor-feedback channel** by physically disconnecting the encoder connector mid-run (manual-injection convention per OV-TEST-FAULT-INJECTION). This build has no digital A/B feedback channel; the break opens the full sin/cos pair.

Fix-forward applied, as in the rest of this campaign: the as-found state had two defects — **`control start` accepted with the encoder physically disconnected** (driving blind until an unrelated safety net tripped), and encoder-loss detection existed at **warning severity only** (no dedicated Critical chain). Both were corrected in firmware (commit `ef8cd17`) and retested on the same bench. As-found and as-left behavior are both recorded.

## Test setup

- **DUT:** OpenVVVF Gen7 control module + C2 power stage, 200 V class variant.
- **Firmware:** RTE generated build, graph `foc_demo`, hash `bd5390d76c425eb1` (82 nodes), verified after flash. Base for as-found runs: `0d6d9d9`; detection fix: **`ef8cd17`** (branch `coproc-flash-fixes`).
- **Machine / load:** Zero ZF75-10 PMSM, coupled, unloaded, free-spinning. **Bus:** 49.3 V current-limited bench supply.
- **Injection:** manual disconnect/reconnect of the encoder connector at the harness (opens both sin and cos; no break switch fitted).
- **Instrumentation:** RTE Studio telemetry (~132 Hz), device console (fault transcripts), firmware 5 kHz spike recorder. No scope this execution — per the campaign's text-evidence convention; the fast-path timing rests on the established ISR-break mechanism (tests 20–22) rather than scope cursors.

## Test conditions

| Run | State at injection | Injection | Result (flag word) | Outcome |
|-----|--------------------|-----------|--------------------|---------|
| 1 (as found) | Standstill, RUNNING, IqVar 0 | encoder disconnect | `0x00402000` (AdcWatchdog + EncoderOutOfRange[W]) | SSO via AWD; latched; blocked re-enable |
| 2 (as found) | **IDLE, encoder disconnected** | `control start` | — | **DEFECT: start accepted**, drove blind; TorqueLoss net tripped (`0x80002000`) |
| 3 (as found) | −13.3 A, −2190 RPM | encoder disconnect | `0x00402000` | SSO via AWD in the ISR; coast-down |
| 4 (as left) | IDLE, encoder disconnected | `control start`, `foc start 5` | — (warning only) | **Both refused**, no outputs, no state change |
| 5 (as left) | −14.1 A, −2083 RPM, 35 s | none (regression) | `0x00000000` | zero false EncoderLoss/TorqueLoss trips |
| 6 (as left) | −15 A, at speed | encoder disconnect | `0x00402000` | SSO via AWD (expected — see layering) |
| 7 (as left) | IDLE | `fault test EncoderLoss` | bit 33 set/cleared by name | synthetic source path verified |
| 8 (as left) | regression | `hwocset 8`+−40 A; `gatepwr 0` | `0x00400000` AdcWatchdog-only; `0x00000001` GateDriver-only | no detector cross-talk; clean recovery |

## Procedure

1. **Stationary pull (run 1):** control running at IqVar 0 (0 RPM); encoder disconnected. Recorded flags, console transcript, post state.
2. **Blind-start discovery (run 2):** with the encoder still out, `control start` was issued — and **accepted**. The drive ran with invalid angle; measured iq ≈ 0 with vq at the voltage rail until the **TorqueLoss detector** (test 21) tripped Critical in its 150 ms debounce: `[FAULT][C][Gate Drive] TorqueLoss triggered: iq near zero with saturated vq request` → safety sequence. No current excursion; an unplanned but real validation of that net.
3. **At-speed pull (run 3):** −13.3 A at −2190 RPM; encoder disconnected. The ADC analog watchdog — armed on **all injected channels**, sin/cos included — tripped in the ISR on the sin/cos collapse → immediate TIM1 break → safety sequence → SSO; `EncoderOutOfRange` warning latched alongside.
4. **Fix-forward (commit `ef8cd17`):**
   - `EncoderADC::feedbackValid()` — valid bounds **and** live raw sin/cos off the rails **and** tracked amplitude; gates `ControlSupervisor::start()` and `FocControlManager::checkSensorReadiness()` **before any state change** (no PWM, no gate startup). Key insight: FRAM-restored learned bounds are *stale* evidence — a disconnected encoder leaves `valid=Y learned=Y` while sin/cos rail, which is how the old bounds check let the blind start through. The gate uses the **live signal**, not the latched warning, so a re-plugged healthy encoder starts normally even with a stale warning latched.
   - **Critical escalation while actuating:** the debounced rail detector (~100 ms) and amplitude-collapse detector (~250 ms) now raise **`EncoderLoss` (bit 33, Critical)** → standard safety sequence, but only while control outputs are enabled; at IDLE the behavior stays warning-only (a disconnected bench encoder locks nothing out). The 100 ms rail debounce beats the 150 ms TorqueLoss debounce, so the encoder fault owns in-window encoder failures; TorqueLoss remains the net.
   - Open-loop V/Hz `start` / induction paths deliberately **not** gated: they are blind by design and do not consume encoder feedback for actuation.
5. **Retest (runs 4–8):** refusal verified with the encoder unplugged (both start paths); plugged-in regression 35 s at −15 A with zero false trips; second at-speed pull (same AWD-caught outcome — expected); synthetic `fault test/clear EncoderLoss`; AWD and gate-power-cut regression; clean recovery to IDLE with no faults.

## Electrical results

- **Hard disconnect → SSO:** on every pull (stationary and at −2190 RPM), the all-channel AWD asserted the TIM1 break in the ISR — the same hardware-async mechanism measured in tests 20–22 — with the 100 Hz safety sequence completing gate reset and power-off within one service cycle. Detection-to-SSO is therefore **microseconds to ≤10 ms**, far inside the ≤100 ms SG-08 budget and the <50 ms LIMIT-04 target. Post-injection: `pwm_moe` = 0, `control_outputs_enabled` = 0, `gate_ready` = 0, iq collapsed to ≈ 0 within the first post-event samples; no overcurrent, no gate re-firing (currents bounded at the pre-injection level, ≤ ~15 A, in all captures).
- **Flag identity:** hard disconnects latch `0x00402000` — AdcWatchdog (Critical, the actuating source) **plus** `EncoderOutOfRange` (bit 13, the encoder-chain identity) — an encoder-loss flag is set and latched on every injection, recorded here as FSR-09 evidence.
- **Re-enable:** all faulted runs refused `control start` before `fault clear` and restarted cleanly after; the disconnected-encoder start is now **refused by design** (run 4).
- **Layered detection (as-left, accepted design):**

  | Encoder failure mode | Caught by | Time to SSO |
  |---|---|---|
  | Hard disconnect (sin/cos out of window) | AWD → ISR break (+ EncoderOutOfRange latched) | µs–10 ms |
  | In-window rail sticking | `EncoderLoss` Critical (bit 33), ~100 ms debounce | ≤ ~110 ms |
  | In-window amplitude collapse (partial degradation — out of this plan's scope, FI-plan territory) | `EncoderLoss` Critical, ~250 ms debounce | ≤ ~260 ms |
  | Anything that slips all of the above | `TorqueLoss` net (bit 31) | ~150 ms |
  | Start attempted with invalid feedback | refused outright, no outputs | — |

  The AWD wins any hard-disconnect race by construction (ISR vs debounce); reconfiguring it narrower was considered and rejected — it would slow the SSO response purely for flag-word attribution and would disturb the tuned watchdog chain.
- **No false trips:** 35 s regression at −15 A plus all closing runs produced zero EncoderLoss/TorqueLoss activity with a healthy encoder; AWD and gate-cut paths unaffected (`0x00400000` / `0x00000001`, sole sources).

## Thermal results

Not applicable — short runs at ≤ 15 A; no meaningful temperature rise.

## Telemetry overview

Exported telemetry windows are filed as artifacts. Note on timing evidence: the 128 Hz telemetry buffer retains only ~20–30 s, so the exports capture the post-injection state and recovery rather than the trip instant; the trip timing rests on the console transcripts (immediate, in-order) and the established AWD ISR-break mechanism. The at-speed pull was performed twice with identical outcome.

## Observations

- **Defect found and fixed — blind start:** `control start` (and `foc start`) previously ran with the encoder physically disconnected. This is now a hard refusal: `[SUP] ERROR: encoder feedback invalid (bounds/raw sin/cos at rail or amplitude collapsed); refusing to drive blind`. This was the most safety-significant finding of the execution — it converted a latent single-point loss-of-control hazard into a start-time interlock plus two independent runtime layers.
- **Unplanned validation:** the TorqueLoss detector added in test 21 caught the blind start in ~150 ms with no current excursion — its first real (non-injected) catch.
- **Known reliability wart (not safety-gating, follow-up):** FRAM-restored learned encoder bounds can be stale after a disconnect/replug cycle — on one occasion the re-plugged encoder read against stale bounds and the drive misbehaved until reboot re-learned them (bounds after reboot: sin 11423–53864, cos 11346–53727, healthy). The live-raw refusal gate bounds the safety impact; a bounds re-validation/re-learn at plug-in or start is the suggested reliability follow-up, deferred as non-blocking.
- **Amplitude-collapse debounce (~250 ms)** exceeds the 100 ms budget for that specific partial-degradation mode; hard loss (this plan's scope) is covered at µs–110 ms. Tightening the amplitude path or covering it in the FI campaign (C-09, C-28–C-30) is left as a recorded note.
- **Deviation:** low bus (49.3 V) and voltage-limited operating point (−13 to −15 A at ~2100–2200 RPM) per the campaign's standing deviation; detection behavior is speed/current-independent. No dynamometer; machine unloaded.
- **Operator note:** immediate history exports after injection still missed the trip instant due to the short telemetry buffer — for future injections, arm a capture *before* the event (or use the 5 kHz spike recorder with an appropriate threshold) to get a measured rather than mechanism-bounded latency.

## Conclusion

**Pass (as left).** Loss of rotor feedback at operating speed drives the Gen7 size 2 to six-switch-open in microseconds-to-≤10 ms via the all-channel ADC watchdog, with the encoder-loss identity latched in the flag word, no overcurrent or gate re-firing during decay, and re-enable blocked until explicit clear. The two as-found defects — blind start acceptance and warning-only detection — are fixed: starts with invalid feedback are refused outright, and a Critical `EncoderLoss` chain (bit 33) covers in-window degradation while actuating, with the TorqueLoss net behind it. SG-08 main-MCU evidence is on record at low bus; remaining items are the FI-plan partial-degradation cases and an optional scope-timed latency capture.

## Artifacts

- [Run 3 — at-speed pull, post-event window (CSV)](sg8_atspeed_pull.csv)
- [Run 6 — second at-speed pull, post-event window (CSV)](sg8_atspeed_pull2_encloss.csv)
- [Run 8 — closing regression: AWD trip, gate cut, recovery (CSV)](sg8_closing_regression.csv)
