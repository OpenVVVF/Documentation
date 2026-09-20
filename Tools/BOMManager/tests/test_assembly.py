"""Tests for InteractiveHtmlBom command construction."""

import subprocess
from pathlib import Path

from bom_manager import assembly


def test_build_ibom_excludes_schematic_native_kicad_dnp(tmp_path, monkeypatch):
    """The CLI must load schematic fields and filter native KiCad DNP."""
    script = (tmp_path / ".venv" / "lib" / "python3.11"
              / "site-packages" / "InteractiveHtmlBom"
              / "generate_interactive_bom.py")
    script.parent.mkdir(parents=True)
    script.write_text("# fake")
    captured = {"commands": []}

    monkeypatch.setattr(assembly, "_generator_script", lambda: script)

    def fake_run(cmd, **kwargs):
        captured["commands"].append(cmd)
        if "--command=kicad-cli" in cmd:
            Path(cmd[cmd.index("-o") + 1]).write_text("<export/>")
            return subprocess.CompletedProcess(cmd, 0, "", "")
        pcb = Path(cmd[-1])
        (Path(cmd[cmd.index("--dest-dir") + 1])
         / f"{pcb.stem}.html").write_text("x")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(assembly.subprocess, "run", fake_run)
    pcb = tmp_path / "control.kicad_pcb"
    pcb.write_text("pcb")
    schematic = pcb.with_suffix(".kicad_sch")
    schematic.write_text("sch")
    out_dir = tmp_path / "Assembly"

    assert assembly.build_ibom(pcb, out_dir)
    netlist_cmd, ibom_cmd = captured["commands"]
    assert str(schematic) in netlist_cmd
    extra_data = Path(ibom_cmd[ibom_cmd.index("--extra-data-file") + 1])
    assert extra_data.name == "control.xml"
    assert extra_data != pcb
    assert ibom_cmd[ibom_cmd.index("--dnp-field") + 1] == "kicad_dnp"


def test_build_ibom_board_only_falls_back_to_pcb_fields(tmp_path, monkeypatch):
    """A board without a matching schematic keeps the pre-existing workflow."""
    script = (tmp_path / ".venv" / "lib" / "python3.11"
              / "site-packages" / "InteractiveHtmlBom"
              / "generate_interactive_bom.py")
    script.parent.mkdir(parents=True)
    script.write_text("# fake")
    pcb = tmp_path / "board_only.kicad_pcb"
    pcb.write_text("pcb")
    captured = {}

    monkeypatch.setattr(assembly, "_generator_script", lambda: script)

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        (Path(cmd[cmd.index("--dest-dir") + 1])
         / f"{pcb.stem}.html").write_text("x")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(assembly.subprocess, "run", fake_run)
    out_dir = tmp_path / "Assembly"

    assert assembly.build_ibom(pcb, out_dir)
    cmd = captured["cmd"]
    assert cmd[cmd.index("--extra-data-file") + 1] == str(pcb)
