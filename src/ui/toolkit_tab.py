"""
CBA Toolkit tab — actionable negotiation tools for communities facing
data center development. Calculators, model clauses, and real-world
examples to help towns extract maximum value.
"""

import streamlit as st
import pandas as pd


# ── Real-world CBA examples database ─────────────────────────────────────── #

_CBA_EXAMPLES = [
    {
        "community": "Cedar Rapids, IA",
        "operator": "Meta / Google",
        "year": 2023,
        "mw": 200,
        "investment_b": 2.4,
        "what_they_got": [
            "Annual community betterment fund payments ($200K+/yr)",
            "Local hiring commitments for construction",
            "Property tax abatement tied to job creation benchmarks",
        ],
        "lesson": "Tied incentives to measurable deliverables, not just promises.",
    },
    {
        "community": "Loudoun County, VA",
        "operator": "Multiple hyperscalers",
        "year": 2024,
        "mw": 3000,
        "investment_b": 50.0,
        "what_they_got": [
            "Data center property taxes fund ~32% of county budget",
            "Residential property tax rate among lowest in Virginia",
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
            "revenue stream tied to the facility's actual size. $500–$2,000/MW/year "
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
            "range from $5,000–$15,000 per MW."
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

    # ================================================================== #
    # SECTION 1 — The core principle
    # ================================================================== #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## The #1 rule: never approve without a contract")
    st.markdown(
        "A data center needs your land, your water, your power grid, and your "
        "community's approval. That is **leverage**. Once you approve, the leverage "
        "is gone. Every approval should be conditioned on a legally binding "
        "**Community Benefit Agreement (CBA)** that specifies exactly what the "
        "community gets, with enforcement mechanisms and penalties."
    )
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
            help="Industry average is $8–12M per MW for AI-ready facilities.",
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
        help="Emerging range is $500–$2,000/MW/year. Aim high.",
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
                    f"Typical range: ${clause['range_low']:,}–"
                    f"${clause['range_high']:,} {clause['unit']}"
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

    st.markdown(
        "Alaska's Permanent Fund takes a portion of oil revenue and pays an annual "
        "dividend to every resident. The same principle applies to data centers: "
        "they extract your community's **land, water, electricity, and grid capacity** "
        "— finite local resources — to generate billions in revenue."
    )

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
            f"**${annual_infra_fee/1e6:.2f}M/year** — or **${dividend_per_hh:,.0f} "
            f"per household per year** as a direct data dividend."
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # ================================================================== #
    # SECTION 6 — Grid Equity
    # ================================================================== #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## ⚡ Grid Equity Demands")
    st.markdown("#### Don't let them raise your electric bill")

    st.markdown(
        "When a data center draws 200+ MW from your local grid, the utility must "
        "build new substations, upgrade transmission lines, and sometimes delay "
        "retiring old fossil plants. Without protection, these costs are spread "
        "across **all ratepayers** — including you."
    )

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
    # SECTION 7 — Meeting prep checklist
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

    st.caption(
        "Print this page or take a screenshot. Every question the developer "
        "can't answer clearly is a reason to pause the approval."
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
