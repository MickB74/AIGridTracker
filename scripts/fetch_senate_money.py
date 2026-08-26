#!/usr/bin/env python3
"""
Tech & utility PAC money to 2026 U.S. Senate candidates, from the FEC.

Writes data/senate_money.json, which build_site.py renders under each
candidate on web/senate-races.html. Absent file -> the page shows no money
lines at all, which is deliberate: a blank total would read as "took nothing",
and that is a claim nobody has checked.

Why the matching works the way it does
--------------------------------------
The FEC does not classify donors by industry — that is OpenSecrets' product,
not a government dataset. So this script does the one thing a public dataset
supports honestly: it pulls every *committee* contribution to each candidate
and matches the contributing committee's name against an explicit, published
list (MATCH_TERMS below). Every matched committee name is written into the
output, so any figure on the page can be audited back to the committees behind
it. That is a narrower claim than "industry money" and the page says so.

Consequence worth stating plainly: this **undercounts**. Individual
contributions from company employees are not counted (the FEC has no reliable
employer-industry rollup), and any PAC whose name does not contain a listed
term is missed. Treat a total here as a floor, never as the full picture.

Usage
-----
    FEC_API_KEY=... python3 scripts/fetch_senate_money.py
    python3 scripts/fetch_senate_money.py --dry-run     # report, write nothing
    python3 scripts/fetch_senate_money.py --offline     # reuse cached pages

A free key comes from https://api.open.fec.gov/developers/. Stdlib only, so it
runs in CI off requirements-build.txt.
"""

import argparse
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.senate_races import SENATE_RACES_2026, ROSTER_AS_OF  # noqa: E402

API = "https://api.open.fec.gov/v1"
CYCLE = 2026
CACHE = ROOT / "data" / "external" / "fec"
OUT = ROOT / "data" / "senate_money.json"

# Committee-name substrings counted as tech or utility money. Deliberately
# explicit and deliberately conservative — the list is the method, so it is
# published here and echoed into the output file rather than hidden in a
# heuristic. Lowercase; matched as substrings of the committee name.
MATCH_TERMS = [
    # hyperscalers and the AI buildout
    "alphabet", "google", "amazon", "microsoft", "meta platforms", "facebook",
    "apple inc", "oracle", "nvidia", "broadcom", "intel", "micron",
    "advanced micro devices", "openai", "anthropic", "palantir", "salesforce",
    "ibm", "hewlett", "dell technologies", "cisco",
    # data-center developers, REITs and colocation
    "equinix", "digital realty", "cyrusone", "quantumscape", "vantage",
    "switch inc", "iron mountain", "stack infrastructure", "aligned",
    # trade associations
    "information technology industry", "techNet", "computer & communications",
    "data center coalition", "netchoice",
    # investor-owned utilities and their trade bodies
    "edison electric", "american electric power", "duke energy", "dominion",
    "southern company", "exelon", "nextera", "xcel energy", "entergy",
    "firstenergy", "aes corp", "ppl corp", "sempra", "consolidated edison",
    "dte energy", "cms energy", "wec energy", "ameren", "evergy",
    "public service enterprise", "pinnacle west", "portland general",
    "alliant energy", "centerpoint", "vistra", "constellation energy",
    "nrg energy", "talen energy", "calpine",
]


def _get(path, params, key, offline=False):
    """One FEC API call, cached to data/external/fec/ so reruns are cheap."""
    qs = urllib.parse.urlencode(sorted(params.items()))
    slug = (path.strip("/").replace("/", "_") + "_"
            + str(abs(hash(qs)) % (10 ** 12)) + ".json")
    cached = CACHE / slug
    if cached.exists() and (offline or os.environ.get("FEC_FREEZE")):
        return json.loads(cached.read_text())
    if offline:
        return None
    url = f"{API}{path}?{qs}&api_key={urllib.parse.quote(key)}"
    req = urllib.request.Request(url, headers={"User-Agent": "GridWatchAI/1.0"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                data = json.loads(r.read().decode())
            CACHE.mkdir(parents=True, exist_ok=True)
            cached.write_text(json.dumps(data))
            return data
        except urllib.error.HTTPError as e:
            # 429 is the documented rate limit; back off rather than give up.
            if e.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(2 ** attempt * 3)
                continue
            print(f"  ! HTTP {e.code} on {path}", file=sys.stderr)
            return None
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < 3:
                time.sleep(2 ** attempt * 3)
                continue
            print(f"  ! {e} on {path}", file=sys.stderr)
            return None
    return None


def find_candidate(name, state, key, offline):
    """FEC candidate id for one Senate candidate, or None.

    Matches on surname within the state's 2026 Senate field, then confirms the
    full name — the Alaska ballot carries two men named Sullivan, so a surname
    match alone is not safe.
    """
    d = _get("/candidates/search/", {
        "q": name, "office": "S", "state": state, "election_year": CYCLE,
        "per_page": 20, "sort": "name"}, key, offline)
    if not d or not d.get("results"):
        return None
    want = {p.lower().strip(".") for p in name.split() if len(p) > 2}
    best = None
    for r in d["results"]:
        got = {p.lower().strip(".,") for p in str(r["name"]).replace(",", " ").split()}
        overlap = len(want & got)
        if overlap >= 2 and (best is None or overlap > best[0]):
            best = (overlap, r["candidate_id"])
    return best[1] if best else None


def committee_money(cand_id, key, offline):
    """(total, [committee names]) of matched committee receipts for a candidate."""
    total, names, page = 0.0, set(), 1
    while page <= 20:
        d = _get("/schedules/schedule_a/", {
            "candidate_id": cand_id, "two_year_transaction_period": CYCLE,
            "contributor_type": "committee", "per_page": 100, "page": page,
            "sort": "-contribution_receipt_amount"}, key, offline)
        if not d or not d.get("results"):
            break
        for row in d["results"]:
            cname = str(row.get("contributor_name") or "")
            low = cname.lower()
            if any(t.lower() in low for t in MATCH_TERMS):
                total += float(row.get("contribution_receipt_amount") or 0)
                names.add(cname)
        if len(d["results"]) < 100:
            break
        page += 1
    return total, sorted(names)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="report totals, write nothing")
    ap.add_argument("--offline", action="store_true",
                    help="reuse cached API pages, make no requests")
    args = ap.parse_args()

    key = os.environ.get("FEC_API_KEY", "")
    if not key and not args.offline:
        sys.exit("FEC_API_KEY is not set. Get a free key at "
                 "https://api.open.fec.gov/developers/ , or pass --offline "
                 "to reuse cached pages.")

    today = time.strftime("%Y-%m-%d")
    out, checked, found = {}, 0, 0
    for race in SENATE_RACES_2026:
        st = race["abbrev"]
        for c in race["candidates"]:
            checked += 1
            cid = find_candidate(c["name"], st, key, args.offline)
            if not cid:
                print(f"  - {st} {c['name']}: no FEC candidate id")
                continue
            total, names = committee_money(cid, key, args.offline)
            if total <= 0:
                print(f"  · {st} {c['name']}: no matched committee money")
                continue
            found += 1
            out[f"{st}|{c['name']}"] = {
                "total": round(total, 2),
                "donors": len(names),
                "committees": names,
                "cycle": CYCLE,
                "pulled": today,
                "fec_candidate_id": cid,
                "source": f"https://www.fec.gov/data/candidate/{cid}/",
            }
            print(f"  + {st} {c['name']}: ${total:,.0f} from {len(names)} committees")

    print(f"\n{found} of {checked} candidates have matched committee money.")
    if args.dry_run:
        print("--dry-run: nothing written.")
        return
    if not out:
        # An empty file is worse than no file: build_site renders money lines
        # only when the file exists, so shipping an empty one would silently
        # publish "no money found" for all 117 candidates.
        sys.exit("no candidate matched — refusing to write an empty "
                 f"{OUT.name}. Check FEC_API_KEY, or drop --offline.")
    OUT.write_text(json.dumps({
        "generated": today,
        "cycle": CYCLE,
        "roster_as_of": ROSTER_AS_OF,
        "method": ("Committee (PAC) receipts reported to the FEC whose "
                   "contributing-committee name matches a published term list. "
                   "Excludes individual contributions from company employees, "
                   "so every total is a floor, not a full industry figure."),
        "match_terms": MATCH_TERMS,
        "candidates": out,
    }, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
