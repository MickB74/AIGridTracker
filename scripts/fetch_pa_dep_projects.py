#!/usr/bin/env python3
"""Sync Pennsylvania DEP's Data Center Permit Tracker into data/projects.json.

Unlike scan_project_candidates.py, this one writes to the registry directly.
The difference is the source: a news headline needs a human to read a primary
document before it earns a `source` + `as_of`, but PA DEP *is* the primary
document. The tracker is the Commonwealth's own list of every data-center
project its regional offices know about, published as two plain CSVs behind
the ArcGIS front end at

    https://gis.dep.pa.gov/DataCenterPermitTracker/

    static/DataCenterProjectTrackingAllProjects.csv  — one row per project
    static/DataCenterPermitTracking.csv              — one row per permit

So `source` is that URL and `as_of` is the date we read it, both known without
a judgement call. Every row this script writes carries `origin: "pa-dep"`,
which is what makes the automation reversible: a human can tell at a glance
which rows a state agency vouches for and which a person researched.

What it will NOT do:

  * Clobber a hand-written row. Rows without `origin: "pa-dep"` are never
    rewritten. When a DEP project looks like one we already track by hand, the
    script reports the collision and skips it — merging two research trails is
    a human call.
  * Infer a land-use outcome. DEP's "DEP Review Complete" means the
    *environmental permits* are done, not that a township approved anything,
    so `outcome` stays null. Reading it as approval would put a false claim in
    a resident's mouth at a hearing.
  * Invent a date. `announced` stays null (DEP doesn't record it);
    `rezoning_filed` is the earliest permit application date, which is the
    only filing date the tracker actually knows.

Permits become `events`. Each is dated (the application date), sourced, and
names its permit number and eFACTS authorization ID so anyone can pull the
file — that is the intelligence log we otherwise assemble by hand.

Usage:
    python3 scripts/fetch_pa_dep_projects.py            # fetch + merge
    python3 scripts/fetch_pa_dep_projects.py --dry-run  # report, write nothing
    python3 scripts/fetch_pa_dep_projects.py --offline  # reuse data/external/
    python3 scripts/fetch_pa_dep_projects.py --report out.md

Stdlib-only, like its sibling scanners, so the CI job installs nothing beyond
requirements-build.txt.
"""

import argparse
import csv
import datetime as dt
import io
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS_PATH = ROOT / "data" / "projects.json"
EXTERNAL = ROOT / "data" / "external"

TRACKER_URL = "https://gis.dep.pa.gov/DataCenterPermitTracker/"
BASE = "https://gis.dep.pa.gov/DataCenterPermitTracker/static/"
PROJECT_CSV = "DataCenterProjectTrackingAllProjects.csv"
PERMIT_CSV = "DataCenterPermitTracking.csv"

ORIGIN = "pa-dep"
UA = "GridWatchAI/1.0 (+https://aigridwatch.com; data-center permit tracking)"

# Tokens that carry no identity — every third project is an "Unnamed Data
# Center (Some LLC)", so matching on these would fuse unrelated campuses.
_STOPWORDS = {
    "data", "center", "centers", "centre", "project", "projects", "unnamed",
    "llc", "inc", "lp", "llp", "co", "company", "corp", "corporation",
    "development", "developer", "developments", "group", "holdings",
    "associates", "partners_", "properties", "property", "real", "estate",
    "township", "townships", "borough", "city", "county", "twp", "the", "of",
    "and", "at", "campus", "site", "park", "expansion", "unknown", "new",
}
# Directional prefixes are not identity either: "Upper Burrell" and "Upper
# Merion" are 200 miles apart and share only the word "Upper".
_PLACE_FILLER = {"upper", "lower", "north", "south", "east", "west", "big",
                 "little", "old", "mount", "mt", "saint", "st"}
_LLC_RE = re.compile(r"\b(LLC|L\.L\.C\.|LP|L\.P\.|Inc\.?|Ltd\.?|Corp\.?)\b", re.I)


# --------------------------------------------------------------------------- #
# fetch
# --------------------------------------------------------------------------- #

def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8-sig")


def load_csvs(offline=False, cache=True):
    """Return (project_rows, permit_rows). Falls back to the cached copy."""
    out = []
    for name in (PROJECT_CSV, PERMIT_CSV):
        cached = EXTERNAL / ("pa_dep_" + ("projects" if name == PROJECT_CSV
                                          else "permits") + ".csv")
        if offline:
            if not cached.exists():
                raise SystemExit(f"--offline but no cached copy at {cached}")
            text = cached.read_text(encoding="utf-8")
        else:
            text = _get(BASE + name)
            if cache:
                EXTERNAL.mkdir(parents=True, exist_ok=True)
                cached.write_text(text, encoding="utf-8")
        out.append(list(csv.DictReader(io.StringIO(text))))
    return out[0], out[1]


# --------------------------------------------------------------------------- #
# normalise
# --------------------------------------------------------------------------- #

def _clean(v):
    return (v or "").strip()


def split_name(raw):
    """"Project Atlas (Edged US)" -> ("Project Atlas", "Edged US").

    DEP writes the developer in a trailing parenthetical. When that
    parenthetical is a shell entity ("Archbald 25 Developer LLC") it is also
    the filing LLC, which is exactly the unmasking link DC_SITES_DF trades in.
    """
    raw = _clean(raw)
    m = re.match(r"^(.*?)\s*\(([^()]*)\)\s*$", raw)
    if not m:
        return raw, None, None
    name, paren = m.group(1).strip(), m.group(2).strip()
    if not name:                       # the whole title was parenthesised
        return paren, None, None
    llc = paren if _LLC_RE.search(paren) else None
    return name, paren or None, llc


def _tokens(text):
    return {t for t in re.split(r"[^a-z0-9]+", (text or "").lower()) if t}


def identity_tokens(row):
    """Distinctive tokens for a DEP row — place words deliberately removed.

    Luzerne County alone has three unrelated projects in Salem Township, so a
    township name proves nothing about identity. What distinguishes them is
    the code name and the developer.
    """
    name, operator, _ = split_name(row["ProjectName"])
    place = _tokens(row.get("Municipality")) | _tokens(row.get("County"))
    return (_tokens(name) | _tokens(operator)) - _STOPWORDS - place


def _f(v):
    try:
        return round(float(v), 6)
    except (TypeError, ValueError):
        return None


def _iso(v):
    """DEP writes M/D/YYYY. Returns ISO, or None — never a guessed date."""
    v = _clean(v)
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"):
        try:
            return dt.datetime.strptime(v, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def slugify(*parts):
    s = re.sub(r"[^a-z0-9]+", "-", " ".join(p or "" for p in parts).lower())
    return re.sub(r"-+", "-", s).strip("-")


def locality_of(row):
    muni, county = _clean(row.get("Municipality")), _clean(row.get("County"))
    if muni and county:
        return f"{muni} ({county} County)"
    return muni or (f"{county} County" if county else "")


def build_note(row, permits):
    """Plain language, and careful about what DEP's status does not mean."""
    status = _clean(row.get("ProjectStatus"))
    issued = sum(1 for p in permits if _clean(p.get("Status")).lower() == "issued")
    pending = sum(1 for p in permits if _clean(p.get("Status")).lower() == "pending")

    if status.startswith("Proposed"):
        head = ("On PA DEP's tracker as proposed — no permit applications "
                "received yet.")
    elif status == "DEP Review Complete":
        head = (f"PA DEP has finished reviewing this project's environmental "
                f"permits ({issued} issued). That is a permit milestone, not "
                f"a local land-use approval.")
    elif status == "Under Review":
        bits = []
        if pending:
            bits.append(f"{pending} pending")
        if issued:
            bits.append(f"{issued} issued")
        head = ("Environmental permits under review at PA DEP"
                + (" (" + ", ".join(bits) + ")." if bits else "."))
    else:
        head = f"PA DEP project status: {status or 'not recorded'}."

    if _clean(row.get("FastTrack")).lower() == "yes":
        head += (" Flagged by DEP as a fast-track project, so the permit "
                 "review clock is shorter than usual.")
    if _clean(row.get("PermitStatus")) == "UnsubmittedUnlocated":
        head += " DEP records the location as approximate."
    return head


def permit_events(permits):
    """One dated, sourced event per permit application."""
    events = []
    for p in sorted(permits, key=lambda r: (_iso(r.get("Submitted")) or "9999",
                                            _clean(r.get("PermitNumber")))):
        date = _iso(p.get("Submitted"))
        if not date:
            continue                     # never invent a date
        auth = _clean(p.get("AuthorizationType")) or _clean(p.get("AuthorizationCategory"))
        cat = _clean(p.get("AuthorizationCategory"))
        num = _clean(p.get("PermitNumber"))
        eid = _clean(p.get("eFactsAuthID"))
        status = _clean(p.get("Status")) or "status not recorded"
        ref = " / ".join(x for x in (num, f"eFACTS auth {eid}" if eid else "") if x)
        summary = (f"{auth} application submitted to PA DEP"
                   + (f" under {cat}" if cat and cat != auth else "")
                   + (f" ({ref})" if ref else "")
                   + f" — DEP status: {status}.")
        events.append({"date": date, "kind": "permit", "summary": summary,
                       "source": TRACKER_URL})
    return events


def to_record(row, permits, today, existing_id=None):
    name, operator, llc = split_name(row["ProjectName"])
    events = permit_events(permits)
    filed = events[0]["date"] if events else None
    # "Unnamed Data Center" is the most common name on the tracker, so the
    # developer has to carry the slug or two unrelated campuses in the same
    # township collapse into one id.
    stem = name if (_tokens(name) - _STOPWORDS) else " ".join(x for x in (operator, name) if x)
    pid = existing_id or slugify(stem, _clean(row.get("Municipality")), "pa")
    return {
        "id": pid,
        "name": name,
        "operator": operator,
        "owner": None,
        "tenant": None,
        "filing_llc": llc,
        "locality": locality_of(row),
        "state": "PA",
        "lat": _f(row.get("Latitude")),
        "lon": _f(row.get("Longitude")),
        "size_mw": None,
        "acres": None,
        "announced": None,
        "rezoning_filed": filed,
        "hearing_date": None,
        "decided_date": None,
        "outcome": None,
        "note": build_note(row, permits),
        "source": TRACKER_URL,
        "as_of": today,
        "origin": ORIGIN,
        "pa_dep_id": _clean(row.get("ProjectID")),
        "pa_dep_county": _clean(row.get("County")),
        "pa_dep_status": _clean(row.get("ProjectStatus")),
        "events": events,
    }


# --------------------------------------------------------------------------- #
# merge
# --------------------------------------------------------------------------- #

def _near(a, b, tol=0.06):
    if a is None or b is None:
        return False
    return abs(a - b) <= tol


def find_collision(row, hand_rows):
    """A hand-written row that plausibly describes this DEP project.

    Requires a distinctive token in common (code name or developer) AND a
    place agreement (coordinates, municipality, or county). Either half alone
    produces false pairs: three Salem Township projects share a township, and
    "Amazon" appears in a dozen unrelated rows nationally.
    """
    dep_tokens = identity_tokens(row)
    if not dep_tokens:
        return None
    lat, lon = _f(row.get("Latitude")), _f(row.get("Longitude"))
    muni = _tokens(row.get("Municipality")) - _STOPWORDS
    county = _tokens(row.get("County")) - _STOPWORDS

    for h in hand_rows:
        h_tokens = (_tokens(h.get("name")) | _tokens(h.get("operator"))
                    | _tokens(h.get("filing_llc"))) - _STOPWORDS
        if not (dep_tokens & h_tokens):
            continue
        h_place = _tokens(h.get("locality"))
        same_place = (
            (_near(lat, _f(h.get("lat"))) and _near(lon, _f(h.get("lon"))))
            or bool(muni & h_place)
            or bool(county & h_place)
        )
        if same_place:
            return h
    return None


def same_township(row, hand_rows):
    """Hand rows in the same municipality — reported for human review.

    Not a collision: multiple distinct campuses per township is the norm in
    Luzerne and Lackawanna. But it is where a missed duplicate would hide, so
    the report names them rather than staying quiet.
    """
    muni = _tokens(row.get("Municipality")) - _STOPWORDS - _PLACE_FILLER
    if not muni:
        return []
    return [h for h in hand_rows
            if muni & (_tokens(h.get("locality")) - _PLACE_FILLER)]


def merge_events(old, new):
    """Union by (date, summary), keeping anything a human added by hand."""
    seen = {(e.get("date"), e.get("summary")) for e in old}
    merged = list(old)
    for e in new:
        if (e.get("date"), e.get("summary")) not in seen:
            merged.append(e)
            seen.add((e.get("date"), e.get("summary")))
    merged.sort(key=lambda e: (e.get("date") or "", e.get("kind") or ""))
    return merged


def merge(payload, dep_rows, permit_rows, today):
    projects = payload.get("projects", [])
    # Compared against PA rows only. A national registry shares plenty of
    # tokens and township names across states — "Center Township" and "Meta"
    # both recur — and a cross-state pair is never the same campus.
    hand = [p for p in projects
            if p.get("origin") != ORIGIN and p.get("state") == "PA"]
    mine = {p.get("pa_dep_id"): p for p in projects if p.get("origin") == ORIGIN}
    taken = {p.get("id") for p in projects}

    by_project = {}
    for p in permit_rows:
        by_project.setdefault(_clean(p.get("ProjectID")), []).append(p)

    added, updated, skipped, review = [], [], [], []

    for row in dep_rows:
        dep_id = _clean(row.get("ProjectID"))
        permits = by_project.get(dep_id, [])
        prior = mine.get(dep_id)

        if prior is None:
            clash = find_collision(row, hand)
            if clash is not None:
                skipped.append((row, clash))
                continue
            rec = to_record(row, permits, today)
            while rec["id"] in taken:                 # slug collisions are real
                rec["id"] = f"{rec['id']}-{dep_id[-2:]}"
            taken.add(rec["id"])
            projects.append(rec)
            added.append(rec)
            near = same_township(row, hand)
            if near:
                review.append((rec, near))
            continue

        # Refresh a row we own. Status, note and as_of are re-derived; events
        # are unioned so a hand-added hearing or vote survives the sync.
        fresh = to_record(row, permits, today, existing_id=prior["id"])
        fresh["events"] = merge_events(prior.get("events", []), fresh["events"])
        changed = any(prior.get(k) != fresh.get(k)
                      for k in fresh if k not in ("as_of", "events"))
        changed = changed or len(fresh["events"]) != len(prior.get("events", []))
        prior.update(fresh)
        if changed:
            updated.append(fresh)

    return added, updated, skipped, review


# --------------------------------------------------------------------------- #
# report
# --------------------------------------------------------------------------- #

def render_report(added, updated, skipped, review, dep_rows, permit_rows, today):
    L = [f"# PA DEP data-center tracker sync — {today}", "",
         f"Source: {TRACKER_URL}", "",
         f"- DEP projects on file: **{len(dep_rows)}**",
         f"- DEP permit records: **{len(permit_rows)}**",
         f"- Added to projects.json: **{len(added)}**",
         f"- Refreshed: **{len(updated)}**",
         f"- Skipped (already tracked by hand): **{len(skipped)}**", ""]

    if skipped:
        L += ["## Skipped — hand-written row already covers this", "",
              "Left alone on purpose. If the DEP row carries detail ours "
              "lacks (a permit trail, exact coordinates), fold it in by hand.", ""]
        for row, clash in skipped:
            L.append(f"- DEP {_clean(row.get('ProjectID'))} "
                     f"*{_clean(row.get('ProjectName'))}* "
                     f"({locality_of(row)}) → `{clash.get('id')}`")
        L.append("")

    if review:
        L += ["## Added, but worth a second look", "",
              "These sit in the same municipality as a project we already "
              "track under a different name. Usually a genuinely separate "
              "campus — Archbald Borough has five — but this is where a "
              "duplicate would hide.", ""]
        for rec, near in review:
            names = ", ".join(f"`{h.get('id')}`" for h in near)
            L.append(f"- `{rec['id']}` ({rec['locality']}) vs {names}")
        L.append("")

    if added:
        L += ["## Added", ""]
        for rec in added:
            ev = len(rec["events"])
            L.append(f"- `{rec['id']}` — {rec['name']}"
                     + (f" ({rec['operator']})" if rec.get("operator") else "")
                     + f", {rec['locality']}"
                     + (f" — {ev} permit event{'s' if ev != 1 else ''}" if ev else ""))
        L.append("")

    if updated:
        L += ["## Refreshed", ""]
        for rec in updated:
            L.append(f"- `{rec['id']}` — {rec['note']}")
        L.append("")

    return "\n".join(L)


# --------------------------------------------------------------------------- #

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true",
                    help="reuse the cached CSVs in data/external/")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would change, write nothing")
    ap.add_argument("--report", metavar="PATH",
                    help="write the markdown sync report here")
    ap.add_argument("--today", metavar="ISO",
                    help="override the as_of date (testing)")
    args = ap.parse_args(argv)

    today = args.today or dt.date.today().isoformat()
    try:
        dep_rows, permit_rows = load_csvs(offline=args.offline,
                                          cache=not args.dry_run)
    except Exception as exc:                          # noqa: BLE001
        print(f"PA DEP fetch failed: {exc}", file=sys.stderr)
        return 1

    payload = json.loads(PROJECTS_PATH.read_text(encoding="utf-8"))
    added, updated, skipped, review = merge(payload, dep_rows, permit_rows, today)

    report = render_report(added, updated, skipped, review,
                           dep_rows, permit_rows, today)
    print(report)
    if args.report and not args.dry_run:
        Path(args.report).write_text(report + "\n", encoding="utf-8")

    if args.dry_run:
        print("\n(dry run — projects.json untouched)")
        return 0

    if added or updated:
        payload["generated"] = today
        PROJECTS_PATH.write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
