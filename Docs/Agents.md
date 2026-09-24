# Agent & Contributor Conventions - Documentation Structure

This file explains how the OpenVVVF documentation is organized. Future agents and contributors should follow these conventions when adding or moving documents.

## Top-level sections

The `Docs/` tree has three top-level sections:

1. **Hardware** - Physical OpenVVVF hardware.
   - `Control-Assembly/` - The reusable inverter control module.
   - `Power-Stages/` - Chassis/inverter assemblies (currently `C2/`).
2. **Safety-and-Compliance** - Cross-cutting safety, standards, and validation docs.
   - `HARA/` - Hazard analyses.
   - `TARA/` - Threat analyses.
   - `Compliance/` - Standards mappings.
   - `Testing/` - Formal test and validation evidence.
3. **Tools** - Software tools and widgets.

Firmware and host-software documentation (formerly `Docs/Software/`) was removed as not yet ready; it will be re-added when the software docs are rewritten.

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
- `OV-HW-*` - Hardware section index
- `OV-CA-*` - Control Assembly
- `OV-PS-*` - Power Stages (top-level)
- `OV-C1-*` - Chassis Size 1 (reserved; no documents yet)
- `OV-C2-*` - Chassis Size 2
  - `OV-C2-IG-*` - C2 Integration Guide
  - `OV-C2-AG-*` - C2 Assembly Guide
  - `OV-C2-DD-*` - C2 Design Documents
- `OV-C3-*` - Chassis Size 3 (reserved; data only, no documents yet)
- `OV-SW-*` - Software (reserved; section removed until firmware docs are rewritten)
- `OV-SAF-*` - Safety and Compliance
- `OV-COMP-*` - Compliance mappings
- `OV-TEST-*` - Testing
- `OV-TOOLS-*` - Tools

`INDEX` is reserved for the index document of a section or sub-section (e.g. `OV-C2-INDEX`, `OV-C2-DD-INDEX`).

### Test-report naming convention (hardware power/thermal series)

Test Report doc_ids use `OV-TEST-HW-<MODE>-<CURRENT>-<CONDITIONS>[-GEN7-SIZE2]`:

- `<MODE>`: `REGEN`, `MOTORING`, `THERMAL-OTP`, or the hardware domain (`INDUCTION`, `PMSM`, `GEN7-TEMP`) for non-power-run reports.
- `<CURRENT>`: peak/hold q-axis current, e.g. `200A`, `300A`.
- `<CONDITIONS>`: `STEADY-STATE`, `NO-COOLING`, etc. (omit for one-shot characterization runs).
- `-GEN7-SIZE2` suffix: mandatory for runs on the Gen7 size 2 (C2) assembly; omitted only for pre-Gen7 hardware (e.g. `OV-TEST-HW-REGEN-100A-NO-COOLING` on the C2-class bare stack).

Folder names follow the same tokens in kebab-case with an optional `Low-Power-` series prefix. Deviations require a note in the report's Observations. New reports must follow `Tools`/methodology references in [OV-TEST-METHODOLOGY](../../Safety-and-Compliance/Testing/Test-Methodology/Index.md).

## Frontmatter schema

Every `Index.md` must begin with YAML frontmatter. Required and optional fields:

| Field | Required | Description |
|-------|----------|-------------|
| `doc_id` | yes | Stable kebab-case identifier (see doc_id prefixes above). |
| `title` | yes | Human-readable title shown in nav, breadcrumbs, and headings. |
| `doctype` | yes | Document type. Use one of the canonical values listed below. |
| `version` | yes | Document version, as a string (e.g. `"1.0"`). |
| `date` | yes | ISO-8601 date (`YYYY-MM-DD`). |
| `nav_order` | yes | Global integer sort key. Lower values appear first. Allocate ranges per section (see below). |
| `description` | yes | One-sentence summary for cards and listings. |
| `product_line` | no | Product line this document belongs to (e.g. `openvvvf`). |
| `applies_to` | no | List of product / variant IDs this document applies to. |
| `normative_refs` | no | List of `doc_id`s this document references. `docgen validate` checks them. |
| `placeholder` | no | Set to `true` to flag an incomplete or under-revision page. Renders a banner, a WIP badge, and emits a validation warning. |
| `menu_only` | no | Set to `true` on an `Index` document to make it act as a nav/menu group only: it appears in the sidebar and breadcrumbs but renders no page of its own, and is excluded from lists and PDFs. |
| `test_id` | no | Friendly numeric test identifier for Test Report/Test Plan documents. The site shows it in listings and the metadata panel in place of the opaque `doc_id`, and PDFs print it as "Test ID". |
| `core_ref` | no | On an Application Profile document: the Core document (doc_id + version) the profile was assessed against, e.g. `OV-SAF-HARA-CORE v5.8`. |
| `profile_for` | no | On an Application Profile document: the profile key from `Config/Products.yaml` `application_profiles`, e.g. `motorcycle`. |
| `standard` | no | On an Application Profile document: the standard applied by the analysis, e.g. `ISO 26262:2018`. |
| `temp` | no | Operating-temperature range the analysis covers, e.g. `−40 °C to +85 °C`. |
| `mcus` | no | Microcontroller(s) covered by the analysis, e.g. `STM32H723ZG + STM32G474RCTx`. |

Document maturity is conveyed by `version` plus the `placeholder` flag. There is deliberately no `status` or `reviewed` field; bump `version` when a document changes materially.

### Canonical doctypes

- `Index` - section or sub-section landing page
- `User Manual` - end-user installation/operation manual
- `User Hardware Manual` - hardware-specific user manual
- `Integration Manual` - electrical/interface integration manual
- `Assembly Guide` - ordered build procedure
- `Design Document` - engineering analysis, calculation, or design rationale
- `Test Plan` - test plan defining test cases, procedures, and acceptance criteria
- `Test Report` - formal test evidence
- `Hazard Analysis` or `Hazard Analysis & Risk Assessment`
- `Application Profile` or `Application Profile - Hazard Analysis & Risk Assessment`
- `Threat Analysis` or `Threat Analysis & Risk Assessment`
- `Compliance Mapping`
- `Analysis`
- `Software Manual`
- `Software Note`
- `Software Plan`
- `Tool Manual`

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
| 300–399 | Safety and Compliance (incl. Testing at 340–379; test plans and stubs extend into 380–399 as the 340–379 block fills) |
| 400–499 | (reserved; formerly Software) |
| 600–699 | Tools |

Within a section or chassis, choose a consistent scheme that makes the document order obvious. For example, in `Power-Stages/C2/Assembly-Guide/` chapters use sequential values within a local block (guide index 222, chapters 223, 224, ...). The exact numbers matter less than being unique and locally consistent.

## Section boundaries

- **`Hardware/Control-Assembly/Software-Manual/`** - the user-facing "operate the software on this hardware" companion. Firmware internals documentation (formerly `Docs/Software/`) will be re-added separately; the manual must not duplicate it.
- **Testing domain folders** - file test documents by what is being tested (DUT), not by bench equipment: Hardware = physical hardware is the DUT; Firmware = firmware logic is the DUT without physical fault injection; Integration = combined system. Campaigns spanning all domains (e.g. the fault-injection plan) are filed directly under `Testing/`. Plans are living documents; each execution campaign produces a separate dated Test Report referencing the plan by doc_id and test ID.

## Product manuals

Do not assemble use-case product manuals (e.g. "Motorcycle Kit"). A user who builds or buys a C2 inverter receives the control-assembly docs, the C2 user manual, the C2 assembly guide, and applicable safety/compliance/software docs.
