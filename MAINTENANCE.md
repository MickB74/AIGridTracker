# Weekly data-freshness digest — 2026-11-16

**224 items need a human look this week: 0 hearings scheduled in the next 30 days, 56 expired + 90 expiring-soon + 78 unclassified-term moratorium rows, 2 stale registries, and a review-queue backlog of 2,661 new moratorium candidates / 203 new project candidates.**

## Upcoming hearings (next 30 days)

`PROJECTS_DF` / `project_status()`: **no project has a scheduled hearing in the next 30 days** (or even the next `PROJECT_HEARING_SOON_DAYS` window).

20 projects are instead in **"Awaiting decision"** — hearing already held, no decision recorded yet, so a ruling could land without further public notice. The most recent, most time-critical:

| Project | Locality | Hearing held | Days since |
|---|---|---|---|
| Plaza 500 (Lincolnia) | Lincolnia (Fairfax County), VA | 2026-09-24 | 53d |
| Dickerson Data Center Campus (Atmosphere) | Dickerson (Montgomery County), MD | 2026-09-10 | 67d |
| Prime Data Centers — Starpointe Business Park | Hanover Township (Washington County), PA | 2026-08-31 | 77d |
| La Osa | Pinal County (near Eloy), AZ | 2026-08-26 | 82d |
| Site Layer 4 Data Center Campus | Wheatland (Platte County), WY | 2026-08-26 | 82d |
| Aligned Data Centers — Pataskala industrial park | Pataskala (Licking County), OH | 2026-08-25 | 83d |
| BCG Cedar Creek Campus | Cedar Creek (Bastrop County), TX | 2026-08-24 | 84d |
| Project Flex | Lyon Township (Oakland County), MI | 2026-08-24 | 84d |
| Kearney Data Center | Kearney, NE | 2026-08-21 | 87d |
| Burkhalter Road data center (4AM Development) | Statesboro (Bulloch County), GA | 2026-08-18 | 90d |

(10 more awaiting decision, oldest hearing 2025-08-11 — Wolcott Data Center, White County IN. Full list on request.)

## Stale registries

`registry_provenance()` over `REGISTRY_PROVENANCE`: **2 of 14** registries flagged (no `as_of` recorded — treated as stale regardless of churn tier):

| Registry | as_of | churn | Note |
|---|---|---|---|
| `DC_SITES_DF` | None | medium | No verification date recorded — shelf life is 18mo once dated |
| `STATE_PUCS_DF` | None | low | No verification date recorded — shelf life is 36mo once dated |

Action: set a real `as_of` (or confirm these were never populated) rather than leaving them silently uncaptioned. Both have carried this flag since at least the last digest — worth a look rather than another deferral.

## Moratorium audit (`verify_moratoriums.py --offline`)

887/887 tracker rows carry a `source`; 44/44 quotable claims (case studies, benchmarks, concessions) carry a citation + `as_of`. **Missing-source: 0. Stale `as_of` (>180d): 0.** Link-checking was skipped (`--offline`), so nothing below has been confirmed to still resolve.

| Check | Count |
|---|---|
| expired | 56 |
| expiring (≤60d) | 90 |
| unclassified-term (`term_kind=unknown`) | 78 |
| undated-term (`fixed_undated`, no end date) | 74 |

### Expired — term end date has passed, `effective_status` needs confirming (56)

Newest first (dates are the recorded term end, not a hearing — these are the most recently lapsed and most likely to still be mid-extension-vote):

| Locality | State | Term ended |
|---|---|---|
| Riley County | KS | 2026-11-12 |
| Dickinson County | IA | 2026-11-12 |
| Johnson County | IA | 2026-11-08 |
| Butler Township | PA | 2026-11-08 |
| Lysander (Onondaga Co.) | NY | 2026-11-06 |
| Camden County | GA | 2026-11-06 |
| Charlotte | NC | 2026-11-05 |
| Lavon | TX | 2026-11-05 |
| Upper Burrell Township | PA | 2026-11-02 |
| Smithfield Township | PA | 2026-11-02 |
| West Whiteland Township | PA | 2026-11-01 |
| Lexington (Fayette County) | KY | 2026-10-31 |
| Arcata | CA | 2026-10-31 |
| Richmond | CA | 2026-10-30 |
| Gilroy | CA | 2026-10-29 |

(41 more, oldest the carried-forward Groton, CT row at 2023-06-21 — still unresolved three digests running. Full 56-row list in `scripts/verify_moratoriums.py --offline` output.)

Each needs its source re-read to set `effective_status` (lapsed / extended / rescinded / became permanent zoning) — the audit doesn't guess.

### Expiring soon — within 60 days (90)

Nearest-first, truncated to the next 14 days (19 rows) — the rest are lower urgency but still worth a status check before they flip to "expired":

| Locality | State | Ends | Days left |
|---|---|---|---|
| Springfield | MO | 2026-11-17 | 1 |
| Putnam County | IN | 2026-11-17 | 1 |
| Aberdeen | SD | 2026-11-18 | 2 |
| Meridian Township | MI | 2026-11-19 | 3 |
| Barnes County | ND | 2026-11-19 | 3 |
| Minneapolis | MN | 2026-11-21 | 5 |
| Iron County | UT | 2026-11-22 | 6 |
| Washington Township (Macomb Co.) | MI | 2026-11-23 | 7 |
| Marshalltown | IA | 2026-11-23 | 7 |
| Hillsboro | OR | 2026-11-24 | 8 |
| Bloomington | IL | 2026-11-26 | 10 |
| Hart | MI | 2026-11-26 | 10 |
| Westbrook | ME | 2026-11-28 | 12 |
| Gorham | ME | 2026-11-29 | 13 |
| Forest Park | GA | 2026-11-29 | 13 |
| Brunswick | ME | 2026-11-29 | 13 |
| Normal | IL | 2026-11-30 | 14 |
| El Dorado | KS | 2026-11-30 | 14 |
| Scarborough | ME | 2026-11-30 | 14 |

(23 more land 15–30 days out, 48 more at 31–60 days — including a heavy Michigan/Ohio/Georgia/Oklahoma cluster of near-identical 6-month pauses enacted in the same June–July window. Full list on request.)

### Unclassified term (78) and undated fixed term (74)

Not immediately time-critical but a growing data-quality backlog: 78 rows have no `term` declared at all (could be permanent bans or unresearched pauses — the page can't tell the reader which), and 74 more have a recorded fixed-duration note but no end date to compute against. Both counts rose since the last digest (76→78, 43→74) — the undated-term jump in particular suggests a batch of recent adds went in without an end date.

## Review-queue backlog

**Not promoted or dismissed — read-only counts, no triage performed here.**

| Queue | New (awaiting review) | Total |
|---|---|---|
| `data/moratorium_candidates.json` | 2,661 | 2,961 (249 promoted, 51 dismissed) |
| `data/project_candidates.json` | 203 | 315 (65 promoted, 47 dismissed) |

Of the 2,661 new moratorium candidates, only 713 have a `guess_locality` resolved; `triage_moratorium_candidates.py --tier A` separately finds 304 "cited" candidates (link or named document already in hand) ready to promote fastest — up sharply from 172 last digest, so this queue is growing faster than it's being worked.

### Top 10 newest moratorium candidates with a resolved locality (of 713)

| First seen | Locality | Title |
|---|---|---|
| 2026-11-15 | New Bedford, ? | New Bedford City Council passes ban on data centers |
| 2026-11-15 | Wynne, ? | Wynne City Council approves one-year moratorium on new data centers |
| 2026-11-15 | Luzerne County, ? | Backup generator use clarified in Luzerne County's proposed data center zoning ordinance |
| 2026-11-14 | Delano, ? | Delano City Council to consider temporary ban on data centers |
| 2026-11-14 | Double Before, MD | Maryland data center seeks to double before county pause (expires) — guessed locality looks wrong, verify |
| 2026-11-14 | Vineland, ? | Vineland data center reveals why we need a moratorium now |
| 2026-11-14 | Dalton, ? | Dalton City Council to consider moratorium on data centers Monday |
| 2026-11-13 | Evanston (guessed as "City"), ? | City council to consider Evanston data center moratorium |
| 2026-11-12 | — | (remaining rows: see full queue) |

*Guessed localities/states above are the scanner's own inference, not confirmed — verify against the locality's own .gov source before promoting, per CLAUDE.md. Several of this week's top hits show the scanner's known failure mode (generic words like "City"/"Town" or a mis-split title) — a reminder that `guess_locality` resolution rate overstates how many are actually ready.*

### Top project candidates with a resolved locality (of 75)

| First seen | Locality | Title |
|---|---|---|
| 2026-11-09 | Hutchinson, ? | Hutchinson Planning Commission to consider permanent data center regulations Tuesday |
| 2026-11-09 | Butler County, ? | Butler County zoning board approves data center regulations |
| 2026-11-09 | Van Buren Township, ? | Google data center site plan up for approval by Van Buren Township Planning Commission |
| 2026-11-02 | Hubbard Township, ? | Hearing tonight on Hubbard Township data center zoning |
| 2026-11-02 | Davidson County, ? | Davidson County commissioners approve new zoning rules for data centers |
| 2026-11-02 | Jefferson County, ? | Jefferson County approves new zoning ordinance that includes data centers |
| 2026-11-02 | Franklin County, ? | Franklin County residents urge planning commission to address data center concerns |
| 2026-11-02 | Sioux County, ? | Sioux County's proposed data center rules go to final reading |
| 2026-10-26 | St. Joseph, ? | St. Joseph City Council to consider rezoning properties, data center ordinances |

Promotion still requires reading each locality's own .gov source for `source` + `as_of` — nothing above has been promoted or dismissed by this run.
