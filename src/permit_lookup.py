"""
Permit paper trail — where to read the public record behind a tracked project.

Same three-tier logic as `local_officials.py`, applied to documents instead of
people: use the specific thing when we have it, fall back to something that
always resolves, and never let the fallback masquerade as the specific thing.

  1. What we already hold — dated `permit` events on the project row itself
     (PA DEP rows arrive with permit numbers and eFACTS auth IDs attached).
  2. Deterministic registers — the state agency's permit database, the PUC's
     docket search, the grid operator's interconnection queue, EPA ECHO.
     Full 51-state coverage, nothing to go stale except a URL.
  3. Search links — a pre-built query when no register exists. Marked as a
     search, because a search result is not a record.

Pure functions, no Streamlit and no network I/O: callable from the site
builder, the wizard, and the PDF pack alike.

Nothing here asserts that a permit exists. `sections()` returns places to
look; only tier 1 returns filings we have actually seen.
"""

from urllib.parse import quote_plus

from src.constants import (
    FERC_ELIBRARY,
    NATIONAL_PERMIT_TOOLS,
    PERMIT_KINDS,
    RTO_QUEUES,
    STATE_PERMIT_PORTALS,
    STATE_PUCS_DF,
    STATE_RTO,
    has_value,
)
from src.local_officials import curated

_SEARCH = "https://duckduckgo.com/?q="


def _bare(locality):
    """'Hazle Township (Luzerne County)' -> 'Hazle Township'.

    Several rows carry the county in parentheses to disambiguate. That is
    useful on a page and actively harmful inside a search query.
    """
    return str(locality or "").split("(")[0].strip()


def _search_link(*terms):
    """A pre-built web search. Never rots, and never pretends to be a record."""
    return _SEARCH + quote_plus(" ".join(t for t in terms if t))


def state_portal(state):
    """The permit register entry for a 2-letter abbrev, or None."""
    return STATE_PERMIT_PORTALS.get(str(state or "").strip().upper())


def puc(state):
    """{'name', 'website'} for the state PUC, or None."""
    st = str(state or "").strip().upper()
    row = STATE_PUCS_DF[STATE_PUCS_DF["abbrev"] == st]
    if row.empty:
        return None
    r = row.iloc[0]
    return {"name": r["name"], "website": r["website"]}


def grid_operators(state):
    """[(label, url)] for the market(s) a state sits in — a routing hint.

    Several states are split between markets and a few sit outside every
    organised market, so an empty list is a real answer: there is no queue to
    read, and the utility's own IRP plus the PUC docket are the record.
    """
    keys = STATE_RTO.get(str(state or "").strip().upper(), [])
    return [RTO_QUEUES[k] for k in keys if k in RTO_QUEUES]


def known_permits(project):
    """Tier 1 — dated `permit` events already on the project row.

    Returns [{date, summary, source}] newest first. These are filings we have
    a source for, which is a different kind of claim from everything below.
    """
    out = []
    for ev in (project or {}).get("events") or []:
        if str(ev.get("kind", "")).lower() != "permit":
            continue
        out.append({"date": ev.get("date"), "summary": ev.get("summary", ""),
                    "source": ev.get("source")})
    return sorted(out, key=lambda e: e.get("date") or "", reverse=True)


def _env_links(state, locality, name):
    portal = state_portal(state)
    links = []
    if not portal:
        return links
    links.append({"label": portal["agency"], "url": portal["agency_url"],
                  "why": "The program page: which permits this state requires, "
                         "and the office that issues them.",
                  "kind": "register"})
    if portal.get("register"):
        links.append({"label": portal["register_label"],
                      "url": portal["register"],
                      "why": "Searchable public filings — search the operator, "
                             "the shell LLC on the deed, and the address.",
                      "kind": "register"})
    else:
        links.append({
            "label": f"Search {portal['agency']} for this project",
            "url": _search_link(portal["agency"], name, _bare(locality), state,
                                "air permit data center"),
            "why": "This state publishes no searchable permit database, so a "
                   "written records request to the agency is the reliable "
                   "route. Use this search only to find the right office.",
            "kind": "search"})
    return links


def _local_links(state, locality):
    """County/town filings — curated agenda page when we have one, else search."""
    links = []
    if not locality:
        return links
    for body in curated(locality, state).get("bodies", []):
        url = body.get("agenda_url")
        if has_value(url):
            links.append({
                "label": f"{body.get('body', 'Governing body')} agendas & packets",
                "url": str(url),
                "why": "The meeting packet carries the staff report, site plan "
                       "and conditions — verified page for this locality.",
                "kind": "register"})
    links.append({
        "label": f"Search {locality} planning filings",
        "url": _search_link(_bare(locality), state, "planning commission agenda "
                                             "rezoning site plan data center"),
        "why": "Planning departments post application files under many "
               "different names. Find the department, then ask the clerk for "
               "the application number — that number unlocks everything else.",
        "kind": "search"})
    links.append({
        "label": f"Search {locality} property records / GIS",
        "url": _search_link(_bare(locality), state, "county GIS parcel viewer "
                                             "property records search"),
        "why": "The parcel record names the buying LLC and the sale date, "
               "which is what ties an anonymous filing to an operator.",
        "kind": "search"})
    return links


def _utility_links(state, locality, name):
    links = []
    for label, url in grid_operators(state):
        links.append({
            "label": f"{label} — interconnection queue",
            "url": url,
            "why": "Requested megawatts, queue position and target in-service "
                   "date. The MW here is the real number; the one at the town "
                   "meeting is often phase one.",
            "kind": "register"})
    if not grid_operators(state):
        links.append({
            "label": "No organised market covers this state",
            "url": FERC_ELIBRARY,
            "why": "There is no public queue to read. The record is the "
                   "utility's integrated resource plan and its filings at the "
                   "PUC — plus FERC eLibrary for anything federally docketed.",
            "kind": "note"})
    p = puc(state)
    if p:
        links.append({
            "label": f"{p['name']} — docket search",
            "url": p["website"],
            "why": "Special contracts, large-load tariffs and rate cases are "
                   "docketed here. Testimony and exhibits are public, and are "
                   "usually more candid than the press release.",
            "kind": "register"})
    links.append({
        "label": "FERC eLibrary",
        "url": FERC_ELIBRARY,
        "why": "Federal filings: transmission agreements, interconnection "
               "service agreements, and co-location disputes.",
        "kind": "register"})
    links.append({
        "label": "Search the serving utility for a will-serve letter",
        "url": _search_link(_bare(locality), state, name,
                            "utility will serve letter large load "
                            "data center interconnection"),
        "why": "The will-serve or load-service letter is the utility's own "
               "written commitment. Ask the utility and the PUC for it by "
               "name — it is frequently the first document to exist.",
        "kind": "search"})
    return links


def _national_links(project):
    links = []
    for t in NATIONAL_PERMIT_TOOLS:
        links.append({**t, "kind": "register"})
    lat, lon = (project or {}).get("lat"), (project or {}).get("lon")
    if has_value(lat) and has_value(lon):
        links[0] = dict(links[0])
        links[0]["why"] += (f" This project's locality centres on "
                            f"{float(lat):.3f}, {float(lon):.3f} — search that "
                            f"point with a 5-mile radius.")
    return links


def sections(project):
    """Grouped places to read the record for one project row.

    [{'tier', 'why', 'links': [{'label','url','why','kind'}]}] — `kind` is
    'register' (a public database), 'search' (a query, not a record) or
    'note'. Callers should render the distinction; conflating them is how a
    resident ends up citing a search result at a hearing.
    """
    p = project or {}
    state = str(p.get("state") or "")
    locality = str(p.get("locality") or "")
    name = str(p.get("name") or "")
    out = []

    env = _env_links(state, locality, name)
    if env:
        out.append({"tier": "State environmental permits",
                    "why": "Backup generators, water withdrawal and stormwater "
                           "are permitted by the state, usually earlier and in "
                           "more detail than anything filed locally.",
                    "links": env})

    loc = _local_links(state, locality)
    if loc:
        out.append({"tier": "County & town filings",
                    "why": "The rezoning application, site plan, traffic and "
                           "noise studies, staff report and every revision.",
                    "links": loc})

    out.append({"tier": "Utility & grid records",
                "why": "The electricity request is filed with the grid "
                       "operator and the utility long before the town hears "
                       "about it — and states the real load.",
                "links": _utility_links(state, locality, name)})

    out.append({"tier": "Federal databases",
                "why": "Works anywhere, and covers the operator's record at "
                       "its other sites.",
                "links": _national_links(p)})
    return out


def document_checklist():
    """The documents worth requesting, in the order they tend to exist."""
    return list(PERMIT_KINDS)


def provenance_note():
    """One line for the footer, wherever this gets rendered."""
    return ("These are places to look, not evidence that anything has been "
            "filed. Links were checked on 2026-08-21; search links are "
            "queries, not records.")
