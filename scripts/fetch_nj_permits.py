#!/usr/bin/env python3
"""Mine NJDEP's air-permit register for data centers New Jersey already permits.

NJDEP's public face for this data is DataMiner (https://dep.nj.gov/dataminer/),
which sits behind an Imperva WAF that blocks every scripted request — and
answers the block with HTTP 200, so a naive link check calls it healthy. The
same NJEMS records are served without a WAF from NJDEP's own ArcGIS instance:

    https://mapsdep.nj.gov/arcgis/rest/services/Features/Environmental_NJEMS
        layer 15 — NJDEP Air Quality Permitted Facilities (~17k statewide)

Layer 15 carries the state's own NAICS/SIC classification per facility, so
"which of these is a data center" is answerable from the register rather than
guessed from a name. It does NOT carry permit numbers, application dates or
pending applications, so unlike PA DEP's tracker this is a census of what is
already permitted — not an early-warning feed. A brand-new proposal appears
here only once its air permit issues.

**This script never writes a registry**, and that is the whole difference from
fetch_pa_dep_projects.py. PA DEP publishes a list of data-center projects;
NJDEP publishes a list of permitted facilities that a filter has to guess at.
The filter is wrong in both directions and visibly so: Memorial Sloan
Kettering Cancer Center is coded NAICS 518210 in NJDEP's own data, and a real
colocation hall coded 541511 would be missed entirely. Every hit lands in a
review queue with the evidence that flagged it, and promoting one into
DC_SITES_DF or data/projects.json means a human reading the record — which is
where `source` and `as_of` come from.

Confidence is reported, never assumed:

  naics     NJDEP's own NAICS code is 5182x (data processing / hosting)
  operator  the facility name matches a tracked operator in OPERATORS_DF
  name      only the facility name says "data center" — weakest, most FPs

Usage:
    python3 scripts/fetch_nj_permits.py             # fetch + update queue
    python3 scripts/fetch_nj_permits.py --dry-run   # report, write nothing
    python3 scripts/fetch_nj_permits.py --offline   # reuse data/external/
    python3 scripts/fetch_nj_permits.py --report out.md

Stdlib-only, like its sibling scanners, so CI installs nothing beyond
requirements-build.txt.
"""

import argparse
import datetime as dt
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.constants import DC_SITES_DF, OPERATORS_DF, PROJECTS      # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "external" / "nj_njems_air_dc.json"
QUEUE = ROOT / "data" / "nj_permit_candidates.json"

SERVICE = ("https://mapsdep.nj.gov/arcgis/rest/services/Features/"
           "Environmental_NJEMS/MapServer/15/query")
HUMAN_SOURCE = "https://dep.nj.gov/dataminer/"
UA = ("Mozilla/5.0 (compatible; GridWatchNJPermits/1.0; "
      "+https://aigridwatch.com)")
TIMEOUT = 45

# Cast wide here and let the confidence tier sort it out downstream. A missed
# facility is invisible; a false positive is at least reviewable.
WHERE = (
    "NAICS_CODE LIKE '5182%' "
    "OR SIC_CODE LIKE '7374%' "
    "OR UPPER(FACILITY_NAME) LIKE '%DATA CENTER%' "
    "OR UPPER(FACILITY_NAME) LIKE '%DATA CTR%' "
    "OR UPPER(FACILITY_NAME) LIKE '%DATACENTER%'"
)
FIELDS = ("PREF_ID_NUM,SITE_ID,FACILITY_NAME,ADDRESS,CITY,ZIP,"
          "FACILITY_TYPE,FACILITY_DESC,NAICS_CODE,NAICS_DESC,"
          "SIC_CODE,SIC_DESC")


def fetch(offline=False):
    """Raw ArcGIS feature list. `--offline` reuses the cached snapshot."""
    if offline:
        if not CACHE.exists():
            raise SystemExit(f"--offline but no snapshot at {CACHE}")
        return json.loads(CACHE.read_text(encoding="utf-8"))

    params = urllib.parse.urlencode({
        "where": WHERE, "outFields": FIELDS, "outSR": "4326",
        "returnGeometry": "true", "f": "json",
    })
    req = urllib.request.Request(f"{SERVICE}?{params}",
                                 headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        payload = json.loads(r.read().decode("utf-8"))
    if "features" not in payload:
        # An ArcGIS error is a JSON body with an "error" key, not an HTTP
        # status — surface it rather than writing an empty queue.
        raise SystemExit(f"unexpected response from NJDEP: "
                         f"{json.dumps(payload)[:400]}")
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    return payload


def _operator_hits(name):
    """Tracked operators whose name appears in the facility name."""
    up = (name or "").upper()
    hits = []
    for op in OPERATORS_DF["operator"].dropna().unique():
        token = str(op).split("(")[0].strip().upper()
        if len(token) >= 4 and token in up:
            hits.append(str(op))
    return sorted(set(hits))


def confidence(attrs, operators):
    """Why this row was flagged — reported, so a reviewer knows what to check."""
    naics = str(attrs.get("NAICS_CODE") or "")
    if naics.startswith("5182"):
        return "naics"
    if operators:
        return "operator"
    return "name"


# NJDEP writes the municipality type into the city field ("Kenilworth Boro",
# "Secaucus Town"); our registries write a campus code or county instead
# ("Kenilworth (NEST11)", "Monroe Township (Gloucester County)"). Neither
# form is a prefix of the other, so a raw comparison reports every locality
# as new — which was exactly wrong for the one NJ site we already track.
_MUNI_SUFFIXES = ("township", "twp", "borough", "boro", "town", "city",
                  "village", "county")


def _norm_locality(value):
    """'Kenilworth (NEST11)' and 'Kenilworth Boro' -> 'kenilworth'."""
    text = str(value or "").split("(")[0].strip().lower()
    parts = text.replace(".", "").split()
    while parts and parts[-1] in _MUNI_SUFFIXES:
        parts.pop()
    return " ".join(parts)


def _known_localities():
    """NJ localities we already track, normalized, from both registries."""
    out = set()
    nj = DC_SITES_DF[DC_SITES_DF["state"] == "NJ"]
    for loc in nj["location"].dropna():
        out.add(_norm_locality(loc))
    for p in PROJECTS:
        if str(p.get("state") or "").upper() == "NJ":
            out.add(_norm_locality(p.get("locality")))
    return {x for x in out if x}


def _locality_seen(city, known):
    """Does this NJDEP municipality match one we already track?"""
    c = _norm_locality(city)
    return bool(c) and c in known


def build_rows(payload):
    known = _known_localities()
    rows = []
    for feat in payload.get("features", []):
        a = feat.get("attributes", {})
        geom = feat.get("geometry") or {}
        name = str(a.get("FACILITY_NAME") or "").strip()
        ops = _operator_hits(name)
        rows.append({
            "pref_id": str(a.get("PREF_ID_NUM") or "").strip(),
            "facility": name,
            "address": str(a.get("ADDRESS") or "").strip(),
            "locality": str(a.get("CITY") or "").strip(),
            "zip": str(a.get("ZIP") or "").strip(),
            "naics": str(a.get("NAICS_CODE") or "").strip() or None,
            "naics_desc": str(a.get("NAICS_DESC") or "").strip() or None,
            "sic": str(a.get("SIC_CODE") or "").strip() or None,
            "lat": round(geom["y"], 5) if geom.get("y") else None,
            "lon": round(geom["x"], 5) if geom.get("x") else None,
            "confidence": confidence(a, ops),
            "operators": ops,
            "locality_tracked": _locality_seen(a.get("CITY"), known),
            "source": HUMAN_SOURCE,
        })
    return sorted(rows, key=lambda r: (r["locality"].lower(), r["facility"]))


def merge(rows, today):
    """Update the queue in place: keep first_seen, bump last_seen, keep verdicts.

    Same contract as the other candidate queues — a row a human marked
    `"status": "dismissed"` (a hospital NJDEP coded as data processing, a
    facility already in DC_SITES_DF) is never resurrected.
    """
    prior = {}
    if QUEUE.exists():
        old = json.loads(QUEUE.read_text(encoding="utf-8"))
        for c in old.get("candidates", []):
            prior[c.get("pref_id")] = c

    out, added = [], 0
    for r in rows:
        was = prior.get(r["pref_id"])
        if was:
            merged = {**r,
                      "first_seen": was.get("first_seen", today),
                      "last_seen": today}
            for keep in ("status", "note"):
                if was.get(keep):
                    merged[keep] = was[keep]
            out.append(merged)
        else:
            out.append({**r, "first_seen": today, "last_seen": today})
            added += 1

    # A queue entry that vanished from the register still happened — keep it,
    # flagged, rather than silently dropping a facility NJDEP delisted.
    live = {r["pref_id"] for r in rows}
    for pid, was in prior.items():
        if pid not in live:
            out.append({**was, "gone_from_register": True})
    return out, added


README = (
    "NJDEP air-permitted facilities that look like data centers, mined from "
    "the NJEMS ArcGIS layer behind DataMiner by scripts/fetch_nj_permits.py. "
    "A REVIEW QUEUE, never a registry: the data-center filter is NJDEP's own "
    "NAICS code where it exists and a name match where it doesn't, and both "
    "are wrong in both directions (NJDEP codes Memorial Sloan Kettering as "
    "NAICS 518210). Read `confidence` before believing a row: naics > "
    "operator > name. Promoting one into DC_SITES_DF or data/projects.json "
    "means a human reading the record, which is where source + as_of come "
    "from. Mark a row \"status\": \"dismissed\" and it is never re-raised. "
    "This layer holds issued permits only — no permit numbers, no "
    "application dates, no pending applications — so it is a census of what "
    "is already permitted, not an early-warning feed."
)


def report(rows, added):
    by_conf = {}
    for r in rows:
        by_conf.setdefault(r["confidence"], []).append(r)
    untracked = [r for r in rows if not r["locality_tracked"]]
    lines = [f"# NJDEP data-center air permits — {dt.date.today().isoformat()}",
             "",
             f"{len(rows)} facilities flagged · {added} new since last run · "
             f"{len(untracked)} in localities we don't track yet", ""]
    for conf in ("naics", "operator", "name"):
        got = by_conf.get(conf, [])
        if not got:
            continue
        lines += [f"## confidence: {conf} ({len(got)})", ""]
        for r in sorted(got, key=lambda x: x["locality"]):
            flag = "" if r["locality_tracked"] else "  **new locality**"
            ops = f" · {', '.join(r['operators'])}" if r["operators"] else ""
            lines.append(f"- {r['facility']} — {r['locality']} "
                         f"(NJDEP ID {r['pref_id']}){ops}{flag}")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="report only, write nothing")
    ap.add_argument("--offline", action="store_true",
                    help="reuse the cached snapshot in data/external/")
    ap.add_argument("--report", help="write the markdown report here")
    args = ap.parse_args()

    today = dt.date.today().isoformat()
    rows = build_rows(fetch(offline=args.offline))
    merged, added = merge(rows, today)

    text = report(merged, added)
    print(text)
    if args.report:
        Path(args.report).write_text(text + "\n", encoding="utf-8")

    if args.dry_run:
        print("[dry-run] queue not written")
        return 0

    QUEUE.write_text(json.dumps({
        "updated": today,
        "source": HUMAN_SOURCE,
        "service": SERVICE,
        "_readme": README,
        "candidates": merged,
    }, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {QUEUE.relative_to(ROOT)} — {len(merged)} candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
