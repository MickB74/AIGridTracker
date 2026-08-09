"""
Regenerate officials.json from authoritative public rosters.

Run this to refresh the Officials directory + scorecard after an election,
appointment, or committee reshuffle. It rebuilds names / party / websites /
committees from source, then re-applies the curated stances from
src/officials_stances.py. Grades come from src/official_grades.py at render
time, so nothing to regenerate there.

    python scripts/refresh_officials.py            # writes officials.json
    python scripts/refresh_officials.py --check    # dry-run, prints a summary

Sources (all public, no key):
  - Senators:  senate.gov official contact XML
  - House:     @unitedstates congress-legislators (websites + contact forms)
  - Governors: Wikipedia "List of current United States governors"
  - Committees: House Clerk MemberData.xml (E&C) + @unitedstates
               committee-membership (Senate Energy & Natural Resources)

After running, rebuild the site (build_site.py) so web/scorecard.html updates.
"""

import csv
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))          # so `src` imports work from anywhere

from src.officials_stances import stance_for  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 Chrome/120 Safari/537.36"}
OUT = ROOT / "officials.json"

ST = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
      "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
      "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
      "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
      "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
      "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
      "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
      "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
      "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
      "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
      "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
      "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
      "WI": "Wisconsin", "WY": "Wyoming", "AS": "American Samoa",
      "DC": "District of Columbia", "GU": "Guam", "MP": "N. Mariana Islands",
      "PR": "Puerto Rico", "VI": "U.S. Virgin Islands"}
TERR = {"AS", "DC", "GU", "MP", "PR", "VI"}
GOVURL = {
    "Alabama": "https://governor.alabama.gov", "Alaska": "https://gov.alaska.gov",
    "Arizona": "https://azgovernor.gov", "Arkansas": "https://governor.arkansas.gov",
    "California": "https://www.gov.ca.gov", "Colorado": "https://governor.colorado.gov",
    "Connecticut": "https://portal.ct.gov/governor", "Delaware": "https://governor.delaware.gov",
    "Florida": "https://www.flgov.com", "Georgia": "https://gov.georgia.gov",
    "Hawaii": "https://governor.hawaii.gov", "Idaho": "https://gov.idaho.gov",
    "Illinois": "https://gov.illinois.gov", "Indiana": "https://www.in.gov/gov",
    "Iowa": "https://governor.iowa.gov", "Kansas": "https://governor.kansas.gov",
    "Kentucky": "https://governor.ky.gov", "Louisiana": "https://gov.louisiana.gov",
    "Maine": "https://www.maine.gov/governor", "Maryland": "https://governor.maryland.gov",
    "Massachusetts": "https://www.mass.gov/orgs/office-of-the-governor",
    "Michigan": "https://www.michigan.gov/whitmer", "Minnesota": "https://mn.gov/governor",
    "Mississippi": "https://governorreeves.ms.gov", "Missouri": "https://governor.mo.gov",
    "Montana": "https://governor.mt.gov", "Nebraska": "https://governor.nebraska.gov",
    "Nevada": "https://gov.nv.gov", "New Hampshire": "https://www.governor.nh.gov",
    "New Jersey": "https://www.nj.gov/governor", "New Mexico": "https://www.governor.state.nm.us",
    "New York": "https://www.governor.ny.gov", "North Carolina": "https://governor.nc.gov",
    "North Dakota": "https://www.governor.nd.gov", "Ohio": "https://governor.ohio.gov",
    "Oklahoma": "https://oklahoma.gov/governor", "Oregon": "https://www.oregon.gov/gov",
    "Pennsylvania": "https://www.governor.pa.gov", "Rhode Island": "https://governor.ri.gov",
    "South Carolina": "https://governor.sc.gov", "South Dakota": "https://governor.sd.gov",
    "Tennessee": "https://www.tn.gov/governor", "Texas": "https://gov.texas.gov",
    "Utah": "https://governor.utah.gov", "Vermont": "https://governor.vermont.gov",
    "Virginia": "https://www.governor.virginia.gov", "Washington": "https://www.governor.wa.gov",
    "West Virginia": "https://governor.wv.gov", "Wisconsin": "https://evers.wi.gov",
    "Wyoming": "https://governor.wyo.gov"}
PARTY = {"D": "Democratic", "R": "Republican", "I": "Independent", "ID": "Independent"}


def _get(url):
    r = requests.get(url, headers=UA, timeout=30)
    r.raise_for_status()
    return r


def senators():
    root = ET.fromstring(_get(
        "https://www.senate.gov/general/contact_information/senators_cfm.xml").content)
    out = []
    for m in root.findall(".//member"):
        g = lambda t: (m.findtext(t) or "").strip()
        site = g("website")
        out.append({"office": "Senator", "state": g("state"),
                    "name": f"{g('first_name')} {g('last_name')}".strip(),
                    "party": PARTY.get(g("party"), g("party")),
                    "website": site, "contact": site.rstrip("/") + "/contact",
                    "district": "", "committee": ""})
    return out


def reps():
    rows = list(csv.DictReader(io.StringIO(_get(
        "https://unitedstates.github.io/congress-legislators/legislators-current.csv").text)))
    # Committees: House E&C (Clerk XML, IF00), Senate ENR (@unitedstates SSEG)
    clerk = ET.fromstring(_get("https://clerk.house.gov/xml/lists/MemberData.xml").content)
    ec = {m.findtext(".//bioguideID") for m in clerk.findall(".//member")
          if any(c.get("comcode") == "IF00"
                 for c in m.findall(".//committee-assignments/committee"))}
    mem = _get("https://unitedstates.github.io/congress-legislators/"
               "committee-membership-current.json").json()
    enr = {x["bioguide"] for x in mem.get("SSEG", [])}
    out = []
    for x in rows:
        if x["type"] != "rep":
            continue
        stt, dist = x["state"], x.get("district", "").strip()
        out.append({
            "office": "Delegate" if stt in TERR else "Representative",
            "state": stt, "name": x.get("full_name") or f"{x['first_name']} {x['last_name']}",
            "party": x.get("party", ""), "district": "At-Large" if dist in ("", "0") else dist,
            "website": x.get("url", ""), "contact": x.get("contact_form") or x.get("url", ""),
            "committee": "Energy & Commerce" if x["bioguide_id"] in ec else ""})
    return out, ec, enr, rows


def apply_senate_committees(sens, enr_bio, all_rows):
    key = {(r["last_name"].lower(), r["state"]) for r in all_rows
           if r["type"] == "sen" and r["bioguide_id"] in enr_bio}
    for s in sens:
        if any(ln in s["name"].lower() and s["state"] == st for ln, st in key):
            s["committee"] = "Energy & Natural Resources"


def governors():
    import pandas as pd
    html = _get("https://en.wikipedia.org/wiki/"
                "List_of_current_United_States_governors").text
    tbl = [t for t in pd.read_html(io.StringIO(html))
           if t.shape[0] == 50 and any("Governor" in str(c) for c in t.columns)][0]
    tbl.columns = [str(c) for c in tbl.columns]
    sc = [c for c in tbl.columns if c.startswith("State")][0]
    gc = [c for c in tbl.columns if c.startswith("Governor")][0]
    pc = [c for c in tbl.columns if "Party" in c
          and tbl[c].astype(str).str.contains("Republican|Democratic").any()][0]
    clean = lambda s: re.sub(r"\[.*?\]|\(list\)", "", str(s)).strip()
    full2st = {v: k for k, v in ST.items()}
    out = []
    for _, row in tbl.iterrows():
        state = clean(row[sc])                 # full name, e.g. "Georgia"
        out.append({"office": "Governor", "state": full2st.get(state, state),
                    "name": clean(row[gc]), "party": clean(row[pc]),
                    "website": GOVURL.get(state, ""), "contact": GOVURL.get(state, ""),
                    "district": "", "committee": ""})
    return out


def main(check=False):
    sens = senators()
    house, ec, enr, rows = reps()
    apply_senate_committees(sens, enr, rows)
    govs = governors()
    officials = sens + house + govs
    for r in officials:
        r["state_full"] = ST.get(r["state"], r["state"])
        r["stance"], r["stance_src"] = stance_for(r["office"], r["state"], r["name"])
    payload = {"generated": "regenerated by scripts/refresh_officials.py "
                            "(Senate XML + congress-legislators + current governors)",
               "officials": officials}
    n_stance = sum(1 for r in officials if r["stance"])
    print(f"senators={len(sens)} house={len(house)} governors={len(govs)} "
          f"total={len(officials)} | E&C={len(ec)} ENR={sum(1 for s in sens if s['committee']=='Energy & Natural Resources')} "
          f"| stances={n_stance}")
    if check:
        print("--check: not writing.")
        return
    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main(check="--check" in sys.argv)
