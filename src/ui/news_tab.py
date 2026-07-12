import streamlit as st
import urllib.parse
import pandas as pd
import altair as alt
from src.constants import COMPANY_STATEMENTS, COMPANY_FEED_TERMS, NEWS_THEMES, MORATORIUMS_DF
from src.helpers import src_link
from src.services.news import fetch_news
from src.services.reddit import load_reddit_corpus, _reddit_query

def render_news_tab():
    st.subheader("Community impact — the frictions and the value")
    st.caption("The build-out isn't frictionless: towns are pausing or blocking "
               "projects over power bills, water, noise, and land use. Below are "
               "the recurring flashpoints *and* how a host community actually "
               "extracts value, plus a live feed — news (Google) or grassroots "
               "sentiment (Reddit), no key required.")

    st.markdown("#### The recurring flashpoints")
    issues = [
        ("💵", "Electricity bills & grid strain",
         "Surging data-center load raises wholesale prices and can shift "
         "transmission/capacity costs onto ordinary ratepayers; PJM's capacity "
         "price spiked ~10× on data-center-driven demand. Utilities also delay "
         "fossil-plant retirements to serve the load.",
         "data center electricity bills ratepayers grid strain news"),
        ("💧", "Water",
         "Evaporative cooling consumes potable water — millions of gallons a day "
         "at a large campus — a flashpoint in drought-prone metros (Phoenix, "
         "Texas, Georgia).",
         "data center water use cooling drought news"),
        ("🏘️", "Zoning, land use & moratoria",
         "Counties are enacting moratoria or rejecting rezonings amid resident "
         "opposition; some developers are pulling out of hostile jurisdictions.",
         "data center zoning moratorium residents oppose rezoning news"),
        ("🔊", "Noise",
         "Chillers and backup generators produce a constant low-frequency hum; "
         "noise complaints have driven lawsuits and setback rules (notably in "
         "Northern Virginia).",
         "data center noise complaints residents hum news"),
        ("🧾", "Tax breaks vs. local benefit",
         "Big sales/property-tax abatements versus relatively few permanent jobs "
         "fuel debate over whether the local trade-off pays off.",
         "data center tax breaks incentives few jobs news"),
        ("🛢️", "Backup diesel & air permits",
         "Fleets of diesel generators for backup draw air-quality scrutiny and "
         "permit fights near residential areas.",
         "data center backup diesel generators air quality permit news"),
    ]
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    cards = st.columns(3)
    for i, (icon, head, body, vquery) in enumerate(issues):
        with cards[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {icon}\n**{head}**")
                st.caption(body)
                yt_url = ("https://www.youtube.com/results?search_query="
                          + urllib.parse.quote(vquery))
                st.markdown(f"▶ **[Watch videos]({yt_url})**")
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("#### How communities extract value")
    st.caption("The flip side of the pushback: the levers through which a host "
               "community actually captures value from a data center. When these "
               "land, local support and future approvals follow; when they don't, "
               "opposition rises and supply shrinks.")
    value_levers = [
        ("👷", "Jobs & local workforce",
         "Construction crews during the build and skilled operations/security "
         "roles once live, plus demand for local trades and suppliers. A "
         "skilled local workforce is itself a top siting criterion — the value "
         "runs both ways.",
         "data center local jobs workforce economic impact"),
        ("🧾", "Tax base & fiscal revenue",
         "Property, sales and equipment taxes can materially expand a small "
         "county's budget — funding schools, roads and services. The live "
         "debate is abatements vs. permanent jobs, so communities increasingly "
         "negotiate the trade-off explicitly.",
         "data center property tax revenue county schools"),
        ("⚡", "Grid stability contributions",
         "Projects developed to *support* the grid — funding transmission "
         "upgrades, adding on-site generation or storage, and offering "
         "flexible/curtailable load — leave the local system more reliable "
         "than they found it.",
         "data center grid stability transmission upgrade flexible load"),
        ("☀️", "Shared clean power",
         "Green tariffs, community solar, on-campus solar PV and clean "
         "microgrids let residents and the operator draw from the same new "
         "clean supply — decarbonizing the local grid rather than just "
         "consuming from it.",
         "data center community solar green tariff clean microgrid"),
        ("🛡️", "Ratepayer protection",
         "Cost-allocation rules that make data centers pay for the grid "
         "capacity they trigger — rather than socializing it onto households — "
         "are the single biggest driver of whether a community feels it's "
         "gaining or subsidizing.",
         "data center cost allocation ratepayer protection tariff"),
        ("🤝", "Community-benefit agreements",
         "Direct, negotiated commitments — local infrastructure, workforce "
         "training, noise/water safeguards, community funds — turn a project "
         "into a proof point that de-risks the next site.",
         "data center community benefit agreement local investment"),
    ]
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    vcards = st.columns(3)
    for i, (icon, head, body, vquery) in enumerate(value_levers):
        with vcards[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {icon}\n**{head}**")
                st.caption(body)
                yt_url = ("https://www.youtube.com/results?search_query="
                          + urllib.parse.quote(vquery))
                st.markdown(f"▶ **[Watch videos]({yt_url})**")
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("#### 🏘️ Case Studies: Lessons & Data Filed in Towns")
    st.caption(
        "Specific municipal files, regulatory submissions, and lessons learned from the front lines of "
        "local data center development."
    )

    TOWN_CASES = {
        "Loudoun County, VA": {
            "operator": "Multiple Hyperscalers & Equinix",
            "data_filed": "Loudoun County Board of Supervisors noise ordinance audits (limiting low-frequency hum to 38 dBA at residential property lines) and zoning amendments requiring Special Use Permits (SUP) for data centers in all commercial zones.",
            "outcome": "Strict noise mitigation walls mandated; developers forced to install custom quiet chillers. Siting is prohibited within 1,000 feet of residential zoning boundaries.",
            "lesson": "Density clusters near residential areas trigger immediate noise lawsuits and grid bottlenecks. Siting now requires strict acoustic engineering from day one."
        },
        "The Dalles, OR": {
            "operator": "Google",
            "data_filed": "Municipal water rights filings and public record lawsuits. Google historically sued the city of The Dalles to protect their water draw figures as a proprietary 'trade secret' during drought seasons.",
            "outcome": "Google withdrew its lawsuit under intense community pressure in late 2023, disclosing a draw of **274.5 Million Gallons** (approx. 29% of the town's total water consumption).",
            "lesson": "Drought-prone communities will not tolerate utility secrecy. Operator transparency regarding local resource consumption is now a public expectation."
        },
        "Mesa, AZ": {
            "operator": "Meta, Google & EdgeCore",
            "data_filed": "Mesa City Council water allocation agreements and dry-cooling zoning resolutions.",
            "outcome": "Mesa enacted a resolution banning all open-loop evaporative cooling for new data centers, requiring closed-loop/dry-cooling setups for all future building permits.",
            "lesson": "Desert municipalities prioritize aquifer conservation over PUE. Operators must use air-cooling in the Southwest, accepting higher summer power draws."
        },
        "Frederick County, MD": {
            "operator": "Aligned Data Centers (Quantum Loophole)",
            "data_filed": "Maryland Public Service Commission CPCN permit application for **168 diesel backup generators** (representing ~504 MW of emergency capacity).",
            "outcome": "PSC rejected the air quality permit due to particulate limits, leading Aligned to cancel the $30B project. This prompted the state legislature to pass CISA (SB 116) to exempt backup power from full CPCN reviews.",
            "lesson": "Massive diesel backup arrays near residential areas are major regulatory vulnerabilities. Clean emergency power (batteries/hydrogen) is increasingly necessary."
        },
        "Lebanon, IN": {
            "operator": "Amazon (AWS) / Eli Lilly",
            "data_filed": "LEAP Innovation District pipeline planning and Indiana DNR aquifer extraction surveys. Proposed drawing 100 Million gallons/day from the Wabash River aquifer via a 35-mile pipeline.",
            "outcome": "Fierce protests from agricultural landowners and rural counties forced the governor to pause pipeline decisions and commission a comprehensive regional water survey.",
            "lesson": "Cross-county resource redirection triggers intense rural-agricultural backlash. Siting in dry agricultural zones requires regional, not just municipal, resource agreements."
        },
        "Secaucus / Piscataway, NJ": {
            "operator": "Equinix & Digital Realty",
            "data_filed": "New Jersey Board of Public Utilities (BPU) Large Load Tariff filings (under Assembly Bill A-796).",
            "outcome": "Governor Sherrill signed P.L. 2025 c. 98 into law, requiring specific tariffs making any large load addition (>= 50 MW) pay for its own grid substation upgrades directly.",
            "lesson": "Ratepayers will no longer subsidize industrial grid connections. Developers must budget millions in direct substation upgrades in their capital allocations."
        }
    }

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    selected_town = st.selectbox(
        "Select a town/county case study:",
        options=["Select a Town..."] + list(TOWN_CASES.keys())
    )

    if selected_town != "Select a Town...":
        case = TOWN_CASES[selected_town]
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**🏢 Operator / Project**: {case['operator']}")
            st.markdown(f"**📜 Specific Data Filed**:")
            st.caption(case['data_filed'])
        with c2:
            st.markdown(f"**Outcome / Regulatory Action**:")
            st.markdown(f"*{case['outcome']}*")
            st.markdown(f"**💡 Key Lesson Learned**:")
            st.info(case['lesson'])
    else:
        st.info("💡 Select a town or county from the dropdown above to view municipal filings, water/noise data, and lessons learned.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("#### What the companies say")
    st.caption("First-party material — economic-impact reports, community "
               "pledges and newsrooms the operators themselves publish. These "
               "make the case *for* the build-out, so read them as the "
               "company's side, alongside the pushback above and the live feed "
               "below.")
    cats = {}
    for cat, company, what, url in COMPANY_STATEMENTS:
        cats.setdefault(cat, []).append((company, what, url))
    for cat, entries in cats.items():
        st.markdown(f"**{cat}**")
        comp_cols = st.columns(3)
        for i, (company, what, url) in enumerate(entries):
            with comp_cols[i % 3]:
                st.markdown(f"**{company}** — [{what}]({url})")

    st.markdown("###### 📣 Live press releases & news")
    st.caption("Fresh Google News hits for a given operator — their own "
               "announcements plus third-party coverage, newest first. No key "
               "required; headlines are unfiltered, not endorsements.")
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    pick = st.selectbox("Operator", ["All operators"]
                        + list(COMPANY_FEED_TERMS.keys()))
    if pick == "All operators":
        pr_query = ("(" + " OR ".join(COMPANY_FEED_TERMS.values()) + ") "
                    "data center (community OR jobs OR investment OR ratepayers "
                    "OR water OR moratorium)")
    else:
        pr_query = (COMPANY_FEED_TERMS[pick]
                    + " data center (community OR jobs OR investment OR "
                    "ratepayers OR water OR moratorium)")
    pr_items, pr_err = fetch_news(pr_query, limit=12)
    if pr_err or pr_items is None:
        gn_url = ("https://news.google.com/search?q="
                  + urllib.parse.quote(pr_query))
        st.warning("Couldn't reach Google News right now — "
                   f"[open this search]({gn_url}).")
    elif not pr_items:
        st.info("No recent items for this operator — try another.")
    else:
        st.caption(f"{len(pr_items)} items • newest first")
        for it in pr_items:
            meta = " · ".join(x for x in (it["source"], it["published"]) if x)
            st.markdown(f"- [{it['title']}]({it['link']})  \n"
                        f"  <small style='color:#888'>{meta}</small>",
                        unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Moratorium & ban tracker")
    st.caption("Towns, counties and states that have paused or blocked data "
               "centers. Point-in-time snapshot (mid-2026) compiled from public "
               "trackers — dozens more churn weekly, so follow the links below "
               "for live status. Not exhaustive.")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    enacted = MORATORIUMS_DF[MORATORIUMS_DF.status == "Enacted"]
    proposed = MORATORIUMS_DF[MORATORIUMS_DF.status == "Proposed"]
    q1, q2, q3 = st.columns(3)
    q1.metric("Enacted (listed)", f"{len(enacted)}")
    q2.metric("Proposed / considering", f"{len(proposed)}")
    q3.metric("States represented", f"{MORATORIUMS_DF.state.nunique()}")
    st.caption("Trackers report **50+ localities enacted** nationally (North "
               "Carolina alone has 20+); the table lists a representative subset.")

    fstat = st.multiselect(
        "Filter by status",
        list(MORATORIUMS_DF.status.unique()),
        default=["Enacted", "Proposed"])
    mdf = MORATORIUMS_DF[MORATORIUMS_DF.status.isin(fstat)] if fstat else MORATORIUMS_DF

    STATUS_COLORS = {"Enacted": "#d73027", "Proposed": "#fdae61",
                     "Rejected": "#9aa0a6", "Vetoed": "#9aa0a6"}
    geo = mdf.dropna(subset=["lat", "lon"]).copy()
    if not geo.empty:
        geo["color"] = geo["status"].map(STATUS_COLORS).fillna("#9aa0a6")
        st.map(geo, latitude="lat", longitude="lon", color="color", size=18000)
        st.caption("🔴 Enacted · 🟠 Proposed · ⚪ Rejected/Vetoed. Points are "
                   "approximate (county seat / city center); statewide actions "
                   "aren't mapped. Zoom to see the North Carolina cluster.")

    tcol, ccol = st.columns([3, 2])
    with tcol:
        st.dataframe(
            mdf[["locality", "state", "level", "status", "when", "note"]],
            use_container_width=True, hide_index=True, height=360,
            column_config={"locality": "Locality", "state": "State",
                           "level": "Level", "status": "Status",
                           "when": "When", "note": "Note"})
    with ccol:
        by_state = (mdf.groupby("state").size().reset_index(name="n")
                    .sort_values("n", ascending=False))
        chart = (alt.Chart(by_state).mark_bar().encode(
            x=alt.X("n:Q", title="Localities / actions"),
            y=alt.Y("state:N", sort="-x", title=None),
            tooltip=["state", "n"],
            color=alt.Color("n:Q", scale=alt.Scale(scheme="reds"), legend=None),
        ).properties(height=360))
        st.altair_chart(chart, use_container_width=True)

    st.caption("Trackers: " + " · ".join(
        src_link(k) for k in ["icap_mor", "dcbans", "dcopp", "dcwatch", "dcresp",
                               "dctrack", "gjf_mor", "rockinst"]))
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Live discussion")
    
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
                        f"  <small style='color:#888'>{it['meta']}</small>",
                        unsafe_allow_html=True)

    st.caption(disclaimer)
    st.markdown('</div>', unsafe_allow_html=True)
