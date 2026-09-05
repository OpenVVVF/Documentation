"""KiCad CLI export helpers.

Mirrors the export commands used by the hardware repo's BOMManager
(../InverterGen5/Hardware/BOMManager/bom_manager/regen.py and assembly.py).
KiCad runs via flatpak (org.kicad.KiCad) with a plain ``kicad-cli`` fallback.
"""

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import List, Optional

_BOM_FIELDS = "Reference,Value,Footprint,QUANTITY,DNP,EXCLUDE_FROM_BOM"
_BOM_LABELS = "Designator,Designation,Footprint,Quantity,DNP,Exclude from BOM"


def kicad(args: List[str], timeout: int = 600,
          ok_rc=(0,)) -> subprocess.CompletedProcess:
    """Run kicad-cli, preferring the KiCad flatpak."""
    cmd = ["flatpak", "run", "--command=kicad-cli", "org.kicad.KiCad"] + args
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        cmd[0:4] = ["kicad-cli"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode not in ok_rc:
        tail = (r.stderr or r.stdout).strip().splitlines()[-2:]
        print(f"  kicad-cli {' '.join(args[:3])}... failed: {' | '.join(tail)}",
              file=sys.stderr)
    return r


def export_sch_pdf(sch: Path, out_pdf: Path) -> bool:
    r = kicad(["sch", "export", "pdf", str(sch), "-o", str(out_pdf)])
    return r.returncode == 0 and out_pdf.is_file()


def export_bom(sch: Path, out_csv: Path) -> bool:
    r = kicad([
        "sch", "export", "bom", str(sch),
        "--fields", _BOM_FIELDS, "--labels", _BOM_LABELS,
        # Group by DNP too: KiCad marks an entire --group-by "Value" row as
        # DNP if ANY symbol in the group is DNP, and BOMManager's parser then
        # drops the whole row (e.g. one DNP 10uF cap erases all 10uF caps).
        "--group-by", "Value,DNP", "--ref-range-delimiter", "",
        "-o", str(out_csv),
    ])
    return r.returncode == 0 and out_csv.is_file()


def export_gerber_zip(pcb: Path, out_zip: Path) -> bool:
    """Export gerbers + drill files and pack them into one zip."""
    fab_dir = out_zip.parent / "_fab_tmp"
    if fab_dir.exists():
        shutil.rmtree(fab_dir)
    fab_dir.mkdir(parents=True)
    ok = True
    r = kicad(["pcb", "export", "gerbers", str(pcb), "-o", str(fab_dir)])
    ok = ok and r.returncode == 0
    r = kicad(["pcb", "export", "drill", str(pcb), "-o", str(fab_dir)])
    ok = ok and r.returncode == 0
    files = [f for f in fab_dir.iterdir() if f.is_file()]
    if not files:
        ok = False
    if ok:
        with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(files):
                zf.write(f, f.name)
    shutil.rmtree(fab_dir, ignore_errors=True)
    return ok and out_zip.is_file()


def run_drc(pcb: Path, out_txt: Path) -> Optional[int]:
    """Run DRC. Returns violation count, or None on failure."""
    r = kicad(["pcb", "drc", str(pcb), "--refill-zones", "--severity-error",
               "-o", str(out_txt)], ok_rc=(0, 5))  # 5 = violations found
    if r.returncode not in (0, 5) or not out_txt.is_file():  # 5 = violations found
        return None
    text = out_txt.read_text(errors="replace")
    for line in text.splitlines():
        if "violations" in line.lower():
            nums = [int(tok) for tok in line.split() if tok.isdigit()]
            if nums:
                return nums[0]
    return 0


def export_step(pcb: Path, out_step: Path) -> bool:
    r = kicad(["pcb", "export", "step", str(pcb), "-o", str(out_step),
               "--subst-models"], timeout=900)
    return r.returncode == 0 and out_step.is_file()


def find_ibom_generator(search_roots: List[Path]) -> Optional[Path]:
    """Locate InteractiveHtmlBom's generate_interactive_bom.py in a venv."""
    for root in search_roots:
        for sp in sorted(root.glob(
                "lib/python3*/site-packages/InteractiveHtmlBom/generate_interactive_bom.py")):
            return sp
    return None


def export_ibom(pcb: Path, out_html: Path, generator: Path) -> bool:
    """Generate the interactive assembly BOM HTML for a board."""
    site = generator.parent.parent
    out_html.parent.mkdir(parents=True, exist_ok=True)
    dest_dir = out_html.parent
    cmd = [
        "flatpak", "run",
        f"--env=PYTHONPATH={site}",
        "--env=INTERACTIVE_HTML_BOM_NO_DISPLAY=1",
        "--command=python3", "org.kicad.KiCad",
        str(generator),
        "--no-browser",
        "--dest-dir", str(dest_dir),
        "--name-format", "%f",
        str(pcb),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    except FileNotFoundError:
        print("  flatpak not found; iBOM needs KiCad (flatpak) on this machine.",
              file=sys.stderr)
        return False
    made = dest_dir / f"{pcb.stem}.html"
    if result.returncode != 0 or not made.is_file():
        tail = (result.stderr or result.stdout).strip().splitlines()[-1:]
        print(f"  iBOM failed for {pcb.stem}: {tail}", file=sys.stderr)
        return False
    if made != out_html:
        made.replace(out_html)
    return True
