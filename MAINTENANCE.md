# Weekly data-freshness digest — 2026-11-02

**33 moratoriums expire within 30 days, 46 are already past their end date, 20 projects have been awaiting a decision for 39–448 days, and 2,369 moratorium leads + 173 project leads are sitting unreviewed.** No stale `as_of` or missing-source rows this week — the tracker's citation discipline is holding.

## Upcoming hearings (next 30 days)

- **No scheduled public hearings** on `PROJECTS_DF` fall in the next 30 days (phase `hearing`, `days_to_hearing` 0–30 → 0 rows).
- **20 projects are stuck in "Awaiting decision"** — hearing already happened, no `decided_date`/`outcome` recorded. These need a status check this week, oldest first:
  - White County, IN — Wolcott Data Center — heard 2025-08-11 (**448d** ago)
  - Lansing (Tompkins Co.), NY — TeraWulf Cayuga — heard 2026-04-27 (189d ago)
  - Cave City, KY — Cave City data center — heard 2026-07-20 (105d ago)
  - Rural Hall, NC — Project Iron Spur — heard 2026-07-30 (95d ago)
  - Alabama, NY (Genesee Co.) — Project Double Reed — heard 2026-08-03 (91d ago)
  - Posey County, IN — Boberg/Hoenert Roads — heard 2026-08-04 (90d ago)
  - North Beaver & Mahoning twps, PA — Powder Mill Works — heard 2026-08-05 (89d ago)
  - Smithfield Township, PA — Smithfield Gateway — heard 2026-08-12 (82d ago)
  - Plymouth Township, PA — 900 Conshohocken Rd — heard 2026-08-17 (77d ago)
  - Pahrump, NV — Manse Technology Campus — heard 2026-08-18 (76d ago)
  - Statesboro, GA — Burkhalter Road — heard 2026-08-18 (76d ago)
  - Kearney, NE — Kearney Data Center — heard 2026-08-21 (73d ago)
  - Lyon Township, MI — Project Flex — heard 2026-08-24 (70d ago)
  - Cedar Creek, TX — BCG Cedar Creek Campus — heard 2026-08-24 (70d ago)
  - Pataskala, OH — Aligned DC industrial park — heard 2026-08-25 (69d ago)
  - Pinal County, AZ — La Osa — heard 2026-08-26 (68d ago)
  - Wheatland, WY — Site Layer 4 Campus — heard 2026-08-26 (68d ago)
  - Hanover Township, PA — Prime DC / Starpointe — heard 2026-08-31 (63d ago)
  - Dickerson, MD — Atmosphere Data Center Campus — heard 2026-09-10 (53d ago)
  - Lincolnia (Fairfax Co.), VA — Plaza 500 — heard 2026-09-24 (39d ago)

## Stale registries

`REGISTRY_PROVENANCE` flags **2 of 14** tracked registries — both for a missing `as_of`, not a churn-shelf-life expiry:

| Registry | as_of | churn |
|---|---|---|
| `DC_SITES_DF` | None | medium |
| `STATE_PUCS_DF` | None | low |

No `as_of` ever recorded on either → both render as stale by default. Needs someone to set a real verification date (never fabricate one).

## Moratorium audit (expiring / expired / missing-source)

`scripts/verify_moratoriums.py --offline`: 887/887 tracker rows sourced, 44/44 quotable case-study/benchmark/concession claims cited. **0 missing-source, 0 stale-as-of (>180d)** — clean on both this week.

**Expired — 46 rows**, oldest first by lapse date (confirm lapsed vs. extended vs. made permanent):
Groton CT (2023-06-21) · Madison County NC (2024-06-13) · Mason MI (2026-02-03) · Aurora IL (2026-03-24) · Montebello CA (2026-03-28) · Montour County PA (2026-04-30) · Jerome Township OH (2026-06-01) · Lenox Township MI (2026-06-02) · Waterville OH (2026-06-08) · Brevard NC (2026-07-02) · Griffin GA (2026-07-12) · Lodi Township MI (2026-08-02) · Kingsland GA (2026-08-09) · Leavenworth County KS (2026-08-11) · Saugatuck Township MI (2026-08-11) · York Township MI (2026-08-12) · Massillon OH (2026-08-14) · Wixom MI (2026-08-26) · Floyd County GA (2026-08-28) · Lyon Charter Township MI (2026-08-30) · Mount Orab OH (2026-08-30) · Covington GA (2026-08-31) · Hogansville GA (2026-09-01) · Birmingham AL (2026-09-03) · Wichita KS (2026-09-10) · Augusta GA (2026-09-15) · Roswell GA (2026-09-20) · Waterford Township MI (2026-10-01) · Rockdale County GA (2026-10-09) · Calaveras County CA (2026-10-09) · Morgan Hill CA (2026-10-10) · Escondido CA (2026-10-12) · Indio CA (2026-10-16) · Cleveland OH (2026-10-16) · Vienna Township OH (2026-10-16) · Eureka CA (2026-10-17) · Caledonia Township MI (2026-10-17) · Plainfield IL (2026-10-18) · White County IN (2026-10-20) · Lowndes County AL (2026-10-25) · Lowndes County GA (2026-10-25) · Gilroy CA (2026-10-29) · Richmond CA (2026-10-30) · Arcata CA (2026-10-31) · Lexington (Fayette Co.) KY (2026-10-31) · West Whiteland Township PA (2026-11-01)

**Expiring within 30 days — 33 rows** (need a "did it lapse or extend" check before they go stale):
Smithfield Township PA & Upper Burrell Township PA — today (0d) · Charlotte NC & Lavon TX — 11/05 (3d) · Camden County GA & Lysander NY — 11/06 (4d) · Butler Township PA & Johnson County IA — 11/08 (6d) · Dickinson County IA & Riley County KS — 11/12 (10d) · Putnam County IN & Springfield MO — 11/17 (15d) · Aberdeen SD — 11/18 (16d) · Barnes County ND & Meridian Township MI — 11/19 (17d) · Minneapolis MN — 11/21 (19d) · Iron County UT — 11/22 (20d) · Marshalltown IA & Washington Township MI — 11/23 (21d) · Hillsboro OR — 11/24 (22d) · Bloomington IL & Hart MI — 11/26 (24d) · Westbrook ME — 11/28 (26d) · Brunswick ME, Forest Park GA, Gorham ME — 11/29 (27d) · El Dorado KS, Normal IL, Scarborough ME — 11/30 (28d) · Nashville TN, Skagit County WA — 12/01 (29d) · Boulder County CO, Braceville Township OH — 12/02 (30d)

- **Expiring 31–60 days: 52 more rows** (lower urgency, full list in the worklist file below).
- **Undated/unclassified term rows (154 total: 74 undated-term + 78 unclassified-term, 2 overlap categories)**: not expiry-urgent but a standing data-quality backlog — each needs its adoption/end date or a `term` classification read off the source.
- Full detail (all 301 findings) saved to `/tmp/claude-0/-home-user-AIGridTracker/e38ff0c7-a64a-5dfe-8807-4d1a20f4df6a/scratchpad/moratorium_audit.json` this run (not committed — regenerate with `python3 scripts/verify_moratoriums.py --offline --json <path>`).

## Review-queue backlog (counts + top items to promote this week)

**Moratorium candidates** (`data/moratorium_candidates.json`, updated 2026-11-01): 2,369 new / 2,669 total (249 promoted, 51 dismissed). Newest unreviewed leads:
1. Prince William, VA(?) — "residents call for 12-month pause on data center approvals"
2. Amherst, ? — "begins discussion on data center ban or regulations"
3. Newark area, ? — "Early Voting + Data Center Ban + Picket Lines"
4. Essex County, NJ(?) — "Data Center Ban in Belleville..."
5. San Diego, CA — "City Council passes a temporary moratorium on data centers"
6. Unlocated — "Readers split over city plan for data center moratorium"
7. Unlocated — "SK Council moves ahead with restrictions on potential data centers"
8. Aiken, SC(?) — "Where do Aiken County governing bodies stand on restrictions?"
9. Unlocated — "Data Center Bans Won't Stop AI..."
10. Dade City, FL(?) — "Ordinance for Data Center Moratorium Moves Forward"

**Project candidates** (`data/project_candidates.json`, updated 2026-10-26): 173 new / 285 total (65 promoted, 47 dismissed). Newest unreviewed leads:
1. St. Joseph, ? — "City Council to consider rezoning properties, data center ordinances"
2. Spokane County, WA — "Data Center Zoning Public Meeting"
3. Luzerne County, PA(?) — "Council set to discuss data center zoning ordinance"
4. Unlocated — "Public hearing set for data center-related zoning ordinance proposal"
5. Unlocated — "Planning Commission's hearing on zoning rewrite"
6. King of Prussia, PA(?) — "developers withdraw applications ... amid lawsuits over zoning dispute"
7. Lexington-Fayette (LFUCC), KY — "passes 2 ordinances regulating zoning and language surrounding data centers"
8. Fauquier County, VA — "restricts future data center development with new zoning rules"
9. Talbot County, MD — "Judge Voids Talbot County Data Center Zoning Rule Over Skipped Hearings"
10. Lawrence, ? — "City Commission approves extra layers of oversight for data centers"

Reminder: promotion requires reading each locality's own ordinance/agenda and adding a sourced row by hand — this digest only ranks the queue, per CLAUDE.md.
