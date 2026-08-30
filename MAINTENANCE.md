# Weekly data freshness digest — 2026-08-24

**7 hearings in the next 30 days · 11 moratoriums expiring soon · 16 expired · 2 stale registries · 999 new review-queue items (971 moratorium / 28 project)**

## Upcoming hearings (next 30 days)

Source: `PROJECTS_DF` / `project_status()`, `days_to_hearing` 0–30.

| Project | Locality | Hearing | Days | Stage |
|---|---|---|---|---|
| Project Flex | Lyon Township (Oakland County), MI | 2026-08-24 | 0 | Hearing scheduled |
| BCG Cedar Creek Campus | Cedar Creek (Bastrop County), TX | 2026-08-24 | 0 | Hearing scheduled |
| Aligned Data Centers – Pataskala industrial park | Pataskala (Licking County), OH | 2026-08-25 | 1 | Hearing scheduled |
| Site Layer 4 Data Center Campus | Wheatland (Platte County), WY | 2026-08-26 | 2 | Hearing scheduled |
| La Osa | Pinal County (near Eloy), AZ | 2026-08-26 | 2 | Hearing scheduled |
| Prime Data Centers — Starpointe Business Park campus | Hanover Township (Washington County), PA | 2026-08-31 | 7 | Hearing scheduled |
| Dickerson Data Center Campus (Atmosphere) | Dickerson (Montgomery County), MD | 2026-09-10 | 17 | Hearing scheduled |

Two hearings are today (2026-08-24) — Lyon Township MI and Cedar Creek/Bastrop County TX.

## Stale registries

`REGISTRY_PROVENANCE` / `registry_provenance()` — 2 of 10 registries flagged (past churn-based shelf life or no `as_of`).

| Registry | as_of | churn |
|---|---|---|
| `DC_SITES_DF` | None | medium |
| `STATE_PUCS_DF` | None | low |

Both have no recorded `as_of` at all (not just an old one) — needs a human read to set a real date, per CLAUDE.md ("never invent an as_of").

## Moratorium audit (`scripts/verify_moratoriums.py --offline`)

333/333 tracker rows checked. Link-checking skipped (offline mode) — no dead-link data this run. `stale-as-of` check: 0 rows (nothing verified >180 days ago on this high-churn dataset — good).

| Check | Count |
|---|---|
| expired | 16 |
| missing-source | 24 |
| undated-term | 29 |
| unclassified-term | 6 |
| expiring | 11 |

### Expiring soon (11) — watch for extension/lapse

| Locality | Ends | Days |
|---|---|---|
| Kings Mountain, NC | 2026-08-25 | 1 |
| Hall County, GA | 2026-08-25 | 1 |
| Larimer County, CO | 2026-08-25 | 1 |
| Hogansville, GA | 2026-09-01 | 8 |
| Birmingham, AL | 2026-09-03 | 10 |
| Augusta, GA | 2026-09-19 | 26 |
| Wixom, MI | 2026-09-24 | 31 |
| Front Royal, VA | 2026-10-04 | 41 |
| Vienna Township (Trumbull Co.), OH | 2026-10-16 | 53 |
| Indio, CA | 2026-10-16 | 53 |
| Bangor, ME | 2026-10-10 | 47 |

Three lapse this week (Kings Mountain NC, Hall County GA, Larimer County CO — all 2026-08-25).

### Expired — term date has passed, status not reconciled (16)

Most urgent (recently lapsed, Michigan cluster from the same source is the bulk of these):

- Cherokee County, GA — ran to 2026-08-21
- Massillon, OH — ran to 2026-08-14
- Hayes Township, MI — ran to 2026-08-09
- Lodi Township, MI — ran to 2026-08-02
- York Township, MI — ran to 2026-08-12
- Sylvan Township, MI — ran to 2026-07-22
- Pontiac, MI — ran to 2026-07-21
- Armada Township, MI — ran to 2026-07-13
- Saginaw, MI — ran to 2026-07-13
- Tyrone Township, MI — ran to 2026-06-01
- Pittsfield Township, MI — ran to 2026-05-17
- Howell Township, MI — ran to 2026-05-20
- Brevard, NC — ran to 2026-06-23
- Aurora, IL — ran to 2026-03-24
- Madison County, NC — ran to 2024-06-13
- Groton, CT — ran to 2023-06-21 (oldest — 3+ years stale)

Full list (all 16, plus the 24 missing-source concession rows, 29 undated-term, and 6 unclassified-term rows) is in the script output — rerun `python scripts/verify_moratoriums.py --offline` for the complete worklist.

## Review-queue backlog

Neither queue is auto-promoted — every row here needs a human reading the locality's own .gov source before it can become a registry row (CLAUDE.md, "Data maintenance scripts").

### `data/moratorium_candidates.json` — 971 new / 1,038 total (67 already promoted)

Tier breakdown from `scripts/triage_moratorium_candidates.py` (827 distinct, not-yet-tracked candidates): **A** cited 149 · **B** structured 67 · **C** thin 252 · **D** unlocated 359. Work Tier A first — it already has a link or named document.

Newest 10 (by last_seen):

| Last seen | Guessed locality | Title |
|---|---|---|
| 2026-08-24 | — | Commissioners approve two-year moratorium on data centers |
| 2026-08-24 | — | A county's data center moratorium doesn't include a small city considering huge project |
| 2026-08-24 | — | Dover data center moratorium gains steam, amid statewide concerns over the industry |
| 2026-08-24 | KY | A Kentucky county passes a data center moratorium — with a city-sized hole |
| 2026-08-24 | — | Modesto residents pack City Council meeting, call for ban on AI data centers |
| 2026-08-24 | Volusia | Volusia County Council to vote on data center moratorium. What's next? |
| 2026-08-24 | — | Counties scramble to respond to data centers, setting moratoriums, a ban |
| 2026-08-24 | Moffat | Moffat County commissioners discuss data center moratorium, address transparency questions |
| 2026-08-24 | Harris | Harris County leaders say data center moratorium unnecessary. Columbus area coalition forms |
| 2026-08-24 | Pittsburg | Pittsburg residents want city to pause data center project |

### `data/project_candidates.json` — 28 new / 140 total (65 promoted, 47 dismissed)

Newest 10 (by last_seen):

| Last seen | Guessed locality | Title |
|---|---|---|
| 2026-08-23 | Lackawanna | Lackawanna County judge voids Clifton Twp.'s data center zoning, as residents provide feedback for updated legislation |
| 2026-08-23 | — | Data center developers press Lehigh Valley community to rezone farmland, quarry |
| 2026-08-23 | — | Council approves generator noise exemption; data center zoning measure returns Sept. 3 |
| 2026-08-23 | — | DATA Centers Future Here, Changes in Zoning Text Amendment Procedures, and a Little Post-Meeting Drama for One Supervisor |
| 2026-08-23 | Stokes | Stokes County data center rezoning heads to second vote in monthslong saga |
| 2026-08-23 | — | Bristol Refers Data Center Zoning to Planning Board |
| 2026-08-23 | IA | Clinton, Iowa planning commission tables vote on data center ordinance |
| 2026-08-23 | Bulloch | Bulloch County commissioners adopt 10.260-mill rate, review proposed data center regulations |
| 2026-08-23 | — | Mason sets town hall for data center proposal as new details emerge |
| 2026-08-23 | — | Little Rock director will propose 18-month halt on permits for planned Google data center, other 'hyperscale' facilities |

This is a summary only — no registry rows or candidate statuses were changed by this run.
