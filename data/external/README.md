# Vendored external datasets

## Moratorium Nation (`moratorium_nation_*`)

Bommarito, M. J., *Moratorium Nation: A Survey of Data Center, Renewable
Energy, and Battery Storage Moratoria in the United States* (April 2026).

- Upstream: https://github.com/mjbommar/moratorium-data-2026
- Site: https://mjbommar.github.io/moratorium-data-2026/
- Data licence: **CC-BY-4.0** (see `moratorium_nation_LICENSE-data.txt`);
  citation metadata in `moratorium_nation_CITATION.cff`.
- Vendored snapshot: upstream `main` as of **2026-08-19**, retrieved 2026-08-20.

Vendored rather than fetched at build time so the daily CI job stays
stdlib-only and offline-safe, and so a change upstream shows up as a
reviewable diff instead of silently altering a published page. Refresh with:

    python3 scripts/import_moratorium_nation.py --fetch

**CC-BY-4.0 requires attribution wherever this data is used.** Two consumers,
with deliberately different bars:

1. `data/external_gazetteer.json` — jurisdiction *names* only, used by
   `story_tracker.build_gazetteer()` to recognise place names in headlines.
   Names are not claims, so this carries no per-row `source`/`as_of` burden.
2. `data/moratorium_candidates.json` — rows appended with
   `"origin": "moratorium-nation"` for **human review**. These are candidates,
   never facts: `verify_count` is not a source URL and is not an `as_of`.
   Promoting one into `MORATORIUMS_DF` still means reading the ordinance and
   recording where it was read, per CLAUDE.md's Data sourcing rules.
