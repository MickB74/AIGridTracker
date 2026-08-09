"""
Official grades — a ratepayer & community-protection scorecard.

This grades officials A–F on ONE explicit axis: **how much their documented
actions protect residents (ratepayers and host communities) from the costs and
impacts of data-center growth** — bills, water, grid strain, local say.

It is deliberately NOT a neutral rating and NOT a judgment of the official
overall. It is GridWatch AI's issue scorecard, in the tradition of advocacy
scorecards, and it is grounded in a single cited action per official.

Method (v0):
  - Each graded official has a protection score 0–4, tied to a documented,
    sourced action (the same stance + source shown in the directory).
      4 → A   protective (make data centers pay their way / real safeguards /
              community pause power)
      3 → B   mostly protective
      2 → C   mixed (courts investment but adds some protections)
      1 → D   weakly protective / prioritizes incentives
      0 → F   actively removes protections
  - Officials with NO documented data-center record are NOT graded (blank).
    Silence is not scored — the gap is disclosed, not punished.

Grades reflect a point-in-time public record and can change with new actions.
"""

import pandas as pd

RUBRIC = (
    "Grades measure one thing: how much an official's **documented** actions "
    "protect ratepayers and host communities from data-center costs and impacts "
    "(A = protective → F = removes protections). It's an issue scorecard, not a "
    "neutral or overall rating, and only officials with a public record are "
    "graded — silence is left blank, not scored."
)

# score 0–4 keyed by (office, state postal, last-name token). Each ties to the
# official's already-cited stance in officials.json (shown as the grade basis).
PROTECTION_SCORES = {
    # Governors
    ("Governor", "VA", "spanberger"): 4,   # fair-share laws + consumption tax
    ("Governor", "PA", "shapiro"): 4,      # GRID standards, developers pay
    ("Governor", "AZ", "hobbs"): 4,        # tax-break pause + water fee
    ("Governor", "TX", "abbott"): 4,       # SB6: pay your way, curtail
    ("Governor", "OH", "dewine"): 3,       # paused tax exemptions
    ("Governor", "UT", "cox"): 3,          # EO "higher bar" water/air/rates
    ("Governor", "IN", "braun"): 3,        # "pay every penny", no abatements
    ("Governor", "OR", "kotek"): 3,        # advisory committee + tax moratorium
    ("Governor", "NV", "lombardo"): 2,     # backs projects, closed-loop water
    ("Governor", "LA", "landry"): 2,       # courts Meta, later ratepayer EO
    ("Governor", "NY", "hochul"): 2,       # weighing a moratorium
    ("Governor", "GA", "kemp"): 1,         # vetoed a tax-break pause
    ("Governor", "ME", "mills"): 1,        # vetoed a moratorium
    ("Governor", "WI", "evers"): 1,        # courted Microsoft, pro-incentive
    # House
    ("Representative", "KY", "guthrie"): 4,     # Ratepayer Protection Act
    ("Representative", "FL", "castor"): 4,      # RPA co-sponsor
    ("Representative", "CO", "evans"): 4,       # RPA co-sponsor
    ("Representative", "NJ", "pallone"): 4,     # national moratorium call
    ("Representative", "VA", "subramanyam"): 4, # NoVA opposition + risk act
}

_LETTER = {4: "A", 3: "B", 2: "C", 1: "D", 0: "F"}


def grade_letter(score) -> str:
    """A–F for a 0–4 protection score; '' if unscored."""
    if score is None or (isinstance(score, float) and pd.isna(score)):
        return ""
    return _LETTER.get(int(score), "")


def _match(office: str, state: str, name: str) -> int | None:
    nm = (name or "").lower()
    for (o, s, ln), score in PROTECTION_SCORES.items():
        if o == office and s == state and ln in nm:
            return score
    return None


def attach_grades(df: pd.DataFrame) -> pd.DataFrame:
    """Add 'protect_score' (0–4 or NaN) and 'grade' (A–F or '') columns,
    matching officials by (office, state, name). Only officials in
    PROTECTION_SCORES are graded; all others stay blank."""
    out = df.copy()
    out["protect_score"] = [
        _match(r["office"], r.get("state", ""), r.get("name", ""))
        for _, r in out.iterrows()
    ]
    out["grade"] = out["protect_score"].map(grade_letter)
    return out
