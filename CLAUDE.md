# CLAUDE.md — AI Token Footprint

Context for Claude Code when working in this repo.

## What this is
A Streamlit app estimating the energy, water, and carbon footprint of LLM token
usage, from a single prompt to the global grid. Single-file app (`app.py`) plus
`requirements.txt` and `README.md`.

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Structure (all in app.py)
- **Static data** at top: `QUERY_COEFFS`, `TOKEN_COEFFS`, `GRID_INTENSITY`,
  `IEA_OUTLOOK`, `GRID_CURVES`, `SOURCES`. Every number is sourced inline.
- **Live data**:
  - `load_mlenergy(slug)` — pulls the ML.ENERGY leaderboard's public compiled
    JSON from raw.githubusercontent, reduces to min-energy config per (model, GPU).
  - `pjm_marginal_co2(api_key, date, pnode_id)` — PJM Data Miner 2
    `fivemin_marginal_emissions` (lbs/MWh → gCO₂/kWh, hourly). Marginal signal.
  - `pjm_fuelmix_co2(api_key, date)` — PJM `gen_by_fuel` × `PJM_EMISSION_FACTORS`,
    generation-weighted average intensity.
  - `eia930_fuelmix_co2(api_key, date, respondent)` — EIA API v2
    `fuel-type-data` (hourly net gen by fuel type per BA) × `EIA_EMISSION_FACTORS`,
    generation-weighted average. One free key covers any US ISO (`EIA_RESPONDENTS`
    maps BA → label + IANA tz). Periods are UTC; localized to the BA's clock and
    filtered to the local calendar day before grouping by local hour.
  - `_pjm_get(...)` — shared Data Miner 2 request helper (base
    `https://api.pjm.com/api/v1/`, `Ocp-Apim-Subscription-Key` header,
    `datetime_beginning_ept=MM/DD/YYYY HH:MMto...` filter, `{items, totalRows,
    links}` envelope).
- **UI**: 6 `st.tabs` — Calculator, Compare sources, Live models, Grid timing,
  Macro outlook, Methodology.

## Conventions
- Keep coefficients and their sources together; anything numeric gets a source in
  `SOURCES` and a line in the Methodology tab.
- Distinguish **marginal** (load-shifting) vs **average** (fuel-mix) intensity.
- Network calls are cached (`@st.cache_data`) and must fall back gracefully when
  offline or unauthenticated — never hard-crash a tab.
- No secrets in code. The PJM key is entered in the UI (password field). For local
  dev you may set `PJM_API_KEY` in `.env` (see `.env.example`) and read it via
  `os.environ` — do not commit `.env`.

## Good next tasks
- Live water-by-hour on the Grid tab (per-ISO WUE).
- Wire remaining ISOs via WattTime (marginal MOER) or Electricity Maps for a
  marginal signal — EIA-930 (`eia930_fuelmix_co2`) already covers average across
  all US BAs.
- Optional env-var default for the PJM / EIA keys in local dev.
- Add tests for the parsers (`pjm_*`, `eia930_*`, `load_mlenergy`) using recorded
  fixtures.

## Verify before committing
```bash
python -m py_compile app.py
python -c "from streamlit.testing.v1 import AppTest; \
  at=AppTest.from_file('app.py',default_timeout=90).run(); \
  assert not at.exception, at.exception; print('smoke OK')"
```
