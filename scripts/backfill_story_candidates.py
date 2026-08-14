#!/usr/bin/env python3
"""One-time (or occasional) backfill of the story tracker archive.

The regular build only ever fetches Google News' `when:7d` window, so as
long as the daily build never has a gap longer than a week it eventually
sees everything — except for history from before the story tracker existed.
This widens the same STORY_QUERY to a longer lookback and merges whatever
Google still indexes for it into data/story_candidates.json, using the same
merge semantics as the regular build (dedup by link; the earliest known
published date wins as first_seen — see story_tracker.merge_stories).

Google News RSS returns roughly its 100 most relevant hits for a query
regardless of window size, so a wider `when:` mostly recovers older stories
that would otherwise be crowded out by the last week's volume — this is a
best-effort catch-up, not a complete crawl of the past N days.

Usage:
    python3 scripts/backfill_story_candidates.py            # last 28 days
    python3 scripts/backfill_story_candidates.py --days 14
    python3 scripts/backfill_story_candidates.py --dry-run
    python3 scripts/backfill_story_candidates.py --relabel  # re-tag existing
                                                              # entries against
                                                              # the current
                                                              # gazetteer

Deliberately stdlib-only (urllib + ElementTree, not requests/streamlit),
matching the other scripts/ jobs.
"""
import argparse
import datetime as dt
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.constants import (                                       # noqa: E402
    GOOGLE_NEWS_RSS, STORY_QUERY, STORY_ANGLES, STORY_IMPACT_WEIGHTS,
)
from src import story_tracker                                    # noqa: E402

# STORY_QUERY's own OR-clause already keyword-filters at the Google end, so
# the default path needs no local check. A custom --query (e.g. "Kenilworth
# New Jersey data center") has no such filter and returns EVERYTHING about
# the place — stock analysis, HQ-relocation announcements, industry-group
# press releases — none of which is a community-impact story. This allowlist
# (reusing the same keyword sets the live feed already classifies angles
# and ranks urgency with) keeps a targeted deep-dive on topic.
_RELEVANCE_KEYWORDS = (set(STORY_IMPACT_WEIGHTS)
                      | {kw for keys, _, _ in STORY_ANGLES for kw in keys}
                      | {"resident", "residents", "protest", "oppose",
                         "concern", "hearing", "backlash", "outcry",
                         # bans/lawsuits/statehouse terms, matching
                         # STORY_QUERY_ACTIONS so a targeted --query keeps
                         # the same stories the live feed now pulls
                         "ordinance", "rezoning", "zoning", "legislation",
                         "legislature", "regulate", "regulation", "tax credit",
                         "guardrail", "governor"})


def _is_relevant(title):
    t = (title or "").lower()
    return any(kw in t for kw in _RELEVANCE_KEYWORDS)

QUEUE_PATH = Path(__file__).resolve().parent.parent / "data" / "story_candidates.json"

UA = ("Mozilla/5.0 (compatible; GridWatchStoryBackfill/1.0; "
      "+https://aigridwatch.com)")


def _widen_query(days, base_query=STORY_QUERY):
    widened, n = re.subn(r"when:\d+d", f"when:{days}d", base_query)
    if not n:
        widened = f"{base_query} when:{days}d"
    return widened


def _fetch(query, limit=100):
    url = GOOGLE_NEWS_RSS.format(q=urllib.parse.quote(query))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        root = ET.fromstring(r.read())

    out = []
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        src_el = it.find("source")
        source = src_el.text.strip() if src_el is not None and src_el.text else ""
        if source and title.endswith(f" - {source}"):
            title = title[: -(len(source) + 3)]
        pub_raw = (it.findtext("pubDate") or "").strip()
        pub_iso = ""
        if pub_raw:
            try:
                pub_iso = parsedate_to_datetime(pub_raw).isoformat()
            except Exception:                                    # noqa: BLE001
                pub_iso = ""
        out.append({
            "title": title, "outlet": source,
            "link": (it.findtext("link") or "").strip(),
            "published": pub_raw, "published_iso": pub_iso,
        })
        if len(out) >= limit:
            break
    return out


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=28,
                    help="lookback window in days (default 28)")
    ap.add_argument("--query", default=None,
                    help="override the base query text (default: STORY_QUERY) "
                         "for a targeted deep-dive on one place, e.g. "
                         "'Kenilworth New Jersey data center'")
    ap.add_argument("--queue", default=str(QUEUE_PATH),
                    help="path to the story archive JSON")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would be added, write nothing")
    ap.add_argument("--relabel", action="store_true",
                    help="skip fetching; re-run guess_locality/guess_state "
                         "over every archived story and fix any that now "
                         "match a locality added to the gazetteer since it "
                         "was archived. Locality/state are set once at fetch "
                         "time otherwise, so a place added to LOCAL_BODIES_DF/"
                         "MORATORIUMS_DF/DC_SITES_DF after the fact needs this "
                         "to retroactively group its already-archived stories.")
    args = ap.parse_args()
    today = dt.date.today().isoformat()

    if args.relabel:
        path = Path(args.queue)
        payload = json.loads(path.read_text(encoding="utf-8"))
        stories = payload.get("stories", [])
        gazetteer = story_tracker.build_gazetteer()
        changed = 0
        for s in stories:
            if s.get("locality"):
                continue                                          # already tagged
            locality, state = story_tracker.guess_locality(s.get("title", ""), gazetteer)
            if not state:
                state = story_tracker.guess_state(s.get("title", ""))
            if locality != s.get("locality") or (locality and state != s.get("state")):
                s["locality"], s["state"] = locality, state
                changed += 1
        print(f"Relabeled {changed} of {len(stories)} archived stories")
        if args.dry_run:
            print("(dry run — archive not written)")
            return 0
        payload["updated"] = today
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
        print(f"Wrote {path}")
        return 0

    base_query = args.query or STORY_QUERY
    query = _widen_query(args.days, base_query)

    try:
        found = _fetch(query)
    except Exception as e:                                        # noqa: BLE001
        print(f"Fetch failed: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    print(f"Fetched {len(found)} headlines over the last {args.days} days "
          f"({query!r})")

    if args.query:
        before = len(found)
        found = [it for it in found if _is_relevant(it["title"])]
        print(f"  filtered to {len(found)} community-impact headlines "
              f"(dropped {before - len(found)} off-topic — custom queries "
              f"aren't pre-filtered by Google the way STORY_QUERY is)")

    gazetteer = story_tracker.build_gazetteer()
    records = []
    for it in found:
        if not it["title"] or not it["link"]:
            continue
        locality, state = story_tracker.guess_locality(it["title"], gazetteer)
        if not state:
            state = story_tracker.guess_state(it["title"])
        records.append({
            "title": it["title"], "outlet": it["outlet"], "link": it["link"],
            "published": it["published"], "published_iso": it["published_iso"],
            "locality": locality, "state": state,
            "first_seen": story_tracker.date_from_iso(it["published_iso"], today),
            "last_seen": today,
        })

    path = Path(args.queue)
    payload = {"updated": today, "stories": []}
    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"{path} is not valid JSON ({e}); refusing to overwrite it.",
                  file=sys.stderr)
            return 1
    existing = payload.get("stories", [])
    before = len(existing)
    added = story_tracker.merge_stories(existing, records, today)
    localized = sum(1 for r in records if r["locality"] or r["state"])
    print(f"{added} new · {before} -> {len(existing)} total archived · "
          f"{localized}/{len(records)} of this fetch tagged with a place")

    if args.dry_run:
        print("(dry run — archive not written)")
        return 0

    payload["updated"] = today
    payload["stories"] = existing
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
