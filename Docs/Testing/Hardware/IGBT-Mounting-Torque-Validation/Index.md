---
doctype: Test Report
doc_id: OV-TEST-HW-IGBT-TORQUE
title: IGBT Mounting Torque Validation
product_line: openvvvf
applies_to:
  - chassis-size-2
version: "1.0"
date: "2026-08-07"
status: released
description: Validation of the C2 IGBT module mounting procedure, torque spec, and retorque behavior.
nav_order: 511
normative_refs:
  - OV-TEST-HW-INDEX
  - OV-C2-AG-03-01
  - OV-SAF-HARA-CORE
---

# IGBT Mounting Torque Validation

## Objective

Verify that the C2 IGBT mounting procedure (doc `OV-C2-AG-03-01`) produces a thermally and mechanically reliable module-to-heatsink interface:

- Torque wrench calibration and technique produce repeatable 4 N·m clamp load.
- Retorque after thermal cycling does not loosen the joint.
- Thermal interface compound coverage is uniform and bubble-free.

## Setup

| Item | Details |
|------|---------|
| Hardware under test | Chassis Size 2 heatspreader, 3× Mitsubishi CM600DY-24T modules, M6×12 socket-head cap screws, Belleville washers |
| Thermal interface | Generic silicone-based TIM, λ ≈ 3 W/(m·K) |
| Torque wrench | CDI 1/4" drive, 0.5–6 N·m, calibrated within 12 months |
| Test environment | Clean bench, grounded ESD mat, 23 °C ambient |
| Operator | Technician following `OV-C2-AG-03-01` |

## Procedure

1. Clean heatspreader mounting pads and module baseplates with isopropyl alcohol.
2. Apply a thin, uniform film of TIM to the module baseplate using a plastic spreader.
3. Install modules on heatspreader with Belleville washers under each screw head.
4. Torque screws in a star pattern to 4 N·m using the calibrated torque wrench.
5. Mark each screw head and module edge with torque-seal paint.
6. Power the heatspreader with resistive heaters to simulate 30 min at rated module temperature (target baseplate ≈ 85 °C).
7. Allow assembly to cool to ambient.
8. Re-torque each screw and record any rotation required to reach 4 N·m.
9. Remove one module and inspect TIM spread pattern.

## Results

| Module | Initial torque (N·m) | Retorque rotation | Retorque final (N·m) | Visual TIM coverage |
|--------|----------------------|-------------------|----------------------|---------------------|
| U | 4.0 | < 5° | 4.0 | > 95 %, no voids > 5 mm |
| V | 4.0 | < 5° | 4.0 | > 95 %, no voids > 5 mm |
| W | 4.0 | < 5° | 4.0 | > 95 %, no voids > 5 mm |

All screws retained torque within the wrench resolution; no screw required more than 5° of rotation to return to 4 N·m after thermal cycling.

## Conclusion

**Pass.** The documented C2 IGBT mounting procedure (4 N·m torque, star pattern, Belleville washers, thin uniform TIM) produces a stable thermal and mechanical joint through at least one thermal cycle. No procedure changes are required.

## Traceability

- `OV-C2-AG-03-01` § Torque procedure - verified.
- HARA Core FSR related to over-temperature due to degraded thermal path - supporting evidence.
