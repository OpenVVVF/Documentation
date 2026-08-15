---
doctype: Assembly Guide
doc_id: OV-C2-AG-01
title: 1 Preparation
product_line: openvvvf
applies_to:
  - chassis-size-2
version: "0.2"
date: "2026-08-15"
placeholder: true
description: Prerequisites, tools, and materials to prepare before assembling the Chassis Size 2 power stage.
nav_order: 223
---

# 1 Preparation

Everything to have done, have on hand, and have checked before starting the C2 power-stage build.

> **NOTE**
> This chapter is a skeleton. The structure is complete; fill in the specific part numbers, torque values, and quantities as the build is finalized.

## Prerequisites

These items must be complete before power-stage assembly begins:

- **Control assembly completed and tested** - the control module must be fully assembled and verified before it is needed for the later chassis-board and final-assembly chapters. See the Control Assembly assembly guide (`OV-CA-AG-INDEX`).
- **Firmware flashed** - main MCU and safety coprocessor firmware flashed and confirmed booting. See the Control Assembly software manual (`OV-CA-SWM-INDEX`).
- **Prior build chapters complete** - each chapter in this guide assumes the chapters before it are done; do not skip ahead, as later steps rely on hardware installed earlier.

## Required documents

- This assembly guide (`OV-C2-AG-INDEX`), printed or on a shop tablet.
- C2 bill of materials - generate the current fabrication/BOM package with BOMManager and verify all parts are on hand before starting.
- Relevant design documents (`OV-C2-DD-INDEX`) for background on torque and thermal decisions.

## Tools

<!-- TODO: confirm sizes and add part numbers where specific tools matter -->

- Torque wrench covering the M5/M6 range (8 N·m capability required)
- Hex key / driver set
- ESD-safe tweezers and small hand tools
- Multimeter
- Permanent marker (for torque-strip witness marks)
- Soldering station and solder (PCB chapters only)
- Clean, lint-free gloves - mandatory when handling bus bars or high-current contact surfaces

## Consumables

<!-- TODO: confirm products and quantities -->

- Thermal interface compound
- Thread-locking compound, medium strength
- Isopropyl alcohol and lint-free wipes
- ESD bags for populated PCBs

## Workspace and ESD

- Clean, well-lit bench with enough room to lay out the heatspreader and all sub-assemblies.
- ESD mat and wrist strap for all PCB population chapters and for handling the control module.
- Keep the work area free of stray metal debris at all times; metal swarf or loose hardware can short high-voltage bus bars.

## Safety

> **SAFETY**
> - Do not power the inverter until all assembly, torque, and inspection steps are complete.
> - Review the hazard analysis (`OV-SAF-HARA-CORE`) before starting; it identifies the hazards each assembly control mitigates.
> - Wear clean gloves whenever handling bus bars, screws, or any high-current contact surface - skin oils increase contact resistance at joints.
