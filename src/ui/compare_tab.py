import streamlit as st
import pandas as pd
import altair as alt
from src.constants import QUERY_COEFFS

def render_compare_tab():
    st.subheader("Per-query energy across sources")
    st.caption("First-party disclosures and benchmark studies vary widely, mostly by "
               "scope (chip-only vs full-stack) and model size. Note the log scale.")
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    df = pd.DataFrame([{"source": k, "energy_wh": v["energy_wh"]} for k, v in QUERY_COEFFS.items()])
    log = st.toggle("Log scale (GPT-5 report dwarfs the rest)", value=True)
    
    # Render premium colored chart
    chart = (alt.Chart(df).mark_bar().encode(
        x=alt.X("energy_wh:Q", title="Wh per query",
                scale=alt.Scale(type="log") if log else alt.Scale(type="linear")),
        y=alt.Y("source:N", sort="-x", title=None),
        tooltip=["source", "energy_wh"],
        color=alt.Color("energy_wh:Q", scale=alt.Scale(scheme="yelloworangered"), legend=None),
    ).properties(height=280))
    st.altair_chart(chart, use_container_width=True)
    st.caption("⚠️ The GPT-5 figure is a contested third-party report — an upper bound, "
               "not a disclosed number.")
    st.markdown('</div>', unsafe_allow_html=True)
