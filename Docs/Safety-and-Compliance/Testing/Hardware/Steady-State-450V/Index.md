---
doctype: Test Plan
doc_id: OV-TEST-HW-STEADY-STATE-450V
title: 450 V Class Steady-State Thermal Campaign
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-09-24"
description: "Fill-in campaign plan for continuous-duty thermal validation of the 450 V class: staircase and steady-state holds mirroring the 200 V campaign (tests 17–19), per the methodology variant matrix."
nav_order: 389
placeholder: true
normative_refs:
  - OV-TEST-METHODOLOGY
  - OV-TEST-COVERAGE
  - OV-TEST-THERMAL-PLAN
---

# 450 V Class Steady-State Thermal Campaign

This is a fill-in test plan: execution parameters marked [FILL: ...] are assigned per campaign before the run, per the variant parameter matrix in methodology [OV-TEST-METHODOLOGY](../../Test-Methodology/Index.md) §6. It follows **archetype A (steady-state thermal hold)** of methodology §4.

## Purpose & safety traceability

This campaign validates **SG-07** (detect over-temperature, progressively derate; critical temperature → safe state, ASIL B) and its technical requirement **FSR-08** for the 450 V DC-bus class: two IGBT NTC sensors (1oo2 voting) plus one DC-link capacitor NTC, **derate at 90 °C**, **SSO at 105 °C** on the capacitor channel (capacitor rating limit), **100 °C IGBT-module hard cap** on the module-sited NTC, with critical thresholds stored in ECC.

It complements the existing 200 V-class evidence: the SG-07 row in [OV-TEST-COVERAGE](../../Test-Coverage-Checklist/Index.md) cites tests 17–19 (200 V steady-state thermal runs) as the steady-state data below derate, while the **450 V column of methodology §6 is entirely [FILL]**. This campaign supplies that column: plateau and ΔT-over-ambient data demonstrating the 450 V-class thermal design operates below the 90 °C derate with margin, as the 200 V data did at ~39 K over ambient against the 80 °C trip. **Caveat:** existing real OT trips occurred at **~80 °C** baseplate, not the FSR-08 thresholds of 90 °C / 105 °C — an open reconciliation flagged in OV-TEST-COVERAGE and [OV-TEST-THERMAL-PLAN](../../Thermal-Test-Plan/Index.md) T-06. This campaign is **not** a threshold-validation test (that is archetype D / T-06 territory); no protection trip is expected or desired here, and stop criteria follow methodology §2 in priority order.

## Scope

- Chassis/bus-class variant: **Size 2 · 450 V class** per methodology §6. All §6 450 V parameters are [FILL] pending campaign assignment: [FILL: nominal 450 V-class bus setpoint], [FILL: supply+sink arrangement], [FILL: machine(s)], [FILL: machine thermal limit], [FILL: target current].
- Test mode: staircase to a target current followed by a steady-state hold (archetype A). Regen vs. motoring orientation is set at execution per the [FILL: supply+sink arrangement] and recorded in words, not just signs (methodology §2).
- Out of scope: OT-threshold validation (covered by [OV-TEST-THERMAL-PLAN](../../Thermal-Test-Plan/Index.md) T-06 and the fault-injection campaign), burst/capability runs (archetype B), endurance ≥ 20 min (archetype C), and 450 V over/undervoltage ceiling/floor variants (reserved in methodology §7).

## Bench setup & preconditions

Per methodology §1, with the 450 V-class variant items as [FILL] placeholders:

- **DUT:** Gen7 control module + C2 power stage, thermal interface state recorded (paste lot/thickness or "dry"); firmware graph + hash logged in the report. Note: the 450 V-class DC link retains hazardous charge after power-down — verify discharge before touching.
- **Machine:** dynamometer-coupled; pole count and resistance from FRAM config. **[FILL: machine and its thermal limit]** identified **before** the run (datasheet or imager-based). If the machine has no telemetry thermistor, it is TI250-monitored for the whole hold and the case temperature at any stop is recorded (200 V campaign lesson: the machine, not the inverter, ended the 300 A run at 86 °C case).
- **DC supply / sink:** **[FILL: supply+sink arrangement for the 450 V class]**. If expected regen current exceeds the supply's sink limit, a Chroma/load bank in CV mode across the link is mandatory (methodology §1). All 450 V-class wiring, probes, and connections must be rated for the [FILL: nominal 450 V-class bus] bus plus margin; treat the DC link as hazardous energy at all times — no live reconfiguration, discharge-and-verify before any change.
- **DC-link capacitors:** this campaign re-validates the DC-link capacitor bank for the 450 V class — voltage rating, ripple-current heating (imager cap-bank pass is mandatory), and the capacitor-NTC channel. 200 V-class steady-state evidence does not transfer (methodology, "Component stress by archetype"). Record fitted capacitance and voltage rating in the report.
- **Current measurement:** probes rated ≥ 1.25 × peak expected phase current (400 A run lesson: 150 A-rated clamps saturate and fabricate spikes).
- **Thermal measurement:** TI250-class imager for surface passes; baseplate NTCs via telemetry; **[FILL: ambient recording method]** — operator log or NTC-at-power-up + imager cold pixels marked *inferred* (methodology §1 requires ambient to be recorded).
- **Telemetry:** full-rate session log + 1 Hz decimated log + overview plot; decimated log linked to the Telemetry Viewer.
- **Personnel/equipment safety:** the 450 V bus and a short-circuit-capable DC link make this a hazardous-energy bench — HV gloves/insulated tools per existing bench practice, discharge-and-verify before reconfiguration, and never operate unattended during the hold.

## Procedure

1. Confirm preconditions: machine thermal limit documented ([FILL: machine and its limit]), bench supply and sink capability verified against the expected DC-link power at [FILL: target current] on a [FILL: nominal 450 V-class bus], all probes rated, ambient method in place ([FILL: ambient recording method]).
2. Power up and start control; confirm clean boot (no startup faults, `gate_fault` = 0) and record firmware graph + hash.
3. Spin the machine to the target speed on the dynamometer; perform the **orientation jog** of −10…−25 A and confirm the regen/motoring sign is as intended (methodology §2 staircase definition).
4. **Staircase** to [FILL: target current] in **25 A steps**, dwell per step ≥ 5 s and ≥ 2× current-loop settling time; capture current, bus voltage, and DC-link power at each step.
5. Hold the target current. The hold is defined as the operating point held within **±5 % of command or ±10 A, whichever is larger**; report average and min/max of the held current. Continue until **steady state is confirmed — |dT/dt| ≤ 0.1 °C over any 5-minute window** on the baseplate NTC, with the window completing while the operating point is still held — or until a stop criterion in priority order: any protection trip; machine thermal limit (imager-monitored if no thermistor, case temperature recorded at stop); operator stop (methodology §2).
6. Once plateau is confirmed, perform the **TI250 photo pass** over the baseplate and (if machine-limit-governing) the machine; record crosshair and spot-max readings.
7. Record the **plateau temperature** — mean of the baseplate NTC over the final 10 minutes of the hold — always quoted with ambient and as ΔT over ambient.
8. Compute and record all methodology §3 calculated quantities over the hold window with the peak-amplitude convention: P = (3/2)(vd·id + vq·iq), Q = (3/2)(vq·id − vd·iq) quoted **as magnitude**, |S| = √(P² + Q²), PF = |P|/|S|, and inverter efficiency η (regen: mean(P_DC-link) ÷ |mean(P_machine)|; motoring: inverted). Apply the §3 reconciliation requirement: machine-terminal P and DC-link P must imply a thermally plausible inverter loss; if they do not reconcile, do not publish P/Q/PF/η and add a data-quality observation with the firmware build.
9. Command zero current, then log **≥ 5 minutes of cooldown** with telemetry running; record baseplate and machine temperatures at the end of the cooldown.
10. An operator stop on a *machine* limit with the DUT stable is a valid, reportable outcome — record the reason and DUT state explicitly (methodology §2).

## Measurements & acceptance criteria

- **Steady state confirmed** per the methodology definition: |dT/dt| ≤ 0.1 °C over a completed 5-minute window under hold. A run that stops on the machine limit before the window completes is reportable but flagged as not reaching confirmed steady state.
- **Plateau and ΔT over ambient** reported: plateau = final-10-minute baseplate NTC mean, quoted with ambient; ambient recording method stated, *inferred* marked where applicable.
- **Hold quality:** held current within ±5 % / ±10 A band, with avg/min/max reported.
- **No faults:** no protection trip and no active fault flag at any point; `gate_fault` = 0 for the session; `cg_vlimit_scale` = 1.000 throughout. (Protection thresholds remain per the open FSR-08 reconciliation — firmware trips observed at ~80 °C vs. the 90 °C derate / 105 °C SSO / 100 °C hard cap — so this test records measured temperatures and behavior for ratification of that reconciliation rather than asserting the thresholds themselves.)
- **Efficiency reconciliation** per methodology §3: implied inverter loss thermally plausible against the observed baseplate rise; if not reconciling, P/Q/PF/η are withheld with a data-quality observation.
- **Machine limit respected:** machine case temperature at or below its documented limit at all times, and the limit value and monitoring method recorded in the report.
- **Data completeness:** §3 quantities, cooldown log ≥ 5 min, and the full evidence package below all present.

## Evidence package

Per methodology §5 (every power test):

- Test Report filed as a sibling under `Testing/Hardware/`, with sections: Test setup, Test conditions (table), Procedure, Electrical results, Thermal results, Telemetry overview, Observations, Conclusion, Artifacts.
- Conditions table: hardware + firmware hash, machine + speed, bus, current command + window, average held current (avg/min/max), DC-link power, §3 quantities (P, Q, |S|, PF, η where reconciling), ambient (recorded or *inferred*), thermal results.
- Telemetry overview plot, standard **5-panel layout**: Iq; DC-link power; machine-terminal P (kW) and Q (kvar); baseplate NTCs with ambient reference; bus voltage.
- Full-rate session log + 1 Hz decimated log; decimated log linked in the Telemetry Viewer.
- Photos per archetype A: bench, thermal passes with crosshair/max readings, machine thermal image if limit-governing.
- Naming and doc_id per the Testing naming convention in [Docs/Agents.md](../../../../Agents.md).

## Execution record

To be filed as a sibling Test Report referencing this plan by doc_id `OV-TEST-HW-STEADY-STATE-450V`; the test ID is assigned at execution.
