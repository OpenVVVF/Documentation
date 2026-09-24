---
doctype: Test Plan
doc_id: OV-TEST-METHODOLOGY
title: Hardware Test Methodology — Standard Definitions and Methods
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-09-24"
description: Standard definitions, methods, and documentation requirements for OpenVVVF power-stage hardware tests (thermal, electrical, endurance, and protection validation). All hardware test reports and test plans must use these definitions so results are comparable across runs, machines, and chassis variants. Methodology is aligned with EN 50155-style endurance practice where applicable.
nav_order: 343
normative_refs:
  - OV-TEST-INDEX
  - OV-TEST-HW-INDEX
---

# Hardware Test Methodology — Standard Definitions and Methods

This document is the shared rulebook for OpenVVVF hardware power tests. It exists so that a "300 A steady-state hold" run in September means exactly the same thing as one run next year on a 450 V chassis: same definitions of steady state, same calculated quantities, same evidence package, same naming. Test plans state *what* to run; this document states *how*.

Scope: power-stage characterization on the Gen7 control module with the C2 chassis assembly (dynamometer-coupled machine, bench DC supply), covering the 200 V and 450 V DC-bus classes. Methods follow common endurance-test practice and are aligned with EN 50155-style severity thinking (temperature classes, supply-voltage variation, functional performance categories); no compliance claim to EN 50155 is made here — it is methodological alignment only. Ceiling/floor variant tests (voltage, temperature, switching-frequency extremes) are reserved for a future revision of this document and are out of scope for now.

## 1. Standard bench configuration

| Item | Requirement |
|------|-------------|
| DUT | Gen7 control module + C2 power stage, thermal interface state recorded (paste lot/thickness or "dry"); firmware graph + hash logged in the report |
| Machine | Dynamometer-coupled, pole count and resistance from FRAM config; machine thermal limit identified **before** the run (datasheet or imager-based) |
| DC supply | Bench supply with regen sink; if expected regen current exceeds the supply's sink limit, a Chroma/load bank in CV mode across the link is mandatory |
| Current measurement | Probes rated ≥ 1.25 × peak expected phase current (400 A run lesson: 150 A-rated clamps saturate and fabricate spikes) |
| Thermal measurement | TI250-class imager for surface passes; baseplate NTCs via telemetry; **ambient must be recorded** (operator log or NTC-at-power-up + imager cold pixels, marked *inferred*) |
| Telemetry | Full-rate session log + 1 Hz decimated log + overview plot (below); decimated log linked to the Telemetry Viewer |

## 2. Standard definitions

- **Steady state (thermal):** |dT/dt| ≤ **0.1 °C over any 5-minute window** on the baseplate NTC under constant operating point. Confirmation requires the window to complete while the operating point is still held.
- **Plateau temperature:** mean of the baseplate NTC over the final 10 minutes of a hold that has reached steady state. Always quoted with the ambient and as ΔT over ambient.
- **Hold:** operating point held within ±5 % of command (or ±10 A, whichever is larger) for the stated window. Average and min/max of the held quantity must be reported.
- **Staircase:** current steps of 25 A after an orientation jog of −10…−25 A (confirms regen/motoring sign before full power); dwell per step ≥ 5 s and ≥ 2× current-loop settling time.
- **Stop criteria (in priority order):** any protection trip; machine thermal limit (no machine thermistor → imager-monitored, case temperature recorded at stop); operator stop. An operator stop on a *machine* limit with the DUT stable is a valid, reportable outcome — record the reason and the DUT state explicitly.
- **Regen / motoring signs:** negative DC-link power = power leaving the link (motoring draw); regen holds are identified by machine delivering P. Quote directions in words, not just signs.

## 3. Standard calculated quantities

All calculated from logged FOC quantities with the **peak-amplitude convention**:

- P = (3/2)·(vd·id + vq·iq) — machine-terminal real power (W); negative = machine generating.
- Q = (3/2)·(vq·id − vd·iq) — machine-terminal reactive power (var). Quote **as magnitude** (machine magnetizing demand); the sign depends on the logged dq frame orientation and is not comparable across runs.
- |S| = √(P² + Q²); **PF = |P| / |S|**, quoted over the hold window.
- **Inverter efficiency:** regen η = mean(P_DC-link) ÷ |mean(P_machine)|; motoring η = |mean(P_machine)| ÷ |mean(P_DC-link)|.

**Reconciliation requirement:** machine-terminal P and DC-link P must imply a thermally plausible inverter loss. If the implied loss is impossible for the observed temperature rise (e.g. ~3 kW "dissipated" while the baseplate climbs 44 K in 10 min), the session's dq-voltage logging does not reconcile — do **not** publish P/Q/PF/η for that session; add a data-quality observation with the firmware build (see the 100 A and 200 A Sept-22 reports). Efficiency quoted within measurement uncertainty reads as ≈95–100 %; values at or above 100 % mean the loss is below telemetry resolution, and must be captioned as such.

## 4. Standard test archetypes

**A. Steady-state thermal hold** — staircase to target current; hold until steady state per §2 (or the applicable stop criterion); TI250 photo pass once plateau is confirmed; record plateau, ΔT over ambient, all §3 quantities; log ≥ 5 min of cooldown.

**B. Burst / capability run** — staircase to a short-duration target; hold for a defined time cap or until a protection trip; for trip-bound runs, record the trip flag word, trip temperature, and time-from-command. Machine thermal limit must be known before starting.

**C. Endurance** — hold at target current ≥ 20 minutes; purpose is sustained-conduction confidence, not plateau acquisition; peak temperature and any drift reported.

**D. Protection validation** — exercise one protection chain deliberately (e.g. drive baseplate into the OT threshold); record threshold value, fault flags, gate behavior, and post-event cooldown. The DUT must trip; a non-trip is a fail.

**E. Electrical quality** — oscilloscope capture of phase currents during a hold (correctly rated probes), bus regulation quality, and the §3 calculated block.

### Component stress by archetype (evidence transfer)

A result transfers across component revisions, capacitance values, or voltage classes only for components the test does not electrically stress. Every report must state which components were stressed; the transfer decision then follows this table:

| Archetype | Electrically stressed | DC-link capacitors stressed? |
|-----------|----------------------|------------------------------|
| A steady-state / C endurance | IGBTs (conduction + switching), DC-link caps (ripple current), busbar links, NTCs | **Yes** — mildly (ripple heating; visible on the imager cap-bank pass). Transfers only within the same voltage class and similar ripple; the 450 V campaign re-validates caps for that class |
| B burst / capability | Same as A, short-duration, high peak | Yes — high ripple during the burst |
| D protection, control-chain injections (SSO latency, encoder loss, overcurrent watchdog, loss-of-regen, externally-heated thermal thresholds) run at low, current-limited bus | Control logic, gate-drive chain, sensing paths; the bus is steady DC | **No** — caps see near-DC conditions at ≤60 V current-limited. Results transfer without cap re-testing, provided the report records the low-power precondition |
| D protection, short-circuit / DESAT (energize-into-fault) | IGBTs, gate drivers, and **the caps themselves as the fault energy source** | **Yes — critically.** Fault energy ≈ ½·C·V² bounds di/dt and deposited energy. Does **not** transfer across voltage class or significant capacitance change without re-validation or an energy-bound calculation |
| D protection, DC-link OV/UV | Bus sensing + protection logic; OV overshoot dynamics depend on total C | **Partially** — logic thresholds transfer; dynamic behavior (OV overshoot, UV ride-through) requires production-representative capacitance in the loop |

Where capacitors are not stressed, one sentence in the report suffices (e.g. "DC-link capacitors not stressed: current-limited bus at ≤60 V, negligible ripple"). Where they are stressed — short-circuit tests and any new voltage class — capacitance and voltage must be recorded and the energy or ripple argument made explicitly.

## 5. Required evidence package (every power test)

1. Test Report under `Docs/Safety-and-Compliance/Testing/Hardware/` with sections: Test setup, Test conditions (table), Procedure, Electrical results, Thermal results, Telemetry overview, Observations, Conclusion, Artifacts.
2. Conditions table including: hardware + firmware hash, machine + speed, bus, current command + window, average held current (avg/min/max), DC-link power, §3 quantities (P, Q, |S|, PF, η where reconciling), ambient (recorded or *inferred*), thermal results.
3. Telemetry overview plot, standard 5-panel layout: Iq; DC-link power; machine-terminal P (kW) and Q (kvar); baseplate NTCs with ambient reference; bus voltage.
4. Full-rate session log + 1 Hz decimated log; decimated log linked in the Telemetry Viewer.
5. Photos per the archetype (bench, scope, thermal passes with crosshair/max readings, machine thermal image if limit-governing).
6. Naming and `doc_id` per the Testing naming convention in `Docs/Agents.md`.

## 6. Variant parameter matrix

Parameters that change between chassis/bus-class executions. Fill in per campaign; tests that consume this table reference it rather than restating values.

| Parameter | Size 2 · 200 V class | Size 2 · 450 V class |
|-----------|----------------------|----------------------|
| Nominal DC bus (test setpoint) | ~145–150 V (Chroma CV 150 V when clamped) | [FILL] |
| Effective switching frequency | 5 kHz | 5 kHz |
| Supply / sink arrangement | Sorensen (~50 A sink) + Chroma CV 150 V | [FILL] |
| Machine(s) | Zero ZF75-10 (10 poles); induction machine (10 poles) | [FILL] |
| Max demonstrated phase current | 470 A peak (450 A cmd, 78 s, dry interface — pre-paste) | [FILL] |
| Continuous demonstrated (pasted) | 300 A, 22.9 min | [FILL] |
| OT protection threshold | 80 °C baseplate (TS1), flag `OvertemperatureInverter` | [FILL] |
| Machine thermal limit (stop crit.) | 86 °C case (ZF75-10, imager) | [FILL] |

## 7. EN 50155 alignment notes

- **Functional performance:** these tests target performance category "characteristic not exceeding specified tolerance / auto-recovery" for protection events — a trip must be clean, flagged, and survivable, and the DUT must be reusable after cooldown without degradation.
- **Temperature practice:** EN 50155-style temperature-class thinking applies to future ceiling/floor campaigns (ambient extremes, −40 °C cold start, elevated ambient derating); those tests are reserved and out of scope for this revision.
- **Supply variation:** future ceiling/floor runs cover bus over/undervoltage behavior; until then, all quoted bus values are nominal-class.
- **Traceability:** the reconciliation requirement in §3 and the firmware-hash logging in §1 are the provenance hooks that make these reports usable as safety-case evidence.
