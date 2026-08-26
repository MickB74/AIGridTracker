#!/usr/bin/env python3
"""
Audit what the race trackers already publish: dead links and stale reads.

Every record on senate-races.html and house-races.html is a claim about a named
candidate, backed by one URL. Two things rot: the link (outlets reorganise,
campaigns delete platforms after a primary) and the read date (a position from
six months ago is not evidence of where someone stands now). Both failures land
on a resident quoting a candidate at a hearing, so both get checked.

Classification matches scripts/verify_sources.py and verify_permit_portals.py,
deliberately: 401/403/405/429 are *blocked* (bot refusal, the page is fine in a
browser — congress.gov and most House member sites answer this way), 5xx is
*flaky*, and only 404/410/DNS is *dead*. Calling a blocked link dead would send
someone chasing a URL that works.

Read-only. Never edits a registry — a dead link needs a human to find the
replacement source, and a stale record needs someone to re-read it.

Usage
-----
    python3 scripts/verify_candidate_records.py
    python3 scripts/verify_candidate_records.py --offline   # staleness only
    python3 scripts/verify_candidate_records.py --strict    # exit 1 on dead
    python3 scripts/verify_candidate_records.py --out data/candidate_review.md
"""

import argparse
import datetime
import json
import pathlib
import sys
import socket
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import race_common as rc                       # noqa: E402
import src.senate_races as senate                       # noqa: E402
import src.house_races as house                         # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (compatible; GridWatchAI-linkcheck/1.0)"}
BLOCKED = {401, 403, 405, 429}


def check(url, timeout=20):
    req = urllib.request.Request(url, headers=UA, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return "ok", r.status
    except urllib.error.HTTPError as e:
        if e.code in BLOCKED:
            return "blocked", e.code
        if e.code in (404, 410):
            return "dead", e.code
        if 500 <= e.code < 600:
            return "flaky", e.code
        # Some servers reject HEAD but serve GET; retry once before judging.
        try:
            with urllib.request.urlopen(
                    urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return "ok", r.status
        except Exception:                                       # noqa: BLE001
            return "dead", e.code
    except (TimeoutError, socket.timeout):
        # A timeout is a big outlet refusing a scripted client (washingtonpost
        # and bloomberg both do this), not a missing page. Calling it dead sends
        # someone hunting a replacement for a URL that opens fine in a browser
        # — and makes --strict cry wolf, which is how a gate gets ignored.
        return "flaky", "timeout"
    except urllib.error.URLError as e:
        if isinstance(e.reason, socket.gaierror):
            return "dead", "dns"            # the host itself is gone
        if isinstance(e.reason, (TimeoutError, socket.timeout)):
            return "flaky", "timeout"
        return "flaky", type(e.reason).__name__
    except Exception as e:                                      # noqa: BLE001
        return "dead", type(e).__name__


def all_records():
    for k, v in senate.AI_RECORDS.items():
        yield "senate", k[0], k[-1], v
    for k, v in house.AI_RECORDS.items():
        yield "house", f"{k[0]}-{k[1]}", k[-1], v


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--offline", action="store_true",
                    help="skip link checks, report staleness only")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero if any link is dead")
    ap.add_argument("--out", help="write a markdown worklist here")
    args = ap.parse_args()

    today = datetime.date.today()
    rows, dead, stale, blocked = [], 0, 0, 0

    for chamber, key, name, rec in all_records():
        age = None
        if rec.get("as_of"):
            try:
                age = (today - datetime.date.fromisoformat(
                    str(rec["as_of"])[:10])).days
            except ValueError:
                age = None
        is_stale = age is None or age > rc.STALE_AFTER_DAYS
        if is_stale:
            stale += 1
        for item in rec.get("items", []):
            url = item.get("source", "")
            if args.offline:
                status, code = "skipped", ""
            else:
                status, code = check(url)
            if status == "dead":
                dead += 1
            if status == "blocked":
                blocked += 1
            rows.append({
                "chamber": chamber, "key": key, "name": name,
                "as_of": rec.get("as_of"), "age_days": age,
                "stale": is_stale, "status": status, "code": code,
                "url": url, "what": item.get("what", "")[:120],
            })
            print(f"  {status:8} {chamber[:3]} {key:8} {name[:24]:26} "
                  f"{'STALE ' if is_stale else '      '}{url[:66]}")

    n = len(rows)
    print(f"\n{n} cited item(s) across "
          f"{len(set((r['chamber'], r['name']) for r in rows))} candidates.")
    flaky = sum(1 for r in rows if r["status"] == "flaky")
    print(f"  dead: {dead}   blocked (bot refusal, not broken): {blocked}   "
          f"flaky (timeout/5xx, retry later): {flaky}   "
          f"stale records (> {rc.STALE_AFTER_DAYS}d): {stale}")

    if args.out:
        p = pathlib.Path(args.out)
        lines = [f"# Candidate record review — {today.isoformat()}", "",
                 f"{n} cited items · {dead} dead · {blocked} blocked · "
                 f"{stale} stale records", "",
                 "| Chamber | Race | Candidate | Read | Age | Link | Item |",
                 "|---|---|---|---|---|---|---|"]
        for r in sorted(rows, key=lambda r: (r["status"] != "dead",
                                             not r["stale"])):
            flag = "**DEAD**" if r["status"] == "dead" else r["status"]
            lines.append(
                f"| {r['chamber']} | {r['key']} | {r['name']} | "
                f"{r['as_of'] or '—'} | {r['age_days'] if r['age_days'] is not None else '—'}"
                f"{' ⏳' if r['stale'] else ''} | {flag} [{r['code']}]({r['url']}) | "
                f"{r['what']} |")
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"wrote {p}")

    if args.strict and dead:
        sys.exit(f"{dead} dead link(s) in published candidate records")


if __name__ == "__main__":
    main()
