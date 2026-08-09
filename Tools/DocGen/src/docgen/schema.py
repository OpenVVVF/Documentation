"""Frontmatter schema validation for OpenVVVF documentation."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from .frontmatter import Document, load_docs


REQUIRED_FIELDS = {
    "doc_id",
    "title",
    "doctype",
    "version",
    "date",
    "status",
    "nav_order",
    "description",
}

OPTIONAL_FIELDS = {
    "product_line",
    "applies_to",
    "normative_refs",
    "reviewed",
    "placeholder",
    "mcus",
    "temp",
    "core_ref",
    "profile_for",
    "standard",
    "menu_only",
    "test_id",
}

ALLOWED_STATUSES = {"draft", "review", "released", "obsolete", "elaborated"}

ALLOWED_DOCTYPES = {
    "Index",
    "User Manual",
    "User Hardware Manual",
    "Integration Manual",
    "Assembly Guide",
    "Design Document",
    "Test Report",
    "Hazard Analysis",
    "Hazard Analysis & Risk Assessment",
    "Application Profile",
    "Application Profile - Hazard Analysis & Risk Assessment",
    "Threat Analysis",
    "Threat Analysis & Risk Assessment",
    "Compliance Mapping",
    "Analysis",
    "Software Manual",
    "Software Note",
    "Software Plan",
    "Tool Manual",
}

# Map a doc_id prefix to a canonical top-level directory. Used for warnings only.
PREFIX_TO_DIR = {
    "OV-DOCS-": "Docs",
    "OV-CA-": "Control-Assembly",
    "OV-PS-": "Power-Stages",
    "OV-C1-": "Power-Stages/C1",
    "OV-C2-": "Power-Stages/C2",
    "OV-C3-": "Power-Stages/C3",
    "OV-SAF-": "Safety-and-Compliance",
    "OV-COMP-": "Safety-and-Compliance/Compliance",
    "OV-SW-": "Software",
    "OV-TEST-": "Testing",
    "OV-TOOLS-": "Tools",
}


@dataclass
class ValidationResult:
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _prefix_for_path(rel_path: Path) -> Optional[str]:
    """Return the expected doc_id prefix for a document path."""
    parts = rel_path.parts
    if len(parts) == 0:
        return "OV-DOCS-"

    top = parts[0]
    if top == "Docs":
        return "OV-DOCS-"
    if top == "Control-Assembly":
        return "OV-CA-"
    if top == "Safety-and-Compliance":
        if len(parts) > 1 and parts[1] == "Compliance":
            return "OV-COMP-"
        return "OV-SAF-"
    if top == "Software":
        return "OV-SW-"
    if top == "Testing":
        return "OV-TEST-"
    if top == "Tools":
        return "OV-TOOLS-"
    if top == "Power-Stages":
        if len(parts) > 1:
            chassis = parts[1]
            if chassis == "C1":
                return "OV-C1-"
            if chassis == "C2":
                return "OV-C2-"
            if chassis == "C3":
                return "OV-C3-"
        return "OV-PS-"
    return None


def _check_prefix(doc: Document, docs_dir: Path, result: ValidationResult) -> None:
    """Warn if doc_id prefix does not match the documented convention."""
    rel_path = doc.path.relative_to(docs_dir)
    expected_prefix = _prefix_for_path(rel_path)
    if expected_prefix is None:
        return
    doc_id = doc.doc_id or ""
    if not doc_id.startswith(expected_prefix):
        result.warnings.append(
            f"{doc.path}: doc_id '{doc_id}' does not start with expected "
            f"prefix '{expected_prefix}' for path {rel_path}"
        )


def validate_docs(docs_dir: Path) -> ValidationResult:
    """Validate frontmatter schema and cross-references for all documents."""
    result = ValidationResult()
    by_id = load_docs(docs_dir)
    docs = list(by_id.values())

    nav_orders: Dict[int, Document] = {}

    for doc in docs:
        fm = doc.frontmatter
        path = doc.path

        # Required fields
        missing = REQUIRED_FIELDS - set(fm.keys())
        if missing:
            result.errors.append(
                f"{path}: missing required frontmatter field(s): {', '.join(sorted(missing))}"
            )

        # Unknown fields
        unknown = set(fm.keys()) - REQUIRED_FIELDS - OPTIONAL_FIELDS
        if unknown:
            result.warnings.append(
                f"{path}: unknown frontmatter field(s): {', '.join(sorted(unknown))}"
            )

        # Status enum
        status = fm.get("status")
        if status is not None and status not in ALLOWED_STATUSES:
            result.errors.append(
                f"{path}: status '{status}' is not one of {sorted(ALLOWED_STATUSES)}"
            )

        # Doctype enum
        doctype = fm.get("doctype")
        if doctype is not None and doctype not in ALLOWED_DOCTYPES:
            result.errors.append(
                f"{path}: doctype '{doctype}' is not one of {sorted(ALLOWED_DOCTYPES)}"
            )

        # Placeholder flag (explicit or heuristic)
        if fm.get("placeholder"):
            result.warnings.append(
                f"{path}: marked as placeholder - content needs to be completed or reviewed"
            )
        elif doc.doc_id != "OV-DOCS-INDEX":
            body_text = doc.body.strip()
            body_len = len(body_text)
            is_index = doctype == "Index"
            placeholder_phrases = re.findall(
                r"(?i)(content to be|placeholder|under revision|to be added|to be migrated|stub)",
                body_text,
            )
            if placeholder_phrases:
                result.warnings.append(
                    f"{path}: document body contains placeholder language; consider adding "
                    f"`placeholder: true` to frontmatter"
                )
            elif not is_index and body_len < 500:
                result.warnings.append(
                    f"{path}: document body is very short ({body_len} chars); may be a placeholder"
                )

        # nav_order uniqueness and type
        nav_order = fm.get("nav_order")
        if nav_order is not None:
            try:
                order = int(nav_order)
            except (TypeError, ValueError):
                result.errors.append(
                    f"{path}: nav_order '{nav_order}' is not an integer"
                )
                order = None

            if order is not None:
                if order in nav_orders:
                    other = nav_orders[order]
                    result.errors.append(
                        f"{path}: nav_order {order} is already used by {other.path}"
                    )
                else:
                    nav_orders[order] = doc

        # doc_id prefix convention
        if doc.doc_id:
            _check_prefix(doc, docs_dir, result)

    return result
