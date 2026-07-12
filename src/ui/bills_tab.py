"""
Bills tab — explains what drives utility bills up, how capacity charges and
peak loads work, and what academic research says about data center load
flexibility and ratepayer impacts.
"""

import streamlit as st


def render_bills_tab():
    st.subheader("💡 Your Utility Bill — What's Actually Driving It Up?")
    st.caption(
        "A plain-language explainer on how electricity bills work, why peak demand "
        "matters so much, and what the latest research says about data centers, "
        "curtailment, and ratepayer cost shifts."
    )

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 1 — Anatomy of your electric bill
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🧾 Anatomy of your electric bill")
    st.markdown("""\
Most people think they pay one rate for electricity. In reality, your bill is
built from **several distinct charges** — and the ones you've never heard of are
often the ones growing fastest.
""")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""\
### ⚡ Energy charges
**What you use** — measured in kilowatt-hours (kWh).

This is the part most people understand: run the AC more, pay more. It's
priced per kWh and reflects the actual fuel and generation cost of the
electricity you consumed.

Typically **40–60%** of a residential bill.
""")
    with col2:
        st.markdown("""\
### 📈 Demand / capacity charges
**What the grid must be ready to deliver** — measured in kilowatts (kW).

Your utility must maintain enough power plants, transformers, and wires
to handle the *highest moment of demand* all year — even if that peak lasts
only a few hours. Those standby costs are spread across all ratepayers as
**capacity charges**.

Typically **15–30%** of a residential bill, but growing fast.
""")
    with col3:
        st.markdown("""\
### 🔌 Transmission & distribution (T&D)
**Moving power from the plant to your home.**

Wires, substations, poles, and underground cables all cost money to build
and maintain. When big new loads (like data centers) require grid upgrades,
those costs flow into T&D charges for *everyone* on that utility system.

Typically **20–30%** of a residential bill.
""")

    st.info(
        "**Key insight:** You don't just pay for the electricity you *use* — you "
        "also pay for the infrastructure that must *exist* to serve the highest "
        "moment of demand. That's why peak load matters so much."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 2 — Peak load: why the hottest afternoon sets your bill
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🌡️ Peak load: why the hottest afternoon sets your annual bill")
    st.markdown("""\
Electricity can't be stored cheaply at scale (yet). So utilities must have
**enough generation and transmission to meet the single highest hour of demand
each year** — typically a sweltering summer afternoon when every AC unit runs
full blast simultaneously.
""")

    p1, p2 = st.columns(2)
    with p1:
        st.markdown("""\
#### How the peak drives costs
1. **Capacity obligation** — The grid operator (PJM, ERCOT, ISO-NE, etc.)
   runs an auction years in advance to ensure enough power plants *commit* to
   being available during peak. Those commitments cost money whether or not
   the plants actually run.
2. **Peaker plants** — Natural gas "peaker" plants that run only 50–200 hours
   per year but must be maintained year-round. Their per-MWh cost is enormous
   because their fixed costs are spread over very few hours.
3. **Transmission upgrades** — Wires are sized for the peak, not the average.
   Building for a 2 GW peak instead of a 1.5 GW peak can mean billions in
   new substations, lines, and right-of-way.
""")
    with p2:
        st.markdown("""\
#### The "coincident peak" trap
Many utilities set your capacity charge based on your usage during the **system
coincident peak (CP)** — the single highest-demand hour across the whole grid
that year.

If a large new load (like a data center) raises the system peak, *every*
customer's capacity allocation increases. This is the mechanism through which
data center growth can raise rates for *all* customers, even those whose own
usage didn't change.

**In PJM (the largest US grid operator):**
- The 2025/26 capacity auction price jumped **833%** — from $28.92 to
  $269.92 per MW-day.
- Data centers were responsible for **63%** of that price increase.
- Average residential bills rose **$15–21/month** from capacity costs alone
  in affected zones (Pepco, AEP, FirstEnergy).
""")

    st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 3 — How data centers specifically affect your bill
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🏗️ How data centers specifically affect your bill")
    st.markdown("""\
Data centers draw **large, constant loads** — often 50–300+ MW per campus,
running 24/7. Here's how that translates into bill impacts for residential
customers:
""")

    st.markdown("""\
| Mechanism | How it works | Estimated impact |
|-----------|-------------|-----------------|
| **Capacity market costs** | Data center load growth forces utilities to procure more generation capacity at auction. Costs are socialized across all ratepayers. | +$15–21/month in PJM zones (2025/26) |
| **Transmission upgrades** | New substations, high-voltage lines, and interconnections to serve data center campuses. Costs are rate-based and recovered from all customers. | $3–7B in planned upgrades in Northern Virginia alone |
| **Rate case increases** | Utilities file rate cases to recover the capital invested in serving new large loads. All customers share the revenue requirement. | Residential rates up 6% nationally in 2025 (2× inflation) |
| **Reduced reserve margins** | Rapid load growth without matching new generation tightens supply, raising wholesale energy prices for everyone. | PJM wholesale prices up 76% (2026 delivery year) |
| **Stranded asset risk** | If data center load doesn't materialize as projected, ratepayers may still pay for overbuilt infrastructure. | Under investigation by multiple PUCs |
""")

    st.warning(
        "**The counterargument:** Industry-funded studies (notably E3/Amazon, Dec 2025) "
        "argue that data centers generate *surplus* utility revenue — paying more than "
        "their cost to serve — which should benefit other ratepayers. However, critics "
        "note these studies assume full build-out and don't account for the capacity market "
        "externalities and transmission costs borne by all customers."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 4 — Duke University study: curtailment-enabled headroom
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 📚 Key Research: Duke University — Data Center Load Flexibility")
    st.markdown("""\
In February 2025, the **Nicholas Institute for Energy, Environment &
Sustainability at Duke University** published a landmark study led by
**Tyler Norris** introducing the concept of *curtailment-enabled headroom*.
""")

    st.markdown("### Core finding")
    st.markdown("""\
> The existing U.S. power grid could accommodate **up to 98 GW** of new large
> loads — more than all data centers use globally today — if those loads agree
> to curtail usage during just **0.5% of annual hours** (≈44 hours/year on
> average, with a maximum of 177 hours in the most constrained regions).
""")

    d1, d2, d3 = st.columns(3)
    with d1:
        st.metric("Grid headroom (with flexibility)", "98 GW",
                  help="New load the existing grid can absorb with 0.5% curtailment")
        st.caption("More than global DC demand today")
    with d2:
        st.metric("Curtailment needed", "0.5%",
                  help="Fraction of annual hours where load must reduce")
        st.caption("≈44 hours/year avg, 177 hrs max")
    with d3:
        st.metric("Potential savings", "$150B+",
                  help="Avoided generation and transmission investment")
        st.caption("By using existing capacity instead of building new")

    st.markdown("""\
### Why this matters for your bill

If data centers participate in **demand response** — briefly reducing load
during the handful of hours each year when the grid is most stressed — the
need for expensive new peaker plants and transmission disappears. That means
the capacity costs driving up your bill could be *dramatically* reduced.

**The catch:** Most data center operators currently refuse curtailment because
of strict uptime SLAs (service-level agreements). The Duke study shows the
technical potential is there — the barrier is contractual and commercial, not
engineering.
""")

    with st.expander("Study details and methodology"):
        st.markdown("""\
- **Scope:** 22 of the largest U.S. balancing areas (covering ~80% of demand)
- **Method:** Production cost modeling with incremental load additions and
  curtailment constraints
- **Key innovation:** The "curtailment-enabled headroom" metric — how much
  load can be added before reliability standards are violated, given a
  specified curtailment rate
- **Result:** At 0.5% curtailment, headroom ranges from 2–15 GW per
  balancing area, totaling ~98 GW nationally
- **Comparison:** Existing demand response programs already curtail at
  comparable rates (FERC Order 2222 resources average 1–3% curtailment)

**Source:** Norris, T. et al. (2025). "Curtailment-Enabled Headroom: How
Flexible Large Loads Can Accelerate Grid Integration." Nicholas Institute
for Energy, Environment & Sustainability, Duke University.
""")

    st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 5 — More academic and industry research
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🔬 Additional Research & Literature")

    st.markdown("### Lawrence Berkeley National Lab (LBNL) — 2024 Data Center Energy Report")
    st.markdown("""\
The U.S. DOE's flagship assessment of data center electricity demand, published
January 2025 (covering 2024 data):

- U.S. data center electricity climbed from **58 TWh (2014)** to **176 TWh (2023)**
- Projected **325–580 TWh by 2028** (6.7–12% of total U.S. electricity)
- Demand growth has **tripled over the past decade** and is projected to double
  or triple again by 2028
- In some regions, AI-driven demand is outpacing available capacity, forcing
  companies to install inefficient on-site generators

**Reliability incident (Jul 2024):** A voltage fluctuation in Northern Virginia
triggered simultaneous disconnection of 60 data centers, causing a 1,500 MW
surplus that required emergency grid adjustments to prevent cascading outages.
""")

    st.markdown("### Harvard Belfer Center — AI, Data Centers, and the U.S. Electric Grid (2026)")
    st.markdown("""\
A comprehensive policy analysis characterizing AI-driven load growth as a
"watershed moment" for grid planning:

- Traditional load forecasting methods are failing because AI demand is
  growing faster than any historical precedent
- Regional concentration of data centers creates localized reliability risks
  that national statistics obscure
- Recommends mandatory demand response participation for large loads and
  reformed interconnection processes
""")

    st.markdown("### E3 / Amazon — Tailored for Scale (Dec 2025)")
    st.markdown("""\
An industry-funded study examining whether data centers raise rates for other
customers:

- Studied Amazon facilities across 4 utility territories (PG&E, Umatilla,
  Dominion, Entergy)
- Found data centers generate **$3.4M surplus revenue** per 100 MW facility
  (2025), rising to $6.1M by 2030
- Concludes data centers are net contributors, not subsidized

**Important context:** This study was commissioned by Amazon and examines
individual facilities in isolation. It does not model the *system-wide* capacity
market and transmission effects that PJM's market monitor attributes to data
center growth. The two findings are not contradictory — a facility can pay more
than its direct cost-to-serve while still driving up system-wide capacity costs
that are socialized to all ratepayers.
""")

    st.markdown("### Columbia / Grid-Enhancing Technologies (GETs) Study (2025)")
    st.markdown("""\
Research from Columbia University examining near-term solutions:

- **Grid-enhancing technologies** (dynamic line ratings, power flow controllers,
  topology optimization) could release 20–40% more capacity from existing
  transmission without new construction
- Combined with demand response, GETs could ease electricity price pressure
  from data centers in the near term (2025–2030)
- Estimated to defer $10–30B in transmission investment nationally
""")

    st.markdown("### UC Berkeley Energy Institute — What Will Data Centers Do To Your Electric Bill? (2025)")
    st.markdown("""\
An independent academic analysis of the rate impact question:

- Investor-owned utilities sought **$18 billion in rate increases** in 2025 —
  the most since the mid-1980s
- Residential electricity prices rose 6% in nominal terms (2× inflation)
- Capacity market costs are the fastest-growing component of bills in RTO
  markets, with data centers identified as the primary demand driver
- Recommends that large loads bear their full cost of service including
  *marginal* capacity and transmission costs, not just embedded average costs
""")
    st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 6 — What can be done?
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🛠️ What can be done? Policy and market solutions")

    st.markdown("""\
| Solution | How it helps | Status |
|----------|-------------|--------|
| **Mandatory demand response** | Require data centers to curtail during peak hours, reducing need for new peaker plants | Proposed in 5+ state legislatures (2026) |
| **Cost-causation rate design** | Charge large loads for the capacity and transmission they actually cause, rather than socializing costs | Under review at FERC; several PUCs investigating |
| **Grid-enhancing technologies** | Squeeze more capacity from existing wires via sensors and software | Deployed in pockets; DOE pushing broader adoption |
| **Load flexibility contracts** | Offer data centers lower rates in exchange for contractual curtailment rights | Duke, Dominion piloting programs |
| **On-site generation requirements** | Require large loads to provide their own backup/peaking capacity | Proposed in NC, VA, GA |
| **Interconnection reform** | Speed up queue processing; require deposits to prevent speculative capacity hoarding | FERC Order 2023 reforms underway |
| **Moratoriums & impact fees** | Pause construction until infrastructure catches up; charge impact fees to fund upgrades | 14+ states with active or proposed moratoriums |
""")

    st.success(
        "**The bottom line:** The Duke University research shows that the *technical* "
        "solution exists — brief, modest curtailment can avoid tens of billions in new "
        "infrastructure costs. The challenge is creating the regulatory and commercial "
        "frameworks to make data centers participate. Until then, residential ratepayers "
        "bear the cost of keeping the grid ready for loads that refuse to flex."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 7 — Further reading
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.expander("📖 Sources & further reading", expanded=False):
        st.markdown("""\
| Source | Title | Date |
|--------|-------|------|
| Duke Nicholas Institute | "Curtailment-Enabled Headroom: Flexible Large Loads and Grid Integration" | Feb 2025 |
| Lawrence Berkeley National Lab | "2024 United States Data Center Energy Usage Report" | Jan 2025 |
| Harvard Belfer Center | "AI, Data Centers, and the U.S. Electric Grid: A Watershed Moment" | Feb 2026 |
| E3 / Amazon | "Tailored for Scale: Designing Electric Rates for Large Loads" | Dec 2025 |
| Columbia University | "Grid-Enhancing Technologies and Data Center Demand Response" | 2025 |
| UC Berkeley Energy Institute | "What Will Data Centers Do To Your Electric Bill?" | Sep 2025 |
| PJM Interconnection | Market Monitor Reports on Capacity Auction Results | 2025–2026 |
| IEEFA | "Projected Data Center Growth Spurs PJM Capacity Prices by Factor of 10" | 2025 |
| Utility Dive | "Data Centers Were 40% of PJM Capacity Costs in Last Auction" | 2026 |
| DOE | "Clean Energy Resources to Meet Data Center Electricity Demand" | 2025 |
| FERC | Order 2023 — Interconnection Queue Reform | 2023 |
""")
    st.markdown("</div>", unsafe_allow_html=True)

    st.caption(
        "Sources: Duke Nicholas Institute (2025), LBNL (2025), PJM Market Monitor "
        "(2025–2026), E3/Amazon (2025), Harvard Belfer Center (2026), UC Berkeley "
        "Energy Institute (2025). See **📚 Methodology** tab for full citations."
    )
