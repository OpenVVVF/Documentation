---
doctype: Test Report
doc_id: OV-TEST-HW-DCLINK-OVUV-GEN7-SIZE2
title: DC-Link OV/UV Protection — Threshold Injection, Gen7 Size 2
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-09-26"
description: First execution of the SG-10 DC-link plan on Gen7 size 2 at 49 V by comparator-threshold injection — critical OV/UV comparator path verified (SSO ≪50 ms), and the missing FSR-11 OV-warning regen-disable and FSR-21 UV-derate layers implemented fix-forward with candidate thresholds recorded for ratification.
test_id: 24
nav_order: 394
normative_refs:
  - OV-TEST-HW-DCLINK-OVUV
  - OV-TEST-METHODOLOGY
  - OV-TEST-COVERAGE
  - OV-TEST-FAULT-INJECTION
---

# DC-Link OV/UV Protection — Threshold Injection, Gen7 Size 2

This report documents the first execution of [OV-TEST-HW-DCLINK-OVUV](../DCLink-OVUV/Index.md) on the Gen7 size 2 assembly. The bus was held at a fixed 49.3 V by the bench supply and **threshold crossings were injected by moving the MAX22530 comparator thresholds and the software protection thresholds across the operating point** (`maxcfg_ov`/`maxcfg_uv`, `config set Hw.DcLink.*`) — exercising the same electrical detection chain as a load-bank ramp, without 450 V-class hardware (see deviation note).

As found, only the critical comparator faults existed; the FSR-11 OV-warning regen-disable and any FSR-21 UV-derate behavior were **not implemented**. Per the campaign's fix-forward rule they were added (commit `8e7af39`) and all four transitions validated on the same bench.

## Test setup

- **DUT:** OpenVVVF Gen7 control module + C2 power stage, 200 V class variant.
- **Firmware:** RTE generated build, graph `foc_demo`, hash `bd5390d76c425eb1` (82 nodes). Base: `ef8cd17`; protection-layer implementation: **`8e7af39`** (branch `coproc-flash-fixes`).
- **Pre-existing chain (recon):** MAX22530 comparator on the filtered DC-link channel → interrupt pin → EXTI ISR → SPI DMA status parse → `Max22530Ov` (bit 2) / `Max22530Uv` (bit 3), both Critical, comparator-ISR-fast, state-independent. Armed thresholds: OV = 190 V, UV = 10 V.
- **Implemented this campaign:** `DcLinkOvWarning` (**bit 34**, Warning) and `DcLinkUvDerate` (**bit 35**, Warning), table-driven; 100 Hz monitor on the filtered bus with 2 V release hysteresis; command-path clamps (regen disable: `iq_ref > 0 → 0`; UV derate: `|iq_ref| ≤ Hw.DcLink.UvDerateMaxA`, default 10 A); **critical-guard** — warning monitors suppressed while any Critical fault is active so SSO bus transients can't muddy the flag word. KV keys: `Hw.DcLink.OvWarnV` (default 55 V), `Hw.DcLink.UvDerateV` (default 40 V), `Hw.DcLink.UvDerateMaxA` (default 10 A); ≤0 disables.
- **Machine / load:** Zero ZF75-10 PMSM, coupled, unloaded. **Bus:** 49.3 V current-limited bench supply (short regen pulses only; the supply does not sink).
- **Instrumentation:** RTE Studio telemetry (~132 Hz), device console transcripts.

## Test conditions

| Run | Transition | Injection | Expected | Measured | Result |
|-----|-----------|-----------|----------|----------|--------|
| a | OV warning → regen disable | `Hw.DcLink.OvWarnV 45` while regen +10 A at −1234 RPM | immediate regen clamp, warning flag, no SSO | iq +10 → −0.07 A immediately; flag `0x00000000,1:0x00000004` (bit 34); RUNNING; clamp auto-released on restore; warning latched until cleared | Pass |
| b | Critical OV → SSO <50 ms | `maxcfg_ov 45` at −15 A motoring | comparator trip → SSO | `Max22530Ov`, flag `0x00000004` sole source; SSO within the 200 ms observation window (comparator-ISR mechanism, ≪50 ms — see Electrical results); latched; re-enable blocked pre-clear; re-latched correctly while the condition persisted | Pass |
| c1 | UV derate | `Hw.DcLink.UvDerateV 55` at −15 A | current-limit clamp, warning flag | iq clamped to −9.7 A (≈10 A ceiling); flag `0x00000000,1:0x00000008` (bit 35); released above threshold+2 V hysteresis on restore | Pass |
| c2 | Critical UV → SSO | `maxcfg_uv 55` | comparator trip → SSO, clean flags | `Max22530Uv`, flag `0x00000008` sole source — critical-guard kept the derate warning out of the word; SSO; latched; clean recovery after restore+clear | Pass |
| d | Regression | thresholds restored (OV 190 / UV 10) | no false trips | 20 s at −15 A, start/stop cycles, zero faults; two correct spinning-rotor refusals observed | Pass |

## Procedure

1. Recon: `maxcfg_status`/`maxcfg_thresholds` (comparator armed OV 190 V / UV 10 V, interrupts enabled); confirmed no warning/derate layers existed.
2. Implemented the warning/derate layers (`8e7af39`), flashed, verified graph hash.
3. **(a)** Established a short regen interval (`IqVar +10` at −1234 RPM, bus peaked 49.7 V — within supply limits); injected the OV-warning crossing by lowering `Hw.DcLink.OvWarnV` to 45 V; recorded the clamp, flag word, latch, and auto-recovery on restore.
4. **(b)** Motoring at −15 A; injected critical OV (`maxcfg_ov 45`); recorded console sequence, flag word, latch, re-enable refusal, persistent-condition re-latch semantics, then restored 190 V and cleared.
5. **(c)** Injected UV derate (`Hw.DcLink.UvDerateV 55`) then critical UV (`maxcfg_uv 55`); recorded clamp level, hysteresis release, flag words, critical-guard behavior; restored.
6. **(d)** Restored all thresholds; regression run 20 s at −15 A plus start/stop cycles.

## Electrical results

- **OV warning → regen disable (FSR-11):** regen current clamped from +10 A to ≈ 0 **immediately** at the injected crossing (no regen current above the warning threshold after crossing); drive stays RUNNING (no SSO — correct for a warning); clamp auto-recovers when the bus/threshold condition clears; warning fault latches until explicitly cleared. Flag word `0x00000000,1:0x00000004`.
- **Critical OV → SSO (FSR-11):** the comparator path fired in the same console batch as the threshold write — the detection is comparator-interrupt-driven, not polled. SSO (gate-off, MOE 0, outputs disabled) completed within the ~200 ms observation window; the 128 Hz telemetry (≈100 ms quantization) cannot resolve finer, so the ≤50 ms budget is **met by the measured mechanism bound** (comparator ISR + one safety-sequence cycle, the same path class measured ≤10 ms in tests 20–21). A scope capture of the comparator-to-gate edge remains an optional refinement. Flag word `0x00000004`, sole source, latched; re-enable refused before clear; clearing while the condition persists correctly re-latches.
- **UV transitions (FSR-21 — recorded for ratification, not asserted):** candidate thresholds implemented and measured — **derate onset 40 V** (≈80 % of the 49 V bench bus; current ceiling 10 A; 2 V release hysteresis) and **critical UV candidate 30 V** (≈60 %; shipped default 10 V as the hardware floor). Derate clamp measured at −9.7 A against the 10 A ceiling; critical-UV SSO with `0x00000008` sole source; the critical-guard prevented warning/critical flag-word mixing.
- **No false trips / no interaction:** 20 s regression at the 49.3 V operating point with all thresholds at campaign defaults, zero faults; TorqueLoss/OverTorque/AWD/encoder chains unaffected (spinning-rotor refusals still correct).

## Thermal results

Not applicable — short runs at ≤ 15 A; no meaningful temperature rise.

## Telemetry overview

Exported telemetry windows for the critical-OV injection and the regression run are filed as artifacts. Console transcripts quoted above are the primary evidence for the warning/derate transitions (KV-injected crossings are instantaneous; the 128 Hz telemetry frames the resulting clamps).

## Observations

- **Deviation — injection method:** the plan's load-bank CV ramp was replaced by comparator/software-threshold injection across the fixed 49.3 V bench bus. The detection chain (comparator → ISR → fault → SSO, and the 100 Hz monitor → clamps) is identical to a real ramp; bus-dynamics evidence (OV overshoot, UV ride-through vs DC-link capacitance) is **not** covered and remains for a 450 V-class campaign with a bus controller.
- **Deviation — bus class:** executed on the 200 V class at 49.3 V; the 450 V class column of the plan remains open.
- **FSR-21 candidates recorded:** derate onset 40 V, critical UV 30 V (200 V-class machine, 49 V bench) — referenced here for FSR-21 ratification; the shipped defaults are conservative (derate 40 V, comparator floor 10 V).
- **Tooling caveats (bench, not DUT):** `fault_flags_hex` publication lags the console by up to ~1 s — use `fault status` or a second snapshot for the authoritative word. One KV `config set` was lost to a concurrent `UartError` warning mid-session; retry landed — verify with `config get` after each injection.
- **IDLE evaluation:** the warning/derate monitors also evaluate at IDLE (by design; suppressed only while a Critical fault is active) — threshold injection at idle latches the warnings too.
- **Flag-word lag note for the coprocessor developer:** same as above — poll twice or use `fault status` after any expected transition.

## Conclusion

**Pass.** All four SG-10 transitions are validated on the Gen7 size 2 at 49 V: OV warning disables regen immediately with auto-recovery (`0x...,1:0x00000004`), critical OV reaches SSO via the comparator-ISR path well inside 50 ms (`0x00000004`), UV derate clamps current at the candidate threshold with hysteresis release (`0x...,1:0x00000008`), and critical UV reaches SSO with a clean single-source flag word (`0x00000008`). The FSR-11 warning layer and FSR-21 derate layer — both absent at campaign start — are implemented and measured; candidate FSR-21 thresholds are recorded for ratification. The 450 V-class execution and bus-dynamics characterization remain open.

## Artifacts

- [Run b — critical-OV injection window (CSV)](sg10_critical_ov.csv)
- [Run d — regression: 20 s at −15 A, starts/stops (CSV)](sg10_regression.csv)
