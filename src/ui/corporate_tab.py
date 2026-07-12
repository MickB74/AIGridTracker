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
    META_DC_ELECTRICITY, META_DC_CAMPUS_ELECTRICITY, META_GHG,
    META_WATER, META_EFFICIENCY, META_2024_HEADLINE,
)
from src.helpers import src_link
from src.services.sec_xbrl import fetch_dynamic_financials

# Financial and profile data
COMPANY_FINANCIALS = [
    {
        "Company": "Microsoft",
        "Ticker": "MSFT",
        "Type": "Public",
        "Market Cap": "$3.15 Trillion",
        "Stock Price": "$420.50",
        "Capital Budget (Annual CapEx)": "$55.7 Billion",
        "Net Income": "$88.1 Billion",
        "Total Assets": "$512.4 Billion",
        "Employees": "228,000",
        "Description": "Azure cloud services provider, chief developer of Copilot services, and major OpenAI partner/backer.",
        "IR Link": "https://www.microsoft.com/en-us/investor"
    },
    {
        "Company": "Google (Alphabet)",
        "Ticker": "GOOGL",
        "Type": "Public",
        "Market Cap": "$2.18 Trillion",
        "Stock Price": "$175.30",
        "Capital Budget (Annual CapEx)": "$51.4 Billion",
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
        "Capital Budget (Annual CapEx)": "$1.5 Billion",
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
        "Capital Budget (Annual CapEx)": "$75.0 Billion",
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
        "Capital Budget (Annual CapEx)": "$38.5 Billion",
        "Net Income": "$39.1 Billion",
        "Total Assets": "$229.6 Billion",
        "Employees": "67,300",
        "Description": "Llama open model developer, constructing hyper-density first-party campuses.",
        "IR Link": "https://investor.fb.com/"
    },
    {
        "Company": "AMD",
        "Ticker": "AMD",
        "Type": "Public",
        "Market Cap": "$282.4 Billion",
        "Stock Price": "$174.50",
        "Capital Budget (Annual CapEx)": "$0.5 Billion",
        "Net Income": "$1.8 Billion",
        "Total Assets": "$68.2 Billion",
        "Employees": "26,000",
        "Description": "Leading GPU designer (Instinct MI300 and MI325 series) competing with NVIDIA in AI accelerators.",
        "IR Link": "https://ir.amd.com/"
    },
    {
        "Company": "Vertiv Holdings",
        "Ticker": "VRT",
        "Type": "Public",
        "Market Cap": "$38.2 Billion",
        "Stock Price": "$101.50",
        "Capital Budget (Annual CapEx)": "$0.2 Billion",
        "Net Income": "$460 Million",
        "Total Assets": "$6.8 Billion",
        "Employees": "27,000",
        "Description": "Global leader in datacenter power management, heat exchangers, and liquid/thermal cooling systems.",
        "IR Link": "https://investors.vertiv.com/"
    },
    {
        "Company": "Constellation Energy",
        "Ticker": "CEG",
        "Type": "Public",
        "Market Cap": "$80.5 Billion",
        "Stock Price": "$251.38",
        "Capital Budget (Annual CapEx)": "$2.2 Billion",
        "Net Income": "$3.8 Billion",
        "Total Assets": "$45.3 Billion",
        "Employees": "15,300",
        "Description": "Largest U.S. nuclear operator; signed the 835 MW Three Mile Island restart deal to power Microsoft AI datacenters.",
        "IR Link": "https://investors.constellationenergy.com/"
    },
    {
        "Company": "Super Micro Computer",
        "Ticker": "SMCI",
        "Type": "Public",
        "Market Cap": "$18.3 Billion",
        "Stock Price": "$32.50",
        "Capital Budget (Annual CapEx)": "$0.2 Billion",
        "Net Income": "$1.2 Billion",
        "Total Assets": "$8.5 Billion",
        "Employees": "5,200",
        "Description": "Builds high-density GPU server racks and liquid-cooling manifolds for hyperscale datacenters.",
        "IR Link": "https://ir.supermicro.com/"
    },
    {
        "Company": "Oracle",
        "Ticker": "ORCL",
        "Type": "Public",
        "Market Cap": "$475.2 Billion",
        "Stock Price": "$172.40",
        "Capital Budget (Annual CapEx)": "$8.5 Billion",
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
        "Capital Budget (Annual CapEx)": "$3.0 Billion",
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
        "Capital Budget (Annual CapEx)": "$2.5 Billion",
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
        "Capital Budget (Annual CapEx)": "$12.0 Billion",
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
        "Capital Budget (Annual CapEx)": "$8.0 Billion",
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
        "Capital Budget (Annual CapEx)": "$6.5 Billion",
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
        "Capital Budget (Annual CapEx)": "$3.5 Billion",
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
        "Capital Budget (Annual CapEx)": "$7.0 Billion",
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

    # Convert to dataframe and merge SEC XBRL data where available
    live_financials = []
    for item in COMPANY_FINANCIALS:
        ticker = item["Ticker"]
        updated_item = item.copy()
        if ticker != "Private":
            sec_data = fetch_dynamic_financials(ticker)
            if sec_data:
                if "Net Income" in sec_data:
                    updated_item["Net Income"] = sec_data["Net Income"]
                if "Capital Budget (Annual CapEx)" in sec_data:
                    updated_item["Capital Budget (Annual CapEx)"] = sec_data["Capital Budget (Annual CapEx)"]
                if "Total Assets" in sec_data:
                    updated_item["Total Assets"] = sec_data["Total Assets"]
        live_financials.append(updated_item)

    df = pd.DataFrame(live_financials)

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
        view[["Company", "Ticker", "Type", "Market Cap", "Stock Price", "Capital Budget (Annual CapEx)", "Net Income", "Total Assets", "Employees"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Company": st.column_config.TextColumn(width="medium"),
            "Ticker": st.column_config.TextColumn(width="small"),
            "Type": st.column_config.TextColumn(width="small"),
            "Market Cap": st.column_config.TextColumn(width="medium"),
            "Stock Price": st.column_config.TextColumn(width="small"),
            "Capital Budget (Annual CapEx)": st.column_config.TextColumn(width="medium"),
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
        comp_info = next(item for item in live_financials if item["Company"] == selected_company)
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f"## {comp_info['Company']} ({comp_info['Ticker']})")
        st.caption(f"Ownership Type: **{comp_info['Type']}**")
        
        st.markdown(f"**Business Overview:** {comp_info['Description']}")
        
        det1, det2, det3 = st.columns(3)
        with det1:
            st.markdown(f"- **Market Cap / Valuation:** {comp_info['Market Cap']}")
            st.markdown(f"- **Stock Price:** {comp_info['Stock Price']}")
            st.markdown(f"- **Capital Budget (Annual CapEx):** {comp_info['Capital Budget (Annual CapEx)']}")
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

    # ------------------------------------------------------------------ #
    # MICROSOFT DEEP-DIVE — 2026 Environmental Sustainability & Community-First (FY2025)
    # ------------------------------------------------------------------ #
    st.divider()
    st.subheader("🟥 Microsoft — Environmental & 'Community-First' Deep-Dive")
    st.caption(
        "First-party data from Microsoft's **2026 Environmental Sustainability Report (FY2025)** "
        "and their landmark **January 2026 Community-First AI Infrastructure** initiative. "
        + src_link("msft_community_2026")
    )

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### ⚡ FY2025 Key Metrics & Commitments")
    ms1, ms2, ms3, ms4 = st.columns(4)
    ms1.metric("Total GHG Emissions", "20.3M tCO₂e", "+25% YoY growth (AI-driven)")
    ms2.metric("Power Draw Growth", "+24% YoY", "100% annual renewable match")
    ms3.metric("Scope 2 Share", "13% of footprint", "vs. 2% previously (RECs pause)")
    ms4.metric("Water Replenished", "14.0M m³", "Achieved global Water Positive")

    st.markdown(
        "**Key Operational Details & Methodological Shift:**  \n"
        "- **Carbon-Free Energy Priority**: Microsoft shifted accounting methodology by pausing the purchase of "
        "non-additional, unbundled Renewable Energy Certificates (RECs) to focus entirely on investing in **net-new** "
        "grid-decarbonizing carbon-free electricity (CFE) projects. This drove their reported Scope 2 emissions up from 2% to 13% "
        "of their footprint, reflecting the raw reality of grid consumption.  \n"
        "- **Supply Chain Scope 3**: Upstream construction materials (steel, concrete) and server hardware manufacturing continue "
        "to represent the largest portion of their carbon footprint."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 🏡 The Community-First AI Infrastructure Framework (January 2026)")
    st.caption("Launched by President Brad Smith in January 2026 to set a 'high bar' for datacenter civic responsibility across 5 core pillars:")
    
    st.markdown(
        "1. **⚡ Electricity (Ratepayer Protection)**: A firm pledge to **pay their own way** for grid upgrades. Microsoft commits to working "
        "with local utilities and public service commissions to set large-customer tariffs so that infrastructure costs (transmission, substations) "
        "are not passed on to residential power bills.  \n"
        "   * *Examples*: Partnering with **Black Hills Energy in Wyoming** on custom rates, and backing a new dedicated tariff for **Very Large Customers in Wisconsin** "
        "to safeguard residential users.  \n"
        "2. **💧 Water Net-Positivity**: Commitment to minimize water draws and replenish **more water than they consume** in the local water basins where they operate.  \n"
        "3. **🛠️ Local Employment**: Concrete mandates for local workforce construction hiring, combined with regional vocational and digital skills programs.  \n"
        "4. **🏥 Local Tax Base Contribution**: Generating substantial property tax revenue to subsidize municipal public schools, hospitals, parks, and libraries.  \n"
        "5. **🧠 Community Investment**: Directly funding local nonprofits and AI literacy training centers in host counties."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------------ #
    # AMAZON (AWS) DEEP-DIVE — Water Stewardship & Efficiency (2026)
    # ------------------------------------------------------------------ #
    st.divider()
    st.subheader("🧡 Amazon (AWS) — Environmental & Water Deep-Dive")
    st.caption(
        "First-party data from AWS's **2026 Water Stewardship Disclosures** "
        "and their corporate **AWS in Communities** program. "
        + src_link("aws_water_2026")
    )

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### ⚡ Water Stewardship & Cooling Metrics")
    aws1, aws2, aws3, aws4 = st.columns(4)
    aws1.metric("2025 Water Withdrawal", "2.5B Gallons", "First-ever disclosure (Jun 2026)")
    aws2.metric("Fleet-wide WUE", "0.12 L/kWh", "7.0× more efficient than industry avg")
    aws3.metric("Water-Positive Target", "75% Complete", "Net-positive water by 2030")
    aws4.metric("Mechanical Cooling Power", "Up to -50%", "Peak energy cut via system upgrades")

    st.markdown(
        "**Key Operational Details & Sourcing Strategies:**  \n"
        "- **Recycled Sourcing**: AWS targets non-drinking water (recycled municipal wastewater) for server cooling to protect public aquifers. "
        "Currently supplying over 100 campuses, with a goal of **120 campuses by 2030**.  \n"
        "- **Historical Transparency Milestone**: In **June 2026**, AWS published its first detailed annual water footprint reporting **2.5 billion gallons** "
        "of global withdrawals, addressing long-standing utility requests.  \n"
        "- **AWS in Communities Program**: Actively sponsors local infrastructure training bootcamps (fiber optic cabling, cloud systems support) in major cluster "
        "metros (such as Loudoun County, VA, and Morrow County, OR) to build a local pipeline of operations staff."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------------ #
    # META DEEP-DIVE — 2025 Environmental Data Index (FY2024)
    # ------------------------------------------------------------------ #
    st.divider()
    st.subheader("🟦 Meta Platforms — Environmental Deep-Dive")
    st.caption(
        "First-party data from Meta's **2025 Environmental Data Index (FY2024)**. "
        "Covers electricity consumption by campus, GHG emissions, water stewardship, PUE & WUE. "
        + src_link("meta_env_2025")
    )

    m = META_2024_HEADLINE
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### ⚡ 2024 Key Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("DC Electricity",      f"{m['dc_twh']} TWh",    "18 owned campuses + leased")
    m2.metric("Fleet-wide PUE",      f"{m['fleet_pue']}",     "Better than Google's 1.09")
    m3.metric("Fleet-wide WUE",      f"{m['fleet_wue']} L/kWh","vs. 0.30 in 2020")
    m4.metric("Renewable Match",     f"{m['renewable_match_pct']}%",  "every year since 2020")

    m5, m6, m7, m8 = st.columns(4)
    m5.metric("Scope 2 (market)",    f"{m['scope2_market_tco2e']:,} tCO2e",  "near-zero w/ RECs")
    m6.metric("Scope 2 (location)",  f"{m['scope2_location_tco2e']/1e6:.1f}M tCO2e","actual grid carbon")
    m7.metric("Scope 3 total",       f"{m['scope3_tco2e']/1e6:.1f}M tCO2e",  "incl. hardware mfg.")
    m8.metric("Water restored",      f"{m['water_restoration_ml']:,} ML",     "via stewardship projects")
    st.markdown('</div>', unsafe_allow_html=True)

    # Electricity growth chart
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 📈 Data Center Electricity Consumption (2020–2024)")
    st.caption("Meta DC electricity grew from 7.0 TWh in 2020 to **18.1 TWh** in 2024 — +159% in four years, driven by AI infrastructure buildout and new campus openings.")

    m_elec = META_DC_ELECTRICITY.copy()
    m_elec["dc_twh"]    = m_elec["dc_mwh"]    / 1e6
    m_elec["total_twh"] = m_elec["total_mwh"] / 1e6
    m_elec_long = m_elec.melt(id_vars="year", value_vars=["dc_twh", "total_twh"],
                              var_name="category", value_name="twh")
    m_elec_long["category"] = m_elec_long["category"].map(
        {"dc_twh": "Data Centers", "total_twh": "Total (incl. Offices)"})

    m_elec_chart = (
        alt.Chart(m_elec_long)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("twh:Q", title="Electricity (TWh)"),
            color=alt.Color("category:N",
                scale=alt.Scale(domain=["Data Centers", "Total (incl. Offices)"],
                                range=["#1877f2", "#42b72a"]),
                legend=alt.Legend(title="")),
            tooltip=["year:O", "category:N", alt.Tooltip("twh:Q", format=".1f", title="TWh")],
        ).properties(height=260)
    )
    st.altair_chart(m_elec_chart, use_container_width=True)
    st.caption(src_link("meta_env_2025") + " · p. F")
    st.markdown('</div>', unsafe_allow_html=True)

    # GHG chart
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 🌡️ GHG Emissions: Scope 2 Market vs. Location-Based (2020–2024)")
    st.caption(
        "Meta's market-based Scope 2 is near-zero (**1,358 tCO2e** in 2024) thanks to 100% REC matching. "
        "Location-based tells the real grid-impact story: **5.97M tCO2e** from actual electrons consumed. "
        "Scope 3 (hardware mfg., logistics, sold products) dominates the total footprint at **8.15M tCO2e**."
    )
    m_ghg = META_GHG.copy()
    m_ghg_long = m_ghg.melt(
        id_vars="year",
        value_vars=["scope2_location", "scope2_market", "scope3"],
        var_name="metric", value_name="tco2e"
    )
    m_ghg_long["Metric"] = m_ghg_long["metric"].map({
        "scope2_location": "Scope 2 (Location-based)",
        "scope2_market":   "Scope 2 (Market-based)",
        "scope3":          "Scope 3 (Value Chain)",
    })
    m_ghg_long["MtCO2e"] = m_ghg_long["tco2e"] / 1e6

    m_ghg_chart = (
        alt.Chart(m_ghg_long)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("MtCO2e:Q", title="Million tCO2e"),
            color=alt.Color("Metric:N",
                scale=alt.Scale(
                    domain=["Scope 2 (Location-based)", "Scope 2 (Market-based)", "Scope 3 (Value Chain)"],
                    range=["#ea4335", "#34a853", "#fa7343"]),
                legend=alt.Legend(title="")),
            tooltip=["year:O", "Metric:N", alt.Tooltip("MtCO2e:Q", format=".3f", title="Mt CO2e")],
        ).properties(height=260)
    )
    st.altair_chart(m_ghg_chart, use_container_width=True)
    st.caption(src_link("meta_env_2025") + " · pp. C–E")
    st.markdown('</div>', unsafe_allow_html=True)

    # PUE & WUE trend
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### ⚙️ PUE & WUE Trend (2020–2024)")
    st.caption(
        "Meta's fleet PUE has improved from 1.10 → **1.08** and WUE from 0.30 → **0.19 L/kWh**, "
        "reflecting continued investment in liquid cooling, airside economization, and AI-optimized airflow management."
    )
    m_eff = META_EFFICIENCY.copy()

    pue_c = (
        alt.Chart(m_eff)
        .mark_line(point=True, strokeWidth=3, color="#1877f2")
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("pue:Q", title="PUE", scale=alt.Scale(domain=[1.0, 1.15])),
            tooltip=["year:O", alt.Tooltip("pue:Q", format=".2f", title="PUE")],
        )
    )
    wue_c = (
        alt.Chart(m_eff)
        .mark_line(point=True, strokeWidth=3, color="#42b72a", strokeDash=[4, 2])
        .encode(
            x=alt.X("year:O"),
            y=alt.Y("wue:Q", title="WUE (L/kWh)", scale=alt.Scale(domain=[0.0, 0.40])),
            tooltip=["year:O", alt.Tooltip("wue:Q", format=".2f", title="WUE")],
        )
    )
    combined = alt.layer(pue_c, wue_c).resolve_scale(y="independent").properties(height=240)
    st.altair_chart(combined, use_container_width=True)
    st.caption("🔵 blue = PUE (left axis) · 🟢 green dashed = WUE in L/kWh (right axis) · " + src_link("meta_env_2025") + " · p. H")
    st.markdown('</div>', unsafe_allow_html=True)

    # Per-campus electricity bar chart
    with st.expander("🏭 Electricity by Data Center Campus (2024, MWh)"):
        st.caption(
            "Top consumers: Altoona IA (1.59 TWh), Prineville OR (1.73 TWh), Sarpy NE (1.26 TWh), and leased facilities (3.07 TWh). "
            + src_link("meta_env_2025") + " · p. F"
        )
        campus_df = META_DC_CAMPUS_ELECTRICITY.sort_values("mwh_2024", ascending=False).copy()
        campus_df["TWh"] = campus_df["mwh_2024"] / 1e6
        campus_bar = (
            alt.Chart(campus_df)
            .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
            .encode(
                x=alt.X("TWh:Q", title="Electricity (TWh)"),
                y=alt.Y("campus:N", sort="-x", title=None),
                color=alt.Color("region:N",
                    scale=alt.Scale(scheme="tableau10"),
                    legend=alt.Legend(title="Region")),
                tooltip=["campus:N", "region:N",
                         alt.Tooltip("mwh_2024:Q", format=",", title="MWh"),
                         alt.Tooltip("TWh:Q", format=".3f", title="TWh")],
            ).properties(height=420)
        )
        st.altair_chart(campus_bar, use_container_width=True)
        campus_df_display = campus_df[["campus", "region", "mwh_2024", "TWh"]].copy()
        campus_df_display.columns = ["Campus", "Region", "MWh (2024)", "TWh (2024)"]
        st.dataframe(campus_df_display, use_container_width=True, hide_index=True,
            column_config={
                "MWh (2024)": st.column_config.NumberColumn(format="%d"),
                "TWh (2024)": st.column_config.NumberColumn(format="%.3f"),
            })


    # Meta community impact program
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 🏡 Meta Data Center Community Action Grants & CBAs")
    st.caption("Meta's local funding and community-benefit commitments in data center host counties: " + src_link("meta_community_2026"))
    
    st.markdown(
        "- **Community Action Grants**: Since 2011, Meta has contributed over **$74 Million** globally (with **$24 Million** through direct "
        "local Community Action Grants) to fund technology integration and STEAM education in regional public schools.  \n"
        "- **2026 Grant Cycle**: Awarded **328 separate grants** across data center communities, expanding the program to include seven "
        "new host regions.  \n"
        "- **Local Community Benefit Agreements (CBAs)**: In counties like Sarpy (NE), Altoona (IA), and Gallatin (TN), Meta enters into CBAs to fund "
        "local public parks, municipal fiber-optic broadband expansions, and water-basin replenishment projects."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------------ #
    # CORPORATE KEY PLAYERS & DIRECTORS
    # ------------------------------------------------------------------ #
    st.divider()
    st.subheader("👥 Key Corporate Players & Sustainability Directors")
    st.caption(
        "A directory of senior executives, data center directors, grid planners, and sustainability leaders "
        "driving hyperscale expansion. Use the search link to look up their professional profile on LinkedIn."
    )

    import urllib.parse
    
    KEY_PLAYERS = [
        # Microsoft
        ("Noelle Walsh", "Microsoft", "Corporate VP, Cloud Operations & Innovation", "Leads global Azure cloud infrastructure construction and operations."),
        ("Bobby Hollis", "Microsoft", "VP of Energy", "Directs global energy sourcing, grid integration, and power purchase agreements (PPAs)."),
        ("Melanie Nakagawa", "Microsoft", "Chief Sustainability Officer", "Directs corporate climate and sustainability policies (carbon negative by 2030)."),
        # Google
        ("Kate Brandt", "Google (Alphabet)", "Chief Sustainability Officer", "Leads circular economy, carbon-free energy, and sustainability goals across Google."),
        ("Michael Terrell", "Google (Alphabet)", "Senior Director of Energy and Climate", "Pioneered Google's 24/7 hourly Carbon-Free Energy (CFE) matching strategy."),
        ("Ben Townsend", "Google (Alphabet)", "Global Head of Infrastructure Planning & Water Policy", "Oversees site selection and cooling water sustainability policies."),
        # Meta
        ("Rachel Peterson", "Meta Platforms", "VP of Data Centers", "Directs Meta's global owned and leased data center physical infrastructure."),
        ("Urvi Parekh", "Meta Platforms", "Head of Renewable Energy", "Leads Meta's clean energy procurement (15+ GW contracted portfolio)."),
        ("Blair Anderson", "Meta Platforms", "Director of State & Local Public Policy", "Leads governmental relations and community tax incentives negotiations."),
        # Amazon (AWS)
        ("Kevin Miller", "Amazon (AWS)", "VP of Global Data Centers", "Directs AWS worldwide physical infrastructure design, build, and operations."),
        ("Chris Roe", "Amazon (AWS)", "Director of Energy & Sustainable Operations", "Leads clean power procurement and operational carbon reduction programs."),
        ("Jenna Leiner", "Amazon (AWS)", "Lead, Water Sustainability", "Manages AWS global water replenishment projects and dry-cooling upgrades."),
        # CoreWeave
        ("Michael Intrator", "CoreWeave", "Co-founder & CEO", "Leads corporate strategy and capital raises for specialized GPU hosting clusters."),
        ("Brian Venturo", "CoreWeave", "Co-founder & CTO", "Designs CoreWeave's hardware architecture and high-density cluster cooling setups."),
        # Equinix
        ("Adaire Fox-Martin", "Equinix", "Chief Executive Officer", "Directs corporate strategy for the world's largest colocation provider."),
        ("Christopher Wellise", "Equinix", "VP of Global Sustainability", "Leads corporate green design, energy reporting, and circular hardware programs."),
        # Digital Realty
        ("Andy Power", "Digital Realty", "President & CEO", "Leads global wholesale data center development and leasing strategy."),
        ("Aaron Binkley", "Digital Realty", "VP of Sustainability", "Directs global environmental reporting, carbon reduction, and green tariffs.")
    ]

    player_list = []
    for name, company, title, focus in KEY_PLAYERS:
        # Generate direct LinkedIn search URL
        search_query = f"{name} {company}"
        linkedin_url = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(search_query)}"
        
        player_list.append({
            "Name": name,
            "Company": company,
            "Title / Corporate Role": title,
            "Infrastructure / Sustainability Focus": focus,
            "LinkedIn Profile": linkedin_url
        })

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # Search box for key players
    search_player = st.text_input("🔍 Filter players by name, company, or role", value="")
    
    player_df = pd.DataFrame(player_list)
    if search_player:
        mask = (
            player_df["Name"].str.contains(search_player, case=False) |
            player_df["Company"].str.contains(search_player, case=False) |
            player_df["Title / Corporate Role"].str.contains(search_player, case=False)
        )
        player_df = player_df[mask]

    st.dataframe(
        player_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Name": st.column_config.TextColumn(width="medium"),
            "Company": st.column_config.TextColumn(width="medium"),
            "Title / Corporate Role": st.column_config.TextColumn(width="large"),
            "Infrastructure / Sustainability Focus": st.column_config.TextColumn(width="large"),
            "LinkedIn Profile": st.column_config.LinkColumn("Professional Profile", display_text="👥 LinkedIn Search", width="medium")
        }
    )
    st.markdown('</div>', unsafe_allow_html=True)

