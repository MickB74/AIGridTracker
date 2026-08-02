"""
Corporate Profiles tab — displays financial and operational profile data
(market cap, stock price, net income, assets, employees) for major public
and private data center developers, hardware manufacturers, and hyperscalers.
Includes an interactive growth trend chart over recent time periods.
"""

import datetime as _dt

import streamlit as st
import pandas as pd
import altair as alt
from src.constants import SHARES_OUTSTANDING
from src.helpers import src_link
from src.services.sec_xbrl import fetch_dynamic_financials
from src.services.marketdata import fetch_live_quotes


def _fmt_market_cap(usd_billions: float) -> str:
    """Format a market cap given in $B as a Trillion/Billion string."""
    if usd_billions >= 1000:
        return f"${usd_billions / 1000:.2f} Trillion"
    return f"${usd_billions:,.1f} Billion"

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
        "The companies driving the build-out: hyperscalers, hardware enablers, "
        "and colocation operators — financials, environmental data, and the "
        "people who run them."
    )

    with st.expander("📑 On this page", expanded=False):
        st.markdown(
            "**1.** Sector financial scale (live stock / SEC data) · "
            "**2.** Company profiles directory · "
            "**3.** Revenue growth over time"
        )

    # Live stock prices (Yahoo Finance) for all public tickers, fetched once.
    _public_tickers = tuple(
        i["Ticker"] for i in COMPANY_FINANCIALS if i["Ticker"] != "Private"
    )
    quotes = fetch_live_quotes(_public_tickers)

    # Convert to dataframe and merge SEC XBRL + live-quote data where available
    live_financials = []
    live_cap_total_b = 0.0     # sum of live-computed public market caps ($B)
    quote_epoch = None          # newest quote timestamp, for the "as of" note
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

            q = quotes.get(ticker)
            if q:
                price = q["price"]
                updated_item["Stock Price"] = f"${price:,.2f}"
                if q.get("time"):
                    quote_epoch = max(quote_epoch or 0, q["time"])
                shares_b = SHARES_OUTSTANDING.get(ticker)
                if shares_b:
                    cap_b = price * shares_b
                    updated_item["Market Cap"] = f"≈ {_fmt_market_cap(cap_b)}"
                    live_cap_total_b += cap_b
        live_financials.append(updated_item)

    df = pd.DataFrame(live_financials)

    # "As of" date from the newest quote (falls back to a static note offline)
    _as_of = ""
    if quote_epoch:
        _as_of = _dt.datetime.utcfromtimestamp(quote_epoch).strftime("%b %d, %Y")

    # Summary metrics row
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Sector Financial Scale")
    
    _cap_str = (f"${live_cap_total_b / 1000:.1f} Trillion" if live_cap_total_b >= 1000
                else "$12.2 Trillion")
    _cap_delta = f"live · as of {_as_of}" if (live_cap_total_b and _as_of) else "static estimate"
    m1, m2, m3 = st.columns(3)
    m1.metric("Combined Public Sector Cap", _cap_str, _cap_delta,
              delta_color="off",
              help="Sum of live market caps (price × shares outstanding) for the public tickers with a quote.")
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
    if _as_of:
        st.caption(
            f"**Stock Price** live via {src_link('yahoo_finance')} (as of {_as_of}); "
            f"**Market Cap** ≈ live price × shares outstanding. "
            "**Net Income / CapEx / Total Assets** from each company's latest SEC 10-K "
            "(XBRL). Employees and private-company valuations are static."
        )
    else:
        st.caption(
            "Live quotes unavailable right now — showing last static figures. "
            "**Net Income / CapEx / Total Assets** still reflect the latest SEC 10-K where available."
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

    st.caption("Stock prices and market caps are live (Yahoo Finance, delayed); income, CapEx and assets come from SEC 10-K XBRL filings; private-company valuations reflect recent PE transactions.")

    st.divider()
    st.info(
        "**Environmental data & executives moved to the site:** "
        "[aigridwatch.com/environment](https://aigridwatch.com/environment) — "
        "hyperscaler environmental comparison, spend estimator, and "
        "deep-dives (Google / Microsoft / AWS / Meta). "
        "[aigridwatch.com/executives](https://aigridwatch.com/executives) — "
        "executive directory."
    )

