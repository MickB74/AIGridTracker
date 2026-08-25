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
    MORATORIUMS_DF, MORATORIUM_OUTCOMES, CBA_BENCHMARKS,
    COMPANY_CONCESSIONS, EXPIRING_SOON_DAYS, has_value,
)
from scripts._linkcheck import check_url as _check_url, classify  # noqa: E402

# High-churn data. Past this, "verified" is a claim about a different year.
STALE_AFTER_DAYS = 180

# Words that mean "this ends at some point" in a note field.
TERM_WORDS = ("-month", "-year", "year-long", "yearlong", "temporary",
              "interim", "pause until", "6 month", "12 month", "18 month")

SEVERITY = ["expired", "dead-link", "missing-source", "undated-term",
            "unclassified-term", "stale-as-of", "expiring", "blocked"]


def _days_since(iso):
    try:
        return (dt.date.today() - dt.date.fromisoformat(str(iso))).days
    except (ValueError, TypeError):
        return None


def _sourced_items():
    """Every registry row that claims a fact and carries its own citations.

    Yields (item, label, state, kind). Kept in one place so a new registry of
    this shape gets audited by adding a line here, rather than by someone
    remembering to. That is the failure this exists to prevent: the case
    studies were fixed on 2026-08-04 while the identical fabrications sat
    untouched in CBA_BENCHMARKS for another day.
    """
    for o in MORATORIUM_OUTCOMES:
        yield o, f"{o['locality']} case study", o["state"], o.get("category", "")
    for b in CBA_BENCHMARKS:
        yield b, f"{b['community']} benchmark", b["state"], b.get("company", "")
    for company, info in COMPANY_CONCESSIONS.items():
        for c in info.get("concessions", []):
            yield c, f"{company}: {c['where']}", "", "concession"


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

    # An enacted row with no end date used to be one undifferentiated chore.
    # It is really three, and only two are work:
    #   fixed_undated — a stated duration with no recorded start/end. Real
    #                   work, and the easiest kind: find the adoption date.
    #   unknown       — nobody has established how the term is bounded.
    #   standing / until_event — not a defect at all. A permanent ban has no
    #                   end date because it has no end, and saying "find the
    #                   adoption date" about one trains the worklist away.
    for r in rows:
        if r.effective_status != "Enacted" or has_value(r.expires):
            continue
        kind = getattr(r, "term_kind", "unknown")
        if kind == "fixed_undated":
            add(r, "undated-term",
                "note describes a fixed term but no end date is recorded — "
                "the page cannot expire it. Find the adoption date")
        elif kind == "unknown":
            add(r, "unclassified-term",
                "no end date and no `term` declared — the row could be a "
                "permanent ban or an unresearched pause and the page cannot "
                "tell the reader which. Read the source and set `term`")

    # Everything that carries `sources` + `as_of` gets the same audit. These
    # three registries are what a resident quotes out loud — case studies as
    # precedent, benchmarks as the ask, concessions to the company's own
    # representative — so an unsourced row here is the most dangerous text in
    # the repo. Both fabrications found on 2026-08-05 had propagated across
    # two of them, which is why this checks all three rather than the one that
    # happened to be noticed.
    for item, label, state, kind in _sourced_items():
        srcs = item.get("sources") or []
        if not srcs:
            findings.append({
                "kind": "missing-source", "locality": label, "state": state,
                "status": kind,
                "detail": "cites nothing; it renders as 'do not cite'. "
                          "Source it or drop it",
                "source": None})
            continue
        age = _days_since(item.get("as_of"))
        if age is None:
            findings.append({
                "kind": "missing-source", "locality": label, "state": state,
                "status": kind,
                "detail": f"unusable as_of: {item.get('as_of')!r}",
                "source": srcs[0]})
        elif age > STALE_AFTER_DAYS:
            findings.append({
                "kind": "stale-as-of", "locality": label, "state": state,
                "status": kind,
                "detail": f"last read {age}d ago (limit {STALE_AFTER_DAYS})",
                "source": srcs[0]})

    if check_links:
        # (row-or-item label, url) pairs, checked in one pass.
        targets = [(r, str(r.source)) for r in rows if has_value(r.source)]
        targets += [({"locality": label, "state": state, "status": kind}, u)
                    for item, label, state, kind in _sourced_items()
                    for u in (item.get("sources") or [])]
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
    items = list(_sourced_items())
    cases = len(items)
    # "cited" is deliberately not called "verified": it counts rows that name
    # a source and a date somebody recorded, which is the most this script can
    # see. Whether the page says the thing is a human read. COMPANY_CONCESSIONS
    # spent two weeks at 100% "verified" on 17 URLs that 404'd and several that
    # had never existed (see the note above the registry in constants.py).
    cases_ok = sum(1 for i, *_ in items
                   if i.get("sources") and _days_since(i.get("as_of")) is not None)
    counts = {k: sum(1 for f in findings if f["kind"] == k) for k in SEVERITY}

    out = ["# Moratorium tracker review queue",
           f"_Generated {dt.date.today().isoformat()} · {verified}/{total} "
           f"tracker rows sourced; {cases_ok}/{cases} quotable claims "
           f"(case studies, benchmarks, concessions) carry a citation and a "
           f"read date_", ""]
    if not checked_links:
        out.append("_Link checking skipped (--offline) — nothing below has "
                   "been confirmed to resolve, let alone to say what the row "
                   "claims._\n")
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
