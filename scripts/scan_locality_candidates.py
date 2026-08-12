#!/usr/bin/env python3
"""Mine the story tracker archive for towns/counties we don't recognize yet.

Most of data/story_candidates.json's "not yet localized" stories aren't
generic — they name a real town, they just aren't in the gazetteer
(DC_SITES_DF / LOCAL_BODIES_DF / MORATORIUMS_DF) yet, so
story_tracker.guess_locality() has nothing to match against. This script
finds the recurring names in that bucket and writes them to a review queue —
it does NOT touch LOCAL_BODIES_DF or MORATORIUMS_DF itself.

**Candidates never reach the public page.** A regex match on "Aurora
residents" doesn't know if that's Aurora, CO or Aurora, IL, or whether a
moratorium vote it names passed or failed. Adding a row to LOCAL_BODIES_DF
means reading that town's own governing-body page; adding one to
MORATORIUMS_DF means confirming the vote outcome from its own coverage.
Both are a human (or a Claude Code session doing real research, the way the
2026-08-11/12 batches were done) reading the candidate's example headlines
and verifying before writing anything — see CLAUDE.md's Data sourcing rules.
This script only decides what's worth that twenty minutes.

The queue file is stable across runs: entries keep their `first_seen` date,
and anything marked `"status": "dismissed"` (not a real distinct town, or
already covered under a different name) is never resurrected. Capped at
--max-new (default 39) newly-surfaced candidates per run so the queue grows
at a reviewable pace instead of dumping the whole backlog at once.

Usage:
    python3 scripts/scan_locality_candidates.py
    python3 scripts/scan_locality_candidates.py --max-new 20
    python3 scripts/scan_locality_candidates.py --dry-run
    python3 scripts/scan_locality_candidates.py --queue data/other.json

Deliberately stdlib-only + story_tracker (which is itself stdlib +
pandas) — no requests/streamlit — so the daily job installs nothing beyond
requirements-build.txt. Reads the already-fetched data/story_candidates.json
rather than hitting Google News again.
"""
import argparse
import datetime as dt
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import story_tracker                                    # noqa: E402
from src.constants import STATE_PUCS_DF                          # noqa: E402

# State names/abbrevs (with and without trailing punctuation, e.g. "N.J.",
# "Mass.") aren't distinct localities — they slip through the trigger-word
# pattern via headlines like "Most N.J. voters want...".
_STATE_NAMES_LOWER = {str(n).strip().lower() for n in STATE_PUCS_DF["state"]}
_STATE_ABBREV_FORMS = set()
for _abbrev in STATE_PUCS_DF["abbrev"]:
    a = str(_abbrev).strip().lower()
    _STATE_ABBREV_FORMS.add(a)
    _STATE_ABBREV_FORMS.add(".".join(a) + ".")   # "nj" -> "n.j."

ARCHIVE_PATH = Path(__file__).resolve().parent.parent / "data" / "story_candidates.json"
QUEUE_PATH = Path(__file__).resolve().parent.parent / "data" / "locality_candidates.json"

# A candidate needs a governance/civic-action word nearby, same spirit as
# scan_moratorium_candidates.py's ACTION_WORDS: "Springfield says hello"
# isn't a signal, but "Springfield residents" or "Springfield City Council"
# is. Order doesn't matter; this is an alternation, not a sequence.
_TRIGGER = (r"County|Township|Village|Borough|Parish|City Council|Town Board|"
           r"Board of Supervisors|Planning (?:Board|Commission)|Commissioners?|"
           r"Selectboard|Council|residents?|voters?|neighbors?|officials?|"
           r"leaders?|city\b")
_CANDIDATE_RE = re.compile(
    r"\b([A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+){0,2})\s+(?:" + _TRIGGER + r")\b")

# Common false positives the pattern's capitalized-phrase-before-trigger
# shape catches that are never a place name. Lowercased for comparison.
_STOPWORDS = {
    "data", "ai", "the", "as", "after", "why", "opinion", "residents",
    "local", "county", "new", "rural", "two", "court", "anti", "update",
    "still", "city", "also", "more", "most", "south", "north", "east",
    "west", "some", "many", "first", "second", "third", "see", "no",
    "this", "it", "that", "a", "an", "is", "has", "have", "will", "u.s.",
    "us", "in a", "this state",
}


def extract_candidates(stories):
    """[(name, count, [(title, outlet, link), ...]), ...] sorted by count
    desc, for stories with no locality/state already resolved. Each example
    list is capped at 3 — enough for a human to eyeball state/context
    without the queue file ballooning."""
    unresolved = [s for s in stories if not s.get("locality") and not s.get("state")]
    counts = Counter()
    examples = {}
    for s in unresolved:
        title = s.get("title", "")
        for m in _CANDIDATE_RE.finditer(title):
            name = m.group(1).strip()
            low = name.lower()
            # Drop the phrase's leading generic word ("Most N.J." -> "N.J.")
            # before the state check, since the modifier defeats an exact match.
            bare = re.sub(r"^(most|some|many)\s+", "", low)
            if (low in _STOPWORDS or len(name) < 3
                    or bare in _STATE_NAMES_LOWER or bare in _STATE_ABBREV_FORMS):
                continue
            counts[name] += 1
            ex = examples.setdefault(name, [])
            if len(ex) < 3:
                ex.append({"title": title, "outlet": s.get("outlet", ""),
                          "link": s.get("link", "")})
    return sorted(
        ((name, n, examples[name]) for name, n in counts.items()),
        key=lambda t: t[1], reverse=True)


def known_names(gazetteer):
    """Lowercased display names already in the gazetteer, so a candidate
    that's already tracked (just not yet matching this particular headline
    for some other reason) doesn't get queued again."""
    return {name.lower() for name, _state, _pattern in gazetteer}


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--archive", default=str(ARCHIVE_PATH),
                    help="path to data/story_candidates.json")
    ap.add_argument("--queue", default=str(QUEUE_PATH),
                    help="path to the review-queue JSON")
    ap.add_argument("--max-new", type=int, default=39,
                    help="cap on newly-surfaced candidates per run (default 39)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would be added, write nothing")
    args = ap.parse_args()

    archive_path = Path(args.archive)
    if not archive_path.exists():
        print(f"{archive_path} does not exist — nothing to scan.", file=sys.stderr)
        return 1
    stories = json.loads(archive_path.read_text(encoding="utf-8")).get("stories", [])

    gazetteer = story_tracker.build_gazetteer()
    already_tracked = known_names(gazetteer)
    found = extract_candidates(stories)
    found = [(name, n, ex) for name, n, ex in found
            if name.lower() not in already_tracked]

    today = dt.date.today().isoformat()
    path = Path(args.queue)
    payload = {"updated": today, "candidates": []}
    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"Queue file is not valid JSON ({e}); refusing to overwrite "
                  f"it. Fix or delete {path}.", file=sys.stderr)
            return 1
    existing = payload.get("candidates", [])
    by_name = {c["name"]: c for c in existing}

    added = 0
    for name, count, examples in found:
        if name in by_name:
            entry = by_name[name]
            entry["count"] = count               # refreshed each run
            entry["examples"] = examples
            entry["last_seen"] = today
            continue
        if added >= args.max_new:
            continue                              # cap newly-surfaced ones only
        existing.append({
            "name": name, "count": count, "examples": examples,
            "guess_state": story_tracker.guess_state(examples[0]["title"]) if examples else None,
            "first_seen": today, "last_seen": today, "status": "new",
        })
        by_name[name] = existing[-1]
        added += 1

    new_rows = [c for c in existing if c.get("status") == "new"]
    print(f"{len(found)} recurring untracked names found · {added} newly queued · "
          f"{len(new_rows)} awaiting review · {len(existing)} total in queue")

    for c in sorted(new_rows, key=lambda c: -c["count"])[:args.max_new]:
        if c.get("first_seen") == today:
            print(f"  [{c['count']}x, guess {c.get('guess_state') or '?'}] {c['name']}")

    if args.dry_run:
        print("(dry run — queue not written)")
        return 0

    existing.sort(key=lambda c: (c.get("status") != "new", -c.get("count", 0)))
    payload["updated"] = today
    payload["candidates"] = existing
    payload.setdefault("_readme", (
        "Review queue for towns/counties recurring in archived-but-unlocalized "
        "story tracker headlines (data/story_candidates.json). Generated by "
        "scripts/scan_locality_candidates.py, capped at --max-new (default 39) "
        "newly-surfaced names per run. Nothing here is published or cited "
        "anywhere on the site. To promote a candidate: research its "
        "governing body (its own .gov/town page, never a search snippet) "
        "and, if it has taken a real vote, its outcome from the vote's own "
        "coverage; add a LOCAL_BODIES_DF row (ongoing fight) and/or a "
        "MORATORIUMS_DF row (a confirmed enacted/rejected/proposed vote) in "
        "src/constants.py, then run "
        "`scripts/backfill_story_candidates.py --relabel` so already-archived "
        "stories for that place regroup correctly. Set this entry's status "
        "to 'promoted' once done, or 'dismissed' if it's not a real distinct "
        "place (a stopword slipped through, or it's already covered under a "
        "different name) — dismissed entries are never re-queued."))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
