# Weekly data-freshness digest — 2026-09-07

**52 moratorium rows need a status/date fix (28 expired, 24 expiring within 60 days) · 2 registries have no verification date on record · 1,336 moratorium candidates and 49 project candidates await triage · 2 project hearings land in the next 30 days.**

## Upcoming hearings (next 30 days)

| Project | State | Stage | Hearing date |
|---|---|---|---|
| Dickerson Data Center Campus (Atmosphere) | MD | Hearing scheduled | 2026-09-10 (3 days) |
| Plaza 500 (Lincolnia) | VA | Hearing scheduled | 2026-09-24 (17 days) |

**Stale "awaiting decision" — hearing already happened, no outcome recorded (oldest first):**
Smithfield Gateway Data Center (PA, heard 2026-08-12), 900 Conshohocken Road (PA, 2026-08-17), Burkhalter Road (GA, 2026-08-18), Manse Technology Campus / Project Blackjack (NV, 2026-08-18), Kearney Data Center (NE, 2026-08-21), Project Flex (MI, 2026-08-24), BCG Cedar Creek Campus (TX, 2026-08-24), Aligned Data Centers – Pataskala (OH, 2026-08-25), Site Layer 4 Data Center Campus (WY, 2026-08-26), La Osa (AZ, 2026-08-26), Prime Data Centers – Starpointe Business Park (PA, 2026-08-31).
11 of 13 flagged projects are in this stale bucket — worth a pass to fill in `outcome` from the board's minutes/vote record.

## Stale registries

`REGISTRY_PROVENANCE` flags 2 of 13 bulk registries as stale — both because no `as_of` is recorded at all, not because of churn:

| Registry | as_of | Churn | Note |
|---|---|---|---|
| `DC_SITES_DF` | none recorded | medium | Campus registry (operator/tenant/filing LLC) — never had a verification pass logged |
| `STATE_PUCS_DF` | none recorded | low | PUC directory — commission names/complaint URLs are stable, but no verification date exists |

## Moratorium audit (`verify_moratoriums.py --offline`)

142 findings total. `missing-source`: 0. `stale-as-of` (>180d since verification): 0.

### Expired (28) — term end date has passed, status still shows "Enacted"
- Birmingham, AL — 2026-09-03
- Hogansville, GA — 2026-09-01
- Mount Orab, OH — 2026-08-30
- Floyd County, GA — 2026-08-28
- Hall County, GA — 2026-08-25
- Massillon, OH — 2026-08-14
- York Township, MI — 2026-08-12
- Saugatuck Township, MI — 2026-08-11
- Hayes Township, MI — 2026-08-09
- Kingsland, GA — 2026-08-09
- Lodi Township, MI — 2026-08-02
- Sylvan Township, MI — 2026-07-22
- Pontiac, MI — 2026-07-21
- Covington, GA — 2026-07-19
- Armada Township, MI — 2026-07-13
- Saginaw, MI — 2026-07-13
- Griffin, GA — 2026-07-12
- Brevard, NC — 2026-06-23
- Waterville, OH — 2026-06-08
- Lenox Township, MI — 2026-06-02
- Tyrone Township, MI — 2026-06-01
- Jerome Township, OH — 2026-06-01
- Howell Township, MI — 2026-05-20
- Pittsfield Township, MI — 2026-05-17
- Aurora, IL — 2026-03-24
- Fluvanna County, VA — 2026-01-31
- Madison County, NC — 2024-06-13
- Groton, CT — 2023-06-21 *(oldest — 3+ years lapsed)*

### Expiring soon (24) — within 60 days, watch for extension votes
- Augusta, GA — 2026-09-19
- Augusta-Richmond County, GA — 2026-09-19
- Roswell, GA — 2026-09-20
- Wixom, MI — 2026-09-24
- Front Royal, VA — 2026-10-04
- Pierce Township, OH — 2026-10-09
- Calaveras County, CA — 2026-10-09
- Bangor, ME — 2026-10-10
- Tallmadge, OH — 2026-10-10
- Palm Springs, CA — 2026-10-10
- Escondido, CA — 2026-10-12
- Vienna Township (Trumbull Co.), OH — 2026-10-16
- Cleveland, OH — 2026-10-16
- Indio, CA — 2026-10-16
- Mendocino County, CA — 2026-10-16
- Eureka, CA — 2026-10-17
- White County, IN — 2026-10-20
- Lowndes County, GA — 2026-10-25
- Lexington (Fayette County), KY — 2026-10-31
- Upper Burrell Township, PA — 2026-11-02
- Charlotte, NC — 2026-11-05
- Lavon, TX — 2026-11-05
- Lysander (Onondaga Co.), NY — 2026-11-06
- Camden County, GA — 2026-11-06

### Other audit categories (not time-critical this week)
- `undated-term` — 38 rows: fixed-duration note but no recorded adoption/end date, so the page can't expire them.
- `unclassified-term` — 52 rows: no end date and no `term` declared — could be a permanent ban or an unresearched pause; largely a block of ~25 New Jersey rows sourced only to the Pinelands Alliance roundup (each still needs its own primary source).

## Review-queue backlog

Read-only per policy — nothing promoted or dismissed. Human triage only, per CLAUDE.md (`source`/`as_of` must come from each locality's own .gov page).

### Moratoriums (`data/moratorium_candidates.json`, updated 2026-09-06)
1,480 total — **1,336 new / awaiting review**, 138 promoted, 6 dismissed.

`triage_moratorium_candidates.py --tier A` (cited — link or named document in hand, so cheapest to promote): **111** ready candidates. Top 10 by outlet corroboration:
- **Effingham** (3 outlets) — "Warnock calls for statewide data center moratorium after Effingham Co. visit"
- **Fairbanks** (3 outlets) — "Fairbanks Borough weighs data center regulations, seeks state moratorium"
- **Hudson** (3 outlets) — "Scenic Hudson president praises Gov. Hochul's moratorium on data centers"
- **Effingham County** (2 outlets) — "Warnock calls for data center moratorium during Effingham County visit"
- **Effingham County** (2 outlets) — "Effingham County residents sue county over data center zoning ordinance, demand transparency"
- **Fairbanks North Star** (2 outlets) — "Fairbanks North Star Borough Assembly doubles up on AI data center moratorium request"
- **Hudson** (2 outlets) — "Hudson Valley residents dissatisfied with data center moratorium"
- **Pataskala** (2 outlets) — "Pataskala rejects company's data center proposal in industrial park"
- **Pott** (2 outlets) — "Residents request a moratorium at Pott County public hearing on data centers"
- **VB** (2 outlets) — "VB City Council establishes 12-month moratorium on data centers in the city"

Other tiers in the queue: B (structured, source still to find) 5 · C (thin/undated/pending) 194 · D (unlocated headline) 582.

### Projects (`data/project_candidates.json`, updated 2026-08-31)
161 total — **49 new / awaiting review**, 65 promoted, 47 dismissed. No triage-tier script exists for this queue yet (only the moratorium queue has one) — newest 10 by `first_seen` (all 2026-08-31):
- Zoning meeting on Emmaus Avenue data center in Allentown postponed
- Residents appeal Throop's data center zoning, argue it benefits private interests
- Spokane, ? — Upcoming public hearings to address data center zoning code in Spokane County
- Hancock, ? — Data center debate heats up in Hancock County ahead of re-zoning hearing
- Two more Metro Detroit communities move to amend data center zoning
- Henry, ? — Henry County supervisors approve new zoning rules for potential data centers
- Salem Twp. supervisors to hold hearing on 3rd data center zoning
- Adelanto planners reject data center zoning update, item moves to council
- Residents urge Butler to hold off on rezoning land for data center's third phase
- Platte, ? — Platte County recommends rezoning private ranchland for proposed data center
