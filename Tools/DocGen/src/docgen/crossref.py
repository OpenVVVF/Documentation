"""Cross-reference and link validation for documentation."""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple

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


# Markdown links/images: [text](url "title") or ![alt](url "title")
_MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
# HTML anchor and image tags written directly in Markdown.
_HTML_HREF_RE = re.compile(r"<a\s+[^>]*href=[\"']([^\"']+)[\"']", re.IGNORECASE)
_HTML_SRC_RE = re.compile(r"<img\s+[^>]*src=[\"']([^\"']+)[\"']", re.IGNORECASE)


def _strip_markdown_title(url: str) -> str:
    """Remove optional title from a Markdown link URL."""
    url = url.strip()
    # URL may be "path/to/file.md" or "path/to/file.md \"title\"" etc.
    for quote in ('"', "'"):
        if quote in url:
            url = url.split(quote, 1)[0].strip()
            break
    return url.split()[0] if url.split() else url


def _link_targets(body: str) -> List[str]:
    """Extract all link/image targets from a Markdown body."""
    targets: List[str] = []
    targets.extend(_strip_markdown_title(m.group(1)) for m in _MARKDOWN_LINK_RE.finditer(body))
    targets.extend(m.group(1).strip() for m in _HTML_HREF_RE.finditer(body))
    targets.extend(m.group(1).strip() for m in _HTML_SRC_RE.finditer(body))
    return targets


def _is_external(url: str) -> bool:
    """Return True for external/anchor/mailto links that we don't validate."""
    if not url or url.startswith("#"):
        return True
    return bool(re.match(r"^[a-z][a-z0-9+.-]*://", url, re.IGNORECASE)) or url.lower().startswith("mailto:")


def _resolve_target(url: str, doc_dir: Path, docs_dir: Path, existing: Set[str]) -> Tuple[bool, str]:
    """Return (ok, resolved_or_original_path) for a link target."""
    if url.startswith("/"):
        rel = Path(url.lstrip("/"))
    else:
        rel = Path(os.path.normpath(doc_dir / url)).relative_to(docs_dir)

    rel_posix = rel.as_posix()
    candidates: List[str] = [rel_posix]

    # Generated HTML links: index.html -> Index.md, foo.html -> foo.md
    if rel_posix.endswith("/index.html"):
        dir_part = rel_posix[: -len("index.html")]
        candidates.append(f"{dir_part}Index.md")
    elif rel_posix.endswith(".html"):
        # Link may point to a generated Markdown page (foo.html -> foo.md)
        # or to a standalone HTML asset (e.g. embedded web tool).
        candidates.append(rel_posix[: -len(".html")] + ".md")
        candidates.append(rel_posix)
    elif rel_posix.endswith("/"):
        candidates.append(rel_posix + "Index.md")
    else:
        # Bare directory or file without extension
        candidates.append(rel_posix + ".md")
        candidates.append(rel_posix + "/Index.md")

    existing_lower = {p.lower(): p for p in existing}
    for cand in candidates:
        if cand.lower() in existing_lower:
            return True, existing_lower[cand.lower()]

    return False, rel_posix


def validate_links(docs_dir: Path) -> ValidationResult:
    """Validate that every Markdown/HTML link in Docs points to an existing file."""
    result = ValidationResult()
    by_id = load_docs(docs_dir)

    existing: Set[str] = set()
    for path in docs_dir.rglob("*"):
        if path.is_file():
            existing.add(path.relative_to(docs_dir).as_posix())

    for doc in by_id.values():
        doc_dir = doc.path.parent
        for url in _link_targets(doc.body):
            if _is_external(url):
                continue
            ok, resolved = _resolve_target(url, doc_dir, docs_dir, existing)
            if not ok:
                result.errors.append(f"{doc.path}: broken link {url!r}")

    return result
