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
}
DEFAULT_COOLING = "Evaporative (water-cooled)"

HOME_KWH_PER_YEAR = 10_500         # EIA average US household consumption
INVESTMENT_USD_PER_MW = 2_000_000  # rough data-center capex benchmark
DATA_DIVIDEND_SHARE = 0.02         # 2% of investment as annual CBA target
DC_INDUSTRIAL_RATE = 0.05          # $/kWh typical negotiated DC rate


def estimate_facility_impact(mw, state, cooling=DEFAULT_COOLING):
    """Annual impact estimates for a facility of `mw` megawatts in `state`.

    Returns a dict with energy (TWh), water (M gal), carbon (tCO2e),
    homes-equivalent, investment/dividend economics, and the state grid
    profile used (rate, gco2, water_stress).
    """
    prof = STATE_GRID_PROFILES.get(state, {})
    rate = prof.get("rate", 0.12)
    gco2 = prof.get("gco2", 400)
    water_stress = prof.get("water_stress", "medium")

    pue, water_gal_per_kwh = COOLING_PROFILES.get(
        cooling, COOLING_PROFILES[DEFAULT_COOLING])

    annual_mwh = mw * 8760 * pue
    annual_kwh = annual_mwh * 1000
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
