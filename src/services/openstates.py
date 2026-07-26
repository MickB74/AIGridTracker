"""
OpenStates v3 — state legislators for a lat/lon point.

This is the free tier of the local-officials stack, and it has one limitation
worth stating plainly in the UI rather than papering over. From OpenStates'
own OpenAPI description of /people.geo:

    "Currently limited to state legislators and US Congress.
     Governors & mayors are not included."

So this fills the gap between a town council and the governor — the state
House/Senate members who vote on preemption bills, NDA bans, and data-center
tax exemptions. It is NOT a substitute for the curated town/county layer.

Requires a free API key from https://open.pluralpolicy.com/accounts/profile/.
Fails soft in every path: returns ([], reason) and never raises into a tab.
"""

import requests
import streamlit as st

_BASE = "https://v3.openstates.org/people.geo"
_TIMEOUT = 12


@st.cache_data(ttl=86_400, show_spinner=False)
def fetch_state_legislators(lat: float, lng: float, api_key: str):
    """State legislators + members of Congress representing a point.

    Returns (rows, note). `rows` is a list of dicts with name, party, chamber,
    district, email, phone, and a link to the member's OpenStates page. On any
    failure `rows` is empty and `note` explains why — callers render the note
    as a caption rather than crashing the tab.
    """
    if not api_key:
        return [], "no-key"
    try:
        r = requests.get(
            _BASE,
            params={"lat": lat, "lng": lng, "include": ["offices"]},
            headers={"X-API-KEY": api_key},
            timeout=_TIMEOUT,
        )
        if r.status_code == 401:
            return [], "OpenStates rejected the API key (401)."
        if r.status_code == 429:
            return [], "OpenStates rate limit reached — try again shortly."
        if r.status_code != 200:
            return [], f"OpenStates returned HTTP {r.status_code}."
        payload = r.json()
    except Exception as e:                                          # noqa: BLE001
        return [], f"Could not reach OpenStates: {e}"

    rows = []
    for p in payload.get("results", []) or []:
        role = p.get("current_role") or {}
        # Offices carry the phone; pick the first with a voice number.
        phone = ""
        for off in p.get("offices") or []:
            if off.get("voice"):
                phone = off["voice"]
                break
        rows.append({
            "name": p.get("name", ""),
            "party": p.get("party", ""),
            "chamber": role.get("org_classification", "") or "",
            "district": str(role.get("district", "") or ""),
            "title": role.get("title", "") or "",
            "email": p.get("email", "") or "",
            "phone": phone,
            "url": p.get("openstates_url", "") or "",
        })

    if not rows:
        return [], "OpenStates returned no legislators for that point."
    return rows, f"{len(rows)} state/federal legislators for this location."
