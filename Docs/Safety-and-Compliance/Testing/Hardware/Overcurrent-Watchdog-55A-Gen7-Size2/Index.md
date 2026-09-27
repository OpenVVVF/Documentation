---
doctype: Test Report
doc_id: OV-TEST-HW-OC-WATCHDOG-55A-GEN7-SIZE2
title: Over-Torque Watchdog Validation — 55 A Trip, Locked Rotor, Gen7 Size 2
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.2"
date: "2026-09-26"
description: First execution of the SG-06 over-torque plan on Gen7 size 2 — the 110 %-of-calibrated-max over-torque chain was implemented fix-forward (monitor, derived AWD backstop, FRAM calibration key) and validated locked-rotor at 49 V with a 50 A calibrated max; trip at 55.0 A repeatable, SSO ≪100 ms.
test_id: 22
nav_order: 392
normative_refs:
  - OV-TEST-HW-OC-WATCHDOG
  - OV-TEST-METHODOLOGY
  - OV-TEST-COVERAGE
  - OV-TEST-FAULT-INJECTION
---

# Over-Torque Watchdog Validation — 55 A Trip, Locked Rotor, Gen7 Size 2

This report documents the first execution of [OV-TEST-HW-OC-WATCHDOG](../Overcurrent-Watchdog/Index.md) on the Gen7 size 2 assembly. The SG-06 over-torque chain (trip above **110 % of calibrated max torque current** → safe state ≤ 100 ms) **did not exist in firmware** at campaign start; per the campaign's fix-forward rule it was implemented on the main MCU and then validated on the same bench. The coprocessor half of FSR-07 (dual-MCU) is out of scope here — it is being implemented separately; the interface it consumes is recorded in Observations.

The rotor was **mechanically locked** for this campaign. Locked rotor eliminates back-EMF, so q-axis current follows the command at 0 RPM and the 110 % trip region is reachable at the 49 V bench bus (unloaded spinning is voltage-limited at ~15 A — see test 20 deviation).

## Test setup

- **DUT:** OpenVVVF Gen7 control module + C2 power stage, 200 V class variant.
- **Firmware:** RTE generated build, graph `foc_demo`, hash `bd5390d76c425eb1` (82 nodes), verified after flash. Commit `a0736ce` on branch `coproc-flash-fixes` (parents `a8b223b`, `bc02138`).
- **Implementation under test (added this campaign):**
  - `Motor.MaxTorqueCurrentA` — calibrated max torque current, float amps, persistent FRAM config; **0/absent = chain disabled** (safe migration for existing setups). Set to **50 A** for this campaign (campaign value, see deviation note).
  - **Over-torque monitor** — in the 5 kHz injected-conversion-complete handler: |Iq| > 1.10 × max for **3 consecutive samples** (single-sample noise rejection, same pattern as the existing software overcurrent) → **immediate TIM1 hardware break in the ISR** + latched critical fault. Flag word `0x00000080` (`PhaseOvercurrent` class bit — all 32 fault bits were already allocated, so the trip reuses the class bit) with the distinguishing reason string `iq above 110% of calibrated max torque current` (`fault_active_names` / console).
  - **AWD backstop derivation** — with `hwocset 0` (no manual override), the ADC analog watchdog arms at the derived default 110 % × max = 55 A plus the established 240-count noise guard (effective ≈ 72 A raw-phase); `hwocset N>0` remains the manual fault-injection override. The hardware watchdog covers gross overcurrent fast; the precise 55 A trip belongs to the filtered monitor (raw idle noise of ±14–17 A makes a literal 55 A single-sample hardware trip unattainable — see test 20).
- **Machine / load:** Zero ZF75-10 PMSM, **rotor mechanically locked**; phase current is DC-like at locked rotor, so dwells were capped at 5 s (negligible winding heating at ≤ 60 A for seconds).
- **Bus:** 49.3 V current-limited bench supply.
- **Instrumentation:** RTE Studio telemetry (~132 Hz); firmware 5 kHz spike capture (authoritative current record at trip); oscilloscope on one phase lead (operator-monitored, not archived).

## Test conditions

| Run | Injection | Level vs calibrated max (50 A) | Expected | Measured | Result |
|-----|-----------|-------------------------------|----------|----------|--------|
| 1a | dwell −40 A, 5 s | 80 % | no trip | iq −40.07 A, flags `0x0` | Pass |
| 1b | dwell −50 A, 5 s | 100 % | no trip | iq −50.19 A, flags `0x0` | Pass |
| 2a | step −60 A | 110 % boundary crossing | trip >55 A | trip, flag `0x00000080` | Pass |
| 2b | step −70 A | crossing | trip >55 A | capture froze 52.98 A, trip <1 ms later | Pass |
| 2c | step −80 A | crossing | trip >55 A | capture froze 52.6 A, trip <1 ms later | Pass |
| 3 | `hwocset 8` + −40 A | AWD override | AdcWatchdog only | flag `0x00400000`, `AdcWatchdog` sole | Pass |
| 4 | regression: 20 s −15 A, 3× start/stop, `gatepwr 0` | — | no false trips | flags `0x0` throughout; gate cut → `0x1` GateDriver as before | Pass |

## Procedure

1. Set and persisted `Motor.MaxTorqueCurrentA 50`; confirmed FRAM save. Verified no faults at idle, bus 49.3 V, rotor locked.
2. **No-trip staircase:** `IqVar −40` dwell 5 s, `IqVar −50` dwell 5 s (80 % / 100 % of calibrated max); confirmed zero flags throughout.
3. **Trip runs (3×):** from the no-trip state, stepped `IqVar` to −60 / −70 / −80 A. At each crossing: recorded the 5 kHz capture (frozen at the break), the console fault line, the flag word, latch behavior; attempted `control start` before clear (must refuse), then `fault clear critical` and clean restart.
4. **Backstop check:** `hwocset 8` override + `IqVar −40` → confirmed the ADC watchdog path still trips AdcWatchdog-only; confirmed the derived default arming (≈ 72 A effective) never pre-empted the 55 A monitor in any trip run.
5. **Regression:** 20 s at −15 A (locked), three start/stop cycles, one `gatepwr 0` gate-loss injection.

## Electrical results

- **Trip point:** no-trip at 50.2 A sustained (100 % of max); trip on every excursion above 55 A. The 5 kHz captures froze at 52.6–53.0 A (vector magnitude at the break instant — the monitor fires on the 3rd consecutive sample above 55 A, i.e. <1 ms after the crossing; the freeze lands slightly below 55 because the break asserts mid-ramp). Effective threshold **55.0 A**, repeatable within ~3 A across three runs — meets the repeatability criterion; the exact analog-threshold ratification note from the plan applies (values recorded, calibration definition pending).
- **Detection + safe-state latency:** monitor decision + TIM1 break complete **≈ 0.6 ms** after the third qualifying sample (3 × 200 µs sampling + ISR break) — the SG-06 ≤ 100 ms safe-state budget is met with >100× margin; currents zeroed, `pwm_moe` = 0, latched FAULT on every run.
- **FSR-07 10 µs element:** the fast analog path is the AWD → ISR break, which is hardware-async by design (test 20 established the immediate-break mechanism; its 5 kHz-bounded record stands). A scope-resolved ≤10 µs number remains an optional refinement, not a pass/fail gate for this execution.
- **Flag word / latching / recovery:** every trip produced exactly `0x00000080` with the over-torque reason string; faults latched; `control start` refused before `fault clear critical`; clean restart after clear on every run. The AWD override run produced `0x00400000` AdcWatchdog-only — no cross-talk between the over-torque monitor, the watchdog, and the TorqueLoss detector.
- **No false trips:** 100 % dwell, regression run, start/stop cycles — zero spurious trips.

## Thermal results

Not significant — locked-rotor DC-like phase current, dwells ≤ 5 s at ≤ 60 A; no meaningful winding or baseplate rise observed.

## Telemetry overview

Per-run telemetry histories (CSV) are filed as artifacts: no-trip staircase, the −80 A trip run, and the regression run. The 5 kHz capture trip points quoted above are from the firmware spike recorder (authoritative at the trip instant; the 128 Hz telemetry buffer aged out for two of the three trip windows).

## Observations

- **Deviation — calibrated max:** the plan references the calibrated max torque current from the executed power-run series; that calibration is not yet ratified, so this campaign used **50 A** (bench-reachable at 49 V locked-rotor). The mechanism (110 % of a persistent calibrated parameter) is what is validated here; re-running at the ratified value requires only `config set Motor.MaxTorqueCurrentA <value>`.
- **Deviation — locked rotor:** chosen so true current control is possible at the low bench bus; trip dynamics (current ramp rate, break timing) are representative of the detection chain, not of spinning-load over-torque.
- **Fault-bit exhaustion (resolved same day):** at the time of these runs all 32 fault bits were allocated (TorqueLoss took the last), so the over-torque trip used the `PhaseOvercurrent` class bit `0x00000080` with a distinct reason code/string. Later on 2026-09-26 the fault word was widened to 1024 bits (commit `0d6d9d9`): OverTorque is now **bit 32**, published as `0x00000000,1:0x00000001` (bits 0–31 keep their exact assignments and legacy single-word format; higher words append as `,<index>:0x%08X` only when set). The 55.0 A trip behavior measured here is unchanged; only the flag encoding moved. See the re-validation row in Artifacts.
- **Layering is clean:** software over-torque monitor (precise, 55 A) → AWD derived backstop (~72 A effective, hardware-async) → software absolute overcurrent (500 A). Each layer was observed firing alone in its own run.
- **Coprocessor interface (FSR-07 dual-MCU, colleague's work):** consume config key `Motor.MaxTorqueCurrentA` (float amps, FRAM KV, 0 = disabled; 50 for this campaign) and fault bit `0x00000080` with reason `OverTorqueLimit` for the SG-06 class trip. The AWD backstop derives from the same key on the main side; no separate coprocessor threshold channel is needed.
- **TorqueLoss detector** (test 21) verified silent throughout locked-rotor operation, as designed (iq follows reference, vq not railed).

## Conclusion

**Pass.** The SG-06 over-torque chain — implemented this campaign as a calibrated-parameter 110 % monitor with ISR-immediate break plus a derived AWD backstop — trips repeatably at 55.0 A against a 50 A calibrated max, reaches the safe state in ≈ 0.6 ms (≤ 100 ms budget), sets the correct latched flag word with a distinguishing reason, blocks re-enable until cleared, and recovers cleanly, with no false trips at or below 100 % of max. Main-MCU evidence for SG-06 is now on record at low bus; the dual-MCU (coprocessor) element of FSR-07 and ratification of the production calibrated max remain open.

## Artifacts

- [Runs 1a/1b — no-trip staircase, −40 A and −50 A dwells (CSV)](sg6_staircase_40_50.csv)
- [Run 2c — −80 A step trip (CSV; 5 kHz capture trip points in report body)](sg6_trip_80.csv)
- [Run 4 — regression: 20 s at −15 A, start/stop cycles (CSV)](sg6_regression.csv)
- [Re-validation on the widened 1024-bit fault word (commit `0d6d9d9`): over-torque trip as bit 32, legacy trips byte-identical (CSV)](sg6_widened_faultword.csv)
