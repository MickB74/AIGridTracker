"""
Blog tab — curated stories and project mission for the AI Grid Tracker.
Renders an 'Our Mission' section and a feed of authored blog posts with
tags, summaries, and full-body markdown expansion.
"""

import streamlit as st
from src.blog_content import ABOUT_SECTION, BLOG_STORIES


def render_blog_tab():
    st.subheader("📝 Blog — Stories, analysis & our mission")
    st.caption(
        "Original reporting and explainers on the energy, water, and community "
        "impacts of AI infrastructure — plus the story behind this tracker."
    )

    # ── Our Mission / About section ─────────────────────────────────────────
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f"## {ABOUT_SECTION['title']}")
    st.markdown(
        f'<p style="font-size:1.15rem;opacity:0.8;margin-bottom:1.2rem;">'
        f'{ABOUT_SECTION["tagline"]}</p>',
        unsafe_allow_html=True,
    )
    st.markdown(ABOUT_SECTION["body"])
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ── Blog stories feed ───────────────────────────────────────────────────
    st.markdown("## 📰 Latest Stories")

    # Sort stories newest-first
    sorted_stories = sorted(BLOG_STORIES, key=lambda s: s["date"], reverse=True)

    for story in sorted_stories:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        # Header row: title + date
        hdr_left, hdr_right = st.columns([5, 1])
        with hdr_left:
            st.markdown(f"### {story['title']}")
        with hdr_right:
            st.caption(story["date"].strftime("%b %d, %Y"))

        # Tags row
        if story.get("tags"):
            tag_html = " ".join(
                f'<span style="display:inline-block;background:rgba(56,239,125,0.15);'
                f"color:#38ef7d;border:1px solid rgba(56,239,125,0.3);"
                f"border-radius:12px;padding:2px 10px;font-size:0.78rem;"
                f'margin-right:6px;margin-bottom:4px;">{t}</span>'
                for t in story["tags"]
            )
            st.markdown(tag_html, unsafe_allow_html=True)

        # Author
        st.caption(f"By {story['author']}")

        # Summary (always visible)
        st.markdown(f"*{story['summary']}*")

        # Expandable full article
        with st.expander("Read full article ▾", expanded=False):
            st.markdown(story["body"])

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("")  # spacer
