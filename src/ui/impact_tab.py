"""
Local Impact Calculator — enter your state and a proposed facility size
to see estimated grid, water, carbon, rate, and tax impacts.
"""

import streamlit as st
import pandas as pd
import altair as alt
from src.constants import (
    STATE_GRID_PROFILES, STATE_DC_DF, MORATORIUMS_DF,
    STATE_PUCS_DF, DC_SITES_DF,
)
from src.helpers import render_freshness, src_link
from src.impact_model import estimate_facility_impact
from src.ui import share

# Keys the calculator carries in a shareable link.
COOLING_OPTIONS = ["Evaporative (water-cooled)", "Dry cooling (air-cooled)",
                   "Hybrid"]

# Guards keep a mangled or stale link from crashing the tab for the recipient.
SHARE_SPEC = {
    "state": ("impact_state", "str", lambda: STATE_GRID_PROFILES.keys()),
    "mw": ("impact_mw", "int", (50, 1000)),
    "cooling": ("impact_cooling", "str", COOLING_OPTIONS),
}


def render_impact_tab():
    share.restore(st, SHARE_SPEC, "impact")
    st.subheader("📍 Local Impact Calculator")
    st.caption(
        "Estimate what a proposed data center means for your community. "
        "Enter the facility size and your state to see projected energy, "
        "water, carbon, rate, and tax impacts — with context from real data."
    )

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### Your proposed facility")

    c1, c2, c3 = st.columns(3)
    with c1:
        _sidebar_state = st.session_state.get("my_state", "All states")
        _states = sorted(STATE_GRID_PROFILES.keys())
        _default_idx = _states.index(_sidebar_state) if _sidebar_state in _states else 0
        state = st.selectbox(
            "State", _states, index=_default_idx, key="impact_state")
    with c2:
        facility_mw = st.slider(
            "Facility size (MW)", 50, 1000, 200, 50, key="impact_mw",
            help="A small campus is 50-100 MW; mid-size 200-500 MW; hyperscale 500+ MW.")
    with c3:
        cooling = st.selectbox(
            "Cooling type",
            COOLING_OPTIONS,
            key="impact_cooling",
            help="Evaporative uses ~2 gal/kWh; dry uses ~0.02 gal/kWh; hybrid ~0.8 gal/kWh.")
    st.markdown('</div>', unsafe_allow_html=True)

    imp = estimate_facility_impact(facility_mw, state, cooling)
    res_rate = imp["rate"]
    gco2 = imp["gco2"]
    water_stress = imp["water_stress"]
    pue = imp["pue"]
    annual_twh = imp["annual_twh"]
    annual_water_mgal = imp["annual_water_mgal"]
    annual_co2_t = imp["annual_co2_t"]
    homes_equiv = imp["homes_equiv"]
    annual_dc_spend = imp["annual_dc_spend_busd"]
    rate_ratio = imp["rate_ratio"]

    # ── Impact dashboard ───────────────────────────────────────────────── #
    st.markdown("### Projected annual impact")
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    r1c1.metric(
        "Electricity consumption",
        f"{annual_twh:.1f} TWh",
        f"{facility_mw} MW × {pue:.2f} PUE × 8,760 hrs")
    r1c2.metric(
        "Carbon emissions",
        f"{annual_co2_t:,.0f} tCO2e",
        f"at {gco2} gCO2/kWh grid avg")
    r1c3.metric(
        "Water consumption",
        f"{annual_water_mgal:,.0f}M gal",
        f"{'High' if water_stress == 'high' else 'Medium' if water_stress == 'medium' else 'Low'} stress region")
    r1c4.metric(
        "Household equivalent",
        f"{homes_equiv:,.0f}",
        "homes' electricity")

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    r2c1.metric(
        "Est. electricity spend",
        f"${annual_dc_spend:.1f}B/yr",
        f"at ~$0.050/kWh industrial rate")
    r2c2.metric(
        "Rate discount vs. you",
        f"{rate_ratio:.1f}x",
        f"You pay ${res_rate:.3f} — they pay ~$0.050")
    r2c3.metric(
        "Water stress",
        water_stress.capitalize(),
        "Based on state water availability")
    r2c4.metric(
        "Grid intensity",
        f"{gco2} gCO2/kWh",
        "Dirtier" if gco2 > 350 else "Cleaner" if gco2 < 250 else "Average")
    st.caption(
        f"Water draw scales with state water stress "
        f"(×0.85 low, ×1.0 medium, ×1.4 high) — hot/arid sites lose more "
        f"water per kWh to evaporation than cool/humid ones "
        f"({src_link('lei_masanet_2022')}; state ratings: "
        f"{src_link('wri_aqueduct')})."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Right under the headline numbers — that is the screenshot people would
    # otherwise take, and a link beats a screenshot because the recipient can
    # change the MW and see it move.
    share.render(
        st, SHARE_SPEC,
        caption=("Reopens this calculator with the same state, size and "
                 "cooling type. Better than a screenshot — whoever you send "
                 "it to can change the numbers and watch them move."))

    # ── Context: how this compares ─────────────────────────────────────── #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### How this compares")

    _state_row = STATE_DC_DF[STATE_DC_DF["state"] == state]
    if not _state_row.empty:
        _existing = _state_row.iloc[0]
        _existing_twh = _existing.get("twh_year", 0) or 0
        _existing_count = int(_existing.get("dc_count", 0) or 0)
        _pct_increase = (annual_twh / _existing_twh * 100) if _existing_twh > 0 else None

        cc1, cc2, cc3 = st.columns(3)
        cc1.metric(
            f"Existing DC load in {state}",
            f"{_existing_twh:.1f} TWh/yr",
            f"{_existing_count} tracked facilities")
        if _pct_increase is not None:
            cc2.metric(
                "This facility would add",
                f"+{_pct_increase:.0f}%",
                f"to {state}'s DC electricity load")
        else:
            cc2.metric("This facility would add", f"{annual_twh:.1f} TWh", "first major facility")
        cc3.metric(
            "Olympic swimming pools",
            f"{annual_water_mgal * 1e6 / 660_000:,.0f}",
            "of water per year")

    _state_abbrev = STATE_PUCS_DF.loc[
        STATE_PUCS_DF["state"] == state, "abbrev"
    ]
    _abbrev = _state_abbrev.iloc[0] if not _state_abbrev.empty else ""

    _local_moras = MORATORIUMS_DF[MORATORIUMS_DF["state"] == _abbrev]
    _local_sites = DC_SITES_DF[DC_SITES_DF["state"] == _abbrev] if "state" in DC_SITES_DF.columns else pd.DataFrame()

    if not _local_moras.empty:
        enacted = (_local_moras["effective_status"] == "Enacted").sum()
        proposed = (_local_moras["effective_status"] == "Proposed").sum()
        parts = []
        if enacted:
            parts.append(f"**{enacted} enacted**")
        if proposed:
            parts.append(f"{proposed} proposed")
        st.warning(
            f"**Moratorium activity in {state}:** {', '.join(parts)}. "
            f"Communities in your state are actively pushing back on data center development."
        )
    if not _local_sites.empty:
        operators = _local_sites["operator"].value_counts().head(5)
        op_list = ", ".join(f"{op} ({n})" for op, n in operators.items())
        st.info(f"**Existing operators in {state}:** {op_list}")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Rate impact estimator ──────────────────────────────────────────── #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### Potential rate impact on your bill")
    st.caption(
        "When a large load connects, utilities may file rate cases to recover "
        "grid upgrade costs (new transmission, substation upgrades, peaker plants). "
        "These costs are spread across all ratepayers."
    )

    grid_upgrade_per_mw = st.slider(
        "Estimated grid upgrade cost ($/MW)",
        500_000, 5_000_000, 2_000_000, 250_000,
        format="$%d",
        help="Typical range: \\$500K-\\$5M per MW depending on existing grid capacity. "
             "Congested areas (NoVA, NYC) are at the high end.")

    total_upgrade = facility_mw * grid_upgrade_per_mw
    _state_homes = 5_000_000
    annual_cost_per_home = total_upgrade / _state_homes / 20

    rc1, rc2, rc3 = st.columns(3)
    rc1.metric(
        "Total grid upgrade cost",
        f"${total_upgrade / 1e6:,.0f}M",
        f"{facility_mw} MW × ${grid_upgrade_per_mw/1e6:.1f}M/MW")
    rc2.metric(
        "Cost spread per household",
        f"${annual_cost_per_home:.0f}/yr",
        f"amortized over 20 years, ~5M homes")
    rc3.metric(
        "Monthly bill increase",
        f"${annual_cost_per_home/12:.2f}",
        "estimated per household")

    st.caption(
        "This is a simplified model. Actual rate impacts depend on utility cost "
        "recovery filings, PUC rulings, existing grid headroom, and whether the "
        "developer pays for interconnection costs directly. Your PUC decides."
    )
    # The residential rate driving these figures is the stalest input in the
    # app, and it is the one someone reads out at a hearing. Say so here
    # rather than in a methodology page nobody opens.
    render_freshness(st, "STATE_GRID_PROFILES")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── What to demand ─────────────────────────────────────────────────── #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### What to demand")

    _data_dividend = imp["data_dividend_usd"]
    _cba_pct = 2.0

    st.markdown(
        f"Based on a **{facility_mw} MW** facility with an estimated investment "
        f"of **\\${facility_mw * 2:.0f}M** (at ~\\$2M/MW):"
    )

    d1, d2, d3 = st.columns(3)
    d1.metric(
        "Data dividend target",
        f"${_data_dividend / 1e6:.1f}M/yr",
        f"{_cba_pct}% of estimated investment")
    d2.metric(
        "Noise limit",
        "45 dBA",
        "at residential property line")
    d3.metric(
        "Water cap",
        f"{annual_water_mgal * 0.5:,.0f}M gal",
        "50% of evaporative baseline")

    demands = [
        f"**Community benefit payment:** \\${_data_dividend/1e6:.1f}M/year ({_cba_pct}% of investment)",
        f"**Rate protection clause:** Developer pays grid upgrade costs, not ratepayers",
        f"**Noise limit:** 45 dBA at nearest residential property line",
        f"**Water cap:** {annual_water_mgal * 0.5:,.0f}M gallons/year with dry-cooling mandate",
        "**Decommissioning bond:** Funded escrow for site restoration",
        "**Local hiring:** 80%+ local labor for construction, prevailing wage",
        f"**Property tax lock:** No abatement below \\${facility_mw * 2 * 0.02:.0f}M/year",
    ]
    for d in demands:
        st.markdown(f"- {d}")

    st.info(
        "**Take this to your town hall.** Use the **Negotiation toolkit** tab "
        "for model CBA clauses, and the **States & officials** tab to find "
        "your PUC's complaint portal."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Export ─────────────────────────────────────────────────────────── #
    _export = (
        f"LOCAL IMPACT ESTIMATE — {state}\n"
        f"{'='*50}\n"
        f"Facility: {facility_mw} MW, {cooling}\n"
        f"PUE: {pue:.2f}\n\n"
        f"ANNUAL PROJECTIONS\n"
        f"  Electricity: {annual_twh:.1f} TWh ({homes_equiv:,.0f} homes equivalent)\n"
        f"  Carbon: {annual_co2_t:,.0f} tCO2e (grid avg {gco2} gCO2/kWh)\n"
        f"  Water: {annual_water_mgal:,.0f}M gallons (stress: {water_stress})\n"
        f"  Est. DC spend: ${annual_dc_spend:.1f}B/yr at $0.050/kWh\n"
        f"  Rate discount: {rate_ratio:.1f}x vs residential ${res_rate:.3f}/kWh\n\n"
        f"GRID UPGRADE COST (at ${grid_upgrade_per_mw/1e6:.1f}M/MW)\n"
        f"  Total: ${total_upgrade/1e6:,.0f}M\n"
        f"  Per household: ${annual_cost_per_home:.0f}/year\n\n"
        f"CBA TARGETS\n"
        f"  Data dividend: ${_data_dividend/1e6:.1f}M/year\n"
        f"  Noise: 45 dBA at property line\n"
        f"  Water cap: {annual_water_mgal*0.5:,.0f}M gal/yr\n\n"
        f"Generated by AI GridWatch — gridwatch.ai\n"
    )
    st.download_button(
        "📥 Download impact report (text)",
        _export, f"impact_estimate_{state.replace(' ', '_')}.txt", "text/plain")
