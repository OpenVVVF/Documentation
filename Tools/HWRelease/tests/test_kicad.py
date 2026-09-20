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

    pcb = tmp_path / "b.kicad_pcb"
    pcb.write_text("pcb")
    pcb.with_suffix(".kicad_sch").write_text("sch")

    def fake_export_netlist(schematic, out_xml):
        out_xml.write_text("<export/>")
        return True

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        pcb = Path(cmd[-1])
        (Path(cmd[cmd.index("--dest-dir") + 1]) / f"{pcb.stem}.html").write_text("x")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(kicad.subprocess, "run", fake_run)
    monkeypatch.setattr(kicad, "export_netlist", fake_export_netlist)
    out = tmp_path / "out" / "ibom.html"
    assert kicad.export_ibom(pcb, out, generator)
    ceilings = [a[len("--env=GIT_CEILING_DIRECTORIES="):] for a in captured["cmd"]
                if a.startswith("--env=GIT_CEILING_DIRECTORIES=")]
    assert ceilings == [str(venv)]


def test_export_ibom_excludes_schematic_native_kicad_dnp(tmp_path, monkeypatch):
    """InteractiveHtmlBom must load schematic fields and use ``kicad_dnp``.

    Without both options, native KiCad DNP footprints are emitted as normal
    placement rows and ``pcbdata.bom.skipped`` is empty.
    """
    generator = (tmp_path / ".venv" / "lib" / "python3.11"
                 / "site-packages" / "InteractiveHtmlBom"
                 / "generate_interactive_bom.py")
    generator.parent.mkdir(parents=True)
    generator.write_text("# fake")
    captured = {}

    pcb = tmp_path / "control.kicad_pcb"
    pcb.write_text("pcb")
    schematic = pcb.with_suffix(".kicad_sch")
    schematic.write_text("sch")

    def fake_export_netlist(input_schematic, out_xml):
        captured["schematic"] = input_schematic
        out_xml.write_text("<export/>")
        return True

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        pcb = Path(cmd[-1])
        (Path(cmd[cmd.index("--dest-dir") + 1])
         / f"{pcb.stem}.html").write_text("x")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(kicad.subprocess, "run", fake_run)
    monkeypatch.setattr(kicad, "export_netlist", fake_export_netlist)
    out = tmp_path / "out" / "ibom.html"

    assert kicad.export_ibom(pcb, out, generator)
    cmd = captured["cmd"]
    extra_data = Path(cmd[cmd.index("--extra-data-file") + 1])
    assert captured["schematic"] == schematic
    assert extra_data.name == "control.xml"
    assert extra_data != pcb
    assert cmd[cmd.index("--dnp-field") + 1] == "kicad_dnp"


def test_export_ibom_board_only_falls_back_to_pcb_fields(tmp_path, monkeypatch):
    """Board-only projects still generate an iBOM using their PCB DNP flags."""
    generator = (tmp_path / ".venv" / "lib" / "python3.11"
                 / "site-packages" / "InteractiveHtmlBom"
                 / "generate_interactive_bom.py")
    generator.parent.mkdir(parents=True)
    generator.write_text("# fake")
    pcb = tmp_path / "board_only.kicad_pcb"
    pcb.write_text("pcb")
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        (Path(cmd[cmd.index("--dest-dir") + 1])
         / f"{pcb.stem}.html").write_text("x")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(kicad.subprocess, "run", fake_run)
    out = tmp_path / "out" / "ibom.html"

    assert kicad.export_ibom(pcb, out, generator)
    cmd = captured["cmd"]
    assert cmd[cmd.index("--extra-data-file") + 1] == str(pcb)
