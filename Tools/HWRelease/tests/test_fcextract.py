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
