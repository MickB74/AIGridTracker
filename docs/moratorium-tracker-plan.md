# Moratorium tracker: plan to be the best list on the net

_Written 2026-09-02 from an audit of `MORATORIUMS_DF`, the page, the
scripts, and a survey of 20 competing trackers. Not rendered by the site._

## Where we stand

| Metric | GridWatch | Best competitor |
|---|---|---|
| Rows | 386 | Moratorium Nation 505 data-center rows (533 total) |
| States | 39 | Moratorium Nation 42, SAVRN 43 |
| Rows with a clickable source | 386 / 386 | SAVRN 298 / 298; Moratorium Nation **0** (no source column) |
| Rows citing an official document (.gov, ordinance, minutes) | 26 | Not published by anyone |
| Machine-readable end date | 215 | Moratorium Nation (`current_end_date_iso`) |
| Derived expiry, expiring-soon feed | Yes (RSS + JSON) | Nobody |
| Open license + download | CC BY 4.0, JSON + CSV | Moratorium Nation (CC BY), datacentertracker.org |
| Embed widget | Yes | Nobody |
| Map on the tracker page | **No** (lat/lon exists, map lives on Start here) | Moratorium Nation, SAVRN, Interconnected, jwklee |
| ISO action date | **22 / 386** (`when` is free text) | Moratorium Nation (`date_enacted_iso`) |
| Term declared | 293 / 386 (93 `unknown`) | Moratorium Nation `duration_kind` on all rows |
| Status history per row | No | jwklee (236 rows) only |
| Review queue | 1,108 candidates, 1,041 unreviewed, 155 tier A | n/a |

**The honest position.** We already own the axis that matters to a resident
at a hearing: every row has a source, a read date, and a derived status. No
one else has sourced *and* open *and* expiry-aware at any scale. We lose on
coverage (about 120 rows and 3 states behind Moratorium Nation), on source
quality (only 26 rows cite the ordinance or the enacting body; 40 rows lean on
one Pinelands Alliance roundup page and 23 on one WKAR article), and on
structure (no ISO date, so no timeline; no ordinance link field; no history).

Coverage gaps by state, Moratorium Nation vs us: MI 58/31, OH 52/19, GA 47/18,
TN 24/8, IA 26/15, KS 10/3, PA 9/3, UT 6/1, ND 8/0, MA 7/0. Seven states they
cover and we do not: ID, LA, MA, MT, ND, NH, SD. A name match finds 326 of
their data-center rows absent from ours (some are the same event under another
name, so the true gap is smaller).

## The claim to win

"Every U.S. data center moratorium, ban and pause, each with the document it
came from, the date we read it, and whether it is still in force today."
Nobody can say that sentence. Moratorium Nation has the count but no links.
SAVRN has links but no download, no license, no expiry. Data Center Watch owns
the headlines with a dollar figure and a weekly newsletter, and publishes no
data at all.

## Plan

Each phase is independently shippable. Numbers in brackets are the target
state of the metric table above.

### Phase 0: schema fixes that unlock everything else (1 week, code only)

1. **Add `date` (ISO) next to `when`.** Backfill with a script that parses
   the free text and writes the result to a review file; a human confirms
   anything ambiguous ("May 2026" becomes `2026-05` with a `date_precision`
   of `month`). Keep `when` as the display string. [ISO date: 386/386]
   Unlocks the timeline chart, "enacted this month" counts, and sorting.
2. **Add `source_kind`.** Values: `ordinance`, `minutes_agenda`,
   `official_page`, `news`, `roundup`. Derive a default from the domain
   (`.gov`, `municode`, `legistar`, `ecode360` are official) and hand-set the
   rest. Render a badge in the Source column and add a headline stat:
   "N rows cite the ordinance itself". This is the Axis Intelligence
   `pending_primary` idea at real scale, and it turns our weakest number into
   a public worklist rather than a hidden one.
3. **Add `id`** (stable slug, `locality-st`) and `#id` row anchors, so a
   row can be cited by URL. Export it. Add `upstream_id` for the Moratorium
   Nation crosswalk so the coverage diff is a script, not a name match.
4. **Add `ordinance_url`** (nullable) separate from `source`. Many rows are
   sourced to a news report of the vote; the ordinance PDF is the stronger
   document and belongs in its own column so the news link is not lost.
5. **Publish `data/moratoriums-summary.json`** (counts by state and status,
   expiring in 30/60/90 days, generated date) for embeds and for anyone who
   wants the number without the table. Moratorium Nation's
   `summary_stats.json` is the closest thing in the field.

### Phase 1: coverage grind (4 weeks, human research, the `/moratoriums` skill)

Target: **500 rows, 46 states by 2026-10-01**, then parity with Moratorium
Nation's 505 by mid-October and past it by November.

1. **Tier A first.** 155 cited candidates are waiting. At the current rate
   of 5 to 10 promotions per session, that is 15 to 20 sessions. Run the
   skill three times a week with a cap of 10, not once a week with a cap of 5.
2. **Then the seven missing states** (ID, LA, MA, MT, ND, NH, SD). One row
   each closes the state gap to 46 and costs an afternoon; a state page that
   says "no moratoriums tracked" is a worse look than a short list.
3. **Then the deficit states in order of gap:** MI, OH, GA, TN, IA. Use
   the Moratorium Nation crosswalk from Phase 0 to produce the exact list of
   their rows we lack, per state, and read each locality's own site.
4. **Add three candidate feeds** to `scan_moratorium_candidates.py` or as
   sibling scanners: SAVRN's state pages, Electric Choice's table, NLC's
   tracker. Same rule as Moratorium Nation: candidates only, never a
   registry source. Their per-row links (SAVRN, Interconnected) shorten
   the path to the ordinance.
5. **Write a per-state coverage ledger** (`data/moratorium_coverage.json`,
   rebuilt by the triage script): our count, Moratorium Nation's count,
   candidates waiting. Render it on the page as a small table under
   "Known gaps". Publishing the gap is what Moratorium Nation does and it
   reads as rigor, not weakness.

### Phase 2: depth nobody has (ongoing, folded into the weekly loop)

1. **Clear the 93 `term: unknown` rows.** Most are the New Jersey batch
   sourced to the Pinelands roundup. Read each town's ordinance, set `term`
   or `expires`, and move `source` to the ordinance where one exists. This
   also fixes the roundup-dependency problem.
2. **Status history.** Add an optional `events` list per row
   (`{date, kind, source}` with kinds `enacted`, `extended`, `expired`,
   `rescinded`, `replaced`, `rejected`). Render it as a short timeline on
   the community page. Only jwklee's 236-row opposition tracker records
   history; no moratorium tracker does. Start with the 9 expiring-soon rows
   and every row whose `when` currently begins with "Extended".
3. **Scope fields.** `threshold` (MW, acres, sq ft, free text) and `covers`
   (`new_applications`, `rezoning`, `permits`, `all_uses`). This is what a
   council member asks first: "what exactly did they pause?" Moratorium
   Nation's 44-clause extraction is the only comparable thing and it is a
   research artifact, not a table anyone reads.
4. **`replaced_by`** for a moratorium that ended in an ordinance. Six case
   studies is a start; the field lets every row say what happened next.

### Phase 3: the page (2 weeks, code)

1. **Map on the tracker page.** Lat/lon exists for 369 local rows. Inline
   SVG states with dots, color by `effective_status`, click to filter the
   table. Every competitor with a map gets cited for the map.
2. **Timeline chart** by month of enactment, once `date` exists. This is
   the "moratoriums are accelerating" graphic newsrooms build by hand.
3. **"Changed this week" section and `changes.xml`.** Diff
   `web/data/moratoriums.json` against the previous commit at build time:
   added, status changed, expired, extended. The alerts feed covers
   deadlines only; a changes feed is what a reporter subscribes to.
4. **"How we count" page** (`moratoriums-methodology.html`): the definition
   (moratorium, ban, pause, restrictive rezoning, and what is excluded),
   the sourcing rules, why counts differ across trackers (SAVRN 298,
   Electric Choice 321, Interconnected ~268, Moratorium Nation 533, NLC 76),
   and the known gaps. Every reporter who has to pick a number cites the
   tracker that explains its number.
5. **"Cite this" block** with a stable citation string and, via Zenodo, a
   DOI on each monthly data release. Researchers cite DOIs.
6. **State rollup** at the top of each state page: in force, expiring,
   proposed, with the list. Partly exists; make it the first thing on the
   page.

### Phase 4: distribution (monthly, 2 hours each)

1. **A monthly number and a post.** First business day: "N communities in
   M states, K new this month, J expiring in the next 30 days, P million
   residents covered." Population needs a Census join on locality, which is
   a one-time script. Data Center Watch owns the headline because it ships
   a number on a schedule; we can ship a better one with the data attached.
2. **Get cited where the counts get cited.** Wikipedia's "Opposition to AI
   data centers" article, Ballotpedia's data center page, Sabin Center's
   blog, NLC's tracker (they accept document submissions), and Moratorium
   Nation's known-gaps page (offer the crosswalk and the source links as a
   CC BY contribution; a link from the best-known dataset is worth more
   than beating it).
3. **Email digest** from the changes feed, using the Formspree signups
   already collected in the footer.

### Phase 5: automation that keeps it true (1 week, code, then CI)

1. **Re-verify expiring rows automatically.** Weekly: for every row with
   `expires` inside 45 days, fetch its source and the locality's agenda page
   and flag it in the review file with the fetched headline. A human still
   decides, but the list of what to check arrives pre-built.
2. **Stale-date rule tied to risk.** `as_of` older than 90 days on a row
   expiring within 60 days is a red flag, not a chore; render it as such.
3. **Online link check in CI** already runs weekly; add `ordinance_url`
   to it and report `source_kind` counts in the job summary so the
   primary-source share is watched, not guessed.
4. **Moratorium Nation crosswalk refresh** on each vendored update, writing
   the per-state coverage ledger from Phase 1.

## Order of work

| Week | Do |
|---|---|
| 1 | Phase 0 (all five items). Phase 1.1 begins: three skill runs, cap 10. |
| 2 | Phase 1.2 (seven missing states). Phase 3.4 methodology page. Skill runs continue. |
| 3 | Phase 1.3 begins with MI and OH. Phase 3.1 map. |
| 4 | Phase 3.2 timeline, 3.3 changes feed. First monthly post (Phase 4.1) on Oct 1. |
| 5–8 | Phase 1.3 through GA, TN, IA. Phase 2.1 NJ term backfill. Phase 5 automation. |
| 9+ | Phase 2.2–2.4 depth fields as rows are touched. Phase 4.2 outreach once past 505 rows. |

## What "best" will mean, measurably

- Rows and states: past 505 and 46 by November 2026.
- Primary-document share (`source_kind` official): from 26 rows to 40 percent.
- ISO date on every row; `term` declared on every row.
- Median `as_of` age under 60 days; no expiring row older than 90 days.
- Changes feed, map, timeline, methodology page live.
- Cited by at least two of: Wikipedia, Ballotpedia, Sabin Center, NLC,
  Moratorium Nation.

## Rules that do not change

Promotion is a human reading a primary source. Never invent an `as_of`.
Never infer `term` from note text. Read `effective_status`, never `status`.
Rebuild `web/` in the same commit as the data. External trackers are
candidate feeds, never registry sources.
