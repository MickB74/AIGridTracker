# Weekly data-freshness digest — 2026-10-19

**19 moratoriums expire within 30 days, 40 have already lapsed unconfirmed, 2 registries carry no `as_of` at all, and 2,233 review-queue items (2,098 moratorium + 135 project) are awaiting human triage. No project in the tracker has a hearing scheduled in the next 30 days.**

## Upcoming hearings (next 30 days)

**None.** `PROJECTS_DF` has 31 rows with a recorded `hearing_date`, but every one of them is in the past — the newest is 2026-09-24. 20 projects are sitting in "Awaiting decision" (hearing already held, no decision/vote date on record); the 5 heard most recently are the ones worth a clerk call this week:

| Project | Locality | Heard |
|---|---|---|
| Plaza 500 (Lincolnia) | Lincolnia (Fairfax County), VA | 2026-09-24 |
| Dickerson Data Center Campus (Atmosphere) | Dickerson (Montgomery County), MD | 2026-09-10 |
| Prime Data Centers — Starpointe Business Park | Hanover Township (Washington County), PA | 2026-08-31 |
| La Osa | Pinal County (near Eloy), AZ | 2026-08-26 |
| Site Layer 4 Data Center Campus | Wheatland (Platte County), WY | 2026-08-26 |

This is a gap worth a human look, not just a quiet week — nobody is entering decision dates once a hearing is heard.

## Stale registries

`REGISTRY_PROVENANCE` carries 14 datasets; 2 are flagged stale by `registry_provenance()` (both for having **no `as_of` at all**, not for age):

| Registry | as_of | churn |
|---|---|---|
| `DC_SITES_DF` | *(none recorded)* | medium |
| `STATE_PUCS_DF` | *(none recorded)* | low |

The other 12 are current (all within their churn-based shelf life, 2–5 months old against 9–36 month limits).

## Moratorium audit (expiring / expired / missing-source)

`scripts/verify_moratoriums.py --offline` over 386 tracked rows:

| Check | Count |
|---|---|
| expired | 40 |
| undated-term (fixed-term, no end date) | 63 |
| unclassified-term (no `term` declared) | 76 |
| expiring (within 60d) | 61 |
| missing-source | 0 |
| stale-as-of (>180d) | 0 |

Missing-source and stale-as-of are both clean — every row that's been verified is verified recently. The real backlog is undated/unclassified terms (139 rows combined) and the expiring/expired list below.

**Expiring within 30 days (19 of the 61) — most time-critical, ordered soonest first:**

| Locality | State | Ends | Days left |
|---|---|---|---|
| White County | IN | 2026-10-20 | 1 |
| Lowndes County | GA | 2026-10-25 | 6 |
| Lowndes County | AL | 2026-10-25 | 6 |
| Gilroy | CA | 2026-10-29 | 10 |
| Richmond | CA | 2026-10-30 | 11 |
| Lexington (Fayette County) | KY | 2026-10-31 | 12 |
| West Whiteland Township | PA | 2026-11-01 | 13 |
| Upper Burrell Township | PA | 2026-11-02 | 14 |
| Smithfield Township | PA | 2026-11-02 | 14 |
| Charlotte | NC | 2026-11-05 | 17 |
| Lavon | TX | 2026-11-05 | 17 |
| Lysander (Onondaga Co.) | NY | 2026-11-06 | 18 |
| Camden County | GA | 2026-11-06 | 18 |
| Johnson County | IA | 2026-11-08 | 20 |
| Butler Township | PA | 2026-11-08 | 20 |
| Riley County | KS | 2026-11-12 | 24 |
| Dickinson County | IA | 2026-11-12 | 24 |
| Springfield | MO | 2026-11-17 | 29 |
| Putnam County | IN | 2026-11-17 | 29 |

(42 more expire between 31–60 days out — see `scripts/verify_moratoriums.py --offline` for the full list.)

**Expired, not yet reconciled (40) — oldest first, needs a human to confirm lapsed / extended / now-permanent:**

- Groton, CT — ran to 2023-06-21
- Madison County, NC — ran to 2024-06-13
- Mason, MI — ran to 2026-02-03
- Aurora, IL — ran to 2026-03-24
- Montebello, CA *(already marked Expired)* — ran to 2026-03-28
- Montour County, PA — ran to 2026-04-30
- Jerome Township, OH — ran to 2026-06-01
- Lenox Township, MI — ran to 2026-06-02
- Waterville, OH — ran to 2026-06-08
- Caledonia Township, MI — ran to 2026-07-01
- Brevard, NC — ran to 2026-07-02
- Griffin, GA — ran to 2026-07-12
- Lodi Township, MI — ran to 2026-08-02
- Kingsland, GA — ran to 2026-08-09
- Saugatuck Township, MI — ran to 2026-08-11
- Leavenworth County, KS *(already marked Expired)* — ran to 2026-08-11
- York Township, MI — ran to 2026-08-12
- Massillon, OH — ran to 2026-08-14
- Wixom, MI — ran to 2026-08-26
- Floyd County, GA — ran to 2026-08-28
- Mount Orab, OH — ran to 2026-08-30
- Lyon Charter Township, MI — ran to 2026-08-30
- Covington, GA — ran to 2026-08-31
- Hogansville, GA — ran to 2026-09-01
- Birmingham, AL — ran to 2026-09-03
- Wichita, KS — ran to 2026-09-10
- Augusta, GA — ran to 2026-09-15
- Augusta-Richmond County, GA — ran to 2026-09-15
- Roswell, GA — ran to 2026-09-20
- Waterford Township, MI — ran to 2026-10-01
- Calaveras County, CA — ran to 2026-10-09
- Rockdale County, GA — ran to 2026-10-09
- Morgan Hill, CA — ran to 2026-10-10
- Escondido, CA — ran to 2026-10-12
- Vienna Township (Trumbull Co.), OH — ran to 2026-10-16
- Cleveland, OH — ran to 2026-10-16
- Indio, CA — ran to 2026-10-16
- Mendocino County, CA — ran to 2026-10-16
- Eureka, CA — ran to 2026-10-17
- Plainfield, IL — ran to 2026-10-18

Two rows (Montebello CA, Leavenworth County KS) already show `effective_status = Expired`; the rest still render as `Enacted` — those 38 are the ones a reader could currently mis-cite as "still in force."

## Review-queue backlog

Scanner queues, read-only — nothing promoted or dismissed here per CLAUDE.md (promotion requires a human reading the locality's own .gov source).

| Queue | New (awaiting review) | Total | Last updated |
|---|---|---|---|
| `data/moratorium_candidates.json` | 2,098 | 2,392 | 2026-10-18 |
| `data/project_candidates.json` | 135 | 247 | 2026-10-12 |

**Top 10 newest moratorium candidates to triage:**

- [2026-10-18] MA — In Massachusetts, residents push to ban future data centers in every district
- [2026-10-18] (unlocalized) — Rapid City data center ordinance open house draws in crowd of over 150 residents
- [2026-10-18] (unlocalized) — Speakers at Leesburg rally call for statewide data center moratorium
- [2026-10-18] (unlocalized) — Dade City Considers Data Center Moratorium
- [2026-10-18] (unlocalized) — As San Jose presents draft rules for data centers, many still call for a moratorium
- [2026-10-18] Poway — Poway council bans large AI data centers in the city
- [2026-10-18] (unlocalized) — Lurie Signs 45-Day Data Center Moratorium
- [2026-10-17] (unlocalized) — BlackRock's Larry Fink warns a data center moratorium could trigger a recession
- [2026-10-17] (unlocalized) — Fayette residents seek more stringent data center ordinance standards
- [2026-10-17] Liberty — Liberty County approves 120-day moratorium on data centers

**Top 10 newest project candidates to triage:**

- [2026-10-12] (unlocalized) — Zoning hearing for proposed data center in Conshohocken resumes on October 15th
- [2026-10-12] Bethlehem — Bethlehem City Council holds public hearing on data centers and passes zoning ordinance amendments
- [2026-10-12] (unlocalized) — Clinton postponing data center zoning public hearing
- [2026-10-12] (unlocalized) — Council moves to extend Lexington's pause on data center development, restart zoning process
- [2026-10-12] (unlocalized) — Clinton postpones public hearing on data center zoning ordinance
- [2026-10-12] (unlocalized) — Lehigh Valley township gets second data center proposal. Its developer brings zoning challenge
- [2026-10-12] (unlocalized) — Tensions flare between attorneys at Throop Data Center Zoning hearing
- [2026-10-12] (unlocalized) — Tighter zoning restrictions on data centers moves forward in Hopkinsville
- [2026-10-12] (unlocalized) — Enid city leaders delay public meeting on proposed data center
- [2026-10-12] (unlocalized) — Lexington council sends data center zoning rules back to planning commission after packed public hearing

*Generated by the weekly data-freshness steward routine. Read-only — no registry rows were edited, no candidates were promoted or dismissed, no build was run.*
