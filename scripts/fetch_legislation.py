#!/usr/bin/env python3
"""Fetch data-center and AI legislation from LegiScan into a local cache.

Queries LegiScan's free Pull API for bills matching data-center and AI terms
across all 50 states, fetches full bill details for new or changed entries,
and writes the result to data/legislation_cache.json.

The cache is a review-free data feed — unlike the moratorium candidate queue,
bills publish straight to the legislation page, because LegiScan *is* the
primary source (state legislature filings). Each bill carries its own
`state_link` to the legislature's official text.

API budget: the free tier allows 30,000 queries/month. A typical daily run
uses ~600 calls (a handful of search queries returning ~500 bills, plus
getBill for each changed hash). Well within budget.

Usage:
    python3 scripts/fetch_legislation.py                # fetch + update cache
    python3 scripts/fetch_legislation.py --dry-run      # report, write nothing
    python3 scripts/fetch_legislation.py --offline       # reuse cached data
    python3 scripts/fetch_legislation.py --report out.md
    python3 scripts/fetch_legislation.py --searches-only # just run searches, skip getBill

Requires LEGISCAN_API_KEY in the environment (free at legiscan.com/legiscan).

Stdlib-only, like its sibling scanners.
"""

import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_PATH = ROOT / "data" / "legislation_cache.json"
EXTERNAL_DIR = ROOT / "data" / "external"

API_BASE = "https://api.legiscan.com/"

# Queries that capture data-center and AI legislation. Each is run against
# all states. LegiScan does full-text search across bill title + text, so
# these catch bills even when the title is generic.
SEARCHES = [
    '"data center"',
    '"data centres"',
    '"artificial intelligence"',
    '"generative AI"',
    '"machine learning"',
    '"hyperscale"',
    '"large language model"',
]

# Bills matching these terms but NOT any of the above are noise — housing
# moratoriums, unrelated zoning. We filter after retrieval.
RELEVANCE_TERMS = [
    "data center", "data centre", "artificial intelligence",
    "machine learning", "generative ai", "hyperscale", "large language model",
    "ai ", " ai,", " ai.", "algorithm", "automated decision",
    "deepfake", "chatbot", "facial recognition", "compute",
    "cloud computing", "colocation", "server farm",
]

UA = ("Mozilla/5.0 (compatible; GridWatchLegislation/1.0; "
      "+https://aigridwatch.com)")

# Map LegiScan status codes to human-readable labels
STATUS_MAP = {
    0: "N/A",
    1: "Introduced",
    2: "Engrossed",
    3: "Enrolled",
    4: "Passed",
    5: "Vetoed",
    6: "Failed",
}

# Map LegiScan progress codes to stages
PROGRESS_MAP = {
    0: "Prefiled",
    1: "Introduced",
    2: "Passed Committee",
    3: "Passed One Chamber",
    4: "Passed Both Chambers",
    5: "Signed/Enacted",
    6: "Vetoed",
}

# Category classification based on keywords in title + description
CATEGORY_RULES = [
    ("Data Centers", [
        "data center", "data centre", "colocation", "server farm",
        "hyperscale", "cloud computing",
    ]),
    ("AI Regulation", [
        "artificial intelligence", "generative ai", "machine learning",
        "large language model", "algorithm", "automated decision",
        "autonomous", "chatbot",
    ]),
    ("Deepfakes & Synthetic Media", [
        "deepfake", "synthetic media", "synthetic image", "synthetic video",
        "ai-generated", "ai generated",
    ]),
    ("Energy & Grid", [
        "electricity", "electric grid", "power purchase", "renewable energy",
        "energy consumption", "kilowatt", "megawatt", "utility rate",
        "grid reliability", "energy infrastructure",
    ]),
    ("Water", [
        "water usage", "water consumption", "water withdrawal", "cooling water",
        "water resource", "aquifer",
    ]),
    ("Healthcare", [
        "health care", "healthcare", "clinical", "patient",
        "medical", "diagnosis",
    ]),
    ("Education", [
        "education", "school", "student", "classroom", "literacy",
        "professional development",
    ]),
    ("Employment & Labor", [
        "worker", "employment", "labor", "workplace",
        "job displacement", "workforce",
    ]),
    ("Privacy", [
        "privacy", "surveillance", "biometric", "facial recognition",
        "personal data", "consumer data",
    ]),
    ("Tax & Incentives", [
        "tax incentive", "tax credit", "tax exemption", "tax abatement",
        "economic incentive", "enterprise zone",
    ]),
]


def _api_key():
    key = os.environ.get("LEGISCAN_API_KEY", "").strip()
    if not key:
        print("ERROR: set LEGISCAN_API_KEY in the environment", file=sys.stderr)
        print("  Free key: https://legiscan.com/legiscan", file=sys.stderr)
        sys.exit(1)
    return key


def _api_call(op, key, params=None, label=""):
    """Call the LegiScan API and return the parsed JSON."""
    p = {"key": key, "op": op}
    if params:
        p.update(params)
    url = API_BASE + "?" + urllib.parse.urlencode(p)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
    except Exception as e:
        print(f"  ! API {op} {label}: {type(e).__name__}: {e}", file=sys.stderr)
        return None
    if data.get("status") != "OK":
        print(f"  ! API {op} {label}: {data.get('alert', {}).get('message', 'unknown error')}",
              file=sys.stderr)
        return None
    return data


def search_bills(key, query, state="ALL", year=2):
    """Search LegiScan for bills. year=2 means current+prior session."""
    results = []
    page = 1
    while True:
        data = _api_call("getSearchRaw", key, {
            "query": query,
            "state": state,
            "year": str(year),
            "page": str(page),
        }, label=f"q={query!r} p={page}")
        if not data:
            break
        sr = data.get("searchresult", {})
        summary = sr.get("summary", {})
        page_total = summary.get("page_total", 1)

        for k, v in sr.items():
            if k == "summary":
                continue
            if isinstance(v, dict) and "bill_id" in v:
                results.append(v)

        if page >= page_total:
            break
        page += 1
        time.sleep(0.25)
    return results


def get_bill(key, bill_id):
    """Fetch full bill details."""
    data = _api_call("getBill", key, {"id": str(bill_id)}, label=f"bill={bill_id}")
    if not data:
        return None
    return data.get("bill")


def classify_bill(title, description=""):
    """Assign category labels based on title + description text."""
    text = f"{title} {description}".lower()
    categories = []
    for cat, terms in CATEGORY_RULES:
        if any(t in text for t in terms):
            categories.append(cat)
    return categories if categories else ["Other"]


def progress_label(progress_events):
    """Derive the furthest progress stage from a bill's progress list."""
    if not progress_events:
        return "Introduced"
    max_event = max(progress_events, key=lambda e: e.get("event", 0))
    return PROGRESS_MAP.get(max_event.get("event", 0), "Introduced")


def is_relevant(bill):
    """Check if a search result is actually about our topics."""
    text = f"{bill.get('title', '')} {bill.get('description', '')}".lower()
    return any(t in text for t in RELEVANCE_TERMS)


def load_cache():
    if CACHE_PATH.exists():
        with open(CACHE_PATH) as f:
            return json.load(f)
    return {"bills": {}, "last_updated": None, "search_meta": {}}


def save_cache(cache):
    cache["last_updated"] = dt.date.today().isoformat()
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    print(f"  Wrote {len(cache['bills'])} bills to {CACHE_PATH}")


def bill_to_record(bill):
    """Convert a full getBill response to our cache format."""
    progress = bill.get("progress", [])
    sponsors = []
    for s in bill.get("sponsors", []):
        sponsors.append({
            "name": s.get("name", ""),
            "party": s.get("party", ""),
            "role": s.get("role", ""),
            "district": s.get("district", ""),
        })

    subjects = [s.get("subject_name", "") for s in bill.get("subjects", [])]

    history = []
    for h in bill.get("history", []):
        history.append({
            "date": h.get("date", ""),
            "action": h.get("action", ""),
            "chamber": h.get("chamber", ""),
        })

    title = bill.get("title", "")
    desc = bill.get("description", "")

    return {
        "bill_id": bill.get("bill_id"),
        "bill_number": bill.get("bill_number", ""),
        "bill_type": bill.get("bill_type", ""),
        "state": bill.get("state", ""),
        "state_abbr": bill.get("state", ""),
        "session_id": bill.get("session", {}).get("session_id") if isinstance(bill.get("session"), dict) else bill.get("session_id"),
        "session_name": bill.get("session", {}).get("session_name", "") if isinstance(bill.get("session"), dict) else "",
        "title": title,
        "description": desc,
        "status": STATUS_MAP.get(bill.get("status"), "Unknown"),
        "status_date": bill.get("status_date", ""),
        "progress_stage": progress_label(progress),
        "progress": progress,
        "categories": classify_bill(title, desc),
        "subjects": subjects,
        "sponsors": sponsors,
        "history": history[-10:],  # keep last 10 actions
        "state_link": bill.get("state_link", ""),
        "legiscan_url": bill.get("url", ""),
        "change_hash": bill.get("change_hash", ""),
        "last_fetched": dt.date.today().isoformat(),
        "completed": bill.get("completed", 0),
    }


def run(dry_run=False, offline=False, searches_only=False, report_path=None):
    key = _api_key() if not offline else "OFFLINE"
    cache = load_cache()
    bills = cache.get("bills", {})

    if offline:
        print(f"Offline mode: {len(bills)} bills in cache")
    else:
        # Phase 1: search for bills
        seen_ids = {}
        for query in SEARCHES:
            print(f"  Searching: {query}")
            results = search_bills(key, query)
            for r in results:
                bid = str(r.get("bill_id"))
                if bid and bid not in seen_ids:
                    if is_relevant(r):
                        seen_ids[bid] = r
            time.sleep(0.5)

        print(f"  Found {len(seen_ids)} relevant bills across all searches")

        if searches_only:
            # Just report what we found
            for bid, r in sorted(seen_ids.items(), key=lambda x: x[1].get("state", "")):
                status = "NEW" if bid not in bills else "known"
                print(f"  [{status}] {r.get('state', '??')} {r.get('bill_number', '??')}: "
                      f"{r.get('title', '??')[:80]}")
            return

        # Phase 2: fetch details for new or changed bills
        to_fetch = []
        for bid, r in seen_ids.items():
            existing = bills.get(bid)
            if not existing:
                to_fetch.append(bid)
            elif existing.get("change_hash") != r.get("change_hash"):
                to_fetch.append(bid)

        print(f"  {len(to_fetch)} bills need detail fetch "
              f"({len(seen_ids) - len(to_fetch)} unchanged)")

        fetched = 0
        for bid in to_fetch:
            bill = get_bill(key, int(bid))
            if bill:
                bills[bid] = bill_to_record(bill)
                fetched += 1
            time.sleep(0.35)
            if fetched % 50 == 0 and fetched > 0:
                print(f"    ...fetched {fetched}/{len(to_fetch)}")

        print(f"  Fetched {fetched} bill details")

        # Mark bills no longer in search results but keep them (they may have
        # been enacted or died — still useful to show)
        for bid in bills:
            if bid not in seen_ids and not bills[bid].get("completed"):
                bills[bid]["_stale"] = True

        cache["bills"] = bills
        cache["search_meta"] = {
            "queries": SEARCHES,
            "total_found": len(seen_ids),
            "new_fetched": fetched,
            "run_date": dt.date.today().isoformat(),
        }

    # Report
    if report_path or dry_run:
        by_state = {}
        for b in bills.values():
            st = b.get("state", "??")
            by_state.setdefault(st, []).append(b)

        by_cat = {}
        for b in bills.values():
            for cat in b.get("categories", ["Other"]):
                by_cat.setdefault(cat, []).append(b)

        lines = [
            f"# Legislation Cache Report — {dt.date.today().isoformat()}",
            f"",
            f"**{len(bills)} bills** across **{len(by_state)} states**",
            f"",
            f"## By category",
        ]
        for cat in sorted(by_cat, key=lambda c: -len(by_cat[c])):
            lines.append(f"- {cat}: {len(by_cat[cat])}")
        lines.append("")
        lines.append("## By state (top 15)")
        for st in sorted(by_state, key=lambda s: -len(by_state[s]))[:15]:
            lines.append(f"- {st}: {len(by_state[st])}")
        lines.append("")

        # Recent activity
        active = sorted(
            [b for b in bills.values() if b.get("status_date")],
            key=lambda b: b["status_date"],
            reverse=True,
        )[:20]
        lines.append("## Recent activity (last 20)")
        for b in active:
            lines.append(
                f"- [{b['status_date']}] {b['state']} {b['bill_number']}: "
                f"{b['title'][:70]} — {b['status']}"
            )

        report = "\n".join(lines) + "\n"

        if report_path:
            Path(report_path).write_text(report)
            print(f"  Report: {report_path}")
        if dry_run:
            print(report)

    if not dry_run and not offline and not searches_only:
        save_cache(cache)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true",
                        help="Report without writing the cache")
    parser.add_argument("--offline", action="store_true",
                        help="Use cached data only, no API calls")
    parser.add_argument("--searches-only", action="store_true",
                        help="Run searches and report, skip getBill calls")
    parser.add_argument("--report", metavar="PATH",
                        help="Write a markdown report")
    args = parser.parse_args()
    run(dry_run=args.dry_run, offline=args.offline,
        searches_only=args.searches_only, report_path=args.report)


if __name__ == "__main__":
    main()
