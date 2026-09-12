"""
2026 U.S. House races — where each candidate stands on AI data centers.

Companion to src/senate_races.py; the shared vocabulary, record model and
freshness rules live in src/race_common.py.

Why the roster is a JSON file and the Senate's is not
----------------------------------------------------
440 districts and 1,161 candidates is ~2,500 lines of pure roster. Inlining it
the way senate_races.py does would bury the curated part — the records — under
data nobody hand-edits. So the ballot lives in `data/house_races_2026.json`
(regenerated from the state candidate lists) and only AI_RECORDS, which is
hand-researched and needs its reasoning next to it, stays in Python.

Sourcing discipline is identical to the Senate tracker:

* Each district's `roster_source` is the state election authority's own
  certified candidate list.
* Every record item carries its own `source` URL and `date`.
* Records key on the FULL candidate name — at 1,161 candidates, repeated
  surnames are guaranteed, not hypothetical.
* Candidates with nothing located are `unrecorded` and render as *No record
  found*, never as neutral.

Coverage will start very low and that is stated on the page rather than hidden.
It grows through scripts/scan_candidate_records.py, which files leads into a
review queue that a human promotes — never straight into this table, because
promotion is where `source` and `as_of` come from.
"""

import functools
import json
import pathlib

from src import race_common as rc

ROOT = pathlib.Path(__file__).resolve().parent.parent
ROSTER_FILE = ROOT / "data" / "house_races_2026.json"

LEANS = rc.LEANS
LEAN_NOTE = rc.LEAN_NOTE
ELECTION_DATE = rc.ELECTION_DATE


@functools.lru_cache(maxsize=1)
def _roster():
    data = json.loads(ROSTER_FILE.read_text())
    return data["roster_as_of"], data["districts"]


ROSTER_AS_OF = _roster()[0]
HOUSE_RACES_2026 = _roster()[1]


# ── the record ─────────────────────────────────────────────────────────────
# Key: (state postal, district, FULL candidate name) -> record dict.
#   summary : one sentence, plain language, nothing the sources don't support
#   lean    : key into rc.LEANS
#   items   : list of {what, date (ISO or ""), source (URL)}
#   as_of   : date this entry was last read. Never invent one.
#
# Seeded from federal legislative action, which is the strongest evidence a
# House record can carry: a cosponsorship is a dated, verifiable act, unlike a
# campaign statement. Challenger records arrive via the review queue.
AI_RECORDS = {
    # ── H.R. 9340, Ratepayer Protection Act ────────────────────────────────
    # Cleared House Energy & Commerce 52-0 on 2026-07-22. A committee vote is
    # the strongest evidence on this page: dated, recorded, and unlike a
    # campaign promise it already happened.
    ("CO", "8", "Gabe Evans"): {
        "lean": "guardrails",
        "summary": "Lead Republican sponsor of the Ratepayer Protection Act, "
                   "which would push states to make large loads — data centers "
                   "included — pay for the generation and transmission they "
                   "require instead of spreading it across households.",
        "items": [
            {"what": "Introduced H.R. 9340, the Ratepayer Protection Act, with "
                     "Rep. Kathy Castor. It directs states and their PUCs to "
                     "consider standards for connecting large-load customers so "
                     "those customers, not families and small businesses, cover "
                     "new generation, transmission and upgrade costs. Cleared "
                     "House Energy and Commerce 52-0.",
             "date": "2026-07-22",
             "source": "https://broadbandbreakfast.com/house-committee-approves-package-to-address-data-centers-growing-energy-demands/"},
        ],
        "as_of": "2026-08-26",
    },
    ("FL", "14", "Kathy Castor"): {
        "lean": "guardrails",
        "summary": "Lead Democratic sponsor of the Ratepayer Protection Act, "
                   "the bipartisan House bill making large loads carry their own "
                   "grid costs.",
        "items": [
            {"what": "Introduced H.R. 9340, the Ratepayer Protection Act, with "
                     "Rep. Gabe Evans — standards for states and PUCs connecting "
                     "large-load customers so the cost of new generation, "
                     "transmission and upgrades falls on those customers rather "
                     "than on households. Cleared House Energy and Commerce "
                     "52-0.",
             "date": "2026-07-22",
             "source": "https://broadbandbreakfast.com/house-committee-approves-package-to-address-data-centers-growing-energy-demands/"},
        ],
        "as_of": "2026-08-26",
    },

    # ── H.R. 8241, Power for the People Act of 2026 ────────────────────────
    # House companion to Van Hollen's S.3682. Cited to the bill of record:
    # congress.gov refuses scripted fetches (verify_candidate_records.py
    # classifies that as *blocked*, not dead — same convention as
    # scripts/verify_sources.py), but it is the canonical page for the text.
    ("MD", "7", "Kweisi Mfume"): {
        "lean": "guardrails",
        "summary": "Introduced the House Power for the People Act, aimed at "
                   "stopping data-center demand from raising household energy "
                   "bills.",
        "items": [
            {"what": "Introduced H.R. 8241, the Power for the People Act of "
                     "2026, with Rep. Paul Tonko — the House companion to "
                     "S.3682, which directs states to consider data-center rate "
                     "classes and seeks a FERC rule making data centers pay for "
                     "the transmission upgrades they require.",
             "date": "2026",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/8241/all-info"},
            {"what": "Co-signed Maryland Congressional delegation letter "
                     "to FERC urging revision of PJM cost-allocation "
                     "rules so Maryland consumers do not finance $2B in "
                     "infrastructure built primarily for out-of-state "
                     "data centers.",
             "date": "2026-07-28",
             "source": "https://mcclaindelaney.house.gov/media/press-releases/maryland-democrats-urge-ferc-protect-marylanders-rising-electricity-costs-due"},
        ],
        "as_of": "2026-09-11",
    },
    ("NY", "20", "Paul Tonko"): {
        "lean": "guardrails",
        "summary": "Co-introduced the House Power for the People Act to shield "
                   "consumers from data-center-driven energy costs; says data "
                   "centers should be built in communities that want them.",
        "items": [
            {"what": "Co-introduced H.R. 8241, the Power for the People Act of "
                     "2026, with Rep. Kweisi Mfume — the House companion to "
                     "S.3682 on data-center rate classes and FERC cost "
                     "allocation.",
             "date": "2026-04-09",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/8241/all-info"},
            {"what": "Said data centers \"should be built in communities that "
                     "want them\" regarding the proposed Kenwood Commons project "
                     "in Bethlehem.",
             "date": "2026-08-11",
             "source": "https://www.wamc.org/news/2026-08-11/tonko-kenwood-project-data-center"},
        ],
        "as_of": "2026-09-11",
    },

    # ── CA deep dive, 2026-09-11 ──────────────────────────────────────────
    ("CA", "25", "Raul Ruiz"): {
        "lean": "guardrails",
        "summary": "Formally opposed data centers in Imperial and Coachella "
                   "Valleys, submitting a letter to the Imperial County Board "
                   "of Supervisors and announcing plans to seek federal "
                   "oversight from EPA and DOE. Sits on House Energy and "
                   "Commerce Committee.",
        "items": [
            {"what": "Submitted letter to Imperial County Board of "
                     "Supervisors opposing the proposed Imperial Valley Data "
                     "Center Campus, read into the public record: "
                     "“I unequivocally oppose data centers in Imperial "
                     "Valley.” Cited reduced life expectancy, air "
                     "pollution, asthma, energy costs and water use. "
                     "Announced plans to send letters to EPA and DOE seeking "
                     "federal environmental review.",
             "date": "2026-06-02",
             "source": "https://www.thedesertreview.com/news/ruiz-formally-opposes-proposed-imperial-data-center-project/article_66fd01cf-c1db-4002-b64e-895dc9b5d09e.html"},
        ],
        "as_of": "2026-09-11",
    },
    ("CA", "49", "Mike Levin"): {
        "lean": "guardrails",
        "summary": "Introduced the SHIELD Act (H.R.7066) creating a separate "
                   "rate class for large energy users so residential ratepayers "
                   "don't subsidize data center grid upgrades. Also co-introduced "
                   "the Energy Bills Relief Act and cosponsored the Responsible "
                   "Data Center Siting Act.",
        "items": [
            {"what": "Introduced the SHIELD Act (H.R.7066, Stopping Hikes In "
                     "Electricity from Large Load Demands): separate rate class "
                     "for loads over 75 MW, prioritizes interconnection for "
                     "renewable-powered large loads. Levin: “Families "
                     "should not be forced to subsidize massive energy costs "
                     "for billion-dollar companies.”",
             "date": "2026-01-14",
             "source": "https://levin.house.gov/media/press-releases/rep-mike-levin-introduces-new-bill-to-stop-data-centers-from-driving-up-electricity-prices-for-consumers"},
            {"what": "Co-introduced the Energy Bills Relief Act (H.R.7977) "
                     "with Rep. Casten and 120 House Democrats, including a "
                     "provision ensuring data centers and large energy users "
                     "pay their own grid costs.",
             "date": "2026-03-18",
             "source": "https://levin.house.gov/media/press-releases/reps-levin-and-casten_seec-clean-energy-deployment-task-force-introduce-the-energy-bills-relief-act"},
            {"what": "Cosponsored the Responsible Data Center Siting Act "
                     "(H.R.10321, introduced by Rep. Subramanyam), directing "
                     "the Secretary of Energy to establish best practices for "
                     "data center siting considering grid impacts, water use "
                     "and utility bills.",
             "date": "2026-09-08",
             "source": "https://www.govinfo.gov/app/details/BILLS-119hr10321ih"},
        ],
        "as_of": "2026-09-11",
    },

    # ── promoted from the review queue, 2026-08-26 ────────────────────────
    # Surfaced by scripts/scan_candidate_records.py as Google News leads, then
    # promoted by hand: each redirect was resolved to the member's own release,
    # which is what these cite. A queue link is never the citation.
    ("CA", "17", "Ro Khanna"): {
        "lean": "guardrails",
        "summary": "Introduced a Data Center Bill of Rights resolution "
                   "affirming a community's right to ban data centers near "
                   "homes and schools, to reject a project outright, and to keep "
                   "local siting authority from being preempted by the state.",
        "items": [
            {"what": "Introduced the Data Center Bill of Rights resolution: "
                     "communities may ban data centers in residential areas and "
                     "within 2,500 feet of homes, schools, childcare, hospitals "
                     "or nursing homes; may reject a project through a "
                     "transparent community process; county and municipal "
                     "authority to prohibit or regulate is preserved against "
                     "state preemption; and every data center must use clean, "
                     "reliable energy under strict noise and air limits. It is a "
                     "resolution, so it does not itself change law.",
             "date": "2026-08-06",
             "source": "https://khanna.house.gov/media/press-releases/release-rep-khanna-introduces-data-center-bill-rights"},
        ],
        "as_of": "2026-08-26",
    },
    ("NJ", "6", "Frank Pallone"): {
        "lean": "guardrails",
        "summary": "The senior Democrat on House Energy and Commerce called for "
                   "a national moratorium on AI data centers until their effect "
                   "on air, water and power bills is resolved.",
        "items": [
            {"what": "Called for a national AI data-center moratorium at an "
                     "Energy Subcommittee markup — \u201cin favor of a national AI "
                     "data center moratorium until we can find a way to ensure "
                     "they don't harm our nation's air, water, and power "
                     "bills.\u201d",
             "date": "2026-06-25",
             "source": "https://pallone.house.gov/media/press-releases/pallone-supports-national-ai-data-center-moratorium"},
        ],
        "as_of": "2026-08-26",
    },
    ("NY", "19", "Josh Riley"): {
        "lean": "guardrails",
        "summary": "Introduced the bipartisan FAIR Data Act to keep the cost of "
                   "generation, transmission and distribution upgrades for data "
                   "centers off New York ratepayers.",
        "items": [
            {"what": "Introduced the FAIR Data Act, bipartisan legislation to "
                     "stop data-center projects from raising energy bills for "
                     "Upstate New York families and small businesses by "
                     "shielding ratepayers from the generation, transmission and "
                     "distribution upgrades those projects require.",
             "date": "2026-07-13",
             "source": "https://riley.house.gov/2026/07/13/riley-introduces-bill-to-stop-data-center-projects-from-driving-up-energy-bills/"},
        ],
        "as_of": "2026-09-11",
    },
    ("GA", "7", "Rich McCormick"): {
        "lean": "accelerate",
        "summary": "Chaired the House Science subcommittee hearing on expanding "
                   "data-center infrastructure and argues against slowing the "
                   "buildout, calling local opposition alarmism while "
                   "acknowledging rural grid limits.",
        "items": [
            {"what": "Opened a House Science, Space and Technology subcommittee "
                     "hearing, \u201cPowering America's AI Future: Assessing Policy "
                     "Options to Increase Data Center Infrastructure\u201d, framing "
                     "the question as whether approval processes can deliver the "
                     "infrastructure AI leadership needs in time, and flagging "
                     "rural Georgia's cooperative grid as a binding constraint.",
             "date": "2026-02",
             "source": "https://mccormick.house.gov/media/press-releases/subcommittee-chairman-mccormick-opens-hearing-ai-data-center-infrastructure"},
            {"what": "Said the U.S. should keep expanding data centers to hold "
                     "AI leadership, arguing they can be built responsibly and "
                     "benefit local economies, and pushed back on what he called "
                     "alarmism in local protests.",
             "date": "2026-08-23",
             "source": "https://www.bloomberg.com/news/videos/2026-08-23/rep-mccormick-warns-against-slowing-ai-buildout-video"},
        ],
        "as_of": "2026-08-26",
    },
    # ── Virginia — the state with the most data centers and, until 2026-09-05,
    # zero records on this page. Each item is the member's own release or a
    # dated interview; a letter to a planning commission is an action, a
    # study bill is a bill, and an interview quote is only a quote — the
    # summaries say which.
    ("VA", "8", "Don Beyer"): {
        "lean": "guardrails",
        "summary": "Wrote to the Fairfax County Planning Commission asking it "
                   "to deny the Dominion substation that would power the Plaza "
                   "500 data center in Lincolnia — a documented action on a "
                   "live project in his district, not a bill.",
        "items": [
            {"what": "Sent a formal letter urging the Fairfax County Planning "
                     "Commission to reject the 2232 permit for the Edsall Road "
                     "data-center substation at Plaza 500, citing flooding, "
                     "light and noise: “Data center infrastructure should not "
                     "be built in residential areas where its scale and likely "
                     "impacts are fundamentally incompatible with the character "
                     "and quality of life of adjacent neighborhoods.”",
             "date": "2026-07-30",
             "source": "https://beyer.house.gov/news/documentsingle.aspx?DocumentID=9183"},
        ],
        "as_of": "2026-09-05",
    },
    ("VA", "7", "Eugene Vindman"): {
        "lean": "guardrails",
        "summary": "Introduced the Smart Data Center Policy Act, a Commerce "
                   "Department study of siting data centers in industrial "
                   "zones, transport hubs and military bases instead of next "
                   "to neighborhoods, schools and parks. A study bill, not a "
                   "mandate.",
        "items": [
            {"what": "Introduced the Smart Data Center Policy Act, directing "
                     "the Department of Commerce to study the costs, benefits "
                     "and possible federal incentives for siting data centers "
                     "in industrial zones, rail and airport hubs and military "
                     "installations rather than near homes and green space, "
                     "with findings due to Congress in 180 days. Vindman: “We "
                     "need to ensure data centers pay their fair share and are "
                     "built in places that make sense — not next to "
                     "neighborhoods, schools, or our public lands.”",
             "date": "2026-08-04",
             "source": "https://vindman.house.gov/2026/08/04/vindman-introduces-legislation-to-prevent-data-center-development-near-neighborhoods-schools-parks/"},
        ],
        "as_of": "2026-09-05",
    },
    ("VA", "10", "Suhas Subramanyam"): {
        "lean": "guardrails",
        "summary": "Represents Data Center Alley and has filed two bills on "
                   "it: a DHS security strategy for communities around data "
                   "centers, and a bipartisan NIST standard for measuring what "
                   "each facility actually draws in power and water.",
        "items": [
            {"what": "Introduced the Data Infrastructure Risk Reduction Act, "
                     "directing the Department of Homeland Security to write a "
                     "security strategy and recommendations for protecting "
                     "communities around data centers and the transmission and "
                     "water systems that serve them.",
             "date": "2026-05-08",
             "source": "https://subramanyam.house.gov/media/press-releases/rep-subramanyam-introduces-bill-protect-homes-and-property-near-data-centers"},
            {"what": "Introduced the bipartisan Data Infrastructure Energy "
                     "Measurement and Standards Act with Reps. Obernolte (R-CA) "
                     "and Foushee (D-NC), directing NIST and DOE to set "
                     "standards for measuring data center energy and water use "
                     "so forecasting and siting rest on disclosed numbers. "
                     "Subramanyam: “We need a simple way to track how much "
                     "power and water these facilities use.”",
             "date": "2026-06-18",
             "source": "https://subramanyam.house.gov/media/press-releases/reps-subramanyam-obernolte-foushee-introduce-legislation-create-first-its-kind"},
        ],
        "as_of": "2026-09-05",
    },
    ("VA", "1", "Rob Wittman"): {
        "lean": "accelerate",
        "summary": "Backed an NDAA provision using a Naval Weapons Station "
                   "Yorktown–Dominion nuclear partnership as a pathfinder for "
                   "meeting military and data-center power demand. Supply-side "
                   "only; nothing located on who pays or on siting.",
        "items": [
            {"what": "Supported the FY2026 NDAA committee text that “directs "
                     "the Navy to use a promising partnership between Naval "
                     "Weapons Station Yorktown and Dominion Energy as a "
                     "pathfinder to determine how to leverage nuclear power to "
                     "meet Navy and Marine Corps installation power demands, in "
                     "addition to supporting the data center energy demands of "
                     "accelerating technologies like artificial intelligence.”",
             "date": "2025-07-15",
             "source": "https://wittman.house.gov/newsroom/press-releases/wittman-supports-legislation-that-strengthens-national-defense-and-supports-virginia-shipbuilding"},
        ],
        "as_of": "2026-09-05",
    },
    ("VA", "2", "Jen Kiggans"): {
        "lean": "mixed",
        "summary": "An interview quote, not an action: said data centers "
                   "cannot all be banned but there is “a commonsense "
                   "conversation to be had” about their energy and water use, "
                   "and that the fight belongs in Richmond. Her district "
                   "includes Virginia Beach and Chesapeake, both under local "
                   "pauses.",
        "items": [
            {"what": "Told The Daily Signal: “They have data centers under the "
                     "ocean floor. We can't ban all data centers,” adding there "
                     "is “a commonsense conversation to be had” on their "
                     "consumption of energy, water and local resources, that "
                     "the debate has so far been left to the General Assembly, "
                     "and that she has “enjoyed watching the Democrats fight "
                     "with each other about the issue.”",
             "date": "2026-08-18",
             "source": "https://www.dailysignal.com/2026/08/18/midterm-rematch-fate-of-country/"},
        ],
        "as_of": "2026-09-05",
    },

    # ── Michigan ───────────────────────────────────────────────────────────
    ("MI", "12", "Rashida Tlaib"): {
        "lean": "guardrails",
        "summary": "Introduced a bill banning AI data centers on federal lands, "
                   "cosponsored the site-selection transparency act, and issued "
                   "a statement opposing a specific data center in her district.",
        "items": [
            {"what": "Introduced H.R. 9939, the No AI Data Centers on Federal "
                     "Lands Act, permanently banning large AI data centers "
                     "(>20 MW) and associated infrastructure on all federal "
                     "land including military bases.",
             "date": "2026-07-23",
             "source": "https://tlaib.house.gov/posts/rep-tlaib-introduces-a-bill-to-ban-ai-data-centers-on-federal-lands"},
            {"what": "Cosponsored H.R. 8488, the AI Data Center Site Selection "
                     "Transparency Act, requiring developers to disclose "
                     "location, impacts, and other information to local elected "
                     "officials and the public before development.",
             "date": "2026-04-23",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/8488/text"},
            {"what": "Issued statement after Southfield City Council approved "
                     "a Metrobloks AI data center, citing residents' concerns "
                     "about electricity costs rising 'as much as 267%' and "
                     "water consumption of 'millions of gallons per day.'",
             "date": "2025-12-16",
             "source": "https://tlaib.house.gov/posts/tlaib-statement-on-ai-data-center-vote-in-southfield"},
        ],
        "as_of": "2026-09-07",
    },
    ("MI", "3", "Hillary Scholten"): {
        "lean": "guardrails",
        "summary": "Introduced two data center accountability bills: a resource "
                   "disclosure act requiring annual energy and water surveys, and "
                   "a DoD data center efficiency bill.",
        "items": [
            {"what": "Introduced H.R. 10005, the Data Center Resource Disclosure "
                     "Act, requiring NTIA to conduct annual surveys of data "
                     "center energy and water consumption and publish results on "
                     "a public dashboard.",
             "date": "2026-07-30",
             "source": "https://scholten.house.gov/media/press-releases/congresswoman-scholten-introduces-two-data-center-accountability-bills"},
            {"what": "Introduced H.R. 10004, the Defending Our Energy and Water "
                     "Act, directing DoD to update data center efficiency "
                     "standards and mandate cooling technologies that reduce "
                     "water impact.",
             "date": "2026-07-30",
             "source": "https://scholten.house.gov/media/press-releases/congresswoman-scholten-introduces-two-data-center-accountability-bills"},
        ],
        "as_of": "2026-09-07",
    },
    ("MI", "6", "Debbie Dingell"): {
        "lean": "guardrails",
        "summary": "Co-signed the first congressional letter specifically "
                   "investigating data center energy cost pass-throughs to "
                   "ratepayers.",
        "items": [
            {"what": "One of 20 House members who signed a letter to FERC, "
                     "Edison Electric Institute, and the Data Center Coalition "
                     "expressing concern that data center energy costs are "
                     "increasingly being passed onto everyday Americans and "
                     "requesting information on consumer protections.",
             "date": "2025-10-28",
             "source": "https://kevinmullin.house.gov/2025/10/28/rep-mullin-leads-group-of-lawmakers-investigating-impact-of-data-centers-on-energy-costs/"},
        ],
        "as_of": "2026-09-07",
    },
    ("MI", "7", "Tom Barrett"): {
        "lean": "mixed",
        "summary": "Voted for the OBBBA's 10-year AI preemption in May 2025, "
                   "then introduced local-control protection and NDA-ban bills "
                   "in August 2026 as data centers became a campaign issue.",
        "items": [
            {"what": "Voted Yea on H.R. 1 (OBBBA) including SEC. 43201, a "
                     "10-year moratorium on state and local enforcement of any "
                     "law regulating AI systems — a provision broad enough to "
                     "cover data center zoning. Stripped by the Senate 99-1.",
             "date": "2025-05-22",
             "source": "https://clerk.house.gov/Votes/2025145"},
            {"what": "Introduced H.R. 10119, the Protecting Local Control of "
                     "Data Centers Act, prohibiting federal agencies from "
                     "overriding local land-use, zoning, siting, or permitting "
                     "authority for data centers.",
             "date": "2026-08-20",
             "source": "https://barrett.house.gov/media/press-releases/barrett-introduces-bills-protect-local-communities-data-center-overreach"},
            {"what": "Introduced H.R. 10118, the No Data Center NDAs Act, "
                     "prohibiting members of Congress from signing NDAs about "
                     "data centers including information on locations, water "
                     "usage, or energy requirements.",
             "date": "2026-08-20",
             "source": "https://barrett.house.gov/media/press-releases/barrett-introduces-bills-protect-local-communities-data-center-overreach"},
        ],
        "as_of": "2026-09-07",
    },
    ("MI", "10", "John James"): {
        "lean": "accelerate",
        "summary": "Voted four times in support of the OBBBA's 10-year AI "
                   "preemption provision, including voting against an amendment "
                   "to remove it.",
        "items": [
            {"what": "Voted four separate times to advance the OBBBA's AI "
                     "preemption provision (SEC. 43201): twice in committee, "
                     "once against an amendment to remove it, and once on final "
                     "passage. The provision would have banned all state and "
                     "local AI/data center regulation for 10 years. Stripped "
                     "by the Senate 99-1.",
             "date": "2025-05-22",
             "source": "https://clerk.house.gov/Votes/2025145"},
        ],
        "as_of": "2026-09-07",
    },

    # ── Ohio ───────────────────────────────────────────────────────────────
    ("OH", "1", "Greg Landsman"): {
        "lean": "guardrails",
        "summary": "Introduced three bills targeting data center accountability: "
                   "FERC cost-shifting recommendations, full-cost-recovery and "
                   "NDA bans, and an EPA/National Academies environmental study.",
        "items": [
            {"what": "Introduced H.R. 6529, the Protecting Families from AI "
                     "Data Center Energy Costs Act, directing FERC to convene "
                     "stakeholders and recommend ways to prevent data center "
                     "energy costs from being passed onto residents.",
             "date": "2025-12-09",
             "source": "https://landsman.house.gov/posts/landsman-beyer-introduce-bill-to-protect-residents-from-rising-costs-caused-by-ai-data-centers"},
            {"what": "Introduced H.R. 8033, the No Harm Data Centers Act, "
                     "requiring data centers to cover full costs of energy "
                     "demands and infrastructure, mandating environmental "
                     "impact studies, and prohibiting NDAs between data center "
                     "developers and elected officials.",
             "date": "2026-04-09",
             "source": "https://landsman.house.gov/posts/landsman-leads-new-bill-requiring-big-tech-to-pay-for-data-centers-and-no-ndas"},
            {"what": "Introduced the Protecting Communities from Data Center "
                     "Impacts Act, directing EPA to contract with the National "
                     "Academies of Sciences for a study on data center "
                     "environmental impacts (noise, air, water, carbon, e-waste).",
             "date": "2026-07-10",
             "source": "https://landsman.house.gov/posts/landsman-introduced-third-ai-data-center-bill-in-congress"},
        ],
        "as_of": "2026-09-06",
    },
    ("OH", "13", "Emilia Sykes"): {
        "lean": "guardrails",
        "summary": "Ranking Member of the Science Committee's Investigations "
                   "and Oversight Subcommittee. Pushed for consumer protections "
                   "at data center hearings, added data center water study "
                   "provisions to WRDA.",
        "items": [
            {"what": "Unveiled Affordability Agenda policy roadmap including a "
                     "provision to reallocate electric grid costs so consumers "
                     "are protected from price hikes driven by data center "
                     "development.",
             "date": "2026-02-11",
             "source": "https://sykes.house.gov/media/press-releases/rep-sykes-unveils-affordability-agenda-to-address-the-cost-of-living-crisis"},
            {"what": "At House Science Committee hearing on data center "
                     "infrastructure, pressed for consumer protections as Ohio "
                     "hosts 217 data centers (fifth most nationally).",
             "date": "2026-02-24",
             "source": "https://sykes.house.gov/media/press-releases/ranking-member-sykes-presses-for-consumer-protections-as-data-centers-expand-across-ohio"},
            {"what": "Incorporated provisions into the bipartisan Water "
                     "Resources Development Act of 2026 to study data center "
                     "impacts on regional water resources.",
             "date": "2026-07-14",
             "source": "https://sykes.house.gov/media/press-releases/rep-sykes-advances-bipartisan-water-infrastructure-bill-with-key-wins-for-northeast-ohio"},
        ],
        "as_of": "2026-09-06",
    },
    ("OH", "5", "Bob Latta"): {
        "lean": "mixed",
        "summary": "Energy Subcommittee Chairman who championed the Ratepayer "
                   "Protection Act through committee (52-0) but also co-signed "
                   "a letter alleging foreign adversaries are behind data "
                   "center opposition.",
        "items": [
            {"what": "As Energy Subcommittee Chairman, championed H.R. 9340, "
                     "the Ratepayer Protection Act, through subcommittee markup "
                     "to protect families from covering grid upgrade costs "
                     "driven by AI infrastructure.",
             "date": "2026-06-24",
             "source": "https://latta.house.gov/news/documentsingle.aspx?DocumentID=406815"},
            {"what": "Applauded full Energy and Commerce Committee passage of "
                     "H.R. 9340 (52-0), noting Ohio already has large load "
                     "tariffs in place for data centers.",
             "date": "2026-07-21",
             "source": "https://latta.house.gov/news/documentsingle.aspx?DocumentID=406829"},
            {"what": "Co-signed letter (with Guthrie and Joyce) to PCAST and "
                     "FBI Director requesting investigation of alleged Chinese "
                     "Communist Party influence campaigns working to block "
                     "American data center infrastructure.",
             "date": "2026-06-04",
             "source": "https://energycommerce.house.gov/posts/chairmen-guthrie-joyce-and-latta-request-investigation-of-foreign-adversaries-efforts-to-block-american-data-center-buildout"},
        ],
        "as_of": "2026-09-06",
    },
    ("OH", "12", "Troy Balderson"): {
        "lean": "accelerate",
        "summary": "Led the GRID Power Act to fast-track dispatchable power "
                   "through interconnection queues, citing central Ohio's data "
                   "center cluster. Co-introduced the Load Forecasting "
                   "Enhancement Act.",
        "items": [
            {"what": "Led H.R. 1047, the GRID Power Act, directing FERC to let "
                     "grid operators fast-track dispatchable power projects "
                     "through interconnection queues. Cited data center growth "
                     "in central Ohio. Passed the House.",
             "date": "2025-09-18",
             "source": "https://balderson.house.gov/news/documentsingle.aspx?DocumentID=2887"},
            {"what": "At Energy and Commerce hearing, noted his district hosts "
                     "Google, AWS, Meta, QTS, Vantage and others, with signed "
                     "power agreements reaching 5,000 MW by 2030. Questioned "
                     "Eric Schmidt about tech companies' role in bringing new "
                     "generation capacity online.",
             "date": "2025-04-09",
             "source": "https://energycommerce.house.gov/posts/energy-and-commerce-committee-holds-hearing-on-ai-and-american-global-competitiveness"},
            {"what": "Co-introduced H.R. 9332, the Load Forecasting Enhancement "
                     "Act, directing FERC to work with state PUCs on improving "
                     "electric load forecasting as demand surges from AI and "
                     "data centers. Passed Energy Subcommittee.",
             "date": "2026-06-24",
             "source": "https://menendez.house.gov/media/press-releases/menendez-and-balderson-applaud-advancement-of-key-grid-reliability-bill"},
        ],
        "as_of": "2026-09-06",
    },
    ("OH", "6", "Michael Rulli"): {
        "lean": "accelerate",
        "summary": "Supports data center buildout near the Lordstown Stargate "
                   "site while acknowledging constituent opposition; claims "
                   "CCP propaganda is behind local resistance.",
        "items": [
            {"what": "On Fox Business, supported the OpenAI/Nvidia $500B data "
                     "center project but acknowledged 'Most of my constituents "
                     "do not like data centers.' Claimed 'The CCP has "
                     "infiltrated Ohio with propaganda against this' and "
                     "advocated 'Keep them out of the corn fields. Keep them "
                     "out of the neighborhoods.'",
             "date": "2026-08-28",
             "source": "https://www.breitbart.com/clips/2026/08/28/gop-rep-rulli-the-ccp-has-infiltrated-ohio-with-propaganda-against-500b-data-center/"},
        ],
        "as_of": "2026-09-06",
    },
    ("OH", "9", "Marcy Kaptur"): {
        "lean": "guardrails",
        "summary": "Ranking Member of the Appropriations Energy and Water "
                   "Subcommittee. Warned on the House floor that unchecked "
                   "data center growth could raise electricity costs 8% by 2030.",
        "items": [
            {"what": "In House floor remarks on the FY2026 Energy and Water "
                     "Development bill, warned that unchecked data center "
                     "growth could raise average US electricity generation "
                     "costs by roughly 8% by 2030. Cited Ohio families seeing "
                     "10%+ monthly bill increases.",
             "date": "2025-09-03",
             "source": "https://kaptur.house.gov/media-center/press-releases/ranking-member-kaptur-floor-remarks-2026-energy-and-water-development"},
        ],
        "as_of": "2026-09-06",
    },

    # ── 5-state deep dive (GA/NC/TX/TN/WI) — 2026-09-11 ─────────────

    ("GA", "2", "Sanford Bishop"): {
        "lean": "guardrails",
        "summary": "Insists communities weigh tradeoffs carefully and require "
                   "data center operators to provide transparency on water and "
                   "power consumption and deliver community benefits.",
        "items": [
            {"what": "Said south Georgia communities need guardrails, "
                     "transparency on water/power consumption, and community "
                     "benefits before data centers move forward.",
             "date": "2026-07-17",
             "source": "https://www.walb.com/2026/07/17/south-georgia-congressmen-say-data-centers-need-guardrails-before-moving-forward/"},
        ],
        "as_of": "2026-09-11",
    },
    ("GA", "7", "Rich McCormick"): {
        "lean": "accelerate",
        "summary": "Chairman of the House Science, Space, and Technology "
                   "Committee. Chaired hearing on data center infrastructure "
                   "policy, advocated streamlining permitting. Called "
                   "opposition 'misinformation'.",
        "items": [
            {"what": "Chaired hearing 'Powering America's AI Future: Assessing "
                     "Policy Options to Increase Data Center Infrastructure,' "
                     "advocated streamlining permitting for data centers.",
             "date": "2026-02",
             "source": "https://science.house.gov/2026/2/opening-statement-of-chairman-rich-mccormick-at"},
        ],
        "as_of": "2026-09-11",
    },
    ("GA", "8", "Austin Scott"): {
        "lean": "mixed",
        "summary": "Supports domestic data centers as a national security "
                   "priority but demands companies pay their own energy costs "
                   "and use closed-loop cooling.",
        "items": [
            {"what": "Said data centers need to be in the US for national "
                     "security but companies must pay their own energy costs "
                     "and use closed-loop cooling systems.",
             "date": "2026-07-17",
             "source": "https://www.walb.com/2026/07/17/south-georgia-congressmen-say-data-centers-need-guardrails-before-moving-forward/"},
        ],
        "as_of": "2026-09-11",
    },
    ("NC", "4", "Valerie Foushee"): {
        "lean": "mixed",
        "summary": "Raised concerns about data center environmental impacts; "
                   "led bipartisan HR 9372 (data center energy/water "
                   "measurement standards, passed committee 34-1).",
        "items": [
            {"what": "Led HR 9372, the Data Infrastructure Energy Measurement "
                     "and Standards Act, authorizing NIST and DOE to establish "
                     "measurement standards for data center energy and water "
                     "use including AI training; passed House Science "
                     "Committee 34-1.",
             "date": "2026-06-01",
             "source": "https://foushee.house.gov/media/press-releases/rep-foushee-led-generative-ai-labeling-frontier-ai-safety-and-data-center-measures-advance-through-house-science-committee"},
        ],
        "as_of": "2026-09-11",
    },
    ("TX", "4", "Pat Fallon"): {
        "lean": "guardrails",
        "summary": "Supported Governor Abbott's data center pause; expressed "
                   "concerns about ERCOT grid capacity for data centers.",
        "items": [
            {"what": "Praised Abbott's data center moratorium: 'I think it "
                     "was a thoughtful, good step.' Said 'the amount of energy "
                     "needed for these new data centers far exceeds the "
                     "capacity that we currently have.'",
             "date": "2026-08",
             "source": "https://www.cbsnews.com/texas/news/push-back-data-centers-texas-voters-gop-leaders-democratic-challengers/"},
        ],
        "as_of": "2026-09-11",
    },
    ("TN", "2", "Tim Burchett"): {
        "lean": "guardrails",
        "summary": "Publicly broke with Trump on data centers, called for "
                   "local control and military-base siting over residential "
                   "areas.",
        "items": [
            {"what": "Responded to Trump's warning that communities rejecting "
                     "data centers risk becoming 'backwards and poor' by "
                     "saying 'I guess I'm backwards and poor.' Called for "
                     "more local control and suggested putting data centers "
                     "in military installations.",
             "date": "2026-08",
             "source": "https://www.newsweek.com/list-of-republicans-publicly-breaking-with-trump-on-ai-data-centers-12391133"},
        ],
        "as_of": "2026-09-11",
    },
    ("TN", "3", "Chuck Fleischmann"): {
        "lean": "guardrails",
        "summary": "As Energy-Water Appropriations chair, said TVA customers "
                   "should not face surprise rate hikes from data center "
                   "demand.",
        "items": [
            {"what": "As chair of the House Energy and Water Development "
                     "Appropriations Subcommittee, said 'there will be no "
                     "rate increases without going to the people' regarding "
                     "TVA rate changes tied to data center demand.",
             "date": "2026-05-27",
             "source": "https://newschannel9.com/news/local/repfleischmann-says-tva-customers-shouldnt-see-surprise-rate-hikes-tied-to-data-centers-chuck-fleischmann-tva-rates-data-center-electricity-demand-tennessee-tva-ai-power-usage-chattanooga-electricity-rates-data-centers"},
        ],
        "as_of": "2026-09-11",
    },
    ("WI", "2", "Mark Pocan"): {
        "lean": "guardrails",
        "summary": "Called for Congress to regulate AI and data centers; said "
                   "Congress is 'not even crawling' on proper regulation.",
        "items": [
            {"what": "Told Wisconsin Watch that Congress needs 'proper "
                     "regulation that's good on all fronts related to AI' and "
                     "that he feels Congress is 'not even crawling at this "
                     "point.' His district includes 11 Madison-based data "
                     "centers.",
             "date": "2025-12",
             "source": "https://wisconsinwatch.org/2025/12/wisconsin-foxconn-data-center-energy-trump-ai-congress-lawmakers-republican-democrat/"},
        ],
        "as_of": "2026-09-11",
    },
    ("WI", "3", "Derrick Van Orden"): {
        "lean": "mixed",
        "summary": "Said Wisconsinites should not subsidize data center power "
                   "or water, but voted for OBBBA which included federal "
                   "preemption of state/local AI data center regulations.",
        "items": [
            {"what": "Said 'The average Wisconsinite should not have to "
                     "subsidize the power or water for a commercial entity' "
                     "and suggested data centers should either help pay for "
                     "rising utility rates or 'self-power.'",
             "date": "2025-12",
             "source": "https://wisconsinwatch.org/2025/12/wisconsin-foxconn-data-center-energy-trump-ai-congress-lawmakers-republican-democrat/"},
        ],
        "as_of": "2026-09-11",
    },

    # ── FL/MD/PA/IA/CO deep dive, 2026-09-11 ─────────────────────────────
    ("CO", "1", "Melat Kiros"): {
        "lean": "guardrails",
        "summary": "Democratic Socialist who defeated incumbent DeGette; "
                   "supports a nationwide moratorium on data center "
                   "construction.",
        "items": [
            {"what": "Supports a nationwide moratorium on data center "
                     "construction; ran as a critic of unchecked AI "
                     "development.",
             "date": "2026-06-30",
             "source": "https://www.dropsitenews.com/p/aipac-ai-degette-melat-kiros-colorado"},
        ],
        "as_of": "2026-09-11",
    },
    ("CO", "4", "Lauren Boebert"): {
        "lean": "mixed",
        "summary": "Supports local government authority over data center "
                   "siting decisions; disagreed with Trump's "
                   "characterization of DC opponents.",
        "items": [
            {"what": "Stated she won't back Trump's claim that data center "
                     "opponents are 'backwards and poor'; supports local "
                     "control over data center decisions.",
             "date": "2026-09-01",
             "source": "https://www.yahoo.com/news/politics/articles/rep-lauren-boebert-won-t-123549824.html"},
        ],
        "as_of": "2026-09-11",
    },
    ("MD", "1", "Andy Harris"): {
        "lean": "mixed",
        "summary": "Argues data centers should generate their own power "
                   "rather than passing costs to consumers; part of "
                   "Maryland Freedom Caucus energy platform but did not "
                   "join Democratic delegation's FERC letter.",
        "items": [
            {"what": "Argued alongside Maryland Freedom Caucus that data "
                     "centers should generate their own power, not pass "
                     "infrastructure costs to consumers; part of 'Lower "
                     "Electric Bills Now' platform.",
             "date": "2026-02-25",
             "source": "https://foxbaltimore.com/news/local/rep-harris-maryland-freedom-caucus-push-series-of-bills-aimed-to-lower-energy-bills"},
        ],
        "as_of": "2026-09-11",
    },
    ("MD", "2", "Johnny Olszewski"): {
        "lean": "guardrails",
        "summary": "Co-signed Maryland Democratic delegation letter to "
                   "FERC demanding data-center-driven transmission costs "
                   "not be passed to Maryland ratepayers.",
        "items": [
            {"what": "Co-signed Maryland Congressional delegation letter "
                     "to FERC urging revision of PJM cost-allocation "
                     "rules so Maryland consumers do not finance $2B in "
                     "infrastructure built primarily for out-of-state "
                     "data centers.",
             "date": "2026-07-28",
             "source": "https://mcclaindelaney.house.gov/media/press-releases/maryland-democrats-urge-ferc-protect-marylanders-rising-electricity-costs-due"},
        ],
        "as_of": "2026-09-11",
    },
    ("MD", "3", "Sarah Elfreth"): {
        "lean": "guardrails",
        "summary": "Co-signed Maryland Democratic delegation letter to "
                   "FERC demanding data-center-driven transmission costs "
                   "not be passed to Maryland ratepayers.",
        "items": [
            {"what": "Co-signed Maryland Congressional delegation letter "
                     "to FERC urging revision of PJM cost-allocation "
                     "rules so Maryland consumers do not finance $2B in "
                     "infrastructure built primarily for out-of-state "
                     "data centers.",
             "date": "2026-07-28",
             "source": "https://mcclaindelaney.house.gov/media/press-releases/maryland-democrats-urge-ferc-protect-marylanders-rising-electricity-costs-due"},
        ],
        "as_of": "2026-09-11",
    },
    ("MD", "4", "Glenn Ivey"): {
        "lean": "guardrails",
        "summary": "Co-signed Maryland Democratic delegation letter to "
                   "FERC demanding data-center-driven transmission costs "
                   "not be passed to Maryland ratepayers.",
        "items": [
            {"what": "Co-signed Maryland Congressional delegation letter "
                     "to FERC urging revision of PJM cost-allocation "
                     "rules so Maryland consumers do not finance $2B in "
                     "infrastructure built primarily for out-of-state "
                     "data centers.",
             "date": "2026-07-28",
             "source": "https://mcclaindelaney.house.gov/media/press-releases/maryland-democrats-urge-ferc-protect-marylanders-rising-electricity-costs-due"},
        ],
        "as_of": "2026-09-11",
    },
    ("MD", "6", "April McClain Delaney"): {
        "lean": "guardrails",
        "summary": "Led Maryland Democratic delegation letter to FERC "
                   "demanding data-center-driven transmission costs "
                   "not be passed to Maryland ratepayers.",
        "items": [
            {"what": "Led and issued press release for Maryland "
                     "Congressional delegation letter to FERC urging "
                     "revision of PJM cost-allocation rules so Maryland "
                     "consumers do not finance $2B in infrastructure "
                     "built primarily for out-of-state data centers.",
             "date": "2026-07-28",
             "source": "https://mcclaindelaney.house.gov/media/press-releases/maryland-democrats-urge-ferc-protect-marylanders-rising-electricity-costs-due"},
        ],
        "as_of": "2026-09-11",
    },
    ("MD", "8", "Jamie Raskin"): {
        "lean": "guardrails",
        "summary": "Co-signed Maryland Democratic delegation letter to "
                   "FERC demanding data-center-driven transmission costs "
                   "not be passed to Maryland ratepayers.",
        "items": [
            {"what": "Co-signed Maryland Congressional delegation letter "
                     "to FERC urging revision of PJM cost-allocation "
                     "rules so Maryland consumers do not finance $2B in "
                     "infrastructure built primarily for out-of-state "
                     "data centers.",
             "date": "2026-07-28",
             "source": "https://mcclaindelaney.house.gov/media/press-releases/maryland-democrats-urge-ferc-protect-marylanders-rising-electricity-costs-due"},
        ],
        "as_of": "2026-09-11",
    },
    ("PA", "1", "Brian Fitzpatrick"): {
        "lean": "mixed",
        "summary": "Cosponsored the Ratepayer Protection Act and Data "
                   "Center Transparency Act, but initially voted for "
                   "OBBBA which contained AI preemption provision.",
        "items": [
            {"what": "Cosponsored H.R. 9340, the Ratepayer Protection "
                     "Act, directing states and PUCs to consider "
                     "standards for connecting large-load customers so "
                     "data centers, not families, cover new generation "
                     "and transmission costs.",
             "date": "2026-07-22",
             "source": "https://www.inquirer.com/politics/election/bob-harvie-ai-data-centers-stance-tv-ad-20260910.html"},
        ],
        "as_of": "2026-09-11",
    },

    # ── KY/NY/MN deep dive, 2026-09-11 ──────────────────────────────────
    ("KY", "2", "Brett Guthrie"): {
        "lean": "accelerate",
        "summary": "As House Energy and Commerce Chair, champions AI data center "
                   "expansion and energy permitting reform; called for FBI "
                   "investigation of foreign influence in anti-DC opposition.",
        "items": [
            {"what": "Published op-ed in Washington Times arguing for expanded "
                     "energy production to power AI data centers, calling for "
                     "permitting reform and warning about China competition.",
             "date": "2025-03-26",
             "source": "https://energycommerce.house.gov/posts/chairman-guthrie-op-ed-driving-the-energy-future-of-ai-development"},
            {"what": "Signed letter with Reps. Joyce and Latta to PCAST and "
                     "FBI Director requesting investigations into foreign "
                     "influence campaigns targeting AI and data center "
                     "opposition.",
             "date": "2026-06-11",
             "source": "https://bgdailynews.com/2026/06/13/guthrie-calls-for-investigations-into-ai-data-center-opposition/"},
            {"what": "Stated \"We can't have a moratorium that would cripple "
                     "us\" while acknowledging local communities should have "
                     "a say; said data centers must \"pay their own way.\"",
             "date": "2026-06-30",
             "source": "https://www.wnky.com/congressman-brett-guthrie-weighs-in-on-data-center-debate/"},
        ],
        "as_of": "2026-09-11",
    },
    ("KY", "3", "Morgan McGarvey"): {
        "lean": "guardrails",
        "summary": "Declared himself \"absolutely opposed\" to hyperscale data "
                   "centers in Kentucky and sent letter to LG&E opposing Camp "
                   "Ground Road data center and demanding ratepayer protections.",
        "items": [
            {"what": "Sent letter to LG&E President opposing Camp Ground Road "
                     "hyperscale data center in Louisville, demanding ratepayer "
                     "protections; cited 63% increase in electricity demand "
                     "(400 MW).",
             "date": "2026-07-09",
             "source": "https://mcgarvey.house.gov/media/press-releases/rep-mcgarvey-opposes-camp-ground-road-data-center-in-letter-to-lgande-dont-raise-louisvilles-rates-to-pay-for-it"},
            {"what": "Declared himself \"absolutely opposed\" to in-state "
                     "hyperscale data centers at Louisville town hall on AI "
                     "data centers; said residents should control what gets "
                     "built in their community.",
             "date": "2026-07-09",
             "source": "https://www.lpm.org/news/2026-07-09/kentucky-congressman-absolutely-opposed-to-in-state-hyperscale-data-centers"},
        ],
        "as_of": "2026-09-11",
    },
    ("NY", "17", "Mike Lawler"): {
        "lean": "accelerate",
        "summary": "Opposes Gov. Hochul's data center moratorium, arguing it "
                   "stifles innovation and drives businesses to other states.",
        "items": [
            {"what": "Criticized Hochul's Executive Order 62 data center "
                     "moratorium on Fox Business, saying \"What she is saying "
                     "is, don't come here. Go do your business elsewhere\" and "
                     "arguing the pause harms NY's business climate.",
             "date": "2026-08-18",
             "source": "https://www.foxbusiness.com/media/new-york-republican-congressman-rips-hochul-policies-sending-businesses-dont-come-here-message"},
        ],
        "as_of": "2026-09-11",
    },
    ("MN", "6", "Tom Emmer"): {
        "lean": "accelerate",
        "summary": "Strongly backs data center buildout citing AI competition "
                   "with China; as House Majority Whip, supported bringing "
                   "Ratepayer Protection Act to floor vote.",
        "items": [
            {"what": "As House Majority Whip, supported bringing bipartisan "
                     "Ratepayer Protection Act (HR 9340) to floor vote, "
                     "requiring data centers to cover full incremental "
                     "infrastructure costs; stated \"I'm a true believer in "
                     "local control.\"",
             "date": "2026-08-01",
             "source": "https://www.polialert.com/political-news/house-gop-to-vote-on-bill-targeting-data-center-power-costs/"},
            {"what": "Tweeted support for Trump's pro-data center position, "
                     "saying China and U.S. adversaries \"would love it if "
                     "the United States was asleep at the wheel and stopped "
                     "innovating and developing AI.\"",
             "date": "2026-09-01",
             "source": "https://www.minnpost.com/national/washington/2026/09/minnesota-gop-lawmakers-grapple-with-data-centers-as-republican-voters-turn-against-the-projects/"},
        ],
        "as_of": "2026-09-11",
    },
    ("MN", "1", "Brad Finstad"): {
        "lean": "mixed",
        "summary": "Supports data centers for economic and national security "
                   "value but emphasizes local control and corporate "
                   "transparency about environmental impacts.",
        "items": [
            {"what": "Said data centers \"can play an important role in our "
                     "economic future and national security, but the "
                     "decision...should be made by the people and local "
                     "leaders who know their communities best, not handed "
                     "down by Washington\"; emphasized need for corporate "
                     "transparency.",
             "date": "2026-09-01",
             "source": "https://www.minnpost.com/national/washington/2026/09/minnesota-gop-lawmakers-grapple-with-data-centers-as-republican-voters-turn-against-the-projects/"},
        ],
        "as_of": "2026-09-11",
    },
    ("MN", "8", "Pete Stauber"): {
        "lean": "mixed",
        "summary": "Set four conditions for data center support: local "
                   "community input, no rate increases, no tax increases, "
                   "and projects must use their own water and energy.",
        "items": [
            {"what": "Stated four conditions for supporting data center "
                     "projects: \"The local community's got to have input. "
                     "It can't increase rates, or taxes, and they have to "
                     "use their own water and energy.\"",
             "date": "2026-08-01",
             "source": "https://www.minnpost.com/national/washington/2026/09/minnesota-gop-lawmakers-grapple-with-data-centers-as-republican-voters-turn-against-the-projects/"},
        ],
        "as_of": "2026-09-11",
    },
    # ── Batch 4 deep dive — OR, AL, IL, OK — 2026-09-11 ─────────────────
    ("OR", "6", "Andrea Salinas"): {
        "lean": "guardrails",
        "summary": "Introduced the Data Center Community Reinvestment Act to "
                   "tax data center electricity use at 1 cent/kWh and reinvest "
                   "$1.76B/year into housing, conservation, clean energy, and "
                   "infrastructure",
        "items": [
            {"what": "Introduced Data Center Community Reinvestment Act "
                     "establishing 1-cent-per-kWh excise tax on data center "
                     "electricity consumption (>1 MW capacity), directing "
                     "$1.76B/year to Land and Water Conservation Fund, Housing "
                     "Trust Fund, Superfund, Highway Trust Fund, and Energy "
                     "Technology Trust Fund",
             "date": "2026-08-14",
             "source": "https://salinas.house.gov/media/press-releases/rep-salinas-introduces-bill-tax-data-centers-reinvest-housing-conservation-and"},
        ],
        "as_of": "2026-09-11",
    },
    ("OR", "2", "Cliff Bentz"): {
        "lean": "accelerate",
        "summary": "Sponsored H.R. 655 to transfer 150 acres of Mt. Hood "
                   "National Forest land to The Dalles to expand water "
                   "reservoir capacity, which critics say primarily benefits "
                   "Google's data centers that use 40% of the city's water",
        "items": [
            {"what": "Sponsored and passed H.R. 655 (The Dalles Watershed "
                     "Development Act) through the House, transferring 150 "
                     "acres from Mt. Hood National Forest to The Dalles to "
                     "triple reservoir capacity; said he did not ask the city "
                     "how the water would be used",
             "date": "2025-12-09",
             "source": "https://bentz.house.gov/media/press-releases/congressman-bentz-s-bill-to-expand-the-city-of-the-dalles-water-passed-in-us-house-of-representatives"},
        ],
        "as_of": "2026-09-11",
    },
    ("OR", "4", "Val Hoyle"): {
        "lean": "mixed",
        "summary": "Endorsed by pro-AI industry super PAC Leading the Future; "
                   "initially distanced herself saying AI must be regulated, "
                   "then backtracked to support industry engagement with "
                   "worker protections",
        "items": [
            {"what": "Endorsed by Leading the Future (pro-AI industry super "
                     "PAC); initially distanced herself saying 'AI must be "
                     "regulated so that it does not harm labor or people,' "
                     "then revised position to support engagement with "
                     "industry while advocating federal regulations and "
                     "worker protections",
             "date": "2026-05-08",
             "source": "https://www.transformernews.ai/p/an-oregon-congresswoman-distanced-val-hoyle"},
        ],
        "as_of": "2026-09-11",
    },
    ("AL", "7", "Terri Sewell"): {
        "lean": "guardrails",
        "summary": "Cosponsored the AI Data Center Moratorium Act (HR 9442) "
                   "calling for a pause on new data center construction until "
                   "federal standards protect communities",
        "items": [
            {"what": "Cosponsored AI Data Center Moratorium Act (HR 9442) to "
                     "temporarily halt data center construction until federal "
                     "guardrails are established; said 'Responsible innovation "
                     "and community protection are not competing goals'",
             "date": "2026-07-22",
             "source": "https://aldailynews.com/sewell-wants-to-stop-new-data-centers-until-guardrails-are-implemented/"},
        ],
        "as_of": "2026-09-11",
    },
    ("AL", "2", "Shomari Figures"): {
        "lean": "guardrails",
        "summary": "Sided with Lowndes County residents opposing a proposed "
                   "1,050-acre data center, demanding community consent for "
                   "data center siting",
        "items": [
            {"what": "Statement at Lowndes County event opposing proposed "
                     "data center: 'I'm with the people of Lowndes County'; "
                     "demands community consent for data center siting",
             "date": "2026-08-01",
             "source": "https://www.alabamagazette.com/story/2026/08/01/news/where-alabamas-major-public-officials-stand-on-hyperscale-ai-data-centers/12100.html"},
        ],
        "as_of": "2026-09-11",
    },
    ("IL", "6", "Sean Casten"): {
        "lean": "guardrails",
        "summary": "Co-led the Energy Bills Relief Act requiring data centers "
                   "to pay their own energy infrastructure costs rather than "
                   "passing expenses to residential ratepayers",
        "items": [
            {"what": "Co-introduced the Energy Bills Relief Act with Rep. "
                     "Mike Levin, requiring data centers to pay their own "
                     "energy infrastructure costs",
             "date": "2026-03-18",
             "source": "https://casten.house.gov/media/press-releases/ebra"},
        ],
        "as_of": "2026-09-11",
    },
    ("OK", "5", "Stephanie Bice"): {
        "lean": "mixed",
        "summary": "Acknowledged data center benefits but emphasized local "
                   "communities must have a voice; applauded state ratepayer "
                   "protection law",
        "items": [
            {"what": "Statement responding to President's comments on data "
                     "centers: 'it is vital that local communities have a "
                     "voice in the decisions on proposed data centers'; "
                     "applauded Oklahoma legislature for passing ratepayer "
                     "protection and groundwater laws",
             "date": "2026-08-31",
             "source": "https://kfor.com/news/local/president-comments-on-data-centers-in-usa/"},
        ],
        "as_of": "2026-09-11",
    },
    ("OK", "2", "Josh Brecheen"): {
        "lean": "guardrails",
        "summary": "Co-sponsors HR 9019 requiring DOE to report on data "
                   "center electricity and water usage; told town hall that "
                   "operators must not drive up electricity costs",
        "items": [
            {"what": "Town hall statement that data center operators 'have to "
                     "make sure that they are not driving up people's "
                     "electricity costs'; co-sponsors HR 9019 requiring "
                     "Secretary of Energy to report on data center electricity "
                     "and water usage",
             "date": "2026-08-27",
             "source": "https://www.kjrh.com/news/local-news/brecheen-gives-views-on-data-centers-smelter-election-denial-in-mcalester"},
        ],
        "as_of": "2026-09-11",
    },
    # ── Batch 5 deep dive — KS, AR, ME, UT, NH — 2026-09-11 ─────────────
    ("KS", "3", "Sharice Davids"): {
        "lean": "guardrails",
        "summary": "No data center should move forward if it raises costs, "
                   "wastes water, or shifts the burden onto Kansas communities",
        "items": [
            {"what": "Statement: 'no data center should move forward if it "
                     "raises electricity costs for families, wastes our limited "
                     "water resources, or shifts the burden onto Kansas "
                     "communities'",
             "date": "2026-09-11",
             "source": "https://www.kshb.com/news/local-news/kansas/johnson-county/voters-guide-kansas-political-candidates-stances-on-data-center-development"},
        ],
        "as_of": "2026-09-11",
    },
    ("KS", "1", "Lauren Reinhold"): {
        "lean": "guardrails",
        "summary": "Supports community-approved projects with transparency, "
                   "opposes tax breaks for data centers",
        "items": [
            {"what": "Statement supporting community-approved projects with "
                     "transparency and opposing tax breaks for data centers; "
                     "'there is no one-size-fits-all approach for this district'",
             "date": "2026-09-11",
             "source": "https://www.kshb.com/news/local-news/kansas/johnson-county/voters-guide-kansas-political-candidates-stances-on-data-center-development"},
        ],
        "as_of": "2026-09-11",
    },
    ("KS", "2", "Derek Schmidt"): {
        "lean": "mixed",
        "summary": "Conditionally supportive; advises communities that "
                   "developers should not get tax abatements and should use "
                   "new power sources and closed water systems",
        "items": [
            {"what": "Town hall advice: data center developers should not "
                     "require tax abatements, should source power from new "
                     "sources to avoid raising local utility costs, and modern "
                     "data centers can use closed systems with minimal water",
             "date": "2026-06-10",
             "source": "https://ransonfinancial.com/2026/06/10/three-tips-for-kansas-communities-on-data-centers/"},
        ],
        "as_of": "2026-09-11",
    },
    ("AR", "4", "Bruce Westerman"): {
        "lean": "accelerate",
        "summary": "Frames data centers as crucial for US-China AI "
                   "competition; downplays environmental concerns",
        "items": [
            {"what": "Town hall promoting data centers as 'crucial to America "
                     "winning the cold war with China on AI tech'; dismissed "
                     "water concerns, argued large loads could lower "
                     "residential electricity prices",
             "date": "2026-09-01",
             "source": "https://hopeprescott.com/2026/09/01/data-centers-crucial-to-america-winning-the-cold-war-with-china-on-ai-tech-according-to-congressman-westerman/"},
        ],
        "as_of": "2026-09-11",
    },
    ("ME", "2", "Paul LePage"): {
        "lean": "accelerate",
        "summary": "Self-described 'big, big fan' of data centers; says they "
                   "create jobs and should generate their own power",
        "items": [
            {"what": "Called himself a 'big, big fan of data centers' at "
                     "former mill site; said they will create jobs and should "
                     "generate their own power",
             "date": "2026-08-24",
             "source": "https://www.bangordailynews.com/2026/08/24/politics/elections/paul-lepage-big-fan-data-centers-joam40zk0w/"},
        ],
        "as_of": "2026-09-11",
    },
    ("ME", "2", "Matthew Dunlap"): {
        "lean": "guardrails",
        "summary": "Favors benchmarks for worker benefits, ratepayer "
                   "protection, and community benefits from data centers",
        "items": [
            {"what": "Campaign warned 'if we don't approach these projects "
                     "deliberately they will jack up energy prices'; favors "
                     "developing benchmarks and standards for worker benefits, "
                     "ratepayer impact, and community benefits",
             "date": "2026-08-24",
             "source": "https://www.bangordailynews.com/2026/08/24/politics/elections/paul-lepage-big-fan-data-centers-joam40zk0w/"},
        ],
        "as_of": "2026-09-11",
    },
    ("ME", "1", "Chellie Pingree"): {
        "lean": "guardrails",
        "summary": "Believes Congress should assess environmental and "
                   "consumer impacts and put strong protections in place",
        "items": [
            {"what": "Spokesperson said she believes Congress has a "
                     "responsibility to assess environmental and consumer "
                     "impacts of data center and AI expansion and put 'strong, "
                     "science-based protections in place'",
             "date": "2025-12-08",
             "source": "https://www.mainepublic.org/climate/2025-12-08/maine-groups-join-call-for-u-s-data-center-moratorium"},
        ],
        "as_of": "2026-09-11",
    },
    ("UT", "1", "Ben McAdams"): {
        "lean": "guardrails",
        "summary": "Opposes Box Elder Stratos project; calls for water "
                   "stewardship and environmental standards",
        "items": [
            {"what": "Posted opposing Stratos Project: 'Utah should welcome "
                     "technology investment only when it aligns with our "
                     "values: water stewardship, Great Salt Lake restoration, "
                     "clean energy, transparency, public accountability'",
             "date": "2026-05-01",
             "source": "https://x.com/BenMcAdams/status/2052173399594528777"},
            {"what": "UT-1 primary debate: opposed Stratos Project; called "
                     "for federal standards to ensure Americans benefit from "
                     "AI transformation",
             "date": "2026-05-27",
             "source": "https://www.kuer.org/politics-government/2026-05-27/1st-district-debate-zeroes-in-on-utah-hot-topics-like-ai-data-centers-and-housing"},
        ],
        "as_of": "2026-09-11",
    },
    ("UT", "2", "Blake Moore"): {
        "lean": "mixed",
        "summary": "Introduced bill requiring study of AI data center "
                   "impacts in rural America while supporting Utah as tech hub",
        "items": [
            {"what": "Introduced bipartisan 'Unleashing Low-Cost Rural AI "
                     "Act' requiring DOE, Interior, and Agriculture to study "
                     "how AI data center expansions impact rural America — "
                     "energy supply, reliability, consumer costs, and "
                     "infrastructure",
             "date": "2025-09-16",
             "source": "https://blakemoore.house.gov/media/press-releases/representatives-moore-costa-introduce-legislation-to-study-impact-of-artificial-intelligence-in-rural-america"},
        ],
        "as_of": "2026-09-11",
    },
    ("NH", "1", "Stefany Shaheen"): {
        "lean": "guardrails",
        "summary": "Strongly supports moratorium; municipalities not yet "
                   "prepared for data center complexity",
        "items": [
            {"what": "Stated 'I feel very strongly we need a moratorium. Our "
                     "municipalities are not yet prepared to handle the "
                     "complexity of what these kinds of projects could mean "
                     "for their communities'",
             "date": "2026-09-07",
             "source": "https://spectrumnews1.com/ma/worcester/news/2026/09/08/new-hampshire-data-centers-shaheen-pappas-ayotte"},
        ],
        "as_of": "2026-09-11",
    },
    ("NH", "2", "Maggie Goodlander"): {
        "lean": "guardrails",
        "summary": "Communities must have ultimate say in data center siting; "
                   "corporations must bear costs, not taxpayers",
        "items": [
            {"what": "Debate statement: communities seeing '200%+ energy "
                     "price increases'; 'people and communities have got to "
                     "have the ultimate say'; called for transparency and "
                     "that corporations should bear costs",
             "date": "2026-09-03",
             "source": "https://indepthnh.org/2026/09/03/congressional-district-2-democratic-primary-candidates-debate-housing-immigration-and-data-centers/"},
        ],
        "as_of": "2026-09-11",
    },
    ("NH", "2", "Paige Beauchemin"): {
        "lean": "guardrails",
        "summary": "Called to stop data center construction until regulatory "
                   "legislation is introduced",
        "items": [
            {"what": "Debate statement: 'stop the construction of any data "
                     "centers until legislation can be introduced to regulate "
                     "the issue accordingly'; emphasized environmental impact "
                     "studies and local control",
             "date": "2026-09-03",
             "source": "https://indepthnh.org/2026/09/03/congressional-district-2-democratic-primary-candidates-debate-housing-immigration-and-data-centers/"},
        ],
        "as_of": "2026-09-11",
    },
    ("NH", "2", "Lily Tang Williams"): {
        "lean": "mixed",
        "summary": "Opposes government subsidies but supports private data "
                   "center development with local control",
        "items": [
            {"what": "Debate statement: 'no government perks, credits and "
                     "taxpayer dollars should be involved. If a private "
                     "company wants to come here, build data centers, then "
                     "they need to respect our local control and address our "
                     "concerns of environmental impact and electricity costs'",
             "date": "2026-09-01",
             "source": "https://indepthnh.org/2026/09/01/orlando-stakes-position-as-working-class-alternative-to-tang-williams-in-nh-02-gop-debate/"},
        ],
        "as_of": "2026-09-11",
    },

    # ── Batch 6 deep dive — CT, NV, NM, DE, NE — 2026-09-11 ─────────────
    ("CT", "1", "Luke Bronin"): {
        "lean": "guardrails",
        "summary": "Campaigned on sensible AI regulation and guardrails; "
                   "called for data center developers to pay their fair share",
        "items": [
            {"what": "Primary victory speech called for 'sensible artificial "
                     "intelligence regulation'; platform commits to AI "
                     "guardrails against algorithmic addiction and AI operating "
                     "without human oversight",
             "date": "2026-08-13",
             "source": "https://www.techtimes.com/articles/324305/20260813/bronin-routs-larson-21-points-connecticut-primary-adds-ai-guardrails-voice-congress.htm"},
            {"what": "Called for regulation requiring data center developers "
                     "to pay their fair share",
             "date": "2026-05",
             "source": "https://prospect.org/2026/05/21/meet-connecticuts-billionaire-backed-dark-money-democrat-bronin-larson-congress/"},
        ],
        "as_of": "2026-09-11",
    },
    ("NV", "1", "Dina Titus"): {
        "lean": "guardrails",
        "summary": "Multiple actions demanding BLM transparency on data "
                   "center permits, called for tax abatement freeze, and "
                   "fought federal land data center approvals",
        "items": [
            {"what": "Letter to BLM demanding robust public consultation and "
                     "transparency for data center permits on public lands; "
                     "criticized switch from solar to data center without "
                     "public review",
             "date": "2026-07-08",
             "source": "https://titus.house.gov/news/documentsingle.aspx?DocumentID=5916"},
            {"what": "Called on Gov. Lombardo to freeze all data center tax "
                     "breaks for projects on federal land until 2027 "
                     "Legislature can act; cited $225.6M in sales/use tax "
                     "breaks and $13.3M in property tax breaks",
             "date": "2026-07-23",
             "source": "https://titus.house.gov/news/documentsingle.aspx?DocumentID=5926"},
            {"what": "NV Independent survey: favors local community input "
                     "before federal land use; supports full environmental "
                     "permitting with water consideration and public hearings",
             "date": "2026-08-01",
             "source": "https://thenevadaindependent.com/article/what-do-nevadas-congressional-candidates-think-about-data-centers"},
        ],
        "as_of": "2026-09-11",
    },
    ("NV", "1", "Carrie Buck"): {
        "lean": "accelerate",
        "summary": "Wants to make it easier to build AI energy and "
                   "infrastructure",
        "items": [
            {"what": "NV Independent survey: federal government should 'make "
                     "it easier to build the energy and infrastructure America "
                     "needs to lead in AI'",
             "date": "2026-08-01",
             "source": "https://thenevadaindependent.com/article/what-do-nevadas-congressional-candidates-think-about-data-centers"},
        ],
        "as_of": "2026-09-11",
    },
    ("NV", "2", "Teresa Benitez-Thompson"): {
        "lean": "guardrails",
        "summary": "Supports local control over data center regulation; "
                   "opposes federal preemption of state/local authority",
        "items": [
            {"what": "NV Independent survey: does not want federal actions to "
                     "prevent state or local governments from taking their own "
                     "regulatory action on data centers",
             "date": "2026-08-01",
             "source": "https://thenevadaindependent.com/article/what-do-nevadas-congressional-candidates-think-about-data-centers"},
        ],
        "as_of": "2026-09-11",
    },
    ("NV", "2", "David Flippo"): {
        "lean": "mixed",
        "summary": "Opposes tax abatements for data centers; supports local "
                   "decision-making but would support federal involvement for "
                   "national security",
        "items": [
            {"what": "NV Independent survey: 'The best decisions are made at "
                     "the most local level possible.' Opposes tax abatements; "
                     "would support federal involvement only for national "
                     "security protection",
             "date": "2026-08-01",
             "source": "https://thenevadaindependent.com/article/what-do-nevadas-congressional-candidates-think-about-data-centers"},
        ],
        "as_of": "2026-09-11",
    },
    ("NV", "3", "Susie Lee"): {
        "lean": "mixed",
        "summary": "Toured Switch AI factory approvingly; opposes federal "
                   "pause on development but supports disclosure requirements",
        "items": [
            {"what": "Toured Switch AI factory in Las Vegas with House "
                     "Democratic Leader Jeffries; praised Switch for 'bringing "
                     "the cutting edge of AI innovation right here to southern "
                     "Nevada' and creating good-paying jobs",
             "date": "2025-08-29",
             "source": "https://susielee.house.gov/media/press-releases/icymi-congresswoman-lee-leader-jeffries-tour-new-cutting-edge-ai-factory-will"},
            {"what": "NV Independent survey: supports water consumption "
                     "disclosure and energy efficiency standards; opposes "
                     "blanket federal pause on development",
             "date": "2026-08-01",
             "source": "https://thenevadaindependent.com/article/what-do-nevadas-congressional-candidates-think-about-data-centers"},
        ],
        "as_of": "2026-09-11",
    },
    ("NV", "3", "Martin O'Donnell"): {
        "lean": "guardrails",
        "summary": "Supports legislation ensuring local communities are not "
                   "negatively affected; backs water usage disclosure",
        "items": [
            {"what": "NV Independent survey: supports legislation ensuring "
                     "local communities are not negatively affected by data "
                     "centers; backs water usage disclosure requirements",
             "date": "2026-08-01",
             "source": "https://thenevadaindependent.com/article/what-do-nevadas-congressional-candidates-think-about-data-centers"},
        ],
        "as_of": "2026-09-11",
    },
    ("NV", "4", "Steven Horsford"): {
        "lean": "mixed",
        "summary": "Partners with OpenAI on AI workforce training and "
                   "opposes moratorium but supports disclosure requirements "
                   "and worker protections",
        "items": [
            {"what": "Joined OpenAI and Rep. Khanna at College of Southern "
                     "Nevada for AI workforce training; helped secure nearly "
                     "$7M for CSN Westside Education and Training Center",
             "date": "2026-04-24",
             "source": "https://horsford.house.gov/media/press-releases/rep-horsford-joins-openai-rep-ro-khanna-and-college-of-southern-nevada-csn-to-expand-ai-workforce-training-in-north-las-vegas"},
            {"what": "NV Independent survey: supports federal disclosure "
                     "standards for energy and water use; states should be "
                     "able to go further than federal baselines; opposes "
                     "blanket moratorium",
             "date": "2026-08-01",
             "source": "https://thenevadaindependent.com/article/what-do-nevadas-congressional-candidates-think-about-data-centers"},
            {"what": "Joined Rep. Khanna and Las Vegas unions to discuss "
                     "AI/automation threats to workers; advocated advance "
                     "notice, training, and collective bargaining as "
                     "accountability tool",
             "date": "2026-08-20",
             "source": "https://lasvegassun.com/news/2026/aug/20/las-vegas-union-workers-reps-ro-khanna-and-steven/"},
        ],
        "as_of": "2026-09-11",
    },
    ("NV", "4", "Cody Whipple"): {
        "lean": "guardrails",
        "summary": "Supports common-sense frameworks safeguarding natural "
                   "resources; calls data centers a national security issue",
        "items": [
            {"what": "NV Independent survey: supports 'common-sense "
                     "frameworks that safeguard Nevada's natural resources "
                     "while fostering technological innovation'; calls data "
                     "centers national security issue; wants federal standards "
                     "bringing water, agriculture, and tech officials together",
             "date": "2026-08-01",
             "source": "https://thenevadaindependent.com/article/what-do-nevadas-congressional-candidates-think-about-data-centers"},
        ],
        "as_of": "2026-09-11",
    },
    ("NM", "1", "Melanie Stansbury"): {
        "lean": "guardrails",
        "summary": "Demanded water accountability for Project Jupiter from "
                   "five NM state officials",
        "items": [
            {"what": "Formal letter to five NM state officials demanding "
                     "written answers on Project Jupiter's water use, water "
                     "rights, permits, and Rio Grande Compact compliance; "
                     "called it 'an important test case for how New Mexico "
                     "evaluates major industrial water users'",
             "date": "2026-08-24",
             "source": "https://stansbury.house.gov/media/press-releases/rep-stansbury-demands-answers-project-jupiters-water-use-new-mexico-supreme"},
        ],
        "as_of": "2026-09-11",
    },
    ("NM", "2", "Gabe Vasquez"): {
        "lean": "guardrails",
        "summary": "Called for Socorro County moratorium; co-sponsored FAIR "
                   "Data Act and Data Center Water and Energy Transparency Act",
        "items": [
            {"what": "Publicly called on Socorro County commissioners to "
                     "approve temporary data center moratorium before their "
                     "June vote",
             "date": "2026-06-09",
             "source": "https://sourcenm.com/briefs/us-rep-vasquez-calls-for-new-mexico-county-to-approve-data-center-moratorium/"},
            {"what": "Co-sponsored FAIR Data Act (H.R. 9655): prevents data "
                     "center projects from raising energy costs for "
                     "residential customers and small businesses",
             "date": "2026-08-25",
             "source": "https://vasquez.house.gov/media/press-releases/rep-gabe-vasquez-demands-accountability-data-center-developers-reiterates-new"},
            {"what": "Co-sponsored Data Center Water and Energy Transparency "
                     "Act (H.R. 9825): mandates disclosure of energy and water "
                     "usage with fines up to $20,000/day for non-compliance",
             "date": "2026-08-25",
             "source": "https://vasquez.house.gov/media/press-releases/rep-gabe-vasquez-demands-accountability-data-center-developers-reiterates-new"},
        ],
        "as_of": "2026-09-11",
    },
    ("DE", "AL", "Sarah McBride"): {
        "lean": "guardrails",
        "summary": "Pressed Trump administration on data center community "
                   "impacts; co-sponsored Liquid Cooling for AI Act; secured "
                   "$5M for cooling technology",
        "items": [
            {"what": "Pressed Trump administration at Science, Space, and "
                     "Technology hearing on data center community impacts; "
                     "raised concerns about strain on energy and water supply "
                     "and utility costs",
             "date": "2026-01-14",
             "source": "https://mcbride.house.gov/media/press-releases/rep-mcbride-presses-trump-administration-data-center-impacts-secures"},
            {"what": "Co-sponsored H.R. 5332, Liquid Cooling for AI Act: "
                     "bipartisan bill directing GAO to assess liquid cooling "
                     "for AI compute and HPC facilities",
             "date": "2025-09-15",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/5332/cosponsors"},
            {"what": "Secured $5M for Chemours liquid cooling technology — "
                     "two-phase immersion cooling that can reduce water use, "
                     "cut cooling energy by up to 90%, and shrink footprints "
                     "by up to 60%",
             "date": "2025-07-01",
             "source": "https://mcbride.house.gov/media/press-releases/rep-mcbride-advances-5-million-delaware-innovation-and-chemours-house"},
        ],
        "as_of": "2026-09-11",
    },
    ("NE", "1", "Mike Flood"): {
        "lean": "accelerate",
        "summary": "Pro-data center at Nebraska energy summit; frames AI as "
                   "requiring legal accountability but supports infrastructure",
        "items": [
            {"what": "At Nebraska energy summit, advocated for data centers "
                     "as needed infrastructure; framed AI as requiring legal "
                     "accountability — companies cannot escape discrimination "
                     "laws by claiming 'that was in our large language model'",
             "date": "2026-08-12",
             "source": "https://nebraskapublicmedia.org/en/news/news-articles/nebraskas-federal-representatives-talk-energy-chinese-competition-and-iran-at-summit/"},
        ],
        "as_of": "2026-09-11",
    },
    ("NE", "1", "Chris Backemeyer"): {
        "lean": "accelerate",
        "summary": "Supports domestic data center construction framed as "
                   "national security priority",
        "items": [
            {"what": "Expressed alarm at Saudi Arabia and UAE offering to host "
                     "US data centers: 'That scares the bejesus out of me'; "
                     "supports building data centers domestically",
             "date": "2026-08-26",
             "source": "https://www.nbcdfw.com/news/national-international/left-and-right-oppose-artificial-intelligence-data-centers/4067951/"},
        ],
        "as_of": "2026-09-11",
    },
    ("NE", "3", "Adrian Smith"): {
        "lean": "accelerate",
        "summary": "Pro-AI efficiency; advocates for data centers despite "
                   "county moratorium wave",
        "items": [
            {"what": "At Nebraska energy summit: 'The efficiencies that can "
                     "be achieved already with AI, it's amazing' and 'We "
                     "should celebrate how much better lives can be with more "
                     "economic efficiency'; advocated for data centers despite "
                     "county moratorium wave",
             "date": "2026-08-12",
             "source": "https://nebraskapublicmedia.org/en/news/news-articles/nebraskas-federal-representatives-talk-energy-chinese-competition-and-iran-at-summit/"},
        ],
        "as_of": "2026-09-11",
    },

    # ── H.R. 9442, AI Data Center Moratorium Act + research batch 2026-09-12 ─
    ("NY", "14", "Alexandria Ocasio-Cortez"): {
        "lean": "guardrails",
        "summary": "Introduced H.R. 9442, the AI Data Center Moratorium Act — "
                   "the House companion to Sanders' S.4214 — halting new data "
                   "center construction until Congress enacts community "
                   "safeguards.",
        "items": [
            {"what": "Introduced H.R. 9442, the Artificial Intelligence Data "
                     "Center Moratorium Act, which would halt construction or "
                     "expansion of AI data centers until Congress passes "
                     "safeguards and 'expressly terminates' the moratorium.",
             "date": "2026-06-24",
             "source": "https://ocasio-cortez.house.gov/media/press-releases/ocasio-cortez-introduces-house-version-ai-data-center-moratorium-act"},
        ],
        "as_of": "2026-09-12",
    },
    ("IN", "7", "André Carson"): {
        "lean": "guardrails",
        "summary": "Introduced the AI Data Center Site Selection Transparency "
                   "Act and cosponsored the moratorium bill.",
        "items": [
            {"what": "Introduced H.R. 8488, the AI Data Center Site Selection "
                     "Transparency Act, requiring developers to disclose "
                     "proposed locations at least 180 days before development, "
                     "including electricity use, water consumption, and "
                     "environmental impacts backed by independent analysis.",
             "date": "2026-04-23",
             "source": "https://carson.house.gov/media/press-releases/carson-introduces-data-center-moratorium-bill"},
            {"what": "Original cosponsor of H.R. 9442, the AI Data Center "
                     "Moratorium Act.",
             "date": "2026-06-24",
             "source": "https://ocasio-cortez.house.gov/media/press-releases/ocasio-cortez-introduces-house-version-ai-data-center-moratorium-act"},
        ],
        "as_of": "2026-09-12",
    },
    # Bonnie Watson Coleman (NJ-12): retiring, not on 2026 ballot.
    ("IL", "14", "Lauren Underwood"): {
        "lean": "guardrails",
        "summary": "Introduced the Data Center Water and Energy Transparency "
                   "Act requiring operators to report energy and water use to "
                   "states, EPA, and federal agencies.",
        "items": [
            {"what": "Introduced H.R. 9825, the Data Center Water and Energy "
                     "Transparency Act, requiring data center operators to "
                     "report energy and water use to states, EPA, and the "
                     "Secretaries of Energy and Agriculture.",
             "date": "2026-07-22",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/9825/all-info"},
        ],
        "as_of": "2026-09-12",
    },
    ("NJ", "8", "Rob Menendez"): {
        "lean": "guardrails",
        "summary": "Co-introduced the PRICE Act (75% renewable by 2035, 100% "
                   "by 2040 for data centers) and the Data Center "
                   "Transparency Act mandating EPA and EIA data collection.",
        "items": [
            {"what": "Co-introduced the PRICE Act and Data Center Transparency "
                     "Act with Rep. Casar. The PRICE Act requires data centers "
                     "to generate their own electricity (75% renewable by "
                     "2035, 100% by 2040). The Transparency Act mandates EPA "
                     "quarterly environmental data and EIA semi-annual energy "
                     "data collection.",
             "date": "2026-01-08",
             "source": "https://menendez.house.gov/media/press-releases/-menendez-casar-introduce-groundbreaking-legislation-to-protect-americans-from-financial-and-environmental-impacts-of-ai-data-centers"},
            {"what": "Cosponsored H.R. 7858, the Data Center Community "
                     "Impact Act.",
             "date": "2026-03-06",
             "source": "https://watsoncoleman.house.gov/newsroom/press-releases/rep-watson-coleman-introduces-bill-to-study-impact-of-ai-data-centers-on-local-communities"},
        ],
        "as_of": "2026-09-12",
    },
    ("TX", "37", "Greg Casar"): {
        "lean": "guardrails",
        "summary": "Co-introduced the PRICE Act and Data Center Transparency "
                   "Act, arguing data center projects should be blocked if "
                   "they raise electricity bills or harm communities.",
        "items": [
            {"what": "Co-introduced the PRICE Act and Data Center Transparency "
                     "Act with Rep. Menendez. Argues data center projects "
                     "should be blocked if they raise electricity bills or "
                     "harm communities.",
             "date": "2026-01-08",
             "source": "https://menendez.house.gov/media/press-releases/-menendez-casar-introduce-groundbreaking-legislation-to-protect-americans-from-financial-and-environmental-impacts-of-ai-data-centers"},
        ],
        "as_of": "2026-09-12",
    },
    ("CA", "15", "Kevin Mullin"): {
        "lean": "guardrails",
        "summary": "Led a 20-member congressional letter to FERC, Edison "
                   "Electric Institute, and the Data Center Coalition on "
                   "data center energy cost pass-throughs to consumers.",
        "items": [
            {"what": "Led a group of 20 House members in a letter to FERC, "
                     "Edison Electric Institute, and the Data Center "
                     "Coalition expressing concern that data center energy "
                     "costs are being passed onto consumers and requesting "
                     "information on consumer protections.",
             "date": "2025-10-28",
             "source": "https://kevinmullin.house.gov/2025/10/28/rep-mullin-leads-group-of-lawmakers-investigating-impact-of-data-centers-on-energy-costs/"},
        ],
        "as_of": "2026-09-12",
    },
    ("NJ", "2", "Jeff Van Drew"): {
        "lean": "guardrails",
        "summary": "Cosponsored the FAIR Data Act, bipartisan legislation to "
                   "prevent data center projects from passing grid upgrade "
                   "costs onto residential ratepayers.",
        "items": [
            {"what": "Cosponsored H.R. 9655, the FAIR Data Act, bipartisan "
                     "legislation to prevent data center projects from "
                     "passing grid upgrade costs onto residential ratepayers "
                     "and small businesses.",
             "date": "2026-07-13",
             "source": "https://riley.house.gov/2026/07/13/riley-introduces-bill-to-stop-data-center-projects-from-driving-up-energy-bills/"},
        ],
        "as_of": "2026-09-12",
    },
    ("NJ", "10", "LaMonica McIver"): {
        "lean": "guardrails",
        "summary": "Introduced a bill to stop surprise AI data center "
                   "development and cosponsored the moratorium act.",
        "items": [
            {"what": "Introduced bill to stop surprise AI data center "
                     "development, requiring site selection transparency.",
             "date": "2026-06-24",
             "source": "https://mciver.house.gov/media/press-releases/mciver-introduces-bill-to-stop-surprise-ai-data-center-development"},
            {"what": "Cosponsored H.R. 9442, the AI Data Center Moratorium "
                     "Act.",
             "date": "2026-06-29",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/9442/cosponsors"},
        ],
        "as_of": "2026-09-12",
    },
    # Dan Goldman (NY-10): lost renomination, not on 2026 ballot.
    ("MA", "2", "Jim McGovern"): {
        "lean": "guardrails",
        "summary": "Original cosponsor of the AI Data Center Moratorium Act; "
                   "told NOTUS Congress should give members a vote on a "
                   "national moratorium.",
        "items": [
            {"what": "Original cosponsor of H.R. 9442, the AI Data Center "
                     "Moratorium Act. Told NOTUS: 'We ought to at least give "
                     "members the opportunity to vote on the national "
                     "moratorium.'",
             "date": "2026-06-24",
             "source": "https://ocasio-cortez.house.gov/media/press-releases/ocasio-cortez-introduces-house-version-ai-data-center-moratorium-act"},
        ],
        "as_of": "2026-09-12",
    },
    # Steve Cohen (TN-9): retiring, not on 2026 ballot.
    # Chuy García (IL-4): retiring, not on 2026 ballot.
    ("AZ", "7", "Adelita Grijalva"): {
        "lean": "guardrails",
        "summary": "Cosponsored the AI Data Center Moratorium Act and the "
                   "Data Center Community Impact Act.",
        "items": [
            {"what": "Original cosponsor of H.R. 9442, the AI Data Center "
                     "Moratorium Act.",
             "date": "2026-06-24",
             "source": "https://ocasio-cortez.house.gov/media/press-releases/ocasio-cortez-introduces-house-version-ai-data-center-moratorium-act"},
            {"what": "Cosponsored H.R. 7858, the Data Center Community "
                     "Impact Act.",
             "date": "2026-03-06",
             "source": "https://watsoncoleman.house.gov/newsroom/press-releases/rep-watson-coleman-introduces-bill-to-study-impact-of-ai-data-centers-on-local-communities"},
        ],
        "as_of": "2026-09-12",
    },
    ("CA", "43", "Maxine Waters"): {
        "lean": "guardrails",
        "summary": "Cosponsored the AI Data Center Moratorium Act.",
        "items": [
            {"what": "Cosponsored H.R. 9442, the AI Data Center Moratorium "
                     "Act.",
             "date": "2026-07-13",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/9442/cosponsors"},
        ],
        "as_of": "2026-09-12",
    },
    ("CA", "10", "Mark DeSaulnier"): {
        "lean": "guardrails",
        "summary": "Cosponsored the AI Data Center Moratorium Act.",
        "items": [
            {"what": "Cosponsored H.R. 9442, the AI Data Center Moratorium "
                     "Act.",
             "date": "2026-07-21",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/9442/cosponsors"},
        ],
        "as_of": "2026-09-12",
    },
    ("PA", "12", "Summer Lee"): {
        "lean": "guardrails",
        "summary": "Cosponsored the Data Center Community Impact Act "
                   "requiring DOE to study effects on communities of color "
                   "and low-income communities.",
        "items": [
            {"what": "Cosponsored H.R. 7858, the Data Center Community "
                     "Impact Act.",
             "date": "2026-03-06",
             "source": "https://watsoncoleman.house.gov/newsroom/press-releases/rep-watson-coleman-introduces-bill-to-study-impact-of-ai-data-centers-on-local-communities"},
        ],
        "as_of": "2026-09-12",
    },
    # ── Batch 7: AZ, MT, AK — 2026-09-12 ────────────────────────────────
    ("AZ", "3", "Yassamin Ansari"): {
        "lean": "guardrails",
        "summary": "Cosponsored H.R. 9442 AI Data Center Moratorium Act",
        "items": [
            {"what": "Cosponsored H.R. 9442 (AI Data Center Moratorium Act), "
                     "which would pause construction of new AI data centers "
                     "over 20 MW until Congress passes comprehensive AI "
                     "legislation",
             "date": "2026-09-12",
             "source": "https://www.govinfo.gov/app/details/BILLS-119hr9442ih"},
        ],
        "as_of": "2026-09-12",
    },
    ("AZ", "4", "Greg Stanton"): {
        "lean": "mixed",
        "summary": "Cosponsored Responsible Data Center Siting Act directing "
                   "DOE to establish siting best practices",
        "items": [
            {"what": "Cosponsored H.R. 10321 (Responsible Data Center Siting "
                     "Act), directing DOE to establish best practices for data "
                     "center siting considering energy, water, utility bills, "
                     "environment, noise, and community impacts",
             "date": "2026-09-08",
             "source": "https://subramanyam.house.gov/media/press-releases/rep-subramanyam-introduces-national-data-center-plan"},
        ],
        "as_of": "2026-09-12",
    },
    ("AZ", "6", "JoAnna Mendoza"): {
        "lean": "guardrails",
        "summary": "Opposes data centers in the desert; cites heat and water "
                   "impacts",
        "items": [
            {"what": "Stated 'No data centers in the desert. Not right now, "
                     "not in our district, not in our state'; cites ASU "
                     "research on 2-4 degree heat emissions from data centers; "
                     "wants federal action on utility bill protection and "
                     "water transparency",
             "date": "2026-09-12",
             "source": "https://blogforarizona.net/201903-2/"},
        ],
        "as_of": "2026-09-12",
    },
    # Adelita Grijalva (AZ-7): duplicate removed, richer entry above at line ~1791.
    ("MT", "2", "Troy Downing"): {
        "lean": "mixed",
        "summary": "Supports data centers with local control and water rights "
                   "protections",
        "items": [
            {"what": "Stated 'Data centers can bring investment and "
                     "opportunity to Montana, but these decisions should be "
                     "made by the communities that will live with them'; "
                     "called for 'light-touch' federal approach; insisted "
                     "'Montana's senior water rights must be protected'",
             "date": "2026-09-12",
             "source": "https://homenewshere.com/national/news/article_5c76009c-97fc-5c0e-841e-126c000d2d21.html"},
        ],
        "as_of": "2026-09-12",
    },
    ("MT", "2", "Brian Miller"): {
        "lean": "guardrails",
        "summary": "Emphasizes local control and transparency; served as "
                   "legal counsel for citizens challenging data center "
                   "development",
        "items": [
            {"what": "Served as legal counsel for citizens challenging "
                     "Quantica data center development in Yellowstone County; "
                     "stated 'We need to have maximum local control and "
                     "respect state sovereignty on data centers'; criticized "
                     "NDAs hiding operational details",
             "date": "2026-09-12",
             "source": "https://homenewshere.com/national/news/article_5c76009c-97fc-5c0e-841e-126c000d2d21.html"},
        ],
        "as_of": "2026-09-12",
    },
    ("MT", "2", "Michael Eisenhauer"): {
        "lean": "mixed",
        "summary": "Supports local decision-making with conditions; not "
                   "opposed to data centers but wants protections",
        "items": [
            {"what": "Stated 'I think local control is the way it needs to "
                     "be. I am not in favor of a mandate either for or "
                     "against'; has 5-Pillar policy including closed-loop "
                     "cooling, worker/ratepayer protections, and community "
                     "final approval",
             "date": "2026-09-12",
             "source": "https://homenewshere.com/national/news/article_5c76009c-97fc-5c0e-841e-126c000d2d21.html"},
        ],
        "as_of": "2026-09-12",
    },
    ("MT", "2", "Patrick McCracken"): {
        "lean": "guardrails",
        "summary": "Highlights environmental and resource concerns; notes "
                   "unaddressed electrical and water impacts",
        "items": [
            {"what": "Stated 'most people would not want to live next door to "
                     "a data center'; highlighted unaddressed electrical and "
                     "water resource impacts; referenced Montana's "
                     "constitutional guarantee of healthful environment",
             "date": "2026-09-12",
             "source": "https://homenewshere.com/national/news/article_5c76009c-97fc-5c0e-841e-126c000d2d21.html"},
        ],
        "as_of": "2026-09-12",
    },
    # --- batch 8 (2026-09-12): MA, LA, RI, ND ---
    ("MA", "3", "Lori Trahan"): {
        "lean": "guardrails",
        "summary": "Voted to advance Ratepayer Protection Act and Protecting "
                   "Families from AI Data Center Energy Costs Act in E&C "
                   "Committee markup",
        "items": [
            {"what": "Supported passage of the Ratepayer Protection Act "
                     "(H.R. 9340) and the Protecting Families from AI Data "
                     "Center Energy Costs Act (H.R. 6529) during House Energy "
                     "and Commerce Committee markup; stated people are "
                     "'already feeling it in their electric bill'",
             "date": "2026-07-21",
             "source": "https://trahan.house.gov/news/documentsingle.aspx?DocumentID=3815"},
        ],
        "as_of": "2026-09-12",
    },
    ("MA", "7", "Ayanna Pressley"): {
        "lean": "guardrails",
        "summary": "Joined site tour and press conference at xAI Memphis "
                   "facility calling for data center oversight",
        "items": [
            {"what": "Joined Reps. AOC, Summer Lee, and Justin Pearson in "
                     "South Memphis for site tour and press conference at xAI "
                     "data center facility, calling for data center oversight; "
                     "met with residents reporting health impacts from methane "
                     "gas turbines powering the facility",
             "date": "2026-07-17",
             "source": "https://www.localmemphis.com/video/news/local/us-reps-aoc-ayanna-pressley-and-summer-lee-join-rep-pearson-to-call-for-data-center-oversight/522-da7811da-261d-4d61-82bf-7a3abb74e29a"},
        ],
        "as_of": "2026-09-12",
    },
    ("LA", "1", "Steve Scalise"): {
        "lean": "accelerate",
        "summary": "Promotes data center benefits; suggested China behind "
                   "anti-DC sentiment; backed Ratepayer Protection Act floor "
                   "vote as Majority Leader",
        "items": [
            {"what": "Promoted data center benefits, citing Richland Parish "
                     "Meta center teacher bonuses: 'They were able to give "
                     "every single school teacher in that parish a $50,000 "
                     "bonus.' Said decisions should remain at the local level",
             "date": "2026-09-03",
             "source": "https://www.moderntreatise.com/the-americas/2026/9/3/in-america-gop-under-pressure-to-pass-data-center-legislation-before-midterms"},
            {"what": "Suggested China was behind anti-data-center sentiment: "
                     "'We are investigating whether China is behind a lot of "
                     "this misinformation, false information against data "
                     "centers.' Claimed to be finding social media bots "
                     "controlled by Beijing opposing data centers",
             "date": "2026-09-04",
             "source": "https://www.ms.now/rachel-maddow-show/maddowblog/data-centers-scalise-trump-republicans-china-conspiracy-theory-gop-elections-midterms"},
            {"what": "As Majority Leader, backed bringing the Ratepayer "
                     "Protection Act to the House floor for a vote",
             "date": "2026-09-10",
             "source": "https://www.axios.com/2026/09/10/house-republicans-data-center-power-bills-ai"},
        ],
        "as_of": "2026-09-12",
    },
    ("LA", "4", "Mike Johnson"): {
        "lean": "mixed",
        "summary": "Opposes moratoriums and frames DC buildout as AI race vs "
                   "China; but also scheduled Ratepayer Protection Act for "
                   "House floor vote",
        "items": [
            {"what": "Warned that 'a broad moratorium against data centers is "
                     "kind of a dangerous prospect' and said 'We're in a race "
                     "with China on that AI race'; campaigned against data "
                     "center moratoriums in Michigan swing seat",
             "date": "2026-08-18",
             "source": "https://www.detroitnews.com/story/news/local/michigan/2026/08/18/johnson-warns-against-data-center-pause-stumping-in-michigan-swing-seat/91358562007/"},
            {"what": "As Speaker, brought the Ratepayer Protection Act "
                     "(H.R. 9340) to the House floor for a vote — bipartisan "
                     "bill requiring state utility regulators to consider "
                     "rules making data centers cover costs of new power "
                     "generation",
             "date": "2026-09-10",
             "source": "https://www.axios.com/2026/09/10/house-republicans-data-center-power-bills-ai"},
        ],
        "as_of": "2026-09-12",
    },
    ("ND", "AL", "Julie Fedorchak"): {
        "lean": "mixed",
        "summary": "Pro-AI/DC buildout framing (national security vs China) "
                   "but insists data centers pay their own infrastructure "
                   "costs",
        "items": [
            {"what": "Launched AI and Energy Working Group; issued RFI on AI "
                     "energy demands (100+ stakeholder responses). Framed as "
                     "competitiveness vs China: 'we need everything we've "
                     "got' for energy supply",
             "date": "2025-03-01",
             "source": "https://fedorchak.house.gov/media/press-releases/fedorchak-issues-request-information-address-ais-growing-energy-demands"},
            {"what": "At Energy Subcommittee hearing 'AI and the Grid,' "
                     "pressed for fair cost allocation — 'those who drive the "
                     "need for new energy infrastructure should pay for it.' "
                     "Promoted FAIR Act (H.R. 6336) and High-Capacity Grid "
                     "Act (H.R. 6633)",
             "date": "2026-04-29",
             "source": "https://fedorchak.house.gov/media/press-releases/fedorchak-presses-fair-cost-allocation-highlights-grid-solutions-energy"},
        ],
        "as_of": "2026-09-12",
    },
    ("AK", "AL", "Nick Begich III"): {
        "lean": "accelerate",
        "summary": "Introduced DATA Act allowing data centers to operate on "
                   "self-contained grid; pro-expansion op-ed",
        "items": [
            {"what": "Introduced H.R. 8400 (DATA Act of 2026) allowing large "
                     "energy users including data centers to operate on "
                     "self-contained 'grid of one' power systems disconnected "
                     "from the broader grid, protecting ratepayers from "
                     "subsidizing data center electricity loads",
             "date": "2026-04-21",
             "source": "https://begich.house.gov/media/press-releases/congressman-begich-leads-legislation-lower-energy-costs-introduces-house"},
            {"what": "Op-ed 'How Alaska can Use our Energy Advantage to "
                     "Capitalize on the AI Gold Rush': argued Alaska should "
                     "aggressively pursue data centers citing natural gas, "
                     "cold climate, and vast land; warned against "
                     "over-regulation",
             "date": "2026-04-23",
             "source": "https://www.adn.com/opinions/2026/04/23/opinion-how-alaska-can-use-our-energy-advantage-to-capitalize-on-the-ai-gold-rush/"},
        ],
        "as_of": "2026-09-12",
    },
}


def _key(r):
    return (r["abbrev"], r["district"])


def races(state=None):
    """Every 2026 House race with records and unverified mentions attached."""
    rows = HOUSE_RACES_2026
    if state:
        rows = [r for r in rows if r["abbrev"] == state or r["state"] == state]
    return rc.attach_records(rows, AI_RECORDS, _key)


def coverage():
    return rc.coverage(races(), ROSTER_AS_OF)


def by_state():
    """Races grouped by state, districts in ballot order."""
    out = {}
    for r in races():
        out.setdefault(r["state"], []).append(r)
    for v in out.values():
        v.sort(key=lambda r: (0 if r["district"] == "AL" else int(r["district"])))
    return dict(sorted(out.items()))


def validate():
    return rc.validate(races(), AI_RECORDS, _key)
