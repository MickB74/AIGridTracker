"""
Static-site generator for the public front door (Vercel).

Renders web/ from the same registries the Streamlit app uses:
  - index.html            landing page
  - states/<slug>.html    51 enriched state one-pagers (PUC, moratoriums,
                          DC sites, officials, CBA wins, case studies, muni league)
  - health-risks.html     sourced health-risks page (mirrors the infographic)
  - moratoriums.html       moratorium tracker + case study outcomes
  - impact.html           client-side impact calculator (JS, embedded coefficients)
  - blog/index.html       blog index (all posts, newest first)
  - blog/<slug>.html      individual blog post pages with prev/next nav
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

import markdown

from src.blog_content import BLOG_STORIES, ABOUT_SECTION
from src.constants import (
    STATE_GRID_PROFILES, STATE_DC_DF, STATE_PUCS_DF, MORATORIUMS_DF,
    MORATORIUM_OUTCOMES, HEALTH_RISKS, CBA_BENCHMARKS, COMPANY_CONCESSIONS,
    DC_SITES_DF, LOCAL_OFFICIALS_DF, LOCAL_BODIES_DF, STATE_MUNI_LEAGUES,
    OPERATORS_DF, EXECUTIVES_DF,
    GOOGLE_2025_HEADLINE, META_2024_HEADLINE,
    MICROSOFT_ENV_HEADLINE, AWS_ENV_HEADLINE,
    EQUINIX_2024_HEADLINE, DIGITAL_REALTY_2024_HEADLINE,
    EDGECONNEX_2024_HEADLINE, STACK_2023_HEADLINE,
    CYRUSONE_2023_HEADLINE, VANTAGE_2023_HEADLINE,
    COREWEAVE_PROFILE, QTS_PROFILE, SWITCH_PROFILE, COMPASS_PROFILE,
    SOURCES, registry_provenance,
)
from src.pdf_pack import build_health_pdf
from src.us_map_data import US_MAP_PATHS, US_MAP_LABELS, US_MAP_VIEWBOX

SITE_URL = os.environ.get("SITE_URL", "https://gridwatch-ai.vercel.app")
APP_URL = os.environ.get("APP_URL", "https://aigridtracker.streamlit.app")

# Third-party existing-facility directory (SOURCES["datacentermap"]). State
# slugs match slugify(state) for all 51 US entries.
DCMAP_BASE = "https://www.datacentermap.com/usa"


def provenance_html(registry_key, depth=0):
    """Freshness note for a registry, as an HTML block. "" if untracked.

    Mirrors helpers.render_freshness for the static site: a dataset past its
    shelf life is called out rather than quietly captioned, because these
    pages are what people print and carry into a hearing.
    """
    p = registry_provenance(registry_key)
    if not p:
        return ""
    src = ""
    if p.get("source") and p["source"] in SOURCES:
        name, url = SOURCES[p["source"]]
        src = f' · Source: <a href="{esc(url)}" rel="nofollow">{esc(name)}</a>'
    cls = "freshness stale" if p["stale"] else "freshness"
    icon = "&#9203; " if p["stale"] else ""
    caveat = (f'<p class="muted" style="margin:6px 0 0">{esc(p["caveat"])}</p>'
              if p.get("caveat") else "")
    return (f'<div class="{cls}"><p><strong>{icon}{esc(p["line"])}</strong>'
            f'{src}</p>{caveat}</div>')

ROOT = pathlib.Path(__file__).resolve().parent
WEB = ROOT / "web"

esc = html.escape

_ABBREV = dict(zip(STATE_PUCS_DF["state"], STATE_PUCS_DF["abbrev"]))


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
.freshness { border-left:3px solid var(--rule); padding:10px 14px;
  margin:14px 0; background:rgba(255,255,255,.02); border-radius:0 8px 8px 0;
  font-size:13.5px; }
.freshness.stale { border-left-color:var(--amber);
  background:rgba(251,191,36,.07); }
.freshness p { margin:0; }
table { width:100%; border-collapse:collapse; font-size:14px; }
th,td { text-align:left; padding:8px 10px; border-bottom:1px solid var(--rule); }
th { color:var(--muted); font-weight:600; }
footer { margin-top:48px; border-top:1px solid var(--rule);
         padding-top:16px; font-size:13px; color:var(--muted); }
.statelist { columns:2; font-size:14.5px; }
@media (min-width:640px){ .statelist{ columns:4; } }
.statelist a { display:block; padding:3px 0; text-decoration:none; }
.us-map { max-width:100%; height:auto; margin:20px auto; display:block; }
.us-map path { fill:var(--card); stroke:var(--rule); stroke-width:.6;
               cursor:pointer; transition:fill .15s; }
.us-map path:hover { fill:var(--teal); }
.us-map text { fill:var(--muted); font-size:7px; pointer-events:none;
               text-anchor:middle; font-weight:600;
               font-family:system-ui,-apple-system,sans-serif; }
.us-map path:hover + text, .us-map path:hover ~ text { fill:var(--bg); }
.map-tooltip { position:fixed; background:var(--card); border:1px solid var(--teal);
               border-radius:8px; padding:6px 12px; font-size:13px;
               color:var(--ink); pointer-events:none; z-index:999;
               display:none; white-space:nowrap; }
.post-meta { color:var(--muted); font-size:14px; margin:8px 0 6px; }
.tags { display:flex; flex-wrap:wrap; gap:6px; margin:8px 0 20px; }
.tag { background:var(--card); border:1px solid var(--rule);
       border-radius:20px; padding:3px 11px; font-size:12px;
       color:var(--muted); }
.prose h3 { font-size:17px; color:var(--teal); margin:24px 0 8px; }
.prose p { margin:10px 0; }
.prose blockquote { border-left:3px solid var(--teal); margin:16px 0;
                    padding:6px 16px; color:var(--muted); }
.prose table { margin:16px 0; }
.prose ul, .prose ol { margin:10px 0; }
.prose hr { border:none; border-top:1px solid var(--rule); margin:24px 0; }
.post-nav { display:flex; justify-content:space-between; gap:14px;
            margin:32px 0 0; padding:18px 0 0;
            border-top:1px solid var(--rule); font-size:14px; }
.post-nav a { max-width:45%; }
.post-nav .dir { color:var(--muted); font-size:12px; display:block; }
.blog-list { list-style:none; padding:0; }
.blog-list li { border-bottom:1px solid var(--rule); padding:18px 0; }
.blog-list li:last-child { border-bottom:none; }
.blog-list h3 { font-size:17px; margin:0 0 4px; }
.blog-list h3 a { text-decoration:none; }
.blog-list .summary { color:var(--muted); font-size:14px; margin:4px 0 0; }
.badge { display:inline-block; font-size:12px; font-weight:700;
         padding:2px 9px; border-radius:6px; }
.badge-enacted { background:#065f46; color:#6ee7b7; }
.badge-proposed { background:#713f12; color:#fde68a; }
.badge-rejected { background:#7f1d1d; color:#fca5a5; }
.badge-vetoed { background:#4c1d95; color:#c4b5fd; }
.outcome { border-left:3px solid var(--teal); padding:10px 14px;
           margin:10px 0; }
.outcome .cat { font-size:12px; font-weight:700; color:var(--teal);
                text-transform:uppercase; letter-spacing:.08em; }
.grid2 { display:grid; grid-template-columns:1fr; gap:14px; }
@media (min-width:640px){ .grid2{ grid-template-columns:repeat(2,1fr);} }
.official { font-size:14px; }
.official .role { color:var(--muted); font-size:13px; }
"""


def page(title, description, body, canonical, depth=0,
         og_type="website", og_extra=""):
    p = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" type="application/rss+xml" title="AI GridWatch Blog"
      href="{SITE_URL}/blog/feed.xml">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="{og_type}">
{og_extra}
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
  <a href="{p}moratoriums.html">Moratoriums</a>
  <a href="{p}impact.html">Calculator</a>
  <a href="{p}companies/index.html">Companies</a>
  <a href="{p}blog/index.html">Blog</a>
  <a class="cta" href="{APP_URL}">Open the toolkit &rarr;</a>
</nav>
{body}
<footer>
  <a href="{p}about.html">About</a> · <a href="{p}search.html">Search</a>
  · <a href="{p}dividend.html">Data dividend calculator</a>
  <br>AI GridWatch — community energy intelligence. Planning estimates, not
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
  <div class="stat"><b>{twh:,.0f} TWh</b><span>estimated annual electricity, all 50 states + D.C.</span></div>
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
  <h2>Latest from the blog</h2>
  <div class="grid3">
    {"".join(
        f'<div class="card"><p class="muted" style="margin-bottom:4px">'
        f'{s["date"].strftime("%b %-d")}</p>'
        f'<h3><a href="blog/{s["id"]}.html">'
        f'{esc(s["title"].replace(chr(92) + "$", "$"))}</a></h3></div>'
        for s in _sorted_posts()[:3]
    )}
  </div>
  <p class="muted" style="margin-top:10px">
    <a href="blog/index.html">All posts &rarr;</a></p>
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


def _status_badge(status):
    cls = f"badge-{status.lower().replace(' ', '-')}"
    return f'<span class="badge {cls}">{esc(status)}</span>'


def build_state(state):
    prof = STATE_GRID_PROFILES[state]
    row = STATE_DC_DF[STATE_DC_DF["state"] == state]
    dc_count = int(row.iloc[0]["dc_count"]) if not row.empty else 0
    twh = row.iloc[0]["twh_year"] if not row.empty else 0.0
    puc_row = STATE_PUCS_DF[STATE_PUCS_DF["state"] == state]
    abbrev = _ABBREV.get(state, "")
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
            f"<td>{_status_badge(str(m.status))}</td>"
            f"<td>{esc(str(m.note))}</td></tr>"
            for m in moras.itertuples())
        mora_html = (
            f'<section><h2>Pushback already happening in {esc(state)}</h2>'
            f'<table><tr><th>Where</th><th>Level</th><th>Status</th>'
            f'<th>Note</th></tr>{rows}</table>'
            f'{provenance_html("MORATORIUMS_DF")}</section>')

    # DC sites in this state
    sites = DC_SITES_DF[DC_SITES_DF["state"] == abbrev]
    sites_html = ""
    if not sites.empty:
        site_rows = "\n".join(
            f"<tr><td>{esc(str(s.operator))}</td>"
            f"<td>{esc(str(s.location))}</td>"
            f"<td>{esc(str(s.tenant)) if str(s.tenant) != 'nan' else '—'}</td>"
            f"<td>{esc(str(s.filing_llc)) if str(s.filing_llc) != 'nan' else '—'}</td></tr>"
            for s in sites.itertuples())
        sites_html = (
            f'<section><h2>Known data center campuses in {esc(state)}</h2>'
            f'<table><tr><th>Operator</th><th>Location</th>'
            f'<th>Tenant</th><th>Filing LLC</th></tr>'
            f'{site_rows}</table>'
            f'{provenance_html("DC_SITES_DF")}</section>')

    # Existing-facility directory link-out. DataCenterMap's state slugs are
    # exactly slugify(state) for all 51 — verified against the live /usa/ index,
    # not guessed. Their counts are deliberately not reproduced here: the
    # directory is colocation-weighted (a carrier hotel counts the same as a
    # gigawatt campus), so it would contradict the dc_count stat above.
    # 21 states have no rows in DC_SITES_DF, so the lead sentence can't assume
    # a campus table sits above it.
    if sites.empty:
        dcmap_lead = (
            f'GridWatch does not yet track a named hyperscale campus in '
            f'{esc(state)}, but that does not mean the state has none. '
            f'DataCenterMap keeps a public directory of existing facilities '
            f'— street addresses included — for {esc(state)}.')
    else:
        dcmap_lead = (
            f'The campuses above are the ones GridWatch tracks by operator and '
            f'filing LLC. For the full inventory — street addresses of every '
            f'existing facility, including the smaller colocation and network '
            f'sites — DataCenterMap keeps a public directory for {esc(state)}.')

    dcmap_html = (
        f'<section><h2>Every data center already built in {esc(state)}</h2>'
        f'<p>{dcmap_lead}</p>'
        f'<p><a class="btn ghost" href="{DCMAP_BASE}/{slugify(state)}/" '
        f'rel="nofollow noopener">Browse the {esc(state)} directory &rarr;</a></p>'
        f'<p class="muted">Two caveats before you cite it at a hearing: it lists '
        f'facilities that already exist, so a newly proposed campus will not '
        f'appear; and it counts a small network room the same as a hyperscale '
        f'campus, so the facility count is not a measure of power draw or '
        f'community impact.</p>'
        f'</section>')

    # CBA benchmarks for this state
    state_cbas = [b for b in CBA_BENCHMARKS if b["state"] == abbrev]
    cba_html = ""
    if state_cbas:
        items = "\n".join(
            f"<li><strong>{esc(b['community'])}</strong> ({esc(b['company'])}) "
            f"— {esc(b['won'])}</li>"
            for b in state_cbas)
        cba_html = (
            f'<section><h2>What communities in {esc(state)} have won</h2>'
            f'<ul>{items}</ul></section>')

    # Moratorium outcomes / case studies for this state
    state_outcomes = [o for o in MORATORIUM_OUTCOMES if o["state"] == abbrev]
    outcome_html = ""
    if state_outcomes:
        cards = "\n".join(
            f'<div class="outcome"><div class="cat">{esc(o["category"])}</div>'
            f'<p><strong>{esc(o["locality"])}</strong> — '
            f'{esc(o["headline"])}</p>'
            f'<p class="muted">{esc(o["outcome"])}</p></div>'
            for o in state_outcomes)
        outcome_html = (
            f'<section><h2>Case studies</h2>{cards}</section>')

    # Local officials (curated, only for covered localities)
    officials = LOCAL_OFFICIALS_DF[LOCAL_OFFICIALS_DF["state"] == abbrev]
    bodies = LOCAL_BODIES_DF[LOCAL_BODIES_DF["state"] == abbrev]
    officials_html = ""
    if not officials.empty:
        for _, b in bodies.iterrows():
            loc = b["locality"]
            loc_officials = officials[officials["locality"] == loc]
            people = "\n".join(
                f'<div class="official"><strong>{esc(o["name"])}</strong>'
                f'<span class="role"> — {esc(o["role"])}'
                f'{", " + esc(o["district"]) if o.get("district") else ""}'
                f'</span></div>'
                for _, o in loc_officials.iterrows())
            comment = (f'<p class="muted">Public comment: '
                       f'{esc(b["comment_process"])}</p>'
                       if b.get("comment_process") else "")
            meets = (f'<p class="muted">Meets: {esc(b["meets"])}'
                     f'{" · " + esc(b["where"]) if b.get("where") else ""}'
                     f'</p>' if b.get("meets") else "")
            agenda = (f'<p class="muted"><a href="{esc(b["agenda_url"])}">'
                      f'Agendas &amp; minutes</a></p>'
                      if b.get("agenda_url") else "")
            officials_html += (
                f'<section><h2>{esc(loc)} — {esc(b["body"])}</h2>'
                f'<div class="grid2">{people}</div>'
                f'{meets}{comment}{agenda}'
                f'<p class="src">Source: <a href="{esc(b["source"])}">'
                f'{esc(b["source"][:60])}</a> · as of {b["as_of"]}</p>'
                f'</section>')

    # Municipal league
    muni = STATE_MUNI_LEAGUES.get(abbrev)
    muni_html = ""
    if muni:
        muni_html = (
            f'<p class="muted" style="margin-top:16px">'
            f'State municipal league: '
            f'<a href="{esc(muni[1])}">{esc(muni[0])}</a></p>')

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
{provenance_html("STATE_DC_DF")}
{puc_html}
{mora_html}
{outcome_html}
{sites_html}
{dcmap_html}
{cba_html}
{officials_html}
{muni_html}
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


_ABBREV_TO_FULL = {v: k for k, v in _ABBREV.items()}


def _build_us_map_svg():
    paths = []
    for abbr, d in US_MAP_PATHS.items():
        full = _ABBREV_TO_FULL.get(abbr, abbr)
        slug = slugify(full)
        paths.append(
            f'<a href="/states/{slug}.html">'
            f'<path d="{d}" data-state="{esc(full)}" data-abbr="{abbr}"/>'
            f'</a>')
    labels = []
    for abbr, (x, y) in US_MAP_LABELS.items():
        labels.append(f'<text x="{x}" y="{y}">{abbr}</text>')
    return (
        f'<svg class="us-map" viewBox="{US_MAP_VIEWBOX}" '
        f'xmlns="http://www.w3.org/2000/svg">\n'
        + "\n".join(paths) + "\n" + "\n".join(labels)
        + "\n</svg>"
    )


def build_states_index():
    links = "\n".join(
        f'<a href="/states/{slugify(s)}.html">{esc(s)}</a>'
        for s in sorted(STATE_GRID_PROFILES))
    us_map = _build_us_map_svg()
    body = f"""
<header>
  <div class="kicker">State briefings</div>
  <h1>Pick your state</h1>
  <p class="sub">Facilities, grid impact, water stress, and your public
  utility commission — one page per state. Click a state on the map or
  choose from the list below.</p>
</header>
<section>{us_map}</section>
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


def _md_to_html(text):
    """Convert markdown body to HTML, stripping Streamlit LaTeX escapes."""
    text = text.replace("\\$", "$")
    md = markdown.Markdown(extensions=["tables"])
    return md.convert(text)


def _sorted_posts():
    return sorted(BLOG_STORIES, key=lambda s: s["date"], reverse=True)


def build_blog_index():
    posts = _sorted_posts()
    items = ""
    for s in posts:
        title_clean = s["title"].replace("\\$", "$")
        summary_clean = s["summary"].replace("\\$", "$")
        items += (
            f'<li><div class="post-meta">{s["date"].strftime("%b %-d, %Y")}'
            f"</div>"
            f'<h3><a href="{s["id"]}.html">{esc(title_clean)}</a></h3>'
            f'<p class="summary">{esc(summary_clean)}</p></li>\n'
        )
    body = f"""
<header>
  <div class="kicker">Blog</div>
  <h1>Analysis &amp; explainers</h1>
  <p class="sub">Deep dives on the forces shaping data center development —
  capacity markets, moratoriums, corporate strategy, and the numbers behind
  your electric bill.</p>
</header>
<section>
  <ul class="blog-list">{items}</ul>
</section>
"""
    return page(
        "Blog — AI GridWatch",
        "Analysis and explainers on data center development, grid impact, "
        "and community advocacy from AI GridWatch.",
        body, f"{SITE_URL}/blog/", depth=1)


def build_blog_post(story, prev_post, next_post):
    title_clean = story["title"].replace("\\$", "$")
    summary_clean = story["summary"].replace("\\$", "$")
    body_html = _md_to_html(story["body"])
    tags_html = " ".join(
        f'<span class="tag">{esc(t)}</span>' for t in story.get("tags", []))

    nav = '<div class="post-nav">'
    if prev_post:
        prev_title = prev_post["title"].replace("\\$", "$")
        nav += (f'<a href="{prev_post["id"]}.html">'
                f'<span class="dir">&larr; Previous</span>'
                f'{esc(prev_title)}</a>')
    else:
        nav += "<span></span>"
    if next_post:
        next_title = next_post["title"].replace("\\$", "$")
        nav += (f'<a href="{next_post["id"]}.html" style="text-align:right">'
                f'<span class="dir">Next &rarr;</span>'
                f'{esc(next_title)}</a>')
    else:
        nav += "<span></span>"
    nav += "</div>"

    body = f"""
<header>
  <div class="kicker">Blog</div>
  <h1>{esc(title_clean)}</h1>
  <div class="post-meta">{story["date"].strftime("%b %-d, %Y")}
  &middot; {esc(story["author"])}</div>
  <div class="tags">{tags_html}</div>
  <p class="sub">{esc(summary_clean)}</p>
</header>
<section class="prose">
  {body_html}
</section>
{nav}
"""
    og_extra = (
        f'<meta property="article:published_time" '
        f'content="{story["date"].isoformat()}">\n'
        f'<meta property="article:author" content="{esc(story["author"])}">')
    return page(
        f"{title_clean} — AI GridWatch",
        summary_clean,
        body, f"{SITE_URL}/blog/{story['id']}", depth=1,
        og_type="article", og_extra=og_extra)


def build_impact_calculator():
    import json
    profiles_json = json.dumps(
        {s: STATE_GRID_PROFILES[s] for s in sorted(STATE_GRID_PROFILES)})

    state_options = "\n".join(
        f'<option value="{esc(s)}">{esc(s)}</option>'
        for s in sorted(STATE_GRID_PROFILES))

    body = f"""
<header>
  <div class="kicker">Community calculator</div>
  <h1>What does a data center cost your community?</h1>
  <p class="sub">Pick a size and your state. The calculator estimates annual
  electricity, water draw, carbon emissions, rate pressure, and the CBA
  target your community should be negotiating — all sourced from the same
  model the full toolkit uses.</p>
</header>
<section>
  <h2>Facility size</h2>
  <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap">
    <input type="range" id="mw-slider" min="10" max="500" value="100"
           step="10" style="flex:1;min-width:200px;accent-color:var(--teal)">
    <span id="mw-label" style="font-size:28px;font-weight:700;color:var(--teal);min-width:80px">100 MW</span>
  </div>
  <p class="muted" style="margin-top:6px">10 MW = small edge facility &middot;
  100 MW = typical hyperscaler campus &middot; 500 MW = mega-project</p>
</section>
<section>
  <h2>Your state</h2>
  <select id="state-select" style="background:var(--card);color:var(--ink);
    border:1px solid var(--rule);border-radius:8px;padding:8px 14px;
    font-size:15px;width:100%;max-width:320px">
    {state_options}
  </select>
</section>
<div class="stats" id="results">
  <div class="stat"><b id="r-energy">—</b><span>annual electricity (MWh)</span></div>
  <div class="stat"><b id="r-homes">—</b><span>homes equivalent</span></div>
  <div class="stat"><b id="r-water">—</b><span>annual water (million gal)</span></div>
  <div class="stat"><b id="r-co2">—</b><span>annual CO&#8322; (metric tons)</span></div>
</div>
<section>
  <h2>Economic impact</h2>
  <div class="grid2">
    <div class="card">
      <h3>Rate pressure</h3>
      <p>Residents pay <strong id="r-ratio">—</strong>&times; what the data
      center pays per kWh (<span id="r-resrate">—</span> vs $0.05).</p>
    </div>
    <div class="card">
      <h3>CBA target</h3>
      <p>At 2% of estimated investment, your community should negotiate at
      least <strong id="r-dividend">—</strong>/year in community benefits.</p>
    </div>
  </div>
  <p class="muted" style="margin-top:8px">Grid carbon:
  <span id="r-gco2">—</span> gCO&#8322;/kWh &middot; Water stress:
  <span id="r-stress">—</span> &middot; Cooling: evaporative (PUE 1.12)</p>
</section>
<section>
  <h2>What to do with these numbers</h2>
  <p>Print this page, or use the full toolkit to generate a complete action
  pack — a meeting brief, comment scripts, letters to officials, and a
  community flyer with these numbers baked in.</p>
  <p><a class="btn" href="{APP_URL}">Generate your action pack &rarr;</a>
  <a class="btn ghost" href="health-risks.html">The health risks, sourced</a></p>
</section>
<script>
(function() {{
  var P = {profiles_json};
  var PUE = 1.12, WG = 2.0, HOME = 10500, INV = 2000000, DIV = 0.02, DCR = 0.05;
  var slider = document.getElementById('mw-slider');
  var label = document.getElementById('mw-label');
  var sel = document.getElementById('state-select');
  function fmt(n) {{
    if (n >= 1e9) return (n/1e9).toFixed(1) + 'B';
    if (n >= 1e6) return (n/1e6).toFixed(1) + 'M';
    if (n >= 1e3) return Math.round(n).toLocaleString();
    return n.toFixed(1);
  }}
  function usd(n) {{
    if (n >= 1e9) return '$' + (n/1e9).toFixed(1) + 'B';
    if (n >= 1e6) return '$' + (n/1e6).toFixed(1) + 'M';
    if (n >= 1e3) return '$' + Math.round(n).toLocaleString();
    return '$' + n.toFixed(0);
  }}
  function calc() {{
    var mw = +slider.value;
    var st = sel.value;
    var prof = P[st] || {{rate:0.12, gco2:400, water_stress:'medium'}};
    label.textContent = mw + ' MW';
    var kwh = mw * 8760 * PUE * 1000;
    var mwh = kwh / 1000;
    document.getElementById('r-energy').textContent = fmt(mwh);
    document.getElementById('r-homes').textContent = fmt(kwh / HOME);
    document.getElementById('r-water').textContent = (kwh * WG / 1e6).toFixed(1);
    document.getElementById('r-co2').textContent = fmt(mwh * prof.gco2 / 1e6);
    document.getElementById('r-ratio').textContent = (prof.rate / DCR).toFixed(1);
    document.getElementById('r-resrate').textContent = '$' + prof.rate.toFixed(3);
    document.getElementById('r-dividend').textContent = usd(mw * INV * DIV);
    document.getElementById('r-gco2').textContent = prof.gco2;
    document.getElementById('r-stress').textContent = prof.water_stress;
  }}
  slider.addEventListener('input', calc);
  sel.addEventListener('change', calc);
  calc();
}})();
</script>
"""
    return page(
        "Data center impact calculator — AI GridWatch",
        "Estimate the electricity, water, carbon, and rate impact of a "
        "data center in your state — free community calculator.",
        body, f"{SITE_URL}/impact")


def build_moratoriums():
    total = len(MORATORIUMS_DF)
    n_states = MORATORIUMS_DF["state"].nunique()
    enacted = len(MORATORIUMS_DF[MORATORIUMS_DF["status"] == "Enacted"])
    proposed = len(MORATORIUMS_DF[MORATORIUMS_DF["status"] == "Proposed"])

    rows = "\n".join(
        f"<tr><td>{esc(str(m.locality))}</td>"
        f"<td><a href=\"states/{slugify(STATE_PUCS_DF[STATE_PUCS_DF['abbrev'] == m.state].iloc[0]['state'])}.html\">"
        f"{esc(str(m.state))}</a></td>"
        f"<td>{esc(str(m.level))}</td>"
        f"<td>{_status_badge(str(m.status))}</td>"
        f"<td>{esc(str(m.when))}</td>"
        f"<td>{esc(str(m.note))}</td></tr>"
        for m in MORATORIUMS_DF.itertuples())

    outcomes = "\n".join(
        f'<div class="outcome"><div class="cat">{esc(o["category"])}</div>'
        f'<p><strong>{esc(o["locality"])}, {esc(o["state"])}</strong> — '
        f'{esc(o["headline"])}</p>'
        f'<p class="muted">{esc(o["outcome"])}</p></div>'
        for o in MORATORIUM_OUTCOMES)

    body = f"""
<header>
  <div class="kicker">Community tracker</div>
  <h1>Data center moratoriums &amp; pushback</h1>
  <p class="sub">Every community that pressed pause on data center
  development — bans, moratoria, zoning fights, and the outcomes.
  Updated as new actions are reported.</p>
</header>
<div class="stats">
  <div class="stat"><b>{total}</b><span>tracked actions</span></div>
  <div class="stat"><b>{n_states}</b><span>states</span></div>
  <div class="stat"><b>{enacted}</b><span>enacted</span></div>
  <div class="stat"><b>{proposed}</b><span>proposed or pending</span></div>
</div>
<section>
  <h2>All tracked moratoriums</h2>
  <div style="overflow-x:auto">
  <table><tr><th>Locality</th><th>State</th><th>Level</th>
  <th>Status</th><th>When</th><th>Note</th></tr>
  {rows}</table>
  </div>
  {provenance_html("MORATORIUMS_DF")}
  <p class="muted" style="margin-top:10px">See the full interactive map and
  filters in the <a href="{APP_URL}">GridWatch toolkit</a>.</p>
</section>
<section>
  <h2>What happened next: case studies</h2>
  <p class="muted" style="margin-bottom:14px">Six communities that took
  action — what they won, what they lost, and what changed.</p>
  {outcomes}
</section>
<section>
  <h2>Your community is next?</h2>
  <p>The toolkit generates a full action pack — impact numbers, CBA targets,
  meeting scripts, and letters — customized for your state and situation.</p>
  <p><a class="btn" href="{APP_URL}">Start here &rarr;</a>
  <a class="btn ghost" href="health-risks.html">The health risks, sourced</a></p>
</section>
"""
    return page(
        "Data center moratoriums & community pushback — AI GridWatch",
        f"{total} data center moratoriums and community actions tracked "
        f"across {n_states} states, with case study outcomes.",
        body, f"{SITE_URL}/moratoriums")


_HYPERSCALERS = [
    {
        "slug": "google", "name": "Google", "report": "FY2025",
        "d": GOOGLE_2025_HEADLINE,
        "twh": GOOGLE_2025_HEADLINE["dc_twh"],
        "pue": GOOGLE_2025_HEADLINE["fleet_pue"],
        "scope2_loc": GOOGLE_2025_HEADLINE["scope2_location_tco2e"],
        "scope2_mkt": GOOGLE_2025_HEADLINE["scope2_market_tco2e"],
        "water_mgal": GOOGLE_2025_HEADLINE["water_consumption_mgal"],
        "renewable": "65% CFE",
        "water_note": f'{GOOGLE_2025_HEADLINE["water_replenished_pct"]}% replenished',
        "extra": [
            ("YoY electricity growth", f'+{GOOGLE_2025_HEADLINE["yoy_electricity_growth_pct"]}%'),
            ("Clean energy signed", f'{GOOGLE_2025_HEADLINE["clean_energy_gw_signed"]} GW'),
            ("Avoided emissions", f'{GOOGLE_2025_HEADLINE["avoided_tco2e_m"]}M tCO2e'),
            ("Gemini efficiency", f'{GOOGLE_2025_HEADLINE["gemini_energy_improvement_x"]}x vs 2019 model'),
        ],
    },
    {
        "slug": "meta", "name": "Meta", "report": "FY2024",
        "d": META_2024_HEADLINE,
        "twh": META_2024_HEADLINE["dc_twh"],
        "pue": META_2024_HEADLINE["fleet_pue"],
        "scope2_loc": META_2024_HEADLINE["scope2_location_tco2e"],
        "scope2_mkt": META_2024_HEADLINE["scope2_market_tco2e"],
        "water_mgal": round(META_2024_HEADLINE["water_consumption_ml"] * 0.264172),
        "renewable": f'{META_2024_HEADLINE["renewable_match_pct"]}% renewable',
        "water_note": f'{round(META_2024_HEADLINE["water_restoration_ml"] * 0.264172):,} Mgal restored',
        "extra": [
            ("Fleet WUE", f'{META_2024_HEADLINE["fleet_wue"]} L/kWh'),
            ("LEED Gold", f'{META_2024_HEADLINE["leed_gold_pct"]}% of campuses'),
            ("Scope 3", f'{META_2024_HEADLINE["scope3_tco2e"]:,} tCO2e'),
        ],
    },
    {
        "slug": "microsoft", "name": "Microsoft", "report": "FY2025",
        "d": MICROSOFT_ENV_HEADLINE,
        "twh": MICROSOFT_ENV_HEADLINE["dc_twh"],
        "pue": MICROSOFT_ENV_HEADLINE["pue"],
        "scope2_loc": int(MICROSOFT_ENV_HEADLINE["scope2_location_mt"] * 1e6),
        "scope2_mkt": int(MICROSOFT_ENV_HEADLINE["scope2_market_mt"] * 1e6),
        "water_mgal": MICROSOFT_ENV_HEADLINE["water_consumption_mgal"],
        "renewable": f'{MICROSOFT_ENV_HEADLINE["renewable_pct"]}% renewable',
        "water_note": f'{MICROSOFT_ENV_HEADLINE["water_replenish_pct"]}% replenished',
        "est": True,
        "extra": [
            ("Total emissions", f'{MICROSOFT_ENV_HEADLINE["total_emissions_mt"]:.1f} Mt CO2e'),
            ("YoY emissions growth", f'+{MICROSOFT_ENV_HEADLINE["yoy_emissions_growth_pct"]}%'),
        ],
        "notes": MICROSOFT_ENV_HEADLINE.get("notes", ""),
    },
    {
        "slug": "aws", "name": "Amazon (AWS)", "report": "CY2025",
        "d": AWS_ENV_HEADLINE,
        "twh": AWS_ENV_HEADLINE["dc_twh"],
        "pue": AWS_ENV_HEADLINE["pue"],
        "scope2_loc": int(AWS_ENV_HEADLINE["scope2_location_mt"] * 1e6),
        "scope2_mkt": int(AWS_ENV_HEADLINE["scope2_market_mt"] * 1e6),
        "water_mgal": AWS_ENV_HEADLINE["water_consumption_mgal"],
        "renewable": f'{AWS_ENV_HEADLINE["renewable_pct"]}% renewable',
        "water_note": f'{AWS_ENV_HEADLINE["water_replenish_pct"]}% toward water-positive',
        "est": True,
        "extra": [
            ("Total Amazon emissions", f'{AWS_ENV_HEADLINE["total_emissions_mt"]:.1f} Mt CO2e'),
            ("YoY emissions growth", f'+{AWS_ENV_HEADLINE["yoy_emissions_growth_pct"]}%'),
        ],
        "notes": AWS_ENV_HEADLINE.get("notes", ""),
    },
]


_OPERATORS = [
    {
        "slug": "equinix", "name": "Equinix", "report": "FY2024",
        "d": EQUINIX_2024_HEADLINE,
        "twh": 8.17, "pue": 1.39,
        "scope2_loc": 2_645_700, "scope2_mkt": 253_300,
        "water_mgal": 1_104, "renewable": "96% renewable",
        "water_note": "37% non-potable; WUE 0.95",
        "scale": "268 data centers · 74 markets · 35 countries",
        "revenue": "$8.7B",
        "est_twh": True,
        "extra": [
            ("Scope 1", "59,400 tCO2e"),
            ("Scope 3", "1.44M tCO2e"),
            ("Net zero target", "2040 (SBTi validated)"),
            ("Heat exported", "14.5 GWh to communities (+245% YoY)"),
        ],
    },
    {
        "slug": "digital-realty", "name": "Digital Realty", "report": "FY2024",
        "d": DIGITAL_REALTY_2024_HEADLINE,
        "pue": 1.38, "wue": 0.59,
        "scope2_loc": 3_311_323, "scope2_mkt": 948_175,
        "renewable": "93% renewable",
        "water_note": "45% non-potable; WUE 0.59",
        "scale": "300+ data centers · 55+ metros · 30+ countries",
        "revenue": "$6.1B",
        "extra": [
            ("Scope 1", "51,745 tCO2e"),
            ("Scope 3", "1.46M tCO2e (+16.9% YoY)"),
            ("EMEA PUE", "1.31; new builds designed at 1.20"),
            ("EU carbon-neutral", "42% of European IT capacity"),
        ],
        "notes": "Absolute TWh and water consumption not disclosed. "
                 "PUE/WUE/renewable from FY2025 report; Scope 1/2/3 "
                 "from FY2024. SBTi validation status unconfirmed.",
    },
    {
        "slug": "edgeconnex", "name": "EdgeConneX", "report": "FY2024",
        "d": EDGECONNEX_2024_HEADLINE,
        "twh": 1.66, "pue": 1.33,
        "scope2_loc": None, "scope2_mkt": 0,
        "water_mgal": 25, "renewable": "90% renewable",
        "water_note": "93% water-free sites; 25 Mgal",
        "scale": "410 MW capacity · 20+ countries",
        "extra": [
            ("Scope 1", "17,925 tCO2e"),
            ("Scope 3", "498,287 tCO2e"),
            ("SBTi S1+2 target", "Met (−50.4%)"),
            ("SBTi S3 target", "Exceeded (−64%)"),
        ],
    },
    {
        "slug": "stack", "name": "STACK Infrastructure", "report": "FY2023",
        "d": STACK_2023_HEADLINE,
        "pue": 1.35,
        "scope2_loc": 295_400, "scope2_mkt": None,
        "renewable": "100% renewable (since 2021)",
        "water_note": "WUE 1.08; 34.8M gal saved via reclaimed water",
        "scale": "37+ facilities · 22 markets · >7 GW capacity",
        "extra": [
            ("Scope 1", "3,900 tCO2e"),
            ("Scope 3", "460,300 tCO2e"),
            ("SBTi", "Committed (Sept 2024)"),
        ],
        "notes": "Scope 2 boundary (location vs market) unclear in report. "
                 ">1,000 GWh procured in 2023.",
    },
    {
        "slug": "cyrusone", "name": "CyrusOne", "report": "FY2023",
        "d": CYRUSONE_2023_HEADLINE,
        "pue": 1.46,
        "scope2_loc": None, "scope2_mkt": 402_058,
        "renewable": "61.6% carbon-free",
        "water_note": "Net Positive Water at 12 facilities",
        "scale": "50+ data centers globally",
        "extra": [
            ("Scope 1", "27,710 tCO2e"),
            ("Scope 3", "474,137 tCO2e"),
            ("vs SBTi target", "−29.4% since 2021 (exceeded by >16 ppts)"),
            ("EcoVadis", "Gold (top 5%) — 3rd consecutive year"),
            ("Green financing", "$11.2B sustainability-linked (2024)"),
        ],
        "notes": "Private since April 2022 (KKR/GIP, $15B). TWh and "
                 "absolute water consumption not disclosed.",
    },
    {
        "slug": "vantage", "name": "Vantage Data Centers", "report": "CY2023",
        "d": VANTAGE_2023_HEADLINE,
        "pue": 1.26,
        "scope2_loc": 49_420, "scope2_mkt": None,
        "renewable": "4 of 34 campuses >99% renewable",
        "water_note": "Near-zero water (air-cooled design)",
        "scale": "34 campuses · 5 continents · >2 GW capacity",
        "extra": [
            ("Scope 1", "4,371 tCO2e"),
            ("Scope 1+2 total", "53,791 tCO2e (+145% YoY)"),
            ("Net zero target", "S1+2 by 2030; all scopes by 2040"),
        ],
        "notes": "PUE is annualized design average, not operational. "
                 "Market-based Scope 2 deferred pending verification. "
                 "Scope 3 not quantified in absolute terms.",
    },
]

_LIMITED_DISCLOSURE = [
    {
        "slug": "coreweave", "name": "CoreWeave", "report": "FY2025",
        "d": COREWEAVE_PROFILE,
        "scale": "43 data centers · >850 MW active · ~3.1 GW contracted",
        "revenue": "$5.13B",
        "disclosure": "none",
        "gap_text": "No sustainability report. No CDP response. No Scope "
                    "1/2/3 inventory. No PUE or WUE figures. Marketing "
                    "claims only (unverified).",
        "context": "IPO March 2025 (NASDAQ: CRWV). Revenue grew from $229M "
                   "(2023) to $5.13B (2025). GPU-specialized cloud building "
                   "at massive scale with zero environmental disclosure.",
    },
    {
        "slug": "qts", "name": "QTS (Blackstone)", "report": "FY2024",
        "d": QTS_PROFILE,
        "scale": ">2 GW contracted capacity",
        "disclosure": "partial",
        "reported": [
            ("WUE", "0.82 L/kWh (−27% YoY)"),
            ("Carbon-free electricity", "100%"),
            ("Water-free new builds", "100% of greenfield"),
        ],
        "not_reported": ["Fleet PUE", "Scope 1/2/3 (absolute)",
                         "Total electricity (TWh)", "Revenue"],
        "context": "Private since 2021 (Blackstone, $10B). Reports strong "
                   "water and clean-energy metrics but omits fleet PUE and "
                   "audited emissions totals.",
    },
    {
        "slug": "switch", "name": "Switch (DigitalBridge)", "report": "CY2024",
        "d": SWITCH_PROFILE,
        "scale": "Las Vegas 315 MW · Tahoe Reno up to 2 GW planned",
        "disclosure": "marketing only",
        "reported": [
            ("PUE (claimed)", "1.18"),
            ("Renewable (claimed)", "100% since 2016"),
        ],
        "not_reported": ["Audited sustainability report", "Scope 1/2/3",
                         "WUE", "Absolute water consumption", "Revenue"],
        "context": "Private since 2023 (DigitalBridge). All environmental "
                   "claims come from marketing pages — no downloadable "
                   "report, no third-party verification found. $20B in "
                   "green financing raised since 2024.",
    },
    {
        "slug": "compass", "name": "Compass Datacenters", "report": "FY2024",
        "d": COMPASS_PROFILE,
        "scale": "Total capacity not disclosed",
        "disclosure": "partial",
        "reported": [
            ("Design PUE", "1.25"),
            ("WUE", "0 (waterless cooling)"),
            ("Embodied carbon", "−33% per MW (2022-2024)"),
        ],
        "not_reported": ["Scope 1/2 for data centers (only corporate "
                         "offices reported)", "Total capacity / campus count",
                         "Revenue"],
        "context": "Build-to-suit model: tenants control operations, so "
                   "Compass's Scope 1/2 covers only corporate offices "
                   "(~3,700 tCO2e). The real DC energy footprint sits in "
                   "Scope 3 Category 13 — easy to misread as 'low-impact.'",
    },
]


def _fmt_co2(t):
    if t >= 1e6:
        return f"{t / 1e6:.1f}M"
    if t >= 1e3:
        return f"{t / 1e3:.0f}K"
    return f"{t:,.0f}"


def _co2_cell(val):
    return _fmt_co2(val) if val is not None else "—"


def build_scorecards_index():
    def _cards(items):
        out = ""
        for h in items:
            twh = h.get("twh")
            twh_str = (f'{twh} TWh{"*" if h.get("est_twh") or h.get("est") else ""}'
                       if twh else "")
            pue = h.get("pue")
            pue_str = f'PUE {pue}' if pue else ""
            detail = " · ".join(filter(None, [h["report"], twh_str, pue_str]))
            out += (
                f'<a href="{h["slug"]}.html" class="card" '
                f'style="text-decoration:none;display:block">'
                f'<h3>{esc(h["name"])}</h3>'
                f'<p class="muted">{detail}</p></a>\n')
        return out

    def _comparison_rows(items):
        rows = ""
        for h in items:
            twh = h.get("twh")
            twh_str = (f'{twh}{"*" if h.get("est_twh") or h.get("est") else ""}'
                       if twh else "—")
            water = h.get("water_mgal")
            water_str = f"{water:,}" if water else "—"
            rows += (
                f'<tr><td><a href="{h["slug"]}.html">'
                f'{esc(h["name"])}</a></td>'
                f'<td>{twh_str}</td>'
                f'<td>{h.get("pue", "—")}</td>'
                f'<td>{_co2_cell(h.get("scope2_loc"))}</td>'
                f'<td>{_co2_cell(h.get("scope2_mkt"))}</td>'
                f'<td>{water_str}</td>'
                f'<td>{esc(h.get("renewable", "—"))}</td></tr>')
        return rows

    gap_rows = ""
    for ld in _LIMITED_DISCLOSURE:
        gap_rows += (
            f'<tr><td><a href="{ld["slug"]}.html">'
            f'{esc(ld["name"])}</a></td>'
            f'<td>{esc(ld["scale"])}</td>'
            f'<td><span class="badge badge-{"rejected" if ld["disclosure"] == "none" else "proposed"}">'
            f'{esc(ld["disclosure"])}</span></td></tr>')

    body = f"""
<header>
  <div class="kicker">Corporate scorecards</div>
  <h1>Who builds the AI grid — and what they disclose</h1>
  <p class="sub">Environmental data from 14 data center companies —
  hyperscalers, operators, and developers — side by side. The gap between
  what they claim and what they report is the gap your community should
  ask about.</p>
</header>
<section>
  <h2>Hyperscalers</h2>
  <p class="muted">The four companies that build and operate their own AI
  infrastructure at the largest scale.</p>
  <div style="overflow-x:auto">
  <table>
    <tr><th></th><th>DC TWh</th><th>PUE</th><th>Scope 2 (location)</th>
    <th>Scope 2 (market)</th><th>Water (Mgal)</th><th>Renewable</th></tr>
    {_comparison_rows(_HYPERSCALERS)}
  </table>
  </div>
  <p class="muted" style="margin-top:6px">* DC-only TWh and location-based
  Scope 2 are estimates; these companies do not break out data-center-only
  electricity.</p>
  <div class="grid2">{_cards(_HYPERSCALERS)}</div>
</section>
<section>
  <h2>Data center operators &amp; developers</h2>
  <p class="muted">Companies that build, own, or lease hyperscale data center
  campuses — the facilities where AI workloads actually run.</p>
  <div style="overflow-x:auto">
  <table>
    <tr><th></th><th>DC TWh</th><th>PUE</th><th>Scope 2 (location)</th>
    <th>Scope 2 (market)</th><th>Water (Mgal)</th><th>Renewable</th></tr>
    {_comparison_rows(_OPERATORS)}
  </table>
  </div>
  <p class="muted" style="margin-top:6px">— = not disclosed or not applicable.
  * = estimated figure.</p>
  <div class="grid2">{_cards(_OPERATORS)}</div>
</section>
<section>
  <h2>Transparency gaps</h2>
  <p class="muted">These companies build or operate significant data center
  capacity but publish little or no environmental data. That silence is itself
  a data point — ask why.</p>
  <div style="overflow-x:auto">
  <table>
    <tr><th></th><th>Scale</th><th>Disclosure level</th></tr>
    {gap_rows}
  </table>
  </div>
  <div class="grid2">{_cards(_LIMITED_DISCLOSURE)}</div>
</section>
"""
    return page(
        "Corporate environmental scorecards — AI GridWatch",
        "Environmental data for 14 data center companies: hyperscalers, "
        "operators, and developers — side by side.",
        body, f"{SITE_URL}/companies/", depth=1)


def build_scorecard(h):
    est = " (est.)" if h.get("est") else ""
    extras = "\n".join(
        f'<tr><td>{esc(k)}</td><td><strong>{esc(v)}</strong></td></tr>'
        for k, v in h.get("extra", []))
    notes_html = ""
    if h.get("notes"):
        notes_html = (
            f'<div class="ask" style="margin-top:18px">'
            f'<strong>Methodology note:</strong> {esc(h["notes"])}</div>')

    concessions = COMPANY_CONCESSIONS.get(h["name"].split(" (")[0], {})
    concession_html = ""
    if concessions.get("concessions"):
        rows = "\n".join(
            f'<tr><td>{esc(c["where"])}</td><td>{esc(c["year"])}</td>'
            f'<td>{esc(c["what"])}</td></tr>'
            for c in concessions["concessions"])
        concession_html = (
            f'<section><h2>What communities have won from {esc(h["name"])}</h2>'
            f'<p class="muted" style="margin-bottom:10px">'
            f'{esc(concessions.get("pattern", ""))}</p>'
            f'<table><tr><th>Where</th><th>Year</th><th>What</th></tr>'
            f'{rows}</table></section>')

    body = f"""
<header>
  <div class="kicker">Corporate scorecard</div>
  <h1>{esc(h['name'])} environmental profile</h1>
  <p class="sub">Key environmental metrics from the {esc(h['report'])}
  sustainability report. Numbers communities cite at hearings.</p>
</header>
<div class="stats">
  <div class="stat"><b>{h['twh']} TWh{est}</b><span>data center electricity</span></div>
  <div class="stat"><b>{h['pue']}</b><span>fleet PUE</span></div>
  <div class="stat"><b>{_fmt_co2(h['scope2_loc'])}</b><span>Scope 2 (location) tCO2e</span></div>
  <div class="stat"><b>{h['water_mgal']:,}</b><span>water consumption (Mgal)</span></div>
</div>
<section>
  <h2>Key metrics</h2>
  <table>
    <tr><td>Scope 2 (market-based)</td><td><strong>{_fmt_co2(h['scope2_mkt'])} tCO2e</strong></td></tr>
    <tr><td>Renewable / CFE claim</td><td><strong>{esc(h['renewable'])}</strong></td></tr>
    <tr><td>Water stewardship</td><td><strong>{esc(h['water_note'])}</strong></td></tr>
    {extras}
  </table>
  {notes_html}
</section>
{concession_html}
<section>
  <h2>What this means for your community</h2>
  <p>The gap between <strong>market-based</strong> and
  <strong>location-based</strong> Scope 2 emissions shows how much carbon
  the grid actually emits vs. what the company claims after buying renewable
  energy certificates (RECs). A large gap means the facility runs on fossil
  power but papers it over with certificates — your community breathes the
  actual emissions.</p>
  <p><a class="btn" href="{APP_URL}">Run the numbers for your community &rarr;</a>
  <a class="btn ghost" href="../companies/index.html">All scorecards</a></p>
</section>
"""
    return page(
        f"{h['name']} environmental scorecard — AI GridWatch",
        f"Environmental data for {h['name']}: {h['twh']} TWh, PUE "
        f"{h['pue']}, water and carbon metrics from {h['report']}.",
        body, f"{SITE_URL}/companies/{h['slug']}", depth=1)


def build_operator_scorecard(h):
    extras = "\n".join(
        f'<tr><td>{esc(k)}</td><td><strong>{esc(v)}</strong></td></tr>'
        for k, v in h.get("extra", []))
    notes_html = ""
    if h.get("notes"):
        notes_html = (
            f'<div class="ask" style="margin-top:18px">'
            f'<strong>Methodology note:</strong> {esc(h["notes"])}</div>')

    stats = []
    if h.get("twh"):
        est = "*" if h.get("est_twh") else ""
        stats.append(f'<div class="stat"><b>{h["twh"]} TWh{est}</b>'
                     f'<span>electricity</span></div>')
    if h.get("pue"):
        stats.append(f'<div class="stat"><b>{h["pue"]}</b>'
                     f'<span>fleet PUE</span></div>')
    if h.get("scope2_loc") is not None:
        stats.append(f'<div class="stat"><b>{_fmt_co2(h["scope2_loc"])}</b>'
                     f'<span>Scope 2 (location) tCO2e</span></div>')
    elif h.get("scope2_mkt") is not None:
        stats.append(f'<div class="stat"><b>{_fmt_co2(h["scope2_mkt"])}</b>'
                     f'<span>Scope 2 (market) tCO2e</span></div>')
    if h.get("water_mgal"):
        stats.append(f'<div class="stat"><b>{h["water_mgal"]:,}</b>'
                     f'<span>water (Mgal)</span></div>')

    metrics_rows = ""
    if h.get("scope2_mkt") is not None and h.get("scope2_loc") is not None:
        metrics_rows += (f'<tr><td>Scope 2 (market-based)</td>'
                         f'<td><strong>{_fmt_co2(h["scope2_mkt"])} tCO2e</strong></td></tr>')
    metrics_rows += (f'<tr><td>Renewable / CFE claim</td>'
                     f'<td><strong>{esc(h.get("renewable", "—"))}</strong></td></tr>')
    metrics_rows += (f'<tr><td>Water</td>'
                     f'<td><strong>{esc(h.get("water_note", "—"))}</strong></td></tr>')

    scale_html = (f'<tr><td>Scale</td>'
                  f'<td><strong>{esc(h.get("scale", ""))}</strong></td></tr>')
    if h.get("revenue"):
        scale_html += (f'<tr><td>Revenue</td>'
                       f'<td><strong>{esc(h["revenue"])}</strong></td></tr>')

    body = f"""
<header>
  <div class="kicker">Corporate scorecard</div>
  <h1>{esc(h['name'])} environmental profile</h1>
  <p class="sub">Key environmental metrics from the {esc(h['report'])}
  sustainability report.</p>
</header>
<div class="stats">{"".join(stats)}</div>
<section>
  <h2>Key metrics</h2>
  <table>
    {metrics_rows}
    {scale_html}
    {extras}
  </table>
  {notes_html}
</section>
<section>
  <h2>What this means for your community</h2>
  <p>These operators lease capacity to hyperscalers — when Google, Microsoft,
  or AWS announces a campus in your area, the building may carry a different
  name on the permit. The environmental footprint belongs to the facility,
  not the tenant's brand. Ask the operator, not just the tenant, for their
  PUE, water, and emissions data.</p>
  <p><a class="btn" href="{APP_URL}">Run the numbers for your community &rarr;</a>
  <a class="btn ghost" href="../companies/index.html">All scorecards</a></p>
</section>
"""
    desc_parts = []
    if h.get("pue"):
        desc_parts.append(f"PUE {h['pue']}")
    if h.get("twh"):
        desc_parts.append(f"{h['twh']} TWh")
    desc_detail = ", ".join(desc_parts)
    return page(
        f"{h['name']} environmental scorecard — AI GridWatch",
        f"Environmental data for {h['name']}: {desc_detail}, "
        f"carbon and water metrics from {h['report']}.",
        body, f"{SITE_URL}/companies/{h['slug']}", depth=1)


def build_limited_scorecard(ld):
    reported_html = ""
    if ld.get("reported"):
        rows = "\n".join(
            f'<tr><td>{esc(k)}</td><td><strong>{esc(v)}</strong></td></tr>'
            for k, v in ld["reported"])
        reported_html = (
            f'<section><h2>What they do report</h2>'
            f'<table>{rows}</table></section>')

    not_reported_html = ""
    if ld.get("not_reported"):
        items = "".join(f"<li>{esc(x)}</li>" for x in ld["not_reported"])
        not_reported_html = (
            f'<section><h2>What they don\'t report</h2>'
            f'<ul>{items}</ul></section>')

    gap_html = ""
    if ld.get("gap_text"):
        gap_html = (
            f'<section><h2>Disclosure gap</h2>'
            f'<div class="ask">{esc(ld["gap_text"])}</div></section>')

    badge_class = "rejected" if ld["disclosure"] == "none" else "proposed"
    body = f"""
<header>
  <div class="kicker">Corporate scorecard</div>
  <h1>{esc(ld['name'])}</h1>
  <p class="sub">{esc(ld.get('scale', ''))} ·
  <span class="badge badge-{badge_class}">disclosure: {esc(ld['disclosure'])}</span></p>
</header>
<section>
  <h2>Context</h2>
  <p>{esc(ld.get('context', ''))}</p>
</section>
{gap_html}
{reported_html}
{not_reported_html}
<section>
  <h2>Why this matters</h2>
  <p>Companies building gigawatts of data center capacity without publishing
  environmental data are asking communities to approve projects on trust.
  If a developer won't disclose PUE, water consumption, and emissions
  before construction, that's a question for your planning board.</p>
  <p><a class="btn" href="{APP_URL}">Run the numbers for your community &rarr;</a>
  <a class="btn ghost" href="../companies/index.html">All scorecards</a></p>
</section>
"""
    return page(
        f"{ld['name']} — AI GridWatch",
        f"{ld['name']}: {ld.get('scale', '')} — disclosure level: "
        f"{ld['disclosure']}.",
        body, f"{SITE_URL}/companies/{ld['slug']}", depth=1)


def build_rss():
    posts = _sorted_posts()[:20]
    items = ""
    for s in posts:
        title_clean = s["title"].replace("\\$", "$")
        summary_clean = s["summary"].replace("\\$", "$")
        items += f"""    <item>
      <title>{esc(title_clean)}</title>
      <link>{SITE_URL}/blog/{s['id']}</link>
      <guid>{SITE_URL}/blog/{s['id']}</guid>
      <pubDate>{s['date'].strftime('%a, %d %b %Y')} 00:00:00 GMT</pubDate>
      <description>{esc(summary_clean)}</description>
    </item>\n"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>AI GridWatch Blog</title>
  <link>{SITE_URL}/blog/</link>
  <description>Analysis and explainers on data center development, grid impact, and community advocacy.</description>
  <atom:link href="{SITE_URL}/blog/feed.xml" rel="self" type="application/rss+xml"/>
{items}</channel>
</rss>
"""


def build_about():
    body_html = _md_to_html(ABOUT_SECTION["body"])
    body = f"""
<header>
  <div class="kicker">About</div>
  <h1>{esc(ABOUT_SECTION['title'])}</h1>
  <p class="sub">{esc(ABOUT_SECTION['tagline'])}</p>
</header>
<section class="prose">
  {body_html}
</section>
<section>
  <h2>Use the tools</h2>
  <p>Everything on this site is free and requires no account.</p>
  <p>
    <a class="btn" href="{APP_URL}">Open the toolkit &rarr;</a>
    <a class="btn ghost" href="impact.html">Impact calculator</a>
  </p>
</section>
"""
    return page(
        "About — AI GridWatch",
        ABOUT_SECTION["tagline"],
        body, f"{SITE_URL}/about")


def build_search():
    import json
    index = []
    for m in MORATORIUMS_DF.itertuples():
        index.append({"t": str(m.locality), "k": "moratorium",
                       "d": f"{m.state} · {m.status}",
                       "u": f"moratoriums.html"})
    for _, r in OPERATORS_DF.iterrows():
        index.append({"t": r["operator"], "k": "operator",
                       "d": f"{r['tier']} · {r['model']}",
                       "u": f"search.html"})
    for _, r in EXECUTIVES_DF.iterrows():
        # Don't present an unconfirmed title as fact in search results.
        suffix = "" if r["verified"] else " · unverified"
        index.append({"t": r["name"], "k": "executive",
                       "d": f"{r['company']} · {r['title']}{suffix}",
                       "u": f"search.html"})
    for _, r in DC_SITES_DF.iterrows():
        loc = str(r.get("location", ""))
        st = str(r.get("state", ""))
        index.append({"t": f"{r['operator']} — {loc}",
                       "k": "site",
                       "d": f"{st} · {r.get('tenant', '—')}",
                       "u": f"states/{slugify(STATE_PUCS_DF[STATE_PUCS_DF['abbrev'] == st].iloc[0]['state'])}.html" if not STATE_PUCS_DF[STATE_PUCS_DF['abbrev'] == st].empty else "states/index.html"})
    for s in sorted(STATE_GRID_PROFILES):
        index.append({"t": s, "k": "state",
                       "d": f"State briefing",
                       "u": f"states/{slugify(s)}.html"})
    for s in _sorted_posts():
        title_clean = s["title"].replace("\\$", "$")
        index.append({"t": title_clean, "k": "blog",
                       "d": s["date"].strftime("%b %Y"),
                       "u": f"blog/{s['id']}.html"})
    for h in _HYPERSCALERS + _OPERATORS:
        index.append({"t": h["name"], "k": "company",
                       "d": f'{h["report"]} · PUE {h.get("pue", "—")}',
                       "u": f"companies/{h['slug']}.html"})
    for ld in _LIMITED_DISCLOSURE:
        index.append({"t": ld["name"], "k": "company",
                       "d": f'disclosure: {ld["disclosure"]}',
                       "u": f"companies/{ld['slug']}.html"})
    index_json = json.dumps(index)

    body = f"""
<header>
  <div class="kicker">Search</div>
  <h1>Find anything</h1>
  <p class="sub">Search across moratoriums, operators, executives, data
  center sites, states, and blog posts.</p>
</header>
<section>
  <input type="text" id="q" placeholder="Type to search..."
         autofocus autocomplete="off"
         style="width:100%;background:var(--card);color:var(--ink);
         border:1px solid var(--rule);border-radius:10px;padding:12px 16px;
         font-size:16px;margin-bottom:14px">
  <div id="results"></div>
  <p class="muted" id="count"></p>
</section>
<script>
(function() {{
  var IX = {index_json};
  var q = document.getElementById('q');
  var box = document.getElementById('results');
  var ct = document.getElementById('count');
  var kinds = {{moratorium:'#ef4444', operator:'#3b82f6', executive:'#a855f7',
                site:'#f59e0b', state:'#2dd4bf', blog:'#6366f1',
                company:'#f472b6'}};
  function render(items) {{
    if (!q.value.trim()) {{ box.innerHTML = ''; ct.textContent = IX.length + ' items indexed'; return; }}
    if (!items.length) {{ box.innerHTML = '<p style="color:var(--muted)">No results.</p>'; ct.textContent = ''; return; }}
    box.innerHTML = items.slice(0, 40).map(function(it) {{
      var c = kinds[it.k] || 'var(--muted)';
      return '<div style="padding:10px 0;border-bottom:1px solid var(--rule)">'
        + '<a href="' + it.u + '" style="text-decoration:none">'
        + '<span class="badge" style="background:' + c + '22;color:' + c + '">' + it.k + '</span> '
        + '<strong>' + it.t + '</strong></a>'
        + '<div class="muted" style="font-size:13px">' + it.d + '</div></div>';
    }}).join('');
    ct.textContent = items.length + ' result' + (items.length === 1 ? '' : 's');
  }}
  q.addEventListener('input', function() {{
    var v = q.value.toLowerCase().trim();
    if (!v) {{ render([]); return; }}
    var words = v.split(/\\s+/);
    var hits = IX.filter(function(it) {{
      var hay = (it.t + ' ' + it.d + ' ' + it.k).toLowerCase();
      return words.every(function(w) {{ return hay.indexOf(w) >= 0; }});
    }});
    render(hits);
  }});
  render([]);
}})();
</script>
"""
    return page(
        "Search — AI GridWatch",
        "Search data center moratoriums, operators, executives, sites, and "
        "state briefings.",
        body, f"{SITE_URL}/search")


def build_data_dividend():
    body = f"""
<header>
  <div class="kicker">Community calculator</div>
  <h1>Data dividend calculator</h1>
  <p class="sub">Estimate what your community should be getting back from a
  data center — annual tax revenue, CBA investment target, and per-household
  benefit. Bring these numbers to the negotiating table.</p>
</header>
<section>
  <h2>Facility details</h2>
  <div class="grid2">
    <div>
      <label class="muted" for="dd-mw">Facility size (MW)</label>
      <div style="display:flex;align-items:center;gap:14px">
        <input type="range" id="dd-mw" min="10" max="500" value="100"
               step="10" style="flex:1;accent-color:var(--teal)">
        <span id="dd-mw-label" style="font-size:22px;font-weight:700;
              color:var(--teal);min-width:70px">100 MW</span>
      </div>
    </div>
    <div>
      <label class="muted" for="dd-homes">Households in your community</label>
      <input type="number" id="dd-homes" value="15000" min="500" max="500000"
             step="500" style="background:var(--card);color:var(--ink);
             border:1px solid var(--rule);border-radius:8px;padding:8px 14px;
             font-size:15px;width:100%">
    </div>
  </div>
  <div class="grid2" style="margin-top:14px">
    <div>
      <label class="muted" for="dd-tax">Local property tax rate (%)</label>
      <input type="number" id="dd-tax" value="1.0" min="0.1" max="5" step="0.1"
             style="background:var(--card);color:var(--ink);
             border:1px solid var(--rule);border-radius:8px;padding:8px 14px;
             font-size:15px;width:100%">
    </div>
    <div>
      <label class="muted" for="dd-cba">CBA share of investment (%)</label>
      <input type="number" id="dd-cba" value="2.0" min="0.5" max="10" step="0.5"
             style="background:var(--card);color:var(--ink);
             border:1px solid var(--rule);border-radius:8px;padding:8px 14px;
             font-size:15px;width:100%">
    </div>
  </div>
</section>
<div class="stats">
  <div class="stat"><b id="dd-invest">—</b><span>estimated investment</span></div>
  <div class="stat"><b id="dd-annual">—</b><span>annual CBA target</span></div>
  <div class="stat"><b id="dd-perhome">—</b><span>per household / year</span></div>
  <div class="stat"><b id="dd-taxrev">—</b><span>est. annual property tax</span></div>
</div>
<section>
  <h2>What good CBA deals include</h2>
  <div class="grid2">
    <div class="card">
      <h3>Direct payments</h3>
      <p class="muted">Annual community benefit fund, infrastructure
      upgrades (roads, water, sewer), school funding, recreation
      facilities.</p>
    </div>
    <div class="card">
      <h3>Protections</h3>
      <p class="muted">Water draw caps, noise limits, visual screening,
      decommissioning bonds, local hiring requirements, rate-impact
      studies.</p>
    </div>
  </div>
</section>
<section>
  <h2>Generate the full package</h2>
  <p>The toolkit builds a complete meeting brief with these numbers, plus
  comment scripts, letters, and CBA clause templates.</p>
  <p><a class="btn" href="{APP_URL}">Generate your action pack &rarr;</a>
  <a class="btn ghost" href="impact.html">Impact calculator</a></p>
</section>
<script>
(function() {{
  var INV_PER_MW = 2000000;
  var mwSlider = document.getElementById('dd-mw');
  var mwLabel = document.getElementById('dd-mw-label');
  var homesInput = document.getElementById('dd-homes');
  var taxInput = document.getElementById('dd-tax');
  var cbaInput = document.getElementById('dd-cba');
  function usd(n) {{
    if (n >= 1e9) return '$' + (n/1e9).toFixed(1) + 'B';
    if (n >= 1e6) return '$' + (n/1e6).toFixed(1) + 'M';
    if (n >= 1e3) return '$' + Math.round(n).toLocaleString();
    return '$' + Math.round(n);
  }}
  function calc() {{
    var mw = +mwSlider.value;
    var homes = +homesInput.value || 15000;
    var taxRate = (+taxInput.value || 1.0) / 100;
    var cbaShare = (+cbaInput.value || 2.0) / 100;
    mwLabel.textContent = mw + ' MW';
    var investment = mw * INV_PER_MW;
    var annualCba = investment * cbaShare;
    var perHome = annualCba / homes;
    var taxRev = investment * taxRate;
    document.getElementById('dd-invest').textContent = usd(investment);
    document.getElementById('dd-annual').textContent = usd(annualCba);
    document.getElementById('dd-perhome').textContent = usd(perHome);
    document.getElementById('dd-taxrev').textContent = usd(taxRev);
  }}
  [mwSlider, homesInput, taxInput, cbaInput].forEach(function(el) {{
    el.addEventListener('input', calc);
  }});
  calc();
}})();
</script>
"""
    return page(
        "Data dividend calculator — AI GridWatch",
        "Estimate the CBA target, tax revenue, and per-household benefit "
        "your community should negotiate from a data center.",
        body, f"{SITE_URL}/dividend")


def build_sitemap(paths):
    urls = "\n".join(
        f"  <url><loc>{SITE_URL}/{p}</loc></url>" for p in paths)
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f'{urls}\n</urlset>\n')


def main():
    shutil.rmtree(WEB, ignore_errors=True)
    (WEB / "states").mkdir(parents=True)
    (WEB / "blog").mkdir(parents=True)
    (WEB / "companies").mkdir(parents=True)
    (WEB / "assets").mkdir()

    shutil.copy(ROOT / "assets" / "logo.svg", WEB / "assets" / "logo.svg")
    (WEB / "assets" / "gridwatch_health_risks.pdf").write_bytes(
        build_health_pdf(HEALTH_RISKS, SOURCES))

    (WEB / "index.html").write_text(build_index(), encoding="utf-8")
    (WEB / "health-risks.html").write_text(build_health(), encoding="utf-8")
    (WEB / "moratoriums.html").write_text(build_moratoriums(), encoding="utf-8")
    (WEB / "impact.html").write_text(build_impact_calculator(), encoding="utf-8")
    (WEB / "about.html").write_text(build_about(), encoding="utf-8")
    (WEB / "search.html").write_text(build_search(), encoding="utf-8")
    (WEB / "dividend.html").write_text(build_data_dividend(), encoding="utf-8")
    (WEB / "states" / "index.html").write_text(
        build_states_index(), encoding="utf-8")

    posts = _sorted_posts()
    (WEB / "blog" / "index.html").write_text(
        build_blog_index(), encoding="utf-8")
    (WEB / "blog" / "feed.xml").write_text(build_rss(), encoding="utf-8")

    for i, story in enumerate(posts):
        prev_post = posts[i - 1] if i > 0 else None
        next_post = posts[i + 1] if i < len(posts) - 1 else None
        (WEB / "blog" / f"{story['id']}.html").write_text(
            build_blog_post(story, prev_post, next_post), encoding="utf-8")

    (WEB / "companies" / "index.html").write_text(
        build_scorecards_index(), encoding="utf-8")
    for h in _HYPERSCALERS:
        (WEB / "companies" / f"{h['slug']}.html").write_text(
            build_scorecard(h), encoding="utf-8")
    for h in _OPERATORS:
        (WEB / "companies" / f"{h['slug']}.html").write_text(
            build_operator_scorecard(h), encoding="utf-8")
    for ld in _LIMITED_DISCLOSURE:
        (WEB / "companies" / f"{ld['slug']}.html").write_text(
            build_limited_scorecard(ld), encoding="utf-8")

    paths = ["", "health-risks", "moratoriums", "impact", "about",
             "search", "dividend", "companies/", "states/", "blog/"]
    paths.extend(f"companies/{h['slug']}" for h in _HYPERSCALERS)
    paths.extend(f"companies/{h['slug']}" for h in _OPERATORS)
    paths.extend(f"companies/{ld['slug']}" for ld in _LIMITED_DISCLOSURE)
    paths.extend(f"blog/{s['id']}" for s in posts)
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
