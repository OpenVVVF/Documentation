---
doctype: Tool Manual
doc_id: OV-TOOLS-BOM-TOOL
title: BOM Tool
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-08-16"
description: Vendor order BOMs (Mouser, McMaster-Carr, SendCutSend, DigiKey) per chassis, revision, and build variant.
nav_order: 603
normative_refs:
  - OV-TOOLS-INDEX
---

# BOM Tool

The BOM Tool serves the per-chassis vendor order BOMs exported from the hardware repository's release tags. Select a chassis, revision, and build variant, then preview or download the vendor BOM you need.

## Using the tool

1. Open the [BOM Tool](bom-tool.html).
2. Choose the **chassis**, **revision**, and **variant** (`base` is the standard build; named variants such as `generous` come from the hardware repo's BOM variants).
3. Click a vendor — **Mouser**, **McMaster-Carr**, **SendCutSend**, **DigiKey**, plus the consolidated, assembly, and PCB BOMs — to preview the CSV inline.
4. Use **Download CSV** to save it for ordering (e.g. pasting into the vendor's BOM import).

## Where the data comes from

The CSVs are copied from `Hardware/<Chassis>/FabricationData/BOMs/` at each `InverterGen5` release tag by the HWRelease tool (`make hw-update`) into `Data/Releases/<chassis>/<rev>/BOMs/`, and indexed in `Data/Releases/manifest.json` under `CHASSIS-<chassis>-<rev>` entries. The page itself is regenerated with `hwrelease build-viewer` (runs automatically after `update`).
