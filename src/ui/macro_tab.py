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
