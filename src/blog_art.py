"""
Generated hero artwork for blog posts.

Every post gets an inline SVG illustration — no binary assets, no external
requests, no stock photos to license. The art is drawn from the same palette
as the site CSS (:root in build_site.py) so it reads as one system.

A post picks its art with an explicit ``"art": "<theme>"`` key in
``BLOG_STORIES``; without one, ``theme_for()`` scores the id/title/tags
against ``_KEYWORDS`` and falls back to the generic campus scene. Adding a
post therefore never *requires* touching this file — but naming the theme
beats letting the keyword match guess.

Gradient/clip ids are suffixed per instance (``uid``) because the blog index
renders every post's art in one document, and duplicate ids across SVGs make
the first definition win for all of them.
"""

# Palette mirrors CSS :root — keep in sync with build_site.CSS.
_BG_TOP, _BG_BOT = "#16233c", "#0b1220"
_CARD, _RULE, _MUTED, _TEAL, _AMBER = "#121c30", "#22304a", "#93a1b5", "#2dd4bf", "#fbbf24"

W, H = 640, 280


def _bg_grid():
    """Faint graph-paper backdrop shared by every scene."""
    lines = []
    for x in range(40, W, 40):
        lines.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>')
    for y in range(40, H, 40):
        lines.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>')
    return (f'<g stroke="{_RULE}" stroke-width=".7" opacity=".45">'
            + "".join(lines) + "</g>")


# ── Scenes ──────────────────────────────────────────────────────────────── #
# Each entry: caption (drawn bottom-left), alt (screen-reader description),
# and draw(u) -> SVG fragment. `u` is the per-instance id suffix.

def _grid_campus(u):
    return f'''
  <g stroke="{_TEAL}" stroke-width="1.6" fill="none" opacity=".5">
    <path d="M 120,104 Q 300,132 470,96"/><path d="M 120,124 Q 300,152 470,116"/>
  </g>
  <g transform="translate(60,70)">
    <path d="M 44,0 L 6,150 M 44,0 L 82,150 M 14,112 L 74,112 M 22,72 L 66,72 M 30,40 L 58,40"
          stroke="{_MUTED}" stroke-width="1.8" fill="none"/>
    <rect x="35" y="-9" width="18" height="11" fill="{_MUTED}"/>
  </g>
  <g transform="translate(400,120)">
    <rect x="0" y="0" width="170" height="100" rx="7" fill="{_CARD}" stroke="{_RULE}" stroke-width="1.5"/>
    <rect x="0" y="0" width="170" height="15" fill="{_RULE}"/>
    <circle cx="11" cy="7.5" r="2.5" fill="{_TEAL}"/><circle cx="21" cy="7.5" r="2.5" fill="{_AMBER}" opacity=".8"/>
    <g fill="{_TEAL}">
      <rect x="12" y="26" width="146" height="7" opacity=".62"/>
      <rect x="12" y="41" width="104" height="7" opacity=".42"/>
      <rect x="12" y="56" width="146" height="7" opacity=".62"/>
      <rect x="12" y="71" width="82" height="7" opacity=".32"/>
    </g>
  </g>
  <g class="glow" fill="{_TEAL}">
    <circle cx="200" cy="115" r="3.5"/><circle cx="300" cy="127" r="3.5"/><circle cx="400" cy="112" r="3.5"/>
  </g>'''


def _transmission(u):
    towers = "".join(
        f'<g transform="translate({x},{y}) scale({s})">'
        f'<path d="M 30,0 L 4,110 M 30,0 L 56,110 M 10,80 L 50,80 M 16,48 L 44,48"'
        f' stroke="{_MUTED}" stroke-width="{2.0 / s:.1f}" fill="none" opacity="{o}"/>'
        f'<rect x="22" y="-7" width="16" height="9" fill="{_MUTED}" opacity="{o}"/></g>'
        for x, y, s, o in ((50, 80, 1.0, .95), (250, 95, .8, .7), (430, 108, .62, .5)))
    return f'''
  <g stroke="{_TEAL}" stroke-width="1.5" fill="none" opacity=".55">
    <path d="M 80,74 Q 200,116 280,94 T 456,100"/>
    <path d="M 80,96 Q 200,138 280,112 T 456,114"/>
  </g>
  {towers}
  <path d="M 0,214 Q 160,196 320,210 T 640,200 L 640,280 L 0,280 Z" fill="{_CARD}" opacity=".85"/>
  <g class="glow" fill="{_TEAL}"><circle cx="170" cy="98" r="4"/><circle cx="330" cy="102" r="4"/></g>'''


def _water(u):
    return f'''
  <defs><linearGradient id="wt{u}" x1="0" x2="0" y1="0" y2="1">
    <stop offset="0" stop-color="{_TEAL}" stop-opacity=".55"/>
    <stop offset="1" stop-color="{_TEAL}" stop-opacity=".05"/></linearGradient></defs>
  <g transform="translate(96,54)">
    <path d="M 18,150 L 34,26 L 92,26 L 108,150 Z" fill="{_CARD}" stroke="{_RULE}" stroke-width="1.6"/>
    <rect x="30" y="18" width="66" height="10" rx="3" fill="{_RULE}"/>
    <g fill="url(#wt{u})">
      <circle cx="44" cy="4" r="16"/><circle cx="68" cy="-6" r="20"/>
      <circle cx="90" cy="6" r="14"/><circle cx="78" cy="-26" r="12"/>
    </g>
  </g>
  <g transform="translate(280,60)" fill="{_TEAL}">
    <path d="M 24,0 C 40,26 50,40 50,54 a 26,26 0 0 1 -52,0 C -2,40 8,26 24,0 Z" opacity=".55"/>
    <path d="M 106,34 C 118,54 126,64 126,74 a 20,20 0 0 1 -40,0 C 86,64 94,54 106,34 Z" opacity=".35"/>
  </g>
  <g stroke="{_TEAL}" stroke-width="2" fill="none" opacity=".7">
    <path d="M 0,206 q 40,-16 80,0 t 80,0 t 80,0 t 80,0 t 80,0 t 80,0 t 80,0"/>
    <path d="M 0,228 q 40,-16 80,0 t 80,0 t 80,0 t 80,0 t 80,0 t 80,0 t 80,0" opacity=".4"/>
  </g>
  <g transform="translate(470,86)">
    <circle cx="52" cy="52" r="46" fill="{_CARD}" stroke="{_RULE}" stroke-width="1.6"/>
    <path d="M 52,52 L 82,32" stroke="{_AMBER}" stroke-width="3.4" stroke-linecap="round"/>
    <path d="M 16,52 a 36,36 0 0 1 72,0" stroke="{_TEAL}" stroke-width="3" fill="none" opacity=".6"/>
  </g>'''


def _money(u):
    bars = "".join(
        f'<rect x="{x}" y="{196 - h}" width="34" height="{h}" rx="3" fill="{_TEAL}" opacity="{o}"/>'
        for x, h, o in ((372, 40, .35), (416, 66, .5), (460, 98, .68), (504, 134, .9)))
    # Each coin is a slab: side wall first, then the face on top of it.
    coins = "".join(
        f'<g opacity="{o}">'
        f'<path d="M 84,{y} v 14 a 66,17 0 0 0 132,0 v -14 Z" fill="{_RULE}"/>'
        f'<ellipse cx="150" cy="{y}" rx="66" ry="17" fill="{_CARD}" stroke="{_AMBER}"'
        f' stroke-width="1.6"/></g>'
        for y, o in ((176, 1), (150, .9), (124, .78)))
    return f'''
  {coins}
  <text x="150" y="132" text-anchor="middle" fill="{_AMBER}" font-size="26"
        font-weight="700" font-family="system-ui,sans-serif">$</text>
  <line x1="352" y1="196" x2="580" y2="196" stroke="{_RULE}" stroke-width="1.5"/>
  {bars}
  <path d="M 372,150 L 424,124 L 470,96 L 540,58" stroke="{_AMBER}" stroke-width="2.4"
        fill="none" opacity=".85"/>
  <circle class="glow" cx="540" cy="58" r="5" fill="{_AMBER}"/>'''


def _bills(u):
    rows = "".join(
        f'<rect x="{x}" y="{y}" width="{w}" height="7" rx="2" fill="{_MUTED}" opacity=".35"/>'
        for x, y, w in ((78, 96, 150), (78, 114, 108), (78, 132, 150), (78, 150, 84)))
    return f'''
  <g>
    <rect x="58" y="52" width="196" height="180" rx="8" fill="{_CARD}" stroke="{_RULE}" stroke-width="1.6"/>
    <rect x="58" y="52" width="196" height="26" rx="8" fill="{_RULE}"/>
    <rect x="58" y="70" width="196" height="8" fill="{_RULE}"/>
    <text x="78" y="70" fill="{_TEAL}" font-size="13" font-weight="700"
          font-family="system-ui,sans-serif">ELECTRIC BILL</text>
    {rows}
    <line x1="78" y1="176" x2="234" y2="176" stroke="{_RULE}" stroke-width="1.4"/>
    <text x="78" y="202" fill="{_AMBER}" font-size="24" font-weight="700"
          font-family="system-ui,sans-serif">$ ↑</text>
  </g>
  <g transform="translate(300,60)">
    <line x1="0" y1="150" x2="288" y2="150" stroke="{_RULE}" stroke-width="1.5"/>
    <line x1="0" y1="0" x2="0" y2="150" stroke="{_RULE}" stroke-width="1.5"/>
    <path d="M 8,132 L 66,124 L 124,104 L 182,72 L 246,26" stroke="{_AMBER}"
          stroke-width="2.6" fill="none"/>
    <path d="M 8,132 L 66,124 L 124,104 L 182,72 L 246,26 L 246,150 L 8,150 Z"
          fill="{_AMBER}" opacity=".1"/>
    <g fill="{_AMBER}"><circle cx="66" cy="124" r="3.4"/><circle cx="124" cy="104" r="3.4"/>
      <circle cx="182" cy="72" r="3.4"/><circle class="glow" cx="246" cy="26" r="5"/></g>
  </g>'''


def _moratorium(u):
    return f'''
  <g transform="translate(72,56)">
    <rect x="0" y="0" width="180" height="164" rx="10" fill="{_CARD}" stroke="{_RULE}" stroke-width="1.6"/>
    <rect x="0" y="0" width="180" height="34" rx="10" fill="{_RULE}"/>
    <rect x="0" y="24" width="180" height="10" fill="{_RULE}"/>
    <g fill="{_MUTED}" opacity=".45">
      {"".join(f'<rect x="{16 + 32 * c}" y="{50 + 28 * r}" width="20" height="16" rx="3"/>'
               for r in range(3) for c in range(5))}
    </g>
    <g stroke="{_AMBER}" stroke-width="4.5" stroke-linecap="round">
      <line x1="120" y1="96" x2="168" y2="144"/><line x1="168" y1="96" x2="120" y2="144"/>
    </g>
  </g>
  <g transform="translate(360,66)">
    <circle cx="86" cy="72" r="70" fill="none" stroke="{_TEAL}" stroke-width="4" opacity=".75"/>
    <rect x="66" y="42" width="14" height="60" rx="4" fill="{_TEAL}"/>
    <rect x="94" y="42" width="14" height="60" rx="4" fill="{_TEAL}"/>
    <circle class="glow" cx="86" cy="72" r="80" fill="none" stroke="{_TEAL}"
            stroke-width="1.2" opacity=".3"/>
  </g>'''


def _land(u):
    parcels = "".join(
        f'<rect x="{60 + 92 * c}" y="{58 + 56 * r}" width="84" height="48" rx="4" '
        f'fill="{_CARD}" stroke="{_RULE}" stroke-width="1.3"/>'
        for r in range(3) for c in range(5))
    return f'''
  {parcels}
  <rect x="244" y="114" width="176" height="48" rx="4" fill="{_TEAL}" opacity=".22"/>
  <rect x="244" y="114" width="176" height="48" rx="4" fill="none" stroke="{_TEAL}" stroke-width="2"/>
  <g stroke="{_MUTED}" stroke-width="1.6" opacity=".5">
    <line x1="60" y1="114" x2="524" y2="114"/><line x1="244" y1="58" x2="244" y2="218"/>
  </g>
  <g transform="translate(288,120)">
    <path d="M 0,34 L 0,0 L 26,9 L 0,18" fill="{_AMBER}" stroke="{_AMBER}" stroke-width="1.4"
          stroke-linejoin="round"/>
  </g>
  <circle class="glow" cx="332" cy="138" r="6" fill="{_TEAL}"/>'''


def _media(u):
    bars = "".join(
        f'<rect x="{300 + i * 20}" y="{140 - h / 2:.0f}" width="9" height="{h}" rx="4.5" '
        f'fill="{_TEAL}" opacity="{0.3 + (h / 200):.2f}"/>'
        for i, h in enumerate((28, 62, 104, 46, 130, 78, 34, 96, 54, 22, 70, 40)))
    return f'''
  <g transform="translate(104,50)">
    <rect x="34" y="0" width="52" height="94" rx="26" fill="{_CARD}" stroke="{_TEAL}" stroke-width="2"/>
    <g fill="{_TEAL}" opacity=".45">
      {"".join(f'<rect x="42" y="{14 + i * 16}" width="36" height="4" rx="2"/>' for i in range(5))}
    </g>
    <path d="M 16,68 a 44,44 0 0 0 88,0" stroke="{_MUTED}" stroke-width="2.6" fill="none"/>
    <line x1="60" y1="112" x2="60" y2="146" stroke="{_MUTED}" stroke-width="2.6"/>
    <rect x="26" y="146" width="68" height="9" rx="4" fill="{_MUTED}"/>
  </g>
  {bars}
  <g transform="translate(492,64)">
    <rect x="0" y="0" width="104" height="66" rx="10" fill="{_CARD}" stroke="{_RULE}" stroke-width="1.5"/>
    <path d="M 22,66 L 22,86 L 44,66 Z" fill="{_CARD}" stroke="{_RULE}" stroke-width="1.5"/>
    <g fill="{_MUTED}" opacity=".5"><rect x="16" y="20" width="72" height="6" rx="3"/>
      <rect x="16" y="36" width="48" height="6" rx="3"/></g>
  </g>'''


def _forecast(u):
    ticks = "".join(f'<line x1="{72 + i * 96}" y1="212" x2="{72 + i * 96}" y2="220" '
                    f'stroke="{_RULE}" stroke-width="1.4"/>' for i in range(6))
    return f'''
  <defs><linearGradient id="fc{u}" x1="0" x2="0" y1="0" y2="1">
    <stop offset="0" stop-color="{_TEAL}" stop-opacity=".45"/>
    <stop offset="1" stop-color="{_TEAL}" stop-opacity="0"/></linearGradient></defs>
  <line x1="72" y1="212" x2="568" y2="212" stroke="{_RULE}" stroke-width="1.6"/>
  <line x1="72" y1="44" x2="72" y2="212" stroke="{_RULE}" stroke-width="1.6"/>
  {ticks}
  <path d="M 72,196 L 168,182 L 264,156 L 360,120 L 456,84 L 552,50 L 552,212 L 72,212 Z"
        fill="url(#fc{u})"/>
  <path d="M 72,196 L 168,182 L 264,156 L 360,120 L 456,84 L 552,50" stroke="{_TEAL}"
        stroke-width="2.8" fill="none"/>
  <g fill="{_TEAL}"><circle cx="168" cy="182" r="4"/><circle cx="264" cy="156" r="4"/>
    <circle cx="360" cy="120" r="4"/><circle cx="456" cy="84" r="4"/>
    <circle class="glow" cx="552" cy="50" r="6"/></g>
  <path d="M 264,156 L 552,50" stroke="{_AMBER}" stroke-width="1.6" stroke-dasharray="5 5"
        fill="none" opacity=".6"/>'''


def _queue(u):
    rows = "".join(
        f'<rect x="72" y="{56 + i * 32}" width="{w}" height="20" rx="4" fill="{_TEAL}" '
        f'opacity="{o}"/>'
        for i, (w, o) in enumerate(((330, .85), (272, .68), (218, .55), (162, .42), (108, .3))))
    labels = "".join(
        f'<text x="{86 + w}" y="{71 + i * 32}" fill="{_MUTED}" font-size="11" '
        f'font-family="system-ui,sans-serif">{lbl}</text>'
        for i, (w, lbl) in enumerate(((330, "requested"), (272, "screened"),
                                      (218, "studied"), (162, "agreement"),
                                      (108, "energized"))))
    return f'''
  {rows}
  {labels}
  <g transform="translate(516,150)">
    <rect x="-5" y="-42" width="12" height="84" rx="4" fill="{_RULE}"/>
    <rect x="4" y="-16" width="88" height="9" rx="4" fill="{_AMBER}" opacity=".85"
          transform="rotate(-26 4 -12)"/>
    <circle class="glow" cx="1" cy="-16" r="6" fill="{_AMBER}"/>
  </g>'''


def _checklist(u):
    rows = "".join(
        f'<g><rect x="112" y="{74 + i * 34}" width="20" height="20" rx="5" fill="none" '
        f'stroke="{_TEAL}" stroke-width="2"/>'
        f'<path d="M 116,{84 + i * 34} l 5,6 l 10,-12" stroke="{_TEAL}" stroke-width="2.6" '
        f'fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="{o}"/>'
        f'<rect x="146" y="{81 + i * 34}" width="{w}" height="7" rx="3" fill="{_MUTED}" '
        f'opacity=".42"/></g>'
        for i, (w, o) in enumerate(((172, 1), (140, 1), (188, 1), (124, .25))))
    return f'''
  <g>
    <rect x="88" y="40" width="280" height="200" rx="10" fill="{_CARD}" stroke="{_RULE}" stroke-width="1.6"/>
    <rect x="196" y="30" width="64" height="20" rx="6" fill="{_RULE}"/>
    {rows}
  </g>
  <g transform="translate(432,74)">
    <circle cx="56" cy="56" r="46" fill="none" stroke="{_AMBER}" stroke-width="4" opacity=".85"/>
    <line x1="90" y1="90" x2="122" y2="122" stroke="{_AMBER}" stroke-width="7" stroke-linecap="round"/>
    <text x="56" y="70" text-anchor="middle" fill="{_AMBER}" font-size="42" font-weight="700"
          font-family="system-ui,sans-serif">?</text>
  </g>'''


def _oversight(u):
    docs = "".join(
        f'<g transform="translate({66 + i * 34},{56 + i * 14}) rotate({-6 + i * 5} 70 90)">'
        f'<rect x="0" y="0" width="140" height="176" rx="8" fill="{_CARD}" stroke="{_RULE}" '
        f'stroke-width="1.5"/>'
        + "".join(f'<rect x="18" y="{26 + r * 20}" width="{104 - 18 * (r % 3)}" height="6" '
                  f'rx="3" fill="{_MUTED}" opacity=".32"/>' for r in range(6))
        + "</g>" for i in range(3))
    return f'''
  {docs}
  <g transform="translate(392,72)">
    <circle cx="60" cy="60" r="52" fill="{_BG_BOT}" fill-opacity=".55" stroke="{_TEAL}" stroke-width="4"/>
    <line x1="98" y1="98" x2="136" y2="136" stroke="{_TEAL}" stroke-width="8" stroke-linecap="round"/>
    <g stroke="{_AMBER}" stroke-width="4" stroke-linecap="round">
      <line x1="38" y1="60" x2="56" y2="60"/><line x1="66" y1="60" x2="84" y2="60"/>
    </g>
  </g>
  <circle class="glow" cx="452" cy="132" r="7" fill="{_AMBER}"/>'''


def _community(u):
    houses = "".join(
        f'<g transform="translate({64 + i * 96},{104})">'
        f'<path d="M -6,26 L 34,-10 L 74,26 Z" fill="{_RULE}"/>'
        f'<rect x="6" y="26" width="56" height="48" rx="3" fill="{_CARD}" stroke="{_RULE}" stroke-width="1.4"/>'
        f'<rect x="26" y="44" width="16" height="30" fill="{_TEAL}" opacity=".35"/></g>'
        for i in range(5))
    people = "".join(
        f'<g transform="translate({100 + i * 84},{206})" fill="{_TEAL}" opacity="{o}">'
        f'<circle cx="0" cy="0" r="8"/>'
        f'<path d="M -14,28 a 14,18 0 0 1 28,0 Z"/></g>'
        for i, o in enumerate((.85, .6, .9, .6, .8)))
    return f'''
  {houses}
  {people}
  <g transform="translate(408,14)">
    <rect x="0" y="0" width="168" height="56" rx="12" fill="{_CARD}" stroke="{_TEAL}" stroke-width="1.8"/>
    <path d="M 30,56 L 30,76 L 54,56 Z" fill="{_CARD}" stroke="{_TEAL}" stroke-width="1.8"/>
    <g fill="{_TEAL}" opacity=".55"><rect x="20" y="16" width="128" height="7" rx="3.5"/>
      <rect x="20" y="33" width="84" height="7" rx="3.5"/></g>
  </g>'''


def _extraction(u):
    strata = "".join(
        f'<rect x="0" y="{188 + i * 24}" width="{W}" height="24" fill="{c}" opacity="{o}"/>'
        for i, (c, o) in enumerate(((_RULE, .5), (_CARD, .8), (_RULE, .35))))
    return f'''
  {strata}
  <g transform="translate(88,44)">
    <path d="M 44,0 L 4,144 M 44,0 L 84,144 M 14,110 L 74,110 M 24,66 L 64,66"
          stroke="{_MUTED}" stroke-width="2" fill="none"/>
    <rect x="30" y="-8" width="28" height="10" rx="2" fill="{_MUTED}"/>
    <circle cx="44" cy="20" r="9" fill="none" stroke="{_AMBER}" stroke-width="2.4"/>
  </g>
  <g stroke="{_AMBER}" stroke-width="2.2" fill="none" opacity=".8">
    <path d="M 132,188 L 132,244"/><path d="M 132,244 L 220,244"/>
  </g>
  <g transform="translate(300,60)">
    <rect x="0" y="0" width="88" height="128" rx="6" fill="{_CARD}" stroke="{_RULE}" stroke-width="1.5"/>
    <rect x="0" y="0" width="88" height="14" fill="{_RULE}"/>
    <g fill="{_TEAL}"><rect x="10" y="28" width="68" height="6" opacity=".6"/>
      <rect x="10" y="44" width="46" height="6" opacity=".4"/>
      <rect x="10" y="60" width="68" height="6" opacity=".6"/>
      <rect x="10" y="76" width="34" height="6" opacity=".3"/></g>
  </g>
  <g stroke="{_MUTED}" stroke-width="1.6" fill="none" opacity=".55" stroke-dasharray="6 6">
    <path d="M 176,120 L 296,120"/>
  </g>
  <g transform="translate(430,70)">
    <circle cx="60" cy="60" r="54" fill="none" stroke="{_MUTED}" stroke-width="2" opacity=".6"/>
    <path d="M 60,22 L 60,60 L 88,76" stroke="{_TEAL}" stroke-width="3.4" fill="none"
          stroke-linecap="round"/>
  </g>'''


def _review(u):
    """Week-in-review: a calendar page beside stacked headline cards."""
    return f'''
  <g transform="translate(60,50)">
    <rect x="0" y="0" width="120" height="140" rx="8" fill="{_CARD}" stroke="{_RULE}" stroke-width="1.5"/>
    <rect x="0" y="0" width="120" height="28" rx="8" fill="{_RULE}"/>
    <rect x="0" y="14" width="120" height="14" fill="{_RULE}"/>
    <g fill="{_MUTED}" font-size="11" text-anchor="middle" opacity=".8">
      <text x="20" y="22" font-weight="bold" fill="{_TEAL}">S</text>
      <text x="40" y="22">M</text><text x="60" y="22">T</text>
      <text x="80" y="22">W</text><text x="100" y="22">T</text>
    </g>
    <g fill="{_MUTED}" font-size="9" text-anchor="middle" opacity=".5">
      <text x="20" y="50">10</text><text x="40" y="50">11</text><text x="60" y="50">12</text>
      <text x="80" y="50">13</text><text x="100" y="50">14</text>
      <text x="20" y="70">17</text><text x="40" y="70">18</text>
    </g>
    <circle cx="60" cy="66" r="11" fill="none" stroke="{_TEAL}" stroke-width="2"/>
    <circle cx="80" cy="46" r="11" fill="none" stroke="{_AMBER}" stroke-width="1.6" opacity=".7"/>
  </g>
  <g transform="translate(260,44)">
    <rect x="0" y="0" width="300" height="44" rx="6" fill="{_CARD}" stroke="{_RULE}" stroke-width="1.2"/>
    <rect x="12" y="12" width="200" height="7" rx="3.5" fill="{_TEAL}" opacity=".6"/>
    <rect x="12" y="27" width="140" height="6" rx="3" fill="{_MUTED}" opacity=".35"/>
  </g>
  <g transform="translate(270,100)">
    <rect x="0" y="0" width="300" height="44" rx="6" fill="{_CARD}" stroke="{_RULE}" stroke-width="1.2"/>
    <rect x="12" y="12" width="180" height="7" rx="3.5" fill="{_AMBER}" opacity=".55"/>
    <rect x="12" y="27" width="120" height="6" rx="3" fill="{_MUTED}" opacity=".35"/>
  </g>
  <g transform="translate(280,156)">
    <rect x="0" y="0" width="300" height="44" rx="6" fill="{_CARD}" stroke="{_RULE}" stroke-width="1.2"/>
    <rect x="12" y="12" width="220" height="7" rx="3.5" fill="{_TEAL}" opacity=".45"/>
    <rect x="12" y="27" width="100" height="6" rx="3" fill="{_MUTED}" opacity=".35"/>
  </g>
  <g stroke="{_TEAL}" stroke-width="1.4" fill="none" opacity=".35" stroke-dasharray="5 5">
    <path d="M 180,120 L 256,80"/><path d="M 180,130 L 266,140"/>
  </g>'''


def _negotiation(u):
    # Two sides of a table with a document between them
    return f'''
  <g transform="translate(120,60)">
    <rect x="0" y="60" width="400" height="120" rx="10" fill="{_CARD}" stroke="{_RULE}" stroke-width="1.6"/>
    <rect x="140" y="40" width="120" height="160" rx="6" fill="{_BG_TOP}" stroke="{_TEAL}" stroke-width="1.6"/>
    <rect x="156" y="60" width="88" height="6" rx="3" fill="{_TEAL}" opacity=".7"/>
    <rect x="156" y="76" width="72" height="5" rx="2.5" fill="{_MUTED}" opacity=".4"/>
    <rect x="156" y="90" width="80" height="5" rx="2.5" fill="{_MUTED}" opacity=".4"/>
    <rect x="156" y="104" width="60" height="5" rx="2.5" fill="{_MUTED}" opacity=".35"/>
    <rect x="156" y="118" width="75" height="5" rx="2.5" fill="{_MUTED}" opacity=".35"/>
    <rect x="156" y="138" width="40" height="14" rx="4" fill="{_TEAL}" opacity=".5"/>
    <rect x="206" y="138" width="40" height="14" rx="4" fill="{_AMBER}" opacity=".5"/>
    <line x1="156" y1="162" x2="244" y2="162" stroke="{_MUTED}" stroke-width="1" stroke-dasharray="4 3" opacity=".4"/>
    <text x="200" y="172" text-anchor="middle" fill="{_MUTED}" font-size="8"
          font-family="system-ui,sans-serif" opacity=".5">BINDING TERMS</text>
  </g>
  <g transform="translate(80,96)">
    <circle cx="24" cy="24" r="22" fill="{_CARD}" stroke="{_TEAL}" stroke-width="1.4"/>
    <text x="24" y="30" text-anchor="middle" fill="{_TEAL}" font-size="18"
          font-family="system-ui,sans-serif" font-weight="700">C</text>
  </g>
  <g transform="translate(536,96)">
    <circle cx="24" cy="24" r="22" fill="{_CARD}" stroke="{_AMBER}" stroke-width="1.4"/>
    <text x="24" y="30" text-anchor="middle" fill="{_AMBER}" font-size="18"
          font-family="system-ui,sans-serif" font-weight="700">D</text>
  </g>
  <g fill="{_TEAL}" opacity=".3">
    <circle cx="60" cy="200" r="3"/><circle cx="76" cy="206" r="2.5"/><circle cx="92" cy="200" r="2"/>
  </g>
  <g fill="{_AMBER}" opacity=".3">
    <circle cx="560" cy="200" r="3"/><circle cx="544" cy="206" r="2.5"/><circle cx="580" cy="200" r="2"/>
  </g>'''


ART_THEMES = {
    "grid":         ("Grid interconnection", "Illustration: a transmission tower feeding a hyperscale data center campus", _grid_campus),
    "transmission": ("Transmission buildout", "Illustration: a line of high-voltage transmission towers receding into the distance", _transmission),
    "water":        ("Water draw", "Illustration: a data center cooling tower, water droplets, and a gauge", _water),
    "money":        ("Public cost", "Illustration: a stack of coins beside a rising bar chart", _money),
    "bills":        ("Ratepayer impact", "Illustration: an electric bill next to a sharply rising cost line", _bills),
    "moratorium":   ("Moratorium", "Illustration: a data center site struck through, beside a large pause symbol", _moratorium),
    "land":         ("Site selection", "Illustration: a parcel map with one plot highlighted and a survey stake planted", _land),
    "media":        ("Coverage", "Illustration: a podcast microphone beside an audio waveform and speech bubbles", _media),
    "forecast":     ("Demand forecast", "Illustration: an area chart of electricity demand rising steeply", _forecast),
    "queue":        ("Interconnection queue", "Illustration: queue stages narrowing from requested to energized, with a gate at the end", _queue),
    "checklist":    ("Questions to ask", "Illustration: a clipboard checklist beside a magnifying glass and a question mark", _checklist),
    "oversight":    ("Oversight gap", "Illustration: a stack of permit documents under a magnifying glass with a visible gap", _oversight),
    "community":    ("Community response", "Illustration: a row of houses with residents below and a speech bubble above", _community),
    "extraction":   ("Extraction precedent", "Illustration: a headframe over geological strata beside a modern data center and a clock", _extraction),
    "review":       ("Week in review", "Illustration: a calendar page beside stacked headline cards", _review),
    "negotiation":  ("Negotiation intel", "Illustration: a negotiation table with a contract document between community and developer icons", _negotiation),
}

# First match wins, so order matters: the more specific themes come first.
# Matched against the post id, title, and tags (lowercased).
_KEYWORDS = [
    ("moratorium",   ("moratorium", "ban", "eo62", "pause")),
    ("water",        ("water", "aquifer", "cooling", "drought")),
    ("queue",        ("queue", "interconnection", "ercot")),
    ("checklist",    ("checklist", "questions to ask", "how to")),
    ("oversight",    ("oversight", "agency shopping", "permit", "transparency", "disclosure")),
    ("media",        ("podcast", "ezra klein", "media", "coverage", "public opinion")),
    ("forecast",     ("forecast", "outlook", "bnef", "projection", "gw ")),
    ("transmission", ("transmission", "doe ", "grid buildout", "high-voltage")),
    ("bills",        ("bill", "ratepayer", "rate hike", "tariff", "capacity auction", "pjm")),
    ("money",        ("tax break", "subsidy", "abatement", "incentive", "dividend")),
    ("land",         ("land", "site selection", "siting", "zoning", "rezoning", "land rush")),
    ("community",    ("backlash", "opposition", "social license", "community", "protest")),
    ("negotiation",  ("negotiation", "concession", "proffer", "cba", "leverage", "bargain")),
    ("extraction",   ("extraction", "precedent", "coal", "mining", "boomtown")),
    ("review",       ("week in review", "weekly review", "roundup")),
]


def theme_for(story):
    """Return the art theme key for a post. Explicit ``art`` key wins."""
    explicit = story.get("art")
    if explicit in ART_THEMES:
        return explicit
    haystack = " ".join([
        story.get("id", ""), story.get("title", ""),
        " ".join(story.get("tags", [])),
    ]).lower()
    for theme, words in _KEYWORDS:
        if any(w in haystack for w in words):
            return theme
    return "grid"


def art_svg(story, cls="post-art", uid=None):
    """Inline SVG hero art for a post. ``uid`` must be unique per document."""
    theme = theme_for(story)
    caption, alt, draw = ART_THEMES[theme]
    u = (uid or story.get("id") or theme).replace(" ", "-")
    return (
        f'<svg class="{cls}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="{alt}">\n'
        f'  <defs><linearGradient id="bg{u}" x1="0" x2="0" y1="0" y2="1">'
        f'<stop offset="0" stop-color="{_BG_TOP}"/>'
        f'<stop offset="1" stop-color="{_BG_BOT}"/></linearGradient></defs>\n'
        f'  <rect width="{W}" height="{H}" rx="14" fill="url(#bg{u})"/>\n'
        f'  {_bg_grid()}\n'
        f'{draw(u)}\n'
        f'  <text x="24" y="262" fill="{_MUTED}" font-size="12" font-weight="700"'
        f' letter-spacing="1.6" font-family="system-ui,-apple-system,sans-serif">'
        f'{caption.upper()}</text>\n'
        f'</svg>'
    )
