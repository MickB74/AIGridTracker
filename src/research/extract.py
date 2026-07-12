"""Pull candidate facility locations out of filing text.

Two complementary passes:
  1. ``locations_from_text`` — regex for "City, ST" mentions, ranked by how
     often they recur and whether data-center vocabulary sits nearby. Works on
     any prose (10-K Item 2 "Properties", 8-K announcements, press releases).
  2. ``tables_from_html`` — parse REIT property schedules (Equinix, Digital
     Realty et al. tabulate every metro) via pandas.read_html.

Everything here is heuristic and meant for HUMAN REVIEW before it touches the
live map — it surfaces candidates, it does not verify them.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict

from .gazetteer import METROS, METRO_NAMES_BY_LEN

# USPS state/territory abbreviations, used to anchor "City, ST" matches.
US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
    "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
    "WI", "WY", "DC", "PR",
}

# Words that, near a "City, ST", raise confidence it's a facility not boilerplate.
_DC_VOCAB = re.compile(
    r"\b(data\s*cent(?:er|re)|colocation|co-?location|facilit(?:y|ies)|"
    r"campus|server|hyperscale|megawatt|MW\b|square\s*f(?:ee|oo)t|"
    r"interconnect|IBX|availability\s*zone|region)\b", re.I)

# "City, ST" — City is 1-4 capitalized tokens; ST is a US abbreviation.
_CITY_ST = re.compile(
    r"\b([A-Z][A-Za-z.'\-]+(?:\s+[A-Z][A-Za-z.'\-]+){0,3}),\s*([A-Z]{2})\b")

# Obvious non-city leading words that precede a comma+STATE by coincidence.
_STOP_LEADS = {
    "Inc", "Corp", "Company", "LLC", "LP", "Street", "Avenue", "Suite",
    "Floor", "Item", "Note", "Table", "Exhibit", "Section", "The", "See",
}


def locations_from_text(text: str, *, window: int = 60, min_count: int = 1):
    """Return candidate locations from prose, best-first.

    Each candidate: {location, state, mentions, dc_score, sample}. `dc_score`
    is how many mentions had data-center vocabulary within `window` chars —
    higher means more likely a real facility reference. Candidates below
    `min_count` mentions are dropped.
    """
    if not text:
        return []
    counts: Counter = Counter()
    dc_hits: Counter = Counter()
    samples: dict = {}
    for m in _CITY_ST.finditer(text):
        city, st = m.group(1).strip(), m.group(2)
        if st not in US_STATES:
            continue
        lead = city.split()[0].rstrip(".")
        if lead in _STOP_LEADS:
            continue
        key = (city, st)
        counts[key] += 1
        lo = max(0, m.start() - window)
        hi = min(len(text), m.end() + window)
        ctx = text[lo:hi]
        if _DC_VOCAB.search(ctx):
            dc_hits[key] += 1
        samples.setdefault(key, ctx.strip())
    out = []
    for (city, st), n in counts.items():
        if n < min_count:
            continue
        out.append({
            "location": city, "state": st, "mentions": n,
            "dc_score": dc_hits.get((city, st), 0), "sample": samples[(city, st)],
        })
    # rank: DC-vocab hits first, then raw frequency
    out.sort(key=lambda d: (d["dc_score"], d["mentions"]), reverse=True)
    return out


def metros_from_text(text: str, *, min_count: int = 1):
    """Return known data-center METROS mentioned in the text, best-first.

    This is the reliable path for colo/REIT filings, which list their footprint
    by metro name rather than "City, ST". Each candidate carries coordinates
    straight from the gazetteer: {location, state, lat, lon, country, mentions,
    dc_score, sample}. `dc_score` counts mentions with facility vocabulary
    nearby; here it mainly distinguishes a real footprint listing from a
    one-off geographic aside.
    """
    if not text:
        return []
    counts: Counter = Counter()
    dc_hits: Counter = Counter()
    samples: dict = {}
    for name in METRO_NAMES_BY_LEN:
        # word-boundary, case-sensitive on the leading capital to avoid matching
        # "london" inside prose; metros are proper nouns in filings.
        for m in re.finditer(rf"\b{re.escape(name)}\b", text):
            counts[name] += 1
            lo, hi = max(0, m.start() - 60), min(len(text), m.end() + 60)
            ctx = text[lo:hi]
            if _DC_VOCAB.search(ctx):
                dc_hits[name] += 1
            samples.setdefault(name, ctx.strip())
    out = []
    for name, n in counts.items():
        if n < min_count:
            continue
        lat, lon, st, country = METROS[name]
        out.append({
            "location": name, "state": st, "lat": lat, "lon": lon,
            "country": country, "mentions": n,
            "dc_score": dc_hits.get(name, 0), "sample": samples[name],
        })
    out.sort(key=lambda d: (d["dc_score"], d["mentions"]), reverse=True)
    return out


def tables_from_html(html: str, *, want_cols=("location", "market", "metro",
                                             "city", "property", "region")):
    """Extract property-schedule rows from filing HTML tables.

    Returns a list of dicts, one per row, from any table whose header row looks
    location-ish (matches `want_cols`). Requires pandas+lxml; returns [] if the
    parse fails or no location table is found.
    """
    try:
        import pandas as pd
        from io import StringIO
        tables = pd.read_html(StringIO(html))
    except Exception:                                             # noqa: BLE001
        return []
    rows = []
    for df in tables:
        cols = [str(c).strip().lower() for c in df.columns]
        if not any(any(w in c for w in want_cols) for c in cols):
            continue
        df.columns = cols
        for _, r in df.iterrows():
            rows.append({c: (str(r[c]).strip() if r[c] == r[c] else "")
                         for c in cols})
    return rows


def group_by_state(candidates):
    """Fold a candidate list into {state: [locations...]} for a quick summary."""
    by = defaultdict(list)
    for c in candidates:
        by[c["state"]].append(c["location"])
    return dict(by)
