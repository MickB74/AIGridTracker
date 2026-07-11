import requests
import pandas as pd
import streamlit as st
from src.constants import PJM_API_BASE, LB_TO_G, PJM_EMISSION_FACTORS, DEFAULT_FACTOR

def _pjm_get(endpoint: str, api_key: str, fields: str, date_str: str,
             extra: dict | None = None, row_count: int = 50000) -> pd.DataFrame:
    """One Data Miner 2 call for a single EPT day. Returns the items DataFrame."""
    params = {
        "fields": fields, "startRow": 1, "rowCount": row_count,
        "datetime_beginning_ept": f"{date_str} 00:00to{date_str} 23:59",
    }
    if extra:
        params.update(extra)
    r = requests.get(PJM_API_BASE + endpoint, params=params,
                     headers={"Ocp-Apim-Subscription-Key": api_key}, timeout=20)
    r.raise_for_status()
    js = r.json()
    if isinstance(js, dict) and js.get("errors"):
        raise RuntimeError(js["errors"])
    return pd.DataFrame(js.get("items", []) if isinstance(js, dict) else js)


@st.cache_data(ttl=3600, show_spinner=False)
def pjm_marginal_co2(api_key: str, date_str: str, pnode_id: str = ""):
    """Marginal CO2 (lbs/MWh) -> 24 hourly gCO2/kWh from fivemin_marginal_emissions.
    Marginal is the correct signal for load-shifting decisions. If pnode_id is
    blank, averages across all returned pnodes (may be truncated at row_count)."""
    extra = {"pnode_id": pnode_id} if pnode_id else None
    df = _pjm_get("fivemin_marginal_emissions", api_key,
                  "datetime_beginning_ept,pnode_id,pnode_name,marginal_co2_rate",
                  date_str, extra=extra)
    if df.empty:
        return None
    df["ts"] = pd.to_datetime(df["datetime_beginning_ept"])
    df["g_kwh"] = pd.to_numeric(df["marginal_co2_rate"], errors="coerce") * LB_TO_G / 1000.0
    hourly = df.groupby(df["ts"].dt.hour)["g_kwh"].mean()
    return [round(float(hourly[h]), 1) if h in hourly.index else None for h in range(24)]


@st.cache_data(ttl=3600, show_spinner=False)
def pjm_fuelmix_co2(api_key: str, date_str: str):
    """Fuel mix (MW by type) -> 24 hourly AVERAGE gCO2/kWh from gen_by_fuel,
    weighting PJM_EMISSION_FACTORS by generation. Average, not marginal."""
    df = _pjm_get("gen_by_fuel", api_key,
                  "datetime_beginning_ept,fuel_type,mw", date_str)
    if df.empty:
        return None
    df["ts"] = pd.to_datetime(df["datetime_beginning_ept"])
    df["mw"] = pd.to_numeric(df["mw"], errors="coerce")
    df["ef"] = df["fuel_type"].map(PJM_EMISSION_FACTORS).fillna(DEFAULT_FACTOR)

    def _wavg(g):
        tot = g["mw"].sum()
        return (g["mw"] * g["ef"]).sum() / tot if tot else float("nan")

    hourly = df.groupby(df["ts"].dt.hour).apply(_wavg)
    return [round(float(hourly[h]), 1) if h in hourly.index else None for h in range(24)]
