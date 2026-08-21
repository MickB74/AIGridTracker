#!/usr/bin/env python3
"""Link-check the permit paper trail — state registers, RTO queues, EPA tools.

These links are the whole value of the feature: a resident clicks through to
pull the permit file, and a 404 sends them back to a search engine, which is
what the registry exists to replace. State environmental agencies reorganise
their sites constantly (three of the URLs collected for this registry had
already moved during the first afternoon of research), so this is a chore that
recurs, not a one-time verification.

Reports the same classes as verify_sources.py, for the same reason — a host
that refuses bots is not a broken link, and reporting it as one trains the
maintainer to ignore the report:

  dead      404 or DNS failure — fix the URL
  flaky     5xx — the server had a bad minute; recheck before editing
  blocked   401/403/405/429, or a WAF block page served as 200 — bot
            refusal; a human must eyeball it

The WAF case is not hypothetical: NJDEP's DataMiner answers scripted requests
with an Imperva block page under HTTP 200, so a status-only check calls it
healthy. That link is still correct for a human in a browser, which is what
this registry is for — but reporting it as verified would be a lie, so it is
reported as blocked.

Usage:
    python3 scripts/verify_permit_portals.py
    python3 scripts/verify_permit_portals.py --out data/permit_portal_review.md
    python3 scripts/verify_permit_portals.py --strict    # exit 1 on dead links

Stdlib only, so CI installs nothing extra.
"""

import argparse
import datetime as dt
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts._linkcheck import BLOCKED_CODES, check_url          # noqa: E402
import urllib.error                                               # noqa: E402
import urllib.request                                             # noqa: E402
from src.constants import (                                       # noqa: E402
    FERC_ELIBRARY, NATIONAL_PERMIT_TOOLS, RTO_QUEUES,
    STATE_PERMIT_PORTALS,
)


UA_BODY = ("Mozilla/5.0 (compatible; GridWatchLinkCheck/1.0; "
           "+https://aigridwatch.com)")


def targets():
    """[(group, label, url)] — every URL the feature can hand a resident."""
    out = []
    for st, p in sorted(STATE_PERMIT_PORTALS.items()):
        out.append((st, p["agency"], p["agency_url"]))
        if p.get("register"):
            out.append((st, p["register_label"], p["register"]))
    for label, url in RTO_QUEUES.values():
        out.append(("RTO", label, url))
    for t in NATIONAL_PERMIT_TOOLS:
        out.append(("EPA", t["label"], t["url"]))
    out.append(("FERC", "FERC eLibrary", FERC_ELIBRARY))
    return out


# Markers that appear in the body of a bot-block interstitial served as 200.
# Kept short and specific — matching on "blocked" or "denied" would catch
# legitimate agency pages about permit denials.
_WAF_MARKERS = ("Incapsula incident ID", "_Incapsula_Resource",
                "Request unsuccessful", "Attention Required! | Cloudflare",
                "Checking your browser before accessing")


def looks_like_block_page(url):
    """True when a 200 response is really a WAF interstitial.

    Only called for responses that already passed the status check, and only
    reads the first few KB — the markers are all in the head.
    """
    req = urllib.request.Request(url, headers={"User-Agent": UA_BODY})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            head = r.read(4096).decode("utf-8", "replace")
    except (urllib.error.URLError, OSError):
        return False
    return any(m in head for m in _WAF_MARKERS)


def classify(code, err):
    if err or code is None:
        return "dead"
    if code in BLOCKED_CODES:
        return "blocked"
    if code >= 500:
        return "flaky"
    if code >= 400:
        return "dead"
    return "ok"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", help="write a markdown worklist here")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when any link is dead")
    args = ap.parse_args()

    rows = targets()

    def go(t):
        group, label, url = t
        code, err = check_url(url)
        verdict = classify(code, err)
        if verdict == "ok" and looks_like_block_page(url):
            verdict, code = "blocked", f"{code} (WAF block page)"
        return group, label, url, verdict, code, err

    with ThreadPoolExecutor(12) as ex:
        results = list(ex.map(go, rows))

    buckets = {"dead": [], "flaky": [], "blocked": []}
    for group, label, url, verdict, code, err in results:
        if verdict in buckets:
            buckets[verdict].append((group, label, url, code, err))

    lines = [f"# Permit portal link check — {dt.date.today().isoformat()}", "",
             f"{len(rows)} links checked · {len(buckets['dead'])} dead · "
             f"{len(buckets['flaky'])} flaky · {len(buckets['blocked'])} blocked",
             ""]
    for name, why in (("dead", "fix the URL in STATE_PERMIT_PORTALS"),
                      ("flaky", "server error — recheck before editing"),
                      ("blocked", "bot refusal — open in a browser to confirm")):
        if not buckets[name]:
            continue
        lines += [f"## {name} ({why})", ""]
        for group, label, url, code, err in sorted(buckets[name]):
            lines.append(f"- **{group}** {label} — `{code or err}` — {url}")
        lines.append("")

    report = "\n".join(lines)
    print(report)
    if args.out:
        Path(args.out).write_text(report + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    if args.strict and buckets["dead"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
