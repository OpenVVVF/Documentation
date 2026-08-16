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
- `hwrelease build-viewer` — regenerate `Docs/Tools/PCB-Tool/pcb-tool.html` and
  `Docs/Tools/BOM-Tool/bom-tool.html` from the manifest (runs automatically
  after `update` when new revisions were exported). docgen copies
  `Data/Releases/` into the built site.

## Vendor BOMs and pricing

`update` regenerates the chassis-level vendor BOMs (Mouser, McMaster-Carr,
SendCutSend, DigiKey, assembly, PCB) with this repo's BOMManager `generate`
against the exported tag — board and harness BOM CSVs are first exported from
the KiCad schematics so nothing is missed. Prices come from the local price
cache / vendor APIs per your BOMManager config; variant totals (base /
standard / generous) are recorded in the manifest. If BOMManager or its deps
are unavailable, the committed BOMs from the tag are copied instead (with a
warning).

## Board ordering specs (FabSpec.md)

If a board directory in the hardware repo contains `FabSpec.md` (next to the
`.kicad_pro`), it is copied into the release and rendered on the board's PCB
Tool page as "Ordering specifications" — copper weight, surface finish, tapped
holes, panelization, and other fab instructions.

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

## Roadmap / planned

- **Ordering screenshots per board and per part** — the user will capture
  screenshots of the JLCPCB / SendCutSend ordering flows. Convention (TBD):
  images alongside `FabSpec.md` per board (PCB Tool) and per mechanical part
  (BOM Tool / part explorer), exported into `Data/Releases/` and shown in the
  tools so ordering settings are unambiguous.
- **Mechanical parts explorer** — auto-discover mechanical parts (SendCutSend
  sheet parts, McMaster hardware) from the hardware repo at export time and
  give them their own tool page, like the PCB Tool: renders/screenshots,
  specs, vendor links, prices.
