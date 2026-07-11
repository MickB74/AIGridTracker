import pathlib
import json
import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=False)
def load_officials():
    """US senators + governors directory from officials.json (built from the
    official Senate contact XML and the current-governors list). Returns
    (DataFrame, generated_note) or (empty, error)."""
    # src/services/officials.py -> root/officials.json
    p = pathlib.Path(__file__).resolve().parent.parent.parent / "officials.json"
    try:
        data = json.loads(p.read_text())
        return pd.DataFrame(data["officials"]), data.get("generated", "")
    except Exception as e:                                          # noqa: BLE001
        return pd.DataFrame(), str(e)
