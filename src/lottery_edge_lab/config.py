from __future__ import annotations

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent.parent.parent
DATA_ROOT = PROJECT_ROOT / "data"
RAW_ROOT = DATA_ROOT / "raw"
NORMALIZED_ROOT = DATA_ROOT / "normalized"
PROCESSED_ROOT = DATA_ROOT / "processed"

for path in (RAW_ROOT, NORMALIZED_ROOT, PROCESSED_ROOT):
    path.mkdir(parents=True, exist_ok=True)
