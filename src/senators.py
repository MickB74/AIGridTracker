"""
Every sitting U.S. senator on AI data centers — not just the 35 on a ballot.

Why this exists
---------------
src/senate_races.py answers "who is asking for my vote this year?" That is
the right question for 35 states in an election year and the wrong one for
the other 15 — and for all 50 the year after. Federal siting, tax and
ratepayer bills get voted on by all 100 senators, two of whom represent
every reader. This module is the roster of all 100 with whatever documented
record the site already holds on each, so a resident can look up *their*
senators without wading through races they cannot vote in.

Where the records come from
---------------------------
Nothing here is researched separately. Each senator is joined to the two
record tables the site already maintains, so one fact lives in one place:

* `src/officials_stances.py` — a sitting official's documented *action*
  (a bill introduced, a veto, an investigation), graded A–F by
  `src/official_grades.py`. This is the stronger evidence.
* `src/senator_records.py` — the researched record for sitting senators:
  bills, letters, hearing questions and on-the-record statements, each with
  its own source and date and a `kind` (action vs statement).
* `src/senate_races.py::AI_RECORDS` — campaign-time items for the incumbents
  on the 2026 ballot, with per-item source and date. A campaign statement
  is a promise, not an action, so it is shown as such and never graded.

Roster: data/senators.json, refreshed by scripts/refresh_senators.py from the
@unitedstates congress-legislators dataset. It carries the one fact
officials.json lacks — the seat's class, hence when it is next on a ballot.

Same rules as the race trackers: silence renders as *No record found*, never
as neutral; nothing is inferred from a party label; every item links.
"""

import json
import pathlib

from src import race_common as rc
from src.constants import SOURCES
from src.official_grades import PROTECTION_SCORES, grade_letter
from src.officials_stances import STANCES
from src.senator_records import SENATOR_RECORDS

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "senators.json"


def _load():
    d = json.loads(DATA.read_text())
    return d["senators"], d.get("generated"), d.get("source"), d.get("source_name")


def _stance(state, name):
    """(text, source_name, source_url, grade) or None — the scorecard record."""
    nm = name.casefold()
    for (office, st, last), (text, key) in STANCES.items():
        if office == "Senator" and st == state and last in nm:
            src = SOURCES.get(key)
            score = PROTECTION_SCORES.get((office, st, last))
            return {"text": text, "source_name": src[0] if src else None,
                    "source": src[1] if src else None,
                    "grade": grade_letter(score) if score is not None else ""}
    return None


def _race_record(state, name):
    """The 2026 campaign record for an incumbent on this year's ballot."""
    import src.senate_races as sr
    r = sr.record_for(state, name)
    if not r:
        # Records key on the ballot name, which can differ from the
        # official one (Dan S. Sullivan / Daniel Sullivan; Jim / James
        # Risch). Fall back to a surname match within the state — safe
        # here because no state seats two senators with one surname, and
        # the roster module already guards against the Alaska collision.
        last = rc.norm(name).split()[-1]
        for (st, cand), rec in sr.AI_RECORDS.items():
            if st == state and rc.norm(cand).split()[-1] == last:
                r = rec
                break
    if not r:
        return None
    return {"lean": r["lean"], "lean_label": rc.LEANS[r["lean"]][0],
            "lean_color": rc.LEANS[r["lean"]][2], "summary": r["summary"],
            "items": r["items"], "as_of": r.get("as_of")}


def senators(with_mentions=True):
    rows, generated, src, src_name = _load()
    archive = rc.load_story_archive() if with_mentions else []
    out = []
    for s in rows:
        stance = _stance(s["state"], s["name"])
        race = _race_record(s["state"], s["name"]) if s["next_election"] == 2026 else None
        rec = SENATOR_RECORDS.get((s["state"], s["name"]))
        record = None
        if rec:
            record = {"lean": rec["lean"], "lean_label": rc.LEANS[rec["lean"]][0],
                      "lean_color": rc.LEANS[rec["lean"]][2],
                      "summary": rec["summary"], "items": rec["items"],
                      "as_of": rec.get("as_of")}
        out.append({
            **s,
            "stance": stance,
            "record": record,
            "race": race,
            "documented": bool(stance or race or record),
            "on_ballot_2026": s["next_election"] == 2026,
            "mentions": rc.mentions_for(s["name"], archive) if archive else [],
        })
    return out


def coverage(rows=None):
    rows = rows or senators(with_mentions=False)
    _, generated, src, src_name = _load()
    return {
        "senators": len(rows),
        "documented": sum(1 for s in rows if s["documented"]),
        "graded": sum(1 for s in rows if s["stance"] and s["stance"]["grade"]),
        "on_ballot_2026": sum(1 for s in rows if s["on_ballot_2026"]),
        "generated": generated, "source": src, "source_name": src_name,
    }
