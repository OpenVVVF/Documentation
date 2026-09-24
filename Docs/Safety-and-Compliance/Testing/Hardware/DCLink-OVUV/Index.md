---
doctype: Test Plan
doc_id: OV-TEST-HW-DCLINK-OVUV
title: DC-Link Overvoltage / Undervoltage Protection
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-09-24"
description: Validates SG-10 bus-voltage protection — regen disable on OV warning, safe state within 50 ms on critical OV, and defined UV behavior (FSR-21 thresholds currently undefined — this test records them).
nav_order: 387
placeholder: true
normative_refs:
  - OV-TEST-METHODOLOGY
  - OV-TEST-COVERAGE
  - OV-TEST-FAULT-INJECTION
---

# DC-Link Overvoltage / Undervoltage Protection

Test archetype **D — protection validation** per [OV-TEST-METHODOLOGY](../../Test-Methodology/Index.md) §4: one protection chain is exercised deliberately, and the DUT must respond; a non-response is a fail.

## Purpose & safety traceability

This test validates **SG-10 (ASIL B, H-10)**, DC-link overvoltage / undervoltage as an hazardous-energy hazard driver:

- **FSR-11 — isolated ADC bus monitoring:** on an **OV warning** the inverter must disable regen immediately (no regen current above the warning threshold); on a **critical OV** the inverter must reach its **safe state (gate-off / SSO) in < 50 ms** from the threshold crossing.
- **FSR-21 — undervoltage:** on UV the inverter must derate, and on **critical UV** it must reach a safe state. The thresholds are currently **Planned / undefined** — this test measures and records candidate values for FSR-21 ratification; it asserts transition behavior, not specific numbers.

**No prior evidence exists.** All regen runs to date (100 A through 450 A, including the 300 A steady-state report in this folder) ran with the bus externally clamped by the Chroma load bank in CV mode, so the bus never approached OV or UV and these chains were never exercised. This test closes that gap and complements the SG-10 evidence expected from [OV-TEST-FAULT-INJECTION](../../Fault-Injection-Test-Plan/Index.md).

**Caveat:** FSR-21 firmware thresholds and derate behavior are still being defined. Execution of §Procedure step 7 (UV characterization) is blocked until a firmware build with candidate UV thresholds is available; the OV portion (steps 1–6) can proceed with any recent build.

## Scope

DUT: Gen7 control module on the C2 chassis. Bus classes and execution parameters come from the variant matrix in [OV-TEST-METHODOLOGY](../../Test-Methodology/Index.md) §6; this campaign fills only:

- **DUT variant:** [FILL: chassis / bus class — 450 V class expected; record 200 V-class result separately if executed]
- **CV ramp rates:** [FILL: dV/dt for the OV upward ramp and UV downward ramp, V/s]
- **Candidate UV thresholds:** [FILL: UV derate onset and critical UV candidate values, V]

Out of scope: fault injection on the ADC chain (covered by OV-TEST-FAULT-INJECTION); ceiling/floor temperature and supply-variation campaigns (reserved in methodology §7).

## Bench setup & preconditions

Per [OV-TEST-METHODOLOGY](../../Test-Methodology/Index.md) §1, with variant-specific items as [FILL] placeholders:

- **DUT:** Gen7 control module + C2 power stage; thermal interface state recorded (paste lot/thickness or "dry"); firmware graph + hash logged in the report. Variant: [FILL: 450 V-class bus hardware, or 200 V class].
- **Machine:** [FILL: dynamometer-coupled machine, pole count and resistance from FRAM config]; machine thermal limit identified before the run (datasheet or imager-based) — [FILL: limit value and monitoring method].
- **DC supply / sink:** bench supply with regen sink, plus a Chroma / CV load bank as the **bus controller** — the load bank, not the inverter, sets the bus voltage in this test. Arrangement: [FILL: e.g. supply + Chroma CV across the link for 450 V class].
- **Current measurement:** probes rated ≥ 1.25 × peak expected phase current.
- **Telemetry:** full-rate session log + 1 Hz decimated log + overview plot, per methodology §1.
- **DC-link capacitance:** use the production-representative DC-link capacitance for the class under test. OV overshoot and UV ride-through dynamics scale with total C — protection-logic thresholds transfer across capacitance changes, dynamic behavior does not (methodology, "Component stress by archetype"). Record the fitted capacitance in the report.
- **Personnel / equipment safety:** the bus is ramped to and above nominal, up to the **450 V class** — lethal-energy territory. Verify discharge-verified access procedure, insulated tools, and meter rated for the bus class before energizing; confirm the load bank is rated for the full regen power at the highest bus setpoint. A critical-UV or critical-OV SSO dumps machine-side energy — keep the shaft speed and regen current moderate (see procedure) and confirm the dyno braking arrangement before starting. Confirm the bus clamp / bleeder path is functional before any hands-on work.

**Preconditions:** clean boot with no active faults; `gate_fault = 0`; telemetry logging verified live; machine thermal limit recorded; candidate FSR-21 thresholds programmed in the firmware build (for step 7).

## Procedure

1. Configure the load bank in CV mode as the bus controller at nominal bus setpoint; power the DUT; confirm clean boot (`RUNNING`, no faults, `gate_fault = 0`). Capture boot state.
2. Spin the machine on the dynamometer to moderate speed; confirm current orientation with an `IqVar = −25 A` jog (staircase orientation jog per methodology §2). Capture the jog.
3. Establish regen at a moderate current ([FILL: current command, within machine thermal limit]) against the load bank CV setpoint; hold until the operating point is stable (hold definition per methodology §2). Capture Iq, DC-link power, and bus voltage at the hold.
4. **OV warning ramp:** ramp the load-bank CV setpoint upward at [FILL: ramp rate] through the FSR-11 OV warning threshold. Capture the threshold-crossing timestamp, the regen-disable flag transition, and the regen current immediately before/after.
5. **Critical OV ramp:** continue ramping upward through the critical OV threshold until SSO. Capture the threshold-crossing timestamp, the gate-off timestamp, the fault flag word, and measure SSO latency as time from critical-threshold crossing to gate-off. Let the DUT cool down per methodology §4 (post-event cooldown); verify the DUT is reusable afterward.
6. Re-establish the nominal operating point and confirm normal regen operation resumes (auto-recovery expectation per methodology §7).
7. **UV ramp:** ramp the load-bank CV setpoint downward at [FILL: ramp rate] through the candidate UV derate threshold and the critical UV threshold. Capture the threshold-crossing timestamps, the point at which derate engages, the point at which the safe state engages, and the fault flag words at each transition. Record the measured thresholds for FSR-21 ratification.
8. End of test: return the bus to a safe discharged state, stop logging, and archive the full-rate and decimated logs.

**Stop criteria** (priority order per methodology §2): any protection trip other than the one under test (investigate before continuing); machine thermal limit; operator stop. A stop on the machine limit with the DUT stable is a valid, reportable outcome — record the reason and DUT state.

## Measurements & acceptance criteria

| # | Criterion | Pass condition |
|---|-----------|----------------|
| 1 | OV warning → regen disable | Immediate regen disable at the warning threshold; **no regen current above threshold** after crossing |
| 2 | Critical OV → SSO | Gate-off within **50 ms** (budget < 50 ms from threshold crossing to gate-off, FSR-11) |
| 3 | UV transitions | Derate at candidate UV threshold and safe state at candidate critical UV threshold are both recorded; measured values documented for FSR-21 ratification — numeric thresholds are **not** asserted as pass/fail in this plan |
| 4 | Flag words | Correct fault flags asserted at each transition (warning, critical OV, UV derate, critical UV), captured verbatim in the report |
| 5 | Recovery | DUT resumes normal regen operation after cooldown without degradation (methodology §7 functional-performance expectation) |

P/Q/PF/efficiency quantities (methodology §3, peak-amplitude convention; Q = (3/2)·(vq·id − vd·iq) quoted as magnitude) are calculated over the step-3 hold for the report's electrical results; steady-state confirmation (|dT/dt| ≤ 0.1 °C over any 5-minute window) is not required for this archetype but may be noted if a hold is held that long.

## Evidence package

Per [OV-TEST-METHODOLOGY](../../Test-Methodology/Index.md) §5:

- Test Report filed under `Docs/Safety-and-Compliance/Testing/Hardware/` with the standard sections (Test setup, Test conditions table, Procedure, Electrical results, Telemetry overview, Observations, Conclusion, Artifacts).
- Telemetry overview plot in the standard 5-panel layout: Iq; DC-link power; machine-terminal P (kW) and Q (kvar); baseplate NTCs with ambient reference; bus voltage — the bus-voltage panel is the primary evidence for this test.
- Full-rate session log + 1 Hz decimated log; decimated log linked in the Telemetry Viewer.
- Photos: bench arrangement including the load bank, scope capture of SSO latency (if measured electrically), and any post-event state photos.
- Measured FSR-21 threshold values recorded in the report and referenced in the FSR-21 requirement document for ratification.
- Naming and doc_id per the Testing naming convention in `Docs/Agents.md`.

## Execution record

To be filed as a sibling Test Report referencing this plan by doc_id (OV-TEST-HW-DCLINK-OVUV); test ID assigned at execution.
