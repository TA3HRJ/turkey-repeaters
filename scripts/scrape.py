"""
scrape.py — Rebuild docs/data/repeaters.json from the existing data file
and apply any overrides from data/overrides.json.

External scraping has been disabled. The database is now manually maintained.

Usage:
    python scripts/scrape.py
"""

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "docs" / "data" / "repeaters.json"
OVERRIDES = ROOT / "data" / "overrides.json"


def apply_overrides(records: list[dict]) -> list[dict]:
    if not OVERRIDES.exists():
        return records
    with open(OVERRIDES, encoding="utf-8") as f:
        overrides = json.load(f)
    if not overrides:
        return records
    print(f"[override] Applying {len(overrides)} override(s) ...")
    index = {r["id"]: i for i, r in enumerate(records)}
    for ov in overrides:
        ov_id = ov.get("id")
        if ov_id and ov_id in index:
            records[index[ov_id]].update(ov)
        else:
            records.append(ov)
    return records


def main():
    if not OUTPUT.exists():
        sys.exit(f"ERROR: {OUTPUT} not found. Nothing to rebuild.")

    with open(OUTPUT, encoding="utf-8") as f:
        d = json.load(f)

    records = d.get("repeaters", [])
    print(f"Loaded {len(records)} records from {OUTPUT}")

    records = apply_overrides(records)

    output = {
        "updated":   str(date.today()),
        "count":     len(records),
        "repeaters": records,
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Done. {len(records)} repeaters written to {OUTPUT}")

    import build_compact
    build_compact.main()


if __name__ == "__main__":
    main()
