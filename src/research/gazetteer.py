"""Data-center metro gazetteer.

Colo/REIT filings (Equinix, Digital Realty, QTS…) enumerate their footprint by
METRO NAME in tables — "Atlanta ● ● Frankfurt ● Singapore …" — not as "City,
ST" prose. This maps the metros that actually appear in those filings to a
centroid (lat, lon), a US state where applicable, and a country, so a matched
name lands straight in the map schema with coordinates already attached (no
geocoding round-trip for known places).

Coordinates are metro centroids — good enough to plot, not surveyed. Extend the
table as new metros show up; unknown names still surface via the "City, ST"
regex pass and can be geocoded with --geocode.
"""
from __future__ import annotations

# name -> (lat, lon, state_or_"", country)
METROS = {
    # ── United States ──────────────────────────────────────────────
    "Ashburn": (39.05, -77.49, "VA", "USA"),
    "Culpeper": (38.47, -77.99, "VA", "USA"),
    "Northern Virginia": (39.02, -77.48, "VA", "USA"),
    "Atlanta": (33.75, -84.39, "GA", "USA"),
    "Boston": (42.36, -71.06, "MA", "USA"),
    "Chicago": (41.85, -87.65, "IL", "USA"),
    "Dallas": (32.78, -96.80, "TX", "USA"),
    "Denver": (39.74, -104.99, "CO", "USA"),
    "Houston": (29.76, -95.37, "TX", "USA"),
    "Los Angeles": (34.05, -118.24, "CA", "USA"),
    "Miami": (25.77, -80.19, "FL", "USA"),
    "New York": (40.71, -74.01, "NY", "USA"),
    "Philadelphia": (39.95, -75.16, "PA", "USA"),
    "Seattle": (47.61, -122.33, "WA", "USA"),
    "Silicon Valley": (37.35, -121.95, "CA", "USA"),
    "San Jose": (37.34, -121.89, "CA", "USA"),
    "Santa Clara": (37.35, -121.95, "CA", "USA"),
    "Phoenix": (33.45, -112.07, "AZ", "USA"),
    "Portland": (45.52, -122.68, "OR", "USA"),
    "Columbus": (39.96, -83.00, "OH", "USA"),
    "Washington": (38.90, -77.04, "DC", "USA"),
    # ── Canada / LatAm ─────────────────────────────────────────────
    "Calgary": (51.05, -114.07, "", "Canada"),
    "Kamloops": (50.68, -120.33, "", "Canada"),
    "Montreal": (45.50, -73.57, "", "Canada"),
    "Ottawa": (45.42, -75.70, "", "Canada"),
    "Toronto": (43.65, -79.38, "", "Canada"),
    "Vancouver": (49.28, -123.12, "", "Canada"),
    "Winnipeg": (49.90, -97.14, "", "Canada"),
    "Saint John": (45.27, -66.06, "", "Canada"),
    "Mexico City": (19.43, -99.13, "", "Mexico"),
    "Monterrey": (25.69, -100.32, "", "Mexico"),
    "Lima": (-12.05, -77.04, "", "Peru"),
    "Santiago": (-33.45, -70.67, "", "Chile"),
    "Rio de Janeiro": (-22.91, -43.17, "", "Brazil"),
    "Sao Paulo": (-23.55, -46.63, "", "Brazil"),
    # ── EMEA ───────────────────────────────────────────────────────
    "Amsterdam": (52.37, 4.90, "", "Netherlands"),
    "East Netherlands": (52.22, 6.90, "", "Netherlands"),
    "Barcelona": (41.39, 2.17, "", "Spain"),
    "Madrid": (40.42, -3.70, "", "Spain"),
    "Bordeaux": (44.84, -0.58, "", "France"),
    "Paris": (48.86, 2.35, "", "France"),
    "Marseille": (43.30, 5.37, "", "France"),
    "Dublin": (53.35, -6.26, "", "Ireland"),
    "Frankfurt": (50.11, 8.68, "", "Germany"),
    "Hamburg": (53.55, 9.99, "", "Germany"),
    "Munich": (48.14, 11.58, "", "Germany"),
    "Geneva": (46.20, 6.14, "", "Switzerland"),
    "Zurich": (47.38, 8.54, "", "Switzerland"),
    "Genoa": (44.41, 8.93, "", "Italy"),
    "Milan": (45.46, 9.19, "", "Italy"),
    "Helsinki": (60.17, 24.94, "", "Finland"),
    "Stockholm": (59.33, 18.07, "", "Sweden"),
    "Istanbul": (41.01, 28.98, "", "Turkey"),
    "Lisbon": (38.72, -9.14, "", "Portugal"),
    "London": (51.51, -0.13, "", "UK"),
    "Manchester": (53.48, -2.24, "", "UK"),
    "Sofia": (42.70, 23.32, "", "Bulgaria"),
    "Warsaw": (52.23, 21.01, "", "Poland"),
    "Abidjan": (5.36, -4.01, "", "Cote d'Ivoire"),
    "Abu Dhabi": (24.45, 54.38, "", "UAE"),
    "Dubai": (25.20, 55.27, "", "UAE"),
    "Accra": (5.60, -0.19, "", "Ghana"),
    "Johannesburg": (-26.20, 28.05, "", "South Africa"),
    "Lagos": (6.52, 3.38, "", "Nigeria"),
    "Muscat": (23.59, 58.41, "", "Oman"),
    "Salalah": (17.02, 54.09, "", "Oman"),
    # ── APAC ───────────────────────────────────────────────────────
    "Adelaide": (-34.93, 138.60, "", "Australia"),
    "Brisbane": (-27.47, 153.03, "", "Australia"),
    "Canberra": (-35.28, 149.13, "", "Australia"),
    "Melbourne": (-37.81, 144.96, "", "Australia"),
    "Perth": (-31.95, 115.86, "", "Australia"),
    "Sydney": (-33.87, 151.21, "", "Australia"),
    "Chennai": (13.08, 80.27, "", "India"),
    "Mumbai": (19.08, 72.88, "", "India"),
    "Hong Kong": (22.32, 114.17, "", "Hong Kong"),
    "Jakarta": (-6.21, 106.85, "", "Indonesia"),
    "Johor": (1.49, 103.74, "", "Malaysia"),
    "Kuala Lumpur": (3.14, 101.69, "", "Malaysia"),
    "Manila": (14.60, 120.98, "", "Philippines"),
    "Osaka": (34.69, 135.50, "", "Japan"),
    "Tokyo": (35.68, 139.69, "", "Japan"),
    "Seoul": (37.57, 126.98, "", "South Korea"),
    "Shanghai": (31.23, 121.47, "", "China"),
    "Beijing": (39.90, 116.40, "", "China"),
    "Singapore": (1.35, 103.82, "", "Singapore"),
}

# Multi-word metros must be tried before single tokens when scanning text,
# so "New York" wins over "York". Longest name first.
METRO_NAMES_BY_LEN = sorted(METROS, key=len, reverse=True)
