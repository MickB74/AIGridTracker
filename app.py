"""
GridWatch AI — energy, water & carbon of LLM usage
==================================================
Streamlit app: turns tokens/queries into energy, water, and CO2; puts a single
query in human terms; compares first-party & benchmark sources; pulls LIVE
measured per-model numbers from the ML.ENERGY leaderboard; and shows how timing
usage to clean grid hours changes carbon (the CFE / hourly-matching angle).

Run:
    pip install -r requirements.txt
    streamlit run app.py
"""

import streamlit as st
import streamlit.components.v1 as components
import os
import pathlib
import datetime as _dt
import json
import base64
import urllib.parse

import pandas as pd

from src.services.news import fetch_community_stories, _story_angle
from src.constants import (
    POLICY_ALERTS, STATE_PUCS_DF, MORATORIUMS_DF, STATE_DC_DF,
    EXECUTIVES_DF, OPERATORS_DF, DC_SITES_DF, VIDEO_TOPICS,
    STATE_GRID_PROFILES,
)
from src.ui.calc_tab import render_calc_tab
from src.ui.compare_tab import render_compare_tab
from src.ui.live_tab import render_live_tab
from src.ui.grid_tab import render_grid_tab
from src.ui.dc_tab import render_dc_tab
from src.ui.news_tab import render_news_tab
from src.ui.news_feed_tab import render_news_feed_tab
from src.ui.officials_tab import render_officials_tab
from src.ui.method_tab import render_method_tab
from src.ui.monitors_tab import render_monitors_tab
from src.ui.learn_tab import render_learn_tab
from src.ui.corporate_tab import render_corporate_tab
from src.ui.studies_tab import render_studies_tab
from src.ui.sandbox_tab import render_sandbox_tab
from src.ui.toolkit_tab import render_toolkit_tab
from src.ui.consulting_tab import render_consulting_tab
from src.ui.impact_tab import render_impact_tab
from src.ui.start_here_tab import render_start_here_tab
from src.ui.newsletter import render_newsletter_signup

# Static front door. Reference content (state briefings, company profiles,
# blog, health risks, moratorium tracker) is published there, not here.
SITE = "https://aigridwatch.com"
SITE_LABEL = "aigridwatch.com"
from src.services.tracking import load_events, load_subscribers

# Load custom CSS styles
def load_css():
    css_path = pathlib.Path(__file__).resolve().parent / "assets" / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# PAGE SETUP
# --------------------------------------------------------------------------- #

st.set_page_config(page_title="AI GridWatch", page_icon="⚡", layout="wide")
load_css()

# --------------------------------------------------------------------------- #
# SIDEBAR — My Community state filter + quick search
# --------------------------------------------------------------------------- #
_all_states = sorted(STATE_PUCS_DF["state"].unique())

with st.sidebar:
    st.markdown("#### 🏠 My Community")
    _my_state = st.selectbox(
        "Your state",
        ["All states"] + list(_all_states),
        key="my_state",
        help="Select your state to auto-filter moratoriums, officials, PUCs, "
             "and data center sites across every tab.",
    )
    if _my_state != "All states":
        _abbrev = STATE_PUCS_DF.loc[
            STATE_PUCS_DF["state"] == _my_state, "abbrev"
        ].iloc[0] if not STATE_PUCS_DF.loc[
            STATE_PUCS_DF["state"] == _my_state, "abbrev"
        ].empty else ""
        st.session_state["my_state_abbrev"] = _abbrev

        _st_moras = MORATORIUMS_DF[MORATORIUMS_DF["state"] == _abbrev]
        _st_sites = DC_SITES_DF[DC_SITES_DF["state"] == _abbrev] if "state" in DC_SITES_DF.columns else pd.DataFrame()
        _st_dc = STATE_DC_DF[STATE_DC_DF["state"] == _my_state] if "state" in STATE_DC_DF.columns else pd.DataFrame()

        _facts = []
        if not _st_dc.empty:
            row = _st_dc.iloc[0]
            if "facilities" in row.index:
                _facts.append(f"**{int(row['facilities'])}** tracked facilities")
            if "twh_year" in row.index:
                _facts.append(f"**{row['twh_year']:.1f} TWh**/year consumption")
        if not _st_moras.empty:
            enacted = (_st_moras["status"] == "Enacted").sum()
            proposed = (_st_moras["status"] == "Proposed").sum()
            parts = []
            if enacted:
                parts.append(f"{enacted} enacted")
            if proposed:
                parts.append(f"{proposed} proposed")
            _facts.append(f"**{len(_st_moras)}** moratoriums ({', '.join(parts)})")
        if not _st_sites.empty:
            _facts.append(f"**{len(_st_sites)}** known campuses")

        if _facts:
            st.caption(" · ".join(_facts))
        st.caption("Tabs will auto-filter to your state where applicable.")
    else:
        st.session_state["my_state_abbrev"] = ""

    st.markdown("---")
    st.markdown("#### 🔍 Quick Search")
    _search_q = st.text_input(
        "Search across all data",
        placeholder="e.g. Google, Mesa AZ, moratorium...",
        key="global_search",
    )
    if _search_q:
        _sq = _search_q.lower()
        _results = []

        _m_hits = MORATORIUMS_DF[
            MORATORIUMS_DF.apply(
                lambda r: _sq in str(r["locality"]).lower()
                or _sq in str(r["state"]).lower()
                or _sq in str(r["note"]).lower(), axis=1
            )
        ]
        if not _m_hits.empty:
            _results.append(("Moratoriums", _m_hits[["locality", "state", "status", "when"]].head(5)))

        _e_hits = EXECUTIVES_DF[
            EXECUTIVES_DF.apply(
                lambda r: any(_sq in str(v).lower() for v in r.values), axis=1
            )
        ].head(5)
        if not _e_hits.empty:
            _cols = [c for c in ["name", "company", "title"] if c in _e_hits.columns]
            _results.append(("Executives", _e_hits[_cols]))

        _s_hits = DC_SITES_DF[
            DC_SITES_DF.apply(
                lambda r: any(_sq in str(v).lower() for v in r.values), axis=1
            )
        ].head(5)
        if not _s_hits.empty:
            _cols = [c for c in ["market", "operator", "mw", "state"] if c in _s_hits.columns]
            if _cols:
                _results.append(("Data center sites", _s_hits[_cols]))

        _p_hits = STATE_PUCS_DF[
            STATE_PUCS_DF.apply(
                lambda r: any(_sq in str(v).lower() for v in r.values), axis=1
            )
        ].head(5)
        if not _p_hits.empty:
            _results.append(("PUCs", _p_hits[["state", "name"]]))

        if _results:
            for _label, _rdf in _results:
                st.markdown(f"**{_label}** ({len(_rdf)})")
                st.dataframe(_rdf, use_container_width=True, hide_index=True, height=150)
        else:
            st.caption(f"No results for '{_search_q}'.")

    st.markdown("---")
    st.markdown("#### 🌐 On aigridwatch.com")
    st.caption("Shareable pages you can send to neighbours or a reporter.")
    # Only deep-link when a real state is selected — the picker's default
    # ("All states") has no page of its own.
    _my_state = st.session_state.get("my_state", "")
    if _my_state in STATE_GRID_PROFILES:
        _slug = _my_state.lower().replace(" ", "-")
        st.markdown(f"- [{_my_state} briefing]({SITE}/states/{_slug}.html)")
    else:
        st.markdown(f"- [State briefings]({SITE}/states)")
    st.markdown(
        f"- [Company profiles]({SITE}/companies)\n"
        f"- [Moratorium tracker]({SITE}/moratoriums)\n"
        f"- [Health risks]({SITE}/health-risks)\n"
        f"- [Blog]({SITE}/blog)"
    )

    st.markdown("---")
    render_newsletter_signup("sidebar", compact=True)

    # Usage dashboard — only for the operator. Visible when GRIDWATCH_ADMIN_KEY
    # is set and the URL carries ?admin=<that key>.
    _admin_key = os.environ.get("GRIDWATCH_ADMIN_KEY", "")
    if _admin_key and st.query_params.get("admin") == _admin_key:
        st.markdown("---")
        with st.expander("📊 Admin — usage data", expanded=False):
            _events = load_events()
            _subs = load_subscribers()
            _packs = (
                _events[_events["event"] == "action_pack_download"]
                if not _events.empty and "event" in _events.columns
                else pd.DataFrame()
            )
            a1, a2 = st.columns(2)
            a1.metric("Action packs downloaded", len(_packs))
            a2.metric("Newsletter subscribers", len(_subs))
            if not _packs.empty and "state" in _packs.columns:
                st.caption("Downloads by state")
                st.dataframe(
                    _packs["state"].value_counts().rename("downloads"),
                    use_container_width=True,
                )
            if not _events.empty:
                st.download_button(
                    "Download all events (CSV)",
                    _events.to_csv(index=False),
                    "gridwatch_events.csv",
                    "text/csv",
                    key="admin_events_dl",
                )
            if not _subs.empty:
                st.download_button(
                    "Download subscribers (CSV)",
                    _subs.to_csv(index=False),
                    "gridwatch_subscribers.csv",
                    "text/csv",
                    key="admin_subs_dl",
                )

# --- Hero banner with background image and overlay content ----------------- #
_hero_path = pathlib.Path(__file__).resolve().parent / "assets" / "hero.png"
_hero_b64 = base64.b64encode(_hero_path.read_bytes()).decode()

_stories, _story_err = fetch_community_stories()
_slides_data = []
if _stories:
    for s in _stories:
        emoji, blurb = _story_angle(s["title"])
        d = s.get("age_days")
        age = "today" if d is not None and d <= 0 else ("yesterday" if d == 1 else f"{d} days ago" if d is not None else "")
        meta = " · ".join(x for x in [s["source"], age] if x)
        _slides_data.append({
            "title": s["title"],
            "link": s["link"],
            "emoji": emoji,
            "blurb": blurb,
            "meta": meta
        })

_carousel_block = ""
if _slides_data:
    _carousel_block = f"""
    <div class="spotlight-container" id="container">
        <div class="carousel-wrapper">
            <div class="slides-container" id="slides"></div>
        </div>
        <div class="controls">
            <button class="control-btn" onclick="prevSlide()">&#9666;</button>
            <button class="control-btn" onclick="nextSlide()">&#9656;</button>
        </div>
    </div>
    <script>
    const data = {json.dumps(_slides_data)};
    let currentIndex = 0;
    let autoPlayInterval;
    const slidesContainer = document.getElementById('slides');
    data.forEach((item, index) => {{
        const slide = document.createElement('div');
        slide.className = 'slide';
        slide.innerHTML = `
            <div class="header-row">
                <div class="title-label">
                    <span>${{item.emoji}}</span>
                    <span>Community spotlight — a data center in the news</span>
                </div>
                <div class="slide-counter">${{index + 1}} / ${{data.length}}</div>
            </div>
            <div class="slide-title">
                <a href="${{item.link}}" target="_blank">${{item.title}}</a>
            </div>
            <div class="slide-blurb">${{item.blurb}}</div>
            <div class="slide-meta">${{item.meta}}</div>
        `;
        slidesContainer.appendChild(slide);
    }});
    function updateCarousel() {{
        slidesContainer.style.transform = `translateX(-${{currentIndex * 100}}%)`;
    }}
    function nextSlide() {{
        currentIndex = (currentIndex + 1) % data.length;
        updateCarousel();
        resetTimer();
    }}
    function prevSlide() {{
        currentIndex = (currentIndex - 1 + data.length) % data.length;
        updateCarousel();
        resetTimer();
    }}
    function startTimer() {{
        autoPlayInterval = setInterval(nextSlide, 7000);
    }}
    function resetTimer() {{
        clearInterval(autoPlayInterval);
        startTimer();
    }}
    const ctr = document.getElementById('container');
    ctr.addEventListener('mouseenter', () => clearInterval(autoPlayInterval));
    ctr.addEventListener('mouseleave', startTimer);
    startTimer();
    </script>
    """

_hero_html = f"""
<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
body {{
    margin: 0; padding: 0;
    font-family: 'Space Grotesk', system-ui, sans-serif;
    background: transparent;
    color: #EAF0F7;
    overflow: hidden;
    -webkit-font-smoothing: antialiased;
}}
.hero {{
    position: relative;
    width: 100%;
    min-height: 480px;
    border-radius: 16px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
}}
.hero-bg {{
    position: absolute;
    inset: 0;
    background: url('data:image/png;base64,{_hero_b64}') center center / cover no-repeat;
    z-index: 0;
}}
.hero-overlay {{
    position: absolute;
    inset: 0;
    background: linear-gradient(
        to bottom,
        rgba(15, 23, 42, 0.15) 0%,
        rgba(15, 23, 42, 0.55) 50%,
        rgba(15, 23, 42, 0.92) 100%
    );
    z-index: 1;
}}
.hero-content {{
    position: relative;
    z-index: 2;
    padding: 32px 36px;
}}
.hero-logo {{
    margin: 0 0 8px 0;
    max-width: 640px;
}}
.hero-logo svg {{
    width: 100%;
    height: auto;
    filter: drop-shadow(0 2px 12px rgba(0,0,0,0.4));
}}
.hero-subtitle {{
    font-size: 0.95rem;
    color: #C8D0DA;
    margin: 0 0 20px 0;
    max-width: 680px;
    line-height: 1.55;
    text-shadow: 0 1px 6px rgba(0,0,0,0.4);
}}
.spotlight-container {{
    background: color-mix(in srgb, #0A0E14 82%, transparent);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid #28313F;
    border-radius: 12px;
    padding: 16px 20px;
    position: relative;
    height: 160px;
    box-sizing: border-box;
}}
.carousel-wrapper {{
    position: relative;
    width: 100%;
    height: 100%;
    overflow: hidden;
}}
.slides-container {{
    display: flex;
    transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    height: 100%;
}}
.slide {{
    min-width: 100%;
    max-width: 100%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: center;
    overflow: hidden;
}}
.header-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
}}
.title-label {{
    font-size: 0.8rem;
    font-weight: 600;
    color: #F98866;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    display: flex;
    align-items: center;
    gap: 6px;
}}
.slide-counter {{
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 0.75rem;
    color: #9CA6B6;
    margin-right: 76px;
}}
.slide-title {{
    font-family: 'Space Grotesk', system-ui, sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    margin: 2px 0 5px 0;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
    line-height: 1.3;
}}
.slide-title a {{
    color: #f8fafc;
    text-decoration: none;
    transition: color 0.2s;
}}
.slide-title a:hover {{
    color: #2DD4BF;
}}
.slide-blurb {{
    font-size: 0.85rem;
    color: #C8D0DA;
    margin: 0;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
    line-height: 1.3;
}}
.slide-meta {{
    font-size: 0.72rem;
    color: #9CA6B6;
    margin-top: 3px;
    font-style: italic;
}}
.controls {{
    position: absolute;
    right: 16px;
    top: 16px;
    display: flex;
    gap: 6px;
    z-index: 10;
}}
.control-btn {{
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid #28313F;
    color: #EAF0F7;
    border-radius: 8px;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.75rem;
    outline: none;
}}
.control-btn:hover {{
    background: rgba(45, 212, 191, 0.14);
    border-color: #2DD4BF;
    color: #2DD4BF;
}}
</style>
</head>
<body>
<div class="hero">
    <div class="hero-bg"></div>
    <div class="hero-overlay"></div>
    <div class="hero-content">
        <div class="hero-logo">
            <svg viewBox="0 0 540 120" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="tg" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#2DD4BF"/><stop offset="100%" stop-color="#14B8A6"/>
                </linearGradient>
                <linearGradient id="pg" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#F98866"/><stop offset="50%" stop-color="#FBBF24"/><stop offset="100%" stop-color="#F98866"/>
                </linearGradient>
                <filter id="gl"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                <filter id="pg2"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
              </defs>
              <g transform="translate(55,52)">
                <polygon points="0,-45 39,-22.5 39,22.5 0,45 -39,22.5 -39,-22.5" fill="none" stroke="url(#tg)" stroke-width="2.2" opacity="0.9"/>
                <polygon points="0,-28 24.2,-14 24.2,14 0,28 -24.2,14 -24.2,-14" fill="none" stroke="url(#tg)" stroke-width="1.3" opacity="0.5"/>
                <line x1="-39" y1="0" x2="39" y2="0" stroke="#2DD4BF" stroke-width="0.8" opacity="0.3"/>
                <line x1="-19.5" y1="-33.5" x2="19.5" y2="33.5" stroke="#2DD4BF" stroke-width="0.8" opacity="0.3"/>
                <line x1="19.5" y1="-33.5" x2="-19.5" y2="33.5" stroke="#2DD4BF" stroke-width="0.8" opacity="0.3"/>
                <circle cx="0" cy="-45" r="2.5" fill="#2DD4BF" opacity="0.7"/>
                <circle cx="39" cy="-22.5" r="2.5" fill="#2DD4BF" opacity="0.7"/>
                <circle cx="39" cy="22.5" r="2.5" fill="#2DD4BF" opacity="0.7"/>
                <circle cx="0" cy="45" r="2.5" fill="#2DD4BF" opacity="0.7"/>
                <circle cx="-39" cy="22.5" r="2.5" fill="#2DD4BF" opacity="0.7"/>
                <circle cx="-39" cy="-22.5" r="2.5" fill="#2DD4BF" opacity="0.7"/>
                <polyline points="-6,-23 3,-5 -5,-5 6,23" fill="none" stroke="url(#pg)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" filter="url(#pg2)"/>
                <circle cx="0" cy="0" r="3.2" fill="#FBBF24" filter="url(#gl)" opacity="0.9"/>
                <path d="M 0,-37 A 37,37 0 0,1 32,-18.5" fill="none" stroke="#2DD4BF" stroke-width="1.8" opacity="0.6" stroke-linecap="round"/>
                <path d="M 32,18.5 A 37,37 0 0,1 0,37" fill="none" stroke="#2DD4BF" stroke-width="1.8" opacity="0.4" stroke-linecap="round"/>
              </g>
              <g transform="translate(115,52)">
                <rect x="0" y="-14" width="42" height="26" rx="5" fill="url(#tg)" opacity="0.15"/>
                <rect x="0" y="-14" width="42" height="26" rx="5" fill="none" stroke="#2DD4BF" stroke-width="1.1" opacity="0.5"/>
                <text x="21" y="4" font-family="'IBM Plex Mono',ui-monospace,monospace" font-size="15" font-weight="600" text-anchor="middle" fill="#2DD4BF">AI</text>
                <text x="54" y="7" font-family="'Space Grotesk',system-ui,sans-serif" font-size="40" font-weight="700" letter-spacing="-0.03em" fill="#EAF0F7">Grid<tspan fill="url(#tg)">Watch</tspan></text>
                <text x="56" y="30" font-family="'Space Grotesk',system-ui,sans-serif" font-size="11" font-weight="400" letter-spacing="0.12em" fill="#9CA6B6">COMMUNITY ENERGY INTELLIGENCE</text>
              </g>
            </svg>
        </div>
        <div class="hero-subtitle">
            The open-source resource for communities facing data center development.
            Energy &amp; water data, negotiation tools, policy tracking, and advocacy
            support &mdash; sourced throughout.
        </div>
        {_carousel_block}
    </div>
</div>
</body>
</html>
"""
_hero_height = 500 if _slides_data else 320
components.html(_hero_html, height=_hero_height)

if _slides_data:
    st.caption("Automated Google News search (last 7 days) for communities "
               "affected by a built or under-construction data center. "
               "Unfiltered and not an endorsement — follow the link to the "
               "original outlet. More on the **Community & backlash** tab.")
elif not _stories:
    st.info("Community spotlight is temporarily unavailable "
            f"({_story_err or 'no recent stories found'}). See the "
            "**Community & backlash** tab for trackers and live discussion.")

# ── What is GridWatch AI? — mission explainer ─────────────────────────── #
st.markdown("#### What is GridWatch AI?")
_mission_cards = [
    ("🎯", "Our mission",
     "Give the people who live near data centers the same quality of "
     "information the companies building them already have."),
    ("🛠️", "What we do",
     "Track the energy, water, and carbon of AI infrastructure — and "
     "aggregate local news, moratoriums, and official filings, all sourced."),
    ("👥", "Who we serve",
     "Residents, local officials, and advocates facing a data-center "
     "proposal or expansion in their community."),
    ("🤝", "How we help",
     "Negotiation toolkits, impact and bill calculators, PUC and official "
     "directories, and meeting-prep briefs you can take to the table."),
]
_mcols = st.columns(4)
for _mcol, (_mic, _mh, _mb) in zip(_mcols, _mission_cards):
    with _mcol:
        with st.container(border=True):
            st.markdown(f"### {_mic}\n**{_mh}**")
            st.caption(_mb)

# ── Breaking policy alerts ────────────────────────────────────────────── #
_severity_styles = {
    "critical": ("🔴", "#ff4444", "rgba(255,68,68,0.08)", "rgba(255,68,68,0.25)"),
    "major":    ("🟠", "#ff9800", "rgba(255,152,0,0.08)", "rgba(255,152,0,0.25)"),
    "info":     ("🔵", "#2196f3", "rgba(33,150,243,0.08)", "rgba(33,150,243,0.25)"),
}
_today = _dt.date.today().isoformat()
for _alert in POLICY_ALERTS[:3]:
    _headline, _detail, _date, _sev, _url = _alert[:5]
    _expires = _alert[5] if len(_alert) > 5 else None
    if _expires and _today > _expires:
        continue
    _dot, _color, _bg, _border = _severity_styles.get(_sev, _severity_styles["info"])
    _link_html = f' <a href="{_url}" target="_blank" style="color:{_color};font-weight:600;">Read more →</a>' if _url else ""
    st.markdown(
        f'<div style="background:{_bg};border:1px solid {_border};border-radius:10px;'
        f'padding:12px 18px;margin:6px 0;display:flex;align-items:flex-start;gap:10px;">'
        f'<span style="font-size:1.1rem;line-height:1.4;">{_dot}</span>'
        f'<div>'
        f'<strong style="color:{_color};font-size:0.95rem;">{_headline}</strong>'
        f'<span style="color:#9CA6B6;font-size:0.8rem;margin-left:10px;">{_date}</span>'
        f'<br><span style="color:#C8D0DA;font-size:0.85rem;">{_detail}{_link_html}</span>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

# ── Videos — curated topic explainers ─────────────────────────────────── #
st.markdown("#### ▶ Videos")
st.caption("Short explainers and reporting on each data-center issue. Each link "
           "opens a fresh YouTube search so results stay current — a starting "
           "point, not an endorsement of any single video.")
for _vgroup, _vtopics in VIDEO_TOPICS.items():
    with st.expander(f"▶ {_vgroup}", expanded=False):
        for _vemoji, _vlabel, _vquery in _vtopics:
            _vurl = ("https://www.youtube.com/results?search_query="
                     + urllib.parse.quote(_vquery))
            st.markdown(f"{_vemoji} [{_vlabel}]({_vurl})")

st.divider()

# --- TABS SETUP ---
# Flow: Start here → Problem → Impact → Action → Deep dive → Reference → Business
st.info(
    "🚨 **New here because of a local proposal?** Open **Start here** — the "
    "first tab below — for a five-step guided plan and a downloadable action pack."
)
(tab_start, tab_toolkit, tab_simulate, tab_technical,
 tab_intel, tab_reference, tab_consulting) = st.tabs([
    "🚨 Start here",
    "🛡️ Negotiation toolkit",
    "🎮 Estimate & simulate",
    "🔬 Token calculator",
    "📡 Live intel",
    "📚 Reference",
    "🤝 Consulting",
])

# ── Start here (guided wizard) ────────────────────────────────────────── #
with tab_start:
    render_start_here_tab()

# ── Negotiation toolkit (generators: CBA, dividend, meeting prep) ─────── #
with tab_toolkit:
    render_toolkit_tab()

# ── Estimate & simulate (interactive models) ──────────────────────────── #
with tab_simulate:
    st.caption("This tab contains: **Local impact calculator** "
               "· **AI Datacenter Siting Sandbox** — scroll down for each.")
    render_impact_tab()
    st.divider()
    render_sandbox_tab()

# ── Token calculator (the LLM footprint model + its coefficients) ─────── #
with tab_technical:
    st.subheader("🔬 Token calculator")
    st.caption(
        "Per-token energy modeling, live model benchmarks, source comparisons, "
        "and grid carbon timing tools. The data behind the advocacy."
    )
    (sub_calc, sub_live, sub_compare, sub_grid, sub_method) = st.tabs([
        "🧮 Footprint calculator", "🔬 Live models",
        "📊 Compare sources", "🕐 Grid timing", "📐 Methodology",
    ])
    with sub_calc:
        render_calc_tab()
    with sub_live:
        render_live_tab()
    with sub_compare:
        render_compare_tab()
    with sub_grid:
        render_grid_tab()
    with sub_method:
        render_method_tab()

# ── Live intel (things that change: news, filings, report editions) ───── #
with tab_intel:
    st.caption("This tab contains: **Top stories** · **Community & backlash** "
               "· **Market monitors** — scroll down for each section.")
    render_news_feed_tab()
    st.divider()
    render_news_tab()
    st.divider()
    render_monitors_tab()

# ── Reference (background reading; migrating to aigridwatch.com) ──────── #
with tab_reference:
    st.caption(
        "Background reading and directories. State briefings, company "
        f"profiles, blog posts, health risks, and the utility-bill explainer "
        f"now live on [{SITE_LABEL}]({SITE}) — this tab holds what hasn't "
        "moved yet."
    )
    st.info(
        f"**Moved to the site:** "
        f"[{SITE_LABEL}/bills]({SITE}/bills) — why your electric bill is going "
        f"up, capacity markets and peak load · "
        f"[{SITE_LABEL}/outlook]({SITE}/outlook) — global and US electricity "
        "forecasts to 2035, and where new facilities are being built."
    )
    (ref_learn, ref_dc, ref_corp, ref_states) = st.tabs([
        "🎓 Learn", "🏢 Data centers",
        "💼 Companies", "🗂️ States & officials",
    ])
    with ref_learn:
        render_learn_tab()
    with ref_dc:
        render_dc_tab()
    with ref_corp:
        render_corporate_tab()
    with ref_states:
        render_studies_tab()
        st.divider()
        render_officials_tab()

# ── Consulting ───────────────────────────────────────────────────────── #
with tab_consulting:
    render_consulting_tab()

st.divider()
st.caption("Scaffold — static coefficients live in src/constants.py; live model data "
           "streams from the ML.ENERGY leaderboard. Not affiliated with any provider.")
