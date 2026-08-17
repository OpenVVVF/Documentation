"""FreeCAD extraction: pull fabricated parts out of the mechanical model.

Runs a script inside the FreeCAD flatpak's headless python (freecadcmd) that
opens the chassis FCStd, finds every PartDesign::Body or App::DocumentObjectGroup
whose label ends with a part number (HW-...), and exports per part:
- <pn>.step   (STEP model, into Mechanical/Fab/<pn>/)
- holes.json  (cylindrical-hole diameter histogram in mm, for spec checking)

The extractor keys on labels only — no translation layer. Rename bodies/groups
in the model so the label ends with the exact part number.
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

_PN_RE = re.compile(r"(HW-[A-Z0-9]+(?:-[A-Z0-9]+)*)\s*$")

# Runs inside freecadcmd. Prints one JSON object on the last stdout line.
_FC_SCRIPT = r"""
import json
import re
import sys

import FreeCAD as App
import Import

pn_re = re.compile(r"(HW-[A-Z0-9]+(?:-[A-Z0-9]+)*?)(?:\d{3})?\s*$")
mc_re = re.compile(r"^(\d{4,6}[A-Z]\d{2,4})[_\s]")
fcstd, out_root = sys.argv[2], sys.argv[3]
doc = App.openDocument(fcstd)

def members(obj):
    if obj.TypeId == "App::DocumentObjectGroup":
        out = []
        for sub in obj.Group:
            out.extend(members(sub))
        return out
    return [obj]

def hole_diameters(shape):
    diams = {}
    for face in shape.Faces:
        surf = face.Surface
        if surf.TypeId == "Part::GeomCylinder":
            try:
                d = round(2 * surf.Radius, 2)
                if d > 0:
                    diams[d] = diams.get(d, 0) + 1
            except Exception:
                pass
    return diams

parts = []
seen = set()
for obj in doc.Objects:
    if obj.TypeId not in ("PartDesign::Body", "App::DocumentObjectGroup"):
        continue
    m = pn_re.search(obj.Label)
    if not m:
        continue
    pn = re.sub(r"([A-Z]+)\d{3}$", r"\1", m.group(1))  # strip instance suffix
    if pn in seen:  # instance duplicates (...001, ...002) — one part per PN
        continue
    seen.add(pn)
    shapes = [o for o in members(obj) if hasattr(o, "Shape") and not o.Shape.isNull()]
    if not shapes:
        continue
    out_dir = f"{out_root}/{pn}"
    __import__("os").makedirs(out_dir, exist_ok=True)
    Import.export(shapes, f"{out_dir}/{pn}.step")
    holes = {}
    for o in shapes:
        for d, n in hole_diameters(o.Shape).items():
            holes[d] = holes.get(d, 0) + n
    with open(f"{out_dir}/holes.json", "w") as f:
        json.dump({str(k): v for k, v in sorted(holes.items())}, f)
    parts.append(pn)

# McMaster hardware: labels like "91292A134_18-8 Stainless ... Screw001".
# Quantity per part number = number of instances in the model.
mcmaster = {}
for obj in doc.Objects:
    if obj.TypeId != "Part::Feature":
        continue
    m = mc_re.match(obj.Label)
    if m:
        mc = m.group(1)
        desc = re.sub(r"\d+$", "", obj.Label)
        entry = mcmaster.setdefault(mc, {"qty": 0, "description": desc})
        entry["qty"] += 1
with open(f"{out_root}/mcmaster_model.json", "w") as f:
    json.dump(mcmaster, f, sort_keys=True)

doc and App.closeDocument(doc.Name)
print("PARTS_JSON=" + json.dumps(sorted(parts)))
"""


def _freecad(args: List[str], timeout: int = 1800) -> Optional[subprocess.CompletedProcess]:
    cmd = ["flatpak", "run", "--command=freecadcmd", "org.freecad.FreeCAD"] + args
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return None


def find_fcstd(chassis_dir: Path) -> Optional[Path]:
    mech = chassis_dir / "Mechanical"
    if not mech.is_dir():
        return None
    files = sorted(mech.glob("*.FCStd"))
    return files[0] if files else None


def extract_parts(chassis_dir: Path) -> List[str]:
    """Export STEP + holes.json per labeled part into Mechanical/Fab/<pn>/.

    Writes into the (temp) hardware tree. Returns part numbers extracted,
    or [] if FreeCAD/FCStd is unavailable.
    """
    fcstd = find_fcstd(chassis_dir)
    if fcstd is None:
        return []
    fab_dir = chassis_dir / "Mechanical" / "Fab"
    fab_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
            "w", suffix=".py", dir=chassis_dir, delete=False) as f:
        f.write(_FC_SCRIPT)
        script = Path(f.name)
    try:
        r = _freecad([str(script), str(fcstd), str(fab_dir)])
    finally:
        script.unlink(missing_ok=True)
    if r is None:
        print("  freecad flatpak not found; skipping model extraction", file=sys.stderr)
        return []
    if r.returncode != 0:
        tail = (r.stderr or r.stdout).strip().splitlines()[-3:]
        print(f"  FreeCAD extraction failed: {tail}", file=sys.stderr)
        return []
    for line in r.stdout.splitlines():
        if line.startswith("PARTS_JSON="):
            return json.loads(line[len("PARTS_JSON="):])
    return []


def check_mcmaster(chassis_dir: Path) -> List[str]:
    """Cross-check MechanicalBOM.txt McMaster lines against the model's
    instance counts (mcmaster_model.json from extract_parts)."""
    model_path = chassis_dir / "Mechanical" / "Fab" / "mcmaster_model.json"
    bom_path = chassis_dir / "Mechanical" / "MechanicalBOM.txt"
    if not model_path.is_file() or not bom_path.is_file():
        return []
    model = json.loads(model_path.read_text())
    bom: Dict[str, int] = {}
    for line in bom_path.read_text(errors="replace").splitlines()[1:]:
        fields = [f.strip() for f in line.split(",")]
        if len(fields) >= 3 and fields[1].lower() == "mcmaster" and fields[2]:
            try:
                bom[fields[2]] = bom.get(fields[2], 0) + int(fields[0])
            except ValueError:
                pass
    warnings = []
    for pn, qty in sorted(bom.items()):
        m = model.get(pn)
        if m is None:
            warnings.append(f"  warning: McMaster {pn}: {qty}x in MechanicalBOM.txt "
                            f"but not found in the model")
        elif m["qty"] != qty:
            warnings.append(f"  warning: McMaster {pn}: {qty}x in MechanicalBOM.txt "
                            f"but {m['qty']}x in the model")
    for pn, m in sorted(model.items()):
        if pn not in bom:
            warnings.append(f"  warning: McMaster {pn}: {m['qty']}x in the model "
                            f"but missing from MechanicalBOM.txt")
    return warnings


# ------------------------------------------------------- spec vs. model check

_DIAM_RES = [
    re.compile(r'(\d+(?:\.\d+)?)\s*"'),          # inches: 0.1968"
    re.compile(r"[⌀ø]\s*(\d+(?:\.\d+)?)\s*mm"),  # mm: ⌀5.0 mm
    re.compile(r"(\d+(?:\.\d+)?)\s*mm"),         # bare mm: 5.0 mm
]


def spec_diameters_mm(text: str) -> List[float]:
    """Extract hole diameters (mm) from a spec string (deduplicated)."""
    out: List[float] = []
    for rx in _DIAM_RES:
        for m in rx.finditer(text):
            value = float(m.group(1))
            if rx is _DIAM_RES[0]:
                value *= 25.4
            value = round(value, 2)
            if value not in out:
                out.append(value)
    return out


def check_spec_holes(pn: str, fab_spec: dict, holes_json: Optional[Path]) -> List[str]:
    """Warn about tap/countersink diameters in fab_spec that the model lacks."""
    if not fab_spec or not holes_json or not holes_json.is_file():
        return []
    holes = {float(d) for d in json.loads(holes_json.read_text())}
    warnings = []
    services = fab_spec.get("services") or {}
    for kind in ("tapping", "countersink", "countersinking"):
        for item in services.get(kind) or []:
            if not isinstance(item, dict):
                continue
            label = item.get("thread") or item.get("for") or kind
            for d in spec_diameters_mm(item.get("holes", "")):
                if not any(abs(d - h) <= 0.05 for h in holes):
                    warnings.append(
                        f"  warning: {pn}: fab_spec {kind} '{label}' references "
                        f"⌀{d} mm but the model has no such hole")
    return warnings
