# OpenVVVF Documentation

This repository is the **single source of truth** for OpenVVVF product documentation, shared hardware data, and documentation tooling.

It is organized by hardware and software domain:

- **Control Assembly**: the reusable inverter control module (user hardware manual and software manual).
- **Power Stages**: physical chassis/inverter assemblies (C1, C2, C3, …), each with a user manual and an assembly guide.
- **Safety and Compliance**: HARA, compliance mappings, and standards references.
- **Software**: firmware and host-software docs by target.
- **Testing**: formal test reports and validation evidence.

Hardware designs remain in [`../InverterGen5`](../InverterGen5). Firmware and host software live in the OpenVVVF/RTE repository. This repo pulls together the documentation for all of them.

## Repository layout

```text
├── Docs/          # All documentation
├── Data/          # Shared part database and pricing data
├── Tools/         # Documentation and fabrication tooling
│   ├── BOMManager/    # Generalized BOM / fabrication package manager
│   └── DocGen/        # Document validation and static site generator
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

# Validate cross-references
python -m docgen validate

# Build the static site
python -m docgen site --output-dir site
```

## Documentation map

| Area | Path |
|------|------|
| Control assembly | `Docs/Control-Assembly/` |
| Power stages | `Docs/Power-Stages/` |
| Safety and compliance | `Docs/Safety-and-Compliance/` |
| Software docs by target | `Docs/Software/` |
| Testing and validation | `Docs/Testing/` |
| Part database | `Data/Parts/` |

## Contributing

See [`AGENTS.md`](AGENTS.md) and [`Docs/Agents.md`](Docs/Agents.md) for conventions used by contributors and AI agents.

## Sponsors

A special thank you to our sponsors for helping make this project possible:

<p>
  <a href="https://mouser.com"><img src="https://cdn.trustedparts.com/company/dd042a20-7bd6-4e96-92c0-203775acde0d-mouser-logo.svg" height="36" alt="Mouser Electronics"></a>
  &nbsp;&nbsp;
  <a href="https://www.mitsubishielectric.com/semiconductors/powerdevices/"><img src="https://upload.wikimedia.org/wikipedia/commons/1/10/Mitsubishi_Electric_logo.svg" height="36" alt="Mitsubishi Electric"></a>
  &nbsp;&nbsp;
  <a href="https://sendcutsend.com/"><img src="https://sendcutsend.com/wp-content/uploads/2022/11/scs-logo-text-1-1.svg" height="36" alt="SendCutSend"></a>
</p>
