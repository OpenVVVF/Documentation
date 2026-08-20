---
doctype: Design Document
doc_id: OV-TOOLS-HWRELEASE
title: HWRelease System Architecture
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
version: "0.1"
date: "2026-08-16"
description: How hardware releases flow from InverterGen5 git tags into the PCB Tool, BOM Tool, and Data/Releases, and the conventions that drive them.
nav_order: 604
normative_refs:
  - OV-TOOLS-INDEX
---

# HWRelease System Architecture

This document describes how hardware release data flows from the hardware repository into the documentation site, and the conventions that make it work. Read this before changing `Tools/HWRelease`, the release data, or the hardware-side spec files.

## Repositories and data flow

```text
InverterGen5 (hardware repo)                Documentation (this repo)
---------------------------                 -------------------------
KiCad projects ──┐
Mechanical/Fab ──┤  git tag (release)       Tools/HWRelease
fab_spec.yaml ───┼──────────────►  hwrelease update
fab_defaults.yaml┘                     │
                                       ├─ kicad-cli exports (per board):
                                       │    schematic PDF, BOM CSV, gerber zip,
                                       │    DRC, STEP, iBOM HTML, renders
                                       ├─ BOMManager generate (per chassis):
                                       │    vendor BOMs, variants, pricing
                                       ├─ mech-part export (Mechanical/Fab)
                                       ├─ per-subassembly export
                                       │    (Mechanical/Assembly/<name>.step|.stl)
                                       ▼
                                 Data/Releases/<chassis>/<rev>/...
                                 Data/Releases/manifest.json
                                       │
                          hwrelease build-viewer (automatic)
                                       ▼
              Docs/Tools/PCB-Tool/pcb-tool.html  (per-board pages)
              Docs/Tools/BOM-Tool/bom-tool.html  (per-chassis ordering)
                                       │
                          docgen site (copies Data/Releases into site/)
```

## The release workflow

1. In InverterGen5: make changes (bump `(rev "X")` in a board's `.kicad_sch`/`.kicad_pcb`, edit specs), commit, push, and create a GitHub release (which creates a tag, e.g. `C2-A`).
2. Here: run `make hw-update` (= `hwrelease update`). It fetches tags, and for each tag not yet in the manifest:
   - Exports the tag's `Hardware/` tree via `git archive` into a temp dir (the hardware repo's working tree is never touched).
   - Reads each board's revision from `(rev "X")` in its KiCad files.
   - Exports board BOM CSVs (`<Board>.csv` beside each project, boards *and* wiring harnesses): BOMManager discovers BOMs from these files, so this step must happen before generation.
   - Regenerates the chassis vendor BOMs with this repo's BOMManager (`generate --variants`), so BOMs and prices are always built from the tag's sources, never copied stale.
   - Extracts fabricated parts from the FreeCAD model (`Mechanical/*.FCStd`): per part (Body/Group labeled with the exact part number; `...001` instance suffixes deduplicated) a fresh STEP, STL, Blender renders, and a `holes.json` diameter histogram, followed by a spec-vs-model hole check. It also harvests McMaster hardware (labels like `91292A134_...Screw001` are counted per part number, **merged into `MechanicalBOM.txt`** (model count wins for modeled parts; unmodeled lines like consumables are kept; model-only parts are appended), then cross-checked with warnings) and counts instances per fabricated part (`model_parts.json`), cross-checked against each part's `info.txt` quantity. The same pass exports the model per subassembly: each top-level group/body becomes `Mechanical/Assembly/<label>.stl` + `<label>.step` (loose hardware instances are grouped into a shared `Hardware` subassembly), copied into the chassis release dir as `Assembly/`; on a STEP-export timeout, completed subassemblies are kept. A chassis with no boards (mechanical concept only, e.g. Chassis3) is exported too whenever it has a `Mechanical/*.FCStd` or `Mechanical/Fab/`; its `CHASSIS-<short>-<rev>` entry falls back to the tag name as rev.
   - Exports per-board artifacts (named `<part-number>-<kind>.<ext>`) and mechanical parts.
   - Updates `Data/Releases/manifest.json` and regenerates both tool pages.
3. Commit `Data/Releases/` and the generated pages.

Already-exported revisions are skipped; `hwrelease update --tag <T> --force` regenerates (e.g. after moving a tag).

## Manifest (`Data/Releases/manifest.json`)

Single source of truth for the tools. Three entry kinds:

- **Boards**: key `HW-<chassis>-PCB-<desc>-<rev>` (e.g. `HW-C2-PCB-CTRL-A`): artifacts map (`ibom`, `schematic_pdf`, `bom_csv`, `gerber_zip`, `drc`, `step`, `renders`, `fab_spec`), plus `source_tag`/`source_url`.
- **Chassis releases**: key `CHASSIS-<chassis>-<rev>`: `vendor_boms` (CSV paths per vendor), `variants` (spares tiers), `price_estimate` (vendor subtotals, grand total, per-variant totals and per-variant vendor subtotals), `pricing_report`, and `assembly` (per-subassembly export from the chassis FCStd: `stl`/`step` path lists under `Assembly/`; a subassembly may lack its STEP after a timeout. The BOM Tool links a combined 3D assembly view from the STLs and one STEP download per subassembly). Entries exist whenever the chassis has vendor BOMs, mech parts, or an assembly model, so mechanical-only chassis (no boards) appear too.
- **Mechanical parts**: key = part number (e.g. `HW-C2-DCLBB-A`), with `mech: true`: `step`, `image`, `info`/`info_fields` (from SendCutSend cart imports), `fab_spec`.

## Conventions (hardware repo)

These files in InverterGen5 drive the tools; keep them current:

- `Boards/fab_defaults.yaml`: chassis-wide ordering notes merged into every board (e.g. serial-number barcode rule).
- `Boards/<Board>/fab_spec.yaml`: per-board fab options and notes:
  ```yaml
  options:            # JLCPCB quote-form settings
    outer_copper: 2 oz
  notes:
    - "2 oz outer copper required (high-current DC bus)."
  ```
- `Mechanical/Fab/<part>/fab_spec.yaml`: per-part ordering spec:
  ```yaml
  process: laser_cut        # or 3d_print
  material: "Copper C110"
  thickness_mm: 4.75
  services:
    bending: true
    tapping:
      - thread: "M6x1.0"
        holes: "all ⌀5.0 mm through-holes (4x)"   # reference holes by drill diameter
    countersink:
      - for: "M5 flathead"
        holes: "⌀5.5 mm holes on top face (2x)"
  notes:
    - "Deburr both sides"
  ```
  For `3d_print`, use `material`/print notes instead (layer height, infill, orientation). Holes are referenced by drill diameter so a future FreeCAD extractor can verify specs against the model.
- `Mechanical/Fab/<part>/info.txt`: auto-imported SendCutSend cart record (price, dims); do not hand-edit.

## Conventions (this repo)

- Ordering walkthroughs live next to `Docs/Tools/BOM-Tool/Index.md` as `ordering-<vendor>-<n>.png` + optional `ordering-<vendor>-<n>.txt` caption (vendors: `mouser`, `digikey`, `mcmaster`, `sendcutsend`, `jlc`). Steps stop at the first missing `n`. The PCBs vendor uses the `jlc` files.
- `Data/Releases/` is committed generated data: never hand-edit; regenerate with `--force`.
- Tool pages are generated (`hwrelease build-viewer`); edit `Tools/HWRelease/hwrelease/viewer.py`, not the HTML.

## The tools

- **PCB Tool** (`/Tools/PCB-Tool/pcb-tool.html`): every released board by part number; renders, embedded interactive assembly (iBOM), part-number-named artifacts, "Open Source" link to the tag, and the board's `fab_spec` as an Ordering specifications table.
- **BOM Tool** (`/Tools/BOM-Tool/bom-tool.html`): chassis / revision / spares-variant selectors, vendor list with price subtotals and a total estimate, CSV preview, per-vendor order links, ordering walkthroughs, gerber downloads + per-board notes on the PCBs view, and per-part spec cards on the SendCutSend view.

## Planned (roadmap)

- **FreeCAD auto-extraction (implemented, first slice)**: on every `hwrelease update`, a headless `freecadcmd` pass opens the chassis `Mechanical/*.FCStd`, finds every Body/Group whose **label ends with the exact part number** (`HW-...`), and exports `<pn>.step`, `<pn>.stl`, and `holes.json` (cylindrical-hole diameter histogram) into `Mechanical/Fab/<pn>/`. A headless **Blender** pass then renders `info.png` + `info-back.png` per part from the STLs (no GUI, two isometric angles). Tap/countersink diameters in each part's `fab_spec.yaml` are checked against the model's actual holes, with warnings on mismatch. Instance counts are harvested for both McMaster hardware and fabricated parts and cross-checked against `MechanicalBOM.txt` / `info.txt` quantities. Mech entries that vanish from the tree are pruned from the manifest. Next: fill `fab_spec.yaml` fields from model properties.
- **Build configurations**: voltage-class builds (200V / 250V / 300V / 450V) that swap both electrical parts (Mouser lines) and mechanical parts (heatspreader, printed holders): a Build dropdown beside Variant, driven by part-number mappings in `Config/Products.yaml`.
- **Mechanical parts explorer**: a dedicated tool page for mech parts (the manifest entries and spec cards are the seed).

## Maintenance cheatsheet

| Task | Where |
|---|---|
| New board revision | bump `(rev ...)` in KiCad files, tag release, `make hw-update` |
| Board ordering spec (2 oz copper, finish) | `Boards/<Board>/fab_spec.yaml` in InverterGen5 |
| Chassis-wide fab note | `Boards/fab_defaults.yaml` |
| Mech part spec (tap/countersink/bend/print) | `Mechanical/Fab/<part>/fab_spec.yaml` |
| Vendor ordering walkthrough | `Docs/Tools/BOM-Tool/ordering-<vendor>-<n>.{png,txt}` |
| Part prices | BOMManager (`Data/Parts/PriceCache.json` / vendor APIs): regenerate via `hwrelease update` |
