# Keeping the Officials scorecard current

The scorecard (`web/scorecard.html`, and the Streamlit Officials tab) is built
from three moving parts. This is how each stays fresh and who/what changes it.

## The three parts

| Part | File | Source of truth | Volatility |
|------|------|-----------------|------------|
| **Roster** (names, party, websites, committees) | `officials.json` | authoritative public rosters | changes with elections/appointments |
| **Stances** (documented actions) | `src/officials_stances.py` | primary/reputable reporting | grows as officials act |
| **Grades** (A–F protection score) | `src/official_grades.py` | our rubric, tied to a stance | changes when a stance changes |

Grades are computed at render time from `PROTECTION_SCORES`, so there is no
grade file to regenerate — edit the score, rebuild, done.

## Routine refresh (roster) — run the script

```bash
python scripts/refresh_officials.py --check   # dry run: prints counts, writes nothing
python scripts/refresh_officials.py           # regenerates officials.json
python build_site.py                          # rebuilds the site incl. web/scorecard.html
```

`refresh_officials.py` rebuilds the roster from:
- **Senators** — `senate.gov` official contact XML
- **House** — `@unitedstates` congress-legislators (websites + contact forms)
- **Governors** — Wikipedia "List of current United States governors"
- **Committees** — House Clerk `MemberData.xml` (Energy & Commerce) +
  `@unitedstates` committee-membership (Senate Energy & Natural Resources)

It re-applies the curated stances automatically, so a refresh never drops them.

**Cadence:** monthly is plenty in a normal year; **within a week** after a
general election, a special election, a resignation/appointment, or the start of
a new Congress (committee rosters reshuffle in January of odd years).

## Adding a stance (and grading it)

1. Add the source to `src.constants.SOURCES` (`"key": ("name", "url")`).
2. Add the stance to `src/officials_stances.py` `STANCES`
   (`(office, state_postal, lastname) -> (text, source_key)`).
3. (Optional) add a 0–4 score to `src/official_grades.py` `PROTECTION_SCORES`
   to grade it (4→A protective … 0→F removes protections). Omit to list the
   stance without a grade.
4. `python scripts/refresh_officials.py && python build_site.py`.

Guardrails, unchanged: grade **only** where there's a documented, cited action;
leave silence blank (never scored as "neutral"); keep the axis explicit
(ratepayer/community protection), not partisan.

## Automating it (optional)

Add a scheduled job (GitHub Action / cron) that runs the two commands, and opens
a PR if `officials.json` changed. Because the roster comes from stable public
endpoints and stances live in code, a refresh is deterministic — a clean diff
means nothing changed; a non-empty diff is a real roster update to review.

## Sanity checks after a refresh

- Totals should read `senators=100 house=437 governors=50 total=587`.
- Committee counts: `E&C=54 ENR=20` (these shift only at a new Congress).
- No stance should point at a missing source — the build fails loudly if a
  `stance_src` isn't in `SOURCES`, and the scorecard shows no fallback links.
