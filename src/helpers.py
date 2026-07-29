from src.constants import SOURCES, registry_provenance

def human_energy(wh: float) -> str:
    """Format energy (Wh) into equivalent hours/minutes of TV watching."""
    tv_seconds = wh / 0.24 * 9
    if tv_seconds < 60:
        return f"≈ {tv_seconds:.0f} seconds of watching TV"
    if tv_seconds < 3600:
        return f"≈ {tv_seconds/60:.1f} minutes of watching TV"
    return f"≈ {tv_seconds/3600:.1f} hours of watching TV"


def human_water(ml: float) -> str:
    """Format water volume (mL) into drops or liters."""
    drops = ml / 0.05
    return f"≈ {drops:.0f} drops of water" if drops < 100 else f"≈ {ml/1000:.2f} L of water"


def src_link(key: str) -> str:
    """Generate a markdown link to a primary source from constants.py."""
    if key not in SOURCES:
        return f"[{key}](https://www.google.com/)"
    name, url = SOURCES[key]
    return f"[{name}]({url})"


def freshness_caption(registry_key: str) -> str:
    """One-line 'as of' caption for a registry, for st.caption().

    Returns "" when the registry has no provenance entry, so callers can drop
    it in unconditionally. Escapes '$' because st.caption renders markdown.
    """
    p = registry_provenance(registry_key)
    if not p:
        return ""
    bits = [p["line"]]
    if p.get("source"):
        bits.append(f"Source: {src_link(p['source'])}")
    return " · ".join(bits).replace("$", "\\$")


def render_freshness(st, registry_key: str, expanded: bool = False) -> None:
    """Render a registry's provenance: freshness line + collapsible caveat.

    A dataset past its churn-based shelf life gets a visible warning rather
    than a grey caption — the whole point is that a resident should not
    quote a number at a hearing without knowing it may have moved.

    Takes `st` as an argument so this module stays Streamlit-free at import
    time, matching the rest of helpers.py.
    """
    p = registry_provenance(registry_key)
    if not p:
        return
    line = freshness_caption(registry_key)
    if p["stale"]:
        st.warning(f"⏳ **{line}**")
    else:
        st.caption(line)
    if p.get("caveat"):
        with st.expander("How current is this? — read before citing it",
                         expanded=expanded or p["stale"]):
            st.markdown(p["caveat"].replace("$", "\\$"))
