# Agent & Contributor Conventions

## Repository purpose

This is the OpenVVVF documentation and hardware-data hub. It does **not** contain KiCad/CAD hardware designs (those live in `../InverterGen5`) or firmware source (OpenVVVF/RTE). It does contain all user-facing, safety, compliance, and software documentation, plus shared tooling and data.

## Document conventions

1. **Frontmatter is required** on every Markdown file under `Docs/`. See the schema in the project README or `Tools/DocGen`.
2. **Unique `doc_id`**: every document must have a stable, kebab-case `doc_id`.
3. **Core + Profile pattern**: safety analyses (HARA, TARA, FMEA) are split into a platform Core document and Application Profile documents.
4. **Cross-references**: reference documents by `doc_id`, not by path. Use `docgen` to validate them.
5. **Product assembly**: product manuals are assembled from fragments declared in `Data/Products/*.yaml` and written to `build/manuals/`.

## Tool conventions

1. **BOMManager** (`Tools/BOMManager`) is the generalized Bill-of-Materials and fabrication package manager. It reads product definitions from `Config/Products.yaml`.
2. **docgen** (`Tools/DocGen`) validates frontmatter, resolves `doc_id` references, and assembles product manuals.
3. Run `pytest` before committing changes to tools.

## Data conventions

1. `Data/Parts/*.json` are committed project data.
2. `Data/Parts/Inventory.json` and `Data/Parts/PriceCache.json` are **gitignored**; they represent personal/local state.
3. Part numbers use the format `HW-{product}-{category}-{descriptor}-{rev}` by default.

## Prohibited changes

1. Do not move hardware designs from `../InverterGen5` into this repo without explicit user approval.
2. Do not commit API keys, vendor credentials, or personal inventory files.
3. Do not hand-edit `Data/Parts/Numbers.json` or `Data/Parts/Descriptors.json`; use BOMManager commands or edit with care.
