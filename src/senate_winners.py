"""
The 35 people who won a U.S. Senate seat in 2026, on AI data centers.

Why this exists
---------------
Until election day the question was "who is asking for my vote?", and
src/senate_races.py answered it for 117 candidates. After it, 82 of those
people hold no office and their campaign lines bind nobody. The useful
question is now "what did the person who won put on the record, so I can
hold them to it?" — 35 people, each of whom votes on federal siting, tax and
ratepayer bills for the next six years.

This module is the join. It reads who won from
data/election_results_2026.json (never from incumbency or lean), takes each
winner's record from src/senate_winner_records.py, and adds the seat facts
from the frozen ballot roster and, for the sixteen who were already sitting
senators, the roster row from data/senators.json.

One fact, one place
-------------------
`WINNER_RECORDS` is the whole documented record for each winner — what they
did in office, what they said on the campaign trail, and what they have
said since. src/senators.py reads the same table for any sitting senator
who appears in it, so a re-elected senator has one record on the site, not
a Senate record and a campaign record that can drift apart. When the
newcomers are sworn in and appear in data/senators.json, the same lookup
picks them up with no migration.

Same rules as every record table here: full-name keys, per-item source and
date, `kind` separates an *action* from a *statement*, `lean` summarises
only the cited items, and a winner with nothing located renders as *No
record found* — never as neutral, and never inferred from party.
"""

import json
import pathlib

from src import race_common as rc
from src.senate_winner_records import WINNER_RECORDS

ROOT = pathlib.Path(__file__).resolve().parent.parent
SENATORS = ROOT / "data" / "senators.json"

LEANS = rc.LEANS


def _sitting():
    """(state, normalised surname) -> roster row for the sitting Senate."""
    rows = json.loads(SENATORS.read_text())["senators"]
    return {(s["state"], rc.norm(s["name"]).split()[-1]): s for s in rows}


def record_for(state, name):
    """The winner record for this person, or None.

    Exact full-name match first; then surname within the state, because the
    ballot name and the official roster name differ (Jim / James Risch). Safe
    for the same reason it is in src/senators.py: no state seats two senators
    with one surname, and only winners are in this table.
    """
    r = WINNER_RECORDS.get((state, name))
    if r:
        return r
    last = rc.norm(name).split()[-1]
    for (st, nm), rec in WINNER_RECORDS.items():
        if st == state and rc.norm(nm).split()[-1] == last:
            return rec
    return None


def winners(with_mentions=True):
    """One dict per Senate race that has a recorded winner, by state name."""
    import src.senate_races as sr
    from src.senators import _stance

    sitting = _sitting()
    archive = rc.load_story_archive() if with_mentions else []
    out = []
    for r in sr.races():
        res = r.get("result") or {}
        name = res.get("winner")
        if not name:
            continue
        st = r["abbrev"]
        seat = sitting.get((st, rc.norm(name).split()[-1]))
        rec = record_for(st, name) or {}
        lean = rec.get("lean") or "unrecorded"
        items = rec.get("items") or []
        out.append({
            "state": r["state"], "abbrev": st, "name": name,
            "party": res.get("winner_party") or "",
            "sitting": bool(seat),
            "bioguide": seat["bioguide"] if seat else None,
            "contact": (seat or {}).get("contact"),
            "website": (seat or {}).get("website"),
            "phone": (seat or {}).get("phone"),
            "flip": bool(res.get("flip")),
            "special": r["special"], "pvi": r["pvi"],
            "seat_held_by": r["incumbent"],
            "seat_held_party": r["incumbent_party"],
            "result": res,
            "lean": lean, "lean_label": LEANS[lean][0],
            "lean_color": LEANS[lean][2],
            "summary": rec.get("summary"),
            "background": rec.get("background"),
            "items": items,
            "actions": [i for i in items if i.get("kind") == "action"],
            "statements": [i for i in items if i.get("kind") != "action"],
            "as_of": rec.get("as_of"),
            "stance": _stance(st, name) if seat else None,
            "documented": lean not in ("unrecorded", "consensus"),
            "mentions": rc.mentions_for(name, archive) if archive else [],
        })
    out.sort(key=lambda w: w["state"])
    return out


def coverage(rows=None):
    rows = rows if rows is not None else winners(with_mentions=False)
    by_lean = {k: sum(1 for w in rows if w["lean"] == k) for k in LEANS}
    return {
        "winners": len(rows),
        "new": sum(1 for w in rows if not w["sitting"]),
        "returning": sum(1 for w in rows if w["sitting"]),
        "flips": sum(1 for w in rows if w["flip"]),
        "documented": sum(1 for w in rows if w["documented"]),
        "items": sum(len(w["items"]) for w in rows),
        "actions": sum(len(w["actions"]) for w in rows),
        "certified": sum(1 for w in rows
                         if w["result"].get("status") == "certified"),
        "by_lean": by_lean,
    }


def validate():
    """Problems that must stop a build: a record on someone who did not win,
    an unknown lean, a missing read date, or an item with no source."""
    results = rc.load_results().get("senate", {})
    problems = []
    for (st, name), rec in WINNER_RECORDS.items():
        res = results.get(st) or {}
        if rc.norm(res.get("winner") or "") != rc.norm(name):
            problems.append(f"{st} {name}: not the recorded winner of that race")
        if rec.get("lean") not in LEANS:
            problems.append(f"{st} {name}: unknown lean {rec.get('lean')!r}")
        if not rec.get("as_of"):
            problems.append(f"{st} {name}: no as_of")
        if rec.get("lean") != "unrecorded" and not rec.get("items"):
            problems.append(f"{st} {name}: a lean with no cited item")
        for i in rec.get("items", []):
            if not str(i.get("source", "")).startswith("http"):
                problems.append(f"{st} {name}: item without a source URL")
            if i.get("kind") not in ("action", "statement"):
                problems.append(f"{st} {name}: item kind must be action or statement")
    return problems
