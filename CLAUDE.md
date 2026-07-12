# CLAUDE.md — GridWatch AI

Context for AI agents working in this repo.

## What this is
A Streamlit app estimating the energy, water, and carbon footprint of LLM token usage, from a single prompt to the global grid.

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Structure
- **app.py** — Main entrypoint coordinating tab navigation.
- **src/constants.py** — Registry for static data, coefficients (PJM, EIA, models), electricchoice, google_env_2026, and meta_env_2025 constants.
- **src/helpers.py** — Reusable UI styling, formatting, and helper functions (e.g. `src_link`).
- **src/ui/** — Individual dashboard tab components:
  - `calculator_tab.py`, `learn_tab.py`, `compare_tab.py`, `models_tab.py`, `grid_tab.py`, `dc_tab.py`, `community_tab.py`, `officials_tab.py`, `corporate_tab.py`, `methodology_tab.py`, `blog_tab.py`.
- **src/services/** — APIs and background fetch logic (EIA-930, PJM, secrets loading).
- **parse_reports.py** — CLI tool to extract environmental metrics from Google's 2026 and Meta's 2025 reports.

## Conventions
- Keep coefficients and their sources together; anything numeric gets a source in `SOURCES` (constants) and a link.
- Distinguish **marginal** (load-shifting) vs **average** (fuel-mix) intensity.
- Network calls are cached (`@st.cache_data`) and must fall back gracefully when offline or unauthenticated — never hard-crash a tab.
- No secrets in code. Use PJM key / EIA keys in UI or locally in `.env`.

## Verify before committing
```bash
python3 -m py_compile app.py
python3 -c "from streamlit.testing.v1 import AppTest; \
  at=AppTest.from_file('app.py',default_timeout=90).run(); \
  assert not at.exception, at.exception; print('smoke OK')"
```

