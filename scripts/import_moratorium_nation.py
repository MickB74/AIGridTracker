#!/usr/bin/env python3
"""Import the Moratorium Nation dataset into the two places it can honestly go.

Moratorium Nation (Bommarito 2026, CC-BY-4.0) inventories 533 local moratoria
across 42 states, 505 of which touch data centers, every one geocoded. That is
wider than MORATORIUMS_DF and it is *not* ours, so this script deliberately
splits it by how much trust each destination requires:

1. `data/external_gazetteer.json` — jurisdiction **names** only, consumed by
   story_tracker.build_gazetteer(). A name is not a claim: recognising
   "Bell County" in a headline asserts nothing about whether Bell County
   passed anything. So this half needs no per-row source/as_of and publishes
   straight through, the same bar the story archive already runs at. This is
   the half that matters most day to day — ~70% of the archive is currently
   unlocalized, and most of those headlines do name a real town.

2. `data/moratorium_candidates.json` — inventory rows whose (locality, state)
   we don't already track, appended with `origin: "moratorium-nation"` for
   **human review**, exactly like the news scanner's output. These never
   reach a public page. Their `verify_count` is somebody else's confidence
   signal, not a source URL and not an `as_of`; promoting one into
   MORATORIUMS_DF still means reading the ordinance and recording where it
   was read (CLAUDE.md, Data sourcing).

Neither half edits a registry. Same discipline as scan_moratorium_candidates.py
and scan_locality_candidates.py.

Usage:
    python3 scripts/import_moratorium_nation.py             # from vendored CSV
    python3 scripts/import_moratorium_nation.py --fetch     # refresh CSV first
    python3 scripts/import_moratorium_nation.py --dry-run
    python3 scripts/import_moratorium_nation.py --gazetteer-only

Stdlib-only apart from importing src.constants (pandas), matching the other
scripts/ jobs so the CI build installs nothing beyond requirements-build.txt.
--fetch is the one network path and is never used by CI: the CSV is vendored
under data/external/ so an upstream change lands as a reviewable diff.
"""
import argparse
import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.constants import MORATORIUMS_DF  # noqa: E402
from src.story_tracker import clean_locality  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
INVENTORY_CSV = ROOT / "data" / "external" / "moratorium_nation_inventory.csv"
GAZETTEER_JSON = ROOT / "data" / "external_gazetteer.json"
CANDIDATES_JSON = ROOT / "data" / "moratorium_candidates.json"

UPSTREAM_CSV = ("https://raw.githubusercontent.com/mjbommar/"
                "moratorium-data-2026/main/data/moratorium_inventory.csv")
ATTRIBUTION = {
    "dataset": "Moratorium Nation: A Survey of Data Center, Renewable Energy, "
               "and Battery Storage Moratoria in the United States",
    "author": "Michael J. Bommarito II",
    "url": "https://mjbommar.github.io/moratorium-data-2026/",
    "repo": "https://github.com/mjbommar/moratorium-data-2026",
    "license": "CC-BY-4.0",
}

# "Town of Normal" and "Village of Godfrey" are how the ordinance names itself;
# a headline says "Normal". Strip the governmental prefix for matching but keep
# the cleaned bare name — clean_locality() separately drops "(Lake County)"
# style parentheticals.
_PREFIX_RE = re.compile(
    r"^(?:city|town|village|township|borough|county|parish)\s+of\s+", re.I)
# A gazetteer name shorter than this matches too much ordinary prose to be
# safe as a \b-bounded regex ("Ada", "Rio"). The news scanner's own false
# positives were all in this range.
MIN_NAME_LEN = 5


def normalize_name(raw):
    """Bare locality name suitable for word-boundary matching, or None."""
    name = clean_locality(_PREFIX_RE.sub("", str(raw or "").strip()))
    return name or None


def load_inventory(path=INVENTORY_CSV):
    """Data-center-touching rows only. Crypto-mining-only moratoria are
    excluded on purpose: they get miscited as data-center precedent, and a
    resident who quotes one at a hearing gets corrected in public."""
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return [r for r in rows if "data_center" in (r.get("sectors") or "")]


def derived_end_date(row):
    """current_end_date_iso when upstream recorded one (only 9 of 505 did),
    else enacted + duration_days. Returns None when the term is open-ended or
    the enacted date is unknown — never a guess."""
    if row.get("current_end_date_iso"):
        return row["current_end_date_iso"]
    if row.get("duration_kind") != "fixed_days":
        return None
    start, days = row.get("date_enacted_iso"), row.get("duration_days")
    if not start or not days:
        return None
    try:
        return (dt.date.fromisoformat(start[:10])
                + dt.timedelta(days=int(float(days)))).isoformat()
    except (ValueError, TypeError):
        return None


def build_gazetteer_payload(rows, today):
    """{name, state, jurisdiction_type} entries, deduped, plus attribution."""
    seen = {}
    skipped = []
    for row in rows:
        name = normalize_name(row.get("jurisdiction"))
        state = (row.get("state_abbrev") or "").strip()
        if not name or not state:
            continue
        if len(name) < MIN_NAME_LEN:
            skipped.append(f"{name}, {state}")
            continue
        seen.setdefault((name.lower(), state), {
            "name": name,
            "state": state,
            "jurisdiction_type": (row.get("jurisdiction_type") or "").strip(),
        })
    entries = sorted(seen.values(), key=lambda e: (e["state"], e["name"]))
    return {
        "updated": today,
        "_readme": (
            "Locality names only, imported from Moratorium Nation "
            "(CC-BY-4.0) by scripts/import_moratorium_nation.py. Consumed by "
            "src/story_tracker.build_gazetteer() to recognise place names in "
            "headlines. A name here asserts nothing about what the locality "
            "did — it is not a moratorium record and must never be rendered "
            "as one. Regenerate, don't hand-edit."
        ),
        "attribution": ATTRIBUTION,
        "entries": entries,
    }, skipped


def tracked_keys():
    """(lowercased locality, state abbrev) already in MORATORIUMS_DF."""
    keys = set()
    for _, row in MORATORIUMS_DF.iterrows():
        name = normalize_name(row["locality"])
        state = str(row["state"]).strip()
        if name and state:
            keys.add((name.lower(), state))
    return keys


def build_candidates(rows, known, today):
    """Inventory rows we don't already track, as review-queue records."""
    out, seen = [], set()
    for row in rows:
        name = normalize_name(row.get("jurisdiction"))
        state = (row.get("state_abbrev") or "").strip()
        if not name or not state:
            continue
        key = (name.lower(), state)
        if key in known or key in seen:
            continue
        seen.add(key)
        out.append({
            "title": f"{name}, {state} — {row.get('jurisdiction_type') or 'Local'} "
                     f"moratorium ({row.get('enacted_status') or 'status unknown'})",
            "locality": name,
            "state": state,
            "level": "Local",
            "upstream_status": row.get("enacted_status") or None,
            "date_enacted_iso": row.get("date_enacted_iso") or None,
            "duration_kind": row.get("duration_kind") or None,
            "duration_days": row.get("duration_days") or None,
            "derived_end_date": derived_end_date(row),
            "sectors": row.get("sectors") or None,
            "legal_basis": (row.get("legal_basis") or "")[:600] or None,
            "current_status_note": (row.get("current_status") or "")[:600] or None,
            "outcome_note": (row.get("outcome") or "")[:600] or None,
            "upstream_id": row.get("moratorium_id") or None,
            "lat": row.get("latitude") or None,
            "lon": row.get("longitude") or None,
            # Upstream's own confidence signal. NOT a source URL and NOT an
            # as_of — see this file's docstring before promoting anything.
            "upstream_verify_count": row.get("verify_count") or None,
            "source": None,
            "as_of": None,
            "first_seen": today,
            "last_seen": today,
            "status": "new",
            "origin": "moratorium-nation",
            "attribution": ATTRIBUTION["url"],
        })
    return out


def merge_candidates(existing, fresh, today):
    """Fold `fresh` into `existing` (mutated), keyed by upstream_id and then
    by (locality, state). Keeps first_seen; never resurrects a dismissed
    entry; never overwrites a human's edits to a promoted one."""
    def key_of(rec):
        if rec.get("origin") == "moratorium-nation" and rec.get("upstream_id"):
            return ("id", rec["upstream_id"])
        loc, state = rec.get("locality"), rec.get("state")
        return ("ls", str(loc).lower(), state) if loc and state else None

    index = {}
    for rec in existing:
        k = key_of(rec)
        if k:
            index.setdefault(k, rec)

    added = 0
    for rec in fresh:
        prior = index.get(key_of(rec))
        if prior is not None:
            prior["last_seen"] = today
            continue
        existing.append(rec)
        index[key_of(rec)] = rec
        added += 1
    return added


def fetch_upstream(path=INVENTORY_CSV):
    import urllib.request
    with urllib.request.urlopen(UPSTREAM_CSV, timeout=60) as resp:
        path.write_bytes(resp.read())
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fetch", action="store_true",
                    help="refresh the vendored CSV from upstream first")
    ap.add_argument("--dry-run", action="store_true", help="write nothing")
    ap.add_argument("--gazetteer-only", action="store_true",
                    help="skip the moratorium-candidate reconciliation")
    args = ap.parse_args(argv)

    today = dt.date.today().isoformat()

    if args.fetch:
        fetch_upstream()
        print(f"fetched {UPSTREAM_CSV} -> {INVENTORY_CSV.relative_to(ROOT)}")

    rows = load_inventory()
    print(f"inventory: {len(rows)} data-center-touching rows")

    payload, skipped = build_gazetteer_payload(rows, today)
    print(f"gazetteer: {len(payload['entries'])} localities "
          f"({len(skipped)} skipped as too short to match safely)")
    if skipped:
        print("  skipped: " + ", ".join(sorted(set(skipped))))

    if not args.dry_run:
        GAZETTEER_JSON.write_text(json.dumps(payload, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"  wrote {GAZETTEER_JSON.relative_to(ROOT)}")

    if args.gazetteer_only:
        return 0

    known = tracked_keys()
    fresh = build_candidates(rows, known, today)
    print(f"candidates: {len(fresh)} localities not in MORATORIUMS_DF "
          f"({len(known)} already tracked)")

    queue = json.loads(CANDIDATES_JSON.read_text(encoding="utf-8"))
    added = merge_candidates(queue.setdefault("candidates", []), fresh, today)
    queue["updated"] = today
    print(f"  {added} new, {len(fresh) - added} already queued")

    if not args.dry_run:
        CANDIDATES_JSON.write_text(json.dumps(queue, indent=2) + "\n",
                                   encoding="utf-8")
        print(f"  wrote {CANDIDATES_JSON.relative_to(ROOT)} "
              f"({len(queue['candidates'])} total)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
