"""Command-line interface for docgen."""

import argparse
import sys
from pathlib import Path

from .crossref import validate_crossrefs, validate_links
from .frontmatter import load_docs
from .pdf import build_all_pdfs, build_pdf
from .product import assemble_manual, list_products, load_product
from .schema import validate_docs
from .site import build_site


def repo_root() -> Path:
    """Return the repository root.

    This module lives at Tools/DocGen/src/docgen/cli.py, so the repo root is
    five parents up.
    """
    return Path(__file__).resolve().parent.parent.parent.parent.parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="OpenVVVF documentation tooling")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # index command
    index_parser = subparsers.add_parser("index", help="List all documented doc_ids")
    index_parser.add_argument(
        "--docs-dir", type=Path, default=repo_root() / "Docs"
    )

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate cross-references")
    validate_parser.add_argument(
        "--docs-dir", type=Path, default=repo_root() / "Docs"
    )

    # build command
    build_parser = subparsers.add_parser("build", help="Assemble a product manual")
    build_parser.add_argument("--product", required=True, help="Product ID or product YAML path")
    build_parser.add_argument(
        "--docs-dir", type=Path, default=repo_root() / "Docs"
    )
    build_parser.add_argument("--output", type=Path, help="Output Markdown file")

    # site command
    site_parser = subparsers.add_parser("site", help="Build a static HTML site")
    site_parser.add_argument(
        "--docs-dir", type=Path, default=repo_root() / "Docs"
    )
    site_parser.add_argument(
        "--output-dir", type=Path, default=repo_root() / "site"
    )

    # pdf command
    pdf_parser = subparsers.add_parser("pdf", help="Generate clean PDFs from the built site")
    pdf_parser.add_argument(
        "--docs-dir", type=Path, default=repo_root() / "Docs"
    )
    pdf_parser.add_argument(
        "--site-dir", type=Path, default=repo_root() / "site"
    )
    pdf_parser.add_argument(
        "--output-dir", type=Path, default=repo_root() / "build" / "pdfs"
    )
    pdf_parser.add_argument("--doc", help="Generate PDF for a single doc_id")
    pdf_parser.add_argument(
        "--all", action="store_true", help="Generate PDFs for all documents"
    )
    pdf_parser.add_argument(
        "--chromium", help="Path to Chromium/Chrome executable"
    )

    args = parser.parse_args(argv)

    if args.command == "index":
        by_id = load_docs(args.docs_dir)
        for doc_id in sorted(by_id):
            doc = by_id[doc_id]
            print(f"{doc_id:40} {doc.path}")
        return 0

    if args.command == "validate":
        frontmatter_result = validate_docs(args.docs_dir)
        crossref_result = validate_crossrefs(args.docs_dir)
        link_result = validate_links(args.docs_dir)
        for error in frontmatter_result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        for warning in frontmatter_result.warnings:
            print(f"WARNING: {warning}", file=sys.stderr)
        for error in crossref_result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        for warning in crossref_result.warnings:
            print(f"WARNING: {warning}", file=sys.stderr)
        for error in link_result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        for warning in link_result.warnings:
            print(f"WARNING: {warning}", file=sys.stderr)
        ok = frontmatter_result.ok and crossref_result.ok and link_result.ok
        if ok:
            print("All cross-references and links valid.")
        return 0 if ok else 1

    if args.command == "build":
        product_path = Path(args.product)
        if not product_path.exists():
            products_dir = repo_root() / "Data" / "Products"
            candidate = products_dir / f"{args.product}.yaml"
            if candidate.exists():
                product_path = candidate
            else:
                # Fall back to matching by product_id inside the YAML files.
                for path in sorted(products_dir.glob("*.yaml")):
                    try:
                        prod = load_product(path)
                    except Exception:  # pragma: no cover
                        continue
                    if prod.product_id == args.product:
                        product_path = path
                        break
                if not product_path.exists():
                    print(f"Product not found: {args.product}", file=sys.stderr)
                    return 1

        product = load_product(product_path)
        output = assemble_manual(product, args.docs_dir)

        if args.output:
            args.output.write_text(output, encoding="utf-8")
            print(f"Wrote {args.output}")
        else:
            print(output)
        return 0

    if args.command == "site":
        build_site(args.docs_dir, args.output_dir)
        return 0

    if args.command == "pdf":
        if args.all:
            build_all_pdfs(
                args.docs_dir,
                args.site_dir,
                args.output_dir,
                chromium_path=args.chromium,
            )
            return 0
        if args.doc:
            output_path = build_pdf(
                args.doc,
                args.docs_dir,
                args.site_dir,
                args.output_dir,
                chromium_path=args.chromium,
            )
            print(f"Wrote {output_path}")
            return 0
        print("Specify --doc <doc_id> or --all", file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
