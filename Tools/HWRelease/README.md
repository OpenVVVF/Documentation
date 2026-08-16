# HWRelease — hardware release exporter

Turns release tags in the hardware repository (`../InverterGen5`) into
versioned, per-board artifacts under `Data/Releases/`, indexed by part number
(`HW-C2-PCB-CTRL-A`, `HW-C2-PCB-CTRL-B`, …) in `Data/Releases/manifest.json`.

## Workflow

1. In `../InverterGen5`: bump the revision in the board's KiCad files
   (`(rev "B")` in the `.kicad_sch` / `.kicad_pcb`), commit, push, and create a
   GitHub release (which creates the tag).
2. Here, run:

   ```sh
   make hw-update        # or: python3 Tools/HWRelease/hwrelease.py update
   ```

   The tool fetches tags, exports each tag's `Hardware/` tree to a temp dir
   (the hardware repo's working tree is never touched), reads each board's
   revision from its KiCad files, and regenerates — via `kicad-cli` (KiCad
   flatpak) — the schematic PDF, BOM CSV, gerber+drill zip, DRC report, STEP
   model, and the interactive assembly HTML (iBOM). Only board revisions not
   yet in the manifest are generated; existing ones are kept as-is.

3. Commit the new `Data/Releases/` content. The revision is now part of the
   documentation repo.

## Commands

- `hwrelease update [--tag T] [--tag-pattern GLOB] [--force] [--hw-repo PATH]`
  — export missing board revisions. Defaults: all tags, repo from
  `Config/Products.yaml` (`hardware_roots`).
- `hwrelease list` — all exported boards grouped by revision.
- `hwrelease show HW-C2-PCB-CTRL-A` — artifact paths for one part number.
- `hwrelease build-viewer` — regenerate `Docs/Tools/PCB-Tool/pcb-tool.html`
  from the manifest (runs automatically after `update` when new revisions were
  exported). The PCB Tool page lists all boards by part number with renders,
  an embedded interactive assembly view (fullscreen / open in new tab), links
  to the part-number-named artifacts (`<pn>-schematic.pdf`, `<pn>-bom.csv`,
  `<pn>-gerbers.zip`, `<pn>-drc.txt`, `<pn>.step`), and an "Open Source" link
  to the hardware repo at the release tag. docgen copies `Data/Releases/`
  into the built site.

## Requirements

- KiCad via flatpak (`org.kicad.KiCad`) or `kicad-cli` on PATH.
- `InteractiveHtmlBom` in `../InverterGen5/Hardware/BOMManager/.venv` or this
  repo's `.venv` (only needed for the interactive assembly HTML; skipped with a
  warning otherwise).

## Conventions

- Board → part number mapping comes from `Config/Products.yaml` (chassis short
  codes) and `Data/Parts/Descriptors.json` (`<Chassis>|pcb|<board> → PREFIX`).
  A board missing either mapping is skipped with a warning.
- Tag naming is up to the hardware repo (e.g. `hw-rev-a`); use `--tag-pattern`
  to restrict discovery.
- `Data/Releases/` is committed generated data — do not hand-edit; regenerate
  with `--force` instead.

## Tests

```sh
make test-hwrelease
```
