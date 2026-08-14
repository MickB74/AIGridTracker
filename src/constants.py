import datetime as _dt
import json
import pathlib
import pandas as pd


def has_value(v):
    """True if a DataFrame cell holds real content rather than a blank.

    Never write `if row["verified"]` against an object column. A missing value
    arrives as None on pandas 2.x but as NaN on 3.x, and **NaN is truthy** — so
    the naive test silently flips meaning across a pandas upgrade. That is not
    hypothetical: it made every "unverified" marker disappear from the site's
    search index when CI built on a newer pandas than the machine that
    generated the committed HTML.

    Defined up here rather than beside the registries because the registries
    themselves now use it at import time (MORATORIUMS_DF derives `verified`
    from it).
    """
    if v is None:
        return False
    if isinstance(v, str):
        return bool(v.strip()) and v.strip().lower() not in ("nan", "none")
    return bool(pd.notna(v))


# --------------------------------------------------------------------------- #
# STATIC DATA (sourced — see SOURCES and the Methodology tab)
# --------------------------------------------------------------------------- #

# Per-QUERY coefficients, median text prompt. energy Wh, co2 gCO2e, water mL.
QUERY_COEFFS = {
    # ── First-party disclosures ──────────────────────────────────────────────
    "Google Gemini 2.0 — full-stack (Google, May 2025)": {
        "energy_wh": 0.24, "co2_g": 0.03, "water_ml": 0.26, "src": "google_2025",
        "scope": "Full-stack",
        "note": "Accelerator + host CPU + idle share + cooling/PUE. Market-based carbon.",
    },
    "Google Gemini 2.0 — chip-only (Google, May 2025)": {
        "energy_wh": 0.10, "co2_g": 0.02, "water_ml": 0.12, "src": "google_2025",
        "scope": "Chip-only",
        "note": "Active TPU/GPU only. Understates real operating footprint.",
    },
    "OpenAI — avg ChatGPT query (Altman, Jan 2025)": {
        "energy_wh": 0.34, "co2_g": None, "water_ml": 0.39, "src": "openai_2025",
        "scope": "Full-stack",
        "note": "CEO blog figure; methodology not published.",
    },
    # ── Benchmark studies ────────────────────────────────────────────────────
    "GPT-4o (How Hungry is AI?, 2025)": {
        "energy_wh": 0.55, "co2_g": None, "water_ml": None, "src": "hungry_2025",
        "scope": "Benchmark",
        "note": "Derived midpoint (~0.51–0.60 Wh/query) from annual estimate.",
    },
    "Claude 3.5 Sonnet (How Hungry is AI?, 2025)": {
        "energy_wh": 0.40, "co2_g": None, "water_ml": None, "src": "hungry_2025",
        "scope": "Benchmark",
        "note": "Estimated from benchmark inference runs on Anthropic API.",
    },
    "Claude 3.5 Haiku — efficient (Epoch AI est., 2025)": {
        "energy_wh": 0.10, "co2_g": None, "water_ml": None, "src": "epoch_2025",
        "scope": "Benchmark",
        "note": "Distilled faster model; estimated from token-level coefficients for small parameter scale.",
    },
    "Claude 3 Opus — heavy workload (Epoch AI est., 2025)": {
        "energy_wh": 0.85, "co2_g": None, "water_ml": None, "src": "epoch_2025",
        "scope": "Benchmark",
        "note": "Large frontier model; estimated from token-level coefficients for high-parameter density.",
    },
    "Llama 3.1 405B — A100 cluster (Epoch AI, 2025)": {
        "energy_wh": 0.97, "co2_g": None, "water_ml": None, "src": "epoch_2025",
        "scope": "Benchmark",
        "note": "~1000 output tokens × Epoch AI high estimate. Large open model on older GPU.",
    },
    "Llama 3.1 70B — A100 (Epoch AI, 2025)": {
        "energy_wh": 0.35, "co2_g": None, "water_ml": None, "src": "epoch_2025",
        "scope": "Benchmark",
        "note": "~1000 output tokens × ~0.35 mWh/token. Mid-size open model.",
    },
    "Mistral Large 2 (Epoch AI est., 2025)": {
        "energy_wh": 0.30, "co2_g": None, "water_ml": None, "src": "epoch_2025",
        "scope": "Benchmark",
        "note": "Estimated from Epoch AI token-level coefficients for ~123B param model.",
    },
    "DeepSeek-V3 — H100 (community benchmark, 2025)": {
        "energy_wh": 0.28, "co2_g": None, "water_ml": None, "src": "community_bench",
        "scope": "Benchmark",
        "note": "Community-reported inference energy for MoE architecture on H100.",
    },
    "Gemma 3 27B — efficient small (Google, 2025)": {
        "energy_wh": 0.06, "co2_g": None, "water_ml": None, "src": "google_2025",
        "scope": "Chip-only",
        "note": "Small model on TPU; chip-only. Very efficient per-query.",
    },
    "GPT-4o mini (Epoch AI est., 2025)": {
        "energy_wh": 0.12, "co2_g": None, "water_ml": None, "src": "epoch_2025",
        "scope": "Benchmark",
        "note": "Distilled small model; ~1000 tokens at low per-token energy.",
    },
    # ── Reasoning / heavy workloads ──────────────────────────────────────────
    "OpenAI o1 — reasoning query (Epoch AI est., 2025)": {
        "energy_wh": 3.50, "co2_g": None, "water_ml": None, "src": "epoch_2025",
        "scope": "Benchmark",
        "note": "Chain-of-thought reasoning generates 5–10× more tokens per query.",
    },
    "Google Gemini 2.5 Pro — deep think (est., 2026)": {
        "energy_wh": 4.20, "co2_g": None, "water_ml": None, "src": "estimate",
        "scope": "Benchmark",
        "note": "Extended thinking mode; ~20k output tokens. Rough community estimate.",
    },
    # ── Contested outlier ────────────────────────────────────────────────────
    "GPT-5 report — avg (2025, contested)": {
        "energy_wh": 18.0, "co2_g": None, "water_ml": None, "src": "gpt5_report",
        "scope": "Contested",
        "note": "Third-party report; up to ~40 Wh on some responses. Disputed methodology.",
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

# ── Water coefficients (Footprint calculator; blog: hidden-water-cost) ──────
# On-site cooling WUE (L per kWh of IT load), fleet-average disclosures.
# Note L/kWh == mL/Wh, so these multiply Wh energy directly into mL water.
ONSITE_WUE = {
    "Google fleet average (2024)":    {"l_per_kwh": 1.10, "src": "google_env_2026"},
    "Microsoft fleet average (2024)": {"l_per_kwh": 1.80, "src": "msft_env_2025"},
    "Meta fleet average (2024)":      {"l_per_kwh": 0.19, "src": "meta_env_2025"},
    "AWS fleet average (2025)":       {"l_per_kwh": 0.12, "src": "amzn_env_2025"},
}

# Off-site (indirect) water consumed by electricity generation, L per kWh.
# Consumption (evaporated), not withdrawal — withdrawal figures run far higher.
OFFSITE_WATER = {
    "US grid average":      {"l_per_kwh": 1.20, "src": "thirsty_2024"},
    "Coal-heavy grid":      {"l_per_kwh": 1.70, "src": "usgs_water"},   # USGS: 1.5–2.0
    "Gas-heavy grid":       {"l_per_kwh": 0.90, "src": "usgs_water"},
    "Nuclear-heavy grid":   {"l_per_kwh": 2.00, "src": "usgs_water"},
    "High-renewables grid": {"l_per_kwh": 0.10, "src": "thirsty_2024"},  # wind/solar PV
}

# On-site evaporative-cooling water intensity varies by climate — hot/arid
# sites lose more water per kWh of heat rejected than cool/humid ones. Lei &
# Masanet (2022) modeled evaporative-tower WUE across 15 US climate zones and
# found a range of 1.99-4.00 L/kWh, roughly a 2x spread between the coolest
# and hottest/driest zones (src: lei_masanet_2022). We don't have a full
# 51-state climate-zone mapping, so this applies that ~2x spread as a
# conservative three-tier multiplier keyed to each state's existing
# `water_stress` rating (STATE_GRID_PROFILES, src: wri_aqueduct) rather than
# claiming zone-level precision. Applied to the on-site water estimate only —
# it approximates a climate effect, not a literature value.
WATER_STRESS_CLIMATE_MULTIPLIER = {"low": 0.85, "medium": 1.0, "high": 1.4}

# IEA data-center electricity outlook (TWh), demand-side.
IEA_OUTLOOK = pd.DataFrame({"year": [2024, 2025, 2030, 2035],
                            "twh":  [415,  485,  945,  1200]})

# Third-party GLOBAL data-center electricity forecasts (TWh) — same metric so
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

# US-only data-center electricity forecasts for 2030 (TWh). The spread is the
# story: central estimates run ~350 → ~970 TWh. Scenario/range midpoints noted.
DC_FORECASTS_US = pd.DataFrame([
    {"source": "Goldman Sachs / McKinsey", "twh": 350, "note": "~300–400 range", "src": "wri_range"},
    {"source": "IEA",                      "twh": 425, "note": "~8% of US power", "src": "iea_2025"},
    {"source": "LBNL (Berkeley Lab)",      "twh": 450, "note": "range 325–580",  "src": "lbnl"},
    {"source": "EPRI (medium)",            "twh": 590, "note": "13% of US power", "src": "epri_pi"},
    {"source": "EPRI (high)",              "twh": 790, "note": "17% of US power", "src": "epri_pi"},
    {"source": "BCG",                      "twh": 970, "note": "high end",        "src": "wri_range"},
])

# Pew Research Center, April 2026 — where new US data centers are being sited.
# The headline finding for community advocacy: the build-out has moved to rural
# counties, most of which have never hosted a facility and have no zoning
# precedent for one. See SOURCES["pew_rural_2026"].
PEW_RURAL_2026 = {
    "planned_rural_pct": 67,
    "operating_rural_pct": 13,
    "planned_urban_pct": 33,
    "operating_urban_pct": 87,
    "new_counties_pct": 39,
    "americans_within_5mi_now_pct": 38,
    "americans_within_5mi_planned_pct": 42,
    "clustered_within_5mi_pct": 90,
    "south_share_pct": 48,
    "south_growth_pct": 62,
    "midwest_growth_pct": 64,
    "as_of": "April 2026",
}

# Top states by operating vs planned facilities (Pew 2026, counts via
# DataCenterMap). Facility counts, not megawatts — see REGISTRY_PROVENANCE.
PEW_STATE_COUNTS = pd.DataFrame([
    {"state": "Virginia",       "operating": 398, "planned": 287},
    {"state": "Texas",          "operating": 296, "planned": 170},
    {"state": "Georgia",        "operating":  94, "planned": 141},
    {"state": "Illinois",       "operating": 139, "planned": 123},
    {"state": "Arizona",        "operating":  98, "planned":  86},
    {"state": "Indiana",        "operating":  38, "planned":  54},
    {"state": "Ohio",           "operating": 166, "planned":  57},
    {"state": "Pennsylvania",   "operating":  78, "planned":  51},
    {"state": "North Carolina", "operating":  72, "planned":  41},
    {"state": "Iowa",           "operating":  64, "planned":  41},
])
PEW_STATE_COUNTS["total"] = (PEW_STATE_COUNTS["operating"]
                             + PEW_STATE_COUNTS["planned"])

# Major data-center markets — OPERATIONAL commissioned power (MW), ~2025.
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
# disclosed). Google: datacenters.google/locations (active US, precise campuses).
# Meta: datacenters.atmeta.com/us-locations (precise campuses). Microsoft:
# local.microsoft.com/communities (metro/"community" level, not per-campus).
# Amazon/AWS: aboutamazon.com investment announcements + long-established AWS US
# regions (metro/county level; Amazon does not publish a per-campus location map).
# Coords approximate (town/county/metro centroid).
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
    # Microsoft — first-party "community" list (local.microsoft.com/communities);
    # metro/region level, plotted at the named campus/metro centroid.
    ("Microsoft", "Goodyear (Greater Phoenix)", "AZ", 33.44, -112.36, "microsoft_dc"),
    ("Microsoft", "Santa Clara / San Jose", "CA", 37.35, -121.95, "microsoft_dc"),
    ("Microsoft", "Greater Atlanta", "GA", 33.75, -84.39, "microsoft_dc"),
    ("Microsoft", "Chicago", "IL", 41.85, -87.65, "microsoft_dc"),
    ("Microsoft", "Northern Indiana (LaPorte)", "IN", 41.61, -86.72, "microsoft_dc"),
    ("Microsoft", "West Des Moines", "IA", 41.58, -93.71, "microsoft_dc"),
    ("Microsoft", "Southeast Michigan", "MI", 42.17, -83.78, "microsoft_dc"),
    ("Microsoft", "Las Vegas", "NV", 36.17, -115.14, "microsoft_dc"),
    ("Microsoft", "Maiden (Catawba Co.)", "NC", 35.58, -81.21, "microsoft_dc"),
    ("Microsoft", "Northern Virginia", "VA", 39.02, -77.48, "microsoft_dc"),
    ("Microsoft", "Central Ohio (Heath)", "OH", 40.02, -82.44, "microsoft_dc"),
    ("Microsoft", "Boydton (Southern Virginia)", "VA", 36.67, -78.39, "microsoft_dc"),
    ("Microsoft", "Greater San Antonio", "TX", 29.42, -98.49, "microsoft_dc"),
    ("Microsoft", "Quincy (Central Washington)", "WA", 47.23, -119.85, "microsoft_dc"),
    ("Microsoft", "Mount Pleasant (Racine Co.)", "WI", 42.72, -87.85, "microsoft_dc"),
    ("Microsoft", "Cheyenne", "WY", 41.14, -104.82, "microsoft_dc"),
    # Amazon / AWS — established US regions + first-party investment announcements
    # (aboutamazon.com); metro/county level, no per-campus map published.
    ("Amazon (AWS)", "Northern Virginia (Loudoun Co.)", "VA", 39.08, -77.65, "aws_dc"),
    ("Amazon (AWS)", "Central Ohio (New Albany)", "OH", 40.08, -82.81, "aws_dc"),
    ("Amazon (AWS)", "Umatilla / Boardman", "OR", 45.84, -119.70, "aws_dc"),
    ("Amazon (AWS)", "New Carlisle (Northern Indiana)", "IN", 41.70, -86.51, "aws_dc"),
    ("Amazon (AWS)", "Madison County", "MS", 32.63, -90.03, "aws_dc"),
    ("Amazon (AWS)", "Warren County (Vicksburg)", "MS", 32.35, -90.88, "aws_dc"),
    ("Amazon (AWS)", "Richmond County (Rockingham)", "NC", 34.97, -79.76, "aws_dc"),
    ("Amazon (AWS)", "Luzerne County (Salem Twp.)", "PA", 41.15, -76.04, "aws_dc"),
    ("Amazon (AWS)", "Falls Township (Bucks Co.)", "PA", 40.17, -74.76, "aws_dc"),
    ("Amazon (AWS)", "Caddo / Bossier Parish", "LA", 32.52, -93.75, "aws_dc"),
]
HYPERSCALERS_DF = pd.DataFrame(
    HYPERSCALERS, columns=["company", "location", "state", "lat", "lon", "src"])

# AI-competitor compute megasites — the frontier-model builders / AI-cloud players
# these hyperscalers name as competition in their SEC 10-K filings (see
# AI_COMPETITORS). Locations are publicly documented via operator announcements
# and press (NOT first-party campus lists like the hyperscalers above), so treat
# them as approximate site/metro centroids, not surveyed coordinates.
AI_COMPETITOR_SITES = [
    # company, location, state, lat, lon, src
    ("xAI (Colossus)", "Memphis (Boxtown / President's Island)", "TN", 35.08, -90.11, "xai_memphis"),
    ("xAI (Colossus)", "Memphis (Whitehaven)", "TN", 35.04, -90.02, "xai_memphis"),
    ("OpenAI · Oracle (Stargate)", "Abilene (Lancium Clean Campus)", "TX", 32.45, -99.73, "stargate"),
    ("OpenAI · Oracle (Stargate)", "Shackelford County", "TX", 32.74, -99.33, "stargate"),
    ("OpenAI · Oracle (Stargate)", "Doña Ana County", "NM", 32.35, -106.87, "stargate"),
    ("OpenAI · Oracle (Stargate)", "Milam County (Rockdale)", "TX", 30.65, -96.97, "stargate"),
    ("OpenAI · Oracle (Stargate)", "Lordstown", "OH", 41.17, -80.85, "stargate"),
    # CoreWeave — AI-cloud "neocloud"; mostly leased / partner-hosted (Core
    # Scientific), so these are documented site metros, not a first-party campus map.
    ("CoreWeave", "Kenilworth (NEST11)", "NJ", 40.68, -74.29, "crwv_dc"),
    ("CoreWeave", "Las Vegas (Core Campus / LAS1)", "NV", 36.10, -115.15, "crwv_dc"),
    ("CoreWeave", "Lancaster", "PA", 40.04, -76.30, "crwv_dc"),
    ("CoreWeave", "Denton (Core Scientific host)", "TX", 33.21, -97.13, "crwv_dc"),
    ("CoreWeave", "Port of Muskogee (Core Scientific host)", "OK", 35.74, -95.37, "crwv_dc"),
]
AI_COMPETITOR_SITES_DF = pd.DataFrame(
    AI_COMPETITOR_SITES, columns=["company", "location", "state", "lat", "lon", "src"])

HYPERSCALER_COLORS = {"Google": "#34a853", "Meta": "#0866ff",
                      "Microsoft": "#f25022", "Amazon (AWS)": "#ff9900",
                      "xAI (Colossus)": "#a855f7",
                      "OpenAI · Oracle (Stargate)": "#14b8a6",
                      "CoreWeave": "#ec4899"}

# --------------------------------------------------------------------------- #
# ROLE-AWARE ATTRIBUTION
# A data-center campus involves up to three distinct parties. Collapsing them
# into one "company" column hides who owns the land, who runs the building, and
# who actually consumes the power. We separate:
#   • owner    — parent / private-equity owner of the operator ("self" = public
#                & independent, no PE parent)
#   • operator — the brand that builds & runs the facility
#   • tenant   — the power consumer (frequently undisclosed for colo/REIT space)
# plus filing_llc (the single-purpose LLC on the deed/permit — the join key back
# to county assessor + Secretary-of-State records) and attribution (how the
# operator/tenant was resolved → drives map-marker confidence).
#
# NOTE: the colocation/REIT ownership facts below were compiled from trade press
# and operator releases; the automated fact-check pass could not run (API spend
# limit), so treat every non-first-party row as press-sourced, not independently
# verified.
ATTRIBUTION_LEVELS = {  # most → least authoritative
    "first_party":  "Operator's own location / community page",
    "deed":         "County deed / assessor record naming the filing LLC",
    "leasing_news": "Operator or tenant leasing announcement",
    "press":        "Trade press / reporting (not first-party)",
    "inferred":     "Inferred from interconnection, PPA, or circumstantial signals",
}

# Operator-level reference: owner/PE parent, build model, tenant disclosure, and
# the property-LLC naming pattern used on deeds & permits. owner="self" means
# public & independent (no PE parent).
#   name: (tier, owner, owner_note, model, discloses_tenant, filing_llc, color, src)
OPERATORS = {
    "Google":        ("hyperscaler", "self", "Public (Alphabet, NASDAQ: GOOGL)", "Own", False,
                      "Land-acquisition shells: Jet Stream LLC, Sharka LLC", "#34a853", "google_dc"),
    "Meta":          ("hyperscaler", "self", "Public (NASDAQ: META)", "Own", False,
                      "Codename shells: Greater Kudu, Raven Northbrook, Stadion, Wobniar, Pinnacle Mountain", "#0866ff", "meta_dc"),
    "Microsoft":     ("hyperscaler", "self", "Public (NASDAQ: MSFT)", "Mixed", False,
                      "Project-name / generic 'Holdings LLC'; less consistently codenamed", "#f25022", "microsoft_dc"),
    "Amazon (AWS)":  ("hyperscaler", "self", "Public (NASDAQ: AMZN)", "Own", False,
                      "Vadata, Inc. — AWS's build/operating entity on many permits", "#ff9900", "aws_dc"),
    "xAI (Colossus)": ("ai", "self", "Private (xAI)", "Mixed", True,
                      "Site/retrofit LLCs (e.g. former Electrolux plant, Memphis)", "#a855f7", "xai_memphis"),
    "OpenAI · Oracle (Stargate)": ("ai", "self", "JV: OpenAI · Oracle · SoftBank; sites developed by Oracle/Crusoe/Vantage", "Mixed", True,
                      "Per-site developer LLCs (Crusoe/Lancium at Abilene, etc.)", "#14b8a6", "stargate"),
    "CoreWeave":     ("ai", "self", "Public (NASDAQ: CRWV, IPO Mar 2025)", "Lease", False,
                      "Mostly TENANT in partners' buildings: Core Scientific, Chirisa/Bulk, Flexential, Lincoln, TierPoint, Digital Realty, DataBank, Switch, Galaxy, Applied Digital", "#ec4899", "crwv_dc"),
    # ---- Colocation / wholesale REITs & operators (press-sourced) ----
    "Digital Realty": ("colo", "self", "Public REIT (NYSE: DLR)", "Mixed", False,
                      "'Digital [City]/[Address] LLC'; legacy Telx entities; Ascenty (LatAm)", "#6366f1", "dc_ownership"),
    "QTS":           ("colo", "Blackstone", "Blackstone take-private ~$10B, closed 2021", "Own", False,
                      "'QTS ... LLC' + Blackstone holding entities; early generic project LLCs", "#8b5cf6", "dc_ownership"),
    "Vantage":       ("colo", "DigitalBridge + Silver Lake", "$9.2B equity round closed Jun 2024", "Own", False,
                      "Per-campus 'Vantage ... LLC' site entities", "#0ea5e9", "vantage_dbsl"),
    "CyrusOne":      ("colo", "KKR + Global Infrastructure Partners", "~$15B take-private, closed 2022", "Own", False,
                      "'CyrusOne LLC' subsidiaries", "#22d3ee", "dc_ownership"),
    "Aligned":       ("colo", "Nvidia · Microsoft · BlackRock/MGX (pending)", "~$40B acquisition announced Oct 2025, close H1 2026 (press)", "Own", False,
                      "Per-site LLCs", "#f59e0b", "dc_ownership"),
    "Switch":        ("colo", "DigitalBridge + IFM Investors", "~$11B EV take-private, closed 2022", "Own", False,
                      "'Switch ... LLC'; campuses branded 'Primes'", "#ef4444", "switch_dbif"),
    "Stack Infrastructure": ("colo", "Blue Owl / IPI Partners", "Blue Owl acquired IPI Partners, 2025", "Own", False,
                      "Per-site LLCs", "#10b981", "dc_ownership"),
    "EdgeConneX":    ("colo", "EQT Infrastructure + ADIA", "EQT-backed", "Own", False,
                      "Per-site LLCs", "#a3a3a3", "dc_ownership"),
    "Equinix":       ("colo", "self", "Public REIT (NASDAQ: EQIX)", "Mixed", False,
                      "IBX-branded site entities", "#dc2626", "dc_ownership"),
    "Core Scientific": ("colo", "self", "Public (NASDAQ: CORZ); CoreWeave acquisition proposed Jul 2025 — outcome uncertain, verify", "Own", True,
                      "Site LLCs; ~10 US facilities (~840 MW HPC + ~500 MW crypto; ~1.3 GW gross)", "#64748b", "crwv_coresci"),
}

# Per-company role resolution for the AI-competitor sites (tenant, attribution).
# CoreWeave is a tenant in partners' buildings, so its "tenant" is undisclosed.
_AI_ROLE = {
    "xAI (Colossus)":             ("xAI (Colossus)", "first_party"),
    "OpenAI · Oracle (Stargate)": ("OpenAI",         "first_party"),
    "CoreWeave":                  (None,             "leasing_news"),
}

def _role_rows():
    """Backfill the flat (company, …) site lists into the role-aware schema."""
    rows = []
    for company, loc, st_, lat, lon, src in HYPERSCALERS:      # own & consume
        llc = OPERATORS[company][5] if company in OPERATORS else None
        rows.append((company, "self", company, loc, st_, lat, lon,
                     llc, "first_party", src))
    for company, loc, st_, lat, lon, src in AI_COMPETITOR_SITES:
        tenant, attribution = _AI_ROLE.get(company, (company, "press"))
        owner = OPERATORS[company][1] if company in OPERATORS else "self"
        llc = OPERATORS[company][5] if company in OPERATORS else None
        rows.append((company, owner, tenant, loc, st_, lat, lon,
                     llc, attribution, src))
    return rows

# Role-aware master site table. The legacy HYPERSCALERS_DF / AI_COMPETITOR_SITES_DF
# above remain the compat view consumed by the existing campus map.
DC_SITES_DF = pd.DataFrame(_role_rows(), columns=[
    "operator", "owner", "tenant", "location", "state",
    "lat", "lon", "filing_llc", "attribution", "src"])

# --------------------------------------------------------------------------- #
# FILING ENTITIES — the shell-LLC → parent mapping
# --------------------------------------------------------------------------- #
# The one question this project answers that nobody else does: a resident has
# a name off a deed or a rezoning notice and no idea who is actually behind it.
#
# DC_SITES_DF.filing_llc cannot answer it. That column holds an operator-level
# *pattern* ("Land-acquisition shells: Jet Stream LLC, Sharka LLC") repeated
# across every row for that operator — useful colour, useless as a lookup,
# because the entity on a resident's notice is usually a name that appears
# nowhere in it.
#
# This is the lookup table instead: one row per named entity, each tied to the
# reporting or filing that established the link, with the date it was read.
# Entities are added only where the link is documented — a plausible guess
# here would send someone to a public hearing to accuse the wrong company,
# which is worse than saying "we don't know, here's how to find out."
#
# `role` distinguishes what the entity actually is, because it changes who a
# resident should be addressing:
#   land       — buys the parcels quietly, pre-announcement
#   project    — the named development entity on permits and rezonings
#   developer  — a third party building for a tenant, not the end user
FILING_ENTITIES = [
    {"entity": "Sharka LLC", "parent": "Google", "role": "land",
     "locality": "Midlothian (Ellis Co.)", "state": "TX",
     "note": "Acquired 375 acres in Railport Business Park, May 2017; a "
             "$500M campus and a 10-year county tax abatement followed. "
             "Registered through Corporation Service Company in Delaware.",
     "as_of": "2026-08-05",
     "source": "https://www.datacenterdynamics.com/en/news/google-is-behind-500m-sharka-data-center-in-midlothian-texas/"},
    {"entity": "Jet Stream LLC", "parent": "Google", "role": "land",
     "locality": "Multiple", "state": "",
     "note": "Google's land-acquisition shell before Sharka; same Delaware "
             "registered agent.",
     "as_of": "2026-08-05",
     "source": "https://www.datacenterdynamics.com/en/news/google-is-behind-500m-sharka-data-center-in-midlothian-texas/"},
    {"entity": "Willowbend Capital LLC", "parent": "Google", "role": "land",
     "locality": "Little Rock (Pulaski Co.)", "state": "AR",
     "note": "Bought ~380 acres at the Port of Little Rock for ~$23M per "
             "Pulaski County property records. Managed by Michael Montfort, "
             "the same name on Google's Indiana and West Memphis shells.",
     "as_of": "2026-08-05",
     "source": "https://www.arkansasonline.com/news/2026/jan/14/tech-giant-google-behind-1-billion-little-rock/"},
    {"entity": "Forgelight Ventures LLC", "parent": "Google", "role": "land",
     "locality": "Conway (Faulkner Co.)", "state": "AR",
     "note": "Delaware front company organised by the same manager as "
             "Willowbend Capital.",
     "as_of": "2026-08-05",
     "source": "https://www.arkansasonline.com/news/2026/jan/14/tech-giant-google-behind-1-billion-little-rock/"},
    {"entity": "Groot LLC", "parent": "Google", "role": "land",
     "locality": "West Memphis (Crittenden Co.)", "state": "AR",
     "note": "Front company on the West Memphis project, later confirmed as "
             "Google.",
     "as_of": "2026-08-05",
     "source": "https://www.arkansasonline.com/news/2025/sep/05/google-behind-10b-data-center-in-west-memphis/"},
    {"entity": "Greater Kudu LLC", "parent": "Meta", "role": "project",
     "locality": "Los Lunas (Valencia Co.)", "state": "NM",
     "note": "The named counterparty on the village's March 2025 water and "
             "wastewater service agreement — the entity a resident would find "
             "on the municipal contract, not 'Meta'.",
     "as_of": "2026-08-05",
     "source": "https://www.news-bulletin.com/news/tax-break-water-deal-for-meta-data-center/article_d4ff8540-163d-4c73-8a17-a5ec65209c42.html"},
    {"entity": "RCM Hill LLC", "parent": "Not publicly attributed", "role": "developer",
     "locality": "Hill County", "state": "TX",
     "note": "Sued Hill County over its moratorium for >$100M, holding "
             "contracts on 800+ acres worth $80M+. The county rescinded; the "
             "suit was dropped. No parent has been publicly identified.",
     "as_of": "2026-08-05",
     "source": "https://www.texastribune.org/2026/06/05/texas-hill-county-moratorium-rescinded-data-centers/"},
    {"entity": "GW Acquisition Co", "parent": "QTS Data Centers", "role": "project",
     "locality": "Prince William County", "state": "VA",
     "note": "QTS affiliate that carried the Digital Gateway appeals, and "
             "whose withdrawal ended the project.",
     "as_of": "2026-08-05",
     "source": "https://virginiabusiness.com/prince-william-digital-gateway-data-center-project-officially-dies/"},
    {"entity": "Nscale", "parent": "Nscale", "role": "developer",
     "locality": "Mason County", "state": "WV",
     "note": "Developer of the Monarch Compute Campus north of Point "
             "Pleasant, and the party running the voluntary 'Good Neighbors' "
             "buyout of 53 adjacent homes.",
     "as_of": "2026-08-05",
     "source": "https://wchstv.com/news/local/voluntary-buyout-offers-rolled-out-for-meadowlands-estates-homes-near-data-center"},
    {"entity": "Diode Ventures", "parent": "Black & Veatch", "role": "developer",
     "locality": "Peculiar (Cass Co.)", "state": "MO",
     "note": "Proposed the $1.5B Harper Road Technology Park; blocked when "
             "the Board of Aldermen removed 'data center' from the zoning "
             "code.",
     "as_of": "2026-08-05",
     "source": "https://www.kshb.com/news/local-news/peculiar-reverses-zoning-for-data-center-after-cries-from-neighbors"},
]
FILING_ENTITIES_DF = pd.DataFrame(FILING_ENTITIES)

# Names that keep turning up as the registered agent or alias behind these
# entities. Not a lookup — a hint for someone reading a filing themselves,
# because recognising the agent is often what tells you a shell is a
# hyperscaler rather than a local developer.
ENTITY_TELLS = [
    ("Corporation Service Company (CSC)",
     "Delaware registered agent used by both Google and Meta shells. Seeing "
     "CSC on a small-town filing is a strong hint the buyer is much larger "
     "than the entity name suggests."),
    ("Repeated manager names",
     "The same individual often manages shells across states — Michael "
     "Montfort appears on Google's Arkansas and Indiana entities. Search the "
     "manager's name in other states' business registries."),
    ("Meta aliases",
     "Meta has negotiated as Raven Northbrook, Greater Kudu and Stadion."),
]


def lookup_filing_entity(query):
    """Rows whose entity name matches `query` (case-insensitive substring).

    Substring rather than exact because a resident types what is printed on a
    notice — "Greater Kudu", "GREATER KUDU LLC", "Kudu" — and an exact match
    would fail all three.
    """
    q = str(query or "").strip().lower()
    if len(q) < 3:
        return FILING_ENTITIES_DF.iloc[0:0]
    return FILING_ENTITIES_DF[
        FILING_ENTITIES_DF["entity"].str.lower().str.contains(q, regex=False)]


def _tenant_disclosure(tier, discloses):
    if tier == "hyperscaler":
        return "Self-consumed"
    return "Sometimes" if discloses else "Rarely"

# Operator-level table for rendering (the colo/REIT + owner reference).
OPERATORS_DF = pd.DataFrame(
    [(name, m[0], m[2], m[3], _tenant_disclosure(m[0], m[4]), m[5])
     for name, m in OPERATORS.items()],
    columns=["operator", "tier", "owner", "model", "discloses_tenant", "filing_llc"])

# Who each company calls a competitor "in AI and AI data centers", straight from
# the SEC 10-K "Competition" section (Item 1) of the filers the tracker follows,
# plus the newly-public AI-cloud filer CoreWeave. Note: only Oracle NAMES specific
# rivals in its filing; the big-tech filings describe competitor *categories*
# (always including AI / frontier models) but name no companies. `named` is what
# the filing literally lists; `rivals` is an editorial cross-reference mapping
# those categories to today's AI / data-center market participants.
AI_COMPETITORS = [
    {"filer": "Alphabet (Google)", "src": "goog_10k", "names": False,
     "quote": "“developers and providers of AI products and services”; also "
              "“providers of enterprise cloud services” and consumer-hardware makers.",
     "named": "—",
     "rivals": "OpenAI, Anthropic, Microsoft, Amazon (AWS), Meta, xAI"},
    {"filer": "Meta", "src": "meta_10k", "names": False,
     "quote": "“companies in the development and application of AI, particularly "
              "with respect to the development of frontier AI models.”",
     "named": "—",
     "rivals": "OpenAI, Google (Alphabet), Anthropic, xAI, Microsoft"},
    {"filer": "Microsoft", "src": "msft_10k", "names": False,
     "quote": "“AI-first application companies”; Azure’s “AI offerings compete with "
              "AI products from hyperscalers … and … open source offerings.”",
     "named": "—",
     "rivals": "Google, Amazon (AWS), OpenAI, Anthropic, Meta, Oracle, Salesforce"},
    {"filer": "Amazon (AWS)", "src": "amzn_10k", "names": False,
     "quote": "competition intensified by “practical applications of artificial "
              "intelligence and machine learning” in “web and infrastructure "
              "computing services.”",
     "named": "—",
     "rivals": "Microsoft (Azure), Google Cloud, Oracle (OCI), CoreWeave, NVIDIA, OpenAI, Anthropic"},
    {"filer": "Oracle", "src": "orcl_10k", "names": True,
     "quote": "cloud/software/hardware offerings “compete directly with … Alphabet "
              "Inc., Amazon.com, Inc., … IBM … Microsoft Corporation, Salesforce, "
              "Inc. and SAP SE …”",
     "named": "Adobe, Alphabet, Amazon.com, Cisco, Intel, IBM, Microsoft, Salesforce, SAP, HPE, Workday",
     "rivals": "Amazon (AWS), Microsoft (Azure), Alphabet (Google Cloud), IBM, CoreWeave"},
    {"filer": "CoreWeave", "src": "crwv_10k", "names": False,
     "quote": "“We primarily compete with hyperscalers … several of which are also "
              "customers … We also compete with smaller cloud service providers.”",
     "named": "—",
     "rivals": "Amazon (AWS), Microsoft (Azure), Google Cloud, Oracle (OCI), Lambda, Nebius"},
]
AI_COMPETITORS_DF = pd.DataFrame(AI_COMPETITORS)

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

# ERCOT large-load interconnection — the clearest public "data centers in the
# queue" signal in the US. ERCOT is the ONLY ISO that publishes an aggregate
# large-LOAD (not generation) interconnection picture and breaks out the
# data-center share; per-project names are confidential. Figures are curated
# from ERCOT's own public reports (see SOURCES: ercot_ll_bc / ercot_ll_tac).
# The story is the funnel: what's *requested* dwarfs what's *approved*, which
# dwarfs what's actually *running*. MW; vintage = data-as-of date in the report.
ERCOT_LL_VINTAGE = "March 26, 2026"      # "as of" date on the ERCOT large-load slides
ERCOT_LL_DC_SHARE = 0.87                 # ~87% of requested large load is data centers
# stage, MW, what it means, source-key
ERCOT_LL_FUNNEL = [
    ("Seeking interconnection", 410_000,
     "Total large-load capacity requesting to connect. ~87% is data centers. "
     "Mostly speculative — many projects never energize.", "ercot_ll_bc"),
    ("Approved to energize", 9_042,
     "Received Approval to Energize from ERCOT Operations — cleared to turn on.",
     "ercot_ll_tac"),
    ("Actually operational", 3_801,
     "Simultaneous monthly peak ERCOT has actually had to serve — real load on "
     "the grid right now (non-simultaneous observed peak: 3,883 MW).",
     "ercot_ll_tac"),
]

# Breaking policy alerts — curated major developments to surface prominently.
# Each entry: (headline, detail, date, severity, url, expires)
# severity: "critical" (red), "major" (amber), "info" (blue)
# expires: ISO date string after which the alert auto-hides (None = manual removal)
POLICY_ALERTS = [
    (
        "New York enacts first statewide data center moratorium",
        "Governor Hochul signed EO 62 on July 14 — a 1-year ban on new 50+ MW facility permits "
        "while the state develops environmental and community benefit standards.",
        "2026-07-14",
        "critical",
        "https://www.governor.ny.gov/executive-order/no-62-establishing-temporary-moratorium-data-centers-new-york-while-state-develops",
        "2026-08-14",
    ),
]

# Curated video topics for the landing-page "Videos" section. Each entry is
# (emoji, label, youtube_search_query); rendered as a live YouTube-search link
# so results stay fresh without hardcoding specific (rot-prone) video URLs.
# Grouped to mirror the flashpoints / value-levers framing used elsewhere.
VIDEO_TOPICS = {
    "Community flashpoints": [
        ("💵", "Electricity bills & grid strain",
         "data center electricity bills ratepayers grid strain"),
        ("💧", "Water use & cooling",
         "data center water use cooling drought"),
        ("🏘️", "Zoning, land use & moratoria",
         "data center zoning moratorium residents oppose rezoning"),
        ("🔊", "Noise from chillers & generators",
         "data center noise complaints residents hum"),
        ("🧾", "Tax breaks vs. local benefit",
         "data center tax breaks incentives few jobs"),
        ("🛢️", "Backup diesel & air permits",
         "data center backup diesel generators air quality permit"),
    ],
    "How communities capture value": [
        ("👷", "Jobs & local workforce",
         "data center local jobs workforce economic impact"),
        ("🧾", "Tax base & fiscal revenue",
         "data center property tax revenue county schools"),
        ("⚡", "Grid stability contributions",
         "data center grid stability transmission upgrade flexible load"),
        ("☀️", "Shared clean power",
         "data center community solar green tariff clean microgrid"),
        ("🛡️", "Ratepayer protection",
         "data center cost allocation ratepayer protection tariff"),
        ("🤝", "Community-benefit agreements",
         "data center community benefit agreement local investment"),
    ],
}

# Data-center moratoriums / bans. Every row carries its own `source` (the
# ordinance, the enacting body's own page, or a datable news report of the
# vote) and `as_of` (the date that source was read) — the LOCAL_OFFICIALS_DF
# pattern, not a bulk snapshot. Rows with source=None have NOT been verified
# against a primary source; they render as unverified and scripts/
# verify_moratoriums.py queues them for review. Never invent an `as_of`.
#
# `expires` is the date a time-limited moratorium lapses, ISO YYYY-MM-DD, or
# None when the action is permanent, condition-based, or the term is not
# documented. A row is NOT marked expired just because its term "sounds"
# finished — moratorium_status() derives that from `expires` alone, so an
# undated term stays Enacted and shows up in the validator's worklist instead
# of being silently downgraded.
#
# level: Local/State. status: Enacted/Proposed/Rejected/Vetoed/Rescinded.
# "Expired" is never stored — it is derived. See moratorium_status().
MORATORIUMS = [
    {"locality": "Minneapolis", "state": "MN", "level": "Local",
     "status": "Enacted", "when": "May 22, 2026",
     "note": "6-month interim ordinance; facilities over 350,000 sq ft, downtown exempt",
     "lat": 44.98, "lon": -93.27, "expires": "2026-11-21", "as_of": "2026-08-04",
     "source": "https://www.mprnews.org/story/2026/05/22/minneapolis-city-council-imposes-six-month-halt-on-data-centers"},
    {"locality": "Denver", "state": "CO", "level": "Local",
     "status": "Enacted", "when": "May 21, 2026",
     "note": "1 year or until updated data center regulations are adopted",
     "lat": 39.74, "lon": -104.99, "expires": "2027-05-21", "as_of": "2026-08-04",
     "source": "https://www.rmpbs.org/news/government/denver-data-centers"},
    {"locality": "Baltimore City", "state": "MD", "level": "Local",
     "status": "Enacted", "when": "Jun 16, 2026",
     "note": "CB 26-0158: 1 year, facilities drawing 10 MW or more; 9-month impact study",
     "lat": 39.29, "lon": -76.61, "expires": "2027-06-16", "as_of": "2026-08-04",
     "source": "https://technical.ly/civics/baltimore-pauses-data-centers-to-study-grid-impacts/"},
    {"locality": "Reno", "state": "NV", "level": "Local",
     "status": "Enacted", "when": "Extended Jun 1, 2026",
     "note": "Extended 6-1 through Aug 2027 while permanent rules are drafted",
     "lat": 39.53, "lon": -119.81, "expires": "2027-08-31", "as_of": "2026-08-04",
     "source": "https://thisisreno.com/2026/06/reno-city-council-data-center-moratorium-3/"},
    {"locality": "Dubuque County", "state": "IA", "level": "Local",
     "status": "Enacted", "when": "May 26, 2026",
     "note": "12-month pause on permits and zoning requests for data center "
             "construction or expansion, amended up from 120 days; county will "
             "host weekly work sessions and at least four public town halls",
     "lat": 42.47, "lon": -90.88, "expires": "2027-05-26", "as_of": "2026-08-13",
     "source": "https://www.kcrg.com/2026/05/26/dubuque-county-passes-12-month-moratorium-data-centers/"},
    {"locality": "Bloomington", "state": "IL", "level": "Local",
     "status": "Enacted", "when": "May 26, 2026",
     "note": "6-month pause, unanimous; facilities over 5 MW. At least two "
             "public hearings required during the moratorium period",
     "lat": 40.48, "lon": -88.99, "expires": "2026-11-26", "as_of": "2026-08-13",
     "source": "https://www.wglt.org/local-news/2026-05-26/bloomington-approves-6-month-moratorium-on-data-centers"},
    {"locality": "Normal", "state": "IL", "level": "Local",
     "status": "Enacted", "when": "May 18, 2026",
     "note": "Unanimous; runs through Nov 30, 2026. Preemptive — no active "
             "data center inquiries at the time",
     "lat": 40.51, "lon": -88.99, "expires": "2026-11-30", "as_of": "2026-08-13",
     "source": "https://www.wglt.org/local-news/2026-05-15/normal-to-vote-on-6-month-data-center-moratorium"},
    {"locality": "Iron County", "state": "UT", "level": "Local",
     "status": "Enacted", "when": "May 26, 2026",
     "note": "Ordinance 2026-13: 180-day halt on data centers, data center "
             "power plants, and solar power plants; prospective only",
     "lat": 37.68, "lon": -113.06, "expires": "2026-11-22", "as_of": "2026-08-13",
     "source": "https://ironcountyut.gov/files/planning/data-center-solar-moratorium.pdf"},
    {"locality": "Manitowoc County", "state": "WI", "level": "Local",
     "status": "Enacted", "when": "Apr 29, 2026",
     "note": "18-month pause, unanimous; covers facilities with more than "
             "1 PB of storage. Requested by three towns (Two Creeks, Two "
             "Rivers, Mishicot) after land-purchase approaches to farmers",
     "lat": 44.09, "lon": -87.66, "expires": "2027-10-29", "as_of": "2026-08-13",
     "source": "https://www.wpr.org/news/manitowoc-county-board-approves-18-month-data-center-moratorium"},
    {"locality": "Smithfield", "state": "RI", "level": "Local",
     "status": "Enacted", "when": "Jun 4, 2026",
     "note": "Adopted 4-1 May 5, effective Jun 4; data centers not permitted in any zoning district",
     "lat": 41.92, "lon": -71.55, "expires": None, "as_of": "2026-08-04",
     "source": "https://www.wpri.com/news/local-news/northwest/smithfield-town-council-approves-ordinance-to-prevent-construction-of-data-centers/"},
    {"locality": "Meridian Township", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "May 19, 2026",
     "note": "6-month pause on data centers and battery storage facilities; "
             "preemptive — no proposals pending",
     "lat": 42.72, "lon": -84.42, "expires": "2026-11-19", "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-05-28/meridian-township-is-officially-putting-a-pause-on-any-data-centers-that-might-come-to-town"},
    {"locality": "Washington Township (Macomb Co.)", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "May 2026",
     "note": "6-month pause or until zoning ordinance amendments take effect; "
             "passed after Prologis withdrew a 312-acre 'technical campus' "
             "application",
     "lat": 42.72, "lon": -82.92, "expires": "2026-11-23", "as_of": "2026-08-13",
     "source": "https://www.detroitnews.com/story/news/local/macomb-county/2026/05/23/washington-township-passes-six-month-moratorium-on-data-centers/90213646007/"},
    {"locality": "Hill County", "state": "TX", "level": "Local",
     "status": "Rescinded", "when": "Rescinded Jun 4, 2026",
     "note": "1-year moratorium passed May 2026, rescinded after a $100M federal suit "
             "argued Texas counties lack moratorium authority; suit dismissed Jul 2026. "
             "Replaced with a disclosure checklist for large projects",
     "lat": 32.01, "lon": -97.13, "expires": None, "as_of": "2026-08-04",
     "source": "https://www.texastribune.org/2026/06/05/texas-hill-county-moratorium-rescinded-data-centers/"},
    {"locality": "DeKalb County", "state": "GA", "level": "Local",
     "status": "Enacted", "when": "Extended Jul 7, 2026",
     "note": "Extended 6-1 through Mar 30, 2027 — two weeks after the commission "
             "rejected the planning department's proposed data center zoning rules, "
             "so the pause is now the only thing holding the line",
     "lat": 33.77, "lon": -84.23, "expires": "2027-03-30", "as_of": "2026-08-04",
     "source": "https://www.decaturish.com/news/dekalb/dekalb-extends-data-center-moratorium-through-early-2027/article_22c7d964-ee2f-49f5-a879-9abaabbd6b45.html"},
    {"locality": "Lysander (Onondaga Co.)", "state": "NY", "level": "Local",
     "status": "Enacted", "when": "May 7, 2026",
     "note": "6-month; no applications accepted by Town, Planning or Zoning boards",
     "lat": 43.17, "lon": -76.35, "expires": "2026-11-06", "as_of": "2026-08-04",
     "source": "https://www.informnny.com/news/local-news/lysander-board-approves-six-month-data-center-moratorium-residents-speak-out-against-project-proposal/"},
    {"locality": "Perth (Fulton Co.)", "state": "NY", "level": "Local",
     "status": "Enacted", "when": "Jun 4, 2026",
     "note": "1-year, passed 3-0; extendable by simple resolution",
     "lat": 43.05, "lon": -74.19, "expires": "2027-06-04", "as_of": "2026-08-04",
     "source": "https://www.dailygazette.com/the_recorder/leader_herald/data-center-moratorium/article_28560f58-b336-4cae-8773-f0a04cd3001b.html"},
    {"locality": "Tonawanda (Erie Co.)", "state": "NY", "level": "Local",
     "status": "Enacted", "when": "Effective Aug 3, 2026",
     "note": "Local Law 2-2026: 1-year pause on facilities drawing 20 MW or more — "
             "a lower threshold than the state EO's 50 MW",
     "lat": 43.02, "lon": -78.88, "expires": "2027-08-03", "as_of": "2026-08-04",
     "source": "https://www.beenews.com/ken_ton_bee/ken_ton_bee/news/town-adopts-one-year-moratorium-on-data-centers/article_b2afd139-7437-48f8-af10-1787cf849858.html"},
    {"locality": "Newfield (Tompkins Co.)", "state": "NY", "level": "Local",
     "status": "Enacted", "when": "Jul 9, 2026",
     "note": "1-year townwide pause on data processing centers and cryptocurrency "
             "mining; town is drafting comprehensive-plan amendments before it lapses",
     "lat": 42.36, "lon": -76.60, "expires": "2027-07-09", "as_of": "2026-08-04",
     "source": "https://www.tompkinsweekly.com/events/newfield-approves-one-year-moratorium-on-data-centers-fdcffc41"},
    {"locality": "Groton", "state": "CT", "level": "Local",
     "status": "Enacted", "when": "Jun 21, 2022",
     "note": "1-year moratorium on data centers over 5,000 sq ft; lapsed into permanent "
             "zoning in Jun 2023 capping buildings at 12,500 sq ft and barring water cooling",
     "lat": 41.35, "lon": -72.08, "expires": "2023-06-21", "as_of": "2026-08-04",
     "source": "https://theday.com/local-news/20220621/groton-approves-one-year-moratorium-on-large-scale-data-centers"},
    {"locality": "Peculiar", "state": "MO", "level": "Local",
     "status": "Enacted", "when": "Oct 2024",
     "note": "Board of Aldermen reversed an earlier zoning change and struck "
             "'data center' from the light-industrial code, permanently "
             "blocking Diode Ventures' $1.5B Harper Road Technology Park. "
             "A 100-day moratorium (Aug 2024) preceded the permanent change",
     "lat": 38.72, "lon": -94.46, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.kshb.com/news/local-news/peculiar-reverses-zoning-for-data-center-after-cries-from-neighbors"},
    {"locality": "Bangor", "state": "ME", "level": "Local",
     "status": "Enacted", "when": "Apr 13, 2026",
     "note": "180-day pause, 9-0. City cited lack of information about "
             "infrastructure impacts and no state-level framework to reference",
     "lat": 44.80, "lon": -68.77, "expires": "2026-10-10", "as_of": "2026-08-13",
     "source": "https://www.wabi.tv/2026/04/14/bangor-passes-180-day-moratorium-data-center-development/"},
    # North Carolina — 20+ jurisdictions since late 2025.
    {"locality": "Gates County", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Dec 17, 2025",
     "note": "1-year pause, unanimous; covers all data center and crypto "
             "mining applications. Preventative — prompted by two inquiries "
             "from a data center consulting firm. County water system has been "
             "under its own moratorium since 2018",
     "lat": 36.44, "lon": -76.70, "expires": "2026-12-17", "as_of": "2026-08-13",
     "source": "https://gatescountync.gov/vertical/sites/%7BC4993D33-7F3A-4388-B179-2EC1739C7E2E%7D/uploads/Data_Center_Moratorium.pdf"},
    {"locality": "Brevard", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Mar 2026",
     "note": "90-day moratorium while city staff draft UDO text amendments. "
             "Term may have lapsed — confirm current status with the city",
     "lat": 35.23, "lon": -82.73, "expires": "2026-06-23", "as_of": "2026-08-13",
     "source": "https://www.transylvaniatimes.com/news/transylvania-county-not-pursuing-data-centers/article_51ca8d5c-a379-4b4b-8676-480c6bda88dd.html"},
    {"locality": "Clay County", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Jan 8, 2026",
     "note": "Permanent ban — Ordinance No. 01.08.2026 prohibits the "
             "establishment, construction, expansion, or operation of "
             "commercial data centers in all zoning districts",
     "lat": 35.06, "lon": -83.75, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.clayconc.com/ordinances"},
    {"locality": "Canton", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Feb 11, 2026",
     "note": "12-month pause, unanimous; covers data centers, crypto mining, "
             "and server farms. ~200 residents attended. Prompted by inquiries "
             "about the former Evergreen Packaging paper mill site",
     "lat": 35.53, "lon": -82.84, "expires": "2027-02-11", "as_of": "2026-08-13",
     "source": "https://www.bpr.org/climate-environment/2026-02-12/canton-passes-a-12-month-moratorium-on-data-centers-and-cryptocurrency-mining"},
    {"locality": "Chatham County", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Feb 11, 2026",
     "note": "12-month pause on data centers, data processing, and crypto "
             "mining in unincorporated areas; expires Feb 11, 2027 or when "
             "new zoning regulations are adopted. A developer has sued, "
             "claiming it blocks a planned 750 MW project",
     "lat": 35.70, "lon": -79.26, "expires": "2027-02-11", "as_of": "2026-08-13",
     "source": "https://www.chathamcountync.gov/Home/Components/News/News/17295/19"},
    {"locality": "Kings Mountain", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Feb 24, 2026",
     "note": "182-day (6-month) pause, passed 5-2. Planning department studying "
             "setbacks/screening, utility capacity, and noise standards",
     "lat": 35.25, "lon": -81.34, "expires": "2026-08-25", "as_of": "2026-08-13",
     "source": "https://www.cityofkm.com/AgendaCenter/ViewFile/Minutes/_02242026-934"},
    {"locality": "Boone", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Mar 23, 2026",
     "note": "1-year pause, unanimous (5-0); covers data centers and crypto "
             "mining within town limits. Nearly 100 residents attended in "
             "support. Council pursuing permanent regulations",
     "lat": 36.22, "lon": -81.67, "expires": "2027-03-23", "as_of": "2026-08-13",
     "source": "https://www.bpr.org/2026-03-23/boone-approves-data-center-development-moratorium"},
    {"locality": "Apex", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Apr 15, 2026",
     "note": "12-month pause, unanimous; effective Apr 28. Covers data centers, "
             "data processing, and crypto mining. Followed withdrawal of the "
             "250 MW 'New Hill Digital Campus' proposal",
     "lat": 35.73, "lon": -78.85, "expires": "2027-04-27", "as_of": "2026-08-13",
     "source": "https://abc11.com/post/apex-nc-leaders-hold-public-hearing-proposed-data-center-moratorium/18885810/"},
    {"locality": "Orange County", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Apr 21, 2026",
     "note": "1-year pause, 6-0; covers large-scale data centers including AI, "
             "crypto mining, and data processing. No large-scale data centers "
             "currently in the county",
     "lat": 36.06, "lon": -79.12, "expires": "2027-04-21", "as_of": "2026-08-13",
     "source": "https://www.orangecountync.gov/m/newsflash/Home/Detail/1391"},
    {"locality": "Rowan County", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Apr 20, 2026",
     "note": "1-year pause, unanimous; prohibits zoning or rezoning for data "
             "center purposes. Does NOT apply to the existing Long Ferry Road "
             "project (Edged Energy). 100+ residents attended; 5,200+ petition "
             "signatures",
     "lat": 35.64, "lon": -80.47, "expires": "2027-05-04", "as_of": "2026-08-13",
     "source": "https://www.wfae.org/politics/2026-04-21/rowan-county-approves-one-year-moratorium-on-new-data-centers"},
    {"locality": "Swain County", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Apr 21, 2026",
     "note": "12-month pause, unanimous. Public hearing drew 140 residents "
             "and 34 speakers in Bryson City. Two citizen advisory committees "
             "formed to study impacts",
     "lat": 35.49, "lon": -83.49, "expires": "2027-04-21", "as_of": "2026-08-13",
     "source": "https://www.bpr.org/climate-environment/2026-04-22/swain-county-unanimously-passes-data-center-moratorium"},
    {"locality": "Watauga County", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Apr 21, 2026",
     "note": "1-year pause, unanimous; suspends new data center construction "
             "county-wide. County collaborating with utilities, conservation "
             "groups, and NC DEQ on permanent regulations. Separate from the "
             "Town of Boone moratorium (Mar 23)",
     "lat": 36.23, "lon": -81.69, "expires": "2027-04-21", "as_of": "2026-08-13",
     "source": "https://www.wataugademocrat.com/news/county-commissioners-pass-a-one-year-data-center-moratorium-for-watauga-county/article_012ca886-b088-4aee-8321-6b0f851fcdca.html"},
    {"locality": "Madison County", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Jun 2023",
     "note": "1-year moratorium on data processing facilities including crypto "
             "mining and large server farms, passed unanimously. Would have "
             "expired ~Jun 2024; no extension or replacement ordinance found. "
             "Confirm current status with the county before citing as active",
     "lat": 35.85, "lon": -82.70, "expires": "2024-06-13", "as_of": "2026-08-13",
     "source": "https://news.yahoo.com/madison-county-imposes-1-moratorium-090939100.html"},
    {"locality": "Clyde", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Jan 14, 2026",
     "note": "Permanent ban — Board of Aldermen voted unanimously to amend "
             "the zoning ordinance to prohibit data centers in all zoning "
             "districts. Proactive; no specific proposal was pending",
     "lat": 35.53, "lon": -82.91, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.themountaineer.com/"},
    # ── Promoted from the news-scan queue, 2026-08-04 ──────────────────────
    {"locality": "Rockford", "state": "IL", "level": "Local",
     "status": "Enacted", "when": "Aug 3, 2026",
     "note": "6-month pause passed 14-0. Does not cover the Edson Road parcel "
             "Monarch Energy is pursuing — an existing annexation agreement "
             "already permits data centers there",
     "lat": 42.27, "lon": -89.09, "expires": "2027-02-03", "as_of": "2026-08-04",
     "source": "https://www.rockrivercurrent.com/2026/08/rockford-approves-data-center-moratorium-but-not-for-monarchs-land/"},
    {"locality": "Flagler County", "state": "FL", "level": "Local",
     "status": "Enacted", "when": "Aug 3, 2026",
     "note": "1-year, unanimous on second reading. Unincorporated county only — "
             "municipalities including Palm Coast are unaffected. Amended to drop "
             "the 'large-scale' qualifier, so it covers all data center types",
     "lat": 29.47, "lon": -81.29, "expires": "2027-08-03", "as_of": "2026-08-04",
     "source": "https://www.observerlocalnews.com/news/2026/aug/03/flagler-county-approves-one-year-data-center-moratorium/"},
    {"locality": "Lakeland", "state": "FL", "level": "Local",
     "status": "Enacted", "when": "Aug 3, 2026",
     "note": "1-year, 4-3; covers any use drawing 50 MW or more, not just data "
             "centers. Took effect immediately",
     "lat": 28.04, "lon": -81.95, "expires": "2027-08-03", "as_of": "2026-08-04",
     "source": "https://www.lkldnow.com/lakeland-approves-one-year-moratorium-on-data-centers/"},
    {"locality": "Pasco County", "state": "FL", "level": "Local",
     "status": "Enacted", "when": "Jul 14, 2026",
     "note": "1-year on large data center construction, passed unanimously",
     "lat": 28.32, "lon": -82.44, "expires": "2027-07-14", "as_of": "2026-08-04",
     "source": "https://www.wusf.org/politics-issues/2026-07-15/pasco-county-one-year-moratorium-large-data-centers"},
    {"locality": "Manatee County", "state": "FL", "level": "Local",
     "status": "Enacted", "when": "Jul 28, 2026",
     "note": "Approved unanimously; term not documented in the coverage read, so "
             "no end date is recorded here — confirm the ordinance before citing "
             "a duration",
     "lat": 27.48, "lon": -82.35, "expires": None, "as_of": "2026-08-04",
     "source": "https://www.wusf.org/politics-issues/2026-08-04/manatee-county-pumps-brakes-data-centers-joining-hernando-pasco"},
    {"locality": "Athens", "state": "OH", "level": "Local",
     "status": "Enacted", "when": "Aug 4, 2026",
     "note": "1-year permit pause inside city limits; the mayor or service-safety "
             "director may extend it a second year. Does not reach the site that "
             "prompted it — that parcel is in Athens Township, outside the city",
     "lat": 39.33, "lon": -82.10, "expires": "2027-08-04", "as_of": "2026-08-04",
     "source": "https://woub.org/2026/08/04/athens-city-council-one-year-moratorium-data-centers/"},
    {"locality": "Nashville", "state": "TN", "level": "Local",
     "status": "Enacted", "when": "Jul 21, 2026",
     "note": "Metro Council passed the city's first data center regulations plus a "
             "permit moratorium; an amendment holds the pause to Dec 1 whether or "
             "not the regulations pass",
     "lat": 36.16, "lon": -86.78, "expires": "2026-12-01", "as_of": "2026-08-04",
     "source": "https://nashvillebanner.com/2026/07/21/nashville-data-center-regulations-moratorium/"},
    {"locality": "San Marcos", "state": "TX", "level": "Local",
     "status": "Enacted", "when": "Jun 16, 2026",
     "note": "Not a pause — a zoning ban. Passed 4-3 after failing once by a single "
             "vote; data centers are now ineligible in every zoning district. First "
             "Texas city to do it, and a live test of the 2023 'Death Star' "
             "preemption law",
     "lat": 29.88, "lon": -97.94, "expires": None, "as_of": "2026-08-04",
     "source": "https://www.texastribune.org/2026/06/30/texas-san-marcos-data-center-ban-zoning-laws/"},
    {"locality": "Hays County", "state": "TX", "level": "Local",
     "status": "Enacted", "when": "2026",
     "note": "Resolution pausing review of high-water-use and large industrial "
             "projects in unincorporated areas through Dec 31, 2026. Weaker than "
             "the moratorium first proposed: it raises scrutiny and halts "
             "development agreements rather than blocking projects outright",
     "lat": 30.05, "lon": -98.03, "expires": "2026-12-31", "as_of": "2026-08-04",
     "source": "https://www.kxan.com/news/local/hays/hays-county-approves-resolution-to-pause-review-of-data-centers/"},
    {"locality": "Prince George's County", "state": "MD", "level": "Local",
     "status": "Enacted", "when": "Jul 7, 2026",
     "note": "2-year pause on hyperscale data centers — the longest in Maryland. "
             "Bars the planning department from considering applications until the "
             "council passes regulations. Three members abstained; one voted no",
     "lat": 38.83, "lon": -76.85, "expires": "2028-07-07", "as_of": "2026-08-04",
     "source": "https://wtop.com/prince-georges-county/2026/07/prince-georges-co-extends-pause-on-hyperscale-data-center-development/"},
    {"locality": "Baltimore County", "state": "MD", "level": "Local",
     "status": "Enacted", "when": "Feb 2026",
     "note": "1-year, passed unanimously; runs no later than Jan 1, 2027. A "
             "6-month extension was being introduced in Aug 2026 with a bipartisan "
             "majority and the county executive behind it",
     "lat": 39.40, "lon": -76.60, "expires": "2027-01-01", "as_of": "2026-08-04",
     "source": "https://www.wypr.org/wypr-news/2026-07-17/baltimore-countys-data-center-ban-likely-to-be-extended"},
    {"locality": "Imperial County", "state": "CA", "level": "Local",
     "status": "Enacted", "when": "Jun 16, 2026",
     "note": "45-day urgency ordinance, extended unanimously on Jul 14 by 10 months "
             "15 days — a full year of paused permits while an advisory committee "
             "drafts rules (recommendations due Jan 2027)",
     "lat": 32.79, "lon": -115.56, "expires": "2027-06-16", "as_of": "2026-08-04",
     "source": "https://inewsource.org/2026/07/14/data-center-moratorium-imperial-county/"},
    {"locality": "Desert Hot Springs", "state": "CA", "level": "Local",
     "status": "Enacted", "when": "Jun 17, 2026",
     "note": "45-day urgency ordinance extended unanimously on Jul 7 by 22 months "
             "15 days — the full two years California law allows",
     "lat": 33.96, "lon": -116.50, "expires": "2028-06-17", "as_of": "2026-08-04",
     "source": "https://riversiderecord.org/desert-hot-springs-data-center-moratorium-extended/"},
    {"locality": "Lochbuie", "state": "CO", "level": "Local",
     "status": "Enacted", "when": "Jul 21, 2026",
     "note": "5-year pause approved 6-1 — the longest active moratorium in "
             "Colorado. Residents cited drought as the driving concern",
     "lat": 40.03, "lon": -104.72, "expires": "2031-07-21", "as_of": "2026-08-04",
     "source": "https://www.rmpbs.org/news/government/lochbuie-approves-five-year-data-center-moratorium"},
    {"locality": "Broomfield", "state": "CO", "level": "Local",
     "status": "Enacted", "when": "Jul 7, 2026",
     "note": "Ordinance 2313, passed 9-0. Covers facilities with a projected load "
             "of 10 MW or more; runs through Dec 2, 2027 or until permanent rules "
             "are adopted",
     "lat": 39.92, "lon": -105.09, "expires": "2027-12-02", "as_of": "2026-08-04",
     "source": "https://www.coloradopolitics.com/2026/07/08/broomfield-passes-temporary-ban-on-new-data-center-construction/"},
    {"locality": "Spokane", "state": "WA", "level": "Local",
     "status": "Enacted", "when": "Jun 23, 2026",
     "note": "Ordinance C36887, passed 6-1 as an emergency measure: 1-year citywide "
             "pause on building permits for new data centers. Followed news that "
             "Avista had been approached about a 500 MW facility",
     "lat": 47.66, "lon": -117.43, "expires": "2027-06-23", "as_of": "2026-08-04",
     "source": "https://my.spokanecity.org/news/releases/2026/06/23/spokane-city-council-passes-one-year-moratorium-on-data-centers/"},
    {"locality": "Sierra County", "state": "NM", "level": "Local",
     "status": "Enacted", "when": "Jul 22, 2026",
     "note": "18-month pause passed unanimously in a surprise vote after public "
             "comment, following a Spaceport America data center proposal",
     "lat": 33.13, "lon": -107.25, "expires": "2028-01-22", "as_of": "2026-08-04",
     "source": "https://sourcenm.com/2026/07/22/new-mexico-county-adopts-data-center-moratorium-as-residents-protest-spaceport-proposal/"},
    {"locality": "Linn County", "state": "IA", "level": "Local",
     "status": "Enacted", "when": "Jul 1, 2026",
     "note": "18-month pause on large-scale data center rezonings in unincorporated "
             "areas, passed 2-1 and effective immediately — adopted even after the "
             "county had put an ordinance in place",
     "lat": 42.08, "lon": -91.60, "expires": "2028-01-01", "as_of": "2026-08-04",
     "source": "https://www.linncountyiowa.gov/CivicAlerts.aspx?AID=4487"},
    {"locality": "London", "state": "KY", "level": "Local",
     "status": "Enacted", "when": "Aug 3, 2026",
     "note": "2-year pause passed 5-1, running to Sep 30, 2028 and extendable a "
             "further year by council",
     "lat": 37.13, "lon": -84.08, "expires": "2028-09-30", "as_of": "2026-08-04",
     "source": "https://www.wkyt.com/2026/08/04/london-city-council-passes-2-year-data-center-moratorium/"},
    {"locality": "Logan County", "state": "KY", "level": "Local",
     "status": "Enacted", "when": "Jul 30, 2026",
     "note": "12-month pause in unincorporated areas, adopted specifically to study "
             "local water supply capacity against high-consumption users",
     "lat": 36.86, "lon": -86.88, "expires": "2027-07-30", "as_of": "2026-08-04",
     "source": "https://www.wbko.com/2026/07/30/logan-county-approves-12-month-moratorium-data-centers/"},
    {"locality": "Paulding County", "state": "GA", "level": "Local",
     "status": "Enacted", "when": "Jul 28, 2026",
     "note": "Suspends new data center applications, zoning requests and civil plan "
             "reviews through Dec 31, 2026",
     "lat": 33.92, "lon": -84.87, "expires": "2027-01-01", "as_of": "2026-08-04",
     "source": "https://www.fox5atlanta.com/news/paulding-county-approves-data-center-moratorium-freezing-projects"},
    {"locality": "Cherokee County", "state": "GA", "level": "Local",
     "status": "Enacted", "when": "Jul 22, 2026",
     "note": "30-day pause, with a stated plan to extend it into early 2027 — the "
             "short term is procedural, not the real horizon",
     "lat": 34.24, "lon": -84.48, "expires": "2026-08-21", "as_of": "2026-08-04",
     "source": "https://www.atlantanewsfirst.com/2026/07/22/cherokee-county-approves-data-center-moratorium/"},
    {"locality": "Walker County", "state": "GA", "level": "Local",
     "status": "Enacted", "when": "Extended Aug 7, 2026",
     "note": "30-day pause adopted Jul 9, extended unanimously to 180 days on "
             "Aug 7 with a data center study group (report due Dec 4, 2026). "
             "Unincorporated county only",
     "lat": 34.73, "lon": -85.30, "expires": "2027-02-03", "as_of": "2026-08-13",
     "source": "https://www.local3news.com/local-news/update-walker-county-extends-data-center-moratorium-for-180-days-creates-study-group/article_f776be3a-1089-4068-ade1-781ea32a2ab9.html"},
    {"locality": "Augusta", "state": "GA", "level": "Local",
     "status": "Enacted", "when": "Extended Jul 21, 2026",
     "note": "Commissioners declined to adopt the proposed data center ordinance "
             "and extended the existing moratorium 60 more days instead",
     "lat": 33.47, "lon": -81.97, "expires": "2026-09-19", "as_of": "2026-08-04",
     "source": "https://www.wjbf.com/news/augusta-commissioners-delaying-approval-of-data-center-ordinance-and-extending-moratorium-by-60-days/"},
    {"locality": "Monroe Township (Gloucester Co.)", "state": "NJ", "level": "Local",
     "status": "Enacted", "when": "Apr 22, 2026",
     "note": "Two ordinances banning data centers township-wide. Hexa Builders is "
             "suing for more than $300M in federal court — the test case for "
             "whether a small municipality can absorb the litigation risk of a ban",
     "lat": 39.68, "lon": -75.06, "expires": None, "as_of": "2026-08-04",
     "source": "https://www.cbsnews.com/philadelphia/news/monroe-gloucester-new-jersey-data-center-ban-law/"},
    {"locality": "Phillipsburg", "state": "NJ", "level": "Local",
     "status": "Enacted", "when": "Apr 2026",
     "note": "Ordinance 2026-08 prohibits data centers throughout the town; council "
             "is folding the ban into the master plan to harden it against "
             "challenge",
     "lat": 40.69, "lon": -75.19, "expires": None, "as_of": "2026-08-04",
     "source": "https://www.tapinto.net/towns/phillipsburg/sections/government/articles/town-council-moves-to-solidify-phillipsburg-s-data-center-ban-via-master-plan-update"},
    {"locality": "Warren", "state": "NJ", "level": "Local",
     "status": "Enacted", "when": "Jun 23, 2026",
     "note": "Township ban on data centers",
     "lat": 40.63, "lon": -74.51, "expires": None, "as_of": "2026-08-04",
     "source": "https://www.roi-nj.com/2026/06/23/industry/energy-utilities/warren-becomes-latest-town-in-n-j-to-ban-data-centers/"},
    {"locality": "Holly Springs", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Jun 16, 2026",
     "note": "1-year pause on data center construction",
     "lat": 35.65, "lon": -78.83, "expires": "2027-06-16", "as_of": "2026-08-04",
     "source": "https://www.wral.com/news/local/holly-springs-officials-aprove-one-year-pause-data-center-development-june-2026/"},
    {"locality": "Gordon County", "state": "GA", "level": "Local",
     "status": "Enacted", "when": "Extended May 2026",
     "note": "Moratoriums on data centers and anaerobic digestion facilities "
             "extended through Jan 29, 2027 while staff drafts ordinances",
     "lat": 34.50, "lon": -84.87, "expires": "2027-01-29", "as_of": "2026-08-04",
     "source": "https://www.discovergordoncounty.com/local/gordon-county-commissioners-extend-moratoriums-on-data-centers-anaerobic-digestion-facilities-through-january-2027/"},
    {"locality": "Carroll County", "state": "GA", "level": "Local",
     "status": "Enacted", "when": "Mar 3, 2026",
     "note": "100-day pause on permits for data centers and battery energy storage "
             "in unincorporated areas, later extended another 100 days. The current "
             "end date is not documented in the coverage read — confirm before "
             "citing it as active",
     "lat": 33.58, "lon": -85.08, "expires": None, "as_of": "2026-08-04",
     "source": "https://gradickcommunications.com/carroll-county-board-of-commissioners-approve-100-day-moratorium-on-data-centers-battery-energy-storage-systems/"},
    {"locality": "Montgomery County", "state": "MD", "level": "Local",
     "status": "Enacted", "when": "Jul 28, 2026",
     "note": "18-month moratorium approved unanimously, alongside limits on data "
             "center development",
     "lat": 39.14, "lon": -77.20, "expires": "2028-01-28", "as_of": "2026-08-04",
     "source": "https://www.montgomerycountymd.gov/news/council-approves-18-month-data-center-moratorium-places-limitations-data-center-development"},
    {"locality": "Sarasota County", "state": "FL", "level": "Local",
     "status": "Enacted", "when": "Jul 8, 2026",
     "note": "1-year freeze approved 5-0 on accepting, reviewing or approving "
             "hyperscale applications (50 MW+ under the state definition); "
             "commissioners signalled interest in a permanent ban",
     "lat": 27.18, "lon": -82.35, "expires": "2027-07-08", "as_of": "2026-08-04",
     "source": "https://www.businessobserverfl.com/news/2026/jul/09/sarasota-county-data-center-moratorium/"},
    {"locality": "Merrillville", "state": "IN", "level": "Local",
     "status": "Enacted", "when": "Jun 1, 2026",
     "note": "1-year moratorium running Jun 1, 2026 to May 31, 2027 — council "
             "explicitly wants to watch the campus under construction in "
             "neighbouring Hobart before writing rules",
     "lat": 41.48, "lon": -87.33, "expires": "2027-05-31", "as_of": "2026-08-04",
     "source": "https://nwitimes.com/news/local/lake/merrillville/article_f506303d-f5ce-4bcc-bb4c-a6abf68fb24d.html"},
    {"locality": "Vienna Township (Trumbull Co.)", "state": "OH", "level": "Local",
     "status": "Enacted", "when": "Extended Aug 2026",
     "note": "Extended 60 days, Aug 16 to Oct 16, 2026, while the county planning "
             "commission reviews the township's draft data center zoning",
     "lat": 41.24, "lon": -80.66, "expires": "2026-10-16", "as_of": "2026-08-04",
     "source": "https://www.tribtoday.com/news/local-news/2026/08/vienna-extends-data-center-moratorium/"},
    {"locality": "Boardman", "state": "OH", "level": "Local",
     "status": "Enacted", "when": "Apr 28, 2026",
     "note": "1-year moratorium to study regulation and zoning changes",
     "lat": 41.02, "lon": -80.66, "expires": "2027-04-28", "as_of": "2026-08-13",
     "source": "https://www.wkbn.com/news/local-news/boardman-news/boardman-places-moratorium-on-data-centers/"},
    {"locality": "La Crosse County", "state": "WI", "level": "Local",
     "status": "Enacted", "when": "Jun 18, 2026",
     "note": "18-month pause in unincorporated areas; county stood up an ad hoc "
             "committee to study data centers, and the city of La Crosse is taking "
             "part in that work while drafting its own rules",
     "lat": 43.90, "lon": -91.01, "expires": "2027-12-18", "as_of": "2026-08-04",
     "source": "https://www.wxow.com/news/la-crosse-county-board-approves-data-center-moratorium/article_89162c21-3240-4d86-9e2d-8a6c3489ddc8.html"},
    {"locality": "Morris", "state": "CT", "level": "Local",
     "status": "Enacted", "when": "May 20, 2026",
     "note": "2-year moratorium covering data centers and battery storage, "
             "passed unanimously by the PZC. Driven by farmland and rural "
             "character concerns",
     "lat": 41.69, "lon": -73.19, "expires": "2028-05-20", "as_of": "2026-08-13",
     "source": "https://www.yahoo.com/news/us/articles/why-one-connecticut-town-approved-100000211.html"},
    # Proposed / under consideration
    {"locality": "Charlotte", "state": "NC", "level": "Local",
     "status": "Proposed", "when": "Jun 9, 2025",
     "note": "180-day moratorium on data centers over 100,000 sq ft; initial "
             "vote deadlocked 5-5 with one member absent, so the motion failed. "
             "Reintroduced in 2026 amid continued community pressure",
     "lat": 35.23, "lon": -80.84, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.charlotteobserver.com/"},
    {"locality": "Durham", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Extended Jun 15, 2026",
     "note": "60-day moratorium passed unanimously May 5, extended to 12 months "
             "on Jun 15. Covers data centers, data processing, and crypto "
             "mining. Council first amended the UDO to remove the local cap on "
             "moratorium length",
     "lat": 35.99, "lon": -78.90, "expires": "2027-06-15", "as_of": "2026-08-13",
     "source": "https://www.wral.com/news/local/durham-city-council-data-center-meeting-may-2026/"},
    {"locality": "Harnett County", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "May 5, 2026",
     "note": "1-year pause, unanimous; unincorporated areas. ~75 minutes of "
             "public comment with no speakers in favour of data centers. "
             "County Manager cited water/electricity consumption concerns",
     "lat": 35.37, "lon": -78.87, "expires": "2027-05-03", "as_of": "2026-08-13",
     "source": "https://jocoreport.com/harnett-county-imposes-moratorium-on-data-centers/"},
    {"locality": "Cumberland County", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Jun 16, 2026",
     "note": "6-month pause, 7-0; unincorporated areas only. Staff developing "
             "a data center ordinance with town halls in Aug and draft in Sep. "
             "Does not reach proposals seeking annexation into Fayetteville",
     "lat": 35.05, "lon": -78.83, "expires": "2026-12-15", "as_of": "2026-08-13",
     "source": "https://www.cityviewnc.com/stories/cumberland-county-enacts-6-month-data-center-moratorium/"},
    {"locality": "Fayetteville", "state": "NC", "level": "Local",
     "status": "Rejected", "when": "Aug 10, 2026",
     "note": "Moratorium motion failed 5-5 on Aug 10; council voted 7-3 to "
             "pursue regulatory ordinance revisions instead, targeted for late "
             "Oct 2026. Cumberland County's 6-month moratorium covers "
             "unincorporated areas but not the city",
     "lat": 35.05, "lon": -78.88, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.cityviewnc.com/stories/fayetteville-punts-data-center-regulations-to-late-october/"},
    {"locality": "Seattle", "state": "WA", "level": "Local",
     "status": "Enacted", "when": "Jun 9, 2026",
     "note": "Emergency ordinance passed 9-0; 1 year, facilities over 20 MVA, "
             "extendable about six months",
     "lat": 47.61, "lon": -122.33, "expires": "2027-06-09", "as_of": "2026-08-04",
     "source": "https://council.seattle.gov/2026/06/09/city-council-passes-emergency-data-center-moratorium-and-policy-framework/"},
    {"locality": "Indianapolis", "state": "IN", "level": "Local",
     "status": "Proposed", "when": "Aug 10, 2026",
     "note": "City-County Council voted 23-1 to advance a moratorium through "
             "end of 2027 to the Metropolitan Development Commission for final "
             "approval (vote scheduled Aug 19). Exempts three already-approved "
             "projects",
     "lat": 39.77, "lon": -86.16, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.wfyi.org/wfyi-news/2026-08-10/indy-council-advances-pause-on-data-centers-sends-to-commission-for-final-approval"},
    {"locality": "Pulaski County", "state": "AR", "level": "Local",
     "status": "Rejected", "when": "Jul 28, 2026",
     "note": "Multiple attempts failed: a May 26 vote appeared to pass but a "
             "tally error voided it (didn't reach the 10-vote two-thirds "
             "threshold); a revised version was explicitly voted down 10-3 on "
             "Jul 28. County now pursuing regulations instead",
     "lat": 34.75, "lon": -92.29, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.arkansasonline.com/news/2026/jul/28/pulaski-county-quorum-court-rejects-data-center/"},
    {"locality": "St. Lawrence County", "state": "NY", "level": "Local",
     "status": "Proposed", "when": "Jun 1, 2026",
     "note": "The county did not adopt a moratorium of its own — it passed a "
             "resolution affirming local zoning authority and urging its "
             "municipalities to consider one. Tracked as a signal, not a restriction",
     "lat": 44.59, "lon": -75.16, "expires": None, "as_of": "2026-08-04",
     "source": "https://www.rockinst.org/blog/updates-on-the-cloud-more-moratoriums-on-data-centers/"},
    {"locality": "Mohawk (Montgomery Co.)", "state": "NY", "level": "Local",
     "status": "Proposed", "when": "Proposed Aug 3, 2026",
     "note": "6-month pause to write zoning rules; public hearing Aug 13, 2026. "
             "Supervisor cites the state EO's 50 MW floor as leaving smaller "
             "facilities unregulated. Would run to Feb 13, 2027 if adopted",
     "lat": 42.92, "lon": -74.42, "expires": None, "as_of": "2026-08-04",
     "source": "https://www.dailygazette.com/leader_herald/the_recorder/news/govt_politics/town-of-mohawk-proposes-data-center-moratorium/article_4b6168e8-568e-4a86-8bd8-bfd298eb59b5.html"},
    {"locality": "Salem", "state": "OR", "level": "Local",
     "status": "Proposed", "when": "Aug 3, 2026",
     "note": "Council voted unanimously to *begin* the process — a 60- or 120-day "
             "moratorium still has to come back for adoption, and staff must first "
             "give the state notice and show a compelling need. No pause is in "
             "effect; a developer advanced its plan ahead of the vote",
     "lat": 44.94, "lon": -123.04, "expires": None, "as_of": "2026-08-04",
     "source": "https://katu.com/news/local/tonight-salem-city-leaders-consider-ai-data-center-moratorium"},
    {"locality": "Jersey City", "state": "NJ", "level": "Local",
     "status": "Proposed", "when": "Introduced Jul 15, 2026",
     "note": "Ordinance 26-057 would bar data centers as the principal use of "
             "industrial land. Passed first reading and the planning board; final "
             "council vote set for Aug 19, 2026",
     "lat": 40.72, "lon": -74.05, "expires": None, "as_of": "2026-08-04",
     "source": "https://www.jerseycitynj.gov/news/jersey_city_introduces_law_to_ban_data_centers"},
    {"locality": "Howell Township", "state": "NJ", "level": "Local",
     "status": "Proposed", "when": "2026",
     "note": "Ordinance reconfirming data centers as a prohibited use; public "
             "hearing and final vote set for Aug 18, 2026",
     "lat": 40.18, "lon": -74.20, "expires": None, "as_of": "2026-08-04",
     "source": "https://patch.com/new-jersey/howell/howell-moves-ban-ai-data-centers-township"},
    {"locality": "Andover Township", "state": "NJ", "level": "Local",
     "status": "Proposed", "when": "May 2026",
     "note": "Township moved to ban AI data centers after a contentious public "
             "meeting; faces a suit from National Land Developers over a former "
             "airport site",
     "lat": 41.00, "lon": -74.74, "expires": None, "as_of": "2026-08-04",
     "source": "https://nj1015.com/andover-township-data-center-ban/"},
    {"locality": "La Crosse", "state": "WI", "level": "Local",
     "status": "Proposed", "when": "Aug 3, 2026",
     "note": "City plan commission advanced an 18-month moratorium, matching the "
             "county's; still needs council adoption",
     "lat": 43.80, "lon": -91.24, "expires": None, "as_of": "2026-08-04",
     "source": "https://www.news8000.com/lifestyle/technology/la-crosse-city-plan-commission-advances-18-month-moratorium-on-data-center-development/article_30c5ee0a-61f9-48e3-9b24-ec2f90ae5e17.html"},
    {"locality": "Yakima County", "state": "WA", "level": "Local",
     "status": "Enacted", "when": "2026",
     "note": "6-month moratorium in unincorporated areas, unanimous. Studying "
             "economic, health, agricultural, and water impacts",
     "lat": 46.60, "lon": -120.51, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.yakimaherald.com/news/local/government/yakima-county-commissioners-pass-six-month-data-center-moratorium/article_997dbbc7-7fe0-476a-9d92-73179f958bf7.html"},
    {"locality": "Greensboro", "state": "NC", "level": "Local",
     "status": "Proposed", "when": "Public hearing Aug 17, 2026",
     "note": "Council voted 5-4 on Jul 21 against even starting the moratorium "
             "process, then reversed course and set a public hearing on a 120-day "
             "pause for facilities above 10 MW. Nothing is in effect yet",
     "lat": 36.07, "lon": -79.79, "expires": None, "as_of": "2026-08-04",
     "source": "https://www.wfdd.org/politics-government/2026-08-04/greensboro-randolph-officials-take-steps-to-address-data-centers"},
    {"locality": "New Haven", "state": "CT", "level": "Local",
     "status": "Proposed", "when": "Jul 6, 2026",
     "note": "12-month moratorium pitched; would bar city departments from "
             "accepting or approving data center applications or conversions",
     "lat": 41.31, "lon": -72.93, "expires": None, "as_of": "2026-08-04",
     "source": "https://www.newhavenindependent.org/2026/07/06/12-month-pause-pitched-for-data-center-dev/"},
    # Rejected
    {"locality": "Henderson", "state": "NV", "level": "Local",
     "status": "Rejected", "when": "Jul 28, 2026",
     "note": "Council rejected the mayor's 180-day pause after nearly two hours of "
             "public comment favouring it, opting for code changes and "
             "project-by-project development agreements instead",
     "lat": 36.04, "lon": -114.98, "expires": None, "as_of": "2026-08-04",
     "source": "https://thenevadaindependent.com/article/henderson-rejects-data-center-moratorium-instead-exploring-code-changes"},
    {"locality": "Cheyenne", "state": "WY", "level": "Local",
     "status": "Rejected", "when": "May 27, 2026",
     "note": "12-month proposal voted down 8–1 after 3.5 hours of public comment",
     "lat": 41.14, "lon": -104.82, "expires": None, "as_of": "2026-08-04",
     "source": "https://wyofile.com/cheyenne-rejects-moratorium-on-data-centers/"},
    # State-level (no single map point)
    {"locality": "New York (statewide)", "state": "NY", "level": "State",
     "status": "Enacted", "when": "Jul 14, 2026",
     "note": "EO 62: first statewide pause. Holds DEC discretionary approvals for "
             "50+ MW facilities until DPS finishes a generic environmental impact "
             "statement — roughly a year, but tied to that study, not a fixed date",
     "lat": None, "lon": None, "expires": None, "as_of": "2026-08-04",
     "source": "https://www.governor.ny.gov/executive-order/no-62-establishing-temporary-moratorium-data-centers-new-york-while-state-develops"},
    {"locality": "New York (S10642/A11560)", "state": "NY", "level": "State",
     "status": "Proposed", "when": "Passed both houses Jun 4, 2026",
     "note": "Responsible Data Center Development Act: 1-year moratorium on state "
             "permits for 20+ MW facilities, plus a dedicated utility rate class, a "
             "DEC impact study, and a host-community benefit program. Passed the "
             "Senate 43-17. Per the Senate's own record it had not been delivered to "
             "the Governor as of Aug 4, 2026 — Hochul acted by executive order "
             "(EO 62, 50 MW floor) instead. Still live, and stricter than the EO",
     "lat": None, "lon": None, "expires": None, "as_of": "2026-08-04",
     "source": "https://www.nysenate.gov/legislation/bills/2025/S10642"},
    {"locality": "Texas (Abbott directive)", "state": "TX", "level": "State",
     "status": "Enacted", "when": "Aug 3, 2026",
     "note": "Governor directed ERCOT and PUC to freeze all data center "
             "interconnection progress pending a comprehensive audit. ERCOT "
             "halted 'Batch Zero' large-load study and suspended Aug 7 "
             "classification notifications. Queue holds ~474 GW (~90%% data "
             "centers) — 5x Texas's record peak demand. Audit scope: tax "
             "incentives, water, community impacts, on-site generation, "
             "ownership. Excludes projects with on-site generation and areas "
             "outside ERCOT. PUCT open meeting Aug 20. No end date — treat "
             "as a hold on the queue, not a construction ban",
     "lat": None, "lon": None, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.texastribune.org/2026/08/03/texas-data-center-project-audit-greg-abbott/"},
    {"locality": "Oregon (statewide)", "state": "OR", "level": "State",
     "status": "Proposed", "when": "Aug 4, 2026",
     "note": "Democratic lawmakers proposed a three-year moratorium on new large "
             "data centers",
     "lat": None, "lon": None, "expires": None, "as_of": "2026-08-04",
     "source": "https://centraloregonian.com/2026/08/04/democratic-lawmakers-propose-three-year-moratorium-on-new-large-data-centers-in-oregon/"},
    {"locality": "Georgia (HB 1012)", "state": "GA", "level": "State",
     "status": "Proposed", "when": "2026",
     "note": "Would bar local permits for new data centers until Mar 1, 2027, "
             "exempting approvals issued before Jul 1, 2026",
     "lat": None, "lon": None, "expires": None, "as_of": "2026-08-04",
     "source": "https://goodjobsfirst.org/data-center-moratorium-bills-are-spreading-in-2026/"},
    {"locality": "Maine (statewide)", "state": "ME", "level": "State",
     "status": "Vetoed", "when": "Apr 24, 2026",
     "note": "LD 307 would have paused 20+ MW facilities to Nov 2027; governor vetoed",
     "lat": None, "lon": None, "expires": None, "as_of": "2026-08-04",
     "source": "https://www.rockinst.org/blog/updates-on-the-cloud-more-moratoriums-on-data-centers/"},
    {"locality": "Ohio (ballot measure)", "state": "OH", "level": "State",
     "status": "Rejected", "when": "Jul 1, 2026",
     "note": "Conserve Ohio's proposed constitutional amendment to ban data "
             "centers over 25 MW gathered only ~70,000 of the required 413,488 "
             "signatures by the Jul 1 deadline. Organizers plan to try again "
             "for the 2027 ballot",
     "lat": None, "lon": None, "expires": None, "as_of": "2026-08-13",
     "source": "https://ballotpedia.org/Ohio_Prohibition_of_Data_Center_Construction_Amendment_(2026)"},
    {"locality": "Bell County", "state": "KY", "level": "Local",
     "status": "Enacted", "when": "Jul 2, 2026",
     "note": "2-year moratorium, passed unanimously by the fiscal court; "
             "halted a Murray Industries hyperscale project that had already "
             "begun clearing land along the Bell-Knox county line",
     "lat": 36.75, "lon": -83.55, "expires": "2028-07-02", "as_of": "2026-08-11",
     "source": "https://www.wymt.com/2026/07/02/bell-county-passes-data-center-moratorium-halting-construction-2-years/"},
    {"locality": "Citrus County", "state": "FL", "level": "Local",
     "status": "Enacted", "when": "May 26, 2026",
     "note": "1-year freeze on new data-center rezoning applications, "
             "development orders and building permits, adopted unanimously; "
             "the Holder Industrial Park project it was aimed at was later "
             "withdrawn by the developer",
     "lat": 28.83, "lon": -82.33, "expires": "2027-05-26", "as_of": "2026-08-11",
     "source": "https://www.fox13news.com/news/citrus-county-commission-approves-freeze-ai-data-center-rezoning-applications"},
    {"locality": "Little Rock", "state": "AR", "level": "Local",
     "status": "Rejected", "when": "Aug 4, 2026",
     "note": "18-month permitting halt on hyperscale data centers "
             "(250,000+ sq ft or 75+ MW), including a planned Google "
             "facility at the Port of Little Rock; failed 4-4 with two "
             "directors absent. The city's June 3, 2026 data-center "
             "regulations (no groundwater cooling, noise monitors) remain "
             "in effect regardless.",
     "lat": 34.75, "lon": -92.29, "expires": None, "as_of": "2026-08-12",
     "source": "https://www.nwaonline.com/news/2026/aug/04/little-rock-data-center-moratorium-falls-short-in/"},
    {"locality": "Coachella", "state": "CA", "level": "Local",
     "status": "Enacted", "when": "Jun 4, 2026",
     "note": "45-day moratorium on new data-center applications, adopted "
             "unanimously alongside terminating the city's agreement with "
             "Stronghold Power over a 400+-acre, six-data-center campus; "
             "extended Jul 9, 2026 as the council moves toward a permanent "
             "ban. Treat any specific expiry as unconfirmed — the council "
             "was actively extending it as of this writing.",
     "lat": 33.68, "lon": -116.17, "expires": None, "as_of": "2026-08-12",
     "source": "https://www.nbcpalmsprings.com/2026/06/04/coachella-approves-data-center-moratorium-ends-stronghold-power-agreement"},
    {"locality": "Aurora", "state": "CO", "level": "Local",
     "status": "Rejected", "when": "Aug 10, 2026",
     "note": "Emergency resolution for a 6-month moratorium on data-center "
             "construction failed 6-5, Mayor Mike Coffman casting the "
             "tiebreaking vote against; council instead passed a resolution "
             "to develop data-center standards (water/zoning) within 35 days, "
             "without a pause.",
     "lat": 39.73, "lon": -104.83, "expires": None, "as_of": "2026-08-12",
     "source": "https://www.denver7.com/news/local-news/in-your-community/aurora-arapahoe-county/aurora-city-council-rejects-six-month-data-center-ban-as-it-pursues-new-regulations"},
    {"locality": "DeSoto County", "state": "FL", "level": "Local",
     "status": "Enacted", "when": "Jul 29, 2026",
     "note": "1-year moratorium on new data-center rezoning, approved 4-0 "
             "(one commissioner recused). Does not apply to rezoning "
             "applications already tied to an 800+-acre data-center project "
             "proposed earlier in 2026, which can still advance.",
     "lat": 27.22, "lon": -81.86, "expires": "2027-07-29", "as_of": "2026-08-12",
     "source": "https://www.wgcu.org/top-story/2026-07-29/desoto-approves-data-center-moratorium-but-controversial-project-can-advance"},
    {"locality": "Snohomish County", "state": "WA", "level": "Local",
     "status": "Enacted", "when": "Jun 24, 2026",
     "note": "6-month emergency zoning moratorium on new data-center "
             "development in unincorporated Snohomish County, adopted "
             "unanimously so the council can craft a permanent policy.",
     "lat": 48.03, "lon": -122.13, "expires": "2026-12-24", "as_of": "2026-08-12",
     "source": "https://www.heraldnet.com/2026/06/25/snohomish-county-council-approves-emergency-data-center-moratorium/"},
    {"locality": "Taylor County", "state": "FL", "level": "Local",
     "status": "Rejected", "when": "Jul 7, 2026",
     "note": "Motion to impose a data-center moratorium failed at the "
             "commission's first public discussion on data centers; "
             "commissioners instead scheduled a public workshop for Aug 25.",
     "lat": 30.11, "lon": -83.58, "expires": None, "as_of": "2026-08-12",
     "source": "https://www.wctv.tv/2026/07/07/taylor-county-commission-votes-down-data-center-moratorium-residents-wonder-what-comes-next/"},
    {"locality": "Clinton", "state": "IA", "level": "Local",
     "status": "Rejected", "when": "Jun 9, 2026",
     "note": "Proposed moratorium rejected 5-2 as QTS considers an AI data "
             "center campus north of US-30/west of Mill Creek Parkway; "
             "council members argued a pause could send the wrong message "
             "to developers.",
     "lat": 41.84, "lon": -90.19, "expires": None, "as_of": "2026-08-12",
     "source": "https://qctimes.com/news/local/government-politics/article_5827c520-3b42-407e-9610-c8a6421385e5.html"},
    {"locality": "Cave City", "state": "KY", "level": "Local",
     "status": "Enacted", "when": "May 20, 2026",
     "note": "12-month moratorium on new data centers, approved 4-1 on "
             "second reading to allow time to draft zoning language; the "
             "city was subsequently sued over the moratorium and has asked "
             "for the suit's dismissal.",
     "lat": 37.13, "lon": -85.96, "expires": "2027-05-20", "as_of": "2026-08-12",
     "source": "https://www.wbko.com/2026/05/21/cave-city-council-enacts-12-month-moratorium-data-centers/"},
    {"locality": "Sanford", "state": "ME", "level": "Local",
     "status": "Enacted", "when": "Extended Aug 5, 2026",
     "note": "91-day emergency moratorium enacted May 19, 2026, halting a "
             "proposed Mousam River data center project; extended "
             "unanimously for 180 more days on Aug 5, 2026.",
     "lat": 43.44, "lon": -70.77, "expires": "2027-01-31", "as_of": "2026-08-12",
     "source": "https://www.pressherald.com/2026/08/05/sanford-extends-data-center-moratorium-for-180-days/"},
    {"locality": "Socorro County", "state": "NM", "level": "Local",
     "status": "Enacted", "when": "Jun 9, 2026",
     "note": "1-year moratorium on data centers and related infrastructure "
             "on unincorporated county land, adopted unanimously after 2+ "
             "months of opposition to the proposed Green Data Center; also "
             "began forming an advisory committee to recommend regulations.",
     "lat": 34.06, "lon": -106.89, "expires": "2027-06-09", "as_of": "2026-08-12",
     "source": "https://www.kob.com/news/top-news/new-mexico-county-approves-1-year-data-center-moratorium/"},
    {"locality": "Nye County", "state": "NV", "level": "Local",
     "status": "Enacted", "when": "Jun 2, 2026",
     "note": "Countywide moratorium on new commercial data-center "
             "applications, approved unanimously after the Nye County Water "
             "District's governing board raised Pahrump Valley water-supply "
             "concerns; stays in place until a regulatory ordinance is "
             "adopted rather than a fixed date.",
     "lat": 36.21, "lon": -115.98, "expires": None, "as_of": "2026-08-12",
     "source": "https://pvtimes.com/news/nye-county-approves-data-center-moratorium-186722/"},
    {"locality": "Farmville", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Aug 3, 2026",
     "note": "12-month moratorium on data-center development, approved "
             "unanimously by the town's Board of Commissioners to allow "
             "staff time to research impacts and draft ordinance language, "
             "after East Energy Renewables (headquartered in Farmville) "
             "pitched a data-center network to town leaders in February.",
     "lat": 35.60, "lon": -77.60, "expires": "2027-08-03", "as_of": "2026-08-12",
     "source": "https://www.witn.com/2026/08/04/farmville-board-adopts-12-month-moratorium-potential-data-center-after-residents-voice-opposition/"},
    {"locality": "Summit", "state": "NJ", "level": "Local",
     "status": "Enacted", "when": "Jun 16, 2026",
     "note": "Ordinance banning AI data centers (20+ MW or significant "
             "municipal water impact) and, separately, detention centers, "
             "passed the same night — the data-center ban is permanent "
             "zoning, not a time-limited pause, aimed partly at keeping one "
             "off the former Bristol Myers Squibb campus. Some residents say "
             "the ordinance's enforcement mechanism falls short.",
     "lat": 40.72, "lon": -74.36, "expires": None, "as_of": "2026-08-12",
     "source": "https://www.tapinto.net/towns/summit/sections/government/articles/summit-council-takes-up-controversial-ai-data-center-and-detention-ban"},
    {"locality": "Newberry County", "state": "SC", "level": "Local",
     "status": "Enacted", "when": "Jul 16, 2026",
     "note": "12-month moratorium on accepting new data-center permits, "
             "confirmed unanimously after the council unanimously denied "
             "the 'Project Altair' land-sale ordinance in June. Staff "
             "directed to research appropriate locations for future "
             "data-center development.",
     "lat": 34.27, "lon": -81.62, "expires": "2027-07-16", "as_of": "2026-08-12",
     "source": "https://www.foxcarolina.com/2026/07/16/newberry-county-council-unanimously-confirms-year-long-moratorium-data-centers/"},
    {"locality": "Colleton County", "state": "SC", "level": "Local",
     "status": "Enacted", "when": "Jul 7, 2026",
     "note": "6-month moratorium on special exceptions, conditional-use "
             "approvals, and other land-use/development approvals for "
             "data centers (Ordinance 26-O-04), adopted unanimously. "
             "Planning Commission separately approved a 'digital "
             "infrastructure overlay district' text amendment.",
     "lat": 32.90, "lon": -80.67, "expires": "2027-01-07", "as_of": "2026-08-12",
     "source": "https://scdailygazette.com/2026/06/26/sc-counties-enacting-data-center-moratoriums/"},
    {"locality": "Dodge County", "state": "WI", "level": "Local",
     "status": "Enacted", "when": "Aug 10, 2026",
     "note": "18-month moratorium on data-center development in "
             "county-zoned unincorporated areas, approved 29-2 by the "
             "Board of Supervisors after a public hearing. Initiated by "
             "Supervisor Cathy Houchin following constituent concerns "
             "about a Beaver Dam-area data center's impact on water.",
     "lat": 43.42, "lon": -88.73, "expires": "2028-02-10", "as_of": "2026-08-12",
     "source": "https://dailydodge.com/dodge-county-to-hold-public-hearing-on-proposed-data-center-moratorium/"},
    {"locality": "Salix", "state": "IA", "level": "Local",
     "status": "Proposed", "when": "Aug 12, 2026",
     "note": "1-year moratorium on data centers, formal vote scheduled "
             "Aug 12, 2026. Council voted 3-2 (Jul 8) to advance the "
             "concept after 100+ residents debated a MidAmerican Energy "
             "data center on ~900 acres of annexed farmland.",
     "lat": 42.28, "lon": -96.29, "expires": None, "as_of": "2026-08-12",
     "source": "https://www.ktiv.com/2026/08/12/salix-city-council-consider-data-center-moratorium/"},
    {"locality": "Hogansville", "state": "GA", "level": "Local",
     "status": "Enacted", "when": "May 2026",
     "note": "90-day moratorium on data-center applications, extended "
             "30 days in Jul 2026 (to approximately early Sep 2026) "
             "while the city develops a new data-center ordinance with "
             "consultant Canvas Planning and a citizen input committee. "
             "QTS (Eagle South LLC) has proposed a 600 MW facility",
     "lat": 33.17, "lon": -84.91, "expires": "2026-09-01", "as_of": "2026-08-13",
     "source": "https://www.lagrangenews.com/news/hogansville-approves-90-day-moratorium-for-data-centers-9d59b175"},
    # ── Promoted from the news-scan queue, 2026-08-13 ──────────────────────
    {"locality": "Jeffersonville", "state": "IN", "level": "Local",
     "status": "Enacted", "when": "Aug 4, 2026",
     "note": "1-year pause, 8-0; does not affect the Meta facility at River "
             "Ridge Commerce Center, which operates under federal/state military "
             "land-use authority",
     "lat": 38.28, "lon": -85.74, "expires": "2027-08-04", "as_of": "2026-08-13",
     "source": "https://www.wave3.com/2026/08/04/jeffersonville-passes-year-long-data-center-moratorium-amid-resident-outcry-major-utility-disclosures/"},
    {"locality": "Palm Beach County", "state": "FL", "level": "Local",
     "status": "Enacted", "when": "Jul 2026",
     "note": "Zoning-in-progress freeze on AI data center applications in "
             "unincorporated areas, 5-2; up to 1 year or until new zoning "
             "adopted. Project Tango (filed pre-freeze) was rejected 5-2",
     "lat": 26.71, "lon": -80.27, "expires": "2027-07-31", "as_of": "2026-08-13",
     "source": "https://www.bocaratontribune.com/bocaratonnews/2026/07/palm-beach-county-enacts-ai-data-center-moratorium/"},
    {"locality": "Escambia County", "state": "FL", "level": "Local",
     "status": "Enacted", "when": "Aug 2026",
     "note": "Ban on large-scale data centers (50+ MW) in unincorporated areas. "
             "Resolution passed 5-0 on Jul 23, ordinance approved 4-1 in Aug. "
             "Small server rooms (accessory use) still permitted",
     "lat": 30.67, "lon": -87.38, "expires": None, "as_of": "2026-08-13",
     "source": "https://weartv.com/news/local/escambia-county-commissioners-vote-to-block-large-scale-data-centers-in-unincorporated-areas"},
    {"locality": "Santa Rosa County", "state": "FL", "level": "Local",
     "status": "Enacted", "when": "Jul 23, 2026",
     "note": "12-month moratorium in unincorporated areas; residents at the "
             "Jul 9 hearing pressed for an outright permanent ban. Follows "
             "SB 484 (DeSantis) granting local authority to restrict data centers",
     "lat": 30.68, "lon": -87.02, "expires": "2027-07-23", "as_of": "2026-08-13",
     "source": "https://srpressgazette.com/santa-rosa-county-looks-to-approve-a-12-month-ban-on-data-center-development/"},
    {"locality": "Warrick County", "state": "IN", "level": "Local",
     "status": "Enacted", "when": "Aug 11, 2026",
     "note": "180-day moratorium, unanimous; Area Plan Commission had separately "
             "tabled its data center ordinance in Jul and paused projects "
             "through Dec 2026",
     "lat": 38.09, "lon": -87.28, "expires": "2027-02-07", "as_of": "2026-08-13",
     "source": "https://www.14news.com/2026/08/11/warrick-commissioners-vote-moratorium-pause-data-center-development/"},
    {"locality": "Islip", "state": "NY", "level": "Local",
     "status": "Enacted", "when": "Aug 12, 2026",
     "note": "18-month ban on new data center facilities; second Long Island "
             "town after Brookhaven",
     "lat": 40.73, "lon": -73.21, "expires": "2028-02-12", "as_of": "2026-08-13",
     "source": "https://longisland.news12.com/2026/08/12/town-of-islip-approves-18-month-ban-on-new-data-centers/5cLcS6GGkBbkzPxp55Kx9u"},
    {"locality": "Brookhaven", "state": "NY", "level": "Local",
     "status": "Enacted", "when": "Jul 17, 2026",
     "note": "18-month moratorium, unanimous after nearly 6 hours of public "
             "hearings; town code doesn't currently define data centers. "
             "First Long Island town to act",
     "lat": 40.78, "lon": -72.92, "expires": "2028-01-17", "as_of": "2026-08-13",
     "source": "https://patch.com/new-york/sachem/brookhaven-pols-enact-18-month-moratorium-data-centers-throughout-town"},
    {"locality": "Waxhaw", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Aug 11, 2026",
     "note": "12-month moratorium, unanimous; covers data centers, crypto mining, "
             "and related digital infrastructure. Preemptive — no proposals pending",
     "lat": 34.93, "lon": -80.74, "expires": "2027-08-11", "as_of": "2026-08-13",
     "source": "https://www.wbtv.com/2026/08/13/town-waxhaw-unanimously-approved-12-month-moratorium-data-centers/"},
    {"locality": "Cobb County", "state": "GA", "level": "Local",
     "status": "Enacted", "when": "Extended Aug 2026",
     "note": "180-day moratorium enacted Feb 2026, extended an additional "
             "180 days ~Aug 2026; unincorporated areas only. Ordinance "
             "changes in progress",
     "lat": 33.94, "lon": -84.58, "expires": "2027-02-15", "as_of": "2026-08-13",
     "source": "https://www.wsbtv.com/news/local/cobb-county/cobb-county-commission-extends-data-center-moratorium-180-days/T7AXV7XHNNGZDI2CSYEI6M7YN4/"},
    {"locality": "Rochester Hills", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Extended Aug 2026",
     "note": "180-day moratorium adopted Mar 2026, extended through mid-Mar 2027; "
             "studying noise, vibration, light pollution, water, electricity demand",
     "lat": 42.66, "lon": -83.15, "expires": "2027-03-15", "as_of": "2026-08-13",
     "source": "https://www.detroitnews.com/story/news/local/oakland-county/2026/08/11/rochester-hills-extends-data-center-moratorium/91256551007/"},
    {"locality": "Independence County", "state": "AR", "level": "Local",
     "status": "Enacted", "when": "Aug 11, 2026",
     "note": "5-year moratorium, unanimous — the longest in Arkansas. "
             "Preemptive; no project currently proposed",
     "lat": 35.74, "lon": -91.57, "expires": "2031-08-11", "as_of": "2026-08-13",
     "source": "https://arkansasadvocate.com/2026/08/11/outside-of-little-rock-arkansas-counties-and-cities-move-ahead-on-data-center-moratoriums/"},
    {"locality": "Russellville", "state": "AR", "level": "Local",
     "status": "Enacted", "when": "Jul 2026",
     "note": "6-month pause on data center approvals",
     "lat": 35.28, "lon": -93.13, "expires": "2027-01-31", "as_of": "2026-08-13",
     "source": "https://arkansasadvocate.com/2026/08/11/outside-of-little-rock-arkansas-counties-and-cities-move-ahead-on-data-center-moratoriums/"},
    {"locality": "Union County", "state": "AR", "level": "Local",
     "status": "Enacted", "when": "Jun 30, 2026",
     "note": "Ordinance 1795: 1-year moratorium (Jul 10, 2026 – Jul 9, 2027), "
             "unanimous; studying water, electricity, utilities, emergency services, "
             "property and zoning impacts",
     "lat": 33.27, "lon": -92.60, "expires": "2027-07-09", "as_of": "2026-08-13",
     "source": "https://www.eldoradonews.com/news/2026/jun/30/union-county-officials-approve-one-year/"},
    {"locality": "Carroll County", "state": "AR", "level": "Local",
     "status": "Enacted", "when": "Jun 17, 2026",
     "note": "1-year moratorium on high-impact industrial and high-intensity "
             "digital infrastructure facilities, unanimous emergency ordinance",
     "lat": 36.34, "lon": -93.53, "expires": "2027-06-17", "as_of": "2026-08-13",
     "source": "https://www.ky3.com/2026/06/17/carroll-county-unanimously-passes-1-year-moratorium-data-centers-other-high-intensity-digital-infrastructure-facilities/"},
    {"locality": "Ridgely", "state": "MD", "level": "Local",
     "status": "Enacted", "when": "Aug 2026",
     "note": "1-year moratorium; part of an Eastern Shore wave of local action "
             "after a controversial Federalsburg data center proposal",
     "lat": 38.95, "lon": -75.88, "expires": "2027-08-31", "as_of": "2026-08-13",
     "source": "http://www.stardem.com/news/caroline/ridgely-passes-one-year-moratorium-on-data-centers/article_97ec1ae7-4a05-4e9e-9551-4bc8b650043a.html"},
    {"locality": "Monterey Park", "state": "CA", "level": "Local",
     "status": "Enacted", "when": "Jun 2, 2026",
     "note": "Permanent ban via ballot measure, approved overwhelmingly by "
             "voters — first U.S. city to ban data centers by popular vote. "
             "Originally a 45-day moratorium (Jan 21), extended 1 year, then "
             "put on the ballot",
     "lat": 34.06, "lon": -118.12, "expires": None, "as_of": "2026-08-13",
     "source": "https://lapublicpress.org/2026/06/monterey-park-data-center-ban-elections-2026/"},
    {"locality": "Cherry Hill", "state": "NJ", "level": "Local",
     "status": "Enacted", "when": "Jul 28, 2026",
     "note": "Ordinance prohibiting data centers as a non-permitted use, "
             "unanimous; small server rooms for standalone businesses still "
             "allowed. Most populous municipality in Camden County",
     "lat": 39.93, "lon": -75.00, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.inquirer.com/south-jersey/cherry-hill-nj-data-center-ban-20260728.html"},
    {"locality": "Medford", "state": "NJ", "level": "Local",
     "status": "Enacted", "when": "Jun 25, 2026",
     "note": "Ordinance prohibiting data centers within town limits, unanimous. "
             "Preemptive — no proposals pending",
     "lat": 39.87, "lon": -74.82, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.inquirer.com/south-jersey/medford-data-center-ban-artificial-intelligence-20260625.html"},
    {"locality": "Mansfield Township (Burlington Co.)", "state": "NJ", "level": "Local",
     "status": "Enacted", "when": "Jul 15, 2026",
     "note": "Ordinance banning data centers as a named use category, unanimous. "
             "27th NJ municipality to pass a local ban",
     "lat": 40.07, "lon": -74.72, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.yahoo.com/news/us/articles/mansfield-revises-zoning-strengthen-data-123013988.html"},
    {"locality": "Chesterfield", "state": "NJ", "level": "Local",
     "status": "Enacted", "when": "Jul 2026",
     "note": "Ban on data centers in all zones, adopted alongside Mansfield "
             "Township",
     "lat": 40.12, "lon": -74.66, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.inquirer.com/south-jersey/cherry-hill-nj-data-center-ban-20260728.html"},
    {"locality": "Berkeley Heights", "state": "NJ", "level": "Local",
     "status": "Enacted", "when": "Jul 2026",
     "note": "Permanent ban on data centers in all zones, unanimous; followed "
             "debate over potential Nokia site conversion",
     "lat": 40.68, "lon": -74.44, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.tapinto.net/towns/berkeley-heights/sections/business-and-finance/articles/berkeley-heights-bans-data-centers-townwide-capping-weeks-of-debate-over-nokia-site"},
    # Proposed / under consideration — 2026-08-13 additions
    {"locality": "Louisville", "state": "KY", "level": "Local",
     "status": "Proposed", "when": "Aug 4, 2026",
     "note": "6-month moratorium advanced by P&Z Committee 7-1 on Aug 4; full "
             "Metro Council vote expected Aug 13. Originally proposed Sep 2025 "
             "after a 1.6M sq ft hyperscale was approved with little public input",
     "lat": 38.25, "lon": -85.76, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.lpm.org/news/2026-08-04/louisville-metro-council-advances-data-center-moratorium"},
    {"locality": "Statesville", "state": "NC", "level": "Local",
     "status": "Proposed", "when": "First reading Aug 2026",
     "note": "180-day moratorium passed first reading; second reading scheduled "
             "Sep 14, 2026. No new data centers planned but city has received "
             "inquiries and the UDC does not address data centers",
     "lat": 35.79, "lon": -80.89, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.iredellfreenews.com/news-features/2026/statesville-city-council-approves-180-day-moratorium-on-data-centers"},
    {"locality": "Fort Worth", "state": "TX", "level": "Local",
     "status": "Proposed", "when": "Aug 11, 2026",
     "note": "Council voted unanimously to begin 90-day moratorium process; "
             "public hearings required before it takes effect (~Feb 2027). "
             "Also created a Data Center & Infrastructure Committee",
     "lat": 32.75, "lon": -97.33, "expires": None, "as_of": "2026-08-13",
     "source": "https://fortworthreport.org/2026/08/12/data-center-moratorium-takes-first-steps-after-fort-worth-city-councils-unanimous-vote/"},
    {"locality": "Denton", "state": "TX", "level": "Local",
     "status": "Proposed", "when": "Aug 5, 2026",
     "note": "Council voted 4-3 to proceed with a possible 90-day moratorium; "
             "public hearings tentatively Sep 22 / Oct 27, final adoption Dec 2",
     "lat": 33.21, "lon": -97.13, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.keranews.org/news/2026-08-05/denton-moves-toward-data-center-moratorium-city-council-weighs-stricter-development-rules"},
    {"locality": "Marshalltown", "state": "IA", "level": "Local",
     "status": "Proposed", "when": "First reading Aug 12, 2026",
     "note": "4-month moratorium passed first reading 6-1; motion to waive "
             "subsequent readings failed. Council previously voted down a "
             "6-month moratorium in Jun",
     "lat": 42.05, "lon": -92.91, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.timesrepublican.com/news/todays-news/2026/08/marshalltown-city-council-passes-first-reading-of-data-center-moratorium/"},
    {"locality": "East Brunswick", "state": "NJ", "level": "Local",
     "status": "Proposed", "when": "Aug 2026",
     "note": "Zoning ban on data centers in commercial, business and industrial "
             "districts advanced by council; hearing set for Aug 10",
     "lat": 40.43, "lon": -74.42, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.tapinto.net/towns/east-brunswick/sections/government/articles/east-brunswick-council-advances-broad-zoning-ban-on-data-centers"},
    {"locality": "Loudoun County", "state": "VA", "level": "Local",
     "status": "Proposed", "when": "Jul 2026",
     "note": "Board of Supervisors voted 6-1 to direct staff to prepare "
             "moratorium options by Sep 15. Legal questions remain about "
             "Virginia law's allowance of blanket moratoriums. World's largest "
             "data center hub (~46M sq ft constructed or permitted)",
     "lat": 39.08, "lon": -77.64, "expires": None, "as_of": "2026-08-13",
     "source": "https://virginiabusiness.com/loudoun-supervisors-mull-data-center-moratorium/"},
    # ── Batch 2 — additional promotions, 2026-08-13 ───────────────────────
    {"locality": "Oklahoma City", "state": "OK", "level": "Local",
     "status": "Enacted", "when": "Apr 22, 2026",
     "note": "Emergency moratorium through end of 2026 on zoning and development "
             "applications for data centers, unanimous. Exempts 75 MW and below "
             "after a later amendment, plus two pending rezonings",
     "lat": 35.47, "lon": -97.52, "expires": "2026-12-31", "as_of": "2026-08-13",
     "source": "https://www.okc.gov/News-articles/Oklahoma-City-Council-approves-moratorium-on-new-data-centers"},
    {"locality": "Boone County", "state": "IN", "level": "Local",
     "status": "Enacted", "when": "Jun 16, 2026",
     "note": "1-year moratorium in unincorporated areas, unanimous; 12th Indiana "
             "county to pause. Does not affect Meta's data centers (in "
             "incorporated Advance)",
     "lat": 40.05, "lon": -86.47, "expires": "2027-06-15", "as_of": "2026-08-13",
     "source": "https://boonecounty.in.gov/2026/06/15/19190/"},
    {"locality": "Grant County", "state": "IN", "level": "Local",
     "status": "Enacted", "when": "Mar 16, 2026",
     "note": "24-month moratorium; gives officials time to study zoning, land use, "
             "infrastructure, and gather public input",
     "lat": 40.51, "lon": -85.66, "expires": "2028-03-16", "as_of": "2026-08-13",
     "source": "https://www.chronicle-tribune.com/news/commissioners-pass-data-center-moratorium/article_a55a569b-62b5-578c-912e-f183d461f1b9.html"},
    {"locality": "Fayette County", "state": "IN", "level": "Local",
     "status": "Enacted", "when": "May 18, 2026",
     "note": "1-year pause; no local policy governing data centers existed. "
             "Consultant developing a framework for the Area Plan Commission",
     "lat": 39.64, "lon": -85.18, "expires": "2027-05-18", "as_of": "2026-08-13",
     "source": "https://www.wfyi.org/statewide/2026-07-06/indiana-counties-data-center-moratoriums-bans-2026"},
    {"locality": "Starke County", "state": "IN", "level": "Local",
     "status": "Enacted", "when": "Dec 2025",
     "note": "1-year moratorium on hyperscale data center projects (>5,000 sq ft) "
             "in unincorporated areas. Plan commission recommended a 1-year "
             "extension in Jul 2026",
     "lat": 41.28, "lon": -86.63, "expires": "2026-12-31", "as_of": "2026-08-13",
     "source": "https://starke.in.gov/dlp_document/ordinance-2025-37-hyperscale-data-center-moratorium/"},
    {"locality": "Marshall County", "state": "IN", "level": "Local",
     "status": "Enacted", "when": "Apr 20, 2026",
     "note": "Permanent ban — replaced a temporary moratorium with a prohibition "
             "in the county zoning ordinance. One of two IN counties (with Cass) "
             "to outright ban data centers",
     "lat": 41.35, "lon": -86.31, "expires": None, "as_of": "2026-08-13",
     "source": "https://wsbt.com/news/local/marshall-county-approves-permanent-ban-on-data-centers-effective-immediately-data-centers-solar-farms-industrial-size-projects-development-county-council-regulations-counties-experts-industries-marshall-county-indiana"},
    {"locality": "Cass County", "state": "IN", "level": "Local",
     "status": "Enacted", "when": "2026",
     "note": "Permanent ban on new data centers — one of two IN counties (with "
             "Marshall) to outright ban rather than pause",
     "lat": 40.76, "lon": -86.35, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.wfyi.org/statewide/2026-07-06/indiana-counties-data-center-moratoriums-bans-2026"},
    {"locality": "Johnson City", "state": "TN", "level": "Local",
     "status": "Enacted", "when": "Extended May 22, 2026",
     "note": "Moratorium extended unanimously to Dec 3, 2026 while a special "
             "board drafts noise and distance regulations. Data centers limited "
             "to I-2 Heavy Industrial zone since 2025. 5,000+ of 6,000 survey "
             "respondents 'extremely concerned'",
     "lat": 36.31, "lon": -82.35, "expires": "2026-12-03", "as_of": "2026-08-13",
     "source": "https://www.supertalk929.com/2026/05/22/johnson-city-commission-votes-to-extend-data-center-moratorium/"},
    {"locality": "McMinnville", "state": "TN", "level": "Local",
     "status": "Enacted", "when": "Jun 3, 2026",
     "note": "18-month moratorium, unanimous; prompted by a proposed 25 MW "
             "Nvidia GB200 NVL72 AI campus. 2,600+ petition signatures. "
             "Town halls scheduled Jun 25 and 29",
     "lat": 35.68, "lon": -85.77, "expires": "2027-12-03", "as_of": "2026-08-13",
     "source": "https://www.wsmv.com/2026/06/03/mcminnville-approves-18-month-moratorium-new-data-centers-creating-requirements-numerous-impact-studies/"},
    {"locality": "Athens-Clarke County", "state": "GA", "level": "Local",
     "status": "Enacted", "when": "Extended Mar 2026",
     "note": "Moratorium adopted Dec 2025, extended 3 months in Mar 2026 while "
             "an ordinance is drafted. Waiting on state-level legislation before "
             "finalising local rules",
     "lat": 33.96, "lon": -83.38, "expires": None, "as_of": "2026-08-13",
     "source": "https://flagpole.com/news/city-dope/2026/03/11/athens-clarke-county-commission-extends-moratorium-on-data-centers/"},
    {"locality": "Palmetto", "state": "GA", "level": "Local",
     "status": "Enacted", "when": "Mar 2026",
     "note": "Permanent ban — city council unanimously rewrote the industrial "
             "zoning code to exclude data centers entirely",
     "lat": 33.51, "lon": -84.67, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.wabe.org/palmetto-city-council-approves-rewritten-industrial-zoning-code-to-ban-exclude-data-centers/"},
    {"locality": "Hall County", "state": "GA", "level": "Local",
     "status": "Enacted", "when": "Feb 26, 2026",
     "note": "180-day moratorium on data centers, high-density residential, and "
             "detention centers, approved 4-0. Staff examining regulations for "
             "impacts on county services and infrastructure",
     "lat": 34.30, "lon": -83.82, "expires": "2026-08-25", "as_of": "2026-08-13",
     "source": "https://accessnorthga.com/news/hall-co-approves-180-day-moratorium-includes-detention-centers"},
    {"locality": "Coweta County", "state": "GA", "level": "Local",
     "status": "Enacted", "when": "Jun 2026",
     "note": "180-day moratorium; five previously proposed data centers (including "
             "the \\$17B Project Sail) are exempt under vested-rights doctrine. "
             "Expires Dec 23 or when the board adopts ordinance amendments",
     "lat": 33.35, "lon": -84.77, "expires": "2026-12-23", "as_of": "2026-08-13",
     "source": "https://www.times-herald.com/news/commissioners-approve-180-day-data-center-moratorium/article_29dd50b8-88fb-4424-98d9-9d87abfb4588.html"},
    {"locality": "Jackson County", "state": "MO", "level": "Local",
     "status": "Enacted", "when": "Jun 22, 2026",
     "note": "180-day moratorium on data center and battery storage land use "
             "applications, 8-0 (one excused). Amended up from 120 days",
     "lat": 39.01, "lon": -94.35, "expires": "2026-12-19", "as_of": "2026-08-13",
     "source": "https://www.kctv5.com/2026/06/22/jackson-county-legislature-passes-180-day-moratorium-data-center-applications/"},
    {"locality": "Springfield", "state": "MO", "level": "Local",
     "status": "Enacted", "when": "Jun 29, 2026",
     "note": "120-day administrative delay, 8-0. Expires Nov 17 or when council "
             "passes a two-reading bill. Public input sessions to follow",
     "lat": 37.22, "lon": -93.29, "expires": "2026-11-17", "as_of": "2026-08-13",
     "source": "https://www.ky3.com/2026/06/29/springfield-city-council-passes-120-day-moratorium-data-centers-heres-what-happens-next/"},
    {"locality": "Inver Grove Heights", "state": "MN", "level": "Local",
     "status": "Enacted", "when": "Jun 26, 2026",
     "note": "1-year moratorium, 3-2; freezes a proposed 55,000 sq ft / 5 MW "
             "project while staff study zoning, water and noise impacts. "
             "Developer QLevr has threatened a \\$150M lawsuit",
     "lat": 44.85, "lon": -93.04, "expires": "2027-06-26", "as_of": "2026-08-13",
     "source": "https://www.mprnews.org/story/2026/06/26/inver-grove-heights-approves-moratorium-data-centers"},
    {"locality": "Flint", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Jun 8, 2026",
     "note": "12-month moratorium, 7-1; no permits, site plans, or construction "
             "for data centers accepted or processed during the pause",
     "lat": 43.01, "lon": -83.69, "expires": "2027-06-08", "as_of": "2026-08-13",
     "source": "https://www.abc12.com/news/business/flint-city-council-approves-one-year-data-center-moratorium/article_8f64b736-0ba6-41bc-a6ce-032bbf62665c.html"},
    {"locality": "Ypsilanti (YCUA)", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Apr 22, 2026",
     "note": "Utility-level: 12-month moratorium on water and sewer service to "
             "new data centers, unanimous. Blocks a \\$1.25B U-M / Los Alamos "
             "computing facility; U-M has threatened to sue",
     "lat": 42.24, "lon": -83.61, "expires": "2027-04-22", "as_of": "2026-08-13",
     "source": "https://planetdetroit.org/2026/04/data-center-water-moratorium-ypsilanti/"},
    {"locality": "Birmingham", "state": "AL", "level": "Local",
     "status": "Enacted", "when": "Mar 3, 2026",
     "note": "6-month moratorium on 20+ MW facilities, unanimous. Exempts the "
             "Nebius AI factory project (application already under review)",
     "lat": 33.52, "lon": -86.80, "expires": "2026-09-03", "as_of": "2026-08-13",
     "source": "https://www.wbrc.com/2026/03/04/birmingham-city-council-votes-pause-new-data-center-applications-six-months/"},
    {"locality": "Homewood", "state": "AL", "level": "Local",
     "status": "Enacted", "when": "Jun 22, 2026",
     "note": "12-month moratorium, extendable 6 months. Preemptive — no data "
             "center proposals pending. Staff and Planning Commission to study "
             "zoning, operational, and infrastructure standards",
     "lat": 33.47, "lon": -86.80, "expires": "2027-06-22", "as_of": "2026-08-13",
     "source": "https://www.wbrc.com/2026/06/23/not-intended-oppose-economic-development-or-technological-investment-homewood-approves-12-month-temporary-moratorium-data-centers/"},
    {"locality": "Waterford Township (Camden Co.)", "state": "NJ", "level": "Local",
     "status": "Enacted", "when": "Apr 2026",
     "note": "Ban on data centers in all zoning districts; cited heightened "
             "concerns as a Pinelands Community",
     "lat": 39.74, "lon": -74.83, "expires": None, "as_of": "2026-08-13",
     "source": "https://nj1015.com/new-jersey-ai-data-center-bans/"},
    # Proposed — batch 2
    {"locality": "Plainfield", "state": "NJ", "level": "Local",
     "status": "Proposed", "when": "First reading Jul 2026",
     "note": "Citywide ban across all zoning districts introduced by council; "
             "final vote scheduled Aug 10. Council rejected a weaker regulatory "
             "approach in May",
     "lat": 40.63, "lon": -74.41, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.tapinto.net/towns/plainfield/articles/plainfield-city-council-takes-significant-step-towards-data-center-ban"},
    {"locality": "North Plainfield", "state": "NJ", "level": "Local",
     "status": "Proposed", "when": "First reading Jun 2026",
     "note": "Ordinance 26-10 banning data centers borough-wide, 6-0 first "
             "reading; second reading and public hearing pending",
     "lat": 40.63, "lon": -74.43, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.tapinto.net/towns/north-plainfield-slash-green-brook-slash-watchung/articles/north-plainfield-advances-ordinance-to-ban-data-centers-borough-wide"},
    # ── Batch 3 — Alabama ─────────────────────────────────────────────────
    {"locality": "Leeds", "state": "AL", "level": "Local",
     "status": "Enacted", "when": "Jun 3, 2026",
     "note": "1-year moratorium on data center applications and permits, "
             "unanimous (Ord. 2026-06-02). Preemptive — no active proposals, "
             "but residents flagged Alabama Power marketing of nearby Grand "
             "River site to data center developers",
     "lat": 33.55, "lon": -86.54, "expires": "2027-06-03", "as_of": "2026-08-13",
     "source": "https://abc3340.com/news/local/leeds-city-council-approves-one-year-moratorium-on-data-center-development"},
    {"locality": "Springville", "state": "AL", "level": "Local",
     "status": "Enacted", "when": "Jul 6, 2026",
     "note": "1-year moratorium on data center proposals. Preemptive — no "
             "proposals in pipeline",
     "lat": 33.77, "lon": -86.47, "expires": "2027-07-06", "as_of": "2026-08-13",
     "source": "https://newsaegis.com/2026/07/16/data-centers-dont-create-jobs-springville-joins-leeds-places-moratorium-on-centers/"},
    {"locality": "Cullman", "state": "AL", "level": "Local",
     "status": "Enacted", "when": "Jun 24, 2026",
     "note": "12-month moratorium, unanimous (Res. 2026-116). Council also "
             "referred Ord. 2026-42 to Planning Commission to prohibit data "
             "centers outright. County cannot follow suit — limited home rule",
     "lat": 34.17, "lon": -86.84, "expires": "2027-06-24", "as_of": "2026-08-13",
     "source": "https://www.wbrc.com/2026/06/26/cullman-city-council-unanimously-passes-12-month-temporary-moratorium-data-centers/"},
    {"locality": "Fort Payne", "state": "AL", "level": "Local",
     "status": "Enacted", "when": "Jun 16, 2026",
     "note": "6-month moratorium, unanimous. Preemptive — no developer "
             "inquiries. Proposed zoning: M2 heavy-industrial only, "
             "conditional use, 1,000-ft residential setback, EIS, "
             "water-use plan, noise standards",
     "lat": 34.44, "lon": -85.72, "expires": "2026-12-16", "as_of": "2026-08-13",
     "source": "https://256today.com/fort-payne-gets-ahead-of-data-center-boom-with-development-moratorium/"},
    {"locality": "Pinson", "state": "AL", "level": "Local",
     "status": "Enacted", "when": "Aug 2026",
     "note": "1-year moratorium targeting hyper/mega data centers, especially "
             "AI facilities. Preemptive — no proposals pending",
     "lat": 33.69, "lon": -86.68, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.trussvilletribune.com/2026/08/07/pinson-council-passes-one-year-moratorium-on-data-centers/"},
    {"locality": "Fairfield", "state": "AL", "level": "Local",
     "status": "Enacted", "when": "Jul 2026",
     "note": "Temporary moratorium after resident pressure over Patmos "
             "(Missouri AI co.) proposal to convert former Walmart to "
             "colocation data center. Duration not specified",
     "lat": 33.48, "lon": -86.91, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.thecooldown.com/green-tech/patmos-company-proposed-ai-data-center-fairfield-alabama/"},
    # ── Batch 3 — Missouri ────────────────────────────────────────────────
    {"locality": "City of St. Charles", "state": "MO", "level": "Local",
     "status": "Enacted", "when": "May 19, 2026",
     "note": "Permanent ban — data centers removed as a permitted use from all "
             "zoning districts, 7-1 (Bill 14085). Triggered by 'Project Cumulus' "
             "proposal near city water wells. Initial 1-year moratorium Aug 2025",
     "lat": 38.78, "lon": -90.52, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.ksdk.com/article/news/politics/st-charles-city-council-votes-7-1-to-effectively-ban-data-centers/63-7c9264ad-1dc5-4c38-853a-1f7cddf9c2ac"},
    {"locality": "St. Charles County", "state": "MO", "level": "Local",
     "status": "Enacted", "when": "Jul 13, 2026",
     "note": "6-month moratorium on projects >100,000 sq ft or >5 MW, "
             "unanimous. Third-party study of health, infrastructure, and "
             "quality-of-life impacts commissioned",
     "lat": 38.78, "lon": -90.55, "expires": "2027-01-13", "as_of": "2026-08-13",
     "source": "https://www.firstalert4.com/2026/07/14/st-charles-county-approves-6-month-data-center-moratorium/"},
    {"locality": "Columbia", "state": "MO", "level": "Local",
     "status": "Enacted", "when": "May 2026",
     "note": "1-year moratorium pausing data center permits and conditional-use "
             "applications, 6-0. Council approved data center definition and "
             "zoning criteria simultaneously",
     "lat": 38.95, "lon": -92.33, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.columbiamissourian.com/news/local/city-council-approves-data-center-definition-requests-moratorium/article_064eadce-c84e-4bfc-8f9c-b930741b94af.html"},
    # ── Batch 3 — Minnesota ───────────────────────────────────────────────
    {"locality": "Minneapolis", "state": "MN", "level": "Local",
     "status": "Enacted", "when": "May 22, 2026",
     "note": "6-month moratorium on data centers >350,000 sq ft, 8-5. "
             "Downtown core exempt. Zoning ordinance updates and environmental "
             "impact report due during the pause",
     "lat": 44.98, "lon": -93.27, "expires": "2026-11-21", "as_of": "2026-08-13",
     "source": "https://www.startribune.com/minneapolis-data-centers-moratorium/601846955"},
    {"locality": "Eagan", "state": "MN", "level": "Local",
     "status": "Enacted", "when": "Feb 2026",
     "note": "1-year moratorium on data centers >20 MW or within 500 ft of "
             "residential, first MN city to pause. Under legal challenge — "
             "developer filed suit Jun 15 alleging city lacks authority to "
             "regulate electricity demand",
     "lat": 44.80, "lon": -93.17, "expires": "2027-02-17", "as_of": "2026-08-13",
     "source": "https://www.fox9.com/news/eagan-data-center-moratorium-city-faces-lawsuit-minnesota-communities-push-back"},
    {"locality": "Carver", "state": "MN", "level": "Local",
     "status": "Enacted", "when": "Apr 6, 2026",
     "note": "1-year moratorium, unanimous. Proactive — no pending data center "
             "project at time of vote",
     "lat": 44.76, "lon": -93.63, "expires": "2027-04-06", "as_of": "2026-08-13",
     "source": "https://www.fox9.com/news/minnesota-data-centers-carver-city-council-1-year-moratorium-april-11"},
    {"locality": "Wright County", "state": "MN", "level": "Local",
     "status": "Enacted", "when": "May 19, 2026",
     "note": "Emergency 1-year moratorium (Ord. 26-2), unanimous. Applies to "
             "unincorporated areas only. Moratorium Workgroup formed Jun 16 to "
             "evaluate environmental, fiscal, infrastructure, and land use "
             "considerations",
     "lat": 45.17, "lon": -93.96, "expires": "2027-05-19", "as_of": "2026-08-13",
     "source": "https://www.wrightcountymn.gov/m/newsflash/Home/Detail/5177"},
    {"locality": "Washington County", "state": "MN", "level": "Local",
     "status": "Enacted", "when": "Jul 2026",
     "note": "1-year moratorium on new data center applications in "
             "unincorporated areas, 4-1. Extended from originally proposed "
             "6-month pause",
     "lat": 45.04, "lon": -92.89, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.startribune.com/minnesota-counties-data-centers/601857833"},
    # ── Batch 3 — Michigan ────────────────────────────────────────────────
    {"locality": "Wixom", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Mar 24, 2026",
     "note": "6-month moratorium on data center permits, construction, and "
             "installation. Under legal challenge — Sansone Group (519,000 sq ft "
             "complex) filed federal suit Aug 7",
     "lat": 42.53, "lon": -83.54, "expires": "2026-09-24", "as_of": "2026-08-13",
     "source": "https://www.wixomgov.org/departments/construction-development-services-building/data-center-moratorium-ordinance"},
    {"locality": "Saline", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Jan 12, 2026",
     "note": "12-month citywide moratorium on new data center approvals, "
             "unanimous",
     "lat": 42.17, "lon": -83.78, "expires": "2027-01-12", "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "Grand Blanc Township", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Jan 21, 2026",
     "note": "1-year moratorium on data center development",
     "lat": 42.93, "lon": -83.63, "expires": "2027-01-21", "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "Manchester Township", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Oct 14, 2025",
     "note": "2-year moratorium — longest duration among Michigan communities",
     "lat": 42.15, "lon": -84.04, "expires": "2027-10-14", "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "Armada Township", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Jan 14, 2026",
     "note": "180-day moratorium on data center development",
     "lat": 42.84, "lon": -82.88, "expires": "2026-07-13", "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "Green Charter Township", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Dec 9, 2025",
     "note": "1-year moratorium citing water, energy, and noise concerns",
     "lat": 43.61, "lon": -85.50, "expires": "2026-12-09", "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "Pittsfield Township", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Nov 18, 2025",
     "note": "180-day moratorium on data center development",
     "lat": 42.22, "lon": -83.74, "expires": "2026-05-17", "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "Howell Township", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Nov 20, 2025",
     "note": "6-month moratorium on data center development",
     "lat": 42.61, "lon": -83.93, "expires": "2026-05-20", "as_of": "2026-08-13",
     "source": "https://www.fractracker.org/2026/01/howell-township-data-center-win"},
    {"locality": "Northville", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Jan 6, 2026",
     "note": "12-month moratorium on data center development",
     "lat": 42.43, "lon": -83.48, "expires": "2027-01-06", "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "Pontiac", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Jan 21, 2026",
     "note": "6-month moratorium on data center development",
     "lat": 42.64, "lon": -83.29, "expires": "2026-07-21", "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "Saginaw", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Jan 13, 2026",
     "note": "6-month moratorium on data center development",
     "lat": 43.42, "lon": -83.95, "expires": "2026-07-13", "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "Sterling Heights", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Feb 4, 2026",
     "note": "1-year moratorium on data center development",
     "lat": 42.58, "lon": -83.03, "expires": "2027-02-04", "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "South Lyon", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Feb 10, 2026",
     "note": "12-month moratorium on data center development",
     "lat": 42.46, "lon": -83.65, "expires": "2027-02-10", "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "Taylor", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Jan 2026",
     "note": "1-year moratorium on data center development",
     "lat": 42.24, "lon": -83.27, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "Tyrone Township", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Dec 2, 2025",
     "note": "6-month moratorium on data center development",
     "lat": 42.66, "lon": -83.86, "expires": "2026-06-01", "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "Dundee Township", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Oct 2025",
     "note": "90-day moratorium with extension on data center development",
     "lat": 41.96, "lon": -83.66, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "Sylvan Township", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Jan 22, 2026",
     "note": "6-month moratorium on data center development",
     "lat": 42.32, "lon": -84.08, "expires": "2026-07-22", "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "Lodi Township", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Feb 3, 2026",
     "note": "180-day moratorium on data center development",
     "lat": 42.23, "lon": -83.86, "expires": "2026-08-02", "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "York Township", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Feb 12, 2026",
     "note": "6-month moratorium on data center development",
     "lat": 42.10, "lon": -83.71, "expires": "2026-08-12", "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "Hayes Township", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Feb 10, 2026",
     "note": "180-day moratorium on data center development",
     "lat": 42.92, "lon": -83.04, "expires": "2026-08-09", "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "Springfield Township", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Dec 2025",
     "note": "180-day moratorium on data center development",
     "lat": 42.76, "lon": -83.48, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "Village of Romeo", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Jan 26, 2026",
     "note": "Moratorium on data center development",
     "lat": 42.80, "lon": -83.01, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "Solon Township", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Feb 2026",
     "note": "6-month moratorium on data center development",
     "lat": 43.61, "lon": -85.58, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "Big Rapids Township", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Feb 23, 2026",
     "note": "1-year moratorium on data center development",
     "lat": 43.70, "lon": -85.48, "expires": "2027-02-23", "as_of": "2026-08-13",
     "source": "https://www.wkar.org/wkar-news/2026-02-27/michigan-data-center-tracker-moratoria-legislation-and-grid-impact"},
    {"locality": "Lenox Township", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "Feb 2, 2026",
     "note": "4-month moratorium with extension option",
     "lat": 42.74, "lon": -82.94, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.lenox-mi.gov/m/newsflash/home/detail/240"},
    # ── Batch 3 — Kentucky ────────────────────────────────────────────────
    {"locality": "Bell County", "state": "KY", "level": "Local",
     "status": "Enacted", "when": "Jul 2, 2026",
     "note": "2-year moratorium, unanimous. Halts Murray Industries' hyperscale "
             "project on former coal mining land along Bell-Knox county line. "
             "Murray had already begun clearing land before the vote",
     "lat": 36.72, "lon": -83.67, "expires": "2028-07-02", "as_of": "2026-08-13",
     "source": "https://kentuckylantern.com/2026/08/04/bell-county-passed-a-data-center-moratorium-resident-worry-that-work-continues/"},
    {"locality": "Daviess County", "state": "KY", "level": "Local",
     "status": "Enacted", "when": "May 28, 2026",
     "note": "12-month moratorium, unanimous. Triggered by hyperscale data "
             "center planned at idled aluminum mill in neighboring Hancock County",
     "lat": 37.77, "lon": -87.11, "expires": "2027-05-28", "as_of": "2026-08-13",
     "source": "https://www.14news.com/2026/05/29/daviess-co-fiscal-court-approves-moratorium-data-center-applications/"},
    {"locality": "Cave City", "state": "KY", "level": "Local",
     "status": "Enacted", "when": "May 20, 2026",
     "note": "12-month moratorium, 4-1. Under legal challenge — Kentucky "
             "Industrial Alliance (proposed 1.2 GW 'Cave Point Commerce Center' "
             "on ~600 acres) filed suit Jun 8",
     "lat": 37.14, "lon": -85.96, "expires": "2027-05-20", "as_of": "2026-08-13",
     "source": "https://bgdailynews.com/2026/05/24/cave-city-looks-ahead-after-data-center-moratorium/"},
    {"locality": "Lexington (Fayette County)", "state": "KY", "level": "Local",
     "status": "Enacted", "when": "Jun 9, 2026",
     "note": "Moratorium on permits, development plans, and zone changes, "
             "unanimous. Expires Oct 31; Planning Division drafting Zoning "
             "Ordinance Text Amendment proposals",
     "lat": 38.04, "lon": -84.50, "expires": "2026-10-31", "as_of": "2026-08-13",
     "source": "https://www.lex18.com/news/covering-kentucky/lexington-city-council-passes-moratorium-on-data-center-development"},
    {"locality": "Allen County", "state": "KY", "level": "Local",
     "status": "Enacted", "when": "Jun 10, 2026",
     "note": "2-year moratorium (Ord. 26-03). Proactive — Judge-Executive "
             "observed 'headaches' in nearby Simpson County with hyperscale "
             "proposal",
     "lat": 36.75, "lon": -86.19, "expires": "2028-06-10", "as_of": "2026-08-13",
     "source": "https://www.wnky.com/allen-county-pauses-data-center-development-for-two-years/"},
    {"locality": "Mercer County", "state": "KY", "level": "Local",
     "status": "Enacted", "when": "Aug 2026",
     "note": "1-year moratorium in unincorporated areas, unanimous. Does NOT "
             "apply to City of Burgin, which is pursuing annexation to "
             "accommodate a proposed hyperscale data center. Grassroots "
             "group 'We Are Mercer County' active",
     "lat": 37.81, "lon": -84.88, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.wkms.org/2026-08-12/a-kentucky-county-passes-a-data-center-moratorium-with-a-city-sized-hole"},
    {"locality": "Jessamine County", "state": "KY", "level": "Local",
     "status": "Enacted", "when": "Aug 4, 2026",
     "note": "12-month moratorium. Proactive — no data center development "
             "inquiries had been made in the county at time of vote",
     "lat": 37.87, "lon": -84.58, "expires": "2027-08-04", "as_of": "2026-08-13",
     "source": "https://fox56news.com/news/local/jessamine-county-approves-12-month-data-center-moratorium/"},
    # ── Batch 3 — Iowa ────────────────────────────────────────────────────
    {"locality": "Johnson County", "state": "IA", "level": "Local",
     "status": "Enacted", "when": "Nov 6, 2025",
     "note": "1-year moratorium in unincorporated areas, unanimous. Excludes "
             "Iowa City, North Liberty, Coralville. Water/electrical bill "
             "concerns",
     "lat": 41.67, "lon": -91.59, "expires": "2026-11-08", "as_of": "2026-08-13",
     "source": "https://cbs2iowa.com/news/local/johnson-county-imposes-moratorium-on-data-centers-to-protect-resources-and-assess-impacts"},
    {"locality": "Linn County", "state": "IA", "level": "Local",
     "status": "Enacted", "when": "Jul 1, 2026",
     "note": "18-month moratorium on EU-3 Large-Scale Data Center rezoning in "
             "unincorporated areas, 2-1. Can end early or extend",
     "lat": 42.08, "lon": -91.59, "expires": "2028-01-01", "as_of": "2026-08-13",
     "source": "https://corridorbusiness.com/linn-county-data-center-moratorium-approved-how-the-board-got-to-2-1-and-what-happens-next/"},
    {"locality": "Dubuque County", "state": "IA", "level": "Local",
     "status": "Enacted", "when": "May 26, 2026",
     "note": "12-month moratorium, 2-1. Originally proposed as 120 days, "
             "extended during meeting. Planning and Zoning Commission had "
             "unanimously recommended the pause",
     "lat": 42.48, "lon": -90.71, "expires": "2027-05-26", "as_of": "2026-08-13",
     "source": "https://www.kcrg.com/2026/05/26/dubuque-county-passes-12-month-moratorium-data-centers/"},
    {"locality": "Woodbury County", "state": "IA", "level": "Local",
     "status": "Enacted", "when": "Jun 23, 2026",
     "note": "12-month moratorium in unincorporated areas, 5-0. Does NOT affect "
             "Salix, which annexed ~900 acres that MidAmerican Energy confirmed "
             "is being considered for a data center",
     "lat": 42.39, "lon": -96.11, "expires": "2027-06-23", "as_of": "2026-08-13",
     "source": "https://www.ktiv.com/2026/06/23/woodbury-county-passes-moratorium-data-center-projects/"},
    {"locality": "Plymouth County", "state": "IA", "level": "Local",
     "status": "Enacted", "when": "Jun 16, 2026",
     "note": "1-year moratorium on data centers and industrial battery storage, "
             "4-0 (one absent). Revocable or extendable at any time",
     "lat": 42.86, "lon": -96.28, "expires": "2027-06-16", "as_of": "2026-08-13",
     "source": "https://www.ktiv.com/2026/06/17/plymouth-county-hits-pause-data-centers-with-1-year-moratorium/"},
    {"locality": "Sioux County", "state": "IA", "level": "Local",
     "status": "Enacted", "when": "Jun 16, 2026",
     "note": "1-year moratorium on data centers and battery storage in "
             "unincorporated areas. PathOne Data Centers considering "
             "redeveloping former Bison Renewable Energy property near Hull",
     "lat": 43.08, "lon": -96.18, "expires": "2027-06-16", "as_of": "2026-08-13",
     "source": "https://www.ktiv.com/2026/06/23/sioux-county-northwest-iowa-places-one-year-moratorium-data-centers/"},
    {"locality": "Ida County", "state": "IA", "level": "Local",
     "status": "Enacted", "when": "Jun 2026",
     "note": "Indefinite moratorium, unanimous. Supervisors want more "
             "information before allowing development",
     "lat": 42.39, "lon": -95.52, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.radioiowa.com/2026/07/13/ida-county-joins-list-of-iowa-counties-with-data-center-moratoriums/"},
    {"locality": "Madison County", "state": "IA", "level": "Local",
     "status": "Enacted", "when": "Jul 22, 2026",
     "note": "1-year moratorium, unanimous",
     "lat": 41.33, "lon": -94.02, "expires": "2027-07-22", "as_of": "2026-08-13",
     "source": "https://www.radioiowa.com/2026/07/08/eight-iowa-counties-have-moratoriums-on-data-center-development/"},
    {"locality": "Shelby County", "state": "IA", "level": "Local",
     "status": "Enacted", "when": "2026",
     "note": "Moratorium through Jul 2027 while permanent rules are developed",
     "lat": 41.77, "lon": -95.31, "expires": "2027-07-01", "as_of": "2026-08-13",
     "source": "https://www.radioiowa.com/2026/07/08/eight-iowa-counties-have-moratoriums-on-data-center-development/"},
    {"locality": "Clarke County", "state": "IA", "level": "Local",
     "status": "Enacted", "when": "2026",
     "note": "Temporary moratorium while permanent rules are developed",
     "lat": 41.03, "lon": -93.78, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.radioiowa.com/2026/07/08/eight-iowa-counties-have-moratoriums-on-data-center-development/"},
    # ── Batch 3 — Pennsylvania ────────────────────────────────────────────
    {"locality": "Olyphant", "state": "PA", "level": "Local",
     "status": "Enacted", "when": "2025",
     "note": "6-month moratorium on new data center development, 4-3. Triggered "
             "a wave of similar actions across Lackawanna, Luzerne, and Chester "
             "counties",
     "lat": 41.47, "lon": -75.60, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.thecentersquare.com/pennsylvania/article_06f92bfc-34c1-430c-9487-375bde5c9415.html"},
    {"locality": "East Whiteland Township", "state": "PA", "level": "Local",
     "status": "Enacted", "when": "Mar 2026",
     "note": "180-day moratorium — board declared parts of data center zoning "
             "'substantively invalid' and launched curative amendment. Developer "
             "Green Fig withdrew 1.7M sq ft application in May after sustained "
             "public opposition",
     "lat": 40.04, "lon": -75.55, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.foodandwaterwatch.org/2026/05/05/east-whiteland-pa-data-center-developer-withdraws-application-after-fierce-public-opposition/"},
    {"locality": "Pennsylvania", "state": "PA", "level": "State",
     "status": "Proposed", "when": "Jul 12, 2026",
     "note": "SB 1345 — would allow municipalities to impose 18-month "
             "moratoriums. Passed Senate Rules & Exec Nominations Committee "
             "13-4. Three competing state bills range from 180 days to 3 years. "
             "Not yet enacted",
     "lat": 40.27, "lon": -76.88, "expires": None, "as_of": "2026-08-13",
     "source": "https://broadbandbreakfast.com/pennsylvania-senate-advances-bill-allowing-18-month-data-center-moratoriums/"},
    # ── Batch 3 — Ohio ────────────────────────────────────────────────────
    {"locality": "Lordstown", "state": "OH", "level": "Local",
     "status": "Enacted", "when": "Jan 2026",
     "note": "180-day moratorium (converted from outright ban after lawsuit). "
             "Developer Bristolville 25 LLC sued over \\$3.6B, 1.65M sq ft "
             "project on former GM Lordstown Assembly site near OpenAI Stargate",
     "lat": 41.17, "lon": -80.87, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.vindy.com/news/local-news/2026/05/lordstown-officials-plan-to-re-up-180-day-moratorium-on-data-centers/"},
    {"locality": "Ravenna", "state": "OH", "level": "Local",
     "status": "Enacted", "when": "Apr 20, 2026",
     "note": "1-year moratorium, unanimous. Nearly 100 residents packed the "
             "special meeting. Resident's 4-minute speech against a proposed "
             "data center near UH Portage Medical Center went viral (250K+ "
             "views on X)",
     "lat": 41.16, "lon": -81.24, "expires": "2027-04-20", "as_of": "2026-08-13",
     "source": "https://www.thecooldown.com/green-tech/ravenna-ohio-residents-oppose-ai-data-centers/"},
    {"locality": "Boardman Township", "state": "OH", "level": "Local",
     "status": "Enacted", "when": "Apr 28, 2026",
     "note": "1-year moratorium, unanimous. Pause for zoning regulation "
             "development",
     "lat": 41.02, "lon": -80.66, "expires": "2027-04-28", "as_of": "2026-08-13",
     "source": "https://www.vindy.com/news/local-news/2026/05/boardman-oks-1-year-data-center-moratorium/"},
    {"locality": "Painesville Township", "state": "OH", "level": "Local",
     "status": "Enacted", "when": "May 2026",
     "note": "12-month moratorium on new data center permits, unanimous",
     "lat": 41.72, "lon": -81.25, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.thecooldown.com/green-business/painesville-township-ohio-data-center/"},
    {"locality": "Vienna Township", "state": "OH", "level": "Local",
     "status": "Enacted", "when": "Extended Aug 2026",
     "note": "Rolling moratorium — originally enacted 2025, extended 60 days "
             "through Oct 16 while zoning solutions including noise and power "
             "limits are developed. Bitdeer (Singapore-based) has plans in area",
     "lat": 41.23, "lon": -80.66, "expires": "2026-10-16", "as_of": "2026-08-13",
     "source": "https://www.tribtoday.com/news/local-news/2026/08/vienna-extends-data-center-moratorium/"},
    {"locality": "Weathersfield Township", "state": "OH", "level": "Local",
     "status": "Enacted", "when": "2026",
     "note": "6-month moratorium. Bitdeer plans a data center on Belmont Ave "
             "on land where an Ohio Edison power plant once operated",
     "lat": 41.13, "lon": -80.76, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.wkbn.com/news/local-news/weathersfield-news/weathersfield-township-trustees-place-moratorium-on-approving-data-center/"},
    {"locality": "Twinsburg", "state": "OH", "level": "Local",
     "status": "Enacted", "when": "2026",
     "note": "12-month moratorium on data center permits",
     "lat": 41.31, "lon": -81.44, "expires": None, "as_of": "2026-08-13",
     "source": "https://mytwinsburg.com/DocumentCenter/View/11167/2026-065-Establishing-Moratorium-for-Data-Centers"},
    {"locality": "South Bloomfield", "state": "OH", "level": "Local",
     "status": "Enacted", "when": "2026",
     "note": "Preventive ban — eliminated all industrial zoning preemptively "
             "to block data center applications. No developer had approached",
     "lat": 39.72, "lon": -82.87, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.statenews.org/section/the-ohio-newsroom/2026-02-26/ohio-towns-are-pushing-back-against-data-centers-to-varying-degrees-of-success"},
    {"locality": "Ohio (tax exemptions)", "state": "OH", "level": "State",
     "status": "Enacted", "when": "2025",
     "note": "Governor's moratorium on data center tax exemptions while Joint "
             "Data Center Committee holds hearings. Two last data centers "
             "received \\$42M in exemptions before the pause took effect",
     "lat": 40.42, "lon": -82.91, "expires": None, "as_of": "2026-08-13",
     "source": "https://signalcleveland.org/ohio-approves-last-data-center-exemption-before-moratorium/"},
    {"locality": "Ohio (ballot measure)", "state": "OH", "level": "State",
     "status": "Rejected", "when": "2026",
     "note": "Proposed constitutional amendment to ban data centers >25 MW "
             "failed to qualify — collected ~70,000 of 413,488 required "
             "signatures. Backers plan to try again for 2027 ballot",
     "lat": 40.42, "lon": -82.91, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.statenews.org/government-politics/2026-03-26/proposed-amendment-to-ban-huge-data-centers-in-ohio-can-move-to-next-step"},
    # ── Batch 3 — Wisconsin ───────────────────────────────────────────────
    {"locality": "Madison", "state": "WI", "level": "Local",
     "status": "Enacted", "when": "Jan 13, 2026",
     "note": "Up to 1-year moratorium on zoning for data centers >10,000 sq ft, "
             "unanimous. Evaluating electricity, water, land use, and community "
             "benefit impacts",
     "lat": 43.07, "lon": -89.40, "expires": "2027-01-13", "as_of": "2026-08-13",
     "source": "https://www.cityofmadison.com/dpced/about/temporary-data-center-moratorium"},
    {"locality": "Town of Cassville", "state": "WI", "level": "Local",
     "status": "Enacted", "when": "Apr 2026",
     "note": "2-year moratorium, unanimous. 36 sq mi in Grant County. "
             "Residents mobilized against a \\$1B proposed project",
     "lat": 42.72, "lon": -90.98, "expires": None, "as_of": "2026-08-13",
     "source": "https://dailyreporter.com/2026/06/05/wisconsin-counties-impose-moratoriums-on-hyperscale-data-centers/"},
    {"locality": "Manitowoc County", "state": "WI", "level": "Local",
     "status": "Enacted", "when": "Apr 2026",
     "note": "18-month moratorium, unanimous. Towns of Two Creeks, Two Rivers, "
             "and Mishicot requested the pause after a developer approached "
             "property owners. Farmland-loss concerns",
     "lat": 44.10, "lon": -87.66, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.wpr.org/news/manitowoc-county-board-approves-18-month-data-center-moratorium"},
    {"locality": "Dane County", "state": "WI", "level": "Local",
     "status": "Enacted", "when": "Jun 4, 2026",
     "note": "18-month moratorium on hyperscale data centers in county zoning "
             "areas. Advisory committee to study benefits and pitfalls",
     "lat": 43.07, "lon": -89.42, "expires": "2027-12-04", "as_of": "2026-08-13",
     "source": "https://isthmus.com/news/news/dane-county-board-approves-data-center-moratorium/"},
    {"locality": "Village of Wrightstown", "state": "WI", "level": "Local",
     "status": "Enacted", "when": "Jun 16, 2026",
     "note": "1-year moratorium, unanimous. Cloverleaf Infrastructure proposed "
             "~1 GW AI data center in region. Aug 2026 advisory referendum: "
             "87%% voted village should NOT authorize public improvements for "
             "large data centers",
     "lat": 44.33, "lon": -88.16, "expires": "2027-06-16", "as_of": "2026-08-13",
     "source": "https://www.wearegreenbay.com/news/local-news/wrightstown-places-moratorium-on-data-centers/"},
    {"locality": "Superior", "state": "WI", "level": "Local",
     "status": "Enacted", "when": "Jun 17, 2026",
     "note": "1-year moratorium, unanimous. City lacks zoning definitions for "
             "data center sizes. Planning commission reviewing zoning and "
             "infrastructure recommendations",
     "lat": 46.72, "lon": -92.10, "expires": "2027-06-17", "as_of": "2026-08-13",
     "source": "https://www.wpr.org/news/superior-joins-growing-number-of-wisconsin-communities-to-pass-data-center-moratorium"},
    {"locality": "Wisconsin", "state": "WI", "level": "State",
     "status": "Proposed", "when": "Feb 26, 2026",
     "note": "SB 1061 — would halt operations at existing data centers until "
             "legislature enacts protections. Would ban shifting energy/water "
             "costs onto residential customers. Not yet voted on",
     "lat": 43.07, "lon": -89.40, "expires": None, "as_of": "2026-08-13",
     "source": "https://docs.legis.wisconsin.gov/document/proposaltext/2025/REG/SB1061,2,5"},
    # ── Batch 3 — Illinois ────────────────────────────────────────────────
    {"locality": "Aurora", "state": "IL", "level": "Local",
     "status": "Enacted", "when": "Sep 25, 2025",
     "note": "180-day moratorium, 10-1. Expired Mar 24, 2026 and replaced by "
             "permanent regulations: noise limits (56/46 dB day/evening), water "
             "standards, energy efficiency, annual reporting. 10 existing DCs",
     "lat": 41.76, "lon": -88.32, "expires": "2026-03-24", "as_of": "2026-08-13",
     "source": "https://abc7chicago.com/post/aurora-city-council-consider-temporary-moratorium-put-pause-development-new-data-centers/17882682/"},
    {"locality": "Champaign County", "state": "IL", "level": "Local",
     "status": "Enacted", "when": "Apr 23, 2026",
     "note": "12-month moratorium on data centers >=10,000 sq ft on "
             "unincorporated land. Board reversed committee's 9-month "
             "recommendation after hearing from dozens of residents. 100+ "
             "attendees. Task force created",
     "lat": 40.14, "lon": -88.20, "expires": "2027-04-23", "as_of": "2026-08-13",
     "source": "https://www.wsiu.org/state-of-illinois/2026-04-24/champaign-county-board-approves-1-year-data-center-moratorium"},
    {"locality": "Normal", "state": "IL", "level": "Local",
     "status": "Enacted", "when": "May 19, 2026",
     "note": "6-month moratorium through Nov 30, unanimous. Pause while leaders "
             "develop regulations",
     "lat": 40.51, "lon": -88.99, "expires": "2026-11-30", "as_of": "2026-08-13",
     "source": "https://www.25newsnow.com/2026/05/19/data-center-pauses-considered-normal-bloomington/"},
    {"locality": "Bloomington", "state": "IL", "level": "Local",
     "status": "Enacted", "when": "May 26, 2026",
     "note": "6-month moratorium on facilities >5 MW, unanimous",
     "lat": 40.48, "lon": -88.99, "expires": "2026-11-26", "as_of": "2026-08-13",
     "source": "https://www.wglt.org/local-news/2026-05-26/bloomington-approves-6-month-moratorium-on-data-centers"},
    {"locality": "Lake County", "state": "IL", "level": "Local",
     "status": "Proposed", "when": "Jun 9, 2026",
     "note": "8-month moratorium proposed; immediate 120-day administrative "
             "deferral enacted. First Chicago-area county to pursue a pause. "
             "Directed zoning board to hold hearing on code changes",
     "lat": 42.35, "lon": -87.86, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.dailyherald.com/20260609/business-openings/taking-this-issue-extremely-seriously-lake-county-pursues-data-center-moratorium/"},
    {"locality": "Illinois (tax incentives)", "state": "IL", "level": "State",
     "status": "Enacted", "when": "Jul 1, 2026",
     "note": "Governor Pritzker paused Data Center Investment Program for 2 "
             "years. Existing incentive agreements honored. Legislature had "
             "adjourned without passing the POWER Act (SB4016/HB5513)",
     "lat": 39.80, "lon": -89.65, "expires": "2028-07-01", "as_of": "2026-08-13",
     "source": "https://gov-pritzker-newsroom.prezly.com/gov-pritzker-pauses-new-data-center-tax-incentives"},
    # ── Batch 4 — Indiana ─────────────────────────────────────────────────
    {"locality": "Dearborn County", "state": "IN", "level": "Local",
     "status": "Enacted", "when": "Feb 25, 2026",
     "note": "Up to 1-year moratorium on rezoning for data centers, commercial "
             "solar, and battery storage. 1,700+ petition signatures. No data "
             "center applications had been submitted at the time",
     "lat": 39.15, "lon": -84.97, "expires": "2027-02-25", "as_of": "2026-08-13",
     "source": "https://www.wvxu.org/environment/2026-02-25/dearborn-county-moratorium-solar-farms-data-center"},
    {"locality": "Putnam County", "state": "IN", "level": "Local",
     "status": "Enacted", "when": "Nov 17, 2025",
     "note": "1-year moratorium on data centers, solar, wind, and SMRs in "
             "unincorporated areas, 2-1. ~100 residents packed the meeting. "
             "EnergyRe subsequently withdrew a 150 MW solar farm proposal",
     "lat": 39.66, "lon": -86.86, "expires": "2026-11-17", "as_of": "2026-08-13",
     "source": "https://www.giant.fm/putnam-county/news/local-news/putnam-county-commissioners-vote-in-favor-of-moratorium-on-solar-farms/"},
    {"locality": "White County", "state": "IN", "level": "Local",
     "status": "Enacted", "when": "Oct 20, 2025",
     "note": "Temporary moratorium on data centers. Prompted by a proposed "
             "project near Wolcott; residents cited water availability and "
             "transparency concerns",
     "lat": 40.75, "lon": -86.86, "expires": None, "as_of": "2026-08-13",
     "source": "https://dailyjournal.net/2025/11/24/3-counties-put-moratoriums-on-data-center-projects/"},
    {"locality": "Pulaski County", "state": "IN", "level": "Local",
     "status": "Enacted", "when": "Feb 2, 2026",
     "note": "12-month moratorium, APC recommended 5-0. Preemptive — no "
             "proposals submitted. County developing ordinance with setback, "
             "power, and water provisions. Extension reviewed Jul 2026",
     "lat": 41.05, "lon": -86.70, "expires": "2027-02-02", "as_of": "2026-08-13",
     "source": "https://www.abc57.com/news/pulaski-county-commissioners-speak-on-data-center-moratorium"},
    {"locality": "Fulton County", "state": "IN", "level": "Local",
     "status": "Enacted", "when": "Mar 3, 2026",
     "note": "1-year moratorium, 2-1. Triggered by proposed 500 MW / 300-acre "
             "Decennial Group campus. Data center study committee to examine "
             "economic and environmental impacts",
     "lat": 41.07, "lon": -86.26, "expires": "2027-03-03", "as_of": "2026-08-13",
     "source": "https://www.wndu.com/2026/03/03/fulton-county-commissioners-approve-one-year-moratorium-data-center-construction/"},
    {"locality": "Miami County", "state": "IN", "level": "Local",
     "status": "Enacted", "when": "May 4, 2026",
     "note": "Moratorium on acceptance, processing, and approval of all data "
             "center applications and permits. Permanent zoning ordinance in "
             "development — public hearing scheduled Jul 20",
     "lat": 40.76, "lon": -86.05, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.miamicountyin.gov/910/Proposed-Data-Center-Ordinance-Moratoriu"},
    {"locality": "New Albany", "state": "IN", "level": "Local",
     "status": "Enacted", "when": "Jul 16, 2026",
     "note": "Up to 1-year moratorium on facilities/campuses >100,000 sq ft, "
             "unanimous. Study of infrastructure, utility costs, environmental "
             "effects, and neighborhood character impacts",
     "lat": 38.29, "lon": -85.82, "expires": "2027-07-16", "as_of": "2026-08-13",
     "source": "https://www.newsandtribune.com/indiana/city-council-pauses-data-center-development-in-new-albany-for-1-year/article_dc3733a3-b9a5-4197-b780-9ffd5035aa89.html"},
    # ── Batch 4 — Washington ──────────────────────────────────────────────
    {"locality": "Federal Way", "state": "WA", "level": "Local",
     "status": "Enacted", "when": "Jul 7, 2026",
     "note": "12-month moratorium, unanimous. Studying impact on former "
             "Weyerhaeuser campus. Public hearing set Sep 1",
     "lat": 47.32, "lon": -122.31, "expires": "2027-07-07", "as_of": "2026-08-13",
     "source": "https://www.rentonreporter.com/2026/07/08/federal-way-passes-1-year-moratorium-on-data-centers/"},
    {"locality": "Burien", "state": "WA", "level": "Local",
     "status": "Enacted", "when": "Jun 29, 2026",
     "note": "12-month emergency moratorium, unanimous, effective immediately",
     "lat": 47.47, "lon": -122.35, "expires": "2027-06-29", "as_of": "2026-08-13",
     "source": "https://b-townblog.com/burien-city-council-approves-one-year-moratorium-on-new-data-centers-hears-concerns-over-nera-zoning-immigration-arrests-school-relocation-more/"},
    {"locality": "Marysville", "state": "WA", "level": "Local",
     "status": "Enacted", "when": "Jul 2026",
     "note": "6-month moratorium on buildings/facilities whose principal use is "
             "data management/transmission, unanimous. Mayor urged surrounding "
             "counties to follow suit",
     "lat": 48.05, "lon": -122.18, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.heraldnet.com/2026/07/15/marysville-initiates-6-month-moratorium-on-data-centers/"},
    {"locality": "Skagit County", "state": "WA", "level": "Local",
     "status": "Enacted", "when": "Jun 1, 2026",
     "note": "6-month moratorium in rural/unincorporated areas on data centers "
             ">2,000 sq ft or >2 MW. Planning Commission advancing code changes "
             "to make it permanent. Farmland and water protection",
     "lat": 48.47, "lon": -121.84, "expires": "2026-12-01", "as_of": "2026-08-13",
     "source": "https://www.skagitcounty.net/Departments/Home/press/060126.htm"},
    {"locality": "Pasco", "state": "WA", "level": "Local",
     "status": "Enacted", "when": "Jul 2026",
     "note": "6-month moratorium, 6-0. Extendable if officials don't have "
             "satisfactory answers. Developing data-center-specific land-use "
             "regulations",
     "lat": 46.24, "lon": -119.10, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.datacenterdynamics.com/en/news/council-in-pasco-washington-unanimously-approves-six-month-data-center-moratorium/"},
    {"locality": "Cle Elum", "state": "WA", "level": "Local",
     "status": "Enacted", "when": "Jul 31, 2026",
     "note": "6-month moratorium, unanimous. Prompted by Blue Fern Development's "
             "20 MW / 100,000 sq ft plan within Bullfrog Flats community near "
             "I-90. Site may be exempt via preexisting development agreement",
     "lat": 47.19, "lon": -120.94, "expires": "2027-01-31", "as_of": "2026-08-13",
     "source": "https://www.dailyrecordnews.com/news/cle-elum-calls-timeout-on-development-applications-for-data-centers/article_43b63382-e7de-48da-9816-e760c936c24a.html"},
    {"locality": "Renton", "state": "WA", "level": "Local",
     "status": "Proposed", "when": "Jun 15, 2026",
     "note": "City council set AI data center moratorium in motion; process "
             "initiated but may not be finalized",
     "lat": 47.48, "lon": -122.22, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.rentonreporter.com/2026/06/15/renton-city-council-sets-ai-data-center-ban-in-motion/"},
    {"locality": "Kittitas County", "state": "WA", "level": "Local",
     "status": "Proposed", "when": "Aug 2026",
     "note": "Commissioners reviewing proposed emergency 6-month moratorium. "
             "Follows Cle Elum ban. Concerns: energy, water, transportation, "
             "noise, lighting, agricultural compatibility",
     "lat": 47.12, "lon": -120.72, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.dailyrecordnews.com/news/kittitas-county-commissioners-to-look-at-data-center-ban/article_e455846e-e6d5-462e-91bb-03856c76cec9.html"},
    # ── Batch 4 — Arizona & Oregon ────────────────────────────────────────
    {"locality": "Arizona (tax incentives)", "state": "AZ", "level": "State",
     "status": "Enacted", "when": "Jul 1, 2026",
     "note": "HB 4168 — 3-year moratorium on new data center sales tax "
             "exemption applications, signed Jun 13. Saves ~\\$57M. Developers "
             "submitted 113 applications in the 2 weeks before the pause "
             "(nearly as many as in the previous 13 years combined)",
     "lat": 34.05, "lon": -111.09, "expires": "2029-06-30", "as_of": "2026-08-13",
     "source": "https://news.bloombergtax.com/daily-tax-report-state/arizona-data-center-tax-incentive-pause-signed-by-governor-hobbs"},
    {"locality": "Pima County", "state": "AZ", "level": "Local",
     "status": "Proposed", "when": "Aug 11, 2026",
     "note": "Board voted 3-2 to direct staff to draft 120-day moratorium on "
             "data center approvals. Prompted by opposition to 'Project Blue'. "
             "Formal approval still needed. Permanent ordinance expected fall 2026",
     "lat": 32.22, "lon": -110.97, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.tucsonsentinel.com/local/report/081126_pima_data_moratorium/pima-county-moves-forward-possible-data-center-moratorium"},
    {"locality": "Oregon (enterprise zone tax)", "state": "OR", "level": "State",
     "status": "Enacted", "when": "Jun 5, 2026",
     "note": "HB 4084 — makes new data centers ineligible for Enterprise Zone "
             "property tax breaks until 90 days after the 2027 session adjourns. "
             "Separate from the proposed 3-year construction moratorium. Oregon "
             "DC tax breaks cost ~\\$450M/year",
     "lat": 43.80, "lon": -120.55, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.dwt.com/blogs/energy--environmental-law-blog/2026/06/oregon-data-center-tax-break-moratorium"},
    # ── Batch 4 — Virginia ────────────────────────────────────────────────
    {"locality": "Chesapeake", "state": "VA", "level": "Local",
     "status": "Enacted", "when": "Jul 2026",
     "note": "8-month pause on data center applications. Council had previously "
             "rejected a 350,000 sq ft project in Jun 2025. Planning commission "
             "drafting zoning amendments for case-by-case review",
     "lat": 36.77, "lon": -76.24, "expires": None, "as_of": "2026-08-13",
     "source": "https://virginiabusiness.com/chesapeake-approves-8-month-pause-on-data-center-applications/"},
    {"locality": "Front Royal", "state": "VA", "level": "Local",
     "status": "Enacted", "when": "Jul 6, 2026",
     "note": "90-day moratorium on land-use applications for data centers, 6-0. "
             "Planning Commission drafting language to prohibit data centers in "
             "every town zoning district",
     "lat": 38.92, "lon": -78.19, "expires": "2026-10-04", "as_of": "2026-08-13",
     "source": "https://www.nvdaily.com/nvdaily/council-oks-moratorium-on-data-center-applications/article_8bbfc9ce-d84e-5dd8-a4be-e8f9ee95cc94.html"},
    {"locality": "Suffolk", "state": "VA", "level": "Local",
     "status": "Proposed", "when": "Jun 17, 2026",
     "note": "Council directed Planning Commission to draft UDO amendment "
             "prohibiting data centers in all zoning districts. Applications "
             "not being considered during drafting, but formal enactment pending",
     "lat": 36.73, "lon": -76.58, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.whro.org/local-government/2026-05-11/suffolk-working-on-data-center-regulations"},
    # ── Batch 4 — Maryland ────────────────────────────────────────────────
    {"locality": "Harford County", "state": "MD", "level": "Local",
     "status": "Enacted", "when": "Jun 10, 2026",
     "note": "Permanent ban — first MD county to permanently ban data centers, "
             "unanimous. A single hyperscale facility could double the county's "
             "residential electricity demand. Legal challenges anticipated",
     "lat": 39.54, "lon": -76.30, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.baltimoresun.com/2026/06/10/harford-council-passes-ban-on-data-centers/"},
    {"locality": "Howard County", "state": "MD", "level": "Local",
     "status": "Enacted", "when": "Jun 1, 2026",
     "note": "17-month moratorium (S.M.A.R.T. Act), unanimous. Expires Nov 2 "
             "2027 or when zoning amendment passes. Task force of up to 11 "
             "appointees studying impacts. Existing zoning dates to 1993",
     "lat": 39.25, "lon": -76.93, "expires": "2027-11-02", "as_of": "2026-08-13",
     "source": "https://ccanactionfund.org/howard-county-approves-data-center-moratorium-and-task-force-legislation/"},
    {"locality": "Carroll County", "state": "MD", "level": "Local",
     "status": "Enacted", "when": "Feb 19, 2026",
     "note": "12-month moratorium to study economic and environmental impacts "
             "and propose regulations",
     "lat": 39.56, "lon": -76.97, "expires": "2027-02-19", "as_of": "2026-08-13",
     "source": "https://www.baltimoresun.com/2026/05/08/carroll-data-centers-commissioners-research/"},
    {"locality": "Queen Anne's County", "state": "MD", "level": "Local",
     "status": "Enacted", "when": "Jul 29, 2026",
     "note": "12-month moratorium, effective immediately. Part of the Eastern "
             "Shore moratorium wave after the Federalsburg data center proposal",
     "lat": 39.08, "lon": -76.08, "expires": "2027-07-29", "as_of": "2026-08-13",
     "source": "https://qac.org/m/newsflash/home/detail/3243"},
    {"locality": "Caroline County", "state": "MD", "level": "Local",
     "status": "Enacted", "when": "Jul 2026",
     "note": "1-year moratorium in unincorporated areas. Part of the Eastern "
             "Shore moratorium wave",
     "lat": 38.87, "lon": -75.83, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.wboc.com/news/caroline-county-commissioners-approve-a-one-year-moratorium-on-new-data-centers/article_e2b4c188-c810-4704-a33a-d95e0e029f28.html"},
    {"locality": "Dorchester County", "state": "MD", "level": "Local",
     "status": "Enacted", "when": "Jun 2026",
     "note": "1-year moratorium. Part of the Eastern Shore moratorium cluster",
     "lat": 38.50, "lon": -76.05, "expires": None, "as_of": "2026-08-13",
     "source": "http://www.stardem.com/news/data_centers/dorchester-county-council-hopes-to-get-ahead-on-regulating-data-center-proposals/article_af7ff49c-f072-4e08-85e9-1cd10bf1ca33.html"},
    {"locality": "Talbot County", "state": "MD", "level": "Local",
     "status": "Proposed", "when": "Sep 8, 2026",
     "note": "1-year moratorium resolution introduced; public comment hearing "
             "scheduled Sep 8. Not yet enacted",
     "lat": 38.75, "lon": -76.17, "expires": None, "as_of": "2026-08-13",
     "source": "https://www.stardem.com/news/local_news/talbot-county-council-to-consider-1-year-data-center-moratorium/article_291971b2-d964-40c8-a533-e9982c8c234f.html"},
    # ── Batch 4 — North Carolina ──────────────────────────────────────────
    {"locality": "Asheville", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Jun 17, 2026",
     "note": "1-year moratorium covering all data centers regardless of size. "
             "City drafting zoning laws. Intensive impacts on local electric "
             "and water utilities, noise, and heat",
     "lat": 35.60, "lon": -82.55, "expires": "2027-06-17", "as_of": "2026-08-13",
     "source": "https://mountainx.com/news/local-government/council-approves-one-year-moratorium-on-data-centers/"},
    {"locality": "Wendell", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "2026",
     "note": "Moratorium through Dec 31, 2026. Preemptive — no data center "
             "applications filed. Pause for leaders to learn about impacts",
     "lat": 35.78, "lon": -78.37, "expires": "2026-12-31", "as_of": "2026-08-13",
     "source": "https://www.wral.com/news/local/central-north-carolina-data-center-plans-april-2026/"},
    # ── Batch 4 — South Carolina ──────────────────────────────────────────
    {"locality": "Spartanburg County", "state": "SC", "level": "Local",
     "status": "Enacted", "when": "Jun 22, 2026",
     "note": "1-year moratorium (extendable by council vote), no dissent on "
             "first reading. Pending ordinance doctrine invoked to halt "
             "applications immediately. Exempts previously approved Kohler "
             "Plant site project",
     "lat": 34.95, "lon": -81.93, "expires": "2027-06-22", "as_of": "2026-08-13",
     "source": "https://www.foxcarolina.com/2026/06/22/spartanburg-county-votes-pause-data-center-applications-one-year/"},
    {"locality": "York County", "state": "SC", "level": "Local",
     "status": "Enacted", "when": "Jul 13, 2026",
     "note": "9-month moratorium in unincorporated areas, final reading. Does "
             "NOT affect QTS project near Lake Wylie (vested rights). Studies: "
             "rate-making, generators, geothermal/heat, noise",
     "lat": 34.99, "lon": -81.24, "expires": "2027-04-13", "as_of": "2026-08-13",
     "source": "https://www.foxcarolina.com/2026/06/22/spartanburg-county-votes-pause-data-center-applications-one-year/"},
]

# Statuses that are already final — an expiry date cannot change them.
_MORATORIUM_FINAL = ("Proposed", "Rejected", "Vetoed", "Rescinded")
EXPIRING_SOON_DAYS = 60


def moratorium_status(status, expires, today=None):
    """Effective status of a moratorium row, given its documented expiry.

    A tracker that shows a lapsed moratorium as "Enacted" is worse than no
    tracker: someone cites it at a hearing and the developer's counsel points
    out it ended a year ago. So "Expired" is derived here on every render
    rather than stored, and the daily site rebuild is what keeps it honest.

    Rows with no `expires` are left alone — an undocumented term is not
    evidence of expiry, and guessing one would reintroduce the same problem
    from the other direction. Those rows surface in the validator instead.

    Returns a dict: effective status, whether it lapsed, days remaining
    (negative once past), and an expiring-soon flag for the next
    EXPIRING_SOON_DAYS days.
    """
    out = {"status": status, "expired": False,
           "days_left": None, "expiring_soon": False}
    if not has_value(expires) or status in _MORATORIUM_FINAL:
        return out
    try:
        end = _dt.date.fromisoformat(str(expires))
    except ValueError:
        return out
    today = today or _dt.date.today()
    days = (end - today).days
    out["days_left"] = days
    if days < 0:
        out["expired"] = True
        out["status"] = "Expired"
    elif days <= EXPIRING_SOON_DAYS:
        out["expiring_soon"] = True
    return out


MORATORIUMS_DF = pd.DataFrame(
    MORATORIUMS,
    columns=["locality", "state", "level", "status", "when", "note",
             "lat", "lon", "expires", "as_of", "source"])
# Derived at import so every consumer sees the same effective status. The
# static site is rebuilt daily by CI, so these stay current without an edit.
_mora_status = MORATORIUMS_DF.apply(
    lambda r: moratorium_status(r["status"], r["expires"]), axis=1)
MORATORIUMS_DF["effective_status"] = [s["status"] for s in _mora_status]
MORATORIUMS_DF["expired"] = [s["expired"] for s in _mora_status]
MORATORIUMS_DF["days_left"] = [s["days_left"] for s in _mora_status]
MORATORIUMS_DF["expiring_soon"] = [s["expiring_soon"] for s in _mora_status]
MORATORIUMS_DF["verified"] = MORATORIUMS_DF["source"].map(has_value)

# Case study outcomes — what actually happened after a moratorium or major fight.
#
# These are labelled "precedents worth citing" in the Start here wizard, which
# makes them the highest-stakes text in the repo: a resident reads one out at a
# hearing. So every row carries `sources` (the reporting or the government's own
# page) and `as_of`, and says only what those sources say.
#
# All six were rewritten on 2026-08-04 after none survived verification. The
# prior versions asserted community wins that no source supports — a $2.5M
# recreation centre in Groton, a 25%-of-supply water cap in The Dalles,
# quarterly community reporting in Mesa — alongside a Cheyenne timeline that
# ran into the future. Anything not in a source below stays out, however good
# an organising story it would make. Where the real outcome is worse than the
# story (The Dalles), the row says so: a community that plans against a cap
# that does not exist is worse off than one that knows it has to win it.
MORATORIUM_OUTCOMES = [
    {
        "locality": "Groton", "state": "CT",
        "headline": "A one-year pause turned into a permanent size cap",
        "outcome": "Groton's Planning and Zoning Commission adopted a "
                   "one-year moratorium on data centers over 5,000 sq ft in "
                   "June 2022 — and spent that year writing rules rather than "
                   "letting it lapse. After a final public hearing in June "
                   "2023 the town adopted data center regulations, effective "
                   "that July, capping data center buildings at 12,500 sq ft. "
                   "Hyperscale campuses typically run 150,000–350,000 sq ft, "
                   "so the cap excludes them by size instead of by argument. "
                   "The moratorium was only the mechanism; the size cap is "
                   "what holds.",
        "category": "Permanent limits adopted",
        "as_of": "2026-08-04",
        "sources": [
            "https://theday.com/local-news/20220621/groton-approves-one-year-moratorium-on-large-scale-data-centers",
            "https://datacenters.ainowinstitute.org/local/",
        ],
    },
    {
        "locality": "Peculiar", "state": "MO",
        "headline": "The town deleted 'data center' from its zoning code",
        "outcome": "Peculiar had already cleared the way for Diode Ventures' "
                   "$1.5B Harper Road Technology Park by adding a 'data "
                   "center' definition to its light-industrial zoning code. "
                   "After hundreds of residents from Peculiar and neighbouring "
                   "Raymore turned out against it, the Board of Aldermen voted "
                   "unanimously in October 2024 to strike that definition back "
                   "out — blocking the project without ever passing a "
                   "moratorium. Removing a permitted use is a quieter tool "
                   "than a ban, and here it was a faster one.",
        "category": "Project blocked",
        "as_of": "2026-08-04",
        "sources": [
            "https://www.kshb.com/news/local-news/peculiar-reverses-zoning-for-data-center-after-cries-from-neighbors",
            "https://www.datacenterdynamics.com/en/news/peculiar-officials-in-missouri-remove-data-centers-from-ordinance-blocking-15bn-diode-project/",
        ],
    },
    {
        "locality": "Cheyenne", "state": "WY",
        "headline": "Council rejected a pause with a 3,200-acre expansion already moving",
        "outcome": "Microsoft announced a 3,200-acre expansion of its Cheyenne "
                   "campus in April 2026, and Wyoming DEQ approved permits for "
                   "30 gas-fired engines plus emergency generators. On May 27, "
                   "2026 the city council voted 8–1 against a 12-month "
                   "moratorium after three and a half hours of public comment "
                   "— supporters raising water and noise, opponents raising "
                   "jobs and tax base. The ratepayer question is being handled "
                   "through Black Hills Energy's Large Power Contract Service "
                   "tariff, under which Microsoft pays directly for the "
                   "infrastructure it needs, rather than through anything the "
                   "city negotiated. No community benefit agreement appears in "
                   "the reporting.",
        "category": "No protections",
        "as_of": "2026-08-04",
        "sources": [
            "https://wyofile.com/cheyenne-rejects-moratorium-on-data-centers/",
            "https://capcity.news/business-feature-2/2026/04/14/microsoft-plans-massive-3200-acre-expansion-of-cheyenne-data-centers/",
            "https://cowboystatedaily.com/2026/06/08/cheyenne-leaders-industry-officials-data-centers-could-lower-electricity-costs/",
        ],
    },
    {
        "locality": "Prince William County", "state": "VA",
        "headline": "Voters removed the board chair; the courts voided the rezoning",
        "outcome": "In 2022 a board majority led by Chair Ann Wheeler rezoned "
                   "more than 2,000 acres of farmland for the Prince William "
                   "Digital Gateway. On June 20, 2023 Wheeler lost the "
                   "Democratic primary to Deshundra Jefferson, who had "
                   "campaigned against large-scale data centers. The board "
                   "approved the rezoning 4–3 that December regardless — and "
                   "it was the courts, not the ballot box, that ended it: the "
                   "rezoning was voided on appeal and a developer withdrew, "
                   "effectively killing the project. Statewide, Virginia voter "
                   "support for new data centers fell from 69% in 2023 to 35%. "
                   "Elections changed who was in the room; litigation changed "
                   "the outcome.",
        "category": "Political shift",
        "as_of": "2026-08-04",
        "sources": [
            "https://www.nbcwashington.com/news/politics/decision-2023/prince-william-county-voters-back-data-center-opponents-in-primary/3372105",
            "https://www.wusa9.com/article/news/legal/judge-retracts-digital-gateway-prince-william-county/65-fb80c9ca-6c4a-4b03-a975-49c2fa19dc40",
            "https://www.tomshardware.com/tech-industry/virginia-voter-support-for-new-data-centers-collapses-to-35-percent",
        ],
    },
    {
        "locality": "The Dalles", "state": "OR",
        "headline": "Google funded the water system — and its share of the water kept climbing",
        "outcome": "Under a 2021 agreement Google paid roughly $28.5M toward "
                   "upgrades to The Dalles' water treatment and storage, "
                   "including an aquifer storage and recovery system it later "
                   "handed to the city, and bought and donated 3.88 million "
                   "gallons/day of water rights from a closed aluminium "
                   "smelter. What the deal did not include was a cap on "
                   "Google's own draw. When The Oregonian sued for the usage "
                   "records, the city spent 13 months fighting disclosure "
                   "before settling — and the records showed the campus using "
                   "about 29% of the city's water, rising to roughly 40% "
                   "(some 550 million gallons a year) by 2025. Infrastructure "
                   "money is not the same protection as a volume limit. This "
                   "is the case that shows the difference, and the reason to "
                   "put a cap in writing.",
        "category": "Mixed outcome",
        "as_of": "2026-08-04",
        "sources": [
            "https://www.thedalles.org/news_detail_T4_R207.php",
            "https://www.rcfp.org/dalles-google-oregonian-settlement/",
            "https://waterwatch.org/googles-water-use-is-soaring-in-the-dalles-records-show-with-two-more-data-centers-to-come-2/",
        ],
    },
    {
        "locality": "Mesa", "state": "AZ",
        "headline": "Zoning rules instead of a moratorium: setbacks, height caps, sound study",
        "outcome": "With 15 data centers built, approved or proposed on "
                   "roughly 1,500 acres in six years, Mesa's council "
                   "introduced zoning controls 6–0 and adopted them in July "
                   "2025. Data centers are now allowed only where the council "
                   "specifically authorises a Planned Area Development overlay "
                   "on industrial land, and each must sit at least 400 feet "
                   "from residential, stay under 60 feet tall, screen its "
                   "mechanical equipment, and submit a sound study. Water "
                   "cooling was argued in council — Councilwoman Jenn Duff "
                   "pushed to restrict it during drought — but did not make it "
                   "into the adopted rules. Worth reading as a list of what a "
                   "council will grant without a moratorium, and what it "
                   "won't.",
        "category": "Permanent limits adopted",
        "as_of": "2026-08-04",
        "sources": [
            "https://www.kjzz.org/business/2025-07-14/mesa-city-council-approves-new-data-center-zoning-rules",
            "https://www.12news.com/article/news/local/valley/new-data-center-regulations-approved-by-mesa-leaders-arizona/75-db14238c-61cd-4f89-9cfa-f7759baa5cf3",
            "https://www.themesatribune.com/news/mesa-council-to-vote-on-data-center-controls/article_95cfba83-0015-4c0e-aa8e-116cef4c8c6e.html",
        ],
    },
]


# --------------------------------------------------------------------------- #
# IDENTIFIED PROJECT TRACKER
#
# One row per identified data-center project, loaded from data/projects.json
# (a plain JSON file so leads can be edited and community-submitted without
# touching Python). Each row carries its own `source` + `as_of` and an
# append-only `events` log — the same per-row provenance discipline as the
# LOCAL_* and MORATORIUMS tables. Leads are mined into
# data/project_candidates.json by scripts/scan_project_candidates.py and
# promoted here BY HAND, because that human read is where source + as_of come
# from.
#
# Status is DERIVED (project_status), never stored: the stage a resident acts
# on — "Hearing scheduled", "Awaiting decision", "Approved", "Withdrawn" — is
# a function of today's date, so the daily CI rebuild keeps it honest without
# an edit. A hearing date that has passed stops reading "scheduled"; a project
# with a documented outcome reads that outcome. Same lesson as
# moratorium_status(): storing a stage means the page asserts it forever.
# --------------------------------------------------------------------------- #

PROJECTS_PATH = pathlib.Path(__file__).resolve().parent.parent / "data" / "projects.json"

_PROJECT_TERMINAL = ("approved", "denied", "withdrawn")
PROJECT_HEARING_SOON_DAYS = 45


def project_status(row, today=None):
    """Derive a project's current stage from its milestone dates + outcome.

    `row` is a mapping with keys announced / rezoning_filed / hearing_date /
    decided_date / outcome. Returns a dict: human `stage`, a machine `phase`
    key, whether it is `terminal`, `days_to_hearing` (None, or negative once
    past), a `hearing_soon` flag, and a plain-language `next_action` a resident
    can act on. Computed on every render, never stored — see the block comment.
    """
    today = today or _dt.date.today()
    out = {"stage": "Rumored", "phase": "rumored", "terminal": False,
           "days_to_hearing": None, "hearing_soon": False, "next_action": ""}

    def _date(v):
        if not has_value(v):
            return None
        try:
            return _dt.date.fromisoformat(str(v)[:10])
        except ValueError:
            return None

    outcome = str(row.get("outcome")).strip().lower() if has_value(row.get("outcome")) else ""
    if outcome in _PROJECT_TERMINAL:
        stage = {"approved": "Approved", "denied": "Denied",
                 "withdrawn": "Withdrawn"}[outcome]
        action = {
            "approved": "Approved — pivot from stopping it to a binding CBA: "
                        "enforceable caps on noise, water and cost, plus a "
                        "community benefit.",
            "denied": "Denied — watch for a re-filing or a scaled-down "
                      "resubmission; ask the clerk to add you to the "
                      "notification list.",
            "withdrawn": "Withdrawn — confirm it is dead in the record and "
                         "watch for the same site resurfacing under a new name "
                         "or LLC.",
        }[outcome]
        out.update(stage=stage, phase=outcome, terminal=True, next_action=action)
        return out

    hd = _date(row.get("hearing_date"))
    if hd is not None:
        days = (hd - today).days
        out["days_to_hearing"] = days
        if days >= 0:
            plural = "" if days == 1 else "s"
            out.update(stage="Hearing scheduled", phase="hearing",
                       hearing_soon=days <= PROJECT_HEARING_SOON_DAYS,
                       next_action=(f"Public hearing in {days} day{plural} "
                                    f"({hd.isoformat()}). Sign up to speak and "
                                    f"file written comment before then."))
            return out
        out.update(stage="Awaiting decision", phase="awaiting",
                   next_action=(f"Heard {hd.isoformat()}; decision pending. "
                                f"Call the board clerk for the vote date and "
                                f"get on the notification list."))
        return out

    if has_value(row.get("rezoning_filed")):
        out.update(stage="In review", phase="review",
                   next_action=("Application filed. Ask the planning office "
                                "for the hearing date and request formal "
                                "notice."))
        return out
    if has_value(row.get("announced")):
        out.update(stage="Proposed", phase="proposed",
                   next_action=("Early stage. File a public-records request "
                                "for the application and site plan."))
        return out
    out["next_action"] = ("Rumored only. Confirm with the planning office and "
                          "file a records request to pin down what is real.")
    return out


def _load_projects():
    """Project records from data/projects.json. [] if missing/unreadable."""
    try:
        payload = json.loads(PROJECTS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return payload.get("projects", [])


PROJECTS = _load_projects()
PROJECT_EVENTS = {p.get("id"): p.get("events", []) for p in PROJECTS}

_PROJECT_COLS = ["id", "name", "operator", "owner", "tenant", "filing_llc",
                 "locality", "state", "lat", "lon", "size_mw", "acres",
                 "announced", "rezoning_filed", "hearing_date", "decided_date",
                 "outcome", "note", "source", "as_of"]
PROJECTS_DF = pd.DataFrame(
    [{c: p.get(c) for c in _PROJECT_COLS} for p in PROJECTS],
    columns=_PROJECT_COLS)
# Derived at import so every consumer (site page, downloads, alerts) sees the
# same effective stage. The daily rebuild is what keeps it current.
_proj_status = [project_status(p) for p in PROJECTS]
PROJECTS_DF["stage"] = [s["stage"] for s in _proj_status]
PROJECTS_DF["phase"] = [s["phase"] for s in _proj_status]
PROJECTS_DF["terminal"] = [s["terminal"] for s in _proj_status]
PROJECTS_DF["days_to_hearing"] = [s["days_to_hearing"] for s in _proj_status]
PROJECTS_DF["hearing_soon"] = [s["hearing_soon"] for s in _proj_status]
PROJECTS_DF["next_action"] = [s["next_action"] for s in _proj_status]
PROJECTS_DF["verified"] = PROJECTS_DF["source"].map(has_value)

# Negotiation intel per operator — documented concessions won elsewhere plus
# a read on how the company negotiates. Keyed by OPERATORS_DF operator name;
# operators without a well-documented track record are simply absent (the
# brief/action pack skips the section). Feeds build_meeting_brief_data().
# Per-operator negotiation intel: documented concessions won elsewhere plus a
# read on how the company negotiates. Feeds the meeting brief and action pack,
# so a resident may say these out loud to the company's own representative —
# every concession therefore carries `sources`, and the `pattern` read is
# labelled as interpretation rather than fact.
#
# Rewritten 2026-08-05. Two entries were deleted outright rather than fixed:
# Google/Mesa ("voluntary noise retrofits and quarterly community reporting")
# and the entire Vantage entry ("$2.5M community recreation center"). Neither
# is supported by any source found, and Vantage's whole strategy read rested
# on that one claim. Operators with no documented track record are simply
# absent — the brief skips the section, which is the correct outcome.
COMPANY_CONCESSIONS = {
    "Google": {
        "pattern": (
            "Negotiates through PR-friendly commitments — water stewardship "
            "pledges, community grants — but its documented concessions came "
            "under permit leverage and records-transparency pressure, not "
            "goodwill. Shell LLCs and confidentiality are standard practice "
            "until approvals are locked, so forcing early disclosure of water "
            "and power demands is where the leverage is. (Strategy read, not "
            "a sourced fact.)"
        ),
        "concessions": [
            {"as_of": "2026-08-05", "where": "The Dalles, OR", "year": "2021-24",
             "what": "Paid ~$28.5M toward city water treatment and storage, "
                     "including an aquifer storage and recovery system later "
                     "transferred to the city, and donated 3.88M gallons/day "
                     "of purchased water rights. Note what is absent: no cap "
                     "on its own draw, which reached ~40% of city supply.",
             "sources": ["https://www.thedalles.org/news_detail_T4_R207.php"]},
            {"as_of": "2026-08-05", "where": "The Dalles, OR", "year": "2022",
             "what": "Dropped its fight to keep water-use records secret "
                     "after The Oregonian sued; the city had spent 13 months "
                     "resisting disclosure before settling.",
             "sources": ["https://www.rcfp.org/dalles-google-oregonian-settlement/"]},
        ],
    },
    "Meta": {
        "pattern": (
            "Runs a standardized siting playbook behind shell LLCs — in Los "
            "Lunas it arrived as 'Greater Kudu LLC' — and moves fast once "
            "incentives are locked. Its public water-restoration programme is "
            "leverage: it has been converted into agreement terms elsewhere, "
            "so ask for the terms, not the pledge. (Strategy read.)"
        ),
        "concessions": [
            {"as_of": "2026-08-05", "where": "Los Lunas, NM", "year": "2025",
             "what": "Village water/wastewater agreement with Greater Kudu "
                     "LLC guarantees up to 3M gallons/day but suspends supply "
                     "during a declared Stage 3 water emergency — a usable "
                     "template for drought-conditioned service.",
             "sources": ["https://www.news-bulletin.com/news/tax-break-water-deal-for-meta-data-center/article_d4ff8540-163d-4c73-8a17-a5ec65209c42.html"]},
            {"as_of": "2026-08-05", "where": "Rio Grande watershed", "year": "ongoing",
             "what": "Funds eight watershed restoration projects returning "
                     "~172M gallons/year. Restoration is not the same as "
                     "reduced local draw — treat it as additional, not as an "
                     "offset against your own supply.",
             "sources": ["https://datacenters.atmeta.com/2026/04/restoring-water-in-our-data-center-communities/"]},
            {"as_of": "2026-08-05", "where": "Data center communities", "year": "ongoing",
             "what": "Community Action Grants to schools and nonprofits near "
                     "campuses, administered via ChangeX. Table stakes, not a "
                     "substitute for a binding agreement.",
             "sources": ["https://datacenters.atmeta.com/community-action-grants/"]},
        ],
    },
    "Microsoft": {
        "pattern": (
            "The most willing of the hyperscalers to accept design and "
            "transparency conditions, and the one whose own published "
            "commitments give you the most to hold it to. Use its zero-water "
            "design as the floor of the ask: it has already built it, so "
            "'evaporative draw is unavoidable' is not available to a "
            "developer proposing otherwise. (Strategy read.)"
        ),
        "concessions": [
            {"as_of": "2026-08-05", "where": "New builds", "year": "2024",
             "what": "All datacenter designs from August 2024 use chip-level "
                     "closed-loop cooling consuming zero water, avoiding "
                     ">125M litres/year per facility. Announced Dec 2024; "
                     "sites online from late 2027.",
             "sources": ["https://www.microsoft.com/en-us/microsoft-cloud/blog/2024/12/09/sustainable-by-design-next-generation-datacenters-consume-zero-water-for-cooling/"]},
            {"as_of": "2026-08-05", "where": "Quincy WA / San Antonio TX", "year": "ongoing",
             "what": "Runs cooling largely on recycled, reused or non-potable "
                     "water — 74% in Quincy, 79% in San Antonio — rather than "
                     "potable municipal supply.",
             "sources": ["https://blogs.microsoft.com/blog/2026/06/24/inside-microsofts-two-decade-push-to-cut-water-intensity-while-scaling-for-growth/"]},
        ],
    },
    "Amazon (AWS)": {
        "pattern": (
            "The hardest bargainer on taxes, and the one most likely to hold "
            "an abatement rather than pay. Where communities have extracted "
            "terms, it has been through payment-in-lieu deals negotiated "
            "before approval — leverage sits entirely with whoever controls "
            "the next permit. (Strategy read.)"
        ),
        "concessions": [
            {"as_of": "2026-08-05", "where": "Morrow County, OR", "year": "2023",
             "what": "Agreed to pay ~$40M in fees over 15 years across five "
                     "new data centers, in exchange for enterprise-zone "
                     "abatements estimated at $1B. Read both halves of that "
                     "trade before citing it as a win.",
             "sources": ["https://www.opb.org/article/2023/05/19/amazon-data-center-oregon-morrow-county/"]},
        ],
    },
    "QTS": {
        "pattern": (
            "Blackstone-owned and growth-driven, so entitlement delay is a "
            "real cost and timeline pressure is genuine leverage. But Prince "
            "William is the cautionary case: proffers offered late in a "
            "contested rezoning were judged too late to evaluate, and the "
            "rezoning was later voided on appeal. Get proffers recorded as "
            "binding conditions early, or they are worth nothing. (Strategy "
            "read.)"
        ),
        "concessions": [
            {"as_of": "2026-08-05", "where": "Prince William County, VA", "year": "2023",
             "what": "Added proffers during the contested Digital Gateway "
                     "rezoning — additional public space and strengthened "
                     "power-line placement language — after 24 hours of "
                     "public comment. Staff and some supervisors said the "
                     "amendments came too late to assess; the rezoning was "
                     "voided on appeal in 2026 and the project died.",
             "sources": ["https://www.datacenterdynamics.com/en/news/prince-william-county-officials-vote-in-favor-of-pw-digital-gateway-data-center-rezoning-in-manassas-virginia/",
                         "https://virginiabusiness.com/prince-william-digital-gateway-data-center-project-officially-dies/"]},
        ],
    },
}

# What similar communities actually won — shown in the Start Here wizard's
# impact step so the CBA target reads as precedent, not aspiration.
# What comparable communities actually won. This is the *ask* — the number a
# resident carries into a negotiation — which makes it the highest-stakes list
# in the repo. Every row carries `sources` + `as_of`, and says only what those
# sources say.
#
# Rewritten 2026-08-05 after verification. The prior version claimed a
# $2.5M recreation centre in Groton and a 25%-of-supply water cap in The
# Dalles; neither exists. Both had propagated here from MORATORIUM_OUTCOMES,
# which is the lesson: an unsourced claim does not stay in one registry. If a
# win cannot be sourced, it does not belong on the list at all — demanding
# something because "Groton got it" when Groton didn't is how a campaign loses
# the room in one meeting.
CBA_BENCHMARKS = [
    {"community": "Loudoun County", "state": "VA", "company": "Multiple",
     "won": "Declined abatements and taxed data centers instead: the FY2027 "
            "budget puts them at roughly $1.3B — about 45% of all county tax "
            "revenue — on ~4% of commercial parcels. The benchmark for what a "
            "jurisdiction with market power can simply refuse to give away",
     "as_of": "2026-08-05",
     "sources": ["https://www.loudoun.gov/Faq.aspx?QID=1793"]},
    {"community": "Groton", "state": "CT", "company": "Multiple",
     "won": "A hard size cap, not a cheque: data center buildings limited to "
            "12,500 sq ft in the zoning adopted June 2023, after a one-year "
            "moratorium. Hyperscale campuses run 150,000–350,000 sq ft, so "
            "the cap excludes them by geometry rather than by argument",
     "as_of": "2026-08-05",
     "sources": ["https://theday.com/local-news/20220621/groton-approves-one-year-moratorium-on-large-scale-data-centers",
                 "https://datacenters.ainowinstitute.org/local/"]},
    {"community": "Los Lunas", "state": "NM", "company": "Meta",
     "won": "A water agreement with terms: the March 2025 village agreement "
            "with Greater Kudu LLC (Meta's filing entity) guarantees up to 3M "
            "gallons/day but suspends supply in a declared Stage 3 water "
            "emergency. Meta also funds eight Rio Grande watershed "
            "restoration projects, ~172M gallons/year",
     "as_of": "2026-08-05",
     "sources": ["https://datacenters.atmeta.com/2026/04/restoring-water-in-our-data-center-communities/",
                 "https://www.news-bulletin.com/news/tax-break-water-deal-for-meta-data-center/article_d4ff8540-163d-4c73-8a17-a5ec65209c42.html"]},
    {"community": "Morrow County", "state": "OR", "company": "Amazon (AWS)",
     "won": "Fees in lieu of taxes, negotiated in the open: ~$40M over 15 "
            "years across five new data centers in exchange for enterprise-"
            "zone abatements worth an estimated $1B (2023). Cited here as a "
            "benchmark of what a payment-in-lieu deal looks like — including "
            "how much is forgone to get it",
     "as_of": "2026-08-05",
     "sources": ["https://www.opb.org/article/2023/05/19/amazon-data-center-oregon-morrow-county/"]},
    {"community": "The Dalles", "state": "OR", "company": "Google",
     "won": "Infrastructure money, but no cap — the cautionary benchmark. "
            "Google paid ~$28.5M toward city water treatment and storage and "
            "donated 3.88M gallons/day of water rights, yet nothing limited "
            "its own draw, which reached ~40% of city supply by 2025. Ask for "
            "the volume limit in writing, not just the capital contribution",
     "as_of": "2026-08-05",
     "sources": ["https://www.thedalles.org/news_detail_T4_R207.php",
                 "https://waterwatch.org/googles-water-use-is-soaring-in-the-dalles-records-show-with-two-more-data-centers-to-come-2/"]},
]

# Digital-organizing playbook — platform-specific tips for the Start Here
# wizard's outreach step and the action pack PDF.
OUTREACH_TIPS = [
    {"platform": "Nextdoor",
     "tips": [
         "The highest-value platform for this fight — it is geofenced to "
         "actual neighbors and town officials often lurk there",
         "Lead with the household bill number, never ideology — "
         "flag-happy moderation removes anything that smells partisan",
         "Name a specific local landmark near the parcel; proximity is "
         "what makes people stop scrolling",
         "Ask neighbors to hit 'Thank' and comment a town name — both "
         "push the post into adjacent neighborhoods",
     ]},
    {"platform": "Ring Neighbors",
     "tips": [
         "Treat it as an alert channel, not a discussion forum — short, "
         "factual, safety-adjacent framing ('heavy truck traffic', "
         "'survey crews spotted') performs best",
         "No links allowed in most posts — tell people to reply for the "
         "fact sheet instead",
         "Great for early-stage rumors: ask if anyone has seen land "
         "clearing, water testing, or unmarked survey stakes",
     ]},
    {"platform": "Facebook",
     "tips": [
         "Create a dedicated group ('[Town] Residents for Responsible "
         "Development') so the fight has a home base the algorithm "
         "can't bury",
         "Post the fact sheet as an IMAGE — image posts outperform link "
         "posts roughly 3:1 and can't be link-throttled",
         "Create a Facebook Event for every hearing and invite the whole "
         "group; RSVP counts create social proof",
         "Go Live from public meetings — the replay reaches neighbors "
         "who couldn't attend, and officials behave differently on "
         "camera",
         "Ask admins of established town groups before posting; getting "
         "a mod to post it for you beats getting flagged",
     ]},
    {"platform": "WhatsApp / group texts",
     "tips": [
         "This is your turnout tool, not your persuasion tool — save it "
         "for the 48 hours before a hearing",
         "One captain per street or church/school group; forward the "
         "flyer image, the time, and a carpool offer",
     ]},
    {"platform": "Local subreddit / forums",
     "tips": [
         "Post the documents themselves (permit screenshots, deed "
         "records) — forums reward receipts over rhetoric",
         "Someone will demand sources; reply with the fact sheet's "
         "source list and you win the thread",
     ]},
]

# Health risks of data centers — six-panel module (health section of the
# Learn tab + downloadable infographic PDF). Format inspired by the
# Environmental Health Project's "Health Risks of Data Centers" infographic
# (see SOURCES["ehp_health"]); every fact carries its own SOURCES key.
# Colors are deep panel hues that read on both the dark app and white PDF.
HEALTH_RISKS = [
    {"key": "air", "title": "Air pollution", "icon": "🫁",
     "color": "#414A5C",
     "summary": "Fossil power plants and diesel backup generators serving "
                "data centers emit pollution linked to ~1,300 premature "
                "deaths a year by 2030.",
     "facts": [
         {"text": "UC Riverside & Caltech researchers project up to ~1,300 "
                  "premature deaths a year by 2030 from U.S. data-center air "
                  "pollution — that is a midpoint, with a published range of "
                  "940 to 1,590 — alongside roughly 600,000 asthma-symptom "
                  "cases, and a total public-health burden exceeding $20B in "
                  "2028. Quote the range rather than the midpoint: it is the "
                  "defensible version, and a point estimate invites an "
                  "argument about precision you do not need to have.",
          "src": "unpaid_toll"},
         {"text": "The pollution comes from two places: the fossil-fueled "
                  "power plants supplying the electricity and on-site diesel "
                  "backup generators emitting NOx and fine particulates "
                  "(PM2.5) — both linked to respiratory disease, "
                  "cardiovascular conditions, and cancer risk.",
          "src": "unpaid_toll"},
         {"text": "The burden lands unevenly: much of the health impact "
                  "falls on communities near the power plants that serve a "
                  "data center, which can sit hundreds of miles from the "
                  "facility itself.", "src": "unpaid_toll"},
     ],
     "ask": "Demand generator run-hour limits, Tier 4 (or battery) backup "
            "instead of legacy diesel, and an air-permit review with public "
            "comment before any approval."},
    {"key": "noise", "title": "Noise pollution", "icon": "🔊",
     "color": "#8C4A2F",
     "summary": "Cooling systems and generators produce a constant "
                "low-frequency hum linked to sleep disturbance, "
                "hypertension, and cardiovascular disease.",
     "facts": [
         {"text": "Data-center cooling systems and backup generators "
                  "produce a continuous low-frequency hum that travels "
                  "farther than ordinary sound and penetrates building "
                  "walls.", "src": "ehp_health"},
         {"text": "The WHO links chronic environmental noise to sleep "
                  "disturbance, cardiovascular and metabolic disease, and "
                  "cognitive impairment — in Europe, environmental noise "
                  "contributes to an estimated 48,000 new heart-disease "
                  "cases and 12,000 premature deaths every year.",
          "src": "eea_noise"},
         {"text": "WHO night-noise recommendations sit around 40-45 dB — "
                  "the reason our model CBA clause sets 45 dBA at the "
                  "nearest residential property line.", "src": "who_noise"},
     ],
     "ask": "A 45 dBA limit at the residential property line as a permit "
            "condition — measured after commissioning, not just modeled — "
            "with quarterly public reporting."},
    {"key": "light", "title": "Light pollution", "icon": "💡",
     "color": "#5B2D5E",
     "summary": "24/7 campus lighting disrupts sleep and circadian "
                "rhythms; the AMA has warned about nighttime light "
                "exposure since 2012.",
     "facts": [
         {"text": "The American Medical Association adopted policy in 2012 "
                  "recognizing nighttime light exposure as a health hazard: "
                  "it suppresses melatonin and disrupts circadian rhythms.",
          "src": "ama_light"},
         {"text": "Chronic light at night is associated with reduced sleep, "
                  "impaired daytime functioning, obesity, and mood "
                  "disorders, with research linking elevated light pollution "
                  "to higher breast and prostate cancer rates.",
          "src": "ama_light"},
         {"text": "Data center campuses typically run high-intensity "
                  "exterior security lighting around the clock.",
          "src": "ehp_health"},
     ],
     "ask": "Full-cutoff shielded fixtures, color temperature at or below "
            "3000K (the AMA community guidance), and dark-sky-compliant "
            "site lighting as approval conditions."},
    {"key": "costs", "title": "Higher bills", "icon": "💸",
     "color": "#7A1F2B",
     "summary": "Large loads strain the grid and shift transmission and "
                "capacity costs onto residential ratepayers.",
     "facts": [
         {"text": "PJM's 2025 capacity auction cleared at a record $16.4B, "
                  "of which the market monitor attributes $6.3B — 38% — to "
                  "data centers. Across PJM's last four base auctions it is "
                  "$29.4B of $63.6B, or 46%. These costs flow through to "
                  "ratepayers across 13 states.", "src": "pjm_auction25"},
         {"text": "Virginia's legislative audit agency (JLARC) found that "
                  "unconstrained data-center growth will raise costs for "
                  "other customers absent policy changes — in the state "
                  "with more data centers than any other.",
          "src": "jlarc_va_2024"},
         {"text": "Berkeley economists warn that who pays for "
                  "data-center-driven grid expansion is a policy choice: "
                  "without large-load tariffs, the default is everyone.",
          "src": "ucb_haas"},
     ],
     "ask": "Cost causation as a condition: the developer pays 100% of "
            "interconnection and grid upgrades, under a large-load tariff "
            "so costs never reach residential bills. Estimate your own "
            "exposure in the Local Impact Calculator."},
    {"key": "water", "title": "Water consumption", "icon": "💧",
     "color": "#1F5D73",
     "summary": "Data centers consume water twice — on site for cooling "
                "and at the power plants that supply them — often in "
                "water-stressed regions.",
     "facts": [
         {"text": "About one-fifth of data centers' direct water footprint "
                  "is drawn from moderately-to-highly water-stressed "
                  "watersheds, and nearly half of servers are powered by "
                  "plants in water-stressed regions.", "src": "siddik_2021"},
         {"text": "Water is consumed twice: directly for evaporative "
                  "cooling on site, and indirectly at the thermoelectric "
                  "power plants generating the electricity.",
          "src": "siddik_2021"},
         {"text": "AI-specific demand is growing fast — researchers project "
                  "AI's water withdrawal could reach billions of cubic "
                  "meters a year by 2027, and most operators still don't "
                  "report site-level water use.", "src": "thirsty_2024"},
     ],
     "ask": "An enforceable annual water cap in the permit, recycled or "
            "non-potable cooling supply, quarterly public metering, and "
            "re-approval before expansion."},
    {"key": "climate", "title": "Climate & reliability", "icon": "🌡️",
     "color": "#2F5D33",
     "summary": "Fossil-heavy demand growth raises emissions, strains "
                "grid reliability, and adds local waste heat.",
     "facts": [
         {"text": "U.S. data-center electricity use is projected to reach "
                  "325-580 TWh by 2028 (Berkeley Lab) — 6.7% to 12% of "
                  "national consumption, up from 176 TWh and 4.4% in 2023 "
                  "— with much of the new supply coming from natural gas.",
          "src": "lbnl"},
         {"text": "The IEA projects data centers will drive one of the "
                  "largest sources of electricity demand growth this "
                  "decade, with the fuel mix determining the emissions "
                  "impact.", "src": "iea_2025"},
         {"text": "Hyperscalers are increasingly turning to on-site gas "
                  "generation as a 'bridge' — locking in fossil combustion "
                  "next to host communities.", "src": "btm_gas"},
     ],
     "ask": "Binding 24/7 carbon-free energy commitments, no "
            "ratepayer-funded gas buildout, and demand-response/curtailment "
            "agreements so the facility sheds load in grid emergencies."},
]

# Two groups, because not every panel is a health risk: air/noise/light/water
# have a documented personal-health pathway, while higher bills is an economic
# harm and climate/reliability is environmental. Presenting "Higher bills" as a
# health risk is inaccurate, so the page and PDF render these under separate
# headings. `title` per group is the section label; membership is by `key`.
HEALTH_RISK_GROUPS = [
    ("health", "Health risks",
     "Documented pathways from a facility to the health of the people who "
     "live near it."),
    ("impacts", "Bills & environment",
     "Not health risks, but the other ways a facility lands on a community — "
     "economic and environmental."),
]
_HEALTH_RISK_GROUP = {"air": "health", "noise": "health", "light": "health",
                      "water": "health", "costs": "impacts",
                      "climate": "impacts"}
for _hr in HEALTH_RISKS:
    _hr["group"] = _HEALTH_RISK_GROUP.get(_hr["key"], "health")

# Project-stage playbook — drives the "Start here" wizard (start_here_tab).
# Each stage maps the situation a community is in to the moves that matter
# this week and the meeting type used for the generated action pack
# (must be a key of MEETING_ADVICE in src/briefs.py).
PROJECT_STAGES = {
    "Rumors — land purchases, unknown LLC activity, nothing filed yet": {
        "emoji": "🕵️",
        "meeting_type": "Town hall / public comment",
        "headline": (
            "You have the most leverage right now — and the least information. "
            "Developers assemble land and utility capacity quietly before anything "
            "is public. Move fast on records."
        ),
        "moves": [
            "Pull county recorder / assessor records for recent land sales near the "
            "parcel — write down the LLC name on every deed",
            "Search the LLC in your Secretary of State's business registry; the "
            "registered agent often points to the real developer or its law firm",
            "Ask your utility (or PUC) whether a large-load interconnection or "
            "will-serve request has been filed for the area",
            "File a public records request for any pre-application meetings between "
            "the developer and your planning or economic development department",
            "Get a data-center item on the next town council agenda before the "
            "applicant controls the narrative",
        ],
    },
    "Application filed — rezoning or permits requested": {
        "emoji": "📋",
        "meeting_type": "Planning commission hearing",
        "headline": (
            "The developer needs approvals from your local boards. Every study you "
            "demand and every condition you attach is binding leverage — a side "
            "letter after approval is not."
        ),
        "moves": [
            "Read the full application at the planning office and note what's "
            "missing: water source, MW at full build-out, noise, tax abatements",
            "Demand water, noise, traffic, and rate-impact studies as conditions "
            "of the permit — before any vote",
            "Insist any community benefit agreement be a written condition of "
            "approval, not a separate promise",
            "Ask for a decommissioning bond so the site isn't abandoned scrap "
            "if the operator leaves",
            "Find out every board member's position before the hearing — "
            "organized residents change votes",
        ],
    },
    "Public hearing scheduled": {
        "emoji": "📣",
        "meeting_type": "Zoning board meeting",
        "headline": (
            "Hearings are won by organized, specific, data-backed comment — not by "
            "turnout alone. Divide the talking points so ten speakers make ten "
            "different arguments."
        ),
        "moves": [
            "Download the action pack below and print copies of the demands for "
            "every board member",
            "Assign each speaker one topic: rates, water, noise, jobs, taxes, "
            "decommissioning — with one number each",
            "Lead with the household cost: grid upgrades land on everyone's bill "
            "unless the developer pays them",
            "Cite communities that won: The Dalles (Google-funded water "
            "infrastructure), Groton CT (CBA as zoning condition)",
            "Ask the board on the record whether a binding CBA is a condition "
            "of approval",
        ],
    },
    "Approved — construction not yet started": {
        "emoji": "🤝",
        "meeting_type": "Direct negotiation with developer",
        "headline": (
            "Approval is not the end. Developers still need building permits, water "
            "agreements, and community goodwill — Mesa AZ residents won noise and "
            "water protections after approval."
        ),
        "moves": [
            "Ask what permits remain (building, water, stormwater) — each is a "
            "negotiation point for a CBA or amendment",
            "Push your council to negotiate a development agreement covering water "
            "caps, noise limits, and annual community payments",
            "Request the utility's interconnection cost estimate and who pays it — "
            "this is where rate impacts are decided",
            "Set up independent baseline monitoring (noise, well levels) before "
            "construction so violations are provable later",
            "Organize now for enforcement: approved conditions only matter if "
            "someone is watching",
        ],
    },
    "Under construction or already operating": {
        "emoji": "⚖️",
        "meeting_type": "PUC rate case hearing",
        "headline": (
            "Your fight moves to the utility commission and enforcement. The goal: "
            "the data center pays its own grid costs, honors its conditions, and "
            "any expansion faces real terms."
        ),
        "moves": [
            "Intervene (or comment) in your utility's next rate case — ask who is "
            "paying for the grid upgrades serving the facility",
            "File complaints through your PUC's portal for noise, water, or "
            "condition violations — linked in your action pack",
            "Request the facility's actual water and power usage via public "
            "records if any public utility serves it",
            "Push for a large-load tariff in your state so the next facility "
            "pays cost-based rates",
            "Treat every expansion request as a new negotiation — grandfathered "
            "terms don't have to carry forward",
        ],
    },
}

# State-level residential electricity rates ($/kWh, 2024 EIA average),
# grid carbon intensity (gCO2/kWh, eGRID 2022 subregion averages mapped to
# dominant state grid), and baseline water stress (low/medium/high, src:
# wri_aqueduct). Used by the local impact calculator.
STATE_GRID_PROFILES = {
    "Alabama":        {"rate": 0.1677, "gco2": 380, "water_stress": "low"},
    "Alaska":         {"rate": 0.2823, "gco2": 450, "water_stress": "low"},
    "Arizona":        {"rate": 0.1523, "gco2": 390, "water_stress": "high"},
    "Arkansas":       {"rate": 0.1436, "gco2": 410, "water_stress": "low"},
    "California":     {"rate": 0.3325, "gco2": 210, "water_stress": "high"},
    "Colorado":       {"rate": 0.1616, "gco2": 420, "water_stress": "medium"},
    "Connecticut":    {"rate": 0.2737, "gco2": 200, "water_stress": "low"},
    "Delaware":       {"rate": 0.1938, "gco2": 370, "water_stress": "low"},
    "District of Columbia": {"rate": 0.254, "gco2": 340, "water_stress": "low"},
    "Florida":        {"rate": 0.1517, "gco2": 370, "water_stress": "low"},
    "Georgia":        {"rate": 0.1584, "gco2": 370, "water_stress": "low"},
    "Hawaii":         {"rate": 0.52, "gco2": 550, "water_stress": "high"},
    "Idaho":          {"rate": 0.1235, "gco2": 120, "water_stress": "medium"},
    "Illinois":       {"rate": 0.2385, "gco2": 310, "water_stress": "low"},
    "Indiana":        {"rate": 0.1815, "gco2": 430, "water_stress": "low"},
    "Iowa":           {"rate": 0.1414, "gco2": 410, "water_stress": "low"},
    "Kansas":         {"rate": 0.1513, "gco2": 420, "water_stress": "medium"},
    "Kentucky":       {"rate": 0.1498, "gco2": 460, "water_stress": "low"},
    "Louisiana":      {"rate": 0.1415, "gco2": 380, "water_stress": "low"},
    "Maine":          {"rate": 0.2863, "gco2": 180, "water_stress": "low"},
    "Maryland":       {"rate": 0.2177, "gco2": 340, "water_stress": "low"},
    "Massachusetts":  {"rate": 0.2882, "gco2": 280, "water_stress": "low"},
    "Michigan":       {"rate": 0.2201, "gco2": 390, "water_stress": "low"},
    "Minnesota":      {"rate": 0.1695, "gco2": 350, "water_stress": "low"},
    "Mississippi":    {"rate": 0.1616, "gco2": 400, "water_stress": "low"},
    "Missouri":       {"rate": 0.1368, "gco2": 440, "water_stress": "low"},
    "Montana":        {"rate": 0.1467, "gco2": 340, "water_stress": "low"},
    "Nebraska":       {"rate": 0.1359, "gco2": 420, "water_stress": "low"},
    "Nevada":         {"rate": 0.136, "gco2": 330, "water_stress": "high"},
    "New Hampshire":  {"rate": 0.2733, "gco2": 190, "water_stress": "low"},
    "New Jersey":     {"rate": 0.2327, "gco2": 250, "water_stress": "low"},
    "New Mexico":     {"rate": 0.1412, "gco2": 410, "water_stress": "high"},
    "New York":       {"rate": 0.2993, "gco2": 250, "water_stress": "low"},
    "North Carolina": {"rate": 0.1509, "gco2": 350, "water_stress": "low"},
    "North Dakota":   {"rate": 0.1361, "gco2": 510, "water_stress": "low"},
    "Ohio":           {"rate": 0.1952, "gco2": 420, "water_stress": "low"},
    "Oklahoma":       {"rate": 0.1338, "gco2": 350, "water_stress": "medium"},
    "Oregon":         {"rate": 0.1627, "gco2": 140, "water_stress": "medium"},
    "Pennsylvania":   {"rate": 0.2155, "gco2": 310, "water_stress": "low"},
    "Rhode Island":   {"rate": 0.2946, "gco2": 280, "water_stress": "low"},
    "South Carolina": {"rate": 0.1618, "gco2": 300, "water_stress": "low"},
    "South Dakota":   {"rate": 0.1573, "gco2": 250, "water_stress": "low"},
    "Tennessee":      {"rate": 0.1447, "gco2": 350, "water_stress": "low"},
    "Texas":          {"rate": 0.1644, "gco2": 350, "water_stress": "medium"},
    "Utah":           {"rate": 0.1296, "gco2": 440, "water_stress": "high"},
    "Vermont":        {"rate": 0.2489, "gco2": 30,  "water_stress": "low"},
    "Virginia":       {"rate": 0.1761, "gco2": 330, "water_stress": "low"},
    "Washington":     {"rate": 0.1495, "gco2": 80,  "water_stress": "medium"},
    "West Virginia":  {"rate": 0.168, "gco2": 520, "water_stress": "low"},
    "Wisconsin":      {"rate": 0.1974, "gco2": 380, "water_stress": "low"},
    "Wyoming":        {"rate": 0.148, "gco2": 460, "water_stress": "low"},
}

# Named campus siting locations: regional temperature penalty on PUE,
# interconnection queue wait (months), and grid carbon (gCO2/kWh). `iso` is
# the regional grid operator the site sits under; the community siting
# evaluator rolls these rows up by ISO rather than keeping its own table.
# Queue waits from LBNL "Queued Up" (2025) + ISO interconnection dashboards;
# carbon from eGRID 2022 subregion averages. `state` maps each named site to
# the STATE_GRID_PROFILES row whose `water_stress` rating (src: wri_aqueduct)
# drives its on-site water-climate multiplier (see
# WATER_STRESS_CLIMATE_MULTIPLIER, src: lei_masanet_2022) — metro areas that
# straddle a state line (Kansas City, "Pacific Northwest") are assigned to
# their larger/primary state; this is a coarser approximation than the named
# site itself.
SITING_REGIONS = [
    {"region": "Northern Virginia (PJM)",                     "iso": "PJM (Mid-Atlantic / Ohio Valley)", "pue_adj": 0.02, "queue_months": 60, "gco2": 380, "state": "Virginia"},
    {"region": "West Texas (ERCOT)",                          "iso": "ERCOT (Texas)",                    "pue_adj": 0.05, "queue_months": 24, "gco2": 340, "state": "Texas"},
    {"region": "Central Iowa (MISO)",                         "iso": "MISO (Midwest)",                   "pue_adj": 0.01, "queue_months": 48, "gco2": 410, "state": "Iowa"},
    {"region": "Pacific Northwest (BPA / PacifiCorp)",        "iso": "BPA / PacifiCorp (Northwest)",     "pue_adj": 0.00, "queue_months": 54, "gco2": 180, "state": "Oregon"},
    {"region": "Central Ohio (PJM)",                          "iso": "PJM (Mid-Atlantic / Ohio Valley)", "pue_adj": 0.02, "queue_months": 54, "gco2": 420, "state": "Ohio"},
    {"region": "Georgia / Atlanta Metro (SERC)",              "iso": "SERC (Southeast)",                 "pue_adj": 0.04, "queue_months": 36, "gco2": 370, "state": "Georgia"},
    {"region": "Phoenix, Arizona (SPP West)",                 "iso": "SPP (Great Plains)",               "pue_adj": 0.08, "queue_months": 30, "gco2": 390, "state": "Arizona"},
    {"region": "South Carolina Midlands (Duke / SERC)",       "iso": "SERC (Southeast)",                 "pue_adj": 0.04, "queue_months": 36, "gco2": 340, "state": "South Carolina"},
    {"region": "North Carolina Piedmont (Duke / PJM)",        "iso": "SERC (Southeast)",                 "pue_adj": 0.03, "queue_months": 42, "gco2": 350, "state": "North Carolina"},
    {"region": "Chicago / NE Illinois (PJM / ComEd)",         "iso": "PJM (Mid-Atlantic / Ohio Valley)", "pue_adj": 0.01, "queue_months": 48, "gco2": 310, "state": "Illinois"},
    {"region": "Dallas–Fort Worth (ERCOT)",                   "iso": "ERCOT (Texas)",                    "pue_adj": 0.05, "queue_months": 24, "gco2": 360, "state": "Texas"},
    {"region": "Salt Lake City, Utah (PacifiCorp)",           "iso": "BPA / PacifiCorp (Northwest)",     "pue_adj": 0.02, "queue_months": 42, "gco2": 440, "state": "Utah"},
    {"region": "New York Metro (NYISO)",                      "iso": "NYISO (New York)",                 "pue_adj": 0.01, "queue_months": 60, "gco2": 250, "state": "New York"},
    {"region": "Mississippi Delta (MISO South)",              "iso": "MISO (Midwest)",                   "pue_adj": 0.06, "queue_months": 30, "gco2": 400, "state": "Mississippi"},
    {"region": "Southeast Michigan (MISO / DTE)",             "iso": "MISO (Midwest)",                   "pue_adj": 0.02, "queue_months": 42, "gco2": 390, "state": "Michigan"},
    {"region": "El Paso, Texas (ERCOT West)",                 "iso": "ERCOT (Texas)",                    "pue_adj": 0.07, "queue_months": 24, "gco2": 350, "state": "Texas"},
    {"region": "San Antonio, Texas (ERCOT / CPS Energy)",     "iso": "ERCOT (Texas)",                    "pue_adj": 0.06, "queue_months": 24, "gco2": 340, "state": "Texas"},
    {"region": "Kansas City (SPP)",                           "iso": "SPP (Great Plains)",               "pue_adj": 0.03, "queue_months": 36, "gco2": 420, "state": "Missouri"},
    {"region": "Indiana (MISO / AES Indiana)",                "iso": "MISO (Midwest)",                   "pue_adj": 0.02, "queue_months": 42, "gco2": 430, "state": "Indiana"},
    {"region": "Nashville, Tennessee (TVA)",                  "iso": "SERC (Southeast)",                 "pue_adj": 0.04, "queue_months": 30, "gco2": 350, "state": "Tennessee"},
    {"region": "Memphis, Tennessee (TVA / MLGW)",             "iso": "SERC (Southeast)",                 "pue_adj": 0.05, "queue_months": 30, "gco2": 370, "state": "Tennessee"},
    {"region": "Reno / Sparks, Nevada (NV Energy)",           "iso": "Not sure / Other",                 "pue_adj": 0.04, "queue_months": 36, "gco2": 330, "state": "Nevada"},
    {"region": "Las Vegas, Nevada (NV Energy)",               "iso": "Not sure / Other",                 "pue_adj": 0.08, "queue_months": 36, "gco2": 380, "state": "Nevada"},
    {"region": "Cheyenne, Wyoming (WAPA / PacifiCorp)",       "iso": "BPA / PacifiCorp (Northwest)",     "pue_adj": 0.00, "queue_months": 36, "gco2": 460, "state": "Wyoming"},
    {"region": "Quincy, Washington (Grant County PUD)",       "iso": "BPA / PacifiCorp (Northwest)",     "pue_adj": 0.00, "queue_months": 42, "gco2": 80,  "state": "Washington"},
    {"region": "The Dalles, Oregon (BPA / PGE)",              "iso": "BPA / PacifiCorp (Northwest)",     "pue_adj": 0.00, "queue_months": 48, "gco2": 120, "state": "Oregon"},
    {"region": "Loudoun County, Virginia (Dominion / PJM)",   "iso": "PJM (Mid-Atlantic / Ohio Valley)", "pue_adj": 0.02, "queue_months": 60, "gco2": 380, "state": "Virginia"},
    {"region": "Prince William County, Virginia (PJM)",       "iso": "PJM (Mid-Atlantic / Ohio Valley)", "pue_adj": 0.02, "queue_months": 60, "gco2": 380, "state": "Virginia"},
    {"region": "Rural Maine (ISO-NE / Versant)",              "iso": "ISO-NE (New England)",             "pue_adj": 0.00, "queue_months": 48, "gco2": 200, "state": "Maine"},
    {"region": "Central Pennsylvania (PJM / PPL)",            "iso": "PJM (Mid-Atlantic / Ohio Valley)", "pue_adj": 0.01, "queue_months": 54, "gco2": 350, "state": "Pennsylvania"},
    {"region": "Upstate New York (NYISO North)",              "iso": "NYISO (New York)",                 "pue_adj": 0.00, "queue_months": 54, "gco2": 180, "state": "New York"},
    {"region": "New Albany, Ohio (AEP / PJM)",                "iso": "PJM (Mid-Atlantic / Ohio Valley)", "pue_adj": 0.02, "queue_months": 54, "gco2": 420, "state": "Ohio"},
    {"region": "Papillion / Sarpy County, Nebraska (OPPD)",   "iso": "SPP (Great Plains)",               "pue_adj": 0.02, "queue_months": 36, "gco2": 440, "state": "Nebraska"},
    {"region": "Albuquerque, New Mexico (PNM / SPP)",         "iso": "SPP (Great Plains)",               "pue_adj": 0.06, "queue_months": 36, "gco2": 370, "state": "New Mexico"},
    {"region": "Sacramento, California (CAISO / SMUD)",       "iso": "CAISO (California)",               "pue_adj": 0.04, "queue_months": 60, "gco2": 220, "state": "California"},
    {"region": "San Jose, California (CAISO / PG&E)",         "iso": "CAISO (California)",               "pue_adj": 0.02, "queue_months": 60, "gco2": 220, "state": "California"},
    {"region": "Henrico County, Virginia (Dominion / PJM)",   "iso": "PJM (Mid-Atlantic / Ohio Valley)", "pue_adj": 0.03, "queue_months": 60, "gco2": 380, "state": "Virginia"},
    {"region": "Abilene, Texas (ERCOT / AEP)",                "iso": "ERCOT (Texas)",                    "pue_adj": 0.06, "queue_months": 24, "gco2": 360, "state": "Texas"},
    {"region": "Stillwater, Oklahoma (SPP / OG&E)",           "iso": "SPP (Great Plains)",               "pue_adj": 0.05, "queue_months": 30, "gco2": 410, "state": "Oklahoma"},
    {"region": "Montgomery County, Missouri (MISO / Ameren)", "iso": "MISO (Midwest)",                   "pue_adj": 0.03, "queue_months": 36, "gco2": 430, "state": "Missouri"},
    {"region": "Farmington, Minnesota (MISO / Xcel)",         "iso": "MISO (Midwest)",                   "pue_adj": 0.01, "queue_months": 42, "gco2": 340, "state": "Minnesota"},
    {"region": "Jackson, Mississippi (Entergy / MISO South)", "iso": "MISO (Midwest)",                   "pue_adj": 0.06, "queue_months": 30, "gco2": 400, "state": "Mississippi"},
    {"region": "Starke County, Indiana (MISO / NIPSCO)",      "iso": "MISO (Midwest)",                   "pue_adj": 0.02, "queue_months": 42, "gco2": 440, "state": "Indiana"},
    {"region": "ACE Basin, South Carolina (Duke / Santee Cooper)", "iso": "SERC (Southeast)",            "pue_adj": 0.04, "queue_months": 36, "gco2": 320, "state": "South Carolina"},
    {"region": "Stokes County, North Carolina (Duke)",        "iso": "SERC (Southeast)",                 "pue_adj": 0.03, "queue_months": 42, "gco2": 350, "state": "North Carolina"},
    {"region": "Pittsylvania County, Virginia (AEP / PJM)",   "iso": "PJM (Mid-Atlantic / Ohio Valley)", "pue_adj": 0.03, "queue_months": 54, "gco2": 370, "state": "Virginia"},
    {"region": "Morgan County, Georgia (Georgia Power / SERC)", "iso": "SERC (Southeast)",               "pue_adj": 0.04, "queue_months": 36, "gco2": 370, "state": "Georgia"},
    {"region": "El Paso County, Texas (ERCOT West / El Paso Electric)", "iso": "ERCOT (Texas)",          "pue_adj": 0.07, "queue_months": 24, "gco2": 350, "state": "Texas"},
    {"region": "Mount Pleasant, Wisconsin (MISO / WE Energies)", "iso": "MISO (Midwest)",                "pue_adj": 0.01, "queue_months": 42, "gco2": 380, "state": "Wisconsin"},
    {"region": "Lousiana Gulf Coast (MISO South / Entergy)",  "iso": "MISO (Midwest)",                   "pue_adj": 0.06, "queue_months": 30, "gco2": 380, "state": "Louisiana"},
]

# Site name → (PUE adjustment, queue months, grid gCO2/kWh, water-climate
# multiplier) for the sandbox. The multiplier comes from the site's mapped
# state's water_stress rating, same as the impact calculator.
SITING_REGION_PROFILES = {
    r["region"]: (
        r["pue_adj"], r["queue_months"], r["gco2"],
        WATER_STRESS_CLIMATE_MULTIPLIER.get(
            STATE_GRID_PROFILES.get(r["state"], {}).get("water_stress", "medium"),
            1.0),
    )
    for r in SITING_REGIONS
}

# ISO-level rollup of SITING_REGIONS — the average queue wait and grid carbon
# across the campus locations in each grid operator's footprint. "Not sure /
# Other" is the fleet-wide average across every location.
GRID_REGION_ROLLUP = {
    iso: {
        "queue_months": round(sum(r["queue_months"] for r in rows) / len(rows)),
        "grid_intensity": round(sum(r["gco2"] for r in rows) / len(rows)),
    }
    for iso, rows in (
        (iso, [r for r in SITING_REGIONS if r["iso"] == iso])
        for iso in dict.fromkeys(r["iso"] for r in SITING_REGIONS)
    )
}
GRID_REGION_ROLLUP["Not sure / Other"] = {
    "queue_months": round(sum(r["queue_months"] for r in SITING_REGIONS) / len(SITING_REGIONS)),
    "grid_intensity": round(sum(r["gco2"] for r in SITING_REGIONS) / len(SITING_REGIONS)),
}

# Farmland price baseline — USDA NASS "Land Values 2024 Summary" (Aug 2024),
# average CROPLAND value ($/acre) by state, 2024. This is the agricultural
# baseline a community can price against when a data-center developer comes
# assembling land: the "before AI" value of the dirt. Source key: usda_land.
# States withheld (D) for cropland in the USDA report use the state's 2024
# FARM REAL ESTATE value from the same report (Arizona 4,000; Nevada 1,150);
# Delaware has no published figure and is omitted. CT/ME/MA/NH/RI/VT are
# reported only as a combined "Other States" group (9,600) and each carries
# that group value. Alaska, Hawaii, and DC are not surveyed and fall back to
# the US average in the UI.
FARMLAND_CROPLAND_USD_ACRE_2024 = {
    "Alabama": 4440, "Arizona": 4000, "Arkansas": 3600, "California": 17330,
    "Colorado": 2810, "Connecticut": 9600, "Florida": 10170, "Georgia": 4330,
    "Idaho": 5820, "Illinois": 9550, "Indiana": 7870, "Iowa": 9800,
    "Kansas": 3300, "Kentucky": 6220, "Louisiana": 3480, "Maine": 9600,
    "Maryland": 8770, "Massachusetts": 9600, "Michigan": 5870, "Minnesota": 6540,
    "Mississippi": 3880, "Missouri": 4910, "Montana": 1280, "Nebraska": 6540,
    "Nevada": 1150, "New Hampshire": 9600, "New Jersey": 16300,
    "New Mexico": 2000, "New York": 3850, "North Carolina": 5120,
    "North Dakota": 2600, "Ohio": 9270, "Oklahoma": 2310, "Oregon": 4350,
    "Pennsylvania": 9270, "Rhode Island": 9600, "South Carolina": 3800,
    "South Dakota": 4350, "Tennessee": 5610, "Texas": 2570, "Utah": 5040,
    "Vermont": 9600, "Virginia": 5930, "Washington": 3410,
    "West Virginia": 4050, "Wisconsin": 6800, "Wyoming": 1960,
}
# US average cropland value, USDA NASS 2024 ($/acre) — UI fallback + anchor.
US_CROPLAND_USD_ACRE_2024 = 5570

# Microsoft & AWS environmental headline data for cross-company comparison
# Microsoft: FY2025 Environmental Sustainability Report (published Jul 2026)
MICROSOFT_ENV_HEADLINE = {
    "report_year": "FY2025",
    "source": "Microsoft 2025 Environmental Sustainability Report",
    "dc_twh": 29.8,           # FY2024 24.0 TWh × reported +24% electricity growth (est.)
    "total_emissions_mt": 20.29,
    "scope2_location_mt": 9.7,   # est. from FY2024 7.8 Mt + 24% electricity growth
    "scope2_market_mt": 2.7,     # reported — jumped from 0.26 Mt after dropping unbundled RECs
    "yoy_emissions_growth_pct": 25,
    "pue": 1.18,                 # fleet design PUE, Microsoft datacenter fact sheet
    "water_consumption_mgal": 6_441,   # FY2024 figure; FY2025 not yet extracted
    "water_replenish_pct": 37,
    "renewable_pct": 100,
    "notes": "Total emissions 20.29 Mt (+25% YoY), driven by data center build-out. "
             "Market-based Scope 2 jumped 0.26 → 2.7 Mt after Microsoft stopped "
             "counting non-additional unbundled RECs — a transparency win that "
             "reveals real grid impact. Electricity +24% YoY; 40 GW renewable "
             "portfolio across 26 countries. DC TWh and location-based Scope 2 "
             "are estimates from reported growth rates; water is FY2024.",
}

# AWS: Amazon 2025 Sustainability Report (published Jul 2026, CY2025 data)
AWS_ENV_HEADLINE = {
    "report_year": "CY2025",
    "source": "Amazon 2025 Sustainability Report",
    "dc_twh": 38.0,           # est.: CY2024 ~30.5 TWh × ~25% capacity growth
    "total_emissions_mt": 80.85,   # all Amazon, not just AWS
    "scope2_location_mt": 11.9,    # est.: purchased-electricity emissions +34% YoY on 8.9 Mt
    "scope2_market_mt": 0.0,
    "yoy_emissions_growth_pct": 16,
    "pue": 1.14,                   # reported global fleet average, 2025
    "water_consumption_mgal": 4_600,   # CY2024 figure; CY2025 reports WUE only
    "water_replenish_pct": 75,     # progress toward 2030 water-positive goal (was 53% in 2024)
    "renewable_pct": 100,
    "notes": "Total Amazon emissions 80.85 Mt (+16% YoY, largest jump since tracking "
             "began); purchased-electricity emissions +34% on record data center "
             "build-out (1.2+ GW added in Q4 2025 alone). Fleet PUE 1.14; WUE 0.12 "
             "L/kWh (−20% YoY); 100% renewable match 3rd straight year; 75% toward "
             "water-positive. AWS does not break out DC-only electricity — TWh and "
             "location-based Scope 2 are estimates from reported growth rates.",
}

# ---------------------------------------------------------------------------
# Data-center operators — environmental headline dicts
# ---------------------------------------------------------------------------

EQUINIX_2024_HEADLINE = {
    "report_year": "FY2024",
    "source": "Equinix 2025 Sustainability Report / Data Summary",
    "dc_twh": 8.17,            # FY2023 confirmed; FY2024 not yet located
    "pue": 1.39,
    "wue": 0.95,
    "scope1_tco2e": 59_400,
    "scope2_location_tco2e": 2_645_700,
    "scope2_market_tco2e": 253_300,
    "scope3_tco2e": 1_435_000,
    "renewable_pct": 96,
    "water_consumption_mgal": 1_104,   # 4,180 ML × 0.264172
    "nonpotable_water_pct": 37,
    "data_centers": 268,
    "markets": 74,
    "countries": 35,
    "revenue_b": 8.7,
    "net_zero_target": 2040,
    "sbti_validated": True,
    "notes": "FY2024 Scope 1+2+3 = 1.75 Mt; down 10% from 2019 baseline "
             "despite business growth. DC TWh is FY2023 (8.17); FY2024 "
             "figure not yet extracted from primary report. PUE improved 6% "
             "YoY. SBTi-validated: −90% absolute Scope 1+2 and −90% Scope 3 "
             "vs. 2019 by 2040. Heat exported to communities: 14.5 GWh (+245%).",
    "est_twh": True,
}

DIGITAL_REALTY_2024_HEADLINE = {
    "report_year": "FY2024/FY2025",
    "source": "Digital Realty 2025 Impact Report",
    "pue": 1.38,               # FY2025 global
    "wue": 0.59,               # FY2025, −15.7% YoY
    "scope1_tco2e": 51_745,    # FY2024
    "scope2_location_tco2e": 3_311_323,
    "scope2_market_tco2e": 948_175,
    "scope3_tco2e": 1_456_435, # FY2024, +16.9% YoY
    "renewable_pct": 93,       # FY2025
    "data_centers": 300,
    "markets": 55,
    "countries": 30,
    "revenue_b": 6.1,
    "nonpotable_water_pct": 45,
    "notes": "PUE/WUE/renewable from FY2025; Scope 1/2/3 from FY2024. "
             "Absolute TWh and water consumption not disclosed. EMEA PUE "
             "1.31; new 2025 builds designed at 1.20. 42% of European IT "
             "capacity carbon-neutral certified. +3% water use vs +34% "
             "portfolio growth (2023-2025). SBTi status unconfirmed.",
}

EDGECONNEX_2024_HEADLINE = {
    "report_year": "FY2024",
    "source": "EdgeConneX 5th Annual Sustainability Report (Sept 2025)",
    "dc_twh": 1.66,            # 1,659,057 MWh
    "pue": 1.33,
    "scope1_tco2e": 17_925,
    "scope2_market_tco2e": 0,
    "scope3_tco2e": 498_287,
    "renewable_pct": 90,
    "water_consumption_mgal": 25,  # 96,491 m³ × 0.000264172 Mgal/m³ ≈ 25
    "water_free_pct": 93,
    "capacity_mw": 410,
    "sbti_validated": True,
    "notes": "SBTi Scope 1+2 target met (−50.4%); Scope 3 target exceeded "
             "(−64%) vs 2021 baseline. Market-based Scope 2 is 0 tCO2e "
             "(100% RECs/PPAs); location-based Scope 2 not disclosed. "
             "93% of sites use water-free cooling. Includes 50% of "
             "AdaniConneX (India) JV from 2022 onward.",
}

STACK_2023_HEADLINE = {
    "report_year": "FY2023",
    "source": "STACK Infrastructure 2024 Impact Report (April 2025)",
    "pue": 1.35,
    "wue": 1.08,
    "scope1_tco2e": 3_900,
    "scope2_tco2e": 295_400,   # renewable-covered; unclear loc vs mkt
    "scope3_tco2e": 460_300,
    "renewable_pct": 100,      # since Dec 31, 2021
    "capacity_gw": 7,          # built + in-development + potential
    "facilities": 37,
    "markets": 22,
    "sbti_committed": True,    # Sept 2024
    "notes": "100% renewable procurement since 2021; >1,000 GWh procured "
             "in 2023. Scope 2 boundary (location vs market) unclear in "
             "report. 34.8 M gallons potable water saved via reclaimed-water "
             "systems. SBTi committed (not yet validated) as of Sept 2024.",
}

CYRUSONE_2023_HEADLINE = {
    "report_year": "FY2023",
    "source": "CyrusOne 2024 Sustainability Report (June 2024)",
    "pue": 1.46,
    "scope1_tco2e": 27_710,
    "scope2_market_tco2e": 402_058,
    "scope3_tco2e": 474_137,
    "carbon_free_pct": 61.6,
    "data_centers": 50,
    "sbti_validated": True,
    "net_positive_water_sites": 12,
    "notes": "Private since April 2022 (KKR/GIP, $15B). Emissions down "
             "29.4% vs 2021 baseline, exceeding SBTi interim by >16 ppts. "
             "Net Positive Water at 12 facilities + US HQ. EcoVadis Gold "
             "(top 5%) 3rd consecutive year. $11.2B sustainability-linked "
             "financing secured in 2024. TWh and absolute water not disclosed.",
}

VANTAGE_2023_HEADLINE = {
    "report_year": "CY2023",
    "source": "Vantage Data Centers 2023 ESG Report (July 2024)",
    "pue": 1.26,               # annualized design PUE
    "scope1_tco2e": 4_371,
    "scope2_location_tco2e": 49_420,
    "capacity_gw": 2,          # >2 GW total IT once fully built
    "campuses": 34,
    "notes": "Design PUE; operational PUE not disclosed. Scope 2 is "
             "location-based only; market-based deferred pending 3rd-party "
             "verification. Scope 3 not quantified (reported as 96.2% of "
             "total). Near-zero water via air-cooled chiller design. 4 of 34 "
             "campuses at >99% renewable. Net zero S1+2 by 2030, all scopes "
             "by 2040 (The Climate Pledge).",
}

# Limited-disclosure operators (capacity/profile only, minimal ESG)
COREWEAVE_PROFILE = {
    "report_year": "FY2025",
    "source": "CoreWeave FY2025 10-K (SEC filing)",
    "capacity_mw": 850,
    "contracted_gw": 3.1,
    "data_centers": 43,
    "revenue_b": 5.13,
    "esg_disclosure": False,
    "notes": "IPO March 2025 (NASDAQ: CRWV). No sustainability report, no "
             "CDP response, no Scope 1/2/3 inventory, no PUE/WUE figures. "
             "Marketing claims: $2B Scotland buildout 'powered by renewable "
             "energy'; liquid cooling '300x more water efficient' (unverified, "
             "no baseline). Revenue grew from $229M (2023) to $5.13B (2025).",
}

QTS_PROFILE = {
    "report_year": "FY2024",
    "source": "QTS 2024 Sustainability Report",
    "wue": 0.82,               # −27% YoY
    "carbon_free_pct": 100,
    "contracted_gw": 2,
    "carbon_free_mwh": 489_390,
    "esg_disclosure": "partial",
    "notes": "Private since 2021 (Blackstone, $10B). Fleet PUE not disclosed "
             "publicly. Scope 1/2/3 not in report summary (third-party "
             "estimates exist but unverified). Claims 100% carbon-free "
             "operational electricity. 100% new greenfield builds are "
             "water-free. ~1.5B gallons/year saved via closed-loop cooling.",
}

SWITCH_PROFILE = {
    "report_year": "CY2024",
    "source": "Switch ESG webpage (marketing claims only)",
    "pue": 1.18,               # marketing claim, not from audited report
    "renewable_pct": 100,      # since 2016, marketing claim
    "esg_disclosure": False,
    "notes": "Private since 2023 (DigitalBridge). No downloadable ESG report "
             "found — only marketing webpage. PUE 1.18 and 100% renewable "
             "since 2016 are unverified claims. No Scope 1/2/3, no WUE, no "
             "absolute water figures. Las Vegas: 315 MW; Tahoe Reno: up to "
             "2 GW planned. $20B green financing raised since 2024.",
}

COMPASS_PROFILE = {
    "report_year": "FY2024",
    "source": "Compass Datacenters Outcomes 2025 Report (Oct 2025)",
    "pue": 1.25,               # annualized design PUE
    "wue": 0,                  # waterless cooling design
    "esg_disclosure": "partial",
    "notes": "Build-to-suit model: Scope 1/2 covers corporate offices only "
             "(~3,700 tCO2e), NOT data center operations. Actual DC energy "
             "sits in Scope 3 Category 13 (downstream leased assets, +17% "
             "in 2024). Total capacity, campus count, and markets not "
             "disclosed. Waterless cooling design (zero water for IT loads). "
             "Embodied carbon in construction −33% per MW (2022-2024).",
}

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
    "thirsty_2024": ("Li et al., Making AI Less Thirsty — water footprint of AI (arXiv:2304.03271)",
                     "https://arxiv.org/abs/2304.03271"),
    "usgs_water":   ("USGS — Thermoelectric power water use (withdrawal & consumption by fuel)",
                     "https://www.usgs.gov/mission-areas/water-resources/science/thermoelectric-power-water-use"),
    "usda_land":    ("USDA NASS — Land Values 2024 Summary (cropland value $/acre by state)",
                     "https://www.nass.usda.gov/Publications/Todays_Reports/reports/land0824.pdf"),
    "usda_quickstats": ("USDA NASS QuickStats — query cropland/farm real estate values live by state & county",
                        "https://quickstats.nass.usda.gov/"),
    "gjf_subsidy":  ("Good Jobs First — Subsidy Tracker (tax abatements & subsidies given to data centers)",
                     "https://subsidytracker.goodjobsfirst.org/"),
    "salem_bloc":   ("Times Leader — 96 Salem Twp. landowners' historic 1,700-acre collective data-center sale",
                     "https://www.timesleader.com/news/1735892/96-salem-twp-landowners-complete-historic-1700-acre-sale-for-major-data-center-campus"),
    "salem_bloc2":  ("Times Leader — 4-3 Group's second Salem Township data-center land deal (~1.2B)",
                     "https://www.timesleader.com/news/1745226/1-2-billion-land-deal-for-second-data-center-project-in-salem-township-announced-by-4-3-group"),
    "marcellus_lease": ("Penn State Extension — natural gas landowner leasing, royalties & coalitions",
                        "https://extension.psu.edu/energy/marcellus-shale-and-natural-gas/landowner-leasing-and-royalties"),
    "mlenergy":     ("ML.ENERGY Leaderboard — measured per-model inference energy (live)",
                     "https://ml.energy/leaderboard"),
    "iea_2025":     ("IEA, Energy and AI (2025) + Key Questions update (2026)",
                     "https://www.iea.org/reports/energy-and-ai"),
    "gpt5_report":  ("Third-party GPT-5 energy report (2025) — contested",
                     "https://www.datacenterdynamics.com/"),
    "yahoo_finance":("Yahoo Finance — live delayed stock quotes (chart API)",
                     "https://finance.yahoo.com/"),
    "elmaps":       ("Electricity Maps — real-time grid carbon intensity API",
                     "https://www.electricitymaps.com/"),
    "watttime":     ("WattTime — marginal emissions (MOER) API",
                     "https://watttime.org/"),
    "gridstatus":   ("GridStatus.io / EIA-930 — ISO fuel mix & emissions",
                     "https://www.gridstatus.io/"),
    "eia_rates":    ("EIA — Electric Power Monthly, Table 5.6.A: average retail price of electricity to residential customers by state (the current figure, updated monthly)",
                     "https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a"),
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
    "microsoft_dc": ("Microsoft — Datacenter communities (first-party, metro-level)",
                     "https://local.microsoft.com/communities/"),
    "aws_dc":       ("Amazon — AWS investment announcements & global infrastructure (first-party)",
                     "https://www.aboutamazon.com/what-we-do/amazon-web-services"),
    # --- SEC 10-K "Competition" sections + AI-competitor compute sites ---
    "goog_10k":     ("Alphabet Inc. — Form 10-K FY2024, Item 1 “Competition” (SEC EDGAR)",
                     "https://www.sec.gov/Archives/edgar/data/1652044/000165204425000014/goog-20241231.htm"),
    "meta_10k":     ("Meta Platforms, Inc. — Form 10-K FY2025, Item 1 “Competition” (SEC EDGAR)",
                     "https://www.sec.gov/Archives/edgar/data/1326801/000162828026003942/meta-20251231.htm"),
    "msft_10k":     ("Microsoft Corp. — Form 10-K FY2025, Item 1 “Competition” (SEC EDGAR)",
                     "https://www.sec.gov/Archives/edgar/data/789019/000095017025100235/msft-20250630.htm"),
    "amzn_10k":     ("Amazon.com, Inc. — Form 10-K FY2025, Item 1 “Competition” (SEC EDGAR)",
                     "https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/amzn-20251231.htm"),
    "orcl_10k":     ("Oracle Corp. — Form 10-K FY2026, Item 1 “Competition” (SEC EDGAR)",
                     "https://www.sec.gov/Archives/edgar/data/1341439/000119312526277521/orcl-20260531.htm"),
    "crwv_10k":     ("CoreWeave, Inc. — Form 10-K FY2025, Item 1 “Competition” (SEC EDGAR)",
                     "https://www.sec.gov/Archives/edgar/data/1769628/000176962826000104/crwv-20251231.htm"),
    "stargate":     ("OpenAI — Stargate AI data-center sites (OpenAI · Oracle · SoftBank; first-party)",
                     "https://openai.com/index/five-new-stargate-sites/"),
    "xai_memphis":  ("xAI — Colossus supercomputer, Memphis (first-party)",
                     "https://x.ai/memphis"),
    "crwv_dc":      ("CoreWeave — Our capacity plans for CoreWeave data centers (first-party) + Core Scientific host-site announcements",
                     "https://www.coreweave.com/blog/our-capacity-plans-for-coreweave-data-centers"),
    # --- Operator ownership / property-LLC structure (press-sourced) ---
    # Composite: one key covering ownership + filing-LLC naming across several
    # operators, so no single first-party page can back it. Points at EDGAR
    # full-text search — the government index where a parent, a subsidiary or
    # a property LLC can actually be looked up — rather than at a trade-press
    # summary. Per-deal claims get their own first-party keys (switch_dbif,
    # vantage_dbsl, …); prefer adding one of those over leaning on this.
    "dc_ownership": ("Operator ownership & filing-LLC naming patterns — compiled from operator releases and county filings, then checked against SEC EDGAR full-text search. Composite, not a single citation: look the entity up yourself before naming it in a filing",
                     "https://www.sec.gov/edgar/search/"),
    "vantage_dbsl": ("Vantage Data Centers — $9.2B equity investment led by DigitalBridge & Silver Lake (closed Jun 2024)",
                     "https://vantage-dc.com/news/vantage-data-centers-completes-9-2-billion-equity-investment-led-by-digitalbridge-and-silver-lake/"),
    "switch_dbif":  ("Switch, Inc. — DigitalBridge & IFM Investors complete $11B take-private, Dec 6 2022 (first-party)",
                     "https://www.switch.com/digitalbridge-and-ifm-investors-complete-11-billion-take-private-of-switch/"),
    "crwv_coresci": ("CoreWeave to acquire Core Scientific — all-stock ~$9B (announced Jul 2025)",
                     "https://www.coreweave.com/news/coreweave-to-acquire-core-scientific"),
    "imasons":      ("Infrastructure Masons (iMasons) — industry & sustainability data",
                     "https://imasons.org/"),
    "bnef":         ("BloombergNEF (BNEF) — data-center power-demand research & forecasts",
                     "https://about.bnef.com/"),
    "ercot_ll":     ("ERCOT — Large Load Interconnection Queue (Dec 2025 board update)",
                     "https://www.ercot.com/gridinfo/load"),
    "pjm_lf":       ("PJM — 2025 Long-Term Load Forecast (data-center-driven growth)",
                     "https://www.pjm.com/-/media/DotCom/library/reports-notices/load-forecast/2025-load-report.pdf"),
    "eia_va":       ("EIA — Commercial electricity sales in Virginia driven by data centers (2025)",
                     "https://www.eia.gov/todayinenergy/detail.php?id=67664"),
    "eia_pilot":    ("EIA — Pilot survey on energy use at data centers (Mar 2026)",
                     "https://www.eia.gov/pressroom/releases/press585.php"),
    "lbnl_price_trends": ("Berkeley Lab (LBNL) — Retail Electricity Price and Cost Trends: 2024 Update (FERC Form 1 data through 2023)",
                     "https://eta-publications.lbl.gov/sites/default/files/2025-01/retail_price_and_cost_trends_2024_update_final_v3.pdf"),
    # --- How the RTOs/ISOs & FERC are responding (Data centers tab) ---
    "ferc_pjm_colo": ("FERC — directs PJM to write co-location rules for data centers (Dec 18, 2025 fact sheet; Docket EL25-49/AD24-11)",
                     "https://www.ferc.gov/news-events/news/fact-sheet-ferc-directs-nations-largest-grid-operator-create-new-rules-embrace"),
    "ferc_showcause": ("FERC — show-cause orders to MISO, SPP & other RTOs on large-load interconnection (Jun 18, 2026)",
                     "https://www.ferc.gov/news-events/news/ferc-launches-aggressive-targeted-action-speed-large-load-integration"),
    "pjm_auction25": ("Monitoring Analytics (PJM market monitor) — data centers drove $6.3B of the record $16.4B 2025 capacity auction (38%), and $29.4B of $63.6B across the last four auctions (46%); see the 2025/2026 RPM Base Residual Auction analyses",
                     "https://www.monitoringanalytics.com/reports/Reports/2025.shtml"),
    "tx_sb6_ll":    ("Texas SB 6 (89R, signed June 20, 2025) — ERCOT may curtail/disconnect large loads (≥75 MW) in emergencies; new interconnection standards. Official bill text & history",
                     "https://capitol.texas.gov/BillLookup/History.aspx?LegSess=89R&Bill=SB6"),
    "spp_hill":     ("SPP — High Impact Large Load (HILL) integration, the 90-day study process from RR696; FERC accepted the tariff revisions effective Jan 15 2026 (first-party)",
                     "https://www.spp.org/markets-operations/high-impact-large-load-hill-integration/"),
    "miso_llir":    ("MISO — Large Load Additions & Large Load Interconnection Reliability Requirements (2025–26)",
                     "https://www.misoenergy.org/planning/large-loads---container-page/large-load-additions/"),
    "gartner":      ("Gartner — data-center electricity to double by 2030 (~980 TWh)",
                     "https://www.gartner.com/en/newsroom/press-releases/2025-11-17-gartner-says-electricity-demand-for-data-centers-to-grow-16-percent-in-2025-and-double-by-2030"),
    "bnef_106":     ("BloombergNEF — US data-center power demand ~106 GW by 2035 (first-party insight, Dec 2025)",
                     "https://about.bnef.com/insights/clean-energy/ai-and-the-power-grid-where-the-rubber-meets-the-road/"),
    "wri_range":    ("World Resources Institute — US 2030 forecasts span 206–970 TWh",
                     "https://www.wri.org/insights/us-data-centers-electricity-demand"),
    "sp_451":       ("S&P Global / 451 Research — global data-center demand ~1,587 TWh by 2030",
                     "https://www.spglobal.com/energy/en/news-research/latest-news/electric-power/110525-global-data-center-power-demand-expected-to-almost-double-by-2030"),
    "epri_pi":      ("EPRI — Powering Intelligence 2026 (US Low/Medium/High scenarios)",
                     "https://powering-intelligence.epri.com/summary-projections.html"),
    "lbnl":         ("Lawrence Berkeley National Lab, 2024 US Data Center Energy Usage Report — 325–580 TWh (6.7–12% of US electricity) by 2028, up from 176 TWh (4.4%) in 2023",
                     "https://eta.lbl.gov/publications/2024-united-states-data-center-energy"),
    "belfer":       ("Harvard Belfer Center — AI, Data Centers, and the U.S. Electric Grid: A Watershed Moment (Feb 2026)",
                     "https://www.belfercenter.org/research-analysis/ai-data-centers-us-electric-grid"),
    "e3_amazon":    ("E3 (for Amazon) — Tailored for Scale: Designing Electric Rates and Tariffs for Large Loads (Dec 2025). Utility-funded: commissioned by Amazon, and concludes its data centers are not cross-subsidized",
                     "https://www.ethree.com/ratepayer-study/"),
    "columbia_get": ("Columbia CGEP — Electricity Affordability and Load Growth: grid-enhancing technologies, demand response and data-center load flexibility as near-term capacity (Jun 2026)",
                     "https://www.energypolicy.columbia.edu/publications/electricity-affordability-and-load-growth-diagnosing-and-fixing-the-problem/"),
    "ucb_haas":     ("UC Berkeley Energy Institute — What Will Data Centers Do To Your Electric Bill? (2025)",
                     "https://energyathaas.wordpress.com/2025/09/29/what-will-data-centers-do-to-your-electric-bill/"),
    # --- Governor data-center stances (Officials tab) ---
    "tx_sb6":       ("Texas Legislature — SB 6 (89R), large-load grid rules, signed June 20, 2025. Official bill text & history",
                     "https://capitol.texas.gov/BillLookup/History.aspx?LegSess=89R&Bill=SB6"),
    # --- House member data-centre stances (Officials tab) ---
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
    # --- Official data-center stances (Officials scorecard) ---
    "ga_kemp":      ("Georgia governor vetoes bill to pause data-center tax breaks (2024)",
                     "https://www.datacenterdynamics.com/en/news/georgia-governor-vetoes-bill-to-pause-data-center-tax-breaks/"),
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
    "house_rpa":    ("House E&C — Ratepayer Protection Act (large loads pay their own way)",
                     "https://www.eenews.net/articles/energy-and-commerce-lawmakers-to-introduce-data-center-bill/"),
    "house_pallone":("Rep. Pallone calls for a national data-center moratorium (2026)",
                     "https://www.eenews.net/articles/data-center-moratorium-still-has-few-takers-on-capitol-hill/"),
    "house_subram": ("Rep. Subramanyam files data-center protection/energy-cost bills (2026)",
                     "https://virginiamercury.com/2026/05/22/va-congressmen-file-energy-cost-transparency-data-center-attack-protections-bills/"),
    "sen_heinrich": ("Sen. Heinrich (ENR Ranking Member) — GRID Savings Act, large users pay for the grid (2026)",
                     "https://www.energy.senate.gov/2026/8/heinrich-introduces-legislation-to-ensure-large-users-of-electricity-pay-for-grid-upgrades-protect-customers-from-costs-of-data-center-expansion"),
    "sen_warner":   ("Sen. Warner — bill so Virginians aren't stuck footing big data-center costs (2026)",
                     "https://www.warner.senate.gov/newsroom/press-releases/warner-sponsors-bill-to-ensure-virginians-arent-stuck-footing-the-bill-for-big-data-centers/"),
    "sen_ossoff":   ("Sen. Ossoff investigates Georgia data centers' impact on power bills (2026)",
                     "https://www.wrdw.com/2026/04/20/ossoff-looks-into-ga-data-centers-impact-power-bills/"),
    "sen_fetterman":("Sen. Fetterman calls a data-center moratorium 'China First' (2026)",
                     "https://thehill.com/homenews/senate/5877732-fetterman-ai-data-centers/"),
    "sen_hawley":   ("Sens. Hawley & Blumenthal — GRID Act to stop data centers raising electric bills (2026)",
                     "https://www.hawley.senate.gov/hawley-blumenthal-introduce-bill-to-prevent-data-centers-from-increasing-electricity-costs-for-americans"),
    "sen_welch":    ("Sen. Welch joins bill so Americans aren't footing big data-center costs (2026)",
                     "https://www.welch.senate.gov/welch-joins-new-bill-to-ensure-americans-arent-footing-the-bill-for-big-data-centers"),
    "sen_husted":   ("Sen. Husted leads bill to protect Americans from new data-center costs (2026)",
                     "https://www.husted.senate.gov/media/press-releases/husted-leads-bill-to-protect-americans-from-footing-the-bill-for-new-data-centers/"),
    "gov_whitmer":  ("Gov. Whitmer — data centers must pledge to cover utility costs (2026)",
                     "https://bridgemi.com/michigan-government/where-michigan-governor-candidates-stand-on-data-centers-the-environment/"),
    "pjm_dm2":      ("PJM Data Miner 2 — gen_by_fuel & fivemin_marginal_emissions feeds",
                     "https://dataminer2.pjm.com/"),
    "ercot_ll":     ("ERCOT — Large Load Integration (forms, reports & Batch Zero)",
                     "https://www.ercot.com/services/rq/large-load-integration"),
    "ercot_ll_bc":  ("ERCOT — Large Load Update to Senate Committee on Business & Commerce "
                     "(Apr 1 2026; data as of Mar 26 2026)",
                     "https://www.ercot.com/files/docs/2026/04/01/ERCOT_LargeLoad_Update_April2026_B-C_-Hearing.pdf"),
    "ercot_ll_tac": ("ERCOT — Large Load Interconnection status, March TAC report (Mar 13 2026)",
                     "https://www.ercot.com/files/docs/2026/03/12/March-TAC-Report.pdf"),
    "electricchoice": ("U.S. Data Center Power Map by State — ElectricChoice.com compilation (updated July 2026; CC-BY 4.0). Underlying load research: LBNL 2024 US Data Center Energy Usage Report; rates: EIA",
                      "https://www.electricchoice.com/datacenters/"),
    "eia_state":    ("EIA — State Electricity Profiles (generation, prices, consumption, emissions per state; U.S. Energy Information Administration)",
                     "https://www.eia.gov/electricity/state/"),
    "google_env_2026": ("Google 2026 Environmental Report (FY2025) — first-party, third-party limited assurance (KPMG). Electricity, GHG, Water, PUE, CFE.",
                      "https://sustainability.google/reports/google-2026-environmental-report/"),
    "meta_env_2025":  ("Meta 2025 Environmental Data Index (FY2024) — Electricity, GHG, Water, PUE/WUE per campus. sustainability.atmeta.com",
                      "https://sustainability.atmeta.com/wp-content/uploads/2025/10/Meta_2025-Environmental-Data-Index.pdf"),
    "msft_env_2025":  ("Microsoft 2025 Environmental Sustainability Report (FY2025, published Jul 2026) — total emissions 20.29 Mt (+25%), Scope 2 market 2.7 Mt after dropping unbundled RECs",
                      "https://www.microsoft.com/en-us/corporate-responsibility/sustainability/report"),
    "amzn_env_2025":  ("Amazon 2025 Sustainability Report (CY2025, published Jul 2026) — 80.85 Mt total (+16%), purchased-electricity emissions +34%, PUE 1.14, WUE 0.12",
                      "https://sustainability.aboutamazon.com/2025-report"),
    "crc_mich_2026":  ("Citizens Research Council of Michigan — Data Centers in Michigan: Policy Controversies (June 2026)",
                      "https://crcmich.org/publications/data-centers-in-michigan-evaluation-controversies-hyperscale-development"),
    "jlarc_va_2024":  ("Virginia JLARC — Data Center Impact Study (Report 591, Dec 2024)",
                      "https://jlarc.virginia.gov/pdfs/reports/Rpt591.pdf"),
    "ga_house_2024":  ("Georgia House of Representatives — Joint Committee on Data Center Tax Incentives (2024)",
                      "https://www.house.ga.gov/"),
    "oregon_doe_2024":("Oregon Department of Energy — Data and Reports (Biennial Energy Report; data-center load is covered in the demand chapter)",
                      "https://www.oregon.gov/energy/Data-and-Reports/Pages/default.aspx"),
    "md_assembly_2024":("Maryland General Assembly — Critical Infrastructure Streamlining Act of 2024 (CISA / SB 116)",
                      "https://mgaleg.maryland.gov/"),
    "iurc_indiana_2026":("Indiana General Assembly — IURC Large Load Energy & Water Study (HB 1245, 2026)",
                      "https://iga.in.gov/"),
    "nj_bpu_2026":    ("New Jersey BPU & Legislature — Ratepayer Subsidy Study & Large Load Tariffs (P.L. 2025 c. 98 / A-796)",
                      "https://www.nj.gov/bpu/"),
    "pew_rural_2026": ("Pew Research Center — Most new data centers in the U.S. are coming to rural areas (April 13, 2026)",
                      "https://www.pewresearch.org/short-reads/2026/04/13/most-new-data-centers-in-the-us-are-coming-to-rural-areas/"),
    "datacentermap":  ("DataCenterMap.com — U.S. Data Center Directory & Industry Map",
                      "https://www.datacentermap.com/usa/"),
    "msft_community_2026": ("Microsoft — Building Community-First AI Infrastructure Framework (January 2026)",
                      "https://blogs.microsoft.com/on-the-issues/2026/01/13/community-first-ai-infrastructure/"),
    "aws_water_2026": ("AWS — Water stewardship, consumption disclosures, and 2030 water-positive progress (June 2026)",
                      "https://sustainability.aboutamazon.com/water"),
    "meta_community_2026": ("Meta — Data Center Community Action Grants (first-party programme page)",
                      "https://datacenters.atmeta.com/community-action-grants/"),
    # --- Independent Market Monitors (IMM) — annual State of the Market reports ---
    "imm_pjm":      ("Monitoring Analytics — PJM State of the Market (Independent Market Monitor)",
                     "https://www.monitoringanalytics.com/reports/PJM_State_of_the_Market/2025.shtml"),
    "imm_ercot":    ("Potomac Economics — ERCOT State of the Market (Independent Market Monitor)",
                     "https://www.potomaceconomics.com/markets-monitored/ercot/"),
    "imm_miso":     ("Potomac Economics — MISO State of the Market (Independent Market Monitor)",
                     "https://www.potomaceconomics.com/markets-monitored/miso/"),
    "imm_isone":    ("Potomac Economics — ISO New England State of the Market (Independent Market Monitor)",
                     "https://www.potomaceconomics.com/markets-monitored/iso-new-england/"),
    "imm_nyiso":    ("Potomac Economics — NYISO State of the Market (Independent Market Monitor)",
                     "https://www.potomaceconomics.com/markets-monitored/new-york-iso/"),
    "imm_caiso":    ("CAISO Department of Market Monitoring — Annual Report on Market Issues & Performance",
                     "https://www.caiso.com/market-operations/market-monitoring/reports-and-presentations"),
    "imm_spp":      ("SPP Market Monitoring Unit — Annual State of the Market Report",
                     "https://www.spp.org/markets-operations/market-monitoring/"),
    "caiso_largeload": ("CAISO — Large Load Considerations Issue Paper (Jan 2026, data-center forecasting)",
                     "https://www.caiso.com/documents/issue-paper-large-load-consideration-jan-20-2026.pdf"),
    # --- Ratepayer / consumer-advocacy organizations ---
    "pulp":         ("Pennsylvania Utility Law Project (PULP) — low-income ratepayer advocacy & data-center cost cases",
                     "https://www.pautilitylawproject.org/"),
    "cause_pa":     ("CAUSE-PA — Coalition for Affordable Utility Services & Energy Efficiency in PA (repped by PULP)",
                     "https://www.pautilitylawproject.org/"),
    "nasuca":       ("NASUCA — National Association of State Utility Consumer Advocates (state advocate network)",
                     "https://www.nasuca.org/"),
    "nclc":         ("National Consumer Law Center — Utility Rights & Affordability",
                     "https://www.nclc.org/topic/equitable-utility-service/"),
    "kleinman":     ("Kleinman Center for Energy Policy (UPenn) — data-center & ratepayer policy research",
                     "https://kleinmanenergy.upenn.edu/"),
    "whyy_dc":      ("WHYY — Pennsylvania data-center electricity cost & ratepayer coverage",
                     "https://whyy.org/articles/pennsylvania-electricity-costs-data-centers/"),
    # --- BNEF 194 GW forecast (July 2026) ---
    "btm_gas":      ("Natural Gas Intelligence — On-site natural gas generation gains favor with hyperscalers (2026)",
                     "https://naturalgasintel.com/news/on-site-natural-gas-generation-gains-favor-with-hyperscalers-as-bridge-to-grid/"),
    # ── Health risks module ──────────────────────────────────────────── #
    "unpaid_toll":  ("Han, Wu, Li, Wierman & Ren — The Unpaid Toll: Quantifying the Public Health Impact of AI (arXiv:2412.06288, UC Riverside/Caltech, 2024)",
                     "https://arxiv.org/abs/2412.06288"),
    "siddik_2021":  ("Siddik, Shehabi & Marston — The environmental footprint of data centers in the United States (Environmental Research Letters, 2021)",
                     "https://iopscience.iop.org/article/10.1088/1748-9326/abfba1"),
    "lei_masanet_2022": ("Lei & Masanet — Climate- and technology-specific PUE and WUE estimations for U.S. data centers using a hybrid statistical and thermodynamics-based approach (Resources, Conservation and Recycling 182, 2022)",
                     "https://doi.org/10.1016/j.resconrec.2022.106323"),
    "wri_aqueduct": ("World Resources Institute — Aqueduct 4.0 Water Risk Atlas (baseline water stress by basin/state)",
                     "https://www.wri.org/aqueduct"),
    "who_noise":    ("WHO Europe — Environmental Noise Guidelines: noise & cardiovascular/metabolic mechanisms (2018)",
                     "https://www.who.int/europe/publications/i/item/WHO-EURO-2018-3009-42767-59666"),
    "eea_noise":    ("European Environment Agency — Health risks caused by environmental noise in Europe (2020)",
                     "https://www.eea.europa.eu/en/analysis/publications/health-risks-caused-by-environmental-noise-in-europe"),
    "ama_light":    ("American Medical Association — Council on Science & Public Health report on light pollution & nighttime lighting (2012 policy)",
                     "https://www.ama-assn.org/sites/ama-assn.org/files/corp/media-browser/public/about-ama/councils/Council%20Reports/council-on-science-public-health/a12-csaph4-lightpollution-summary.pdf"),
    "ehp_health":   ("Environmental Health Project — The Health Risks of Data Centers (infographic, 2026)",
                     "https://www.environmentalhealthproject.org/_files/ugd/a9ce25_3c3574ea12324c65909d308c3a716e56.pdf"),
    # --- Closest-neighbor protections (property values, buyouts, eminent domain) ---
    "mason_buyout": ("WCHS — Nscale's voluntary 'Good Neighbors' buyout of 53 homes beside the Monarch campus, Mason County WV (Jun 2026)",
                     "https://wchstv.com/news/local/voluntary-buyout-offers-rolled-out-for-meadowlands-estates-homes-near-data-center"),
    "ashburn_buyout": ("NBC4 Washington — Loudoun County / Ashburn homeowners report ~$4M buyout offers from data center developers",
                     "https://www.nbcwashington.com/news/local/northern-virginia/data-center-expansion-loudoun-county-homeowners-buyout-offers/"),
    "ga_eminent":   ("Fortune — Georgia Power eminent domain for data-center transmission; opening offers at 125% of appraised value (Jul 2026)",
                     "https://fortune.com/2026/07/26/georgia-power-utility-company-eminent-domain-grid-expansion-data-center/"),
    "nuisance_law": ("Windham Law — damages recoverable in a data-center nuisance suit (plaintiffs' practice summary, not a neutral authority — read it for the categories, not the odds)",
                     "https://windhamlaw.com/what-damages-can-you-recover-in-a-data-center-nuisance-lawsuit/"),
}

# Shares outstanding (billions, all classes) for live market-cap = price ×
# shares. Prices come live from Yahoo Finance; share counts change slowly
# (buybacks/issuance ~1–3%/yr) so they're maintained here from each company's
# most recent 10-Q cover. Used only for the Corporate Profiles cards.
# Last reviewed FY2025 filings.
SHARES_OUTSTANDING = {
    "MSFT": 7.43, "GOOGL": 12.05, "NVDA": 24.36, "AMZN": 10.62,
    "META": 2.53, "AMD": 1.62, "VRT": 0.381, "CEG": 0.313,
    "SMCI": 0.596, "ORCL": 2.80, "EQIX": 0.0965, "DLR": 0.336,
}

# --------------------------------------------------------------------------- #
# GOOGLE 2026 ENVIRONMENTAL REPORT DATA (FY2025)
# Source: Google 2026 Environmental Report — first-party, third-party limited
# assurance by KPMG. All figures for FY2025 unless noted.
# PDF: https://storage.googleapis.com/gweb-mobius-cdn/sustainability/uploads/
#      7f477eb723fe0c23d03f94b90a08882b9f28187d.pdf
# --------------------------------------------------------------------------- #

# Electricity consumption (MWh) — data centers only, 2021–2025
GOOGLE_DC_ELECTRICITY = pd.DataFrame([
    {"year": 2021, "dc_mwh": 17_429_800, "total_mwh": 18_058_300},
    {"year": 2022, "dc_mwh": 20_616_500, "total_mwh": 21_586_400},
    {"year": 2023, "dc_mwh": 23_980_800, "total_mwh": 24_994_000},
    {"year": 2024, "dc_mwh": 30_637_100, "total_mwh": 31_713_900},
    {"year": 2025, "dc_mwh": 42_415_800, "total_mwh": 43_586_600},
])

# GHG emissions (tCO2e) — operational scope 1+2 (market-based) and total
# ambition-based, 2019–2025
GOOGLE_GHG = pd.DataFrame([
    {"year": 2019, "scope1": 65_300,  "scope2_market": 788_200,  "scope2_location": 5_173_000,  "total_ambition": 8_002_500},
    {"year": 2020, "scope1": 50_200,  "scope2_market": 921_200,  "scope2_location": 5_845_000,  "total_ambition": 7_152_400},
    {"year": 2021, "scope1": 57_600,  "scope2_market": 1_769_400,"scope2_location": 6_498_700,  "total_ambition": 8_462_000},
    {"year": 2022, "scope1": 89_400,  "scope2_market": 2_430_200,"scope2_location": 7_963_700,  "total_ambition": 9_558_600},
    {"year": 2023, "scope1": 75_100,  "scope2_market": 3_288_000,"scope2_location": 9_085_700,  "total_ambition": 10_906_100},
    {"year": 2024, "scope1": 71_700,  "scope2_market": 2_898_600,"scope2_location": 11_067_100, "total_ambition": 12_233_300},
    {"year": 2025, "scope1": 86_100,  "scope2_market": 2_815_000,"scope2_location": 15_148_700, "total_ambition": 14_473_100},
])

# Water use (million gallons) 2021–2025
GOOGLE_WATER = pd.DataFrame([
    {"year": 2021, "withdrawal": 6_297,  "discharge": 1_735, "consumption": 4_562},
    {"year": 2022, "withdrawal": 7_600,  "discharge": 2_035, "consumption": 5_565},
    {"year": 2023, "withdrawal": 8_653,  "discharge": 2_301, "consumption": 6_352},
    {"year": 2024, "withdrawal": 11_011, "discharge": 2_876, "consumption": 8_135},
    {"year": 2025, "withdrawal": 14_689, "discharge": 3_820, "consumption": 10_869},
])

# Fleet-wide average PUE 2021–2025
GOOGLE_PUE_FLEET = pd.DataFrame([
    {"year": 2021, "pue": 1.10},
    {"year": 2022, "pue": 1.10},
    {"year": 2023, "pue": 1.10},
    {"year": 2024, "pue": 1.09},
    {"year": 2025, "pue": 1.09},
])

# Per-campus PUE 2025 (US locations from the report)
GOOGLE_PUE_SITES = [
    # location, state/country, pue_2025
    ("Berkeley County, SC",        "US", 1.09),
    ("Bristol, VA",                "US", 1.09),
    ("Central Ohio (Lancaster), OH","US", 1.04),
    ("Columbus, OH",               "US", 1.06),
    ("Council Bluffs, IA (1st)",   "US", 1.11),
    ("Council Bluffs, IA (2nd)",   "US", 1.08),
    ("The Dalles, OR (1st)",       "US", 1.10),
    ("The Dalles, OR (2nd)",       "US", 1.06),
    ("Douglas County, GA",         "US", 1.09),
    ("Henderson, NV",              "US", 1.09),
    ("Jackson County, AL",         "US", 1.10),
    ("Lenoir, NC",                 "US", 1.10),
    ("Loudoun County, VA (1st)",   "US", 1.08),
    ("Loudoun County, VA (2nd)",   "US", 1.08),
    ("Mayes County, OK",           "US", 1.12),
    ("Midlothian, TX",             "US", 1.10),
    ("Montgomery County, TN",      "US", 1.09),
    ("New Albany, OH",             "US", 1.06),
    ("Omaha, NE",                  "US", 1.05),
    ("Papillion, NE",              "US", 1.09),
    ("Storey County, NV",          "US", 1.14),
    # International
    ("St. Ghislain, Belgium",      "Europe", 1.08),
    ("Quilicura, Chile",           "LatAm",  1.08),
    ("Fredericia, Denmark",        "Europe", 1.07),
    ("Hamina, Finland",            "Europe", 1.10),
    ("Dublin, Ireland",            "Europe", 1.08),
    ("Inzai, Japan",               "APAC",   1.12),
    ("Eemshaven, Netherlands",     "Europe", 1.07),
    ("Singapore (1st)",            "APAC",   1.12),
    ("Singapore (2nd)",            "APAC",   1.14),
    ("Changhua County, Taiwan",    "APAC",   1.13),
]
GOOGLE_PUE_SITES_DF = pd.DataFrame(
    GOOGLE_PUE_SITES, columns=["location", "region", "pue_2025"])

# Carbon-free energy % by US grid region (hourly matching, 2025)
GOOGLE_CFE_BY_GRID = [
    # grid, google_cfe_pct, contracted_pct, consumed_grid_pct, grid_cfe_pct
    ("Arizona Salt River Project (SRP)",       86, 73, 13, 56),
    ("Bonneville Power Administration (BPA)",  83,  0, 83, 84),
    ("Duke Energy Carolinas (DUKE)",           65, 18, 47, 57),
    ("ERCOT (Texas)",                          83, 73, 10, 46),
    ("MISO (Midwest)",                         88, 83,  5, 36),
    ("NV Energy (NVE)",                        65, 55, 10, 32),
    ("PJM (Mid-Atlantic)",                     57, 29, 28, 40),
    ("South Carolina (SC)",                    31,  8, 23, 25),
    ("Southern Company (SOCO)",                42, 14, 28, 33),
    ("Southwest Power Pool (SPP)",             84, 77,  7, 47),
    ("Tennessee Valley Authority (TVA)",       58, 20, 38, 47),
]
GOOGLE_CFE_BY_GRID_DF = pd.DataFrame(
    GOOGLE_CFE_BY_GRID,
    columns=["grid", "google_cfe", "contracted_cfe", "consumed_grid_cfe", "grid_cfe"])

# Key 2025 headline metrics (for callout cards)
GOOGLE_2025_HEADLINE = {
    "dc_twh": 42.4,              # data-center electricity consumption TWh
    "total_twh": 43.6,           # total company electricity TWh
    "yoy_electricity_growth_pct": 37,  # year-on-year % increase
    "fleet_pue": 1.09,
    "global_cfe_pct": 65,        # hourly CFE match
    "scope2_market_tco2e": 2_815_000,
    "scope2_location_tco2e": 15_148_700,
    "total_ambition_tco2e": 14_473_100,
    "water_consumption_mgal": 10_869,  # million gallons
    "water_dc_mgal": 10_523,           # data centers only
    "clean_energy_gw_signed": 12,      # GW of new clean energy signed in 2025
    "avoided_tco2e_m": 58,             # million tCO2e avoided across operations
    "gemini_energy_improvement_x": 33, # 33x energy reduction median text prompt
    "gemini_carbon_improvement_x": 44, # 44x carbon reduction median text prompt
    "water_replenished_pct": 78,       # freshwater replenishment %
}

# --------------------------------------------------------------------------- #
# META 2025 ENVIRONMENTAL DATA INDEX (FY2024)
# Source: Meta 2025 Environmental Data Index — sustainability.atmeta.com
# PDF: https://sustainability.atmeta.com/wp-content/uploads/2025/10/
#      Meta_2025-Environmental-Data-Index.pdf
# All figures for FY2024 unless noted.
# --------------------------------------------------------------------------- #

# Electricity consumption (MWh) total by year, 2020-2024
META_DC_ELECTRICITY = pd.DataFrame([
    {"year": 2020, "dc_mwh": 6_966_000,  "total_mwh": 7_170_000},
    {"year": 2021, "dc_mwh": 9_117_122,  "total_mwh": 9_420_839},
    {"year": 2022, "dc_mwh": 11_167_416, "total_mwh": 11_508_131},
    {"year": 2023, "dc_mwh": 14_975_435, "total_mwh": 15_325_314},
    {"year": 2024, "dc_mwh": 18_061_781, "total_mwh": 18_423_634},
])

# Electricity by campus (MWh, 2024) — owned data centers
META_DC_CAMPUS_ELECTRICITY = pd.DataFrame([
    {"campus": "Altoona, IA",          "region": "US",      "mwh_2024": 1_585_392},
    {"campus": "Clonee, Ireland",       "region": "Europe",  "mwh_2024": 1_076_961},
    {"campus": "DeKalb, IL",            "region": "US",      "mwh_2024":   372_339},
    {"campus": "Eagle Mountain, UT",    "region": "US",      "mwh_2024": 1_115_619},
    {"campus": "Forest City, NC",       "region": "US",      "mwh_2024":   535_555},
    {"campus": "Fort Worth, TX",        "region": "US",      "mwh_2024": 1_109_004},
    {"campus": "Gallatin, TN",          "region": "US",      "mwh_2024":   359_730},
    {"campus": "Henrico, VA",           "region": "US",      "mwh_2024":   948_859},
    {"campus": "Huntsville, AL",        "region": "US",      "mwh_2024":   865_803},
    {"campus": "Kansas City, MO",       "region": "US",      "mwh_2024":    22_963},
    {"campus": "Los Lunas, NM",         "region": "US",      "mwh_2024": 1_143_067},
    {"campus": "Luleå, Sweden",         "region": "Europe",  "mwh_2024":   468_809},
    {"campus": "Mesa, AZ",              "region": "US",      "mwh_2024":    24_657},
    {"campus": "New Albany, OH",        "region": "US",      "mwh_2024":   521_217},
    {"campus": "Odense, Denmark",       "region": "Europe",  "mwh_2024":   569_374},
    {"campus": "Prineville, OR",        "region": "US",      "mwh_2024": 1_728_291},
    {"campus": "Sarpy, NE",             "region": "US",      "mwh_2024": 1_258_239},
    {"campus": "Stanton Springs, GA",   "region": "US",      "mwh_2024": 1_184_380},
    {"campus": "Leased facilities",     "region": "Various", "mwh_2024": 3_069_504},
])

# GHG emissions (tCO2e) 2020-2024 — scope 1, scope 2 market/location, scope 3 total
META_GHG = pd.DataFrame([
    {"year": 2020, "scope1": 126_000, "scope2_market":  9_000, "scope2_location": 2_718_000, "scope3": 5_091_000},
    {"year": 2021, "scope1":  97_000, "scope2_market":  2_487, "scope2_location": 3_080_194, "scope3": 5_772_583},
    {"year": 2022, "scope1": 126_000, "scope2_market":    273, "scope2_location": 3_921_611, "scope3": 8_466_264},
    {"year": 2023, "scope1":  86_000, "scope2_market":  1_658, "scope2_location": 5_141_350, "scope3": 7_445_621},
    {"year": 2024, "scope1":  97_000, "scope2_market":  1_358, "scope2_location": 5_967_348, "scope3": 8_151_769},
])

# Water withdrawal by campus (megaliters, 2024)
META_WATER_CAMPUS = pd.DataFrame([
    {"campus": "Altoona, IA",        "region": "US",      "withdrawal_ml": 242, "consumption_ml": None},
    {"campus": "Clonee, Ireland",     "region": "Europe",  "withdrawal_ml": 571, "consumption_ml": None},
    {"campus": "DeKalb, IL",          "region": "US",      "withdrawal_ml": 105, "consumption_ml": None},
    {"campus": "Eagle Mountain, UT",  "region": "US",      "withdrawal_ml": 133, "consumption_ml": None},
    {"campus": "Forest City, NC",     "region": "US",      "withdrawal_ml":  16, "consumption_ml": None},
    {"campus": "Fort Worth, TX",      "region": "US",      "withdrawal_ml": 311, "consumption_ml": None},
    {"campus": "Gallatin, TN",        "region": "US",      "withdrawal_ml": 205, "consumption_ml": None},
    {"campus": "Henrico, VA",         "region": "US",      "withdrawal_ml":  92, "consumption_ml": None},
    {"campus": "Huntsville, AL",      "region": "US",      "withdrawal_ml": 209, "consumption_ml": None},
    {"campus": "Los Lunas, NM",       "region": "US",      "withdrawal_ml": 252, "consumption_ml": None},
    {"campus": "Luleå, Sweden",       "region": "Europe",  "withdrawal_ml":  29, "consumption_ml": None},
    {"campus": "New Albany, OH",      "region": "US",      "withdrawal_ml":  86, "consumption_ml": None},
    {"campus": "Odense, Denmark",     "region": "Europe",  "withdrawal_ml": 292, "consumption_ml": None},
    {"campus": "Prineville, OR",      "region": "US",      "withdrawal_ml": 328, "consumption_ml": None},
    {"campus": "Sarpy, NE",           "region": "US",      "withdrawal_ml": 142, "consumption_ml": None},
    {"campus": "Stanton Springs, GA", "region": "US",      "withdrawal_ml": 146, "consumption_ml": None},
])

# Global water totals (megaliters) 2020-2024
META_WATER = pd.DataFrame([
    {"year": 2020, "withdrawal_ml": 3_726, "consumption_ml": 2_202, "discharge_ml": 1_524},
    {"year": 2021, "withdrawal_ml": 5_043, "consumption_ml": 2_569, "discharge_ml": 2_473},
    {"year": 2022, "withdrawal_ml": 4_893, "consumption_ml": 2_638, "discharge_ml": 2_254},
    {"year": 2023, "withdrawal_ml": 5_274, "consumption_ml": 3_078, "discharge_ml": 2_196},
    {"year": 2024, "withdrawal_ml": 5_637, "consumption_ml": 3_123, "discharge_ml": 2_514},
])

# Fleet PUE and WUE 2020-2024
META_EFFICIENCY = pd.DataFrame([
    {"year": 2020, "pue": 1.10, "wue": 0.30},
    {"year": 2021, "pue": 1.09, "wue": 0.26},
    {"year": 2022, "pue": 1.08, "wue": 0.20},
    {"year": 2023, "pue": 1.08, "wue": 0.18},
    {"year": 2024, "pue": 1.08, "wue": 0.19},
])

# Key 2024 headline metrics
META_2024_HEADLINE = {
    "dc_twh": 18.1,              # data center electricity TWh
    "total_twh": 18.4,           # total electricity TWh
    "fleet_pue": 1.08,
    "fleet_wue": 0.19,           # liters per kWh IT load
    "scope2_market_tco2e": 1_358,
    "scope2_location_tco2e": 5_967_348,
    "scope3_tco2e": 8_151_769,
    "water_withdrawal_ml": 5_637,  # megaliters
    "water_consumption_ml": 3_123,
    "water_restoration_ml": 6_017, # ml restored via stewardship projects
    "renewable_match_pct": 100,
    "leed_gold_pct": 100,          # data centers covered by LEED Gold or ISO 50001
    "as_of": "FY2024",
}

# --------------------------------------------------------------------------- #
# STATE-LEVEL DATA CENTER DATA

# Source: ElectricChoice.com/datacenters (updated July 2026; CC-BY 4.0)
# Underlying cites: LBNL-2001637 (Dec 2024), EIA, EPRINC, DCE/industry reports.
# dc = active facility count; twh = annual TWh consumed; upcoming = major
# projects under construction or announced in that state.
# --------------------------------------------------------------------------- #
STATE_DC_NATIONAL = {
    "active_facilities": 4500,
    "twh_annual": 176,
    "pct_us_power": 4.4,
    "under_construction": 700,
    "homes_equivalent_millions": 16,
    "as_of": "2026",
}

STATE_DC_ROWS = [
    # state, abbrev, dc_count, twh_year, major_hubs, upcoming
    ("Alabama",             "AL",  35,  0.6,  "Birmingham, Huntsville",                                                             False),
    ("Alaska",              "AK",   5,  0.1,  "Anchorage",                                                                         False),
    ("Arizona",             "AZ", 190, 10.5,  "Phoenix (Mesa, Goodyear, Chandler) — Microsoft, Apple, Vantage, QTS, Iron Mountain",  True),
    ("Arkansas",            "AR",  15,  0.3,  "West Memphis — Google",                                                              True),
    ("California",          "CA", 321, 11.0,  "Silicon Valley, Los Angeles — Equinix, Digital Realty, CoreSite, Vantage",           False),
    ("Colorado",            "CO",  70,  1.8,  "Denver, Colorado Springs — Flexential, Viawest",                                     False),
    ("Connecticut",         "CT",  60,  1.0,  "Stamford, Hartford",                                                                 False),
    ("Delaware",            "DE",  22,  0.4,  "Wilmington",                                                                        False),
    ("Dist. of Columbia",   "DC",  12,  0.3,  "Washington D.C.",                                                                   False),
    ("Florida",             "FL", 135,  4.2,  "Miami, Tampa, Jacksonville — Equinix, Digital Realty, CyrusOne",                     False),
    ("Georgia",             "GA", 162,  9.0,  "Atlanta (Douglasville, Palmetto) — Switch, Google, Microsoft, QTS",                  True),
    ("Hawaii",              "HI",   8,  0.1,  "Honolulu",                                                                          False),
    ("Idaho",               "ID",  12,  0.2,  "Boise",                                                                             False),
    ("Illinois",            "IL", 244, 12.0,  "Chicago (Elk Grove Village, Aurora) — Microsoft, Equinix, Digital Realty, Meta",     False),
    ("Indiana",             "IN",  85,  2.0,  "Lebanon, La Porte, Indianapolis — Amazon ($15B), Meta ($10B), Microsoft ($1B)",      True),
    ("Iowa",                "IA", 115,  3.8,  "Des Moines, Altoona — Apple, Google, Meta",                                         False),
    ("Kansas",              "KS",  22,  0.4,  "Kansas City metro, Wichita",                                                        False),
    ("Kentucky",            "KY",  40,  0.6,  "Louisville, Lexington",                                                             False),
    ("Louisiana",           "LA",  30,  0.5,  "Richland Parish, Caddo & Bossier Parishes — Meta ($27B), Amazon ($12B), Hut 8",      True),
    ("Maine",               "ME",   8,  0.1,  "Portland",                                                                          False),
    ("Maryland",            "MD",  48,  0.9,  "Baltimore, Frederick",                                                               False),
    ("Massachusetts",       "MA",  58,  1.1,  "Boston, Holyoke, Cambridge",                                                        False),
    ("Michigan",            "MI",  62,  1.1,  "Detroit, Grand Rapids",                                                             False),
    ("Minnesota",           "MN",  78,  1.5,  "Minneapolis, Shakopee",                                                             False),
    ("Mississippi",         "MS",  20,  0.3,  "Madison County, Meridian — Amazon ($16B+), Compass ($10B)",                          True),
    ("Missouri",            "MO",  55,  1.2,  "Kansas City, St. Louis — Google ($2B)",                                             True),
    ("Montana",             "MT",  12,  0.2,  "Billings, Missoula",                                                                False),
    ("Nebraska",            "NE",  42,  2.1,  "Omaha, Lincoln — Google, Meta",                                                     False),
    ("Nevada",              "NV",  72,  2.8,  "Las Vegas (Henderson), Reno — Switch (SUPERNAP), Google, Apple",                     False),
    ("New Hampshire",       "NH",  14,  0.2,  "Manchester",                                                                        False),
    ("New Jersey",          "NJ",  95,  2.2,  "Secaucus, Piscataway (NYC Metro) — Equinix, Digital Realty",                        False),
    ("New Mexico",          "NM",  28,  1.6,  "Albuquerque, Los Lunas — Meta",                                                     False),
    ("New York",            "NY", 155,  4.5,  "NYC Metro, Buffalo — Equinix, DataBank, Digital Realty",                            False),
    ("North Carolina",      "NC", 115,  4.5,  "Charlotte, Research Triangle, Richmond County — Apple, Google, Amazon ($10B)",       True),
    ("North Dakota",        "ND",  18,  0.3,  "Fargo",                                                                             False),
    ("Ohio",                "OH", 203,  7.5,  "Columbus (New Albany), Hebron — Google, Meta, Amazon ($10B), Microsoft",             True),
    ("Oklahoma",            "OK",  38,  0.6,  "Oklahoma City, Tulsa",                                                              False),
    ("Oregon",              "OR", 148,  6.5,  "Hillsboro, Prineville, The Dalles — Apple, Meta, Google",                           False),
    ("Pennsylvania",        "PA",  98,  2.5,  "Salem Twp., Fairless Hills, Lancaster — Amazon ($20B), CoreWeave ($6B)",             True),
    ("Rhode Island",        "RI",   8,  0.2,  "Providence",                                                                        False),
    ("South Carolina",      "SC",  40,  0.6,  "Aiken County, Charleston — Meta ($800M)",                                           True),
    ("South Dakota",        "SD",  10,  0.1,  "Sioux Falls",                                                                       False),
    ("Tennessee",           "TN",  68,  1.8,  "Nashville, Memphis — Oracle ($1.5B), xAI ($1B+)",                                   False),
    ("Texas",               "TX", 413, 17.0,  "Dallas–Fort Worth, Austin, San Antonio, West Texas — Google ($40B), Meta, Stargate", True),
    ("Utah",                "UT",  48,  2.6,  "Salt Lake City, Bluffdale — Meta, Google",                                          False),
    ("Vermont",             "VT",   5,  0.1,  "Burlington",                                                                        False),
    ("Virginia",            "VA", 665, 24.0,  "Ashburn ('Data Center Alley'), Loudoun Co., Prince William — AWS, Microsoft, Google, Equinix", True),
    ("Washington",          "WA", 142,  4.2,  "Quincy, Seattle, Moses Lake — Microsoft, Amazon",                                   False),
    ("West Virginia",       "WV",   8,  0.1,  "Charleston",                                                                        False),
    ("Wisconsin",           "WI",  52,  0.9,  "Mount Pleasant, Milwaukee — Microsoft ($3.3B)",                                     True),
    ("Wyoming",             "WY",  18,  0.5,  "Cheyenne — Microsoft",                                                              False),
]
STATE_DC_DF = pd.DataFrame(
    STATE_DC_ROWS,
    columns=["state", "abbrev", "dc_count", "twh_year", "major_hubs", "upcoming"])

# Top 10 mega-projects under construction / announced (ElectricChoice 2026 + press).
MEGA_PROJECTS = [
    {"project": "Stargate",              "company": "OpenAI / Oracle / SoftBank", "location": "Abilene, TX",          "invest": "$100B+",  "capacity": "1+ GW",    "status": "Under Construction"},
    {"project": "West Texas campus",     "company": "Google",                    "location": "West Texas (3 sites)", "invest": "$40B",    "capacity": "multi-GW", "status": "Under Construction"},
    {"project": "Meta Hyperion",         "company": "Meta / Blue Owl",           "location": "Richland Parish, LA", "invest": "$27B",    "capacity": "2–5 GW",   "status": "Under Construction"},
    {"project": "Vantage Frontier",      "company": "Vantage Data Centers",      "location": "Shackelford Co., TX", "invest": "$25B",    "capacity": "1.4 GW",   "status": "Under Construction"},
    {"project": "AWS Mississippi",       "company": "Amazon (AWS)",              "location": "Mississippi",         "invest": "$25B",    "capacity": "multi-site","status": "Under Construction"},
    {"project": "xAI Colossus",          "company": "xAI",                       "location": "Memphis, TN",         "invest": "$20B",    "capacity": "~2 GW",    "status": "Under Construction"},
    {"project": "AWS Pennsylvania",      "company": "Amazon (AWS)",              "location": "Pennsylvania",        "invest": "$20B",    "capacity": "2+ GW",    "status": "Under Construction"},
    {"project": "EdgeCore Virginia",     "company": "EdgeCore",                  "location": "Louisa County, VA",   "invest": "$17B",    "capacity": "1.1+ GW",  "status": "Under Construction"},
    {"project": "AWS Northern Indiana",  "company": "Amazon (AWS)",              "location": "Northern Indiana",    "invest": "$15B",    "capacity": "2.4 GW",   "status": "Under Construction"},
    {"project": "QTS Cedar Rapids",      "company": "QTS Data Centers",          "location": "Cedar Rapids, IA",    "invest": "$10B",    "capacity": "GW-scale",  "status": "Under Construction"},
]
MEGA_PROJECTS_DF = pd.DataFrame(MEGA_PROJECTS)

# --------------------------------------------------------------------------- #
# EXECUTIVES — key leadership at data center operators & mega-project sponsors
# LinkedIn links use search URLs (always resolve) rather than guessed profile slugs.
# --------------------------------------------------------------------------- #

def _li(name, company):
    """LinkedIn people-search URL for a name + company."""
    q = f"{name} {company}".replace(" ", "+").replace("&", "%26")
    return f"https://www.linkedin.com/search/results/people/?keywords={q}"

EXECUTIVES = [
    # --- Google / Alphabet ---
    {"company": "Google",       "name": "Sundar Pichai",      "title": "CEO, Alphabet / Google",
     "category": "leadership", "focus": "Corporate strategy across Google, Cloud, DeepMind, and Waymo.",
     "linkedin": _li("Sundar Pichai", "Alphabet")},
    {"company": "Google",       "name": "Ruth Porat",         "title": "President & CIO, Alphabet",
     "category": "leadership", "focus": "Capital allocation and infrastructure investment.",
     "linkedin": _li("Ruth Porat", "Alphabet")},
    {"company": "Google",       "name": "Joe Kava",           "title": "VP, Global Data Centers",
     "category": "infrastructure", "focus": "Global data center design, construction, and operations.",
     "linkedin": _li("Joe Kava", "Google")},
    {"company": "Google",       "name": "Kate Brandt",        "title": "Chief Sustainability Officer",
     "category": "sustainability", "focus": "Circular economy, carbon-free energy, and sustainability goals.",
     "linkedin": _li("Kate Brandt", "Google")},
    {"company": "Google",       "name": "Michael Terrell",    "title": "Senior Director, Energy & Climate",
     "category": "sustainability", "focus": "Pioneered Google's 24/7 hourly Carbon-Free Energy (CFE) matching.",
     "linkedin": _li("Michael Terrell", "Google")},
    {"company": "Google",       "name": "Ben Townsend",       "title": "Global Head, Infrastructure Planning & Water Policy",
     "category": "infrastructure", "focus": "Site selection and cooling water sustainability policies.",
     "linkedin": _li("Ben Townsend", "Google")},
    # --- Meta ---
    {"company": "Meta",         "name": "Mark Zuckerberg",    "title": "CEO",
     "category": "leadership", "focus": "Corporate strategy and AI investment direction.",
     "linkedin": _li("Mark Zuckerberg", "Meta")},
    {"company": "Meta",         "name": "Susan Li",           "title": "CFO",
     "category": "leadership", "focus": "Capital expenditure and infrastructure finance.",
     "linkedin": _li("Susan Li", "Meta")},
    {"company": "Meta",         "name": "Rachel Peterson",    "title": "VP, Data Centers",
     "category": "infrastructure", "focus": "Global owned and leased data center physical infrastructure.",
     "linkedin": _li("Rachel Peterson", "Meta")},
    {"company": "Meta",         "name": "Urvi Parekh",        "title": "Head of Renewable Energy",
     "category": "sustainability", "focus": "Clean energy procurement (15+ GW contracted portfolio).",
     "linkedin": _li("Urvi Parekh", "Meta")},
    {"company": "Meta",         "name": "Blair Anderson",     "title": "Director, State & Local Public Policy",
     "category": "policy", "focus": "Governmental relations and community tax incentive negotiations.",
     "linkedin": _li("Blair Anderson", "Meta")},
    # --- Microsoft ---
    {"company": "Microsoft",    "name": "Satya Nadella",      "title": "Chairman & CEO",
     "category": "leadership", "focus": "Corporate strategy and Azure/AI investment.",
     "linkedin": _li("Satya Nadella", "Microsoft")},
    {"company": "Microsoft",    "name": "Noelle Walsh",       "title": "CVP, Cloud Operations & Innovation",
     "category": "infrastructure", "focus": "Global Azure cloud infrastructure construction and operations.",
     "linkedin": _li("Noelle Walsh", "Microsoft")},
    # Left Microsoft for STACK, announced May 5 2026 — was Microsoft's VP of
    # Energy. Kept under STACK below; do not re-add him to Microsoft.
    {"company": "Microsoft",    "name": "Melanie Nakagawa",   "title": "Chief Sustainability Officer",
     "category": "sustainability", "focus": "Corporate climate and sustainability policies (carbon negative by 2030).",
     "linkedin": _li("Melanie Nakagawa", "Microsoft")},
    # --- Amazon (AWS) ---
    {"company": "Amazon (AWS)", "name": "Andy Jassy",         "title": "CEO, Amazon",
     "category": "leadership", "focus": "Corporate strategy and AWS investment.",
     "linkedin": _li("Andy Jassy", "Amazon")},
    {"company": "Amazon (AWS)", "name": "Matt Garman",        "title": "CEO, AWS",
     "category": "leadership", "focus": "AWS cloud and data center strategy.",
     "linkedin": _li("Matt Garman", "AWS")},
    {"company": "Amazon (AWS)", "name": "Kevin Miller",       "title": "VP, Global Data Centers",
     "category": "infrastructure", "focus": "Worldwide physical infrastructure design, build, and operations.",
     "linkedin": _li("Kevin Miller", "AWS")},
    {"company": "Amazon (AWS)", "name": "Chris Roe",          "title": "Director, Energy & Sustainable Operations",
     "category": "sustainability", "focus": "Clean power procurement and operational carbon reduction.",
     "linkedin": _li("Chris Roe", "AWS")},
    {"company": "Amazon (AWS)", "name": "Jenna Leiner",       "title": "Lead, Water Sustainability",
     "category": "sustainability", "focus": "Global water replenishment projects and dry-cooling upgrades.",
     "linkedin": _li("Jenna Leiner", "AWS")},
    # --- AI / neocloud ---
    {"company": "xAI (Colossus)", "name": "Elon Musk",       "title": "CEO, xAI",
     "category": "leadership", "focus": "xAI strategy and Colossus supercluster build-out.",
     "linkedin": _li("Elon Musk", "xAI")},
    {"company": "OpenAI · Oracle (Stargate)", "name": "Sam Altman", "title": "CEO, OpenAI",
     "category": "leadership", "focus": "OpenAI strategy and Stargate JV.",
     "linkedin": _li("Sam Altman", "OpenAI")},
    {"company": "OpenAI · Oracle (Stargate)", "name": "Larry Ellison", "title": "CTO & Chairman, Oracle",
     "category": "leadership", "focus": "Oracle cloud infrastructure and Stargate site development.",
     "linkedin": _li("Larry Ellison", "Oracle")},
    {"company": "OpenAI · Oracle (Stargate)", "name": "Masayoshi Son", "title": "CEO, SoftBank Group",
     "category": "leadership", "focus": "SoftBank capital commitment to Stargate JV.",
     "linkedin": _li("Masayoshi Son", "SoftBank")},
    {"company": "CoreWeave",    "name": "Michael Intrator",   "title": "CEO & Co-founder",
     "category": "leadership", "focus": "Corporate strategy and capital raises for GPU hosting.",
     "linkedin": _li("Michael Intrator", "CoreWeave")},
    {"company": "CoreWeave",    "name": "Brian Venturo",      "title": "Chief Strategy Officer & Co-founder",
     "category": "leadership", "focus": "Corporate strategy; was CTO until March 2024.",
     "linkedin": _li("Brian Venturo", "CoreWeave")},
    # --- Colocation / wholesale REITs ---
    {"company": "Digital Realty", "name": "Andy Power",       "title": "President & CEO",
     "category": "leadership", "focus": "Global wholesale data center development and leasing.",
     "linkedin": _li("Andy Power", "Digital Realty")},
    {"company": "Digital Realty", "name": "Chris Sharp",      "title": "CTO",
     "category": "infrastructure", "focus": "Platform architecture and interconnection strategy.",
     "linkedin": _li("Chris Sharp", "Digital Realty")},
    {"company": "Digital Realty", "name": "Aaron Binkley",    "title": "VP of Sustainability",
     "category": "sustainability", "focus": "Global environmental reporting, carbon reduction, and green tariffs.",
     "linkedin": _li("Aaron Binkley", "Digital Realty")},
    # Chad Williams (founder) no longer appears on QTS's leadership page; QTS
    # now lists co-CEOs. Removed rather than kept with a guessed title.
    {"company": "QTS",          "name": "Thomas A. \"Tag\" Greason", "title": "Co-Chief Executive Officer",
     "category": "leadership", "focus": "QTS strategy under Blackstone ownership.",
     "linkedin": _li("Tag Greason", "QTS Data Centers")},
    {"company": "QTS",          "name": "David Robey",        "title": "Co-Chief Executive Officer",
     "category": "leadership", "focus": "QTS operations and delivery under Blackstone ownership.",
     "linkedin": _li("David Robey", "QTS Data Centers")},
    {"company": "QTS",          "name": "Brian Herlihy",      "title": "Chief Energy Strategy Officer",
     "category": "sustainability", "focus": "Power procurement and grid strategy for QTS campuses.",
     "linkedin": _li("Brian Herlihy", "QTS Data Centers")},
    {"company": "QTS",          "name": "Theo Yedinsky",      "title": "Chief External Affairs Officer",
     "category": "policy", "focus": "Government relations and community engagement — the contact for siting disputes.",
     "linkedin": _li("Theo Yedinsky", "QTS Data Centers")},
    {"company": "Vantage",      "name": "Sureel Choksi",     "title": "President & CEO",
     "category": "leadership", "focus": "Vantage global expansion and hyperscale campus development.",
     "linkedin": _li("Sureel Choksi", "Vantage Data Centers")},
    {"company": "CyrusOne",     "name": "Eric Schwartz",     "title": "CEO",
     "category": "leadership", "focus": "CyrusOne strategy under KKR/GIP ownership.",
     "linkedin": _li("Eric Schwartz", "CyrusOne")},
    {"company": "Aligned",      "name": "Andrew Schaap",     "title": "CEO",
     "category": "leadership", "focus": "Adaptive data center design and Nvidia/BlackRock acquisition.",
     "linkedin": _li("Andrew Schaap", "Aligned Data Centers")},
    {"company": "Switch",       "name": "Rob Roy",           "title": "Founder & CEO",
     "category": "leadership", "focus": "Switch strategy under DigitalBridge ownership; designer of the Prime campuses.",
     "linkedin": _li("Rob Roy", "Switch")},
    # STACK runs regional CEOs, not one global CEO — name the right region.
    {"company": "Stack Infrastructure", "name": "Matt VanderZanden", "title": "CEO, STACK Americas",
     "category": "leadership", "focus": "US hyperscale campus development for STACK/Blue Owl.",
     "linkedin": _li("Matt VanderZanden", "Stack Infrastructure")},
    {"company": "Stack Infrastructure", "name": "Brian Cox",  "title": "Interim CEO, STACK EMEA",
     "category": "leadership", "focus": "STACK EMEA; was CEO of STACK Americas from 2018.",
     "linkedin": _li("Brian Cox", "Stack Infrastructure")},
    {"company": "Stack Infrastructure", "name": "Bobby Hollis", "title": "Chief Development Officer, STACK Americas",
     "category": "sustainability", "focus": "Site selection, preconstruction, and power strategy. Was Microsoft's VP of Energy until May 2026.",
     "linkedin": _li("Bobby Hollis", "Stack Infrastructure")},
    {"company": "EdgeConneX",   "name": "Randy Brouckman",   "title": "CEO",
     "category": "leadership", "focus": "Edge and hyperscale data center development.",
     "linkedin": _li("Randy Brouckman", "EdgeConneX")},
    {"company": "Equinix",      "name": "Adaire Fox-Martin", "title": "CEO",
     "category": "leadership", "focus": "Corporate strategy for the world's largest colocation provider.",
     "linkedin": _li("Adaire Fox-Martin", "Equinix")},
    {"company": "Equinix",      "name": "Christopher Wellise", "title": "VP, Global Sustainability",
     "category": "sustainability", "focus": "Green design, energy reporting, and circular hardware programs.",
     "linkedin": _li("Christopher Wellise", "Equinix")},
    {"company": "Core Scientific", "name": "Adam Sullivan",  "title": "CEO",
     "category": "leadership", "focus": "HPC/AI pivot and CoreWeave acquisition negotiations.",
     "linkedin": _li("Adam Sullivan", "Core Scientific")},
]
# Verification log — read off each company's OWN leadership page on the date
# shown. Keyed by (company, name). Kept separate from the rows above because
# it is provenance, not identity: a name/title is a claim, this is the receipt.
#
# A row absent from this map is NOT verified, and renders as "Unverified" in
# the UI. That is the honest state for most VP- and director-level people:
# no company publishes a leadership page that lists them, so there is no
# first-party source to check them against. Search results and third-party
# profiles do not count — the same rule the LOCAL_OFFICIALS rows follow.
_EXEC_VERIFIED_ON = "2026-07-29"
EXEC_VERIFIED = {
    ("Microsoft", "Satya Nadella"):        "https://news.microsoft.com/leadership/",
    ("Meta", "Mark Zuckerberg"):           "https://www.meta.com/media-gallery/executives/",
    ("Meta", "Susan Li"):                  "https://www.meta.com/media-gallery/executives/",
    ("Amazon (AWS)", "Andy Jassy"):        "https://www.aboutamazon.com/news/workplace/amazon-s-team-members",
    ("Amazon (AWS)", "Matt Garman"):       "https://www.aboutamazon.com/news/workplace/amazon-s-team-members",
    ("OpenAI · Oracle (Stargate)", "Masayoshi Son"): "https://group.softbank/en/about/officer",
    ("CoreWeave", "Michael Intrator"):     "https://www.coreweave.com/leadership/mike-intrator",
    ("CoreWeave", "Brian Venturo"):        "https://www.coreweave.com/leadership/brian-venturo",
    ("Digital Realty", "Andy Power"):      "https://www.digitalrealty.com/about/leadership",
    ("Digital Realty", "Chris Sharp"):     "https://www.digitalrealty.com/about/leadership",
    ("Vantage", "Sureel Choksi"):          "https://vantage-dc.com/leadership/",
    ("CyrusOne", "Eric Schwartz"):         "https://cyrusone.com/leadership/",
    ("Aligned", "Andrew Schaap"):          "https://aligneddc.com/team/andrew-schaap/",
    ("Switch", "Rob Roy"):                 "https://www.switch.com/executive-team/",
    ("EdgeConneX", "Randy Brouckman"):     "https://www.edgeconnex.com/company/management-team/randy-brouckman/",
    ("Equinix", "Adaire Fox-Martin"):      "https://investor.equinix.com/about-equinix/leadership-team",
    ("Core Scientific", "Adam Sullivan"):  "https://corescientific.com/about/leadership/",
    ("QTS", "Thomas A. \"Tag\" Greason"):  "https://q.com/company/leadership",
    ("QTS", "David Robey"):                "https://q.com/company/leadership",
    ("QTS", "Brian Herlihy"):              "https://q.com/company/leadership",
    ("QTS", "Theo Yedinsky"):              "https://q.com/company/leadership",
    ("Stack Infrastructure", "Matt VanderZanden"): "https://www.stackinfra.com/about/meet-the-team/",
    ("Stack Infrastructure", "Brian Cox"): "https://www.stackinfra.com/about/meet-the-team/",
    ("Stack Infrastructure", "Bobby Hollis"): "https://www.stackinfra.com/about/meet-the-team/",
}

EXECUTIVES_DF = pd.DataFrame(EXECUTIVES)
EXECUTIVES_DF["verified"] = [
    _EXEC_VERIFIED_ON if (c, n) in EXEC_VERIFIED else None
    for c, n in zip(EXECUTIVES_DF["company"], EXECUTIVES_DF["name"])]
EXECUTIVES_DF["verified_source"] = [
    EXEC_VERIFIED.get((c, n))
    for c, n in zip(EXECUTIVES_DF["company"], EXECUTIVES_DF["name"])]

# --------------------------------------------------------------------------- #
# STATE PUBLIC UTILITY COMMISSIONS (PUCs) — 50 states + DC
# The bodies that approve utility rate cases, large-load tariffs, and
# interconnection rules — the real decision-makers when data centers
# affect residential electricity rates.
# --------------------------------------------------------------------------- #

STATE_PUCS = [
    {"state": "Alabama",        "abbrev": "AL", "name": "Alabama Public Service Commission",
     "website": "https://psc.alabama.gov/", "complaint": "https://psc.alabama.gov/file-a-complaint/"},
    {"state": "Alaska",         "abbrev": "AK", "name": "Regulatory Commission of Alaska",
     "website": "https://rca.alaska.gov/", "complaint": "https://rca.alaska.gov/RCAWeb/ForConsumers/SubmitInformalComplaint.aspx"},
    {"state": "Arizona",        "abbrev": "AZ", "name": "Arizona Corporation Commission",
     "website": "https://www.azcc.gov/", "complaint": "https://www.azcc.gov/utilities/consumer-services"},
    {"state": "Arkansas",       "abbrev": "AR", "name": "Arkansas Public Service Commission",
     "website": "https://apsc.arkansas.gov/", "complaint": "https://apsc.arkansas.gov/filing-a-complaint/"},
    {"state": "California",     "abbrev": "CA", "name": "California Public Utilities Commission",
     "website": "https://www.cpuc.ca.gov/", "complaint": "https://www.cpuc.ca.gov/consumer-support/file-a-complaint"},
    {"state": "Colorado",       "abbrev": "CO", "name": "Colorado Public Utilities Commission",
     "website": "https://puc.colorado.gov/", "complaint": "https://puc.colorado.gov/for-consumers"},
    {"state": "Connecticut",    "abbrev": "CT", "name": "Connecticut Public Utilities Regulatory Authority",
     "website": "https://portal.ct.gov/pura", "complaint": "https://portal.ct.gov/pura/consumer-services"},
    {"state": "Delaware",       "abbrev": "DE", "name": "Delaware Public Service Commission",
     "website": "https://depsc.delaware.gov/", "complaint": "https://depsc.delaware.gov/customer-assistance/"},
    {"state": "District of Columbia", "abbrev": "DC", "name": "DC Public Service Commission",
     "website": "https://dcpsc.org/", "complaint": "https://complaints.dcpsc.dc.gov/en-US/"},
    {"state": "Florida",        "abbrev": "FL", "name": "Florida Public Service Commission",
     "website": "https://www.psc.state.fl.us/", "complaint": "https://www.psc.state.fl.us/ConsumerAssistance"},
    {"state": "Georgia",        "abbrev": "GA", "name": "Georgia Public Service Commission",
     "website": "https://psc.ga.gov/", "complaint": "https://psc.ga.gov/services-resources/file-consumer-complaint/"},
    {"state": "Hawaii",         "abbrev": "HI", "name": "Hawaii Public Utilities Commission",
     "website": "https://puc.hawaii.gov/", "complaint": "https://cca.hawaii.gov/dca/filing-a-complaint/"},
    {"state": "Idaho",          "abbrev": "ID", "name": "Idaho Public Utilities Commission",
     "website": "https://puc.idaho.gov/", "complaint": "https://puc.idaho.gov/Form/ConsumerAssistance"},
    {"state": "Illinois",       "abbrev": "IL", "name": "Illinois Commerce Commission",
     "website": "https://www.icc.illinois.gov/", "complaint": "https://www.icc.illinois.gov/complaints/"},
    {"state": "Indiana",        "abbrev": "IN", "name": "Indiana Utility Regulatory Commission",
     "website": "https://www.in.gov/iurc/", "complaint": "https://www.in.gov/iurc/customer-assistance/"},
    {"state": "Iowa",           "abbrev": "IA", "name": "Iowa Utilities Commission",
     "website": "https://iuc.iowa.gov/", "complaint": "https://iuc.iowa.gov/customer-assistance/how-do-i-file-utility-complaint"},
    {"state": "Kansas",         "abbrev": "KS", "name": "Kansas Corporation Commission",
     "website": "https://kcc.ks.gov/", "complaint": "https://puc.kcc.ks.gov/complaint/"},
    {"state": "Kentucky",       "abbrev": "KY", "name": "Kentucky Public Service Commission",
     "website": "https://psc.ky.gov/", "complaint": "https://psc.ky.gov/agencies/psc/consumer/complaint.aspx"},
    {"state": "Louisiana",      "abbrev": "LA", "name": "Louisiana Public Service Commission",
     "website": "https://www.lpsc.louisiana.gov/", "complaint": "https://www.lpsc.louisiana.gov/Consumers"},
    {"state": "Maine",          "abbrev": "ME", "name": "Maine Public Utilities Commission",
     "website": "https://www.maine.gov/mpuc/", "complaint": "https://www.maine.gov/mpuc/consumer-assistance"},
    {"state": "Maryland",       "abbrev": "MD", "name": "Maryland Public Service Commission",
     "website": "https://www.psc.state.md.us/", "complaint": "https://www.psc.state.md.us/electricity/file-a-complaint/"},
    {"state": "Massachusetts",  "abbrev": "MA", "name": "Massachusetts Department of Public Utilities",
     "website": "https://www.mass.gov/orgs/department-of-public-utilities", "complaint": "https://www.mass.gov/how-to/file-a-complaint-involving-a-gas-electric-or-water-company"},
    {"state": "Michigan",       "abbrev": "MI", "name": "Michigan Public Service Commission",
     "website": "https://www.michigan.gov/mpsc", "complaint": "https://www.michigan.gov/mpsc/consumer/complaints"},
    {"state": "Minnesota",      "abbrev": "MN", "name": "Minnesota Public Utilities Commission",
     "website": "https://mn.gov/puc/", "complaint": "https://mn.gov/puc/consumers/help/complaints/"},
    {"state": "Mississippi",    "abbrev": "MS", "name": "Mississippi Public Service Commission",
     "website": "https://www.psc.ms.gov/", "complaint": "https://ctsportal.psc.ms.gov/portal/"},
    {"state": "Missouri",       "abbrev": "MO", "name": "Missouri Public Service Commission",
     "website": "https://psc.mo.gov/", "complaint": "https://psc.mo.gov/General/Submit_A_Complaint"},
    {"state": "Montana",        "abbrev": "MT", "name": "Montana Public Service Commission",
     "website": "https://psc.mt.gov/", "complaint": "https://psc.mt.gov/Consumers/Request-Assistance"},
    {"state": "Nebraska",       "abbrev": "NE", "name": "Nebraska Power Review Board",
     "website": "https://powerreview.nebraska.gov/", "complaint": ""},
    {"state": "Nevada",         "abbrev": "NV", "name": "Public Utilities Commission of Nevada",
     "website": "https://puc.nv.gov/", "complaint": "https://puc.nv.gov/FAQ/Resolving_Disputes/"},
    {"state": "New Hampshire",  "abbrev": "NH", "name": "New Hampshire Public Utilities Commission",
     "website": "https://www.puc.nh.gov/", "complaint": "https://www.energy.nh.gov/rules-and-regulatory/proceedings/complaint-proceedings"},
    {"state": "New Jersey",     "abbrev": "NJ", "name": "New Jersey Board of Public Utilities",
     "website": "https://www.nj.gov/bpu/", "complaint": "https://www.nj.gov/bpu/assistance/complaints/"},
    {"state": "New Mexico",     "abbrev": "NM", "name": "New Mexico Public Regulation Commission",
     "website": "https://www.prc.nm.gov/", "complaint": "https://www.prc.nm.gov/consumer-relations/file-a-complaint/"},
    {"state": "New York",       "abbrev": "NY", "name": "New York Public Service Commission",
     "website": "https://www.dps.ny.gov/", "complaint": "https://dps.ny.gov/file-complaint"},
    {"state": "North Carolina", "abbrev": "NC", "name": "North Carolina Utilities Commission",
     "website": "https://www.ncuc.gov/", "complaint": "https://www.ncuc.gov/consumer/consumer.html"},
    {"state": "North Dakota",   "abbrev": "ND", "name": "North Dakota Public Service Commission",
     "website": "https://www.psc.nd.gov/", "complaint": "https://www.psc.nd.gov/contact"},
    {"state": "Ohio",           "abbrev": "OH", "name": "Public Utilities Commission of Ohio",
     "website": "https://puco.ohio.gov/", "complaint": "https://puco.ohio.gov/wps/portal/gov/puco/help-center"},
    {"state": "Oklahoma",       "abbrev": "OK", "name": "Oklahoma Corporation Commission",
     "website": "https://oklahoma.gov/occ.html", "complaint": "https://oklahoma.gov/occ/divisions/public-utility/consumer-services.html"},
    {"state": "Oregon",         "abbrev": "OR", "name": "Oregon Public Utility Commission",
     "website": "https://www.oregon.gov/puc/", "complaint": "https://www.oregon.gov/puc/Pages/consumer-complaint.aspx"},
    {"state": "Pennsylvania",   "abbrev": "PA", "name": "Pennsylvania Public Utility Commission",
     "website": "https://www.puc.pa.gov/", "complaint": "https://www.puc.pa.gov/complaints/"},
    {"state": "Rhode Island",   "abbrev": "RI", "name": "Rhode Island Public Utilities Commission",
     "website": "https://ripuc.ri.gov/", "complaint": "https://ripuc.ri.gov/consumer-information/how-file-complaint"},
    {"state": "South Carolina", "abbrev": "SC", "name": "Public Service Commission of South Carolina",
     "website": "https://psc.sc.gov/", "complaint": "https://psc.sc.gov/consumer-info/file-complaint"},
    {"state": "South Dakota",   "abbrev": "SD", "name": "South Dakota Public Utilities Commission",
     "website": "https://puc.sd.gov/", "complaint": "https://puc.sd.gov/Consumer/"},
    {"state": "Tennessee",      "abbrev": "TN", "name": "Tennessee Public Utility Commission",
     "website": "https://www.tn.gov/tpuc.html", "complaint": "https://www.tn.gov/tpuc/utility-complaint-resources.html"},
    {"state": "Texas",          "abbrev": "TX", "name": "Public Utility Commission of Texas",
     "website": "https://www.puc.texas.gov/", "complaint": "https://www.puc.texas.gov/consumer/complaint/"},
    {"state": "Utah",           "abbrev": "UT", "name": "Utah Public Service Commission",
     "website": "https://psc.utah.gov/", "complaint": "https://psc.utah.gov/complaint-process/"},
    {"state": "Vermont",        "abbrev": "VT", "name": "Vermont Public Utility Commission",
     "website": "https://puc.vermont.gov/", "complaint": "https://puc.vermont.gov/public-participation/complaints"},
    {"state": "Virginia",       "abbrev": "VA", "name": "Virginia State Corporation Commission",
     "website": "https://www.scc.virginia.gov/", "complaint": "https://www.scc.virginia.gov/consumers/public-utility/utility-complaints/"},
    {"state": "Washington",     "abbrev": "WA", "name": "Washington Utilities and Transportation Commission",
     "website": "https://www.utc.wa.gov/", "complaint": "https://www.utc.wa.gov/consumers/file-complaint"},
    {"state": "West Virginia",  "abbrev": "WV", "name": "West Virginia Public Service Commission",
     "website": "https://www.psc.state.wv.us/", "complaint": "https://www.psc.state.wv.us/Efile/Informal_Request/default.htm"},
    {"state": "Wisconsin",      "abbrev": "WI", "name": "Public Service Commission of Wisconsin",
     "website": "https://psc.wi.gov/", "complaint": "https://psc.wi.gov/Pages/ForConsumers/LogAComplaint.aspx"},
    {"state": "Wyoming",        "abbrev": "WY", "name": "Wyoming Public Service Commission",
     "website": "https://psc.wyo.gov/", "complaint": "https://psc.wyo.gov/home/file-a-complaint"},
]
STATE_PUCS_DF = pd.DataFrame(STATE_PUCS)

# --------------------------------------------------------------------------- #
# REGISTRY PROVENANCE — when each dataset was last known good, and how fast it
# rots. A resident who cites a number at a hearing and gets asked "as of when?"
# has to be able to answer; a stale figure they can't date destroys their
# credibility for everything else they say.
#
# The LOCAL_* registries carry per-row `source` + `as_of`, which is the better
# pattern. The registries below predate it and were compiled in bulk, so the
# honest unit of provenance is the dataset, not the row.
#
# RULE: `as_of=None` means "not recorded" — never a guess. A fabricated date is
# worse than no date, because it invites a citation the user can't defend. The
# renderer shows those as "verify before citing" rather than hiding them.
#
# churn = how quickly rows go wrong on their own:
#   low    — institutional facts (a PUC does not move)
#   medium — capital projects (announcements shift over quarters)
#   high   — contested/personnel facts (votes and job titles change weekly)
# --------------------------------------------------------------------------- #

REGISTRY_PROVENANCE = {
    "STATE_DC_DF": {
        "label": "State data center counts & electricity use",
        "as_of": "July 2026",
        "source": "electricchoice",
        "churn": "medium",
        "caveat": (
            "Facility counts vary by directory because each one draws the "
            "boundary differently — DataCenterMap lists 44 in Alabama where "
            "this table says 35, since it counts small network rooms "
            "alongside hyperscale campuses. Cite the TWh figure rather than "
            "the facility count when you can; it is the number that speaks "
            "to grid impact. Underlying load research is LBNL-2001637 "
            "(Dec 2024)."),
    },
    "STATE_GRID_PROFILES": {
        "label": "State residential rates, grid carbon & water stress",
        "as_of": "May 2026",
        "source": "eia_rates",
        "churn": "high",
        "caveat": (
            "**Rates** are EIA Electric Power Monthly Table 5.6.A, May 2026 — "
            "all 51 refreshed together from the published table rather than "
            "spot-edited, so cross-state comparisons stay valid. Note this is "
            "a single month, not an annual average: residential prices are "
            "seasonal, and May is a shoulder month, so summer-peaking states "
            "may run higher than shown.\n\n"
            "The refresh moved rates up a mean of 18.6%, and 48 of 51 "
            "jurisdictions (50 states plus D.C.) rose. The largest increases "
            "land in the PJM footprint and other "
            "data-center-dense markets — D.C. +61%, Illinois +55%, Maryland "
            "+36%, Ohio +36%, New York +34% — which is the correlation worth "
            "raising at a hearing, though correlation is all it is: this "
            "table cannot attribute a rate increase to a cause.\n\n"
            "**Carbon intensities** are state annual averages and move far "
            "more slowly than prices; they were not part of this refresh and "
            "remain broadly usable. **Water stress** is a coarse "
            "low/medium/high banding, not a basin-level assessment — a state "
            "marked 'low' can still contain a stressed watershed, which is "
            "the scale that actually decides a cooling permit."),
    },
    "MORATORIUMS_DF": {
        "label": "Moratorium & ban tracker",
        "as_of": "August 2026",
        "source": None,
        "churn": "high",
        "caveat": (
            "Illustrative rather than exhaustive — dozens of localities churn "
            "weekly, and this tracks the ones we have read a source for.\n\n"
            "**Each row carries its own provenance.** Rows showing a "
            "verification date link to the ordinance, the enacting body's own "
            "page, or a datable report of the vote, and were read on that "
            "date. Rows marked *unverified* came from bulk compilation and "
            "have not been checked against a primary source — the locality, "
            "the year, and the status may all be off. Verify one of those "
            "with the town clerk before citing it as precedent.\n\n"
            "**Expiry is derived, not asserted.** A row with a documented end "
            "date flips to *Expired* on its own once that date passes. A "
            "time-limited moratorium whose start date was never documented "
            "keeps showing as enacted — that is a known gap, not a claim that "
            "it is still in force. Moratoriums are also routinely extended, so "
            "an expiry date is the earliest it could have ended, not proof "
            "that it did."),
    },
    "MEGA_PROJECTS_DF": {
        "label": "Megaprojects under construction",
        "as_of": "2026",
        "source": "electricchoice",
        "churn": "medium",
        "caveat": (
            "Announced investment and capacity figures are the developer's "
            "own claims, repeated by trade press. Treat them as what the "
            "company said, not as verified build-out."),
    },
    "PROJECTS_DF": {
        "label": "Identified project tracker",
        "as_of": "August 2026",
        "source": None,
        "churn": "high",
        "caveat": (
            "A working set of identified proposals a community can track, not "
            "a census — most of the country's activity is not in here yet.\n\n"
            "**Each row carries its own provenance.** Rows showing a "
            "verification date link to reporting or the governing body's own "
            "record and were read on that date; rows marked *unverified* have "
            "no source on record — a lead to check, not a fact to cite.\n\n"
            "**Stage is derived, not asserted.** *Hearing scheduled*, "
            "*Awaiting decision*, *Approved* and *Withdrawn* are computed from "
            "each row's milestone dates on every rebuild, so a hearing date "
            "that has passed stops reading 'scheduled'. Hearings get moved and "
            "projects re-file under new names — treat a scheduled date as the "
            "earliest to act by, and confirm with the clerk before relying on "
            "it. Leads are mined into data/project_candidates.json and promoted "
            "here only after a human reads a primary source."),
    },
    "DC_SITES_DF": {
        "label": "Campus registry (operator / tenant / filing LLC)",
        "as_of": None,
        "source": "dc_ownership",
        "churn": "medium",
        "caveat": (
            "Each row carries its own attribution level — first-party rows "
            "come from the operator's own site, but colocation and REIT "
            "ownership was compiled from trade press and never passed an "
            "independent fact-check. Check the attribution column before "
            "citing a row."),
    },
    "EXECUTIVES_DF": {
        "label": "Executive directory",
        "as_of": "July 2026",
        "source": None,
        "churn": "high",
        "caveat": (
            "Only some rows are verified. Every row marked Verified was read "
            "off that company's own leadership page on the date shown, and "
            "links to it. Rows marked Unverified are mostly VP- and "
            "director-level people: no company publishes a page listing them, "
            "so there is no first-party source to check them against, and "
            "their titles may be a year or more out of date. Confirm any "
            "name before you put it in a letter or read it out at a hearing. "
            "The July 2026 sweep found five people whose entries were wrong, "
            "including one who had changed companies."),
    },
    "STATE_PUCS_DF": {
        "label": "Public utility commission directory",
        "as_of": None,
        "source": None,
        "churn": "low",
        "caveat": (
            "Commission names and complaint URLs are stable year to year, "
            "but no verification date is recorded. The linked site is "
            "authoritative if a URL has moved."),
    },
}

_CHURN_NOTE = {
    "low": "rarely changes",
    "medium": "changes over months",
    "high": "changes weekly — re-check before citing",
}

# How old a dataset may get before it is flagged, by churn rate.
_STALE_AFTER_MONTHS = {"low": 36, "medium": 18, "high": 9}

_MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"], start=1)}


def _as_of_months_old(as_of, today=None):
    """Months elapsed since a coarse `as_of` string, or None if unparseable.

    Handles the three shapes used above: "July 2026", "mid-2026", "2026".
    Coarse forms resolve to the middle//end of their period so the age is
    never overstated — an unflagged dataset is a smaller error than a
    falsely-flagged one.
    """
    if not as_of:
        return None
    text = as_of.strip().lower()
    year = None
    for token in text.replace("-", " ").split():
        if token.isdigit() and len(token) == 4:
            year = int(token)
    if year is None:
        return None
    month = next((v for k, v in _MONTHS.items() if k in text), None)
    if month is None:
        # "mid-YYYY" → June; bare "YYYY" → December (newest reading).
        month = 6 if "mid" in text else 12
    today = today or _dt.date.today()
    return (today.year - year) * 12 + (today.month - month)


def registry_provenance(key, today=None):
    """Provenance for a registry, or None if untracked.

    Returns a dict with a rendered `line` suitable for a caption, plus the
    raw fields, `months_old`, and a `stale` flag. `as_of=None` renders as an
    explicit warning, never a guess.
    """
    p = REGISTRY_PROVENANCE.get(key)
    if not p:
        return None
    out = dict(p)
    months = _as_of_months_old(p["as_of"], today=today)
    limit = _STALE_AFTER_MONTHS.get(p["churn"], 18)
    out["months_old"] = months
    # No recorded date is treated as stale: it cannot be shown to be current.
    out["stale"] = months is None or months > limit

    when = (f"As of {p['as_of']}" if p["as_of"]
            else "No verification date recorded")
    if months is not None and months >= 12:
        when += f" ({months // 12}y {months % 12}m ago)"
    elif months is not None and months >= 2:
        when += f" ({months}m ago)"
    out["line"] = f"{when} · {_CHURN_NOTE.get(p['churn'], '')}"
    return out


# --------------------------------------------------------------------------- #
# LIVE DATA CONFIGS
# --------------------------------------------------------------------------- #

MLENERGY_BASE = ("https://raw.githubusercontent.com/ml-energy/leaderboard/"
                 "master/public/data/tasks/{slug}.json")
MLENERGY_TASKS = {
    "Text chat (LM Arena)": "lm-arena-chat",
    "Code completion (Sourcegraph FIM)": "sourcegraph-fim",
    "Reasoning (GPQA)": "gpqa",
}

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

EIA_DEMAND_BASE = "https://api.eia.gov/v2/electricity/rto/region-data/data/"
ERCOT_LL_PAGE = "https://www.ercot.com/services/rq/large-load-integration"
GOOGLE_NEWS_RSS = ("https://news.google.com/rss/search?q={q}"
                   "&hl=en-US&gl=US&ceid=US:en")

# Third-party projections of global/US data-center electricity (TWh)
COMPANY_STATEMENTS = [
    # --- Hyperscalers & AI cloud ---
    ("Hyperscalers & AI cloud", "Amazon / AWS",
     "Impact in communities hub + 2025 economic-impact report",
     "https://www.aboutamazon.com/aws-impact-in-communities"),
    ("Hyperscalers & AI cloud", "Amazon / AWS",
     "Data centers: water & electricity use explainer",
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

# Operator -> Google-News search term for the live press-release feed.
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

# Rotating spotlight banner configurations
STORY_QUERY = ('data center residents (noise OR water OR "electric bill" OR '
               'rates OR lawsuit OR complaints OR moratorium OR pollution OR '
               '"property values") when:7d')

# Companion query without the "residents" anchor: bans, lawsuits, ordinances,
# and statehouse action routinely run under headlines that never say
# "residents" ("Millville Bans Data Centers…", "Legislature votes to
# eliminate…"), so STORY_QUERY alone missed most of the NJ ban/lawsuit wave.
# Pooled with STORY_QUERY (deduped by link) everywhere the community-impact
# feed is fetched.
STORY_QUERY_ACTIONS = ('data center (ban OR moratorium OR lawsuit OR '
                       'ordinance OR rezoning OR "planning board" OR '
                       '"town council" OR "public hearing" OR "tax credits" '
                       'OR legislation) when:7d')

# Per-state feeds for states with unusually hot fights — broad "<state> data
# center" pulls so town-level stories that match no impact keyword still make
# the archive. Key = full state name (matches _news_states_for / STATE_PUCS_DF
# "state" column); items fetched from one of these are force-tagged with that
# state. Used at site-build time only (build_site.py), not by the app carousel.
STORY_STATE_QUERIES = {
    "New Jersey": '"New Jersey" data center when:7d',
    "Virginia": '"Virginia" data center when:7d',
    "Georgia": '"Georgia" data center when:7d',
    "Texas": '"Texas" data center when:7d',
}

STORY_ANGLES = [
    (("noise", "hum", "sound", "decibel"), "🔊",
     "Noise from the facility is drawing resident complaints."),
    (("water", "drought", "cooling", "aquifer", "well"), "💧",
     "Water use for cooling is straining the local supply."),
    (("bill", "rate", "ratepayer", "electric", "utility", "cost of power"), "💸",
     "Neighbors say the new load is pushing up their power bills."),
    (("lawsuit", "sue", "sued", "court", "legal", "litigation"), "⚖️",
     "The dispute has escalated into litigation."),
    (("moratorium", "ban", "pause", "zoning", "rezone", "rezoning", "permit"), "🛑",
     "Local officials are moving to pause or block the project."),
    (("pollution", "air quality", "diesel", "emissions", "health", "smog"), "🏭",
     "Residents are raising air-quality and health concerns."),
    (("property value", "property values", "home value", "tax", "subsidy"), "🏠",
     "Residents question property-value hits and local benefit."),
]

# Substring → weight table for the heuristic "top stories" ranker. A headline's
# score is (recency + sum of matched weights), so outcome/escalation words
# (lawsuit, moratorium, rate hike) float the highest-stakes stories to the top.
# Keys are matched case-insensitively as substrings against the headline.
STORY_IMPACT_WEIGHTS = {
    "moratorium": 3.0, "ban": 3.0, "lawsuit": 3.0, "sued": 2.5, "sue": 2.0,
    "reject": 2.5, "denied": 2.5, "block": 2.5, "halt": 2.5, "withdraw": 2.5,
    "pull out": 2.5, "kill": 2.0, "pause": 2.0, "referendum": 2.0,
    "settlement": 2.0, "protest": 2.0, "approve": 1.8, "vote": 1.5,
    "ratepayer": 2.5, "rate hike": 2.5, "electric bill": 2.5,
    "power bill": 2.5, "utility bill": 2.5, "rates": 1.5, "bills": 1.2,
    "drought": 2.0, "water": 1.5, "aquifer": 2.0, "noise": 1.5,
    "diesel": 1.5, "pollution": 1.8, "air quality": 1.8,
    "oppose": 1.5, "opposition": 1.5, "backlash": 2.0, "outcry": 2.0,
    "property value": 1.8, "subsidy": 1.5, "tax break": 1.5,
    "billion": 1.5, "gigawatt": 1.2, "hyperscale": 1.0,
}

# Reddit search configurations
REDDIT_HOSTS = ("https://old.reddit.com/search.rss",
                "https://www.reddit.com/search.rss")
_ATOM = "{http://www.w3.org/2005/Atom}"
REDDIT_UA = "AIGridTracker/1.0 (public sentiment tab; contact via GitHub)"
REDDIT_PARQUET = pathlib.Path(__file__).resolve().parent.parent / "reddit_corpus.parquet"

# Subreddits pulled directly each day — site-wide keyword search misses the
# data-center communities. datacenter/datacenters are on-topic wholesale; the
# rest are searched (restrict_sr) for "data center" so only relevant posts land.
CURATED_SUBS = ("datacenter", "datacenters", "energy", "RealEstate")
# Obvious noise to drop from any source (site-wide search drags these in). Any
# subreddit ending in "content" or a u/ user page is also dropped in code.
DENY_SUBS = {
    "askreddit", "codwarzone", "thefinals", "smallstreetbets", "etfinvesting",
    "sndk_stock", "irenstocks", "passive_income", "sui", "lovegrok",
    "pokecorner", "ffxivrecruitment", "purtle", "marketfluxhub", "facepalm",
    "defendingaiart", "lovegroknews", "coherencephysics",
}

# ── Independent Market Monitors (IMM) ─────────────────────────────────────── #
# Every organized US wholesale market has an independent monitor that publishes
# an annual State of the Market report. These reports are the authoritative,
# non-industry source on capacity-auction costs, congestion, and large-load
# (data-center) driven price impacts — exactly the numbers a community needs at
# a rate case. All PDF/landing-page only (no public API), so this is a curated
# citation registry, not a live feed. "src_key" links via src_link() to SOURCES.
# "finding" = the most advocacy-relevant, load/data-center-related takeaway;
# where a headline number comes from reporting rather than the report body,
# "finding_src" points to that citation instead of the report.
MARKET_MONITORS = [
    {"monitor": "Monitoring Analytics", "grid": "PJM", "region": "Mid-Atlantic / 13 states + DC",
     "report": "Annual State of the Market Report for PJM", "edition": "2025 (Vol. 1 & 2)",
     "finding": "PJM's 2025/26 capacity auction cleared at ~$14.7B, up from ~$2.2B a year earlier — "
                "a spike driven largely by data-center load growth outpacing new supply.",
     "src_key": "imm_pjm", "finding_src": "whyy_dc"},
    {"monitor": "Potomac Economics", "grid": "ERCOT", "region": "Texas (~90% of state load)",
     "report": "State of the Market Report for the ERCOT Markets", "edition": "2025 (pub. May 2026)",
     "finding": "Tracks large-flexible-load (crypto/data-center) interconnection and its effect on "
                "scarcity pricing and reserve margins in the fastest-growing large-load market.",
     "src_key": "imm_ercot", "finding_src": "imm_ercot"},
    {"monitor": "Potomac Economics", "grid": "MISO", "region": "Midwest / South, 15 states",
     "report": "State of the Market Report for the MISO Electricity Markets", "edition": "2024 (latest annual)",
     "finding": "Day-ahead congestion cost ~$1.3B in 2024 (+10% YoY) — a signal of transmission strain "
                "as new large loads queue across the footprint.",
     "src_key": "imm_miso", "finding_src": "imm_miso"},
    {"monitor": "Potomac Economics", "grid": "ISO-NE", "region": "New England, 6 states",
     "report": "Annual Markets Report (ISO New England)", "edition": "2024 (latest annual)",
     "finding": "Baseline competitiveness and capacity-market reference for the Northeast; useful "
                "comparison point for large-load cost-allocation arguments.",
     "src_key": "imm_isone", "finding_src": "imm_isone"},
    {"monitor": "Potomac Economics", "grid": "NYISO", "region": "New York State",
     "report": "State of the Market Report for the New York ISO Markets", "edition": "2024 (latest annual)",
     "finding": "Covers capacity, congestion and interconnection trends for NY, where data-center siting "
                "pressure is rising upstate.",
     "src_key": "imm_nyiso", "finding_src": "imm_nyiso"},
    {"monitor": "CAISO Dept. of Market Monitoring", "grid": "CAISO", "region": "California + part of NV",
     "report": "Annual Report on Market Issues & Performance (+ Large Load Considerations paper)",
     "edition": "2024 report (pub. Oct 2025) + Jan 2026 large-load paper",
     "finding": "CA data-center load is forecast to grow ~1.8 GW by 2030 and ~4.9 GW by 2040; CAISO's "
                "large-load paper flags transmission cost-allocation and demand-forecast risk.",
     "src_key": "imm_caiso", "finding_src": "caiso_largeload"},
    {"monitor": "SPP Market Monitoring Unit", "grid": "SPP", "region": "Central US, 14 states",
     "report": "Annual State of the Market Report", "edition": "2025",
     "finding": "Finds SPP broadly competitive (output gap <0.1% in 2025); the annual report is the "
                "reference for congestion and new large-load interconnection in the plains.",
     "src_key": "imm_spp", "finding_src": "imm_spp"},
]
MARKET_MONITORS_DF = pd.DataFrame(MARKET_MONITORS)

# ── Ratepayer / consumer-advocacy organizations ──────────────────────────── #
# Groups that intervene in rate cases and PUC proceedings on behalf of
# residential / low-income customers — natural allies and model-language sources
# for a community facing data-center cost shifting. Not data feeds; a curated
# directory of who to read, cite, and contact. "key_point" is a quotable,
# sourced takeaway; "src_key"/"stat_src" link via src_link().
ADVOCACY_ORGS = [
    {"org": "Pennsylvania Utility Law Project (PULP)", "scope": "Pennsylvania", "type": "Legal aid / advocacy",
     "focus": "Low-income residential ratepayers; data-center cost-causation in rate cases",
     "key_point": "Estimates PA ratepayers already pay ~$1B/yr more in capacity costs from data-center "
                  "load growth, with residential customers facing $78M+/month more — and notes universal-"
                  "service program costs fall on residential customers alone.",
     "src_key": "pulp", "stat_src": "whyy_dc"},
    {"org": "CAUSE-PA", "scope": "Pennsylvania", "type": "Consumer coalition",
     "focus": "Affordable utility service & energy efficiency; large-load cost allocation",
     "key_point": "Argues in PUC proceedings that grid upgrades for large loads should be paid by those "
                  "loads unless proven otherwise, and that data centers post collateral for forecasts.",
     "src_key": "cause_pa", "stat_src": "whyy_dc"},
    {"org": "NASUCA", "scope": "National (state advocates)", "type": "Advocate network",
     "focus": "Umbrella for state utility consumer advocates; coordination & federal comments",
     "key_point": "The clearinghouse for finding and coordinating with your own state's consumer "
                  "advocate office — the party that formally intervenes in rate cases on your behalf.",
     "src_key": "nasuca", "stat_src": "nasuca"},
    {"org": "National Consumer Law Center (NCLC)", "scope": "National", "type": "Legal advocacy / research",
     "focus": "Energy & utility affordability, shutoff protections, low-income programs",
     "key_point": "Publishes model regulatory language and testimony on protecting residential customers "
                  "from cost shifts — reusable in comments and CBA drafting.",
     "src_key": "nclc", "stat_src": "nclc"},
    {"org": "Kleinman Center for Energy Policy (UPenn)", "scope": "National / research", "type": "Academic research",
     "focus": "Data-center load, rate design, and ratepayer-protection policy analysis",
     "key_point": "Independent analysis of new large-load tariff frameworks (e.g. PA's) — useful neutral "
                  "backing when a company disputes advocacy-group numbers.",
     "src_key": "kleinman", "stat_src": "kleinman"},
]
ADVOCACY_ORGS_DF = pd.DataFrame(ADVOCACY_ORGS)

# ──────────────────────────────────────────────────────────────────────────────
# LOCAL OFFICIALS — town/county layer
#
# Three-tier design (see src/local_officials.py for the resolution logic):
#   1. LOCAL_BODIES / LOCAL_OFFICIALS — hand-verified rows for localities with
#      an active data-center fight. Every row carries `source` (the official
#      .gov page it came from) and `as_of` (the date it was read). NOTHING here
#      is inferred, pattern-matched, or guessed: if a name, email or phone was
#      not on the official page, the field is left blank.
#   2. OpenStates /people.geo — free API, state legislators only (see
#      src/services/openstates.py). Explicitly excludes mayors and governors.
#   3. STATE_MUNI_LEAGUES + build_lookup_links() — deterministic "go find them"
#      links, 100% state coverage, zero staleness risk.
#
# TO ADD A LOCALITY: open its official government site, read the roster page,
# and append rows below with the page URL as `source` and today's date as
# `as_of`. Do not populate from search-engine snippets — during the initial
# build those were wrong for 2 of the first 4 localities checked.
# ──────────────────────────────────────────────────────────────────────────────

# State municipal leagues — official URLs as published by the National League
# of Cities (nlc.org/membership/state-municipal-leagues), read 2026-07-26.
# 49 leagues: Hawaii has none (no independent municipalities — county govt only).
STATE_MUNI_LEAGUES = {
    "AK": ("Alaska Municipal League", "http://www.akml.org/"),
    "AL": ("Alabama League of Municipalities", "https://almonline.org/"),
    "AR": ("Arkansas Municipal League", "http://www.arml.org/"),
    "AZ": ("League of Arizona Cities and Towns", "http://www.azleague.org/"),
    "CA": ("League of California Cities", "http://www.cacities.org/"),
    "CO": ("Colorado Municipal League", "http://www.cml.org/"),
    "CT": ("Connecticut Conference of Municipalities", "http://www.ccm-ct.org/"),
    "DE": ("Delaware League of Local Governments", "https://www.dllg.us/"),
    "FL": ("Florida League of Cities", "http://www.flcities.com/"),
    "GA": ("Georgia Municipal Association", "https://www.gacities.com/"),
    "IA": ("Iowa League of Cities", "http://www.iowaleague.org/"),
    "ID": ("Association of Idaho Cities", "http://www.idahocities.org/"),
    "IL": ("Illinois Municipal League", "http://www.iml.org/"),
    "IN": ("Accelerate Indiana Municipalities", "https://aimindiana.org/"),
    "KS": ("League of Kansas Municipalities", "http://www.lkm.org/"),
    "KY": ("Kentucky League of Cities", "http://www.klc.org/"),
    "LA": ("Louisiana Municipal Association", "http://www.lma.org/"),
    "MA": ("Massachusetts Municipal Association", "http://www.mma.org/"),
    "MD": ("Maryland Municipal League", "http://www.mdmunicipal.org/"),
    "ME": ("Maine Municipal Association", "http://www.memun.org/"),
    "MI": ("Michigan Municipal League", "http://www.mml.org/"),
    "MN": ("League of Minnesota Cities", "http://www.lmc.org/"),
    "MO": ("Missouri Municipal League", "http://www.mocities.com/"),
    "MS": ("Mississippi Municipal League", "http://www.mmlonline.com/"),
    "MT": ("Montana League of Cities and Towns", "https://mtleague.org/"),
    "NC": ("North Carolina League of Municipalities", "http://www.nclm.org/"),
    "ND": ("North Dakota League of Cities", "http://www.ndlc.org/"),
    "NE": ("League of Nebraska Municipalities", "http://www.lonm.org/"),
    "NH": ("New Hampshire Municipal Association", "https://www.nhmunicipal.org/"),
    "NJ": ("New Jersey State League of Municipalities", "https://www.njlm.org/"),
    "NM": ("New Mexico Municipal League", "http://www.nmml.org/"),
    "NV": ("Nevada League of Cities and Municipalities", "https://nvleague.com/"),
    "NY": ("NY State Conference of Mayors (NYCOM)", "http://www.nycom.org/"),
    "OH": ("Ohio Municipal League", "http://www.omlohio.org/"),
    "OK": ("Oklahoma Municipal League", "http://www.oml.org/"),
    "OR": ("League of Oregon Cities", "http://www.orcities.org/"),
    "PA": ("Pennsylvania Municipal League", "http://www.pml.org/"),
    "RI": ("Rhode Island League of Cities and Towns", "http://www.rileague.org/"),
    "SC": ("Municipal Association of South Carolina", "http://www.masc.sc/"),
    "SD": ("South Dakota Municipal League", "http://www.sdmunicipalleague.org/"),
    "TN": ("Tennessee Municipal League", "http://www.tml1.org/"),
    "TX": ("Texas Municipal League", "http://www.tml.org/"),
    "UT": ("Utah League of Cities and Towns", "http://www.ulct.org/"),
    "VA": ("Virginia Municipal League", "http://www.vml.org/"),
    "VT": ("Vermont League of Cities and Towns", "http://www.vlct.org/"),
    "WA": ("Association of Washington Cities", "https://wacities.org/"),
    "WI": ("League of Wisconsin Municipalities", "http://www.lwm-info.org/"),
    "WV": ("West Virginia Municipal League", "http://www.wvml.org/"),
    "WY": ("Wyoming Association of Municipalities", "http://www.wyomuni.org/"),
}

# National fallbacks used when a state has no league or the locality is a county.
NACO_COUNTY_SEARCH = "https://www.naco.org/counties"
USA_GOV_LOCAL = "https://www.usa.gov/local-governments"

# ── Tier 1: governing bodies (stable — survives elections) ───────────────────
# `decides` = what this body actually votes on, so users pick the right room.
LOCAL_BODIES = [
    {"locality": "Tucker County", "state": "WV",
     "body": "Tucker County Commission",
     "decides": "County-level approvals, resolutions and budget. Note: WV HB 2014 "
                "strips counties of zoning authority over certified microgrid "
                "districts and high-impact data centers.",
     "meets": "2nd Wednesday 9:00 a.m. year-round; 4th Wednesday 4:00 p.m. "
              "(Nov-Apr) / 6:00 p.m. (May-Oct)",
     "where": "Courtroom, Tucker County Courthouse, 211 First Street, Parsons, WV 26287",
     "agenda_url": "https://tuckercountycommission.com/agendas",
     "comment_process": "Agendas posted on the website and around the courthouse. "
                        "To be added to the agenda, contact the Tucker County "
                        "Clerk's Office in advance.",
     "phone": "304-478-2866 ext. 1207", "email": "sdevilder@tuckercountycommission.com",
     "website": "https://tuckercountycommission.com/county-commission",
     "as_of": "2026-07-26", "source": "https://tuckercountycommission.com/county-commission"},

    {"locality": "Port Washington", "state": "WI",
     "body": "Common Council",
     "decides": "Ordinances and resolutions, budget and tax levy, contracts for "
                "city services, and appointments to boards and commissions — "
                "including the Plan Commission that handles land use.",
     "meets": "1st and 3rd Tuesday of the month",
     "where": "City Hall, 100 W. Grand Avenue, Port Washington, WI 53074",
     "agenda_url": "https://www.portwashingtonwi.gov/our-city/meeting-calendar",
     "comment_process": "Council meetings include a public comment period. Meeting "
                        "location has moved for high-attendance data-center items — "
                        "check the calendar listing before you go.",
     "phone": "262-284-5585", "email": "",
     "website": "https://www.portwashingtonwi.gov/our-city/mayor-common-council",
     "as_of": "2026-07-26", "source": "https://www.portwashingtonwi.gov/our-city/mayor-common-council"},

    {"locality": "Goochland County", "state": "VA",
     "body": "Board of Supervisors",
     "decides": "Land use and rezoning, conditional use permits, budget and tax "
                "rates. Data centers are permitted by right across most of the "
                "designated technology district; gas peakers and SMRs still "
                "require a conditional use permit.",
     "meets": "1st Tuesday monthly, 2:00 p.m. (public hearings at 6:00 p.m.); "
              "3rd Tuesday reserved for additional meetings",
     "where": "County Administration Building, Board Meeting Room 250, "
              "1800 Sandy Hook Road, Goochland, VA 23063",
     "agenda_url": "https://www.goochlandva.us/381/Public-Notices-Meetings-Agendas-Minutes",
     "comment_process": "Email comments on any agenda item to BOSCOMMENT@GOOCHLANDVA.US. "
                        "Meetings stream on the county's YouTube channel. Each member "
                        "has a published Voting History page.",
     "phone": "804-556-5800", "email": "BOSCOMMENT@GOOCHLANDVA.US",
     "website": "https://www.goochlandva.us/158/Board-of-Supervisors",
     "as_of": "2026-07-26", "source": "https://www.goochlandva.us/158/Board-of-Supervisors"},

    {"locality": "Prince William County", "state": "VA",
     "body": "Board of County Supervisors",
     "decides": "Rezonings, special use permits and comprehensive plan amendments — "
                "the body that approved the PW Digital Gateway. Seven district "
                "members plus an at-large Chair.",
     "meets": "See the county's published annual meeting calendar",
     "where": "1 County Complex Court, Prince William, VA 22192",
     "agenda_url": "https://www.pwcva.gov/department/board-county-supervisors",
     "comment_process": "Residents may attend in person or participate remotely. "
                        "Each supervisor keeps a district office — contacting your "
                        "own district member directly is more effective than the "
                        "general line.",
     "phone": "703-792-4311", "email": "",
     "website": "https://www.pwcva.gov/department/board-county-supervisors/contact-us",
     "as_of": "2026-07-26", "source": "https://www.pwcva.gov/department/board-county-supervisors/contact-us"},

    {"locality": "San Marcos", "state": "TX",
     "body": "City Council",
     "decides": "Ordinances, resolutions, the annual budget and the city tax "
                "rate — and, unusually, the city's own water, electric and "
                "wastewater rates. San Marcos was the first Texas city to ban "
                "data centers.",
     "meets": "1st and 3rd Tuesday monthly — 3:00 p.m. work/executive session, "
              "6:00 p.m. regular meeting",
     "where": "City Council Chambers, City Hall, 630 E Hopkins, San Marcos, TX 78666",
     "agenda_url": "https://www.sanmarcostx.gov/AgendaCenter/City-Council-4",
     "comment_process": "Regular meetings include citizen comment. The sign-up "
                        "process and rules are on the city's Citizen Comments "
                        "page and the Legistar agenda portal "
                        "(san-marcos-tx.legistar.com).",
     "phone": "512-393-8000", "email": "councilmembers@sanmarcostx.gov",
     "website": "https://www.sanmarcostx.gov/149/City-Council",
     "as_of": "2026-08-05", "source": "https://www.sanmarcostx.gov/149/City-Council"},

    {"locality": "Chesterfield County", "state": "VA",
     "body": "Board of Supervisors",
     "decides": "Rezonings, conditional use permits and comprehensive plan "
                "amendments across five magisterial districts — the body that "
                "rules on data center rezonings in a county seeing heavy data "
                "center interest.",
     "meets": "See the county's published 2026 meeting schedule (Board Meetings page)",
     "where": "Public Meeting Room, 10001 Iron Bridge Road, Chesterfield, VA 23831",
     "agenda_url": "https://www.chesterfield.gov/244/Agendas-and-Minutes",
     "comment_process": "Regular meetings include public comment periods; see "
                        "the county's Public Comments page. Public hearing "
                        "notices are posted for rezoning items.",
     "phone": "804-748-1200", "email": "WilsonSu@chesterfield.gov",
     "website": "https://www.chesterfield.gov/1218/Board-of-Supervisors",
     "as_of": "2026-08-05", "source": "https://www.chesterfield.gov/1218/Board-of-Supervisors"},

    {"locality": "Manatee County", "state": "FL",
     "body": "Board of County Commissioners",
     "decides": "Land use, rezonings and the county budget across five districts "
                "plus two at-large seats. The District 1 seat is vacant (as of "
                "Aug 2026). The county has advanced a data center moratorium.",
     "meets": "Regular meeting the 25th of each month; Land Use meeting the 6th; "
              "both 9:00 a.m.-5:00 p.m.",
     "where": "Manatee County Administration Building, 1112 Manatee Ave West, "
              "Bradenton, FL 34205",
     "agenda_url": "https://agendaonline.mymanatee.org",
     "comment_process": "Residents sign up through the county's 'Sign up to Speak "
                        "at a Public Meeting' page; agendas are on Agenda Online.",
     "phone": "", "email": "",
     "website": "https://www.mymanatee.org/government/government-information/board-of-county-commissioners",
     "as_of": "2026-08-05", "source": "https://www.mymanatee.org/government/government-information/board-of-county-commissioners"},

    {"locality": "Vineland", "state": "NJ",
     "body": "Planning Board",
     "decides": "Site plan and subdivision applications, including the DataOne "
                "USA data center on South Lincoln Avenue that residents have "
                "sued over for noise. Vineland City Council handles zoning "
                "ordinance changes and moratoriums; the Planning Board rules on "
                "individual project applications.",
     "meets": "2nd Wednesday of the month; pre-meeting conference 6:00 p.m., "
              "regular meeting 6:30 p.m.",
     "where": "City Council Chambers, 640 E. Wood Street, Vineland, NJ 08360",
     "agenda_url": "https://www.vinelandcity.org/planning-board/",
     "comment_process": "Public Comment period at the end of the agenda for "
                        "matters not otherwise on it; for a specific application, "
                        "raise your hand to speak after being sworn in. Speakers "
                        "are limited to five minutes each.",
     "phone": "856-794-4000 ext. 4088 (general); ext. 4101 (master plan/"
              "redevelopment); ext. 4769 (subdivisions/site plans)",
     "email": "",
     "website": "https://www.vinelandcity.org/planning-board/",
     "as_of": "2026-08-08", "source": "https://www.vinelandcity.org/planning-board/"},

    {"locality": "Flagler County", "state": "FL",
     "body": "Board of County Commissioners",
     "decides": "Land use, rezonings and the county budget across five districts. "
                "Flagler enacted a one-year data center moratorium (through Aug 2027).",
     "meets": "1st Monday 9:00 a.m. and 3rd Monday 5:00 p.m.",
     "where": "Government Services Building #2, 1769 E. Moody Boulevard, Bunnell, FL 32110",
     "agenda_url": "https://www.flaglercounty.gov/Government/Board-of-County-Commissioners/Meetings-Agendas-Summaries",
     "comment_process": "Meetings are streamed live; see the board's Rules & "
                        "Procedures and the meetings page for the public-comment process.",
     "phone": "386-313-4001", "email": "",
     "website": "https://www.flaglercounty.gov/Government/Board-of-County-Commissioners",
     "as_of": "2026-08-07", "source": "https://www.flaglercounty.gov/Government/Board-of-County-Commissioners"},

    {"locality": "Hays County", "state": "TX",
     "body": "Commissioners Court",
     "decides": "County budget, roads and development in the unincorporated county "
                "across four precincts, presided over by the County Judge. Hays "
                "enacted a data center moratorium (through Dec 31, 2026); San "
                "Marcos, the county seat, was the first Texas city to ban data centers.",
     "meets": "Tuesdays 9:00 a.m.",
     "where": "Hays County Historic Courthouse, 111 E. San Antonio St., San Marcos, "
              "TX 78666 (offices at 712 South Stagecoach Trail)",
     "agenda_url": "https://www.hayscountytx.gov/164/Commissioners-Court",
     "comment_process": "Commissioners Court meets Tuesday mornings; see the "
                        "county's agenda portal for the public-comment process.",
     "phone": "512-393-7779", "email": "",
     "website": "https://www.hayscountytx.gov/188/Commissioners-Court-Members",
     "as_of": "2026-08-07", "source": "https://www.hayscountytx.gov/188/Commissioners-Court-Members"},

    {"locality": "Broomfield", "state": "CO",
     "body": "City Council",
     "decides": "Ordinances, land use and budget for the consolidated City and "
                "County of Broomfield — ten members across five wards plus an "
                "at-large mayor. Broomfield enacted Ordinance 2313, an 18-month "
                "data center pause (through Dec 2027).",
     "meets": "See the city's published council meeting calendar",
     "where": "George Di Ciero City and County Building, Broomfield, CO — check "
              "the council calendar for time and room",
     "agenda_url": "https://www.broomfield.org/128/Broomfield-Council",
     "comment_process": "See 'Participate in City Council Meetings' "
                        "(broomfield.org/467) for how to give public comment; "
                        "meetings are also streamed.",
     "phone": "303-438-6300", "email": "",
     "website": "https://www.broomfield.org/954/Council-Members",
     "as_of": "2026-08-07", "source": "https://www.broomfield.org/954/Council-Members"},

    {"locality": "Lakeland", "state": "FL",
     "body": "City Commission",
     "decides": "Ordinances, land use, the city budget and the municipal "
                "electric utility (Lakeland Electric). Lakeland enacted a "
                "one-year data center moratorium (through Aug 2027).",
     "meets": "1st and 3rd Monday of the month, 9:00 a.m. (excluding holidays)",
     "where": "City Hall, 228 S Massachusetts Avenue, Lakeland, FL 33801",
     "agenda_url": "https://www.lakelandgov.net/departments/city-clerk/",
     "comment_process": "Meetings air live on LGTV; contact the City Clerk for "
                        "the agenda and public-comment process.",
     "phone": "863-834-6005", "email": "citycommission@lakelandgov.net",
     "website": "https://www.lakelandgov.net/government/mayor-city-commission/",
     "as_of": "2026-08-07", "source": "https://www.lakelandgov.net/government/mayor-city-commission/"},

    {"locality": "Desert Hot Springs", "state": "CA",
     "body": "City Council",
     "decides": "Ordinances, land use and the city budget across four districts "
                "plus an at-large mayor. Desert Hot Springs extended its data "
                "center moratorium to two years (through mid-2028).",
     "meets": "See the council's published agenda calendar",
     "where": "City Hall, 11999 Palm Drive, Desert Hot Springs, CA 92240",
     "agenda_url": "https://cityofdhs.civicweb.net/Portal/",
     "comment_process": "See the council's Agendas, Minutes & Videos portal for "
                        "the public-comment process.",
     "phone": "760-329-6411", "email": "",
     "website": "https://www.cityofdhs.org/departments/city-council/",
     "as_of": "2026-08-07", "source": "https://www.cityofdhs.org/departments/city-council/"},

    {"locality": "Butte County", "state": "CA",
     "body": "Water Commission",
     "decides": "Advisory body that studies water issues and recommends "
                "solutions to the Board of Supervisors; not a permitting "
                "authority. County zoning does not currently allow data "
                "centers in unincorporated areas and no project has been "
                "proposed — a commissioner requested this review specifically "
                "so the county has a policy position before a proposal arrives.",
     "meets": "1st Wednesday of the month, 1:30 p.m.",
     "where": "Board of Supervisors Chambers, 25 County Center Drive, Suite 205, Oroville, CA 95965",
     "agenda_url": "https://buttecounty.granicus.com/boards/w/839ba29f34a61ab5/boards/34489",
     "comment_process": "In person, or electronically to BCWATER@BUTTECOUNTY.NET.",
     "phone": "530-552-3595", "email": "BCWATER@BUTTECOUNTY.NET",
     "website": "https://www.buttecounty.net/1221/Water-Commission",
     "as_of": "2026-08-10", "source": "https://buttecounty.granicus.com/boards/w/839ba29f34a61ab5/boards/34489"},

    {"locality": "Spartanburg County", "state": "SC",
     "body": "County Council",
     "decides": "Zoning, land-use ordinances, and the county budget. A "
                "lawsuit (Southern Environmental Law Center) accuses the "
                "county of letting the $2.8B, 457 MW NorthMark/Valara data "
                "center on Pine Street bypass the Planning Commission by "
                "treating it as two 'minor' developments instead of one "
                "'major' one, which would have required public review.",
     "meets": "See the council's published meeting calendar; regular "
              "meetings are typically 5:15 p.m. in Council Chambers.",
     "where": "Spartanburg County Administration Building, 366 North Church "
              "Street, Spartanburg, SC 29303",
     "agenda_url": "https://www.spartanburgcounty.gov/189/County-Council",
     "comment_process": "See the council's published agenda/meeting calendar "
                        "for the public-comment process.",
     "phone": "864-596-2528", "email": "",
     "website": "https://www.spartanburgcounty.gov/189/County-Council",
     "as_of": "2026-08-11", "source": "https://www.spartanburgcounty.gov/189/County-Council"},

    {"locality": "Effingham County", "state": "GA",
     "body": "Board of Commissioners",
     "decides": "Zoning, land use, and county budget across five districts "
                "plus an at-large chairman. Negotiated a $20B OpenAI data "
                "center deal (Savannah Gateway Industrial Hub, Rincon) with "
                "the county's Industrial Development Authority before any "
                "public vote or comment — the announcement itself is what "
                "drew nearly 1,000 residents to a since-held open house.",
     "meets": "1st and 3rd Tuesday of the month, 5:00 p.m.",
     "where": "Effingham Administration Complex, Commissioner Meeting Room, "
              "804 S. Laurel Street, Springfield, GA 31329",
     "agenda_url": "https://www.effinghamcounty.org/384/County-Board-of-Commissioners",
     "comment_process": "See the 'Meeting Appearance/Presentation Procedures' "
                        "document in the county's Document Center.",
     "phone": "912-754-2123", "email": "effinghamclerk@effinghamcounty.org",
     "website": "https://www.effinghamcounty.org/384/County-Board-of-Commissioners",
     "as_of": "2026-08-11", "source": "https://www.effinghamcounty.org/384/County-Board-of-Commissioners"},

    {"locality": "Plymouth Township", "state": "PA",
     "body": "Zoning Hearing Board",
     "decides": "Special-exception and variance applications, including "
                "developer Brian O'Neill's proposal to convert the former "
                "Cleveland-Cliffs steel mill at 900 Conshohocken Road into a "
                "2-million-sq-ft data center. Township Council has separately "
                "issued a public statement opposing the project and listed "
                "43 conditions it says the proposal would need to meet.",
     "meets": "Hearings are scheduled individually and announced on the "
              "township website; recent sessions have been held at Colonial "
              "Middle School, 716 Belvoir Road, Plymouth Meeting, PA.",
     "where": "Colonial Middle School, 716 Belvoir Road, Plymouth Meeting, PA 19462",
     "agenda_url": "https://www.plymouthtownship.org/data-center-update/",
     "comment_process": "Public comment is not taken at procedural/opening "
                        "hearings; the township announces in advance which "
                        "session will take resident testimony. Use the "
                        "Citizen Request option at plymouthtownship.org/"
                        "citizen-action-line/ for general contact.",
     "phone": "", "email": "",
     "website": "https://www.plymouthtownship.org/data-center-update/",
     "as_of": "2026-08-11", "source": "https://www.plymouthtownship.org/zoning-hearing-board-meeting-scheduled-for-special-exception-for-proposed-data-center/"},

    {"locality": "Wytheville", "state": "VA",
     "body": "Town Council",
     "decides": "Ordinances, land use, and town budget. Residents have "
                "pushed back on a data center boom in the town over land, "
                "water, and electric-rate impacts.",
     "meets": "2nd and 4th Monday, 5:00 p.m.",
     "where": "Wytheville Municipal Building, 150 E. Monroe Street, Wytheville, VA 24382",
     "agenda_url": "https://www.wytheville.org/town-council",
     "comment_process": "See the town's Agendas & Minutes page for the "
                        "public-comment process for a specific meeting.",
     "phone": "276-223-3333", "email": "",
     "website": "https://www.wytheville.org/town-council",
     "as_of": "2026-08-12", "source": "https://www.wytheville.org/town-council"},

    {"locality": "Dowagiac", "state": "MI",
     "body": "City Council",
     "decides": "Ordinances, land use, and town budget. Hyperscale Data, "
                "Inc.'s existing bitcoin-mining site (over 48 acres) is "
                "converting to AI computing; residents have filed a "
                "class-action lawsuit over noise, and Mayor Patrick Bakeman "
                "publicly gave the company 45 days to submit formal plans.",
     "meets": "See the council's published agendas & minutes page.",
     "where": "Dowagiac City Hall, 241 S. Front Street, Dowagiac, MI 49047",
     "agenda_url": "https://www.cityofdowagiac.com/government/city_council/agendas___minutes.php",
     "comment_process": "See the council's published agenda for a specific "
                        "meeting's public-comment process.",
     "phone": "269-782-2195", "email": "",
     "website": "https://www.cityofdowagiac.com/",
     "as_of": "2026-08-12", "source": "https://www.cityofdowagiac.com/"},

    {"locality": "Pittsburg", "state": "CA",
     "body": "City Council",
     "decides": "Zoning, land use and city budget. Held a public workshop "
                "on data-center development after residents raised concerns "
                "at a June 2026 meeting; a data center is already operating "
                "in the city.",
     "meets": "1st and 3rd Monday, 7:00 p.m.",
     "where": "Pittsburg Civic Center, City Council Chambers, 65 Civic Avenue, Pittsburg, CA 94565",
     "agenda_url": "https://www.pittsburgca.gov/services/city-council/council-meetings",
     "comment_process": "Agendas are posted at City Hall, the Pittsburg "
                        "Library, and the city website; emailed 10 days in "
                        "advance to those who request notice.",
     "phone": "", "email": "",
     "website": "https://www.pittsburgca.gov/government/city-council-1594",
     "as_of": "2026-08-12", "source": "https://www.pittsburgca.gov/services/city-council/council-meetings"},

    {"locality": "Westlake", "state": "TX",
     "body": "Town Council",
     "decides": "Zoning and land use; approved an 87-acre data center with "
                "added conditions, and a separate proposed campus near a "
                "Buddhist monastery has drawn pushback from Westlake "
                "residents and neighboring Keller.",
     "meets": "See the council's published Agenda Center for the current "
              "meeting calendar.",
     "where": "Westlake Town Hall, 1500 Solana Boulevard, Building 7, Suite 7200, Westlake, TX 76262",
     "agenda_url": "https://westlake-tx.legistar.com/",
     "comment_process": "Submit feedback via the town's official comment "
                        "form, or attend a meeting (streamed live and "
                        "archived on demand).",
     "phone": "817-430-0941", "email": "",
     "website": "https://www.westlake-tx.org/148/Town-Council",
     "as_of": "2026-08-12", "source": "https://www.westlake-tx.org/148/Town-Council"},

    {"locality": "Hoffman Estates", "state": "IL",
     "body": "Plan Commission / Village Board",
     "decides": "Rezoning and land-use applications. The Plan Commission "
                "voted 4-2 against rezoning the 'Plum Farms' site (Higgins "
                "Road & Route 59) for a data center after a packed 3-hour "
                "hearing; the developer withdrew its request July 1, 2026.",
     "meets": "Village Board meets 1st and 3rd Monday, 7:00 p.m.",
     "where": "Village Hall Council Chambers, 1900 Hassell Road, Hoffman Estates, IL 60169",
     "agenda_url": "https://www.hoffmanestates.org/updates/meeting-agendas-packets-minutes/village-board",
     "comment_process": "See the village's published agendas for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.hoffmanestates.org/",
     "as_of": "2026-08-12", "source": "https://www.hoffmanestates.org/updates/meeting-agendas-packets-minutes/village-board"},

    {"locality": "Grayslake", "state": "IL",
     "body": "Village Board",
     "decides": "Zoning and land use; approved the T5 Data Center Campus "
                "near Peterson Road after multiple Plan Commission and "
                "Village Board meetings. Opponents have since sued to try "
                "to stop construction.",
     "meets": "Twice monthly, 6:00 p.m.",
     "where": "Village Hall, 10 S Seymour Avenue, Grayslake, IL 60030",
     "agenda_url": "https://www.villageofgrayslake.com/6/Agendas-Minutes",
     "comment_process": "See the village's published agendas for the "
                        "public-comment process for a specific meeting.",
     "phone": "847-223-8515", "email": "",
     "website": "https://www.villageofgrayslake.com/881/Approved-T5-Data-Center-Campus-Informati",
     "as_of": "2026-08-12", "source": "https://www.villageofgrayslake.com/881/Approved-T5-Data-Center-Campus-Informati"},

    {"locality": "Wrightstown", "state": "WI",
     "body": "Village Board",
     "decides": "Zoning and infrastructure decisions. Put an advisory "
                "referendum on the Aug. 11, 2026 ballot asking whether the "
                "village should support utility infrastructure for a "
                "large-scale data center (developer: Cloverleaf "
                "Infrastructure); voters said no.",
     "meets": "1st and 3rd Tuesday, 6:00 p.m.",
     "where": "352 High Street, Wrightstown, WI 54180",
     "agenda_url": "https://www.wrightstown.us/agendas/",
     "comment_process": "See the village's published agendas for the "
                        "public-comment process for a specific meeting.",
     "phone": "920-532-5567", "email": "",
     "website": "https://www.wrightstown.us/",
     "as_of": "2026-08-12", "source": "https://www.wrightstown.us/agendas/"},

    {"locality": "Little Rock", "state": "AR",
     "body": "Board of Directors",
     "decides": "City ordinances, permits and zoning. Passed data-center "
                "regulations (groundwater cooling ban, noise monitors, "
                "generator-testing limits) June 3, 2026; a separate 18-month "
                "permitting moratorium on hyperscale facilities — including "
                "a planned Google data center at the Port of Little Rock — "
                "failed on a 4-4 vote August 4, 2026.",
     "meets": "Regular meetings 1st & 3rd Tuesday, 6:00 p.m.; Agenda "
              "meetings 2nd & 4th Tuesday, 4:00 p.m.",
     "where": "City Hall, 500 W. Markham Street, Little Rock, AR 72201",
     "agenda_url": "https://littlerock.gov/government/board-of-directors/board-meeting-calendar/",
     "comment_process": "See the board's published meeting agendas for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://littlerock.gov/government/board-of-directors/",
     "as_of": "2026-08-12", "source": "https://littlerock.gov/government/board-of-directors/board-meeting-calendar/"},

    {"locality": "Topeka", "state": "KS",
     "body": "City Council",
     "decides": "Zoning code and conditional-use permits. Discussed defining "
                "data centers under the zoning code and requiring "
                "Conditional Use Permits for future proposals at a Jul 7, "
                "2026 presentation.",
     "meets": "1st three Tuesdays of the month, 6:00 p.m.",
     "where": "City Council Chambers, 214 SE 8th Street, 2nd Floor, Topeka, KS 66603",
     "agenda_url": "https://topeka.granicus.com/ViewPublisher.php?view_id=1",
     "comment_process": "Contact the city clerk's office (785-368-3940, "
                        "cclerk@topeka.org) by 5:00 p.m. the day of the "
                        "meeting to sign up; or comment online at "
                        "topekaspeaks.org.",
     "phone": "785-368-3940", "email": "cclerk@topeka.org",
     "website": "https://www.topeka.org/citycouncil/",
     "as_of": "2026-08-12", "source": "https://www.topeka.org/citycouncil/sign-up-to-speak-at-a-council-committee-meeting/"},

    {"locality": "Sturtevant", "state": "WI",
     "body": "Village Board",
     "decides": "Zoning and land use. Residents filed a class-action suit "
                "against Microsoft over noise from its data center; the "
                "company says it hosted a June 23, 2026 open house and "
                "considers the complaints resolved.",
     "meets": "1st and 3rd Tuesday, 6:00 p.m.",
     "where": "Village Hall, Sturtevant, WI",
     "agenda_url": "https://www.sturtevant-wi.gov/meetings",
     "comment_process": "See the village's published agendas for the "
                        "public-comment process for a specific meeting.",
     "phone": "262-886-7201", "email": "",
     "website": "https://www.sturtevant-wi.gov/villageboard",
     "as_of": "2026-08-12", "source": "https://www.sturtevant-wi.gov/villageboard"},

    {"locality": "Davie County", "state": "NC",
     "body": "Board of Commissioners",
     "decides": "Zoning, land use and county budget across a five-member "
                "board. Residents have asked the board to consider a "
                "data-center moratorium; no vote confirmed yet.",
     "meets": "See the county's published agendas & minutes page.",
     "where": "Administrative Office Building, 123 South Main Street, Mocksville, NC 27028",
     "agenda_url": "https://www.daviecountync.gov/264/Agendas-Minutes",
     "comment_process": "See the board's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.daviecountync.gov/107/County-Commissioners",
     "as_of": "2026-08-12", "source": "https://www.daviecountync.gov/1201/Board-Members-and-Meetings"},

    {"locality": "Sangamon County", "state": "IL",
     "body": "County Board",
     "decides": "Zoning and land use. Residents near a proposed data center "
                "have filed a lawsuit as the county works through the "
                "project's land-use questions.",
     "meets": "See the county's published events list.",
     "where": "Sangamon County, Springfield, IL",
     "agenda_url": "https://sangamonil.gov/eventslist?category=county-board-meetings",
     "comment_process": "See the county's published agendas for the "
                        "public-comment process for a specific meeting.",
     "phone": "217-753-6700", "email": "",
     "website": "https://sangamonil.gov/",
     "as_of": "2026-08-12", "source": "https://sangamonil.gov/eventslist?category=county-board-meetings"},

    {"locality": "Guilderland", "state": "NY",
     "body": "Town Board",
     "decides": "Zoning and land use. Opened discussion on whether to adopt "
                "its own data-center moratorium and set a Sep 15, 2026 "
                "public hearing to continue the conversation; a separate "
                "statewide executive order from Gov. Hochul already pauses "
                "server farms needing 50+ MW for one year.",
     "meets": "See the town's Agenda Center for the current schedule.",
     "where": "Guilderland Town Hall, NY",
     "agenda_url": "https://townofguilderland.org/AgendaCenter",
     "comment_process": "See the town's published agenda for the "
                        "public-comment process for the Sep 15, 2026 public "
                        "hearing or other meetings.",
     "phone": "", "email": "",
     "website": "https://www.townofguilderland.gov/",
     "as_of": "2026-08-12", "source": "https://www.news10.com/top-stories/guilderland-residents-ask-town-board-to-place-moratorium-on-data-centers/"},

    {"locality": "Tonganoxie", "state": "KS",
     "body": "Governing Body (City Council)",
     "decides": "Zoning and land use. Residents submitted a petition for an "
                "18-month moratorium on data centers.",
     "meets": "1st and 3rd Monday of the month.",
     "where": "Tonganoxie, KS",
     "agenda_url": "https://www.tonganoxie.org/minutes-and-agendas",
     "comment_process": "Contact the City Clerk (913-845-2620) by 1:00 p.m. "
                        "the day of the meeting to sign up; comment limited "
                        "to 3 minutes per person.",
     "phone": "913-845-2620", "email": "",
     "website": "https://www.tonganoxie.org/city-council",
     "as_of": "2026-08-12", "source": "https://www.tonganoxie.org/city-council"},

    {"locality": "Osawatomie", "state": "KS",
     "body": "City Council",
     "decides": "Zoning and land use. Alcove Development presented a "
                "roughly $1B data-center project proposal at a Jun 25, 2026 "
                "special meeting; residents have pushed back on the meeting "
                "format itself.",
     "meets": "2nd and 4th Thursday, 6:00 p.m. (temporarily relocated to "
              "City Auditorium, 439 Main Street, during Memorial Hall "
              "construction).",
     "where": "City Auditorium, 439 Main Street, Osawatomie, KS 66064",
     "agenda_url": "https://www.osawatomieks.org/mayor-city-council/pages/council-meetings",
     "comment_process": "See the city's published agendas for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.osawatomieks.org/mayor-city-council",
     "as_of": "2026-08-12", "source": "https://www.osawatomieks.org/mayor-city-council"},

    {"locality": "Allen Park", "state": "MI",
     "body": "City Council",
     "decides": "Zoning, land use and city budget. Residents have pushed "
                "for a data-center moratorium amid growing opposition; no "
                "vote confirmed yet.",
     "meets": "2nd and 4th Tuesday, 6:00 p.m.",
     "where": "Allen Park City Hall, 15915 Southfield Rd, Allen Park, MI 48101",
     "agenda_url": "https://cityofallenpark.org/government/agenda_and_minutes/allen_park_michigan_city_council.php",
     "comment_process": "See the city's published agendas for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://cityofallenpark.org/",
     "as_of": "2026-08-12", "source": "https://cityofallenpark.org/government/agenda_and_minutes/allen_park_michigan_city_council.php"},

    {"locality": "Nelson County", "state": "KY",
     "body": "Fiscal Court",
     "decides": "County-level land use and budget. County officials have "
                "publicly opposed hyperscale data centers as residents call "
                "for a moratorium; no vote confirmed yet.",
     "meets": "1st Tuesday 9:00 a.m. and 3rd Tuesday 6:00 p.m.",
     "where": "Fiscal Court Room, 2nd Floor, Old Courthouse Building, One Court Square, Bardstown, KY 40004",
     "agenda_url": "https://nelsoncountyky.gov/fiscal-court-meetings-agenda/",
     "comment_process": "See the court's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "nelsoncoky@nelsoncountyky.gov",
     "website": "https://nelsoncountyky.gov/fiscal-court-meetings-agenda/",
     "as_of": "2026-08-12", "source": "https://nelsoncountyky.gov/fiscal-court-meetings-agenda/"},

    {"locality": "Garfield Township", "state": "MI",
     "body": "Township Board (Grand Traverse County)",
     "decides": "Zoning and land use, in a township that relies on the City "
                "of Traverse City for water/sewer service. Its Planning "
                "Commission voted Jul 8, 2026 to recommend a zoning "
                "amendment letting the board freeze data-center "
                "applications for up to a year (extendable 6 months); the "
                "board had not yet acted on the recommendation as of this "
                "writing.",
     "meets": "See the township's published meetings page.",
     "where": "Garfield Township, Grand Traverse County, MI",
     "agenda_url": "https://www.garfield-twp.com/meetings.asp",
     "comment_process": "See the township's published agendas for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.garfield-twp.com/",
     "as_of": "2026-08-12", "source": "https://www.traverseticker.com/news/garfield-township-tees-up-data-center-moratorium-incomplete-application-submitted-for-project/"},

    {"locality": "Harrison County", "state": "KY",
     "body": "Fiscal Court",
     "decides": "County-level land use and budget. Judge-Executive Jason "
                "Marshall held a Jul 28, 2026 public forum on data centers "
                "(no proposal currently pending) where nearly every attendee "
                "raised a hand in opposition; the court had a data-center "
                "moratorium vote scheduled for its Aug 11, 2026 meeting — "
                "confirm the outcome before citing a status.",
     "meets": "See the court's published meeting schedule.",
     "where": "Old Courthouse, Cynthiana, KY",
     "agenda_url": "http://www.harrisoncountyfiscalcourt.com/",
     "comment_process": "See the court's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "http://www.harrisoncountyfiscalcourt.com/",
     "as_of": "2026-08-12", "source": "https://www.wkyt.com/2026/07/29/harrison-county-leaders-hear-public-opposition-data-centers-ahead-moratorium-vote/"},

    {"locality": "Lowndes County", "state": "GA",
     "body": "Board of Commissioners",
     "decides": "Zoning, land use and county budget. Residents have "
                "continued pushing for a data-center moratorium; no vote "
                "confirmed yet.",
     "meets": "See the county's published Board of Commissioners calendar.",
     "where": "Board of Commissioners Administration Building, 327 N. Ashley Street, Valdosta, GA 31601",
     "agenda_url": "https://www.lowndescounty.com/AgendaCenter/Board-of-Commissioners-1",
     "comment_process": "See the board's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.lowndescounty.com/181/Board-of-Commissioners",
     "as_of": "2026-08-12", "source": "https://www.lowndescounty.com/181/Board-of-Commissioners"},

    {"locality": "Clark County", "state": "NV",
     "body": "Board of County Commissioners",
     "decides": "Zoning and land-use approval for data centers in "
                "unincorporated Clark County. Discussed the application/"
                "approval process at a Jul 2026 meeting (requested by "
                "Commissioner Tick Segerblom) amid environmental-group calls "
                "for a moratorium, but took no action on a pause.",
     "meets": "See the county's published Commission meeting calendar.",
     "where": "Clark County Government Center, 500 S Grand Central Pkwy, Las Vegas, NV 89106",
     "agenda_url": "https://www.clarkcountynv.gov/government/board_of_county_commissioners/index.php",
     "comment_process": "See the county's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.clarkcountynv.gov/government/board_of_county_commissioners/index.php",
     "as_of": "2026-08-12", "source": "https://nevadacurrent.com/2026/07/08/clark-county-commission-hears-push-for-data-center-moratorium-but-takes-no-action/"},

    {"locality": "St. Joseph", "state": "MO",
     "body": "City Council",
     "decides": "Zoning and land use. A proposed data center on Pickett "
                "Road drew a town-hall-style informational meeting Jul 16, "
                "2026 at the Missouri Theater; no moratorium confirmed.",
     "meets": "Every other Monday, 5:30 p.m.",
     "where": "Council Chamber, City Hall, 1100 Frederick Avenue, St. Joseph, MO 64501",
     "agenda_url": "https://www.stjosephmo.gov/AgendaCenter",
     "comment_process": "See the city's published agendas for the "
                        "public-comment process for a specific meeting.",
     "phone": "816-271-4730", "email": "",
     "website": "https://www.stjosephmo.gov/169/Agendas-Minutes",
     "as_of": "2026-08-12", "source": "https://www.stjosephmo.gov/169/Agendas-Minutes"},

    {"locality": "Alliance", "state": "OH",
     "body": "City Council",
     "decides": "Zoning and land use. Residents have organized opposition "
                "to a proposed data center ('We don't need them here') and "
                "the council has taken some action in response; confirm the "
                "specifics before citing a status.",
     "meets": "1st and 3rd Monday, 6:00 p.m.",
     "where": "Alliance Municipal Court Chambers, 470 E. Market St., Alliance, OH 44601",
     "agenda_url": "https://www.cityofalliance.com/agendacenter",
     "comment_process": "See the city's published agendas for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.cityofalliance.com/220/City-Council",
     "as_of": "2026-08-12", "source": "https://www.cityofalliance.com/220/City-Council"},

    {"locality": "Montour County", "state": "PA",
     "body": "Board of Commissioners",
     "decides": "Zoning and land use. Denied a data-center rezoning "
                "request; a real outcome, though short of a moratorium.",
     "meets": "See the county's published meeting agendas.",
     "where": "Montour County Administration Center, Conference Room B, 435 East Front Street, Danville, PA 17821",
     "agenda_url": "https://www.montourcounty.gov/home/minutes-and-agendas",
     "comment_process": "See the county's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "570-271-3000", "email": "",
     "website": "https://www.montourcounty.gov/departments/commissioners",
     "as_of": "2026-08-12", "source": "https://www.montourcounty.gov/home/minutes-and-agendas"},

    {"locality": "Fairfax County", "state": "VA",
     "body": "Board of Supervisors",
     "decides": "Zoning and land use in one of the country's largest data "
                "center markets. Residents have publicly questioned Dominion "
                "Energy over a specific data-center proposal's power needs.",
     "meets": "2 Tuesdays per month.",
     "where": "Board Auditorium, Fairfax County Government Center, 12000 Government Center Parkway, Fairfax, VA 22035",
     "agenda_url": "https://www.fairfaxcounty.gov/boardofsupervisors/board-supervisors-meetings",
     "comment_process": "See the board's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.fairfaxcounty.gov/boardofsupervisors/",
     "as_of": "2026-08-12", "source": "https://www.fairfaxcounty.gov/boardofsupervisors/board-supervisors-meetings"},

    {"locality": "Loudoun County", "state": "VA",
     "body": "Board of Supervisors",
     "decides": "Zoning and land use in 'Data Center Alley', the largest "
                "concentration of data centers in the world. Adopted a Data "
                "Center Standards & Locations Comprehensive Plan Amendment "
                "and Zoning Ordinance Amendment requiring Special Exception "
                "approval for new data-center uses; residents separately "
                "report a rising flood of noise and fumes complaints.",
     "meets": "See the board's published meeting calendar.",
     "where": "Board Room, Loudoun County Government Center, 1 Harrison Street SE, Leesburg, VA 20175",
     "agenda_url": "https://www.loudoun.gov/3426/Board-of-Supervisors-Meetings-Packets",
     "comment_process": "See the board's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.loudoun.gov/86/Board-of-Supervisors",
     "as_of": "2026-08-12", "source": "https://www.loudoun.gov/6221/Phase-1-Project-Plan-for-Data-Center-Sta"},

    {"locality": "Lee County", "state": "NC",
     "body": "Board of Commissioners",
     "decides": "Zoning, land use and county budget, seven-member board. "
                "Residents have demanded a pause on a data center proposal, "
                "alleging the approval process involved deception.",
     "meets": "One work session and one regular business meeting per "
              "month (except Dec/Jun).",
     "where": "Lee County, Sanford, NC",
     "agenda_url": "https://leecountync.gov/government/board_of_commissions/meeting_videos.php",
     "comment_process": "Public comment accepted at any regular business "
                        "meeting.",
     "phone": "", "email": "",
     "website": "https://leecountync.gov/",
     "as_of": "2026-08-12", "source": "https://leecountync.gov/news_detail_T12_R264.php"},

    {"locality": "Eagle Creek Township", "state": "IN",
     "body": "Lake County Council",
     "decides": "County-level zoning approval for townships including Eagle "
                "Creek Township. Approved zoning for a data center there "
                "despite resident opposition — a real, already-decided "
                "outcome, not an open fight.",
     "meets": "See the county's published meeting schedule.",
     "where": "Lake County Government Center, Crown Point, IN",
     "agenda_url": "https://lakecountyin.gov/",
     "comment_process": "See the county's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "219-996-4572", "email": "",
     "website": "https://lakecountyin.gov/departments/eagle-creek-township",
     "as_of": "2026-08-12", "source": "https://lakecountyin.gov/departments/eagle-creek-township"},

    {"locality": "Shreveport", "state": "LA",
     "body": "City Council",
     "decides": "Zoning and land use. Residents packed a town hall over "
                "data-center concerns; no vote confirmed yet.",
     "meets": "2nd and 4th Tuesday, 3:00 p.m.",
     "where": "Government Plaza, 505 Travis St., 1st Floor, Shreveport, LA 71101",
     "agenda_url": "https://www.shreveportla.gov/201/City-Council",
     "comment_process": "See the council's published agendas for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.shreveportla.gov/201/City-Council",
     "as_of": "2026-08-12", "source": "https://www.shreveportla.gov/201/City-Council"},

    {"locality": "Caddo Parish", "state": "LA",
     "body": "Parish Commission",
     "decides": "Zoning and land use across 12 single-member districts. "
                "Residents have raised water and wildlife concerns over a "
                "proposed data center.",
     "meets": "Regular session the Thursday after the 1st and 3rd Tuesday; "
              "work session the preceding Monday.",
     "where": "Caddo Parish, Shreveport, LA",
     "agenda_url": "https://caddo.gov/commission-clerks-office/",
     "comment_process": "See the commission's published agendas for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://caddo.gov/commission-clerks-office/",
     "as_of": "2026-08-12", "source": "https://caddo.gov/commission-clerks-office/"},

    {"locality": "Mason County", "state": "WV",
     "body": "County Commission",
     "decides": "County-level land use. Residents have pressed commissioners "
                "on the Monarch Compute Campus, a 1,100-acre hyperscale "
                "complex (North Point Pleasant + an expansion at Lakin); no "
                "moratorium confirmed.",
     "meets": "4 regular sessions/year at the courthouse (statutory "
              "minimum); see the county's agenda page for the full schedule.",
     "where": "Mason County Courthouse, Point Pleasant, WV",
     "agenda_url": "https://masoncountywv.gov/agenda/",
     "comment_process": "See the commission's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://masoncountywv.gov/government/mason-county-commissioners/",
     "as_of": "2026-08-12", "source": "https://masoncountywv.gov/government/mason-county-commissioners/"},

    {"locality": "Mason County", "state": "KY",
     "body": "Fiscal Court",
     "decides": "County-level land use. Voted May 22, 2026 to rezone 28 "
                "properties (2,080 acres north of Germantown Road) for rural "
                "industrial use — proposed by the Maysville-Mason County "
                "Industrial Authority for a 6-building, undisclosed "
                "'Fortune 50' data-center campus. A real, already-decided "
                "outcome, not an open fight.",
     "meets": "See the Maysville data-center information page for hearing-"
              "specific dates.",
     "where": "Mason County, Maysville, KY",
     "agenda_url": "https://www.cityofmaysvilleky.gov/departments/codes_department/data_center.php",
     "comment_process": "Contact Planning & Zoning Administrator George "
                        "Larger, 606-564-2719, georgelarger@cityofmaysvilleky.gov.",
     "phone": "606-564-2719", "email": "georgelarger@cityofmaysvilleky.gov",
     "website": "https://www.cityofmaysvilleky.gov/departments/codes_department/data_center.php",
     "as_of": "2026-08-12", "source": "https://www.weku.org/the-commonwealth/2026-05-26/mason-county-gives-final-approval-on-rezoning-properties-for-data-center-construction"},

    {"locality": "Amherst", "state": "OH",
     "body": "Board of Zoning Appeals",
     "decides": "Use variances. Heard a proposal to convert a Nordson Drive "
                "industrial site into a data center; a July 30, 2026 hearing "
                "drew hundreds, with many turned away at a capacity limit.",
     "meets": "Last Wednesday of the month, 6:30 p.m.",
     "where": "Council Chambers, 206 South Main Street, Amherst, OH 44001",
     "agenda_url": "https://amherstohio.org/planning-commission/board-of-zoning-appeals/",
     "comment_process": "Request an agenda/minutes by mail (self-addressed "
                        "stamped envelope to the Building Department) or in "
                        "person, 480 Park Avenue.",
     "phone": "", "email": "",
     "website": "https://amherstohio.org/planning-commission/board-of-zoning-appeals/",
     "as_of": "2026-08-12", "source": "https://www.cleveland19.com/2026/07/30/capacity-limits-push-amherst-residents-outside-zoning-board-hears-data-center-proposal/"},

    {"locality": "Wisconsin Rapids", "state": "WI",
     "body": "Common Council",
     "decides": "Zoning, land use and city budget, 8-member council. "
                "Residents have pressed for answers at a heated data-center "
                "meeting; no vote confirmed yet.",
     "meets": "See the city's Agenda Center for the current schedule.",
     "where": "City Hall Council Chambers, 444 West Grand Avenue, Wisconsin Rapids, WI 54494",
     "agenda_url": "https://www.wirapids.gov/AgendaCenter",
     "comment_process": "See the council's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.wirapids.gov/161/Common-Council",
     "as_of": "2026-08-12", "source": "https://www.wirapids.gov/161/Common-Council"},

    {"locality": "Forsyth County", "state": "NC",
     "body": "Board of Commissioners",
     "decides": "Zoning, land use and county budget, 7-member board. "
                "Weighing a data-center decision amid statewide debate over "
                "how NC counties should respond to the industry.",
     "meets": "Briefings 2:00 p.m. two Mondays/month; meetings 2:00 p.m. two "
              "Thursdays/month (one at 6:00 p.m. quarterly).",
     "where": "Forsyth County, Winston-Salem, NC",
     "agenda_url": "https://coforsythnc.civicweb.net/portal/",
     "comment_process": "See the board's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://co.forsyth.nc.us/Commissioners/default.aspx",
     "as_of": "2026-08-12", "source": "https://co.forsyth.nc.us/Commissioners/default.aspx"},

    {"locality": "Chesterfield County", "state": "VA",
     "body": "Board of Supervisors",
     "decides": "Zoning and land use. Approved three Google data-center "
                "campuses ($9B+ investment) in a public vote; residents say "
                "the county used NDAs and concealed Google's involvement "
                "until after approval, raising transparency concerns.",
     "meets": "See the county's published Board of Supervisors meeting "
              "calendar.",
     "where": "Chesterfield County Public Meeting Room, 10001 Iron Bridge Road, Chesterfield, VA 23832",
     "agenda_url": "https://www.chesterfield.gov/datacenters",
     "comment_process": "See the board's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.chesterfield.gov/datacenters",
     "as_of": "2026-08-12", "source": "https://www.chesterfield.gov/datacenters"},

    {"locality": "Edgewater", "state": "FL",
     "body": "City Council",
     "decides": "Zoning and land use. Considering a November 2026 ballot "
                "measure that would ban data centers citywide (there are "
                "none in Edgewater today) — ask this locality's own page "
                "whether the referendum passed before citing a status.",
     "meets": "1st Monday of the month, 6:00 p.m.",
     "where": "Council Chambers, 104 N. Riverside Drive, Edgewater, FL 32132",
     "agenda_url": "https://cityofedgewater.granicus.com/MediaPlayer.php?view_id=2",
     "comment_process": "See the council's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.cityofedgewater.org/citycouncil/page/council-meeting",
     "as_of": "2026-08-12", "source": "https://www.clickorlando.com/news/local/2026/07/20/edgewater-could-let-voters-decide-whether-to-ban-data-centers-citywide/"},

    {"locality": "North Richland Hills", "state": "TX",
     "body": "City Council",
     "decides": "Zoning and land use. A second data center is under "
                "discussion after an earlier approval; many residents "
                "oppose it.",
     "meets": "2nd and 4th Monday, 7:00 p.m.",
     "where": "Council Chamber, City Hall, 4301 City Point Drive, North Richland Hills, TX 76180",
     "agenda_url": "https://nrhtx.legistar.com/MainBody.aspx",
     "comment_process": "Complete a Public Meeting Appearance Form before "
                        "the meeting; 3-minute limit per speaker.",
     "phone": "", "email": "",
     "website": "https://www.nrhtx.com/359/City-Council",
     "as_of": "2026-08-12", "source": "https://www.nrhtx.com/359/City-Council"},

    {"locality": "Castro County", "state": "TX",
     "body": "Commissioners Court",
     "decides": "County-level land use. Residents cite water, land and "
                "pollution fears over a proposed data center.",
     "meets": "See the county's published Commissioners Court minutes page.",
     "where": "100 E. Bedford, Room 111, Dimmitt, TX 79027",
     "agenda_url": "https://www.co.castro.tx.us/page/castro.Commissioners.Court",
     "comment_process": "See the court's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "806-647-3338", "email": "",
     "website": "https://www.co.castro.tx.us/page/castro.Commissioners.Court",
     "as_of": "2026-08-12", "source": "https://www.co.castro.tx.us/page/castro.Commissioners.Court"},

    {"locality": "Archer County", "state": "TX",
     "body": "Commissioners Court",
     "decides": "County-level land use. Held a public forum on data-center "
                "and battery-storage (BESS) projects; officials have "
                "encouraged residents to attend court meetings with "
                "concerns.",
     "meets": "See the county's published public-notices page.",
     "where": "Archer County Courthouse, 100 S Center St., Archer City, TX 76351",
     "agenda_url": "https://www.co.archer.tx.us/page/archer.Commissioners.Court",
     "comment_process": "See the court's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.co.archer.tx.us/page/archer.Commissioners.Court",
     "as_of": "2026-08-12", "source": "https://www.archercountynews.com/county-holds-public-forum-over-data-center-bess-projects"},

    {"locality": "Guadalupe County", "state": "TX",
     "body": "Commissioners Court",
     "decides": "Tax-abatement and development agreements. Sued by the Data "
                "Center Action Coalition and residents over the CloudBurst "
                "and Palomino Alpha data-center agreements, alleging Texas "
                "Open Meetings Act violations and an undisclosed conflict of "
                "interest (County Judge Kyle Kutscher's family owns land "
                "within the Palomino Alpha site).",
     "meets": "See the county's published Commissioners Court calendar.",
     "where": "Guadalupe County, Seguin, TX",
     "agenda_url": "https://www.co.guadalupe.tx.us/",
     "comment_process": "See the court's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.co.guadalupe.tx.us/",
     "as_of": "2026-08-12", "source": "https://www.ksat.com/news/local/2026/07/24/data-centers-draw-backlash-lawsuit-in-guadalupe-county-as-residents-raise-transparency-concerns/"},

    {"locality": "Cass County", "state": "NE",
     "body": "Board of Commissioners",
     "decides": "County-level land use, 5-member board. Residents are "
                "pushing back on a proposed data center over water and "
                "farmland concerns.",
     "meets": "Every other Tuesday, 8:00 a.m.",
     "where": "Cass County Courthouse, Room 101, Plattsmouth, NE 68048",
     "agenda_url": "https://www.casscountyne.gov/board-of-commissioners-meetings-agendas",
     "comment_process": "See the board's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "402-296-9304", "email": "",
     "website": "https://www.casscountyne.gov/board-of-commissioners",
     "as_of": "2026-08-12", "source": "https://www.casscountyne.gov/board-of-commissioners"},

    {"locality": "Posey County", "state": "IN",
     "body": "Board of Commissioners",
     "decides": "County-level land use. Commissioners acknowledged signing "
                "an NDA with a developer after residents raised data-center "
                "concerns; no application has been filed, though farmers "
                "near Boberg and Hoenert roads have been approached about "
                "leasing land.",
     "meets": "1st and 3rd Tuesday, 9:00 a.m.",
     "where": "Hovey House, Posey County, IN",
     "agenda_url": "https://www.poseycountyin.gov/meetings/",
     "comment_process": "See the county's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.poseycountyin.gov/welcome/",
     "as_of": "2026-08-12", "source": "https://www.14news.com/2026/07/21/amidst-data-center-concerns-posey-co-commissioners-reveal-theyve-signed-an-nda/"},

    {"locality": "Hallam", "state": "NE",
     "body": "Village Board",
     "decides": "Zoning/site approval. Monolith (a carbon-black producer, "
                "partnering with AI-factory firm Crusoe) is seeking a text "
                "amendment and site approval for a 10-acre, 35 MW data "
                "center on its Olive Creek Campus; asked for village-board "
                "approval by Sep 7, 2026.",
     "meets": "See the village's meeting minutes for the current schedule.",
     "where": "Hallam, NE",
     "agenda_url": "https://nebraskapublicmedia.org/en/news/news-articles/hallam-residents-pack-town-hall-for-monoliths-proposed-data-center-expansion/",
     "comment_process": "See the village's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://nebraskapublicmedia.org/en/news/news-articles/we-need-to-embrace-it-hallam-commission-hears-data-center-plans/",
     "as_of": "2026-08-12", "source": "https://nebraskapublicmedia.org/en/news/news-articles/hallam-residents-pack-town-hall-for-monoliths-proposed-data-center-expansion/"},

    {"locality": "Allegheny County", "state": "PA",
     "body": "County Council",
     "decides": "Legislative branch, 15 members. Residents have asked the "
                "county to step in on data-center impacts (air quality, "
                "water, electricity, property values) via its Climate "
                "Action Plan process, but county regulatory power is "
                "limited — Pennsylvania municipalities, not counties, "
                "control zoning, and a legal land use can't simply be "
                "prohibited. The county is drafting a model zoning ordinance "
                "for municipalities to adopt.",
     "meets": "2 Tuesdays/month, 5:00 p.m.",
     "where": "Allegheny County Courthouse, Suite 119, 436 Grant Street, Pittsburgh, PA 15219",
     "agenda_url": "https://www.alleghenycounty.us/Government/Row-Offices/County-Council/Council-Meetings",
     "comment_process": "See the council's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.alleghenycounty.us/Government/Row-Offices/County-Council",
     "as_of": "2026-08-12", "source": "https://www.monvalleyindependent.com/2026/06/24/data-center-concerns-have-residents-asking-allegheny-county-to-step-in-but-its-power-may-be-limited/"},

    {"locality": "LeRay", "state": "NY",
     "body": "Town Board",
     "decides": "Zoning and land use. A real-estate broker has been "
                "marketing hundreds of acres in the town for a data center; "
                "the board agreed to widen a proposed moratorium to 12 "
                "months after resident pushback, with a public hearing and "
                "vote set for Aug 13, 2026 — confirm the outcome before "
                "citing a status.",
     "meets": "2nd Thursday of the month (except Nov.), 4:00 p.m.",
     "where": "Municipal Office Building, 8650 LeRay Street, Evans Mills, NY 13637",
     "agenda_url": "https://www.townofleray.gov/town-board",
     "comment_process": "See the town's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.townofleray.gov/",
     "as_of": "2026-08-12", "source": "https://www.northcountrypublicradio.org/news/story/53719/20260720/near-watertown-locals-push-to-restrict-data-centers-as-talks-of-a-new-facility-loom"},

    {"locality": "Limerick Township", "state": "PA",
     "body": "Board of Supervisors",
     "decides": "Conditional-use approvals. Held Data Center Conditional "
                "Use Hearings with increased security measures amid resident "
                "opposition; no outcome confirmed yet.",
     "meets": "1st and 3rd Tuesday, 7:00 p.m.",
     "where": "Limerick Township Municipal Building, 646 W Ridge Pike, Limerick, PA 19468",
     "agenda_url": "https://www.limerickpa.org/AgendaCenter/Board-of-Supervisors-2/",
     "comment_process": "See the board's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "610-495-6432", "email": "",
     "website": "https://www.limerickpa.org/202/Board-of-Supervisors",
     "as_of": "2026-08-12", "source": "https://www.limerickpa.org/m/newsflash/home/detail/437"},

    {"locality": "Prairie Township", "state": "OH",
     "body": "Board of Trustees",
     "decides": "Zoning (via the Commercial Building and Zoning "
                "Department) and the Big Darby Accord, a land-use agreement "
                "protecting the Big Darby Creek watershed. Drafting a zoning "
                "amendment for data centers; residents have raised concerns "
                "about a potential facility on Big Darby Accord land.",
     "meets": "Every other Wednesday, 7:00 p.m.",
     "where": "Township Hall, 23 Maple Drive, Columbus, OH 43228",
     "agenda_url": "https://www.prairietownship.org/AgendaCenter",
     "comment_process": "See the township's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.prairietownship.org/142/Darby-Accord",
     "as_of": "2026-08-12", "source": "https://www.prairietownship.org/142/Darby-Accord"},

    {"locality": "Shalersville Township", "state": "OH",
     "body": "Board of Trustees",
     "decides": "Zoning and land use. A local developer and Bitdeer (global "
                "AI-computing firm) have a contract to buy ~257 acres at the "
                "Turnpike Commerce Center for a 15-building AI data-center "
                "hub; residents are outraged.",
     "meets": "1st Tuesday 7:00 p.m. and 3rd Tuesday 5:30 p.m.",
     "where": "Town Hall, 9090 St. Rt. 44, Ravenna, OH 44266",
     "agenda_url": "https://www.shalersvilletwp.com/meeting-minutes",
     "comment_process": "See the township's published minutes for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "Shalersvilletownship@yahoo.com",
     "website": "https://www.shalersvilletwp.com/",
     "as_of": "2026-08-12", "source": "https://www.news5cleveland.com/news/local-news/local-developer-global-tech-firm-plan-major-data-center-project-in-portage-county"},

    {"locality": "Middleton Township", "state": "OH",
     "body": "Board of Trustees",
     "decides": "Zoning. Voted (split, July 2026) to approve rezoning 32 "
                "more acres — 13 parcels from residential/agricultural to "
                "M-1 industrial — for a $750M Fortune 200 data center near "
                "I-75/SR-582. A real, already-decided outcome.",
     "meets": "1st and 3rd Wednesday, 6:00 p.m.",
     "where": "Township Building, 21745 N. Dixie Highway, Bowling Green, OH 43402",
     "agenda_url": "https://www.middletontownship.com/",
     "comment_process": "See the township's published minutes for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.middletontownship.com/",
     "as_of": "2026-08-12", "source": "https://bgindependentmedia.org/with-split-vote-middleton-township-approves-zoning-change-for-acreage-bordering-data-center/"},

    {"locality": "Brownhelm Township", "state": "OH",
     "body": "Board of Trustees",
     "decides": "Zoning and land use. No project has been proposed, but "
                "trustees have begun discussing a data-center regulation "
                "modeled on Montour County, PA's ordinance and say data "
                "centers are 'neither wanted nor welcome' in the township.",
     "meets": "2nd Monday of the month, 6:00 p.m.",
     "where": "Township Hall, 1940 N. Ridge Rd., Vermilion, OH 44089",
     "agenda_url": "https://www.brownhelm.us/minutes",
     "comment_process": "See the township's published minutes for the "
                        "public-comment process for a specific meeting.",
     "phone": "440-984-2243", "email": "office@brownhelm.us",
     "website": "https://www.brownhelm.us/",
     "as_of": "2026-08-12", "source": "https://www.news5cleveland.com/news/local-news/oh-lorain/fighting-a-ghost-lorain-county-community-hopes-to-get-ahead-of-possible-data-center-development"},

    {"locality": "South Strabane Township", "state": "PA",
     "body": "Board of Supervisors",
     "decides": "Zoning and ordinances. Unanimously adopted two data-center "
                "ordinances (Jun 2026) after 6+ months of public meetings: a "
                "development ordinance (1,500-ft residential setback, "
                "30-acre minimum lot size, height limits) and a separate "
                "noise/dust ordinance — real, already-decided regulatory "
                "outcomes, not a pause or ban.",
     "meets": "4th Tuesday, 6:30 p.m.",
     "where": "South Strabane Township, Washington County, PA",
     "agenda_url": "https://www.southstrabane.com/board-supervisors",
     "comment_process": "See the board's published minutes for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.southstrabane.com/board-supervisors",
     "as_of": "2026-08-12", "source": "https://www.observer-reporter.com/news/local-news/2026/jun/11/south-strabane-adopts-data-center-noise-ordinances/"},

    {"locality": "Asbury Park", "state": "NJ",
     "body": "City Council",
     "decides": "Zoning and city budget. Adopted Resolution 2026-264 urging "
                "Gov. Sherrill and the NJ Legislature to enact a statewide "
                "data-center moratorium — a policy statement, not a local "
                "zoning ban.",
     "meets": "See the city's published agenda for the current schedule.",
     "where": "City Hall, 1 Municipal Plaza, Asbury Park, NJ 07712",
     "agenda_url": "https://www.cityofasburypark.com/129/City-Council-Meetings",
     "comment_process": "See the council's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.cityofasburypark.com/158/Mayor-City-Council",
     "as_of": "2026-08-12", "source": "https://www.cityofasburypark.com/158/Mayor-City-Council"},

    {"locality": "Martindale-Brightwood", "state": "IN",
     "body": "Metropolitan Development Commission (Indianapolis)",
     "decides": "Rezoning within Indianapolis/Marion County. Approved "
                "rezoning (Apr 2026) for a $500M Metrobloks data center on "
                "14 acres near Brightwood Plaza despite months of pushback; "
                "five residents and the Hoosier Environmental Council sued "
                "in Marion County Superior Court (May 2026) seeking an "
                "injunction, citing noise, air quality, water use, "
                "brownfield contamination and environmental-justice concerns "
                "in a historically Black neighborhood shaped by decades of "
                "industrial and rail activity.",
     "meets": "See the Indianapolis MDC's published meeting schedule.",
     "where": "Indianapolis, IN",
     "agenda_url": "https://www.indy.gov/agency/metropolitan-development-commission",
     "comment_process": "See the MDC's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.indy.gov/agency/metropolitan-development-commission",
     "as_of": "2026-08-12", "source": "https://www.wfyi.org/wfyi-news/2026-05-12/martindale-brightwood-data-center-court-challenge"},

    {"locality": "Bristol", "state": "IN",
     "body": "Town Council",
     "decides": "Zoning (jointly with the Elkhart County Plan Commission). "
                "The 'Bristol Innovation Project' rezoning — nearly 1,000 "
                "acres of farmland for a planned unit development that "
                "could include a data center — was withdrawn by the "
                "petitioner Aug 3, 2026, after the county Plan Commission "
                "sent it to county council with an unfavorable recommendation "
                "following a 5-hour, 500+-person hearing. A real, "
                "already-decided outcome: the rezoning did not happen.",
     "meets": "See the town's published meeting packets.",
     "where": "Bristol, IN",
     "agenda_url": "https://bristol.in.gov/",
     "comment_process": "See the town's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://bristol.in.gov/",
     "as_of": "2026-08-12", "source": "https://www.insideindianabusiness.com/articles/bristol-council-accepts-withdrawal-of-rezoning-application-after-july-uproar"},

    {"locality": "Wolfe County", "state": "KY",
     "body": "Fiscal Court",
     "decides": "County-level land use. A resident has complained about "
                "ongoing industrial hum from a data center; no vote "
                "confirmed yet.",
     "meets": "2nd Tuesday of the month, 1:30 p.m.",
     "where": "Wolfe County Courthouse, Campton, KY",
     "agenda_url": "https://www.wolfecountyky.com/home/resources/",
     "comment_process": "See the court's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "606-668-3040", "email": "",
     "website": "https://www.wolfecountyky.com/home/resources/",
     "as_of": "2026-08-12", "source": "https://www.lex18.com/"},

    {"locality": "Saline Township", "state": "MI",
     "body": "Township Board",
     "decides": "Zoning and land use. Oracle/OpenAI's $43B 'The Barn' data "
                "center is under construction after a consent judgment "
                "resolved a developer lawsuit. Board voted 5-0 to approve a "
                "12-year, 50% tax abatement; an earlier cap was dropped "
                "after township counsel warned it violated the consent "
                "judgment. EGLE wastewater discharge permit for the Saline "
                "River is under public review through Aug 24, 2026.",
     "meets": "2nd Wednesday of the month, 7:00 p.m.",
     "where": "Saline Township Hall, 5731 Braun Rd, Saline, MI 48176",
     "agenda_url": "https://salinetownship.org/meeting-agendas.php",
     "comment_process": "Contact the Clerk to be added to the agenda. "
                        "Planning Commission meets 1st Tuesday at 7:00 p.m.",
     "phone": "734-429-9968", "email": "salinetownship@gmail.com",
     "website": "https://salinetownship.org/",
     "as_of": "2026-08-12",
     "source": "https://salinetownship.org/board.html"},

    {"locality": "Lubbock", "state": "TX",
     "body": "City Council",
     "decides": "Zoning and annexation. Council approved (Jul 29, 2026) "
                "annexation of an 8-acre tract and rezoning of 52 acres "
                "from residential to industrial, tied to LEDA data-center "
                "recruitment; separately approved 'Project Infrared' "
                "(50,000 sq ft inference data center). Nearly 2,500 "
                "residents signed a petition for an 18-month moratorium; "
                "mayor has indicated the council opposes a moratorium.",
     "meets": "2nd and 4th Tuesday of the month, 2:00 p.m.",
     "where": "City Council Chambers, Citizens Tower, 1314 Avenue K, "
              "Lubbock, TX 79401",
     "agenda_url": "https://www.mylubbock.us/AgendaCenter/City-Council-52/",
     "comment_process": "In-person: sign up outside chambers by 2:00 p.m. "
                        "Remote: submit to City Secretary by 11:00 a.m. "
                        "on the meeting date.",
     "phone": "806-775-2061", "email": "",
     "website": "https://www.mylubbock.us/170/City-Council-Mayor",
     "as_of": "2026-08-12",
     "source": "https://www.mylubbock.us/170/City-Council-Mayor"},

    {"locality": "Statesboro", "state": "GA",
     "body": "City Council",
     "decides": "Zoning and annexation (with Planning Commission). "
                "Planning Commission recommended rezoning for a Burkhalter "
                "Road data center; council has final say.",
     "meets": "1st Tuesday at 9:00 a.m., 3rd Tuesday at 5:30 p.m.",
     "where": "Statesboro City Hall, Statesboro, GA 30458",
     "agenda_url": "https://www.statesboroga.gov/",
     "comment_process": "See the city's published agenda for the "
                        "public-comment process for a specific meeting.",
     "phone": "", "email": "",
     "website": "https://www.statesboroga.gov/",
     "as_of": "2026-08-12",
     "source": "https://www.statesboroga.gov/"},

    {"locality": "Newberry County", "state": "SC",
     "body": "County Council",
     "decides": "Land use and zoning (7 members, Council-Administrator). "
                "Unanimously denied 'Project Altair' land-sale ordinance "
                "(Jun 2026) and confirmed a 12-month moratorium on new "
                "data-center permits (Jul 16, 2026). Staff directed to "
                "research where data centers would be appropriate.",
     "meets": "1st and 3rd Wednesday of the month, 6:00 p.m.",
     "where": "Newberry County Courthouse Annex, 1309 College Street, "
              "Newberry, SC 29108",
     "agenda_url": "https://www.newberrycounty.gov/agendas-minutes",
     "comment_process": "Sign up before the meeting begins. Contact the "
                        "county office (803-321-2100) for details.",
     "phone": "803-321-2100", "email": "",
     "website": "https://www.newberrycounty.gov/county-council",
     "as_of": "2026-08-12",
     "source": "https://www.newberrycounty.gov/county-council"},

    {"locality": "Hogansville", "state": "GA",
     "body": "City Council",
     "decides": "Zoning and ordinances (Mayor + 5 council members). QTS "
                "(Eagle South LLC) has proposed a 600 MW data center on "
                "~435 acres. Council approved a 90-day moratorium (late "
                "2025), extended 30 days in Jul 2026; developing a new "
                "data-center ordinance with consultant Canvas Planning and "
                "a citizen input committee.",
     "meets": "1st and 3rd Monday of the month, 7:00 p.m.",
     "where": "Council Chambers, 111 High Street, Hogansville, GA 30230",
     "agenda_url": "https://www.cityofhogansville.org/AgendasAndMinutes.aspx",
     "comment_process": "Meeting participation requests must be submitted "
                        "no later than noon on the Wednesday before the "
                        "meeting.",
     "phone": "706-637-8629",
     "email": "cityhall@cityofhogansville.org",
     "website": "https://www.cityofhogansville.org/MayorAndCouncil.aspx",
     "as_of": "2026-08-12",
     "source": "https://www.cityofhogansville.org/MayorAndCouncil.aspx"},

    {"locality": "Ottawa", "state": "KS",
     "body": "City Commission",
     "decides": "Land use and contracts (5 commissioners, commission-manager "
                "form). Approved a $5.3M sale of Proximity Park (300 acres) "
                "to Lightfield Energy LLC for data centers + 440 MW gas "
                "plant (Dec 2024). Community group 'Ottawa United' launched "
                "a ballot petition to ban data centers over 25 MW; aiming "
                "for 600 signatures.",
     "meets": "Wednesdays: 1st at 7:00 p.m., 2nd at 4:00 p.m., "
              "3rd at 10:00 a.m., 4th at 4:00 p.m. (study session).",
     "where": "City Hall, 101 S. Hickory, Ottawa, KS 66067",
     "agenda_url": "https://www.ottawaks.gov/AgendaCenter",
     "comment_process": "Persons may address the Commission on agenda "
                        "items as each is called. Non-agenda items when "
                        "called upon by the Mayor. 3-minute limit.",
     "phone": "785-229-3600", "email": "",
     "website": "https://www.ottawaks.gov/",
     "as_of": "2026-08-12",
     "source": "https://www.ottawaks.gov/"},

    {"locality": "St. Charles Parish", "state": "LA",
     "body": "Parish Council",
     "decides": "Zoning and ordinances (9 members, Home Rule Charter). "
                "Rejected a proposed 8-month moratorium (Apr 2026, 5-3) "
                "but unanimously adopted the parish's first data-center "
                "zoning regulations (Jun 2026): M-1/M-2 zones only, "
                "300-ft buffer from residences, 55 dB noise limit, "
                "backup generator testing weekdays 7a-6p only.",
     "meets": "1st and 3rd Monday of the month, 6:00 p.m.",
     "where": "Council Chambers, 2nd Floor, St. Charles Parish Courthouse, "
              "15045 River Road, Hahnville, LA 70057",
     "agenda_url": "https://www.stcharlesparish.gov/government/council-meeting",
     "comment_process": "Submit a written request to address the Council. "
                        "5-minute limit per speaker; additional 3 minutes "
                        "with two-thirds consent.",
     "phone": "985-783-5125", "email": "",
     "website": "https://www.stcharlesparish.gov/government/parish-council",
     "as_of": "2026-08-12",
     "source": "https://www.stcharlesparish.gov/government/parish-council"},

    {"locality": "Colleton County", "state": "SC",
     "body": "County Council",
     "decides": "Zoning and land use (5 members, Council-Administrator). "
                "Unanimously adopted a 6-month moratorium on data-center "
                "approvals (Jul 7, 2026) via Ordinance 26-O-04. Planning "
                "Commission has approved a 'digital infrastructure overlay "
                "district' text amendment; council has final say.",
     "meets": "1st Monday of the month, 6:00 p.m.",
     "where": "Council Chambers, Old Jail Building, 109 Benson Street, "
              "2nd Floor, Walterboro, SC 29488",
     "agenda_url": "https://www.colletoncounty.org/county-council/agendas-minutes",
     "comment_process": "Online comments at colletoncounty.org/public-comments. "
                        "In-person comment available at meetings.",
     "phone": "843-549-1725",
     "email": "administration@colletoncounty.org",
     "website": "https://www.colletoncounty.org/county-council",
     "as_of": "2026-08-12",
     "source": "https://www.colletoncounty.org/county-council"},

    {"locality": "Salix", "state": "IA",
     "body": "City Council",
     "decides": "Zoning and land use (Mayor + 5 council members). "
                "MidAmerican Energy proposed a data center on ~900 acres "
                "of farmland annexed in Apr 2026. Council voted 3-2 "
                "(Jul 8, 2026) to advance a 1-year moratorium concept; "
                "formal moratorium vote scheduled Aug 12, 2026.",
     "meets": "2nd Wednesday of the month, 7:00 p.m.",
     "where": "Council Chambers behind City Hall, 317 Tipton Street, "
              "Salix, IA 51052",
     "agenda_url": "https://salixiowa.com/",
     "comment_process": "Public hearings held for zoning/annexation "
                        "matters. Contact the Clerk for details.",
     "phone": "712-946-5645",
     "email": "salixiowa@gmail.com",
     "website": "https://salixiowa.com/council",
     "as_of": "2026-08-12",
     "source": "https://salixiowa.com/council"},

    {"locality": "Dodge County", "state": "WI",
     "body": "Board of Supervisors",
     "decides": "Zoning in unincorporated areas (29 supervisors). Board "
                "voted 29-2 (Aug 2026) to approve an 18-month moratorium "
                "on data-center development in county-zoned unincorporated "
                "areas, after concerns about a Beaver Dam-area data "
                "center's impact on neighbors' water.",
     "meets": "3rd Tuesday of most months, 6:00 p.m. (Apr and Nov: 9:00 a.m.)",
     "where": "County Board Room, 4th floor, Dodge County Administration "
              "Building, 127 E. Oak Street, Juneau, WI 53039",
     "agenda_url": "https://www.co.dodge.wi.gov/government/county-board/meetings",
     "comment_process": "Public hearings held per Wisconsin open-meetings "
                        "rules. Contact the County Clerk for details.",
     "phone": "", "email": "",
     "website": "https://www.co.dodge.wi.gov/government/county-board",
     "as_of": "2026-08-12",
     "source": "https://www.co.dodge.wi.gov/government/county-board"},

    {"locality": "Harris County", "state": "GA",
     "body": "Board of Commissioners",
     "decides": "Land use and zoning (5 districts). Resident petition "
                "with ~150 signatures requested a 1-year moratorium on "
                "hyperscale data center approvals (Aug 5, 2026); "
                "commissioners took no action. County is updating its "
                "comprehensive land use plan.",
     "meets": "1st and 3rd Tuesday of the month, 6:30 p.m.",
     "where": "Courthouse, 102 N. College St., Hamilton, GA 31811",
     "agenda_url": "https://www.harriscountyga.gov/minutes_agendas_fy22-23/",
     "comment_process": "Residents may speak at commission meetings. "
                        "See the board's published agenda for details.",
     "phone": "706-628-4958", "email": "",
     "website": "https://www.harriscountyga.gov/board-of-commissioners/",
     "as_of": "2026-08-12",
     "source": "https://www.harriscountyga.gov/board-of-commissioners/"},

    {"locality": "Gilroy", "state": "CA",
     "body": "City Council",
     "decides": "Zoning and land use (7 members, charter city). Amazon "
                "is building a ~49 MW data center on 56 acres under a "
                "1981 industrial zoning — approved at staff level with "
                "no council vote or Planning Commission review. The "
                "45-day CEQA comment window (Aug-Sep 2024) closed before "
                "most residents learned of the project.",
     "meets": "1st and 3rd Monday of the month, 6:00 p.m.",
     "where": "City Council Chambers, 7351 Rosanna Street, Gilroy, CA 95020",
     "agenda_url": "https://cityofgilroy.org/965/Agendas-Minutes",
     "comment_process": "In-person: up to 3 min (scaled to 2 or 1 min "
                        "for 11+ or 20+ speakers). Zoom participation "
                        "available. Written comments to "
                        "publiccomments@cityofgilroy.org by 1:00 p.m. "
                        "on the meeting date.",
     "phone": "408-846-0204",
     "email": "publiccomments@cityofgilroy.org",
     "website": "https://www.cityofgilroy.org/341/City-Council",
     "as_of": "2026-08-12",
     "source": "https://www.cityofgilroy.org/341/City-Council"},
]
LOCAL_BODIES_DF = pd.DataFrame(LOCAL_BODIES)

# ── Tier 1: named officials ─────────────────────────────────────────────────
# `stance` is blank unless a documented, citable position exists — matching the
# convention used for the Congress/governor directory. Blank means "not
# recorded", never "neutral".
LOCAL_OFFICIALS = [
    # Tucker County, WV — https://tuckercountycommission.com/county-commission
    {"locality": "Tucker County", "state": "WV", "body": "Tucker County Commission",
     "name": "Michael Rosenau", "role": "Commission President", "district": "",
     "email": "mrosenau@tuckercountycommission.com", "phone": "304-614-4006",
     "stance": "", "as_of": "2026-07-26",
     "source": "https://tuckercountycommission.com/county-commission"},
    {"locality": "Tucker County", "state": "WV", "body": "Tucker County Commission",
     "name": "Fred Davis", "role": "Commissioner", "district": "",
     "email": "fdavis@tuckercountycommission.com", "phone": "304-614-3227",
     "stance": "", "as_of": "2026-07-26",
     "source": "https://tuckercountycommission.com/county-commission"},
    {"locality": "Tucker County", "state": "WV", "body": "Tucker County Commission",
     "name": "Tim Knotts", "role": "Commissioner", "district": "",
     "email": "tknotts@tuckercountycommission.com", "phone": "301-616-8073",
     "stance": "", "as_of": "2026-07-26",
     "source": "https://tuckercountycommission.com/county-commission"},
    {"locality": "Tucker County", "state": "WV", "body": "Tucker County Commission",
     "name": "Shelia DeVilder", "role": "County Administrator (staff, not elected)",
     "district": "", "email": "sdevilder@tuckercountycommission.com",
     "phone": "304-478-2866 ext. 1207", "stance": "", "as_of": "2026-07-26",
     "source": "https://tuckercountycommission.com/county-commission"},

    # Port Washington, WI — https://www.portwashingtonwi.gov/our-city/mayor-common-council
    {"locality": "Port Washington", "state": "WI", "body": "Common Council",
     "name": "Ted Neitzke IV", "role": "Mayor", "district": "",
     "email": "tneitzke@portwashingtonwi.gov", "phone": "262-284-5585",
     "stance": "", "as_of": "2026-07-26",
     "source": "https://www.portwashingtonwi.gov/our-city/mayor-common-council"},
    {"locality": "Port Washington", "state": "WI", "body": "Common Council",
     "name": "Deborah Postl", "role": "Alderperson", "district": "Wards 1 & 9",
     "email": "dpostl@portwashingtonwi.gov", "phone": "262-284-5585",
     "stance": "", "as_of": "2026-07-26",
     "source": "https://www.portwashingtonwi.gov/our-city/mayor-common-council"},
    {"locality": "Port Washington", "state": "WI", "body": "Common Council",
     "name": "Paul Neumyer", "role": "Alderperson", "district": "Ward 2",
     "email": "pneumyer@portwashingtonwi.gov", "phone": "262-284-5585",
     "stance": "", "as_of": "2026-07-26",
     "source": "https://www.portwashingtonwi.gov/our-city/mayor-common-council"},
    {"locality": "Port Washington", "state": "WI", "body": "Common Council",
     "name": "Michael Gasper", "role": "Alderperson", "district": "Ward 3",
     "email": "mgasper@portwashingtonwi.gov", "phone": "262-284-5585",
     "stance": "", "as_of": "2026-07-26",
     "source": "https://www.portwashingtonwi.gov/our-city/mayor-common-council"},
    {"locality": "Port Washington", "state": "WI", "body": "Common Council",
     "name": "Dan Benning", "role": "Alderperson", "district": "Wards 4 & 8",
     "email": "dbenning@portwashingtonwi.gov", "phone": "262-284-5585",
     "stance": "", "as_of": "2026-07-26",
     "source": "https://www.portwashingtonwi.gov/our-city/mayor-common-council"},
    {"locality": "Port Washington", "state": "WI", "body": "Common Council",
     "name": "Jonathan Pleitner", "role": "Alderperson", "district": "Ward 5",
     "email": "jpleitner@portwashingtonwi.gov", "phone": "262-284-5585",
     "stance": "", "as_of": "2026-07-26",
     "source": "https://www.portwashingtonwi.gov/our-city/mayor-common-council"},
    {"locality": "Port Washington", "state": "WI", "body": "Common Council",
     "name": "Michael Beaster", "role": "Alderperson", "district": "Ward 6",
     "email": "mbeaster@portwashingtonwi.gov", "phone": "262-284-5585",
     "stance": "", "as_of": "2026-07-26",
     "source": "https://www.portwashingtonwi.gov/our-city/mayor-common-council"},
    {"locality": "Port Washington", "state": "WI", "body": "Common Council",
     "name": "Mary Lou Mueller", "role": "Alderperson", "district": "Ward 7",
     "email": "mmueller@portwashingtonwi.gov", "phone": "262-284-5585",
     "stance": "", "as_of": "2026-07-26",
     "source": "https://www.portwashingtonwi.gov/our-city/mayor-common-council"},

    # Goochland County, VA — https://www.goochlandva.us/158/Board-of-Supervisors
    {"locality": "Goochland County", "state": "VA", "body": "Board of Supervisors",
     "name": "Jonathan Christy", "role": "Chair", "district": "District 1",
     "email": "jchristy@goochlandva.us", "phone": "804-837-7056",
     "stance": "", "as_of": "2026-07-26",
     "source": "https://www.goochlandva.us/158/Board-of-Supervisors"},
    {"locality": "Goochland County", "state": "VA", "body": "Board of Supervisors",
     "name": "Neil Spoonhower", "role": "Vice-Chair", "district": "District 2",
     "email": "nspoonhower@goochlandva.us", "phone": "804-316-5584",
     "stance": "", "as_of": "2026-07-26",
     "source": "https://www.goochlandva.us/158/Board-of-Supervisors"},
    {"locality": "Goochland County", "state": "VA", "body": "Board of Supervisors",
     "name": "Tom Winfree", "role": "Supervisor", "district": "District 3",
     "email": "twinfree@goochlandva.us", "phone": "804-659-4607",
     "stance": "", "as_of": "2026-07-26",
     "source": "https://www.goochlandva.us/158/Board-of-Supervisors"},
    {"locality": "Goochland County", "state": "VA", "body": "Board of Supervisors",
     "name": "Charlie Vaughters", "role": "Supervisor", "district": "District 4",
     "email": "cvaughters@goochlandva.us", "phone": "804-508-8763",
     "stance": "", "as_of": "2026-07-26",
     "source": "https://www.goochlandva.us/158/Board-of-Supervisors"},
    {"locality": "Goochland County", "state": "VA", "body": "Board of Supervisors",
     "name": "Jonathan Lyle", "role": "Supervisor", "district": "District 5",
     "email": "jlyle@goochlandva.us", "phone": "804-584-7524",
     "stance": "", "as_of": "2026-07-26",
     "source": "https://www.goochlandva.us/158/Board-of-Supervisors"},

    # Prince William County, VA — https://www.pwcva.gov/department/board-county-supervisors/contact-us
    {"locality": "Prince William County", "state": "VA",
     "body": "Board of County Supervisors", "name": "Deshundra Jefferson",
     "role": "Chair", "district": "At-Large", "email": "chair@pwcgov.org",
     "phone": "703-792-4640", "stance": "", "as_of": "2026-07-26",
     "source": "https://www.pwcva.gov/department/board-county-supervisors/contact-us"},
    {"locality": "Prince William County", "state": "VA",
     "body": "Board of County Supervisors", "name": "Tom Gordy",
     "role": "Supervisor", "district": "Brentsville", "email": "tgordy@pwcgov.org",
     "phone": "703-792-6190", "stance": "", "as_of": "2026-07-26",
     "source": "https://www.pwcva.gov/department/board-county-supervisors/contact-us"},
    {"locality": "Prince William County", "state": "VA",
     "body": "Board of County Supervisors", "name": "Yesli Vega",
     "role": "Supervisor", "district": "Coles", "email": "yvega@pwcgov.org",
     "phone": "703-792-4620", "stance": "", "as_of": "2026-07-26",
     "source": "https://www.pwcva.gov/department/board-county-supervisors/contact-us"},
    {"locality": "Prince William County", "state": "VA",
     "body": "Board of County Supervisors", "name": "George Stewart",
     "role": "Supervisor", "district": "Gainesville", "email": "gstewart@pwcgov.org",
     "phone": "703-792-6195", "stance": "", "as_of": "2026-07-26",
     "source": "https://www.pwcva.gov/department/board-county-supervisors/contact-us"},
    {"locality": "Prince William County", "state": "VA",
     "body": "Board of County Supervisors", "name": "Victor S. Angry",
     "role": "Supervisor", "district": "Neabsco", "email": "vsangry@pwcgov.org",
     "phone": "703-792-4668", "stance": "", "as_of": "2026-07-26",
     "source": "https://www.pwcva.gov/department/board-county-supervisors/contact-us"},
    {"locality": "Prince William County", "state": "VA",
     "body": "Board of County Supervisors", "name": "Kenny Boddye",
     "role": "Supervisor", "district": "Occoquan", "email": "kboddye@pwcgov.org",
     "phone": "703-792-4643", "stance": "", "as_of": "2026-07-26",
     "source": "https://www.pwcva.gov/department/board-county-supervisors/contact-us"},
    {"locality": "Prince William County", "state": "VA",
     "body": "Board of County Supervisors", "name": "Andrea Bailey",
     "role": "Supervisor", "district": "Potomac", "email": "abailey@pwcgov.org",
     "phone": "703-792-4563", "stance": "", "as_of": "2026-07-26",
     "source": "https://www.pwcva.gov/department/board-county-supervisors/contact-us"},
    {"locality": "Prince William County", "state": "VA",
     "body": "Board of County Supervisors", "name": "Jeannie LaCroix",
     "role": "Supervisor", "district": "Woodbridge", "email": "JLaCroix@pwcgov.org",
     "phone": "", "stance": "", "as_of": "2026-07-26",
     "source": "https://www.pwcva.gov/department/board-county-supervisors/contact-us"},

    # San Marcos, TX — https://www.sanmarcostx.gov/149/City-Council
    # Mayor + 6 at-large "Place" seats; the city publishes a shared council
    # address (councilmembers@sanmarcostx.gov), not per-member emails.
    {"locality": "San Marcos", "state": "TX", "body": "City Council",
     "name": "Jane Hughson", "role": "Mayor", "district": "At-large",
     "email": "", "phone": "", "stance": "", "as_of": "2026-08-05",
     "source": "https://www.sanmarcostx.gov/149/City-Council"},
    {"locality": "San Marcos", "state": "TX", "body": "City Council",
     "name": "Matthew Mendoza", "role": "Council Member", "district": "Place 1",
     "email": "", "phone": "", "stance": "", "as_of": "2026-08-05",
     "source": "https://www.sanmarcostx.gov/149/City-Council"},
    {"locality": "San Marcos", "state": "TX", "body": "City Council",
     "name": "Josh Paselk", "role": "Council Member", "district": "Place 2",
     "email": "", "phone": "", "stance": "", "as_of": "2026-08-05",
     "source": "https://www.sanmarcostx.gov/149/City-Council"},
    {"locality": "San Marcos", "state": "TX", "body": "City Council",
     "name": "Alyssa Garza", "role": "Council Member", "district": "Place 3",
     "email": "", "phone": "", "stance": "", "as_of": "2026-08-05",
     "source": "https://www.sanmarcostx.gov/149/City-Council"},
    {"locality": "San Marcos", "state": "TX", "body": "City Council",
     "name": "Shane Scott", "role": "Council Member", "district": "Place 4",
     "email": "", "phone": "", "stance": "", "as_of": "2026-08-05",
     "source": "https://www.sanmarcostx.gov/149/City-Council"},
    {"locality": "San Marcos", "state": "TX", "body": "City Council",
     "name": "Lorenzo Gonzalez", "role": "Council Member", "district": "Place 5",
     "email": "", "phone": "", "stance": "", "as_of": "2026-08-05",
     "source": "https://www.sanmarcostx.gov/149/City-Council"},
    {"locality": "San Marcos", "state": "TX", "body": "City Council",
     "name": "Amanda Rodriguez", "role": "Council Member", "district": "Place 6",
     "email": "", "phone": "", "stance": "", "as_of": "2026-08-05",
     "source": "https://www.sanmarcostx.gov/149/City-Council"},

    # Chesterfield County, VA — https://www.chesterfield.gov/1218/Board-of-Supervisors
    # Five magisterial districts; only the general board line is published.
    {"locality": "Chesterfield County", "state": "VA", "body": "Board of Supervisors",
     "name": "Mark S. Miller", "role": "Chair", "district": "Midlothian",
     "email": "", "phone": "804-748-1200", "stance": "", "as_of": "2026-08-05",
     "source": "https://www.chesterfield.gov/1218/Board-of-Supervisors"},
    {"locality": "Chesterfield County", "state": "VA", "body": "Board of Supervisors",
     "name": "Kevin Carroll", "role": "Vice Chair", "district": "Matoaca",
     "email": "", "phone": "804-748-1200", "stance": "", "as_of": "2026-08-05",
     "source": "https://www.chesterfield.gov/1218/Board-of-Supervisors"},
    {"locality": "Chesterfield County", "state": "VA", "body": "Board of Supervisors",
     "name": "Jim Ingle", "role": "Supervisor", "district": "Bermuda",
     "email": "", "phone": "804-748-1200", "stance": "", "as_of": "2026-08-05",
     "source": "https://www.chesterfield.gov/1218/Board-of-Supervisors"},
    {"locality": "Chesterfield County", "state": "VA", "body": "Board of Supervisors",
     "name": "Jessica Schneider", "role": "Supervisor", "district": "Clover Hill",
     "email": "", "phone": "804-748-1200", "stance": "", "as_of": "2026-08-05",
     "source": "https://www.chesterfield.gov/1218/Board-of-Supervisors"},
    {"locality": "Chesterfield County", "state": "VA", "body": "Board of Supervisors",
     "name": "LeQuan M. Hylton", "role": "Supervisor", "district": "Dale",
     "email": "", "phone": "804-748-1200", "stance": "", "as_of": "2026-08-05",
     "source": "https://www.chesterfield.gov/1218/Board-of-Supervisors"},

    # Manatee County, FL — https://www.mymanatee.org/government/government-information/board-of-county-commissioners
    # Five districts + two at-large; District 1 vacant as of Aug 2026.
    {"locality": "Manatee County", "state": "FL", "body": "Board of County Commissioners",
     "name": "Amanda Ballard", "role": "Commissioner", "district": "District 2",
     "email": "", "phone": "941-745-3702", "stance": "", "as_of": "2026-08-05",
     "source": "https://www.mymanatee.org/government/government-information/board-of-county-commissioners"},
    {"locality": "Manatee County", "state": "FL", "body": "Board of County Commissioners",
     "name": "Tal Siddique", "role": "Chair", "district": "District 3",
     "email": "", "phone": "", "stance": "", "as_of": "2026-08-05",
     "source": "https://www.mymanatee.org/government/government-information/board-of-county-commissioners"},
    {"locality": "Manatee County", "state": "FL", "body": "Board of County Commissioners",
     "name": "Mike Rahn", "role": "Commissioner", "district": "District 4",
     "email": "", "phone": "941-745-3713", "stance": "", "as_of": "2026-08-05",
     "source": "https://www.mymanatee.org/government/government-information/board-of-county-commissioners"},
    {"locality": "Manatee County", "state": "FL", "body": "Board of County Commissioners",
     "name": "Dr. Bob McCann", "role": "Commissioner", "district": "District 5",
     "email": "", "phone": "941-398-6758", "stance": "", "as_of": "2026-08-05",
     "source": "https://www.mymanatee.org/government/government-information/board-of-county-commissioners"},
    {"locality": "Manatee County", "state": "FL", "body": "Board of County Commissioners",
     "name": "George Kruse", "role": "Commissioner", "district": "At-large",
     "email": "", "phone": "941-745-3714", "stance": "", "as_of": "2026-08-05",
     "source": "https://www.mymanatee.org/government/government-information/board-of-county-commissioners"},
    {"locality": "Manatee County", "state": "FL", "body": "Board of County Commissioners",
     "name": "Jason Bearden", "role": "Commissioner", "district": "At-large",
     "email": "", "phone": "941-705-8709", "stance": "", "as_of": "2026-08-05",
     "source": "https://www.mymanatee.org/government/government-information/board-of-county-commissioners"},

    # Flagler County, FL — https://www.flaglercounty.gov/Government/Board-of-County-Commissioners
    {"locality": "Flagler County", "state": "FL", "body": "Board of County Commissioners",
     "name": "Leann Pennington", "role": "Chair", "district": "District 4",
     "email": "", "phone": "386-313-4001", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.flaglercounty.gov/Government/Board-of-County-Commissioners"},
    {"locality": "Flagler County", "state": "FL", "body": "Board of County Commissioners",
     "name": "Kim Carney", "role": "Vice Chair", "district": "District 3",
     "email": "", "phone": "386-313-4001", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.flaglercounty.gov/Government/Board-of-County-Commissioners"},
    {"locality": "Flagler County", "state": "FL", "body": "Board of County Commissioners",
     "name": "Andy Dance", "role": "Commissioner", "district": "District 1",
     "email": "", "phone": "386-313-4001", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.flaglercounty.gov/Government/Board-of-County-Commissioners"},
    {"locality": "Flagler County", "state": "FL", "body": "Board of County Commissioners",
     "name": "Gregory Hansen", "role": "Commissioner", "district": "District 2",
     "email": "", "phone": "386-313-4001", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.flaglercounty.gov/Government/Board-of-County-Commissioners"},
    {"locality": "Flagler County", "state": "FL", "body": "Board of County Commissioners",
     "name": "Pam Richardson", "role": "Commissioner", "district": "District 5",
     "email": "", "phone": "386-313-4001", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.flaglercounty.gov/Government/Board-of-County-Commissioners"},

    # Hays County, TX — https://www.hayscountytx.gov/188/Commissioners-Court-Members
    {"locality": "Hays County", "state": "TX", "body": "Commissioners Court",
     "name": "Ruben Becerra", "role": "County Judge (presides)", "district": "At-large",
     "email": "", "phone": "512-393-7779", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.hayscountytx.gov/188/Commissioners-Court-Members"},
    {"locality": "Hays County", "state": "TX", "body": "Commissioners Court",
     "name": "Debbie Ingalsbe", "role": "Commissioner", "district": "Precinct 1",
     "email": "", "phone": "512-393-2243", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.hayscountytx.gov/188/Commissioners-Court-Members"},
    {"locality": "Hays County", "state": "TX", "body": "Commissioners Court",
     "name": "Michelle Cohen", "role": "Commissioner", "district": "Precinct 2",
     "email": "", "phone": "", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.hayscountytx.gov/188/Commissioners-Court-Members"},
    {"locality": "Hays County", "state": "TX", "body": "Commissioners Court",
     "name": "Morgan Hammer", "role": "Commissioner", "district": "Precinct 3",
     "email": "", "phone": "", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.hayscountytx.gov/188/Commissioners-Court-Members"},
    {"locality": "Hays County", "state": "TX", "body": "Commissioners Court",
     "name": "Walt Smith", "role": "Commissioner", "district": "Precinct 4",
     "email": "", "phone": "512-858-7268", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.hayscountytx.gov/188/Commissioners-Court-Members"},

    # Broomfield, CO — https://www.broomfield.org/954/Council-Members
    {"locality": "Broomfield", "state": "CO", "body": "City Council",
     "name": "Guyleen Castriotta", "role": "Mayor", "district": "At-large",
     "email": "", "phone": "303-438-6300", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.broomfield.org/954/Council-Members"},
    {"locality": "Broomfield", "state": "CO", "body": "City Council",
     "name": "Jean Lim", "role": "Mayor Pro Tem", "district": "Ward 3",
     "email": "", "phone": "303-438-6300", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.broomfield.org/954/Council-Members"},
    {"locality": "Broomfield", "state": "CO", "body": "City Council",
     "name": "Sarah Braun", "role": "Council Member", "district": "Ward 3",
     "email": "", "phone": "303-438-6300", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.broomfield.org/954/Council-Members"},
    {"locality": "Broomfield", "state": "CO", "body": "City Council",
     "name": "Julie Twiss", "role": "Council Member", "district": "Ward 1",
     "email": "", "phone": "303-438-6300", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.broomfield.org/954/Council-Members"},
    {"locality": "Broomfield", "state": "CO", "body": "City Council",
     "name": "Katie Peterson", "role": "Council Member", "district": "Ward 1",
     "email": "", "phone": "303-438-6300", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.broomfield.org/954/Council-Members"},
    {"locality": "Broomfield", "state": "CO", "body": "City Council",
     "name": "Paloma Delgadillo", "role": "Council Member", "district": "Ward 2",
     "email": "", "phone": "303-438-6300", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.broomfield.org/954/Council-Members"},
    {"locality": "Broomfield", "state": "CO", "body": "City Council",
     "name": "Austin Ward", "role": "Council Member", "district": "Ward 2",
     "email": "", "phone": "303-438-6300", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.broomfield.org/954/Council-Members"},
    {"locality": "Broomfield", "state": "CO", "body": "City Council",
     "name": "Laurie Anderson", "role": "Council Member", "district": "Ward 4",
     "email": "", "phone": "303-438-6300", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.broomfield.org/954/Council-Members"},
    {"locality": "Broomfield", "state": "CO", "body": "City Council",
     "name": "Sean McKenzie", "role": "Council Member", "district": "Ward 4",
     "email": "", "phone": "303-438-6300", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.broomfield.org/954/Council-Members"},
    {"locality": "Broomfield", "state": "CO", "body": "City Council",
     "name": "Heidi Henkel", "role": "Council Member", "district": "Ward 5",
     "email": "", "phone": "303-438-6300", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.broomfield.org/954/Council-Members"},
    {"locality": "Broomfield", "state": "CO", "body": "City Council",
     "name": "Todd Cohen", "role": "Council Member", "district": "Ward 5",
     "email": "", "phone": "303-438-6300", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.broomfield.org/954/Council-Members"},

    # Lakeland, FL — https://www.lakelandgov.net/government/mayor-city-commission/
    # Shared address citycommission@lakelandgov.net reaches all members.
    {"locality": "Lakeland", "state": "FL", "body": "City Commission",
     "name": "Sara Roberts McCarley", "role": "Mayor", "district": "At-large",
     "email": "", "phone": "863-834-6005", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.lakelandgov.net/government/mayor-city-commission/"},
    {"locality": "Lakeland", "state": "FL", "body": "City Commission",
     "name": "Stephanie Madden", "role": "Commissioner", "district": "At-large",
     "email": "", "phone": "863-834-6005", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.lakelandgov.net/government/mayor-city-commission/"},
    {"locality": "Lakeland", "state": "FL", "body": "City Commission",
     "name": "Chad McLeod", "role": "Commissioner", "district": "At-large",
     "email": "", "phone": "863-834-6005", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.lakelandgov.net/government/mayor-city-commission/"},
    {"locality": "Lakeland", "state": "FL", "body": "City Commission",
     "name": "Ashley C. Troutman", "role": "Commissioner", "district": "Southwest",
     "email": "", "phone": "863-834-6005", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.lakelandgov.net/government/mayor-city-commission/"},
    {"locality": "Lakeland", "state": "FL", "body": "City Commission",
     "name": "Mike Musick", "role": "Commissioner", "district": "Southeast",
     "email": "", "phone": "863-834-6005", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.lakelandgov.net/government/mayor-city-commission/"},
    {"locality": "Lakeland", "state": "FL", "body": "City Commission",
     "name": "Terry G. Coney", "role": "Commissioner", "district": "Northeast",
     "email": "", "phone": "863-834-6005", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.lakelandgov.net/government/mayor-city-commission/"},
    {"locality": "Lakeland", "state": "FL", "body": "City Commission",
     "name": "Guy LaLonde Jr.", "role": "Commissioner", "district": "Northwest",
     "email": "", "phone": "863-834-6005", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.lakelandgov.net/government/mayor-city-commission/"},

    # Desert Hot Springs, CA — https://www.cityofdhs.org/departments/city-council/
    {"locality": "Desert Hot Springs", "state": "CA", "body": "City Council",
     "name": "Scott Matas", "role": "Mayor", "district": "At-large",
     "email": "", "phone": "760-329-6411", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.cityofdhs.org/departments/city-council/"},
    {"locality": "Desert Hot Springs", "state": "CA", "body": "City Council",
     "name": "Dirk Voss", "role": "Mayor Pro Tem", "district": "District 4",
     "email": "", "phone": "760-329-6411", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.cityofdhs.org/departments/city-council/"},
    {"locality": "Desert Hot Springs", "state": "CA", "body": "City Council",
     "name": "Gary Gardner", "role": "Council Member", "district": "District 1",
     "email": "", "phone": "760-329-6411", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.cityofdhs.org/departments/city-council/"},
    {"locality": "Desert Hot Springs", "state": "CA", "body": "City Council",
     "name": "Daniel Pitts", "role": "Council Member", "district": "District 2",
     "email": "", "phone": "760-329-6411", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.cityofdhs.org/departments/city-council/"},
    {"locality": "Desert Hot Springs", "state": "CA", "body": "City Council",
     "name": "Jan Pye", "role": "Council Member", "district": "District 3",
     "email": "", "phone": "760-329-6411", "stance": "", "as_of": "2026-08-07",
     "source": "https://www.cityofdhs.org/departments/city-council/"},
]
LOCAL_OFFICIALS_DF = pd.DataFrame(LOCAL_OFFICIALS)
