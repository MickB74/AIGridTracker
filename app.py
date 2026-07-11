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
import time
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

# Third-party GLOBAL data-centre electricity forecasts (TWh) — same metric so
# they're comparable. Shows how much the projections diverge by year/scenario.
DC_FORECASTS = pd.DataFrame([
    {"source": "IEA (base)",     "year": 2030, "twh": 945,  "src": "iea_2025"},
    {"source": "IEA (base)",     "year": 2035, "twh": 1200, "src": "iea_2025"},
    {"source": "IEA (lift-off)", "year": 2035, "twh": 1700, "src": "iea_2025"},
    {"source": "Gartner",        "year": 2030, "twh": 980,  "src": "gartner"},
    {"source": "451 Research",   "year": 2030, "twh": 1587, "src": "sp_451"},
    {"source": "BloombergNEF",   "year": 2035, "twh": 1200, "src": "bnef"},
    {"source": "BloombergNEF",   "year": 2050, "twh": 3700, "src": "bnef"},
])

# US-only data-centre electricity forecasts for 2030 (TWh). The spread is the
# story: central estimates run ~350 → ~970 TWh. Scenario/range midpoints noted.
DC_FORECASTS_US = pd.DataFrame([
    {"source": "Goldman Sachs / McKinsey", "twh": 350, "note": "~300–400 range", "src": "wri_range"},
    {"source": "IEA",                      "twh": 425, "note": "~8% of US power", "src": "iea_2025"},
    {"source": "LBNL (Berkeley Lab)",      "twh": 450, "note": "range 325–580",  "src": "lbnl"},
    {"source": "EPRI (medium)",            "twh": 590, "note": "13% of US power", "src": "epri_pi"},
    {"source": "EPRI (high)",              "twh": 790, "note": "17% of US power", "src": "epri_pi"},
    {"source": "BCG",                      "twh": 970, "note": "high end",        "src": "wri_range"},
])

# Major data-centre markets — OPERATIONAL commissioned power (MW), ~2025.
# Market-level totals from broker inventories (CBRE / Cushman & Wakefield /
# datacenterHawk) — NOT per-facility disclosures, which operators don't publish.
# grid = the ISO/grid feed this app can pull carbon for ("" = not yet wired).
# Approximate; sources on the Methodology tab and in each row's `src`.
# Market power (MW) across three phases, so the app can toggle the metric:
#   mw       = OPERATIONAL / commissioned (CBRE North America & Global 2025)
#   uc       = UNDER CONSTRUCTION (JLL year-end 2025; NoVA per Cushman & Wakefield)
#   planned  = PLANNED PIPELINE beyond current construction (JLL year-end 2025)
# None = that phase isn't broken out for the market in the cited reports.
DATACENTERS = [
    # name, region, country, grid, lat, lon, mw, uc, planned, src
    ("Northern Virginia (Ashburn)", "US", "USA", "PJM",   38.98, -77.46, 4900, 6300, 5900, "cbre_dc"),
    ("Dallas–Fort Worth",           "US", "USA", "ERCO",  32.78, -96.80, 1650, None, 3900, "cbre_dc"),
    ("Phoenix",                     "US", "USA", "",      33.45, -112.07, 1380, 1300, 4200, "cbre_dc"),
    ("Atlanta",                     "US", "USA", "",      33.75, -84.39, 1300, 1110, None, "cbre_dc"),
    ("Chicago",                     "US", "USA", "PJM",   41.85, -87.65, 1200, 1180, None, "cbre_dc"),
    ("Silicon Valley (Santa Clara)","US", "USA", "CISO",  37.35, -121.95, 950, None, None, "cbre_dc"),
    ("Columbus (Central Ohio)",     "US", "USA", "PJM",   39.96, -83.00,  700, None, None, "cbre_dc"),
    ("Portland / Hillsboro",        "US", "USA", "",      45.52, -122.98, 600, None, None, "cbre_dc"),
    ("Beijing",              "APAC", "China",      "", 39.90, 116.40, 1799, None, None, "cbre_glob"),
    ("London",               "EMEA", "UK",         "", 51.51,  -0.13, 1189, None, None, "cbre_glob"),
    ("Sydney",               "APAC", "Australia",  "", -33.87, 151.21, 1050, None, None, "cbre_glob"),
    ("Tokyo",                "APAC", "Japan",      "", 35.68, 139.69, 1000, None, None, "cbre_glob"),
    ("Shanghai",             "APAC", "China",      "", 31.23, 121.47, 1000, None, None, "cbre_glob"),
    ("Singapore",            "APAC", "Singapore",  "",  1.35, 103.82, 1000, None, None, "cbre_glob"),
    ("Frankfurt",            "EMEA", "Germany",    "", 50.11,   8.68,  900, None, None, "cbre_glob"),
    ("Dublin",               "EMEA", "Ireland",    "", 53.35,  -6.26,  700, None, None, "cbre_glob"),
    ("Amsterdam",            "EMEA", "Netherlands","", 52.37,   4.90,  550, None, None, "cbre_glob"),
    ("Paris",                "EMEA", "France",     "", 48.86,   2.35,  500, None, None, "cbre_glob"),
]
DATACENTERS_DF = pd.DataFrame(
    DATACENTERS,
    columns=["market", "region", "country", "grid", "lat", "lon",
             "mw", "uc", "planned", "src"])

# First-party hyperscaler campuses — self-published LOCATIONS (no per-facility MW
# disclosed). Google: datacenters.google/locations (active US). Meta:
# datacenters.atmeta.com/us-locations. Coords approximate (town/county centroid).
HYPERSCALERS = [
    # company, location, state, lat, lon, src
    ("Google", "The Dalles", "OR", 45.59, -121.18, "google_dc"),
    ("Google", "Council Bluffs", "IA", 41.26, -95.86, "google_dc"),
    ("Google", "Douglas County", "GA", 33.75, -84.75, "google_dc"),
    ("Google", "Ellis County", "TX", 32.35, -96.85, "google_dc"),
    ("Google", "Henderson", "NV", 36.04, -114.98, "google_dc"),
    ("Google", "New Carlisle", "IN", 41.70, -86.51, "google_dc"),
    ("Google", "Jackson County", "AL", 34.75, -85.86, "google_dc"),
    ("Google", "Lenoir", "NC", 35.91, -81.54, "google_dc"),
    ("Google", "Mayes County", "OK", 36.31, -95.32, "google_dc"),
    ("Google", "Midlothian", "TX", 32.48, -96.99, "google_dc"),
    ("Google", "Montgomery County", "TN", 36.53, -87.36, "google_dc"),
    ("Google", "Northern Virginia", "VA", 39.02, -77.48, "google_dc"),
    ("Google", "Papillion", "NE", 41.15, -96.04, "google_dc"),
    ("Google", "Red Oak", "TX", 32.52, -96.80, "google_dc"),
    ("Google", "Storey County", "NV", 39.44, -119.42, "google_dc"),
    ("Google", "New Albany (Central Ohio)", "OH", 40.08, -82.81, "google_dc"),
    ("Google", "Omaha", "NE", 41.26, -95.94, "google_dc"),
    ("Google", "The Lowcountry (Berkeley Co.)", "SC", 33.20, -80.01, "google_dc"),
    ("Meta", "Prineville", "OR", 44.30, -120.83, "meta_dc"),
    ("Meta", "Altoona", "IA", 41.64, -93.46, "meta_dc"),
    ("Meta", "Fort Worth", "TX", 32.76, -97.33, "meta_dc"),
    ("Meta", "Temple", "TX", 31.10, -97.34, "meta_dc"),
    ("Meta", "El Paso", "TX", 31.76, -106.49, "meta_dc"),
    ("Meta", "Los Lunas", "NM", 34.81, -106.73, "meta_dc"),
    ("Meta", "New Albany", "OH", 40.08, -82.80, "meta_dc"),
    ("Meta", "Bowling Green", "OH", 41.37, -83.65, "meta_dc"),
    ("Meta", "DeKalb", "IL", 41.93, -88.75, "meta_dc"),
    ("Meta", "Forest City", "NC", 35.33, -81.86, "meta_dc"),
    ("Meta", "Gallatin", "TN", 36.39, -86.45, "meta_dc"),
    ("Meta", "Stanton Springs (Newton Co.)", "GA", 33.60, -83.71, "meta_dc"),
    ("Meta", "Sarpy County", "NE", 41.10, -96.11, "meta_dc"),
    ("Meta", "Eagle Mountain", "UT", 40.31, -112.01, "meta_dc"),
    ("Meta", "Mesa", "AZ", 33.42, -111.83, "meta_dc"),
    ("Meta", "Huntsville", "AL", 34.73, -86.59, "meta_dc"),
    ("Meta", "Montgomery", "AL", 32.37, -86.30, "meta_dc"),
    ("Meta", "Kuna", "ID", 43.49, -116.42, "meta_dc"),
    ("Meta", "Jeffersonville", "IN", 38.28, -85.74, "meta_dc"),
    ("Meta", "Lebanon", "IN", 40.05, -86.47, "meta_dc"),
    ("Meta", "Richland Parish", "LA", 32.47, -91.75, "meta_dc"),
    ("Meta", "Rosemount", "MN", 44.74, -93.13, "meta_dc"),
    ("Meta", "Kansas City", "MO", 39.10, -94.58, "meta_dc"),
    ("Meta", "Tulsa", "OK", 36.15, -95.99, "meta_dc"),
    ("Meta", "Aiken", "SC", 33.56, -81.72, "meta_dc"),
    ("Meta", "Henrico", "VA", 37.56, -77.40, "meta_dc"),
    ("Meta", "Beaver Dam", "WI", 43.46, -88.84, "meta_dc"),
    ("Meta", "Cheyenne", "WY", 41.14, -104.82, "meta_dc"),
]
HYPERSCALERS_DF = pd.DataFrame(
    HYPERSCALERS, columns=["company", "location", "state", "lat", "lon", "src"])
HYPERSCALER_COLORS = {"Google": "#34a853", "Meta": "#0866ff", "Microsoft": "#f25022"}

# Metric toggle config: label -> (column, source keys, blurb).
DC_METRICS = {
    "Operational (running today)":
        ("mw", ["cbre_dc", "cbre_glob"],
         "Commissioned & running. CBRE North America & Global Data Center Trends 2025."),
    "Under construction":
        ("uc", ["jll_dc", "cushman_dc"],
         "Being built now. JLL year-end 2025; Northern Virginia per Cushman & Wakefield. "
         "US markets only; blank = not broken out."),
    "Planned pipeline":
        ("planned", ["jll_dc"],
         "Announced/planned beyond current construction. JLL year-end 2025. "
         "US markets only; blank = not broken out."),
}

# Data-centre moratoriums / bans — POINT-IN-TIME SNAPSHOT (mid-2026). Compiled
# from public trackers (see MORATORIUM_TRACKERS); dozens more churn weekly, so
# treat as illustrative, not exhaustive — follow the tracker links for current
# status. level: Local/State. status: Enacted/Proposed/Rejected/Vetoed.
MORATORIUMS = [
    # locality, state, level, status, when, note, lat, lon
    ("Minneapolis", "MN", "Local", "Enacted", "May 2026", "", 44.98, -93.27),
    ("Denver", "CO", "Local", "Enacted", "May 2026", "", 39.74, -104.99),
    ("Baltimore City", "MD", "Local", "Enacted", "May 2026", "", 39.29, -76.61),
    ("Reno", "NV", "Local", "Enacted", "May 2026", "", 39.53, -119.81),
    ("Dubuque County", "IA", "Local", "Enacted", "2026", "", 42.47, -90.88),
    ("Bloomington", "IL", "Local", "Enacted", "2026", "", 40.48, -88.99),
    ("Normal", "IL", "Local", "Enacted", "2026", "", 40.51, -88.99),
    ("Iron County", "UT", "Local", "Enacted", "2026", "", 37.68, -113.06),
    ("Manitowoc County", "WI", "Local", "Enacted", "2026", "18-month", 44.09, -87.66),
    ("Smithfield", "RI", "Local", "Enacted", "2026", "Outright ban", 41.92, -71.55),
    ("Meridian Township", "MI", "Local", "Enacted", "2026", "", 42.72, -84.42),
    ("Washington Township (Macomb Co.)", "MI", "Local", "Enacted", "2026", "", 42.72, -82.92),
    ("Hill County", "TX", "Local", "Enacted", "2026", "Under developer lawsuit", 32.01, -97.13),
    ("DeKalb County", "GA", "Local", "Enacted", "2026", "", 33.77, -84.23),
    ("Lysander (Onondaga Co.)", "NY", "Local", "Enacted", "May 2026", "6-month", 43.17, -76.35),
    ("Perth (Fulton Co.)", "NY", "Local", "Enacted", "Jun 2025", "1-year", 43.05, -74.19),
    ("Groton", "CT", "Local", "Enacted", "2025", "Year-long", 41.35, -72.08),
    ("Peculiar", "MO", "Local", "Enacted", "2025", "Ban", 38.72, -94.46),
    ("Bangor", "ME", "Local", "Enacted", "2025", "Temporary ban", 44.80, -68.77),
    # North Carolina — 20+ jurisdictions since late 2025
    ("Gates County", "NC", "Local", "Enacted", "Dec 2025", "", 36.44, -76.70),
    ("Brevard", "NC", "Local", "Enacted", "Sep 2025", "", 35.23, -82.73),
    ("Clay County", "NC", "Local", "Enacted", "Sep 2025", "", 35.06, -83.75),
    ("Canton", "NC", "Local", "Enacted", "Feb 2026", "", 35.53, -82.84),
    ("Chatham County", "NC", "Local", "Enacted", "Feb 2026", "", 35.70, -79.26),
    ("Kings Mountain", "NC", "Local", "Enacted", "Feb 2026", "", 35.25, -81.34),
    ("Boone", "NC", "Local", "Enacted", "Mar 2026", "", 36.22, -81.67),
    ("Apex", "NC", "Local", "Enacted", "Apr 2026", "", 35.73, -78.85),
    ("Orange County", "NC", "Local", "Enacted", "Apr 2026", "", 36.06, -79.12),
    ("Rowan County", "NC", "Local", "Enacted", "Apr 2026", "", 35.64, -80.47),
    ("Swain County", "NC", "Local", "Enacted", "Apr 2026", "", 35.49, -83.49),
    ("Watauga County", "NC", "Local", "Enacted", "2026", "Ban", 36.23, -81.69),
    ("Madison County", "NC", "Local", "Enacted", "2026", "Ban", 35.85, -82.70),
    ("Clyde", "NC", "Local", "Enacted", "2026", "Ban", 35.53, -82.91),
    # Proposed / under consideration
    ("Charlotte", "NC", "Local", "Proposed", "2026", "Council deadlocked 5–5", 35.23, -80.84),
    ("Durham", "NC", "Local", "Proposed", "2026", "", 35.99, -78.90),
    ("Harnett County", "NC", "Local", "Proposed", "2026", "", 35.37, -78.87),
    ("Cumberland County", "NC", "Local", "Proposed", "2026", "", 35.05, -78.83),
    ("Fayetteville", "NC", "Local", "Proposed", "2026", "", 35.05, -78.88),
    ("Seattle", "WA", "Local", "Proposed", "Jun 2026", "", 47.61, -122.33),
    ("Indianapolis", "IN", "Local", "Proposed", "Jun 2026", "Non-binding pause", 39.77, -86.16),
    ("Pulaski County", "AR", "Local", "Proposed", "2026", "", 34.75, -92.29),
    ("St. Lawrence County", "NY", "Local", "Proposed", "2026", "Urged municipalities", 44.59, -75.16),
    # Rejected
    ("Cheyenne", "WY", "Local", "Rejected", "2026", "Voted down 8–1", 41.14, -104.82),
    # State-level (no single map point)
    ("New York (statewide)", "NY", "State", "Proposed", "Jun 2026", "Passed legislature; awaiting governor", None, None),
    ("Georgia (HB 1012)", "GA", "State", "Proposed", "2026", "Permit bar to Mar 2027", None, None),
    ("Maine (statewide)", "ME", "State", "Vetoed", "Apr 2026", "Governor veto", None, None),
    ("Ohio (ballot measure)", "OH", "State", "Rejected", "2026", "Failed signature threshold", None, None),
]
MORATORIUMS_DF = pd.DataFrame(
    MORATORIUMS,
    columns=["locality", "state", "level", "status", "when", "note", "lat", "lon"])

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
    "jll_dc":       ("JLL — North America Data Center Report, Year-end 2025 (under-construction & planned MW)",
                     "https://www.jll.com/en-us/insights/market-dynamics/north-america-data-centers"),
    "cushman_dc":   ("Cushman & Wakefield — Americas Data Center Update H2 2025 (Virginia under-construction)",
                     "https://www.cushmanwakefield.com/en/insights/americas-data-center-update"),
    "google_dc":    ("Google — Data center locations (first-party)",
                     "https://datacenters.google/locations/"),
    "meta_dc":      ("Meta — US data center locations (first-party)",
                     "https://datacenters.atmeta.com/us-locations/"),
    "imasons":      ("Infrastructure Masons (iMasons) — industry & sustainability data",
                     "https://imasons.org/"),
    "bnef":         ("BloombergNEF (BNEF) — data-centre power-demand research & forecasts",
                     "https://about.bnef.com/"),
    "ercot_ll":     ("ERCOT — Large Load Interconnection Queue (Dec 2025 board update)",
                     "https://www.ercot.com/gridinfo/load"),
    "pjm_lf":       ("PJM — 2025 Long-Term Load Forecast (data-centre-driven growth)",
                     "https://www.pjm.com/-/media/DotCom/library/reports-notices/load-forecast/2025-load-report.pdf"),
    "eia_va":       ("EIA — Commercial electricity sales in Virginia driven by data centers (2025)",
                     "https://www.eia.gov/todayinenergy/detail.php?id=67664"),
    "eia_pilot":    ("EIA — Pilot survey on energy use at data centers (Mar 2026)",
                     "https://www.eia.gov/pressroom/releases/press585.php"),
    "gartner":      ("Gartner — data-centre electricity to double by 2030 (~980 TWh)",
                     "https://www.gartner.com/en/newsroom/press-releases/2025-11-17-gartner-says-electricity-demand-for-data-centers-to-grow-16-percent-in-2025-and-double-by-2030"),
    "bnef_106":     ("BloombergNEF — US data-centre power demand ~106 GW by 2035",
                     "https://www.utilitydive.com/news/us-data-center-power-demand-could-reach-106-gw-by-2035-bloombergnef/806972/"),
    "wri_range":    ("World Resources Institute — US 2030 forecasts span 206–970 TWh",
                     "https://www.wri.org/insights/us-data-centers-electricity-demand"),
    "sp_451":       ("S&P Global / 451 Research — global data-centre demand ~1,587 TWh by 2030",
                     "https://www.spglobal.com/energy/en/news-research/latest-news/electric-power/110525-global-data-center-power-demand-expected-to-almost-double-by-2030"),
    "epri_pi":      ("EPRI — Powering Intelligence 2026 (US Low/Medium/High scenarios)",
                     "https://powering-intelligence.epri.com/summary-projections.html"),
    "lbnl":         ("Lawrence Berkeley National Lab — US data centres 325–580 TWh by 2030",
                     "https://eta.lbl.gov/publications/2024-united-states-data-center-energy"),
    # --- Governor data-centre stances (Officials tab) ---
    "ga_kemp":      ("Georgia governor vetoes bill to pause data-center tax breaks (2024)",
                     "https://www.datacenterdynamics.com/en/news/georgia-governor-vetoes-bill-to-pause-data-center-tax-breaks/"),
    "tx_sb6":       ("Gov. Abbott signs SB 6 — large-load grid rules (2025)",
                     "https://www.forbes.com/sites/davidblackmon/2025/06/22/gov-greg-abbott-signs-sb-6-to-improve-texas-grid-reliability/"),
    "la_landry":    ("Gov. Landry — Meta $10B Louisiana data center (2025)",
                     "https://gov.louisiana.gov/news/4697"),
    "va_span":      ("Gov. Spanberger signs energy legislation on data centers (2026)",
                     "https://www.governor.virginia.gov/newsroom/news-releases/2026/july-releases/name-1120725-en.html"),
    "pa_shapiro":   ("Gov. Shapiro releases GRID standards for data centers (2026)",
                     "https://www.pa.gov/governor/newsroom/2026-press-releases/gov-shapiro-releases-full-grid-standards-to-protect-pennsylvania"),
    "az_hobbs":     ("Arizona data-center tax pause signed by Gov. Hobbs (2026)",
                     "https://news.bloombergtax.com/daily-tax-report-state/arizona-data-center-tax-incentive-pause-signed-by-governor-hobbs"),
    "oh_dewine":    ("Gov. DeWine pauses Ohio data-center tax exemption (2026)",
                     "https://governor.ohio.gov/wps/portal/gov/governor/media/news-and-media/governor-dewine-announces-pause-of-data-center-tax-exemption"),
    "wi_evers":     ("Gov. Evers announces Microsoft $4B Wisconsin data center (2025)",
                     "https://wedc.org/gov-evers-microsoft-officials-announce-new-4-billion-investment-in-mount-pleasant-datacenter/"),
    "ut_cox":       ("Gov. Cox signs EO — higher bar for data-center development (2026)",
                     "https://governor.utah.gov/wp-content/uploads/2026.05.29-EO-Higher-Bar-for-Data-Center-Development-1.pdf"),
    "nv_lombardo":  ("Gov. Lombardo backs data centers with closed-loop water rule (2026)",
                     "https://nevadacurrent.com/2026/06/04/lombardo-backs-natural-gas-pipeline-expansion-for-data-centers/"),
    "or_kotek":     ("Gov. Kotek convenes Oregon Data Center Advisory Committee (2026)",
                     "https://oregoncapitalchronicle.com/2026/01/20/oregon-governor-forms-new-committee-to-advise-on-massive-data-center-growth/"),
    "in_braun":     ("Gov. Braun — hyperscalers must pay, opposes tax abatements (2026)",
                     "https://www.wfyi.org/public-affairs/2026-03-09/governor-braun-touts-efforts-to-bring-down-energy-costs-following-legislative-session-highlights-data-center-agreement"),
    "google_news":  ("Google News — live headline search (Community & backlash tab)",
                     "https://news.google.com/"),
    "reddit":       ("Reddit — public search JSON (grassroots sentiment; Community & backlash tab)",
                     "https://www.reddit.com/"),
    "icap_mor":     ("Interconnected Capital — US Data Center Moratorium Tracker (2026)",
                     "https://www.interconnectedcapital.com/research/data-center-moratoriums"),
    "dcbans":       ("DataCenterBans.com — moratorium & ban tracker",
                     "https://www.datacenterbans.com/"),
    "dcopp":        ("Data Center Opposition — grassroots opposition & local fights tracker",
                     "https://datacenteropposition.com/"),
    "dcwatch":      ("Data Center Watch — activist-group & blocked/delayed-project tracker",
                     "https://www.datacenterwatch.org/report"),
    "dcresp":       ("Coalition for Responsible Data Center Development — map of community organizations",
                     "https://www.datacenterresponsibility.com/mapofcommunityorganizations"),
    "dctrack":      ("Data Center Tracker — community response & legislative-action database",
                     "https://datacentertracker.org/"),
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

# Official company hubs / reports / press releases on data centres & communities.
# (category, company, what it is, url) — first-party material: economic-impact
# reports, community pledges, newsrooms. Curated landing pages, not one-off links.
COMPANY_STATEMENTS = [
    # --- Hyperscalers & AI cloud ---
    ("Hyperscalers & AI cloud", "Amazon / AWS",
     "Impact in communities hub + 2025 economic-impact report",
     "https://www.aboutamazon.com/aws-impact-in-communities"),
    ("Hyperscalers & AI cloud", "Amazon / AWS",
     "Data centres: water & electricity use explainer",
     "https://www.aboutamazon.com/news/sustainability/amazon-data-centers-electricity-bills-water-use"),
    ("Hyperscalers & AI cloud", "Google",
     "Accelerating economies — 2025 Data Center Community Impact Report",
     "https://datacenters.google/accelerating-economies/"),
    ("Hyperscalers & AI cloud", "Microsoft",
     "Datacenter Community Pledge (Local blog)",
     "https://local.microsoft.com/blog/microsofts-datacenter-community-pledge/"),
    ("Hyperscalers & AI cloud", "Microsoft",
     "Community-First AI Infrastructure framework (Jan 2026)",
     "https://blogs.microsoft.com/on-the-issues/2026/01/13/community-first-ai-infrastructure/"),
    ("Hyperscalers & AI cloud", "Meta",
     "Data Centers — Economic impact & growing local economies",
     "https://datacenters.atmeta.com/economic-impact/"),
    ("Hyperscalers & AI cloud", "CoreWeave",
     "Newsroom — project & jobs announcements",
     "https://www.coreweave.com/newsroom"),
    ("Hyperscalers & AI cloud", "CoreWeave",
     "Data Centers Explained: myths, facts & answers",
     "https://www.coreweave.com/blog/the-data-center-questions-everyone-is-asking-answered"),
    # --- Colocation & wholesale developers ---
    ("Colocation & wholesale developers", "QTS",
     "Community Commitments (energy, water, jobs, transparency)",
     "https://q.com/commitments/"),
    ("Colocation & wholesale developers", "Digital Realty",
     "2025 Impact Report",
     "https://www.digitalrealty.com/resources/reports/impact-report"),
    ("Colocation & wholesale developers", "Equinix",
     "Newsroom — press releases & workforce/community investment",
     "https://newsroom.equinix.com/"),
    ("Colocation & wholesale developers", "Vantage Data Centers",
     "Our approach to responsible growth + news",
     "https://blog.vantage-dc.com/2026/03/26/our-approach-to-responsible-growth/"),
    ("Colocation & wholesale developers", "Prime Data Centers",
     "Community Commitment (energy, water, air, noise)",
     "https://primedatacenters.com/community-commitment/"),
    ("Colocation & wholesale developers", "CyrusOne",
     "Communities commitments + 2025 Sustainability Report",
     "https://www.cyrusone.com/commitments/communities"),
    ("Colocation & wholesale developers", "Aligned Data Centers",
     "Empowering the community",
     "https://aligneddc.com/community/"),
    ("Colocation & wholesale developers", "EdgeConneX",
     "Sustainability — annual report & goals",
     "https://www.edgeconnex.com/company/sustainability/"),
    ("Colocation & wholesale developers", "STACK Infrastructure",
     "Responsibility — community stewardship & Impact report",
     "https://www.stackinfra.com/responsibility/"),
    ("Colocation & wholesale developers", "Switch",
     "Sustainability — community partnerships & ESG report",
     "https://www.switch.com/sustainability/"),
]

# Operator -> Google-News search term for the live press-release feed. Keyed by a
# clean brand token (drops "/ AWS", "Data Centers", etc. that hurt recall).
COMPANY_FEED_TERMS = {
    "Amazon / AWS": "AWS",
    "Google": '"Google" data center',
    "Microsoft": '"Microsoft" datacenter',
    "Meta": '"Meta" data center',
    "CoreWeave": "CoreWeave",
    "QTS": '"QTS" data center',
    "Digital Realty": '"Digital Realty"',
    "Equinix": "Equinix",
    "Vantage Data Centers": '"Vantage Data Centers"',
    "Prime Data Centers": '"Prime Data Centers"',
    "CyrusOne": "CyrusOne",
    "Aligned Data Centers": '"Aligned" data center',
    "EdgeConneX": "EdgeConneX",
    "STACK Infrastructure": '"STACK Infrastructure"',
    "Switch": '"Switch" data center',
}

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
#
# On shared datacenter IPs (Streamlit Cloud), the www host rate-limits hard:
# a 429 can hit the very first request because many apps share the IP. But
# old.reddit.com serves the same search.rss from different infrastructure that
# doesn't throttle nearly as aggressively — so we hit it first and only fall
# back to www if it's unreachable. A unique, identifying User-Agent (per
# Reddit's API rules) plus a short backoff retry further reduce 429s; a
# spoofed browser UA from a datacenter actually gets throttled the worst.
REDDIT_HOSTS = ("https://old.reddit.com/search.rss",
                "https://www.reddit.com/search.rss")
_ATOM = "{http://www.w3.org/2005/Atom}"
REDDIT_UA = "AIGridTracker/1.0 (public sentiment tab; contact via GitHub)"


def _parse_reddit_rss(content: bytes, limit: int):
    root = ET.fromstring(content)
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
    return out


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_reddit(query: str, limit: int = 15, sort: str = "relevance",
                 period: str = "year"):
    """Live Reddit threads via the public Atom search RSS (keyless). Returns
    (list_of_dicts, error_or_None); each dict has title/subreddit/link/created.
    Tries old.reddit.com (rarely throttled) first, then www, each with a short
    backoff retry on 429."""
    params = {"q": query, "sort": sort, "t": period}
    last = "Reddit unreachable"
    for host in REDDIT_HOSTS:
        for attempt in range(3):
            try:
                r = requests.get(host, params=params,
                                 headers={"User-Agent": REDDIT_UA}, timeout=15)
                if r.status_code == 429:
                    last = "429 (rate-limited)"
                    time.sleep(1.5 * (attempt + 1))   # 1.5s, 3s, 4.5s
                    continue
                r.raise_for_status()
                if not r.content.lstrip().startswith(b"<"):
                    raise RuntimeError("Reddit returned non-XML "
                                       "(rate-limited or blocked)")
                return _parse_reddit_rss(r.content, limit), None
            except Exception as e:                                # noqa: BLE001
                last = str(e)
                break   # network/parse error on this host — try the next host
    return None, last


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
def load_officials():
    """US senators + governors directory from officials.json (built from the
    official Senate contact XML and the current-governors list). Returns
    (DataFrame, generated_note) or (empty, error)."""
    p = pathlib.Path(__file__).resolve().parent / "officials.json"
    try:
        data = json.loads(p.read_text())
        return pd.DataFrame(data["officials"]), data.get("generated", "")
    except Exception as e:                                          # noqa: BLE001
        return pd.DataFrame(), str(e)


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

(tab_calc, tab_compare, tab_live, tab_grid, tab_dc, tab_news, tab_officials,
 tab_macro, tab_method) = st.tabs(
    ["🧮 Calculator", "📊 Compare sources", "🔬 Live models",
     "🕐 Grid timing", "🏢 Data centers", "🗞️ Community & backlash",
     "🏛️ Officials", "🌍 Macro outlook", "📚 Methodology"]
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
    st.caption("Market-level power by phase (~2025). Totals are broker inventories "
               "(CBRE / JLL / Cushman & Wakefield) — operators don't disclose "
               "per-facility MW. Toggle the phase; each is cited separately because "
               "the shops measure different things. Approximate; see **Methodology**.")

    cmet, creg = st.columns([2, 2])
    metric_label = cmet.radio("Phase", list(DC_METRICS.keys()), horizontal=True)
    col, msrcs, blurb = DC_METRICS[metric_label]
    region = creg.radio("Region", ["All", "US", "EMEA", "APAC"], horizontal=True)

    dcd = DATACENTERS_DF if region == "All" else DATACENTERS_DF[DATACENTERS_DF.region == region]
    dcd = dcd[dcd[col].notna()].copy()          # only markets with data for this phase
    dcd["val"] = dcd[col]

    st.caption(f"**{metric_label}** — {blurb}")

    if dcd.empty:
        st.info("No markets report this phase for the selected region. Try "
                "**Operational**, or switch region to **US**.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Markets shown", f"{len(dcd)}")
        m2.metric(f"{metric_label.split(' (')[0]} power", f"{dcd['val'].sum()/1000:,.1f} GW")
        m3.metric("Largest", f"{dcd.loc[dcd['val'].idxmax(), 'market'].split(' (')[0]}",
                  f"{dcd['val'].max():,.0f} MW")

        map_df = dcd.rename(columns={"lat": "latitude", "lon": "longitude"}).copy()
        map_df["size"] = map_df["val"] * 40     # radius in metres, scaled by MW
        st.map(map_df, latitude="latitude", longitude="longitude", size="size",
               color="#ff5a1f")

        bar = (alt.Chart(dcd).mark_bar().encode(
            x=alt.X("val:Q", title=f"{metric_label.split(' (')[0]} power (MW)"),
            y=alt.Y("market:N", sort="-x", title=None),
            tooltip=[alt.Tooltip("market"), alt.Tooltip("country"),
                     alt.Tooltip("grid"), alt.Tooltip("val:Q", title="MW")],
            color=alt.Color("region:N", legend=alt.Legend(title="Region")),
        ).properties(height=max(280, 26 * len(dcd))))
        st.altair_chart(bar, use_container_width=True)

        with st.expander("Table — all phases + sources"):
            show = dcd[["market", "region", "country", "grid",
                        "mw", "uc", "planned"]].copy()
            st.dataframe(
                show, use_container_width=True, hide_index=True,
                column_config={
                    "grid": "ISO feed",
                    "mw": st.column_config.NumberColumn("Operational (MW)", format="%d"),
                    "uc": st.column_config.NumberColumn("Under constr. (MW)", format="%d"),
                    "planned": st.column_config.NumberColumn("Planned (MW)", format="%d")})
            st.caption("Sources — " + " · ".join(src_link(k) for k in
                       ["cbre_dc", "cbre_glob", "jll_dc", "cushman_dc"]))

    st.caption("Sources for this phase: " + " · ".join(src_link(k) for k in msrcs))
    st.caption("⚡ Markets tagged with an **ISO feed** (ERCO / CISO / PJM) can be "
               "pulled live for carbon on the **Grid timing** tab.")

    st.divider()
    st.subheader("First-party: hyperscaler campuses")
    st.caption("Individual data-centre campuses that operators publish themselves "
               "— exact locations, from Google's and Meta's own sites. Neither "
               "discloses per-facility MW, so these are location markers (not sized "
               "by power); the broker map above is the place to read scale.")

    firms = st.multiselect("Company", list(HYPERSCALERS_DF.company.unique()),
                           default=list(HYPERSCALERS_DF.company.unique()))
    hdf = HYPERSCALERS_DF[HYPERSCALERS_DF.company.isin(firms)].copy() if firms \
        else HYPERSCALERS_DF.copy()

    if hdf.empty:
        st.info("Pick a company to plot its campuses.")
    else:
        h1, h2 = st.columns(2)
        h1.metric("Campuses shown", f"{len(hdf)}")
        h2.metric("States", f"{hdf.state.nunique()}")
        hdf["color"] = hdf["company"].map(HYPERSCALER_COLORS).fillna("#888888")
        st.map(hdf, latitude="lat", longitude="lon", color="color", size=16000)
        st.caption(" · ".join(f"{c} = {len(hdf[hdf.company==c])}"
                              for c in firms if len(hdf[hdf.company == c])) +
                   "  ·  🟢 Google · 🔵 Meta")
        with st.expander("Campus list + sources"):
            st.dataframe(hdf[["company", "location", "state"]],
                         use_container_width=True, hide_index=True,
                         column_config={"company": "Company", "location": "Location",
                                        "state": "State"})
            st.caption("First-party sources: " + " · ".join(
                src_link(k) for k in ["google_dc", "meta_dc"]))
    st.caption("Only Google and Meta publish full campus lists; Microsoft, AWS, "
               "Oracle and others disclose regions but not per-site locations as "
               "cleanly. Research/forecast context: "
               + src_link("imasons") + " · " + src_link("bnef") + ".")

    st.info(
        "📋 **Authoritative facility data is coming (EIA).** Data centres are "
        "electricity *customers*, so they've never been in federal facility data "
        "— which is why the maps above rely on broker estimates and operator "
        "self-disclosure. That's starting to change: in **March 2026 the EIA "
        "launched its first pilot survey** of data-centre energy use — 196 "
        "companies across **Texas, Washington, and Northern Virginia/DC** "
        "(electricity, cooling, IT specs, efficiency), voluntary now with a "
        "**mandatory survey to follow**. Results aren't published yet. Meanwhile "
        "EIA already powers this app's live grid data (EIA-930): the carbon "
        "curves on **Grid timing** and the live system-demand metric below. "
        + src_link("eia_pilot") + " · " + src_link("eia930") + ".")

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
    # (icon, headline, body, youtube-search-query) — the query surfaces news
    # clips / explainers that demonstrate the issue, no API key required.
    issues = [
        ("💵", "Electricity bills & grid strain",
         "Surging data-centre load raises wholesale prices and can shift "
         "transmission/capacity costs onto ordinary ratepayers; PJM's capacity "
         "price spiked ~10× on data-centre-driven demand. Utilities also delay "
         "fossil-plant retirements to serve the load.",
         "data center electricity bills ratepayers grid strain news"),
        ("💧", "Water",
         "Evaporative cooling consumes potable water — millions of gallons a day "
         "at a large campus — a flashpoint in drought-prone metros (Phoenix, "
         "Texas, Georgia).",
         "data center water use cooling drought news"),
        ("🏘️", "Zoning, land use & moratoria",
         "Counties are enacting moratoria or rejecting rezonings amid resident "
         "opposition; some developers are pulling out of hostile jurisdictions.",
         "data center zoning moratorium residents oppose rezoning news"),
        ("🔊", "Noise",
         "Chillers and backup generators produce a constant low-frequency hum; "
         "noise complaints have driven lawsuits and setback rules (notably in "
         "Northern Virginia).",
         "data center noise complaints residents hum news"),
        ("🧾", "Tax breaks vs. local benefit",
         "Big sales/property-tax abatements versus relatively few permanent jobs "
         "fuel debate over whether the local trade-off pays off.",
         "data center tax breaks incentives few jobs news"),
        ("🛢️", "Backup diesel & air permits",
         "Fleets of diesel generators for backup draw air-quality scrutiny and "
         "permit fights near residential areas.",
         "data center backup diesel generators air quality permit news"),
    ]
    cards = st.columns(3)
    for i, (icon, head, body, vquery) in enumerate(issues):
        with cards[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {icon}\n**{head}**")
                st.caption(body)
                yt_url = ("https://www.youtube.com/results?search_query="
                          + urllib.parse.quote(vquery))
                st.markdown(f"▶ **[Watch videos]({yt_url})**")

    st.divider()
    st.markdown("#### What the companies say")
    st.caption("First-party material — economic-impact reports, community "
               "pledges and newsrooms the operators themselves publish. These "
               "make the case *for* the build-out, so read them as the "
               "company's side, alongside the pushback above and the live feed "
               "below.")
    # dict preserves insertion order -> categories render in list order.
    cats = {}
    for cat, company, what, url in COMPANY_STATEMENTS:
        cats.setdefault(cat, []).append((company, what, url))
    for cat, entries in cats.items():
        st.markdown(f"**{cat}**")
        comp_cols = st.columns(3)
        for i, (company, what, url) in enumerate(entries):
            with comp_cols[i % 3]:
                st.markdown(f"**{company}** — [{what}]({url})")

    st.markdown("###### 📣 Live press releases & news")
    st.caption("Fresh Google News hits for a given operator — their own "
               "announcements plus third-party coverage, newest first. No key "
               "required; headlines are unfiltered, not endorsements.")
    pick = st.selectbox("Operator", ["All operators"]
                        + list(COMPANY_FEED_TERMS.keys()))
    if pick == "All operators":
        pr_query = ("(" + " OR ".join(COMPANY_FEED_TERMS.values()) + ") "
                    "data center (community OR jobs OR investment OR ratepayers "
                    "OR water OR moratorium)")
    else:
        pr_query = (COMPANY_FEED_TERMS[pick]
                    + " data center (community OR jobs OR investment OR "
                    "ratepayers OR water OR moratorium)")
    pr_items, pr_err = fetch_news(pr_query, limit=12)
    if pr_err or pr_items is None:
        gn_url = ("https://news.google.com/search?q="
                  + urllib.parse.quote(pr_query))
        st.warning("Couldn't reach Google News right now — "
                   f"[open this search]({gn_url}).")
    elif not pr_items:
        st.info("No recent items for this operator — try another.")
    else:
        st.caption(f"{len(pr_items)} items • newest first")
        for it in pr_items:
            meta = " · ".join(x for x in (it["source"], it["published"]) if x)
            st.markdown(f"- [{it['title']}]({it['link']})  \n"
                        f"  <small style='color:#888'>{meta}</small>",
                        unsafe_allow_html=True)

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

    # map — local actions with coordinates, coloured by status
    STATUS_COLORS = {"Enacted": "#d73027", "Proposed": "#fdae61",
                     "Rejected": "#9aa0a6", "Vetoed": "#9aa0a6"}
    geo = mdf.dropna(subset=["lat", "lon"]).copy()
    if not geo.empty:
        geo["color"] = geo["status"].map(STATUS_COLORS).fillna("#9aa0a6")
        st.map(geo, latitude="lat", longitude="lon", color="color", size=18000)
        st.caption("🔴 Enacted · 🟠 Proposed · ⚪ Rejected/Vetoed. Points are "
                   "approximate (county seat / city centre); statewide actions "
                   "aren't mapped. Zoom to see the North Carolina cluster.")

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
        src_link(k) for k in ["icap_mor", "dcbans", "dcopp", "dcwatch", "dcresp",
                               "dctrack", "gjf_mor", "rockinst"]))

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
# TAB 7 — OFFICIALS (senators + governors contact directory)
# --------------------------------------------------------------------------- #

with tab_officials:
    st.subheader("Contact your officials — senators & governors")
    st.caption("All 100 US senators and 50 governors: party, official website, "
               "and contact page — a directory for reaching decision-makers on "
               "data-centre policy, where much of the action (moratoriums, "
               "incentives, permitting) actually happens.")

    odf, ogen = load_officials()
    if odf.empty:
        st.warning("Couldn't load the officials directory.")
        st.caption(f"Detail: {ogen}")
    else:
        st.info(
            "**Two honest limits.** (1) **Stances are only shown where documented** "
            "and cited — most officials have made no public data-centre statement, "
            "so that column is usually blank; nothing is inferred. (2) Senators and "
            "governors **don't publish direct emails** — the Contact link opens "
            "their official webform. Roster: " + ogen + ".")

        f1, f2, f3 = st.columns([1.2, 1.4, 2])
        office = f1.radio("Office", ["All", "Senator", "Governor"])
        parties = f2.multiselect("Party", sorted(odf.party.unique()),
                                 default=sorted(odf.party.unique()))
        states = f3.multiselect("State", sorted(odf.state_full.unique()),
                                default=[])
        only_stance = st.checkbox("Only show officials with a documented "
                                  "data-centre stance", value=False)

        view = odf.copy()
        if office != "All":
            view = view[view.office == office]
        if parties:
            view = view[view.party.isin(parties)]
        if states:
            view = view[view.state_full.isin(states)]
        if only_stance:
            view = view[view.stance.str.len() > 0]
        view = view.sort_values(["state_full", "office", "name"])

        q1, q2, q3 = st.columns(3)
        q1.metric("Officials shown", f"{len(view)}")
        q2.metric("Senators", f"{(view.office=='Senator').sum()}")
        q3.metric("With sourced stance", f"{(view.stance.str.len()>0).sum()}")

        show = view[["name", "office", "state_full", "party",
                     "stance", "website", "contact"]].copy()
        st.dataframe(
            show, use_container_width=True, hide_index=True, height=560,
            column_config={
                "name": "Name", "office": "Office", "state_full": "State",
                "party": "Party",
                "stance": st.column_config.TextColumn("Data-centre stance (sourced)",
                                                      width="large"),
                "website": st.column_config.LinkColumn("Website", display_text="site"),
                "contact": st.column_config.LinkColumn("Contact", display_text="contact"),
            })

        stanced = view[view.stance.str.len() > 0]
        if not stanced.empty:
            st.markdown("**Documented stances in this view:**")
            for _, r in stanced.iterrows():
                src = f" ({src_link(r['stance_src'])})" if r["stance_src"] else ""
                st.markdown(f"- **{r['name']}** ({r['party']}, {r['office']}, "
                            f"{r['state_full']}): {r['stance']}{src}")

        st.caption("Sources: official [US Senate contact list]"
                   "(https://www.senate.gov/general/contact_information/senators_cfm.xml)"
                   " · [current US governors]"
                   "(https://en.wikipedia.org/wiki/List_of_current_United_States_governors)"
                   ". Governor site URLs are official state-government pages. "
                   "Verify before any outreach — rosters change with elections "
                   "and appointments.")

# --------------------------------------------------------------------------- #
# TAB 8 — MACRO OUTLOOK
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

    st.divider()
    st.subheader("Forecasts disagree — a lot")
    st.caption("Third-party projections of **global** data-centre electricity (TWh) "
               "vary widely by forecaster, year, and scenario. Same metric, so "
               "they're comparable; the gap is the honest uncertainty.")
    fdf = DC_FORECASTS.copy()
    fdf["label"] = fdf["source"] + " · " + fdf["year"].astype(str)
    fc = (alt.Chart(fdf).mark_bar().encode(
        x=alt.X("twh:Q", title="Global data-centre electricity (TWh/yr)"),
        y=alt.Y("label:N", sort="-x", title=None),
        color=alt.Color("source:N", legend=alt.Legend(title="Forecaster")),
        tooltip=["source", "year", "twh"],
    ).properties(height=max(240, 30 * len(fdf))))
    st.altair_chart(fc, use_container_width=True)

    st.markdown("**US-only, 2030 (TWh)** — the spread across forecasters is the "
                "whole point: central estimates run ~2.8× from low to high.")
    udf = DC_FORECASTS_US.copy()
    uc = (alt.Chart(udf).mark_bar().encode(
        x=alt.X("twh:Q", title="US data-centre electricity, 2030 (TWh/yr)"),
        y=alt.Y("source:N", sort="x", title=None),
        color=alt.Color("twh:Q", scale=alt.Scale(scheme="yelloworangered"), legend=None),
        tooltip=["source", "twh", "note"],
    ).properties(height=max(200, 34 * len(udf))))
    st.altair_chart(uc, use_container_width=True)

    st.markdown(
        f"- **In capacity terms:** BloombergNEF sees US data-centre power hitting "
        f"**~106 GW by 2035** (from ~25 GW in 2024) — **8.6%** of all US "
        f"electricity, more than double today's 3.5%. {src_link('bnef_106')}.\n"
        f"- **Why the spread:** forecasts hinge on how much announced pipeline "
        f"actually gets built and powered (interconnection queues are heavily "
        f"speculative), plus efficiency gains and utilisation assumptions.")
    st.caption("Forecasters: " + " · ".join(src_link(k) for k in
               ["iea_2025", "bnef", "gartner", "sp_451", "epri_pi", "lbnl",
                "wri_range"]))

# --------------------------------------------------------------------------- #
# TAB 8 — METHODOLOGY
# --------------------------------------------------------------------------- #

with tab_method:
    st.subheader("Sources & coefficients")
    for key in ["google_2025", "openai_2025", "epoch_2025", "hungry_2025",
                "mlenergy", "iea_2025", "gpt5_report", "eia930", "pjm_dm2",
                "cbre_dc", "cbre_glob", "jll_dc", "cushman_dc", "google_dc",
                "meta_dc", "imasons", "bnef", "bnef_106", "gartner", "wri_range",
                "sp_451", "epri_pi", "lbnl", "ercot_ll", "pjm_lf", "eia_va",
                "eia_pilot",
                "google_news", "reddit", "icap_mor", "dcbans", "dcopp", "dcwatch",
                "dcresp", "dctrack", "gjf_mor",
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
