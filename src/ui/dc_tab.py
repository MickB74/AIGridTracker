import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from src.constants import (DATACENTERS_DF, DC_METRICS, ERCOT_LL_VINTAGE,
                           ERCOT_LL_DC_SHARE, ERCOT_LL_FUNNEL, HYPERSCALERS_DF,
                           HYPERSCALER_COLORS, AI_COMPETITOR_SITES_DF,
                           AI_COMPETITORS_DF, STATE_DC_DF, STATE_DC_NATIONAL,
                           MEGA_PROJECTS_DF)
from src.helpers import src_link
from src.services.ercot import ercot_largeload_latest
from src.services.eia import eia_latest_demand
from src.services.secrets import load_local_secrets

def render_dc_tab():
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
    dcd = dcd[dcd[col].notna()].copy()          # only markets with data for this phase
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

        map_df = dcd.rename(columns={"lat": "latitude", "lon": "longitude"}).copy()
        map_df["size"] = map_df["val"] * 40     # radius in metres, scaled by MW
        st.map(map_df, latitude="latitude", longitude="longitude", size="size",
               color="#ff5a1f")

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
    st.caption("⚡ Markets tagged with an **ISO feed** (ERCO / CISO / PJM) can be "
               "pulled live for carbon on the **Grid timing** tab.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------------ #
    # ERCOT large-load interconnection queue — data centers in the queue
    # ------------------------------------------------------------------ #
    st.divider()
    st.subheader("⚡ In the queue: ERCOT's large-load surge")
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
    st.caption("Log scale — the requested pile is **~100× the load actually on the "
               "grid**. Most queued large load is speculative and will never energize.")

    for _, r in fdf.iterrows():
        st.markdown(f"- **{r.stage}** ({r.mw:,.0f} MW) — {r.blurb}  \n"
                    f"  ↳ {src_link(r.src)}")

    if st.button("↻ Check ERCOT for a newer report",
                 help="ERCOT publishes no live large-load feed — this scans their "
                      "Large Load Integration page for the newest posted document."):
        with st.spinner("Scanning ercot.com…"):
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
    st.caption("⚠️ Other ISOs (PJM, MISO, CAISO…) publish only *generation* queues, "
               "which don't identify data centers; the paid trackers "
               "(interconnection.fyi, Cleanview) infer them by name-matching. This "
               "panel sticks to ERCOT's own published large-load aggregates.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("Hyperscaler campuses + AI-competitor megasites")
    st.caption("Individual data-center sites. **Hyperscalers** (Google, Meta, "
               "Microsoft, Amazon) are plotted from operators' own location pages. "
               "**AI-competitor sites** — the frontier-model builders and AI-cloud "
               "players these companies name as competition in their SEC 10-K "
               "filings (see the competitor table below) — are plotted from public "
               "announcements and press (xAI's Colossus, the OpenAI · Oracle · "
               "SoftBank *Stargate* campuses). No operator discloses per-facility "
               "MW, so these are location markers, not sized by power.")

    campus_df = pd.concat([HYPERSCALERS_DF, AI_COMPETITOR_SITES_DF],
                          ignore_index=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    firms = st.multiselect("Company", list(campus_df.company.unique()),
                           default=list(campus_df.company.unique()))
    hdf = campus_df[campus_df.company.isin(firms)].copy() if firms \
        else campus_df.copy()

    if hdf.empty:
        st.info("Pick a company to plot its campuses.")
    else:
        h1, h2 = st.columns(2)
        h1.metric("Campuses shown", f"{len(hdf)}")
        h2.metric("States", f"{hdf.state.nunique()}")
        hdf["id"] = hdf["company"] + " · " + hdf["location"]

        fig = px.scatter_geo(
            hdf, lat="lat", lon="lon", color="company", scope="usa",
            color_discrete_map=HYPERSCALER_COLORS, hover_name="location",
            custom_data=["id", "company", "location", "state", "lat", "lon", "src"])
        fig.update_traces(marker=dict(size=11, line=dict(width=0.5, color="white")),
                          hovertemplate="%{customdata[1]} — %{customdata[2]}, "
                                        "%{customdata[3]}<extra></extra>")
        fig.update_geos(bgcolor="rgba(0,0,0,0)", landcolor="#26272b",
                        subunitcolor="#3c3f44", showsubunits=True,
                        countrycolor="#3c3f44", lakecolor="rgba(0,0,0,0)")
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0), height=460,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(title="Company", orientation="h",
                        y=1.0, yanchor="bottom", x=0))
        event = st.plotly_chart(fig, use_container_width=True,
                                on_select="rerun", key="campus_map")

        picked = []
        try:
            picked = [p["customdata"][0] for p in event.selection["points"]]
        except (AttributeError, KeyError, TypeError, IndexError):
            pass
        if picked:
            for _, r in hdf[hdf.id.isin(picked)].iterrows():
                st.markdown(
                    f"**{r.company} — {r['location']}, {r.state}**  \n"
                    f"📍 {r.lat:.2f}, {r.lon:.2f}  ·  source: {src_link(r.src)}")
        else:
            st.caption("👆 Click a dot to see that campus's details.")

        st.caption(" · ".join(f"{c} = {len(hdf[hdf.company==c])}"
                               for c in firms if len(hdf[hdf.company == c])) +
                   "  ·  🟢 Google · 🔵 Meta · 🔴 Microsoft · 🟠 Amazon (AWS) · "
                   "🟣 xAI · 🩵 OpenAI · Oracle (Stargate) · 🩷 CoreWeave")
        with st.expander("Site list + sources"):
            st.dataframe(hdf[["company", "location", "state"]],
                         use_container_width=True, hide_index=True,
                         column_config={"company": "Company", "location": "Location",
                                        "state": "State"})
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

    # --- Who each company names as a competitor (from SEC 10-K filings) --------
    st.divider()
    st.subheader("Who each company calls a competitor — from SEC 10-K filings")
    st.caption("Straight from the “Competition” section (Item 1) of each filer's "
               "latest annual report. **Only Oracle names specific rivals**; the "
               "big-tech filings describe competitor *categories* — always "
               "including AI and frontier models — but name no companies. "
               "*Named in filing* is what the 10-K literally lists; *Key AI / "
               "data-center rivals* maps those categories to today's market "
               "participants.")

    comp = AI_COMPETITORS_DF.copy()
    comp["Names rivals?"] = comp["names"].map({True: "✅ Yes", False: "— categories only"})
    show = comp[["filer", "Names rivals?", "quote", "named", "rivals"]].rename(
        columns={"filer": "Filer",
                 "quote": "AI-competitor language (from the 10-K)",
                 "named": "Named in filing", "rivals": "Key AI / data-center rivals"})
    st.dataframe(show, use_container_width=True, hide_index=True)
    st.caption("Filings: " + " · ".join(
        src_link(k) for k in
        ["goog_10k", "meta_10k", "msft_10k", "amzn_10k", "orcl_10k", "crwv_10k"]))

    st.info(
        "📋 **Authoritative facility data is coming (EIA).** Data centers are "
        "electricity *customers*, so they've never been in federal facility data "
        "— which is why the maps above rely on broker estimates and operator "
        "self-disclosure. That's starting to change: in **March 2026 the EIA "
        "launched its first pilot survey** of data-center energy use — 196 "
        "companies across **Texas, Washington, and Northern Virginia/DC** "
        "(electricity, cooling, IT specs, efficiency), voluntary now with a "
        "**mandatory survey to follow**. Results aren't published yet. Meanwhile "
        "EIA already powers this app's live grid data (EIA-930): the carbon "
        "curves on **Grid timing** and the live system-demand metric below. "
        + src_link("eia_pilot") + " · " + src_link("eia930") + ".")
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("The demand wave — ERCOT & PJM")
    st.caption("The two US grids where data-center load growth is most acute. "
               "Interconnection-queue figures are filed point-in-time snapshots "
               "(not a live API); headline numbers sourced below.")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    ge, gp = st.columns(2)
    with ge:
        st.markdown("**ERCOT (Texas)**")
        e1, e2 = st.columns(2)
        e1.metric("Large-load queue", "~233 GW", "requests, Nov 2025")
        e2.metric("Data centers", "72.9%", "of the queue")
        st.caption("Nearly **4×** the 63 GW at end-2024. + crypto ~8.8%. "
                   f"{src_link('ercot_ll')}.")
    with gp:
        st.markdown("**PJM (Mid-Atlantic)**")
        p1, p2 = st.columns(2)
        p1.metric("Peak load 2024→30", "+32 GW", "94% data centers")
        p2.metric("Dominion (VA) summer peak", "23.9 GW", "+23% vs 2019")
        st.caption("Dominion zone (NoVA \"Data Center Alley\") drives the biggest "
                   f"absolute rise. {src_link('pjm_lf')}; {src_link('eia_va')}.")

    st.markdown("**Live system demand (EIA-930)** — grid-scale total load right "
                "now (all uses, not data-center-only):")
    secrets = load_local_secrets()
    dk = st.text_input("EIA API key", type="password", key="dc_eia_key",
                       value=secrets["eia"],
                       help="Free instant key: eia.gov/opendata/register.php "
                            "— same key as the Grid timing tab.")
    if secrets["eia"]:
        st.caption("🔑 Auto-loaded from local config.")
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

    st.divider()
    st.subheader("How the grid operators & FERC are responding")
    st.caption("Every US RTO/ISO is now rewriting the rulebook for how giant, "
               "inflexible data-center loads connect and pay — with FERC forcing "
               "the pace. The common thread: make large loads *provably* firm, "
               "curtailable, and cost-causation-fair so existing ratepayers "
               "aren't left holding the bill.")

    st.markdown(f"""
**⚖️ FERC — the federal referee.**
On **Dec 18, 2025** FERC ordered **PJM** — the nation's largest grid operator —
to write new tariff rules for *co-location* (data centers plugging directly into
a power plant behind the meter), giving PJM 60 days to file and demanding an
interim reliability report. It found PJM's tariff lacked the "clarity or
consistency" to price co-located load fairly. {src_link('ferc_pjm_colo')}.
Then on **Jun 18, 2026** FERC went wider, issuing **show-cause orders to MISO,
SPP and other RTOs**: justify your large-load rules within 60 days, or reform
them. {src_link('ferc_showcause')}.
""")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    ra, rb = st.columns(2)
    with ra:
        st.markdown("**🟠 PJM (Mid-Atlantic / Data Center Alley)**")
        st.markdown(f"""
- Data-center demand is now showing up as **price**: the latest capacity auction
  cleared at a **record ~$16.4B**, with data centers ~**40% ($6.5B)** of the
  cost — and it hit the price cap for the third straight year. {src_link('pjm_auction25')}.
- Building a distinct **co-located load service** and large-load tariff under
  FERC's Dec 2025 order (NITS on a gross basis, plus new firm / non-firm
  contract-demand services). {src_link('ferc_pjm_colo')}.
""")
        st.markdown("**🔵 MISO (Midwest / South)**")
        st.markdown(f"""
- Facing an "unprecedented surge" in large-load requests; standing up
  **Large Load Interconnection Reliability Requirements** and expedited study
  paths (ERAS) to integrate them without degrading reliability. {src_link('miso_llir')}.
- Under FERC's Jun 2026 show-cause order to justify or revise its tariff. {src_link('ferc_showcause')}.
""")
    with rb:
        st.markdown("**🟢 ERCOT (Texas)**")
        st.markdown(f"""
- **SB 6 (2025)** is the most aggressive large-load law yet: loads **≥75 MW**
  get new interconnection standards, a **$50k/MW** fee, and mandatory
  **curtailment/shut-off equipment** — ERCOT can order them to drop load or run
  backup generation during grid emergencies. {src_link('tx_sb6_ll')}; {src_link('tx_sb6')}.
- Ties directly to the **~233 GW large-load queue** above — the rules are how
  Texas decides which of those actually get to plug in.
""")
        st.markdown("**🟡 SPP (Central Plains)**")
        st.markdown(f"""
- Created a **High Impact Large Load (HILL)** track: a targeted **~90-day**
  study-and-approval process (plus a HILL Generation Assessment for load paired
  with on-site generation) to fast-track big connections while catching system
  constraints early. {src_link('spp_hill')}.
- Also named in FERC's Jun 2026 show-cause order. {src_link('ferc_showcause')}.
""")

    st.info("**The through-line:** co-location + cost allocation. Regulators are "
            "converging on two questions — *can this load be curtailed when the "
            "grid is tight?* and *who pays for the transmission it needs?* "
            "Expect firm-service requirements, large upfront interconnection "
            "fees, and curtailment obligations to spread across every ISO.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------------ #
    # NEW: ElectricChoice.com — 50-state data center landscape (July 2026)
    # ------------------------------------------------------------------ #
    st.divider()
    st.subheader("🗺️ All 50 states: data center facility count & power draw")
    st.caption(
        "State-by-state breakdown from ElectricChoice.com's U.S. Data Center Power "
        "Map (updated July 2026; CC-BY 4.0), itself citing Lawrence Berkeley National "
        "Lab (LBNL-2001637, Dec 2024), EIA, EPRINC, and industry facility inventories. "
        "Facility counts = active data centers as of 2026; TWh/year = annual electricity "
        "consumption; 🔜 = states with major projects under construction or announced."
    )

    # --- National headline stats ---
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    n = STATE_DC_NATIONAL
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active data centers", f"{n['active_facilities']:,}+", "across all 50 states")
    c2.metric("Annual power use", f"{n['twh_annual']} TWh", f"{n['pct_us_power']}% of U.S. electricity")
    c3.metric("Under construction", f"{n['under_construction']}+", "in 38 states")
    c4.metric("Homes equivalent", f"{n['homes_equivalent_millions']}M homes", "powered annually")

    st.caption(f"As of {n['as_of']}. Source: {src_link('electricchoice')} · {src_link('lbnl')}")

    st.divider()

    # --- Sort / filter controls ---
    sc1, sc2, sc3 = st.columns([2, 1, 1])
    search_q = sc1.text_input("🔍 Search states or hubs", placeholder="e.g. Virginia, Google, Phoenix…", key="state_dc_search")
    sort_by = sc2.selectbox("Sort by", ["TWh/year ↓", "Facilities ↓", "TWh/year ↑", "Facilities ↑", "State A→Z"], key="state_dc_sort")
    show_upcoming_only = sc3.checkbox("🔜 Upcoming projects only", value=False, key="state_dc_upcoming")

    sdf = STATE_DC_DF.copy()

    # Apply search
    if search_q:
        q = search_q.lower()
        sdf = sdf[sdf["state"].str.lower().str.contains(q) |
                  sdf["major_hubs"].str.lower().str.contains(q) |
                  sdf["abbrev"].str.lower().str.contains(q)]

    # Apply upcoming filter
    if show_upcoming_only:
        sdf = sdf[sdf["upcoming"]]

    # Apply sort
    sort_map = {
        "TWh/year ↓":    ("twh_year", False),
        "TWh/year ↑":    ("twh_year", True),
        "Facilities ↓":  ("dc_count", False),
        "Facilities ↑":  ("dc_count", True),
        "State A→Z":     ("state", True),
    }
    sort_col, sort_asc = sort_map[sort_by]
    sdf = sdf.sort_values(sort_col, ascending=sort_asc).reset_index(drop=True)

    # --- Bar chart ---
    top_n = min(25, len(sdf))
    chart_df = sdf.head(top_n).copy()
    chart_df["label"] = chart_df["abbrev"] + ("  🔜" if False else "")   # flag via color
    bar = (
        alt.Chart(chart_df)
        .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
        .encode(
            x=alt.X("twh_year:Q", title="TWh / year"),
            y=alt.Y("state:N", sort="-x" if "↓" in sort_by and "TWh" in sort_by else None,
                    title=None),
            color=alt.Color(
                "upcoming:N",
                scale=alt.Scale(domain=[True, False], range=["#ff5a1f", "#3b82f6"]),
                legend=alt.Legend(title="Major projects upcoming", labelExpr=(
                    "datum.label === 'true' ? '🔜 Yes' : 'No'"
                ))
            ),
            tooltip=[
                alt.Tooltip("state:N", title="State"),
                alt.Tooltip("dc_count:Q", title="Active facilities"),
                alt.Tooltip("twh_year:Q", title="TWh/year"),
                alt.Tooltip("major_hubs:N", title="Hubs & operators"),
            ],
        )
        .properties(height=max(280, 22 * top_n), title=f"Top {top_n} states by TWh/year (orange = major projects underway)")
    )
    st.altair_chart(bar, use_container_width=True)

    # --- Sortable table ---
    display_df = sdf[["state", "abbrev", "dc_count", "twh_year", "major_hubs", "upcoming"]].copy()
    display_df["upcoming"] = display_df["upcoming"].map({True: "🔜 Yes", False: "—"})
    display_df.index = range(1, len(display_df) + 1)
    st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            "state":      st.column_config.TextColumn("State"),
            "abbrev":     st.column_config.TextColumn("Abbrev.", width="small"),
            "dc_count":   st.column_config.NumberColumn("Active Facilities", format="%d"),
            "twh_year":   st.column_config.NumberColumn("TWh / year", format="%.1f"),
            "major_hubs": st.column_config.TextColumn("Major Hubs & Operators", width="large"),
            "upcoming":   st.column_config.TextColumn("Projects Underway", width="small"),
        }
    )
    st.caption(
        f"Showing {len(sdf)} of 51 entries (50 states + D.C.).  "
        f"Source: {src_link('electricchoice')} · Underlying data: {src_link('lbnl')}"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Mega-projects leaderboard ---
    st.divider()
    st.subheader("💰 Largest data center projects under construction (2024–2028)")
    st.caption(
        "Top 10 individual megaprojects ranked by announced investment. "
        "Represents hundreds of billions in committed capital and tens of GW of new AI compute capacity. "
        f"Source: {src_link('electricchoice')} · {src_link('stargate')} · {src_link('xai_memphis')}"
    )

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    mp = MEGA_PROJECTS_DF.copy()
    st.dataframe(
        mp,
        use_container_width=True,
        hide_index=True,
        column_config={
            "project":  st.column_config.TextColumn("Project"),
            "company":  st.column_config.TextColumn("Company"),
            "location": st.column_config.TextColumn("Location"),
            "invest":   st.column_config.TextColumn("Investment"),
            "capacity": st.column_config.TextColumn("Power Capacity"),
            "status":   st.column_config.TextColumn("Status"),
        }
    )
    st.markdown('</div>', unsafe_allow_html=True)

