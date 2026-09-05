"""
Blog content — curated stories and project narrative for the GridWatch AI blog tab.
Each story is a dict with: id, section, title, date, author, summary, body (markdown),
and optional tags. Sections: "stories" for reported pieces, "about" for project mission.

`art` names the generated hero illustration (see `src/blog_art.py` for the theme
keys). It's optional — `blog_art.theme_for()` guesses from the id/title/tags when
it's missing — but set it explicitly: the keyword guess reads the whole tag list
and picks up the wrong subject often enough not to be trusted.
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

- **Open coefficients, cited sources.** Every number on the
  [impact calculator](/impact.html) links to the primary disclosure or peer-reviewed
  study it came from — IEA, Google, Epoch AI, ML.ENERGY, EPRI, EIA, PJM. Nothing is
  inferred or editorialized, and where a figure is an estimate we say so.
- **Every claim carries its date and its document.** The
  [moratorium tracker](/moratoriums.html) records where communities have paused or
  banned data centers, and each row carries the ordinance or council record behind it
  plus the date we last read it. A row we could not source is labelled unverified
  rather than quietly presented as fact, and a moratorium that has lapsed says so —
  because a resident who cites an expired pause at a hearing loses the room.
- **The paper trail, not the press release.** The
  [project tracker](/projects.html) points at where a campus's public record actually
  lives — state environmental permits, county filings, the interconnection queue, the
  PUC docket — and distinguishes a public register from a search query, because those
  are different claims.
- **Community voice, front and center.** The [story tracker](/story-tracker.html)
  archives local reporting by locality so the concerns of residents — noise, water
  draw, rate hikes, zoning fights — are as visible as a company's sustainability
  report. Headlines are grouped automatically and labelled as such.
- **Direct civic action.** [Officials](/officials.html) and the
  [scorecard](/scorecard.html) put every senator, representative, and governor one
  click away, with documented data-center positions where they exist and *no record
  found* where they do not. [Start here](/start-here.html) walks you through the
  three weeks before a zoning vote.

Everything here is a static page built from committed data. There are no accounts,
no trackers beyond a privacy-preserving page counter, and nothing to install — the
site loads on a phone in a council parking lot, which is where a lot of it gets read.

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
    {
        "id": "nc-august-moratorium-wave-2026",
        "art": "moratorium",
        "section": "stories",
        "title": "North Carolina Added Eight Data Center Pauses in August. Read the Fine Print Before You Cite One.",
        "seo_title": "North Carolina data center moratoriums: August 2026's eight votes",
        "date": _dt.date(2026, 9, 5),
        "author": "GridWatch AI",
        "tags": ["North Carolina", "moratoriums", "local government", "zoning"],
        "summary": "Eight North Carolina councils and county boards paused data centers in August, or extended a pause that was about to lapse. The terms range from six months to two years, and half of them carry a size threshold or a geographic carve-out that a resident quoting them at a hearing needs to know about.",
        "body": """
North Carolina's data center pauses came in a cluster last month. Between
August 3 and August 25, five county boards and three city councils either
enacted a moratorium or extended one that was days from expiring. The [North
State Journal](https://nsjonline.com/article/2026/09/data-center-moratorium-count-rises-again/),
which has been keeping a running count from public records, put the statewide
total at **at least 14 counties and 20 municipalities** by early September, up
from [11 and 17](https://nsjonline.com/article/2026/08/data-center-moratoriums-spreading/)
a month earlier. Our own [tracker](/moratoriums.html) lists 28 pauses in
force in the state as of this post, each with its source and end date.

The headline number is the least useful thing about these votes. What matters
to someone three weeks from a zoning hearing is *what each one actually
covers*, because the eight are not alike. Four have a size threshold. Two
apply only outside town limits. Three end early if the jurisdiction adopts new
rules. One of them was extended for twice as long as the agenda proposed, and
another was lengthened after residents asked for something far longer.

## The eight, in the order they happened

**Edgecombe County, August 3 — two years.** After a public hearing, all five
commissioners present voted for a moratorium under which, until August 3,
2028, the county "cannot accept, process and approve development applications
and development permits for data centers and related uses within the county's
zoning jurisdiction," per the [Rocky Mount Telegram / Daily
Reflector](https://www.reflector.com/apgstate/commissioners-approve-two-year-moratorium-on-data-centers/article_d746111c-f601-5252-9055-22af0e2b292e.html).
The same report says the vote followed news that Energy Storage Solutions,
which had been eyeing a wooded parcel in the Kingsboro Business Park, had
backed out. Two years is the longest term in this group.
[Community page](/communities/edgecombe-county-nc.html).

**Waxhaw, August 11 — twelve months.** The town board voted unanimously to
pause "acceptance, processing and approval of development applications for
data centers, cryptocurrency mining facilities, data storage and processing,
and related telecommunications equipment," according to
[WBTV](https://www.wbtv.com/2026/08/13/town-waxhaw-unanimously-approved-12-month-moratorium-data-centers/).
No proposal was pending. The mayor's stated reason was to avoid getting
"caught unprepared." [Community page](/communities/waxhaw-nc.html).

**Alamance County, August 17 — one year, 10 MW threshold.** Commissioners
voted 5-0 after a hearing that ran more than two hours, with more than 23
speakers in favor, per [Elon News
Network](https://www.elonnewsnetwork.com/article/2026/08/alamance-county-commissioners-pass-one-year-data-center-moratorium).
The ordinance applies to "large-scale" projects, which the county defines as
needing 10 megawatts or more, and it requires the board to meet at least 30
days before the August 2027 expiry to decide whether to let it lapse or extend
it. Commissioner Ed Priola's remark that non-disclosure agreements "should be
not part of government" is worth keeping for your own hearing.
[Community page](/communities/alamance-county-nc.html).

**Yadkin County, August 17 — two years, unincorporated areas only.** The
agenda carried a 12-month pause. After more than an hour of opposition
testimony, a commissioner moved to double it, and the board approved two years
5-0, according to the [Yadkin
Ripple](https://www.yadkinripple.com/news/moratorium-approved-for-yadkin-county-as-potential-yadkinville-data-center-project-announced/article_485d48fb-c61b-4167-b885-3d469e9a6bbe.html).
The same story reports the catch: the moratorium covers unincorporated county
land only, and the county manager confirmed it does not reach the
municipalities. That matters because the Ripple also reports that Enovum Data
Centers, operating as White Fiber, has announced a $60 million purchase of two
former Unifi properties *inside Yadkinville* for campuses it says would start
at 60 MW with potential for about 200 MW. The county's pause does not touch
that site. [Community page](/communities/yadkin-county-nc.html).

**Greensboro, August 18 — 180 days, 10 MW threshold.** Council voted 8-0 with
one recusal for a pause on data centers whose electrical demand exceeds 10
megawatts, per the [Greensboro
Thread](https://greensborothread.com/news/politics/greensboro-nc-data-center-moratorium-denise-roth/).
The draft council had [voted on August 3 to take to a
hearing](https://www.wfdd.org/politics-government/2026-08-04/greensboro-randolph-officials-take-steps-to-address-data-centers)
was 120 days; council lengthened it after public input, and residents in the
room were asking for 32 months. The
[North State Journal](https://nsjonline.com/article/2026/09/data-center-moratorium-count-rises-again/)
puts the end in mid-February 2027. [Community page](/communities/greensboro-nc.html).

**Durham County, August 24 — nine months, 100,000 sq ft threshold, with an
exemption.** The county's own [manager's
update](https://dconc.gov/DurhamCo-News/From-the-Desk-to-the-County-Manager-August-28-2026.htm)
describes a moratorium on "the creation of new data centers and the expansion
of current data centers, beyond 100,000 total square feet," with a staff draft
ordinance due in December and adoption targeted for May.
[WFAE](https://www.wfae.org/2026-08-26/durham-county-data-center-moratorium)
reports the vote was 4-1, that it runs to May 2027 in step with the City of
Durham's separate pause, and that the lone no vote, Commissioner Nida Allam,
objected to the exemption: facilities under 100,000 square feet that use
closed-loop cooling and have no diesel backup generators are not covered. If
you live near a smaller proposed site, read that exemption twice.
[Community page](/communities/durham-county-nc.html).

**Kings Mountain, August 25 — extended twelve months.** The city's original
182-day pause, adopted in February, was set to lapse the same week. The
[August 25 agenda](https://www.cityofkm.com/AgendaCenter/ViewFile/Agenda/_08252026-984)
gave council two ordinances to choose from, a 12-month extension and a 6-month
one. Per the [North State
Journal](https://nsjonline.com/article/2026/09/data-center-moratorium-count-rises-again/),
council took the year. [Community page](/communities/kings-mountain-nc.html).

**Whiteville, August 25 — twelve months, with an early-end clause.** The city
council enacted an immediate pause on new data centers, data processing
facilities and cryptocurrency mining, running to August 25, 2027 "or until the
city adopts a zoning ordinance text amendment addressing these land uses,
whichever comes first," per
[WECT](https://www.wect.com/2026/08/26/whiteville-approves-12-month-moratorium-new-data-centers-crypto-mining/).
The stated concerns were water for cooling, electricity demand, diesel backup
emissions and noise, and the fact that the city's code had no definition for
any of it. [Community page](/communities/whiteville-nc.html).

## What the fine print has in common

**Thresholds cut both ways.** Alamance and Greensboro draw the line at 10 MW;
Durham County at 100,000 square feet. A threshold keeps a pause from sweeping
in a hospital's server room, which is why counsel likes it. It also means a
developer can size a first phase to slip under it. Ask your own planning staff
which number their draft uses, and why.

**"County" often means "unincorporated."** Yadkin's board said so on the
record. Durham County and the City of Durham have two separate moratoriums
with two separate end dates. If your project sits inside town limits, a county
pause may not apply to it at all, and a hearing where you cite the wrong one
is a hearing you lose.

**The clock has escape hatches.** Whiteville's pause ends the day the city
adopts a text amendment. Alamance requires a decision meeting 30 days before
expiry. Kings Mountain shows the other direction: a "six-month" pause adopted
in February now runs eighteen months. Our tracker derives each row's status from its stated end
date, so a lapsed pause shows as *Expired* rather than staying "Enacted"
forever. Check the date on the row before you read it aloud.

**Length is negotiable in the room.** Yadkin doubled its term after an hour of
comment. Greensboro added two months. Neither board arrived intending to do
that. Show up with a specific number and a reason for it.

## What this does not tell you

A moratorium is a pause, not a policy. Every one of the eight is explicitly a
window for staff to write rules, and the rules are where the substance will be:
setbacks, noise limits, water sourcing, who pays for grid upgrades. Several of
these jurisdictions have said drafts are due this winter. That is the meeting
to prepare for. The [Start here](/start-here.html) guide walks through what to
ask for when the ordinance draft lands.

## See also

- [North Carolina state page](/states/north-carolina.html) — every tracked
  locality, project and pause in the state, with sources
- [Moratorium tracker](/moratoriums.html) — all 397 rows nationwide, with
  end dates and verification status
""",
    },
    # ── New Jersey's ban wave, and the trouble with counting it ──
    {
        "id": "new-jersey-ban-count-2026",
        "art": "moratorium",
        "section": "stories",
        "title": "Four Groups Counted New Jersey's Data Center Bans. They Got 37, 38, 50 and 69.",
        "seo_title": "New Jersey data center bans: why four counts disagree",
        "date": _dt.date(2026, 9, 2),
        "author": "GridWatch AI",
        "tags": ["New Jersey", "moratoriums", "bans", "ordinances",
                 "Millville", "Vineland", "Monroe Township", "Andover",
                 "Stafford Township", "East Brunswick", "litigation",
                 "Data Center Fair Share Act", "analysis"],
        "summary": (
            "Three New Jersey towns banned data centers on the same night in "
            "late August. Four organizations published a statewide count in "
            "the same two weeks and got four different numbers, because they "
            "are counting different things. Here is why the discrepancy "
            "matters more than any of the four totals \u2014 and what to ask "
            "your clerk before you cite one at a hearing."
        ),
        "body": """
Three New Jersey towns banned data centers on the same night in late August.
That is now an ordinary week here. It raises a question a resident three weeks
from a zoning vote actually needs answered: how many towns have done this, and
is mine one of them?

Four organizations published a count in the last two weeks of August. They got
37, 38, "more than 50," and 69.

None of them is wrong, exactly. They are counting different things. Working out
why is more useful than any of the four numbers, because the same ambiguity is
sitting inside your own town's ordinance, and it is the first thing a
developer's attorney will go looking for.

## The four counts

- **38.** The Climate Revolution Action Network's tally, reported by
  [94.3 The Point on August 27](https://943thepoint.com/ixp/385/p/data-center-bans-sweep-new-jersey/),
  which made Jackson "the 38th New Jersey community" to act.
- **~38.** [datacenterbans.com](https://www.datacenterbans.com/), a national
  tracker built by Will Manidis and last updated August 28, counts "roughly 38
  municipalities that have blocked data centers by local ordinance, the most of
  any state."
- **More than 50.** Charlie Kratovil of Food and Water Watch, quoted by
  [Patch](https://patch.com/new-jersey/eastbrunswick/data-centers-banned-east-brunswick-environmental-group-applauds-move)
  the night East Brunswick acted: "East Brunswick now joins more than 50 other
  New Jersey communities in taking this action."
- **69.** The Pinelands Preservation Alliance's
  [tracker](https://pinelandsalliance.org/datacenters/): "As of August 27,
  2026, the following 69 New Jersey municipalities have banned data centers."

Our own [moratorium tracker](/moratoriums.html) carries 67 New Jersey
localities — 62 recorded as enacted, five as proposed. That is the most of any
state; nationally we have 317 enacted rows across 37 states.

We should be equally honest about the soft part of our own number. Forty of
those 67 New Jersey rows are sourced to the Pinelands list itself, with no
ordinance number and no adoption date we have read. They carry the date we read
the list, not the date the town acted. That is a weaker claim than our rows for
Stafford or East Brunswick, and the tracker marks them as such.

## Why the counts diverge

Three reasons, all of which matter for your town.

**A ban, a moratorium and a zoning amendment are not the same instrument.**
Stafford Township's Ordinance 2026-22, [reported by
Patch](https://patch.com/new-jersey/barnegat-manahawkin/data-center-ban-approved-stafford-township),
says it plainly: "All data centers are hereby prohibited from operating
anywhere in the Township of Stafford." East Brunswick's Ordinance 26-21 does
something narrower — Patch reported it defines data centers and makes them a
prohibited use in all commercial, business and industrial zoning districts.
Both get counted as bans. Only one is a blanket prohibition on its face, and
the difference is exactly where an application in a district nobody listed
would go.

**Introduced is not adopted.** Jersey City introduced a ban in July; our
tracker still carries it as proposed, along with Howell, Andover, North
Plainfield and Plainfield. A count that includes introductions runs ahead of a
count that waits for second reading. The Inquirer
[reported in early August](https://www.inquirer.com/south-jersey/monroe-township-data-center-lawsuit-ban-collingswood-20260805.html)
that Collingswood had a data center ban headed for final passage in early
September. We have not confirmed the outcome, so we are not counting it, and
neither should you until you see the adopted text.

**Documentation costs time.** The largest count is also the one with the least
per-town paperwork: most entries on the Pinelands list carry no ordinance
number. That is not a knock on a tracker doing more than anyone else in the
state. It is a warning about what happens to an undocumented number once it is
repeated in a council chamber.

## The number is not your argument. The ordinance is.

If you stand up and say sixty-nine New Jersey towns have banned these, expect
to be asked which ones — and expect the applicant's attorney to have read three
of them and found one that only regulates building height.

The stronger move is to bring a single ordinance, ideally from a town that
resembles yours, and read the operative sentence out loud. Ask your clerk for
five things: the ordinance number, the **adopted** text rather than the
introduced draft, the zoning districts it covers, the effective date, and
whether any pending application was grandfathered. That last one decides
everything.

## What a ban actually stops

Three New Jersey cases, in increasing order of how much the ban accomplished.

**Vineland: the wave arrived after the vote.** On August 18 the Vineland
planning board approved the site plan for the second phase of a 300 MW campus
being built by DataOne for Nebius, whose capacity there is tied to a Microsoft
deal [WHYY](https://whyy.org/articles/vineland-planning-board-approves-data-center-plan/)
described as worth 17 billion dollars. WHYY reported a six-hour hearing
attended by a couple hundred people, that nobody spoke in favor during public
comment, and that the 8–1 approval drew boos from the room. Phase one was
already under construction. A citywide ban passed this month would not touch
any of it. See our [Vineland briefing](/communities/vineland-nj.html).

**Millville: a ban against a proposal never formally filed.** The Board of
Commissioners banned data centers citywide on May 19, which
[News 12](https://newjersey.news12.com/2026/05/20/millville-bans-data-centers-killing-largest-proposed-facility-in-new-jersey-history/77eDMHsKNvb6HkPeGLzLLN)
reported killed the A1 Data Center, describing it as a 2.6 million square foot
facility that would have drawn 1.4 GW at full capacity. The developer's own
[master plan page](https://www.a1datacenter.net/master-plan-development)
advertises the site at 1300 Wheaton Avenue as a "66-acre master-planned
development" with "2.9M SQ FT of optimized technical space," a "1.4 GW" scale
horizon, "49 MW Live redundant substation energy" today, and a five-acre
freshwater cooling pond. Note that the two square-footage figures do not match:
2.6 million from the newsroom, 2.9 million from the developer. Cite whichever
you want, but say whose number it is. Our project dossier records that no site
plan was ever formally submitted to the city — which is worth knowing before
you describe the ban as having stopped a project that was, on the public
record, still a marketing page. See our
[Millville briefing](/communities/millville-nj.html).

**Monroe Township and Andover: banned, then sued.** Monroe adopted a
township-wide ban on April 22 that reached previously approved projects. On
June 5, Hexa Builders filed a 104-page, 20-count complaint in Gloucester County
Superior Court seeking 300 million dollars, later removed to federal court in
Camden. Among the counts is a First Amendment theory: per the
[Jersey Vindicator's](https://jerseyvindicator.org/2026/08/01/developer-challenges-gloucester-county-data-center-ban-on-free-speech-grounds)
reading of the filing, Hexa argues data centers are used "in sending email and
text messages, using social media, storing data to be retrieved from
internet-based searches," so restricting them burdens speech. Monroe's
attorney, Todd Gelfand, moved to dismiss on July 28, arguing the ban is
ordinary land-use regulation and that a township has a right to amend zoning in
response to public objection; the Inquirer reported that U.S. District Judge
Edward Kiel had not ruled as of early August. Andover Township drew a separate
suit on July 10, when National Land Developers — which holds 248 Stickles Pond
Road — asked the Sussex County court to void Ordinance 2026-13, alleging
defective notice and an arbitrary Land Use Board review.
[WRNJ](https://wrnjradio.com/developer-files-lawsuit-challenging-andover-township-data-center-ordinance/)
reported township officials said they intend to defend and have no interest in
settling.

Neither suit has produced a ruling. That is the point. For a town with a live
application, a ban is the start of the fight, not the end of it — and a town
that acts before an application lands is in a materially stronger position than
one that acts after.

## The state layer

Municipal bans are not New Jersey's only lever. On July 7, Gov. Sherrill signed
the Data Center Fair Share Act (S731/A796), which
[the governor's office](https://www.nj.gov/governor/news/2026/20260707a.shtml)
describes as creating "a new ratepayer class and rate structure for data
centers, ensuring they pay for their own energy use and associated grid
infrastructure," and requiring large loads to "cut back before residential
ratepayers are impacted" when the grid is strained. A town that cannot get a
ban through can still make the cost-shifting argument the state has now written
into law.

## See also

- [New Jersey state page](/states/new-jersey.html) — every tracked locality,
  project and ban in the state
- [Moratorium tracker](/moratoriums.html) — 317 enacted rows across 37 states,
  each with its own source and read date
- [Project tracker](/projects.html) — the Vineland, Millville, Monroe and
  Andover dossiers, with the permit paper trail for each
""",
    },
    # ── The gas buildout, the water behind it, and the notice being deleted ──
    {
        "id": "gas-buildout-water-notice-2026",
        "art": "oversight",
        "section": "stories",
        "title": "The Power Plant Is Now Part of the Data Center \u2014 and the Public Notice for It Is Being Deleted",
        "seo_title": "Data center gas plants and the vanishing public notice",
        "date": _dt.date(2026, 8, 26),
        "author": "GridWatch AI",
        "tags": ["natural gas", "Global Energy Monitor", "air permits",
                 "New Source Review", "EPA", "water", "Ceres", "Ohio",
                 "Pike County", "OpenAI", "SB Energy", "Texas", "analysis"],
        "summary": (
            "Three things landed in the same week. Global Energy Monitor "
            "counted 189 GW of U.S. gas capacity in development tied to data "
            "centers \u2014 nearly double the figure six months earlier. Ceres "
            "put a number on the water those power plants use, which is the "
            "part of a data center's water footprint nobody meters. And EPA "
            "moved to delete the federal requirement that states give public "
            "notice on the air permits those plants need. Read together, they "
            "describe one shift: the generator is now part of the project, "
            "and the process for the generator is the process being narrowed."
        ),
        "body": """\
Three separate items landed in the last week of August 2026. Individually
each is a news story. Together they describe a single structural change in
how these projects get built \u2014 and where a community still has a say.

**One.** Global Energy Monitor counted **189 GW of U.S. gas-fired capacity in
development tied specifically to data centers**, up from 97 GW at the end of
2025 \u2014 nearly a doubling in six months
([GEM, Aug 25](https://globalenergymonitor.org/research/us-gas-power-proposals-tied-data-centers-nearly-double-six-months)).

**Two.** Ceres modeled the water consumed by the power plants that serve data
centers in the seven states holding about half the country's fleet, and put
it at roughly **3.4 trillion gallons of freshwater a year** \u2014 a figure that
dwarfs on-site cooling, which is the only number most hearings ever discuss
([Ceres, Aug 25](https://www.ceres.org/resources/reports/water-behind-the-watts-the-hidden-risk-of-powering-data-centers)).

**Three.** EPA moved to eliminate the federal requirement that states
publicize and take comment on minor-source air permits \u2014 the permit class
that covers many data centers and the generation built alongside them
([New York Times, Aug 25](https://www.nytimes.com/2026/08/25/climate/epa-data-centers-public-comment.html)).

The through-line: for a growing share of projects, the power plant is no
longer something the utility builds somewhere else. It is on the parcel, in
the same application, owned by the same parties. That moves the decision out
of the rate case and into the air permit \u2014 which is the exact process now
losing its public-notice floor.

---

### Part 1 \u2014 The gas number, and its honest caveats

GEM's Global Oil and Gas Plant Tracker now counts 378 GW of U.S. gas capacity
across the announced, pre-construction, and construction phases, up from
252 GW at the end of 2025 \u2014 a 50% increase in six months. Of that, **189 GW
is tied to data centers.** U.S. gas capacity actually *under construction*
reached 52 GW, against China's 24 GW; on the full development pipeline, the
U.S. now leads roughly three to one.

Texas alone accounts for 122 GW in development \u2014 31% of the national total,
up 51% in six months \u2014 with 77 GW of that designated for data centers.

Now the caveats, which matter more than the headline if you are the one
standing up at a hearing:

- **About 86% of the U.S. pipeline is announced or pre-construction**, not
  under construction. An announcement is a press release, not a turbine.
- **Nearly a quarter of the data-center-linked gas projects have no named
  start year at all.**
- **Two-thirds of global gas capacity in development has no identified
  turbine manufacturer**, and turbine lead times now run years. GEM logged
  45 GW of announced and pre-construction capacity slipping in the first half
  of 2026 alone.

GEM's own project manager, Jenny Martos, framed the tracker's limits plainly:
this wave of proposals is "running headlong into the hurdles of an already
tight gas market."

Use the caveats in both directions. When a developer presents new on-site
generation as settled, ask which phase it is in, who is supplying the
turbines, and what the contracted delivery date is. When an opponent cites
189 GW as though it were poured concrete, the same question applies. **The
number that belongs in a hearing record is the phase, not the total.**

### Part 2 \u2014 Pike County is the template, not the exception

The clearest example of the new structure is the PORTS-Pike Technology
Campus in Piketon, Ohio \u2014 already tracked in our
[project dossiers](/projects.html).

The shape of the deal:

- **8 GW-IT of capacity leased by OpenAI** from SB Energy, a SoftBank Group
  company, under a 20-year lease
  ([OpenAI, Aug 18](https://openai.com/index/openai-joins-ports-pike-project/)).
- **9.2 GW of new on-site natural gas generation**, funded in part through
  $33.3 billion tied to the U.S.\u2013Japan Strategic Trade and Investment
  Agreement. **The generating assets are to be owned by the U.S.
  government**, with SB Energy operating them.
- **The land is federal** \u2014 DOE's former Portsmouth Gaseous Diffusion
  Plant, a uranium enrichment site with its own long contamination record.
- **The financing is circular.** OpenAI invested $500 million in SB Energy in
  January 2026; Nvidia announced a $1.5 billion investment this month and is
  the campus's compute provider. The tenant and the chip supplier are both
  investors in the landlord.

If that were a utility-built plant, there would be a rate case, a docket
number, and a ratepayer-impact figure a commissioner has to look at. Here,
much of that is displaced. We made the same point about Amazon's
[7.65 GW gas plant in Pecos County](/blog/amazon-pecos-county-gas-plant-2026.html):
when the generation is behind the meter, the ratepayer argument thins out
and the leverage moves to the air permit and the local land-use process.

Two doors are still wide open at Piketon, and they are worth naming because
they generalize:

- **The transmission still gets sited publicly.** AEP Ohio's roughly 50-mile,
  765 kV Piketon Area Improvements Project runs through Pike, Jackson, and
  Gallia counties and goes to the **Ohio Power Siting Board** \u2014 a
  contested proceeding with intervenor rights, regardless of who owns the
  gas plant.
- **The air permit still exists.** Behind-the-meter generation is still a
  stationary source. Which brings us to the third item.

### Part 3 \u2014 The water nobody meters

Ceres' *Water Behind the Watts* looked at Virginia, Texas, California,
Illinois, Georgia, Ohio, and Arizona \u2014 about half the U.S. data center
fleet \u2014 and found:

- Roughly **3.4 trillion gallons of freshwater a year** associated with the
  electricity those data centers use, which Ceres compares to about **12
  times** the combined annual use of Los Angeles, Phoenix, and Washington,
  D.C.
- **78%** of electricity in those states comes from plants that need water to
  operate.
- **66%** of those water-using plants sit in areas rated medium-high to
  extremely high water stress.
- By 2030, the associated annual withdrawals could reach **4.1 to 7.6
  trillion gallons.**

One precision note, because it will be the first thing a developer's
consultant says: **withdrawal and consumption are not the same number.**
A once-through cooled plant withdraws enormous volumes and returns most of
it (warmer); a cooling-tower plant withdraws less and evaporates most of what
it takes. Coverage of this report uses both words. When you cite it, cite the
metric \u2014 and when a company gives you a water figure, ask which one it is,
and whether it covers generation or only the building.

On disclosure, the gap is stark. **Meta is the only hyperscaler that reports
indirect water embedded in purchased electricity, and its 2024 figure was
more than 20 times its direct data-center water consumption** \u2014 rising every
year since 2021. Amazon told Latitude Media it tracks the number but has not
published it, citing the absence of a reporting standard. Neither Google nor
Microsoft said whether they track it at all
([Latitude Media, Aug 26](https://www.latitudemedia.com/news/data-centers-hidden-water-footprint-is-linked-to-the-grid/)).

So when a project promises a closed-loop cooling system and a modest gallons-
per-day figure, that promise is real \u2014 and it is describing the small half
of the footprint. **The question that gets you the other half is: where does
this facility's power come from, and how much water does *that* plant use?**

### Part 4 \u2014 The door that is closing

On July 1, 2026, EPA proposed removing the **minimum federal public
participation requirements for minor New Source Review permitting** in state
implementation plans; it published in the Federal Register on July 7, and the
comment period closed **August 21, 2026**
([EPA news release](https://www.epa.gov/newsreleases/epa-proposes-streamline-state-and-local-permitting-process-minor-sources);
[Federal Register, Jul 7](https://www.federalregister.gov/documents/2026/07/07/2026-13667/minor-new-source-review-program-air-permitting-public-participation-requirements-for-state)).

Minor NSR is the permit class that covers new minor stationary sources and
minor modifications to existing ones \u2014 in practice, many data centers, their
backup generator fleets, and emissions-increasing additions at existing
power plants. It is the process where a resident first learns a facility is
coming.

EPA's framing is that it is returning a procedural choice to the states.
Administrator Lee Zeldin: state and local authorities "closest to issues
should make permitting decisions, not Washington." The agency says emission
standards themselves are unchanged.

That framing is worth taking literally, because it defines where the fight
now is. **The proposal does not forbid public notice. It removes the federal
floor requiring it.** Every state keeps the authority to require notice and
comment in its own minor NSR program \u2014 and after this rule, that becomes a
state-by-state decision made by your state air agency, not a national
guarantee.

Roughly 200 environmental, health, and community organizations, plus more
than a dozen states, filed in opposition during the comment window
([NYT, Aug 25](https://www.nytimes.com/2026/08/25/climate/epa-data-centers-public-comment.html)).
That window is now shut. What is not shut is the state one.

Meanwhile the generation rules are moving the same direction: CEOs of
generation-and-transmission cooperatives, including NRECA's Jim Matheson,
publicly pressed EPA this month to fully repeal the 2024 greenhouse-gas
standards for gas plants, arguing the 40% capacity-factor threshold and
carbon-capture requirement are "untenable" given data-center load growth
([Utility Dive, Aug 2026](https://www.utilitydive.com/news/electric-co-ops-repeal-epa-gas-power-plant-emissions-rules/828377/)).

### What this changes about your hearing

1. **Ask first whether the generation is grid-connected or behind the
   meter.** The answer determines whether there is a rate case to intervene
   in at all. If there isn't, the air permit and local land use are the whole
   board \u2014 start there on day one, not after the first hearing.
2. **Ask your state air agency, in writing, whether it will keep public
   notice and comment in its minor NSR program** regardless of what the
   federal floor says. Get the answer on the record before a permit is
   pending, not after. This is the single highest-leverage thing to do in
   response to the EPA proposal, and it is a state-level ask.
3. **Ask for the water number that covers generation**, not just the
   building \u2014 and pin down withdrawal versus consumption. Our
   [impact calculator](/impact.html) gives you a defensible per-facility
   estimate to bring as a baseline.
4. **Follow the transmission.** Even where the plant is private, the lines
   usually are not. Your [state PUC or siting board](/puc.html) is a public
   docket with intervenor rights.
5. **Check the paper trail before you argue.** Every dossier on the
   [project tracker](/projects.html) lists where that project's permits and
   filings actually live, and distinguishes a public register from a
   pre-built search \u2014 because citing a search result at a hearing is how a
   resident loses one.

> The old script assumed the utility built the power plant and the community
> argued about the data center. Increasingly it is one application, one set
> of owners, and one permit \u2014 the air permit. Find out today whether your
> state intends to keep telling you when one is filed.

### Sources

- [Global Energy Monitor \u2014 "U.S. gas power proposals tied to data centers nearly double in six months" (Aug. 25, 2026)](https://globalenergymonitor.org/research/us-gas-power-proposals-tied-data-centers-nearly-double-six-months)
- [Ceres \u2014 "Water Behind the Watts: The Hidden Risk of Powering Data Centers" (Aug. 25, 2026)](https://www.ceres.org/resources/reports/water-behind-the-watts-the-hidden-risk-of-powering-data-centers)
- [The New York Times \u2014 "E.P.A. Moves to Curb Public Input on Air Pollution Permits for Data Centers" (Aug. 25, 2026)](https://www.nytimes.com/2026/08/25/climate/epa-data-centers-public-comment.html)
- [EPA \u2014 "EPA Proposes to Streamline State and Local Permitting Process for Minor Sources" (Jul. 1, 2026)](https://www.epa.gov/newsreleases/epa-proposes-streamline-state-and-local-permitting-process-minor-sources)
- [Federal Register \u2014 Minor New Source Review Program Air Permitting Public Participation Requirements for State Implementation Plans (Jul. 7, 2026)](https://www.federalregister.gov/documents/2026/07/07/2026-13667/minor-new-source-review-program-air-permitting-public-participation-requirements-for-state)
- [Latitude Media \u2014 "Data centers' hidden water footprint is linked to the grid" (Aug. 26, 2026)](https://www.latitudemedia.com/news/data-centers-hidden-water-footprint-is-linked-to-the-grid/)
- [OpenAI \u2014 "OpenAI joins PORTS-Pike project" (Aug. 18, 2026)](https://openai.com/index/openai-joins-ports-pike-project/)
- [WOSU \u2014 "OpenAI joins data center venture at former nuclear enrichment site in Pike County" (Aug. 17, 2026)](https://www.wosu.org/2026-08-17/openai-joins-data-center-venture-at-former-nuclear-enrichment-site-in-pike-county)
- [Utility Dive \u2014 "Electric co-ops press for repeal of gas power plant emissions rules"](https://www.utilitydive.com/news/electric-co-ops-repeal-epa-gas-power-plant-emissions-rules/828377/)
""",
    },
    # ── Trump doubles down on data centers as the backlash goes bipartisan ──
    {
        "id": "trump-data-center-support-2026",
        "art": "bills",
        "section": "stories",
        "title": "Trump Says Your Town Is \"Making a Mistake.\" Here's What the Record Actually Shows.",
        "seo_title": "Trump on data center opposition: what the record shows",
        "date": _dt.date(2026, 8, 26),
        "author": "GridWatch AI",
        "tags": ["federal policy", "Trump", "ratepayer protection", "FERC",
                 "executive order", "Texas", "Abbott", "polling", "midterms",
                 "analysis"],
        "summary": (
            "In an interview that aired August 23, President Trump said "
            "communities rejecting data centers are \"making a mistake\" and "
            "that the industry could be \"bigger than oil.\" That doubles down "
            "on eighteen months of federal policy — permitting orders, federal "
            "land, a FERC interconnection push, and a 300-signatory ratepayer "
            "pledge with no enforcement mechanism. We walk through what the "
            "administration has actually done, what reporters and analysts "
            "across the spectrum say about it, and what none of it changes "
            "about the vote in front of your planning board."
        ),
        "body": """\
On August 23, 2026, an interview President Trump recorded with his former
attorney Michael Cohen aired in full. Asked about the data center fights
spreading through both red and blue states, Trump was unambiguous:
communities that turn projects away are *"making a mistake,"* because data
centers bring *"tremendous amounts of jobs and money."* He added that
operators *"are making their own power plants"* and that the facilities are
not drawing from the existing grid, and said the U.S. leads China in AI
*"by a lot"* ([Axios, Aug 23](https://www.axios.com/2026/08/23/trump-data-centers-michael-cohen-interview);
[The Hill, Aug 23](https://thehill.com/homenews/administration/6016051-trump-its-a-mistake-to-go-against-data-centers/);
[Forbes, Aug 24](https://www.forbes.com/sites/siladityaray/2026/08/24/trump-defends-ai-data-centers-says-opposing-them-is-a-mistake-and-smart-ones-want-them/)).

It was the second time this month. On August 7, responding to Texas Governor
Greg Abbott's pause on new data center grid connections, Trump called the
state's position *"a mistake"* and said the industry *"could be bigger than
oil"* ([Texas Tribune, Aug 7](https://www.texastribune.org/2026/08/07/donald-trump-texas-data-centers-greg-abbott/)).

Those remarks are not off-the-cuff. They are the rhetorical layer on top of a
federal program that has been building since July 2025. If you are heading
into a zoning hearing, it is worth knowing exactly what that program does —
and, more importantly, what it does not do.

---

### Part 1 — What the administration has actually built

**Permitting (July 2025).** Executive Order
[*Accelerating Federal Permitting of Data Center Infrastructure*](https://www.whitehouse.gov/presidential-actions/2025/07/accelerating-federal-permitting-of-data-center-infrastructure/)
directs agencies to streamline environmental review, offer financial support
through Commerce, and open federal land. It covers "Qualifying Projects" —
those adding more than 100 MW of new load, costing at least $500 million, or
serving national security
([White & Case](https://www.whitecase.com/insight-alert/trump-administration-issues-executive-order-streamline-data-center-development);
[Beveridge & Diamond](https://www.bdlaw.com/publications/trump-administration-issues-executive-order-to-facilitate-data-center-development/)).

**Federal land.** DOE named four sites — Idaho National Laboratory, Oak Ridge,
the Paducah Gaseous Diffusion Plant, and Savannah River — and the Air Force
added five bases (Arnold, Edwards, Joint Base McGuire-Dix-Lakehurst,
Davis-Monthan, Robins). In Kentucky, DOE has since announced a Paducah
"AI and high-performance computing innovation campus" with NextEra, Brookfield
and three utilities, pitched at more than $100 billion in private investment,
8,000 construction jobs and 600 permanent ones
([DOE](https://www.energy.gov/node/4851856);
[NOTUS](https://www.notus.org/energy/trump-administration-announces-data-center-on-federal-land)).

Progress is uneven. Counsel at Davis Graham
[note](https://davisgraham.com/news-events/the-trump-administrations-progress-to-site-data-centers-on-federal-lands-initial-steps-but-work-remains/)
that the Interior Department — which manages over 530 million acres — has
identified *no* sites at all, because BLM would likely need multi-year
resource management plan amendments first, and that EPA's brownfield and
Superfund criteria have lagged their own deadline.

**Grid access (June 2026).** On June 18, FERC issued show-cause orders under
section 206 of the Federal Power Act to all six RTOs and ISOs — PJM, MISO,
SPP, CAISO, ISO-NE and NYISO — preliminarily finding their tariffs may be
unjust and unreasonable because they don't adequately handle large-load and
co-located interconnection. Grid operators got 60 days to respond, extendable
to 150 ([FERC docket RM26-4](https://www.ferc.gov/rm26-4);
[Holland & Knight](https://www.hklaw.com/en/insights/publications/2026/06/ferc-advances-new-oversight-framework-for-large-loads);
[Utility Dive](https://www.utilitydive.com/news/ferc-doe-data-center-interconnection/823360/)).

**The pledge (Feb–July 2026).** Trump announced the **Ratepayer Protection
Pledge** in the February 24 State of the Union. On March 4, seven hyperscalers
— Amazon, Google, Meta, Microsoft, OpenAI, Oracle and xAI — signed at the
White House. On July 23 it was expanded to add 55 utilities, 106 cooperatives,
28 developers and 23 governors, every one of them Republican; the White House
says signatories now cover roughly 80% of power delivered to American homes
and businesses
([White House](https://www.whitehouse.gov/ratepayer-protection-pledge/);
[POWER Magazine](https://www.powermag.com/white-house-expands-data-center-ratepayer-pledge-as-congress-moves-to-codify-protections/);
[NOTUS](https://www.notus.org/energy/trump-expands-ratepayer-pledge-republican-governors-utilities)).

The five commitments are worth reading closely, because they are close to what
communities have been asking for:

1. Build, bring, or buy new power supply to cover the load
2. Pay for the new power delivery infrastructure
3. Pay for that power **whether or not they use it**
4. Invest in local jobs and workforce development
5. Contribute to grid and community resilience

---

### Part 2 — What critics say, and they are not all Democrats

**It has no teeth.** This is the near-universal criticism, and it comes from
across the spectrum. In a July 9 analysis for Brookings, David M. Klaus and
Mark MacCarthy argue the pledge
[needs enforcement](https://www.brookings.edu/articles/the-pledge-to-protect-ratepayers-from-ai-data-center-costs-needs-enforcement/)
to mean anything: separate rate classes for large loads, standardized tariff
models developed through NARUC, take-or-pay contracts, and independent
oversight of interconnection agreements. Without them, they warn residential
rates could climb 15–40% by 2030. Jeff Dennis of the Electricity Customer
Alliance put the practical problem to NOTUS more mildly: *"We'll be
interested to see how utilities that have signed this pledge go about
implementing that specific piece."*

**The signatories are fighting enforcement elsewhere.** A staff attorney at
The Utility Reform Network has pointed out that the same companies signing in
Washington have opposed state-level bills that would make the same promises
binding, California among them. Consumer Reports found **75% of American
adults are not confident** developers will actually cover their own costs.

**The state-level free-market critique.** ALEC, no one's idea of a
degrowth outfit, [supports the pledge](https://alec.org/article/data-centers-energy-demand-and-the-ratepayer-protection-pledge/)
but frames the whole question as regulatory competition — states with
"complex mandates and higher energy costs risk deterring data center
investment." That is the honest version of the industry's argument, and it is
the one your developer will make: *if you say no, they go somewhere else.*

**FERC's own ratepayer advocates aren't satisfied.** Consumer advocates from
four PJM states plus the Pennsylvania Office of Consumer Advocate told FERC
its PJM order still leaves existing customers holding part of the
data-center-driven transmission bill
([Utility Dive](https://www.utilitydive.com/news/ferc-data-center-pjm-transmission-costs/825760/)).
Former FERC Commissioner Allison Clements noted a structural gap: the orders
reach only RTO regions, leaving roughly a third of Americans outside them
entirely.

**And the claim that data centers aren't taking grid power is hard to square
with the auctions.** PJM's capacity price went from $28.92/MW-day in the
2024/25 auction to $329.17/MW-day for 2026/27. Analysis by
[IEEFA](https://ieefa.org/resources/projected-data-center-growth-spurs-pjm-capacity-prices-factor-10)
and [SemiAnalysis](https://newsletter.semianalysis.com/p/are-ai-datacenters-increasing-electric)
attributes the majority of the increase to data center load — removing
projected data centers from the forecast cuts total capacity payments by
roughly $9.3 billion. Some large campuses genuinely are building dedicated
generation. Many are not, and the bill for those shows up in a capacity
auction that every household in the footprint pays into.

---

### Part 3 — The politics turned before the policy did

The most important number in this story isn't a megawatt figure.

[Gallup](https://news.gallup.com/poll/709772/americans-oppose-data-centers-area.aspx),
surveying 1,000 adults March 2–18, 2026 (±4 points), found **71% of Americans
oppose construction of an AI data center in their local area**, 48% strongly.
Only 25% were in favor and just 7% strongly so. Opposition ran higher than
opposition to a local **nuclear plant** (53%) — and it was highest in the
Midwest (76%) and South (75%), the regions the buildout is moving into
fastest.

And it is still moving. The Annenberg Public Policy Center's
Institutions of Democracy survey (SSRS, n=1,320, ±3.5) found opposition to
new local data centers rose from **49% in February–March to 61% by
June–July 2026**, with support falling from 21% to 14% — twelve points in
four months
([phys.org](https://phys.org/news/2026-08-opposition-local-centers-sharply-survey.html)).

That is why the reaction to Trump's remarks was not partisan. Governor Abbott
— a Republican, in the state with the most aggressive load growth in the
country — said AI companies *"dug their own grave"* by failing to work with
local officials, and paused new grid connections pending a review that Axios
reports touches as many as 1,800 projects
([Axios, Aug 23](https://www.axios.com/2026/08/23/greg-abbott-texas-data-centers-ai-backlash)).
Forbes reports GOP strategists worrying openly about midterm exposure,
particularly in Ohio.

In Congress the response is already bipartisan in both directions. Senators
Josh Hawley (R-MO) and Richard Blumenthal (D-CT) introduced the
[GRID Act](https://www.hawley.senate.gov/hawley-blumenthal-introduce-bill-to-prevent-data-centers-from-increasing-electricity-costs-for-americans)
on February 11, 2026, which would require data centers to source power
independently of the grid over a 10-year transition, put consumers first in
line, and mandate public disclosure of electricity use. On July 21 the House
Energy and Commerce Committee advanced the **Ratepayer Protection Act
(H.R. 9340)** from Reps. Gabe Evans (R-CO) and Kathy Castor (D-FL) by
**52–0** — a PURPA amendment that would require state regulators to consider
making 100+ MW data centers cover the full incremental cost of grid upgrades.
That is the pledge, with a statute behind it.

---

### Part 4 — What this actually means for your hearing

Here is the part that matters, and it is the part the coverage tends to bury.

**1. The federal orders do not preempt you.** MultiState's tracker is explicit:
the executive orders "do not preempt state permitting requirements, zoning
laws, or energy regulations"
([MultiState](https://www.multistate.us/insider/2026/4/14/federal-ai-data-center-policy-meets-resistance-from-state-lawmakers)).
A December 2025 order directed Commerce to publish a list of state AI laws
deemed invalid; as of MultiState's April review, no such list had been
published. Federal enthusiasm is not federal authority. Your zoning code is
still your zoning code.

**2. The 100 MW threshold leaves most projects out.** The federal fast lane
starts at 100 MW and $500 million. States are legislating down to **10 MW**,
and 27 of them are advancing large-load bills; California, Ohio and Utah have
enacted them. Maine is positioned to enact the first statewide moratorium,
through November 2027. The project in front of your board is far more likely
to be governed by that layer than by anything in Washington.

**3. The pledge is a document you can hold a developer to — locally.** This is
the single most useful thing to take from the last six months. If your
developer's parent company is on the White House list, they have publicly
committed to bringing their own power, paying for delivery infrastructure, and
paying **whether or not they use it**. The pledge has no federal enforcement.
A community benefits agreement does. Ask, on the record, whether they will
put commitments 1, 2 and 3 into a binding CBA and a signed tariff — and note
the answer in the minutes either way. Our
[model clause library](/cba-clauses.html) has the take-or-pay and
cost-causation language.

**4. "They'll just go elsewhere" is testable, not axiomatic.** Brookings cites
Sightline Climate's estimate that as much as half of announced 2026 projects
may never materialize, and counts at least 48 projects worth $156 billion
blocked by local opposition in 2025. That is not proof a given developer is
bluffing. It is proof the sector's announcement pipeline is not the same thing
as its build pipeline — and your board is entitled to ask which one it is
looking at.

**5. Watch the interconnection venue, not the podium.** FERC's show-cause
orders will reshape how your RTO treats large loads over the next year, and
state PUCs will decide the rate class question. Those are the proceedings
where the money actually moves. Our [permit and docket lookup](/projects.html)
points at the RTO queue and PUC docket for a given project.

---

### The honest summary

The President's position is consistent and has been for eighteen months: build
fast, build big, treat this as an industrial race with China. His
administration has paired that with a real attempt to answer the cost
objection — the Ratepayer Protection Pledge asks for close to the right
things. What it does not have is a mechanism. It is a promise made in
Washington that has to be enforced in fifty state capitals and several
thousand county buildings, by people with no obligation to enforce it.

Which puts the burden exactly where it has been all along. The pledge only
becomes real in the room where the vote happens. Bring a copy.

---

*See also: [Moratorium tracker](/moratoriums.html) —
what other communities have enacted, with sources and expiry dates ·
[Start here](/start-here.html) — a three-week plan for a zoning fight ·
[2026 Senate races](/senate-races.html) — where candidates stand on making
data centers pay their own way.*

*This piece links to primary documents and to reporting from Axios, The Hill,
Forbes, the Texas Tribune, Utility Dive, POWER Magazine, NOTUS, Brookings,
Gallup and the Annenberg Public Policy Center. Where an outlet's framing is
contested, we've said so. Corrections: reach out through the newsletter
signup.*
""",
    },
    # ── Pennsylvania Governor Shapiro signs GRID executive order ──
    {
        "id": "pennsylvania-grid-executive-order-2026",
        "art": "oversight",
        "section": "stories",
        "title": "Pennsylvania Just Told Data Centers: Build Your Own Power, or Don't Build Here",
        "seo_title": "Pennsylvania data center order: build your own power",
        "date": _dt.date(2026, 8, 21),
        "author": "GridWatch AI",
        "tags": ["Pennsylvania", "policy", "executive order", "GRID",
                 "ratepayer protection", "permitting", "community benefits",
                 "Amazon", "analysis"],
        "summary": (
            "Governor Shapiro signed Executive Order 2026-05 on August 18, "
            "establishing the nation's strictest permitting standards for data "
            "centers. The GRID framework requires developers to fund their own "
            "power infrastructure, obtain local approval before any state permit, "
            "and sign enforceable community benefit agreements — or face the "
            "slowest permitting lane in the state."
        ),
        "body": """\
On August 18, 2026, Governor Josh Shapiro signed [Executive Order 2026-05](https://www.pa.gov/content/dam/copapwp-pagov/en/governor/documents/eo2026_05_protecting%20pennsylvania%20consumers%20from%20data%20center%20impacts_final_executed.pdf),
creating what Pennsylvania is calling the strictest data center development
standards in the nation. The order establishes the **GRID** (Governor's
Responsible Infrastructure Development) framework — a set of enforceable
requirements that any large data center must meet to receive state permits
and tax benefits.

Shapiro's message was blunt: *"If you can't agree to our strict requirements
and get the community where you want to build to say 'yes,' you're not going
to have the Commonwealth's support either."*

### What GRID actually requires

**Pay for your own power.** Developers must fund the generation, transmission,
and distribution infrastructure their projects require. PUC Chair Steve DeFrank
put it simply: *"Growth should pay for growth."* No more shifting grid upgrade
costs to residential ratepayers.

**Bring your own generation.** Projects over 25 MW are incentivized to source
new power rather than drawing from existing plants. The order imposes an
escalating clean-energy sourcing requirement: 10% at opening, 14.5% within
three years, and 32% by 2035.

**Local approval before state permits.** This is the structural shift. The
Department of Environmental Protection will not issue permits unless the project
has already secured all required local government approvals. Municipalities
effectively have veto power.

**Enforceable community benefit agreements.** Developers must sign legally
binding commitments covering local hiring, workforce training, and investment
in schools, infrastructure, and economic development.

**No more NDAs.** The order bans non-disclosure agreements on data center
matters — a direct response to the secrecy that has defined developer
negotiations with local governments nationwide.

**Transparency mandate.** DEP must publish a public permitting-status map,
and developers must provide early public notification and hold community
meetings before major design decisions.

**Environmental standards.** Water conservation requirements, pollution-limiting
DEP regulations, and annual energy and water consumption reporting.

**Fast Track is dead.** All AI data center projects — including Amazon's
\\$20 billion Luzerne County and Bucks County campuses — have been immediately
pulled from the PA Permit Fast Track Program. Future data center projects are
permanently ineligible.

**Tax breaks are conditional.** Pennsylvania's existing Computer Data Center
Equipment sales-tax exemption now requires GRID compliance. The Department of
Revenue is updating exemption guidelines accordingly.

### How it works: the consent order model

Rather than an outright ban or moratorium, GRID uses a carrot-and-stick
permitting model. Developers who meet the requirements execute a **Consent
Order and Agreement (COA)** with DEP after pre-application meetings, gaining
access to a streamlined permitting lane. Non-compliant projects aren't banned
— they're shunted into conventional permitting, which is dramatically slower.

This is a deliberate design choice. Shapiro's team built the order with a
severability clause, anticipating legal challenge from the data center industry.
A consent-order framework is harder to strike down than a blanket moratorium
because it technically doesn't prohibit anything — it just makes noncompliance
very expensive in time and bureaucratic friction.

### Why it happened now

The numbers forced the issue. Pennsylvania is tracking over **100 proposed data
center projects** statewide. Of those, 58 have engaged DEP informally, 15 have
filed for at least one permit, and only 5 have all the permits needed for a
first phase. The pipeline is enormous and accelerating.

The political math mattered too. A Quinnipiac poll found **76% of Pennsylvania
voters oppose data centers near their communities**. And the legislative route
had stalled: the House passed [HB 2650](https://www.legis.state.pa.us/cfdocs/billInfo/BillInfo.cfm?syear=2025&sind=0&body=H&type=B&bn=2650)
codifying GRID on June 24, 134-68, with bipartisan support — but the
GOP-controlled Senate refused to take it up. Senate Democrats pushed for a
special session; Senate Majority Leader Joe Pittman declined. Facing Senate
inaction, Shapiro went executive.

### The reaction

The order drew praise from an unusually broad coalition: building trades unions
(PA Building & Construction Trades Council), environmental groups (Conservation
Voters of PA, NRDC, Environmental Defense Fund), municipal organizations (PA
State Association of Township Supervisors), and clean-energy advocates (Clean
Power PA).

Criticism came from both directions:

**Too weak.** Food & Water Watch wants a mandatory moratorium, not a
voluntary-compliance model. GOP Treasurer Stacey Garrity — Shapiro's likely
2026 gubernatorial rival — called the order "gaslighting," arguing that
consent-based permitting gives developers too many paths around the rules.

**Too restrictive.** The Data Center Coalition (representing Amazon, Microsoft,
and others) objected to *"rules changed midstream impacting ongoing investment
in verified and responsible projects."* Senate Majority Leader Pittman
complained that his chamber's own tax-exemption repeal bill was derailed by
House amendments.

### What this means for your community

Even outside Pennsylvania, the GRID framework changes the landscape:

**1. "Growth pays for growth" is now precedent.** Before this, communities
had to argue from scratch that data centers should fund their own grid
upgrades. Pennsylvania just made it the default. Cite it.

**2. The local-veto model is replicable.** Requiring local approval before
state permits is something any governor can do by executive order. It doesn't
require new legislation.

**3. The NDA ban sets a standard.** If Pennsylvania's governor says
non-disclosure agreements on public infrastructure decisions are unacceptable,
your planning board can say the same thing.

**4. Fast Track removal is the real leverage.** The single most concrete action
was pulling Amazon's \\$20 billion projects from expedited permitting. It signals
that even the largest developers can't buy their way past community opposition.

**5. Watch the legal challenge.** The consent-order model is legally novel for
data centers. If it survives court challenge, it becomes a template. If it
doesn't, the fallback is legislation — and HB 2650 already passed the House.

### How Pennsylvania compares

Shapiro claims the strictest guardrails in the nation. That's true among states
without an outright moratorium. For context:

- **New York** imposed a [1-year moratorium](/blog/ny-moratorium-eo62-2026.html)
  on 50+ MW facilities and proposed a \\$1M/MW community benefit benchmark
- **Georgia** introduced [HB 1059](https://legiscan.com/GA/text/HB1059/id/3339585)
  to ban local data center permits through December 2028, but the bill stalled —
  and Governor Kemp [vetoed](https://www.datacenterdynamics.com/en/news/georgia-governor-vetoes-bill-to-pause-data-center-tax-breaks/)
  a separate tax-exemption pause
- **Texas** [froze its entire interconnection queue](/blog/texas-ercot-queue-freeze-2026.html)
  of 474 GW

Pennsylvania's approach is different: it doesn't stop projects, it conditions
them. Whether that's stronger or weaker depends on enforcement — and whether
the consent-order model holds up in court.

### What to do now

- **Read the [full executive order](https://www.pa.gov/content/dam/copapwp-pagov/en/governor/documents/eo2026_05_protecting%20pennsylvania%20consumers%20from%20data%20center%20impacts_final_executed.pdf)**
  — print the GRID requirements list for your next planning meeting
- **If you're in Pennsylvania**, your municipality now has veto power. Use our
  [Start Here wizard](/app) to build a meeting brief with the GRID framework
  as leverage
- **If you're anywhere else**, bring the "growth pays for growth" principle
  and the NDA ban to your council. Pennsylvania just proved a governor can do
  this without the legislature
- **Contact your governor's office** using our [state directory](/states/) —
  executive orders don't require legislative majorities

---

*Sources: [PA.gov press release](https://www.pa.gov/governor/newsroom/2026-press-releases/governor-shapiro-signs-executive-order-on-data-center-developmen),
[EO 2026-05 full text (PDF)](https://www.pa.gov/content/dam/copapwp-pagov/en/governor/documents/eo2026_05_protecting%20pennsylvania%20consumers%20from%20data%20center%20impacts_final_executed.pdf),
[WHYY](https://whyy.org/articles/shapiro-data-centers-executive-order-pennsylvania/),
[Philadelphia Inquirer](https://www.inquirer.com/politics/pennsylvania/josh-shapiro-data-center-order-20260818.html),
[Pennsylvania Capital-Star](https://penncapital-star.com/technology-information/gov-shapiro-signs-data-center-executive-order-critics-say-it-falls-short/),
[Utility Dive](https://www.utilitydive.com/news/pennsylvania-executive-order-data-centers/828261/),
[PA.gov reaction roundup](https://www.pa.gov/governor/newsroom/2026-press-releases/what-people-are-saying-about-governor-shapiro-s-executive-order-)*
""",
    },
    # ── Texas freezes 474 GW ERCOT data center queue ──
    {
        "id": "texas-ercot-queue-freeze-2026",
        "art": "queue",
        "section": "stories",
        "title": "Texas Just Froze 474 GW of Data Center Interconnections. Here's What It Means.",
        "seo_title": "Texas freezes 474 GW of data center interconnections",
        "date": _dt.date(2026, 8, 13),
        "author": "GridWatch AI",
        "tags": ["ERCOT", "Texas", "grid", "demand", "infrastructure",
                 "moratorium", "Governor Abbott", "PUC", "analysis"],
        "summary": (
            "On August 3, Governor Abbott directed ERCOT and the PUC of Texas "
            "to halt all data center interconnection progress pending a "
            "comprehensive audit. The queue holds roughly 474 GW of requests "
            "— five times the state's record peak demand — and about 90% of "
            "them are data centers. It may be the single most consequential "
            "action any government has taken against the data center buildout."
        ),
        "body": """\
Six weeks ago, we wrote about [ERCOT's data center queue hitting
233 GW](/blog/ercot-queue-explainer.html) — a number so large it was hard to
take seriously. Since then, the queue has more than doubled. It now stands at
roughly **474 GW** of interconnection requests, according to filings reviewed
by [Utility Dive](https://www.utilitydive.com/news/texas-hits-pause-data-center-interconnections/827046/)
and multiple law firms tracking the situation. About **90% of those requests
are data centers**.

On August 3, Governor Greg Abbott did something no one in Texas energy policy
expected: he told ERCOT to stop.

### What happened

Abbott issued a
[directive](https://gov.texas.gov/news/post/governor-abbott-directs-comprehensive-data-center-audit)
to the Public Utility Commission of Texas (PUCT) and ERCOT ordering a
"comprehensive verification and audit" of every data center project in the
interconnection queue. His language was blunt: the scale of development "could
endanger the reliability and stability of the Texas electric grid," and "any
data center project that fails to comply with the verification and audit
process... must be denied."

ERCOT responded immediately:

- **Halted "Batch Zero"** — the large-load transmission planning study
  created under SB 6 (2025) to process applications of 75 MW or more.
  Approximately 204 GW was eligible; another 270 GW was applying but
  ineligible
- **Suspended classification notifications** that were scheduled for August 7,
  which would have told applicants whether their projects could move forward
- **Filed for a "good cause exception"** from the PUCT, to be heard at the
  [August 20 open meeting](https://www.ercot.com/services/comm/mkt_notices/M-A080326-01)

Until the audit is complete, no new data center project can advance through
ERCOT's interconnection process. There is no stated end date.

### The scale

To understand why this matters, compare the queue to the grid it's trying to
connect to:

| Metric | Value |
|--------|-------|
| ERCOT interconnection queue | **~474 GW** |
| Data center share of queue | **~90%** (~427 GW) |
| Texas record peak demand | ~91.3 GW (Jul 22, 2026) |
| Ratio: queue to peak | **5.2x** |
| Share of total US DC pipeline | ~20% (~49.8 GW near-term) |
| Revenue at risk (BNEF est.) | \\$8--15 billion by Q1 2027 |

Not every project in the queue will be built — most won't. Interconnection
queues are speculative by nature, and the attrition rate is typically 70-80%.
But even if only 10% of this queue materialises, that's 47 GW of new demand on
a grid that set its all-time peak of 91.3 GW just two weeks before the freeze.
ERCOT projects demand reaching approximately 175 GW by 2032 — roughly double
the current record.

Bloomberg New Energy Finance
[estimates](https://www.powermag.com/texas-audit-could-delay-49-8-gw-of-data-center-load-cost-projects-up-to-15-billion-bnef-warns/)
that 49.8 GW of data center load — nearly 20% of the entire U.S. development
pipeline — faces delays. Revenue at risk: \\$8 billion cumulative by Q1 2027,
rising to \\$15 billion in a worst case.

### What the audit covers

The directive's scope goes far beyond the usual grid-reliability review. Each
project must disclose:

1. **Tax incentives and public financial assistance** — what breaks are these
   projects getting, and are they worth it?
2. **Electricity demand projections** — projected annual and peak consumption,
   and whether the grid can serve the load
3. **On-site generation plans** — are developers building their own power
   (like Amazon's [7.65 GW gas plant in Pecos County](/blog/amazon-pecos-county-gas-plant-2026.html)),
   or relying on the shared grid?
4. **Water sourcing and reuse** — critical in a state where 64 public water
   systems are currently
   [limiting usage](https://www.tceq.texas.gov/drinkingwater/trot/droughtw.html)
   to avoid shortages, and data center water consumption could reach
   [399 billion gallons annually](https://texasscorecard.com/state/texas-data-centers-thirst-for-water-challenging-state-infrastructure/)
   by 2030
5. **Cooling technologies** — air-cooled, closed-loop, or water-efficient
6. **Community impacts** — noise, lighting, setbacks, traffic, emergency
   response
7. **Project ownership** — identifying all controlling interests

That last item is notable. Texas has seen a pattern of projects filed under
opaque shell companies, making it difficult for communities and regulators to
assess the financial backing or track record of applicants. The ownership audit
could force transparency that the market hasn't provided on its own.

### What triggered the survey stat

A proximate trigger was embarrassing data. When the PUCT sent a voluntary
survey to data center operators asking about water and power usage, only **28
of 377 companies responded** — a 7.4% response rate covering just 92
facilities. State Rep. Brad Buckley (R-Salado)
[called](https://www.texastribune.org/2026/06/23/texas-data-centers-puc-water-survey/)
participation "pretty pathetic" and said "bad data, bad study." The Data Center
Coalition's Dan Diorio cited concerns about "proprietary, confidential, and
competitive information." Non-compliance? A Class C misdemeanor — maximum \\$500
fine.

That stonewalling gave Abbott political cover. If the industry won't
self-report, the state will audit.

### What's exempt

The directive carves out two categories:

- **Projects with on-site generation** — if a developer is building its own
  power plant rather than drawing from the shared grid, the queue freeze
  doesn't apply. This effectively rewards the Amazon/Pecos County model (build
  your own gas plant) while penalising developers who planned to tap the grid.
- **Areas outside ERCOT** — El Paso (on the Western Interconnection) and parts
  of East Texas (on the Eastern Interconnection) are unaffected.

QTS Data Centers has already
[agreed to comply](https://gov.texas.gov/news/post/governor-abbott-announces-qts-data-centers-will-meet-texas-standards),
committing to closed-loop cooling, dedicated on-site power generation, and
ensuring projects don't increase residential electricity costs — becoming the
first major operator to publicly meet Abbott's standards. Meanwhile, Diode
Ventures
[withdrew](https://gov.texas.gov/news/post/east-texas-data-center-withdraws-after-falling-short-of-governor-abbotts-standards)
its proposed data center near Cedar Creek Lake after failing to meet them.
Abbott: "Data centers that want to do business in Texas must meet a clear
standard. This project did not."

### Abbott's reversal

The political arc is striking. In November 2025, Abbott celebrated Texas as
"the epicenter of AI development" when Google announced a \\$40 billion
investment. By June 10, 2026, he was issuing standards requiring data centers
to provide their own power and water. By June 30, he called for banning data
centers from "rural Texas neighborhoods." By August 3, he froze the entire
interconnection queue.

What changed? Three forces converged:

**Grid stress.** ERCOT set a new all-time peak of
[91,308 MW on July 22](https://www.eia.gov/todayinenergy/detail.php?id=67906),
and CEO Pablo Vegas warned that "the ease at which we got through last week's
peaks would not be the way I would characterize the future in two to three
years." Peak demand pressure is shifting to late evening when solar drops and
batteries deplete.

**Rural backlash.** Nearly half of planned facilities now target unincorporated
rural areas (up from 12%), and nearly two-thirds of rural Texans oppose
construction in their communities, per a UT/Texas Politics Project poll. Most
facilities are in districts with Republican representatives. Communities across
Texas — San Marcos, Hays County, Fort Worth, Denton — have been fighting data
center proposals for months. Nationally, **285 communities across 35 states**
have now enacted or proposed moratoriums, according to our
[tracker](/moratoriums.html). Hill County passed the state's first local data
center moratorium in May 2026 but
[rescinded it](https://www.texastribune.org/2026/06/05/texas-hill-county-moratorium-rescinded-data-centers/)
after a developer sued for \\$100 million — a cautionary tale about the limits
of local action.

**Bipartisan pressure.** Perhaps the most remarkable signal: Texas Agriculture
Commissioner Sid Miller, a Republican, called Abbott's directive
"[all hat and no cattle](https://www.texastribune.org/2026/08/06/sid-miller-republicans-elections-data-centers-abbott/),"
demanded a special session, and said Abbott should return campaign donations
from data center companies. "Republicans should be on this issue and we're
not," Miller said. "The Democrats are, and they're right." He warned
Republicans will lose statewide elections over data centers. When a Republican
statewide official tells his own party to follow the Democrats on an
infrastructure issue in Texas, the political ground has shifted.

### What it means for developers

Multiple law firms have published client advisories since the directive, and
the consensus is that this is not a temporary inconvenience:

- [Foley & Lardner](https://www.foley.com/insights/publications/2026/08/governor-abbott-pauses-texas-data-center-interconnections-and-calls-for-verification-and-audit-what-data-center-developers-need-to-know-now/):
  "open-ended approval delays" with "no one knowing how long audits will take."
  Advises developers to prepare comprehensive audit documentation immediately
- [Morrison & Foerster](https://www.mofo.com/resources/insights/260811-texas-governor-orders-data-center-moratorium-disrupting):
  the moratorium "disrupts projects under construction and challenges the
  ability of parties to existing transactions to comply with their contractual
  obligations"
- [Holland & Knight](https://www.hklaw.com/en/insights/publications/2026/08/texas-gov-abbott-directs-data-center-audit):
  "political strategy is now as critical as securing land and power access"
- [Troutman Pepper](https://www.troutman.com/insights/texas-hits-pause-on-data-center-grid-connections-amid-growing-oversight-push/):
  advises reviewing contracts for "change in law" and "force majeure" triggers

Oncor CEO Allen Nye
[maintained](https://www.utilitydive.com/news/fate-of-oncors-nearly-300-gw-load-pipeline-unclear-following-texas-data-ce/827303/)
confidence — "we continue to have really strong growth" — but Oncor's
\\$47.5 billion capital plan does not yet include Batch Zero spending. Sempra
CEO Jeff Martin backed the pause, supporting "durable long-term outcomes."

### What it means for communities

This is the most powerful signal yet that the "build first, ask permission
later" era of data center development may be ending — at least in Texas.

For communities currently fighting data center proposals, the audit provides
new leverage. If the state itself is questioning whether these projects are
worth the cost, a local planning board has cover to ask the same questions.

For communities where projects are already approved, the freeze changes nothing
directly. But the audit's findings — particularly on tax incentives and
community impacts — could reshape the terms of future negotiations everywhere.

### What to watch

- **August 20**: PUCT open meeting where ERCOT presents its "good cause
  exception" request. This will signal how long the freeze is likely to last.
- **The QTS model**: If individual projects can proceed upon completing their
  own audit (as
  [Jones Day notes](https://www.jonesday.com/en/insights/2026/08/texas-pauses-data-center-approvals-for-statewide-audit-stops-short-of-ban)
  is ambiguous in the directive), the freeze becomes a compliance filter rather
  than a blanket pause. Good actors advance; speculators exit.
- **On-site generation carve-out**: If the freeze pushes more developers toward
  building private gas plants to bypass the queue, the environmental
  implications could be significant — trading grid reliability risk for
  emissions risk.
- **January 2027 legislature**: PUCT has indicated it will seek expanded
  statutory authority when the 90th Texas Legislature convenes. Abbott has
  signaled he will pursue legislation codifying audit requirements, mandatory
  annual reporting of electricity and water usage, and repeal of data center
  sales tax exemptions.
- **Other states watching**: Ohio, Arizona, Illinois, and Oregon have already
  paused data center tax incentives. A Texas-scale queue freeze could inspire
  similar actions in PJM, SPP, or MISO territories where large-load queues
  are also growing.

### Unprecedented

ERCOT has never frozen its entire interconnection queue. The Batch Zero process
itself was brand new — created by SB 6 in 2025 — so the freeze hit the very
first cohort of applicants. For comparison, the last time Texas's grid was this
much in the national spotlight was February 2021, when
[Winter Storm Uri](https://energy.utexas.edu/research/ercot-blackout-2021)
caused 34 GW of unplanned outages, left 4.5+ million homes without power, and
killed at least 57 people. Since then, about 40,000 MW of generation has been
added. But NERC has warned that data centers' round-the-clock consumption makes
it harder to sustain supply during extreme demand — the very scenario Uri
demonstrated.

The freeze is Abbott's answer to a question Texas hasn't had to ask before:
what happens when the demand side of the grid grows faster than the supply side
can keep up?

---

*The [ERCOT queue explainer](/blog/ercot-queue-explainer.html) provides
background on how the interconnection process works and why the queue grew so
fast. Our [moratorium tracker](/moratoriums.html) tracks all 285 local and
state-level actions nationwide.*
""",
    },
    # ── Amazon's off-grid gas plant in Pecos County, TX ──
    {
        "id": "amazon-pecos-county-gas-plant-2026",
        "art": "grid",
        "section": "stories",
        "title": "Amazon's New Texas Data Center Could Become the Single Biggest Polluter in America",
        "seo_title": "Amazon's Pecos County data center: a top US polluter?",
        "date": _dt.date(2026, 8, 9),
        "author": "GridWatch AI",
        "tags": ["Amazon", "Texas", "Pecos County", "natural gas", "emissions",
                 "climate pledge", "off-grid power", "air pollution",
                 "public health", "TCEQ", "analysis"],
        "summary": (
            "Amazon confirmed it's investing in a 35-turbine, 7.65-gigawatt "
            "gas plant to power a new Texas data center — permitted to emit "
            "up to 33 million tons of CO2 a year, more than any power plant "
            "operating in the U.S. today. Because it won't initially connect "
            "to the wider grid, it also won't go through a utility rate case "
            "— which means the usual ratepayer-impact fight isn't where the "
            "leverage is this time."
        ),
        "body": """\
Amazon confirmed on Friday that it is investing in a large, dedicated
natural-gas power plant in Pecos County, Texas, built to run alongside a new
AI data center on the same site. According to permitting records reviewed by
[the *New York Times*](https://www.nytimes.com/2026/08/08/climate/amazon-data-center-texas-pollution.html),
the plant is permitted to release up to **33 million tons of carbon dioxide a
year** — enough, if it operates anywhere near that ceiling, to make it the
single largest source of climate pollution of any power plant in the country.

That is a genuinely large number, and it is worth being precise about why.
Natural gas burns cleaner than coal per unit of electricity generated. But
the current record-holder for U.S. power-plant emissions is a coal
plant — the James H. Miller Jr. plant in Quinton, Alabama, which
[reports](https://www.epa.gov/ghgreporting/ghgrp-power-plants) about 16
million tons of CO2 a year to the EPA. The Pecos County plant's *permitted
ceiling* is roughly double that. Scale beats fuel type: a gas plant built
big enough can out-pollute a coal plant even while burning the "cleaner"
fuel.

### The build, in numbers

Per the permits described in the *Times*' reporting, the plant will run
**35 natural-gas turbines** generating **up to 7.65 gigawatts** — enough
capacity to rank among the largest power plants in the country regardless of
fuel — dedicated to Amazon's data center. Two details matter more than the
headline number:

- **It won't initially connect to the wider grid.** This is a
  behind-the-meter, on-site plant, not a utility asset feeding the Texas
  grid ERCOT manages. Amazon says it's also evaluating solar and battery
  storage for the site.
- **It's in a remote part of West Texas, near the state's major
  gas-producing basins** — chosen, in part, precisely *because* fuel is
  cheap and close, and because bypassing the interconnection queue avoids
  the multi-year wait a grid-connected project would face.

Amazon spokeswoman Margaret Callahan said the plant would be "powered by new
on-site generation that won't raise electricity costs for Texas families."
That statement is narrowly true and worth taking seriously — and it is also
the whole reason this deal looks nothing like the ratepayer fights this site
usually covers. More on that below.

### A climate pledge under real strain

Amazon co-founded the Climate Pledge, a voluntary commitment to eliminate
its net carbon emissions by 2040. Its own emissions have risen every year
for the past several, and the company has acknowledged that AI data-center
growth is a direct threat to that goal — a tension the *Times* covered in
detail in [a companion piece on corporate climate
commitments](https://www.nytimes.com/2026/07/17/climate/company-climate-change-commitments-renege.html)
last month. Amazon's own framing hasn't changed: "our commitment hasn't
changed," Callahan said. Building the single largest emitting power plant in
the country is the test of whether that survives contact with an AI buildout
this size.

This isn't happening in a vacuum. The *Times*' ["Dirtier Air, Dirtier
Water" series](https://www.nytimes.com/2026/08/05/climate/data-centers-pollution-trump-ai-energy.html)
has been documenting how the Trump administration's "energy dominance"
push — fast-tracking data-center permitting, favoring oil, gas, and coal over
renewables — is directly shaping where and how this generation gets built.
Developers are choosing on-site gas plants specifically because they are
the fastest path to power that doesn't require years in a utility's
interconnection queue.

Michael Thomas, founder of Cleanview, the firm that
[first reported](https://newsletter.cleanview.co/p/scoop-amazon-is-behind-one-of-the)
Amazon's role in the project, called it a possible "foreshadowing of what's
to come": Amazon has historically bought its power from the ordinary utility
mix, and a shift to dedicated off-grid gas at this scale signals, in his
words, "an explosion of off-grid gas projects" in Texas and beyond.

### Why this doesn't fit the usual playbook

Every negotiating framework on this site — the [impact
calculator](/impact.html), the [PUC directory](/puc.html), the [model CBA
clauses](/cba-clauses.html) — assumes a data center is buying its power from
a regulated utility, which means there's a rate case, a docket, and a
ratepayer-impact number a community can put in front of a commissioner. An
off-grid, behind-the-meter power plant sidesteps that structure entirely.
There's no utility rate case to intervene in, because ratepayers aren't
paying for it — which is exactly what "won't raise electricity costs for
Texas families" means, and exactly why it's true.

That doesn't mean there's no leverage. It means the leverage moves to
different doors:

- **Air permits, not rate cases.** A 35-turbine gas plant needs air-quality
  permits from the Texas Commission on Environmental Quality (TCEQ), and
  TCEQ permits have public-comment periods and contested-case hearing
  rights. That's the process where local air-quality and health impacts —
  the smog-forming pollutants tied to heart disease and asthma that Public
  Citizen's Kathryn Guerra flagged in the *Times*' reporting — actually get
  argued on the record.
- **County tax abatements are still on the table.** Texas's data-center
  incentive statutes and county-level abatement agreements are negotiated
  locally, independent of how the facility gets its power. That's still the
  point where a community can attach binding community-benefit conditions.
- **Land use and zoning haven't gone anywhere.** A 7.65 GW gas plant is a
  large industrial facility in its own right, sited on land Pecos County
  still has zoning and permitting authority over.

The lesson for any community facing a similar "we'll build our own power"
pitch: ask *immediately* whether the plant will be grid-connected. If the
answer is no, the ratepayer argument disappears — and the fight has to move
to the air permit and the local land-use process on day one, not after the
first hearing.

> If a facility like this is proposed near you, the state and county air
> permit is usually where public comment actually lands — check your
> [state profile](/states/) for the environmental regulator to watch, and
> use the [story tracker](/story-tracker.html) to see whether other
> communities are already organizing around it.

### Sources

- [The New York Times — "New Amazon Data Center Stokes Worry It Would Be the Most Polluting Power Plant in the U.S." (Aug. 8, 2026)](https://www.nytimes.com/2026/08/08/climate/amazon-data-center-texas-pollution.html)
- [The New York Times — "Trump's Vision for A.I. Dominance Comes With Major Air Pollution" (Aug. 5, 2026)](https://www.nytimes.com/2026/08/05/climate/data-centers-pollution-trump-ai-energy.html)
- [The New York Times — "How to Abandon Your Climate Commitments and Get Away With It" (Jul. 17, 2026)](https://www.nytimes.com/2026/07/17/climate/company-climate-change-commitments-renege.html)
- [Cleanview — Amazon's involvement in the Pecos County plant](https://newsletter.cleanview.co/p/scoop-amazon-is-behind-one-of-the)
- [EPA GHG Reporting Program — power plant emissions data](https://www.epa.gov/ghgreporting/ghgrp-power-plants)
""",
    },
    # ── The Times' AI-chip-boom scale piece, translated for local negotiators ──
    {
        "id": "ai-chip-boom-scale-2026",
        "art": "money",
        "section": "stories",
        "title": "20 Million Chips Today, 200 Million by 2028: What the Times' AI Numbers Mean for Your County",
        "seo_title": "200 million AI chips by 2028: what it means for counties",
        "date": _dt.date(2026, 8, 9),
        "author": "GridWatch AI",
        "tags": ["AI infrastructure", "forecast", "investment", "capacity",
                 "Epoch AI", "backlash", "midterms", "negotiation",
                 "community advocacy", "analysis"],
        "summary": (
            "The Times went looking for a way to describe the scale of the "
            "AI build-out and landed on comparisons to the railroads and the "
            "Manhattan Project. The chip count — doubling roughly every nine "
            "months — is the number that explains why the pipeline of new "
            "proposals isn't slowing down. Here's what the rest of the "
            "numbers mean if you're the one facing the next one."
        ),
        "body": """\
[The *New York Times*' July 29 feature on the AI build-out](https://www.nytimes.com/interactive/2026/07/29/technology/ai-chips-data-center-boom.html)
opens with a hard problem: how do you describe a construction boom this size
in numbers a reader can actually hold in their head? Its answer — railroads
in the 1800s, the New Deal, the Manhattan Project — is the kind of
comparison that sounds like hyperbole until you look at the chip count.

### The numbers worth writing down

| What the Times reported | Number |
|---|---|
| AI chips in operation today (H100-equivalents) | **~20 million** |
| Time to double | **~9 months** |
| Projected by end of 2028 | **~200 million** — 10x today |
| Global AI-infrastructure investment, 2025 | **\\$318 billion** (IDC) |
| Global AI-infrastructure investment, forecast 2029 | **>\\$1 trillion** (IDC) |
| 5 largest U.S. hyperscalers' capex, 2026 (est.) | **~\\$750 billion**, up from ~\\$400B in 2025 (Goldman Sachs) |
| Cost per gigawatt of frontier AI data-center capacity | **\\$40–60 billion** (servers, land, connectivity, utility hookups) |
| Global data-center electricity use, 2025 | **64 GW** — roughly Germany's total consumption (SemiAnalysis) |
| Projected global data-center electricity use, end of 2030 | **~4x today** — more than South America and Africa combined |
| U.S. data centers today | **~5,500** — about 10x the next-closest country |
| Share of global AI compute controlled by the top U.S. hyperscalers | **~80%** (Epoch AI) |

Every one of those numbers is a proxy for the same underlying fact: the
industry believes bigger models need more chips, more chips need more
power, and whoever builds the most capacity first wins the race. Amazon's
Peter DeSantis, who leads the company's foundational AI models, put it
plainly to the *Times*: "It's hard to get your mind around the scale."

### Why "doubling every nine months" matters more than any single project

Most community fights are fought project by project — one rezoning
application, one interconnection request, one hearing at a time. That's the
right way to fight the project in front of you. But the compute numbers are
the reason there will be another one behind it, and another behind that.
If the chip count really doubles every nine months through 2028, the
pipeline of proposals hitting county planning boards over the next two
years won't be a continuation of the last two — it will be several times
larger. A county that has fielded one data-center proposal so far should
plan for that not being the last.

### The backlash the Times itself flagged

Buried in the middle of the piece is a sentence worth pulling out on its
own: data centers are shaping up as a **major issue in November's midterm
elections**, part of a "growing national movement" pushing back on the
industry — a trend the *Times* [documented in its own April
piece](https://www.nytimes.com/2026/04/27/technology/ai-artificial-intelligence-backlash.html).
That's a national newsroom confirming what this site's [story
tracker](/story-tracker.html) and [moratorium tracker](/moratoriums.html)
show every week in the headlines: this isn't a scattering of local NIMBY
disputes, it's a recognized national pattern, and organizers can now cite a
midterm-election-level story to make that case to a skeptical council
member.

### The bubble question is also a negotiating window

Economists quoted in the piece — including Philippe Aghion, who won the
2025 Nobel in economic science for research on innovation-driven growth —
point out that every past infrastructure boom of this shape (railroads,
electrification, the dot-com buildout) has been followed by a bust before
the technology's benefits fully materialized. Nobody knows if or when that
happens to AI. But the possibility cuts two ways for a community
negotiating right now:

- **Leverage now may be as good as it gets.** A developer racing to lock in
  capacity while the "arms race" framing holds (the *Times* quotes Oxford
  economist Carl Benedikt Frey: "if they don't invest, they are
  acknowledging defeat") is under real time pressure to get local approval
  fast. That urgency is exactly what makes binding community-benefit terms
  negotiable *before* groundbreaking — see the [model CBA
  clauses](/cba-clauses.html) — in a way they may not be once a project is
  already operating.
- **Decommissioning and stranded-asset language matters more, not less.**
  If capital spending this far ahead of realized revenue does correct, the
  facility that gets built fastest is also the one a community most needs
  a binding decommissioning bond and site-restoration clause for. We
  covered the same stranded-asset dynamic on the gas-plant side of this
  equation in [our post on Meta's Louisiana
  buildout](meta-hyperion-louisiana-ratepayer-fight-2026) — the logic holds
  here too.

### What to do with it

1. **Don't wait to see if the boom slows before you organize.** The
   Times' own numbers say it's accelerating, not cooling — if a proposal
   is active near you, the [Start here wizard](/start-here.html) builds a
   negotiating packet in minutes.
2. **Translate "gigawatts of compute" into your own numbers.** The
   \\$40–60B-per-gigawatt figure is a national average, not what's proposed
   in your county — run the actual facility size through the [impact
   calculator](/impact.html) for water, electricity, and rate-impact
   estimates specific to your state.
3. **Expect federal policy to keep favoring speed.** The same week this
   piece ran, the *Times* reported on the [White House's AI
   framework](https://www.nytimes.com/2026/08/04/technology/white-house-ai-framework.html)
   pushing to fast-track approvals nationally. As we wrote after Amazon's
   Pecos County, Texas plant, that shifts real leverage toward local air
   permits and zoning review — the layers federal fast-tracking reaches
   slowest.
4. **The capital is real, which means the ask can be too.** \\$750 billion
   in hyperscaler spending this year alone means a "we can't afford
   community benefits" objection from a developer this size rarely
   survives scrutiny — see what [similar communities have already
   won](/dividend.html).

The Times went looking for a comparison big enough to describe this
build-out and landed on the Manhattan Project. Whatever you think of that
comparison, the practical takeaway for a community is the same one that
document always has: the people who show up to the hearing before the
decision is made get a very different outcome than the people who show up
after.

### Sources

- [The New York Times — "The Impending, Inescapable Deluge of A.I." (Jul. 29, 2026)](https://www.nytimes.com/interactive/2026/07/29/technology/ai-chips-data-center-boom.html)
- [Epoch AI — AI chip ownership data (H100 equivalents)](https://epoch.ai/data/ai-chip-owners?view=graph&tab=h100_equivalents)
- [IDC — AI infrastructure spending forecast to eclipse \\$1 trillion by 2029](https://www.idc.com/resource-center/blog/ai-infrastructure-spending-caps-historic-year-at-90-billion-in-q4-2025-2029-spending-to-eclipse-1-trillion/)
- [The New York Times — the national AI backlash movement (Apr. 27, 2026)](https://www.nytimes.com/2026/04/27/technology/ai-artificial-intelligence-backlash.html)
- [The New York Times — the White House's AI framework (Aug. 4, 2026)](https://www.nytimes.com/2026/08/04/technology/white-house-ai-framework.html)
- [BIS Working Paper 1367 — past technology infrastructure booms and busts](https://www.bis.org/publ/work1367.pdf)
""",
    },
    # ── Evergreen SEO guide: property values ──
    {
        "id": "data-centers-property-values-2026",
        "art": "land",
        "section": "stories",
        "title": "Do Data Centers Lower Property Values? What the Studies Actually Show",
        "seo_title": "Do data centers lower property values? What studies show",
        "date": _dt.date(2026, 8, 6),
        "author": "GridWatch AI",
        "tags": ["property values", "home prices", "real estate", "JLARC",
                 "Northern Virginia", "Indiana", "community advocacy",
                 "buyouts", "explainer"],
        "summary": (
            "It's the first question at every hearing: will a data center "
            "tank my home's value? The honest answer isn't the scary one or "
            "the industry one. The headline studies say \"no measurable "
            "drag\" — but most were commissioned by developers, measure "
            "average distance rather than the house across the street, and "
            "come from hot markets where everything appreciates. Here's what "
            "the evidence really says, and the move that beats arguing about it."
        ),
        "body": """\
It is the first question at almost every hearing, and the one residents are
most often told not to worry about: *will a data center lower my home's
value?*

The honest answer is neither the frightening one nor the reassuring one the
developer's consultant will give you. The evidence is genuinely mixed — and
understanding **why** it's mixed is what lets you act on it.

### What the headline studies say

Two studies get cited constantly, and both point the same way:

- **Northern Virginia, 2023.** Researchers Terry Clower and Keith Waters of
  George Mason University's Center for Regional Analysis studied home sales
  across Fairfax, Loudoun, and Prince William counties. Their conclusion: the
  analysis
  [\"fails to demonstrate statistical evidence that proximity to a data center negatively impacts housing values\"](https://www.fxbgadvance.com/p/digital-insights-home-values-and)
  — in fact, closer homes tended to sell *higher*. The model explained 87% of
  the variance in 2023 sales.
- **Indiana, four counties.** Integra Realty Resources looked at single-family
  homes within 1.5 miles of four large data centers, 2021–2026. Homes near the
  facilities appreciated **42%** against **41%** countywide — essentially no
  gap.
  ([Bisnow's roundup](https://www.bisnow.com/national/news/data-center-community-relations/data-centers-may-not-be-a-drag-on-nearby-home-prices-135084)
  covers both.)

If you stop reading there — as the pitch deck wants you to — the answer is
"no effect." But three things about these studies deserve the fine print.

### Read the fine print

**1. Who paid for them.** The Integra Realty analysis was an appraisal
prepared in support of a proposed data center. Industry-commissioned studies
reliably find industry-friendly results. That doesn't make them wrong — but it
means they are advocacy, not neutral science.

**2. Averages hide the house across the street.** That same Indiana study,
broken out by county, is far less tidy: only one of the four counties (St.
Joseph) showed homes near the data center gaining *more* value. In the other
three — Allen, LaPorte, and Clark — homes near the facility appreciated **1%,
6%, and 9% less** than the surrounding market. The headline "42 versus 41"
washes all of that out. A county-wide average is not the appraisal on *your*
street.

**3. A rising tide hides the drag.** Both studies come from markets that were
appreciating fast. When every home is going up 40%, a data center's drag can
be invisible under the tide — and the George Mason authors said as much,
noting their findings may be "more applicable in areas with constrained
housing demand." In a flat or cooling market, the same facility could read
very differently.

### Where the discount actually lives: the first few hundred feet

Here is the detail the aggregate studies quietly bury. They measure homes
"within 1.5 miles" — but a data center's effect isn't spread evenly across a
mile and a half. It concentrates at the fence line. A Northern Virginia paired
case makes the gap concrete: a four-bedroom home roughly **200 feet** from a
hyperscale campus listed at **\\$580,000**, against comparable homes with no
data-center adjacency at
[\\$685,000–\\$710,000](https://www.ownluxuryhomes.com/markets/ai/guide/data-center-adjacent-residential-values)
— a discount of about **15–18%**.

That single case isn't a contradiction of the "no effect on average" studies —
it's the *resolution* of them. Average one house at −18% across a 1.5-mile ring
of hundreds of unaffected homes, and the signal vanishes. Two other findings
fit the same shape: University of Rochester researchers found
[little measurable effect on nearby prices](https://www.ipm.org/news/2026-04-13/will-data-centers-impact-property-values-depends-on-who-you-ask)
overall, while a separate George Mason–led analysis found new data centers
**slowed local home-price growth**. Even the industry-friendly work rarely
finds a clean positive — it finds "not as much, not as fast."

The practical takeaway: the closer your home is to the fence line, the less the
countywide averages tell you, and the more the appraisal turns on the specific
site — its setbacks, its cooling design, and which direction the substation
faces.

### What actually moves the number

The studies measure sale prices; they rarely isolate the things a neighbor
actually experiences. Those are the externalities to name at a hearing:

- **Noise** — a continuous low-frequency hum from cooling systems and
  generator testing that travels farther than ordinary sound and penetrates
  walls. The WHO's night-noise guideline sits around **40–45 dB**, which is
  exactly why our [model CBA clause](/cba-clauses) caps a facility at **45 dBA
  at the nearest residential property line**. Ask what the projected level is
  at *your* lot line, not at the fence.
- **Construction traffic** for the 12–18 months of the build — heavy trucks,
  road wear, and dust on a rural road that never carried it before.
- **Viewshed** — windowless industrial walls, security fencing, and substations
  replacing farmland or tree line. Appraisers price a view; they also price the
  loss of one.
- **Heat.** Across more than 6,000 data centers worldwide, surrounding land
  temperatures rose about
  [2°C on average from 2004 to 2024](https://fortune.com/2026/04/01/ai-data-centers-heat-island-hyperscalers/)
  — a measurable "data heat island" that raises neighbors' own cooling bills.

### The bottom line — and the move

"No measurable effect on average" is not "no effect on your house." The
evidence is mixed, mostly developer-funded, and almost never isolates
immediate adjacency in a normal market.

So don't get pulled into arguing the studies — **neutralize the risk
instead.** Communities facing pipelines, wind farms, and mines have won
[property-value guarantees and voluntary buyout programs](resource-extraction-precedent-2026)
for fifty years; there is no reason a \\$30-billion data center can't fund the
same. Make a property-value protection a condition of approval, not a hope.
Then run your own local numbers on the
[impact calculator](/impact) and bring them to the meeting.
""",
    },

    # ── Evergreen SEO guide: unmasking the LLC ──
    {
        "id": "unmask-data-center-llc-2026",
        "art": "oversight",
        "section": "stories",
        "title": "How to Unmask the Shell Company Behind a Data Center",
        "date": _dt.date(2026, 8, 6),
        "author": "GridWatch AI",
        "tags": ["shell companies", "LLC", "transparency", "NDAs",
                 "Project Blue", "Amazon", "public records", "site selection",
                 "community advocacy", "how-to"],
        "summary": (
            "A project lands in your town under a code name — \"Project "
            "Blue,\" \"Project Rowan\" — bought by an LLC no one has heard "
            "of. That anonymity is a strategy, not an accident. Here's the "
            "five-step method to find the hyperscaler actually behind it, "
            "worked through the real chain of shell companies that hid Amazon "
            "behind Tucson's Project Blue — and why naming them changes your "
            "leverage."
        ),
        "body": """\
A proposal appears in your county under a code name — *Project Blue*, *Project
Rowan*, *Project Ludi* — and the land is bought by a limited liability company
no one has heard of, formed a few weeks earlier. You can't find out who is
behind it, and that is not an accident. It is the plan.

### Why they hide

Developers manage what they call
[\"social license to operate\"](social-license-risk-2026) as a financial risk.
A code name and a shell LLC buy time: they let a project lock in land,
rezoning, and incentives *before* organized opposition can form around the
name of a company people recognize. By the time "Project Blue" is revealed as
a hyperscaler, the entitlements are often already granted.

### The patterns, by operator

Anonymity has fingerprints. From our own [site registry](/data-centers), the
major operators each shell their land deals in recognizable ways — and knowing
the family is often step zero:

- **Google** buys through land-acquisition shells named **Jet Stream LLC** and
  **Sharka LLC** — the same two names recur from The Dalles, Oregon to Northern
  Virginia.
- **Meta** rotates codename shells: **Greater Kudu, Raven Northbrook, Stadion,
  Pinnacle Mountain**, and **Wobniar** — which is "Rainbow" spelled backwards.
- **Microsoft** leans on project names and generic **"Holdings LLC"** entities,
  less consistently codenamed.
- **xAI (Colossus)** files through site- and retrofit-specific LLCs — the
  former Electrolux plant in Memphis is the known one.
- **OpenAI–Oracle (Stargate)** works through per-site developer LLCs like
  **Crusoe** and **Lancium** at Abilene, Texas.

If the LLC on your deed matches a name one of these companies has used
elsewhere, you may already have your answer before you file a single request.

### A worked example: how Amazon hid behind "Project Blue"

Tucson's Project Blue is the textbook case, because the layers eventually came
apart in public:

- The land was purchased by **Humphrey's Peak Property, LLC**, which then
  assigned its rights to a second shell, **Bobcat B1 LLC**, before the deal
  [closed on 290 acres](https://www.tucsonsentinel.com/local/report/122425_project_blue_close/).
- The named developer was **Beale Infrastructure**.
- The actual client was **Amazon Web Services** — a fact confirmed only when a
  Pima County
  [non-disclosure agreement surfaced](https://azluminaria.org/2025/10/01/pima-county-nda-confirms-amazon-is-behind-project-blue-data-center/),
  an agreement to keep Amazon's identity secret for *five years*.

Two shell LLCs, a development company, and a hidden hyperscaler behind an NDA:
that is the standard structure, not the exception. We documented the same
pattern of one project wearing
[different faces for different agencies](oversight-gaps-agency-shopping-2026)
in Tucker County, West Virginia.

### The five-step unmasking method

You can run most of this from a laptop before the next hearing.

**1. Pull the deed.** Your county recorder or assessor's property records name
the LLC that bought or optioned the land. In most counties this is free and
online. Note the sale date and the exact LLC name.

**2. Look up the LLC.** Search that name in your Secretary of State's business
registry. You're after the **registered agent**, the **organizer**, and the
**formation date**. A generic corporate agent (CT Corporation, a big law firm)
and a formation date weeks before the land deal are both tells that this is a
purpose-built shell.

**3. Match the pattern.** Hyperscalers reuse naming conventions, law firms, and
site-selection consultants across projects. Cross-reference the LLC and its
agent against our
[operator and site registry](/data-centers), which maps known operators to the
shell entities and campuses they've used elsewhere.

**4. Read the utility filings.** The land deal may be anonymous, but the power
isn't. Interconnection-queue entries and rate filings frequently name the load,
its size in megawatts, or the consultant representing it — even when the deed
does not.

**5. Request the development agreement and any NDA.** The public body
negotiating tax incentives holds the documents — including, as in Tucson, the
agreement specifying *who* they promised to keep secret. A public-records
request is the single highest-leverage step; the
[hearing-prep questions](/hearing-questions) page has language you can adapt.

### Why it's worth the effort

You cannot negotiate with a shell company. Putting the real name on the
project changes everything: it tells you the true power and water demand, it
gives you the corporate climate and community commitments you can hold the
company to, and it reveals
[what that operator has already conceded](/data-centers) to other communities.

Los Lunas, New Mexico is the proof. When the village traced **Greater Kudu
LLC** back to Meta, it didn't just win a name — it negotiated a water agreement
with real teeth: up to 3 million gallons a day, **automatically suspended in a
declared Stage 3 water emergency**, plus Meta funding for Rio Grande watershed
restoration worth roughly 172 million gallons a year. You cannot get a clause
like that from "Greater Kudu LLC." You get it from Meta. Anonymity is leverage
— for them. Naming them takes it back.
""",
    },

    # ── Evergreen SEO guide: jobs ──
    {
        "id": "data-center-jobs-2026",
        "art": "money",
        "section": "stories",
        "title": "How Many Jobs Does a Data Center Actually Create?",
        "date": _dt.date(2026, 8, 6),
        "author": "GridWatch AI",
        "tags": ["jobs", "economic development", "JLARC", "tax breaks",
                 "subsidies", "Virginia", "construction", "clawbacks",
                 "community advocacy", "explainer"],
        "summary": (
            "Every data center pitch leads with jobs — usually thousands of "
            "them. The number that actually matters is far smaller and fully "
            "knowable: a typical hyperscale hall runs on about 50 full-time "
            "workers, half of them contractors. Here's the real math from "
            "Virginia's own legislative watchdog, the construction mirage "
            "behind the big headline, and the three questions that put it on "
            "the record."
        ),
        "body": """\
Every data center proposal leads with jobs. The banner number is almost always
in the thousands. The number that matters for your community is far smaller —
and, unlike most of the pitch, it is precisely knowable.

### The claim versus the reality

Virginia's Joint Legislative Audit and Review Commission (JLARC) produced the
most thorough independent study of the industry to date. Its finding on
permanent employment:

> A typical 250,000-square-foot data center employs about **50 full-time
> workers** — roughly **one job per 5,000 square feet**, and about **half of
> those are contractors**, not the operator's own staff.

([JLARC, *Data Centers in Virginia*, 2024](https://jlarc.virginia.gov/landing-2024-data-centers-in-virginia.asp).)

Fifty people. For a building the size of several football fields drawing the
power of a small city. That is the operating reality of a facility designed,
by definition, to run on automation.

**And those fifty aren't the office jobs the pitch implies.** A running data
center employs security staff, HVAC and mechanical technicians, a few
electricians, and a small network/facilities crew. The servers are owned and
operated remotely by the tenant; the "high-tech jobs" mostly live at a
corporate campus in another state. What lands in your county is a hardened,
lightly-staffed industrial building.

### The construction mirage

So where do "thousands of jobs" come from? Construction. A large build can peak
at **as many as 1,500 workers on site** — but the build
[lasts just 12 to 18 months](https://www.wric.com/news/taking-action/jlarc-report-data-centers-virginia/),
and then those workers leave for the next site. A headcount that disappears in
eighteen months is not a tax base, and it is not what "jobs" means to a family
deciding whether to support a rezoning.

### The statewide illusion

JLARC credits data centers with **74,000 jobs, \\$5.5 billion in labor income,
and \\$9.1 billion in annual GDP** across all of Virginia. Those numbers are
real — but the majority is construction and indirect activity, not permanent
operations. When a developer quotes a *statewide industry total* to describe
*your one facility*, that is the sleight of hand to watch for. The state's whole
data center sector is not moving into your county; roughly fifty operating jobs
are.

### The number nobody puts on the slide: cost per job

Here is where it stings, and it's not a hypothetical — the per-job math has
been done. Good Jobs First found that eleven of the largest data centers
received public subsidies worth
[about \\$1.95 million per permanent job](https://www.datacenterdynamics.com/en/news/research-us-state-subsidies-pay-2-million-per-data-center-job/).
In Ohio, the per-job cost runs roughly **\\$1.4 million at Google's** facilities
and **\\$1 million at Meta's**. For comparison, Good Jobs First recommends states
cap data-center subsidies at **\\$50,000 per job** — the deals on the table today
routinely run twenty to forty times that.

Two facts make it worse. First, the giveaway is often unnecessary: Georgia's
own analysis concluded that **about 70% of data-center projects would have
located there even without the subsidy** — the state is paying billions for
investment it was already getting. Second, the largest state exemptions now
cost
[over \\$1 billion a year each](data-center-tax-break-blowouts-2026), and Georgia
alone raised its projected FY2026 loss to **\\$2.5 billion**. The jobs are real.
They are just, per job, among the most expensive economic development a state
can buy.

### The move: three questions for the record

Don't argue the banner number — pin down the real one. Ask these at the
hearing, and ask for the answers *in writing* (the
[hearing-prep page](/hearing-questions) has more):

1. **How many permanent, full-time jobs employed by the operator** — not
   contractors — and will that floor be guaranteed in the agreement?
2. **What is the total public subsidy, and the subsidy *per permanent job*?**
3. **Is there a clawback** if the promised job numbers aren't met?

Then set the answer next to the [tax breaks on the table](/tax-breaks) and run
your own local figures on the [impact calculator](/impact). A project that
genuinely creates lasting jobs will answer all three without flinching. Most
can't.
""",
    },

    # ── Ezra Klein "The A.I. Revolt Is Here" — backlash goes mainstream ──
    {
        "id": "ezra-klein-ai-revolt-mainstream-2026",
        "art": "media",
        "section": "stories",
        "title": "\"The A.I. Revolt Is Here\": When Ezra Klein Covers Your Zoning Fight, the Politics Have Changed",
        "seo_title": "Ezra Klein's 'AI revolt': data center fights go mainstream",
        "date": _dt.date(2026, 8, 4),
        "author": "GridWatch AI",
        "tags": ["Ezra Klein", "Jasmine Sun", "backlash", "moratoriums",
                 "New York", "public opinion", "politics", "media",
                 "community advocacy", "analysis"],
        "summary": (
            "The Ezra Klein Show's August 4 episode is titled \"The A.I. "
            "Revolt Is Here,\" and its subject is data centers — the "
            "bipartisan opposition, Hochul's New York moratorium, and the "
            "100-plus moratorium proposals nationwide. When the country's "
            "flagship policy podcast frames local zoning fights as a "
            "national political force, the leverage map has changed. "
            "Here's what the episode covers, what our own tracker shows, "
            "and why this moment favors communities that are ready to "
            "negotiate."
        ),
        "body": """\
The Ezra Klein Show's August 4 episode is titled
[\"The A.I. Revolt Is Here\"](https://www.nytimes.com/2026/08/04/opinion/ezra-klein-podcast-jasmine-sun.html)
([also on YouTube](https://www.youtube.com/watch?v=rbgvTlt1VB8)), and the
opening question tells you everything about where this issue now sits:
what's big and ugly and has united Republicans and Democrats? **A.I. data
centers.**

Klein's guest is [Jasmine Sun](https://jasmine.substack.com/), whose
newsletter covers both the culture inside the A.I. companies and the anger
building against them — and who had just returned from a Midwest reporting
trip interviewing people on every side of a data center fight. The episode
runs 78 minutes, and its framing rests on three facts that will be
familiar to anyone reading this site:

1. **An overwhelming majority of Americans say they'd oppose a data
   center built near where they live.**
2. **New York Gov. Kathy Hochul just imposed a one-year moratorium on
   data center construction** — the same executive order we broke down
   [when it happened](ny-moratorium-eo62-2026).
3. **There are more than 100 local or statewide moratorium proposals**
   across the country.

Klein's question is whether A.I.'s momentum has finally met, in the
show's words, \"the messy politics of getting things done in the real
world\" — and whether the backlash is about the buildings or about A.I.
itself.

### Why this episode matters more than most coverage

Not because the facts are new. Our
[moratorium tracker](/moratoriums) currently documents **99
moratoriums and bans, 73 of them enacted** across 29 states — and that is
still a floor, not a census: every week of local reporting turns up more,
and our review queue is never empty. We called this
[the moratorium wave](moratorium-wave-2026) back in the spring, and the
[Morgan Stanley analysis](morgan-stanley-opposition-bottleneck-2026)
identifying community opposition as the industry's binding constraint is
five months old.

What's new is **who is saying it**. The Ezra Klein Show is the closest
thing American liberalism has to a policy seminar of record — the
audience is staffers, regulators, journalists, and the people who write
the next round of legislation. For two years, data center opposition has
been covered as a local-news story: a county board here, an angry hearing
there. The national frame was \"NIMBYs vs. progress.\" This episode
retires that frame. When the flagship abundance-agenda podcast — hosted
by the co-author of a book *about how America should build more,
faster* — leads with the revolt rather than the buildout, the opposition
has stopped being a nuisance narrative and become a political fact both
parties have to plan around.

That's consistent with what the polling has shown all year: opposition
to nearby data centers isn't a partisan position, it's a
near-consensus one — and it's strongest in the rural and exurban
counties where the projects actually land, the same places we mapped in
our [rural buildout coverage](/states/).

### The question Klein asks is the question that matters

Midway through the framing there's a distinction worth sitting with: how
much of the backlash is about **the construction** — the noise, the
water, the transmission lines, the tax deals — and how much is about
**A.I. itself**: job anxiety, Sun's \"permanent underclass\" essay, the
sense that a handful of companies are reshaping the economy without
asking anyone.

For communities, the honest answer is: it doesn't matter, and the
distinction mostly benefits developers. Every concrete grievance in the
first category is negotiable — that's what
[CBAs](questions-to-ask-data-center-checklist-2026), water agreements,
noise limits in permits, and
[tax-deal transparency](data-center-tax-break-blowouts-2026) are for.
The second category is why the leverage exists. A developer who can no
longer count on the national narrative treating opponents as cranks has
a much stronger incentive to sign something enforceable.

### Moratoriums are negotiating positions, not endings

The episode asks whether slowing A.I. down is good or bad. Our outcome
data suggests that's the wrong binary. Of the six resolved moratorium
fights we've documented in the
[tracker's case studies](/moratoriums), **three ended with the community
securing a Community Benefit Agreement** — the moratorium wasn't the end
state, it was the leverage that produced a deal. One produced a
sustained ban, one a political shift, and only one ended with no
protections. A pause that forces real terms onto paper is not
anti-growth; it's the mechanism by which growth starts paying its own
way.

That's the reading we'd offer of Hochul's New York order, too: a
one-year clock during which the state writes rules — not a wall. The
communities that come out of these pauses best are the ones that spend
the year preparing, not celebrating.

### If the revolt is here, be ready to negotiate

A national spotlight raises leverage; it doesn't exercise it for you.
Three places to start:

- **[The 26-question checklist](questions-to-ask-data-center-checklist-2026)**
  — the questions to put on the record while attention is high.
- **[The moratorium tracker](/moratoriums)** — what 47 other
  jurisdictions did, and what happened next.
- **[Model CBA clauses](/cba-clauses)** and the
  **[data-dividend calculator](/dividend)** — the language communities have
  actually won, and what the revenue is worth to yours.
- **[Start here](/start-here)** — a meeting-prep brief generated for your
  specific hearing.

The episode's title is a diagnosis. Whether the revolt produces
enforceable community wins or just louder hearings is decided county by
county — usually in the ninety days after everyone else stops paying
attention.
""",
    },
    # ── Data center tax-break cost blowouts (Good Jobs First, June 2026) ─
    {
        "id": "data-center-tax-break-blowouts-2026",
        "art": "money",
        "section": "stories",
        "title": "The \\$327 Million Guess That Became \\$2.5 Billion: States Are Finally Learning What Data Center Tax Breaks Cost",
        "seo_title": "Data center tax breaks: the $327M guess that hit $2.5B",
        "date": _dt.date(2026, 8, 4),
        "author": "GridWatch AI",
        "tags": ["tax breaks", "subsidies", "Good Jobs First", "Georgia",
                 "Ohio", "Texas", "Virginia", "Indiana", "state budgets",
                 "transparency", "analysis"],
        "summary": (
            "Four states now lose more than \\$1 billion a year to data "
            "center sales-tax exemptions — and every one of them originally "
            "projected a fraction of that. Georgia revised its estimate up "
            "664% in one January. Ohio's real cost came in at 12 times its "
            "projection. Indiana admitted 83% of its subsidy went to one "
            "company: Amazon. Fourteen states still won't publish a number "
            "at all. Here's what the June 2026 Good Jobs First report "
            "found, and what it means for the fiscal-note fight in your "
            "county."
        ),
        "body": """\
A headline crossed our [news feed](../news/) this week —
[\"Data Center Tax Breaks Promised 'No Significant Fiscal Impact': States
Are Losing Billions\"](https://www.techtimes.com/articles/322775/20260803/data-center-tax-breaks-promised-no-significant-fiscal-impact-states-are-losing-billions.htm)
(Tech Times, August 3). The story behind the headline is a June 2026
report from **Good Jobs First**, the subsidy-watchdog group, with the
memorable title
[*Even Cloudier with a Greater Loss of Spending Control*](https://goodjobsfirst.org/even-cloudier-with-a-greater-loss-of-spending-control-how-data-center-tax-abatements-undermine-public-budgets/)
(Kasia Tarczynska). It is the most complete accounting yet of what data
center tax exemptions actually cost states — and the pattern it documents
is the same one we keep finding in
[capacity markets](pjm-capacity-auction-ratepayer-shock-2026) and
[ratepayer fights](meta-hyperion-louisiana-ratepayer-fight-2026): the
original estimate is always wrong, and always wrong in the same direction.

### The tire and the chip

The report opens with the cleanest explanation of this subsidy we've seen.
When General Motors buys an \\$80 tire to build a car, it pays no sales
tax — correctly, because GM isn't the end user; the car buyer pays tax on
the whole car at the dealership. But when Amazon Web Services or Google
buys an Nvidia AI chip for \\$30,000–\\$50,000, **in 37 states it also
pays no sales tax** — even though the data center *is* the end user. There
is no downstream consumer purchase where the tax gets collected. It's
simply gone. Multiply by tens of thousands of chips per hyperscale
campus — plus servers, generators, cooling systems, and in some states
electricity and building materials — against an industry that spent
roughly **\\$375 billion** on AI infrastructure in 2025 and has slated
about twice that for 2026.

### Every estimate was wrong, and all in the same direction

What makes the report unusual is that it isn't projections — it's the
record of what happened when states finally checked:

- **Georgia** projected its data center exemption would cost \\$327
  million in FY 2026. In January 2026 it revised that to **\\$2.5
  billion** — a 664% increase — and projected **almost \\$3 billion for FY
  2027**. Three-year cumulative cost, 2025–2027: **\\$7.3 billion**.
- **Ohio** initially projected \\$135.8 million. In May 2026 the
  Department of Taxation revealed the real 2025 cost: **\\$1.6 billion**
  at the state level alone — **12 times the projection** — after \\$555
  million in 2024. Days after the numbers became public, Gov. Mike DeWine
  paused the program for new applications. (Existing contracts keep their
  breaks.)
- **Indiana** didn't disclose at all until Good Jobs First called it out
  in April 2026. It then admitted to **\\$655.6 million** in cumulative
  losses — and that **83% went to a single company, Amazon**: \\$50.5
  million in 2024, then \\$561 million in 2025, a **1,011% one-year
  increase** to one firm.
- **Texas** projects \\$1.3 billion for FY 2026, rising to \\$1.75
  billion by FY 2030 — a cumulative **\\$9 billion** between 2025 and
  2030.
- **Virginia**'s exemption cost \\$136 million in FY 2022. For FY 2025,
  counting state and local losses, it's **\\$1.94 billion** — a
  fourteen-fold increase in three years.
- **North Carolina**'s 2015 fiscal note projected **\\$4 million a
  year**. Current estimates: \\$45–57 million annually — and if planned
  projects are built, an additional **\\$1.5–2.3 billion** during
  construction. Gov. Josh Stein's own words: \"When this tax break was
  enacted in 2006 and then widened in 2015, we lived in an entirely
  different world.\"
- **Wisconsin**'s number only exists because a state senator forced the
  Legislative Fiscal Bureau to produce it: **\\$1.5 billion** during
  construction of four planned projects, then \\$269 million a year.
- Smaller programs are blowing out at the same rate: **Pennsylvania** up
  180% in one year (\\$41M → \\$114.8M), **Arizona** up 98% (\\$19.4M →
  \\$38.5M).

The report's summary of the mechanism: these exemptions were written for
an era of small server rooms, and are now being claimed by \\$50-billion
hyperscale campuses under the same statutes. Most programs have **no
caps**, no sunset dates, and — critically — **no requirement that
companies report how much tax they avoided**. States are guessing, and
the guesses are systematically low.

### Fourteen states won't publish a number

Per [Stateline's coverage](https://stateline.org/2026/04/15/many-states-dont-report-losses-from-data-center-tax-breaks-study-says/)
(Kevin Hardy, April 2026), fourteen states with data center exemptions
disclose no aggregate cost at all: Alabama, Arkansas, Idaho, Iowa,
Indiana*, Louisiana, Maryland, Mississippi, Missouri, North Carolina,
North Dakota, Oklahoma, South Carolina, and Utah. Good Jobs First argues
this violates Governmental Accounting Standards Board reporting standards
for tax abatements. As executive director Greg LeRoy put it: \"No form of
state spending is more out of control today than data center tax
abatements.\"

*\\*Indiana disclosed after the April report — see above.*

The local layer is worse-documented still. Sales-tax exemptions granted
by states silently drain **local** budgets too: Georgia localities are
projected to lose **\\$1.1 billion in 2026** and \\$1.4 billion in 2027.
And that's before local property-tax abatements — in Oregon, data centers
owned by Amazon, Apple, Alphabet, and Meta collected **\\$616 million**
in property tax abatements between 2016 and 2025, with annual costs up
762% over the period.

### The turn has started

The same report season produced the fastest wave of subsidy pullbacks
this industry has seen:

- **Ohio** paused its program for new applicants (May 2026).
- **Illinois**' governor called for suspending the exemption; the state
  hasn't disclosed annual losses since 2023 (\\$361 million).
- **Maine** approved the country's first statewide moratorium on data
  centers over 20 MW, through November 2027.
- **North Carolina** is moving to phase out its exemptions.
- **Oklahoma** passed ratepayer protections; **New Jersey** froze a
  program; **Arizona** paused incentives.

Good Jobs First's own recommendation goes further — end the subsidies, or
at minimum impose moratoriums until costs are known, and add caps,
sunsets, transparency requirements, and construction-phase-only
eligibility to anything that survives.

### What this means at your county hearing

Every one of these numbers started as a fiscal note that said \"no
significant impact.\" That's question 13 on our
[26-question checklist](questions-to-ask-data-center-checklist-2026):
demand the tax revenue projection **after** all abatements, signed by an
independent economist — not the developer. This report is the evidence
for why that demand is reasonable. When the official estimates in
Georgia, Ohio, and North Carolina were off by 8×, 12×, and 14×, \"trust
the fiscal note\" is not a plan.

Three GridWatch tools pair with this story:

- **[Your bill, explained](/bills)** — how data center load shows up on
  residential electric bills, the other half of the subsidy story.
- **[Data dividend calculator](/dividend)** — what a revenue-sharing
  deal would look like if your community negotiated one instead.
- **[PUC directory](/puc)** — where to file comments in your state.

If a developer's pitch deck says the tax break \"pays for itself,\" ask
which of these ten states' fiscal offices reviewed the math. The answer
so far, everywhere anyone has checked, is that nobody did.
""",
    },
    # ── Questions to ask before approving a data center (checklist) ─────
    {
        "id": "questions-to-ask-data-center-checklist-2026",
        "art": "checklist",
        "section": "stories",
        "title": "Before You Approve a Data Center: 26 Questions Every Community Should Ask",
        "seo_title": "26 questions to ask before approving a data center",
        "date": _dt.date(2026, 8, 2),
        "author": "GridWatch AI",
        "tags": ["checklist", "community advocacy", "CBA", "negotiation",
                 "public engagement", "NDAs", "decommissioning",
                 "ratepayers", "process", "analysis"],
        "summary": (
            "A working synthesis of the checklists published by RFD-TV, "
            "Public Knowledge, EDF, the AI Now Institute, and the Alliance "
            "for the Great Lakes — collapsed into 26 questions, grouped by "
            "topic, with the reason each one matters and what a good answer "
            "looks like. Print it, bring it to the hearing, ask them all."
        ),
        "body": """\
Half a dozen advocacy groups have published \"questions to ask a data center
developer\" guides in the last six months. They mostly agree with each other
— and that consensus is the point. When RFD-TV's rural readers, Public
Knowledge's D.C. tech-policy shop, EDF's environmental lawyers, the AI Now
Institute, and the Alliance for the Great Lakes all converge on the same
questions, a community that walks into a hearing with those 26 questions is
walking in with the current professional consensus of what a diligent local
official is supposed to ask.

This is that combined list. Each question has a **why it matters** line and
a **what a good answer looks like** line — because a question you can't
interpret is easy for a developer to deflect. Nothing here is exotic. What's
exotic is asking them all before the ink is dry.

**Sources synthesized:** RFD-TV
([Tony St. James, Jul 2026](https://www.rfdtv.com/before-approving-a-data-center-experts-say-communities-should-ask-tough-questions)),
Public Knowledge
([Nat Purser, Apr 2026](https://publicknowledge.org/what-to-ask-when-a-data-center-comes-to-town/)),
EDF Energy Exchange
([Benson & Calhoun, Jul 2026](https://blogs.edf.org/energyexchange/2026/07/14/laying-the-foundation-communities-deserve-a-voice-in-the-data-center-boom/)),
AI Now Institute community toolkit, and the Alliance for the Great Lakes
[Community Checklist for Evaluating Data Center Impacts](https://greatlakes.org/wp-content/uploads/2026/03/AGL_CommCheck_EvalDataCenter_2026_Final.pdf).

---

### 1. Who pays for the infrastructure this facility demands?

This is the single most important question and the one developers try
hardest to compress into a soundbite. A hyperscale campus routinely requires
new substations, new transmission lines, water main upgrades, road
improvements, and often new generation capacity. All five sources agree that
communities must ask, in writing, **who pays for each of those**.

**1. Will the developer cover the cost of the new substation and any
distribution upgrades — or will the utility recover them from all
ratepayers?**
*Why it matters:* Most large-load tariffs make the developer pay for
\"direct\" upgrades but silently place \"shared\" upgrades into the general
rate base. That's how a single tenant can raise everyone's bill.
*What a good answer looks like:* A dollar figure, a cost-allocation clause
in the tariff filing, and a public commitment to a **minimum bill floor** or
**exit fee** if the tenant leaves early.

**2. Who pays for new transmission lines built to serve the load?**
*Why it matters:* Transmission is the biggest hidden subsidy in the current
buildout. Louisiana's Meta deal put a \\$470M+ 60-mile line into Entergy's
general rate base — costs shared across every household in the state
([Alliance for Affordable Energy](https://www.all4energy.org/watchdog/meta-data-center-to-cause-entergy-bill-increase/)).
*What a good answer looks like:* A signed cost-allocation agreement that
names the developer as the sole beneficiary and assigns them the incremental
cost.

**3. What is the term of the developer's power contract vs. the payback
period of the infrastructure being built?**
*Why it matters:* A 15-year contract that requires 30 years of infrastructure
means ratepayers own the second half. Meta/Entergy is the current textbook
case.
*What a good answer looks like:* Matched terms, or explicit stranded-asset
protection paid for by the developer.

**4. Has the developer signed a Large Load Interconnection Agreement, and
can we see the tariff?**
*Why it matters:* The public tariff is the enforceable document. Everything
in press releases is marketing.
*What a good answer looks like:* A publicly filed tariff and a link to the
Public Utility Commission docket.

### 2. Water

**5. What is the projected annual and peak-summer water consumption, and in
what units?**
*Why it matters:* Peak summer draw is the number that stresses drought-year
supplies. Annual averages hide it.
*What a good answer looks like:* Gallons per day at peak, an independent
hydrologist's review, and a commitment to publish actual consumption
quarterly.

**6. What is the water source — groundwater, municipal, surface, or
recycled?**
*Why it matters:* Groundwater draw depletes aquifers permanently in some
basins; municipal draw competes with residential supply during shortages.
*What a good answer looks like:* A signed water-supply agreement naming the
source, volume, and priority tier during drought restrictions.

**7. What cooling technology will be used — evaporative, closed-loop, dry
cooling, or hybrid?**
*Why it matters:* Cooling choice is the single biggest lever on water use.
Dry cooling uses ~1% of the water of evaporative cooling but costs more
capex.
*What a good answer looks like:* Named technology, PUE and WUE
(Water Usage Effectiveness) commitments, and a design review shared with
the local water utility.

**8. During declared drought restrictions, does the facility comply — or
is it exempt?**
*Why it matters:* Several state deals exempt data centers from local
watering restrictions. Residents cutting lawn watering while a facility
draws millions of gallons is a political flashpoint.
*What a good answer looks like:* Explicit inclusion under existing drought
ordinances with no carve-outs.

### 3. Power, emissions, and backup generation

**9. What is the peak electrical demand in megawatts, and over what
ramp-up period?**
*Why it matters:* The MW number determines everything downstream — grid
upgrades, gas plants, capacity charges.
*What a good answer looks like:* A single, unqualified number and a
commissioning schedule.

**10. How many backup generators, what fuel, how much on-site fuel storage,
and how many hours per year of testing?**
*Why it matters:* Backup generators are usually diesel or natural gas. Their
testing schedule determines local air quality — and in some cases, they
operate as \"non-emergency\" peakers that skip air-permit review entirely.
xAI's Memphis facility ran gas turbines without air permits in a
predominantly Black community with the region's highest pollution-related
illness rates
([Public Knowledge](https://publicknowledge.org/what-to-ask-when-a-data-center-comes-to-town/)).
*What a good answer looks like:* Named generator count, fuel type, testing
hours capped in the permit, and full air-permit compliance before turn-on.

**11. Will the facility meet or exceed carbon-intensity benchmarks
(hourly matching, 24/7 CFE), or only annual RECs?**
*Why it matters:* Annual renewable energy credits let a developer claim
\"100% renewable\" while running on gas at night. Hourly matching or 24/7
carbon-free energy is the real test.
*What a good answer looks like:* A public 24/7 CFE commitment with
transparent reporting.

### 4. Local economics — what your community actually gets

**12. How many permanent jobs after construction ends, and at what wages?**
*Why it matters:* Construction employment is real but temporary. Permanent
staffing is usually 30–150 people for a hyperscale campus — often far less
than the developer's talking points imply.
*What a good answer looks like:* A contractually binding minimum, broken
out by role and wage, with a local-hire clause.

**13. What is the tax revenue projection AFTER all abatements, exemptions,
and PILOT agreements?**
*Why it matters:* Headline tax revenue is gross. Net revenue after
abatements can be a small fraction. Prince William County, VA saw data
center tax revenues rise from \\$6.5M to \\$166.4M between 2012 and 2023
— but rate pressure on residents rose with it
([Public Knowledge](https://publicknowledge.org/what-to-ask-when-a-data-center-comes-to-town/)).
*What a good answer looks like:* A ten-year net-revenue projection signed
by an independent economist, not the developer.

**14. Is there a Community Benefit Agreement, and is it enforceable in
the permit — not a side letter?**
*Why it matters:* A CBA that lives outside the permit is a promise with no
teeth. A CBA written into the permit is a legal obligation.
*What a good answer looks like:* A CBA drafted as a permit condition, with
clear remedies for breach and a named community signatory who can enforce
it.

### 5. Noise, land use, and daily life

**15. What are the noise levels at the property boundary and at the nearest
residence — measured in dBA and in low-frequency dB(C)?**
*Why it matters:* dBA understates the low-frequency hum that data center
cooling produces. The 24/7 low-frequency component is what triggers
resident lawsuits.
*What a good answer looks like:* Both measurements, with limits written
into the permit and third-party acoustic monitoring after commissioning.

**16. What are the setbacks from residences, schools, and hospitals?**
*Why it matters:* Setbacks are the cheapest and most durable community
protection. They cannot be negotiated away later.
*What a good answer looks like:* Larger than the zoning minimum, in
writing.

**17. Can the developer expand the site later without triggering a new
public review?**
*Why it matters:* Many projects double or triple in size after approval.
Language allowing \"as-of-right\" expansion is a trap door.
*What a good answer looks like:* Every phase requires a fresh public
hearing.

### 6. Transparency and process

**18. Has any local official been asked to sign an NDA?**
*Why it matters:* The AI Now toolkit and every other source in this list
say the same thing: **local officials should not sign NDAs**, and communities
should adopt ordinances banning them.
*What a good answer looks like:* No NDAs. Full disclosure of every entity
in the developer's corporate structure — shell LLCs included.

**19. Who exactly is the developer, and every parent, subsidiary, and
tenant?**
*Why it matters:* Data-center deals routinely surface through shell LLCs
that hide the ultimate tenant (Amazon, Microsoft, Meta, xAI). Communities
have a right to know who they are negotiating with.
*What a good answer looks like:* A signed disclosure identifying the LLC
chain and the anchor tenant. If the tenant is \"confidential,\" walk away.

**20. Have there been public meetings advertised in advance, held at times
when working people can attend?**
*Why it matters:* A 2 p.m. Tuesday hearing is engineered for low turnout.
*What a good answer looks like:* Minimum two evening or weekend meetings
before approval, with 30 days' notice.

**21. Will the developer publish an annual environmental impact report to
the community — water, power, emissions, noise complaints — with third-party
audit?**
*Why it matters:* Without ongoing reporting, promises decay.
*What a good answer looks like:* A binding reporting clause in the permit
with a named enforcement path.

### 7. Closure and accountability

**22. Is a decommissioning plan required, filed, and approved BEFORE
construction begins?**
*Why it matters:* Data centers are built to depreciate over 10–15 years,
but the buildings, transformers, batteries, and cooling infrastructure can
sit derelict for decades if the operator walks. Fixing decommissioning
after the fact is impossible.
*What a good answer looks like:* A plan filed as a permit exhibit before
groundbreaking.

**23. Is there a financial assurance mechanism — a surety bond, escrow, or
letter of credit — sized to the full removal cost?**
*Why it matters:* Bankruptcy or sale can leave the community with an
abandoned facility. Financial assurance is the only thing that protects
against that.
*What a good answer looks like:* A bond sized by an independent cost
estimator, updated every five years for inflation.

**24. Who is liable if the parent company sells, spins off, or goes
bankrupt?**
*Why it matters:* Corporate structures shift. Rights of first refusal on
sale, successor-liability language, and personal guarantees from the
parent are all standard tools.
*What a good answer looks like:* Successor liability written into the CBA
and land-use agreement.

**25. Does the site have to be restored to its prior productive use — and
who decides what \"restored\" means?**
*Why it matters:* \"Restoration\" without a definition means slab and
gravel. Farmland restoration means topsoil.
*What a good answer looks like:* A written restoration standard signed by
a state agricultural or land-use agency, not the developer.

**26. What's the enforcement mechanism if any commitment is broken?**
*Why it matters:* All of the above is worthless without a way to enforce
it. Communities usually assume the county attorney will handle enforcement.
County attorneys are usually not staffed for a multi-year fight with a
Fortune 100 company.
*What a good answer looks like:* Named enforcement authority, funded
enforcement budget, and third-party arbitration.

---

### How to use this list

You are unlikely to get 26 clean answers in one hearing. That's the point.
Ask them, publish the ones the developer refuses to answer, and let the
gap between the questions asked and the answers given become part of the
public record.

If your community is at the beginning of a fight, GridWatch has three tools
that pair with this checklist:

- **[Start Here wizard](/start-here.html)** — pick your state, size the impact,
  see what similar communities have won.
- **The negotiation toolkit in the app** — CBA templates, model clauses,
  and a meeting-prep generator that produces a downloadable brief for your
  specific hearing.
- **[PUC directory](/puc.html)** — every state Public Utility Commission
  and where to file a comment on the tariff.

The best time to ask these questions was before the developer picked your
county. The second-best time is at the next public hearing.
""",
    },
    # ── Meta Hyperion (Richland Parish, LA) — who pays for 5 GW ──────────
    {
        "id": "meta-hyperion-louisiana-ratepayer-fight-2026",
        "art": "transmission",
        "section": "stories",
        "title": "\"Meta pays the full cost.\" Louisiana ratepayers pay \\$8–13 a month. Both are true.",
        "seo_title": "Meta Hyperion: Louisiana ratepayers pay $8-13 a month",
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
> [Start here wizard](/start-here.html) will generate
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
        "art": "bills",
        "section": "stories",
        "title": "Five Auctions, \\$29 Billion: How Data Centers Took Over the PJM Capacity Market — and Sent Your Bill to the Moon",
        "seo_title": "PJM capacity auctions: how data centers raised your bill",
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
        "art": "oversight",
        "section": "stories",
        "title": "One Project, Two Stories: How Data Center Developers Shop the Gaps Between Agencies",
        "seo_title": "How data center developers shop the gaps between agencies",
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
        "art": "transmission",
        "section": "stories",
        "title": "DOE Just Named Data Centers the #1 Reason America Needs New Power Lines. Here's Why Your Community Should Read the Fine Print.",
        "seo_title": "DOE: data centers are the #1 reason for new power lines",
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
        "art": "forecast",
        "section": "stories",
        "title": "One in Five Electrons: BNEF Says Data Centers Will Consume 20% of U.S. Power by 2035",
        "seo_title": "BNEF: data centers to use 20% of US power by 2035",
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
        "art": "grid",
        "section": "stories",
        "title": "Amazon Says It Picks Sites Where the Grid Needs Help. Here's What Communities Should Hear.",
        "seo_title": "Amazon's site-selection pitch: what communities should hear",
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
        "art": "land",
        "section": "stories",
        "title": "A \\$15B Data Center Made Wisconsin Farmers Millionaires — and the Same Playbook Is Headed for 10 More Markets",
        "seo_title": "Port Washington's $15B land rush: the data center playbook",
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
        "art": "community",
        "section": "stories",
        "title": "Morgan Stanley Says Community Opposition Is the Biggest Threat to the Data Center Buildout. Are They Right?",
        "seo_title": "Morgan Stanley calls opposition the top data center risk",
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
        "art": "moratorium",
        "section": "stories",
        "title": "New York Just Changed the Game: What EO 62 Means for Every Community Fighting a Data Center",
        "seo_title": "New York EO 62: what it means for data center fights",
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
        "art": "bills",
        "section": "stories",
        "title": "Why Your Electric Bill Is Going Up — and What Data Centers Have to Do With It",
        "seo_title": "Why your electric bill is going up: data centers' role",
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
        "art": "moratorium",
        "section": "stories",
        "title": "The Moratorium Wave: Why 14 States Are Pressing Pause on Data Centers",
        "seo_title": "The moratorium wave: 14 states press pause on data centers",
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
        "art": "water",
        "section": "stories",
        "title": "The Hidden Water Cost of Your AI Query: What the Data Actually Shows",
        "seo_title": "The hidden water cost of an AI query: what the data shows",
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
        "art": "queue",
        "section": "stories",
        "title": "233 GW of Demand Is Waiting in Line: Inside ERCOT's Data Center Queue",
        "seo_title": "ERCOT's data center queue: 233 GW waiting in line",
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
        "art": "community",
        "section": "stories",
        "title": "How the Industry Files Your Protest: 'Social License' and the \\$64B Risk Column",
        "seo_title": "'Social license': how the industry files your protest",
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
        "art": "extraction",
        "section": "stories",
        "title": "They Figured This Out Fifty Years Ago: What Oil, Wind, and Pipeline Towns Already Know About Protecting Neighbors",
        "seo_title": "Oil, wind, pipeline towns: lessons for data center neighbors",
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
    # ── Week in Review ──────────────────────────────────────────────────────
    {
        "id": "week-in-review-2026-08-16",
        "art": "review",
        "section": "stories",
        "title": "Week in Review: Amazon Walks Away, UK Rations Water, and Texas Hits the Brakes",
        "seo_title": "Week in review: Amazon walks away, Texas hits the brakes",
        "date": _dt.date(2026, 8, 16),
        "author": "GridWatch AI",
        "tags": ["week in review", "moratorium", "water", "Texas", "Maryland",
                 "UK", "noise", "community", "policy"],
        "summary": (
            "This week Amazon abandoned a data center campus in Maryland after "
            "community pushback, UK data centers faced water rationing during a "
            "drought, and Texas launched an audit of 300 data center projects. "
            "Plus: Michigan residents sued over noise, Chicago signed an executive "
            "order, and moratorium proposals multiplied from Indiana to San Antonio."
        ),
        "body": """\
Welcome to the first GridWatch AI Week in Review — a Sunday roundup of the
most important data center stories from the past seven days, what they mean
for communities, and what you can learn from each one.

---

### 1. Amazon abandons Calvert County data centers after community pushback

**What happened:** Amazon scrapped plans for a data center campus in
Calvert County, Maryland, citing what it called a changed business
environment. Residents had organized sustained opposition over water use,
noise, and the transformation of agricultural land.

**Why it matters:** This is one of the clearest examples of community
opposition directly influencing a hyperscaler's site-selection decision.
Calvert County isn't a regulatory powerhouse — it's a rural county of about
93,000 people. What residents had was organization, turnout at public
hearings, and specific demands. Amazon didn't lose a lawsuit. It decided the
political cost wasn't worth it.

**The lesson:** Site selection is a business decision. When communities make
a project politically expensive — through organized testimony, media
coverage, and specific conditions — developers will go elsewhere. That's
leverage, and it works even without a moratorium.

*Source: [Capital Gazette, Aug 14](https://www.capitalgazette.com/)*

---

### 2. UK data centers hit with water rationing during drought

**What happened:** Data centers in the United Kingdom were placed under
water-rationing orders as a drought forced regulators to prioritize
residential and agricultural use. The restrictions affected cooling
operations at multiple facilities.

**Why it matters:** This is the first time a major Western economy has
explicitly rationed water *away* from data centers during a drought.
Data centers using evaporative cooling consume roughly
[1.8 liters per kWh](/blog/hidden-water-cost) of electricity — a 100 MW
campus can draw over a million gallons per day. When that competes with
drinking water, regulators face a stark choice.

**What to learn — how data center cooling actually works:**

Most large data centers reject heat one of three ways:

| Method | Water use | Efficiency | Cost |
|--------|-----------|------------|------|
| **Evaporative (wet) cooling** | High — 1.8 L/kWh | Best (PUE 1.1–1.2) | Lowest capex |
| **Air-cooled (dry) cooling** | Near zero | Good (PUE 1.3–1.4) | Higher capex, needs more land |
| **Closed-loop / liquid-to-chip** | Low — recirculates coolant | Excellent (PUE 1.05–1.15) | Highest capex |

Developers default to evaporative cooling because it's cheapest. But "cheapest
for the developer" isn't the same as "cheapest for the community" once you
account for the water those towers consume. When negotiating a CBA, asking
**what cooling technology will be used** is one of the most important
questions — and the answer directly determines your community's water exposure.

*Source: [The Telegraph, Aug 14](https://www.telegraph.co.uk/)*

---

### 3. Texas launches audit of up to 300 data center projects

**What happened:** Following Governor Abbott's executive order, ERCOT
confirmed it will audit up to 300 large-load projects — most of them data
centers — currently in its interconnection queue. The audit could take
months to complete.

**Why it matters:** Texas's grid operator has
[233 GW of large-load requests](/blog/ercot-queue-explainer) waiting in line.
The audit is the state's first attempt to separate real projects from
speculative queue-squatting. Meanwhile, companies including Meta and Amazon
have signed voluntary commitments to Abbott's proposed standards, signaling
the industry would rather negotiate than face legislation.

**What to learn — the interconnection queue, explained:**

Before a data center can draw power from the grid, it files an
**interconnection request** — essentially raising its hand and saying
"I'd like 200 MW at this location." The grid operator studies whether
the transmission system can handle it, what upgrades are needed, and
who pays.

The problem: filing is cheap, and there's no penalty for filing
speculatively. Developers file early to hold their place, even if the
project is years from breaking ground — or may never be built. This clogs
the queue, delays legitimate projects, and forces grid planners to model
a future that will never arrive.

Abbott's audit is asking a simple question: **which of these 300 projects
are real?** That's a question every community with a proposed data center
should be asking too.

*Sources: [Houston Public Media, Aug 15](https://www.houstonpublicmedia.org/);
[fox34.com, Aug 15](https://www.fox34.com/)*

---

### 4. Michigan residents sue data center over noise pollution

**What happened:** Residents near a data center in Michigan filed a lawsuit
alleging persistent noise pollution from cooling equipment. The complaint
describes low-frequency hum and fan noise that disrupts sleep and daily life.

**Why it matters:** Noise is one of the most common complaints about
operational data centers, and one of the hardest to fix after construction.
Cooling fans, backup generators, and HVAC systems run 24/7. The sound
isn't always loud in decibel terms — it's the *constancy* and the
low-frequency character that makes it debilitating.

**What to learn — how to negotiate noise protections *before* a project is
approved:**

1. **Demand a noise study** as part of the site plan review. The developer
   should model expected dBA levels at the nearest property line — not just
   at the facility boundary.

2. **Set a hard limit**, not a guideline. Many communities use 55 dBA during
   the day and 45 dBA at night, measured at the nearest residence.
   Write it into the CBA or zoning conditions with an enforcement mechanism.

3. **Require sound walls and equipment enclosures** as conditions of
   approval, not voluntary commitments. Once the permit is issued, voluntary
   measures evaporate.

4. **Include a complaint-response protocol.** The CBA should specify who
   residents call, how quickly the operator must respond, and what happens
   if readings exceed the limit.

*Source: [bgr.com, Aug 12](https://www.bgr.com/)*

---

### 5. Chicago mayor signs executive order for stricter data center regulations

**What happened:** Mayor Brandon Johnson signed an executive order
establishing new standards for data center development in Chicago,
including stricter noise limits, water-use reporting requirements, and
a community-engagement process for proposed facilities.

**Why it matters:** Chicago is one of the largest cities to use executive
authority — rather than waiting for legislation — to set data center
standards. The order creates a framework that other mayors can replicate
without going through a city council vote.

**The lesson:** Executive orders are faster than ordinances but weaker —
the next mayor can revoke them. If your city's mayor issues an EO, the
next step is to push for a permanent ordinance that codifies the same
protections.

*Sources: [CBS News, Aug 11](https://www.cbsnews.com/);
[ABC7 Chicago, Aug 11](https://abc7chicago.com/)*

---

### 6. Moratorium wave continues: Indiana, San Antonio, Virginia Beach, and more

**What happened this week:**

- **Indianapolis** — City council advanced a data center pause to the
  planning commission for final approval
  ([WFYI, Aug 11](https://www.wfyi.org/))
- **San Antonio** — Councilmember Galvan called for a moratorium on new
  data center construction
  ([San Antonio Report, Aug 10](https://sanantonioreport.org/))
- **Virginia Beach** — City is considering a 12-month pause on new data
  center applications to develop regulations
  ([WTKR, Aug 15](https://www.wtkr.com/))
- **St. Croix County, WI** — Committee sent a moratorium ordinance to the
  county board
  ([Hudson Star Observer, Aug 15](https://www.hudsonstarobserver.com/))
- **Statesville, NC** — City council advanced a 180-day pause on new
  data centers
  ([WSOC TV, Aug 11](https://www.wsoctv.com/))
- **Aurora, CO** — Council rejected a 6-month moratorium but approved new
  regulations and water-use requirements — a reminder that a moratorium
  isn't the only path to protections
  ([Sentinel Colorado, Aug 11](https://www.sentinelcolorado.com/))

**What to learn — the anatomy of a moratorium:**

A moratorium is a **temporary pause**, not a permanent ban. Its purpose is
to give a community time to write the rules before more projects get
approved under inadequate ones. Here's how they typically work:

- **Duration:** Usually 6–18 months. Longer pauses face legal challenges.
- **Scope:** Can cover all new applications, just large facilities
  (>5 MW), or specific zoning districts.
- **Legal basis:** The community's police power to regulate land use.
  Courts generally uphold temporary pauses if they're tied to a stated
  planning purpose (e.g., "to develop zoning standards for high-intensity
  industrial uses").
- **What happens during the pause:** The planning commission drafts new
  standards — noise limits, setbacks, water-use caps, visual screening,
  community-benefit requirements. The moratorium buys time for this work.
- **What doesn't stop:** Projects with already-issued permits typically
  aren't affected. The pause covers *new* applications.

A moratorium is the opening move, not the endgame. The real work is what
the community writes during the pause.

> Track active moratoriums on the
> [Moratorium Tracker](/moratoriums.html) and see what other communities
> have won on the [Start here](/app) tab.

---

### 7. The data center PR blitz is backfiring

**What happened:** Multiple outlets this week noted that the industry's
public-relations campaign — emphasizing jobs and economic development —
is generating more skepticism than support.
[NC Newsline](https://ncnewsline.com/) published an analysis calling the
PR strategy counterproductive; the
[San Antonio Report](https://sanantonioreport.org/) argued residents need
to organize independently of state-level action.

**Why it matters:** The data center industry's standard pitch —
"jobs, tax revenue, innovation" — worked when communities didn't have
information. It's less effective now that residents can look up how many
permanent jobs a data center actually creates (50–150 per facility),
how much water it uses, and what happened to electricity rates in Northern
Virginia. Information asymmetry was the industry's advantage.
**Platforms like this one exist to close that gap.**

*Sources: [NC Newsline, Aug 15](https://ncnewsline.com/);
[San Antonio Report, Aug 15](https://sanantonioreport.org/)*

---

### What to watch next week

- **ERCOT audit timeline** — will the scope narrow under industry pressure?
- **Virginia Beach** — 12-month pause vote expected
- **Congressional hearings** — data center policy continues to surface as
  a midterm issue
- **Water disclosure** — following the UK rationing, pressure for mandatory
  water-use reporting is building in several US states

---

*This is the first of our weekly roundups. Every Sunday we'll cover the
week's most important data center stories, explain the underlying concepts,
and point you to the tools you need. Know a story we should cover? Reach
out through the signup form in the site footer.*
""",
    },
    # ── Negotiation patterns across all 17 operators ──
    {
        "id": "negotiation-patterns-all-operators-2026",
        "art": "negotiation",
        "section": "stories",
        "title": "How to Negotiate with Every Major Data Center Developer: A Strategy Guide",
        "seo_title": "How to negotiate with every major data center developer",
        "date": _dt.date(2026, 8, 18),
        "author": "GridWatch AI",
        "tags": ["negotiation", "concession", "CBA", "strategy", "leverage",
                 "hyperscaler", "colocation", "AI", "community", "analysis"],
        "summary": (
            "We've built negotiation profiles for all 17 major data center "
            "operators — from Google and Amazon to CoreWeave and xAI. Here's "
            "what the patterns reveal: who has actually conceded terms, who "
            "hasn't, and where your leverage really sits."
        ),
        "body": """\
If your community is facing a data center proposal, the single most important
thing to know is: **who are you actually negotiating with?**

That sounds obvious. It isn't. The entity on your rezoning notice is usually
a shell LLC — "Greater Kudu," "Vadata Inc.," "Jet Stream LLC" — and the
company behind it determines what kind of negotiation you're walking into.
A Google campus and a CoreWeave lease inside someone else's building are
fundamentally different fights, even if they draw the same amount of power.

We've now built [negotiation profiles for all 17 major operators](/case-studies.html)
in our tracker — every hyperscaler, every major colocation provider, and the
new wave of AI-native builders. Here's what the data shows.

---

### The uncomfortable headline: almost nobody has conceded anything

Of 17 operators, only five have **any** documented concessions. And of those
five, only the hyperscalers (Google, Meta, Microsoft, Amazon) have given up
terms that communities could point to as wins — and even those come with
serious caveats.

| Tier | Operators | With documented concessions |
|------|-----------|----------------------------|
| Hyperscalers | Google, Meta, Microsoft, Amazon | 4 of 4 |
| AI-native builders | CoreWeave, xAI, Stargate (OpenAI/Oracle) | 0 of 3 |
| Colocation/wholesale | QTS, Digital Realty, Equinix, Vantage, CyrusOne, Aligned, Switch, Stack, EdgeConneX, Core Scientific | 1 of 10 (QTS — and it's a cautionary tale) |

That 1-of-10 for the colo tier is striking. These are the companies building
the **majority** of new data center capacity in the United States. Communities
negotiate with them constantly. And yet we cannot find a single documented
case of a colo operator voluntarily accepting binding community-benefit terms.

That doesn't mean it hasn't happened — it means it hasn't been reported,
recorded, or made public. Which is its own problem.

---

### Three tiers, three different fights

The 17 operators break into three groups, and the negotiation dynamics are
completely different for each.

**Tier 1: Hyperscalers (Google, Meta, Microsoft, Amazon)** — These companies
own and operate their own facilities. They have a public brand to protect,
sustainability reports to defend, and PR teams that care about headlines.
That gives communities two kinds of leverage:

1. **Reputational** — a hyperscaler's own published commitments become the
   floor of your ask. Microsoft has already built zero-water cooling; that
   means "evaporative draw is unavoidable" is no longer available to any
   developer proposing a wet-cooled facility in your town.
2. **Regulatory** — hyperscalers need permits, water allocations, and grid
   interconnections. Every one of those is a choke point.

The concessions they've made follow a pattern: they give up environmental
commitments (water infrastructure, renewable PPAs) more readily than financial
ones. Google paid \\$28.5M toward The Dalles water treatment. Amazon paid
\\$40M over 15 years in Morrow County — but got an estimated \\$1B in
tax abatements in return.

**The lesson:** Read both halves of every deal. A concession that costs the
developer less than the abatement it unlocks is not a community win.

**Tier 2: AI-native builders (CoreWeave, xAI, Stargate)** — These are the
newest and fastest-moving entrants, and they present a completely different
challenge. They have **no documented concessions anywhere**, no
sustainability track record, and in xAI's case, a history of moving faster
than local government can respond.

But they also have the most to lose from delay:

- **CoreWeave** has a \\$12B+ contracted revenue backlog and leases space
  inside partners' buildings. Every month of delay costs real GPU-rental
  revenue. The catch: because CoreWeave is a tenant, the entity on your
  permit may be the landlord (Core Scientific, Digital Realty, Switch), not
  CoreWeave — and the landlord may be less motivated to concede.
- **xAI** built the Memphis Colossus cluster in ~122 days. Speed is its
  entire business model. That makes permitting leverage unusually potent —
  if you exercise it early. Memphis residents learned this the hard way:
  noise, generator exhaust, and unpermitted cooling towers appeared before
  any public meeting.
- **Stargate** carries federal "national infrastructure" branding and
  political cover, but state and local land-use authority still applies.
  The JV structure (OpenAI, Oracle, SoftBank) means the developer on a
  local permit is often Crusoe, Lancium, or Vantage — not OpenAI.

**The lesson:** With AI-native builders, speed is both their advantage and
your leverage. Get conditions on the record before ground is broken, because
once GPUs are racked, the political calculus changes entirely.

**Tier 3: Colocation and wholesale (QTS, Digital Realty, Equinix, etc.)** —
These ten operators build the buildings that everyone else rents. They're
the plumbing of the data center industry, and they are almost completely
invisible to the communities they affect.

The negotiation dynamics are bleak:

- **Private-equity-owned operators** (QTS/Blackstone, CyrusOne/KKR,
  Switch/DigitalBridge, Stack/Blue Owl, Aligned/pending Nvidia-BlackRock)
  have no public brand to protect and no sustainability report to cite back
  at them. You negotiate with a financial sponsor whose metric is IRR, not
  headlines.
- **Public REITs** (Digital Realty, Equinix) are the partial exception —
  institutional investors and ESG ratings create pressure that private
  operators don't face. Equinix's published science-based targets and 96%
  renewable energy coverage are leverage if you can cite them in a permit
  hearing.
- **The QTS cautionary tale** — The only documented colo concession is a
  warning, not a model. QTS added proffers during the contested Prince
  William County Digital Gateway rezoning after 24 hours of public comment.
  Staff said the amendments came too late to evaluate. The rezoning was
  voided on appeal in 2026. **Late proffers are worth nothing.**

**The lesson:** With colo operators, your leverage is almost entirely
structural — you control land-use approvals, utility interconnection
sign-offs, and building permits. Use them. There is no reputational lever
to pull.

---

### Five things every negotiator should know

Across all 17 operators, a few patterns emerge:

**1. Timeline pressure is your best friend.** Every operator — hyperscaler,
AI builder, or colo — is in a race. Data center demand is growing faster
than supply. Every month of delay costs real revenue. This is the single
most universal piece of leverage any community has, and it works regardless
of who the developer is.

**2. Get terms recorded as binding conditions before the vote.** The QTS/Prince
William case is the clearest cautionary example: proffers offered during
deliberation were judged too late to evaluate, and the entire rezoning
was voided. If conditions aren't in writing before the public hearing,
they aren't conditions — they're promises.

**3. Distinguish the operator from the landlord.** In the AI tier especially,
the entity on your permit may not be the company driving the power demand.
CoreWeave leases space from Core Scientific, Digital Realty, and Switch.
Stargate sites are developed by Crusoe, Lancium, and Vantage. You may
need to negotiate with both.

**4. Hold companies to their own published commitments.** Microsoft has
already deployed zero-water cooling. Google funds water infrastructure.
Meta runs watershed restoration. These are not favors — they're precedents.
If the developer in your town proposes less than what their own company
has done elsewhere, say so on the record.

**5. Tax abatements are the hidden cost.** Amazon's \\$40M payment to
Morrow County looks like a win until you learn the abatement it unlocked
was worth an estimated \\$1B. Most colo operators receive abatements as a
matter of course, and most communities don't calculate the net cost.
Before celebrating a payment-in-lieu deal, do the math on what you're
giving up.

---

### What's missing — and how you can help

The biggest gap in this dataset is the colocation tier. Ten major operators,
one documented concession (and it's a failure case). We don't believe
communities have never negotiated terms with Digital Realty, Equinix, or
Vantage — we believe those terms were never made public.

If your community has negotiated binding conditions with any data center
developer, we want to hear about it. Every documented concession makes the
next community's negotiation stronger, because it proves the ask is
realistic.

{{CONCESSION_FORM}}

---

*All 17 operator profiles — including negotiation patterns, documented
concessions, and strategy reads — are available on our
[case studies page](/case-studies.html). The meeting prep generator in the
[negotiation toolkit](/app) pulls from these profiles automatically when
you select an operator.*
""",
    },
    # ── Data center politics go national ───────────────────────────────────
    {
        "id": "data-center-midterms-politics-2026",
        "art": "community",
        "section": "stories",
        "title": "Data Center Opposition Just Became a National Political Force",
        "seo_title": "Data center opposition becomes a national political force",
        "date": _dt.date(2026, 8, 20),
        "author": "GridWatch AI",
        "tags": ["politics", "midterms", "community", "moratorium",
                 "Ohio", "Texas", "Pennsylvania", "Wisconsin", "Wyoming",
                 "Michigan", "New York", "policy", "analysis"],
        "summary": (
            "Axios reports that data center opposition is scrambling the 2026 "
            "midterms. Candidates in both parties are racing to distance "
            "themselves from projects their own leaders spent years courting. "
            "What started as scattered local fights has become a cross-partisan "
            "national movement — and it's changing how elections are won."
        ),
        "body": """\
For two years, community opposition to data centers has been dismissed as
NIMBY noise — localized, emotional, and destined to fade once residents
understood the economic benefits. Today, [Axios
reports](https://www.axios.com/2026/08/20/data-center-uproar-2026-midterms)
that this analysis was dead wrong. Data center opposition is now a defining
issue in the 2026 midterms, and it's rewriting the playbook in both parties.

---

### The political map

The scope is striking. This isn't one swing-state story — it's a
coast-to-coast realignment:

- **Ohio:** Former Sen. Sherrod Brown has spent millions branding Republican
  Sen. Jon Husted as "the face of data centers." The NRSC privately warned AI
  companies that a Husted loss could chill industry support nationwide.
- **Texas:** Gov. Greg Abbott — who once declared Texas "the epicenter of AI
  development" — is now pushing to restrict data centers in rural communities
  and strip away tax incentives after Democrat Gina Hinojosa called the state
  the "wild west of data centers."
- **Pennsylvania:** Gov. Josh Shapiro imposed new guardrails this week after
  Republican challenger Stacy Garrity accused him of "rolling out the red
  carpet" for developers.
- **Wisconsin:** GOP nominee Tom Tiffany is running ads attacking his
  Democratic opponent as "data center David Crowley" — putting a Trump ally
  on the same side as a democratic socialist primary rival.
- **Wyoming:** Republican Chuck Gray won his primary after running ads
  promising to "stop data centers" and calling for a federal ban.
- **Michigan:** Democratic Senate nominee Abdul El-Sayed called for state and
  federal moratoriums days before winning his primary.

This is not a partisan issue. It's a populist one. Candidates on the left
and right are reaching the same conclusion: defending data centers costs
votes.

---

### Why this matters for your community

If you're organizing against a proposed data center, the political ground
just shifted under your feet — in your favor. Here's what changed:

**1. The "jobs and investment" talking point has a counter-message now.**

For years, developers and their political allies have led with economic
benefits. That message is now being turned against incumbents. When Brown
calls Husted "the face of data centers," he's making the economic argument
a liability. The subtext: *those jobs came at your expense.*

**2. Elected officials are scrambling to get on your side.**

Abbott in Texas. Shapiro in Pennsylvania. Hochul in New York. These aren't
insurgent candidates — they're sitting governors reversing their own
positions because the politics changed. When a governor who courted data
center investment starts restricting it, that's a signal to every planning
board and county commission below them.

**3. The industry knows it has a problem — and its response is revealing.**

Axios quotes a Republican operative saying the hyperscalers' comms teams
"don't know how to fight" and are "just used to fluffy ads and corporate
media." The industry's proposed solution is to expand workforce programs,
community funds, and promises to cover infrastructure costs. That's an
important concession — but it's also a list of things communities can
demand in writing, with enforcement mechanisms, before any project breaks
ground.

**4. The ratepayer-protection pledge sets a new floor.**

President Trump's ratepayer-protection pledge — which Google, Microsoft,
Meta, Oracle, xAI, OpenAI, and Amazon have all signed — requires companies
to cover power generation and grid upgrades. That's significant, but a
pledge is not a permit condition. Communities should insist these
commitments appear in binding agreements, not press releases.

---

### What to do with this moment

The Axios piece captures something we've been tracking at GridWatch for
months: the gap between how the industry talks about opposition (as a
communications problem) and what opposition actually is (a political
force). Here's how to use this moment:

**Cite the political cost.** When you testify at a public hearing, you can
now point to specific races where data center support is a losing position.
Abbott reversed course in Texas. Shapiro added guardrails in Pennsylvania.
Gray won a primary on an anti-data-center platform in Wyoming. These are
facts your planning board can't ignore.

**Demand binding conditions, not promises.** The industry is offering
community funds and workforce programs. Good — get them in writing. Use our
[negotiation toolkit](/app) to see what similar communities have won and
generate a meeting brief with specific asks.

**Connect with the national movement.** Your town's fight is no longer
isolated. The [moratorium tracker](/moratoriums.html) now lists over 100
actions across the country. Find communities in similar situations, compare
notes, and share what's working.

**Move before the election.** The window between now and November is when
elected officials are most responsive. If your state legislators, county
commissioners, or city council members haven't taken a public position on
data centers, now is the time to put them on the record.

---

### The bottom line

The industry spent years building bipartisan consensus for the AI buildout.
That consensus is broken. What broke it wasn't an editorial board or a
think tank — it was residents showing up at planning meetings, organizing
on Nextdoor, and telling their elected officials that data centers are a
voting issue.

The political class is now catching up to what communities already knew:
that the costs of data centers — to water, to electric bills, to quality
of life — are real, and that voters will punish anyone who ignores them.

If you're in the middle of a fight, this is validation. If you're just
getting started, this is wind at your back. Use it.

---

*Source: [Axios, "Data center uproar scrambles the midterm election,"
Aug 20, 2026](https://www.axios.com/2026/08/20/data-center-uproar-2026-midterms)*
""",
    },
    # ── Week in Review: 2026-08-23 ──
    {
        "id": "week-in-review-2026-08-23",
        "art": "review",
        "section": "stories",
        "title": "Week in Review: Pennsylvania's Crackdown, New Jersey's Ban Wave, and Nevada Says No to a Dry Basin",
        "seo_title": "Week in review: PA crackdown, NJ ban wave, Nevada says no",
        "date": _dt.date(2026, 8, 23),
        "author": "GridWatch AI",
        "tags": ["week in review", "moratorium", "Pennsylvania", "New Jersey",
                 "Nevada", "Virginia", "Kansas", "Georgia", "Michigan", "water",
                 "policy", "community"],
        "summary": (
            "This week Pennsylvania's governor signed what Bloomberg Law called "
            "the strictest data center executive order in the country, New Jersey "
            "towns kept banning data centers faster than developers could sue over "
            "it, and Nevada regulators banned new data centers outright in an "
            "over-appropriated water basin. Plus: Kansas cities suing their own "
            "residents over ballot petitions, a DeKalb County win, and Michigan's "
            "moratorium fight goes to court."
        ),
        "body": """\
Welcome back to the GridWatch AI Week in Review — our Sunday roundup of the
most important data center stories from the past seven days, what they mean
for communities, and what you can learn from each one.

---

### 1. Pennsylvania's governor signs the "strictest" data center order in the US

**What happened:** Governor Josh Shapiro signed Executive Order 2026-05 on
August 18, creating the **GRID** framework — requiring developers to fund
their own power infrastructure, secure local government approval *before*
any state permit, sign enforceable community benefit agreements, and drop
out of the state's Permit Fast Track program entirely. [NBC News](https://www.nbcnews.com/)
described Shapiro taking a hard line against "predatory" developer
practices; [Bloomberg Law](https://news.bloomberglaw.com/) called it the
strictest data center order in the country.

**Why it matters:** Pennsylvania has been one of the most aggressively
courted states for new data center campuses, thanks to cheap natural gas and
a governor who has otherwise embraced the industry. A governor who campaigned
on data centers as an economic win turning around and requiring local
approval before state permitting is a signal of how far the politics have
shifted in a single year — and it flips the leverage: a town's planning
commission now effectively holds a veto that used to belong entirely to the
state.

**What to learn — what an executive order can and can't do:** An executive
order directs state agencies to change how they operate — it can tighten
permit review, require disclosure of previously confidential contract
terms, and condition tax breaks on compliance, the way GRID does. It
generally can't create binding rate caps through legislation, and it can't
bind a future governor, who can rescind it. GRID's designers built around
that weakness with a consent-order model rather than an outright ban —
details worth reading in full in
[Pennsylvania Just Told Data Centers: Build Your Own Power, or Don't Build Here](/blog/pennsylvania-grid-executive-order-2026).
The follow-up ask for residents is to push legislators to codify the same
protections into statute before the next election changes who's signing
orders. See our analysis of the broader political shift in
[Data Center Opposition Just Became a National Political Force](/blog/data-center-midterms-politics-2026).

*Sources: [WHYY, Aug 18](https://whyy.org/); [NBC News, Aug 18](https://www.nbcnews.com/);
[Bloomberg Law, Aug 18](https://news.bloomberglaw.com/)*

---

### 2. New Jersey's ban wave keeps growing — and a developer wants \\$300 million for it

**What happened:** Jersey City's council voted unanimously to ban new
standalone data centers in the city's industrial zones, joining a growing
list of New Jersey municipalities — including Bayonne and Howell — that
have passed outright bans rather than temporary moratoriums this year. Days
later, [inc.com](https://www.inc.com/) reported that a developer is seeking
\\$300 million in damages from a New Jersey town over its ban.

**Why it matters:** Most of the country is still debating temporary
*moratoriums* — pauses of 6 to 18 months while a town writes new zoning
rules. New Jersey's wave is different: these are permanent zoning bans, not
pauses. That's a stronger tool, but it also invites a stronger legal
response — developers arguing the ban destroys the value of land they
already control or have under contract.

**What to learn — moratorium vs. outright ban, and why developers sue over both:**

| | Moratorium | Zoning ban |
|--|-----------|-----------|
| **Duration** | Temporary (6–18 months) | Permanent, until repealed |
| **Legal basis** | Police power to pause while writing rules | Police power to zone land use |
| **Developer's likely claim** | "You paused my *pending* application" | "You destroyed the value of land I already hold" |
| **Strongest defense for the town** | Tie it to a stated planning purpose | Show the ban applies to a use category, not one project |

A "regulatory takings" lawsuit — the theory behind the \\$300 million claim —
argues a zoning change went so far it amounts to the government seizing the
property without paying for it. Courts set a high bar for these claims, but
towns should expect them any time a ban follows a specific project's
announcement rather than a general policy review. Track the state's growing
list on the [moratorium tracker](/moratoriums.html), and see how other
operators have responded to bans in
[How to Negotiate with Every Major Data Center Developer](/blog/negotiation-patterns-all-operators-2026).

*Sources: [Hudson County View, Aug 20](https://hudsoncountyview.com/);
[inc.com, Aug 21](https://www.inc.com/)*

---

### 3. Nevada bans new data centers in an over-appropriated water basin

**What happened:** Nye County commissioners voted to ban new data centers in
the Pahrump Water Basin, which state regulators have already designated as
over-appropriated — meaning more water rights are on paper than the basin
can actually sustain.

**Why it matters:** This is one of the clearest wins so far for a
resource-based argument, rather than a noise or traffic argument. Nevada's
water law follows prior appropriation ("first in time, first in right"),
and an over-appropriated basin means existing water-rights holders —
farms, wells, small water utilities — are already competing for a shrinking
supply. Adding a data center's cooling demand into that basin isn't a
theoretical risk; it's math the state had already done.

**What to learn — how to find out if your basin is already stressed:**

1. Ask your state's water authority (in Nevada, the Division of Water
   Resources) whether your basin has a designated status — over-appropriated,
   critical management area, or similar.
2. If it does, that status is a stronger legal hook than a general "we're
   worried about water" comment at a hearing — it's the state's own finding.
3. Ask what cooling technology is proposed. Evaporative cooling draws far
   more water than air-cooled or closed-loop systems — see our breakdown in
   last week's issue and in
   [They Figured This Out Fifty Years Ago](/blog/resource-extraction-precedent-2026).

*Sources: [Nevada Current, Aug 20](https://nevadacurrent.com/);
[KSNV, Aug 19](https://news3lv.com/)*

---

### 4. Virginia Beach pauses hyperscale data centers for a year

**What happened:** Virginia Beach's city council approved a 12-month
moratorium on new large-scale data center applications, giving the city time
to write zoning standards. Neighboring Chesapeake moved the same week to
restrict data center development further.

**Why it matters:** Virginia is the most data-center-dense state in the
country, and Hampton Roads has largely been spared the buildout concentrated
in Loudoun and Prince William counties — until now. Two Hampton Roads
cities moving in the same week signals the pattern spreading to a new part
of the state before the facilities are even built, not after residents are
already living with them.

**What to learn — what a moratorium does and doesn't freeze:** A pause
typically applies only to *new* applications filed after the ordinance takes
effect. Projects that already have a complete application on file are often
"grandfathered" and continue under the old rules unless the ordinance
explicitly says otherwise. If your city is about to vote on a pause, ask
your council member directly: does this apply to applications already in
the pipeline, or only future ones? That one sentence in the ordinance
determines whether the pause protects your neighborhood or just the next one.

*Sources: [WTKR, Aug 19](https://www.wtkr.com/);
[The Virginian-Pilot, Aug 19](https://www.pilotonline.com/);
[WHRO, Aug 19](https://whro.org/)*

---

### 5. Kansas cities are suing their own residents over data center ballot petitions

**What happened:** The city of Edgerton, Kansas, sued residents who filed a
petition seeking a public vote on a proposed data center ban, and a similar
fight played out in El Dorado, where a judge ruled the city must either
adopt a data-center ban itself or put the question to voters.

**Why it matters:** Most states give residents the right to force a
ballot referendum on a local ordinance if they collect enough signatures.
A city suing the *petitioners* — rather than simply certifying or rejecting
the petition — is an aggressive move, and it puts the city in the position
of fighting its own residents' right to vote on the issue rather than
fighting the data center developer.

**What to learn — protecting your right to petition:**

- Most states set specific rules for what a petition must contain and how
  many signatures are needed (often a percentage of votes cast in the last
  municipal election). Get those rules from your city clerk *before* you
  circulate anything, in writing.
- If a city challenges your petition's validity, that's a normal legal step.
  A lawsuit specifically aimed at the *organizers*, asking a court to block
  the vote entirely, is a different and more aggressive posture — document
  it and get it in front of local media.
- El Dorado's outcome — a judge ordering the city to either act or let
  voters decide — is the precedent to cite if your city tries to simply
  ignore a valid petition.

*Sources: [Johnson County Post, Aug 18](https://johnsoncountypost.com/);
[KMBC, Aug 21](https://www.kmbc.com/);
[KSN.com, Aug 22](https://www.ksn.com/)*

---

### 6. A Black DeKalb County community wins its year-long fight against a data center

**What happened:** [Capital B News Atlanta](https://atlanta.capitalbnews.org/)
reported that a Black community in DeKalb County, Georgia, successfully
blocked a massive data center project after nearly a year of organizing.
In the same week, Atlanta's city council utilities committee approved
forming a Data Center Task Force to study the industry's local impact.

**Why it matters:** Data center siting in the Southeast has followed a
pattern documented in multiple environmental-justice studies: developers
disproportionately target land near lower-income and majority-Black
communities, where zoning is often lighter and organized political
opposition is assumed to be weaker. DeKalb's win is a direct rebuttal to
that assumption — and a reminder that a sustained, year-long campaign,
not just a single hearing, is often what it takes.

**What to learn — task forces are slower, but they can outlast a single
project fight:** A task force doesn't stop any specific proposal the way a
moratorium does. What it can do is build the data and political cover for
stronger permanent rules — recommending noise limits, water reporting, or
a siting map that keeps future projects away from residential areas. If
your city forms one, push to get a resident or community advocate seated on
it, not just industry and staff representatives. More on organizing for the
long fight in
[How the Industry Files Your Protest](/blog/social-license-risk-2026).

*Sources: [Capital B News Atlanta, Aug 18](https://atlanta.capitalbnews.org/);
[FOX 5 Atlanta, Aug 17](https://www.fox5atlanta.com/)*

---

### 7. Michigan's moratorium fight moves to the courtroom

**What happened:** A data center developer sued the city of Gibraltar,
Michigan, claiming its one-year moratorium unlawfully halted an
already-in-progress project. In the same week, Republican U.S. Senate
candidate Mike Rogers came out in favor of a statewide, one-year data
center moratorium after new data center investments in the state were
revealed.

**Why it matters:** Gibraltar's lawsuit is the sharpest test yet of whether
a moratorium can be applied to a project that was already under review when
the ordinance passed — the same "was this application already in the
pipeline" question raised in the Virginia Beach story above. Meanwhile,
Rogers backing a moratorium shows data center opposition breaking out of
its usual local-politics lane and into a statewide, partisan campaign
message.

**What to learn — a moratorium is more legally durable when it treats every
pending application the same way.** The strongest legal defense for a town
being sued over a moratorium is consistency: applying the pause to every
project in a category, not carving out exceptions, and documenting the
planning purpose (drafting zoning standards) in the ordinance itself.
Singling out one already-filed project for a "pause" is what invites — and
sometimes wins — a lawsuit like Gibraltar's.

*Sources: [WXYZ Channel 7, Aug 20](https://www.wxyz.com/);
[Michigan Advance, Aug 20](https://michiganadvance.com/)*

---

### What to watch next week

- **Gibraltar, Michigan** — how the court rules on whether the moratorium
  can apply to an already-filed application
- **El Dorado, Kansas** — whether the city adopts a ban itself or the
  question goes to voters
- **Pennsylvania's legislature** — whether lawmakers move to codify
  Shapiro's executive order into statute before it can be reversed by a
  future governor
- **More New Jersey towns** — additional council votes are queued up
  following Jersey City's ban

---

*Every Sunday we cover the week's most important data center stories,
explain the underlying concepts, and point you to the tools you need. Know
a story we should cover? Reach out through the signup form in the site
footer.*
""",
    },
    {
        "id": "week-in-review-2026-08-30",
        "art": "review",
        "section": "stories",
        "title": "Week in Review: Georgia's Secret OpenAI Contract, New Jersey's New Transparency Law, and a Second California City Bans Data Centers",
        "seo_title": "Week in review: Georgia's OpenAI secret, a second CA ban",
        "date": _dt.date(2026, 8, 30),
        "author": "GridWatch AI",
        "tags": ["week in review", "moratorium", "Georgia", "New Jersey",
                 "California", "Texas", "PJM", "water", "policy",
                 "transparency", "community"],
        "summary": (
            "This week Georgia regulators approved a confidential 3.2-gigawatt "
            "contract to power OpenAI's \\$20 billion Effingham County data "
            "center and Sen. Warnock answered with a call for a statewide "
            "moratorium, New Jersey's governor signed a law forcing data "
            "centers to report their water and energy use, and Coachella "
            "became the second California city to ban data centers outright. "
            "Plus: a Microsoft-tied New Jersey site accused of running dozens "
            "of unpermitted gas turbines, PJM's plan to make data centers "
            "bring their own power, and ten more communities that paused or "
            "banned data centers in a single week."
        ),
        "body": """\
Welcome back to the GridWatch AI Week in Review — our Sunday roundup of the
most important data center stories from the past seven days, what they mean
for communities, and what you can learn from each one.

---

### 1. Georgia regulators approve OpenAI's \\$20B power contract — and Warnock answers with a call for a statewide moratorium

**What happened:** Georgia's Public Service Commission approved Georgia
Power's 3.2-gigawatt contract to supply [OpenAI's](https://openai.com/)
roughly \\$20 billion data center in Effingham County on August 27, after
commissioners extended their review timeline once already under public
pressure and added ratepayer-protection provisions before signing off
([thecurrentga.org](https://thecurrentga.org/) called it "PSC boosts
safeguards"). Georgia Power says the contract is part of a larger portfolio
of large-load deals that will save residential customers about \\$950
million a year starting in 2029 — a claim [CleanTechnica](https://cleantechnica.com/)
covered skeptically as "Georgia PSC Approves Secret OpenAI Contract,"
because the underlying contract terms were filed with regulators
confidentially. The next day, Sen. Raphael Warnock visited the future
Effingham County site and called for a statewide data center moratorium,
accusing OpenAI and Georgia Power of striking the deal "in the dark."

**Why it matters:** This is the same pattern GridWatch AI has flagged in
Louisiana, Ohio, and elsewhere: a utility asks its state regulator to
approve a multibillion-dollar contract to serve one customer, the regulator
signs off with the *company's own* savings estimate as the headline number,
and the terms that would let anyone check that estimate stay under seal.
Georgia's PSC did add safeguards this time — but "safeguards were added"
and "the public can verify the number" are two different things, and only
one of them happened here.

**What to learn — how to ask for the number behind the number:** A PSC or
PUC docket is a public record, even when specific contract exhibits are
filed confidentially. You can:

1. Look up your state's docket for the case (Georgia's is searchable
   through the PSC's own site) and read the *order* — commissioners
   usually have to explain, in writing, why they found a proposed rate or
   contract "just and reasonable," even when the underlying numbers are
   redacted.
2. Ask whether an independent consumer advocate's office (most states have
   one) intervened in the case — their filings are often less redacted
   than the utility's.
3. Compare the claimed savings to your own bill category. A statewide
   "$950 million" figure sounds large; divided across millions of
   ratepayers it may be a few dollars a month — see our breakdown of how
   utility bills actually work in
   [Why Your Electric Bill Is Going Up — and What Data Centers Have to Do
   With It](/blog/utility-bill-explainer-2026). Georgia's own PUC contact
   and docket links are on our [PUC directory](/puc.html).

*Sources: [AJC, Aug 27](https://www.ajc.com/); [CleanTechnica, Aug 28](https://cleantechnica.com/);
[thecurrentga.org, Aug 27](https://thecurrentga.org/); [CBS News, Aug 28](https://www.cbsnews.com/)*

---

### 2. New Jersey makes data centers report their water and energy use — and ends a \\$250 million tax break

**What happened:** Gov. Mikie Sherrill signed a package of bills into law,
including one requiring data centers to report their energy and water
usage to the state Board of Public Utilities, and a bipartisan bill from
Assemblyman Macurdy ending roughly \\$250 million in state tax credits for
AI data centers. In the same week, East Brunswick formally banned data
centers across its commercial, business, and industrial zones, and Jackson
Township voted to ban them as well — both joining a growing list of New
Jersey towns that have moved from moratoriums to permanent bans this year.

**Why it matters:** New Jersey is now running two tracks at once: towns are
banning specific projects locally, while the state is building the
disclosure and tax infrastructure to hold *every* data center in the state
accountable, not just the ones a town happens to catch. A reporting mandate
doesn't stop a project the way a ban does — but it creates a public record
of exactly how much water and power a facility uses, which is the evidence
residents need for the *next* fight.

**What to learn — disclosure laws are a different tool than bans, and they
compound over time:** A mandatory reporting law only works if someone
actually pulls the reports once they're filed. Once New Jersey's BPU starts
collecting this data, expect it to become public record — mark your
calendar to request it, the way advocates already do with New Jersey's
[hidden water costs](/blog/hidden-water-cost). Pair a reporting requirement
with a request in your own town's community benefit agreement for the same
disclosure at the local level — see the model clauses on
[cba-clauses.html](/cba-clauses.html), and how tax breaks like the one New
Jersey just ended got scrutinized nationally in
[The \\$327 Million Guess That Became \\$2.5 Billion](/blog/data-center-tax-break-blowouts-2026).

*Sources: [NJ.com, Aug 27](https://www.nj.com/); [NJBIZ, Aug 28](https://njbiz.com/);
[TAPinto, Aug 28](https://www.tapinto.net/); [Bloomberg Law, Aug 27](https://news.bloomberglaw.com/)*

---

### 3. A Microsoft-tied New Jersey data center is accused of running dozens of unpermitted gas turbines

**What happened:** A large AI data center under construction in Vineland,
New Jersey — built by Nebius, with Microsoft as a tenant, and already hit
with a stop-construction order earlier this month over unpermitted fuel
cells — is now accused of operating dozens of natural gas turbines
([Tom's Hardware](https://www.tomshardware.com/) reported 62) and a
1.5-million-gallon liquefied natural gas storage tank without the required
permits. [The Guardian](https://www.theguardian.com/) and
[WHYY](https://whyy.org/) reported that community and environmental groups
are demanding Microsoft halt operations at the roughly \\$19.4 billion
facility, which sits near the Philadelphia metro area, and
[Common Dreams](https://www.commondreams.org/) published an investigation
describing an "army" of unpermitted generators on site.

**Why it matters:** Backup and bridge power at data centers — the gas
turbines and generators that keep a facility running before it has a full
grid interconnection — almost always require their own air permits,
separate from the construction permit for the building itself. When a
developer runs that equipment before the permits are issued, it's usually
because waiting for the permit would have delayed opening the facility, not
because the equipment is exempt from needing one.

**What to learn — how to check whether a facility near you actually has
its permits:** Don't take a company's word that a project is "fully
permitted." Your state environmental agency's air-permit database (or, if
none exists, a public records request) will show what's actually been
issued and for what equipment. GridWatch AI's own
[project paper-trail tool](/projects.html#records) walks through where to
look state by state. And this is exactly the kind of gap a developer can
exploit when a project touches multiple agencies — see
[One Project, Two Stories: How Data Center Developers Shop the Gaps Between
Agencies](/blog/oversight-gaps-agency-shopping-2026).

*Sources: [The Guardian, Aug 27](https://www.theguardian.com/);
[WHYY, Aug 28](https://whyy.org/); [Tom's Hardware, Aug 29](https://www.tomshardware.com/);
[Common Dreams, Aug 27](https://www.commondreams.org/)*

---

### 4. Coachella becomes the second California city to ban data centers outright

**What happened:** Coachella's city council voted unanimously on August 26
to adopt Ordinance No. 1231, a permanent ban on large-scale data centers in
all zoning districts, replacing a 45-day moratorium the city had adopted in
June alongside terminating its agreement with a developer over a
400-plus-acre, six-data-center campus. Coachella is the second California
city to ban data centers outright, after Monterey Park, and the first in
the Coachella Valley; the mayor has asked staff to explore a ballot measure
to entrench the ban further. The same week, Escondido's city council
approved its own moratorium, and a Fresno councilmember introduced a
proposal for a citywide prohibition.

**Why it matters:** California's fights are increasingly about
*permanence*. A moratorium buys a town time to write rules; an outright
zoning ban, like Coachella's, is meant to be the rule. Exploring a ballot
measure on top of that is a step further still — it's a town trying to
make its own ban harder for a *future* council to undo.

**What to learn — why some towns take a ban to the ballot box:** A city
council that passes an ordinance by a simple majority vote can just as
easily repeal it by a simple majority vote of a differently composed
council two years later. A ballot measure approved directly by voters
typically requires another vote of the people (and sometimes a
supermajority) to undo — making it a stronger, harder-to-reverse form of
the same ban. It's slower and costs more to run, which is why most towns
start with a council ordinance and only take the ballot-measure route once
they're confident the ban has lasting public support. Track every locality
on the [moratorium tracker](/moratoriums.html).

*Sources: [kvcrnews.org, Aug 28](https://www.kvcrnews.org/);
[10News, Aug 24](https://www.10news.com/); [Fresnoland, Aug 29](https://fresnoland.org/)*

---

### 5. Texas's data center "pause" faces its first real scrutiny — and a bot study undercuts one excuse

**What happened:** Gov. Greg Abbott told [Business Insider](https://www.businessinsider.com/)
this week that Chinese bots are not behind the backlash against Texas data
centers, after a researcher found that many of the accounts flagged as
part of a Chinese influence campaign had no followers or engagement at
all. Meanwhile [Texas Public Radio](https://www.tpr.org/) and
[Houston Public Media](https://www.houstonpublicmedia.org/) both published
pieces this week asking, plainly, whether Abbott's audit-and-pause of up to
1,800 data center interconnection requests will actually change anything —
noting it still has no firm completion date and no enforcement mechanism
beyond delaying ERCOT interconnection review. The Washington Post reported
a prominent Texas Republican now predicts the party will lose seats over
the issue.

**Why it matters:** Last week we covered Pennsylvania's executive order
requiring developers to fund their own power infrastructure before getting
a state permit. Texas's "pause" looks similar on the surface but is
weaker: it's a directive to two agencies (ERCOT and the PUCT) to slow-walk
interconnection reviews while they audit, not a new permitting requirement
written into law. Nothing in it stops a future governor — or this one,
after the audit ends — from waving projects through unchanged.

**What to learn — separating a real pause from a stalling tactic:** Ask
three questions about any government "pause" on data center approvals:
(1) Is there a **statutory or regulatory basis** for it, or is it purely a
directive that could be reversed by the next phone call? (2) Is there a
**published end date or trigger** for when the pause lifts? (3) What
happens to projects **already in the queue** when it does? Texas's answer
to all three is currently "unclear," which is different from Nevada's
water-basin ban or Coachella's ordinance above, both of which rest on a
specific legal finding. For background on what's actually backed up in the
queue Abbott paused, see
[233 GW of Demand Is Waiting in Line: Inside ERCOT's Data Center Queue](/blog/ercot-queue-explainer)
and [Texas Just Froze 474 GW of Data Center Interconnections. Here's What
It Means.](/blog/texas-ercot-queue-freeze-2026)

*Sources: [Business Insider, Aug 29](https://www.businessinsider.com/);
[Texas Public Radio, Aug 28](https://www.tpr.org/);
[Houston Public Media, Aug 27](https://www.houstonpublicmedia.org/);
[The Washington Post, Aug 29](https://www.washingtonpost.com/)*

---

### 6. PJM wants new data centers to bring their own power — or get curtailed first

**What happened:** Grid operator PJM, which serves 13 states plus D.C.,
proposed new rules that would require large new data centers to either
bring their own dedicated generation or agree to be curtailed first when
the shared grid is under stress, rather than drawing on the grid at full
capacity by default the way existing customers do. The proposal follows a
report from PJM's own independent market monitor that data center load
made up roughly 9% of PJM's wholesale electricity costs so far in 2026.

**Why it matters:** This is the same idea behind Pennsylvania's executive
order and Georgia Power's large-load tariffs — new data center demand
shouldn't get to draw on infrastructure that existing residential
ratepayers already paid to build — but PJM is proposing to apply it at the
grid-operator level, across its entire multi-state footprint, rather than
state by state.

**What to learn — what "bring your own power" actually means:** Instead of
getting the same priority grid access as an existing factory or
neighborhood, a large new load under this kind of rule either (a) builds
or contracts for generation that matches its own draw, so it isn't relying
on the shared grid at peak, or (b) accepts that it will be the first thing
curtailed — cut off, temporarily — when supply gets tight, before any
residential circuit is touched. It doesn't ban data centers or cap their
growth; it changes who bears the risk when the grid is stressed. For more
on how data center load has already pushed up PJM capacity prices, see
[Five Auctions, \\$29 Billion: How Data Centers Took Over the PJM Capacity
Market](/blog/pjm-capacity-auction-ratepayer-shock-2026).

*Sources: [Utility Dive, Aug 27](https://www.utilitydive.com/);
[Virginia Mercury, Aug 27](https://virginiamercury.com/);
[WWBT/NBC12, Aug 27](https://www.nbc12.com/)*

---

### 7. Ten more communities paused or banned data centers this week

Beyond the stories above, at least ten more local governments moved on
data centers in the past seven days:

| Locality | State | Action | Duration / scope |
|--|--|--|--|
| Carlton County | MN | Moratorium, unanimous | 1 year |
| Elkhart | IN | Moratorium (data centers + battery storage), unanimous | Until new ordinance |
| Cary | NC | Moratorium, unanimous | 18 months |
| Savannah | GA | Moratorium | 155 days |
| Palm Beach County | FL | Moratorium, initial approval | 1 year |
| Nehawka | NE | Ban (village-level) | Standing |
| Harford County | MD | Ban — first county in Maryland to ban data centers | Standing |
| Pierce County | WA | Ban, unincorporated areas only | 1 year |
| Isanti | MN | Moratorium extended | 1 year |
| Lancaster County | NE | Moratorium introduced | Not yet voted |

**What to learn — check whether a ban covers your address, not just your
county:** Pierce County's ban, like several others this year, applies only
to *unincorporated* areas — land outside any city or town's own boundary.
If you live inside an incorporated city within a county that just passed a
ban, that county's ordinance may not cover your street at all; you'd need
your city council to pass its own. Always ask your local clerk which map
the ordinance actually applies to before you tell your neighbors it
protects them.

*Sources: [fox21online.com, Aug 25](https://www.fox21online.com/) (Carlton County);
[WSBT, Aug 28](https://www.wsbt.com/) (Elkhart); [WRAL, Aug 28](https://www.wral.com/) (Cary);
[WTOC, Aug 28](https://www.wtoc.com/) (Savannah); [WPTV, Aug 28](https://www.wptv.com/) (Palm Beach County);
[KETV, Aug 28](https://www.ketv.com/) (Nehawka); [Inside Towers, Aug 28](https://www.insidetowers.com/) (Harford County);
[The News Tribune, Aug 27](https://www.thenewstribune.com/) (Pierce County);
[isanti-chisagocountystar.com, Aug 27](https://www.isanti-chisagocountystar.com/) (Isanti);
[Nebraska Public Media, Aug 27](https://nebraskapublicmedia.org/) (Lancaster County)*

---

### What to watch next week

- **Palm Beach County, FL** — whether commissioners give final approval to
  the one-year moratorium after this week's initial vote
- **Fresno, CA** — whether the full council takes up the citywide ban
  proposal
- **Coachella, CA** — whether the mayor's proposed ballot measure to
  entrench the data center ban moves forward
- **Texas** — whether Abbott's audit gets a firm completion date, or
  legislators call the special session Democrats have requested
- **Vineland, NJ** — how state and local regulators respond to the
  unpermitted-turbine allegations at the Nebius/Microsoft site

---

*Every Sunday we cover the week's most important data center stories,
explain the underlying concepts, and point you to the tools you need. Know
a story we should cover? Reach out at hello@aigridwatch.com or sign up for
the newsletter below.*
""",
    },
]
