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

from src.constants import GOOGLE_NEWS_RSS, STORY_QUERY          # noqa: E402
from src import story_tracker                                    # noqa: E402

QUEUE_PATH = Path(__file__).resolve().parent.parent / "data" / "story_candidates.json"

UA = ("Mozilla/5.0 (compatible; GridWatchStoryBackfill/1.0; "
      "+https://aigridwatch.com)")


def _widen_query(days):
    widened, n = re.subn(r"when:\d+d", f"when:{days}d", STORY_QUERY)
    if not n:
        widened = f"{STORY_QUERY} when:{days}d"
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
    ap.add_argument("--queue", default=str(QUEUE_PATH),
                    help="path to the story archive JSON")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would be added, write nothing")
    args = ap.parse_args()

    query = _widen_query(args.days)
    today = dt.date.today().isoformat()

    try:
        found = _fetch(query)
    except Exception as e:                                        # noqa: BLE001
        print(f"Fetch failed: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    print(f"Fetched {len(found)} headlines over the last {args.days} days "
          f"({query!r})")

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
