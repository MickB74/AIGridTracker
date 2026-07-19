import streamlit as st
from src.constants import (
    QUERY_COEFFS, TOKEN_COEFFS, GRID_INTENSITY, ONSITE_WUE, OFFSITE_WATER, SOURCES,
)
from src.helpers import human_energy, human_water, src_link
from src.services.news import fetch_news

def render_calc_tab():
    st.subheader("Your usage")
    
    left, right = st.columns([1, 1.1], gap="large")

    with left:
        mode = st.radio(
            "Estimate by",
            ["Queries", "Tokens"],
            horizontal=True,
            help="Choose 'Queries' to calculate by individual user prompts, or 'Tokens' for raw text-generation volume."
        )
        
        # Brief description of Queries vs Tokens to educate users
        st.caption(
            "💡 **What are these?**  \n"
            "• **Queries**: A complete prompt-and-response interaction (asking a model a question). Includes model compute plus network and search routing. Typically ranges from **0.3 Wh to 3 Wh** depending on size and features.  \n"
            "• **Tokens**: Granular chunks of text (approx. 4 characters or 0.75 words). A typical page of single-spaced text contains **500 to 800 tokens**."
        )

        if mode == "Queries":
            n = st.number_input("Number of queries", min_value=0, value=1000, step=100)
            
            # Filter and Sort controls
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                family_filter = st.selectbox(
                    "Filter by Provider",
                    ["All", "Google / Gemini", "OpenAI", "Anthropic / Claude", "Meta / Llama", "Other"]
                )
            with f_col2:
                sort_order = st.selectbox(
                    "Sort by",
                    ["Alphabetical", "Energy (Low → High)", "Energy (High → Low)"]
                )
            
            # Apply filtering
            filtered_keys = list(QUERY_COEFFS.keys())
            if family_filter == "Google / Gemini":
                filtered_keys = [k for k in filtered_keys if "Gemini" in k or "Gemma" in k]
            elif family_filter == "OpenAI":
                filtered_keys = [k for k in filtered_keys if "OpenAI" in k or "GPT" in k]
            elif family_filter == "Anthropic / Claude":
                filtered_keys = [k for k in filtered_keys if "Claude" in k]
            elif family_filter == "Meta / Llama":
                filtered_keys = [k for k in filtered_keys if "Llama" in k]
            elif family_filter == "Other":
                filtered_keys = [k for k in filtered_keys if not any(x in k for x in ["Gemini", "Gemma", "OpenAI", "GPT", "Claude", "Llama"])]
            
            # Apply sorting
            if sort_order == "Alphabetical":
                filtered_keys = sorted(filtered_keys)
            elif sort_order == "Energy (Low → High)":
                filtered_keys = sorted(filtered_keys, key=lambda k: QUERY_COEFFS[k]["energy_wh"])
            elif sort_order == "Energy (High → Low)":
                filtered_keys = sorted(filtered_keys, key=lambda k: QUERY_COEFFS[k]["energy_wh"], reverse=True)
            
            src_water_ml = None
            if not filtered_keys:
                st.warning("No sources match the selected provider filter.")
                energy_wh, co2_g, grid_label, per_unit_e = 0.0, 0.0, "", 0.0
            else:
                coeff_name = st.selectbox("Per-query source", filtered_keys)
                c = QUERY_COEFFS[coeff_name]
                energy_wh = n * c["energy_wh"]
                src_water_ml = n * c["water_ml"] if c["water_ml"] is not None else None
                if c["co2_g"] is not None:
                    co2_g = n * c["co2_g"]
                    grid_label = "source's own carbon accounting"
                else:
                    grid_name = st.selectbox("Grid carbon intensity", list(GRID_INTENSITY.keys()), index=2)
                    co2_g = energy_wh / 1000 * GRID_INTENSITY[grid_name]
                    grid_label = grid_name
                
                note_text = c["note"]
                src_key = c["src"]
                if src_key in SOURCES:
                    src_lbl, src_url = SOURCES[src_key]
                    note_text += f"\n\n🔗 **Source Link:** [{src_lbl}]({src_url})"
                st.info(note_text)
                per_unit_e = c["energy_wh"]
            
            # "Find more sources" discovery button
            st.markdown("---")
            if st.button("🔍 Find new disclosures & sources", use_container_width=True):
                with st.spinner("Searching Google News for recent AI energy/carbon disclosures..."):
                    q = '("data center" OR "AI model" OR "LLM") ("electricity consumption" OR "energy disclosure" OR "carbon footprint" OR "water use")'
                    news, err = fetch_news(q, limit=5)
                    if err or not news:
                        st.warning("No recent news updates found. Try visiting [Methodology](file:///Users/michaelbarry/Documents/GitHub/AIGridTracker/app.py#L93) for reference sites.")
                    else:
                        st.success("Found recent articles regarding AI and data center footprint disclosures:")
                        for item in news:
                            st.markdown(f"- [{item['title']}]({item['link']}) (*{item['source']}*)")
        else:
            n = st.number_input("Output tokens", min_value=0, value=500_000, step=10_000)
            # merge static references with any live coefficients loaded on Live tab
            live = st.session_state.get("live_coeffs", {})
            token_opts = {**TOKEN_COEFFS, **live}
            tok_name = st.selectbox("Per-token source", list(token_opts.keys()))
            per_unit_e = token_opts[tok_name]
            energy_wh = n * per_unit_e
            grid_name = st.selectbox("Grid carbon intensity", list(GRID_INTENSITY.keys()), index=2)
            co2_g = energy_wh / 1000 * GRID_INTENSITY[grid_name]
            grid_label = grid_name
            src_water_ml = None
            if not live:
                st.caption("Tip: open **Live models** to add measured per-token "
                           "coefficients from the ML.ENERGY leaderboard.")

        # Water = energy × (on-site cooling WUE + off-site generation water).
        with st.expander("💧 Water methodology — on-site + off-site"):
            wue_name = st.selectbox(
                "On-site cooling (operator WUE)", list(ONSITE_WUE.keys()),
                help="Water Usage Effectiveness: liters evaporated on-site per kWh of IT load.",
            )
            offsite_name = st.selectbox(
                "Off-site generation water (grid mix)", list(OFFSITE_WATER.keys()),
                help="Water consumed by the power plants supplying the data center. "
                     "Consumption (evaporated), not withdrawal.",
            )
            st.caption(
                f"Sources: {src_link(ONSITE_WUE[wue_name]['src'])} · "
                f"{src_link(OFFSITE_WATER[offsite_name]['src'])} · "
                f"{src_link('thirsty_2024')}"
            )
        onsite_ml = energy_wh * ONSITE_WUE[wue_name]["l_per_kwh"]
        offsite_ml = energy_wh * OFFSITE_WATER[offsite_name]["l_per_kwh"]
        water_ml = onsite_ml + offsite_ml

    with right:
        # Wrap right column calculations in a premium glass-card styled container
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Footprint Summary")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Energy", f"{energy_wh/1000:,.3f} kWh" if energy_wh >= 1000 else f"{energy_wh:,.1f} Wh")
        m2.metric("Water", f"{water_ml/1000:,.2f} L" if water_ml >= 1000 else f"{water_ml:,.1f} mL")
        m3.metric("Carbon", f"{co2_g/1000:,.2f} kg" if co2_g >= 1000 else f"{co2_g:,.1f} g")

        st.caption(
            f"Water split: **{onsite_ml/1000:,.2f} L** on-site cooling + "
            f"**{offsite_ml/1000:,.2f} L** off-site generation"
            if water_ml >= 1000 else
            f"Water split: **{onsite_ml:,.1f} mL** on-site cooling + "
            f"**{offsite_ml:,.1f} mL** off-site generation"
        )
        if src_water_ml is not None:
            st.caption(
                f"This source's own water disclosure (on-site only): "
                f"**{src_water_ml/1000:,.2f} L**" if src_water_ml >= 1000 else
                f"This source's own water disclosure (on-site only): "
                f"**{src_water_ml:,.1f} mL**"
            )

        st.markdown("### Human Scale Equivalents")
        st.markdown(f"- {human_energy(energy_wh)}")
        st.markdown(f"- {human_water(water_ml)}")
        st.markdown(f"- Carbon accounting: *{grid_label}*")

        st.divider()
        unit = "queries" if mode == "Queries" else "tokens"
        per_unit_w = water_ml / max(n, 1)
        per_unit_c = co2_g / max(n, 1)
        st.markdown("### Scale-up to 1 Million Units")
        st.markdown(f"- **{per_unit_e*1e6/1000:,.0f} kWh**, "
                    f"**{per_unit_w*1e6/1000:,.1f} L** water, "
                    f"**{per_unit_c*1e6/1000:,.1f} kg** CO₂e per 1M {unit}")
        st.markdown('</div>', unsafe_allow_html=True)
