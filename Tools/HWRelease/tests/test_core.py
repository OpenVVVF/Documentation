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
    (board / "fab_spec.yaml").write_text(
        'options:\n  outer_copper: 2 oz\nnotes:\n  - "2 oz copper"\n')
    (repo / "Hardware" / "Chassis2" / "Boards" / "fab_defaults.yaml").write_text(
        'notes:\n  - "2D serial 10x10mm"\n')
    boms = repo / "Hardware" / "Chassis2" / "FabricationData" / "BOMs"
    (boms / "Variants" / "standard").mkdir(parents=True)
    (boms / "mouser_bom.csv").write_text("pn,qty\nX,1\n")
    (boms / "sendcutsend_bom.csv").write_text("part,qty\nY,2\n")
    (boms / "Variants" / "standard" / "mouser_bom.csv").write_text("pn,qty\nZ,3\n")
    (boms / "Variants" / "standard" / "Consolidated_BOM.csv").write_text(
        "Quantity,Order Qty,Pack Size,Leftover,Internal P/N,Description,"
        "Customer Part No.,Manufacturer Part No.,Vendor,Vendor P/N,Unit Price,Line Total\n"
        "1,1,,,X,M,PN,M,mouser,VP,10.00,10.00\n"
        "2,2,,,Y,N,PN,N,mcmaster,VP,2.50,5.00\n")
    (boms.parent / "Pricing_Report.md").write_text(
        "# Report\n**Mouser subtotal:** $12.34\n"
        "**McMaster-Carr subtotal:** $5.00\n"
        "## Grand Total (1 unit): **$17.34**\n")
    mech = repo / "Hardware" / "Chassis2" / "Mechanical" / "Fab" / "HW-C2-DCLBB-A"
    mech.mkdir(parents=True)
    (mech / "info.txt").write_text("PartName=HW-C2-DCLBB-A\nMaterial=Copper\nUnitPrice=45.12\n")
    (mech / "info.png").write_bytes(b"png")
    (mech / "HW-C2-DCLBB-A.step").write_text("step")
    (mech / "HW-C2-DCLBB-A.stl").write_text("stl")
    (mech / "fab_spec.yaml").write_text(
        'process: laser_cut\nmaterial: "Copper C110"\nservices:\n  bending: true\n')
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
    monkeypatch.setattr(core, "regenerate_vendor_boms", lambda hw: {"standard": "2,241.19"})


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


def test_export_chassis_boms_copies_build_variants(tmp_path):
    """FabricationData/Builds/ + Variant_Comparison.md + variants.json ride along."""
    fab = tmp_path / "Chassis2" / "FabricationData"
    boms = fab / "BOMs"
    boms.mkdir(parents=True)
    (boms / "mouser_bom.csv").write_text("pn,qty\nX,1\n")
    build = fab / "Builds" / "450v" / "BOMs"
    build.mkdir(parents=True)
    (build / "mouser_bom.csv").write_text("pn,qty\nY,60\n")
    (fab / "Variant_Comparison.md").write_text("# comparison\n")
    (fab / "variants.json").write_text(json.dumps({
        "chassis": "Chassis2", "default": "200v",
        "variants": [{"name": "200v"}, {"name": "450v"}]}))
    out = tmp_path / "out"
    artifacts = core.export_chassis_boms(tmp_path / "Chassis2", out)
    assert (out / "Builds" / "450v" / "BOMs" / "mouser_bom.csv").is_file()
    assert (out / "Variant_Comparison.md").is_file()
    assert (out / "variants.json").is_file()
    assert artifacts["variant_comparison"] == "Variant_Comparison.md"
    assert artifacts["variants_manifest"] == "variants.json"
    assert artifacts["build_variants"] == ["200v", "450v"]


def test_update_exports_each_revision_once(hw_repo, docs_root, fake_kicad):
    manifest_path = docs_root / "Data" / "Releases" / "manifest.json"
    rc = core.update(hw_repo, tag_pattern="hw-rev-*", manifest_path=manifest_path)
    assert rc == 0
    manifest = json.loads(manifest_path.read_text())
    assert set(manifest) == {"HW-C2-PCB-CTRL-A", "HW-C2-PCB-CTRL-B",
                             "CHASSIS-C2-A", "CHASSIS-C2-B", "HW-C2-DCLBB-A"}
    mech = manifest["HW-C2-DCLBB-A"]
    assert mech["mech"] is True
    assert mech["artifacts"]["info_fields"]["Material"] == "Copper"
    assert mech["artifacts"]["fab_spec"]["process"] == "laser_cut"
    assert mech["artifacts"]["fab_spec"]["services"]["bending"] is True
    assert mech["artifacts"]["stl"] == "HW-C2-DCLBB-A.stl"
    assert (docs_root / mech["dir"] / "HW-C2-DCLBB-A.step").is_file()

    # mech pruning: delete the part from the tree, retag, re-export
    import subprocess as sp
    import shutil as sh
    sp.run(["git", "-C", str(hw_repo), "rm", "-rq",
            "Hardware/Chassis2/Mechanical/Fab/HW-C2-DCLBB-A"], check=True)
    sp.run(["git", "-C", str(hw_repo), "commit", "-q", "-m", "remove part"],
           check=True, env=_git_env())
    sp.run(["git", "-C", str(hw_repo), "tag", "-f", "hw-rev-a"], check=True)
    rc = core.update(hw_repo, only_tag="hw-rev-a", force=True,
                     manifest_path=manifest_path)
    assert rc == 0
    manifest = json.loads(manifest_path.read_text())
    assert "HW-C2-DCLBB-A" not in manifest
    chassis = manifest["CHASSIS-C2-A"]
    assert chassis["artifacts"]["vendor_boms"]["mouser"] == "BOMs/mouser_bom.csv"
    assert chassis["artifacts"]["vendor_boms"]["sendcutsend"] == "BOMs/sendcutsend_bom.csv"
    assert chassis["artifacts"]["variants"]["standard"]["mouser"] == "BOMs/Variants/standard/mouser_bom.csv"
    assert (docs_root / chassis["dir"] / "BOMs" / "mouser_bom.csv").is_file()
    est = chassis["artifacts"]["price_estimate"]
    assert est["total"] == "17.34" and est["vendors"]["Mouser"] == "12.34"
    assert est["variants"] == {"standard": "2,241.19"}
    assert est["variant_vendors"]["standard"] == {"mcmaster": "5.00", "mouser": "10.00"}
    entry = manifest["HW-C2-PCB-CTRL-A"]
    assert entry["artifacts"]["fab_spec"] == {
        "options": {"outer_copper": "2 oz"},
        "notes": ["2 oz copper"],
        "default_notes": ["2D serial 10x10mm"],
    }
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
    assert set(manifest) == {"HW-C2-PCB-CTRL-B", "CHASSIS-C2-B", "HW-C2-DCLBB-A"}


def test_update_chassis_tag_pins_rev_for_mech_only_release(hw_repo, docs_root,
                                                           fake_kicad):
    """A chassis-named tag (C2-B) pins the chassis rev even when no board
    rev changed, so a mechanical-only release publishes as a new chassis rev,
    and other chassis are not exported from that tag."""
    import subprocess as sp
    # give the repo a second chassis with mech content
    c3 = hw_repo / "Hardware" / "Chassis3" / "Mechanical" / "Fab" / "HW-C3-PBB-A"
    c3.mkdir(parents=True)
    (c3 / "info.txt").write_text("PartName=HW-C3-PBB-A\n")
    (c3 / "HW-C3-PBB-A.step").write_text("step")
    sp.run(["git", "-C", str(hw_repo), "add", "."], check=True)
    sp.run(["git", "-C", str(hw_repo), "commit", "-q", "-m", "c3 mech"],
           check=True, env=_git_env())
    # register Chassis3 in the products config so it is exportable
    products = docs_root / "Config" / "Products.yaml"
    products.write_text(products.read_text() +
                        "  Chassis3:\n    short_code: C3\n")
    sp.run(["git", "-C", str(hw_repo), "tag", "C2-B"], check=True)
    manifest_path = docs_root / "Data" / "Releases" / "manifest.json"
    rc = core.update(hw_repo, only_tag="C2-B", manifest_path=manifest_path)
    assert rc == 0
    manifest = json.loads(manifest_path.read_text())
    assert manifest["CHASSIS-C2-B"]["rev"] == "B"
    assert manifest["CHASSIS-C2-B"]["source_tag"] == "C2-B"
    # boards unchanged by the tag: rev comes from the KiCad files as usual
    assert manifest["HW-C2-PCB-CTRL-B"]["rev"] == "B"
    # the tag names C2: Chassis3 content is not exported from it
    assert not any(k.startswith("CHASSIS-C3") or k.startswith("HW-C3")
                   for k in manifest)


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
    bom_html = (out_path.parent.parent / "BOM-Tool" / "bom-tool.html").read_text()
    assert "BOM Tool" in bom_html
    assert "CHASSIS-C2-A" in bom_html
    assert "Mouser" in bom_html
    # mech card material priority: fab_spec > extracted material.json > info.txt
    assert "spec.material || a.material || f.Material" in bom_html
    # empty manifest -> error
    assert viewer.build_viewer(docs_root / "nope.json", out_path) == 1


@pytest.fixture
def hw_repo_mech_only(tmp_path):
    """A hardware repo whose only content is a Chassis3 FreeCAD model."""
    repo = tmp_path / "InverterGen5"
    mech = repo / "Hardware" / "Chassis3" / "Mechanical"
    mech.mkdir(parents=True)
    (mech / "InverterMechanical.FCStd").write_bytes(b"fcstd")
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "mech"],
                   check=True, env=_git_env())
    subprocess.run(["git", "-C", str(repo), "tag", "hw-c3"], check=True)
    return repo


@pytest.fixture
def docs_root_c3(tmp_path, monkeypatch):
    """A fake docs repo root registering Chassis3 (short code C3)."""
    root = tmp_path / "docs"
    (root / "Config").mkdir(parents=True)
    (root / "Config" / "Products.yaml").write_text(
        "product_line: openvvvf\n"
        "chassis:\n"
        "  Chassis3:\n"
        "    short_code: C3\n")
    (root / "Data" / "Parts").mkdir(parents=True)
    (root / "Data" / "Parts" / "Descriptors.json").write_text("{}")
    monkeypatch.setattr(core, "REPO_ROOT", root)
    return root


def _fake_extract(chassis_dir):
    """Stand-in for extract_parts: drop one fabricated part into Fab/."""
    part = chassis_dir / "Mechanical" / "Fab" / "HW-C3-PBB-A"
    part.mkdir(parents=True, exist_ok=True)
    (part / "HW-C3-PBB-A.step").write_text("step")
    (part / "info.txt").write_text("Material=Copper\n")
    (part / "material.json").write_text(
        json.dumps({"material": "Copper C110"}))
    return ["HW-C3-PBB-A"]


def test_update_boardless_chassis(hw_repo_mech_only, docs_root_c3, fake_kicad,
                                  monkeypatch):
    """A chassis with no boards but mech content still gets a CHASSIS entry
    plus mech entries."""
    from hwrelease import fcextract
    monkeypatch.setattr(fcextract, "extract_parts", _fake_extract)
    manifest_path = docs_root_c3 / "Data" / "Releases" / "manifest.json"
    rc = core.update(hw_repo_mech_only, tag_pattern="hw-*",
                     manifest_path=manifest_path)
    assert rc == 0
    manifest = json.loads(manifest_path.read_text())
    assert set(manifest) == {"CHASSIS-C3-hw-c3", "HW-C3-PBB-A"}
    entry = manifest["CHASSIS-C3-hw-c3"]  # rev falls back to the tag
    assert entry["chassis"] == "C3"
    # boardless chassis: no vendor BOMs, no variant price totals
    assert "vendor_boms" not in entry["artifacts"]
    assert "price_estimate" not in entry["artifacts"]
    mech = manifest["HW-C3-PBB-A"]
    assert mech["mech"] is True
    assert mech["chassis"] == "C3"
    assert mech["artifacts"]["info_fields"]["Material"] == "Copper"
    assert mech["artifacts"]["material"] == "Copper C110"
    assert (docs_root_c3 / mech["dir"] / "HW-C3-PBB-A.step").is_file()
    assert (docs_root_c3 / mech["dir"] / "material.json").is_file()


def test_update_boardless_chassis_no_content(hw_repo_mech_only, docs_root_c3,
                                             fake_kicad, monkeypatch):
    """FCStd present but extraction yields nothing -> no entry, clean skip."""
    from hwrelease import fcextract
    monkeypatch.setattr(fcextract, "extract_parts", lambda d: [])
    manifest_path = docs_root_c3 / "Data" / "Releases" / "manifest.json"
    rc = core.update(hw_repo_mech_only, tag_pattern="hw-*",
                     manifest_path=manifest_path)
    assert rc == 0
    # skipped before the manifest is ever written
    assert not manifest_path.exists() \
        or json.loads(manifest_path.read_text()) == {}


def test_update_no_boards_no_mech(hw_repo_mech_only, docs_root_c3, fake_kicad):
    """A tag with neither boards nor mechanical content is skipped early."""
    (hw_repo_mech_only / "Hardware" / "Chassis3" / "Mechanical"
     / "InverterMechanical.FCStd").unlink()
    subprocess.run(["git", "-C", str(hw_repo_mech_only), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(hw_repo_mech_only), "commit", "-q",
                    "-m", "drop model"], check=True, env=_git_env())
    subprocess.run(["git", "-C", str(hw_repo_mech_only), "tag", "-f", "hw-c3"],
                   check=True)
    manifest_path = docs_root_c3 / "Data" / "Releases" / "manifest.json"
    rc = core.update(hw_repo_mech_only, tag_pattern="hw-*",
                     manifest_path=manifest_path)
    assert rc == 0
    # skipped before the manifest is ever written
    assert not manifest_path.exists() \
        or json.loads(manifest_path.read_text()) == {}
