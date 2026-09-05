"""
Refresh data/senators.json — every sitting U.S. senator, with the one fact the
officials.json roster lacks: which class the seat is in, and so when it is
next on a ballot.

Source: the @unitedstates congress-legislators dataset (public domain),
`legislators-current.json`. The same dataset already supplies the House half
of officials.json via scripts/refresh_officials.py; this script reads only the
Senate terms and keeps only what senators.html renders.

    python3 scripts/refresh_senators.py            # fetch + write
    python3 scripts/refresh_senators.py --offline  # rebuild from the cached copy
    python3 scripts/refresh_senators.py --check    # fetch, report, write nothing

Stdlib only, like every other maintenance script: it runs off
requirements-build.txt. The cached copy of the upstream file lives in
data/external/ so an --offline rebuild is reproducible.
"""

import datetime
import json
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC_URL = "https://unitedstates.github.io/congress-legislators/legislators-current.json"
CACHE = ROOT / "data" / "external" / "legislators-current.json"
OUT = ROOT / "data" / "senators.json"

PARTY = {"Democrat": "Democratic"}


def fetch(offline):
    if offline:
        return json.loads(CACHE.read_text())
    req = urllib.request.Request(SRC_URL, headers={"User-Agent": "aigridwatch.com build"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_bytes(raw)
    return json.loads(raw)


def senators(legislators):
    out = []
    for leg in legislators:
        t = leg["terms"][-1]
        if t.get("type") != "sen":
            continue
        n = leg["name"]
        end = t["end"]
        out.append({
            "bioguide": leg["id"].get("bioguide"),
            "name": n.get("official_full") or f"{n['first']} {n['last']}",
            "first": n["first"],
            "last": n["last"],
            "state": t["state"],
            "party": PARTY.get(t.get("party"), t.get("party")),
            "class": t["class"],
            "term_start": t["start"],
            "term_end": end,
            # A full term ends January 3 of year Y, so the seat is on the
            # ballot in November of Y-1. Upstream ends an appointee's term on
            # the special-election date itself (Moody and Husted both carry
            # 2026-11-03), so a term that does not end on January 3 is on
            # the ballot in the year it ends. Derived, never stored by hand.
            "next_election": int(end[:4]) - (1 if end.endswith("-01-03") else 0),
            "state_rank": t.get("state_rank"),
            "website": t.get("url"),
            "contact": t.get("contact_form"),
            "phone": t.get("phone"),
        })
    out.sort(key=lambda s: (s["state"], s["state_rank"] != "senior", s["last"]))
    return out


def main(argv):
    offline = "--offline" in argv
    check = "--check" in argv
    rows = senators(fetch(offline))
    states = {r["state"] for r in rows}
    assert len(rows) == 100, f"expected 100 senators, got {len(rows)}"
    assert len(states) == 50, f"expected 50 states, got {len(states)}"
    by_year = {}
    for r in rows:
        by_year[r["next_election"]] = by_year.get(r["next_election"], 0) + 1
    print(f"{len(rows)} senators · next on the ballot: "
          + ", ".join(f"{y}: {n}" for y, n in sorted(by_year.items())))
    if check:
        return
    OUT.write_text(json.dumps({
        "generated": datetime.date.today().isoformat(),
        "source": SRC_URL,
        "source_name": "@unitedstates congress-legislators (legislators-current)",
        "senators": rows,
    }, indent=1) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])
