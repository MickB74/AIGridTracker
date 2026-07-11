import streamlit as st
import pandas as pd
import altair as alt
import datetime as _dt
from src.constants import GRID_CURVES, EIA_RESPONDENTS
from src.services.secrets import load_local_secrets
from src.services.eia import eia930_fuelmix_co2
from src.services.pjm import pjm_marginal_co2, pjm_fuelmix_co2

def render_grid_tab():
    st.subheader("When you run it matters — hourly grid carbon")
    st.caption("Same tokens, different carbon depending on the hour and grid. Shift "
               "flexible/batch workloads to clean hours (the CFE / 24-7 matching idea).")

    with st.expander("What is **gCO₂/kWh** — and marginal vs. average?"):
        st.markdown(
            "**gCO₂/kWh = grams of CO₂ per kilowatt-hour** — the carbon emitted for "
            "each unit of electricity you draw. Multiply by your energy use to get "
            "carbon: `1 kWh × 400 gCO₂/kWh = 400 g = 0.4 kg CO₂`.\n\n"
            "It **changes by the hour**: when wind and solar are abundant (midday in "
            "CAISO, windy nights in ERCOT) the number drops; when gas and coal cover "
            "the load it rises. That's why *when* you run a flexible job matters.\n\n"
            "- **Average (fuel-mix):** the carbon of the *whole grid mix* that hour — "
            "generation-weighted across every fuel. Good for footprint accounting. "
            "The EIA-930 and PJM fuel-mix options here are average.\n"
            "- **Marginal:** the carbon of the *next* MWh — the plant that ramps up "
            "when you add load (usually gas). This is the **correct signal for "
            "load-shifting**, because it's what your extra demand actually causes. "
            "The PJM marginal option is this.")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    src = st.radio("Curve source", [
        "Stylized (offline)",
        "EIA-930 · fuel-mix avg (any US ISO)",
        "PJM · marginal CO₂ (Data Miner 2)",
        "PJM · fuel-mix avg (Data Miner 2)",
    ], horizontal=True)

    energy_kwh = st.number_input("Energy of the workload (kWh)", min_value=0.0,
                                 value=1.0, step=0.5,
                                 help="From the Calculator, or any batch job.")

    curve, label, note = None, "", ""
    secrets = load_local_secrets()

    if src == "Stylized (offline)":
        grid_name = st.selectbox("Grid / ISO", list(GRID_CURVES.keys()))
        curve = GRID_CURVES[grid_name]
        label = grid_name.split(" (")[0]
        note = ("Stylized illustration, not live. Use the EIA-930 option for any US "
                "ISO, a PJM option for marginal data, or wire Electricity Maps / "
                "WattTime for others.")
    elif src.startswith("EIA-930"):
        c1, c2, c3 = st.columns([2, 1.2, 1])
        api_key = c1.text_input("EIA API key", type="password",
                                value=secrets["eia"],
                                help="Free instant key: eia.gov/opendata/register.php")
        if secrets["eia"]:
            c1.caption("🔑 Auto-loaded from local config.")
        ba = c2.selectbox("Balancing authority", list(EIA_RESPONDENTS.keys()),
                          format_func=lambda k: EIA_RESPONDENTS[k][0])
        date = c3.date_input("Date (local)", value=_dt.date.today() - _dt.timedelta(days=1),
                             key="eia_date")
        date_str = date.strftime("%Y-%m-%d")
        ba_label = EIA_RESPONDENTS[ba][0].split(" (")[0]
        if not api_key:
            st.info("Enter your free EIA API key to pull live fuel-mix data. "
                    "Falling back to a stylized curve below.")
            curve = GRID_CURVES.get(
                {"ERCO": "ERCOT (wind + solar)", "CISO": "CAISO (solar duck curve)"}
                .get(ba, "PJM (coal/gas/nuclear, flatter)"),
                GRID_CURVES["Flat average (illustrative)"])
            label = f"{ba_label} (stylized fallback)"
        else:
            try:
                curve = eia930_fuelmix_co2(api_key, date_str, ba)
                label = f"{ba_label} fuel-mix avg · {date_str}"
                if not curve or all(v is None for v in curve):
                    raise RuntimeError("no rows returned")
                note = ("Live EIA-930 net generation by fuel type × direct-combustion "
                        "emission factors (editable in EIA_EMISSION_FACTORS), weighted "
                        "to an hourly AVERAGE in local time. Average, not marginal.")
            except Exception as e:                                # noqa: BLE001
                st.warning(f"EIA fetch failed ({e}). Using a stylized curve.")
                curve = GRID_CURVES["Flat average (illustrative)"]
                label = f"{ba_label} (stylized fallback)"
    else:
        c1, c2 = st.columns([2, 1])
        api_key = c1.text_input("PJM Data Miner 2 subscription key", type="password",
                                value=secrets["pjm"],
                                help="Data Miner 2 → account icon → API Access.")
        if secrets["pjm"]:
            c1.caption("🔑 Auto-loaded from local config.")
        date = c2.date_input("Date (EPT)", value=_dt.date.today() - _dt.timedelta(days=1))
        date_str = date.strftime("%m/%d/%Y")
        pnode = ""
        marginal = src.startswith("PJM · marginal")
        if marginal:
            pnode = st.text_input("pnode_id (blank = average all zones)", value="",
                                  help="Restrict to one zone/hub for a small, fast query.")
        if not api_key:
            st.info("Enter your subscription key to pull live PJM data. "
                    "Falling back to a stylized PJM-shaped curve below.")
            curve = GRID_CURVES["PJM (coal/gas/nuclear, flatter)"]
            label = "PJM (stylized fallback)"
        else:
            try:
                if marginal:
                    curve = pjm_marginal_co2(api_key, date_str, pnode)
                    label = f"PJM marginal · {date_str}"
                else:
                    curve = pjm_fuelmix_co2(api_key, date_str)
                    label = f"PJM fuel-mix avg · {date_str}"
                if not curve or all(v is None for v in curve):
                    raise RuntimeError("no rows returned")
                note = ("Live from PJM Data Miner 2. Marginal = correct signal for "
                        "load-shifting; fuel-mix avg uses editable emission factors."
                        if marginal else
                        "Live fuel mix × direct-combustion emission factors "
                        "(editable in PJM_EMISSION_FACTORS). Average, not marginal.")
            except Exception as e:                                # noqa: BLE001
                st.warning(f"PJM fetch failed ({e}). Using stylized PJM curve.")
                curve = GRID_CURVES["PJM (coal/gas/nuclear, flatter)"]
                label = "PJM (stylized fallback)"

    # --- chart + stats (robust to missing/None hours) ---------------------- #
    curve_df = pd.DataFrame({"hour": list(range(24)), "gco2_kwh": curve})
    area = (alt.Chart(curve_df).mark_area(opacity=0.25, line=True).encode(
        x=alt.X("hour:O", title="Hour of day"),
        y=alt.Y("gco2_kwh:Q", title="gCO₂ / kWh"),
        tooltip=["hour", "gco2_kwh"],
    ).properties(height=280))
    st.altair_chart(area, use_container_width=True)

    valid = [(h, v) for h, v in enumerate(curve) if v is not None]
    if not valid:
        st.warning("No usable intensity values for this selection.")
    else:
        lo_h, lo = min(valid, key=lambda t: t[1])
        hi_h, hi = max(valid, key=lambda t: t[1])
        avg = sum(v for _, v in valid) / len(valid)
        co2_clean, co2_dirty, co2_avg = (energy_kwh * x / 1000 for x in (lo, hi, avg))
        saved = co2_dirty - co2_clean
        pct = (saved / co2_dirty * 100) if co2_dirty else 0

        k1, k2, k3 = st.columns(3)
        k1.metric(f"Cleanest hour ({lo_h:02d}:00)", f"{co2_clean:.3f} kg", f"{lo:.0f} gCO₂/kWh")
        k2.metric("24h average", f"{co2_avg:.3f} kg", f"{avg:.0f} gCO₂/kWh")
        k3.metric(f"Dirtiest hour ({hi_h:02d}:00)", f"{co2_dirty:.3f} kg",
                  f"{hi:.0f} gCO₂/kWh", delta_color="inverse")

        st.success(f"Shifting this workload from the dirtiest to the cleanest hour cuts "
                   f"carbon by **{saved:.3f} kg ({pct:.0f}%)** on {label}.")
        if len(valid) < 24:
            st.caption(f"Note: only {len(valid)}/24 hours had data.")
    st.caption(note)
    st.markdown('</div>', unsafe_allow_html=True)
