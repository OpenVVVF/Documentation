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
├── Docs/          # All documentation (platform, power stages, software, manuals)
├── Data/          # Shared part database, product definitions, pricing data
├── Tools/         # Documentation and fabrication tooling
│   ├── bom-manager/   # Generalized BOM / fabrication package manager
│   └── docgen/        # Document assembly and cross-reference validation
├── Config/        # Repo-level configuration (product registry)
├── README.md
└── pyproject.toml
```

## Quick start

```bash
# Install tool dependencies
pip install -e Tools/BOMManager
pip install -e Tools/DocGen

# Run tests
pytest Tools/BOMManager/tests Tools/DocGen/tests

# Build a product manual
python -m docgen build --product OV-MOTO-C2
```

## Documentation map

| Area | Path |
|------|------|
| Platform safety (HARA, TARA) | `Docs/Platform/Safety/` |
| Compliance standards mapping | `Docs/Platform/Compliance/` |
| Per-chassis docs | `Docs/PowerStages/` |
| Software docs by target | `Docs/Software/` |
| Assembled product manuals | `Docs/Manuals/ProductManuals/` |
| Part database | `Data/Parts/` |
| Product definitions | `Data/Products/` |

## Contributing

See [`AGENTS.md`](AGENTS.md) for conventions used by contributors and AI agents.
