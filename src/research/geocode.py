"""Optional geocoding via OpenStreetMap Nominatim (free, no key).

Nominatim's usage policy caps you at ~1 request/second and requires a
descriptive User-Agent. Off by default in the CLI (--geocode to enable) so a
plain research run stays fast and dependency-free. Fails soft: an unresolved
place returns (None, None) rather than raising.
"""
from __future__ import annotations

import time
import requests

_URL = "https://nominatim.openstreetmap.org/search"
_MIN_GAP = 1.05  # honor the 1 req/sec policy
_last = [0.0]


def geocode(location: str, state: str = "", country: str = "USA",
            ua: str = "AIGridTracker facilities-research (mickeybarry@gmail.com)"):
    """Return (lat, lon) rounded to 4 dp for a "City, ST" place, or (None, None).

    Coordinates are town/metro centroids — good enough to plot, not surveyed.
    """
    q = ", ".join(p for p in (location, state, country) if p)
    gap = _MIN_GAP - (time.monotonic() - _last[0])
    if gap > 0:
        time.sleep(gap)
    try:
        r = requests.get(
            _URL, params={"q": q, "format": "json", "limit": 1},
            headers={"User-Agent": ua}, timeout=20)
        _last[0] = time.monotonic()
        r.raise_for_status()
        hits = r.json()
        if hits:
            return round(float(hits[0]["lat"]), 4), round(float(hits[0]["lon"]), 4)
    except Exception:                                             # noqa: BLE001
        _last[0] = time.monotonic()
    return None, None
