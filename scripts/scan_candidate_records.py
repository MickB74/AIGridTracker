#!/usr/bin/env python3
"""
Find candidate statements on data centers that the race trackers don't have yet.

Mines the story archive (`data/story_candidates.json` — the same running feed
behind story-tracker.html) for headlines that name a 2026 Senate or House
candidate AND mention data centers or AI, and files anything not already
published into `data/candidate_record_candidates.json`.

**A review queue, never a registry.** This script does not touch AI_RECORDS in
src/senate_races.py or src/house_races.py, and it must not be changed to. A
record on those pages is a claim about a named person that a resident may read
aloud at a hearing, and the two fields that make it quotable — `source` and
`as_of` — only exist once a human has opened the link and confirmed the person
actually said the thing. A headline is a lead. Promotion is the human step.
(Same discipline as scan_moratorium_candidates.py; the one scanner allowed to
write a registry, fetch_pa_dep_projects.py, earns it by reading a state
agency's own permit register, where there is no judgement call to skip.)

Queue entries keep `first_seen` and bump `last_seen`, so repeat coverage of one
statement collapses into a single row rather than re-raising. Anything a human
marks `"status": "dismissed"` is never surfaced again.

Usage
-----
    python3 scripts/scan_candidate_records.py            # scan and write
    python3 scripts/scan_candidate_records.py --dry-run  # report only
    python3 scripts/scan_candidate_records.py --chamber house
    python3 scripts/scan_candidate_records.py --report   # print the queue

Stdlib only — runs in CI off requirements-build.txt.
"""

import argparse
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import race_common as rc                       # noqa: E402
import src.senate_races as senate                       # noqa: E402
import src.house_races as house                         # noqa: E402

QUEUE = ROOT / "data" / "candidate_record_candidates.json"


def _load_queue():
    try:
        return json.loads(QUEUE.read_text())
    except (OSError, ValueError):
        return {"generated": None, "entries": []}


def _candidates(chamber):
    """(chamber, key, race_label, candidate) for every filed candidate."""
    out = []
    if chamber in ("senate", "both"):
        for r in senate.SENATE_RACES_2026:
            for c in r["candidates"]:
                out.append(("senate", r["abbrev"], r["state"], c))
    if chamber in ("house", "both"):
        for r in house.HOUSE_RACES_2026:
            for c in r["candidates"]:
                out.append(("house", f"{r['abbrev']}-{r['district']}",
                            f"{r['state']} {r['abbrev']}-{r['district']}", c))
    return out


def _published(chamber):
    """Names already carrying a documented record — nothing to re-raise."""
    done = set()
    if chamber in ("senate", "both"):
        done |= {rc.norm(k[-1]) for k in senate.AI_RECORDS}
    if chamber in ("house", "both"):
        done |= {rc.norm(k[-1]) for k in house.AI_RECORDS}
    return done


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="report, write nothing")
    ap.add_argument("--chamber", choices=["senate", "house", "both"],
                    default="both")
    ap.add_argument("--report", action="store_true",
                    help="print the existing queue and exit")
    ap.add_argument("--limit", type=int, default=0,
                    help="cap newly-added entries this run (0 = no cap)")
    args = ap.parse_args()

    q = _load_queue()
    by_key = {(e["chamber"], e["key"], rc.norm(e["name"]), e["link"]): e
              for e in q["entries"] if e.get("link")}

    if args.report:
        live = [e for e in q["entries"]
                if e.get("status") not in ("dismissed", "promoted")]
        print(f"{len(live)} open leads ({len(q['entries'])} total)\n")
        for e in sorted(live, key=lambda e: str(e.get("last_seen")), reverse=True)[:60]:
            print(f"  [{e['chamber'][:3]}] {e['key']:8} {e['name'][:28]:30} "
                  f"{str(e.get('last_seen'))[:10]}  {e['title'][:70]}")
        return

    archive = rc.load_story_archive()
    if not archive:
        sys.exit("no story archive at data/story_candidates.json — run the "
                 "site build first, which is what refreshes it.")
    print(f"scanning {len(archive)} archived stories…")

    done = _published(args.chamber)
    today = time.strftime("%Y-%m-%d")
    added = updated = promoted = 0

    # Close the loop: a lead whose candidate now carries a published record has
    # done its job. Without this the queue only ever grows, and the count stops
    # meaning "work outstanding" — which is the only reason to have a queue.
    for e in q["entries"]:
        if e.get("status") in ("dismissed", "promoted"):
            continue
        if rc.norm(e["name"]) in done:
            e["status"] = "promoted"
            e["promoted_on"] = today
            promoted += 1

    for chamber, key, label, c in _candidates(args.chamber):
        if rc.norm(c["name"]) in done:
            continue                      # already has a verified record
        for m in rc.mentions_for(c["name"], archive, limit=5):
            if not m.get("link"):
                continue
            k = (chamber, key, rc.norm(c["name"]), m["link"])
            if k in by_key:
                e = by_key[k]
                if e.get("status") == "dismissed":
                    continue
                e["last_seen"] = today
                updated += 1
                continue
            if args.limit and added >= args.limit:
                continue
            e = {
                "chamber": chamber, "key": key, "race": label,
                "name": c["name"], "party": c.get("party", ""),
                "title": m["title"], "link": m["link"],
                "outlet": m.get("source"),
                "first_seen": today, "last_seen": today,
                "status": "new",
                # Filled in by the human who promotes this into AI_RECORDS.
                "verified_source": None, "as_of": None, "lean": None,
            }
            q["entries"].append(e)
            by_key[k] = e
            added += 1
            print(f"  + [{chamber[:3]}] {key:8} {c['name'][:26]:28} {m['title'][:64]}")

    live = [e for e in q["entries"]
            if e.get("status") not in ("dismissed", "promoted")]
    print(f"\n{added} new lead(s), {updated} re-seen, {promoted} closed as "
          f"promoted. {len(live)} open in the queue.")
    if added:
        print("These are LEADS, not records. Promote one by opening the link, "
              "confirming the candidate said it, and adding a row to "
              "AI_RECORDS with its own source + as_of.")
    if args.dry_run:
        print("--dry-run: nothing written.")
        return
    q["generated"] = today
    QUEUE.write_text(json.dumps(q, indent=1, sort_keys=False) + "\n",
                     encoding="utf-8")
    print(f"wrote {QUEUE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
