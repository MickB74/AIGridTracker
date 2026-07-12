"""First-party data-center location pages.

Hyperscalers publish their own site lists — the same pages you hand-curate into
HYPERSCALERS today. This module fetches a page and pulls "City, ST" candidates
out of it with the shared text extractor. Some of these pages are JavaScript-
rendered, so a plain fetch may return little; the CLI reports the hit count so
you can tell when a page needs a browser render instead (fall back to the
claude-in-chrome MCP or paste the rendered HTML in with --html-file).

`FIRST_PARTY_PAGES` is a starting registry — URLs drift, so treat a zero-hit
result as "page moved / JS-only", not "no data centers".
"""
from __future__ import annotations

import requests
from .extract import locations_from_text

FIRST_PARTY_PAGES = {
    "Google":        "https://www.google.com/about/datacenters/locations/",
    "Meta":          "https://datacenters.atmeta.com/",
    "Microsoft":     "https://local.microsoft.com/communities/",
    "Amazon (AWS)":  "https://aws.amazon.com/about-aws/global-infrastructure/",
    "Equinix":       "https://www.equinix.com/data-centers",
    "Digital Realty":"https://www.digitalrealty.com/data-centers",
    "QTS":           "https://www.qtsdatacenters.com/data-centers",
    "CoreWeave":     "https://www.coreweave.com/data-centers",
}

_UA = "AIGridTracker facilities-research (mickeybarry@gmail.com)"


def fetch_page_text(url: str, ua: str = _UA) -> str:
    """Fetch a URL and reduce it to plain text. Returns '' on failure."""
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": ua})
        r.raise_for_status()
    except Exception:                                             # noqa: BLE001
        return ""
    html = r.text
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for t in soup(["script", "style", "noscript"]):
            t.decompose()
        return soup.get_text(" ")
    except Exception:                                             # noqa: BLE001
        import re
        return re.sub(r"<[^>]+>", " ", html)


def discover(company: str, *, url: str | None = None, html: str | None = None):
    """Return (candidates, page_url). `candidates` are location dicts from the
    text extractor. Pass `html` to parse already-rendered markup (e.g. from a
    headless browser) instead of doing a live fetch; pass `url` to override the
    registry entry.
    """
    page_url = url or FIRST_PARTY_PAGES.get(company, "")
    if html is not None:
        text = html
        try:
            from bs4 import BeautifulSoup
            text = BeautifulSoup(html, "html.parser").get_text(" ")
        except Exception:                                         # noqa: BLE001
            pass
    else:
        text = fetch_page_text(page_url) if page_url else ""
    return locations_from_text(text, min_count=1), page_url
