"""Parse and normalize YAML frontmatter from Markdown documents."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class Document:
    path: Path
    frontmatter: Dict[str, Any]
    body: str
    line_offset: int

    @property
    def doc_id(self) -> Optional[str]:
        return self.frontmatter.get("doc_id")

    @property
    def title(self) -> Optional[str]:
        return self.frontmatter.get("title")

    @property
    def doctype(self) -> Optional[str]:
        return self.frontmatter.get("doctype")

    @property
    def normative_refs(self) -> List[str]:
        refs = self.frontmatter.get("normative_refs", [])
        return list(refs) if isinstance(refs, list) else []

    @property
    def applies_to(self) -> List[str]:
        value = self.frontmatter.get("applies_to", [])
        return list(value) if isinstance(value, list) else []


def parse_document(path: Path) -> Document:
    """Parse a Markdown file, extracting YAML frontmatter if present."""
    text = path.read_text(encoding="utf-8")
    frontmatter: Dict[str, Any] = {}
    body = text
    line_offset = 0

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if match:
        try:
            frontmatter = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid frontmatter in {path}: {e}") from e
        body = text[match.end() :]
        line_offset = match.group(0).count("\n")

    return Document(
        path=path,
        frontmatter=frontmatter,
        body=body,
        line_offset=line_offset,
    )


def load_docs(docs_dir: Path) -> Dict[str, Document]:
    """Load all Markdown documents under docs_dir, indexed by doc_id."""
    by_id: Dict[str, Document] = {}
    for path in sorted(docs_dir.rglob("*.md")):
        doc = parse_document(path)
        if doc.doc_id:
            if doc.doc_id in by_id:
                raise ValueError(
                    f"Duplicate doc_id {doc.doc_id!r}: {by_id[doc.doc_id].path} and {path}"
                )
            by_id[doc.doc_id] = doc
    return by_id
