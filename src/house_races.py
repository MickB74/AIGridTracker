"""
2026 U.S. House races — where each candidate stands on AI data centers.

Companion to src/senate_races.py; the shared vocabulary, record model and
freshness rules live in src/race_common.py.

Why the roster is a JSON file and the Senate's is not
----------------------------------------------------
440 districts and 1,161 candidates is ~2,500 lines of pure roster. Inlining it
the way senate_races.py does would bury the curated part — the records — under
data nobody hand-edits. So the ballot lives in `data/house_races_2026.json`
(regenerated from the state candidate lists) and only AI_RECORDS, which is
hand-researched and needs its reasoning next to it, stays in Python.

Sourcing discipline is identical to the Senate tracker:

* Each district's `roster_source` is the state election authority's own
  certified candidate list.
* Every record item carries its own `source` URL and `date`.
* Records key on the FULL candidate name — at 1,161 candidates, repeated
  surnames are guaranteed, not hypothetical.
* Candidates with nothing located are `unrecorded` and render as *No record
  found*, never as neutral.

Coverage will start very low and that is stated on the page rather than hidden.
It grows through scripts/scan_candidate_records.py, which files leads into a
review queue that a human promotes — never straight into this table, because
promotion is where `source` and `as_of` come from.
"""

import functools
import json
import pathlib

from src import race_common as rc

ROOT = pathlib.Path(__file__).resolve().parent.parent
ROSTER_FILE = ROOT / "data" / "house_races_2026.json"

LEANS = rc.LEANS
LEAN_NOTE = rc.LEAN_NOTE
ELECTION_DATE = rc.ELECTION_DATE


@functools.lru_cache(maxsize=1)
def _roster():
    data = json.loads(ROSTER_FILE.read_text())
    return data["roster_as_of"], data["districts"]


ROSTER_AS_OF = _roster()[0]
HOUSE_RACES_2026 = _roster()[1]


# ── the record ─────────────────────────────────────────────────────────────
# Key: (state postal, district, FULL candidate name) -> record dict.
#   summary : one sentence, plain language, nothing the sources don't support
#   lean    : key into rc.LEANS
#   items   : list of {what, date (ISO or ""), source (URL)}
#   as_of   : date this entry was last read. Never invent one.
#
# Seeded from federal legislative action, which is the strongest evidence a
# House record can carry: a cosponsorship is a dated, verifiable act, unlike a
# campaign statement. Challenger records arrive via the review queue.
AI_RECORDS = {
    # ── H.R. 9340, Ratepayer Protection Act ────────────────────────────────
    # Cleared House Energy & Commerce 52-0 on 2026-07-22. A committee vote is
    # the strongest evidence on this page: dated, recorded, and unlike a
    # campaign promise it already happened.
    ("CO", "8", "Gabe Evans"): {
        "lean": "guardrails",
        "summary": "Lead Republican sponsor of the Ratepayer Protection Act, "
                   "which would push states to make large loads — data centers "
                   "included — pay for the generation and transmission they "
                   "require instead of spreading it across households.",
        "items": [
            {"what": "Introduced H.R. 9340, the Ratepayer Protection Act, with "
                     "Rep. Kathy Castor. It directs states and their PUCs to "
                     "consider standards for connecting large-load customers so "
                     "those customers, not families and small businesses, cover "
                     "new generation, transmission and upgrade costs. Cleared "
                     "House Energy and Commerce 52-0.",
             "date": "2026-07-22",
             "source": "https://broadbandbreakfast.com/house-committee-approves-package-to-address-data-centers-growing-energy-demands/"},
        ],
        "as_of": "2026-08-26",
    },
    ("FL", "14", "Kathy Castor"): {
        "lean": "guardrails",
        "summary": "Lead Democratic sponsor of the Ratepayer Protection Act, "
                   "the bipartisan House bill making large loads carry their own "
                   "grid costs.",
        "items": [
            {"what": "Introduced H.R. 9340, the Ratepayer Protection Act, with "
                     "Rep. Gabe Evans — standards for states and PUCs connecting "
                     "large-load customers so the cost of new generation, "
                     "transmission and upgrades falls on those customers rather "
                     "than on households. Cleared House Energy and Commerce "
                     "52-0.",
             "date": "2026-07-22",
             "source": "https://broadbandbreakfast.com/house-committee-approves-package-to-address-data-centers-growing-energy-demands/"},
        ],
        "as_of": "2026-08-26",
    },

    # ── H.R. 8241, Power for the People Act of 2026 ────────────────────────
    # House companion to Van Hollen's S.3682. Cited to the bill of record:
    # congress.gov refuses scripted fetches (verify_candidate_records.py
    # classifies that as *blocked*, not dead — same convention as
    # scripts/verify_sources.py), but it is the canonical page for the text.
    ("MD", "7", "Kweisi Mfume"): {
        "lean": "guardrails",
        "summary": "Introduced the House Power for the People Act, aimed at "
                   "stopping data-center demand from raising household energy "
                   "bills.",
        "items": [
            {"what": "Introduced H.R. 8241, the Power for the People Act of "
                     "2026, with Rep. Paul Tonko — the House companion to "
                     "S.3682, which directs states to consider data-center rate "
                     "classes and seeks a FERC rule making data centers pay for "
                     "the transmission upgrades they require.",
             "date": "2026",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/8241/all-info"},
        ],
        "as_of": "2026-08-26",
    },
    ("NY", "20", "Paul Tonko"): {
        "lean": "guardrails",
        "summary": "Co-introduced the House Power for the People Act to shield "
                   "consumers from data-center-driven energy costs.",
        "items": [
            {"what": "Co-introduced H.R. 8241, the Power for the People Act of "
                     "2026, with Rep. Kweisi Mfume — the House companion to "
                     "S.3682 on data-center rate classes and FERC cost "
                     "allocation.",
             "date": "2026",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/8241/all-info"},
        ],
        "as_of": "2026-08-26",
    },

    # ── promoted from the review queue, 2026-08-26 ────────────────────────
    # Surfaced by scripts/scan_candidate_records.py as Google News leads, then
    # promoted by hand: each redirect was resolved to the member's own release,
    # which is what these cite. A queue link is never the citation.
    ("CA", "17", "Ro Khanna"): {
        "lean": "guardrails",
        "summary": "Introduced a Data Center Bill of Rights resolution "
                   "affirming a community's right to ban data centers near "
                   "homes and schools, to reject a project outright, and to keep "
                   "local siting authority from being preempted by the state.",
        "items": [
            {"what": "Introduced the Data Center Bill of Rights resolution: "
                     "communities may ban data centers in residential areas and "
                     "within 2,500 feet of homes, schools, childcare, hospitals "
                     "or nursing homes; may reject a project through a "
                     "transparent community process; county and municipal "
                     "authority to prohibit or regulate is preserved against "
                     "state preemption; and every data center must use clean, "
                     "reliable energy under strict noise and air limits. It is a "
                     "resolution, so it does not itself change law.",
             "date": "2026-08-06",
             "source": "https://khanna.house.gov/media/press-releases/release-rep-khanna-introduces-data-center-bill-rights"},
        ],
        "as_of": "2026-08-26",
    },
    ("NJ", "6", "Frank Pallone"): {
        "lean": "guardrails",
        "summary": "The senior Democrat on House Energy and Commerce called for "
                   "a national moratorium on AI data centers until their effect "
                   "on air, water and power bills is resolved.",
        "items": [
            {"what": "Called for a national AI data-center moratorium at an "
                     "Energy Subcommittee markup — \u201cin favor of a national AI "
                     "data center moratorium until we can find a way to ensure "
                     "they don't harm our nation's air, water, and power "
                     "bills.\u201d",
             "date": "2026-06-25",
             "source": "https://pallone.house.gov/media/press-releases/pallone-supports-national-ai-data-center-moratorium"},
        ],
        "as_of": "2026-08-26",
    },
    ("NY", "19", "Josh Riley"): {
        "lean": "guardrails",
        "summary": "Introduced the bipartisan FAIR Data Act to keep the cost of "
                   "generation, transmission and distribution upgrades for data "
                   "centers off New York ratepayers.",
        "items": [
            {"what": "Introduced the FAIR Data Act, bipartisan legislation to "
                     "stop data-center projects from raising energy bills for "
                     "Upstate New York families and small businesses by "
                     "shielding ratepayers from the generation, transmission and "
                     "distribution upgrades those projects require.",
             "date": "2026-07-13",
             "source": "https://riley.house.gov/2026/07/13/riley-introduces-bill-to-stop-data-center-projects-from-driving-up-energy-bills/"},
        ],
        "as_of": "2026-08-26",
    },
    ("GA", "7", "Rich McCormick"): {
        "lean": "accelerate",
        "summary": "Chaired the House Science subcommittee hearing on expanding "
                   "data-center infrastructure and argues against slowing the "
                   "buildout, calling local opposition alarmism while "
                   "acknowledging rural grid limits.",
        "items": [
            {"what": "Opened a House Science, Space and Technology subcommittee "
                     "hearing, \u201cPowering America's AI Future: Assessing Policy "
                     "Options to Increase Data Center Infrastructure\u201d, framing "
                     "the question as whether approval processes can deliver the "
                     "infrastructure AI leadership needs in time, and flagging "
                     "rural Georgia's cooperative grid as a binding constraint.",
             "date": "2026-02",
             "source": "https://mccormick.house.gov/media/press-releases/subcommittee-chairman-mccormick-opens-hearing-ai-data-center-infrastructure"},
            {"what": "Said the U.S. should keep expanding data centers to hold "
                     "AI leadership, arguing they can be built responsibly and "
                     "benefit local economies, and pushed back on what he called "
                     "alarmism in local protests.",
             "date": "2026-08-23",
             "source": "https://www.bloomberg.com/news/videos/2026-08-23/rep-mccormick-warns-against-slowing-ai-buildout-video"},
        ],
        "as_of": "2026-08-26",
    },
}


def _key(r):
    return (r["abbrev"], r["district"])


def races(state=None):
    """Every 2026 House race with records and unverified mentions attached."""
    rows = HOUSE_RACES_2026
    if state:
        rows = [r for r in rows if r["abbrev"] == state or r["state"] == state]
    return rc.attach_records(rows, AI_RECORDS, _key)


def coverage():
    return rc.coverage(races(), ROSTER_AS_OF)


def by_state():
    """Races grouped by state, districts in ballot order."""
    out = {}
    for r in races():
        out.setdefault(r["state"], []).append(r)
    for v in out.values():
        v.sort(key=lambda r: (0 if r["district"] == "AL" else int(r["district"])))
    return dict(sorted(out.items()))


def validate():
    return rc.validate(races(), AI_RECORDS, _key)
