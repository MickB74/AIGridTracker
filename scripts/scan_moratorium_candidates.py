#!/usr/bin/env python3
"""Mine the news feed for moratoriums we are not tracking yet.

This is the inbound half of keeping the tracker current. It reads the same
Google News RSS the site already uses, keeps headlines that look like a
governing body pausing or banning data centers, drops anything that names a
locality already in MORATORIUMS_DF, and writes what is left to a review queue.

**Candidates never reach the public page.** A headline is not an ordinance:
it can describe a vote that failed, a proposal that was withdrawn, or the same
action a third outlet already reported. Promotion into MORATORIUMS_DF is a
human step, because that is where `source` and `as_of` come from — and those
are the whole point of the schema. The script only decides what is worth a
human's next twenty minutes.

The queue file is stable across runs: entries keep their `first_seen` date,
and anything a human marks `"status": "dismissed"` is never resurrected, so
the same false positive does not come back every week.

Usage:
    python3 scripts/scan_moratorium_candidates.py
    python3 scripts/scan_moratorium_candidates.py --dry-run
    python3 scripts/scan_moratorium_candidates.py --queue data/other.json

Deliberately stdlib-only (urllib + ElementTree, not requests/streamlit), so
the weekly job installs nothing beyond requirements-build.txt.
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
    GOOGLE_NEWS_RSS, MORATORIUMS_DF, STATE_PUCS_DF,
)

QUEUE_PATH = Path(__file__).resolve().parent.parent / "data" / "moratorium_candidates.json"

SEARCHES = [
    "data center moratorium city council",
    "data center moratorium county commission approved",
    "data center ban zoning ordinance town board",
    "data center moratorium extended",
    "data center moratorium rescinded lawsuit",
]

# A headline needs one word from each list. "Moratorium" alone pulls in
# housing and short-term rentals; "data center" alone pulls in every
# groundbreaking announcement in the country.
ACTION_WORDS = ("moratorium", "ban ", "bans ", "banned", "pause", "paused",
                "halt", "freeze", "rescind", "rescinded", "repeal")
SUBJECT_WORDS = ("data center", "data centre", "data centers", "data centres",
                 "hyperscale")

# Enough of a hint to triage on. Explicitly a guess — the human reading the
# queue confirms the locality from the article, not from this regex.
BODY_WORDS = (r"County|City Council|Town Board|Township|Village|Borough|Parish|"
              r"Board of Supervisors|Planning Commission|Board of Aldermen|"
              r"Commissioners Court|Selectboard")
LOCALITY_RE = re.compile(
    r"\b([A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+){0,2})\s+(?:" + BODY_WORDS + r")\b")

UA = ("Mozilla/5.0 (compatible; GridWatchNewsScan/1.0; "
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
    return (any(w in t for w in SUBJECT_WORDS)
            and any(w in t for w in ACTION_WORDS))


def _guess_state(title):
    """State abbrev if the headline names a state, else None."""
    for _, r in STATE_PUCS_DF.iterrows():
        name, abbrev = str(r["state"]), str(r["abbrev"])
        if re.search(rf"\b{re.escape(name)}\b", title):
            return abbrev
        if re.search(rf"\b{re.escape(abbrev)}\b", title):
            return abbrev
    return None


def _guess_locality(title):
    m = LOCALITY_RE.search(title)
    return m.group(1).strip() if m else None


def _tracked_names():
    """Lowercased locality names already in the tracker, plus bare county names.

    "Gordon County" must not match the tracked "Gates County", so this keeps
    full names rather than single tokens.
    """
    names = set()
    for loc in MORATORIUMS_DF["locality"]:
        s = str(loc).lower()
        names.add(s)
        # "Lysander (Onondaga Co.)" -> "lysander"
        names.add(re.sub(r"\s*\(.*?\)\s*", "", s).strip())
    return {n for n in names if n}


def scan():
    tracked = _tracked_names()
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
            if any(n in low for n in tracked):
                continue                      # already on the page

            candidates.append({
                "title": title,
                "outlet": item["outlet"],
                "link": item["link"],
                "published": item["published"],
                "guess_locality": _guess_locality(title),
                "guess_state": _guess_state(title),
                "query": q,
            })
    return candidates


def duplicate_links(existing):
    """Links used by more than one queue entry.

    `link` is the dedup key, so it has to be unique per entry. Hand-added
    candidates are the risk: four rows once shared a tracker's bare homepage
    URL, which made three of them invisible to the dedup map and would have
    silently swallowed any later hit on that URL. Give hand-added entries a
    `#slug` fragment rather than reusing a landing page.
    """
    counts = {}
    for e in existing:
        link = e.get("link")
        if link:
            counts[link] = counts.get(link, 0) + 1
    return {link: n for link, n in counts.items() if n > 1}


def merge(existing, found, today):
    """Fold new hits into the queue without disturbing human decisions."""
    by_link = {}
    for e in existing:
        if e.get("link"):
            by_link.setdefault(e["link"], []).append(e)
    added = 0
    for c in found:
        prior = by_link.get(c["link"])
        if prior:
            for e in prior:               # never clobber a shadowed duplicate
                e["last_seen"] = today
            continue
        if any(e.get("status") == "dismissed"
               and e.get("title") == c["title"] for e in existing):
            continue                          # a human already said no
        c.update({"first_seen": today, "last_seen": today,
                  "status": "new", "origin": "news-scan"})
        existing.append(c)
        by_link.setdefault(c["link"], []).append(c)
        added += 1
    existing.sort(key=lambda e: (e.get("status") != "new",
                                 e.get("first_seen", "")), reverse=False)
    return added


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--queue", default=str(QUEUE_PATH),
                    help="path to the review-queue JSON")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would be added, write nothing")
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

    found = scan()
    added = merge(existing, found, today)

    new_rows = [e for e in existing if e.get("status") == "new"]
    print(f"{len(found)} relevant headlines · {added} new candidate(s) · "
          f"{len(new_rows)} awaiting review · {len(existing)} total")

    for link, n in sorted(duplicate_links(existing).items()):
        print(f"  ! {n} entries share {link} — `link` is the dedup key, so "
              f"give each a distinct #fragment", file=sys.stderr)

    for c in existing[:15]:
        if c.get("status") != "new":
            continue
        where = " / ".join(x for x in (c.get("guess_locality"),
                                       c.get("guess_state")) if x) or "?"
        print(f"  [{where}] {c['title']}")

    if args.dry_run:
        print("(dry run — queue not written)")
        return 0

    payload["updated"] = today
    payload["candidates"] = existing
    payload.setdefault("_readme", (
        "Review queue for the moratorium tracker. Entries are UNVERIFIED "
        "leads from a news scan and are never published. To promote one: read "
        "the locality's own ordinance or agenda, add a row to MORATORIUMS in "
        "src/constants.py with source + as_of + expires, then set this "
        "entry's status to 'promoted'. To reject one, set status to "
        "'dismissed' — the scanner will not raise it again. `link` is the "
        "dedup key and must be unique per entry: a hand-added candidate that "
        "cites a tracker or index page needs a distinct #fragment, not the "
        "bare URL."))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
