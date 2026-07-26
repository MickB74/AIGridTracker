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
    return text.encode("cp1252", "replace").decode("cp1252")


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
        self.set_font("Helvetica", style, size)
        self.set_text_color(*color)
        self.multi_cell(0, 5.2, _latin1(text))

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


def build_action_pack_pdf(state, stage, stage_info, brief_data):
    """Render the Start Here action pack. Returns PDF bytes.

    `stage`/`stage_info` come from PROJECT_STAGES; `brief_data` from
    build_meeting_brief_data().
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

    return bytes(pdf.output())
