# GridWatch AI — weekly data-freshness digest
_2026-11-09 UTC_

**54 moratorium rows read past their term with no reconfirmation, 83 more lapse within ~60 days, 2 registries have no verification date on record, and the review queues hold 2,727 unreviewed leads (277 of them cheap to promote this week). No project has a hearing or decision scheduled in the next 30 days.**

## Upcoming hearings (next 30 days)

None. `PROJECTS_DF` (288 rows) has zero rows with `days_to_hearing` in `[0, 30]` — every `hearing_date` on file is already in the past.

- Secondary watch item: 20 projects sit in stage `Awaiting decision` — their hearing already happened and the outcome is still unset (`outcome=None`). None of these are "upcoming," but they're the likeliest candidates to need an `outcome`/`decided_date` update soon. Oldest-hearing-first isn't tracked here; worth a pass with `scripts/fetch_pa_dep_projects.py`-style primary-source checks or manual promotion from `data/project_candidates.json`.

## Stale registries

`REGISTRY_PROVENANCE` flags 2 of 15 registries as stale (no `as_of` on record, so they can't even be scored against their churn shelf-life):

| Registry | as_of | churn | Note |
|---|---|---|---|
| `DC_SITES_DF` | None | medium | Campus registry (operator/tenant/filing LLC) — attribution level varies per row, but the registry itself has never been timestamped. |
| `STATE_PUCS_DF` | None | low | PUC directory — low churn, but still no recorded verification date. |

Everything else (`STATE_DC_DF`, `STATE_GRID_PROFILES`, `MORATORIUMS_DF`, `PROJECTS_DF`, `EXECUTIVES_DF`, `HOUSE_RACES_2026`, `SENATE_RACES_2026`, `SENATORS`, `MEGA_PROJECTS_DF`, `STATE_STUDIES`, `STATE_PERMIT_PORTALS`, `DC_CLEAN_ENERGY_LAWS_DF`) is within its churn-based shelf life (`stale: False`).

## Moratorium audit (`scripts/verify_moratoriums.py --offline`)

Offline run (no link checks) — 289 findings, missing-source: **0**.

| Finding | Count |
|---|---|
| expired | 54 |
| expiring (within window) | 83 |
| undated-term (time-limited, no end date recorded) | 74 |
| unclassified-term (no `term` declared at all) | 78 |
| missing-source | 0 |

Link-check categories (dead-link / blocked / stale-as-of) were **not** run — `--offline` skips network calls by design. Run the full (online) pass separately if link rot is a live concern.

**Most recently expired (top 15 of 54)** — term end date has passed; status not yet reconfirmed as lapsed/extended/permanent:

| Locality | State | Term ran to |
|---|---|---|
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
| Lowndes County | GA | 2026-10-25 |
| Lowndes County | AL | 2026-10-25 |

**Soonest expiring (top 15 of 83)** — still "Enacted," term lapses soon unless extended:

| Locality | State | Ends | Days left |
|---|---|---|---|
| Riley County | KS | 2026-11-12 | 3 |
| Dickinson County | IA | 2026-11-12 | 3 |
| Springfield | MO | 2026-11-17 | 8 |
| Putnam County | IN | 2026-11-17 | 8 |
| Aberdeen | SD | 2026-11-18 | 9 |
| Meridian Township | MI | 2026-11-19 | 10 |
| Barnes County | ND | 2026-11-19 | 10 |
| Minneapolis | MN | 2026-11-21 | 12 |
| Iron County | UT | 2026-11-22 | 13 |
| Washington Township (Macomb Co.) | MI | 2026-11-23 | 14 |
| Marshalltown | IA | 2026-11-23 | 14 |
| Hillsboro | OR | 2026-11-24 | 15 |
| Bloomington | IL | 2026-11-26 | 17 |
| Hart | MI | 2026-11-26 | 17 |
| Westbrook | ME | 2026-11-28 | 19 |

Full worklist (289 findings) saved to the run log; not reproduced here in full — promotion/dismissal of any of the above is a human step (read the locality's own source), per CLAUDE.md.

## Review-queue backlog

| Queue | New (awaiting review) | Total | Promoted | Dismissed |
|---|---|---|---|---|
| `data/moratorium_candidates.json` | 2,537 | 2,837 | 249 | 51 |
| `data/project_candidates.json` | 190 | 302 | 65 | 47 |

### Moratorium queue — triage tiers (`scripts/triage_moratorium_candidates.py`)

1,775 distinct untracked candidates (502 already published, dropped): **A cited 277**, B structured 1, C thin 91, D unlocated 1,406.

Top 10 tier-A (cited, cheapest to promote this week — one page to read, one row to write):

1. Pickens Co. — council holds first reading of proposed data center moratorium (22 outlets)
2. Eugene — residents urge city council to consider data center moratorium (6 outlets)
3. Hudson — Scenic Hudson president praises Gov. Hochul's moratorium on data centers (3 outlets)
4. Pitt (County) — to hold public hearing on data center moratorium (3 outlets)
5. Alachua — commissioners vote to advance one-year data center moratorium (2 outlets)
6. Butler Twp. — supervisors to consider data center ordinance Oct. 13 (2 outlets)
7. Casey (County) — Fiscal Court approves data center moratorium (2 outlets)
8. Dauphin (County, PA) — township moves to get ahead of data center development with a targeted ordinance (2 outlets)
9. Florence (County, SC) — board approves data center moratorium, ends Flock camera use (2 outlets)
10. "City" — council to vote on data center moratorium (2 outlets, locality name itself unresolved — needs a read before it's usable)

(267 more tier-A items behind these; run `python3 scripts/triage_moratorium_candidates.py --tier A --limit 50` for the next batch.)

### Project queue — newest 10 "new" items

| First seen | Guessed locality/state | Title |
|---|---|---|
| 2026-11-02 | — | Harmony planning commission approves draft data center ordinance |
| 2026-11-02 | — | Public meeting to focus on data centers, battery storage and local zoning |
| 2026-11-02 | Hubbard, — | Hearing tonight on Hubbard Township data center zoning |
| 2026-11-02 | Davidson, — | Davidson County commissioners approve new zoning rules for data centers |
| 2026-11-02 | — | Public hearing on proposed data center on Mike Padgett Highway moved to Dec. 7 |
| 2026-11-02 | — | New date set for public hearing on Clinton's data center ordinance |
| 2026-11-02 | — | Data center applications withdrawn ahead of Upper Merion zoning meeting |
| 2026-11-02 | — | Cincinnati launches zoning study to guide data center growth, seeks public input |
| 2026-11-02 | —, FL | Florida developer seeks approval for Rossford data center |
| 2026-11-02 | — | League City now requires developers to secure special use permit for data centers |

Most candidates arrive with no resolved locality/state (`guess_locality`/`guess_state` null) — per CLAUDE.md, `scan_locality_candidates.py` mines these from the story archive, but turning a headline into a trackable row is still a human read of the primary source.

---
_Promotion, dismissal, and registry edits are human steps — this digest is read-only. No registry, `web/`, or review-queue file was modified to produce it._
