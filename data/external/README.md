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

## PA DEP Data Center Permit Tracker (`pa_dep_*`)

Pennsylvania Department of Environmental Protection, *Data Center Permit
Tracker*.

- Site: https://gis.dep.pa.gov/DataCenterPermitTracker/
- Underlying data: two CSVs served from `static/` behind the ArcGIS front end
  — `DataCenterProjectTrackingAllProjects.csv` (one row per project) and
  `DataCenterPermitTracking.csv` (one row per environmental permit). No key,
  no rate limit, no terms beyond ordinary Commonwealth public-records status.
- Snapshot cached here on every sync so an upstream change reads as a
  reviewable diff. Refresh (and merge) with:

      python3 scripts/fetch_pa_dep_projects.py

Unlike Moratorium Nation, this one feeds a registry directly rather than a
review queue. The difference is not trust in the automation but what the
source *is*: a state agency's own register of the projects its regional
offices are permitting supplies `source` and `as_of` with no judgement call,
which is the whole reason promotion is otherwise a human step. Synced rows
carry `origin: "pa-dep"` in `data/projects.json`, hand-researched rows are
never overwritten, and DEP's "DEP Review Complete" is recorded as a permit
milestone — never as a local land-use approval.
