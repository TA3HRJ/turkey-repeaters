"""
find_similar_locations.py — Find similar location names and suggest canonical forms.

Usage:
    python scripts/find_similar_locations.py

Output:
    data/location_aliases_draft.json  — review and edit this file
    then run: python scripts/apply_location_aliases.py
"""

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "docs" / "data" / "repeaters.json"
OUTPUT = ROOT / "data" / "location_aliases_draft.json"

# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------
SUFFIXES = [
    "dagi", "dg", "dag", "tepe", "tp", "t", "mevkii", "mevki", "mvk", "mv",
    "zirvesi", "zirvesi", "gediği", "gedigi", "kale", "kalesi", "koyu",
    "burnu", "bumu", "sehir", "sehir merkezi", "s.merkezi", "s.m",
    "merkezi", "mrk", "dere", "ovasi", "ova", "buku",
]

def norm(s: str) -> str:
    """Aggressive normalization: lowercase, ASCII, remove suffixes & punctuation."""
    s = (s or "").strip()
    # Turkish → ASCII
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    # Remove punctuation / extra spaces
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    # Remove common geographic suffixes
    words = s.split()
    filtered = [w for w in words if w not in SUFFIXES]
    if filtered:
        s = " ".join(filtered)
    return s

def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            curr.append(min(prev[j] + 1, curr[j-1] + 1, prev[j-1] + (ca != cb)))
        prev = curr
    return prev[-1]

def similarity(a: str, b: str) -> float:
    """0.0–1.0 similarity score."""
    na, nb = norm(a), norm(b)
    if not na or not nb:
        return 0.0
    # Exact normalized match
    if na == nb:
        return 1.0
    # One contains the other
    if na in nb or nb in na:
        return 0.85
    # Levenshtein ratio
    max_len = max(len(na), len(nb))
    dist = levenshtein(na, nb)
    return 1.0 - dist / max_len

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)

    repeaters = data["repeaters"]
    # Collect unique locations with example record info
    loc_map: dict[str, list[dict]] = {}
    for r in repeaters:
        loc = (r.get("location") or "").strip()
        if not loc:
            continue
        if loc not in loc_map:
            loc_map[loc] = []
        loc_map[loc].append({"id": r["id"], "city": r.get("city",""), "freq": r.get("frequency")})

    locations = list(loc_map.keys())
    print(f"Unique locations: {len(locations)}")

    # Find groups of similar locations
    THRESHOLD = 0.80
    visited = set()
    groups = []

    for i, loc_a in enumerate(locations):
        if loc_a in visited:
            continue
        group = [loc_a]
        visited.add(loc_a)
        for loc_b in locations[i+1:]:
            if loc_b in visited:
                continue
            score = similarity(loc_a, loc_b)
            if score >= THRESHOLD:
                group.append(loc_b)
                visited.add(loc_b)
        if len(group) > 1:
            # Pick canonical: longest after normalization (usually most complete)
            canonical = max(group, key=lambda s: len(norm(s)))
            # Title-case it, clean up
            canonical_clean = re.sub(r"\s+", " ", canonical).strip().title()
            groups.append({
                "canonical": canonical_clean,
                "variants": group,
                "records": {v: loc_map[v] for v in group},
            })

    groups.sort(key=lambda g: g["canonical"])
    print(f"Similar groups found: {len(groups)}")

    # Write draft
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)

    print(f"Draft written to {OUTPUT}")
    print("Review and edit 'canonical' values, then run apply_location_aliases.py")

if __name__ == "__main__":
    main()
