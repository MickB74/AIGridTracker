"""Shared HTTP link checking for the data validators.

One copy, because the interesting logic is the *classification*, not the
request: a 403 from a paywalled newsroom or from SEC's bot policy says
nothing about whether the page is still there. Reporting those as dead links
trains the reader to ignore the check, which costs more than the check gains.

Stdlib only — these run in CI off requirements-build.txt, which excludes
requests and streamlit on purpose.
"""

import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

TIMEOUT = 20
UA = ("Mozilla/5.0 (compatible; GridWatchLinkCheck/1.0; "
      "+https://aigridwatch.com)")

# Refusal, not absence. SEC in particular 403s any user-agent that does not
# declare a contact address, so sec.gov links land here by design.
BLOCKED_CODES = {401, 403, 405, 406, 429, 999}


def check_url(url):
    """(status_code_or_None, error_string_or_None).

    HEAD first because it is cheap, then GET: plenty of newsrooms answer HEAD
    with 405 while serving the page fine, and CivicPlus DocumentCenter PDFs
    (Twinsburg's ordinance) answer HEAD with 404 while serving GET — so a
    HEAD 404 is only a dead link once GET agrees.
    """
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method,
                                     headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return r.status, None
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (404, 405, 501):
                continue
            return e.code, None
        except Exception as e:                                # noqa: BLE001
            if method == "HEAD":
                continue
            return None, f"{type(e).__name__}: {e}"
    return None, "unreachable"


def check_many(urls, workers=8):
    """Check urls concurrently, preserving order."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(check_url, urls))


def classify(code, err):
    """'ok' | 'blocked' | 'flaky' | 'dead' for a check_url result.

    5xx is the server having a bad minute, not the page being gone — EIA in
    particular 503s under load. Filing that next to a 404 would send someone
    hunting for a replacement URL that was never broken, so transient server
    errors get their own bucket and never fail a --strict run.
    """
    if err:
        return "dead"
    if code in BLOCKED_CODES:
        return "blocked"
    if code and code >= 500:
        return "flaky"
    if code and code >= 400:
        return "dead"
    return "ok"
