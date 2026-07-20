import urllib.parse
import xml.etree.ElementTree as ET
import requests
import streamlit as st
import datetime as _dt
from email.utils import parsedate_to_datetime
from src.constants import (
    GOOGLE_NEWS_RSS, STORY_QUERY, STORY_ANGLES, STORY_IMPACT_WEIGHTS,
)

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_news(query: str, limit: int = 15):
    """Live headlines from Google News RSS (no API key). Returns
    (list_of_dicts, error_or_None); each dict has title/source/link/published."""
    try:
        url = GOOGLE_NEWS_RSS.format(q=urllib.parse.quote(query))
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        root = ET.fromstring(r.content)
        out = []
        for it in root.iter("item"):
            title = (it.findtext("title") or "").strip()
            src_el = it.find("source")
            source = src_el.text.strip() if src_el is not None and src_el.text else ""
            # Google News formats titles as "Headline - Source"; drop the suffix.
            if source and title.endswith(f" - {source}"):
                title = title[: -(len(source) + 3)]
            out.append({
                "title": title,
                "source": source,
                "link": (it.findtext("link") or "").strip(),
                "published": (it.findtext("pubDate") or "").strip()[:16],
            })
            if len(out) >= limit:
                break
        return out, None
    except Exception as e:                                        # noqa: BLE001
        return None, str(e)


def _story_angle(title: str):
    """Classifies a news story title into community spotlight themes."""
    t = title.lower()
    for keys, emoji, blurb in STORY_ANGLES:
        if any(k in t for k in keys):
            return emoji, blurb
    return "⚠️", "A community is pushing back on a nearby data center."


def rank_stories(items, top_n: int = 5):
    """Heuristic 'most important' ranking for community-impact headlines.
    Score = recency (fresher = higher) + summed weights of high-stakes keywords
    (lawsuit, moratorium, rate hike, …). No LLM, no API key. Returns a new list
    of the top `top_n` items, each annotated with score/angle_emoji/angle_blurb,
    sorted most-important first."""
    scored = []
    for it in items or []:
        title = it.get("title") or ""
        t = title.lower()
        weight = sum(w for kw, w in STORY_IMPACT_WEIGHTS.items() if kw in t)
        age = it.get("age_days")
        # unknown age is treated as fresh (server-side when:7d already gated it)
        recency = 3.0 if age is None else max(0.0, 3.0 - 0.4 * age)
        emoji, blurb = _story_angle(title)
        scored.append({**it, "score": round(weight + recency, 2),
                       "angle_emoji": emoji, "angle_blurb": blurb})
    scored.sort(key=lambda s: s["score"], reverse=True)
    return scored[:top_n]


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_community_stories(limit: int = 12, max_age_days: int = 7):
    """Recent headlines about communities negatively affected by a built or
    under-construction data center. Filters to the last `max_age_days` by
    pubDate. Returns (list_of_dicts, error_or_None); each dict has
    title/source/link/published/age_days."""
    try:
        url = GOOGLE_NEWS_RSS.format(q=urllib.parse.quote(STORY_QUERY))
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        root = ET.fromstring(r.content)
        now = _dt.datetime.now(_dt.timezone.utc)
        out = []
        for it in root.iter("item"):
            title = (it.findtext("title") or "").strip()
            src_el = it.find("source")
            source = src_el.text.strip() if src_el is not None and src_el.text else ""
            if source and title.endswith(f" - {source}"):
                title = title[: -(len(source) + 3)]
            pub_raw = (it.findtext("pubDate") or "").strip()
            age_days = None
            if pub_raw:
                try:
                    age_days = (now - parsedate_to_datetime(pub_raw)).days
                except Exception:                                 # noqa: BLE001
                    age_days = None
            # gate to the recency window; keep unparseable dates (when:7d already
            # constrained them server-side).
            if age_days is not None and age_days > max_age_days:
                continue
            out.append({
                "title": title, "source": source,
                "link": (it.findtext("link") or "").strip(),
                "published": pub_raw, "age_days": age_days,
            })
            if len(out) >= limit:
                break
        return out, None
    except Exception as e:                                        # noqa: BLE001
        return None, str(e)
