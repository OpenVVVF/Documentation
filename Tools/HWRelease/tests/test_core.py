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
    (boms.parent / "Subassembly_Pricing.json").write_text(json.dumps({
        "chassis": "Chassis2", "variant": "base", "qty": 1,
        "subassemblies": {}, "total": "17.34", "unpriced": 0}))
    (boms / "Variants" / "standard" / "Subassembly_Pricing.json").write_text(
        json.dumps({"chassis": "Chassis2", "variant": "standard", "qty": 1,
                    "subassemblies": {}, "total": "18.50", "unpriced": 0}))
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
    monkeypatch.setattr(core, "regenerate_vendor_boms",
                        lambda hw: {"Chassis2": {"standard": "2,241.19"}})


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
    (build.parent / "Subassembly_Pricing.json").write_text(json.dumps({
        "chassis": "Chassis2", "variant": "450v", "qty": 1,
        "subassemblies": {}, "total": "99.00", "unpriced": 0}))
    # The hardware repo's per-build .gitignore must not ride along: this repo
    # commits Data/Releases/ wholesale.
    (fab / "Builds" / "450v" / ".gitignore").write_text("*\n!Pricing_Report.md\n")
    (fab / "Variant_Comparison.md").write_text("# comparison\n")
    (fab / "variants.json").write_text(json.dumps({
        "chassis": "Chassis2", "default": "200v",
        "variants": [{"name": "200v"}, {"name": "450v"}]}))
    out = tmp_path / "out"
    artifacts = core.export_chassis_boms(tmp_path / "Chassis2", out)
    assert (out / "Builds" / "450v" / "BOMs" / "mouser_bom.csv").is_file()
    assert not (out / "Builds" / "450v" / ".gitignore").exists()
    assert (out / "Variant_Comparison.md").is_file()
    assert (out / "variants.json").is_file()
    assert artifacts["variant_comparison"] == "Variant_Comparison.md"
    assert artifacts["variants_manifest"] == "variants.json"
    assert artifacts["build_variants"] == ["200v", "450v"]
    # The build's pricing JSON rides along, copied next to the build's own
    # Consolidated_BOM.csv (base JSON absent here -> no "base" key).
    assert artifacts["subassembly_pricing"] == {
        "builds": {"450v": "Builds/450v/BOMs/Subassembly_Pricing.json"}}
    assert (out / "Builds" / "450v" / "BOMs" / "Subassembly_Pricing.json").is_file()


def test_export_chassis_boms_copies_subassembly_pricing(tmp_path):
    """Base/tier pricing JSONs land beside their Consolidated_BOM.csv copies."""
    fab = tmp_path / "Chassis2" / "FabricationData"
    variants = fab / "BOMs" / "Variants" / "standard"
    variants.mkdir(parents=True)
    (fab / "BOMs" / "Consolidated_BOM.csv").write_text("h\n")
    (variants / "Consolidated_BOM.csv").write_text("h\n")
    base_doc = {"chassis": "Chassis2", "variant": "base", "qty": 1,
                "subassemblies": {"gate-driver": {"name": "Gate Driver",
                "total": "10.00", "vendors": {"mouser": "10.00"}, "lines": []}},
                "total": "42.00", "unpriced": 1}
    (fab / "Subassembly_Pricing.json").write_text(json.dumps(base_doc))
    (variants / "Subassembly_Pricing.json").write_text(json.dumps(base_doc))
    out = tmp_path / "out"
    artifacts = core.export_chassis_boms(tmp_path / "Chassis2", out)
    assert artifacts["subassembly_pricing"] == {
        "base": "BOMs/Subassembly_Pricing.json",
        "tiers": {"standard": "BOMs/Variants/standard/Subassembly_Pricing.json"},
    }
    assert (out / "BOMs" / "Subassembly_Pricing.json").is_file()
    assert (out / "BOMs" / "Variants" / "standard"
            / "Subassembly_Pricing.json").is_file()
    # Old releases predating the JSON: absent-tolerant, no key at all
    out2 = tmp_path / "out2"
    (fab / "Subassembly_Pricing.json").unlink()
    (variants / "Subassembly_Pricing.json").unlink()
    artifacts = core.export_chassis_boms(tmp_path / "Chassis2", out2)
    assert "subassembly_pricing" not in artifacts
    assert not (out2 / "BOMs" / "Subassembly_Pricing.json").exists()


def test_pricing_totals_reads_subassembly_json(tmp_path):
    """Totals come from the generated Subassembly_Pricing.json files (money
    strings have no separators in the JSON, gain them for the manifest)."""
    fab = tmp_path / "FabricationData"
    std = fab / "BOMs" / "Variants" / "standard"
    std.mkdir(parents=True)
    (fab / "Subassembly_Pricing.json").write_text(json.dumps({
        "chassis": "Chassis2", "variant": "base", "qty": 1,
        "subassemblies": {}, "total": "2397.20", "unpriced": 0}))
    (std / "Subassembly_Pricing.json").write_text(json.dumps({
        "chassis": "Chassis2", "variant": "standard", "qty": 1,
        "subassemblies": {}, "total": "2450.86", "unpriced": 0}))
    assert core._pricing_totals(fab) == {"base": "2,397.20",
                                         "standard": "2,450.86"}


def test_scrape_variant_totals_matches_generate_output():
    """Lock the stdout fallback to the print format of bom_manager's
    generate.write_variant_outputs ("Spares variants (N unit[s]): bare
    minimum $X" then "<tier> $X (+$Y)  -> BOMs/Variants/<tier>")."""
    output = (
        "No vendor API keys configured; using cached/manual prices only.\n"
        "Discovered 3 BOM sources.\n"
        "\n=== Chassis2 (C2) ===\n"
        "Consolidated to 42 unique BOM lines.\n"
        "  Wrote BOMs/Consolidated_BOM.csv\n"
        "\n  Spares variants (1 unit): bare minimum $2,397.20\n"
        "  standard   $2,450.86 (+$53.66)  -> BOMs/Variants/standard\n"
        "  generous   $2,775.55 (+$378.35)  -> BOMs/Variants/generous\n"
        "Done.\n"
    )
    assert core._scrape_variant_totals(output) == {
        "Chassis2": {"base": "2,397.20", "standard": "2,450.86",
                     "generous": "2,775.55"}}


def test_scrape_variant_totals_is_per_chassis():
    """Regression: the old global scrape conflated '=== Chassis ===' sections,
    so a chassis could record its neighbour's totals (the manifest's
    price_estimate.variants zeros). Totals must stay in their own section."""
    output = (
        "\n=== Chassis1 (C1) ===\n"
        "  Spares variants (2 units): bare minimum $0.00\n"
        "  standard   $0.00 (+$0.00)  -> BOMs/Variants/standard\n"
        "\n=== Chassis2 (C2) ===\n"
        "  Spares variants (2 units): bare minimum $4,794.40\n"
        "  standard   $4,901.72 (+$107.32)  -> BOMs/Variants/standard\n"
    )
    totals = core._scrape_variant_totals(output)
    assert totals["Chassis1"] == {"base": "0.00", "standard": "0.00"}
    assert totals["Chassis2"] == {"base": "4,794.40", "standard": "4,901.72"}


def test_update_exports_each_revision_once(hw_repo, docs_root, fake_kicad):
    manifest_path = docs_root / "Data" / "Releases" / "manifest.json"
    rc = core.update(hw_repo, tag_pattern="hw-rev-*", manifest_path=manifest_path)
    assert rc == 0
    manifest = json.loads(manifest_path.read_text())
    assert set(manifest) == {"HW-C2-PCB-CTRL-A", "HW-C2-PCB-CTRL-B",
                             "CHASSIS-C2-A", "CHASSIS-C2-B", "HW-C2-DCLBB-A",
                             "HW-C2-DCLBB-A--C2-B"}
    mech = manifest["HW-C2-DCLBB-A"]
    assert mech["mech"] is True
    assert mech["rev"] == "A"
    assert mech["artifacts"]["info_fields"]["Material"] == "Copper"
    assert mech["artifacts"]["fab_spec"]["process"] == "laser_cut"
    assert mech["artifacts"]["fab_spec"]["services"]["bending"] is True
    assert mech["artifacts"]["stl"] == "HW-C2-DCLBB-A.stl"
    assert (docs_root / mech["dir"] / "HW-C2-DCLBB-A.step").is_file()
    # the same part under rev B rides along as a composite key, not a clobber
    mech_b = manifest["HW-C2-DCLBB-A--C2-B"]
    assert (mech_b["mech"], mech_b["chassis"], mech_b["rev"]) == (True, "C2", "B")
    assert mech_b["part_number"] == "HW-C2-DCLBB-A"
    assert mech_b["dir"] == "Data/Releases/C2/B/Mech/HW-C2-DCLBB-A"
    assert mech_b["artifacts"]["stl"] == "HW-C2-DCLBB-A.stl"

    # mech pruning: delete the part from the tree, retag hw-rev-b (a rev-B
    # release: the board files move only forward in this fixture), re-export;
    # only that release's entry goes away — rev A's entry survives untouched
    import subprocess as sp
    import shutil as sh
    sp.run(["git", "-C", str(hw_repo), "rm", "-rq",
            "Hardware/Chassis2/Mechanical/Fab/HW-C2-DCLBB-A"], check=True)
    sp.run(["git", "-C", str(hw_repo), "commit", "-q", "-m", "remove part"],
           check=True, env=_git_env())
    sp.run(["git", "-C", str(hw_repo), "tag", "-f", "hw-rev-b"], check=True)
    rc = core.update(hw_repo, only_tag="hw-rev-b", force=True,
                     manifest_path=manifest_path)
    assert rc == 0
    manifest = json.loads(manifest_path.read_text())
    assert "HW-C2-DCLBB-A--C2-B" not in manifest
    assert manifest["HW-C2-DCLBB-A"]["rev"] == "A"
    assert (docs_root / "Data/Releases/C2/A/Mech/HW-C2-DCLBB-A").is_dir()
    assert not (docs_root / "Data/Releases/C2/B/Mech/HW-C2-DCLBB-A").exists()
    chassis = manifest["CHASSIS-C2-B"]
    assert chassis["artifacts"]["vendor_boms"]["mouser"] == "BOMs/mouser_bom.csv"
    assert chassis["artifacts"]["vendor_boms"]["sendcutsend"] == "BOMs/sendcutsend_bom.csv"
    assert chassis["artifacts"]["variants"]["standard"]["mouser"] == "BOMs/Variants/standard/mouser_bom.csv"
    assert (docs_root / chassis["dir"] / "BOMs" / "mouser_bom.csv").is_file()
    est = chassis["artifacts"]["price_estimate"]
    assert est["total"] == "17.34" and est["vendors"]["Mouser"] == "12.34"
    assert est["variants"] == {"standard": "2,241.19"}
    assert est["variant_vendors"]["standard"] == {"mcmaster": "5.00", "mouser": "10.00"}
    pricing = chassis["artifacts"]["subassembly_pricing"]
    assert pricing["base"] == "BOMs/Subassembly_Pricing.json"
    assert pricing["tiers"] == {
        "standard": "BOMs/Variants/standard/Subassembly_Pricing.json"}
    base_pricing = docs_root / chassis["dir"] / "BOMs" / "Subassembly_Pricing.json"
    assert json.loads(base_pricing.read_text())["total"] == "17.34"
    tier_pricing = (docs_root / chassis["dir"] / "BOMs" / "Variants"
                    / "standard" / "Subassembly_Pricing.json")
    assert json.loads(tier_pricing.read_text())["total"] == "18.50"
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


def test_mech_manifest_key():
    """Bare pn while free; composite once another release holds the bare key."""
    m = {}
    assert core.mech_manifest_key("HW-C2-X-A", "C2", "A", m) == "HW-C2-X-A"
    m["HW-C2-X-A"] = {"mech": True, "part_number": "HW-C2-X-A",
                      "chassis": "C2", "rev": "A"}
    # same release re-export reuses the bare key ...
    assert core.mech_manifest_key("HW-C2-X-A", "C2", "A", m) == "HW-C2-X-A"
    # ... another release gets a composite
    assert core.mech_manifest_key("HW-C2-X-A", "C2", "B", m) == "HW-C2-X-A--C2-B"
    m["HW-C2-X-A--C2-B"] = {"mech": True, "part_number": "HW-C2-X-A",
                            "chassis": "C2", "rev": "B"}
    # and re-exporting it reuses the composite
    assert core.mech_manifest_key("HW-C2-X-A", "C2", "B", m) == "HW-C2-X-A--C2-B"


def _write_mech_tree(releases: Path, short: str, rev: str, pn: str) -> Path:
    part_dir = releases / short / rev / "Mech" / pn
    part_dir.mkdir(parents=True)
    (part_dir / f"{pn}.step").write_text("step")
    (part_dir / f"{pn}.stl").write_text("stl")
    (part_dir / "info.png").write_bytes(b"png")
    (part_dir / "info.txt").write_text(f"PartName={pn}\nUnitPrice=12.34\n")
    (part_dir / "holes.json").write_text("{}")
    (part_dir / "material.json").write_text(json.dumps({"material": "Copper C110"}))
    return part_dir


def test_migrate_mech_rebuilds_per_release_entries(tmp_path):
    """Bare-key leftovers become one entry per <chassis>/<rev>/Mech/<pn> dir,
    templated from the old entry, artifacts re-read from disk."""
    releases = tmp_path / "Data" / "Releases"
    manifest_path = releases / "manifest.json"
    releases.mkdir(parents=True)
    template = {
        "mech": True, "part_number": "HW-C2-BSP-A",
        "chassis": "C2-DCDC", "rev": "A", "source_tag": "C2-DCDC-A",
        "generated": "2026-09-05T23:23:43+00:00",
        "dir": "Data/Releases/C2-DCDC/A/Mech/HW-C2-BSP-A",
        "source_url": "https://github.com/ex/hw/tree/C2-DCDC-A",
        "artifacts": {"fab_spec": {"process": "laser_cut"},
                      "info_fields": {"PartName": "HW-C2-BSP-A", "Notes": "stale"},
                      "material": "stale-material"},
    }
    core.save_manifest({"HW-C2-BSP-A": template,
                        "CHASSIS-C2-A": {"chassis": "C2", "rev": "A"}},
                       manifest_path)
    _write_mech_tree(releases, "C2", "A", "HW-C2-CHSP-A")  # unique -> bare key
    b_dir = _write_mech_tree(releases, "C2", "B", "HW-C2-BSP-A")
    (b_dir / "C2-HW-BSP-A.step").write_text("stray")  # legacy mis-named import
    _write_mech_tree(releases, "C2", "C", "HW-C2-BSP-A")
    _write_mech_tree(releases, "C2-DCDC", "A", "HW-C2-BSP-A")

    assert core.migrate_mech(manifest_path) == 0
    m = core.load_manifest(manifest_path)
    assert "CHASSIS-C2-A" in m  # non-mech entries untouched
    assert "HW-C2-BSP-A" not in m  # supersedes bare key: part is in 3 trees
    assert m["HW-C2-CHSP-A"]["chassis"] == "C2"  # unique part keeps bare key
    for rev in ("B", "C"):
        e = m[f"HW-C2-BSP-A--C2-{rev}"]
        assert (e["chassis"], e["rev"], e["source_tag"]) == ("C2", rev, f"C2-{rev}")
        assert e["dir"] == f"Data/Releases/C2/{rev}/Mech/HW-C2-BSP-A"
        assert e["artifacts"]["step"] == "HW-C2-BSP-A.step"
        assert e["artifacts"]["stl"] == "HW-C2-BSP-A.stl"
        assert e["artifacts"]["image"] == "info.png"
        assert e["artifacts"]["holes"] == "holes.json"
        # disk wins for info/material; fab_spec survives from the template
        assert e["artifacts"]["info_fields"]["UnitPrice"] == "12.34"
        assert e["artifacts"]["material"] == "Copper C110"
        assert e["artifacts"]["fab_spec"] == {"process": "laser_cut"}
        assert e["generated"] == template["generated"]
        assert e["source_url"] == f"https://github.com/ex/hw/tree/C2-{rev}"
    fam = m["HW-C2-BSP-A--C2-DCDC-A"]
    assert fam["chassis"] == "C2-DCDC"
    assert fam["source_tag"] == "C2-DCDC-A"  # rev "A" prefixed with short code
    assert fam["source_url"] == "https://github.com/ex/hw/tree/C2-DCDC-A"
    assert not (b_dir / "C2-HW-BSP-A.step").exists()  # stray removed

    # second half of the round trip: a release tree vanishes -> entry dropped
    import shutil
    shutil.rmtree(releases / "C2" / "B")
    assert core.migrate_mech(manifest_path) == 0
    m = core.load_manifest(manifest_path)
    assert "HW-C2-BSP-A--C2-B" not in m
    assert "HW-C2-BSP-A--C2-C" in m and "HW-C2-BSP-A--C2-DCDC-A" in m


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


def test_update_release_family_tag(hw_repo, docs_root, fake_kicad):
    """A release-family tag (C2-DCDC-A) publishes the family's chassis tree
    under the family's own short code and rev, and does not leak other
    chassis (Chassis3) that happen to have content at that tag."""
    import subprocess as sp
    # give the repo a second chassis with mech content
    c3 = hw_repo / "Hardware" / "Chassis3" / "Mechanical" / "Fab" / "HW-C3-PBB-A"
    c3.mkdir(parents=True)
    (c3 / "info.txt").write_text("PartName=HW-C3-PBB-A\n")
    (c3 / "HW-C3-PBB-A.step").write_text("step")
    sp.run(["git", "-C", str(hw_repo), "add", "."], check=True)
    sp.run(["git", "-C", str(hw_repo), "commit", "-q", "-m", "c3 mech"],
           check=True, env=_git_env())
    # register Chassis3 and the C2-DCDC release family (from Chassis2)
    products = docs_root / "Config" / "Products.yaml"
    products.write_text(products.read_text() +
                        "  Chassis3:\n    short_code: C3\n"
                        "release_families:\n"
                        "  C2-DCDC:\n    chassis: Chassis2\n")
    sp.run(["git", "-C", str(hw_repo), "tag", "C2-DCDC-A"], check=True)
    manifest_path = docs_root / "Data" / "Releases" / "manifest.json"
    rc = core.update(hw_repo, only_tag="C2-DCDC-A", manifest_path=manifest_path)
    assert rc == 0
    manifest = json.loads(manifest_path.read_text())
    entry = manifest["CHASSIS-C2-DCDC-A"]
    assert entry["chassis"] == "C2-DCDC"
    assert entry["rev"] == "A"
    assert entry["source_tag"] == "C2-DCDC-A"
    assert entry["dir"] == "Data/Releases/C2-DCDC/A"
    assert (docs_root / entry["dir"] / "BOMs" / "mouser_bom.csv").is_file()
    # mech parts ride along under the family, chassis labeled C2-DCDC
    mech = manifest["HW-C2-DCLBB-A"]
    assert mech["chassis"] == "C2-DCDC"
    assert mech["dir"] == "Data/Releases/C2-DCDC/A/Mech/HW-C2-DCLBB-A"
    # boards keep the chassis short code (shared C2 hardware)
    assert manifest["HW-C2-PCB-CTRL-B"]["chassis"] == "C2"
    # the tag names the C2-DCDC family: Chassis3 content is not exported
    assert not any(k.startswith("CHASSIS-C3") or k.startswith("HW-C3")
                   for k in manifest)


def test_update_wip_tag_scopes_to_named_chassis(hw_repo, docs_root, fake_kicad):
    """A tag with a multi-letter rev (C3-WIP) still scopes the chassis-level
    export to the named chassis: Chassis2 content is not republished from it."""
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
    sp.run(["git", "-C", str(hw_repo), "tag", "C3-WIP"], check=True)
    manifest_path = docs_root / "Data" / "Releases" / "manifest.json"
    rc = core.update(hw_repo, only_tag="C3-WIP", manifest_path=manifest_path)
    assert rc == 0
    manifest = json.loads(manifest_path.read_text())
    # boardless chassis: rev falls back to the full tag name
    assert manifest["CHASSIS-C3-C3-WIP"]["rev"] == "C3-WIP"
    assert manifest["HW-C3-PBB-A"]["chassis"] == "C3"
    # the tag names C3: no Chassis2 chassis-level or mech entries from it
    assert not any(k.startswith("CHASSIS-C2") for k in manifest)
    assert "HW-C2-DCLBB-A" not in manifest
    # boards are shared and rev-keyed: still exported under the chassis code
    assert manifest["HW-C2-PCB-CTRL-B"]["chassis"] == "C2"


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
