# GridWatch AI — weekly data-freshness digest

_Generated 2026-10-26 (UTC) · read-only audit, no registries edited, no candidates promoted or dismissed_

**41 moratoriums expired · 25 more expire within 30 days (67 within 60) · 0 project hearings scheduled in the next 30 days (20 projects stuck in "awaiting decision" with no date) · 2 registries flagged stale (no `as_of`) · 2,249 moratorium + 153 project candidates still in the review queue (221 moratorium candidates are cited and ready to promote).**

## Upcoming hearings (next 30 days)

`PROJECTS_DF` / `project_status()`: **0** projects have a hearing scheduled with `days_to_hearing` between 0 and 30. (The 20 most recent hearing dates in the data have all already passed — see below.)

- **20 projects are in "Awaiting decision"** (`phase == "awaiting"`): a hearing happened but no `decided_date` is recorded, so the page can't tell a resident when a vote is coming. Most recent hearings with no decision yet: Plaza 500 / Lincolnia, VA (2026-09-24), Dickerson Data Center Campus / Dickerson, MD (2026-09-10), Prime Data Centers — Starpointe / Hanover Twp., PA (2026-08-31), La Osa / Pinal County, AZ (2026-08-26), Site Layer 4 / Wheatland, WY (2026-08-26). Worth a round of "call the clerk for the vote date" follow-ups rather than a data problem per se.

## Stale registries

`REGISTRY_PROVENANCE` / `registry_provenance()`: **2 of 14** tracked registries are flagged stale, both because `as_of` is `None` (never recorded a verification date — not a shelf-life expiry):

| Registry | as_of | churn | Status |
|---|---|---|---|
| `DC_SITES_DF` | — (none recorded) | medium (18mo shelf life) | No verification date recorded |
| `STATE_PUCS_DF` | — (none recorded) | low (36mo shelf life) | No verification date recorded |

Everything else in `REGISTRY_PROVENANCE` is within its churn-based shelf life.

## Moratorium audit (expiring / expired / missing-source)

`scripts/verify_moratoriums.py --offline` against **887** tracked rows:

| Finding | Count |
|---|---|
| expired | 41 |
| expiring soon (≤60d) | 67 |
| missing-source | 0 |
| as_of stale (>180d) | 0 |
| undated-term (fixed term, no end date) | 74 |
| unclassified-term (no `term` declared) | 78 |
| dead-link / blocked | not checked — ran `--offline`, no network |

Sourcing hygiene is in good shape (0 missing-source, 0 stale-as-of). The backlog is almost entirely **time-critical status**, not citations: 108 rows (41 expired + 67 expiring) need a human to check whether the ban lapsed, was extended, or went permanent, plus 152 rows (`undated-term` + `unclassified-term`) where no `term` was ever declared.

### Expired — confirm lapsed / extended / permanent (41, oldest overdue first)

| Locality | State | Term ran to | Days overdue |
|---|---|---|---|
| Groton | CT | 2023-06-21 | 1223 |
| Madison County | NC | 2024-06-13 | 865 |
| Mason | MI | 2026-02-03 | 265 |
| Aurora | IL | 2026-03-24 | 216 |
| Montebello | CA | 2026-03-28 | 212 |
| Montour County | PA | 2026-04-30 | 179 |
| Jerome Township | OH | 2026-06-01 | 147 |
| Lenox Township | MI | 2026-06-02 | 146 |
| Waterville | OH | 2026-06-08 | 140 |
| Brevard | NC | 2026-07-02 | 116 |
| Griffin | GA | 2026-07-12 | 106 |
| Lodi Township | MI | 2026-08-02 | 85 |
| Kingsland | GA | 2026-08-09 | 78 |
| Saugatuck Township | MI | 2026-08-11 | 76 |
| Leavenworth County | KS | 2026-08-11 | 76 |
| York Township | MI | 2026-08-12 | 75 |
| Massillon | OH | 2026-08-14 | 73 |
| Wixom | MI | 2026-08-26 | 61 |
| Floyd County | GA | 2026-08-28 | 59 |
| Mount Orab | OH | 2026-08-30 | 57 |
| Lyon Charter Township | MI | 2026-08-30 | 57 |
| Covington | GA | 2026-08-31 | 56 |
| Hogansville | GA | 2026-09-01 | 55 |
| Birmingham | AL | 2026-09-03 | 53 |
| Wichita | KS | 2026-09-10 | 46 |
| Augusta | GA | 2026-09-15 | 41 |
| Roswell | GA | 2026-09-20 | 36 |
| Waterford Township | MI | 2026-10-01 | 25 |
| Calaveras County | CA | 2026-10-09 | 17 |
| Rockdale County | GA | 2026-10-09 | 17 |
| Morgan Hill | CA | 2026-10-10 | 16 |
| Escondido | CA | 2026-10-12 | 14 |
| Vienna Township (Trumbull Co.) | OH | 2026-10-16 | 10 |
| Cleveland | OH | 2026-10-16 | 10 |
| Indio | CA | 2026-10-16 | 10 |
| Caledonia Township | MI | 2026-10-17 | 9 |
| Eureka | CA | 2026-10-17 | 9 |
| Plainfield | IL | 2026-10-18 | 8 |
| White County | IN | 2026-10-20 | 6 |
| Lowndes County | GA | 2026-10-25 | 1 |
| Lowndes County | AL | 2026-10-25 | 1 |

### Expiring within 30 days — watch for extension (25 of 67 total; the rest expire 31–60 days out)

| Locality | State | Ends | Days left |
|---|---|---|---|
| Gilroy | CA | 2026-10-29 | 3 |
| Richmond | CA | 2026-10-30 | 4 |
| Lexington (Fayette County) | KY | 2026-10-31 | 5 |
| Arcata | CA | 2026-10-31 | 5 |
| West Whiteland Township | PA | 2026-11-01 | 6 |
| Upper Burrell Township | PA | 2026-11-02 | 7 |
| Smithfield Township | PA | 2026-11-02 | 7 |
| Charlotte | NC | 2026-11-05 | 10 |
| Lavon | TX | 2026-11-05 | 10 |
| Lysander (Onondaga Co.) | NY | 2026-11-06 | 11 |
| Camden County | GA | 2026-11-06 | 11 |
| Johnson County | IA | 2026-11-08 | 13 |
| Butler Township | PA | 2026-11-08 | 13 |
| Riley County | KS | 2026-11-12 | 17 |
| Dickinson County | IA | 2026-11-12 | 17 |
| Springfield | MO | 2026-11-17 | 22 |
| Putnam County | IN | 2026-11-17 | 22 |
| Aberdeen | SD | 2026-11-18 | 23 |
| Meridian Township | MI | 2026-11-19 | 24 |
| Barnes County | ND | 2026-11-19 | 24 |
| Minneapolis | MN | 2026-11-21 | 26 |
| Iron County | UT | 2026-11-22 | 27 |
| Washington Township (Macomb Co.) | MI | 2026-11-23 | 28 |
| Marshalltown | IA | 2026-11-23 | 28 |
| Hillsboro | OR | 2026-11-24 | 29 |

*(42 more expire between 31 and 60 days out — Bloomington IL through Sedgwick County KS — full list in `verify_moratoriums.py --offline` output; omitted here to keep this digest to the truly imminent items.)*

## Review-queue backlog (counts + top items to promote this week)

**Reminder: promotion requires a human reading the locality's own `.gov` source — this digest only ranks the queue, it does not promote or dismiss anything.**

### Moratorium candidates (`data/moratorium_candidates.json`, updated 2026-10-25)

- **2,249 of 2,549** total candidates are still `status: new` (awaiting review); 249 already promoted, 51 dismissed.
- `scripts/triage_moratorium_candidates.py --tier A` found **221 Tier-A (cited)** candidates — a publisher link or named document already in hand, just needs the ordinance located and a `LOCAL_BODIES_DF`/`MORATORIUMS_DF` row written. Tier breakdown: A (cited) 221, B (structured, source TBD) 1, C (thin/undated) 91, D (unlocated headline) 1,242.
- **Top Tier-A picks to promote this week** (ranked by corroborating-outlet count; the scanner left state unresolved — `guess_state` is `None` — on nearly all of these, so a human still has to identify the jurisdiction before searching for the .gov source):
  1. "Eugene" — 6 outlets — "Residents urge Eugene City Council to consider data center moratorium amid AI growth"
  2. "Hudson" — 3 outlets — "Scenic Hudson president praises Gov. Hochul's moratorium on data centers" (NY context implied by "Gov. Hochul," not confirmed by the scanner)
  3. "Pitt" — 3 outlets — "Pitt County to hold public hearing on data center moratorium"
  4. "Butler. Twp." — 2 outlets — "Butler Twp. supervisors to consider data center ordinance on Oct. 13"
  5. "Florence" — 2 outlets — "Florence County Board approves data center moratorium, ends Flock camera use"
  6. "Hackettstown" — 2 outlets — "Hackettstown Town Council Votes 4-0 to Ban Data Centers Across Town" (a separate newer item in the same queue explicitly titles this "Hackettstown NJ")
  7. "Mahaska" — 2 outlets — "Mahaska County works on data center ordinance"
  8. "LA" — 2 outlets — "Supervisors considering AI data center ban for unincorporated LA County"
  9. "Hudson" — 2 outlets — "Hudson Valley residents dissatisfied with data center moratorium"
  10. "City" — 2 outlets — "City council to vote on data center moratorium" — locality string is literally "City"; needs manual ID before it's workable
- **Newest raw `new` items** (first_seen 2026-10-25, unranked, straight off the scan): "Hackettstown NJ Bans Data Centers Townwide" (locality unresolved by the scanner but `guess_state: NJ` from the headline text itself), "Parsippany Council Rejects Buffer Reduction, Advances Data Center Restrictions..." (locality/state both unresolved), "Upper Burrell supervisors pass data center ordinance" (`guess_locality: Upper Burrell`, state unresolved), "Wheeling City Council considers data center ordinance" (`guess_locality: Wheeling`, state unresolved), "Irondale moves toward new data center restrictions..." (locality/state unresolved), "New Braunfels eyes ordinance changes to curb data centers" (locality/state unresolved).

### Project candidates (`data/project_candidates.json`, updated 2026-10-19)

- **153 of 265** total candidates are still `status: new`; 65 promoted, 47 dismissed.
- Newest 10 `new` items (all from 2026-10-19, most still missing a located state):
  1. St. Cloud, ? — "St. Cloud City Council to Set Public Hearing on Data Center Zoning Rules"
  2. ?, ? — "Cincinnati officials holding public meeting about data center zoning study"
  3. ?, ? — "East Lyme Planners Oppose Black Point Road Rezoning... Review Data Center Rules"
  4. Tehama, ? — "Tehama Planning Commission recommends data center rezoning, more oversight"
  5. ?, ? — "383-acre data center campus proposed off Mike Padgett Highway"
  6. ?, ? — "City Commission approves data center zoning measures, water policies... one person arrested"
  7. ?, ? — "Council moves to extend Lexington's pause on data center development, restart zoning process"
  8. ?, ? — "Penalties in Bloomington's draft data center regulations follow current city zoning rules"
  9. Jersey County, ? — "Jersey County Board Hears Opposition To Data Centers, Debate Over Zoning"
  10. Lake County, ? — "Lake County pivots to reconsider new data center permits and regulations"
- This feed hasn't refreshed since 2026-10-19 (a week before this digest) — worth checking whether the scanner is still running on schedule.

---
_Audit trail: `scripts/verify_moratoriums.py --offline`, a `registry_provenance()` sweep over `REGISTRY_PROVENANCE`, `scripts/triage_moratorium_candidates.py --tier A`, and `PROJECTS_DF`/`project_status()` from `src.constants`. No file under `web/` or any registry was modified; `build_site.py` was not run._
