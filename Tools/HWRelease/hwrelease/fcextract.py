"""FreeCAD extraction: pull fabricated parts out of the mechanical model.

Runs a script inside the FreeCAD flatpak's headless python (freecadcmd) that
opens the chassis FCStd, finds every PartDesign::Body or App::DocumentObjectGroup
whose label ends with a part number (HW-...), and exports per part:
- <pn>.step   (STEP model, into Mechanical/Fab/<pn>/)
- holes.json  (cylindrical-hole diameter histogram in mm, for spec checking)

The extractor keys on labels only: no translation layer. Rename bodies/groups
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
import Mesh

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
qty = {}
for obj in doc.Objects:
    if obj.TypeId not in ("PartDesign::Body", "App::DocumentObjectGroup"):
        continue
    m = pn_re.search(obj.Label)
    if not m:
        continue
    pn = re.sub(r"([A-Z]+)\d{3}$", r"\1", m.group(1))  # strip instance suffix
    key = "bodies" if obj.TypeId == "PartDesign::Body" else "groups"
    qty.setdefault(pn, {"bodies": 0, "groups": 0})[key] += 1
    if pn in seen:  # instance duplicates (...001, ...002): one part per PN
        continue
    seen.add(pn)
    shapes = [o for o in members(obj) if hasattr(o, "Shape") and not o.Shape.isNull()]
    if not shapes:
        continue
    out_dir = f"{out_root}/{pn}"
    __import__("os").makedirs(out_dir, exist_ok=True)
    Import.export(shapes, f"{out_dir}/{pn}.step")
    Mesh.export(shapes, f"{out_dir}/{pn}.stl")
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
with open(f"{out_root}/model_parts.json", "w") as f:
    json.dump({pn: (q["bodies"] or q["groups"]) for pn, q in sorted(qty.items())},
              f, sort_keys=True)

doc and App.closeDocument(doc.Name)
print("PARTS_JSON=" + json.dumps(sorted(parts)))
"""


def _freecad(args: List[str], timeout: int = 1800) -> Optional[subprocess.CompletedProcess]:
    cmd = ["flatpak", "run", "--command=freecadcmd", "org.freecad.FreeCAD"] + args
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return None


# Runs inside headless Blender. Renders each <pn>.stl under the fab dir from
# two isometric angles: <pn>/info.png (front) and <pn>/info-back.png.
_RENDER_SCRIPT = r"""
import math
import sys
from pathlib import Path

import bpy

fab = Path(sys.argv[sys.argv.index("--") + 1])
ANGLES = [("info.png", 45.0), ("info-back.png", 225.0)]


def render(stl: Path, out: Path, azimuth_deg: float) -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.stl_import(filepath=str(stl))
    obj = bpy.context.selected_objects[0]

    # Center on origin, sit on Z=0.
    import mathutils
    bb = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
    lo = mathutils.Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
    hi = mathutils.Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    center = (lo + hi) / 2
    obj.location -= center
    size = max(hi.x - lo.x, hi.y - lo.y, hi.z - lo.z)

    cam_data = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cam_data)
    bpy.context.collection.objects.link(cam)
    az = math.radians(azimuth_deg)
    el = math.radians(30)
    dist = size * 2.2
    cam.location = (dist * math.cos(el) * math.cos(az),
                    dist * math.cos(el) * math.sin(az),
                    dist * math.sin(el))
    direction = -cam.location.normalized()
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam

    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.rotation_euler = (math.radians(45), 0, math.radians(30))
    bpy.context.collection.objects.link(sun)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.render.resolution_x = 800
    scene.render.resolution_y = 600
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new("world")
    scene.world.color = (1, 1, 1)
    scene.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    print("rendered", out.name)


for part_dir in sorted(fab.iterdir()):
    if not part_dir.is_dir():
        continue
    stls = list(part_dir.glob("*.stl"))
    if not stls:
        continue
    for name, az in ANGLES:
        try:
            render(stls[0], part_dir / name, az)
        except Exception as exc:
            print("render failed", part_dir.name, name, exc)
"""


def render_images(chassis_dir: Path) -> int:
    """Render each fabricated part's STL to info.png (+info-back.png) with
    headless Blender. Returns the number of images rendered."""
    fab_dir = chassis_dir / "Mechanical" / "Fab"
    if not fab_dir.is_dir():
        return 0
    with tempfile.NamedTemporaryFile(
            "w", suffix=".py", dir=chassis_dir, delete=False) as f:
        f.write(_RENDER_SCRIPT)
        script = Path(f.name)
    cmd = ["flatpak", "run", "--command=blender", "org.blender.Blender",
           "-b", "--factory-startup", "-P", str(script), "--", str(fab_dir)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    except FileNotFoundError:
        script.unlink(missing_ok=True)
        return 0
    finally:
        script.unlink(missing_ok=True)
    return r.stdout.count("rendered ")


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
    except subprocess.TimeoutExpired:
        print("  warning: FreeCAD extraction timed out; skipping model "
              "extraction", file=sys.stderr)
        return []
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


# Runs inside freecadcmd. Splits the document's top-level objects into
# subassemblies and exports each as <name>.stl + <name>.step (each object's
# global placement is honored by Mesh.export/Import.export):
# - top-level App::DocumentObjectGroup: one subassembly per group label
# - top-level PartDesign::Body not in a group: one subassembly per body label
# - loose visible Part::Feature instances (e.g. McMaster hardware): one
#   shared "Hardware" subassembly
# The STL (fast) is written before the STEP (slow) per subassembly, so a
# timeout still leaves every completed subassembly on disk.
_ASM_SCRIPT = r"""
import json
import re
import sys

import FreeCAD as App
import Import
import Mesh

fcstd, out_dir = sys.argv[2], sys.argv[3]
doc = App.openDocument(fcstd)

def members(obj):
    if obj.TypeId == "App::DocumentObjectGroup":
        out = []
        for sub in obj.Group:
            out.extend(members(sub))
        return out
    return [obj]

def visible_solids(objs):
    return [o for o in objs
            if hasattr(o, "Shape") and not o.Shape.isNull()
            and o.Shape.Solids
            and getattr(o, "Visibility", True)]

def sanitize(label, fallback):
    name = re.sub(r"_+", "_", re.sub(r"[^A-Za-z0-9._-]", "_", label)).strip("_")
    return name or fallback

# Top-level objects: not referenced by any group (nested groups are reached
# through their top-level parent via members()).
children = set()
for obj in doc.Objects:
    if obj.TypeId == "App::DocumentObjectGroup":
        for sub in obj.Group:
            children.add(sub.Name)
top = [o for o in doc.Objects if o.Name not in children]

subs = []   # (name, shapes)
hardware = []
for obj in top:
    if obj.TypeId == "App::DocumentObjectGroup":
        shapes = visible_solids(members(obj))
        if shapes:
            subs.append((sanitize(obj.Label, obj.Name), shapes))
    elif obj.TypeId == "PartDesign::Body":
        shapes = visible_solids([obj])
        if shapes:
            subs.append((sanitize(obj.Label, obj.Name), shapes))
    elif obj.TypeId == "Part::Feature":
        if visible_solids([obj]):
            hardware.append(obj)
if hardware:
    subs.append(("Hardware", hardware))

__import__("os").makedirs(out_dir, exist_ok=True)
exported = []
used = set()
for name, shapes in subs:
    base = name
    n = 2
    while name in used:
        name = f"{base}_{n}"
        n += 1
    used.add(name)
    Mesh.export(shapes, f"{out_dir}/{name}.stl")
    Import.export(shapes, f"{out_dir}/{name}.step")
    exported.append(name)

doc and App.closeDocument(doc.Name)
print("ASSEMBLY_JSON=" + json.dumps(exported))
"""

# Assembly STEP export can be very slow on large models; give it more room
# than the per-part extraction. On timeout, completed subassemblies are kept.
_ASM_TIMEOUT = 3600


def _assembly_stls(asm_dir: Path) -> List[str]:
    return sorted(p.stem for p in asm_dir.glob("*.stl"))


def export_assembly(chassis_dir: Path) -> List[str]:
    """Export the chassis model as per-subassembly files in Mechanical/Assembly/.

    Writes into the (temp) hardware tree. Returns the names of subassemblies
    whose STL was produced (a subassembly missing its STEP, e.g. after a
    timeout, still counts; the STL is what the viewer needs). Returns [] if
    FreeCAD/FCStd is unavailable or nothing was exported.
    """
    fcstd = find_fcstd(chassis_dir)
    if fcstd is None:
        return []
    asm_dir = chassis_dir / "Mechanical" / "Assembly"
    with tempfile.NamedTemporaryFile(
            "w", suffix=".py", dir=chassis_dir, delete=False) as f:
        f.write(_ASM_SCRIPT)
        script = Path(f.name)
    try:
        r = _freecad([str(script), str(fcstd), str(asm_dir)],
                     timeout=_ASM_TIMEOUT)
    except subprocess.TimeoutExpired:
        done = _assembly_stls(asm_dir)
        if done:
            print(f"  warning: assembly export timed out; keeping "
                  f"{len(done)} completed subassembly(ies)", file=sys.stderr)
            return done
        print("  warning: assembly export timed out before any subassembly "
              "was written", file=sys.stderr)
        return []
    finally:
        script.unlink(missing_ok=True)
    if r is None:
        print("  freecad flatpak not found; skipping assembly export",
              file=sys.stderr)
        return []
    if r.returncode != 0:
        tail = (r.stderr or r.stdout).strip().splitlines()[-3:]
        print(f"  FreeCAD assembly export failed: {tail}", file=sys.stderr)
        return []
    for line in r.stdout.splitlines():
        if line.startswith("ASSEMBLY_JSON="):
            names = json.loads(line[len("ASSEMBLY_JSON="):])
            return [n for n in names
                    if (asm_dir / f"{n}.stl").is_file()]
    return _assembly_stls(asm_dir)


def merge_mcmaster(chassis_dir: Path) -> List[str]:
    """Merge model-harvested McMaster hardware into MechanicalBOM.txt.

    Model instance counts win for modeled parts; lines for parts not in the
    model (consumables, unmodeled hardware) are kept as-is; model-only parts
    are appended. Returns human-readable notes about what changed.
    """
    model_path = chassis_dir / "Mechanical" / "Fab" / "mcmaster_model.json"
    bom_path = chassis_dir / "Mechanical" / "MechanicalBOM.txt"
    if not model_path.is_file() or not bom_path.is_file():
        return []
    model = json.loads(model_path.read_text())
    lines = bom_path.read_text(errors="replace").splitlines()
    header = lines[0] if lines else "Qty,Vendor,PN,Description"
    kept, changed, notes = [], {}, []
    seen = set()
    for line in lines[1:]:
        fields = [f.strip() for f in line.split(",")]
        if len(fields) >= 3 and fields[1].lower() == "mcmaster" and fields[2] in model:
            pn = fields[2]
            qty = model[pn]["qty"]
            if str(qty) != fields[0]:
                notes.append(f"  mcmaster {pn}: qty {fields[0]} -> {qty} (from model)")
            kept.append(f"{qty},McMaster,{pn},{fields[3] if len(fields) > 3 else ''}")
            seen.add(pn)
        else:
            kept.append(line)
    for pn, entry in sorted(model.items()):
        if pn not in seen:
            kept.append(f"{entry['qty']},McMaster,{pn},{entry['description']}")
            notes.append(f"  mcmaster {pn}: added {entry['qty']}x (from model)")
    if notes:
        bom_path.write_text("\n".join([header] + kept) + "\n")
    return notes


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


def check_part_qty(chassis_dir: Path) -> List[str]:
    """Cross-check fabricated-part quantities (info.txt Qty) against the
    model's instance counts (model_parts.json)."""
    model_path = chassis_dir / "Mechanical" / "Fab" / "model_parts.json"
    if not model_path.is_file():
        return []
    model = json.loads(model_path.read_text())
    from .core import parse_info_txt  # lazy: core imports this module lazily
    fab_dir = chassis_dir / "Mechanical" / "Fab"
    warnings = []
    for pn, model_qty in sorted(model.items()):
        info = parse_info_txt(fab_dir / pn / "info.txt")
        if not info.get("Qty"):
            continue
        try:
            bom_qty = int(info["Qty"])
        except ValueError:
            continue
        if bom_qty != model_qty:
            warnings.append(f"  warning: {pn}: info.txt Qty={bom_qty} but "
                            f"{model_qty} instance(s) in the model")
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
