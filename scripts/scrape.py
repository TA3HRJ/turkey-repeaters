"""
scrape.py — Fetch repeater data from amatortelsizcilik.com.tr and AKRAD,
normalize into a unified schema, and write docs/data/repeaters.json.

Usage:
    python scripts/scrape.py

Output:
    docs/data/repeaters.json
"""

import json
import sys
import re
from datetime import date
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("Missing dependency: pip install requests")

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("Missing dependency: pip install beautifulsoup4")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "docs" / "data" / "repeaters.json"
OVERRIDES = ROOT / "data" / "overrides.json"

# ---------------------------------------------------------------------------
# Offset calculation (IARU Region 1 standard)
# ---------------------------------------------------------------------------
VHF_OFFSET = -0.600   # MHz
UHF_OFFSET = -7.600   # MHz

def calc_offset(frequency: float, band: str) -> float:
    band = (band or "").upper()
    if band == "VHF":
        return VHF_OFFSET
    if band == "UHF":
        return UHF_OFFSET
    return 0.0


# ---------------------------------------------------------------------------
# Source 1: amatortelsizcilik.com.tr  (JSON endpoint)
# ---------------------------------------------------------------------------
AT_URL = "https://amatortelsizcilik.com.tr/roleler/data.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,tr;q=0.8",
    "Referer": "https://amatortelsizcilik.com.tr/roleler",
}

MODE_MAP = {0: "FM", 1: "DMR", 2: "C4FM", 3: "D-STAR", 4: "NXDN"}

def _safe_float(val) -> float | None:
    if val is None:
        return None
    try:
        return float(str(val).split()[0].replace(",", "."))
    except (ValueError, IndexError):
        return None

def fetch_amatortelsiz() -> list[dict]:
    print(f"[1/2] Fetching {AT_URL} ...")
    resp = requests.get(AT_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    raw = resp.json()

    records = []
    for r in raw:
        digital_code = r.get("digital", 0) or 0
        mode = MODE_MAP.get(digital_code, "FM")
        raw_freq = str(r.get("frekans") or "0").split("-")[0].strip().replace(",", ".")
        try:
            freq = float(raw_freq)
        except ValueError:
            freq = 0.0
        band = (r.get("bant") or "").upper()
        offset = calc_offset(freq, band)

        records.append({
            "id":           f"AT_{r['id']}",
            "callsign":     "",                        # not in source
            "city":         (r.get("sehir") or "").title(),
            "district":     (r.get("ilce") or "").title() or None,
            "location":     r.get("konum") or "",
            "frequency":    freq,
            "offset":       offset,
            "tone":         _safe_float(r.get("ton")),
            "band":         band,
            "mode":         mode,
            "status":       bool(r.get("durum")),
            "licensed":     bool(r.get("ruhsat")),
            "power_w":      r.get("guc"),
            "altitude_m":   r.get("yukseklik"),
            "lat":          float(r["lat"]) if r.get("lat") else None,
            "lon":          float(r["lon"]) if r.get("lon") else None,
            "ta_region":    r.get("tabolge") or "",
            "source":       "amatortelsizcilik.com.tr",
            "last_seen":    str(date.today()),
        })
    print(f"    -> {len(records)} records")
    return records


# ---------------------------------------------------------------------------
# Source 2: akrad.org.tr  (HTML table)
# ---------------------------------------------------------------------------
AKRAD_URL = "https://www.akrad.org.tr/turkiye-geneli-role-listesi/"

def fetch_akrad() -> list[dict]:
    print(f"[2/2] Fetching {AKRAD_URL} ...")
    resp = requests.get(AKRAD_URL, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    records = []
    tables = soup.find_all("table")
    if not tables:
        print("    ! No tables found on AKRAD page — skipping")
        return records

    # Use the largest table
    table = max(tables, key=lambda t: len(t.find_all("tr")))
    rows = table.find_all("tr")

    # Try to detect header row
    header_row = rows[0] if rows else None
    headers = []
    if header_row:
        headers = [th.get_text(strip=True).lower() for th in header_row.find_all(["th", "td"])]

    # Expected columns (flexible match)
    def col(row_cells, name_candidates):
        for name in name_candidates:
            for i, h in enumerate(headers):
                if name in h and i < len(row_cells):
                    return row_cells[i].get_text(strip=True)
        return ""

    idx = 0
    for row in rows[1:]:
        cells = row.find_all("td")
        if not cells:
            continue
        raw_freq = col(cells, ["frekans", "freq"])
        if not raw_freq:
            continue
        # Clean frequency
        freq_str = re.sub(r"[^\d.,]", "", raw_freq).replace(",", ".")
        try:
            freq = float(freq_str)
        except ValueError:
            continue

        band = col(cells, ["band", "bant"]).upper()
        if not band:
            band = "VHF" if freq < 300 else "UHF"

        tone_str = col(cells, ["tone", "ton", "ctcss"])
        try:
            tone = float(tone_str.replace(",", ".")) if tone_str and tone_str.lower() not in ("yok", "-", "") else None
        except ValueError:
            tone = None

        callsign = col(cells, ["çağrı", "cagri", "callsign", "istasyon"])
        city = col(cells, ["ili", "şehir", "sehir", "il"]).title()
        location = col(cells, ["yeri", "konum", "lokasyon"])
        locator = col(cells, ["locator"])

        idx += 1
        records.append({
            "id":           f"AK_{idx}",
            "callsign":     callsign,
            "city":         city,
            "district":     None,
            "location":     location,
            "frequency":    freq,
            "offset":       calc_offset(freq, band),
            "tone":         tone,
            "band":         band,
            "mode":         "FM",
            "status":       True,          # AKRAD doesn't indicate status
            "licensed":     None,
            "power_w":      None,
            "altitude_m":   None,
            "lat":          None,
            "lon":          None,
            "ta_region":    "",
            "locator":      locator,
            "source":       "akrad.org.tr",
            "last_seen":    str(date.today()),
        })
    print(f"    -> {len(records)} records")
    return records


# ---------------------------------------------------------------------------
# Merge: deduplicate by frequency+city, AT is primary, AKRAD fills callsign
# ---------------------------------------------------------------------------
def merge(at_records: list[dict], akrad_records: list[dict]) -> list[dict]:
    print("[merge] Deduplicating ...")

    # Index AKRAD by (rounded_freq, city) for callsign lookup
    akrad_index: dict[tuple, dict] = {}
    for r in akrad_records:
        key = (round(r["frequency"], 3), r["city"].lower())
        akrad_index[key] = r

    merged = []
    for r in at_records:
        key = (round(r["frequency"], 3), r["city"].lower())
        akrad_match = akrad_index.get(key)
        if akrad_match:
            if not r["callsign"]:
                r["callsign"] = akrad_match.get("callsign", "")
            if not r.get("locator"):
                r["locator"] = akrad_match.get("locator", "")
            akrad_index.pop(key)   # mark as matched
        merged.append(r)

    # Add remaining AKRAD-only records
    for r in akrad_index.values():
        merged.append(r)

    print(f"    -> {len(merged)} total records after merge")
    return merged


# ---------------------------------------------------------------------------
# Apply overrides (from RepeaterBook CSV import or manual edits)
# ---------------------------------------------------------------------------
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
            # New record from RepeaterBook
            records.append(ov)

    return records


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    at_records = fetch_amatortelsiz()
    akrad_records = fetch_akrad()
    records = merge(at_records, akrad_records)
    records = apply_overrides(records)

    output = {
        "updated":  str(date.today()),
        "count":    len(records),
        "repeaters": records,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nDone. {len(records)} repeaters written to {OUTPUT}")


if __name__ == "__main__":
    main()
