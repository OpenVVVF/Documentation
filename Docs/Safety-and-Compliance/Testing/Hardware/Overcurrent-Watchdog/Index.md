---
doctype: Test Plan
doc_id: OV-TEST-HW-OC-WATCHDOG
title: Over-Torque / Analog Watchdog Overcurrent Validation
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-09-24"
description: Validates the SG-06 over-torque chain — analog-watchdog overcurrent detection within 10 µs and safe state within 100 ms at >110 % of calibrated max torque current.
nav_order: 371
placeholder: true
normative_refs:
  - OV-TEST-METHODOLOGY
  - OV-TEST-COVERAGE
  - OV-TEST-FAULT-INJECTION
---

# Over-Torque / Analog Watchdog Overcurrent Validation

This plan defines the protection-validation test for the SG-06 over-torque safety chain. It follows the standard definitions and methods of [OV-TEST-METHODOLOGY](../../Test-Methodology/Index.md); execution parameters come from its §6 variant matrix, and the evidence package follows its §5 requirements. This is methodology archetype **D (protection validation)**: the DUT must trip — a non-trip is a fail.

## Purpose & safety traceability

This test validates the over-torque safety goal and its derived requirements:

- **SG-06 (ASIL C, hazard H-06):** over-torque above **110 %** of the calibrated maximum torque current must drive the DUT to a **safe state within 100 ms**.
- **FSR-07:** dual-MCU analog watchdog overcurrent detection within **10 µs**.
- **Boundary:** hard-short desaturation protection on the NCV57100 gate driver (**<2 µs** DESAT) is explicitly out of scope here and covered separately by OV-TEST-HW-DESAT-SHORT. This plan covers the analog-watchdog overcurrent chain (current-sense path into the fast protection inputs of both MCUs), not the DESAT path.

No prior executed evidence exists for this chain; the DESAT short-circuit plan and the thermal/power run series (e.g. OV-TEST-HW-REGEN-300A-STEADY-STATE-GEN7-SIZE2) complement it but do not exercise the over-torque detection path. The calibrated max torque current this plan references is itself defined by the executed power-run series; the 110 % trip point must be set from that calibration before execution.

## Scope

DUT is the Gen7 control module on the chassis-size-2 power stage. Per methodology §6, executions cover both bus classes:

| Parameter | Size 2 · 200 V class | Size 2 · 450 V class |
|-----------|----------------------|----------------------|
| DUT variant | [FILL: DUT variant] | [FILL: DUT variant] |
| Nominal DC bus (test setpoint) | ≤60 V for this test (de-energized power class) | ≤60 V for this test (de-energized power class) |
| Injection method | [FILL: injection method] | [FILL: injection method] |
| Trip threshold setting | [FILL: trip threshold setting] | [FILL: trip threshold setting] |

Note: despite the 200 V / 450 V classes in the variant matrix, this protection test runs at a low bus (≤60 V) with a current-limited supply — the chain's detection latency and safe-state timing are electrical, not bus-dependent. The §6 matrix entries are completed per campaign; this plan references them rather than restating values.

## Bench setup & preconditions

Per methodology §1, with the variant-specific items as [FILL] placeholders:

- **DUT:** [FILL: DUT variant] — Gen7 control module + C2 power stage; firmware graph + hash logged in the report; thermal interface state recorded.
- **Machine:** [FILL: machine and its thermal limit] — machine thermal limit identified before the run (datasheet or imager-based), even though this test is not thermally bound; an uncontrolled over-torque event can overheat the machine before the operator reacts.
- **DC supply / sink:** [FILL: supply/sink] — current-limited bench supply, bus ≤60 V for all injections; regen sink per methodology §1 if the machine can return power.
- **Fixture:** [FILL: fixture] — injection fixture (command-step path or sense-path injection harness) with defined, repeatable injection levels; see OV-TEST-FAULT-INJECTION for injection rig conventions.
- **Instrumentation:** RTE Studio telemetry; oscilloscope with appropriately rated current probes (≥1.25 × peak expected phase current per methodology §1) and voltage probes on the watchdog trip signal and gate-enable lines; ambient recorded.
- **Personnel safety:** staged currents beyond 110 % of calibrated max are deliberate over-torque events — keep personnel clear of the shaft coupling (mechanical over-torque hazard) and treat every phase lead as live at injection level. Although this run uses a ≤60 V current-limited bus, the same chain is later verified at full bus by campaign OV-TEST-COVERAGE, where 200 V / 450 V-class DC-link energy applies: discharged-link verification before touching the fixture, and single-operator/observer rule during injection.

## Procedure

1. Configure the DUT per the §6 matrix: set the analog-watchdog trip threshold from [FILL: trip threshold setting] at 110 % of the calibrated max torque current; log the firmware graph + hash and the threshold value.
2. Bring the bench to ≤60 V bus on the current-limited supply; confirm no active faults at idle and capture a baseline scope trace of the watchdog trip signal and gate-enable lines.
3. Arm the oscilloscope on the watchdog trip signal with sufficient time resolution to resolve a 10 µs interval; start full-rate and 1 Hz decimated telemetry logging.
4. If using the over-current command step: apply the staircase convention of methodology §2 (25 A steps after a −10…−25 A orientation jog, dwell per step ≥5 s) up to just below the trip threshold, confirming command/current orientation and stable readings; record the pre-trip operating point.
5. Stage the first injection beyond the threshold via [FILL: injection method] — either an over-current command step or a sense-path injection per OV-TEST-FAULT-INJECTION. Capture: watchdog trip point (current at trip), detection latency (current/threshold crossing to watchdog trip, budget ≤10 µs), and gate-off/SSO completion (trip to safe-state observable, budget ≤100 ms).
6. Record the FAULT flag word from telemetry, whether the fault latches, and the gate status; attempt a safe re-enable per the defined recovery sequence and record whether it succeeds cleanly (and whether the trip is non-destructive — DUT reusable after the event).
7. Repeat at a few current levels across the trip threshold (below, at, and above 110 %) to establish threshold repeatability; record the measured trip point at each level.
8. After the final injection, command zero current, let the DUT cool per methodology archetype D (post-event cooldown logged), and verify no gate-driver damage: clean idle boot, no gate faults, scope check of gate waveforms at low bus.
9. End the session; export logs and scope captures for the evidence package.

## Measurements & acceptance criteria

| # | Measurement | Pass criterion |
|---|-------------|----------------|
| 1 | Watchdog detection latency (threshold crossing → watchdog trip) | ≤10 µs on scope, per FSR-07 |
| 2 | Safe-state completion (trip → gate-off/SSO observable) | ≤100 ms, per SG-06 |
| 3 | Trip threshold | Repeatable across levels; measured trip point recorded at each level and ratified against the 110 % setting — the exact analog threshold is pending calibration definition, so this test records measured values for ratification rather than asserting them |
| 4 | FAULT flags / latching | Correct flag word for the analog-watchdog overcurrent source; latching behavior matches the fault-response definition; safe re-enable succeeds |
| 5 | Post-event health | No gate-driver damage; clean re-boot; no spurious faults |

A non-trip at any staged level above the threshold is a fail (archetype D). Any unexpected protection trip at or below the confirmed pre-trip operating point is also a fail and ends the run pending review.

## Evidence package

Per methodology §5 (all items required):

- Test Report filed as a sibling under `Docs/Safety-and-Compliance/Testing/Hardware/`, with sections: Test setup, Test conditions (table), Procedure, Electrical results, Thermal results, Telemetry overview, Observations, Conclusion, Artifacts.
- Telemetry overview plot in the standard 5-panel layout (Iq; DC-link power; machine-terminal P and Q; baseplate NTCs with ambient reference; bus voltage).
- Full-rate session log + 1 Hz decimated log; decimated log linked in the Telemetry Viewer.
- Scope captures: watchdog trip point, detection latency, and gate-off/SSO timing screenshots with probe/scale annotations.
- Photos per archetype D: bench, injection fixture, scope, and any thermally notable readings.

## Execution record

To be filed as a sibling Test Report referencing this plan by doc_id (`OV-TEST-HW-OC-WATCHDOG`); test ID assigned at execution.
