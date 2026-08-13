"""
Unified Map tab — consolidates all geographic views into a single interactive
Plotly Mapbox map with togglable layers and a click-to-select info panel that
shows everything about the selected point.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.constants import (DC_SITES_DF, DATACENTERS_DF, MORATORIUMS_DF,
                           PROJECTS_DF, PROJECT_EVENTS, STATE_DC_DF,
                           STATE_GRID_PROFILES, OPERATORS, COMPANY_CONCESSIONS,
                           LOCAL_BODIES_DF, LOCAL_OFFICIALS_DF, has_value)
from src.helpers import src_link
from src.ui.state_detail import render_state_profile

_REGION_PRESETS = {
    "Full USA": {"lat": 39.5, "lon": -98.5, "zoom": 3.2},
    "Data Center Alley (NoVA)": {"lat": 39.04, "lon": -77.5, "zoom": 9},
    "Dallas-Fort Worth": {"lat": 32.78, "lon": -96.8, "zoom": 9},
    "Silicon Valley / Bay Area": {"lat": 37.4, "lon": -122.0, "zoom": 9},
    "Central Ohio": {"lat": 40.08, "lon": -82.8, "zoom": 9},
    "Phoenix / Mesa, AZ": {"lat": 33.45, "lon": -111.9, "zoom": 9},
    "Pacific NW (OR / WA)": {"lat": 45.5, "lon": -120.5, "zoom": 7},
    "Texas (statewide)": {"lat": 31.5, "lon": -99.5, "zoom": 5.5},
    "Memphis, TN (xAI)": {"lat": 35.06, "lon": -90.06, "zoom": 10},
    "Abilene, TX (Stargate)": {"lat": 32.45, "lon": -99.7, "zoom": 10},
}

_MAP_STYLES = {
    "Dark": "carto-darkmatter",
    "Road": "open-street-map",
    "Light": "carto-positron",
}

_STAGE_COLORS = {
    "hearing_soon": "#ef4444",
    "approved": "#34d399",
    "denied": "#94a3b8",
    "withdrawn": "#94a3b8",
    "default": "#fbbf24",
}

_ATTRIB_LABELS = {
    "first_party": "First-party (operator site)",
    "deed": "County deed / assessor",
    "leasing_news": "Leasing announcement",
    "press": "Trade press",
    "inferred": "Inferred",
}


def _project_color(row):
    if row.get("hearing_soon"):
        return _STAGE_COLORS["hearing_soon"]
    stage = str(row.get("stage", "")).lower()
    if "approv" in stage:
        return _STAGE_COLORS["approved"]
    if "denied" in stage or "withdrawn" in stage:
        return _STAGE_COLORS["denied"]
    return _STAGE_COLORS["default"]


def _abbrev_to_state(abbrev):
    match = STATE_DC_DF[STATE_DC_DF["abbrev"] == abbrev]
    if not match.empty:
        return match.iloc[0]["state"]
    return abbrev


def render_map_tab():
    st.subheader("Interactive Map")
    st.caption(
        "All tracked data center campuses, active projects, and moratoriums "
        "on one map. Click any point for full details."
    )

    # ── Controls ──────────────────────────────────────────────────────── #
    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([2, 2, 1.5, 1.5])

    with ctrl1:
        all_ops = sorted(DC_SITES_DF["operator"].unique())
        selected_ops = st.multiselect(
            "Filter operators", all_ops, default=all_ops, key="umap_ops")

    with ctrl2:
        all_states = sorted(set(
            list(DC_SITES_DF["state"].unique()) +
            list(MORATORIUMS_DF["state"].unique()) +
            list(PROJECTS_DF["state"].unique())
        ))
        my_state = st.session_state.get("my_state_abbrev")
        default_states = [my_state] if my_state and my_state in all_states else all_states
        selected_states = st.multiselect(
            "Filter states", all_states, default=default_states, key="umap_states")

    with ctrl3:
        preset = st.selectbox("Jump to region", list(_REGION_PRESETS.keys()),
                              key="umap_preset")

    with ctrl4:
        map_style = st.radio("Style", list(_MAP_STYLES.keys()),
                             horizontal=True, key="umap_style")

    layer_cols = st.columns(4)
    show_campuses = layer_cols[0].checkbox("Campuses", value=True, key="umap_l_campus")
    show_projects = layer_cols[1].checkbox("Projects", value=True, key="umap_l_proj")
    show_morats = layer_cols[2].checkbox("Moratoriums", value=True, key="umap_l_morat")
    show_markets = layer_cols[3].checkbox("Markets (MW)", value=False, key="umap_l_market")

    # ── Metrics row ───────────────────────────────────────────────────── #
    campus_count = len(DC_SITES_DF[
        DC_SITES_DF["operator"].isin(selected_ops) &
        DC_SITES_DF["state"].isin(selected_states)
    ]) if show_campuses else 0
    proj_df = PROJECTS_DF[PROJECTS_DF["state"].isin(selected_states)]
    proj_count = len(proj_df) if show_projects else 0
    hearing_count = proj_df["hearing_soon"].sum() if show_projects and not proj_df.empty else 0
    morat_count = len(MORATORIUMS_DF[
        MORATORIUMS_DF["state"].isin(selected_states)
    ]) if show_morats else 0

    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Campuses", campus_count)
    mc2.metric("Projects", f"{proj_count}", f"{int(hearing_count)} hearing soon" if hearing_count else None)
    mc3.metric("Moratoriums", morat_count)

    # ── Build figure ──────────────────────────────────────────────────── #
    fig = go.Figure()
    vp = _REGION_PRESETS[preset]
    op_colors = {name: m[6] for name, m in OPERATORS.items()}

    # Layer 1: DC campuses
    if show_campuses:
        cdf = DC_SITES_DF[
            DC_SITES_DF["operator"].isin(selected_ops) &
            DC_SITES_DF["state"].isin(selected_states)
        ].copy()
        if not cdf.empty:
            cdf["_owner_label"] = cdf["owner"].replace("self", "Self-owned")
            cdf["_tenant_label"] = cdf["tenant"].fillna("Undisclosed")
            cdf["_attrib_label"] = cdf["attribution"].map(_ATTRIB_LABELS).fillna("Unknown")
            cdf["_color"] = cdf["operator"].map(
                lambda o: op_colors.get(o, "#6b7280"))
            cdf["_layer"] = "campus"
            fig.add_trace(go.Scattermapbox(
                lat=cdf["lat"], lon=cdf["lon"],
                mode="markers",
                marker=dict(size=9, color=cdf["_color"],
                            opacity=0.85),
                text=cdf["operator"] + " — " + cdf["location"] + ", " + cdf["state"],
                customdata=list(zip(
                    cdf["_layer"], cdf.index,
                    cdf["operator"], cdf["location"], cdf["state"],
                    cdf["_owner_label"], cdf["_tenant_label"],
                    cdf["_attrib_label"], cdf["src"]
                )),
                hovertemplate=(
                    "<b>%{customdata[2]}</b><br>"
                    "%{customdata[3]}, %{customdata[4]}<br>"
                    "Owner: %{customdata[5]}<br>"
                    "Tenant: %{customdata[6]}<br>"
                    "Source: %{customdata[7]}"
                    "<extra>Campus</extra>"
                ),
                name="Campuses",
                showlegend=True,
            ))

    # Layer 2: Tracked projects
    if show_projects:
        pdf = PROJECTS_DF[PROJECTS_DF["state"].isin(selected_states)].copy()
        pdf = pdf[pdf["lat"].notna() & pdf["lon"].notna()]
        if not pdf.empty:
            pdf["_color"] = pdf.apply(_project_color, axis=1)
            pdf["_mw_str"] = pdf["size_mw"].apply(
                lambda v: f"{v:.0f} MW" if has_value(v) else "TBD")
            pdf["_layer"] = "project"
            fig.add_trace(go.Scattermapbox(
                lat=pdf["lat"], lon=pdf["lon"],
                mode="markers",
                marker=dict(size=12, color=pdf["_color"],
                            opacity=0.9, symbol="circle"),
                text=pdf["name"] + " — " + pdf["locality"] + ", " + pdf["state"],
                customdata=list(zip(
                    pdf["_layer"], pdf["id"],
                    pdf["name"], pdf["operator"], pdf["locality"],
                    pdf["state"], pdf["_mw_str"], pdf["stage"],
                    pdf["next_action"]
                )),
                hovertemplate=(
                    "<b>%{customdata[2]}</b><br>"
                    "%{customdata[4]}, %{customdata[5]}<br>"
                    "Operator: %{customdata[3]}<br>"
                    "%{customdata[6]} · %{customdata[7]}<br>"
                    "%{customdata[8]}"
                    "<extra>Project</extra>"
                ),
                name="Projects",
                showlegend=True,
            ))

    # Layer 3: Moratoriums
    if show_morats:
        mdf = MORATORIUMS_DF[MORATORIUMS_DF["state"].isin(selected_states)].copy()
        mdf = mdf[mdf["lat"].notna() & mdf["lon"].notna()]
        if not mdf.empty:
            mdf["_note"] = mdf["note"].apply(lambda v: v if has_value(v) else "")
            mdf["_layer"] = "moratorium"
            mdf["_verified"] = mdf["verified"].map({True: "Verified", False: "Unverified"})
            fig.add_trace(go.Scattermapbox(
                lat=mdf["lat"], lon=mdf["lon"],
                mode="markers",
                marker=dict(size=8, color="#a855f7", opacity=0.8),
                text=mdf["locality"] + ", " + mdf["state"] + " — " + mdf["effective_status"],
                customdata=list(zip(
                    mdf["_layer"], mdf.index,
                    mdf["locality"], mdf["state"], mdf["effective_status"],
                    mdf["when"], mdf["_note"], mdf["_verified"]
                )),
                hovertemplate=(
                    "<b>%{customdata[2]}, %{customdata[3]}</b><br>"
                    "Status: %{customdata[4]}<br>"
                    "%{customdata[5]}<br>"
                    "%{customdata[7]}"
                    "<extra>Moratorium</extra>"
                ),
                name="Moratoriums",
                showlegend=True,
            ))

    # Layer 4: Markets (MW)
    if show_markets:
        mkdf = DATACENTERS_DF[DATACENTERS_DF["region"] == "US"].copy()
        if not mkdf.empty:
            mkdf["_layer"] = "market"
            mkdf["_mw_total"] = mkdf[["mw", "uc", "planned"]].sum(axis=1)
            fig.add_trace(go.Scattermapbox(
                lat=mkdf["lat"], lon=mkdf["lon"],
                mode="markers",
                marker=dict(
                    size=mkdf["_mw_total"].clip(lower=100) / 80,
                    color="#ff5a1f", opacity=0.5,
                    sizemode="area",
                ),
                text=mkdf["market"],
                customdata=list(zip(
                    mkdf["_layer"], mkdf.index,
                    mkdf["market"], mkdf["grid"],
                    mkdf["mw"].fillna(0).astype(int),
                    mkdf["uc"].fillna(0).astype(int),
                    mkdf["planned"].fillna(0).astype(int),
                    mkdf["src"]
                )),
                hovertemplate=(
                    "<b>%{customdata[2]}</b><br>"
                    "Grid: %{customdata[3]}<br>"
                    "Operational: %{customdata[4]} MW<br>"
                    "Under construction: %{customdata[5]} MW<br>"
                    "Planned: %{customdata[6]} MW"
                    "<extra>Market</extra>"
                ),
                name="Markets (MW)",
                showlegend=True,
            ))

    fig.update_layout(
        mapbox=dict(
            style=_MAP_STYLES[map_style],
            center=dict(lat=vp["lat"], lon=vp["lon"]),
            zoom=vp["zoom"],
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=560,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h", y=1.0, yanchor="bottom", x=0,
            bgcolor="rgba(0,0,0,0.4)", font=dict(color="white", size=11),
        ),
        showlegend=True,
    )

    event = st.plotly_chart(fig, use_container_width=True,
                            on_select="rerun", key="unified_map",
                            selection_mode="points")

    st.caption(
        "Click any point for full details. "
        "Map tiles: CARTO/OpenStreetMap. Campus coordinates are "
        "town/county/metro centroids, not surveyed GPS positions."
    )

    # ── Click handler — unified info panel ────────────────────────────── #
    picked_points = []
    try:
        if event.selection and "points" in event.selection:
            picked_points = event.selection["points"]
    except (AttributeError, KeyError, TypeError):
        pass

    if not picked_points:
        st.info("Click a point on the map to see full details — site info, state context, "
                "moratoriums, officials, projects, and news, all in one place.")
        return

    point = picked_points[0]
    cd = point.get("customdata", [])
    if not cd or len(cd) < 2:
        return

    layer_type = cd[0]
    row_id = cd[1]

    st.divider()

    if layer_type == "campus":
        _render_campus_detail(cd)
    elif layer_type == "project":
        _render_project_detail(cd)
    elif layer_type == "moratorium":
        _render_moratorium_detail(cd)
    elif layer_type == "market":
        _render_market_detail(cd)


def _render_campus_detail(cd):
    """Info panel for a clicked campus point."""
    _, idx, operator, location, state_abbrev, owner, tenant, attrib, src_key = cd

    state_name = _abbrev_to_state(state_abbrev)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f"### {operator} — {location}, {state_abbrev}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Owner", owner)
    c2.metric("Tenant", tenant)
    c3.metric("Source", attrib)
    if has_value(src_key):
        st.caption(f"Attribution: {src_link(src_key)}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Company concessions
    concessions = COMPANY_CONCESSIONS.get(operator)
    if concessions:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f"#### Negotiation Intel: {operator}")
        st.markdown(concessions.get("pattern", ""))
        for c in concessions.get("concessions", [])[:3]:
            where = c.get("where", "")
            what = c.get("what", "")
            st.markdown(f"- **{where}**: {what}")
        st.markdown('</div>', unsafe_allow_html=True)

    # State context + everything else
    _render_state_context(state_name, state_abbrev)
    _render_locality_officials(None, state_abbrev)
    _render_nearby_moratoriums(state_abbrev)
    _render_nearby_projects(state_abbrev)


def _render_project_detail(cd):
    """Info panel for a clicked project point."""
    _, proj_id, name, operator, locality, state_abbrev, mw_str, stage, next_action = cd

    state_name = _abbrev_to_state(state_abbrev)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f"### {name}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Operator", operator if has_value(operator) else "Unknown")
    c2.metric("Location", f"{locality}, {state_abbrev}")
    c3.metric("Size", mw_str)
    c4.metric("Stage", stage)
    if has_value(next_action):
        st.info(f"**Next action:** {next_action}")

    # Full project details from PROJECTS_DF
    proj_row = PROJECTS_DF[PROJECTS_DF["id"] == proj_id]
    if not proj_row.empty:
        p = proj_row.iloc[0]
        details = []
        if has_value(p.get("owner")):
            details.append(f"**Owner:** {p['owner']}")
        if has_value(p.get("tenant")):
            details.append(f"**Tenant:** {p['tenant']}")
        if has_value(p.get("filing_llc")):
            details.append(f"**Filing LLC:** {p['filing_llc']}")
        if has_value(p.get("acres")):
            details.append(f"**Acres:** {p['acres']}")
        if has_value(p.get("hearing_date")):
            details.append(f"**Hearing date:** {p['hearing_date']}")
        if has_value(p.get("decided_date")):
            details.append(f"**Decided:** {p['decided_date']}")
        if has_value(p.get("outcome")):
            details.append(f"**Outcome:** {p['outcome']}")
        if has_value(p.get("note")):
            details.append(f"**Note:** {p['note']}")
        if has_value(p.get("source")):
            details.append(f"**Source:** [{p['source']}]({p['source']})")
        if details:
            st.markdown(" · ".join(details))

    # Events timeline
    events = PROJECT_EVENTS.get(proj_id, [])
    if events:
        st.markdown("#### Timeline")
        for ev in events:
            date = ev.get("date", "")
            kind = ev.get("kind", "")
            summary = ev.get("summary", "")
            src = ev.get("source", "")
            src_md = f" ([source]({src}))" if src else ""
            st.markdown(f"- **{date}** [{kind}] — {summary}{src_md}")

    st.markdown('</div>', unsafe_allow_html=True)

    # Company concessions
    if has_value(operator):
        concessions = COMPANY_CONCESSIONS.get(operator)
        if concessions:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(f"#### Negotiation Intel: {operator}")
            st.markdown(concessions.get("pattern", ""))
            for c in concessions.get("concessions", [])[:3]:
                st.markdown(f"- **{c.get('where', '')}**: {c.get('what', '')}")
            st.markdown('</div>', unsafe_allow_html=True)

    _render_state_context(state_name, state_abbrev)
    _render_locality_officials(locality, state_abbrev)
    _render_nearby_moratoriums(state_abbrev, locality)


def _render_moratorium_detail(cd):
    """Info panel for a clicked moratorium point."""
    _, idx, locality, state_abbrev, effective_status, when, note, verified = cd

    state_name = _abbrev_to_state(state_abbrev)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f"### Moratorium: {locality}, {state_abbrev}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Status", effective_status)
    c2.metric("Enacted", when if has_value(when) else "Unknown")
    c3.metric("Verification", verified)

    # Full row from MORATORIUMS_DF
    morat_row = MORATORIUMS_DF.iloc[idx] if idx < len(MORATORIUMS_DF) else None
    if morat_row is not None:
        details = []
        if has_value(morat_row.get("level")):
            details.append(f"**Level:** {morat_row['level']}")
        if has_value(morat_row.get("expires")):
            details.append(f"**Expires:** {morat_row['expires']}")
        if has_value(morat_row.get("days_left")):
            details.append(f"**Days left:** {morat_row['days_left']}")
        if morat_row.get("expiring_soon"):
            details.append("**Expiring soon**")
        if details:
            st.markdown(" · ".join(details))
        if has_value(note):
            st.markdown(f"*{note}*")
        if has_value(morat_row.get("source")):
            st.caption(f"Source: [{morat_row['source']}]({morat_row['source']})")
        if has_value(morat_row.get("as_of")):
            st.caption(f"Last verified: {morat_row['as_of']}")

    st.markdown('</div>', unsafe_allow_html=True)

    _render_locality_officials(locality, state_abbrev)
    _render_nearby_projects(state_abbrev, locality)
    _render_state_context(state_name, state_abbrev)


def _render_market_detail(cd):
    """Info panel for a clicked market point."""
    _, idx, market, grid, mw, uc, planned, src_key = cd

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f"### Market: {market}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Operational", f"{mw:,} MW")
    c2.metric("Under Construction", f"{uc:,} MW")
    c3.metric("Planned", f"{planned:,} MW")
    c4.metric("Grid ISO", grid if has_value(grid) else "N/A")
    if has_value(src_key):
        st.caption(f"Source: {src_link(src_key)}")
    st.markdown('</div>', unsafe_allow_html=True)


def _render_state_context(state_name, state_abbrev):
    """Collapsible state context card."""
    row = STATE_DC_DF[STATE_DC_DF["abbrev"] == state_abbrev]
    if row.empty:
        return
    row = row.iloc[0]
    grid_prof = STATE_GRID_PROFILES.get(state_name, {})

    with st.expander(f"State context: {state_name}", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.metric("Facilities", row["dc_count"])
        c2.metric("Power Draw", f"{row['twh_year']:.1f} TWh/yr")
        c3.metric("Major Hubs", row["major_hubs"][:30] + "..." if len(str(row["major_hubs"])) > 30 else row["major_hubs"])
        if grid_prof:
            g1, g2, g3 = st.columns(3)
            g1.metric("Residential Rate", f"\\${grid_prof.get('rate', 0):.2f}/kWh")
            g2.metric("Grid Carbon", f"{grid_prof.get('gco2', 0)} gCO\\u2082/kWh")
            g3.metric("Water Stress", grid_prof.get("water_stress", "unknown").title())
        st.caption(f"[Full state profile on aigridwatch.com](https://aigridwatch.com/states/{state_name.lower().replace(' ', '-')})")


def _render_locality_officials(locality, state_abbrev):
    """Show local officials and governing bodies for a locality."""
    bodies = LOCAL_BODIES_DF[LOCAL_BODIES_DF["state"] == state_abbrev]
    officials = LOCAL_OFFICIALS_DF[LOCAL_OFFICIALS_DF["state"] == state_abbrev]
    if locality:
        loc_bodies = bodies[bodies["locality"].str.lower() == locality.lower()]
        loc_officials = officials[officials["locality"].str.lower() == locality.lower()]
        if not loc_bodies.empty or not loc_officials.empty:
            bodies = loc_bodies
            officials = loc_officials

    if bodies.empty and officials.empty:
        return

    with st.expander(f"Local officials & governing bodies ({len(officials)} officials, {len(bodies)} bodies)", expanded=False):
        if not bodies.empty:
            for _, b in bodies.iterrows():
                parts = [f"**{b['body']}** — {b['locality']}, {b['state']}"]
                if has_value(b.get("meets")):
                    parts.append(f"Meets: {b['meets']}")
                if has_value(b.get("comment_process")):
                    parts.append(f"Comment: {b['comment_process']}")
                if has_value(b.get("website")):
                    parts.append(f"[Website]({b['website']})")
                st.markdown(" · ".join(parts))

        if not officials.empty:
            st.markdown("**Officials:**")
            for _, o in officials.iterrows():
                parts = [f"**{o['name']}** — {o['role']}"]
                if has_value(o.get("email")):
                    parts.append(o["email"])
                if has_value(o.get("phone")):
                    parts.append(o["phone"])
                if has_value(o.get("stance")):
                    parts.append(f"Stance: {o['stance']}")
                st.markdown("- " + " · ".join(parts))


def _render_nearby_moratoriums(state_abbrev, locality=None):
    """Show moratoriums in the same state (or locality)."""
    morats = MORATORIUMS_DF[MORATORIUMS_DF["state"] == state_abbrev]
    if locality:
        loc_morats = morats[morats["locality"].str.lower() == locality.lower()]
        if not loc_morats.empty:
            morats = loc_morats
    if morats.empty:
        return

    with st.expander(f"Moratoriums in area ({len(morats)})", expanded=False):
        for _, m in morats.iterrows():
            status = m["effective_status"]
            loc = m["locality"]
            note = m["note"] if has_value(m["note"]) else ""
            src = f" · [Source]({m['source']})" if has_value(m["source"]) else " · *Unverified*"
            st.markdown(f"- **{loc}** — {status}{' · ' + note if note else ''}{src}")


def _render_nearby_projects(state_abbrev, locality=None):
    """Show projects in the same state (or locality)."""
    projs = PROJECTS_DF[PROJECTS_DF["state"] == state_abbrev]
    if locality:
        loc_projs = projs[projs["locality"].str.lower() == locality.lower()]
        if not loc_projs.empty:
            projs = loc_projs
    if projs.empty:
        return

    with st.expander(f"Projects in area ({len(projs)})", expanded=False):
        for _, p in projs.iterrows():
            mw_str = f" · {p['size_mw']:.0f} MW" if has_value(p["size_mw"]) else ""
            st.markdown(f"- **{p['name']}** ({p['locality']}){mw_str} — {p['stage']}")
