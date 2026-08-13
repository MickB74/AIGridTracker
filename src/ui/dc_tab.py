import streamlit as st
import pandas as pd
import altair as alt
from src.constants import (DATACENTERS_DF, DC_METRICS, ERCOT_LL_VINTAGE,
                           ERCOT_LL_DC_SHARE, ERCOT_LL_FUNNEL,
                           DC_SITES_DF, OPERATORS)
from src.helpers import src_link
from src.services.ercot import ercot_largeload_latest
from src.services.eia import eia_latest_demand
from src.services.secrets import load_local_secrets


def render_dc_tab():
    with st.expander("On this page", expanded=False):
        st.markdown(
            "**1.** Market power by phase · "
            "**2.** ERCOT large-load surge · "
            "**3.** Site list + sources · "
            "**4.** Live EIA-930 grid demand"
        )
    st.info("**See the interactive map on the Map tab** for a unified view of all "
            "campuses, projects, and moratoriums.")
    st.divider()
    st.subheader("Where the data centers are — and how much power they pull")
    st.caption("Market-level power by phase (~2025). Totals are broker inventories "
               "(CBRE / JLL / Cushman & Wakefield) — operators don't disclose "
               "per-facility MW. Toggle the phase; each is cited separately because "
               "the shops measure different things. Approximate; see **Methodology**.")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    cmet, creg = st.columns([2, 2])
    metric_label = cmet.radio("Phase", list(DC_METRICS.keys()), horizontal=True)
    col, msrcs, blurb = DC_METRICS[metric_label]
    region = creg.radio("Region", ["All", "US", "EMEA", "APAC"], horizontal=True)

    dcd = DATACENTERS_DF if region == "All" else DATACENTERS_DF[DATACENTERS_DF.region == region]
    dcd = dcd[dcd[col].notna()].copy()
    dcd["val"] = dcd[col]

    st.caption(f"**{metric_label}** — {blurb}")

    if dcd.empty:
        st.info("No markets report this phase for the selected region. Try "
                "**Operational**, or switch region to **US**.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Markets shown", f"{len(dcd)}")
        m2.metric(f"{metric_label.split(' (')[0]} power", f"{dcd['val'].sum()/1000:,.1f} GW")
        m3.metric("Largest", f"{dcd.loc[dcd['val'].idxmax(), 'market'].split(' (')[0]}",
                  f"{dcd['val'].max():,.0f} MW")

        bar = (alt.Chart(dcd).mark_bar().encode(
            x=alt.X("val:Q", title=f"{metric_label.split(' (')[0]} power (MW)"),
            y=alt.Y("market:N", sort="-x", title=None),
            tooltip=[alt.Tooltip("market"), alt.Tooltip("country"),
                     alt.Tooltip("grid"), alt.Tooltip("val:Q", title="MW")],
            color=alt.Color("region:N", legend=alt.Legend(title="Region")),
        ).properties(height=max(280, 26 * len(dcd))))
        st.altair_chart(bar, use_container_width=True)

        with st.expander("Table — all phases + sources"):
            show = dcd[["market", "region", "country", "grid",
                        "mw", "uc", "planned"]].copy()
            st.dataframe(
                show, use_container_width=True, hide_index=True,
                column_config={
                    "grid": "ISO feed",
                    "mw": st.column_config.NumberColumn("Operational (MW)", format="%d"),
                    "uc": st.column_config.NumberColumn("Under constr. (MW)", format="%d"),
                    "planned": st.column_config.NumberColumn("Planned (MW)", format="%d")})
            st.caption("Sources — " + " · ".join(src_link(k) for k in
                       ["cbre_dc", "cbre_glob", "jll_dc", "cushman_dc"]))

    st.caption("Sources for this phase: " + " · ".join(src_link(k) for k in msrcs))
    st.caption("Markets tagged with an **ISO feed** (ERCO / CISO / PJM) can be "
               "pulled live for carbon on the **Grid timing** tab.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------------ #
    # ERCOT large-load interconnection queue
    # ------------------------------------------------------------------ #
    st.divider()
    st.subheader("In the queue: ERCOT's large-load surge")
    st.caption(
        "Interconnection queues are mostly *generation* queues — they don't tag "
        "data centers, which are **load**. ERCOT is the one US grid operator that "
        "publishes an aggregate large-**load** picture and breaks out the "
        "data-center share (per-project names are confidential). The story is the "
        f"funnel below, all as of **{ERCOT_LL_VINTAGE}**.")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    fdf = pd.DataFrame(
        [(s, mw, blurb, src) for s, mw, blurb, src in ERCOT_LL_FUNNEL],
        columns=["stage", "mw", "blurb", "src"])
    requested = fdf.loc[fdf.stage == "Seeking interconnection", "mw"].iloc[0]
    live_mw = fdf.loc[fdf.stage == "Actually operational", "mw"].iloc[0]

    e1, e2, e3 = st.columns(3)
    e1.metric("Large load requested", f"{requested/1000:,.0f} GW",
              f"~{ERCOT_LL_DC_SHARE*100:.0f}% data centers")
    e2.metric("Large-load DC share", f"{requested*ERCOT_LL_DC_SHARE/1000:,.0f} GW")
    e3.metric("Actually running today", f"{live_mw/1000:,.1f} GW",
              f"{live_mw/requested*100:.1f}% of requested", delta_color="off")

    fdf["label"] = fdf.apply(
        lambda r: f"{r.stage} — {r.mw/1000:,.1f} GW" if r.mw >= 1000
        else f"{r.stage} — {r.mw:,.0f} MW", axis=1)
    funnel = (alt.Chart(fdf).mark_bar().encode(
        x=alt.X("mw:Q", title="MW (log scale)",
                scale=alt.Scale(type="log")),
        y=alt.Y("stage:N", sort=list(fdf.stage), title=None),
        color=alt.Color("stage:N", sort=list(fdf.stage),
                        scale=alt.Scale(range=["#ff5a1f", "#f5a623", "#4caf50"]),
                        legend=None),
        tooltip=[alt.Tooltip("stage"), alt.Tooltip("mw:Q", title="MW", format=","),
                 alt.Tooltip("blurb", title="What it means")],
    ).properties(height=180))
    text = funnel.mark_text(align="left", dx=4, color="#ddd").encode(text="label:N")
    st.altair_chart(funnel + text, use_container_width=True)
    st.caption("Log scale — the requested pile is **~100x the load actually on the "
               "grid**. Most queued large load is speculative and will never energize.")

    for _, r in fdf.iterrows():
        st.markdown(f"- **{r.stage}** ({r.mw:,.0f} MW) — {r.blurb}  \n"
                    f"  ↳ {src_link(r.src)}")

    if st.button("Check ERCOT for a newer report",
                 help="ERCOT publishes no live large-load feed — this scans their "
                      "Large Load Integration page for the newest posted document."):
        with st.spinner("Scanning ercot.com..."):
            latest = ercot_largeload_latest()
        if not latest:
            st.info("Couldn't reach ERCOT just now — the curated snapshot above "
                    f"stands. Browse manually: {src_link('ercot_ll')}.")
        else:
            newest_date, docs = latest
            snap_date = "2026-03-26"
            if newest_date > snap_date:
                st.warning(f"ERCOT has posted documents dated **{newest_date}** "
                           f"(newer than this snapshot's {snap_date}) — the figures "
                           "above may be stale. Newest postings:")
            else:
                st.success(f"No large-load document newer than the snapshot "
                           f"({snap_date}); latest posted is {newest_date}.")
            for d, name, url in docs:
                st.markdown(f"- `{d}` — [{name}]({url})")

    st.caption("Sources: " + " · ".join(src_link(k) for k in
               ["ercot_ll_bc", "ercot_ll_tac", "ercot_ll"]))
    st.caption("Other ISOs (PJM, MISO, CAISO...) publish only *generation* queues, "
               "which don't identify data centers; the paid trackers "
               "(interconnection.fyi, Cleanview) infer them by name-matching. This "
               "panel sticks to ERCOT's own published large-load aggregates.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Site list + sources ──────────────────────────────────────────────── #
    st.divider()
    st.subheader("Hyperscaler campuses + AI-competitor megasites")
    st.caption("Individual data-center sites. See the **Map** tab for the "
               "interactive map; the table below lists all tracked sites with "
               "source attribution.")

    campus_df = DC_SITES_DF.copy()
    campus_df["_owner_label"] = campus_df["owner"].replace("self", "Self-owned")
    campus_df["_tenant_label"] = campus_df["tenant"].fillna("Undisclosed")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.expander("Site list + sources", expanded=True):
        st.dataframe(
            campus_df[["operator", "_owner_label", "_tenant_label",
                 "location", "state", "attribution"]].rename(
                columns={"_owner_label": "Owner", "_tenant_label": "Tenant",
                         "operator": "Operator", "location": "Location",
                         "state": "State", "attribution": "Source type"}),
            use_container_width=True, hide_index=True)
        st.caption("Hyperscaler (first-party): " + " · ".join(
            src_link(k) for k in
            ["google_dc", "meta_dc", "microsoft_dc", "aws_dc"]))
        st.caption("AI-competitor sites: " + " · ".join(
            src_link(k) for k in ["stargate", "xai_memphis", "crwv_dc"]))
    st.caption("Google and Meta publish precise campus lists; Microsoft "
               "(metro-level communities) and Amazon/AWS (investment announcements) "
               "disclose locations less granularly. AI-competitor sites are "
               "publicly documented but not first-party campus lists, so their "
               "coordinates are approximate. Research/forecast context: "
               + src_link("imasons") + " · " + src_link("bnef") + ".")
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.info(
        "**Market data moved to the site:** "
        "[aigridwatch.com/data-centers](https://aigridwatch.com/data-centers) -- "
        "50-state facility count, operators & LLCs, ERCOT queue, SEC 10-K "
        "analysis, grid operators & FERC response."
    )

    # --- Live EIA-930 grid demand (requires API key — stays in Streamlit) ------
    st.divider()
    st.subheader("Live grid demand (EIA-930)")
    st.caption("Grid-scale total load right now (all uses, not data-center-only).")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    secrets = load_local_secrets()
    dk = st.text_input("EIA API key", type="password", key="dc_eia_key",
                       value=secrets["eia"],
                       help="Free instant key: eia.gov/opendata/register.php "
                            "— same key as the Grid timing tab.")
    if secrets["eia"]:
        st.caption("Auto-loaded from local config.")
    if dk:
        cols = st.columns(3)
        for col, ba in zip(cols, ["ERCO", "PJM", "CISO"]):
            try:
                res = eia_latest_demand(dk, ba)
                if res:
                    mw, period = res
                    col.metric(f"{ba} demand", f"{mw/1000:,.1f} GW", period)
                else:
                    col.metric(f"{ba} demand", "—", "no data")
            except Exception as e:                                # noqa: BLE001
                col.metric(f"{ba} demand", "—", "fetch failed")
                col.caption(f"{e}")
    else:
        st.caption("Enter your EIA key to pull each grid's latest total demand.")
    st.markdown('</div>', unsafe_allow_html=True)
