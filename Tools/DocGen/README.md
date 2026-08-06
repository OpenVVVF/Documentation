# docgen

OpenVVVF documentation assembly and validation.

## Commands

```bash
# List all doc_ids
python -m docgen index

# Validate cross-references
python -m docgen validate

# Build a product manual
python -m docgen build --product OV-MOTO-C2 --output docs/manuals/product-manuals/openvvvf-motorcycle-kit-c2.md
```

## Product definitions

Products are declared in `data/products/*.yaml`. Each product lists the documents that compose it; `docgen build` concatenates them into a single Markdown manual.
