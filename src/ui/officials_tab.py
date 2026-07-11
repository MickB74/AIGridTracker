import streamlit as st
import pandas as pd
from src.helpers import src_link
from src.services.officials import load_officials
from src.services.news import fetch_news
from src.services.reddit import load_reddit_corpus

def render_officials_tab():
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
        states = f3.multiselect("State / territory", sorted(odf.state_full.unique()),
                                default=[])
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

        stanced = view[view.stance.str.len() > 0]
        if not stanced.empty:
            st.markdown("**Documented stances in this view:**")
            for _, r in stanced.iterrows():
                src = f" ({src_link(r['stance_src'])})" if r["stance_src"] else ""
                st.markdown(f"- **{r['name']}** ({r['party']}, {r['office']}, "
                            f"{r['state_full']}): {r['stance']}{src}")

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
                                st.markdown(f"- [{n['title']}]({n['link']}) ({n['source']})")
                    with c_reddit:
                        st.markdown("**Community Sentiment (Reddit)**")
                        if cerr or not reddit_items:
                            st.caption(f"No recent local discussions found in snapshot matching '{state}'/'{abbr}'.")
                        else:
                            for r in reddit_items:
                                st.markdown(f"- [{r['title']}]({r['link']}) (r/{r['subreddit']})")
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
    st.markdown('</div>', unsafe_allow_html=True)
