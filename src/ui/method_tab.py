import streamlit as st
import pandas as pd
from src.constants import QUERY_COEFFS
from src.helpers import src_link

def render_method_tab():
    st.subheader("Sources & coefficients")
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    # Output all primary source links in order
    for key in ["google_2025", "openai_2025", "epoch_2025", "hungry_2025",
                "mlenergy", "iea_2025", "gpt5_report", "eia930", "pjm_dm2",
                "cbre_dc", "cbre_glob", "jll_dc", "cushman_dc", "google_dc",
                "meta_dc", "imasons", "bnef", "bnef_106", "gartner", "wri_range",
                "sp_451", "epri_pi", "lbnl", "ercot_ll", "ercot_ll_bc",
                "ercot_ll_tac", "pjm_lf", "eia_va",
                "eia_pilot",
                "ferc_pjm_colo", "ferc_showcause", "pjm_auction25", "tx_sb6_ll",
                "spp_hill", "miso_llir",
                "google_news", "reddit", "icap_mor", "dcbans", "dcopp", "dcwatch",
                "dcresp", "dctrack", "gjf_mor",
                "rockinst", "elmaps", "watttime", "gridstatus", "datacentermap"]:
        st.markdown(f"- {src_link(key)}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("Coefficient table (per query, median text prompt)")
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    tbl = pd.DataFrame([{"Source": k, "Wh": v["energy_wh"], "gCO₂e": v["co2_g"],
                         "mL water": v["water_ml"]} for k, v in QUERY_COEFFS.items()])
    st.dataframe(tbl, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("Read the numbers carefully")
    st.markdown(
        "- **Scope matters most.** Chip-only figures (~0.10 Wh) roughly halve full-stack "
        "(~0.24 Wh). Google's excludes training, network, and end-user device energy.\n"
        "- **Carbon accounting.** Market-based (PPA/certificate) intensity can be ~⅓ of "
        "location-based grid intensity. The Calculator and Grid tab let you pick.\n"
        "- **ML.ENERGY live numbers** are min-energy (max-batch) configs on H100/B200 — a "
        "well-utilised server, so a lower bound vs. bursty real traffic.\n"
        "- **Text only.** Image/video/reasoning prompts cost materially more.\n"
        "- **Water is indirect too.** Most disclosures count cooling water, not water "
        "embedded in generating the electricity.\n"
        "- **Grid timing** can run live on **PJM Data Miner 2** (marginal CO₂ in "
        "lbs/MWh, or fuel-mix × emission factors); other ISOs use stylized curves "
        "until a feed is wired. **Marginal** intensity is the right signal for "
        "load-shifting; **average** (fuel-mix) answers a different question.")
