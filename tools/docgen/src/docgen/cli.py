"""Command-line interface for docgen."""

import argparse
import sys
from pathlib import Path

from .crossref import validate_crossrefs
from .frontmatter import load_docs
from .product import assemble_manual, list_products, load_product


def repo_root() -> Path:
    """Return the repository root.

    This module lives at tools/docgen/src/docgen/cli.py, so the repo root is
    five parents up.
    """
    return Path(__file__).resolve().parent.parent.parent.parent.parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="OpenVVVF documentation tooling")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # index command
    index_parser = subparsers.add_parser("index", help="List all documented doc_ids")
    index_parser.add_argument(
        "--docs-dir", type=Path, default=repo_root() / "docs"
    )

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate cross-references")
    validate_parser.add_argument(
        "--docs-dir", type=Path, default=repo_root() / "docs"
    )

    # build command
    build_parser = subparsers.add_parser("build", help="Assemble a product manual")
    build_parser.add_argument("--product", required=True, help="Product ID or product YAML path")
    build_parser.add_argument(
        "--docs-dir", type=Path, default=repo_root() / "docs"
    )
    build_parser.add_argument("--output", type=Path, help="Output Markdown file")

    args = parser.parse_args(argv)

    if args.command == "index":
        by_id = load_docs(args.docs_dir)
        for doc_id in sorted(by_id):
            doc = by_id[doc_id]
            print(f"{doc_id:40} {doc.path}")
        return 0

    if args.command == "validate":
        result = validate_crossrefs(args.docs_dir)
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        for warning in result.warnings:
            print(f"WARNING: {warning}", file=sys.stderr)
        if result.ok:
            print("All cross-references valid.")
        return 0 if result.ok else 1

    if args.command == "build":
        product_path = Path(args.product)
        if not product_path.exists():
            products_dir = repo_root() / "data" / "products"
            candidate = products_dir / f"{args.product}.yaml"
            if candidate.exists():
                product_path = candidate
            else:
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

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
