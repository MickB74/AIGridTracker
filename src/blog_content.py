"""
Blog content — curated stories and project narrative for the AIGridTracker blog tab.
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
**AI Grid Tracker** exists because the people who live near data centers deserve the
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

*— The AI Grid Tracker team*
""",
}

# ──────────────────────────────────────────────────────────────────────────────
# BLOG STORIES
# ──────────────────────────────────────────────────────────────────────────────

BLOG_STORIES = [
    # ── Story 1 ──────────────────────────────────────────────────────────────
    {
        "id": "moratorium-wave-2026",
        "section": "stories",
        "title": "The Moratorium Wave: Why 14 States Are Pressing Pause on Data Centers",
        "date": _dt.date(2026, 7, 8),
        "author": "AI Grid Tracker",
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
        "author": "AI Grid Tracker",
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

The AI Grid Tracker's **Calculator** tab accounts for both. When you enter a query
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
        "author": "AI Grid Tracker",
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
        "author": "AI Grid Tracker",
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
