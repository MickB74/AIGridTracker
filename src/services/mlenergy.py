import requests
import pandas as pd
import streamlit as st
from src.constants import MLENERGY_BASE

@st.cache_data(ttl=86_400, show_spinner=False)
def load_mlenergy(slug: str):
    """Fetch a task file and reduce to the min-energy (best-batched) config per
    (model, gpu). Returns (DataFrame, error_str_or_None)."""
    try:
        r = requests.get(MLENERGY_BASE.format(slug=slug), timeout=12)
        r.raise_for_status()
        cfgs = r.json()["configurations"]
        rows = [{
            "model": c["nickname"],
            "gpu": c["gpu_model"],
            "wh_per_token": c["energy_per_token_joules"] / 3600.0,
            "wh_per_request": c["energy_per_request_joules"] / 3600.0,
            "params_b": c.get("total_params_billions"),
            "precision": c.get("weight_precision", "—"),
            "arch": c.get("architecture", "—"),
        } for c in cfgs]
        df = pd.DataFrame(rows)
        idx = df.groupby(["model", "gpu"])["wh_per_token"].idxmin()
        df = df.loc[idx].sort_values("wh_per_token").reset_index(drop=True)
        return df, None
    except Exception as e:                                    # noqa: BLE001
        return None, str(e)
