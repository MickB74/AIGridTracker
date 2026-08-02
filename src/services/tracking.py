"""
Local, file-based usage analytics + newsletter signups.

Events (action-pack downloads, brief generations, signups) append to
data/analytics/events.jsonl; subscribers append to data/analytics/subscribers.csv.
Both live outside git (see .gitignore) because subscriber emails are PII.

Best-effort by design: every write/read is wrapped so a full disk or read-only
deploy can never crash a tab.

Durability: on ephemeral hosts (Streamlit Community Cloud) local files reset on
every redeploy, so the CSV alone silently loses subscribers. Set
SUBSCRIBE_WEBHOOK_URL (env var, .env line, or Streamlit secret) to any endpoint
that accepts a JSON POST — Formspree, a Google Apps Script web app, Zapier —
and each signup is delivered there first; the CSV remains as a local log.
"""

import csv
import json
import os
import pathlib
import re
from datetime import datetime, timezone

import pandas as pd
import requests

ANALYTICS_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent / "data" / "analytics"
)
EVENTS_PATH = ANALYTICS_DIR / "events.jsonl"
SUBSCRIBERS_PATH = ANALYTICS_DIR / "subscribers.csv"

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]{2,}$")


def _webhook_url() -> str:
    """Resolve the subscriber webhook. Order: env var -> .env -> st.secrets.
    Returns '' when unconfigured (CSV-only mode). Never raises."""
    url = os.environ.get("SUBSCRIBE_WEBHOOK_URL", "").strip()
    if url:
        return url
    env_path = ANALYTICS_DIR.parent.parent / ".env"
    try:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("SUBSCRIBE_WEBHOOK_URL") and "=" in line:
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:                                              # noqa: BLE001
        pass
    try:  # Streamlit Community Cloud exposes secrets only via st.secrets
        import streamlit as st
        return str(st.secrets.get("SUBSCRIBE_WEBHOOK_URL", "")).strip()
    except Exception:                                              # noqa: BLE001
        return ""


def _post_subscriber(email: str, state: str, source: str) -> bool:
    """Deliver one signup to the configured webhook. True only on a 2xx.
    False when unconfigured or on any failure — caller falls back to CSV."""
    url = _webhook_url()
    if not url:
        return False
    try:
        r = requests.post(
            url,
            json={"ts": _utc_now(), "email": email,
                  "state": state, "source": source},
            headers={"Accept": "application/json"},
            timeout=6,
        )
        return 200 <= r.status_code < 300
    except Exception:                                              # noqa: BLE001
        return False


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log_event(event: str, **fields) -> None:
    """Append one analytics event. Silently no-ops on any I/O failure."""
    try:
        ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
        record = {"ts": _utc_now(), "event": event, **fields}
        with EVENTS_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")
    except Exception:
        pass


def add_subscriber(email: str, state: str = "", source: str = "") -> tuple[bool, str]:
    """Validate + store a newsletter signup. Returns (ok, user-facing message)."""
    email = (email or "").strip().lower()
    if not _EMAIL_RE.match(email):
        return False, "That doesn't look like a valid email address."
    try:
        existing = load_subscribers()
        if not existing.empty and email in existing["email"].values:
            return True, "You're already on the list — thanks!"
        delivered = _post_subscriber(email, state, source)
        # CSV is the durable store when no webhook is configured, and a local
        # log/backstop when one is. Its failure only matters in CSV-only mode.
        csv_ok = True
        try:
            ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
            is_new_file = not SUBSCRIBERS_PATH.exists()
            with SUBSCRIBERS_PATH.open("a", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                if is_new_file:
                    writer.writerow(["ts", "email", "state", "source"])
                writer.writerow([_utc_now(), email, state, source])
        except Exception:                                          # noqa: BLE001
            csv_ok = False
        if not delivered and not csv_ok:
            return False, "Couldn't save your signup right now — please try again."
        log_event("newsletter_signup", state=state, source=source,
                  delivered=delivered)
        return True, "You're in! We'll email you when something changes in your state."
    except Exception:
        return False, "Couldn't save your signup right now — please try again."


def load_events() -> pd.DataFrame:
    """All logged events as a DataFrame (empty on any failure)."""
    try:
        if not EVENTS_PATH.exists():
            return pd.DataFrame()
        rows = []
        for line in EVENTS_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()


def load_subscribers() -> pd.DataFrame:
    """Subscriber list as a DataFrame (empty on any failure)."""
    try:
        if not SUBSCRIBERS_PATH.exists():
            return pd.DataFrame(columns=["ts", "email", "state", "source"])
        return pd.read_csv(SUBSCRIBERS_PATH)
    except Exception:
        return pd.DataFrame(columns=["ts", "email", "state", "source"])
