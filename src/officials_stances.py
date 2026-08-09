"""
Curated, sourced data-center stances for federal + gubernatorial officials.

Kept in code (not just baked into officials.json) so the roster can be
regenerated from scratch by scripts/refresh_officials.py without losing the
hand-verified stances. Each entry is a documented action with a source key that
must exist in src.constants.SOURCES.

Key: (office, state_postal, last-name-token-lowercase) -> (stance_text, src_key).
Add a new stance here, add its source to constants.SOURCES, and (optionally) a
protection score in src.official_grades.PROTECTION_SCORES to grade it.
"""

STANCES = {
    # ── Governors ──────────────────────────────────────────────────────────
    ("Governor", "GA", "kemp"): (
        "Vetoed HB 1192 (2024), which would have paused data-center sales-tax "
        "exemptions — sided with keeping incentives.", "ga_kemp"),
    ("Governor", "TX", "abbott"): (
        "Signed SB 6 (2025): 75 MW+ loads must pay for grid upgrades and curtail "
        "in emergencies; later urged limits on rural-neighborhood builds.", "tx_sb6"),
    ("Governor", "LA", "landry"): (
        "Courted Meta's $10B campus with a 20-year sales-tax exemption; later "
        "signed an order to protect utility ratepayers.", "la_landry"),
    ("Governor", "VA", "spanberger"): (
        "Signed 2026 energy laws: data centers pay their fair share, stricter "
        "backup-generator rules, and a first-of-its-kind energy-consumption tax.",
        "va_span"),
    ("Governor", "PA", "shapiro"): (
        "Proposed 'GRID' standards tying incentives to escalating clean-firm "
        "energy use and making developers pay grid-upgrade costs.", "pa_shapiro"),
    ("Governor", "AZ", "hobbs"): (
        "Signed a 3-year pause on new data-center sales-tax breaks and proposed "
        "a per-gallon water-user fee.", "az_hobbs"),
    ("Governor", "OH", "dewine"): (
        "Paused new data-center tax exemptions pending a legislative study; says "
        "data centers should pay their fair share.", "oh_dewine"),
    ("Governor", "WI", "evers"): (
        "Courted Microsoft's $7B+ Mount Pleasant campus and signed pro-data-center "
        "incentive legislation.", "wi_evers"),
    ("Governor", "UT", "cox"): (
        "Signed EO 2026-03 setting a 'higher bar' for data centers — protecting "
        "water, air quality, and ratepayers.", "ut_cox"),
    ("Governor", "NV", "lombardo"): (
        "Backs data-center projects but requires closed-loop water recycling to "
        "limit consumption.", "nv_lombardo"),
    ("Governor", "OR", "kotek"): (
        "Convened a state Data Center Advisory Committee and backed a one-year "
        "tax-break moratorium ('stop being a cheap date').", "or_kotek"),
    ("Governor", "IN", "braun"): (
        "Broke ground on Meta's $10B campus but insists hyperscalers 'pay every "
        "penny' and opposes tax abatements.", "in_braun"),
    ("Governor", "ME", "mills"): (
        "Vetoed a statewide data-center moratorium bill (Apr 2026).", "rockinst"),
    ("Governor", "NY", "hochul"): (
        "Weighing a data-center moratorium passed by the legislature (Jun 2026).",
        "rockinst"),
    # ── House ──────────────────────────────────────────────────────────────
    ("Representative", "KY", "guthrie"): (
        "Sponsors the Ratepayer Protection Act — a federal standard requiring "
        "large loads (data centers) to pay the full cost of new generation and "
        "transmission.", "house_rpa"),
    ("Representative", "FL", "castor"): (
        "Co-sponsors the Ratepayer Protection Act — large loads pay their own "
        "grid-upgrade costs.", "house_rpa"),
    ("Representative", "CO", "evans"): (
        "Co-sponsors the Ratepayer Protection Act — large loads pay their own "
        "grid-upgrade costs.", "house_rpa"),
    ("Representative", "NJ", "pallone"): (
        "Called for a nationwide moratorium on new data-center development.",
        "house_pallone"),
    ("Representative", "VA", "subramanyam"): (
        "Opposes data-center expansion in his Northern Virginia district; "
        "introduced the Data Infrastructure Risk Reduction Act.", "house_subram"),
    # ── Senate ─────────────────────────────────────────────────────────────
    ("Senator", "NM", "heinrich"): (
        "Introduced the GRID Savings Act (2026) — large electricity users pay "
        "for grid infrastructure; opposes moratoriums as a race to the bottom.",
        "sen_heinrich"),
    ("Senator", "VA", "warner"): (
        "Sponsored legislation so Virginians aren't stuck footing data-center "
        "utility costs, plus an energy/water disclosure bill.", "sen_warner"),
    ("Senator", "GA", "ossoff"): (
        "Launched an investigation into data centers' impact on Georgians' "
        "power bills.", "sen_ossoff"),
    ("Senator", "PA", "fetterman"): (
        "Blasted a proposed data-center moratorium as 'China First,' opposing "
        "the pause approach.", "sen_fetterman"),
    ("Senator", "MO", "hawley"): (
        "Co-introduced the GRID Act to stop data centers from raising Americans' "
        "electricity costs.", "sen_hawley"),
    ("Senator", "CT", "blumenthal"): (
        "Co-introduced the GRID Act to stop data centers from raising Americans' "
        "electricity costs.", "sen_hawley"),
    ("Senator", "VT", "welch"): (
        "Joined a bill to ensure Americans aren't footing the bill for big data "
        "centers.", "sen_welch"),
    ("Senator", "OH", "husted"): (
        "Leads a Senate bill to protect Americans from footing the bill for new "
        "data centers.", "sen_husted"),
    # ── Additional governors ───────────────────────────────────────────────
    ("Governor", "MI", "whitmer"): (
        "Proposed that data centers pledge to cover utility costs, protect the "
        "environment, and provide good-paying jobs.", "gov_whitmer"),
}


def stance_for(office: str, state: str, name: str):
    """(stance_text, src_key) for an official, or ("", "") if none on file."""
    nm = (name or "").lower()
    for (o, s, ln), val in STANCES.items():
        if o == office and s == state and ln in nm:
            return val
    return ("", "")
