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
    # Power for the People Act — Welch/Van Hollen's release (2026-01-22) names
    # the cosponsors; Warner joined 2026-06-02 (his own release). One action,
    # one source, one score each — the same bill Welch is graded on.
    ("Senator", "MD", "van hollen"): (
        "Co-led the Power for the People Act with Welch: data-center operators "
        "pay the infrastructure and energy costs they create instead of "
        "ratepayers.", "sen_welch"),
    ("Senator", "NJ", "booker"): (
        "Cosponsored the Power for the People Act, making data-center operators "
        "pay the grid costs they create.", "sen_welch"),
    ("Senator", "IL", "duckworth"): (
        "Cosponsored the Power for the People Act, making data-center operators "
        "pay the grid costs they create.", "sen_welch"),
    ("Senator", "MN", "smith"): (
        "Cosponsored the Power for the People Act, making data-center operators "
        "pay the grid costs they create.", "sen_welch"),
    ("Senator", "MD", "alsobrooks"): (
        "Cosponsored the Power for the People Act, making data-center operators "
        "pay the grid costs they create.", "sen_welch"),
    # Researched 2026-09-05 (see src/senator_records.py for the full items)
    ("Senator", "MA", "markey"): (
        "Led letters to ISO New England and to NARUC on shielding ratepayers "
        "from data-center costs; released a draft bill requiring a federal "
        "public-interest certificate before a data center is permitted.",
        "sen_markey"),
    ("Senator", "MA", "warren"): (
        "Opened an investigation into whether Big Tech data centers raise "
        "families' utility bills and, with Hawley, secured mandatory EIA "
        "energy-use reporting for data centers.", "sen_warren"),
    ("Senator", "KS", "marshall"): (
        "Introduced a resolution backing the Ratepayer Protection Pledge — "
        "tech companies pay their own grid costs — and opposes tax incentives "
        "for data centers.", "sen_marshall"),
    ("Senator", "MS", "hyde-smith"): (
        "Pressed FERC commissioners at oversight to make large loads such as "
        "data centers pay upfront so residential rates do not rise.",
        "sen_hydesmith"),
    ("Senator", "NH", "shaheen"): (
        "Signed the New England senators' letter asking ISO New England how it "
        "will protect residential ratepayers from data-center-driven price "
        "increases.", "sen_shaheen"),
    ("Senator", "IL", "durbin"): (
        "Cosponsored the Power for the People Act and introduced the Data "
        "Center Water and Energy Transparency Act (S. 4213).", "sen_durbin"),
    ("Senator", "OR", "wyden"): (
        "Demanded answers from Google, Apple, Meta and Amazon on data-center "
        "water use in Oregon, and proposed stripping data centers of federal "
        "investment incentives plus a new excise tax.", "sen_wyden"),
    ("Senator", "RI", "whitehouse"): (
        "Co-led the New England senators' letter to ISO New England on "
        "data-center-driven rate increases; earlier urged the White House not to "
        "fast-track data centers past clean-air, water and cost protections.",
        "sen_whitehouse"),
    ("Senator", "RI", "reed"): (
        "Co-led the New England senators' letter asking ISO New England how it "
        "will shield residential ratepayers from data-center-driven price "
        "increases.", "sen_reed"),
    ("Senator", "OR", "merkley"): (
        "With Wyden, wrote Oregon's data center advisory committee listing "
        "constituent concerns on energy demand, consumer costs, water, noise and "
        "farmland.", "sen_merkley"),
    ("Senator", "NJ", "kim"): (
        "Co-led the NJ delegation's letter pressing PJM on the data-center-driven "
        "capacity price increase behind a ~17% rate rise.", "sen_kim"),
    ("Senator", "VT", "sanders"): (
        "Introduced the AI Data Center Moratorium Act (S. 4214) with Rep. "
        "Ocasio-Cortez: no new or expanded AI data centers until federal "
        "safeguards, including against higher utility costs, are in place.",
        "sen_sanders"),
    ("Senator", "TN", "blackburn"): (
        "Released the TRUMP AMERICA AI Act discussion draft, which would make "
        "data-center operators responsible for the full cost of energy and water "
        "infrastructure with no impact on ratepayers.", "sen_blackburn"),
    ("Senator", "UT", "lee"): (
        "As Energy Committee chair, backed FERC's Large Load Order at oversight "
        "and agreed existing ratepayers should not subsidize data centers; says "
        "data-center legislation is not currently a priority.", "sen_lee"),
    ("Senator", "CA", "schiff"): (
        "Introduced the Energy Cost Fairness and Reliability Act: large loads "
        "such as data centers pay 100% of the grid upgrades needed to serve them "
        "and bring their own generation before connecting.", "sen_schiff"),
    ("Senator", "GA", "warnock"): (
        "Led a letter to FERC to shield households from data-center costs, "
        "secured $50M for communities facing data-center energy and water "
        "demands, and called for a Georgia data-center pause.", "sen_warnock"),
    ("Senator", "AZ", "kelly"): (
        "Co-signed a letter asking FERC to convene a technical conference on "
        "data-center load and affordable rates; previewed legislation to bring "
        "communities into siting with enforceable commitments.", "sen_kelly"),
    ("Senator", "FL", "scott"): (
        "Introduced, with Marshall, a resolution endorsing the Ratepayer "
        "Protection Pledge: tech companies pay their own electricity and "
        "grid-infrastructure costs.", "sen_rickscott"),
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
