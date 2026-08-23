#!/usr/bin/env python3
"""Golden cases for story_tracker.guess_state.

This function has silently produced wrong data twice. The second time it
mislabelled 45 queue rows as Indiana, because the sweep's private copy keyed
its lookup on lowercased abbreviations and matched case-sensitively, so the
English word "in" resolved to IN. Nothing failed; the rows just quietly
claimed the wrong state, and a triage list built on them sent a researcher to
the wrong state's records.

That is the failure mode worth guarding: no exception, no empty output, just
plausible wrong answers. Hence a table of cases rather than a smoke test, with
both directions represented — what must resolve, and what must stay None.
Guessing nothing is always better than guessing wrong here, because a null
prompts a human to look and a wrong state does not.

Usage:
    python3 scripts/verify_state_guess.py
    python3 scripts/verify_state_guess.py --quiet    # only report failures

Stdlib-only, so it can run in CI off requirements-build.txt.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.story_tracker import guess_state  # noqa: E402

# (headline, expected abbrev or None, why this case is here)
CASES = [
    # Full names resolve, case-insensitively.
    ("Ohio residents sue over data center", "OH", "plain state name"),
    ("Indiana counties pause data centers", "IN", "name, not the preposition"),
    # Postal context.
    ("Loudoun County, VA approves pause", "VA", "comma-prefixed abbrev"),
    ("Texas HB 1234 targets data centers", "TX", "bill token"),
    # Bare uppercase abbrevs — the common headline form.
    ("More NJ towns ban AI data centers", "NJ", "bare abbrev before a noun"),
    ("WV leaders pledge ratepayer protections", "WV", "bare abbrev, sentence start"),
    ("Western MD county approves data center moratorium", "MD", "bare abbrev mid-sentence"),
    # The regression that shipped: English words are not states.
    ("Data center ban proposed in Bernards Township", None, "the word 'in'"),
    ("Residents rally or protest data center", None, "the word 'or'"),
    ("Council backs data center, ok with residents", None, "the word 'ok'"),
    # Uppercase collisions found in the real archive.
    ("DC Blox sues Metro over data center moratorium", None, "DC Blox is an operator"),
    ("Andover backtracks on OK'ing massive AI facilities", None, "OK'ing"),
    ("Google ID'd as Operator of Tulsa Area Data Center", None, "ID'd"),
    ("DATA CENTER CREATES BUZZ IN VINELAND", None, "IN in an all-caps headline"),
    # Cities carrying another state's name.
    ("Kansas City officials denied a plan", None, "ambiguous city, no state given"),
    ("Kansas City, MO council votes", "MO", "same city, state stated"),
    ("Oklahoma City council weighs pause", None, "ambiguous city"),
    # Two states named: the one led with wins, not registry order.
    ("Ohio utility sues Indiana regulator", "OH", "earliest match, not A-Z"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quiet", action="store_true", help="only print failures")
    args = ap.parse_args()

    failures = []
    for headline, expected, why in CASES:
        got = guess_state(headline)
        ok = got == expected
        if not ok:
            failures.append((headline, expected, got, why))
        if not args.quiet:
            print(f"{'ok  ' if ok else 'FAIL'} {str(got):5} "
                  f"(want {str(expected):5})  {why}")

    if failures:
        print(f"\n{len(failures)} of {len(CASES)} failed:", file=sys.stderr)
        for headline, expected, got, why in failures:
            print(f"  {headline!r}\n    want {expected!r}, got {got!r} — {why}",
                  file=sys.stderr)
        return 1
    if not args.quiet:
        print(f"\nall {len(CASES)} cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
