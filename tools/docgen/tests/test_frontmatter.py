"""Tests for frontmatter parsing."""

from pathlib import Path

from docgen.frontmatter import load_docs, parse_document


def test_parse_document_with_frontmatter(tmp_path):
    doc_path = tmp_path / "doc.md"
    doc_path.write_text(
        "---\ndoc_id: OV-TEST-1\ntitle: Test\n---\n\n# Body\n",
        encoding="utf-8",
    )
    doc = parse_document(doc_path)
    assert doc.doc_id == "OV-TEST-1"
    assert doc.title == "Test"
    assert doc.body.strip() == "# Body"


def test_parse_document_without_frontmatter(tmp_path):
    doc_path = tmp_path / "doc.md"
    doc_path.write_text("# Body\n", encoding="utf-8")
    doc = parse_document(doc_path)
    assert doc.doc_id is None
    assert doc.body.strip() == "# Body"


def test_load_docs_indexed_by_doc_id(tmp_path):
    doc_path = tmp_path / "doc.md"
    doc_path.write_text(
        "---\ndoc_id: OV-TEST-2\ntitle: Test\n---\n\n# Body\n",
        encoding="utf-8",
    )
    by_id = load_docs(tmp_path)
    assert "OV-TEST-2" in by_id
    assert by_id["OV-TEST-2"].title == "Test"


def test_duplicate_doc_id_raises(tmp_path):
    (tmp_path / "a.md").write_text(
        "---\ndoc_id: OV-DUP\n---\n\nA\n", encoding="utf-8"
    )
    (tmp_path / "b.md").write_text(
        "---\ndoc_id: OV-DUP\n---\n\nB\n", encoding="utf-8"
    )
    try:
        load_docs(tmp_path)
        assert False, "expected ValueError"
    except ValueError as e:
        assert "Duplicate doc_id" in str(e)
