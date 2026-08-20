---
doctype: Tool Manual
doc_id: OV-TOOLS-BOM-TOOL
title: BOM Tool
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.2"
date: "2026-08-17"
description: Vendor order BOMs (Mouser, McMaster-Carr, SendCutSend, DigiKey) per chassis, revision, and build variant.
nav_order: 603
normative_refs:
  - OV-TOOLS-INDEX
---

# BOM Tool

The BOM Tool serves the per-chassis vendor order BOMs exported from the hardware repository's release tags. Select a chassis, revision, and build variant, then preview or download the vendor BOM you need.

![BOM Tool showing the Mouser order BOM with the ordering walkthrough](bom-tool-mouser-view.jpg)

![BOM Tool showing fabricated parts with 3D previews and SendCutSend ordering](bom-tool-sendcutsend-view.jpg)

## Using the tool

1. Open the [BOM Tool](bom-tool.html).
2. Choose the **chassis**, **revision**, and **variant** (`base` is the standard build; named variants such as `generous` come from the hardware repo's BOM variants).
3. Click a vendor (**Mouser**, **McMaster-Carr**, **SendCutSend**, **DigiKey**, plus the consolidated, assembly (in-house harnesses), and PCB BOMs) to preview the CSV inline. Vendor buttons show their share of the cost estimate.
4. Use **Download CSV** to save it for ordering (e.g. pasting into the vendor's BOM import). For boards, **View boards in PCB Tool** takes you to the per-board gerbers/specs, and **Order PCBs at JLCPCB** opens the fab.

### Ordering walkthrough screenshots

When a vendor is selected, the tool shows a step-by-step walkthrough of that vendor's upload/ordering flow below the buttons (for McMaster-Carr there's also a button that copies the order paste to the clipboard). The walkthrough is hand-maintained: drop files next to this document named `ordering-<vendor>-<n>.png` (screenshot) and `ordering-<vendor>-<n>.txt` (one-line caption), numbered in order (`n` = 1, 2, …; vendors: `mouser`, `digikey`, `mcmaster`, `sendcutsend`, `jlcpcb`). Either file may exist alone: steps without a screenshot show as text only. No regeneration is needed; they are picked up on the next site build.

The estimate in the header reflects the selected variant (`base`, `standard`, `generous`).

## Where the data comes from

The CSVs are regenerated from the tag's KiCad sources on every export: HWRelease (`make hw-update`) runs BOMManager's `generate` (with pricing) against the exported tag tree, so they can never go stale. They live in `Data/Releases/<chassis>/<rev>/BOMs/` and are indexed in `Data/Releases/manifest.json` under `CHASSIS-<chassis>-<rev>` entries. The page itself is regenerated with `hwrelease build-viewer` (runs automatically after `update`).
