---
doctype: Assembly Guide
doc_id: OV-CA-AG-04-TF
title: Control Module Test Fit
product_line: openvvvf
applies_to:
  - openvvvf-control-module
version: "0.2"
date: "2026-08-21"
description: Test-fit the populated control module boards together and verify the headers seat cleanly.
nav_order: 135
normative_refs:
  - OV-CA-INDEX
  - OV-CA-AG-01-IO
  - OV-CA-AG-02-GD
  - OV-CA-AG-03-CB
---

# Control Module Test Fit

After populating the IO board, gate driver board, and control board, do a test fit of the three-board stack. This catches crooked headers, reversed connectors, and mechanical interference before the module is fully committed.

> **Important:** This is a mechanical fit check only. Do not apply power.

> **Safety**
> - Work in an ESD-safe area and use a grounded wrist strap or ESD mat while handling populated boards.
> - Keep the boards on a soft, clean surface to avoid scratching components or shorting against metal tools.

## Required materials

| Item | Qty | Notes |
|------|-----|-------|
| Populated IO board | 1 | `OV-CA-AG-01-IO` |
| Populated gate driver board | 1 | `OV-CA-AG-02-GD` |
| Populated control board | 1 | `OV-CA-AG-03-CB` |

## Step 1 - Lay out the three boards

Start with the populated IO board, gate driver board, and control board on the bench. Check each one for any obviously loose parts, solder bridges, or connectors that did not get fully seated during population.

![IO board, control board, and gate driver board laid out for test fitting](Preparation.jpg)

## Step 2 - Seat the control board onto the gate driver board

Pick up the control board and align its headers with the matching sockets on the gate driver board. Lower the control board straight down; the headers should slide in without forcing.

![Lowering the control board onto the gate driver board](Hand-Lowering-Control-Board-To-Gate-Driver.jpg)

Make sure the long header rows are straight and fully engaged before pressing the boards together.

![Aligned header pins ready to seat](Alligned-And-Inserted-Ctrlbd-To-Gate-Driver.jpg)

Press the connector fully home with your thumb. The boards should sit parallel with no gaps at the connector.

![Pressing the control-board connector fully into the gate driver](Thumb-Pushing-Control-Connector-To-Gate-Driver.jpg)

## Step 3 - Seat the IO board onto the control board

Take the IO board and align its headers with the sockets on the control board. Again, lower it straight down and verify the headers are not crooked before applying pressure.

![Aligning the IO board with the control board](Aligning-IO-Board-To-Controlbd.jpg)

Press the IO-board connector into the control board until it is fully seated.

![Seating the IO-board connector into the control board](Hand-Seating-Connector-To-Control-From-IO.jpg)

## Step 4 - Check the assembly

With all three boards connected, look at the stack from the sides and ends:

- The boards should be parallel and evenly spaced.
- No header should look tilted or only partially inserted.
- All mating connectors should be fully seated with no visible gap.

If anything looks off, pull the boards apart and recheck header orientation and straightness before trying again.

![Fully inserted three-board assembly](Fully-Inserted-Assembly.jpg)

![Top view of the assembled control module stack](Final-Top.jpg)

![Back view of the assembled control module stack](Final-Back.jpg)

## Step 5 - Disassemble

Once you have confirmed everything seats cleanly, separate the boards and set them aside in ESD-safe containers or on a mat. Keep them ready for the final control-module assembly step.

## Next steps

With the control module boards verified to fit together, proceed to the remaining control-module assembly steps described in the control assembly index (`OV-CA-INDEX`).
