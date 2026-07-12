"""
SEC EDGAR XBRL service — fetches and parses dynamic financial statements
(Net Income, Capital Expenditures, and Total Assets) directly from the SEC Company Facts API.
Caches requests for 24 hours to stay within SEC rate limits and ensure fast load times.
"""

import requests
import streamlit as st
import time

# SEC EDGAR user agent contact info (required by SEC Webmaster Guidelines)
SEC_UA = "AIGridTracker financial-fetcher (mickeybarry@gmail.com)"

# Map public tickers to CIK numbers
CIK_MAPPING = {
    "MSFT": "0000789019",
    "GOOGL": "0001652044",
    "NVDA": "0001045810",
    "AMZN": "0001018724",
    "META": "0001326801",
    "AMD": "0000002488",
    "VRT": "0001674101",
    "CEG": "0001868275",
    "SMCI": "0001375365",
    "ORCL": "0001341439",
    "EQIX": "0001101239",
    "DLR": "0001297996"
}

# Candidate us-gaap tags for CapEx (ordered by suitability)
CAPEX_TAGS = [
    "PaymentsToAcquirePropertyPlantAndEquipment",
    "PaymentsToAcquireProductiveAssets",          # Amazon style
    "PaymentsToDevelopRealEstateAssets",          # REIT (Digital Realty style)
    "PaymentsToAcquireRealEstateHeldForInvestment", # REIT alternative
    "PaymentsToAcquireRealEstate",                 # REIT alternative
    "PaymentsToAcquireOtherPropertyPlantAndEquipment"
]

@st.cache_data(ttl=86400) # Cache for 24 hours
def get_sec_company_facts(cik: str) -> dict | None:
    """Fetch raw facts from the SEC EDGAR Company Facts API."""
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json"
    headers = {
        "User-Agent": SEC_UA,
        "Accept-Encoding": "gzip, deflate"
    }
    try:
        # Be polite: rate limit wait
        time.sleep(0.15)
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

def fetch_dynamic_financials(ticker: str) -> dict | None:
    """
    Fetch and parse the latest Annual (10-K/FY) metrics from the SEC.
    Returns: {
        "Net Income": str,
        "Capital Budget (Annual CapEx)": str,
        "Total Assets": str
    } or None if private / request fails.
    """
    cik = CIK_MAPPING.get(ticker)
    if not cik:
        return None # Private company

    raw_data = get_sec_company_facts(cik)
    if not raw_data:
        return None

    us_gaap = raw_data.get("facts", {}).get("us-gaap", {})
    if not us_gaap:
        return None

    out = {}

    # 1. Net Income
    net_income_data = us_gaap.get("NetIncomeLoss", {}).get("units", {}).get("USD", [])
    if net_income_data:
        fy_entries = [e for e in net_income_data if e.get("form") == "10-K" or e.get("fp") == "FY"]
        if fy_entries:
            latest = max(fy_entries, key=lambda x: (x.get("fy", 0), x.get("filed", "")))
            out["Net Income"] = f"${latest.get('val') / 1e9:.2f} Billion (FY{latest.get('fy')})"

    # 2. Capital Expenditures (CapEx)
    for tag in CAPEX_TAGS:
        capex_data = us_gaap.get(tag, {}).get("units", {}).get("USD", [])
        if capex_data:
            fy_entries = [e for e in capex_data if e.get("form") == "10-K" or e.get("fp") == "FY"]
            if fy_entries:
                latest = max(fy_entries, key=lambda x: (x.get("fy", 0), x.get("filed", "")))
                # Only trust recent entries to avoid ancient defaults
                if latest.get("fy", 0) >= 2023:
                    out["Capital Budget (Annual CapEx)"] = f"${latest.get('val') / 1e9:.2f} Billion (FY{latest.get('fy')})"
                    break

    # 3. Total Assets
    assets_data = us_gaap.get("Assets", {}).get("units", {}).get("USD", [])
    if assets_data:
        fy_entries = [e for e in assets_data if e.get("form") == "10-K"]
        if fy_entries:
            latest = max(fy_entries, key=lambda x: (x.get("fy", 0), x.get("filed", "")))
            out["Total Assets"] = f"${latest.get('val') / 1e9:.2f} Billion (FY{latest.get('fy')})"

    # Only return if we parsed at least one field successfully
    return out if out else None
