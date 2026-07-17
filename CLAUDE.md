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

- **app.py** — Main page. Hero section, news carousel, and 10 top-level tabs (some with stacked sub-modules). Tab order follows the advocacy flow: Community & advocacy → Industry landscape → Learn → Technical deep-dive → Reference.
- **pages/consulting.py** — Secondary Streamlit page for consulting intake form.

### Tab layout (app.py)

| Tab | Module(s) | Purpose |
|-----|-----------|---------|
| Negotiation toolkit | `toolkit_tab` | CBA templates, data dividend calculator, model clauses, meeting checklist |
| Community & backlash | `news_tab` | Moratorium tracker, live news/Reddit, case studies |
| Your utility bill | `bills_tab` | Bill anatomy, rate impact, wholesale-to-retail flow |
| States & officials | `studies_tab` + `officials_tab` | State market profiles, Congress/governor directory, PUC directory |
| Data centers | `dc_tab` | Interactive map, market power, ERCOT queue, campuses, operators, executives, competitors, FERC response, 50-state stats, mega-projects |
| Corporate profiles | `corporate_tab` | Google/Meta/Microsoft/AWS environmental deep-dives, sustainability directors |
| Macro outlook | `macro_tab` | IEA forecasts, geographic shift analysis |
| Learn & simulate | `learn_tab` + `sandbox_tab` | Data center explainer + interactive siting simulator |
| Technical deep-dive | `calc_tab`, `live_tab`, `compare_tab`, `grid_tab` (nested sub-tabs) | Token calculator, live benchmarks, source comparison, grid timing |
| Blog & methodology | `blog_tab` + `method_tab` | Blog posts + source coefficients |

Three tabs stack two modules with a divider between them (States, Learn, Blog). Each has a "This tab contains…" caption at the top. The three longest tabs (Data centers, Toolkit, Learn) have an "On this page" expander for navigation.

### Data layer

- **src/constants.py** (~1,500 lines) — All static data, coefficients, and registries. Major datasets:
  - `SOURCES` — dict mapping source keys to `(name, url)` pairs; used by `src_link()` everywhere
  - `DATACENTERS_DF` — market-level power by phase (operational/UC/planned)
  - `DC_SITES_DF` — per-campus site table with operator/owner/tenant/LLC/attribution
  - `OPERATORS` / `OPERATORS_DF` — operator registry (tier, owner, model, LLCs)
  - `EXECUTIVES_DF` — 39 executives with company, title, category, focus, LinkedIn
  - `AI_COMPETITORS_DF` — SEC 10-K competitor analysis
  - `STATE_DC_DF` — 50-state facility count and TWh/year
  - `MEGA_PROJECTS_DF` — top 10 megaprojects under construction
  - `STATE_PUCS_DF` — 51 state PUC commissions with website and complaint links
  - `MORATORIUMS_DF` — data center moratorium/ban tracker
  - Google/Meta environmental report data (`GOOGLE_*`, `META_*`)
  - Grid coefficients, model parameters, ERCOT large-load data

- **src/helpers.py** — Three utility functions: `human_energy()`, `human_water()`, `src_link()`.

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
| `secrets.py` | API key loading from `.env` or local config |

### Other files

- **parse_reports.py** — CLI tool to extract metrics from Google/Meta environmental reports into constants
- **assets/style.css** — Custom CSS (glass-card styling, dark theme)
- **assets/hero.png** — Header background image
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
- **Tab state**: All tabs render on every page load (not lazy). Keep expensive operations behind `@st.cache_data` or user-triggered buttons.
- **Tab bar overflow**: At 10 tabs the bar scrolls horizontally on narrow screens. Tab names should be short.
- **No deep-linking**: Streamlit tabs don't support URL anchors. Users can't share a link to a specific tab.

## Key patterns

- **Glass cards**: Wrap sections in `st.markdown('<div class="glass-card">', unsafe_allow_html=True)` / `st.markdown('</div>', ...)`. Defined in `assets/style.css`.
- **Source links**: Always use `src_link('key')` from `src/helpers.py` — never hardcode URLs for sourced data.
- **Filterable dataframes**: Use `st.multiselect` for filters, then `df[df.col.isin(selected)]` before `st.dataframe()`. Use `st.column_config.LinkColumn` for clickable URLs.
- **Cross-links**: At the bottom of sections, use `st.info("**See also:** ...")` to point users to related tabs.
- **On-this-page navigation**: For tabs with 5+ sections, add a collapsed `st.expander("📑 On this page")` at the top listing all sections.
