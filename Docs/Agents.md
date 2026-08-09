# Agent & Contributor Conventions - Documentation Structure

This file explains how the OpenVVVF documentation is organized. Future agents and contributors should follow these conventions when adding or moving documents.

## Top-level sections

The `Docs/` tree has five top-level sections:

1. **Hardware** - Physical OpenVVVF hardware.
   - `Control-Assembly/` - The reusable inverter control module.
   - `Power-Stages/` - Chassis/inverter assemblies (`C1/`, `C2/`, `C3/`).
2. **Software** - Firmware and host-software docs by target.
   - `Main-MCU/`, `Safety-Coprocessor/`, `RTE-Studio/`, `Codegen/`.
   - `Tools/` - Software tools and widgets.
3. **Safety-and-Compliance** - Cross-cutting safety, standards, and validation docs.
   - `HARA/` - Hazard analyses.
   - `TARA/` - Threat analyses.
   - `Compliance/` - Standards mappings.
   - `Testing/` - Formal test and validation evidence.

## Every document is a folder containing `Index.md`

Do not create leaf `.md` files directly in a parent directory. Instead, create a folder and put `Index.md` inside it.

Good:
```text
Integration-Guide/
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

- `OV-DOCS-*` - Site / root index
- `OV-CA-*` - Control Assembly
- `OV-PS-*` - Power Stages (top-level)
- `OV-C1-*` - Chassis Size 1
- `OV-C2-*` - Chassis Size 2
  - `OV-C2-IG-*` - C2 Integration Guide
  - `OV-C2-AG-*` - C2 Assembly Guide
  - `OV-C2-DD-*` - C2 Design Documents
- `OV-C3-*` - Chassis Size 3
- `OV-SAF-*` - Safety and Compliance
- `OV-COMP-*` - Compliance mappings
- `OV-SW-*` - Software
- `OV-TEST-*` - Testing

`INDEX` is reserved for the index document of a section or sub-section (e.g. `OV-C2-INDEX`, `OV-C2-DD-INDEX`).

## Frontmatter schema

Every `Index.md` must begin with YAML frontmatter. Required and optional fields:

| Field | Required | Description |
|-------|----------|-------------|
| `doc_id` | yes | Stable kebab-case identifier (see doc_id prefixes above). |
| `title` | yes | Human-readable title shown in nav, breadcrumbs, and headings. |
| `doctype` | yes | Document type. Use one of the canonical values listed below. |
| `version` | yes | Document version, as a string (e.g. `"1.0"`). |
| `date` | yes | ISO-8601 date (`YYYY-MM-DD`). |
| `status` | yes | `draft`, `review`, `released`, or `obsolete`. |
| `nav_order` | yes | Global integer sort key. Lower values appear first. Allocate ranges per section (see below). |
| `description` | yes | One-sentence summary for cards and listings. |
| `product_line` | no | Product line this document belongs to (e.g. `openvvvf`). |
| `applies_to` | no | List of product / variant IDs this document applies to. |
| `normative_refs` | no | List of `doc_id`s this document references. `docgen validate` checks them. |
| `reviewed` | no | Review status or reviewer/date. Omit if not yet reviewed. |
| `placeholder` | no | Set to `true` to flag an incomplete or under-revision page. Renders a banner and emits a validation warning. |

### Canonical doctypes

- `Index` - section or sub-section landing page
- `User Manual` - end-user installation/operation manual
- `User Hardware Manual` - hardware-specific user manual
- `Integration Manual` - electrical/interface integration manual
- `Assembly Guide` - ordered build procedure
- `Design Document` - engineering analysis, calculation, or design rationale
- `Test Report` - formal test evidence
- `Hazard Analysis` or `Hazard Analysis & Risk Assessment`
- `Application Profile` or `Application Profile - Hazard Analysis & Risk Assessment`
- `Threat Analysis` or `Threat Analysis & Risk Assessment`
- `Compliance Mapping`
- `Analysis`
- `Software Manual`
- `Software Note`
- `Software Plan`

Avoid free-form `doctype` values. If none of the canonical types fit, propose a new one in `Docs/Agents.md` rather than inventing an ad-hoc value.

## nav_order allocation

`nav_order` is an integer sort key. Values must be unique across all documents; `make validate` checks this.

Use these ranges for top-level section indices so the sidebar orders consistently:

| Range | Section |
|-------|---------|
| 0 | Root index (`OV-DOCS-INDEX`) |
| 10–99 | Hardware |
| 100–199 | Control Assembly |
| 200–299 | Power Stages |
| 300–399 | Safety and Compliance |
| 400–499 | Software |
| 500–599 | Testing and Validation (under Safety and Compliance) |

Within a section or chassis, choose a consistent scheme that makes the document order obvious. For example, in `Power-Stages/C2/Assembly-Guide/` the convention is `chapter × 10` for chapters and `chapter × 10 + step` for substeps:

- Chapter 3: `nav_order: 30`
- Chapter 3, step 1: `nav_order: 31`
- Chapter 3, step 2: `nav_order: 32`

The exact numbers matter less than being unique and locally consistent.

## Product manuals

Do not assemble use-case product manuals (e.g. "Motorcycle Kit"). A user who builds or buys a C2 inverter receives the control-assembly docs, the C2 user manual, the C2 assembly guide, and applicable safety/compliance/software docs.
