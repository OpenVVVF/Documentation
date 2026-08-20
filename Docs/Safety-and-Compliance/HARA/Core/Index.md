---
doctype: Hazard Analysis & Risk Assessment
doc_id: OV-SAF-HARA-CORE
title: HARA Core
product_line: openvvvf
applies_to:
  - openvvvf-control-module
mcus: STM32H723ZG + STM32G474RCTx
temp: −40 °C to +85 °C
version: "5.8"
date: "2026-08-13"
description: Platform hazard analysis, safety goals, and functional safety requirements for the dual-MCU control module; fault-injection validation is defined in OV-TEST-FAULT-INJECTION.
nav_order: 311
normative_refs:
  - OV-SAF-HARA-PROF-MOTO
  - OV-TEST-FAULT-INJECTION
---

# Introduction

## Document Set - Core Platform and Application Profiles

The OpenVVVF HARA is published as a **document set** rather than a single document:

| Document | ID | Role |
| --- | --- | --- |
| **OpenVVVF HARA - Core Platform** (this document) | OV-SAF-HARA-CORE | Defines the control module as an application-independent safety element: hardware, base safety firmware image, safety architecture, platform hazard set, Safety Goals, and Functional Safety Requirements. Fault-injection validation of these requirements is defined in the standalone plan OV-TEST-FAULT-INJECTION. Hazards are stated at the **torque / power boundary** and are application-agnostic. |
| **OpenVVVF HARA - Motorcycle Application Profile** | OV-SAF-HARA-PROF-MOTO | Assigns motorcycle-specific Operational Situations, Severity/Exposure/Controllability ratings, and ASIL targets to the platform hazard set. Normatively references this Core document. |

Additional application profiles (passenger car, rail, industrial/dynamometer) are planned as future documents in the same format. This Core document shall not contain application-specific risk ratings; profile documents shall not restate platform content, and shall declare the Core document version against which they were assessed.

Rationale for the split: the malfunctioning behaviors of a 3-phase traction inverter are platform properties, but the *risk* they create (severity, exposure, controllability, harmed parties, applicable standard) is an application property. A single S/E/C table cannot honestly cover a motorcycle, a car, a train, and a dynamometer; a layered document set can.

## Compliance Statement

> **This Is Not an ISO 26262 Compliance Claim**
>
> This document **applies ISO 26262:2018 methodology** (Part 3: Concept Phase) to identify hazards, assess risk via Severity/Exposure/Controllability classification, and derive Safety Goals with ASIL ratings. For non-road-vehicle application profiles, the equivalent domain standard is referenced for vocabulary and safe-function mapping only (IEC 61800-5-2 for industrial drives; EN 50126/50128/50129 for rail). This is a **best-effort** application of functional safety engineering practice within an open-source project. Full compliance with these standards is not achievable for the project itself: the manufacturer data required for a complete safety case (safety manuals, FMEDAs, certified software libraries) is generally available only under NDA and at costs incompatible with an open-source effort, and the required test facilities (environmental, EMC) are not available. The goal is that this design and its documentation serve as a **starting point that is ready for full compliance work**: the architecture, analyses, and test plan are structured so that a party with access to the required data and facilities can carry the design through complete compliance testing without redesign. The following must be understood clearly:
>
> - **ASIL ratings are targets** derived from the HARA process. They represent the assessed risk level of identified hazardous events, **not a claim that the design has been verified or certified to meet those ASILs**.
> - **The system described is not ISO 26262 compliant**, nor compliant with IEC 61508, IEC 61800-5-2, or the EN 5012x railway series. Full compliance would require: complete product development per the applicable standard's product-development parts, hardware architectural metrics (e.g., SPFM ≥ 90% for ASIL B, ≥ 97% for ASIL D; LFM ≥ 60% for ASIL B, ≥ 80% for ASIL D), dependent failure analysis (DFA), software tool qualification, verification and validation testing (including fault injection), configuration management, change control, and independent safety assessment. **None of these have been completed.**
> - The hardware implements a **dual-MCU architecture**: STM32H723ZG main MCU + STM32G474RCTx safety coprocessor. The coprocessor provides independent ADC monitoring of all safety-critical signals, 1oo2 gate drive power kill, challenge/response watchdog, independent CAN bus snooping, and bidirectional NRST. This makes **ASIL D achievable for SG-01 and SG-13 via ASIL B(D) + ASIL B(D) decomposition**.
> - The gate driver ICs (onsemi NCV57100) are **automotive-qualified (AEC-Q100)** but are **not ISO 26262 safety elements**. No safety manual, FMEDA, or ASIL claim is available from the manufacturer. Internal protections (DESAT, anti-shoot-through, UVLO) provide hardware-level risk reduction but cannot be claimed as ASIL-rated safety mechanisms without additional justification.
> - **Software Test Library (STL) limitation:** This project uses ST's publicly available X-CUBE-CLASSB library (IEC 60730-1 Class B certified). The ISO 26262-certified Class D STL (X-CUBE-STL) requires an NDA and is not available for open-source use. The following ASIL process gaps result: no FMEDA/SPFM/LFM metrics derived for this hardware configuration; no ISO 26262 software tool qualification (compiler, static analysis); no fault injection testing campaign with coverage evidence; no independent safety assessment. ASIL decomposition using the Class B STL is a design and educational exercise only.
> - The firmware is **architecturally complete**. Field-Oriented Control (FOC) is implemented. Safety mechanisms (tractive effort plausibility checking, immediate safe-state transition, boot CRC, challenge/response watchdog) are specified in this document; their implementation status is tracked in Sections 8 and 11.
> - This HARA and its accompanying Fault Injection Test Plan are **living design-input documents** intended to guide development and establish a safety engineering baseline. They do not constitute a product safety case, compliance certification, or warranty of fitness for any purpose.
>
> This is an **open-source traction inverter** project. The documentation is published in the interest of transparency. Users bear full responsibility for evaluating the suitability of this design for their specific application, risk tolerance, and applicable regulatory requirements.

## Scope

This document presents the Hazard Analysis and Risk Assessment (HARA) and Fault Injection Test Plan for the **OpenVVVF control module**: a combined traction inverter control unit and Vehicle Control Unit (VCU) designed to drive 3-phase PMSM traction motors from a DC link bus supply. The core platform is application-agnostic and may drive any compatible DC link supply and 3-phase traction motor. Application-specific operational situations, hazard analysis, and ASIL assignments are defined in separate application profile documents (see §1.1).

The DC link may be supplied by any compatible DC source (for example, a traction battery pack with a Battery Management System); no specific DC source is assumed. The analysis covers the control module and its interfaces to external systems that affect safety.

The scope includes all hardware and software within the control module: the STM32H723ZG main MCU, the STM32G474RCTx safety coprocessor, six NCV57100 gate drivers, 3-phase IGBT power stage, current/voltage/temperature sensing, HV interlock loop (HVIL) digital input, tractive effort control input processing, motor control algorithm, CAN communication, inter-MCU challenge/response watchdog, and fault handling. The Safety Coprocessor is **part of the current design** and provides independent monitoring, 1oo2 gate drive power kill, and ASIL B(D) decomposition.

**Out of scope:** The traction motor itself (external product), the rotor position sensor/encoder (part of the external motor), the Battery Management System (BMS), the IO board and its associated power supplies (including the Cincon DC/DC converter on the IO side - excluded from this analysis), the charger, and the vehicle display - these are external CAN nodes or external equipment interfaced by the VCU but not designed or manufactured by this project. The CAN protocol definitions in this document are the VCU-side interface only.

> **ASIL Decomposition via Dual MCU**
>
> This design implements **ASIL B(D) decomposition** through two independent MCUs: the STM32H723ZG (main processor) and the STM32G474RCTx (safety coprocessor). Each MCU independently monitors all safety-critical signals. Either MCU can trigger safe state entry. The 1oo2 gate drive power kill (GATE_DRIVE_PWR1_ENABLE from main, GATE_DRIVE_PWR2_ENABLE from coprocessor) provides an independent supply shutdown path. Target ASIL D is achievable for SG-01 and SG-13 via ASIL B(D) + ASIL B(D) decomposition.

## Reference Standards

| Standard | Title | Application |
| --- | --- | --- |
| ISO 26262-1:2018 | *Road vehicles - Functional Safety - Part 1: Vocabulary* | Definitions and abbreviations |
| ISO 26262-3:2018 | *Part 3: Concept phase* | HARA methodology, Safety Goals, FSR derivation |
| ISO 26262-4:2018 | *Part 4: Product development at the system level* | Technical Safety Requirements, system design |
| ISO 26262-5:2018 | *Part 5: Product development at the hardware level* | Hardware architectural metrics (SPFM, LFM) |
| ISO 26262-8:2018 | *Part 8: Supporting processes* | Test planning, change management, software tool confidence |
| ISO 26262-9:2018 | *Part 9: ASIL-oriented and safety-oriented analyses* | ASIL decomposition, safety analysis |
| ISO 6469-3:2018 | *Electrically propelled road vehicles - Safety specifications - Part 3: Electrical safety* | HV isolation requirements |
| IEC 61800-5-2:2016 | *Adjustable speed electrical power drive systems - Part 5-2: Safety requirements - Functional* | Safe-function vocabulary (STO, SS1, SLS); safe-state mapping in Section 2.3 |
| IEC 61508 | *Functional safety of E/E/PE safety-related systems* | SIL terminology reference (future profiles) |
| EN 50155 | *Railway applications - Electronic equipment used on rolling stock* | Reference for future rail profile |

# Item Definition

## System Boundaries

**Table 1 - System Boundary Inclusions and Exclusions**

| Category | Description |
| --- | --- |
| **In Scope** | Combined traction inverter control module / VCU PCB, six onsemi NCV57100 isolated gate drivers (AEC-Q100), 3-phase 2-level IGBT bridge, **STM32H723ZG main MCU + STM32G474RCTx safety coprocessor** (dual independent core), phase current sensing (3-phase + DC link), DC link bus voltage sensing, phase voltage sensing, IGBT temperature sensing (2 NTC), DC link capacitor temperature sensing (1 NTC), traction motor temperature sensing, traction motor encoder input, HVIL circuit, dual redundant tractive effort control input + end-travel limit switch, CAN1 (DC source management interface), CAN2 (ABS, display, charger, IO board), precharge control, fault handling logic, 1oo2 gate drive power supply kill (GATE_DRIVE_PWR1_ENABLE + GATE_DRIVE_PWR2_ENABLE), inter-MCU challenge/response watchdog, CY15B102Q-SXET 256 KB FRAM (main MCU side) |
| **Interfaced (external)** | DC link source (any compatible DC supply; a source management node such as a BMS may be present on CAN1, heartbeat 5 s), ABS module (CAN2, independently powered), display/dash (CAN2), charger(s) (CAN2), IO board (CAN2, brake switch, kickstand switch, turn signal feedback, headlight feedback, 1 s heartbeat), 3-phase PMSM traction motor with encoder, 12 V onboard power (external DC/DC from DC link; IO-side supplies, including the Cincon converter, are out of scope) |
| **Out of Scope** | DC source internals (including BMS cell protection where a battery is used), HV contactor control, weld detection, and contactor-related hazards (assessed in the DC source / OEM safety case, not here), ABS hydraulic/mechanical system, charger AC-side circuitry, vehicle chassis, traction motor construction, DC link source beyond electrical interface, IO-board-side power conversion (Cincon DC/DC) |

## Architecture Overview

The control module is a combined unit that performs both motor control (inverter) and vehicle-level control (VCU) functions. The architecture comprises the primary control path, the hardware protection layer, an independent safety monitor, rail supervision, and the safe state actuation layer.

**Table 2 - External Interfaces**

| Interface | Connected System |
| --- | --- |
| DC link | DC source (any compatible supply) |
| 3-phase AC via NCV57100 x6 | PMSM traction motor |
| CAN1 (heartbeat 5 s) | DC source management node (e.g., BMS, if present) |
| CAN2 (heartbeat 1 s) | IO board (brake, kickstand, signals) |
| CAN2 | ABS module, display, charger |
| Analog (dual pot + limit switch) | Tractive effort control input |
| Sin/Cos analog / Hall effect | Traction motor encoder |
| External DC/DC (IO side) | 12 V onboard power rail |
| FLT (OR'd, active low) | Six NCV57100 fault outputs |

**Primary control path - STM32H723ZG main MCU.** 550 MHz Cortex-M7, ECC RAM, brown-out detect, internal watchdog. Software functions: FOC motor control, tractive effort command processing, sensor acquisition and plausibility checking, fault detection and handling, CAN communication (FDCAN1 + FDCAN2), safe state management, gate drive power kill (Path 2a). Coprocessor interface: inter-MCU UART, timer sync line, bidirectional NRST. Storage: CY15B102Q-SXET 256 KB FRAM (SPI) for fault logs, configuration, hour meter, odometer; hardware write-protect pin.

**Hardware protection layer - six NCV57100 gate drivers (AEC-Q100).** Each device provides local hardware protection for its IGBT: DESAT short-circuit detection (<2 us), complementary anti-shoot-through inputs, UVLO, active Miller clamp, soft turn-off, and gate active pull-down. These protections operate independently of either MCU and provide the first line of defense against power stage faults. All six FLT outputs are OR'd together and fed to both MCUs. ASIL credit for these protections is addressed in Section 2.7.

**Independent safety monitor - STM32G474RCTx safety coprocessor.** 170 MHz Cortex-M4+FPU, 8 MHz crystal, shared +3.3 V rail (dedicated RD7-12S033R DC/DC converter), independent oscillator. Independent ADC access to all 4 current sense signals (phase U/V/W + DC link) + reference, both IGBT temperature sensors, the DC link capacitor temperature sensor, motor temperature, and all encoder signals (Hall U/V/W, Sin/Cos). Independent gate drive monitoring: GATE_DRIVE_FAULT (OR'd FLT), GATE_DRIVE_READY, GATE_DRIVE_RESET, GATE_DRIVE_PWR1_FB, GATE_DRIVE_PWR2_FB, and all 6 PWM outputs (PH_U/V/W_HIGH/LOW). Independent CAN: FDCAN2 + FDCAN3 - can snoop both CAN buses to cross-check torque commands and node heartbeats. Inter-MCU communication: dedicated UART + timer sync line + bidirectional NRST cross-reset. 1oo2 gate drive power kill: GATE_DRIVE_PWR2_ENABLE (coprocessor) in logical-OR with GATE_DRIVE_PWR1_ENABLE (main); either MCU deasserting its enable kills all six gate drive supplies, each with independent feedback. Challenge/response watchdog: the coprocessor issues a challenge; the main MCU must respond within the window - failure leads to NRST on the main MCU and SSO. Safe state authority: the coprocessor can independently trigger SSO via gate drive power kill, gate drive RESET, or main MCU NRST.

**Rail supervisor - TPS389006-Q1 6-channel window supervisor.** Monitors the +3.3 V, +5 V, +12 V, and sensor +5 V rails plus both gate-drive power feedbacks (GATE_DRIVE_PWR1_FB, GATE_DRIVE_PWR2_FB). Window thresholds are I2C-configured by the main MCU at boot. On any out-of-window rail fault - including brownout of the +3.3 V rail shared by both MCUs - its NIRQ output asserts the shared GATE_DRIVER_FAULT line, which is monitored by both MCUs (the same net that carries the OR'd gate-driver FLT). The device is TI Functional Safety-Compliant and supports designs up to SIL 3 / ASIL D per TI. The boot-time I2C threshold configuration is a dependency to be covered by the pending DFA (LIMIT-08).

**Safe state actuation layer - six redundant SSO pathways.**

- **Path 1 (hardware, <100 ns):** TIM1 break input (TIM1_BKIN) → hardware clears MOE, all PWM outputs disabled. Triggered by OR'd gate driver FLT (DESAT/UVLO) or software fault. Independent of both CPU states after trigger.
- **Path 2a (active, ~10 us):** Main MCU → GATE_DRIVE_PWR1_ENABLE low → all six Murata MGJ2D121509MPC-R7 supplies shut down → NCV57100 UVLO → active pull-down → SSO. Feedback via GATE_DRIVE_PWR1_FB.
- **Path 2b (active, ~10 us):** Coprocessor → GATE_DRIVE_PWR2_ENABLE low → same supply shutdown. Independent of Path 2a. Feedback via GATE_DRIVE_PWR2_FB. Either Path 2a or 2b alone achieves SSO (1oo2). The ~10 us figures are actuation-only; time-to-SSO on the power-kill paths additionally depends on gate-bias rail decay to the NCV57100 UVLO threshold and is under characterization.
- **Path 3 (hardware, passive):** Loss of shared 3.3 V rail → NCV57100 VDD lost → internal active pull-down → SSO. Automatic, no software intervention.
- **Path 4 (active, <1 us):** Either MCU → DRIVER_RESET asserted → all NCV57100 RESET inputs → outputs immediately disabled (hard turn-off via OUTL active pull-down; on the NCV57100, soft turn-off exists only on the DESAT path) → SSO. Both MCUs share the RESET line (either can assert). The TPS389006-Q1 rail supervisor is an additional fault source on this pathway: on any monitored-rail fault, including brownout of the +3.3 V rail shared by both MCUs, it asserts the shared GATE_DRIVER_FAULT line, signaling both MCUs to assert DRIVER_RESET.
- **Path 5 (active, ~100 ms):** Coprocessor challenge/response watchdog failure → coprocessor asserts main MCU NRST → system reset → SSO during boot. Main MCU WDT timeout as backup.
- **Path 6 (active, <10 us):** Coprocessor detects critical fault independently → asserts GATE_DRIVE_PWR2_ENABLE low + GATE_DRIVE_RESET → SSO without relying on the main MCU.

## Safe State Philosophy - Immediate SSO, No Software Ramp-Down

> **Design Decision (v5.0): Fault response shall be immediate transition to Six-Switch-Open (SSO). Software-controlled torque ramp-down on fault is explicitly rejected.**
>
> In IEC 61800-5-2 vocabulary, this design implements **Safe Torque Off (STO)** as its sole fault response, and deliberately does **not** implement SS1 (controlled deceleration followed by STO). The rationale is as follows:
>
> 1. **A controlled ramp requires a trustworthy controller.** A ramp-down on fault detection is executed by the same system whose integrity has just been compromised. If the fault is a lying current sensor, a corrupted tractive effort calculation, or a misbehaving MCU, the "controlled" ramp is closed around untrusted data. Worst case, the ramp-down code is itself where the fault lives. Continued torque production from a faulted controller is unbounded; abrupt torque loss is bounded and, in most operational situations, recoverable by the operator. Moreover, SSO is freewheel: at loss of drive the machine produces no braking torque either, so the torque-free state is dynamically gentle at the drive boundary. Vehicle-level consequences of abrupt torque loss are assessed in the applicable profile document.
> 2. **Hardware already forces SSO.** DESAT on the NCV57100 disables the phase within <2 us regardless of software intent; TIM1_BKIN disables all PWM within <100 ns. Any software ramp-down would apply only to the subset of faults that do not assert a hardware path - i.e., precisely the faults where software integrity is most in doubt.
> 3. **The base-image / generated-code trust model requires a minimal safety kernel.** Application and control code on this platform is intended to be user-generated via node-based code generation (Section 2.6). A torque-ramping state machine in the base safety image would add safety-critical states, timing edge cases (new fault arriving mid-ramp, regen-to-motoring zero-crossing during ramp), and verification burden. Immediate SSO removes that class of edge-case defects entirely.
> 4. **Residual risk is owned, not hidden.** The consequence of this decision is that every fault produces an immediate torque step to zero, which is the H-03/H-03a hazardous event. This is an **accepted residual risk**, documented in Section 2.3 and the applicable profile document. The primary risk-reduction mechanism for loss-of-traction hazards under this philosophy is **detection speed** (fault-to-SSO latency), not torque shaping.
>
> Note: the NCV57100 **soft turn-off on the DESAT path** is retained. It is a microsecond-scale di/dt/overvoltage protection inside the gate driver and is unrelated to software torque ramping.

## Mitigation Strategy

The following table explains how each hazard class is mitigated by the architecture, which mechanisms cover which failure modes, and where the known limitations are.

**Table 3 - Hazard Mitigation Strategy**

| Hazard Category | Failure Mode | Mitigation Mechanism | Limitation |
| --- | --- | --- | --- |
| **Unintended tractive effort** (H-01, H-15) | Throttle sensor fault (open, short, drift) | Dual redundant pots with >5% discrepancy check (FSR-01) on both MCUs; throttle limit switch override (FSR-18); rate limiter (FSR-03) | Both MCUs independently read throttle; either detecting discrepancy triggers SSO via independent power kill |
| **Unintended tractive effort** (H-01, H-15) | Software error in tractive effort calculation | Torque command vs. measured current plausibility (FSR-02); boot CRC (FSR-19); ECC RAM (FSR-20); windowed WDT (FSR-15) | Plausibility check is software-based; common-cause with main control possible |
| **Unintended tractive effort** (H-01, H-15) | MCU latch-up / runaway | Windowed watchdog ≤50 ms (FSR-15); breakpoint HW PWM disable (FSR-14) | WDT is on-chip; common-cause with MCU failure possible |
| **Loss of tractive effort** (H-03, H-03a) | Fault-triggered safe state entry | Immediate SSO on fault (FSR-05); detection-to-SSO latency minimized (FSR-14, FSR-15, six SSO pathways) | No torque shaping on fault: every fault produces an immediate torque step to zero. Accepted residual risk (Section 2.3); detection speed is the primary mitigation |
| **Loss of tractive effort** (H-03, H-03a) | External system loss (CAN) | CAN heartbeat timeouts with safe defaults (FSR-17); graceful degradation | IO board loss → immediate SSO (abrupt torque loss possible; accepted residual risk) |
| **Over-torque** (H-06) | Excessive tractive effort command | Software torque limit LUT (FSR-07); torque command plausibility (FSR-02); coprocessor independent current monitoring with cross-check | DESAT handles hard short-circuit (<2 us). Regular overcurrent detected within 10 us by dual-MCU analog watchdog monitoring - sufficient for safe state off without hardware damage. No separate HW OCP comparator required. |
| **Over-torque** (H-06) | Short-circuit / shoot-through | NCV57100 DESAT (<2 us) (FSR-13); complementary anti-shoot-through inputs (FSR-12); active Miller clamp | Gate driver protections are hardware-level (Section 2.7); coprocessor independently monitors all 6 PWM output pairs for deadtime violations and stuck-on/stuck-off |
| **Over-temperature** (H-07) | IGBT thermal runaway | 2 IGBT NTC sensors, 1oo2 voting (FSR-08), plus 1 DC link capacitor NTC; progressive derating; critical threshold → SSO | 1oo2 voter implemented; a stuck-high sensor can cause unnecessary derating (known trade-off: safety over availability). Note: derating applies to *pre-fault* thermal management only; once a fault threshold is crossed, response is immediate SSO. |
| **Encoder loss** (H-08) | Loss of rotor position feedback | Encoder timeout detection <100 ms (FSR-09); immediate SSO on loss | Single encoder (no redundancy); bounded sensorless fallback if implemented |
| **DC link overvoltage** (H-10) | Regen-induced bus rise | Isolated ADC monitoring (FSR-11); regen disable at warning threshold; SSO at critical threshold | None significant |
| **HV isolation** (H-09) | HV exposure via isolation loss or open interlock | HVIL continuous monitoring (FSR-10); interruption → immediate PWM disable + contactor open request on CAN1 | Contactor actuation and weld detection are BMS/OEM-domain (Section 1.3); the VCU-side obligation ends at the request |
| **Safe state failure** (H-13, H-14) | Cannot reach SSO; latched tractive effort | Six redundant SSO pathways (Path 2a and Path 2b are redundant channels of one 1oo2 power-kill pathway): Path 1 = TIM1_BKIN hardware (<100 ns); Path 2a/2b = 1oo2 gate-drive power kill (GATE_DRIVE_PWR1_ENABLE / GATE_DRIVE_PWR2_ENABLE); Path 3 = shared 3.3 V rail loss → NCV57100 pull-down; Path 4 = GATE_DRIVE_RESET; Path 5 = coprocessor watchdog → NRST; Path 6 = coprocessor independent fault trigger. WDT reset (FSR-15); POST before PWM enable (FSR-16). | 1oo2 power kill: either GATE_DRIVE_PWR1_ENABLE or GATE_DRIVE_PWR2_ENABLE going low achieves SSO. Each has independent feedback (GATE_DRIVE_PWR1_FB, GATE_DRIVE_PWR2_FB). Coprocessor provides fully independent safe state actuation. Six pathways provide extensive redundancy against any single-point failure. |
| **Gate driver fault** (H-16, H-17) | DESAT/UVLO not detected; PWM deadtime violation | OR'd FLT input to STM32 (FSR-13); DESAT self-test at POST (FSR-16); complementary inputs (FSR-12) | OR'd FLT monitored by both MCUs; coprocessor additionally monitors the combined READY signal and all 6 PWM outputs for independent fault diagnosis |

> **How to read this table:** Each row maps a hazard category to the specific failure modes that could cause it, the mitigation mechanisms in the current architecture that address those failure modes, and the known limitations of those mitigations. The left column is the **what could go wrong**; the middle column is the **how we prevent or detect it**; the right column is the **why this might not be enough**. The limitations are addressed in Section 9 (Gap Analysis).

## Technical Parameters

**Table 4 - Key Technical Parameters (Core Platform)**

| Parameter | Value / Range |
| --- | --- |
| Traction motor type | 3-phase PMSM, FOC controlled |
| DC link voltage / phase current | Set by the attached power stage; the control module itself has no intrinsic DC link voltage or phase current limit |
| DC link source | Any compatible DC source |
| Main MCU | STM32H723ZG, 550 MHz Cortex-M7, ECC RAM, FDCAN1/2, HRTIM |
| Safety coprocessor | STM32G474RCTx, 170 MHz Cortex-M4+FPU, 3x FDCAN |
| Gate driver | onsemi NCV57100 x6 (AEC-Q100) |
| Isolation | >5 kV<sub>rms</sub> (reinforced) per channel |
| Power stage | External to the control module; 3-phase 2-level IGBT bridge on the reference board |
| Fail-safe default | Six-switch-open (SSO) via NCV57100 active pull-down - immediate, no software ramp-down (Section 2.3) |
| Safe function mapping (industrial vocabulary) | SSO ≙ STO per IEC 61800-5-2; SS1 deliberately not implemented (Section 2.3) |
| Gate kill paths | Six redundant SSO pathways (TIM1_BKIN, 1oo2 gate-drive power kill, shared 3.3 V rail loss, GATE_DRIVE_RESET, coprocessor NRST, coprocessor independent trigger) |
| FLT outputs | All six NCV57100 FLT OR'd to fault input read by both MCUs |
| Regenerative braking | Application-dependent (see profile documents) |

Application-specific parameters (vehicle mass, speed, controllability assumptions) are defined in the applicable profile document, not in this core table.

## Application Software Trust Model - Node-Based Code Generation

The OpenVVVF platform is intended to support user-defined control, modulation, and application-layer logic produced by a **node-based code generation tool**, running on top of a **base safety-tested firmware image**. The following trust model applies and is a platform assumption for all safety claims in this document:

> **Generated code is an untrusted element.**
>
> 1. All safety mechanisms defined in this document - input plausibility and discrepancy checking (FSR-01, FSR-02), rate limiting (FSR-03), torque limiting (FSR-07), temperature voting (FSR-08), encoder-loss detection (FSR-09), HVIL and DC link supervision (FSR-10, FSR-11, FSR-21), watchdog and challenge/response (FSR-15), POST (FSR-16), boot CRC (FSR-19), ECC handling (FSR-20), and all six SSO actuation pathways - **shall reside in the base firmware image and shall be independent of, and not modifiable by, generated application code** (freedom from interference).
> 2. Generated code may *request* torque within platform-enforced limits; it shall not be able to inhibit, bypass, delay, or reconfigure any safety mechanism or safe-state path.
> 3. The safe state (immediate SSO, Section 2.3) is hardware-enforced and does not depend on any property of generated code.
> 4. The code generator itself is a software tool whose output affects safety-relevant behavior. Under ISO 26262-8 tool-confidence terminology it shall be treated as requiring at least **TCL2/TCL3-level confidence**; no tool qualification has been performed and this is recorded as an open limitation (Section 9, GAP-SW-04).
> 5. Interface contract between generated code and the base image (allowable request ranges, update rates, permitted modulation schemes, sanity envelopes) shall be defined in a separate Interface Control Document. This HARA assumes such a contract exists and is enforced by the base image.
> 6. The safety coprocessor executes only fixed, project-maintained firmware; no generated code runs on the coprocessor, and its monitoring and actuation functions are trusted without qualification. On the main MCU, the safety-critical base image (fault detection and response, safe state management) is likewise outside the generated-code surface.

## Gate Drivers (Non-ASIL)

Six **onsemi NCV57100** isolated high-current IGBT gate drivers. Automotive-qualified per AEC-Q100. These devices are **not ISO 26262 safety elements** - no safety manual, FMEDA, or ASIL claim is available.

**Table 5 - NCV57100 Safety-Relevant Features**

| Feature | Specification | Safety Role | ASIL Credit |
| --- | --- | --- | --- |
| Reinforced isolation | >5 kV<sub>rms</sub>, 1200 V working | HV-to-logic barrier | Hardware only |
| Complementary inputs (IN+/IN−) | Internal anti-shoot-through logic | Prevents HS+LS simultaneous ON | None (not ASIL-rated) |
| DESAT protection | V<sub>TH</sub> = 6.5 V, prog. blanking | Short-circuit detection every ON cycle | None (not ASIL-rated) |
| Soft turn-off | Controlled slope on DESAT | Limits di/dt overvoltage | None (not ASIL-rated) |
| Active Miller clamp | Internal N-FET | Prevents dV/dt turn-on | None (not ASIL-rated) |
| Gate active pull-down | OUT pulled low on fault/UVLO | Ensures IGBT OFF | None (not ASIL-rated) |
| UVLO | V<sub>UVLO+</sub> = 12.2 V, V<sub>UVLO−</sub> = 11.3 V | No operation at low gate drive | None (not ASIL-rated) |
| Negative gate drive | VEE2 to −9 V | Robust OFF-state | Hardware only |
| FLT output | Open-drain, active low | Fault reporting to MCU | OR'd; monitored by both MCUs |

> **Non-ASIL Gate Driver Implications:** The NCV57100 internal protections provide valuable hardware-level risk reduction but cannot be counted toward ASIL metrics. The OR'd FLT output is monitored by **both** the main MCU (via TIM1_BKIN) and the coprocessor (via independent GPIO). Either MCU detecting FLT can trigger SSO. The coprocessor additionally monitors the combined NCV57100 READY output and can detect a stuck-active FLT line through its independent PWM output monitoring (all 6 phase high/low signals). This dual monitoring closes the single-point FLT path gap.

## Future Considerations

> **Safety Coprocessor - STM32G474RCTx (Implemented)**
>
> The Safety Coprocessor is a **STM32G474RCTx** (170 MHz Cortex-M4+FPU, 3x FDCAN, advanced motor-control timers) that operates as an **independent safety monitor** alongside the main STM32H723ZG. It is part of the current design and provides:
>
> - **Independent gate driver supply kill** (GATE_DRIVE_PWR2_ENABLE, Path 2b) - 1oo2 with main MCU's GATE_DRIVE_PWR1_ENABLE. Independent feedback via GATE_DRIVE_PWR2_FB.
> - **Independent ADC monitoring** of all current sensors, temperature sensors, and encoder signals via voltage divider networks
> - **Challenge-response watchdog** with the main STM32 via inter-MCU UART
> - **Independent PWM output monitoring** - all 6 phase high/low signals monitored for deadtime violations, stuck-on, stuck-off
> - **Independent gate driver FLT monitoring** via OR'd fault line + combined READY signal
> - **Independent CAN bus snooping** via FDCAN2 + FDCAN3 - cross-checks torque commands and heartbeat timing
> - **Bidirectional NRST** - coprocessor can reset main MCU; main MCU can reset coprocessor
>
> The coprocessor enables **target ASIL D claims for SG-01 and SG-13 via ASIL B(D) + ASIL B(D) decomposition**. Both MCUs must independently agree that operation is safe; either can trigger SSO.

# Operational Situations

Operational Situations are **application-specific** and are defined in the applicable Application Profile document:

- OV-SAF-HARA-PROF-MOTO - Motorcycle Application Profile

Environmental operating conditions for the core platform hardware: ambient −20 °C to +50 °C (storage/qualification −40 °C to +85 °C per front matter), humidity 0–100% condensing, altitude 0–3,000 m MSL, high-vibration mobile mounting. Profiles shall refine these per application.

# Hazard Identification (HAZID) - Core Platform

Hazards are identified via systematic Functional Hazard Analysis (FHA) combining top-down FMEA perspective, expert judgment on power electronics and traction drive dynamics, and ISO 26262 hazard category checklists. Core-platform hazards are stated at the **drive boundary** (torque production and HV state) with application-neutral harmed parties. Application-specific hazards are defined in the applicable profile document and are additive to this table.

**Table 6 - Identified Hazards (Core Platform)**

| ID | Malfunctioning Behavior | Drive-Boundary Hazard | Potentially Affected Parties (application-dependent) |
| --- | --- | --- | --- |
| **H-01** | Unintended positive tractive effort production not requested by operator | Unintended acceleration / unintended driven-load motion | Operator, bystanders, other road users |
| **H-02** | Unintended reverse tractive effort | Unexpected rearward motion | Operator, nearby persons |
| **H-03** | Sudden loss of tractive effort (inability to produce requested tractive effort) | Unexpected loss of drive; application-dependent consequences (collision risk, process interruption) | Operator, following vehicles, process equipment |
| **H-04** | Inability to produce requested regenerative braking tractive effort | Extended stopping distance / loss of expected braking contribution | Operator, following vehicles |
| **H-05** | Unintended regenerative braking tractive effort (uncommanded) | Unexpected deceleration, loss of stability | Operator, following vehicles |
| **H-06** | Excessive tractive effort exceeding design limits | Wheel spin / load over-speed, loss of traction, component damage | Operator, equipment |
| **H-07** | Failure to limit tractive effort during over-temperature | Fire, thermal damage, burn injury | Operator, nearby persons |
| **H-08** | Motor overspeed due to loss of rotor position feedback | Loss of FOC control, unpredictable tractive effort | Operator, equipment |
| **H-09** | HV electrical isolation failure | Electric shock, potentially fatal | Operator, service personnel |
| **H-10** | DC link bus overvoltage not detected / not limited | Component rupture, arc flash, fire | Operator, nearby persons |
| **H-12** | IGBT shoot-through (HS and LS simultaneously ON) | Immediate DC link short, fire, catastrophic failure | Operator, nearby persons |
| **H-13** | Failure to execute safe state (SSO) on detected fault | Hazardous operation continues despite fault | Operator, nearby persons |
| **H-14** | Corrupted or latched tractive effort command held indefinitely | Persistent unintended acceleration or braking | Operator, nearby persons |
| **H-15** | Incorrect tractive effort command due to software error | Non-requested tractive effort, unexpected drivability | Operator, nearby persons |
| **H-16** | Gate driver fault (DESAT/UVLO/TSD) not acted upon | Phase loss, imbalance, unexpected tractive effort | Operator, equipment |
| **H-17** | PWM deadtime violation or stuck-on not detected upstream | Shoot-through, DC link short, fire | Operator, nearby persons |

Application-profile-specific hazards:

| ID | Defined In | Summary |
| --- | --- | --- |
| **H-03a** | OV-SAF-HARA-PROF-MOTO | Loss of tractive effort in an application-specific operating situation (defined and assessed in the profile) |

# Risk Assessment Methodology

Severity, Exposure, and Controllability classifications follow ISO 26262-3:2018 Tables 1–3 for road-vehicle profiles. Non-road profiles use the equivalent domain classification (future profile documents). The class definitions below are reproduced for convenience; the per-hazard ratings are **application-specific and are assigned in the annexes**, not in this core section.

### Severity (ISO 26262-3 Table 1)

| Class | Description |
| --- | --- |
| **S1** | Light and moderate injuries |
| **S2** | Severe, life-threatening (survival probable) |
| **S3** | Life-threatening to fatal (survival uncertain) |

### Exposure (ISO 26262-3 Table 2)

| Class | Description |
| --- | --- |
| **E1** | Very low probability (<1% of time) |
| **E2** | Low (1–10% of time) |
| **E3** | Medium (10–50% of time) |
| **E4** | High (>50% of time) |

### Controllability (ISO 26262-3 Table 3)

| Class | Description |
| --- | --- |
| **C1** | Simply controllable |
| **C2** | Normally controllable (requires attention/skill) |
| **C3** | Difficult to control or uncontrollable |

> **Target Assignment Policy (deliberate conservatism):** Profile documents assign ASIL targets per ISO 26262-3 Table 4, and may then **raise a target by up to one level** for hazards whose mitigation depends substantially on software integrity (e.g., software plausibility checks, software fault handling), where a single systematic software fault could defeat multiple nominal mitigations simultaneously. This policy intentionally produces some targets above the Table 4 lookup value (e.g., H-01, H-13, H-15 at ASIL D from S3/E3/C3 inputs). The elevation is a design choice, not a Table 4 result, and shall be read as such.

# Safety Goals - Core Platform

Safety Goals are platform-level. The **Target** integrity level shown is assigned by the applicable profile document; each profile shall assign targets per its own S/E/C assessment. "Achievable" reflects the current architecture's capability, not verified compliance.

**Table 7 - Safety Goals**

| SG | Safety Goal | Target (Ref. Profile) | Achievable | Hazards | Safe State |
| --- | --- | --- | --- | --- | --- |
| **SG-01** | Prevent unintended positive tractive effort when the operator is not requesting propulsion. Unintended tractive effort shall not exceed 10 Nm for more than 200 ms before safe state entry. | D | D | H-01, H-15 | SSO, zero tractive effort |
| **SG-02** | Prevent unintended reverse tractive effort. Reverse requests outside permitted conditions shall be rejected; failure → safe state. | B | B | H-02 | SSO, zero tractive effort |
| **SG-03** | On loss of tractive effort due to fault, transition to the torque-free state immediately; fault-detection-to-SSO latency shall not exceed 200 ms (FSR-05). | C | C | H-03, H-03a | SSO, zero tractive effort (immediate) |
| **SG-04** | Monitor regenerative braking availability; on loss of regen, the operator shall be informed and friction brakes shall remain available (independent system). | A | A | H-04 | Zero regen |
| **SG-05** | Prevent unintended regenerative braking. Uncommanded regen >10 Nm for >200 ms → safe state. | C | C | H-05 | SSO, zero tractive effort |
| **SG-06** | Limit max tractive effort to calibrated max. Over-torque >110% → safe state within 100 ms. | C | C | H-06 | SSO, zero tractive effort |
| **SG-07** | Detect over-temperature, progressively derate (pre-fault thermal management). Critical temp → safe state. | B | B | H-07 | SSO, monitoring |
| **SG-08** | Detect loss of rotor position → safe state within 100 ms. | C | C | H-08 | SSO, zero tractive effort |
| **SG-09** | Maintain HV isolation (>500 Ohm/V). Isolation fault → safe state. | A | A | H-09 | SSO, contactor open request |
| **SG-10** | Detect DC link bus overvoltage, limit regen. Critical OV → safe state. | B | B | H-10 | SSO, regen disable |
| **SG-12** | Prevent IGBT shoot-through. Risk → PWM disable <10 us via hardware. | C | C | H-12 | SSO, HW PWM kill |
| **SG-13** | Achieve safe state (SSO) within 200 ms of any fault. Safe state entry shall be independent of the main control loop and of generated application code. | D | D | H-13, H-14 | SSO, HW-enforced |
| **SG-14** | Detect any NCV57100 fault (DESAT, UVLO, TSD) and transition to safe state. | C | C | H-16 | SSO, FLT detect |
| **SG-15** | Detect PWM deadtime violations and stuck-on faults. Deadtime collapse or stuck-high >100 us → safe state. | C | C | H-17 | SSO, PWM kill |

# Functional Safety Requirements

Requirements use "shall" for binding provisions and "should" for recommendations. "Tgt" is the target integrity level assigned by the applicable profile document; "Now" is the level achievable with the current architecture.

**Table 8 - Functional Safety Requirements (FSRs)**

| FSR | Requirement | Tgt | Now | SG |
| --- | --- | --- | --- | --- |
| **FSR-01** | The system shall read dual redundant tractive effort control pots on both MCUs. A discrepancy >5% or an out-of-range reading on either channel, detected by either MCU, shall cause transition to safe state. | D | D | SG-01 |
| **FSR-02** | The system shall perform tractive effort command plausibility: commanded current reference vs. measured phase currents. Deviation >20% for >100 ms shall cause transition to safe state. | D | C | SG-01, SG-06 |
| **FSR-03** | The tractive effort control input shall be rate-limited. Max tractive effort application rate: 500 Nm/s (calibration parameter). | D | C | SG-01 |
| **FSR-04** | The system shall reject reverse tractive effort when speed >0. Reverse shall be permitted only when stationary AND explicitly selected. | B | B | SG-02 |
| **FSR-05** | On detection of any fault requiring safe state entry, the system shall transition to SSO **immediately**, without software-controlled torque ramp-down (Section 2.3). Safe state entry shall not depend on software execution beyond the detecting agent, and shall not be inhibitable by generated application code. Fault-detection-to-SSO latency shall not exceed 200 ms end-to-end. | C | C | SG-03 |
| **FSR-06** | The system shall monitor regenerative braking tractive effort continuously. Uncommanded regen >10 Nm for >200 ms shall cause transition to safe state. | C | C | SG-05 |
| **FSR-07** | Max tractive effort shall be limited by software LUT on both MCUs with cross-check. Dual-MCU independent current monitoring (STM32 analog watchdogs on both MCUs) shall detect overcurrent within 10 us. DESAT handles hard short-circuit (<2 us). | C | C | SG-06 |
| **FSR-08** | Two IGBT NTC temperature sensors (1oo2 voting) plus one DC link capacitor NTC. Derate at 90 °C; SSO at 105 °C (capacitor rating limit). Critical thresholds shall be stored in ECC memory. (The 90 °C / 105 °C thresholds apply to the DC link capacitor channel, whose devices are rated 105 °C.) | B | B | SG-07 |
| **FSR-09** | Encoder loss shall cause transition to safe state within 100 ms. No sensorless fallback is implemented (GAP-SW-03, closed). | C | C | SG-08 |
| **FSR-10** | HVIL shall be monitored continuously. Interruption shall cause immediate PWM disable + HV contactor open request on CAN1 (when a contactor controller is present) within 50 ms. | B | B | SG-09 |
| **FSR-11** | DC link bus voltage shall be monitored with isolated ADC. OV warning threshold → immediate regen disable. Critical OV → SSO within 50 ms. | B | B | SG-10 |
| **FSR-12** | NCV57100 complementary inputs (IN+/IN−) shall prevent HS+LS simultaneous conduction. Power-on self-test shall confirm. | C | A | SG-12 |
| **FSR-13** | NCV57100 DESAT detection shall be active on all six IGBTs. A DESAT event shall cause local PWM disable within <2 us, independent of MCU. | C | A | SG-12, SG-14 |
| **FSR-14** | The STM32 breakpoint input shall cause HW PWM disable within <10 us on any critical fault, independent of main CPU execution. | D | C | SG-13 |
| **FSR-15** | An independent windowed watchdog shall be maintained. Failure to service shall cause automatic PWM disable + system reset. Timeout ≤50 ms. | D | C | SG-13, SG-01 |
| **FSR-16** | Power-on self-test (POST) shall cover: ADC references, current sensor offsets, gate driver communications, encoder signal, HVIL continuity, watchdog, NCV57100 DESAT self-test. All checks shall pass before PWM enable. | D | C | SG-13 |
| **FSR-17** | CAN heartbeat timeouts shall apply safe-state defaults. IO board heartbeat (1 s) loss → safe-state defaults (brake pressed, kickstand down) and tractive effort restricted to zero. CAN1 source-management heartbeat (5 s, when such a node is present) loss → tractive effort restricted to zero. | C | C | SG-01 |
| **FSR-18** | The tractive effort control limit switch shall be monitored independently of the analog pots. Activation shall override any analog value and command zero tractive effort. | D | C | SG-01 |
| **FSR-19** | Boot-time CRC-32 shall be computed over safety-critical code and calibration data. Mismatch → PWM enable prevented, fault logged. | D | C | SG-01, SG-13 |
| **FSR-20** | ECC RAM shall be used for all safety-critical variables. Single-bit errors shall be corrected (SECDED). Double-bit errors → safe state. | D | C | SG-15 |
| **FSR-21** | DC link bus undervoltage shall be monitored. UV → tractive effort derate; critical UV → safe state. Prevents overcurrent due to insufficient DC link voltage. | B | B | SG-03, SG-10 |
| **FSR-22** | Generated application code (Section 2.6) shall not be able to inhibit, bypass, delay, or reconfigure any safety mechanism or safe-state path. All torque requests from generated code shall pass through the platform-enforced limits (FSR-02, FSR-03, FSR-07). | D | C | SG-01, SG-13 |

# Current Design Coverage

**Table 9 - Honest Assessment of Design vs. FSRs**

Status vocabulary used throughout this document: **Covered** (implemented in current design), **Planned** (specified, not yet implemented), **Partial** (partially implemented), **To implement** (not started), **Limited** (implemented with documented constraint). No status in this document shall be read as "verified by test" - verification evidence is produced only by execution of the fault-injection test plan OV-TEST-FAULT-INJECTION and is recorded separately per that plan's evidence framework.

| FSR | Tgt | Now | Status | Existing / Planned | Gap |
| --- | --- | --- | --- | --- | --- |
| FSR-01 | D | D | Covered | Dual pots on both MCUs; independent voters | Achieved via dual-MCU ASIL B(D) decomposition |
| FSR-02 | D | D | Planned | Commanded vs. measured cross-check on both MCUs | Not yet implemented in firmware (Phase 2) |
| FSR-03 | D | C | Covered | Rate limiter implemented | Part of SG-01 decomposition; main MCU handles rate limiting |
| FSR-04 | B | B | Planned | Reverse interlock: speed >100 rpm → reverse clamped | Not yet implemented in firmware |
| FSR-05 | C | C | Covered | Immediate SSO on fault (design decision, Section 2.3); hardware-enforced via six SSO pathways | Ramp-down explicitly rejected (GAP-HW-02 closed, Section 9.2) |
| FSR-06 | C | C | Planned | Uncommanded regen monitor on both MCUs | Not yet implemented in firmware (Phase 2) |
| FSR-07 | C | C | Covered | Dual-MCU independent current monitoring (STM32 analog watchdogs) | 10 us detection; DESAT for hard shorts |
| FSR-08 | B | B | Planned | Dual IGBT temp sensors + DC link capacitor sensor (hardware) | 1oo2 voter software not yet implemented (Phase 2) |
| FSR-09 | C | C | Limited | Single encoder (external constraint) | Immediate SSO on loss; no sensorless fallback (GAP-SW-03 closed) |
| FSR-10 | B | B | Covered | HVIL digital input implemented | Verify ≤50 ms E2E |
| FSR-11 | B | B | Covered | DC link isolated ADC | Define OV thresholds |
| FSR-12 | C | A | Covered | NCV57100 complementary inputs | No ASIL credit claimed |
| FSR-13 | C | A | Covered | NCV57100 DESAT on all six | No ASIL credit claimed |
| FSR-14 | D | D | Covered | Breakpoint input to HW PWM disable + 1oo2 gate drive power kill | Six redundant SSO pathways; either MCU achieves SSO independently |
| FSR-15 | D | C | Covered | Independent watchdog on STM32 | On-chip WDT subject to common cause |
| FSR-16 | D | C | Partial | NCV57100 DESAT self-test exists | Expand to all safety functions |
| FSR-17 | C | C | Planned | 1-second heartbeat timeout confirmed | Safe defaults on CAN loss |
| FSR-18 | D | C | Covered | Limit switch input implemented | Verify override precedence |
| FSR-19 | D | C | To implement | STM32 flash CRC peripheral available | Add boot-time CRC check |
| FSR-20 | D | C | Covered | STM32H723 has ECC RAM | Enable + DED handler to safe state |
| FSR-21 | B | B | Planned | DC link ADC can measure UV | Define UV thresholds and response |
| FSR-22 | D | C | Planned | Base-image enforcement of interface contract | Codegen toolchain under development; contract ICD to be written (GAP-SW-04) |

# Gap Analysis

## Architecture Gaps

> **GAP-ARCH-01: Single-Core MCU Without Independent Monitor (P0)**
>
> **Issue:** All safety mechanisms execute on one STM32H723. A single MCU fault (clock failure, latch-up, supply collapse) can disable all safety functions simultaneously. The independent watchdog is on-chip and subject to common-cause failure.
>
> **Impact:** SG-01 and SG-13 target ASIL D, achievable via dual-MCU ASIL B(D) + ASIL B(D) decomposition (Table 7). The remaining gap is the formal ASIL D claim, pending the Dependent Failure Analysis (LIMIT-08).
>
> **Mitigation path:** Dual-MCU ASIL B(D) decomposition - implemented. Main MCU + coprocessor each achieve ASIL B(D); combined via 1oo2 voter on safe state actuation.

> **GAP-ARCH-02: Power Kill Without Feedback Monitoring (P1, was P0)**
>
> **Issue:** The GATE_DRIVE_PWR1_ENABLE (main MCU) and GATE_DRIVE_PWR2_ENABLE (coprocessor) paths provide a 1oo2 active SSO mechanism. **Feedback:** GATE_DRIVE_PWR1_FB and GATE_DRIVE_PWR2_FB provide independent per-supply status. When the NCV57100 detects VDD_UVLO (loss of gate drive supply), it asserts FLT (active low), which both MCUs can read. The 1oo2 architecture means a stuck-high GATE_DRIVE_PWR1_ENABLE is not a single-point failure - the coprocessor can still achieve SSO via GATE_DRIVE_PWR2_ENABLE (Path 2b), GATE_DRIVE_RESET (Path 4), or NRST (Path 5). The shared 3.3V rail provides a passive SSO path (NCV57100 pull-down on VDD loss, Path 3).
>
> **Impact:** SG-13 targets ASIL D via ASIL B(D) decomposition. Six SSO pathways exist (see Section 2.2). The 1oo2 power kill with independent feedback provides diagnostic coverage for the supply kill path.
>
> **Mitigation path:** Implemented - GATE_DRIVE_PWR1_FB (main MCU) and GATE_DRIVE_PWR2_FB (coprocessor) provide independent per-supply feedback. Six SSO pathways (TIM1_BKIN; 1oo2 power kill via GATE_DRIVE_PWR1_ENABLE / GATE_DRIVE_PWR2_ENABLE; 3.3 V rail loss; GATE_DRIVE_RESET; coprocessor watchdog/NRST; coprocessor independent fault trigger) provide extensive redundancy. Verify feedback paths in C-17, C-26, C-27, S-10, and S-11.

> **GAP-ARCH-03: Gate Driver Protection Credit - CLOSED**
>
> **Issue:** NCV57100 internal protections are hardware-level and not ASIL-rated (Section 2.7). The OR'd FLT output is a single shared wire, though it is read by both MCUs.
>
> **Impact assessment:** Reviewed per affected safety goal. SG-15 (PWM deadtime violations) does not depend on the gate drivers at all - it is enforced by the coprocessor's independent monitoring of all 6 PWM output pairs; unaffected. SG-12 (shoot-through) is covered by the NCV57100 complementary inputs as the hardware first line, with coprocessor deadtime/stuck monitoring and DESAT (SG-14) as independent detection - no gap in practice. SG-14 (gate driver fault detection) retains one diagnosed path concern - a stuck-active or stuck-inactive OR'd FLT wire - which is caught by the coprocessor's combined READY monitoring and its PWM output cross-check (a real gate fault that the FLT wire fails to report still appears as anomalous phase switching). The residual limitation is the absence of manufacturer qualification data (safety manual/FMEDA), which is not available for this part; no ASIL credit is claimed for the internal protections anywhere in this document.
>
> **Resolution:** Closed - analysis complete. No safety goal depends on an ASIL rating of the gate driver; the monitoring coverage above addresses the shared FLT wire. Verification of the cross-check logic remains in C-14, C-15, C-16.

## Component and Software Gaps

> **GAP-HW-01: Hardware Overcurrent Detection - CLOSED (Not Required)**
>
> Hard short-circuit protection is handled by NCV57100 DESAT (<2 us). Regular overcurrent (below the DESAT threshold) is detected within **10 us by the STM32 analog watchdogs**: both the main STM32H723 and the coprocessor STM32G474 independently monitor all four current sense channels with hardware analog watchdog comparators, so detection does not depend on software sampling rate. Either MCU detecting overcurrent triggers SSO via its independent gate drive power kill path, providing full redundancy - and the coprocessor side runs only fixed, trusted firmware (Section 2.6), so the redundant path does not share the main MCU's software fault surface. **Closed - dual-MCU analog watchdog monitoring is sufficient.**

> **GAP-HW-02: Tractive Effort Ramp-Down - CLOSED (Rejected by Design Decision)**
>
> Software-controlled torque ramp-down on fault (≤200 Nm/s before SSO) was evaluated and **rejected** (Section 2.3): a controlled ramp requires a trustworthy controller, which cannot be assumed once a fault has been detected; hardware paths (DESAT, TIM1_BKIN) force immediate SSO regardless; and a ramping state machine in the base safety image would add safety-critical states and verification burden while being incompatible with the generated-code trust model (Section 2.6). The requirement is replaced by FSR-05 (immediate SSO; detection-to-SSO ≤200 ms). The resulting abrupt-torque-loss exposure is recorded as accepted residual risk for H-03/H-03a (Section 2.3; applicable profile document). **Closed - no implementation planned.**

> **GAP-SW-01: No Boot CRC (P1)**
>
> FSR-19: Boot CRC verification is not yet implemented. Add a boot-time CRC-32 using the STM32 CRC peripheral to validate safety-critical code and calibration data before PWM enable.

> **GAP-SW-03: Sensorless Fallback Policy - CLOSED**
>
> Policy: immediate SSO on encoder loss (FSR-09). No sensorless fallback mode is implemented; a bounded fallback would require trusting speed estimation derived from potentially faulted sensing, which is incompatible with the Section 2.3 philosophy.

> **GAP-SW-04: Codegen Tool Confidence and Interface Contract Undefined (P1, new in v5.0)**
>
> The node-based code generation toolchain (Section 2.6) is under development. Open items: (1) no software tool confidence assessment of the generator (ISO 26262-8 TCL); (2) the interface contract between generated code and the base safety image (FSR-22) is not yet documented; (3) freedom-from-interference between generated code and safety mechanisms has not been analyzed or tested. Mitigation: define the contract ICD, enforce limits in the base image, and extend the fault injection plan with generated-code fault cases (e.g., generated code requests out-of-envelope torque, generates no request, or corrupts its own state) before any public release of the codegen feature.

## Gap Summary

**Table 10 - Gap Mitigation Priority**

| Gap | Priority | Mitigation | Effort |
| --- | --- | --- | --- |
| Dual MCU with coprocessor | **RESOLVED** | STM32G474RCTx implemented - 1oo2 power kill, independent ADC, challenge/response watchdog, independent CAN snoop | Complete |
| HW overcurrent detection | **CLOSED** | Dual-MCU STM32 analog watchdogs detect overcurrent within 10 us - sufficient for SSO without damage. | N/A |
| Torque ramp-down on fault | **CLOSED - REJECTED** | Replaced by FSR-05 immediate SSO (Section 2.3). Residual risk documented. | N/A |
| Power kill feedback monitoring | **P1** | GATE_DRIVE_PWR1_FB and GATE_DRIVE_PWR2_FB provide independent per-supply feedback. Verify in C-17, C-26, C-27, S-10, and S-11. | Low |
| Gate driver protection credit | **CLOSED** | No SG depends on gate-driver ASIL rating (GAP-ARCH-03). Coprocessor monitors FLT, READY, all 6 PWM outputs. Verify cross-check logic in C-14, C-15, C-16. | Low |
| Boot CRC | **P1** | STM32 CRC peripheral | Low |
| Sensorless policy | **CLOSED** | Immediate SSO on encoder loss (FSR-09); no fallback mode | N/A |
| Codegen tool confidence + contract | **P1** | Contract ICD, base-image enforcement, generated-code fault cases | Medium |
| No DFA (ISO 26262-9) | **P0** | Dependent Failure Analysis | Medium |
| No EMI/EMC pre-compliance | **P1** | CISPR 25 pre-compliance test | Medium |

**Note:** With the dual-MCU architecture (STM32H723 + STM32G474 coprocessor), ASIL D is achievable for SG-01 and SG-13 via ASIL B(D) decomposition. The four hazards previously limited to ASIL A (H-06, H-16, H-17, and H-13 safe state failure) are now fully covered: H-06 by dual-MCU independent current monitoring (10 us analog watchdog detection + independent power kill), H-16 by coprocessor FLT/READY/PWM monitoring, H-17 by coprocessor independent deadtime monitoring, and H-13 by six redundant SSO pathways. GAP-HW-01 (HW overcurrent detection) is closed - dual-MCU analog watchdog monitoring is sufficient. No hazards remain below their target ASIL under the applicable profile assessment.

# Fault Injection Test Plan

The fault-injection test plan that validates the safety mechanisms, safe-state entry paths, and timing budgets defined in this HARA has been extracted to a standalone document in the Testing tree: [OV-TEST-FAULT-INJECTION - Fault Injection Test Plan](../../Testing/Fault-Injection-Test-Plan/Index.md). It defines 80 tests in three categories - component-level (43 tests, C-01 to C-50 with numbering gaps), system-level (S-01 to S-19), and integration-level (I-01 to I-18) - plus 12 environmental test stubs (E-01 to E-12, deferred type tests), with per-test executability status, evidence requirements, pass/fail criteria, Safety Goal / FSR / hazard traceability matrices, and a recommended execution order with hardware damage risk classification. Every Safety Goal, Functional Safety Requirement, and identified hazard in this document is covered by at least one executable test case in that plan. Test execution records and evidence are maintained separately as described in the plan.

# Implementation Roadmap

## Phase 1: Safety-Critical Foundation (Immediate)

**Table 11 - Phase 1 - Safety-Critical Foundation**

| Gap | Action | Effort | Validation |
| --- | --- | --- | --- |
| GAP-HW-01 | **CLOSED** - Dual-MCU STM32 analog watchdog monitoring (10 us). | N/A | C-06, C-07, S-09, S-15 |
| GAP-HW-02 | **CLOSED - REJECTED** - Immediate SSO adopted (Section 2.3); FSR-05 rewritten accordingly. | N/A | S-03, S-04, S-11: verify immediate SSO and latency budget |
| GAP-SW-01 | Implement boot CRC-32 (STM32 CRC peripheral) over safety-critical code + calibration before PWM enable. | Low | C-20, C-39 |
| GAP-SW-03 | ~~Define sensorless fallback policy~~ - closed: immediate SSO on encoder loss (FSR-09); no fallback mode. | N/A | C-09 |

## Phase 2: Monitors and Platform Hardening (Short Term)

**Table 12 - Phase 2 - Monitors and Platform Hardening**

| Item | Action | Effort | Validation |
| --- | --- | --- | --- |
| FSR-06 | Implement uncommanded regen monitor (>10 Nm for >200 ms → safe state). | Medium | S-05, S-17 |
| FSR-02 | Implement command-vs-measured current plausibility (>20% for >100 ms → safe state). | Medium | C-06, C-07 |
| FSR-17 | Implement CAN heartbeat timeouts with safe-state defaults. | Medium | I-01, I-02 |
| FSR-08 | Implement 1oo2 IGBT temperature voter; thresholds in ECC memory. | Medium | C-08, C-45 |
| FSR-22 / GAP-SW-04 | Define the codegen interface contract ICD; implement base-image enforcement of the torque-request envelope; add generated-code fault cases to the test plan. | Medium | Generated-code fault cases (to be defined) |
| GAP-TEST-01 | Define a dedicated SG-04 loss-of-regen test (command regen, suppress inverter response, verify operator indication and friction-brake posture). | Low | New test ID at next test-plan revision |

## Phase 3: Test Execution and Validation

**Table 13 - Phase 3 - Test Execution and Validation**

| Activity | Effort | Description |
| --- | --- | --- |
| Execute component tests (C-01 to C-50, executable set) | High | Bench campaign per the recommended execution order in OV-TEST-FAULT-INJECTION. All evidence captured per that plan's evidence requirements. Fix failures before proceeding. |
| Execute system tests (S-01 to S-19) | High | Dyno campaign. Measure detection-to-SSO latencies, torque transitions, thermal behavior. |
| Execute integration tests (I-01 to I-18) | Medium | CAN simulation campaign. |
| Conditional LV-rail tests (C-21, C-22, C-24, C-25) | Low | Schedule once a small programmable LV bench supply is confirmed. |
| Application-level characterization (LIMIT-01) | High | In-application testing per the applicable profile, graduated operating points, known fault injection. Characterizes (does not "verify safe") the profile-level residual risk. |
| Verification report | Medium | Compile executed results and evidence references into the OpenVVVF Verification Report; assess against the pass/fail criteria in OV-TEST-FAULT-INJECTION; document residual risks. |

## Coprocessor Integration Validation

The STM32G474RCTx safety coprocessor is **part of the current hardware design**. The following table maps coprocessor capabilities to safety goals:

**Table 14 - Coprocessor Capability to Safety Goal Mapping**

| Feature | Description | Impact |
| --- | --- | --- |
| Independent throttle monitoring | Coprocessor reads throttle channels via independent ADC. Discrepancy >5% → GATE_DRIVE_PWR2_ENABLE low + GATE_DRIVE_RESET → SSO. | SG-01 → ASIL D |
| Independent current monitoring | Coprocessor samples all 4 current sense channels + REF. Cross-checks against main MCU torque command. Overcurrent → SSO within 100 ms. | SG-06, SG-07 → ASIL target |
| Challenge-response watchdog | Main MCU must respond within the window. Failure → NRST → reset → SSO. Not subject to on-chip common-cause. | SG-13 → ASIL D |
| PWM integrity monitoring | All 6 PWM output pairs monitored for deadtime violations, stuck-on, stuck-off, frequency anomalies. | SG-12, SG-14, SG-15 → ASIL C |
| 1oo2 gate drive power kill | GATE_DRIVE_PWR2_ENABLE in OR with GATE_DRIVE_PWR1_ENABLE. Independent feedback per channel. | SG-13 → ASIL D |
| Independent CAN snooping | FDCAN2 + FDCAN3 monitor both buses; cross-check torque commands, heartbeats, fault flags. | SG-01, SG-04, SG-05 → ASIL target |
| Independent temperature monitoring | All heatsink + motor temps via independent ADC; 1oo2 cross-check; capacitor channel derate 90 °C, SSO 105 °C. | SG-07 → ASIL target |
| FRAM logging | CY15B102Q-SXET 256 KB FRAM (main MCU SPI): fault logs, configuration, hour meter, odometer. Hardware WP. | SG-03 → ASIL C |

The dual-MCU architecture makes **ASIL D achievable for SG-01 and SG-13 via ASIL B(D) + ASIL B(D) decomposition** under the applicable profile assessment. The coprocessor firmware shall be validated alongside the main firmware - see C-14, S-16 through S-19, and I-16.

# References

**Table 15 - Referenced Standards and Documents**

| Reference | Title / Description |
| --- | --- |
| ISO 26262-1:2018 | *Road vehicles - Functional safety - Part 1: Vocabulary*. |
| ISO 26262-3:2018 | *Part 3: Concept phase*. HARA methodology, ASIL assignment, safety goal derivation. |
| ISO 26262-5:2018 | *Part 5: Product development at the hardware level*. Hardware architectural metrics. |
| ISO 26262-8:2018 | *Part 8: Supporting processes*. Software tool confidence (codegen tool, GAP-SW-04). |
| ISO 26262-9:2018 | *Part 9: ASIL-oriented and safety-oriented analyses*. Decomposition, DFA. |
| ISO 6469-3:2018 | *Electrically propelled road vehicles - Part 3: Electrical safety*. HV isolation (>500 Ω/V). |
| IEC 61800-5-2:2016 | *Adjustable speed drives - Safety - Functional*. STO/SS1/SLS vocabulary; Section 2.3 mapping. |
| IEC 61508 | *Functional safety of E/E/PE safety-related systems*. SIL terminology. |
| EN 50155:2021 | *Railway applications - Electronic equipment on rolling stock*. Reference for future rail profile. |
| AEC-Q100 | *Failure Mechanism Based Stress Test Qualification for ICs*. NCV57100 qualification. |
| STM32H723ZG | *STM32H723/733 Reference Manual (RM0433)*. STMicroelectronics. |
| STM32G474RCTx | *STM32G474/484 Reference Manual (RM0440)*. STMicroelectronics. |
| CY15B102Q-SXET | *2-Mbit Serial (SPI) F-RAM*. Infineon/Cypress. |
| NCV57100 | *Isolated IGBT Gate Driver with Desaturation Protection*. onsemi datasheet. |

Note: the Cincon EC7BW-110S12 DC/DC converter resides on the IO side and is **excluded from this HARA** (Section 1.3). It appears here neither as a safety element nor as a referenced component.

# Document History

**Table 16 - Revision History**

| Version | Date | Changes |
| --- | --- | --- |
| 1.0 | 2026-06-13 | Initial unified HARA document. |
| 2.0 | 2026-06-13 | Major expansion: 30 new component tests, 14 system tests, 11 integration tests, 12 environmental tests, execution order, damage risk classification. |
| 3.0 | 2026-06-14 | LIMIT-07/08/09; CORDIC subsection; dual ASIL evaluations; state machine table. |
| 3.1 | 2026-06-14 | S-16 to S-19 modulation transition tests. |
| 4.0 | 2026-07-08 | Dual-MCU primary architecture; six SSO pathways; GAP-HW-01 closed; 1oo2 power kill; ASIL B(D) decomposition. |
| 4.1 | 2026-07-13 | Editorial consistency pass; test counts corrected to 99; TPS389006-Q1 integrated; 2oo3 temperature voting. |
| 5.0 | 2026-07-30 | **Restructure into Core Platform (Layer 0) + Application Profiles (Layer 1):** motorcycle profile fully elaborated; car/rail/industrial profiles added as preliminary stubs (subsequently split out in v5.1). **Safe-state philosophy change:** software torque ramp-down on fault rejected; FSR-05 rewritten as immediate SSO with ≤200 ms detection-to-SSO budget (Section 2.3); SG-03, Table 3, S-03, S-04, S-11, S-13, I-01–I-03 updated; GAP-HW-02 closed as rejected. **Codegen trust model added** (Section 2.6, FSR-22, GAP-SW-04). **Test plan re-cut to available equipment:** executability status per test; E-series deferred to type tests; C-36 deferred; C-31–C-34 changed to energize-into-fault; C-50 changed to 1 kV applied-leakage alternative method; C-01–C-04/S-01 throttle via dual DC supplies; C-21/22/24/25 conditional on LV bench supply. **Evidence framework added:** status vocabulary, per-test Status/Evidence fields, naming convention, execution-record statement (Section 10.1–10.2.3). Cincon IO-side DC/DC explicitly excluded. Formal "shall" language adopted for requirements and acceptance criteria. |


| 5.1 | 2026-07-30 | Document set split: Core Platform (this document, OV-SAF-HARA-CORE) and Motorcycle Application Profile (OV-SAF-HARA-PROF-MOTO) are now separate documents. Core made profile-neutral; application annexes removed; car/rail/industrial profiles deferred to future documents. Formatting constrained for automated PDF generation (stable YAML front matter, document IDs, standard Markdown tables only). |
| 5.2 | 2026-07-30 | Consistency fixes: wrong test cross-references in Table 10 gap summary corrected (S-16–S-19 are modulation tests; power-kill feedback verified by C-17/C-26/C-27/S-10/S-11); contactor wording aligned with BMS-domain authority (VCU requests, BMS actuates); SG-04 reworded (availability monitoring, not availability guarantee); §2.3 residual-risk sentence upgraded with SSO-is-freewheel argument (aligns with OV-SAF-HARA-PROF-MOTO v1.1 H-03a re-rating to ASIL A); §2.7 retitled (coprocessor is implemented, not future); status-count phrasing corrected. |
| 5.3 | 2026-07-30 | Review pass: (1) deliberate-conservatism target policy added to §5 (targets may exceed Table 4 by one level for software-integrity-dependent hazards); (2) HV contactor references removed where out of VCU domain (BMS actuates contactors); (3) SG-04 coverage marked indirect with GAP-TEST-01 added (dedicated loss-of-regen test to be defined); (4) S-12 converted to offline bench test, no dyno; (5) LIMIT-05 rewritten - shared-rail common-cause is fail-safe by construction (Path 3) and TPS389006-Q1 hardware shutdown path (SIL 3 / ASIL D-capable per TI) documented; stray-statistic scan clean. |
| 5.4 | 2026-07-31 | HV contactor scope cleanup: contactor actuation, weld detection, and contactor-related hazards are BMS/OEM-domain and excluded (Section 1.3). H-11 and SG-11 removed; HARA now covers only VCU-side interface behavior (HVIL → PWM disable + CAN1 contactor open request per FSR-10). I-15 retains the VCU response to a BMS weld-detected message (fatal log + lockout). |
| 5.5 | 2026-07-31 | Application-neutrality pass: core document scoped to the platform only; application-specific wording moved to profile documents, which the core now references generically (Sections 1.3, 2.3, 4, 6, 10). No technical content changed. |
| 5.6 | 2026-07-31 | Core scoping cleanup: remaining application-specific descriptors removed; the core now points to the application profile documents generically without naming a reference application. No technical content changed. |
| 5.7 | 2026-07-31 | Review pass: (1) disclaimer reframed as best-effort functional safety practice with explicit goal of readiness for full compliance work; (2) no DC source type assumed - BMS references generalized to an optional CAN1 source management node; (3) Table 2 restructured (external interfaces table + per-layer descriptions); (4) power-stage-dependent parameters removed from the control-module table (module is power-stage agnostic); (5) gate-driver qualification stated once (Section 2.7), AEC-Q100 elsewhere; (6) GAP-ARCH-03 closed with per-SG analysis (SG-15 independent of gate drivers, SG-12 covered, SG-14 FLT-wire fault caught by coprocessor cross-check); (7) GAP-HW-01 re-based on STM32 analog watchdogs (10 us, dual-MCU redundant); (8) GAP-SW-02 removed, GAP-SW-03 closed (immediate SSO, no sensorless fallback); (9) method notes moved into Section 10.4, Section 10.2.4 removed, HV-safety equipment row removed; (10) tests removed as not executable or not meaningful on this hardware: C-37, C-38, C-40, C-44, C-46, C-47, C-48; C-43 key-cycle requirement replaced by heartbeat/plausibility restoration; (11) phase-to-phase shorts restructured one pair at a time (C-31 U-V, C-32 V-W, C-33 U-W), phase-to-DC-rail merged into C-34; (12) temperature sensing updated to 2 IGBT NTC (1oo2) + 1 DC link capacitor NTC with capacitor derate 90 °C / SSO 105 °C; (13) coprocessor firmware explicitly trusted (no generated code). Plan now 92 line items (80 defined tests + 12 deferred E-series stubs). |
| 5.8 | 2026-08-13 | Fault-injection test plan extracted to OV-TEST-FAULT-INJECTION (standalone document under Testing/); Section 10 replaced by a reference to the standalone plan. |
