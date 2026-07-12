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
    # SECTION 1b — Residential vs. Commercial vs. Industrial
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🏠🏢🏭 Three customers, three completely different bills")
    st.markdown("""\
Residential, commercial, and industrial customers all pay for the same
grid — but the way costs show up on their bills is radically different.
Understanding this gap is key to seeing why data center growth hits
homeowners hardest.
""")

    r_col, c_col, i_col = st.columns(3)
    with r_col:
        st.markdown("""\
### 🏠 Residential
**You get a blended rate and no demand meter.**

- Billed almost entirely on **kWh consumed** — a flat or tiered cents-per-kWh
  rate that bundles energy, capacity, and T&D into one number
- **No demand charge** on most residential tariffs — you never see a $/kW
  line item
- Capacity costs are **socialized** into your per-kWh rate or added as a
  small rider/surcharge — you pay them, but you can't see them or manage them
- No interval meter in most homes — your utility records total monthly usage,
  not *when* you used it
- **You have almost zero visibility or control** over the capacity costs
  embedded in your bill
""")
    with c_col:
        st.markdown("""\
### 🏢 Commercial
**You get a demand meter and a separate $/kW charge.**

- Billed on **kWh consumed** *plus* a **demand charge** ($/kW) based on your
  highest 15-minute peak during the billing period
- The demand charge is a **visible line item** — an office building can see
  that its peak hit 450 kW on a Tuesday afternoon and that cost $6,750
- Smart building managers actively **shave peaks** — staggering HVAC startups,
  dimming lights, shedding non-critical loads — to reduce their demand charge
- Capacity and transmission costs show up separately, not bundled
- **Demand charges are typically 30–50%** of a commercial bill
""")
    with i_col:
        st.markdown("""\
### 🏭 Industrial (including data centers)
**You negotiate custom rates and manage demand in real time.**

- Very large loads (1 MW+) often get **negotiated tariffs** or special rate
  schedules with discounted energy rates in exchange for high load factor
- Explicit **demand charges** ($/kW) based on monthly or annual peak, plus
  separate capacity and transmission charges
- Many have **interval meters** logging demand every 5–15 minutes, and
  dedicated energy managers monitoring load curves
- Some negotiate **interruptible rates** — lower prices in exchange for
  agreeing to curtail during grid emergencies (though data centers rarely
  accept these)
- **Data centers** typically draw 50–300+ MW at 95%+ load factor, making
  them the largest single loads on most utility systems
""")

    st.markdown("""\
### The asymmetry that drives the problem
""")

    st.markdown("""\
| | Residential | Commercial | Industrial / Data Center |
|---|---|---|---|
| **Sees demand charges?** | No — buried in kWh rate | Yes — explicit $/kW line item | Yes — negotiated and managed |
| **Has a demand meter?** | Rarely (smart meters are spreading) | Yes — 15-min interval | Yes — 5-15 min interval |
| **Can manage peak usage?** | Barely — no real-time signal | Yes — building automation | Yes — dedicated energy team |
| **Capacity cost allocation** | Socialized across all ratepayers | Partially based on individual peak | Negotiated; often discounted for high load factor |
| **Benefits from curtailment?** | No direct savings | Yes — lower demand charge | Yes — but won't do it (SLAs) |
| **Typical monthly bill** | $150–250 | $5,000–50,000 | $500,000–5,000,000+ |
""")

    st.error(
        "**The core inequity:** Industrial customers like data centers have dedicated "
        "demand meters, energy management teams, and negotiated rates that let them "
        "optimize their costs. Residential customers have none of these tools — yet "
        "when data center growth drives up system-wide capacity costs, those costs are "
        "socialized into the blended per-kWh rate that homeowners pay. The customers "
        "with the *least* ability to respond bear a disproportionate share of the cost "
        "caused by the customers with the *most* ability to respond."
    )

    with st.expander("How this works in different market structures"):
        st.markdown("""\
The mechanism varies by region, but the outcome is similar everywhere:

**Deregulated markets (PJM, ISO-NE, NYISO)** — Capacity is procured through
auctions. The cost is allocated to utilities based on their total load during
system peak hours, then passed through to customers. Residential customers see
it as a line item ("generation capacity charge") or bundled into the default
service rate. C&I customers see explicit demand and capacity charges and can
manage them.

**Regulated/vertically integrated markets (Duke, Southern Company, Entergy)** —
No separate capacity market. The utility owns generation and recovers costs
through base rates set in rate cases. When the utility builds new capacity to
serve data center growth, the capital is rate-based and recovered from *all*
customers through higher per-kWh rates. C&I customers still have demand charges
on their tariff; residential customers just see a rate increase.

**ERCOT (Texas)** — No capacity market at all. Texas uses an "energy-only"
market where scarcity pricing during peak hours is supposed to incentivize
generation investment. Residential customers on variable-rate plans are directly
exposed to wholesale price spikes (which is why bills exploded during Winter
Storm Uri). C&I customers with fixed contracts are partially insulated. Data
centers can negotiate bilateral PPAs that lock in low prices, shifting scarcity
cost to the remaining pool.

**In all three structures**, the pattern holds: large industrial loads have
tools, tariffs, and negotiating power to manage their exposure. Residential
customers absorb socialized costs with no visibility and no control.
""")

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
    # SECTION 2b — How wholesale MW charges land on your residential bill
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🧮 How wholesale MW charges actually land on your bill")
    st.markdown("""\
The capacity auction clears at **$269.92 per MW-day**. But you're not a power
plant and you don't buy megawatts. So how does a wholesale market price end up
on your residential bill? Through a chain of translations:
""")

    h1, h2 = st.columns(2)
    with h1:
        st.markdown("""\
#### Step 1: Your utility buys capacity in bulk

Your utility (Pepco, Duke, AEP, ComEd, etc.) is obligated to procure enough
capacity to cover every customer's share of the system peak — plus a reserve
margin. It buys this capacity at the auction price and the total cost enters
its **revenue requirement** — the amount it needs to collect from all
customers combined.

For a utility serving 1 million homes in PJM, the 2025/26 auction cost
roughly **$800 million to $1.2 billion** in capacity obligations alone —
before a single electron flows.

#### Step 2: The cost is allocated to you via your "capacity tag"

In PJM, every customer gets a **Peak Load Contribution (PLC)** — also called
a "capacity tag." It's your usage during the **five highest-demand hours**
of the prior summer (the "5 CP" hours), averaged together.

If you ran your AC hard on those specific afternoons, your PLC is high and
you carry a bigger share of the capacity cost. If you were away on vacation,
your tag is lower. Most residential customers have **no idea** which hours
set their tag — the utility doesn't alert you in advance.
""")
    with h2:
        st.markdown("""\
#### Step 3: It shows up as a line item — or it's buried

How the capacity cost actually appears on your bill depends on your utility
and state:

| How it shows up | Example utilities |
|----------------|-------------------|
| **Explicit "capacity" or "generation capacity" line item** | Pepco (DC/MD), BGE, PECO — deregulated markets where supply and delivery are separated |
| **Bundled into "supply charges" per kWh** | Duke Energy, Dominion, Southern Company — regulated utilities that roll capacity into a blended rate |
| **"Default service" rider or surcharge** | ComEd, PPL — appears as a separate rider that changes when auction prices change |
| **Invisible — embedded in base rate** | Many rural co-ops and munis that set rates annually |

In deregulated states, when the PJM capacity auction price jumps, you'll see
it directly: Pepco customers got a separate notice in spring 2025 that their
capacity charge was increasing by ~$10/month. In regulated states, the same
cost flows through the next rate case — it's delayed, but it still arrives.

#### Step 4: Peak-period pricing (if your utility uses it)

Some utilities go further with **time-of-use (TOU)** rates that charge more
during peak hours (typically 2–7 PM on summer weekdays). This is designed to
incentivize you to shift usage — run the dishwasher at night, pre-cool the
house in the morning — but it also means your bill is directly affected by
*when* you use power, not just *how much*.
""")

    st.markdown("""\
#### A worked example: the PJM capacity cost on a typical home
""")

    ex1, ex2, ex3 = st.columns(3)
    with ex1:
        st.metric("Typical residential PLC", "2.5 kW",
                  help="Average capacity tag for a home with central AC in PJM")
        st.caption("Your share of the system peak")
    with ex2:
        st.metric("2024/25 capacity cost", "$2.20/month",
                  help="2.5 kW × $28.92/MW-day × 30.4 days ÷ 1000")
        st.caption("Before the price jump")
    with ex3:
        st.metric("2025/26 capacity cost", "$20.50/month",
                  help="2.5 kW × $269.92/MW-day × 30.4 days ÷ 1000",
                  delta="+$18.30/month", delta_color="inverse")
        st.caption("After the 833% auction increase")

    st.markdown("""\
That **$18.30/month increase** — about **$220/year** — is entirely from the
capacity market. Your usage didn't change. Your appliances didn't change.
The *grid's obligation* changed because total system peak demand grew, driven
largely by data center load, and the price of securing enough generation to
meet that peak went up accordingly.
""")

    st.info(
        "**What you can do:** In PJM territory, your capacity tag is set by your "
        "usage during the ~5 hottest summer afternoons. If you can reduce AC usage "
        "during **2–6 PM on the hottest weekdays in July/August** — by pre-cooling, "
        "raising the thermostat, or using a smart thermostat's demand-response mode — "
        "you can lower your PLC and reduce your share of capacity costs for the "
        "following year. Some utilities offer **peak-time rebate** programs that pay "
        "you $1–2/kWh for reducing usage during these critical hours."
    )
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
    # SECTION 4b — Why don't data centers voluntarily curtail?
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🚫 Why don't data centers voluntarily curtail?")
    st.markdown("""\
If cutting load for just 44 hours a year could save $150 billion in grid
costs, why aren't data center operators lining up to do it? The barriers are
real — but they're business and contractual, not technical.
""")

    b1, b2 = st.columns(2)
    with b1:
        st.markdown("""\
### 💰 The financial incentives are misaligned

**They don't pay the costs they cause.** When a data center drives up the
system peak, the resulting capacity charges are spread across *all*
ratepayers — residential, commercial, and industrial alike. The data center
pays its share, but the *incremental* cost it imposes on the system is
socialized. There's no price signal telling the operator "your load during
this hour just cost the grid $50 million in capacity obligations."

**Curtailment has a cost; the status quo is free.** Under current rate
structures, a data center that curtails during peak hours saves nothing
extra on its own bill — the capacity charges are set by auction results
months in advance, not by real-time behavior. Meanwhile, every hour of
curtailment risks SLA penalties, lost revenue, and reputational damage.

**The math is simple:** the operator bears 100% of the curtailment cost
and captures almost none of the grid-wide savings.
""")
    with b2:
        st.markdown("""\
### 📋 Uptime SLAs are contractually sacred

Cloud and colocation contracts guarantee **99.99–99.999% uptime** ("four
nines" to "five nines"). Five-nines uptime means a maximum of **5.26 minutes
of downtime per year** — total.

Even the Duke study's modest 44-hour curtailment would require renegotiating
these contracts from scratch. For hyperscalers serving enterprise customers,
any voluntary curtailment — even partial load reduction — triggers:

- **SLA breach penalties** (often millions of dollars per incident)
- **Customer churn risk** (enterprises won't tolerate unreliable cloud)
- **Competitive disadvantage** (if AWS curtails but Azure doesn't, customers
  move)
- **Insurance and liability exposure** (downtime in financial, healthcare,
  or government workloads has legal consequences)

The irony: AI *training* workloads are actually quite flexible — a training
run can pause and resume. But operators bundle training and inference on
shared infrastructure and apply the strictest SLA to everything.
""")

    st.markdown("""\
### 🏛️ No regulatory mandate, no market mechanism

Unlike power plants, which are required to bid into capacity markets and can
be penalized for non-performance, **data centers have no obligation to
participate in demand response**. They are treated as ordinary load — they
simply consume what they want, when they want.

Several mechanisms *could* change this but don't exist yet at scale:
""")

    st.markdown("""\
| Missing mechanism | Why it matters |
|------------------|---------------|
| **Marginal capacity pricing** | Current rates charge average cost, not the marginal cost a new load imposes. If data centers paid the true incremental capacity cost of their peak-hour consumption, curtailment would become profitable overnight. |
| **Interruptible tariffs with teeth** | Some utilities offer interruptible rates, but participation is voluntary and discounts are too small to offset SLA risk. Making participation mandatory above a load threshold (e.g., 10+ MW) would change the calculus. |
| **Behind-the-meter flexibility markets** | Data centers could bid their flexible workloads (training, batch processing, backups) into demand response markets, earning revenue for curtailment. PJM and ERCOT are exploring this but adoption is minimal. |
| **Differentiated SLAs for AI training** | Separating training (flexible, delay-tolerant) from inference (latency-critical) would let operators curtail training load without touching customer-facing services. This requires both technical workload separation and new contract structures. |
""")

    st.error(
        "**The core problem in one sentence:** Data centers externalize peak-load "
        "costs onto all ratepayers, face no regulatory requirement to curtail, and "
        "have financial incentives that reward consuming as much power as possible "
        "at all hours — even when the grid is at its breaking point."
    )
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
| Duke Nicholas Institute | ["Curtailment-Enabled Headroom: Flexible Large Loads and Grid Integration"](https://nicholasinstitute.duke.edu/publications/curtailment-enabled-headroom-how-flexible-large-loads-can-accelerate-decarbonization) | Feb 2025 |
| Lawrence Berkeley National Lab | ["2024 United States Data Center Energy Usage Report"](https://eta.lbl.gov/publications/2024-united-states-data-center-energy) | Jan 2025 |
| Harvard Belfer Center | ["AI, Data Centers, and the U.S. Electric Grid: A Watershed Moment"](https://www.belfercenter.org/publication/ai-data-centers-and-us-electric-grid) | Feb 2026 |
| E3 / Amazon | ["Tailored for Scale: Designing Electric Rates for Large Loads"](https://www.ethree.com/wp-content/uploads/2025/01/Tailored-for-Scale-Report.pdf) | Dec 2025 |
| Columbia University | ["Grid-Enhancing Technologies and Data Center Demand Response"](https://energypolicy.columbia.edu/publications/grid-enhancing-technologies/) | 2025 |
| UC Berkeley Energy Institute | ["What Will Data Centers Do To Your Electric Bill?"](https://energyathaas.wordpress.com/2025/09/08/what-will-data-centers-do-to-your-electric-bill/) | Sep 2025 |
| PJM Interconnection | [Market Monitor Reports on Capacity Auction Results](https://www.monitoringanalytics.com/reports/Reports/2025.shtml) | 2025–2026 |
| IEEFA | ["Projected Data Center Growth Spurs PJM Capacity Prices by Factor of 10"](https://ieefa.org/resources/projected-data-center-growth-spurs-pjm-capacity-prices-factor-10) | 2025 |
| Utility Dive | ["Data Centers Were 40% of PJM Capacity Costs in Last Auction"](https://www.utilitydive.com/news/data-centers-pjm-capacity-auction-cost/742851/) | 2026 |
| DOE | ["Clean Energy Resources to Meet Data Center Electricity Demand"](https://www.energy.gov/policy/articles/clean-energy-resources-meet-data-center-electricity-demand) | 2025 |
| FERC | [Order 2023 — Interconnection Queue Reform](https://www.ferc.gov/media/e-1-rm22-14-000) | 2023 |
""")
    st.markdown("</div>", unsafe_allow_html=True)

    st.caption(
        "Sources: Duke Nicholas Institute (2025), LBNL (2025), PJM Market Monitor "
        "(2025–2026), E3/Amazon (2025), Harvard Belfer Center (2026), UC Berkeley "
        "Energy Institute (2025). See **📚 Methodology** tab for full citations."
    )
