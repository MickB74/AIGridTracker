"""
Market monitors & advocacy — a reference directory of two non-industry data
sources a community can cite at a rate case:

1. Independent Market Monitors (IMMs) — every organized US wholesale market has
   one, and each publishes an annual State of the Market report. These are the
   authoritative, non-utility numbers on capacity costs, congestion, and
   large-load (data-center) driven price impacts.
2. Ratepayer / consumer-advocacy organizations — the groups that formally
   intervene in PUC proceedings on behalf of residential customers, plus the
   quotable stats and model language they produce.

Static curated registries (constants.py) — no live fetch. Grid-aware: when the
sidebar "My Community" state is set, the relevant grid's monitor is surfaced.
"""

import streamlit as st
from src.constants import MARKET_MONITORS_DF, ADVOCACY_ORGS_DF, SOURCES
from src.helpers import src_link
from src.services.report_check import check_monitor_freshness

# Rough state → grid map, so a sidebar state selection can highlight the
# monitor that covers it. Only the clear-cut single-grid states are listed;
# split/overlapping states fall through to "no highlight".
_STATE_GRID = {
    "TX": "ERCOT", "CA": "CAISO",
    "PA": "PJM", "OH": "PJM", "NJ": "PJM", "MD": "PJM", "VA": "PJM",
    "DE": "PJM", "WV": "PJM", "DC": "PJM", "KY": "PJM",
    "IL": "MISO", "MI": "MISO", "MN": "MISO", "IN": "MISO", "WI": "MISO",
    "IA": "MISO", "LA": "MISO", "AR": "MISO", "MS": "MISO",
    "NY": "NYISO",
    "MA": "ISO-NE", "CT": "ISO-NE", "ME": "ISO-NE", "NH": "ISO-NE",
    "VT": "ISO-NE", "RI": "ISO-NE",
    "KS": "SPP", "OK": "SPP", "NE": "SPP", "ND": "SPP", "SD": "SPP",
}


def _url(key: str) -> str:
    """Bare URL for a SOURCES key (for LinkColumn), safe if missing."""
    return SOURCES.get(key, ("", ""))[1]


def render_monitors_tab():
    st.subheader("📑 Market monitors & advocacy")
    st.caption(
        "Two non-industry sources to arm a rate-case argument: the **independent "
        "market monitors** that publish the authoritative numbers on data-center "
        "cost impacts, and the **consumer-advocacy groups** that fight for "
        "residential ratepayers — with their quotable stats and who to contact."
    )

    my_grid = _STATE_GRID.get(st.session_state.get("my_state_abbrev", ""))

    # ── 1. Independent Market Monitors ──────────────────────────────────── #
    st.markdown("### 🛰️ Independent Market Monitors (State of the Market)")
    st.info(
        "Every organized wholesale market has an **independent** monitor "
        "(separate from the grid operator) that publishes an annual *State of "
        "the Market* report. Because they're independent of the utilities and "
        "developers, their capacity-cost, congestion, and large-load numbers "
        "carry weight a company can't easily dispute. All are PDF/landing-page "
        "reports — no login required."
    )

    if my_grid:
        hit = MARKET_MONITORS_DF[MARKET_MONITORS_DF["grid"] == my_grid]
        if not hit.empty:
            r = hit.iloc[0]
            st.success(
                f"**Your grid ({my_grid}):** {r['monitor']} publishes the "
                f"*{r['report']}* — {r['edition']}. Start here.  \n"
                f"→ {src_link(r['src_key'])}"
            )

    monitors = MARKET_MONITORS_DF.copy()
    monitors["Report link"] = monitors["src_key"].map(_url)
    st.dataframe(
        monitors[["grid", "region", "monitor", "report", "edition", "Report link"]],
        use_container_width=True, hide_index=True,
        column_config={
            "grid": "Grid",
            "region": "Region",
            "monitor": "Market monitor",
            "report": "Report",
            "edition": "Latest edition",
            "Report link": st.column_config.LinkColumn(
                "Open", display_text="View report"),
        },
    )

    with st.expander("💡 What to pull from these reports — the advocacy-relevant findings"):
        for _, r in MARKET_MONITORS_DF.iterrows():
            st.markdown(
                f"**{r['grid']} — {r['monitor']}:** {r['finding']}  \n"
                f"<small>Source: {src_link(r['src_key'])}"
                + ("" if r["finding_src"] == r["src_key"]
                   else f" · finding via {src_link(r['finding_src'])}")
                + "</small>",
                unsafe_allow_html=True,
            )
            st.markdown("")

    with st.expander("🔄 Check for newer editions (live)"):
        st.caption(
            "Scans each monitor's landing page for report years newer than "
            "the edition tracked above. Checked once per day."
        )
        freshness = check_monitor_freshness()
        any_newer = False
        for item in freshness:
            if item["status"] == "newer":
                any_newer = True
                st.warning(
                    f"**{item['grid']}:** a **{item['latest_seen']}** edition "
                    f"may be available (we track {item['have']}).  \n"
                    f"→ [Check the page]({item['url']})"
                )
            elif item["status"] == "current":
                st.markdown(
                    f"**{item['grid']}:** ✅ current (tracking {item['have']})"
                )
            elif item["status"] == "unreachable":
                st.markdown(
                    f"**{item['grid']}:** ⚠️ page unreachable — "
                    f"[check manually]({item['url']})"
                )
            else:
                st.markdown(
                    f"**{item['grid']}:** ❓ couldn't detect edition year — "
                    f"[check manually]({item['url']})"
                )
        if not any_newer:
            st.success("All tracked editions appear current.")

    st.divider()

    # ── 2. Consumer-advocacy organizations ──────────────────────────────── #
    st.markdown("### 🤝 Ratepayer & consumer-advocacy organizations")
    st.info(
        "These groups **intervene in rate cases and PUC proceedings** on behalf "
        "of residential and low-income customers. They are your natural allies, "
        "a source of model regulatory language, and — via NASUCA — the way to "
        "find your own state's official consumer advocate."
    )

    orgs = ADVOCACY_ORGS_DF.copy()
    orgs["Website"] = orgs["src_key"].map(_url)
    st.dataframe(
        orgs[["org", "scope", "type", "focus", "Website"]],
        use_container_width=True, hide_index=True,
        column_config={
            "org": "Organization",
            "scope": "Scope",
            "type": "Type",
            "focus": "Focus",
            "Website": st.column_config.LinkColumn("Site", display_text="Visit"),
        },
    )

    with st.expander("💬 Quotable stats & why each org matters"):
        for _, r in ADVOCACY_ORGS_DF.iterrows():
            st.markdown(
                f"**{r['org']}** ({r['scope']})  \n"
                f"{r['key_point']}  \n"
                f"<small>Source: {src_link(r['src_key'])}"
                + ("" if r["stat_src"] == r["src_key"]
                   else f" · stat via {src_link(r['stat_src'])}")
                + "</small>",
                unsafe_allow_html=True,
            )
            st.markdown("")

    st.info(
        "**See also:** the **Negotiation toolkit** tab for CBA templates and the "
        "data-dividend calculator, and **States & officials** for your state's "
        "PUC complaint links — the venue where these advocates file."
    )
