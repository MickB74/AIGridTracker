#!/usr/bin/env python3
"""Mine intelligence for data-center projects we are not tracking yet.

The inbound half of the project tracker, and a sibling of
scan_moratorium_candidates.py. It gathers leads from several signals, drops
anything that already names a tracked project or locality, and writes what is
left to a review queue.

**Candidates never reach the public page.** A headline or a filing is not a
tracked project: it can be a rumour, a duplicate, a project that was cancelled,
or the same campus a third outlet already covered. Promotion into
data/projects.json is a HUMAN step, because that read is where each row's
`source` and `as_of` come from — and those are the whole point of the schema.
This script only decides what is worth a human's next twenty minutes.

Signals:
  * news    — Google News RSS, proposal/rezoning/hearing queries (default)
  * mega    — MEGA_PROJECTS_DF megaprojects not yet in the tracker (default)
  * ercot   — live ERCOT large-load interconnection scrape (--online only;
              needs the `requests`/service stack, so it is opt-in and never
              runs in the stdlib-only CI job)

SEC filings are deliberately NOT a lead source here: a 10-K gives company
capex, not a locality or a hearing date, so it enriches a project already in
the tracker rather than discovering one. Use src/services/sec_xbrl.py for that
in the app context.

The queue is stable across runs: entries keep their `first_seen` date, and
anything a human marks `"status": "dismissed"` is never resurrected.

Usage:
    python3 scripts/scan_project_candidates.py
    python3 scripts/scan_project_candidates.py --dry-run
    python3 scripts/scan_project_candidates.py --online     # also scrape ERCOT
    python3 scripts/scan_project_candidates.py --queue data/other.json

The default run is stdlib-only (urllib + ElementTree), so the weekly job
installs nothing beyond requirements-build.txt.
"""

import argparse
import datetime as dt
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.constants import (                                   # noqa: E402
    GOOGLE_NEWS_RSS, PROJECTS_DF, MEGA_PROJECTS_DF,
)
from src import story_tracker                                  # noqa: E402

QUEUE_PATH = Path(__file__).resolve().parent.parent / "data" / "project_candidates.json"

SEARCHES = [
    "data center rezoning public hearing",
    "data center special use permit planning commission",
    "data center proposed county board zoning",
    "hyperscale data center campus proposed",
    "data center site plan application approved",
    "data center billion investment announced county",
]

# A headline needs one SUBJECT word and one ACTION word. "Data center" alone
# pulls in every ribbon-cutting; the action words pin it to a project moving
# through a land-use process. "Moratorium"/"ban" hits are the sibling
# scanner's job and are filtered out below.
SUBJECT_WORDS = ("data center", "data centre", "data centers", "data centres",
                 "hyperscale", "server farm")
ACTION_WORDS = ("propos", "rezon", "special use", "special exception",
                "public hearing", "planning commission", "planning board",
                "site plan", "conditional use", "zoning", "approv", "permit",
                "application", "board of supervisors", "commissioners")
# Moratorium/ban stories belong to scan_moratorium_candidates.py, not here.
EXCLUDE_WORDS = ("moratorium", "ban ", "bans ", "banned")

BODY_WORDS = (r"County|City Council|Town Board|Township|Village|Borough|Parish|"
              r"Board of Supervisors|Planning Commission|Planning Board|"
              r"Board of Aldermen|Commissioners Court|Selectboard")
LOCALITY_RE = re.compile(
    r"\b([A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+){0,2})\s+(?:" + BODY_WORDS + r")\b")

UA = ("Mozilla/5.0 (compatible; GridWatchProjectScan/1.0; "
      "+https://aigridwatch.com)")


def _fetch(query, limit=25):
    """Headline dicts from Google News RSS. Returns [] on any failure."""
    url = GOOGLE_NEWS_RSS.format(q=urllib.parse.quote(query))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=25) as r:
            root = ET.fromstring(r.read())
    except Exception as e:                                    # noqa: BLE001
        print(f"  ! {query!r}: {type(e).__name__}: {e}", file=sys.stderr)
        return []

    out = []
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        src_el = it.find("source")
        source = src_el.text.strip() if src_el is not None and src_el.text else ""
        if source and title.endswith(f" - {source}"):
            title = title[: -(len(source) + 3)]
        out.append({
            "title": title,
            "outlet": source,
            "link": (it.findtext("link") or "").strip(),
            "published": (it.findtext("pubDate") or "").strip()[:16],
        })
        if len(out) >= limit:
            break
    return out


def _relevant(title):
    t = title.lower()
    if any(w in t for w in EXCLUDE_WORDS):
        return False
    return (any(w in t for w in SUBJECT_WORDS)
            and any(w in t for w in ACTION_WORDS))


def _guess_state(text):
    """State abbrev if the text names a state, else None.

    Delegates to story_tracker.guess_state, which is the one implementation
    that gets the abbreviation case right. Four copies of this logic had
    drifted apart: this one keyed its lookup on LOWERCASED abbreviations and
    matched case-sensitively, so the English words "in", "or", "ok", "me",
    "hi", "id", "la", "ma", "pa", "de", "co" and "al" each resolved to a
    state — "Data center ban proposed in Bernards Township" came back as
    Indiana. It was wrong in the other direction too, missing the postal form
    it was meant to catch ("Loudoun County, VA" resolved to nothing).
    """
    return story_tracker.guess_state(text)


def _guess_locality(title):
    m = LOCALITY_RE.search(title)
    return m.group(1).strip() if m else None


def _tracked_terms():
    """Lowercased project names + localities already in the tracker.

    Full names, not tokens, so "Loudoun County" doesn't shadow a new
    "Louisa County" lead. A hit on any of these means we already track it.
    """
    terms = set()
    for col in ("name", "locality"):
        for v in PROJECTS_DF[col]:
            s = str(v).lower().strip()
            if not s or s in ("nan", "none"):
                continue
            terms.add(s)
            terms.add(re.sub(r"\s*\(.*?\)\s*", "", s).strip())   # drop "(Fairfax County)"
    return {t for t in terms if t}


def scan_news():
    """News-RSS leads: proposal/rezoning/hearing headlines, deduped."""
    tracked = _tracked_terms()
    seen_links, candidates = set(), []
    for q in SEARCHES:
        for item in _fetch(q):
            title = item["title"]
            if not title or not _relevant(title):
                continue
            if item["link"] in seen_links:
                continue
            seen_links.add(item["link"])
            low = title.lower()
            if any(t in low for t in tracked):
                continue                          # already tracked
            candidates.append({
                "title": title,
                "outlet": item["outlet"],
                "link": item["link"],
                "published": item["published"],
                "guess_locality": _guess_locality(title),
                "guess_state": _guess_state(title),
                "query": q,
                "origin": "news-scan",
            })
    return candidates


def scan_megaprojects():
    """Known megaprojects (MEGA_PROJECTS_DF) not yet in the tracker.

    A GW-scale campus in the trade press is a project worth a tracker row even
    with no active local hearing — the interconnection-queue signal in static
    form. `link` gets a stable #fragment because these have no article URL.
    """
    tracked = _tracked_terms()
    out = []
    for _, r in MEGA_PROJECTS_DF.iterrows():
        name = str(r["project"]).strip()
        low = name.lower()
        if not name or any(t in low for t in tracked):
            continue
        loc = str(r["location"])
        out.append({
            "title": f"{name} — {r['company']} ({loc}); {r['invest']}, "
                     f"{r['capacity']}, {r['status']}",
            "outlet": "MEGA_PROJECTS_DF",
            "link": f"https://aigridwatch.com/data-centers#mega-{_slug(name)}",
            "published": "",
            "guess_locality": loc,
            "guess_state": _guess_state(loc),
            "query": "megaprojects",
            "origin": "megaprojects",
        })
    return out


def scan_ercot():
    """Live ERCOT large-load interconnection leads. Best-effort, opt-in.

    Imported lazily so the default stdlib-only run (and the CI job) never
    touches the requests/streamlit service stack. Returns [] on any failure.
    """
    try:
        from src.services.ercot import fetch_large_loads          # noqa: E402
        rows = fetch_large_loads()
    except Exception as e:                                        # noqa: BLE001
        print(f"  ! ercot: {type(e).__name__}: {e} (skipped)", file=sys.stderr)
        return []
    tracked = _tracked_terms()
    out = []
    for row in (rows or []):
        title = str(row.get("title") or row.get("name") or "").strip()
        link = str(row.get("link") or row.get("url") or "").strip()
        if not title or any(t in title.lower() for t in tracked):
            continue
        out.append({
            "title": f"ERCOT large load: {title}",
            "outlet": "ERCOT",
            "link": link or f"https://aigridwatch.com/data-centers#ercot-{_slug(title)}",
            "published": str(row.get("date") or ""),
            "guess_locality": None,
            "guess_state": "TX",
            "query": "ercot-large-load",
            "origin": "ercot",
        })
    return out


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def duplicate_links(existing):
    """Links used by more than one queue entry — `link` is the dedup key."""
    counts = {}
    for e in existing:
        link = e.get("link")
        if link:
            counts[link] = counts.get(link, 0) + 1
    return {link: n for link, n in counts.items() if n > 1}


def merge(existing, found, today):
    """Fold new leads into the queue without disturbing human decisions."""
    by_link = {}
    for e in existing:
        if e.get("link"):
            by_link.setdefault(e["link"], []).append(e)
    added = 0
    for c in found:
        prior = by_link.get(c["link"])
        if prior:
            for e in prior:                       # never clobber a duplicate
                e["last_seen"] = today
            continue
        if any(e.get("status") == "dismissed"
               and e.get("title") == c["title"] for e in existing):
            continue                              # a human already said no
        c.update({"first_seen": today, "last_seen": today, "status": "new"})
        existing.append(c)
        by_link.setdefault(c["link"], []).append(c)
        added += 1
    existing.sort(key=lambda e: (e.get("status") != "new",
                                 e.get("first_seen", "")))
    return added


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--queue", default=str(QUEUE_PATH),
                    help="path to the review-queue JSON")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would be added, write nothing")
    ap.add_argument("--online", action="store_true",
                    help="also scrape live ERCOT large loads (needs requests)")
    args = ap.parse_args()

    path = Path(args.queue)
    today = dt.date.today().isoformat()

    payload = {"updated": today, "candidates": []}
    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"Queue file is not valid JSON ({e}); refusing to overwrite "
                  f"it. Fix or delete {path}.", file=sys.stderr)
            return 1
    existing = payload.get("candidates", [])

    found = scan_news() + scan_megaprojects()
    if args.online:
        found += scan_ercot()
    added = merge(existing, found, today)

    new_rows = [e for e in existing if e.get("status") == "new"]
    print(f"{len(found)} leads · {added} new candidate(s) · "
          f"{len(new_rows)} awaiting review · {len(existing)} total")

    for link, n in sorted(duplicate_links(existing).items()):
        print(f"  ! {n} entries share {link} — give each a distinct #fragment",
              file=sys.stderr)

    for c in existing[:15]:
        if c.get("status") != "new":
            continue
        where = " / ".join(x for x in (c.get("guess_locality"),
                                       c.get("guess_state")) if x) or "?"
        print(f"  [{where}] {c['title'][:96]}")

    if args.dry_run:
        print("(dry run — queue not written)")
        return 0

    payload["updated"] = today
    payload["candidates"] = existing
    payload.setdefault("_readme", (
        "Review queue for the identified-project tracker. Entries are "
        "UNVERIFIED leads from a news/registry scan and are never published. "
        "To promote one: read the governing body's own agenda or the reporting, "
        "add a record to data/projects.json with source + as_of (and any known "
        "milestone dates), then set this entry's status to 'promoted'. To "
        "reject one, set status to 'dismissed' — the scanner will not raise it "
        "again. `link` is the dedup key and must be unique per entry; a "
        "hand-added lead that cites an index page needs a distinct #fragment."))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
