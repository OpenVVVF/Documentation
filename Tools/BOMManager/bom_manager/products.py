"""Product-line registry loader.

Reads Config/Products.yaml at the repository root and exposes the hardware
roots, chassis definitions, and application profiles to the rest of the tool.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


def repo_root() -> Path:
    """Return the repository root (Documentation/).

    This module lives at Tools/BOMManager/bom_manager/products.py, so the
    repo root is four parents up.
    """
    return Path(__file__).resolve().parent.parent.parent.parent


def products_path() -> Path:
    return repo_root() / "Config" / "Products.yaml"


def data_dir() -> Path:
    """Return the shared data directory at the repo root."""
    return repo_root() / "Data" / "Parts"


def load_products() -> Dict[str, Any]:
    """Load the product registry from Config/Products.yaml."""
    path = products_path()
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def hardware_roots() -> List[Path]:
    """Return resolved hardware root directories."""
    cfg = load_products()
    roots = cfg.get("hardware_roots", [])
    resolved = []
    for r in roots:
        p = Path(r)
        if not p.is_absolute():
            p = repo_root() / p
        resolved.append(p.resolve())
    return resolved


def chassis_config(name: str) -> Optional[Dict[str, Any]]:
    """Return configuration for a chassis directory basename (e.g. 'Chassis2')."""
    cfg = load_products()
    return cfg.get("chassis", {}).get(name)


def list_chassis() -> List[str]:
    """Return registered chassis directory basenames in sorted order."""
    cfg = load_products()
    return sorted(cfg.get("chassis", {}).keys())


def chassis_dir(name: str, hardware_root: Optional[Path] = None) -> Optional[Path]:
    """Return the resolved path to a chassis directory, if it exists."""
    roots = [hardware_root] if hardware_root else hardware_roots()
    for root in roots:
        candidate = root / name
        if candidate.is_dir():
            return candidate.resolve()
    return None


def chassis_short_code(name: str) -> str:
    """Return the configured short code for a chassis, or abbreviate the name."""
    cfg = chassis_config(name)
    if cfg and cfg.get("short_code"):
        return cfg["short_code"]
    # Fallback for unregistered chassis directories.
    import re

    m = re.match(r"chassis\s*(\d+)", name, re.IGNORECASE)
    if m:
        return f"C{m.group(1)}"
    return name.upper()[:6]


def control_module() -> Optional[Dict[str, Any]]:
    """Return the control module definition."""
    return load_products().get("control_module")


def application_profiles() -> Dict[str, Dict[str, Any]]:
    """Return registered application profiles keyed by identifier."""
    return load_products().get("application_profiles", {})
