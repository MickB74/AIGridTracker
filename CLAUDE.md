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

| Tab | Module(s) | Purpose |
|-----|-----------|---------|
| Start here | `start_here_tab` | Guided 5-step wizard for someone facing a new proposal: situation/stage/hearing date → LLC unmasking lookup → impact estimate + `CBA_BENCHMARKS` → stage playbook (`PROJECT_STAGES`, dated countdown when a hearing date is set) → action kit (PDF pack with comment scripts/letters/`OUTREACH_TIPS`, EN/ES flyer + petition sheet, social posts, downloadable campaign site) |
| Negotiation toolkit | `toolkit_tab` | CBA templates, data dividend calculator, model clauses, meeting checklist, meeting prep generator (downloadable brief) |
| Community & backlash | `news_tab` | Moratorium tracker + map, live news/Reddit, town case studies, 4-company environmental scorecard, spend estimator, report-freshness checker |
| Your utility bill | `bills_tab` | Bill anatomy, rate impact, wholesale-to-retail flow, curtailment research library |
| States & officials | `studies_tab` + `officials_tab` | State market profiles, Congress/governor directory, PUC directory |
| Data centers | `dc_tab` | Interactive map, market power, ERCOT queue, campuses, operators, executives, competitors, FERC response, 50-state stats, mega-projects |
| Corporate profiles | `corporate_tab` | Google/Meta/Microsoft/AWS environmental deep-dives, sustainability directors |
| Macro outlook | `macro_tab` | IEA forecasts, geographic shift analysis |
| Learn & simulate | `learn_tab` + `impact_tab` + `sandbox_tab` | Data center explainer + local impact calculator + interactive siting simulator |
| Technical deep-dive | `calc_tab`, `live_tab`, `compare_tab`, `grid_tab` (nested sub-tabs) | Token calculator, live benchmarks, source comparison, grid timing |
| Blog & methodology | `blog_tab` + `method_tab` | Blog posts + source coefficients |
| Consulting | `consulting_tab` | Consulting pitch + intake form |

Stacked tabs (States, Learn, Blog) have a "This tab contains…" caption at the top and a divider between modules. Long tabs (Data centers, Toolkit, Learn, Bills, News, Corporate) have an "On this page" expander for navigation.

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
  - `STATE_PUCS_DF` — 51 state PUC commissions with website and complaint links
  - `MORATORIUMS_DF` — data center moratorium/ban tracker
  - `MORATORIUM_OUTCOMES` — case-study outcomes (CBA secured / ban sustained / etc.)
  - `COMPANY_CONCESSIONS` — per-operator negotiation intel: documented concessions won elsewhere + a strategy read; feeds the meeting brief / action pack
  - `CBA_BENCHMARKS` — what similar communities won (Start here impact step)
  - `OUTREACH_TIPS` — platform-by-platform digital organizing playbook (Nextdoor/Ring/Facebook/WhatsApp/forums)
  - Environmental report headline data for all four hyperscalers:
    `GOOGLE_*` (FY2025), `META_*` (FY2024), `MICROSOFT_ENV_HEADLINE` (FY2025),
    `AWS_ENV_HEADLINE` (CY2025). Microsoft/AWS don't break out DC-only
    electricity — those TWh and location-based Scope 2 values are estimates
    derived from reported growth rates; keep the "(est.)" markers when
    displaying them. When a new report edition lands, update the headline
    dict, its `SOURCES` entry, and the `REPORT_REGISTRY` year in
    `src/services/report_check.py`.
  - Grid coefficients, model parameters, ERCOT large-load data

- **src/helpers.py** — Three utility functions: `human_energy()`, `human_water()`, `src_link()`.

- **src/impact_model.py** — `estimate_facility_impact(mw, state, cooling)`: the single shared facility-impact model (PUE/water by cooling type, homes-equivalent, investment/data-dividend economics). Used by the impact calculator, meeting prep generator, and Start here wizard — never duplicate these coefficients inline in a tab.

- **src/briefs.py** — `build_meeting_brief_data(state, operator, meeting_type, mw)`: structured meeting-brief assembly (sections of kv/bullets/numbered/advice) plus the `MEETING_ADVICE` strategy dict. `build_meeting_brief(...)` renders it as plain text (toolkit's meeting prep generator, Start here text download). Output is plain text — don't escape `$` here.

- **src/pdf_pack.py** — `build_action_pack_pdf(state, stage, stage_info, brief_data, dated_moves=, scripts=, letters=, social_posts=, outreach_tips=)`: branded PDF rendering of the Start here action pack (fpdf2; natively drawn logo, header/footer with page numbers), plus `build_flyer_pdf(...)`: one-page EN/ES community flyer + petition/sign-up sheet. Consumes `build_meeting_brief_data()` output; core fonts are cp1252-only, so all text goes through its `_latin1()` sanitizer (drops emoji). Layout gotchas the helpers already handle: call `_ensure_room()` before any row that captures `get_y()` (else orphaned bullets at page breaks), and multi_cell leaves x at the right edge (paragraph() resets it).

- **src/scripts_letters.py** — `build_comment_scripts(state, mw, imp, bill, operator, lang)` (2-minute speech + 30-second topic scripts, EN/ES), `build_letters(...)` (records request / PUC inquiry / council letter), `build_social_posts(...)` (Nextdoor/Ring/Facebook, numbers pre-filled). Pure text, no Streamlit.

- **src/site_builder.py** — `build_campaign_site(...)`: self-contained single-file campaign `index.html` (inline CSS, OG tags, no external assets) users host on Netlify Drop / GitHub Pages.

### Services (src/services/)

External data fetchers. All must be cached with `@st.cache_data` and fail gracefully (return empty/None, never crash a tab).

| File | What it fetches |
|------|----------------|
| `eia.py` | EIA-930 live grid demand (requires API key) |
| `pjm.py` | PJM real-time marginal emissions (requires API key) |
| `ercot.py` | ERCOT large-load document scraping |
| `news.py` | Google News RSS feeds |
| `officials.py` | Congress/governor directory (Senate XML + @unitedstates project) |
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
- Distinguish **marginal** (load-shifting) vs **average** (fuel-mix) carbon intensity.
- Shared registries live in `constants.py` — never duplicate data inline in tab modules. If two tabs need the same data, one filters the shared DataFrame.

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
