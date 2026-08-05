#!/usr/bin/env python3
"""Validate the moratorium tracker and print a review worklist.

The tracker's failure mode is silence: a row goes stale, the page keeps
rendering it with a confident badge, and nobody notices until a resident
cites it at a hearing and gets corrected in public. This script is the thing
that notices. It does not edit data — it produces the queue a human works
through, because only a human reading the clerk's page can set an `as_of`.

Checks, worst first:

  expired         the documented term has run out (the page already says so)
  dead-link       the source URL no longer resolves
  missing-source  nobody has verified this row against anything
  undated-term    a time-limited moratorium with no recorded end date — the
                  page cannot tell whether it lapsed, so it still shows it as
                  in force. This is the gap the schema deliberately leaves
                  visible rather than papering over with a guessed date.
  stale-as-of     verified, but longer ago than a high-churn dataset supports
  expiring        ends within EXPIRING_SOON_DAYS; extension or lapse incoming
  blocked         source host refuses bots — a human must eyeball it

Usage:
    python3 scripts/verify_moratoriums.py              # full run, checks links
    python3 scripts/verify_moratoriums.py --offline    # skip network
    python3 scripts/verify_moratoriums.py --json out.json
    python3 scripts/verify_moratoriums.py --strict     # exit 1 if anything fails

Deliberately stdlib-only (urllib, not requests). It runs in CI off
requirements-build.txt, which excludes requests and streamlit on purpose.
"""

import argparse
import datetime as dt
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.constants import (                                   # noqa: E402
    MORATORIUMS_DF, MORATORIUM_OUTCOMES, EXPIRING_SOON_DAYS, has_value,
)
from scripts._linkcheck import check_url as _check_url, classify  # noqa: E402

# High-churn data. Past this, "verified" is a claim about a different year.
STALE_AFTER_DAYS = 180

# Words that mean "this ends at some point" in a note field.
TERM_WORDS = ("-month", "-year", "year-long", "yearlong", "temporary",
              "interim", "pause until", "6 month", "12 month", "18 month")

SEVERITY = ["expired", "dead-link", "missing-source", "undated-term",
            "stale-as-of", "expiring", "blocked"]


def _days_since(iso):
    try:
        return (dt.date.today() - dt.date.fromisoformat(str(iso))).days
    except (ValueError, TypeError):
        return None


def _looks_time_limited(note):
    n = str(note).lower()
    return any(w in n for w in TERM_WORDS)


def audit(check_links=True):
    """Return a list of finding dicts, worst first."""
    findings = []

    def add(row, kind, detail):
        findings.append({
            "kind": kind,
            "locality": str(row.locality),
            "state": str(row.state),
            "status": str(row.status),
            "detail": detail,
            "source": str(row.source) if has_value(row.source) else None,
        })

    rows = list(MORATORIUMS_DF.itertuples())

    for r in rows:
        if r.expired:
            add(r, "expired",
                f"term ran to {r.expires}; confirm whether it lapsed, was "
                f"extended, or became permanent zoning")
        elif r.expiring_soon:
            add(r, "expiring",
                f"ends {r.expires} ({r.days_left}d) — watch for an extension")

        if not has_value(r.source):
            add(r, "missing-source",
                "no source recorded; renders as unverified. Read the "
                "locality's own ordinance or agenda page")
            continue

        if not has_value(r.as_of):
            add(r, "missing-source",
                "has a source but no verification date, so it counts as "
                "unchecked. Read the source and record the date")
        else:
            age = _days_since(r.as_of)
            if age is None:
                add(r, "missing-source", f"unparseable as_of: {r.as_of!r}")
            elif age > STALE_AFTER_DAYS:
                add(r, "stale-as-of",
                    f"last read {age}d ago (limit {STALE_AFTER_DAYS})")

    # An enacted, time-limited row with no end date: the page shows it in
    # force indefinitely and has no way to know better.
    for r in rows:
        if (r.effective_status == "Enacted" and not has_value(r.expires)
                and _looks_time_limited(r.note)):
            add(r, "undated-term",
                "note describes a fixed term but no end date is recorded — "
                "the page cannot expire it. Find the adoption date")

    # Case studies get the same audit. They are labelled "precedents worth
    # citing" in the Start here wizard, which makes an unsourced one the most
    # dangerous text in the repo — it is read out loud at a hearing.
    for o in MORATORIUM_OUTCOMES:
        srcs = o.get("sources") or []
        where = f"{o['locality']} case study"
        if not srcs:
            findings.append({
                "kind": "missing-source", "locality": where,
                "state": o["state"], "status": o.get("category", ""),
                "detail": "case study cites nothing; it renders as "
                          "'do not cite'. Source it or drop it",
                "source": None})
            continue
        age = _days_since(o.get("as_of"))
        if age is None:
            findings.append({
                "kind": "missing-source", "locality": where,
                "state": o["state"], "status": o.get("category", ""),
                "detail": f"unusable as_of: {o.get('as_of')!r}",
                "source": srcs[0]})
        elif age > STALE_AFTER_DAYS:
            findings.append({
                "kind": "stale-as-of", "locality": where,
                "state": o["state"], "status": o.get("category", ""),
                "detail": f"last read {age}d ago (limit {STALE_AFTER_DAYS})",
                "source": srcs[0]})

    if check_links:
        # (row-or-outcome label, url) pairs, checked in one pass.
        targets = [(r, str(r.source)) for r in rows if has_value(r.source)]
        targets += [({"locality": f"{o['locality']} case study",
                      "state": o["state"], "status": o.get("category", "")}, u)
                    for o in MORATORIUM_OUTCOMES
                    for u in (o.get("sources") or [])]
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda t: _check_url(t[1]), targets))
        for (owner, url), (code, err) in zip(targets, results):
            def _add_link(kind, detail, owner=owner, url=url):
                if isinstance(owner, dict):
                    findings.append({"kind": kind, "locality": owner["locality"],
                                     "state": owner["state"],
                                     "status": owner["status"],
                                     "detail": detail, "source": url})
                else:
                    add(owner, kind, detail)
            verdict = classify(code, err)
            if verdict == "dead":
                _add_link("dead-link", f"{err or f'HTTP {code}'} — {url}")
            elif verdict == "blocked":
                _add_link("blocked", f"HTTP {code} (bot-blocked, check by hand)")

    findings.sort(key=lambda f: SEVERITY.index(f["kind"]))
    return findings


def render(findings, checked_links):
    total = len(MORATORIUMS_DF)
    verified = int(MORATORIUMS_DF["verified"].sum())
    cases = len(MORATORIUM_OUTCOMES)
    cases_ok = sum(1 for o in MORATORIUM_OUTCOMES if o.get("sources"))
    counts = {k: sum(1 for f in findings if f["kind"] == k) for k in SEVERITY}

    out = ["# Moratorium tracker review queue",
           f"_Generated {dt.date.today().isoformat()} · {verified}/{total} "
           f"tracker rows and {cases_ok}/{cases} case studies "
           f"source-verified_", ""]
    if not checked_links:
        out.append("_Link checking skipped (--offline)._\n")
    if not findings:
        out.append("Nothing to review — every row is sourced and current.")
        return "\n".join(out)

    out.append("| Check | Count |")
    out.append("|---|---|")
    for k in SEVERITY:
        if counts[k]:
            out.append(f"| {k} | {counts[k]} |")
    out.append("")

    for kind in SEVERITY:
        group = [f for f in findings if f["kind"] == kind]
        if not group:
            continue
        out.append(f"## {kind} ({len(group)})")
        for f in group:
            src = f" · [source]({f['source']})" if f["source"] else ""
            out.append(f"- **{f['locality']}, {f['state']}** "
                       f"({f['status']}) — {f['detail']}{src}")
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--offline", action="store_true",
                    help="skip HTTP link checking")
    ap.add_argument("--json", metavar="PATH",
                    help="also write findings as JSON")
    ap.add_argument("--out", metavar="PATH",
                    help="write the markdown worklist to a file")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when anything is flagged (default: exit 0, "
                         "because a stale row is a chore, not a build break)")
    args = ap.parse_args()

    findings = audit(check_links=not args.offline)
    report = render(findings, checked_links=not args.offline)
    print(report)

    if args.out:
        Path(args.out).write_text(report + "\n", encoding="utf-8")
    if args.json:
        Path(args.json).write_text(
            json.dumps({"generated": dt.date.today().isoformat(),
                        "findings": findings}, indent=2) + "\n",
            encoding="utf-8")

    # Expiring-soon and blocked are informational; everything else is work.
    actionable = [f for f in findings
                  if f["kind"] not in ("expiring", "blocked")]
    if args.strict and actionable:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
