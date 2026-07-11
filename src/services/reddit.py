import xml.etree.ElementTree as ET
import requests
import time
import pandas as pd
import streamlit as st
from src.constants import (REDDIT_HOSTS, _ATOM, REDDIT_UA, REDDIT_PARQUET,
                           NEWS_THEMES, CURATED_SUBS, DENY_SUBS)

# base hosts (REDDIT_HOSTS are full .../search.rss URLs) for subreddit endpoints
_REDDIT_BASES = tuple(h.rsplit("/search.rss", 1)[0] for h in REDDIT_HOSTS)

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


def _reddit_rss(path: str, params: dict, limit: int):
    """GET a Reddit .rss endpoint across mirror hosts with 429 backoff.
    `path` is appended to each base host (e.g. "/search.rss", "/r/energy/new.rss").
    Returns (list_of_dicts, error_or_None). Tries old.reddit.com (rarely
    throttled) first, then www, each with a short backoff retry on 429."""
    last = "Reddit unreachable"
    for base in _REDDIT_BASES:
        for attempt in range(3):
            try:
                r = requests.get(base + path, params=params,
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


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_reddit(query: str, limit: int = 15, sort: str = "relevance",
                 period: str = "year"):
    """Site-wide Reddit search via the public Atom RSS (keyless). Returns
    (list_of_dicts, error_or_None); each dict has title/subreddit/link/created."""
    return _reddit_rss("/search.rss",
                       {"q": query, "sort": sort, "t": period}, limit)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_subreddit(sub: str, query: str = None, limit: int = 25):
    """Posts from r/<sub>: newest, or a subreddit-restricted search if `query`
    is given. Lets us pull the data-center communities directly instead of
    hoping site-wide search happens to surface them."""
    if query:
        return _reddit_rss(f"/r/{sub}/search.rss",
                           {"q": query, "restrict_sr": 1, "sort": "new",
                            "t": "year"}, limit)
    return _reddit_rss(f"/r/{sub}/new.rss", {}, limit)


def _is_junk_sub(sub: str) -> bool:
    """Drop obvious noise (spam/content-farm subs, u/ user pages) that site-wide
    keyword search drags in — see DENY_SUBS."""
    s = (sub or "").replace("r/", "").strip().lower()
    return s.startswith("u/") or s.endswith("content") or s in DENY_SUBS


def _theme_of(title: str) -> list:
    """Which NEWS_THEMES a Reddit title plausibly belongs to, by descriptor
    keyword. Used to file curated-subreddit posts under the right theme filter;
    a post matching none is dropped (keeps the theme-organized feed on-topic)."""
    t = (title or "").lower()
    hits = []
    for theme, q in NEWS_THEMES.items():
        words = q.split()
        terms = (words[2:] if [w.lower() for w in words[:2]] == ["data", "center"]
                 else words)
        if any(w.lower() in t for w in terms):
            hits.append(theme)
    return hits


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

    # pull the data-center communities directly, then file each post under the
    # theme(s) it matches (datacenter subs wholesale; adjacent subs on-topic only)
    for sub in CURATED_SUBS:
        time.sleep(2)
        q = None if sub.lower() in ("datacenter", "datacenters") else '"data center"'
        posts, err = fetch_subreddit(sub, query=q)
        if posts:
            for p in posts:
                for theme in _theme_of(p["title"]):
                    rows.append({**p, "theme": theme})
        else:
            errs.append(f"r/{sub}: {err or 'no results'}")

    # drop obvious junk subreddits from every source
    rows = [r for r in rows if not _is_junk_sub(r.get("subreddit"))]

    if rows:
        df = (pd.DataFrame(rows)
              .drop_duplicates(["link", "theme"]).reset_index(drop=True))
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
