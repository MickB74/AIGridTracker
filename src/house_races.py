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
        "summary": "Lead Republican sponsor of the Ratepayer Protection Act, which would push states to make large loads — data centers included — pay for the generation and transmission they require instead of spreading it across households.",
        "items": [
            {
             "what": "Introduced H.R. 9340, the Ratepayer Protection Act, with Rep. Kathy Castor. It directs states and their PUCs to consider standards for connecting large-load customers so those customers, not families and small businesses, cover new generation, transmission and upgrade costs. Cleared House Energy and Commerce 52-0.",
             "date": "2026-07-22",
             "source": "https://broadbandbreakfast.com/house-committee-approves-package-to-address-data-centers-growing-energy-demands/"},
            {
             "what": "H.R. 9340 passed the full House 417-3. It directs state utility commissions to consider rate designs under which data centers with 100 MW or more of peak demand at one site bear the full incremental cost of the generation, transmission and distribution upgrades they require. Now goes to the Senate.",
             "date": "2026-09-16",
             "source": "https://energycommerce.house.gov/posts/ratepayer-protection-act-passes-house-with-strong-bipartisan-support"},
        ],
        "as_of": "2026-11-21",
    },
    ("FL", "14", "Kathy Castor"): {
        "lean": "guardrails",
        "summary": "Named with Rep. Gabe Evans as a sponsor of H.R. 9340, the Ratepayer Protection Act, which would require state utility regulators to consider making data centers of 100 MW or more pay the full cost of grid upgrades needed to serve them.",
        "items": [
            {
             "what": "Sponsor, with Rep. Gabe Evans (R-CO), of H.R. 9340, the Ratepayer Protection Act, which would require each state regulatory authority to consider a federal standard under which data centers and hyperscalers with demand of 100 megawatts pay the full cost of generation, transmission or distribution upgrades needed to serve them. Cleared the House Energy and Commerce Committee 52-0.",
             "date": "2026-07-22",
             "source": "https://broadbandbreakfast.com/house-committee-approves-package-to-address-data-centers-growing-energy-demands/"},
        ],
        "as_of": "2026-11-21",
    },

    # ── H.R. 8241, Power for the People Act of 2026 ────────────────────────
    # House companion to Van Hollen's S.3682. Cited to the bill of record:
    # congress.gov refuses scripted fetches (verify_candidate_records.py
    # classifies that as *blocked*, not dead — same convention as
    # scripts/verify_sources.py), but it is the canonical page for the text.
    ("MD", "7", "Kweisi Mfume"): {
        "lean": "guardrails",
        "summary": "Original cosponsor of the Power for the People Act (H.R. 8241, sponsor Rep. Tonko), later cosponsor of the AI Data Center Moratorium Act, and one of the Maryland delegation members named in a July 2026 letter asking FERC to require PJM protections for Maryland ratepayers.",
        "items": [
            {
             "what": "Original cosponsor of H.R. 8241, the Power for the People Act of 2026, sponsored by Rep. Tonko; congress.gov gives its purpose as promoting data center load queues and data center-specific rate classes to mitigate the impact of data centers on other electricity consumers.",
             "date": "2026-04-09",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/8241/all-info"},
            {
             "what": "Added as a cosponsor of H.R. 9442, the AI Data Center Moratorium Act (sponsor Rep. Ocasio-Cortez), on 08/27/2026.",
             "date": "2026-08-27",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/9442/cosponsors"},
            {
             "what": "Named among the Maryland congressional delegation members calling on FERC to require PJM to protect Marylanders after PJM assigned roughly $2 billion in costs to Maryland ratepayers for infrastructure needed primarily to serve out-of-state data centers; the letter supports a complaint filed by the Maryland Office of People's Counsel.",
             "date": "2026-07-28",
             "source": "https://mcclaindelaney.house.gov/media/press-releases/maryland-democrats-urge-ferc-protect-marylanders-rising-electricity-costs-due"},
        ],
        "as_of": "2026-11-21",
    },
    ("NY", "20", "Paul Tonko"): {
        "lean": "guardrails",
        "summary": "Sponsor of the Power for the People Act (H.R. 8241), on data center load queues and data center-specific rate classes; said in August 2026 that data centers “should be built in communities that want them”.",
        "items": [
            {
             "what": "Sponsor of H.R. 8241, the Power for the People Act of 2026, introduced 04/09/2026. congress.gov gives its purpose as promoting data center load queues and data center-specific rate classes to mitigate the impact of data centers on other electricity consumers.",
             "date": "2026-04-09",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/8241/all-info"},
            {
             "what": "Said at an Albany roundtable that data centers like the one proposed for the Kenwood site in South Albany \"should be built in communities that want them\", and that \"we have to provide for those safety nets and the guardrails for both AI and data centers.\"",
             "date": "2026-08-11",
             "source": "https://www.wamc.org/news/2026-08-11/tonko-kenwood-project-data-center"},
        ],
        "as_of": "2026-11-21",
    },

    # ── CA deep dive, 2026-09-11 ──────────────────────────────────────────
    ("CA", "25", "Raul Ruiz"): {
        "lean": "guardrails",
        "summary": "Formally opposed the proposed Imperial Valley data center project in a statement read into the Imperial County Board of Supervisors record on June 2, 2026, and said he plans to ask EPA and DOE for federal environmental review of projects in water-stressed environmental justice communities, including the Imperial and Coachella valleys. One source.",
        "items": [
            {
             "what": "Letter to the Imperial County Board of Supervisors, read into the record by a district representative on June 2: \"I unequivocally oppose data centers in Imperial Valley and urge local officials to prevent them from happening.\" Cited reduced life expectancy, air pollution, asthma, energy costs and water use. His office said he plans to send letters to EPA and DOE seeking federal oversight and environmental review of proposed projects in water-stressed environmental justice communities, including the Imperial and Coachella valleys.",
             "date": "2026-06-02",
             "source": "https://www.thedesertreview.com/news/ruiz-formally-opposes-proposed-imperial-data-center-project/article_66fd01cf-c1db-4002-b64e-895dc9b5d09e.html"},
        ],
        "as_of": "2026-11-21",
    },
    ("CA", "49", "Mike Levin"): {
        "lean": "guardrails",
        "summary": "Introduced the SHIELD Act with Rep. Kathy Castor (separate rate class for large-load customers over 75 MW), co-led the Energy Bills Relief Act, and is a cosponsor of the Responsible Data Center Siting Act.",
        "items": [
            {
             "what": "Introduced, with Rep. Kathy Castor, the Stopping Hikes In Electricity from Large Load Demands (SHIELD) Act: a separate rate class for large load customers (facilities using more than 75MW) so households do not pay for their grid upgrades, plus priority interconnection for large loads powered by zero-emission electricity. \"Families should not be forced to subsidize massive energy costs for billion-dollar companies.\"",
             "date": "2026-01-14",
             "source": "https://levin.house.gov/media/press-releases/rep-mike-levin-introduces-new-bill-to-stop-data-centers-from-driving-up-electricity-prices-for-consumers"},
            {
             "what": "With Rep. Sean Casten, led 120 House Democrats in introducing the Energy Bills Relief Act, which Levin said \"ensures that data centers and large energy users pay their fair share instead of passing those costs onto families and small businesses.\"",
             "date": "2026-03-18",
             "source": "https://levin.house.gov/media/press-releases/reps-levin-and-casten_seec-clean-energy-deployment-task-force-introduce-the-energy-bills-relief-act"},
            {
             "what": "Listed as a cosponsor of H.R. 10321, the Responsible Data Center Siting Act of 2026 (sponsor Rep. Suhas Subramanyam), 'to direct the Secretary of Energy to establish best practices for the siting of data centers'.",
             "date": "2026-09-08",
             "source": "https://www.govinfo.gov/app/details/BILLS-119hr10321ih"},
        ],
        "as_of": "2026-11-21",
    },

    # ── promoted from the review queue, 2026-08-26 ────────────────────────
    # Surfaced by scripts/scan_candidate_records.py as Google News leads, then
    # promoted by hand: each redirect was resolved to the member's own release,
    # which is what these cite. A queue link is never the citation.
    ("CA", "17", "Ro Khanna"): {
        "lean": "guardrails",
        "summary": "Introduced a Data Center Bill of Rights resolution affirming a community's right to ban data centers near homes and schools, to reject a project outright, and to keep local siting authority from being preempted by the state.",
        "items": [
            {
             "what": "Introduced the Data Center Bill of Rights resolution: communities may ban data centers in residential areas and within 2,500 feet of homes, schools, childcare, hospitals or nursing homes; may reject a project through a transparent community process; county and municipal authority to prohibit or regulate is preserved against state preemption; and every data center must use clean, reliable energy under strict noise and air limits. It is a resolution, so it does not itself change law.",
             "date": "2026-08-06",
             "source": "https://khanna.house.gov/media/press-releases/release-rep-khanna-introduces-data-center-bill-rights"},
        ],
        "as_of": "2026-11-21",
    },
    ("NJ", "6", "Frank Pallone"): {
        "lean": "guardrails",
        "summary": "The senior Democrat on House Energy and Commerce called for a national moratorium on AI data centers until their effect on air, water and power bills is resolved.",
        "items": [
            {
             "what": "Called for a national AI data-center moratorium at an Energy Subcommittee markup — “in favor of a national AI data center moratorium until we can find a way to ensure they don't harm our nation's air, water, and power bills.”",
             "date": "2026-06-24",
             "source": "https://pallone.house.gov/media/press-releases/pallone-supports-national-ai-data-center-moratorium"},
        ],
        "as_of": "2026-11-21",
    },
    ("NY", "19", "Josh Riley"): {
        "lean": "guardrails",
        "summary": "Introduced the bipartisan FAIR Data Act to keep the cost of generation, transmission and distribution upgrades for data centers off New York ratepayers.",
        "items": [
            {
             "what": "Introduced the FAIR Data Act, bipartisan legislation to stop data-center projects from raising energy bills for Upstate New York families and small businesses by shielding ratepayers from the generation, transmission and distribution upgrades those projects require.",
             "date": "2026-07-13",
             "source": "https://riley.house.gov/2026/07/13/riley-introduces-bill-to-stop-data-center-projects-from-driving-up-energy-bills/"},
        ],
        "as_of": "2026-11-21",
    },
    ("GA", "7", "Rich McCormick"): {
        "lean": "accelerate",
        "summary": "As Science Committee chairman, opened a February 2026 hearing on data center infrastructure by citing permitting delays and asking whether a 1970s-era permitting framework suits the buildout; he also raised, as a question, whether residential ratepayers could end up subsidizing grid upgrades for data centers. No bill or vote located. One source.",
        "items": [
            {
             "what": "Opening statement as chairman at the hearing 'Powering America's AI Future: Assessing Policy Options to Increase Data Center Infrastructure': called the Trump executive order prioritizing data center permitting 'a positive step', said several projects have faced substantial permitting hurdles, and asked whether a permitting framework 'largely designed in the 1970s' is suited to this infrastructure; also raised the question of whether residential ratepayers could end up subsidizing upgrades that primarily serve high-intensity users.",
             "date": "2026-02-24",
             "source": "https://science.house.gov/2026/2/opening-statement-of-chairman-rich-mccormick-at"},
        ],
        "as_of": "2026-11-21",
    },
    # ── Virginia — the state with the most data centers and, until 2026-09-05,
    # zero records on this page. Each item is the member's own release or a
    # dated interview; a letter to a planning commission is an action, a
    # study bill is a bill, and an interview quote is only a quote — the
    # summaries say which.
    ("VA", "8", "Don Beyer"): {
        "lean": "guardrails",
        "summary": "Wrote to the Fairfax County Planning Commission on July 30, 2026 asking it to deny the permit application for the Edsall Data Center Substation 2232 at the Plaza 500 site in Lincolnia -- a documented action on a live project in his district, not a bill. One source.",
        "items": [
            {
             "what": "Letter urging the Fairfax County Planning Commission to deny the Edsall Data Center Substation 2232 application, citing land use, flooding mitigation, light and noise pollution and Lincolnia's growth goals: \"Data center infrastructure should not be built in residential areas where its scale and likely impacts are fundamentally incompatible with the character and quality of life of adjacent neighborhoods.\"",
             "date": "2026-07-30",
             "source": "https://beyer.house.gov/news/documentsingle.aspx?DocumentID=9183"},
        ],
        "as_of": "2026-11-21",
    },
    ("VA", "7", "Eugene Vindman"): {
        "lean": "guardrails",
        "summary": "Introduced the Smart Data Center Policy Act, a Commerce Department study of siting data centers in industrial zones, transport hubs and military bases instead of next to neighborhoods, schools and parks. A study bill, not a mandate.",
        "items": [
            {
             "what": "Introduced the Smart Data Center Policy Act, directing the Department of Commerce to study the costs, benefits and possible federal incentives for siting data centers in industrial zones, rail and airport hubs and military installations rather than near homes and green space, with findings due to Congress in 180 days. Vindman: “We need to ensure data centers pay their fair share and are built in places that make sense — not next to neighborhoods, schools, or our public lands.”",
             "date": "2026-08-04",
             "source": "https://vindman.house.gov/2026/08/04/vindman-introduces-legislation-to-prevent-data-center-development-near-neighborhoods-schools-parks/"},
        ],
        "as_of": "2026-11-21",
    },
    ("VA", "10", "Suhas Subramanyam"): {
        "lean": "guardrails",
        "summary": "Represents a district with more than 300 data centers; introduced a DHS security-strategy bill for communities around data centers (May 2026) and, with Reps. Obernolte and Foushee, a bipartisan NIST/DOE data center energy and water measurement bill (June 2026); sponsor of H.R. 10321, the Responsible Data Center Siting Act. At a Brookings event said he wants a national strategy that puts communities first.",
        "items": [
            {
             "what": "Introduced the Data Infrastructure Risk Reduction Act, directing DHS to produce a security strategy and recommendations for protecting communities around data centers, considering the security of transmission and water infrastructure.",
             "date": "2026-05-08",
             "source": "https://subramanyam.house.gov/media/press-releases/rep-subramanyam-introduces-bill-protect-homes-and-property-near-data-centers"},
            {
             "what": "Introduced, with Reps. Jay Obernolte (R-CA) and Valerie Foushee (D-NC), the Data Infrastructure Energy Measurement and Standards Act, directing NIST in coordination with DOE to develop best practices and technical standards for measuring data center energy and water use, as a foundation for forecasting, planning and siting. \"We need a simple way to track how much power and water these facilities use.\"",
             "date": "2026-06-18",
             "source": "https://subramanyam.house.gov/media/press-releases/reps-subramanyam-obernolte-foushee-introduce-legislation-create-first-its-kind"},
            {
             "what": "At a Brookings Institution event called the community-by-community approach to data center siting \"short-term profit-driven, sometimes it's a little predatory, and it's not working\" and said he wants \"a national strategy that puts communities first\"; also called for transparency in development agreements, which often include nondisclosure agreements signed by officials, and on actual power and water use.",
             "date": "2026-09-22",
             "source": "https://www.nextgov.com/modernization/2026/09/do-data-centers-need-national-strategy-puts-communities-first/416137/"},
        ],
        "as_of": "2026-11-21",
    },
    ("VA", "1", "Rob Wittman"): {
        "lean": "accelerate",
        "summary": "Backed an NDAA provision using a Naval Weapons Station Yorktown–Dominion nuclear partnership as a pathfinder for meeting military and data-center power demand. Supply-side only; nothing located on who pays or on siting.",
        "items": [
            {
             "what": "Supported the FY2026 NDAA committee text that “directs the Navy to use a promising partnership between Naval Weapons Station Yorktown and Dominion Energy as a pathfinder to determine how to leverage nuclear power to meet Navy and Marine Corps installation power demands, in addition to supporting the data center energy demands of accelerating technologies like artificial intelligence.”",
             "date": "2025-07-15",
             "source": "https://wittman.house.gov/newsroom/press-releases/wittman-supports-legislation-that-strengthens-national-defense-and-supports-virginia-shipbuilding"},
        ],
        "as_of": "2026-11-21",
    },
    ("VA", "2", "Jen Kiggans"): {
        "lean": "mixed",
        "summary": "An interview quote, not an action: said data centers cannot all be banned but there is “a commonsense conversation to be had” about their energy and water use, and that the debate has so far been left to Virginia’s Legislature.",
        "items": [
            {
             "what": "Told The Daily Signal: “They have data centers under the ocean floor. We can’t ban all data centers,” adding there is a “commonsense conversation to be had” on their use of energy, water and other local resources, that the debate has so far been left to Virginia’s Legislature, and that she has “enjoyed watching the Democrats fight with each other about the issue.”",
             "date": "2026-08-18",
             "source": "https://www.dailysignal.com/2026/08/18/midterm-rematch-fate-of-country/"},
        ],
        "as_of": "2026-11-21",
    },

    # ── Michigan ───────────────────────────────────────────────────────────
    ("MI", "12", "Rashida Tlaib"): {
        "lean": "guardrails",
        "summary": "Introduced a bill banning large AI data centers on federal lands, issued a December 2025 statement siding with residents pushing back on a proposed Southfield data center, and was one of three House members to vote no on the Ratepayer Protection Act, saying it 'fails to meaningfully protect our communities' and calling for a national moratorium.",
        "items": [
            {
             "what": "Introduced the No AI Data Centers on Federal Lands Act, which permanently bans large AI data centers and associated infrastructure on land owned or managed by the U.S., including military bases, and requires removal of existing qualifying data centers and site remediation.",
             "date": "2026-07-23",
             "source": "https://tlaib.house.gov/posts/rep-tlaib-introduces-a-bill-to-ban-ai-data-centers-on-federal-lands"},
            {
             "what": "Statement after Southfield City Council approved a site plan for Metrobloks' proposed AI data center: cited residents' concerns about electricity costs rising 'by as much as 267%' and consuming 'millions of gallons of water per day', said she was inspired to see residents 'organizing together to push back', and said she would work with them to 'protect our communities'.",
             "date": "2025-12-16",
             "source": "https://tlaib.house.gov/posts/tlaib-statement-on-ai-data-center-vote-in-southfield"},
            {
             "what": "One of three House members (with Summer Lee and Delia Ramirez) to vote against H.R. 9340, the Ratepayer Protection Act (417-3). Said it 'fails to meaningfully protect our communities'; before the vote wrote on X: \"The strongest action Congress can take right now is to pass a national moratorium on data centers and enact a prohibition on federal lands.\"",
             "date": "2026-09-16",
             "source": "https://www.nbcnews.com/politics/congress/house-passes-bill-shield-consumers-data-center-price-hikes-energy-rcna597683"},
        ],
        "as_of": "2026-11-21",
    },
    ("MI", "3", "Hillary Scholten"): {
        "lean": "guardrails",
        "summary": "Introduced two data center transparency bills in July 2026: one directing NTIA to run an annual survey of data center energy and water use and publish results on a dashboard, and one directing DoD to update its data center efficiency requirements and use water-saving cooling. Neither addresses who pays for grid costs or siting. One source.",
        "items": [
            {
             "what": "Announced introduction of two bills, the Data Center Resource Disclosure Act (NTIA annual survey of operators' energy and water consumption, public comment, public dashboard, list of non-responders) and the Defending Our Energy and Water Act (DoD to update data center efficiency requirements and ensure new facilities adopt cooling technologies that reduce water impact). \"Accountability starts with transparency.\"",
             "date": "2026-07-30",
             "source": "https://scholten.house.gov/media/press-releases/congresswoman-scholten-introduces-two-data-center-accountability-bills"},
        ],
        "as_of": "2026-11-21",
    },
    ("MI", "6", "Debbie Dingell"): {
        "lean": "guardrails",
        "summary": "Co-signed an October 2025 letter, led by Rep. Kevin Mullin and signed by 20 House members, to FERC, the Edison Electric Institute and the Data Center Coalition expressing concern that data center energy costs are being passed on to everyday Americans and small businesses and requesting information. One source; no bill or vote located.",
        "items": [
            {
             "what": "Named among the co-signers of the Mullin-led letters to FERC, the Edison Electric Institute and the Data Center Coalition raising concern that energy costs associated with data center development 'are increasingly being passed on to everyday Americans and small businesses' and requesting information.",
             "date": "2025-10-28",
             "source": "https://kevinmullin.house.gov/2025/10/28/rep-mullin-leads-group-of-lawmakers-investigating-impact-of-data-centers-on-energy-costs/"},
        ],
        "as_of": "2026-11-21",
    },
    ("MI", "7", "Tom Barrett"): {
        "lean": "guardrails",
        "summary": "Introduced two bills in August 2026: one barring federal agencies from overriding local land-use, zoning, siting or permitting authority over data centers, and one barring members of Congress from signing data center NDAs. His office says he voted against data center tax breaks in the Michigan House. One source.",
        "items": [
            {
             "what": "Introduced H.R. 10119, the Protecting Local Control of Data Centers Act (prohibits federal agencies from overriding local land-use, zoning, siting or permitting authority related to data centers and from leveraging federal funds to force local governments to give up that authority) and H.R. 10118, the No Data Center NDAs Act (prohibits members of Congress from signing NDAs about data centers, including locations or expected water and energy use). \"They deserve to know all the facts and have the final say over any proposed project.\" His release says that in the Michigan House he voted against legislation giving data center construction and equipment tax breaks.",
             "date": "2026-08-20",
             "source": "https://barrett.house.gov/media/press-releases/barrett-introduces-bills-protect-local-communities-data-center-overreach"},
        ],
        "as_of": "2026-11-21",
    },
    # ("MI", "10", "John James") was removed on 2026-10-19. He is retiring
    # from MI-10 to run for governor, so he is on no 2026 congressional
    # ballot, and validate() had been failing on the orphaned key
    # ("record key not on any ballot"). attach_records() never matched it to
    # a candidate, so it rendered nowhere — it only kept the guard red.
    # His four OBBBA AI-preemption votes are real and are in git history;
    # this registry tracks the ballot, and there is no governor tracker to
    # move them to. Restore them here only if he lands on a federal ballot.

    # ── Ohio ───────────────────────────────────────────────────────────────
    ("OH", "1", "Greg Landsman"): {
        "lean": "guardrails",
        "summary": "Sponsor of two data center bills: H.R. 6529, which directs FERC to hold a technical conference on protecting residential ratepayers from large-load costs, and H.R. 8033, the No Harm Data Centers Act.",
        "items": [
            {
             "what": "Introduced H.R. 6529, the Protecting Families from AI Data Center Energy Costs Act, whose official title is to require FERC to hold a technical conference on protecting residential ratepayers from increased costs associated with large loads. Ordered to be reported by House Energy and Commerce on 07/21/2026.",
             "date": "2025-12-09",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/6529/all-info"},
            {
             "what": "Introduced H.R. 8033, the No Harm Data Centers Act; official title: to ensure that American families are protected from the impacts of data centers on the electric grid. Referred to House Energy and Commerce.",
             "date": "2026-03-20",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/8033/all-info"},
        ],
        "as_of": "2026-11-21",
    },
    ("OH", "13", "Emilia Sykes"): {
        "lean": "guardrails",
        "summary": "Ranking member of the Science Committee's Investigations and Oversight Subcommittee. Said at a February 2026 data center hearing, \"We need to put strong guardrails in place so that data centers support our communities rather than the other way around.\" Her Affordability Agenda includes reallocating grid costs to protect consumers from price hikes from manufacturing and data center development.",
        "items": [
            {
             "what": "Released the Affordability Agenda with the New Democrat Coalition; its energy section includes 'Reallocate electric grid costs to protect consumers from price hikes due to manufacturing and data center development.'",
             "date": "2026-02-11",
             "source": "https://sykes.house.gov/media/press-releases/rep-sykes-unveils-affordability-agenda-to-address-the-cost-of-living-crisis"},
            {
             "what": "At the House Science Committee hearing on data center infrastructure said: \"We need to put strong guardrails in place so that data centers support our communities rather than the other way around. Ohioans should not pay higher electricity bills so billionaires in Silicon Valley can see higher profits.\" Noted Ohio has 217 data centers, the fifth most of any state.",
             "date": "2026-02-24",
             "source": "https://sykes.house.gov/media/press-releases/ranking-member-sykes-presses-for-consumer-protections-as-data-centers-expand-across-ohio"},
            {
             "what": "Advanced the Water Resources Development Act of 2026 (H.R. 9497) in the Transportation and Infrastructure Committee; the release says the bill 'advances efforts to study the impact of data centers on regional water resources' but does not attribute that provision to her.",
             "date": "2026-07-14",
             "source": "https://sykes.house.gov/media/press-releases/rep-sykes-advances-bipartisan-water-infrastructure-bill-with-key-wins-for-northeast-ohio"},
        ],
        "as_of": "2026-11-21",
    },
    ("OH", "5", "Bob Latta"): {
        "lean": "mixed",
        "summary": "As chairman of the Energy Subcommittee, led the Ratepayer Protection Act through subcommittee markup and spoke for it at the full committee; also co-signed a letter asking PCAST and the FBI for information on evidence that Chinese Communist Party-backed entities and other foreign adversaries may be influencing decisions on American data center infrastructure.",
        "items": [
            {
             "what": "Statement after chairing the June 24, 2026 subcommittee markup: \"We must ensure that American families are not left footing the bill for the significant grid upgrades and increased electricity demand driven by new AI infrastructure and other large load operations.\"",
             "date": "2026-06-24",
             "source": "https://latta.house.gov/news/documentsingle.aspx?DocumentID=406815"},
            {
             "what": "Statement on full Energy and Commerce Committee approval of H.R. 9340, the Ratepayer Protection Act (July 21, 2026): said he spoke in support at the markup and that numerous states, including Ohio, already have large load tariffs in place for data centers.",
             "date": "2026-07-21",
             "source": "https://latta.house.gov/news/documentsingle.aspx?DocumentID=406829"},
            {
             "what": "Co-signed, with Chairmen Guthrie and Joyce, a letter to the PCAST co-chairs and FBI Director Kash Patel requesting information about evidence suggesting foreign influence campaigns are working to slow American AI progress and block data center infrastructure.",
             "date": "2026-06-04",
             "source": "https://energycommerce.house.gov/posts/chairmen-guthrie-joyce-and-latta-request-investigation-of-foreign-adversaries-efforts-to-block-american-data-center-buildout"},
        ],
        "as_of": "2026-11-21",
    },
    ("OH", "12", "Troy Balderson"): {
        "lean": "accelerate",
        "summary": "Led the GRID Power Act to fast-track dispatchable power through interconnection queues, citing central Ohio's data center cluster. Co-introduced the Load Forecasting Enhancement Act.",
        "items": [
            {
             "what": "Led H.R. 1047, the GRID Power Act, directing FERC to let grid operators fast-track dispatchable power projects through interconnection queues. Cited data center growth in central Ohio. Passed the House.",
             "date": "2025-09-18",
             "source": "https://balderson.house.gov/news/documentsingle.aspx?DocumentID=2887"},
            {
             "what": "At Energy and Commerce hearing, noted his district hosts Google, AWS, Meta, QTS, Vantage and others, with signed power agreements reaching 5,000 MW by 2030. Questioned Eric Schmidt about tech companies' role in bringing new generation capacity online.",
             "date": "2025-04-09",
             "source": "https://energycommerce.house.gov/posts/energy-and-commerce-committee-holds-hearing-on-ai-and-american-global-competitiveness"},
            {
             "what": "Co-introduced H.R. 9332, the Load Forecasting Enhancement Act, directing FERC to work with state PUCs on improving electric load forecasting as demand surges from AI and data centers. Passed Energy Subcommittee.",
             "date": "2026-06-24",
             "source": "https://menendez.house.gov/media/press-releases/menendez-and-balderson-applaud-advancement-of-key-grid-reliability-bill"},
        ],
        "as_of": "2026-11-21",
    },
    ("OH", "6", "Michael Rulli"): {
        "lean": "mixed",
        "summary": "On Fox Business (Aug. 28, 2026) said most of his constituents do not want data centers, told them to ask whether the company pays (behind the meter) and whether water is self-contained, and said to keep data centers out of corn fields and neighborhoods. Also said 'there is so many positives' about AI, 'China is going to win this war,' and 'The CCP has infiltrated Ohio with propaganda against this.' Single interview.",
        "items": [
            {
             "what": "On Fox Business's Mornings with Maria, said 'Most of my constituents do not like data centers. They don't want them.' Told constituents to learn 'in front of the meter' (you pay) vs 'behind the meter' (the company pays) and whether the water system is self-contained, said data centers 'shouldn't put them on waste lands, brown fields' and 'Keep them out of the corn fields. Keep them out of the neighborhoods. We need to do better.' Also said 'The CCP has infiltrated Ohio with propaganda against this.' Did not state a position on the OpenAI/Nvidia project by name.",
             "date": "2026-08-28",
             "source": "https://www.breitbart.com/clips/2026/08/28/gop-rep-rulli-the-ccp-has-infiltrated-ohio-with-propaganda-against-500b-data-center/"},
        ],
        "as_of": "2026-11-21",
    },

    # ── 5-state deep dive (GA/NC/TX/TN/WI) — 2026-09-11 ─────────────

    ("GA", "2", "Sanford Bishop"): {
        "lean": "guardrails",
        "summary": "Insists communities weigh tradeoffs carefully and require data center operators to provide transparency on water and power consumption and deliver community benefits.",
        "items": [
            {
             "what": "Said south Georgia communities need guardrails, transparency on water/power consumption, and community benefits before data centers move forward.",
             "date": "2026-07-17",
             "source": "https://www.walb.com/2026/07/17/south-georgia-congressmen-say-data-centers-need-guardrails-before-moving-forward/"},
        ],
        "as_of": "2026-11-21",
    },
    ("GA", "7", "Rich McCormick"): {
        "lean": "accelerate",
        "summary": "As Science Committee chairman, opened a February 2026 hearing on data center infrastructure by citing permitting delays and asking whether a 1970s-era permitting framework suits the buildout; he also raised, as a question, whether residential ratepayers could end up subsidizing grid upgrades for data centers. No bill or vote located. One source.",
        "items": [
            {
             "what": "Opening statement as chairman at the hearing 'Powering America's AI Future: Assessing Policy Options to Increase Data Center Infrastructure': called the Trump executive order prioritizing data center permitting 'a positive step', said several projects have faced substantial permitting hurdles, and asked whether a permitting framework 'largely designed in the 1970s' is suited to this infrastructure; also raised the question of whether residential ratepayers could end up subsidizing upgrades that primarily serve high-intensity users.",
             "date": "2026-02-24",
             "source": "https://science.house.gov/2026/2/opening-statement-of-chairman-rich-mccormick-at"},
        ],
        "as_of": "2026-11-21",
    },
    ("GA", "8", "Austin Scott"): {
        "lean": "mixed",
        "summary": "Told WALB that data centers matter for national security and should be located in the U.S., that there 'are going to have to be some parameters' on water and power, and that companies must pay their own cost of energy with no increased power cost to residents. Said communities should ask about cooling systems, noting closed-loop systems use much less water. Single article.",
        "items": [
            {
             "what": "Said computing 'is a big part of national security' and data centers should be in the U.S.; said 'We need to make sure that the companies who build the data centers are paying their own cost of energy' and that residents see no increased power costs. Said 'Closed-loop systems don't use nearly as much water as the old systems do. We need to make sure that we're talking about what kind of cooling systems they have.'",
             "date": "2026-07-17",
             "source": "https://www.walb.com/2026/07/17/south-georgia-congressmen-say-data-centers-need-guardrails-before-moving-forward/"},
        ],
        "as_of": "2026-11-21",
    },
    ("TX", "4", "Pat Fallon"): {
        "lean": "guardrails",
        "summary": "Told CBS News Texas that Gov. Abbott's new data center policy (a pause plus requirements that data centers supply their own power and water) was 'a thoughtful, good step' and said constituents' concerns about data centers are ones 'I' share. Single interview.",
        "items": [
            {
             "what": "Told CBS News Texas: 'I think it was a thoughtful, good step that the governor put in place. He was listening to his constituents... They share those concerns, as I do.' Referring to Abbott's data center directives, which CBS describes as including a pause.",
             "date": "2026-08-17",
             "source": "https://www.cbsnews.com/texas/news/push-back-data-centers-texas-voters-gop-leaders-democratic-challengers/"},
        ],
        "as_of": "2026-11-21",
    },
    ("TN", "2", "Tim Burchett"): {
        "lean": "guardrails",
        "summary": "Publicly broke with Trump on data centers, called for local control and military-base siting over residential areas.",
        "items": [
            {
             "what": "Responded to Trump's warning that communities rejecting data centers risk becoming 'backwards and poor' by saying 'I guess I'm backwards and poor.' Called for more local control and suggested putting data centers in military installations.",
             "date": "2026-09-01",
             "source": "https://www.newsweek.com/list-of-republicans-publicly-breaking-with-trump-on-ai-data-centers-12391133"},
        ],
        "as_of": "2026-11-21",
    },
    ("TN", "3", "Chuck Fleischmann"): {
        "lean": "guardrails",
        "summary": "As Energy-Water Appropriations chair, said TVA customers should not face surprise rate hikes from data center demand.",
        "items": [
            {
             "what": "As chair of the House Energy and Water Development Appropriations Subcommittee, said 'there will be no rate increases without going to the people' regarding TVA rate changes tied to data center demand.",
             "date": "2026-05-27",
             "source": "https://newschannel9.com/news/local/repfleischmann-says-tva-customers-shouldnt-see-surprise-rate-hikes-tied-to-data-centers-chuck-fleischmann-tva-rates-data-center-electricity-demand-tennessee-tva-ai-power-usage-chattanooga-electricity-rates-data-centers"},
        ],
        "as_of": "2026-11-21",
    },
    ("WI", "3", "Derrick Van Orden"): {
        "lean": "guardrails",
        "summary": "Said the average Wisconsinite should not have to subsidize power or water for a commercial entity and, of data centers, that they should help pay rising utility rates or self-power.",
        "items": [
            {
             "what": "Told Wisconsin Watch: “The average Wisconsinite should not have to subsidize the power or water for a commercial entity” (said of manufacturers’ energy and water use, in a Foxconn story), and, of data centers, that they are “either going to help pay for those utility rates (that) are rising, or you’re going to self-power.”",
             "date": "2025-12",
             "source": "https://wisconsinwatch.org/2025/12/wisconsin-foxconn-data-center-energy-trump-ai-congress-lawmakers-republican-democrat/"},
        ],
        "as_of": "2026-11-21",
    },

    # ── FL/MD/PA/IA/CO deep dive, 2026-09-11 ─────────────────────────────
    ("CO", "1", "Melat Kiros"): {
        "lean": "guardrails",
        "summary": "Democratic socialist candidate in the Colorado 1st District Democratic primary against Rep. Diana DeGette. Told Drop Site News and the American Prospect that a federal data center moratorium is imperative and should be a negotiating tactic for significant AI regulation. Single pre-primary article.",
        "items": [
            {
             "what": "Told Drop Site News she supports a moratorium on data center construction; said 'a federal data center moratorium is imperative and should be used as a negotiation tactic to implement significant regulation of AI.'",
             "date": "2026-06-29",
             "source": "https://www.dropsitenews.com/p/aipac-ai-degette-melat-kiros-colorado"},
        ],
        "as_of": "2026-11-21",
    },
    ("CO", "4", "Lauren Boebert"): {
        "lean": "guardrails",
        "summary": "Asked about Trump's 'backwards and poor' remark, said 'The president says a lot of things' and 'I want people to have local control. That's what I fought for.' Does not describe the legislation she means. Single aggregator article.",
        "items": [
            {
             "what": "Asked by a MeidasTouch reporter about Trump saying data center opponents are 'backwards and poor,' said 'The president says a lot of things. Sometimes, it's really funny... Anyway, I fought for data centers to have local control' and 'I want people to have local control. That's what I fought for.'",
             "date": "2026-09-01",
             "source": "https://www.yahoo.com/news/politics/articles/rep-lauren-boebert-won-t-123549824.html"},
        ],
        "as_of": "2026-11-21",
    },
    ("MD", "2", "Johnny Olszewski"): {
        "lean": "guardrails",
        "summary": "Co-signed Maryland Democratic delegation letter to FERC demanding data-center-driven transmission costs not be passed to Maryland ratepayers.",
        "items": [
            {
             "what": "Co-signed Maryland Congressional delegation letter to FERC urging revision of PJM cost-allocation rules so Maryland consumers do not finance $2B in infrastructure built primarily for out-of-state data centers.",
             "date": "2026-07-28",
             "source": "https://mcclaindelaney.house.gov/media/press-releases/maryland-democrats-urge-ferc-protect-marylanders-rising-electricity-costs-due"},
        ],
        "as_of": "2026-11-21",
    },
    ("MD", "3", "Sarah Elfreth"): {
        "lean": "guardrails",
        "summary": "Co-signed Maryland Democratic delegation letter to FERC demanding data-center-driven transmission costs not be passed to Maryland ratepayers.",
        "items": [
            {
             "what": "Co-signed Maryland Congressional delegation letter to FERC urging revision of PJM cost-allocation rules so Maryland consumers do not finance $2B in infrastructure built primarily for out-of-state data centers.",
             "date": "2026-07-28",
             "source": "https://mcclaindelaney.house.gov/media/press-releases/maryland-democrats-urge-ferc-protect-marylanders-rising-electricity-costs-due"},
        ],
        "as_of": "2026-11-21",
    },
    ("MD", "4", "Glenn Ivey"): {
        "lean": "guardrails",
        "summary": "Co-signed Maryland Democratic delegation letter to FERC demanding data-center-driven transmission costs not be passed to Maryland ratepayers.",
        "items": [
            {
             "what": "Co-signed Maryland Congressional delegation letter to FERC urging revision of PJM cost-allocation rules so Maryland consumers do not finance $2B in infrastructure built primarily for out-of-state data centers.",
             "date": "2026-07-28",
             "source": "https://mcclaindelaney.house.gov/media/press-releases/maryland-democrats-urge-ferc-protect-marylanders-rising-electricity-costs-due"},
        ],
        "as_of": "2026-11-21",
    },
    ("MD", "6", "April McClain Delaney"): {
        "lean": "guardrails",
        "summary": "Joined the Maryland Congressional delegation's July 2026 letter urging FERC to protect Maryland ratepayers from roughly $2 billion in PJM-assigned costs for infrastructure built primarily for out-of-state data centers. Single joint letter.",
        "items": [
            {
             "what": "Joined, and issued the press release for, the Maryland Congressional delegation letter to FERC urging revision of PJM transmission cost-allocation rules so Maryland ratepayers do not pay roughly $2 billion for infrastructure needed primarily for out-of-state data centers; letter supports the Maryland Office of People's Counsel's FERC complaint.",
             "date": "2026-07-28",
             "source": "https://mcclaindelaney.house.gov/media/press-releases/maryland-democrats-urge-ferc-protect-marylanders-rising-electricity-costs-due"},
        ],
        "as_of": "2026-11-21",
    },
    ("MD", "8", "Jamie Raskin"): {
        "lean": "guardrails",
        "summary": "Co-signed Maryland Democratic delegation letter to FERC demanding data-center-driven transmission costs not be passed to Maryland ratepayers.",
        "items": [
            {
             "what": "Co-signed Maryland Congressional delegation letter to FERC urging revision of PJM cost-allocation rules so Maryland consumers do not finance $2B in infrastructure built primarily for out-of-state data centers.",
             "date": "2026-07-28",
             "source": "https://mcclaindelaney.house.gov/media/press-releases/maryland-democrats-urge-ferc-protect-marylanders-rising-electricity-costs-due"},
        ],
        "as_of": "2026-11-21",
    },
    ("PA", "1", "Brian Fitzpatrick"): {
        "lean": "mixed",
        "summary": "His campaign says he cosponsored the Ratepayer Protection Act and Data Center Transparency Act and wants '100% control by local residents who could be impacted.' He initially voted for the House OBBBA, which included a state/local AI regulation ban dropped from the final law, and he voted against the final version. Called the Falls Township Amazon data center transformative. Source is campaign statements in a news article.",
        "items": [
            {
             "what": "Per the Inquirer, his campaign spokesperson said he supports 'uniform federal regulations' and '100% control by local residents who could be impacted' and pointed to his cosponsorship of the Ratepayer Protection Act and the Data Center Transparency Act. The article notes his initial House vote for OBBBA (with a provision banning state/local AI regulation) and that he voted against the final version, which lacked the provision.",
             "date": "2026-09-10",
             "source": "https://www.inquirer.com/politics/election/bob-harvie-ai-data-centers-stance-tv-ad-20260910.html"},
        ],
        "as_of": "2026-11-21",
    },

    # ── KY/NY/MN deep dive, 2026-09-11 ──────────────────────────────────
    ("KY", "2", "Brett Guthrie"): {
        "lean": "mixed",
        "summary": "As House Energy and Commerce Chair, wrote an op-ed urging more energy production and permitting reform to power AI data centers and beat China, and signed a June 2026 letter asking PCAST and the FBI director to look into foreign influence campaigns against AI and data center buildout. Also said (WNKY, Jun 30, 2026) 'We can't have a moratorium that would cripple us' but 'We also have to respect local communities and ensure these data centers pay their own way.'",
        "items": [
            {
             "what": "Washington Times op-ed (posted by E&C): argued for expanded energy production for AI data centers and permitting reform, warned about China; said 'common-sense, tailored protections may be necessary'.",
             "date": "2025-03-27",
             "source": "https://energycommerce.house.gov/posts/chairman-guthrie-op-ed-driving-the-energy-future-of-ai-development"},
            {
             "what": "Signed a letter with Reps. Joyce and Latta to the PCAST co-chairs and FBI Director Kash Patel expressing worries about 'foreign influence campaigns targeting artificial intelligence'; told the Daily News there is 'reasonable suspicion' that opposition is backed by China.",
             "date": "2026-06-11",
             "source": "https://bgdailynews.com/2026/06/13/guthrie-calls-for-investigations-into-ai-data-center-opposition/"},
            {
             "what": "Told WNKY: 'We can't have a moratorium that would cripple us. We also have to respect local communities and ensure these data centers pay their own way.' Said 'there's a good reason to be concerned' and developers should cover infrastructure costs.",
             "date": "2026-06-30",
             "source": "https://www.wnky.com/congressman-brett-guthrie-weighs-in-on-data-center-debate/"},
        ],
        "as_of": "2026-11-21",
    },
    ("KY", "3", "Morgan McGarvey"): {
        "lean": "guardrails",
        "summary": "Sent a July 2026 letter to LG&E opposing the planned Camp Ground Road hyperscale data center in Louisville and asking who will pay for the upgrades. LPM reports he told a Louisville forum he opposes hyperscale data centers in the city and state and that residents should control what gets built.",
        "items": [
            {
             "what": "Sent a letter to LG&E President John Crockett III opposing the hyperscale data center planned for Camp Ground Road and demanding existing ratepayers not bear the cost; release says the 400 MW facility is a 63% increase in demand.",
             "date": "2026-07-09",
             "source": "https://mcgarvey.house.gov/media/press-releases/rep-mcgarvey-opposes-camp-ground-road-data-center-in-letter-to-lgande-dont-raise-louisvilles-rates-to-pay-for-it"},
            {
             "what": "LPM reported he told a forum he opposes hyperscale data center construction in Louisville and the state, and that residents should control what gets put into their community (headline: 'absolutely opposed'; his own quoted words: 'I am done with out-of-state corporations coming into our state, our home, our community, and using our resources').",
             "date": "2026-07-09",
             "source": "https://www.lpm.org/news/2026-07-09/kentucky-congressman-absolutely-opposed-to-in-state-hyperscale-data-centers"},
        ],
        "as_of": "2026-11-21",
    },
    ("NY", "17", "Mike Lawler"): {
        "lean": "accelerate",
        "summary": "On Fox Business (Aug. 18, 2026), criticized Gov. Hochul's statewide data center moratorium as telling companies 'don't come here', alongside broader complaints about New York taxes and energy policy. Single interview.",
        "items": [
            {
             "what": "On Fox Business's Mornings with Maria, said of Hochul's data center pause: 'What she is saying is, don't come here. Go do your business elsewhere, which is why New York State leads the nation in out-migration.' Also said New York has 'the highest tax burden and the worst business climate'.",
             "date": "2026-08-18",
             "source": "https://www.foxbusiness.com/media/new-york-republican-congressman-rips-hochul-policies-sending-businesses-dont-come-here-message"},
        ],
        "as_of": "2026-11-21",
    },
    ("MN", "6", "Tom Emmer"): {
        "lean": "accelerate",
        "summary": "Publicly embraced President Trump’s push for data center construction, citing competition with China.",
        "items": [
            {
             "what": "MinnPost reported Emmer “immediately embraced” Trump’s message of support for data centers. In a post on X he said Trump was “absolutely spot on” and that “Communist China and our adversaries would love it if the United States was asleep at the wheel and stopped innovating and developing AI and emerging tech.”",
             "date": "2026-09-03",
             "source": "https://www.minnpost.com/national/washington/2026/09/minnesota-gop-lawmakers-grapple-with-data-centers-as-republican-voters-turn-against-the-projects/"},
        ],
        "as_of": "2026-11-21",
    },
    ("MN", "1", "Brad Finstad"): {
        "lean": "mixed",
        "summary": "Supports data centers for economic and national security value but emphasizes local control and corporate transparency about environmental impacts.",
        "items": [
            {
             "what": "Said data centers \"can play an important role in our economic future and national security, but the decision...should be made by the people and local leaders who know their communities best, not handed down by Washington\"; emphasized need for corporate transparency.",
             "date": "2026-09-03",
             "source": "https://www.minnpost.com/national/washington/2026/09/minnesota-gop-lawmakers-grapple-with-data-centers-as-republican-voters-turn-against-the-projects/"},
        ],
        "as_of": "2026-11-21",
    },
    # ── Batch 4 deep dive — OR, AL, IL, OK — 2026-09-11 ─────────────────
    ("OR", "6", "Andrea Salinas"): {
        "lean": "guardrails",
        "summary": "Introduced the Data Center Community Reinvestment Act to tax data center electricity use at 1 cent/kWh and reinvest $1.76B/year into housing, conservation, clean energy, and infrastructure",
        "items": [
            {
             "what": "Introduced Data Center Community Reinvestment Act establishing 1-cent-per-kWh excise tax on data center electricity consumption (>1 MW capacity), directing $1.76B/year to Land and Water Conservation Fund, Housing Trust Fund, Superfund, Highway Trust Fund, and Energy Technology Trust Fund",
             "date": "2026-08-14",
             "source": "https://salinas.house.gov/media/press-releases/rep-salinas-introduces-bill-tax-data-centers-reinvest-housing-conservation-and"},
        ],
        "as_of": "2026-11-21",
    },
    ("AL", "7", "Terri Sewell"): {
        "lean": "guardrails",
        "summary": "Announced she cosponsors the AI Data Center Moratorium Act (sponsor: Rep. Ocasio-Cortez), which would stop new construction and large expansions of AI data centers until a federal framework is established; says she is not 'anti-AI'.",
        "items": [
            {
             "what": "Announced cosponsorship of the AI Data Center Moratorium Act, which would stop new construction and large expansions of AI data centers until a federal framework is established; said 'The bill simply says, let's put common sense guardrails in place before this expansion continues' and 'Responsible innovation and community protection are not competing goals—they are complementary ones.'",
             "date": "2026-07-21",
             "source": "https://aldailynews.com/sewell-wants-to-stop-new-data-centers-until-guardrails-are-implemented/"},
        ],
        "as_of": "2026-11-21",
    },
    ("AL", "2", "Shomari Figures"): {
        "lean": "guardrails",
        "summary": "At a Lowndes County event he asked residents whether they wanted a proposed 1,050-acre, $1.5B data center in Hayneville, and after they said no told them 'I'm with the people of Lowndes County'; the columnist adds he is not entirely opposed to hyperscale data centers but says companies should pick sites where communities want them; also a cosponsor of the AI Data Center Moratorium Act (H.R. 9442).",
        "items": [
            {
             "what": "At a Lowndes County event asked residents if they wanted the proposed 1,050-acre, $1.5B AI data center in Hayneville; when they said no, said 'Well, I'm with the people of Lowndes County.' Columnist reports he is not entirely opposed to hyperscale data centers but says companies need to pick sites where communities actually want them.",
             "date": "2026-08-01",
             "source": "https://www.alabamagazette.com/story/2026/08/01/news/where-alabamas-major-public-officials-stand-on-hyperscale-ai-data-centers/12100.html"},
            {
             "what": "Cosponsor of H.R. 9442, the AI Data Center Moratorium Act (sponsor Rep. Ocasio-Cortez), added 07/22/2026.",
             "date": "2026-07-22",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/9442/cosponsors"},
        ],
        "as_of": "2026-11-21",
    },
    ("IL", "6", "Sean Casten"): {
        "lean": "guardrails",
        "summary": "Co-led (with Rep. Levin) introduction of the Energy Bills Relief Act, which per the release ensures facilities like data centers pay for their own costs rather than pushing them onto households; the data-center provision is one line of a broader renewable-energy bill.",
        "items": [
            {
             "what": "Co-led, with Rep. Mike Levin, the introduction by 120 House Democrats of the Energy Bills Relief Act; release lists 'Ensuring that facilities like data centers are paying for their own costs because it's not fair for their expenses to be pushed onto your household'. Casten's own quoted remarks do not mention data centers.",
             "date": "2026-03-18",
             "source": "https://casten.house.gov/media/press-releases/ebra"},
        ],
        "as_of": "2026-11-21",
    },
    ("OK", "5", "Stephanie Bice"): {
        "lean": "mixed",
        "summary": "Acknowledged data center benefits but emphasized local communities must have a voice; applauded state ratepayer protection law",
        "items": [
            {
             "what": "Statement responding to President's comments on data centers: 'it is vital that local communities have a voice in the decisions on proposed data centers'; applauded Oklahoma legislature for passing ratepayer protection and groundwater laws",
             "date": "2026-08-31",
             "source": "https://kfor.com/news/local/president-comments-on-data-centers-in-usa/"},
        ],
        "as_of": "2026-11-21",
    },
    ("OK", "2", "Josh Brecheen"): {
        "lean": "guardrails",
        "summary": "At a town hall he said data center operators 'have to make sure that they are not driving up people's electricity costs' and that he co-sponsors a bill (HR9019) requiring the Energy Secretary to report to Congress on data center electricity and water use, while saying Congress is not going to create the regulatory environment.",
        "items": [
            {
             "what": "Town hall, McAlester: said operators 'have to make sure that they are not driving up people's electricity costs'; 'Congress is not gonna create the regulatory environment. What we can do is make sure people have information about the data centers.' Co-sponsors HR9019 requiring the Energy Secretary to report to Congress on data center electricity and water use.",
             "date": "2026-08-27",
             "source": "https://www.kjrh.com/news/local-news/brecheen-gives-views-on-data-centers-smelter-election-denial-in-mcalester"},
        ],
        "as_of": "2026-11-21",
    },
    # ── Batch 5 deep dive — KS, AR, ME, UT, NH — 2026-09-11 ─────────────
    ("KS", "3", "Sharice Davids"): {
        "lean": "guardrails",
        "summary": "No data center should move forward if it raises costs, wastes water, or shifts the burden onto Kansas communities",
        "items": [
            {
             "what": "Statement: 'no data center should move forward if it raises electricity costs for families, wastes our limited water resources, or shifts the burden onto Kansas communities'",
             "date": "2026-09-11",
             "source": "https://www.kshb.com/news/local-news/kansas/johnson-county/voters-guide-kansas-political-candidates-stances-on-data-center-development"},
        ],
        "as_of": "2026-11-21",
    },
    ("KS", "1", "Lauren Reinhold"): {
        "lean": "guardrails",
        "summary": "Supports community-approved projects with transparency, opposes tax breaks for data centers",
        "items": [
            {
             "what": "Statement supporting community-approved projects with transparency and opposing tax breaks for data centers; 'there is no one-size-fits-all approach for this district'",
             "date": "2026-09-11",
             "source": "https://www.kshb.com/news/local-news/kansas/johnson-county/voters-guide-kansas-political-candidates-stances-on-data-center-development"},
        ],
        "as_of": "2026-11-21",
    },
    ("KS", "2", "Derek Schmidt"): {
        "lean": "guardrails",
        "summary": "Per a secondhand summary of a town hall, advised that data center developers should not require tax abatements and should source power from new or supplemental sources to avoid raising local utility costs. The page does not state whether he supports data centers.",
        "items": [
            {
             "what": "Per Ranson Financial's summary of a CJonline report: at a town hall gave three tips for communities: developers should not require tax abatements; data centers should source power from new or supplemental sources to avoid raising local utility costs; modern data centers can be designed as closed systems that do not consume large amounts of water.",
             "date": "2026-06-10",
             "source": "https://ransonfinancial.com/2026/06/10/three-tips-for-kansas-communities-on-data-centers/"},
        ],
        "as_of": "2026-11-21",
    },
    ("AR", "4", "Bruce Westerman"): {
        "lean": "mixed",
        "summary": "At a town hall he framed AI as a Cold War race with China and said data centers are needed, and said water use is not as big an issue as some make it; he also said data center companies are willing to pay for new generation and transmission and that communities and the PSC should set water and electricity requirements and hold companies accountable.",
        "items": [
            {
             "what": "Town hall: 'We are in a Cold War with China on developing AI technology'; 'we have to develop AI. To develop AI, you have to have data centers'; on water, 'I don't think is as big an issue as what some people make it out to be'; said data center companies 'are willing to pay for that new generating equipment' and transmission, and that communities should define water and electrical requirements and hold the companies accountable.",
             "date": "2026-09-01",
             "source": "https://hopeprescott.com/2026/09/01/data-centers-crucial-to-america-winning-the-cold-war-with-china-on-ai-tech-according-to-congressman-westerman/"},
        ],
        "as_of": "2026-11-21",
    },
    ("ME", "2", "Paul LePage"): {
        "lean": "mixed",
        "summary": "Called himself 'a big, big fan of data centers' and said they will create jobs and help solve energy problems; his campaign said afterward that he supports 'sensible regulation,' including water supply guarantees, local community buy-in and no consumer rate hikes.",
        "items": [
            {
             "what": "Said 'I'm a big, big fan of data centers... I think they're going to create jobs. I think we can solve our energy problems' at a former mill site in Lincoln; downplayed water and power concerns. His campaign said Friday he supports 'sensible regulation,' including guarantees of adequate water supply, local community buy-in and no rate hikes for consumers.",
             "date": "2026-08-24",
             "source": "https://www.bangordailynews.com/2026/08/24/politics/elections/paul-lepage-big-fan-data-centers-joam40zk0w/"},
        ],
        "as_of": "2026-11-21",
    },
    ("ME", "2", "Matthew Dunlap"): {
        "lean": "guardrails",
        "summary": "Favors benchmarks for worker benefits, ratepayer protection, and community benefits from data centers",
        "items": [
            {
             "what": "Campaign warned 'if we don't approach these projects deliberately they will jack up energy prices'; favors developing benchmarks and standards for worker benefits, ratepayer impact, and community benefits",
             "date": "2026-08-24",
             "source": "https://www.bangordailynews.com/2026/08/24/politics/elections/paul-lepage-big-fan-data-centers-joam40zk0w/"},
        ],
        "as_of": "2026-11-21",
    },
    ("ME", "1", "Chellie Pingree"): {
        "lean": "guardrails",
        "summary": "Cosponsor of the AI Data Center Moratorium Act (H.R. 9442, added 09/14/2026) and the Power for the People Act (H.R. 8241, added 04/30/2026); in December 2025 a spokesperson said she believes Congress has a responsibility to put ‘strong, science-based protections in place’.",
        "items": [
            {
             "what": "Spokesperson Gabrielle Maninno said Pingree believes Congress has a responsibility to assess the environmental and consumer impacts of data center and AI expansion and put 'strong, science-based protections in place'.",
             "date": "2025-12-08",
             "source": "https://www.mainepublic.org/climate/2025-12-08/maine-groups-join-call-for-u-s-data-center-moratorium"},
            {
             "what": "Cosponsor of H.R. 9442, the AI Data Center Moratorium Act (sponsor Rep. Ocasio-Cortez), added 09/14/2026.",
             "date": "2026-09-14",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/9442/cosponsors"},
            {
             "what": "Cosponsor of H.R. 8241, the Power for the People Act of 2026 (sponsor Rep. Tonko), added 04/30/2026.",
             "date": "2026-04-30",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/8241/all-info"},
        ],
        "as_of": "2026-11-21",
    },
    ("UT", "1", "Ben McAdams"): {
        "lean": "mixed",
        "summary": "Opposes the proposed Box Elder County (Stratos) data center and calls for federal standards, but opponents at the May 27 debate raised his financial stake in a Millard County data center project, which he said was stock options and past consulting pay and that he had helped add renewable energy to it.",
        "items": [
            {
             "what": "Posted that 'Utah should welcome technology investment only when it aligns with our values: water stewardship, Great Salt Lake restoration, clean energy, transparency, public accountability, and real public benefit. This proposed data center project in Box Elder County does not meet that standard.'",
             "date": "2026-05-06",
             "source": "https://x.com/BenMcAdams/status/2052173399594528777"},
            {
             "what": "UT-1 Democratic debate: all four candidates opposed the Stratos Project; said 'What we need are federal standards to make sure that when, as the economy is transformed, that the American people are the ones who benefit'. Opponents pointed to his financial stake in a data center project near Delta in Millard County; he said he was 'the only candidate who has worked to make a data center better by adding renewable energy' and described the stake as stock options and consulting pay from two years ago.",
             "date": "2026-05-27",
             "source": "https://www.kuer.org/politics-government/2026-05-27/1st-district-debate-zeroes-in-on-utah-hot-topics-like-ai-data-centers-and-housing"},
        ],
        "as_of": "2026-11-21",
    },
    ("UT", "2", "Blake Moore"): {
        "lean": "mixed",
        "summary": "Introduced bill requiring study of AI data center impacts in rural America while supporting Utah as tech hub",
        "items": [
            {
             "what": "Introduced bipartisan 'Unleashing Low-Cost Rural AI Act' requiring DOE, Interior, and Agriculture to study how AI data center expansions impact rural America — energy supply, reliability, consumer costs, and infrastructure",
             "date": "2025-09-16",
             "source": "https://blakemoore.house.gov/media/press-releases/representatives-moore-costa-introduce-legislation-to-study-impact-of-artificial-intelligence-in-rural-america"},
        ],
        "as_of": "2026-11-21",
    },
    ("NH", "1", "Stefany Shaheen"): {
        "lean": "guardrails",
        "summary": "Strongly supports moratorium; municipalities not yet prepared for data center complexity",
        "items": [
            {
             "what": "Stated 'I feel very strongly we need a moratorium. Our municipalities are not yet prepared to handle the complexity of what these kinds of projects could mean for their communities'",
             "date": "2026-09-07",
             "source": "https://spectrumnews1.com/ma/worcester/news/2026/09/08/new-hampshire-data-centers-shaheen-pappas-ayotte"},
        ],
        "as_of": "2026-11-21",
    },
    ("NH", "2", "Maggie Goodlander"): {
        "lean": "guardrails",
        "summary": "At the WMUR debate she said communities elsewhere are seeing more than 200% energy price increases from data centers, that people and communities 'have got to have the ultimate say in whether a data center comes into their community', and that there must be transparency and accountability with the corporations paying the price rather than taxpayers (reporter's paraphrase).",
        "items": [
            {
             "what": "Debate (WMUR, via InDepthNH): said some communities are seeing more than 200% increases in energy prices because of data centers; people and communities 'have got to have the ultimate say in whether a data center comes into their community'; reporter paraphrases her as calling for transparency and accountability and for the corporations to pay rather than taxpayers.",
             "date": "2026-09-03",
             "source": "https://indepthnh.org/2026/09/03/congressional-district-2-democratic-primary-candidates-debate-housing-immigration-and-data-centers/"},
        ],
        "as_of": "2026-11-21",
    },
    ("NH", "2", "Paige Beauchemin"): {
        "lean": "guardrails",
        "summary": "At the WMUR debate she said she supports stopping construction of any data centers until legislation can be introduced to regulate them (reporter's paraphrase), with regulations ensuring environmental impact studies, utility costs paid by the companies, and local control.",
        "items": [
            {
             "what": "Debate (WMUR, via InDepthNH): reporter says she supports stopping the construction of any data centers until legislation can be introduced to regulate the issue; quoted: 'Those kinds of regulations need to ensure that environmental impact studies initially and ongoing, they need to ensure that utility costs are paid for by the companies and not from the other folks, and we also need to make sure that the local folks have their own local control.'",
             "date": "2026-09-03",
             "source": "https://indepthnh.org/2026/09/03/congressional-district-2-democratic-primary-candidates-debate-housing-immigration-and-data-centers/"},
        ],
        "as_of": "2026-11-21",
    },
    ("NH", "2", "Lily Tang Williams"): {
        "lean": "guardrails",
        "summary": "At the WMUR GOP debate said 'no government perks, credits and taxpayer dollars should be involved' and that a private company that wants to build data centers must respect local control and address concerns about environmental impact and electricity costs.",
        "items": [
            {
             "what": "GOP debate (WMUR, via InDepthNH): 'I would say no government perks, credits and taxpayer dollars should be involved. If a private company wants to come here, build data centers, then they need to respect our local control and address our concerns of environmental impact and electricity costs.'",
             "date": "2026-09-01",
             "source": "https://indepthnh.org/2026/09/01/orlando-stakes-position-as-working-class-alternative-to-tang-williams-in-nh-02-gop-debate/"},
        ],
        "as_of": "2026-11-21",
    },

    # ── Batch 6 deep dive — CT, NV, NM, DE, NE — 2026-09-11 ─────────────
    ("CT", "1", "Luke Bronin"): {
        "lean": "guardrails",
        "summary": "Called for ‘sensible artificial intelligence regulation’ in his primary-night speech; the American Prospect reported in May 2026 that he has called for regulation requiring data center developers to pay their fair share (a secondhand characterisation, not a quote).",
        "items": [
            {
             "what": "Victory speech called for 'sensible artificial intelligence regulation'; published platform says 'We need guardrails' against algorithmic addiction of kids and 'machines that act without human input or oversight'. The article records no data-center position.",
             "date": "2026-08-11",
             "source": "https://www.techtimes.com/articles/324305/20260813/bronin-routs-larson-21-points-connecticut-primary-adds-ai-guardrails-voice-congress.htm"},
            {
             "what": "The American Prospect wrote that, despite donations from billionaires with a stake in the data center build-out, Bronin “has called for regulation requiring data center developers to pay their fair share.” The article does not quote him or say where he said it.",
             "date": "2026-05-21",
             "source": "https://prospect.org/2026/05/21/meet-connecticuts-billionaire-backed-dark-money-democrat-bronin-larson-congress/"},
        ],
        "as_of": "2026-11-21",
    },
    ("NV", "1", "Dina Titus"): {
        "lean": "guardrails",
        "summary": "Pressed BLM for public consultation and transparency on data centers on federal land (Boulder City) and asked the governor to halt state tax abatements for such projects until the 2027 Legislature reviews.",
        "items": [
            {
             "what": "Letter to BLM (sent July 8) asking for 'robust public consultation and transparency' in permitting data centers on public land; said the BLM let a developer switch from a solar farm to a data center on federal land 'without any public review. This is unacceptable.'",
             "date": "2026-07-08",
             "source": "https://titus.house.gov/news/documentsingle.aspx?DocumentID=5916"},
            {
             "what": "Asked Gov. Lombardo to refrain from approving data center tax abatements for projects on BLM land until the Legislature reconvenes to reconsider; the governor's reply did not commit to halting abatements.",
             "date": "2026-08-17",
             "source": "https://titus.house.gov/news/documentsingle.aspx?DocumentID=5926"},
            {
             "what": "Nevada Independent: described the permitting process she wants for data centers on federal land as 'Full environmental permitting process with consideration for water and also public consultation and hearings'.",
             "date": "2026-08-01",
             "source": "https://thenevadaindependent.com/article/what-do-nevadas-congressional-candidates-think-about-data-centers"},
        ],
        "as_of": "2026-11-21",
    },
    ("NV", "1", "Carrie Buck"): {
        "lean": "accelerate",
        "summary": "Wants to make it easier to build AI energy and infrastructure",
        "items": [
            {
             "what": "NV Independent survey: federal government should 'make it easier to build the energy and infrastructure America needs to lead in AI'",
             "date": "2026-08-01",
             "source": "https://thenevadaindependent.com/article/what-do-nevadas-congressional-candidates-think-about-data-centers"},
        ],
        "as_of": "2026-11-21",
    },
    ("NV", "2", "Teresa Benitez-Thompson"): {
        "lean": "guardrails",
        "summary": "Supports local control over data center regulation; opposes federal preemption of state/local authority",
        "items": [
            {
             "what": "NV Independent survey: does not want federal actions to prevent state or local governments from taking their own regulatory action on data centers",
             "date": "2026-08-01",
             "source": "https://thenevadaindependent.com/article/what-do-nevadas-congressional-candidates-think-about-data-centers"},
        ],
        "as_of": "2026-11-21",
    },
    ("NV", "2", "David Flippo"): {
        "lean": "mixed",
        "summary": "Opposes tax abatements for data centers; supports local decision-making but would support federal involvement for national security",
        "items": [
            {
             "what": "NV Independent survey: 'The best decisions are made at the most local level possible.' Opposes tax abatements; would support federal involvement only for national security protection",
             "date": "2026-08-01",
             "source": "https://thenevadaindependent.com/article/what-do-nevadas-congressional-candidates-think-about-data-centers"},
        ],
        "as_of": "2026-11-21",
    },
    ("NV", "3", "Susie Lee"): {
        "lean": "mixed",
        "summary": "Toured a Switch AI factory with Leader Jeffries and praised the jobs; told the Nevada Independent she backs water-consumption disclosure and potentially energy-efficiency standards.",
        "items": [
            {
             "what": "Toured Switch AI factory in Las Vegas with Democratic Leader Jeffries; said 'Switch is bringing the cutting edge of AI innovation right here to southern Nevada' and that the factories 'will help create good-paying jobs'.",
             "date": "2025-08-29",
             "source": "https://susielee.house.gov/media/press-releases/icymi-congresswoman-lee-leader-jeffries-tour-new-cutting-edge-ai-factory-will"},
            {
             "what": "Nevada Independent: said there should be disclosure requirements on water consumption and potentially energy efficiency standards. The article reports almost all candidates opposed a blanket federal pause on data centers.",
             "date": "2026-08-01",
             "source": "https://thenevadaindependent.com/article/what-do-nevadas-congressional-candidates-think-about-data-centers"},
        ],
        "as_of": "2026-11-21",
    },
    ("NV", "3", "Martin O'Donnell"): {
        "lean": "guardrails",
        "summary": "Supports legislation ensuring local communities are not negatively affected; backs water usage disclosure",
        "items": [
            {
             "what": "NV Independent survey: supports legislation ensuring local communities are not negatively affected by data centers; backs water usage disclosure requirements",
             "date": "2026-08-01",
             "source": "https://thenevadaindependent.com/article/what-do-nevadas-congressional-candidates-think-about-data-centers"},
        ],
        "as_of": "2026-11-21",
    },
    ("NV", "4", "Steven Horsford"): {
        "lean": "mixed",
        "summary": "Backs federal energy and water disclosure standards that states can exceed and kept the door open to a future moratorium; also joined an OpenAI workforce-training event.",
        "items": [
            {
             "what": "Nevada Independent: said the federal government should set standards requiring disclosure of energy and water use; states should be allowed to 'go further' ('a national standard should act as a floor we can build on, never a ceiling'). The only candidate who kept the door open to a federal moratorium in future.",
             "date": "2026-08-01",
             "source": "https://thenevadaindependent.com/article/what-do-nevadas-congressional-candidates-think-about-data-centers"},
            {
             "what": "Release announced he would join OpenAI and Rep. Khanna at a College of Southern Nevada AI workforce-training event; says he helped secure almost $7 million for CSN's Westside Education and Training Center.",
             "date": "2026-04-24",
             "source": "https://horsford.house.gov/media/press-releases/rep-horsford-joins-openai-rep-ro-khanna-and-college-of-southern-nevada-csn-to-expand-ai-workforce-training-in-north-las-vegas"},
            {
             "what": "At a town hall on AI and automation with Khanna, advocated advance notice and training for workers and collective bargaining as accountability tools (about worker automation, not data centers).",
             "date": "2026-08-19",
             "source": "https://lasvegassun.com/news/2026/aug/20/las-vegas-union-workers-reps-ro-khanna-and-steven/"},
        ],
        "as_of": "2026-11-21",
    },
    ("NV", "4", "Cody Whipple"): {
        "lean": "mixed",
        "summary": "Supports unspecified 'common-sense frameworks' protecting Nevada's resources while fostering innovation, and calls data centers a national security issue; no concrete proposal on costs, siting or a pause.",
        "items": [
            {
             "what": "Nevada Independent: written response supports 'common-sense frameworks that safeguard Nevada's natural resources while fostering technological innovation'; campaign later said he wants local water, agricultural and technology officials to inform federal standards. At a closed-door event recording he called data centers a 'national security issue for us'.",
             "date": "2026-08-01",
             "source": "https://thenevadaindependent.com/article/what-do-nevadas-congressional-candidates-think-about-data-centers"},
        ],
        "as_of": "2026-11-21",
    },
    ("NM", "1", "Melanie Stansbury"): {
        "lean": "guardrails",
        "summary": "Demanded water accountability for Project Jupiter from five NM state officials",
        "items": [
            {
             "what": "Formal letter to five NM state officials demanding written answers on Project Jupiter's water use, water rights, permits, and Rio Grande Compact compliance; called it 'an important test case for how New Mexico evaluates major industrial water users'",
             "date": "2026-08-24",
             "source": "https://stansbury.house.gov/media/press-releases/rep-stansbury-demands-answers-project-jupiters-water-use-new-mexico-supreme"},
        ],
        "as_of": "2026-11-21",
    },
    ("NM", "2", "Gabe Vasquez"): {
        "lean": "guardrails",
        "summary": "Called on Socorro County in May 2026 to approve a temporary data center moratorium, cosponsors the Data Center Water and Energy Transparency Act (H.R. 9825), and announced support for the FAIR Data Act (H.R. 9655).",
        "items": [
            {
             "what": "Told Source NM he encourages the county to approve the temporary moratorium it was considering on the proposed Socorro County data center, saying the proposal “should not be considered at this time.”",
             "date": "2026-05-26",
             "source": "https://sourcenm.com/2026/05/26/us-rep-vasquez-calls-for-new-mexico-county-to-approve-data-center-moratorium/"},
            {
             "what": "Per his Aug 25 release, was 'the only statewide or federal official' to publicly call for an end to the Socorro County data center proposal; the developer pulled out and commissioners unanimously approved a one-year moratorium.",
             "date": "2026-08-25",
             "source": "https://vasquez.house.gov/media/press-releases/rep-gabe-vasquez-demands-accountability-data-center-developers-reiterates-new"},
            {
             "what": "Announced support for the FAIR Data Act (H.R. 9655), which would force large corporate electricity users to pay their own way so residential customers and small businesses do not cover data center costs.",
             "date": "2026-08-25",
             "source": "https://vasquez.house.gov/media/press-releases/rep-gabe-vasquez-demands-accountability-data-center-developers-reiterates-new"},
            {
             "what": "Cosponsor of H.R. 9825, the Data Center Water and Energy Transparency Act of 2026 (sponsor Rep. Underwood), whose official title is to require data center operators to submit reports on data center energy and water use; added as a cosponsor 08/13/2026.",
             "date": "2026-08-13",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/9825/all-info"},
        ],
        "as_of": "2026-11-21",
    },
    ("NE", "3", "Adrian Smith"): {
        "lean": "accelerate",
        "summary": "Praised AI efficiency gains and said 'we should not stand in the way' at a summit where the delegation was reported to advocate for data centers amid county moratoriums; no safeguards or specifics offered.",
        "items": [
            {
             "what": "At Nebraska energy summit: 'The efficiencies that can be achieved already with AI, it's amazing... We should not stand in the way. We should celebrate how much better lives can be with more economic efficiency out there that can be a result of AI.' Article reports the delegation advocated for data centers while a dozen-plus counties weighed moratoriums, and that members said AI should have rules without specifics.",
             "date": "2026-08-12",
             "source": "https://nebraskapublicmedia.org/en/news/news-articles/nebraskas-federal-representatives-talk-energy-chinese-competition-and-iran-at-summit/"},
        ],
        "as_of": "2026-11-21",
    },

    # ── H.R. 9442, AI Data Center Moratorium Act + research batch 2026-09-12 ─
    ("NY", "14", "Alexandria Ocasio-Cortez"): {
        "lean": "guardrails",
        "summary": "Introduced the Artificial Intelligence Data Center Moratorium Act, the House version of Sen. Sanders' bill: a temporary ban on new data centers and expansion until Congress passes comprehensive AI legislation and safeguards.",
        "items": [
            {
             "what": "Introduced the Artificial Intelligence Data Center Moratorium Act, a temporary prohibition on construction of new data centers and expansion of existing ones until national safeguards (including that AI does not increase electricity and utility prices) are in place; requires reporting on water, energy, wastewater and wages.",
             "date": "2026-06-24",
             "source": "https://ocasio-cortez.house.gov/media/press-releases/ocasio-cortez-introduces-house-version-ai-data-center-moratorium-act"},
        ],
        "as_of": "2026-11-21",
    },
    ("IN", "7", "André Carson"): {
        "lean": "guardrails",
        "summary": "Original cosponsor of the AI Data Center Moratorium Act (H.R. 9442) and of the AI Data Center Site Selection Transparency Act (H.R. 8488, sponsor Rep. McIver), which requires developers to disclose site plans at least 180 days ahead.",
        "items": [
            {
             "what": "In a release on the AI Data Center Moratorium Act (H.R. 9442, of which he is an original cosponsor) he said: 'Our bill would enact a pause until we can guarantee common sense protections.'",
             "date": "2026-06-29",
             "source": "https://carson.house.gov/media/press-releases/carson-introduces-data-center-moratorium-bill"},
            {
             "what": "Listed as a cosponsor of the House AI Data Center Moratorium Act in Ocasio-Cortez's release.",
             "date": "2026-06-24",
             "source": "https://ocasio-cortez.house.gov/media/press-releases/ocasio-cortez-introduces-house-version-ai-data-center-moratorium-act"},
            {
             "what": "Original cosponsor (04/23/2026) of H.R. 8488, the AI Data Center Site Selection Transparency Act of 2026, sponsored by Rep. McIver. Its text requires developers, 180 days before a definitive step, to disclose the site location and estimated resource needs and environmental impact to local elected officials and the public, and limits non-disclosure agreements.",
             "date": "2026-04-23",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/8488/cosponsors"},
        ],
        "as_of": "2026-11-21",
    },
    # Bonnie Watson Coleman (NJ-12): retiring, not on 2026 ballot.
    ("IL", "14", "Lauren Underwood"): {
        "lean": "guardrails",
        "summary": "Sponsor of the Data Center Water and Energy Transparency Act (H.R. 9825), which would require data center operators to report energy and water use.",
        "items": [
            {
             "what": "Introduced H.R. 9825, the Data Center Water and Energy Transparency Act of 2026. Its official title: to require data center operators to submit to States or the EPA Administrator and the Secretaries of Energy and Agriculture reports on data center energy and water use. Referred to House Energy and Commerce.",
             "date": "2026-07-22",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/9825/all-info"},
        ],
        "as_of": "2026-11-21",
    },
    ("NJ", "8", "Rob Menendez"): {
        "lean": "guardrails",
        "summary": "Co-introduced the PRICE Act and the Data Center Transparency Act with Rep. Casar, and cosponsors the Data Center Community Impact Act (a federal impact study).",
        "items": [
            {
             "what": "Co-introduced the PRICE Act (require data centers to generate the electricity they consume; 75% renewable by 2035, 100% by 2040) and the Data Center Transparency Act (EPA quarterly and EIA semi-annual data collection) with Rep. Casar.",
             "date": "2026-01-08",
             "source": "https://menendez.house.gov/media/press-releases/-menendez-casar-introduce-groundbreaking-legislation-to-protect-americans-from-financial-and-environmental-impacts-of-ai-data-centers"},
            {
             "what": "Listed as a cosponsor of the Data Center Community Impact Act, which would authorize a federal study of data centers' environmental, economic and public health impacts.",
             "date": "2026-03-06",
             "source": "https://watsoncoleman.house.gov/newsroom/press-releases/rep-watson-coleman-introduces-bill-to-study-impact-of-ai-data-centers-on-local-communities"},
        ],
        "as_of": "2026-11-21",
    },
    ("TX", "37", "Greg Casar"): {
        "lean": "guardrails",
        "summary": "Co-introduced the PRICE Act and Data Center Transparency Act with Rep. Menendez; said 'AI data centers should not be allowed to jack up your electric bill or poison your environment.'; also a cosponsor of the AI Data Center Moratorium Act (H.R. 9442).",
        "items": [
            {
             "what": "Co-introduced the PRICE Act and Data Center Transparency Act with Rep. Menendez; quoted: 'Families should not pay more for utilities so that billionaires can get rich off AI data centers' and 'AI data centers should not be allowed to jack up your electric bill or poison your environment.'",
             "date": "2026-01-08",
             "source": "https://menendez.house.gov/media/press-releases/-menendez-casar-introduce-groundbreaking-legislation-to-protect-americans-from-financial-and-environmental-impacts-of-ai-data-centers"},
            {
             "what": "Cosponsor of H.R. 9442, the AI Data Center Moratorium Act (sponsor Rep. Ocasio-Cortez), added 09/17/2026.",
             "date": "2026-09-17",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/9442/cosponsors"},
        ],
        "as_of": "2026-11-21",
    },
    ("CA", "15", "Kevin Mullin"): {
        "lean": "guardrails",
        "summary": "Led a 20-member congressional letter to FERC, Edison Electric Institute, and the Data Center Coalition on data center energy cost pass-throughs to consumers.",
        "items": [
            {
             "what": "Led a group of 20 House members in a letter to FERC, Edison Electric Institute, and the Data Center Coalition expressing concern that data center energy costs are being passed onto consumers and requesting information on consumer protections.",
             "date": "2025-10-28",
             "source": "https://kevinmullin.house.gov/2025/10/28/rep-mullin-leads-group-of-lawmakers-investigating-impact-of-data-centers-on-energy-costs/"},
        ],
        "as_of": "2026-11-21",
    },
    ("NJ", "2", "Jeff Van Drew"): {
        "lean": "guardrails",
        "summary": "Introduced the bipartisan FAIR Data Act with Rep. Riley, to keep data center grid-upgrade costs from households and small businesses.",
        "items": [
            {
             "what": "With Rep. Riley, introduced the FAIR Data Act, which prohibits utilities from passing grid upgrade costs for very large (75+ MW) data centers onto households and small businesses; said companies behind these projects should 'cover those added costs instead of passing them on to ratepayers'.",
             "date": "2026-07-13",
             "source": "https://riley.house.gov/2026/07/13/riley-introduces-bill-to-stop-data-center-projects-from-driving-up-energy-bills/"},
        ],
        "as_of": "2026-11-21",
    },
    ("NJ", "10", "LaMonica McIver"): {
        "lean": "guardrails",
        "summary": "Sponsor of the AI Data Center Site Selection Transparency Act (H.R. 8488) and cosponsor of the AI Data Center Moratorium Act (H.R. 9442).",
        "items": [
            {
             "what": "Introduced H.R. 8488, the AI Data Center Site Selection Transparency Act of 2026 (04/23/2026). Its text requires developers, 180 days before a definitive step, to disclose the site location and estimated resource needs and environmental impact to local elected officials and the public, limits non-disclosure agreements, and requires a developer-funded independent environmental impact analysis.",
             "date": "2026-04-23",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/8488/text"},
            {
             "what": "Cosponsor of H.R. 9442, the AI Data Center Moratorium Act (sponsor Rep. Ocasio-Cortez), added 06/29/2026.",
             "date": "2026-06-29",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/9442/cosponsors"},
        ],
        "as_of": "2026-11-21",
    },
    # Dan Goldman (NY-10): lost renomination, not on 2026 ballot.
    ("MA", "2", "Jim McGovern"): {
        "lean": "guardrails",
        "summary": "Listed as a cosponsor of H.R. 9442, the AI Data Center Moratorium Act, when Ocasio-Cortez introduced it on June 24, 2026. This is the only evidence on record; no statement from him was located.",
        "items": [
            {
             "what": "Listed among the cosponsors of H.R. 9442, the AI Data Center Moratorium Act, which would institute an immediate federal moratorium on construction of new data centers and expansion of existing ones until Congress passes comprehensive AI legislation.",
             "date": "2026-06-24",
             "source": "https://ocasio-cortez.house.gov/media/press-releases/ocasio-cortez-introduces-house-version-ai-data-center-moratorium-act"},
        ],
        "as_of": "2026-11-21",
    },
    # Steve Cohen (TN-9): retiring, not on 2026 ballot.
    # Chuy García (IL-4): retiring, not on 2026 ballot.
    ("AZ", "7", "Adelita Grijalva"): {
        "lean": "guardrails",
        "summary": "Cosponsored the AI Data Center Moratorium Act and the Data Center Community Impact Act.",
        "items": [
            {
             "what": "Original cosponsor of H.R. 9442, the AI Data Center Moratorium Act.",
             "date": "2026-06-24",
             "source": "https://ocasio-cortez.house.gov/media/press-releases/ocasio-cortez-introduces-house-version-ai-data-center-moratorium-act"},
            {
             "what": "Cosponsored H.R. 7858, the Data Center Community Impact Act.",
             "date": "2026-03-06",
             "source": "https://watsoncoleman.house.gov/newsroom/press-releases/rep-watson-coleman-introduces-bill-to-study-impact-of-ai-data-centers-on-local-communities"},
        ],
        "as_of": "2026-11-21",
    },
    ("CA", "43", "Maxine Waters"): {
        "lean": "guardrails",
        "summary": "Cosponsored the AI Data Center Moratorium Act.",
        "items": [
            {
             "what": "Cosponsored H.R. 9442, the AI Data Center Moratorium Act.",
             "date": "2026-07-13",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/9442/cosponsors"},
        ],
        "as_of": "2026-11-21",
    },
    ("CA", "10", "Mark DeSaulnier"): {
        "lean": "guardrails",
        "summary": "Cosponsored the AI Data Center Moratorium Act.",
        "items": [
            {
             "what": "Cosponsored H.R. 9442, the AI Data Center Moratorium Act.",
             "date": "2026-07-21",
             "source": "https://www.congress.gov/bill/119th-congress/house-bill/9442/cosponsors"},
        ],
        "as_of": "2026-11-21",
    },
    ("IL", "3", "Delia Ramirez"): {
        "lean": "guardrails",
        "summary": "Voted no on the Ratepayer Protection Act — not against making data centers pay, but because, she said, it only suggests states act and does not address the threats data centers pose to her district.",
        "items": [
            {
             "what": "One of three members to vote no on H.R. 9340, the Ratepayer Protection Act (passed 417-3). To NBC News: the bill “does not address the concerns of our constituents and the threats that data centers pose,” and “my district is demanding more than a bill that suggests states take action.”",
             "date": "2026-09-16",
             "source": "https://www.nbcnews.com/politics/congress/house-passes-bill-shield-consumers-data-center-price-hikes-energy-rcna597683"},
        ],
        "as_of": "2026-11-21",
    },
    ("PA", "12", "Summer Lee"): {
        "lean": "guardrails",
        "summary": "Cosponsored the Data Center Community Impact Act requiring DOE to study effects on communities of color and low-income communities. Voted no on the Ratepayer Protection Act as too weak on pollution and health.",
        "items": [
            {
             "what": "Cosponsored H.R. 7858, the Data Center Community Impact Act.",
             "date": "2026-03-06",
             "source": "https://watsoncoleman.house.gov/newsroom/press-releases/rep-watson-coleman-introduces-bill-to-study-impact-of-ai-data-centers-on-local-communities"},
            {
             "what": "One of three members to vote no on H.R. 9340, the Ratepayer Protection Act (passed 417-3), saying it would not guarantee lower rates and “pays lip service to affordability talking points and doesn't address the water and noise pollution or the environmental and health concerns that continue to harass frontline communities that data centers are strategically placed in.”",
             "date": "2026-09-16",
             "source": "https://www.nbcnews.com/politics/congress/house-passes-bill-shield-consumers-data-center-price-hikes-energy-rcna597683"},
        ],
        "as_of": "2026-11-21",
    },
    # ── Batch 7: AZ, MT, AK — 2026-09-12 ────────────────────────────────
    ("AZ", "4", "Greg Stanton"): {
        "lean": "guardrails",
        "summary": "Named as a cosponsor of the Responsible Data Center Siting Act (H.R. 10321), which would direct the Energy Secretary to establish best practices for siting data centers. One cosponsorship is the only evidence; the page does not list him on the package's other bills.",
        "items": [
            {
             "what": "Named as a cosponsor of the Responsible Data Center Siting Act, which would direct the Secretary of Energy to establish best practices for siting data centers considering energy availability, utility bills, water and electricity use, the environment, and community impacts such as noise.",
             "date": "2026-09-08",
             "source": "https://subramanyam.house.gov/media/press-releases/rep-subramanyam-introduces-national-data-center-plan"},
        ],
        "as_of": "2026-11-21",
    },
    ("AZ", "6", "JoAnna Mendoza"): {
        "lean": "guardrails",
        "summary": "Says no data centers in the desert 'right now'; argues they should not sit near residential areas, citing Arizona State University research on heat and concern about energy bills.",
        "items": [
            {
             "what": "Said: 'No data centers in the desert... Not right now, not in our district, not in our state.' Also said 'We can't have data centers near residential areas,' citing ASU research that air-cooled data centers emit heat 'anywhere between two to four degrees more,' and warned energy bills would go up.",
             "date": "2026-08-14",
             "source": "https://blogforarizona.net/201903-2/"},
        ],
        "as_of": "2026-11-21",
    },
    # Adelita Grijalva (AZ-7): duplicate removed, richer entry above at line ~1791.
    ("MT", "2", "Troy Downing"): {
        "lean": "mixed",
        "summary": "Supports data centers with local control and water rights protections",
        "items": [
            {
             "what": "Stated 'Data centers can bring investment and opportunity to Montana, but these decisions should be made by the communities that will live with them'; called for 'light-touch' federal approach; insisted 'Montana's senior water rights must be protected'",
             "date": "2026-09-12",
             "source": "https://homenewshere.com/national/news/article_5c76009c-97fc-5c0e-841e-126c000d2d21.html"},
        ],
        "as_of": "2026-11-21",
    },
    ("MT", "2", "Brian Miller"): {
        "lean": "guardrails",
        "summary": "Emphasizes local control and transparency; served as legal counsel for citizens challenging data center development",
        "items": [
            {
             "what": "Served as legal counsel for citizens challenging Quantica data center development in Yellowstone County; stated 'We need to have maximum local control and respect state sovereignty on data centers'; criticized NDAs hiding operational details",
             "date": "2026-09-12",
             "source": "https://homenewshere.com/national/news/article_5c76009c-97fc-5c0e-841e-126c000d2d21.html"},
        ],
        "as_of": "2026-11-21",
    },
    ("MT", "2", "Michael Eisenhauer"): {
        "lean": "mixed",
        "summary": "Supports local decision-making with conditions; not opposed to data centers but wants protections",
        "items": [
            {
             "what": "Stated 'I think local control is the way it needs to be. I am not in favor of a mandate either for or against'; has 5-Pillar policy including closed-loop cooling, worker/ratepayer protections, and community final approval",
             "date": "2026-09-12",
             "source": "https://homenewshere.com/national/news/article_5c76009c-97fc-5c0e-841e-126c000d2d21.html"},
        ],
        "as_of": "2026-11-21",
    },
    ("MT", "2", "Patrick McCracken"): {
        "lean": "guardrails",
        "summary": "Highlights environmental and resource concerns; notes unaddressed electrical and water impacts",
        "items": [
            {
             "what": "Stated 'most people would not want to live next door to a data center'; highlighted unaddressed electrical and water resource impacts; referenced Montana's constitutional guarantee of healthful environment",
             "date": "2026-09-12",
             "source": "https://homenewshere.com/national/news/article_5c76009c-97fc-5c0e-841e-126c000d2d21.html"},
        ],
        "as_of": "2026-11-21",
    },
    # --- batch 8 (2026-09-12): MA, LA, RI, ND ---
    ("MA", "3", "Lori Trahan"): {
        "lean": "guardrails",
        "summary": "Spoke in favor of the Ratepayer Protection Act and H.R. 6529 at the July 21, 2026 Energy and Commerce markup, saying 'If you build the data center, you pay for the data center,' while calling both only 'good first steps' that do not fully address water or grid-priority concerns.",
        "items": [
            {
             "what": "At the Energy and Commerce markup she supported passage of the Ratepayer Protection Act and the Protecting Families from AI Data Center Energy Costs Act (H.R. 6529). Said: 'If you build the data center, you pay for the data center.' Said both are 'good first steps' but 'don't fully address the water these facilities draw from our communities.'",
             "date": "2026-07-21",
             "source": "https://trahan.house.gov/news/documentsingle.aspx?DocumentID=3815"},
        ],
        "as_of": "2026-11-21",
    },
    ("LA", "1", "Steve Scalise"): {
        "lean": "accelerate",
        "summary": "Promotes the economic benefits of data centers (a Louisiana school-bonus example) and says data centers are 'paying their own way'; said Republicans are investigating whether China is behind 'misinformation' against data centers. Whether he backed the Ratepayer Protection Act floor vote is not established by a page that could be read.",
        "items": [
            {
             "what": "Article says he highlights a Richland Parish, LA data center that paid every schoolteacher in the parish a $50,000 bonus. Quoted: 'They're good customers, they're good neighbors, and studies prove that they don't add to the cost of the grid. They're paying their own way.'",
             "date": "2026-09-10",
             "source": "https://www.moderntreatise.com/the-americas/2026/9/3/in-america-gop-under-pressure-to-pass-data-center-legislation-before-midterms"},
            {
             "what": "Told Fox Business: 'We are investigating whether China is behind a lot of this misinformation, false information against data centers,' and said Republicans are 'finding some things,' including Beijing-controlled social media bots.",
             "date": "2026-09-01",
             "source": "https://www.ms.now/rachel-maddow-show/maddowblog/data-centers-scalise-trump-republicans-china-conspiracy-theory-gop-elections-midterms"},
        ],
        "as_of": "2026-11-21",
    },
    ("ND", "AL", "Julie Fedorchak"): {
        "lean": "mixed",
        "summary": "Frames AI energy supply as national competitiveness ('To be AI dominant, we must first be energy dominant') and, at an April 2026 hearing, pressed the principle that those who drive the need for new energy infrastructure should pay for it, including large loads such as data centers.",
        "items": [
            {
             "what": "Announced the next step of her AI and Energy Working Group, an RFI on AI energy demand with a topic titled 'Strategic Competition: Outpacing China.' Said: 'To be AI dominant, we must first be energy dominant.'",
             "date": "2025-03-10",
             "source": "https://fedorchak.house.gov/media/press-releases/fedorchak-issues-request-information-address-ais-growing-energy-demands"},
            {
             "what": "At the Energy Subcommittee hearing 'AI and the Grid: Meeting Growing Power Demand While Protecting Ratepayers,' emphasized that those who drive the need for new energy infrastructure should pay for it (press release paraphrase), asked witnesses whether large loads such as data centers have shown willingness to pay for upgrades, and highlighted her FAIR Act and High-Capacity Grid Act.",
             "date": "2026-04-29",
             "source": "https://fedorchak.house.gov/media/press-releases/fedorchak-presses-fair-cost-allocation-highlights-grid-solutions-energy"},
        ],
        "as_of": "2026-11-21",
    },
    ("AK", "AL", "Nick Begich III"): {
        "lean": "mixed",
        "summary": "Introduced the DATA Act of 2026 to let energy-intensive users, which he says include data centers, run on self-contained 'grid of one' power so ratepayers do not subsidize new load, and argued in an op-ed that Alaska should use its energy advantage to attract AI investment and not 'regulate too early.'",
        "items": [
            {
             "what": "Introduced the DATA Act of 2026 with Reps. Crenshaw and Owens; the release says it lets manufacturers and other energy-intensive industries run fully isolated off-grid power so 'innovation can scale without forcing households to subsidize massive new energy demands.'",
             "date": "2026-04-21",
             "source": "https://begich.house.gov/media/press-releases/congressman-begich-leads-legislation-lower-energy-costs-introduces-house"},
            {
             "what": "Op-ed: said Alaska's natural gas, renewables and stranded energy assets are an advantage for AI data centers; said the DATA Act protects ratepayers from subsidizing new loads; wrote 'We can hesitate, regulate too early and risk becoming an observer... or we can engage thoughtfully, strategically and on our own terms.'",
             "date": "2026-04-23",
             "source": "https://www.adn.com/opinions/2026/04/23/opinion-how-alaska-can-use-our-energy-advantage-to-capitalize-on-the-ai-gold-rush/"},
        ],
        "as_of": "2026-11-21",
    },
    # --- batch 9 (2026-09-12): VT, WY, HI, WV ---
    ("WY", "AL", "Chuck Gray"): {
        "lean": "guardrails",
        "summary": "At an Aug. 5, 2026 forum said he opposes AI data centers; Cowboy State Daily reports he alone among the candidates has indicated a desire to ban them federally. The same article notes he voted in 2021 to keep Wyoming's data-center tax exemption and that his office approved the registration of a data-center-linked business.",
        "items": [
            {
             "what": "At a Sheridan forum said: 'I'm the only candidate on stage that has been talking about these data AI data centers and expressed my opposition to these AI data centers.' Reporter: only Gray has indicated a desire to ban them at the federal level.",
             "date": "2026-08-05",
             "source": "https://cowboystatedaily.com/2026/08/05/u-s-house-forum-gray-hammers-data-centers-clashes-with-host/"},
            {
             "what": "Same article: Rasner said Gray voted in 2021 for data-center tax breaks; the article confirms Gray voted to keep the tax exemption, and that his signature is on the business registration approval for Terra Crypto, tied by a 2024 order to MineOne, which Gray denied wrongdoing over.",
             "date": "2026-08-05",
             "source": "https://cowboystatedaily.com/2026/08/05/u-s-house-forum-gray-hammers-data-centers-clashes-with-host/"},
        ],
        "as_of": "2026-11-21",
    },
    ("WV", "2", "Ace Parsi"): {
        "lean": "guardrails",
        "summary": "At a 'Candidates Against Transmission Lines' news conference he said people feel unheard on data centers and transmission lines and that the architects of the state's data-center build-out have withheld information. The article does not record a specific policy position from him.",
        "items": [
            {
             "what": "Said at a virtual 'Candidates Against Transmission Lines' news conference: 'People don't feel like they're listened to or represented, because if nobody wants these, how did this go through such an overwhelming majority in the House and Senate.' Said the architects behind the data-center build-out have been withholding information. (HB 2014 repeal was called for by another candidate, Vince George.)",
             "date": "2026-08-05",
             "source": "https://www.timeswv.com/news/local_news/data-centers-and-power-lines-might-be-defining-issue-this-election-season-for-ncwv-voters/article_e07b109f-bda6-4bd5-bcfb-4dd7ece657e4.html"},
        ],
        "as_of": "2026-11-21",
    },
}


def _key(r):
    return (r["abbrev"], r["district"])


ROLL_CALLS_FILE = ROOT / "data" / "house_roll_calls.json"


def _roll_calls():
    try:
        return json.loads(ROLL_CALLS_FILE.read_text(encoding="utf-8"))["votes"]
    except FileNotFoundError:
        return []


def records():
    """AI_RECORDS plus recorded roll-call votes from data/house_roll_calls.json.

    AI_RECORDS stays the hand-researched table (the scanners and link checker
    read it, so a member on the record only for a roll call is still flagged
    as needing research). A roll-call item is appended to an existing record
    without touching its lean; a member with no other record gets lean
    'consensus' when the vote was near-unanimous, so a 417-3 vote is visible
    on every record but never scores anyone by itself.
    """
    out = {k: {**v, "items": list(v.get("items", []))}
           for k, v in AI_RECORDS.items()}
    by_name = {(k[0], k[1], rc.norm(k[2])): k for k in out}
    for vote in _roll_calls():
        item = {"what": vote["what_yea"], "date": vote["date"],
                "source": vote["source"]}
        for st, dist, name in vote["yea"]:
            k = by_name.get((st, dist, rc.norm(name)))
            if k:
                rec = out[k]
                # Hand records sometimes already cite the passage (Evans,
                # Castor); don't list the same vote twice.
                if not any(it.get("date") == vote["date"]
                           and vote["bill"] in it.get("what", "")
                           for it in rec["items"]):
                    rec["items"].append(item)
            else:
                out[(st, dist, name)] = {
                    "lean": "consensus" if vote.get("consensus") else "guardrails",
                    "summary": (f"On the record only for voting yes on "
                                f"{vote['bill']}, the {vote['title']} "
                                f"({vote['result']}). No other data-center "
                                f"record located yet."),
                    "items": [item], "as_of": vote["as_of"]}
                by_name[(st, dist, rc.norm(name))] = (st, dist, name)
    return out


def races(state=None):
    """Every 2026 House race with records and unverified mentions attached."""
    rows = HOUSE_RACES_2026
    if state:
        rows = [r for r in rows if r["abbrev"] == state or r["state"] == state]
    return rc.attach_records(rows, records(), _key)


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
    return rc.validate(races(), records(), _key)
