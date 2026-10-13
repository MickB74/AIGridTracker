# Weekly data-freshness digest — 2026-10-12 (UTC)

**Headline:** 54 moratoriums expiring within 30 days, 33 already past their documented end date, 2 bulk registries flagged stale, 1,963 unreviewed moratorium leads + 112 unreviewed project leads in the queues, 0 projects with a *future* hearing date on record.

This is a summary only — no registry rows or candidate statuses were changed. Promotion/dismissal and `as_of` edits remain a human step, per CLAUDE.md.

## Upcoming hearings (next 30 days)

**None found.** `PROJECTS_DF` has no row with a `hearing_date` in the future — the most recent recorded `hearing_date` is **2026-09-24** (Plaza 500 / Lincolnia, Fairfax County, VA), already 18 days past. This likely means the tracker's hearing dates aren't being kept current rather than that nothing is actually scheduled — worth a scan of `data/project_candidates.json` and local agendas for dates to add.

Related and time-critical even without a future `hearing_date`: **20 projects are `Awaiting decision`** — a hearing already happened and the vote is still pending, with no `decided_date` recorded. Most recently heard, in order (most urgent to watch for a vote first):
- Plaza 500 (Lincolnia), Fairfax County, VA — heard 2026-09-24
- Dickerson Data Center Campus (Atmosphere), Montgomery County, MD — heard 2026-09-10
- Prime Data Centers — Starpointe Business Park, Washington County, PA — heard 2026-08-31
- La Osa, Pinal County, AZ — heard 2026-08-26
- Site Layer 4 Data Center Campus, Platte County, WY — heard 2026-08-26

(15 more awaiting decision, heard 2026-02-12 through 2026-08-25 — see `PROJECTS_DF` rows with `stage == "Awaiting decision"`.)

## Stale registries

`REGISTRY_PROVENANCE` flags 2 of 14 registries as stale (no `as_of` recorded at all — not just past shelf life):

| Registry | as_of | churn | Issue |
|---|---|---|---|
| `DC_SITES_DF` | *(none)* | medium | Campus/operator/tenant/LLC registry — "No verification date recorded." Shelf life for medium-churn is 18mo, so this has been unverifiable the whole time it's been flagged. |
| `STATE_PUCS_DF` | *(none)* | low | PUC directory — "No verification date recorded." Low churn (36mo shelf life) means this is lower urgency, but still needs one read-through to set a real date. |

All other 12 registries (`STATE_DC_DF`, `STATE_GRID_PROFILES`, `HOUSE_RACES_2026`, `SENATORS`, `SENATE_RACES_2026`, `MORATORIUMS_DF`, `MEGA_PROJECTS_DF`, `PROJECTS_DF`, `EXECUTIVES_DF`, `STATE_STUDIES`, `STATE_PERMIT_PORTALS`, `DC_CLEAN_ENERGY_LAWS_DF`) have a recorded `as_of` and are within their churn-based shelf life.

## Moratorium audit (`scripts/verify_moratoriums.py --offline`)

871/871 tracker rows sourced; 44/44 quotable claims (case studies, benchmarks, concessions) carry a citation. **0 missing-source and 0 stale-as-of findings** — sourcing discipline is holding. Link-checking was skipped (`--offline`), so nothing below has been confirmed to still resolve.

| Check | Count |
|---|---|
| expired | 33 |
| expiring (≤30d) | 54 |
| undated-term | 63 |
| unclassified-term | 76 |

### Expiring soon (next 30 days) — 54 total, 20 most urgent

| Locality | State | Ends | Days left |
|---|---|---|---|
| Escondido | CA | 2026-10-12 | 0 |
| Vienna Township (Trumbull Co.) | OH | 2026-10-16 | 4 |
| Cleveland | OH | 2026-10-16 | 4 |
| Indio | CA | 2026-10-16 | 4 |
| Mendocino County | CA | 2026-10-16 | 4 |
| Eureka | CA | 2026-10-17 | 5 |
| Plainfield | IL | 2026-10-18 | 6 |
| White County | IN | 2026-10-20 | 8 |
| Lowndes County | GA | 2026-10-25 | 13 |
| Lowndes County | AL | 2026-10-25 | 13 |
| Gilroy | CA | 2026-10-29 | 17 |
| Richmond | CA | 2026-10-30 | 18 |
| Lexington (Fayette County) | KY | 2026-10-31 | 19 |
| West Whiteland Township | PA | 2026-11-01 | 20 |
| Upper Burrell Township | PA | 2026-11-02 | 21 |
| Smithfield Township | PA | 2026-11-02 | 21 |
| Charlotte | NC | 2026-11-05 | 24 |
| Lavon | TX | 2026-11-05 | 24 |
| Lysander (Onondaga Co.) | NY | 2026-11-06 | 25 |
| Camden County | GA | 2026-11-06 | 25 |

(34 more expiring by 2026-12-10 — full list in `verify_moratoriums.py --offline` output.)

### Already past their end date — 33 total, 15 most overdue

| Locality | State | Term ran to |
|---|---|---|
| Morgan Hill | CA | 2026-10-10 |
| Calaveras County | CA | 2026-10-09 |
| Rockdale County | GA | 2026-10-09 |
| Waterford Township | MI | 2026-10-01 |
| Roswell | GA | 2026-09-20 |
| Augusta | GA | 2026-09-15 |
| Augusta-Richmond County | GA | 2026-09-15 |
| Wichita | KS | 2026-09-10 |
| Birmingham | AL | 2026-09-03 |
| Hogansville | GA | 2026-09-01 |
| Covington | GA | 2026-08-31 |
| Mount Orab | OH | 2026-08-30 |
| Lyon Charter Township | MI | 2026-08-30 |
| Floyd County | GA | 2026-08-28 |
| Wixom | MI | 2026-08-26 |

(18 more, oldest back to Groton, CT — lapsed 2023-06-21 — need a human check: lapsed, extended, or converted to permanent zoning?)

**undated-term (63)** and **unclassified-term (76)** rows need research, not urgency — these are rows where the tracker cannot derive an expiry because no end date or `term` kind was ever recorded (see `src/constants.py` moratorium docs). Not reproduced in full here; see the full worklist from `scripts/verify_moratoriums.py --offline --out <file>`.

## Review-queue backlog

| Queue | New (awaiting review) | Promoted | Dismissed | Total |
|---|---|---|---|---|
| `data/moratorium_candidates.json` | 1,963 | 249 | 45 | 2,257 |
| `data/project_candidates.json` | 112 | 65 | 47 | 224 |

### Top items to triage this week — moratorium candidates (newest first)

Most of this week's intake has no resolved locality/state (the RSS-title guesser couldn't place them) — those need a human read of the article before they're even promotable:

- 2026-10-11 — *City data center moratorium gets public hearing date* (locality unresolved)
- 2026-10-11 — *What Comes After a Data Center Moratorium?* (locality unresolved)
- 2026-10-11 — *Oakland puts temporary pause on new data centers* (locality unresolved — likely Oakland, CA)
- 2026-10-11 — *Data center moratorium on Venice Council's agenda* (locality unresolved — likely Venice, FL or CA)
- 2026-10-11 — *SF approves 45-day data center moratorium* (locality unresolved — likely San Francisco, CA)
- 2026-10-11 — *Citizen coalition calls on Sioux Falls to enact temporary data center moratorium before final permitting of Gemini Project* (locality unresolved — likely Sioux Falls, SD)
- 2026-10-11 — *Nevada city council to discuss moratorium on data centers and cryptocurrency projects* (state: NV)
- 2026-10-11 — *Manatee Commissioners put AI data centers on ice with 12-month moratorium* (locality unresolved — likely Manatee County, FL)
- 2026-10-11 — *Box Elder and Iron have been busy as county data center pauses start to run out* (locality unresolved — likely Box Elder/Iron County, UT — note: Box Elder Co, UT is already tracked and shows up in "expiring soon" above)
- 2026-10-11 — *12-Month Data Center Moratorium Approved By Manatee Commissioners* (duplicate coverage of the Manatee item above)

### Top items to triage this week — project candidates (newest first)

- 2026-10-05 — *WI Rapids to hold 3 public hearings on data centers at Oct. 5 meeting* (state: WI)
- 2026-10-05 — *Bethlehem data center would fail proposed zoning rules, but project is exempt* (locality unresolved)
- 2026-10-05 — *Fremont County Commission to discuss data center zoning, regulation during regular meeting Tuesday* (locality: Fremont)
- 2026-10-05 — *Corunna City Council approves data center ordinance* (locality: Corunna)
- 2026-10-05 — *Shreveport City Council's Amazon data center approval questioned in court* (locality: Shreveport)
- 2026-10-05 — *County continues work on data center zoning, hosts open houses* (locality unresolved)
- 2026-10-05 — *Luzerne County's proposed data center zoning ordinance amendment up for discussion Thursday* (locality: Luzerne)
- 2026-10-05 — *Bitcoin Data Center Proposed In Jersey County, No Progress Reported* (locality guess "Proposed In Jersey" is a parsing artifact — actually Jersey County, likely IL)
- 2026-10-05 — *Rally targets proposed Mahomet data center ahead of Oct. 13 village meeting* (locality unresolved — likely Mahomet, IL — **note: Oct. 13 meeting is tomorrow relative to this digest's date**)
- 2026-10-05 — *£16.5BN Data Centre Campus Proposed in Dumfries and Galloway* (out of scope — UK, not a US jurisdiction this tracker covers)

**Flag for a human:** the Mahomet, IL rally item names an Oct. 13 village meeting — one day after this digest — and is still sitting in `new` status. Worth a priority read before the meeting happens.
