import requests
import re
import streamlit as st
from src.constants import ERCOT_LL_PAGE

@st.cache_data(ttl=3600, show_spinner=False)
def ercot_largeload_latest():
    """Best-effort scan of ERCOT's Large Load Integration page for the most
    recent report/document links. ERCOT publishes NO machine-readable large-load
    queue — the aggregate numbers live in dated PDFs/slides — so this just
    surfaces the newest posted document (by its /files/docs/YYYY/MM/DD/ date) so
    the user can tell whether fresher figures exist than the curated snapshot.
    Returns (latest_date_str, [(date, name, url), ...]) or None on any failure.
    Never raises — the tab must render offline."""
    try:
        r = requests.get(ERCOT_LL_PAGE, timeout=20,
                         headers={"User-Agent": "Mozilla/5.0 (AIGridTracker)"})
        r.raise_for_status()
        html = r.text
    except Exception:
        return None
    # ERCOT hosts docs at /files/docs/YYYY/MM/DD/<name>.<ext>; links appear as
    # either root-relative or absolute (https://www.ercot.com/...).
    seen, docs = set(), []
    for m in re.finditer(
            r'href="(?:https://www\.ercot\.com)?(/files/docs/'
            r'(\d{4})/(\d{2})/(\d{2})/([^"?]+))"', html):
        href, y, mo, d, fname = m.groups()
        if href in seen:
            continue
        seen.add(href)
        docs.append((f"{y}-{mo}-{d}", fname, "https://www.ercot.com" + href))
    if not docs:
        return None
    docs.sort(key=lambda t: t[0], reverse=True)
    return docs[0][0], docs[:8]
