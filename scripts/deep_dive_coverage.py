#!/usr/bin/env python3
"""
Deep dive coverage tracker.

Shows which states have been deep-dived for moratoriums and House records,
coverage stats, and recommends the next batch of states to research.

Usage:
    python3 scripts/deep_dive_coverage.py             # summary
    python3 scripts/deep_dive_coverage.py --next 5    # recommend next 5
    python3 scripts/deep_dive_coverage.py --all        # full state-by-state
    python3 scripts/deep_dive_coverage.py --json       # machine-readable
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DEEP_DIVED = {
    # batch 1 (2026-09-11)
    "CA", "MI", "OH", "VA", "NJ", "IN", "GA", "NC", "TX", "TN", "WI",
    # batch 2 (2026-09-11)
    "FL", "MD", "PA", "IA", "CO",
    # batch 3 (2026-09-11)
    "KY", "NY", "MO", "MN", "SC",
    # batch 4 (2026-09-11)
    "WA", "IL", "AL", "OK", "OR",
    # batch 5 (2026-09-11)
    "KS", "AR", "ME", "UT", "NH",
    # batch 6 (2026-09-11)
    "CT", "NV", "NM", "DE", "NE",
    # batch 7 (2026-09-12)
    "ID", "SD", "AZ", "MT", "AK",
}


def load_data():
    from src.constants import MORATORIUMS
    from src.house_races import AI_RECORDS

    with open(ROOT / "data" / "house_races_2026.json") as f:
        house = json.load(f)

    mora_by_state = Counter(m["state"] for m in MORATORIUMS)
    rec_by_state = Counter(k[0] for k in AI_RECORDS)
    dist_by_state = Counter(d["abbrev"] for d in house["districts"])

    all_states = sorted(set(mora_by_state) | set(dist_by_state))
    return all_states, mora_by_state, rec_by_state, dist_by_state, MORATORIUMS, AI_RECORDS


def state_row(st, mora_by_state, rec_by_state, dist_by_state):
    m = mora_by_state.get(st, 0)
    r = rec_by_state.get(st, 0)
    d = dist_by_state.get(st, 0)
    dived = st in DEEP_DIVED
    return {"state": st, "moratoriums": m, "records": r, "districts": d, "dived": dived}


def recommend_next(rows, n):
    undived = [r for r in rows if not r["dived"]]
    undived.sort(key=lambda r: (-r["moratoriums"], -r["districts"]))
    return undived[:n]


def main():
    parser = argparse.ArgumentParser(description="Deep dive coverage tracker")
    parser.add_argument("--next", type=int, default=0, help="Recommend next N states")
    parser.add_argument("--all", action="store_true", help="Show all states")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    all_states, mora_by_state, rec_by_state, dist_by_state, moratoriums, ai_records = load_data()
    rows = [state_row(st, mora_by_state, rec_by_state, dist_by_state) for st in all_states]

    total_mora = sum(r["moratoriums"] for r in rows)
    total_recs = len(ai_records)
    dived_count = sum(1 for r in rows if r["dived"])
    dived_mora = sum(r["moratoriums"] for r in rows if r["dived"])
    undived_mora = sum(r["moratoriums"] for r in rows if not r["dived"])

    if args.json:
        out = {
            "summary": {
                "total_states": len(all_states),
                "dived_states": dived_count,
                "remaining_states": len(all_states) - dived_count,
                "total_moratoriums": total_mora,
                "total_house_records": total_recs,
                "dived_moratoriums": dived_mora,
                "undived_moratoriums": undived_mora,
            },
            "states": rows,
        }
        if args.next:
            out["recommended"] = recommend_next(rows, args.next)
        json.dump(out, sys.stdout, indent=2)
        print()
        return

    print(f"Deep dive coverage: {dived_count}/{len(all_states)} states")
    print(f"  Moratoriums: {total_mora} total ({dived_mora} in dived states, {undived_mora} in remaining)")
    print(f"  House records: {total_recs}")
    print(f"  States dived: {', '.join(sorted(DEEP_DIVED))}")
    print()

    if args.all:
        print(f"{'ST':>2}  {'Mora':>4}  {'Rec':>3}  {'Dist':>4}  {'Dived':>5}")
        print(f"{'--':>2}  {'----':>4}  {'---':>3}  {'----':>4}  {'-----':>5}")
        for r in sorted(rows, key=lambda x: (-x["moratoriums"], x["state"])):
            flag = "  YES" if r["dived"] else ""
            print(f"{r['state']:>2}  {r['moratoriums']:>4}  {r['records']:>3}  {r['districts']:>4}{flag}")
        print()

    if args.next:
        recs = recommend_next(rows, args.next)
        print(f"Recommended next {len(recs)} states (by moratorium count + district count):")
        for r in recs:
            print(f"  {r['state']}: {r['moratoriums']} moratorium rows, "
                  f"{r['records']}/{r['districts']} House records")

    if not args.all and not args.next:
        remaining = [r for r in rows if not r["dived"]]
        remaining.sort(key=lambda r: (-r["moratoriums"], -r["districts"]))
        print("Remaining states (sorted by moratorium count):")
        for r in remaining:
            print(f"  {r['state']}: {r['moratoriums']} mora, {r['records']}/{r['districts']} House")


if __name__ == "__main__":
    main()
