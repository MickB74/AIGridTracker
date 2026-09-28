# Weekly data-freshness digest — 2026-09-28

**161 items need a human look this week: 0 hearings scheduled in the next 30 days, 42 expired + 43 expiring-soon + 76 unclassified-term moratorium rows, 2 stale registries, and a review-queue backlog of 1,765 new moratorium candidates / 83 new project candidates.**

## Upcoming hearings (next 30 days)

`PROJECTS_DF` / `project_status()`: **no project has a scheduled hearing in the next 30 days** (or even the next `PROJECT_HEARING_SOON_DAYS` = 45).

20 projects are instead in **"Awaiting decision"** — hearing already held, no decision recorded yet, so a ruling could land without further public notice. The most recent, most time-critical:

| Project | Locality | Hearing held | Days since |
|---|---|---|---|
| Plaza 500 (Lincolnia) | Lincolnia (Fairfax County), VA | 2026-09-24 | 4d |
| Dickerson Data Center Campus (Atmosphere) | Dickerson (Montgomery County), MD | 2026-09-10 | 18d |
| Prime Data Centers — Starpointe Business Park | Hanover Township (Washington County), PA | 2026-08-31 | 28d |
| Site Layer 4 Data Center Campus | Wheatland (Platte County), WY | 2026-08-26 | 33d |
| La Osa | Pinal County (near Eloy), AZ | 2026-08-26 | 33d |
| Aligned Data Centers — Pataskala industrial park | Pataskala (Licking County), OH | 2026-08-25 | 34d |
| Project Flex | Lyon Township (Oakland County), MI | 2026-08-24 | 35d |
| BCG Cedar Creek Campus | Cedar Creek (Bastrop County), TX | 2026-08-24 | 35d |
| Kearney Data Center | Kearney, NE | 2026-08-21 | 38d |
| Burkhalter Road data center (4AM Development) | Statesboro (Bulloch County), GA | 2026-08-18 | 41d |

(10 more awaiting decision, oldest hearing 2025-08-11 — Wolcott Data Center, White County IN. Full list on request.)

## Stale registries

`registry_provenance()` over `REGISTRY_PROVENANCE`: **2 of 13** registries flagged (no `as_of` recorded — treated as stale regardless of churn tier):

| Registry | as_of | churn | Note |
|---|---|---|---|
| `DC_SITES_DF` | None | medium | No verification date recorded — shelf life is 18mo once dated |
| `STATE_PUCS_DF` | None | low | No verification date recorded — shelf life is 36mo once dated |

Action: set a real `as_of` (or confirm these were never populated) rather than leaving them silently uncaptioned.

## Moratorium audit (`verify_moratoriums.py --offline`)

858/858 tracker rows carry a `source`; 44/44 quotable claims (case studies, benchmarks, concessions) carry a citation + `as_of`. **Missing-source: 0. Stale `as_of` (>180d): 0.** Link-checking was skipped (`--offline`), so nothing below has been confirmed to still resolve.

| Check | Count |
|---|---|
| expired | 42 |
| expiring (≤60d) | 43 |
| unclassified-term (`term_kind=unknown`) | 76 |
| undated-term (`fixed_undated`, no end date) | 43 |

### Expired — term end date has passed, `effective_status` needs confirming (42)

Oldest first (dates are the recorded term end, not a hearing):

| Locality | State | Term ended |
|---|---|---|
| Groton | CT | 2023-06-21 |
| Madison County | NC | 2024-06-13 |
| Fluvanna County | VA | 2026-01-31 |
| Mason | MI | 2026-02-03 |
| Montebello | CA | 2026-03-28 |
| Aurora | IL | 2026-03-24 |
| Montour County | PA | 2026-04-30 |
| Howell Township | MI | 2026-05-20 |
| Pittsfield Township | MI | 2026-05-17 |
| Lenox Township | MI | 2026-06-02 |
| Tyrone Township | MI | 2026-06-01 |
| Jerome Township | OH | 2026-06-01 |
| Waterville | OH | 2026-06-08 |
| Brevard | NC | 2026-06-23 |
| Caledonia Township | MI | 2026-07-01 |
| Griffin | GA | 2026-07-12 |
| Armada Township | MI | 2026-07-13 |
| Saginaw | MI | 2026-07-13 |
| Covington | GA | 2026-07-19 |
| Pontiac | MI | 2026-07-21 |
| Sylvan Township | MI | 2026-07-22 |
| Massillon | OH | 2026-08-14 |
| Leavenworth County | KS | 2026-08-11 |
| Saugatuck Township | MI | 2026-08-11 |
| Kingsland | GA | 2026-08-09 |
| Lodi Township | MI | 2026-08-02 |
| Hayes Township | MI | 2026-08-09 |
| York Township | MI | 2026-08-12 |
| Hall County | GA | 2026-08-25 |
| Wixom | MI | 2026-08-26 |
| Floyd County | GA | 2026-08-28 |
| Mount Orab | OH | 2026-08-30 |
| Lyon Charter Township | MI | 2026-08-30 |
| Hogansville | GA | 2026-09-01 |
| Birmingham | AL | 2026-09-03 |
| Rockdale County | GA | 2026-09-08 |
| Wichita | KS | 2026-09-10 |
| Scott County | KY | 2026-09-13 |
| Augusta / Augusta-Richmond County | GA | 2026-09-19 |
| Roswell | GA | 2026-09-20 |
| Waterford Township | MI | 2026-09-23 |

Each needs its source re-read to set `effective_status` (lapsed / extended / rescinded / became permanent zoning) — the audit doesn't guess.

### Expiring soon — within 60 days (43)

Nearest-first:

| Locality | State | Ends | Days left |
|---|---|---|---|
| Front Royal | VA | 2026-10-04 | 6 |
| Newton County | GA | 2026-10-05 | 7 |
| Tulare County | CA | 2026-10-02 | 4 |
| Calaveras County | CA | 2026-10-09 | 11 |
| Pierce Township | OH | 2026-10-09 | 11 |
| Lake Elsinore | CA | 2026-10-09 | 11 |
| Morgan Hill | CA | 2026-10-10 | 12 |
| Tallmadge | OH | 2026-10-10 | 12 |
| Palm Springs | CA | 2026-10-10 | 12 |
| Escondido | CA | 2026-10-12 | 14 |
| Cleveland | OH | 2026-10-16 | 18 |
| Indio | CA | 2026-10-16 | 18 |
| Mendocino County | CA | 2026-10-16 | 18 |
| Eureka | CA | 2026-10-17 | 19 |
| Plainfield | IL | 2026-10-18 | 20 |
| White County | IN | 2026-10-20 | 22 |
| Lowndes County | GA | 2026-10-25 | 27 |
| Lowndes County | AL | 2026-10-25 | 27 |
| Putnam County | IN | 2026-11-17 | 50 |
| Hillsboro | OR | 2026-11-24 | 57 |
| Hart | MI | 2026-11-26 | 59 |

(+ 22 more between 34–59 days out, including several PA townships on 180-day curative-amendment clocks — Upper Burrell, Butler Township, Smithfield Township, West Whiteland — and GA/KS/IA counties in the 39–52 day range. Full list on request.)

These are exactly the rows most likely to get quietly extended without the tracker noticing — worth a status check before they flip to "expired" next week.

### Unclassified term (76) and undated fixed term (43)

Not immediately time-critical but a data-quality backlog: 76 rows have no `term` declared at all (could be permanent bans or unresearched pauses — the page can't tell the reader which), and 43 more have a recorded fixed-duration note but no end date to compute against. Heavy NJ Pinelands-area concentration in the unclassified set (one shared source, `pinelandsalliance.org/datacenters`, covering ~20+ townships) — worth one research pass rather than one row at a time.

## Review-queue backlog

**Not promoted or dismissed — read-only counts, no triage performed here.**

| Queue | New (awaiting review) | Total |
|---|---|---|
| `data/moratorium_candidates.json` | 1,765 | 1,973 (167 promoted, 41 dismissed) |
| `data/project_candidates.json` | 83 | 195 (65 promoted, 47 dismissed) |

Of the 1,765 new moratorium candidates, only 533 have a `guess_locality` resolved; `triage_moratorium_candidates.py --tier A` separately finds 172 "cited" candidates (link or named document already in hand) ready to promote fastest.

### Top 10 newest moratorium candidates with a resolved locality (of 533)

| First seen | Locality | Title |
|---|---|---|
| 2026-09-27 | Tuolumne, CA(?) | Tuolumne County To Seek Public Input On Data Center Ordinance |
| 2026-09-27 | Mesa, CO(?) | Mesa County to consider data center moratorium |
| 2026-09-26 | Brighton | Brighton Township latest to adopt data center moratorium |
| 2026-09-26 | Shaker | 'Needs to be protected': Shaker Village CEO urges public to speak out ahead of data center ordinance vote |
| 2026-09-26 | Janesville, WI(?) | Janesville City Council to host hearing on proposed data center moratorium |
| 2026-09-26 | Troy | Troy City Council extends data center moratorium until March 2027 |
| 2026-09-25 | LA | LA County issues temporary ban on data centers in unincorporated areas |
| 2026-09-25 | Fort Wayne, IN(?) | Fort Wayne City Council delays decision on data center moratorium |
| 2026-09-25 | Americus, GA(?) | Americus City Council passes data center moratorium |
| 2026-09-24 | Columbus | Columbus County Considers a Moratorium on Data Centers |

*Guessed states above are the scanner's own inference (unresolved in the raw records), not confirmed — verify against the locality's own .gov source before promoting, per CLAUDE.md.*

### Top project candidates with a resolved locality (of 34, all first-seen 2026-09-21)

| Locality | Title |
|---|---|
| Custer County, MT | MONTANA: Data Center concerns dominate Custer County zoning hearing |
| Colleton County | Colleton County approves new zoning changes to allow data center |
| Stokes County | Data Center Debate: Stokes County Commissioners hold public hearing |
| Effingham County | Effingham County residents sue county over data center zoning ordinance, demand transparency |
| Luzerne County | Luzerne County zoning plan for data centers under legal review |
| Spotsylvania | Spotsylvania Planning Commission recommends approval of 555-acre data center campus |
| Prince William | Prince William Planning Commission recommends ending by-right data centers, downsizing data center district |
| Scott County | Scott County planning commission tables data center ordinance |
| Wood County | Wood County enacts ordinance to ensure notice of data center proposals |

Promotion still requires reading each locality's own .gov source for `source` + `as_of` — nothing above has been promoted or dismissed by this run.
