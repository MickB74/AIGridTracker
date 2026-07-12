"""
Learn tab — educational explainer on data centers, AI infrastructure,
inputs/outputs, efficiency strategies, and site-selection criteria.
"""

import streamlit as st


def render_learn_tab():
    st.subheader("🎓 Learn — What is a data center and why does it matter?")
    st.caption(
        "A plain-language guide to the buildings behind AI: what goes in, what comes "
        "out, how AI facilities differ from traditional ones, and what companies look "
        "for when choosing where to build."
    )

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 1 — What is a data center?
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🏢 What is a data center?")
    st.markdown("""\
A **data center** is a purpose-built facility that houses computer servers, storage
systems, and networking equipment. Every time you stream a video, send an email, use
a banking app, or ask an AI chatbot a question, a data center somewhere is doing the
work.

Think of it as a **warehouse for computing** — but instead of shelves of products,
the racks hold thousands of servers running 24/7, connected to the internet by
fiber-optic cables and kept running by dedicated power and cooling systems.
""")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Global data centers", "~11,000+",
                   help="Facilities with 1 MW+ capacity worldwide (2025)")
        st.caption("From small server rooms to 300+ MW campuses")
    with col_b:
        st.metric("Global electricity use", "~485 TWh (2025)",
                   help="IEA estimate — about 2% of world electricity")
        st.caption("More than many entire countries")
    with col_c:
        st.metric("Projected by 2030", "~945 TWh",
                   help="IEA base projection — could double in 5 years")
        st.caption("Driven largely by AI workloads")

    st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 2 — How are AI data centers different?
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🤖 How are AI data centers different?")
    st.markdown("""\
Traditional data centers run **general workloads** — web hosting, email, databases,
video streaming. The servers inside use standard CPUs and draw moderate power.

AI data centers are fundamentally different in three ways:
""")

    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown("""\
### ⚡ Power density
Traditional servers draw **5–15 kW per rack**. AI racks packed with GPUs like
NVIDIA's H100 or B200 draw **40–120 kW per rack** — up to **10× more** in the
same physical space. This means AI facilities need vastly more power per square
foot and generate far more heat.
""")
    with d2:
        st.markdown("""\
### 🧊 Cooling demands
Standard air cooling can't handle GPU-density heat loads. AI data centers
increasingly use **liquid cooling** — piping coolant directly to chips — or
**rear-door heat exchangers**. Some use evaporative cooling towers that consume
millions of gallons of water per day.
""")
    with d3:
        st.markdown("""\
### 🔌 Grid impact
A single AI training cluster can draw **50–100 MW** continuously — the electrical
load of a small city. When dozens of these facilities cluster in one region (like
Northern Virginia or Central Texas), they can strain the local grid, drive up
electricity rates, and require billions in new transmission infrastructure.
""")

    st.info(
        "**The key difference in one sentence:** A traditional data center serves "
        "millions of small, quick requests; an AI data center runs fewer, far more "
        "computationally intensive workloads that demand specialized hardware, "
        "extreme power density, and advanced cooling."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 3 — What actually happens inside an AI data center
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## ⚙️ What actually happens inside an AI data center?")
    st.markdown("""\
Inside the building, thousands of **GPUs** (specialized AI chips) are wired together
into clusters and run nearly non-stop. But they're doing two very different kinds of
work — **training** and **inference** — with very different power profiles. Almost
everything on your electricity bill and this tracker traces back to one of these two.
""")

    t_col, i_col = st.columns(2)
    with t_col:
        st.markdown("""\
### 🏋️ Training — *building* the model
Training is how an AI model is created. Engineers feed it enormous datasets — much
of the public internet, books, code — and the model adjusts billions of internal
numbers ("parameters") over and over until it can predict language and patterns well.

- **Runs once per model**, but for **weeks or months** without stopping.
- Uses **thousands of GPUs in lockstep** on a single job — a "training cluster" of
  50–100+ MW running flat-out, 24/7.
- Extremely **power-hungry and steady** — a near-constant, city-sized electrical load
  that's hard for a grid to absorb.
- Training a single frontier model can consume **tens of gigawatt-hours** — as much
  electricity as thousands of homes use in a year.
""")
    with i_col:
        st.markdown("""\
### 💬 Inference — *using* the model
Inference is what happens every time someone actually uses the AI. Your prompt goes
to a data center, runs through the already-trained model, and a response comes back —
usually in under a second.

- **Runs constantly, forever** — every chat message, image, and search summary is an
  inference request.
- Each request is **small**, but there are **billions per day** across all users.
- Load is **spiky and follows the clock** — busy in waking hours, lighter overnight —
  which makes it easier to shift toward cleaner grid hours.
- Over a model's lifetime, **inference usually dwarfs training** in total energy,
  simply because it never stops.
""")

    st.info(
        "**Rule of thumb:** *Training* is a one-time, massive, steady burst to build "
        "the model. *Inference* is the endless drip of everyday use. Training gets the "
        "headlines; inference quietly dominates the long-run footprint."
    )

    st.markdown("""\
#### The full lifecycle, start to finish
""")
    st.markdown("""\
| Stage | What happens | Energy character |
|-------|-------------|------------------|
| **1. Data prep** | Collecting, cleaning, and filtering the training dataset | Moderate, bursty — mostly CPU and storage |
| **2. Training** | The model learns from the data over weeks/months on a GPU cluster | Huge, steady, 24/7 — the single biggest one-time draw |
| **3. Fine-tuning** | Smaller follow-up training to specialize or align the model (e.g. safety) | Much smaller than training, done repeatedly |
| **4. Deployment** | Loading the finished model onto inference servers | Low — a setup step |
| **5. Inference** | Serving real user requests, 24/7, for the life of the model | Spiky but relentless; dominates lifetime total |
| **6. Retraining** | Building the next, better model — the cycle repeats | Back to a full training-sized burst |
""")

    st.caption(
        "This is why AI facilities come in two flavors: **training campuses** built for "
        "massive, constant power, and **inference campuses** placed close to users for "
        "low latency. Some sites do both."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 4 — Using the right model for the task
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🎯 Using the right model for the task")
    st.markdown("""\
Not every question needs the biggest, most powerful model. A frontier model with
hundreds of billions of parameters can use **10–100× more energy per response** than
a small model — and for most everyday tasks, the small model answers just as well.
**Matching the model to the job** is one of the simplest ways to cut AI's energy and
carbon footprint, and it's a choice made by the people *building* AI products, not
just the data-center operators.
""")

    m1, m2 = st.columns(2)
    with m1:
        st.markdown("""\
#### Bigger isn't always better
- **Small / "mini" models** handle the bulk of real traffic — classification,
  summarizing, autocomplete, simple Q&A — at a fraction of the energy.
- **Large frontier models** shine at hard reasoning, complex code, and nuanced
  writing, but are wasteful overkill for routine requests.
- Sending every request to the largest model is like **taking a semi-truck to pick
  up a bag of groceries** — it works, but you're burning far more fuel than the trip
  requires.
""")
    with m2:
        st.markdown("""\
#### How teams right-size in practice
- **Model routing** — a lightweight system sends easy questions to a small model and
  only escalates hard ones to a large model.
- **Distillation** — training a small, cheap model to mimic a big one for a specific
  task, keeping most of the quality at a fraction of the cost.
- **Caching & retrieval** — reusing past answers or looking facts up in a database
  instead of re-running the model from scratch.
- **Shorter prompts & outputs** — energy scales with the number of tokens processed,
  so concise in-and-out means less compute.
""")

    st.info(
        "**The takeaway:** the greenest AI request is often the one that never touches "
        "a giant model. Right-sizing — the *right* model, a *short* prompt, a *cached* "
        "answer when possible — can cut the energy of a typical workload dramatically "
        "with no visible drop in quality."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 5 — Inputs and Outputs
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🔄 Inputs and outputs — what goes in, what comes out")

    in_col, out_col = st.columns(2)

    with in_col:
        st.markdown("### 📥 Inputs (what a data center consumes)")
        st.markdown("""\
| Resource | What it's for | Scale |
|----------|--------------|-------|
| **Electricity** | Powers servers, cooling, lighting, networking | 50–300+ MW per campus |
| **Water** | Evaporative cooling towers, humidification | 1–5 million gal/day for large facilities |
| **Land** | Building footprint, setbacks, future expansion | 50–500+ acres per campus |
| **Fiber optic cables** | Internet connectivity, data transit | Multiple redundant paths required |
| **Backup fuel** | Diesel/gas generators for outages | Thousands of gallons stored on-site |
| **Hardware** | GPUs, CPUs, memory, SSDs, networking gear | Refreshed every 3–5 years |
| **Construction materials** | Concrete, steel, copper for the building itself | 12–24 month build cycles |
""")

    with out_col:
        st.markdown("### 📤 Outputs (what a data center produces)")
        st.markdown("""\
| Output | Description | Community impact |
|--------|------------|-----------------|
| **Compute services** | AI inference, cloud apps, storage | The product — delivered over fiber |
| **Heat** | Waste heat from servers and power conversion | Radiated or cooled away; rarely recaptured |
| **Noise** | Cooling fans, generators, transformers | 50–70+ dB at property line; constant |
| **CO₂ emissions** | From grid electricity and backup generators | Varies by grid mix; 0 if 100% renewable |
| **Wastewater** | Blowdown from cooling towers (mineral-laden) | Discharged to municipal systems |
| **Jobs** | Construction (temporary) and operations (permanent) | 50–150 permanent jobs per facility |
| **Tax revenue** | Property taxes, sales taxes on equipment | Often reduced by abatement deals |
""")

    st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 6 — Efficiency
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 🌱 How can data centers be more efficient?")
    st.markdown("""\
The industry uses several strategies to reduce energy, water, and carbon footprint.
Not all operators adopt all of these — and the gap between the best and worst
performers is wide.
""")

    e1, e2 = st.columns(2)
    with e1:
        st.markdown("""\
#### Power efficiency (PUE)
**Power Usage Effectiveness** measures total facility energy ÷ IT equipment energy.
- **PUE 1.0** = perfect (impossible in practice)
- **PUE 1.1–1.2** = best-in-class (Google, Meta)
- **PUE 1.5–1.8** = older or poorly designed facilities
- **Industry average** ≈ 1.55 (Uptime Institute, 2024)

Every 0.1 reduction in PUE saves **~7–10%** of total energy.

#### Liquid cooling
Direct-to-chip liquid cooling removes heat far more efficiently than air. It enables
higher rack densities and can reduce cooling energy by **30–50%**. Increasingly
required for AI GPU racks drawing 60+ kW.

#### Free cooling
Facilities in cold climates (Nordics, Pacific Northwest, Ireland) can use outside
air for cooling much of the year, drastically cutting water and energy for chiller
systems.
""")

    with e2:
        st.markdown("""\
#### Renewable energy
Leading operators sign **Power Purchase Agreements (PPAs)** for wind and solar to
match their electricity consumption. The gold standard is **24/7 Carbon-Free
Energy (CFE)** — matching consumption with clean energy hour-by-hour on the same
grid, not just annually through credits.

#### Water efficiency (WUE)
**Water Usage Effectiveness** measures liters of water consumed per kWh of IT energy.
- **WUE 0.0** = air-cooled, no water used
- **WUE 0.2–0.5** = efficient evaporative cooling
- **WUE 1.0–2.0** = heavy water use
- Some facilities in arid regions are switching to **closed-loop** or **air-cooled**
  chillers that use zero water at the cost of higher energy use.

#### Waste heat reuse
A few European facilities pipe waste heat to district heating networks, warming
nearby homes and offices. This is rare in the US but represents a major untapped
efficiency opportunity.

#### Compute efficiency
The cheapest watt is the one you never draw. Key levers:
- **Server utilization** — Average utilization across the industry is just
  **12–18%** (NRDC, 2024). Virtualization and workload packing can push this
  above 60%, cutting servers (and energy) by half or more.
- **Model optimization** — Techniques like quantization, distillation, and
  sparse attention can reduce inference energy per query by **2–10×** with
  minimal quality loss.
- **Right-sizing hardware** — Matching GPU/CPU tier to the workload avoids
  powering idle silicon. Not every task needs an H100.
- **Workload scheduling** — Shifting deferrable jobs (training, batch
  inference, backups) to off-peak hours or periods of high renewable
  generation reduces both grid strain and carbon intensity.
""")

    st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 7 — Site selection
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 📍 Where do companies build — and what do they look for?")
    st.markdown("""\
Site selection is driven by a specific checklist of requirements. Understanding what
companies prioritize explains why data centers cluster in certain regions — and why
some communities are targeted more than others.
""")

    st.markdown("""\
| Priority | What they need | Why it matters | Where it leads |
|----------|---------------|----------------|----------------|
| **1. Power availability** | 50–300+ MW of firm, deliverable electricity | Without power, nothing runs. New generation or transmission takes 3–7 years to build. | Northern Virginia, Central Texas, Central Ohio — where grid capacity exists or is planned |
| **2. Fiber connectivity** | Dense fiber routes with low latency to major metros | AI inference must respond in milliseconds. Distance = delay. | Along major internet exchange points and cable landing stations |
| **3. Tax incentives** | Property tax abatements, sales tax exemptions on equipment | A $1B+ campus can save $50–200M over 20 years with incentives | States with aggressive incentive programs (Virginia, Texas, Georgia, Indiana) |
| **4. Land cost & availability** | 50–500 acres, flat, outside flood zones | Campuses are expanding rapidly and need room to grow | Exurban and rural areas with cheap agricultural land |
| **5. Water access** | Reliable municipal or well water supply for cooling | Evaporative cooling is the cheapest thermal solution | Near rivers, reservoirs, or municipal water systems |
| **6. Permitting speed** | Fast zoning approval and building permits | Every month of delay costs millions in lost revenue | Jurisdictions with business-friendly zoning or by-right development |
| **7. Natural disaster risk** | Low earthquake, hurricane, tornado, flood exposure | Downtime is unacceptable for mission-critical workloads | Inland areas with moderate climates |
| **8. Workforce** | Electricians, HVAC techs, security, network engineers | Ongoing operations require specialized labor | Near population centers (but not so close that land is expensive) |
""")

    st.warning(
        "**What's often missing from this checklist:** community input, cumulative "
        "impact on local water and power resources, noise standards, and long-term "
        "rate impacts on existing ratepayers. These are the gaps this tracker aims "
        "to make visible."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 8 — Key terms glossary
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.expander("📖 Glossary of key terms", expanded=False):
        st.markdown("""\
| Term | Definition |
|------|-----------|
| **PUE** | Power Usage Effectiveness — ratio of total facility energy to IT energy. Lower is better. |
| **WUE** | Water Usage Effectiveness — liters of water per kWh of IT energy. Lower is better. |
| **CFE** | Carbon-Free Energy — electricity from zero-carbon sources (solar, wind, nuclear, hydro). |
| **Hyperscaler** | The largest cloud/AI companies that build their own data centers (Google, Microsoft, Amazon, Meta). |
| **Colocation (colo)** | A data center operator that leases space, power, and cooling to tenants. |
| **Interconnection queue** | The list of projects waiting for grid connection approval from the regional operator (e.g., PJM, ERCOT). |
| **Moratorium** | A temporary ban or pause on new data-center construction, usually enacted by local or state government. |
| **PPA** | Power Purchase Agreement — a long-term contract to buy electricity from a specific generator, often renewable. |
| **Rack density** | The amount of power drawn per server rack, measured in kW. AI racks are 40–120+ kW vs. 5–15 kW traditional. |
| **GPU** | Graphics Processing Unit — specialized chips (like NVIDIA H100/B200) that power AI training and inference. |
| **Inference** | Running a trained AI model to generate responses — what happens when you use ChatGPT, Gemini, etc. |
| **Training** | The initial process of building an AI model by processing massive datasets. Extremely energy-intensive. |
| **Evaporative cooling** | Cooling method that evaporates water to remove heat. Effective but water-intensive. |
| **Liquid cooling** | Piping coolant directly to server chips. More efficient for high-density AI workloads. |
| **Marginal emissions** | The CO₂ rate of the *next* power plant that would turn on to serve new load. The right signal for load-shifting. |
""")
    st.markdown("</div>", unsafe_allow_html=True)

    st.caption(
        "This page is a living explainer. Sources: IEA *Energy and AI* (2025), "
        "Uptime Institute Global Survey (2024), EPRI *Powering Intelligence* (2025), "
        "Google Environmental Report (2024), US DOE Data Center Primer. "
        "See the **📚 Methodology** tab for full citations."
    )
