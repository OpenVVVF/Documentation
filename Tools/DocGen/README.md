# docgen

OpenVVVF documentation validation and static site generator.

## Commands

```bash
# List all doc_ids
python -m docgen index

# Validate cross-references
python -m docgen validate

# Build the static HTML site
python -m docgen site --output-dir site

# Assemble a document set into a single Markdown file (legacy product-manual mode)
python -m docgen build --product <product_id> --output <file.md>
```

## Document structure

Documents live under `Docs/` as `Index.md` files inside kebab-case folders. Ordered assembly chapters/steps use a `<N>_<kebab-case-title>` naming convention; the site generator renders dashes as spaces and title-cases the result.
