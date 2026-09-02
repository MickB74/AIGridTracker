# Weekly data-freshness digest — 2026-08-31

**27 items need eyes this week: 8 moratoriums expiring within 46 days, 3 hearings inside 30 days, 2 registries with no recorded `as_of`, and a 1,041-item candidate backlog (157 of them cheap to promote).**

This is a summary and priority list only — nothing here has been edited, promoted, or dismissed. All promotions require a human reading the locality's own `.gov` source (per `CLAUDE.md`).

## Upcoming hearings (next 30 days)

Derived from `PROJECTS_DF` / `project_status()` in `src/constants.py`.

| Project | State | Stage | Hearing date | Days out |
|---|---|---|---|---|
| Prime Data Centers — Starpointe Business Park campus | PA | Hearing scheduled | 2026-08-31 | today |
| Dickerson Data Center Campus (Atmosphere) | MD | Hearing scheduled | 2026-09-10 | 10 |
| Plaza 500 (Lincolnia) | VA | Hearing scheduled | 2026-09-24 | 24 |

Also **16 projects are in "awaiting decision"** (hearing already held, no decision date recorded) — undated but could resolve any day: Project Iron Spur (NC), Burkhalter Road / 4AM Development (GA), Aligned Data Centers Pataskala (OH), Posey County (IN), Project Flex (MI), TeraWulf Cayuga (NY), Project Double Reed / STAMP (NY), Stonebridge Powder Mill Works (PA), 900 Conshohocken Road (PA), BCG Cedar Creek Campus (TX), Manse Technology Campus (NV), Cave City (KY), Smithfield Gateway (PA), Site Layer 4 (WY), La Osa (AZ), and one more. Worth a status check with each project's clerk.

## Stale registries

From `REGISTRY_PROVENANCE` / `registry_provenance()` in `src/constants.py` — flagged when past churn-based shelf life *or* `as_of` was never recorded. Both cases below are the latter (no date on record, not an aged one):

| Registry | as_of | churn | Note |
|---|---|---|---|
| `DC_SITES_DF` | *(none recorded)* | medium | Campus registry (operator/tenant/filing LLC). Colocation/REIT attribution came from trade press, never independently fact-checked. |
| `STATE_PUCS_DF` | *(none recorded)* | low | PUC directory. Names/URLs are stable, but no verification pass has been logged. |

All other registries (`STATE_DC_DF`, `STATE_GRID_PROFILES`, `HOUSE_RACES_2026`, `SENATE_RACES_2026`, `MORATORIUMS_DF`, `MEGA_PROJECTS_DF`, `PROJECTS_DF`, `EXECUTIVES_DF`, `STATE_STUDIES`, `STATE_PERMIT_PORTALS`) are within their churn window.

## Moratorium audit

`python scripts/verify_moratoriums.py --offline` — 333/333 tracker rows carry a `source`, so **missing-source: 0** and **stale-as-of (>180d): 0** this run. (Link-liveness wasn't checked — offline run.)

| Check | Count |
|---|---|
| expired | 19 |
| expiring (≤46d) | 8 |
| undated-term | 29 |
| unclassified-term | 5 |

**Expiring soon (act first — extension or lapse imminent):**

| Locality | State | Ends | Days left |
|---|---|---|---|
| Hogansville | GA | 2026-09-01 | 1 |
| Birmingham | AL | 2026-09-03 | 3 |
| Wixom | MI | 2026-09-24 | 24 |
| Front Royal | VA | 2026-10-04 | 34 |
| Augusta | GA | 2026-09-19 | 19 |
| Bangor | ME | 2026-10-10 | 40 |
| Vienna Township (Trumbull Co.) | OH | 2026-10-16 | 46 |
| Indio | CA | 2026-10-16 | 46 |

**Expired — term has already run out, page still shows it as in force (top priority to re-verify):**

Groton CT (2023-06-21), Madison County NC (2024-06-13), Brevard NC (2026-06-23), Kings Mountain NC (2026-08-25), Cherokee County GA (2026-08-21), Massillon OH (2026-08-14), Hall County GA (2026-08-25), Aurora IL (2026-03-24), Larimer County CO (2026-08-25), and 10 Michigan townships (Armada, Pittsfield, Howell, Pontiac, Saginaw, Tyrone, Sylvan, Lodi, York, Hayes — all sourced to the same WKAR tracker, ending 2026-05-17 through 2026-08-12).

29 more rows carry a fixed term with no recorded end date (`undated-term`) and 5 have no `term` classification at all (`unclassified-term`) — full lists in the script's markdown output; not reproduced here for length.

## Review-queue backlog

**Moratorium candidates** (`data/moratorium_candidates.json`): 1,077 total — **1,010 new / awaiting review**, 67 already promoted, 0 dismissed.

Triaged by `scripts/triage_moratorium_candidates.py` into cost-to-verify tiers (856 not-yet-tracked after dedup): **Tier A (cited, cheapest) 157 · Tier B (structured, source still needed) 67 · Tier C (thin) 252 · Tier D (unlocated) 380.**

Top 10 Tier A to promote this week (link/document already in hand — read one page, write one row):

1. Bloomingdale — "Bloomingdale City Council approves data center moratorium" (3 outlets)
2. Harrington — "Harrington City Council rejects data center ordinance after heated community meeting" (3 outlets)
3. Lowell — "Residents want a judge to pause Lowell data center expansion" (2 outlets)
4. Lowell — "Court orders pause Lowell data center expansion" (2 outlets, likely same event as #3 — verify before creating two rows)
5. Lowndes County — "Lowndes County residents demand moratorium on data center development as county drafts new ordinance" (2 outlets)
6. Pott County — "Residents request a moratorium at Pott County public hearing on data centers" (2 outlets)
7. Tazewell / Woodford County — "Tazewell County revisits data center ordinance; Woodford County passes moratorium" (2 outlets) — Woodford County, IL is already tracked (see `undated-term` above); check whether Tazewell needs its own row
8. Maryland (statewide, MD?) — 2026-session moratorium legislation reported in committee; **bill number not given by source — do not create a row without one**
9. Western Maryland (MD?) — "Western MD county approves data center moratorium"
10. (7 more in Tier A queue at same confidence — run `triage_moratorium_candidates.py --tier A --limit 20` for the rest)

**Project candidates** (`data/project_candidates.json`): 143 total — **31 new / awaiting review**, 65 promoted, 47 dismissed.

10 newest new items:

1. 2026-08-24 — Speakers Back Proposed Cumberland Data Center Zoning Limits as Ordinance Heads to Subcommittee
2. 2026-08-24 — Proposed Spartanburg data center project appeals after county rejects application
3. 2026-08-24 — Revised plans approved for 'hyper-scale' data center in South Jersey
4. 2026-08-23 — Lackawanna County judge voids Clifton Twp.'s data center zoning, as residents provide feedback for updated legislation
5. 2026-08-23 — Data center developers press Lehigh Valley community to rezone farmland, quarry
6. 2026-08-23 — Council approves generator noise exemption; data center zoning measure returns Sept. 3
7. 2026-08-23 — DATA Centers Future Here, Changes in Zoning Text Amendment Procedures, and a Little Post-Meeting Drama for One Supervisor
8. 2026-08-23 — Stokes County data center rezoning heads to second vote in monthslong saga
9. 2026-08-23 — Bristol Refers Data Center Zoning to Planning Board
10. 2026-08-23 — Clinton, Iowa planning commission tables vote on data center ordinance (IA)

---
*Generated by the weekly data-freshness steward. Read-only run — no registry, review-queue, or `web/` file was modified.*
