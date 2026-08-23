#!/usr/bin/env python3
"""Rank the moratorium review queue by how cheap each candidate is to verify.

The queue has grown past 900 unreviewed entries from five different scanners,
which is more than anyone will read top to bottom. The scanners answer "is
this worth a human's next twenty minutes?"; this script answers the question
that comes after it — *whose* twenty minutes are cheapest, and in what order.

Cost here means one thing only: how much work stands between the candidate and
the two fields the registry actually requires, `source` and `as_of`. A row that
arrives naming the document to pull is minutes of work. A row that arrives as a
Google News headline with no locality is an afternoon. Both are legitimate
research, but mixing them in one undifferentiated list is why 958 of them have
sat untouched.

The tiers, cheapest first:

    A  cited      A publisher link or a named document, plus a locality.
                  Read one page, write one row.
    B  structured Moratorium Nation rows with a date, an active status, and at
                  least one upstream verification. No source URL — upstream
                  publishes a confidence count, not a citation — so the
                  ordinance still has to be found, but locality + date +
                  legal basis make it a targeted search.
    C  thin       Structured but weak: verify_count 0, or pending/unknown
                  status, or no enactment date. Full research from scratch.
    D  unlocated  A headline with no resolvable locality. The first hour goes
                  to working out which town it is even about.

Nothing here writes a registry, and nothing here writes the queue: this is a
read-only view over `data/moratorium_candidates.json`. Promotion is still a
human reading a primary source, same as it has always been.

Already-published localities are dropped, so the list is only work that would
actually add a row.

Two things this script deliberately does not trust. A guessed state is still
a guess: `guess_state` used to be actively wrong (it filed Bernards Township
and Carter County both under Indiana, a case-sensitivity bug now fixed and
pinned by scripts/verify_state_guess.py), and it is now conservative rather
than infallible — it returns nothing for most headlines and can still be
fooled by a locality whose name it has never seen. So a guessed state is
rendered with a trailing `?` and never used to decide whether a locality is
already tracked, where a wrong state would let a duplicate through. And
scanner rows repeat: the same council vote arrives from three outlets. Those
collapse into one entry whose `coverage` count is itself a signal, since three
outlets covering one action is a stronger lead than one.

Usage:
    python3 scripts/triage_moratorium_candidates.py
    python3 scripts/triage_moratorium_candidates.py --tier A --limit 40
    python3 scripts/triage_moratorium_candidates.py --out worklist.md
    python3 scripts/triage_moratorium_candidates.py --json out.json

Deliberately stdlib-only, like its sibling scanners.
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.constants import MORATORIUMS  # noqa: E402

QUEUE = Path("data/moratorium_candidates.json")

# Dropped when fingerprinting a headline, so "Council approves data center
# moratorium" and "Data center moratorium approved by council" collapse.
_STOPWORDS = {
    "a", "an", "the", "of", "on", "in", "for", "to", "at", "by", "as", "and",
    "or", "its", "new", "data", "center", "centers", "centre", "s", "",
}

TIER_LABEL = {
    "A": "cited — link or named document in hand",
    "B": "structured — dated, active, upstream-verified; source still to find",
    "C": "thin — structured but unverified, pending, or undated",
    "D": "unlocated — headline with no resolvable locality",
}

# Upstream statuses worth a human's time before the rest. A rescinded or
# replaced ordinance is still a real registry row (the tracker stores
# `Rescinded`), but it is never the row a resident needs first.
LIVE_STATUS = {"active", "extended"}


def published_localities():
    """(locality, state) pairs already in the registry, lowercased."""
    return {
        (str(r["locality"]).strip().lower(), str(r["state"]).strip().upper())
        for r in MORATORIUMS
    }


def published_names():
    """Locality names alone — a candidate may not carry a state."""
    return {str(r["locality"]).strip().lower() for r in MORATORIUMS}


def locality_of(row):
    return row.get("locality") or row.get("guess_locality")


def state_of(row):
    """Authoritative state, or None. Never returns a guess."""
    return row.get("state")


def guessed_state(row):
    """The sweep's guess. Wrong often enough that callers must mark it."""
    return row.get("guess_state")


def where(row):
    """Human-readable place, with `?` on anything guessed."""
    loc = locality_of(row) or "—"
    st = state_of(row)
    if st:
        return f"{loc}, {st}"
    g = guessed_state(row)
    return f"{loc}, {g}?" if g else loc


def title_key(row):
    """Normalized title, for collapsing the same action reported repeatedly."""
    t = (row.get("title") or "").lower()
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return " ".join(sorted(set(t.split()) - _STOPWORDS))


def already_tracked(row, pairs, names):
    loc, st = locality_of(row), state_of(row)
    if not loc:
        return False
    loc = str(loc).strip().lower()
    if st:
        return (loc, str(st).strip().upper()) in pairs
    # No trustworthy state: fall back to the name, which over-matches on
    # purpose. A duplicate suppressed here costs one missed row; a duplicate
    # promoted costs a double-counted moratorium on a public page — the defect
    # this whole pass exists to clear.
    return loc in names


def classify(row):
    """Return (tier, one-line reason)."""
    origin = row.get("origin")
    loc = locality_of(row)

    if origin == "moratorium-nation":
        try:
            verify = int(row.get("upstream_verify_count") or 0)
        except (TypeError, ValueError):
            verify = 0
        status = (row.get("upstream_status") or "").lower()
        dated = bool(row.get("date_enacted_iso"))
        if dated and status in LIVE_STATUS and verify >= 1:
            return "B", f"{status}, enacted {row['date_enacted_iso']}, {verify}x upstream verify"
        why = []
        if not dated:
            why.append("no enactment date")
        if status not in LIVE_STATUS:
            why.append(status or "no status")
        if verify == 0:
            why.append("unverified upstream")
        return "C", ", ".join(why)

    # Scanner rows. A named document to pull beats a bare link, and a Google
    # News redirect is a link to a link — still cheap, but say which it is.
    if not loc:
        return "D", "no locality in the headline"
    if row.get("verify"):
        return "A", f"document named: {row['verify']}"
    link = row.get("link") or ""
    if link:
        kind = "google-news redirect" if "news.google.com" in link else "publisher link"
        return "A", f"{kind}, locality '{loc}'"
    return "D", f"locality '{loc}' but no link"


def load(queue_path):
    data = json.loads(queue_path.read_text())
    rows = data["candidates"] if isinstance(data, dict) else data
    return [r for r in rows if r.get("status", "new") == "new"]


def collapse(rows):
    """Fold repeat coverage of one action into a single candidate.

    Scanner rows are one per headline, so a vote covered by the local paper,
    the AP pickup and a trade blog is three queue entries. They are the same
    piece of research. Keyed on locality plus a word-set fingerprint of the
    headline, which is loose enough to survive re-wording and tight enough not
    to merge a proposal with the vote that rejected it.

    Structured rows are keyed on their upstream id instead and never merge.
    """
    groups = {}
    for row in rows:
        if row.get("origin") == "moratorium-nation":
            key = ("mn", row.get("upstream_id") or id(row))
        else:
            key = ((locality_of(row) or "").lower(), title_key(row))
        groups.setdefault(key, []).append(row)

    out = []
    for members in groups.values():
        # Keep the one that gives a researcher the most to work with: a named
        # document first, then a real publisher link over a news redirect.
        def rank(r):
            link = r.get("link") or ""
            return (0 if r.get("verify") else 1,
                    0 if link and "news.google.com" not in link else 1,
                    r.get("first_seen") or "9999")
        best = sorted(members, key=rank)[0]
        best = dict(best)
        best["coverage"] = len(members)
        best["outlets"] = sorted({m.get("outlet") for m in members if m.get("outlet")})
        out.append(best)
    return out


def triage(queue_path):
    pairs, names = published_localities(), published_names()
    rows, skipped = [], 0
    for row in load(queue_path):
        if already_tracked(row, pairs, names):
            skipped += 1
            continue
        rows.append(row)

    out = []
    for row in collapse(rows):
        tier, why = classify(row)
        out.append({
            "tier": tier,
            "why": why,
            "where": where(row),
            "locality": locality_of(row),
            "state": state_of(row),
            "guess_state": guessed_state(row),
            "title": row.get("title"),
            "origin": row.get("origin"),
            "link": row.get("link"),
            "coverage": row.get("coverage", 1),
            "outlets": row.get("outlets", []),
            "first_seen": row.get("first_seen"),
        })
    # Within a tier, corroboration first: more outlets on one action is the
    # cheapest thing resembling verification the queue can offer.
    out.sort(key=lambda r: (r["tier"], -r["coverage"],
                            r["state"] or r["guess_state"] or "ZZ",
                            r["locality"] or "zz"))
    return out, skipped


def render(rows, skipped, tier_filter=None, limit=None):
    by_tier = defaultdict(list)
    for r in rows:
        by_tier[r["tier"]].append(r)

    lines = ["# Moratorium candidate triage", ""]
    lines.append(f"{len(rows)} distinct candidates not already tracked "
                 f"({skipped} dropped as already published; repeat coverage collapsed).")
    lines.append("")
    lines.append("A trailing `?` on a state is inferred from the headline, not "
                 "confirmed — worth a glance before you search.")
    lines.append("")
    lines.append("| Tier | Meaning | Count |")
    lines.append("|---|---|---|")
    for t in "ABCD":
        lines.append(f"| {t} | {TIER_LABEL[t]} | {len(by_tier[t])} |")
    lines.append("")

    for t in "ABCD":
        picked = by_tier[t]
        if tier_filter and t not in tier_filter:
            continue
        if not picked:
            continue
        lines.append(f"## Tier {t} — {TIER_LABEL[t]} ({len(picked)})")
        lines.append("")
        states = Counter((r["state"] or (r["guess_state"] + "?" if r["guess_state"] else "unknown"))
                         for r in picked)
        lines.append("States: " + ", ".join(f"{s} {n}" for s, n in states.most_common(12)))
        lines.append("")
        for r in (picked[:limit] if limit else picked):
            corro = f" · {r['coverage']} outlets" if r["coverage"] > 1 else ""
            lines.append(f"- **{r['where']}**{corro} — {r['why']}")
            lines.append(f"  - {r['title']}")
            if r["link"]:
                lines.append(f"  - {r['link']}")
        if limit and len(picked) > limit:
            lines.append(f"- …and {len(picked) - limit} more (raise --limit)")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--queue", type=Path, default=QUEUE)
    ap.add_argument("--tier", help="only render these tiers, e.g. AB")
    ap.add_argument("--limit", type=int, help="max rows rendered per tier")
    ap.add_argument("--out", type=Path, help="write the markdown worklist here")
    ap.add_argument("--json", type=Path, help="write the ranked rows as JSON")
    args = ap.parse_args()

    if not args.queue.exists():
        print(f"queue not found: {args.queue}", file=sys.stderr)
        return 1

    rows, skipped = triage(args.queue)
    text = render(rows, skipped, args.tier, args.limit)

    if args.json:
        args.json.write_text(json.dumps(rows, indent=1) + "\n")
        print(f"wrote {args.json} ({len(rows)} rows)")
    if args.out:
        args.out.write_text(text + "\n")
        print(f"wrote {args.out}")
    if not args.out and not args.json:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
