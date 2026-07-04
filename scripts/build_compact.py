"""
build_compact.py — Convert docs/data/repeaters.json into a column-oriented
compact file (docs/data/repeaters.min.json) that the frontend loads first.

The compact format stores field names once and each record as a plain array,
roughly halving the raw size. repeaters.json stays the canonical file used
by all other scripts; run this after any script that rewrites it.

Usage:
    python scripts/build_compact.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "docs" / "data" / "repeaters.json"
OUTPUT = ROOT / "docs" / "data" / "repeaters.min.json"

# Stable column order; frontend expands rows back into objects by this list.
COLS = [
    "id", "callsign", "city", "district", "location",
    "frequency", "offset", "tone", "band", "mode",
    "status", "licensed", "power_w", "altitude_m",
    "lat", "lon", "coord_approx", "ta_region",
    "source", "last_seen", "locator",
]


def main():
    with open(SOURCE, encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("repeaters", [])
    rows = [[r.get(c) for c in COLS] for r in records]

    compact = {
        "updated": data.get("updated"),
        "count": len(rows),
        "cols": COLS,
        "rows": rows,
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(compact, f, ensure_ascii=False, separators=(",", ":"))

    src_kb = SOURCE.stat().st_size / 1024
    out_kb = OUTPUT.stat().st_size / 1024
    print(f"{SOURCE.name}: {src_kb:.0f} KB -> {OUTPUT.name}: {out_kb:.0f} KB "
          f"({len(rows)} records)")


if __name__ == "__main__":
    main()
