"""Tests for the kicad-cli export helpers (kicad-cli itself mocked)."""

import subprocess

from hwrelease import kicad


def test_export_bom_groups_by_value_and_dnp(tmp_path, monkeypatch):
    """Regression: grouping by "Value" alone lets a single DNP symbol flag the
    whole grouped row as DNP (KiCad behaviour), and BOMManager's parser then
    drops the populated rows of that value too. The export must group by
    "Value,DNP" so populated and DNP symbols land in separate rows."""
    captured = {}

    def fake_kicad(args, **kwargs):
        captured["args"] = args
        out = tmp_path / args[args.index("-o") + 1]
        out.write_text("dummy")
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(kicad, "kicad", fake_kicad)
    assert kicad.export_bom(tmp_path / "b.kicad_sch", tmp_path / "b.csv")
    args = captured["args"]
    assert args[args.index("--group-by") + 1] == "Value,DNP"
    # the DNP column must be exported for the split rows to be distinguishable
    assert "DNP" in kicad._BOM_FIELDS
