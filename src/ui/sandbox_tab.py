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
                "Pacific Northwest (BPA / PacifiCorp)",
                "Central Ohio (PJM)",
                "Georgia / Atlanta Metro (SERC)",
                "Phoenix, Arizona (SPP West)",
                "South Carolina Midlands (Duke / SERC)",
                "North Carolina Piedmont (Duke / PJM)",
                "Chicago / NE Illinois (PJM / ComEd)",
                "Dallas–Fort Worth (ERCOT)",
                "Salt Lake City, Utah (PacifiCorp)",
                "New York Metro (NYISO)",
                "Mississippi Delta (MISO South)",
                "Southeast Michigan (MISO / DTE)",
                "El Paso, Texas (ERCOT West)",
                "San Antonio, Texas (ERCOT / CPS Energy)",
                "Kansas City (SPP)",
                "Indiana (MISO / AES Indiana)",
                "Nashville, Tennessee (TVA)",
                "Memphis, Tennessee (TVA / MLGW)",
                "Reno / Sparks, Nevada (NV Energy)",
                "Las Vegas, Nevada (NV Energy)",
                "Cheyenne, Wyoming (WAPA / PacifiCorp)",
                "Quincy, Washington (Grant County PUD)",
                "The Dalles, Oregon (BPA / PGE)",
                "Loudoun County, Virginia (Dominion / PJM)",
                "Prince William County, Virginia (PJM)",
                "Rural Maine (ISO-NE / Versant)",
                "Central Pennsylvania (PJM / PPL)",
                "Upstate New York (NYISO North)",
                "New Albany, Ohio (AEP / PJM)",
                "Papillion / Sarpy County, Nebraska (OPPD)",
                "Albuquerque, New Mexico (PNM / SPP)",
                "Sacramento, California (CAISO / SMUD)",
                "San Jose, California (CAISO / PG&E)",
                "Henrico County, Virginia (Dominion / PJM)",
                "Abilene, Texas (ERCOT / AEP)",
                "Stillwater, Oklahoma (SPP / OG&E)",
                "Montgomery County, Missouri (MISO / Ameren)",
                "Farmington, Minnesota (MISO / Xcel)",
                "Jackson, Mississippi (Entergy / MISO South)",
                "Starke County, Indiana (MISO / NIPSCO)",
                "ACE Basin, South Carolina (Duke / Santee Cooper)",
                "Stokes County, North Carolina (Duke)",
                "Pittsylvania County, Virginia (AEP / PJM)",
                "Morgan County, Georgia (Georgia Power / SERC)",
                "El Paso County, Texas (ERCOT West / El Paso Electric)",
                "Mount Pleasant, Wisconsin (MISO / WE Energies)",
                "Lousiana Gulf Coast (MISO South / Entergy)",
            ],
            help="Determines baseline grid carbon intensity, regional temperatures, and interconnection queue lengths."
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
        
    # Regional profiles: (PUE adjustment, queue wait months, grid gCO2/kWh)
    REGION_PROFILES = {
        "Northern Virginia (PJM)":              (0.02, 60, 380),
        "West Texas (ERCOT)":                   (0.05, 24, 340),
        "Central Iowa (MISO)":                  (0.01, 48, 410),
        "Pacific Northwest (BPA / PacifiCorp)": (0.00, 54, 180),
        "Central Ohio (PJM)":                   (0.02, 54, 420),
        "Georgia / Atlanta Metro (SERC)":       (0.04, 36, 370),
        "Phoenix, Arizona (SPP West)":          (0.08, 30, 390),
        "South Carolina Midlands (Duke / SERC)":(0.04, 36, 340),
        "North Carolina Piedmont (Duke / PJM)": (0.03, 42, 350),
        "Chicago / NE Illinois (PJM / ComEd)":  (0.01, 48, 310),
        "Dallas–Fort Worth (ERCOT)":            (0.05, 24, 360),
        "Salt Lake City, Utah (PacifiCorp)":    (0.02, 42, 440),
        "New York Metro (NYISO)":               (0.01, 60, 250),
        "Mississippi Delta (MISO South)":       (0.06, 30, 400),
        "Southeast Michigan (MISO / DTE)":      (0.02, 42, 390),
        "El Paso, Texas (ERCOT West)":          (0.07, 24, 350),
        "San Antonio, Texas (ERCOT / CPS Energy)":(0.06, 24, 340),
        "Kansas City (SPP)":                    (0.03, 36, 420),
        "Indiana (MISO / AES Indiana)":         (0.02, 42, 430),
        "Nashville, Tennessee (TVA)":           (0.04, 30, 350),
        "Memphis, Tennessee (TVA / MLGW)":      (0.05, 30, 370),
        "Reno / Sparks, Nevada (NV Energy)":    (0.04, 36, 330),
        "Las Vegas, Nevada (NV Energy)":        (0.08, 36, 380),
        "Cheyenne, Wyoming (WAPA / PacifiCorp)":(0.00, 36, 460),
        "Quincy, Washington (Grant County PUD)":(0.00, 42, 80),
        "The Dalles, Oregon (BPA / PGE)":       (0.00, 48, 120),
        "Loudoun County, Virginia (Dominion / PJM)": (0.02, 60, 380),
        "Prince William County, Virginia (PJM)":(0.02, 60, 380),
        "Rural Maine (ISO-NE / Versant)":       (0.00, 48, 200),
        "Central Pennsylvania (PJM / PPL)":     (0.01, 54, 350),
        "Upstate New York (NYISO North)":       (0.00, 54, 180),
        "New Albany, Ohio (AEP / PJM)":         (0.02, 54, 420),
        "Papillion / Sarpy County, Nebraska (OPPD)": (0.02, 36, 440),
        "Albuquerque, New Mexico (PNM / SPP)":  (0.06, 36, 370),
        "Sacramento, California (CAISO / SMUD)":(0.04, 60, 220),
        "San Jose, California (CAISO / PG&E)":  (0.02, 60, 220),
        "Henrico County, Virginia (Dominion / PJM)": (0.03, 60, 380),
        "Abilene, Texas (ERCOT / AEP)":         (0.06, 24, 360),
        "Stillwater, Oklahoma (SPP / OG&E)":    (0.05, 30, 410),
        "Montgomery County, Missouri (MISO / Ameren)": (0.03, 36, 430),
        "Farmington, Minnesota (MISO / Xcel)":  (0.01, 42, 340),
        "Jackson, Mississippi (Entergy / MISO South)": (0.06, 30, 400),
        "Starke County, Indiana (MISO / NIPSCO)":(0.02, 42, 440),
        "ACE Basin, South Carolina (Duke / Santee Cooper)": (0.04, 36, 320),
        "Stokes County, North Carolina (Duke)": (0.03, 42, 350),
        "Pittsylvania County, Virginia (AEP / PJM)": (0.03, 54, 370),
        "Morgan County, Georgia (Georgia Power / SERC)": (0.04, 36, 370),
        "El Paso County, Texas (ERCOT West / El Paso Electric)": (0.07, 24, 350),
        "Mount Pleasant, Wisconsin (MISO / WE Energies)": (0.01, 42, 380),
        "Lousiana Gulf Coast (MISO South / Entergy)": (0.06, 30, 380),
    }
    pue_adj, queue_wait, grid_intensity = REGION_PROFILES.get(
        region, (0.03, 36, 350))
    pue += pue_adj

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
    if "Ohio" in region:
        feasibility_score -= 10
        backlash_reasons.append("📋 **Ohio Scrutiny**: Governor paused tax exemptions; Select Committee investigating data center impacts on ratepayers.")
    if "Mississippi" in region:
        feasibility_score -= 15
        backlash_reasons.append("⚖️ **Environmental Justice**: Mississippi communities are actively litigating air quality and permitting violations (xAI precedent).")
    if "Georgia" in region:
        feasibility_score -= 10
        backlash_reasons.append("💧 **Georgia Water Stress**: Atlanta metro faces growing water competition; governor vetoed tax-break reform attempts.")
    if "Phoenix" in region:
        feasibility_score -= 20
        backlash_reasons.append("🏜️ **Desert Water Crisis**: Arizona has paused groundwater-dependent development; extreme heat raises PUE and cooling costs.")
    if "New York" in region:
        feasibility_score -= 20
        backlash_reasons.append("🚫 **Moratorium Enacted**: NY EO 62 imposes 1-year moratorium on 50+ MW facilities (Jul 2026); first statewide ban in the US.")
    if "Michigan" in region:
        feasibility_score -= 10
        backlash_reasons.append("⚡ **Rate Contestation**: Michigan AG challenged DTE data center contracts; first contested rate case in state history.")
    if "Indiana" in region and campus_size >= 200:
        feasibility_score -= 10
        backlash_reasons.append("🏘️ **Community Opposition**: Meta's \\$10B Indiana campus drew 2,400+ petition signatures and organized resistance.")
    if "Memphis" in region:
        feasibility_score -= 20
        backlash_reasons.append("⚖️ **xAI Precedent**: Memphis xAI facility triggered Clean Air Act lawsuits from NAACP and Earthjustice; unpermitted gas turbines drew federal investigation.")
    if "Prince William" in region:
        feasibility_score -= 20
        backlash_reasons.append("🚫 **Organized Resistance**: Coalition to Protect Prince William County has blocked major projects since 2014; Board denied Dulles Cloud South rezoning.")
    if "Loudoun" in region:
        feasibility_score -= 15
        backlash_reasons.append("🔌 **Saturation Zone**: Loudoun County hosts 70%+ of world internet traffic; residents and officials pushing back on further expansion.")
    if "Maine" in region:
        feasibility_score -= 15
        backlash_reasons.append("🚫 **Moratorium Momentum**: Maine legislature passed a data-center moratorium bill (governor vetoed Apr 2026); political risk remains high.")
    if "California" in region:
        feasibility_score -= 15
        backlash_reasons.append("📜 **CEQA & Permitting**: California's environmental review process adds 12–24 months; energy costs are 2–3x national average.")
    if "Abilene" in region:
        feasibility_score -= 10
        backlash_reasons.append("🏘️ **Rural Opposition**: Save Abilene coalition organized against large-scale data center development near residential areas.")
    if "Stillwater" in region or "Oklahoma" in region:
        feasibility_score -= 10
        backlash_reasons.append("📋 **NDA Controversy**: County officials required to sign NDAs before seeing project details; conflicts with Oklahoma open government statutes.")
    if "Montgomery County, Missouri" in region:
        feasibility_score -= 10
        backlash_reasons.append("🌾 **Agricultural Land Loss**: Farmers and residents testified against converting productive farmland to data center campuses.")
    if "Farmington" in region:
        feasibility_score -= 10
        backlash_reasons.append("📋 **CRDCD Opposition**: Coalition for Responsible Data Center Development (501(c)(3)) organized; testified before MN Senate Energy Committee.")
    if "ACE Basin" in region:
        feasibility_score -= 15
        backlash_reasons.append("🌿 **Conservation Area**: SELC lawsuit to protect ACE Basin ecological preserve; one of SC's most pristine coastal ecosystems.")
    if "Stokes County" in region:
        feasibility_score -= 10
        backlash_reasons.append("🏘️ **Rural Zoning Fight**: Sierra Club and local residents challenged data center zoning in agricultural community.")
    if "Morgan County" in region:
        feasibility_score -= 15
        backlash_reasons.append("💧 **Contamination Risk**: Rep. AOC cited Meta's Georgia data center contaminating Morgan County drinking water at EPA hearing.")
    if "Pittsylvania" in region:
        feasibility_score -= 10
        backlash_reasons.append("🏥 **Health Concerns**: SELC published health impact research on gas plant associated with data center; community organized opposition.")
    if "Wyoming" in region:
        feasibility_score += 5
        backlash_reasons.append("✅ **State Support**: Wyoming governor framed data center projects as national security imperative; low population density reduces opposition.")
    if "Quincy" in region:
        feasibility_score += 5
        backlash_reasons.append("✅ **Established Hub**: Grant County PUD provides ultra-cheap hydropower; existing Microsoft, Yahoo, and Sabey campuses set precedent.")
    if "Nebraska" in region:
        feasibility_score += 5
        backlash_reasons.append("✅ **Utility Support**: OPPD actively courting data center load; public power keeps rates competitive.")
    if "Lousiana" in region:
        feasibility_score -= 5
        backlash_reasons.append("📋 **Mixed Signals**: Governor courted Meta with 20-year tax exemptions but later signed ratepayer protection order; regulatory whiplash risk.")
    if "Mount Pleasant" in region:
        feasibility_score -= 5
        backlash_reasons.append("⚠️ **Foxconn Precedent**: Community skeptical after Foxconn promised \\$10B campus but dramatically scaled back; trust deficit for megaprojects.")

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
