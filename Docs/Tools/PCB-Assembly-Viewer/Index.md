---
doctype: Tool Manual
doc_id: OV-TOOLS-PCB-ASSEMBLY-VIEWER
title: PCB Assembly Viewer
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-08-16"
description: Browse released PCBs by part number — renders, interactive assembly, schematics, and fabrication files.
nav_order: 602
normative_refs:
  - OV-TOOLS-INDEX
---

# PCB Assembly Viewer

The PCB Assembly Viewer lists every released board revision by part number (e.g. `HW-C2-PCB-CTRL-A`). Selecting a board shows its renders and gives access to the interactive assembly tool, schematic, BOM, and fabrication files — all generated from the hardware repository's release tags.

## Using the viewer

1. Open the [PCB Assembly Viewer](pcb-viewer.html).
2. Pick a part number from the list (use the filter box to search by part number or board name).
3. View the board renders, then click **Open Interactive Assembly** to launch the interactive HTML assembly tool in a new tab.

Direct links work too: append `#<part-number>` to the viewer URL, e.g. `pcb-viewer.html#HW-C2-PCB-CTRL-A`.

## Available artifacts per board

- **Interactive assembly (iBOM)** — click components to locate them on the board; opens in a new tab.
- **Schematic PDF** — full board schematic as released.
- **BOM (CSV)** — bill of materials exported from the schematic.
- **Gerbers (ZIP)** — fabrication package (gerbers + drill files).
- **DRC report** — design-rule check result at release time.
- **STEP model** — 3D board model.

## Where the data comes from

Artifacts are exported from `InverterGen5` release tags by the HWRelease tool (`make hw-update`) and stored in `Data/Releases/`, indexed by part number in `Data/Releases/manifest.json`. The viewer page itself is regenerated from that manifest with `hwrelease build-viewer` (runs automatically after `update`).
