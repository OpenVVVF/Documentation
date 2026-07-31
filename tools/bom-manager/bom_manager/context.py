"""Shared application context: config, databases, registries, vendor clients.

Every command (interactive shell or one-shot) uses a single Context built by
build_context() instead of re-constructing the same objects per script.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from . import products
from .config import Config
from .db import Inventory, PartDatabase
from .descriptor_registry import DescriptorRegistry
from .part_numbers import PartNumberRegistry
from .pricing import PriceCache
from .vendors import DigiKeyClient, McMasterClient, MouserClient, OctopartClient


@dataclass
class Context:
    """Everything a BOM Manager command needs, built once and shared."""

    root: Path
    hardware_root: Path
    config: Config
    db: PartDatabase
    cache: PriceCache
    inventory: Inventory
    pn_registry: PartNumberRegistry
    descriptor_registry: DescriptorRegistry
    mouser: MouserClient
    digikey: DigiKeyClient
    octopart: OctopartClient
    mcmaster: McMasterClient

    @property
    def data_dir(self) -> Path:
        return products.data_dir()


def build_context(
    hardware_root: Optional[Path] = None,
    allow_prompt: bool = True,
) -> Context:
    # Package root is tools/bom-manager; repo root is the Documentation/ hub.
    root = Path(__file__).resolve().parent.parent
    repo = products.repo_root()

    if hardware_root:
        hw_root = Path(hardware_root).resolve()
    else:
        # Default to the first configured hardware root, falling back to the
        # parent of the package root for backward compatibility.
        configured = products.hardware_roots()
        hw_root = configured[0] if configured else root.parent

    config = Config(root / "config.yaml")
    data = products.data_dir()
    db = PartDatabase(data / "database.json")
    cache = PriceCache(data / "price-cache.json")
    inventory = Inventory(data / "inventory.json")
    pn_format = config.get("part_number.format", PartNumberRegistry.DEFAULT_FORMAT)
    pn_registry = PartNumberRegistry(data / "numbers.json", format=pn_format)
    descriptor_registry = DescriptorRegistry(
        data / "descriptors.json", allow_prompt=allow_prompt
    )

    mouser = MouserClient(config.get("mouser.api_key"))
    digikey = DigiKeyClient(
        config.get("digikey.client_id"),
        config.get("digikey.client_secret"),
        sandbox=bool(config.get("digikey.sandbox", False)),
    )
    octopart = OctopartClient(config.get("octopart.api_key"))
    cert_path = config.get("mcmaster.cert_path")
    mcmaster = McMasterClient(
        username=config.get("mcmaster.username"),
        password=config.get("mcmaster.password"),
        cert_path=Path(cert_path) if cert_path else None,
        cert_password=config.get("mcmaster.cert_password") or None,
        use_scrape=True,
    )

    return Context(
        root=root,
        hardware_root=hw_root,
        config=config,
        db=db,
        cache=cache,
        inventory=inventory,
        pn_registry=pn_registry,
        descriptor_registry=descriptor_registry,
        mouser=mouser,
        digikey=digikey,
        octopart=octopart,
        mcmaster=mcmaster,
    )
