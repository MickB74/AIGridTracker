#!/usr/bin/env python3
"""
Tech & utility PAC money to 2026 U.S. Senate candidates, from the FEC.

Writes data/senate_money.json, which build_site.py renders under each
candidate on web/senate-races.html. Absent file -> the page shows no money
lines at all, which is deliberate: a blank total would read as "took nothing",
and that is a claim nobody has checked.

How it queries, and the wrong way that looks right
--------------------------------------------------
The obvious approach — ask /schedules/schedule_a/ for one candidate's receipts
via `candidate_id` — **silently returns the wrong data**. That endpoint has no
`candidate_id` filter, so the parameter is ignored and you get a nationwide
firehose of the largest receipts on record, sorted by amount. The first run
built this way paged 866 times, cached 266 MB, matched zero of 117 candidates,
and from the outside looked like a finding ("no tech money anywhere") rather
than a bug. Nothing in the response says the filter was dropped.

So this goes the other way round: resolve each term to a real PAC committee via
/committees/, then read that PAC's own contributions from /schedules/schedule_a/
with `contributor_id`, and keep the rows whose recipient is a 2026 Senate
candidate committee. Beyond correctness that is one pass per PAC (~70) rather
than thousands of pages per candidate, and what gets recorded is an FEC
committee id, not a substring that happened to match.

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
    python3 scripts/fetch_senate_money.py --max-requests 800

api.data.gov allows ~1,000 requests/hour per key. A run stops cleanly on a 429
and keeps what it already has instead of thrashing retries; re-running after
the hour rolls over resumes almost free, because every response is cached.

A free key comes from https://api.open.fec.gov/developers/. Stdlib only, so it
runs in CI off requirements-build.txt.
"""

import argparse
import hashlib
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


class RateLimited(Exception):
    """The key's hourly budget is gone. Stop and keep what we have."""


class Budget:
    def __init__(self, cap):
        self.cap, self.used = cap, 0

    def spend(self):
        self.used += 1
        if self.cap and self.used > self.cap:
            raise RateLimited(f"local cap of {self.cap} requests reached")


def _get(path, params, key, offline=False, budget=None):
    """One FEC API call, cached under data/external/fec/ so reruns are cheap.

    The cache key is the request path+query, so a re-run after a rate-limit
    stop replays what was already fetched without spending any budget.
    """
    qs = urllib.parse.urlencode(sorted(params.items()))
    slug = (path.strip("/").replace("/", "_") + "_"
            + hashlib.sha1(qs.encode()).hexdigest()[:16] + ".json")
    cached = CACHE / slug
    if cached.exists():
        try:
            return json.loads(cached.read_text())
        except ValueError:
            pass
    if offline:
        return None
    if budget:
        budget.spend()
    url = f"{API}{path}?{qs}&api_key={urllib.parse.quote(key)}"
    req = urllib.request.Request(url, headers={"User-Agent": "GridWatchAI/1.0"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                data = json.loads(r.read().decode())
            CACHE.mkdir(parents=True, exist_ok=True)
            cached.write_text(json.dumps(data))
            return data
        except urllib.error.HTTPError as e:
            if e.code == 429:
                # Hourly budget exhausted. Retrying burns the next hour too, so
                # surface it and let the caller save what it already has.
                raise RateLimited("HTTP 429 from api.data.gov") from e
            if e.code in (500, 502, 503) and attempt < 2:
                time.sleep(2 ** attempt * 3)
                continue
            print(f"  ! HTTP {e.code} on {path}", file=sys.stderr)
            return None
        except (urllib.error.URLError, TimeoutError):
            if attempt < 2:
                time.sleep(2 ** attempt * 3)
                continue
            return None
    return None


def find_candidate(name, state, key, offline, budget):
    """FEC candidate id for one Senate candidate, or None.

    Confirms on the FULL name, never a surname — the Alaska ballot carries two
    men named Sullivan.
    """
    d = _get("/candidates/search/", {
        "q": name, "office": "S", "state": state,
        "per_page": 20, "sort": "name"}, key, offline, budget)
    if not d or not d.get("results"):
        return None
    want = {p.lower().strip(".") for p in name.split() if len(p) > 2}
    best = None
    for r in d["results"]:
        if CYCLE not in (r.get("election_years") or []):
            continue
        got = {p.lower().strip(".,") for p in
               str(r["name"]).replace(",", " ").split()}
        overlap = len(want & got)
        if overlap >= 2 and (best is None or overlap > best[0]):
            best = (overlap, r["candidate_id"])
    return best[1] if best else None


def resolve_pacs(key, offline, budget):
    """MATCH_TERMS -> real FEC committees.

    Every match is kept with its committee id and official name, so a figure on
    the page traces back to an FEC committee rather than to a substring.
    """
    pacs = {}
    for term in MATCH_TERMS:
        d = _get("/committees/", {"q": term, "per_page": 20},
                 key, offline, budget)
        for c in (d or {}).get("results", []):
            ctype = str(c.get("committee_type_full") or "").upper()
            # Candidate and party committees are not industry money.
            if "PAC" not in ctype and "SEPARATE" not in ctype:
                continue
            pacs[c["committee_id"]] = {
                "id": c["committee_id"], "name": c["name"],
                "type": c.get("committee_type_full"), "matched_term": term,
            }
    return pacs


# Only committees the candidate actually controls count as money to them.
#   P = principal campaign committee, A = authorized by the candidate.
# Everything else is somebody else's money:
#   U = unauthorized — this is how the NRSC (C00027466) appears in Dan
#       Sullivan's committee list. Counting it credited every tech and utility
#       PAC donation to the national party as a personal contribution to him:
#       $821,000, including $95,000 "from Dell", against a $10,000 per-cycle
#       legal maximum.
#   J = joint fundraising committee — CASSIDY PERDUE SULLIVAN TILLIS VICTORY
#       FUND is shared by four candidates, so attributing it wholly to one is
#       wrong no matter which one you pick.
#   D = leadership PAC — the member's own vehicle for giving to others, not
#       money spent on their campaign.
KEEP_DESIGNATIONS = {"P", "A"}


def senate_committees(key, offline, budget):
    """Recipient committee id -> (state, candidate name, fec candidate id)."""
    out = {}
    for race in SENATE_RACES_2026:
        st = race["abbrev"]
        for c in race["candidates"]:
            cid = find_candidate(c["name"], st, key, offline, budget)
            if not cid:
                continue
            d = _get(f"/candidate/{cid}/committees/", {"per_page": 50},
                     key, offline, budget)
            for com in (d or {}).get("results", []):
                desig = str(com.get("designation") or "").upper()
                if not desig:
                    full = str(com.get("designation_full") or "").lower()
                    if "principal" in full:
                        desig = "P"
                    elif "authorized by a candidate" in full:
                        desig = "A"
                if desig not in KEEP_DESIGNATIONS:
                    continue
                out[com["committee_id"]] = (st, c["name"], cid)
    return out


def pac_contributions(pac_id, key, offline, budget, max_pages=8):
    """Contributions made BY one PAC during the cycle, deduplicated.

    Rows are keyed by `sub_id`, the FEC's unique row identifier, because deep
    paging with `page=N` REPEATS rows: the documented mechanism for walking
    past the first page is keyset pagination via the `last_indexes` block the
    API returns, and `sort` is not a unique ordering. Without the dedupe every
    total came out as a clean multiple of itself — Amazon's PAC showed
    $320,000 to one candidate against a $10,000 per-cycle legal maximum, and
    Duke Energy showed $60,000 and $64,000 to others. Numbers that are all
    suspiciously round multiples of the statutory cap are the tell.
    """
    rows, seen, page = [], set(), 1
    while page <= max_pages:
        d = _get("/schedules/schedule_a/", {
            "contributor_id": pac_id, "two_year_transaction_period": CYCLE,
            "per_page": 100, "page": page,
            "sort": "-contribution_receipt_amount"}, key, offline, budget)
        if not d or not d.get("results"):
            break
        fresh = 0
        for row in d["results"]:
            sid = row.get("sub_id")
            key_ = sid or (row.get("transaction_id"), row.get("committee_id"),
                           row.get("contribution_receipt_date"),
                           row.get("contribution_receipt_amount"))
            if key_ in seen:
                continue
            seen.add(key_)
            rows.append(row)
            fresh += 1
        # A page that adds nothing new means paging has started repeating.
        if fresh == 0 or len(d["results"]) < 100:
            break
        page += 1
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="report totals, write nothing")
    ap.add_argument("--offline", action="store_true",
                    help="reuse cached pages, make no requests")
    ap.add_argument("--max-requests", type=int, default=900,
                    help="stop before api.data.gov's hourly limit (0 = no cap)")
    args = ap.parse_args()

    key = os.environ.get("FEC_API_KEY", "")
    if not key and not args.offline:
        sys.exit("FEC_API_KEY is not set. Get a free key at "
                 "https://api.open.fec.gov/developers/ , or pass --offline "
                 "to reuse cached pages.")

    today = time.strftime("%Y-%m-%d")
    budget = Budget(args.max_requests)
    out, pacs, recipients, stopped = {}, {}, {}, None

    try:
        print("resolving PAC committees…")
        pacs = resolve_pacs(key, args.offline, budget)
        print(f"  {len(pacs)} committees matched from {len(MATCH_TERMS)} terms")

        print("mapping 2026 Senate candidate committees…")
        recipients = senate_committees(key, args.offline, budget)
        print(f"  {len(recipients)} committees across "
              f"{len({v[1] for v in recipients.values()})} candidates")

        print("reading PAC contributions…")
        for i, (pid, pac) in enumerate(sorted(pacs.items()), 1):
            for row in pac_contributions(pid, key, args.offline, budget):
                rcid = row.get("committee_id")
                if rcid not in recipients:
                    continue
                st, name, fec_id = recipients[rcid]
                amt = float(row.get("contribution_receipt_amount") or 0)
                if amt <= 0:
                    continue
                e = out.setdefault(f"{st}|{name}", {
                    "total": 0.0, "committees": {}, "cycle": CYCLE,
                    "pulled": today, "fec_candidate_id": fec_id,
                    "source": f"https://www.fec.gov/data/candidate/{fec_id}/",
                })
                e["total"] += amt
                e["committees"][pac["name"]] = round(
                    e["committees"].get(pac["name"], 0.0) + amt, 2)
    except RateLimited as e:
        # Keep the partial result. Every response is cached, so the next run
        # resumes almost free once the hour rolls over.
        stopped = str(e)
        print(f"\n  ! stopped: {e}", file=sys.stderr)

    for e in out.values():
        e["total"] = round(e["total"], 2)
        e["donors"] = len(e["committees"])
        e["committees"] = dict(sorted(e["committees"].items(),
                                      key=lambda kv: -kv[1]))

    for k, e in sorted(out.items(), key=lambda kv: -kv[1]["total"])[:25]:
        print(f"  + {k}: ${e['total']:,.0f} from {e['donors']} committees")
    print(f"\n{len(out)} candidate(s) with matched PAC money. "
          f"{budget.used} API request(s) this run.")
    if stopped:
        print("Run was cut short — re-run after the hour rolls over; the cache "
              "makes the completed part free.")

    if args.dry_run:
        print("--dry-run: nothing written.")
        return
    if not out:
        # An empty file is worse than no file: build_site renders money lines
        # only when the file exists, so shipping an empty one would publish
        # "no money found" for all 117 candidates.
        sys.exit("no candidate matched — refusing to write an empty "
                 f"{OUT.name}. Check FEC_API_KEY, or drop --offline.")
    OUT.write_text(json.dumps({
        "generated": today,
        "cycle": CYCLE,
        "roster_as_of": ROSTER_AS_OF,
        "complete": stopped is None,
        "stopped_reason": stopped,
        "method": ("Contributions made by PAC committees whose FEC-registered "
                   "name matches a published term list, to the principal and "
                   "candidate-authorized committees of 2026 Senate candidates. "
                   "Excludes party committees, joint fundraising committees and "
                   "leadership PACs — that is somebody else's money, not the "
                   "candidate's. Excludes individual contributions from company "
                   "employees, so every total is a floor, not a full industry "
                   "figure. Rows are deduplicated on the FEC's sub_id."),
        "match_terms": MATCH_TERMS,
        "matched_committees": sorted(p["name"] for p in pacs.values()),
        "candidates": out,
    }, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
