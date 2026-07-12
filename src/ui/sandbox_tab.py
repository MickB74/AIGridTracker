"""
🎮 Siting Sandbox tab — an interactive simulator for data center siting,
cooling designs, power procurement, and grid reliability trade-offs.
Calculates interconnection queue wait times, capital costs, water draw, carbon footprint,
and local community backlash risk based on user inputs.
"""

import streamlit as st
import pandas as pd
import altair as alt

def render_sandbox_tab():
    st.subheader("🎮 AI Datacenter Siting Sandbox")
    st.caption(
        "You are the Director of Infrastructure Planning. Design a new high-density AI compute campus "
        "and simulate its construction cost, power draw, carbon footprint, and local regulatory feasibility."
    )

    # Layout: Sidebar inputs on left, outcomes on right
    left, right = st.columns([1, 1.2], gap="large")

    with left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Campus Design Specs")
        
        campus_size = st.slider(
            "Target Facility Capacity (MW)",
            min_value=50,
            max_value=1000,
            value=200,
            step=50,
            help="AI workloads require massive scale. A single frontier cluster can draw 100 MW to 500 MW."
        )
        
        region = st.selectbox(
            "Siting Region / Grid Zone",
            options=[
                "Northern Virginia (PJM)",
                "West Texas (ERCOT)",
                "Central Iowa (MISO)",
                "Pacific Northwest (BPA / PacifiCorp)"
            ],
            help="Determines baseline grid carbon intensity, regional temperatures, and interconnection queue queue lengths."
        )
        
        cooling = st.selectbox(
            "Cooling Infrastructure",
            options=[
                "Open-Loop Evaporative (Water Intensive)",
                "Closed-Loop Dry Air Cooling (Zero Water)",
                "Direct-to-Chip Liquid Cooling (Premium / Low Overhead)"
            ],
            help="Evaporative cooling is cheap but draws millions of gallons daily. Liquid/dry cooling costs more but protects water resources."
        )
        
        power = st.selectbox(
            "Power Procurement Strategy",
            options=[
                "Standard Grid Connection",
                "24/7 Hourly Clean Energy Match (Solar + Wind + Battery)",
                "Nuclear Co-location (Behind the Meter)",
                "On-site Natural Gas Turbines (Microgrid)"
            ],
            help="Grid power is fast but carbon-heavy. CFE matching or nuclear co-location protects grid emission goals but incurs capital premiums."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # --- SIMULATOR LOGIC ---
    # 1. Base PUE and regional temperature adjustments
    pue = 1.0
    cooling_cost_adj = 0.0
    water_rate = 0.0 # gallons per kWh
    
    if cooling.startswith("Open-Loop"):
        pue = 1.12
        water_rate = 2.0
        cooling_cost_adj = 0.0
    elif cooling.startswith("Closed-Loop"):
        pue = 1.22
        water_rate = 0.02
        cooling_cost_adj = 0.5 # million $ per MW
    else: # Direct-to-chip
        pue = 1.05
        water_rate = 0.10
        cooling_cost_adj = 1.5 # million $ per MW
        
    # Regional PUE adjustments (warmer climates require more fan/chiller power)
    if "Texas" in region:
        pue += 0.05
    elif "Virginia" in region:
        pue += 0.02
    elif "Iowa" in region:
        pue += 0.01

    # 2. Interconnection Queue Wait Times (months)
    queue_wait = 36
    if "Virginia" in region:
        queue_wait = 60 # PJM queues are heavily constrained
    elif "Texas" in region:
        queue_wait = 24 # ERCOT connects fast
    elif "Iowa" in region:
        queue_wait = 48
    else: # Northwest
        queue_wait = 54

    # Bypassing the grid queue with gas turbines or behind-the-meter nuclear
    if power.startswith("On-site Natural Gas"):
        queue_wait = min(queue_wait, 12) # Turbines are constructed on-site in a year
    elif power.startswith("Nuclear"):
        queue_wait = min(queue_wait, 42) # Nuclear agreements are complex but bypass utility lines

    # 3. Capital Expenditures (CapEx) calculation
    # Base cost is $8.0M per MW
    base_cost_per_mw = 8.0
    power_cost_adj = 0.0
    
    if power.startswith("24/7"):
        power_cost_adj = 4.0 # Add solar+wind+battery costs
    elif power.startswith("Nuclear"):
        power_cost_adj = 6.0 # Behind the meter connection premiums
    elif power.startswith("On-site Natural Gas"):
        power_cost_adj = 2.5 # Cost of gas turbines

    total_capex = campus_size * (base_cost_per_mw + cooling_cost_adj + power_cost_adj)

    # 4. Energy and Carbon Calculations
    # Assume 85% utilization (load factor) for AI clusters
    load_factor = 0.85
    annual_power_mwh = campus_size * 8760 * load_factor * pue
    
    # Grid emission factors (gCO2/kWh)
    grid_intensity = 350
    if "Virginia" in region:
        grid_intensity = 380
    elif "Texas" in region:
        grid_intensity = 340
    elif "Iowa" in region:
        grid_intensity = 410
    else: # Northwest
        grid_intensity = 180

    # Apply procurement strategies
    carbon_intensity = grid_intensity
    if power.startswith("24/7"):
        carbon_intensity = grid_intensity * 0.05 # 95% CFE match reduces net grid intensity
    elif power.startswith("Nuclear"):
        carbon_intensity = 0.0 # Zero carbon
    elif power.startswith("On-site Natural Gas"):
        carbon_intensity = 390 # Carbon of modern CCGT gas turbines

    annual_carbon_tons = (annual_power_mwh * 1000 * carbon_intensity) / 1e6

    # 5. Water Consumption
    annual_water_gallons = (annual_power_mwh * 1000 * water_rate)

    # 6. Siting Feasibility & Backlash Score (0-100, higher is more feasible/less backlash)
    feasibility_score = 100
    backlash_reasons = []

    if water_rate > 1.0:
        feasibility_score -= 25
        backlash_reasons.append("⚠️ **High Water Backlash**: Open-loop cooling draws heavy local opposition in agricultural/residential areas.")
    if carbon_intensity > 300:
        feasibility_score -= 15
        backlash_reasons.append("🌡️ **Carbon Footprint Penalty**: Drawing standard grid power in a coal/gas zone clashes with corporate zero-carbon targets.")
    if queue_wait > 36:
        feasibility_score -= 20
        backlash_reasons.append("⏳ **Grid Queue Constraint**: Interconnection queue delay slows commercial time-to-market.")
    if power.startswith("On-site Natural Gas"):
        feasibility_score -= 30
        backlash_reasons.append("🛢️ **Air Quality Backlash**: On-site fossil-fuel combustion triggers severe local emissions permit battles.")
    if "Virginia" in region and campus_size >= 300:
        feasibility_score -= 15
        backlash_reasons.append("🔌 **Loudoun Over-Density**: High scale in Virginia triggers immediate transmission upgrade surcharges.")

    # Clamp score
    feasibility_score = max(5, min(100, feasibility_score))

    # --- RENDERING RESULTS ---
    with right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Simulation Outcomes")
        
        # Siting Feasibility Badge
        if feasibility_score >= 75:
            st.success(f"🟢 **APPROVED** — Permitting Feasibility: **{feasibility_score}%**")
        elif feasibility_score >= 45:
            st.warning(f"🟡 **CONDITIONAL WARNING** — Permitting Feasibility: **{feasibility_score}%**")
        else:
            st.error(f"🔴 **HIGH BACKLASH RISK** — Permitting Feasibility: **{feasibility_score}%**")
            
        # Metric Grid
        st.divider()
        m1, m2 = st.columns(2)
        m1.metric("Est. Capital Cost", f"${total_capex/1e3:.2f} Billion", f"${total_capex/campus_size:.1f}M / MW")
        m2.metric("Grid Interconnection Queue", f"{queue_wait} Months", "Wait time to power up")
        
        m3, m4 = st.columns(2)
        m3.metric("Annual Carbon Draw", f"{annual_carbon_tons:,.0f} tCO₂e", f"{carbon_intensity} gCO₂/kWh eff.")
        m4.metric("Annual Cooling Water", f"{annual_water_gallons/1e6:.1f} Million Gal", f"{water_rate} L/kWh rate")
        
        st.divider()
        st.markdown(f"**Calculated Fleet-Wide PUE**: `{pue:.2f}`")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Risk factors expander
        if backlash_reasons:
            with st.expander("🔍 Siting Risk Factors Identified", expanded=True):
                for reason in backlash_reasons:
                    st.markdown(reason)
        else:
            st.success("✅ **Zero Friction Design**: Your combinations of direct-to-chip cooling, renewable matching, and siting minimizes local impact.")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🧠 The Siting Trade-Off Guide")
    st.markdown(
        "- **Speed vs. Cleanliness**: Selecting *On-site Natural Gas* bypasses utilities queues (12 months wait vs 60 in Virginia) "
        "but triggers severe local opposition and increases emissions, conflicting with corporate pledges.  \n"
        "- **Water vs. Power (The PUE Paradox)**: *Closed-loop dry-air cooling* saves water entirely but has a worse PUE (1.22+). "
        "This means the server consumes more net electricity, raising the carbon footprint unless backed by 100% CFE.  \n"
        "- **Direct-to-Chip Liquid Cooling**: The premium option. Incurs high initial CapEx (+$1.5M/MW) but enables a "
        "fleet-wide PUE of 1.05 and supports modern high-power GPUs (like Nvidia Blackwell B200s drawing 1.2 kW per chip)."
    )
    st.markdown('</div>', unsafe_allow_html=True)
