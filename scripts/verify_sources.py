#!/usr/bin/env python3
"""Link-check every URL in SOURCES.

SOURCES is the spine of the whole site: `src_link(key)` renders these next to
numeric claims on nearly every page, so a rotted entry is a citation a
resident cannot defend at a hearing — the same failure the moratorium
validator exists to catch, just spread across ~100 keys nobody re-reads.

Reports three things a maintainer can act on:

  dead          the URL no longer resolves (404, DNS failure)
  unregistered  a tracked registry declares no provenance at all
  orphan        the key is defined but nothing references it
  flaky         5xx — the server had a bad minute; recheck before editing
  blocked       the host refuses bots (403/429); a human must eyeball it

Does not judge whether a source still *says* what the label claims — no
script can. It catches rot, not drift.

Usage:
    python3 scripts/verify_sources.py
    python3 scripts/verify_sources.py --offline    # orphans only, no network
    python3 scripts/verify_sources.py --out data/source_review.md
    python3 scripts/verify_sources.py --strict     # exit 1 on dead links

Stdlib only, so the weekly workflow installs nothing extra.
"""

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.constants import SOURCES, REGISTRY_PROVENANCE        # noqa: E402
from scripts._linkcheck import check_many, classify           # noqa: E402

# Registries whose numbers reach a reader — a page, a brief, or the printed
# pack. Each must declare its own freshness; see REGISTRY_PROVENANCE.
TRACKED_REGISTRIES = [
    "STATE_GRID_PROFILES", "STATE_DC_DF", "MORATORIUMS_DF", "DC_SITES_DF",
    "EXECUTIVES_DF", "MEGA_PROJECTS_DF",
]

# Where a src_link('key') / "key" reference could live.
SEARCH_DIRS = ("src", "scripts")
SEARCH_FILES = ("build_site.py", "app.py")


def _referenced_keys():
    """Keys mentioned anywhere outside the SOURCES definition itself."""
    blob = []
    for f in SEARCH_FILES:
        p = ROOT / f
        if p.exists():
            blob.append(p.read_text(encoding="utf-8", errors="ignore"))
    for d in SEARCH_DIRS:
        for p in (ROOT / d).rglob("*.py"):
            if p.name == "constants.py":
                # Read it, but drop the SOURCES literal — every key appears
                # there by definition, which would make nothing look orphaned.
                txt = p.read_text(encoding="utf-8", errors="ignore")
                txt = re.sub(r"^SOURCES\s*=\s*\{.*?^\}", "", txt,
                             flags=re.S | re.M)
                blob.append(txt)
            else:
                blob.append(p.read_text(encoding="utf-8", errors="ignore"))
    text = "\n".join(blob)
    return {k for k in SOURCES if f'"{k}"' in text or f"'{k}'" in text}


def audit(check_links=True):
    used = _referenced_keys()
    findings = []

    for key in sorted(SOURCES):
        if key not in used:
            findings.append({"kind": "orphan", "key": key,
                             "url": SOURCES[key][1],
                             "detail": "defined but never referenced — delete "
                                       "it or wire it up"})

    if check_links:
        keys = sorted(SOURCES)
        urls = [SOURCES[k][1] for k in keys]
        for key, url, (code, err) in zip(keys, urls, check_many(urls)):
            verdict = classify(code, err)
            if verdict == "dead":
                findings.append({"kind": "dead", "key": key, "url": url,
                                 "detail": err or f"HTTP {code}"})
            elif verdict == "blocked":
                findings.append({"kind": "blocked", "key": key, "url": url,
                                 "detail": f"HTTP {code} — check by hand"})
            elif verdict == "flaky":
                findings.append({"kind": "flaky", "key": key, "url": url,
                                 "detail": f"HTTP {code} — transient, recheck "
                                           f"before touching it"})

    # A registry with no REGISTRY_PROVENANCE entry declares nothing: no
    # vintage, no caveat, and no stale flag can ever fire for it. That is how
    # STATE_GRID_PROFILES sat undated while feeding every impact number and
    # the printed action pack — the freshness machinery worked perfectly and
    # was simply never pointed at it. Silence is the failure mode, so check
    # for the absence rather than trusting that someone remembered.
    for name in TRACKED_REGISTRIES:
        if name not in REGISTRY_PROVENANCE:
            findings.append({
                "kind": "unregistered", "key": name, "url": "",
                "detail": "registry has no REGISTRY_PROVENANCE entry — it can "
                          "never be flagged stale. Add as_of, source, churn "
                          "and a caveat"})

    order = ["dead", "unregistered", "orphan", "flaky", "blocked"]
    findings.sort(key=lambda f: order.index(f["kind"]))
    return findings


def render(findings, checked_links):
    out = ["# SOURCES review queue",
           f"_Generated {dt.date.today().isoformat()} · {len(SOURCES)} keys_",
           ""]
    if not checked_links:
        out.append("_Link checking skipped (--offline)._\n")
    if not findings:
        out.append("Every source resolves and every key is referenced.")
        return "\n".join(out)

    for kind in ("dead", "unregistered", "orphan", "flaky", "blocked"):
        group = [f for f in findings if f["kind"] == kind]
        if not group:
            continue
        out.append(f"## {kind} ({len(group)})")
        for f in group:
            out.append(f"- **`{f['key']}`** — {f['detail']} · <{f['url']}>")
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--out", metavar="PATH")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if any source is dead (blocked and orphan "
                         "are chores, not breakage)")
    args = ap.parse_args()

    findings = audit(check_links=not args.offline)
    report = render(findings, checked_links=not args.offline)
    print(report)
    if args.out:
        Path(args.out).write_text(report + "\n", encoding="utf-8")

    if args.strict and any(f["kind"] == "dead" for f in findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
