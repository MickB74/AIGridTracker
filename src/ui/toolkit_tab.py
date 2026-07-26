"""
CBA Toolkit tab — actionable negotiation tools for communities facing
data center development. Calculators, model clauses, and real-world
examples to help towns extract maximum value.
"""

import urllib.parse
import streamlit as st
import pandas as pd
import altair as alt
from src.constants import (
    OPERATORS_DF, STATE_GRID_PROFILES,
    FARMLAND_CROPLAND_USD_ACRE_2024, US_CROPLAND_USD_ACRE_2024,
)
from src.briefs import build_meeting_brief
from src.helpers import src_link
from src.services.tracking import log_event


# ── Real-world CBA examples database ─────────────────────────────────────── #

_CBA_EXAMPLES = [
    {
        "community": "Cedar Rapids, IA",
        "operator": "Google / QTS",
        "year": 2023,
        "mw": 200,
        "investment_b": 2.4,
        "what_they_got": [
            "Google: \\$400K/yr for 15 years (\\$6M total community betterment fund)",
            "QTS: \\$18M over 18 years (\\$1M/yr) in community payments",
            "Local hiring commitments for construction",
            "Property tax abatement tied to job creation benchmarks",
        ],
        "lesson": "Tied incentives to measurable deliverables with long time horizons. "
                  "Per-year community payments create accountability.",
    },
    {
        "community": "Lancaster, PA",
        "operator": "Arcadian Infracom",
        "year": 2024,
        "mw": 160,
        "investment_b": 1.8,
        "what_they_got": [
            "\\$20.25M total community benefit package",
            "\\$10M letter of credit for clean energy compliance",
            "20,000 gallon/day hard cap on water usage",
            "Annual community benefit payments tied to phases",
        ],
        "lesson": "The \\$10M letter of credit for clean energy is a powerful innovation — "
                  "the developer loses real money if they don't meet sustainability targets.",
    },
    {
        "community": "Loudoun County, VA",
        "operator": "Multiple hyperscalers",
        "year": 2024,
        "mw": 3000,
        "investment_b": 50.0,
        "what_they_got": [
            "Data center equipment taxes: \\$330M in FY2020 alone",
            "DCs fund 38% of general fund (from just 4% of parcels)",
            "Over \\$100M/yr in new revenue; property tax rate dropped "
            "from \\$1.145 to \\$0.805 per \\$100 assessed value",
            "Strict noise ordinance (38 dBA at residential property lines)",
            "1,000-ft setback from residential zoning",
        ],
        "lesson": "The gold standard — massive tax base offsets residential burden. "
                  "But it took decades of negotiation and pushback to get the noise "
                  "and setback protections.",
    },
    {
        "community": "Mesa, AZ",
        "operator": "Meta / Google / EdgeCore",
        "year": 2023,
        "mw": 300,
        "investment_b": 3.0,
        "what_they_got": [
            "Mandatory closed-loop / dry cooling (no evaporative)",
            "Banned open-loop cooling in new data center permits",
            "Water consumption transparency requirements",
        ],
        "lesson": "Desert communities can and should demand zero-water cooling. "
                  "Operators accept higher PUE rather than lose the site.",
    },
    {
        "community": "New Jersey (statewide)",
        "operator": "Equinix / Digital Realty / all",
        "year": 2025,
        "mw": 500,
        "investment_b": 10.0,
        "what_they_got": [
            "Large Load Tariff: any load >= 50 MW pays for its own substation upgrades",
            "Ratepayers protected from subsidizing industrial grid connections",
            "Signed into law (P.L. 2025 c. 98)",
        ],
        "lesson": "State-level legislation can protect all communities at once. "
                  "Push for large-load tariffs at the PUC level.",
    },
    {
        "community": "Chesterfield County, VA",
        "operator": "QTS / Microsoft",
        "year": 2024,
        "mw": 250,
        "investment_b": 2.0,
        "what_they_got": [
            "Negotiated proffers: road improvements, broadband expansion",
            "Committed to local workforce training pipeline",
            "Proffers tied to each phase of development, not just initial approval",
        ],
        "lesson": "Phase-tied proffers prevent developers from building phase 1, "
                  "collecting the incentive, and abandoning later phases.",
    },
]

# ── Model CBA clauses ────────────────────────────────────────────────────── #

_MODEL_CLAUSES = {
    "Landowner bloc: no-individual-deals pact": {
        "icon": "🤝",
        "clause": (
            "The undersigned landowners agree to negotiate the sale or lease of their "
            "parcels to [Developer / any data-center developer] solely as a group, "
            "through [designated representative or attorney]. No signatory shall enter "
            "into any individual sale, option, or letter of intent on terms below those "
            "secured for the group. Net proceeds shall be shared pro rata by contributed "
            "acreage. If any signatory is offered superior terms, those terms shall be "
            "extended to all signatories (most-favored-nation). A signatory who sells "
            "individually in breach shall [forfeit $[X] / grant the group a right of "
            "first refusal]. This agreement expires on [date] if no group transaction "
            "has closed."
        ),
        "why": (
            "Unlike the other entries here, this is a landowner-to-landowner agreement — "
            "the foundation of bloc negotiation (see 'Negotiate as a bloc' above), not a "
            "term you hand the developer. It denies the developer its favorite tactic: "
            "buying owners one at a time and sweetening a single holdout to break ranks. "
            "Salem Township, PA landowners used exactly this alignment to pool ~1,700 "
            "acres and sell together for ~\\$586M. Have a licensed real-estate attorney "
            "draft the binding version for your state."
        ),
        "range_low": None,
        "range_high": None,
        "unit": None,
    },
    "Direct financial payments": {
        "icon": "💰",
        "clause": (
            "Developer shall pay an annual Community Benefit Payment of $[X] per MW "
            "of contracted power capacity into a Community Benefit Fund administered "
            "by [County/Town]. Payments commence upon certificate of occupancy and "
            "adjust annually by CPI."
        ),
        "why": (
            "A per-MW annual payment creates a predictable, inflation-protected "
            "revenue stream tied to the facility's actual size. \\$500–\\$2,000/MW/year "
            "is the emerging range in negotiated deals."
        ),
        "range_low": 500,
        "range_high": 2000,
        "unit": "per MW per year",
    },
    "Water consumption cap": {
        "icon": "💧",
        "clause": (
            "Total facility water withdrawal shall not exceed [X] gallons per day. "
            "Developer shall install metering equipment accessible to [Municipal Water "
            "Authority] and pay a surcharge of $[Y] per 1,000 gallons exceeding the cap. "
            "Annual water usage reports shall be public record."
        ),
        "why": (
            "Without a hard cap, evaporative cooling can consume millions of gallons "
            "daily. The penalty surcharge creates a financial incentive to stay under "
            "the cap and funds water infrastructure if they exceed it."
        ),
        "range_low": None,
        "range_high": None,
        "unit": None,
    },
    "Grid upgrade cost allocation": {
        "icon": "⚡",
        "clause": (
            "Developer shall bear 100% of the cost of all transmission and distribution "
            "upgrades, including substation construction, required to serve the facility. "
            "No portion of these costs shall be allocated to existing ratepayers through "
            "base rate adjustments or capacity charges."
        ),
        "why": (
            "Without this clause, utilities socialize grid upgrade costs across all "
            "ratepayers — meaning households subsidize industrial infrastructure. "
            "New Jersey's Large Load Tariff (2025) codifies this at the state level."
        ),
        "range_low": None,
        "range_high": None,
        "unit": None,
    },
    "Residential tax offset": {
        "icon": "🏠",
        "clause": (
            "Revenue from data center property taxes, equipment taxes, and any "
            "negotiated fees shall be applied to reduce the residential property tax "
            "rate before being allocated to general fund expenditures. Annual reporting "
            "shall demonstrate the residential rate reduction attributable to data "
            "center revenue."
        ),
        "why": (
            "Loudoun County, VA demonstrates the model: data center taxes fund ~32% "
            "of the county budget, keeping residential rates among the lowest in "
            "the state. Without explicit allocation, the revenue can be absorbed "
            "into general spending without visible resident benefit."
        ),
        "range_low": None,
        "range_high": None,
        "unit": None,
    },
    "Noise standards": {
        "icon": "🔊",
        "clause": (
            "Facility operations shall not exceed [X] dBA at any residential property "
            "line, measured as a 1-hour Leq. Developer shall conduct third-party noise "
            "monitoring quarterly for the first 3 years and annually thereafter. Results "
            "shall be filed with [County] and made available to the public."
        ),
        "why": (
            "Cooling systems run 24/7 and produce a constant low-frequency hum. "
            "Loudoun County's 38 dBA standard at the property line is the benchmark. "
            "Without a negotiated standard, state noise laws may allow 55–65 dBA."
        ),
        "range_low": None,
        "range_high": None,
        "unit": None,
    },
    "Local hiring & workforce": {
        "icon": "👷",
        "clause": (
            "Developer shall use best efforts to ensure that [X]% of construction labor "
            "and [Y]% of permanent operations staff are sourced from [County/Region]. "
            "Developer shall fund a workforce training program at [local community "
            "college] of not less than $[Z] per year for [N] years, focused on "
            "electrical, HVAC, and network operations certifications."
        ),
        "why": (
            "Data centers create 50–150 permanent jobs per facility — far fewer than "
            "the thousands promised during construction. Workforce training commitments "
            "create lasting value beyond the build phase."
        ),
        "range_low": None,
        "range_high": None,
        "unit": None,
    },
    "Waste heat recovery": {
        "icon": "🌡️",
        "clause": (
            "Developer shall conduct a waste heat feasibility study within 12 months "
            "of certificate of occupancy and, where technically viable, make waste heat "
            "available at no cost to [municipal district heating / school district / "
            "community greenhouse] within [X] miles of the facility."
        ),
        "why": (
            "Data centers reject enormous amounts of heat — typically at 30–45°C, "
            "usable for space heating, greenhouses, and aquaculture. European "
            "facilities already pipe heat to district networks. US communities should "
            "demand this as standard."
        ),
        "range_low": None,
        "range_high": None,
        "unit": None,
    },
    "Decommissioning bond": {
        "icon": "🏗️",
        "clause": (
            "Developer shall post a decommissioning bond or letter of credit equal to "
            "$[X] per MW within 90 days of certificate of occupancy, to fund site "
            "remediation and restoration if the facility ceases operations."
        ),
        "why": (
            "Without a bond, a bankrupt or departing operator can leave the community "
            "with a derelict industrial site and no funds for cleanup. Typical bonds "
            "range from \\$5,000–\\$15,000 per MW."
        ),
        "range_low": 5000,
        "range_high": 15000,
        "unit": "per MW (one-time bond)",
    },
}

# ── Data Dividend calculator defaults ─────────────────────────────────────── #

_DEFAULT_MW = 200
_DEFAULT_CAPEX_PER_MW = 10.0  # $M per MW
_DEFAULT_EQUIP_REFRESH_YRS = 4
_DEFAULT_PROP_TAX_RATE = 1.1  # percent
_DEFAULT_EQUIP_TAX_RATE = 4.0  # percent of assessed value (declining schedule)
_DEFAULT_RESIDENTIAL_PARCELS = 25000
_DEFAULT_CURRENT_RES_TAX = 2800  # $/year per household


def render_toolkit_tab():

    st.subheader("🛡️ Community Negotiation Toolkit")
    st.caption(
        "Actionable tools, model contract language, and calculators to help your "
        "community negotiate the best possible deal — or decide to say no."
    )

    with st.expander("📑 On this page", expanded=False):
        st.markdown(
            "**1.** Your leverage & what to demand · "
            "**2.** Data Dividend Calculator · "
            "**2b.** Land price discovery (USDA farmland baseline) · "
            "**2c.** Negotiate as a bloc (+ checklist) · "
            "**3.** Model CBA clauses (copy & customize) · "
            "**4.** What other communities have won · "
            "**5.** The Alaska Model — data dividends · "
            "**6.** Grid equity demands · "
            "**7.** Protecting the closest neighbors · "
            "**8.** Meeting prep checklist · "
            "**9.** Meeting prep generator (downloadable brief) · "
            "**10.** Advanced revenue capture strategies · "
            "**11.** Industry benchmarks · "
            "**12.** Free consultation request"
        )

    # ================================================================== #
    # SECTION 1 — The core principle
    # ================================================================== #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## The #1 rule: never approve without a contract")

    lev1, lev_arrow, lev2 = st.columns([1, 0.3, 1])
    with lev1:
        st.markdown("#### 🏘️ Your leverage")
        for icon, item in [("🏗️", "Land"), ("💧", "Water"), ("⚡", "Grid capacity"), ("📋", "Zoning approval")]:
            with st.container(border=True):
                st.markdown(f"{icon} **{item}**")
    with lev_arrow:
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("### ➡️")
        st.markdown("*Don't give these away*")
    with lev2:
        st.markdown("#### 📜 What to demand")
        for icon, item in [("💰", "Annual payments"), ("💧", "Water caps"), ("🔊", "Noise limits"), ("⚡", "Rate protection")]:
            with st.container(border=True):
                st.markdown(f"{icon} **{item}**")

    st.error(
        "**Without a CBA:** the developer gets tax breaks, your utility rates rise, "
        "your water table drops, and you get a press release about '50 permanent jobs.'  \n"
        "**With a CBA:** you get annual payments, rate protection, water caps, noise "
        "limits, workforce training, and a decommissioning bond."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ================================================================== #
    # SECTION 2 — Data Dividend Calculator
    # ================================================================== #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 💰 Data Dividend Calculator")
    st.markdown("#### What is your community's data center worth?")
    st.caption(
        "Enter the proposed facility size and your community's details. "
        "This calculator estimates the annual revenue your community should "
        "demand — and what that means for every household."
    )

    calc1, calc2 = st.columns(2)
    with calc1:
        st.markdown("**Facility details**")
        facility_mw = st.slider(
            "Facility capacity (MW)", 50, 1000, _DEFAULT_MW, 25,
            key="tk_mw",
        )
        capex_per_mw = st.slider(
            "CapEx per MW ($M)", 5.0, 20.0, _DEFAULT_CAPEX_PER_MW, 0.5,
            key="tk_capex",
            help="Industry average is \\$8–12M per MW for AI-ready facilities.",
        )
        total_capex = facility_mw * capex_per_mw

    with calc2:
        st.markdown("**Your community**")
        num_households = st.number_input(
            "Residential parcels / households", 1000, 500000,
            _DEFAULT_RESIDENTIAL_PARCELS, 1000,
            key="tk_hh",
        )
        current_res_tax = st.number_input(
            "Current avg. residential property tax ($/yr)", 500, 20000,
            _DEFAULT_CURRENT_RES_TAX, 100,
            key="tk_restax",
        )

    st.divider()
    st.markdown("#### Revenue streams")

    # Property tax on real estate (land + building)
    building_value = total_capex * 0.30  # ~30% of capex is the building
    prop_tax_rate = _DEFAULT_PROP_TAX_RATE / 100
    annual_prop_tax = building_value * 1e6 * prop_tax_rate

    # Equipment/personal property tax (servers, GPUs, networking)
    equip_value = total_capex * 0.50  # ~50% of capex is equipment
    equip_tax_rate = _DEFAULT_EQUIP_TAX_RATE / 100
    annual_equip_tax = equip_value * 1e6 * equip_tax_rate * 0.7  # avg depreciation

    # CBA direct payment
    cba_per_mw = st.slider(
        "Negotiated CBA payment ($/MW/year)", 0, 3000, 1000, 100,
        key="tk_cba_rate",
        help="Emerging range is \\$500–\\$2,000/MW/year. Aim high.",
    )
    annual_cba = facility_mw * cba_per_mw

    # Infrastructure fee
    infra_fee_pct = st.slider(
        "Infrastructure & Energy Fee (% of annual electricity cost)", 0.0, 5.0, 2.0, 0.5,
        key="tk_infra",
        help="A surcharge on the facility's electricity consumption that funds "
             "a local trust fund. 1–3% is reasonable.",
    )
    annual_kwh = facility_mw * 8760 * 0.85 * 1000  # 85% utilization
    avg_rate = 0.07  # $/kWh wholesale
    annual_elec_cost = annual_kwh * avg_rate
    annual_infra_fee = annual_elec_cost * (infra_fee_pct / 100)

    total_annual = annual_prop_tax + annual_equip_tax + annual_cba + annual_infra_fee

    rv1, rv2, rv3, rv4 = st.columns(4)
    rv1.metric("Property tax", f"${annual_prop_tax/1e6:.1f}M/yr")
    rv2.metric("Equipment tax", f"${annual_equip_tax/1e6:.1f}M/yr")
    rv3.metric("CBA payment", f"${annual_cba/1e6:.2f}M/yr")
    rv4.metric("Infrastructure fee", f"${annual_infra_fee/1e6:.2f}M/yr")

    rev_df = pd.DataFrame([
        {"Source": "Property tax", "Amount_M": annual_prop_tax / 1e6},
        {"Source": "Equipment tax", "Amount_M": annual_equip_tax / 1e6},
        {"Source": "CBA payment", "Amount_M": annual_cba / 1e6},
        {"Source": "Infrastructure fee", "Amount_M": annual_infra_fee / 1e6},
    ])
    rev_chart = (
        alt.Chart(rev_df)
        .mark_arc(innerRadius=50, outerRadius=100)
        .encode(
            theta=alt.Theta("Amount_M:Q"),
            color=alt.Color("Source:N",
                scale=alt.Scale(
                    domain=["Property tax", "Equipment tax", "CBA payment", "Infrastructure fee"],
                    range=["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b"]),
                legend=alt.Legend(title="Revenue source")),
            tooltip=["Source:N", alt.Tooltip("Amount_M:Q", format=".2f", title="$M/yr")],
        ).properties(height=220)
    )
    st.altair_chart(rev_chart, use_container_width=True)

    st.divider()
    st.markdown("#### What this means for your community")

    per_household = total_annual / num_households
    tax_offset_pct = min(100, (total_annual / (num_households * current_res_tax)) * 100)
    trust_fund_20yr = annual_infra_fee * 20

    im1, im2, im3 = st.columns(3)
    im1.metric(
        "Total annual revenue",
        f"${total_annual/1e6:.1f}M",
        help="Combined property tax + equipment tax + CBA + infrastructure fee",
    )
    im2.metric(
        "Per household value",
        f"${per_household:,.0f}/yr",
        f"{tax_offset_pct:.0f}% of current property tax",
    )
    im3.metric(
        "20-year trust fund",
        f"${trust_fund_20yr/1e6:.1f}M",
        "From infrastructure fee alone",
    )

    if tax_offset_pct >= 50:
        st.success(
            f"A {facility_mw} MW facility could offset **{tax_offset_pct:.0f}%** of "
            "your community's residential property tax burden — if the revenue is "
            "allocated correctly. **Demand explicit residential tax offset language "
            "in the CBA.**"
        )
    elif tax_offset_pct >= 20:
        st.info(
            f"A {facility_mw} MW facility could offset **{tax_offset_pct:.0f}%** of "
            "residential property taxes. Meaningful, but push for a higher CBA rate "
            "and infrastructure fee to maximize the benefit."
        )
    else:
        st.warning(
            f"At current settings, the offset is only **{tax_offset_pct:.0f}%** of "
            "residential taxes. Consider whether the community impact (water, noise, "
            "grid strain) is worth the deal at these terms."
        )

    st.info(
        "**Want a custom analysis for your community?** GridWatch Consulting "
        "builds facility-specific impact models using your local utility data. "
        "See the **Consulting** tab for a free initial assessment."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ================================================================== #
    # SECTION 2b — Land Price Discovery
    # ================================================================== #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🔎 Land price discovery")
    st.markdown("#### What is the developer really willing to pay?")
    st.caption(
        "The land rush runs on an information gap: the developer knows the campus "
        "is worth billions; sellers priced their acreage against crops. Start here — "
        "the USDA agricultural baseline for your state, plus where to find what the "
        "developer has already paid nearby."
    )

    _pd_states = sorted(FARMLAND_CROPLAND_USD_ACRE_2024.keys())
    _pd_sidebar = st.session_state.get("my_state", "All states")
    _pd_default = _pd_sidebar if _pd_sidebar in _pd_states else "Wisconsin"
    pdc1, pdc2 = st.columns([1.25, 1])
    with pdc1:
        pd_state = st.selectbox(
            "Your state", _pd_states,
            index=_pd_states.index(_pd_default), key="tk_pd_state",
        )
        pd_offer = st.number_input(
            "Offer you've heard ($/acre)", 0, 500000, 0, 5000, key="tk_pd_offer",
            help="Enter a per-acre offer a neighbor received (or leave at 0). "
                 "Recorded deeds show what the developer actually paid — see the "
                 "links below.",
        )
        pd_acres = st.number_input(
            "Acreage in play (optional)", 0, 5000, 0, 10, key="tk_pd_acres",
        )

    pd_baseline = FARMLAND_CROPLAND_USD_ACRE_2024.get(pd_state, US_CROPLAND_USD_ACRE_2024)
    with pdc2:
        st.metric(f"USDA cropland baseline · {pd_state} (2024)", f"${pd_baseline:,}/acre")
        if pd_offer > 0:
            st.metric("Offer vs. farmland value", f"{pd_offer / pd_baseline:.1f}×")
        else:
            st.metric("Typical data-center premium", "10–40× farmland")

    if pd_offer > 0:
        _mult = pd_offer / pd_baseline
        if _mult >= 10:
            st.success(
                f"At **{_mult:.1f}×** the farmland baseline, this offer reflects the "
                "land's value **to the data center**, not to a farmer. That multiple "
                "is your anchor — and a signal the parcel matters to the site plan."
            )
        elif _mult >= 3:
            st.warning(
                f"At **{_mult:.1f}×** farmland value, the offer beats agricultural "
                "comps but is likely well below the developer's ceiling. Neighbors "
                "who compared notes and held out have gotten more."
            )
        else:
            st.info(
                f"At **{_mult:.1f}×** farmland value, this is close to an ordinary "
                "land sale — far under what data-center assemblers have paid "
                "elsewhere. Don't price against crops; price against the campus."
            )

    if pd_acres > 0:
        _base_total = pd_baseline * pd_acres
        _line = f"Farmland-basis value of **{pd_acres:,} acres**: **\\${_base_total:,.0f}**"
        if pd_offer > 0:
            _line += f"  ·  at the \\${pd_offer:,}/acre offer: **\\${pd_offer * pd_acres:,.0f}**"
        st.markdown(_line)

    st.caption(
        "Reference: in Port Washington, WI, sellers were reportedly offered up to "
        "~\\$120,000/acre — roughly **18×** the state's ~\\$6,800/acre cropland baseline."
    )

    st.markdown("**Where to run your own price discovery:**")
    _deed_q = urllib.parse.quote(f"{pd_state} register of deeds property sale price records")
    st.markdown(
        f"- **County deed / recorder records** — what the developer *actually paid* "
        f"for nearby parcels is public record: "
        f"[search {pd_state} deed & property records](https://www.google.com/search?q={_deed_q})\n"
        f"- **USDA NASS QuickStats** — pull live cropland and county-level land values: "
        f"{src_link('usda_quickstats')}\n"
        f"- **Good Jobs First Subsidy Tracker** — tax abatements already handed to "
        f"data centers in your state: {src_link('gjf_subsidy')}\n"
        f"- Baseline figures above: {src_link('usda_land')}"
    )
    st.caption(
        "Cropland baseline is the USDA NASS 2024 state average; AZ and NV use the "
        "state farm-real-estate value (cropland withheld), and the six New England "
        "states share USDA's regional figure. Treat it as the *floor*, not the offer."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ================================================================== #
    # SECTION 2c — Negotiate as a bloc
    # ================================================================== #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🤝 Negotiate as a bloc, not parcel-by-parcel")
    st.caption(
        "Developers assemble land quietly, one owner at a time, so no seller ever "
        "sees the whole picture. Neighbors who negotiate together erase that "
        "information gap — and the largest collective deals show how much is at stake."
    )

    st.markdown("#### The precedent: Salem Township, Pennsylvania")
    sb1, sb2, sb3, sb4 = st.columns(4)
    sb1.metric("Landowners", "96")
    sb2.metric("Acres pooled", "~1,700")
    sb3.metric("Total sale", "$586M")
    sb4.metric("Avg / acre", "$330K")
    st.markdown(
        "Rather than let a developer pick them off one parcel at a time, **96 Salem "
        "Township families pooled ~1,700 acres and sold together to QTS (a Blackstone "
        "company) for \\$586 million** — about **\\$330,000 an acre**, roughly \\$5.5M "
        "per family — anchoring a ~\\$10B campus. The organizers describe the strategy "
        "in exactly these terms: keep landowners *aligned and informed* and work the "
        f"township process together, instead of forcing a deal one property at a time. "
        f"{src_link('salem_bloc')} A second Salem Township bloc has since announced a "
        f"~\\$1.2 billion follow-on deal. {src_link('salem_bloc2')}"
    )
    st.info(
        "Contrast Port Washington, where owners sold one at a time — and some later "
        "said *\"after the fact, you hear what everybody else got.\"* Same land rush, "
        "opposite outcome."
    )

    st.markdown("#### A proven playbook from resource extraction")
    st.markdown(
        "Landowner bloc negotiation isn't new — it's how rural communities have dealt "
        "with extractive industries for decades:\n"
        f"- **Oil & gas** — Marcellus Shale **landowner coalitions** pooled thousands of "
        f"acres to negotiate gas leases together, winning higher signing bonuses and "
        f"royalties than neighbors who signed alone. {src_link('marcellus_lease')}\n"
        "- **Wind & solar** — developer leases carry confidentiality clauses precisely so "
        "neighbors *can't* compare terms; landowner groups that pool information close "
        "that gap.\n"
        "- **The through-line:** whoever controls the information controls the price. A "
        "bloc is how sellers take that control back — the same logic behind the **Alaska "
        "Model** for ongoing revenue (Section 5 below)."
    )

    with st.expander("📋 How to build a landowner bloc — the playbook", expanded=False):
        st.markdown(
            "**Set it up**\n"
            "1. **Talk to neighbors the moment LLC offers appear.** That's the signal "
            "assembly has begun — and the strategy depends on you *not* comparing notes. "
            "One meeting erases the information gap.\n"
            "2. **Form a real structure.** A landowner association/LLC or a **land-pooling "
            "agreement** (borrowed from oil & gas): negotiate as one, share proceeds by a "
            "set formula (usually pro-rata by acreage) so no single parcel is a make-or-"
            "break holdout — or a target to buy off.\n"
            "3. **Sign a \"no individual deals\" pact with teeth** — a right of first "
            "refusal to the group and/or liquidated damages for breaking ranks, plus a "
            "**most-favored-nation clause** so any better price one owner wins flows to "
            "everyone. This is what defeats the sweetened-holdout play.\n"
            "4. **Hire shared professionals and split the cost** — a land-use attorney and "
            "an appraiser/broker who knows **industrial / data-center comps, not "
            "cropland**. The developer already has all three.\n\n"
            "**Run it**\n"
            "5. **Do price discovery first** (see the tool above): deed records, the USDA "
            "baseline, and data-center land comps tell you the developer's likely ceiling.\n"
            "6. **One voice, closed cards.** One spokesperson; never reveal individual "
            "reservation prices.\n"
            "7. **Know your leverage geometry.** Contiguous parcels the site *needs* = a "
            "critical bloc; peripheral/fungible parcels = less leverage. The site plan and "
            "interconnection filings hint at what they actually require.\n"
            "8. **Negotiate more than price** — escalators, phased payments, environmental "
            "protections, and terms for neighbors facing **transmission eminent domain** so "
            "non-sellers aren't left carrying the wires for nothing.\n\n"
            "**Expect the traps**\n"
            "9. **Fake deadlines and \"your neighbor already signed\" bluffs** are split "
            "tactics — a written pact and shared counsel make them inert. Verify the claim; "
            "it's often untrue.\n"
            "10. **Fix the proceeds formula and taxes up front** (installment sales, 1031 "
            "exchanges) so the structure doesn't quietly erode the gain.\n"
            "11. **Coordinate with the town's CBA process** so the developer can't play "
            "landowners against the municipality."
        )

    _bloc_checklist = (
        "LANDOWNER BLOC NEGOTIATION — QUICK CHECKLIST (GridWatch AI)\n"
        "=========================================================\n\n"
        "SET IT UP\n"
        "[ ] Talk to neighbors the moment mysterious LLC offers appear\n"
        "[ ] Compare notes: what has each owner been offered? (kills the info gap)\n"
        "[ ] Form a structure: landowner association/LLC or land-pooling agreement\n"
        "[ ] Agree a proceeds-sharing formula (usually pro-rata by acreage)\n"
        "[ ] Sign a 'no individual deals' pact: right of first refusal to the group\n"
        "    + liquidated damages for breaking ranks + most-favored-nation clause\n"
        "[ ] Hire shared pros (split cost): land-use attorney + industrial appraiser/broker\n\n"
        "RUN IT\n"
        "[ ] Price discovery first: county deed records, USDA baseline, data-center comps\n"
        "[ ] One spokesperson; never disclose individual reservation prices\n"
        "[ ] Assess leverage geometry: are your parcels critical to the site footprint?\n"
        "[ ] Negotiate beyond price: escalators, phased payments, environmental terms,\n"
        "    and protections for neighbors facing transmission eminent domain\n\n"
        "EXPECT THE TRAPS\n"
        "[ ] Treat deadlines and 'your neighbor already signed' as split tactics — verify\n"
        "[ ] Set proceeds formula + tax structure up front (installment sales / 1031)\n"
        "[ ] Coordinate with the town's CBA / permit process\n\n"
        "PRECEDENTS\n"
        "- Salem Township, PA: 96 owners pooled ~1,700 acres, sold together for ~$586M\n"
        "  (~$330K/acre) to QTS/Blackstone; a 2nd bloc announced a ~$1.2B follow-on.\n"
        "- Marcellus Shale gas landowner coalitions: pooled acreage won higher bonuses\n"
        "  and royalties than solo signers.\n\n"
        "NOT LEGAL ADVICE. Consult a licensed land-use / real-estate attorney in your\n"
        "state before forming a coalition or signing anything. Requirements for pooling\n"
        "agreements, and any antitrust considerations, vary by jurisdiction.\n"
    )
    st.download_button(
        "⬇️ Download the bloc-negotiation checklist",
        data=_bloc_checklist,
        file_name="landowner-bloc-negotiation-checklist.txt",
        mime="text/plain",
        key="tk_bloc_dl",
        on_click=log_event,
        args=("toolkit_download",),
        kwargs={"item": "bloc_checklist"},
    )

    st.warning(
        "**Not legal advice.** This is educational information, not a substitute for "
        "counsel. Forming a landowner coalition, drafting a pooling or "
        "no-individual-deals agreement, and structuring the sale (and its taxes) all "
        "carry legal consequences that vary by state — and collective arrangements can "
        "raise antitrust questions in some framings. **Consult a licensed land-use / "
        "real-estate attorney in your jurisdiction before organizing a bloc or signing "
        "anything.**"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ================================================================== #
    # SECTION 3 — Model CBA Clauses
    # ================================================================== #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 📜 Model CBA clauses")
    st.markdown("#### Copy, customize, and bring to your planning commission")
    st.caption(
        "These are starting points — not legal advice. Have a local attorney "
        "review and adapt them to your state's laws and your community's needs."
    )

    for name, clause in _MODEL_CLAUSES.items():
        with st.expander(f"{clause['icon']} {name}", expanded=False):
            st.markdown("**Model language:**")
            st.code(clause["clause"], language=None)
            st.markdown(f"**Why this matters:** {clause['why']}")
            if clause.get("range_low"):
                st.caption(
                    f"Typical range: \\${clause['range_low']:,}–"
                    f"\\${clause['range_high']:,} {clause['unit']}"
                )
    st.info(
        "**Need clauses tailored to your situation?** These are starting points — "
        "GridWatch Consulting drafts custom CBA language for your specific "
        "developer, facility, and jurisdiction. See the **Consulting** tab."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ================================================================== #
    # SECTION 4 — Real-world examples
    # ================================================================== #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🏆 What other communities have won")
    st.markdown("#### Real deals, real outcomes")
    st.caption("Learn from communities that negotiated well — and those that didn't.")

    for ex in _CBA_EXAMPLES:
        with st.expander(
            f"**{ex['community']}** — {ex['operator']} ({ex['year']})",
            expanded=False,
        ):
            e1, e2 = st.columns([1, 1.5])
            with e1:
                st.metric("Facility size", f"{ex['mw']} MW")
                st.metric("Investment", f"${ex['investment_b']:.1f}B")
            with e2:
                st.markdown("**What they got:**")
                for item in ex["what_they_got"]:
                    st.markdown(f"- {item}")
            st.info(f"**Key lesson:** {ex['lesson']}")
    st.markdown("</div>", unsafe_allow_html=True)

    # ================================================================== #
    # SECTION 5 — The Alaska Model
    # ================================================================== #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🏔️ The Alaska Model — Data Dividends")
    st.markdown("#### If they're extracting your resources, you deserve a share")

    ak1, ak_arrow, ak2, ak_arrow2, ak3 = st.columns([1, 0.2, 1, 0.2, 1])
    with ak1:
        st.markdown("**🏘️ Resources extracted**")
        for item in ["🏗️ Your land", "💧 Your water", "⚡ Your grid", "🏚️ Your stability"]:
            st.markdown(f"&nbsp;&nbsp;{item}")
    with ak_arrow:
        st.markdown("")
        st.markdown("")
        st.markdown("### ➡️")
    with ak2:
        with st.container(border=True):
            st.markdown("**🏢 Data Center**")
            st.markdown("Generates billions")
            st.markdown("⬇️ 1–3% fee")
            st.markdown("**🏦 Trust Fund**")
    with ak_arrow2:
        st.markdown("")
        st.markdown("")
        st.markdown("### ➡️")
    with ak3:
        st.markdown("**🏘️ Community receives**")
        for item in ["💵 Direct payments", "🎓 Scholarships", "⚡ Bill credits", "👶 Childcare"]:
            st.markdown(f"&nbsp;&nbsp;{item}")

    st.markdown("#### How to build a local Data Dividend fund")

    step1, step2, step3 = st.columns(3)
    with step1:
        with st.container(border=True):
            st.markdown("**Step 1: Levy the fee**")
            st.markdown(
                "Pass a local **Infrastructure and Energy Fee** — a small surcharge "
                "(1–3%) on the data center's annual electricity consumption. This is "
                "not a tax on the company; it's a fee for the community infrastructure "
                "their load demands."
            )
    with step2:
        with st.container(border=True):
            st.markdown("**Step 2: Create the fund**")
            st.markdown(
                "Revenues flow into a **Community Data Dividend Trust Fund** — a "
                "ring-fenced account that cannot be raided for general spending. "
                "The fund is governed by an independent board with resident "
                "representation."
            )
    with step3:
        with st.container(border=True):
            st.markdown("**Step 3: Distribute the dividend**")
            st.markdown(
                "The fund pays out annually as: **direct payments** to households, "
                "**free/reduced childcare**, **technical education scholarships**, "
                "or **residential utility bill credits**. The community votes on "
                "the allocation."
            )

    if annual_infra_fee > 0:
        dividend_per_hh = annual_infra_fee / num_households
        st.success(
            f"Based on your calculator inputs above: a {infra_fee_pct:.1f}% "
            f"infrastructure fee on a {facility_mw} MW facility would generate "
            f"**\\${annual_infra_fee/1e6:.2f}M/year** — or **\\${dividend_per_hh:,.0f} "
            f"per household per year** as a direct data dividend."
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # ================================================================== #
    # SECTION 6 — Grid Equity
    # ================================================================== #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## ⚡ Grid Equity Demands")
    st.markdown("#### Don't let them raise your electric bill")

    ge_a, ge_b, ge_c = st.columns(3)
    with ge_a:
        with st.container(border=True):
            st.markdown("**🏢 200+ MW Data Center**")
            st.markdown("Requires grid upgrades: substations, transmission lines — \\$100M+")
    with ge_b:
        st.error("**❌ WITHOUT protection**\n\nAll ratepayers pay via rate increase")
    with ge_c:
        st.success("**✅ WITH cost causation**\n\nDeveloper pays 100% of upgrades")

    ge1, ge2 = st.columns(2)
    with ge1:
        st.markdown("**Demand these grid protections:**")
        st.markdown(
            "1. **Cost causation:** The data center pays for 100% of the grid "
            "upgrades its load requires — no cost-shifting to households.  \n"
            "2. **Rate impact study:** Require the utility to publish a study "
            "showing the rate impact on residential customers *before* approval.  \n"
            "3. **Rate cap commitment:** The developer commits to covering any "
            "residential rate increase attributable to their load for [X] years.  \n"
            "4. **Clean backup power:** No diesel generators — require battery "
            "storage or clean fuel cells for emergency backup."
        )
    with ge2:
        st.markdown("**Demand these resource protections:**")
        st.markdown(
            "1. **Water metering and public reporting:** Real-time or monthly "
            "disclosure of water withdrawal, publicly accessible.  \n"
            "2. **Drought curtailment:** During water shortage declarations, the "
            "data center reduces cooling water use before any residential "
            "restrictions take effect.  \n"
            "3. **Waste heat offer:** The developer must study and, where viable, "
            "provide waste heat to local buildings at no cost.  \n"
            "4. **Noise monitoring:** Continuous noise monitoring with automatic "
            "public reporting and financial penalties for exceedances."
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ================================================================== #
    # SECTION 7 — Protecting the closest neighbors
    # ================================================================== #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🏠 Protecting and compensating the closest neighbors")
    st.caption(
        "A regional study that finds 'no measurable effect on property values' "
        "and the family 300 feet from the fence line are two different realities. "
        "If your property directly borders the site, the community-wide CBA may "
        "not be enough — you need protections specific to proximity."
    )

    st.info(
        "**If you are a directly-affected property owner:** Identify yourself "
        "early in the process, attend every hearing, and start a **dated impact "
        "log** now — photos, noise readings (a free phone app works), before-and-"
        "after appraisals, any health complaints. Documentation created *before* "
        "construction is far stronger than memories reconstructed after."
    )

    st.markdown("### Five remedies — from permit conditions to litigation")
    st.markdown(
        "These build on each other. Start at the top; litigation is the "
        "backstop, not the first move."
    )

    with st.expander("1. Developer-paid mitigation (permit conditions)", expanded=True):
        st.markdown(
            "The most direct tool: **make the developer pay to mitigate the "
            "impact on adjacent properties as a condition of the permit.** "
            "Planning commissions and zoning boards can require these before "
            "any approval is granted."
        )
        mit_items = [
            ("Sound walls / noise barriers", "$150–$300/lin. ft",
             "Effective for mechanical noise from cooling systems at the "
             "property line. Demand third-party acoustic design, not the "
             "developer's own spec."),
            ("Acoustic windows for adjacent homes", "$800–$1,500/window",
             "Double- or triple-pane retrofits for homes within the noise "
             "impact zone. Developer funds the full replacement."),
            ("HVAC / air filtration upgrades", "$5K–$15K/home",
             "Backup generator emissions and construction dust affect the "
             "nearest homes. Developer-funded HEPA filtration or HVAC upgrades."),
            ("Landscape screening & setback buffers", "Varies",
             "Dense tree plantings, earthen berms, or expanded setbacks "
             "beyond the minimum zoning requirement — especially for light "
             "pollution from 24/7 security lighting."),
        ]
        for label, cost, desc in mit_items:
            with st.container(border=True):
                mc1, mc2 = st.columns([2, 1])
                with mc1:
                    st.markdown(f"**{label}**")
                    st.caption(desc)
                with mc2:
                    st.metric("Typical cost", cost)

        st.warning(
            "**Push for these as binding permit conditions**, not voluntary "
            "commitments. A condition in the zoning approval is enforceable; "
            "a promise in a press release is not."
        )

    with st.expander("2. Property-value guarantees", expanded=False):
        st.markdown(
            "A **property-value guarantee** is a written commitment from the "
            "developer: if you sell your home within a set period and the sale "
            "price is less than the pre-project appraised value, **the developer "
            "makes you whole** — paying the difference."
        )
        st.markdown(
            "- **Precedent:** Property-value guarantees are well-established in "
            "**wind energy** and **pipeline** siting. They are still uncommon in "
            "data center deals specifically, but that makes them an *ask*, not a "
            "fantasy — communities that demand them first set the benchmark.\n"
            "- **Structure:** Independent pre-construction appraisal (not the "
            "developer's appraiser), a guarantee period of at least 5–10 years, "
            "and an arbitration mechanism for disputes.\n"
            "- **Key principle:** The guarantee should cover the *difference* "
            "between the pre-project appraisal and the actual sale price, not "
            "just a fixed dollar amount."
        )
        st.info(
            "**Honest caveat:** Property-value guarantees are proven in wind "
            "and pipeline siting but still rare in data center deals. We frame "
            "this as a documented tool to demand — and communities that go first "
            "create the precedent."
        )

    with st.expander("3. Voluntary buyouts", expanded=False):
        st.markdown(
            "When mitigation isn't enough, the next step is a **voluntary "
            "buyout** — the developer purchases the adjacent property at a "
            "fair (or above-market) price so the family can relocate."
        )

        bo1, bo2 = st.columns(2)
        with bo1:
            with st.container(border=True):
                st.markdown("**Mason County, WV — 'Good Neighbors' program**")
                st.markdown(
                    "A data center developer created a formal buyout program "
                    "for the closest residential properties. The program offers "
                    "the **highest of three independent appraisals plus a "
                    f"relocation premium.** {src_link('mason_buyout')}"
                )
        with bo2:
            with st.container(border=True):
                st.markdown("**Ashburn / Loudoun County, VA**")
                st.markdown(
                    "Homeowners adjacent to expanding data center campuses "
                    "have reported buyout offers of **~\\$4 million per home** "
                    "from developers assembling buffer land around their "
                    f"facilities. {src_link('ashburn_buyout')}"
                )

        st.markdown(
            "**Key principles for a fair buyout:**\n"
            "- **Voluntary** — the owner decides whether to sell. A buyout "
            "program that pressures holdouts is a forced taking in disguise.\n"
            "- **Above-market pricing** — the highest of multiple independent "
            "appraisals, plus a premium for involuntary disruption.\n"
            "- **Relocation assistance** — moving costs, temporary housing, "
            "and a reasonable timeline (6–12 months minimum).\n"
            "- **Leverage note:** If your property is needed for the site "
            "footprint or as a buffer, and the project requires a rezoning "
            "that needs unanimous consent (or near-unanimous), **holdouts "
            "have real leverage** — use it to negotiate, not just to block."
        )

    with st.expander("4. Eminent domain — know the real risk", expanded=False):
        st.markdown(
            "Data centers themselves are almost never built via eminent "
            "domain — they need willing sellers and zoning approval. **The "
            "real forced-taking risk is the transmission line**, not the "
            "data center."
        )
        st.markdown(
            "- **Transmission easements** are acquired by the utility (not the "
            "developer) under state eminent-domain authority. In Georgia, "
            "utilities building lines to serve data centers have offered "
            f"**125% of appraised value** for easements. {src_link('ga_eminent')}\n"
            "- **Easements outlive the sale** — even if you sell the property "
            "later, the transmission easement stays. It permanently limits "
            "what you can build on the affected strip.\n"
            "- **Compensation is for the easement, not the property** — you "
            "keep the land but lose the use. Negotiate the compensation "
            "based on the full diminution of property value, not just the "
            "strip's acreage."
        )
        st.warning(
            "If a new transmission line is proposed to serve a data center "
            "near your property, **hire your own appraiser immediately** — "
            "the utility's offer is a starting point, not a final number. "
            "You have the right to negotiate and, in most states, to "
            "challenge the valuation in court."
        )

    with st.expander("5. Litigation as a backstop", expanded=False):
        st.markdown(
            "If the developer won't mitigate, won't guarantee values, and "
            "won't buy you out, **litigation is the backstop** — not the "
            "first move, but sometimes the only one left."
        )
        st.markdown(
            f"Typical claims in industrial-siting neighbor suits "
            f"({src_link('nuisance_law')}):\n"
            "- **Diminished property value** — the difference between your "
            "home's value before and after the facility, supported by "
            "appraisals and comparable sales.\n"
            "- **Loss of use and enjoyment** — noise, light, vibration, "
            "or traffic that materially interferes with your use of your "
            "own property (the common-law nuisance standard).\n"
            "- **Mitigation costs** — if you've had to install your own "
            "sound barriers, window treatments, or filtration systems to "
            "make the property livable."
        )
        st.info(
            "**Your dated impact log is your evidence.** The photos, noise "
            "readings, and before-and-after appraisals you started at the "
            "beginning of this process become the foundation of any legal "
            "claim. Start documenting now, even if you hope you'll never "
            "need it."
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # ================================================================== #
    # SECTION 8 — Meeting prep checklist
    # ================================================================== #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 📋 Meeting prep checklist")
    st.markdown(
        "#### Going to a planning commission or zoning board meeting? Bring this."
    )

    questions = [
        ("Power", "How many MW will this facility draw? Who pays for grid upgrades? What is the projected impact on residential electricity rates?"),
        ("Water", "How many gallons per day will cooling consume? From which source? Is there a hard cap with penalties? What happens during drought?"),
        ("Tax deal", "What specific tax incentives are being offered? For how long? What are the clawback provisions if commitments aren't met?"),
        ("Jobs", "How many permanent local jobs? What percentage of construction labor will be local? Is there a funded workforce training program?"),
        ("Noise", "What is the projected noise level at the nearest residential property line? How does it compare to Loudoun County's 38 dBA standard?"),
        ("Community benefit", "Is there a Community Benefit Agreement? What are the annual payments? Who administers the fund? Is it legally binding?"),
        ("Decommissioning", "What happens if the facility closes? Is there a decommissioning bond? Who pays for site remediation?"),
        ("Transparency", "Will water usage, noise levels, and emissions data be publicly reported? How often? Where?"),
    ]

    for topic, q in questions:
        st.checkbox(f"**{topic}:** {q}", key=f"tk_check_{topic}")

    st.divider()
    st.markdown("**For the closest property owners:**")
    neighbor_questions = [
        ("Setbacks", "What is the minimum setback from the facility boundary to the nearest residential property line? How does it compare to Loudoun County's 1,000-ft standard?"),
        ("Mitigation", "Will the developer fund sound walls, acoustic windows, or HVAC upgrades for adjacent homes — and are these binding permit conditions or voluntary promises?"),
        ("Property values", "Is the developer offering a property-value guarantee or buyout program for directly-affected homeowners? What are the terms?"),
        ("Transmission", "Will new transmission lines cross residential properties? If so, what is the compensation for easements, and does it cover full diminution of value?"),
    ]
    for topic, q in neighbor_questions:
        st.checkbox(f"**{topic}:** {q}", key=f"tk_check_nbr_{topic}")

    st.caption(
        "Print this page or take a screenshot. Every question the developer "
        "can't answer clearly is a reason to pause the approval."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ================================================================== #
    # SECTION 7b — Meeting Prep Generator
    # ================================================================== #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 📄 Meeting Prep Generator")
    st.markdown("#### Auto-generate a one-page brief for your next meeting")
    st.caption(
        "Select your state, the company/operator you're facing, and the "
        "meeting type. We'll pull real data from our databases to build a "
        "downloadable brief with talking points, CBA targets, and questions."
    )

    mg1, mg2, mg3 = st.columns(3)
    with mg1:
        _sidebar_st = st.session_state.get("my_state", "All states")
        _mg_states = sorted(STATE_GRID_PROFILES.keys())
        _mg_idx = _mg_states.index(_sidebar_st) if _sidebar_st in _mg_states else 0
        mg_state = st.selectbox("Your state", _mg_states, index=_mg_idx, key="mg_state")
    with mg2:
        _ops = sorted(OPERATORS_DF["operator"].unique().tolist())
        _ops_with_unknown = ["Unknown / not listed"] + _ops
        mg_operator = st.selectbox("Company / operator", _ops_with_unknown, key="mg_operator")
    with mg3:
        mg_meeting = st.selectbox(
            "Meeting type",
            ["Planning commission hearing", "Zoning board meeting",
             "Town hall / public comment", "Direct negotiation with developer",
             "PUC rate case hearing"],
            key="mg_meeting")

    mg_mw = st.slider("Proposed facility size (MW)", 50, 1000, 200, 50, key="mg_mw")

    if st.button("📝 Generate meeting brief", type="primary", key="mg_generate"):
        brief = build_meeting_brief(mg_state, mg_operator, mg_meeting, mg_mw)
        log_event("meeting_brief_generated", state=mg_state,
                  operator=mg_operator, meeting=mg_meeting, mw=mg_mw)

        st.success("Brief generated! Review below and download.")
        st.text(brief)
        st.download_button(
            "📥 Download meeting brief",
            brief,
            f"meeting_brief_{mg_state.replace(' ', '_')}_{mg_meeting.split()[0].lower()}.txt",
            "text/plain",
            key="mg_download",
            on_click=log_event,
            args=("toolkit_download",),
            kwargs={"item": "meeting_brief", "state": mg_state,
                    "operator": mg_operator, "mw": mg_mw},
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # ================================================================== #
    # SECTION 8 — Advanced Revenue Capture Strategies
    # ================================================================== #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🏛️ Advanced Revenue Capture Strategies")
    st.markdown("#### Beyond the CBA — policy tools that maximize community value")
    st.caption(
        "These strategies go beyond individual CBAs. They're legislative and "
        "policy tools that states and municipalities can adopt to ensure data "
        "centers pay their fair share permanently — not just during a one-time negotiation."
    )

    # ── Energy Severance Tax ─────────────────────────────────────────── #
    with st.expander("⚡ Energy Severance Tax", expanded=True):
        st.markdown(
            "**The idea:** Just as oil-producing states levy a severance tax on "
            "extracted oil, communities can levy a per-kWh fee on massive "
            "electricity consumers that are 'extracting' local grid capacity."
        )

        st.markdown("**Real legislation:**")
        ev1, ev2 = st.columns(2)
        with ev1:
            with st.container(border=True):
                st.markdown("**Virginia H.B. 30 (2026)**")
                st.markdown(
                    "- **\\$0.011/kWh** electricity consumption tax on data centers\n"
                    "- **\\$600M annual revenue cap** (statewide)\n"
                    "- Applies to facilities drawing significant grid load\n"
                    "- *Source: Virginia General Assembly budget bill*"
                )
        with ev2:
            with st.container(border=True):
                st.markdown("**Minnesota Data Center Fees (2025)**")
                st.markdown(
                    "- **Tiered annual fees** by facility size:\n"
                    "  - \\$2M/yr for smaller facilities\n"
                    "  - \\$5M/yr for large (100+ MW) facilities\n"
                    "- Removed sales tax exemption on electricity\n"
                    "- *Source: Minnesota Legislature*"
                )

        st.markdown("**What it means for your community:**")
        sev_mw = facility_mw
        sev_kwh = sev_mw * 8760 * 0.85 * 1000
        sev_revenue = sev_kwh * 0.011
        sev_rev_str = f"\\${sev_revenue/1e6:.1f}M/year"
        st.info(
            f"At Virginia's \\$0.011/kWh rate, a {sev_mw} MW facility would generate "
            f"**{sev_rev_str}** in severance tax revenue. "
            "Push your state legislature to adopt a similar measure — or negotiate "
            "an equivalent 'energy impact fee' directly in the CBA."
        )

    # ── Compute Royalty / Revenue Share ──────────────────────────────── #
    with st.expander("💎 Compute Royalty — Revenue Share", expanded=True):
        st.markdown(
            "**The idea:** Data centers use local resources (land, water, power, "
            "grid capacity) to generate cloud computing revenue. A compute royalty "
            "captures a small percentage of that revenue — similar to mineral "
            "royalties — rather than relying solely on property taxes."
        )

        st.markdown("**Real examples:**")
        cr1, cr2, cr3 = st.columns(3)
        with cr1:
            with st.container(border=True):
                st.markdown("**Lancaster, PA**")
                st.markdown(
                    "- \\$20.25M total CBA package\n"
                    "- \\$10M letter of credit tied to\n"
                    "  clean energy compliance\n"
                    "- Effectively a revenue-linked\n"
                    "  performance guarantee"
                )
        with cr2:
            with st.container(border=True):
                st.markdown("**Cedar Rapids, IA**")
                st.markdown(
                    "- Google: \\$400K/yr × 15 years\n"
                    "- QTS: \\$1M/yr × 18 years\n"
                    "- Annual payments create\n"
                    "  ongoing accountability"
                )
        with cr3:
            with st.container(border=True):
                st.markdown("**Proposed Federal Act**")
                st.markdown(
                    "- **0.5% of gross revenue**\n"
                    "  as annual community\n"
                    "  contribution\n"
                    "- Would standardize compute\n"
                    "  royalties nationally"
                )

        annual_revenue_est = facility_mw * 1.1  # ~$1.1M revenue per MW (conservative)
        royalty_05 = annual_revenue_est * 0.005
        royalty_1 = annual_revenue_est * 0.01
        royalty_2 = annual_revenue_est * 0.02
        st.markdown("**Estimated royalty revenue** (based on ~\\$1.1M revenue/MW):")
        ry1, ry2, ry3 = st.columns(3)
        ry1.metric("0.5% royalty", f"${royalty_05:.1f}M/yr")
        ry2.metric("1.0% royalty", f"${royalty_1:.1f}M/yr")
        ry3.metric("2.0% royalty", f"${royalty_2:.1f}M/yr")

    # ── Gross Receipts Tax ───────────────────────────────────────────── #
    with st.expander("🧾 Gross Receipts Tax", expanded=True):
        st.markdown(
            "**The idea:** Unlike income taxes (which data centers minimize via "
            "depreciation), a gross receipts tax applies to total revenue — "
            "before deductions. It's harder to avoid and captures value even "
            "when companies report minimal profit."
        )

        st.markdown("**States that already tax data center revenue:**")
        grt_data = pd.DataFrame([
            {"State": "Ohio", "Tax": "Commercial Activity Tax (CAT)",
             "Rate": "0.26% of gross receipts > $1M", "Note": "Broad-based, includes data processing"},
            {"State": "Oregon", "Rate": "0.57%", "Tax": "Corporate Activity Tax (CAT)",
             "Note": "Applies to commercial activity > $1M"},
            {"State": "Texas", "Tax": "Franchise Tax (margin tax)",
             "Rate": "0.375–0.75%", "Note": "Taxes 'data processing services' under 34 TAC §3.330"},
            {"State": "Virginia", "Tax": "BPOL Tax",
             "Rate": "Varies by locality", "Note": "Business license tax on gross receipts; localities set rates"},
            {"State": "Washington", "Tax": "Business & Occupation Tax",
             "Rate": "0.471–1.5%", "Note": "No corporate income tax; B&O applies to all business activity"},
        ])
        st.dataframe(grt_data, hide_index=True, use_container_width=True)

        st.markdown(
            "**Connecticut** also applies a reduced **1% rate** specifically on "
            "data processing services."
        )
        st.info(
            "**Why this matters:** A data center with \\$220M in annual revenue "
            "paying a 0.5% gross receipts tax generates **\\$1.1M/year** for the "
            "state — revenue that can't be zeroed out by depreciation schedules "
            "or transfer pricing."
        )

    # ── Corporate Tax Apportionment ──────────────────────────────────── #
    with st.expander("📊 Corporate Tax Apportionment — Who Gets the Tax Base?", expanded=True):
        st.markdown(
            "**The idea:** States divide a multistate corporation's taxable income "
            "using an apportionment formula. The formula determines how much of "
            "a data center's profits your state can tax. The wrong formula means "
            "billions in equipment sits in your state but the tax revenue goes elsewhere."
        )

        ap1, ap2 = st.columns(2)
        with ap1:
            with st.container(border=True):
                st.markdown("**✅ Property-weighted formula (better for communities)**")
                st.markdown(
                    "The traditional **UDITPA 3-factor formula** divides income "
                    "equally among property, payroll, and sales. Since data centers "
                    "have massive property (servers, buildings) but sell services "
                    "to customers everywhere, the property factor keeps tax revenue "
                    "in the state where the equipment sits.\n\n"
                    "**Virginia** retains its property factor — one reason Loudoun "
                    "County captures so much revenue."
                )
        with ap2:
            with st.container(border=True):
                st.markdown("**❌ Single-sales-factor (bad for host communities)**")
                st.markdown(
                    "**12+ states** have adopted single-sales-factor apportionment, "
                    "which assigns income only based on where customers are — not "
                    "where the data center is built. This effectively **exempts "
                    "capital-intensive operations** from state income tax.\n\n"
                    "If your state uses single-sales-factor, the data center's "
                    "\\$775M in equipment generates almost no income tax revenue "
                    "for your community."
                )

        st.warning(
            "**Action item:** Before approving any data center incentive package, "
            "check whether your state uses property-weighted or single-sales-factor "
            "apportionment. If single-sales-factor, the income tax revenue projections "
            "in the developer's pitch are likely inflated. Demand higher CBA payments "
            "and property/equipment taxes to compensate."
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # ================================================================== #
    # SECTION 9 — Know the Numbers
    # ================================================================== #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 📐 Know the Numbers — Industry Benchmarks")
    st.markdown(
        "#### Walk into any negotiation knowing what the facility is actually worth"
    )
    st.caption(
        "These are the real economics data center developers don't volunteer. "
        "Sources: Loudoun County government, Epoch AI, Brookings Institution, "
        "Tax Foundation, Columbia Law School."
    )

    bn1, bn2, bn3, bn4 = st.columns(4)
    bn1.metric(
        "Typical CapEx",
        "$8–12M / MW",
        "AI-ready facilities trend higher",
        help="A 100 MW AI facility costs \\$800M–\\$1.2B to build. A 1 GW "
             "campus: ~\\$38B (Epoch AI estimate).",
    )
    bn2.metric(
        "Equipment share",
        "~77% of CapEx",
        "Servers, GPUs, networking",
        help="For a \\$1B facility, ~\\$775M is taxable equipment. This is the "
             "property tax base developers try to get exempted.",
    )
    bn3.metric(
        "Permanent jobs",
        "~157 / facility",
        "Avg across industry",
        help="Subsidies average \\$1.4M–\\$2.1M per permanent job created. "
             "Compare to manufacturing at ~\\$50K–\\$200K per job.",
    )
    bn4.metric(
        "Annual TCO",
        "~$8.5M / MW",
        "Operating cost (Epoch AI)",
        help="A 100 MW facility costs ~\\$850M/year to operate (power, cooling, "
             "staff, maintenance, refresh cycles).",
    )

    st.divider()
    st.markdown("#### The Loudoun County benchmark")
    lc1, lc2, lc3 = st.columns(3)
    lc1.metric(
        "% of county budget",
        "38%",
        "From just 4% of parcels",
        help="Data centers fund over a third of Loudoun County's general fund "
             "while occupying a tiny fraction of the land.",
    )
    lc2.metric(
        "Equipment tax revenue",
        "$330M+",
        "FY2020 (single year)",
        help="Computer equipment tax (personal property) is the largest single "
             "revenue source for Loudoun County.",
    )
    lc3.metric(
        "Property tax rate drop",
        "$1.145 → $0.805",
        "Per $100 assessed value",
        help="DC revenue allowed the county to cut residential property tax "
             "rates by 30% — the most tangible resident benefit.",
    )

    st.success(
        "**Use Loudoun County as your benchmark.** When a developer says 'we'll "
        "bring tax revenue,' ask: will you match Loudoun County's model, where "
        "data centers fund 38% of the county budget and residential tax rates "
        "dropped 30%? If not, why should we approve?"
    )

    st.divider()
    st.markdown("#### The subsidy trap")
    st.warning(
        "**Virginia foregoes ~\\$1B/year** in data center tax subsidies (sales tax "
        "exemptions, investment incentives). That's \\$1B that could fund schools, "
        "roads, and services. Before accepting a subsidized deal, calculate:\n\n"
        "- **What the developer is asking for** (tax breaks, free land, utility discounts)\n"
        "- **What the community actually gets** (jobs × salary × years)\n"
        "- **Subsidy per permanent job** — if it exceeds \\$500K/job, the deal is bad\n\n"
        "Industry average: **\\$1.4M–\\$2.1M per permanent job** in subsidies. "
        "For comparison, manufacturing subsidies average \\$50K–\\$200K per job."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ================================================================== #
    # SECTION 10 — Consulting CTA / Intake
    # ================================================================== #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🤝 Need expert help negotiating?")
    st.markdown(
        "The tools above give you the data. But going up against a \\$2B developer "
        "with a team of lawyers is different from reading a checklist. "
        "**GridWatch Consulting** works directly with communities to negotiate "
        "CBAs, data dividends, and grid equity protections — and we only get "
        "paid when you win."
    )

    wh1, wh2, wh3 = st.columns(3)
    with wh1:
        with st.container(border=True):
            st.markdown("**📊 Custom impact analysis**")
            st.markdown(
                "We model the real energy, water, and grid strain of the "
                "proposed facility using your local utility data — not the "
                "developer's projections."
            )
    with wh2:
        with st.container(border=True):
            st.markdown("**📜 CBA drafting & review**")
            st.markdown(
                "We customize model clauses for your state's laws, "
                "set negotiation anchors using our Data Dividend Calculator, "
                "and review developer proposals for gaps."
            )
    with wh3:
        with st.container(border=True):
            st.markdown("**🎤 Hearing support**")
            st.markdown(
                "Expert testimony at planning commission and zoning "
                "board hearings, backed by data the developer can't dispute."
            )

    st.info(
        "**Success-fee model:** We believe communities shouldn't pay upfront "
        "to defend their own resources. Our fee is a small percentage of the "
        "community benefits we help you win — if we don't deliver results, "
        "you don't pay. Initial consultations are always free."
    )

    st.markdown("---")
    st.markdown("#### Request a free consultation")

    consult_col1, consult_col2 = st.columns(2)
    with consult_col1:
        contact_name = st.text_input(
            "Your name", key="consult_name",
            placeholder="Jane Smith",
        )
        contact_email = st.text_input(
            "Email", key="consult_email",
            placeholder="jane@example.com",
        )
        community_name = st.text_input(
            "Community / municipality", key="consult_community",
            placeholder="e.g. Springfield Township, OH",
        )
    with consult_col2:
        developer_name = st.text_input(
            "Developer (if known)", key="consult_developer",
            placeholder="e.g. Meta, Google, QTS, unknown",
        )
        facility_size = st.selectbox(
            "Proposed facility size",
            ["Not sure yet", "Under 50 MW", "50–200 MW", "200–500 MW", "500+ MW"],
            key="consult_size",
        )
        timeline = st.selectbox(
            "Where are you in the process?",
            [
                "Just heard about the proposal",
                "Public comment period open",
                "Zoning / planning hearing scheduled",
                "Negotiating terms with developer",
                "Already approved — want to reopen terms",
            ],
            key="consult_timeline",
        )

    situation = st.text_area(
        "Tell us about your situation",
        key="consult_situation",
        placeholder="What's happening in your community? What are your biggest concerns "
                    "(water, noise, grid strain, tax giveaways)? Any upcoming deadlines?",
        height=120,
    )

    if st.button("📨 Request free consultation", type="primary", key="consult_submit"):
        if not contact_name or not contact_email or not community_name:
            st.error("Please fill in your name, email, and community name.")
        else:
            st.success(
                f"**Thank you, {contact_name}!** We'll reach out within 48 hours "
                f"to schedule your free consultation about the situation in "
                f"**{community_name}**. Check your inbox at **{contact_email}**."
            )
            st.balloons()
            st.caption(
                "In the meantime, use the calculator and model clauses above to "
                "start preparing. The more you know before we talk, the stronger "
                "your position."
            )

    st.markdown("</div>", unsafe_allow_html=True)

    # ================================================================== #
    # Footer
    # ================================================================== #
    st.caption(
        "This toolkit is educational, not legal advice. Consult a local attorney "
        "before entering negotiations. Model clauses are drawn from real-world "
        "CBAs and legislative frameworks. See the **Methodology** tab for sources."
    )
