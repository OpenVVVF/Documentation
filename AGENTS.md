# Agent & Contributor Conventions

## Repository purpose

This is the OpenVVVF documentation and hardware-data hub. It does **not** contain KiCad/CAD hardware designs (those live in `../InverterGen5`) or firmware source (OpenVVVF/RTE). It does contain all user-facing, safety, compliance, and software documentation, plus shared tooling and data.

## Document conventions

1. **Frontmatter is required** on every Markdown file under `Docs/`. See the schema in the project README or `Tools/DocGen`.
2. **Unique `doc_id`**: every document must have a stable, kebab-case `doc_id`.
3. **One document = one folder**: every document under `Docs/` lives in its own folder and is named `Index.md`. See `Docs/Agents.md` for the full structure.
4. **Folder naming**: use kebab-case. Ordered assembly chapters/steps are prefixed with `<N>_` (e.g. `3_Main-Assembly`, `1_IGBT-Mounting`). The generator displays dashes as spaces.
5. **Core + Profile pattern**: safety analyses (HARA, TARA, FMEA) are split into a platform Core document and Application Profile documents.
6. **Cross-references**: reference documents by `doc_id`, not by path. Use `docgen` to validate them.
7. **No use-case product manuals**: documentation is organized by hardware (control assembly, power stage) and supporting domains (safety, software, testing). Users receive the documents that apply to the hardware they have.

## Tool conventions

1. **BOMManager** (`Tools/BOMManager`) is the generalized Bill-of-Materials and fabrication package manager. It reads product definitions from `Config/Products.yaml`.
2. **docgen** (`Tools/DocGen`) validates frontmatter, resolves `doc_id` references, and assembles product manuals.
3. **HWRelease** (`Tools/HWRelease`) exports per-board release artifacts (schematic PDF, BOM, gerbers, DRC, STEP, iBOM HTML) from `../InverterGen5` release tags into `Data/Releases/`, indexed by part number in `Data/Releases/manifest.json`.
4. Run `pytest` before committing changes to tools.

## Data conventions

1. `Data/Parts/*.json` are committed project data.
2. `Data/Parts/Inventory.json` and `Data/Parts/PriceCache.json` are **gitignored**; they represent personal/local state.
3. Part numbers use the format `HW-{product}-{category}-{descriptor}-{rev}` by default.
4. `Data/Releases/` is committed generated data (written by HWRelease); do not hand-edit — regenerate with `hwrelease update --force`.

## Prohibited changes

1. Do not move hardware designs from `../InverterGen5` into this repo without explicit user approval.
2. Do not commit API keys, vendor credentials, or personal inventory files.
3. Do not hand-edit `Data/Parts/Numbers.json` or `Data/Parts/Descriptors.json`; use BOMManager commands or edit with care.
