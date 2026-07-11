import requests
import pandas as pd
import streamlit as st
from src.constants import EIA_BASE, EIA_EMISSION_FACTORS, EIA_RESPONDENTS, DEFAULT_FACTOR, EIA_DEMAND_BASE

@st.cache_data(ttl=3600, show_spinner=False)
def eia930_fuelmix_co2(api_key: str, date_str: str, respondent: str):
    """EIA-930 hourly net generation by fuel type -> 24 hourly AVERAGE gCO2/kWh,
    weighting EIA_EMISSION_FACTORS by generation. date_str is 'YYYY-MM-DD' in the
    BA's local clock. Average, not marginal. Returns a 24-slot list or None."""
    tz = EIA_RESPONDENTS.get(respondent, (respondent, "UTC"))[1]
    # Query a UTC window wide enough to cover the local day, then filter by
    # local calendar date so partial-day edge hours don't skew the average.
    start = (pd.Timestamp(date_str, tz=tz) - pd.Timedelta(hours=1)).tz_convert("UTC")
    end = start + pd.Timedelta(hours=27)
    params = {
        "api_key": api_key,
        "frequency": "hourly",
        "data[0]": "value",
        "facets[respondent][]": respondent,
        "start": start.strftime("%Y-%m-%dT%H"),
        "end": end.strftime("%Y-%m-%dT%H"),
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "length": 5000,
    }
    r = requests.get(EIA_BASE, params=params, timeout=20)
    r.raise_for_status()
    js = r.json()
    if js.get("response", {}).get("errors"):
        raise RuntimeError(js["response"]["errors"])
    rows = js.get("response", {}).get("data", [])
    df = pd.DataFrame(rows)
    if df.empty:
        return None
    # EIA periods are UTC (naive "YYYY-MM-DDTHH"); localize then convert.
    ts = pd.to_datetime(df["period"], utc=True).dt.tz_convert(tz)
    df["mwh"] = pd.to_numeric(df["value"], errors="coerce").clip(lower=0)
    df["ef"] = df["fueltype"].map(EIA_EMISSION_FACTORS).fillna(DEFAULT_FACTOR)
    df = df[ts.dt.strftime("%Y-%m-%d") == date_str]
    hour = ts[df.index].dt.hour
    if df.empty:
        return None

    def _wavg(g):
        tot = g["mwh"].sum()
        return (g["mwh"] * g["ef"]).sum() / tot if tot else float("nan")

    hourly = df.groupby(hour).apply(_wavg)
    return [round(float(hourly[h]), 1) if h in hourly.index else None for h in range(24)]


@st.cache_data(ttl=1800, show_spinner=False)
def eia_latest_demand(api_key: str, respondent: str):
    """Latest hourly system demand (MW) for a balancing authority via EIA-930
    region-data (type 'D'). Returns (mw, period_str) or None. Grid-scale total
    load, not data-center-only — context for 'how much power'."""
    params = {
        "api_key": api_key, "frequency": "hourly", "data[0]": "value",
        "facets[respondent][]": respondent, "facets[type][]": "D",
        "sort[0][column]": "period", "sort[0][direction]": "desc", "length": 1,
    }
    r = requests.get(EIA_DEMAND_BASE, params=params, timeout=20)
    r.raise_for_status()
    rows = r.json().get("response", {}).get("data", [])
    if not rows:
        return None
    return float(rows[0]["value"]), rows[0]["period"]
