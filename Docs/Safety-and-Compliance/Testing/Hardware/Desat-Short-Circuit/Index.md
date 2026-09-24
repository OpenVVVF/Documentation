---
doctype: Test Plan
doc_id: OV-TEST-HW-DESAT-SHORT
title: Short-Circuit / DESAT Protection (Energize-Into-Fault)
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-09-24"
description: Exercises the SG-12/SG-14 short-circuit protection by energizing the inverter into a pre-faulted phase at ≤140 V and verifying DESAT detection <2 µs, soft turn-off, FLT routing to both MCUs, and safe state.
nav_order: 375
placeholder: true
normative_refs:
  - OV-TEST-METHODOLOGY
  - OV-TEST-COVERAGE
  - OV-TEST-FAULT-INJECTION
---

# Short-Circuit / DESAT Protection (Energize-Into-Fault)

Methodology archetype **D — protection validation** per [OV-TEST-METHODOLOGY](../../Test-Methodology/Index.md) §4: the protection chain is exercised deliberately, and a non-trip is a fail.

## Purpose & safety traceability

This plan validates the short-circuit protection chain allocated to:

- **SG-12 (ASIL C, hazard H-12):** prevent shoot-through; risk reduction → PWM disable **<10 µs** via hardware.
- **FSR-13:** DESAT detection on all six IGBTs — threshold **VTH 6.5 V**, local disable **<2 µs**, soft turn-off, active Miller clamp, gate-driver UVLO at **12.2 / 11.3 V**.
- **SG-14 (ASIL C):** a gate-driver fault (DESAT/UVLO/TSD) drives the system to a safe state via OR'd FLT routed to both MCUs.
- **LIMIT-10:** no mid-operation short injection is possible on this hardware; the test is energize-into-fault only, at **≤140 V**.

Quantified budgets under test: DESAT detection **<2 µs**, hardware PWM disable **<10 µs**, and FLT asserted to both MCUs with safe-state output (SSO) within **≤200 ms**.

This complements the existing protection-validation evidence — the overtemperature chain in [OV-TEST-HW-THERMAL-OTP-200A-GEN7-SIZE2](../Thermal-OTP-200A-Gen7-Size2/Index.md) — by covering the short-circuit path, which no executed run has exercised yet (see coverage status in OV-TEST-COVERAGE). It is filed as a hardware test (physical DUT) that consumes the energize-into-fault constraints of OV-TEST-FAULT-INJECTION. No firmware change is expected for this test; if DESAT/FLT telemetry capture requires a firmware build not yet available, execution is blocked on that build and the report must record the firmware graph + hash actually used.

## Scope

- **DUT variant:** [FILL: chassis size 2 assembly, bus class (200 V vs 450 V), thermal interface state] — selected per the variant matrix §6 of OV-TEST-METHODOLOGY.
- **Protection scope:** DESAT local disable + soft turn-off per IGBT, OR'd FLT routing to main MCU and coprocessor, safe-state output, gate-driver UVLO behavior (recorded if practical).
- **Out of scope:** mid-operation short injection (LIMIT-10), shoot-through injection between phase legs, bus voltages above 140 V, and TSD (thermal shutdown) triggering — covered by thermal campaigns.

## Bench setup & preconditions

Per methodology §1, adapted for a fault-injection bench:

- **DUT:** Gen7 control module + C2 power stage; thermal interface state recorded; firmware graph + hash logged.
- **Pre-faulted fixture:** [FILL: fixture design — shorted phase leg via bolted/low-inductance short, switched by a contactor so the fault is applied before energize].
- **DC supply:** current-limited bench supply, [FILL: supply model and current limit], setpoint ≤140 V for this campaign.
- **Machine:** [FILL: machine and its thermal limit, if the fault leg is machine-coupled rather than bench-shorted].
- **Instrumentation:** high-sample-rate oscilloscope on DESAT pin, gate-emitter, and FLT lines (differential, rated for the bus class); RTE Studio telemetry; TI250-class imager for post-event inspection.
- **Safety:** a hard short on an energized inverter stores destructive energy. All personnel safety interlocks (emergency stop, discharge path, exclusion zone, PPE) must be documented before the first shot; the supply current limit and ≤140 V cap are mandatory preconditions; verify DC-link discharge to a safe voltage before touching the fixture between shots.
- **DC-link capacitance (transfer-critical):** the DC-link capacitors are the fault energy source — E ≈ ½·C·V². Record total capacitance and bus voltage for every shot. Results do **not** transfer to another voltage class or a significantly different capacitance without re-validation or an explicit energy-bound argument (methodology, "Component stress by archetype").

## Procedure

1. **Fixture checkout:** verify the shorted leg's impedance and the contactor operation with the DUT unpowered; record fixture identifiers and the current-limit setting. Capture: fixture photos, short impedance measurement.
2. **Baseline:** power the DUT with the fault contactor open; confirm clean boot, no fault flags, and normal gate waveforms. Capture: boot log, baseline gate/DESAT scope traces.
3. **Pre-charge and arm:** close the fault contactor to apply the pre-fault; set the supply to ≤140 V with the current limit active; confirm the DUT is commanded to a defined energize state (per [FILL: energize command/state]). Capture: supply settings screenshot.
4. **Energize into fault:** apply bus power; the DESAT chain must trip locally. Capture at high sample rate: DESAT pin voltage vs the 6.5 V threshold, gate-emitter during soft turn-off, phase current decay, and FLT line on both MCU paths.
5. **Record latency:** from the scope/telemetry timestamps, extract fault onset → DESAT assertion (**<2 µs** budget) and fault onset → hardware PWM disable (**<10 µs** budget). Capture: measurement screenshots with cursors.
6. **Safe-state verification:** confirm the OR'd FLT is received by the main MCU and the coprocessor and that the safe-state output is asserted within **≤200 ms**; record the FAULT flag words in telemetry. Capture: telemetry excerpt + flag dump.
7. **Post-event inspection:** with the bus discharged, inspect the faulted IGBT leg (imager pass, visual check) and power the DUT again at low bus to confirm it still boots and runs — the DUT must survive for post-test insulation/functional checks.
8. **UVLO check (if practical):** ramp the gate-driver supply down and up and record the UVLO trip thresholds against **12.2 / 11.3 V**. Capture: ramp plot with trip points.
9. **Repeat** steps 3–8 for [FILL: number of shots / repetitions per variant], cooling to ambient between shots.

## Measurements & acceptance criteria

| # | Criterion | Pass condition |
|---|-----------|----------------|
| 1 | DESAT detection latency | <2 µs from fault onset to local disable, per IGBT faulted |
| 2 | Hardware PWM disable | <10 µs (SG-12 budget) |
| 3 | Turn-off behavior | Soft turn-off observed; no destructive overshoot on VCE; active Miller clamp active; DUT undamaged |
| 4 | FLT routing | OR'd FLT asserted at both MCUs; SSO within ≤200 ms of fault |
| 5 | Fault flags | Correct FAULT flag word recorded in telemetry for the faulted leg |
| 6 | DUT health | DUT survives; post-test insulation/functional check passes |
| 7 | UVLO thresholds | 12.2 / 11.3 V verified, or deviation noted as an observation with measured values recorded for ratification |

Where a value is pending definition at the safety-requirement level (e.g. final UVLO ratification thresholds), the test records the measured values and flags them for ratification rather than asserting compliance.

## Evidence package

Per methodology §5, the resulting Test Report must include:

- Report sections: Test setup, Test conditions (table), Procedure, Electrical results, Observations, Conclusion, Artifacts.
- Telemetry overview plot in the standard 5-panel layout (Iq; DC-link power; machine-terminal P and Q; baseplate NTCs with ambient reference; bus voltage) — for this protection test annotated with the fault-onset marker.
- Full-rate session log + 1 Hz decimated log, decimated log linked in the Telemetry Viewer.
- High-sample-rate scope captures: DESAT vs 6.5 V threshold, gate soft turn-off, FLT both paths, current decay.
- Photos: fixture, contactor/short assembly, post-event DUT inspection, imager passes with crosshair/max readings.
- Naming and doc_id per the Testing naming convention in Docs/Agents.md.

## Execution record

To be filed as a sibling Test Report under `Docs/Safety-and-Compliance/Testing/Hardware/` referencing this plan by doc_id `OV-TEST-HW-DESAT-SHORT`; test ID assigned at execution.
