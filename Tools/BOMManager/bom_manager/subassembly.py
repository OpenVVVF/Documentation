"""Per-subassembly price breakdowns, written as Subassembly_Pricing.json.

Each BOM line carries per-source quantities (BomLine.source_qty); sources map
to subassemblies — one per board, plus shared groups for wiring harnesses,
mechanical hardware, and fabricated/printed parts. Totals re-apply pack
rounding per (line, source) pair, i.e. they are the cost of ordering only
that subassembly, so their sum can exceed the consolidated-BOM total.
"""

import json
import math
import re
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from .bom import BomLine

OUTPUT_NAME = "Subassembly_Pricing.json"

# Display names for boards whose CamelCase splits poorly or reads oddly.
FRIENDLY_BOARD_NAMES = {
    "ControlBoard": "Control Board",
    "IOBoard": "IO Board",
    "GateDriver": "Gate Driver",
    "DCBusCapacitorBoard": "DC-Link Capacitor Board",
    "DCBusFilter": "DC-Link Filter Board",
}

HARNESS_GROUP = ("wiring-harnesses", "Wiring Harnesses")
MECHANICAL_GROUP = ("mechanical-hardware", "Mechanical Hardware")
FABRICATED_GROUP = ("fabricated-printed-parts", "Fabricated / Printed Parts")


def _fmt(amount: float) -> str:
    """Money as a plain 2-decimal string (no thousand separators, easy parsing)."""
    return f"{amount:.2f}"


def _camel_split(name: str) -> str:
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", name)  # IOBoard -> IO Board
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", s)    # MainBoard -> Main Board


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def source_categories(items) -> Dict[str, str]:
    """Map 'chassis/source' labels to the parser category of the source.

    A label can appear with two categories (board components + its pcb_fab
    line, harness components + its harness_asm line); both classify into the
    same subassembly, so first-seen is fine.
    """
    out: Dict[str, str] = {}
    for item in items:
        out.setdefault(f"{item.chassis}/{item.source}", item.category)
    return out


def group_for(source: str, category: str, line_type: str) -> Tuple[str, str]:
    """(slug, display name) of the subassembly a (line, source) pair belongs to."""
    if line_type == "3dprint" or category in ("custom", "sendcutsend_folder"):
        return FABRICATED_GROUP
    if category in ("harness", "harness_asm"):
        return HARNESS_GROUP
    if category == "mechanical":
        return MECHANICAL_GROUP
    # Board components and the board's pcb_fab line; also the fallback for
    # unknown sources: camel-split the source name.
    name = FRIENDLY_BOARD_NAMES.get(source) or _camel_split(source)
    return _slug(name), name


def distribute(total: int, weights: Dict[str, int]) -> Dict[str, int]:
    """Largest-remainder split of `total` across labels, proportional to weights.

    Used to spread a spares-tier line total over its per-source quantities so
    the parts sum back to exactly the tier quantity.
    """
    labels = sorted(weights)
    base = sum(weights.values())
    if total <= 0 or base <= 0:
        return {k: 0 for k in labels}
    exact = {k: total * weights[k] / base for k in labels}
    out = {k: int(math.floor(exact[k])) for k in labels}
    by_remainder = sorted(labels, key=lambda k: (out[k] - exact[k], k))
    for k in by_remainder[: total - sum(out.values())]:
        out[k] += 1
    return out


def build_pricing(
    chassis: str,
    variant: str,
    qty: int,
    line_entries: List[Tuple[BomLine, Optional[float]]],
    categories: Dict[str, str],
    need_fn: Optional[Callable[[BomLine, Optional[float]], Dict[str, int]]] = None,
) -> dict:
    """Build the Subassembly_Pricing.json document for one output.

    line_entries: (line, unit price or None) pairs. need_fn overrides the
    per-source need (default: base source quantities scaled by qty); spares
    tiers pass one that distributes their adjusted quantity across sources.
    """
    subs: Dict[str, dict] = {}
    unpriced = 0
    for line, unit in line_entries:
        needs = need_fn(line, unit) if need_fn else {
            label: n * qty for label, n in line.source_qty.items()
        }
        vendor = line.primary_vendor() or "unknown"
        packed = line.pack_size and line.pack_size > 1
        # Unit price in the JSON is per piece; vendor prices for packed parts
        # are per pack, so effective per-piece = pack price / pack size and
        # total = order pieces x per-piece price, equal to packs x pack price.
        per_piece = unit / line.pack_size if (unit is not None and packed) else unit
        for label, need in sorted(needs.items()):
            source = label.split("/", 1)[-1]
            slug, name = group_for(source, categories.get(label, ""), line.type)
            sub = subs.setdefault(slug, {"name": name, "total": 0.0, "vendors": {}, "lines": []})
            order = line.pieces_ordered(need)
            if per_piece is None:
                unpriced += 1
                amount = 0.0
            else:
                amount = round(per_piece * order, 2)
            sub["total"] += amount
            sub["vendors"][vendor] = sub["vendors"].get(vendor, 0.0) + amount
            sub["lines"].append({
                "pn": line.internal_pn,
                "description": line.description,
                "qty": need,
                "order_qty": order,
                "unit": None if per_piece is None else _fmt(per_piece),
                "total": _fmt(amount),
                "vendor": vendor,
                "vendor_pn": line.vendor_part_number(vendor),
            })
    doc_subs = {}
    grand = 0.0
    for slug in sorted(subs):
        sub = subs[slug]
        grand += sub["total"]
        sub["lines"].sort(key=lambda l: (l["vendor"], l["description"].lower()))
        doc_subs[slug] = {
            "name": sub["name"],
            "total": _fmt(sub["total"]),
            "vendors": {v: _fmt(sub["vendors"][v]) for v in sorted(sub["vendors"])},
            "lines": sub["lines"],
        }
    return {
        "chassis": chassis,
        "variant": variant,
        "qty": qty,
        "subassemblies": doc_subs,
        "total": _fmt(grand),
        "unpriced": unpriced,
    }


def write_pricing_json(doc: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")

