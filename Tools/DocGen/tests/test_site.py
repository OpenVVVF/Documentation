"""Tests for site generation helpers."""

from docgen.site import _apply_callout_classes, _split_consecutive_blockquotes


def test_split_consecutive_blockquotes_on_blank_line():
    src = "> A\n\n> B\n"
    assert _split_consecutive_blockquotes(src) == "> A\n<!-- -->\n> B"


def test_no_split_when_blockquote_lines_are_adjacent():
    src = "> A\n> B\n"
    assert _split_consecutive_blockquotes(src) == "> A\n> B"


def test_no_split_inside_code_fence():
    src = "```\n> A\n\n> B\n```\n"
    assert _split_consecutive_blockquotes(src) == "```\n> A\n\n> B\n```"


def test_apply_callout_classes_adds_note_class_and_icon():
    html = '<blockquote><p><strong>NOTE</strong><br />\nBody</p></blockquote>'
    out = _apply_callout_classes(html)
    assert 'class="callout-note"' in out
    assert '<span class="callout-icon" aria-hidden="true"></span>' in out
    assert '<strong>Note</strong>' in out


def test_apply_callout_classes_preserves_colon():
    html = '<blockquote><p><strong>WARNING:</strong> Body</p></blockquote>'
    out = _apply_callout_classes(html)
    assert 'class="callout-warning"' in out
    assert '<strong>Warning:</strong>' in out
