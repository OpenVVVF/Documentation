---
doctype: Test Plan
doc_id: OV-TEST-VIB-PLAN
title: Vibration Test Plan
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.3"
date: "2026-08-20"
description: Vibration test plan for the C2 inverter assembly based on MIL-STD-810H Method 514.8 Category 4 wheeled-vehicle random vibration, with a low-cost screening alternative.
nav_order: 372
normative_refs:
  - OV-SAF-HARA-CORE
  - OV-TEST-FAULT-INJECTION
---

# Vibration Test Plan

This document is the vibration test plan for the OpenVVVF C2 inverter assembly (control module plus C2 power stage, hard-mounted as one test article). It is written for the C2 chassis but is intended to be reusable for other chassis by substituting the applicable mounting and mass data.

Per the evidence framework shared with the fault-injection plan ([OV-TEST-FAULT-INJECTION](../Fault-Injection-Test-Plan/Index.md)), this plan is a living document; each execution campaign produces a separate dated `Test Report` document filed as a sibling of this plan, referencing it by doc_id and test ID.

## Purpose and scope

Verify that the C2 power-stage and control assembly survive road-induced random vibration without mechanical or electrical degradation. Specifically, the test shall demonstrate:

- No fastener loosening, verified by torque witness marks.
- No connector back-out or terminal fretting.
- No harness chafing, fretting, or insulation damage.
- No PCB damage. The large DC-link capacitors are the heaviest and tallest components on the power board and are the primary at-risk items for lead/terminal fatigue and board flexure damage.
- No solder-joint fatigue cracking on through-hole and heavy SMT components.
- Gate-drive and current-sense harness integrity (crimp retention, shield continuity).
- Unchanged pre/post electrical function (continuity, gate-drive function at low voltage, insulation resistance).

## Normative basis

- MIL-STD-810H, Method 514.8 (Vibration), Category 4: composite wheeled vehicle vibration exposure. Category 4 applies to materiel transported by or installed in wheeled vehicles traversing highways and cross-country terrain; it is the appropriate category for a road-vehicle traction inverter.
- The following installation considerations shall be folded into the fixture and profile selection:
  - Mounting orientation in the vehicle is often not horizontal; the worst-case axis assignment shall follow the actual vehicle installation.
  - A specific vehicle installation may exceed Category 4 composite wheeled-vehicle levels (for example where the assembly is mounted to unsprung or lightly-damped structure, or where engine orders add narrowband content on top of the random road profile). If so, the installation shall be measured and the profile tailored from the measured data rather than relaxed below Category 4.

The qualification profile and the screening profile are defined in the Vibration profiles section below; verify all values against the current standard before test as noted there.

## Test item description

The test item is a complete, representative C2 assembly:

- C2 power-stage chassis with power board, DC-link capacitors, busbar/terminal hardware, heatsink, and enclosure covers.
- OpenVVVF control module installed in its production position.
- Production gate-drive and current-sense harnesses, routed and clamped as in the vehicle installation.
- All external connectors mated, with either production mating halves plus short harness pigtails or production-equivalent test cables.
- Fasteners torqued to production specification and marked with torque witness paint/lacquer before test.

The assembly shall be production-representative in mass and center of gravity. Any missing vehicle-side masses (motor cabling, coolant, contactor box) shall be noted in the test report.

## Mounting and fixturing

- Mount the assembly to the fixture using the same hard-mount scheme as the vehicle installation: same mounting points, same fastener class, same torque, same interface stiffness (no rubber isolation unless the vehicle uses it).
- The fixture shall be rigid across the test bandwidth: up to at least 500 Hz plus margin for a Category 4 qualification run, and up to at least 2000 Hz if the minimum-integrity screening profile below is used. Its first resonance shall be above the applicable test bandwidth or well damped. A welded or thick-plate machined fixture is acceptable.
- Orientation shall match the vehicle installation attitude; record the attitude used.
- The fixture shall bolt to the shaker head or slip table at enough points to avoid fixture rocking modes.

## Instrumentation

- Control accelerometer on the fixture at the shaker interface (closed-loop control channel).
- Response accelerometer on the assembly, mounted on the power board near the DC-link capacitor bank (highest-mass region) or on the chassis wall adjacent to it.
- Optional third accelerometer on the control module for board-level response.
- Torque witness marks on all structural and electrical fasteners, inspected before, between axes, and after test.
- Photographic record: full assembly, each mounting point, each connector, harness routing, and any anomaly, before and after each axis.
- Pre/post electrical checks:
  - Continuity of gate-drive, current-sense, and low-voltage harnesses (pin-to-pin).
  - Gate-drive function at low voltage (bench power supply, gate-drive self-test or low-voltage switching check per existing bring-up practice).
  - Insulation resistance between DC bus and chassis at 500 VDC megohmmeter, before and after test.

## Vibration profiles

### Qualification profile: MIL-STD-810H Category 4 composite wheeled vehicle

A lab qualification run to Category 4 uses the per-axis random-vibration spectra published in MIL-STD-810H Method 514.8: Figure 514.8C-6 and Table 514.8C-VII (composite wheeled vehicle vibration exposure) for known mounting orientation, or Figure 514.8C-7 and Table 514.8C-VIII where the orientation is unknown. The spectra span 5 to 500 Hz; the vertical-axis envelope is approximately 2.24 g RMS, with the transverse and longitudinal axes at lower levels per the published tables. The breakpoint values shall be taken from those tables in the current revision of the standard; they are not reproduced here. (Note: Figure 514.8C-1 is the transportation-scenario duration guidance, not a spectrum.)

### Minimum-integrity screening profile (per axis)

For a general workmanship screen where a full Category 4 run is not yet planned, the following minimum-integrity-style profile may be used. This table is not the 810H Category 4 spectrum; it is a generic minimum-integrity exposure of the kind historically published in MIL-STD-810 for general robustness screening, and it extends to 2000 Hz, unlike Category 4.

Random vibration, acceleration spectral density (ASD) breakpoints:

| Frequency (Hz) | ASD (g^2/Hz) |
|----------------|---------------|
| 10 | 0.015 |
| 40 | 0.015 |
| 500 | 0.00015 |
| 2000 | 0.00015 |

Overall level: approximately 1.04 g RMS. Straight-line segments on log-log axes between breakpoints.

> **Verify against the current standard before test.** The screening table above is a general minimum-integrity-style profile, not the Category 4 spectrum. Before any formal run, confirm the applicable figure and table numbers and breakpoint values against the current MIL-STD-810H (Figure 514.8C-6 / Table 514.8C-VII, or C-7 / C-VIII for unknown orientation), and record the revision used in the test report.

### Duration

- Minimum screening duration: 1 hour per axis, all three orthogonal axes (3 hours total). This is a workmanship/infant-mortality screen, not a life demonstration.
- The standard's full-life durations for Category 4 are derived from the vehicle life-cycle exposure (Method 514.8 defines duration from expected service time and transport scenario; typical composite wheeled-vehicle exposures run several hours per axis). For a qualification claim, compute the duration from the application profile's service life and record the derivation in the test report.

### Axes

All three orthogonal axes shall be tested. Axis assignment shall follow the vehicle installation: vertical, lateral, and longitudinal as installed in the vehicle. Record the assignment in the test report.

## Low-cost screening without a shaker

A meaningful screen can be run without an electrodynamic shaker, but its claims are limited.

Options:

- **Mechanical vibration table / low-cost modal shaker:** A cam-driven or unbalanced-motor table can deliver broadband-ish excitation. Instrument with a response accelerometer and log the achieved ASD; accept that control is open-loop and the spectrum is not shaped.
- **Road simulation:** Bolt the instrumented assembly (with a data-logging accelerometer) to a test vehicle or trailer and drive a fixed rough-road circuit (washboard, potholes, cobble/gravel) for a defined number of laps. Record time and route; repeat identically for each build.
- **Repetitive shock / drop table:** Not a substitute for random vibration; usable only as a coarse robustness check.

What a low-cost screen can claim:

- Workmanship screening: loose fasteners, connector back-out, harness chafing, and grossly under-supported heavy components (DC-link capacitors) are found reliably by any sustained broadband excitation combined with witness marks and pre/post electrical checks.
- Comparative screening between builds or design iterations run on the same rig.

What it cannot claim:

- Compliance with MIL-STD-810H Method 514.8. Only a closed-loop shaker run reproducing the applicable Category 4 spectrum (Figure 514.8C-6 / Table 514.8C-VII) within tolerance supports that claim.
- Fatigue-life equivalence, since uncontrolled spectra over- or under-test specific resonances.

A low-cost screen shall be reported as a screen, with the achieved measured spectrum (if available) attached to the test report.

## Procedure

1. **Pre-test inspection:** Photograph assembly, verify torque witness marks on all fasteners, verify connectors fully seated and locked, inspect harness clamping. Run pre-test electrical checks (continuity, gate-drive function at low voltage, insulation resistance) and record results.
2. **Installation:** Mount the assembly on the fixture per the Mounting section. Install control and response accelerometers. For closed-loop shaker runs, perform a low-level (0.25 g RMS) signature run to check the control loop and identify fixture/assembly resonances; record the response spectrum. This step does not apply to open-loop low-cost rigs.
3. **Per-axis runs:** Run the full profile for the planned duration on axis 1. Repeat for axes 2 and 3. If a lab shaker is used, maintain ASD within the standard's tolerance bands; if a low-cost rig is used, log the achieved spectrum continuously.
4. **Inspection intervals:** After each axis, and at least every hour for multi-hour runs: visual inspection of fasteners/witness marks, connectors, harnesses; listen for rattles; check response accelerometer data for resonance shifts (a shifting resonance indicates developing damage). Any anomaly pauses the test for evaluation.
5. **Post-test teardown inspection:** Full photographic record, witness-mark inspection, connector pin inspection for fretting debris, close visual (magnified) inspection of DC-link capacitor terminals and solder joints, harness flex/insulation inspection at clamp points. Run post-test electrical checks identical to pre-test.

## Acceptance criteria

The test item passes if and only if all of the following hold:

1. No fastener torque witness mark shows rotation or breakage.
2. No connector shows back-out, partial unlatching, or terminal fretting debris.
3. No harness shows chafing, insulation breach, or clamp displacement.
4. No PCB crack, pad lift, or solder-joint crack is found on visual (magnified) inspection, in particular at the DC-link capacitor terminals.
5. Gate-drive and current-sense harness continuity is unchanged from pre-test values.
6. Post-test gate-drive function check at low voltage passes identically to pre-test.
7. Post-test insulation resistance (500 VDC, DC bus to chassis) meets the specified minimum (specify value, e.g. 10 Mohm at 500 VDC; the assembly specification must define this value). Because insulation resistance varies with temperature and humidity, any decrease beyond measurement scatter relative to the pre-test value shall be dispositioned by engineering review.
8. No new resonances or resonance shifts greater than 5 percent in frequency appear in the response spectra between the pre-test signature run and the post-test condition.

## Failure definitions

- **Mechanical failure:** any item failing acceptance criteria 1 to 4, or any loose part, crack, or deformation found at inspection.
- **Electrical failure:** any item failing acceptance criteria 5 to 7, or any intermittent observed during the run (if the assembly is powered or monitored during test).
- **Indication of incipient failure:** a resonance shift under the 5 percent threshold, witness-mark creep without full rotation, or fretting discoloration without debris; these are dispositioned by engineering review and recorded in the test report even when the overall result is pass.

Any failure stops the campaign; the failed article is quarantined for teardown analysis, and the failure is linked to the affected HARA failure modes before retest.

## Traceability

- HARA Core ([OV-SAF-HARA-CORE](../../HARA/Core/Index.md)): vibration-related mechanical failure modes connect to the HARA wherever Functional Safety Requirements rely on connectors, harnesses, and sensor wiring remaining intact, for example torque-command plausibility, current-sense integrity, and gate-drive command paths. A vibration-induced open or short on these interfaces is a credible initiator for the corresponding hazards; this plan provides the environmental evidence that those interfaces survive the road environment.
- Fault-Injection Test Plan ([OV-TEST-FAULT-INJECTION](../Fault-Injection-Test-Plan/Index.md)): the E-series environmental cases are the closest relatives of this plan, in particular E-01 (random vibration, currently deferred as a type test). **Discrepancy note:** E-01 is currently specified to ISO 16750-3 (10 to 1000 Hz, 5 g RMS, 8 h/axis), a different standard at a substantially higher level than the Category 4 profile used here. The governing standard and level shall be reconciled when the E-series is executed; this plan's fixture and instrumentation still apply regardless of which spectrum is chosen. Note also that fault-injection case C-02 (tractive-effort control channel shorted to +5 V rail) exercises the harness-chafing fault mode electrically at the bench; this vibration plan addresses the mechanical initiator (chafing/fretting) that produces such faults in the field. E-series tests remain deferred and shall not be cited as coverage for any Safety Goal, FSR, or hazard until executed.

## Test record and evidence expectations

Consistent with the existing testing documents:

- Each execution campaign produces a dated `Test Report` document (doctype `Test Report`), filed as a sibling of this plan under `Testing/`, referencing this plan by doc_id and test ID, with `normative_refs` including `OV-TEST-VIB-PLAN`.
- The report shall record: test item serial/configuration, fixture description, accelerometer locations, achieved ASD plots or low-cost rig logs, duration per axis, witness-mark and inspection photographs, pre/post electrical measurements, anomalies and dispositions, and a pass/fail statement against the numbered acceptance criteria.
- Reports are immutable once released; corrections are issued as a new version referencing the original.
