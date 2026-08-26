"""
Local-officials resolution — the town/county layer of the officials directory.

Two tiers, tried in order, so a page always has something to show:

  1. `curated(locality, state)` — hand-verified names/emails/phones plus the
     governing body's meeting and public-comment mechanics. Sourced from the
     locality's own .gov page; every row carries `source` and `as_of`.
  2. `build_lookup_links(state, locality)` — deterministic directory links.
     No names, but full 51-state coverage and nothing to go stale.

There is deliberately no OpenStates tier. Its API covers state legislators and
Congress ONLY — the spec states "Governors & mayors are not included" — so it
can never stand in for tier 1, which is exactly the layer this module exists to
resolve. The retired app's `src/services/openstates.py` wrapper was deleted
with the rest of the Streamlit tree in August 2026.

Pure functions, no network — callable from build_site.py, the meeting-prep
brief, and the action pack alike.
"""

from urllib.parse import quote_plus

from src.constants import (
    LOCAL_BODIES_DF,
    LOCAL_OFFICIALS_DF,
    NACO_COUNTY_SEARCH,
    STATE_MUNI_LEAGUES,
    USA_GOV_LOCAL,
)

# Localities we have hand-verified rows for, as "Locality, ST" display strings.
def covered_localities() -> list[str]:
    """Sorted 'Locality, ST' labels that have curated rows. Drives the picker."""
    if LOCAL_OFFICIALS_DF.empty:
        return []
    pairs = (LOCAL_OFFICIALS_DF[["locality", "state"]]
             .drop_duplicates()
             .itertuples(index=False))
    return sorted(f"{loc}, {st}" for loc, st in pairs)


def split_label(label: str) -> tuple[str, str]:
    """'Goochland County, VA' -> ('Goochland County', 'VA'). Tolerates junk."""
    if not label or "," not in label:
        return (label or "").strip(), ""
    loc, _, st = label.rpartition(",")
    return loc.strip(), st.strip()


def curated(locality: str, state: str) -> dict:
    """Verified officials + governing bodies for one locality.

    Returns {"officials": [...], "bodies": [...]} — empty lists when the
    locality isn't in the curated set, which is the normal case. Matching is
    case-insensitive so "tucker county" and "Tucker County" both resolve.
    """
    out = {"officials": [], "bodies": []}
    if not locality or not state:
        return out
    loc_k, st_k = locality.strip().lower(), state.strip().upper()

    if not LOCAL_OFFICIALS_DF.empty:
        m = LOCAL_OFFICIALS_DF[
            (LOCAL_OFFICIALS_DF.locality.str.lower() == loc_k)
            & (LOCAL_OFFICIALS_DF.state.str.upper() == st_k)]
        out["officials"] = m.to_dict("records")

    if not LOCAL_BODIES_DF.empty:
        b = LOCAL_BODIES_DF[
            (LOCAL_BODIES_DF.locality.str.lower() == loc_k)
            & (LOCAL_BODIES_DF.state.str.upper() == st_k)]
        out["bodies"] = b.to_dict("records")

    return out


def build_lookup_links(state: str, locality: str = "") -> list[dict]:
    """Directory links for any locality, curated or not.

    Every entry is {"label", "url", "why"}. These are navigational, not
    assertions about who holds office — which is exactly why this tier can
    cover all 51 jurisdictions without a staleness problem.
    """
    st_k = (state or "").strip().upper()
    links: list[dict] = []

    league = STATE_MUNI_LEAGUES.get(st_k)
    if league:
        name, url = league
        links.append({
            "label": name, "url": url,
            "why": "Statewide association of cities and towns — member "
                   "directories usually list every municipality's clerk and "
                   "council contacts.",
        })
    elif st_k == "HI":
        links.append({
            "label": "Hawaii county governments", "url": USA_GOV_LOCAL,
            "why": "Hawaii has no municipal league — it has no independent "
                   "municipalities. All local authority sits with the four "
                   "county governments.",
        })

    links.append({
        "label": "NACo — county government directory", "url": NACO_COUNTY_SEARCH,
        "why": "Use this when the decision is a county one (boards of "
               "supervisors, county commissions, planning commissions) — which "
               "is where most data-center land-use votes actually happen.",
    })
    links.append({
        "label": "USA.gov — state & local government directory", "url": USA_GOV_LOCAL,
        "why": "Federal front door to official state, county, and municipal "
               "sites. Slower, but authoritative.",
    })

    if locality:
        q = quote_plus(f"{locality} {st_k} city council OR board of supervisors "
                       f"contact site:.gov")
        links.append({
            "label": f"Search official .gov pages for {locality}",
            "url": f"https://duckduckgo.com/?q={q}",
            "why": "Restricted to .gov so you land on the roster page itself "
                   "rather than a data broker's stale copy.",
        })

    return links


def verification_note(records: list[dict]) -> str:
    """One-line provenance footer: how many rows, read from where, and when."""
    if not records:
        return ""
    dates = sorted({r.get("as_of", "") for r in records if r.get("as_of")})
    srcs = sorted({r.get("source", "") for r in records if r.get("source")})
    when = dates[-1] if dates else "unknown date"
    return (f"{len(records)} entries, read from "
            f"{len(srcs)} official government page(s) on {when}.")
