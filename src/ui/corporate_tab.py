"""
Corporate Profiles tab — displays financial and operational profile data
(market cap, stock price, net income, assets, employees) for major public
and private data center developers and hyperscalers.
"""

import streamlit as st
import pandas as pd

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
        "Description": "Google Cloud provider and TPU custom-accelerator hardware designer.",
        "IR Link": "https://abc.xyz/investor/"
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

def render_corporate_tab():
    st.subheader("💼 Corporate Profiles — Financials & Scale")
    st.caption(
        "Financial and operational scale of the companies driving data center expansion. "
        "Hyperscale players (Microsoft, Google, Amazon, Meta) and specialised operators "
        "(colocation REITs and private-equity-backed developers) are listed below."
    )

    # Convert to dataframe
    df = pd.DataFrame(COMPANY_FINANCIALS)

    # Summary metrics row
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Cloud & Data Center Sector Power")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Public Hyperscaler Cap", "$8.53 Trillion", help="Combined market cap of MSFT, GOOGL, AMZN, and META")
    m2.metric("Combined Sector Employees", "> 2.2 Million", help="Total employees across listed firms, including retail divisions")
    m3.metric("Annual Cloud Net Income", "> $230 Billion", help="Aggregated net income for the five public tech filers")
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

    st.caption("Figures reflect FY2025/2026 filings, annual reports, SEC 10-K competition statements, and recent private equity valuations.")
