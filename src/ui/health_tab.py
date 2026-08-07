"""
Health risks module — six-panel overview of how data centers affect the
people living near them (air, noise, light, bills, water, climate), with
every fact wired to SOURCES and a "what to demand" ask per risk. Format
inspired by the Environmental Health Project's "Health Risks of Data
Centers" infographic (SOURCES["ehp_health"]). Stacked in the Learn tab;
ships with a downloadable infographic PDF for hearings.

Unused: content is rendered by web/health-risks.html from the same
HEALTH_RISKS data (see CLAUDE.md). `build_health_pdf` is still live —
called directly from src/pdf_pack.py — but this render function and its
import of it are not. Not imported by app.py. Kept for reference.
"""

import streamlit as st

from src.constants import HEALTH_RISKS, SOURCES
from src.helpers import src_link
from src.pdf_pack import build_health_pdf
from src.services.tracking import log_event


@st.cache_data
def _health_pdf_bytes():
    return build_health_pdf(HEALTH_RISKS, SOURCES)


def render_health_tab():
    st.subheader("🏥 The health risks of data centers")
    st.caption(
        "Six ways a facility affects the people who live near one — every "
        "claim sourced, every risk paired with the permit condition that "
        "addresses it. Format inspired by the Environmental Health "
        f"Project's community infographic ({src_link('ehp_health')})."
    )

    # 2 rows x 3 columns of colored summary cards
    for row_start in (0, 3):
        cols = st.columns(3)
        for col, risk in zip(cols, HEALTH_RISKS[row_start:row_start + 3]):
            with col:
                st.markdown(
                    f'<div style="background:{risk["color"]};'
                    'border-radius:12px;padding:14px 16px;min-height:150px;'
                    'margin-bottom:12px;">'
                    f'<div style="font-size:1.4rem;">{risk["icon"]}</div>'
                    f'<div style="font-weight:700;color:#fff;'
                    f'margin:4px 0 6px;">{risk["title"]}</div>'
                    f'<div style="font-size:0.8rem;color:'
                    f'rgba(255,255,255,0.85);line-height:1.35;">'
                    f'{risk["summary"]}</div></div>',
                    unsafe_allow_html=True)

    st.download_button(
        "📥 Download the infographic (PDF) — print it for your next hearing",
        _health_pdf_bytes(),
        "gridwatch_health_risks.pdf",
        "application/pdf",
        key="health_pdf_dl",
        type="primary",
        on_click=log_event,
        args=("health_pdf_download",),
    )

    st.markdown("#### The evidence, risk by risk")
    for risk in HEALTH_RISKS:
        with st.expander(f"{risk['icon']} {risk['title']}"):
            for fact in risk["facts"]:
                st.markdown(f"- {fact['text']} — {src_link(fact['src'])}")
            st.success(f"**What to demand:** {risk['ask']}")

    st.info(
        "**See also:** put dollar figures on these risks in the **Local "
        "Impact Calculator** (above) · model CBA clauses for noise, water, "
        "and cost causation in the **Negotiation toolkit** · the full "
        "advocacy flow starts at **Start here**."
    )
