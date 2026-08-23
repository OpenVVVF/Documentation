---
doctype: Test Plan
doc_id: OV-TEST-THERMAL-PLAN
title: Thermal Test Plan
product_line: openvvvf
applies_to:
  - chassis-size-2
version: "1.3"
date: "2026-08-23"
description: Bench thermal validation of the C2 inverter using a thermal chamber built from a styrofoam cooler; verifies the heatsink and DC-link thermal design claims and the FSR-08 derate/SSO thresholds.
nav_order: 373
normative_refs:
  - OV-C2-DD-THERMAL
  - OV-C2-DD-DCLINK-THERMAL
  - OV-SAF-HARA-CORE
  - OV-TEST-FAULT-INJECTION
---

# Thermal Test Plan

This document is the thermal test plan for the Chassis Size 2 (C2) traction inverter. It defines test cases that can be executed with a thermal chamber built from a styrofoam cooler, plus standard bench instrumentation. It verifies the thermal design claims made in the C2 design documents [OV-C2-DD-THERMAL](../../../Hardware/Power-Stages/C2/Design-Documents/Thermal-Analysis/Index.md) and [OV-C2-DD-DCLINK-THERMAL](../../../Hardware/Power-Stages/C2/Design-Documents/DC-Link-Thermal/Index.md), and the temperature derate / safe-state-off (SSO) thresholds of FSR-08 in [OV-SAF-HARA-CORE](../../HARA/Core/Index.md).

This plan is filed directly under `Testing/` because it spans the Hardware domain (physical thermal characterization of the power stage) and firmware behavior verification (derating, SSO, NTC telemetry). The DUT is the C2 power stage; the control module is not under test here, but it supplies the firmware NTC telemetry (two IGBT NTCs, one DC-link capacitor NTC) that T-02 through T-06 correlate against the reference probes. Test execution records and evidence are maintained separately per the same evidence framework as [OV-TEST-FAULT-INJECTION](../Fault-Injection-Test-Plan/Index.md): each execution campaign produces a dated `Test Report` document filed as a sibling of this plan, referencing it by doc_id and test ID. Evidence reports are immutable once released; this plan's status tables are the living roll-up.

## Purpose and Claims Under Verification

| ID | Claim / behavior | Source | Test(s) |
|----|------------------|--------|---------|
| CLM-1 | Required heatsink thermal resistance $R_{th(s-a)} \le 0.0141$ K/W at the 600 A (424 A RMS) / 320 V / 2 kHz reference point and $\le 0.0095$ K/W at 600 A / 320 V / 6 kHz (design target 0.007 K/W with margin at 6 kHz); $\le 0.0139$ K/W at the 465 A (330 A RMS) / 320 V / 6 kHz continuous rating point (values per OV-C2-DD-THERMAL v1.3, $R_G = 2.7 \ \Omega$; 600 A is the 60 s peak duty, continuous rating is 465 A per OV-C2-DD-THERMAL v1.3 §6.4) | OV-C2-DD-THERMAL | T-04 |
| CLM-2 | DC-link spreader plate rises approximately +32.4 K over the heatsink base at 40 W capacitor heat load (with thermal paste, rev-B 6.35 mm plate); ~72 C plate at 40 C heatsink base | OV-C2-DD-DCLINK-THERMAL | T-05 |
| CLM-3 | Firmware derates at 90 C and enters SSO at 105 C on the DC-link capacitor NTC channel (FSR-08; capacitor rating limit) | OV-SAF-HARA-CORE (FSR-08) | T-06 |
| CLM-4 | IGBT NTC channels (two sensors, 1oo2 voting per FSR-08; 100 C hard cap on the module-sited NTC per OV-C2-DD-THERMAL) track the reference probes and behave plausibly over temperature | OV-SAF-HARA-CORE (FSR-08), OV-C2-DD-THERMAL | T-02, T-03, T-06 |
| CLM-5 | Temperature-sensor accuracy: firmware NTC readings agree with calibrated reference probes within the stated tolerance across the operating range | this plan | T-01, T-02, T-03 |

Where a design-doc number is an unvalidated estimate, that is stated explicitly in the acceptance criteria. In particular, OV-C2-DD-THERMAL is marked "design estimate ... to be validated by test" and the DC-link +40.1 K rise is a 1-D analytical result with a stated ±20 % spreading uncertainty.

## Test Chamber

### Construction

The chamber is a rigid styrofoam (EPS/XPS) picnic cooler, used lid-on, with the following modifications:

1. **Heater.** A resistive heat source inside the chamber: either two to four chassis-mount power resistors (e.g. 50 W aluminum-housed resistors on a small aluminum plate) driven from a bench supply, or a cartridge heater in an aluminum block. The heater assembly is mounted on a metal stand so that no part of the heater or its mounting plate touches the styrofoam wall; minimum 50 mm clearance to any styrofoam surface. Styrofoam softens near 100 C and ignites at much higher temperature, but local hot spots from direct contact can melt it well below that.
2. **Control.** A simple bang-bang (on/off with hysteresis) controller or a PID controller switching the heater through a relay or SSR, using one of the chamber air-temperature probes as feedback. Bang-bang control with 1-2 K hysteresis is sufficient for the soak tests in this plan.
3. **Air circulation.** A small 12 V fan (80 mm PC fan or similar) inside the chamber, running continuously during all tests, hot and cold, to keep air temperature uniform. Without forced circulation, stratification of 10 K or more is typical and invalidates the measurements; ice packs stratify just as badly as the heater.
4. **Cooling for cold tests.** Ice packs or frozen water bottles placed inside the chamber (in a tray to catch condensation) pull the chamber down toward 0 C. There is no active refrigeration; lower temperatures are achievable only transiently (see Limitations).
5. **Feedthroughs.** Probe wires and the DUT harness exit through a small slit in the lid gasket, taped closed. Keep the opening small to limit leakage.
6. **DUT support.** The DUT (or the heatsink assembly under test) sits on a raised insulating grid so air circulates on all sides.

### Safety limits (mandatory)

- **Maximum chamber temperature: 80 C air temperature, hard limit.** This is below the styrofoam softening region with margin, and above the highest test point required by this plan (60 C chamber soak; FSR-08 thresholds are reached by local probe heating where needed). The controller shall have an independent over-temperature cutout set at 80 C chamber air temperature.
- **Thermal fuse cutout (backup layer):** a one-shot thermal fuse (94-104 C class, 10 A) wired in series with the heater, sensing chamber air or the DUT-side plate (mounted in the air stream near the DUT). It is the last-resort backup above the 80 C controller cutout. Do not bond the fuse to the heater mounting plate: the heater plate is the hottest surface in the chamber, sits above 80 C in normal operation, and would nuisance-blow the fuse long before the air limit is reached. A blown fuse requires manual replacement; it is not a resettable thermostat.
- **Mains/wiring fuse:** the heater circuit shall be fused for the chosen heater option. Guidance: a 12/24 V cartridge heater at 100-200 W implies roughly a 5-15 A class fuse; power-resistor heaters on a bench supply are limited by the supply's own current limit. Size the fuse for the actual option wired up.
- **Never operate unattended.** The chamber shall be supervised whenever the heater is energized.
- **Keep styrofoam away from heater surfaces.** Maintain the 50 mm clearance; shield any radiant line-of-sight from heater to wall with a thin aluminum sheet if the geometry is tight.
- No flammable materials (solvents, loose paper) inside the chamber during hot tests.
- For tests on the energized DUT, follow the HV safety practices of the existing bench procedures; the chamber adds no exemption.

### Chamber BOM (rough prices)

| Item | Specification | Qty | Rough price (USD) |
|------|---------------|-----|-------------------|
| Styrofoam cooler | ~25-50 l EPS/XPS chest cooler | 1 | 10-30 |
| Power resistors, aluminum housed | 50 W, e.g. 10 ohm, chassis mount | 4 | 15-25 |
| (alternative) Cartridge heater | 12/24 V, 100-200 W, in aluminum block | 1 | 10-20 |
| Aluminum plate/scrap | heater mounting and radiant shield | 1 | 5-10 |
| Relay or SSR + controller | bang-bang thermostat module or PID (e.g. cheap PID + 25 A SSR) | 1 | 10-30 |
| Thermal fuse | 94-104 C class, 10 A, one-shot | 2 | 2-5 |
| Fan | 80 mm 12 V DC fan + grill | 1 | 5-10 |
| 12 V / heater supply | bench supply or fixed PSU sized for heater | 1 | 0-40 (often on hand) |
| Ice packs / frozen bottles | for cold tests | 4-6 | 5-15 |
| Fuses, wire, terminals, tape | - | - | 5-10 |
| **Total** | | | **~60-190** |

## Instrumentation

### Measurement points

| Probe ID | Location | Purpose |
|----------|----------|---------|
| P-AMB | chamber air, mid-height, away from heater discharge | chamber control and ambient reference |
| P-HS | heatsink base, under the center IGBT module footprint | heatsink base temperature $T_s$ |
| P-IGBT | IGBT module case/baseplate edge (co-located with the module NTC where accessible) | correlation against firmware IGBT NTC channels |
| P-CAP | DC-link capacitor can top (hottest expected point of the can) | capacitor temperature, FSR-08 channel correlation |
| P-PLT | DC-link aluminium spreader plate, mid-plate | plate temperature for the +40.1 K rise check |

Thermocouples (type K or T) with a multi-channel logger, or digital temperature probes (e.g. DS18B20-class on a logger), are both acceptable. Attach probes with thermally conductive adhesive or tape plus a dab of thermal compound; insulate the probe bead from chamber air with a small pad of foam tape so the probe reads the surface, not the air.

### Expected accuracy and calibration

- Type K thermocouple with a decent logger: ±1.5-2.2 C class. Type T: ±1.0 C class. DS18B20-class digital probes: ±0.5 C over 0-85 C.
- All probes shall pass a two-point check before the campaign (see T-01): ice-point (0 C) and boiling-water (approx. 100 C, corrected for local barometric pressure). Probes reading outside ±1 C of the reference points shall be corrected by offset or replaced.
- Absolute accuracy of ±1-2 C is sufficient for all pass criteria in this plan; the pass criteria below carry margins sized accordingly.

### Firmware correlation and logging

The project telemetry viewer exists for CAN data; the firmware NTC channels (two IGBT NTCs, one DC-link capacitor NTC) are broadcast on CAN and shall be logged with the telemetry viewer for the full duration of every test, time-synchronized with the reference probe log. Correlating firmware NTC readings against the reference probes at the same physical points is a required output of T-02 through T-06, not a nice-to-have: it is how CLM-4 and CLM-5 are verified.

## Test Cases

Status vocabulary follows OV-TEST-FAULT-INJECTION (Defined / Executable / Conditional / Deferred / Executed / Verified). As of this revision all tests are **Defined**.

### T-01: Reference Probe Calibration Check

**Objective:** Establish reference-probe accuracy before any thermal measurement. Supports CLM-5.

**Setup:** All reference probes, a stirred ice-water bath (crushed ice + a little water, well mixed), and a pot of boiling water. Note local barometric pressure and compute the local boiling point.

**Steps:**

1. Immerse all probe tips together in the stirred ice bath for 5 minutes; record stabilized readings.
2. Immerse all probe tips in boiling water (not touching the pot wall) for 3 minutes; record stabilized readings.
3. Record offset of each probe at both points.

**Pass criteria:** Every probe used in the campaign reads 0 C ±1 C in the ice bath and the local boiling point ±1 C in boiling water, or has a documented offset correction applied to all its campaign data.

**Data table:**

| Probe | Ice bath (C) | Boiling (C) | Offset applied | Verdict |
|-------|--------------|-------------|----------------|---------|
| P-AMB | | | | |
| P-HS | | | | |
| P-IGBT | | | | |
| P-CAP | | | | |
| P-PLT | | | | |

### T-02: Cold-Start and Low-Temperature Operation

**Objective:** Verify the DUT starts and operates at low chamber temperature, and that firmware NTC readings remain plausible at the cold end. Supports CLM-4, CLM-5.

**Setup:** DUT in chamber with ice packs / frozen bottles in a condensate tray; circulation fan on (a 12 V PC fan is fine at 0 C, and the stratification warning above applies to cold tests too), LV bench supply and low-voltage dummy load per bench practice. Target chamber temperature: around 0 C; record the actual achieved minimum (lower may not be achievable, see Limitations).

**Steps:**

1. Soak the powered-down DUT in the cold chamber for at least 2 hours after P-AMB and P-HS stabilize.
2. Record reference probes and firmware NTC channels at the stabilized cold point.
3. Power up at the cold soak temperature; verify normal startup, no false temperature faults.
4. Run the low-voltage dummy load at light load for 10 minutes; verify plausible NTC rise from the cold baseline.

**Pass criteria:** DUT starts and runs at the achieved cold soak temperature without false faults. Firmware NTC channels agree with the corresponding reference probes within ±3 C at the cold soak point. No condensation-related malfunction (visual inspection after the test).

**Data table:**

| Quantity | P-AMB | P-HS | P-IGBT | P-CAP | FW IGBT NTC 1 | FW IGBT NTC 2 | FW cap NTC |
|----------|-------|------|--------|-------|---------------|---------------|------------|
| Cold soak (C) | | | | | | | |
| After 10 min light load (C) | | | | | | | |

### T-03: Controlled Thermal Soak at Elevated Ambient

**Objective:** Verify operation at elevated ambient (chamber 40-60 C) with a low-voltage dummy load, and cross-check sensor tracking near the middle of the operating range. Supports CLM-4, CLM-5.

**Setup:** DUT in chamber, heater controlled to 40 C air temperature, fan on, low-voltage dummy load.

**Steps:**

1. Stabilize the chamber at 40 C with the DUT powered down; soak 1 hour after stabilization.
2. Power up; run the dummy load at a fixed light operating point for 30 minutes.
3. Record all probes and firmware NTC channels at 5-minute intervals.
4. Repeat the soak and run at 60 C chamber temperature (the highest chamber point of this plan).

**Pass criteria:** Continuous operation at both soak points with no false faults. Firmware NTC vs reference probe agreement within ±3 C at each stabilized point. P-CAP and P-PLT remain below the 90 C derate threshold with margin at the light operating point (expected: they should; if not, record it, as it indicates unexpected internal heating).

**Data table:**

| Chamber setpoint | Time (min) | P-AMB | P-HS | P-IGBT | P-CAP | P-PLT | FW NTCs (1/2/cap) |
|------------------|------------|-------|------|--------|-------|-------|-------------------|
| 40 C | 0/5/.../30 | | | | | | |
| 60 C | 0/5/.../30 | | | | | | |

### T-04: Heatsink Thermal-Resistance Measurement

**Objective:** Measure the effective sink-to-ambient thermal resistance of the heatsink assembly at a known dissipation and compare with the design-doc claims (CLM-1). This is the primary quantitative check of OV-C2-DD-THERMAL.

**Setup:** Heatsink assembly (with the three IGBT modules mounted and greased per the assembly guide) fitted with power resistors as dummy heat sources, bolted flat to the module footprints with thermal grease; resistor dissipation set by a bench supply and measured by volts x amps at the resistor terminals. Use as much dissipation as the heatsink and supply allow: **500 W to 1 kW total** across the three module footprints (e.g. 3 x 170-330 W). Measurability drives this number: at the 0.0234 K/W requirement, 500 W-1 kW gives a delta-T of roughly 12-24 K, resolvable with the specified probes; at 100-300 W the delta-T would be only 2.4-7.2 K, and probe accuracy of ±1-2 C would dominate the result. Run at the intended cooling condition of the heatsink (forced air or liquid, as applicable); record the cooling condition. Runs in still air are characterization only and cannot count toward CLM-1.

**Steps:**

1. Bolt the dummy heat-source resistors to the three module footprints; attach P-HS under the center module and P-AMB nearby.
2. Apply a known total power $P$; record $P$ precisely (measure V and I).
3. Run until steady state (temperature drift < 0.5 K over 10 minutes; expect 30-90 minutes).
4. Record $T_s$ (P-HS) and $T_{amb}$ (P-AMB); compute $R_{th(s-a)} = (T_s - T_{amb}) / P$.
5. Repeat at a second power level to check linearity.

**Pass criteria:** Error budget for this measurement: probe accuracy ±1-2 C absolute applies to both $T_s$ and $T_{amb}$, giving roughly ±1.4-2.8 K on the delta-T (RSS); power measurement with bench V x A is ±2 % class. At 500 W / ~7 K rise at the 0.0139 K/W continuous-point requirement, the resulting $R_{th(s-a)}$ uncertainty is roughly ±20-40 %. With this instrumentation **T-04 can bound $R_{th(s-a)}$ to roughly the 0.02 K/W class: it can validate the 0.0141 K/W (2 kHz reference) and 0.0139 K/W (330 A RMS continuous) points (1 kW yields ~14 K rise, above the probe error), but not the 0.0095 K/W (6 kHz) peak point** (1 kW yields ~9.5 K rise, marginal against the error band). Validating the 600 A peak / 6 kHz point with margin needs the dyno or a calorimetric flow rig and remains open. Bench-level pass for CLM-1: measured $R_{th(s-a)} \le 0.0139$ K/W including the error band, at the intended cooling condition; still-air runs are recorded as characterization data only. If the measured value exceeds the requirement for the intended operating point, the result shall be raised as a design deviation against OV-C2-DD-THERMAL (whose loss model is an unvalidated design estimate, marked as such in that document). The two power levels shall agree within the error band above.

**Data table:**

| Run | $P$ (W) | $T_{amb}$ (C) | $T_s$ (C) | $\Delta T$ (K) | $R_{th(s-a)}$ (K/W) | Cooling condition |
|-----|---------|---------------|-----------|----------------|----------------------|-------------------|
| 1 | | | | | | |
| 2 | | | | | | |

### T-05: DC-Link Plate Temperature Rise Verification

**Objective:** Verify the OV-C2-DD-DCLINK-THERMAL claim that the spreader plate rises approximately +40.1 K over the heatsink base at 40 W capacitor heat load (CLM-2).

**Setup:** DC-link capacitor bank on its standoffs and spreader plate, mounted on the heatsink. Apply a known 40 W heat input representative of the bank: either dissipate 40 W in resistors thermally bonded to the plate, distributed across the plate area (the model assumes uniform plate heating, so matching the exact capacitor layout is not required), or drive ripple current into the actual bank at a level computed to produce 40 W (requires the ripple estimate from OV-C2-DD-DCLINK-THERMAL; record the method used). The resistor substitution method is the default because it makes the 40 W input exact and repeatable; it verifies the conduction path (standoffs, contacts, spreading), which is what the design doc analyzes.

**Steps:**

1. Instrument P-HS (heatsink base under the standoff field) and P-PLT (mid-plate); keep the heatsink base near a known, roughly constant temperature (clamp the heatsink at approximately 40 C with the chamber or a controlled plate if available; otherwise record actual $T_s$).
2. Apply 40 W to the plate/bank; run to steady state.
3. Record $T_{plate}$ and $T_{sink base}$; compute $\Delta T = T_{plate} - T_{sink base}$.

**Pass criteria:** Measured $\Delta T$ shall be 40.1 K ±20 % (i.e. 32-48 K), matching the analytical model's own stated ±20 % spreading uncertainty. Note explicitly: **+40.1 K is an unvalidated 1-D analytical estimate**; this test is its validation. A result below 32 K is acceptable (better than designed, expected direction since the model neglects convection/radiation); a result above 48 K is a design deviation against OV-C2-DD-DCLINK-THERMAL (check thermal paste and standoff torque per its recommendations before concluding).

**Data table:**

| Run | Heat input (W) | Method | $T_{sink base}$ (C) | $T_{plate}$ (C) | $\Delta T$ (K) | Verdict |
|-----|----------------|--------|----------------------|------------------|----------------|---------|
| 1 | 40 | | | | | |

### T-06: Firmware Derate and SSO Threshold Verification (FSR-08)

**Objective:** Verify firmware derates at 90 C and enters SSO at 105 C on the DC-link capacitor NTC channel, and that the IGBT NTC channels behave per FSR-08 (CLM-3, CLM-4). Complements the fault-injection coverage of the same mechanism (C-08, C-35, C-45 in OV-TEST-FAULT-INJECTION); here the stimulus is real heat, not injected signals.

**Setup:** DUT powered on the bench or in the chamber at low voltage, telemetry viewer logging the capacitor NTC channel, IGBT NTC channels, derate state, and fault/SSO status. Heat the capacitor NTC sensing point locally (heated probe tip, hot-air pencil, or small power resistor bonded near the sensor) so the sensor channel can be swept through the thresholds without heating the whole inverter. A reference probe (P-CAP) shall be co-located with the NTC.

**Steps:**

1. Baseline: record the capacitor NTC channel vs P-CAP at ambient.
2. Ramp the sensor temperature slowly (target < 1 K/s near thresholds) through 90 C. Record the temperature at which derating asserts in telemetry.
3. Continue the ramp through 105 C. Record the temperature at which SSO asserts (PWM disabled, fault latched).
4. Verify SSO is immediate (no torque ramp-down behavior) and that the fault is logged with the correct DTC.
5. Cool below the thresholds; record recovery / reset behavior per firmware design.
6. Repeat the sweep on the IGBT NTC channels (heat the module-sited NTC area) to verify channel plausibility and any module-side threshold behavior (100 C hard cap per OV-C2-DD-THERMAL).

**Pass criteria:** Derating asserts at 90 C and SSO at 105 C on the capacitor NTC channel, within ±3 C of the firmware setpoints as read by the co-located reference probe. SSO entry is immediate and latched. The firmware channel agrees with the reference probe within ±3 C across the sweep (CLM-5). Note explicitly: **the FSR-08 1oo2 IGBT temperature voter is marked "Planned / not yet implemented (Phase 2)" in OV-SAF-HARA-CORE**; if the firmware under test does not yet implement the voter or these thresholds, this test is recorded as blocked for the affected items, not failed.

**Data table:**

| Channel | Event | FW setpoint (C) | Trip at ref probe (C) | Telemetry confirmed | Verdict |
|---------|-------|------------------|------------------------|---------------------|---------|
| Cap NTC | derate | 90 | | | |
| Cap NTC | SSO | 105 | | | |
| IGBT NTC 1 | behavior/hard cap | | | | |
| IGBT NTC 2 | behavior/hard cap | | | | |

### T-07: Thermal Cycling (Workmanship Screening)

**Objective:** Screen the assembled hardware for workmanship defects (grease voids, loose standoffs, cracked solder joints) by cycling between hot and cold. This is a screening test, not a qualification.

**Setup:** DUT (unpowered or at light load; record which) in the chamber. Cold end: ice packs. Hot end: heater to 60 C chamber.

**Steps:**

1. Cycle chamber temperature between the achievable cold point (target around 0 C) and 60 C, with at least 30 minutes dwell at each extreme after stabilization. Run 10 cycles.
2. Log all probes and firmware NTC channels continuously.
3. Before and after the cycling, repeat a shortened T-04 single-point $R_{th(s-a)}$ measurement and a T-05 single-point plate-rise measurement.
4. Visual inspection after cycling: grease condition/pump-out, standoff torque witness marks, solder joints, connectors.

**Pass criteria:** No failures or false faults during cycling. Post-cycling $R_{th(s-a)}$ and plate $\Delta T$ within 10 % of pre-cycling values. No visible grease pump-out, loosened hardware, or joint damage.

**Data table:**

| Cycle | Cold dwell (C / min) | Hot dwell (C / min) | Anomalies |
|-------|----------------------|---------------------|-----------|
| 1-10 | | | |

| Measurement | Pre-cycling | Post-cycling | Change (%) |
|-------------|-------------|--------------|------------|
| $R_{th(s-a)}$ (K/W) | | | |
| Plate $\Delta T$ (K) | | | |

## Acceptance Criteria Summary

| Claim | Acceptance threshold | Basis |
|-------|----------------------|-------|
| CLM-1 | Measured $R_{th(s-a)} \le 0.0139$ K/W at the intended cooling condition, within the T-04 error band (roughly ±20-40 % at 500 W-1 kW). This validates both the 330 A RMS continuous point and the 424 A RMS / 2 kHz reference point (both ≈0.014 K/W); the 0.0095 K/W 600 A peak / 6 kHz point is marginal on the bench and should be confirmed on the dyno or a calorimetric flow rig (remains open). Design-doc values are unvalidated estimates; deviation raised against OV-C2-DD-THERMAL. | T-04 |
| CLM-2 | Plate rise 26-39 K at 40 W (32.4 K ±20 %, rev-B 6.35 mm plate). Design-doc value is an unvalidated 1-D estimate; this test is its validation. | T-05 |
| CLM-3 | Derate at 90 C ±3 C; immediate SSO at 105 C ±3 C, capacitor NTC channel. | T-06 |
| CLM-4 | IGBT NTC channels plausible and tracking within ±3 C across cold, soak, and sweep tests. | T-02, T-03, T-06 |
| CLM-5 | Firmware NTC vs calibrated reference probes within ±3 C at all recorded points. | T-01 through T-06 |

Any failed or blocked criterion shall be recorded in the campaign Test Report with the measured data and a disposition (design deviation, firmware gap, or test-equipment limitation).

## Evidence and Records

Evidence expectations follow OV-TEST-FAULT-INJECTION, Section "Test Records and Evidence":

1. **Telemetry log** - CAN capture from the project telemetry viewer (all NTC channels, derate state, fault/SSO status) for the full duration of every test.
2. **Reference-probe log** - time-synchronized logger export of all P-* probes.
3. **Photos/video** - chamber setup, probe placement, and (for T-06) the threshold crossings as displayed in telemetry.

Naming convention: `T-0<N>_run<M>_<YYYY-MM-DD>_<condition>.<ext>`, e.g. `T-06_run1_2026-09-01_cap-ntc-sweep.csv`, with the telemetry log sharing the same base name. Each execution campaign produces a dated Test Report filed as a sibling of this plan, referencing OV-TEST-THERMAL-PLAN and the test IDs above.

## Limitations of the Cooler Chamber

This chamber is adequate for the verification goals above, but it cannot show:

- **No humidity control.** Condensation during cold tests is managed (trays, inspection) but not characterized; damp-heat and humidity type tests need a real environmental chamber.
- **No altitude / pressure simulation.** Reduced-pressure cooling effects (lower convective heat transfer at altitude) are not represented.
- **Limited temperature range.** Practical range is roughly 0 C (ice, transient lower) to 60-80 C (safety-limited). The -40 C cold-soak end of the module operating range and any >80 C ambient test are out of reach; the E-series environmental type tests in OV-TEST-FAULT-INJECTION (E-01 through E-12) remain Deferred for exactly this reason.
- **Limited temperature rate.** Passive insulation plus a small heater gives slow ramps (typically < 1 K/min); thermal-shock rates per IEC 60068-2-14 are not achievable. T-07 is a workmanship screen, not a thermal-shock qualification.
- **Temperature uniformity.** Even with the fan, expect a few K of spatial variation; all pass criteria are written with margins that absorb this.
- **No vibration, EMC, or combined environments.**

Items needing a real chamber (controlled humidity, altitude, fast ramp, sub-0 C soak, >80 C ambient) shall be scheduled with the deferred E-series type-test campaign at an external lab.

## Traceability

| This document | References |
|---------------|------------|
| CLM-1, T-04 | OV-C2-DD-THERMAL (heatsink sizing, $R_{th(s-a)}$ requirements) |
| CLM-2, T-05 | OV-C2-DD-DCLINK-THERMAL (+40.1 K standoff/plate heat path) |
| CLM-3, CLM-4, T-06 | OV-SAF-HARA-CORE, FSR-08 (90 C derate / 105 C SSO, capacitor channel; 1oo2 IGBT NTC voting) |
| T-06 method, evidence framework, status vocabulary, E-series deferral | OV-TEST-FAULT-INJECTION (C-08, C-35, C-45; Sections "Test Status Vocabulary", "Test Records and Evidence") |

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-08-20 | (Prior revision; see git history for details.) |
| 1.2 | 2026-08-20 | CLM-1 updated to the OV-C2-DD-THERMAL v1.1+ heatsink requirements ($R_G = 2.7 \ \Omega$ gate drive): 0.0073 K/W at 600 A / 320 V / 2 kHz and 0.0047 K/W at 600 A / 320 V / 6 kHz (was 0.0076 K/W), 0.0234 K/W at 300 A / 320 V (was 0.0239 K/W); T-04 setup and acceptance tables aligned. CLM-1 notes that 600 A is now the 60 s peak duty and the continuous rating is 220 A per OV-C2-DD-THERMAL v1.2. |
| 1.3 | 2026-08-23 | Aligned to OV-C2-DD-THERMAL v1.3 (600 A = peak = 424 A RMS; continuous rating 330 A RMS / 465 A pk) and OV-C2-DD-DCLINK-THERMAL v1.3 (rev-B 6.35 mm plate, +32.4 K reference rise). CLM-1 requirements relaxed: 0.0141 K/W (2 kHz reference) / 0.0095 K/W (6 kHz peak) / 0.0139 K/W (continuous point); design target 0.007 K/W. T-04 bench acceptance tightened to ≤0.0139 K/W, which the bench instrumentation can now reach for the continuous and 2 kHz points; only the 6 kHz peak point remains dyno-only. CLM-2 acceptance updated to 26-39 K at 40 W for the rev-B plate. |
