"""
AI Token Footprint — energy, water & carbon of LLM usage
=========================================================
Streamlit app: turns tokens/queries into energy, water, and CO2; puts a single
query in human terms; compares first-party & benchmark sources; pulls LIVE
measured per-model numbers from the ML.ENERGY leaderboard; and shows how timing
usage to clean grid hours changes carbon (the CFE / hourly-matching angle).

Run:
    pip install -r requirements.txt
    streamlit run app.py
"""

import streamlit as st
import pathlib
import datetime as _dt

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

# Load custom CSS styles
def load_css():
    css_path = pathlib.Path(__file__).resolve().parent / "assets" / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# PAGE SETUP
# --------------------------------------------------------------------------- #

st.set_page_config(page_title="AI Token Footprint", page_icon="⚡", layout="wide")
load_css()

st.markdown('<h1 class="main-title">⚡ AI Token Footprint</h1>', unsafe_allow_html=True)
st.caption("The energy, water, and carbon behind LLM token usage — from a single "
           "prompt to the global data-center grid. Sourced throughout; see **Methodology**.")

# --- Rotating community spotlight (last 7 days) ----------------------------- #
st.markdown('<div class="spotlight-container">', unsafe_allow_html=True)
_stories, _story_err = fetch_community_stories()
if _stories:
    _n = len(_stories)
    st.session_state.setdefault("story_idx", _dt.date.today().toordinal())
    _i = st.session_state["story_idx"] % _n
    _s = _stories[_i]
    _emoji, _blurb = _story_angle(_s["title"])
    _age = ""
    _d = _s.get("age_days")
    if _d is not None:
        _age = "today" if _d <= 0 else ("yesterday" if _d == 1 else f"{_d} days ago")
    
    _c1, _c2 = st.columns([6, 1])
    with _c1:
        st.markdown(f"**{_emoji} Community spotlight — a data center in the news**")
        st.markdown(f"#### [{_s['title']}]({_s['link']})")
        _meta = " · ".join(x for x in [_s["source"], _age] if x)
        st.caption(f"{_blurb}" + (f"  \n*{_meta}*" if _meta else ""))
    with _c2:
        st.caption(f"{_i + 1} / {_n}")
        _pv, _nx = st.columns(2)
        if _pv.button("◂", key="story_prev", use_container_width=True,
                      help="Previous story"):
            st.session_state["story_idx"] = _i - 1
            st.rerun()
        if _nx.button("▸", key="story_next", use_container_width=True,
                      help="Next story"):
            st.session_state["story_idx"] = _i + 1
            st.rerun()
    st.caption("Automated Google News search (last 7 days) for communities "
               "affected by a built or under-construction data center. "
               "Unfiltered and not an endorsement — follow the link to the "
               "original outlet. More on the **Community & backlash** tab.")
else:
    st.info("Community spotlight is temporarily unavailable "
            f"({_story_err or 'no recent stories found'}). See the "
            "**Community & backlash** tab for trackers and live discussion.")
st.markdown('</div>', unsafe_allow_html=True)
st.divider()

# --- TABS SETUP ---
(tab_calc, tab_learn, tab_compare, tab_live, tab_grid, tab_dc, tab_news,
 tab_officials, tab_macro, tab_method, tab_blog) = st.tabs(
    ["🧮 Calculator", "🎓 Learn", "📊 Compare sources", "🔬 Live models",
     "🕐 Grid timing", "🏢 Data centers", "🗞️ Community & backlash",
     "🏛️ Officials", "🌍 Macro outlook", "📚 Methodology", "📝 Blog"]
)

with tab_calc:
    render_calc_tab()

with tab_learn:
    render_learn_tab()

with tab_compare:
    render_compare_tab()

with tab_live:
    render_live_tab()

with tab_grid:
    render_grid_tab()

with tab_dc:
    render_dc_tab()

with tab_news:
    render_news_tab()

with tab_officials:
    render_officials_tab()

with tab_macro:
    render_macro_tab()

with tab_method:
    render_method_tab()

with tab_blog:
    render_blog_tab()

st.divider()
st.caption("Scaffold — static coefficients live in src/constants.py; live model data "
           "streams from the ML.ENERGY leaderboard. Not affiliated with any provider.")
