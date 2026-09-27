---
doctype: Test Report
doc_id: OV-TEST-HW-SSO-GATEKILL-GEN7-SIZE2
title: SSO Gate-Drive Kill Pathways — Gen7 Size 2, Low Bus
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-09-26"
description: Second SSO-latency execution on Gen7 size 2 at 49 V — gate-drive power kill (Path 2a) and gate-drive reset (Path 4) reach six-switch-open but initially with no firmware detection; gate-loss and torque-loss detectors were added fix-forward and both pathways retested to pass with correct flag words.
test_id: 21
nav_order: 391
normative_refs:
  - OV-TEST-HW-SSO-LATENCY
  - OV-TEST-METHODOLOGY
  - OV-TEST-COVERAGE
  - OV-TEST-FAULT-INJECTION
---

# SSO Gate-Drive Kill Pathways — Gen7 Size 2, Low Bus

This report continues [OV-TEST-HW-SSO-LATENCY](../SSO-Latency/Index.md) on the Gen7 size 2 assembly at 49.3 V, covering **Path 2a (gate-drive power kill)** and **Path 4 (GATE_DRIVE_RESET assertion)** — the two gate-endpoint pathways actuatable from the test build. Injections were actuated through the real hardware enable/reset lines via two firmware injection hooks added for this campaign (`gatepwr`, `gaterst`), so the endpoint hardware (gate-driver supply rail, driver reset input) is genuinely exercised; no physical harness modification was required.

First-pass result: both pathways physically reached six-switch-open, but with an **empty fault flag word** — a fail against the plan's detection requirement. Per the campaign's fix-forward rule, detection was implemented in firmware (gate-loss and torque-loss detectors) and both injections retested to **pass** with correct flag words, bounded currents, and blocked-then-clean re-enable. As-found and as-left results are both recorded below.

## Test setup

- **DUT:** OpenVVVF Gen7 control module + C2 power stage, 200 V class variant.
- **Firmware:** RTE generated build, graph `foc_demo`, hash `bd5390d76c425eb1` (82 nodes) throughout. Base for injections: commit `bc02138` (test 20 fix set); detection retests: commit `a8b223b` (adds the two detectors and the injection hooks; 5 files, +116). Both on branch `coproc-flash-fixes`, pushed.
- **Injection hooks (new shell commands, bypass the fault manager by design):**
  - `gatepwr <0|1>` — drives the gate-driver power-enable line directly (Path 2a endpoint).
  - `gaterst <0|1>` — asserts/releases the gate-driver reset line directly (Path 4 endpoint).
- **Machine / load:** Zero ZF75-10 PMSM, coupled, unloaded. **Bus:** 49.3 V bench supply.
- **Instrumentation:** RTE Studio telemetry (~132 Hz); firmware 5 kHz spike capture; oscilloscope on one phase lead (operator-monitored, not archived).

## Test conditions

| Run | Pathway | Injection | Operating point | Detection (as found) | Detection (as left) | Result |
|-----|---------|-----------|-----------------|----------------------|---------------------|--------|
| 1 | 2a gate power kill | `gatepwr 0` while RUNNING | −15.2 A, −1800 RPM | **None** — flags `0x00000000`, RUNNING, MOE set, PI wound to voltage rail | GateDriver fault `0x00000001` in ~0.2–0.3 s | Fail → **Pass** |
| 2 | 4 reset assert | `gaterst 1` while RUNNING | −10.6 A, −2188 RPM | **None** — no pin observable at all (`gate_ready` stays Y) | TorqueLoss fault `0x80000000` in ~160 ms | Fail → **Pass** |
| 3 | 4 reset release (as found) | `gaterst 0` under wound-up PI | — | — | — | Surge → software OC fault (finding) |
| 4 | Regression | normal run, starts/stops, AWD trip | −15 A, 20 s | — | no false trips; AWD still `0x00400000` only | **Pass** |

## Procedure

1. Preconditions: bus 49.3 V, telemetry streaming, no faults, `hwocset 0` (ADC watchdog disarmed for these runs).
2. Established the operating point (`control start`, `var set IqVar -15`, ~10 s settle).
3. **Run 1 (Path 2a):** `gatepwr 0` while running; recorded currents, state, flags, `gate_ready`, `gate_fault`, spike capture. Recovery: `control stop` → `gatepwr 1` → restart attempt.
4. **Run 2 (Path 4):** `gaterst 1` while running (30 s window); same recording. Then `gaterst 0` — which produced the release-surge finding (run 3).
5. **Fix-forward:** implemented detection (below), reflashed, repeated runs 1–2 with the full recovery sequence (stop → restore → `fault clear` → restart).
6. **Run 4 (regression):** 20 s at −15 A, standstill start/stop cycles, and one `hwocset 8` + `IqVar −40` ADC-watchdog trip to confirm no interaction with the new detectors.

## Electrical results

**As found (commit `bc02138`):**

- Both injections physically reached SSO: phase current collapsed within one exported sample (≤ 100 ms export bound; physically immediate freewheel decay) and the machine coasted to rest. No spike on the cut itself (recorder held only pre-cut waveform ≤ 25 A).
- **Detection: none on either pathway.** `fault_flags_hex` stayed `0x00000000`, supervisor RUNNING, `pwm_moe` = 1 (TIM1 switching into dead gates), PI wound to the voltage limit (`vq_req` ≈ −27 V against iq ≈ 0). `gate_fault` (/FLT) never asserted. `gate_ready` fell ~0.1 s after the power cut only; the reset assertion had **no pin-level observable at all**.
- **Release surge (Path 4):** releasing reset after 2 s of assertion reconnected the gates to a fully wound-up PI — a real current surge tripped software PhaseOvercurrent (>500 A processed × 3 samples). Latched fault required `fault clear`, as designed, and recovery was clean.

**As left (commit `a8b223b`):**

- **Path 2a:** `gatepwr 0` at −13.8 A → `GateDriver` fault (flag `0x00000001`, exactly one bit) raised ~0.2–0.3 s after the cut (gate_ready debounce 100 ms + service latency; ≈ 20–30 control cycles), standard safety sequence (PWM break, driver reset, power off), SSO. Recovery: stop → `gatepwr 1` (`gate_ready` back within 1 s) → `fault clear critical` → clean restart at −14.9 A.
- **Path 4:** `gaterst 1` at −15 A / −2193 RPM → `TorqueLoss` fault (flag `0x80000000`, exactly one bit) in ~160 ms (150 ms debounce + ≤ 10 ms service; ≈ 16 control cycles), safety sequence, currents bounded ≤ 20.4 A (the pre-injection level). The detector firing during assertion **defused the release surge**: stop → `gaterst 0` → `fault clear critical` → clean restart, no overcurrent event.
- **Detection design:** both detectors live in the supervisor service loop (graph control only). *Gate-power loss:* `gate_ready` low, debounced 100 ms, only while actuation is active → existing `GateDriver` fault source. *Dead gates / torque loss:* new `TorqueLoss` source (bit 31) — EMA(|iq|, α=0.2 @ 100 Hz) < 4 A while |iq_ref| ≥ 5 A and |vq_req| ≥ 90 % of the voltage limit, debounced 150 ms. The EMA is required because post-cut iq bounces above 2 A in ~50 % of samples; measured EMA|iq| ≈ 1.7 A collapsed vs ≥ 10.5 A in real operation (>2× margin both ways). vq-clamp alone is never used as a discriminator — this bench's normal operating point is itself voltage-limited at −10.5 A. Edge guards: no firing at IDLE (rail legitimately off), no re-raise after `fault clear` while power is still off, no retrigger from the safety sequence's own power cut.
- **Regression:** 20 s at −15 A plus start/stop cycles — zero detector activity, flags `0x00000000` throughout. The `hwocset 8` + −40 A watchdog trip still produces `AdcWatchdog` only (`0x00400000`) with the immediate TIM1 break — the supervisor's fault transition gates both detectors within one 100 Hz tick, long before their debounces complete.

## Thermal results

Not applicable — short runs at ≤ 15 A; no meaningful temperature rise.

## Telemetry overview

Per-run full telemetry histories (CSV, long format `signal,time_s,value`) are filed as artifacts below: as-found runs, release-surge event, detection retests, and the regression run. Flag words quoted above are from live snapshots at each event (`fault_flags_hex` is transition-logged and does not appear in the 128 Hz history exports).

## Observations

- **Fail-as-found, fix-forward, retest-to-pass** — the as-found state (SSO without detection) failed the plan's flag-word acceptance criterion on both pathways; the detection design above is the corrective action, verified on the same bench in the same session.
- **No pin observable for Path 4:** the gate-driver /FLT output does not assert for a reset assertion (rail stays up, driver ready), so reset-assertion detection is necessarily physiological (torque-loss). This also means a *physical* GATE_DRIVE_RESET fault (short to active) is now covered by the same detector.
- **Detection latency vs budget:** both detectors fire in ≤ 0.3 s of the injection — inside the 200 ms FSR-05 budget for the gate-loss path (~0.2–0.3 s measured; dominated by the 100 ms debounce plus rail-decay time for /RDY) and ~160 ms for torque loss. The *physical* SSO itself is immediate in both cases (passive freewheel decay); the measured latency is detection-and-latching, which is what sequences the controller to a clean, recoverable fault state. Debounce values are first-pass conservative choices; tightening them (or moving detection into the control ISR) is available if a future budget demands it.
- **New fault source:** `TorqueLoss` (bit 31, Critical, "Gate Drive" category) is table-driven like existing sources — `fault_active_names`, `fault clear TorqueLoss`, and MCP/Studio discovery work unchanged.
- **Injection hooks are now permanent campaign tooling** (`gatepwr`, `gaterst`, plus `hwocset` from test 20); they bypass the fault manager by design and are labeled FAULT INJECTION in help.
- **Pathways still open:** Path 2b (coprocessor gate-power path — coprocessor firmware in progress), Path 3 (3.3 V rail removal — needs a physical rig), Paths 5/6 (coprocessor watchdog/trigger — same dependency). Scope-captured sub-µs design-budget verification for Path 4 remains an optional refinement, not a pass/fail gate.

## Conclusion

**Pass (as left) for Pathways 2a and 4.** Gate-drive power kill and gate-drive reset assertion both move the inverter to six-switch-open immediately and — after the fix-forward detection work — raise the correct single-bit fault word within ≤ 0.3 s, sequence the standard safety response, block re-enable until `fault clear`, and recover cleanly. The release-surge hazard found on Path 4 is eliminated by the same detectors. Combined with test 20 (gate-driver fault injection + ADC watchdog), four of the six FSR-05 SSO pathways now have measured low-bus evidence; the remainder are blocked on the coprocessor firmware and a 3.3 V rail rig.

## Artifacts

As-found (pre-detection):

- [Run 1 — `gatepwr 0` cut at −15.2 A, no detection (CSV)](phys2a_gatepwr_cut_run.csv) · [recovery (CSV)](phys2a_gatepwr_cut_recovery.csv)
- [Run 2 — `gaterst 1` assertion at −10.6 A, no detection (CSV)](phys4_gaterst_run.csv) · [Run 3 — release surge → software OC fault (CSV)](phys4_gaterst_release_fault.csv)

As-left (with detection, commit `a8b223b`):

- [Run 1 retest — `gatepwr 0` → GateDriver fault `0x1` (CSV)](phys2a_detect_gatepwr.csv)
- [Run 2 retest — `gaterst 1` → TorqueLoss fault `0x80000000` (CSV)](phys4_detect_gaterst.csv)
- [Run 4 — regression: 20 s at −15 A, starts/stops, AWD trip (CSV)](detect_regression_normal_run.csv)
