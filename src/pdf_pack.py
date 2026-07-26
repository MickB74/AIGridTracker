"""
Action-pack PDF builder — renders the Start Here wizard's action pack as a
branded, print-ready PDF: logo + wordmark header on every page, teal section
headings, checkbox checklist, and a footer with page numbers and generation
date. Pure fpdf2, no Streamlit.

The logo is drawn natively (hexagon + pulse bolt) rather than embedding
assets/logo.svg — the SVG relies on gradients/filters that PDF importers
don't support, and its light-on-dark wordmark is unreadable on paper.

Core PDF fonts cover WinAnsi/cp1252 only, so all text passes through
_latin1() (kept name; it sanitizes to the cp1252 glyph set).
"""

from datetime import date

from fpdf import FPDF

# Print-friendly variants of the app palette (assets/style.css is dark-theme)
TEAL = (13, 148, 136)
AMBER = (217, 119, 6)
INK = (31, 41, 55)
MUTED = (100, 116, 139)
RULE = (203, 213, 225)

_MARGIN = 18  # mm

_CHAR_MAP = {"─": "-", "\xa0": " "}


def _latin1(text):
    """Make text safe for the core fonts (WinAnsi/cp1252 glyph set —
    covers em/en dashes, curly quotes, and bullets natively)."""
    for src, dst in _CHAR_MAP.items():
        text = text.replace(src, dst)
    # drop (not "?") anything outside the glyph set — emoji in social posts
    # should vanish on paper, not litter it with question marks
    return text.encode("cp1252", "ignore").decode("cp1252")


class _ActionPackPDF(FPDF):
    """Letter-format PDF with the GridWatch header and footer on every page."""

    def __init__(self, doc_title, doc_subtitle):
        super().__init__(orientation="portrait", unit="mm", format="letter")
        self.doc_title = _latin1(doc_title)
        self.doc_subtitle = _latin1(doc_subtitle)
        self.core_fonts_encoding = "cp1252"
        self.set_margins(_MARGIN, 32, _MARGIN)
        self.set_auto_page_break(auto=True, margin=22)
        self.alias_nb_pages()

    # -- logo -------------------------------------------------------------- #
    def _draw_logo_mark(self, cx, cy, r):
        """Hexagon grid + amber pulse bolt, scaled from assets/logo.svg."""
        s = r / 45.0
        hexagon = [(0, -45), (39, -22.5), (39, 22.5),
                   (0, 45), (-39, 22.5), (-39, -22.5)]
        pts = [(cx + x * s, cy + y * s) for x, y in hexagon]
        self.set_draw_color(*TEAL)
        self.set_line_width(0.45)
        for i in range(6):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % 6]
            self.line(x1, y1, x2, y2)
        for x, y in pts:
            self.set_fill_color(*TEAL)
            self.ellipse(x - 0.55, y - 0.55, 1.1, 1.1, "F")

        bolt = [(-6, -23), (3, -5), (-5, -5), (6, 23)]
        bpts = [(cx + x * s, cy + y * s) for x, y in bolt]
        self.set_draw_color(*AMBER)
        self.set_line_width(0.8)
        for i in range(len(bpts) - 1):
            x1, y1 = bpts[i]
            x2, y2 = bpts[i + 1]
            self.line(x1, y1, x2, y2)

    # -- chrome ------------------------------------------------------------ #
    def header(self):
        self._draw_logo_mark(_MARGIN + 6, 17, 6.5)

        x = _MARGIN + 16
        self.set_xy(x, 12)
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(*TEAL)
        self.cell(self.get_string_width("AI ") + 1, 6, "AI")
        self.set_text_color(*INK)
        self.cell(self.get_string_width("Grid"), 6, "Grid")
        self.set_text_color(*TEAL)
        self.cell(self.get_string_width("Watch") + 2, 6, "Watch")
        self.set_xy(x, 18.5)
        self.set_font("Helvetica", "", 6.5)
        self.set_text_color(*MUTED)
        self.cell(0, 3, "C O M M U N I T Y   E N E R G Y   I N T E L L I G E N C E")

        self.set_xy(_MARGIN, 12)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*MUTED)
        self.cell(0, 6, self.doc_title, align="R")
        self.set_xy(_MARGIN, 18)
        self.set_font("Helvetica", "", 8)
        self.cell(0, 4, self.doc_subtitle, align="R")

        self.set_draw_color(*TEAL)
        self.set_line_width(0.5)
        self.line(_MARGIN, 26.5, self.w - _MARGIN, 26.5)
        self.set_y(32)

    def footer(self):
        self.set_y(-16)
        self.set_draw_color(*RULE)
        self.set_line_width(0.2)
        self.line(_MARGIN, self.get_y(), self.w - _MARGIN, self.get_y())
        self.set_y(-13)
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(*MUTED)
        self.cell(0, 4, _latin1(
            "AI GridWatch — planning estimates, not engineering studies. "
            "Sources & methodology: Blog & methodology tab."))
        self.set_y(-13)
        self.set_x(_MARGIN)
        self.cell(0, 4, f"Page {self.page_no()} of {{nb}}", align="R")

    # -- body helpers -------------------------------------------------------#
    def _ensure_room(self, needed):
        """Break the page BEFORE starting a row that captures get_y() —
        otherwise the first cell can trigger the auto page break and the
        rest of the row lands at the stale y on the new page (orphaned
        number/bullet with its text a page later)."""
        if self.get_y() + needed > self.page_break_trigger:
            self.add_page()

    def section_title(self, title):
        if self.get_y() > self.h - 50:
            self.add_page()
        self.ln(3)
        self.set_font("Helvetica", "B", 10.5)
        self.set_text_color(*TEAL)
        self.cell(0, 6, _latin1(title.upper()), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*RULE)
        self.set_line_width(0.2)
        self.line(_MARGIN, self.get_y(), self.w - _MARGIN, self.get_y())
        self.ln(2)

    def kv_row(self, label, value):
        self._ensure_room(6)
        y = self.get_y()
        self.set_xy(_MARGIN, y)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*MUTED)
        self.cell(58, 5.2, _latin1(label))
        self.set_xy(_MARGIN + 58, y)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*INK)
        self.multi_cell(0, 5.2, _latin1(value))

    def bullet(self, text, indent=4):
        self._ensure_room(8)
        y = self.get_y()
        self.set_fill_color(*TEAL)
        self.ellipse(_MARGIN + indent - 3, y + 2.1, 1.3, 1.3, "F")
        self.set_xy(_MARGIN + indent, y)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*INK)
        self.multi_cell(0, 5.2, _latin1(text))
        self.ln(0.8)

    def numbered(self, n, text):
        self._ensure_room(8)
        y = self.get_y()
        self.set_xy(_MARGIN, y)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*TEAL)
        self.cell(7, 5.2, f"{n}.")
        self.set_xy(_MARGIN + 7, y)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*INK)
        self.multi_cell(0, 5.2, _latin1(text))
        self.ln(0.8)

    def checkbox_item(self, text):
        self._ensure_room(9)
        y = self.get_y()
        self.set_draw_color(*MUTED)
        self.set_line_width(0.3)
        self.rect(_MARGIN + 1, y + 0.9, 3.4, 3.4)
        self.set_xy(_MARGIN + 7, y)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*INK)
        self.multi_cell(0, 5.2, _latin1(text))
        self.ln(1.2)

    def paragraph(self, text, style="", size=9, color=INK):
        # multi_cell leaves x at the cell's right edge; a paragraph always
        # starts at the left margin, else back-to-back paragraphs get zero
        # width ("Not enough horizontal space").
        self.set_x(self.l_margin)
        self.set_font("Helvetica", style, size)
        self.set_text_color(*color)
        self.multi_cell(0, 5.2, _latin1(text), new_x="LMARGIN", new_y="NEXT")

    def rich_bullet(self, lead, rest, indent=4):
        """Bullet whose text starts with a bold lead-in ("Where (year): ...")."""
        self._ensure_room(10)
        y = self.get_y()
        self.set_fill_color(*TEAL)
        self.ellipse(_MARGIN + indent - 3, y + 2.1, 1.3, 1.3, "F")
        self.set_left_margin(_MARGIN + indent)
        self.set_xy(_MARGIN + indent, y)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*INK)
        self.write(5.2, _latin1(lead))
        self.set_font("Helvetica", "", 9)
        self.write(5.2, _latin1(rest))
        self.ln(5.2)
        self.set_left_margin(_MARGIN)
        self.set_x(_MARGIN)
        self.ln(1.2)

    def exec_entry(self, name, title, focus, linkedin):
        self._ensure_room(16)
        y = self.get_y()
        self.set_fill_color(*TEAL)
        self.ellipse(_MARGIN + 1, y + 2.1, 1.3, 1.3, "F")
        self.set_xy(_MARGIN + 4, y)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*INK)
        self.multi_cell(0, 5.2, _latin1(f"{name} — {title}"))
        if focus:
            self.set_x(_MARGIN + 4)
            self.set_font("Helvetica", "", 8.5)
            self.set_text_color(*MUTED)
            self.multi_cell(0, 4.6, _latin1(focus))
        if linkedin:
            self.set_x(_MARGIN + 4)
            self.set_font("Helvetica", "", 7.5)
            self.set_text_color(*TEAL)
            self.multi_cell(0, 4.2, _latin1(linkedin), link=linkedin)
        self.ln(1.6)

    def advice_block(self, advice):
        """MEETING_ADVICE strings: 'STRATEGY: ...' paragraph, 'KEY MOVES:'
        subheading, '  - ' bullet lines."""
        for raw in advice.split("\n"):
            line = raw.strip()
            if not line:
                self.ln(1.5)
            elif line.startswith("- "):
                self.bullet(line[2:])
            elif line.endswith(":") and len(line) < 30:
                self._ensure_room(12)
                self.set_font("Helvetica", "B", 9)
                self.set_text_color(*INK)
                self.cell(0, 5.2, _latin1(line), new_x="LMARGIN", new_y="NEXT")
            else:
                self.paragraph(line)


def build_action_pack_pdf(state, stage, stage_info, brief_data,
                          dated_moves=None, scripts=None, letters=None,
                          social_posts=None, outreach_tips=None):
    """Render the Start Here action pack. Returns PDF bytes.

    `stage`/`stage_info` come from PROJECT_STAGES; `brief_data` from
    build_meeting_brief_data(). Optional extras:
      - dated_moves:   [(due_str, move), ...] replaces the undated checklist
      - scripts:       build_comment_scripts() output
      - letters:       build_letters() output (each letter gets its own page)
      - social_posts:  build_social_posts() output
      - outreach_tips: OUTREACH_TIPS registry
    """
    pdf = _ActionPackPDF(
        doc_title="START-HERE ACTION PACK",
        doc_subtitle=f"{state} · {date.today():%B %d, %Y}",
    )
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*INK)
    pdf.cell(0, 9, "Your Action Pack", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(0, 5.2, _latin1(
        f"{state} · {brief_data['mw']} MW proposed · "
        f"operator: {brief_data['operator']} · "
        f"prepared for: {brief_data['meeting_type'].lower()}"))
    pdf.ln(1)

    pdf.section_title("Your situation")
    pdf.paragraph(stage, style="B")
    pdf.ln(1)
    pdf.paragraph(stage_info["headline"])

    if dated_moves:
        pdf.section_title("Your countdown checklist")
        for due, move in dated_moves:
            pdf.checkbox_item(f"By {due} — {move}")
    else:
        pdf.section_title("This week — your checklist")
        for move in stage_info["moves"]:
            pdf.checkbox_item(move)

    for sec in brief_data["sections"]:
        pdf.section_title(sec["title"])
        if sec["kind"] == "kv":
            for label, value in sec["items"]:
                pdf.kv_row(label, value)
        elif sec["kind"] == "bullets":
            for item in sec["items"]:
                pdf.bullet(item)
        elif sec["kind"] == "numbered":
            for i, item in enumerate(sec["items"], 1):
                pdf.numbered(i, item)
        elif sec["kind"] == "advice":
            pdf.advice_block(sec["text"])
        elif sec["kind"] == "execs":
            for ex in sec["items"]:
                pdf.exec_entry(ex["name"], ex["title"],
                               ex["focus"], ex["linkedin"])
        elif sec["kind"] == "concessions":
            pdf.paragraph(sec["pattern"], style="I", color=MUTED)
            pdf.ln(2)
            for c in sec["items"]:
                pdf.rich_bullet(f"{c['where']} ({c['year']}): ", c["what"])

    if scripts:
        pdf.section_title("Your 2-minute public comment")
        pdf.paragraph("Read at a normal pace this runs about two minutes. "
                      "Fill in your name, practice it once out loud, and "
                      "hand the board a printed copy.",
                      style="I", color=MUTED)
        pdf.ln(2)
        for para in scripts["main"].split("\n\n"):
            pdf.paragraph(para)
            pdf.ln(1.5)
        pdf.section_title("30-second topic scripts (divide the speakers)")
        for title, text in scripts["topics"]:
            pdf.rich_bullet(f"{title}: ", text)

    if social_posts or outreach_tips:
        pdf.section_title("Spread the word online")
        if social_posts:
            pdf.paragraph("Copy-paste posts — replace the [BRACKETS] and "
                          "post. Numbers are already filled in.",
                          style="I", color=MUTED)
            pdf.ln(2)
            for platform, post in social_posts.items():
                pdf._ensure_room(20)
                pdf.paragraph(platform, style="B")
                pdf.paragraph(post, color=MUTED)
                pdf.ln(2)
        if outreach_tips:
            pdf.paragraph("Platform playbook:", style="B")
            pdf.ln(1)
            for entry in outreach_tips:
                pdf._ensure_room(16)
                pdf.paragraph(entry["platform"], style="B")
                for tip in entry["tips"]:
                    pdf.bullet(tip)
                pdf.ln(1)

    if letters:
        for letter in letters:
            pdf.add_page()
            pdf.section_title(f"Ready to send — {letter['title']}")
            pdf.kv_row("To", letter["to"])
            pdf.kv_row("Re", letter["re"])
            pdf.ln(2)
            for para in letter["body"].split("\n\n"):
                for line in para.split("\n"):
                    pdf.paragraph(line)
                pdf.ln(2)

    return bytes(pdf.output())


# ---------------------------------------------------------------------- #
# Community flyer + petition sheet
# ---------------------------------------------------------------------- #

_FLYER_STRINGS = {
    "en": {
        "doc_title": "COMMUNITY FACT SHEET",
        "headline": "A {mw} MW data center is proposed near you",
        "sub": "What it means for {state} households — planning estimates "
               "with sources at the link below.",
        "stat_power": "homes' worth of electricity",
        "stat_water": "gallons of water per year",
        "stat_bill": "per household per year if WE fund the grid upgrades",
        "stat_cba": "per year — the community benefit agreement to ask for",
        "asks_title": "What we're asking for — before any approval",
        "asks": [
            "A binding community benefit agreement (~{cba}/year), recorded "
            "as a condition of approval — not a side letter",
            "The developer pays 100% of grid upgrades, so they never "
            "appear on our electric bills",
            "An enforceable water cap, a 45 dBA noise limit at homes, and "
            "quarterly public reporting",
        ],
        "meeting_title": "Show up — decisions are made by those in the room",
        "learn": "Fact sources & tools: GridWatch AI — ask the person who "
                 "shared this sheet for the link.",
        "petition_title": "Petition — conditions before approval",
        "petition_body": "We, the undersigned residents, ask our elected "
                         "officials to require a binding community benefit "
                         "agreement, developer-funded grid upgrades, and "
                         "enforceable water and noise limits as conditions "
                         "of any data center approval near {state_loc}.",
        "cols": ["#", "Name", "Street address", "Email", "Phone",
                 "Signature"],
    },
    "es": {
        "doc_title": "HOJA INFORMATIVA COMUNITARIA",
        "headline": "Se propone un centro de datos de {mw} MW cerca de usted",
        "sub": "Lo que significa para los hogares de {state} — estimaciones "
               "de planificación con fuentes en el enlace de abajo.",
        "stat_power": "hogares en consumo de electricidad",
        "stat_water": "galones de agua al año",
        "stat_bill": "por hogar al año si NOSOTROS pagamos las mejoras "
                     "de la red",
        "stat_cba": "al año — el acuerdo de beneficios comunitarios que "
                    "debemos exigir",
        "asks_title": "Lo que pedimos — antes de cualquier aprobación",
        "asks": [
            "Un acuerdo de beneficios comunitarios vinculante (~{cba}/año), "
            "registrado como condición de la aprobación — no una carta "
            "aparte",
            "Que el desarrollador pague el 100% de las mejoras de la red, "
            "para que nunca aparezcan en nuestras facturas de luz",
            "Un límite de agua exigible, un límite de ruido de 45 dBA en "
            "las viviendas y reportes públicos trimestrales",
        ],
        "meeting_title": "Asista — las decisiones las toman los presentes",
        "learn": "Fuentes y herramientas: GridWatch AI — pida el enlace a "
                 "quien le compartió esta hoja.",
        "petition_title": "Petición — condiciones antes de aprobar",
        "petition_body": "Nosotros, los residentes abajo firmantes, pedimos "
                         "a nuestros funcionarios electos que exijan un "
                         "acuerdo de beneficios comunitarios vinculante, "
                         "mejoras de red pagadas por el desarrollador y "
                         "límites exigibles de agua y ruido como condiciones "
                         "de cualquier aprobación de un centro de datos "
                         "cerca de {state_loc}.",
        "cols": ["#", "Nombre", "Dirección", "Correo", "Teléfono", "Firma"],
    },
}


def build_flyer_pdf(state, mw, imp, upgrade_per_home_yr,
                    meeting_when="", meeting_where="", lang="en"):
    """One-page hand-out flyer + petition/sign-up sheet. Returns PDF bytes.

    `imp` is estimate_facility_impact() output; `meeting_when`/`where` are
    free-text (already formatted). lang: "en" or "es".
    """
    s = _FLYER_STRINGS.get(lang, _FLYER_STRINGS["en"])
    cba_str = f"${imp['data_dividend_usd'] / 1e6:.1f}M"

    pdf = _ActionPackPDF(
        doc_title=s["doc_title"],
        doc_subtitle=f"{state} · {date.today():%B %d, %Y}",
    )
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 19)
    pdf.set_text_color(*INK)
    pdf.set_x(_MARGIN)
    pdf.multi_cell(0, 8.5, _latin1(s["headline"].format(mw=mw)), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(*MUTED)
    pdf.set_x(_MARGIN)
    pdf.multi_cell(0, 5.2, _latin1(s["sub"].format(state=state)), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # 2x2 stat grid
    stats = [
        (f"{imp['homes_equiv']:,.0f}", s["stat_power"]),
        (f"{imp['annual_water_mgal']:,.0f}M", s["stat_water"]),
        (f"${upgrade_per_home_yr:,.0f}", s["stat_bill"]),
        (cba_str, s["stat_cba"]),
    ]
    col_w = (pdf.w - 2 * _MARGIN - 8) / 2
    row_h = 30
    top = pdf.get_y()
    for i, (big, label) in enumerate(stats):
        x = _MARGIN + (i % 2) * (col_w + 8)
        y = top + (i // 2) * (row_h + 5)
        pdf.set_draw_color(*RULE)
        pdf.set_line_width(0.3)
        pdf.rect(x, y, col_w, row_h, "D")
        pdf.set_xy(x + 5, y + 5)
        pdf.set_font("Helvetica", "B", 21)
        pdf.set_text_color(*TEAL)
        pdf.cell(col_w - 10, 9, _latin1(big))
        pdf.set_xy(x + 5, y + 15.5)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(*INK)
        pdf.multi_cell(col_w - 10, 4.2, _latin1(label))
    pdf.set_y(top + 2 * row_h + 5 + 6)

    pdf.section_title(s["asks_title"])
    for ask in s["asks"]:
        pdf.bullet(ask.format(cba=cba_str))

    # meeting box
    pdf.ln(3)
    box_y = pdf.get_y()
    box_h = 26
    pdf.set_draw_color(*TEAL)
    pdf.set_line_width(0.6)
    pdf.rect(_MARGIN, box_y, pdf.w - 2 * _MARGIN, box_h, "D")
    pdf.set_xy(_MARGIN + 5, box_y + 4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*TEAL)
    pdf.cell(0, 6, _latin1(s["meeting_title"]))
    pdf.set_xy(_MARGIN + 5, box_y + 12)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*INK)
    when = meeting_when if meeting_when else "[DATE & TIME]"
    where = meeting_where if meeting_where else "[LOCATION]"
    pdf.multi_cell(pdf.w - 2 * _MARGIN - 10, 6, _latin1(f"{when} — {where}"))
    pdf.set_y(box_y + box_h + 4)

    pdf.set_font("Helvetica", "I", 8.5)
    pdf.set_text_color(*MUTED)
    pdf.set_x(_MARGIN)
    pdf.multi_cell(0, 4.6, _latin1(s["learn"]), new_x="LMARGIN", new_y="NEXT")

    # -- petition / sign-up sheet ---------------------------------------- #
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(*INK)
    pdf.set_x(_MARGIN)
    pdf.multi_cell(0, 7, _latin1(s["petition_title"]), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_x(_MARGIN)
    pdf.multi_cell(0, 5.2, _latin1(
        s["petition_body"].format(state_loc=f"[{'CIUDAD' if lang == 'es' else 'TOWN'}], {state}")))
    pdf.ln(4)

    widths = [9, 38, 50, 40, 23, 20]
    header_h, row_h = 8, 11
    x0, y0 = _MARGIN, pdf.get_y()
    # rect() doesn't auto-paginate — fit rows to the space above the footer
    n_rows = int((pdf.page_break_trigger - y0 - header_h - 2) // row_h)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(*INK)
    pdf.set_draw_color(*MUTED)
    pdf.set_line_width(0.25)
    x = x0
    for w, col in zip(widths, s["cols"]):
        pdf.rect(x, y0, w, header_h, "D")
        pdf.set_xy(x + 1.5, y0 + 2)
        pdf.cell(w - 3, 4, _latin1(col))
        x += w
    for r in range(n_rows):
        y = y0 + header_h + r * row_h
        x = x0
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*MUTED)
        for ci, w in enumerate(widths):
            pdf.rect(x, y, w, row_h, "D")
            if ci == 0:
                pdf.set_xy(x + 1.5, y + 3.5)
                pdf.cell(w - 3, 4, str(r + 1))
            x += w

    return bytes(pdf.output())


# ---------------------------------------------------------------------- #
# Health-risks infographic (format inspired by EHP's "Health Risks of
# Data Centers"; see SOURCES["ehp_health"])
# ---------------------------------------------------------------------- #

def _hex_rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def build_health_pdf(health_risks, sources):
    """Infographic: page 1 is a six-panel color grid, then one page per
    risk with sourced facts and a "what to demand" box.

    `health_risks` is the HEALTH_RISKS registry; `sources` is SOURCES
    (used to print the citation name + URL under each fact).
    """
    pdf = _ActionPackPDF(
        doc_title="THE HEALTH RISKS OF DATA CENTERS",
        doc_subtitle=f"Community briefing · {date.today():%B %d, %Y}",
    )
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 19)
    pdf.set_text_color(*INK)
    pdf.cell(0, 9, "The Health Risks of Data Centers",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(0, 5.2, _latin1(
        "Six ways a data center affects the people who live near one — "
        "every claim sourced on the pages that follow, with the permit "
        "condition that addresses it."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # 2-column x 3-row panel grid
    col_w = (pdf.w - 2 * _MARGIN - 6) / 2
    row_h = 56
    top = pdf.get_y()
    for i, risk in enumerate(health_risks):
        x = _MARGIN + (i % 2) * (col_w + 6)
        y = top + (i // 2) * (row_h + 5)
        r, g, b = _hex_rgb(risk["color"])
        pdf.set_fill_color(r, g, b)
        pdf.rect(x, y, col_w, row_h, "F")
        pdf.set_xy(x + 5, y + 5)
        pdf.set_font("Helvetica", "B", 12.5)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(col_w - 10, 6, _latin1(risk["title"]))
        pdf.set_xy(x + 5, y + 13.5)
        pdf.set_font("Helvetica", "", 8.8)
        pdf.multi_cell(col_w - 10, 4.4, _latin1(risk["summary"]))

    # detail pages
    for risk in health_risks:
        pdf.add_page()
        r, g, b = _hex_rgb(risk["color"])
        band_y = pdf.get_y()
        pdf.set_fill_color(r, g, b)
        pdf.rect(_MARGIN, band_y, pdf.w - 2 * _MARGIN, 12, "F")
        pdf.set_xy(_MARGIN + 5, band_y + 3)
        pdf.set_font("Helvetica", "B", 12.5)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 6, _latin1(risk["title"].upper()))
        pdf.set_y(band_y + 16)

        for fact in risk["facts"]:
            pdf._ensure_room(20)
            pdf.bullet(fact["text"])
            src_name, src_url = sources.get(fact["src"], ("", ""))
            if src_name:
                pdf.set_x(_MARGIN + 4)
                pdf.set_font("Helvetica", "I", 7.5)
                pdf.set_text_color(*MUTED)
                pdf.multi_cell(0, 3.8, _latin1(f"Source: {src_name}"),
                               new_x="LMARGIN", new_y="NEXT")
                pdf.set_x(_MARGIN + 4)
                pdf.set_font("Helvetica", "", 7)
                pdf.set_text_color(*TEAL)
                pdf.multi_cell(0, 3.6, _latin1(src_url), link=src_url,
                               new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

        pdf._ensure_room(26)
        pdf.ln(2)
        box_y = pdf.get_y()
        pdf.set_draw_color(*TEAL)
        pdf.set_line_width(0.5)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*TEAL)
        pdf.set_xy(_MARGIN + 5, box_y + 4)
        pdf.cell(0, 5, "WHAT TO DEMAND")
        pdf.set_xy(_MARGIN + 5, box_y + 10)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*INK)
        pdf.multi_cell(pdf.w - 2 * _MARGIN - 10, 5.0, _latin1(risk["ask"]),
                       new_x="LMARGIN", new_y="NEXT")
        box_h = pdf.get_y() - box_y + 4
        pdf.rect(_MARGIN, box_y, pdf.w - 2 * _MARGIN, box_h, "D")
        pdf.set_y(box_y + box_h + 2)

    return bytes(pdf.output())
