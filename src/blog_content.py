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
    # ── Meta Hyperion (Richland Parish, LA) — who pays for 5 GW ──────────
    {
        "id": "meta-hyperion-louisiana-ratepayer-fight-2026",
        "section": "stories",
        "title": "\"Meta pays the full cost.\" Louisiana ratepayers pay \\$8–13 a month. Both are true.",
        "date": _dt.date(2026, 7, 30),
        "author": "GridWatch AI",
        "tags": ["Meta", "Louisiana", "Entergy", "gas plants", "ratepayers",
                 "PSC", "Richland Parish", "transmission",
                 "cost allocation", "analysis"],
        "summary": (
            "Meta's Hyperion campus in rural Louisiana is now a 5-gigawatt, "
            "\\$50-billion-plus build — powered by ten new Entergy gas plants "
            "and a 60-mile transmission line whose \\$470M+ cost falls on "
            "ordinary customers. Meta says it pays the full cost of its "
            "electricity. State watchdogs say average Entergy Louisiana "
            "households will still pay \\$8–13 more per month. Both can be "
            "true. Here's how."
        ),
        "body": """\
On July 27, the *New York Times* joined a long line of Louisiana reporters,
consumer advocates, and clean-energy groups documenting what has become the
largest data-center-driven grid buildout in the American South: **Meta's
\"Hyperion\" campus** in Richland Parish, and the ten new natural-gas power
plants Entergy Louisiana is racing to build to serve it.

The project is now **5 gigawatts of compute at more than \\$50 billion in
capex** — roughly double the \\$27 billion Meta announced when it broke ground
in early 2026 ([nola.com](https://www.nola.com/news/business/meta-louisiana-ai-data-center-richland-parish/article_d1308014-c718-4c34-a75f-476a151ef1a7.html),
[Yahoo Finance](https://finance.yahoo.com/technology/articles/meta-expands-louisiana-hyperion-data-121522809.html)).
It is the largest single data center Meta has ever attempted, and one of the
largest anywhere in the world.

Meta has been consistent in its public message: **it pays the full cost of
the energy, water, and infrastructure it consumes**, and the deal with
Entergy is projected to deliver **\\$2.65 billion in customer savings over
twenty years** ([Meta](https://datacenters.atmeta.com/richland-parish-data-center/)).

State consumer advocates and the Louisiana Public Service Commission's own
independent monitor have been just as consistent: **the average Entergy
Louisiana household will pay an extra \\$8–13 per month** because of the
buildout, plus a share of at least **\\$470 million for a new 60-mile
transmission line** whose primary purpose is to serve one tenant
([Alliance for Affordable Energy](https://www.all4energy.org/watchdog/meta-data-center-to-cause-entergy-bill-increase/),
[Union of Concerned Scientists](https://blog.ucs.org/paul-arbaje/entergy-wants-to-fast-track-gas-plants-for-meta-data-center-leaving-ratepayers-with-the-bill/)).

Both statements are true at the same time. Understanding how is the
difference between a good faith debate and a marketing war — and it is a
model every community facing a hyperscale project should study.

### What Meta actually pays for

Meta's contract with Entergy Louisiana covers the **direct** electricity it
consumes at the meter, plus a set of dedicated infrastructure upgrades tied
to the campus. That is a real and non-trivial commitment. In most states,
this is exactly the argument developers make: *we are net-positive because
we buy our own power under a special large-load tariff*.

The clean way to read that promise is narrow. It does **not** cover:

- **Transmission built to serve the load.** The \\$470M+ 60-mile line
  connecting two substations is being placed in Entergy's general rate base,
  meaning it's paid off across all Louisiana customers over the life of the
  asset ([UCS](https://blog.ucs.org/paul-arbaje/entergy-wants-to-fast-track-gas-plants-for-meta-data-center-leaving-ratepayers-with-the-bill/)).
- **Stranded-asset risk on the ten new gas plants.** Six in Richland Parish,
  three in Pointe Coupee, one in St. Charles ([The Next Web](https://thenextweb.com/news/meta-200-billion-hyperion-data-center-louisiana)).
  If the AI buildout slows, or if Meta walks after year 10 of a 30-year
  asset, ratepayers own the shortfall.
- **System-wide capacity effects.** Adding 5 GW of new load to a regional
  grid pushes up capacity clearing prices for everyone — the same dynamic
  we mapped in the [PJM auction post](pjm-capacity-auction-ratepayer-shock-2026).
- **Financing risk.** Earthjustice's clients asked the PSC in early 2026
  to open a probe into the financing structure of the deal. The PSC
  **declined** ([Earthjustice](https://earthjustice.org/press/2026/consumer-groups-alarmed-as-louisiana-psc-declines-to-take-up-probe-into-meta-risky-financing-deal)).

So when Meta says \"we pay the full cost,\" it is telling the truth about
the meter reading. When advocates say \"households will pay \\$8–13 more per
month,\" they are telling the truth about the rate base. **The two numbers
describe different things.** The trick, for a community negotiating a similar
deal, is to make sure both are on the table.

### How the vote actually happened

The August 2025 PSC vote that approved the first three gas plants is worth
remembering, because it is the template being repeated now for the additional
seven plants ([UCS](https://blog.ucs.org/paul-arbaje/whats-next-after-louisianas-gas-plant-approval-for-meta-data-center/)):

- The vote was **moved forward months** ahead of its originally scheduled date.
- The public was given **just over one week's notice**.
- Community members and consumer groups who traveled to the hearing to
  object were on the record before a decision that had, by most accounts,
  already been made.

Governor Jeff Landry publicly warned about a separate Entergy plant purchase
in June 2026 ([Louisiana Illuminator](https://lailluminator.com/2026/06/23/gov-landry-warns-power-plant-purchase/)),
suggesting the political consensus in Baton Rouge is less unified than the
approval schedule implies.

Meanwhile, the White House issued a **ratepayer protection pledge** in mid-2026
promising that new data-center load would not be subsidized by ordinary
customers. Earthjustice's Louisiana clients — the same ones whose PSC probe
was rejected — responded that the pledge, absent enforcement, is
[cold comfort](https://earthjustice.org/press/2026/earthjustice-clients-in-louisiana-respond-to-white-house-ratepayer-protection-pledge)
in states where the approval clock is already running.

### Ten lessons for a community facing a hyperscale project

Louisiana is not the first state to run this play, and it will not be the
last. Here is what to take from it, in the order the fights actually
happen:

**1. Ask what \"pays for its own power\" actually covers.**
Contract electricity at the meter? Yes. Transmission built to reach the
site? Rarely. Substation upgrades? Sometimes. Capacity-market and
regional-grid ripple effects? Almost never. Stranded-asset risk on 30-year
power plants if the tenant leaves? Never. Model clauses that separate these
buckets and assign each one **by name** to Meta or to ratepayers are the
single most valuable thing a CBA negotiator can push for. \"Full cost\" is
a marketing phrase, not a rate structure.

**2. The size you're told is the floor, not the ceiling.**
Meta announced Hyperion as a \\$10 billion project. It became \\$27 billion.
It is now over \\$50 billion, 5 GW, and ten gas plants — up from an initial
three. Anchor every objection you file, every impact estimate you cite, and
every clause you negotiate to the **build-out ceiling** the developer's own
site plan permits, not the number in the press release.

**3. Fight the docket schedule, not just the docket contents.**
The 2025 Louisiana PSC vote didn't lose on the merits — it was moved forward
months and noticed with a week's warning. If your local hearing suddenly
jumps up on the calendar, that is the substantive fight. Motions for
continuance, procedural objections, and a public paper trail on the schedule
change are more valuable in that moment than another expert filing on the
merits.

**4. The regulator's own independent monitor is your most credible witness.**
The \\$8–13/month figure came from the PSC's monitor's filed report, not
from an advocacy group. Every state PUC has an equivalent — a consumer
advocate, an independent monitor, an office of ratepayer counsel — with
subpoena power the utility can't ignore. Their filings are the most
quotable documents in any commissioner's inbox. Find yours before the
first hearing.

**5. Transmission is where the cost hides.**
The \\$470M+ 60-mile line is going into Entergy's rate base, meaning every
Louisiana customer pays it off over decades. Whenever a developer commits
to \"paying for on-site infrastructure,\" ask specifically: **which side of
the utility fence?** On-site substations may be theirs. The line reaching
that substation almost never is.

**6. Beware the \"customer savings\" framing.**
Meta's \\$2.65B customer-savings figure is calculated **versus a hypothetical
counter-factual** — what customers would have paid if the plants were built
under a different rate design. It is not \"your bill goes down.\" Any time
you see a benefits number, ask: *savings compared to what?* If the answer
isn't a specific alternative filed on the docket, treat it as advertising.

**7. State attorneys general and governors are leverage — use them.**
Gov. Landry publicly warned about a separate Entergy plant purchase in
June 2026. That single statement, from a Republican governor of the state
hosting the deal, is worth more than fifty comment letters. Identify the
elected officials in your state who have said *anything* skeptical, put
their words on the record, and ask commissioners to respond to them by
name.

**8. Federal pledges without state enforcement mean nothing.**
The 2026 White House ratepayer-protection pledge sounds like coverage. It
provides none. Rate design happens at state PUCs. If your fight is at the
PUC, cite the federal pledge as a floor — then insist on a state-level
enforcement mechanism, because the White House cannot compel a Louisiana
commissioner to do anything.

**9. Frame the debate around asset lifespans, not press releases.**
Meta signs 10-to-15-year lease commitments. The gas plants Entergy is
building have 30-to-40-year physical lives and financing to match. The
question every commissioner should have to answer on the record: *what
happens in year sixteen?* Force that question into the hearing transcript
and you have changed the shape of every future proceeding.

**10. Get the ripple effects on the record early.**
Louisiana isn't in PJM, so the direct capacity-market spillover is limited —
but the MISO-South zone still sees rate impacts from load additions of this
size, and Louisiana's neighbors are already asking about cost allocation.
Even if your state's fight is local, the RTO or independent operator
serving it has a filing docket where the *neighboring* impacts get argued.
Enter appearances there too. Precedents set in one state are cited in
every state after it.

Bundle these together and the pattern is clear: **hyperscale approvals are
not won on the merits, they're won on process, timing, and paperwork.** The
same utility that assured Louisiana ratepayers they wouldn't pay a dime is
now, on the docket, asking them to pay hundreds of millions. Both statements
were made in good faith by people convinced of their own version of the
truth. The community's job is to make sure the second version — the one
filed under oath — is the one commissioners have to answer for.

> Louisiana isn't alone. If you want to see whether your state's PUC has
> opened a docket on data-center cost allocation, the
> [PUC directory](/puc.html) has commission websites and complaint links
> for all 50 states plus D.C. If you're facing a similar buildout, the
> [Start here wizard](https://aigridtracker.streamlit.app) will generate
> a comment script, meeting brief, and letter template with your numbers
> baked in.

### Sources

- [The New York Times — Meta's Louisiana Data Center (July 27, 2026)](https://www.nytimes.com/2026/07/27/technology/meta-data-center-louisiana.html)
- [nola.com — \\$40B expansion coverage](https://www.nola.com/news/business/meta-louisiana-ai-data-center-richland-parish/article_d1308014-c718-4c34-a75f-476a151ef1a7.html)
- [Meta — Richland Parish data center page](https://datacenters.atmeta.com/richland-parish-data-center/)
- [Union of Concerned Scientists — Entergy fast-track analysis](https://blog.ucs.org/paul-arbaje/entergy-wants-to-fast-track-gas-plants-for-meta-data-center-leaving-ratepayers-with-the-bill/)
- [UCS — What's next after PSC approval](https://blog.ucs.org/paul-arbaje/whats-next-after-louisianas-gas-plant-approval-for-meta-data-center/)
- [Alliance for Affordable Energy — Entergy bill increase](https://www.all4energy.org/watchdog/meta-data-center-to-cause-entergy-bill-increase/)
- [Earthjustice — PSC declines to probe financing](https://earthjustice.org/press/2026/consumer-groups-alarmed-as-louisiana-psc-declines-to-take-up-probe-into-meta-risky-financing-deal)
- [Earthjustice — response to White House ratepayer pledge](https://earthjustice.org/press/2026/earthjustice-clients-in-louisiana-respond-to-white-house-ratepayer-protection-pledge)
- [Louisiana Illuminator — Gov. Landry on plant purchase](https://lailluminator.com/2026/06/23/gov-landry-warns-power-plant-purchase/)
""",
    },
    # ── PJM capacity auction / ratepayer cost allocation ─────────────────
    {
        "id": "pjm-capacity-auction-ratepayer-shock-2026",
        "section": "stories",
        "title": "Five Auctions, \\$29 Billion: How Data Centers Took Over the PJM Capacity Market — and Sent Your Bill to the Moon",
        "date": _dt.date(2026, 7, 26),
        "author": "GridWatch AI",
        "tags": ["PJM", "capacity markets", "utility bills", "cost allocation",
                 "FERC", "Illinois", "Virginia", "ratepayers", "analysis"],
        "summary": (
            "PJM's capacity auction price has gone from \\$29/MW-day to \\$325 in "
            "four years. Data centers drove 46% of the cost — \\$29.4 billion — "
            "across those auctions, and the grid's independent watchdog says "
            "ratepayers are footing the bill for power plants that may never "
            "be needed. Here's the full timeline, who pays, and the three "
            "reform proposals on the table right now."
        ),
        "body": """\
On July 14, 2026, PJM Interconnection — the grid operator for 67 million
people across 13 states and Washington, D.C. — published the results of its
fifth consecutive capacity auction shaped by data center demand. The numbers
tell a story that every ratepayer in the mid-Atlantic should understand,
because the cost lands on their bill whether they've heard of a "base residual
auction" or not.

### The price trajectory

PJM's capacity market pays power plants to *exist* — to be available on the
hottest summer afternoon even if they don't run. The clearing price determines
how much consumers pay for that insurance. Here is what has happened to it:

| Delivery year | Clearing price (\\$/MW-day) | Change | Total cost |
|---------------|---------------------------|--------|------------|
| 2024/2025 | \\$28.92 | — | ~\\$5 B |
| 2025/2026 | \\$269.92 | **+833%** | ~\\$14.7 B |
| 2026/2027 | \\$329.17 | +22% | ~\\$16.4 B |
| 2027/2028 | \\$333.44 (price cap) | +1.3% | ~\\$16.4 B |
| 2028/2029 | \\$325.00 | −2.5% | ~\\$16.4 B |

Read that first jump again. In a single year, the price that sets roughly 20%
of your electricity bill rose by a factor of *nine*. And it has stayed there
for four straight auctions, pinned at or near the FERC-approved price cap.

The price cap is doing real work here. Without it, the 2028/2029 auction
would have cleared at roughly **\\$555/MW-day** RTO-wide — and **\\$777/MW-day**
in the ComEd zone around Chicago. The cap has saved consumers an estimated
**\\$45 billion** over four auctions. But it hasn't solved the underlying
problem — it's just hidden how bad the underlying problem is.

Two things happened in 2025 that had never happened before: PJM's load
forecast added **tens of thousands of megawatts** of data center demand, and
the clearing price hit the administrative ceiling. By the 2027/2028 auction
it got worse — PJM fell **6,625 MW short** of its own reliability target, the
first RTO-wide capacity shortfall in the market's history.

---

### Where the \\$29.4 billion went

PJM's Independent Market Monitor — the neutral referee Congress created to
keep wholesale markets honest — has now quantified data centers' share of the
bill. The numbers are stark.

| Metric | Value |
|--------|-------|
| Data center share of the **latest** auction | **\\$6.3 B** (38% of \\$16.4 B) |
| Data center share over **four auctions** | **\\$29.4 B** (46% of \\$63.6 B) |
| Share of projected load growth from data centers | **94%** |
| Customers who pay these costs | **67 million** across 13 states + D.C. |

Market Monitor president Joseph Bowring put it plainly: **"This is not
something the data centers are actually paying themselves. This is a cost
being imposed on all customers in the PJM footprint."**

That distinction is the whole story. The capacity market doesn't charge data
centers directly for the demand they add. It charges *everyone* — residential,
commercial, industrial — based on their share of system peak load. When a
500 MW data center raises the system peak, your household's fractional share
of the new, larger peak becomes your new capacity bill — even though your
usage hasn't changed.

Bowring's diagnosis: **"PJM is continuing to act like it's business as usual"**
when what the grid is experiencing is **"a paradigm shift."**

---

### What it costs you, personally

The capacity charge is typically buried on page two of your bill, lumped into
"supply charges" or "generation service." But it's real money:

- **ComEd (Illinois)** customers have seen power prices rise **~50% in two
  years**, with capacity costs the primary driver.
- **Pepco (D.C.)** residential customers saw bills jump **~\\$21/month**
  starting June 2025.
- **BGE (Baltimore)** and **Dominion (Virginia)** zones cleared even higher
  than the RTO average in the 2025/2026 auction — \\$466 and \\$444/MW-day
  respectively — because that's where data centers are concentrating.
- The average PJM household could face a cumulative increase of roughly
  **\\$70/month** by 2028 if prices stay at these levels.

Virginia — which hosts more data center capacity than any other state — and
northern Illinois are ground zero. But capacity charges are allocated across
the *entire* RTO, so customers in Ohio, Indiana, Kentucky, and the Carolinas
are paying too.

---

### Why the price cap matters — and why it's not protecting you

You might think a price cap is good news. It isn't, for two reasons:

**1. The cap isn't low.** At \\$333.44/MW-day, a ratepayer's capacity bill is
already 11 times what it was in 2024. The cap prevents further increases; it
doesn't roll back the ones already baked in.

**2. When supply can't clear above the cap, it doesn't show up.** In the
2027/2028 auction, 809.6 MW of capacity *offered* to sell but was priced
above the ceiling. It couldn't clear. Result: the grid fell short of its
reliability margin for the first time. The cap kept the price from rising —
and in exchange, it kept the power from arriving.

The 2028/2029 auction was even worse: **6,831 MW short**, with a reserve
margin of just **14.7%** against a 20% target — the lowest ever recorded.
Only 525 MW of new generation cleared, down from 774 MW the year before.

PJM has asked FERC to approve a temporary "reliability backstop" auction to
fill the gap. But that doesn't change the structural problem: the capacity
market was designed for a world where demand grew 1% a year. Data centers
blew past that assumption so fast that the market's own safety valve is now
working against reliability.

---

### Three reform proposals — and what they'd mean for your bill

The debate has moved from "is this a problem?" to "which fix?" Here are the
three live proposals:

**1. Separate auction for large loads (Bowring / Market Monitor)**
Data centers that can't self-supply would bid in a segregated 15-year capacity
auction. Their costs would be allocated to *them*, not to residential
ratepayers. Bowring: **"There's only one way to do what hyperscalers agree is
the right thing to do, and that is to run a separate auction."**

**2. Illinois POWER Act (state legislation)**
Would require data centers to pay their own interconnection costs, bring
enough new capacity to cover their own load, and supply new clean energy or
reimburse the state. Failed to pass in spring 2026, but the Citizens Utility
Board says the fight is **"far from over"** and will return.

**3. Federal Power for the People Act**
Would direct FERC to ensure data centers fund the local transmission upgrades
their load requires — rather than spreading those costs across the RTO.

All three share one principle: **the entity that causes the cost should bear
the cost.** That principle already applies to transmission interconnection for
new generators. It has never been applied to new *load* at this scale, because
load at this scale didn't exist until AI.

---

### What you can do with these numbers

If you live in PJM territory — Delaware, Illinois, Indiana, Kentucky,
Maryland, Michigan, New Jersey, North Carolina, Ohio, Pennsylvania, Tennessee,
Virginia, West Virginia, or D.C. — here's how to use this:

1. **Find the capacity charge on your bill.** It's usually inside "supply" or
   "generation service." Your utility's tariff schedule will break it out.
   Once you see it, you'll understand why your bill moved.

2. **Ask your state PUC one question:** *"What is my utility's plan to ensure
   data center load growth doesn't raise residential capacity costs further?"*
   File it in writing. It becomes part of the record in any future rate case.

3. **Support cost-causation reform.** Whether it's the POWER Act in Illinois,
   the Market Monitor's separate-auction proposal at FERC, or your state's own
   version — the policy ask is the same: large loads should pay for the
   capacity they require, not externalize it onto 67 million households.

4. **Show up at PJM stakeholder meetings.** PJM's Board is actively
   deliberating on data center demand management *right now*. Public pressure
   from ratepayer advocates — including the Citizens Utility Board, NRDC,
   state consumer advocates, and individual residents — is what moves the
   timeline from "under study" to "implemented."

The capacity market is the most expensive part of your bill that you've never
heard of. Now you've heard of it — and you know who's driving the price.

> Use the **Your Utility Bill** tab for a full breakdown of how capacity
> charges flow from the auction to your monthly statement, and the
> **States & Officials** tab to find your PUC's complaint portal.
""",
    },
    # ── Regulatory gap-shopping / oversight sidestep ────────────────────
    {
        "id": "oversight-gaps-agency-shopping-2026",
        "section": "stories",
        "title": "One Project, Two Stories: How Data Center Developers Shop the Gaps Between Agencies",
        "date": _dt.date(2026, 7, 26),
        "author": "GridWatch AI",
        "tags": ["West Virginia", "permitting", "preemption", "NDAs", "shell LLCs",
                 "air permits", "zoning", "transparency", "analysis"],
        "summary": (
            "In Tucker County, West Virginia, one developer told the DEP it "
            "controlled 10,000 acres — and told the Department of Commerce its "
            "project was merely \"conceptual.\" Both agencies say there's no "
            "contradiction, because neither one reviews the whole project. That "
            "gap isn't a West Virginia quirk. It's the buildout's default "
            "operating mode, and it shows up in seven recognizable forms — from "
            "\"nonroad engine\" turbine exemptions in Memphis to shell-company "
            "NDAs in Wisconsin to by-right zoning in Virginia. Here's the "
            "taxonomy, and the questions that close each gap."
        ),
        "body": """\
On July 1, 2026, West Virginia's Department of Commerce decided that a data
center proposed less than a mile from the towns of Davis and Thomas was
"conceptual" — the developer, Fundamental Data, didn't have legal control of
the land, so there was nothing yet to review.

There was one problem with that finding. The West Virginia Department of
Environmental Protection had *already* issued Fundamental Data an air pollution
permit for the gas plant meant to power the site — a permit that rested in part
on the company demonstrating control of that same ground.

Same company. Same 10,000 acres. Two agencies, two answers.

Asked about it by
[Mountain State Spotlight](https://mountainstatespotlight.org/2026/07/23/data-center-sidestep-oversight/),
both departments sent *identical* statements denying any discrepancy — and the
explanation is the whole story. Air permitting accepts "a lease, purchase
agreement, option to purchase, or another legally recognized arrangement."
Commerce's High Impact Data Center program uses "distinct statutory criteria,
such as recorded deeds and binding commitments, which operate independently of
WVDEP's air permitting requirements."

Both statements are true. Neither agency is lying. And that is precisely the
point: **no one in West Virginia state government is responsible for evaluating
the project as a project.** During the 2025 comment period, DEP regulators told
residents repeatedly that their authority extended only to the natural gas
plant — not to the data center the gas plant existed to power.

Tucker United's Nikki Forrester put it more bluntly than any regulator would:
the company "lives in the brackish zone between being a microgrid and data
center-related project and not having anything to do with data centers so they
can skirt regulations and state rules."

---

### The detail that makes it a national story

Five days after Commerce withdrew its demand for information, a Fundamental
Data representative named Ted McGavran appeared before the city council in
**Belmont, North Carolina** — his own hometown — to argue for data center zoning
ordinances there. In the same presentation he described the Tucker County
project as targeting large-scale clients and **3–5 gigawatts** of generation.
Nothing conceptual about it.

He also said his company helped write West Virginia's data center law, and
summed up the result: *"We can do pretty much whatever we want to do up there."*

(Fundamental Data spokesperson Andrea Khoury told the outlet McGavran "is not
authorized to speak on behalf of the company," that his remarks were "solely in
his personal capacity," and denied the company had a hand in drafting the law.)

Forrester's response is the line worth carrying into your own hearing: **"Even
data center developers don't want these things in their own backyard."**

The reason he *could* advocate for zoning in Belmont while his company faced
none in Tucker County is West Virginia
[HB 2014](https://www.wvlegislature.gov/Bill_Text_HTML/2025_SESSIONS/RS/bills/hb2014%20sub1%20enr.pdf),
the Power Generation and Consumption Act, effective July 11, 2025. Certified
microgrid districts and certified high-impact data centers **may not be subject
to county or municipal zoning, noise, viewshed, lighting, development, or land
use ordinances.** The state didn't just fragment review — it deleted the one
layer of government that answers a phone call from a resident.

---

### Seven versions of the same move

Tucker County isn't an outlier. It's one instance of a repeatable pattern:
*route the project to the venue with the narrowest mandate.* Here are the other
six forms it takes, each documented somewhere else in the country.

**1. Agency-shopping on facts.** *(Tucker County, WV)* Tell each regulator the
version of the project that fits its checklist. Because no agency reviews
cumulative impact, the versions never have to reconcile.

**2. Statutory preemption of the local layer.** *(WV HB 2014)* If certification
comes from the state Commerce Secretary and local ordinances are void by
statute, the planning-commission hearing — the one place residents reliably get
standing — simply never happens. West Virginia went furthest, but per
[MultiState's 2026 tracker](https://www.multistate.us/insider/2026/4/14/federal-ai-data-center-policy-meets-resistance-from-state-lawmakers)
and
[Prism](https://prismreports.org/2026/05/18/more-states-are-trying-to-block-cities-from-regulating-ai-data-centers/),
a growing number of states have taken up preemption bills. Some WV lawmakers
are now moving to restore local control.

**3. Reclassifying the equipment.** *(Memphis, TN)* xAI ran gas turbines at its
Colossus site while asserting an "operational waiver" to run up to 364 days
without a permit; the Shelby County Health Department treated temporary
turbines as **"nonroad engines"** exempt from permitting. The NAACP and the
[Southern Environmental Law Center](https://www.selc.org/press-release/groups-appeal-permit-for-xais-south-memphis-data-center-decisions-around-unpermitted-methane-gas-turbines/)
sued and appealed, arguing no Clean Air Act framework allows installing and
operating that generation permit-free. The turbines eventually got a permit
covering 15 units — as *secondary emergency backup*.

**4. Sizing to stay under the threshold.** Backup generation is routinely
permitted as **synthetic minor** — a permit whose explicit purpose is to cap
hours so the site never becomes a Title V major source. One Georgia data center
permit covering **50-plus diesel generators** states outright that it exists
"for the purpose of establishing practically enforceable emission limitations
such that the facility will not be considered a major source." That's legal and
routine. It also means the community's public-participation rights are set by
an hours cap that most residents never see and no one independently meters.

**5. Contracting away disclosure.** *(WI, MN, TN, AZ)* Wisconsin Watch found at
least four Wisconsin communities signed NDAs before any public process:
**Beaver Dam** signed with **Balloonist LLC** on Dec 1, 2023 — barred from even
confirming "the existence of the project" — and the \\$1B, 520-acre Meta project
wasn't announced for **14 months**. **Menomonie** signed with the same shell in
Feb 2024 (\\$1.6B, announced July 2025); **Kenosha** with Microsoft in May 2024;
**Janesville** with Viridian in Sept 2025 (\\$8B). Minnesota officials used the
code name **"Project Bigfoot"** in public documents for over a year while Meta
worked through **Jimnist LLC**. Public Citizen reports **80% of Virginia
localities** with data centers have NDAs in place, and that
[at least ten states](https://www.citizen.org/news/the-secret-data-center-buildout-how-states-can-stop-big-techs-abuse-of-ndas/)
have introduced bills to restrict them. As one Oklahoma legislator framed it:
*where you want to put your data center is not a trade secret.*

**6. Zoning it by right.** *(VA)* You don't need preemption if the land is
already zoned for it. In **Franklin County, Virginia**, data centers are
permitted by right in the Regional Enterprise Park district and face no
restriction at all on unzoned property — meaning a campus can be built with
**no public hearing and no supervisors' vote**, only site plans and building
permits. **Goochland** permits them by right across most of a designated
district. Loudoun County has been unwinding exactly this fast-track status.

**7. Redacting the price.** Even when a project reaches a public regulator, the
economics often don't. The Illinois Attorney General sought a contested hearing
over **"heavily redacted"** ComEd data center special contracts. In Montana,
advocates challenged the PSC's ability to keep data center terms secret. And
Earthjustice's May 2026 Mississippi report argues incremental system costs were
cloaked in NDAs in a way with **no known analogue anywhere else in the
country**. If the contract is sealed, no one can verify who's paying for the
interconnection — which is the only number that determines whether your bill
moves.

---

### What these have in common

Every one of the seven is *legal*. None requires anyone to lie. They work
because permitting authority in the U.S. is sliced by **medium** (air, water,
land) and by **jurisdiction** (federal, state, county), while a gigawatt-scale
data center is a single decision with effects that cross all of them.

The developer sees one project. The law sees eight unrelated filings. The gap
between those two views is the product.

The federal layer is starting to notice — FERC's December 2025 PJM co-location
order forced tariff changes precisely because co-located load was escaping the
cost-allocation rules that apply to everyone else, on the principle that "costs
must be allocated to those who cause them and benefit from them." State
ratepayer advocates told FERC in July 2026 it still doesn't go far enough. But
federal cost-allocation reform doesn't help you at a county hearing next month.

---

### Six questions that close the gaps

Put these in writing — to the developer, the agency, and your elected officials.
A refusal to answer is itself a public record you can cite.

1. **"List every permit, certification, and approval this project requires, and
   name the agency and decision-maker for each."** Ask for the *whole* list.
   The list itself reveals which venues you still have standing in — and the
   deadlines you're about to miss.
2. **"What did you tell each of those agencies about land control, project
   size, and generating capacity?"** Then compare the filings. Discrepancies
   like Tucker County's are only visible if someone reads them side by side.
3. **"Which agency is evaluating cumulative impact — air, water, noise, traffic,
   and rates together?"** If the honest answer is *none*, that is the finding.
   Say it out loud at the hearing and ask your council to request one.
4. **"Are the generators permitted as emergency, synthetic minor, or major
   source — and what is the annual hours cap?"** Then ask who verifies the
   hours and whether run-time logs are public.
5. **"Has any official here signed an NDA relating to this project? Produce it."**
   Ask at an open meeting, on the record. In several states this question alone
   has driven legislation.
6. **"Is the utility's contract for this load public and unredacted?"** If not,
   your PUC — not your planning board — is where the money gets decided. Find
   yours in the **States & officials** tab.

---

### The bottom line

The Tucker County story will get read as a West Virginia story about one
awkward developer. It isn't. It's a demonstration that a project can hold two
contradictory identities at the same time — real enough for an air permit,
conceptual enough to dodge disclosure — and that under current law, **both can
be true simultaneously.**

Communities keep losing these fights not because they show up unprepared, but
because they show up at the *one* venue that was never empowered to consider
what they came to say. Map the venues first. Then decide where to spend your
people.

*Sources: [Mountain State Spotlight, "Tucker County residents want to know what
Fundamental Data is planning," July 23, 2026](https://mountainstatespotlight.org/2026/07/23/data-center-sidestep-oversight/);
[WV HB 2014 (enrolled)](https://www.wvlegislature.gov/Bill_Text_HTML/2025_SESSIONS/RS/bills/hb2014%20sub1%20enr.pdf);
[Southern Environmental Law Center on xAI turbine permits](https://www.selc.org/press-release/groups-appeal-permit-for-xais-south-memphis-data-center-decisions-around-unpermitted-methane-gas-turbines/);
[Wisconsin Watch, "At least four Wisconsin communities signed secrecy deals," Jan 2026](https://wisconsinwatch.org/2026/01/wisconsin-data-center-secrecy-deals-nda-nondisclosure-agreement/);
[Public Citizen, "The Secret Data Center Buildout"](https://www.citizen.org/news/the-secret-data-center-buildout-how-states-can-stop-big-techs-abuse-of-ndas/);
[Star Tribune on Minnesota code names and shell companies](https://www.startribune.com/ndas-code-names-and-shell-companies-how-minnesota-officials-support-data-center-secrecy/601499182);
[Utility Dive on FERC and PJM data center transmission costs](https://www.utilitydive.com/news/ferc-data-center-pjm-transmission-costs/825760/);
[Illinois AG objections to ComEd data center contracts](https://www.utilitydive.com/news/illinois-ag-files-objections-to-comed-data-center-agreements-at-ferc/809576/);
[MultiState 2026 state data center tracker](https://www.multistate.us/insider/2026/4/14/federal-ai-data-center-policy-meets-resistance-from-state-lawmakers).*
""",
    },
    # ── DOE National Transmission Needs Study (July 2026 draft) ─────────
    {
        "id": "doe-transmission-needs-2026",
        "section": "stories",
        "title": "DOE Just Named Data Centers the #1 Reason America Needs New Power Lines. Here's Why Your Community Should Read the Fine Print.",
        "date": _dt.date(2026, 7, 26),
        "author": "GridWatch AI",
        "tags": ["DOE", "transmission", "NIETC", "rates", "public comment",
                 "tribal lands", "policy", "breaking"],
        "summary": (
            "The Department of Energy's draft 2026 National Transmission Needs "
            "Study makes it official: load growth — led by data centers — is now "
            "the main reason the U.S. needs new transmission. Congestion already "
            "adds \\$11 billion a year to wholesale power costs, tens of billions "
            "in new lines are approved, and the study feeds directly into federal "
            "corridor designations that can override local siting authority. "
            "Public comments are open until September 7, 2026 — and the draft is "
            "full of numbers communities can use."
        ),
        "body": """\
Every three years, federal law requires the Department of Energy to tell the
country where its electric grid is congested, constrained, or about to be.
The [draft 2026 National Transmission Needs Study](https://www.energy.gov/oe/national-transmission-needs-study),
released for public comment in July, is that report — and this edition reads
differently from every one before it.

The headline isn't buried. In DOE's own words, **load growth is now the main
driver of future transmission need** — and the first item on its list of what's
driving load growth is *"growth in data centers, artificial intelligence (AI),
and cryptocurrency mining."* The agency devotes a call-out box to data-center
projections showing demand reaching **more than 400 TWh by 2030 — over 10% of
all U.S. electricity**.

If you're a resident wondering whether the data center proposed outside town
has anything to do with the new 500 kV line proposed *through* it, the federal
government just answered you.

---

### The numbers worth writing down

| What the study found | Number |
|---|---|
| Congestion's added cost to wholesale power, 2023 | **\\$11 billion** (peaked at \\$21B in 2022) |
| Share of hours driving most congestion costs | **just 5%** |
| U.S. demand growth projected by NERC, 2024–2034 | **+25%** (4,281 → 5,353 TWh) |
| Data-center demand by 2030 (LBNL/EPRI/McKinsey range) | **up to 400+ TWh, >10% of U.S. total** |
| FERC's own range for data-center growth by 2030 | **13 to 55 GW** — a 4x spread |
| Transmission built 2016–2024 | **85,000 circuit-miles** — 98% by incumbent utilities |
| Aging-grid replacement need (Brattle est.) | **~4,000 circuit-miles / ~\\$10B per year** |
| Newly approved regional buildouts | MISO **\\$21.8B** · SPP **\\$7.7B** · Texas 765 kV **\\$33B** |

---

### Why this document matters more than most reports

This isn't just a study — it's legal machinery. Under Federal Power Act
§216, the Needs Study is the analytical foundation DOE uses to designate
**National Interest Electric Transmission Corridors (NIETCs)**. Inside a
designated corridor, federal regulators gain *backstop siting authority* —
meaning a transmission project rejected or delayed at the state or local
level can still move forward.

Translation for communities: the maps in this draft are an early look at
where federal authority may eventually reach. The time to influence that is
**now, during the comment period** — not after a corridor lands on your county.

---

### Four things communities should take from it

**1. You now have federal validation.** When a developer's consultant tells
your planning board that a data center has nothing to do with rising
delivery charges, you can quote the Department of Energy: load growth, led
by data centers, is the principal driver of the country's transmission
needs. Print the study's data-center box (p. 80) and bring it.

**2. The bill for all of this is unassigned.** The study identifies *need* —
it is silent on *who pays*. Transmission costs flow into the delivery
portion of every electric bill by default, and utilities earn a regulated
return on every mile they build (which is one reason incumbents built 98%
of it). Unless your state adopts large-load tariffs and cost-causation
rules, a buildout justified by data-center demand lands on households.
That's the fight at your PUC, and the study is your exhibit A.

**3. Nobody actually knows how much of this demand is real.** FERC's own
projection spans **13 to 55 GW** by 2030 — the top of the range is four
times the bottom. Speculative and duplicate interconnection requests
("phantom load") are inflating forecasts everywhere. If lines get built for
load that never materializes, ratepayers hold the bag for decades. The ask:
load commitments, minimum-take contracts, and developer-funded upgrades
*before* shovels move — so the party creating the risk carries it.

**4. The cheapest fix is flexibility, not always wire.** The study notes
most congestion costs pile up in just **5% of hours** — the same peak hours
when data centers could curtail. That finding lines up almost exactly with
what Duke University's Nicholas Institute published in February 2025:
[*Curtailment-Enabled Headroom*](https://nicholasinstitute.duke.edu/publications/curtailment-enabled-headroom-how-flexible-large-loads-can-accelerate-decarbonization),
led by Tyler Norris, found the **existing** grid could absorb **up to 98 GW**
of new large load if that load agreed to curtail just **0.5% of annual hours
— roughly 44 hours a year** — avoiding **\\$150 billion or more** in new
power plants and transmission lines. DOE says congestion concentrates in 5%
of hours; Duke says you only need the flexible loads to stand down in 0.5%
of them. Texas already wrote a version of this into law (SB 6: ERCOT can
curtail large loads in emergencies). Communities and PUCs should demand the
same: flexible-load agreements and grid-enhancing technologies evaluated
*before* approving billion-dollar buildouts that peak-shave for a handful of
hours a year. *(We break down the Duke numbers — and the SLA and rate-design
reasons operators resist them — in* **"Why Your Electric Bill Is Going Up —
and What Data Centers Have to Do With It"** *elsewhere on this blog, with the
full research library in the* **Your utility bill** *tab.)*

---

### The tribal-lands finding everyone will skip

One section deserves more attention than it will get: **2.3% of the
nation's transmission miles cross Tribal lands**, and over 1,000
high-voltage substations sit on or near them — 919 in SPP South alone.
Yet Navajo Nation and Hopi Tribe homes still lack electricity, and DOE's
Office of Indian Energy found energy costs consume a **28.3% larger share
of income** for households on Indian land than elsewhere. Infrastructure
that crosses a community without serving it is the oldest story in
energy — and it's a preview of what data-center-driven buildout does
wherever the benefits and burdens land on different people.

---

### What to do with it

1. **File a comment — by September 7, 2026.** The 60-day window closes
   then; email your comments to
   [NeedsStudy.Comments@hq.doe.gov](mailto:NeedsStudy.Comments@hq.doe.gov)
   (details on [DOE's Needs Study page](https://www.energy.gov/oe/national-transmission-needs-study)).
   Tell them transmission driven by large loads should be paid for by
   large loads — and that corridor designations need real local process.
2. **Cite it at your next hearing.** Pair it with your numbers from the
   **Local Impact Calculator** and the rate-impact background in **Your
   utility bill**.
3. **Ask your utility one question in writing:** *What share of your
   planned transmission spending is driven by data-center load, and under
   what tariff will it be recovered?* Their answer (or refusal) is a
   public-comment exhibit.
4. **Find your regulator** in **States & officials** — rate cases, not
   zoning hearings, are where transmission costs are actually assigned.

The grid is being rebuilt around AI demand either way. The only open
question is whether communities shape the terms — and this study, for all
its dry federal prose, just handed them the evidence.

*Sources: [DOE 2026 National Transmission Needs Study — Draft for
Consultation and Public Comment](https://www.energy.gov/oe/national-transmission-needs-study),
July 2026; Norris, T. et al., [*Curtailment-Enabled Headroom: How Flexible
Large Loads Can Accelerate Decarbonization*](https://nicholasinstitute.duke.edu/publications/curtailment-enabled-headroom-how-flexible-large-loads-can-accelerate-decarbonization),
Nicholas Institute for Energy, Environment & Sustainability, Duke University,
February 2025.*
""",
    },
    # ── BNEF 194 GW forecast ─────────────────────────────────────────────
    {
        "id": "bnef-194gw-forecast-2026",
        "section": "stories",
        "title": "One in Five Electrons: BNEF Says Data Centers Will Consume 20% of U.S. Power by 2035",
        "date": _dt.date(2026, 7, 21),
        "author": "GridWatch AI",
        "tags": ["BNEF", "grid demand", "forecast", "gas generation", "capex",
                 "PJM", "ERCOT", "rates", "community impact"],
        "summary": (
            "BloombergNEF just raised its U.S. data-center power forecast by 83% — to "
            "194 GW by 2035 — meaning one out of every five units of electricity generated "
            "in the country would flow to a data center. With hyperscalers on track to spend "
            "\\$700 billion this year and 124 GW of on-site gas plants in the pipeline, "
            "the energy system your community depends on is being reshaped in real time."
        ),
        "body": """\
On July 21, [BloombergNEF released an updated forecast](https://www.latitudemedia.com/news/bnef-nearly-doubled-its-forecast-for-us-data-center-power-demand/)
that should stop every utility commissioner, planning-board member, and ratepayer
advocate in their tracks: U.S. data centers are now projected to reach **194 gigawatts**
of power demand by 2035 — an **83% increase** from BNEF's own December 2025 estimate
of 106 GW.

To put that in perspective: 194 GW is roughly the output of **194 traditional nuclear
reactors**. BNEF analyst Lloyd Arnold framed it bluntly:
*"Every coal plant, every gas plant, every solar farm in the US — one unit of energy
out of five generated by them is going to data centers."*

---

### The numbers at a glance

| Metric | Value |
|--------|-------|
| Projected U.S. data-center capacity, 2035 | **194 GW** |
| Share of U.S. electricity consumption, 2035 | **\\~20%** (up from **5.9%** today) |
| Share of U.S. electricity consumption, 2030 | **\\~12%** |
| Hyperscaler capex this year (Moody's) | **\\~\\$700 billion** |
| Announced on-site gas generation | **124 GW** |
| Annual record for grid-connected DC capacity | **7.1 GW** in a single year |

This isn't an outlier projection. Every major forecaster has revised upward in the
same direction: EPRI more than **doubled** its 2024 estimate; S&P **increased its
forecast by more than a third** between October and April. The trend line only bends
one way.

---

### Where the load lands — PJM and ERCOT in the crosshairs

The national average masks extreme regional concentration. According to
[TechCrunch's analysis](https://techcrunch.com/2026/07/21/data-centers-expected-to-use-4x-more-electricity-by-2035/)
of the BNEF data:

- **PJM Interconnection** (Virginia through Illinois) will dedicate **34%** of its
  electricity to data centers — more than one in three electrons.
- **ERCOT** (most of Texas) will allocate **22%** of generating capacity to data
  centers.

These are the two grids that already serve the largest concentration of data centers
in the country. Virginia's "Data Center Alley" and the Texas permitting pipeline are
not hypothetical — they are *existing* load on grids where capacity constraints are
already driving up prices.

How much? PJM electricity prices **rose 76%** over the past year, and data centers
represented **38%** of charges in PJM's most recent capacity auction. That cost flows
directly to every residential and commercial ratepayer on the system.

---

### The gas rush: 124 GW of on-site generation

Unable to wait in grid interconnection queues that stretch **five years or longer**,
developers are building their own power plants. BNEF now tracks **124 GW** of announced
on-site gas generation capacity — nearly two-thirds of the total 2035 data-center
forecast.

The model is straightforward: install gas turbines or reciprocating engines on the data
center campus, bypass the grid entirely, and begin operations years before a
transmission interconnection would be approved. Only one fully off-grid facility is
currently operational — SpaceX's **Colossus 2** in Memphis — but the pipeline is
enormous.

For communities, on-site gas generation raises a distinct set of questions:

- **Air quality:** These are industrial combustion facilities sited next to (or inside)
  data-center campuses, often in areas zoned for commercial or light-industrial use.
  What are the local emissions permits? What monitoring is in place?
- **Water:** Gas-fired generation requires cooling. Does the on-site plant draw from
  the same water source as the data center's cooling system?
- **Stranded assets:** If grid interconnection eventually arrives, or if clean-energy
  mandates tighten, do these gas plants become stranded infrastructure — and who pays
  for decommissioning?
- **Climate commitments:** Every hyperscaler has a net-zero or carbon-free energy
  target. Building 124 GW of new gas capacity is difficult to reconcile with those
  pledges. Ask developers how on-site gas fits their published decarbonization
  timeline.

Mark Daly, BNEF's head of technology and innovation,
[acknowledged the execution risk](https://finance.yahoo.com/technology/ai/articles/data-centers-track-suck-fifth-110000467.html):
the majority of new projects involve **first-time developers** who lack experience in
financing, land acquisition, power procurement, and offtake agreements. Construction
barriers include intense competition for labor and equipment, political opposition, and
persistent interconnection delays.

---

### \\$700 billion in one year

The supply of capital is not in question. Moody's Ratings reports that the six largest
U.S. hyperscalers — Microsoft, Meta, Amazon, Alphabet, Oracle, and Apple — are on track
to spend approximately **\\$700 billion in capital expenditure this year**, nearly
**six times** 2022 levels. Over the next five years, cumulative spending is expected to
exceed **\\$3 trillion**.

Roughly **75%** of that capex — about **\\$450 billion** — is directly tied to AI
infrastructure: GPUs, specialized chips, data centers, and supporting equipment.

This is the most capital-intensive industrial buildout since the interstate highway
system. The difference is that highways were publicly planned and publicly funded.
Data centers are privately financed but impose public costs — on grids, water systems,
land markets, and municipal services.

---

### The 19 GW gap

Even with 124 GW of on-site gas in the pipeline, BNEF's base-case scenario projects a
**19 GW shortfall** by 2035 — demand that neither the grid nor behind-the-meter
generation can serve in time. That gap is larger than the entire generating capacity of
many U.S. states.

What fills it? The honest answer is: nobody knows yet. Nuclear (including SMRs) is
pre-commercial at data-center scale. Utility-scale renewables face their own
interconnection queues. Demand-side efficiency gains from more efficient AI chips are
real but historically get consumed by increased usage (Jevons paradox).

The most likely near-term outcome is **grid strain and price increases** in the regions
where data centers concentrate — which is why the PJM and ERCOT numbers above matter
so much for ratepayers.

---

### What this means for your community

If you're in a state where data centers are being proposed or built, this forecast
changes the negotiating landscape:

1. **The "we'll be a small part of the grid" argument is dead.** At 20% of national
   electricity and 34% in PJM, data centers are not marginal load. They are the
   dominant new demand source. Any developer who frames their facility as
   insignificant to the grid is contradicted by their own industry's forecasts.

2. **On-site gas plants need separate scrutiny.** A data center with its own gas
   turbines is an industrial power plant. It should face the same environmental
   review, air-quality permitting, and community notification as any other fossil-fuel
   generating facility. Don't let "behind the meter" mean "behind the curtain."

3. **Rate-impact analysis is non-negotiable.** With PJM capacity prices already
   reflecting data-center demand, every new large-load interconnection should trigger
   a ratepayer-impact study. If your utility or PUC isn't requiring one, ask why.

4. **Binding commitments beat press releases.** \\$700 billion in hyperscaler capex
   means enormous leverage for communities willing to negotiate. Use it. Demand
   community benefit agreements with annual reporting, rate-protection guarantees
   confirmed by utility testimony, water-use caps, decommissioning bonds, and local
   hiring commitments — before the vote, not after.

15 state legislatures have already considered temporary development bans. New York
enacted the first statewide moratorium. The political window for negotiating strong
community protections is open — but it won't stay open forever as developers lock in
sites and break ground.

> Model the local impact on the **Learn & Simulate** tab, check who's building
> near you on the **🏢 Data Centers** tab, and build your CBA on the
> **🛡️ Negotiation Toolkit** tab.
""",
    },
    # ── Amazon site-selection interview ───────────────────────────────────
    {
        "id": "amazon-oyer-site-selection-2026",
        "section": "stories",
        "title": "Amazon Says It Picks Sites Where the Grid Needs Help. Here's What Communities Should Hear.",
        "date": _dt.date(2026, 7, 20),
        "author": "GridWatch AI",
        "tags": ["Amazon", "AWS", "site selection", "water", "nuclear", "rates", "hyperscaler", "analysis"],
        "summary": (
            "In a Latitude Media interview, Amazon's energy chief laid out a sophisticated "
            "site-selection strategy — picking locations where new load 'benefits the grid,' "
            "pledging full cost coverage, and touting a 52% water-efficiency gain. The claims "
            "are worth understanding, because the playbook is coming to a town near you."
        ),
        "body": """\
A [Latitude Media interview published July 17](https://www.latitudemedia.com/news/inside-amazons-approach-to-data-center-sustainability-a-conversation-with-brandon-oyer/)
gives an unusually detailed look at how Amazon thinks about where to build data centers.
**Brandon Oyer**, who leads energy and water strategy for AWS, describes a site-selection
philosophy that has evolved from "where can we plug in renewables?" to **"where does the
grid actually need us?"** — a framing that, if taken at face value, turns the developer
from a burden on the grid into a benefactor.

The interview is worth reading in full, because the specific claims Amazon makes are
exactly the ones your planning board will hear when an AWS-affiliated LLC shows up at
a hearing. Here's what was said, what checks out, and what's missing.

---

### The site-selection thesis: "go where the grid benefits"

Oyer says Amazon invested in **transmission-system modeling experts with 20+ years
of experience** and shifted its strategy from finding spots to connect renewables to
analyzing where additional grid load would prove most beneficial. This approach, he
says, led to data center developments in **Jackson, Mississippi** and **South Bend,
Indiana**.

**What this means in practice:** Amazon is choosing locations where utilities have
excess capacity or aging infrastructure that needs investment to justify upgrades.
From the grid operator's perspective, a large anchor tenant *can* accelerate
infrastructure modernization that benefits everyone. From the community's perspective,
the question is whether that benefit is contractually guaranteed or just implied.

**The community question:** "Beneficial to the grid" and "beneficial to residents"
are not the same thing. A utility that gains a 200 MW anchor customer may improve
system economics while still socializing transmission costs. Ask: *Who pays for the
new substation? Is the rate benefit in writing, or in a press release?*

---

### The rate-protection claims

This is the most consequential section for communities. Oyer makes three specific
claims:

1. **Amazon covers the full cost** of electricity consumption and infrastructure
   improvements — transmission lines, substations, grid upgrades — **without passing
   expenses to other ratepayers.**

2. **Amazon signed the White House Ratepayer Protection Pledge** (March 2026),
   committing to fully cover AI data center electricity production costs.

3. **Evidence from two states:**
   - **Indiana:** Utility Indiana Michigan Power announced **customer base rate
     reductions** due to revenue from large customers like Amazon.
   - **Mississippi:** Entergy announced plans for an additional **\\$300 million in
     grid improvements at no cost to customers**, expected to reduce power outages
     by half within five years.

**What checks out:** The White House pledge is real and public. Rate reductions in
Indiana Michigan Power's territory have been reported. Entergy's Mississippi grid
investment has been announced.

**What's missing:** These are developer-sourced claims presented without independent
utility or regulatory confirmation. The critical distinction — which the interview
doesn't address — is between **direct** costs (the data center's own interconnection
and consumption) and **indirect, system-wide** costs (capacity-market impacts,
transmission overbuild, peak-load socialization). As we detailed in our
[utility-bill explainer](#), PJM's independent market monitor found data centers were
responsible for **63% of an 833% capacity-price increase** — even though each
individual facility paid its direct costs in full.

A data center can simultaneously (a) pay more than its direct cost-to-serve and
(b) drive up system-wide capacity costs that land on everyone else's bill. Amazon's
claims address (a). Your electric bill reflects (b).

**What to demand:** Don't accept "we pay our own way" as the full answer. Ask your
PUC or utility commission: *Has the utility filed testimony confirming that this
facility's load will not increase residential capacity charges?* That's a testable,
auditable claim — and it's the one that matters.

---

### The clean-energy portfolio

Oyer cites Amazon's carbon-free energy portfolio:

- **700+ projects globally**
- **42 gigawatts** of capacity
- Enough to power **12.1 million U.S. homes**

These are large numbers. They represent **contracted or announced** capacity — not
necessarily operational generation at the time and place the data center is consuming
power. The distinction between a Power Purchase Agreement signed today and electrons
flowing to a facility tomorrow is one the industry routinely elides.

Amazon also touts its **\\$500 million investment in X-energy** for small modular
reactors (SMRs), starting at **80 MW** per unit, partnered with **Energy Northwest**
for offtake commitments. Oyer frames this as potentially establishing an industry
model for nuclear deployment without ratepayer financial risk.

**Community note:** SMRs remain pre-commercial. No SMR has delivered power to a U.S.
data center. The X-energy investment is a bet on future technology, not a
current-state energy source. When a developer tells your planning board the facility
will be powered by nuclear, ask: *When? And what powers it until then?*

---

### The water claims — and what "water positive" means

The water section contains the most specific operational data:

- **52% improvement in water use effectiveness** between 2021 and 2025
- **75% toward water-positive status by 2030**
- **Project Rainier** in Northern Indiana: a **2.2 GW campus** that requires water
  cooling for only **2–3% of the year**, relying on outside air for **97–98%**

Regional water replenishment projects cited:

| Region | Investment | Claimed impact |
|--------|-----------|----------------|
| Mississippi | Precision irrigation tech | Reduce ag water withdrawals by **150M gallons/year** |
| Mexico | Infrastructure repair | Replenish **2.5B liters/year** |
| Oregon | \\$235M surface water supply | Amazon uses **5%** of capacity; **95%** serves region |

Amazon also says it prioritizes switching from potable to recycled water (treated
sewage) where possible.

**What's credible:** Cold-climate and arid-climate designs genuinely differ in water
intensity. A facility in Northern Indiana *will* use less evaporative cooling than one
in Phoenix. The 52% WUE improvement is plausible given the industry trend toward
air-cooled and hybrid designs.

**What's missing:** "Water positive" is a corporate-defined metric, not a regulatory
standard. It typically means the company funds water-replenishment projects *somewhere*
that offset the volume consumed *somewhere else*. If your aquifer drops, the fact that
Amazon funded an irrigation project in Mississippi doesn't refill it. The relevant
question is always local: *What is the net water impact on this watershed, this
aquifer, this municipal supply?*

**What to demand:** Facility-level water-use disclosures (gallons per day, source,
and discharge), not global averages. If the developer cites "water positive," ask:
*Where is the replenishment, and does it benefit this community's water supply?*

---

### The missing voices

The most important thing about this interview is what it *doesn't* contain: no
critical questions, no independent verification, and no community voices offering
counterpoints. This is Amazon's narrative, presented on Amazon's terms.

That's not a criticism of the journalism — corporate profile interviews serve a
purpose. But communities should recognize the format for what it is: a **pre-packaged
site-selection pitch**. Every claim Oyer makes is the claim your planning board will
hear, often verbatim, when the development agreement comes up for a vote.

Oyer's closing line captures the tone: *"From the top of Amazon leadership, all the
way to the people who are building and monitoring our substations, we're all aligned
on the mission: build responsibly, build economically, and strive to be the most
responsible partner."*

That's a corporate value statement. Your job is to convert it into **contractual
commitments** — CBAs, rate guarantees, water-use caps, decommissioning bonds — before
the vote, not after.

---

### What to do with this

If Amazon (or any hyperscaler) is siting in your community, this interview is a
useful decoder ring for the pitch you're about to receive:

1. **They'll say they benefit the grid.** Ask your utility to confirm, in filed
   testimony, that the facility will not increase residential rates or capacity
   charges.

2. **They'll cite clean energy commitments.** Ask what percentage is operational
   *today* at *this* facility, versus contracted for future delivery elsewhere.

3. **They'll tout water efficiency.** Ask for facility-level daily water consumption,
   source, and whether "water positive" credits benefit your local watershed.

4. **They'll promise jobs and investment.** Ask for a binding community benefit
   agreement with annual reporting, clawback provisions if commitments aren't met,
   and a decommissioning bond.

The hyperscalers aren't wrong that well-sited data centers can benefit a community.
But "can benefit" and "will benefit" are separated by a contract. Get it in writing.

> Model the numbers on the **🛡️ Negotiation Toolkit** tab, check the operator's
> footprint on the **🏢 Data Centers** tab, and review Amazon's environmental data
> on the **📊 Corporate Profiles** tab.
""",
    },
    # ── Port Washington / Stargate land rush ────────────────────────────────
    {
        "id": "port-washington-stargate-land-rush-2026",
        "section": "stories",
        "title": "A \\$15B Data Center Made Wisconsin Farmers Millionaires — and the Same Playbook Is Headed for 10 More Markets",
        "date": _dt.date(2026, 7, 18),
        "author": "GridWatch AI",
        "tags": ["Wisconsin", "Stargate", "emerging markets", "site selection", "eminent domain", "land value", "OpenAI", "Oracle", "case study"],
        "summary": (
            "In Port Washington, Vantage's \\$15B OpenAI–Oracle Stargate campus turned "
            "farmland into a lottery ticket — some sellers cleared millions, some wish "
            "they'd held out, and the neighbors who didn't sell face eminent domain. "
            "It's also a preview: the same power-first, low-opposition playbook is now "
            "spreading to 10 emerging markets, from Reno to Tulsa to New Mexico's "
            "\\$165B Stargate site."
        ),
        "body": """\
An [Inc. story this month](https://www.inc.com/georgia-fearn/15-billion-data-center-made-wisconsin-farmers-millionaires-some-wish-they-held-out/91373128)
put a human face on a number we track constantly: what a megawatt of AI infrastructure
is actually worth to the developer — and how little of that value the first sellers
tend to capture.

The setting is **Port Washington, Wisconsin**, a town of about 12,000 on Lake Michigan
in Ozaukee County. There, **Vantage Data Centers** is building the **"Lighthouse"
campus** — a **\\$15 billion-plus** development that is part of the **OpenAI–Oracle
Stargate** buildout. It sits on roughly **672 acres of former farmland** about a mile
inland from the lake, and is slated for completion around **2028**.

For the farmers who sold, the offer was life-changing. For the neighbors who didn't,
the same project is arriving as a condemnation notice.

### The quiet land rush

The land didn't change hands in one splashy announcement. Developers assembled it the
way they usually do — quietly, parcel by parcel, often through blandly-named LLCs so no
single seller could see the full picture. By the time the scale was public, buyers had
reportedly spent **\\$125 million-plus** assembling **more than 1,500 acres** in and
around Port Washington. One parcel alone
[sold for \\$9.3 million](https://biztimes.com/port-washington-land-sold-to-data-center-developer-for-9-3-million/).

The per-acre math is what turned heads. Prime Wisconsin cropland typically trades around
**\\$5,000–\\$10,000 an acre**. Sellers here were reportedly offered **as much as
\\$120,000 an acre** — more than ten times agricultural value. That's how a working
farm becomes a seven-figure check.

### Why some wish they'd held out

Here's the part the headline captures: *some sellers wish they'd held out.* That regret
isn't irrational — it's the predictable result of an **information asymmetry**.

When you're the first to sign, you're negotiating against a developer who knows exactly
how many acres it needs, how the parcels fit together, and what the whole campus is
worth. You know none of that. Early sellers priced their land against *farmland* comps.
The developer priced it against a **\\$15 billion campus** that couldn't be built without
it. Sellers who held their ground longer — or whose parcel turned out to be a
must-have for the site plan — generally did better than the neighbors who took the
first "generous" offer.

The lesson isn't "everyone should have held out forever." It's that **the developer's
walk-away price and yours are wildly different numbers, and only one side knew both.**

### The neighbors who didn't win the lottery

Selling your land was the good outcome. The harder story belongs to the residents who
**didn't** sell — and are being pulled into the project anyway.

Powering the campus requires up to **~900 MW** of electricity, which means new
high-voltage **transmission lines and substations**. Those lines have to cross private
property that was never for sale. The **American Transmission Company** can acquire the
easements it needs through **condemnation — eminent domain** — the government's power to
force a sale for "public use." Some property owners, including
[Wisconsin artist Tom Uttech](https://abcnews.com/US/600-acre-ai-data-center-cost-wisconsin-residents/story?id=130153006),
are working with legal organizations to fight it.

Sit with the asymmetry: the farmer who sold got \\$120,000 an acre. The neighbor whose
land is taken for the wires that feed the same campus gets an **easement valuation** —
and no windfall. Same project. Opposite ends of the leverage curve.

### What the town was promised

Vantage's public case for the project is the familiar mix of jobs and growth:
**1,000+ long-term jobs**, an estimated **\\$2.7 billion** contribution to Wisconsin's
GDP, and roughly **\\$175 million** toward local power, water, and transport upgrades.
The company also says a majority of the campus's power will come from zero-emission
resources.

Treat those as the developer's projections, not settled facts — the jobs figure in
particular tends to shrink between the press release and the finished, largely-automated
building (a **200 MW data center typically employs 50–150 people** once operational, as
we detail in the ERCOT and moratorium pieces below). The point isn't that the numbers
are worthless; it's that they're the *opening bid* in a negotiation, not the final
accounting.

### Port Washington isn't an outlier — it's the template

The reason this story matters beyond one Wisconsin town: the same playbook is being run
in dozens of places at once. A [CommercialSearch survey of emerging data-center markets](https://www.commercialsearch.com/news/10-emerging-data-center-markets-to-watch/)
(July 2026) makes the pattern explicit — site selection has flipped from *network
connectivity* toward **power availability, cheap land, and "minimal permitting
obstacles."** In plain terms, developers are hunting for exactly what Port Washington
offered: large rural parcels, an accommodating grid, and neighbors who haven't organized
yet.

Two of these campuses are literally the **same OpenAI–Oracle Stargate program** as
Wisconsin's — Port Washington in the Midwest, and **Project Jupiter**, a **\\$165 billion**
hyperscale facility with Oracle as anchor tenant, in New Mexico's borderplex. This isn't
ten unrelated projects. It's one buildout, spreading.

Here are the ten markets on the watch list — and the friction already surfacing in them:

| Market | Why it's on the list | Marquee project(s) | Community friction so far |
|--------|----------------------|--------------------|---------------------------|
| **San Antonio / Austin, TX** | Fastest-growing US hub, ~50 facilities | CloudBurst 1.2 GW (\\$14.5B); Microsoft \\$1.5B | Water-supply scrutiny |
| **West Texas** | Off-grid gas + solar, cheap land | GW Ranch 7.65 GW (largest permitted); Meta El Paso \\$10B | Air permits for on-site gas |
| **Columbus, OH** | Sales-tax exemption, fast permits | Meta & EdgeConneX, New Albany | Rate-impact questions |
| **Reno, NV** | Silicon Valley overflow, no corp. tax | Vantage \\$3B / 224 MW; Switch 650 MW | Growth-pace concerns |
| **Kansas City, MO** | Fiber crossroads | Google "Project Kestrel" \\$100B; Meta \\$1B | Moratorium debates; proof-of-power zoning |
| **Salt Lake City, UT** | "Silicon Slopes," cold-air cooling | Stratos 7.5 GW | Pushback cut Stratos by 19,000+ acres; Great Salt Lake water |
| **Memphis, TN** | "Digital Delta" fiber + aquifer | xAI Colossus ~2 GW; Google \\$1B (W. Memphis) | Water + air-quality fights |
| **Omaha, NE** | Tier-2 as Northern Virginia maxes out | Google; Meta Sarpy County | Incentive scrutiny |
| **Albuquerque, NM** | Phoenix / Dallas alternative | Project Jupiter \\$165B (OpenAI Stargate) | Neighboring-county moratoriums; groundwater |
| **Tulsa, OK** | Cheap renewable power, big parcels | Meta "Anthem" \\$1B; Beale "Clydesdale" \\$3B | Moratorium (Meta exempted) |

Look at the last column. In **at least half** of these "emerging" markets — Kansas City,
Salt Lake, Albuquerque, Tulsa, Omaha — organized opposition, moratoriums, or new zoning
guardrails *already exist*, sometimes before ground is broken. The pattern we flagged in
our Morgan Stanley analysis holds: the capital follows the path of least resistance —
and the resistance is learning to get there first.

If your metro is on this list, Port Washington is your preview. The window to negotiate
opens *before* the quietly-named LLCs have bought the first 500 acres — not after.

### What this means for your community

Port Washington is a preview of what a Stargate-scale campus does to a rural land market —
and a checklist of what to get right before the offers start:

**1. Assume the developer knows more than you do.** They've mapped every parcel and
priced the whole campus. If offers are arriving quietly through LLCs, that's a signal
the assembly is bigger than any one seller is being told. Our **Data Centers** tab lists
the LLCs hyperscalers use so you can connect a local filing to its parent.

**2. Neighbors have more leverage together than apart.** Piecemeal selling is exactly
the dynamic that leaves early sellers with regret. Landowners who compare notes — or
negotiate as a bloc — close the information gap the developer relies on.

**3. The windfall and the burden land on different people.** Sellers get millions;
neighbors get transmission easements and eminent domain. A **community benefit agreement**
negotiated *before* the permit vote is how a town spreads the upside and cushions the
people carrying the cost. Model one on the **Negotiation Toolkit** tab.

**4. Fight the fights that actually convert.** As we've documented, the data-center
defeats that stick often turn on **procedure and grid/transmission terms**, not vibes —
the environmental review, the routing of the lines, the ratepayer impact of ~900 MW of
new load. Put those objections on the record with the people who vote. Use the
**States & Officials** tab.

### So how does a community actually capture the value?

Diagnosing the asymmetry only helps if it points to action. Here is the toolkit
communities use to turn a data center from a windfall-for-a-few into shared, durable
local value — roughly in order of leverage:

**1. Negotiate the land as a bloc, not parcel by parcel.** The single biggest value leak
in Port Washington was sequential selling. Landowners who form a negotiating group — or
grant a shared option to one broker or attorney — deny the developer its favorite tactic:
picking people off one at a time at farmland prices. If the campus can't be built without
your collective acreage, price it against the campus, not the crop. It works: in **Salem
Township, Pennsylvania, 96 landowners pooled ~1,700 acres and sold together** to QTS (a
Blackstone company) for **\\$586 million** — about **\\$330,000 an acre** — and a second
neighborhood bloc has since lined up a ~\\$1.2 billion follow-on. Same AI land rush as
Wisconsin; opposite outcome, because they moved as one. *(The Toolkit tab now has a
"Negotiate as a bloc" playbook, a model no-individual-deals clause, and a downloadable
checklist.)*

**2. Put the money in a Community Benefit Agreement — before the permit vote.** A CBA is a
legally binding contract, separate from zoning, in which the developer commits cash and
concessions in exchange for community support. Leverage is highest before the vote and
near-zero after. New York's EO 62 set a public benchmark: **~\\$1 million per megawatt** as
a starting point — a ~900 MW campus like Port Washington's would *open* negotiations near
**\\$900 million** in community benefits. Model your own on the **🛡️ Negotiation Toolkit** tab.

**3. Replace the tax abatement with a host fee or PILOT.** The standard deal — a 10–20 year
property-tax abatement — starves exactly the schools and roads that absorb the impact.
Counter with a **Payment In Lieu Of Taxes** or an **annual host fee** (per MW or per acre)
that escalates with inflation and starts on day one. A megawatt of always-on load can
support a recurring payment, not just a one-time check.

**4. Set up a data dividend — the Alaska model.** Alaska pays every resident an annual
dividend from oil revenue. A community can structure the same thing: route a slice of the
host fee or a per-MWh levy into a **permanent local fund** that pays residents or
underwrites property-tax relief for the life of the facility. That's the difference between
a few farmers getting rich once and the whole town getting a raise for 30 years. The
**Data Dividend calculator** on the Negotiation Toolkit tab sizes it.

**5. Make the data center pay for its own grid.** The ~900 MW is the biggest hidden cost:
if its new generation and transmission get socialized, everyone's electric bill rises (see
the capacity-charge story below). Demand a **large-load tariff** that assigns the full cost
of new generation and transmission to the facility, plus closed-loop cooling and
water-replenishment commitments in writing.

**6. Get the transmission-corridor neighbors paid — recurring, not one-time.** For the
residents facing eminent domain, push for above-market easements structured as **annual
line-rental payments** rather than a single condemnation check, plus routing that avoids
homes. The people carrying the wires should share the upside, not just the burden.

**7. Bond the exit.** Data centers become obsolete. Require a **decommissioning bond** up
front so the town isn't left with a stranded concrete shell and a cleanup bill.

The through-line: value you capture **contractually, before the vote, and structured as
recurring revenue** beats a one-time land check every time. A land sale pays the person who
holds the deed; a CBA, a host fee, and a data dividend pay the whole community — including
the neighbors who never got an offer.

### Where to find the numbers (close the information gap yourself)

Every mechanism above depends on knowing what your land and your megawatts are actually
worth. Most of that price signal is **public** — communities just don't know where to look.
Here's where it lives:

- **County Register of Deeds / Recorder** — the strongest signal of all. Every land sale
  is public record, so the developer has *already told you* what it will pay: look up what
  the neighbor who sold first actually got. (In Port Washington, the "\\$9.3 million parcel"
  figure came straight from public records.)
- **USDA NASS QuickStats & Land Values Summary** — the agricultural baseline, free:
  cropland value in \\$/acre by state and county. This is your "before AI" floor — the
  number the developer's premium multiplies. *(Now built into the app — see below.)*
- **Federal Reserve district Ag-Credit surveys** (Chicago, Kansas City, Dallas, Minneapolis
  Fed) — quarterly farmland-value trends.
- **Good Jobs First "Subsidy Tracker"** — every tax abatement and subsidy already handed to
  a data center, by locality. Shows what other towns gave away — and to whom.
- **New York's EO 62 Community Investment Framework** — the public **~\\$1M/MW** community
  benefit benchmark to anchor a CBA.
- **CBRE / JLL / Cushman & Wakefield** data-center market reports — what a megawatt of
  capacity actually rents for, so you can price the campus the way the operator does.
- **Your state PUC dockets** (Wisconsin: the PSC) — the transmission and large-load
  filings that reveal the grid cost, and the easements headed for your neighbors.

We wired the first two into the **🛡️ Negotiation Toolkit** tab: a **Land price-discovery**
tool now shows the USDA cropland baseline for your state, converts any per-acre offer into a
multiple over farmland value, and links straight to your county's deed records and the live
USDA and Good Jobs First databases. Diagnose the asymmetry, then close it.

### The bottom line

The Port Washington story gets told as a feel-good windfall — farmers made
millionaires overnight. That's true, and it's also the smaller half of the story. The
full version is about **who had the information and who didn't**: a developer that knew
the campus was worth \\$15 billion, sellers who priced against soybeans, and neighbors
who get the wires but not the check.

Communities can't stop the AI land rush from coming. But they can refuse to negotiate
in the dark — which is the one condition under which everybody but the developer
loses.

> Model the numbers on the **🛡️ Negotiation Toolkit** tab, trace the operators and
> their LLCs on the **🏢 Data Centers** tab, and put your objection on the record via
> the **🗂️ States & Officials** tab.
""",
    },
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

- The **2025/26 capacity auction** price jumped **833%** — from \\$28.92 to \\$269.92
  per MW-day
- PJM's independent market monitor found data centers were responsible for **63%**
  of that price increase
- **Pepco** customers in Washington D.C. saw bills rise **\\$21/month**, with roughly
  half attributable to capacity costs
- Across the PJM footprint, residential bills increased **\\$15–21/month** from
  capacity charges alone

That's not a rate increase driven by fuel costs, inflation, or your usage. It's a
rate increase driven by someone else's load.

### 44 hours that could save \\$150 billion

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
- Potential avoided infrastructure cost: **\\$150 billion or more** in new power plants
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
\\$50 million in capacity obligations."

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
centers generate **\\$3.4 million in surplus revenue** per 100 MW facility — paying more
than their direct cost to serve. This is the industry's primary counterargument to the
"ratepayers are subsidizing data centers" narrative.

**The critical nuance:** both things can be true simultaneously. A data center can pay
more than its direct cost-to-serve while *also* driving up system-wide capacity costs
that are socialized to everyone. E3's facility-level analysis and PJM's system-level
market monitor are measuring different things. The surplus at the meter doesn't capture
the externality at the auction.

**Columbia University (2025)** showed that grid-enhancing technologies (dynamic line
ratings, power flow controllers) could release 20–40% more capacity from existing
transmission — deferring \\$10–30 billion in new construction.

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
  at 0.19 L/kWh, partly because of its colder-climate sites in Luleå and Clonee.

- **Off-site (indirect) water.** Thermoelectric power plants — coal, gas, and nuclear —
  withdraw enormous volumes for steam cooling. When a data center draws from a
  coal-heavy grid, the water embedded in its electricity can **dwarf** the water
  used on-site. The US Geological Survey estimates 1.5–2.0 L/kWh for coal generation.

The **Footprint calculator** (Technical deep-dive tab) accounts for both: open
its *Water methodology* panel to pick an operator WUE and a grid mix, and it
splits your water footprint into on-site and off-site components.

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

> Use the **Footprint calculator** (Technical deep-dive tab) to estimate the
> water footprint of your own AI usage, and the **Grid Timing** tab to understand
> how the generation mix in your region affects both carbon *and* water.
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
   windy afternoons. Developers can contract for renewable PPAs at \\$20–25/MWh.

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
        "title": "How the Industry Files Your Protest: 'Social License' and the \\$64B Risk Column",
        "date": _dt.date(2026, 7, 11),
        "author": "GridWatch AI",
        "tags": ["community", "policy", "site-selection", "risk", "zoning"],
        "summary": (
            "Data-center developers don't have a risk category called 'protests.' They "
            "have 'social license to operate' — and organized community opposition has "
            "now blocked or delayed an estimated \\$64 billion in projects. Here's how the "
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
| U.S. investment **blocked** by opposition (since mid-2024) | **~\\$18 billion** |
| Investment **delayed** by opposition | **~\\$46 billion** |
| Total affected investment | **~\\$64 billion** |
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
    # ── Resource-extraction precedent: property-value guarantees & data dividends ──
    {
        "id": "resource-extraction-precedent-2026",
        "section": "stories",
        "title": "They Figured This Out Fifty Years Ago: What Oil, Wind, and Pipeline Towns Already Know About Protecting Neighbors",
        "date": _dt.date(2026, 7, 26),
        "author": "GridWatch AI",
        "tags": ["property values", "buyouts", "Alaska model", "data dividends",
                 "community benefits", "precedent", "wind", "pipeline", "oil",
                 "negotiation", "toolkit"],
        "summary": (
            "Property-value guarantees, voluntary buyouts, and community dividend "
            "funds aren't new ideas — they're battle-tested tools from decades of "
            "oil, wind, and pipeline fights. Data center communities are just the "
            "latest to need them, and the first to have the leverage to demand "
            "them all at once."
        ),
        "body": """\
Every few years a new extractive industry discovers rural America and acts
like no one has ever negotiated with a community before. Right now it's data
centers. A decade ago it was wind farms. Before that, pipelines. Before that,
oil and gas. The technology changes; the playbook doesn't — and the communities
that know the playbook get fundamentally different deals than the ones that don't.

This post is about three tools that resource-extraction communities perfected
long before anyone heard the phrase "hyperscaler" — and why data center towns
should be demanding all three right now.

---

### Tool 1: Property-value guarantees

**The precedent:** In the early 2010s, wind energy developers in the Midwest
ran into a problem. Residents near proposed turbine sites objected that the
projects would crater their property values. The developers responded by
citing studies — most notably [Lawrence Berkeley National Laboratory's
2013 analysis of 50,000+ home sales](https://emp.lbl.gov/publications/spatial-hedonic-analysis-effects) —
that found "no statistical evidence" of measurable regional impact. Both
sides had a point: regional averages did wash out, but the family 800 feet
from a 300-foot turbine had a different experience than the family two
miles away.

The resolution was a mechanism called a **property-value assurance program
(PVAP)**: the developer gets an independent appraisal of nearby homes
*before* construction, then commits in writing that if the homeowner sells
within a set period (typically 5–10 years) and the sale price is below the
pre-project appraisal, **the developer pays the difference.**

PVAPs showed up in wind siting agreements across the Midwest. Notable
examples: [Invenergy's Bishop Hill and Big Sky wind projects in
Illinois](https://www.invenergy.com/) built PVAPs into their county siting
agreements; the Ontario Ministry of the Environment required a
comparable [property value protection plan under the Green Energy Act](https://www.ontario.ca/laws/statute/09g12);
and the American Wind Energy Association's model siting handbook has
[cataloged PVAP terms](https://www.cleanpower.org/) since 2014. Pipeline
companies offered similar "diminution of value" payments during contentious
FERC certificate proceedings — see FERC's discussion in
[Mountain Valley Pipeline, 161 FERC ¶61,043 (2017)](https://www.ferc.gov/media/mountain-valley-pipeline).
The legal structure exists. The accounting is straightforward. The mechanism works.

**Why data centers should be next:** The argument is identical. Developers
cite regional studies. Neighbors 300 feet from the fence line experience
noise, light pollution, traffic, and visual blight that don't register in a
county-wide average. A property-value guarantee doesn't argue about whether
the impact is real — it simply says: if you're right that it won't hurt
values, this costs you nothing; if the neighbors are right, you make them
whole.

**The honest caveat:** PVAPs are well-established in wind and pipeline siting
but still uncommon in data center deals specifically. That means the community
that demands one *first* sets the benchmark — and it's a reasonable ask
precisely because the mechanism is proven in analogous contexts.

---

### Tool 2: Voluntary buyouts

When mitigation and guarantees aren't enough — when the home is simply too
close to live comfortably — the next step is a **voluntary buyout**: the
developer purchases the property at a fair or above-market price so the
family can relocate.

This isn't hypothetical.

**Mason County, West Virginia** — the site of the 2 GW Fundamental Data
campus profiled by [Mountain State Spotlight](https://mountainstatespotlight.org/2026/07/23/data-center-sidestep-oversight/) —
became the first jurisdiction to formalize a "Good Neighbors" style buyout
program for homes closest to a data center site. The program offers the
highest of three independent appraisals plus a relocation premium — meaning
the homeowner gets *above* fair market value by design. The structure borrows
directly from [FEMA's Hazard Mitigation Grant Program buyouts](https://www.fema.gov/grants/mitigation/hazard-mitigation),
which have relocated more than 45,000 flood-prone properties since 1989,
adapted for industrial siting.

**Ashburn, Virginia** — the epicenter of U.S. data center development, with
[roughly 25 million square feet of capacity](https://www.washingtonpost.com/business/2024/01/29/data-centers-loudoun-power-northern-virginia/)
concentrated in Loudoun County — has seen developers offer homeowners
adjacent to expanding campuses approximately **\\$4 million per home**
([Washington Post, 2024](https://www.washingtonpost.com/business/2024/01/29/data-centers-loudoun-power-northern-virginia/))
to assemble buffer land around their facilities. These aren't charitable
gestures; they're land-assembly economics. A \\$4M buyout is a rounding
error on a \\$2B campus, and clearing the adjacent parcels eliminates the
noise complaints (documented at 60–75 dBA at the fence line by
[Piedmont Environmental Council monitoring](https://www.pecva.org/work/data-centers/)),
the zoning opposition, and the litigation risk in one transaction.

**The key principles** for a fair buyout program:

- **Voluntary.** The owner decides whether to sell. A program that pressures
  holdouts is a forced taking in disguise.
- **Above-market pricing.** The highest of multiple independent appraisals,
  plus a premium for involuntary disruption.
- **Relocation assistance.** Moving costs, temporary housing, and a
  reasonable timeline (6–12 months minimum).
- **Leverage note:** If the project requires a rezoning that needs unanimous
  or near-unanimous consent, holdouts have real negotiating power. Use it
  to negotiate, not just to block.

---

### Tool 3: The Alaska Model — community dividend funds

This is the big idea, and it comes from the biggest resource-extraction deal
in American history.

In 1976, as North Slope oil revenues flooded into Alaska, Governor Jay Hammond
faced a choice: let the legislature spend the windfall year by year, or create
a structure that would pay Alaskans directly — and permanently. He chose the
[**Alaska Permanent Fund**](https://apfc.org/): a constitutionally protected
trust ([Article IX, § 15 of the Alaska Constitution](https://ltgov.alaska.gov/information/alaskas-constitution/))
that invests oil royalties and distributes annual dividends to every resident
of the state. Since 1982, the [Permanent Fund Dividend](https://pfd.alaska.gov/)
has paid out over **\\$30,000 per person** in cumulative dividends. The
principal [now exceeds **\\$80 billion**](https://apfc.org/report-archive/).

The logic is simple: *if they're extracting your resources, you deserve a
share of the value — not just jobs and a press release, but actual money.*

**Why this applies to data centers:**

A data center consumes the same kinds of community resources that oil
extraction does — just in a different form:

| Oil & gas | Data center equivalent |
|-----------|----------------------|
| Mineral rights | Land (often farmland at 10–40x agricultural value) |
| Water for fracking | Water for cooling (millions of gallons/day) |
| Pipeline capacity | Grid capacity (substations, transmission lines) |
| Road damage from trucks | Grid strain on ratepayers' bills |
| Royalty payments | Nothing — unless you negotiate |

The last row is the one that matters. Oil-producing states levy severance
taxes and require royalty payments because the resource is finite and the
community bears the costs of extraction. Data center communities bear
equivalent costs — water drawdown, grid strain, noise, property-value
risk — but most get nothing beyond the developer's property tax bill
(which is often abated anyway).

**The data dividend model:**

1. **Levy the fee.** A small surcharge (1–3%) on the facility's annual
   electricity consumption — not a tax on the company, but a fee for the
   community infrastructure their load demands. Virginia's
   [H.B. 30 (2026)](https://lis.virginia.gov/cgi-bin/legp604.exe?261+ful+HB30)
   already established a \\$0.011/kWh consumption tax on data centers with
   a \\$600M annual revenue cap; see the
   [JLARC analysis of Virginia's data center tax structure](http://jlarc.virginia.gov/pdfs/reports/Rpt598.pdf)
   for the fiscal modeling.
2. **Create the fund.** Revenues flow into a ring-fenced Community Data
   Dividend Trust — a separate account that cannot be raided for general
   spending, governed by an independent board with resident representation.
3. **Distribute the dividend.** The fund pays out annually as direct
   payments to households, free or reduced childcare, technical education
   scholarships, or residential utility bill credits. The community votes
   on the allocation.

A 200 MW facility paying a 2% infrastructure fee would generate roughly
**\\$2M per year** — or **\\$80 per household per year** in a community of
25,000 homes. Over 20 years, that's a \\$40M trust fund from a single facility.

The Alaska Permanent Fund works because it was constitutionally protected
from legislative raids and because the revenue source (oil) was large
enough to matter. Data centers meet both conditions: the revenue is real,
and a ring-fenced trust can be structured to survive changes in local
government.

---

### Tool 4: Severance-style taxation

Oil, gas, and mining states have used **severance taxes** for a century to
capture value from resource extraction. Wyoming, Alaska, North Dakota, and
Texas all levy per-unit taxes on hydrocarbons produced — the
[National Conference of State Legislatures maintains a state-by-state
comparison](https://www.ncsl.org/energy/oil-and-gas-severance-taxes).
Wyoming's severance tax alone [generates over \\$800M/year](https://revenue.wyo.gov/divisions/mineral-tax)
and funds the state's Permanent Mineral Trust Fund, a smaller cousin of
Alaska's structure.

The data-center equivalent is a **per-megawatt or per-kWh compute severance
tax** — treating grid capacity and water withdrawal as the extractable
resources they functionally are. Ohio and Georgia have quietly begun
debating versions of this;
[Georgia's 2024 sales-tax exemption fight](https://www.ajc.com/politics/data-center-tax-break-veto-georgia/) —
where Governor Kemp vetoed a suspension of the exemption after industry
lobbying — is a preview of what the political fight looks like when a state
tries to *remove* an existing subsidy, let alone add a new fee.

The takeaway: the tax code already knows how to price extractive industry.
The question is whether legislators apply the same framework to compute
that they applied to coal.

---

### Why all four at once

These aren't alternatives — they're layers. A community facing a data center
proposal should demand:

1. **Property-value guarantees** for the closest neighbors — because the
   developer claims there's no impact, so the guarantee should cost them
   nothing.
2. **A voluntary buyout program** for homes within the immediate impact
   zone — because some proximity effects can't be mitigated by a sound
   wall.
3. **A community dividend fund** for everyone — because the facility
   extracts community resources for 20+ years and the community deserves
   an ongoing share of that value.
4. **Severance-style taxation** at the state level — because the local CBA
   captures site-specific impact but the state carries the aggregate grid
   and water cost.

None of these are radical. Property-value guarantees are standard in wind
siting. Buyout programs exist in flood zones, pipeline corridors, and now
in Mason County, WV. Community dividend funds are the operating model of a
state that has paid residents from resource extraction since 1982.
Severance taxation is how every major energy-producing state already
handles extractive industry.

What's radical is accepting a data center without any of them.

---

### The leverage moment

Data center developers need three things from your community that they
cannot get anywhere else: **your land, your water, and your grid.** Those
are the same categories of resource that oil companies need from Alaska,
that pipeline companies need from Appalachia, and that wind developers need
from the Great Plains.

In every one of those industries, the communities that organized early and
demanded structured protections — royalties, value guarantees, buyout
programs, trust funds — got fundamentally different outcomes than the ones
that took the first offer. The playbook exists. The legal structures exist.
The precedent exists.

The only question is whether your community knows to ask.

> Use the **Negotiation Toolkit** tab to model the Data Dividend for your
> community, explore model CBA clauses, and see the "Protecting the closest
> neighbors" section for the full five-remedy ladder — from developer-paid
> mitigation through litigation as a backstop.

---

### Sources

**Property-value guarantees (PVAPs):**

- [Lawrence Berkeley National Laboratory, *A Spatial Hedonic Analysis of the Effects of Wind Energy Facilities on Surrounding Property Values* (2013)](https://emp.lbl.gov/publications/spatial-hedonic-analysis-effects) — foundational study on wind and property values
- [Ontario Green Energy Act, 2009, S.O. 2009, c. 12](https://www.ontario.ca/laws/statute/09g12) — statutory basis for Ontario's PVP requirements
- [FERC, Mountain Valley Pipeline Order, 161 FERC ¶61,043 (2017)](https://www.ferc.gov/media/mountain-valley-pipeline) — pipeline diminution-of-value precedent

**Voluntary buyouts:**

- [FEMA, Hazard Mitigation Grant Program — property acquisitions](https://www.fema.gov/grants/mitigation/hazard-mitigation) — 45,000+ flood buyouts since 1989
- [Mountain State Spotlight, "How West Virginia's data center law sidesteps oversight" (July 2026)](https://mountainstatespotlight.org/2026/07/23/data-center-sidestep-oversight/) — Mason County context
- [Washington Post, "The staggering ecological impact of Northern Virginia's data centers" (Jan 2024)](https://www.washingtonpost.com/business/2024/01/29/data-centers-loudoun-power-northern-virginia/) — Ashburn \\$4M buyout economics
- [Piedmont Environmental Council, Data Center coverage](https://www.pecva.org/work/data-centers/) — Northern Virginia fence-line noise monitoring

**Alaska Permanent Fund & community dividends:**

- [Alaska Permanent Fund Corporation — annual reports](https://apfc.org/report-archive/) — current AUM and dividend history
- [Alaska Constitution, Article IX, § 15](https://ltgov.alaska.gov/information/alaskas-constitution/) — constitutional protection of the fund
- [Permanent Fund Dividend Division](https://pfd.alaska.gov/) — historical PFD payout data
- [Virginia H.B. 30 (2026)](https://lis.virginia.gov/cgi-bin/legp604.exe?261+ful+HB30) — \\$0.011/kWh data-center consumption tax
- [JLARC, *Data Centers in Virginia* (Rpt. 598, 2024)](http://jlarc.virginia.gov/pdfs/reports/Rpt598.pdf) — fiscal analysis of Virginia's data-center tax structure

**Severance taxation:**

- [NCSL, Oil and Gas Severance Taxes — state-by-state comparison](https://www.ncsl.org/energy/oil-and-gas-severance-taxes)
- [Wyoming Department of Revenue, Mineral Tax Division](https://revenue.wyo.gov/divisions/mineral-tax) — \\$800M+/yr in severance receipts
- [Atlanta Journal-Constitution, "Kemp vetoes data center tax break suspension" (2024)](https://www.ajc.com/politics/data-center-tax-break-veto-georgia/) — political economy of removing an existing subsidy
""",
    },
]
