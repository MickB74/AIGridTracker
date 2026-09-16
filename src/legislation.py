"""Load and expose the legislation cache for the site build.

Reads data/legislation_cache.json (written by scripts/fetch_legislation.py),
classifies bills into categories, and exposes them as a DataFrame plus
summary helpers. Pure functions, no network, no Streamlit.
"""

import json
from pathlib import Path

import pandas as pd

from src.constants import has_value

_ROOT = Path(__file__).resolve().parent.parent
_CACHE_PATH = _ROOT / "data" / "legislation_cache.json"

# US state abbreviation -> full name
_STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
    "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
    "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
    "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
    "DC": "District of Columbia",
}

# Progress stage ordering for sorting
PROGRESS_ORDER = {
    "Prefiled": 0,
    "Introduced": 1,
    "Passed Committee": 2,
    "Passed One Chamber": 3,
    "Passed Both Chambers": 4,
    "Signed/Enacted": 5,
    "Vetoed": 6,
}

# Category priority for primary classification
CATEGORY_PRIORITY = [
    "Data Centers",
    "AI Regulation",
    "Deepfakes & Synthetic Media",
    "Privacy",
    "Energy & Grid",
    "Water",
    "Tax & Incentives",
    "Healthcare",
    "Education",
    "Employment & Labor",
    "Other",
]


def load_legislation():
    """Load the legislation cache and return (bills_list, meta_dict).

    Returns an empty list and empty dict if the cache doesn't exist —
    the build must not crash on a missing cache, it just skips the page.
    """
    if not _CACHE_PATH.exists():
        return [], {}
    with open(_CACHE_PATH) as f:
        data = json.load(f)
    bills = list(data.get("bills", {}).values())
    meta = data.get("search_meta", {})
    meta["last_updated"] = data.get("last_updated")
    return bills, meta


def legislation_df():
    """Return a DataFrame of all cached bills, sorted by status_date desc."""
    bills, _ = load_legislation()
    if not bills:
        return pd.DataFrame()

    df = pd.DataFrame(bills)

    # Add full state name
    if "state" in df.columns:
        df["state_name"] = df["state"].map(lambda s: _STATE_NAMES.get(s, s))

    # Primary category (first in priority order)
    if "categories" in df.columns:
        def _primary(cats):
            if not cats:
                return "Other"
            for c in CATEGORY_PRIORITY:
                if c in cats:
                    return c
            return cats[0]
        df["primary_category"] = df["categories"].map(_primary)

    # Progress sort key
    if "progress_stage" in df.columns:
        df["progress_order"] = df["progress_stage"].map(
            lambda s: PROGRESS_ORDER.get(s, 1))

    # Sort by most recent activity
    if "status_date" in df.columns:
        df = df.sort_values("status_date", ascending=False).reset_index(drop=True)

    return df


def legislation_summary():
    """Return summary stats for the legislation page header."""
    df = legislation_df()
    if df.empty:
        return {}

    by_cat = {}
    for cats in df["categories"]:
        if isinstance(cats, list):
            for c in cats:
                by_cat[c] = by_cat.get(c, 0) + 1

    return {
        "total_bills": len(df),
        "states": df["state"].nunique() if "state" in df.columns else 0,
        "by_category": by_cat,
        "by_status": df["status"].value_counts().to_dict() if "status" in df.columns else {},
        "by_progress": df["progress_stage"].value_counts().to_dict() if "progress_stage" in df.columns else {},
        "data_center_count": by_cat.get("Data Centers", 0),
        "ai_regulation_count": by_cat.get("AI Regulation", 0),
    }


def bills_for_state(state_abbr):
    """Return bills for one state, sorted by status_date desc."""
    df = legislation_df()
    if df.empty:
        return df
    return df[df["state"] == state_abbr].reset_index(drop=True)
