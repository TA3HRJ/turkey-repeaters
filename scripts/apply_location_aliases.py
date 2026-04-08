"""
apply_location_aliases.py — Apply reviewed location aliases to overrides.json.

Usage:
    1. Run find_similar_locations.py to generate data/location_aliases_draft.json
    2. Edit the draft — set correct 'canonical' for each group, delete groups you don't want
    3. Run this script: python scripts/apply_location_aliases.py
    4. Run scrape.py to rebuild repeaters.json

The script adds/updates override records for all variants,
setting their 'location' to the canonical value.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFT = ROOT / "data" / "location_aliases_draft.json"
OVERRIDES = ROOT / "data" / "overrides.json"

def main():
    if not DRAFT.exists():
        print("Draft not found. Run find_similar_locations.py first.")
        return

    with open(DRAFT, encoding="utf-8") as f:
        groups = json.load(f)

    with open(OVERRIDES, encoding="utf-8") as f:
        overrides = json.load(f)

    # Index existing overrides by id
    ov_index = {o["id"]: i for i, o in enumerate(overrides)}

    applied = 0
    for group in groups:
        canonical = group["canonical"]
        records_map = group.get("records", {})
        for variant, records in records_map.items():
            if variant == canonical:
                continue  # no change needed
            for rec in records:
                rid = rec["id"]
                if rid in ov_index:
                    overrides[ov_index[rid]]["location"] = canonical
                else:
                    overrides.append({"id": rid, "location": canonical})
                    ov_index[rid] = len(overrides) - 1
                applied += 1

    with open(OVERRIDES, "w", encoding="utf-8") as f:
        json.dump(overrides, f, ensure_ascii=False, indent=2)

    print(f"Applied {applied} location fixes to {OVERRIDES}")
    print("Run 'python scripts/scrape.py' to rebuild repeaters.json")

if __name__ == "__main__":
    main()
