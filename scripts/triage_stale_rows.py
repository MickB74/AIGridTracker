#!/usr/bin/env python3
"""Flag moratorium rows most likely to have changed since last review.

The deep-dive sweep researched every state; this script maintains it by
surfacing the rows a monthly re-check should prioritize:

  pending       status is Proposed or Under Review — a vote is coming
  expiring      expires within 90 days — extension, lapse, or conversion
  expired       term ran out — confirm whether it lapsed or was extended
  stale-active  Enacted with as_of older than 120 days — still in force?
  rescind-check Rescinded/Rejected but as_of > 120 days ago

The output is a worklist sorted by urgency, not an edit. Promotion means
reading the locality's own minutes/agenda and updating the row with a
fresh source + as_of.

Usage:
    python3 scripts/triage_stale_rows.py              # summary
    python3 scripts/triage_stale_rows.py --all         # full worklist
    python3 scripts/triage_stale_rows.py --json out.json
    python3 scripts/triage_stale_rows.py --state MA    # one state
"""

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.constants import MORATORIUMS_DF, has_value  # noqa: E402

PENDING_STATUSES = {"Proposed", "Under Review"}
ACTIVE_STALE_DAYS = 120
EXPIRING_SOON_DAYS = 90


def _days_since(iso):
    try:
        return (dt.date.today() - dt.date.fromisoformat(str(iso))).days
    except (ValueError, TypeError):
        return None


def _days_until(iso):
    try:
        return (dt.date.fromisoformat(str(iso)) - dt.date.today()).days
    except (ValueError, TypeError):
        return None


def triage(state=None):
    """Return a list of finding dicts, most urgent first."""
    findings = []
    rows = MORATORIUMS_DF
    if state:
        rows = rows[rows["state"] == state.upper()]

    for r in rows.itertuples():
        loc = f"{r.locality}, {r.state}"
        status = str(r.status)
        as_of_age = _days_since(r.as_of) if has_value(r.as_of) else None

        if status in PENDING_STATUSES:
            detail = f"Status is {status}"
            if has_value(r.when):
                detail += f" since {r.when}"
            if as_of_age is not None:
                detail += f" (last checked {as_of_age}d ago)"
            findings.append({
                "priority": 1,
                "kind": "pending",
                "locality": str(r.locality),
                "state": str(r.state),
                "status": status,
                "as_of": str(r.as_of) if has_value(r.as_of) else None,
                "detail": detail,
            })
            continue

        if has_value(r.expires):
            days_left = _days_until(r.expires)
            if days_left is not None:
                if days_left < 0:
                    if status not in ("Rescinded", "Rejected", "Defeated",
                                      "Vetoed", "Withdrawn"):
                        findings.append({
                            "priority": 2,
                            "kind": "expired",
                            "locality": str(r.locality),
                            "state": str(r.state),
                            "status": status,
                            "as_of": str(r.as_of) if has_value(r.as_of) else None,
                            "detail": f"Expired {-days_left}d ago ({r.expires})"
                                      f" — extended, lapsed, or converted?",
                        })
                elif days_left <= EXPIRING_SOON_DAYS:
                    findings.append({
                        "priority": 3,
                        "kind": "expiring",
                        "locality": str(r.locality),
                        "state": str(r.state),
                        "status": status,
                        "as_of": str(r.as_of) if has_value(r.as_of) else None,
                        "detail": f"Expires in {days_left}d ({r.expires})"
                                  f" — watch for extension or vote",
                    })

        if status == "Enacted" and as_of_age is not None:
            if as_of_age > ACTIVE_STALE_DAYS:
                findings.append({
                    "priority": 4,
                    "kind": "stale-active",
                    "locality": str(r.locality),
                    "state": str(r.state),
                    "status": status,
                    "as_of": str(r.as_of) if has_value(r.as_of) else None,
                    "detail": f"Enacted, last checked {as_of_age}d ago",
                })

    findings.sort(key=lambda f: (f["priority"], -(
        _days_since(f["as_of"]) or 0)))
    return findings


def main():
    parser = argparse.ArgumentParser(description="Triage stale moratorium rows")
    parser.add_argument("--all", action="store_true", help="Show full worklist")
    parser.add_argument("--state", help="Filter to one state")
    parser.add_argument("--json", metavar="FILE", help="Write JSON output")
    args = parser.parse_args()

    items = triage(state=args.state)

    if args.json:
        with open(args.json, "w") as f:
            json.dump(items, f, indent=2)
        print(f"Wrote {len(items)} items to {args.json}")
        return

    by_kind = {}
    for item in items:
        by_kind.setdefault(item["kind"], []).append(item)

    print(f"Triage: {len(items)} rows need attention")
    for kind in ("pending", "expired", "expiring", "stale-active"):
        group = by_kind.get(kind, [])
        if group:
            print(f"  {kind}: {len(group)}")

    if not args.all:
        print()
        top = items[:15]
        if top:
            print("Top 15 (use --all for full list):")
            for item in top:
                print(f"  [{item['kind']:14s}] {item['locality']}, "
                      f"{item['state']} — {item['detail']}")
        return

    print()
    for kind in ("pending", "expired", "expiring", "stale-active"):
        group = by_kind.get(kind, [])
        if not group:
            continue
        print(f"--- {kind} ({len(group)}) ---")
        for item in group:
            print(f"  {item['locality']}, {item['state']} — {item['detail']}")
        print()


if __name__ == "__main__":
    main()
