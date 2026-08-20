"""Groups tracked data-center news headlines by locality so a pattern spread
across many separate stories — six headlines about the same fight over two
months — is visible as one thread instead of scrolling out of a 7-day feed.
Also produces a lightweight extractive summary once a locality has enough
coverage to be a pattern rather than a one-off.

Pure functions, no Streamlit and no network I/O — importable by build_site.py
(which must stay stdlib-only beyond pandas) and by the app.
"""
import json
import re
from pathlib import Path

from src.constants import (
    DC_SITES_DF, LOCAL_BODIES_DF, MORATORIUMS_DF, STATE_PUCS_DF, STORY_ANGLES,
)

_PAREN_RE = re.compile(r"\s*\(.*?\)\s*")

# Locality names imported from Moratorium Nation (CC-BY-4.0) by
# scripts/import_moratorium_nation.py. Names only — this file records that a
# place exists and is in scope, never what it did, so it carries none of the
# source/as_of burden a registry row does and can feed the matcher directly.
# Without it ~70% of the story archive stays "not yet localized" for want of a
# town name we simply never had.
_EXTERNAL_GAZETTEER = Path(__file__).resolve().parent.parent / "data" / "external_gazetteer.json"


def _external_entries():
    """[(name, state_abbrev), ...] from the imported gazetteer; empty when the
    file is absent or unreadable. Never fatal — a missing import degrades
    matching, it doesn't break the build."""
    try:
        payload = json.loads(_EXTERNAL_GAZETTEER.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    out = []
    for entry in payload.get("entries", []):
        name = str(entry.get("name") or "").strip()
        state = str(entry.get("state") or "").strip()
        if name and state:
            out.append((name, state))
    return out

# Full state names, lowercased. A registry row like "Ohio (ballot measure)"
# strips down to bare "Ohio" once the parenthetical is dropped — without this
# guard that reads as a specific locality and matches any headline that
# merely mentions the state, mislabeling a statewide story as a town-level one.
_STATE_NAMES_LOWER = {str(n).strip().lower() for n in STATE_PUCS_DF["state"]}


def clean_locality(name):
    return _PAREN_RE.sub(" ", str(name)).strip()


def build_gazetteer():
    """[(display_name, state_abbrev, compiled_word_boundary_regex), ...],
    longest name first so "Council Bluffs" is matched before a shorter,
    coincidentally-overlapping name would be.
    """
    seen = {}
    pairs = []
    for df, col in ((DC_SITES_DF, "location"), (LOCAL_BODIES_DF, "locality"),
                    (MORATORIUMS_DF, "locality")):
        for _, row in df.iterrows():
            pairs.append((clean_locality(row[col]), str(row["state"]).strip()))
    # Curated rows first so their display spelling wins the setdefault over an
    # imported variant of the same place.
    pairs.extend(_external_entries())
    for name, state in pairs:
        if not name or not state or state == "nan":
            continue
        if name.lower() in _STATE_NAMES_LOWER:
            continue
        seen.setdefault((name.lower(), state), (name, state))
    entries = sorted(seen.values(), key=lambda e: len(e[0]), reverse=True)
    return [(name, state, re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE))
            for name, state in entries]


def guess_locality(title, gazetteer):
    """Best-effort (locality, state_abbrev) match against the gazetteer, or
    (None, None). A headline naming no locality we track still gets archived
    — it just groups by state (or "not yet localized") instead."""
    for name, state, pattern in gazetteer:
        if pattern.search(title or ""):
            return name, state
    return None, None


_NON_STATE_PHRASES = ("Washington Post", "Washington, D.C.", "Washington DC",
                     "Washington, DC", "New Yorker", "New York Times",
                     "Georgia Tech")
# Two-letter abbrevs only match in tight postal-style contexts (a comma
# before them, "state of X", or right before a bill/regulator token) — same
# guard build_site.py's _post_states/_news_states_for use, to avoid the
# classic "OR/IN/OK" false positives inside ordinary prose.
_ABBREV_TOKEN = {
    abbrev: re.compile(rf"(?:,\s*|\bstate\s+of\s+){re.escape(abbrev)}\b"
                       rf"|\b{re.escape(abbrev)}(?=\s+(?:H\.?B\.?|S\.?B\.?|PUC|PSC))")
    for _, abbrev in zip(STATE_PUCS_DF["state"], STATE_PUCS_DF["abbrev"])
}
_STATE_NAME_TO_ABBREV = dict(zip(STATE_PUCS_DF["state"], STATE_PUCS_DF["abbrev"]))


def guess_state(text):
    """Best-effort state abbrev mentioned in `text` (a headline, typically),
    or None. Used as the fallback when guess_locality finds no known town —
    "Ohio residents sue..." still archives as OH instead of unclassified."""
    haystack = text or ""
    cleaned = haystack
    for bad in _NON_STATE_PHRASES:
        cleaned = cleaned.replace(bad, " ")
    for name, abbrev in _STATE_NAME_TO_ABBREV.items():
        if re.search(rf"\b{re.escape(name)}\b", cleaned, re.IGNORECASE):
            return abbrev
        if _ABBREV_TOKEN[abbrev].search(haystack):
            return abbrev
    return None


def date_from_iso(iso, default=None):
    """YYYY-MM-DD from an ISO datetime string, or `default` if blank/unparseable."""
    if iso and len(iso) >= 10:
        return iso[:10]
    return default


def merge_stories(existing, fresh_records, today):
    """Fold `fresh_records` into `existing` (mutated in place), deduped by
    link. A record already present only gets `last_seen` bumped and, if the
    fresh copy's own published date is earlier than what's on file,
    `first_seen` is pulled back to it — first_seen means the earliest known
    date this coverage existed, not "the day a crawler happened to see it",
    so a later backfill can correct an entry the live feed recorded late.
    Returns the number of genuinely new records added."""
    by_link = {s["link"]: s for s in existing if s.get("link")}
    added = 0
    for record in fresh_records:
        link = record.get("link")
        if not link:
            continue
        prior = by_link.get(link)
        if prior:
            prior["last_seen"] = today
            if record.get("first_seen") and record["first_seen"] < prior.get("first_seen", today):
                prior["first_seen"] = record["first_seen"]
            continue
        existing.append(record)
        by_link[link] = record
        added += 1
    return added


def classify_angle(title):
    """(emoji, one-line blurb) for the headline's dominant concern, same
    taxonomy the live app feed uses (STORY_ANGLES)."""
    t = (title or "").lower()
    for keys, emoji, blurb in STORY_ANGLES:
        if any(k in t for k in keys):
            return emoji, blurb
    return "⚠️", "A community is pushing back on a nearby data center."


# A state-only story (no town matched) is usually one of two very different
# things: a genuine statewide policy/politics story (a governor, a legislature,
# a statewide bill or tax program, statewide polling) or a specific local story
# whose town simply isn't in the gazetteer yet. Labeling both "(locality not
# identified)" reads as a detection failure and buries the statewide ones.
# These signals pull the statewide ones into their own bucket; anything without
# a signal (e.g. "a plant in her neighborhood") stays as an unidentified town.
STATEWIDE_SIGNALS = (
    "governor", "gov.", " gov ", "legislat", "lawmaker", "senate",
    "assembly", "statehouse", "state house", " bill ", " bills",
    "bill to", "tariff", "statewide",
    "first state", "ratepayer", "tax break", "tax credit", "tax incentive",
    "rein in", "regulators", "public utilit", "utility board", " puc",
    " psc", " bpu", "moratorium bill", "communities are moving",
    "residents support", "residents oppose", "half of", "state law",
    "state to ", "state moves", "state would", "attorney general",
)


def is_statewide(title):
    """True when a state-only story reads as state-level policy or politics
    rather than a specific-but-undetected town."""
    t = (title or "").lower()
    return any(sig in t for sig in STATEWIDE_SIGNALS)


# Topic taxonomy for organizing stories that share a group — and for giving
# the no-place-at-all stories (national policy, industry, finance) real
# groups instead of one undifferentiated "Not yet localized" blob. Checked in
# order, first match wins; keywords are \b-prefixed regexes so "ban" matches
# "ban/bans/banning" but not "urban".
STORY_TOPICS = [
    ("bans", "Bans & moratoriums",
     ("moratorium", "ban", "ordinance", "rezon", "zoning", "pause")),
    ("legal", "Lawsuits & legal fights",
     ("lawsuit", "sue", "sued", "court", "litigation", "legal", "settlement",
      "judge", "appeal")),
    ("policy", "Policy & legislation",
     ("legislat", "bill", "governor", "gov.", "regulat", "tax credit",
      "tax break", "tax incentive", "lawmaker", "senate", "congress",
      "guardrail", "oversight", "statehouse", "moratorium bill")),
    ("grid", "Electric bills & the grid",
     ("electric bill", "power bill", "utility bill", "ratepayer", "rate hike",
      "rates", "grid", "transmission", "pjm", "ercot", "electricity",
      "power demand", "energy cost")),
    ("water", "Water & environment",
     ("water", "drought", "aquifer", "pollution", "emission", "air quality",
      "environment", "diesel", "climate")),
    ("noise", "Noise & health",
     ("noise", "hum", "decibel", "health")),
    ("pushback", "Community pushback",
     ("protest", "oppos", "backlash", "outcry", "resident", "hearing",
      "packed", "rally", "fight", "revolt", "pushback")),
    ("build", "Projects & construction",
     ("construction", "build", "approv", "propos", "campus", "megawatt",
      "gigawatt", "expansion", "breaks ground", "invest")),
]
_TOPIC_PATTERNS = [
    (key, label, re.compile("|".join(rf"\b{re.escape(k)}" for k in kws),
                            re.IGNORECASE))
    for key, label, kws in STORY_TOPICS
]


def classify_topic(title):
    """(key, label) for the headline's dominant topic; ("other",
    "Other coverage") when nothing matches."""
    for key, label, pattern in _TOPIC_PATTERNS:
        if pattern.search(title or ""):
            return key, label
    return "other", "Other coverage"


def group_key_for(locality, state, statewide=False):
    if locality and state:
        return f"{locality}|{state}"
    if state and statewide:
        return f"statewide|{state}"
    if state:
        return f"|{state}"
    return "unclassified"


def group_label_for(locality, state, statewide=False):
    if locality and state:
        return f"{locality}, {state}"
    if state and statewide:
        return f"{state} (statewide)"
    if state:
        return f"{state} (town not identified)"
    return "Not yet localized"


def summarize_group(stories):
    """Heuristic extractive summary — no LLM call, no API key. Counts how
    often each STORY_ANGLES theme recurs across the group's headlines and
    surfaces the most common ones plus the freshest story, so a resident
    scanning the tracker sees the shape of the pattern without reading every
    headline in the group."""
    outlets = sorted({s.get("outlet") for s in stories if s.get("outlet")})
    seen_dates = sorted(s.get("first_seen") for s in stories if s.get("first_seen"))
    since = seen_dates[0] if seen_dates else None

    theme_counts = {}
    for s in stories:
        _, blurb = classify_angle(s.get("title", ""))
        theme_counts[blurb] = theme_counts.get(blurb, 0) + 1
    top_themes = sorted(theme_counts.items(), key=lambda kv: kv[1], reverse=True)[:2]

    bits = [f"{len(stories)} stories"]
    if since:
        bits.append(f"tracked since {since}")
    if outlets:
        bits.append(f"across {len(outlets)} outlet{'s' if len(outlets) != 1 else ''}")
    lead = " ".join(bits) + "."
    theme_line = " ".join(f"{n}× {blurb}" for blurb, n in top_themes)
    latest = stories[0]
    latest_line = (f'Most recent: “{latest.get("title", "")}” '
                   f'({latest.get("outlet", "")}, {latest.get("first_seen", "")}).')
    return " ".join(x for x in (lead, theme_line, latest_line) if x)


def group_stories(stories, min_for_summary=4):
    """Groups persisted story dicts (each with title/outlet/link/published/
    published_iso/first_seen/locality/state) by locality. Returns a list
    sorted by story count (most-covered first), then most-recent. Each group
    carries `summary` (str) once it has `min_for_summary`+ stories, else
    None — that's the "AI summary when more than 3" trigger."""
    groups = {}
    for s in stories:
        loc, st = s.get("locality"), s.get("state")
        # Statewide classification only applies to state-only stories (a town
        # match always wins — a story about a specific town is not statewide).
        sw = bool(st and not loc and is_statewide(s.get("title", "")))
        if not loc and not st:
            # No place at all — national policy, industry, finance. One
            # "Not yet localized" blob is unreadable at scale, so these
            # group by topic instead.
            tkey, tlabel = classify_topic(s.get("title", ""))
            key = f"topic:{tkey}"
            label = f"National & industry — {tlabel}"
        else:
            key = group_key_for(loc, st, sw)
            label = group_label_for(loc, st, sw)
        g = groups.setdefault(key, {
            "key": key,
            "locality": loc,
            "state": st,
            "statewide": sw,
            "label": label,
            "stories": [],
        })
        g["stories"].append(s)

    out = []
    for g in groups.values():
        g["stories"].sort(
            key=lambda s: s.get("published_iso") or s.get("published") or "",
            reverse=True)
        g["count"] = len(g["stories"])
        firsts = [s.get("first_seen") for s in g["stories"] if s.get("first_seen")]
        g["first_seen"] = min(firsts) if firsts else None
        g["summary"] = (summarize_group(g["stories"])
                        if g["count"] >= min_for_summary else None)
        out.append(g)

    out.sort(key=lambda g: (g["count"],
                            g["stories"][0].get("published_iso", "") if g["stories"] else ""),
             reverse=True)
    return out
