---
doctype: Test Plan
doc_id: OV-TEST-HW-SSO-LATENCY
title: Safe-State (SSO) Pathway Latency
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-09-24"
description: Measures fault-detection-to-six-switch-open latency for each independent SSO pathway against the 200 ms budget, the first hardware test targeting SG-03/SG-13.
nav_order: 382
placeholder: true
normative_refs:
  - OV-TEST-METHODOLOGY
  - OV-TEST-COVERAGE
  - OV-TEST-FAULT-INJECTION
---

# Safe-State (SSO) Pathway Latency

## Purpose & safety traceability

This plan validates the safe-state (SSO) entry pathways of the Gen7 control module against two safety goals from the platform hazard analyses:

- **SG-03 (ASIL C)** — backed by **FSR-05: fault-to-SSO ≤ 200 ms**. Every independent pathway below must move the inverter to six-switch-open (all gates off, phase current decaying to zero) within 200 ms of fault detection.
- **SG-13 (ASIL D)** — SSO entry must be **independent of the main control loop**: a stuck, corrupted, or deliberately starved main firmware must not be able to prevent the safe state.

Pathways under test, with their design budgets:

| # | Pathway | Mechanism | Budget |
|---|---------|-----------|--------|
| 1 | TIM1_BKIN hardware break | MCU PWM break input from comparator/overcurrent chain | < 100 ns |
| 2a/2b | 1oo2 gate-drive power kill | Redundant gate-drive PSU cut paths | ~10 µs actuation |
| 3 | 3.3 V rail loss | Passive loss of logic rail removes gate drive | passive (no energy to defeat) |
| 4 | GATE_DRIVE_RESET | Direct gate-driver reset assertion | < 1 µs |
| 5 | Coprocessor windowed watchdog → main NRST | Safety MCU watchdog expiry resets main MCU | ~100 ms |
| 6 | Coprocessor independent trigger | Coprocessor fires SSO without main MCU involvement | < 10 µs |

This is the **first hardware test targeting SG-03/SG-13**; no earlier latency evidence exists for these pathways, so there is nothing to complement — baseline measurements here become the reference for later regression runs. A caveats note: where firmware support for a pathway (watchdog window configuration, coprocessor trigger routing) is not yet implemented on the test build, the run records the measured value against the design budget and flags the gap rather than blocking the campaign; see the fault-injection plan ([OV-TEST-FAULT-INJECTION](../../Fault-Injection-Test-Plan/Index.md)).

## Scope

Applies to the Gen7 control module on chassis size 2, both DC-bus classes. Execution parameters come from the variant parameter matrix §6 of [OV-TEST-METHODOLOGY](../../Test-Methodology/Index.md):

- **Size 2 · 200 V class:** [FILL: DUT variant confirmed — 200 V class, hardware + firmware hash logged]
- **Size 2 · 450 V class:** [FILL: DUT variant confirmed — 450 V class, hardware + firmware hash logged]

Variant-specific values — injection points/harness, current level, scope channels — are [FILL] placeholders in the sections below, fixed per campaign before execution. Archetype: **D. Protection validation** per methodology §4 (the DUT must reach the safe state; a non-trip is a fail).

## Bench setup & preconditions

Standard bench configuration per methodology §1, adapted for a protection-injection run:

- **DUT:** [FILL: Gen7 control module + C2 power stage, 200 V or 450 V variant], thermal interface state recorded; firmware graph + hash logged in the report.
- **Bus:** low bus, **≤ 60 V**, from the bench DC supply with regen sink — the latency result is topology-dependent, not bus-voltage-dependent, and running below 60 V keeps the safe-state verification inside the extra-low-voltage regime. Do **not** repeat injections on the 450 V class at full bus: 450 V DC-link capacitors hold lethal charge after any stop; discharge-verify procedure and qualified personnel are mandatory before touching the harness (methodology §1 supply rules still apply for the supply/sink arrangement).
- **Machine / load:** [FILL: machine coupled or resistor load], pole count and resistance from FRAM config; machine thermal limit identified before the run.
- **Operating point:** control running at moderate current, ~[FILL: 50 A] phase current, so phase-current decay is observable on the scope after SSO entry.
- **Injection harness:** [FILL: injection points — gate-drive PSU cut for Path 2a/2b, GATE_DRIVE_RESET line, 3.3 V rail feed, coprocessor watchdog service point], with a safe means of restoring each after the event.
- **Instrumentation:** logic analyzer / oscilloscope with channels on the injection trigger, the six gate signals, and at least one phase current; probes rated ≥ 1.25 × peak expected phase current (methodology §1); RTE Studio telemetry logging FAULT flags and state.
- **Personnel safety:** injection (a) opens the gate-drive power path while the power stage is live — expect uncontrolled-but-safe coasting of the load, and treat the DC link as charged throughout; injection (d) deliberately starves the safety watchdog, so the operator must be able to cut bus power independently of the DUT at all times.

## Procedure

1. Confirm preconditions: bus ≤ 60 V, machine/load thermal limit known, telemetry streaming, injection harness fitted at the [FILL: injection points], scope armed on trigger, gates, and phase current.
2. Establish the operating point: start control and ramp to ~[FILL: 50 A] with a 25 A staircase (methodology §2: −10…−25 A orientation jog first, dwell per step ≥ 5 s) or direct command; confirm the current is stable before each injection.
3. **Injection (a) — gate-drive power kill, Paths 2a and 2b:** cut the gate-drive PSU via Path 2a; capture the injection instant, gate signals, and phase-current decay. Restore, re-arm, repeat via Path 2b. Record FAULT flag word and whether re-enable is blocked pending POST/clear.
4. **Injection (b) — GATE_DRIVE_RESET:** assert the gate-drive reset line while control is running at the operating point. Capture the same channels; record latency from assertion to gates off and to phase current zero.
5. **Injection (c) — 3.3 V rail removal:** remove the 3.3 V rail (passive pathway; no software involvement expected). Confirm the safe state is reached with no dependence on the main loop and record the observed decay; note the rail-loss threshold value measured for ratification (design thresholds pending definition, cf. FSR UV limits).
6. **Injection (d) — coprocessor watchdog starvation:** stop servicing the coprocessor windowed watchdog while the main control loop continues running current (validates SG-13 independence — the main loop is healthy yet the safe state must still fire). Capture watchdog-expiry-to-NRST and NRST-to-gates-off intervals; where watchdog window configuration is blocked-on-firmware, record the observed behavior and flag it in Observations.
7. For each injection, allow the DUT to cool down per the cooldown practice, then attempt a normal re-enable. Record whether re-enable required POST/clear (expected) or was possible immediately (a defect against SG-03).
8. Repeat each pathway [FILL: repetition count] times per variant and log the full-rate session log + 1 Hz decimated log per methodology §1.

## Measurements & acceptance criteria

Per-pathway pass/fail against the **200 ms** FSR-05 budget (methodology archetype D: a pathway that does not reach the safe state is a fail):

- **Latency:** for every pathway, phase current zeroed **and** all six gates open **≤ 200 ms** from the injection instant. Quote each path's measured latency against its design budget: TIM1_BKIN < 100 ns; gate-drive kill ~10 µs actuation; GATE_DRIVE_RESET < 1 µs; coprocessor watchdog → NRST ~100 ms; coprocessor independent trigger < 10 µs; 3.3 V rail loss passive. The per-path measured value is recorded even when the design budget is itself pending ratification.
- **FAULT flag word:** the correct fault flag(s) set for the injected pathway, recorded from telemetry at the event; an incorrect or empty flag word is a fail even if the safe state was reached.
- **Re-enable behavior:** after cooldown, safe re-enable occurs **only** after POST/clear; immediate re-enable without clear is a fail.
- **No shoot-through:** no phase-current shoot-through spike during any transition, confirmed on the scope capture and in the current telemetry; any shoot-through is a fail regardless of latency.
- Threshold values that are pending definition in the safety analysis (e.g. rail-loss UV levels) are recorded as measured values for ratification, not asserted as pass/fail.

## Evidence package

Per methodology §5:

- Test Report filed under `Docs/Safety-and-Compliance/Testing/Hardware/` with sections: Test setup, Test conditions (table), Procedure, Electrical results, Thermal results, Telemetry overview, Observations, Conclusion, Artifacts.
- Conditions table: hardware + firmware hash, variant (200 V / 450 V class), bus, injection pathway, current at injection, per-path measured latency vs budget, ambient.
- Per-injection scope/logic-analyzer captures: injection instant, gate signals, phase-current decay (the 5-panel overview plot layout per §5 where telemetry quantities are relevant; the latency captures are the primary artifact here).
- Full-rate session log + 1 Hz decimated log per injection, decimated log linked in the Telemetry Viewer.
- Photos: bench with injection harness, scope captures, injection-point close-ups.

## Execution record

To be filed as a sibling Test Report referencing this plan by `doc_id` (OV-TEST-HW-SSO-LATENCY); test ID assigned at execution.
