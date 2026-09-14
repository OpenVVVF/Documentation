"""Tests for the kicad-cli export helpers (kicad-cli itself mocked)."""

import subprocess
from pathlib import Path

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


def test_export_ibom_stops_git_describe_at_venv(tmp_path, monkeypatch):
    """Regression: InteractiveHtmlBom's version.py runs `git describe` in its
    own directory. The venv sits inside the tagged hardware repo, so the
    generated pcbdata.ibom_version became e.g. "C2-DCDC-A-10-g342f-*", and the
    iBOM page crashed on /^v\\d+\\.\\d+/.exec(ibom_version) (blank body, empty
    component list). GIT_CEILING_DIRECTORIES must confine git to the venv so
    the plugin falls back to its built-in vX.Y.Z version string."""
    venv = tmp_path / ".venv"
    generator = (venv / "lib" / "python3.11" / "site-packages"
                 / "InteractiveHtmlBom" / "generate_interactive_bom.py")
    generator.parent.mkdir(parents=True)
    generator.write_text("# fake")
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        pcb = Path(cmd[-1])
        (Path(cmd[cmd.index("--dest-dir") + 1]) / f"{pcb.stem}.html").write_text("x")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(kicad.subprocess, "run", fake_run)
    out = tmp_path / "out" / "ibom.html"
    assert kicad.export_ibom(tmp_path / "b.kicad_pcb", out, generator)
    ceilings = [a[len("--env=GIT_CEILING_DIRECTORIES="):] for a in captured["cmd"]
                if a.startswith("--env=GIT_CEILING_DIRECTORIES=")]
    assert ceilings == [str(venv)]
