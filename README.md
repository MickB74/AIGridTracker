# AI Token Footprint

A Streamlit app for the energy, water, and carbon footprint of LLM token usage —
from a single prompt to the global data-centre grid.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Interface (8 tabs)

1. **🧮 Calculator** — enter queries *or* raw output tokens, pick a source's
   coefficient (including live ML.ENERGY models once added), choose a grid carbon
   intensity, and get energy / water / CO₂ plus human-scale equivalents and a
   "per 1M units" scale-up.
2. **📊 Compare sources** — per-query energy across first-party disclosures and
   benchmark studies (log scale; the contested GPT-5 report is flagged).
3. **🔬 Live models** — pulls measured per-model inference energy straight from the
   **ML.ENERGY leaderboard** (public compiled JSON on GitHub) for text chat, code
   completion, and reasoning tasks on H100 / B200. Pick models to push their
   per-token coefficients into the Calculator. Falls back gracefully if offline.
4. **🏢 Data centers** — where the load actually is: major US + global markets by
   operational commissioned power (MW) on a map and MW-by-market bar chart, tagged
   with the ISO feed the app can pull carbon for. Plus the **ERCOT / PJM demand
   wave** (ERCOT's ~233 GW large-load queue, ~73% data centres; PJM's +32 GW
   2024→2030, 94% data-centre-driven) and a **live EIA-930 total-demand** pull per
   grid. Market MW are broker-inventory estimates (CBRE / Cushman & Wakefield),
   not per-facility disclosures.
5. **🕐 Grid timing** — the CFE / 24-7 matching angle: hourly carbon-intensity
   curves per ISO (CAISO / ERCOT / PJM), showing the carbon saved by shifting a
   flexible workload from the dirtiest to the cleanest hour. Curves are stylized
   placeholders behind a `fetch_grid_intensity()` stub — wire a live feed there.
6. **🗞️ Community & backlash** — the pushback side: a sourced rundown of the
   recurring flashpoints (power bills / grid strain, water, zoning & moratoria,
   noise, tax breaks, backup diesel) plus a **live feed** — news (Google News
   RSS) or grassroots sentiment (Reddit Atom search RSS) — filterable by theme
   and place. Both keyless; Reddit uses the RSS endpoint (the JSON API is closed)
   so it works from any IP.
7. **🌍 Macro outlook** — IEA data-centre electricity trajectory (415 → 945 TWh),
   AI's rising share, inference dominance, and the Jevons-paradox caveat.
8. **📚 Methodology** — every coefficient, its source link, and the scope caveats
   (chip-only vs full-stack, market vs location-based carbon, text-only, water).

## Live data wiring

- **ML.ENERGY** (Live models tab): streams from
  `raw.githubusercontent.com/ml-energy/leaderboard/master/public/data/tasks/*.json`,
  cached 24h. Each config carries `energy_per_token_joules` and
  `energy_per_request_joules`; the app reduces to the min-energy (best-batched)
  config per (model, GPU).
- **Grid intensity** (Grid timing tab): four sources —
  - *Stylized (offline)* — illustrative CAISO / ERCOT / PJM day curves.
  - *EIA-930 · fuel-mix avg* — live from EIA API v2 `fuel-type-data` (hourly net
    generation by fuel type per balancing authority) × editable
    `EIA_EMISSION_FACTORS`, generation-weighted to an hourly average. **One free
    key covers any US ISO** — ERCOT, CAISO, PJM, MISO, ISO-NE, NYISO, SPP, BPA.
    Periods are UTC; the app localizes to the BA's clock so the cleanest-hour
    label is meaningful. Get the key at
    [eia.gov/opendata/register.php](https://www.eia.gov/opendata/register.php).
  - *PJM · marginal CO₂* — live from Data Miner 2 `fivemin_marginal_emissions`
    (`marginal_co2_rate` in lbs/MWh → gCO₂/kWh, resampled to hourly). Marginal is
    the **correct signal for load-shifting**.
  - *PJM · fuel-mix avg* — live from `gen_by_fuel` (MW by fuel type) × editable
    `PJM_EMISSION_FACTORS`, generation-weighted to an hourly average intensity.

  Both PJM paths call `https://api.pjm.com/api/v1/{feed}` with your subscription
  key in the `Ocp-Apim-Subscription-Key` header (paste it in the app; nothing is
  stored). Get the key from PJM Tools → View Profile → Your Subscriptions. Note
  the rate limit: 6 requests/min for non-members. For other ISOs, wire Electricity
  Maps, WattTime (marginal MOER), or EIA-930 / GridStatus the same way.

## Where to edit

All coefficients and sources are dicts at the top of `app.py`
(`QUERY_COEFFS`, `TOKEN_COEFFS`, `GRID_INTENSITY`, `IEA_OUTLOOK`, `SOURCES`).
Swap in new disclosures without touching the UI.

## Primary sources

- IEA — *Energy and AI* (2025) + 2026 update — macro data-centre outlook
- Google — *Measuring the environmental impact of AI inference* (Aug 2025) — per-prompt
- Epoch AI (2025) — per-token inference energy
- *How Hungry is AI?* (arXiv:2505.09598) — per-query energy/water/carbon benchmark
- ML.Energy leaderboard — live per-model inference energy

## Extending it

- **Water by grid.** Add water-usage effectiveness (WUE) per ISO so the Grid tab
  shows water as well as carbon by hour.
- **Image / video mode.** Add multimodal coefficients (materially higher per call).
- **Persisted usage log.** Track cumulative footprint over a session or user.
