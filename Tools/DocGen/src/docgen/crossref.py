"""Cross-reference validation for doc_id links."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from .frontmatter import Document, load_docs


@dataclass
class ValidationResult:
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_crossrefs(docs_dir: Path) -> ValidationResult:
    """Validate that every normative_refs entry points to a known doc_id."""
    result = ValidationResult()
    by_id = load_docs(docs_dir)

    for doc in by_id.values():
        for ref in doc.normative_refs:
            if ref not in by_id:
                result.errors.append(
                    f"{doc.path}: unknown normative_ref {ref!r}"
                )

    return result
