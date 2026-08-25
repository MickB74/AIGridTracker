#!/usr/bin/env python3
"""Sweep the story archive for moratoriums the tracker is missing.

The news-scan scanner (`scan_moratorium_candidates.py`) queries Google News
live for a handful of moratorium-specific searches.  This script mines the
**existing** story archive (`data/story_candidates.json`) — 1 500+ headlines
already collected by the daily site build — with a much broader keyword net
and organizes the results by state and locality.

Why broader?  Headlines about the same ordinance use different words:
"council votes to restrict", "zoning change blocks", "supervisors reject
proposal", "residents demand pause."  The narrow scanner misses these.

Output goes to the same `data/moratorium_candidates.json` queue with
`origin: "archive-sweep"`.  Same rules apply: entries are leads, not facts,
and promotion into MORATORIUMS_DF is a human step.

Usage:
    python3 scripts/sweep_moratoriums_from_archive.py
    python3 scripts/sweep_moratoriums_from_archive.py --dry-run
    python3 scripts/sweep_moratoriums_from_archive.py --report

Deliberately stdlib-only (runs in CI off requirements-build.txt).
"""

import argparse
import datetime as dt
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.constants import MORATORIUMS_DF                 # noqa: E402
from src import story_tracker                            # noqa: E402

ARCHIVE_PATH = (Path(__file__).resolve().parent.parent
                / "data" / "story_candidates.json")
QUEUE_PATH = (Path(__file__).resolve().parent.parent
              / "data" / "moratorium_candidates.json")

# ── Keyword tiers ────────────────────────────────────────────────────────
# Tier 1: explicit moratorium language (high signal)
TIER1_ACTION = (
    "moratorium", "ban ", "bans ", "banned", "banning",
    "pause", "paused", "pauses",
    "halt", "halts", "halted",
    "freeze", "freezes", "froze", "frozen",
    "rescind", "rescinded",
)
# Tier 2: governing-body actions that often indicate a moratorium
TIER2_ACTION = (
    "blocks", "blocked", "blocking",
    "rejects", "rejected", "rejection",
    "denies", "denied", "denial",
    "restricts", "restricted", "restriction",
    "opposes", "opposed", "opposition",
    "votes no", "voted no",
    "votes against",
    "stops", "stopped",
    "prevents", "prevented",
    "ordinance",
    "zoning change",
)
SUBJECT = (
    "data center", "data centre", "data centers", "data centres",
    "hyperscale", "ai facility", "ai facilities",
)

# Governing-body hints for locality extraction
BODY_WORDS = (
    r"County|City Council|Town Board|Township|Village|Borough|Parish|"
    r"Board of Supervisors|Planning Commission|Board of Aldermen|"
    r"Commissioners Court|Selectboard|Metro Council|"
    r"Town Council|City of|supervisors|commissioners|council"
)
LOCALITY_RE = re.compile(
    r"\b([A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+){0,2})\s+(?:"
    + BODY_WORDS + r")\b")


def _tracked_names():
    names = set()
    for loc in MORATORIUMS_DF["locality"]:
        s = str(loc).lower()
        names.add(s)
        names.add(re.sub(r"\s*\(.*?\)\s*", "", s).strip())
    return {n for n in names if n}


def _guess_state(title):
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
    return story_tracker.guess_state(title)


def _guess_locality(title):
    m = LOCALITY_RE.search(title)
    return m.group(1).strip() if m else None


def _is_tier1(title_lower):
    return (any(w in title_lower for w in SUBJECT)
            and any(w in title_lower for w in TIER1_ACTION))


def _is_tier2(title_lower):
    return (any(w in title_lower for w in SUBJECT)
            and any(w in title_lower for w in TIER2_ACTION))


def sweep(archive_path=ARCHIVE_PATH):
    """Return candidate dicts from the story archive."""
    data = json.loads(archive_path.read_text(encoding="utf-8"))
    stories = data.get("stories", [])
    tracked = _tracked_names()

    candidates = []
    for s in stories:
        title = (s.get("title") or "").strip()
        if not title:
            continue
        t_low = title.lower()

        tier = None
        if _is_tier1(t_low):
            tier = 1
        elif _is_tier2(t_low):
            tier = 2
        else:
            continue

        # Skip if the story's locality is already tracked
        loc_field = (s.get("locality") or "").lower()
        if loc_field and loc_field in tracked:
            continue
        # Also check against the title
        if any(n in t_low for n in tracked if len(n) > 4):
            continue

        guess_loc = s.get("locality") or _guess_locality(title)
        guess_st = _guess_state(title)

        candidates.append({
            "title": title,
            "outlet": s.get("source", ""),
            "link": s.get("link", ""),
            "published": (s.get("first_seen") or "")[:10],
            "guess_locality": guess_loc,
            "guess_state": guess_st,
            "tier": tier,
        })

    # Deduplicate by link
    seen = set()
    deduped = []
    for c in candidates:
        if c["link"] not in seen:
            seen.add(c["link"])
            deduped.append(c)
    return deduped


def report(candidates):
    """Print an organized summary by state and locality."""
    by_state = defaultdict(lambda: defaultdict(list))
    no_state = []
    for c in candidates:
        st = c.get("guess_state")
        loc = c.get("guess_locality") or "Unknown locality"
        if st:
            by_state[st][loc].append(c)
        else:
            no_state.append(c)

    total_t1 = sum(1 for c in candidates if c["tier"] == 1)
    total_t2 = sum(1 for c in candidates if c["tier"] == 2)
    print(f"\n{'='*60}")
    print(f"MORATORIUM SWEEP REPORT")
    print(f"{'='*60}")
    print(f"Total candidates: {len(candidates)} "
          f"(tier 1: {total_t1}, tier 2: {total_t2})")
    print(f"States: {len(by_state)}")
    print()

    for st in sorted(by_state):
        locs = by_state[st]
        count = sum(len(v) for v in locs.values())
        print(f"── {st} ({count} stories) {'─'*40}")
        for loc in sorted(locs):
            stories = locs[loc]
            tier_label = "T1" if any(s["tier"] == 1 for s in stories) else "T2"
            print(f"  [{tier_label}] {loc} ({len(stories)} stories)")
            for s in stories[:3]:
                print(f"       {s['published']}  {s['title'][:80]}")
            if len(stories) > 3:
                print(f"       ... +{len(stories)-3} more")
        print()

    if no_state:
        print(f"── No state identified ({len(no_state)} stories) ─────────")
        for s in no_state[:10]:
            print(f"  {s['published']}  {s['title'][:80]}")
        if len(no_state) > 10:
            print(f"  ... +{len(no_state)-10} more")
    print()


def merge_into_queue(candidates, queue_path, today):
    """Merge candidates into the moratorium_candidates.json queue."""
    payload = {"updated": today, "candidates": []}
    if queue_path.exists():
        try:
            payload = json.loads(queue_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"Queue file is not valid JSON ({e}); refusing to overwrite.",
                  file=sys.stderr)
            return -1, None
    existing = payload.get("candidates", [])

    by_link = {}
    for e in existing:
        if e.get("link"):
            by_link.setdefault(e["link"], []).append(e)

    added = 0
    for c in candidates:
        prior = by_link.get(c["link"])
        if prior:
            for e in prior:
                e["last_seen"] = today
            continue
        if any(e.get("status") == "dismissed" and e.get("title") == c["title"]
               for e in existing):
            continue
        c.update({"first_seen": today, "last_seen": today,
                  "status": "new",
                  "origin": "archive-sweep"})
        existing.append(c)
        by_link.setdefault(c["link"], []).append(c)
        added += 1

    existing.sort(key=lambda e: (e.get("status") != "new",
                                 e.get("first_seen", "")))
    payload["updated"] = today
    payload["candidates"] = existing
    return added, payload


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would be added, write nothing")
    ap.add_argument("--report", action="store_true",
                    help="print organized report by state/locality")
    ap.add_argument("--queue", default=str(QUEUE_PATH))
    ap.add_argument("--archive", default=str(ARCHIVE_PATH))
    args = ap.parse_args()

    archive_path = Path(args.archive)
    queue_path = Path(args.queue)
    today = dt.date.today().isoformat()

    if not archive_path.exists():
        print(f"Archive not found at {archive_path}", file=sys.stderr)
        return 1

    candidates = sweep(archive_path)
    print(f"Swept {archive_path.name}: {len(candidates)} candidates")

    if args.report or args.dry_run:
        report(candidates)

    if args.dry_run:
        print("(dry run — queue not written)")
        return 0

    added, payload = merge_into_queue(candidates, queue_path, today)
    if added < 0:
        return 1

    queue_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")

    new_count = sum(1 for c in payload["candidates"]
                    if c.get("status") == "new")
    print(f"{added} new candidate(s) merged into queue · "
          f"{new_count} awaiting review · "
          f"{len(payload['candidates'])} total")
    print(f"Wrote {queue_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
