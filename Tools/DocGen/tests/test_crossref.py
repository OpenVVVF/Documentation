"""Tests for cross-reference and link validation."""

from docgen.crossref import validate_crossrefs, validate_links


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


def test_validate_links_ok(tmp_path):
    (tmp_path / "a.md").write_text(
        "---\ndoc_id: OV-A\n---\n\n[A](b.md) and [image](img.png)\n",
        encoding="utf-8",
    )
    (tmp_path / "b.md").write_text("---\ndoc_id: OV-B\n---\n\nB\n", encoding="utf-8")
    (tmp_path / "img.png").write_text("png", encoding="utf-8")
    result = validate_links(tmp_path)
    assert result.ok
    assert not result.errors


def test_validate_links_broken(tmp_path):
    (tmp_path / "a.md").write_text(
        "---\ndoc_id: OV-A\n---\n\n[Broken](missing.md)\n",
        encoding="utf-8",
    )
    result = validate_links(tmp_path)
    assert not result.ok
    assert any("missing.md" in e for e in result.errors)


def test_validate_links_html_and_index_mapping(tmp_path):
    (tmp_path / "a.md").write_text(
        "---\ndoc_id: OV-A\n---\n\n<a href=\"sub/index.html\">sub</a>\n",
        encoding="utf-8",
    )
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "Index.md").write_text(
        "---\ndoc_id: OV-SUB\n---\n\nSub\n", encoding="utf-8"
    )
    result = validate_links(tmp_path)
    assert result.ok
    assert not result.errors


def test_validate_links_external_skipped(tmp_path):
    (tmp_path / "a.md").write_text(
        "---\ndoc_id: OV-A\n---\n\n[External](https://example.com)\n",
        encoding="utf-8",
    )
    result = validate_links(tmp_path)
    assert result.ok
    assert not result.errors
