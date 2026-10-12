#!/usr/bin/env python3
"""Print the live headline counts used in outreach copy, README and docs.

Stdlib + the repo's own constants. Run it, then paste the numbers; never
type a count into outreach copy from memory (the docs said "99 moratoriums"
long after the registry passed 800).

    python3 scripts/outreach_counts.py          # human-readable
    python3 scripts/outreach_counts.py --json   # machine-readable
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.constants import MORATORIUMS_DF, PROJECTS_DF  # noqa: E402


def counts():
    mor = MORATORIUMS_DF
    states = {s for s in mor["state"] if len(str(s)) == 2}
    house = json.loads((ROOT / "data" / "house_races_2026.json").read_text())
    comm = len(list((ROOT / "web" / "communities").glob("*.html"))) - 1 \
        if (ROOT / "web" / "communities").exists() else None
    return {
        "moratoriums": len(mor),
        "moratorium_states": len(states),
        "projects": len(PROJECTS_DF),
        "project_states": int(PROJECTS_DF["state"].nunique()),
        "house_districts": len(house.get("districts", [])),
        "community_pages": comm,
    }


if __name__ == "__main__":
    c = counts()
    if "--json" in sys.argv:
        print(json.dumps(c, indent=2))
    else:
        for k, v in c.items():
            print(f"{k:18} {v}")
