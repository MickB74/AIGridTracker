#!/usr/bin/env python3
"""Tell IndexNow which pages changed in the latest build.

IndexNow is the push half of Bing indexing (Yandex, Naver and Seznam share
the endpoint, and Bing is what ChatGPT's browsing reads). Instead of waiting
for a crawl to notice a changed sitemap, this submits the URLs whose sitemap
``lastmod`` moved between the committed ``data/sitemap_hashes.json`` at a git
ref (default ``HEAD~1``) and the working copy — i.e. exactly the pages the
build just changed. Runs in ``build-site.yml`` after the rebuild is pushed,
so Bing fetches the deployed page, not the previous one.

No account is needed: ownership is proven by ``/<key>.txt`` on the host,
which ``build_site.py`` writes from ``INDEXNOW_KEY``. Stdlib-only, like every
script here, so it runs off ``requirements-build.txt``.

Usage:
    python3 scripts/indexnow_ping.py            # diff HEAD~1 vs working copy
    python3 scripts/indexnow_ping.py --since HEAD~3
    python3 scripts/indexnow_ping.py --dry-run  # print the URL list, no POST
    python3 scripts/indexnow_ping.py --all      # resubmit every sitemap URL
                                                # (first run, or after a
                                                # domain-wide change)

Exit status is 0 unless the endpoint refuses the key (4xx). A network
failure is reported and exits 0: IndexNow is a hint, and the daily sitemap
crawl still happens without it.
"""
import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ENDPOINT = "https://api.indexnow.org/indexnow"
BATCH = 10_000          # protocol maximum per POST


def _site_and_key():
    import importlib.util
    # build_site.py is heavy to import (it builds nothing at import, but pulls
    # every registry). We only need two constants, so read them the same way
    # the module does: env first, then the literal default.
    import os
    import re
    src = (ROOT / "build_site.py").read_text(encoding="utf-8")
    def const(name):
        env = os.environ.get(name)
        if env:
            return env
        m = re.search(rf'^{name} = os\.environ\.get\("{name}", "([^"]+)"\)',
                      src, re.M)
        return m.group(1) if m else None
    return const("SITE_URL"), const("INDEXNOW_KEY")


def _hashes_at(ref):
    try:
        out = subprocess.check_output(
            ["git", "show", f"{ref}:data/sitemap_hashes.json"],
            cwd=ROOT, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return {}
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {}


def changed_paths(since):
    now = json.loads((ROOT / "data" / "sitemap_hashes.json").read_text())
    before = _hashes_at(since)
    out = []
    for p, cur in sorted(now.items()):
        prev = before.get(p)
        if not prev or prev.get("lastmod") != cur.get("lastmod"):
            out.append(p)
    return out


def to_url(site, p):
    return f"{site}/{p}" if p else f"{site}/"


def submit(site, key, urls):
    host = site.split("://", 1)[1].rstrip("/")
    payload = {"host": host, "key": key,
               "keyLocation": f"{site}/{key}.txt", "urlList": urls}
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8",
                 "User-Agent": "aigridwatch-indexnow/1.0"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--since", default="HEAD~1",
                    help="git ref whose sitemap_hashes.json is the baseline")
    ap.add_argument("--all", action="store_true",
                    help="submit every sitemap URL, ignoring the diff")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    site, key = _site_and_key()
    if not site or not key:
        print("SITE_URL / INDEXNOW_KEY not found", file=sys.stderr)
        return 2
    if a.all:
        paths = sorted(json.loads(
            (ROOT / "data" / "sitemap_hashes.json").read_text()))
    else:
        paths = changed_paths(a.since)
    urls = [to_url(site, p) for p in paths]
    print(f"{len(urls)} URL(s) changed since {a.since if not a.all else 'ever'}")
    for u in urls[:40]:
        print("  " + u)
    if len(urls) > 40:
        print(f"  … +{len(urls) - 40} more")
    if not urls or a.dry_run:
        return 0
    rc = 0
    for i in range(0, len(urls), BATCH):
        chunk = urls[i:i + BATCH]
        for attempt in (1, 2):
            try:
                status = submit(site, key, chunk)
                print(f"IndexNow accepted {len(chunk)} URL(s): HTTP {status}")
                break
            except urllib.error.HTTPError as e:
                print(f"IndexNow refused: HTTP {e.code} {e.reason}",
                      file=sys.stderr)
                # 403 = "key not valid", which on a site that just deployed
                # usually means the endpoint fetched /<key>.txt before the
                # new deploy was serving. Seen on 2026-09-05: the same
                # request succeeded on retry. One wait, one retry.
                if e.code == 403 and attempt == 1:
                    time.sleep(60)
                    continue
                if 400 <= e.code < 500:
                    rc = 1    # bad key or malformed request: worth a red X
                break
            except (urllib.error.URLError, TimeoutError) as e:
                print(f"IndexNow unreachable: {e}", file=sys.stderr)
                break
    return rc


if __name__ == "__main__":
    sys.exit(main())
