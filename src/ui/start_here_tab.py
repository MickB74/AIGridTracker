"""
Start Here wizard — a guided flow for someone who just learned a data center
is proposed near them. Five steps on one page (progressive disclosure, no
routing), ending in a downloadable action pack. Reuses the shared impact
model, the meeting-brief builder, and existing registries (DC_SITES_DF LLC
attribution, MORATORIUM_OUTCOMES, STATE_PUCS_DF).
"""

from datetime import date, timedelta

import streamlit as st
from src.constants import (
    PROJECT_STAGES, STATE_GRID_PROFILES, STATE_PUCS_DF, MORATORIUMS_DF,
    MORATORIUM_OUTCOMES, DC_SITES_DF, OPERATORS_DF, CBA_BENCHMARKS,
    OUTREACH_TIPS,
)
from src.alerts import alerts_for_state
from src.impact_model import estimate_facility_impact, INVESTMENT_USD_PER_MW
from src.briefs import build_meeting_brief, build_meeting_brief_data
from src.pdf_pack import build_action_pack_pdf, build_flyer_pdf
from src.scripts_letters import (
    build_comment_scripts, build_letters, build_social_posts,
)
from src.site_builder import build_campaign_site
from src.services.tracking import log_event
from src.ui.newsletter import render_newsletter_signup
from src.ui import share

_UNKNOWN_LLC = "I don't know — I only have an LLC or company name from a filing"


# Inputs worth carrying in a link. Deliberately not everything — the point is
# that a neighbour opens the same situation, not that every scratch field is
# reproduced. Restore runs before any widget below is created; see share.py.
# Third element guards the value against what the widget will actually
# accept: a link arriving with a state Streamlit has never heard of would
# otherwise take the tab down for whoever opened it.
SHARE_SPEC = {
    "state": ("sh_state", "str", lambda: STATE_GRID_PROFILES.keys()),
    "stage": ("sh_stage", "str", lambda: PROJECT_STAGES.keys()),
    "mw": ("sh_mw", "int", (50, 1000)),
    "who": ("sh_who", "str",
            lambda: [_UNKNOWN_LLC] + OPERATORS_DF["operator"].unique().tolist()),
    "llc": ("sh_llc", "str"),
    "hearing": ("sh_hearing", "date"),
}


def render_start_here_tab():
    share.restore(st, SHARE_SPEC, "start_here")
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
        hearing_date = st.date_input(
            "Next hearing or vote (if known)", value=None,
            min_value=date.today(), key="sh_hearing",
            help="Turns your checklist into a dated countdown plan and "
                 "pre-fills the flyer and social posts.")
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

    st.markdown("**What similar communities actually won:**")
    for _b in CBA_BENCHMARKS:
        st.markdown(
            f"- **{_b['community']}, {_b['state']}** ({_b['company']}) — "
            f"{_b['won']}")
    st.caption(
        "Your CBA target above isn't aspirational — it's in line with what "
        "organized communities have negotiated. Scale the ask to the MW."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Placed here rather than at the end: this is the point where the page is
    # worth forwarding — the numbers are on screen and specific to the reader's
    # town. Asking someone to share before they have seen anything is asking
    # them to vouch for a link they have not read.
    share.render(
        st, SHARE_SPEC,
        caption=(
            "Opens this page with your state, project size and stage already "
            "filled in — so a neighbour sees the same numbers instead of "
            "starting from a blank form. Paste it into a group chat, a "
            "Nextdoor post, or an email to your council member."
        ))

    # ── Step 4 — what to do at this stage ──────────────────────────────── #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f"### Step 4 — {stage_info['emoji']} What to do this week")
    st.info(stage_info["headline"])

    # With a hearing date, spread the moves across the runway (last due
    # 2 days before the hearing); without one, show the undated list.
    dated_moves = None
    if hearing_date:
        _days = (hearing_date - date.today()).days
        _n = len(stage_info["moves"])
        dated_moves = []
        for _i, _move in enumerate(stage_info["moves"]):
            _offset = max(1, round((_i + 1) * max(_days - 2, 1) / _n))
            _due = date.today() + timedelta(days=min(_offset, max(_days - 2, 1)))
            dated_moves.append((f"{_due:%b %d}", _move))
        st.markdown(
            f"**⏳ {_days} days until your hearing** — your countdown plan:")
        for _due, _move in dated_moves:
            st.markdown(f"- **By {_due}** — {_move}")
    else:
        for _move in stage_info["moves"]:
            st.markdown(f"- {_move}")

    # In-state pushback context + precedents from real fights
    _abbrev_row = STATE_PUCS_DF[STATE_PUCS_DF["state"] == state]
    _abbrev = _abbrev_row.iloc[0]["abbrev"] if not _abbrev_row.empty else ""
    # A lapsing moratorium near you is more actionable than the fact that one
    # exists — it is a dated deadline, and the community that won the pause is
    # usually the last to hear it is ending.
    for _alert in alerts_for_state(_abbrev):
        if _alert["severity"] == "expired":
            st.error(f"⏰ **{_alert['title']}** — {_alert['body']}")
        else:
            st.warning(f"⏰ **{_alert['title']}** — {_alert['body']}")

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
    st.caption(
        "Open the source links before you quote one of these — a precedent "
        "you cannot cite is worse than none at all."
    )
    for _case in _shown:
        with st.expander(
                f"{_case['locality']}, {_case['state']} — {_case['headline']} "
                f"({_case['category']})"):
            st.markdown(_case["outcome"].replace("$", "\\$"))
            _srcs = _case.get("sources") or []
            if _srcs:
                st.caption(
                    " · ".join(f"[Source {_i}]({_u})"
                               for _i, _u in enumerate(_srcs, 1))
                    + f" · verified {_case.get('as_of') or '—'}"
                )
            else:
                st.warning("Unverified — do not cite this one.")

    if not _abbrev_row.empty:
        _puc = _abbrev_row.iloc[0]
        st.markdown(
            f"**Your regulator:** {_puc['name']} — "
            f"[website]({_puc['website']}) · "
            f"[file a complaint]({_puc['complaint']})"
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Step 5 — your action kit ───────────────────────────────────────── #
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### Step 5 — Your action kit")
    st.caption(
        "Everything below is pre-filled with your numbers: the action-pack "
        "PDF (now with your speech, letters, and outreach playbook), a "
        "hand-out flyer with a petition sheet, ready-to-paste social posts, "
        "and a one-page campaign website you can host for free."
    )

    _puc_name = (_abbrev_row.iloc[0]["name"] if not _abbrev_row.empty
                 else "Your state public utility commission")
    _puc_complaint = (_abbrev_row.iloc[0]["complaint"]
                      if not _abbrev_row.empty else "")
    _hearing_str = f"{hearing_date:%A, %B %d}" if hearing_date else ""

    _brief_data = build_meeting_brief_data(
        state, operator_for_brief, stage_info["meeting_type"], mw)
    _scripts_en = build_comment_scripts(
        state, mw, imp, _upgrade_per_home_yr, operator_for_brief, "en")
    _letters = build_letters(
        state, operator_for_brief, mw, _puc_name, _puc_complaint)
    _posts = build_social_posts(
        state, mw, imp, _upgrade_per_home_yr, operator_for_brief,
        _hearing_str)

    pack_pdf = build_action_pack_pdf(
        state, stage, stage_info, _brief_data,
        dated_moves=dated_moves, scripts=_scripts_en, letters=_letters,
        social_posts=_posts, outreach_tips=OUTREACH_TIPS)

    if dated_moves:
        _checklist = "".join(f"  [ ] By {_d} — {_m}\n"
                             for _d, _m in dated_moves)
    else:
        _checklist = "".join(f"  [ ] {_m}\n" for _m in stage_info["moves"])
    _letters_txt = "\n\n".join(
        f"{'-'*60}\n{_l['title'].upper()}\nTo: {_l['to']}\nRe: {_l['re']}"
        f"\n\n{_l['body']}" for _l in _letters)
    _topics_txt = "\n\n".join(f"[{_t}]\n{_s}"
                              for _t, _s in _scripts_en["topics"])
    pack_txt = (
        f"START-HERE ACTION PACK\n"
        f"{'='*60}\n"
        f"SITUATION: {stage}\n"
        f"{stage_info['headline']}\n\n"
        f"THIS WEEK\n"
        f"{_checklist}\n"
        + build_meeting_brief(state, operator_for_brief,
                              stage_info["meeting_type"], mw)
        + f"\n{'='*60}\nYOUR 2-MINUTE PUBLIC COMMENT\n{'='*60}\n"
        + _scripts_en["main"]
        + f"\n\n30-SECOND TOPIC SCRIPTS\n\n{_topics_txt}\n\n"
        + f"{'='*60}\nREADY-TO-SEND LETTERS\n{'='*60}\n\n{_letters_txt}\n"
    )

    _fname = f"gridwatch_action_pack_{state.replace(' ', '_')}"
    _pack_meta = {"state": state, "stage": stage,
                  "operator": operator_for_brief, "mw": mw}
    d1, d2 = st.columns([1, 1])
    d1.download_button(
        "📥 Download action pack (PDF)",
        pack_pdf,
        f"{_fname}.pdf",
        "application/pdf",
        key="sh_download",
        type="primary",
        use_container_width=True,
        on_click=log_event,
        args=("action_pack_download",),
        kwargs={"fmt": "pdf", **_pack_meta},
    )
    d2.download_button(
        "Plain text version",
        pack_txt,
        f"{_fname}.txt",
        "text/plain",
        key="sh_download_txt",
        use_container_width=True,
        on_click=log_event,
        args=("action_pack_download",),
        kwargs={"fmt": "txt", **_pack_meta},
    )

    # -- speak: 2-minute comment script -------------------------------- #
    with st.expander("🎤 Your 2-minute public comment (pre-filled)"):
        _lang = st.radio("Language", ["English", "Español"],
                         horizontal=True, key="sh_script_lang")
        _scripts_show = (_scripts_en if _lang == "English" else
                         build_comment_scripts(state, mw, imp,
                                               _upgrade_per_home_yr,
                                               operator_for_brief, "es"))
        st.text_area("Read at a normal pace — about two minutes. Fill in "
                     "your name and practice once out loud.",
                     _scripts_show["main"], height=340, key="sh_script_txt")
        st.markdown("**30-second topic scripts** — assign one per speaker "
                    "so ten neighbors make ten different arguments:")
        for _t, _s in _scripts_show["topics"]:
            st.markdown(f"**{_t}:** {_s}")

    # -- send: ready-to-send letters ------------------------------------ #
    with st.expander("✉️ Ready-to-send letters (records request · PUC · "
                     "council)"):
        st.caption("Replace the [BRACKETED] placeholders and send. All "
                   "three are also in the action-pack PDF, one per page.")
        for _i, _l in enumerate(_letters):
            st.markdown(f"**{_l['title']}**  \nTo: {_l['to']}  \n"
                        f"Re: {_l['re']}")
            st.text_area(_l["title"], _l["body"], height=260,
                         key=f"sh_letter_{_i}", label_visibility="collapsed")

    # -- post: social media playbook ------------------------------------ #
    with st.expander("📣 Post it — Nextdoor, Ring, Facebook & more"):
        st.caption("Copy-paste posts with your numbers filled in — replace "
                   "the [BRACKETS]. Then the platform playbook.")
        for _platform, _post in _posts.items():
            st.markdown(f"**{_platform}**")
            st.text_area(_platform, _post, height=140,
                         key=f"sh_post_{_platform}",
                         label_visibility="collapsed")
        st.markdown("---")
        for _entry in OUTREACH_TIPS:
            st.markdown(f"**{_entry['platform']}**")
            for _tip in _entry["tips"]:
                st.markdown(f"- {_tip}")

    # -- rally: flyer, petition sheet, campaign site --------------------- #
    st.markdown("#### 🪧 Rally your neighbors")
    r1, r2, r3 = st.columns([1.2, 1.2, 0.8])
    _meet_when = r1.text_input(
        "Meeting date & time",
        value=(f"{hearing_date:%A, %B %d} · 6:30 PM" if hearing_date else ""),
        placeholder="Tuesday, Aug 12 · 6:30 PM", key="sh_meet_when")
    _meet_where = r2.text_input(
        "Location", placeholder="Town Hall, 123 Main St",
        key="sh_meet_where")
    _flyer_lang = r3.radio("Flyer language", ["English", "Español"],
                           key="sh_flyer_lang")
    flyer_pdf = build_flyer_pdf(
        state, mw, imp, _upgrade_per_home_yr,
        meeting_when=_meet_when, meeting_where=_meet_where,
        lang="es" if _flyer_lang == "Español" else "en")
    f1, f2 = st.columns([1, 1])
    f1.download_button(
        "🪧 Flyer + petition sheet (PDF)",
        flyer_pdf,
        f"gridwatch_flyer_{state.replace(' ', '_')}.pdf",
        "application/pdf",
        key="sh_flyer_dl",
        use_container_width=True,
        on_click=log_event,
        args=("flyer_download",),
        kwargs={"lang": _flyer_lang, **_pack_meta},
    )

    with st.expander("🌐 Your campaign website (free to host)"):
        st.caption(
            "A complete one-page site with your numbers baked in — no "
            "coding needed. Download `index.html`, then drag it onto "
            "**Netlify Drop** (netlify.com/drop) or upload to **GitHub "
            "Pages** — both free — and share the link in every post."
        )
        s1, s2 = st.columns([1, 1])
        _group = s1.text_input(
            "Group name", placeholder="Smith County Residents for "
            "Responsible Development", key="sh_site_group")
        _contact = s2.text_input(
            "Contact email (shown on the site)",
            placeholder="ourgroup@gmail.com", key="sh_site_email")
        _site_html = build_campaign_site(
            state, mw, imp, _upgrade_per_home_yr,
            group_name=_group, contact_email=_contact,
            meeting_when=_meet_when, meeting_where=_meet_where,
            operator=operator_for_brief)
        st.download_button(
            "🌐 Download your site (index.html)",
            _site_html,
            "index.html",
            "text/html",
            key="sh_site_dl",
            use_container_width=True,
            on_click=log_event,
            args=("campaign_site_download",),
            kwargs=_pack_meta,
        )

    render_newsletter_signup("start_here")

    st.info(
        "**Go deeper:** model CBA clauses and the data dividend calculator in "
        "**Negotiation toolkit** · rate-impact background in **Your utility "
        "bill** · sourced health-risk evidence (printable) in **Learn & "
        "simulate → Health risks** · your officials and PUC in **States & "
        "officials**."
    )
    st.markdown('</div>', unsafe_allow_html=True)
