"""Release pipeline: tags -> KiCad exports -> Data/Releases + manifest."""

import contextlib
import io
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from . import kicad

REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = REPO_ROOT / "Data" / "Releases" / "manifest.json"

_REV_RE = re.compile(r'\(rev\s+"([^"]+)"\)')


@dataclass
class Board:
    chassis: str        # directory name, e.g. "Chassis2"
    name: str           # e.g. "ControlBoard"
    sch: Optional[Path]
    pcb: Optional[Path]
    rev: str
    renders: List[Path] = field(default_factory=list)


# ---------------------------------------------------------------- git helpers

def git(hw_repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(hw_repo)] + list(args),
                          capture_output=True, text=True)


def fetch_tags(hw_repo: Path) -> None:
    r = git(hw_repo, "fetch", "--tags")
    if r.returncode != 0:
        print(f"  warning: git fetch --tags failed: {r.stderr.strip()}")


def list_tags(hw_repo: Path, pattern: str = "*") -> List[str]:
    r = git(hw_repo, "tag", "--list", pattern, "--sort=creatordate")
    if r.returncode != 0:
        raise RuntimeError(f"git tag failed: {r.stderr.strip()}")
    return [t for t in r.stdout.split() if t]


def archive_tag(hw_repo: Path, tag: str, dest: Path) -> bool:
    """Extract Hardware/ from a tag into dest. Returns False if absent."""
    r = subprocess.run(
        f'git -C "{hw_repo}" archive "{tag}" Hardware | tar -x -C "{dest}"',
        shell=True, capture_output=True, text=True)
    return (dest / "Hardware").is_dir() and r.returncode == 0


def repo_web_url(hw_repo: Path) -> Optional[str]:
    """HTTPS web URL of the hardware repo's origin (for source links)."""
    r = git(hw_repo, "config", "--get", "remote.origin.url")
    if r.returncode != 0:
        return None
    url = r.stdout.strip()
    if url.startswith("git@"):  # git@github.com:owner/repo.git
        url = "https://" + url[4:].replace(":", "/", 1)
    if url.endswith(".git"):
        url = url[:-4]
    return url or None


# ------------------------------------------------------------- board scanning

def parse_rev(sch_path: Path) -> Optional[str]:
    try:
        m = _REV_RE.search(sch_path.read_text(errors="replace"))
        return m.group(1) if m else None
    except OSError:
        return None


def find_boards(hardware_root: Path) -> List[Board]:
    """Scan Hardware/<Chassis>/Boards/<Name>/ for KiCad designs."""
    boards = []
    for chassis_dir in sorted(hardware_root.iterdir()):
        boards_dir = chassis_dir / "Boards"
        if not chassis_dir.is_dir() or not boards_dir.is_dir():
            continue
        for board_dir in sorted(boards_dir.iterdir()):
            if not board_dir.is_dir():
                continue
            name = board_dir.name
            sch = board_dir / f"{name}.kicad_sch"
            pcb = board_dir / f"{name}.kicad_pcb"
            if not sch.is_file() and not pcb.is_file():
                continue
            rev = parse_rev(sch) if sch.is_file() else None
            if rev is None and pcb.is_file():
                rev = parse_rev(pcb)
            if rev is None:
                print(f"  warning: no (rev ...) in {chassis_dir.name}/{name}; skipped")
                continue
            renders = [p for p in boards_dir.glob(f"{name}*.png") if p.is_file()]
            boards.append(Board(chassis_dir.name, name,
                                sch if sch.is_file() else None,
                                pcb if pcb.is_file() else None,
                                rev, renders))
    return boards


# -------------------------------------------------------------- part numbers

def load_products(config_path: Optional[Path] = None) -> dict:
    config_path = config_path or REPO_ROOT / "Config" / "Products.yaml"
    return yaml.safe_load(config_path.read_text())


def chassis_short_code(products: dict, chassis: str) -> Optional[str]:
    entry = (products.get("chassis") or {}).get(chassis)
    return entry.get("short_code") if entry else None


def board_descriptor(descriptors_path: Path, chassis: str, board: str) -> Optional[str]:
    descriptors = json.loads(descriptors_path.read_text())
    return descriptors.get(f"{chassis}|pcb|{board.lower()}")


def part_number(short_code: str, descriptor: str, rev: str) -> str:
    return f"HW-{short_code}-PCB-{descriptor}-{rev}"


# ------------------------------------------------------------------ manifest

def load_manifest(path: Path = MANIFEST_PATH) -> Dict[str, dict]:
    if path.is_file():
        return json.loads(path.read_text())
    return {}


def save_manifest(manifest: Dict[str, dict], path: Path = MANIFEST_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


# --------------------------------------------------------- chassis-level BOMs

_VENDOR_BOMS = {
    "mouser_bom.csv": "mouser",
    "mcmaster_bom.csv": "mcmaster",
    "sendcutsend_bom.csv": "sendcutsend",
    "digikey_bom.csv": "digikey",
    "Consolidated_BOM.csv": "consolidated",
    "assembly_bom.csv": "assembly",
    "pcb_bom.csv": "pcb",
    "McMaster_Order_Paste.txt": "mcmaster_paste",
}


def _scan_bom_dir(bom_dir: Path, base: Path) -> Dict[str, str]:
    return {key: str(f.relative_to(base))
            for f, key in ((bom_dir / name, key) for name, key in _VENDOR_BOMS.items())
            if f.is_file()}


def _variant_vendor_totals(consolidated: Path) -> Dict[str, float]:
    """Sum Line Total per vendor from a variant Consolidated_BOM.csv."""
    import csv as _csv

    totals: Dict[str, float] = {}
    if not consolidated.is_file():
        return totals
    with open(consolidated, newline="", errors="replace") as f:
        for row in _csv.DictReader(f):
            try:
                amount = float(row["Line Total"])
            except (TypeError, ValueError):
                continue
            vendor = (row.get("Vendor") or "unknown").strip()
            totals[vendor] = totals.get(vendor, 0.0) + amount
    return totals


def export_chassis_boms(chassis_dir: Path, out_dir: Path) -> dict:
    """Copy FabricationData/BOMs/ (incl. Variants) into out_dir/BOMs."""
    src = chassis_dir / "FabricationData" / "BOMs"
    if not src.is_dir():
        return {}
    dest = out_dir / "BOMs"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    # The base McMaster paste file lives next to BOMs/, not inside it.
    base_paste = chassis_dir / "FabricationData" / "McMaster_Order_Paste.txt"
    if base_paste.is_file():
        shutil.copy2(base_paste, dest / "McMaster_Order_Paste.txt")
    artifacts = {"vendor_boms": _scan_bom_dir(dest, out_dir)}
    variants_dir = dest / "Variants"
    variants = {}
    variant_vendors: Dict[str, Dict[str, str]] = {}
    if variants_dir.is_dir():
        for vdir in sorted(variants_dir.iterdir()):
            if vdir.is_dir():
                variants[vdir.name] = _scan_bom_dir(vdir, out_dir)
                totals = _variant_vendor_totals(vdir / "Consolidated_BOM.csv")
                if totals:
                    variant_vendors[vdir.name] = {
                        vendor: f"{amount:,.2f}" for vendor, amount in sorted(totals.items())
                    }
    if variants:
        artifacts["variants"] = variants
    report = chassis_dir / "FabricationData" / "Pricing_Report.md"
    if report.is_file():
        shutil.copy2(report, out_dir / "Pricing_Report.md")
        artifacts["pricing_report"] = "Pricing_Report.md"
        estimate = parse_price_estimate(report)
        if estimate:
            artifacts["price_estimate"] = estimate
    if variant_vendors:
        artifacts.setdefault("price_estimate", {})[
            "variant_vendors"] = variant_vendors
    return artifacts


def regenerate_vendor_boms(hardware_root: Path) -> Optional[Dict[str, str]]:
    """Regenerate vendor BOMs + pricing from the exported KiCad sources using
    this repo's BOMManager, so exports never ship stale committed BOMs.

    Returns {variant: total} price totals (e.g. {"bare minimum": "2,198.58",
    "standard": "2,241.19"}), or None if generation was unavailable.
    """
    try:
        from bom_manager import generate
        from bom_manager.context import build_context
    except ImportError:
        print("  warning: bom_manager not installed; copying committed BOMs")
        return None
    ctx = build_context(hardware_root=hardware_root, allow_prompt=False)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = generate.run(["--no-prompt", "--variants", "--no-pcb-zips"], ctx)
    except Exception as exc:  # generation failure must not kill the export
        print(f"  warning: vendor BOM generation failed ({exc}); copying committed BOMs")
        return None
    output = buf.getvalue()
    print(output, end="")
    if rc != 0:
        print("  warning: vendor BOM generation failed; copying committed BOMs")
        return None
    totals: Dict[str, str] = {}
    m = re.search(r"bare minimum \$([\d,]+\.\d\d)", output)
    if m:
        totals["base"] = m.group(1)
    for m in re.finditer(r"^\s*(\w+)\s+\$([\d,]+\.\d\d) \(\+\$[\d,]+\.\d\d\)",
                         output, re.MULTILINE):
        totals[m.group(1)] = m.group(2)
    return totals


def _fmt_amount(raw: str) -> str:
    return f"{float(raw.replace(',', '')):,.2f}"


def parse_price_estimate(report_path: Path) -> dict:
    """Pull per-vendor subtotals and the grand total out of Pricing_Report.md."""
    estimate: Dict[str, object] = {}
    if not report_path.is_file():
        return estimate
    text = report_path.read_text(errors="replace")
    vendors = {m.group(1): _fmt_amount(m.group(2))
               for m in re.finditer(r"\*\*(.+?) subtotal:\*\* \$([\d,]+\.\d\d)", text)}
    if vendors:
        estimate["vendors"] = vendors
    m = re.search(r"Grand Total \((\d+) unit.*?\$([\d,]+\.\d\d)", text)
    if m:
        estimate["qty"] = int(m.group(1))
        estimate["total"] = _fmt_amount(m.group(2))
    return estimate


def load_fab_spec(board_dir: Path) -> Optional[dict]:
    """Read a board's fab_spec.yaml, merged over Boards/fab_defaults.yaml.

    Returns {"options": {...}, "notes": [...], "default_notes": [...]}
    (board-specific vs. chassis-default notes), or None.
    """
    spec: Dict[str, object] = {"options": {}, "notes": [], "default_notes": []}
    defaults_path = board_dir.parent / "fab_defaults.yaml"
    board_path = board_dir / "fab_spec.yaml"
    if not defaults_path.is_file() and not board_path.is_file():
        return None
    if defaults_path.is_file():
        data = yaml.safe_load(defaults_path.read_text()) or {}
        spec["options"].update(data.get("options") or {})
        spec["default_notes"].extend(data.get("notes") or [])
    if board_path.is_file():
        data = yaml.safe_load(board_path.read_text()) or {}
        spec["options"].update(data.get("options") or {})
        spec["notes"].extend(data.get("notes") or [])
    if not spec["options"] and not spec["notes"] and not spec["default_notes"]:
        return None
    return spec


def parse_info_txt(path: Path) -> Dict[str, str]:
    """Parse a SendCutSend-style info.txt (Key=value lines)."""
    out: Dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(errors="replace").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def export_mech_parts(chassis_dir: Path, out_dir: Path) -> List[dict]:
    """Export fabricated mechanical parts (Mechanical/Fab/<part>/) -> Mech/.

    Copies STEP, image, info.txt and reads fab_spec.yaml; returns one
    artifacts dict per part.
    """
    fab_dir = chassis_dir / "Mechanical" / "Fab"
    if not fab_dir.is_dir():
        return []
    parts = []
    for part_dir in sorted(fab_dir.iterdir()):
        if not part_dir.is_dir():
            continue
        dest = out_dir / "Mech" / part_dir.name
        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True)
        artifacts: Dict[str, object] = {}
        for step in part_dir.glob("*.step"):
            shutil.copy2(step, dest / step.name)
            artifacts["step"] = step.name
        for stl in part_dir.glob("*.stl"):
            shutil.copy2(stl, dest / stl.name)
            artifacts["stl"] = stl.name
        for img in part_dir.glob("*.png"):
            shutil.copy2(img, dest / img.name)
            artifacts["image"] = img.name
        info = parse_info_txt(part_dir / "info.txt")
        if info:
            shutil.copy2(part_dir / "info.txt", dest / "info.txt")
            artifacts["info"] = "info.txt"
            artifacts["info_fields"] = info
        spec_file = part_dir / "fab_spec.yaml"
        if spec_file.is_file():
            artifacts["fab_spec"] = yaml.safe_load(spec_file.read_text()) or {}
        holes_file = part_dir / "holes.json"
        if holes_file.is_file():
            shutil.copy2(holes_file, dest / "holes.json")
            artifacts["holes"] = "holes.json"
        mat_file = part_dir / "material.json"
        if mat_file.is_file():
            shutil.copy2(mat_file, dest / "material.json")
            artifacts["material"] = json.loads(
                mat_file.read_text()).get("material")
        parts.append({"part": part_dir.name, "artifacts": artifacts})
    return parts


def _chassis_has_mech_content(chassis_dir: Path) -> bool:
    """True if a chassis has a FreeCAD model or a Mechanical/Fab dir."""
    mech = chassis_dir / "Mechanical"
    return mech.is_dir() and (any(mech.glob("*.FCStd")) or (mech / "Fab").is_dir())


# -------------------------------------------------------------------- update

def default_hw_repo() -> Path:
    products = load_products()
    roots = products.get("hardware_roots") or ["../InverterGen5/Hardware"]
    return (REPO_ROOT / roots[0]).resolve().parent


def _ibom_search_roots(hw_repo: Path) -> List[Path]:
    return [
        hw_repo / "Hardware" / "BOMManager" / ".venv",
        REPO_ROOT / ".venv",
    ]


def export_board(board: Board, out_dir: Path, ibom_generator: Optional[Path],
                 pn: str) -> dict:
    """Generate all artifacts for one board into out_dir. Returns artifact map.

    Files are named after the part number (e.g. HW-C2-PCB-CTRL-A-schematic.pdf)
    except the interactive assembly (ibom.html) and the render PNGs.
    """
    if out_dir.exists():
        shutil.rmtree(out_dir)  # generated data; start clean
    out_dir.mkdir(parents=True, exist_ok=True)
    artifacts: Dict[str, str] = {}
    marks = []

    if board.sch:
        pdf = out_dir / f"{pn}-schematic.pdf"
        ok = kicad.export_sch_pdf(board.sch, pdf)
        marks.append(f"pdf {'✓' if ok else '✗'}")
        if ok:
            artifacts["schematic_pdf"] = pdf.name
        bom = out_dir / f"{pn}-bom.csv"
        ok = kicad.export_bom(board.sch, bom)
        marks.append(f"bom {'✓' if ok else '✗'}")
        if ok:
            artifacts["bom_csv"] = bom.name

    if board.pcb:
        gz = out_dir / f"{pn}-gerbers.zip"
        ok = kicad.export_gerber_zip(board.pcb, gz)
        marks.append(f"gerbers {'✓' if ok else '✗'}")
        if ok:
            artifacts["gerber_zip"] = gz.name
        drc = out_dir / f"{pn}-drc.txt"
        violations = kicad.run_drc(board.pcb, drc)
        marks.append("drc clean" if violations == 0 else
                     (f"drc {violations} error(s)" if violations is not None else "drc ✗"))
        if violations is not None:
            artifacts["drc"] = drc.name
            artifacts["drc_violations"] = violations
        step = out_dir / f"{pn}.step"
        ok = kicad.export_step(board.pcb, step)
        marks.append(f"step {'✓' if ok else '✗'}")
        if ok:
            artifacts["step"] = step.name
        if ibom_generator:
            ibom = out_dir / "ibom.html"
            ok = kicad.export_ibom(board.pcb, ibom, ibom_generator)
            marks.append(f"ibom {'✓' if ok else '✗'}")
            if ok:
                artifacts["ibom"] = ibom.name
        else:
            marks.append("ibom skipped (InteractiveHtmlBom not found)")

    copied = []
    for png in board.renders:
        shutil.copy2(png, out_dir / png.name)
        copied.append(png.name)
    if copied:
        artifacts["renders"] = copied

    # Optional per-board ordering specs (fab_spec.yaml beside the project),
    # merged over chassis defaults (Boards/fab_defaults.yaml).
    board_dir = (board.sch or board.pcb).parent
    fab_spec = load_fab_spec(board_dir)
    if fab_spec:
        artifacts["fab_spec"] = fab_spec

    print(f"  {board.chassis}/{board.name} rev {board.rev}: {'  '.join(marks)}")
    return artifacts


def update(hw_repo: Path, tag_pattern: str = "*", only_tag: Optional[str] = None,
           force: bool = False, manifest_path: Path = MANIFEST_PATH,
           releases_dir: Optional[Path] = None) -> int:
    """Export every missing (board, rev) from matching release tags."""
    releases_dir = releases_dir or manifest_path.parent
    releases_dir.mkdir(parents=True, exist_ok=True)
    products = load_products()
    descriptors_path = REPO_ROOT / "Data" / "Parts" / "Descriptors.json"
    manifest = load_manifest(manifest_path)

    fetch_tags(hw_repo)
    web_url = repo_web_url(hw_repo)
    tags = [only_tag] if only_tag else list_tags(hw_repo, tag_pattern)
    if not tags:
        print(f"No tags matching '{tag_pattern}' in {hw_repo}.")
        return 1

    known_tags = {e.get("source_tag") for e in manifest.values()}
    new_count = 0
    for tag in tags:
        if not force and only_tag is None and tag in known_tags:
            print(f"Tag {tag}: already in manifest, skipped.")
            continue
        # Temp dir must live under $HOME: the KiCad flatpak sandbox cannot
        # access /tmp. Repo root works and is cleaned up automatically.
        with tempfile.TemporaryDirectory(prefix=f".hwrelease-tmp-{tag}-",
                                         dir=REPO_ROOT) as tmp:
            tmp_path = Path(tmp)
            if not archive_tag(hw_repo, tag, tmp_path):
                print(f"Tag {tag}: no Hardware/ tree, skipped.")
                continue
            boards = find_boards(tmp_path / "Hardware")
            if not boards and not any(
                    _chassis_has_mech_content(d)
                    for d in (tmp_path / "Hardware").iterdir() if d.is_dir()):
                print(f"Tag {tag}: no boards or mechanical content found, skipped.")
                continue
            # BOMManager discovers board BOMs as <Board>.csv beside the KiCad
            # project (same for wiring harnesses); export them from the
            # schematics before generating.
            for board in boards:
                if board.sch:
                    kicad.export_bom(board.sch,
                                     board.sch.parent / f"{board.name}.csv")
            for chassis_dir in sorted((tmp_path / "Hardware").iterdir()):
                for hroot in ("Wiring", "Harnesses"):
                    hdir = chassis_dir / hroot
                    if not hdir.is_dir():
                        continue
                    for part_dir in sorted(hdir.iterdir()):
                        sch = part_dir / f"{part_dir.name}.kicad_sch"
                        if part_dir.is_dir() and sch.is_file():
                            kicad.export_bom(sch, part_dir / f"{part_dir.name}.csv")
            from . import fcextract
            extracted_by_chassis = {}
            for chassis_dir in sorted((tmp_path / "Hardware").iterdir()):
                if not chassis_dir.is_dir():
                    continue
                extracted = fcextract.extract_parts(chassis_dir)
                if extracted:
                    print(f"  {chassis_dir.name} model extraction: "
                          f"{len(extracted)} part(s) from FCStd")
                    n_img = fcextract.render_images(chassis_dir)
                    print(f"  {chassis_dir.name} model renders: {n_img} image(s)")
                    for w in fcextract.check_mcmaster(chassis_dir):
                        print(w)
                    for note in fcextract.merge_mcmaster(chassis_dir):
                        print(note)
                    extracted_by_chassis[chassis_dir.name] = extracted
            variant_totals = regenerate_vendor_boms(tmp_path / "Hardware")
            ibom_gen = kicad.find_ibom_generator(_ibom_search_roots(hw_repo))
            print(f"Tag {tag}: {len(boards)} board(s)"
                  + ("" if ibom_gen else " (iBOM generator not found)"))
            for board in boards:
                short = chassis_short_code(products, board.chassis)
                desc = board_descriptor(descriptors_path, board.chassis, board.name)
                if not short or not desc:
                    print(f"  {board.chassis}/{board.name}: no short code/descriptor "
                          f"mapping in Config/Products.yaml or Data/Parts/Descriptors.json; skipped")
                    continue
                pn = part_number(short, desc, board.rev)
                if pn in manifest and not force:
                    print(f"  {pn}: already exported, skipped.")
                    continue
                out_dir = releases_dir / short / board.rev / board.name
                artifacts = export_board(board, out_dir, ibom_gen, pn)
                entry = {
                    "part_number": pn,
                    "chassis": short,
                    "board": board.name,
                    "rev": board.rev,
                    "source_tag": tag,
                    "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "dir": str(out_dir.relative_to(REPO_ROOT)),
                    "artifacts": artifacts,
                }
                if web_url:
                    entry["source_url"] = f"{web_url}/tree/{tag}"
                manifest[pn] = entry
                new_count += 1
            # Chassis-level export (one entry per chassis per revision): any
            # chassis with boards or mechanical content.
            chassis_dirs = {b.chassis for b in boards}
            for d in (tmp_path / "Hardware").iterdir():
                if d.is_dir() and _chassis_has_mech_content(d):
                    chassis_dirs.add(d.name)
            for chassis in sorted(chassis_dirs):
                short = chassis_short_code(products, chassis)
                if not short:
                    continue
                # A tag naming a chassis directly (e.g. "C2-B") scopes the
                # release to that chassis: other chassis are not exported
                # from this tag.
                tag_chassis = re.fullmatch(r"([A-Z]\d+)-[A-Z]\d*", tag)
                if tag_chassis and tag_chassis.group(1) != short:
                    continue
                revs = {b.rev for b in boards if b.chassis == chassis}
                rev = revs.pop() if len(revs) == 1 else tag
                # ...and pins the chassis rev, so a mechanical-only release
                # can move the chassis revision without a board rev bump.
                m = re.fullmatch(rf"{short}-([A-Z]\d*)", tag)
                if m:
                    rev = m.group(1)
                key = f"CHASSIS-{short}-{rev}"
                if key in manifest and not force:
                    continue
                out_dir = releases_dir / short / rev
                artifacts = export_chassis_boms(tmp_path / "Hardware" / chassis,
                                                out_dir)
                had_boms = bool(artifacts)
                mech_parts = export_mech_parts(tmp_path / "Hardware" / chassis,
                                               out_dir)
                # Skip only when there is genuinely nothing: no vendor BOMs,
                # no mech parts.
                if not artifacts and not mech_parts:
                    continue
                if variant_totals and had_boms:
                    artifacts.setdefault("price_estimate", {})[
                        "variants"] = variant_totals
                extracted = extracted_by_chassis.get(chassis, [])
                if extracted:
                    for w in fcextract.check_part_qty(tmp_path / "Hardware" / chassis):
                        print(w)
                for mp in mech_parts:
                    for w in fcextract.check_spec_holes(
                            mp["part"], mp["artifacts"].get("fab_spec"),
                            tmp_path / "Hardware" / chassis / "Mechanical" / "Fab"
                            / mp["part"] / "holes.json"):
                        print(w)
                    if extracted and "info" not in mp["artifacts"] \
                            and "fab_spec" not in mp["artifacts"]:
                        print(f"  note: {mp['part']} came from the model and has no "
                              f"info.txt/fab_spec.yaml yet")
                for mp in mech_parts:
                    pn = mp["part"]
                    if pn in manifest and not force:
                        continue
                    entry = {
                        "mech": True,
                        "part_number": pn,
                        "chassis": short,
                        "rev": rev,
                        "source_tag": tag,
                        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        "dir": str((out_dir / "Mech" / pn).relative_to(REPO_ROOT)),
                        "artifacts": mp["artifacts"],
                    }
                    if web_url:
                        entry["source_url"] = f"{web_url}/tree/{tag}"
                    manifest[pn] = entry
                if mech_parts:
                    print(f"  {chassis} mech parts: {len(mech_parts)} exported")
                # Prune mech entries that vanished from the hardware tree.
                seen = {mp["part"] for mp in mech_parts}
                for pn in [k for k, v in manifest.items()
                           if v.get("mech") and v.get("chassis") == short
                           and v.get("source_tag") == tag and k not in seen]:
                    del manifest[pn]
                    shutil.rmtree(out_dir / "Mech" / pn, ignore_errors=True)
                    print(f"  {pn}: no longer in the hardware tree, pruned")
                entry = {
                    "chassis": short,
                    "rev": rev,
                    "source_tag": tag,
                    "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "dir": str(out_dir.relative_to(REPO_ROOT)),
                    "artifacts": artifacts,
                }
                if web_url:
                    entry["source_url"] = f"{web_url}/tree/{tag}"
                manifest[key] = entry
                print(f"  {chassis} chassis export rev {rev}: exported")
                new_count += 1
        save_manifest(manifest, manifest_path)

    print(f"\n{new_count} board revision(s) exported -> {releases_dir.relative_to(REPO_ROOT)}")
    if new_count:
        from . import viewer
        viewer.build_viewer(manifest_path)
    return 0


# ---------------------------------------------------------------- show / list

def show(pn: str, manifest_path: Path = MANIFEST_PATH) -> int:
    manifest = load_manifest(manifest_path)
    entry = manifest.get(pn)
    if entry is None:
        matches = {k: v for k, v in manifest.items() if pn.upper() in k}
        if not matches:
            print(f"{pn}: not found in manifest.")
            return 1
        entry = next(iter(matches.values()))
    print(json.dumps(entry, indent=2))
    return 0


def list_boards(manifest_path: Path = MANIFEST_PATH) -> int:
    manifest = load_manifest(manifest_path)
    if not manifest:
        print("Manifest is empty - run: hwrelease update")
        return 0
    by_rev: Dict[str, List[dict]] = {}
    for key, entry in manifest.items():
        by_rev.setdefault(entry["rev"], []).append((key, entry))
    for rev in sorted(by_rev):
        print(f"Rev {rev}:")
        for key, e in sorted(by_rev[rev], key=lambda x: x[0]):
            if "board" not in e:
                print(f"  {key:<24} chassis {e['chassis']:<5} vendor BOMs  {e['dir']}")
                continue
            ibom = "ibom" if "ibom" in e.get("artifacts", {}) else "no-ibom"
            print(f"  {key:<24} {e['board']:<22} [{ibom}]  {e['dir']}")
    return 0
