---
doctype: Test Plan
doc_id: OV-TEST-HW-ENCODER-LOSS
title: Rotor Feedback Loss Detection
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-09-24"
description: "Validates SG-08: loss of rotor position feedback while spinning must be detected and reach safe state within 100 ms (target <50 ms per LIMIT-04)."
nav_order: 373
placeholder: true
normative_refs:
  - OV-TEST-METHODOLOGY
  - OV-TEST-COVERAGE
  - OV-TEST-FAULT-INJECTION
---

# Rotor Feedback Loss Detection

This plan defines the rotor-feedback-loss (encoder-loss) protection validation for the Gen7 control module driving the C2 power stage: deliberately open the rotor position feedback channel while the machine is spinning under control, and measure the time from channel loss to safe state. It follows methodology archetype **D. Protection validation** ([OV-TEST-METHODOLOGY](../../Test-Methodology/Index.md) §4) — the DUT must trip; a non-trip is a fail. It is part of the hardware test coverage matrix (OV-TEST-COVERAGE) and complements the wider fault-injection campaign (OV-TEST-FAULT-INJECTION).

## Purpose & safety traceability

- **Safety goal:** SG-08 (ASIL C, H-08) — loss of rotor position feedback while spinning must be detected and the inverter driven to a safe state within **100 ms**.
- **Quantified budgets (quoted exactly):** detection-to-safe-state **≤100 ms**; LIMIT-04 target **<50 ms**, noting the detection window itself remains a loss-of-control exposure — for the whole window the control loop is running on stale or invalid angle. Both numbers are recorded per injection.
- **Functional requirement:** FSR-09 (encoder-loss detection). This plan validates the FSR-09 chain end to end: channel open → fault flag → gate-off, at operating speed under moderate load.
- **Earlier evidence:** none exists for this chain — the prior power-stage runs (e.g. [OV-TEST-HW-REGEN-300A-STEADY-STATE-GEN7-SIZE2](../Low-Power-Regen-300A-Steady-State-Gen7-Size2/Index.md)) validated thermal/electrical behavior and never tripped encoder-loss. This test fills that gap.
- **Firmware caveat to confirm at setup:** the fault flag identity/latching for encoder loss, and whether a detection timestamp is telemetry-visible on the build under test. If it is not, scope-based timing (Procedure step 3) is the fallback and must be arranged before spin-up.

## Scope

- **DUT:** Gen7 control module + C2 power stage, chassis size 2. [FILL: DUT variant — board revision, thermal interface state, firmware graph + hash]
- **Bus classes:** both size-2 classes (200 V and 450 V) are covered by this plan; execution parameters are filled per campaign via the methodology variant matrix ([OV-TEST-METHODOLOGY](../../Test-Methodology/Index.md) §6), which this plan references rather than restating values.
- **Channels:** Sin/Cos analog feedback and digital (A/B incremental) feedback, opened independently if the harness allows. If the harness cannot isolate them, record which channel(s) the break switch actually opens.
- **Out of scope:** degraded-but-connected feedback (noise, resolution errors) — this plan covers hard channel loss only; partial faults belong to OV-TEST-FAULT-INJECTION.

## Bench setup & preconditions

Per methodology §1 (standard bench configuration), with the variant-specific items as [FILL] placeholders:

- **DUT:** Gen7 control module + C2 power stage; thermal interface state recorded (paste lot/thickness or "dry"); firmware graph + hash logged in the report. [FILL: DUT variant details]
- **Machine:** dynamometer-coupled; pole count and resistance from FRAM config; machine thermal limit identified **before** the run (datasheet or imager-based). [FILL: machine, pole count, thermal limit]
- **DC supply:** bench supply with regen sink; Chroma/load bank in CV mode across the link is mandatory if expected regen current exceeds the supply's sink limit. [FILL: supply/sink arrangement — 200 V vs 450 V class]
- **Fixture / encoder break arrangement:** break switch or relay inserted in each feedback channel (Sin/Cos pair, digital pair) so the channel opens mid-run without disturbing the rest of the harness; verify closed continuity before the run. [FILL: break arrangement — switch type, channels, insertion point]
- **Instrumentation:** current probes rated ≥1.25 × peak expected phase current on two phases; oscilloscope armed for single-shot capture of the gate-disable edge and current decay; telemetry logging per §1.
- **Personnel/equipment safety:** the machine spins at speed with the DC link energized at up to 450 V — hazardous stored energy plus rotating machinery. Verify the E-stop chain before spin-up; keep hands and tools clear of the coupling; meter-check the DC-link capacitors are discharged before touching the encoder harness; operate the break switch remotely or with hands clear of the rotating assembly.

## Procedure

1. Configure the DUT per the bench setup, record firmware graph + hash, and verify both break switches read closed (continuity). Arm the scope single-shot on the gate-enable/fault line with both phase-current probes capturing.
2. Spin the machine to [FILL: test speed, e.g. 2,000 RPM] on the dynamometer and close control at a moderate current command ([FILL: current]). Confirm current orientation with an orientation jog per the staircase convention (methodology §2), then confirm the operating point is held per the hold definition (±5 % of command or ±10 A, whichever is larger). Capture a short baseline window: phase currents, P/Q (P = (3/2)(vd·id + vq·iq), Q = (3/2)(vq·id − vd·iq), quoted as magnitude per methodology §3), and the telemetry overview.
3. Mid-run, open the Sin/Cos channel via its break switch at a logged operator timestamp. Capture: fault flag word before/after, the gate-disable instant (scope), and phase-current decay through safe state. Log until currents have fully decayed.
4. Attempt to re-enable control **without** clearing the fault; record the DUT response (expected refusal or immediate re-trip). Then clear faults per procedure and record whether a POST or power cycle is required before control re-accepts; if control is re-accepted, capture the restart transient on the scope.
5. Repeat steps 2–4 at each [FILL: test speed] in the speed matrix, and with the digital feedback channel opened instead of Sin/Cos (channels independently, harness permitting). Re-check the machine against its thermal limit between injections. Stop criteria in priority order per methodology §2: any protection trip; machine thermal limit; operator stop.
6. End of run: command safe state, spin the dynamometer down, log ≥5 min of cooldown, and record the teardown state (gate drivers, fault latches) before power-down.

## Measurements & acceptance criteria

| # | Measurement | Acceptance criterion |
|---|-------------|----------------------|
| 1 | Detection-to-safe-state time (channel open → all gates off), scope-measured per injection | ≤100 ms at every injection; measured value quoted against the <50 ms LIMIT-04 target; a non-trip is an immediate fail (archetype D) |
| 2 | Fault flags | Encoder-loss fault flag set and latched on every injection; flag identity recorded as FSR-09 evidence |
| 3 | Gate behavior | Gates cut cleanly at detection — no re-firing or pulse bursts during decay (scope) |
| 4 | Phase-current decay | No overcurrent events during decay; currents freewheel to zero with no shoot-through (scope + telemetry) |
| 5 | Restart behavior | Restart only after explicit fault clear; refusal/re-trip before clear is the expected correct behavior; any POST requirement recorded |
| 6 | Operating point at injection | Held per the methodology hold definition up to the instant of channel open |

## Evidence package

Per methodology §5, adapted to a protection event (no thermal plateau required):

- Test Report (sibling to this plan) with sections: Test setup, Test conditions (table), Procedure, Electrical results, Fault/timing results, Telemetry overview, Observations, Conclusion, Artifacts.
- Conditions table: hardware + firmware hash, machine + speed, bus, injection channel, measured detection-to-SSO times, ambient, and stop reasons.
- Telemetry overview plot in the standard 5-panel layout (Iq; DC-link power; machine-terminal P and Q; baseplate NTCs with ambient reference; bus voltage) spanning each injection, plus scope captures of the gate-disable edge and current decay with timing cursors.
- Full-rate session log + 1 Hz decimated log; decimated log linked in the Telemetry Viewer.
- Photos: bench, break-switch arrangement, scope captures, machine thermal image if its limit governed a stop.

## Execution record

To be filed as a sibling Test Report under `Docs/Safety-and-Compliance/Testing/Hardware/` referencing this plan by doc_id (OV-TEST-HW-ENCODER-LOSS); the test ID is assigned at execution per the Testing naming convention in Docs/Agents.md.
