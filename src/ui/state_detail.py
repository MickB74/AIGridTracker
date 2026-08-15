"""
Reusable state profile renderer — extracted from studies_tab so both the
unified Map tab and the States & Officials tab can show full state detail
cards without duplicating code.
"""

import streamlit as st
import pandas as pd
import urllib.parse
from src.constants import (STATE_DC_DF, HYPERSCALERS_DF, AI_COMPETITOR_SITES_DF,
                           MORATORIUMS_DF, PROJECTS_DF, LOCAL_BODIES_DF,
                           LOCAL_OFFICIALS_DF, STATE_GRID_PROFILES,
                           COMPANY_CONCESSIONS, has_value)
from src.helpers import src_link, render_freshness
from src.services.news import fetch_news
from src.services.reddit import load_reddit_corpus

STATE_STUDIES = {
    "Michigan": {
        "title": "Data Centers in Michigan: Evaluation of Policy Controversies Regarding Hyperscale Data Center Development (June 2026)",
        "author": "Citizens Research Council of Michigan (Report 426)",
        "src_key": "crc_mich_2026",
        "pdf_url": "https://crcmich.org/PUBLICAT/2020s/2026/rpt426-data_centers_in_Michigan.pdf",
        "as_of": "2026-08-13",
        "summary": "Evaluation of tax policies, local grid capacity, water usage, and localized noise impacts.",
        "findings": [
            "**Modest Economic Multiplier**: High temporary construction impact (1,000+ workers), but low permanent operational jobs (a few dozen per campus). Host communities benefit most from local property taxes and Community Benefit Agreements.",
            "**Grid Capacity & Rates**: Michigan's grid can accommodate load under current policies, but rapid load growth risks shifting infrastructure costs onto residential ratepayers. The Michigan Public Service Commission (MPSC) now requires utilities to prove large load additions will not raise rates for other customers.",
            "**Clean Energy Goals**: The 2023 Clean Energy Law requires 100% clean targets. Heavy data center draw risks forcing fossil-fuel runtimes if generation buildout lag behind. Most developers in MI are now investing directly in storage/renewables to mitigate this.",
            "**Water Resources**: Unlikely to threaten overall water resources due to closed-loop or evaporative cooling designs, but localized groundwater draw should be monitored.",
            "**Noise Pollution**: Identified as the most concerning localized community impact; requires strict zoning and noise mitigation from local permitting agencies."
        ],
        "metrics": {
            "Peak Construction Jobs": "1,000+ workers",
            "Permanent Jobs": "20–50 per hyperscale site",
            "Water Threat Level": "Low (closed-loop standard)",
            "Primary Local Benefit": "Property Taxes / CBA"
        }
    },
    "Virginia": {
        "title": "Joint Legislative Audit and Review Commission (JLARC) Data Center Study (December 2024)",
        "author": "Commonwealth of Virginia (Report 591)",
        "src_key": "jlarc_va_2024",
        "pdf_url": "https://jlarc.virginia.gov/pdfs/reports/Rpt591.pdf",
        "as_of": "2026-08-13",
        "summary": "Comprehensive analysis of Loudoun County ('Data Center Alley') density, PJM transmission bottlenecks, and tax revenues.",
        "findings": [
            "**Tax Revenue Windfall**: Data centers generated over \\$1B in annual local tax revenue in Northern Virginia, significantly subsidizing residential public school systems and services.",
            "**Transmission Constraints**: Unprecedented cluster density in Loudoun & Prince William counties has triggered PJM transmission constraints, requiring billions in grid upgrades (e.g. 500kV lines) funded by all grid ratepayers.",
            "**Clean Energy Backlash**: Meeting hyperscaler green commitments (100% renewable matching) has led to massive solar land-use debates across rural Virginia counties.",
            "**Water Stewardship**: Transitioning away from open-loop evaporative cooling towards air-cooling has reduced water intensity, but older facilities still consume millions of gallons daily."
        ],
        "metrics": {
            "State DC Power Draw": "3,000+ MW (largest globally)",
            "Annual Local Tax Revenue": "\\$1.2+ Billion",
            "Grid Bottleneck Level": "High (PJM queues restricted)",
            "Zoning Controversy": "Agricultural land-use conversion"
        }
    },
    "Georgia": {
        "title": "Joint Committee on Data Center Tax Incentives & Grid Reliability (2024–2025)",
        "author": "Georgia General Assembly Special Study Committee",
        "src_key": "ga_house_2024",
        "pdf_url": "https://www.house.ga.gov/",
        "as_of": "2026-08-13",
        "summary": "Legislative review of state sales-tax breaks for data centers and rising grid capacity warnings.",
        "findings": [
            "**Incentive Suspensions**: Recommended temporary suspension or capping of sales-tax exemptions on data center equipment, arguing that the low operational employment does not justify the foregone state revenue.",
            "**Grid Capacity Crisis**: Georgia Power warned regulators that data centers are the primary driver of a massive upward revision in its peak load projections, prompting proposals to construct new fossil-fueled generation.",
            "**Local Benefits vs. State Cost**: While local counties gain substantial property taxes, the state loses sales tax revenue on server upgrades (which occur every 3-4 years)."
        ],
        "metrics": {
            "State Incentive Status": "Suspended / Capped (2025)",
            "Georgia Power Peak Revision": "+3,400 MW load forecast",
            "Fossil-Fuel Runtimes": "Increased (new gas units approved)",
            "Employment Multiplier": "Low (capital intensive)"
        }
    },
    "Oregon": {
        "title": "Data Centers and Energy Use in Oregon (2024)",
        "author": "Oregon Department of Energy (ODOE) Sector Report",
        "src_key": "oregon_doe_2024",
        "pdf_url": "https://www.oregon.gov/energy/data-and-reports/pages/biennial-energy-report.aspx",
        "as_of": "2026-08-15",
        "summary": "Statewide review of energy draw, water rights in The Dalles (Columbia River), and utility disclosure laws.",
        "findings": [
            "**Columbia River Water Draw**: Spotlights Google's major campus at The Dalles. Evaporative cooling draws significant water from the municipal aquifer, causing municipal water rights disputes during dry seasons.",
            "**Hydroelectric Load**: Historically attracted by cheap Bonneville Power Administration (BPA) hydropower. However, hydro capacity is fully allocated, forcing new expansion to draw from mixed Pacific Northwest grids with higher carbon intensities.",
            "**Transparency Laws**: Led to new state laws regarding municipal utility disclosure. Utilities are now permitted to release actual water consumption figures, which were previously protected as proprietary trade secrets."
        ],
        "metrics": {
            "Water Source": "Columbia River / Aquifer",
            "Energy Source": "BPA Hydropower + Mixed Grid",
            "Transparency Level": "Improved (New state disclosure laws)",
            "Primary Issue": "Water rights vs. Agricultural demand"
        }
    },
    "Maryland": {
        "title": "Critical Infrastructure Streamlining Act of 2024 & State Data Center Impact Mandate (2024)",
        "author": "Maryland General Assembly (CISA / SB 116)",
        "src_key": "md_assembly_2024",
        "pdf_url": "https://mgaleg.maryland.gov/",
        "as_of": "2026-08-13",
        "summary": "Legislative response to utility generator permit denials and creation of state-wide environmental impact study.",
        "findings": [
            "**Backup Generator Controversy**: Aligned Data Centers canceled a massive \\$30B project in late 2023 after the Maryland PSC denied a permit for 168 diesel backup generators due to air quality emissions thresholds.",
            "**Regulatory Streamlining (CISA)**: In May 2024, Maryland enacted the Critical Infrastructure Streamlining Act to exempt data center backup power from Certificate of Public Convenience and Necessity (CPCN) reviews to attract investment.",
            "**Environmental Safeguards**: Environmental groups expressed concern over local particulate and carbon emissions from diesel backup arrays, prompting the state to commission a comprehensive data center impact study due September 1, 2026."
        ],
        "metrics": {
            "Streamlining Bill (CISA)": "Passed (May 2024)",
            "Canceled Project Investment": "\\$30 Billion",
            "Controversial Hardware": "168 Diesel Generators",
            "Comprehensive Study Due": "Sept 1, 2026"
        }
    },
    "Indiana": {
        "title": "Indiana Utility Regulatory Commission Grid & Water Studies (2026)",
        "author": "Indiana General Assembly / IURC (HB 1245)",
        "src_key": "iurc_indiana_2026",
        "pdf_url": "https://iga.in.gov/",
        "as_of": "2026-08-13",
        "summary": "Administrative mandates on ratepayer protection, utility load forecasts, and local water inventory reviews.",
        "findings": [
            "**Ratepayer Cost-Shifting**: House Bill 1245 was introduced in the 2026 session to mandate that the IURC study how data center demand affects retail electric rates, ensuring residential users do not subsidize transmission expansions.",
            "**Statewide Water Inventory**: Due to significant Meta (\\$10B in La Porte) and Amazon (\\$15B in Lebanon) campuses, the state is currently building a statewide water inventory by end of 2026 to monitor large industrial draws.",
            "**County-Level Moratoriums**: Due to perceived gaps in state environmental oversight, multiple Indiana counties and cities (including Indianapolis) have enacted temporary data center construction moratoriums to protect local resources."
        ],
        "metrics": {
            "IURC Study Mandate": "Active (HB 1245, 2026)",
            "Featured Projects": "Amazon (\\$15B), Meta (\\$10B)",
            "Local Moratoriums": "Enacted (multiple counties)",
            "State Water Inventory": "Due Late 2026"
        }
    },
    "New Jersey": {
        "title": "New Jersey Hyperscale Grid Studies & Market Inventory (2025–2026)",
        "author": "NJBPU / New Jersey Policy Perspective (NJPP) Research",
        "src_key": "nj_bpu_2026",
        "pdf_url": "https://www.nj.gov/bpu/",
        "as_of": "2026-08-13",
        "summary": "Administrative investigations on grid costs alongside independent market assessments of wholesale compute capacity.",
        "findings": [
            "**Market Capacity Inventory**: NJ holds approximately **1.04 GW** of total data center power capacity in 2026, projected to reach **1.23 GW by 2031**. This makes the state a top-5 U.S. data center market.",
            "**Operational vs. Planned**: NJ hosts **12 active wholesale/colocation campuses** representing roughly **325 MW** of operational draw. There are **7 major planned expansion projects** in the pipeline representing an additional **640 MW** of capacity.",
            "**Severe Supply Constraints**: Driven by NYC-proximity financial trading links and AI cloud deployments, NJ's vacancy rate is under **4%** (occupancy at 96%). Major hubs are concentrated in Secaucus, Piscataway, and Carteret (Equinix, Digital Realty, DataBank).",
            "**Grid Cost Shifting (P.L. 2025 c. 98 / A-796)**: The NJBPU and independent watchdogs (NJPP) warn that data centers trigger massive utility transmission cost-sharing. In July 2026, Governor Sherrill signed A-796 requiring specific large load tariffs (>= 50 MW) to make operators pay for their own grid upgrades."
        ],
        "metrics": {
            "Total Power Capacity": "1.04 GW (2026)",
            "Operational / Planned": "325 MW / 640 MW",
            "Market Vacancy Rate": "Under 4% (Highly constrained)",
            "Featured Hubs": "Secaucus, Piscataway, Carteret"
        }
    },
    "Texas": {
        "title": "Senate Bill 6 (89th Legislature): Large-Load Interconnection Standards & the 2026 ERCOT Queue Audit",
        "author": "Texas Legislature (Senate Research Center); 2026 audit directive by the Office of the Governor",
        "src_key": "tx_sb6_2025",
        "pdf_url": "https://capitol.texas.gov/tlodocs/89R/analysis/pdf/SB00006F.pdf",
        "as_of": "2026-08-15",
        "summary": "State rules for connecting data centers and other large loads to the ERCOT grid — cost allocation, mandatory curtailment during grid emergencies, and a separate 2026 gubernatorial audit of the interconnection queue.",
        "findings": [
            "**Large-load interconnection standards (SB 6)**: Signed June 20, 2025, SB 6 directs the Public Utility Commission of Texas (PUCT) to set statewide standards for connecting large loads to ERCOT, applying to new or expanded sites above a 75 MW demand threshold (the PUCT may set it lower).",
            "**Residents share of load shed**: The statute's stated goals include protecting residential customers during shortages by requiring large loads to share the load-shed obligation, and it directs the PUCT to reevaluate the Four Coincident Peak (4CP) transmission cost-allocation method by December 31, 2026.",
            "**Mandatory curtailment**: Transmission-voltage large loads connected after December 31, 2025 must install equipment allowing them to be curtailed during firm load shed; a new demand-management service can direct loads of at least 75 MW to curtail for the duration of an Energy Emergency Alert with 24-hour notice.",
            "**Cost and disclosure conditions**: Large loads face a minimum \\$100,000 interconnection study fee, per-MW financial security, proof of site control, and disclosure of duplicative 'substantially similar' requests at other sites, and must contribute to the utility's cost to connect them.",
            "**2026 queue audit (separate, gubernatorial)**: On August 3, 2026 the Governor directed the PUCT and ERCOT to audit data centers in the interconnection queue before projects proceed. BloombergNEF — an analyst firm, not a state body — projects the review could delay roughly 49.8 GW of load and cost projects up to \\$15 billion; treat those figures as a projection, not a state finding."
        ],
        "metrics": {
            "Instrument": "SB 6, 89th Legislature (June 2025)",
            "Large-load threshold": "75 MW (PUCT may lower)",
            "Emergency curtailment": "Large loads shed during grid emergencies",
            "Queue under audit": "~474 GW of requests, ~90% data centers (Gov., 2026)"
        }
    },
    "Arizona": {
        "title": "Arizona Energy Promise Taskforce Report (2026)",
        "author": "Arizona Energy Promise Taskforce (Gov. Katie Hobbs, Executive Order 2025-13)",
        "src_key": "az_energy_promise_2026",
        "pdf_url": "https://resilient.az.gov/sites/default/files/2026-04/arizona-energy-promise-taskforce-report.pdf",
        "as_of": "2026-08-15",
        "summary": "A 36-member governor's taskforce delivered 31 consensus recommendations on meeting Arizona's fast-growing electricity demand, several aimed squarely at large-load data-center customers.",
        "findings": [
            "**Cost-shift protection via the ACC**: The taskforce backs the Arizona Corporation Commission's existing large-load process (Docket E-00000A-25-0069) 'to prevent cost shifts, mitigate stranded asset risks, and increase development transparency.'",
            "**Bring-your-own-capacity**: It recommends exploring BYOC initiatives so large loads work with utilities to help deliver their own power.",
            "**Tax and financial incentives**: It recommends the state 'update tax and financial incentives for large load customers' — news coverage framed this as revisiting the data-center sales-tax exemption, and three members (the Data Center Coalition, Microsoft, and Google) dissented. Cite the taskforce's own softer wording.",
            "**Community engagement**: It recommends requiring or incentivizing large-load customers to engage communities and invest in community-identified priorities, and to help local governments navigate large-load development.",
            "**Water**: Among overarching recommendations it calls to 'encourage transparent and responsible water use in project development' — notably not framed as a data-center-specific mandate, despite Arizona's water stress."
        ],
        "metrics": {
            "Instrument": "Executive Order 2025-13",
            "Recommendations": "31 (36-member taskforce)",
            "Projected peak demand": "Up to +40% over 15 years",
            "Report released": "April 2026"
        }
    },
    "North Carolina": {
        "title": "North Carolina Energy Policy Task Force — Interim Report (February 2026)",
        "author": "NC Energy Policy Task Force (Gov. Josh Stein, Executive Order No. 23)",
        "src_key": "nc_eptf_2026",
        "pdf_url": "https://governor.nc.gov/nceptf2026interimreport/open",
        "as_of": "2026-08-15",
        "summary": "The governor's task force found data centers driving much of North Carolina's projected load growth, warned of cost-shifting to other ratepayers, and made nine preliminary recommendations.",
        "findings": [
            "**Load growth**: Total net load on Duke's two NC systems is projected to rise 16%–60% over 15 years, versus just 7% statewide over the prior two decades — a large share driven by data centers and other large loads.",
            "**Cost-shifting warning**: Meeting large-load growth needs new generation and transmission that 'could increase rates on all customers unless the primary users of new infrastructure bear the cost burden.'",
            "**No reliable data-center data**: The report finds 'there is not reliable public data for the total number and size of existing and proposed data centers in North Carolina,' leaving a historically wide range in load forecasts.",
            "**Concentrated demand**: Data centers are about 30% of Duke's economic-development pipeline but roughly 80% of its projected demand (a Duke figure reproduced in the report), while residential bills rose ~30% from 2017–2024 — nearly two-thirds of that from fuel costs.",
            "**Carbon target**: North Carolina's statutory target (HB 951, 2021) requires Duke generation to be carbon-neutral by 2050; the report finds load growth may challenge that target but, with the right policies, could be an opportunity to build more carbon-free power.",
            "**Two data-center-specific asks**: Of nine preliminary recommendations, two target data centers directly — reviewing the value of their sales-and-use tax exemptions, and requiring energy and water usage reporting."
        ],
        "metrics": {
            "Instrument": "Executive Order No. 23 (Aug 2025)",
            "Projected load growth": "16%–60% over 15 years (Duke NC)",
            "Data-center demand share": "~80% of Duke pipeline demand",
            "Recommendations": "9 preliminary (2 data-center-specific)"
        }
    }
}


def render_state_profile(selected_state):
    """Render a full state data center profile card.

    Expects *selected_state* to be a full state name (e.g. "Texas") that
    exists in STATE_DC_DF.  Renders curated deep-dives for states in
    STATE_STUDIES and dynamic profiles for all others, plus campus table
    and news/Reddit feeds.
    """
    row = STATE_DC_DF[STATE_DC_DF["state"] == selected_state]
    if row.empty:
        st.warning(f"No data available for {selected_state}.")
        return
    row = row.iloc[0]

    st.markdown(f"## {selected_state} Data Center Profile")

    is_curated = selected_state in STATE_STUDIES

    if is_curated:
        study = STATE_STUDIES[selected_state]
        _verified = study.get("as_of")
        _verified_note = f" · Verified {_verified}" if _verified else " · Verification date not recorded"
        st.caption(f"**Curated Policy Deep-Dive** · Reference: {src_link(study['src_key'])}{_verified_note}")
        st.markdown(f"*{study['summary']}*")

        cols = st.columns(len(study["metrics"]))
        for i, (k, v) in enumerate(study["metrics"].items()):
            cols[i].metric(k, v)

        st.divider()
        st.markdown("#### Curated Report Findings")
        for finding in study["findings"]:
            st.markdown(f"- {finding}")

        st.divider()
        state_slug = selected_state.lower().replace(" ", "-")
        dc_map_url = f"https://www.datacentermap.com/usa/{state_slug}/"
        dcl1, dcl2 = st.columns(2)
        dcl1.markdown(f"[Download Full Official Study PDF]({study['pdf_url']})")
        dcl2.markdown(f"[View {selected_state} Directory on Data Center Map]({dc_map_url})")
        render_freshness(st, "STATE_STUDIES")
    else:
        st.caption(f"**Data Center Market Profile** · Source: {src_link('electricchoice')} / Lawrence Berkeley Lab")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Active Facilities", f"{row['dc_count']}")
        c2.metric("Power Draw", f"{row['twh_year']:.1f} TWh/yr")
        pct_us = (row["twh_year"] / 176.0) * 100
        c3.metric("US Power Share", f"{pct_us:.1f}%")
        pipeline_status = "Active Projects" if row["upcoming"] else "Stable Market"
        c4.metric("Upcoming Pipeline", pipeline_status)

        st.divider()
        st.markdown("#### Grid Integration & Local Impacts")
        st.markdown(
            f"**Clustered Operator Hubs**: Primary facilities and operators in {selected_state} are "
            f"concentrated in: *{row['major_hubs']}*."
        )

        if row["twh_year"] >= 5.0:
            st.warning(
                f"**High Grid Demand**: Drawing {row['twh_year']:.1f} TWh annually, {selected_state} represents a major cluster "
                "for industrial load. Utilities and state public service commissions are heavily reviewing interconnection queues "
                "to prevent cost-shifting to residential ratepayers."
            )
            st.markdown(
                "- **Power Cost-Shifting**: Large load connections require substantial substation upgrades. Regulators are moving towards dedicated "
                "tariffs ensuring hyperscalers pay for transmission buildouts directly."
                "\n- **Water Scarcity Risk**: Dense server concentrations require millions of gallons of cooling water daily. Closed-loop, air-cooled "
                "designs are increasingly mandated in local municipal zoning codes."
            )
        else:
            st.info(
                f"**Stable Load Profile**: With a load of {row['twh_year']:.1f} TWh annually across {row['dc_count']} facilities, "
                f"{selected_state}'s data center footprint is currently manageable under standard utility tariffs. Infrastructure is typically "
                "integrated without major grid-reliability risks."
            )
            st.markdown(
                "- **Local Economic Impact**: While economic benefits during operations are modest (limited permanent jobs), "
                "local municipalities benefit from commercial property taxes and construction-phase employment multipliers."
            )

        st.divider()
        state_slug = selected_state.lower().replace(" ", "-")
        dc_map_url = f"https://www.datacentermap.com/usa/{state_slug}/"
        dcl1, dcl2 = st.columns(2)
        dcl1.markdown(f"[View U.S. Data Center Power Map on ElectricChoice.com](https://www.electricchoice.com/datacenters/)")
        dcl2.markdown(f"[View {selected_state} Directory on Data Center Map]({dc_map_url})")

    # Grid profile context
    abbrev = row["abbrev"]
    grid_prof = STATE_GRID_PROFILES.get(selected_state, {})
    if grid_prof:
        st.divider()
        st.markdown("#### Grid & Resource Profile")
        gc1, gc2, gc3 = st.columns(3)
        gc1.metric("Residential Rate", f"\\${grid_prof.get('rate', 0):.2f}/kWh")
        gc2.metric("Grid Carbon", f"{grid_prof.get('gco2', 0)} gCO₂/kWh")
        gc3.metric("Water Stress", grid_prof.get("water_stress", "unknown").title())

    # Campus table
    campuses = pd.concat([HYPERSCALERS_DF, AI_COMPETITOR_SITES_DF], ignore_index=True)
    state_campuses = campuses[campuses["state"] == abbrev].copy()
    if not state_campuses.empty:
        st.divider()
        st.markdown(f"#### Hyperscaler & AI Campuses in {selected_state}")
        st.caption("Individual facility locations. Google and Meta publish precise lists; other coordinates are metro/county centroids.")
        campus_list = []
        for _, r in state_campuses.iterrows():
            query_str = f"{r['company']} data center {r['location']} {selected_state}"
            maps_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(query_str)}"
            company_clean = r["company"].replace(" (AWS)", "").replace(" (Colossus)", "").split(" · ")[0]
            location_clean = r["location"].split(" (")[0]
            role_terms = (
                '"data center technician" OR "critical facilities" OR '
                '"data center operations" OR "site operations" OR "facilities engineer" OR '
                '"mechanical technician" OR "electrical technician" OR "commissioning" OR '
                '"construction manager" OR "site contractor" OR "general contractor" OR '
                '"MEP" OR "controls technician"'
            )
            li_query = f'{company_clean} "{location_clean}" ({role_terms})'
            linkedin_url = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(li_query)}"
            exec_terms = (
                '"data center site selection" OR "site acquisition" OR '
                '"energy procurement" OR "energy strategy" OR "head of energy" OR '
                '"utility partnerships" OR "grid strategy" OR "power procurement" OR '
                '"infrastructure development" OR "data center development"'
            )
            exec_query = f'{company_clean} ({exec_terms})'
            exec_url = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(exec_query)}"
            campus_list.append({
                "Company": r["company"],
                "Metro/Location": r["location"],
                "Coordinates": f"{r['lat']:.4f}, {r['lon']:.4f}",
                "Source": src_link(r["src"]),
                "Google Maps": maps_url,
                "LinkedIn Search": linkedin_url,
                "Exec Search": exec_url
            })
        st.dataframe(
            pd.DataFrame(campus_list), use_container_width=True, hide_index=True,
            column_config={
                "Company": st.column_config.TextColumn(width="medium"),
                "Metro/Location": st.column_config.TextColumn(width="large"),
                "Coordinates": st.column_config.TextColumn(width="small"),
                "Source": st.column_config.TextColumn(width="small"),
                "Google Maps": st.column_config.LinkColumn("Google Maps Directions", display_text="View Map", width="medium"),
                "LinkedIn Search": st.column_config.LinkColumn("Local Staff Directory", display_text="Find Staff", width="medium"),
                "Exec Search": st.column_config.LinkColumn("Energy & Siting Leadership", display_text="Find Execs", width="medium")
            })

    # Moratoriums in this state
    state_morats = MORATORIUMS_DF[MORATORIUMS_DF["state"] == abbrev]
    if not state_morats.empty:
        st.divider()
        st.markdown(f"#### Moratoriums & Pushback in {selected_state}")
        for _, m in state_morats.iterrows():
            status_badge = m["effective_status"]
            locality = m["locality"]
            note = m["note"] if has_value(m["note"]) else ""
            src = f" · [Source]({m['source']})" if has_value(m["source"]) else " · *Unverified*"
            st.markdown(f"- **{locality}** — {status_badge}{' · ' + note if note else ''}{src}")

    # Projects in this state
    state_projs = PROJECTS_DF[PROJECTS_DF["state"] == abbrev]
    if not state_projs.empty:
        st.divider()
        st.markdown(f"#### Tracked Projects in {selected_state}")
        for _, p in state_projs.iterrows():
            mw_str = f" · {p['size_mw']:.0f} MW" if has_value(p["size_mw"]) else ""
            st.markdown(f"- **{p['name']}** ({p['locality']}){mw_str} — {p['stage']}")

    # News & Reddit
    st.divider()
    st.subheader(f"Live Local Updates: {selected_state}")
    st.caption(
        f"Google News hits for data centers in {selected_state} and grassroots "
        "mentions filtered from today's Reddit local grid discussion snapshot."
    )
    feed_col1, feed_col2 = st.columns(2)

    with feed_col1:
        st.markdown("##### Recent Google News")
        news_q = f'"{selected_state}" "data center" (electricity OR grid OR water OR community OR ratepayer OR moratorium)'
        news_items, news_err = fetch_news(news_q, limit=6)
        if news_err or news_items is None:
            gn_url = "https://news.google.com/search?q=" + urllib.parse.quote(news_q)
            st.warning("Google News feed is temporarily unavailable.")
            st.markdown(f"[Open search on Google News]({gn_url})")
        elif not news_items:
            st.info(f"No recent news articles found for data centers in {selected_state}.")
        else:
            for it in news_items:
                meta = " · ".join(x for x in (it["source"], it["published"]) if x)
                st.markdown(
                    f"- [{it['title']}]({it['link']})  \n"
                    f"  <small style='color:#9CA6B6'>{meta}</small>",
                    unsafe_allow_html=True
                )

    with feed_col2:
        st.markdown("##### Local Reddit Discussion")
        corpus, cerr = load_reddit_corpus(pd.Timestamp.now().strftime("%Y-%m-%d"))
        reddit_items = []
        if not corpus.empty:
            state_lower = selected_state.lower()
            abbrev_term = f" {abbrev} "
            has_selftext = "selftext" in corpus.columns
            match_mask = (
                corpus["title"].str.lower().str.contains(state_lower, na=False) |
                corpus["subreddit"].str.lower().str.contains(state_lower, na=False) |
                corpus["title"].str.contains(abbrev_term, na=False)
            )
            if has_selftext:
                match_mask = match_mask | (
                    corpus["selftext"].str.lower().str.contains(state_lower, na=False) |
                    corpus["selftext"].str.contains(abbrev_term, na=False)
                )
            matching_posts = corpus[match_mask]
            if not matching_posts.empty:
                for p in matching_posts.head(6).itertuples():
                    reddit_items.append({
                        "title": p.title, "link": p.link,
                        "meta": f"r/{p.subreddit} · {p.created}"
                    })

        if reddit_items:
            for it in reddit_items:
                st.markdown(
                    f"- [{it['title']}]({it['link']})  \n"
                    f"  <small style='color:#9CA6B6'>{it['meta']}</small>",
                    unsafe_allow_html=True
                )
        else:
            rq = f'data center "{selected_state}"'
            reddit_url = "https://www.reddit.com/search/?q=" + urllib.parse.quote(rq) + "&sort=new"
            st.info(f"No recent Reddit snapshot discussions found mentioning {selected_state}.")
            st.markdown(f"[Search Reddit Live for '{selected_state}']({reddit_url})")
