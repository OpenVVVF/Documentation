"""Assemble product manuals from product definitions."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

import yaml

from .frontmatter import Document, load_docs


@dataclass
class Product:
    product_id: str
    data: Dict[str, Any]

    @property
    def name(self) -> str:
        return self.data.get("name", self.product_id)

    @property
    def doc_paths(self) -> List[Path]:
        paths = self.data.get("docs", [])
        return [Path(p) for p in paths]


def load_product(path: Path) -> Product:
    """Load a product definition YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return Product(product_id=data.get("product_id", path.stem), data=data)


def list_products(products_dir: Path) -> List[Product]:
    """Load all product definitions in products_dir."""
    products = []
    for path in sorted(products_dir.glob("*.yaml")):
        products.append(load_product(path))
    return products


def assemble_manual(product: Product, docs_dir: Path) -> str:
    """Assemble a product manual by concatenating referenced documents."""
    by_id = load_docs(docs_dir)
    parts: List[str] = []

    parts.append(f"# {product.name}\n")
    parts.append(f"_Product ID: `{product.product_id}`_\n")

    for rel_path in product.doc_paths:
        doc_path = docs_dir.parent / rel_path
        if not doc_path.exists():
            parts.append(f"\n> Missing document: {rel_path}\n")
            continue

        doc = Document(path=doc_path, frontmatter={}, body=doc_path.read_text(encoding="utf-8"), line_offset=0)
        # Re-parse to strip frontmatter if present.
        from .frontmatter import parse_document
        doc = parse_document(doc_path)

        parts.append(f"\n<!-- begin {doc.doc_id or rel_path} -->\n")
        # Add a heading if the body doesn't start with one.
        body = doc.body.strip()
        if doc.title and not body.startswith("# "):
            parts.append(f"\n## {doc.title}\n")
        parts.append(body)
        parts.append(f"\n<!-- end {doc.doc_id or rel_path} -->\n")

    return "\n".join(parts)
