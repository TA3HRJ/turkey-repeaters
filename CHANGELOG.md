# Changelog

## [Unreleased]

### Changed
- aprsagent.com family look (2026-10-10): `docs/assets/family.css` (paper background, Maidenhead
  grid, airmail strip, mono uppercase headings, 2px corners), family header bar with link back to
  aprsagent.com, family footer with the other tools. Blue Material palette, emoji icons and
  rounded floating cards removed; map and badge colours follow `--series-*`. Dark theme kept,
  using the family dark values. PWA icons redrawn in the same palette; service worker cache v2.

### Removed
- External scraping: `scrape.py` no longer fetches amatortelsizcilik.com.tr or akrad.org.tr.
  It now only rebuilds `repeaters.json` from the existing file, applies `data/overrides.json`
  and regenerates `repeaters.min.json`. The database is manually maintained (2026-08-12).
- Scheduled GitHub Actions run: `update-data.yml` is manual dispatch only and just rebuilds
  the compact payload.
- Footer links to amatortelsizcilik and akrad (RepeaterBook link kept).

### Added
- About tab with a trademarks and disclaimer section (`#legal`), EN/TR; same text in README.
- PWA: `manifest.json`, icons, network-first service worker (`sw.js`).
- `build_compact.py`: column-oriented `repeaters.min.json` (~50% smaller), loaded by the site.
- Interactive map tab (Leaflet + MarkerCluster).
- Community voting (Working? / Location correct?) via Firebase anonymous auth.
- AT_530-532: three repeaters from TA3HRJ's Anytone log.
- Mode filter, TA region filter, frequency conflict filter, plate number column.

### Fixed
- RepeaterBook Import button needed two clicks to open the panel the first time.
- "All cities" filter option was not translated to Turkish.
- Five records with placeholder Ankara-center coordinates.
- City name normalisation (Turkish uppercase, canonical spellings, compound city/district names).

## [0.1.0] - 2026-04-07

### Added
- Initial project structure
- `scrape.py`: fetches data from amatortelsizcilik.com.tr (JSON API) and akrad.org.tr (HTML table)
- `merge_repeaterbook.py`: imports RepeaterBook CSV export into overrides
- `docs/index.html`: static site with DataTables, EN/TR toggle, CSV export, client-side RepeaterBook import
- `data/overrides.json`: manual corrections layer
- `docs/data/repeaters.json`: generated repeater database
