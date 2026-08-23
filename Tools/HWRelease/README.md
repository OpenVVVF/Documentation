# HWRelease - hardware release exporter

Turns release tags in the hardware repository (`../InverterGen5`) into
versioned, per-board artifacts under `Data/Releases/`, indexed by part number
(`HW-C2-PCB-CTRL-A`, `HW-C2-PCB-CTRL-B`, …) in `Data/Releases/manifest.json`.

## Workflow

1. In `../InverterGen5`: bump the revision in the board's KiCad files
   (`(rev "B")` in the `.kicad_sch` / `.kicad_pcb`), commit, push, and create a
   GitHub release (which creates the tag). For mechanical-only changes, instead
   rename the FreeCAD part labels and `Mechanical/Fab/<part>` folders to the
   new rev suffix and tag `<chassis-short>-<rev>` (e.g. `C2-B`): a
   chassis-named tag pins the chassis release rev and scopes the export to
   that chassis, no board rev bump needed.
2. Here, run:

   ```sh
   make hw-update        # or: python3 Tools/HWRelease/hwrelease.py update
   ```

   The tool fetches tags, exports each tag's `Hardware/` tree to a temp dir
   (the hardware repo's working tree is never touched), reads each board's
   revision from its KiCad files, and regenerates, via `kicad-cli` (KiCad
   flatpak), the schematic PDF, BOM CSV, gerber+drill zip, DRC report, STEP
   model, and the interactive assembly HTML (iBOM). Only board revisions not
   yet in the manifest are generated; existing ones are kept as-is.

3. Commit the new `Data/Releases/` content. The revision is now part of the
   documentation repo.

## Commands

- `hwrelease update [--tag T] [--tag-pattern GLOB] [--force] [--hw-repo PATH]`
  - export missing board revisions. Defaults: all tags, repo from
  `Config/Products.yaml` (`hardware_roots`).
- `hwrelease list` - all exported boards grouped by revision.
- `hwrelease show HW-C2-PCB-CTRL-A` - artifact paths for one part number.
- `hwrelease build-viewer` - regenerate `Docs/Tools/PCB-Tool/pcb-tool.html` and
  `Docs/Tools/BOM-Tool/bom-tool.html` from the manifest (runs automatically
  after `update` when new revisions were exported). docgen copies
  `Data/Releases/` into the built site.

## Vendor BOMs and pricing

`update` regenerates the chassis-level vendor BOMs (Mouser, McMaster-Carr,
SendCutSend, DigiKey, assembly, PCB) with this repo's BOMManager `generate`
against the exported tag. Board and harness BOM CSVs are first exported from
the KiCad schematics so nothing is missed. Prices come from the local price
cache / vendor APIs per your BOMManager config; variant totals (base /
standard / generous) are recorded in the manifest. If BOMManager or its deps
are unavailable, the committed BOMs from the tag are copied instead (with a
warning).

## Board ordering specs (fab_spec.yaml)

If a board directory in the hardware repo contains `fab_spec.yaml` (next to
the `.kicad_pro`), it is recorded in the manifest and shown in the tools:

```yaml
options:            # settings to pick in the JLCPCB quote form
  outer_copper: 2 oz
notes:              # free-text per-board instructions
  - "2 oz outer copper required (high-current DC bus)."
```

`Boards/fab_defaults.yaml` (same schema) holds chassis-wide notes merged into
every board (e.g. serial-number barcode instructions). The PCB Tool renders
options + notes as an "Ordering specifications" section; the BOM Tool's PCBs
table shows the per-board notes in a Notes column.

## Requirements

- KiCad via flatpak (`org.kicad.KiCad`) or `kicad-cli` on PATH.
- FreeCAD via flatpak (`org.freecad.FreeCAD`), used for mechanical-part
  extraction (optional; skipped with a warning if absent).
- `InteractiveHtmlBom` in `../InverterGen5/Hardware/BOMManager/.venv` or this
  repo's `.venv` (only needed for the interactive assembly HTML; skipped with a
  warning otherwise).

## FreeCAD extraction

On `update`, each chassis's `Mechanical/*.FCStd` is opened headlessly
(`freecadcmd` flatpak). Every `PartDesign::Body` / `App::DocumentObjectGroup`
whose **label ends with the exact part number** (`HW-...`) is exported:

- `<pn>.step`: fresh STEP, overwriting the manually exported one,
- `holes.json`: cylindrical-hole diameter histogram (mm),
- `material.json`: the part's material from the model (`ShapeMaterial` card
  name, e.g. `Aluminum-6061-T6`), when assigned; omitted when the body/group
  has no material ("Default").

The extracted material is recorded in the mech manifest entry and shown in the
BOM Tool part cards (priority: `fab_spec.yaml` material, then the extracted
material, then `info.txt` Material).

Tap/countersink diameters in `fab_spec.yaml` are validated against the model's
holes and mismatches are printed as warnings. Keep model labels exact,
e.g. `HW-C2-BSP-A`, `PhaseBusBars-HW-C2-PBB-A`.

A chassis with no boards (mechanical concept only, e.g. Chassis3) is exported
too: as long as it has a `Mechanical/*.FCStd` or a `Mechanical/Fab/` dir it
gets a `CHASSIS-<short>-<rev>` entry (rev falls back to the tag name) with its
mech parts. A chassis with no vendor BOMs and no mech parts is skipped.

## Conventions

- Board → part number mapping comes from `Config/Products.yaml` (chassis short
  codes) and `Data/Parts/Descriptors.json` (`<Chassis>|pcb|<board> → PREFIX`).
  A board missing either mapping is skipped with a warning.
- Tag naming is up to the hardware repo (e.g. `hw-rev-a`); use `--tag-pattern`
  to restrict discovery.
- `Data/Releases/` is committed generated data: do not hand-edit; regenerate
  with `--force` instead.

## Tests

```sh
make test-hwrelease
```

## Roadmap / planned

- **Ordering screenshots per board and per part**: the user will capture
  screenshots of the JLCPCB / SendCutSend ordering flows. Convention (TBD):
  images alongside `FabSpec.md` per board (PCB Tool) and per mechanical part
  (BOM Tool / part explorer), exported into `Data/Releases/` and shown in the
  tools so ordering settings are unambiguous.
- **Mechanical parts explorer**: auto-discover mechanical parts (SendCutSend
  sheet parts, McMaster hardware) from the hardware repo at export time and
  give them their own tool page, like the PCB Tool: renders/screenshots,
  specs, vendor links, prices.
