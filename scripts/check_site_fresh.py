#!/usr/bin/env python3
"""Catch committed web/ drifting out of sync with the data that generates it.

web/ is committed output served by Vercel as-is, so a commit that edits
constants.py without running build_site.py ships a site that disagrees with
its own data. This is not hypothetical: ef0e369 merged 10 duplicated
moratorium rows and did not rebuild, so aigridwatch.com kept publishing the
duplicates — Ohio read 16 moratoriums where the data said 14, plus a state
page linking a community page for a locality that no longer existed. A
resident citing that page at a hearing is citing a number the project's own
data contradicts.

The daily cron in build-site.yml does heal this within 24h, silently. What it
cannot do is stop the wrong numbers going live in the first place, because CI
deliberately does not run on push (every push-triggered rebuild committed
web/, and that commit triggered its own Vercel deploy — two deploys per source
change). So the only moment a guard helps is before the push, on the
committer's machine.

Why this can be a hard gate when the other verify_* scripts can't: those check
the live web, where a 403 is a bot refusal rather than a broken link, so they
report and leave the judgement to a human. This one compares generated output
against its own inputs. There is no ambiguity to defer — either the build
reproduces what is committed or it doesn't.

Determinism is what makes that true, and it needs NEWS_FREEZE=1. News and
YouTube are fetched at build time, so once the 6h cache TTL lapses a rebuild
rewrites ~35 files regardless of the data. Freezing both to the committed
cache leaves registry changes as the only thing that can move web/.

Usage:
    python3 scripts/check_site_fresh.py             # report
    python3 scripts/check_site_fresh.py --strict    # exit 1 on drift
    python3 scripts/check_site_fresh.py --fix       # keep the rebuild

Install as a pre-push hook:
    printf '#!/bin/sh\\nexec python3 scripts/check_site_fresh.py --strict\\n' \\
      > .git/hooks/pre-push && chmod +x .git/hooks/pre-push

Stdlib only, so CI installs nothing beyond what the build already needs.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Only these are compared. data/ is excluded on purpose: the scanners append
# to their review queues on every run, so it is expected to move when web/
# does not.
TRACKED = ["web/"]

# The build also writes these. They are not drift signals, but leaving them
# modified after a run that advertises itself as read-only is its own small
# betrayal — so they get restored too, and only when this run is what dirtied
# them. Anything already modified beforehand is somebody else's work.
ALSO_WRITTEN = [
    "data/sitemap_hashes.json",
    "data/story_candidates.json",
    "data/news_cache.json",
    "data/youtube_cache.json",
    "data/video_candidates.json",
]


def _git(*args):
    """Run git in the repo root, returning stdout. Raises on failure."""
    out = subprocess.run(["git", "-C", str(ROOT), *args],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout


def _dirty(paths=None):
    """Return porcelain status lines, one per changed path."""
    return [ln for ln in _git("status", "--porcelain", "--",
                              *(paths or TRACKED)).splitlines() if ln.strip()]


def _paths(lines):
    return {ln[3:].strip().strip('"') for ln in lines}


def _restore(before_untracked, incidental):
    """Put web/ back as it was: revert tracked edits, delete files the build
    added. Only paths git reports as untracked *now* and not before are
    removed — never a blanket `git clean`, which would take real work with it.

    `incidental` is the subset of ALSO_WRITTEN that this run dirtied; those are
    reverted too. Files already modified when we started are left alone.
    """
    _git("checkout", "--", *TRACKED)
    for ln in _dirty():
        if ln.startswith("??"):
            path = ln[3:].strip().strip('"')
            if path not in before_untracked:
                target = ROOT / path
                if target.is_file():
                    target.unlink()
    if incidental:
        _git("checkout", "--", *sorted(incidental))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when web/ is out of date")
    ap.add_argument("--fix", action="store_true",
                    help="leave the rebuilt web/ in place instead of restoring")
    args = ap.parse_args()

    # A rebuild would bury uncommitted work in web/, and the restore below
    # would then revert it. Refuse rather than guess which lines were theirs.
    pre_existing = _dirty()
    if pre_existing and not args.fix:
        print("web/ has uncommitted changes — commit or stash them first, "
              "or pass --fix to rebuild over them.")
        for ln in pre_existing[:10]:
            print(f"  {ln}")
        if len(pre_existing) > 10:
            print(f"  … and {len(pre_existing) - 10} more")
        return 2
    before_untracked = _paths([ln for ln in pre_existing if ln.startswith("??")])
    dirty_before = _paths(_dirty(ALSO_WRITTEN))

    env = dict(os.environ, NEWS_FREEZE="1")
    build = subprocess.run([sys.executable, "build_site.py"],
                           cwd=str(ROOT), env=env,
                           capture_output=True, text=True)
    if build.returncode != 0:
        print("build_site.py failed — that is the finding; drift is unknown.")
        print(build.stderr.strip()[-2000:])
        return 1

    incidental = _paths(_dirty(ALSO_WRITTEN)) - dirty_before
    drift = _dirty()
    if not drift:
        if incidental:
            _git("checkout", "--", *sorted(incidental))
        print("web/ is up to date with the data that generates it.")
        return 0

    print(f"web/ is stale — rebuilding changed {len(drift)} file(s):")
    for ln in drift[:20]:
        print(f"  {ln}")
    if len(drift) > 20:
        print(f"  … and {len(drift) - 20} more")

    if args.fix:
        print("\nRebuilt output left in place. Commit web/ with your data change.")
    else:
        _restore(before_untracked, incidental)
        print("\nweb/ restored. Run with --fix (or `python3 build_site.py`) "
              "and commit the result alongside the data change.")

    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
