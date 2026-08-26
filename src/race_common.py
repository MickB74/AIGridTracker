"""
Shared machinery for the 2026 race trackers (Senate and House).

Both chambers answer the same question — where does the person on my ballot
stand on AI data centers? — so the vocabulary, the record model, the freshness
rules and the election-phase logic live here once. Only the rosters and the
records themselves are per-chamber.

The rules that matter, in one place:

* **Records key on the FULL candidate name, never the surname.** The Alaska
  Senate ballot carries both `Dan S. Sullivan` (the incumbent) and an unrelated
  `Dan J. Sullivan` placed there by court order; a surname key gave the
  senator's record to both men. At House scale this is worse, not better —
  1,161 candidates across 440 districts, with repeated surnames guaranteed.
* **Silence is disclosed, never scored.** No record found renders as exactly
  that, never as "neutral" and never as a bad grade.
* **`lean` summarises the cited items, not the person.** One axis only: does
  this candidate's documented position make data centers pay their own way and
  give the host community a say?
* **Nothing here is a grade.** src/official_grades.py grades sitting officials
  A–F on roll-call votes and signed laws. Most candidates are challengers whose
  entire record is a press release, and a promise is not an action.
"""

import datetime
import json
import pathlib
import re

ELECTION_DATE = "2026-11-03"
ROOT = pathlib.Path(__file__).resolve().parent.parent

# ── lean vocabulary ────────────────────────────────────────────────────────
LEANS = {
    "guardrails": (
        "Guardrails",
        "Documented support for making data centers carry their own costs, "
        "for community say over siting, or for a pause.",
        "#22c55e"),
    "mixed": (
        "Mixed",
        "Documented on both sides — courts the buildout but backs some "
        "ratepayer or community protection.",
        "#f59e0b"),
    "accelerate": (
        "Accelerate",
        "Documented emphasis on building faster — competitiveness, "
        "incentives, or siting help — without a matching cost or community "
        "safeguard on the record.",
        "#ef4444"),
    "unrecorded": (
        "No record found",
        "No documented statement or action on data centers located. Not "
        "scored — the gap is disclosed, not punished.",
        "#64748b"),
}

LEAN_NOTE = (
    "“Lean” summarises only the cited items below it, on one axis: "
    "does this candidate's documented position make data centers pay their own "
    "way and give the host community a say? It is not an overall rating, not a "
    "grade, and not an endorsement. Candidates with no located record are left "
    "unscored."
)

# A record whose as_of is older than this is called stale on the page rather
# than quietly shown. Campaign positions move fast — a six-month-old read of a
# candidate's platform is not evidence of where they stand today.
STALE_AFTER_DAYS = 120


def norm(name):
    """Normalised FULL name — the record key. Never key on a surname.

    Alaska 2026 is the worked example: `Dan S. Sullivan` (the incumbent) and
    `Dan J. Sullivan` (unrelated, on the ballot by court order) are different
    people, and a surname key silently merged them.
    """
    return " ".join(str(name or "").split()).casefold()


def today():
    return datetime.date.today()


def _age_days(as_of):
    try:
        d = datetime.date.fromisoformat(str(as_of)[:10])
    except (TypeError, ValueError):
        return None
    return (today() - d).days


def election_phase(on=None):
    """Where we are relative to election day, as data rather than as prose.

    Drives the post-election archival mode: once the votes are in, the page
    stops being a voter guide and becomes a record of what each winner promised
    — which is the more useful artifact for the four years after. Derived, never
    stored, so the daily CI rebuild flips it with no edit (see CLAUDE.md,
    "Derive time-sensitive status, never store it").
    """
    d = on or today()
    e = datetime.date.fromisoformat(ELECTION_DATE)
    if d < e:
        return {"phase": "campaign", "days_to_election": (e - d).days,
                "election_date": ELECTION_DATE}
    if d == e:
        return {"phase": "election_day", "days_to_election": 0,
                "election_date": ELECTION_DATE}
    return {"phase": "archive", "days_since_election": (d - e).days,
            "election_date": ELECTION_DATE}


# ── automated, unverified mentions ─────────────────────────────────────────
# Sourced from the same story archive that already feeds story-tracker.html,
# which publishes unreviewed headlines under an explicit caveat. Same bargain
# here: a mention is a lead, never a record, and the page must say so.
_MENTION_TERMS = re.compile(
    r"data cent|datacent|\bAI\b|artificial intelligence|hyperscal", re.I)


def load_story_archive():
    f = ROOT / "data" / "story_candidates.json"
    try:
        data = json.loads(f.read_text())
    except (OSError, ValueError):
        return []
    return data if isinstance(data, list) else data.get("stories", [])


def _name_pattern(name):
    """Match a candidate in a headline: full name, or surname with a first
    initial/first name adjacent. A bare surname is far too loose at House
    scale — "Collins", "Rogers" and "Brown" each match several unrelated
    people, plus ordinary nouns."""
    parts = [p for p in re.split(r"\s+", str(name)) if len(p.strip(".")) > 1]
    if len(parts) < 2:
        return None
    first, last = re.escape(parts[0]), re.escape(parts[-1])
    return re.compile(rf"\b{first}\s+(?:\w+\.?\s+)?{last}\b", re.I)


def mentions_for(name, archive, limit=3):
    """Recent unreviewed headlines that name this candidate AND mention data
    centers/AI. Returns [] readily — a false negative is cheap here, a false
    positive attributes someone else's words to a candidate."""
    pat = _name_pattern(name)
    if not pat:
        return []
    hits = []
    for s in archive:
        title = str(s.get("title") or "")
        if pat.search(title) and _MENTION_TERMS.search(title):
            hits.append({"title": title, "link": s.get("link"),
                         "seen": s.get("first_seen") or s.get("last_seen"),
                         "source": s.get("source") or s.get("outlet")})
    hits.sort(key=lambda h: str(h.get("seen") or ""), reverse=True)
    return hits[:limit]


# ── assembly ───────────────────────────────────────────────────────────────
def attach_records(races, records, key_fields, with_mentions=True):
    """Merge documented records (and unverified mentions) onto a roster.

    `key_fields(race)` returns the tuple prefix used to key records for that
    race — ("TX",) for a Senate race, ("TX", "33") for a House district — so
    the same record table shape works for both chambers.
    """
    by_name = {(k[:-1], norm(k[-1])): v for k, v in records.items()}
    archive = load_story_archive() if with_mentions else []
    out = []
    for r in races:
        race = dict(r)
        prefix = key_fields(r)
        inc_names = {norm(n) for n in race.get("incumbents", [])}
        if race.get("incumbent"):
            inc_names.add(norm(race.get("incumbent_on_ballot")
                               or race["incumbent"]))
        cands = []
        for c in race["candidates"]:
            rec = by_name.get((prefix, norm(c["name"]))) or {}
            lean = rec.get("lean", "unrecorded")
            label, _desc, color = LEANS[lean]
            age = _age_days(rec.get("as_of")) if rec else None
            cands.append({
                **c,
                "incumbent": norm(c["name"]) in inc_names,
                "lean": lean, "lean_label": label, "lean_color": color,
                "summary": rec.get("summary"),
                "items": rec.get("items", []),
                "as_of": rec.get("as_of"),
                "stale": bool(rec) and (age is None or age > STALE_AFTER_DAYS),
                "mentions": mentions_for(c["name"], archive) if archive else [],
            })
        order = {"Democratic": 0, "DFL": 0, "Republican": 0}
        cands.sort(key=lambda c: (c["lean"] == "unrecorded",
                                  order.get(c["party"], 1), c["name"]))
        race["candidates"] = cands
        race["documented"] = sum(1 for c in cands if c["lean"] != "unrecorded")
        race["contested"] = race["documented"] > 0
        race["mention_count"] = sum(len(c["mentions"]) for c in cands)
        out.append(race)
    return out


def coverage(races, roster_as_of):
    cands = [c for r in races for c in r["candidates"]]
    return {
        "races": len(races),
        "candidates": len(cands),
        "documented": sum(1 for c in cands if c["lean"] != "unrecorded"),
        "stale": sum(1 for c in cands if c.get("stale")),
        "races_documented": sum(1 for r in races if r["contested"]),
        "mentions": sum(len(c["mentions"]) for c in cands),
        "as_of": roster_as_of,
        **election_phase(),
    }


def validate(races, records, key_fields):
    """Invariants that must hold before a build ships. Returns a list of
    problems; empty means clean.

    Exists because the failure mode here is not a crash — it is a page that
    confidently attributes a position to the wrong person on a ballot.
    """
    problems = []
    roster = {(key_fields(r), norm(c["name"]))
              for r in races for c in r["candidates"]}
    for k in records:
        if (k[:-1], norm(k[-1])) not in roster:
            problems.append(f"record key not on any ballot: {k}")
    for k, v in records.items():
        if v.get("lean") not in LEANS:
            problems.append(f"{k}: unknown lean {v.get('lean')!r}")
        if not v.get("as_of"):
            problems.append(f"{k}: no as_of (never invent one — leave None "
                            f"only if the record itself is absent)")
        for i in v.get("items", []):
            if not str(i.get("source", "")).startswith("http"):
                problems.append(f"{k}: item without a source URL")
    for r in races:
        names = [c["name"] for c in r["candidates"]]
        if len(set(map(norm, names))) != len(names):
            problems.append(f"{key_fields(r)}: duplicate candidate name")
    return problems
