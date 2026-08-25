# GridWatch AI

**The energy, water, and carbon behind LLM token usage — from a single prompt to the global data-center grid.**

GridWatch AI is an open-source static site that gives communities, researchers, and policymakers the data they need to understand and negotiate the impact of AI data centers. It combines per-token energy modeling, a sourced moratorium and project tracker, corporate environmental disclosures, and actionable negotiation tools into a single platform.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

### 🌐 [aigridwatch.com](https://aigridwatch.com) — live site · [Start here](https://aigridwatch.com/start-here)

- 🧮 [Data center impact calculator](https://aigridwatch.com/impact) — electricity, water, carbon, and rate impact for any facility size, in your state
- 📋 [Moratorium tracker](https://aigridwatch.com/moratoriums) — 333 U.S. data center moratoriums and community actions across 39 states, each sourced and dated — **open data ([JSON](https://aigridwatch.com/data/moratoriums.json) · [CSV](https://aigridwatch.com/data/moratoriums.csv)), CC BY 4.0**
- 🏛️ [Model CBA clause library](https://aigridwatch.com/cba-clauses) · [Questions to ask at your hearing](https://aigridwatch.com/hearing-questions)
- ⚕️ [The health risks of data centers](https://aigridwatch.com/health-risks), sourced · [Why your electric bill is going up](https://aigridwatch.com/bills)
- 📍 [State briefings — all 50 states + D.C.](https://aigridwatch.com/states/) · [Methodology](https://aigridwatch.com/methodology) — every coefficient, its source, and its caveats

---

## Why this exists

A hyperscaler shows up with a $2B data center proposal. Your planning commission has 30 days to respond. The developer has a team of consultants and lawyers. Your community has a Facebook group and a lot of questions.

**GridWatch AI closes that information gap.** Every number is sourced. Every claim links to the primary data. The same models and coefficients that power the free tool are available for communities to use in hearings, public comment periods, and CBA negotiations.

---

## Features

### Community advocacy (lead tabs)

| Tab | What it does |
|-----|-------------|
| **Negotiation toolkit** | Data Dividend Calculator (the Alaska model for data centers), model CBA clause library with copy-paste legal language, real-world deal database, leverage scorecard, and consulting intake form |
| **Community & backlash** | Automated Google News feed of communities affected by data centers (last 7 days), Reddit discussion tracker, and links to opposition groups nationwide |
| **Your utility bill** | Interactive explainer showing how wholesale MW capacity charges land on residential bills, Duke Energy curtailment study, residential vs. commercial vs. industrial rate comparisons, and academic literature on rate impacts |
| **States & officials** | State-by-state data center legislation tracker (300+ bills filed in 2026 across 30 states), elected official lookup, and case studies from towns that have fought or negotiated |

### Industry landscape

| Tab | What it does |
|-----|-------------|
| **Data centers** | Interactive campus map with facility details by operator, community siting evaluator, and ERCOT/PJM demand queue analysis |
| **Corporate profiles** | Environmental disclosures from Google, Meta, Microsoft, Amazon, and others; live SEC EDGAR XBRL financial data (Net Income, CapEx, Assets); water and carbon commitments; AWS, Microsoft, and Meta deep-dives |
| **Macro outlook** | IEA data-center electricity trajectory (415 → 945 TWh), Pew Research rural shift study, AI's rising share of global energy demand |

### Learn & reference

| Tab | What it does |
|-----|-------------|
| **Learn & simulate** | Educational explainers on how AI inference uses energy, marginal vs. average grid intensity, and an interactive AI data center siting sandbox simulator |
| **Technical deep-dive** | Per-token footprint calculator, live ML.ENERGY model benchmarks, source comparison matrix (first-party vs. benchmark, log scale), and grid carbon timing tools — all in nested subtabs |
| **Blog & methodology** | Long-form analysis posts and full methodology with every coefficient, its source link, and scope caveats |

### Standalone pages

| Page | Route | What it does |
|------|-------|-------------|
| **Consulting** | `/consulting` | Landing page for community consulting services with success-fee pricing, three service tiers, credibility metrics, and a full intake form |

---

## Quickstart

### Prerequisites

- Python 3.10+
- pip

### Install and run

```bash
git clone https://github.com/MickB74/AIGridTracker.git
cd AIGridTracker
pip install -r requirements-build.txt
python3 build_site.py
```

That writes `web/` — ~495 static pages. Serve it with any static server
(`python3 -m http.server -d web 8777`) and open `http://localhost:8777`.

Set `NEWS_FREEZE=1` to skip the live news fetch and build from the committed
cache.

### Optional API keys

Some features require API keys. The app degrades gracefully without them — no tab will crash.

| Key | What it unlocks | Where to get it |
|-----|----------------|-----------------|
| **EIA API key** | Hourly grid fuel mix and carbon intensity via EIA-930 (any US ISO — ERCOT, CAISO, PJM, MISO, ISO-NE, NYISO, SPP, BPA) | [eia.gov/opendata](https://www.eia.gov/opendata/) |
| **PJM API key** | Real-time 5-minute marginal emissions and fuel-mix generation from PJM Data Miner 2 | [dataminer2.pjm.com](https://dataminer2.pjm.com/) |

Enter keys in the app's sidebar or set them in a `.env` file:

```bash
EIA_API_KEY=your_key_here
PJM_API_KEY=your_key_here
```

---

## Project structure

```
AIGridTracker/
├── build_site.py               # The static-site generator — the whole product
├── web/                        # Generated output, committed and served by Vercel
├── requirements-build.txt      # Build dependencies (stdlib + pandas + markdown)
│
├── assets/
│   └── hero.png                # Hero image and OG-card fallback
│
├── src/
│   ├── constants.py            # All coefficients, emission factors, sources registry
│   ├── helpers.py              # Formatting utilities (human_energy, human_water, src_link)
│   ├── blog_content.py         # Blog post content
│   │
│   ├── services/               # External API integrations (all cached, all fail gracefully)
│   │   ├── eia.py              # EIA-930 hourly fuel mix → average gCO2/kWh
│   │   ├── pjm.py              # PJM Data Miner 2 marginal emissions + fuel-mix
│   │   ├── ercot.py            # ERCOT large load interconnection queue
│   │   ├── mlenergy.py         # ML.ENERGY leaderboard scraper (per-model inference energy)
│   │   ├── news.py             # Google News RSS community stories feed
│   │   ├── reddit.py           # Reddit discussion tracker (JSON API)
│   │   ├── officials.py        # Elected official lookup
│   │   ├── sec_xbrl.py         # SEC EDGAR XBRL company facts (financials)
│   │   └── secrets.py          # API key loading from .env (legacy)
│   │
│   ├── research/               # Data collection and parsing tools
│   │   ├── dc_finder.py        # Data center facility discovery
│   │   ├── edgar.py            # SEC EDGAR filing parser
│   │   ├── extract.py          # Environmental report metric extraction
│   │   ├── firstparty.py       # First-party disclosure scraper
│   │   ├── gazetteer.py        # Geographic facility matching
│   │   └── geocode.py          # Geocoding utilities
│   │
│   └── ui/                     # Tab rendering modules (one file per tab)
│       ├── toolkit_tab.py      # Negotiation toolkit — CBA calculator, model clauses
│       ├── learn_tab.py        # Educational explainers
│       ├── corporate_tab.py    # Corporate profiles and SEC data
│       ├── bills_tab.py        # Utility bill explainer
│       ├── dc_tab.py           # Data center map and profiles
│       ├── studies_tab.py      # State legislation tracker
│       ├── news_tab.py         # Community news feed
│       ├── sandbox_tab.py      # AI siting simulator
│       ├── compare_tab.py      # Source comparison matrix
│       ├── grid_tab.py         # Grid carbon timing tools
│       ├── officials_tab.py    # Elected official lookup
│       ├── calc_tab.py         # Footprint calculator
│       ├── macro_tab.py        # Macro outlook
│       ├── live_tab.py         # Live ML.ENERGY benchmarks
│       ├── blog_tab.py         # Blog posts
│       └── method_tab.py       # Methodology and citations
│
├── parse_reports.py            # CLI: extract metrics from Google/Meta environmental reports
└── research_output/            # Cached facility research data (JSON)
```

---

## Live data feeds

| Feed | Provider | Update frequency | Key required |
|------|----------|-----------------|--------------|
| Hourly fuel mix / carbon intensity | EIA-930 API v2 | Hourly | Yes (free) |
| 5-min marginal emissions by node | PJM Data Miner 2 | 5-minute | Yes (free) |
| Fuel-mix generation by type | PJM Data Miner 2 | Hourly | Yes (free) |
| Per-model inference energy | ML.ENERGY leaderboard (GitHub JSON) | Daily scrape, cached 24h | No |
| Community news stories | Google News RSS | On page load | No |
| Reddit discussions | Reddit JSON API | On page load | No |
| SEC EDGAR company facts | SEC XBRL API | On demand, cached | No |

News and video feeds are fetched at build time and cached in `data/*_cache.json` (6h TTL); a failed fetch falls back to the committed cache. The published pages make no runtime requests.

---

## Per-query energy coefficients

GridWatch AI tracks energy per query from both first-party disclosures and independent benchmarks:

### First-party disclosures

| Source | Model | Energy (Wh/query) | Scope |
|--------|-------|--------------------|-------|
| Google Environmental Report (2025) | Gemini 2.0 | 0.24 (full-stack), 0.10 (chip-only) | Accelerator + host + cooling |
| OpenAI / Altman (Jan 2025) | ChatGPT avg | 0.34 | Full-stack (methodology unpublished) |

### Benchmark studies

| Source | Model | Energy (Wh/query) | Notes |
|--------|-------|--------------------|-------|
| How Hungry is AI? (2025) | GPT-4o | 0.55 | arXiv:2505.09598 |
| How Hungry is AI? (2025) | Claude 3.5 Sonnet | 0.40 | Anthropic API benchmark |
| Epoch AI (2025) | Llama 3.1 405B | 0.97 | A100 cluster, ~1000 output tokens |
| Epoch AI (2025) | Claude 3 Opus | 0.85 | High-parameter density estimate |
| Epoch AI (2025) | Llama 3.1 70B | 0.35 | A100, mid-size open model |
| Epoch AI (2025) | Claude 3.5 Haiku | 0.10 | Distilled small model |

The app distinguishes **marginal** (load-shifting — what happens when you add load to the grid) from **average** (fuel-mix — what the grid is currently doing) carbon intensity. Both are available in the Grid Timing tools.

---

## Design system

The app uses the **AIGridStatus design system**, defined in [`assets/style.css`](assets/style.css):

| Token | Value | Usage |
|-------|-------|-------|
| **Primary font** | Space Grotesk | UI text, headings, buttons |
| **Editorial font** | Newsreader | Alert callouts, editorial content |
| **Data font** | IBM Plex Mono (tabular-nums) | Metrics, code blocks, numeric values |
| **Brand teal** | `#2DD4BF` | Links, active states, slider tracks, hover accents |
| **Warm orange** | `#F98866` | Primary buttons, community spotlight labels |
| **Amber** | `#F5B841` | Warning states |
| **Coral** | `#E4785A` | Secondary warm accent |
| **Surface 0** | `#0A0E14` | Page background |
| **Surface 1** | `#10151D` | Cards, tab bar, expanders |
| **Surface 2** | `#161D28` | Inputs, hover states, code blocks |
| **Surface 3** | `#1F2835` | Tooltips, elevated elements |
| **Border** | `#28313F` | Default borders |
| **Border hover** | `#3A4656` | Hover borders |
| **Text primary** | `#EAF0F7` | Headings, body text |
| **Text secondary** | `#A4B0C0` | Descriptions, subtitles |
| **Text muted** | `#6B7789` | Captions, labels, metadata |

---

## Consulting services

GridWatch AI powers a community consulting practice using a **success-fee model** — communities don't pay unless the deal improves.

| Service | What's included |
|---------|----------------|
| **Impact analysis** | Energy load modeling (PJM, EIA-930), water consumption by cooling type, residential rate projections, counter-analysis to developer's economic study |
| **Deal structuring** | Custom CBA drafting, Data Dividend fund design, tax abatement analysis, clawback provisions, decommissioning bond sizing |
| **Hearing support** | Expert testimony at planning/zoning hearings, data presentations, talking points for officials, media briefing materials, post-approval compliance monitoring |

**Pricing:** Free 60-minute initial consultation. Full engagements use a success fee (small percentage of new benefits secured, capped). Flat project fee available for grant-funded work.

The intake form is available in-app (Negotiation Toolkit tab) and as a standalone page at `/consulting`.

---

## Development

### Verify before committing

```bash
# Syntax check + full rebuild
python3 -m py_compile build_site.py src/constants.py && NEWS_FREEZE=1 python3 build_site.py

# Prove committed web/ still matches committed data
python3 scripts/check_site_fresh.py --strict
```

### Conventions

- **Coefficients belong with their sources.** Every numeric value gets a source key in the `SOURCES` dict (`constants.py`) and a citation link via `src_link()`.
- **Marginal vs. average.** Always distinguish load-shifting (marginal) from fuel-mix (average) carbon intensity in UI labels and documentation.
- **Graceful degradation.** Build-time fetches must fall back to the committed cache; a news outage never fails a build.
- **No secrets in code.** `FORMSPREE_ID` and the analytics URL are public by design; anything else comes from the environment.
- **`web/` is committed output.** Rebuild it in the same commit as any data change.

### Adding a new page

1. Write a `build_<name>()` in `build_site.py` that returns `page(...)` output.
2. Call it from `main()`, add it to the nav group it belongs to and to the sitemap.
3. Rebuild and commit `web/` alongside the change.

### Adding a new data source

1. Add the coefficient to the appropriate dict in `src/constants.py`.
2. Add the source citation to `SOURCES` with a URL.
3. Use `src_link("key")` anywhere you reference the number in UI text.

---

## Contributing

Contributions welcome. The most impactful areas:

- **New data sources** — state-level legislation databases, utility rate APIs, corporate disclosures
- **CBA examples** — documented community benefit agreements with measurable outcomes
- **Model coefficients** — published per-token or per-query energy/water/carbon measurements
- **Accessibility** — screen reader support, keyboard navigation, color contrast
- **Bug reports** — especially around API failures, data rendering, or mobile layout issues

Please open an issue before starting work on large features.

---

## License

MIT

---

## Acknowledgments

- [EIA Open Data](https://www.eia.gov/opendata/) — hourly grid generation data
- [PJM Data Miner 2](https://dataminer2.pjm.com/) — real-time marginal emissions
- [ML.ENERGY Leaderboard](https://ml.energy/leaderboard) — per-model inference benchmarks
- [Epoch AI](https://epoch.ai/) — token-level energy coefficient research
- [IEA](https://www.iea.org/) — global data-center electricity outlook
- [Pew Research Center](https://www.pewresearch.org/) — rural data center community impact studies
- Google, Meta, Microsoft, and OpenAI — first-party environmental disclosures
- The **345+ community groups** across 37 states whose advocacy work this tool supports
