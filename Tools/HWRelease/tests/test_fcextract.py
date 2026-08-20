"""Tests for the FreeCAD-extraction helpers (no FreeCAD needed)."""

import json

from hwrelease import fcextract


def test_spec_diameters_mm():
    assert fcextract.spec_diameters_mm('all 0.1968" (5.0 mm) holes') == [5.0]
    assert fcextract.spec_diameters_mm("⌀5.5 mm holes on top") == [5.5]
    assert fcextract.spec_diameters_mm("no diameters here") == []


def test_check_spec_holes(tmp_path):
    holes = tmp_path / "holes.json"
    holes.write_text(json.dumps({"5.5": 4, "6.0": 6}))
    spec = {"services": {"countersinking": [
        {"for": "82 deg", "holes": 'all 0.2166" (5.5 mm) holes'}]}}
    assert fcextract.check_spec_holes("PN", spec, holes) == []
    spec_bad = {"services": {"tapping": [
        {"thread": "M8", "holes": 'all 0.2756" (7.0 mm) holes'}]}}
    warnings = fcextract.check_spec_holes("PN", spec_bad, holes)
    assert len(warnings) == 1 and "M8" in warnings[0]
    # no spec / no holes.json -> no warnings
    assert fcextract.check_spec_holes("PN", None, holes) == []
    assert fcextract.check_spec_holes("PN", spec, tmp_path / "nope.json") == []


def test_check_mcmaster(tmp_path):
    fab = tmp_path / "Mechanical" / "Fab"
    fab.mkdir(parents=True)
    (fab / "mcmaster_model.json").write_text(json.dumps({
        "91292A134": {"qty": 18, "description": "screw"},
        "98044A224": {"qty": 25, "description": "washer"},
    }))
    (tmp_path / "Mechanical" / "MechanicalBOM.txt").write_text(
        "Qty,Vendor,PN,Description\n"
        "18,McMaster,91292A134,\n"
        "6,McMaster,94669A190,\n")
    warnings = fcextract.check_mcmaster(tmp_path)
    assert any("98044A224" in w and "missing" in w for w in warnings)
    assert any("94669A190" in w and "not found" in w for w in warnings)
    assert not any("91292A134" in w for w in warnings)
    assert fcextract.check_mcmaster(tmp_path / "nope") == []


def test_check_part_qty(tmp_path):
    fab = tmp_path / "Mechanical" / "Fab"
    (fab / "HW-C2-PBB-A").mkdir(parents=True)
    (fab / "model_parts.json").write_text(json.dumps({"HW-C2-PBB-A": 3}))
    (fab / "HW-C2-PBB-A" / "info.txt").write_text("Qty=3\n")
    assert fcextract.check_part_qty(tmp_path) == []
    (fab / "HW-C2-PBB-A" / "info.txt").write_text("Qty=2\n")
    warnings = fcextract.check_part_qty(tmp_path)
    assert len(warnings) == 1 and "PBB" in warnings[0]


def test_merge_mcmaster(tmp_path):
    mech = tmp_path / "Mechanical"
    (mech / "Fab").mkdir(parents=True)
    (mech / "Fab" / "mcmaster_model.json").write_text(json.dumps({
        "91292A134": {"qty": 18, "description": "screw"},
        "6926K352": {"qty": 8, "description": "nut"},
    }))
    bom = mech / "MechanicalBOM.txt"
    bom.write_text("Qty,Vendor,PN,Description\n"
                   "6,McMaster,91292A134,\n"
                   "1,McMaster,1821A55,Dielectric grease\n"
                   "3,Mouser,CM600DY-24T,IGBT module\n")
    notes = fcextract.merge_mcmaster(tmp_path)
    text = bom.read_text()
    assert "18,McMaster,91292A134," in text
    assert "8,McMaster,6926K352,nut" in text
    assert "1,McMaster,1821A55,Dielectric grease" in text
    assert "3,Mouser,CM600DY-24T" in text
    assert any("qty 6 -> 18" in n for n in notes)
    assert any("added 8x" in n for n in notes)


def test_export_assembly_no_fcstd(tmp_path):
    assert fcextract.export_assembly(tmp_path) is False


def test_export_assembly_flatpak_missing(tmp_path, monkeypatch, capsys):
    mech = tmp_path / "Mechanical"
    mech.mkdir()
    (mech / "m.FCStd").write_bytes(b"x")
    monkeypatch.setattr(fcextract, "_freecad", lambda args, **kw: None)
    assert fcextract.export_assembly(tmp_path) is False
    assert "freecad flatpak not found" in capsys.readouterr().err


def test_export_assembly_failure(tmp_path, monkeypatch, capsys):
    import subprocess
    mech = tmp_path / "Mechanical"
    mech.mkdir()
    (mech / "m.FCStd").write_bytes(b"x")
    monkeypatch.setattr(fcextract, "_freecad",
                        lambda args, **kw: subprocess.CompletedProcess(
                            args, 1, "", "boom"))
    assert fcextract.export_assembly(tmp_path) is False
    assert "assembly export failed" in capsys.readouterr().err


def test_export_assembly_success(tmp_path, monkeypatch):
    import subprocess
    from pathlib import Path
    mech = tmp_path / "Mechanical"
    mech.mkdir()
    (mech / "m.FCStd").write_bytes(b"x")

    def fake_freecad(args, **kw):
        Path(args[2]).write_text("step")
        Path(args[3]).write_text("stl")
        return subprocess.CompletedProcess(args, 0, "ASSEMBLY_OK", "")

    monkeypatch.setattr(fcextract, "_freecad", fake_freecad)
    assert fcextract.export_assembly(tmp_path) is True
    assert (mech / "assembly.step").is_file()
    assert (mech / "assembly.stl").is_file()


def _mk_fcstd(tmp_path):
    mech = tmp_path / "Mechanical"
    mech.mkdir()
    (mech / "m.FCStd").write_bytes(b"x")
    return mech


def test_export_assembly_timeout_no_stl(tmp_path, monkeypatch, capsys):
    import subprocess
    _mk_fcstd(tmp_path)

    def raise_timeout(args, **kw):
        raise subprocess.TimeoutExpired(args, kw.get("timeout"))

    monkeypatch.setattr(fcextract, "_freecad", raise_timeout)
    assert fcextract.export_assembly(tmp_path) is False
    err = capsys.readouterr().err
    assert "timed out" in err
    assert not (tmp_path / "Mechanical" / "assembly.stl").exists()


def test_export_assembly_timeout_keeps_stl(tmp_path, monkeypatch, capsys):
    import subprocess
    from pathlib import Path
    mech = _mk_fcstd(tmp_path)

    def slow_step(args, **kw):
        # STL (fast) is written before the STEP export hangs.
        Path(args[3]).write_text("stl")
        raise subprocess.TimeoutExpired(args, kw.get("timeout"))

    monkeypatch.setattr(fcextract, "_freecad", slow_step)
    assert fcextract.export_assembly(tmp_path) is True
    assert (mech / "assembly.stl").is_file()
    assert not (mech / "assembly.step").exists()
    assert "keeping STL only" in capsys.readouterr().err


def test_extract_parts_timeout(tmp_path, monkeypatch, capsys):
    import subprocess
    _mk_fcstd(tmp_path)

    def raise_timeout(args, **kw):
        raise subprocess.TimeoutExpired(args, kw.get("timeout"))

    monkeypatch.setattr(fcextract, "_freecad", raise_timeout)
    assert fcextract.extract_parts(tmp_path) == []
    assert "timed out" in capsys.readouterr().err
