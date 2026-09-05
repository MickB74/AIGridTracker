---
description: Weekly moratorium maintenance — audit, scan, promote researched rows, rebuild web/
argument-hint: "[max rows to promote, default 5]"
allowed-tools: Bash, Read, Edit, Grep, Glob, WebSearch, WebFetch, TodoWrite
---

# Weekly moratorium refresh

Run the whole moratorium maintenance loop for `MORATORIUMS_DF` in
`src/constants.py`, then regenerate the site so `web/` matches the data.

Promote at most **$1** (default 5) candidates this run. Fewer is fine — a row
you cannot source is a row you do not add.

Read `CLAUDE.md`'s Data sourcing rules before editing any registry row. The
three that decide this task: never invent an `as_of`; never infer `term` from
the note text; `expires` is data and `effective_status` is derived.

## 1. Audit what is already published

```bash
python3 scripts/verify_moratoriums.py --out data/moratorium_review.md --json data/moratorium_review.json
```

Read `data/moratorium_review.md`. Fix what is fixable here and now:

- **Lapsed terms** — a moratorium past its `expires` already renders as
  *Expired* (derived). Only edit the row if the locality actually extended,
  rescinded, or replaced it, and only with a primary source. Otherwise leave
  it; the derivation is doing its job.
- **Dead source links** — *blocked* (403/405/429) is bot refusal, not rot;
  leave those alone. A real 404/410/DNS failure means find the article's new
  home or an equivalent primary document, and update `source` **and** its
  paired `as_of` together.
- **Rows with no source** — these render as *Unverified*. Try to source them;
  if you cannot, leave them unverified rather than attaching a weak link.
- **Stale `as_of` (>180 days)** — re-read the source, confirm the status still
  holds, bump `as_of` to today's date. If the source no longer supports the
  stored `status`, change the status, not just the date.
- **Time-limited rows with no end date** — find the ordinance's stated term.
  If it truly is undated, declare `term` (`standing` / `until_event` /
  `fixed_undated`) instead of guessing an `expires`.

## 2. Refresh the candidate queue

```bash
python3 scripts/scan_moratorium_candidates.py
```

```bash
python3 scripts/sweep_moratoriums_from_archive.py --report
```

Then rank what is waiting:

```bash
python3 scripts/triage_moratorium_candidates.py --tier AB --limit 25 --out data/moratorium_triage.md
```

Tier A is cited (publisher link or a named document plus a locality) — start
there. Tier B rows are dated and upstream-verified but ship **no source URL**,
so the ordinance still has to be found before the row can exist.

## 3. Promote researched rows (the human step)

For each candidate you take, in order:

1. Open the locality's own site — the ordinance PDF, the council agenda or
   minutes, or the county's own notice. A news article is acceptable when it
   is the only record, but the .gov document is the better `source`.
2. Confirm the **locality, state, status, and dates** from that document. Do
   not take them from a headline or a search-engine snippet.
3. Add one row to `MORATORIUMS_DF` in `src/constants.py` with `source`,
   `as_of` (today, the date you read it), `expires` (ISO date, or `None` when
   permanent / condition-based / undocumented) and, when `expires` is `None`,
   a declared `term`.
4. If you could not confirm it, mark the queue entry `"status": "dismissed"`
   in `data/moratorium_candidates.json` with a one-line reason so the scanner
   never re-raises it.

Never add a row with a fabricated date, and never add a duplicate
`(locality, state)` pair — check before you write.

## 4. Rebuild and verify

```bash
python3 -m py_compile build_site.py src/constants.py && NEWS_FREEZE=1 python3 build_site.py
```

```bash
python3 scripts/check_site_fresh.py --strict
```

`web/` is committed output: it has to be rebuilt in the same commit as the
data. `NEWS_FREEZE=1` keeps news out of the diff. Expect
`web/assets/gridwatch_health_risks.pdf` to change bytes regardless — fpdf2 is
not byte-deterministic.

Re-run the audit at the end to confirm the worklist actually shrank:

```bash
python3 scripts/verify_moratoriums.py --offline --out data/moratorium_review.md --json data/moratorium_review.json
```

## 5. Report

Tell me, in a few lines:

- rows added (locality, state, status, source domain)
- rows corrected, and what changed
- candidates dismissed, and why
- what is still open in the worklist

Then stage the change and show me the diff stat. **Do not commit or push** —
I will read the new rows first.
