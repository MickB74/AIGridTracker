# CLAUDE.md — GridWatch AI

Context for AI agents working in this repo.

## What this is

A Streamlit app that (1) estimates the energy, water, and carbon footprint of LLM token usage — from a single prompt to the global data-center grid — and (2) serves as a community advocacy platform with CBA negotiation tools, data dividend calculators, PUC directories, executive directories, and policy templates. The audience is community members facing data center development who need data and tools to negotiate effectively.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Port defaults to 8501; override with `--server.port=XXXX`. The `.streamlit/config.toml` sets `headless = true`.

## Verify before committing

```bash
python3 -m py_compile app.py
python3 -c "from streamlit.testing.v1 import AppTest; \
  at=AppTest.from_file('app.py',default_timeout=90).run(); \
  assert not at.exception, at.exception; print('smoke OK')"
```

Always run both checks. The smoke test catches runtime import errors and widget crashes that py_compile misses.

## Architecture

### Entrypoints

- **app.py** — Single page. Hero section, news carousel, sidebar, and 11 top-level tabs (some with stacked sub-modules). Tab order follows the advocacy flow: Community & advocacy → Industry landscape → Learn → Technical deep-dive → Reference → Business.

### Sidebar (app.py)

- **My Community** — state selectbox (`key="my_state"`); when set, shows quick facts and stores `st.session_state["my_state_abbrev"]`. Tabs read these keys to pre-filter (officials, PUC, moratoriums, impact calculator, meeting prep). Default state selections should check `st.session_state.get("my_state", ...)`.
- **Quick Search** — free-text search across `MORATORIUMS_DF`, `EXECUTIVES_DF`, `DC_SITES_DF`, `STATE_PUCS_DF`, rendered grouped by type in the sidebar.

### Tab layout (app.py)

**The app is the workshop; `web/` is the encyclopedia.** The static site owns
reference and lookup content (state briefings, company profiles, blog, health
risks, moratorium tracker) because it is shareable, indexable, and has no cold
start. The Streamlit app owns what a static page can't do: stateful wizards,
document generators, live fetches, and interactive models. **Don't add
reference/explainer content to the app — add it to `build_site.py`.** The
sidebar links out to the site's key pages.

Seven top-level tabs — the first five are all "do something", in rough order
of how urgent the user's situation is:

| Tab | Module(s) | Purpose |
|-----|-----------|---------|
| Start here | `start_here_tab` | Guided 5-step wizard for someone facing a new proposal: situation/stage/hearing date → LLC unmasking lookup → impact estimate + `CBA_BENCHMARKS` → stage playbook (`PROJECT_STAGES`, dated countdown when a hearing date is set) → action kit (PDF pack with comment scripts/letters/`OUTREACH_TIPS`, EN/ES flyer + petition sheet, social posts, downloadable campaign site) |
| Negotiation toolkit | `toolkit_tab` | CBA templates, data dividend calculator, model clauses, meeting checklist, meeting prep generator (downloadable brief) |
| Estimate & simulate | `impact_tab` + `sandbox_tab` | Local impact calculator + interactive siting simulator |
| Token calculator | `calc_tab`, `live_tab`, `compare_tab`, `grid_tab`, `method_tab` (nested sub-tabs) | Per-token footprint model, live benchmarks, source comparison, grid timing, and the source coefficients behind them |
| Live intel | `news_feed_tab` + `news_tab` + `monitors_tab` | Top stories, community backlash / flashpoints / `TOWN_CASES`, per-operator news feed, market monitors + report-freshness checker. Static content was stripped out of `news_tab`: the hyperscaler scorecard and spend estimator moved to `corporate_tab`, and the moratorium tracker is now a link-out to the site's `moratoriums.html` |
| Reference | `dc_tab`, `corporate_tab`, `studies_tab` + `officials_tab` (nested sub-tabs) | Background reading and directories **staged for migration to the static site** — see below |
| Consulting | `consulting_tab` | Consulting pitch + intake form |

The Reference tab is a holding pen, not a permanent home. Its sub-tabs cover
content the site doesn't publish yet (interactive maps, live EIA/SEC/Yahoo
Finance data, the Congress + PUC directories). As each is ported to
`build_site.py`, drop the sub-tab and link out instead. Already migrated:
`bills_tab` → `web/bills.html`, `macro_tab` → `web/outlook.html`,
`learn_tab` → `web/learn.html`, PUC directory → `web/puc.html`,
executives/megaprojects → `web/executives.html`, 50-state profiles /
operators / ERCOT queue / SEC 10-K / grid operators → `web/data-centers.html`,
environmental comparison / deep-dives / spend estimator →
`web/environment.html`. The Siting Evaluator (interactive geocoding tool)
remains in `learn_tab.py` but is accessed via the Streamlit app link on the
learn page.

`blog_tab` and `health_tab` were removed — `web/blog/` and
`web/health-risks.html` render the same `BLOG_STORIES` / `HEALTH_RISKS` data.
`build_health_pdf` is still used by the site generator.

Stacked tabs (Estimate & simulate, Live intel) have a "This tab contains…"
caption at the top and a divider between modules. Long modules have an "On
this page" expander for navigation.

### Data layer

- **src/constants.py** (~1,700 lines) — All static data, coefficients, and registries. Major datasets:
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
    Maintained by `scripts/verify_moratoriums.py` (audits what is published)
    and `scripts/scan_moratorium_candidates.py` (finds what is missing) — see
    Data maintenance scripts below.
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
  - `COMPANY_CONCESSIONS` — per-operator negotiation intel: documented concessions won elsewhere + a strategy read; feeds the meeting brief / action pack
  - `CBA_BENCHMARKS` — what similar communities won (Start here impact step)
  - `OUTREACH_TIPS` — platform-by-platform digital organizing playbook (Nextdoor/Ring/Facebook/WhatsApp/forums)
  - `HEALTH_RISKS` — six health-risk panels (air/noise/light/bills/water/climate); every fact carries a SOURCES key; rendered by `health_tab` and `build_health_pdf`
  - Environmental report headline data for all four hyperscalers:
    `GOOGLE_*` (FY2025), `META_*` (FY2024), `MICROSOFT_ENV_HEADLINE` (FY2025),
    `AWS_ENV_HEADLINE` (CY2025). Microsoft/AWS don't break out DC-only
    electricity — those TWh and location-based Scope 2 values are estimates
    derived from reported growth rates; keep the "(est.)" markers when
    displaying them. When a new report edition lands, update the headline
    dict, its `SOURCES` entry, and the `REPORT_REGISTRY` year in
    `src/services/report_check.py`.
  - Grid coefficients, model parameters, ERCOT large-load data

- **src/helpers.py** — `human_energy()`, `human_water()`, `src_link()`, plus `freshness_caption(registry_key)` / `render_freshness(st, registry_key)` for dataset provenance (see Data sourcing below). `render_freshness` takes `st` as an argument so the module stays Streamlit-free at import time.

- **src/impact_model.py** — `estimate_facility_impact(mw, state, cooling)`: the single shared facility-impact model (PUE/water by cooling type, homes-equivalent, investment/data-dividend economics). Used by the impact calculator, meeting prep generator, and Start here wizard — never duplicate these coefficients inline in a tab.

- **src/local_officials.py** — Three-tier local-official resolution, pure
  functions, no Streamlit: `curated(locality, state)` (verified rows from
  `LOCAL_OFFICIALS_DF`/`LOCAL_BODIES_DF`), `covered_localities()` for the
  picker, `build_lookup_links(state, locality)` (deterministic directory links,
  full 51-state coverage), and `verification_note()` for the provenance footer.
  Tier 2 (state legislators) lives in `services/openstates.py`. The tiers are
  not interchangeable — OpenStates excludes mayors, so it can never substitute
  for tier 1.

- **src/briefs.py** — `build_meeting_brief_data(state, operator, meeting_type, mw)`: structured meeting-brief assembly (sections of kv/bullets/numbered/advice) plus the `MEETING_ADVICE` strategy dict. `build_meeting_brief(...)` renders it as plain text (toolkit's meeting prep generator, Start here text download). Output is plain text — don't escape `$` here.

- **src/pdf_pack.py** — `build_action_pack_pdf(state, stage, stage_info, brief_data, dated_moves=, scripts=, letters=, social_posts=, outreach_tips=)`: branded PDF rendering of the Start here action pack (fpdf2; natively drawn logo, header/footer with page numbers), plus `build_flyer_pdf(...)`: one-page EN/ES community flyer + petition/sign-up sheet. Consumes `build_meeting_brief_data()` output; core fonts are cp1252-only, so all text goes through its `_latin1()` sanitizer (drops emoji). Layout gotchas the helpers already handle: call `_ensure_room()` before any row that captures `get_y()` (else orphaned bullets at page breaks), and multi_cell leaves x at the right edge (paragraph() resets it).

- **src/scripts_letters.py** — `build_comment_scripts(state, mw, imp, bill, operator, lang)` (2-minute speech + 30-second topic scripts, EN/ES), `build_letters(...)` (records request / PUC inquiry / council letter), `build_social_posts(...)` (Nextdoor/Ring/Facebook, numbers pre-filled). Pure text, no Streamlit.

- **src/site_builder.py** — `build_campaign_site(...)`: self-contained single-file campaign `index.html` (inline CSS, OG tags, no external assets) users host on Netlify Drop / GitHub Pages.

### Static site (web/ — Vercel front door)

- **build_site.py** — Python static-site generator; renders `web/` from the same constants registries: landing page, 51 enriched state one-pagers (`states/<slug>.html`), sourced health-risks page, moratorium tracker (`moratoriums.html`), story tracker (`story-tracker.html` — every archived community-impact headline grouped by locality, see below), client-side impact calculator (`impact.html`), utility-bill explainer (`bills.html`), electricity outlook (`outlook.html`), data-center explainer/glossary (`learn.html`), PUC directory (`puc.html`), executives/megaprojects (`executives.html`), data-center market data (`data-centers.html` — 50-state profiles, operators, ERCOT queue, SEC 10-K, grid operators/FERC), hyperscaler environmental impact (`environment.html` — comparison, spend estimator, deep-dives, revenue growth), company scorecards, blog posts, health infographic PDF, sitemap/robots/vercel.json. Blog posts are markdown converted to HTML via the `markdown` library; Streamlit `\$` escapes are stripped automatically. Regenerate with `python3 build_site.py` (env overrides: `SITE_URL`, `APP_URL`) and commit the output whenever constants change — Vercel serves `web/` as-is (Root Directory = `web`, framework "Other", no build step). Preview locally with the `static-site` entry in `.claude/launch.json` (port 8777). The Streamlit app is NOT hosted on Vercel — the site links to it via `APP_URL`.

- **src/story_tracker.py** — Pure grouping/summarization for the story tracker: `build_gazetteer()` (known localities from `DC_SITES_DF`/`LOCAL_BODIES_DF`/`MORATORIUMS_DF`, longest-name-first, excluding entries that collapse to a bare state name — see the code comment on `"Ohio (ballot measure)"`), `guess_locality(title, gazetteer)`, `group_stories(stories, min_for_summary=4)`. Each build, `build_site.py::_persist_story_candidates()` merges the same live-fetched community-impact feed used by `/news/` into `data/story_candidates.json` (dedup by link; `first_seen` is set once and kept, `last_seen` bumps on every re-fetch — this is what makes it a running archive rather than the news page's rolling 7-day window). Unlike `moratorium_candidates.json`/`project_candidates.json`, this queue is **not** a human-review gate — headlines publish straight to `story-tracker.html`, same as the live news feed already does, just with an "automated, not verified" caveat on the page. A locality with 4+ archived stories gets `summarize_group()`'s heuristic extractive summary (keyword/outlet counts, no LLM call) — that's the "AI summary" trigger.

### Services (src/services/)

External data fetchers. All must be cached with `@st.cache_data` and fail gracefully (return empty/None, never crash a tab).

| File | What it fetches |
|------|----------------|
| `eia.py` | EIA-930 live grid demand (requires API key) |
| `pjm.py` | PJM real-time marginal emissions (requires API key) |
| `ercot.py` | ERCOT large-load document scraping |
| `news.py` | Google News RSS feeds |
| `officials.py` | Congress/governor directory (Senate XML + @unitedstates project) |
| `openstates.py` | OpenStates v3 `/people.geo` — state legislators + Congress for a lat/lon. Free key (`OPENSTATES_API_KEY`). Per OpenStates' own spec, **governors and mayors are excluded** — say so in the UI rather than implying town coverage. Returns `(rows, note)`; never raises |
| `mlenergy.py` | ML.ENERGY leaderboard benchmark data |
| `reddit.py` | Reddit community posts (from local parquet snapshot) |
| `sec_xbrl.py` | SEC XBRL financial data |
| `report_check.py` | Polls hyperscaler report pages for editions newer than tracked (`REPORT_REGISTRY` holds the tracked year per company; cached 24 h) |
| `secrets.py` | API key loading from `.env` or local config |
| `tracking.py` | Local usage analytics + newsletter signups (not a fetcher): `log_event()` appends JSON lines to `data/analytics/events.jsonl` (gitignored — subscriber emails are PII); `add_subscriber()` writes `subscribers.csv`. Wired to download buttons via `on_click=log_event`. The signup widget is `src/ui/newsletter.py::render_newsletter_signup(source)` (sidebar + Start here). Admin view: set `GRIDWATCH_ADMIN_KEY` env var and open the app with `?admin=<key>`. |

### Other files

- **parse_reports.py** — CLI tool to extract metrics from Google/Meta environmental reports into constants
- **assets/style.css** — Custom CSS (glass-card styling, dark theme, mobile breakpoints at 768/1024 px, expander + prose typography)
- **assets/hero.png** / **assets/logo.svg** — Header background image and logo
- **docs/marketing-plan.md** — Marketing plan (not rendered by the app)
- **data/reports/** — Source PDF reports
- **officials.json** — Cached officials data
- **reddit_corpus.parquet** — Reddit discussion snapshot

## Conventions

### Data sourcing
- Every numeric claim gets a source key in `SOURCES` and a link via `src_link(key)`.
- **Every registry declares its freshness.** New bulk registries get an entry in `REGISTRY_PROVENANCE` (`src/constants.py`): `as_of`, `source`, `churn` (low/medium/high), and a plain-language `caveat`. Render it with `render_freshness(st, "MY_DF")` in the app and `provenance_html("MY_DF")` in `build_site.py` — both flag a dataset past its churn-based shelf life (low 36mo / medium 18mo / high 9mo) instead of quietly captioning it. Per-row `source` + `as_of` (the `LOCAL_*` pattern) is better where rows are added individually; `REGISTRY_PROVENANCE` is for datasets compiled in bulk.
- **Never test a DataFrame cell for emptiness with `if v` or `str(v) != "nan"`.** A missing object-column value is `None` on pandas 2.x but `NaN` on 3.x — and `NaN` is truthy. Use `has_value(v)` from `src/constants.py` (or `cell(v)` in `build_site.py`, which also escapes and falls back to an em-dash). Both bugs this caused shipped to production: the literal word "None" in the Tenant column on five state pages, and every "unverified" marker vanishing from the search index. `web/` is generated on whatever pandas the builder has, so this diverges silently.
- **Never invent an `as_of`.** Set it to `None` if the verification date isn't known — it renders as "No verification date recorded" and counts as stale. A fabricated date is worse than no date: it invites a citation the user can't defend at a hearing.
- **Derive time-sensitive status, never store it.** A registry row whose truth expires (a moratorium term, a comment deadline, a rate case) gets the end date as data and a pure function that computes the current state from it — `moratorium_status()` is the reference implementation. Storing "Enacted" means the page keeps asserting it forever; deriving it means the daily CI rebuild corrects the page with no edit. Consumers must read the derived column (`effective_status`), not the stored one.
- Distinguish **marginal** (load-shifting) vs **average** (fuel-mix) carbon intensity.
- Shared registries live in `constants.py` — never duplicate data inline in tab modules. If two tabs need the same data, one filters the shared DataFrame.

### Data maintenance scripts (`scripts/`)

Stdlib-only on purpose — they run in CI off `requirements-build.txt`, which excludes `requests` and `streamlit`. Neither script edits a registry: promotion and verification are human steps, because that is where `source` and `as_of` come from.

| Script | What it does |
|---|---|
| `verify_moratoriums.py` | Audits `MORATORIUMS_DF` **and `MORATORIUM_OUTCOMES`**: lapsed terms, dead source links (403/405/429 reported as *blocked*, not dead), rows with no source, `as_of` older than 180 days, and time-limited rows with no recorded end date. `--offline` skips link checks, `--out`/`--json` write the worklist, `--strict` exits non-zero. |
| `scan_moratorium_candidates.py` | Mines the Google News RSS feed for moratoriums not yet tracked and appends them to `data/moratorium_candidates.json`. Entries keep `first_seen`; anything a human marks `"status": "dismissed"` is never re-raised. |
| `scan_locality_candidates.py` | Mines `data/story_candidates.json` (the story tracker archive) for towns/counties that keep recurring in unlocalized headlines but aren't in the locality gazetteer yet, and appends them to `data/locality_candidates.json`, capped at `--max-new` (default 39) newly-surfaced names per run. Same never-writes-a-registry discipline as the moratorium scanner — promoting a candidate means researching its governing body (and, if it's had a real vote, the outcome) from primary sources and adding a `LOCAL_BODIES_DF`/`MORATORIUMS_DF` row by hand, then running `backfill_story_candidates.py --relabel` so its already-archived stories regroup. Runs daily as a step in `build-site.yml` (after the story archive itself refreshes), not the weekly moratorium job — it needs a fresh archive, not a fresh RSS fetch of its own. |

`.github/workflows/verify-moratoriums.yml` runs the moratorium/project scanners weekly and commits the queue. It deliberately does **not** fail the build — a stale row is a chore, not a broken deploy, and a weekly red X gets trained away. The signal is the committed diff in `data/` plus the job summary. `scan_locality_candidates.py` runs daily instead, inside `build-site.yml`, for the same non-blocking reason.

### Network calls
- All external fetches use `@st.cache_data` with a TTL.
- Must fall back gracefully when offline or unauthenticated — never hard-crash a tab.
- No secrets in code. API keys come from UI text inputs or local `.env` via `secrets.py`.

### Adding a new data registry
1. Add the data to `src/constants.py` as a list of dicts + a `_DF = pd.DataFrame(...)` line.
2. Import the DataFrame in the relevant `src/ui/*_tab.py` module.
3. If the data needs a source citation, add entries to `SOURCES` first.

### Adding a new tab module
1. Create `src/ui/new_tab.py` with a `render_new_tab()` function.
2. Import it in `app.py` and add it to the `st.tabs()` call.
3. If stacking it with another module in an existing tab, add a "This tab contains…" caption.

## Streamlit gotchas

- **Dollar signs in markdown**: Streamlit renders `$...$` as LaTeX in `st.markdown()`, `st.info()`, `st.success()`, `st.warning()`, `st.error()`, `st.caption()`, and `help=` tooltips. Escape with `\\$` in these contexts. But `st.metric()` values/deltas, slider/input labels, and dataframe cell values do NOT render markdown — use plain `$` there.
- **Mermaid diagrams**: Streamlit does not render ```mermaid code fences. Use Streamlit-native layouts instead (`st.columns` + `st.container(border=True)` for flows, Altair charts for data).
- **Altair charts**: Import `altair as alt`. Use `st.altair_chart(chart, use_container_width=True)`.
- **Altair column names**: A dot in a DataFrame column name (e.g. `"Est. Spend ($B)"`) is parsed by Altair as a nested-field accessor and silently produces zeros. Use simple column names (`"Spend"`) and set display titles via `alt.X/Y/Tooltip(title=...)`.
- **Tab state**: All tabs render on every page load (not lazy). Keep expensive operations behind `@st.cache_data` or user-triggered buttons.
- **Tab bar overflow**: At 11 tabs the bar scrolls horizontally on narrow screens. Tab names should be short.
- **Scroll container**: Streamlit's scrollable element is `section.main`, not `window` — relevant for any browser automation or scroll-to JS.
- **No deep-linking**: Streamlit tabs don't support URL anchors. Users can't share a link to a specific tab.

## Key patterns

- **Glass cards**: Wrap sections in `st.markdown('<div class="glass-card">', unsafe_allow_html=True)` / `st.markdown('</div>', ...)`. Defined in `assets/style.css`.
- **Source links**: Always use `src_link('key')` from `src/helpers.py` — never hardcode URLs for sourced data.
- **Filterable dataframes**: Use `st.multiselect` for filters, then `df[df.col.isin(selected)]` before `st.dataframe()`. Use `st.column_config.LinkColumn` for clickable URLs.
- **Cross-links**: At the bottom of sections, use `st.info("**See also:** ...")` to point users to related tabs.
- **On-this-page navigation**: For tabs with 5+ sections, add a collapsed `st.expander("📑 On this page")` at the top listing all sections.
- **Metrics-first sections ("prime-time" style)**: Long-form sections lead with `st.metric` cards carrying the headline numbers + a one-sentence takeaway (`st.info`), with the full prose in a collapsed `st.expander("Read more — ...")`. Don't add new always-visible prose walls — follow this pattern.
- **Sidebar-aware defaults**: Widgets that filter by state should default from `st.session_state.get("my_state")` / `st.session_state.get("my_state_abbrev")` so the sidebar "My Community" selection flows through.
- **Downloadable outputs**: Calculators and generators end with `st.download_button` (text, CSV, or PDF via `src/pdf_pack.py`) so users can take results to meetings.
