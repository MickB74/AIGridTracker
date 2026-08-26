"""
2026 U.S. Senate races — where each candidate stands on AI data centers.

Why this exists
---------------
Data centers became a Senate campaign issue in 2026. Residents fighting a
project locally keep asking the same question at the federal level: does the
person on my ballot want data centers to pay their own way, or not? This
module is the answer, one race at a time, with the receipts.

Sourcing discipline (same as MORATORIUMS_DF / LOCAL_BODIES_DF)
--------------------------------------------------------------
* **The roster is primary-sourced.** Every race's `roster_source` points at the
  state election authority's own certified candidate list — not a wire
  round-up, not an encyclopedia. Who is on the ballot is a fact the state
  publishes, so that is where it is read from.
* **Every record item carries its own `source` URL and `date`.** A candidate's
  position is a claim, and a resident may repeat it at a hearing or in a
  letter, so it ships with the link that backs it.
* **Silence is disclosed, never scored.** A candidate with no documented
  data-center record gets `lean="unrecorded"` and renders as *No documented
  record found* — not as "neutral", and not as a bad grade. Most candidates
  in most races are here. That gap is the honest state of the record, and the
  page says so.
* **`lean` is a summary of the cited items, not a rating of the candidate.**
  It is derived from what the sources below actually show, on one axis only:
  whether the candidate's documented position makes data centers carry their
  own costs and gives host communities a say.

Deliberately NOT graded A–F like src/official_grades.py. That scorecard grades
sitting officials on roll-call votes and signed laws. Most people here are
challengers whose entire record is a campaign statement, which is much weaker
evidence — a press release is a promise, not an action, and the page should
not launder one into the other.
"""

import json
import pathlib

ROSTER_AS_OF = "2026-08-25"
ELECTION_DATE = "2026-11-03"

# ── lean vocabulary ────────────────────────────────────────────────────────
# Ordered strongest-protection first. `unrecorded` is not a position on this
# axis at all — it means nobody has found a documented statement or action.
LEANS = {
    "guardrails": (
        "Guardrails",
        "Documented support for making data centers carry their own costs, "
        "for community say over siting, or for a pause.",
        "#22c55e"),
    "mixed": (
        "Mixed",
        "Documented on both sides — courts the buildout but backs some "
        "ratepayer or community protection.",
        "#f59e0b"),
    "accelerate": (
        "Accelerate",
        "Documented emphasis on building faster — competitiveness, "
        "incentives, or siting help — without a matching cost or community "
        "safeguard on the record.",
        "#ef4444"),
    "unrecorded": (
        "No record found",
        "No documented statement or action on data centers located. Not "
        "scored — the gap is disclosed, not punished.",
        "#64748b"),
}

LEAN_NOTE = (
    "“Lean” summarises only the cited items below it, on one axis: "
    "does this candidate's documented position make data centers pay their own "
    "way and give the host community a say? It is not an overall rating, not a "
    "grade, and not an endorsement. Candidates with no located record are left "
    "unscored."
)

# ── the record ─────────────────────────────────────────────────────────────
# Key: (state postal, lowercase last-name token) -> record dict.
#   summary : one sentence, plain language, no adjectives the sources don't support
#   lean    : key into LEANS
#   items   : list of {what, date (ISO or ""), source (URL)}
#   as_of   : date this entry was last read. Never invent one.
AI_RECORDS = {
    # ── Texas — the race where this became the defining issue ─────────────
    ("TX", "James Talarico"): {
        "lean": "guardrails",
        "summary": "Ran on a “Hold Data Centers Accountable” plan: end "
                   "the state sales-tax break, require closed-loop cooling, and "
                   "let communities decide whether a project comes in.",
        "items": [
            {"what": "Released a data-center plan calling to end Texas sales-tax "
                     "incentives for data centers, set federal minimum standards "
                     "for grid, environment and jobs, require closed-loop cooling "
                     "to cut water use, and empower localities to approve or "
                     "reject projects.",
             "date": "2026-07-22",
             "source": "https://www.texastribune.org/2026/07/22/texas-james-talarico-data-centers-regulation-senate-2026/"},
        ],
        "as_of": "2026-08-25",
    },
    ("TX", "Ken Paxton"): {
        "lean": "mixed",
        "summary": "Called the issue “complicated” and stressed competing "
                   "with China, then released a “Texas First” plan built "
                   "on Chinese-technology bans and child-safety liability rather "
                   "than on ratepayer cost allocation.",
        "items": [
            {"what": "Released a four-point “Texas First Data Center Plan”: "
                     "bar Chinese technology from powering American data centers, "
                     "hold operators criminally liable where a center powers AI "
                     "chatbots that endanger children, and co-sponsor Sen. Tom "
                     "Cotton's DATA Act.",
             "date": "2026-08-24",
             "source": "https://thehill.com/policy/technology/6049559-ken-paxton-texas-senate-ai-data-center-plan/"},
            {"what": "Reported to have taken roughly $400,000 from data-center-"
                     "connected donors; as attorney general, declined requests to "
                     "act against local data-center development.",
             "date": "2026-08-24",
             "source": "https://www.washingtonpost.com/nation/2026/08/24/ken-paxton-unveils-anti-data-center-plan-gop-voter-anger-mounts-texas/"},
        ],
        "as_of": "2026-08-25",
    },

    # ── Ohio (special) ────────────────────────────────────────────────────
    ("OH", "Sherrod Brown"): {
        "lean": "guardrails",
        "summary": "Made data centers a central campaign theme, running ads "
                   "against his opponent's record on developer tax breaks and "
                   "promising to make data centers pay the full cost of the "
                   "electricity they use.",
        "items": [
            {"what": "Ran two July ads attacking Husted's record supporting tax "
                     "breaks for data-center developers, and pledged to make data "
                     "centers pay the full cost of their electricity use.",
             "date": "2026-08-10",
             "source": "https://ohiocapitaljournal.com/2026/08/10/ohio-u-s-senate-candidates-offer-contrasting-visions-for-data-centers/"},
        ],
        "as_of": "2026-08-25",
    },
    ("OH", "Jon Husted"): {
        "lean": "mixed",
        "summary": "Frames AI buildout as a national-security necessity, and "
                   "introduced a bill directing states to make 100 MW+ loads "
                   "cover their own infrastructure costs.",
        "items": [
            {"what": "Introduced the Ratepayer Protection Act: standards for "
                     "states and PUCs connecting 100 MW+ loads, requiring "
                     "large-load customers to recover full incremental upgrade "
                     "costs and post financial assurances so utilities cannot "
                     "shift them to households. “We must do that without "
                     "passing the costs on to working families and small "
                     "businesses.”",
             "date": "2026-07-20",
             "source": "https://www.husted.senate.gov/media/press-releases/husted-leads-bill-to-protect-americans-from-footing-the-bill-for-new-data-centers/"},
            {"what": "Bill introduced the day after Brown's first attack ad aired; "
                     "reported to have taken roughly $69,750 from tech and energy "
                     "PACs and employees including Google, Amazon, Microsoft, "
                     "Oracle, AEP, Duke Energy and Vistra.",
             "date": "2026-08-21",
             "source": "https://ohiocapitaljournal.com/2026/08/21/leaked-memo-about-data-centers-shows-gop-worried-about-ohios-u-s-senate-race/"},
        ],
        "as_of": "2026-08-25",
    },

    # ── Michigan ──────────────────────────────────────────────────────────
    ("MI", "Abdul El-Sayed"): {
        "lean": "guardrails",
        "summary": "Published “terms of engagement” for data centers: "
                   "zero rate hikes, closed-loop cooling, no weakening of the "
                   "state's clean-energy law, and penalties for noncompliance.",
        "items": [
            {"what": "Released a framework requiring developers to guarantee no "
                     "utility rate increases, protect water and grid reliability, "
                     "bar utilities from citing data-center demand to weaken "
                     "Michigan clean-energy law, and attach clear penalties to "
                     "every commitment.",
             "date": "2026-01",
             "source": "https://planetdetroit.org/2026/01/el-sayed-data-centers-senate/"},
        ],
        "as_of": "2026-08-25",
    },
    ("MI", "Mike Rogers"): {
        "lean": "mixed",
        "summary": "Backed state and local control, then endorsed a one-year "
                   "statewide moratorium days after his AI-sector investments "
                   "were reported.",
        "items": [
            {"what": "Endorsed a one-year Michigan moratorium on new data-center "
                     "development, citing community control, utility price hikes, "
                     "water, and “pay-to-play schemes” — a state "
                     "pause, not a national ban.",
             "date": "2026-08-20",
             "source": "https://www.detroitnews.com/story/news/politics/2026/08/20/data-center-politics-michigan-senate-mike-rogers-abdul-el-sayed/91385736007/"},
            {"what": "Shift came days after reporting that he holds millions in "
                     "tech investments that stand to benefit from the data-center "
                     "buildout; his campaign would not say whether he would "
                     "divest.",
             "date": "2026-08-20",
             "source": "https://michiganadvance.com/2026/08/20/after-data-center-investments-revealed-rogers-backs-statewide-moratorium/"},
        ],
        "as_of": "2026-08-25",
    },

    # ── Georgia ───────────────────────────────────────────────────────────
    ("GA", "Jon Ossoff"): {
        "lean": "guardrails",
        "summary": "Asked FERC to examine what AI server load is doing to power "
                   "bills.",
        "items": [
            {"what": "Sent a letter to FERC probing the impact of AI servers on "
                     "electricity bills.",
             "date": "2026-04",
             "source": "https://www.newsweek.com/ai-data-center-war-where-democrats-republicans-in-key-senate-races-stand-12354265"},
        ],
        "as_of": "2026-08-25",
    },
    ("GA", "Mike Collins"): {
        "lean": "mixed",
        "summary": "Names data centers a priority issue and argues local leaders "
                   "should decide siting, while backing a federal role because "
                   "“we're in a race with China for AI.”",
        "items": [
            {"what": "Campaigning on data centers: says Georgia's 200+ data "
                     "centers matter but local leaders should decide whether one "
                     "fits their community — “if a data center goes into "
                     "a local community and destroys the infrastructure, you "
                     "didn't do good” — while allowing a federal role "
                     "given AI competition with China. Meta operates a large "
                     "campus in his House district.",
             "date": "2026",
             "source": "https://www.local3news.com/local-news/decision-2026-u-s-senate-candidate-mike-collins-makes-campaign-stop-in-dalton/article_7ca14bf8-2e99-40a6-acc6-6dfd684a1f0e.html"},
        ],
        "as_of": "2026-08-25",
    },

    # ── Virginia ──────────────────────────────────────────────────────────
    ("VA", "Mark Warner"): {
        "lean": "guardrails",
        "summary": "Sponsored federal legislation to stop data-center costs "
                   "landing on Virginia ratepayers, and would tie tax benefits to "
                   "water- and energy-use disclosure.",
        "items": [
            {"what": "Sponsored the Power for the People Act: directs states to "
                     "consider new data-center rate classes, seeks a FERC rule "
                     "making data centers pay for the transmission upgrades they "
                     "require, and raises accountability for local grid "
                     "infrastructure.",
             "date": "2026-06-03",
             "source": "https://www.warner.senate.gov/newsroom/press-releases/warner-sponsors-bill-to-ensure-virginians-arent-stuck-footing-the-bill-for-big-data-centers/"},
            {"what": "Introduced further bills tying certain deferred tax "
                     "benefits to disclosure of water and energy use and "
                     "compliance with related standards.",
             "date": "2026-07-22",
             "source": "https://www.arlnow.com/2026/07/22/sen-warner-targets-data-centers-energy-usage-economic-impacts-of-ai-in-new-bills/"},
        ],
        "as_of": "2026-08-25",
    },

    # ── New Jersey ────────────────────────────────────────────────────────
    ("NJ", "Cory Booker"): {
        "lean": "guardrails",
        "summary": "Original cosponsor of the Power for the People Act, the "
                   "Senate's main data-center cost-allocation bill.",
        "items": [
            {"what": "Cosponsored the Power for the People Act (Van Hollen, "
                     "introduced Jan 15 2026): new data-center rate classes, a "
                     "FERC rule making data centers pay for local transmission "
                     "upgrades, interconnection incentives to bring their own "
                     "generation and storage, and prevailing-wage standards.",
             "date": "2026-01-15",
             "source": "https://www.booker.senate.gov/news/press/booker-van-hollen-colleagues-introduce-legislation-to-ensure-americans-arent-footing-the-bill-for-big-data-centers"},
        ],
        "as_of": "2026-08-25",
    },

    # ── North Carolina ────────────────────────────────────────────────────
    ("NC", "Michael Whatley"): {
        "lean": "accelerate",
        "summary": "Called data-center opposition “not organic” and "
                   "backs tax breaks for developers; reported to hold stock in "
                   "data-center companies.",
        "items": [
            {"what": "Told a Fox News interview that “this opposition to data "
                     "centers is not organic”, and agreed governments should "
                     "offer developers tax breaks, though not subsidies, to "
                     "encourage expansion.",
             "date": "2026-07",
             "source": "https://www.newsweek.com/ai-data-center-war-where-democrats-republicans-in-key-senate-races-stand-12354265"},
            {"what": "Reported by NBC News to back data-center tax breaks while "
                     "owning stock in data-center companies.",
             "date": "2026",
             "source": "https://www.ncdp.org/media/new-from-nbc-news-michael-whatley-backs-tax-breaks-for-data-centers-while-owning-stock-in-data-center-companies/"},
        ],
        "as_of": "2026-08-25",
    },

    # ── Maine ─────────────────────────────────────────────────────────────
    ("ME", "Troy Jackson"): {
        "lean": "guardrails",
        "summary": "Would require data centers to cover their own power costs, "
                   "pay fair taxes, use union labour and engage the host "
                   "community.",
        "items": [
            {"what": "Set conditions for data centers: good-paying union jobs, "
                     "fair tax payment, environmental protection, local community "
                     "engagement, and covering their own power costs.",
             "date": "2026",
             "source": "https://www.newsweek.com/ai-data-center-war-where-democrats-republicans-in-key-senate-races-stand-12354265"},
        ],
        "as_of": "2026-08-25",
    },
    ("ME", "Susan Collins"): {
        "lean": "mixed",
        "summary": "Says she shares concerns about data-center energy use and "
                   "cost pressure, while attributing Maine's rate increases to "
                   "state Democratic leadership.",
        "items": [
            {"what": "Voiced concern about data-center energy consumption and "
                     "cost pressure and toured redevelopment sites with Energy "
                     "Secretary Chris Wright, while blaming rising rates on "
                     "Democratic state leaders.",
             "date": "2026",
             "source": "https://www.newsweek.com/ai-data-center-war-where-democrats-republicans-in-key-senate-races-stand-12354265"},
        ],
        "as_of": "2026-08-25",
    },

    # ── Iowa ──────────────────────────────────────────────────────────────
    ("IA", "Josh Turek"): {
        "lean": "mixed",
        "summary": "Campaigns against “billionaires and large corporations” "
                   "and has echoed local moratorium sentiment, without a published "
                   "data-center platform.",
        "items": [
            {"what": "Framed his campaign around opposing billionaires and large "
                     "corporations and embraced local moratorium sentiment; no "
                     "detailed data-center platform published.",
             "date": "2026",
             "source": "https://www.newsweek.com/ai-data-center-war-where-democrats-republicans-in-key-senate-races-stand-12354265"},
        ],
        "as_of": "2026-08-25",
    },
    ("IA", "Ashley Hinson"): {
        "lean": "accelerate",
        "summary": "Emphasises American AI leadership against China; no "
                   "data-center cost or siting restriction located on the record.",
        "items": [
            {"what": "Emphasised American AI leadership and competition with "
                     "China; no specific data-center restrictions stated.",
             "date": "2026",
             "source": "https://www.newsweek.com/ai-data-center-war-where-democrats-republicans-in-key-senate-races-stand-12354265"},
        ],
        "as_of": "2026-08-25",
    },

    # ── Alaska ────────────────────────────────────────────────────────────
    ("AK", "Dan S. Sullivan"): {
        "lean": "accelerate",
        "summary": "Pushed to site data centers on Air Force and other military "
                   "installations.",
        "items": [
            {"what": "Petitioned to place data centers on Air Force and military "
                     "installations.",
             "date": "2026",
             "source": "https://www.newsweek.com/ai-data-center-war-where-democrats-republicans-in-key-senate-races-stand-12354265"},
        ],
        "as_of": "2026-08-25",
    },

    # ── Nebraska ──────────────────────────────────────────────────────────
    ("NE", "Dan Osborn"): {
        "lean": "guardrails",
        "summary": "Argues Nebraska should be investing in hospitals rather than "
                   "data centers.",
        "items": [
            {"what": "Called for shifting investment away from data centers and "
                     "toward hospitals.",
             "date": "2026",
             "source": "https://rivercountry.newschannelnebraska.com/story/336427630/fact-check-dan-osborn-data-centers"},
        ],
        "as_of": "2026-08-25",
    },
}


# ── the roster ─────────────────────────────────────────────────────────────
# Generated from each state election authority's certified candidate list; see
# `roster_source` on each race. Candidate order is as filed.
SENATE_RACES_2026 = [
    {
        "state": 'Florida', "abbrev": 'FL', "pvi": 'R+5',
        "special": True,
        "incumbent": 'Ashley Moody',
        "incumbent_party": 'Republican',
        "status": 'Interim appointee nominated',
        "roster_source": 'https://dos.elections.myflorida.com/candidates/CanList.asp',
        "candidates": [
            {"name": 'Neil Gillespie', "party": 'Independent'},
            {"name": 'Ashley Moody', "party": 'Republican'},
            {"name": 'Angie Nixon', "party": 'Democratic'},
        ],
    },
    {
        "state": 'Ohio', "abbrev": 'OH', "pvi": 'R+5',
        "special": True,
        "incumbent": 'Jon Husted',
        "incumbent_party": 'Republican',
        "status": 'Interim appointee nominated',
        "roster_source": 'https://www.ohiosos.gov/media-center/press-releases/2026/2026-02-04/',
        "candidates": [
            {"name": 'Sherrod Brown', "party": 'Democratic'},
            {"name": 'Jon Husted', "party": 'Republican'},
            {"name": 'Greg Levy', "party": 'Independent'},
            {"name": 'William Redpath', "party": 'Libertarian'},
        ],
    },
    {
        "state": 'Alabama', "abbrev": 'AL', "pvi": 'R+15',
        "special": False,
        "incumbent": 'Tommy Tuberville',
        "incumbent_party": 'Republican',
        "status": 'Incumbent retiring to run for governor',
        "roster_source": 'https://aldemocrats.org/2026-qualified-candidates',
        "candidates": [
            {"name": 'Barry Moore', "party": 'Republican'},
            {"name": 'Everett Wess', "party": 'Democratic'},
        ],
    },
    {
        "state": 'Alaska', "abbrev": 'AK', "pvi": 'R+6',
        "special": False,
        "incumbent": 'Dan Sullivan',
        # Ballot name differs from the common name, and a second, unrelated
        # "Dan J. Sullivan" is on the same ballot by court order — so the
        # incumbent is matched by an explicit ballot name, never by surname.
        "incumbent_on_ballot": 'Dan S. Sullivan',
        "incumbent_party": 'Republican',
        "status": 'Incumbent advanced to general',
        "roster_source": 'https://www.elections.alaska.gov/candidates',
        "candidates": [
            {"name": 'Gerald Heikes', "party": 'Republican'},
            {"name": 'David Leslie', "party": 'Democratic'},
            {"name": 'Mary Peltola', "party": 'Democratic'},
            {"name": 'Dan J. Sullivan', "party": 'Republican'},
            {"name": 'Dan S. Sullivan', "party": 'Republican'},
        ],
    },
    {
        "state": 'Arkansas', "abbrev": 'AR', "pvi": 'R+15',
        "special": False,
        "incumbent": 'Tom Cotton',
        "incumbent_party": 'Republican',
        "status": 'Incumbent renominated',
        "roster_source": 'https://candidates.arkansas.gov/',
        "candidates": [
            {"name": 'Tom Cotton', "party": 'Republican'},
            {"name": 'Hallie Shoffner', "party": 'Democratic'},
            {"name": 'Jeff Wadlin', "party": 'Libertarian'},
        ],
    },
    {
        "state": 'Colorado', "abbrev": 'CO', "pvi": 'D+6',
        "special": False,
        "incumbent": 'John Hickenlooper',
        "incumbent_party": 'Democratic',
        "status": 'Incumbent renominated',
        "roster_source": 'https://www.sos.state.co.us/pubs/elections/vote/primaryCandidates.html',
        "candidates": [
            {"name": 'Mark Baisley', "party": 'Republican'},
            {"name": 'John Hickenlooper', "party": 'Democratic'},
        ],
    },
    {
        "state": 'Delaware', "abbrev": 'DE', "pvi": 'D+8',
        "special": False,
        "incumbent": 'Chris Coons',
        "incumbent_party": 'Democratic',
        "status": 'Incumbent running',
        "roster_source": 'https://elections.delaware.gov/candidates/candidatelist/prim_fcddt_2026.shtml',
        "candidates": [
            {"name": 'Jeff Appelhans', "party": 'Democratic'},
            {"name": 'Chris Coons', "party": 'Democratic'},
            {"name": 'E. No-Trump Hansen', "party": 'Democratic'},
            {"name": 'Michael Katz', "party": 'Republican'},
            {"name": 'Mary Louve', "party": 'Democratic'},
            {"name": 'John Shulli', "party": 'Republican'},
        ],
    },
    {
        "state": 'Georgia', "abbrev": 'GA', "pvi": 'R+1',
        "special": False,
        "incumbent": 'Jon Ossoff',
        "incumbent_party": 'Democratic',
        "status": 'Incumbent renominated',
        "roster_source": 'https://mvp.sos.ga.gov/s/qualifying-candidate-information',
        "candidates": [
            {"name": 'Mike Collins', "party": 'Republican'},
            {"name": 'Jon Ossoff', "party": 'Democratic'},
        ],
    },
    {
        "state": 'Idaho', "abbrev": 'ID', "pvi": 'R+18',
        "special": False,
        "incumbent": 'Jim Risch',
        "incumbent_party": 'Republican',
        "status": 'Incumbent renominated',
        "roster_source": 'https://run.voteidaho.gov/search',
        "candidates": [
            {"name": 'Todd Achilles', "party": 'Independent'},
            {"name": 'Natalie Fleming', "party": 'Independent'},
            {"name": 'Matt Loesby', "party": 'Libertarian'},
            {"name": 'Jim Risch', "party": 'Republican'},
        ],
    },
    {
        "state": 'Illinois', "abbrev": 'IL', "pvi": 'D+6',
        "special": False,
        "incumbent": 'Dick Durbin',
        "incumbent_party": 'Democratic',
        "status": 'Incumbent retiring',
        "roster_source": 'https://www.elections.il.gov/ElectionOperations/CandidateFilingSearch.aspx?ID=Z2J%2fvYpKX8w%3d',
        "candidates": [
            {"name": 'Juliana Stratton', "party": 'Democratic'},
            {"name": 'Don Tracy', "party": 'Republican'},
        ],
    },
    {
        "state": 'Iowa', "abbrev": 'IA', "pvi": 'R+6',
        "special": False,
        "incumbent": 'Joni Ernst',
        "incumbent_party": 'Republican',
        "status": 'Incumbent retiring',
        "roster_source": 'https://sos.iowa.gov/primary-election',
        "candidates": [
            {"name": 'Ashley Hinson', "party": 'Republican'},
            {"name": 'Thomas Laehn', "party": 'Libertarian'},
            {"name": 'Josh Turek', "party": 'Democratic'},
        ],
    },
    {
        "state": 'Kansas', "abbrev": 'KS', "pvi": 'R+8',
        "special": False,
        "incumbent": 'Roger Marshall',
        "incumbent_party": 'Republican',
        "status": 'Incumbent renominated',
        "roster_source": 'https://www.sos.ks.gov/elections/elections_upcoming_candidate.aspx',
        "candidates": [
            {"name": 'Adam Hamilton', "party": 'Democratic'},
            {"name": 'Roger Marshall', "party": 'Republican'},
        ],
    },
    {
        "state": 'Kentucky', "abbrev": 'KY', "pvi": 'R+15',
        "special": False,
        "incumbent": 'Mitch McConnell',
        "incumbent_party": 'Republican',
        "status": 'Incumbent retiring',
        "roster_source": 'https://web.sos.ky.gov/CandidateFilings/default.aspx?elecid=86&id=3',
        "candidates": [
            {"name": 'Andy Barr', "party": 'Republican'},
            {"name": 'Charles Booker', "party": 'Democratic'},
        ],
    },
    {
        "state": 'Louisiana', "abbrev": 'LA', "pvi": 'R+11',
        "special": False,
        "incumbent": 'Bill Cassidy',
        "incumbent_party": 'Republican',
        "status": 'Incumbent lost renomination',
        "roster_source": 'https://voterportal.sos.la.gov/candidateinquiry',
        "candidates": [
            {"name": 'Jamie Davis', "party": 'Democratic'},
            {"name": 'Julia Letlow', "party": 'Republican'},
        ],
    },
    {
        "state": 'Maine', "abbrev": 'ME', "pvi": 'D+4',
        "special": False,
        "incumbent": 'Susan Collins',
        "incumbent_party": 'Republican',
        "status": 'Incumbent renominated',
        "roster_source": 'https://www.maine.gov/sos/elections-voting/upcoming-elections',
        "candidates": [
            {"name": 'Susan Collins', "party": 'Republican'},
            {"name": 'Troy Jackson', "party": 'Democratic'},
        ],
    },
    {
        "state": 'Massachusetts', "abbrev": 'MA', "pvi": 'D+14',
        "special": False,
        "incumbent": 'Ed Markey',
        "incumbent_party": 'Democratic',
        "status": 'Primary pending (September 1, 2026)',
        "roster_source": 'https://www.sec.state.ma.us/divisions/elections/research-and-statistics/dem-state-primary-candidates2026.htm',
        "note": 'Nominees are not yet settled — the state primary is September 1, '
                '2026, so the names below are primary candidates, not the '
                'general-election field.',
        "candidates": [
            {"name": 'John Deaton', "party": 'Republican'},
            {"name": 'Ed Markey', "party": 'Democratic'},
            {"name": 'Seth Moulton', "party": 'Democratic'},
        ],
    },
    {
        "state": 'Michigan', "abbrev": 'MI', "pvi": 'EVEN',
        "special": False,
        "incumbent": 'Gary Peters',
        "incumbent_party": 'Democratic',
        "status": 'Incumbent retiring',
        "roster_source": 'https://mi-boe.entellitrak.com/etk-mi-boe-prod/page.request.do?page=page.miboePublicReport&electionType=GEN&electionYear=2026',
        "candidates": [
            {"name": 'Lydia Christensen', "party": 'Libertarian'},
            {"name": 'Abdul El-Sayed', "party": 'Democratic'},
            {"name": 'Tim Long', "party": 'U.S. Taxpayers'},
            {"name": 'Douglas P. Marsh', "party": 'Green'},
            {"name": 'Mike Rogers', "party": 'Republican'},
        ],
    },
    {
        "state": 'Minnesota', "abbrev": 'MN', "pvi": 'D+3',
        "special": False,
        "incumbent": 'Tina Smith',
        "incumbent_party": 'DFL',
        "status": 'Incumbent retiring',
        "roster_source": 'https://candidates.sos.mn.gov/CandidateFilingResults.aspx?county=0&municipality=0&schooldistrict=0&hospitaldistrict=0&level=1&party=0&federal=True&judicial=True&executive=True&senate=True&representative=True&title=&office=0&candidateid=0',
        "candidates": [
            {"name": 'Peggy Flanagan', "party": 'DFL'},
            {"name": 'Michele Tafoya', "party": 'Republican'},
        ],
    },
    {
        "state": 'Mississippi', "abbrev": 'MS', "pvi": 'R+11',
        "special": False,
        "incumbent": 'Cindy Hyde-Smith',
        "incumbent_party": 'Republican',
        "status": 'Incumbent renominated',
        "roster_source": 'https://www.sos.ms.gov/elections-voting/candidate-referenda-information',
        "candidates": [
            {"name": 'Scott Colom', "party": 'Democratic'},
            {"name": 'Cindy Hyde-Smith', "party": 'Republican'},
            {"name": 'Ty Pinkins', "party": 'Independent'},
        ],
    },
    {
        "state": 'Montana', "abbrev": 'MT', "pvi": 'R+10',
        "special": False,
        "incumbent": 'Steve Daines',
        "incumbent_party": 'Republican',
        "status": 'Incumbent retiring',
        "roster_source": 'https://candidatefiling.mt.gov/candidatefiling/CandidateList.aspx?e=450002928',
        "candidates": [
            {"name": 'Kurt Alme', "party": 'Republican'},
            {"name": 'Kyle Austin', "party": 'Libertarian'},
            {"name": 'Alani Bankhead', "party": 'Democratic'},
            {"name": 'Seth Bodnar', "party": 'Independent'},
        ],
    },
    {
        "state": 'Nebraska', "abbrev": 'NE', "pvi": 'R+10',
        "special": False,
        "incumbent": 'Pete Ricketts',
        "incumbent_party": 'Republican',
        "status": 'Incumbent renominated',
        "roster_source": 'https://sos.nebraska.gov/elections',
        "candidates": [
            {"name": 'Mike Marvin', "party": 'Legal Marijuana Now'},
            {"name": 'Dan Osborn', "party": 'Independent'},
            {"name": 'Pete Ricketts', "party": 'Republican'},
        ],
    },
    {
        "state": 'New Hampshire', "abbrev": 'NH', "pvi": 'D+2',
        "special": False,
        "incumbent": 'Jeanne Shaheen',
        "incumbent_party": 'Democratic',
        "status": 'Incumbent retiring',
        "roster_source": 'https://nhjournal.com/john-e-sununu-jumps-into-race/',
        "candidates": [
            {"name": 'Scott Brown', "party": 'Republican'},
            {"name": 'Karishma Manzur', "party": 'Democratic'},
            {"name": 'Chris Pappas', "party": 'Democratic'},
            {"name": 'Jared Sullivan', "party": 'Democratic'},
            {"name": 'John E. Sununu', "party": 'Republican'},
        ],
    },
    {
        "state": 'New Jersey', "abbrev": 'NJ', "pvi": 'D+4',
        "special": False,
        "incumbent": 'Cory Booker',
        "incumbent_party": 'Democratic',
        "status": 'Incumbent renominated',
        "roster_source": 'https://www.nj.gov/state/elections/election-information-2026.shtml',
        "candidates": [
            {"name": 'Cory Booker', "party": 'Democratic'},
            {"name": 'Justin Murphy', "party": 'Republican'},
        ],
    },
    {
        "state": 'New Mexico', "abbrev": 'NM', "pvi": 'D+4',
        "special": False,
        "incumbent": 'Ben Ray Luján',
        "incumbent_party": 'Democratic',
        "status": 'Incumbent renominated',
        "roster_source": 'https://candidateportal.servis.sos.state.nm.us/CandidateList.aspx?eid=2911&cty=99',
        "candidates": [
            {"name": 'Ben Ray Luján', "party": 'Democratic'},
            {"name": 'Larry Marker', "party": 'Republican'},
        ],
    },
    {
        "state": 'North Carolina', "abbrev": 'NC', "pvi": 'R+1',
        "special": False,
        "incumbent": 'Thom Tillis',
        "incumbent_party": 'Republican',
        "status": 'Incumbent retiring',
        "roster_source": 'https://www.ncsbe.gov/results-data/candidate-lists',
        "candidates": [
            {"name": 'Shannon Bray', "party": 'Libertarian'},
            {"name": 'Roy Cooper', "party": 'Democratic'},
            {"name": 'Michael Whatley', "party": 'Republican'},
        ],
    },
    {
        "state": 'Oklahoma', "abbrev": 'OK', "pvi": 'R+17',
        "special": False,
        "incumbent": 'Alan S. Armstrong',
        "incumbent_party": 'Republican',
        "status": 'Interim appointee ineligible to run',
        "roster_source": 'https://filings.okelections.gov/ViewCandidates/2026040120260403/99/all',
        "candidates": [
            {"name": 'Kevin Hern', "party": 'Republican'},
            {"name": 'Ron Meinhardt', "party": 'Independent'},
            {"name": 'Curtis Stinnett', "party": 'Independent'},
            {"name": "N'Kiyla Thomas", "party": 'Democratic'},
            {"name": 'Sevier White', "party": 'Libertarian'},
        ],
    },
    {
        "state": 'Oregon', "abbrev": 'OR', "pvi": 'D+8',
        "special": False,
        "incumbent": 'Jeff Merkley',
        "incumbent_party": 'Democratic',
        "status": 'Incumbent renominated',
        "roster_source": 'https://secure.sos.state.or.us/orestar/CFSearchPage.do#',
        "candidates": [
            {"name": 'Jeff Merkley', "party": 'Democratic'},
            {"name": 'David Brock Smith', "party": 'Republican'},
        ],
    },
    {
        "state": 'Rhode Island', "abbrev": 'RI', "pvi": 'D+8',
        "special": False,
        "incumbent": 'Jack Reed',
        "incumbent_party": 'Democratic',
        "status": 'Incumbent running',
        "roster_source": 'https://vote.sos.ri.gov/Candidates/CandidateSearch',
        "candidates": [
            {"name": 'Michael Bahry', "party": 'Independent'},
            {"name": 'Connor Burbridge', "party": 'Democratic'},
            {"name": 'Raymond McKay', "party": 'Republican'},
            {"name": 'Luis Munoz', "party": 'Democratic'},
            {"name": 'Jack Reed', "party": 'Democratic'},
        ],
    },
    {
        "state": 'South Carolina', "abbrev": 'SC', "pvi": 'R+8',
        "special": False,
        "incumbent": 'Darline Graham',
        "incumbent_party": 'Republican',
        "status": 'Interim appointee nominated in runoff',
        "roster_source": 'https://vrems.scvotes.sc.gov/Candidate/CandidateSearch?electionId=22598',
        "candidates": [
            {"name": 'Annie Andrews', "party": 'Democratic'},
            {"name": 'Darline Graham', "party": 'Republican'},
            {"name": 'Mark Hackett', "party": 'Constitution'},
            {"name": 'Kasie Whitener', "party": 'Libertarian'},
            {"name": 'Catherine Fleming Bruce', "party": "Democratic, ''write-in''"},
        ],
    },
    {
        "state": 'South Dakota', "abbrev": 'SD', "pvi": 'R+15',
        "special": False,
        "incumbent": 'Mike Rounds',
        "incumbent_party": 'Republican',
        "status": 'Incumbent renominated',
        "roster_source": 'https://vip.sdsos.gov/candidatelist.aspx?eid=773',
        "candidates": [
            {"name": 'Brian Bengs', "party": 'Independent'},
            {"name": 'Mike Rounds', "party": 'Republican'},
        ],
    },
    {
        "state": 'Tennessee', "abbrev": 'TN', "pvi": 'R+14',
        "special": False,
        "incumbent": 'Bill Hagerty',
        "incumbent_party": 'Republican',
        "status": 'Incumbent renominated',
        "roster_source": 'https://sos.tn.gov/elections/2026-candidate-lists',
        "candidates": [
            {"name": 'Marquita Bradshaw', "party": 'Democratic'},
            {"name": 'Tharon Chandler', "party": 'Independent'},
            {"name": 'Andrew Gerena', "party": 'Independent'},
            {"name": 'Bill Hagerty', "party": 'Republican'},
            {"name": 'Jeremy Hearn', "party": 'Independent'},
            {"name": 'Robert Jones', "party": 'Independent'},
            {"name": 'James Macon III', "party": 'Independent'},
            {"name": 'Yoshi Matthews', "party": 'Independent'},
            {"name": 'David Sutman Jr.', "party": 'Independent'},
            {"name": 'Catherine Whitson', "party": 'Independent'},
        ],
    },
    {
        "state": 'Texas', "abbrev": 'TX', "pvi": 'R+6',
        "special": False,
        "incumbent": 'John Cornyn',
        "incumbent_party": 'Republican',
        "status": 'Incumbent lost renomination in runoff',
        "roster_source": 'https://goelect.txelections.civixapps.com/ivis-cbp-ui/candidate-information',
        "candidates": [
            {"name": 'Ted Brown', "party": 'Libertarian'},
            {"name": 'Ken Paxton', "party": 'Republican'},
            {"name": 'James Talarico', "party": 'Democratic'},
        ],
    },
    {
        "state": 'Virginia', "abbrev": 'VA', "pvi": 'D+3',
        "special": False,
        "incumbent": 'Mark Warner',
        "incumbent_party": 'Democratic',
        "status": 'Incumbent renominated',
        "roster_source": 'https://www.elections.virginia.gov/casting-a-ballot/candidate-list/',
        "candidates": [
            {"name": 'Bert Mizusawa', "party": 'Republican'},
            {"name": 'Mark Moran', "party": 'Independent'},
            {"name": 'Mark Warner', "party": 'Democratic'},
        ],
    },
    {
        "state": 'West Virginia', "abbrev": 'WV', "pvi": 'R+21',
        "special": False,
        "incumbent": 'Shelley Moore Capito',
        "incumbent_party": 'Republican',
        "status": 'Incumbent renominated',
        "roster_source": 'https://candidates.wvsos.gov/',
        "candidates": [
            {"name": 'Rachel Fetty Anderson', "party": 'Democratic'},
            {"name": 'Shelley Moore Capito', "party": 'Republican'},
            {"name": 'Rio Phillips', "party": 'Write-in'},
            {"name": 'S. Marshall Wilson', "party": 'Constitution'},
        ],
    },
    {
        "state": 'Wyoming', "abbrev": 'WY', "pvi": 'R+23',
        "special": False,
        "incumbent": 'Cynthia Lummis',
        "incumbent_party": 'Republican',
        "status": 'Incumbent retiring',
        "roster_source": 'https://sos.wyo.gov/elections/',
        "candidates": [
            {"name": 'James W. Byrd', "party": 'Democratic'},
            {"name": 'Harriet Hageman', "party": 'Republican'},
        ],
    },
]


def _norm(name):
    """Normalised full name. Keys are FULL names, never surnames.

    Alaska 2026 is why: the ballot carries both `Dan S. Sullivan` (the
    incumbent) and `Dan J. Sullivan`, an unrelated candidate who won a state
    Supreme Court case to appear under that name. A surname key — the pattern
    src/officials_stances.py uses, where one person holds one office per
    state — gave the senator's record to both men and flagged both as the
    incumbent. Attributing a position to the wrong candidate on a ballot is
    the worst failure this page has, so the key is the whole name.
    """
    return " ".join(str(name).split()).casefold()


_BY_NAME = {(st, _norm(n)): rec for (st, n), rec in AI_RECORDS.items()}


def record_for(abbrev, name):
    """The documented AI/data-center record for one candidate, or None."""
    return _BY_NAME.get((abbrev, _norm(name)))


def races(include_minor=True):
    """Every 2026 Senate race with each candidate's record attached.

    Each candidate gains `lean`, `lean_label`, `lean_color`, `summary`,
    `items`, `as_of` and `incumbent`. Candidates with no located record get
    lean "unrecorded" and an empty item list — deliberately, so the page can
    show the gap rather than imply neutrality.
    """
    out = []
    for r in SENATE_RACES_2026:
        race = dict(r)
        cands = []
        for c in r["candidates"]:
            rec = record_for(r["abbrev"], c["name"]) or {}
            lean = rec.get("lean", "unrecorded")
            label, _desc, color = LEANS[lean]
            cands.append({
                **c,
                "incumbent": _norm(c["name"]) == _norm(
                    r.get("incumbent_on_ballot") or r["incumbent"]),
                "lean": lean,
                "lean_label": label,
                "lean_color": color,
                "summary": rec.get("summary"),
                "items": rec.get("items", []),
                "as_of": rec.get("as_of"),
            })
        if not include_minor:
            cands = [c for c in cands
                     if c["party"] in ("Democratic", "Republican", "DFL")
                     or c["lean"] != "unrecorded"]
        # documented records first, then major parties, then the rest
        order = {"Democratic": 0, "DFL": 0, "Republican": 0}
        cands.sort(key=lambda c: (c["lean"] == "unrecorded",
                                  order.get(c["party"], 1), c["name"]))
        race["candidates"] = cands
        race["documented"] = sum(1 for c in cands if c["lean"] != "unrecorded")
        race["contested"] = race["documented"] > 0
        out.append(race)
    return out


def coverage():
    """How much of the roster actually has a documented record.

    Published on the page. A coverage number that is low is the point: it
    tells a reader the silence is real rather than an omission we hid.
    """
    rs = races()
    cands = [c for r in rs for c in r["candidates"]]
    return {
        "races": len(rs),
        "candidates": len(cands),
        "documented": sum(1 for c in cands if c["lean"] != "unrecorded"),
        "races_documented": sum(1 for r in rs if r["contested"]),
        "as_of": ROSTER_AS_OF,
    }
