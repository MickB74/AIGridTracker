"""
Shared facility-impact model — one place for the physics and economics used
by the Local Impact Calculator, the Meeting Prep Generator, and the Start
Here wizard. These coefficients were previously duplicated inline in
impact_tab.py and toolkit_tab.py; change them here, not in the tabs.
"""

from src.constants import STATE_GRID_PROFILES

# (PUE, gallons of cooling water per IT kWh) by cooling type
COOLING_PROFILES = {
    "Evaporative (water-cooled)": (1.12, 2.0),
    "Dry cooling (air-cooled)":   (1.22, 0.02),
    "Hybrid":                     (1.15, 0.80),
    "Direct-to-chip (liquid)":    (1.05, 0.10),
}
DEFAULT_COOLING = "Evaporative (water-cooled)"

# The siting sandbox labels the same physics differently; map its choices onto
# the profiles above rather than re-declaring the coefficients.
SANDBOX_COOLING_ALIASES = {
    "Open-Loop":      "Evaporative (water-cooled)",
    "Closed-Loop":    "Dry cooling (air-cooled)",
    "Direct-to-chip": "Direct-to-chip (liquid)",
}

# Share of nameplate MW actually drawn, averaged over a year.
# 1.0 is the conservative planning assumption used for community impact
# estimates (wizard, calculator, meeting brief) — it answers "how bad can this
# get". 0.85 reflects observed utilization at AI training campuses and is used
# where the question is expected revenue rather than worst-case impact.
LOAD_FACTOR_FULL = 1.0
LOAD_FACTOR_AI_CLUSTER = 0.85

HOME_KWH_PER_YEAR = 10_500         # EIA average US household consumption
INVESTMENT_USD_PER_MW = 2_000_000  # rough data-center capex benchmark
DATA_DIVIDEND_SHARE = 0.02         # 2% of investment as annual CBA target
DC_INDUSTRIAL_RATE = 0.05          # $/kWh typical negotiated DC rate


def cooling_profile(cooling):
    """(PUE, gal water per IT kWh) for a cooling label, accepting either a
    COOLING_PROFILES key or a sandbox label prefix."""
    if cooling in COOLING_PROFILES:
        return COOLING_PROFILES[cooling]
    for prefix, canonical in SANDBOX_COOLING_ALIASES.items():
        if cooling.startswith(prefix):
            return COOLING_PROFILES[canonical]
    return COOLING_PROFILES[DEFAULT_COOLING]


def facility_annual_kwh(mw, load_factor=LOAD_FACTOR_FULL, pue=1.0):
    """Annual kWh for an `mw` facility. Leave `pue` at 1.0 for IT load only;
    pass a PUE to get total facility draw including cooling and overhead."""
    return mw * 8760 * load_factor * pue * 1000


def estimate_facility_impact(mw, state, cooling=DEFAULT_COOLING,
                             load_factor=LOAD_FACTOR_FULL):
    """Annual impact estimates for a facility of `mw` megawatts in `state`.

    Returns a dict with energy (TWh), water (M gal), carbon (tCO2e),
    homes-equivalent, investment/dividend economics, and the state grid
    profile used (rate, gco2, water_stress).
    """
    prof = STATE_GRID_PROFILES.get(state, {})
    rate = prof.get("rate", 0.12)
    gco2 = prof.get("gco2", 400)
    water_stress = prof.get("water_stress", "medium")

    pue, water_gal_per_kwh = cooling_profile(cooling)

    annual_kwh = facility_annual_kwh(mw, load_factor, pue)
    annual_mwh = annual_kwh / 1000
    investment_musd = mw * INVESTMENT_USD_PER_MW / 1e6

    return {
        "pue": pue,
        "water_gal_per_kwh": water_gal_per_kwh,
        "annual_mwh": annual_mwh,
        "annual_twh": annual_mwh / 1e6,
        "annual_water_mgal": annual_kwh * water_gal_per_kwh / 1e6,
        "annual_co2_t": annual_mwh * gco2 / 1e6,
        "homes_equiv": annual_kwh / HOME_KWH_PER_YEAR,
        "annual_dc_spend_busd": annual_kwh * DC_INDUSTRIAL_RATE / 1e9,
        "rate_ratio": rate / DC_INDUSTRIAL_RATE,
        "investment_musd": investment_musd,
        "data_dividend_usd": investment_musd * 1e6 * DATA_DIVIDEND_SHARE,
        "rate": rate,
        "gco2": gco2,
        "water_stress": water_stress,
    }
