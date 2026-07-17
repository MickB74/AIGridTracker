"""
Blog content — curated stories and project narrative for the GridWatch AI blog tab.
Each story is a dict with: id, section, title, date, author, summary, body (markdown),
and optional tags. Sections: "stories" for reported pieces, "about" for project mission.
"""

import datetime as _dt

# ──────────────────────────────────────────────────────────────────────────────
# PROJECT / "ABOUT US" SECTION
# ──────────────────────────────────────────────────────────────────────────────

ABOUT_SECTION = {
    "title": "Our Mission",
    "tagline": "Transparency tools for the communities living next to AI infrastructure.",
    "body": """\
**GridWatch AI** exists because the people who live near data centers deserve the
same quality of information that the people who *build* them already have.

Every week a new hyperscaler or colocation developer files interconnection paperwork
for another 500 MW campus. Every week a local planning board holds a public hearing
where residents ask the same unanswered questions: *How much water will it use?
Will my electric bill go up? What happens to property values?*

We built this tracker to close that information gap:

- **Open coefficients, cited sources.** Every number on the Calculator and Methodology
  tabs links to the primary disclosure or peer-reviewed study it came from — IEA, Google,
  Epoch AI, ML.ENERGY, EPRI, EIA, PJM. Nothing is inferred or editorialized.
- **Live grid data, not marketing.** The Grid Timing and Data Centers tabs pull real-time
  generation mix and marginal emissions from the EIA-930 and PJM APIs so you can see the
  actual carbon intensity of the grid that powers a facility — not the clean-energy credits
  a company purchased months later.
- **Community voice, front and center.** The Community & Backlash tab aggregates local news
  and Reddit sentiment so the concerns of residents — noise, water draw, rate hikes,
  zoning fights — are as visible as a company's sustainability report.
- **Direct civic action.** The Officials tab puts every senator, representative, and
  governor one click away, with documented data-center stances where they exist. Select
  your state and the app surfaces the local controversies you can reference in your message.

This project is independent, unfunded, and open-source. It is not affiliated with any
cloud provider, data-center developer, or advocacy group. Our only agenda is that public
decisions should be informed by public data.

*— The GridWatch AI team*
""",
}

# ──────────────────────────────────────────────────────────────────────────────
# BLOG STORIES
# ──────────────────────────────────────────────────────────────────────────────

BLOG_STORIES = [
    # ── Morgan Stanley opposition analysis ──────────────────────────────────
    {
        "id": "morgan-stanley-opposition-bottleneck-2026",
        "section": "stories",
        "title": "Morgan Stanley Says Community Opposition Is the Biggest Threat to the Data Center Buildout. Are They Right?",
        "date": _dt.date(2026, 7, 15),
        "author": "GridWatch AI",
        "tags": ["Wall Street", "community opposition", "moratorium", "investment", "analysis"],
        "summary": (
            "Morgan Stanley warns that \\$156B in data center projects were canceled or "
            "delayed in 2025, with another \\$130B disrupted in Q1 2026 — driven by "
            "community resistance. We checked their thesis against our data."
        ),
        "body": """\
Morgan Stanley published an analyst note this week warning that community opposition
has become the single biggest bottleneck for AI data center expansion. Their numbers
are stark: **\\$156 billion** in data center projects were canceled or delayed during
2025, with another **\\$130 billion** disrupted in Q1 2026 alone.

We ran their thesis against everything we track. Here's where they're right, where
they're incomplete, and what it means for your community.

### The moratorium wave is real — and accelerating

Morgan Stanley cites Morning Consult survey data showing roughly **50% of Americans**
believe data centers will negatively impact electricity prices and the grid, with
**45%** worried about water costs and environmental damage. That's not fringe
sentiment. That's mainstream.

Our moratorium tracker tells the same story from the policy side. We now count
**50+ localities and four states** that have enacted, proposed, or considered data
center moratoriums or outright bans:

- **North Carolina** alone has 14+ local bans or moratoriums — from Brevard to
  Boone to Apex — plus proposed actions in Charlotte (deadlocked 5–5), Durham,
  and Fayetteville
- **New York** enacted the nation's first statewide moratorium (EO 62, July 2026)
  — a one-year freeze on facilities over 50 MW
- Cities as diverse as **Denver, Minneapolis, Baltimore, Reno, and Seattle** have
  enacted or proposed restrictions
- Even in developer-friendly states, individual counties are pushing back —
  **Hill County, TX** enacted a moratorium and is now being sued by the developer

A year ago, opposition was scattered. Today it's a coordinated national movement
with its own advocacy infrastructure.

### The dollar figures add up

Morgan Stanley's \\$156B disruption figure sounds enormous until you look at the
pipeline. Our mega-projects tracker alone shows **\\$300 billion+** in announced
hyperscale investment currently under construction:

| Project | Company | Investment | Capacity |
|---------|---------|-----------|----------|
| Stargate | OpenAI / Oracle / SoftBank | \\$100B+ | 1+ GW |
| West Texas campus | Google | \\$40B | Multi-GW |
| Meta Hyperion | Meta / Blue Owl | \\$27B | 2–5 GW |
| Vantage Frontier | Vantage | \\$25B | 1.4 GW |
| AWS Mississippi | Amazon | \\$25B | Multi-site |
| xAI Colossus | xAI | \\$20B | ~2 GW |

If even half this pipeline faces permitting delays, grid interconnection queues,
or community opposition, \\$156B in disruption is entirely plausible. These aren't
small-business permits being held up — each project represents a multi-year,
multi-gigawatt commitment that touches land use, water rights, grid capacity,
and ratepayer impacts.

### Where Morgan Stanley is right

**Opposition is a material constraint.** This is no longer a risk factor buried
in an S-1 filing. When 50% of the public thinks data centers will raise their
electric bills — and the PJM capacity auction just proved them right with an
833% price jump — the political environment for permitting has fundamentally
changed.

**On-site power is an obvious hedge.** Morgan Stanley identifies Bloom Energy,
Solaris Energy Infrastructure, and Innio as beneficiaries, and the logic is
sound. Behind-the-meter gas turbines and fuel cells let developers sidestep
both the grid interconnection queue and the community argument that "this
facility will raise my electric bill." If you can't connect to the grid, bring
your own.

**Data center REITs are somewhat insulated.** Digital Realty and peers operate
smaller, urban-edge facilities that draw less community ire than a 500 MW
hyperscale campus in a rural county. Morgan Stanley is right that the
opposition movement is primarily targeting hyperscale, not colo.

### Where they're incomplete

Morgan Stanley frames community opposition primarily as a **risk to total
investment** — implying the buildout might shrink. Our data suggests something
different: it's a **geographic reshuffling**, not a demand reduction.

Look at where the mega-projects are actually being built: Abilene, TX.
Richland Parish, LA. Shackelford County, TX. Northern Indiana. Rural
Mississippi. These are locations chosen specifically for low population
density, cheap land, available power, and — crucially — minimal organized
opposition.

Northern Virginia (Ashburn) has **4,900 MW operational** with **12,200 MW**
more in the pipeline. But new hyperscale capacity is increasingly fleeing
to places where the planning commission has three members, not thirty
concerned residents.

The capital isn't disappearing. It's following the path of least resistance
— literally.

### What this means for communities

**1. If a developer is courting your town, you have more leverage than you
think.** Morgan Stanley just told its institutional clients that community
opposition is the #1 risk to a \\$500 billion capital cycle. That's your
negotiating position stated in the language Wall Street understands.

**2. The window for negotiation is now.** Developers are racing to lock in
sites before the opposition movement matures further. If your county is
being approached, the CBA negotiation happens before the permit vote, not
after. Use the **Negotiation Toolkit** tab to prepare.

**3. Watch the geographic displacement.** If your state enacts restrictions
(as New York just did), neighboring states without protections will see an
influx. If you're in a state that hasn't acted, the developer may already
be scouting your county. Check the **Data Centers** tab to see what's in
your pipeline.

**4. "Canceled" doesn't always mean canceled.** Some of the \\$156B in
"disrupted" projects will resurface in new jurisdictions with new LLCs and
new permitting applications. Track the operators and their subsidiary
companies — our **Operators** registry lists the LLCs that hyperscalers
use so you can connect a new filing to its parent company.

### The bottom line

Is Morgan Stanley right? **Mostly, yes.** Community opposition is a real,
material constraint on the data center buildout — and the financial markets
are finally pricing it in.

But the deeper story is one they don't fully tell: the opposition isn't
killing the buildout, it's **democratizing** it. For the first time,
communities have enough organized power to demand a seat at the table
before the concrete is poured. New York's \\$1M/MW community benefit
benchmark, the proliferating moratoriums, the 50% public concern numbers
— these aren't obstacles to progress. They're the market correcting for
decades of data centers arriving with tax breaks and leaving communities
with the bill.

The question isn't whether the data centers get built. They will. The
question is whether your community gets a fair deal when they do.

> Use the **Negotiation Toolkit** tab to model community benefit agreements,
> the **Data Centers** tab to see what's in your region's pipeline, and the
> **States & Officials** tab to contact your representatives.
""",
    },
    # ── NY Moratorium ───────────────────────────────────────────────────────
    {
        "id": "ny-moratorium-eo62-2026",
        "section": "stories",
        "title": "New York Just Changed the Game: What EO 62 Means for Every Community Fighting a Data Center",
        "date": _dt.date(2026, 7, 15),
        "author": "GridWatch AI",
        "tags": ["moratorium", "New York", "policy", "EO 62", "community benefits", "breaking"],
        "summary": (
            "Governor Hochul signed the nation's first statewide data center moratorium "
            "on July 14 — a 1-year pause on 50+ MW facilities that sets a precedent for "
            "community negotiating power nationwide."
        ),
        "body": """\
On July 14, 2026, Governor Kathy Hochul signed Executive Order 62, making New York
the first state in the nation to impose a moratorium on new hyperscale data centers.
The order pauses state environmental permits for any facility drawing 50 megawatts or
more — effectively freezing the pipeline of large AI and cloud campuses for up to one
year.

This isn't a symbolic gesture. It's a structural shift in how states can respond to
the data center buildout.

### What the order actually does

**Permit freeze.** The Department of Environmental Conservation will not issue
discretionary permits for large data centers that haven't already been deemed complete.
Projects already in the approval pipeline with complete applications are grandfathered.

**Environmental standards.** The Department of Public Service will develop a Generic
Environmental Impact Statement (GEIS) — a uniform framework for evaluating a data
center's effect on energy demand, water use, water quality, and air quality. This
replaces the current ad hoc, project-by-project review.

**Community Investment Framework.** Within 60 days, Empire State Development must
publish a template that gives towns and counties a standardized playbook for
negotiating with developers. The preliminary recommendation is striking: **\\$1 million
per megawatt** as a starting point for developer contributions. A 200 MW facility
would begin negotiations at \\$200 million in community benefits.

**Labor standards.** Data center construction projects will face prevailing wage
requirements, project labor agreements, local hiring targets, and apprenticeship
mandates.

**Grid and ratepayer protection.** Hochul is separately pursuing a Grid Acceleration
Fund that would require data centers to pay into the state's aging power
infrastructure, and legislation to repeal sales tax exemptions that large facilities
currently enjoy.

### Why it happened

The numbers explain the urgency. As of May 2026, nearly **12 gigawatts** of proposed
data center demand was sitting in NYISO's interconnection queue — more than 8 GW
added during 2025 alone. For context, 12 GW is roughly equivalent to the output of
12 nuclear power plants.

Hochul framed the order as protecting New Yorkers from rising electricity bills,
strained water supplies, and a grid that wasn't built for this kind of load growth.
The political backdrop matters too: communities across upstate New York — from the
Hudson Valley to the Finger Lakes — had been pushing back against proposed campuses,
and several local moratoriums were already in place (Lysander, Perth, St. Lawrence
County).

### What it means for your community

Even if you're not in New York, EO 62 changes the landscape:

**1. The \\$1M/MW benchmark is now public.** Before this, communities negotiated in
the dark. The state of New York just told every planning board in America what a
megawatt of data center capacity is worth to the developer. Use it.

**2. The GEIS model is replicable.** Other states can adopt the same uniform
environmental review framework instead of letting each project define its own
scope of impact.

**3. Developers will route around.** Expect an acceleration of data center proposals
in states without moratoriums or strong environmental review — making it even more
important for those communities to be prepared with CBA demands before the developer
arrives.

**4. The moratorium is temporary.** One year. The real legacy is the regulatory
framework that comes out of it — the standards, the community benefit formula, and
the environmental review process. Watch what New York builds during this pause.

### What to do now

- **Read the executive order** in full:
  [EO 62 text](https://www.governor.ny.gov/executive-order/no-62-establishing-temporary-moratorium-data-centers-new-york-while-state-develops)
- **Use our Data Dividend Calculator** on the Negotiation Toolkit tab to model what
  the \\$1M/MW benchmark means for your specific facility
- **Download the Model CBA Clauses** and bring them to your next planning commission
  meeting — the NY framework validates every provision we recommend
- **Contact your state legislators** using the States & Officials tab if you want
  your state to follow New York's lead

The era of data centers arriving with no accountability is ending. New York just
proved that states can act — and communities should demand it.
""",
    },
    # ── Story 0 ──────────────────────────────────────────────────────────────
    {
        "id": "utility-bill-explainer-2026",
        "section": "stories",
        "title": "Why Your Electric Bill Is Going Up — and What Data Centers Have to Do With It",
        "date": _dt.date(2026, 7, 12),
        "author": "GridWatch AI",
        "tags": ["utility bills", "capacity markets", "PJM", "demand response", "research", "explainer"],
        "summary": (
            "Capacity charges, peak load auctions, and the coincident-peak trap: a "
            "plain-language guide to the parts of your electric bill you've never heard "
            "of — and why data center growth is making them explode."
        ),
        "body": """\
If your electricity bill has been climbing and you can't figure out why — you're
not using more power, you haven't added appliances — the answer is probably hiding
in a line item you've never looked at.

It's not the kilowatt-hours. It's the **capacity charges**.

### The part of your bill nobody explains

Most people think of electricity as a single rate: use more, pay more. In reality,
your bill has three major components, and the one growing fastest is the one almost
nobody understands:

| Component | What it pays for | Typical share | Growing? |
|-----------|-----------------|---------------|----------|
| **Energy charges** | The actual electricity you consumed (kWh) | 40–60% | Slowly |
| **Capacity charges** | Keeping enough power plants *available* to meet the highest hour of demand all year | 15–30% | **Fast** |
| **Transmission & distribution** | Wires, substations, and poles to move power from plant to home | 20–30% | Moderately |

The energy charge is intuitive — run the AC more, pay more. But capacity charges
are different. You pay them whether you use the power or not, because the grid must
maintain enough generation to handle the *worst-case peak* — even if that peak lasts
only a few hours each summer.

Think of it like a fire department: your taxes pay for fire stations that sit idle
most of the year, because they need to be there the one day your house catches fire.
Capacity charges are the grid's fire department. And right now, someone is building
a factory that requires its own fire station — and sending you part of the bill.

### The coincident peak trap

Here's where it gets personal. In most deregulated markets, your capacity charge
isn't based on *your* individual peak usage. It's based on your usage during the
**system coincident peak (CP)** — the single highest-demand hour across the entire
grid that year.

If a new 200 MW data center comes online in your utility's territory and raises the
system peak, *your* capacity allocation goes up even though your behavior didn't
change. The new load raises the waterline, and everyone pays more to keep the system
above it.

This isn't hypothetical. In PJM — the grid operator serving 65 million people across
13 states from New Jersey to Illinois — it just happened:

- The **2025/26 capacity auction** price jumped **833%** — from $28.92 to $269.92
  per MW-day
- PJM's independent market monitor found data centers were responsible for **63%**
  of that price increase
- **Pepco** customers in Washington D.C. saw bills rise **$21/month**, with roughly
  half attributable to capacity costs
- Across the PJM footprint, residential bills increased **$15–21/month** from
  capacity charges alone

That's not a rate increase driven by fuel costs, inflation, or your usage. It's a
rate increase driven by someone else's load.

### 44 hours that could save $150 billion

In February 2025, researchers at **Duke University's Nicholas Institute for Energy,
Environment & Sustainability** published a study that reframed the entire debate.
Led by Tyler Norris, the analysis introduced a concept called **"curtailment-enabled
headroom"** — how much new load the existing grid can absorb if that load agrees to
briefly reduce consumption during the handful of hours each year when the system is
most stressed.

The findings were striking:

- The existing U.S. grid could absorb **up to 98 GW** of new data center load —
  more than the world's entire current data center fleet
- The required curtailment: just **0.5% of annual hours** — an average of **44 hours
  per year**, with a maximum of 177 hours in the most constrained regions
- Potential avoided infrastructure cost: **$150 billion or more** in new power plants
  and transmission lines that wouldn't need to be built
- The curtailment rate is comparable to existing demand response programs that
  industrial customers already participate in

In plain English: if data centers agreed to dim the lights for less than two days a
year — spread across the summer's hottest afternoons — we wouldn't need to build
tens of billions of dollars in new infrastructure, and your capacity charges would
stay flat.

### So why don't they just do it?

This is the question everyone asks, and the answer reveals a structural failure in
how we regulate large electricity consumers.

**1. The costs they impose aren't the costs they pay.**

When a data center raises the system peak, the resulting capacity charges are
socialized across *all* ratepayers. The data center pays its share, but the
*incremental* system-wide cost it imposes — the billions in new capacity procurement
triggered by its load — is spread across millions of customers. There's no price
signal telling the operator: "Your consumption during this hour just cost the grid
$50 million in capacity obligations."

Under current rate design, a data center that curtails during peak hours saves almost
nothing on its own bill. The capacity auction was settled months ago; the price is
already set. Curtailment is a cost with no reward.

**2. Uptime SLAs are contractually sacred.**

Cloud and colocation contracts guarantee **99.99–99.999% uptime** — "four nines" to
"five nines." Five-nines means a maximum of **5.26 minutes of total downtime per
year**. The Duke study's 44-hour curtailment, even if it's just a partial load
reduction, would blow through any existing SLA by orders of magnitude.

Renegotiating these contracts means:
- SLA breach penalties (often millions per incident)
- Customer churn risk (if AWS curtails but Azure doesn't, customers switch)
- Insurance and liability exposure (financial, healthcare, and government workloads
  have legal uptime requirements)

Here's the irony: **AI training workloads are actually highly flexible**. A training
run can pause, checkpoint, and resume — it doesn't care about latency or real-time
availability. But operators run training and inference on shared infrastructure and
apply the strictest SLA to everything. Separating these workloads is technically
straightforward but commercially inconvenient.

**3. There's no regulatory mandate.**

Unlike power plants, which must bid into capacity markets and face penalties for
non-performance, **data centers have no obligation to participate in demand response**.
They're classified as ordinary load. They consume what they want, when they want, and
the grid must accommodate them.

Several mechanisms could change this but don't exist at scale:

- **Marginal capacity pricing** — charge new large loads for the *incremental* capacity
  cost they impose, not just the system average. If a 200 MW data center knew it would
  pay the full marginal cost of the capacity auction increase it triggered, curtailment
  would become profitable overnight.
- **Mandatory demand response above a threshold** — require any load above 10 MW to
  participate in curtailment programs, the way generators must participate in capacity
  markets.
- **Differentiated SLAs** — regulatory frameworks that distinguish delay-tolerant
  workloads (AI training, batch processing, backups) from latency-critical ones
  (inference, real-time services), enabling curtailment of the flexible portion without
  touching customer-facing services.

### The research landscape: what we know and what's contested

The Duke study didn't land in a vacuum. A growing body of academic and policy research
is wrestling with the same questions:

**Lawrence Berkeley National Lab (LBNL, Jan 2025)** found U.S. data center electricity
surged from 58 TWh (2014) to 176 TWh (2023) and projects **325–580 TWh by 2028** —
potentially 12% of all U.S. electricity. In July 2024, a voltage fluctuation in
Northern Virginia triggered simultaneous disconnection of 60 data centers, causing a
1,500 MW surplus that required emergency grid adjustments.

**The Harvard Belfer Center (Feb 2026)** called AI-driven load growth a "watershed
moment" for grid planning, noting that traditional forecasting methods are failing
because demand is growing faster than any historical precedent.

**E3, funded by Amazon (Dec 2025)**, studied four Amazon facilities and concluded data
centers generate **$3.4 million in surplus revenue** per 100 MW facility — paying more
than their direct cost to serve. This is the industry's primary counterargument to the
"ratepayers are subsidizing data centers" narrative.

**The critical nuance:** both things can be true simultaneously. A data center can pay
more than its direct cost-to-serve while *also* driving up system-wide capacity costs
that are socialized to everyone. E3's facility-level analysis and PJM's system-level
market monitor are measuring different things. The surplus at the meter doesn't capture
the externality at the auction.

**Columbia University (2025)** showed that grid-enhancing technologies (dynamic line
ratings, power flow controllers) could release 20–40% more capacity from existing
transmission — deferring $10–30 billion in new construction.

### What would actually fix this?

The research converges on a handful of structural reforms:

1. **Cost-causation rate design** — charge large loads for the capacity and transmission
   costs they *cause*, not the system average. FERC and several state PUCs are
   investigating this, but no major market has implemented it yet.

2. **Mandatory demand response for large loads** — if you consume more than 10 MW, you
   participate in curtailment programs, period. At least five state legislatures
   introduced versions of this in 2026.

3. **Load flexibility contracts** — utilities offer lower rates in exchange for
   contractual curtailment rights during peak hours. Duke Energy and Dominion are
   piloting programs, but participation is voluntary and uptake is low.

4. **Interconnection reform** — FERC Order 2023 is speeding up queue processing and
   requiring deposits to prevent speculative capacity hoarding, but implementation is
   slow.

5. **On-site generation requirements** — require large loads to provide their own
   peaking capacity (batteries, on-site generation) so the grid doesn't have to overbuild
   for them. Proposed in North Carolina, Virginia, and Georgia.

### The bottom line

The Duke University research proves the *technical* solution exists: brief, modest
curtailment — less than two days a year — could avoid tens of billions in new
infrastructure and keep your capacity charges from spiraling. The barrier isn't
engineering. It's a regulatory and commercial framework that lets the largest
electricity consumers externalize their peak-load costs onto everyone else's bill.

Until that framework changes, residential ratepayers bear the cost of keeping the
grid ready for loads that refuse to flex.

> **Explore more:** Use the **💡 Your Utility Bill** tab for an interactive breakdown
> of bill components, the **🕐 Grid Timing** tab to see real-time grid stress in your
> region, and the **🏛️ Officials** tab to contact your legislators about rate reform.
""",
    },
    # ── Story 1 ──────────────────────────────────────────────────────────────
    {
        "id": "moratorium-wave-2026",
        "section": "stories",
        "title": "The Moratorium Wave: Why 14 States Are Pressing Pause on Data Centers",
        "date": _dt.date(2026, 7, 8),
        "author": "GridWatch AI",
        "tags": ["policy", "moratoriums", "zoning", "community"],
        "summary": (
            "From Virginia's Loudoun County to rural Indiana, a rolling wave of moratorium "
            "bills and local zoning freezes is reshaping where the next generation of AI "
            "data centers can be built."
        ),
        "body": """\
In the first half of 2026, at least **14 US states** introduced or enacted legislation
to pause, restrict, or add conditions to new data-center construction. The trend marks
a dramatic shift from just two years ago, when states competed to *attract* hyperscale
campuses with generous tax abatements and expedited permitting.

### What changed?

Three pressure points converged:

1. **Electricity costs.** Dominion Energy's 2025 rate case in Virginia — where data
   centers consume roughly **25% of the state's electricity** — projected residential
   bill increases of 8–12% over five years to fund grid upgrades. Ratepayer groups
   organized, and the General Assembly responded with SB 1291, requiring cost-benefit
   analyses before new special-rate contracts.

2. **Water scarcity.** In Mesa, Arizona, and The Dalles, Oregon, municipal water
   audits revealed that a single hyperscale campus can draw **1–5 million gallons
   per day** for evaporative cooling — the equivalent consumption of a 10,000-home
   subdivision. Drought conditions amplified public anger.

3. **Grid reliability.** PJM Interconnection's 2026 load forecast showed a
   **+32 GW demand surge** by 2030, with 94% attributable to data centers. Reliability
   planners warned that generation retirements and transmission bottlenecks could force
   rolling curtailments if the pipeline isn't managed.

### The policy spectrum

Not every moratorium is the same. Virginia's SB 1291 adds transparency requirements
without banning construction. Indiana's HB 1382 imposes a **two-year freeze** on
projects exceeding 50 MW in counties below a population threshold. Georgia's approach
ties approvals to proof of dedicated renewable generation.

Good Jobs First tracks **37 active bills** across state legislatures. The Rockefeller
Institute notes that many are bipartisan, backed by both fiscal conservatives wary of
subsidies and progressives focused on environmental justice.

### What it means for communities

For residents living near proposed sites, the moratorium wave offers breathing room —
time to negotiate community-benefit agreements, demand noise and water-use disclosures,
and push for impact assessments *before* ground is broken rather than after.

For the industry, it signals that the era of frictionless expansion is over. The
companies that engage early, share operational data transparently, and invest in
genuine community benefit will find smoother paths than those that don't.

> Use the **Officials** tab to find your state legislators and their documented
> stances on data-center policy — and the **Community & Backlash** tab to see what
> residents in your area are already organizing around.
""",
    },
    # ── Story 2 ──────────────────────────────────────────────────────────────
    {
        "id": "hidden-water-cost",
        "section": "stories",
        "title": "The Hidden Water Cost of Your AI Query: What the Data Actually Shows",
        "date": _dt.date(2026, 7, 3),
        "author": "GridWatch AI",
        "tags": ["water", "energy", "research", "explainer"],
        "summary": (
            "A single ChatGPT query uses about 18 mL of water — roughly a medicine-cup "
            "pour. Multiply by billions of daily queries and the numbers start to matter, "
            "especially in water-stressed regions."
        ),
        "body": """\
When researchers at UC Riverside published *"Making AI Less Thirsty"* in early 2024,
the headline number — **a 500 mL bottle of water for every 20–50 ChatGPT responses** —
lit up social media. But the discourse quickly split into two camps: alarmists who
extrapolated to apocalyptic shortages, and industry voices who dismissed the figures
as rounding errors compared to agriculture.

The truth, as usual, is in the denominator.

### Where the water goes

Data-center water use has two components:

- **On-site (direct) cooling.** Evaporative cooling towers in hot climates consume
  water directly. Google reported a global average **Water Usage Effectiveness (WUE)**
  of 1.1 L per kWh of IT load in 2024. Microsoft reported 1.8 L/kWh. Meta was lower
  at 0.26 L/kWh, partly because of its colder-climate sites in Luleå and Clonee.

- **Off-site (indirect) water.** Thermoelectric power plants — coal, gas, and nuclear —
  withdraw enormous volumes for steam cooling. When a data center draws from a
  coal-heavy grid, the water embedded in its electricity can **dwarf** the water
  used on-site. The US Geological Survey estimates 1.5–2.0 L/kWh for coal generation.

GridWatch AI's **Calculator** tab accounts for both. When you enter a query
count and select a grid carbon intensity, the water estimate multiplies the energy
draw by a blended WUE factor that includes off-site generation water.

### Scale matters — but so does location

At the individual level, 18 mL per query is genuinely small. An average American uses
**300 liters per day** on showers, laundry, and irrigation. A hundred AI queries adds
1.8 L — less than a single toilet flush.

But data centers aren't evenly distributed. They cluster in **tax-advantaged, fiber-rich
corridors** — Northern Virginia, Central Texas, Phoenix metro, The Dalles — that don't
always align with water abundance. A campus drawing 3 million gallons per day in Goodyear,
Arizona hits differently than the same facility in upstate New York.

### What you can do with this information

The point isn't to stop using AI. It's to ensure that:

1. **Developers disclose water use** at the facility level, not just global averages.
2. **Planning boards require water-impact assessments** before approving new campuses
   in drought-prone regions.
3. **Grid operators account for indirect water** when modeling the full resource cost
   of new data-center loads.

> Explore the **Calculator** tab to see the water footprint of your own AI usage,
> and the **Grid Timing** tab to understand how the generation mix in your region
> affects both carbon *and* water.
""",
    },
    # ── Story 3 ──────────────────────────────────────────────────────────────
    {
        "id": "ercot-queue-explainer",
        "section": "stories",
        "title": "233 GW of Demand Is Waiting in Line: Inside ERCOT's Data Center Queue",
        "date": _dt.date(2026, 6, 25),
        "author": "GridWatch AI",
        "tags": ["grid", "ERCOT", "Texas", "demand", "infrastructure"],
        "summary": (
            "Texas's grid operator has 233 GW of large-load interconnection requests — "
            "roughly three times the state's current peak demand. Most of the queue is "
            "data centers. Here's what it means."
        ),
        "body": """\
If you built every project currently sitting in ERCOT's large-load interconnection
queue, you would need an electric grid **three times the size of Texas's current one**.
That's not going to happen — but the queue tells a revealing story about where AI
infrastructure investment is headed and what it's doing to the grid that serves
30 million Texans.

### The numbers

As of ERCOT's March 2026 TAC report:

| Metric | Value |
|--------|-------|
| Total large-load requests | **233 GW** |
| Data-center share | ~73% (~170 GW) |
| Requests with signed ISAs | ~18 GW |
| Current ERCOT peak demand | ~85 GW |
| Projected 2030 peak (ERCOT) | ~115 GW |

The queue is not a forecast — it's a **wish list**. Many projects will never break
ground. Developers file early to secure their place in line, and attrition rates
historically run 60–70%. But even if only a quarter materializes, that's a 50+ GW
addition on a grid that struggled to keep the lights on during Winter Storm Uri.

### Why Texas?

Three factors make Texas the epicenter of the data-center land rush:

1. **Deregulated market.** ERCOT is the only major US grid that isn't federally
   regulated by FERC, which means faster interconnection timelines and fewer
   transmission cost-allocation disputes.

2. **Cheap land and power.** West Texas wind and solar have pushed wholesale energy
   prices to some of the lowest in the nation — sometimes negative during sunny,
   windy afternoons. Developers can contract for renewable PPAs at $20–25/MWh.

3. **No state income tax.** Combined with local Chapter 313 (now Chapter 403)
   property-tax abatements, the effective tax burden on a billion-dollar campus
   can be remarkably low.

### The community tension

For small towns along the I-35 corridor and in the Permian Basin, the pitch is
jobs and tax revenue. But the reality is more complicated:

- **A 200 MW data center employs 50–150 people** once built. Construction crews
  are larger but temporary.
- **Property-tax abatements** often run 10–20 years, meaning the school district
  and county see limited revenue during the period of highest community impact.
- **Water rights** in West Texas are governed by the rule of capture — first come,
  first served — and data centers are arriving with deep pockets and drilling rigs.

Local water districts in Abilene and Midland have begun demanding **long-term
water-supply agreements** before signing off on projects, a trend likely to spread.

### What to watch

ERCOT's Board of Directors is considering a **queue-management reform** that would
require refundable deposits and milestone deadlines to clear speculative filings.
The April 2026 presentation to the Texas Senate Business & Commerce Committee
signaled that legislators are paying attention.

> Use the **Data Centers** tab to see the live ERCOT large-load queue data and
> the **Officials** tab to contact your Texas state legislators directly.
""",
    },
    # ── Story 4 ──────────────────────────────────────────────────────────────
    {
        "id": "social-license-risk-2026",
        "section": "stories",
        "title": "How the Industry Files Your Protest: 'Social License' and the $64B Risk Column",
        "date": _dt.date(2026, 7, 11),
        "author": "GridWatch AI",
        "tags": ["community", "policy", "site-selection", "risk", "zoning"],
        "summary": (
            "Data-center developers don't have a risk category called 'protests.' They "
            "have 'social license to operate' — and organized community opposition has "
            "now blocked or delayed an estimated $64 billion in projects. Here's how the "
            "industry actually scores the risk that you'll show up to a hearing."
        ),
        "body": """\
Ask a data-center developer whether they worry about protests and you'll get a careful
answer. That's because inside the industry, *"protest"* isn't a risk category. What you
do when you pack a planning-board hearing gets filed under a quieter, more clinical
heading — and understanding that heading tells you exactly how much leverage residents
actually have.

### The term of art: "social license to operate"

Borrowed from mining and oil & gas, **social license to operate (SLO)** is the industry's
name for whether a community *tacitly accepts* your project — separate from whether you
have the permits. You can hold every entitlement and still be dead in the water. In 2026,
consultants began urging developers to treat SLO with "the same technical rigor applied
to power and fiber due diligence." Data Center Dynamics coined a companion phrase —
**"social interconnection"** — to sit alongside grid interconnection on the site checklist.

The blunt version, from an engineering-firm white paper this June: *"Data centers don't
fail on power. They fail on public trust."*

### Why the reframing happened: the numbers got real

Community opposition stopped being a soft, hand-wavy concern the moment it started
showing up on balance sheets:

| Metric | Value |
|--------|-------|
| U.S. investment **blocked** by opposition (since mid-2024) | **~$18 billion** |
| Investment **delayed** by opposition | **~$46 billion** |
| Total affected investment | **~$64 billion** |
| Local opposition groups (end of 2024) | ~76 |
| Local opposition groups (April 2026) | 268 |
| Local opposition groups (mid-2026) | **430+ across 40+ states** |
| Restriction/moratorium bills filed | 300+ across 30+ states |

That's a 5x growth in organized opposition groups in eighteen months. When a risk grows
that fast and carries a ten-figure price tag, it stops being a PR footnote and becomes a
column in the underwriting model.

### How the risk actually gets scored

Here's the part residents rarely see. Developers don't guess at community mood anymore —
they buy it as a data product. Site-selection platforms now sell a **"community sentiment
layer"** that scrapes municipal records, meeting transcripts, and hyper-local news, then
runs sentiment analysis to flag friction *before a dollar of capital is committed.*

The scoring is weighted by **topic** and by **geography**:

- **By issue** — negativity ratings that tell developers which objections stick:
  noise pollution **87%**, wildlife impact **83%**, environmental impact **79%**,
  water usage **64%**, direct costs to residents **49%**. Note that *noise* — not
  carbon, not water — tops the list. It's the most visceral and the hardest to spin.
- **By state** — jurisdictions get ranked receptive-to-hostile. Most positive:
  Mississippi (78%), Wyoming (74%), South Carolina (69%). Most negative: West Virginia,
  Delaware, Kansas.

One sobering data point on *whose* voice the coverage reflects: in the media these tools
ingest, **industry sources supply 51% of quotes at 90% positive sentiment**, while
individual citizens are just **4% of quotes at a 6-to-1 negative ratio**. The models
know residents are outgunned in the press — which is precisely why an organized,
on-the-record community can move the needle out of proportion to its size.

### What "risk" means to them — and why it favors you

Crucially, the industry doesn't fear a picket line directly. It fears what the picket
line *converts into*. Opposition is classified as a **second-order, indirect risk** —
dangerous because it becomes:

- **Entitlement risk** — rezoning denied or, as in Prince William County, Virginia,
  a rezoning **voided in court** on a public-notice technicality that opponents found
  and litigated all the way toward the state Supreme Court.
- **Schedule risk** — permitting delays measured in months and years of carrying cost.
- **Reputational risk** — disclosed in hyperscalers' own 10-Ks as a threat to their
  ability to build capacity.
- **Financing risk** — whether "announced demand" is actually *executable* at the
  proposed site.

That chain — protest → delay/denial → dead capital — is the whole reason a resident at
a microphone matters. You are not the risk. You are the *trigger* for the risks they've
already priced.

### The mitigation playbook (read it as a tell)

How developers respond reveals how they think. The countermeasures — **community-benefit
agreements**, local-hiring pledges, front-loaded water-recycling and renewable
commitments, choosing pro-development counties on purpose, and assembling land through
blandly-named LLCs to avoid attention — are all attempts to *manufacture* social license
before opposition can organize. The single most effective counter they cite is
unglamorous: **early, continuous communication.** Opposition thrives on being surprised.

### What it means for communities

The lesson isn't that protest is futile — it's the opposite. The industry has spent real
money building tools to detect you *early* precisely because organized, informed, on-the-
record opposition is one of the few forces that reliably converts into delay and denial.
Three things maximize that leverage:

1. **Show up early and on the record.** Sentiment models weight documented, attributed
   opposition — public comment, letters, meeting testimony — far more than social-media
   noise.
2. **Lead with noise, water, and cost.** These are the objections the industry's own
   scoring rates as stickiest and hardest to spin.
3. **Watch the procedure.** The biggest data-center defeat of the cycle turned on a
   notice technicality, not a vote. Entitlements have rules; enforcing them is leverage.

> Use the **Community & Backlash** tab to see what residents near you are already
> organizing around, and the **Officials** tab to put your documented objection on the
> record with the people who actually vote on the rezoning.
""",
    },
]
