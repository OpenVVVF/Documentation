"""Tests for cross-reference validation."""

from docgen.crossref import validate_crossrefs


def test_validate_crossrefs_ok(tmp_path):
    (tmp_path / "a.md").write_text(
        "---\ndoc_id: OV-A\nnormative_refs:\n  - OV-B\n---\n\nA\n",
        encoding="utf-8",
    )
    (tmp_path / "b.md").write_text(
        "---\ndoc_id: OV-B\n---\n\nB\n", encoding="utf-8"
    )
    result = validate_crossrefs(tmp_path)
    assert result.ok
    assert not result.errors


def test_validate_crossrefs_missing_ref(tmp_path):
    (tmp_path / "a.md").write_text(
        "---\ndoc_id: OV-A\nnormative_refs:\n  - OV-MISSING\n---\n\nA\n",
        encoding="utf-8",
    )
    result = validate_crossrefs(tmp_path)
    assert not result.ok
    assert any("OV-MISSING" in e for e in result.errors)
