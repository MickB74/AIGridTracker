# Facilities research (`src/research`)

A standalone CLI that discovers where a company's **data centers** are, from
public sources — **SEC EDGAR filings** and **first-party location pages** — and
writes review-ready rows in the map schema used by `HYPERSCALERS` /
`AI_COMPETITOR_SITES` in [`src/constants.py`](../constants.py).

It is deliberately **not** imported by `app.py`. It surfaces *candidates* for a
human to vet; you paste the good rows into `constants.py` yourself. Scraped,
unverified data never reaches the live map automatically.

## Run

```bash
# best signal: colo/REIT 10-Ks itemize every metro
python -m src.research.dc_finder --ticker EQIX                 # Equinix
python -m src.research.dc_finder --company "Digital Realty"    # name match

# hyperscalers don't itemize in 10-Ks — mine 8-K announcements instead
python -m src.research.dc_finder --ticker MSFT --forms 8-K --filings 12

# add coordinates for any place not in the metro gazetteer
python -m src.research.dc_finder --ticker QTS --geocode

# first-party page (or both). JS-only pages: save the rendered HTML and pass it
python -m src.research.dc_finder --company "Google" --source firstparty
python -m src.research.dc_finder --company "Meta" --source firstparty \
    --html-file meta_rendered.html
```

Output lands in `research_output/<slug>_facilities.{csv,json}`.

## How it works

| Module | Role |
|---|---|
| `edgar.py` | ticker/name → CIK, recent filings, fetch filing text, full-text search. No API key; polite rate-limit + SEC contact User-Agent (`--contact`). |
| `gazetteer.py` | ~90 global DC metros → (lat, lon, state, country). Colo filings list metros by name; this resolves them **with coordinates**, no geocoding. |
| `extract.py` | `metros_from_text` (gazetteer pass, reliable for colos), `locations_from_text` ("City, ST" regex for anything else), `tables_from_html`. |
| `firstparty.py` | fetch a hyperscaler's own location page and mine it. Registry of known URLs; `--url` / `--html-file` to override. |
| `geocode.py` | optional OSM Nominatim lookup (`--geocode`, ~1 req/s) for un-gazetteered places. |
| `dc_finder.py` | CLI: resolve → gather → (geocode) → dedupe → write CSV+JSON. |

## Reading the output

Columns: `company, location, state, lat, lon, src` (map schema) plus provenance
— `mentions` (how often the place appears), `dc_score` (mentions with
data-center vocabulary nearby — higher = more likely a real facility), `filing`,
`source_url`, `sample` (surrounding text). Sort by `dc_score` then `mentions`;
skim `sample` to reject boilerplate before copying rows into `constants.py`.

## Caveats

- Candidates need **human review** — the extractor is heuristic.
- Coordinates are **metro/town centroids**, not surveyed sites.
- Hyperscaler 10-Ks don't list facilities; use `--forms 8-K` for announcements.
- First-party pages are often JS-rendered; a 0-hit result means "render it
  first" (`--html-file`), not "no data centers".
