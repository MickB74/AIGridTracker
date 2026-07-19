"""
Live market-data service — fetches current stock prices from Yahoo Finance's
keyless chart endpoint. Used to refresh the Corporate Profiles financial cards
(stock price, and market cap when combined with shares outstanding).

The quote/quoteSummary endpoints now require a crumb, so we use the public
`chart` endpoint which returns regularMarketPrice without authentication.
Cached 1 hour; fails gracefully (returns {}) so the tab falls back to static
values when offline or rate-limited.
"""

import time

import requests
import streamlit as st

_UA = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    )
}


@st.cache_data(ttl=3600)  # 1 hour — prices are delayed and this is a scale indicator
def fetch_live_quotes(tickers: tuple[str, ...]) -> dict[str, dict]:
    """
    Fetch latest price for each ticker from Yahoo Finance's chart endpoint.

    Returns {ticker: {"price": float, "prev_close": float, "time": int}} for
    every ticker that resolved; missing/failed tickers are simply omitted.
    Returns {} on total failure. Takes a tuple (hashable) so @st.cache_data
    can key on it.
    """
    out: dict[str, dict] = {}
    session = requests.Session()
    session.headers.update(_UA)
    for i, ticker in enumerate(tickers):
        if i:
            time.sleep(0.25)  # be polite; avoid burst throttling
        # Up to 2 tries: Yahoo returns 429 on bursts, usually clears on a short wait.
        for attempt in range(2):
            try:
                r = session.get(
                    f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}",
                    params={"interval": "1d", "range": "1d"},
                    timeout=10,
                )
                if r.status_code == 429 and attempt == 0:
                    time.sleep(1.0)
                    continue
                if r.status_code != 200:
                    break
                meta = r.json()["chart"]["result"][0]["meta"]
                price = meta.get("regularMarketPrice")
                if price is None:
                    break
                out[ticker] = {
                    "price": float(price),
                    "prev_close": meta.get("chartPreviousClose") or meta.get("previousClose"),
                    "time": meta.get("regularMarketTime"),
                }
                break
            except Exception:
                break
    return out
