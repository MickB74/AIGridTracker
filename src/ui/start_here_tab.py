"""
Start Here wizard — a guided flow for someone who just learned a data center
is proposed near them. Five steps on one page (progressive disclosure, no
routing), ending in a downloadable action pack. Reuses the shared impact
model, the meeting-brief builder, and existing registries (DC_SITES_DF LLC
attribution, MORATORIUM_OUTCOMES, STATE_PUCS_DF).
"""

import streamlit as st
from src.constants import (
    PROJECT_STAGES, STATE_GRID_PROFILES, STATE_PUCS_DF, MORATORIUMS_DF,
    MORATORIUM_OUTCOMES, DC_SITES_DF, OPERATORS_DF,
)
from src.impact_model import estimate_facility_impact, INVESTMENT_USD_PER_MW
from src.briefs import build_meeting_brief, build_meeting_brief_data
from src.pdf_pack import build_action_pack_pdf

_UNKNOWN_LLC = "I don't know — I only have an LLC or company name from a filing"


def render_start_here_tab():
    st.subheader("🚨 A data center was proposed near me — start here")
    st.caption(
        "Five quick steps: your situation → who's behind it → what it costs "
        "you → what to do this week → a downloadable action pack for your "
        "next meeting."
    )

    # ── Step 1 — your situation ────────────────────────────────────────── #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### Step 1 — Your situation")
    c1, c2 = st.columns([1, 2])
    with c1:
        _sidebar_state = st.session_state.get("my_state", "All states")
        _states = sorted(STATE_GRID_PROFILES.keys())
        _idx = _states.index(_sidebar_state) if _sidebar_state in _states else 0
        state = st.selectbox("Your state", _states, index=_idx, key="sh_state")
    with c2:
        stage = st.radio(
            "Where does the project stand?",
            list(PROJECT_STAGES.keys()),
            key="sh_stage",
        )
    stage_info = PROJECT_STAGES[stage]
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Step 2 — who's really behind it ────────────────────────────────── #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### Step 2 — Who's really behind it")
    _ops = sorted(OPERATORS_DF["operator"].unique().tolist())
    who = st.selectbox(
        "Who's building it?", [_UNKNOWN_LLC] + _ops, key="sh_who",
        help="Developers usually file under single-purpose LLCs. If you only "
             "have a shell-company name from a deed or permit, pick the first "
             "option and we'll try to unmask it.")

    operator_for_brief = "Unknown / not listed"
    if who == _UNKNOWN_LLC:
        llc_q = st.text_input(
            "Name on the deed, permit, or utility filing",
            key="sh_llc", placeholder="e.g. Jet Stream LLC, Greasewood LLC")
        if llc_q:
            _mask = (
                DC_SITES_DF["filing_llc"].str.contains(
                    llc_q, case=False, na=False, regex=False)
                | DC_SITES_DF["operator"].str.contains(
                    llc_q, case=False, na=False, regex=False)
                | DC_SITES_DF["owner"].str.contains(
                    llc_q, case=False, na=False, regex=False)
            )
            _hits = DC_SITES_DF[_mask]
            if not _hits.empty:
                _found_ops = _hits["operator"].unique().tolist()
                st.success(
                    f"**Match.** \"{llc_q}\" appears in our site registry, "
                    f"linked to: **{', '.join(_found_ops)}**."
                )
                st.dataframe(
                    _hits[["operator", "owner", "tenant", "location",
                           "state", "filing_llc"]].drop_duplicates(),
                    use_container_width=True, hide_index=True)
                if len(_found_ops) == 1 and _found_ops[0] in _ops:
                    operator_for_brief = _found_ops[0]
            else:
                st.warning(
                    f"No match for \"{llc_q}\" in our registry — that doesn't "
                    "mean it's not a data center. Here's how to unmask an LLC "
                    "yourself:"
                )
                st.markdown(
                    "- **County recorder:** pull the deed — note the LLC's "
                    "mailing address and the law firm that filed it\n"
                    "- **Secretary of State business search:** look up the LLC; "
                    "the registered agent or organizer often traces to the real "
                    "developer\n"
                    "- **Utility filings:** ask your utility or PUC whether a "
                    "large-load interconnection request covers the parcel\n"
                    "- **Planning department:** records requests for "
                    "pre-application meetings usually name the actual company"
                )
    else:
        operator_for_brief = who
        _op_row = OPERATORS_DF[OPERATORS_DF["operator"] == who]
        if not _op_row.empty:
            _op = _op_row.iloc[0]
            st.markdown(
                f"**{who}** — tier: {_op.get('tier', 'N/A')} · "
                f"owner: {_op.get('owner', 'N/A')} · "
                f"model: {_op.get('model', 'N/A')}"
            )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Step 3 — what it will cost you ─────────────────────────────────── #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### Step 3 — What it will cost your community")
    mw = st.slider(
        "Announced or estimated size (MW)", 50, 1000, 200, 50, key="sh_mw",
        help="If you only know acreage: a typical campus runs 50-100 MW per "
             "large building; mid-size campuses are 200-500 MW.")

    imp = estimate_facility_impact(mw, state)
    # Same simplified rate-impact model as the Local Impact Calculator:
    # $2M/MW of grid upgrades spread over ~5M households for 20 years.
    _upgrade_per_home_yr = mw * INVESTMENT_USD_PER_MW / 5_000_000 / 20

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Electricity", f"{imp['annual_twh']:.1f} TWh/yr",
              f"{imp['homes_equiv']:,.0f} homes' worth")
    m2.metric("Water", f"{imp['annual_water_mgal']:,.0f}M gal/yr",
              f"{imp['water_stress']} stress region")
    m3.metric("Your bill risk", f"${_upgrade_per_home_yr:.0f}/yr",
              "per household if ratepayers fund upgrades")
    m4.metric("CBA target", f"${imp['data_dividend_usd']/1e6:.1f}M/yr",
              "2% of est. investment")
    st.caption(
        "Rough planning numbers — tune cooling type, grid-upgrade costs, and "
        "more in the full **Local Impact Calculator** (Learn & simulate tab)."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Step 4 — what to do at this stage ──────────────────────────────── #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f"### Step 4 — {stage_info['emoji']} What to do this week")
    st.info(stage_info["headline"])
    for _move in stage_info["moves"]:
        st.markdown(f"- {_move}")

    # In-state pushback context + precedents from real fights
    _abbrev_row = STATE_PUCS_DF[STATE_PUCS_DF["state"] == state]
    _abbrev = _abbrev_row.iloc[0]["abbrev"] if not _abbrev_row.empty else ""
    _local_moras = MORATORIUMS_DF[MORATORIUMS_DF["state"] == _abbrev]
    if not _local_moras.empty:
        st.warning(
            f"**You are not alone:** {len(_local_moras)} tracked "
            f"moratorium/pushback effort(s) in {state}. See the map in "
            "**Community & backlash**."
        )

    _local_cases = [c for c in MORATORIUM_OUTCOMES if c["state"] == _abbrev]
    _shown = _local_cases if _local_cases else [
        c for c in MORATORIUM_OUTCOMES
        if c["locality"] in ("The Dalles", "Groton", "Cheyenne")
    ]
    st.markdown("**Precedents worth citing:**")
    for _case in _shown:
        with st.expander(
                f"{_case['locality']}, {_case['state']} — {_case['headline']} "
                f"({_case['category']})"):
            st.markdown(_case["outcome"])

    if not _abbrev_row.empty:
        _puc = _abbrev_row.iloc[0]
        st.markdown(
            f"**Your regulator:** {_puc['name']} — "
            f"[website]({_puc['website']}) · "
            f"[file a complaint]({_puc['complaint']})"
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Step 5 — your action pack ──────────────────────────────────────── #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### Step 5 — Download your action pack")
    st.caption(
        "One print-ready PDF: your situation, the operator intel, impact "
        "numbers, meeting strategy, CBA targets, questions to ask, and your "
        "this-week checklist. Print it and bring it."
    )

    _brief_data = build_meeting_brief_data(
        state, operator_for_brief, stage_info["meeting_type"], mw)
    pack_pdf = build_action_pack_pdf(state, stage, stage_info, _brief_data)

    _checklist = "".join(f"  [ ] {_m}\n" for _m in stage_info["moves"])
    pack_txt = (
        f"START-HERE ACTION PACK\n"
        f"{'='*60}\n"
        f"SITUATION: {stage}\n"
        f"{stage_info['headline']}\n\n"
        f"THIS WEEK\n"
        f"{_checklist}\n"
        + build_meeting_brief(state, operator_for_brief,
                              stage_info["meeting_type"], mw)
    )

    _fname = f"gridwatch_action_pack_{state.replace(' ', '_')}"
    d1, d2 = st.columns([1, 1])
    d1.download_button(
        "📥 Download action pack (PDF)",
        pack_pdf,
        f"{_fname}.pdf",
        "application/pdf",
        key="sh_download",
        type="primary",
        use_container_width=True,
    )
    d2.download_button(
        "Plain text version",
        pack_txt,
        f"{_fname}.txt",
        "text/plain",
        key="sh_download_txt",
        use_container_width=True,
    )

    st.info(
        "**Go deeper:** model CBA clauses and the data dividend calculator in "
        "**Negotiation toolkit** · rate-impact background in **Your utility "
        "bill** · your officials and PUC in **States & officials**."
    )
    st.markdown('</div>', unsafe_allow_html=True)
