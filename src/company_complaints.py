"""Groups the archived story headlines by the company they name, and by the
complaint the headline is about — the "who is being complained about, and for
what" cut of the same archive `story_tracker` cuts by locality.

Attribution is deliberately narrow: a story counts against a company only when
the headline *names* it. We do not infer a company from the town (a fight in a
town where Google has a campus is not necessarily a fight about Google), so the
counts under-report rather than over-report. Everything here is a headline
keyword match, not a verified claim — the page says so, loudly.

Pure functions, no Streamlit and no network I/O.
"""
import re

from src.constants import OPERATORS

# (display name, [alias patterns], context-required?) — order is irrelevant,
# a headline can name several companies and counts once under each.
#
# `strict=True` means the alias is an ordinary English word ("Switch",
# "Aligned", "Prime", "Oracle" in prose) and only counts when the headline
# also carries a data-center context word. Without that guard "Switch" alone
# tagged unrelated headlines.
COMPANY_ALIASES = [
    ("Amazon (AWS)",  [r"amazon", r"aws"],                            False),
    ("Meta",          [r"meta", r"facebook"],                         False),
    ("Google",        [r"google", r"alphabet"],                       False),
    ("Microsoft",     [r"microsoft"],                                 False),
    ("OpenAI",        [r"open\s?ai", r"stargate", r"altman"],          False),
    ("xAI (Colossus)", [r"xai", r"colossus", r"musk"],                False),
    ("Oracle",        [r"oracle"],                                    False),
    ("Anthropic",     [r"anthropic"],                                 False),
    ("Nvidia",        [r"nvidia"],                                    False),
    ("Apple",         [r"apple"],                                     True),
    ("CoreWeave",     [r"coreweave"],                                 False),
    ("QTS",           [r"qts"],                                       False),
    ("Blackstone",    [r"blackstone"],                                False),
    ("Equinix",       [r"equinix"],                                   False),
    ("Digital Realty", [r"digital realty"],                           False),
    ("CyrusOne",      [r"cyrusone"],                                  False),
    ("Vantage",       [r"vantage"],                                   True),
    ("Switch",        [r"switch"],                                    True),
    ("Aligned",       [r"aligned"],                                   True),
    ("Stack Infrastructure", [r"stack infrastructure"],               False),
    ("EdgeConneX",    [r"edgeconnex"],                                False),
    ("Core Scientific", [r"core scientific"],                         False),
    ("Crusoe",        [r"crusoe"],                                    False),
    ("Prime Data Centers", [r"prime data cent\w*"],                   False),
    ("Tract",         [r"tract"],                                     True),
    ("Fermi",         [r"fermi"],                                     False),
    ("TikTok",        [r"tiktok", r"bytedance"],                      False),
    ("Related Digital", [r"related digital"],                         False),
    ("PowerHouse",    [r"powerhouse"],                                True),
]

_CONTEXT_RE = re.compile(r"data\s?cent|datacenter|campus|server farm|hyperscal",
                         re.IGNORECASE)

# How far from an ambiguous alias a data-center context word has to sit for the
# mention to count as the company. Generous enough for "Switch's Reno campus",
# tight enough to reject "Nebius Says Switch To Bloom ... New Jersey AI Data
# Center", which is the verb.
_CONTEXT_WINDOW = 30

_COMPANY_PATTERNS = [
    (name, re.compile("|".join(rf"\b{a}\b" for a in aliases), re.IGNORECASE), strict)
    for name, aliases, strict in COMPANY_ALIASES
]

# Brand colours come from the operator registry where the company is one of
# ours; the rest fall back to a neutral slate so a card never depends on a
# colour we invented for a company we don't otherwise track.
_REGISTRY_COLOR = {name: meta[6] for name, meta in OPERATORS.items()}
_EXTRA_COLOR = {
    "OpenAI": "#14b8a6", "xAI (Colossus)": "#a855f7", "Oracle": "#c74634",
    "Anthropic": "#d97757", "Nvidia": "#76b900", "Apple": "#a3a3a3",
    "Blackstone": "#1f4e79", "Crusoe": "#f97316", "Fermi": "#eab308",
    "TikTok": "#ff0050", "Tract": "#0d9488", "Related Digital": "#7c3aed",
    "PowerHouse": "#f43f5e", "Prime Data Centers": "#3b82f6",
    "Amazon (AWS)": "#ff9900",
}


def company_color(name):
    return _REGISTRY_COLOR.get(name) or _EXTRA_COLOR.get(name) or "#94a3b8"


def _near_context(text, match):
    """True when a data-center context word sits within _CONTEXT_WINDOW
    characters of the matched alias."""
    lo = max(0, match.start() - _CONTEXT_WINDOW)
    hi = min(len(text), match.end() + _CONTEXT_WINDOW)
    return bool(_CONTEXT_RE.search(text[lo:hi]))


def companies_in(title):
    """Every tracked company the headline names. Empty when it names none —
    most of the archive, since local coverage usually says "the data center"
    rather than who owns it."""
    text = title or ""
    out = []
    for name, pattern, strict in _COMPANY_PATTERNS:
        for m in pattern.finditer(text):
            if not strict or _near_context(text, m):
                out.append(name)
                break
    return out


# What the headline is complaining about. Multi-label on purpose: "water and
# power bills" is one headline about two grievances, and forcing it into one
# bucket is what makes a single-label taxonomy read as noise.
COMPLAINT_THEMES = [
    ("bills", "\U0001F4B8", "Electric bills & rates",
     (r"electric bill", r"power bill", r"utility bill", r"ratepayer",
      r"rate hike", r"rate increase", r"\brates\b", r"energy cost",
      r"cost shift", r"bills? (?:are |will )?(?:go|going|rise|rising|up)")),
    ("water", "\U0001F4A7", "Water use",
     (r"water", r"drought", r"aquifer", r"\bwell\b", r"wells\b", r"cooling",
      r"groundwater", r"river")),
    ("noise", "\U0001F50A", "Noise",
     (r"noise", r"\bhum\b", r"humming", r"decibel", r"\bsound\b", r"loud")),
    ("air", "\U0001F3ED", "Air quality & health",
     (r"pollut", r"air quality", r"diesel", r"emission", r"turbine", r"smog",
      r"asthma", r"health", r"toxic")),
    ("power", "⚡", "Grid strain & new generation",
     (r"\bgrid\b", r"transmission", r"power line", r"blackout", r"outage",
      r"gas plant", r"nuclear", r"reactor", r"substation", r"\bpjm\b",
      r"ercot", r"power demand", r"electricity demand")),
    ("land", "\U0001F6D1", "Zoning, bans & moratoriums",
     (r"moratorium", r"\bbans?\b", r"banning", r"zoning", r"rezon",
      r"ordinance", r"\bpause\b", r"planning (?:board|commission)",
      r"land use", r"setback")),
    ("legal", "⚖️", "Lawsuits & legal fights",
     (r"lawsuit", r"\bsues?\b", r"\bsued\b", r"litigation", r"court",
      r"\bjudge\b", r"appeal", r"settlement", r"injunction",
      r"attorney general")),
    ("money", "\U0001F3E0", "Tax breaks, land value & local benefit",
     (r"tax break", r"tax credit", r"tax incentive", r"subsid", r"abatement",
      r"property value", r"home value", r"\bjobs\b", r"giveaway")),
    ("secrecy", "\U0001F575️", "Secrecy & shell companies",
     (r"secret", r"shell (?:compan|llc)", r"\bllc\b", r"nondisclosure",
      r"\bnda\b", r"code ?name", r"undisclosed", r"public records",
      r"transparen")),
    ("pushback", "\U0001F4E3", "Organized opposition",
     (r"protest", r"rally", r"packed", r"oppos", r"backlash", r"outcry",
      r"petition", r"revolt", r"pushback", r"angry", r"\bfight")),
]
_THEME_PATTERNS = [
    (key, emoji, label, re.compile("|".join(kws), re.IGNORECASE))
    for key, emoji, label, kws in COMPLAINT_THEMES
]
THEME_LABELS = {key: (emoji, label) for key, emoji, label, _ in _THEME_PATTERNS}


def themes_in(title):
    """[(key, emoji, label), ...] for every complaint the headline touches;
    empty when it reads as coverage rather than a grievance."""
    text = title or ""
    return [(key, emoji, label) for key, emoji, label, pattern in _THEME_PATTERNS
            if pattern.search(text)]


def group_by_company(stories, min_stories=2):
    """One entry per company named in `min_stories`+ archived headlines,
    most-covered first. Each carries its complaint-theme tallies (a headline
    counts under every theme it raises, so theme counts sum to more than the
    story count) and its stories, newest first."""
    groups = {}
    for s in stories:
        title = s.get("title", "")
        names = companies_in(title)
        if not names:
            continue
        themes = themes_in(title)
        for name in names:
            g = groups.setdefault(name, {
                "company": name,
                "color": company_color(name),
                "stories": [],
                "themes": {},
                "states": set(),
            })
            g["stories"].append(s)
            for key, _, _ in themes:
                g["themes"][key] = g["themes"].get(key, 0) + 1
            if s.get("state"):
                g["states"].add(s["state"])

    out = []
    for g in groups.values():
        if len(g["stories"]) < min_stories:
            continue
        g["stories"].sort(
            key=lambda s: s.get("published_iso") or s.get("published") or "",
            reverse=True)
        g["count"] = len(g["stories"])
        firsts = [s.get("first_seen") for s in g["stories"] if s.get("first_seen")]
        g["first_seen"] = min(firsts) if firsts else None
        g["states"] = sorted(g["states"])
        g["top_themes"] = sorted(g["themes"].items(), key=lambda kv: kv[1],
                                 reverse=True)
        g["untagged"] = sum(1 for s in g["stories"] if not themes_in(s.get("title", "")))
        out.append(g)
    out.sort(key=lambda g: (g["count"], g["company"]), reverse=True)
    return out


def theme_totals(groups):
    """[(key, emoji, label, total), ...] across every company group, ordered
    by the taxonomy above so the matrix columns are stable."""
    totals = {}
    for g in groups:
        for key, n in g["themes"].items():
            totals[key] = totals.get(key, 0) + n
    return [(key, emoji, label, totals.get(key, 0))
            for key, emoji, label, _ in _THEME_PATTERNS if totals.get(key)]
