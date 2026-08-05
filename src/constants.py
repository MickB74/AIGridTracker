import datetime as _dt
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
     "status": "Enacted", "when": "2026", "note": "",
     "lat": 42.47, "lon": -90.88, "expires": None, "as_of": None, "source": None},
    {"locality": "Bloomington", "state": "IL", "level": "Local",
     "status": "Enacted", "when": "2026", "note": "",
     "lat": 40.48, "lon": -88.99, "expires": None, "as_of": None, "source": None},
    {"locality": "Normal", "state": "IL", "level": "Local",
     "status": "Enacted", "when": "2026", "note": "",
     "lat": 40.51, "lon": -88.99, "expires": None, "as_of": None, "source": None},
    {"locality": "Iron County", "state": "UT", "level": "Local",
     "status": "Enacted", "when": "2026", "note": "",
     "lat": 37.68, "lon": -113.06, "expires": None, "as_of": None, "source": None},
    {"locality": "Manitowoc County", "state": "WI", "level": "Local",
     "status": "Enacted", "when": "2026", "note": "18-month; start date not documented",
     "lat": 44.09, "lon": -87.66, "expires": None, "as_of": None, "source": None},
    {"locality": "Smithfield", "state": "RI", "level": "Local",
     "status": "Enacted", "when": "Jun 4, 2026",
     "note": "Adopted 4-1 May 5, effective Jun 4; data centers not permitted in any zoning district",
     "lat": 41.92, "lon": -71.55, "expires": None, "as_of": "2026-08-04",
     "source": "https://www.wpri.com/news/local-news/northwest/smithfield-town-council-approves-ordinance-to-prevent-construction-of-data-centers/"},
    {"locality": "Meridian Township", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "2026", "note": "",
     "lat": 42.72, "lon": -84.42, "expires": None, "as_of": None, "source": None},
    {"locality": "Washington Township (Macomb Co.)", "state": "MI", "level": "Local",
     "status": "Enacted", "when": "2026", "note": "",
     "lat": 42.72, "lon": -82.92, "expires": None, "as_of": None, "source": None},
    {"locality": "Hill County", "state": "TX", "level": "Local",
     "status": "Rescinded", "when": "Rescinded Jun 4, 2026",
     "note": "1-year moratorium passed May 2026, rescinded after a $100M federal suit "
             "argued Texas counties lack moratorium authority; suit dismissed Jul 2026. "
             "Replaced with a disclosure checklist for large projects",
     "lat": 32.01, "lon": -97.13, "expires": None, "as_of": "2026-08-04",
     "source": "https://www.texastribune.org/2026/06/05/texas-hill-county-moratorium-rescinded-data-centers/"},
    {"locality": "DeKalb County", "state": "GA", "level": "Local",
     "status": "Enacted", "when": "2026", "note": "",
     "lat": 33.77, "lon": -84.23, "expires": None, "as_of": None, "source": None},
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
    {"locality": "Groton", "state": "CT", "level": "Local",
     "status": "Enacted", "when": "Jun 21, 2022",
     "note": "1-year moratorium on data centers over 5,000 sq ft; lapsed into permanent "
             "zoning in Jun 2023 capping buildings at 12,500 sq ft and barring water cooling",
     "lat": 41.35, "lon": -72.08, "expires": "2023-06-21", "as_of": "2026-08-04",
     "source": "https://theday.com/local-news/20220621/groton-approves-one-year-moratorium-on-large-scale-data-centers"},
    {"locality": "Peculiar", "state": "MO", "level": "Local",
     "status": "Enacted", "when": "2025",
     "note": "Board of Aldermen removed 'data center' from the light-industrial zoning "
             "code, blocking a $1.5B project; exact date unconfirmed",
     "lat": 38.72, "lon": -94.46, "expires": None, "as_of": None, "source": None},
    {"locality": "Bangor", "state": "ME", "level": "Local",
     "status": "Enacted", "when": "2025", "note": "Temporary ban; term not documented",
     "lat": 44.80, "lon": -68.77, "expires": None, "as_of": None, "source": None},
    # North Carolina — 20+ jurisdictions since late 2025. Compiled in bulk and
    # not yet verified row-by-row against each locality's own ordinance.
    {"locality": "Gates County", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Dec 2025", "note": "",
     "lat": 36.44, "lon": -76.70, "expires": None, "as_of": None, "source": None},
    {"locality": "Brevard", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Sep 2025", "note": "",
     "lat": 35.23, "lon": -82.73, "expires": None, "as_of": None, "source": None},
    {"locality": "Clay County", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Sep 2025", "note": "",
     "lat": 35.06, "lon": -83.75, "expires": None, "as_of": None, "source": None},
    {"locality": "Canton", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Feb 2026", "note": "",
     "lat": 35.53, "lon": -82.84, "expires": None, "as_of": None, "source": None},
    {"locality": "Chatham County", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Feb 2026", "note": "",
     "lat": 35.70, "lon": -79.26, "expires": None, "as_of": None, "source": None},
    {"locality": "Kings Mountain", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Feb 2026", "note": "",
     "lat": 35.25, "lon": -81.34, "expires": None, "as_of": None, "source": None},
    {"locality": "Boone", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Mar 2026", "note": "",
     "lat": 36.22, "lon": -81.67, "expires": None, "as_of": None, "source": None},
    {"locality": "Apex", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Apr 2026", "note": "",
     "lat": 35.73, "lon": -78.85, "expires": None, "as_of": None, "source": None},
    {"locality": "Orange County", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Apr 2026", "note": "",
     "lat": 36.06, "lon": -79.12, "expires": None, "as_of": None, "source": None},
    {"locality": "Rowan County", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Apr 2026", "note": "",
     "lat": 35.64, "lon": -80.47, "expires": None, "as_of": None, "source": None},
    {"locality": "Swain County", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "Apr 2026", "note": "",
     "lat": 35.49, "lon": -83.49, "expires": None, "as_of": None, "source": None},
    {"locality": "Watauga County", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "2026", "note": "Ban",
     "lat": 36.23, "lon": -81.69, "expires": None, "as_of": None, "source": None},
    {"locality": "Madison County", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "2026", "note": "Ban",
     "lat": 35.85, "lon": -82.70, "expires": None, "as_of": None, "source": None},
    {"locality": "Clyde", "state": "NC", "level": "Local",
     "status": "Enacted", "when": "2026", "note": "Ban",
     "lat": 35.53, "lon": -82.91, "expires": None, "as_of": None, "source": None},
    # Proposed / under consideration
    {"locality": "Charlotte", "state": "NC", "level": "Local",
     "status": "Proposed", "when": "2026", "note": "Council deadlocked 5–5",
     "lat": 35.23, "lon": -80.84, "expires": None, "as_of": None, "source": None},
    {"locality": "Durham", "state": "NC", "level": "Local",
     "status": "Proposed", "when": "2026", "note": "",
     "lat": 35.99, "lon": -78.90, "expires": None, "as_of": None, "source": None},
    {"locality": "Harnett County", "state": "NC", "level": "Local",
     "status": "Proposed", "when": "2026", "note": "",
     "lat": 35.37, "lon": -78.87, "expires": None, "as_of": None, "source": None},
    {"locality": "Cumberland County", "state": "NC", "level": "Local",
     "status": "Proposed", "when": "2026", "note": "",
     "lat": 35.05, "lon": -78.83, "expires": None, "as_of": None, "source": None},
    {"locality": "Fayetteville", "state": "NC", "level": "Local",
     "status": "Proposed", "when": "2026", "note": "",
     "lat": 35.05, "lon": -78.88, "expires": None, "as_of": None, "source": None},
    {"locality": "Seattle", "state": "WA", "level": "Local",
     "status": "Enacted", "when": "Jun 9, 2026",
     "note": "Emergency ordinance passed 9-0; 1 year, facilities over 20 MVA, "
             "extendable about six months",
     "lat": 47.61, "lon": -122.33, "expires": "2027-06-09", "as_of": "2026-08-04",
     "source": "https://council.seattle.gov/2026/06/09/city-council-passes-emergency-data-center-moratorium-and-policy-framework/"},
    {"locality": "Indianapolis", "state": "IN", "level": "Local",
     "status": "Proposed", "when": "Jun 2026", "note": "Non-binding pause",
     "lat": 39.77, "lon": -86.16, "expires": None, "as_of": None, "source": None},
    {"locality": "Pulaski County", "state": "AR", "level": "Local",
     "status": "Proposed", "when": "2026", "note": "",
     "lat": 34.75, "lon": -92.29, "expires": None, "as_of": None, "source": None},
    {"locality": "St. Lawrence County", "state": "NY", "level": "Local",
     "status": "Proposed", "when": "2026", "note": "Urged municipalities",
     "lat": 44.59, "lon": -75.16, "expires": None, "as_of": None, "source": None},
    # Rejected
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
     "status": "Rejected", "when": "2026", "note": "Failed signature threshold",
     "lat": None, "lon": None, "expires": None, "as_of": None, "source": None},
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

# Negotiation intel per operator — documented concessions won elsewhere plus
# a read on how the company negotiates. Keyed by OPERATORS_DF operator name;
# operators without a well-documented track record are simply absent (the
# brief/action pack skips the section). Feeds build_meeting_brief_data().
COMPANY_CONCESSIONS = {
    "Google": {
        "pattern": (
            "Negotiates through PR-friendly commitments — water stewardship "
            "pledges, community grants — but its largest concessions came only "
            "under permit leverage and records-transparency pressure. Secrecy "
            "is standard practice (NDAs with local officials, shell LLCs like "
            "'Design LLC') until approvals are locked; forcing early "
            "disclosure of water and power demands shifts the balance."
        ),
        "concessions": [
            {"where": "The Dalles, OR", "year": "2021-22",
             "what": "Funded a ~$29M water/wastewater infrastructure upgrade "
                     "and committed to recycled-water cooling after the city "
                     "tied expansion approval to water guarantees; dropped its "
                     "fight to keep water-use records secret after a local "
                     "newspaper's public-records lawsuit."},
            {"where": "Mesa, AZ", "year": "2023",
             "what": "Accepted voluntary noise retrofits and quarterly "
                     "community reporting under the city's data-center "
                     "overlay zone."},
            {"where": "Multiple campuses", "year": "ongoing",
             "what": "Routinely funds local community grants near campuses — "
                     "treat these as table stakes, not a substitute for a "
                     "binding CBA."},
        ],
    },
    "Meta": {
        "pattern": (
            "Runs a standardized siting playbook behind shell LLCs (in Los "
            "Lunas it arrived as 'Greater Kudu LLC') and moves fast once "
            "incentives are locked. Its public 'water positive by 2030' "
            "pledge is leverage: communities have converted it into binding "
            "local water caps, restoration funding, and reporting terms."
        ),
        "concessions": [
            {"where": "Los Lunas, NM", "year": "2016-22",
             "what": "Agreed to water-use limits and funded Rio Grande basin "
                     "water-restoration projects after drought-driven "
                     "scrutiny of the campus's cooling demand."},
            {"where": "Multiple campuses", "year": "ongoing",
             "what": "Funds community action grants and local infrastructure "
                     "near campuses; amounts are negotiated site by site — "
                     "get them written into approval conditions."},
        ],
    },
    "Microsoft": {
        "pattern": (
            "The most willing of the hyperscalers to accept transparency and "
            "design conditions: it has publicly committed new builds to "
            "zero-water evaporative cooling designs and has paid for its own "
            "water treatment where municipal systems pushed back. Use its "
            "published sustainability commitments as the floor of your ask, "
            "not the ceiling."
        ),
        "concessions": [
            {"where": "Quincy, WA", "year": "2010s",
             "what": "Funded and built water treatment/reuse capacity after "
                     "the city objected to cooling discharge loads on the "
                     "municipal system."},
            {"where": "San Antonio, TX", "year": "ongoing",
             "what": "Runs cooling on recycled municipal wastewater instead "
                     "of potable supply."},
            {"where": "New builds (announced)", "year": "2024",
             "what": "Committed next-generation data center designs to zero "
                     "water for cooling — cite this when a developer claims "
                     "evaporative water draw is unavoidable."},
        ],
    },
    "Amazon (AWS)": {
        "pattern": (
            "The hardest bargainer on taxes — AWS extracts enterprise-zone "
            "abatements and has litigated assessments — but its Oregon deals "
            "prove terms are reopenable when officials organize. Leverage "
            "sits with whoever controls the next approval; its 'water "
            "positive by 2030' pledge is a hook for binding water terms."
        ),
        "concessions": [
            {"where": "Morrow & Umatilla Counties, OR", "year": "2022",
             "what": "Renegotiated enterprise-zone tax agreements to raise "
                     "annual community payments after county commissioners "
                     "and residents pushed back on earlier abatements."},
            {"where": "Loudoun County, VA", "year": "ongoing",
             "what": "Pays hundreds of millions per year in data-center "
                     "property taxes — precedent that a jurisdiction with "
                     "market power can decline abatements entirely."},
        ],
    },
    "QTS": {
        "pattern": (
            "Blackstone-owned and growth-driven — entitlement delay is its "
            "biggest cost, which makes timeline leverage real. In contested "
            "Virginia rezonings QTS offered proffers (buffers, transmission "
            "undergrounding contributions, community funds) to keep projects "
            "moving. Get proffers recorded as binding conditions of approval, "
            "not letters of intent."
        ),
        "concessions": [
            {"where": "Prince William County, VA", "year": "2022-23",
             "what": "Offered rezoning proffers — setbacks, buffering, and "
                     "community contributions — during the contested Digital "
                     "Gateway rezoning; the approval was later challenged in "
                     "court, a reminder to secure commitments that survive "
                     "litigation."},
        ],
    },
    "Vantage": {
        "pattern": (
            "Colocation developer that needs local zoning wins to serve "
            "hyperscaler tenants; it has accepted CBAs as zoning conditions "
            "when boards held firm through a moratorium."
        ),
        "concessions": [
            {"where": "Groton, CT", "year": "2023",
             "what": "Agreed to a CBA funding a $2.5M community recreation "
                     "center as part of permanent zoning controls adopted "
                     "after a year-long moratorium."},
        ],
    },
}

# What similar communities actually won — shown in the Start Here wizard's
# impact step so the CBA target reads as precedent, not aspiration.
CBA_BENCHMARKS = [
    {"community": "The Dalles", "state": "OR", "company": "Google",
     "won": "$29M wastewater treatment upgrade + recycled-water cooling; "
            "city capped DC draws at 25% of municipal supply"},
    {"community": "Groton", "state": "CT", "company": "Vantage",
     "won": "$2.5M community recreation center CBA, recorded as a zoning "
            "condition after a year-long moratorium"},
    {"community": "Morrow & Umatilla Counties", "state": "OR",
     "company": "Amazon (AWS)",
     "won": "Renegotiated tax agreements with higher annual community "
            "payments after commissioners pushed back"},
    {"community": "Loudoun County", "state": "VA", "company": "Multiple",
     "won": "Hundreds of millions/year in data-center property taxes — "
            "~38% of the county budget — by declining abatements"},
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
         {"text": "UC Riverside & Caltech researchers project that air "
                  "pollution from U.S. data centers could contribute to "
                  "roughly 1,300 premature deaths and 600,000 asthma-symptom "
                  "cases a year by 2030, with public-health costs "
                  "approaching $20B annually.", "src": "unpaid_toll"},
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
         {"text": "PJM's 2025 capacity auction cleared at a record $16.4B — "
                  "with data centers responsible for roughly 40% (~$6.5B) "
                  "of the increase, costs that flow through to ratepayers "
                  "across 13 states.", "src": "pjm_auction25"},
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
                  "325-580 TWh by 2030 (Berkeley Lab) — up to ~12% of "
                  "national consumption — with much of the new supply "
                  "coming from natural gas.", "src": "lbnl"},
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

# State-level residential electricity rates ($/kWh, 2024 EIA average)
# and grid carbon intensity (gCO2/kWh, eGRID 2022 subregion averages
# mapped to dominant state grid). Used by the local impact calculator.
STATE_GRID_PROFILES = {
    "Alabama":        {"rate": 0.146, "gco2": 380, "water_stress": "low"},
    "Alaska":         {"rate": 0.229, "gco2": 450, "water_stress": "low"},
    "Arizona":        {"rate": 0.139, "gco2": 390, "water_stress": "high"},
    "Arkansas":       {"rate": 0.124, "gco2": 410, "water_stress": "low"},
    "California":     {"rate": 0.285, "gco2": 210, "water_stress": "high"},
    "Colorado":       {"rate": 0.150, "gco2": 420, "water_stress": "medium"},
    "Connecticut":    {"rate": 0.268, "gco2": 200, "water_stress": "low"},
    "Delaware":       {"rate": 0.155, "gco2": 370, "water_stress": "low"},
    "District of Columbia": {"rate": 0.158, "gco2": 340, "water_stress": "low"},
    "Florida":        {"rate": 0.157, "gco2": 370, "water_stress": "low"},
    "Georgia":        {"rate": 0.143, "gco2": 370, "water_stress": "low"},
    "Hawaii":         {"rate": 0.410, "gco2": 550, "water_stress": "high"},
    "Idaho":          {"rate": 0.112, "gco2": 120, "water_stress": "medium"},
    "Illinois":       {"rate": 0.154, "gco2": 310, "water_stress": "low"},
    "Indiana":        {"rate": 0.149, "gco2": 430, "water_stress": "low"},
    "Iowa":           {"rate": 0.139, "gco2": 410, "water_stress": "low"},
    "Kansas":         {"rate": 0.142, "gco2": 420, "water_stress": "medium"},
    "Kentucky":       {"rate": 0.126, "gco2": 460, "water_stress": "low"},
    "Louisiana":      {"rate": 0.117, "gco2": 380, "water_stress": "low"},
    "Maine":          {"rate": 0.228, "gco2": 180, "water_stress": "low"},
    "Maryland":       {"rate": 0.160, "gco2": 340, "water_stress": "low"},
    "Massachusetts":  {"rate": 0.280, "gco2": 280, "water_stress": "low"},
    "Michigan":       {"rate": 0.186, "gco2": 390, "water_stress": "low"},
    "Minnesota":      {"rate": 0.151, "gco2": 350, "water_stress": "low"},
    "Mississippi":    {"rate": 0.131, "gco2": 400, "water_stress": "low"},
    "Missouri":       {"rate": 0.131, "gco2": 440, "water_stress": "low"},
    "Montana":        {"rate": 0.125, "gco2": 340, "water_stress": "low"},
    "Nebraska":       {"rate": 0.121, "gco2": 420, "water_stress": "low"},
    "Nevada":         {"rate": 0.138, "gco2": 330, "water_stress": "high"},
    "New Hampshire":  {"rate": 0.243, "gco2": 190, "water_stress": "low"},
    "New Jersey":     {"rate": 0.187, "gco2": 250, "water_stress": "low"},
    "New Mexico":     {"rate": 0.143, "gco2": 410, "water_stress": "high"},
    "New York":       {"rate": 0.223, "gco2": 250, "water_stress": "low"},
    "North Carolina": {"rate": 0.132, "gco2": 350, "water_stress": "low"},
    "North Dakota":   {"rate": 0.117, "gco2": 510, "water_stress": "low"},
    "Ohio":           {"rate": 0.144, "gco2": 420, "water_stress": "low"},
    "Oklahoma":       {"rate": 0.121, "gco2": 350, "water_stress": "medium"},
    "Oregon":         {"rate": 0.128, "gco2": 140, "water_stress": "medium"},
    "Pennsylvania":   {"rate": 0.171, "gco2": 310, "water_stress": "low"},
    "Rhode Island":   {"rate": 0.265, "gco2": 280, "water_stress": "low"},
    "South Carolina": {"rate": 0.146, "gco2": 300, "water_stress": "low"},
    "South Dakota":   {"rate": 0.128, "gco2": 250, "water_stress": "low"},
    "Tennessee":      {"rate": 0.125, "gco2": 350, "water_stress": "low"},
    "Texas":          {"rate": 0.142, "gco2": 350, "water_stress": "medium"},
    "Utah":           {"rate": 0.114, "gco2": 440, "water_stress": "high"},
    "Vermont":        {"rate": 0.207, "gco2": 30,  "water_stress": "low"},
    "Virginia":       {"rate": 0.142, "gco2": 330, "water_stress": "low"},
    "Washington":     {"rate": 0.112, "gco2": 80,  "water_stress": "medium"},
    "West Virginia":  {"rate": 0.131, "gco2": 520, "water_stress": "low"},
    "Wisconsin":      {"rate": 0.162, "gco2": 380, "water_stress": "low"},
    "Wyoming":        {"rate": 0.111, "gco2": 460, "water_stress": "low"},
}

# Named campus siting locations: regional temperature penalty on PUE,
# interconnection queue wait (months), and grid carbon (gCO2/kWh). `iso` is
# the regional grid operator the site sits under; the community siting
# evaluator rolls these rows up by ISO rather than keeping its own table.
# Queue waits from LBNL "Queued Up" (2025) + ISO interconnection dashboards;
# carbon from eGRID 2022 subregion averages.
SITING_REGIONS = [
    {"region": "Northern Virginia (PJM)",                     "iso": "PJM (Mid-Atlantic / Ohio Valley)", "pue_adj": 0.02, "queue_months": 60, "gco2": 380},
    {"region": "West Texas (ERCOT)",                          "iso": "ERCOT (Texas)",                    "pue_adj": 0.05, "queue_months": 24, "gco2": 340},
    {"region": "Central Iowa (MISO)",                         "iso": "MISO (Midwest)",                   "pue_adj": 0.01, "queue_months": 48, "gco2": 410},
    {"region": "Pacific Northwest (BPA / PacifiCorp)",        "iso": "BPA / PacifiCorp (Northwest)",     "pue_adj": 0.00, "queue_months": 54, "gco2": 180},
    {"region": "Central Ohio (PJM)",                          "iso": "PJM (Mid-Atlantic / Ohio Valley)", "pue_adj": 0.02, "queue_months": 54, "gco2": 420},
    {"region": "Georgia / Atlanta Metro (SERC)",              "iso": "SERC (Southeast)",                 "pue_adj": 0.04, "queue_months": 36, "gco2": 370},
    {"region": "Phoenix, Arizona (SPP West)",                 "iso": "SPP (Great Plains)",               "pue_adj": 0.08, "queue_months": 30, "gco2": 390},
    {"region": "South Carolina Midlands (Duke / SERC)",       "iso": "SERC (Southeast)",                 "pue_adj": 0.04, "queue_months": 36, "gco2": 340},
    {"region": "North Carolina Piedmont (Duke / PJM)",        "iso": "SERC (Southeast)",                 "pue_adj": 0.03, "queue_months": 42, "gco2": 350},
    {"region": "Chicago / NE Illinois (PJM / ComEd)",         "iso": "PJM (Mid-Atlantic / Ohio Valley)", "pue_adj": 0.01, "queue_months": 48, "gco2": 310},
    {"region": "Dallas–Fort Worth (ERCOT)",                   "iso": "ERCOT (Texas)",                    "pue_adj": 0.05, "queue_months": 24, "gco2": 360},
    {"region": "Salt Lake City, Utah (PacifiCorp)",           "iso": "BPA / PacifiCorp (Northwest)",     "pue_adj": 0.02, "queue_months": 42, "gco2": 440},
    {"region": "New York Metro (NYISO)",                      "iso": "NYISO (New York)",                 "pue_adj": 0.01, "queue_months": 60, "gco2": 250},
    {"region": "Mississippi Delta (MISO South)",              "iso": "MISO (Midwest)",                   "pue_adj": 0.06, "queue_months": 30, "gco2": 400},
    {"region": "Southeast Michigan (MISO / DTE)",             "iso": "MISO (Midwest)",                   "pue_adj": 0.02, "queue_months": 42, "gco2": 390},
    {"region": "El Paso, Texas (ERCOT West)",                 "iso": "ERCOT (Texas)",                    "pue_adj": 0.07, "queue_months": 24, "gco2": 350},
    {"region": "San Antonio, Texas (ERCOT / CPS Energy)",     "iso": "ERCOT (Texas)",                    "pue_adj": 0.06, "queue_months": 24, "gco2": 340},
    {"region": "Kansas City (SPP)",                           "iso": "SPP (Great Plains)",               "pue_adj": 0.03, "queue_months": 36, "gco2": 420},
    {"region": "Indiana (MISO / AES Indiana)",                "iso": "MISO (Midwest)",                   "pue_adj": 0.02, "queue_months": 42, "gco2": 430},
    {"region": "Nashville, Tennessee (TVA)",                  "iso": "SERC (Southeast)",                 "pue_adj": 0.04, "queue_months": 30, "gco2": 350},
    {"region": "Memphis, Tennessee (TVA / MLGW)",             "iso": "SERC (Southeast)",                 "pue_adj": 0.05, "queue_months": 30, "gco2": 370},
    {"region": "Reno / Sparks, Nevada (NV Energy)",           "iso": "Not sure / Other",                 "pue_adj": 0.04, "queue_months": 36, "gco2": 330},
    {"region": "Las Vegas, Nevada (NV Energy)",               "iso": "Not sure / Other",                 "pue_adj": 0.08, "queue_months": 36, "gco2": 380},
    {"region": "Cheyenne, Wyoming (WAPA / PacifiCorp)",       "iso": "BPA / PacifiCorp (Northwest)",     "pue_adj": 0.00, "queue_months": 36, "gco2": 460},
    {"region": "Quincy, Washington (Grant County PUD)",       "iso": "BPA / PacifiCorp (Northwest)",     "pue_adj": 0.00, "queue_months": 42, "gco2": 80},
    {"region": "The Dalles, Oregon (BPA / PGE)",              "iso": "BPA / PacifiCorp (Northwest)",     "pue_adj": 0.00, "queue_months": 48, "gco2": 120},
    {"region": "Loudoun County, Virginia (Dominion / PJM)",   "iso": "PJM (Mid-Atlantic / Ohio Valley)", "pue_adj": 0.02, "queue_months": 60, "gco2": 380},
    {"region": "Prince William County, Virginia (PJM)",       "iso": "PJM (Mid-Atlantic / Ohio Valley)", "pue_adj": 0.02, "queue_months": 60, "gco2": 380},
    {"region": "Rural Maine (ISO-NE / Versant)",              "iso": "ISO-NE (New England)",             "pue_adj": 0.00, "queue_months": 48, "gco2": 200},
    {"region": "Central Pennsylvania (PJM / PPL)",            "iso": "PJM (Mid-Atlantic / Ohio Valley)", "pue_adj": 0.01, "queue_months": 54, "gco2": 350},
    {"region": "Upstate New York (NYISO North)",              "iso": "NYISO (New York)",                 "pue_adj": 0.00, "queue_months": 54, "gco2": 180},
    {"region": "New Albany, Ohio (AEP / PJM)",                "iso": "PJM (Mid-Atlantic / Ohio Valley)", "pue_adj": 0.02, "queue_months": 54, "gco2": 420},
    {"region": "Papillion / Sarpy County, Nebraska (OPPD)",   "iso": "SPP (Great Plains)",               "pue_adj": 0.02, "queue_months": 36, "gco2": 440},
    {"region": "Albuquerque, New Mexico (PNM / SPP)",         "iso": "SPP (Great Plains)",               "pue_adj": 0.06, "queue_months": 36, "gco2": 370},
    {"region": "Sacramento, California (CAISO / SMUD)",       "iso": "CAISO (California)",               "pue_adj": 0.04, "queue_months": 60, "gco2": 220},
    {"region": "San Jose, California (CAISO / PG&E)",         "iso": "CAISO (California)",               "pue_adj": 0.02, "queue_months": 60, "gco2": 220},
    {"region": "Henrico County, Virginia (Dominion / PJM)",   "iso": "PJM (Mid-Atlantic / Ohio Valley)", "pue_adj": 0.03, "queue_months": 60, "gco2": 380},
    {"region": "Abilene, Texas (ERCOT / AEP)",                "iso": "ERCOT (Texas)",                    "pue_adj": 0.06, "queue_months": 24, "gco2": 360},
    {"region": "Stillwater, Oklahoma (SPP / OG&E)",           "iso": "SPP (Great Plains)",               "pue_adj": 0.05, "queue_months": 30, "gco2": 410},
    {"region": "Montgomery County, Missouri (MISO / Ameren)", "iso": "MISO (Midwest)",                   "pue_adj": 0.03, "queue_months": 36, "gco2": 430},
    {"region": "Farmington, Minnesota (MISO / Xcel)",         "iso": "MISO (Midwest)",                   "pue_adj": 0.01, "queue_months": 42, "gco2": 340},
    {"region": "Jackson, Mississippi (Entergy / MISO South)", "iso": "MISO (Midwest)",                   "pue_adj": 0.06, "queue_months": 30, "gco2": 400},
    {"region": "Starke County, Indiana (MISO / NIPSCO)",      "iso": "MISO (Midwest)",                   "pue_adj": 0.02, "queue_months": 42, "gco2": 440},
    {"region": "ACE Basin, South Carolina (Duke / Santee Cooper)", "iso": "SERC (Southeast)",            "pue_adj": 0.04, "queue_months": 36, "gco2": 320},
    {"region": "Stokes County, North Carolina (Duke)",        "iso": "SERC (Southeast)",                 "pue_adj": 0.03, "queue_months": 42, "gco2": 350},
    {"region": "Pittsylvania County, Virginia (AEP / PJM)",   "iso": "PJM (Mid-Atlantic / Ohio Valley)", "pue_adj": 0.03, "queue_months": 54, "gco2": 370},
    {"region": "Morgan County, Georgia (Georgia Power / SERC)", "iso": "SERC (Southeast)",               "pue_adj": 0.04, "queue_months": 36, "gco2": 370},
    {"region": "El Paso County, Texas (ERCOT West / El Paso Electric)", "iso": "ERCOT (Texas)",          "pue_adj": 0.07, "queue_months": 24, "gco2": 350},
    {"region": "Mount Pleasant, Wisconsin (MISO / WE Energies)", "iso": "MISO (Midwest)",                "pue_adj": 0.01, "queue_months": 42, "gco2": 380},
    {"region": "Lousiana Gulf Coast (MISO South / Entergy)",  "iso": "MISO (Midwest)",                   "pue_adj": 0.06, "queue_months": 30, "gco2": 380},
]

# Site name → (PUE adjustment, queue months, grid gCO2/kWh) for the sandbox.
SITING_REGION_PROFILES = {
    r["region"]: (r["pue_adj"], r["queue_months"], r["gco2"])
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
    "dc_ownership": ("Data-center operator ownership & M&A — compiled from trade press (Data Center Dynamics, dgtlinfra, ABI Research) + operator releases; automated fact-check pending",
                     "https://dgtlinfra.com/data-center-companies/"),
    "vantage_dbsl": ("Vantage Data Centers — $9.2B equity investment led by DigitalBridge & Silver Lake (closed Jun 2024)",
                     "https://vantage-dc.com/news/vantage-data-centers-completes-9-2-billion-equity-investment-led-by-digitalbridge-and-silver-lake/"),
    "switch_dbif":  ("Switch, Inc. — DigitalBridge & IFM Investors take-private (~$11B EV, 2022)",
                     "https://dgtlinfra.com/digitalbridge-ifm-switch-inc-data-center/"),
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
    "eia_price_components": ("EIA — Electricity prices reflect rising delivery costs, declining power production costs (Today in Energy)",
                     "https://www.eia.gov/todayinenergy/detail.php?id=32812"),
    "lbnl_price_trends": ("Berkeley Lab (LBNL) — Retail Electricity Price and Cost Trends: 2024 Update (FERC Form 1 data through 2023)",
                     "https://eta-publications.lbl.gov/sites/default/files/2025-01/retail_price_and_cost_trends_2024_update_final_v3.pdf"),
    # --- How the RTOs/ISOs & FERC are responding (Data centers tab) ---
    "ferc_pjm_colo": ("FERC — directs PJM to write co-location rules for data centers (Dec 18, 2025 fact sheet; Docket EL25-49/AD24-11)",
                     "https://www.ferc.gov/news-events/news/fact-sheet-ferc-directs-nations-largest-grid-operator-create-new-rules-embrace"),
    "ferc_showcause": ("FERC — show-cause orders to MISO, SPP & other RTOs on large-load interconnection (Jun 18, 2026)",
                     "https://www.ferc.gov/news-events/news/ferc-launches-aggressive-targeted-action-speed-large-load-integration"),
    "pjm_auction25": ("PJM 2025 capacity auction — record $16.4B; data centers ~40% ($6.5B) of cost",
                     "https://www.utilitydive.com/news/data-centers-pjm-capacity-auction/808951/"),
    "pjm_auction_imm_6b": ("PJM IMM Bowring — data centers drove $6.3B (38%) of $16.4B 2028/29 capacity auction cost (Jul 2026)",
                     "https://www.utilitydive.com/news/pjm-data-centers-capacity-auction-imm-bowring/825626/"),
    "pjm_bra_2028":  ("PJM 2028/29 BRA — 134,479 MW cleared at $325/MW-day; 2028/29 delivery year (Jul 14, 2026)",
                     "https://insidelines.pjm.com/pjm-auction-procures-134311-mw-of-generation-resources-supply-responds-to-price-signal/"),
    "pjm_bra_2027":  ("PJM 2027/28 BRA — hit $333.44 price cap; first-ever RTO-wide reliability shortfall of 6,625 MW (Dec 2025)",
                     "https://www.pjm.com/-/media/DotCom/markets-ops/rpm/rpm-auction-info/2027-2028/2027-2028-bra-report.pdf"),
    "cub_pjm_reform": ("Citizens Utility Board — sustained high PJM capacity prices ramp up urgency for data center reform (Jul 2026)",
                     "https://www.citizensutilityboard.org/blog/2026/07/15/cub-sustained-high-pjm-capacity-prices-ramp-up-urgency-for-data-center-reform/"),
    "ieefa_pjm_10x": ("IEEFA — projected data center growth spurs PJM capacity prices by factor of 10",
                     "https://ieefa.org/resources/projected-data-center-growth-spurs-pjm-capacity-prices-factor-10"),
    "tx_sb6_ll":    ("Texas SB 6 — ERCOT may curtail/disconnect large loads (≥75 MW) in emergencies; new interconnection standards (2025)",
                     "https://www.utilitydive.com/news/texas-law-gives-grid-operator-power-to-disconnect-data-centers-during-crisi/751587/"),
    "spp_hill":     ("SPP — High Impact Large Load (HILL) 90-day study process (RR696, 2025)",
                     "https://perkinscoie.com/insights/update/new-southwest-power-pool-rule-could-supercharge-industrial-and-data-center"),
    "miso_llir":    ("MISO — Large Load Additions & Large Load Interconnection Reliability Requirements (2025–26)",
                     "https://www.misoenergy.org/planning/large-loads---container-page/large-load-additions/"),
    "gartner":      ("Gartner — data-center electricity to double by 2030 (~980 TWh)",
                     "https://www.gartner.com/en/newsroom/press-releases/2025-11-17-gartner-says-electricity-demand-for-data-centers-to-grow-16-percent-in-2025-and-double-by-2030"),
    "bnef_106":     ("BloombergNEF — US data-center power demand ~106 GW by 2035",
                     "https://www.utilitydive.com/news/us-data-center-power-demand-could-reach-106-gw-by-2035-bloombergnef/806972/"),
    "wri_range":    ("World Resources Institute — US 2030 forecasts span 206–970 TWh",
                     "https://www.wri.org/insights/us-data-centers-electricity-demand"),
    "sp_451":       ("S&P Global / 451 Research — global data-center demand ~1,587 TWh by 2030",
                     "https://www.spglobal.com/energy/en/news-research/latest-news/electric-power/110525-global-data-center-power-demand-expected-to-almost-double-by-2030"),
    "epri_pi":      ("EPRI — Powering Intelligence 2026 (US Low/Medium/High scenarios)",
                     "https://powering-intelligence.epri.com/summary-projections.html"),
    "lbnl":         ("Lawrence Berkeley National Lab — US data centers 325–580 TWh by 2030",
                     "https://eta.lbl.gov/publications/2024-united-states-data-center-energy"),
    "belfer":       ("Harvard Belfer Center — AI, Data Centers, and the U.S. Electric Grid (2026)",
                     "https://www.belfercenter.org/publication/ai-data-centers-and-us-electric-grid"),
    "e3_amazon":    ("E3 / Amazon — Tailored for Scale: Designing Electric Rates for Large Loads (2025)",
                     "https://www.ethree.com/wp-content/uploads/2025/01/Tailored-for-Scale-Report.pdf"),
    "columbia_get": ("Columbia University — Grid-Enhancing Technologies and Data Center Demand Response (2025)",
                     "https://energypolicy.columbia.edu/publications/grid-enhancing-technologies/"),
    "ucb_haas":     ("UC Berkeley Energy Institute — What Will Data Centers Do To Your Electric Bill? (2025)",
                     "https://energyathaas.wordpress.com/2025/09/08/what-will-data-centers-do-to-your-electric-bill/"),
    # --- Governor data-center stances (Officials tab) ---
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
    # --- House member data-centre stances (Officials tab) ---
    "house_rpa":    ("House E&C — Ratepayer Protection Act (large loads pay their own way)",
                     "https://www.eenews.net/articles/energy-and-commerce-lawmakers-to-introduce-data-center-bill/"),
    "house_pallone":("Rep. Pallone calls for a national data-center moratorium (2026)",
                     "https://www.eenews.net/articles/data-center-moratorium-still-has-few-takers-on-capitol-hill/"),
    "house_subram": ("Rep. Subramanyam files data-center protection/energy-cost bills (2026)",
                     "https://virginiamercury.com/2026/05/22/va-congressmen-file-energy-cost-transparency-data-center-attack-protections-bills/"),
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
    "ercot_ll":     ("ERCOT — Large Load Integration (forms, reports & Batch Zero)",
                     "https://www.ercot.com/services/rq/large-load-integration"),
    "ercot_ll_bc":  ("ERCOT — Large Load Update to Senate Committee on Business & Commerce "
                     "(Apr 1 2026; data as of Mar 26 2026)",
                     "https://www.ercot.com/files/docs/2026/04/01/ERCOT_LargeLoad_Update_April2026_B-C_-Hearing.pdf"),
    "ercot_ll_tac": ("ERCOT — Large Load Interconnection status, March TAC report (Mar 13 2026)",
                     "https://www.ercot.com/files/docs/2026/03/12/March-TAC-Report.pdf"),
    "electricchoice": ("ElectricChoice.com — U.S. Data Center Power Map by State (2026; updated July 2026; CC-BY 4.0; cites LBNL, EPRINC, EIA)",
                      "https://www.electricchoice.com/datacenters/"),
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
    "oregon_doe_2024":("Oregon Department of Energy — Data Centers and Energy Use in Oregon (2024)",
                      "https://www.oregon.gov/energy/Data-Center-Energy-Use.aspx"),
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
    "meta_community_2026": ("Meta — Data Center Community Action Grants & Local Investment (2026)",
                      "https://sustainability.atmeta.com/community/"),
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
    "nclc":         ("National Consumer Law Center — utility & energy affordability advocacy",
                     "https://www.nclc.org/topic/energy-utilities/"),
    "kleinman":     ("Kleinman Center for Energy Policy (UPenn) — data-center & ratepayer policy research",
                     "https://kleinmanenergy.upenn.edu/"),
    "whyy_dc":      ("WHYY — Pennsylvania data-center electricity cost & ratepayer coverage",
                     "https://whyy.org/articles/pennsylvania-electricity-costs-data-centers/"),
    # --- BNEF 194 GW forecast (July 2026) ---
    "bnef_194gw":   ("Latitude Media — BNEF nearly doubled its forecast for US data center power demand (Jul 2026)",
                     "https://www.latitudemedia.com/news/bnef-nearly-doubled-its-forecast-for-us-data-center-power-demand/"),
    "bnef_194gw_bb":("Bloomberg — Data Centers on Track to Suck Up a Fifth of US Power (Jul 2026)",
                     "https://finance.yahoo.com/technology/ai/articles/data-centers-track-suck-fifth-110000467.html"),
    "tc_4x_dc":     ("TechCrunch — Data centers expected to use 4x more electricity by 2035 (Jul 2026)",
                     "https://techcrunch.com/2026/07/21/data-centers-expected-to-use-4x-more-electricity-by-2035/"),
    "moodys_700b":  ("Moody's Ratings — Hyperscalers' spending surges to \\$700B (2026)",
                     "https://datacentremagazine.com/news/moodys-report-ai-data-centre-spend-set-to-reach-us-700bn"),
    "btm_gas":      ("Natural Gas Intelligence — On-site natural gas generation gains favor with hyperscalers (2026)",
                     "https://naturalgasintel.com/news/on-site-natural-gas-generation-gains-favor-with-hyperscalers-as-bridge-to-grid/"),
    "doe_needs_2026": ("DOE Office of Electricity — 2026 National Transmission Needs Study, Draft for Consultation and Public Comment (Jul 2026)",
                       "https://www.energy.gov/oe/national-transmission-needs-study"),
    # ── Health risks module ──────────────────────────────────────────── #
    "unpaid_toll":  ("Han, Wu, Li, Wierman & Ren — The Unpaid Toll: Quantifying the Public Health Impact of AI (arXiv:2412.06288, UC Riverside/Caltech, 2024)",
                     "https://arxiv.org/abs/2412.06288"),
    "siddik_2021":  ("Siddik, Shehabi & Marston — The environmental footprint of data centers in the United States (Environmental Research Letters, 2021)",
                     "https://iopscience.iop.org/article/10.1088/1748-9326/abfba1"),
    "who_noise":    ("WHO Europe — Environmental Noise Guidelines: noise & cardiovascular/metabolic mechanisms (2018)",
                     "https://www.who.int/europe/publications/i/item/WHO-EURO-2018-3009-42767-59666"),
    "eea_noise":    ("European Environment Agency — Health risks caused by environmental noise in Europe (2020)",
                     "https://www.eea.europa.eu/en/analysis/publications/health-risks-caused-by-environmental-noise-in-europe"),
    "ama_light":    ("American Medical Association — Council on Science & Public Health report on light pollution & nighttime lighting (2012 policy)",
                     "https://www.ama-assn.org/sites/ama-assn.org/files/corp/media-browser/public/about-ama/councils/Council%20Reports/council-on-science-public-health/a12-csaph4-lightpollution-summary.pdf"),
    "ehp_health":   ("Environmental Health Project — The Health Risks of Data Centers (infographic, 2026)",
                     "https://www.environmentalhealthproject.org/_files/ugd/a9ce25_3c3574ea12324c65909d308c3a716e56.pdf"),
    # --- Closest-neighbor protections (property values, buyouts, eminent domain) ---
    "mason_buyout": ("WCHS/Eyewitness News — Mason County, WV 'Good Neighbors' buyout program for data center neighbors",
                     "https://www.wchstv.com/news/local/mason-county-data-center-good-neighbors-program"),
    "ashburn_buyout": ("NBC4 Washington — Loudoun County / Ashburn homeowners report ~$4M buyout offers from data center developers",
                     "https://www.nbcwashington.com/news/local/northern-virginia/data-center-expansion-loudoun-county-homeowners-buyout-offers/"),
    "ga_eminent":   ("Fortune — Georgia power-line eminent domain for data centers: 125% of appraised value offers",
                     "https://fortune.com/2025/06/01/georgia-eminent-domain-power-lines-data-centers/"),
    "nuisance_law": ("Bernstein & Maryanoff — property value diminution & nuisance damages in industrial siting cases (plaintiffs' practice summary)",
                     "https://www.bernsteinandmaryanoff.com/nuisance-property-damage/"),
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
]
LOCAL_OFFICIALS_DF = pd.DataFrame(LOCAL_OFFICIALS)
