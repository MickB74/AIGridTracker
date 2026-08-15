#!/usr/bin/env python3
"""Validate the state-studies library and print a review worklist.

The studies page (`web/studies.html`, built from STATE_STUDIES in
src/ui/state_detail.py) has a quieter failure mode than the moratorium
tracker: the *report* it summarises does not go stale — a JLARC or CRC report
is still that report next year. Two things do go wrong on their own, and this
script is what notices them:

  dead-link       the PDF or source URL no longer resolves (a commissioner
                  clicks "Read the PDF" and lands on a 404)
  stale-as-of     nobody has re-read the entry in longer than a medium-churn
                  dataset supports, so a newer edition may have superseded it
                  without anyone checking

Plus the two structural gaps that make an entry uncitable at all:

  missing-source  no `src_key` in SOURCES and no `pdf_url` — nothing to click
  missing-date    no `as_of`, so it counts as never verified

It does not edit data. Promoting or refreshing a study is a human step, read
from the source — that is where `as_of` comes from — and this only produces
the queue that human works through.

Usage:
    python3 scripts/verify_studies.py              # full run, checks links
    python3 scripts/verify_studies.py --offline    # skip network
    python3 scripts/verify_studies.py --json out.json
    python3 scripts/verify_studies.py --strict     # exit 1 if anything fails

Deliberately stdlib-only (urllib, not requests). It runs in CI off
requirements-build.txt, which excludes requests and streamlit on purpose.
"""

import argparse
import ast
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.constants import SOURCES                              # noqa: E402
from scripts._linkcheck import check_many, classify           # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
STUDIES_SRC = ROOT / "src" / "ui" / "state_detail.py"

# Medium-churn data (new editions arrive over quarters, not weeks). Past this,
# "verified" is a claim about a report that may have been superseded.
STALE_AFTER_DAYS = 365

SEVERITY = ["dead-link", "missing-source", "missing-date", "stale-as-of",
            "blocked"]


def load_studies():
    """STATE_STUDIES as a plain dict, without importing streamlit.

    state_detail.py imports streamlit at module load, so it can't be imported
    in the requirements-build.txt CI env — read the literal instead, the same
    trick build_site.py::_load_ast_literal uses.
    """
    tree = ast.parse(STUDIES_SRC.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if getattr(target, "id", None) == "STATE_STUDIES":
                    return ast.literal_eval(node.value)
    raise SystemExit("STATE_STUDIES not found in src/ui/state_detail.py")


def _days_since(iso):
    try:
        return (dt.date.today() - dt.date.fromisoformat(str(iso))).days
    except (ValueError, TypeError):
        return None


def _source_url(study):
    """The SOURCES URL behind a study's src_key, or None."""
    key = study.get("src_key")
    if key in SOURCES:
        return SOURCES[key][1]
    return None


def audit(studies, check_links=True):
    """Return a list of finding dicts, worst first."""
    findings = []

    def add(state, kind, detail, source=None):
        findings.append({"state": state, "kind": kind, "detail": detail,
                         "source": source})

    for state, s in studies.items():
        src_url = _source_url(s)
        pdf_url = s.get("pdf_url")

        if not src_url and not pdf_url:
            add(state, "missing-source",
                "no src_key in SOURCES and no pdf_url — nothing to cite. Add "
                "the report's own URL")

        as_of = s.get("as_of")
        if not as_of:
            add(state, "missing-date",
                "no as_of recorded, so it counts as never verified. Read the "
                "source and stamp the date you read it")
        else:
            age = _days_since(as_of)
            if age is None:
                add(state, "missing-date", f"unparseable as_of: {as_of!r} "
                    "(want an ISO date, e.g. 2026-08-13)")
            elif age > STALE_AFTER_DAYS:
                add(state, "stale-as-of",
                    f"last read {age}d ago (limit {STALE_AFTER_DAYS}) — check "
                    "for a newer edition and re-stamp as_of")

    if check_links:
        # (state, label, url) for every clickable link on the page.
        targets = []
        for state, s in studies.items():
            if _source_url(s):
                targets.append((state, "source", _source_url(s)))
            if s.get("pdf_url"):
                targets.append((state, "PDF", s["pdf_url"]))
        results = check_many([u for _, _, u in targets])
        for (state, label, url), (code, err) in zip(targets, results):
            verdict = classify(code, err)
            if verdict == "dead":
                add(state, "dead-link", f"{label}: {err or f'HTTP {code}'} — "
                    f"{url}", source=url)
            elif verdict == "blocked":
                add(state, "blocked",
                    f"{label}: HTTP {code} (bot-blocked, check by hand)",
                    source=url)

    findings.sort(key=lambda f: SEVERITY.index(f["kind"]))
    return findings


def render(studies, findings, checked_links):
    total = len(studies)
    dated = sum(1 for s in studies.values() if s.get("as_of"))
    counts = {k: sum(1 for f in findings if f["kind"] == k) for k in SEVERITY}

    out = ["# State-studies review queue",
           f"_Generated {dt.date.today().isoformat()} · {dated}/{total} "
           f"studies carry a verification date_", ""]
    if not checked_links:
        out.append("_Link checking skipped (--offline)._\n")
    if not findings:
        out.append("Nothing to review — every study is sourced, dated, and "
                   "its links resolve.")
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
            src = f" · [link]({f['source']})" if f["source"] else ""
            out.append(f"- **{f['state']}** — {f['detail']}{src}")
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
                         "because a stale study is a chore, not a build break)")
    args = ap.parse_args()

    studies = load_studies()
    findings = audit(studies, check_links=not args.offline)
    report = render(studies, findings, checked_links=not args.offline)
    print(report)

    if args.out:
        Path(args.out).write_text(report + "\n", encoding="utf-8")
    if args.json:
        Path(args.json).write_text(
            json.dumps({"generated": dt.date.today().isoformat(),
                        "findings": findings}, indent=2) + "\n",
            encoding="utf-8")

    # Blocked links are informational (a human eyeballs them); everything else
    # is real work.
    actionable = [f for f in findings if f["kind"] != "blocked"]
    if args.strict and actionable:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
