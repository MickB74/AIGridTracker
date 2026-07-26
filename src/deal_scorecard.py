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


DEALS = [
    # ── Model deals (C or above) ──────────────────────────────────────────

    {
        "company": "CoreWeave", "location": "Lancaster", "state": "PA",
        "size_mw": 300, "announced": "Jul 2025", "investment": "$6B",
        "status": "approved",
        "scores": {
            "revenue": 4, "tax": 2, "water": 4, "grid": 3,
            "transparency": 3, "local_benefit": 2,
        },
        "notes": {
            "revenue": "$20.25M total ($10M Community Foundation + $10M city Sustainable Development Fund), backed by $20M Letter of Credit",
            "tax": "NJ EDA tax-credit program — structured, not a blanket abatement",
            "water": "Hard cap: 20,000 gal/day per campus",
            "grid": "100% clean-energy requirement with tiered penalties: 80% compliance = $2.5–5M, 60% = $5–10M, below 60% = injunctive relief; backed by separate $10M LOC",
            "transparency": "Binding CBA (32 pp.), successor clause (runs with property), annual City Council report — but report covers only clean energy, not water/hiring; no independent monitoring board; noise checks capped at every 2 years",
            "local_benefit": "~150 jobs/campus expected; process-based Local Hiring Plan, not numeric quotas; 20-year term",
        },
        "verdict": "The gold standard so far — $20M backed by Letters of Credit, hard water cap, clean-energy penalties, binding on successors. Gaps: annual report doesn't cover water/hiring, no independent oversight.",
        "sources": [
            "https://lancasteronline.com/news/local/heres-what-a-data-center-community-benefits-agreement-could-include-for-lancaster-city/article_02064716-82f8-4dc8-9b98-907c29027c49.html",
        ],
    },
    {
        "company": "STACK", "location": "Berry Hill Megasite, Pittsylvania County", "state": "VA",
        "size_mw": 299, "announced": "2025–26", "investment": "$100B",
        "status": "approved",
        "scores": {
            "revenue": 3, "tax": 3, "water": 4, "grid": 2,
            "transparency": 3, "local_benefit": 3,
        },
        "notes": {
            "revenue": "$48.5M/yr minimum guaranteed tax payment at full buildout ($16.25M/yr on first 1,000 acres + $16,250/acre beyond); 50/50 revenue sharing on $737.8M land sale",
            "tax": "Equipment taxed at $1.62/$100; minimum payment floor enforceable regardless of buildout pace; county retains right to raise rate if milestones missed; no discretionary cash incentive — only $1K/job enterprise-zone credit",
            "water": "Dry-cooled — 10,000–20,000 gal/day for entire 2,990-acre campus",
            "grid": "299 MW initial allocation by end of 2028; no explicit ratepayer-protection clause found; contingent on state sales/use tax exemption remaining law",
            "transparency": "Performance agreement approved unanimously May 18, 2026; enforceable milestones; no community-benefit fund or CBA found",
            "local_benefit": "2,500 permanent jobs + 2,000+ construction at ~$80K avg wage",
        },
        "verdict": "A $48.5M/yr tax floor with clawback rights and dry cooling is structurally excellent — the best large-deal framework found. No CBA or community fund is the gap.",
        "sources": [
            "https://cardinalnews.org/2026/06/30/stack-infrastructure-says-its-moving-forward-with-ai-data-center-in-pittsylvania/",
            "https://virginiabusiness.com/stack-100b-berry-hill-data-center-project/",
        ],
    },

    # ── D-tier (some protections) ─────────────────────────────────────────

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
        "company": "Amazon (AWS)", "location": "Montgomery County", "state": "MO",
        "size_mw": None, "announced": "Dec 2025", "investment": "$8.5B",
        "status": "approved",
        "scores": {
            "revenue": 3, "tax": 1, "water": 3, "grid": 3,
            "transparency": 2, "local_benefit": 2,
        },
        "notes": {
            "revenue": "~$7M+ CBA: $3M for 911/dispatch, $1M+ community space, $3M+ education/STEM, $150K community fund, $50K school grants, new rail bridge",
            "tax": "Ch. 100 bonds: $3M/yr flat (2028–32) → 5% of taxes (2033–42) → 25% (2043–52); valued $244M–$982M; Sunshine Law lawsuit alleges $35B true cost",
            "water": "On-site wells + treatment plant, ~50M gal/yr at full buildout, donated to public water district at no cost",
            "grid": "Ameren Missouri: Amazon pays 100% of grid costs, 12-yr minimum contract, collateral = 2 yrs of bills, no ratepayer discount",
            "transparency": "CBA terms public but Sunshine Law lawsuit (Feb 2026) alleges closed-session negotiations and NDAs; hearing Aug 3, 2026",
            "local_benefit": "150 FTE minimum at 150% of county average wage; $7M+ in community infrastructure",
        },
        "verdict": "Unusually strong grid terms (100% developer-funded) and a real CBA, but the Sunshine Law lawsuit clouds the transparency picture.",
        "sources": ["https://www.stlpr.org/economy-business/2025-12-19/montgomery-county-commission-approves-amazon-data-center-tax-incentive-framework"],
    },
    {
        "company": "xAI", "location": "Memphis", "state": "TN",
        "size_mw": 2000, "announced": "2025–26", "investment": "$20B",
        "status": "approved",
        "scores": {
            "revenue": 3, "tax": 3, "water": 1, "grid": 1,
            "transparency": 2, "local_benefit": 2,
        },
        "notes": {
            "revenue": "25% of property tax revenue from xAI sites dedicated to community reinvestment (up to $100M total, capped to 5-mile radius); FY2026 disbursement: $3.26M split across home repair, cleanup, safety, environmental testing, education",
            "tax": "No property tax abatement — pays ~$30M+/yr combined city/county. Council carved out 1% for environmental education",
            "water": "812,502 gal/day from Memphis Sand Aquifer; pledged 'world's largest ceramic membrane greywater facility' but no signed agreement; purchased >25M gal from MLGW in March alone",
            "grid": "TVA→MLGW supplies 300 MW; 35 unpermitted methane gas turbines installed then removed after SELC notice; 15 turbines later permitted 24/7 over 2,000+ opposing comments",
            "transparency": "Community reinvestment fund is public and structured; but unpermitted turbines and air quality fight undermine process trust; NAACP Clean Air Act suit filed April 2026",
            "local_benefit": "Community reinvestment disbursements are real ($3.26M yr 1); no permanent job count disclosed",
        },
        "verdict": "The surprise: xAI actually pays its taxes ($30M+/yr, no abatement) and funds a real community reinvestment program. But 812K gal/day from the aquifer and 35 unpermitted turbines are serious.",
        "sources": ["https://www.teslarati.com/elon-musk-xai-659m-building-expansion-memphis-supercomputer-site/"],
    },

    # ── F-tier with some positives ────────────────────────────────────────

    {
        "company": "Saline Township (Stargate/Oracle)", "location": "Saline Township", "state": "MI",
        "size_mw": 1383, "announced": "2025–26", "investment": "$16–43B",
        "status": "approved",
        "scores": {
            "revenue": 2, "tax": 1, "water": None, "grid": 3,
            "transparency": 1, "local_benefit": 3,
        },
        "notes": {
            "revenue": "$4M farmland preservation trust + $2M community investment fund (from lawsuit settlement)",
            "tax": "50% abatement for 12 years on full $43B valuation; township tried to cap at original $4.8B (saving ~$127M/yr) but forced to reverse 6 days later under consent-judgment legal pressure; clawback for non-completion remains",
            "water": "Pledged water resource protection but no specific cap or permit found",
            "grid": "DTE contract: 80% minimum billing demand (vs. 50–60% standard), 19-year term, 10-year termination penalty; MPSC required DTE to absorb any unrecoverable costs — strong ratepayer protection",
            "transparency": "Township voted 4–1 to deny rezoning; developer sued 2 days later; consent judgment forced project through; 'secretly negotiated'; resident intervention denied by judge",
            "local_benefit": "450+ permanent jobs + 2,500 union construction; $6M total community investment",
        },
        "verdict": "The township said no, got sued, and lost. The DTE grid contract is model-quality but the democratic override is the story.",
        "sources": [
            "https://civicmedia.us/news/2026/07/16/massive-data-center-wins-local-tax-break-but-9-times-smaller-than-requested",
            "https://planetdetroit.org/2026/07/data-center-news-saline-township/",
        ],
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
        "company": "Amazon (AWS)", "location": "Northern Indiana", "state": "IN",
        "size_mw": 2400, "announced": "2024–25", "investment": "$11–15B",
        "status": "approved",
        "scores": {
            "revenue": 2, "tax": 0, "water": 2, "grid": 2,
            "transparency": 2, "local_benefit": 2,
        },
        "notes": {
            "revenue": "$143M Community Enhancement Agreement (St. Joseph County)",
            "tax": "10-yr 50% real property + 85% personal property for 35 years (~$1.9B in savings to Amazon); county Republicans sent letter asking Amazon to renegotiate after Microsoft nearby declined any abatement",
            "water": "$114M in water/sewer infrastructure; 100M+ gal/yr watershed replenishment; 24M gal/day aquifer permit; construction dewatering permit (31M gal/day) tabled after farmer objections",
            "grid": "IN statute: large-load pays ≥80% of infrastructure costs; NIPSCO claims $1B ratepayer savings over 15 years",
            "transparency": "Terms public; county politicians now pushing renegotiation; public friction over dewatering permit",
            "local_benefit": "1,000–1,100 jobs; $5M training grants; $143M community enhancement",
        },
        "verdict": "The $143M community enhancement is real, but 85% personal-property abatement for 35 years (~$1.9B) dwarfs it. County politicians asking for renegotiation is the live story.",
        "sources": ["https://events.in.gov/event/gov-holcomb-announces-amazon-web-services-plans-to-invest-11b-to-create-a-new-data-center-campus-in-northern-indiana"],
    },
    {
        "company": "Applied Digital", "location": "Harwood", "state": "ND",
        "size_mw": 280, "announced": "2025", "investment": "$3B",
        "status": "approved",
        "scores": {
            "revenue": 0, "tax": None, "water": 3, "grid": 4,
            "transparency": 2, "local_benefit": 2,
        },
        "notes": {
            "revenue": "No community fund; only road-upgrade MOA",
            "tax": "No county PILOT found; ND statewide DC sales tax exemption capped at first 4 certified facilities",
            "water": "Closed-loop, trucked-in initial fill, not drawn from Cass Rural Water",
            "grid": "$110M Agassiz transmission line/substation paid 100% by Applied Digital (ND PSC approved ~Apr 2026); zero cost to other ratepayers",
            "transparency": "SEC 8-K disclosures, MOA for road upgrades public",
            "local_benefit": "200–250 FTE; road upgrades at developer cost",
        },
        "verdict": "The grid terms are exemplary — $110M transmission paid 100% by the developer. No community fund or CBA is the gap.",
        "sources": ["https://ir.applieddigital.com/news-events/press-releases/detail/132/applied-digital-announces-5-billion-ai-factory-lease-with"],
    },
    {
        "company": "CyrusOne", "location": "Whitney, Bosque County", "state": "TX",
        "size_mw": 400, "announced": "Dec 2025", "investment": "$375–500M+",
        "status": "proposed",
        "scores": {
            "revenue": 0, "tax": 2, "water": 3, "grid": 1,
            "transparency": 2, "local_benefit": 1,
        },
        "notes": {
            "revenue": "No community fund",
            "tax": "Ch. 312: 10-year, 30% property tax abatement with embedded conditions: road-repair obligation, 'buy local' requirement, implied clawback; ~$70M projected revenue over 30 years; June 2026 deadline to revise terms after pushback",
            "water": "Closed-loop, trucked-in refill every ~15 years; well-permit pending; Brazos River Authority confirms no lake-water agreement",
            "grid": "Calpine 'powered land' deal at Thad Hill (190+210 MW); no pricing disclosed",
            "transparency": "Public process with revision deadline; community pushback led to conditions",
            "local_benefit": "~40 on-site employees; $70M revenue over 30 years",
        },
        "verdict": "A 30% abatement with embedded conditions is moderate by TX standards. Closed-loop cooling is good. 40 jobs for a $500M+ investment is not.",
        "sources": ["https://hoodline.com/2025/12/tiny-whitney-braces-as-cyrusone-drops-400-megawatt-data-center-bombshell/"],
    },
    {
        "company": "Compass", "location": "Hoffman Estates (former Sears HQ)", "state": "IL",
        "size_mw": None, "announced": "2025–26", "investment": "$10B",
        "status": "approved",
        "scores": {
            "revenue": 2, "tax": 1, "water": None, "grid": None,
            "transparency": 2, "local_benefit": 2,
        },
        "notes": {
            "revenue": "$800K/building = $4M total CBA paid at certificate of occupancy; reported to 'run with the land'",
            "tax": "Cook County Class 6B classification (12-yr clock starts at 60% occupancy per building); TIF-district overlap unconfirmed",
            "water": "No permitted gallons-per-day found",
            "grid": "ComEd dedicated substation (200–500 MW capacity cited inconsistently); no ratepayer terms found",
            "transparency": "CBA terms reported but need primary-source confirmation via village ordinance FOIA",
            "local_benefit": "~1,000 construction jobs; repurposes dead Sears HQ; no operational headcount",
        },
        "verdict": "A $4M CBA and the Sears-site reuse are positives; Class 6B tax treatment needs scrutiny.",
        "sources": ["https://www.chicagoconstructionnews.com/compass-datacenters-marks-milestone-with-building-1-topping-off-at-hoffman-estates-campus/"],
    },
    {
        "company": "QTS", "location": "Van Wert", "state": "OH",
        "size_mw": None, "announced": "May 2026", "investment": "$10B",
        "status": "approved",
        "scores": {
            "revenue": None, "tax": 1, "water": 3, "grid": 2,
            "transparency": 2, "local_benefit": 2,
        },
        "notes": {
            "revenue": "Not disclosed; $200M projected tax revenue over 20 years",
            "tax": "$73M Ohio sales-tax exemption — got in before Gov. DeWine's May 27, 2026 pause (actual program cost: $1.57B vs. $136M projection, a >10x miss); HB 975 would end exemption Oct 2026",
            "water": "Closed-loop cooling with no ongoing water consumption once operational",
            "grid": "AEP Ohio tariff (if in territory): 85% minimum capacity payment, 12-yr minimum contract, 3-year exit penalty — strong ratepayer protection",
            "transparency": "Public announcement; need to confirm AEP territory and county commission terms",
            "local_benefit": "200 permanent + 1,500 construction; building-trades partnership",
        },
        "verdict": "$73M exemption from a program that cost 10x its projection — QTS got in just before the door closed. Closed-loop cooling and AEP tariff terms are genuinely good.",
        "sources": ["https://www.hometownstations.com/news/van_wert_county/van-wert-announces-10-billion-qts-data-center-campus-investment/article_18b9e9fc-010b-4353-95c0-4ed96293c1ed.html"],
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
            "tax": "First project under NJ EDA's new data-center tax-credit program — structured, not a blank check",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Program-based incentive with state oversight",
            "local_benefit": "Construction jobs; operational target early 2027",
        },
        "verdict": "State-program-based incentive is better than ad hoc abatements, but community terms remain thin.",
        "sources": ["https://re-nj.com/coreweave-begins-1-8-billion-data-center-project-in-kenilworth-landing-first-award-under-new-eda-tax-credit-program/"],
    },
    {
        "company": "Google", "location": "Lenoir", "state": "NC",
        "size_mw": None, "announced": "Mar 2026", "investment": "$1B",
        "status": "approved",
        "scores": {
            "revenue": 2, "tax": 1, "water": 2, "grid": None,
            "transparency": 2, "local_benefit": 2,
        },
        "notes": {
            "revenue": "$2M Energy Impact Fund (Blue Ridge Community Action / Blue Ridge Energy / Advanced Energy) + $100K historic school renovation + $270K workforce development fund",
            "tax": "20-year term: 50% real property + 85% personal property tax incentive grants; performance-based with NC statutory clawback; $4.8M state JDIG grant",
            "water": "$6.8M voluntary water capacity expansion; no hard cap on consumption",
            "grid": "Alliant Energy/ITC Midwest filed for 300 MW interconnection; no specific renewable PPA confirmed for this site",
            "transparency": "Incentives approved at joint county/city meeting Oct 2024; terms public",
            "local_benefit": "JDIG: ~210 jobs at $26.20–31.44/hr; $270K workforce fund with Caldwell CC&TI",
        },
        "verdict": "$2.4M in community benefits on a $1B investment — 0.24%. The Energy Impact Fund is real but modest; 85% personal-property abatement is heavy.",
        "sources": ["https://www.cityoflenoir.com/CivicAlerts.aspx?AID=498"],
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

    # ── F-tier — bad deals ────────────────────────────────────────────────

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
        "company": "OpenAI / Oracle / SoftBank", "location": "Abilene", "state": "TX",
        "size_mw": 1200, "announced": "2025", "investment": "$3.5B",
        "status": "approved",
        "scores": {
            "revenue": 0, "tax": 0, "water": 3, "grid": 0,
            "transparency": 2, "local_benefit": 2,
        },
        "notes": {
            "revenue": "No community fund, no annual payment, no PILOT beyond abatement",
            "tax": "Ch. 312: 85% city / 80% county for 10+ years; Oracle separately protesting its assessment to go even lower; $2.4B minimum investment commitment",
            "water": "Closed-loop liquid cooling; 1M gal one-time fill per building (8 buildings); <1% of Abilene daily usage per city",
            "grid": "$500M on-site gas plant 0.5–2 mi from residential neighborhoods; 1.6M tons/yr GHG, 14 tons/yr hazardous air pollutants; 1.2 GW ERCOT interconnect; no ratepayer protection",
            "transparency": "Terms public via TX Comptroller Ch. 312 records; no CBA; Save Abilene opposition active",
            "local_benefit": "357 permanent jobs at $57,600/yr minimum; ~1,500 construction; no local-hire requirement found",
        },
        "verdict": "85% tax abatement, a half-billion-dollar gas plant near homes producing 1.6M tons/yr CO2, and Oracle protesting to pay even less. The water design is the one bright spot.",
        "sources": [
            "https://comptroller.texas.gov/economy/development/search-tools/ch312/abatements-details.php?id=000017852",
            "https://www.texasobserver.org/abilene-texas-stargate-natural-gas-plant-harms/",
        ],
    },
    {
        "company": "Amazon (AWS)", "location": "New Albany", "state": "OH",
        "size_mw": None, "announced": "2023 (active through 2026)", "investment": "$3.5B",
        "status": "approved",
        "scores": {
            "revenue": 0, "tax": 0, "water": None, "grid": None,
            "transparency": 1, "local_benefit": 0,
        },
        "notes": {
            "revenue": "PILOT: $352K/yr escalating to $1.1M/yr — negligible vs. $3.5B; no clawback found",
            "tax": "30-year CRA: 100% for first 15 years, 75% for next 15; Ohio law requires school-district compensation agreement for >50%/>10yr but none found publicly",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Terms public via council vote; no CBA, no clawback found; comparable: 19 Columbus-area DC deals = $750M+ foregone tax for 770 jobs (~$974K/job)",
            "local_benefit": "105 full-time jobs (21/building); Meta's nearby New Albany deal: $189.6M foregone for 98 jobs",
        },
        "verdict": "30-year exemption, 105 jobs, and a PILOT that rounds to zero. Part of a $750M+ regional tax giveaway across 19 deals for 770 total jobs.",
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
            "tax": "10-year 100% corporate income tax exemption; sales/use tax incentives; 30-year rolling exemption if $500M+/yr invested + 50 jobs/yr",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "AWS identity not disclosed initially",
            "local_benefit": "50 additional jobs/year required — low bar for $10B",
        },
        "verdict": "Decade of zero corporate tax plus a rolling 30-year extension — enormous concessions with minimal public benefit.",
        "sources": ["https://www.datacenterdynamics.com/en/news/aws-confirmed-as-company-behind-10bn-mississippi-data-center-development/"],
    },
    {
        "company": "Google", "location": "Cedar Rapids", "state": "IA",
        "size_mw": 300, "announced": "2024–26", "investment": "$576M",
        "status": "approved",
        "scores": {
            "revenue": 0, "tax": 0, "water": 0, "grid": 1,
            "transparency": 1, "local_benefit": 0,
        },
        "notes": {
            "revenue": "No community fund or CBA",
            "tax": "20-year, 70% local property-tax exemption ($56M) via IEDA High Quality Jobs program; plus uncapped statewide sales-tax exemption",
            "water": "Up to 12M gal/day from Cedar River (comparable to city's largest existing user); city's water plant is 50 years old, undergoing $348M upgrade; no water-use cap or agreement found",
            "grid": "ITC Midwest filed for 300 MW interconnection; $3M water-main extension partly funded by Alliant Energy; no ratepayer-protection terms found",
            "transparency": "IEDA board approval public; no CBA, no community engagement beyond statutory requirements",
            "local_benefit": "HQJ contract: only 31 FTEs minimum at $26.20–31.44/hr — ratio: ~$18.6M invested per required job",
        },
        "verdict": "$56M in tax breaks, up to 12M gal/day from the river, and 31 required jobs. The jobs-per-dollar ratio ($18.6M/job) is the worst we've found.",
        "sources": [
            "https://www.thegazette.com/business/state-panel-signs-off-on-cedar-rapids-56-million-tax-break-for-google-data-center/",
            "https://www.kcrg.com/2025/04/17/concerns-expressed-over-water-usage-new-cedar-rapids-data-centers-leads-much-larger-questions/",
        ],
    },
    {
        "company": "Meta", "location": "Richland Parish", "state": "LA",
        "size_mw": 5000, "announced": "2025–26 (expanded Jul 2026)", "investment": "$50B+",
        "status": "approved",
        "scores": {
            "revenue": 1, "tax": 0, "water": 1, "grid": 0,
            "transparency": 1, "local_benefit": 1,
        },
        "notes": {
            "revenue": "Meta claims $1B+ in road/water/wastewater infrastructure; no dedicated community fund",
            "tax": "~$3.3B in foregone sales tax (20-year equipment exemption on ~$35B in GPUs at 9.56% combined rate); Entergy seeking 80% ITEP property-tax exemption (~$237M/10yr on first two gas plants); Parish PILOT: 60% local property-tax exemption contingent on 300 jobs, 'quietly approved'",
            "water": "1.5M gal/day baseline draw from Mississippi River Alluvial Aquifer; state permit ceiling reported up to 23M gal/day — discrepancy unreconciled",
            "grid": "Entergy's $21.37B capital plan (7 gas plants, 3 batteries, nuclear uprates) to serve Meta; 15-year power contract; consumer advocates flag ~$3.2B stranded-asset risk when contract expires; ratepayer cost-shifting contested at LPSC",
            "transparency": "PILOTs 'quietly approved'; expanded from 2 GW to 5 GW without visible public process",
            "local_benefit": "'Several hundred jobs' for $50B+ — ratio is among the worst found",
        },
        "verdict": "The largest DC campus in the world: ~$3.3B in foregone sales tax, $237M in property-tax exemptions via Entergy, $3.2B in stranded-asset risk for ratepayers, and 'several hundred jobs.'",
        "sources": [
            "https://news.constructconnect.com/meta-expands-louisiana-data-center-to-5gw-lifts-richland-parish-investment-above-50-billion",
            "https://www.nola.com/news/data-center-meta-amazon-louisiana-tax-break/article_6ccd632e-f470-425a-ad8b-0fba3916bd4d.html",
        ],
    },
    {
        "company": "xAI", "location": "Southaven, DeSoto County", "state": "MS",
        "size_mw": 2000, "announced": "Jan 2026", "investment": "$20B",
        "status": "approved",
        "scores": {
            "revenue": 0, "tax": 1, "water": None, "grid": None,
            "transparency": 1, "local_benefit": 1,
        },
        "notes": {
            "revenue": "No community fund disclosed",
            "tax": "MS Data Center Incentive Act: 10-year sales/use exemption; fee-in-lieu ≥1/3 of normal ad valorem levy (statutory), capped at 30 years (no single item >10 years); actual executed fee % not public",
            "water": "Not disclosed; NAACP + coalition filed federal Clean Air Act suit April 2026",
            "grid": "Not disclosed",
            "transparency": "State announcement; DeSoto County fee-in-lieu agreement not public",
            "local_benefit": "~100 direct jobs for $20B",
        },
        "verdict": "Largest private investment in Mississippi history — 100 jobs, statutory-minimum tax payments, federal lawsuit over air quality.",
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
            "tax": "Not itemized publicly; Foxconn tax-deal precedent looms large",
            "water": "Microsoft committed to zero-water cooling designs for new builds",
            "grid": "Not disclosed",
            "transparency": "Plan Commission 5–2 and Village Board approval; public process",
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
            "tax": "50% real property + 85% personal property tax incentive grants, 10-year minimum investment",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Terms public via county filings",
            "local_benefit": "Job numbers not specified",
        },
        "verdict": "Heavy tax incentives (85% personal property) in a state with 14 active moratoriums.",
        "sources": ["https://www.datacenterdynamics.com/en/news/microsoft-to-invest-at-least-1bn-on-four-data-centers-in-catawba-county-nc/"],
    },
    {
        "company": "Microsoft", "location": "Person County", "state": "NC",
        "size_mw": 300, "announced": "2024–26", "investment": None,
        "status": "proposed",
        "scores": {
            "revenue": 0, "tax": 0, "water": 1, "grid": 0,
            "transparency": 0, "local_benefit": 0,
        },
        "notes": {
            "revenue": "No community fund; offered to fund new EMS facility after road closure caused 11-min-longer response times",
            "tax": "NC statewide DC sales/use exemption ($75M+ investment threshold); state DC breaks cost ~$57M/yr total; operators not required to report amounts claimed",
            "water": "'Water-positive' pledge — not binding; ~500K gal/day implied from infrastructure asks (40K gal/day cited as '~8%' of eventual need)",
            "grid": "Duke building 2×1,360 MW gas plants at Person County Energy Complex (48× county household consumption); 9.5% residential rate increase; NCUC large-load tariff settlement Jul 2026",
            "transparency": "NDAs signed by county manager, attorney, and ED director before rezoning; Aug 2024 rezoning without disclosing end user; records released then withdrawn 36 minutes later; all Microsoft commitments voluntary, not binding",
            "local_benefit": "No jobs committed; voluntary pledges for local IT training and nonprofits",
        },
        "verdict": "NDAs between a corporation and elected officials, records released then snatched back, rezoning without disclosure, and 2.7 GW of gas plants in a county that uses 57 MW. The secrecy is the score.",
        "sources": [
            "https://www.theassemblync.com/news/business/person-county-microsoft-data-center-nondisclosure-agreements/",
            "https://www.theassemblync.com/news/business/data-centers-economic-impact-north-carolina/",
        ],
    },
    {
        "company": "Compass", "location": "Meridian, Lauderdale County", "state": "MS",
        "size_mw": 500, "announced": "Jan 2025", "investment": "$10B",
        "status": "approved",
        "scores": {
            "revenue": 0, "tax": 0, "water": None, "grid": None,
            "transparency": 0, "local_benefit": 0,
        },
        "notes": {
            "revenue": "$4M county site grant is a cost TO the county, not a payment from the developer",
            "tax": "10-yr state income/franchise exemption + sales/use exemption; secondary source claims 66% property-tax reduction for 30 years (unverified); named 'Worst Economic Development Deal of 2025' by Center for Economic Accountability",
            "water": "Mississippi Power 500 MW via dedicated substation; PSC special negotiated contract; rate terms not public",
            "grid": "Not disclosed",
            "transparency": "Announced via Governor's office; county supervisors admitted (Nov 2025) they still lack confirmed revenue projections; no CBA",
            "local_benefit": "No committed headcount from Compass; first tenant: 20 jobs/$100M equipment",
        },
        "verdict": "Named 'Worst Economic Development Deal of 2025.' County supervisors admitted they don't know their own revenue projections. 20 jobs from the first tenant.",
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
            "transparency": "HOA lawsuit overturned rezoning (Aug 2025); court stayed ruling (Oct 2025)",
            "local_benefit": "Years of unchecked growth triggered voter revolt; 8–15% property value decline near campuses",
        },
        "verdict": "The cautionary tale — decades of DC growth without protections led to property value drops and a political revolt.",
        "sources": [
            "moratorium_outcomes:Prince William County",
            "https://patch.com/virginia/manassas/digital-gateway-rezoning-overturned-judge-prince-william-county",
        ],
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
            "revenue": None, "tax": None, "water": 0, "grid": 1,
            "transparency": 0, "local_benefit": 1,
        },
        "notes": {
            "revenue": "County projects $30M–108M/yr revenue but no binding agreement; no community fund",
            "tax": "Not disclosed",
            "water": "Both water-rights change-of-use applications WITHDRAWN after 4,000+ public comments/protests; as of Jul 2026, Stratos has NO approved water right — project cannot legally operate",
            "grid": "Off-grid/self-generating via gas (Ruby Pipeline); Phase 1 = 3 GW; environmental review ongoing",
            "transparency": "MIDA board + county commission approved with controversy; conditional-use permit terms not public; county tabled once then approved after continued pressure",
            "local_benefit": "~2,000 permanent jobs projected at full buildout; nothing binding",
        },
        "verdict": "9 GW approved with no water rights (both applications withdrawn after 4,000+ protests), no binding revenue agreement, and no public permit terms. Community opposition is winning the water fight.",
        "sources": [
            "https://www.ksl.com/article/51355852/worlds-largest-data-center-campus-could-be-coming-to-central-utah",
            "https://www.techradar.com/pro/utah-just-approved-a-data-center-twice-the-size-of-manhattan-that-will-consume-more-electricity-than-the-entire-state",
        ],
    },
    {
        "company": "DC Blox", "location": "East Side / Warren Township, Indianapolis", "state": "IN",
        "size_mw": 52, "announced": "Apr–Jul 2026", "investment": "$2B",
        "status": "approved",
        "scores": {
            "revenue": 0, "tax": None, "water": 2, "grid": 2,
            "transparency": 1, "local_benefit": 0,
        },
        "notes": {
            "revenue": "$20K/yr for 5 years to Pennsy Trail ($100K total) — negligible for $2B",
            "tax": "Not disclosed; KY-style incentive not confirmed",
            "water": "Closed-loop cooling, no groundwater draw",
            "grid": "AES Indiana: large-load pays ≥80% of infrastructure costs per IN statute; DC Blox pledged to pay all utility infrastructure costs",
            "transparency": "MDC approved 6–1 (not City Council — use variance, not rezoning); 83% opposition figure from informal councilor survey, not formal hearing; DC Blox pledges may not be legally binding conditions",
            "local_benefit": "17–21 permanent jobs; scaled down from 80 MW/3 buildings to 52 MW/2 buildings after opposition; adjacent to elementary school; brownfield site",
        },
        "verdict": "21 jobs and $100K in trail funding for a $2B project approved over 83% community opposition — on a brownfield next to an elementary school.",
        "sources": ["https://www.wfyi.org/wfyi-news/2026-07-15/east-side-data-center-wins-approval-despite-community-opposition"],
    },
    {
        "company": "Poe Companies / PowerHouse", "location": "West Louisville", "state": "KY",
        "size_mw": 400, "announced": "Jan 2025", "investment": None,
        "status": "approved",
        "scores": {
            "revenue": 0, "tax": None, "water": None, "grid": None,
            "transparency": 0, "local_benefit": 0,
        },
        "notes": {
            "revenue": "No community fund, no PILOT",
            "tax": "KY HB 775: up to 50-year sales/use tax exemption available but not yet granted to this project; projected $68M/yr in local tax revenue (unverified)",
            "water": "Louisville Water says it can meet demand from Ohio River; no specific gal/day commitment or agreement found",
            "grid": "400 MW = 85% of LG&E's 330,000 residential customers; 335 MW initial, near-term to 402 MW; no LG&E tariff filing or cost-allocation found",
            "transparency": "No rezoning required — classified as 'telecommunications hotel' under outdated code; Metro Council moratorium tabled Oct 2025; Planning Commission 6–1, not Council vote; Council's DC zoning ordinance was '141 days overdue'",
            "local_benefit": "No jobs committed; Rubbertown environmental-justice area; 20+ residents spoke in opposition",
        },
        "verdict": "400 MW in a Rubbertown EJ neighborhood, classified as a 'telecommunications hotel' to bypass Council review, with no CBA, no jobs commitment, and no water terms.",
        "sources": [
            "https://www.lpm.org/news/2026-03-05/west-louisville-data-center-approved-despite-opposition",
            "https://www.whas11.com/article/news/local/louisville-data-center-regulations-overdue-metro-council-office-of-planning-kentucky/417-8d3dd614-e32b-4ba9-a05c-e6f075df48c8",
        ],
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
        "company": "Vantage", "location": "Storey County", "state": "NV",
        "size_mw": 224, "announced": "2025", "investment": "$3B",
        "status": "approved",
        "scores": {
            "revenue": 0, "tax": 0, "water": 0, "grid": None,
            "transparency": 0, "local_benefit": 0,
        },
        "notes": {
            "revenue": "No community fund or CBA",
            "tax": "~$30.8M in state tax abatements for first 2 of 4 buildings; NV13/NV14 filings not yet public",
            "water": "State Engineer denied 9 TRI GID groundwater expansion applications (Jan 2026) — 'no water left to appropriate'; Pyramid Lake Paiute Tribe opposed; no Vantage-specific water permit found",
            "grid": "PUCN docket 26-05028 (large-load service agreement) is sealed/confidential",
            "transparency": "NV Energy rate terms confidential; no CBA; water situation unresolved",
            "local_benefit": "20 direct FTEs across first 2 buildings for $3B",
        },
        "verdict": "$3B, 20 jobs, sealed power terms, and the State Engineer said there's no water left. The confidentiality itself is the finding.",
        "sources": ["https://vantage-dc.com/news/vantage-data-centers-invests-3-billion-to-deliver-ai-campus-in-growing-nevada-market/"],
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
            "tax": "$42M in combined tax breaks rushed through before state moratorium; program cost ballooned to $1.57B vs. $136M projection (>10x miss)",
            "water": "Not disclosed",
            "grid": "Not disclosed",
            "transparency": "Approved in rush before moratorium took effect — procedural end-run",
            "local_benefit": "Not disclosed",
        },
        "verdict": "$42M in tax breaks rushed through before a moratorium — from a program that cost Ohio 10x what was projected.",
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
