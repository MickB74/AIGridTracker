import streamlit as st
import urllib.parse
import pandas as pd
from src.constants import NEWS_THEMES
from src.services.news import fetch_news, fetch_community_stories, rank_stories
from src.services.reddit import load_reddit_corpus, _reddit_query


def _age_label(age_days):
    """Human 'x days ago' from an integer age; blank if unknown."""
    if age_days is None:
        return ""
    if age_days <= 0:
        return "today"
    if age_days == 1:
        return "yesterday"
    return f"{age_days} days ago"


def render_news_feed_tab():
    st.subheader("📰 News — data centers & communities")
    st.caption("A live, automated read on what's happening: the top stories of "
               "the week ranked by impact, plus a browsable news + Reddit feed by "
               "theme. Headlines come from an automated search — follow each link "
               "to the original outlet.")

    # ── Top stories (heuristic ranking) ─────────────────────────────────── #
    st.markdown("#### 🔝 Top stories this week")
    st.caption(
        "Ranked automatically from the last 7 days by how fresh the story is and "
        "how high-stakes the headline reads — lawsuits, moratoriums, and rate "
        "hikes weigh most. This is a keyword heuristic, not editorial judgment.")

    stories, serr = fetch_community_stories(limit=40, max_age_days=7)
    gn_url = ("https://news.google.com/search?q="
              + urllib.parse.quote("data center community impact"))

    if serr or not stories:
        st.info("Couldn't pull this week's stories right now (offline or the news "
                f"feed was unreachable). [Open the search on Google News]({gn_url}).")
        if serr:
            st.caption(f"Detail: {serr}")
    else:
        top = rank_stories(stories, top_n=5)
        for i, s in enumerate(top, 1):
            with st.container(border=True):
                st.markdown(
                    f"**{i}. {s['angle_emoji']} [{s['title']}]({s['link']})**")
                meta = " · ".join(
                    x for x in (s.get("source"), _age_label(s.get("age_days")))
                    if x)
                st.caption(f"{s['angle_blurb']}"
                           + (f"  \n{meta}" if meta else ""))
        st.caption(f"Scanned {len(stories)} recent headlines · showing the top "
                   f"{len(top)} · [more on Google News]({gn_url})")

    st.divider()

    # ── Browse the feed by theme (News / Reddit) ────────────────────────── #
    st.markdown("#### Browse the feed")
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    csrc, cth = st.columns([1, 2])
    feed = csrc.radio("Source", ["📰 News", "👥 Reddit"], horizontal=True)
    theme = cth.selectbox("Theme", list(NEWS_THEMES.keys()))
    extra = st.text_input("Add a place or keyword (optional)",
                          placeholder="e.g. Virginia, Georgia, Tucson")
    extra_s = extra.strip()

    items, err, disclaimer = None, None, ""
    if feed == "📰 News":
        query = NEWS_THEMES[theme] + (f" {extra_s}" if extra_s else "")
        raw, err = fetch_news(query)
        disclaimer = ("Headlines are an automated news search, unfiltered and not "
                      "endorsements; follow the link to the original outlet.")
        if raw:
            items = [{"title": a["title"], "link": a["link"], "when": a["published"],
                      "meta": " · ".join(x for x in (a["source"], a["published"]) if x),
                      "dt": pd.to_datetime(a["published"], errors="coerce")}
                     for a in raw]
    else:
        query = theme + (f" · {extra_s}" if extra_s else "")
        corpus, cerr = load_reddit_corpus(pd.Timestamp.now().strftime("%Y-%m-%d"))
        disclaimer = ("Reddit threads are user posts — anecdotal and unverified; a "
                      "read on local sentiment, not reporting. Snapshot refreshes "
                      "once a day.")
        if corpus.empty:
            err = cerr or "no data"
        else:
            sub = corpus[corpus.theme == theme]
            if extra_s:
                hay = sub["title"].fillna("") + " " + sub["subreddit"].fillna("")
                sub = sub[hay.str.contains(extra_s, case=False, na=False,
                                           regex=False)]
            if cerr:
                disclaimer += f" ({cerr})"
            items = [{"title": p.title, "link": p.link, "when": p.created,
                      "meta": " · ".join(x for x in (p.subreddit, p.created) if x),
                      "dt": pd.to_datetime(p.created, errors="coerce")}
                     for p in sub.itertuples()]

    if err or items is None:
        rq = _reddit_query(NEWS_THEMES[theme])
        if extra_s:
            rq += f' "{extra_s}"' if " " in extra_s else f" {extra_s}"
        reddit_url = ("https://www.reddit.com/search/?q="
                      + urllib.parse.quote(rq) + "&sort=new")
        if feed == "👥 Reddit":
            st.warning("Couldn't load today's Reddit snapshot (Reddit was "
                       "unreachable and no saved snapshot exists yet).")
            st.markdown(f"🔗 **[Open this search on Reddit]({reddit_url})** — or "
                        "browse r/energy, r/RealEstate, r/climate, and your local "
                        "city/county subreddit.")
        else:
            st.warning("Couldn't reach Google News (offline or blocked).")
        st.caption(f"Detail: {err}")
    elif not items:
        st.info("Nothing for this theme right now — try another or add a place.")
    else:
        items.sort(key=lambda it: it["dt"] if pd.notna(it["dt"]) else pd.Timestamp.min,
                   reverse=True)
        st.caption(f"{len(items)} items • “{query}” • newest first")
        for it in items:
            st.markdown(f"- [{it['title']}]({it['link']})  \n"
                        f"  <small style='color:#9CA6B6'>{it['meta']}</small>",
                        unsafe_allow_html=True)

    st.caption(disclaimer)
    st.markdown('</div>', unsafe_allow_html=True)

    st.info("**See also:** the **🗞️ Community & backlash** tab for the moratorium "
            "tracker, town case studies, and the hyperscaler environmental "
            "scorecard. This feed only shows the last 7 days — for every "
            "headline GridWatch has archived, grouped by town/county with a "
            "pattern summary once a place has 4+ stories, see the "
            "**[story tracker](https://aigridwatch.com/story-tracker)** on "
            "the GridWatch site.")
