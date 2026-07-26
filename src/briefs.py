"""
Meeting-brief builder — pure text assembly, no Streamlit. Extracted from the
Meeting Prep Generator in toolkit_tab.py so the Start Here wizard and the
toolkit share one implementation. Output is plain text (st.text / download),
so dollar signs are NOT escaped here.
"""

from src.constants import (
    STATE_GRID_PROFILES, STATE_DC_DF, STATE_PUCS_DF, MORATORIUMS_DF,
    OPERATORS_DF, EXECUTIVES_DF, COMPANY_CONCESSIONS,
)
from src.impact_model import estimate_facility_impact

MEETING_ADVICE = {
    "Planning commission hearing": (
        "STRATEGY: Focus on conditions of approval, not outright denial. "
        "Planning commissions can attach binding conditions (CBAs, noise limits, "
        "water caps) to conditional use permits.\n\n"
        "KEY MOVES:\n"
        "  - Request the developer present a water impact study\n"
        "  - Ask for the utility's rate impact analysis\n"
        "  - Demand the CBA be a condition of approval, not a side letter\n"
        "  - Request a noise study at the nearest residential property line\n"
        "  - Ask whether tax abatements are being offered and for how long"
    ),
    "Zoning board meeting": (
        "STRATEGY: Zoning boards control land use. Your leverage is the variance "
        "or rezoning the developer needs. Don't grant it without binding conditions.\n\n"
        "KEY MOVES:\n"
        "  - Challenge whether the proposed use is compatible with the zone\n"
        "  - Request traffic, noise, and environmental impact studies\n"
        "  - Ask about setback distances from residential areas\n"
        "  - Demand a decommissioning bond as a condition\n"
        "  - Request public water usage reporting as a condition"
    ),
    "Town hall / public comment": (
        "STRATEGY: Public comment shapes the political environment. Bring "
        "specific data, not just feelings. Elected officials respond to "
        "organized, fact-based opposition.\n\n"
        "KEY MOVES:\n"
        "  - Lead with the rate impact: 'This will cost every household $X/year'\n"
        "  - Cite specific water consumption numbers\n"
        "  - Reference what other communities have won (Lancaster, Loudoun County)\n"
        "  - Present the Data Dividend model as a positive alternative\n"
        "  - Bring printed copies of your demands for every council member"
    ),
    "Direct negotiation with developer": (
        "STRATEGY: The developer wants your land, water, and grid. You have "
        "leverage until you sign. Never negotiate alone — bring a lawyer and "
        "a technical advisor.\n\n"
        "KEY MOVES:\n"
        "  - Open with the Loudoun County benchmark (38% of budget from DCs)\n"
        "  - Present your Data Dividend calculation as the starting ask\n"
        "  - Demand cost causation: developer pays 100% of grid upgrades\n"
        "  - Require a decommissioning bond ($5K-15K per MW)\n"
        "  - Insist on annual public reporting of water, noise, and emissions"
    ),
    "PUC rate case hearing": (
        "STRATEGY: PUC hearings determine who pays for grid upgrades. Your "
        "goal is to prevent cost-shifting from the data center to ratepayers.\n\n"
        "KEY MOVES:\n"
        "  - Request the utility's load growth forecast with/without the DC\n"
        "  - Ask whether the DC is paying for its own interconnection costs\n"
        "  - Cite New Jersey's Large Load Tariff as a model\n"
        "  - Request that grid upgrade costs be assigned to the cost-causer\n"
        "  - Ask for a residential rate impact analysis before approval"
    ),
}


def build_meeting_brief_data(state, operator, meeting_type, mw):
    """Assemble the meeting brief as structured data.

    Returns a dict with meta fields plus a `sections` list. Each section is
    {"title", "kind", ...} where kind is one of:
      - "kv":          items = [(label, value), ...]
      - "bullets":     items = [str, ...]
      - "numbered":    items = [str, ...]
      - "advice":      text  = raw MEETING_ADVICE string
      - "execs":       items = [{"name","title","focus","linkedin"}, ...]
      - "concessions": pattern = strategy read, items = [{"where","year","what"}, ...]

    Consumed by build_meeting_brief (plain text) and src/pdf_pack.py (PDF)
    so the two renderings can never drift.

    `operator` should be an OPERATORS_DF operator name, or
    "Unknown / not listed" to skip the operator profile section.
    """
    imp = estimate_facility_impact(mw, state)

    _st_row = STATE_DC_DF[STATE_DC_DF["state"] == state]
    _st_twh = _st_row.iloc[0]["twh_year"] if not _st_row.empty else 0
    _st_count = int(_st_row.iloc[0]["dc_count"]) if not _st_row.empty else 0
    _st_abbrev_row = STATE_PUCS_DF[STATE_PUCS_DF["state"] == state]
    _abbrev = _st_abbrev_row.iloc[0]["abbrev"] if not _st_abbrev_row.empty else ""
    _puc_name = _st_abbrev_row.iloc[0]["name"] if not _st_abbrev_row.empty else "N/A"
    _puc_web = _st_abbrev_row.iloc[0]["website"] if not _st_abbrev_row.empty else ""
    _puc_complaint = _st_abbrev_row.iloc[0]["complaint"] if not _st_abbrev_row.empty else ""

    _moras = MORATORIUMS_DF[MORATORIUMS_DF["state"] == _abbrev]
    _mora_text = ""
    if not _moras.empty:
        enacted = (_moras["status"] == "Enacted").sum()
        proposed = (_moras["status"] == "Proposed").sum()
        parts = []
        if enacted:
            parts.append(f"{enacted} enacted")
        if proposed:
            parts.append(f"{proposed} proposed")
        _mora_text = ", ".join(parts)

    sections = []

    _glance = [
        ("Existing DC facilities", f"{_st_count}"),
        ("Existing DC load", f"{_st_twh:.1f} TWh/year"),
        ("Grid carbon intensity", f"{imp['gco2']} gCO2/kWh"),
        ("Residential electricity rate", f"${imp['rate']:.3f}/kWh"),
        ("Water stress", f"{imp['water_stress']}"),
        ("PUC", _puc_name),
        ("PUC website", _puc_web),
        ("PUC complaint portal", _puc_complaint),
    ]
    if _mora_text:
        _glance.append(("Moratorium activity", _mora_text))
    sections.append(
        {"title": "YOUR STATE AT A GLANCE", "kind": "kv", "items": _glance})

    sections.append({
        "title": "FACILITY IMPACT ESTIMATES", "kind": "kv", "items": [
            ("Annual electricity", f"{imp['annual_twh']:.1f} TWh"),
            ("Annual carbon", f"{imp['annual_co2_t']:,.0f} tCO2e"),
            ("Annual water (evaporative)",
             f"{imp['annual_water_mgal']:,.0f}M gallons"),
            ("Homes equivalent", f"{imp['homes_equiv']:,.0f}"),
            ("Estimated investment", f"${imp['investment_musd']:.0f}M"),
        ]})

    if operator != "Unknown / not listed":
        _op_rows = OPERATORS_DF[OPERATORS_DF["operator"] == operator]
        if not _op_rows.empty:
            _op = _op_rows.iloc[0]
            sections.append({
                "title": f"OPERATOR PROFILE: {operator}", "kind": "kv",
                "items": [
                    ("Tier", f"{_op.get('tier', 'N/A')}"),
                    ("Owner", f"{_op.get('owner', 'N/A')}"),
                    ("Business model", f"{_op.get('model', 'N/A')}"),
                ]})
        _exec_rows = EXECUTIVES_DF[
            EXECUTIVES_DF["company"].str.contains(
                operator, case=False, na=False, regex=False)
        ]
        if not _exec_rows.empty:
            sections.append({
                "title": "KEY EXECUTIVES & HOW TO REACH THEM", "kind": "execs",
                "items": [{"name": ex["name"], "title": ex["title"],
                           "focus": ex.get("focus", ""),
                           "linkedin": ex.get("linkedin", "")}
                          for _, ex in _exec_rows.head(5).iterrows()]})

        _cc = COMPANY_CONCESSIONS.get(operator)
        if _cc:
            sections.append({
                "title": f"TRACK RECORD — WHAT {operator.upper()} "
                         "HAS CONCEDED ELSEWHERE",
                "kind": "concessions",
                "pattern": _cc["pattern"],
                "items": _cc["concessions"]})

    sections.append({
        "title": f"MEETING STRATEGY: {meeting_type.upper()}", "kind": "advice",
        "text": MEETING_ADVICE.get(meeting_type, "")})

    sections.append({
        "title": "CBA TARGETS (bring these to the table)", "kind": "kv",
        "items": [
            ("Data dividend",
             f"${imp['data_dividend_usd']/1e6:.1f}M/year (2% of investment)"),
            ("Noise limit", "45 dBA at residential property line"),
            ("Water cap", f"{imp['annual_water_mgal'] * 0.5:,.0f}M gallons/year"),
            ("Grid upgrades", "Developer pays 100%"),
            ("Decommissioning bond", f"${mw * 10_000 / 1e6:.1f}M"),
            ("Local hiring", "80%+ construction labor, prevailing wage"),
            ("Property tax lock",
             f"No abatement below ${imp['investment_musd'] * 0.02:.0f}M/year"),
        ]})

    sections.append({
        "title": "QUESTIONS TO ASK", "kind": "numbered", "items": [
            "How many MW will this facility draw at full build-out?",
            "Who pays for grid upgrades (substation, transmission)?",
            "What is the projected impact on residential electricity rates?",
            "How many gallons/day will cooling consume? From which source?",
            "What specific tax incentives are being offered, and for how long?",
            "How many permanent local jobs (not construction)?",
            "What is the projected noise level at the nearest home?",
            "Is there a binding CBA? What are the annual payments?",
            "What happens if the facility closes — is there a decommissioning bond?",
            "Will water, noise, and emissions data be publicly reported?",
        ]})

    return {
        "meeting_type": meeting_type,
        "state": state,
        "operator": operator,
        "mw": mw,
        "sections": sections,
    }


def build_meeting_brief(state, operator, meeting_type, mw):
    """Render the meeting brief as plain text (st.text / .txt download)."""
    data = build_meeting_brief_data(state, operator, meeting_type, mw)

    brief = (
        f"MEETING PREP BRIEF\n"
        f"{'='*60}\n"
        f"Generated by AI GridWatch\n\n"
        f"MEETING: {data['meeting_type']}\n"
        f"STATE: {data['state']}\n"
        f"OPERATOR: {data['operator']}\n"
        f"FACILITY: {data['mw']} MW proposed\n"
    )
    for sec in data["sections"]:
        brief += f"\n{'─'*60}\n{sec['title']}\n{'─'*60}\n"
        if sec["kind"] == "kv":
            for label, value in sec["items"]:
                brief += f"  {label}: {value}\n"
        elif sec["kind"] == "bullets":
            for item in sec["items"]:
                brief += f"  - {item}\n"
        elif sec["kind"] == "numbered":
            for i, item in enumerate(sec["items"], 1):
                brief += f"  {i}. {item}\n"
        elif sec["kind"] == "advice":
            brief += f"{sec['text']}\n"
        elif sec["kind"] == "execs":
            for ex in sec["items"]:
                brief += f"  - {ex['name']}, {ex['title']}\n"
                if ex["focus"]:
                    brief += f"      Focus: {ex['focus']}\n"
                if ex["linkedin"]:
                    brief += f"      LinkedIn: {ex['linkedin']}\n"
        elif sec["kind"] == "concessions":
            brief += f"{sec['pattern']}\n\n"
            for c in sec["items"]:
                brief += f"  - {c['where']} ({c['year']}): {c['what']}\n"
    return brief
