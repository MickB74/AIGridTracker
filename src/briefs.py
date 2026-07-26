"""
Meeting-brief builder — pure text assembly, no Streamlit. Extracted from the
Meeting Prep Generator in toolkit_tab.py so the Start Here wizard and the
toolkit share one implementation. Output is plain text (st.text / download),
so dollar signs are NOT escaped here.
"""

from src.constants import (
    STATE_GRID_PROFILES, STATE_DC_DF, STATE_PUCS_DF, MORATORIUMS_DF,
    OPERATORS_DF, EXECUTIVES_DF,
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


def build_meeting_brief(state, operator, meeting_type, mw):
    """Assemble the one-page meeting brief as plain text.

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
        _mora_text = f"Moratorium activity: {', '.join(parts)}"

    _op_info = ""
    _op_execs = ""
    if operator != "Unknown / not listed":
        _op_rows = OPERATORS_DF[OPERATORS_DF["operator"] == operator]
        if not _op_rows.empty:
            _op = _op_rows.iloc[0]
            _op_info = (
                f"  Tier: {_op.get('tier', 'N/A')}\n"
                f"  Owner: {_op.get('owner', 'N/A')}\n"
                f"  Business model: {_op.get('model', 'N/A')}\n"
            )
        _exec_rows = EXECUTIVES_DF[
            EXECUTIVES_DF["company"].str.contains(operator, case=False, na=False)
        ]
        if not _exec_rows.empty:
            _op_execs = "KEY EXECUTIVES\n"
            for _, ex in _exec_rows.head(5).iterrows():
                _op_execs += f"  - {ex['name']}, {ex['title']}\n"

    _advice = MEETING_ADVICE.get(meeting_type, "")

    brief = (
        f"MEETING PREP BRIEF\n"
        f"{'='*60}\n"
        f"Generated by AI GridWatch\n\n"
        f"MEETING: {meeting_type}\n"
        f"STATE: {state}\n"
        f"OPERATOR: {operator}\n"
        f"FACILITY: {mw} MW proposed\n\n"
        f"{'─'*60}\n"
        f"YOUR STATE AT A GLANCE\n"
        f"{'─'*60}\n"
        f"  Existing DC facilities: {_st_count}\n"
        f"  Existing DC load: {_st_twh:.1f} TWh/year\n"
        f"  Grid carbon intensity: {imp['gco2']} gCO2/kWh\n"
        f"  Residential electricity rate: ${imp['rate']:.3f}/kWh\n"
        f"  Water stress: {imp['water_stress']}\n"
        f"  PUC: {_puc_name}\n"
        f"  PUC website: {_puc_web}\n"
        f"  PUC complaint portal: {_puc_complaint}\n"
    )
    if _mora_text:
        brief += f"  {_mora_text}\n"

    brief += (
        f"\n{'─'*60}\n"
        f"FACILITY IMPACT ESTIMATES\n"
        f"{'─'*60}\n"
        f"  Annual electricity: {imp['annual_twh']:.1f} TWh\n"
        f"  Annual carbon: {imp['annual_co2_t']:,.0f} tCO2e\n"
        f"  Annual water (evaporative): {imp['annual_water_mgal']:,.0f}M gallons\n"
        f"  Homes equivalent: {imp['homes_equiv']:,.0f}\n"
        f"  Estimated investment: ${imp['investment_musd']:.0f}M\n"
    )

    if _op_info:
        brief += (
            f"\n{'─'*60}\n"
            f"OPERATOR PROFILE: {operator}\n"
            f"{'─'*60}\n"
            f"{_op_info}"
        )
    if _op_execs:
        brief += f"\n{_op_execs}"

    brief += (
        f"\n{'─'*60}\n"
        f"{_advice}\n"
        f"\n{'─'*60}\n"
        f"CBA TARGETS (bring these to the table)\n"
        f"{'─'*60}\n"
        f"  Data dividend: ${imp['data_dividend_usd']/1e6:.1f}M/year (2% of investment)\n"
        f"  Noise limit: 45 dBA at residential property line\n"
        f"  Water cap: {imp['annual_water_mgal'] * 0.5:,.0f}M gallons/year\n"
        f"  Grid upgrades: Developer pays 100%\n"
        f"  Decommissioning bond: ${mw * 10_000 / 1e6:.1f}M\n"
        f"  Local hiring: 80%+ construction labor, prevailing wage\n"
        f"  Property tax lock: No abatement below ${imp['investment_musd'] * 0.02:.0f}M/year\n"
        f"\n{'─'*60}\n"
        f"QUESTIONS TO ASK\n"
        f"{'─'*60}\n"
        f"  1. How many MW will this facility draw at full build-out?\n"
        f"  2. Who pays for grid upgrades (substation, transmission)?\n"
        f"  3. What is the projected impact on residential electricity rates?\n"
        f"  4. How many gallons/day will cooling consume? From which source?\n"
        f"  5. What specific tax incentives are being offered, and for how long?\n"
        f"  6. How many permanent local jobs (not construction)?\n"
        f"  7. What is the projected noise level at the nearest home?\n"
        f"  8. Is there a binding CBA? What are the annual payments?\n"
        f"  9. What happens if the facility closes — is there a decommissioning bond?\n"
        f"  10. Will water, noise, and emissions data be publicly reported?\n"
    )
    return brief
