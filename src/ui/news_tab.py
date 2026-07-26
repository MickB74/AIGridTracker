import streamlit as st
import urllib.parse
import pandas as pd
import altair as alt
import pydeck as pdk
from src.constants import (
    COMPANY_STATEMENTS, COMPANY_FEED_TERMS, MORATORIUMS_DF,
    MORATORIUM_OUTCOMES,
    GOOGLE_DC_ELECTRICITY, GOOGLE_GHG, GOOGLE_WATER, GOOGLE_2025_HEADLINE,
    META_DC_ELECTRICITY, META_GHG, META_WATER, META_2024_HEADLINE,
    MICROSOFT_ENV_HEADLINE, AWS_ENV_HEADLINE,
)
from src.helpers import src_link
from src.services.news import fetch_news
from src.services.report_check import check_report_freshness, REPORT_REGISTRY

def render_news_tab():
    st.subheader("Community impact — the frictions and the value")
    st.caption("Towns are pausing or blocking projects over power bills, water, "
               "noise, and land use. The flashpoints, the value levers, and the "
               "trackers. (Live headlines now live in the **📰 News** tab.)")

    with st.expander("📑 On this page", expanded=False):
        st.markdown(
            "**1.** The recurring flashpoints · "
            "**2.** How communities extract value · "
            "**3.** Town case studies · "
            "**4.** Hyperscaler environmental scorecard · "
            "**5.** What they pay for electricity · "
            "**6.** Moratorium & ban tracker (map) · "
            "**7.** Case study outcomes"
        )

    st.markdown("#### The recurring flashpoints")
    issues = [
        ("💵", "Electricity bills & grid strain",
         "Surging data-center load raises wholesale prices and can shift "
         "transmission/capacity costs onto ordinary ratepayers; PJM's capacity "
         "price spiked ~10× on data-center-driven demand. Utilities also delay "
         "fossil-plant retirements to serve the load.",
         "data center electricity bills ratepayers grid strain news"),
        ("💧", "Water",
         "Evaporative cooling consumes potable water — millions of gallons a day "
         "at a large campus — a flashpoint in drought-prone metros (Phoenix, "
         "Texas, Georgia).",
         "data center water use cooling drought news"),
        ("🏘️", "Zoning, land use & moratoria",
         "Counties are enacting moratoria or rejecting rezonings amid resident "
         "opposition; some developers are pulling out of hostile jurisdictions.",
         "data center zoning moratorium residents oppose rezoning news"),
        ("🔊", "Noise",
         "Chillers and backup generators produce a constant low-frequency hum; "
         "noise complaints have driven lawsuits and setback rules (notably in "
         "Northern Virginia).",
         "data center noise complaints residents hum news"),
        ("🧾", "Tax breaks vs. local benefit",
         "Big sales/property-tax abatements versus relatively few permanent jobs "
         "fuel debate over whether the local trade-off pays off.",
         "data center tax breaks incentives few jobs news"),
        ("🛢️", "Backup diesel & air permits",
         "Fleets of diesel generators for backup draw air-quality scrutiny and "
         "permit fights near residential areas.",
         "data center backup diesel generators air quality permit news"),
    ]
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    cards = st.columns(3)
    for i, (icon, head, body, vquery) in enumerate(issues):
        with cards[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {icon}\n**{head}**")
                st.caption(body)
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("#### How communities extract value")
    st.caption("The flip side of the pushback: the levers through which a host "
               "community actually captures value from a data center. When these "
               "land, local support and future approvals follow; when they don't, "
               "opposition rises and supply shrinks.")
    value_levers = [
        ("👷", "Jobs & local workforce",
         "Construction crews during the build and skilled operations/security "
         "roles once live, plus demand for local trades and suppliers. A "
         "skilled local workforce is itself a top siting criterion — the value "
         "runs both ways.",
         "data center local jobs workforce economic impact"),
        ("🧾", "Tax base & fiscal revenue",
         "Property, sales and equipment taxes can materially expand a small "
         "county's budget — funding schools, roads and services. The live "
         "debate is abatements vs. permanent jobs, so communities increasingly "
         "negotiate the trade-off explicitly.",
         "data center property tax revenue county schools"),
        ("⚡", "Grid stability contributions",
         "Projects developed to *support* the grid — funding transmission "
         "upgrades, adding on-site generation or storage, and offering "
         "flexible/curtailable load — leave the local system more reliable "
         "than they found it.",
         "data center grid stability transmission upgrade flexible load"),
        ("☀️", "Shared clean power",
         "Green tariffs, community solar, on-campus solar PV and clean "
         "microgrids let residents and the operator draw from the same new "
         "clean supply — decarbonizing the local grid rather than just "
         "consuming from it.",
         "data center community solar green tariff clean microgrid"),
        ("🛡️", "Ratepayer protection",
         "Cost-allocation rules that make data centers pay for the grid "
         "capacity they trigger — rather than socializing it onto households — "
         "are the single biggest driver of whether a community feels it's "
         "gaining or subsidizing.",
         "data center cost allocation ratepayer protection tariff"),
        ("🤝", "Community-benefit agreements",
         "Direct, negotiated commitments — local infrastructure, workforce "
         "training, noise/water safeguards, community funds — turn a project "
         "into a proof point that de-risks the next site.",
         "data center community benefit agreement local investment"),
    ]
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    vcards = st.columns(3)
    for i, (icon, head, body, vquery) in enumerate(value_levers):
        with vcards[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {icon}\n**{head}**")
                st.caption(body)
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("#### 🏘️ Case Studies: Lessons & Data Filed in Towns")
    st.caption(
        "Specific municipal files, regulatory submissions, and lessons learned from the front lines of "
        "local data center development."
    )

    TOWN_CASES = {
        "Loudoun County, VA": {
            "operator": "Multiple Hyperscalers & Equinix",
            "data_filed": "Loudoun County Board of Supervisors noise ordinance audits (limiting low-frequency hum to 38 dBA at residential property lines) and zoning amendments requiring Special Use Permits (SUP) for data centers in all commercial zones.",
            "outcome": "Strict noise mitigation walls mandated; developers forced to install custom quiet chillers. Siting is prohibited within 1,000 feet of residential zoning boundaries.",
            "lesson": "Density clusters near residential areas trigger immediate noise lawsuits and grid bottlenecks. Siting now requires strict acoustic engineering from day one."
        },
        "The Dalles, OR": {
            "operator": "Google",
            "data_filed": "Municipal water rights filings and public record lawsuits. Google historically sued the city of The Dalles to protect their water draw figures as a proprietary 'trade secret' during drought seasons.",
            "outcome": "Google withdrew its lawsuit under intense community pressure in late 2023, disclosing a draw of **274.5 Million Gallons** (approx. 29% of the town's total water consumption).",
            "lesson": "Drought-prone communities will not tolerate utility secrecy. Operator transparency regarding local resource consumption is now a public expectation."
        },
        "Mesa, AZ": {
            "operator": "Meta, Google & EdgeCore",
            "data_filed": "Mesa City Council water allocation agreements and dry-cooling zoning resolutions.",
            "outcome": "Mesa enacted a resolution banning all open-loop evaporative cooling for new data centers, requiring closed-loop/dry-cooling setups for all future building permits.",
            "lesson": "Desert municipalities prioritize aquifer conservation over PUE. Operators must use air-cooling in the Southwest, accepting higher summer power draws."
        },
        "Frederick County, MD": {
            "operator": "Aligned Data Centers (Quantum Loophole)",
            "data_filed": "Maryland Public Service Commission CPCN permit application for **168 diesel backup generators** (representing ~504 MW of emergency capacity).",
            "outcome": "PSC rejected the air quality permit due to particulate limits, leading Aligned to cancel the $30B project. This prompted the state legislature to pass CISA (SB 116) to exempt backup power from full CPCN reviews.",
            "lesson": "Massive diesel backup arrays near residential areas are major regulatory vulnerabilities. Clean emergency power (batteries/hydrogen) is increasingly necessary."
        },
        "Lebanon, IN": {
            "operator": "Amazon (AWS) / Eli Lilly",
            "data_filed": "LEAP Innovation District pipeline planning and Indiana DNR aquifer extraction surveys. Proposed drawing 100 Million gallons/day from the Wabash River aquifer via a 35-mile pipeline.",
            "outcome": "Fierce protests from agricultural landowners and rural counties forced the governor to pause pipeline decisions and commission a comprehensive regional water survey.",
            "lesson": "Cross-county resource redirection triggers intense rural-agricultural backlash. Siting in dry agricultural zones requires regional, not just municipal, resource agreements."
        },
        "Secaucus / Piscataway, NJ": {
            "operator": "Equinix & Digital Realty",
            "data_filed": "New Jersey Board of Public Utilities (BPU) Large Load Tariff filings (under Assembly Bill A-796).",
            "outcome": "Governor Sherrill signed P.L. 2025 c. 98 into law, requiring specific tariffs making any large load addition (>= 50 MW) pay for its own grid substation upgrades directly.",
            "lesson": "Ratepayers will no longer subsidize industrial grid connections. Developers must budget millions in direct substation upgrades in their capital allocations."
        }
    }

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    selected_town = st.selectbox(
        "Select a town/county case study:",
        options=["Select a Town..."] + list(TOWN_CASES.keys())
    )

    if selected_town != "Select a Town...":
        case = TOWN_CASES[selected_town]
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**🏢 Operator / Project**: {case['operator']}")
            st.markdown(f"**📜 Specific Data Filed**:")
            st.caption(case['data_filed'])
        with c2:
            st.markdown(f"**Outcome / Regulatory Action**:")
            st.markdown(f"*{case['outcome']}*")
            st.markdown(f"**💡 Key Lesson Learned**:")
            st.info(case['lesson'])
    else:
        st.info("💡 Select a town or county from the dropdown above to view municipal filings, water/noise data, and lessons learned.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("#### What the companies say — by the numbers")
    st.caption(
        "The companies publish environmental reports with real data on "
        "electricity, water, and carbon. Below is what those reports actually "
        "show — read alongside the community concerns above. Full deep-dives "
        "are on the **Corporate Profiles** tab."
    )

    # -- Side-by-side headline comparison --------------------------------- #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("##### Hyperscaler environmental scorecard")
    st.caption(
        "Latest first-party reports: "
        + src_link("google_env_2026") + " · "
        + src_link("meta_env_2025") + " · "
        + src_link("msft_env_2025") + " · "
        + src_link("amzn_env_2025")
    )

    g = GOOGLE_2025_HEADLINE
    m = META_2024_HEADLINE
    ms = MICROSOFT_ENV_HEADLINE
    aw = AWS_ENV_HEADLINE

    scorecard = pd.DataFrame([
        {
            "Metric": "Data center electricity",
            "Google (FY2025)": f"{g['dc_twh']} TWh",
            "Microsoft (FY2025)": f"~{ms['dc_twh']} TWh (est.)",
            "AWS (CY2025)": f"~{aw['dc_twh']} TWh (est.)",
            "Meta (FY2024)": f"{m['dc_twh']} TWh",
            "Why it matters": "Total grid load — drives capacity charges on your bill",
        },
        {
            "Metric": "YoY electricity growth",
            "Google (FY2025)": f"+{g['yoy_electricity_growth_pct']}%",
            "Microsoft (FY2025)": "+24%",
            "AWS (CY2025)": "+34% (elec. emissions)",
            "Meta (FY2024)": f"+{(18.1-15.0)/15.0*100:.0f}%",
            "Why it matters": "How fast the load is increasing",
        },
        {
            "Metric": "Fleet PUE",
            "Google (FY2025)": f"{g['fleet_pue']}",
            "Microsoft (FY2025)": f"{ms['pue']} (design)",
            "AWS (CY2025)": f"{aw['pue']}",
            "Meta (FY2024)": f"{m['fleet_pue']}",
            "Why it matters": "Overhead energy per unit of compute (industry avg: 1.54)",
        },
        {
            "Metric": "Water consumed",
            "Google (FY2025)": f"{g['water_consumption_mgal']:,}M gal",
            "Microsoft (FY2025)": f"{ms['water_consumption_mgal']:,}M gal (FY24)",
            "AWS (CY2025)": f"{aw['water_consumption_mgal']:,}M gal (CY24)",
            "Meta (FY2024)": f"{m['water_consumption_ml'] * 0.264172:.0f}M gal",
            "Why it matters": "Potable water drawn from local supplies",
        },
        {
            "Metric": "Scope 2 (location-based)",
            "Google (FY2025)": f"{g['scope2_location_tco2e']/1e6:.1f}M tCO2e",
            "Microsoft (FY2025)": f"~{ms['scope2_location_mt']}M tCO2e (est.)",
            "AWS (CY2025)": f"~{aw['scope2_location_mt']}M tCO2e (est.)",
            "Meta (FY2024)": f"{m['scope2_location_tco2e']/1e6:.1f}M tCO2e",
            "Why it matters": "Actual grid carbon — what the atmosphere sees",
        },
        {
            "Metric": "Scope 2 (market-based)",
            "Google (FY2025)": f"{g['scope2_market_tco2e']/1e6:.2f}M tCO2e",
            "Microsoft (FY2025)": f"{ms['scope2_market_mt']}M tCO2e",
            "AWS (CY2025)": f"{aw['scope2_market_mt']}M tCO2e",
            "Meta (FY2024)": f"{m['scope2_market_tco2e']/1e3:.1f}K tCO2e",
            "Why it matters": "After renewable credits — what the company reports",
        },
        {
            "Metric": "Renewable match",
            "Google (FY2025)": f"{g['global_cfe_pct']}% hourly CFE",
            "Microsoft (FY2025)": "100% annual",
            "AWS (CY2025)": "100% annual (3rd yr)",
            "Meta (FY2024)": f"{m['renewable_match_pct']}% annual",
            "Why it matters": "Hourly matching is stricter than annual",
        },
    ])
    st.dataframe(scorecard, use_container_width=True, hide_index=True,
                 column_config={
                     "Metric": st.column_config.TextColumn(width="medium"),
                     "Why it matters": st.column_config.TextColumn(width="large"),
                 })
    st.caption(
        "**Reading the estimates:** Microsoft and AWS don't break out data-center-only "
        "electricity, so TWh and location-based Scope 2 marked *(est.)* are derived "
        "from their reported growth rates. Microsoft's market-based Scope 2 jumped "
        "0.26 → 2.7M tCO2e in FY2025 because it **stopped counting non-additional "
        "unbundled RECs** — the number went up because the accounting got more honest."
    )

    # -- Report freshness checker ------------------------------------------ #
    with st.expander("🔄 Check for newer reports"):
        st.caption(
            "These companies publish annually (May–October). This checks each "
            "company's report page for an edition newer than the one this app "
            "tracks. Cached for 24 hours."
        )
        if st.button("Check now", key="report_freshness_btn"):
            with st.spinner("Checking report pages..."):
                results = check_report_freshness()
            for res in results:
                if res["status"] == "newer":
                    st.warning(
                        f"**{res['company']}** — a **{res['latest_seen']}** edition "
                        f"appears to be out (this app tracks the {res['tracked']}). "
                        f"[Open report page]({res['url']})")
                elif res["status"] == "current":
                    st.success(
                        f"**{res['company']}** — {res['tracked']} is the latest. ✓")
                elif res["status"] == "unreachable":
                    st.info(
                        f"**{res['company']}** — couldn't reach the report page "
                        f"(offline or blocked). [Check manually]({res['url']})")
                else:
                    st.info(
                        f"**{res['company']}** — page loaded but no edition year "
                        f"found. [Check manually]({res['url']})")
        else:
            for company, info in REPORT_REGISTRY.items():
                st.markdown(
                    f"- **{company}**: tracking the {info['label']} — "
                    f"[report page]({info['url']})")
    st.caption(
        "**Location-based vs. market-based**: Location-based emissions reflect "
        "the actual carbon intensity of the grid where the data center operates. "
        "Market-based emissions subtract renewable energy credits (RECs) the "
        "company purchased — often from wind/solar farms hundreds of miles away. "
        "The gap between the two numbers tells you how much of their 'clean' "
        "claim is accounting vs. actual grid decarbonization."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # -- Electricity growth comparison chart ------------------------------- #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("##### Electricity consumption growth")

    g_elec = GOOGLE_DC_ELECTRICITY[["year", "dc_mwh"]].copy()
    g_elec["TWh"] = g_elec["dc_mwh"] / 1e6
    g_elec["Company"] = "Google"
    m_elec = META_DC_ELECTRICITY[["year", "dc_mwh"]].copy()
    m_elec["TWh"] = m_elec["dc_mwh"] / 1e6
    m_elec["Company"] = "Meta"
    elec_cmp = pd.concat([g_elec, m_elec], ignore_index=True)

    elec_chart = (
        alt.Chart(elec_cmp)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("TWh:Q", title="Data Center Electricity (TWh)"),
            color=alt.Color("Company:N",
                scale=alt.Scale(domain=["Google", "Meta"],
                                range=["#34a853", "#0866ff"]),
                legend=alt.Legend(title="")),
            tooltip=["Company:N", "year:O",
                     alt.Tooltip("TWh:Q", format=".1f", title="TWh")],
        ).properties(height=260)
    )
    st.altair_chart(elec_chart, use_container_width=True)
    st.caption(
        "Google's data center electricity grew 143% in four years (17.4 → 42.4 TWh). "
        "Meta grew 160% over the same span (6.97 → 18.1 TWh). Combined, these two "
        "companies alone consume more electricity than many U.S. states."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # -- Water consumption comparison chart -------------------------------- #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("##### Water consumption growth")

    g_water = GOOGLE_WATER[["year", "consumption"]].copy()
    g_water.columns = ["year", "mgal"]
    g_water["Company"] = "Google"
    m_water = META_WATER[["year", "consumption_ml"]].copy()
    m_water["mgal"] = m_water["consumption_ml"] * 0.264172
    m_water = m_water[["year", "mgal"]].copy()
    m_water["Company"] = "Meta"
    water_cmp = pd.concat([g_water, m_water], ignore_index=True)

    water_chart = (
        alt.Chart(water_cmp)
        .mark_area(opacity=0.25)
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("mgal:Q", title="Water Consumed (M gallons)"),
            color=alt.Color("Company:N",
                scale=alt.Scale(domain=["Google", "Meta"],
                                range=["#34a853", "#0866ff"]),
                legend=alt.Legend(title="")),
        ).properties(height=240)
    ) + (
        alt.Chart(water_cmp)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x="year:O", y="mgal:Q",
            color=alt.Color("Company:N",
                scale=alt.Scale(domain=["Google", "Meta"],
                                range=["#34a853", "#0866ff"])),
            tooltip=["Company:N", "year:O",
                     alt.Tooltip("mgal:Q", format=",.0f", title="M gal")],
        )
    )
    st.altair_chart(water_chart, use_container_width=True)
    st.caption(
        "Google consumed 10.9 billion gallons of water in 2025 — enough to supply "
        "~100,000 U.S. households for a year. Meta consumed 825 million gallons "
        "in 2024. Both figures are growing as campuses expand."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # -- Location-based emissions comparison ------------------------------- #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("##### Carbon emissions — what the grid actually sees")

    g_ghg = GOOGLE_GHG[["year", "scope2_location"]].copy()
    g_ghg["MtCO2e"] = g_ghg["scope2_location"] / 1e6
    g_ghg["Company"] = "Google"
    m_ghg = META_GHG[["year", "scope2_location"]].copy()
    m_ghg["MtCO2e"] = m_ghg["scope2_location"] / 1e6
    m_ghg["Company"] = "Meta"
    ghg_cmp = pd.concat([g_ghg, m_ghg], ignore_index=True)

    ghg_chart = (
        alt.Chart(ghg_cmp)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("MtCO2e:Q", title="Scope 2 Location-Based (Mt CO2e)"),
            color=alt.Color("Company:N",
                scale=alt.Scale(domain=["Google", "Meta"],
                                range=["#34a853", "#0866ff"]),
                legend=alt.Legend(title="")),
            tooltip=["Company:N", "year:O",
                     alt.Tooltip("MtCO2e:Q", format=".2f", title="Mt CO2e")],
        ).properties(height=260)
    )
    st.altair_chart(ghg_chart, use_container_width=True)
    st.caption(
        "Location-based Scope 2 emissions show what the atmosphere actually absorbs — "
        "before renewable-credit accounting. Google's real grid emissions nearly tripled "
        "from 5.2 Mt in 2019 to 15.1 Mt in 2025. The market-based figure (2.8 Mt) is "
        "far lower because of purchased credits — but credits don't reduce the actual "
        "carbon intensity of the grid your community breathes."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # -- Estimated utility spend --------------------------------------------- #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("##### What do they actually pay for electricity?")
    st.caption(
        "None of these companies disclose their utility spend or the rates they "
        "negotiate. But we can estimate it from their published consumption and "
        "public data on industrial electricity rates. Adjust the assumptions below."
    )

    rc1, rc2 = st.columns(2)
    with rc1:
        dc_rate = st.slider(
            "Estimated data center rate (\\$/kWh)",
            min_value=0.02, max_value=0.10, value=0.05, step=0.005,
            format="$%.3f",
            help="Large-load industrial contracts typically range $0.03–0.06/kWh. "
                 "Some economic-development tariffs go as low as $0.02.")
    with rc2:
        res_rate = st.slider(
            "Your residential rate (\\$/kWh)",
            min_value=0.08, max_value=0.30, value=0.16, step=0.01,
            format="$%.2f",
            help="U.S. average residential rate is ~$0.16/kWh (EIA, 2025). "
                 "Ranges from $0.10 (LA, WV) to $0.30+ (CT, MA, CA).")

    g_twh = g["dc_twh"]
    m_twh = m["dc_twh"]
    ms_twh = ms["dc_twh"]
    aw_twh = aw["dc_twh"]
    all_twh = g_twh + m_twh + ms_twh + aw_twh

    g_spend = g_twh * 1e9 * dc_rate
    m_spend = m_twh * 1e9 * dc_rate
    ms_spend = ms_twh * 1e9 * dc_rate
    aw_spend = aw_twh * 1e9 * dc_rate
    all_spend = g_spend + m_spend + ms_spend + aw_spend
    rate_ratio = res_rate / dc_rate

    all_equiv_homes = all_twh * 1e6 / 10.5

    sp1, sp2, sp3, sp4 = st.columns(4)
    sp1.metric("Google est. spend",
               f"${g_spend / 1e9:.1f}B/yr",
               f"{g_twh} TWh × ${dc_rate:.3f}")
    sp2.metric("AWS est. spend",
               f"${aw_spend / 1e9:.1f}B/yr",
               f"~{aw_twh} TWh × ${dc_rate:.3f}")
    sp3.metric("Microsoft est. spend",
               f"${ms_spend / 1e9:.1f}B/yr",
               f"~{ms_twh} TWh × ${dc_rate:.3f}")
    sp4.metric("Meta est. spend",
               f"${m_spend / 1e9:.1f}B/yr",
               f"{m_twh} TWh × ${dc_rate:.3f}")

    sq1, sq2, sq3 = st.columns(3)
    sq1.metric("All four combined",
               f"${all_spend / 1e9:.1f}B/yr",
               f"{all_twh:.0f} TWh total")
    sq2.metric("Rate discount vs. you",
               f"{rate_ratio:.1f}×",
               f"You pay ${res_rate:.2f} — they pay ~${dc_rate:.3f}")
    sq3.metric("Combined household equiv.",
               f"{all_equiv_homes / 1e6:.1f}M homes",
               "at 10,500 kWh/yr avg")

    spend_data = []
    for yr_row in GOOGLE_DC_ELECTRICITY.itertuples():
        spend_data.append({
            "Year": str(yr_row.year), "Company": "Google",
            "Spend": yr_row.dc_mwh * 1e3 * dc_rate / 1e9,
        })
    for yr_row in META_DC_ELECTRICITY.itertuples():
        spend_data.append({
            "Year": str(yr_row.year), "Company": "Meta",
            "Spend": yr_row.dc_mwh * 1e3 * dc_rate / 1e9,
        })
    spend_df = pd.DataFrame(spend_data)

    spend_chart = (
        alt.Chart(spend_df)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y("Spend:Q", title="Estimated Spend ($ Billions)"),
            color=alt.Color("Company:N",
                scale=alt.Scale(domain=["Google", "Meta"],
                                range=["#34a853", "#0866ff"]),
                legend=alt.Legend(title="")),
            tooltip=["Company:N", "Year:O",
                     alt.Tooltip("Spend:Q", format="$.2f",
                                 title="Est. Spend ($B)")],
        ).properties(height=260)
    )
    st.altair_chart(spend_chart, use_container_width=True)

    st.caption(
        f"At **\\${dc_rate:.3f}/kWh**, the four hyperscalers' combined estimated "
        f"electricity spend is **\\${all_spend / 1e9:.1f}B/year** on "
        f"**{all_twh:.0f} TWh** — roughly "
        f"**{all_equiv_homes / 1e6:.1f} million U.S. households** of consumption. "
        f"You pay **{rate_ratio:.1f}× more per kWh** than they do. "
        "These are estimates — actual rates are negotiated confidentially and "
        "filed under seal with state PUCs; no hyperscaler discloses utility spend. "
        "The chart shows Google and Meta only (the two that publish multi-year "
        "electricity series)."
    )
    st.info(
        "**Why does this matter?** Large data centers often negotiate rates 60–80% "
        "below what residential customers pay, plus tax abatements and infrastructure "
        "subsidies. When their load raises system peak demand, the resulting capacity "
        "charges are spread across *all* ratepayers. Your bill subsidizes their discount. "
        "Use the **Your Utility Bill** tab to see exactly how this works."
    )

    _spend_summary = (
        f"Estimated Hyperscaler Electricity Spend (at ${dc_rate:.3f}/kWh)\n\n"
        f"Google (FY2025): {g_twh} TWh → ${g_spend/1e9:.1f}B/year\n"
        f"AWS (CY2025, est.): {aw_twh} TWh → ${aw_spend/1e9:.1f}B/year\n"
        f"Microsoft (FY2025, est.): {ms_twh} TWh → ${ms_spend/1e9:.1f}B/year\n"
        f"Meta (FY2024): {m_twh} TWh → ${m_spend/1e9:.1f}B/year\n"
        f"Combined: {all_twh:.0f} TWh → ${all_spend/1e9:.1f}B/year\n"
        f"Rate discount vs residential (${res_rate:.2f}/kWh): {rate_ratio:.1f}x\n"
        f"Household equivalent: {all_equiv_homes/1e6:.1f}M homes\n\n"
        "Note: These are estimates. Actual rates are negotiated confidentially. "
        "Microsoft/AWS TWh derived from reported growth rates."
    )
    st.download_button(
        "📥 Download spend estimate (text)",
        _spend_summary, "electricity_spend_estimate.txt", "text/plain",
        use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)

    # -- Collapsible: company PR links (preserved) ------------------------- #
    with st.expander("📄 Company reports & community pledge pages"):
        st.caption(
            "First-party material — economic-impact reports, community pledges "
            "and newsrooms the operators themselves publish. Read these as the "
            "company's side of the story."
        )
        cats = {}
        for cat, company, what, url in COMPANY_STATEMENTS:
            cats.setdefault(cat, []).append((company, what, url))
        for cat, entries in cats.items():
            st.markdown(f"**{cat}**")
            comp_cols = st.columns(3)
            for i, (company, what, url) in enumerate(entries):
                with comp_cols[i % 3]:
                    st.markdown(f"**{company}** — [{what}]({url})")

    st.markdown("###### 📣 Live press releases & news")
    st.caption("Fresh Google News hits for a given operator — their own "
               "announcements plus third-party coverage, newest first. No key "
               "required; headlines are unfiltered, not endorsements.")
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    pick = st.selectbox("Operator", ["All operators"]
                        + list(COMPANY_FEED_TERMS.keys()))
    if pick == "All operators":
        pr_query = ("(" + " OR ".join(COMPANY_FEED_TERMS.values()) + ") "
                    "data center (community OR jobs OR investment OR ratepayers "
                    "OR water OR moratorium)")
    else:
        pr_query = (COMPANY_FEED_TERMS[pick]
                    + " data center (community OR jobs OR investment OR "
                    "ratepayers OR water OR moratorium)")
    pr_items, pr_err = fetch_news(pr_query, limit=12)
    if pr_err or pr_items is None:
        gn_url = ("https://news.google.com/search?q="
                  + urllib.parse.quote(pr_query))
        st.warning("Couldn't reach Google News right now — "
                   f"[open this search]({gn_url}).")
    elif not pr_items:
        st.info("No recent items for this operator — try another.")
    else:
        st.caption(f"{len(pr_items)} items • newest first")
        for it in pr_items:
            meta = " · ".join(x for x in (it["source"], it["published"]) if x)
            st.markdown(f"- [{it['title']}]({it['link']})  \n"
                        f"  <small style='color:#9CA6B6'>{meta}</small>",
                        unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Moratorium & ban tracker")
    st.caption("Towns, counties and states that have paused or blocked data "
               "centers. Point-in-time snapshot (mid-2026) compiled from public "
               "trackers — dozens more churn weekly, so follow the links below "
               "for live status. Not exhaustive.")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    enacted = MORATORIUMS_DF[MORATORIUMS_DF.status == "Enacted"]
    proposed = MORATORIUMS_DF[MORATORIUMS_DF.status == "Proposed"]
    q1, q2, q3 = st.columns(3)
    q1.metric("Enacted (listed)", f"{len(enacted)}")
    q2.metric("Proposed / considering", f"{len(proposed)}")
    q3.metric("States represented", f"{MORATORIUMS_DF.state.nunique()}")
    st.caption("Trackers report **50+ localities enacted** nationally (North "
               "Carolina alone has 20+); the table lists a representative subset.")

    _fc1, _fc2 = st.columns(2)
    with _fc1:
        fstat = st.multiselect(
            "Filter by status",
            list(MORATORIUMS_DF.status.unique()),
            default=["Enacted", "Proposed"])
    with _fc2:
        _sidebar_abbrev = st.session_state.get("my_state_abbrev", "")
        _mora_states = sorted(MORATORIUMS_DF.state.unique())
        _mora_st_default = [_sidebar_abbrev] if _sidebar_abbrev and _sidebar_abbrev in _mora_states else []
        fstate_mora = st.multiselect(
            "Filter by state",
            _mora_states, default=_mora_st_default,
            key="mora_state_filter",
            placeholder="All states")
    mdf = MORATORIUMS_DF.copy()
    if fstat:
        mdf = mdf[mdf.status.isin(fstat)]
    if fstate_mora:
        mdf = mdf[mdf.state.isin(fstate_mora)]

    STATUS_COLORS = {"Enacted": [215, 48, 39], "Proposed": [253, 174, 97],
                     "Rejected": [154, 160, 166], "Vetoed": [154, 160, 166]}
    geo = mdf.dropna(subset=["lat", "lon"]).copy()
    if not geo.empty:
        geo["color"] = geo["status"].map(STATUS_COLORS).apply(
            lambda c: c if isinstance(c, list) else [154, 160, 166])
        geo["label"] = (geo["locality"] + ", " + geo["state"]
                        + " — " + geo["status"]
                        + geo["when"].apply(lambda w: f" ({w})" if w else "")
                        + geo["note"].apply(lambda n: f"\n{n}" if n else ""))
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=geo,
            get_position=["lon", "lat"],
            get_fill_color="color",
            get_radius=18000,
            pickable=True,
            auto_highlight=True,
            highlight_color=[255, 255, 255, 80],
        )
        view = pdk.ViewState(latitude=38.5, longitude=-96.0, zoom=3.4, pitch=0)
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view,
            tooltip={"text": "{label}"},
            map_style="mapbox://styles/mapbox/dark-v11",
        )
        st.pydeck_chart(deck, use_container_width=True)
        st.caption("🔴 Enacted · 🟠 Proposed · ⚪ Rejected/Vetoed. **Hover or "
                   "click** a point to see details. Statewide actions aren't "
                   "mapped. Zoom to see the North Carolina cluster.")

    tcol, ccol = st.columns([3, 2])
    with tcol:
        st.dataframe(
            mdf[["locality", "state", "level", "status", "when", "note"]],
            use_container_width=True, hide_index=True, height=360,
            column_config={"locality": "Locality", "state": "State",
                           "level": "Level", "status": "Status",
                           "when": "When", "note": "Note"})
    with ccol:
        by_state = (mdf.groupby("state").size().reset_index(name="n")
                    .sort_values("n", ascending=False))
        chart = (alt.Chart(by_state).mark_bar().encode(
            x=alt.X("n:Q", title="Localities / actions"),
            y=alt.Y("state:N", sort="-x", title=None),
            tooltip=["state", "n"],
            color=alt.Color("n:Q", scale=alt.Scale(scheme="reds"), legend=None),
        ).properties(height=360))
        st.altair_chart(chart, use_container_width=True)

    st.caption("Trackers: " + " · ".join(
        src_link(k) for k in ["icap_mor", "dcbans", "dcopp", "dcwatch", "dcresp",
                               "dctrack", "gjf_mor", "rockinst"]))

    _mora_csv = mdf.to_csv(index=False)
    st.download_button(
        "📥 Download moratorium data (CSV)",
        _mora_csv, "moratorium_tracker.csv", "text/csv",
        use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)

    # Before / after: what actually happened
    st.markdown("#### What happened next? Case study outcomes")
    st.caption(
        "Moratoriums are the opening move, not the end. These cases show what "
        "communities actually got — or lost — depending on how they played their hand.")

    _cat_icons = {
        "CBA secured": "🟢", "Ban sustained": "🔵",
        "No protections": "🔴", "Political shift": "🟠",
    }
    for cs in MORATORIUM_OUTCOMES:
        _icon = _cat_icons.get(cs["category"], "⚪")
        with st.expander(f"{_icon} {cs['locality']}, {cs['state']} — {cs['headline']}"):
            st.markdown(cs["outcome"])
            st.caption(f"Category: **{cs['category']}**")

    st.divider()
    st.markdown("#### Live discussion")
    st.info("📰 The live news + Reddit feed and the automatically ranked **top "
            "stories of the week** now live in their own **📰 News** tab "
            "(in the main tab bar). This tab keeps the trackers, case studies, "
            "and scorecards.")
    st.markdown('</div>', unsafe_allow_html=True)
