"""Tests for hwrelease core pipeline (kicad-cli calls mocked)."""

import json
import subprocess
from pathlib import Path

import pytest

from hwrelease import core


@pytest.fixture
def hw_repo(tmp_path):
    """A minimal git repo mimicking InverterGen5, tagged hw-rev-a and hw-rev-b."""
    repo = tmp_path / "InverterGen5"
    board = repo / "Hardware" / "Chassis2" / "Boards" / "ControlBoard"
    board.mkdir(parents=True)
    (board / "ControlBoard.kicad_sch").write_text('(kicad_sch (rev "A"))')
    (board / "ControlBoard.kicad_pcb").write_text('(kicad_pcb (rev "A"))')
    (repo / "Hardware" / "Chassis2" / "Boards" / "ControlBoard.png").write_bytes(b"png")
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "--allow-empty",
                    "-m", "init"], check=True,
                   env=_git_env())
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "rev A"],
                   check=True, env=_git_env())
    subprocess.run(["git", "-C", str(repo), "tag", "hw-rev-a"], check=True)
    # bump to rev B on a second tag
    (board / "ControlBoard.kicad_sch").write_text('(kicad_sch (rev "B"))')
    (board / "ControlBoard.kicad_pcb").write_text('(kicad_pcb (rev "B"))')
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "rev B"],
                   check=True, env=_git_env())
    subprocess.run(["git", "-C", str(repo), "tag", "hw-rev-b"], check=True)
    return repo


def _git_env():
    import os
    env = dict(os.environ)
    env.update({
        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
    })
    return env


@pytest.fixture
def docs_root(tmp_path, monkeypatch):
    """A fake docs repo root with Products.yaml + Descriptors.json."""
    root = tmp_path / "docs"
    (root / "Config").mkdir(parents=True)
    (root / "Config" / "Products.yaml").write_text(
        "product_line: openvvvf\n"
        "chassis:\n"
        "  Chassis2:\n"
        "    short_code: C2\n")
    (root / "Data" / "Parts").mkdir(parents=True)
    (root / "Data" / "Parts" / "Descriptors.json").write_text(json.dumps(
        {"Chassis2|pcb|controlboard": "CTRL"}))
    monkeypatch.setattr(core, "REPO_ROOT", root)
    return root


@pytest.fixture
def fake_kicad(monkeypatch):
    """Replace all kicad exports with dummy file writers."""
    def touch(out, suffix_ok=True):
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("dummy")
        return suffix_ok

    monkeypatch.setattr(core.kicad, "export_sch_pdf", lambda sch, out: touch(out))
    monkeypatch.setattr(core.kicad, "export_bom", lambda sch, out: touch(out))
    monkeypatch.setattr(core.kicad, "export_gerber_zip", lambda pcb, out: touch(out))
    monkeypatch.setattr(core.kicad, "run_drc", lambda pcb, out: touch(out) and 0)
    monkeypatch.setattr(core.kicad, "export_step", lambda pcb, out: touch(out))
    monkeypatch.setattr(core.kicad, "export_ibom", lambda pcb, out, gen: touch(out))
    monkeypatch.setattr(core.kicad, "find_ibom_generator", lambda roots: Path("/fake/gen.py"))
    monkeypatch.setattr(core, "fetch_tags", lambda repo: None)


def test_parse_rev(tmp_path):
    sch = tmp_path / "b.kicad_sch"
    sch.write_text('(kicad_sch (version 20221018) (rev "C"))')
    assert core.parse_rev(sch) == "C"
    sch.write_text("(kicad_sch (version 20221018))")
    assert core.parse_rev(sch) is None


def test_part_number():
    assert core.part_number("C2", "CTRL", "A") == "HW-C2-PCB-CTRL-A"


def test_find_boards(hw_repo, tmp_path):
    dest = tmp_path / "extract"
    dest.mkdir()
    assert core.archive_tag(hw_repo, "hw-rev-a", dest)
    boards = core.find_boards(dest / "Hardware")
    assert len(boards) == 1
    b = boards[0]
    assert (b.chassis, b.name, b.rev) == ("Chassis2", "ControlBoard", "A")
    assert [p.name for p in b.renders] == ["ControlBoard.png"]


def test_update_exports_each_revision_once(hw_repo, docs_root, fake_kicad):
    manifest_path = docs_root / "Data" / "Releases" / "manifest.json"
    rc = core.update(hw_repo, tag_pattern="hw-rev-*", manifest_path=manifest_path)
    assert rc == 0
    manifest = json.loads(manifest_path.read_text())
    assert set(manifest) == {"HW-C2-PCB-CTRL-A", "HW-C2-PCB-CTRL-B"}
    entry = manifest["HW-C2-PCB-CTRL-A"]
    assert entry["source_tag"] == "hw-rev-a"
    assert entry["artifacts"]["ibom"] == "ibom.html"
    assert entry["artifacts"]["renders"] == ["ControlBoard.png"]
    out = docs_root / entry["dir"]
    assert (out / "ibom.html").is_file()
    assert (out / "HW-C2-PCB-CTRL-A-schematic.pdf").is_file()
    assert (out / "HW-C2-PCB-CTRL-A-gerbers.zip").is_file()

    # second run: everything already exported, nothing changes
    before = manifest_path.read_text()
    rc = core.update(hw_repo, tag_pattern="hw-rev-*", manifest_path=manifest_path)
    assert rc == 0
    assert manifest_path.read_text() == before


def test_update_only_tag(hw_repo, docs_root, fake_kicad):
    manifest_path = docs_root / "Data" / "Releases" / "manifest.json"
    rc = core.update(hw_repo, only_tag="hw-rev-b", manifest_path=manifest_path)
    assert rc == 0
    manifest = json.loads(manifest_path.read_text())
    assert set(manifest) == {"HW-C2-PCB-CTRL-B"}


def test_update_no_tags(hw_repo, docs_root, fake_kicad):
    manifest_path = docs_root / "Data" / "Releases" / "manifest.json"
    rc = core.update(hw_repo, tag_pattern="nope-*", manifest_path=manifest_path)
    assert rc == 1


def test_show_and_list(hw_repo, docs_root, fake_kicad, capsys):
    manifest_path = docs_root / "Data" / "Releases" / "manifest.json"
    core.update(hw_repo, only_tag="hw-rev-a", manifest_path=manifest_path)
    assert core.show("HW-C2-PCB-CTRL-A", manifest_path) == 0
    out = capsys.readouterr().out
    assert "ControlBoard" in out
    assert core.show("HW-C2-PCB-NOPE-A", manifest_path) == 1
    assert core.list_boards(manifest_path) == 0
    out = capsys.readouterr().out
    assert "Rev A:" in out and "HW-C2-PCB-CTRL-A" in out


def test_build_viewer(hw_repo, docs_root, fake_kicad):
    from hwrelease import viewer

    manifest_path = docs_root / "Data" / "Releases" / "manifest.json"
    out_path = docs_root / "Docs" / "Tools" / "PCB-Tool" / "pcb-tool.html"
    core.update(hw_repo, only_tag="hw-rev-a", manifest_path=manifest_path)
    # update() already rebuilt the viewer; rebuild explicitly to check rc.
    assert viewer.build_viewer(manifest_path, out_path) == 0
    html = out_path.read_text()
    assert "HW-C2-PCB-CTRL-A" in html
    assert "PCB Tool" in html
    assert "Open Interactive Assembly" in html
    # empty manifest -> error
    assert viewer.build_viewer(docs_root / "nope.json", out_path) == 1
