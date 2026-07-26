import re
import html as _html
import streamlit as st
import pandas as pd
from src.helpers import src_link
from src.constants import STATE_PUCS_DF, MORATORIUMS_DF, DC_SITES_DF
from src.local_officials import (
    build_lookup_links, covered_localities, curated, split_label,
    verification_note,
)
from src.services.officials import load_officials
from src.services.news import fetch_news
from src.services.openstates import fetch_state_legislators
from src.services.reddit import load_reddit_corpus
from src.services.secrets import load_local_secrets


# Abbrev -> full name, borrowed from the PUC registry so we don't add a
# fourth copy of the state list to the codebase.
def _abbrev_to_full() -> dict:
    try:
        return dict(zip(STATE_PUCS_DF["abbrev"], STATE_PUCS_DF["state"]))
    except Exception:                                              # noqa: BLE001
        return {}


def _resolve_latlon(locality: str, state: str):
    """Best-effort lat/lon for a locality, reusing coordinates the app already
    carries in the moratorium tracker and the site table. Returns None when the
    locality isn't in either — we then ask the user rather than guessing."""
    loc_k = (locality or "").strip().lower()
    st_k = (state or "").strip().upper()
    if not loc_k or not st_k:
        return None
    for df, col in ((MORATORIUMS_DF, "locality"), (DC_SITES_DF, "location")):
        try:
            m = df[(df[col].str.strip().str.lower() == loc_k)
                   & (df["state"].str.upper() == st_k)]
            if not m.empty:
                return float(m.iloc[0]["lat"]), float(m.iloc[0]["lon"])
        except Exception:                                          # noqa: BLE001
            continue
    return None


def render_local_officials():
    """Town/county officials — the layer closest to an actual land-use vote."""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🏛️ Your local officials — town & county")
    st.caption(
        "Land-use votes happen here, not in Congress. This section resolves in "
        "three tiers: hand-verified rosters for localities with an active "
        "data-center fight, a free state-legislator lookup, and directory links "
        "that work everywhere else.")

    a2f = _abbrev_to_full()
    f2a = {v: k for k, v in a2f.items()}
    labels = covered_localities()

    # Default the picker from the sidebar "My Community" selection.
    sidebar_state = st.session_state.get("my_state", "All states")
    sidebar_abbrev = st.session_state.get(
        "my_state_abbrev", f2a.get(sidebar_state, ""))
    default_idx = 0
    if sidebar_abbrev:
        for i, lb in enumerate(labels):
            if lb.endswith(f", {sidebar_abbrev}"):
                default_idx = i + 1
                break

    choice = st.selectbox(
        "Locality", ["— Not listed / somewhere else —"] + labels,
        index=default_idx, key="local_off_locality",
        help="Verified rosters exist for localities with an active fight. "
             "Pick the first option for anywhere else and you'll get "
             "directory links instead.")

    if choice.startswith("—"):
        locality, state = "", (sidebar_abbrev or "")
        st.text_input("Locality name (optional)", key="local_off_freetext",
                      placeholder="e.g. Beaver Dam")
        locality = st.session_state.get("local_off_freetext", "").strip()
        state_full = st.selectbox(
            "State", ["Select…"] + sorted(a2f.values()),
            index=(sorted(a2f.values()).index(sidebar_state) + 1
                   if sidebar_state in a2f.values() else 0))
        state = f2a.get(state_full, "")
    else:
        locality, state = split_label(choice)

    data = curated(locality, state)

    # ── Tier 1: verified bodies + people ────────────────────────────────────
    if data["bodies"] or data["officials"]:
        for b in data["bodies"]:
            with st.container(border=True):
                st.markdown(f"**{b['body']}** — {b['locality']}, {b['state']}")
                st.markdown(f"*What it decides:* {b['decides']}")
                c1, c2 = st.columns(2)
                c1.markdown(f"**Meets:** {b['meets'] or '—'}")
                c1.markdown(f"**Where:** {b['where'] or '—'}")
                c2.markdown(f"**Phone:** {b['phone'] or '—'}")
                c2.markdown(f"**Clerk / comment email:** {b['email'] or '—'}")
                st.markdown(f"**Public comment:** {b['comment_process']}")
                lc1, lc2 = st.columns(2)
                if b.get("agenda_url"):
                    lc1.markdown(f"[📅 Agendas & minutes]({b['agenda_url']})")
                if b.get("website"):
                    lc2.markdown(f"[🔗 Official page]({b['website']})")

        if data["officials"]:
            odf = pd.DataFrame(data["officials"])
            show = odf[["name", "role", "district", "email", "phone",
                        "stance", "source"]].copy()
            show["stance"] = show["stance"].replace(
                "", "Not recorded — ask them")
            st.dataframe(
                show, use_container_width=True, hide_index=True,
                column_config={
                    "name": st.column_config.TextColumn("Name"),
                    "role": st.column_config.TextColumn("Role"),
                    "district": st.column_config.TextColumn("District",
                                                            width="small"),
                    "email": st.column_config.TextColumn("Email", width="medium"),
                    "phone": st.column_config.TextColumn("Phone", width="small"),
                    "stance": st.column_config.TextColumn("Data-center stance"),
                    "source": st.column_config.LinkColumn("Verified from",
                                                          display_text="source"),
                })

            emails = [e for e in odf["email"].tolist() if e]
            if emails:
                st.markdown("**Copy-paste all emails:**")
                st.code(", ".join(emails), language=None)
            st.download_button(
                "⬇️ Download roster (CSV)",
                odf.to_csv(index=False).encode("utf-8"),
                file_name=f"{locality.replace(' ', '_')}_{state}_officials.csv",
                mime="text/csv", key="dl_local_officials")

            st.caption(
                "Provenance: " + verification_note(data["officials"])
                + " Nothing here is inferred — blank fields mean the official "
                "page didn't publish that detail. Rosters change with "
                "elections: click **source** to confirm before you send "
                "anything that matters.")
    elif locality or state:
        st.info(
            "**No verified roster for this locality yet.** Rather than show you "
            "names we haven't checked, here are the directories that will have "
            "them. (Search-engine snippets were wrong for 2 of the first 4 "
            "localities we validated, which is why this app won't repeat them.)")

    # ── Tier 3: directory links ─────────────────────────────────────────────
    # Always rendered, including before a state is picked — otherwise the
    # "not listed" path dead-ends. With no state we still have the national
    # county and USA.gov directories, which beat an empty panel.
    _has_curated = bool(data["bodies"] or data["officials"])
    with st.expander("🔎 Find officials for any town — directory links",
                     expanded=not _has_curated):
        if not state:
            st.caption("Pick your state above to add its municipal-league "
                       "directory to this list.")
        for lk in build_lookup_links(state, locality):
            st.markdown(f"**[{lk['label']}]({lk['url']})** — {lk['why']}")

    # ── Tier 2: OpenStates state legislators ────────────────────────────────
    with st.expander("🗳️ Your state legislators (free OpenStates lookup)"):
        st.caption(
            "OpenStates covers **state legislators and members of Congress "
            "only** — its API explicitly excludes mayors and governors, so this "
            "supplements the roster above rather than replacing it. These are "
            "the members who vote on preemption bills, NDA bans, and "
            "data-center tax exemptions.")
        key = load_local_secrets().get("openstates", "")
        key = st.text_input(
            "OpenStates API key", value=key, type="password",
            help="Free key from open.pluralpolicy.com. Also read from "
                 "OPENSTATES_API_KEY in your environment or .env.")
        ll = _resolve_latlon(locality, state)
        c1, c2 = st.columns(2)
        lat = c1.number_input("Latitude", value=float(ll[0]) if ll else 0.0,
                              format="%.4f")
        lng = c2.number_input("Longitude", value=float(ll[1]) if ll else 0.0,
                              format="%.4f")
        if ll:
            st.caption("Coordinates pre-filled from the app's own site data.")
        if st.button("Look up legislators", key="os_lookup"):
            if not key:
                st.warning("Add a free OpenStates API key to use this lookup.")
            elif lat == 0.0 and lng == 0.0:
                st.warning("Enter the coordinates of the proposed site.")
            else:
                rows, note = fetch_state_legislators(lat, lng, key)
                if rows:
                    st.dataframe(
                        pd.DataFrame(rows), use_container_width=True,
                        hide_index=True,
                        column_config={
                            "url": st.column_config.LinkColumn(
                                "Profile", display_text="OpenStates"),
                        })
                    st.caption(note)
                else:
                    st.warning(f"No results. {note}")

    st.info(
        "**Where this fits:** use the **Negotiation toolkit** to generate a "
        "meeting brief for the body above, and the **Start here** wizard to "
        "build a comment script sized to your hearing date. For rate and "
        "interconnection questions, the PUC directory below is the right venue "
        "— not your council.")
    st.markdown('</div>', unsafe_allow_html=True)


def render_officials_tab():
    render_local_officials()
    st.divider()
    st.subheader("Contact your officials — Congress & governors")
    st.caption("Every US senator, representative, and governor: party, official "
               "website, and contact page — a directory for reaching "
               "decision-makers on data-center policy, where much of the action "
               "(moratoriums, incentives, permitting) actually happens.")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    odf, ogen = load_officials()
    if odf.empty:
        st.warning("Couldn't load the officials directory.")
        st.caption(f"Detail: {ogen}")
    else:
        nS = (odf.office == "Senator").sum()
        nH = odf.office.isin(["Representative", "Delegate"]).sum()
        nG = (odf.office == "Governor").sum()
        st.info(
            f"**{nS} senators · {nH} House members · {nG} governors = "
            f"{len(odf)} officials.** Two honest limits: (1) **stances are only "
            "shown where documented** and cited — most officials have made no "
            "public data-center statement, so that column is usually blank; "
            "nothing is inferred. (2) Members **don't publish direct emails** — "
            "the Contact link opens their official webform. Roster: " + ogen + ".")

        f1, f2, f3 = st.columns([1.6, 1.4, 2])
        offices = f1.multiselect("Office", ["Senator", "Representative",
                                            "Delegate", "Governor"],
                                 default=["Senator", "Representative",
                                          "Delegate", "Governor"])
        parties = f2.multiselect("Party", sorted(odf.party.unique()),
                                 default=sorted(odf.party.unique()))
        # Default the state filter from the sidebar "My Community" pick first,
        # then fall back to the state selected in the profile module above
        # (studies_tab's selectbox, key="state_study_select") so a Wisconsin
        # profile also scopes this directory to Wisconsin officials.
        _sidebar_state = st.session_state.get("my_state", "All states")
        _studies_state = st.session_state.get("state_study_select", "Select State...")
        _focus_state = None
        if _sidebar_state != "All states" and _sidebar_state in odf.state_full.values:
            _focus_state = _sidebar_state
        elif _studies_state not in ("Select State...", None) and _studies_state in odf.state_full.values:
            _focus_state = _studies_state
        _default_states = [_focus_state] if _focus_state else []
        states = f3.multiselect("State / territory", sorted(odf.state_full.unique()),
                                default=_default_states)
        cbx1, cbx2 = st.columns(2)
        only_stance = cbx1.checkbox("Only officials with a documented "
                                    "data-center stance", value=False)
        ec_only = cbx2.checkbox("Only House Energy & Commerce members "
                                "(the committee with jurisdiction)", value=False)

        view = odf.copy()
        if offices:
            view = view[view.office.isin(offices)]
        if parties:
            view = view[view.party.isin(parties)]
        # Snapshot after office/party filters but BEFORE the state filter, so
        # federal (national-scope) champions can pass through the state filter
        # in the stances list below.
        view_pre_state = view.copy()
        if states:
            view = view[view.state_full.isin(states)]
        if only_stance:
            view = view[view.stance.str.len() > 0]
        if ec_only:
            view = view[view.get("committee", "") == "Energy & Commerce"]
        view = view.sort_values(["state_full", "office", "name"])

        q1, q2, q3 = st.columns(3)
        q1.metric("Officials shown", f"{len(view)}")
        q2.metric("House members",
                  f"{view.office.isin(['Representative','Delegate']).sum()}")
        q3.metric("With sourced stance", f"{(view.stance.str.len()>0).sum()}")

        show = view[["name", "office", "state_full", "district", "party",
                     "committee", "stance", "website", "contact"]].copy()
        st.dataframe(
            show, use_container_width=True, hide_index=True, height=560,
            column_config={
                "name": "Name", "office": "Office", "state_full": "State",
                "district": "District", "party": "Party",
                "committee": st.column_config.TextColumn("Committee"),
                "stance": st.column_config.TextColumn("Data-center stance (sourced)",
                                                      width="large"),
                "website": st.column_config.LinkColumn("Website", display_text="site"),
                "contact": st.column_config.LinkColumn("Contact", display_text="contact"),
            })

        def _stance_li(r):
            # Build one <li> of full-brightness HTML (the .stance-list CSS keeps
            # these bright rather than the muted body-prose gray). src_link()
            # returns markdown [name](url) — convert it to an anchor, and use the
            # &#36; entity for any '$' so Streamlit doesn't LaTeX-render it.
            src = ""
            if r["stance_src"]:
                anchor = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                                r'<a href="\2" target="_blank">\1</a>',
                                src_link(r["stance_src"]))
                src = f" ({anchor})"
            stance = _html.escape(r["stance"]).replace("$", "&#36;")
            return (f"<li><strong>{_html.escape(r['name'])}</strong> "
                    f"({_html.escape(r['party'])}, {_html.escape(r['office'])}, "
                    f"{_html.escape(r['state_full'])}): {stance}{src}</li>")

        def _render_stances(df):
            lis = "".join(_stance_li(r) for _, r in df.iterrows())
            st.markdown(f'<ul class="stance-list">{lis}</ul>',
                        unsafe_allow_html=True)

        stanced = view[view.stance.str.len() > 0]
        if not stanced.empty:
            st.markdown("**Documented stances in this view:**")
            _render_stances(stanced)

        # Federal champions: members of Congress whose stance is a national
        # standard (e.g. the Ratepayer Protection Act). Their stances apply
        # everywhere, so surface them even when a state filter would hide them.
        FEDERAL_OFFICES = ("Senator", "Representative", "Delegate")
        federal_stanced = view_pre_state[
            (view_pre_state.stance.str.len() > 0)
            & (view_pre_state.office.isin(FEDERAL_OFFICES))
        ]
        if ec_only:
            federal_stanced = federal_stanced[
                federal_stanced.get("committee", "") == "Energy & Commerce"]
        # Drop any already listed above (avoids duplicates when no state filter
        # is active and the federal members are already in `stanced`).
        already_shown = set(zip(stanced["name"], stanced["state_full"]))
        federal_extra = federal_stanced[~federal_stanced.apply(
            lambda r: (r["name"], r["state_full"]) in already_shown, axis=1)] \
            if not federal_stanced.empty else federal_stanced
        if not federal_extra.empty:
            st.markdown("**Federal champions (national scope — apply to every state):**")
            _render_stances(federal_extra)

        # State-specific active issues tracker
        st.divider()
        if states:
            st.markdown("### 🔍 Active local data center issues")
            # Build mapping from state_full to state abbreviation
            state_to_abbr = dict(zip(odf.state_full, odf.state))
            
            for state in states[:3]:
                abbr = state_to_abbr.get(state, "")
                news_query = f'"data center" "{state}" (noise OR water OR rates OR zoning OR moratorium OR opposition)'
                news, err = fetch_news(news_query, limit=5)
                
                today = pd.Timestamp.now().strftime("%Y-%m-%d")
                corpus, cerr = load_reddit_corpus(today)
                reddit_items = []
                if not corpus.empty:
                    # Filter matching state name or state abbreviation boundary
                    sub = corpus[corpus.title.str.contains(state, case=False, na=False) | 
                                 corpus.title.str.contains(rf"\b{abbr}\b", case=True, na=False, regex=True)]
                    reddit_items = [{"title": r.title, "link": r.link, "subreddit": r.subreddit} 
                                    for r in sub.head(5).itertuples()]

                with st.expander(f"📰 Active issues in {state} (News & Reddit)", expanded=True):
                    c_news, c_reddit = st.columns(2)
                    with c_news:
                        st.markdown("**Latest Local News**")
                        if err or news is None:
                            st.caption(f"Error fetching news: {err or 'no response'}")
                        elif not news:
                            st.caption(f"No recent local news headlines found matching '{state}' issues.")
                        else:
                            for n in news:
                                t = n['title'].replace('$', '\\$')
                                st.markdown(f"- [{t}]({n['link']}) ({n['source']})")
                    with c_reddit:
                        st.markdown("**Community Sentiment (Reddit)**")
                        if cerr or not reddit_items:
                            st.caption(f"No recent local discussions found in snapshot matching '{state}'/'{abbr}'.")
                        else:
                            for r in reddit_items:
                                t = r['title'].replace('$', '\\$')
                                st.markdown(f"- [{t}]({r['link']}) (r/{r['subreddit']})")
            if len(states) > 3:
                st.warning("Showing active issues for the first 3 selected states only to optimize speed.")
        else:
            st.caption("💡 **Tip:** Select one or more states in the **State / territory** filter above to view live active news & Reddit issues for those states.")

        st.caption("Sources: official [Senate contact list]"
                   "(https://www.senate.gov/general/contact_information/senators_cfm.xml)"
                   " · [House member data]"
                   "(https://unitedstates.github.io/congress-legislators/) "
                   "(@unitedstates project) · [current US governors]"
                   "(https://en.wikipedia.org/wiki/List_of_current_United_States_governors)"
                   ". Governor URLs are official state pages. Verify before "
                   "outreach — rosters change with elections and appointments.")

        st.info(
            "**See also:** The **Data centers** tab has an interactive map of "
            "every tracked data center campus — filter by state to see which "
            "operators are building in your officials' districts. The "
            "**Negotiation toolkit** tab has model CBA clauses and a Data "
            "Dividend Calculator to bring to meetings.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------------ #
    # State PUC directory
    # ------------------------------------------------------------------ #
    st.divider()
    st.subheader("Your state Public Utility Commission (PUC)")
    st.caption(
        "PUCs approve rate cases, large-load tariffs, and interconnection "
        "rules — they decide whether data center costs land on residential "
        "bills. Every state has one. File a complaint or intervene in a "
        "rate case to make your voice heard.")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    puc_df = STATE_PUCS_DF.copy()

    # Sync the filter to the sidebar "My Community" state whenever it changes,
    # while still letting the user override the dropdown manually afterward.
    # (A multiselect with both default= and key= ignores default on reruns, so
    # a later sidebar change never propagates — hence the explicit sync.)
    _sidebar_state = st.session_state.get("my_state", "All states")
    if st.session_state.get("_puc_last_sidebar") != _sidebar_state:
        st.session_state["_puc_last_sidebar"] = _sidebar_state
        st.session_state["puc_state_filter"] = (
            [_sidebar_state]
            if _sidebar_state != "All states" and _sidebar_state in puc_df["state"].values
            else []
        )
    puc_filter = st.multiselect(
        "Filter by state", sorted(puc_df["state"].unique()),
        key="puc_state_filter",
        placeholder="All states — or pick yours")
    if puc_filter:
        puc_df = puc_df[puc_df["state"].isin(puc_filter)]

    st.dataframe(
        puc_df, use_container_width=True, hide_index=True,
        column_config={
            "state": st.column_config.TextColumn("State"),
            "abbrev": st.column_config.TextColumn("Abbrev.", width="small"),
            "name": st.column_config.TextColumn("Commission Name", width="large"),
            "website": st.column_config.LinkColumn("Website", display_text="site"),
            "complaint": st.column_config.LinkColumn(
                "File complaint / intervene", display_text="complaint"),
        })

    st.caption(
        f"Showing {len(puc_df)} of {len(STATE_PUCS_DF)} commissions. "
        "URLs are official state PUC pages. Complaint links open the "
        "consumer-assistance or formal-complaint portal — procedures "
        "vary by state. Nebraska (public power state) has a Power Review "
        "Board with no separate consumer-complaint portal, so its "
        "complaint cell is blank. Texas (PUCT) has deregulated retail but "
        "still regulates transmission and distribution rates.")

    st.info(
        "**How to use this:** When a data center developer applies for a "
        "large-load interconnection or a utility files a rate case to "
        "recover grid upgrade costs, you can intervene at your PUC. "
        "Filing a consumer complaint puts your concerns on the record. "
        "See the **Utility bill** tab for how wholesale costs flow to "
        "your bill, and the **Negotiation toolkit** for model rate-"
        "protection clauses.")
    st.markdown('</div>', unsafe_allow_html=True)
