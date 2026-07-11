import pathlib
import pandas as pd

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

WATER_ML_PER_WH = 0.26 / 0.24  # ~1.083 mL/Wh, implied by Gemini disclosure

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

# Data-center moratoriums / bans — POINT-IN-TIME SNAPSHOT (mid-2026). Compiled
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
    # --- How the RTOs/ISOs & FERC are responding (Data centers tab) ---
    "ferc_pjm_colo": ("FERC — directs PJM to write co-location rules for data centers (Dec 18, 2025 fact sheet; Docket EL25-49/AD24-11)",
                     "https://www.ferc.gov/news-events/news/fact-sheet-ferc-directs-nations-largest-grid-operator-create-new-rules-embrace"),
    "ferc_showcause": ("FERC — show-cause orders to MISO, SPP & other RTOs on large-load interconnection (Jun 18, 2026)",
                     "https://www.ferc.gov/news-events/news/ferc-launches-aggressive-targeted-action-speed-large-load-integration"),
    "pjm_auction25": ("PJM 2025 capacity auction — record $16.4B; data centers ~40% ($6.5B) of cost",
                     "https://www.utilitydive.com/news/data-centers-pjm-capacity-auction/808951/"),
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
}

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
DC_FORECASTS = pd.DataFrame([
    {"source": "IEA (base)",     "year": 2030, "twh": 945,  "src": "iea_2025"},
    {"source": "IEA (base)",     "year": 2035, "twh": 1200, "src": "iea_2025"},
    {"source": "IEA (lift-off)", "year": 2035, "twh": 1700, "src": "iea_2025"},
    {"source": "Gartner",        "year": 2030, "twh": 980,  "src": "gartner"},
    {"source": "451 Research",   "year": 2030, "twh": 1587, "src": "sp_451"},
    {"source": "BloombergNEF",   "year": 2035, "twh": 1200, "src": "bnef"},
    {"source": "BloombergNEF",   "year": 2050, "twh": 3700, "src": "bnef"},
])

DC_FORECASTS_US = pd.DataFrame([
    {"source": "Goldman Sachs / McKinsey", "twh": 350, "note": "~300–400 range", "src": "wri_range"},
    {"source": "IEA",                      "twh": 425, "note": "~8% of US power", "src": "iea_2025"},
    {"source": "LBNL (Berkeley Lab)",      "twh": 450, "note": "range 325–580",  "src": "lbnl"},
    {"source": "EPRI (medium)",            "twh": 590, "note": "13% of US power", "src": "epri_pi"},
    {"source": "EPRI (high)",              "twh": 790, "note": "17% of US power", "src": "epri_pi"},
    {"source": "BCG",                      "twh": 970, "note": "high end",        "src": "wri_range"},
])

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
