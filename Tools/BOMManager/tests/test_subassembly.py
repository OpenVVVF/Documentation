"""Per-subassembly pricing: source grouping, pack math, Subassembly_Pricing.json."""

import json
import re

from bom_manager import generate
from bom_manager.bom import BomLine, aggregate_bom
from bom_manager.db import PartDatabase
from bom_manager.parsers import LineItem
from bom_manager.pricing import PriceInfo
from bom_manager.subassembly import (
    FABRICATED_GROUP,
    HARNESS_GROUP,
    MECHANICAL_GROUP,
    build_pricing,
    distribute,
    group_for,
    source_categories,
)
from conftest import make_chassis


def _register_descriptors(ctx):
    ctx.descriptor_registry.set("Chassis1", "pcb", "MainBoard", "MAIN")
    ctx.descriptor_registry.set("Chassis1", "wiring", "GDHarness", "GDH")


def _seed_prices(ctx):
    """Price the mouser resistor (pack of 25) and cap, plus the McMaster screw."""
    ctx.db.add("R_1210_3225Metric", "10k", {
        "description": "Resistor 10k", "type": "resistor", "pack_size": 25,
        "mouser_part": "RES10K",
    })
    ctx.db.add("C_1210_3225Metric", "100nF 100V", {
        "description": "Capacitor 100nF 100V", "type": "capacitor",
        "mouser_part": "CAP100N",
    })
    ctx.cache.set(PriceInfo(vendor="mouser", part_number="RES10K", unit_price=5.00))  # per pack
    ctx.cache.set(PriceInfo(vendor="mouser", part_number="CAP100N", unit_price=0.10))
    ctx.cache.set(PriceInfo(vendor="mcmaster", part_number="94669A199", unit_price=1.50))


class TestGrouping:
    def test_known_boards_have_friendly_names(self):
        assert group_for("ControlBoard", "board", "chip") == ("control-board", "Control Board")
        assert group_for("IOBoard", "board", "chip") == ("io-board", "IO Board")
        assert group_for("GateDriver", "board", "chip") == ("gate-driver", "Gate Driver")
        assert group_for("DCBusCapacitorBoard", "board", "capacitor") == \
            ("dc-link-capacitor-board", "DC-Link Capacitor Board")
        assert group_for("DCBusFilter", "board", "other") == ("dc-link-filter-board", "DC-Link Filter Board")

    def test_unknown_board_camel_split(self):
        assert group_for("MainBoard", "board", "resistor") == ("main-board", "Main Board")
        assert group_for("DCBusCapacitorBank", "board", "capacitor") == \
            ("dc-bus-capacitor-bank", "DC Bus Capacitor Bank")

    def test_fixed_groups(self):
        assert group_for("GDHarness", "harness", "wiring") == HARNESS_GROUP
        assert group_for("GDHarness", "harness_asm", "wiring") == HARNESS_GROUP
        assert group_for("MechanicalBOM", "mechanical", "mechanical") == MECHANICAL_GROUP
        assert group_for("HW-C1-PLATE-A", "sendcutsend_folder", "plate") == FABRICATED_GROUP
        assert group_for("MainBoard", "board", "3dprint") == FABRICATED_GROUP

    def test_pcb_fab_folds_into_board(self):
        assert group_for("MainBoard", "pcb_fab", "pcb") == ("main-board", "Main Board")


class TestPerSourceQty:
    def test_shared_pn_splits_by_source(self, tmp_path):
        db = PartDatabase(tmp_path / "db.json")
        items = [
            LineItem(chassis="Chassis1", source="MainBoard", category="board",
                     footprint="McMaster", designation="94669A199", quantity=2, vendor_hint="mcmaster"),
            LineItem(chassis="Chassis1", source="MechanicalBOM", category="mechanical",
                     footprint="McMaster", designation="94669A199", quantity=12, vendor_hint="mcmaster"),
        ]
        lines = aggregate_bom(iter(items), db)
        assert len(lines) == 1
        assert lines[0].quantity == 14
        assert lines[0].source_qty == {"Chassis1/MainBoard": 2, "Chassis1/MechanicalBOM": 12}

        doc = build_pricing("Chassis1", "base", 1, [(lines[0], 1.50)], source_categories(items))
        board_line = doc["subassemblies"]["main-board"]["lines"][0]
        mech_line = doc["subassemblies"]["mechanical-hardware"]["lines"][0]
        assert (board_line["qty"], board_line["total"]) == (2, "3.00")
        assert (mech_line["qty"], mech_line["total"]) == (12, "18.00")
        assert doc["total"] == "21.00"

    def test_distribute_sums_to_total(self):
        assert distribute(0, {}) == {}
        out = distribute(7, {"a": 1, "b": 1, "c": 1})
        assert sum(out.values()) == 7
        assert out == {"a": 3, "b": 2, "c": 2}  # largest remainder, deterministic
        assert distribute(4, {"a": 0, "b": 5}) == {"a": 0, "b": 4}

    def test_pack_rounding_per_subassembly(self):
        line = BomLine(key="k", footprint="R_1210_3225Metric", designation="10k",
                       description="Resistor 10k", customer_part="", quantity=3,
                       type="resistor", pack_size=25, mouser_part="RES10K",
                       source_qty={"Chassis1/MainBoard": 2, "Chassis1/OtherBoard": 1})
        doc = build_pricing("Chassis1", "base", 1, [(line, 5.00)], {})
        # Each source rounds up to its own pack of 25: 25 x $0.20/piece = $5.00.
        for slug in ("main-board", "other-board"):
            sub = doc["subassemblies"][slug]
            assert sub["lines"][0]["order_qty"] == 25
            assert sub["lines"][0]["unit"] == "0.20"
            assert sub["total"] == "5.00"
        assert doc["total"] == "10.00"


class TestGenerateRun:
    def test_subassembly_pricing_json_outputs(self, ctx):
        make_chassis(ctx.hardware_root)
        _register_descriptors(ctx)
        _seed_prices(ctx)
        assert generate.run(["--chassis", "Chassis1", "--no-prompt", "--no-pcb-zips",
                             "--variants"], ctx) == 0
        fab_dir = ctx.hardware_root / "Chassis1" / "FabricationData"

        root = json.loads((fab_dir / "Subassembly_Pricing.json").read_text())
        assert root["chassis"] == "Chassis1"
        assert root["variant"] == "base"
        assert root["qty"] == 1
        assert set(root["subassemblies"]) >= {
            "main-board", "mechanical-hardware", "fabricated-printed-parts", "wiring-harnesses"}

        board = root["subassemblies"]["main-board"]
        assert board["name"] == "Main Board"
        res = next(l for l in board["lines"] if l["description"] == "Resistor 10k")
        assert (res["qty"], res["order_qty"], res["unit"], res["total"], res["vendor"]) == \
            (2, 25, "0.20", "5.00", "mouser")
        cap = next(l for l in board["lines"] if l["description"] == "Capacitor 100nF 100V")
        assert (cap["qty"], cap["order_qty"], cap["total"]) == (1, 1, "0.10")
        assert board["total"] == "5.10"
        assert board["vendors"] == {"mouser": "5.10", "pcb": "0.00"}

        mech = root["subassemblies"]["mechanical-hardware"]
        assert mech["vendors"]["mcmaster"] == "18.00"  # 12 x $1.50

        fab = root["subassemblies"]["fabricated-printed-parts"]
        assert fab["total"] == "101.42"  # qty 2 x $50.71 (info.txt UnitPrice)

        # Totals reconcile: per-entry and per-subassembly sums equal the top total.
        total = sum(float(s["total"]) for s in root["subassemblies"].values())
        assert f"{total:.2f}" == root["total"]
        unpriced = sum(1 for s in root["subassemblies"].values()
                       for l in s["lines"] if l["unit"] is None)
        assert root["unpriced"] == unpriced >= 1

        # Spares tiers and build variants get their own JSONs.
        std = json.loads((fab_dir / "BOMs/Variants/standard/Subassembly_Pricing.json").read_text())
        assert std["variant"] == "standard"
        assert json.loads((fab_dir / "BOMs/Variants/generous/Subassembly_Pricing.json")
                          .read_text())["variant"] == "generous"
        # Standard tier: cheap cap gets 1+2 = 3; mcmaster screw is medium -> unchanged.
        std_cap = next(l for l in std["subassemblies"]["main-board"]["lines"]
                       if l["description"] == "Capacitor 100nF 100V")
        assert (std_cap["qty"], std_cap["total"]) == (3, "0.30")
        std_screw = next(l for l in std["subassemblies"]["mechanical-hardware"]["lines"]
                         if l["vendor"] == "mcmaster")
        assert (std_screw["qty"], std_screw["total"]) == (12, "18.00")

        alt = json.loads((fab_dir / "Builds/alt/Subassembly_Pricing.json").read_text())
        assert alt["variant"] == "alt"
        assert "fabricated-printed-parts" not in alt["subassemblies"]  # plate excluded
        assert any(l["description"] == "220nF 100V"
                   for l in alt["subassemblies"]["main-board"]["lines"])

        # The generated .gitignore keeps the JSONs trackable.
        gitignore = (fab_dir / ".gitignore").read_text()
        assert "!Subassembly_Pricing.json" in gitignore and "!*/" in gitignore

    def test_report_has_subassembly_section_and_hwrelease_regexes_still_parse(self, ctx):
        make_chassis(ctx.hardware_root)
        _register_descriptors(ctx)
        _seed_prices(ctx)
        assert generate.run(["--chassis", "Chassis1", "--no-prompt", "--no-pcb-zips"], ctx) == 0
        report = (ctx.hardware_root / "Chassis1/FabricationData/Pricing_Report.md").read_text()

        section = report.index("## Subassembly Totals")
        grand = report.index("## Grand Total")
        assert section < grand
        table = report[section:grand]
        assert "| Main Board |" in table
        assert "Mouser" in table.splitlines()[2]  # vendor column headers

        # hwrelease/core.py parse_price_estimate regexes still match.
        subs = re.findall(r"\*\*(.+?) subtotal:\*\* \$([\d,]+\.\d\d)", report)
        assert ("Mouser", "5.10") in subs and ("McMaster-Carr", "18.00") in subs
        m = re.search(r"Grand Total \((\d+) unit.*?\$([\d,]+\.\d\d)", report)
        assert m and m.group(1) == "1" and float(m.group(2)) > 0
