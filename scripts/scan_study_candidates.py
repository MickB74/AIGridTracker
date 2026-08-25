#!/usr/bin/env python3
"""Mine the news feed for state data-center studies we aren't tracking yet.

This is the inbound half of keeping the studies library current. It reads the
same Google News RSS the site already uses, keeps headlines that look like a
state legislature, PUC, energy department, or audit agency publishing a study
on data centers, and writes what's left to a review queue.

**Candidates never reach the public page.** A headline is not a report: it can
describe a study that was merely *proposed*, a press release restating an old
one, or a third outlet covering something already in the library. Promotion
into STATE_STUDIES is a human step — read the actual report, summarise its
findings, and stamp the `as_of` you read it on. The script only decides what
is worth a human's next twenty minutes.

Unlike the moratorium scanner, this does **not** drop headlines that name a
state already in the library: a state can publish a *newer edition* that
supersedes what we summarise, and that is exactly what we want to catch. Each
candidate is annotated with `state_tracked` so the reviewer can tell a brand
new state from a possible update.

The queue file is stable across runs: entries keep their `first_seen` date,
and anything a human marks `"status": "dismissed"` is never resurrected.

Usage:
    python3 scripts/scan_study_candidates.py
    python3 scripts/scan_study_candidates.py --dry-run
    python3 scripts/scan_study_candidates.py --queue data/other.json

Deliberately stdlib-only (urllib + ElementTree, not requests/streamlit), so
the daily job installs nothing beyond requirements-build.txt.
"""

import argparse
import ast
import datetime as dt
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.constants import GOOGLE_NEWS_RSS, STATE_PUCS_DF       # noqa: E402
from src import story_tracker                                  # noqa: E402

_ABBREV_TO_NAME = dict(zip(STATE_PUCS_DF["abbrev"], STATE_PUCS_DF["state"]))

ROOT = Path(__file__).resolve().parent.parent
QUEUE_PATH = ROOT / "data" / "study_candidates.json"
STUDIES_SRC = ROOT / "src" / "ui" / "state_detail.py"

SEARCHES = [
    "data center legislative study state",
    "data center impact study commissioned",
    "data center legislative audit report",
    "data center task force report recommendations",
    "public utility commission data center report",
    "state energy office data center study",
]

# A headline needs one word from each list. "Study"/"report" alone pulls in
# every think-tank and vendor white paper; "data center" alone pulls in every
# groundbreaking in the country. Requiring both, plus an official-body hint
# below, is what keeps this to government-commissioned work.
SUBJECT_WORDS = ("data center", "data centre", "data centers", "data centres",
                 "hyperscale")
STUDY_WORDS = ("study", "studies", "report", "audit", "task force",
               "commission", "legislative", "analysis", "assessment",
               "inquiry", "review", "findings")

# At least one of these must appear too, so a vendor's "market report" or an
# advocacy group's "analysis" doesn't masquerade as a state study. The human
# reviewer still confirms the commissioning body from the article.
OFFICIAL_WORDS = ("legislature", "legislative", "general assembly", "senate",
                  "house", "committee", "commission", "public utility",
                  "public service", "utility commission", "department of energy",
                  "energy office", "auditor", "comptroller", "audit",
                  "regulators", "state study", "task force", "governor",
                  "attorney general", "jlarc")

UA = ("Mozilla/5.0 (compatible; GridWatchStudyScan/1.0; "
      "+https://aigridwatch.com)")


def load_tracked_states():
    """State names already in STATE_STUDIES (read via ast, no streamlit)."""
    tree = ast.parse(STUDIES_SRC.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if getattr(target, "id", None) == "STATE_STUDIES":
                    return set(ast.literal_eval(node.value).keys())
    return set()


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
            and any(w in t for w in STUDY_WORDS)
            and any(w in t for w in OFFICIAL_WORDS))


def _guess_state(title):
    """(full name, abbrev) if the headline names a state, else (None, None).

    Wraps story_tracker.guess_state — see the note in the sibling scanners on
    why four hand-rolled copies of this became one.
    """
    abbrev = story_tracker.guess_state(title)
    if not abbrev:
        return None, None
    return _ABBREV_TO_NAME.get(abbrev), abbrev


def scan(tracked_states):
    seen_links, candidates = set(), []

    for q in SEARCHES:
        for item in _fetch(q):
            title = item["title"]
            if not title or not _relevant(title):
                continue
            if item["link"] in seen_links:
                continue
            seen_links.add(item["link"])

            name, abbrev = _guess_state(title)
            candidates.append({
                "title": title,
                "outlet": item["outlet"],
                "link": item["link"],
                "published": item["published"],
                "guess_state": name,
                "guess_abbrev": abbrev,
                # A hit on a state we already cover is likely a NEW edition,
                # not a duplicate — flagged, never dropped.
                "state_tracked": bool(name and name in tracked_states),
                "query": q,
            })
    return candidates


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
            for e in prior:
                e["last_seen"] = today
                # A state we started tracking since first sighting is now an
                # update lead, not a new-state lead — keep the flag current.
                e["state_tracked"] = c["state_tracked"]
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

    tracked = load_tracked_states()
    found = scan(tracked)
    added = merge(existing, found, today)

    new_rows = [e for e in existing if e.get("status") == "new"]
    print(f"{len(found)} relevant headlines · {added} new candidate(s) · "
          f"{len(new_rows)} awaiting review · {len(existing)} total")

    for c in existing[:15]:
        if c.get("status") != "new":
            continue
        flag = " [UPDATE?]" if c.get("state_tracked") else ""
        where = c.get("guess_state") or "?"
        print(f"  [{where}]{flag} {c['title']}")

    if args.dry_run:
        print("(dry run — queue not written)")
        return 0

    payload["updated"] = today
    payload["candidates"] = existing
    payload.setdefault("_readme", (
        "Review queue for the state-studies library (STATE_STUDIES in "
        "src/ui/state_detail.py). Entries are UNVERIFIED leads from a news "
        "scan and are never published. `state_tracked: true` means the state "
        "is already in the library, so this is probably a NEWER EDITION worth "
        "checking, not a duplicate. To promote one: read the actual report, "
        "add or update the STATE_STUDIES entry with src_key/pdf_url + an "
        "as_of set to the date you read it, then set this entry's status to "
        "'promoted'. To reject one, set status to 'dismissed' — the scanner "
        "will not raise it again. `link` is the dedup key and must be unique "
        "per entry."))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
