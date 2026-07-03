# Turkey Amateur Radio Repeaters

A static, open-source repeater database for Turkey — searchable, filterable, and exportable.  
Live site: **https://ta3hrj.github.io/turkey-repeaters**

---

## Features

- Live search and filter by band, city, status — filters are shareable via URL (`?band=VHF&city=İzmir&tab=map`)
- Interactive map (Leaflet, lazy-loaded on first use)
- "📍 Nearest" button: sorts repeaters by distance from your location
- EN / TR language toggle, dark mode (follows system, manual toggle persists)
- CSV export (filtered or full)
- Client-side RepeaterBook CSV import (session only)
- Installable PWA — works fully offline (service worker caches app + data)
- Weekly automated data refresh via GitHub Actions
- No login required, no backend, hosted free on GitHub Pages

---

## Data Sources

Data is aggregated from multiple Turkish amateur radio sources and cross-checked for accuracy.
[RepeaterBook](https://www.repeaterbook.com/row_repeaters/index2.php?state_id=TR) CSV can be imported manually for corrections and additions.

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r scripts/requirements.txt
```

### 2. Fetch / update repeater data

```bash
python scripts/scrape.py
```

This writes `docs/data/repeaters.json` and the compact `docs/data/repeaters.min.json`
the site actually loads (regenerate it alone with `python scripts/build_compact.py`).
Serve `docs/` locally (e.g. `python -m http.server --directory docs`) to view.

> Data also refreshes automatically every Monday via the
> `.github/workflows/update-data.yml` GitHub Action.

### 3. (Optional) Import a RepeaterBook CSV

Download CSV from RepeaterBook → Turkey filter, then:

```bash
python scripts/merge_repeaterbook.py path/to/export.csv
```

Then re-run `scrape.py` to rebuild the JSON.

### 4. Deploy

```bash
git add docs/data/repeaters.json
git commit -m "Update repeater data YYYY-MM-DD"
git push
```

GitHub Pages serves the `docs/` folder automatically.

---

## Repository Structure

```
turkey-repeaters/
├── docs/                  # GitHub Pages root
│   ├── index.html         # Website
│   └── data/
│       └── repeaters.json # Generated data file (commit after update)
├── scripts/
│   ├── scrape.py          # Fetch & normalize data from all sources
│   ├── merge_repeaterbook.py  # Import RepeaterBook CSV into overrides
│   └── requirements.txt
├── data/
│   └── overrides.json     # Manual corrections & RepeaterBook imports
├── CHANGELOG.md
└── README.md
```

---

## Repeater JSON Schema

Each record in `repeaters.json` contains:

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique ID (`AT_`, `AK_`, `RB_` prefix = source) |
| `callsign` | string | Amateur callsign |
| `city` | string | Province / city |
| `district` | string\|null | District (ilçe) |
| `location` | string | Site name |
| `frequency` | float | TX frequency (MHz) |
| `offset` | float | Offset in MHz (−0.600 VHF, −7.600 UHF) |
| `tone` | float\|null | CTCSS tone (Hz) |
| `band` | string | VHF / UHF / APRS / ECHO |
| `mode` | string | FM / DMR / C4FM / D-STAR / NXDN |
| `status` | bool | true = On-Air |
| `licensed` | bool\|null | Licensed repeater |
| `power_w` | int\|null | Power (Watts) |
| `altitude_m` | int\|null | Altitude (metres) |
| `lat` / `lon` | float\|null | GPS coordinates |
| `ta_region` | string | TA0–TA9 region code |
| `source` | string | Origin website |
| `last_seen` | string | Date of last scrape |

---

## Export Formats

All formats are available via the Export Wizard on the site:

- **Generic CSV** — spreadsheet-compatible
- **CHIRP CSV** — import into CHIRP software
- **Anytone CPS CSV** — Anytone D890UV channel list
- **GPX** — GPS waypoints (exact or approximate coords)
- **KML** — Google Earth / Maps layer

---

## License

MIT — for personal use only.
