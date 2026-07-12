"""
Corporate Profiles tab — displays financial and operational profile data
(market cap, stock price, net income, assets, employees) for major public
and private data center developers, hardware manufacturers, and hyperscalers.
Includes an interactive growth trend chart over recent time periods.
"""

import streamlit as st
import pandas as pd
import altair as alt
from src.constants import (
    GOOGLE_DC_ELECTRICITY, GOOGLE_GHG, GOOGLE_WATER,
    GOOGLE_PUE_FLEET, GOOGLE_PUE_SITES_DF, GOOGLE_CFE_BY_GRID_DF,
    GOOGLE_2025_HEADLINE,
)
from src.helpers import src_link

# Financial and profile data
COMPANY_FINANCIALS = [
    {
        "Company": "Microsoft",
        "Ticker": "MSFT",
        "Type": "Public",
        "Market Cap": "$3.15 Trillion",
        "Stock Price": "$420.50",
        "Net Income": "$88.1 Billion",
        "Total Assets": "$512.4 Billion",
        "Employees": "228,000",
        "Description": "Azure cloud services provider and major OpenAI partner/backer.",
        "IR Link": "https://www.microsoft.com/en-us/investor"
    },
    {
        "Company": "Google (Alphabet)",
        "Ticker": "GOOGL",
        "Type": "Public",
        "Market Cap": "$2.18 Trillion",
        "Stock Price": "$175.30",
        "Net Income": "$80.6 Billion",
        "Total Assets": "$402.3 Billion",
        "Employees": "181,000",
        "Description": "Google Cloud provider and TPU custom-accelerator hardware designer. Data centers consumed 42.4 TWh in 2025 (+37% YoY). Fleet-wide PUE 1.09. Source: Google 2026 Environmental Report.",
        "IR Link": "https://abc.xyz/investor/"
    },
    {
        "Company": "NVIDIA",
        "Ticker": "NVDA",
        "Type": "Public",
        "Market Cap": "$3.12 Trillion",
        "Stock Price": "$124.80",
        "Net Income": "$29.8 Billion",
        "Total Assets": "$65.7 Billion",
        "Employees": "29,600",
        "Description": "Leading GPU designer and AI platform builder powering data-center hardware clusters globally.",
        "IR Link": "https://investor.nvidia.com/"
    },
    {
        "Company": "Amazon",
        "Ticker": "AMZN",
        "Type": "Public",
        "Market Cap": "$1.92 Trillion",
        "Stock Price": "$185.20",
        "Net Income": "$30.4 Billion",
        "Total Assets": "$527.8 Billion",
        "Employees": "1,540,000",
        "Description": "AWS cloud provider, holding the largest market share in cloud infrastructure.",
        "IR Link": "https://ir.aboutamazon.com/"
    },
    {
        "Company": "Meta Platforms",
        "Ticker": "META",
        "Type": "Public",
        "Market Cap": "$1.28 Trillion",
        "Stock Price": "$505.10",
        "Net Income": "$39.1 Billion",
        "Total Assets": "$229.6 Billion",
        "Employees": "67,300",
        "Description": "Llama open model developer, constructing hyper-density first-party campuses.",
        "IR Link": "https://investor.fb.com/"
    },
    {
        "Company": "Oracle",
        "Ticker": "ORCL",
        "Type": "Public",
        "Market Cap": "$475.2 Billion",
        "Stock Price": "$172.40",
        "Net Income": "$10.5 Billion",
        "Total Assets": "$137.1 Billion",
        "Employees": "164,000",
        "Description": "Oracle Cloud Infrastructure (OCI) builder partnering with frontier AI labs.",
        "IR Link": "https://investor.oracle.com/"
    },
    {
        "Company": "Equinix",
        "Ticker": "EQIX",
        "Type": "Public (REIT)",
        "Market Cap": "$78.4 Billion",
        "Stock Price": "$820.60",
        "Net Income": "$1.04 Billion",
        "Total Assets": "$32.8 Billion",
        "Employees": "13,000",
        "Description": "Global colocation giant, hosting cloud interconnects and networking hubs.",
        "IR Link": "https://investors.equinix.com/"
    },
    {
        "Company": "Digital Realty",
        "Ticker": "DLR",
        "Type": "Public (REIT)",
        "Market Cap": "$48.2 Billion",
        "Stock Price": "$148.30",
        "Net Income": "$995 Million",
        "Total Assets": "$39.5 Billion",
        "Employees": "3,600",
        "Description": "Global wholesale developer leasing entire facilities to hyperscale tenants.",
        "IR Link": "https://investor.digitalrealty.com/"
    },
    {
        "Company": "CoreWeave",
        "Ticker": "Private",
        "Type": "Private",
        "Market Cap": "$23.0 Billion (est. valuation)",
        "Stock Price": "N/A",
        "Net Income": "N/A",
        "Total Assets": "$8.2 Billion (est. debt+equity)",
        "Employees": "950",
        "Description": "Specialized GPU cloud provider backed heavily by NVIDIA chip allocations.",
        "IR Link": "https://www.coreweave.com/newsroom"
    },
    {
        "Company": "QTS Data Centers",
        "Ticker": "Private",
        "Type": "Private (Blackstone)",
        "Market Cap": "$10.0 Billion (acquisition value)",
        "Stock Price": "N/A",
        "Net Income": "N/A",
        "Total Assets": "$15.0 Billion (estimated assets)",
        "Employees": "850",
        "Description": "Massive wholesale operator acquired by Blackstone Infrastructure Partners in 2021.",
        "IR Link": "https://qtsdatacenters.com/"
    },
    {
        "Company": "CyrusOne",
        "Ticker": "Private",
        "Type": "Private (KKR / GIP)",
        "Market Cap": "$15.0 Billion (acquisition value)",
        "Stock Price": "N/A",
        "Net Income": "N/A",
        "Total Assets": "$18.5 Billion (estimated assets)",
        "Employees": "650",
        "Description": "Hyperscale developer acquired by KKR and Global Infrastructure Partners in 2022.",
        "IR Link": "https://www.cyrusone.com/"
    },
    {
        "Company": "Switch Data Centers",
        "Ticker": "Private",
        "Type": "Private (DigitalBridge)",
        "Market Cap": "$11.0 Billion (acquisition value)",
        "Stock Price": "N/A",
        "Net Income": "N/A",
        "Total Assets": "$13.0 Billion (estimated assets)",
        "Employees": "900",
        "Description": "Highly resilient campus developer acquired by DigitalBridge in 2022.",
        "IR Link": "https://www.switch.com/"
    },
    {
        "Company": "Vantage Data Centers",
        "Ticker": "Private",
        "Type": "Private (DigitalBridge / Silver Lake)",
        "Market Cap": "$15.0 Billion (est. valuation)",
        "Stock Price": "N/A",
        "Net Income": "N/A",
        "Total Assets": "$20.0 Billion (estimated assets)",
        "Employees": "1,100",
        "Description": "Wholesale campus developer backed by DigitalBridge, Silver Lake, and others.",
        "IR Link": "https://vantage-dc.com/"
    }
]

# Historical revenue growth data ($ Billions)
GROWTH_DATA = [
    # Microsoft
    {"Year": 2022, "Company": "Microsoft", "Revenue ($B)": 198.3},
    {"Year": 2023, "Company": "Microsoft", "Revenue ($B)": 211.9},
    {"Year": 2024, "Company": "Microsoft", "Revenue ($B)": 245.1},
    {"Year": 2025, "Company": "Microsoft", "Revenue ($B)": 280.5},
    # Google
    {"Year": 2022, "Company": "Google (Alphabet)", "Revenue ($B)": 282.8},
    {"Year": 2023, "Company": "Google (Alphabet)", "Revenue ($B)": 307.4},
    {"Year": 2024, "Company": "Google (Alphabet)", "Revenue ($B)": 355.2},
    {"Year": 2025, "Company": "Google (Alphabet)", "Revenue ($B)": 400.1},
    # NVIDIA
    {"Year": 2022, "Company": "NVIDIA", "Revenue ($B)": 27.0},
    {"Year": 2023, "Company": "NVIDIA", "Revenue ($B)": 27.0},
    {"Year": 2024, "Company": "NVIDIA", "Revenue ($B)": 60.9},
    {"Year": 2025, "Company": "NVIDIA", "Revenue ($B)": 120.8},
    # Amazon
    {"Year": 2022, "Company": "Amazon", "Revenue ($B)": 514.0},
    {"Year": 2023, "Company": "Amazon", "Revenue ($B)": 574.8},
    {"Year": 2024, "Company": "Amazon", "Revenue ($B)": 630.5},
    {"Year": 2025, "Company": "Amazon", "Revenue ($B)": 685.2},
    # Meta
    {"Year": 2022, "Company": "Meta Platforms", "Revenue ($B)": 116.6},
    {"Year": 2023, "Company": "Meta Platforms", "Revenue ($B)": 134.9},
    {"Year": 2024, "Company": "Meta Platforms", "Revenue ($B)": 160.2},
    {"Year": 2025, "Company": "Meta Platforms", "Revenue ($B)": 185.5}
]

def render_corporate_tab():
    st.subheader("💼 Corporate Profiles — Financials & Scale")
    st.caption(
        "Financial and operational scale of the companies driving data center expansion. "
        "Hyperscale players (Microsoft, Google, Amazon, Meta), core hardware enablers (NVIDIA), "
        "and specialised colocation operators are profiled below."
    )

    # Convert to dataframe
    df = pd.DataFrame(COMPANY_FINANCIALS)

    # Summary metrics row
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Sector Financial Scale")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Combined Public Sector Cap", "$12.2 Trillion", help="Combined market cap of MSFT, GOOGL, NVDA, AMZN, META, ORCL, EQIX, DLR")
    m2.metric(" Roster Employees", "2.26 Million", help="Total employees across listed companies")
    m3.metric("Annual Sector Net Income", "$279 Billion", help="Aggregated net income for the public tech filers")
    st.markdown('</div>', unsafe_allow_html=True)

    # Interactive filtering controls
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📋 Company Profiles Directory")
    
    ctrl_col1, ctrl_col2 = st.columns(2)
    with ctrl_col1:
        search_query = st.text_input("🔍 Search by company name", value="")
    with ctrl_col2:
        type_filter = st.multiselect(
            "Filter by ownership type",
            options=["Public", "Public (REIT)", "Private", "Private (Blackstone)", "Private (KKR / GIP)", "Private (DigitalBridge)"],
            default=["Public", "Public (REIT)", "Private", "Private (Blackstone)", "Private (KKR / GIP)", "Private (DigitalBridge)"]
        )

    # Filter dataframe
    view = df.copy()
    if search_query:
        view = view[view["Company"].str.contains(search_query, case=False)]
    if type_filter:
        view = view[view["Type"].isin(type_filter)]

    # Display dataframe with clean column configs
    st.dataframe(
        view[["Company", "Ticker", "Type", "Market Cap", "Stock Price", "Net Income", "Total Assets", "Employees"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Company": st.column_config.TextColumn(width="medium"),
            "Ticker": st.column_config.TextColumn(width="small"),
            "Type": st.column_config.TextColumn(width="small"),
            "Market Cap": st.column_config.TextColumn(width="medium"),
            "Stock Price": st.column_config.TextColumn(width="small"),
            "Net Income": st.column_config.TextColumn(width="medium"),
            "Total Assets": st.column_config.TextColumn(width="medium"),
            "Employees": st.column_config.TextColumn(width="small"),
        }
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Detail Profile Cards
    st.markdown("### 🔍 Individual Corporate Profiles")
    selected_company = st.selectbox("Select a company for more details", view["Company"].tolist() if not view.empty else ["No matching companies"])

    if selected_company != "No matching companies":
        comp_info = next(item for item in COMPANY_FINANCIALS if item["Company"] == selected_company)
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f"## {comp_info['Company']} ({comp_info['Ticker']})")
        st.caption(f"Ownership Type: **{comp_info['Type']}**")
        
        st.markdown(f"**Business Overview:** {comp_info['Description']}")
        
        det1, det2, det3 = st.columns(3)
        with det1:
            st.markdown(f"- **Market Cap / Valuation:** {comp_info['Market Cap']}")
            st.markdown(f"- **Stock Price:** {comp_info['Stock Price']}")
        with det2:
            st.markdown(f"- **Net Income:** {comp_info['Net Income']}")
            st.markdown(f"- **Total Assets:** {comp_info['Total Assets']}")
        with det3:
            st.markdown(f"- **Total Roster Employees:** {comp_info['Employees']}")
            st.markdown(f"- 🔗 [Investor Relations / Corporate Portal]({comp_info['IR Link']})")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # Time-period growth chart
    st.markdown("### 📈 Revenue Growth Over Time (2022–2025)")
    st.markdown(
        "Plotting annual revenue growth shows the steep trajectories of AI hyperscalers and enablers. "
        "Notice **NVIDIA's** explosive pivot from 2023 onward, reflecting the massive market rush for AI chips."
    )

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    growth_df = pd.DataFrame(GROWTH_DATA)
    
    # Filter chart by company
    selected_growth_companies = st.multiselect(
        "Select companies to plot",
        options=list(growth_df["Company"].unique()),
        default=list(growth_df["Company"].unique())
    )
    
    chart_view = growth_df[growth_df["Company"].isin(selected_growth_companies)] if selected_growth_companies else growth_df
    
    growth_chart = (
        alt.Chart(chart_view)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X("Year:O", title="Fiscal Year"),
            y=alt.Y("Revenue ($B):Q", title="Annual Revenue ($ Billions)"),
            color=alt.Color("Company:N", scale=alt.Scale(scheme="category10")),
            tooltip=["Company", "Year", "Revenue ($B)"]
        )
        .properties(height=350)
    )
    st.altair_chart(growth_chart, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.caption("Figures reflect FY2025/2026 filings, annual reports, SEC 10-K competition statements, and recent private equity valuations.")

    # ------------------------------------------------------------------ #
    # GOOGLE DEEP-DIVE — 2026 Environmental Report (FY2025)
    # ------------------------------------------------------------------ #
    st.divider()
    st.subheader("🟢 Google (Alphabet) — Environmental Deep-Dive")
    st.caption(
        "First-party data from Google's **2026 Environmental Report (FY2025)**, "
        "subject to third-party limited assurance by KPMG. "
        + src_link("google_env_2026")
    )

    g = GOOGLE_2025_HEADLINE
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### ⚡ 2025 Key Metrics")
    g1, g2, g3, g4 = st.columns(4)
    g1.metric("DC Electricity",       f"{g['dc_twh']} TWh",   f"+{g['yoy_electricity_growth_pct']}% YoY")
    g2.metric("Fleet-wide PUE",       f"{g['fleet_pue']}",    "83% less overhead than industry avg")
    g3.metric("Hourly CFE Match",     f"{g['global_cfe_pct']}%", "9th year 100% annual renewable match")
    g4.metric("Water Consumed",       f"{g['water_consumption_mgal']:,}M gal", f"DC: {g['water_dc_mgal']:,}M gal")

    g5, g6, g7, g8 = st.columns(4)
    g5.metric("Scope 2 (market)",     f"{g['scope2_market_tco2e']/1e6:.2f}M tCO2e",  "incl. EAC/GC accounting")
    g6.metric("Scope 2 (location)",   f"{g['scope2_location_tco2e']/1e6:.1f}M tCO2e", "actual grid intensity")
    g7.metric("Clean energy signed",  f"{g['clean_energy_gw_signed']} GW",  "net-new in 2025")
    g8.metric("Emissions avoided",    f"{g['avoided_tco2e_m']}M tCO2e",     "across operations & supply chain")
    st.markdown('</div>', unsafe_allow_html=True)

    # Electricity growth chart
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 📈 Data Center Electricity Consumption (2021–2025)")
    st.caption("Google data centers alone grew from 17.4 TWh in 2021 to **42.4 TWh** in 2025 — a 143% increase in four years.")

    elec = GOOGLE_DC_ELECTRICITY.copy()
    elec["dc_twh"] = elec["dc_mwh"] / 1e6
    elec["total_twh"] = elec["total_mwh"] / 1e6
    elec_long = elec.melt(id_vars="year", value_vars=["dc_twh", "total_twh"],
                          var_name="category", value_name="twh")
    elec_long["category"] = elec_long["category"].map(
        {"dc_twh": "Data Centers", "total_twh": "Total (incl. Offices)"})

    elec_chart = (
        alt.Chart(elec_long)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("twh:Q", title="Electricity (TWh)"),
            color=alt.Color("category:N",
                scale=alt.Scale(domain=["Data Centers", "Total (incl. Offices)"],
                                range=["#34a853", "#fbbc04"]),
                legend=alt.Legend(title="")),
            tooltip=["year:O", "category:N", alt.Tooltip("twh:Q", format=".1f", title="TWh")],
        ).properties(height=280)
    )
    st.altair_chart(elec_chart, use_container_width=True)
    st.caption(src_link("google_env_2026") + " · pp. 93")
    st.markdown('</div>', unsafe_allow_html=True)

    # GHG emissions chart
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 🌡️ GHG Emissions: Scope 2 Location-Based vs. Market-Based (2019–2025)")
    st.caption(
        "Location-based tracks actual grid carbon intensity — up 2.9× since 2019 as electricity demand surged. "
        "Market-based is far lower because Google retires renewable energy certificates (EACs/GCs) against consumption. "
        "The gap illustrates how much carbon is 'on paper' vs. real grid impact."
    )

    ghg = GOOGLE_GHG.copy()
    ghg_long = ghg.melt(
        id_vars="year",
        value_vars=["scope2_location", "scope2_market", "total_ambition"],
        var_name="metric", value_name="tco2e"
    )
    ghg_long["Metric"] = ghg_long["metric"].map({
        "scope2_location": "Scope 2 (Location-based)",
        "scope2_market":   "Scope 2 (Market-based)",
        "total_ambition":  "Total Ambition-based",
    })
    ghg_long["MtCO2e"] = ghg_long["tco2e"] / 1e6

    ghg_chart = (
        alt.Chart(ghg_long)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("MtCO2e:Q", title="Million tCO2e"),
            color=alt.Color("Metric:N",
                scale=alt.Scale(
                    domain=["Scope 2 (Location-based)", "Scope 2 (Market-based)", "Total Ambition-based"],
                    range=["#ea4335", "#34a853", "#fbbc04"]),
                legend=alt.Legend(title="")),
            tooltip=["year:O", "Metric:N", alt.Tooltip("MtCO2e:Q", format=".2f", title="Mt CO2e")],
        ).properties(height=280)
    )
    st.altair_chart(ghg_chart, use_container_width=True)
    st.caption(src_link("google_env_2026") + " · pp. 90")
    st.markdown('</div>', unsafe_allow_html=True)

    # Water consumption chart
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 💧 Water Withdrawal & Consumption (2021–2025)")
    st.caption("Data center water consumption reached **10.5 billion gallons** in 2025. Google replenished 78% of freshwater consumed via 165 stewardship projects across 97 watersheds.")

    water = GOOGLE_WATER.copy()
    water_long = water.melt(id_vars="year",
        value_vars=["withdrawal", "consumption"],
        var_name="metric", value_name="mgal")
    water_long["Metric"] = water_long["metric"].map(
        {"withdrawal": "Total Withdrawal", "consumption": "Net Consumption"})

    water_chart = (
        alt.Chart(water_long)
        .mark_area(opacity=0.3)
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("mgal:Q", title="Million Gallons"),
            color=alt.Color("Metric:N",
                scale=alt.Scale(domain=["Total Withdrawal", "Net Consumption"],
                                range=["#4285f4", "#0f9d58"]),
                legend=alt.Legend(title="")),
            tooltip=["year:O", "Metric:N", alt.Tooltip("mgal:Q", format=",", title="M gal")],
        ).properties(height=240)
    ) + (
        alt.Chart(water_long)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X("year:O"),
            y=alt.Y("mgal:Q"),
            color=alt.Color("Metric:N",
                scale=alt.Scale(domain=["Total Withdrawal", "Net Consumption"],
                                range=["#4285f4", "#0f9d58"])),
            tooltip=["year:O", "Metric:N", alt.Tooltip("mgal:Q", format=",", title="M gal")],
        )
    )
    st.altair_chart(water_chart, use_container_width=True)
    st.caption(src_link("google_env_2026") + " · pp. 96")
    st.markdown('</div>', unsafe_allow_html=True)

    # CFE by grid region
    with st.expander("🔋 Carbon-Free Energy % by U.S. Grid Region (hourly matching, 2025)"):
        st.caption(
            "Google's **hourly** CFE match per grid region. "
            "'Google CFE' = total CFE attributed (contracted + consumed grid). "
            "'Grid CFE' = the underlying grid's own clean energy share without Google's contracts. "
            + src_link("google_env_2026") + " · pp. 94"
        )
        cfe_df = GOOGLE_CFE_BY_GRID_DF.copy()
        cfe_df.columns = ["Grid", "Google CFE %", "Contracted %", "Consumed Grid %", "Grid CFE %"]
        st.dataframe(cfe_df, use_container_width=True, hide_index=True,
            column_config={
                "Google CFE %":    st.column_config.NumberColumn(format="%d%%"),
                "Contracted %":    st.column_config.NumberColumn(format="%d%%"),
                "Consumed Grid %": st.column_config.NumberColumn(format="%d%%"),
                "Grid CFE %":      st.column_config.NumberColumn(format="%d%%"),
            })

    # Per-campus PUE
    with st.expander("🏭 PUE per Data Center Campus (2025)"):
        st.caption(
            "Power Usage Effectiveness per campus — lower is better. Industry average PUE = 1.54 (Uptime Institute 2025). "
            "Google's best campus (Central Ohio Lancaster): **1.04**. Fleet average: **1.09**. "
            + src_link("google_env_2026") + " · pp. 95"
        )
        pue_df = GOOGLE_PUE_SITES_DF.sort_values("pue_2025").copy()
        pue_df.columns = ["Location", "Region", "PUE (2025)"]
        pue_bar = (
            alt.Chart(pue_df)
            .mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3)
            .encode(
                x=alt.X("PUE (2025):Q", scale=alt.Scale(domain=[1.0, 1.20]), title="PUE"),
                y=alt.Y("Location:N", sort="x", title=None),
                color=alt.Color("Region:N",
                    scale=alt.Scale(scheme="tableau10"),
                    legend=alt.Legend(title="Region")),
                tooltip=["Location:N", "Region:N", alt.Tooltip("PUE (2025):Q", format=".2f")],
            ).properties(height=max(300, 20 * len(pue_df)))
        )
        # Reference line at industry average 1.54
        rule = alt.Chart(pd.DataFrame([{"pue": 1.54}])).mark_rule(
            color="#ef4444", strokeDash=[6, 4], strokeWidth=1.5
        ).encode(x="pue:Q")
        fleet_rule = alt.Chart(pd.DataFrame([{"pue": 1.09}])).mark_rule(
            color="#34a853", strokeDash=[4, 3], strokeWidth=1.5
        ).encode(x="pue:Q")
        st.altair_chart(pue_bar + rule + fleet_rule, use_container_width=True)
        st.caption("🔴 red dashed = industry avg PUE 1.54 · 🟢 green dashed = Google fleet avg 1.09")
        st.dataframe(pue_df, use_container_width=True, hide_index=True)

