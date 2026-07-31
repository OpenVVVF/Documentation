# OpenVVVF Documentation

This repository is the **single source of truth** for OpenVVVF product documentation, shared hardware data, and documentation tooling.

It is organized around a product-line model:

- **Platform** — the reusable control module and its safety architecture.
- **Power Stages** — physical chassis variants (Chassis Size 2, Size 3, …).
- **Application Profiles** — safety/compliance overlays for motorcycle, passenger car, industrial, rail, etc.
- **Software Targets** — main MCU, safety coprocessor, RTE host, codegen.

Hardware designs remain in [`../InverterGen5`](../InverterGen5). Firmware and host software live in the OpenVVVF/RTE repository. This repo pulls together the documentation for all of them.

## Repository layout

```text
├── docs/          # All documentation (platform, power stages, software, manuals)
├── data/          # Shared part database, product definitions, pricing data
├── tools/         # Documentation and fabrication tooling
│   ├── bom-manager/   # Generalized BOM / fabrication package manager
│   └── docgen/        # Document assembly and cross-reference validation
├── config/        # Repo-level configuration (product registry)
├── README.md
└── pyproject.toml
```

## Quick start

```bash
# Install tool dependencies
pip install -e tools/bom-manager
pip install -e tools/docgen

# Run tests
pytest tools/bom-manager/tests tools/docgen/tests

# Build a product manual
python -m docgen build --product OV-MOTO-C2
```

## Documentation map

| Area | Path |
|------|------|
| Platform safety (HARA, TARA) | `docs/platform/safety/` |
| Compliance standards mapping | `docs/platform/compliance/` |
| Per-chassis docs | `docs/power-stages/` |
| Software docs by target | `docs/software/` |
| Assembled product manuals | `docs/manuals/product-manuals/` |
| Part database | `data/parts/` |
| Product definitions | `data/products/` |

## Contributing

See [`AGENTS.md`](AGENTS.md) for conventions used by contributors and AI agents.
