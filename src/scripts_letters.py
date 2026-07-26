"""
Public-comment scripts and ready-to-send letters for the Start Here wizard.
Pure text assembly, no Streamlit. Numbers come from the shared impact model
via the caller (never recompute coefficients here).

Scripts are available in English and Spanish ("en"/"es"); letters are
English-only (they go to English-speaking agencies).
"""


def build_comment_scripts(state, mw, imp, upgrade_per_home_yr,
                          operator="Unknown / not listed", lang="en"):
    """Returns {"main": 2-minute script, "topics": [(title, 30s script), ...]}."""
    homes = f"{imp['homes_equiv']:,.0f}"
    twh = f"{imp['annual_twh']:.1f}"
    water = f"{imp['annual_water_mgal']:,.0f}"
    bill = f"{upgrade_per_home_yr:.0f}"
    cba = f"{imp['data_dividend_usd'] / 1e6:.1f}"
    op_clause = (
        "" if operator == "Unknown / not listed"
        else f" backed by {operator}" if lang == "en"
        else f" respaldado por {operator}")

    if lang == "es":
        main = (
            f"Buenas noches. Me llamo ____________ y vivo en esta comunidad.\n\n"
            f"Estoy aquí por el centro de datos de {mw} MW que se propone"
            f"{op_clause}. Tres números merecen su atención esta noche.\n\n"
            f"Primero, la electricidad. A plena capacidad, esta sola "
            f"instalación consumiría unos {twh} TWh al año — tanta "
            f"electricidad como {homes} hogares.\n\n"
            f"Segundo, el agua: aproximadamente {water} millones de galones "
            f"al año para enfriamiento.\n\n"
            f"Tercero, el costo. Si esta junta no exige que el desarrollador "
            f"pague las mejoras de la red eléctrica, terminarán en nuestras "
            f"facturas — cerca de ${bill} por hogar al año.\n\n"
            f"Las comunidades que se organizaron lograron protecciones "
            f"reales: The Dalles obtuvo de Google un sistema de agua de "
            f"$29 millones; Groton hizo de un acuerdo de beneficios "
            f"comunitarios de $2.5 millones una condición de zonificación.\n\n"
            f"No pedimos que rechacen el desarrollo. Pedimos condiciones: "
            f"(1) un acuerdo de beneficios comunitarios vinculante de al "
            f"menos ${cba} millones al año; (2) que el desarrollador pague "
            f"el 100% de las mejoras de la red; (3) límites de agua "
            f"exigibles y reportes públicos.\n\n"
            f"Una aprobación sin condiciones es un subsidio. Por favor, no "
            f"firmen nuestros nombres en él. Gracias."
        )
        topics = [
            ("Tarifas eléctricas",
             f"Soy cliente residencial. Las mejoras de red para una "
             f"instalación de {mw} MW cuestan millones, y sin una orden de "
             f"esta junta se reparten entre todos nosotros — unos ${bill} "
             f"por hogar al año. Pido una sola condición: que el "
             f"desarrollador pague el 100% de las mejoras que causa. Eso es "
             f"causalidad de costos, y otros estados ya lo exigen."),
            ("Agua",
             f"Esta instalación evaporaría unos {water} millones de galones "
             f"al año. Pido tres condiciones: un límite de agua exigible en "
             f"el permiso, medición pública trimestral, y que la expansión "
             f"requiera nueva aprobación. The Dalles logró que Google "
             f"pagara $29 millones en infraestructura de agua — nosotros no "
             f"deberíamos aceptar menos transparencia."),
            ("Responsabilidad",
             f"¿Qué pasa si esta instalación cierra en diez años? Pido una "
             f"fianza de desmantelamiento de ${mw * 10_000 / 1e6:.1f} "
             f"millones como condición del permiso, y un acuerdo de "
             f"beneficios comunitarios vinculante — no una carta de "
             f"intención — de al menos ${cba} millones al año. Si el "
             f"proyecto es tan bueno como dicen, ponerlo por escrito no "
             f"debería ser un problema."),
        ]
        return {"main": main, "topics": topics}

    main = (
        f"Good evening. My name is ____________, and I live in this "
        f"community.\n\n"
        f"I'm here about the proposed {mw} MW data center{op_clause}. "
        f"Three numbers deserve your attention tonight.\n\n"
        f"First, electricity. At full build-out this single facility would "
        f"draw about {twh} TWh a year — as much electricity as {homes} "
        f"homes.\n\n"
        f"Second, water: roughly {water} million gallons a year for "
        f"cooling.\n\n"
        f"Third, cost. Unless this board requires the developer to pay for "
        f"grid upgrades, they land on our bills — about ${bill} per "
        f"household per year.\n\n"
        f"Communities that organized won real protections: The Dalles got "
        f"a $29 million water system funded by Google; Groton made a $2.5 "
        f"million community benefit agreement a condition of zoning.\n\n"
        f"We are not asking you to reject growth. We are asking you to "
        f"attach conditions: (1) a binding community benefit agreement of "
        f"at least ${cba} million per year; (2) the developer pays 100% of "
        f"grid upgrades; (3) enforceable water caps with public "
        f"reporting.\n\n"
        f"Approval without conditions is a subsidy. Please don't sign our "
        f"names to it. Thank you."
    )
    topics = [
        ("Electric rates",
         f"I'm a residential ratepayer. Grid upgrades for a {mw} MW "
         f"facility cost millions, and without an order from this board "
         f"they are spread across all of us — about ${bill} per household "
         f"per year. I'm asking for one condition: the developer pays 100% "
         f"of the upgrades it causes. That's cost causation, and other "
         f"states already require it."),
        ("Water",
         f"This facility would evaporate roughly {water} million gallons a "
         f"year. I'm asking for three conditions: an enforceable water cap "
         f"in the permit, quarterly public metering, and re-approval "
         f"before any expansion. The Dalles got Google to fund $29 million "
         f"of water infrastructure — we should not accept less "
         f"transparency."),
        ("Accountability",
         f"What happens if this facility closes in ten years? I'm asking "
         f"for a ${mw * 10_000 / 1e6:.1f} million decommissioning bond as "
         f"a permit condition, and a binding community benefit agreement — "
         f"not a letter of intent — of at least ${cba} million per year. "
         f"If the project is as good as promised, putting it in writing "
         f"should be no problem."),
    ]
    return {"main": main, "topics": topics}


def build_social_posts(state, mw, imp, upgrade_per_home_yr,
                       operator="Unknown / not listed", hearing_str=""):
    """Ready-to-paste posts, keyed by platform. Numbers pre-filled;
    [BRACKETS] mark the spots the user personalizes."""
    homes = f"{imp['homes_equiv']:,.0f}"
    water = f"{imp['annual_water_mgal']:,.0f}"
    bill = f"{upgrade_per_home_yr:.0f}"
    op_bit = ("" if operator == "Unknown / not listed"
              else f" (operator: {operator})")
    when = hearing_str if hearing_str else "[DATE/TIME]"

    nextdoor = (
        f"Heads up, neighbors — a {mw} MW data center has been proposed "
        f"near [LOCATION]{op_bit}. That's a facility drawing as much "
        f"electricity as {homes} homes and evaporating ~{water}M gallons "
        f"of water a year. Unless the developer is required to pay for "
        f"grid upgrades, the cost lands on our bills (~${bill}/household/"
        f"yr). There's a public meeting on {when} — showing up is the "
        f"single most effective thing we can do. I have a one-page fact "
        f"sheet with sources; comment or message me and I'll share it."
    )
    ring = (
        f"Community alert: a large data center ({mw} MW) is proposed near "
        f"[LOCATION]. Public meeting {when}. It affects local electric "
        f"bills and water use. Reply for a one-page fact sheet — decisions "
        f"are being made now."
    )
    facebook = (
        f"🚨 [TOWN] — a {mw} MW data center is proposed near [LOCATION]"
        f"{op_bit}.\n\n"
        f"What that means, with sources:\n"
        f"⚡ Electricity: as much as {homes} homes\n"
        f"💧 Water: ~{water}M gallons/year for cooling\n"
        f"💸 Your bill: ~${bill}/household/year IF ratepayers fund the "
        f"grid upgrades\n\n"
        f"Communities that organized won real protections — The Dalles got "
        f"Google to fund a $29M water system; Groton made a $2.5M benefit "
        f"agreement a zoning condition. We can too, but only BEFORE "
        f"approval.\n\n"
        f"🗓️ Public meeting: {when} at [LOCATION]\n"
        f"✅ Comment 'INFO' and I'll send the fact sheet + 3 asks\n"
        f"Please share to [TOWN] groups."
    )
    return {"Nextdoor": nextdoor, "Ring Neighbors": ring,
            "Facebook": facebook}


def build_letters(state, operator, mw, puc_name, puc_complaint):
    """Three ready-to-send letters. Returns a list of dicts:
    {"title", "to", "re", "body"} — body is plain text with [BRACKETED]
    placeholders the user fills in."""
    op_ref = ("the proposed data center development"
              if operator == "Unknown / not listed"
              else f"the proposed {operator} data center development")

    records = {
        "title": "Public records request — planning department",
        "to": "Records Officer, [Town/County] Planning Department",
        "re": f"Public records request — {op_ref}",
        "body": (
            f"To whom it may concern:\n\n"
            f"Under {state}'s public records law, I request copies of the "
            f"following records from the past 24 months:\n\n"
            f"1. All applications, site plans, studies, and permits "
            f"referencing [PARCEL NUMBER / LLC NAME / PROJECT NAME];\n"
            f"2. Minutes, notes, presentations, or correspondence from any "
            f"pre-application or economic-development meetings concerning "
            f"a data center or large electric load;\n"
            f"3. Any water or sewer will-serve letters, capacity studies, "
            f"or utility correspondence for the parcel(s) above;\n"
            f"4. Any proposed or executed tax abatement, incentive, or "
            f"non-disclosure agreements related to the project.\n\n"
            f"I ask that fees be waived because this request concerns a "
            f"matter of significant public interest and is not for "
            f"commercial use. If any portion of this request is denied, "
            f"please cite the specific statutory exemption and release all "
            f"segregable portions.\n\n"
            f"Please confirm receipt of this request and the expected "
            f"response date.\n\n"
            f"Sincerely,\n[NAME]\n[STREET ADDRESS]\n[EMAIL / PHONE]"
        ),
    }

    puc = {
        "title": "Inquiry to your public utility commission",
        "to": puc_name,
        "re": f"Large-load interconnection inquiry — {op_ref} "
              f"(approx. {mw} MW)",
        "body": (
            f"Dear Commission staff:\n\n"
            f"I am a residential ratepayer in [CITY/COUNTY], {state}. A "
            f"data center of approximately {mw} MW has been proposed in my "
            f"community, and I request the Commission's help with the "
            f"following:\n\n"
            f"1. Has any utility filed a large-load interconnection "
            f"request, special contract, or will-serve commitment that "
            f"would serve this project? If so, please provide docket "
            f"numbers.\n"
            f"2. Has a residential rate impact analysis been performed for "
            f"the associated transmission and distribution upgrades?\n"
            f"3. What is the procedure for residents to intervene or "
            f"comment in any related proceeding, and what are the current "
            f"deadlines?\n\n"
            f"I would appreciate a response in writing. Thank you for your "
            f"assistance.\n\n"
            f"Sincerely,\n[NAME]\n[STREET ADDRESS]\n[EMAIL / PHONE]\n\n"
            f"(Consumer complaint portal, for reference: {puc_complaint})"
        ),
    }

    council = {
        "title": "Public comment letter — council / board",
        "to": "[Council members / Planning board], [Town/County]",
        "re": f"Conditions requested before any approval of {op_ref}",
        "body": (
            f"Dear members of the board:\n\n"
            f"I am writing about the proposed {mw} MW data center. I am "
            f"not asking you to reject growth — I am asking you to attach "
            f"binding conditions before any approval, as other "
            f"communities have successfully done:\n\n"
            f"1. A community benefit agreement, recorded as a condition of "
            f"approval rather than a side letter;\n"
            f"2. Cost causation: the developer pays 100% of substation and "
            f"transmission upgrades, so they do not appear on residential "
            f"bills;\n"
            f"3. An enforceable water cap with quarterly public reporting;\n"
            f"4. A noise limit of 45 dBA at the nearest residential "
            f"property line, measured, not modeled;\n"
            f"5. A decommissioning bond so the site is not abandoned "
            f"scrap if the operator leaves.\n\n"
            f"Precedents: The Dalles, OR secured $29M in water "
            f"infrastructure from Google; Groton, CT made a $2.5M CBA a "
            f"zoning condition. Communities that asked, received; "
            f"communities that didn't, paid.\n\n"
            f"I ask that this letter be entered into the public record.\n\n"
            f"Respectfully,\n[NAME]\n[STREET ADDRESS]"
        ),
    }
    return [records, puc, council]
