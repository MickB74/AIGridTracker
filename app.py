"""
AI Token Footprint — energy, water & carbon of LLM usage
=========================================================
Streamlit app: turns tokens/queries into energy, water, and CO2; puts a single
query in human terms; compares first-party & benchmark sources; pulls LIVE
measured per-model numbers from the ML.ENERGY leaderboard; and shows how timing
usage to clean grid hours changes carbon (the CFE / hourly-matching angle).

Run:
    pip install -r requirements.txt
    streamlit run app.py

Coefficients are sourced inline (see SOURCES) and surfaced on the Methodology
tab. Figures are point-in-time estimates, not guarantees.
"""

import json
import os
import pathlib
import urllib.parse
import xml.etree.ElementTree as ET

import streamlit as st
import pandas as pd
import altair as alt
import requests

# --------------------------------------------------------------------------- #
# STATIC DATA (sourced — see SOURCES and the Methodology tab)
# --------------------------------------------------------------------------- #

# Per-QUERY coefficients, median text prompt. energy Wh, co2 gCO2e, water mL.
QUERY_COEFFS = {
    "Google Gemini — comprehensive (May 2025)": {
        "energy_wh": 0.24, "co2_g": 0.03, "water_ml": 0.26, "src": "google_2025",
        "note": "Full-stack: accelerator + host CPU + idle + cooling/PUE. Market-based carbon.",
    },
    "Google Gemini — chip-only (May 2025)": {
        "energy_wh": 0.10, "co2_g": 0.02, "water_ml": 0.12, "src": "google_2025",
        "note": "Active TPU/GPU only. Understates real operating footprint.",
    },
    "OpenAI — avg query (Altman, 2025)": {
        "energy_wh": 0.34, "co2_g": None, "water_ml": 0.39, "src": "openai_2025",
        "note": "CEO blog figure; methodology not published.",
    },
    "GPT-4o benchmark (How Hungry is AI?, 2025)": {
        "energy_wh": 0.55, "co2_g": None, "water_ml": None, "src": "hungry_2025",
        "note": "Derived midpoint (~0.51–0.60 Wh/query) from annual estimate.",
    },
    "GPT-5 report — avg (2025, contested)": {
        "energy_wh": 18.0, "co2_g": None, "water_ml": None, "src": "gpt5_report",
        "note": "Third-party report; up to ~40 Wh on some responses. High / disputed.",
    },
}

# Per-TOKEN energy (Wh per output token), static references.
TOKEN_COEFFS = {
    "Epoch AI midpoint (2025)": 0.0005,      # ~1.8 J/token
    "Epoch AI low (efficient)": 0.0001,
    "Epoch AI high": 0.002,
    "LLaMA-65B, older GPU (~3.5 J/token)": 0.00097,
}

# Grid carbon intensity presets, gCO2 per kWh (flat, for the Calculator).
GRID_INTENSITY = {
    "Google market-based (~2024 fleet)": 125,
    "US grid average": 385,
    "Global grid average": 480,
    "Coal-heavy grid": 700,
}

WATER_ML_PER_WH = 0.26 / 0.24  # ~1.083 mL/Wh, implied by Gemini disclosure

# IEA data-centre electricity outlook (TWh), demand-side.
IEA_OUTLOOK = pd.DataFrame({"year": [2024, 2025, 2030, 2035],
                            "twh":  [415,  485,  945,  1200]})

# Major data-centre markets — OPERATIONAL commissioned power (MW), ~2025.
# Market-level totals from broker inventories (CBRE / Cushman & Wakefield /
# datacenterHawk) — NOT per-facility disclosures, which operators don't publish.
# grid = the ISO/grid feed this app can pull carbon for ("" = not yet wired).
# Approximate; sources on the Methodology tab and in each row's `src`.
DATACENTERS = [
    # name, region, country, grid, lat, lon, mw, src
    ("Northern Virginia (Ashburn)", "US", "USA", "PJM",   38.98, -77.46, 4900, "cbre_dc"),
    ("Dallas–Fort Worth",           "US", "USA", "ERCO",  32.78, -96.80, 1650, "cbre_dc"),
    ("Phoenix",                     "US", "USA", "",      33.45, -112.07, 1380, "cbre_dc"),
    ("Atlanta",                     "US", "USA", "",      33.75, -84.39, 1300, "cbre_dc"),
    ("Chicago",                     "US", "USA", "PJM",   41.85, -87.65, 1200, "cbre_dc"),
    ("Silicon Valley (Santa Clara)","US", "USA", "CISO",  37.35, -121.95, 950, "cbre_dc"),
    ("Columbus (Central Ohio)",     "US", "USA", "PJM",   39.96, -83.00,  700, "cbre_dc"),
    ("Portland / Hillsboro",        "US", "USA", "",      45.52, -122.98, 600, "cbre_dc"),
    ("Beijing",              "APAC", "China",      "", 39.90, 116.40, 1799, "cbre_glob"),
    ("London",               "EMEA", "UK",         "", 51.51,  -0.13, 1189, "cbre_glob"),
    ("Sydney",               "APAC", "Australia",  "", -33.87, 151.21, 1050, "cbre_glob"),
    ("Tokyo",                "APAC", "Japan",      "", 35.68, 139.69, 1000, "cbre_glob"),
    ("Shanghai",             "APAC", "China",      "", 31.23, 121.47, 1000, "cbre_glob"),
    ("Singapore",            "APAC", "Singapore",  "",  1.35, 103.82, 1000, "cbre_glob"),
    ("Frankfurt",            "EMEA", "Germany",    "", 50.11,   8.68,  900, "cbre_glob"),
    ("Dublin",               "EMEA", "Ireland",    "", 53.35,  -6.26,  700, "cbre_glob"),
    ("Amsterdam",            "EMEA", "Netherlands","", 52.37,   4.90,  550, "cbre_glob"),
    ("Paris",                "EMEA", "France",     "", 48.86,   2.35,  500, "cbre_glob"),
]
DATACENTERS_DF = pd.DataFrame(
    DATACENTERS,
    columns=["market", "region", "country", "grid", "lat", "lon", "mw", "src"])

# Data-centre moratoriums / bans — POINT-IN-TIME SNAPSHOT (mid-2026). Compiled
# from public trackers (see MORATORIUM_TRACKERS); dozens more churn weekly, so
# treat as illustrative, not exhaustive — follow the tracker links for current
# status. level: Local/State. status: Enacted/Proposed/Rejected/Vetoed.
MORATORIUMS = [
    # locality, state, level, status, when, note
    ("Minneapolis", "MN", "Local", "Enacted", "May 2026", ""),
    ("Denver", "CO", "Local", "Enacted", "May 2026", ""),
    ("Baltimore City", "MD", "Local", "Enacted", "May 2026", ""),
    ("Reno", "NV", "Local", "Enacted", "May 2026", ""),
    ("Dubuque County", "IA", "Local", "Enacted", "2026", ""),
    ("Bloomington", "IL", "Local", "Enacted", "2026", ""),
    ("Normal", "IL", "Local", "Enacted", "2026", ""),
    ("Iron County", "UT", "Local", "Enacted", "2026", ""),
    ("Manitowoc County", "WI", "Local", "Enacted", "2026", "18-month"),
    ("Smithfield", "RI", "Local", "Enacted", "2026", "Outright ban"),
    ("Meridian Township", "MI", "Local", "Enacted", "2026", ""),
    ("Washington Township (Macomb Co.)", "MI", "Local", "Enacted", "2026", ""),
    ("Hill County", "TX", "Local", "Enacted", "2026", "Under developer lawsuit"),
    ("DeKalb County", "GA", "Local", "Enacted", "2026", ""),
    ("Lysander (Onondaga Co.)", "NY", "Local", "Enacted", "May 2026", "6-month"),
    ("Perth (Fulton Co.)", "NY", "Local", "Enacted", "Jun 2025", "1-year"),
    ("Groton", "CT", "Local", "Enacted", "2025", "Year-long"),
    ("Peculiar", "MO", "Local", "Enacted", "2025", "Ban"),
    ("Bangor", "ME", "Local", "Enacted", "2025", "Temporary ban"),
    # North Carolina — 20+ jurisdictions since late 2025 (subset)
    ("Gates County", "NC", "Local", "Enacted", "2025–26", ""),
    ("Brevard", "NC", "Local", "Enacted", "2025–26", ""),
    ("Clay County", "NC", "Local", "Enacted", "2025–26", ""),
    ("Canton", "NC", "Local", "Enacted", "2025–26", ""),
    ("Chatham County", "NC", "Local", "Enacted", "2025–26", ""),
    ("Kings Mountain", "NC", "Local", "Enacted", "2025–26", ""),
    ("Boone", "NC", "Local", "Enacted", "2025–26", ""),
    ("Apex", "NC", "Local", "Enacted", "2025–26", ""),
    ("Orange County", "NC", "Local", "Enacted", "2025–26", ""),
    ("Rowan County", "NC", "Local", "Enacted", "2025–26", ""),
    ("Swain County", "NC", "Local", "Enacted", "2025–26", ""),
    ("Watauga County", "NC", "Local", "Enacted", "2025–26", ""),
    ("Madison County", "NC", "Local", "Enacted", "2025–26", ""),
    ("Clyde", "NC", "Local", "Enacted", "2025–26", ""),
    # Proposed / under consideration
    ("Seattle", "WA", "Local", "Proposed", "Jun 2026", ""),
    ("Indianapolis", "IN", "Local", "Proposed", "Jun 2026", "Non-binding pause"),
    ("Pulaski County", "AR", "Local", "Proposed", "2026", ""),
    ("St. Lawrence County", "NY", "Local", "Proposed", "2026", "Urged municipalities"),
    # Rejected
    ("Cheyenne", "WY", "Local", "Rejected", "2026", "Voted down 8–1"),
    # State-level
    ("New York (statewide)", "NY", "State", "Proposed", "Jun 2026", "Passed legislature; awaiting governor"),
    ("Georgia (HB 1012)", "GA", "State", "Proposed", "2026", "Permit bar to Mar 2027"),
    ("Maine (statewide)", "ME", "State", "Vetoed", "Apr 2026", "Governor veto"),
    ("Ohio (ballot measure)", "OH", "State", "Rejected", "2026", "Failed signature threshold"),
]
MORATORIUMS_DF = pd.DataFrame(
    MORATORIUMS,
    columns=["locality", "state", "level", "status", "when", "note"])

# Illustrative 24-hour marginal carbon-intensity curves (gCO2/kWh).
# STYLIZED shapes anchored to plausible ranges — NOT live. Replace via the
# fetch_grid_intensity() stub with Electricity Maps / WattTime / EIA-930 /
# GridStatus, or an ISO fuel-mix feed (ERCOT / PJM Data Miner 2 -> emissions).
GRID_CURVES = {
    "CAISO (solar duck curve)": [
        360, 355, 350, 350, 355, 365, 350, 300, 240, 180, 150, 140,
        140, 150, 175, 230, 320, 430, 470, 460, 430, 400, 385, 370],
    "ERCOT (wind + solar)": [
        410, 400, 390, 385, 385, 395, 400, 380, 350, 330, 315, 310,
        315, 330, 355, 390, 430, 480, 510, 500, 470, 440, 425, 415],
    "PJM (coal/gas/nuclear, flatter)": [
        430, 420, 415, 410, 415, 430, 460, 480, 485, 480, 475, 475,
        480, 485, 490, 495, 500, 505, 505, 500, 490, 470, 450, 440],
    "Flat average (illustrative)": [480] * 24,
}

SOURCES = {
    "google_2025":  ("Google, Measuring the environmental impact of AI inference (Aug 2025)",
                     "https://cloud.google.com/blog/products/infrastructure/measuring-the-environmental-impact-of-ai-inference"),
    "openai_2025":  ("Sam Altman, The Gentle Singularity (2025) — per-query figure",
                     "https://blog.samaltman.com/the-gentle-singularity"),
    "epoch_2025":   ("Epoch AI — per-token inference energy (2025)",
                     "https://epoch.ai/"),
    "hungry_2025":  ("How Hungry is AI? Benchmarking Energy, Water, Carbon (arXiv:2505.09598)",
                     "https://arxiv.org/abs/2505.09598"),
    "mlenergy":     ("ML.ENERGY Leaderboard — measured per-model inference energy (live)",
                     "https://ml.energy/leaderboard"),
    "iea_2025":     ("IEA, Energy and AI (2025) + Key Questions update (2026)",
                     "https://www.iea.org/reports/energy-and-ai"),
    "gpt5_report":  ("Third-party GPT-5 energy report (2025) — contested",
                     "https://www.datacenterdynamics.com/"),
    "elmaps":       ("Electricity Maps — real-time grid carbon intensity API",
                     "https://www.electricitymaps.com/"),
    "watttime":     ("WattTime — marginal emissions (MOER) API",
                     "https://watttime.org/"),
    "gridstatus":   ("GridStatus.io / EIA-930 — ISO fuel mix & emissions",
                     "https://www.gridstatus.io/"),
    "eia930":       ("EIA-930 — hourly net generation by fuel type (API v2, free key)",
                     "https://www.eia.gov/opendata/browser/electricity/rto/fuel-type-data"),
    "cbre_dc":      ("CBRE — North America Data Center Trends 2025 (market operational MW)",
                     "https://www.cbre.com/insights/reports/north-america-data-center-trends-h1-2025"),
    "cbre_glob":    ("CBRE — Global Data Center Trends 2025 (EMEA/APAC market MW)",
                     "https://www.cbre.com/insights/reports/global-data-center-trends-2025"),
    "ercot_ll":     ("ERCOT — Large Load Interconnection Queue (Dec 2025 board update)",
                     "https://www.ercot.com/gridinfo/load"),
    "pjm_lf":       ("PJM — 2025 Long-Term Load Forecast (data-centre-driven growth)",
                     "https://www.pjm.com/-/media/DotCom/library/reports-notices/load-forecast/2025-load-report.pdf"),
    "eia_va":       ("EIA — Commercial electricity sales in Virginia driven by data centers (2025)",
                     "https://www.eia.gov/todayinenergy/detail.php?id=67664"),
    "google_news":  ("Google News — live headline search (Community & backlash tab)",
                     "https://news.google.com/"),
    "reddit":       ("Reddit — public search JSON (grassroots sentiment; Community & backlash tab)",
                     "https://www.reddit.com/"),
    "icap_mor":     ("Interconnected Capital — US Data Center Moratorium Tracker (2026)",
                     "https://www.interconnectedcapital.com/research/data-center-moratoriums"),
    "dcbans":       ("DataCenterBans.com — moratorium & ban tracker",
                     "https://www.datacenterbans.com/"),
    "gjf_mor":      ("Good Jobs First — Data Center Moratorium Bills Are Spreading (2026)",
                     "https://goodjobsfirst.org/data-center-moratorium-bills-are-spreading-in-2026/"),
    "rockinst":     ("Rockefeller Institute — Updates on the Cloud: More Moratoriums (2026)",
                     "https://www.rockinst.org/blog/updates-on-the-cloud-more-moratoriums-on-data-centers/"),
    "pjm_dm2":      ("PJM Data Miner 2 — gen_by_fuel & fivemin_marginal_emissions feeds",
                     "https://dataminer2.pjm.com/"),
}

# --------------------------------------------------------------------------- #
# LIVE DATA — ML.ENERGY leaderboard (public, ungated compiled JSON)
# --------------------------------------------------------------------------- #

MLENERGY_BASE = ("https://raw.githubusercontent.com/ml-energy/leaderboard/"
                 "master/public/data/tasks/{slug}.json")
MLENERGY_TASKS = {
    "Text chat (LM Arena)": "lm-arena-chat",
    "Code completion (Sourcegraph FIM)": "sourcegraph-fim",
    "Reasoning (GPQA)": "gpqa",
}


@st.cache_data(ttl=86_400, show_spinner=False)
def load_mlenergy(slug: str):
    """Fetch a task file and reduce to the min-energy (best-batched) config per
    (model, gpu). Returns (DataFrame, error_str_or_None)."""
    try:
        r = requests.get(MLENERGY_BASE.format(slug=slug), timeout=12)
        r.raise_for_status()
        cfgs = r.json()["configurations"]
        rows = [{
            "model": c["nickname"],
            "gpu": c["gpu_model"],
            "wh_per_token": c["energy_per_token_joules"] / 3600.0,
            "wh_per_request": c["energy_per_request_joules"] / 3600.0,
            "params_b": c.get("total_params_billions"),
            "precision": c.get("weight_precision", "—"),
            "arch": c.get("architecture", "—"),
        } for c in cfgs]
        df = pd.DataFrame(rows)
        idx = df.groupby(["model", "gpu"])["wh_per_token"].idxmin()
        df = df.loc[idx].sort_values("wh_per_token").reset_index(drop=True)
        return df, None
    except Exception as e:                                    # noqa: BLE001
        return None, str(e)


# --- PJM Data Miner 2 live grid carbon (real feeds) ------------------------- #
# Base: https://api.pjm.com/api/v1/{feed}  •  header: Ocp-Apim-Subscription-Key
# Envelope: {"items": [...], "totalRows": N, "links": [{"rel":"next","href":...}]}
# Date filter: datetime_beginning_ept = "MM/DD/YYYY HH:MM" + "to" + "MM/DD/YYYY HH:MM"
PJM_API_BASE = "https://api.pjm.com/api/v1/"
LB_TO_G = 453.59237                        # pounds -> grams

# Direct-combustion emission factors (gCO2/kWh) for the fuel-mix (AVERAGE) path.
# Editable; unknown fuels fall back to DEFAULT_FACTOR. Zero-carbon at point of use.
PJM_EMISSION_FACTORS = {
    "Coal": 1000, "Gas": 400, "Oil": 800, "Multiple Fuels": 600, "Other": 600,
    "Nuclear": 0, "Hydro": 0, "Wind": 0, "Solar": 0, "Storage": 0,
    "Other Renewables": 0,
}
DEFAULT_FACTOR = 450


def _pjm_get(endpoint: str, api_key: str, fields: str, date_str: str,
             extra: dict | None = None, row_count: int = 50000) -> pd.DataFrame:
    """One Data Miner 2 call for a single EPT day. Returns the items DataFrame."""
    params = {
        "fields": fields, "startRow": 1, "rowCount": row_count,
        "datetime_beginning_ept": f"{date_str} 00:00to{date_str} 23:59",
    }
    if extra:
        params.update(extra)
    r = requests.get(PJM_API_BASE + endpoint, params=params,
                     headers={"Ocp-Apim-Subscription-Key": api_key}, timeout=20)
    r.raise_for_status()
    js = r.json()
    if isinstance(js, dict) and js.get("errors"):
        raise RuntimeError(js["errors"])
    return pd.DataFrame(js.get("items", []) if isinstance(js, dict) else js)


@st.cache_data(ttl=3600, show_spinner=False)
def pjm_marginal_co2(api_key: str, date_str: str, pnode_id: str = ""):
    """Marginal CO2 (lbs/MWh) -> 24 hourly gCO2/kWh from fivemin_marginal_emissions.
    Marginal is the correct signal for load-shifting decisions. If pnode_id is
    blank, averages across all returned pnodes (may be truncated at row_count)."""
    extra = {"pnode_id": pnode_id} if pnode_id else None
    df = _pjm_get("fivemin_marginal_emissions", api_key,
                  "datetime_beginning_ept,pnode_id,pnode_name,marginal_co2_rate",
                  date_str, extra=extra)
    if df.empty:
        return None
    df["ts"] = pd.to_datetime(df["datetime_beginning_ept"])
    df["g_kwh"] = pd.to_numeric(df["marginal_co2_rate"], errors="coerce") * LB_TO_G / 1000.0
    hourly = df.groupby(df["ts"].dt.hour)["g_kwh"].mean()
    return [round(float(hourly[h]), 1) if h in hourly.index else None for h in range(24)]


@st.cache_data(ttl=3600, show_spinner=False)
def pjm_fuelmix_co2(api_key: str, date_str: str):
    """Fuel mix (MW by type) -> 24 hourly AVERAGE gCO2/kWh from gen_by_fuel,
    weighting PJM_EMISSION_FACTORS by generation. Average, not marginal."""
    df = _pjm_get("gen_by_fuel", api_key,
                  "datetime_beginning_ept,fuel_type,mw", date_str)
    if df.empty:
        return None
    df["ts"] = pd.to_datetime(df["datetime_beginning_ept"])
    df["mw"] = pd.to_numeric(df["mw"], errors="coerce")
    df["ef"] = df["fuel_type"].map(PJM_EMISSION_FACTORS).fillna(DEFAULT_FACTOR)

    def _wavg(g):
        tot = g["mw"].sum()
        return (g["mw"] * g["ef"]).sum() / tot if tot else float("nan")

    hourly = df.groupby(df["ts"].dt.hour).apply(_wavg)
    return [round(float(hourly[h]), 1) if h in hourly.index else None for h in range(24)]


# --- EIA-930 live grid carbon (any US balancing authority) ------------------ #
# EIA API v2 hourly net generation by fuel type per respondent (BA). One free
# key (https://www.eia.gov/opendata/register.php) covers ERCOT, CAISO, PJM,
# MISO, ISO-NE, NYISO, SPP, BPA, etc. Same fuel-mix × emission-factor pattern
# as PJM's AVERAGE path. Periods are UTC; we localize to the BA's clock so the
# "cleanest hour" label is meaningful.
EIA_BASE = "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/"

# EIA-930 fuel-type codes -> direct-combustion emission factors (gCO2/kWh).
EIA_EMISSION_FACTORS = {
    "COL": 1000, "NG": 400, "OIL": 800, "OTH": 600,
    "NUC": 0, "WAT": 0, "WND": 0, "SUN": 0, "BAT": 0, "PS": 0, "GEO": 0,
}

# Balancing authorities offered in the UI -> (label, IANA timezone).
EIA_RESPONDENTS = {
    "ERCO": ("ERCOT (Texas)", "America/Chicago"),
    "CISO": ("CAISO (California)", "America/Los_Angeles"),
    "PJM":  ("PJM (Mid-Atlantic)", "America/New_York"),
    "MISO": ("MISO (Midwest)", "America/New_York"),
    "SWPP": ("SPP (Central)", "America/Chicago"),
    "ISNE": ("ISO-NE (New England)", "America/New_York"),
    "NYIS": ("NYISO (New York)", "America/New_York"),
    "BPAT": ("BPA (Pacific NW)", "America/Los_Angeles"),
}


@st.cache_data(ttl=3600, show_spinner=False)
def eia930_fuelmix_co2(api_key: str, date_str: str, respondent: str):
    """EIA-930 hourly net generation by fuel type -> 24 hourly AVERAGE gCO2/kWh,
    weighting EIA_EMISSION_FACTORS by generation. date_str is 'YYYY-MM-DD' in the
    BA's local clock. Average, not marginal. Returns a 24-slot list or None."""
    tz = EIA_RESPONDENTS.get(respondent, (respondent, "UTC"))[1]
    # Query a UTC window wide enough to cover the local day, then filter by
    # local calendar date so partial-day edge hours don't skew the average.
    start = (pd.Timestamp(date_str, tz=tz) - pd.Timedelta(hours=1)).tz_convert("UTC")
    end = start + pd.Timedelta(hours=27)
    params = {
        "api_key": api_key,
        "frequency": "hourly",
        "data[0]": "value",
        "facets[respondent][]": respondent,
        "start": start.strftime("%Y-%m-%dT%H"),
        "end": end.strftime("%Y-%m-%dT%H"),
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "length": 5000,
    }
    r = requests.get(EIA_BASE, params=params, timeout=20)
    r.raise_for_status()
    js = r.json()
    if js.get("response", {}).get("errors"):
        raise RuntimeError(js["response"]["errors"])
    rows = js.get("response", {}).get("data", [])
    df = pd.DataFrame(rows)
    if df.empty:
        return None
    # EIA periods are UTC (naive "YYYY-MM-DDTHH"); localize then convert.
    ts = pd.to_datetime(df["period"], utc=True).dt.tz_convert(tz)
    df["mwh"] = pd.to_numeric(df["value"], errors="coerce").clip(lower=0)
    df["ef"] = df["fueltype"].map(EIA_EMISSION_FACTORS).fillna(DEFAULT_FACTOR)
    df = df[ts.dt.strftime("%Y-%m-%d") == date_str]
    hour = ts[df.index].dt.hour
    if df.empty:
        return None

    def _wavg(g):
        tot = g["mwh"].sum()
        return (g["mwh"] * g["ef"]).sum() / tot if tot else float("nan")

    hourly = df.groupby(hour).apply(_wavg)
    return [round(float(hourly[h]), 1) if h in hourly.index else None for h in range(24)]


EIA_DEMAND_BASE = "https://api.eia.gov/v2/electricity/rto/region-data/data/"


@st.cache_data(ttl=1800, show_spinner=False)
def eia_latest_demand(api_key: str, respondent: str):
    """Latest hourly system demand (MW) for a balancing authority via EIA-930
    region-data (type 'D'). Returns (mw, period_str) or None. Grid-scale total
    load, not data-centre-only — context for 'how much power'."""
    params = {
        "api_key": api_key, "frequency": "hourly", "data[0]": "value",
        "facets[respondent][]": respondent, "facets[type][]": "D",
        "sort[0][column]": "period", "sort[0][direction]": "desc", "length": 1,
    }
    r = requests.get(EIA_DEMAND_BASE, params=params, timeout=20)
    r.raise_for_status()
    rows = r.json().get("response", {}).get("data", [])
    if not rows:
        return None
    return float(rows[0]["value"]), rows[0]["period"]


# --- Live news — Google News RSS (free, keyless) ---------------------------- #
GOOGLE_NEWS_RSS = ("https://news.google.com/rss/search?q={q}"
                   "&hl=en-US&gl=US&ceid=US:en")

# Recurring flashpoints -> a search query that surfaces them.
NEWS_THEMES = {
    "Community opposition & moratoria": "data center community opposition moratorium residents",
    "Electricity bills & grid strain": "data center electricity rates ratepayers grid cost",
    "Water use": "data center water use drought cooling",
    "Zoning & land-use fights": "data center zoning rezoning land use fight",
    "Noise complaints": "data center noise complaints residents",
    "Tax breaks vs. local benefit": "data center tax incentives subsidy jobs",
}


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_news(query: str, limit: int = 15):
    """Live headlines from Google News RSS (no API key). Returns
    (list_of_dicts, error_or_None); each dict has title/source/link/published."""
    try:
        url = GOOGLE_NEWS_RSS.format(q=urllib.parse.quote(query))
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        root = ET.fromstring(r.content)
        out = []
        for it in root.iter("item"):
            title = (it.findtext("title") or "").strip()
            src_el = it.find("source")
            source = src_el.text.strip() if src_el is not None and src_el.text else ""
            # Google News formats titles as "Headline - Source"; drop the suffix.
            if source and title.endswith(f" - {source}"):
                title = title[: -(len(source) + 3)]
            out.append({
                "title": title,
                "source": source,
                "link": (it.findtext("link") or "").strip(),
                "published": (it.findtext("pubDate") or "").strip()[:16],
            })
            if len(out) >= limit:
                break
        return out, None
    except Exception as e:                                        # noqa: BLE001
        return None, str(e)


# --- Live Reddit — public search RSS (keyless, works from any IP) ------------ #
# Reddit's search.json API is closed (403s off datacenter IPs), but the Atom
# search.rss feed is still open and reachable from anywhere. RSS carries
# title/subreddit/link/date but not scores — a fair trade for reliability.
# (Technique cf. github.com/mvanhorn/last30days-skill: RSS instead of JSON.)
REDDIT_RSS = "https://www.reddit.com/search.rss"
_ATOM = "{http://www.w3.org/2005/Atom}"
REDDIT_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_reddit(query: str, limit: int = 15, sort: str = "relevance",
                 period: str = "year"):
    """Live Reddit threads via the public Atom search RSS (keyless). Returns
    (list_of_dicts, error_or_None); each dict has title/subreddit/link/created.
    A 429 means Reddit is rate-limiting — the 1h cache normally avoids it."""
    try:
        r = requests.get(REDDIT_RSS,
                         params={"q": query, "sort": sort, "t": period},
                         headers={"User-Agent": REDDIT_UA}, timeout=15)
        r.raise_for_status()
        if not r.content.lstrip().startswith(b"<"):
            raise RuntimeError("Reddit returned non-XML (rate-limited or blocked)")
        root = ET.fromstring(r.content)
        out = []
        for e in root.iter(_ATOM + "entry"):
            link_el = e.find(_ATOM + "link")
            cat = e.find(_ATOM + "category")
            out.append({
                "title": (e.findtext(_ATOM + "title") or "").strip(),
                "subreddit": (cat.get("label") or cat.get("term") or "")
                             if cat is not None else "",
                "link": link_el.get("href") if link_el is not None else "",
                "created": (e.findtext(_ATOM + "published") or "")[:10],
            })
            if len(out) >= limit:
                break
        return out, None
    except Exception as e:                                        # noqa: BLE001
        return None, str(e)


# --------------------------------------------------------------------------- #
# HELPERS
# --------------------------------------------------------------------------- #

def human_energy(wh: float) -> str:
    tv_seconds = wh / 0.24 * 9
    if tv_seconds < 60:
        return f"≈ {tv_seconds:.0f} seconds of watching TV"
    if tv_seconds < 3600:
        return f"≈ {tv_seconds/60:.1f} minutes of watching TV"
    return f"≈ {tv_seconds/3600:.1f} hours of watching TV"


def human_water(ml: float) -> str:
    drops = ml / 0.05
    return f"≈ {drops:.0f} drops of water" if drops < 100 else f"≈ {ml/1000:.2f} L of water"


def src_link(key: str) -> str:
    name, url = SOURCES[key]
    return f"[{name}]({url})"


@st.cache_data(show_spinner=False)
def load_local_secrets() -> dict:
    """Best-effort local API keys for dev convenience, so keys needn't be pasted
    each session. Never raises; returns {'eia': str, 'pjm': str} (blank if absent).
    Lookup order per key: environment variable -> ./.env -> sibling
    pjm-suite/PJM_Data_Hub/config.json. Nothing is committed — .gitignore blocks
    .env and config.json. The UI fields still override whatever is found here."""
    out = {"eia": os.environ.get("EIA_API_KEY", "").strip(),
           "pjm": os.environ.get("PJM_API_KEY", "").strip()}
    here = pathlib.Path(__file__).resolve().parent

    env_path = here / ".env"
    if env_path.exists():
        try:
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                v = v.strip().strip('"').strip("'")
                if k.strip() == "EIA_API_KEY" and not out["eia"]:
                    out["eia"] = v
                elif k.strip() == "PJM_API_KEY" and not out["pjm"]:
                    out["pjm"] = v
        except Exception:                                          # noqa: BLE001
            pass

    if not out["eia"] or not out["pjm"]:
        cfg = here.parent / "pjm-suite" / "PJM_Data_Hub" / "config.json"
        try:
            data = json.loads(cfg.read_text())
            out["eia"] = out["eia"] or str(data.get("eia_api_key", "")).strip()
            out["pjm"] = out["pjm"] or str(data.get("subscription_key", "")).strip()
        except Exception:                                          # noqa: BLE001
            pass
    return out


LOCAL_SECRETS = load_local_secrets()


# --------------------------------------------------------------------------- #
# PAGE
# --------------------------------------------------------------------------- #

st.set_page_config(page_title="AI Token Footprint", page_icon="⚡", layout="wide")
st.title("⚡ AI Token Footprint")
st.caption("The energy, water, and carbon behind LLM token usage — from a single "
           "prompt to the global grid. Sourced throughout; see **Methodology**.")

(tab_calc, tab_compare, tab_live, tab_grid, tab_dc, tab_news, tab_macro,
 tab_method) = st.tabs(
    ["🧮 Calculator", "📊 Compare sources", "🔬 Live models",
     "🕐 Grid timing", "🏢 Data centers", "🗞️ Community & backlash",
     "🌍 Macro outlook", "📚 Methodology"]
)

# --------------------------------------------------------------------------- #
# TAB 1 — CALCULATOR
# --------------------------------------------------------------------------- #

with tab_calc:
    left, right = st.columns([1, 1.1], gap="large")

    with left:
        st.subheader("Your usage")
        mode = st.radio("Estimate by", ["Queries", "Tokens"], horizontal=True)

        if mode == "Queries":
            n = st.number_input("Number of queries", min_value=0, value=1000, step=100)
            coeff_name = st.selectbox("Per-query source", list(QUERY_COEFFS.keys()))
            c = QUERY_COEFFS[coeff_name]
            energy_wh = n * c["energy_wh"]
            water_ml = (n * c["water_ml"] if c["water_ml"] is not None
                        else n * c["energy_wh"] * WATER_ML_PER_WH)
            if c["co2_g"] is not None:
                co2_g = n * c["co2_g"]
                grid_label = "source's own carbon accounting"
            else:
                grid_name = st.selectbox("Grid carbon intensity", list(GRID_INTENSITY.keys()), index=2)
                co2_g = energy_wh / 1000 * GRID_INTENSITY[grid_name]
                grid_label = grid_name
            st.info(c["note"])
            per_unit_e = c["energy_wh"]
        else:
            n = st.number_input("Output tokens", min_value=0, value=500_000, step=10_000)
            # merge static references with any live coefficients loaded on Live tab
            live = st.session_state.get("live_coeffs", {})
            token_opts = {**TOKEN_COEFFS, **live}
            tok_name = st.selectbox("Per-token source", list(token_opts.keys()))
            per_unit_e = token_opts[tok_name]
            energy_wh = n * per_unit_e
            grid_name = st.selectbox("Grid carbon intensity", list(GRID_INTENSITY.keys()), index=2)
            co2_g = energy_wh / 1000 * GRID_INTENSITY[grid_name]
            water_ml = energy_wh * WATER_ML_PER_WH
            grid_label = grid_name
            if not live:
                st.caption("Tip: open **Live models** to add measured per-token "
                           "coefficients from the ML.ENERGY leaderboard.")

    with right:
        st.subheader("Footprint")
        m1, m2, m3 = st.columns(3)
        m1.metric("Energy", f"{energy_wh/1000:,.3f} kWh" if energy_wh >= 1000 else f"{energy_wh:,.1f} Wh")
        m2.metric("Water", f"{water_ml/1000:,.2f} L" if water_ml >= 1000 else f"{water_ml:,.1f} mL")
        m3.metric("Carbon", f"{co2_g/1000:,.2f} kg" if co2_g >= 1000 else f"{co2_g:,.1f} g")

        st.markdown("**In human terms (total):**")
        st.markdown(f"- {human_energy(energy_wh)}")
        st.markdown(f"- {human_water(water_ml)}")
        st.markdown(f"- Carbon accounting: *{grid_label}*")

        st.divider()
        unit = "queries" if mode == "Queries" else "tokens"
        per_unit_w = water_ml / max(n, 1)
        per_unit_c = co2_g / max(n, 1)
        st.markdown("**Scaled to 1 million of the same unit:**")
        st.markdown(f"- **{per_unit_e*1e6/1000:,.0f} kWh**, "
                    f"**{per_unit_w*1e6/1000:,.1f} L** water, "
                    f"**{per_unit_c*1e6/1000:,.1f} kg** CO₂e per 1M {unit}")

# --------------------------------------------------------------------------- #
# TAB 2 — COMPARE SOURCES
# --------------------------------------------------------------------------- #

with tab_compare:
    st.subheader("Per-query energy across sources")
    st.caption("First-party disclosures and benchmark studies vary widely, mostly by "
               "scope (chip-only vs full-stack) and model size. Note the log scale.")
    df = pd.DataFrame([{"source": k, "energy_wh": v["energy_wh"]} for k, v in QUERY_COEFFS.items()])
    log = st.toggle("Log scale (GPT-5 report dwarfs the rest)", value=True)
    chart = (alt.Chart(df).mark_bar().encode(
        x=alt.X("energy_wh:Q", title="Wh per query",
                scale=alt.Scale(type="log") if log else alt.Scale(type="linear")),
        y=alt.Y("source:N", sort="-x", title=None),
        tooltip=["source", "energy_wh"],
        color=alt.Color("energy_wh:Q", scale=alt.Scale(scheme="yelloworangered"), legend=None),
    ).properties(height=280))
    st.altair_chart(chart, use_container_width=True)
    st.caption("⚠️ The GPT-5 figure is a contested third-party report — an upper bound, "
               "not a disclosed number.")

# --------------------------------------------------------------------------- #
# TAB 3 — LIVE MODELS (ML.ENERGY)
# --------------------------------------------------------------------------- #

with tab_live:
    st.subheader("Measured per-model inference energy — ML.ENERGY leaderboard")
    st.caption("Live pull from the ML.ENERGY benchmark (H100 / B200, vLLM). Shows the "
               "min-energy (best-batched) config per model — a well-utilised server.")

    with st.expander("What is **Wh/token**? (and why size isn't everything)"):
        st.markdown(
            "**Wh/token = watt-hours per token** — the electricity to generate **one "
            "output token** (a token ≈ ¾ of a word, so ~750 tokens ≈ 550 words).\n\n"
            "- **Wh (watt-hour)** is a unit of energy: a 10-watt LED bulb running for "
            "one hour uses 10 Wh. `0.000008 Wh/token` = 8 millionths of a watt-hour "
            "per token.\n"
            "- **Wh/response** is just Wh/token × the tokens in a full answer — the "
            "other column.\n"
            "- Numbers look tiny because these are the **max-batch** configs (a busy, "
            "well-utilised server) — a lower bound vs. bursty real traffic.\n\n"
            "**Size isn't the whole story.** Energy per token is driven as much by "
            "**precision** (4-bit `mxfp4` fires far fewer bits than 16-bit `bfloat16`) "
            "and **architecture** (Mixture-of-Experts activates only a slice of the "
            "weights per token) as by raw parameter count — so a bigger model can use "
            "*less* per token than a smaller dense one.")

    cta, cgpu = st.columns(2)
    task_label = cta.selectbox("Task", list(MLENERGY_TASKS.keys()))
    gpu = cgpu.radio("GPU", ["H100", "B200"], horizontal=True)

    df_live, err = load_mlenergy(MLENERGY_TASKS[task_label])

    if err or df_live is None:
        st.warning("Couldn't reach the ML.ENERGY leaderboard (offline or blocked). "
                   "The Calculator still works with the static coefficients.")
        st.caption(f"Detail: {err}")
    else:
        d = df_live[df_live.gpu == gpu].copy()
        d["wh_per_1k_tok"] = d["wh_per_token"] * 1000
        st.caption(f"{len(d)} models • pulled live • GPU: {gpu}")

        chart = (alt.Chart(d).mark_bar().encode(
            x=alt.X("wh_per_request:Q", title="Wh per full response"),
            y=alt.Y("model:N", sort="-x", title=None),
            tooltip=[alt.Tooltip("model"), alt.Tooltip("wh_per_request", format=".4f"),
                     alt.Tooltip("wh_per_token", format=".6f"),
                     "params_b", "precision", "arch"],
            color=alt.Color("wh_per_request:Q", scale=alt.Scale(scheme="tealblues"), legend=None),
        ).properties(height=max(280, 26 * len(d))))
        st.altair_chart(chart, use_container_width=True)

        # --- dynamic takeaway read straight off the live numbers ------------- #
        eff = d.loc[d["wh_per_token"].idxmin()]
        hog = d.loc[d["wh_per_token"].idxmax()]
        ratio = hog["wh_per_token"] / eff["wh_per_token"] if eff["wh_per_token"] else 0
        st.markdown(
            f"**On {gpu}, {eff['model']} is the most efficient** at "
            f"{eff['wh_per_token']*1000:.4f} Wh per 1k tokens — "
            f"**{ratio:,.0f}× less** than {hog['model']} "
            f"({hog['wh_per_token']*1000:.4f}). ")
        # Surface a case where a bigger model beats a smaller one (arch/precision).
        dd = d.dropna(subset=["params_b"])
        if len(dd) >= 2:
            big = dd.loc[dd["params_b"].idxmax()]
            inversions = dd[(dd["params_b"] < big["params_b"]) &
                            (dd["wh_per_token"] > big["wh_per_token"])]
            if not inversions.empty:
                sm = inversions.loc[inversions["wh_per_token"].idxmax()]
                st.info(
                    f"💡 Size ≠ energy: **{big['model']}** ({big['params_b']:.0f}B, "
                    f"{big['precision']}, {big['arch']}) uses **less per token** than "
                    f"the smaller **{sm['model']}** ({sm['params_b']:.0f}B, "
                    f"{sm['precision']}, {sm['arch']}) — precision and architecture "
                    f"outweigh parameter count.")

        with st.expander("Table (per-token & per-request)"):
            show = d[["model", "params_b", "precision", "arch", "wh_per_token", "wh_per_request"]]
            st.dataframe(show, use_container_width=True, hide_index=True,
                         column_config={
                             "wh_per_token": st.column_config.NumberColumn("Wh/token", format="%.6f"),
                             "wh_per_request": st.column_config.NumberColumn("Wh/response", format="%.4f"),
                             "params_b": st.column_config.NumberColumn("Params (B)"),
                         })

        # push selected coefficients into the Calculator (Token mode)
        picks = st.multiselect("Add to Calculator as per-token sources", d["model"].tolist())
        if picks:
            st.session_state["live_coeffs"] = {
                f"🔬 {m} ({gpu})": float(d.loc[d.model == m, "wh_per_token"].iloc[0])
                for m in picks
            }
            st.success(f"Added {len(picks)} model(s). Switch to **Calculator → Tokens**.")

# --------------------------------------------------------------------------- #
# TAB 4 — GRID TIMING (CFE / hourly matching)
# --------------------------------------------------------------------------- #

with tab_grid:
    st.subheader("When you run it matters — hourly grid carbon")
    st.caption("Same tokens, different carbon depending on the hour and grid. Shift "
               "flexible/batch workloads to clean hours (the CFE / 24-7 matching idea).")

    with st.expander("What is **gCO₂/kWh** — and marginal vs. average?"):
        st.markdown(
            "**gCO₂/kWh = grams of CO₂ per kilowatt-hour** — the carbon emitted for "
            "each unit of electricity you draw. Multiply by your energy use to get "
            "carbon: `1 kWh × 400 gCO₂/kWh = 400 g = 0.4 kg CO₂`.\n\n"
            "It **changes by the hour**: when wind and solar are abundant (midday in "
            "CAISO, windy nights in ERCOT) the number drops; when gas and coal cover "
            "the load it rises. That's why *when* you run a flexible job matters.\n\n"
            "- **Average (fuel-mix):** the carbon of the *whole grid mix* that hour — "
            "generation-weighted across every fuel. Good for footprint accounting. "
            "The EIA-930 and PJM fuel-mix options here are average.\n"
            "- **Marginal:** the carbon of the *next* MWh — the plant that ramps up "
            "when you add load (usually gas). This is the **correct signal for "
            "load-shifting**, because it's what your extra demand actually causes. "
            "The PJM marginal option is this.")

    src = st.radio("Curve source", [
        "Stylized (offline)",
        "EIA-930 · fuel-mix avg (any US ISO)",
        "PJM · marginal CO₂ (Data Miner 2)",
        "PJM · fuel-mix avg (Data Miner 2)",
    ], horizontal=True)

    energy_kwh = st.number_input("Energy of the workload (kWh)", min_value=0.0,
                                 value=1.0, step=0.5,
                                 help="From the Calculator, or any batch job.")

    curve, label, note = None, "", ""

    if src == "Stylized (offline)":
        grid_name = st.selectbox("Grid / ISO", list(GRID_CURVES.keys()))
        curve = GRID_CURVES[grid_name]
        label = grid_name.split(" (")[0]
        note = ("Stylized illustration, not live. Use the EIA-930 option for any US "
                "ISO, a PJM option for marginal data, or wire Electricity Maps / "
                "WattTime for others.")
    elif src.startswith("EIA-930"):
        import datetime as _dt
        c1, c2, c3 = st.columns([2, 1.2, 1])
        api_key = c1.text_input("EIA API key", type="password",
                                value=LOCAL_SECRETS["eia"],
                                help="Free instant key: eia.gov/opendata/register.php")
        if LOCAL_SECRETS["eia"]:
            c1.caption("🔑 Auto-loaded from local config.")
        ba = c2.selectbox("Balancing authority", list(EIA_RESPONDENTS.keys()),
                          format_func=lambda k: EIA_RESPONDENTS[k][0])
        date = c3.date_input("Date (local)", value=_dt.date.today() - _dt.timedelta(days=1),
                             key="eia_date")
        date_str = date.strftime("%Y-%m-%d")
        ba_label = EIA_RESPONDENTS[ba][0].split(" (")[0]
        if not api_key:
            st.info("Enter your free EIA API key to pull live fuel-mix data. "
                    "Falling back to a stylized curve below.")
            curve = GRID_CURVES.get(
                {"ERCO": "ERCOT (wind + solar)", "CISO": "CAISO (solar duck curve)"}
                .get(ba, "PJM (coal/gas/nuclear, flatter)"),
                GRID_CURVES["Flat average (illustrative)"])
            label = f"{ba_label} (stylized fallback)"
        else:
            try:
                curve = eia930_fuelmix_co2(api_key, date_str, ba)
                label = f"{ba_label} fuel-mix avg · {date_str}"
                if not curve or all(v is None for v in curve):
                    raise RuntimeError("no rows returned")
                note = ("Live EIA-930 net generation by fuel type × direct-combustion "
                        "emission factors (editable in EIA_EMISSION_FACTORS), weighted "
                        "to an hourly AVERAGE in local time. Average, not marginal.")
            except Exception as e:                                # noqa: BLE001
                st.warning(f"EIA fetch failed ({e}). Using a stylized curve.")
                curve = GRID_CURVES["Flat average (illustrative)"]
                label = f"{ba_label} (stylized fallback)"
    else:
        import datetime as _dt
        c1, c2 = st.columns([2, 1])
        api_key = c1.text_input("PJM Data Miner 2 subscription key", type="password",
                                value=LOCAL_SECRETS["pjm"],
                                help="Data Miner 2 → account icon → API Access.")
        if LOCAL_SECRETS["pjm"]:
            c1.caption("🔑 Auto-loaded from local config.")
        date = c2.date_input("Date (EPT)", value=_dt.date.today() - _dt.timedelta(days=1))
        date_str = date.strftime("%m/%d/%Y")
        pnode = ""
        marginal = src.startswith("PJM · marginal")
        if marginal:
            pnode = st.text_input("pnode_id (blank = average all zones)", value="",
                                  help="Restrict to one zone/hub for a small, fast query.")
        if not api_key:
            st.info("Enter your subscription key to pull live PJM data. "
                    "Falling back to a stylized PJM-shaped curve below.")
            curve = GRID_CURVES["PJM (coal/gas/nuclear, flatter)"]
            label = "PJM (stylized fallback)"
        else:
            try:
                if marginal:
                    curve = pjm_marginal_co2(api_key, date_str, pnode)
                    label = f"PJM marginal · {date_str}"
                else:
                    curve = pjm_fuelmix_co2(api_key, date_str)
                    label = f"PJM fuel-mix avg · {date_str}"
                if not curve or all(v is None for v in curve):
                    raise RuntimeError("no rows returned")
                note = ("Live from PJM Data Miner 2. Marginal = correct signal for "
                        "load-shifting; fuel-mix avg uses editable emission factors."
                        if marginal else
                        "Live fuel mix × direct-combustion emission factors "
                        "(editable in PJM_EMISSION_FACTORS). Average, not marginal.")
            except Exception as e:                                # noqa: BLE001
                st.warning(f"PJM fetch failed ({e}). Using stylized PJM curve.")
                curve = GRID_CURVES["PJM (coal/gas/nuclear, flatter)"]
                label = "PJM (stylized fallback)"

    # --- chart + stats (robust to missing/None hours) ---------------------- #
    curve_df = pd.DataFrame({"hour": list(range(24)), "gco2_kwh": curve})
    area = (alt.Chart(curve_df).mark_area(opacity=0.25, line=True).encode(
        x=alt.X("hour:O", title="Hour of day (EPT)"),
        y=alt.Y("gco2_kwh:Q", title="gCO₂ / kWh"),
        tooltip=["hour", "gco2_kwh"],
    ).properties(height=280))
    st.altair_chart(area, use_container_width=True)

    valid = [(h, v) for h, v in enumerate(curve) if v is not None]
    if not valid:
        st.warning("No usable intensity values for this selection.")
    else:
        lo_h, lo = min(valid, key=lambda t: t[1])
        hi_h, hi = max(valid, key=lambda t: t[1])
        avg = sum(v for _, v in valid) / len(valid)
        co2_clean, co2_dirty, co2_avg = (energy_kwh * x / 1000 for x in (lo, hi, avg))
        saved = co2_dirty - co2_clean
        pct = (saved / co2_dirty * 100) if co2_dirty else 0

        k1, k2, k3 = st.columns(3)
        k1.metric(f"Cleanest hour ({lo_h:02d}:00)", f"{co2_clean:.3f} kg", f"{lo:.0f} gCO₂/kWh")
        k2.metric("24h average", f"{co2_avg:.3f} kg", f"{avg:.0f} gCO₂/kWh")
        k3.metric(f"Dirtiest hour ({hi_h:02d}:00)", f"{co2_dirty:.3f} kg",
                  f"{hi:.0f} gCO₂/kWh", delta_color="inverse")

        st.success(f"Shifting this workload from the dirtiest to the cleanest hour cuts "
                   f"carbon by **{saved:.3f} kg ({pct:.0f}%)** on {label}.")
        if len(valid) < 24:
            st.caption(f"Note: only {len(valid)}/24 hours had data.")
    st.caption(note)

# --------------------------------------------------------------------------- #
# TAB 5 — DATA CENTERS (where the load is, and the demand wave)
# --------------------------------------------------------------------------- #

with tab_dc:
    st.subheader("Where the data centres are — and how much power they pull")
    st.caption("Operational commissioned power by market (~2025). Market-level "
               "totals from broker inventories (CBRE / Cushman & Wakefield) — "
               "operators don't disclose per-facility MW. Approximate; see "
               "**Methodology** for sources.")

    region = st.radio("Region", ["All", "US", "EMEA", "APAC"], horizontal=True)
    dcd = DATACENTERS_DF if region == "All" else DATACENTERS_DF[DATACENTERS_DF.region == region]

    m1, m2, m3 = st.columns(3)
    m1.metric("Markets shown", f"{len(dcd)}")
    m2.metric("Operational power", f"{dcd['mw'].sum()/1000:,.1f} GW")
    m3.metric("Largest", f"{dcd.loc[dcd['mw'].idxmax(), 'market'].split(' (')[0]}",
              f"{dcd['mw'].max():,.0f} MW")

    map_df = dcd.rename(columns={"lat": "latitude", "lon": "longitude"}).copy()
    map_df["size"] = map_df["mw"] * 40          # radius in metres, scaled by MW
    st.map(map_df, latitude="latitude", longitude="longitude", size="size",
           color="#ff5a1f")

    bar = (alt.Chart(dcd).mark_bar().encode(
        x=alt.X("mw:Q", title="Operational power (MW)"),
        y=alt.Y("market:N", sort="-x", title=None),
        tooltip=["market", "country", "grid", "mw"],
        color=alt.Color("region:N", legend=alt.Legend(title="Region")),
    ).properties(height=max(280, 26 * len(dcd))))
    st.altair_chart(bar, use_container_width=True)

    with st.expander("Table + sources"):
        show = dcd[["market", "region", "country", "grid", "mw"]].copy()
        show["source"] = dcd["src"].map(lambda k: SOURCES[k][0])
        st.dataframe(show, use_container_width=True, hide_index=True,
                     column_config={"mw": st.column_config.NumberColumn("MW", format="%d"),
                                    "grid": "ISO feed"})
    st.caption("⚡ Markets tagged with an **ISO feed** (ERCO / CISO / PJM) can be "
               "pulled live for carbon on the **Grid timing** tab.")

    st.divider()
    st.subheader("The demand wave — ERCOT & PJM")
    st.caption("The two US grids where data-centre load growth is most acute. "
               "Interconnection-queue figures are filed point-in-time snapshots "
               "(not a live API); headline numbers sourced below.")

    ge, gp = st.columns(2)
    with ge:
        st.markdown("**ERCOT (Texas)**")
        e1, e2 = st.columns(2)
        e1.metric("Large-load queue", "~233 GW", "requests, Nov 2025")
        e2.metric("Data centres", "72.9%", "of the queue")
        st.caption("Nearly **4×** the 63 GW at end-2024. + crypto ~8.8%. "
                   f"{src_link('ercot_ll')}.")
    with gp:
        st.markdown("**PJM (Mid-Atlantic)**")
        p1, p2 = st.columns(2)
        p1.metric("Peak load 2024→30", "+32 GW", "94% data centres")
        p2.metric("Dominion (VA) summer peak", "23.9 GW", "+23% vs 2019")
        st.caption("Dominion zone (NoVA \"Data Center Alley\") drives the biggest "
                   f"absolute rise. {src_link('pjm_lf')}; {src_link('eia_va')}.")

    st.markdown("**Live system demand (EIA-930)** — grid-scale total load right "
                "now (all uses, not data-centre-only):")
    dk = st.text_input("EIA API key", type="password", key="dc_eia_key",
                       value=LOCAL_SECRETS["eia"],
                       help="Free instant key: eia.gov/opendata/register.php "
                            "— same key as the Grid timing tab.")
    if LOCAL_SECRETS["eia"]:
        st.caption("🔑 Auto-loaded from local config.")
    if dk:
        cols = st.columns(3)
        for col, ba in zip(cols, ["ERCO", "PJM", "CISO"]):
            try:
                res = eia_latest_demand(dk, ba)
                if res:
                    mw, period = res
                    col.metric(f"{ba} demand", f"{mw/1000:,.1f} GW", period)
                else:
                    col.metric(f"{ba} demand", "—", "no data")
            except Exception as e:                                # noqa: BLE001
                col.metric(f"{ba} demand", "—", "fetch failed")
                col.caption(f"{e}")
    else:
        st.caption("Enter your EIA key to pull each grid's latest total demand.")

# --------------------------------------------------------------------------- #
# TAB 6 — COMMUNITY & BACKLASH (live news + the recurring issues)
# --------------------------------------------------------------------------- #

with tab_news:
    st.subheader("Community pushback & the issues data centres face")
    st.caption("The build-out isn't frictionless: towns are pausing or blocking "
               "projects over power bills, water, noise, and land use. Recurring "
               "themes below, plus a live feed — news (Google) or grassroots "
               "sentiment (Reddit), no key required.")

    st.markdown("#### The recurring flashpoints")
    issues = [
        ("💵", "Electricity bills & grid strain",
         "Surging data-centre load raises wholesale prices and can shift "
         "transmission/capacity costs onto ordinary ratepayers; PJM's capacity "
         "price spiked ~10× on data-centre-driven demand. Utilities also delay "
         "fossil-plant retirements to serve the load."),
        ("💧", "Water",
         "Evaporative cooling consumes potable water — millions of gallons a day "
         "at a large campus — a flashpoint in drought-prone metros (Phoenix, "
         "Texas, Georgia)."),
        ("🏘️", "Zoning, land use & moratoria",
         "Counties are enacting moratoria or rejecting rezonings amid resident "
         "opposition; some developers are pulling out of hostile jurisdictions."),
        ("🔊", "Noise",
         "Chillers and backup generators produce a constant low-frequency hum; "
         "noise complaints have driven lawsuits and setback rules (notably in "
         "Northern Virginia)."),
        ("🧾", "Tax breaks vs. local benefit",
         "Big sales/property-tax abatements versus relatively few permanent jobs "
         "fuel debate over whether the local trade-off pays off."),
        ("🛢️", "Backup diesel & air permits",
         "Fleets of diesel generators for backup draw air-quality scrutiny and "
         "permit fights near residential areas."),
    ]
    cards = st.columns(3)
    for i, (icon, head, body) in enumerate(issues):
        with cards[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {icon}\n**{head}**")
                st.caption(body)

    st.divider()
    st.markdown("#### Moratorium & ban tracker")
    st.caption("Towns, counties and states that have paused or blocked data "
               "centres. Point-in-time snapshot (mid-2026) compiled from public "
               "trackers — dozens more churn weekly, so follow the links below "
               "for live status. Not exhaustive.")

    enacted = MORATORIUMS_DF[MORATORIUMS_DF.status == "Enacted"]
    proposed = MORATORIUMS_DF[MORATORIUMS_DF.status == "Proposed"]
    q1, q2, q3 = st.columns(3)
    q1.metric("Enacted (listed)", f"{len(enacted)}")
    q2.metric("Proposed / considering", f"{len(proposed)}")
    q3.metric("States represented", f"{MORATORIUMS_DF.state.nunique()}")
    st.caption("Trackers report **50+ localities enacted** nationally (North "
               "Carolina alone has 20+); the table lists a representative subset.")

    fstat = st.multiselect(
        "Filter by status",
        list(MORATORIUMS_DF.status.unique()),
        default=["Enacted", "Proposed"])
    mdf = MORATORIUMS_DF[MORATORIUMS_DF.status.isin(fstat)] if fstat else MORATORIUMS_DF

    tcol, ccol = st.columns([3, 2])
    with tcol:
        st.dataframe(
            mdf[["locality", "state", "level", "status", "when", "note"]],
            use_container_width=True, hide_index=True, height=360,
            column_config={"locality": "Locality", "state": "State",
                           "level": "Level", "status": "Status",
                           "when": "When", "note": "Note"})
    with ccol:
        by_state = (mdf.groupby("state").size().reset_index(name="n")
                    .sort_values("n", ascending=False))
        chart = (alt.Chart(by_state).mark_bar().encode(
            x=alt.X("n:Q", title="Localities / actions"),
            y=alt.Y("state:N", sort="-x", title=None),
            tooltip=["state", "n"],
            color=alt.Color("n:Q", scale=alt.Scale(scheme="reds"), legend=None),
        ).properties(height=360))
        st.altair_chart(chart, use_container_width=True)

    st.caption("Trackers: " + " · ".join(
        src_link(k) for k in ["icap_mor", "dcbans", "gjf_mor", "rockinst"]))

    st.divider()
    st.markdown("#### Live discussion")
    csrc, cth = st.columns([1, 2])
    feed = csrc.radio("Source", ["📰 News", "👥 Reddit"], horizontal=True)
    theme = cth.selectbox("Theme", list(NEWS_THEMES.keys()))
    extra = st.text_input("Add a place or keyword (optional)",
                          placeholder="e.g. Virginia, Georgia, Tucson")
    query = NEWS_THEMES[theme] + (f" {extra}" if extra.strip() else "")

    # --- fetch + normalize both feeds to a common {title, link, meta, dt} shape --- #
    items, err, disclaimer = None, None, ""
    if feed == "📰 News":
        raw, err = fetch_news(query)
        disclaimer = ("Headlines are an automated news search, unfiltered and not "
                      "endorsements; follow the link to the original outlet.")
        if raw:
            items = [{"title": a["title"], "link": a["link"], "when": a["published"],
                      "meta": " · ".join(x for x in (a["source"], a["published"]) if x),
                      "dt": pd.to_datetime(a["published"], errors="coerce")}
                     for a in raw]
    else:
        raw, err = fetch_reddit(query, sort="new")
        disclaimer = ("Reddit threads are user posts — anecdotal and unverified; a "
                      "read on local sentiment, not reporting.")
        if raw:
            items = [{"title": p["title"], "link": p["link"], "when": p["created"],
                      "meta": " · ".join(x for x in (p["subreddit"], p["created"]) if x),
                      "dt": pd.to_datetime(p["created"], errors="coerce")}
                     for p in raw]

    if err or items is None:
        reddit_url = ("https://www.reddit.com/search/?q="
                      + urllib.parse.quote(query) + "&sort=new")
        if feed == "👥 Reddit":
            st.warning("Couldn't load the Reddit feed right now (it rate-limits "
                       "rapid requests — try again in a moment).")
            st.markdown(f"🔗 **[Open this search on Reddit]({reddit_url})** — or "
                        "browse r/energy, r/RealEstate, r/climate, and your local "
                        "city/county subreddit.")
        else:
            st.warning("Couldn't reach Google News (offline or blocked).")
        st.caption(f"Detail: {err}")
    elif not items:
        st.info("Nothing for this theme right now — try another or add a place.")
    else:
        # newest first; items with an unparseable date sink to the bottom
        items.sort(key=lambda it: it["dt"] if pd.notna(it["dt"]) else pd.Timestamp.min,
                   reverse=True)
        st.caption(f"{len(items)} items • “{query}” • newest first")
        for it in items:
            st.markdown(f"- [{it['title']}]({it['link']})  \n"
                        f"  <small style='color:#888'>{it['meta']}</small>",
                        unsafe_allow_html=True)

    st.caption(disclaimer)

# --------------------------------------------------------------------------- #
# TAB 7 — MACRO OUTLOOK
# --------------------------------------------------------------------------- #

with tab_macro:
    st.subheader("Global data-centre electricity — IEA outlook")
    line = (alt.Chart(IEA_OUTLOOK).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X("year:O", title=None), y=alt.Y("twh:Q", title="TWh / year"),
        tooltip=["year", "twh"]).properties(height=320))
    st.altair_chart(line, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("2024 → 2030", "~415 → 945 TWh", "≈ Japan's total demand")
    c2.metric("Share of global electricity, 2030", "~3%")
    c3.metric("Data-centre CO₂, 2030", "~1%", "of global emissions")

    st.markdown(
        "- AI's slice of data-centre power is projected to climb from **5–15%** recently "
        "to **35–50% by 2030**.\n"
        "- **Inference dominates**: it accounts for the majority of a model's lifetime "
        "energy (>90% by some operator accounts) — *usage*, not training, is the lever.\n"
        "- **Jevons paradox:** per-query efficiency keeps improving (Gemini fell ~33× in "
        "a year), but cheaper inference drives more usage — total load still rises.")

# --------------------------------------------------------------------------- #
# TAB 8 — METHODOLOGY
# --------------------------------------------------------------------------- #

with tab_method:
    st.subheader("Sources & coefficients")
    for key in ["google_2025", "openai_2025", "epoch_2025", "hungry_2025",
                "mlenergy", "iea_2025", "gpt5_report", "eia930", "pjm_dm2",
                "cbre_dc", "cbre_glob", "ercot_ll", "pjm_lf", "eia_va",
                "google_news", "reddit", "icap_mor", "dcbans", "gjf_mor",
                "rockinst", "elmaps", "watttime", "gridstatus"]:
        st.markdown(f"- {src_link(key)}")

    st.divider()
    st.subheader("Coefficient table (per query, median text prompt)")
    tbl = pd.DataFrame([{"Source": k, "Wh": v["energy_wh"], "gCO₂e": v["co2_g"],
                         "mL water": v["water_ml"]} for k, v in QUERY_COEFFS.items()])
    st.dataframe(tbl, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Read the numbers carefully")
    st.markdown(
        "- **Scope matters most.** Chip-only figures (~0.10 Wh) roughly halve full-stack "
        "(~0.24 Wh). Google's excludes training, network, and end-user device energy.\n"
        "- **Carbon accounting.** Market-based (PPA/certificate) intensity can be ~⅓ of "
        "location-based grid intensity. The Calculator and Grid tab let you pick.\n"
        "- **ML.ENERGY live numbers** are min-energy (max-batch) configs on H100/B200 — a "
        "well-utilised server, so a lower bound vs. bursty real traffic.\n"
        "- **Text only.** Image/video/reasoning prompts cost materially more.\n"
        "- **Water is indirect too.** Most disclosures count cooling water, not water "
        "embedded in generating the electricity.\n"
        "- **Grid timing** can run live on **PJM Data Miner 2** (marginal CO₂ in "
        "lbs/MWh, or fuel-mix × emission factors); other ISOs use stylized curves "
        "until a feed is wired. **Marginal** intensity is the right signal for "
        "load-shifting; **average** (fuel-mix) answers a different question.")

st.divider()
st.caption("Scaffold — static coefficients live at the top of app.py; live model data "
           "streams from the ML.ENERGY leaderboard. Not affiliated with any provider.")
