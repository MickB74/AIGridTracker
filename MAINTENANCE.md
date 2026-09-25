# Weekly data-freshness digest — 2026-09-21

**1 hearing inside 30 days · 1 moratorium expires in 2 days · 41 moratoriums already past their stated term · 2 registries with no `as_of` · 1,622 moratorium + 49 project candidates awaiting triage.**

This is a read-only summary. Nothing in `src/`, `web/`, or any registry was edited; no candidate was promoted or dismissed.

## Upcoming hearings (next 30 days)

Derived from `PROJECTS_DF` / `project_status()` (`src/constants.py`), computed as of 2026-09-21.

- **Plaza 500 (Lincolnia)** — Lincolnia (Fairfax County), VA — hearing **2026-09-24 (3 days)**

Only one project in the tracker carries a `hearing_date` in the near term — worth double-checking that this isn't a coverage gap (many rows sit in "In review" / "Awaiting decision" with no dated next step). Separately, 19 projects are in `phase=awaiting` (heard, decision pending, no dated hearing to re-check) — not listed individually here since they have no forward date, but worth a scan if you're chasing decisions this month.

## Stale registries

From `REGISTRY_PROVENANCE` / `registry_provenance()` in `src/constants.py` — flagged when `as_of` is missing or older than the registry's churn-based shelf life (low 36mo / medium 18mo / high 9mo).

| Registry | as_of | churn | Why flagged |
|---|---|---|---|
| `DC_SITES_DF` | *(none recorded)* | medium | No verification date — cannot be shown as current |
| `STATE_PUCS_DF` | *(none recorded)* | low | No verification date — cannot be shown as current |

All 11 other tracked registries (`STATE_DC_DF`, `STATE_GRID_PROFILES`, `HOUSE_RACES_2026`, `SENATORS`, `SENATE_RACES_2026`, `MORATORIUMS_DF`, `MEGA_PROJECTS_DF`, `PROJECTS_DF`, `EXECUTIVES_DF`, `STATE_STUDIES`, `STATE_PERMIT_PORTALS`) are within their shelf life.

## Moratorium audit (`scripts/verify_moratoriums.py --offline`)

853/853 tracker rows carry a `source`. **Missing-source: 0. Stale-as-of (>180d): 0.** (Link-liveness wasn't checked — this ran `--offline`; run the online pass separately if a link-rot sweep is due.)

- **Expired (term already lapsed, still shows Enacted/Expired on the page): 41**
- **Undated term (fixed-length term, no end date recorded): 41**
- **Unclassified term (no end date, no `term` declared — page can't tell ban vs. unresearched pause): 76**
- **Expiring soon (next 30–60 days): 37**

### Expiring soon — newest deadline first (37)

- Waterford Township, MI — ends 2026-09-23 (2d)
- Tulare County, CA — ends 2026-10-02 (11d)
- Front Royal, VA — ends 2026-10-04 (13d)
- Newton County, GA — ends 2026-10-05 (14d)
- Pierce Township, OH — ends 2026-10-09 (18d)
- Calaveras County, CA — ends 2026-10-09 (18d)
- Lake Elsinore, CA — ends 2026-10-09 (18d)
- Bangor, ME — ends 2026-10-10 (19d)
- Tallmadge, OH — ends 2026-10-10 (19d)
- Palm Springs, CA — ends 2026-10-10 (19d)
- Morgan Hill, CA — ends 2026-10-10 (19d)
- Escondido, CA — ends 2026-10-12 (21d)
- Vienna Township (Trumbull Co.), OH — ends 2026-10-16 (25d)
- Cleveland, OH — ends 2026-10-16 (25d)
- Indio, CA — ends 2026-10-16 (25d)
- Mendocino County, CA — ends 2026-10-16 (25d)
- Eureka, CA — ends 2026-10-17 (26d)
- Plainfield, IL — ends 2026-10-18 (27d)
- White County, IN — ends 2026-10-20 (29d)
- Lowndes County, GA — ends 2026-10-25 (34d)
- Lowndes County, AL — ends 2026-10-25 (34d)
- Lexington (Fayette County), KY — ends 2026-10-31 (40d)
- West Whiteland Township, PA — ends 2026-11-01 (41d)
- Upper Burrell Township, PA — ends 2026-11-02 (42d)
- Smithfield Township, PA — ends 2026-11-02 (42d)
- Charlotte, NC — ends 2026-11-05 (45d)
- Lavon, TX — ends 2026-11-05 (45d)
- Lysander (Onondaga Co.), NY — ends 2026-11-06 (46d)
- Camden County, GA — ends 2026-11-06 (46d)
- Johnson County, IA — ends 2026-11-08 (48d)
- Butler Township, PA — ends 2026-11-08 (48d)
- Riley County, KS — ends 2026-11-12 (52d)
- Dickinson County, IA — ends 2026-11-12 (52d)
- Springfield, MO — ends 2026-11-17 (57d)
- Putnam County, IN — ends 2026-11-17 (57d)
- Meridian Township, MI — ends 2026-11-19 (59d)
- Barnes County, ND — ends 2026-11-19 (59d)

### Expired — most recent lapse first (41)

- Roswell, GA — term ran to 2026-09-20
- Augusta, GA — term ran to 2026-09-19
- Augusta-Richmond County, GA — term ran to 2026-09-19
- Scott County, KY — term ran to 2026-09-13
- Wichita, KS — term ran to 2026-09-10
- Rockdale County, GA — term ran to 2026-09-08
- Birmingham, AL — term ran to 2026-09-03
- Hogansville, GA — term ran to 2026-09-01
- Mount Orab, OH — term ran to 2026-08-30
- Lyon Charter Township, MI — term ran to 2026-08-30
- Floyd County, GA — term ran to 2026-08-28
- Wixom, MI — term ran to 2026-08-26
- Hall County, GA — term ran to 2026-08-25
- Massillon, OH — term ran to 2026-08-14
- York Township, MI — term ran to 2026-08-12
- Saugatuck Township, MI — term ran to 2026-08-11
- Leavenworth County, KS — term ran to 2026-08-11
- Hayes Township, MI — term ran to 2026-08-09
- Kingsland, GA — term ran to 2026-08-09
- Lodi Township, MI — term ran to 2026-08-02
- Sylvan Township, MI — term ran to 2026-07-22
- Pontiac, MI — term ran to 2026-07-21
- Covington, GA — term ran to 2026-07-19
- Armada Township, MI — term ran to 2026-07-13
- Saginaw, MI — term ran to 2026-07-13
- Griffin, GA — term ran to 2026-07-12
- Caledonia Township, MI — term ran to 2026-07-01
- Brevard, NC — term ran to 2026-06-23
- Waterville, OH — term ran to 2026-06-08
- Lenox Township, MI — term ran to 2026-06-02
- Tyrone Township, MI — term ran to 2026-06-01
- Jerome Township, OH — term ran to 2026-06-01
- Howell Township, MI — term ran to 2026-05-20
- Pittsfield Township, MI — term ran to 2026-05-17
- Montour County, PA — term ran to 2026-04-30
- Montebello, CA — term ran to 2026-03-28
- Aurora, IL — term ran to 2026-03-24
- Mason, MI — term ran to 2026-02-03
- Fluvanna County, VA — term ran to 2026-01-31
- Madison County, NC — term ran to 2024-06-13 (oldest — over 2 years lapsed)
- Groton, CT — term ran to 2023-06-21 (oldest — over 3 years lapsed)

*(76 more rows are "unclassified-term" — no end date and no `term` declared, so the page can't tell a permanent ban from an unresearched pause. Full list in `python3 scripts/verify_moratoriums.py --offline`.)*

## Review-queue backlog

**Never auto-promoted or dismissed** — promotion requires a human reading the locality's own .gov source (CLAUDE.md, `MORATORIUMS_DF` sourcing rules).

### Moratorium candidates (`data/moratorium_candidates.json`)
1,622 new / 1,830 total (167 promoted, 41 dismissed). Ranked by `scripts/triage_moratorium_candidates.py --tier A` (cited — link or named document in hand, cheapest to verify): **147 tier-A candidates**, top 10 by outlet coverage:

- Evansville — "Evansville City Council to consider data center moratorium" (32 outlets, first seen 2026-09-20)
- Eugene — "Residents urge Eugene City Council to consider data center moratorium amid AI growth" (6 outlets, first seen 2026-09-20)
- Boerne — "Restrictions on data centers move to Boerne City Council" (4 outlets, first seen 2026-09-20)
- Beaufort County — "Residents voice support for data center moratorium in Beaufort County" (3 outlets, first seen 2026-09-20)
- Clermont County — "San Francisco company pitches data center in Clermont County despite local moratorium" (3 outlets, first seen 2026-09-20)
- Hudson — "Scenic Hudson president praises Gov. Hochul's moratorium on data centers" (3 outlets, first seen 2026-09-02)
- Beaufort County — "Beaufort County data center moratorium hearing postponed, officials say" (2 outlets, first seen 2026-09-20)
- Gilroy — "Gilroy considers moratorium on new data centers" (2 outlets, first seen 2026-09-20)
- Hudson Valley — "Hudson Valley residents dissatisfied with data center moratorium" (2 outlets, first seen 2026-09-02)
- Manchester & Upper Township — "Data Center Bans Spread As Manchester And Upper Township Approve Restrictions" (2 outlets, first seen 2026-09-20)

(States weren't resolved by the scanner for any of these — confirm locality + state before researching. Full ranked list: `python3 scripts/triage_moratorium_candidates.py --tier A`.)

### Project candidates (`data/project_candidates.json`)
49 new / 161 total (65 promoted, 47 dismissed). No triage script exists for this queue yet — newest 10 'new' items by first-seen date:

- Spokane County, WA (guessed) — "Upcoming public hearings to address data center zoning code in Spokane County." (2026-08-31)
- Hancock County (guessed, state unresolved) — "Data center debate heats up in Hancock County ahead of re-zoning hearing" (2026-08-31)
- Henry County (guessed, state unresolved) — "Henry County supervisors approve new zoning rules for potential data centers" (2026-08-31)
- Platte County (guessed, state unresolved) — "Platte County Recommends Rezoning Private Ranchland For Proposed Data Center" (2026-08-31)
- Allentown, PA (locality unresolved) — "Zoning meeting on Emmaus Avenue data center in Allentown postponed"
- Throop, PA (locality unresolved) — "Residents appeal Throop's data center zoning, argue it benefits private interests"
- Metro Detroit, MI (locality unresolved) — "Two more Metro Detroit communities move to amend data center zoning"
- Salem Township (locality unresolved) — "Salem Twp. supervisors to hold hearing on 3rd data center zoning"
- Adelanto, CA (locality unresolved) — "Adelanto planners reject data center zoning update, item moves to council"
- Butler (locality unresolved) — "Residents urge ask Butler to hold off on rezoning land for data center's third phase"

All 10 above are from the 2026-08-31 scan batch — the queue hasn't been triaged in ~3 weeks; worth a look this week.
