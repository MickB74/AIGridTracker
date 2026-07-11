"""
Compare sources tab — per-query energy across models, first-party disclosures,
and benchmark studies. Color-coded by measurement scope with contextual detail.
"""

import streamlit as st
import pandas as pd
import altair as alt
from src.constants import QUERY_COEFFS

# Scope color palette
SCOPE_COLORS = {
    "Full-stack": "#38ef7d",
    "Chip-only": "#6ec6ff",
    "Benchmark": "#ffb347",
    "Contested": "#ff5252",
}


def render_compare_tab():
    st.subheader("Per-query energy across models & sources")
    st.caption(
        "How much electricity does a single AI query use? The answer depends on "
        "the model, the hardware, and — critically — what's being measured. "
        "**Full-stack** includes cooling and infrastructure overhead; **chip-only** "
        "counts just the GPU/TPU; **benchmark** figures are third-party estimates."
    )

    # ── Build data ───────────────────────────────────────────────────────────
    rows = []
    for name, d in QUERY_COEFFS.items():
        rows.append({
            "Model / Source": name,
            "Wh per query": d["energy_wh"],
            "Scope": d.get("scope", "Benchmark"),
            "Note": d.get("note", ""),
        })
    df = pd.DataFrame(rows)

    # ── Filters & controls ───────────────────────────────────────────────────
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    ctrl1, ctrl2 = st.columns([1, 1])
    with ctrl1:
        log = st.toggle("Log scale (recommended — the GPT-5 outlier spans 300×)",
                         value=True)
    with ctrl2:
        scopes = st.multiselect(
            "Filter by measurement scope",
            options=sorted(df["Scope"].unique()),
            default=sorted(df["Scope"].unique()),
        )

    view = df[df["Scope"].isin(scopes)].copy() if scopes else df.copy()

    # ── Chart ────────────────────────────────────────────────────────────────
    x_scale = alt.Scale(type="log") if log else alt.Scale(type="linear")

    chart = (
        alt.Chart(view)
        .mark_bar(cornerRadiusEnd=4, height=18)
        .encode(
            x=alt.X("Wh per query:Q", title="Wh per query", scale=x_scale),
            y=alt.Y("Model / Source:N", sort="-x", title=None,
                     axis=alt.Axis(labelLimit=400)),
            color=alt.Color(
                "Scope:N",
                scale=alt.Scale(
                    domain=list(SCOPE_COLORS.keys()),
                    range=list(SCOPE_COLORS.values()),
                ),
                legend=alt.Legend(title="Measurement scope", orient="bottom"),
            ),
            tooltip=[
                alt.Tooltip("Model / Source:N"),
                alt.Tooltip("Wh per query:Q", format=".3f"),
                alt.Tooltip("Scope:N"),
                alt.Tooltip("Note:N"),
            ],
        )
        .properties(height=max(len(view) * 36, 200))
    )
    st.altair_chart(chart, use_container_width=True)

    # ── Legend / context boxes ───────────────────────────────────────────────
    leg1, leg2, leg3, leg4 = st.columns(4)
    with leg1:
        st.markdown(
            f'<span style="color:{SCOPE_COLORS["Full-stack"]}">●</span> '
            "**Full-stack** — includes cooling, networking, PUE overhead",
            unsafe_allow_html=True,
        )
    with leg2:
        st.markdown(
            f'<span style="color:{SCOPE_COLORS["Chip-only"]}">●</span> '
            "**Chip-only** — GPU/TPU active power only",
            unsafe_allow_html=True,
        )
    with leg3:
        st.markdown(
            f'<span style="color:{SCOPE_COLORS["Benchmark"]}">●</span> '
            "**Benchmark** — third-party or derived estimate",
            unsafe_allow_html=True,
        )
    with leg4:
        st.markdown(
            f'<span style="color:{SCOPE_COLORS["Contested"]}">●</span> '
            "**Contested** — disputed methodology / outlier",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Human-scale context ──────────────────────────────────────────────────
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 💡 Putting it in perspective")

    ctx1, ctx2, ctx3 = st.columns(3)
    with ctx1:
        st.metric("Typical AI query", "0.2 – 0.6 Wh",
                   help="Range across major models (full-stack)")
        st.caption("About **7 seconds** of running a microwave")
    with ctx2:
        st.metric("Reasoning query (o1, deep think)", "3 – 5 Wh",
                   help="Chain-of-thought models generating 10k+ tokens")
        st.caption("About **1 minute** of a desktop computer")
    with ctx3:
        st.metric("Google search (for comparison)", "~0.3 Wh",
                   help="Google's 2024 disclosure of avg search energy")
        st.caption("AI queries are now in the **same ballpark** as search")

    st.info(
        "**Why do estimates vary so much?** Three factors: **(1) Model size** — "
        "a 405B-parameter model uses ~10× more energy than a 27B model. "
        "**(2) Measurement scope** — chip-only figures exclude ~40–60% of real "
        "facility energy (cooling, networking, storage, idle). "
        "**(3) Reasoning depth** — chain-of-thought models generate 5–20× more "
        "tokens internally, multiplying the energy cost per user query."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Detail table ─────────────────────────────────────────────────────────
    with st.expander("📋 Full data table with notes", expanded=False):
        st.dataframe(
            view[["Model / Source", "Wh per query", "Scope", "Note"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Model / Source": st.column_config.TextColumn(width="large"),
                "Wh per query": st.column_config.NumberColumn(format="%.3f"),
                "Note": st.column_config.TextColumn(width="large"),
            },
        )

    st.caption(
        "⚠️ The GPT-5 figure is from a contested third-party report — an upper-bound "
        "estimate, not a first-party disclosure. It is included for context but should "
        "not be treated as representative. All figures assume a ~1,000 output-token "
        "text response unless noted."
    )
