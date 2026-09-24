---
doctype: Test Plan
doc_id: OV-TEST-HW-LOSS-OF-REGEN
title: Loss-of-Regen Detection and Indication
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-09-24"
description: "Exercises the SG-04 loss-of-regen monitoring path (HARA GAP-TEST-01): regen must be detected as unavailable, the operator informed, and friction brakes remain the independent fallback."
nav_order: 370
placeholder: true
normative_refs:
  - OV-TEST-METHODOLOGY
  - OV-TEST-COVERAGE
  - OV-TEST-FAULT-INJECTION
---

# Loss-of-Regen Detection and Indication

Test plan stub (placeholder). Execution parameters marked `[FILL: ...]` are assigned per campaign before the run; everything else follows [OV-TEST-METHODOLOGY](../../Test-Methodology/Index.md).

## Purpose & safety traceability

Validates **SG-04 (ASIL A, H-04): monitor regen availability; on loss, inform the operator; friction brakes remain the independent fallback.** The monitoring path is a coprocessor CAN snoop that watches the inverter's regen-availability state and raises the operator indication when regen is lost.

This plan closes **HARA GAP-TEST-01**: a dedicated loss-of-regen test did not exist until this stub. It complements the completed regen power/thermal evidence (e.g. OV-TEST-HW-REGEN-300A-STEADY-STATE-GEN7-SIZE2), which demonstrates regen capability but never exercises its loss. The loss-inducing fault follows the fault-injection approach of [OV-TEST-FAULT-INJECTION](../../Fault-Injection-Test-Plan/Index.md) at system level, applied to one test article.

Quantified budget: detection and indication over CAN within **≤1 s** of the loss event. This plan *proposes* the ≤1 s budget pending HARA allocation; the measured value is recorded for ratification rather than asserted (see Measurements & acceptance criteria). Friction-brake independence is an architectural property (hydraulic/mechanical path, not dependent on the inverter or coprocessor); it is stated and configuration-checked here, not re-proven.

Blocked-on-firmware caveat: the CAN indication message (ID/content) and the regen-availability signal it carries must exist in the coprocessor firmware before execution. If either is not yet implemented, this plan cannot execute and the gap remains open — record the firmware graph + hash and the blocking state in the coverage checklist (OV-TEST-COVERAGE).

## Scope

- DUT: Gen7 control module + C2 power stage, chassis size 2, dynamometer-coupled machine per methodology §1.
- Bus classes: both the 200 V and 450 V class as columns of the variant parameter matrix (methodology §6). This plan does not restate matrix values; execution selects one column.
- Chosen execution parameters: **[FILL: DUT variant]**, **[FILL: chosen loss-inducing fault]** (commanded regen disable or simulated inverter-side inhibit — select the fault that represents H-04), **[FILL: CAN message ID/content]**.
- Out of scope: friction-brake performance, machine-level torque confirmation on a vehicle, other safety goals.

## Bench setup & preconditions

Per methodology §1, with the variant-specific items as `[FILL]` placeholders:

| Item | State |
|------|-------|
| DUT | Gen7 control module + C2 power stage, thermal interface state recorded; firmware graph + hash logged — variant: **[FILL: DUT variant (200 V vs 450 V class)]** |
| Machine | Dynamometer-coupled, pole count and resistance from FRAM config; machine thermal limit identified **before** the run — **[FILL: machine and its thermal limit]** |
| DC supply | Bench supply with regen sink; Chroma/load bank in CV mode mandatory when regen exceeds the supply's sink limit — **[FILL: supply/sink arrangement]** |
| Fixture / guarding | **[FILL: fixture]** |
| CAN monitoring | Coprocessor CAN-snoop node on the DUT bus, logging the regen-availability signal and the operator-indication message; message definition per **[FILL: CAN message ID/content]** |
| Current measurement | Probes rated ≥ 1.25 × peak expected phase current (≥125 A class here) |
| Telemetry | Full-rate session log + 1 Hz decimated log + overview plot per methodology §1 |

Safety notes: regen at ~100 A pushes energy back into the bus — the sink arrangement must be verified before the hold, and on the 450 V class the DC link holds lethal energy (verify discharge/bleed before touching). The machine and dynamometer are rotating equipment; confirm guarding and e-stop reach before the staircase. No short-circuit fault is applied in this test; the loss-inducing fault is a control-level inhibit only.

## Procedure

Archetype mapping: methodology **archetype A (steady-state thermal hold)** — used to *establish* regen at ~100 A against the dynamometer before the loss event; the hold window is shortened, and steady-state confirmation per methodology §2 is not required. Stop criteria priority per methodology §2 applies throughout.

1. Configure the DUT per the bench table; record firmware graph + hash, bus class, and machine identity in the operator log.
2. Bring the machine to speed on the dynamometer; confirm regen/motoring orientation with a −10…−25 A jog, then staircase to the ~100 A regen point in 25 A steps per methodology §2 (dwell ≥ 5 s and ≥ 2× current-loop settling time per step).
3. Hold ~100 A regen within ±5 % of command (or ±10 A, whichever is larger); record the held-current average and min/max. Capture the baseline 5-panel telemetry window.
4. At a logged timestamp T0, inject the chosen loss fault (**[FILL: chosen loss-inducing fault]**) mid-hold. Do not touch the current command — the DUT must detect the loss, not the operator.
5. Capture: time from T0 to CAN indication (detection time); the indication message ID and content (**[FILL: CAN message ID/content]**); FOC state and phase currents through the event; confirm tractive behavior goes torque-free (iq → 0, no unintended torque) by command or by the DUT's own response.
6. Hold the post-event state for ≥ 1 min; verify no unintended torque appears during or after the event (phase currents at zero within the noise band).
7. Record the friction-brake independence statement: braking authority is unaffected by the inverter-side inhibit and the coprocessor indication (independent hydraulic/mechanical path); capture the vehicle/brake-interface configuration evidence.
8. Clear the fault at a logged timestamp T1; verify normal operation resumes — repeat the orientation jog and staircase to ~100 A regen and hold briefly.
9. Log ≥ 5 min of cooldown. Stop per methodology §2 priority order, recording the reason and DUT state explicitly.

## Measurements & acceptance criteria

| # | Criterion | Pass condition |
|---|-----------|----------------|
| 1 | Detection + indication time | Loss detected and indicated over CAN within **≤1 s** of T0. The ≤1 s budget is *proposed* in this plan pending HARA allocation — record the measured value for ratification rather than asserting final compliance |
| 2 | Indication content | CAN message ID and content match the defined loss-of-regen indication (**[FILL: CAN message ID/content]**); content recorded verbatim in the report |
| 3 | No unintended torque | Phase currents and iq remain at zero (within noise band) during and after the event; tractive behavior is torque-free |
| 4 | Recovery | After clearing the fault at T1, regen re-establishes at the staircased operating point with no faults latched |
| 5 | Friction-brake independence | Independence of the friction-brake fallback stated and configuration evidence recorded |

All §3 calculated quantities (P, Q, |S|, PF, η) are reported over the pre-event hold window only; the post-event window is torque-free by definition and is reported as state/flags, not power.

## Evidence package

Per methodology §5:

- Sibling Test Report under `Hardware/` with the standard sections (Test setup, Test conditions, Procedure, Electrical results, Thermal results, Telemetry overview, Observations, Conclusion, Artifacts).
- Conditions table including hardware + firmware hash, machine + speed, bus class, current command + held window (avg/min/max), ambient, CAN message ID/content, and the measured detection time.
- Telemetry overview plot, standard 5-panel layout: Iq; DC-link power; machine-terminal P (kW) and Q (kvar); baseplate NTCs with ambient reference; bus voltage — spanning T0 and T1.
- Full-rate session log + 1 Hz decimated log; decimated log linked in the Telemetry Viewer.
- Photos: bench/fixture, CAN trace capture of the indication, current probes; the archetype-A thermal photo pass is optional here since no plateau is acquired.
- Naming and `doc_id` per the Testing naming convention in Docs/Agents.md; fault-injection provenance logged per OV-TEST-FAULT-INJECTION.

## Execution record

To be filed as a sibling Test Report referencing this plan by doc_id `OV-TEST-HW-LOSS-OF-REGEN`; the test ID is assigned at execution and recorded in both the report and OV-TEST-COVERAGE.
