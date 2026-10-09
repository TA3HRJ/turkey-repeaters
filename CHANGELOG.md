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
- Repeater list overflowed and the Community (voting) column was out of sight: the 17-column
  table only scrolled sideways, with its scrollbar under all 574 rows. The table now sits in a
  viewport-high box (scrollbar always reachable, sticky header row), the Community column is
  pinned to the right edge, its labels moved into the header, and the Location column wraps
  again (wrapping had been applied to City since the Plate column was added). At a 1024px
  viewport the table went from 1670px to 1336px wide.
- Trademarks and disclaimer section (`#legal`) is aligned with the rest of the About tab
  instead of shifted to the middle of the page (2026-10-10). Service worker cache v3.
- Community votes were saved but never shown: `castVote` writes `{"AT_1.wy": …}` with
  `set(…, {merge:true})`, which stores literal dotted field names, while the page read nested
  objects. The page now folds the flat fields back (`unflattenVotes`); existing votes appear,
  "you voted" highlighting works and changing a vote subtracts the previous one.
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
