"""Time-sensitive alerts derived from dates the registries already hold.

The tracker knows when every documented moratorium lapses, and until now
nothing acted on it. A moratorium expiring is the single most actionable
event in this domain: it is a hard deadline, it is knowable weeks ahead, and
the community that pressed pause is usually the last to hear that the pause
is ending.

Deliberately built on public data only. Subscriber emails are PII and live
outside git, so anything keyed to a person needs infrastructure this repo
does not have. An expiry feed needs none: it publishes as JSON and RSS, and a
resident, a reporter or a council clerk can subscribe today. That is the
version that ships rather than the version that waits.

Pure functions, no Streamlit and no I/O — `build_site.py` publishes the
output and the app renders it.
"""

import datetime as _dt

from src.constants import MORATORIUMS_DF, has_value

# How far ahead to warn. Long enough that a town board can get an extension
# onto an agenda — most meet monthly, so a fortnight's notice is not notice.
LOOKAHEAD_DAYS = 90

# How long a lapse stays newsworthy after the fact.
LOOKBACK_DAYS = 60


def _severity(days_left):
    """Urgency band for a countdown, used for ordering and wording."""
    if days_left < 0:
        return "expired"
    if days_left <= 30:
        return "urgent"
    return "upcoming"


def build_alerts(today=None, lookahead=LOOKAHEAD_DAYS, lookback=LOOKBACK_DAYS):
    """Alerts for moratoriums lapsing soon or recently lapsed, worst first.

    Only rows with a documented `expires` can produce an alert — an undated
    term is a gap in the data, not a deadline, and inventing one here would
    put a fictional date in a feed people plan around. Those rows are the
    validator's problem, not this function's.
    """
    today = today or _dt.date.today()
    out = []
    for m in MORATORIUMS_DF.itertuples():
        if not has_value(m.expires) or m.status in ("Proposed", "Rejected",
                                                    "Vetoed", "Rescinded"):
            continue
        try:
            end = _dt.date.fromisoformat(str(m.expires))
        except ValueError:
            continue
        days = (end - today).days
        if days > lookahead or days < -lookback:
            continue
        sev = _severity(days)
        where = f"{m.locality}, {m.state}"
        if sev == "expired":
            title = f"{where}: data center moratorium has lapsed"
            body = (f"The moratorium's documented term ran to {m.expires} "
                    f"({abs(days)} days ago). Unless it was extended, new "
                    f"applications can be filed again. Confirm the current "
                    f"status with the clerk before relying on either reading.")
        else:
            title = (f"{where}: data center moratorium expires in "
                     f"{days} day{'s' if days != 1 else ''}")
            body = (f"The documented term ends {m.expires}. If your community "
                    f"wants it extended, that decision usually has to reach a "
                    f"meeting agenda weeks beforehand — check when the board "
                    f"next meets.")
        out.append({
            "id": f"mora-{m.state}-{str(m.locality).lower().replace(' ', '-')}-{m.expires}",
            "kind": "moratorium-expiry",
            "severity": sev,
            "locality": str(m.locality),
            "state": str(m.state),
            "expires": str(m.expires),
            "days_left": days,
            "title": title,
            "body": body,
            "source": str(m.source) if has_value(m.source) else None,
            "verified": bool(m.verified),
        })
    # Expired first, then soonest deadline.
    out.sort(key=lambda a: (a["severity"] != "expired", a["days_left"]))
    return out


def alerts_for_state(abbrev, today=None):
    """Alerts scoped to one state, for the app's state-aware surfaces."""
    return [a for a in build_alerts(today=today) if a["state"] == abbrev]
