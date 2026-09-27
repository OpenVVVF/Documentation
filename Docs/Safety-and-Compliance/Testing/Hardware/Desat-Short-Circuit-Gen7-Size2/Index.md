---
doctype: Test Report
doc_id: OV-TEST-HW-DESAT-SHORT-GEN7-SIZE2
title: DESAT / Gate-Driver FLT Protection — Pulse Injection, Gen7 Size 2
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-09-27"
description: First execution of the DESAT plan on Gen7 size 2 via full-duty winding pulses at 50 V and 100 V — 50 V cannot reach the DESAT region (≥800 A, no event); 100 V pulses drive the gate driver into /FLT, exposing a fully blind FLT→main-MCU chain (missing BIE, NVIC, and GPIO poll), fixed and retested to latched PwmBreak + SSO.
test_id: 25
nav_order: 395
normative_refs:
  - OV-TEST-HW-DESAT-SHORT
  - OV-TEST-METHODOLOGY
  - OV-TEST-COVERAGE
  - OV-TEST-FAULT-INJECTION
---

# DESAT / Gate-Driver FLT Protection — Pulse Injection, Gen7 Size 2

This report documents the first execution of [OV-TEST-HW-DESAT-SHORT](../Desat-Short-Circuit/Index.md) on the Gen7 size 2 assembly, covering **SG-12** (hardware PWM disable on shoot-through-class events), **FSR-13** (DESAT chain), and the main-MCU half of **SG-14** (gate-driver fault → safe state). The injection method deviates from the plan's bolted-short fixture: **full-duty `gatefire` pulses through the motor winding** at standstill, at 50 V and 100 V bus (≤140 V per LIMIT-10). Two firmware defects were found and fixed fix-forward; all results below distinguish as-found from as-left behavior.

## Test setup

- **DUT:** OpenVVVF Gen7 control module + C2 power stage, 200 V class variant; Zero ZF75-10 PMSM coupled, rotor free, standstill throughout (no spinning at 100 V — overspeed risk).
- **Firmware:** graph `foc_demo`, hash `bd5390d76c425eb1` (82 nodes) throughout. Commits: `3e0c2d4` (`gatefire` re-arm fix), **`c5659cf`** (FLT detection fix), branch `coproc-flash-fixes`.
- **Injection:** `gatefire <phase> 100 <ms>` — one high-side held on, other legs parked; current ramps through the winding (~96 A/ms at 50 V, ~200 A/ms late-phase at 100 V with IPM inductance saturation).
- **Protection window for the pulses (deliberate):** `Motor.MaxTorqueCurrentA=0` (OverTorque + derived AWD disabled), `ocset 800` backstop, OV comparator 190 V armed, `Hw.DcLink.OvWarnV=150`. All restored at the end except OvWarnV (bus still 100 V — see Observations).
- **Instrumentation:** RTE Studio telemetry, firmware 5 kHz spike capture, TIM1 register diagnostics (`BDTR`/`SR`, GPIO IDR) added to the `status` command during this work. No scope — the user's scope watched the phase lead; sub-µs figures are mechanism/register-domain evidence, not cursor-measured.

## Test conditions

| Run | Bus | Pulse | Peak current | Driver /FLT | Firmware response | Result |
|-----|-----|-------|--------------|-------------|-------------------|--------|
| 1 | 50 V | 1 ms | −106 A | none | none | no event (expected) |
| 2 | 50 V | 2 ms | ±618 A (sensor limit) | none | none | **no DESAT** |
| 3 | 50 V | 2 ms | >800 A; bus sag <10 V (PSU fold) | none | software OC + Max22530Uv | **no DESAT** — 50 V can't reach the region |
| 4 | 100 V | 3 ms | (ramp) | **LATCHED** (`gate_fault=1`) | **NONE — `0x00000000`** | **DEFECT: FLT→MCU blind** |
| 5 | 100 V | 1 ms | −229 A | none | none | no event (expected) |
| 6 | 100 V | 2 ms | collapsed mid-pulse (driver off) | asserted | **`PwmBreak` `0x00000002`** + safety sequence → SSO | **Pass (as left)** |
| 7 | 100 V | 5 ms | driver event reproduced | asserted | **`0x00000002`** + SSO, no app hang | **Pass (as left)** |

## Procedure

1. **50 V escalation** (after fixing `gatefire` — see Observations): 1 ms, 2 ms pulses with protections windowed open; monitored /FLT, `PwmBreak`, currents, bus.
2. **100 V escalation:** 1 ms, 2 ms, 3 ms; the 3 ms pulse produced a **latched driver /FLT with zero firmware response** — the campaign's key finding.
3. **Root cause (three layers, all confirmed by register measurement):** the TIM1 BKIN hardware path was correctly wired and configured all along (PE15, AF1, break enabled, polarity LOW matching active-low /FLT) and the hardware break *did* fire — MOE dropped, BIF set. But (a) `TIM_IT_BREAK` (BIE) was never set, so the HAL never dispatched the break callback; (b) `TIM1_BRK_IRQn` was never enabled in the NVIC; (c) no 100 Hz GPIO poll of the /FLT pin existed. `PwmBreak` was unreachable by any path.
4. **Fix (`c5659cf`):** enable BIE + `TIM1_BRK_IRQn` (priority 2, above the control ISRs); break callback raises `PwmBreak` ("DESAT break (/FLT low)") and **one-shots the IRQ** — required because the NCx5710y /FLT latch holds the break input active, and a level-retriggered priority-2 IRQ **livelocked the whole application** when first enabled (measured; recovery via bridge re-flash); `resetGateHardware()` re-arms BIE after the driver reset pulse clears /FLT; plus a **100 Hz /FLT GPIO backstop poll** (rail-on + out-of-reset + /FLT low for 3 ticks → `PwmBreak`, reason `GateDriverFaultPin`) covering any future BKIN-path failure and the running case.
5. **Retest:** 1/2/3/5 ms pulses at 100 V; DESAT events now latch `PwmBreak` `0x00000002` with the standard safety sequence; a follow-up pulse while latched is correctly refused; recovery verified twice (`fault clear critical` → driver reset pulse clears /FLT → pins/BDTR healthy); the one-shot re-arm works across repeated events.

## Electrical results

- **50 V negative bound:** ≥800 A through the winding with no driver event — the 450 A-class IGBT's Vce at ~1.8× rated current (~2.5–3.5 V) stays below the 6.5 V DESAT threshold; the winding ramp at 50 V cannot reach the DESAT region without destructive current. Recorded as a lower bound, not a fail.
- **100 V:** the winding ramp reaches the driver's protection region in 2–5 ms (reproduction is ramp-dependent — rotor position changes effective inductance: 1 ms never fired, 2/5 ms fired reliably, 3 ms ~50 %).
- **SG-12 (hardware PWM disable):** with the fix, /FLT assertion drops TIM1 MOE and sets BIF **at hardware speed** (register-measured: `BDTR` MOE=0, `SR` BIF=1 on the faulted state, healthy otherwise) — the <10 µs budget is met by the hardware path's construction; the exact figure is scope-domain evidence.
- **SG-14 (main MCU):** the driver fault now latches a Critical `PwmBreak` (`0x00000002`), runs the standard safety sequence (gate reset, power off), blocks re-enable until `fault clear`, and recovers cleanly — verified across two independent DESAT events. The coprocessor /FLT path (OR'd net to the safety MCU) is out of scope here — it is the coprocessor firmware owner's domain.
- **FSR-13 elements not characterized:** soft turn-off waveform, Miller clamp, UVLO 12.2/11.3 V thresholds — these need scope work at the driver pins and remain open (the driver's isolated ±15/−9 V rails were verified healthy; bootstrap sag does not apply on this design).

## Thermal results

Not significant — millisecond pulses; post-event inspection showed a healthy DUT (clean boot, fault-free 10 s control run at 50 V after the 50 V series; gate/telemetry healthy after the 100 V series).

## Telemetry overview

Exported windows for the 50 V pulse series and the 100 V FLT-detection series are filed as artifacts. The 5 kHz spike captures quoted above were dumped per pulse (the recorder's re-arm logic was re-verified during this work — an earlier suspected re-trigger bug was a dump-ordering artifact, not a defect).

## Observations

- **Deviation — injection method:** full-duty winding pulses replace the plan's bolted-short contactor fixture. The winding limits di/dt, so the DESAT event develops over milliseconds rather than microseconds; the protection chain exercised (driver DESAT → /FLT → BKIN → firmware fault → SSO) is the same. A bolted-short fixture remains the method for microsecond-regime energy and for characterizing soft turn-off.
- **gatefire re-arm fix (`3e0c2d4`):** the bring-up command could not fire after any safety sequence — the gate rail was never re-powered (only the reset line toggled, and /RDY reads high through its pull-up regardless) and per-channel HAL PWM stops silently clear MOE. It now mirrors the supervisor's gate-startup sequence and parks phases at the CCER level. Also refuses while graph control is running.
- **IRQ livelock hazard (found during the fix):** naively enabling the break IRQ against a *latched* /FLT hangs the entire application (priority-2 level interrupt re-triggering forever). Any future work on this path must keep the one-shot + re-arm-after-driver-reset discipline.
- **Reproduction variance:** whether a given pulse length fires depends on rotor position (inductance seen by the ramp). For regression purposes, 2 ms and 5 ms at 100 V were reliable; 3 ms was not.
- **`Hw.DcLink.OvWarnV` left at 150 V** while the bus remains at 100 V (the 55 V bench default would latch the OV warning); restore to 55 V when the bus returns to 50 V.
- **Tooling note:** `rte device mode` transiently reported `app_unresponsive_or_silent` after an SSO power-off while telemetry was actually healthy — cosmetic.

## Conclusion

**Pass (as left) for the exercised chain.** At 100 V, a driver-side DESAT event now produces: hardware PWM break at the timer (MOE off, BIF set — SG-12 hardware path), a latched Critical `PwmBreak` fault word on the main MCU with the standard SSO sequence (SG-14 main-MCU half), blocked re-enable until explicit clear, and verified recovery across repeated events. The campaign's as-found state — a fully functional BKIN hardware path made unreachable by missing interrupt plumbing, with no GPIO backstop — would have left every real gate-driver fault invisible to the controller; this is closed. Remaining open: coprocessor /FLT path (colleague's firmware), scope-measured <2 µs/<10 µs figures, soft turn-off/Miller clamp/UVLO characterization, and the bolted-short microsecond-regime fixture.

## Artifacts

- [Runs 1–3 — 50 V pulse series (CSV)](desat_pulses.csv)
- [Runs 5–7 — 100 V FLT-detection series (CSV)](desat_flt_detection.csv)
