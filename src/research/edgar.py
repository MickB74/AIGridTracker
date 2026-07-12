"""SEC EDGAR client for facilities research.

No API key required. SEC only asks for a descriptive User-Agent with contact
info (https://www.sec.gov/os/webmaster-faq#developers) and rate-limits to
~10 req/s — we stay well under that. Every network call fails soft (returns
empty / None) so a CLI run never hard-crashes on one bad request.

Endpoints used:
  - company_tickers.json          ticker/name  -> CIK
  - data.sec.gov/submissions/...  CIK          -> recent filings index
  - efts.sec.gov/LATEST/search-index  full-text search across filing bodies
  - www.sec.gov/Archives/...      accession    -> the actual filing document
"""
from __future__ import annotations

import re
import time
import requests

# SEC wants "Company/App contact@email" so they can reach you if a script
# misbehaves. Override via the CLI --contact flag.
DEFAULT_UA = "AIGridTracker facilities-research (mickeybarry@gmail.com)"

_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik10}.json"
_FTS_URL = "https://efts.sec.gov/LATEST/search-index"
_ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc_nodash}/{doc}"

# Be polite: minimum gap between requests to SEC hosts (seconds).
_MIN_GAP = 0.15
_last_call = [0.0]


def _get(url: str, ua: str, *, params=None, timeout=20):
    """Rate-limited GET with SEC-friendly headers. Returns a Response or None."""
    gap = _MIN_GAP - (time.monotonic() - _last_call[0])
    if gap > 0:
        time.sleep(gap)
    try:
        r = requests.get(
            url, params=params, timeout=timeout,
            headers={"User-Agent": ua, "Accept-Encoding": "gzip, deflate"})
        _last_call[0] = time.monotonic()
        r.raise_for_status()
        return r
    except Exception:                                             # noqa: BLE001
        _last_call[0] = time.monotonic()
        return None


def resolve_cik(query: str, ua: str = DEFAULT_UA):
    """Map a ticker or company name to (cik:int, title:str, ticker:str).

    Ticker match is exact (case-insensitive); name match is substring. Returns
    None if nothing matches or the lookup fails.
    """
    r = _get(_TICKERS_URL, ua)
    if r is None:
        return None
    try:
        data = r.json()
    except ValueError:
        return None
    q = query.strip().lower()
    rows = list(data.values()) if isinstance(data, dict) else data
    # exact ticker first, then substring on company title
    for row in rows:
        if str(row.get("ticker", "")).lower() == q:
            return int(row["cik_str"]), row.get("title", ""), row.get("ticker", "")
    for row in rows:
        if q in str(row.get("title", "")).lower():
            return int(row["cik_str"]), row.get("title", ""), row.get("ticker", "")
    return None


def recent_filings(cik: int, ua: str = DEFAULT_UA, *, forms=("10-K", "8-K"),
                   limit: int = 10):
    """Return recent filings for a CIK as a list of dicts:
    {form, filing_date, accession, primary_doc, primary_doc_url, description}.
    Only forms in `forms` are kept, newest first.
    """
    cik10 = f"{cik:010d}"
    r = _get(_SUBMISSIONS_URL.format(cik10=cik10), ua)
    if r is None:
        return []
    try:
        recent = r.json().get("filings", {}).get("recent", {})
    except ValueError:
        return []
    forms_u = {f.upper() for f in forms}
    out = []
    accs = recent.get("accessionNumber", [])
    for i in range(len(accs)):
        form = recent.get("form", [""] * len(accs))[i]
        if forms_u and form.upper() not in forms_u:
            continue
        acc = accs[i]
        acc_nodash = acc.replace("-", "")
        doc = recent.get("primaryDocument", [""] * len(accs))[i]
        out.append({
            "form": form,
            "filing_date": recent.get("filingDate", [""] * len(accs))[i],
            "accession": acc,
            "primary_doc": doc,
            "primary_doc_url": _ARCHIVE_URL.format(
                cik=cik, acc_nodash=acc_nodash, doc=doc) if doc else "",
            "description": recent.get("primaryDocDescription",
                                      [""] * len(accs))[i],
        })
        if len(out) >= limit:
            break
    return out


def fetch_document_text(url: str, ua: str = DEFAULT_UA) -> str:
    """Fetch a filing document and strip it to plain text. Returns '' on failure.
    Uses BeautifulSoup when available, else a crude tag-stripping fallback.
    """
    r = _get(url, ua, timeout=40)
    if r is None:
        return ""
    html = r.text
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text(" ")
    except Exception:                                             # noqa: BLE001
        text = re.sub(r"<[^>]+>", " ", html)
    # collapse whitespace / non-breaking spaces
    return re.sub(r"[\s ]+", " ", text).strip()


def fulltext_search(query: str, ua: str = DEFAULT_UA, *, forms=None,
                    ciks=None, limit: int = 20):
    """EDGAR full-text search (efts) across filing bodies since 2001. Returns a
    list of hit dicts: {accession, form, filing_date, cik, display_names, url}.

    `query` is passed verbatim — wrap phrases in double quotes for exact match.
    `forms` filters by form type; `ciks` restricts to one or more companies.
    """
    params = {"q": query}
    if forms:
        params["forms"] = ",".join(forms) if not isinstance(forms, str) else forms
    if ciks:
        if isinstance(ciks, (list, tuple)):
            params["ciks"] = ",".join(f"{int(c):010d}" for c in ciks)
        else:
            params["ciks"] = f"{int(ciks):010d}"
    r = _get(_FTS_URL, ua, params=params)
    if r is None:
        return []
    try:
        hits = r.json().get("hits", {}).get("hits", [])
    except ValueError:
        return []
    out = []
    for h in hits[:limit]:
        src = h.get("_source", {})
        # _id looks like "0000000000-00-000000:document.htm"
        _id = h.get("_id", "")
        acc, _, doc = _id.partition(":")
        cik = (src.get("ciks") or [""])[0]
        url = ""
        if cik and acc and doc:
            url = _ARCHIVE_URL.format(
                cik=int(cik), acc_nodash=acc.replace("-", ""), doc=doc)
        out.append({
            "accession": acc,
            "form": src.get("root_form") or (src.get("file_type") or ""),
            "filing_date": src.get("file_date", ""),
            "cik": cik,
            "display_names": src.get("display_names", []),
            "url": url,
        })
    return out
