"""
apply_safe_aliases.py — Apply ONLY safe location aliases (case/punctuation/suffix
differences) from location_aliases_draft.json to overrides.json.

A group is "safe" if ALL variants normalize to the SAME string.
Suspicious groups (where normalized forms diverge) are skipped and listed.

Usage:
    python scripts/apply_safe_aliases.py
"""

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFT   = ROOT / "data" / "location_aliases_draft.json"
OVERRIDES = ROOT / "data" / "overrides.json"

# ---------------------------------------------------------------------------
# Same normalization as find_similar_locations.py
# ---------------------------------------------------------------------------
SUFFIXES = {
    "dagi","dg","dag","tepe","tp","t","mevkii","mevki","mvk","mv",
    "zirvesi","gedigi","kale","kalesi","koyu","burnu","bumu",
    "sehir","merkezi","mrk","dere","ovasi","ova","buku","ky",
}

def norm(s: str) -> str:
    s = (s or "").strip()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    words = s.split()
    filtered = [w for w in words if w not in SUFFIXES]
    return " ".join(filtered) if filtered else s

def is_safe(variants: list[str]) -> bool:
    """All variants must normalize to the same non-empty string."""
    norms = {norm(v) for v in variants}
    return len(norms) == 1 and "" not in norms

# ---------------------------------------------------------------------------
# Pick best canonical: prefer title-case, longer, no ALL-CAPS
# ---------------------------------------------------------------------------
def best_canonical(variants: list[str]) -> str:
    def score(s):
        is_title = s == s.title()
        not_allcaps = s != s.upper()
        length = len(s)
        has_accent = any(c in s for c in "ğşçöüıİĞŞÇÖÜ")
        return (not_allcaps, is_title, has_accent, length)
    return max(variants, key=score)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if not DRAFT.exists():
        print("Draft not found. Run find_similar_locations.py first.")
        return

    with open(DRAFT, encoding="utf-8") as f:
        groups = json.load(f)

    with open(OVERRIDES, encoding="utf-8") as f:
        overrides = json.load(f)

    ov_index = {o["id"]: i for i, o in enumerate(overrides)}

    safe_count = skipped_count = applied = 0
    skipped_groups = []

    for group in groups:
        variants = group["variants"]
        records_map = group.get("records", {})

        if not is_safe(variants):
            skipped_count += 1
            skipped_groups.append({
                "variants": variants,
                "norm_forms": [norm(v) for v in variants],
            })
            continue

        safe_count += 1
        canonical = best_canonical(variants)

        for variant, records in records_map.items():
            if variant == canonical:
                continue
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

    print(f"Safe groups applied : {safe_count}")
    print(f"Suspicious (skipped): {skipped_count}")
    print(f"Override records set: {applied}")
    print()
    print("--- SKIPPED GROUPS (review manually) ---")
    for g in skipped_groups:
        print(f"  variants : {g['variants']}")
        print(f"  norm     : {g['norm_forms']}")
        print()
    print("Run 'python scripts/scrape.py' to rebuild repeaters.json")

if __name__ == "__main__":
    main()
