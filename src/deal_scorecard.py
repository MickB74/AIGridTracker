"""
Deal Scorecard — grades announced data-center deals A–F on community terms.

Scoring model (v0): six categories, weighted, each scored 0–4.
  1. Direct community revenue  (25%)
  2. Tax terms                 (20%)
  3. Water                     (15%)
  4. Grid & rates              (15%)
  5. Transparency              (15%)
  6. Local benefit             (10%)

Raw score = sum(score_i * weight_i) / 4, scaled to 0–100.
A = 90–100, B = 80–89, C = 70–79, D = 60–69, F = below 60.

Deals with insufficient public information for a category get a "?" and
are scored conservatively (0) with a note — the gap itself is the story.
"""

import pandas as pd


def _grade(total: int | float) -> str:
    if total >= 90:
        return "A"
    if total >= 80:
        return "B"
    if total >= 70:
        return "C"
    if total >= 60:
        return "D"
    return "F"


def compute_score(revenue, tax, water, grid, transparency, local_benefit):
    raw = (revenue * 25 + tax * 20 + water * 15
           + grid * 15 + transparency * 15 + local_benefit * 10)
    return round(raw / 4)


# Each deal: company, location, state, size, announced, investment,
# status (proposed/approved/operating/rejected), scores (0–4 per category,
# None = insufficient info), notes per category, one-line verdict, sources.
# Scores of None are treated as 0 for grading with a gap flag.

DEALS = [
    # ── Deals with enough detail to score ─────────────────────────────────

    {
        "company": "CoreWeave", "location": "Lancaster", "state": "PA",
        "size_mw": 300, "announced": "Jul 2025", "investment": "$6B",
        "status": "approved",
        "scores": {
            "revenue": 3, "tax": 2, "water": 4, "grid": 3,
            "transparency": 4, "local_benefit": 2,
        },
        "notes": {
            "revenue": "$20M community contributions via signed CBA",
            "tax": "Tax credits under NJ-style program; not a blanket abatement",
            "water": "Hard cap: 20,000 gal/day municipal water per campus",
            "grid": "100% clean-energy requirement with tiered penalties up to $10M/building",
            "transparency": "Binding CBA, full public-records transparency, penalties for missed targets",
            "local_benefit": "Construction jobs; permanent job count not disclosed",
        },
        "verdict": "The gold standard so far — binding CBA with hard water caps, energy penalties, and public transparency.",
        "sources": ["https://lancasteronline.com/news/local/heres-what-a-data-center-community-benefits-agreement-could-include-for-lancaster-city/article_02064716-82f8-4dc8-9b98-907c29027c49.html"],
    },
    {
        "company": "Vantage", "location": "Groton", "state": "CT",
        "size_mw": None, "announced": "2025", "investment": None,
        "status": "approved",
        "scores": {
            "revenue": 3, "tax": 2, "water": 2, "grid": 2,
            "transparency": 3, "local_benefit": 3,
        },
        "notes": {
            "revenue": "$2.5M community recreation center funded by developer",
            "tax": "Standard industrial zone taxation after moratorium",
            "water": "Mandatory stormwater management; no hard potable cap disclosed",
            "grid": "No ratepayer-cost details public",
            "transparency": "Permanent zoning amendments with 45 dBA noise limits — enforceable",
            "local_benefit": "Recreation center is tangible community asset",
        },
        "verdict": "Moratorium leverage produced real, enforceable zoning controls and a funded community facility.",
        "sources": ["moratorium_outcomes:Groton"],
    },
    {
        "company": "Google", "location": "The Dalles", "state": "OR",
        "size_mw": None, "announced": "2021–22", "investment": None,
        "status": "operating",
        "scores": {
            "revenue": 1, "tax": 1, "water": 3, "grid": 2,
            "transparency": 3, "local_benefit": 2,
        },
        "notes": {
            "revenue": "No annual community payment; infrastructure investment instead",
            "tax": "Enterprise-zone benefits; terms not fully public",
            "water": "$29M wastewater treatment upgrade funded; city capped DC water at 25% of municipal supply",
            "grid": "Infrastructure funded but no explicit ratepayer-protection clause",
            "transparency": "Won only after newspaper's public-records lawsuit forced disclosure",
            "local_benefit": "Wastewater upgrade benefits whole city; jobs modest",
        },
        "verdict": "Community pressure and a records lawsuit forced real water protections — but it took years and litigation.",
        "sources": ["company_concessions:Google:The Dalles"],
    },
    {
        "company": "OpenAI / Oracle / SoftBank", "location": "Abilene", "state": "TX",
        "size_mw": 1000, "announced": "2025", "investment": "$3.5B (site)",
        "status": "approved",
        "scores": {
            "revenue": 1, "tax": 0, "water": None, "grid": 1,
            "transparency": 2, "local_benefit": 2,
        },
        "notes": {
            "revenue": "No disclosed community fund or annual payment",
            "tax": "85% property tax abatement for 20 years — near-total exemption",
            "water": "Not publicly disclosed; arid region, significant concern",
            "grid": "357 permanent jobs required contractually; grid cost allocation unknown",
            "transparency": "Terms public via city filings; no CBA; Save Abilene opposition group active",
            "local_benefit": "357 permanent jobs + ~6,000 construction; no community assets",
        },
        "verdict": "Massive 85% tax abatement for 20 years with no CBA — the kind of deal the scorecard exists to flag.",
        "sources": [
            "https://finance.yahoo.com/news/stargate-first-data-center-size-202854022.html",
            "https://www.lonestarleft.com/p/abilene-is-paying-the-price-for-texas",
        ],
    },
    {
        "company": "Amazon (AWS)", "location": "New Albany", "state": "OH",
        "size_mw": None, "announced": "2023 (active through 2026)", "investment": "$3.5B",
        "status": "approved",
        "scores": {
            "revenue": 1, "tax": 0, "water": None, "grid": None,
            "transparency": 1, "local_benefit": 0,
        },
        "notes": {
            "revenue": "Minimum PILOT of $352,750/yr — negligible vs. $3.5B investment",
            "tax": "30-year abatement: 100% for first 15 years, 75% for next 15",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Terms public via council vote, but no CBA or clawbacks",
            "local_benefit": "Only ~105 full-time jobs (21/building) — frequently cited as low-yield",
        },
        "verdict": "30-year tax exemption, 105 jobs, and a PILOT that rounds to zero — the poster child for a bad deal.",
        "sources": ["https://www.nbc4i.com/news/local-news/new-albany/new-albany-city-council-approves-30-year-tax-break-for-amazon-data-centers/"],
    },
    {
        "company": "Amazon (AWS)", "location": "Mississippi (statewide)", "state": "MS",
        "size_mw": None, "announced": "2025", "investment": "$10B+",
        "status": "approved",
        "scores": {
            "revenue": None, "tax": 0, "water": None, "grid": None,
            "transparency": 1, "local_benefit": 1,
        },
        "notes": {
            "revenue": "No community fund disclosed",
            "tax": "10-year 100% corporate income tax exemption; sales/use tax incentives; 30-year rolling exemption if $500M+/yr invested",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "AWS identity not disclosed initially; DCD confirmed",
            "local_benefit": "50 additional jobs/year required for rolling exemption — low bar for $10B",
        },
        "verdict": "Decade of zero corporate tax plus a rolling 30-year extension — enormous concessions with minimal public benefit.",
        "sources": ["https://www.datacenterdynamics.com/en/news/aws-confirmed-as-company-behind-10bn-mississippi-data-center-development/"],
    },
    {
        "company": "Amazon (AWS)", "location": "Northern Indiana", "state": "IN",
        "size_mw": 2400, "announced": "2024–25", "investment": "$11–15B",
        "status": "approved",
        "scores": {
            "revenue": None, "tax": 0, "water": None, "grid": None,
            "transparency": 2, "local_benefit": 2,
        },
        "notes": {
            "revenue": "No community fund disclosed",
            "tax": "50-year sales-tax exemption for DC equipment; $18.3M headcount credits; $55M Hoosier Business Investment credits; $20M redevelopment credits",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Terms public via state IEDC; no CBA",
            "local_benefit": "1,000–1,100 jobs committed; $5M training grants",
        },
        "verdict": "Half-century sales-tax exemption headline is staggering; job count is real but comes with $93M+ in state credits.",
        "sources": ["https://events.in.gov/event/gov-holcomb-announces-amazon-web-services-plans-to-invest-11b-to-create-a-new-data-center-campus-in-northern-indiana"],
    },
    {
        "company": "Google", "location": "Franklin Furnace, Scioto County", "state": "OH",
        "size_mw": None, "announced": "Jan 2026", "investment": None,
        "status": "approved",
        "scores": {
            "revenue": 1, "tax": 1, "water": None, "grid": None,
            "transparency": 2, "local_benefit": 1,
        },
        "notes": {
            "revenue": "PILOT of $500K/yr plus per-sq-ft compensation",
            "tax": "25% property tax abatement for 15 years (pays 75%)",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Approved at public meeting; terms in filings",
            "local_benefit": "Job numbers not disclosed",
        },
        "verdict": "Better than many — pays 75% of taxes with a modest PILOT — but water, grid, and job terms are unknown.",
        "sources": ["https://www.wsaz.com/2026/01/22/googles-request-tax-abatement-proposed-data-center-approved/"],
    },
    {
        "company": "Google", "location": "Cedar Rapids", "state": "IA",
        "size_mw": None, "announced": "2025–26", "investment": "$576M",
        "status": "approved",
        "scores": {
            "revenue": None, "tax": 0, "water": None, "grid": None,
            "transparency": 1, "local_benefit": 1,
        },
        "notes": {
            "revenue": "No community fund disclosed",
            "tax": "$56M in tax abatements over 20 years — nearly 10% of project value",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Approved by Iowa Economic Development Authority; no CBA",
            "local_benefit": "Job numbers not disclosed",
        },
        "verdict": "$56M in tax breaks for a $576M project with no disclosed community benefits — the ratio tells the story.",
        "sources": ["https://www.aol.com/google-gets-tax-break-cedar-205429107.html"],
    },
    {
        "company": "Meta", "location": "Richland Parish", "state": "LA",
        "size_mw": 5000, "announced": "2025–26 (expanded Jul 2026)", "investment": "$50B+",
        "status": "approved",
        "scores": {
            "revenue": None, "tax": 0, "water": None, "grid": None,
            "transparency": 1, "local_benefit": 1,
        },
        "notes": {
            "revenue": "No community fund disclosed publicly",
            "tax": "LA High Impact Jobs Tax Credit + Data Center Sales Tax Exemption; blanket state programs",
            "water": "Not disclosed; Louisiana has abundant water but no DC-specific terms found",
            "grid": "5 GW demand would dominate regional grid; no ratepayer protection disclosed",
            "transparency": "Scale expanded from 2 GW to 5 GW without visible public process",
            "local_benefit": "'Several hundred jobs' — minimal for $50B+ investment",
        },
        "verdict": "The largest data center campus in the world, with terms dictated by state-level tax programs and minimal local negotiation.",
        "sources": [
            "https://news.constructconnect.com/meta-expands-louisiana-data-center-to-5gw-lifts-richland-parish-investment-above-50-billion",
            "https://www.nola.com/news/data-center-meta-amazon-louisiana-tax-break/article_6ccd632e-f470-425a-ad8b-0fba3916bd4d.html",
        ],
    },
    {
        "company": "xAI", "location": "Memphis", "state": "TN",
        "size_mw": 2000, "announced": "2025–26", "investment": "$20B",
        "status": "approved",
        "scores": {
            "revenue": None, "tax": None, "water": None, "grid": 0,
            "transparency": 0, "local_benefit": 1,
        },
        "notes": {
            "revenue": "No community fund disclosed",
            "tax": "No public abatement terms found — significant gap",
            "water": "Not disclosed; community groups raised environmental concerns",
            "grid": "Gas turbines on-site raised air quality concerns; no ratepayer protection",
            "transparency": "No CBA; permits filed without visible community engagement process",
            "local_benefit": "Jobs not quantified publicly",
        },
        "verdict": "A $20B campus approved with near-zero public disclosure of community terms — the opacity is the finding.",
        "sources": ["https://www.teslarati.com/elon-musk-xai-659m-building-expansion-memphis-supercomputer-site/"],
    },
    {
        "company": "xAI", "location": "Southaven, DeSoto County", "state": "MS",
        "size_mw": 2000, "announced": "Jan 2026", "investment": "$20B",
        "status": "approved",
        "scores": {
            "revenue": None, "tax": 0, "water": None, "grid": None,
            "transparency": 1, "local_benefit": 1,
        },
        "notes": {
            "revenue": "No community fund disclosed",
            "tax": "State sales/use/corporate-income/franchise tax exemption + city/county fee-in-lieu",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Terms disclosed via state announcement; no CBA",
            "local_benefit": "~100 direct jobs for a $20B investment",
        },
        "verdict": "Largest private investment in Mississippi history — 100 jobs, full tax exemption, no CBA.",
        "sources": ["https://www.areadevelopment.com/newsItems/1-14-2026/xai-southaven-mississippi.shtml"],
    },
    {
        "company": "Microsoft", "location": "Racine County (Foxconn site)", "state": "WI",
        "size_mw": None, "announced": "2025–26", "investment": "$13B+",
        "status": "approved",
        "scores": {
            "revenue": None, "tax": None, "water": None, "grid": None,
            "transparency": 2, "local_benefit": 2,
        },
        "notes": {
            "revenue": "Not disclosed",
            "tax": "Not itemized publicly; Foxconn precedent looms",
            "water": "Microsoft has committed to zero-water cooling designs for new builds",
            "grid": "Not disclosed",
            "transparency": "Plan Commission 5–2 vote and Village Board approval; public process",
            "local_benefit": "Repurposes largely vacant Foxconn site; job numbers not specified",
        },
        "verdict": "Reuses the Foxconn ghost campus — poetic — but tax terms aren't public, which is a red flag given the site's history.",
        "sources": ["https://www.cnbc.com/2026/01/26/microsoft-wins-approval-for-15-data-centers-at-wisconsin-foxconn-site.html"],
    },
    {
        "company": "Microsoft", "location": "Catawba County", "state": "NC",
        "size_mw": None, "announced": "2025–26", "investment": "$1B+",
        "status": "approved",
        "scores": {
            "revenue": None, "tax": 0, "water": None, "grid": None,
            "transparency": 2, "local_benefit": 1,
        },
        "notes": {
            "revenue": "No community fund disclosed",
            "tax": "50% real-property + 85% personal-property tax value incentive grants, 10-year minimum investment",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Terms public via county filings",
            "local_benefit": "Job numbers not specified",
        },
        "verdict": "Heavy tax incentives (85% personal property) in a state with 14 active moratoriums — the disconnect is telling.",
        "sources": ["https://www.datacenterdynamics.com/en/news/microsoft-to-invest-at-least-1bn-on-four-data-centers-in-catawba-county-nc/"],
    },
    {
        "company": "Microsoft", "location": "Person County", "state": "NC",
        "size_mw": None, "announced": "2025", "investment": None,
        "status": "proposed",
        "scores": {
            "revenue": None, "tax": None, "water": 2, "grid": 1,
            "transparency": 0, "local_benefit": None,
        },
        "notes": {
            "revenue": "Not disclosed",
            "tax": "Hidden behind NDAs with county officials",
            "water": "Pledged water-positive (replenish more than consumed) — needs binding verification",
            "grid": "Pledged not to spike electricity prices — again, binding status unclear",
            "transparency": "NDAs with local officials — The Assembly reported terms 'hidden from Person County'",
            "local_benefit": "Not disclosed",
        },
        "verdict": "NDAs between a corporation and elected officials over a public land-use decision — the secrecy is the story.",
        "sources": ["https://www.theassemblync.com/news/business/person-county-microsoft-data-center-nondisclosure-agreements/"],
    },
    {
        "company": "Apple / Google", "location": "Mesa", "state": "AZ",
        "size_mw": None, "announced": "2023 (protections won)", "investment": None,
        "status": "operating",
        "scores": {
            "revenue": 1, "tax": 2, "water": 2, "grid": 2,
            "transparency": 3, "local_benefit": 2,
        },
        "notes": {
            "revenue": "No direct annual payment; infrastructure contributions",
            "tax": "Standard zone taxation under overlay",
            "water": "Water recycling plans required",
            "grid": "No explicit ratepayer protection but overlay limits scope",
            "transparency": "Data center overlay zone with 55 dBA limits and quarterly community reporting — enforceable",
            "local_benefit": "Existing facilities agreed to voluntary noise retrofits",
        },
        "verdict": "Residents organized mid-construction and won enforceable noise and water rules — proof that leverage doesn't end at approval.",
        "sources": ["moratorium_outcomes:Mesa"],
    },
    {
        "company": "AWS", "location": "Morrow & Umatilla Counties", "state": "OR",
        "size_mw": None, "announced": "2022 (renegotiated)", "investment": None,
        "status": "operating",
        "scores": {
            "revenue": 2, "tax": 2, "water": None, "grid": None,
            "transparency": 2, "local_benefit": 1,
        },
        "notes": {
            "revenue": "Renegotiated enterprise-zone payments upward after community pushback",
            "tax": "Original abatements reduced after renegotiation — proof terms are reopenable",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Renegotiation was public process driven by county commissioners",
            "local_benefit": "Jobs modest; main win was financial terms",
        },
        "verdict": "Proof that a signed tax deal can be reopened when officials organize — the renegotiation itself is the model.",
        "sources": ["company_concessions:Amazon:Oregon"],
    },
    {
        "company": "Compass", "location": "Meridian, Lauderdale County", "state": "MS",
        "size_mw": None, "announced": "Jan 2025", "investment": "$10B",
        "status": "approved",
        "scores": {
            "revenue": None, "tax": None, "water": None, "grid": None,
            "transparency": 1, "local_benefit": 1,
        },
        "notes": {
            "revenue": "Not disclosed",
            "tax": "Not disclosed; MS state-level exemptions likely apply",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Announced via Governor's office, not local process",
            "local_benefit": "8 data centers over 8 years; job numbers not specified",
        },
        "verdict": "A $10B campus announced by the governor with almost no public detail on community terms.",
        "sources": ["https://governorreeves.ms.gov/compass-datacenters-project-generates-10-billion-investment-in-lauderdale-county/"],
    },
    {
        "company": "Compass / QTS", "location": "Prince William County", "state": "VA",
        "size_mw": None, "announced": "2023 (litigation 2025)", "investment": None,
        "status": "approved",
        "scores": {
            "revenue": 1, "tax": 1, "water": None, "grid": None,
            "transparency": 2, "local_benefit": 1,
        },
        "notes": {
            "revenue": "Proffers (buffers, transmission, community funds) offered to keep projects moving",
            "tax": "70+ existing DC facilities pay hundreds of millions — precedent for declining abatements",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "HOA lawsuit overturned rezoning (Aug 2025); court stayed ruling (Oct 2025) — messy public process",
            "local_benefit": "Years of unchecked growth triggered voter revolt; 8–15% property value decline near campuses",
        },
        "verdict": "The cautionary tale — decades of DC growth without protections led to property value drops and a political revolt.",
        "sources": [
            "moratorium_outcomes:Prince William County",
            "https://patch.com/virginia/manassas/digital-gateway-rezoning-overturned-judge-prince-william-county",
        ],
    },
    {
        "company": "QTS", "location": "Van Wert", "state": "OH",
        "size_mw": None, "announced": "May 2026", "investment": "$10B",
        "status": "approved",
        "scores": {
            "revenue": None, "tax": None, "water": None, "grid": None,
            "transparency": 1, "local_benefit": 2,
        },
        "notes": {
            "revenue": "Not disclosed",
            "tax": "Not disclosed; Ohio paused new DC tax exemptions",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Announced via press; limited detail",
            "local_benefit": "1,500 construction + ~200 permanent QTS jobs",
        },
        "verdict": "$10B investment with 200 permanent jobs and no disclosed tax or community terms — big gap.",
        "sources": ["https://www.hometownstations.com/news/van_wert_county/van-wert-announces-10-billion-qts-data-center-campus-investment/article_18b9e9fc-010b-4353-95c0-4ed96293c1ed.html"],
    },
    {
        "company": "QTS", "location": "DeForest/Vienna, Dane County", "state": "WI",
        "size_mw": None, "announced": "2025–26", "investment": "$12B",
        "status": "rejected",
        "scores": {
            "revenue": 3, "tax": None, "water": None, "grid": None,
            "transparency": 2, "local_benefit": 2,
        },
        "notes": {
            "revenue": "$50M community fund offered by QTS",
            "tax": "Not reached — project rejected",
            "water": "Not reached",
            "grid": "Not reached",
            "transparency": "Public village board process; determined 'not feasible'",
            "local_benefit": "Would have had jobs; rejected on feasibility grounds",
        },
        "verdict": "Even a $50M community fund wasn't enough — the village said no. Proof that communities can reject even rich offers.",
        "sources": ["https://www.wpr.org/news/developer-qts-data-centers-looks-build-data-campus-dane-county-vienna"],
    },
    {
        "company": "Stratos AI", "location": "Box Elder County, Hansel Valley", "state": "UT",
        "size_mw": 9000, "announced": "2026", "investment": None,
        "status": "approved",
        "scores": {
            "revenue": None, "tax": None, "water": None, "grid": None,
            "transparency": 0, "local_benefit": None,
        },
        "notes": {
            "revenue": "Not disclosed",
            "tax": "Not disclosed",
            "water": "Not disclosed; Utah is arid — 9 GW would be enormous water demand",
            "grid": "9 GW = more power than entire state of Utah currently uses",
            "transparency": "County commission approved with significant community controversy but minimal public terms",
            "local_benefit": "Not disclosed",
        },
        "verdict": "Approved a campus that would consume more power than the entire state — with no disclosed terms whatsoever.",
        "sources": [
            "https://www.ksl.com/article/51355852/worlds-largest-data-center-campus-could-be-coming-to-central-utah",
            "https://www.techradar.com/pro/utah-just-approved-a-data-center-twice-the-size-of-manhattan-that-will-consume-more-electricity-than-the-entire-state",
        ],
    },
    {
        "company": "CyrusOne", "location": "Whitney, Bosque County", "state": "TX",
        "size_mw": 400, "announced": "Dec 2025", "investment": "$375–500M+",
        "status": "proposed",
        "scores": {
            "revenue": None, "tax": None, "water": None, "grid": 1,
            "transparency": 1, "local_benefit": None,
        },
        "notes": {
            "revenue": "Not disclosed",
            "tax": "Not disclosed",
            "water": "Not disclosed",
            "grid": "Adjacent to power plant (Thad Hill Energy Center); behind-the-meter",
            "transparency": "Local opposition reported ('tiny Whitney braces'); limited public engagement",
            "local_benefit": "Not disclosed",
        },
        "verdict": "400 MW dropped on a tiny town with almost no public information about terms — the imbalance is stark.",
        "sources": ["https://hoodline.com/2025/12/tiny-whitney-braces-as-cyrusone-drops-400-megawatt-data-center-bombshell/"],
    },
    {
        "company": "Compass", "location": "Hoffman Estates (former Sears HQ)", "state": "IL",
        "size_mw": None, "announced": "2025–26", "investment": "$10B",
        "status": "approved",
        "scores": {
            "revenue": None, "tax": None, "water": None, "grid": None,
            "transparency": 1, "local_benefit": 2,
        },
        "notes": {
            "revenue": "Not disclosed",
            "tax": "Not disclosed",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Construction milestone reported; limited public terms",
            "local_benefit": "~1,000 construction jobs; repurposes Sears HQ site",
        },
        "verdict": "Repurposing a dead corporate campus is a land-use win, but $10B with no disclosed community terms is a gap.",
        "sources": ["https://www.chicagoconstructionnews.com/compass-datacenters-marks-milestone-with-building-1-topping-off-at-hoffman-estates-campus/"],
    },
    {
        "company": "STACK", "location": "Berry Hill Megasite, Pittsylvania County", "state": "VA",
        "size_mw": None, "announced": "2025–26", "investment": "$100B",
        "status": "proposed",
        "scores": {
            "revenue": None, "tax": None, "water": None, "grid": None,
            "transparency": 1, "local_benefit": 2,
        },
        "notes": {
            "revenue": "Not disclosed",
            "tax": "Not disclosed",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Moving forward per June 2026 statement; 3,528-acre megasite",
            "local_benefit": "~2,500 jobs projected",
        },
        "verdict": "Potentially the single largest data center investment ever — $100B — with zero disclosed community terms.",
        "sources": [
            "https://cardinalnews.org/2026/06/30/stack-infrastructure-says-its-moving-forward-with-ai-data-center-in-pittsylvania/",
            "https://virginiabusiness.com/stack-100b-berry-hill-data-center-project/",
        ],
    },
    {
        "company": "Crusoe / Lancium", "location": "Childress", "state": "TX",
        "size_mw": 1000, "announced": "Jul 2026", "investment": None,
        "status": "approved",
        "scores": {
            "revenue": None, "tax": None, "water": 3, "grid": 3,
            "transparency": 2, "local_benefit": 2,
        },
        "notes": {
            "revenue": "Not disclosed",
            "tax": "Not disclosed",
            "water": "Closed-loop cooling — no potable water draw",
            "grid": "Behind-the-meter solar + storage; doesn't draw from public grid",
            "transparency": "Technical details public; financial community terms not disclosed",
            "local_benefit": "100+ permanent jobs",
        },
        "verdict": "The technical design is exemplary (closed-loop, solar-powered) — but no disclosed community financial terms.",
        "sources": ["https://www.crusoe.ai/resources/newsroom/crusoe-and-lancium-announce-1-0-gigawatt-ai-data-center-campus-in-childress-texas"],
    },
    {
        "company": "CoreWeave", "location": "Kenilworth", "state": "NJ",
        "size_mw": 250, "announced": "Sep 2025", "investment": "$1.8B",
        "status": "approved",
        "scores": {
            "revenue": None, "tax": 1, "water": None, "grid": None,
            "transparency": 2, "local_benefit": 2,
        },
        "notes": {
            "revenue": "Not disclosed",
            "tax": "First project under NJ EDA's new data center tax-credit program — structured, not a blank check",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Program-based incentive with state oversight",
            "local_benefit": "Construction jobs; operational target early 2027",
        },
        "verdict": "State-program-based incentive is better than ad hoc abatements, but community terms remain thin.",
        "sources": ["https://re-nj.com/coreweave-begins-1-8-billion-data-center-project-in-kenilworth-landing-first-award-under-new-eda-tax-credit-program/"],
    },
    {
        "company": "Applied Digital", "location": "Harwood", "state": "ND",
        "size_mw": 280, "announced": "2025", "investment": "$3B",
        "status": "approved",
        "scores": {
            "revenue": None, "tax": None, "water": None, "grid": None,
            "transparency": 1, "local_benefit": 1,
        },
        "notes": {
            "revenue": "Not disclosed",
            "tax": "Not disclosed",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "IR press releases; no community process detail",
            "local_benefit": "Jobs not quantified",
        },
        "verdict": "$3B AI campus in rural North Dakota with no disclosed community terms.",
        "sources": ["https://ir.applieddigital.com/news-events/press-releases/detail/132/applied-digital-announces-5-billion-ai-factory-lease-with"],
    },
    {
        "company": "Vantage", "location": "Storey County", "state": "NV",
        "size_mw": 224, "announced": "2025", "investment": "$3B",
        "status": "approved",
        "scores": {
            "revenue": None, "tax": None, "water": None, "grid": None,
            "transparency": 1, "local_benefit": 1,
        },
        "notes": {
            "revenue": "Not disclosed",
            "tax": "Not disclosed; NV has favorable DC tax climate",
            "water": "Not disclosed; near Reno — water-stressed region",
            "grid": "Not disclosed",
            "transparency": "Press release only",
            "local_benefit": "Jobs not quantified",
        },
        "verdict": "$3B in a water-stressed region with no disclosed community protections.",
        "sources": ["https://vantage-dc.com/news/vantage-data-centers-invests-3-billion-to-deliver-ai-campus-in-growing-nevada-market/"],
    },
    {
        "company": "Data center (unnamed)", "location": "East Side / Warren Township, Indianapolis", "state": "IN",
        "size_mw": None, "announced": "Jul 2026", "investment": None,
        "status": "approved",
        "scores": {
            "revenue": None, "tax": None, "water": None, "grid": None,
            "transparency": 1, "local_benefit": 0,
        },
        "notes": {
            "revenue": "Not disclosed",
            "tax": "Not disclosed",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Approved 6–1 despite 83% survey opposition",
            "local_benefit": "Community overwhelmingly opposed; protests at City-County Building",
        },
        "verdict": "Approved over 83% community opposition — the democratic deficit is the score.",
        "sources": ["https://www.wfyi.org/wfyi-news/2026-07-15/east-side-data-center-wins-approval-despite-community-opposition"],
    },
    {
        "company": "Data center (unnamed)", "location": "West Louisville", "state": "KY",
        "size_mw": 400, "announced": "Mar 2026", "investment": None,
        "status": "approved",
        "scores": {
            "revenue": None, "tax": None, "water": None, "grid": None,
            "transparency": 1, "local_benefit": 0,
        },
        "notes": {
            "revenue": "Not disclosed",
            "tax": "Not disclosed",
            "water": "Not disclosed; residents cited water concerns",
            "grid": "Not disclosed; residents cited electricity drain concerns",
            "transparency": "20+ residents spoke in opposition; approved regardless",
            "local_benefit": "Residents cited pollution concerns; no community benefits disclosed",
        },
        "verdict": "400 MW approved over resident opposition with no disclosed terms — a blank check.",
        "sources": ["https://www.lpm.org/news/2026-03-05/west-louisville-data-center-approved-despite-opposition"],
    },
    {
        "company": "Data center (unnamed)", "location": "Imperial County", "state": "CA",
        "size_mw": None, "announced": "Apr 2026", "investment": None,
        "status": "approved",
        "scores": {
            "revenue": None, "tax": None, "water": None, "grid": None,
            "transparency": 1, "local_benefit": None,
        },
        "notes": {
            "revenue": "Not disclosed",
            "tax": "Not disclosed",
            "water": "Not disclosed; rural county, arid region",
            "grid": "Not disclosed",
            "transparency": "County reconsidering approval as of June 2026",
            "local_benefit": "Not disclosed",
        },
        "verdict": "Approved and then the county started reconsidering — a sign the original process was rushed.",
        "sources": ["https://calmatters.org/environment/2026/06/imperial-county-data-center/"],
    },
    {
        "company": "DAMAC / undisclosed", "location": "Edgerton, Johnson County", "state": "KS",
        "size_mw": None, "announced": "2026", "investment": None,
        "status": "proposed",
        "scores": {
            "revenue": None, "tax": None, "water": None, "grid": None,
            "transparency": 1, "local_benefit": None,
        },
        "notes": {
            "revenue": "Not disclosed",
            "tax": "Not disclosed",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Residents launched petition for moratorium; a separate 300-acre Gardner project withdrawn after 100+ residents opposed",
            "local_benefit": "Not disclosed",
        },
        "verdict": "Community organized before the deal was done — petition-driven moratorium effort is a model for early action.",
        "sources": [
            "https://www.nakedcapitalism.com/2026/07/the-kansas-community-fighting-data-centers-before-they-arrive.html",
            "https://www.kshb.com/news/local-news/kansas/johnson-county/edgerton-neighbors-launch-petition-to-have-more-say-in-data-center-development-decisions",
        ],
    },
    {
        "company": "Amazon (AWS)", "location": "Montgomery County", "state": "MO",
        "size_mw": None, "announced": "Dec 2025", "investment": "$8.5B",
        "status": "approved",
        "scores": {
            "revenue": None, "tax": 1, "water": None, "grid": None,
            "transparency": 2, "local_benefit": 2,
        },
        "notes": {
            "revenue": "Emergency services funding committed",
            "tax": "Tax incentive framework approved by county commission",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "County commission vote Dec 19, 2025; public process",
            "local_benefit": "400+ jobs committed",
        },
        "verdict": "Emergency services funding is a start, but $8.5B with an unspecified 'tax incentive framework' needs details.",
        "sources": ["https://www.stlpr.org/economy-business/2025-12-19/montgomery-county-commission-approves-amazon-data-center-tax-incentive-framework"],
    },
    {
        "company": "Google", "location": "Lenoir", "state": "NC",
        "size_mw": None, "announced": "2025–26", "investment": "$1B",
        "status": "approved",
        "scores": {
            "revenue": 1, "tax": None, "water": None, "grid": None,
            "transparency": 2, "local_benefit": 1,
        },
        "notes": {
            "revenue": "$2M Energy Impact Fund with Blue Ridge Community Action / Blue Ridge Energy / Advanced Energy",
            "tax": "Not disclosed",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Community fund is public and named; no binding CBA",
            "local_benefit": "Fund is genuine but modest relative to $1B investment",
        },
        "verdict": "$2M community fund on a $1B investment — 0.2% — is better than nothing but barely a rounding error.",
        "sources": ["Google blog; DCD coverage"],
    },
    {
        "company": "LiquidCool Solutions", "location": "Loring AFB, Limestone", "state": "ME",
        "size_mw": 2, "announced": "Oct 2025", "investment": None,
        "status": "approved",
        "scores": {
            "revenue": None, "tax": None, "water": 3, "grid": 3,
            "transparency": 2, "local_benefit": 2,
        },
        "notes": {
            "revenue": "Not disclosed",
            "tax": "Not disclosed",
            "water": "Liquid immersion cooling — minimal water use",
            "grid": "50 MW hydropower from New Brunswick; doesn't strain local grid",
            "transparency": "Sized to stay under Maine's 20 MW moratorium threshold — transparent about design choice",
            "local_benefit": "Reuses decommissioned military base",
        },
        "verdict": "Small, hydro-powered, immersion-cooled, on a dead military base — technically a model, but sized to dodge regulation.",
        "sources": ["https://www.newscentermaine.com/article/news/local/data-center-planned-loring-air-force-base/97-53a8f077-ef31-4d65-ac58-5acf96194aa1"],
    },
    {
        "company": "Saline Township (Stargate/Oracle)", "location": "Saline Township", "state": "MI",
        "size_mw": None, "announced": "2026", "investment": "$16B",
        "status": "approved",
        "scores": {
            "revenue": None, "tax": 1, "water": None, "grid": None,
            "transparency": 2, "local_benefit": 1,
        },
        "notes": {
            "revenue": "Not disclosed",
            "tax": "12-year, 50% abatement — community pushback reduced the ask by 9x from original request",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Abatement reduced after community pushback — public process worked",
            "local_benefit": "Jobs not quantified",
        },
        "verdict": "Community pushback cut the tax abatement request by 9x — the most dramatic example of negotiation working.",
        "sources": ["https://civicmedia.us/news/2026/07/16/massive-data-center-wins-local-tax-break-but-9-times-smaller-than-requested"],
    },
    {
        "company": "Ohio (statewide — pre-moratorium rush)", "location": "Ohio (statewide)", "state": "OH",
        "size_mw": None, "announced": "2025–26", "investment": None,
        "status": "approved",
        "scores": {
            "revenue": None, "tax": 0, "water": None, "grid": None,
            "transparency": 0, "local_benefit": None,
        },
        "notes": {
            "revenue": "Not disclosed",
            "tax": "$42M in combined tax breaks rushed through before state moratorium on new exemptions",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Approved in rush before moratorium took effect — procedural end-run",
            "local_benefit": "Not disclosed",
        },
        "verdict": "$42M in tax breaks rushed through before a moratorium — the regulatory arbitrage is the grade.",
        "sources": ["https://signalcleveland.org/ohio-approves-last-data-center-exemption-before-moratorium/"],
    },
    {
        "company": "AVAIO Digital", "location": "Brandon", "state": "MS",
        "size_mw": None, "announced": "Aug 2025", "investment": "$6B",
        "status": "approved",
        "scores": {
            "revenue": None, "tax": None, "water": None, "grid": None,
            "transparency": 1, "local_benefit": 1,
        },
        "notes": {
            "revenue": "Not disclosed",
            "tax": "MS state-level exemptions likely",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Press announcement; limited community terms",
            "local_benefit": "Jobs not quantified; sister site in AR ($21B buildout)",
        },
        "verdict": "$6B with no disclosed community terms — another Mississippi deal with the same pattern.",
        "sources": ["https://mississippitoday.org/2026/06/01/mississippi-ddata-center-plans/"],
    },
]


def _score_deal(d: dict) -> dict:
    """Add computed total, grade, and gap_count to a deal dict."""
    s = d["scores"]
    vals = {k: (v if v is not None else 0) for k, v in s.items()}
    total = compute_score(**vals)
    gaps = sum(1 for v in s.values() if v is None)
    return {
        **d,
        "total": total,
        "grade": _grade(total),
        "gap_count": gaps,
    }


SCORED_DEALS = [_score_deal(d) for d in DEALS]

DEALS_DF = pd.DataFrame([
    {
        "company": d["company"],
        "location": d["location"],
        "state": d["state"],
        "size_mw": d.get("size_mw"),
        "investment": d.get("investment"),
        "announced": d["announced"],
        "status": d["status"],
        "grade": d["grade"],
        "total": d["total"],
        "gap_count": d["gap_count"],
        "revenue": d["scores"]["revenue"],
        "tax": d["scores"]["tax"],
        "water": d["scores"]["water"],
        "grid": d["scores"]["grid"],
        "transparency": d["scores"]["transparency"],
        "local_benefit": d["scores"]["local_benefit"],
        "verdict": d["verdict"],
    }
    for d in SCORED_DEALS
])
