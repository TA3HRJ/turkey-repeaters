"""
merge_repeaterbook.py — Import a RepeaterBook CSV export and merge it into
the overrides file (data/overrides.json).  Run this after downloading a
fresh CSV from repeaterbook.com.

Usage:
    python scripts/merge_repeaterbook.py path/to/repeaterbook_export.csv

The script matches records by (frequency, city).  Matching records are
updated; new records are added.  The result is saved to data/overrides.json
and will be applied on the next run of scrape.py.
"""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OVERRIDES = ROOT / "data" / "overrides.json"

# RepeaterBook CSV column names (generic/international export)
# Adjust if your export uses different headers.
COL_MAP = {
    "Frequency":    "frequency",
    "Duplex":       "_duplex",    # + / - / off
    "Offset":       "_raw_offset",
    "Tone":         "_tone_mode", # Tone / TSQL / DCS / ""
    "rToneFreq":    "tone",
    "cToneFreq":    "_ctone",
    "DtcsCode":     "_dtcs",
    "Mode":         "mode",
    "Name":         "location",
    "Comment":      "_comment",
}

# RepeaterBook "State" column contains the city for international exports
CITY_COLS = ["Nearest City", "State", "County"]
CALL_COLS = ["Call", "Callsign"]


def load_overrides() -> list[dict]:
    if OVERRIDES.exists():
        with open(OVERRIDES, encoding="utf-8") as f:
            return json.load(f)
    return []


def parse_offset(duplex: str, raw_offset: str, frequency: float) -> float:
    try:
        offset_val = float(raw_offset)
    except (ValueError, TypeError):
        offset_val = 0.0
    if duplex == "-":
        return -abs(offset_val)
    if duplex == "+":
        return abs(offset_val)
    return 0.0


def import_csv(csv_path: Path) -> list[dict]:
    records = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []

        city_col = next((c for c in CITY_COLS if c in headers), None)
        call_col = next((c for c in CALL_COLS if c in headers), None)

        for i, row in enumerate(reader):
            freq_str = row.get("Frequency", "").strip()
            try:
                freq = float(freq_str)
            except ValueError:
                continue

            duplex = row.get("Duplex", "").strip()
            raw_offset = row.get("Offset", "").strip()
            offset = parse_offset(duplex, raw_offset, freq)

            tone_str = row.get("rToneFreq", row.get("cToneFreq", "")).strip()
            try:
                tone = float(tone_str) if tone_str and tone_str != "88.5" else (88.5 if tone_str == "88.5" else None)
            except ValueError:
                tone = None
            # Re-parse cleanly
            try:
                tone = float(tone_str) if tone_str else None
            except ValueError:
                tone = None

            city = row.get(city_col, "").strip().title() if city_col else ""
            callsign = row.get(call_col, "").strip().upper() if call_col else ""
            location = row.get("Name", "").strip()
            mode = row.get("Mode", "FM").strip().upper()
            comment = row.get("Comment", "").strip()

            band = "VHF" if freq < 300 else "UHF"

            status_str = comment.lower() if comment else ""
            status = not any(x in status_str for x in ["off", "inactive", "closed"])

            records.append({
                "id":          f"RB_{i+1}",
                "callsign":    callsign,
                "city":        city,
                "district":    None,
                "location":    location,
                "frequency":   freq,
                "offset":      offset,
                "tone":        tone,
                "band":        band,
                "mode":        mode,
                "status":      status,
                "licensed":    None,
                "power_w":     None,
                "altitude_m":  None,
                "lat":         None,
                "lon":         None,
                "ta_region":   "",
                "source":      "repeaterbook.com",
                "last_seen":   str(__import__("datetime").date.today()),
            })
    return records


def merge_into_overrides(new_records: list[dict], existing: list[dict]) -> list[dict]:
    # Index existing overrides by (freq, city)
    index: dict[tuple, int] = {}
    for i, r in enumerate(existing):
        key = (round(r.get("frequency", 0), 3), (r.get("city") or "").lower())
        index[key] = i

    added = updated = 0
    for r in new_records:
        key = (round(r["frequency"], 3), r["city"].lower())
        if key in index:
            existing[index[key]].update(r)
            updated += 1
        else:
            existing.append(r)
            added += 1

    print(f"    RepeaterBook import: {updated} updated, {added} added")
    return existing


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python scripts/merge_repeaterbook.py <path_to_csv>")

    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        sys.exit(f"File not found: {csv_path}")

    print(f"Importing {csv_path.name} ...")
    new_records = import_csv(csv_path)
    print(f"    Parsed {len(new_records)} records from CSV")

    existing = load_overrides()
    merged = merge_into_overrides(new_records, existing)

    OVERRIDES.parent.mkdir(parents=True, exist_ok=True)
    with open(OVERRIDES, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(merged)} override records to {OVERRIDES}")
    print("Run 'python scripts/scrape.py' to rebuild repeaters.json")


if __name__ == "__main__":
    main()
