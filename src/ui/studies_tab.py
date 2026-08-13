"""
State Studies tab — state-level data center market profiles and curated
legislative deep-dives. The choropleth map has moved to the unified Map tab;
this tab keeps the dropdown selector and the state profile renderer.
"""

import streamlit as st
from src.constants import STATE_DC_DF
from src.ui.state_detail import render_state_profile


def render_studies_tab():
    st.subheader("State Studies & Market Profiles")
    st.caption(
        "A directory of official state policy audits, utility Board of Public Utilities (BPU) load studies, "
        "and detailed data center market statistics. Use the **Map** tab to click a state on the map, "
        "or choose a state from the dropdown below."
    )
    st.info("**See the Map tab** for an interactive choropleth and clickable state profiles.")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### State Data Center Profile Details")

    dropdown_states = ["Select State..."] + sorted(list(STATE_DC_DF["state"].unique()))

    my_state = st.session_state.get("my_state")
    default_idx = 0
    if my_state and my_state in dropdown_states:
        default_idx = dropdown_states.index(my_state)

    selected_state = st.selectbox(
        "Choose a state to view details:",
        options=dropdown_states,
        index=default_idx,
        key="state_study_select"
    )

    if selected_state != "Select State...":
        render_state_profile(selected_state)
    else:
        st.info("Select a state from the dropdown to load its comprehensive data center profile.")

    st.markdown('</div>', unsafe_allow_html=True)

    st.info(
        "**Facing a data center project in your state?** GridWatch Consulting "
        "provides impact analysis, CBA drafting, and hearing support — with a "
        "success-fee model. See the **Consulting** tab for a free assessment."
    )
