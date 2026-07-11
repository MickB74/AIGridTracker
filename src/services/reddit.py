import xml.etree.ElementTree as ET
import requests
import time
import pandas as pd
import streamlit as st
from src.constants import REDDIT_HOSTS, _ATOM, REDDIT_UA, REDDIT_PARQUET, NEWS_THEMES

def _parse_reddit_rss(content: bytes, limit: int):
    root = ET.fromstring(content)
    out = []
    for e in root.iter(_ATOM + "entry"):
        link_el = e.find(_ATOM + "link")
        cat = e.find(_ATOM + "category")
        out.append({
            "title": (e.findtext(_ATOM + "title") or "").strip(),
            "subreddit": (cat.get("label") or cat.get("term") or "")
                         if cat is not None else "",
            "link": link_el.get("href") if link_el is not None else "",
            "created": (e.findtext(_ATOM + "published") or "")[:10],
        })
        if len(out) >= limit:
            break
    return out


def _reddit_query(news_query: str) -> str:
    """Reshape a Google-News-style keyword bag into a Reddit search query that
    actually filters. Reddit's search is fuzzy/loose on space-separated terms
    (it happily returns posts matching none of them), so we anchor on the quoted
    core phrase ``"data center"`` and OR the descriptor words — that keeps every
    result on-topic instead of pulling in job listings and random threads."""
    words = news_query.split()
    if len(words) >= 2 and words[0].lower() == "data" and words[1].lower() == "center":
        rest = words[2:]
        base = '"data center"'
    else:
        rest, base = words, ""
    if rest:
        grp = " OR ".join(rest)
        return f'{base} ({grp})'.strip()
    return base or news_query


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_reddit(query: str, limit: int = 15, sort: str = "relevance",
                 period: str = "year"):
    """Live Reddit threads via the public Atom search RSS (keyless). Returns
    (list_of_dicts, error_or_None); each dict has title/subreddit/link/created.
    Tries old.reddit.com (rarely throttled) first, then www, each with a short
    backoff retry on 429."""
    params = {"q": query, "sort": sort, "t": period}
    last = "Reddit unreachable"
    for host in REDDIT_HOSTS:
        for attempt in range(3):
            try:
                r = requests.get(host, params=params,
                                 headers={"User-Agent": REDDIT_UA}, timeout=15)
                if r.status_code == 429:
                    last = "429 (rate-limited)"
                    time.sleep(1.5 * (attempt + 1))   # 1.5s, 3s, 4.5s
                    continue
                r.raise_for_status()
                if not r.content.lstrip().startswith(b"<"):
                    raise RuntimeError("Reddit returned non-XML "
                                       "(rate-limited or blocked)")
                return _parse_reddit_rss(r.content, limit), None
            except Exception as e:                                # noqa: BLE001
                last = str(e)
                break   # network/parse error on this host — try the next host
    return None, last


@st.cache_data(ttl=86400, show_spinner=False)
def load_reddit_corpus(day: str) -> tuple:
    """Fetch each NEWS_THEMES query's Reddit threads once per `day`
    (YYYY-MM-DD, which busts the daily cache) and persist to parquet. Returns
    (DataFrame[title, subreddit, link, created, theme], error_or_None). If the
    live fetch yields nothing, falls back to the last parquet on disk so the tab
    always has data to filter even when Reddit is down or rate-limiting."""
    prior = pd.DataFrame()
    if REDDIT_PARQUET.exists():
        try:
            prior = pd.read_parquet(REDDIT_PARQUET)
        except Exception:                                         # noqa: BLE001
            prior = pd.DataFrame()

    rows, errs = [], []
    for i, (theme, news_q) in enumerate(NEWS_THEMES.items()):
        if i:
            time.sleep(2)   # space requests out — Reddit throttles rapid bursts
        posts, err = fetch_reddit(_reddit_query(news_q), limit=40, sort="new")
        if posts:
            for p in posts:
                rows.append({**p, "theme": theme})
        else:
            errs.append(f"{theme}: {err or 'no results'}")
            # keep yesterday's rows for this theme rather than showing nothing
            if not prior.empty and "theme" in prior:
                rows.extend(prior[prior.theme == theme].to_dict("records"))

    if rows:
        df = (pd.DataFrame(rows).drop_duplicates("link").reset_index(drop=True))
        try:
            df.to_parquet(REDDIT_PARQUET, index=False)
        except Exception:                                         # noqa: BLE001
            pass   # read-only FS — cache in memory only, still usable this run
        note = None
        if errs:
            missed = ", ".join(e.split(":")[0] for e in errs)
            note = f"Couldn't refresh: {missed} (showing last good data)."
        return df, note
    if not prior.empty:
        return prior, "Live fetch unavailable — showing the last saved snapshot."
    return pd.DataFrame(), ("; ".join(errs) or "no data")
