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
import pathlib
import datetime as _dt
import json
import base64

from src.services.news import fetch_community_stories, _story_angle
from src.ui.calc_tab import render_calc_tab
from src.ui.compare_tab import render_compare_tab
from src.ui.live_tab import render_live_tab
from src.ui.grid_tab import render_grid_tab
from src.ui.dc_tab import render_dc_tab
from src.ui.news_tab import render_news_tab
from src.ui.officials_tab import render_officials_tab
from src.ui.macro_tab import render_macro_tab
from src.ui.method_tab import render_method_tab
from src.ui.blog_tab import render_blog_tab
from src.ui.learn_tab import render_learn_tab
from src.ui.corporate_tab import render_corporate_tab
from src.ui.studies_tab import render_studies_tab
from src.ui.sandbox_tab import render_sandbox_tab
from src.ui.bills_tab import render_bills_tab

# Load custom CSS styles
def load_css():
    css_path = pathlib.Path(__file__).resolve().parent / "assets" / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# PAGE SETUP
# --------------------------------------------------------------------------- #

st.set_page_config(page_title="GridWatch AI", page_icon="⚡", layout="wide")
load_css()

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
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
body {{
    margin: 0; padding: 0;
    font-family: 'Inter', sans-serif;
    background: transparent;
    color: #e2e8f0;
    overflow: hidden;
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
.hero-title {{
    font-family: 'Outfit', sans-serif;
    font-size: 2.6rem;
    font-weight: 700;
    margin: 0 0 8px 0;
    text-shadow: 0 2px 12px rgba(0,0,0,0.5);
}}
.hero-subtitle {{
    font-size: 0.95rem;
    color: #cbd5e1;
    margin: 0 0 20px 0;
    max-width: 680px;
    line-height: 1.5;
    text-shadow: 0 1px 6px rgba(0,0,0,0.4);
}}
.spotlight-container {{
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 90, 31, 0.2);
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
    color: #ff5a1f;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    display: flex;
    align-items: center;
    gap: 6px;
}}
.slide-counter {{
    font-size: 0.8rem;
    color: #64748b;
    margin-right: 76px;
}}
.slide-title {{
    font-family: 'Outfit', sans-serif;
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
    color: #38ef7d;
}}
.slide-blurb {{
    font-size: 0.85rem;
    color: #94a3b8;
    margin: 0;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
    line-height: 1.3;
}}
.slide-meta {{
    font-size: 0.72rem;
    color: #64748b;
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
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #e2e8f0;
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
    background: rgba(56, 239, 125, 0.1);
    border-color: #38ef7d;
    color: #38ef7d;
}}
</style>
</head>
<body>
<div class="hero">
    <div class="hero-bg"></div>
    <div class="hero-overlay"></div>
    <div class="hero-content">
        <div class="hero-title">&#9889; GridWatch AI</div>
        <div class="hero-subtitle">
            The energy, water, and carbon behind LLM token usage &mdash; from a single
            prompt to the global data-center grid. Sourced throughout; see Methodology.
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
st.divider()

# --- TABS SETUP ---
# Grouped flow: Personal tools → Data analysis → Industry → Community/policy → Reference
(tab_calc, tab_learn, tab_bills,
 tab_live, tab_compare, tab_grid,
 tab_dc, tab_corporate, tab_states,
 tab_news, tab_macro,
 tab_blog) = st.tabs([
    "🧮 Calculator", "🎓 Learn & simulate", "💡 Your utility bill",
    "🔬 Live models", "📊 Compare sources", "🕐 Grid timing",
    "🏢 Data centers", "💼 Corporate profiles", "🗂️ States & officials",
    "🗞️ Community & backlash", "🌍 Macro outlook",
    "📝 Blog & methodology",
])

# ── Personal tools ────────────────────────────────────────────────────── #
with tab_calc:
    render_calc_tab()

with tab_learn:
    render_learn_tab()
    st.divider()
    render_sandbox_tab()

with tab_bills:
    render_bills_tab()

# ── Data analysis ─────────────────────────────────────────────────────── #
with tab_live:
    render_live_tab()

with tab_compare:
    render_compare_tab()

with tab_grid:
    render_grid_tab()

# ── Industry landscape ────────────────────────────────────────────────── #
with tab_dc:
    render_dc_tab()

with tab_corporate:
    render_corporate_tab()

# ── Community & policy ────────────────────────────────────────────────── #
with tab_states:
    render_studies_tab()
    st.divider()
    render_officials_tab()

with tab_news:
    render_news_tab()

with tab_macro:
    render_macro_tab()

# ── Reference ─────────────────────────────────────────────────────────── #
with tab_blog:
    render_blog_tab()
    st.divider()
    render_method_tab()

st.divider()
st.caption("Scaffold — static coefficients live in src/constants.py; live model data "
           "streams from the ML.ENERGY leaderboard. Not affiliated with any provider.")
