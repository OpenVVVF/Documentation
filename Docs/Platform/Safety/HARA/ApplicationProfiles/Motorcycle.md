---
doctype: Application Profile — Hazard Analysis & Risk Assessment
doc_id: OV-HARA-PROF-MOTO
title: OpenVVVF HARA — Motorcycle Application Profile
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - application-profile-motorcycle
core_ref: OV-HARA-CORE v5.7
profile_for: motorcycle
standard: ISO 26262:2018
temp: −40 °C to +85 °C
version: "1.6"
prepared: Thomas Liao
reviewed: (not yet reviewed)
date: "2026-07-30"
status: elaborated
description: Motorcycle-specific HARA profile — operational situations, S/E/C ratings, and ASIL targets applied to the platform hazard set.
nav_order: 120
normative_refs:
  - OV-HARA-CORE
---

# 1. Introduction

This document is an **Application Profile** of the OpenVVVF HARA document set. It assigns motorcycle-specific Operational Situations, Severity/Exposure/Controllability ratings, and ASIL targets to the platform hazard set, Safety Goals, and Functional Safety Requirements defined in the Core Platform document.

- **Core document:** OV-HARA-CORE v5.1 (*OpenVVVF HARA — Core Platform*). This profile was assessed against that version; it shall be reviewed on any Core revision.
- **Normative reference:** hazards H-01 through H-17, Safety Goals SG-01 through SG-15, and FSR-01 through FSR-22 are defined in the Core document and are **not** restated here. The Core compliance statement (Core §1.2) applies in full to this profile: ASIL ratings herein are **targets**, not claims of verified compliance.
- **Standard applied:** ISO 26262:2018 (methodology), as for the Core.
- **Status:** elaborated — this profile is the current reference S/E/C assessment for the platform.

# 2. Application Definition


High-performance electric 2-wheel motorcycles — Zero (102 V nominal), Energica (<320 V), and similar platforms. Combined traction inverter + VCU function. One-pedal regenerative braking (tractive effort rollback), not wheel-lock capable.

**Table 1 — Application-Specific Parameters**

| Parameter | Value / Range |
| --- | --- |
| Vehicle type | Electric 2-wheel motorcycle |
| Max vehicle speed | 150 mph (240 km/h) |
| Vehicle kerb weight | Up to 600 lbs (272 kg) |
| Driven wheels | 1 (rear) |
| Operator controls | Twist throttle (dual pot + limit switch), friction brakes (independent), kickstand interlock |

# 3. Operational Situations

**Table 2 — Operational Situations (Motorcycle)**

| ID | Operational Situation | Description | Speed |
| --- | --- | --- | --- |
| OS-01 | Stationary, system active | Vehicle stopped, key-on, rider present, in gear | 0 mph |
| OS-02 | Creep / low speed | Parking lot, driveway, traffic jam | 0–10 mph |
| OS-03 | Urban driving | City streets, intersections | 10–45 mph |
| OS-04 | Rural / arterial road | Secondary roads, moderate curves | 45–65 mph |
| OS-05 | Highway cruising | Multi-lane highway, dense traffic | 65–85 mph |
| OS-06 | High speed highway | Limited maneuvering space | 85–150 mph |
| OS-07 | Hard acceleration | Wide open throttle | Variable |
| OS-08 | Regenerative braking | Throttle rollback, one-pedal regen | Variable |
| OS-09 | Combined braking | Mechanical brake + regen blend | Variable |
| OS-10 | Cornering / lean | Banked turn, leaned over, on throttle | Variable |
| OS-10a | Cornering at limit / racetrack | High lean angle, maximum traction demand, rider relying on tractive effort to hold line | Variable (high) |
| OS-11 | Power-on sequence | Precharge, initialization | 0 mph |
| OS-12 | Power-off / shutdown | Key-off, discharge | 0 mph |
| OS-13 | Rain / wet road | Reduced traction | Variable |
| OS-14 | High ambient temperature | Desert operation, >40 °C | Variable |
| OS-15 | Low traction surface | Gravel, sand, wet leaves, paint | Variable |
| OS-16 | Sustained grade / downhill descent | Long downhill, regen or coasting, gravity-fed speed | Variable (high) |

> **OS-10a (Cornering at Limit):** Distinct from OS-10: at full lean the rider actively uses tractive effort to modulate the cornering line with the rear tire at its traction limit. For this platform, loss of drive in this situation is freewheel and dynamically benign (Section 5); controllability for loss-of-power hazards here is **C2**. Unintended *application* of tractive effort at lean remains **C3** (Section 6).

# 4. Environmental Conditions

Ambient −20 °C to +50 °C; humidity 0–100% condensing; surfaces dry/wet/standing water/gravel/sand; altitude 0–3,000 m; motorcycle-mounted high vibration.

# 5. Profile-Specific Hazard

> **H-03a: Loss of Tractive Effort During Cornering at Lean**
>
> **Dynamics assessment (v1.1):** The fault response of this platform is six-switch-open (SSO): on fault, the motor produces zero torque in either direction — dynamically equivalent to pulling in the clutch. Unlike an ICE throttle chop, there is **no engine-braking torque**, hence no forward weight transfer, no rear-tire unloading, and no stand-up tendency. On loss of drive at lean, the rear tire's longitudinal friction demand vanishes and the full friction ellipse becomes available for lateral force. Mid-corner and corner-exit loss of drive is therefore **dynamically benign** for this architecture: the motorcycle coasts through the corner and decelerates gently. The dangerous direction at lean is the opposite one — *unintended* tractive effort (H-01/H-06, highside) — which is covered by SG-01 (ASIL D).
>
> **Residual harm path:** the retained hazard is **contextual, not dynamic**: (1) following traffic — a coasting, rapidly decelerating motorcycle (track: on the racing line at corner exit; road: in a live lane) creates a collision risk from closing-speed differential, severity up to S3 at track/highway speeds; (2) the startle transient at the limit, which may provoke rider error on low-grip surfaces. Track use typically involves full PPE (leathers, armor, helmet), which reduces likely harm in the track scenario; however, severity is rated on the worst reasonable outcome and PPE is neither part of the item nor enforceable — the street case (no PPE, intersections) must also be covered. **S3 is retained on the traffic-collision path; controllability C2 (recoverable; freewheel dynamics); exposure E2 (cornering at or near the limit is well under 10% of operating time even for a track-capable platform; E3 previously assigned was not defensible).**
>
> **v5.0 residual-risk statement:** Under the immediate-SSO philosophy (Core §2.3), every fault produces this event. The platform mitigations are detection speed (FSR-05 latency budget) and the cleanliness of the torque transition (S-04). The rider-level consequence is **accepted residual risk**, assessed as small for the reasons above, and shall be characterized by track testing (LIMIT-01) before racetrack use.

# 6. Controllability Considerations

Motorcycles are inherently less stable than 4-wheeled vehicles: two contact patches, simultaneous roll/pitch/yaw management, high CG relative to wheelbase, single driven wheel. Unintended acceleration/braking at highway speed is therefore **C3**. Loss of tractive effort during cornering at lean (OS-10a) was formerly rated C3 on ICE-dynamics intuition (engine-braking stand-up). For this platform, SSO is freewheel — there is no engine-braking torque — so loss of drive at lean is rated **C2** (Section 5). Unintended *application* of tractive effort at lean remains **C3**.

# 7. Risk Assessment and ASIL Assignment

**Table 3 — Hazard Risk Assessment & ASIL Assignment (Motorcycle Profile)**

| Hazard | Worst OS | S | E | C | Target ASIL | Achievable Now | Rationale |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **H-01** | OS-06 (85–150 mph) | S3 | E3 | C3 | D | D | Unintended tractive effort at high speed → loss of control. Dual-MCU decomposition: independent throttle ADC, CAN snoop, 1oo2 power kill. |
| **H-02** | OS-01 (stationary) | S2 | E2 | C2 | B | B | Rearward tip-over at standstill; rider can brace. |
| **H-03** | OS-06 (highway) | S3 | E3 | C2 | C | C | Sudden loss at highway speed; rear-collision risk. v5.0: abrupt loss on every fault; C2 retained — rider retains brakes/steering; following-traffic risk unchanged by ramp-vs-step at these energies. |
| **H-03a** | OS-10a (corner at limit) | S3 | E2 | C2 | A | A | Mid-corner loss → stand-up/run-wide. SSO is freewheel — loss of drive at lean is dynamically benign (Section 5); S3 retained on the following-traffic collision path; E2 per Section 5 exposure assessment. Accepted residual risk; detection-to-SSO latency is the mitigation; track characterization required. |
| **H-04** | OS-09 (braking) | S2 | E3 | C2 | A | A | Loss of regen; friction brakes remain. |
| **H-05** | OS-13 (wet road) | S3 | E3 | C3 | C | C | Unexpected deceleration on wet surface. |
| **H-06** | OS-06 (highway WOT) | S3 | E3 | C3 | C | C | Wheel spin at speed. Dual-MCU current monitoring (100 ms); DESAT for hard shorts. |
| **H-07** | OS-14 (desert) | S3 | E2 | C2 | B | B | Thermal runaway; 3x redundant sensing. |
| **H-08** | OS-16 (downhill descent) | S3 | E2 | C3 | C | C | Encoder loss at speed; single encoder (external constraint); both MCUs monitor. |
| **H-09** | OS-01 (crash/service) | S3 | E1 | C2 | A | A | HV shock; HVIL + reinforced isolation. |
| **H-10** | OS-16 (regen on descent) | S3 | E2 | C2 | B | B | DC link overvoltage from regen. |
| **H-12** | OS-07 (hard accel) | S3 | E2 | C3 | C | C | Shoot-through; NCV57100 anti-shoot-through (non-ASIL); coprocessor PWM monitoring. |
| **H-13** | OS-06 (fault at speed) | S3 | E3 | C3 | D | D | Six redundant SSO pathways. |
| **H-14** | OS-06 (highway) | S3 | E3 | C3 | C | C | Stuck command; WDT catches CPU halt. |
| **H-15** | OS-06 (highway) | S3 | E3 | C3 | D | D | Software error; coprocessor independent verification + independent SSO. |
| **H-16** | OS-07 (hard accel) | S3 | E2 | C3 | C | C | Both MCUs monitor OR'd FLT; coprocessor READY/PWM monitoring. |
| **H-17** | OS-07 (hard accel) | S3 | E3 | C3 | C | C | Coprocessor monitors all 6 PWM pairs for deadtime/stuck faults. |

---

# References

| Ref | Citation |
| --- | --- |
| OV-HARA-CORE | OpenVVVF HARA — Core Platform, v5.7 (doc_id OV-HARA-CORE). Normative. |
| Cossalter | Cossalter, Lot, Massaro, *Motorcycle Dynamics* (chapter), 2014. Lean mechanics and tire friction-ellipse basis for the Section 5 dynamics assessment. |
| NHTSA | *Motorcycle Safety*. https://www.nhtsa.gov/motorcycles. Accident causation context for severity assessment. |

---

# Document History

| Version | Date | Changes |
| --- | --- | --- |
| 1.0 | 2026-07-30 | Initial standalone profile, split from the v5.0 combined document (Annex A therein). Assessed against OV-HARA-CORE v5.4. H-03a residual-risk statement aligned with Core §2.3 (immediate SSO, no software ramp-down). |
| 1.1 | 2026-07-30 | H-03a re-analyzed: SSO-is-freewheel dynamics assessment added (no engine-braking equivalent; loss of drive at lean is dynamically benign). Re-rated S3/E3/C3/ASIL C → S3/E2/C2/ASIL A. Severity retained at S3 on the following-traffic collision path; PPE context noted but not credited (not part of the item). No cascade: SG-03 target unchanged (driven by H-03). |
| 1.2 | 2026-07-30 | OS-16 (sustained grade / downhill descent) added; H-08 and H-10 worst-OS references corrected to OS-16 (previously dangling "downhill"/borrowed references). Assessed against OV-HARA-CORE v5.3. |
| 1.3 | 2026-07-31 | H-11 row removed: HV contactor actuation, weld detection, and contactor-related hazards are BMS/OEM-domain (OV-HARA-CORE v5.4, Section 1.3) and are excluded from this profile. |
| 1.4 | 2026-07-31 | Table 3 H-03a row corrected to S3/E2/C2/ASIL A, matching the v1.1 re-analysis recorded in Sections 5–6 (the table row had retained the superseded S3/E3/C3/ASIL C values). References section added (Cossalter, NHTSA). Assessed against OV-HARA-CORE v5.5. |
| 1.5 | 2026-07-31 | Formatting and consistency cleanup: OS-10a/OS-16 table rows no longer bolded; "aftermarket" descriptors removed from the application definition; OS-10a note aligned with the Section 5 dynamics assessment (loss of drive at lean = C2, superseding the earlier C3 statement in the note). Assessed against OV-HARA-CORE v5.6. |
| 1.6 | 2026-07-31 | Dynamics reference corrected: the lean-mechanics citation is now Cossalter, Lot, Massaro, *Motorcycle Dynamics* (2014 chapter). Assessed against OV-HARA-CORE v5.7. |
