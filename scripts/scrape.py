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
# City center coordinates (approximate) — used when source has no GPS data
# ---------------------------------------------------------------------------
CITY_COORDS: dict[str, tuple[float, float]] = {
    # norm_city -> (lat, lon)
    "adana":(37.00,35.32),"adiyaman":(37.76,38.28),"afyonkarahisar":(38.76,30.54),
    "afyon":(38.76,30.54),"agri":(39.72,43.05),"amasya":(40.65,35.83),
    "ankara":(39.93,32.86),"antalya":(36.90,30.70),"artvin":(41.18,41.82),
    "aydin":(37.85,27.85),"balikesir":(39.65,27.88),"bilecik":(40.15,29.98),
    "bingol":(38.88,40.50),"bitlis":(38.40,42.12),"bolu":(40.74,31.61),
    "burdur":(37.72,30.29),"bursa":(40.18,29.06),"canakkale":(40.15,26.41),
    "cankiri":(40.60,33.62),"corum":(40.55,34.96),"denizli":(37.77,29.09),
    "diyarbakir":(37.91,40.23),"edirne":(41.68,26.56),"elazig":(38.67,39.22),
    "erzincan":(39.75,39.50),"erzurum":(39.90,41.27),"eskisehir":(39.78,30.52),
    "gaziantep":(37.06,37.38),"giresun":(40.92,38.39),"gumushane":(40.46,39.48),
    "hakkari":(37.57,43.74),"hatay":(36.40,36.35),"isparta":(37.76,30.55),
    "mersin":(36.80,34.64),"icel":(36.80,34.64),"istanbul":(41.01,28.96),
    "izmir":(38.42,27.14),"kars":(40.60,43.10),"kastamonu":(41.38,33.78),
    "kayseri":(38.73,35.49),"kirklareli":(41.73,27.22),"kirsehir":(39.15,34.16),
    "kocaeli":(40.85,29.88),"konya":(37.87,32.49),"kony":(37.87,32.49),"kutahya":(39.42,29.98),
    "malatya":(38.35,38.32),"manisa":(38.62,27.43),"kahramanmaras":(37.58,36.94),
    "maras":(37.58,36.94),"mardin":(37.32,40.74),"mugla":(37.22,28.37),
    "mus":(38.73,41.49),"nevsehir":(38.62,34.71),"nigde":(37.97,34.68),
    "ordu":(40.98,37.88),"rize":(41.02,40.52),"sakarya":(40.69,30.44),
    "samsun":(41.29,36.33),"siirt":(37.93,41.95),"sinop":(42.03,35.15),
    "sivas":(39.75,37.02),"tekirdag":(40.98,27.52),"tokat":(40.31,36.55),
    "trabzon":(41.00,39.73),"tunceli":(39.10,39.55),"sanliurfa":(37.17,38.79),
    "urfa":(37.17,38.79),"usak":(38.68,29.41),"van":(38.49,43.38),
    "yozgat":(39.82,34.81),"zonguldak":(41.45,31.79),"aksaray":(38.37,34.04),
    "bayburt":(40.26,40.23),"karaman":(37.18,33.22),"kirikkale":(39.85,33.52),
    "batman":(37.89,41.13),"sirnak":(37.52,42.46),"bartin":(41.64,32.34),
    "ardahan":(41.11,42.70),"igdir":(39.92,44.05),"yalova":(40.65,29.27),
    "karabuk":(41.20,32.62),"kilis":(36.72,37.12),"osmaniye":(37.07,36.25),
    "duzce":(40.84,31.16),
}

def get_city_coords(city: str) -> tuple[float, float] | None:
    """Return approximate (lat, lon) for a city name, or None if unknown.
    Handles compound names like 'Adana Ceyhan' or 'Bolu/Abant' by falling
    back to the first word (parent city).
    """
    if not city:
        return None
    # Try full name
    key = _norm_city(city)
    if key in CITY_COORDS:
        return CITY_COORDS[key]
    # Split on space/slash BEFORE normalising (norm removes spaces)
    first = _norm_city(city.replace("/", " ").strip().split()[0])
    return CITY_COORDS.get(first)


# ---------------------------------------------------------------------------
# City -> TA region map (authoritative, overrides source data)
# ---------------------------------------------------------------------------
CITY_TA = {
    # TA1 - Istanbul + Trakya
    "istanbul":"TA1","edirne":"TA1","kirklareli":"TA1","tekirdag":"TA1",
    # TA2 - Marmara
    "bursa":"TA2","kocaeli":"TA2","sakarya":"TA2","bolu":"TA2",
    "bilecik":"TA2","yalova":"TA2","duzce":"TA2",
    # TA3 - Orta Anadolu Bati
    "ankara":"TA3","eskisehir":"TA3","kutahya":"TA3","afyonkarahisar":"TA3",
    "afyon":"TA3","cankiri":"TA3","kirikkale":"TA3",
    # TA4 - Ege
    "izmir":"TA4","aydin":"TA4","manisa":"TA4","mugla":"TA4",
    "denizli":"TA4","usak":"TA4","canakkale":"TA4","balikesir":"TA4",
    # TA5 - Akdeniz
    "adana":"TA5","mersin":"TA5","hatay":"TA5","kahramanmaras":"TA5",
    "osmaniye":"TA5","kilis":"TA5","gaziantep":"TA5",
    # TA6 - Karadeniz
    "samsun":"TA6","ordu":"TA6","giresun":"TA6","trabzon":"TA6",
    "rize":"TA6","artvin":"TA6","sinop":"TA6","kastamonu":"TA6",
    "bartin":"TA6","karabuk":"TA6","zonguldak":"TA6","tokat":"TA6",
    "amasya":"TA6","corum":"TA6","gumushane":"TA6",
    # TA7 - Dogu Anadolu
    "erzurum":"TA7","kars":"TA7","agri":"TA7","igdir":"TA7",
    "ardahan":"TA7","van":"TA7","mus":"TA7","bitlis":"TA7",
    "hakkari":"TA7","erzincan":"TA7","bayburt":"TA7","tunceli":"TA7",
    "bingol":"TA7",
    # TA8 - Gunes Orta Anadolu
    "konya":"TA8","kony":"TA8","karaman":"TA8","antalya":"TA8","isparta":"TA8",
    "burdur":"TA8","nigde":"TA8","aksaray":"TA8","nevsehir":"TA8",
    "kirsehir":"TA8","yozgat":"TA8",
    # TA9 - Guneydogu + Orta-Dogu Anadolu
    "kayseri":"TA9","sivas":"TA9","malatya":"TA9","elazig":"TA9",
    "diyarbakir":"TA9","sanliurfa":"TA9","mardin":"TA9","batman":"TA9",
    "sirnak":"TA9","siirt":"TA9","adiyaman":"TA9",
    # TA0 - Islands / Adalar (special district)
    "adalar":"TA0","buyukada":"TA0","heybeliada":"TA0","burgaz":"TA0",
    "kinaliada":"TA0","imrali":"TA0","avsa":"TA0","marmara":"TA0",
    "gokceada":"TA0","bozcaada":"TA0","cunda":"TA0","alibey":"TA0",
}

def _norm_city(s: str) -> str:
    return (s or "").lower() \
        .replace("ş","s").replace("ç","c").replace("ğ","g") \
        .replace("ü","u").replace("ö","o").replace("ı","i") \
        .replace("i̇","i").replace(" ","").strip()

def _norm_city_first(s: str) -> str:
    """Normalize only the FIRST word/segment of a compound city name.
    Handles 'Adana Ceyhan', 'Bolu/Abant', 'Amasya / Merzifon' etc."""
    first = (s or "").replace("/", " ").strip().split()[0] if (s or "").strip() else ""
    return _norm_city(first)

def split_city_district(city_raw: str) -> tuple[str, str]:
    """Split a compound city name into (main_city, district).
    'Adana Ceyhan' -> ('Adana', 'Ceyhan')
    'Amasya / Merzifon' -> ('Amasya', 'Merzifon')
    'Ankara' -> ('Ankara', '')
    Returns district='' if city is already a known province or can't be split."""
    if not city_raw:
        return city_raw, ""
    if _norm_city(city_raw) in CITY_TA:
        return city_raw, ""
    parts = re.split(r"\s*/\s*|\s+", city_raw.strip(), maxsplit=1)
    if len(parts) == 2 and _norm_city(parts[0]) in CITY_TA:
        return parts[0].strip().title(), parts[1].strip().title()
    return city_raw, ""

def correct_ta(city: str, source_ta: str, location: str = "") -> str:
    """Return authoritative TA region; fall back to source value if unknown.
    Tries full name first, then first word for compound names.
    Also checks location field for island keywords (TA0)."""
    # Location-based override for islands
    loc_norm = _norm_city(location)
    if any(k in loc_norm for k in ("adalar","gokceada","bozcaada","buyukada","heybeliada","kinaliada","burgaz")):
        return "TA0"
    ta = CITY_TA.get(_norm_city(city))
    if not ta:
        ta = CITY_TA.get(_norm_city_first(city))
    return ta if ta else (source_ta or "")


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

_LOC_PLACEHOLDERS = {"---", "--", "-", ".", "..", "yok", "none", "n/a", ""}

def _clean_loc(s: str) -> str:
    """Return empty string if s is a placeholder, otherwise return s as-is."""
    return "" if (s or "").strip().lower() in _LOC_PLACEHOLDERS else (s or "").strip()

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
        # Override: if location mentions NXDN explicitly, trust the text
        konum = (r.get("konum") or "").upper()
        if "NXDN" in konum:
            mode = "NXDN"
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
            "location":     r.get("konum") or r.get("sehir") or "",
            "frequency":    freq,
            "offset":       offset,
            "tone":         _safe_float(r.get("ton")),
            "band":         band,
            "mode":         mode,
            "status":       bool(r.get("durum")),
            "licensed":     bool(r.get("ruhsat")),
            "power_w":      r.get("guc"),
            "altitude_m":   r.get("yukseklik"),
            "lat":          float(r["lat"]) if r.get("lat") else (get_city_coords(r.get("sehir","")) or (None,None))[0],
            "lon":          float(r["lon"]) if r.get("lon") else (get_city_coords(r.get("sehir","")) or (None,None))[1],
            "coord_approx": not bool(r.get("lat")),
            "ta_region":    correct_ta(r.get("sehir",""), r.get("tabolge","")),
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
    # Normalize: lowercase + strip Unicode combining marks (e.g. İ → i, not i̇)
    import unicodedata
    def _norm_hdr(s):
        return unicodedata.normalize("NFKD", s.lower()) \
            .encode("ascii", "ignore").decode("ascii").strip()

    header_row = rows[0] if rows else None
    headers = []
    if header_row:
        headers = [_norm_hdr(th.get_text(strip=True)) for th in header_row.find_all(["th", "td"])]

    # Expected columns (flexible match)
    def col(row_cells, name_candidates):
        for name in name_candidates:
            for i, h in enumerate(headers):
                if name in h and i < len(row_cells):
                    return row_cells[i].get_text(strip=True)
        return ""

    idx = 0
    last_city = ""   # carry forward city across rowspan gaps
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

        callsign = col(cells, ["çağrı işareti", "cagri", "callsign", "istasyon"])
        city_raw = col(cells, ["ili", "şehir", "sehir"]).title()  # "il" removed — too broad
        city = city_raw if city_raw else last_city   # use last known city if cell empty (rowspan)
        if city_raw:
            last_city = city_raw
        location = col(cells, ["yeri", "konum", "lokasyon"])
        locator = col(cells, ["locator"])

        idx += 1
        records.append({
            "id":           f"AK_{idx}",
            "callsign":     callsign,
            "city":         city,
            "district":     None,
            "location":     _clean_loc(location) or callsign or city,
            "frequency":    freq,
            "offset":       calc_offset(freq, band),
            "tone":         tone,
            "band":         band,
            "mode":         "FM",
            "status":       True,          # AKRAD doesn't indicate status
            "licensed":     None,
            "power_w":      None,
            "altitude_m":   None,
            "lat":          (get_city_coords(city) or (None,None))[0],
            "lon":          (get_city_coords(city) or (None,None))[1],
            "coord_approx": True,
            "ta_region":    correct_ta(city, "", location),
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
# Normalize compound city names (e.g. "Adana Ceyhan" -> city="Adana", prepend district to location)
# ---------------------------------------------------------------------------
def normalize_cities(records: list[dict]) -> list[dict]:
    for r in records:
        city, district = split_city_district(r.get("city", "") or "")
        if district:
            r["city"] = city
            loc = r.get("location") or ""
            if district.lower() not in loc.lower():
                r["location"] = f"{district} / {loc}" if loc else district
            # Re-derive TA with clean city name if not already set
            if not r.get("ta_region"):
                r["ta_region"] = correct_ta(city, "", r.get("location", ""))
    return records


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    at_records = fetch_amatortelsiz()
    akrad_records = fetch_akrad()
    records = merge(at_records, akrad_records)
    records = normalize_cities(records)
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
