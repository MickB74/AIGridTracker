"""
Newsletter signup widget — reused in the sidebar and after downloadable
outputs. Email capture is always optional (never gates a download); rows land
in data/analytics/subscribers.csv via src/services/tracking.py.
"""

import streamlit as st

from src.services.tracking import add_subscriber


def render_newsletter_signup(source: str, compact: bool = False) -> None:
    """One email field + subscribe button. `source` tags where the signup
    happened (sidebar, start_here, ...); keys derive from it, so each
    placement on a page needs a distinct source."""
    if not compact:
        st.markdown("#### 📬 The GridWatch Dispatch")
    st.caption(
        "One email per week: new moratoriums, rate cases, and "
        "negotiation wins — filtered to your state. No spam, unsubscribe "
        "anytime."
    )
    with st.form(key=f"nl_form_{source}", clear_on_submit=True, border=False):
        email = st.text_input(
            "Email address",
            placeholder="you@example.com",
            key=f"nl_email_{source}",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button(
            "Subscribe", use_container_width=compact
        )
    if submitted:
        ok, msg = add_subscriber(
            email,
            state=st.session_state.get("my_state", ""),
            source=source,
        )
        (st.success if ok else st.error)(msg)
