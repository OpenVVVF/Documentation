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
