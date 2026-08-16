"""Release pipeline: tags -> KiCad exports -> Data/Releases + manifest."""

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


def export_board(board: Board, out_dir: Path, ibom_generator: Optional[Path]) -> dict:
    """Generate all artifacts for one board into out_dir. Returns artifact map."""
    out_dir.mkdir(parents=True, exist_ok=True)
    artifacts: Dict[str, str] = {}
    marks = []

    if board.sch:
        pdf = out_dir / "schematic.pdf"
        ok = kicad.export_sch_pdf(board.sch, pdf)
        marks.append(f"pdf {'✓' if ok else '✗'}")
        if ok:
            artifacts["schematic_pdf"] = pdf.name
        bom = out_dir / "bom.csv"
        ok = kicad.export_bom(board.sch, bom)
        marks.append(f"bom {'✓' if ok else '✗'}")
        if ok:
            artifacts["bom_csv"] = bom.name

    if board.pcb:
        gz = out_dir / "gerbers.zip"
        ok = kicad.export_gerber_zip(board.pcb, gz)
        marks.append(f"gerbers {'✓' if ok else '✗'}")
        if ok:
            artifacts["gerber_zip"] = gz.name
        drc = out_dir / "drc.txt"
        violations = kicad.run_drc(board.pcb, drc)
        marks.append("drc clean" if violations == 0 else
                     (f"drc {violations} error(s)" if violations is not None else "drc ✗"))
        if violations is not None:
            artifacts["drc"] = drc.name
            artifacts["drc_violations"] = violations
        step = out_dir / f"{board.name}.step"
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
        # Temp dir must live under $HOME (releases dir) — the KiCad flatpak
        # sandbox cannot access /tmp.
        with tempfile.TemporaryDirectory(prefix=f".tmp-{tag}-",
                                         dir=releases_dir) as tmp:
            tmp_path = Path(tmp)
            if not archive_tag(hw_repo, tag, tmp_path):
                print(f"Tag {tag}: no Hardware/ tree, skipped.")
                continue
            boards = find_boards(tmp_path / "Hardware")
            if not boards:
                print(f"Tag {tag}: no boards found, skipped.")
                continue
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
                artifacts = export_board(board, out_dir, ibom_gen)
                manifest[pn] = {
                    "part_number": pn,
                    "chassis": short,
                    "board": board.name,
                    "rev": board.rev,
                    "source_tag": tag,
                    "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "dir": str(out_dir.relative_to(REPO_ROOT)),
                    "artifacts": artifacts,
                }
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
        print("Manifest is empty — run: hwrelease update")
        return 0
    by_rev: Dict[str, List[dict]] = {}
    for entry in manifest.values():
        by_rev.setdefault(entry["rev"], []).append(entry)
    for rev in sorted(by_rev):
        print(f"Rev {rev}:")
        for e in sorted(by_rev[rev], key=lambda x: x["part_number"]):
            ibom = "ibom" if "ibom" in e.get("artifacts", {}) else "no-ibom"
            print(f"  {e['part_number']:<24} {e['board']:<22} [{ibom}]  {e['dir']}")
    return 0
