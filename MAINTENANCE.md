# Weekly data-freshness digest — 2026-10-05

**173 tracker rows need a human look this week (42 expired + 55 expiring-soon + 76 unclassified-term): 0 hearings scheduled in the next 30 days (but 20 projects stuck in "awaiting decision", one for 420 days), 2 stale registries with no `as_of`, and a review-queue backlog of 1,864 new moratorium candidates / 101 new project candidates awaiting triage.**

## Upcoming hearings (next 30 days)

`PROJECTS_DF` / `project_status()`: **no project has a scheduled hearing in the next 30 days** (or even the next `PROJECT_HEARING_SOON_DAYS` window) — every recorded `hearing_date` is already in the past.

20 projects are instead stuck in **"Awaiting decision"** — hearing already held, no outcome recorded, so a ruling could land with no further public notice. Oldest (most overdue) first:

| Project | Locality | Hearing held | Days since |
|---|---|---|---|
| Wolcott Data Center (Mid-America Commerce Park) | White County, IN | 2025-08-11 | 420d |
| TeraWulf Cayuga data center (former Cayuga Power Plant) | Lansing (Tompkins County), NY | 2026-04-27 | 161d |
| Cave City data center (Kentucky Industrial Alliance) | Cave City (Barren County), KY | 2026-07-20 | 77d |
| Project Iron Spur | Rural Hall (Forsyth County), NC | 2026-07-30 | 67d |
| Project Double Reed (Stream US Data Centers at STAMP) | Alabama (Genesee County), NY | 2026-08-03 | 63d |
| Posey County data center (Boberg/Hoenert Roads) | Posey County, IN | 2026-08-04 | 62d |
| Stonebridge Associates campus at Powder Mill Works | North Beaver & Mahoning townships, PA | 2026-08-05 | 61d |
| Smithfield Gateway Data Center | Smithfield Township (Monroe County), PA | 2026-08-12 | 54d |
| Burkhalter Road data center (4AM Development) | Statesboro (Bulloch County), GA | 2026-08-18 | 48d |
| Manse Technology Campus (Project Blackjack) | Pahrump (Nye County), NV | 2026-08-18 | 48d |

(10 more awaiting decision, most recent hearing 2026-09-24 — Plaza 500, Lincolnia VA, 4d ago.) **Action:** `Wolcott Data Center` (420 days, White County IN) is the one most likely to just be stale data rather than a real pending decision — worth a human check on whether the record needs an `outcome` set or the project has gone quiet.

## Stale registries

`registry_provenance()` over `REGISTRY_PROVENANCE`: **2 of 14** registries flagged — both have no `as_of` recorded at all, which counts as stale regardless of churn tier (unchanged from last week):

| Registry | as_of | churn | Note |
|---|---|---|---|
| `DC_SITES_DF` | None | medium | No verification date recorded — 18mo shelf life once dated |
| `STATE_PUCS_DF` | None | low | No verification date recorded — 36mo shelf life once dated |

Action: set a real `as_of` (or confirm these were deliberately never dated) rather than leaving them silently uncaptioned.

## Moratorium audit (`verify_moratoriums.py --offline`)

863/863 tracker rows carry a `source`; 44/44 quotable claims (case studies, benchmarks, concessions) carry a citation + `as_of`. **Missing-source: 0. Stale `as_of` (>180d): 0.** Link-checking was skipped (`--offline`), so nothing below has been confirmed to still resolve.

| Check | Count |
|---|---|
| expired | 42 |
| expiring (≤60d) | 55 |
| unclassified-term (`term_kind=unknown`) | 76 |
| undated-term (`fixed_undated`, no end date) | 44 |

### Expired — term end date has passed, `effective_status` needs confirming (42)

Oldest first (dates are the recorded term end, not a hearing):

| Locality | State | Term ended |
|---|---|---|
| Groton | CT | 2023-06-21 |
| Madison County | NC | 2024-06-13 |
| Fluvanna County | VA | 2026-01-31 |
| Mason | MI | 2026-02-03 |
| Aurora | IL | 2026-03-24 |
| Montebello | CA | 2026-03-28 |
| Montour County | PA | 2026-04-30 |
| Pittsfield Township | MI | 2026-05-17 |
| Howell Township | MI | 2026-05-20 |
| Tyrone Township | MI | 2026-06-01 |
| Jerome Township | OH | 2026-06-01 |
| Lenox Township | MI | 2026-06-02 |
| Waterville | OH | 2026-06-08 |
| Brevard | NC | 2026-06-23 |
| Caledonia Township | MI | 2026-07-01 |
| Griffin | GA | 2026-07-12 |
| Armada Township | MI | 2026-07-13 |
| Saginaw | MI | 2026-07-13 |
| Covington | GA | 2026-07-19 |
| Pontiac | MI | 2026-07-21 |
| Sylvan Township | MI | 2026-07-22 |
| Leavenworth County | KS | 2026-08-11 |
| Saugatuck Township | MI | 2026-08-11 |
| Kingsland | GA | 2026-08-09 |
| Hayes Township | MI | 2026-08-09 |
| Lodi Township | MI | 2026-08-02 |
| York Township | MI | 2026-08-12 |
| Massillon | OH | 2026-08-14 |
| Hall County | GA | 2026-08-25 |
| Wixom | MI | 2026-08-26 |
| Floyd County | GA | 2026-08-28 |
| Lyon Charter Township | MI | 2026-08-30 |
| Mount Orab | OH | 2026-08-30 |
| Hogansville | GA | 2026-09-01 |
| Birmingham | AL | 2026-09-03 |
| Wichita | KS | 2026-09-10 |
| Augusta / Augusta-Richmond County | GA | 2026-09-15 |
| Roswell | GA | 2026-09-20 |
| Waterford Township | MI | 2026-10-01 |
| Tulare County | CA | 2026-10-02 |
| Front Royal | VA | 2026-10-04 |

Each needs its source re-read to set `effective_status` (lapsed / extended / rescinded / became permanent zoning) — the audit doesn't guess. **Changed since last week's digest:** Tulare County CA and Front Royal VA newly crossed into expired; Rockdale County GA dropped off (now shows in expiring-soon with a later end date — someone updated the row) and Scott County KY dropped off (now `undated-term` — its own source says it was extended to March, but no end date has been entered yet).

### Expiring soon — within 60 days (55)

Nearest-first:

| Locality | State | Ends | Days left |
|---|---|---|---|
| Newton County | GA | 2026-10-05 | 0 |
| Calaveras County | CA | 2026-10-09 | 4 |
| Lake Elsinore | CA | 2026-10-09 | 4 |
| Rockdale County | GA | 2026-10-09 | 4 |
| Bangor | ME | 2026-10-10 | 5 |
| Tallmadge | OH | 2026-10-10 | 5 |
| Palm Springs | CA | 2026-10-10 | 5 |
| Morgan Hill | CA | 2026-10-10 | 5 |
| Escondido | CA | 2026-10-12 | 7 |
| Vienna Township (Trumbull Co.) | OH | 2026-10-16 | 11 |
| Cleveland | OH | 2026-10-16 | 11 |
| Indio | CA | 2026-10-16 | 11 |
| Mendocino County | CA | 2026-10-16 | 11 |
| Eureka | CA | 2026-10-17 | 12 |
| Plainfield | IL | 2026-10-18 | 13 |
| White County | IN | 2026-10-20 | 15 |
| Lowndes County | GA | 2026-10-25 | 20 |
| Lowndes County | AL | 2026-10-25 | 20 |
| Richmond | CA | 2026-10-30 | 25 |
| Gilroy | CA | 2026-10-29 | 24 |
| Lexington (Fayette County) | KY | 2026-10-31 | 26 |

(+ 34 more between 27–59 days out, including several PA townships on 180-day curative-amendment clocks — Upper Burrell, Butler Township, Smithfield Township, West Whiteland — and a cluster of GA/KS/IA/ME counties. Full list on request.)

These are exactly the rows most likely to get quietly extended without the tracker noticing — worth a status check before they flip to "expired," especially **Newton County, GA (0 days left — expires today)**.

### Unclassified term (76) and undated fixed term (44)

Not immediately time-critical but a data-quality backlog: 76 rows have no `term` declared at all (could be permanent bans or unresearched pauses — the page can't tell the reader which), and 44 more have a recorded fixed-duration note but no end date to compute against. Heavy NJ Pinelands-area concentration in the unclassified set (one shared source, `pinelandsalliance.org/datacenters`, covering ~24 townships) and a Nebraska cluster (7 counties, one shared `nebraskapublicmedia.org` source) in the undated set — each worth one research pass rather than one row at a time.

## Review-queue backlog

**Not promoted or dismissed — read-only counts, no triage performed here.**

| Queue | New (awaiting review) | Total |
|---|---|---|
| `data/moratorium_candidates.json` | 1,864 | 2,093 (188 promoted, 41 dismissed) |
| `data/project_candidates.json` | 101 | 213 (65 promoted, 47 dismissed) |

Of the 1,864 new moratorium candidates, only 541 have a `guess_locality` resolved; `triage_moratorium_candidates.py --tier A` separately finds **177 "cited" candidates** (link or named document already in hand, 1,225 distinct not-yet-tracked after collapsing repeat coverage) ready to promote fastest — top of that list: Evansville (35 outlets), Eugene (6), Boerne (4), Beaufort County (3), Hudson/Hochul NY moratorium (3).

### Top 10 newest moratorium candidates with a resolved locality (of 541)

| First seen | Locality (guessed) | Title |
|---|---|---|
| 2026-10-04 | Ransom Twp. | Ransom Twp. supervisors poised to vote on data center ordinance |
| 2026-10-03 | Columbus | Columbus County to consider 120-day data center moratorium |
| 2026-10-03 | McHenry | McHenry County mulls data center moratorium |
| 2026-10-03 | Statesboro | Group called Protect Statesboro plans petition to repeal data center ordinance |
| 2026-10-02 | Rutherford | Rutherford County discussing one-year data center moratorium |
| 2026-10-02 | Oakland | Oakland City Council prepares vote on data center moratorium |
| 2026-10-02 | Bucksport | Bucksport Town Council advances proposed 180-day moratorium |
| 2026-10-01 | Mesa | Mesa County Commissioners approve data center moratorium |
| 2026-10-01 | Calumet (county name in headline) | "Why Calumet County hasn't passed a data center moratorium" |
| (same day) | — | several duplicate entries from repeat RSS coverage of the above |

*Guessed localities above are the scanner's own inference, not confirmed — verify against the locality's own .gov source before promoting, per CLAUDE.md.*

### Top project candidates with a resolved locality (of 41)

| First seen | Locality (guessed) | Title |
|---|---|---|
| 2026-09-28 | Walls | Walls Planning Commission Denies Data Center Rezoning Request |
| 2026-09-28 | Colleton | Colleton County leaders OK zoning changes to allow data centers farther north |
| 2026-09-28 | Stokes | Data center proposal in Stokes County inches closer to a resolution |
| 2026-09-28 | Spotsylvania | Spotsylvania Planning Commission approves mega data center complex |
| 2026-09-28 | Corunna | Corunna City Council advances data center ordinance proposal |
| 2026-09-28 | Pima | Pima County halts new data center permits for 120 days to update zoning rules |
| 2026-09-28 | Fauquier County | Fauquier County Planning Commission recommends restricting data center development |
| 2026-09-21 | Custer (MT) | Data Center concerns dominate Custer County zoning hearing |
| 2026-09-21 | Colleton | Colleton County approves new zoning changes to allow data center |
| 2026-09-21 | Stokes | Data Center Debate: Stokes County Commissioners hold public hearing |

Promotion still requires reading each locality's own .gov source for `source` + `as_of` — nothing above has been promoted or dismissed by this run.
