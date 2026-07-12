"""Facilities research CLI — discover a company's data-center locations from
public sources and emit review-ready rows for the map.

Usage:
    python -m src.research.dc_finder --ticker EQIX
    python -m src.research.dc_finder --company "Digital Realty" --forms 10-K
    python -m src.research.dc_finder --ticker MSFT --source firstparty --geocode
    python -m src.research.dc_finder --ticker AMZN --source both --geocode

Output (research_output/<slug>_facilities.{csv,json}) uses the HYPERSCALERS
schema — company, location, state, lat, lon, src — plus provenance columns
(mentions, dc_score, source_url, filing, sample) so you can vet each row before
pasting the good ones into src/constants.py. Nothing here writes to the app.

SEC asks for a real contact in the User-Agent; override with --contact.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

from . import edgar, firstparty
from .extract import locations_from_text, metros_from_text, group_by_state

OUT_DIR = Path(__file__).resolve().parents[2] / "research_output"


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_") or "company"


def from_edgar(query: str, ua: str, *, forms, filings: int, per_doc_cap: int):
    """Resolve the company on EDGAR, read recent filings, and mine each filing's
    text for location candidates. Returns (label, candidates)."""
    hit = edgar.resolve_cik(query, ua)
    if not hit:
        print(f"  ! EDGAR: could not resolve '{query}' to a CIK", file=sys.stderr)
        return query, []
    cik, title, ticker = hit
    print(f"  · EDGAR: {title} (CIK {cik}, {ticker or 'no ticker'})")
    fils = edgar.recent_filings(cik, ua, forms=forms, limit=filings)
    print(f"  · {len(fils)} filing(s) matching {forms}")
    agg: dict = {}
    for f in fils:
        if not f["primary_doc_url"]:
            continue
        text = edgar.fetch_document_text(f["primary_doc_url"], ua)
        if not text:
            continue
        # metro gazetteer (coords included) + "City, ST" regex for anything not
        # in the gazetteer; the metro pass is the reliable one for colo/REITs.
        cands = (metros_from_text(text, min_count=1)
                 + locations_from_text(text, min_count=2))[:per_doc_cap]
        tag = f"{f['form']} {f['filing_date']}"
        print(f"    - {tag}: {len(cands)} candidate location(s)")
        for c in cands:
            key = (c["location"], c["state"])
            keep = agg.setdefault(key, {**c, "mentions": 0, "dc_score": 0,
                                        "filing": tag,
                                        "source_url": f["primary_doc_url"]})
            keep["mentions"] += c["mentions"]
            keep["dc_score"] = max(keep["dc_score"], c["dc_score"])
    ranked = sorted(agg.values(),
                    key=lambda d: (d["dc_score"], d["mentions"]), reverse=True)
    return title or query, ranked


def from_firstparty(company: str, *, url=None, html=None):
    """Scrape the company's own location page. Returns (label, candidates)."""
    cands, page = firstparty.discover(company, url=url, html=html)
    src = url or page or "(no registry URL)"
    print(f"  · first-party: {page or 'no page'} -> {len(cands)} candidate(s)")
    if not cands:
        print("    (0 hits often means the page is JS-rendered — re-run with "
              "--html-file after saving the rendered page)", file=sys.stderr)
    for c in cands:
        c["filing"] = "first-party page"
        c["source_url"] = src
    return company, cands


def write_outputs(label: str, company: str, rows: list, do_geocode: bool):
    """Geocode (optional), then write CSV + JSON in the map schema. Returns paths."""
    if do_geocode:
        from .geocode import geocode
        todo = [r for r in rows if not r.get("lat")]
        print(f"  · geocoding {len(todo)} un-resolved location(s) via "
              f"Nominatim (~1/s)…")
        for r in todo:
            r["lat"], r["lon"] = geocode(r["location"], r["state"])
    else:
        for r in rows:
            r.setdefault("lat", "")
            r.setdefault("lon", "")

    OUT_DIR.mkdir(exist_ok=True)
    slug = _slug(label)
    cols = ["company", "location", "state", "lat", "lon", "src",
            "mentions", "dc_score", "filing", "source_url", "sample"]
    src_tag = _slug(company)[:20] + "_dc"
    records = [{
        "company": company, "location": r["location"], "state": r["state"],
        "lat": r.get("lat", ""), "lon": r.get("lon", ""), "src": src_tag,
        "mentions": r.get("mentions", ""), "dc_score": r.get("dc_score", ""),
        "filing": r.get("filing", ""), "source_url": r.get("source_url", ""),
        "sample": r.get("sample", "")[:200],
    } for r in rows]

    csv_path = OUT_DIR / f"{slug}_facilities.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(records)
    json_path = OUT_DIR / f"{slug}_facilities.json"
    json_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    return csv_path, json_path


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Discover a company's data-center locations from public "
                    "sources (SEC EDGAR + first-party pages).")
    who = ap.add_mutually_exclusive_group(required=True)
    who.add_argument("--ticker", help="stock ticker, e.g. EQIX")
    who.add_argument("--company", help="company name (substring match)")
    ap.add_argument("--source", choices=["edgar", "firstparty", "both"],
                    default="edgar")
    ap.add_argument("--forms", default="10-K,8-K",
                    help="comma-separated SEC form types (default 10-K,8-K)")
    ap.add_argument("--filings", type=int, default=6,
                    help="max filings to read (default 6)")
    ap.add_argument("--per-doc-cap", type=int, default=80,
                    help="max candidate locations kept per filing (default 80)")
    ap.add_argument("--geocode", action="store_true",
                    help="resolve lat/lon via OSM Nominatim (~1 req/s)")
    ap.add_argument("--url", help="override the first-party page URL")
    ap.add_argument("--html-file",
                    help="parse a saved/rendered HTML file instead of fetching "
                         "(for JS-only first-party pages)")
    ap.add_argument("--contact", default=edgar.DEFAULT_UA,
                    help="User-Agent contact string sent to SEC")
    args = ap.parse_args(argv)

    query = args.ticker or args.company
    ua = args.contact
    print(f"Facilities research: {query}  (source={args.source})")

    rows: list = []
    label = query
    company = args.company or (args.ticker.upper() if args.ticker else query)

    if args.source in ("edgar", "both"):
        forms = tuple(f.strip() for f in args.forms.split(",") if f.strip())
        label, ecands = from_edgar(query, ua, forms=forms, filings=args.filings,
                                   per_doc_cap=args.per_doc_cap)
        if args.company is None:
            company = label
        rows.extend(ecands)

    if args.source in ("firstparty", "both"):
        html = None
        if args.html_file:
            html = Path(args.html_file).read_text(encoding="utf-8", errors="ignore")
        _, fcands = from_firstparty(company, url=args.url, html=html)
        # merge, preferring EDGAR provenance when a place appears in both
        seen = {(r["location"], r["state"]) for r in rows}
        rows.extend(c for c in fcands if (c["location"], c["state"]) not in seen)

    if not rows:
        print("\nNo candidate locations found. Try --source both, a different "
              "--forms set, or --html-file for a JS-rendered page.")
        return 1

    csv_path, json_path = write_outputs(label, company, rows, args.geocode)
    by_state = group_by_state(rows)
    print(f"\n✓ {len(rows)} candidate location(s) across {len(by_state)} "
          f"state(s)/region(s)")
    print(f"  {csv_path}")
    print(f"  {json_path}")
    print("\nReview the CSV (check dc_score / sample), then paste vetted rows "
          "into HYPERSCALERS / AI_COMPETITOR_SITES in src/constants.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
