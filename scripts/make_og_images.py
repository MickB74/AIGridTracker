"""Generate per-page OG card images into assets/og/ (committed).

LOCAL-ONLY tool — requires Pillow, which is deliberately NOT in
requirements-build.txt. This never runs in CI: generated binaries that differ
per-environment cause the exact rebuild-commit loop the fpdf2 pin in
requirements-build.txt exists to prevent. Instead the PNGs are committed as
static assets and build_site.py copies them verbatim, which is deterministic.

Run it again whenever the baked-in numbers drift (state fight counts, tracker
totals):

    python3 scripts/make_og_images.py

Cards are 1200x630 (the OG standard), dark theme matching the site.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "og"
sys.path.insert(0, str(ROOT))

from src.constants import (  # noqa: E402
    MORATORIUMS_DF, STATE_GRID_PROFILES, STATE_PUCS_DF, STATE_DC_DF,
)

W, H = 1200, 630
BG = (11, 18, 32)        # --bg  #0b1220
CARD = (18, 28, 48)      # --card #121c30
INK = (234, 240, 247)    # --ink #eaf0f7
MUTED = (147, 161, 181)  # --muted #93a1b5
TEAL = (45, 212, 191)    # --teal #2dd4bf
AMBER = (251, 191, 36)   # --amber #fbbf24

_FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def _font(size, bold=True):
    for p in _FONT_CANDIDATES:
        if "Bold" in p and not bold:
            continue
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    # Non-bold fallback: retry any candidate.
    for p in _FONT_CANDIDATES:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def card(title, stat=None, stat_label=None, kicker="AI GridWatch",
         sub="aigridwatch.com — sourced tools for communities"):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Teal accent bar down the left edge — echoes the site's kicker styling.
    d.rectangle([0, 0, 14, H], fill=TEAL)

    # Kicker
    d.text((70, 64), kicker.upper(), font=_font(30), fill=TEAL)

    # Title, wrapped
    tf = _font(72)
    y = 130
    for line in _wrap(d, title, tf, W - 140)[:4]:
        d.text((70, y), line, font=tf, fill=INK)
        y += 88

    # Stat block
    if stat:
        y = max(y + 24, 400)
        d.text((70, y), str(stat), font=_font(64), fill=AMBER)
        if stat_label:
            sw = d.textlength(str(stat), font=_font(64))
            d.text((70 + sw + 24, y + 22), stat_label, font=_font(34, bold=False),
                   fill=MUTED)

    # Footer
    d.rectangle([0, H - 78, W, H], fill=CARD)
    d.text((70, H - 58), sub, font=_font(28, bold=False), fill=MUTED)
    return img


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0

    # --- Key pages -------------------------------------------------------
    total = len(MORATORIUMS_DF)
    n_states = MORATORIUMS_DF["state"].nunique()
    key_pages = {
        "moratoriums": card(
            "Data center moratoriums & community pushback",
            f"{total} tracked", f"actions across {n_states} states"),
        "communities": card(
            "Data center fights, town by town",
            f"{total} briefings", "status, sources, next steps"),
        "impact": card(
            "What does a data center cost your community?",
            "Free calculator", "electricity · water · carbon · rates"),
        "bills": card(
            "Why your electric bill is going up",
            "Capacity markets", "peak load & cost-shifting, sourced"),
        "health-risks": card(
            "The health risks of data centers",
            "6 risks", "every claim sourced"),
        "hearing-questions": card(
            "Questions to ask at your next hearing",
            "23 questions", "force answers onto the record"),
        "cba-clauses": card(
            "Model CBA clauses communities have won",
            "Copy-paste", "community benefit agreement language"),
        "dividend": card(
            "The data dividend your town could negotiate",
            "The Alaska model", "for data centers"),
    }
    for name, img in key_pages.items():
        img.save(OUT / f"{name}.png", optimize=True)
        n += 1

    # --- State pages -----------------------------------------------------
    abbr = dict(zip(STATE_PUCS_DF["state"], STATE_PUCS_DF["abbrev"]))
    for state in sorted(STATE_GRID_PROFILES):
        ab = abbr.get(state, "")
        fights = int((MORATORIUMS_DF["state"] == ab).sum())
        row = STATE_DC_DF[STATE_DC_DF["state"] == state]
        dcs = int(row.iloc[0]["dc_count"]) if not row.empty else 0
        stat, label = ((f"{fights} fight{'s' if fights != 1 else ''} tracked",
                        f"· {dcs} data centers") if fights
                       else (f"{dcs} data centers",
                             "rates · grid carbon · water stress"))
        slug = state.lower().replace(" ", "-")
        card(f"{state}: data center community briefing", stat, label).save(
            OUT / f"state-{slug}.png", optimize=True)
        n += 1

    print(f"wrote {n} OG cards -> {OUT.relative_to(ROOT)}/")
    print("Commit them, then rebuild the site. Re-run when counts drift.")


if __name__ == "__main__":
    main()
