import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import pydeck as pdk
from src.constants import (DATACENTERS_DF, DC_METRICS, ERCOT_LL_VINTAGE,
                           ERCOT_LL_DC_SHARE, ERCOT_LL_FUNNEL, HYPERSCALERS_DF,
                           HYPERSCALER_COLORS, AI_COMPETITOR_SITES_DF,
                           DC_SITES_DF, OPERATORS)
from src.helpers import src_link
from src.services.ercot import ercot_largeload_latest
from src.services.eia import eia_latest_demand
from src.services.secrets import load_local_secrets

def _hex_to_rgb(hex_color):
    """Convert '#rrggbb' to [r, g, b, a]."""
    h = hex_color.lstrip("#")
    return [int(h[i:i+2], 16) for i in (0, 2, 4)] + [200]

_REGION_PRESETS = {
    "Full USA": {"lat": 39.5, "lon": -98.5, "zoom": 3.5, "pitch": 0},
    "Data Center Alley (NoVA)": {"lat": 39.04, "lon": -77.5, "zoom": 9, "pitch": 30},
    "Dallas–Fort Worth": {"lat": 32.78, "lon": -96.8, "zoom": 9, "pitch": 30},
    "Silicon Valley / Bay Area": {"lat": 37.4, "lon": -122.0, "zoom": 9, "pitch": 30},
    "Central Ohio": {"lat": 40.08, "lon": -82.8, "zoom": 9, "pitch": 30},
    "Phoenix / Mesa, AZ": {"lat": 33.45, "lon": -111.9, "zoom": 9, "pitch": 30},
    "Pacific NW (OR / WA)": {"lat": 45.5, "lon": -120.5, "zoom": 7, "pitch": 20},
    "Texas (statewide)": {"lat": 31.5, "lon": -99.5, "zoom": 5.5, "pitch": 15},
    "Memphis, TN (xAI)": {"lat": 35.06, "lon": -90.06, "zoom": 10, "pitch": 30},
    "Abilene, TX (Stargate)": {"lat": 32.45, "lon": -99.7, "zoom": 10, "pitch": 30},
}

def _render_interactive_map():
    """Detailed, zoomable interactive map of all US data center sites."""
    st.subheader("🗺️ Interactive US data center map")
    st.caption(
        "Explore every tracked data center campus on a zoomable street-level "
        "map. Zoom in to see individual sites; hover for operator, owner, "
        "tenant, and attribution details. Color-coded by operator."
    )

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    all_sites = DC_SITES_DF.copy()
    all_sites["_owner_label"] = all_sites["owner"].replace("self", "Self-owned")
    all_sites["_tenant_label"] = all_sites["tenant"].fillna("Undisclosed")
    all_sites["_attrib_label"] = all_sites["attribution"].map({
        "first_party": "First-party (operator site)",
        "deed": "County deed / assessor",
        "leasing_news": "Leasing announcement",
        "press": "Trade press",
        "inferred": "Inferred",
    }).fillna("Unknown")

    op_colors = {name: m[6] for name, m in OPERATORS.items()}
    all_sites["color"] = all_sites["operator"].map(
        lambda o: _hex_to_rgb(op_colors.get(o, "#6b7280")))

    fc1, fc2 = st.columns([3, 2])
    operators = sorted(all_sites["operator"].unique())
    selected_ops = fc1.multiselect(
        "Filter by operator", operators, default=operators,
        key="map_op_filter")
    states = sorted(all_sites["state"].unique())
    selected_states = fc2.multiselect(
        "Filter by state", states, default=states,
        key="map_state_filter")

    filtered = all_sites[
        all_sites["operator"].isin(selected_ops) &
        all_sites["state"].isin(selected_states)
    ].copy()

    rc1, rc2, rc3 = st.columns([2, 1, 1])
    preset = rc1.selectbox("Jump to region", list(_REGION_PRESETS.keys()),
                           key="map_preset")
    map_style = rc2.radio("Map style", ["Road", "Satellite", "Dark"],
                          horizontal=True, key="map_style")
    show_labels = rc3.checkbox("Show site labels", value=False, key="map_labels")

    style_urls = {
        "Road": "road",
        "Satellite": "satellite",
        "Dark": "dark",
    }

    vp = _REGION_PRESETS[preset]

    m1, m2, m3 = st.columns(3)
    m1.metric("Sites shown", f"{len(filtered)}")
    m2.metric("Operators", f"{filtered['operator'].nunique()}")
    m3.metric("States", f"{filtered['state'].nunique()}")

    if filtered.empty:
        st.info("No sites match the current filters. Broaden the selection.")
    else:
        tooltip = {
            "html": (
                "<div style='font-family:sans-serif;padding:4px'>"
                "<b style='font-size:14px'>{operator}</b><br/>"
                "<span style='color:#C8D0DA'>📍</span> {location}, {state}<br/>"
                "<span style='color:#C8D0DA'>Owner:</span> {_owner_label}<br/>"
                "<span style='color:#C8D0DA'>Tenant:</span> {_tenant_label}<br/>"
                "<span style='color:#C8D0DA'>Source:</span> {_attrib_label}"
                "</div>"
            ),
            "style": {
                "backgroundColor": "#1a1a2e",
                "color": "white",
                "border": "1px solid #333",
                "border-radius": "6px",
            }
        }

        layers = [
            pdk.Layer(
                "ScatterplotLayer",
                data=filtered,
                get_position=["lon", "lat"],
                get_fill_color="color",
                get_radius=6000,
                radius_min_pixels=4,
                radius_max_pixels=20,
                pickable=True,
                auto_highlight=True,
                highlight_color=[255, 255, 0, 100],
            ),
        ]

        if show_labels:
            layers.append(
                pdk.Layer(
                    "TextLayer",
                    data=filtered,
                    get_position=["lon", "lat"],
                    get_text="location",
                    get_size=12,
                    get_color=[255, 255, 255, 200],
                    get_angle=0,
                    get_text_anchor="'middle'",
                    get_alignment_baseline="'top'",
                    get_pixel_offset=[0, 12],
                )
            )

        deck = pdk.Deck(
            layers=layers,
            initial_view_state=pdk.ViewState(
                latitude=vp["lat"],
                longitude=vp["lon"],
                zoom=vp["zoom"],
                pitch=vp["pitch"],
                bearing=0,
            ),
            map_style=style_urls[map_style],
            tooltip=tooltip,
        )
        st.pydeck_chart(deck, use_container_width=True)

    with st.expander("Map legend — operator colors"):
        legend_items = []
        for op in sorted(filtered["operator"].unique()):
            c = op_colors.get(op, "#6b7280")
            count = len(filtered[filtered["operator"] == op])
            legend_items.append(
                f'<span style="display:inline-block;width:12px;height:12px;'
                f'border-radius:50%;background:{c};margin-right:6px"></span>'
                f'**{op}** ({count} sites)')
        st.markdown("  \n".join(legend_items), unsafe_allow_html=True)

    st.caption(
        "Map tiles: OpenStreetMap / Mapbox. Data from operator first-party "
        "location pages, SEC filings, press, and deed records. Coordinates "
        "are town/county/metro centroids — not surveyed GPS positions."
    )
    st.markdown('</div>', unsafe_allow_html=True)

def render_dc_tab():
    with st.expander("📑 On this page", expanded=False):
        st.markdown(
            "**1.** Interactive US data center map · "
            "**2.** Market power by phase · "
            "**3.** Hyperscaler campuses & AI megasites · "
            "**4.** Live EIA-930 grid demand"
        )
    _render_interactive_map()
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

    campus_df = DC_SITES_DF.copy()
    campus_df["_owner_label"] = campus_df["owner"].replace("self", "Self-owned")
    campus_df["_tenant_label"] = campus_df["tenant"].fillna("Undisclosed")

    _OP_COLORS = {name: m[6] for name, m in OPERATORS.items()}
    _OWNER_COLORS = {
        "Self-owned": "#6b7280",
        "Blackstone": "#8b5cf6", "DigitalBridge + Silver Lake": "#0ea5e9",
        "KKR + Global Infrastructure Partners": "#22d3ee",
        "DigitalBridge + IFM Investors": "#ef4444",
        "Nvidia · Microsoft · BlackRock/MGX (pending)": "#f59e0b",
        "Blue Owl / IPI Partners": "#10b981",
        "EQT Infrastructure + ADIA": "#a3a3a3",
    }
    _TENANT_COLORS = {
        "Google": "#34a853", "Meta": "#0866ff", "Microsoft": "#f25022",
        "Amazon (AWS)": "#ff9900", "xAI (Colossus)": "#a855f7",
        "OpenAI": "#14b8a6", "CoreWeave": "#ec4899", "Undisclosed": "#6b7280",
    }

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    ccol, rcol = st.columns([3, 2])
    color_role = rcol.radio(
        "Color by", ["Operator", "Owner / PE parent", "Tenant"],
        horizontal=True, help="Switch the map legend between who runs the "
        "building (operator), who owns the company (PE parent), or who "
        "actually consumes the power (tenant).")
    _role_col = {"Operator": "operator", "Owner / PE parent": "_owner_label",
                 "Tenant": "_tenant_label"}[color_role]
    _role_colors = {"Operator": _OP_COLORS, "Owner / PE parent": _OWNER_COLORS,
                    "Tenant": _TENANT_COLORS}[color_role]

    role_vals = sorted(campus_df[_role_col].unique())
    firms = ccol.multiselect("Filter", role_vals, default=role_vals,
                             key="campus_filter")
    hdf = campus_df[campus_df[_role_col].isin(firms)].copy() if firms \
        else campus_df.copy()

    if hdf.empty:
        st.info("Pick a value to plot campuses.")
    else:
        h1, h2 = st.columns(2)
        h1.metric("Campuses shown", f"{len(hdf)}")
        h2.metric("States", f"{hdf.state.nunique()}")
        hdf["id"] = hdf["operator"] + " · " + hdf["location"]

        fig = px.scatter_geo(
            hdf, lat="lat", lon="lon", color=_role_col, scope="usa",
            color_discrete_map=_role_colors, hover_name="location",
            custom_data=["id", "operator", "location", "state",
                         "_owner_label", "_tenant_label", "attribution"])
        fig.update_traces(
            marker=dict(size=11, line=dict(width=0.5, color="white")),
            hovertemplate=(
                "<b>%{customdata[1]}</b> — %{customdata[2]}, %{customdata[3]}<br>"
                "Owner: %{customdata[4]}<br>"
                "Tenant: %{customdata[5]}<br>"
                "Source: %{customdata[6]}"
                "<extra></extra>"))
        fig.update_geos(bgcolor="rgba(0,0,0,0)", landcolor="#26272b",
                        subunitcolor="#3c3f44", showsubunits=True,
                        countrycolor="#3c3f44", lakecolor="rgba(0,0,0,0)")
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0), height=460,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(title=color_role, orientation="h",
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
                    f"**{r.operator} — {r['location']}, {r.state}**  \n"
                    f"Owner: {r._owner_label} · Tenant: {r._tenant_label} · "
                    f"Attribution: {r.attribution}  \n"
                    f"📍 {r.lat:.2f}, {r.lon:.2f}  ·  source: {src_link(r.src)}")
        else:
            st.caption("👆 Click a dot to see operator, owner & tenant details.")

        counts = " · ".join(f"{v} = {len(hdf[hdf[_role_col]==v])}"
                            for v in firms if len(hdf[hdf[_role_col] == v]))
        st.caption(counts)
        with st.expander("Site list + sources"):
            st.dataframe(
                hdf[["operator", "_owner_label", "_tenant_label",
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


