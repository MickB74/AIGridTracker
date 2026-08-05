"""Shareable deep links for the Streamlit tools.

Organising is the whole premise of this app, and until now none of it could
be sent to anyone: Streamlit has no routing, so a resident who built an
estimate for their town could download a PDF but could not hand a neighbour a
link. This encodes a tab's inputs in the query string and restores them on
load, which is what makes the toolkit forwardable in a group chat.

Two Streamlit constraints drive the design:

1. **Restore before widgets.** Streamlit refuses to write `session_state` for
   a key whose widget already exists this run, so `restore()` must be called
   at the very top of a tab's render function, before any widget using those
   keys is created. Calling it late raises rather than silently no-oping,
   which is the better failure.

2. **Restore once.** Query params survive reruns. Re-applying them on every
   rerun would stamp the shared values back over whatever the user just
   changed, so the link would feel broken the moment anyone touched a
   control. A session-scoped sentinel makes it a one-time seed.
"""

import datetime as _dt
import urllib.parse

# Where the hosted app lives, for building absolute links. Overridable so a
# fork or a local run doesn't hand people links to somebody else's deploy.
import os

APP_PUBLIC_URL = os.environ.get("GRIDWATCH_APP_URL",
                                "https://aigridtracker.streamlit.app")

_SEEDED = "_share_seeded_{}"


def _coerce(raw, kind):
    """Query-string text → a value Streamlit will accept, or None.

    Anything unparseable returns None and the caller skips that key: a
    malformed link should drop one field, never crash the tab someone was
    sent to.
    """
    try:
        if kind == "int":
            return int(raw)
        if kind == "float":
            return float(raw)
        if kind == "date":
            return _dt.date.fromisoformat(raw)
        return str(raw)
    except (TypeError, ValueError):
        return None


def _validate(value, kind, guard):
    """Reject or clamp a restored value against the widget's real options.

    Without this, a link is a loaded gun pointed at the recipient: seeding
    `sh_state` with a string Streamlit's selectbox has never heard of makes
    the widget raise, and the whole tab dies for whoever opened the link.
    Links get mangled by chat clients, truncated by emails, and go stale when
    an option is renamed — so the untrusted case is the normal case.

    For str/date a guard is the collection of allowed values; for numbers it
    is a (lo, hi) range and out-of-bounds is clamped rather than dropped,
    because a slider's neighbouring value is a fine answer where a
    nonexistent state is not.
    """
    if guard is None:
        return value
    allowed = guard() if callable(guard) else guard
    if kind in ("int", "float"):
        lo, hi = allowed
        return min(max(value, lo), hi)
    return value if value in allowed else None


def restore(st, spec, name):
    """Seed session_state from the URL. Call before creating any widget.

    `spec` maps a short query-param name to (session_key, kind) or
    (session_key, kind, guard) — see `_validate`. `name` scopes the
    once-only sentinel to this tool.

    That scoping is load-bearing, not decoration. Every tab renders on every
    Streamlit run, so with a single session-wide sentinel the first tab to
    render consumes it and every later tab silently skips its own restore —
    which is exactly what happened here: a shared link seeded Start here and
    left the impact calculator on its defaults.

    Values are only applied when the key is not already in session_state, so
    a param can never overwrite something the user set this session. Two
    tools may map the same param (both read `state`), which is deliberate:
    one link seeds whichever tool the recipient opens.
    """
    sentinel = _SEEDED.format(name)
    if st.session_state.get(sentinel):
        return
    st.session_state[sentinel] = True
    params = st.query_params
    for param, entry in spec.items():
        key, kind = entry[0], entry[1]
        guard = entry[2] if len(entry) > 2 else None
        if param not in params or key in st.session_state:
            continue
        value = _coerce(params.get(param), kind)
        if value is None:
            continue
        value = _validate(value, kind, guard)
        if value is not None:
            st.session_state[key] = value


def link(st, spec, base=None):
    """Absolute URL encoding the current values of `spec`'s session keys.

    Empty and unset values are dropped rather than serialised as blanks — a
    link full of `&who=` teaches the reader nothing and is harder to paste.
    """
    query = {}
    for param, entry in spec.items():
        key, kind = entry[0], entry[1]
        value = st.session_state.get(key)
        if value is None or value == "":
            continue
        if kind == "date" and isinstance(value, _dt.date):
            value = value.isoformat()
        query[param] = str(value)
    root = (base or APP_PUBLIC_URL).rstrip("/")
    if not query:
        return root
    return f"{root}/?{urllib.parse.urlencode(query)}"


def render(st, spec, caption=None, base=None):
    """Show the shareable link with a one-line explanation.

    st.code gives a copy button for free, and renders the URL as text rather
    than a live link — which is what you want, since clicking your own share
    link inside the app is not the point.
    """
    url = link(st, spec, base=base)
    with st.expander("🔗 Share this — send it to a neighbour"):
        st.caption(caption or
                   "This link reopens the tool with everything below already "
                   "filled in. Paste it into a group chat, a Nextdoor post, "
                   "or an email to your council member.")
        st.code(url, language=None)
