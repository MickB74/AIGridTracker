"""
Static-site generator for the public front door (Vercel).

Renders web/ from the same registries the Streamlit app uses:
  - index.html            landing page
  - states/<slug>.html    51 SEO-indexable state one-pagers
  - health-risks.html     sourced health-risks page (mirrors the infographic)
  - assets/               logo + downloadable health-risks PDF
  - sitemap.xml, robots.txt, vercel.json (cleanUrls)

Usage:
    python3 build_site.py
    # optionally: SITE_URL=https://gridwatch.example APP_URL=https://xxx.streamlit.app python3 build_site.py

Commit the regenerated web/ whenever constants change. On Vercel: import
the repo, set Root Directory to `web`, framework "Other", no build step.
"""

import html
import os
import pathlib
import shutil

from src.constants import (
    STATE_GRID_PROFILES, STATE_DC_DF, STATE_PUCS_DF, MORATORIUMS_DF,
    HEALTH_RISKS, CBA_BENCHMARKS, SOURCES,
)
from src.pdf_pack import build_health_pdf

SITE_URL = os.environ.get("SITE_URL", "https://gridwatch-ai.vercel.app")
APP_URL = os.environ.get("APP_URL", "https://aigridtracker.streamlit.app")

ROOT = pathlib.Path(__file__).resolve().parent
WEB = ROOT / "web"

esc = html.escape


def slugify(state):
    return state.lower().replace(" ", "-")


CSS = """
:root { --bg:#0b1220; --card:#121c30; --ink:#eaf0f7; --muted:#93a1b5;
        --teal:#2dd4bf; --amber:#fbbf24; --rule:#22304a; }
* { box-sizing:border-box; margin:0; }
body { background:var(--bg); color:var(--ink);
       font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif; }
.wrap { max-width:900px; margin:0 auto; padding:20px 20px 64px; }
nav { display:flex; align-items:center; gap:14px; padding:14px 0;
      border-bottom:1px solid var(--rule); flex-wrap:wrap; }
nav img { height:34px; }
nav a { color:var(--muted); text-decoration:none; font-size:14px; }
nav a:hover { color:var(--teal); }
nav .cta { margin-left:auto; background:var(--teal); color:#06251f;
           font-weight:700; padding:8px 16px; border-radius:8px; }
header { padding:44px 0 10px; }
.kicker { color:var(--teal); font-weight:700; letter-spacing:.12em;
          text-transform:uppercase; font-size:13px; }
h1 { font-size:clamp(28px,5vw,44px); line-height:1.12; margin:10px 0; }
.sub { color:var(--muted); max-width:640px; }
.stats { display:grid; grid-template-columns:repeat(2,1fr); gap:14px;
         margin:30px 0; }
@media (min-width:640px){ .stats{ grid-template-columns:repeat(4,1fr);} }
.stat { background:var(--card); border:1px solid var(--rule);
        border-radius:14px; padding:16px; }
.stat b { display:block; font-size:24px; color:var(--teal); }
.stat span { font-size:13px; color:var(--muted); }
section { margin:34px 0; }
h2 { font-size:20px; color:var(--teal); margin-bottom:12px;
     border-bottom:1px solid var(--rule); padding-bottom:8px; }
ul { padding-left:22px; } li { margin:9px 0; }
a { color:var(--teal); }
.btn { display:inline-block; background:var(--teal); color:#06251f;
       font-weight:700; padding:12px 22px; border-radius:10px;
       text-decoration:none; margin:8px 8px 0 0; }
.btn.ghost { background:transparent; color:var(--teal);
             border:1px solid var(--teal); }
.muted { color:var(--muted); font-size:14px; }
.grid3 { display:grid; grid-template-columns:1fr; gap:14px; }
@media (min-width:640px){ .grid3{ grid-template-columns:repeat(3,1fr);} }
.card { background:var(--card); border:1px solid var(--rule);
        border-radius:14px; padding:18px; }
.card h3 { margin-bottom:6px; font-size:16px; }
.panel { border-radius:14px; padding:18px; color:#fff; }
.panel h3 { margin-bottom:8px; }
.panel p { font-size:14px; color:rgba(255,255,255,.85); }
.ask { background:rgba(45,212,191,.08); border:1px solid var(--teal);
       border-radius:10px; padding:12px 14px; font-size:14px; margin-top:10px; }
.src { font-size:12.5px; color:var(--muted); }
table { width:100%; border-collapse:collapse; font-size:14px; }
th,td { text-align:left; padding:8px 10px; border-bottom:1px solid var(--rule); }
th { color:var(--muted); font-weight:600; }
footer { margin-top:48px; border-top:1px solid var(--rule);
         padding-top:16px; font-size:13px; color:var(--muted); }
.statelist { columns:2; font-size:14.5px; }
@media (min-width:640px){ .statelist{ columns:4; } }
.statelist a { display:block; padding:3px 0; text-decoration:none; }
"""


def page(title, description, body, canonical, depth=0):
    p = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website">
<link rel="icon" href="{p}assets/logo.svg" type="image/svg+xml">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<nav>
  <a href="{p}index.html"><img src="{p}assets/logo.svg" alt="AI GridWatch"></a>
  <a href="{p}index.html">Home</a>
  <a href="{p}states/index.html">Your state</a>
  <a href="{p}health-risks.html">Health risks</a>
  <a class="cta" href="{APP_URL}">Open the toolkit &rarr;</a>
</nav>
{body}
<footer>
  AI GridWatch — community energy intelligence. Planning estimates, not
  engineering studies; every number is sourced in the
  <a href="{APP_URL}">full toolkit</a>. Built from public data.
</footer>
</div>
</body>
</html>
"""


def build_index():
    n_states = len(STATE_DC_DF)
    n_dc = int(STATE_DC_DF["dc_count"].sum())
    twh = STATE_DC_DF["twh_year"].sum()
    n_mora = len(MORATORIUMS_DF)
    states_links = "\n".join(
        f'<a href="states/{slugify(s)}.html">{esc(s)}</a>'
        for s in sorted(STATE_GRID_PROFILES))
    benches = "\n".join(
        f"<li><strong>{esc(b['community'])}, {esc(b['state'])}</strong> "
        f"({esc(b['company'])}) — {esc(b['won'])}</li>"
        for b in CBA_BENCHMARKS)
    body = f"""
<header>
  <div class="kicker">AI GridWatch</div>
  <h1>A data center is coming to town.<br>Negotiate like you know the numbers.</h1>
  <p class="sub">Free tools for communities facing data center development:
  impact calculators, negotiation playbooks, health evidence, and the
  documents to bring to your next hearing — all sourced.</p>
  <p>
    <a class="btn" href="{APP_URL}">Start here — the 5-step wizard</a>
    <a class="btn ghost" href="health-risks.html">The health risks, sourced</a>
  </p>
</header>
<div class="stats">
  <div class="stat"><b>{n_dc:,}</b><span>tracked U.S. data center facilities</span></div>
  <div class="stat"><b>{twh:,.0f} TWh</b><span>estimated annual electricity, {n_states} states</span></div>
  <div class="stat"><b>{n_mora}</b><span>tracked moratorium &amp; pushback efforts</span></div>
  <div class="stat"><b>325&ndash;580 TWh</b><span>projected U.S. data center demand by 2030 (Berkeley Lab)</span></div>
</div>
<section>
  <h2>What you get</h2>
  <div class="grid3">
    <div class="card"><h3>📥 Action pack</h3><p class="muted">A personalized
    PDF: impact numbers, meeting strategy, CBA targets, a 2-minute speech,
    and ready-to-send letters.</p></div>
    <div class="card"><h3>🪧 Flyer + petition</h3><p class="muted">A one-page
    hand-out with your community's numbers, in English and Spanish, with a
    sign-up sheet.</p></div>
    <div class="card"><h3>🌐 Campaign site</h3><p class="muted">A complete
    one-page website with your numbers baked in — free to host, no coding
    needed.</p></div>
  </div>
  <p class="muted" style="margin-top:10px">All generated in the free
  <a href="{APP_URL}">GridWatch toolkit</a> — no signup required.</p>
</section>
<section>
  <h2>Communities that organized, won</h2>
  <ul>{benches}</ul>
  <p class="muted">Every one of these happened <em>before</em> final
  approval. Timing is the leverage.</p>
</section>
<section>
  <h2>Find your state</h2>
  <div class="statelist">{states_links}</div>
</section>
"""
    return page(
        "AI GridWatch — data center impact tools for communities",
        "Free calculators, negotiation playbooks, and sourced health "
        "evidence for communities facing data center development.",
        body, f"{SITE_URL}/")


def build_state(state):
    prof = STATE_GRID_PROFILES[state]
    row = STATE_DC_DF[STATE_DC_DF["state"] == state]
    dc_count = int(row.iloc[0]["dc_count"]) if not row.empty else 0
    twh = row.iloc[0]["twh_year"] if not row.empty else 0.0
    puc_row = STATE_PUCS_DF[STATE_PUCS_DF["state"] == state]
    abbrev = puc_row.iloc[0]["abbrev"] if not puc_row.empty else ""
    moras = MORATORIUMS_DF[MORATORIUMS_DF["state"] == abbrev]

    puc_html = ""
    if not puc_row.empty:
        p = puc_row.iloc[0]
        puc_html = (
            f'<section><h2>Your regulator</h2>'
            f'<p><strong>{esc(p["name"])}</strong> — '
            f'<a href="{esc(p["website"])}">website</a> · '
            f'<a href="{esc(p["complaint"])}">file a complaint</a></p>'
            f'</section>')

    mora_html = ""
    if not moras.empty:
        rows = "\n".join(
            f"<tr><td>{esc(str(m.locality))}</td><td>{esc(str(m.level))}</td>"
            f"<td>{esc(str(m.status))}</td><td>{esc(str(m.note))}</td></tr>"
            for m in moras.itertuples())
        mora_html = (
            f'<section><h2>Pushback already happening in {esc(state)}</h2>'
            f'<table><tr><th>Where</th><th>Level</th><th>Status</th>'
            f'<th>Note</th></tr>{rows}</table></section>')

    body = f"""
<header>
  <div class="kicker">State briefing</div>
  <h1>{esc(state)}: data centers &amp; your electric bill</h1>
  <p class="sub">The numbers residents cite at hearings — grid, water, and
  regulator contacts for {esc(state)}, from the free GridWatch toolkit.</p>
</header>
<div class="stats">
  <div class="stat"><b>{dc_count:,}</b><span>tracked data center facilities</span></div>
  <div class="stat"><b>{twh:.1f} TWh</b><span>estimated annual DC electricity</span></div>
  <div class="stat"><b>{prof['rate'] * 100:.1f}&cent;</b><span>residential rate per kWh</span></div>
  <div class="stat"><b>{prof['gco2']}</b><span>grid gCO&#8322;/kWh · water stress: {esc(prof['water_stress'])}</span></div>
</div>
{puc_html}
{mora_html}
<section>
  <h2>A data center was proposed near you?</h2>
  <p>The free toolkit walks you through it in five steps: who's really
  behind the LLC, what it costs your community, what to do this week, and
  a downloadable action pack — speech, letters, flyer, and CBA targets
  included.</p>
  <p><a class="btn" href="{APP_URL}">Start here &rarr;</a>
  <a class="btn ghost" href="../health-risks.html">The health risks, sourced</a></p>
</section>
"""
    return page(
        f"{state} data centers: electricity, water & who to call",
        f"Data center facilities, grid impact, and regulator contacts for "
        f"{state} — free community negotiation tools from AI GridWatch.",
        body, f"{SITE_URL}/states/{slugify(state)}", depth=1)


def build_states_index():
    links = "\n".join(
        f'<a href="{slugify(s)}.html">{esc(s)}</a>'
        for s in sorted(STATE_GRID_PROFILES))
    body = f"""
<header>
  <div class="kicker">State briefings</div>
  <h1>Pick your state</h1>
  <p class="sub">Facilities, grid impact, water stress, and your public
  utility commission — one page per state.</p>
</header>
<section><div class="statelist">{links}</div></section>
"""
    return page(
        "State data center briefings — AI GridWatch",
        "Data center impact briefings for all 50 states + DC: facilities, "
        "electricity, water stress, and regulator contacts.",
        body, f"{SITE_URL}/states/", depth=1)


def build_health():
    panels = ""
    for r in HEALTH_RISKS:
        facts = ""
        for f in r["facts"]:
            name, url = SOURCES[f["src"]]
            facts += (f'<li>{esc(f["text"])} '
                      f'<span class="src">— <a href="{esc(url)}">'
                      f'{esc(name.split(" — ")[0])}</a></span></li>')
        panels += f"""
<section>
  <div class="panel" style="background:{r['color']}">
    <h3>{r['icon']} {esc(r['title'])}</h3>
    <p>{esc(r['summary'])}</p>
  </div>
  <ul>{facts}</ul>
  <div class="ask"><strong>What to demand:</strong> {esc(r['ask'])}</div>
</section>"""
    body = f"""
<header>
  <div class="kicker">Community briefing</div>
  <h1>The health risks of data centers</h1>
  <p class="sub">Six ways a facility affects the people who live near one —
  every claim sourced, every risk paired with the permit condition that
  addresses it. Format inspired by the
  <a href="{esc(SOURCES['ehp_health'][1])}">Environmental Health Project's
  community infographic</a>.</p>
  <p><a class="btn" href="assets/gridwatch_health_risks.pdf">📥 Print the
  infographic (PDF)</a>
  <a class="btn ghost" href="{APP_URL}">Open the full toolkit</a></p>
</header>
{panels}
"""
    return page(
        "The health risks of data centers — sourced community briefing",
        "Air, noise, light, bills, water, and climate: the documented "
        "health impacts of data centers, with sources and the permit "
        "conditions that address them.",
        body, f"{SITE_URL}/health-risks")


def build_sitemap(paths):
    urls = "\n".join(
        f"  <url><loc>{SITE_URL}/{p}</loc></url>" for p in paths)
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f'{urls}\n</urlset>\n')


def main():
    shutil.rmtree(WEB, ignore_errors=True)
    (WEB / "states").mkdir(parents=True)
    (WEB / "assets").mkdir()

    shutil.copy(ROOT / "assets" / "logo.svg", WEB / "assets" / "logo.svg")
    (WEB / "assets" / "gridwatch_health_risks.pdf").write_bytes(
        build_health_pdf(HEALTH_RISKS, SOURCES))

    (WEB / "index.html").write_text(build_index(), encoding="utf-8")
    (WEB / "health-risks.html").write_text(build_health(), encoding="utf-8")
    (WEB / "states" / "index.html").write_text(
        build_states_index(), encoding="utf-8")

    paths = ["", "health-risks", "states/"]
    for state in sorted(STATE_GRID_PROFILES):
        slug = slugify(state)
        (WEB / "states" / f"{slug}.html").write_text(
            build_state(state), encoding="utf-8")
        paths.append(f"states/{slug}")

    (WEB / "sitemap.xml").write_text(build_sitemap(paths), encoding="utf-8")
    (WEB / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n",
        encoding="utf-8")
    (WEB / "vercel.json").write_text(
        '{ "cleanUrls": true, "trailingSlash": false }\n', encoding="utf-8")

    n = len(list(WEB.rglob("*.html")))
    print(f"built web/ — {n} pages, sitemap, robots.txt, vercel.json")
    print(f"SITE_URL={SITE_URL}\nAPP_URL={APP_URL}")


if __name__ == "__main__":
    main()
