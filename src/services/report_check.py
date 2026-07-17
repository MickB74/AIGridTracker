"""
Report freshness checker — polls each hyperscaler's sustainability-report
landing page and flags when an edition newer than the one this app tracks
appears. Cached daily; fails gracefully offline.
"""

import re
import requests
import streamlit as st

# The report edition currently baked into src/constants.py, per company.
# "have" is the edition year in the report's own title (not the fiscal year).
REPORT_REGISTRY = {
    "Google": {
        "have": 2026,
        "label": "2026 Environmental Report (FY2025 data)",
        "url": "https://sustainability.google/reports/",
    },
    "Meta": {
        "have": 2025,
        "label": "2025 Sustainability Report (FY2024 data)",
        "url": "https://sustainability.atmeta.com/",
    },
    "Microsoft": {
        # The FY2025 report was published in 2026 and the page references it by
        # publication year, so 2026 is the max year the current edition shows.
        "have": 2026,
        "label": "2025 Environmental Sustainability Report (FY2025 data)",
        "url": "https://www.microsoft.com/en-us/corporate-responsibility/sustainability/report",
    },
    "Amazon / AWS": {
        "have": 2025,
        "label": "2025 Sustainability Report (CY2025 data)",
        "url": "https://sustainability.aboutamazon.com/reports",
    },
}

_KEYWORD_BEFORE = re.compile(
    r"(20\d{2})[^<>{}]{0,60}?(?:Environmental|Sustainability)\s+(?:Report|Data)",
    re.IGNORECASE)
_KEYWORD_AFTER = re.compile(
    r"(?:Environmental|Sustainability)\s+(?:Report|Data)[^<>{}]{0,60}?(20\d{2})",
    re.IGNORECASE)


@st.cache_data(ttl=86400, show_spinner=False)
def check_report_freshness():
    """Return a list of dicts: company, tracked, url, status, latest_seen.

    status is one of: "newer" (a later edition was spotted), "current",
    "unknown" (page fetched but no year found), "unreachable" (fetch failed).
    Never raises.
    """
    results = []
    for company, info in REPORT_REGISTRY.items():
        status, latest_seen = "unknown", None
        try:
            r = requests.get(
                info["url"], timeout=10,
                headers={"User-Agent": "Mozilla/5.0 (GridWatchAI report checker)"})
            r.raise_for_status()
            years = [int(m.group(1)) for m in _KEYWORD_BEFORE.finditer(r.text)]
            years += [int(m.group(1)) for m in _KEYWORD_AFTER.finditer(r.text)]
            pool = [y for y in years if 2020 <= y <= 2035]
            if pool:
                latest_seen = max(pool)
                status = "newer" if latest_seen > info["have"] else "current"
        except Exception:
            status = "unreachable"
        results.append({
            "company": company,
            "tracked": info["label"],
            "url": info["url"],
            "status": status,
            "latest_seen": latest_seen,
        })
    return results
