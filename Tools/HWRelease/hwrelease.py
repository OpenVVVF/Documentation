#!/usr/bin/env python3
"""hwrelease - hardware release exporter.

Usage:
    python3 hwrelease.py update [--tag TAG] [--force]
    python3 hwrelease.py list
    python3 hwrelease.py show HW-C2-PCB-CTRL-A

If the repository .venv exists, the tool re-executes itself with the venv's
python so dependencies (PyYAML) are available regardless of the system python.
"""

import os
import sys
from pathlib import Path

_VENV_PY = Path(__file__).resolve().parents[2] / ".venv" / "bin" / "python"

if _VENV_PY.is_file() and Path(sys.executable) != _VENV_PY:
    os.execv(str(_VENV_PY), [str(_VENV_PY)] + sys.argv)

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hwrelease.cli import main

if __name__ == "__main__":
    sys.exit(main())
