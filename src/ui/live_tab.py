import streamlit as st
import altair as alt
from src.constants import MLENERGY_TASKS
from src.services.mlenergy import load_mlenergy

def render_live_tab():
    st.subheader("Measured per-model inference energy — ML.ENERGY leaderboard")
    st.caption("Live pull from the ML.ENERGY benchmark (H100 / B200, vLLM). Shows the "
               "min-energy (best-batched) config per model — a well-utilised server.")

    with st.expander("What is **Wh/token**? (and why size isn't everything)"):
        st.markdown(
            "**Wh/token = watt-hours per token** — the electricity to generate **one "
            "output token** (a token ≈ ¾ of a word, so ~750 tokens ≈ 550 words).\n\n"
            "- **Wh (watt-hour)** is a unit of energy: a 10-watt LED bulb running for "
            "one hour uses 10 Wh. `0.000008 Wh/token` = 8 millionths of a watt-hour "
            "per token.\n"
            "- **Wh/response** is just Wh/token × the tokens in a full answer — the "
            "other column.\n"
            "- Numbers look tiny because these are the **max-batch** configs (a busy, "
            "well-utilised server) — a lower bound vs. bursty real traffic.\n\n"
            "**Size isn't the whole story.** Energy per token is driven as much by "
            "**precision** (4-bit `mxfp4` fires far fewer bits than 16-bit `bfloat16`) "
            "and **architecture** (Mixture-of-Experts activates only a slice of the "
            "weights per token) as by raw parameter count — so a bigger model can use "
            "*less* per token than a smaller dense one.")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    cta, cgpu = st.columns(2)
    task_label = cta.selectbox("Task", list(MLENERGY_TASKS.keys()))
    gpu = cgpu.radio("GPU", ["H100", "B200"], horizontal=True)

    df_live, err = load_mlenergy(MLENERGY_TASKS[task_label])

    if err or df_live is None:
        st.warning("Couldn't reach the ML.ENERGY leaderboard (offline or blocked). "
                   "The Calculator still works with the static coefficients.")
        st.caption(f"Detail: {err}")
    else:
        d = df_live[df_live.gpu == gpu].copy()
        d["wh_per_1k_tok"] = d["wh_per_token"] * 1000
        st.caption(f"{len(d)} models • pulled live • GPU: {gpu}")

        chart = (alt.Chart(d).mark_bar().encode(
            x=alt.X("wh_per_request:Q", title="Wh per full response"),
            y=alt.Y("model:N", sort="-x", title=None),
            tooltip=[alt.Tooltip("model"), alt.Tooltip("wh_per_request", format=".4f"),
                     alt.Tooltip("wh_per_token", format=".6f"),
                     "params_b", "precision", "arch"],
            color=alt.Color("wh_per_request:Q", scale=alt.Scale(scheme="tealblues"), legend=None),
        ).properties(height=max(280, 26 * len(d))))
        st.altair_chart(chart, use_container_width=True)

        # --- dynamic takeaway read straight off the live numbers ------------- #
        eff = d.loc[d["wh_per_token"].idxmin()]
        hog = d.loc[d["wh_per_token"].idxmax()]
        ratio = hog["wh_per_token"] / eff["wh_per_token"] if eff["wh_per_token"] else 0
        st.markdown(
            f"**On {gpu}, {eff['model']} is the most efficient** at "
            f"{eff['wh_per_token']*1000:.4f} Wh per 1k tokens — "
            f"**{ratio:,.0f}× less** than {hog['model']} "
            f"({hog['wh_per_token']*1000:.4f}). ")
        # Surface a case where a bigger model beats a smaller one (arch/precision).
        dd = d.dropna(subset=["params_b"])
        if len(dd) >= 2:
            big = dd.loc[dd["params_b"].idxmax()]
            inversions = dd[(dd["params_b"] < big["params_b"]) &
                            (dd["wh_per_token"] > big["wh_per_token"])]
            if not inversions.empty:
                sm = inversions.loc[inversions["wh_per_token"].idxmax()]
                st.info(
                    f"💡 Size ≠ energy: **{big['model']}** ({big['params_b']:.0f}B, "
                    f"{big['precision']}, {big['arch']}) uses **less per token** than "
                    f"the smaller **{sm['model']}** ({sm['params_b']:.0f}B, "
                    f"{sm['precision']}, {sm['arch']}) — precision and architecture "
                    f"outweigh parameter count.")

        with st.expander("Table (per-token & per-request)"):
            show = d[["model", "params_b", "precision", "arch", "wh_per_token", "wh_per_request"]]
            st.dataframe(show, use_container_width=True, hide_index=True,
                         column_config={
                             "wh_per_token": st.column_config.NumberColumn("Wh/token", format="%.6f"),
                             "wh_per_request": st.column_config.NumberColumn("Wh/response", format="%.4f"),
                             "params_b": st.column_config.NumberColumn("Params (B)"),
                         })

        # push selected coefficients into the Calculator (Token mode)
        picks = st.multiselect("Add to Calculator as per-token sources", d["model"].tolist())
        if picks:
            st.session_state["live_coeffs"] = {
                f"🔬 {m} ({gpu})": float(d.loc[d.model == m, "wh_per_token"].iloc[0])
                for m in picks
            }
            st.success(f"Added {len(picks)} model(s). Switch to **Calculator → Tokens**.")
    st.markdown('</div>', unsafe_allow_html=True)
