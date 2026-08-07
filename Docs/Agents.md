# Agent & Contributor Conventions — Documentation Structure

This file explains how the OpenVVVF documentation is organized. Future agents and contributors should follow these conventions when adding or moving documents.

## Top-level sections

The `Docs/` tree has five top-level sections:

1. **Control-Assembly** — The reusable inverter control module.
   - `User-Hardware-Manual/` — Installation, assembly, and hardware specs.
   - `Software-Manual/` — Base firmware, RTE host, flashing, custom code.
2. **Power-Stages** — Physical chassis/inverter assemblies.
   - One folder per chassis family: `C1/`, `C2/`, `C3/`.
   - Each chassis has a `User-Manual/` and an `Assembly-Guide/`.
3. **Safety-and-Compliance** — Cross-cutting safety and standards docs.
   - `HARA/` — Hazard analyses.
   - `Compliance/` — Standards mappings.
4. **Software** — Firmware and host-software docs by target.
   - `Main-MCU/`, `Safety-Coprocessor/`, `RTE-Host/`, `Codegen/`.
5. **Testing** — Formal test and validation evidence.
   - `Hardware/`, `Firmware/`, `Integration/`.

## Every document is a folder containing `Index.md`

Do not create leaf `.md` files directly in a parent directory. Instead, create a folder and put `Index.md` inside it.

Good:
```text
User-Manual/
  └── Index.md
```

Bad:
```text
UserManual.md
```

## Folder naming

- Use kebab-case: `Main-Assembly`, `IGBT-Mounting`, `ISO-26262-Mapping`.
- For ordered assembly chapters/steps, prefix with `<N>_`: `3_Main-Assembly`, `1_IGBT-Mounting`.
- The site generator converts dashes to spaces and renders title case, so `1_IGBT-Mounting` displays as `1 IGBT Mounting`.

## doc_ids

Use hierarchical, kebab-case IDs:

- `OV-CA-*` — Control Assembly
- `OV-C2-*` — Chassis Size 2
- `OV-SAF-*` — Safety and Compliance
- `OV-COMP-*` — Compliance mappings
- `OV-SW-*` — Software
- `OV-TEST-*` — Testing

## Product manuals

Do not assemble use-case product manuals (e.g. "Motorcycle Kit"). A user who builds or buys a C2 inverter receives the control-assembly docs, the C2 user manual, the C2 assembly guide, and applicable safety/compliance/software docs.
