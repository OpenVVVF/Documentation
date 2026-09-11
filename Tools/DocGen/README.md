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

# Generate clean PDFs from the built site (run `site` first; uses headless Chromium)
python -m docgen pdf --all                    # one PDF per document
python -m docgen pdf --doc OV-C2-UM-INDEX     # a single document
python -m docgen pdf --manual OV-C2-AG-INDEX  # umbrella PDF: index document plus its chapters
python -m docgen pdf --all --chromium /path/to/chrome   # explicit Chromium/Chrome binary
```

## Document structure

Documents live under `Docs/` as `Index.md` files inside kebab-case folders. Ordered assembly chapters/steps use a `<N>_<kebab-case-title>` naming convention; the site generator renders dashes as spaces and title-cases the result.
