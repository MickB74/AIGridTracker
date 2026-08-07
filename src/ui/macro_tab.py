"""
Macro tab — global data-center electricity outlook (IEA).

Unused: content was ported to web/outlook.html (see CLAUDE.md). Not
imported by app.py. Kept for reference.
"""

import streamlit as st
import altair as alt
from src.constants import IEA_OUTLOOK, DC_FORECASTS, DC_FORECASTS_US
from src.helpers import src_link

def render_macro_tab():
    st.subheader("Global data-center electricity — IEA outlook")
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    line = (alt.Chart(IEA_OUTLOOK).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X("year:O", title=None), y=alt.Y("twh:Q", title="TWh / year"),
        tooltip=["year", "twh"]).properties(height=320))
    st.altair_chart(line, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("2024 → 2030", "~415 → 945 TWh", "≈ Japan's total demand")
    c2.metric("Share of global electricity, 2030", "~3%")
    c3.metric("Data-center CO₂, 2030", "~1%", "of global emissions")

    st.markdown(
        "- AI's slice of data-center power is projected to climb from **5–15%** recently "
        "to **35–50% by 2030**.\n"
        "- **Inference dominates**: it accounts for the majority of a model's lifetime "
        "energy (>90% by some operator accounts) — *usage*, not training, is the lever.\n"
        "- **Jevons paradox:** per-query efficiency keeps improving (Gemini fell ~33× in "
        "a year), but cheaper inference drives more usage — total load still rises.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("Forecasts disagree — a lot")
    st.caption("Third-party projections of **global** data-center electricity (TWh) "
               "vary widely by forecaster, year, and scenario. Same metric, so "
               "they're comparable; the gap is the honest uncertainty.")
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    fdf = DC_FORECASTS.copy()
    fdf["label"] = fdf["source"] + " · " + fdf["year"].astype(str)
    fc = (alt.Chart(fdf).mark_bar().encode(
        x=alt.X("twh:Q", title="Global data-center electricity (TWh/yr)"),
        y=alt.Y("label:N", sort="-x", title=None),
        color=alt.Color("source:N", legend=alt.Legend(title="Forecaster")),
        tooltip=["source", "year", "twh"],
    ).properties(height=max(240, 30 * len(fdf))))
    st.altair_chart(fc, use_container_width=True)

    st.markdown("**US-only, 2030 (TWh)** — the spread across forecasters is the "
                "whole point: central estimates run ~2.8× from low to high.")
    udf = DC_FORECASTS_US.copy()
    uc = (alt.Chart(udf).mark_bar().encode(
        x=alt.X("twh:Q", title="US data-center electricity, 2030 (TWh/yr)"),
        y=alt.Y("source:N", sort="x", title=None),
        color=alt.Color("twh:Q", scale=alt.Scale(scheme="yelloworangered"), legend=None),
        tooltip=["source", "twh", "note"],
    ).properties(height=max(200, 34 * len(udf))))
    st.altair_chart(uc, use_container_width=True)

    st.markdown(
        f"- **In capacity terms:** BloombergNEF sees US data-center power hitting "
        f"**~106 GW by 2035** (from ~25 GW in 2024) — **8.6%** of all US "
        f"electricity, more than double today's 3.5%. {src_link('bnef_106')}.\n"
        f"- **Why the spread:** forecasts hinge on how much announced pipeline "
        f"actually gets built and powered (interconnection queues are heavily "
        f"speculative), plus efficiency gains and utilisation assumptions.")
    st.caption("Forecasters: " + " · ".join(src_link(k) for k in
               ["iea_2025", "bnef", "gartner", "sp_451", "epri_pi", "lbnl",
                "wri_range"]))
    st.markdown('</div>', unsafe_allow_html=True)

    # ── RURAL DATA CENTER SHIFT (Pew Research 2026) ─────────────────────────
    st.divider()
    st.subheader("🏡 U.S. Geographic Shift — The Rural Migration")
    st.caption(
        "Analysis of national data-center geographic placement by the **Pew Research Center (April 2026)**. "
        "Shows a major structural shift in site selection away from traditional urban centers towards rural areas. "
        + src_link("pew_rural_2026")
    )
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 📊 Planned vs. Operating Data Centers by Census Type")
    r1, r2, r3 = st.columns(3)
    r1.metric("Planned in Rural Areas", "67%", "vs. 13% of currently operating")
    r2.metric("Planned in Urban Areas", "33%", "vs. 87% of currently operating")
    r3.metric("Landing in 'New' Counties", "39%", "counties with zero current data centers")
    
    st.markdown(
        "**Key Findings from the 2026 Pew Report:**  \n"
        "- **The Regional Drivers**: The South and Midwest are capturing the vast majority (**three-quarters**) of all planned "
        "U.S. data center developments. The South alone accounts for nearly half (**48%**) of all upcoming sites.  \n"
        "- **Growth Speed**: Planned developments represent a **62% increase** in total facilities for the South and a **64% increase** "
        "for the Midwest relative to current counts.  \n"
        "- **Proximity to Residents**: Currently, **38% of Americans** live within 5 miles of an operational data center. Once planned "
        "projects are built, this number rises to **42%**.  \n"
        "- **Tight Siting Clusters**: Data centers remain highly clustered: **90%** of all operating and planned sites are within 5 miles of another."
    )
    
    # State operating vs planned leaderboard
    with st.expander("📈 Top States by Planned & Operating Facilities (Pew 2026)"):
        st.caption("Leaders in planned and operating facilities as of Feb 2026. Source: Pew Research / Data Center Map.")
        import pandas as pd
        pew_states = pd.DataFrame([
            {"State": "Virginia", "Operating": 398, "Planned": 287, "Total": 685},
            {"State": "Texas", "Operating": 296, "Planned": 170, "Total": 466},
            {"State": "Georgia", "Operating": 94, "Planned": 141, "Total": 235},
            {"State": "Illinois", "Operating": 139, "Planned": 123, "Total": 262},
            {"State": "Arizona", "Operating": 98, "Planned": 86, "Total": 184},
            {"State": "Indiana", "Operating": 38, "Planned": 54, "Total": 92},
            {"State": "Ohio", "Operating": 166, "Planned": 57, "Total": 223},
            {"State": "Pennsylvania", "Operating": 78, "Planned": 51, "Total": 129},
            {"State": "North Carolina", "Operating": 72, "Planned": 41, "Total": 113},
            {"State": "Iowa", "Operating": 64, "Planned": 41, "Total": 105},
        ])
        
        # Draw a grouped bar chart
        pew_long = pew_states.melt(id_vars="State", value_vars=["Operating", "Planned"], 
                                   var_name="Status", value_name="Count")
        pew_chart = (
            alt.Chart(pew_long)
            .mark_bar()
            .encode(
                x=alt.X("Count:Q", title="Number of Data Centers"),
                y=alt.Y("State:N", sort="-x", title=None),
                color=alt.Color("Status:N", scale=alt.Scale(domain=["Operating", "Planned"], range=["#2b5c8f", "#ff7f0e"])),
                tooltip=["State", "Status", "Count"]
            ).properties(height=280)
        )
        st.altair_chart(pew_chart, use_container_width=True)
        st.dataframe(pew_states.sort_values("Total", ascending=False), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

