"""Consulting tab — community data center negotiation services."""

import streamlit as st


def render_consulting_tab():
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #0A0E14 0%, #10151D 50%, #0A0E14 100%);
            border: 1px solid #28313F;
            border-radius: 14px;
            padding: 48px 40px;
            margin-bottom: 24px;
            color: #EAF0F7;
        ">
            <h1 style="
                font-size: 2.4rem;
                font-weight: 700;
                letter-spacing: -0.03em;
                margin: 0 0 12px 0;
                color: #EAF0F7;
            ">GridWatch Consulting</h1>
            <p style="
                font-size: 1.15rem;
                color: #C8D0DA;
                margin: 0 0 20px 0;
                max-width: 700px;
                line-height: 1.55;
            ">
                Data-driven negotiation support for communities facing data center
                development. We help you win better deals — and only get paid when you do.
            </p>
            <p style="
                display: inline-block;
                background: rgba(45, 212, 191, 0.14);
                border: 1px solid rgba(45, 212, 191, 0.3);
                border-radius: 999px;
                padding: 8px 16px;
                font-size: 0.9rem;
                color: #2DD4BF;
                font-weight: 600;
            ">Success-fee model — no results, no cost</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── The problem ─────────────────────────────────────────────────────── #

    st.markdown("## The problem")

    p1, p2 = st.columns(2)
    with p1:
        st.markdown(
            "A hyperscaler shows up with a \\$2B proposal, a team of lawyers, and "
            "promises of '500 construction jobs.' Your planning commission has 30 days "
            "to respond. The developer's hired consultants produce a glossy economic "
            "impact study. Your community has... a Facebook group and a lot of questions."
        )
    with p2:
        st.error(
            "**The asymmetry is the problem.** The developer knows exactly what your "
            "land, water, and grid capacity are worth to them. You don't. That's where "
            "we come in."
        )

    st.divider()

    # ── What we do ──────────────────────────────────────────────────────── #

    st.markdown("## What we deliver")

    s1, s2, s3 = st.columns(3)
    with s1:
        with st.container(border=True):
            st.markdown("### Impact analysis")
            st.markdown(
                "- Energy load modeling using real grid data (PJM, EIA-930)\n"
                "- Water consumption estimates by cooling type\n"
                "- Residential rate impact projections\n"
                "- Grid strain and reliability analysis\n"
                "- Counter-analysis to the developer's economic study"
            )

    with s2:
        with st.container(border=True):
            st.markdown("### Deal structuring")
            st.markdown(
                "- Custom Community Benefit Agreement drafting\n"
                "- Data Dividend fund design (the Alaska model)\n"
                "- Tax abatement analysis — what you're actually giving up\n"
                "- Clawback provisions and performance guarantees\n"
                "- Decommissioning bond sizing"
            )

    with s3:
        with st.container(border=True):
            st.markdown("### Hearing support")
            st.markdown(
                "- Expert testimony at planning and zoning hearings\n"
                "- Data presentations for public comment periods\n"
                "- Talking points for elected officials\n"
                "- Media briefing materials\n"
                "- Post-approval compliance monitoring"
            )

    st.divider()

    # ── How we get paid ─────────────────────────────────────────────────── #

    st.markdown("## How we get paid")

    st.markdown(
        "Communities shouldn't have to pay upfront to defend their own resources. "
        "We use a **success-fee model** that aligns our incentives with yours."
    )

    fee1, fee2, fee3 = st.columns(3)

    with fee1:
        with st.container(border=True):
            st.markdown("### Free")
            st.markdown("**Initial consultation**")
            st.markdown(
                "- 60-minute situation assessment\n"
                "- Preliminary impact estimate\n"
                "- Recommendation on whether a CBA is achievable\n"
                "- No obligation"
            )

    with fee2:
        with st.container(border=True):
            st.markdown("### Success fee")
            st.markdown("**Full engagement**")
            st.markdown(
                "- Small percentage of annual community benefits secured\n"
                "- Fee only applies to **new** benefits we help negotiate\n"
                "- Capped at a fair maximum — we're not the developer\n"
                "- If we don't improve the deal, you pay nothing"
            )

    with fee3:
        with st.container(border=True):
            st.markdown("### Alternative")
            st.markdown("**Flat project fee**")
            st.markdown(
                "- For communities that prefer fixed pricing\n"
                "- Scoped to specific deliverables\n"
                "- Payment milestones tied to project phases\n"
                "- Available for grant-funded engagements"
            )

    st.divider()

    # ── Track record / credibility ──────────────────────────────────────── #

    st.markdown("## Why communities trust us")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active opposition groups", "345+", "Across 37 states")
    c2.metric("Blocked/delayed projects", "$64B+", "Community wins nationwide")
    c3.metric("Bills filed (2026)", "300+", "In 30 states")
    c4.metric("CBA precedents tracked", "50+", "Real deals analyzed")

    st.info(
        "We built **AI GridWatch** — the open-source platform used by communities "
        "nationwide to understand data center impacts. The same data and models "
        "that power the free tool power our consulting analysis, with deeper "
        "customization for your specific situation."
    )

    st.divider()

    # ── Intake form ─────────────────────────────────────────────────────── #

    st.markdown("## Request a free consultation")
    st.markdown(
        "Tell us about your situation. We'll respond within 48 hours with a "
        "preliminary assessment and recommended next steps."
    )

    form_col1, form_col2 = st.columns(2)

    with form_col1:
        contact_name = st.text_input(
            "Your name *", key="lp_name",
            placeholder="Jane Smith",
        )
        contact_email = st.text_input(
            "Email *", key="lp_email",
            placeholder="jane@example.com",
        )
        st.text_input(
            "Phone (optional)", key="lp_phone",
            placeholder="(555) 123-4567",
        )
        community_name = st.text_input(
            "Community / municipality *", key="lp_community",
            placeholder="e.g. Springfield Township, OH",
        )

    with form_col2:
        st.selectbox(
            "Your role",
            [
                "Concerned resident",
                "Community organizer / activist",
                "Elected official",
                "Planning commission member",
                "Municipal staff",
                "Attorney representing community",
                "Journalist / researcher",
                "Other",
            ],
            key="lp_role",
        )
        st.text_input(
            "Developer (if known)", key="lp_developer",
            placeholder="e.g. Meta, Google, QTS, unknown",
        )
        st.selectbox(
            "Proposed facility size",
            ["Not sure yet", "Under 50 MW", "50-200 MW", "200-500 MW", "500+ MW", "Multiple facilities"],
            key="lp_size",
        )
        st.selectbox(
            "Where are you in the process?",
            [
                "Rumors / early stage — nothing filed yet",
                "Proposal submitted to planning commission",
                "Public comment period open",
                "Zoning / planning hearing scheduled",
                "Actively negotiating terms with developer",
                "Already approved — want to reopen or enforce terms",
                "State-level legislation effort",
            ],
            key="lp_timeline",
        )

    st.markdown("**What are your biggest concerns?**")
    concern_cols = st.columns(4)
    with concern_cols[0]:
        c_water = st.checkbox("Water usage", key="lp_c_water")
        c_noise = st.checkbox("Noise", key="lp_c_noise")
    with concern_cols[1]:
        c_grid = st.checkbox("Grid strain / rates", key="lp_c_grid")
        c_tax = st.checkbox("Tax giveaways", key="lp_c_tax")
    with concern_cols[2]:
        c_jobs = st.checkbox("Job promises", key="lp_c_jobs")
        c_env = st.checkbox("Environmental justice", key="lp_c_env")
    with concern_cols[3]:
        c_property = st.checkbox("Property values", key="lp_c_property")
        c_other = st.checkbox("Other", key="lp_c_other")

    st.text_area(
        "Tell us more about your situation",
        key="lp_situation",
        placeholder=(
            "What's happening in your community? Any upcoming deadlines (hearings, "
            "votes, comment periods)? What has the developer promised? What are "
            "residents most worried about?"
        ),
        height=150,
    )

    st.selectbox(
        "How did you hear about us?",
        [
            "GridWatch AI tool",
            "Community organizer referral",
            "News article",
            "Social media",
            "Search engine",
            "Other",
        ],
        key="lp_heard",
    )

    if st.button("Request free consultation", type="primary", key="lp_submit"):
        if not contact_name or not contact_email or not community_name:
            st.error("Please fill in your name, email, and community name.")
        else:
            concerns = []
            if c_water: concerns.append("water")
            if c_noise: concerns.append("noise")
            if c_grid: concerns.append("grid/rates")
            if c_tax: concerns.append("tax giveaways")
            if c_jobs: concerns.append("jobs")
            if c_env: concerns.append("environmental justice")
            if c_property: concerns.append("property values")
            if c_other: concerns.append("other")

            st.success(
                f"**Thank you, {contact_name}!** We'll reach out within 48 hours "
                f"to schedule your free consultation about the situation in "
                f"**{community_name}**. Check your inbox at **{contact_email}**."
            )
            st.balloons()

            with st.expander("What to expect next"):
                st.markdown(
                    "1. **Within 48 hours:** We'll email you to schedule a 60-minute "
                    "   introductory call.\n"
                    "2. **On the call:** We'll assess your situation, review any "
                    "   documents you have (developer proposals, tax abatement "
                    "   applications, zoning filings), and give you an honest "
                    "   assessment of what's achievable.\n"
                    "3. **After the call:** If there's a fit, we'll propose a scope "
                    "   of work with a clear success-fee structure. If not, we'll "
                    "   point you to the best free resources for your situation.\n\n"
                    "**In the meantime:** Explore the free AI GridWatch toolkit — "
                    "the Data Dividend Calculator and Model CBA Clauses on the "
                    "Negotiation Toolkit tab are a great place to start."
                )

    st.divider()
    st.caption(
        "GridWatch Consulting is not a law firm and does not provide legal advice. "
        "We recommend engaging local counsel for all legally binding agreements. "
        "Our role is analytical, strategic, and advisory."
    )
