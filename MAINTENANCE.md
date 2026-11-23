# Weekly data-freshness digest — 2026-11-23

**132 time-critical moratorium rows (49 expired + 83 expiring ≤30d) · 2 stale registries · 0 hearings scheduled in the next 30 days, but 20 projects stuck in "Awaiting decision" (one 469 days overdue) · 2,832 moratorium leads and 228 project leads still awaiting human triage.**

This is a summary only — no registry rows, candidates, or `web/` files were edited.

## Upcoming hearings (next 30 days)

- **0** projects have a `hearing_date` in the future. `PROJECTS_DF` currently has no dated, scheduled hearings at all (0 rows in `phase == "hearing"` with `days_to_hearing >= 0`).
- **20** projects are stuck in **Awaiting decision** (hearing already happened, no `decided_date`/`outcome` recorded) — these are the most actionable follow-ups right now since a vote could land any time with no public notice window. Most overdue first:
  - **blue-ladder-wolcott-data-center-in** — White County, IN — heard 2025-08-11 (**469 days** ago)
  - **terawulf-cayuga-lansing-ny** — Lansing, NY — heard 2026-04-27 (210 days ago)
  - **cave-city-doyle-avenue-data-center** — Cave City, KY — heard 2026-07-20 (126 days ago)
  - **project-iron-spur-rural-hall-nc** — Rural Hall, NC — heard 2026-07-30 (116 days ago)
  - **powder-mill-works-lawrence-pa** — North Beaver & Mahoning townships, PA — heard 2026-08-05 (110 days ago)
  - ...plus 15 more (posey-county-in, project-flex-mi, double-reed-ny, stamp/alabama-ny dup, dickerson-atmosphere-md, hanover-starpointe-pa, plymouth-conshohocken-pa, bastrop-bcg-tx, pahrump-manse-nv, smithfield-gateway-pa, platte-layer4-wy, vermaland-la-osa-az, kearney-ne, aligned-pataskala-oh, burkhalter-statesboro-ga)
  - Action: someone should call each clerk for a vote date / confirm it already happened off-record, since the tracker can't tell the two apart.

## Stale registries

`REGISTRY_PROVENANCE` flags **2 of 14** tracked registries — both for having **no `as_of` at all**, not for age:

| Registry | as_of | churn |
|---|---|---|
| `DC_SITES_DF` | None recorded | medium (9mo/18mo/36mo shelf life by churn) |
| `STATE_PUCS_DF` | None recorded | low |

No registry is stale *by age* this run — the other 12 are within their churn-based shelf life.

## Moratorium audit (`verify_moratoriums.py --offline`)

887/887 tracker rows carry a source. Breakdown of flagged rows:

| Check | Count |
|---|---|
| expiring (≤ `EXPIRING_SOON_DAYS`) | 83 |
| expired | 49 |
| undated-term (fixed term, no end date) | 80 |
| unclassified-term (no `term` declared) | 78 |
| missing-source | 0 |
| stale-as-of (>180 days) | 0 |

**Expired — oldest unresolved first (time-critical, sample of 15 of 49):**
- Minneapolis, MN — ran to 2026-11-21
- Meridian Township, MI — ran to 2026-11-19
- Putnam County, IN — ran to 2026-11-17
- Riley County, KS — ran to 2026-11-12
- Dickinson County, IA — ran to 2026-11-12
- Upper Burrell Township, PA — ran to 2026-11-02
- Lowndes County, GA — ran to 2026-10-25
- White County, IN — ran to 2026-10-20
- Plainfield, IL — ran to 2026-10-18
- Caledonia Township, MI — ran to 2026-10-17
- Eureka, CA — ran to 2026-10-17
- Vienna Township (Trumbull Co.), OH — ran to 2026-10-16
- Cleveland, OH — ran to 2026-10-16
- Indio, CA — ran to 2026-10-16
- West Whiteland Township, PA — ran to 2026-10-14
- ...plus 34 more (full list in the script's own `--out` worklist, not reproduced here)

**Expiring soon — next 20 of 83 by date:**
- Washington Township (Macomb Co.), MI — ends 2026-11-23 (today)
- Marshalltown, IA — ends 2026-11-23 (today)
- Bloomington, IL — ends 2026-11-26 (3d)
- Forest Park, GA — ends 2026-11-29 (6d)
- Brunswick, ME — ends 2026-11-29 (6d)
- Nashville, TN — ends 2026-12-01 (8d)
- Braceline Township, OH — ends 2026-12-02 (9d)
- Johnson City, TN — ends 2026-12-03 (10d)
- Hazle Township, PA — ends 2026-12-05 (12d)
- Little Britain Township, PA — ends 2026-12-06 (13d)
- Lake County, FL — ends 2026-12-07 (14d)
- Box Elder County, UT — ends 2026-12-07 (14d)
- Center Township, PA — ends 2026-12-07 (14d)
- Green Charter Township, MI — ends 2026-12-09 (16d)
- Howland Township, OH — ends 2026-12-10 (17d)
- Milford, UT — ends 2026-12-13 (20d)
- Brookville, PA — ends 2026-12-14 (21d)
- Cumberland County, NC — ends 2026-12-15 (22d)
- Starke County, IN — ends 2026-12-15 (22d)
- Lycoming County, PA — ends 2026-12-15 (22d)
- ...plus 63 more ending through mid-2027 (see worklist)

Link-checking was skipped (`--offline`), so none of the above has been confirmed to still resolve.

## Review-queue backlog

| Queue | New (awaiting review) | Total |
|---|---|---|
| `data/moratorium_candidates.json` | **2,832** | 3,132 (249 promoted, 51 dismissed) |
| `data/project_candidates.json` | **228** | 340 (65 promoted, 47 dismissed) |

The moratorium backlog is large and growing faster than it's being triaged — worth a dedicated pass soon. Top 10 newest moratorium leads to triage first:

- 2026-11-22 — Asbury, ? — "Draft ordinance would ban hyperscale data centers in Asbury"
- 2026-11-22 — Roanoke, ? — "Roanoke City Council seeks statewide data center pause as local project moves forward"
- 2026-11-22 — Cameron, ? — "Cameron County rejects tax abatement for SpaceX's $24B data center"
- 2026-11-22 — ?, ? — "DW News: Protests against new AI data centers are making headlines..."
- 2026-11-22 — ?, ? — "City Beat: Council modifies data center definitions bill, extends moratorium into next year"
- 2026-11-21 — McHenry, ? — "'Protect people first': McHenry County Board approves 12-month ban on new data centers"
- 2026-11-21 — ?, ? — "Proposed Ordinance to Ban Hyperscale Data Centers"
- 2026-11-21 — ?, ? — "Letters: San Jose mustn't cede its leadership in tech with data center moratorium"
- 2026-11-21 — ?, ? — "Roanoke Council Seeks Statewide Data Center Pause"
- 2026-11-21 — ?, ? — "YESTERDAY IN SUPES: Temporary Ban on Data Centers Extended for Another 10 Months"

Top 10 newest project leads to triage first:

- 2026-11-16 — VA — "Some Southwest Virginia localities look to zoning to slow down data centers"
- 2026-11-16 — MI — "Rezoning meeting canceled in Michigan township engulfed in data center controversy"
- 2026-11-16 — ?, ? — "Some Georgetown residents opposing proposed data center ahead of zoning hearing"
- 2026-11-16 — ?, ? — "Data center developers request delay in public hearing"
- 2026-11-16 — Lenox, ? — "Lenox Township to consider rezoning of land. Some think it's a data center"
- 2026-11-16 — ?, ? — "Florham Park Council to Consider Data Center Zoning, Stormwater Regulations"
- 2026-11-16 — Red Deer, ? — "Facebook group forms after Red Deer County data centre proposed"
- 2026-11-16 — Rossford, ? — "Rossford Planning Commission approves special use permit, preliminary site plan"
- 2026-11-16 — ?, ? — "Rossford commission OKs zoning for data center"
- 2026-11-16 — ?, ? — "Special-use permit requirement for East Dundee data centers heads to board"

Per CLAUDE.md, none of these were promoted or dismissed — each needs a human to read the locality's own .gov source before it can become a registry row.
