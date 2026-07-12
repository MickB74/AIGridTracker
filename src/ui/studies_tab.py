"""
State Studies tab — presents official state-level data center impact studies,
legislative reports, and grid integration papers (e.g. Michigan CRC, Virginia JLARC).
Includes an interactive US map showing featured states.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.helpers import src_link

# Featured state studies data
STATE_STUDIES = {
    "Michigan": {
        "abbrev": "MI",
        "title": "Data Centers in Michigan: Evaluation of Policy Controversies Regarding Hyperscale Data Center Development (June 2026)",
        "author": "Citizens Research Council of Michigan (Report 426)",
        "src_key": "crc_mich_2026",
        "pdf_url": "https://crcmich.org/PUBLICAT/2020s/2026/rpt426-data_centers_in_Michigan.pdf",
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
        "abbrev": "VA",
        "title": "Joint Legislative Audit and Review Commission (JLARC) Data Center Study (December 2024)",
        "author": "Commonwealth of Virginia (Report 591)",
        "src_key": "jlarc_va_2024",
        "pdf_url": "https://jlarc.virginia.gov/pdfs/reports/Rpt591.pdf",
        "summary": "Comprehensive analysis of Loudoun County ('Data Center Alley') density, PJM transmission bottlenecks, and tax revenues.",
        "findings": [
            "**Tax Revenue Windfall**: Data centers generated over $1B in annual local tax revenue in Northern Virginia, significantly subsidizing residential public school systems and services.",
            "**Transmission Constraints**: Unprecedented cluster density in Loudoun & Prince William counties has triggered PJM transmission constraints, requiring billions in grid upgrades (e.g. 500kV lines) funded by all grid ratepayers.",
            "**Clean Energy Backlash**: Meeting hyperscaler green commitments (100% renewable matching) has led to massive solar land-use debates across rural Virginia counties.",
            "**Water Stewardship**: Transitioning away from open-loop evaporative cooling towards air-cooling has reduced water intensity, but older facilities still consume millions of gallons daily."
        ],
        "metrics": {
            "State DC Power Draw": "3,000+ MW (largest globally)",
            "Annual Local Tax Revenue": "$1.2+ Billion",
            "Grid Bottleneck Level": "High (PJM queues restricted)",
            "Zoning Controversy": "Agricultural land-use conversion"
        }
    },
    "Georgia": {
        "abbrev": "GA",
        "title": "Joint Committee on Data Center Tax Incentives & Grid Reliability (2024–2025)",
        "author": "Georgia General Assembly Special Study Committee",
        "src_key": "ga_house_2024",
        "pdf_url": "https://www.house.ga.gov/",
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
        "abbrev": "OR",
        "title": "Data Centers and Energy Use in Oregon (2024)",
        "author": "Oregon Department of Energy (ODOE) Sector Report",
        "src_key": "oregon_doe_2024",
        "pdf_url": "https://www.oregon.gov/energy/Data-Center-Energy-Use.aspx",
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
        "abbrev": "MD",
        "title": "Critical Infrastructure Streamlining Act of 2024 & State Data Center Impact Mandate (2024)",
        "author": "Maryland General Assembly (CISA / SB 116)",
        "src_key": "md_assembly_2024",
        "pdf_url": "https://mgaleg.maryland.gov/",
        "summary": "Legislative response to utility generator permit denials and creation of state-wide environmental impact study.",
        "findings": [
            "**Backup Generator Controversy**: Aligned Data Centers canceled a massive $30B project in late 2023 after the Maryland PSC denied a permit for 168 diesel backup generators due to air quality emissions thresholds.",
            "**Regulatory Streamlining (CISA)**: In May 2024, Maryland enacted the Critical Infrastructure Streamlining Act to exempt data center backup power from Certificate of Public Convenience and Necessity (CPCN) reviews to attract investment.",
            "**Environmental Safeguards**: Environmental groups expressed concern over local particulate and carbon emissions from diesel backup arrays, prompting the state to commission a comprehensive data center impact study due September 1, 2026."
        ],
        "metrics": {
            "Streamlining Bill (CISA)": "Passed (May 2024)",
            "Canceled Project Investment": "$30 Billion",
            "Controversial Hardware": "168 Diesel Generators",
            "Comprehensive Study Due": "Sept 1, 2026"
        }
    },
    "Indiana": {
        "abbrev": "IN",
        "title": "Indiana Utility Regulatory Commission Large Load Grid & Water Studies (2026)",
        "author": "Indiana General Assembly / IURC (HB 1245)",
        "src_key": "iurc_indiana_2026",
        "pdf_url": "https://iga.in.gov/",
        "summary": "Administrative mandates on ratepayer protection, utility load forecasts, and local water inventory reviews.",
        "findings": [
            "**Ratepayer Cost-Shifting**: House Bill 1245 was introduced in the 2026 session to mandate that the IURC study how data center demand affects retail electric rates, ensuring residential users do not subsidize transmission expansions.",
            "**Statewide Water Inventory**: Due to significant Meta ($10B in La Porte) and Amazon ($15B in Lebanon) campuses, the state is currently building a statewide water inventory by end of 2026 to monitor large industrial draws.",
            "**County-Level Moratoriums**: Due to perceived gaps in state environmental oversight, multiple Indiana counties and cities (including Indianapolis) have enacted temporary data center construction moratoriums to protect local resources."
        ],
        "metrics": {
            "IURC Study Mandate": "Active (HB 1245, 2026)",
            "Featured Projects": "Amazon ($15B), Meta ($10B)",
            "Local Moratoriums": "Enacted (multiple counties)",
            "State Water Inventory": "Due Late 2026"
        }
    }
}

# Mapping states for Choropleth
MAP_STATES = [
    # state, code, has_study, val
    ("Michigan", "MI", 1, 10),
    ("Virginia", "VA", 1, 10),
    ("Georgia", "GA", 1, 10),
    ("Oregon", "OR", 1, 10),
    ("Maryland", "MD", 1, 10),
    ("Indiana", "IN", 1, 10),
    # Fill others
    ("Alabama", "AL", 0, 0), ("Alaska", "AK", 0, 0), ("Arizona", "AZ", 0, 0), ("Arkansas", "AR", 0, 0),
    ("California", "CA", 0, 0), ("Colorado", "CO", 0, 0), ("Connecticut", "CT", 0, 0), ("Delaware", "DE", 0, 0),
    ("Florida", "FL", 0, 0), ("Hawaii", "HI", 0, 0), ("Idaho", "ID", 0, 0), ("Illinois", "IL", 0, 0),
    ("Iowa", "IA", 0, 0), ("Kansas", "KS", 0, 0), ("Kentucky", "KY", 0, 0),
    ("Louisiana", "LA", 0, 0), ("Maine", "ME", 0, 0), ("Massachusetts", "MA", 0, 0),
    ("Minnesota", "MN", 0, 0), ("Mississippi", "MS", 0, 0), ("Missouri", "MO", 0, 0), ("Montana", "MT", 0, 0),
    ("Nebraska", "NE", 0, 0), ("Nevada", "NV", 0, 0), ("New Hampshire", "NH", 0, 0), ("New Jersey", "NJ", 0, 0),
    ("New Mexico", "NM", 0, 0), ("New York", "NY", 0, 0), ("North Carolina", "NC", 0, 0), ("North Dakota", "ND", 0, 0),
    ("Ohio", "OH", 0, 0), ("Oklahoma", "OK", 0, 0), ("Pennsylvania", "PA", 0, 0), ("Rhode Island", "RI", 0, 0),
    ("South Carolina", "SC", 0, 0), ("South Dakota", "SD", 0, 0), ("Tennessee", "TN", 0, 0), ("Texas", "TX", 0, 0),
    ("Utah", "UT", 0, 0), ("Vermont", "VT", 0, 0), ("Washington", "WA", 0, 0), ("West Virginia", "WV", 0, 0),
    ("Wisconsin", "WI", 0, 0), ("Wyoming", "WY", 0, 0)
]
MAP_DF = pd.DataFrame(MAP_STATES, columns=["state", "code", "has_study", "value"])

def render_studies_tab():
    st.subheader("🏛️ State Studies — Local Impact & Legislative Audits")
    st.caption(
        "A directory of official, state-level data center impact studies, joint legislative audits, "
        "and public policy evaluation reports. Click a colored state on the map or select from the dropdown "
        "to view key findings."
    )

    # US Map visualization
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🗺️ U.S. State Studies Map")
    
    # Custom plotly map
    fig = px.choropleth(
        MAP_DF,
        locations="code",
        locationmode="USA-states",
        color="value",
        scope="usa",
        color_continuous_scale=["rgba(0,0,0,0)", "#ff5a1f"],
        labels={"value": "Featured Study"},
        hover_name="state"
    )
    fig.update_layout(
        geo=dict(
            bgcolor="rgba(0,0,0,0)",
            lakecolor="rgba(0,0,0,0)",
            subunitcolor="#3c3f44",
            landcolor="#1c1d21",
            showlakes=False
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=380,
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    event = st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="state_studies_map")
    st.caption("Orange states have featured studies. Click a state to view or use the selector below.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Get state selection from click
    clicked_state = None
    try:
        if event.selection and "points" in event.selection and len(event.selection["points"]) > 0:
            point = event.selection["points"][0]
            # Map abbrev back to state name
            code = point.get("location")
            for name, c, hs, v in MAP_STATES:
                if c == code and hs == 1:
                    clicked_state = name
    except Exception:
        pass

    # Dropdown selector
    dropdown_states = ["Select State..."] + sorted(list(STATE_STUDIES.keys()))
    default_idx = 0
    if clicked_state in STATE_STUDIES:
        default_idx = dropdown_states.index(clicked_state)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📋 Study Directory & Details")
    selected_state = st.selectbox(
        "Choose a state study to view details:",
        options=dropdown_states,
        index=default_idx,
        key="state_study_select"
    )

    if selected_state != "Select State...":
        study = STATE_STUDIES[selected_state]
        st.markdown(f"## {selected_state}: {study['title']}")
        st.caption(f"**Author / Agency:** {study['author']} · **Reference Link:** {src_link(study['src_key'])}")
        st.markdown(f"**Study Scope Summary:** *{study['summary']}*")
        
        # Summary Metrics
        st.markdown("#### Key Metrics from Report")
        cols = st.columns(len(study["metrics"]))
        for i, (k, v) in enumerate(study["metrics"].items()):
            cols[i].metric(k, v)
        
        st.divider()
        
        # Key Findings
        st.markdown("#### 🔍 Core Findings")
        for finding in study["findings"]:
            st.markdown(f"- {finding}")
            
        st.divider()
        st.markdown(f"🔗 **[Download Full Report PDF]({study['pdf_url']})**")
    else:
        st.info("💡 Select an orange state on the map or choose a state from the dropdown to load its policy findings.")
    
    st.markdown('</div>', unsafe_allow_html=True)
