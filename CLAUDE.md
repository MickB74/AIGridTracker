# CLAUDE.md — GridWatch AI

Context for AI agents working in this repo.

## What this is

A static site — **[aigridwatch.com](https://aigridwatch.com)** — that (1)
estimates the energy, water, and carbon footprint of LLM token usage, from a
single prompt to the global data-center grid, and (2) serves as a community
advocacy platform: a moratorium tracker, a project tracker, CBA negotiation
tools, data dividend calculators, PUC and executive directories, and policy
templates. The audience is community members facing data center development who
need data and tools to negotiate effectively — typically inside a ~3-week
window before a zoning vote.

Everything ships as generated HTML. `build_site.py` renders `web/` from the
registries in `src/constants.py`; Vercel serves `web/` as-is with no build step.

**There is no Streamlit app.** It was retired in August 2026 and its code was
deleted in August 2026 — `app.py`, `src/ui/`, `.streamlit/`, `assets/style.css`
and twelve `src/services/` modules are gone from the tree, not merely unused.
No tracked file imports `streamlit`. Do not resurrect them from git history, do
not point users at a hosted app, and do not reintroduce a `streamlit` import
anywhere.

## Run

```bash
python3 build_site.py
```

Writes `web/` (~565 pages) plus `sitemap.xml`, `robots.txt`, and both
`vercel.json` files. Env overrides: `SITE_URL`, `GC_URL`, `FORMSPREE_ID`.
`NEWS_FREEZE=1` pins the news/YouTube fetches to the committed cache — use it
for any rebuild that isn't specifically refreshing news, so the diff shows only
what the data moved. `NEWS_REFRESH=1` forces a live fetch.

Preview locally with the `static-site` entry in `.claude/launch.json`
(port 8777). It runs `scripts/serve_web.py`, not the stock `http.server`,
because the site's links are extensionless (see the clean-URL gotcha below)
and the stock server 404s on them.

**The repo lives at `~/GitHub/AIGridTracker`.** It was moved out of
`~/Documents/GitHub/` on 2026-08-30 because that path is inside the
iCloud-synced Desktop & Documents container, which had evicted 15,565 of the
tree's 15,591 files to APFS `dataless` stubs — real metadata, zero bytes. That
is the cause of the historical half-empty `web/` builds and of the `name 2`
duplicates the build guard trips on (21 of them, including a bogus
`.git/refs/heads/master 2`). If a build ever produces suspiciously few pages,
check `du -sh web/` against `ls -lO` for `dataless` before debugging anything
else, and do not move this repo back under `~/Documents`.

**`build_site.py` deletes `web/` and regenerates it.** An interrupted build
leaves the tree half-empty; recover with `git checkout-index` over the deleted
paths, then rebuild. Don't panic and don't hand-edit `web/`.

## Verify before committing

```bash
python3 -m py_compile build_site.py src/constants.py && NEWS_FREEZE=1 python3 build_site.py
```

```bash
python3 scripts/check_site_fresh.py --strict
```

The first proves the site still builds; the second proves committed `web/`
matches committed data. Run the second before any push — `web/` is committed
output, so a registry edit without a rebuild publishes a site that contradicts
its own constants.

## Architecture

### Entrypoint

- **build_site.py** (~14,000 lines) — the whole product. One module, one
  `main()`, one function per page. It imports from `src/` only — but in two
  places, and both count as the build path:

  - **Top of file:** `constants`, `blog_content`, `blog_art`, `alerts`,
    `briefs`, `permit_lookup`, `pdf_pack`, `us_map_data`,
    `company_complaints`, `story_tracker`.
  - **Inside functions** (deferred to keep the roster modules off the import
    cost of every build step): `senate_races`, `house_races`, `race_common`,
    `official_grades`, `local_officials`, `services.officials`.

  Sixteen modules, not ten. An earlier version of this file listed only the
  first group and called it "the whole build path", which contradicted the
  NOT-legacy table below — verify with the `ast` walk described at the end of
  this file rather than trusting either list. Keep it short, and keep every
  module on it free of `streamlit`, network calls, and Streamlit `\$`
  escaping.


### Data layer

- **src/constants.py** (~10,400 lines) — All static data, coefficients, and registries. Major datasets:
  - `SOURCES` — dict mapping source keys to `(name, url)` pairs; used by `src_link()` everywhere
  - `DATACENTERS_DF` — market-level power by phase (operational/UC/planned)
  - `DC_SITES_DF` — per-campus site table with operator/owner/tenant/LLC/attribution
  - `OPERATORS` / `OPERATORS_DF` — operator registry (tier, owner, model, LLCs)
  - `EXECUTIVES_DF` — 39 executives with company, title, category, focus, LinkedIn
  - `AI_COMPETITORS_DF` — SEC 10-K competitor analysis
  - `STATE_DC_DF` — 50-state facility count and TWh/year
  - `STATE_GRID_PROFILES` — 51-state residential rate ($/kWh), grid carbon (gCO2/kWh), water stress; feeds the impact calculator and meeting prep generator
  - `MEGA_PROJECTS_DF` — top 10 megaprojects under construction
  - `STATE_PUCS_DF` — 51 PUC commissions (50 states + D.C.) with website and complaint links
  - `LOCAL_BODIES_DF` / `LOCAL_OFFICIALS_DF` — town/county governing bodies
    (meeting schedule, agenda URL, public-comment process) and named local
    officials for localities with an active fight. **Every row carries `source`
    (the official .gov page) and `as_of` (the date it was read).** Populate only
    by reading the locality's own roster page — never from search-engine
    snippets, which were wrong for 2 of the first 4 localities validated.
    Blank `stance` means "not recorded", never "neutral".
  - `STATE_MUNI_LEAGUES` — 49 state municipal leagues (per NLC). Hawaii has
    none: no independent municipalities, county government only.
  - `MORATORIUMS_DF` — data center moratorium/ban tracker. **Per-row `source`
    + `as_of` + `expires`**, same discipline as the `LOCAL_*` tables: a row
    with `source=None` renders as *Unverified* everywhere and is never
    presented as fact. `expires` (ISO date, or `None` when permanent,
    condition-based, or undocumented) drives `moratorium_status()`, which
    derives the `effective_status` / `expired` / `days_left` /
    `expiring_soon` / `verified` columns at import. **Read
    `effective_status`, never `status`** — a lapsed moratorium cited as
    current is the fastest way for a resident to lose a hearing. `Expired` is
    derived and never stored; `Rescinded` is a real stored status.
    An optional per-row `term` declares how an *undated* term is bounded —
    `standing` (permanent ban or standing statute), `until_event` (ends on a
    condition), `fixed_undated` (a stated duration whose start/end nobody has
    recorded). `moratorium_term()` derives `term_kind` / `term_label` at
    import, and `until_date` (any row with an `expires`) always wins over the
    stored value. **Never infer `term` from the `note` text** — a regex over
    the notes read Coachella's 45-day pause as a permanent ban and Peculiar's
    zoning strike as a fixed term. An undeclared row is `unknown`, which is a
    worklist item, not a guess. The point is that a null `expires` used to
    mean three incompatible things at once, so the strongest rows on the page
    (permanent bans) rendered identically to the weakest (unresearched).
    Maintained by `scripts/verify_moratoriums.py` (audits what is published),
    `scripts/scan_moratorium_candidates.py` (finds what is missing) and
    `scripts/triage_moratorium_candidates.py` (ranks the queue) — see Data
    maintenance scripts below. **386 rows, no duplicate `(locality, state)`
    pairs.** Ten duplicated events from overlapping research batches were
    merged on 2026-08-23; when merging, keep the row whose source actually
    supports the stored `status` (two of the ten cited an article predating
    the vote it claimed to document) and keep `source` paired with its own
    `as_of`. Seven source URLs are still shared by several rows — those are
    multi-locality roundup articles, not duplicates, so dedupe on
    `(locality, state)` rather than on the URL.
  - `MORATORIUM_OUTCOMES` — six case studies, each with `sources` (a list of
    URLs) and `as_of`. The Start here wizard labels these "precedents worth
    citing" and a resident reads them aloud at a hearing, so the bar is higher
    than for the tracker: **say only what the sources say, and render the
    sources alongside the claim** (`_outcome_card()` in `build_site.py`, the
    expander in `start_here_tab.py`). All six were rewritten on 2026-08-04
    after none survived verification — the originals asserted wins no source
    supports (a $2.5M rec centre in Groton, a 25%-of-supply water cap in The
    Dalles, quarterly reporting in Mesa) plus a Cheyenne timeline set in the
    future. When the real outcome is worse than the story, say so: The Dalles
    is now categorised *Mixed outcome* precisely because a community planning
    around a cap that was never won is worse off than one that knows it still
    has to win it.
  - `SENATE_RACES_2026` (in **`src/senate_races.py`**, not `constants.py` —
    it is ~500 lines of roster) — the 35 races on the 2026 U.S. Senate ballot,
    117 filed candidates, and each candidate's documented AI/data-center
    record. **The roster is primary-sourced**: every race's `roster_source` is
    the state election authority's own certified candidate list, because who is
    on a ballot is a fact the state publishes. **Records key on the full
    candidate name, never the surname** — the Alaska ballot carries both
    `Dan S. Sullivan` (the incumbent) and an unrelated `Dan J. Sullivan` placed
    there by court order, and a surname key gave the senator's record to both
    men. `lean` summarises only the cited items on one axis (does this
    candidate's documented position make data centers pay their own way?); it
    is **not** a grade, which is the deliberate difference from
    `src/official_grades.py` — most people here are challengers whose entire
    record is a press release, and a promise is not an action. Candidates with
    nothing located are `unrecorded` and render as *No record found*, never as
    neutral. Coverage is published on the page precisely because it is low
    (17 of 117 at launch).
  - `HOUSE_RACES_2026` — the 2026 U.S. House ballot: 435 voting districts
    plus 5 non-voting delegates, 1,161 filed candidates. **The roster lives in
    `data/house_races_2026.json`, not in Python** — 440 districts is ~2,500
    lines of pure roster, and inlining it the way `senate_races.py` does would
    bury the curated part under data nobody hand-edits. Only `AI_RECORDS`,
    which is hand-researched, stays in `src/house_races.py`. Where mid-decade
    redistricting put two sitting members in one seat (CA-41, FL-25, TX-33,
    UT-3) both appear in `incumbents`. Same rules as the Senate registry:
    primary-sourced roster, per-item `source` + `date`, full-name keys,
    `unrecorded` for silence. Coverage starts near zero by construction and the
    page says so — this is a complete *ballot* with an almost-empty *record*.
  - `STATE_PERMIT_PORTALS` / `NATIONAL_PERMIT_TOOLS` / `RTO_QUEUES` +
    `STATE_RTO` / `PERMIT_KINDS` — the permit paper trail: where a project's
    public record lives. **Navigational links, not claims** — nothing here
    says a permit exists, which is why they carry a link-check date rather
    than a research `as_of`. Only 16 of the 51 jurisdictions (50 states and D.C.) publish a searchable
    permit register; `register: None` is a real answer meaning a records
    request is the only route, so never paper over it with a search link
    dressed as a database. `STATE_RTO` is a routing hint (several states are
    split between markets, several sit outside every market) — the serving
    utility is the only authority on which queue a site is in. Maintained by
    `scripts/verify_permit_portals.py`.
  - `COMPANY_CONCESSIONS` — per-operator negotiation intel: documented concessions won elsewhere + a strategy read; feeds the meeting brief / action pack
  - `CBA_BENCHMARKS` — what similar communities won (Start here impact step)
  - `OUTREACH_TIPS` — platform-by-platform digital organizing playbook (Nextdoor/Ring/Facebook/WhatsApp/forums)
  - `HEALTH_RISKS` — six health-risk panels (air/noise/light/bills/water/climate); every fact carries a SOURCES key; rendered by `build_site.py::build_health_risks()` and `build_health_pdf`
  - Environmental report headline data for all four hyperscalers:
    `GOOGLE_*` (FY2025), `META_*` (FY2024), `MICROSOFT_ENV_HEADLINE` (FY2025),
    `AWS_ENV_HEADLINE` (CY2025). Microsoft/AWS don't break out DC-only
    electricity — those TWh and location-based Scope 2 values are estimates
    derived from reported growth rates; keep the "(est.)" markers when
    displaying them. When a new report edition lands, update the headline
    dict, its `SOURCES` entry, and the `REPORT_REGISTRY` year in
    `src/services/report_check.py`.
  - `STATE_STUDIES` / `MODEL_CLAUSES` — state-commissioned impact studies and the model CBA clause library. Moved out of `src/ui/` in August 2026 when the app was retired; they render `studies.html` and `cba-clauses.html`.
  - `NEWS_SOURCE_TIERS` / `news_source_tier()` — outlet-quality classifier for
    the live news feed. Google News returns AP next to stock-tip portals, so
    every headline's outlet is placed in a tier: `wire`, `national`,
    `nonprofit`, `trade`, `local`, `official` (a `.gov` page) — the citable
    ones, listed in `NEWS_REPUTABLE_TIERS` — plus `aggregator` (press-release
    wires and syndication hosts) and `advocacy` (think tanks, law firms,
    campaign sites), which are `NEWS_DEMOTED_TIERS`: labelled in the browse
    feed but excluded from the ranked "Top stories" block and from state
    pages. `unrated` is the honest default and means "we couldn't place this
    masthead", never "don't trust it" — about a fifth of the archive is
    unrated and it still renders, just without a badge or a ranking bonus.
    Local press can't be enumerated, so it's recognised structurally
    (broadcast call letters, affiliate numbering like `41NBC`, masthead
    vocabulary). **Two ordering rules are load-bearing:** the affiliate
    regex runs *before* the tier lists (else "41NBC News" reads as NBC News,
    and "NBC 5 Dallas-Fort Worth" as national), and bare call letters run
    *after* them (else "WSJ" reads as a TV station). Masthead words match on
    word boundaries — a substring test filed "Startup Fortune" under local
    via "star" — except for bare-domain names, where boundaries mean nothing.
    `NEWS_SOURCE_EXACT` handles mastheads that contain another tier's needle
    ("MSNBC" contains "msn", "Heatmap News" contains "ap news").
    Tiers feed `_rank_stories_build()` as a score term, so mainstream and
    wire reporting floats. **Videos share this registry — there is no separate
    video allowlist.** The old `YOUTUBE_QUALITY_SOURCES` set was deleted in
    August 2026 because it was dead code that could never have worked: Google
    News reports the source of every `site:youtube.com` result as the literal
    string "YouTube", so an outlet allowlist over that field matches nothing.
    The videos page therefore carries no source labels and says so; its
    curated `VIDEO_CHANNELS` list is the only publisher claim on it. **Top stories are re-ranked every build** from the
    cached theme buckets rather than read back from `news_cache.json` — the
    weights live in code, so a `NEWS_FREEZE=1` rebuild must not keep
    publishing a ranking the current rules would reject.
  - Grid coefficients, model parameters, ERCOT large-load data

- **src/permit_lookup.py** — `sections(project)`: where to read one
  project's public record, grouped into state environmental permits, county
  and town filings, utility/grid records (RTO queue, PUC docket, FERC), and
  federal databases. Each link carries a `kind`: `register` (a public
  database), `search` (a pre-built query — **render the distinction**, since
  citing a search result at a hearing is how a resident loses one), or
  `note`. `known_permits(project)` is the separate, stronger claim: dated
  `permit` events already sourced on the row (PA DEP rows arrive with permit
  numbers). `document_checklist()` returns `PERMIT_KINDS`. Pure functions, no
  network. Rendered by `build_site.py::_project_paper_trail`
  (every dossier on `web/projects.html`, plus the `#records` section) and by
  Step 2 of the Start here wizard.

- **src/race_common.py** — shared machinery for both race trackers: the
  `LEANS` vocabulary, full-name record keys, staleness (`STALE_AFTER_DAYS`),
  `election_phase()` (campaign → election day → archive, derived from
  `ELECTION_DATE` so the daily rebuild flips the page's framing with no edit),
  automated `mentions_for()` matching against the story archive, and
  `validate()`. **`validate()` is the guard that matters**: it fails a record
  keyed to a candidate who is not on that ballot, an unknown `lean`, a missing
  `as_of`, or an item without a source URL. The failure mode on these pages is
  not a crash — it is confidently attributing a position to the wrong person.

- **src/briefs.py** — `build_meeting_brief_data(state, operator, meeting_type, mw)`: structured meeting-brief assembly (sections of kv/bullets/numbered/advice) plus the `MEETING_ADVICE` strategy dict. Only `MEETING_ADVICE` is imported by the build; the site's own meeting brief is generated client-side in `build_start_here()`. Output is plain text — don't escape `$` here.

- **src/pdf_pack.py** — **only `build_health_pdf()` is on the build path** (it draws `web/assets/gridwatch_health_risks.pdf`); the rest served the retired app's downloads. `build_action_pack_pdf(state, stage, stage_info, brief_data, dated_moves=, scripts=, letters=, social_posts=, outreach_tips=)`: branded PDF rendering of the Start here action pack (fpdf2; natively drawn logo, header/footer with page numbers), plus `build_flyer_pdf(...)`: one-page EN/ES community flyer + petition/sign-up sheet. Consumes `build_meeting_brief_data()` output; core fonts are cp1252-only, so all text goes through its `_latin1()` sanitizer (drops emoji). Layout gotchas the helpers already handle: call `_ensure_room()` before any row that captures `get_y()` (else orphaned bullets at page breaks), and multi_cell leaves x at the right edge (paragraph() resets it).

### Static site (web/ — Vercel front door)

- **Pages built** — landing page, Start here wizard (`start-here.html`), 51 state one-pagers (`states/<slug>.html`), moratorium tracker (`moratoriums.html`), 2026 Senate race tracker (`senate-races.html`), project tracker (`projects.html`), 379 community briefings (`communities/<loc>-<st>.html`), story tracker (`story-tracker.html`), client-side impact calculator (`impact.html`), bills / outlook / learn / puc / executives / data-centers / environment / studies / cba-clauses, company scorecards, blog posts, the health infographic PDF, per-state RSS feeds, JSON+CSV open-data downloads, and sitemap/robots/vercel.json. Blog posts are markdown converted via the `markdown` library.

- **Deployment** — Vercel serves `web/` as-is (Root Directory = `web`, framework "Other", no build step). `web/` is committed output: rebuild it in the same commit as any data change. The **root** `vercel.json` is the load-bearing one.

- **Long pages get collapsible sections.** `build_site.py::_md_sections()` (markdown source) and `_html_sections()` (pages already written as flat `<section><h2>…` blocks) both feed `_sections_shell()`, which emits an "On this page" jump nav plus one numbered `<details class="more sect">` per heading, first section open. Used by `community-value.html` and `learn.html`. The nav's **Expand all** button is not decoration — closed `<details>` are invisible to Ctrl-F and to printing, which is how a resident actually uses these pages. Section ids are slugged from the heading, and the inline script opens the target on `#s-…` deep links, so existing anchors keep working. Reach for this whenever a page passes ~4,000px of scroll.

- **src/story_tracker.py** — Pure grouping/summarization for the story tracker: `build_gazetteer()` (known localities from `DC_SITES_DF`/`LOCAL_BODIES_DF`/`MORATORIUMS_DF`, longest-name-first, excluding entries that collapse to a bare state name — see the code comment on `"Ohio (ballot measure)"`), `guess_locality(title, gazetteer)`, `group_stories(stories, min_for_summary=4)`. Each build, `build_site.py::_persist_story_candidates()` merges the same live-fetched community-impact feed used by `/news/` into `data/story_candidates.json` (dedup by link; `first_seen` is set once and kept, `last_seen` bumps on every re-fetch — this is what makes it a running archive rather than the news page's rolling 7-day window). Unlike `moratorium_candidates.json`/`project_candidates.json`, this queue is **not** a human-review gate — headlines publish straight to `story-tracker.html`, same as the live news feed already does, just with an "automated, not verified" caveat on the page. A locality with 4+ archived stories gets `summarize_group()`'s heuristic extractive summary (keyword/outlet counts, no LLM call) — that's the "AI summary" trigger.

### Services (src/services/)

One module, and it is **on the build path**:

- **src/services/officials.py** — `load_officials()`: reads the root
  `officials.json` (Senate contact XML + current-governors list) into a
  DataFrame. `functools.lru_cache`, no network, no Streamlit. Feeds
  `build_official_scorecard()` → `web/scorecard.html`. Refreshed by
  `scripts/refresh_officials.py`.

The other twelve modules were **deleted** in August 2026 — eleven
`@st.cache_data` live-fetch wrappers plus `secrets.py`, the app's env/config
helper. Two facts they carried were preserved rather than lost with them:

- `REPORT_REGISTRY` and `MONITOR_REGISTRY` (was `report_check.py`) now live in
  `src/constants.py`, next to the hyperscaler headline dicts they describe.
  When a new environmental report lands, update the headline dict, its
  `SOURCES` entry, and the `have`/`label` in `REPORT_REGISTRY` in one commit.
- OpenStates **excludes governors and mayors** (was `openstates.py`), which is
  why `LOCAL_OFFICIALS_DF` has to be hand-read off each locality's own .gov
  roster. That note now lives in `src/local_officials.py`'s docstring.

`ercot.py` was deleted too, along with the `scan_ercot()` stub in
`scripts/scan_project_candidates.py` that called it. The stub imported
`fetch_large_loads`, a name the module never defined, so the ERCOT lead path
raised `ImportError` into its own `except` on every `--online` run and had
never produced a candidate. ERCOT publishes no machine-readable large-load
queue, so reviving it means finding a real source first, not restoring the
call.

### Other files

- **parse_reports.py** — CLI tool to extract metrics from Google/Meta environmental reports into constants
- **assets/hero.png** / **assets/logo.svg** — header image and logo (also the OG-card fallback)
- **scripts/make_og_images.py** — local-only (needs Pillow, deliberately absent from `requirements-build.txt`); redraws the committed per-page OG PNGs in `web/assets/og/` when page counts drift
- **docs/marketing-plan.md** / **docs/backlink-campaign.md** / **docs/outreach-ready.md** — distribution plans, not rendered by the site
- **data/reports/** — Source PDF reports

## Conventions

### Data sourcing
- Every numeric claim gets a source key in `SOURCES` and a link via `src_link(key)`.
- **Every registry declares its freshness.** New bulk registries get an entry in `REGISTRY_PROVENANCE` (`src/constants.py`): `as_of`, `source`, `churn` (low/medium/high), and a plain-language `caveat`. Render it with `render_freshness(st, "MY_DF")` in the app and `provenance_html("MY_DF")` in `build_site.py` — both flag a dataset past its churn-based shelf life (low 36mo / medium 18mo / high 9mo) instead of quietly captioning it. Per-row `source` + `as_of` (the `LOCAL_*` pattern) is better where rows are added individually; `REGISTRY_PROVENANCE` is for datasets compiled in bulk.
- **Never test a DataFrame cell for emptiness with `if v` or `str(v) != "nan"`.** A missing object-column value is `None` on pandas 2.x but `NaN` on 3.x — and `NaN` is truthy. Use `has_value(v)` from `src/constants.py` (or `cell(v)` in `build_site.py`, which also escapes and falls back to an em-dash). Both bugs this caused shipped to production: the literal word "None" in the Tenant column on five state pages, and every "unverified" marker vanishing from the search index. `web/` is generated on whatever pandas the builder has, so this diverges silently.
- **Never invent an `as_of`.** Set it to `None` if the verification date isn't known — it renders as "No verification date recorded" and counts as stale. A fabricated date is worse than no date: it invites a citation the user can't defend at a hearing.
- **Derive time-sensitive status, never store it.** A registry row whose truth expires (a moratorium term, a comment deadline, a rate case) gets the end date as data and a pure function that computes the current state from it — `moratorium_status()` is the reference implementation. Storing "Enacted" means the page keeps asserting it forever; deriving it means the daily CI rebuild corrects the page with no edit. Consumers must read the derived column (`effective_status`), not the stored one.
- **`web/` is committed output — rebuild it in the same commit as the data.** A registry edit without `python3 build_site.py` publishes a site that contradicts its own constants, and the daily CI rebuild only corrects it the next morning. `scripts/check_site_fresh.py` catches this before the push; `NEWS_FREEZE=1 python3 build_site.py` pins news/YouTube to the committed cache so a rebuild moves only what the data moved (without it, a lapsed 6h TTL rewrites ~35 files and buries the signal).
- Distinguish **marginal** (load-shifting) vs **average** (fuel-mix) carbon intensity.
- Shared registries live in `constants.py` — never duplicate data inline in tab modules. If two tabs need the same data, one filters the shared DataFrame.

### Data maintenance scripts (`scripts/`)

Stdlib-only on purpose — they run in CI off `requirements-build.txt`, which excludes `requests` and `streamlit`. With one exception, these scripts never edit a registry: promotion and verification are human steps, because that is where `source` and `as_of` come from. The exception is `fetch_pa_dep_projects.py`, and the reason is the source rather than the automation — a state agency's own permit register supplies `source` and `as_of` without a judgement call, so there is no human read to skip.

| Script | What it does |
|---|---|
| `verify_moratoriums.py` | Audits `MORATORIUMS_DF` **and `MORATORIUM_OUTCOMES`**: lapsed terms, dead source links (403/405/429 reported as *blocked*, not dead), rows with no source, `as_of` older than 180 days, and time-limited rows with no recorded end date. `--offline` skips link checks, `--out`/`--json` write the worklist, `--strict` exits non-zero. |
| `scan_moratorium_candidates.py` | Mines the Google News RSS feed for moratoriums not yet tracked and appends them to `data/moratorium_candidates.json`. Entries keep `first_seen`; anything a human marks `"status": "dismissed"` is never re-raised. |
| `triage_moratorium_candidates.py` | Ranks the review queue by how much work stands between a candidate and the two fields the registry requires, `source` and `as_of`. Read-only over `data/moratorium_candidates.json` — writes neither registry nor queue. Four tiers: **A** cited (a publisher link or a named document plus a locality), **B** structured (Moratorium Nation rows that are dated, active and upstream-verified — but that feed ships *no* source URLs, so the ordinance still has to be found), **C** thin (undated, pending, or verify_count 0), **D** unlocated (a headline with no resolvable locality). Drops already-published localities and collapses repeat coverage of one action, using the outlet count as a corroboration signal. Never prints the sweep's `guess_state` as fact — it files Bernards Township and Carter County both under Indiana — so guessed states get a trailing `?` and are ignored when matching against the registry. `--tier`, `--limit`, `--out`, `--json`. |
| `scan_locality_candidates.py` | Mines `data/story_candidates.json` (the story tracker archive) for towns/counties that keep recurring in unlocalized headlines but aren't in the locality gazetteer yet, and appends them to `data/locality_candidates.json`, capped at `--max-new` (default 39) newly-surfaced names per run. Same never-writes-a-registry discipline as the moratorium scanner — promoting a candidate means researching its governing body (and, if it's had a real vote, the outcome) from primary sources and adding a `LOCAL_BODIES_DF`/`MORATORIUMS_DF` row by hand, then running `backfill_story_candidates.py --relabel` so its already-archived stories regroup. Runs daily as a step in `build-site.yml` (after the story archive itself refreshes), not the weekly moratorium job — it needs a fresh archive, not a fresh RSS fetch of its own. |
| `fetch_nj_permits.py` | Mines NJDEP's air-permit register for facilities that look like data centers, into `data/nj_permit_candidates.json`. **A review queue, never a registry** — the opposite call from `fetch_pa_dep_projects.py`, because PA publishes a list of data-center *projects* while NJ publishes 17k permitted facilities that a filter has to guess at (NJDEP codes Memorial Sloan Kettering as NAICS 518210). Each row reports `confidence`: `naics` (NJDEP's own 5182x code) > `operator` (name matches `OPERATORS_DF`) > `name`. Reads NJDEP's ArcGIS NJEMS layer at `mapsdep.nj.gov`, **not** DataMiner — `dep.nj.gov` is behind an Imperva WAF that blocks scripted requests and answers with HTTP 200. Issued permits only: no permit numbers, no application dates, no pending applications, so it is a census of what is already permitted, not an early-warning feed. `--dry-run`, `--offline`, `--report`. Not yet wired into CI. |
| `fetch_senate_money.py` | Pulls tech/utility PAC receipts to 2026 Senate candidates from the FEC into `data/senate_money.json`. The FEC does **not** classify donors by industry, so this matches the *contributing committee's name* against an explicit term list published in the script, and writes every matched committee into the output so any figure on the page audits back to its donors. **Undercounts by design** — individual contributions from company employees are excluded, so a total is a floor. Needs a free `FEC_API_KEY`; refuses to write an empty file, because `build_site.py` renders money lines only when the file exists and an empty one would publish "no money found" for all 117 candidates. `--dry-run`, `--offline`. Not wired into CI. |
| `scan_candidate_records.py` | Mines `data/story_candidates.json` for headlines naming a 2026 Senate or House candidate alongside data-center/AI terms, for candidates with no `AI_RECORDS` entry yet, into `data/candidate_record_candidates.json`. **A review queue, never a registry.** Its `link` is a Google News *redirect*, which is why promotion is a human step: resolve it to the publisher (ideally the member's own release), confirm the person actually said it, then add a row with its own `source` + `as_of`. Name matching requires first name + surname adjacent — a bare surname matches several unrelated members at 1,161 candidates. `--dry-run`, `--chamber`, `--report`, `--limit`. Runs daily in `build-site.yml` after the story archive refreshes. |
| `verify_candidate_records.py` | Audits what the trackers already publish: link-checks every cited URL and flags records whose `as_of` is older than `STALE_AFTER_DAYS`. Classification matches `verify_sources.py` — 401/403/405/429 *blocked* (congress.gov and most house.gov sites refuse scripted clients), 5xx and **timeouts** *flaky*, only 404/410/DNS *dead*. Getting that wrong made `--strict` cry wolf on a live washingtonpost.com link the first time it ran. Read-only. `--offline`, `--strict`, `--out`. Runs daily, non-blocking. |
| `check_site_fresh.py` | Rebuilds with `NEWS_FREEZE=1` and reports whether committed `web/` still matches committed data — the guard against a registry edit shipping without `python3 build_site.py`. **The one maintenance script that is a hard gate rather than a report**, because it compares generated output against its own inputs: there is no 403-vs-404 judgement to defer to a human. `--strict` exits 1, `--fix` keeps the rebuild, and by default it restores `web/` (plus any build-written `data/` file *this run* dirtied) so it is safe on a clean tree. Refuses to run when `web/` is already dirty rather than burying your edits. Runs non-blocking in `build-site.yml` before the real build, so the daily job summary names drift instead of silently absorbing it. Install as a pre-push hook — that is the only moment it can stop a wrong number reaching Vercel, since CI does not run on push. |
| `verify_permit_portals.py` | Link-checks every URL in `STATE_PERMIT_PORTALS`, `RTO_QUEUES`, `NATIONAL_PERMIT_TOOLS` and `FERC_ELIBRARY` — the links a resident clicks to pull a permit file, where a 404 sends them back to the search engine the registry exists to replace. Same classification as `verify_sources.py`: 401/403/405/429 are *blocked* (bot refusal), 5xx *flaky*, 404/DNS *dead*. `--out` writes a worklist, `--strict` exits non-zero on dead links. State agencies reorganise often — expect this to find something. |
| `fetch_pa_dep_projects.py` | Syncs PA DEP's [Data Center Permit Tracker](https://gis.dep.pa.gov/DataCenterPermitTracker/) — two public CSVs behind the ArcGIS front end — into `data/projects.json`. **The only scanner that writes a registry.** Rows land tagged `origin: "pa-dep"`; hand-researched rows are never rewritten (collisions are reported and skipped, since merging two research trails is a human call). Each environmental permit becomes a dated `permit` event carrying its permit number and eFACTS auth ID. Deliberately conservative about what DEP does *not* say: `outcome` stays null ("DEP Review Complete" is a permit milestone, not a township approval), `announced` stays null, and `rezoning_filed` is the earliest permit application date. `--dry-run` reports without writing, `--offline` reuses the cached snapshot in `data/external/`. Runs daily in `build-site.yml` before the build. |

`.github/workflows/verify-moratoriums.yml` runs the moratorium/project scanners weekly and commits the queue. It deliberately does **not** fail the build — a stale row is a chore, not a broken deploy, and a weekly red X gets trained away. The signal is the committed diff in `data/` plus the job summary. `scan_locality_candidates.py` runs daily instead, inside `build-site.yml`, for the same non-blocking reason.

### Network calls

The build fetches news and YouTube at build time (`_load_news` / `_load_youtube`
in `build_site.py`, cached to `data/*_cache.json`, 6h TTL). Everything else on
the site is pre-rendered from committed data — no runtime fetches, because the
published pages are static files.

- A failed fetch must fall back to the committed cache, never crash the build.
- `NEWS_FREEZE=1` skips fetching entirely. Use it for every rebuild that isn't
  about news, or a lapsed TTL rewrites ~35 files and buries your actual diff.
- No secrets in code. `FORMSPREE_ID` and `GC_URL` are public by design (they
  ship in the HTML); anything else comes from the environment.

### Adding a new data registry
1. Add the data to `src/constants.py` as a list of dicts + a `_DF = pd.DataFrame(...)` line.
2. If the data needs a source citation, add entries to `SOURCES` first.
3. Add a `REGISTRY_PROVENANCE` entry and render it with `provenance_html("MY_DF")`.
4. Import it in `build_site.py` and render it; rebuild and commit `web/` in the same commit.

### Adding a new page
1. Write a `build_<name>()` in `build_site.py` returning `page(...)` output.
2. Call it from `main()`, add the page to the nav group it belongs to, to
   `sitemap.xml`, and to the OG-image map if it needs its own card.
3. Long pages (past ~4,000px of scroll) go through `_sections_shell()` — see
   the collapsible-sections note above.

## Site build gotchas

- **Dollar signs in blog markdown**: `src/blog_content.py` was authored when the
  app rendered it through Streamlit, so it still carries `\$` escapes.
  `_md_to_html()` strips them. Write new prose with a plain `$`.
- **pandas 2.x vs 3.x null cells**: see the `has_value()` / `cell()` rule under
  Data sourcing. This is the single most-repeated bug in this repo.
- **`web/` is wiped and regenerated** on every build. Never hand-edit it, and
  never leave a Finder "name 2" copy in it — the build guard fails loudly on
  duplicate-suffixed files and unexpected directories, because Vercel would
  serve and index them as real pages.
- **fpdf2 is not byte-deterministic**: `web/assets/gridwatch_health_risks.pdf`
  changes bytes on every build even when its content doesn't. Expect it in the
  diff; it isn't a content change.
- **Internal links are clean URLs, rewritten at render time.** Vercel serves
  `web/` with `cleanUrls` + `trailingSlash: false`, so `/foo.html` and
  `/blog/` both 308-redirect to `/foo` and `/blog`. Builder functions still
  write `href="{p}foo.html"` and `href="blog/"` (that is what the local
  filesystem understands), and `page()` runs `_clean_links()` over the
  finished document to emit `foo` / `blog`; `_canon()` does the same for
  the canonical tag, breadcrumb items and sitemap. Before this, every
  internal link and five section-index canonicals pointed at a redirect.
  Don't hand-write extensionless hrefs in builders — the rewrite is
  idempotent, but the filesystem preview is not.
- **A dropped page becomes a redirect, never a 404.** `data/retired_paths.json`
  maps every URL the site has ever published and since removed to a live
  destination, and `main()` emits it into `vercel.json`. It was seeded from
  git history on 2026-09-02, when Search Console listed 467 dead URLs, nearly
  all news-only community pages that vanished when their story group
  thinned out. The build maintains it: any path in the previous sitemap
  that is missing from the new one is retired automatically (community
  page -> its state page, anything else -> home), a path that comes back is
  un-retired, and a destination that is not a live page fails the build.
  Renamed localities should still get a `_COMMUNITY_SLUG_ALIASES` entry so
  they redirect to the right locality rather than to the state.
- **`web/404.html` is a real page.** Vercel serves it for any miss; it
  carries `<base href="/">` because it renders at arbitrary depths, and
  `noindex` so it never ranks.
- **The root `vercel.json` is load-bearing.** It carries `outputDirectory` and
  every redirect. Deleting it took the domain down for two days.
- **Renaming a locality changes its community-page URL.** Add an entry to
  `_COMMUNITY_SLUG_ALIASES` in `build_site.py` so the old URL still resolves.

## Key patterns

- **Source links**: sourced data renders its source inline. Never state a number
  on a page without the link a resident can click at a hearing.
- **Provenance blocks**: every bulk registry renders `provenance_html("MY_DF")`,
  which flags a dataset past its churn-based shelf life instead of quietly
  captioning it.
- **Register vs search**: a link to a public database and a link to a pre-built
  search query are different claims — render the distinction (`permit_lookup`).
- **Cross-links**: end a section with a "See also" pointing at the related page.
- **Downloadable outputs**: calculators and generators end with a download —
  `.txt`, `.csv`, or Print/Save-as-PDF via the `@media print` stylesheet — so
  users can take results to meetings.
- **Client-side interactivity is plain JS**, embedded in the page with its data
  as one JSON blob (`build_start_here()` is the reference implementation). No
  frameworks, no external requests: a strict no-dependency page loads instantly
  for someone on a phone in a council parking lot.

## Deleted code, and what is NOT legacy

The retired Streamlit tree was **deleted** in August 2026: `app.py`,
`src/ui/` (26 tab modules), `.streamlit/`, `assets/style.css`,
`Restart GridWatch AI.command`, `src/helpers.py`, `src/scripts_letters.py`,
`src/site_builder.py`, `src/deal_scorecard.py`, and twelve `src/services/`
fetchers. `git log` has them if a rendering decision ever needs archaeology,
but they are not reference material: each held a stale twin of logic that
lives in `build_site.py`, and **the twin in `build_site.py` is the source of
truth**. Do not restore one to "check" the site against it.

All of them, plus `requirements-site.txt` (superseded by
`requirements-build.txt`), **reappeared on disk as untracked files** while the
repo sat in iCloud — the sync replaying deletions it had never fully applied.
They were removed again on 2026-08-30 along with the move out of the container.
If you ever see `src/ui/` or a `src/services/` fetcher on disk again, it is
sync residue, not a revival: delete it. `git ls-files` is the authority on what
this repo contains, not `ls`.

An earlier version of this file listed five things as legacy that are in fact
**live build dependencies**. Verify before you delete:

| Module | Why it is live |
|---|---|
| `src/services/officials.py` | `build_official_scorecard()` → `scorecard.html` |
| `src/local_officials.py` | `build_officials()` → `officials.html` |
| `src/impact_model.py` | imported by `src/briefs.py`, which is on the build path |
| `src/research/` | standalone CLI: `python -m src.research.dc_finder` → `research_output/` |
| `parse_reports.py` | standalone CLI: extracts metrics from report PDFs |

The last two are not on the build path and never were — they are local research
tooling, which is a different thing from dead code. They are what
`requirements.txt` exists for; the site itself builds off
`requirements-build.txt`.

To check reachability rather than trust this list, walk the import graph from
`build_site.py` plus every file in `scripts/` with `ast`, and diff it against
`git ls-files '*.py'`. That is how the five above were caught.
