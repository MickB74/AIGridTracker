"""
Learn tab — educational explainer on data centers, AI infrastructure,
inputs/outputs, efficiency strategies, and site-selection criteria.
"""

import math
import streamlit as st
import pandas as pd
import altair as alt
import requests


# ── Community Siting Evaluator — lookup tables ───────────────────────────── #

_GRID_REGIONS = {
    "PJM (Mid-Atlantic / Ohio Valley)": {
        "power": 8, "fiber": 9, "queue_months": 60, "grid_intensity": 380,
    },
    "ERCOT (Texas)": {
        "power": 9, "fiber": 7, "queue_months": 24, "grid_intensity": 340,
    },
    "MISO (Midwest)": {
        "power": 7, "fiber": 5, "queue_months": 48, "grid_intensity": 410,
    },
    "SPP (Great Plains)": {
        "power": 6, "fiber": 4, "queue_months": 42, "grid_intensity": 370,
    },
    "CAISO (California)": {
        "power": 5, "fiber": 8, "queue_months": 48, "grid_intensity": 210,
    },
    "BPA / PacifiCorp (Northwest)": {
        "power": 7, "fiber": 5, "queue_months": 54, "grid_intensity": 180,
    },
    "ISO-NE (New England)": {
        "power": 4, "fiber": 7, "queue_months": 54, "grid_intensity": 290,
    },
    "NYISO (New York)": {
        "power": 5, "fiber": 8, "queue_months": 48, "grid_intensity": 250,
    },
    "SERC (Southeast)": {
        "power": 7, "fiber": 6, "queue_months": 36, "grid_intensity": 400,
    },
    "Not sure / Other": {
        "power": 6, "fiber": 5, "queue_months": 42, "grid_intensity": 350,
    },
}

# State → grid region key (for auto-detection from geocoded address)
_STATE_TO_GRID = {
    "VA": "PJM (Mid-Atlantic / Ohio Valley)", "MD": "PJM (Mid-Atlantic / Ohio Valley)",
    "PA": "PJM (Mid-Atlantic / Ohio Valley)", "OH": "PJM (Mid-Atlantic / Ohio Valley)",
    "WV": "PJM (Mid-Atlantic / Ohio Valley)", "NJ": "PJM (Mid-Atlantic / Ohio Valley)",
    "DE": "PJM (Mid-Atlantic / Ohio Valley)", "DC": "PJM (Mid-Atlantic / Ohio Valley)",
    "KY": "PJM (Mid-Atlantic / Ohio Valley)", "IN": "PJM (Mid-Atlantic / Ohio Valley)",
    "NC": "SERC (Southeast)",
    "TX": "ERCOT (Texas)",
    "IA": "MISO (Midwest)", "MN": "MISO (Midwest)", "WI": "MISO (Midwest)",
    "IL": "MISO (Midwest)", "MI": "MISO (Midwest)", "MO": "MISO (Midwest)",
    "AR": "MISO (Midwest)", "LA": "MISO (Midwest)", "MS": "MISO (Midwest)",
    "ND": "MISO (Midwest)",
    "KS": "SPP (Great Plains)", "OK": "SPP (Great Plains)",
    "NE": "SPP (Great Plains)", "SD": "SPP (Great Plains)",
    "NM": "SPP (Great Plains)",
    "CA": "CAISO (California)",
    "OR": "BPA / PacifiCorp (Northwest)", "WA": "BPA / PacifiCorp (Northwest)",
    "ID": "BPA / PacifiCorp (Northwest)", "MT": "BPA / PacifiCorp (Northwest)",
    "UT": "BPA / PacifiCorp (Northwest)", "WY": "BPA / PacifiCorp (Northwest)",
    "MA": "ISO-NE (New England)", "CT": "ISO-NE (New England)",
    "NH": "ISO-NE (New England)", "VT": "ISO-NE (New England)",
    "ME": "ISO-NE (New England)", "RI": "ISO-NE (New England)",
    "NY": "NYISO (New York)",
    "GA": "SERC (Southeast)", "SC": "SERC (Southeast)", "AL": "SERC (Southeast)",
    "TN": "SERC (Southeast)", "FL": "SERC (Southeast)",
    "CO": "Not sure / Other", "AZ": "Not sure / Other", "NV": "Not sure / Other",
    "HI": "Not sure / Other", "AK": "Not sure / Other",
}

# State-level tax incentive scores (0–10).
# Sources: stateside.com DC incentive tracker, Rich Miller / DCF state rankings
_STATE_TAX = {
    "VA": 9, "TX": 8, "GA": 8, "IN": 8, "OH": 7, "NC": 7, "SC": 7,
    "NV": 7, "IA": 7, "MS": 7, "OK": 7, "TN": 7, "AL": 6, "NE": 6,
    "ND": 6, "SD": 6, "KS": 6, "MO": 6, "AZ": 6, "UT": 6, "OR": 6,
    "PA": 5, "IL": 5, "MI": 5, "WI": 5, "MN": 5, "CO": 5, "WA": 5,
    "FL": 5, "KY": 5, "AR": 5, "LA": 5, "NM": 4, "WV": 4, "ID": 4,
    "MT": 4, "WY": 4, "MD": 4, "DE": 4, "ME": 3, "VT": 3, "NH": 3,
    "RI": 3, "CT": 3, "NJ": 3, "NY": 3, "MA": 3, "CA": 2, "HI": 1,
}

# State-level permitting friendliness (0–10).
# Combines zoning flexibility, moratorium status, and speed reputation.
_STATE_PERMIT = {
    "TX": 9, "VA": 8, "GA": 8, "IN": 8, "NC": 7, "SC": 7, "OH": 7,
    "TN": 7, "NV": 7, "AZ": 7, "IA": 7, "OK": 7, "MS": 7, "AL": 7,
    "SD": 7, "ND": 7, "NE": 6, "KS": 6, "MO": 6, "AR": 6, "LA": 6,
    "UT": 6, "ID": 6, "WY": 6, "KY": 6, "FL": 6, "CO": 5, "OR": 5,
    "WA": 5, "MT": 5, "PA": 5, "IL": 5, "MI": 5, "WI": 5, "MN": 5,
    "NM": 5, "WV": 5, "MD": 4, "DE": 4, "ME": 4, "NH": 4, "RI": 4,
    "VT": 3, "CT": 3, "NJ": 3, "MA": 3, "NY": 3, "CA": 2, "HI": 2,
}

# State-level natural disaster safety (0–10, 10 = low risk).
# Blends FEMA risk index, tornado/hurricane/earthquake/flood exposure.
_STATE_DISASTER = {
    "MN": 7, "WI": 7, "MI": 7, "OH": 7, "PA": 7, "NY": 7, "VT": 8,
    "NH": 8, "ME": 8, "MA": 6, "CT": 6, "RI": 6, "NJ": 5, "DE": 5,
    "MD": 6, "VA": 7, "WV": 7, "NC": 5, "SC": 4, "GA": 5, "FL": 3,
    "AL": 4, "MS": 4, "TN": 5, "KY": 6, "IN": 6, "IL": 5, "IA": 6,
    "MO": 4, "AR": 4, "LA": 3, "TX": 4, "OK": 3, "KS": 4, "NE": 5,
    "SD": 6, "ND": 6, "MT": 7, "WY": 8, "CO": 6, "NM": 6, "AZ": 7,
    "UT": 7, "NV": 7, "ID": 6, "OR": 5, "WA": 4, "CA": 3, "HI": 4,
    "AK": 4,
}

# State-level water availability (0–10).
# Based on USGS water stress, drought monitor historical patterns.
_STATE_WATER = {
    "MN": 8, "WI": 8, "MI": 9, "OH": 8, "PA": 8, "NY": 8, "VT": 8,
    "NH": 8, "ME": 8, "MA": 7, "CT": 7, "RI": 7, "NJ": 6, "DE": 6,
    "MD": 7, "VA": 7, "WV": 8, "NC": 7, "SC": 6, "GA": 6, "FL": 6,
    "AL": 7, "MS": 7, "TN": 7, "KY": 8, "IN": 7, "IL": 7, "IA": 7,
    "MO": 7, "AR": 7, "LA": 8, "TX": 4, "OK": 4, "KS": 4, "NE": 5,
    "SD": 5, "ND": 6, "MT": 6, "WY": 5, "CO": 3, "NM": 2, "AZ": 2,
    "UT": 3, "NV": 2, "ID": 6, "OR": 6, "WA": 7, "CA": 3, "HI": 6,
    "AK": 8,
}

# State-level land cost & availability (0–10).
# Composite of median $/acre and rural acreage availability.
_STATE_LAND = {
    "TX": 8, "IA": 8, "IN": 7, "OH": 7, "GA": 7, "NC": 7, "SC": 7,
    "VA": 5, "TN": 7, "AL": 8, "MS": 8, "AR": 8, "LA": 7, "MO": 7,
    "KS": 9, "OK": 8, "NE": 8, "SD": 9, "ND": 9, "MT": 8, "WY": 8,
    "CO": 5, "NM": 7, "AZ": 6, "UT": 5, "NV": 6, "ID": 6, "OR": 5,
    "WA": 4, "CA": 2, "MI": 6, "WI": 6, "MN": 6, "IL": 6, "PA": 5,
    "NY": 3, "NJ": 2, "MA": 2, "CT": 2, "RI": 2, "NH": 4, "VT": 5,
    "ME": 6, "MD": 3, "DE": 3, "WV": 7, "KY": 7, "FL": 4, "HI": 1,
}

# Major metro centers for fiber/workforce proximity scoring
_MAJOR_METROS = [
    (38.90, -77.04, "Washington DC"),   (40.71, -74.01, "New York"),
    (34.05, -118.24, "Los Angeles"),     (41.88, -87.63, "Chicago"),
    (29.76, -95.37, "Houston"),          (33.45, -112.07, "Phoenix"),
    (29.42, -98.49, "San Antonio"),      (32.78, -96.80, "Dallas"),
    (37.34, -121.89, "San Jose"),        (30.27, -97.74, "Austin"),
    (39.96, -82.99, "Columbus OH"),      (35.23, -80.84, "Charlotte"),
    (39.74, -104.99, "Denver"),          (47.61, -122.33, "Seattle"),
    (36.16, -86.78, "Nashville"),        (39.10, -84.51, "Cincinnati"),
    (39.77, -86.16, "Indianapolis"),     (33.75, -84.39, "Atlanta"),
    (37.54, -77.44, "Richmond"),         (36.85, -75.98, "Virginia Beach"),
    (42.36, -71.06, "Boston"),           (25.76, -80.19, "Miami"),
    (44.98, -93.27, "Minneapolis"),      (38.63, -90.20, "St Louis"),
    (32.72, -117.16, "San Diego"),       (27.95, -82.46, "Tampa"),
    (45.52, -122.68, "Portland OR"),     (35.47, -97.52, "Oklahoma City"),
    (36.17, -115.14, "Las Vegas"),       (43.04, -87.91, "Milwaukee"),
    (35.15, -90.05, "Memphis"),          (30.45, -91.19, "Baton Rouge"),
    (41.08, -81.52, "Akron"),            (40.44, -79.99, "Pittsburgh"),
    (42.33, -83.05, "Detroit"),          (28.54, -81.38, "Orlando"),
    (37.78, -122.42, "San Francisco"),   (40.76, -111.89, "Salt Lake City"),
]


def _haversine_miles(lat1, lon1, lat2, lon2):
    R = 3959
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


def _nearest_metro(lat, lon):
    best_dist, best_name = 1e9, None
    for mlat, mlon, name in _MAJOR_METROS:
        d = _haversine_miles(lat, lon, mlat, mlon)
        if d < best_dist:
            best_dist, best_name = d, name
    return best_dist, best_name


def _fiber_score_from_distance(miles):
    if miles < 15:
        return 9
    if miles < 40:
        return 7
    if miles < 80:
        return 5
    if miles < 150:
        return 3
    return 1


def _workforce_score_from_distance(miles):
    if miles < 25:
        return 8
    if miles < 60:
        return 6
    if miles < 120:
        return 4
    if miles < 200:
        return 3
    return 1


def _extract_state(address: str):
    """Pull 2-letter state code from a geocoded address string."""
    import re
    m = re.search(r'\b([A-Z]{2})\b', address)
    if m and m.group(1) in _STATE_TAX:
        return m.group(1)
    parts = [p.strip() for p in address.split(",")]
    for part in parts:
        tok = part.strip().split()
        for t in tok:
            if t.upper() in _STATE_TAX:
                return t.upper()
    return None


@st.cache_data(ttl=86400, show_spinner=False)
def _geocode_place(query: str):
    """Free geocoding via US Census Bureau (no key needed)."""
    try:
        r = requests.get(
            "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress",
            params={"address": query, "benchmark": "Public_AR_Current", "format": "json"},
            timeout=8,
        )
        r.raise_for_status()
        matches = r.json().get("result", {}).get("addressMatches", [])
        if matches:
            coords = matches[0]["coordinates"]
            addr = matches[0]["matchedAddress"]
            return coords["y"], coords["x"], addr
    except Exception:
        pass
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": query, "format": "json", "limit": 1, "countrycodes": "us"},
            headers={"User-Agent": "GridWatchAI/1.0"},
            timeout=8,
        )
        r.raise_for_status()
        results = r.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"]), results[0].get("display_name", query)
    except Exception:
        pass
    return None, None, None


def _render_community_evaluator():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🏘️ Could they build here?")
    st.markdown("#### Community Siting Evaluator")
    st.markdown(
        "Enter your town or address to see how it scores on the 8 factors "
        "data-center developers use to choose sites. Scores are auto-populated "
        "from public data — adjust any slider if you have better local knowledge."
    )

    place = st.text_input(
        "Your town, city, or address",
        placeholder="e.g. Loudoun County, VA  or  Springfield, IL",
        key="eval_place",
    )

    if not place:
        st.info("Enter a location above to start the evaluation.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    lat, lon, matched = _geocode_place(place)
    state = None
    metro_dist, metro_name = None, None
    if lat is not None:
        state = _extract_state(matched)
        metro_dist, metro_name = _nearest_metro(lat, lon)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Section: Location match ───────────────────────────────────────── #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📍 Your location")
    if lat is not None:
        l1, l2 = st.columns([1.4, 1])
        with l1:
            st.map([{"latitude": lat, "longitude": lon}], zoom=8)
        with l2:
            st.markdown(f"**Matched address**  \n{matched}")
            st.markdown(f"**Coordinates**  \n{lat:.4f}, {lon:.4f}")
            if metro_name:
                st.markdown(f"**Nearest major metro**  \n{metro_name} ({metro_dist:.0f} mi)")
            if state:
                st.markdown(f"**State**  \n{state}")
    else:
        st.warning("Could not geocode this location — select your state below and adjust sliders manually.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Compute defaults ──────────────────────────────────────────────── #
    grid_default = _STATE_TO_GRID.get(state, "Not sure / Other") if state else "Not sure / Other"
    grid_keys = list(_GRID_REGIONS.keys())
    grid_idx = grid_keys.index(grid_default) if grid_default in grid_keys else len(grid_keys) - 1

    tax_default = _STATE_TAX.get(state, 5) if state else 5
    permit_default = _STATE_PERMIT.get(state, 5) if state else 5
    disaster_default = _STATE_DISASTER.get(state, 6) if state else 6
    water_default = _STATE_WATER.get(state, 5) if state else 5
    land_default = _STATE_LAND.get(state, 5) if state else 5
    fiber_default = _fiber_score_from_distance(metro_dist) if metro_dist is not None else 5
    workforce_default = _workforce_score_from_distance(metro_dist) if metro_dist is not None else 5

    # ── Section: What we looked up ────────────────────────────────────── #
    if state or metro_name:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📊 What we looked up")
        st.caption("Auto-detected from your location using public data sources.")

        lu1, lu2, lu3 = st.columns(3)
        with lu1:
            st.markdown("**From state-level data**")
            if state:
                st.markdown(f"- Grid region: {grid_default}")
                st.markdown(f"- Tax incentives: {tax_default}/10")
                st.markdown(f"- Permitting: {permit_default}/10")
        with lu2:
            st.markdown("**Environmental / land**")
            if state:
                st.markdown(f"- Disaster safety: {disaster_default}/10")
                st.markdown(f"- Water availability: {water_default}/10")
                st.markdown(f"- Land cost: {land_default}/10")
        with lu3:
            st.markdown("**From metro proximity**")
            if metro_name:
                st.markdown(f"- Fiber: {fiber_default}/10 ({metro_dist:.0f} mi to {metro_name})")
                st.markdown(f"- Workforce: {workforce_default}/10")

        st.caption(
            "Sources: EIA grid regions, state incentive databases (stateside.com), "
            "FEMA National Risk Index, USGS water stress, USDA land values, "
            "metro proximity for fiber/workforce."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Section: Factor scores (sliders) ──────────────────────────────── #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🎛️ Factor scores")
    st.caption("Pre-filled from public data. Adjust any slider if you have better local knowledge.")

    grid_region = st.selectbox(
        "Grid region / ISO",
        grid_keys, index=grid_idx,
        help="Which regional grid operator covers your area?",
        key="eval_grid",
    )
    region_info = _GRID_REGIONS[grid_region]

    st.markdown("#### Infrastructure")
    inf1, inf2 = st.columns(2)
    with inf1:
        power_score = st.slider(
            "Power availability", 0, 10, region_info["power"],
            help="Spare grid capacity nearby? 10 = abundant, 0 = maxed out.",
            key="eval_power",
        )
    with inf2:
        fiber_score = st.slider(
            "Fiber connectivity", 0, 10, fiber_default,
            help="Proximity to fiber routes and internet exchanges. 10 = fiber hub.",
            key="eval_fiber",
        )

    st.markdown("#### Environment & land")
    env1, env2, env3 = st.columns(3)
    with env1:
        water_score = st.slider(
            "Water access", 0, 10, water_default,
            help="Water supply for industrial cooling. 10 = abundant, 0 = drought-stressed.",
            key="eval_water",
        )
    with env2:
        land_score = st.slider(
            "Land cost & availability", 0, 10, land_default,
            help="Cheap flat acreage outside flood zones. 10 = abundant cheap land.",
            key="eval_land",
        )
    with env3:
        disaster_score = st.slider(
            "Natural disaster safety", 0, 10, disaster_default,
            help="Low earthquake/hurricane/tornado/flood risk. 10 = very low risk.",
            key="eval_disaster",
        )

    st.markdown("#### Policy & workforce")
    pol1, pol2, pol3 = st.columns(3)
    with pol1:
        tax_score = st.slider(
            "Tax incentives", 0, 10, tax_default,
            help="State/county tax abatements for data centers. 10 = aggressive incentives.",
            key="eval_tax",
        )
    with pol2:
        permit_score = st.slider(
            "Permitting speed", 0, 10, permit_default,
            help="How fast does your jurisdiction approve industrial projects? 10 = by-right.",
            key="eval_permit",
        )
    with pol3:
        workforce_score = st.slider(
            "Workforce availability", 0, 10, workforce_default,
            help="Electricians, HVAC techs, network engineers nearby. 10 = strong labor pool.",
            key="eval_workforce",
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Scoring ───────────────────────────────────────────────────────── #
    scores = {
        "Power availability": power_score,
        "Fiber connectivity": fiber_score,
        "Tax incentives": tax_score,
        "Land cost & availability": land_score,
        "Water access": water_score,
        "Permitting speed": permit_score,
        "Natural disaster safety": disaster_score,
        "Workforce": workforce_score,
    }

    weights = {
        "Power availability": 2.0,
        "Fiber connectivity": 1.5,
        "Tax incentives": 1.2,
        "Land cost & availability": 1.0,
        "Water access": 1.0,
        "Permitting speed": 1.3,
        "Natural disaster safety": 0.8,
        "Workforce": 0.7,
    }

    weighted_sum = sum(scores[k] * weights[k] for k in scores)
    max_possible = sum(10 * w for w in weights.values())
    overall = round(weighted_sum / max_possible * 100)

    # ── Section: Results ──────────────────────────────────────────────── #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📋 Results")

    if overall >= 70:
        st.error(
            f"🔴 **High likelihood ({overall}%)** — Your community matches what "
            "data-center developers prioritize. Your area may already be on their "
            "radar. Now is the time to get informed and engaged. "
            "Head to the **🛡️ Negotiation toolkit** tab for model CBA clauses, "
            "a Data Dividend calculator, and a meeting prep checklist."
        )
    elif overall >= 45:
        st.warning(
            f"🟡 **Moderate likelihood ({overall}%)** — Some factors are attractive; "
            "others may deter developers or slow the process. Stay informed about "
            "zoning changes and large land transactions. See the **🛡️ Negotiation "
            "toolkit** tab to prepare in advance."
        )
    else:
        st.success(
            f"🟢 **Lower likelihood ({overall}%)** — Current conditions make your "
            "area less attractive to developers, but this can change quickly if "
            "power, incentives, or zoning shift."
        )

    r1, r2, r3 = st.columns(3)
    r1.metric("Overall Attractiveness", f"{overall}%")
    r2.metric("Grid Queue Wait", f"~{region_info['queue_months']} months")
    r3.metric("Grid Carbon Intensity", f"{region_info['grid_intensity']} gCO₂/kWh")

    st.markdown("#### Score breakdown")
    score_df = pd.DataFrame([
        {"Factor": k, "Your Score": v, "Weight": f"{weights[k]:.1f}×",
         "Weighted": round(v * weights[k], 1)}
        for k, v in scores.items()
    ])
    st.dataframe(score_df, use_container_width=True, hide_index=True,
                 column_config={
                     "Your Score": st.column_config.ProgressColumn(
                         min_value=0, max_value=10, format="%d/10"),
                 })

    strengths = [k for k, v in scores.items() if v >= 7]
    weaknesses = [k for k, v in scores.items() if v <= 3]

    sc1, sc2 = st.columns(2)
    with sc1:
        if strengths:
            st.markdown("**Strongest draws for developers**")
            for s in strengths:
                st.markdown(f"- {s} ({scores[s]}/10)")
    with sc2:
        if weaknesses:
            st.markdown("**Biggest deterrents**")
            for w in weaknesses:
                st.markdown(f"- {w} ({scores[w]}/10)")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Section: What to watch for ────────────────────────────────────── #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🔍 What should you watch for?")
    st.caption("Based on your scores — specific things to monitor in your community.")

    watch_items = []
    if power_score >= 7:
        watch_items.append(
            "⚡ **Grid capacity is a magnet.** Your area has available power — "
            "the #1 factor. Watch for large interconnection requests filed with "
            "your utility or ISO."
        )
    if tax_score >= 7:
        watch_items.append(
            "💰 **Tax incentives attract scouts.** If your state/county offers "
            "abatements, expect developer interest. Review whether incentive "
            "agreements include community benefit requirements."
        )
    if land_score >= 7:
        watch_items.append(
            "🏗️ **Available land draws attention.** Large flat parcels near "
            "power lines are exactly what scouts look for. Monitor large "
            "agricultural land sales and rezoning applications."
        )
    if water_score >= 7 and permit_score >= 5:
        watch_items.append(
            "💧 **Water + permitting = fast build.** Abundant water and "
            "reasonable permitting make your area attractive for evaporative-cooled "
            "facilities. Ask whether your water utility has been contacted by "
            "industrial users."
        )
    if permit_score <= 3:
        watch_items.append(
            "🛡️ **Slow permitting is a buffer — for now.** But developers "
            "lobby for by-right zoning changes. Watch for proposed zoning "
            "amendments that fast-track industrial development."
        )
    if overall >= 60:
        watch_items.append(
            "📋 **General vigilance.** With a score this high, attend planning "
            "commission and zoning board meetings. Ask your local officials if "
            "they've been approached by data-center developers or site selectors."
        )
    if not watch_items:
        watch_items.append(
            "Your community scores low on most factors. Data-center development "
            "is less likely here in the near term, but conditions can change — "
            "especially if new transmission lines, tax incentives, or zoning "
            "changes are proposed."
        )
    for item in watch_items:
        st.markdown(item)

    st.caption(
        "This tool reflects the priorities documented in industry site-selection "
        "guides (CBRE, JLL, Cushman & Wakefield) and SEC filings. Scores are "
        "auto-populated from state-level public data and proximity calculations. "
        "It does **not** predict specific developer plans — it estimates how well "
        "your community matches what they typically look for."
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_learn_tab():
    st.subheader("🎓 Learn — What is a data center and why does it matter?")
    st.caption(
        "A plain-language guide to the buildings behind AI: what goes in, what comes "
        "out, how AI facilities differ from traditional ones, and what companies look "
        "for when choosing where to build."
    )

    with st.expander("📑 On this page", expanded=False):
        st.markdown(
            "**1.** What is a data center? · "
            "**2.** How are AI data centers different? · "
            "**3.** What happens inside an AI data center · "
            "**4.** Using the right model for the task · "
            "**5.** Inputs & outputs · "
            "**6.** Efficiency (PUE, WUE, CUE) · "
            "**7.** Site selection & community siting evaluator · "
            "**8.** Key terms glossary · "
            "**Also below:** 🎮 AI Datacenter Siting Sandbox (interactive simulation)"
        )

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 1 — What is a data center?
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🏢 What is a data center?")
    st.markdown(
        "A **warehouse for computing** — thousands of servers running 24/7 behind "
        "every video stream, banking app, and AI chatbot, kept alive by dedicated "
        "power, cooling, and fiber."
    )

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Global data centers", "~11,000+",
                   help="Facilities with 1 MW+ capacity worldwide (2025)")
        st.caption("From small server rooms to 300+ MW campuses")
    with col_b:
        st.metric("Global electricity use", "~485 TWh (2025)",
                   help="IEA estimate — about 2% of world electricity")
        st.caption("More than many entire countries")
    with col_c:
        st.metric("Projected by 2030", "~945 TWh",
                   help="IEA base projection — could double in 5 years")
        st.caption("Driven largely by AI workloads")

    st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 2 — How are AI data centers different?
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🤖 How are AI data centers different?")

    d1, d2, d3 = st.columns(3)
    with d1:
        st.metric("⚡ Power density", "40–120 kW/rack", "vs 5–15 kW traditional")
        st.caption("Up to 10× more power in the same space — and far more heat.")
    with d2:
        st.metric("🧊 Cooling", "Liquid-cooled", "air can't keep up")
        st.caption("Evaporative towers can consume millions of gallons a day.")
    with d3:
        st.metric("🔌 Grid draw", "50–100 MW", "per training cluster")
        st.caption("The continuous load of a small city, per cluster.")

    st.info(
        "**In one sentence:** a traditional data center serves millions of small, "
        "quick requests; an AI data center runs fewer, far heavier workloads that "
        "demand extreme power density and advanced cooling."
    )
    with st.expander("Read more — why the difference matters"):
        st.markdown("""\
Traditional data centers run **general workloads** — web hosting, email, databases,
video streaming — on standard CPUs drawing moderate power.

- **Power density:** AI racks packed with GPUs like NVIDIA's H100 or B200 draw
  **40–120 kW per rack** vs 5–15 kW for traditional servers. AI facilities need
  vastly more power per square foot and generate far more heat.
- **Cooling:** Standard air cooling can't handle GPU heat loads, so AI facilities
  use **liquid cooling** (piping coolant to chips) or rear-door heat exchangers.
  Some rely on evaporative cooling towers that consume millions of gallons of
  water per day.
- **Grid impact:** When dozens of 50–100 MW clusters concentrate in one region
  (Northern Virginia, Central Texas), they strain the grid, drive up electricity
  rates, and require billions in new transmission infrastructure.
""")
    st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 3 — What actually happens inside an AI data center
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## ⚙️ What actually happens inside an AI data center?")
    st.markdown(
        "Two kinds of work with very different power profiles: **training** "
        "(building the model — one massive, months-long burn) and **inference** "
        "(using it — a smaller but endless drip, billions of requests a day)."
    )

    st.markdown("#### At a glance")
    ti_compare = pd.DataFrame([
        {"Attribute": "Duration", "Training": "Weeks–months (one-time)", "Inference": "Forever (24/7)"},
        {"Attribute": "GPU usage", "Training": "Thousands in lockstep", "Inference": "Spread across clusters"},
        {"Attribute": "Power profile", "Training": "Steady, flat, 24/7", "Inference": "Spiky, follows clock"},
        {"Attribute": "Total lifetime energy", "Training": "~20–30%", "Inference": "~70–80%"},
    ])
    st.dataframe(ti_compare, use_container_width=True, hide_index=True,
                 column_config={
                     "Attribute": st.column_config.TextColumn(width="small"),
                     "Training": st.column_config.TextColumn("🏋️ Training", width="medium"),
                     "Inference": st.column_config.TextColumn("💬 Inference", width="medium"),
                 })

    st.info(
        "**Rule of thumb:** *Training* is a one-time, massive, steady burst to build "
        "the model. *Inference* is the endless drip of everyday use. Training gets the "
        "headlines; inference quietly dominates the long-run footprint."
    )

    with st.expander("Read more — training vs inference, in depth"):
        t_col, i_col = st.columns(2)
        with t_col:
            st.markdown("""\
##### 🏋️ Training — *building* the model
Engineers feed enormous datasets — much of the public internet, books, code — and
the model adjusts billions of internal parameters until it can predict language well.

- **Runs once per model**, but for **weeks or months** without stopping.
- **Thousands of GPUs in lockstep** — a 50–100+ MW cluster running flat-out, 24/7.
- A near-constant, city-sized electrical load that's hard for a grid to absorb.
- A single frontier model can consume **tens of gigawatt-hours** — as much
  electricity as thousands of homes use in a year.
""")
        with i_col:
            st.markdown("""\
##### 💬 Inference — *using* the model
Your prompt goes to a data center, runs through the trained model, and a response
comes back — usually in under a second.

- **Runs constantly, forever** — every chat message and search summary.
- Each request is small, but there are **billions per day** across all users.
- Load is **spiky and follows the clock** — easier to shift toward cleaner grid hours.
- Over a model's lifetime, **inference usually dwarfs training** in total energy.
""")

    st.markdown("#### The full lifecycle, start to finish")

    lifecycle_df = pd.DataFrame([
        {"Stage": "1. Data prep", "Energy": 2, "Type": "Moderate"},
        {"Stage": "2. Training", "Energy": 10, "Type": "HUGE"},
        {"Stage": "3. Fine-tuning", "Energy": 3, "Type": "Moderate"},
        {"Stage": "4. Deployment", "Energy": 1, "Type": "Low"},
        {"Stage": "5. Inference", "Energy": 7, "Type": "Relentless"},
        {"Stage": "6. Retraining", "Energy": 10, "Type": "HUGE"},
    ])
    lifecycle_bar = (
        alt.Chart(lifecycle_df)
        .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6)
        .encode(
            x=alt.X("Energy:Q", title="Relative energy intensity", scale=alt.Scale(domain=[0, 10])),
            y=alt.Y("Stage:N", sort=None, title=None),
            color=alt.Color("Energy:Q",
                scale=alt.Scale(scheme="redyellowgreen", reverse=True, domain=[0, 10]),
                legend=None),
            tooltip=["Stage:N", "Type:N", alt.Tooltip("Energy:Q", title="Intensity (0–10)")],
        ).properties(height=200)
    )
    st.altair_chart(lifecycle_bar, use_container_width=True)

    lc1, lc2, lc3 = st.columns(3)
    lc1.markdown("**One-time burst:** Training & retraining are the biggest single energy draws")
    lc2.markdown("**Never stops:** Inference runs 24/7 for the life of the model")
    lc3.markdown("**The cycle repeats:** Each new model generation starts the process over")

    st.caption(
        "This is why AI facilities come in two flavors: **training campuses** built for "
        "massive, constant power, and **inference campuses** placed close to users for "
        "low latency. Some sites do both."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 4 — Using the right model for the task
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🎯 Using the right model for the task")
    st.markdown(
        "A frontier model can use **10–100× more energy per response** than a small "
        "one — and for most everyday tasks, the small model answers just as well. "
        "Sending every request to the largest model is like taking a semi-truck to "
        "pick up groceries."
    )

    st.info(
        "**The takeaway:** the greenest AI request is often the one that never touches "
        "a giant model. Right-sizing — the *right* model, a *short* prompt, a *cached* "
        "answer when possible — cuts energy dramatically with no visible drop in quality."
    )
    with st.expander("Read more — how teams right-size in practice"):
        st.markdown("""\
- **Model routing** — a lightweight system sends easy questions to a small model and
  only escalates hard ones to a large model.
- **Distillation** — training a small, cheap model to mimic a big one for a specific
  task, keeping most of the quality at a fraction of the cost.
- **Caching & retrieval** — reusing past answers or looking facts up in a database
  instead of re-running the model from scratch.
- **Shorter prompts & outputs** — energy scales with tokens processed, so concise
  in-and-out means less compute.

Small "mini" models already handle the bulk of real traffic — classification,
summarizing, autocomplete, simple Q&A — at a fraction of the energy. Large frontier
models shine at hard reasoning and complex code, but are overkill for routine requests.
""")
    st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 5 — Inputs and Outputs
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🔄 Inputs and outputs — what goes in, what comes out")

    io_in, io_mid, io_out = st.columns([1, 0.4, 1])
    with io_in:
        st.markdown("### 📥 What goes IN")
        for icon, resource, scale in [
            ("⚡", "Electricity", "50–300+ MW"),
            ("💧", "Water", "1–5M gal/day"),
            ("🏗️", "Land", "50–500+ acres"),
            ("🔌", "Fiber", "Redundant paths"),
            ("🖥️", "Hardware", "Refreshed every 3–5 yrs"),
        ]:
            with st.container(border=True):
                st.markdown(f"{icon} **{resource}** — {scale}")
    with io_mid:
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("### &nbsp;&nbsp;➡️")
        st.markdown("### 🏢")
        st.markdown("### &nbsp;&nbsp;➡️")
    with io_out:
        st.markdown("### 📤 What comes OUT")
        for icon, output, impact in [
            ("☁️", "Compute services", "AI & cloud (the product)"),
            ("🌡️", "Waste heat", "Rarely recaptured in US"),
            ("🔊", "Noise", "50–70+ dB at property line"),
            ("💨", "CO₂ emissions", "Varies by grid mix"),
            ("👷", "Jobs", "50–150 permanent"),
            ("💰", "Tax revenue", "Often reduced by abatements"),
        ]:
            with st.container(border=True):
                st.markdown(f"{icon} **{output}** — {impact}")

    st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 6 — Efficiency
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🌱 How can data centers be more efficient?")
    st.markdown(
        "The industry uses several strategies to reduce energy, water, and carbon footprint. "
        "Not all operators adopt all of these — and the gap between the best and worst "
        "performers is wide."
    )

    pue_compare = pd.DataFrame([
        {"Facility type": "Best-in-class (Google/Meta)", "PUE": 1.10},
        {"Facility type": "Good modern facility", "PUE": 1.20},
        {"Facility type": "Industry average (2024)", "PUE": 1.55},
        {"Facility type": "Older / poorly designed", "PUE": 1.80},
    ])
    pue_bar = (
        alt.Chart(pue_compare)
        .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6)
        .encode(
            x=alt.X("PUE:Q", scale=alt.Scale(domain=[1.0, 2.0]), title="PUE (lower = better)"),
            y=alt.Y("Facility type:N", sort=None, title=None),
            color=alt.Color("PUE:Q", scale=alt.Scale(scheme="redyellowgreen", reverse=True, domain=[1.0, 2.0]),
                            legend=None),
            tooltip=["Facility type", alt.Tooltip("PUE:Q", format=".2f")],
        ).properties(height=160)
    )
    perfect_line = alt.Chart(pd.DataFrame([{"pue": 1.0}])).mark_rule(
        color="#10b981", strokeDash=[4, 3], strokeWidth=1.5
    ).encode(x="pue:Q")
    st.altair_chart(pue_bar + perfect_line, use_container_width=True)
    st.caption("🟢 Green dashed = theoretical perfect PUE (1.0). Every 0.1 improvement saves ~7–10% total energy.")

    ef1, ef2, ef3 = st.columns(3)
    ef1.metric("Industry avg PUE", "1.55", "best-in-class: 1.10")
    ef2.metric("Server utilization", "12–18%", "could be 60%+")
    ef3.metric("Liquid cooling savings", "30–50%", "of cooling energy")

    with st.expander("Read more — the six efficiency levers, explained"):
        e1, e2 = st.columns(2)
        with e1:
            st.markdown("""\
##### Power efficiency (PUE)
Total facility energy ÷ IT equipment energy. 1.0 = perfect (impossible);
1.1–1.2 = best-in-class (Google, Meta); industry average ≈ 1.55 (Uptime
Institute, 2024). Every 0.1 reduction saves ~7–10% of total energy.

##### Liquid cooling
Direct-to-chip cooling removes heat far more efficiently than air — 30–50% less
cooling energy, and increasingly required for AI GPU racks drawing 60+ kW.

##### Free cooling
Cold-climate facilities (Nordics, Pacific Northwest, Ireland) use outside air
much of the year, drastically cutting water and chiller energy.
""")
        with e2:
            st.markdown("""\
##### Renewable energy
Leading operators sign PPAs for wind and solar. The gold standard is **24/7
Carbon-Free Energy** — matching consumption with clean energy hour-by-hour on
the same grid, not just annually through credits.

##### Water efficiency (WUE)
Liters of water per kWh of IT energy. 0.0 = air-cooled; 0.2–0.5 = efficient
evaporative; 1.0–2.0 = heavy use. Arid-region facilities are switching to
closed-loop chillers that use zero water at the cost of more energy.

##### Compute efficiency
The cheapest watt is the one you never draw: raise server utilization (industry
average is just 12–18%), optimize models (quantization and distillation cut
inference energy 2–10×), right-size hardware, and schedule deferrable jobs
into off-peak, high-renewable hours.
""")

    st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 7 — Site selection
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 📍 Where do companies build — and what do they look for?")
    st.markdown(
        "Site selection is driven by a specific checklist of requirements. Understanding what "
        "companies prioritize explains why data centers cluster in certain regions — and why "
        "some communities are targeted more than others."
    )

    site_factors = pd.DataFrame([
        {"Factor": "1. Power availability", "Weight": 10, "What they need": "50–300+ MW of firm electricity"},
        {"Factor": "2. Fiber connectivity", "Weight": 8, "What they need": "Dense fiber with low latency"},
        {"Factor": "3. Tax incentives", "Weight": 7, "What they need": "Abatements, exemptions"},
        {"Factor": "4. Land (cheap & flat)", "Weight": 6, "What they need": "50–500 acres, no flood zones"},
        {"Factor": "5. Water access", "Weight": 6, "What they need": "Reliable municipal or well supply"},
        {"Factor": "6. Permitting speed", "Weight": 7, "What they need": "Fast zoning & building permits"},
        {"Factor": "7. Disaster safety", "Weight": 5, "What they need": "Low quake/hurricane/tornado risk"},
        {"Factor": "8. Workforce", "Weight": 4, "What they need": "Electricians, HVAC, network engineers"},
    ])
    factor_bar = (
        alt.Chart(site_factors)
        .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6)
        .encode(
            x=alt.X("Weight:Q", title="Relative importance", scale=alt.Scale(domain=[0, 10])),
            y=alt.Y("Factor:N", sort=None, title=None),
            color=alt.Color("Weight:Q",
                scale=alt.Scale(scheme="orangered", domain=[0, 10]),
                legend=None),
            tooltip=["Factor:N", "What they need:N", alt.Tooltip("Weight:Q", title="Importance (0–10)")],
        ).properties(height=240)
    )
    st.altair_chart(factor_bar, use_container_width=True)
    st.caption("Power is king — everything else follows. Without available grid capacity, no amount of tax incentives matters.")

    st.warning(
        "**What's often missing from this checklist:** community input, cumulative "
        "impact on local water and power resources, noise standards, and long-term "
        "rate impacts on existing ratepayers. These are the gaps this tracker aims "
        "to make visible."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 7b — Community Siting Evaluator
    # ══════════════════════════════════════════════════════════════════════════
    _render_community_evaluator()

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 8 — Key terms glossary
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.expander("📖 Glossary of key terms", expanded=False):
        st.markdown("""\
| Term | Definition |
|------|-----------|
| **PUE** | Power Usage Effectiveness — ratio of total facility energy to IT energy. Lower is better. |
| **WUE** | Water Usage Effectiveness — liters of water per kWh of IT energy. Lower is better. |
| **CFE** | Carbon-Free Energy — electricity from zero-carbon sources (solar, wind, nuclear, hydro). |
| **Hyperscaler** | The largest cloud/AI companies that build their own data centers (Google, Microsoft, Amazon, Meta). |
| **Colocation (colo)** | A data center operator that leases space, power, and cooling to tenants. |
| **Interconnection queue** | The list of projects waiting for grid connection approval from the regional operator (e.g., PJM, ERCOT). |
| **Moratorium** | A temporary ban or pause on new data-center construction, usually enacted by local or state government. |
| **PPA** | Power Purchase Agreement — a long-term contract to buy electricity from a specific generator, often renewable. |
| **Rack density** | The amount of power drawn per server rack, measured in kW. AI racks are 40–120+ kW vs. 5–15 kW traditional. |
| **GPU** | Graphics Processing Unit — specialized chips (like NVIDIA H100/B200) that power AI training and inference. |
| **Inference** | Running a trained AI model to generate responses — what happens when you use ChatGPT, Gemini, etc. |
| **Training** | The initial process of building an AI model by processing massive datasets. Extremely energy-intensive. |
| **Evaporative cooling** | Cooling method that evaporates water to remove heat. Effective but water-intensive. |
| **Liquid cooling** | Piping coolant directly to server chips. More efficient for high-density AI workloads. |
| **Marginal emissions** | The CO₂ rate of the *next* power plant that would turn on to serve new load. The right signal for load-shifting. |
""")
    st.markdown("</div>", unsafe_allow_html=True)

    st.caption(
        "This page is a living explainer. Sources: IEA *Energy and AI* (2025), "
        "Uptime Institute Global Survey (2024), EPRI *Powering Intelligence* (2025), "
        "Google Environmental Report (2024), US DOE Data Center Primer. "
        "See the **📚 Methodology** tab for full citations."
    )
