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
import json
import os
import pathlib
import shutil

import markdown
import pandas as pd

from src.blog_art import art_svg
from src.blog_content import BLOG_STORIES, ABOUT_SECTION
from src.alerts import build_alerts, LOOKAHEAD_DAYS as ALERT_LOOKAHEAD
from src.constants import (
    AI_COMPETITORS_DF,
    STATE_GRID_PROFILES, STATE_DC_DF, STATE_DC_NATIONAL,
    STATE_PUCS_DF, MORATORIUMS_DF,
    MORATORIUM_OUTCOMES, HEALTH_RISKS, CBA_BENCHMARKS, COMPANY_CONCESSIONS,
    DC_SITES_DF, LOCAL_OFFICIALS_DF, LOCAL_BODIES_DF, STATE_MUNI_LEAGUES,
    OPERATORS_DF, EXECUTIVES_DF, MEGA_PROJECTS_DF,
    ERCOT_LL_VINTAGE, ERCOT_LL_DC_SHARE, ERCOT_LL_FUNNEL,
    GOOGLE_2025_HEADLINE, META_2024_HEADLINE,
    MICROSOFT_ENV_HEADLINE, AWS_ENV_HEADLINE,
    GOOGLE_DC_ELECTRICITY, GOOGLE_GHG, GOOGLE_WATER,
    GOOGLE_PUE_FLEET, GOOGLE_PUE_SITES_DF, GOOGLE_CFE_BY_GRID_DF,
    META_DC_ELECTRICITY, META_DC_CAMPUS_ELECTRICITY, META_GHG,
    META_WATER, META_EFFICIENCY,
    EQUINIX_2024_HEADLINE, DIGITAL_REALTY_2024_HEADLINE,
    EDGECONNEX_2024_HEADLINE, STACK_2023_HEADLINE,
    CYRUSONE_2023_HEADLINE, VANTAGE_2023_HEADLINE,
    COREWEAVE_PROFILE, QTS_PROFILE, SWITCH_PROFILE, COMPASS_PROFILE,
    SOURCES, registry_provenance, has_value,
    QUERY_COEFFS, TOKEN_COEFFS, GRID_INTENSITY, ONSITE_WUE, OFFSITE_WATER,
    IEA_OUTLOOK, DC_FORECASTS, DC_FORECASTS_US,
    PEW_RURAL_2026, PEW_STATE_COUNTS,
    NEWS_THEMES, STORY_ANGLES, STORY_IMPACT_WEIGHTS,
)
from src.pdf_pack import build_health_pdf
from src.us_map_data import US_MAP_PATHS, US_MAP_LABELS, US_MAP_VIEWBOX

# The live domain. Canonical tags and the sitemap are built from this, so it
# must be the domain users actually reach — pointing them at the *.vercel.app
# deployment URL tells search engines that subdomain is the real site.
SITE_URL = os.environ.get("SITE_URL", "https://aigridwatch.com")
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
nav a[aria-current] { color:var(--teal); font-weight:600; }
nav .cta { margin-left:auto; background:var(--teal); color:#06251f;
           font-weight:700; padding:8px 16px; border-radius:8px; }
/* Desktop: the link-group wrapper dissolves so flex layout is unchanged. */
.nav-burger { display:none; }
.nav-links { display:contents; }
@media (max-width:820px) {
  nav { gap:8px; }
  nav img { height:30px; }
  .nav-burger { display:block; order:3; font-size:20px; line-height:1;
    color:var(--muted); cursor:pointer; padding:5px 8px; border-radius:8px;
    border:1px solid var(--rule); user-select:none; }
  .nav-burger:hover { color:var(--teal); border-color:var(--teal); }
  nav .cta { order:2; margin-left:auto; padding:6px 11px; font-size:13px; }
  .nav-links { order:4; display:none; flex-basis:100%;
    flex-direction:column; gap:0; padding:4px 0 2px; }
  #navToggle:checked ~ .nav-links { display:flex; }
  .nav-links a { padding:10px 2px; font-size:15px;
    border-bottom:1px solid rgba(255,255,255,.05); }
  .nav-links a:last-child { border-bottom:none; }
}
.skip { position:absolute; left:-9999px; }
.skip:focus { position:fixed; left:16px; top:10px; z-index:1000;
  background:var(--teal); color:#06251f; font-weight:700;
  padding:9px 16px; border-radius:8px; }
header { padding:44px 0 10px; }
.kicker { color:var(--teal); font-weight:700; letter-spacing:.12em;
          text-transform:uppercase; font-size:13px; }
h1 { font-size:clamp(28px,5vw,44px); line-height:1.12; margin:10px 0;
     text-wrap:balance; }
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
.note { border-left:3px solid var(--rule); padding:12px 16px; margin:18px 0;
  border-radius:0 8px 8px 0; font-size:14.5px; line-height:1.55; }
.note.info { border-left-color:var(--teal); background:rgba(45,212,191,.07); }
.note.warn { border-left-color:var(--amber); background:rgba(251,191,36,.07); }
.note.bad  { border-left-color:#ef4444; background:rgba(239,68,68,.08); }
.note.good { border-left-color:#34d399; background:rgba(52,211,153,.07); }
.note p { margin:0; }
details.more { border:1px solid var(--rule); border-radius:10px;
  padding:0 16px; margin:16px 0; background:rgba(255,255,255,.02); }
details.more > summary { cursor:pointer; padding:13px 0; font-weight:600;
  color:var(--teal); font-size:14.5px; }
details.more[open] { padding-bottom:10px; }
.billbar { display:flex; height:60px; border-radius:8px; overflow:hidden;
  margin:20px 0 12px; }
.billbar > div { display:flex; align-items:center; justify-content:center;
  color:#fff; font-weight:700; font-size:14px; }
.barkey { display:flex; flex-wrap:wrap; gap:14px; font-size:13px;
  color:var(--muted); }
.barkey span { display:flex; align-items:center; gap:6px; }
.barkey i { width:12px; height:12px; border-radius:3px; }
.flow { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  gap:12px; margin:18px 0; }
.flow .step { border:1px solid var(--rule); border-radius:10px; padding:12px 14px;
  background:rgba(255,255,255,.02); font-size:14px; }
.flow .step b { display:block; margin-bottom:4px; }
.flow .step.end { border-color:#ef4444; background:rgba(239,68,68,.08); }
.hbars { margin:18px 0; display:flex; flex-direction:column; gap:8px; }
.hbar-row { display:grid; grid-template-columns:minmax(90px,1.1fr) 2.4fr
  minmax(90px,1.3fr); gap:10px; align-items:center; font-size:13.5px; }
.hbar-label { color:var(--ink); }
.hbar-track { background:rgba(255,255,255,.06); border-radius:5px; height:16px; }
.hbar-fill { height:16px; border-radius:5px; }
.hbar-val { color:var(--muted); font-variant-numeric:tabular-nums; }
@media (max-width:640px) {
  .hbar-row { grid-template-columns:1fr; gap:2px; }
  .hbar-track { height:12px; }
}
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
.blog-list li { border-bottom:1px solid var(--rule); padding:18px 0;
  content-visibility:auto; contain-intrinsic-size:auto 110px; }
.blog-list li:last-child { border-bottom:none; }
/* Only posts carry art — news/video lists reuse .blog-list without a thumb,
   so the two-column grid is scoped to .has-art rather than the whole list. */
.blog-list li.has-art { display:grid; grid-template-columns:1fr; gap:14px; }
@media (min-width:680px){ .blog-list li.has-art {
  grid-template-columns:200px 1fr; gap:18px; align-items:start;
  contain-intrinsic-size:auto 150px; } }
.blog-list .thumb { width:100%; height:auto; display:block; border-radius:10px;
  border:1px solid var(--rule); }
.post-art { width:100%; height:auto; display:block; border-radius:14px;
  border:1px solid var(--rule); margin:4px 0 24px;
  filter:drop-shadow(0 8px 24px rgba(45,212,191,.10)); }
.post-art .glow, .thumb .glow { animation:pulse 3.2s ease-in-out infinite; }
@media (prefers-reduced-motion:reduce){
  .post-art .glow, .thumb .glow { animation:none; opacity:.7 } }
.blog-list h3 { font-size:17px; margin:0 0 4px; }
.blog-list h3 a { text-decoration:none; }
.blog-list .summary { color:var(--muted); font-size:14px; margin:4px 0 0; }
.badge { display:inline-block; font-size:12px; font-weight:700;
         padding:2px 9px; border-radius:6px; }
.badge-enacted { background:#065f46; color:#6ee7b7; }
.badge-proposed { background:#713f12; color:#fde68a; }
.badge-rejected { background:#7f1d1d; color:#fca5a5; }
.badge-vetoed { background:#4c1d95; color:#c4b5fd; }
.badge-expired { background:#374151; color:#d1d5db; }
.badge-rescinded { background:#4c1d95; color:#c4b5fd; }
.badge-note { font-size:11px; font-weight:600; color:var(--muted);
              display:block; margin-top:3px; }
.unverified { font-size:12px; color:#fca5a5; font-weight:600; }
.verified-on { font-size:12px; color:var(--muted); white-space:nowrap; }
.outcome { border-left:3px solid var(--teal); padding:10px 14px;
           margin:10px 0; }
.outcome .cat { font-size:12px; font-weight:700; color:var(--teal);
                text-transform:uppercase; letter-spacing:.08em; }
.grid2 { display:grid; grid-template-columns:1fr; gap:14px; }
@media (min-width:640px){ .grid2{ grid-template-columns:repeat(2,1fr);} }
.official { font-size:14px; }
.official .role { color:var(--muted); font-size:13px; }
.hero-grid { display:grid; grid-template-columns:1fr; gap:24px;
  align-items:center; padding:44px 0 10px; }
@media (min-width:820px){ .hero-grid{ grid-template-columns:1.15fr .85fr; padding:56px 0 20px; } }
.hero-grid header { padding:0; }
.hero-art { width:100%; max-width:420px; margin:0 auto; display:block;
  filter:drop-shadow(0 8px 24px rgba(45,212,191,.12)); }
.hero-art .glow { animation:pulse 3.2s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:.35} 50%{opacity:1} }
@media (prefers-reduced-motion:reduce){ .hero-art .glow{ animation:none; opacity:.7 } }
.iconcard { display:flex; gap:14px; align-items:flex-start; }
.iconcard .ico { flex-shrink:0; width:40px; height:40px; border-radius:10px;
  background:rgba(45,212,191,.12); display:flex; align-items:center;
  justify-content:center; color:var(--teal); }
.iconcard .ico svg { width:22px; height:22px; }
.iconcard .body h3 { margin:0 0 4px; }
.demand-chart { margin:14px 0 6px; }
.demand-chart .row { display:grid; grid-template-columns:minmax(80px,90px) 1fr minmax(90px,110px);
  gap:12px; align-items:center; padding:6px 0; font-size:14px; }
.demand-chart .yr { color:var(--muted); font-variant-numeric:tabular-nums; }
.demand-chart .bar { height:22px; border-radius:6px;
  background:linear-gradient(90deg, rgba(45,212,191,.85), rgba(45,212,191,.55));
  position:relative; }
.demand-chart .bar.range { background:linear-gradient(90deg,
  rgba(251,191,36,.85) 0%, rgba(251,191,36,.85) var(--lo,50%),
  rgba(251,191,36,.35) var(--lo,50%), rgba(251,191,36,.35) 100%); }
.demand-chart .val { color:var(--ink); font-variant-numeric:tabular-nums;
  font-weight:600; text-align:right; }
.grid-flow-svg { width:100%; height:auto; max-width:820px; margin:14px auto;
  display:block; }
.grid-flow-svg text { font:600 12px system-ui,-apple-system,sans-serif;
  fill:var(--ink); }
.grid-flow-svg text.small { font-size:10.5px; font-weight:500; fill:var(--muted); }
.grid-flow-svg .flow-dot { fill:var(--teal); }
.grid-flow-svg .flow-dot.a1 { animation:flowa 3s linear infinite; }
.grid-flow-svg .flow-dot.a2 { animation:flowb 3s linear infinite; animation-delay:1s; }
.grid-flow-svg .flow-dot.a3 { animation:flowc 3s linear infinite; animation-delay:2s; }
@keyframes flowa { 0%{opacity:0; transform:translateX(0)} 20%{opacity:1}
  80%{opacity:1} 100%{opacity:0; transform:translateX(180px)} }
@keyframes flowb { 0%{opacity:0; transform:translateX(0)} 20%{opacity:1}
  80%{opacity:1} 100%{opacity:0; transform:translateX(180px)} }
@keyframes flowc { 0%{opacity:0; transform:translateX(0)} 20%{opacity:1}
  80%{opacity:1} 100%{opacity:0; transform:translateX(180px)} }
@media (prefers-reduced-motion:reduce){ .grid-flow-svg .flow-dot{ animation:none } }
"""


NAV_LINKS = [
    ("Home", "index.html"),
    ("Your state", "states/index.html"),
    ("Siting score", "siting.html"),
    ("Case studies", "case-studies.html"),
    ("Clauses", "cba-clauses.html"),
    ("Tax breaks", "tax-breaks.html"),
    ("Hearing prep", "hearing-questions.html"),
    ("Health risks", "health-risks.html"),
    ("Moratoriums", "moratoriums.html"),
    ("Calculator", "impact.html"),
    ("Your bill", "bills.html"),
    ("Outlook", "outlook.html"),
    ("Learn", "learn.html"),
    ("PUCs", "puc.html"),
    ("Data centers", "data-centers.html"),
    ("Environment", "environment.html"),
    ("Companies", "companies/index.html"),
    ("Blog", "blog/index.html"),
    ("News", "news/index.html"),
]


def _nav_links_html(p, canonical):
    """Nav links with aria-current on the section the page belongs to.
    Section = first path element of the canonical URL, so /blog/any-post
    lights up Blog and /states/ohio lights up Your state."""
    rel = canonical[len(SITE_URL):].strip("/") if canonical.startswith(SITE_URL) else ""
    page_section = (rel.split("/")[0].replace(".html", "") or "index")
    out = []
    for label, target in NAV_LINKS:
        section = target.split("/")[0].replace(".html", "")
        cur = ' aria-current="page"' if section == page_section else ""
        out.append(f'<a href="{p}{target}"{cur}>{label}</a>')
    return "\n    ".join(out)


def page(title, description, body, canonical, depth=0,
         og_type="website", og_extra="", jsonld=None):
    p = "../" * depth
    ld_block = ""
    if jsonld:
        items = jsonld if isinstance(jsonld, list) else [jsonld]
        ld_block = "\n".join(
            f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>'
            for s in items)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0b1220">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" type="application/rss+xml" title="AI GridWatch Blog"
      href="{SITE_URL}/blog/feed.xml">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="AI GridWatch">
<meta property="og:image" content="{SITE_URL}/assets/hero.png">
<meta property="og:image:width" content="1024">
<meta property="og:image:height" content="479">
<meta name="twitter:card" content="summary_large_image">
{og_extra}
{ld_block}
<link rel="icon" href="{p}assets/logo.svg" type="image/svg+xml">
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="wrap">
<nav>
  <a href="{p}index.html"><img src="{p}assets/logo.svg" alt="AI GridWatch"></a>
  <input type="checkbox" id="navToggle" hidden>
  <label for="navToggle" class="nav-burger" aria-label="Menu"
         role="button">&#9776;</label>
  <div class="nav-links">
    {_nav_links_html(p, canonical)}
  </div>
  <a class="cta" href="{APP_URL}">Open the toolkit &rarr;</a>
</nav>
<main id="main">
{body}
</main>
<footer>
  <p style="margin-bottom:8px"><strong>Reference</strong> ·
    <a href="{p}methodology.html">Methodology</a> ·
    <a href="{p}studies.html">State studies</a> ·
    <a href="{p}officials.html">Officials directory</a> ·
    <a href="{p}glossary.html">Glossary</a> ·
    <a href="{p}tax-breaks.html">Tax breaks</a> ·
    <a href="{p}dividend.html">Data dividend</a></p>
  <p style="margin-bottom:8px"><strong>Site</strong> ·
    <a href="{p}about.html">About</a> ·
    <a href="{p}consulting.html">Consulting</a> ·
    <a href="{p}search.html">Search</a></p>
  <p>AI GridWatch — community energy intelligence. Planning estimates, not
  engineering studies; every number is sourced in the
  <a href="{APP_URL}">full toolkit</a>. Built from public data.</p>
</footer>
</div>
</body>
</html>
"""


_ORG = {
    "@type": "Organization",
    "name": "AI GridWatch",
    "url": SITE_URL,
    "description": "Free community tools for negotiating with data center "
                   "developers: impact calculators, CBA templates, health "
                   "evidence, and sourced data.",
    "logo": f"{SITE_URL}/assets/logo.svg",
}


def _breadcrumb(*items):
    """BreadcrumbList schema. items = [(name, url), ...]."""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1,
             "name": name, "item": url}
            for i, (name, url) in enumerate(items)
        ],
    }


def _faq_schema(pairs):
    """FAQPage schema. pairs = [(question, answer), ...]."""
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in pairs
        ],
    }


def _article_schema(title, description, url, date_str, author="AI GridWatch"):
    """Article schema for blog posts."""
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "url": url,
        "datePublished": date_str,
        "author": {"@type": "Organization", "name": author},
        "publisher": {**_ORG, "@context": "https://schema.org"},
    }


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
        f"({esc(b['company'])}) — {esc(b['won'])}{_prov_links(b)}</li>"
        for b in CBA_BENCHMARKS)
    body = f"""
<div class="hero-grid">
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
{_hero_art_svg()}
</div>
<div class="stats">
  <div class="stat"><b>{n_dc:,}</b><span>tracked U.S. data center facilities</span></div>
  <div class="stat"><b>{twh:,.0f} TWh</b><span>estimated annual electricity, all 50 states + D.C.</span></div>
  <div class="stat"><b>{n_mora}</b><span>tracked moratorium &amp; pushback efforts</span></div>
  <div class="stat"><b>325&ndash;580 TWh</b><span>projected U.S. data center demand by 2030 (Berkeley Lab)</span></div>
</div>
<section>
  <h2>The trajectory</h2>
  <p class="muted" style="margin-bottom:6px">U.S. data-center electricity demand, actual and projected — TWh per year.</p>
  <div class="demand-chart">
    <div class="row"><span class="yr">2018</span>
      <div class="bar" style="width:14%"></div><span class="val">76 TWh</span></div>
    <div class="row"><span class="yr">2023</span>
      <div class="bar" style="width:32%"></div><span class="val">176 TWh</span></div>
    <div class="row"><span class="yr">2028</span>
      <div class="bar range" style="width:59%; --lo:56%"></div><span class="val">325&ndash;580</span></div>
    <div class="row"><span class="yr">2030</span>
      <div class="bar range" style="width:100%; --lo:56%"></div><span class="val">up to 580</span></div>
  </div>
  <p class="src">Source: Lawrence Berkeley National Laboratory,
  <em>2024 U.S. Data Center Energy Usage Report</em> (Dec 2024). 2028&ndash;2030 range reflects low/high AI-adoption scenarios.</p>
</section>
<section>
  <h2>What you get</h2>
  <div class="grid3">
    <div class="card"><div class="iconcard">
      <div class="ico">{_ico_doc()}</div><div class="body">
      <h3>Action pack</h3><p class="muted">A personalized
      PDF: impact numbers, meeting strategy, CBA targets, a 2-minute speech,
      and ready-to-send letters.</p></div></div></div>
    <div class="card"><div class="iconcard">
      <div class="ico">{_ico_flyer()}</div><div class="body">
      <h3>Flyer + petition</h3><p class="muted">A one-page
      hand-out with your community's numbers, in English and Spanish, with a
      sign-up sheet.</p></div></div></div>
    <div class="card"><div class="iconcard">
      <div class="ico">{_ico_globe()}</div><div class="body">
      <h3>Campaign site</h3><p class="muted">A complete
      one-page website with your numbers baked in — free to host, no coding
      needed.</p></div></div></div>
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
    home_ld = [
        {"@context": "https://schema.org", **_ORG},
        {"@context": "https://schema.org",
         "@type": "WebSite", "name": "AI GridWatch", "url": SITE_URL,
         "potentialAction": {
             "@type": "SearchAction",
             "target": f"{SITE_URL}/search?q={{search_term_string}}",
             "query-input": "required name=search_term_string"}},
    ]
    return page(
        "AI GridWatch — data center impact tools for communities",
        "Free calculators, negotiation playbooks, and sourced health "
        "evidence for communities facing data center development.",
        body, f"{SITE_URL}/", jsonld=home_ld)


def _status_badge(status):
    cls = f"badge-{status.lower().replace(' ', '-')}"
    return f'<span class="badge {cls}">{esc(status)}</span>'


def _mora_status_cell(m):
    """Status badge for a moratorium row, plus the expiry line under it.

    Reads `effective_status`, never the stored `status` — a lapsed moratorium
    must not render as "Enacted". The date is spelled out either way so a
    reader can see whether the badge is a claim about now or about a term that
    ran out.
    """
    html = _status_badge(str(m.effective_status))
    if m.expired:
        html += f'<span class="badge-note">term ran to {esc(str(m.expires))}</span>'
    elif has_value(m.expires):
        word = "expires" if not m.expiring_soon else "expires soon —"
        html += f'<span class="badge-note">{word} {esc(str(m.expires))}</span>'
    return html


def _prov_links(item, label="Source"):
    """Inline `sources` + `as_of` for any registry row that carries them.

    Shared by CBA benchmarks and operator concessions: both get quoted at a
    negotiating table, so the citation has to travel with the claim rather
    than living in a methodology page nobody opens. An unsourced row says so
    out loud instead of rendering a confident blank.
    """
    srcs = item.get("sources") or []
    if not srcs:
        return ' <span class="unverified">(unverified — do not cite)</span>'
    links = " · ".join(
        f'<a href="{esc(u)}" rel="nofollow noopener" target="_blank">'
        f'{label} {i}</a>' for i, u in enumerate(srcs, 1))
    on = f" · verified {esc(str(item['as_of']))}" if item.get("as_of") else ""
    return f' <span class="verified-on">{links}{on}</span>'


def _outcome_card(o):
    """One case-study card, with its sources on the card itself.

    These get read out at hearings, so the citation has to travel with the
    claim — a reader who cannot see where it came from has no way to defend it
    when a developer's counsel pushes back.
    """
    srcs = o.get("sources") or []
    if srcs:
        links = " · ".join(
            f'<a href="{esc(u)}" rel="nofollow noopener" target="_blank">'
            f'Source {i}</a>' for i, u in enumerate(srcs, 1))
        prov = (f'<p class="verified-on">{links} · verified '
                f'{esc(str(o.get("as_of") or "—"))}</p>')
    else:
        prov = '<p class="unverified">Unverified — do not cite</p>'
    return (f'<div class="outcome"><div class="cat">{esc(o["category"])}</div>'
            f'<p><strong>{esc(o["locality"])}, {esc(o["state"])}</strong> — '
            f'{esc(o["headline"])}</p>'
            f'<p class="muted">{esc(o["outcome"])}</p>{prov}</div>')


def _mora_source_cell(m):
    """Per-row provenance: the source link and the date it was read.

    An unverified row says so in as many words. The alternative — a blank
    cell — reads as "nothing to add" when it actually means "nobody has
    checked this."
    """
    if not has_value(m.source):
        return '<span class="unverified">Unverified</span>'
    on = (f'<span class="verified-on">read {esc(str(m.as_of))}</span>'
          if has_value(m.as_of) else "")
    return (f'<a href="{esc(str(m.source))}" rel="nofollow noopener" '
            f'target="_blank">Source</a><br>{on}')


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
            f"<td>{_mora_status_cell(m)}</td>"
            f"<td>{cell(m.note, dash='')}</td>"
            f"<td>{_mora_source_cell(m)}</td></tr>"
            for m in moras.itertuples())
        mora_html = (
            f'<section><h2>Pushback already happening in {esc(state)}</h2>'
            f'<table><tr><th>Where</th><th>Level</th><th>Status</th>'
            f'<th>Note</th><th>Source</th></tr>{rows}</table>'
            f'{provenance_html("MORATORIUMS_DF")}</section>')

    # DC sites in this state
    sites = DC_SITES_DF[DC_SITES_DF["state"] == abbrev]
    sites_html = ""
    if not sites.empty:
        site_rows = "\n".join(
            f"<tr><td>{esc(str(s.operator))}</td>"
            f"<td>{esc(str(s.location))}</td>"
            f"<td>{cell(s.tenant)}</td>"
            f"<td>{cell(s.filing_llc)}</td></tr>"
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
            f"— {esc(b['won'])}{_prov_links(b)}</li>"
            for b in state_cbas)
        cba_html = (
            f'<section><h2>What communities in {esc(state)} have won</h2>'
            f'<ul>{items}</ul></section>')

    # Moratorium outcomes / case studies for this state
    state_outcomes = [o for o in MORATORIUM_OUTCOMES if o["state"] == abbrev]
    outcome_html = ""
    if state_outcomes:
        cards = "\n".join(_outcome_card(o) for o in state_outcomes)
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

    # Latest blog posts that mention this state
    state_posts = _posts_for_state(state, limit=6)
    stories_html = ""
    if state_posts:
        items = "\n".join(
            f'<li><div class="post-meta">{p["date"].strftime("%b %-d, %Y")}</div>'
            f'<h3><a href="../blog/{p["id"]}.html">'
            f'{esc(p["title"].replace(chr(92) + "$", "$"))}</a></h3>'
            f'<p class="summary">{esc(p["summary"].replace(chr(92) + "$", "$"))}</p></li>'
            for p in state_posts)
        stories_html = (
            f'<section><h2>Latest stories about {esc(state)}</h2>'
            f'<ul class="blog-list">{items}</ul>'
            f'<p><a class="btn ghost" href="../blog/?state={esc(state)}">'
            f'All {esc(state)} posts &rarr;</a></p></section>')

    # Live news headlines mentioning this state
    state_news = _news_for_state(state, limit=6)
    news_html = ""
    if state_news:
        def _fmt(iso):
            if not iso:
                return ""
            try:
                import datetime as _dt
                return _dt.datetime.fromisoformat(iso).strftime("%b %-d, %Y")
            except Exception:                                     # noqa: BLE001
                return ""
        items = "\n".join(
            f'<li>'
            f'<div class="post-meta">{esc(" · ".join(x for x in (n.get("source",""), _fmt(n.get("published_iso",""))) if x))}</div>'
            f'<h3><a href="{esc(n["link"])}" rel="nofollow noopener" target="_blank">'
            f'{esc(n["title"])}</a></h3></li>'
            for n in state_news)
        news_html = (
            f'<section><h2>This week&#39;s headlines mentioning {esc(state)}</h2>'
            f'<ul class="blog-list">{items}</ul>'
            f'<p><a class="btn ghost" href="../news/?state={esc(state)}">'
            f'All {esc(state)} news &rarr;</a></p></section>')

    # Videos mentioning this state
    state_videos = _videos_for_state(state, limit=4)
    videos_html = ""
    if state_videos:
        cards = []
        placeholder = (
            '<div style="width:100%;aspect-ratio:16/9;background:'
            'linear-gradient(135deg,#1a1f2e,#2d1a3d);display:flex;'
            'align-items:center;justify-content:center;font-size:42px;'
            'color:#ff4136">▶</div>')
        for v in state_videos:
            vid = v.get("video_id", "")
            thumb = f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg' if vid else ""
            cards.append(
                f'<a href="{esc(v["link"])}" rel="nofollow noopener" target="_blank" '
                f'style="display:block;border:1px solid rgba(255,255,255,0.08);'
                f'border-radius:12px;overflow:hidden;text-decoration:none;color:inherit">'
                f'{("<img src=" + repr(thumb) + " alt=\"\" loading=\"lazy\" style=\"width:100%;display:block;aspect-ratio:16/9;object-fit:cover\">") if thumb else placeholder}'
                f'<div style="padding:10px 12px">'
                f'<div class="post-meta" style="font-size:12px;opacity:0.75">{esc(v.get("source",""))}</div>'
                f'<div style="font-weight:600;margin-top:4px;line-height:1.3">'
                f'{esc(v["title"])}</div></div></a>')
        videos_html = (
            f'<section><h2>Video coverage mentioning {esc(state)}</h2>'
            f'<div style="display:grid;grid-template-columns:repeat(auto-fill,'
            f'minmax(260px,1fr));gap:16px">{"".join(cards)}</div></section>')

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
{news_html}
{videos_html}
{stories_html}
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
        body, f"{SITE_URL}/states/{slugify(state)}", depth=1,
        jsonld=_breadcrumb(("Home", SITE_URL), ("States", f"{SITE_URL}/states/"), (state, f"{SITE_URL}/states/{slugify(state)}")))


_ABBREV_TO_FULL = {v: k for k, v in _ABBREV.items()}


def _hero_art_svg():
    return '''<svg class="hero-art" viewBox="0 0 420 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Illustration: a data center campus connected to a transmission tower by high-voltage lines">
  <defs>
    <linearGradient id="hg-sky" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0" stop-color="#1a2a48"/><stop offset="1" stop-color="#0b1220"/>
    </linearGradient>
    <linearGradient id="hg-teal" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stop-color="#2dd4bf" stop-opacity=".9"/>
      <stop offset="1" stop-color="#2dd4bf" stop-opacity=".2"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="420" height="300" rx="18" fill="url(#hg-sky)"/>
  <circle cx="330" cy="60" r="28" fill="#2dd4bf" opacity=".08"/>
  <circle cx="330" cy="60" r="16" fill="#2dd4bf" opacity=".14"/>
  <g stroke="#22304a" stroke-width="1" fill="none">
    <line x1="0" y1="240" x2="420" y2="240"/>
    <line x1="0" y1="260" x2="420" y2="260" opacity=".6"/>
  </g>
  <g stroke="#2dd4bf" stroke-width="1.5" fill="none" opacity=".55">
    <path d="M 78,120 Q 200,150 322,110"/>
    <path d="M 78,140 Q 200,170 322,130"/>
  </g>
  <g transform="translate(40,90)">
    <path d="M 38,0 L 4,150 M 38,0 L 72,150 M 12,110 L 64,110 M 20,70 L 56,70 M 26,40 L 50,40"
          stroke="#93a1b5" stroke-width="1.6" fill="none"/>
    <rect x="30" y="-8" width="16" height="10" fill="#93a1b5"/>
  </g>
  <g transform="translate(250,150)">
    <rect x="0" y="0" width="140" height="90" rx="6" fill="#121c30" stroke="#22304a" stroke-width="1.5"/>
    <rect x="0" y="0" width="140" height="14" fill="#22304a"/>
    <circle cx="8" cy="7" r="2" fill="#2dd4bf"/>
    <circle cx="16" cy="7" r="2" fill="#fbbf24" opacity=".8"/>
    <g fill="#2dd4bf">
      <rect x="10" y="22" width="120" height="6" opacity=".65"/>
      <rect x="10" y="34" width="90" height="6" opacity=".45"/>
      <rect x="10" y="46" width="120" height="6" opacity=".65"/>
      <rect x="10" y="58" width="70" height="6" opacity=".35"/>
      <rect x="10" y="70" width="120" height="6" opacity=".55"/>
    </g>
    <rect x="150" y="20" width="30" height="70" rx="3" fill="#121c30" stroke="#22304a"/>
    <rect x="154" y="26" width="22" height="6" fill="#93a1b5" opacity=".6"/>
    <rect x="154" y="36" width="22" height="6" fill="#93a1b5" opacity=".6"/>
    <rect x="154" y="46" width="22" height="6" fill="#93a1b5" opacity=".6"/>
  </g>
  <g class="glow">
    <circle cx="140" cy="118" r="3" fill="#2dd4bf"/>
    <circle cx="200" cy="128" r="3" fill="#2dd4bf"/>
    <circle cx="260" cy="122" r="3" fill="#2dd4bf"/>
  </g>
  <g fill="#93a1b5" font-family="system-ui,-apple-system,sans-serif" font-size="10" font-weight="600">
    <text x="40" y="260">345 kV transmission</text>
    <text x="250" y="260">Hyperscale campus</text>
  </g>
</svg>'''


def _ico_doc():
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/>'
            '<path d="M14 3v5h5"/><path d="M9 14l2 2 4-4"/></svg>')


def _ico_flyer():
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M4 4h16v13H4z"/><path d="M4 21h16"/>'
            '<path d="M8 8h8"/><path d="M8 12h5"/></svg>')


def _ico_globe():
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="12" cy="12" r="9"/>'
            '<path d="M3 12h18"/><path d="M12 3a14 14 0 0 1 0 18a14 14 0 0 1 0-18"/></svg>')


def _grid_flow_svg():
    return '''<svg class="grid-flow-svg" viewBox="0 0 820 210" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagram: how a data center connects to the grid, from power plant through transmission and substation">
  <defs>
    <marker id="gf-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#2dd4bf"/>
    </marker>
  </defs>
  <line x1="110" y1="105" x2="230" y2="105" stroke="#2dd4bf" stroke-width="2" marker-end="url(#gf-arrow)"/>
  <line x1="330" y1="105" x2="450" y2="105" stroke="#2dd4bf" stroke-width="2" marker-end="url(#gf-arrow)"/>
  <line x1="550" y1="105" x2="670" y2="105" stroke="#2dd4bf" stroke-width="2" marker-end="url(#gf-arrow)"/>
  <g transform="translate(20,55)">
    <rect x="0" y="20" width="90" height="60" rx="6" fill="#121c30" stroke="#22304a" stroke-width="1.5"/>
    <path d="M 15,20 Q 25,0 45,10 Q 65,-5 75,20" fill="none" stroke="#93a1b5" stroke-width="1.5"/>
    <rect x="10" y="45" width="20" height="30" fill="#22304a"/>
    <rect x="35" y="35" width="20" height="40" fill="#22304a"/>
    <rect x="60" y="50" width="20" height="25" fill="#22304a"/>
    <text x="45" y="105" text-anchor="middle">Generation</text>
    <text x="45" y="120" text-anchor="middle" class="small">Gas, wind, solar, nuclear</text>
  </g>
  <g transform="translate(240,45)">
    <path d="M 45,10 L 15,120 M 45,10 L 75,120 M 25,80 L 65,80 M 30,55 L 60,55" stroke="#93a1b5" stroke-width="1.5" fill="none"/>
    <rect x="38" y="4" width="14" height="8" fill="#93a1b5"/>
    <path d="M 8,55 Q 45,45 82,55" stroke="#2dd4bf" stroke-width="1.2" fill="none" opacity=".7"/>
    <path d="M 8,80 Q 45,70 82,80" stroke="#2dd4bf" stroke-width="1.2" fill="none" opacity=".7"/>
    <text x="45" y="140" text-anchor="middle">Transmission</text>
    <text x="45" y="155" text-anchor="middle" class="small">115&#8211;765 kV, long distance</text>
  </g>
  <g transform="translate(460,55)">
    <rect x="0" y="20" width="90" height="60" rx="6" fill="#121c30" stroke="#22304a" stroke-width="1.5"/>
    <circle cx="25" cy="50" r="10" fill="none" stroke="#93a1b5" stroke-width="1.5"/>
    <circle cx="45" cy="50" r="10" fill="none" stroke="#93a1b5" stroke-width="1.5"/>
    <circle cx="65" cy="50" r="10" fill="none" stroke="#93a1b5" stroke-width="1.5"/>
    <line x1="10" y1="72" x2="80" y2="72" stroke="#93a1b5" stroke-width="1.5"/>
    <text x="45" y="105" text-anchor="middle">Substation</text>
    <text x="45" y="120" text-anchor="middle" class="small">Step-down to 12&#8211;34 kV</text>
  </g>
  <g transform="translate(680,55)">
    <rect x="0" y="20" width="120" height="60" rx="6" fill="#121c30" stroke="#2dd4bf" stroke-width="1.5"/>
    <rect x="0" y="20" width="120" height="10" fill="#22304a"/>
    <g fill="#2dd4bf">
      <rect x="6" y="35" width="108" height="5" opacity=".6"/>
      <rect x="6" y="44" width="80" height="5" opacity=".45"/>
      <rect x="6" y="53" width="108" height="5" opacity=".6"/>
      <rect x="6" y="62" width="66" height="5" opacity=".35"/>
      <rect x="6" y="71" width="108" height="5" opacity=".55"/>
    </g>
    <text x="60" y="105" text-anchor="middle">Data center</text>
    <text x="60" y="120" text-anchor="middle" class="small">50&#8211;300+ MW continuous</text>
  </g>
</svg>'''


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
        body, f"{SITE_URL}/states/", depth=1,
        jsonld=_breadcrumb(("Home", SITE_URL), ("States", f"{SITE_URL}/states/")))


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
        body, f"{SITE_URL}/health-risks",
        jsonld=_breadcrumb(("Home", SITE_URL), ("Health risks", f"{SITE_URL}/health-risks")))


def _md_to_html(text):
    """Convert markdown body to HTML, stripping Streamlit LaTeX escapes."""
    text = text.replace("\\$", "$")
    md = markdown.Markdown(extensions=["tables"])
    return md.convert(text)


def _sorted_posts():
    return sorted(BLOG_STORIES, key=lambda s: s["date"], reverse=True)


# Build a (state name, abbrev) list from STATE_PUCS_DF so we can auto-detect
# which posts mention which states. Two-letter abbrevs are matched only as
# whole tokens preceded by a comma/space (e.g. "Ashburn, VA") to avoid the
# classic "OR/IN/OK" false positives inside prose.
_STATE_LIST = [(r["state"], r["abbrev"]) for _, r in STATE_PUCS_DF.iterrows()]

import re as _re
_ABBREV_TOKEN = {
    abbrev: _re.compile(rf"(?:,\s*|\bstate\s+of\s+){_re.escape(abbrev)}\b"
                        rf"|\b{_re.escape(abbrev)}(?=\s+(?:H\.?B\.?|S\.?B\.?|PUC|PSC))")
    for _, abbrev in _STATE_LIST
}

def _post_states(story):
    """Return sorted list of state names mentioned in a post's title/summary/body/tags."""
    cached = story.get("_states")
    if cached is not None:
        return cached
    haystack = " ".join([
        story.get("title", ""),
        story.get("summary", ""),
        story.get("body", ""),
        " ".join(story.get("tags", [])),
    ])
    hits = set()
    # Strip out well-known non-state uses of state names before matching.
    cleaned = haystack
    for bad in ("Washington Post", "Washington, D.C.", "Washington DC",
                "Washington, DC", "New Yorker", "New York Times",
                "Georgia Tech"):
        cleaned = cleaned.replace(bad, " ")
    for name, abbrev in _STATE_LIST:
        if _re.search(rf"\b{_re.escape(name)}\b", cleaned, _re.IGNORECASE):
            hits.add(name)
            continue
        # Fall back to abbrev only in tight postal-style contexts
        if _ABBREV_TOKEN[abbrev].search(haystack):
            hits.add(name)
    story["_states"] = sorted(hits)
    return story["_states"]


def _posts_for_state(state_name, limit=None):
    matches = [s for s in _sorted_posts() if state_name in _post_states(s)]
    return matches[:limit] if limit else matches


# Populated during main(); state pages read these to render their per-state
# news + video sections without re-fetching.
_NEWS_ITEMS = []
_VIDEO_ITEMS = []

def _news_for_state(state_name, limit=6):
    return [it for it in _NEWS_ITEMS
            if state_name in it.get("states", [])][:limit]

def _videos_for_state(state_name, limit=4):
    return [it for it in _VIDEO_ITEMS
            if state_name in it.get("states", [])][:limit]


# ── Live news headlines (fetched at build time) ─────────────────────────── #
# One broad Google News query, bucketed into states using the same detection
# logic as blog posts. Cached to data/news_cache.json so builds work offline
# and don't hammer Google News on every rebuild. Set NEWS_REFRESH=1 to force.

NEWS_CACHE_PATH = pathlib.Path(__file__).parent / "data" / "news_cache.json"
NEWS_CACHE_TTL_HOURS = 6

def _news_states_for(item):
    haystack = " ".join([item.get("title", ""), item.get("source", "")])
    # Strip common non-state uses before matching abbrev/name.
    cleaned = haystack
    for bad in ("Washington Post", "Washington, D.C.", "Washington DC",
                "Washington, DC", "New Yorker", "New York Times",
                "Georgia Tech"):
        cleaned = cleaned.replace(bad, " ")
    hits = set()
    for name, abbrev in _STATE_LIST:
        if _re.search(rf"\b{_re.escape(name)}\b", cleaned, _re.IGNORECASE):
            hits.add(name)
            continue
        if _ABBREV_TOKEN[abbrev].search(haystack):
            hits.add(name)
    return sorted(hits)


def _fetch_google_news_rss(query, limit=60):
    """Fetch and parse one Google News RSS query. Returns a list of item dicts
    (title/source/link/published/published_iso/age_days) or [] on failure. No
    streamlit dependency, no ranking, no theme/state tagging — pure I/O."""
    import urllib.parse as _up
    import urllib.request as _ur
    import xml.etree.ElementTree as _ET
    import datetime as _dt
    from email.utils import parsedate_to_datetime
    from src.constants import GOOGLE_NEWS_RSS
    try:
        url = GOOGLE_NEWS_RSS.format(q=_up.quote(query))
        req = _ur.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with _ur.urlopen(req, timeout=20) as resp:
            data = resp.read()
        root = _ET.fromstring(data)
    except Exception as e:                                        # noqa: BLE001
        print(f"  [news] fetch failed for query {query!r}: {e}")
        return []
    now = _dt.datetime.now(_dt.timezone.utc)
    out = []
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        src_el = it.find("source")
        source = src_el.text.strip() if src_el is not None and src_el.text else ""
        if source and title.endswith(f" - {source}"):
            title = title[: -(len(source) + 3)]
        pub_raw = (it.findtext("pubDate") or "").strip()
        pub_iso = ""
        age_days = None
        if pub_raw:
            try:
                parsed = parsedate_to_datetime(pub_raw)
                pub_iso = parsed.isoformat()
                age_days = (now - parsed).days
            except Exception:                                     # noqa: BLE001
                pub_iso = ""
                age_days = None
        out.append({
            "title": title,
            "source": source,
            "link": (it.findtext("link") or "").strip(),
            "published": pub_raw,
            "published_iso": pub_iso,
            "age_days": age_days,
        })
        if len(out) >= limit:
            break
    return out


def _fetch_news_live(limit=60):
    """Broad community-impact query used by state pages and the flat feed.
    Returns a list of items (each tagged with `states`) or None on failure."""
    from src.constants import STORY_QUERY
    items = _fetch_google_news_rss(STORY_QUERY, limit=limit)
    if not items:
        return None
    for it in items:
        it["states"] = _news_states_for(it)
    return items


def _story_angle_build(title):
    """Build-time port of src.services.news._story_angle (no streamlit dep)."""
    t = (title or "").lower()
    for keys, emoji, blurb in STORY_ANGLES:
        if any(k in t for k in keys):
            return emoji, blurb
    return "⚠️", "A community is pushing back on a nearby data center."


def _rank_stories_build(items, top_n=5):
    """Build-time port of src.services.news.rank_stories. Score = recency +
    summed weights of high-stakes keywords in the title. Returns new dicts
    annotated with score/angle_emoji/angle_blurb, most-important first."""
    scored = []
    for it in items or []:
        title = it.get("title") or ""
        t = title.lower()
        weight = sum(w for kw, w in STORY_IMPACT_WEIGHTS.items() if kw in t)
        age = it.get("age_days")
        recency = 3.0 if age is None else max(0.0, 3.0 - 0.4 * age)
        emoji, blurb = _story_angle_build(title)
        scored.append({**it, "score": round(weight + recency, 2),
                       "angle_emoji": emoji, "angle_blurb": blurb})
    scored.sort(key=lambda s: s["score"], reverse=True)
    return scored[:top_n]


def _fetch_themes_live(limit_per_theme=20):
    """One RSS pull per NEWS_THEMES entry. Returns dict of theme→items (each
    tagged with `states`). Missing themes get an empty list, never omitted."""
    out = {}
    for theme, query in NEWS_THEMES.items():
        items = _fetch_google_news_rss(query, limit=limit_per_theme)
        for it in items:
            it["states"] = _news_states_for(it)
            it["theme"] = theme
        out[theme] = items
        print(f"  [news] theme {theme!r}: {len(items)} items")
    return out


def _rank_top_stories_from_themes(themes, max_age_days=7, top_n=5):
    """Pool every theme's items, dedupe by link, gate to the last week, rank.
    Uses the theme pulls (already fetched) instead of a separate STORY_QUERY
    call — one fewer HTTP round-trip per build."""
    seen, pooled = set(), []
    for items in themes.values():
        for it in items:
            link = it.get("link", "")
            if not link or link in seen:
                continue
            age = it.get("age_days")
            if age is not None and age > max_age_days:
                continue
            seen.add(link)
            pooled.append(it)
    return _rank_stories_build(pooled, top_n=top_n)


# Quality-source allowlist — used to filter Google News video results to
# outlets we trust. Match is case-insensitive substring on the source name.
YOUTUBE_QUALITY_SOURCES = {
    "pbs", "wsj", "wall street journal", "bloomberg", "cnbc", "reuters",
    "financial times", "the verge", "vox", "npr", "cbs news", "abc news",
    "nbc news", "cnn", "bbc", "utility dive", "canary media", "grid brief",
    "e&e news", "inside climate news", "propublica", "the guardian",
    "washington post", "new york times", "politico", "axios", "60 minutes",
    "frontline", "vice news", "yahoo finance", "fox business", "bloomberg tv",
    "cbs mornings", "cbs saturday morning",
}

# Google News search query dedicated to YouTube-hosted videos.
YOUTUBE_QUERY = ('("data center" OR "data centers" OR datacenter) '
                 '(community OR moratorium OR ratepayer OR noise OR water '
                 'OR grid OR electricity OR lawsuit OR zoning) '
                 'site:youtube.com')


def _extract_youtube_id(url):
    import urllib.parse as _up
    try:
        u = _up.urlparse(url)
        host = (u.netloc or "").lower()
        if "youtube.com" in host:
            qs = _up.parse_qs(u.query)
            if "v" in qs and qs["v"]:
                return qs["v"][0]
            # /shorts/<id> and /embed/<id>
            parts = [p for p in u.path.split("/") if p]
            if len(parts) >= 2 and parts[0] in ("shorts", "embed", "v"):
                return parts[1]
        if "youtu.be" in host:
            parts = [p for p in u.path.split("/") if p]
            if parts:
                return parts[0]
    except Exception:                                             # noqa: BLE001
        pass
    return ""


def _fetch_youtube_live(limit=40):
    """Query Google News RSS for YouTube-hosted videos on data-center topics.
    Google News wraps YouTube links in an opaque redirect; the browser follows
    it to the underlying watch page. We keep the redirect URL and skip
    thumbnails (no video id extractable without decoding the redirect)."""
    import urllib.parse as _up
    import urllib.request as _ur
    import xml.etree.ElementTree as _ET
    from src.constants import GOOGLE_NEWS_RSS
    try:
        url = GOOGLE_NEWS_RSS.format(q=_up.quote(YOUTUBE_QUERY))
        req = _ur.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with _ur.urlopen(req, timeout=20) as resp:
            data = resp.read()
        root = _ET.fromstring(data)
    except Exception as e:                                        # noqa: BLE001
        print(f"  [youtube] fetch failed: {e}")
        return []
    from email.utils import parsedate_to_datetime
    # Google News OR-matches loosely, so re-filter titles ourselves:
    # require BOTH a data-center term and at least one impact/community term.
    DC_TERMS = ("data center", "datacenter", "data centre", "hyperscale")
    IMPACT_TERMS = (
        "community", "residents", "neighbor", "neighbour", "noise",
        "water", "cooling", "moratorium", "ban", "ratepayer", "bill",
        "grid", "electricity", "power", "utility", "lawsuit", "sue",
        "zoning", "rezoning", "permit", "protest", "opposition",
        "environmental", "pollution", "health", "town", "county",
    )
    JUNK = ("shocked", "shock you", "shocking", "you won't believe",
            "must watch", "insane", "gone wrong", "bitcoin", "coldcard",
            "kevin o'leary", "kevin oleary")
    out = []
    seen_titles = set()
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        # Google News appends " - YouTube" to the title
        if title.endswith(" - YouTube"):
            title = title[: -len(" - YouTube")]
        src_el = it.find("source")
        source = src_el.text.strip() if src_el is not None and src_el.text else "YouTube"
        if source and title.endswith(f" - {source}"):
            title = title[: -(len(source) + 3)]
        tl = title.lower()
        if any(j in tl for j in JUNK):
            continue
        if not any(t in tl for t in DC_TERMS):
            continue
        if not any(t in tl for t in IMPACT_TERMS):
            continue
        link = (it.findtext("link") or "").strip()
        if not link:
            continue
        # Dedupe by normalized title
        key = tl.strip()
        if key in seen_titles:
            continue
        seen_titles.add(key)
        pub_raw = (it.findtext("pubDate") or "").strip()
        pub_iso = ""
        if pub_raw:
            try:
                pub_iso = parsedate_to_datetime(pub_raw).isoformat()
            except Exception:                                     # noqa: BLE001
                pub_iso = ""
        item = {
            "title": title,
            "source": source,
            "link": link,
            "video_id": "",  # unavailable — Google News wraps the URL
            "published_iso": pub_iso,
        }
        item["states"] = _news_states_for(item)
        out.append(item)
        if len(out) >= limit:
            break
    out.sort(key=lambda x: x.get("published_iso", ""), reverse=True)
    return out


YOUTUBE_CACHE_PATH = pathlib.Path(__file__).parent / "data" / "youtube_cache.json"

def _load_youtube():
    import datetime as _dt
    cache = None
    if YOUTUBE_CACHE_PATH.exists():
        try:
            cache = json.loads(YOUTUBE_CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:                                         # noqa: BLE001
            cache = None
    force = os.environ.get("NEWS_REFRESH") == "1"
    fresh = False
    if cache and not force:
        try:
            fetched = _dt.datetime.fromisoformat(cache["fetched_at"])
            age_h = (_dt.datetime.now(_dt.timezone.utc) - fetched).total_seconds() / 3600
            fresh = age_h < NEWS_CACHE_TTL_HOURS
        except Exception:                                         # noqa: BLE001
            fresh = False
    if fresh:
        return cache["items"], cache["fetched_at"]
    live = _fetch_youtube_live()
    if not live:
        if cache:
            return cache["items"], cache["fetched_at"]
        return [], _dt.datetime.now(_dt.timezone.utc).isoformat()
    fetched_at = _dt.datetime.now(_dt.timezone.utc).isoformat()
    YOUTUBE_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    YOUTUBE_CACHE_PATH.write_text(
        json.dumps({"fetched_at": fetched_at, "items": live}, indent=2),
        encoding="utf-8")
    print(f"  [youtube] fetched {len(live)} videos")
    return live, fetched_at


def _load_news():
    """Return (items, themes, top_stories, fetched_at_iso). Uses cached JSON
    when fresh; refreshes otherwise. Falls back to whatever cache exists if
    the live fetch fails. `items` is the flat community-impact feed used by
    state pages and the RSS; `themes` maps NEWS_THEMES keys to their per-theme
    feeds; `top_stories` are ranked most-important-first for the last 7 days."""
    import datetime as _dt
    cache = None
    if NEWS_CACHE_PATH.exists():
        try:
            cache = json.loads(NEWS_CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:                                         # noqa: BLE001
            cache = None
    force = os.environ.get("NEWS_REFRESH") == "1"
    fresh_enough = False
    if cache and not force:
        try:
            fetched = _dt.datetime.fromisoformat(cache["fetched_at"])
            age_h = (_dt.datetime.now(_dt.timezone.utc) - fetched).total_seconds() / 3600
            fresh_enough = age_h < NEWS_CACHE_TTL_HOURS
        except Exception:                                         # noqa: BLE001
            fresh_enough = False
    # Older caches don't have `themes`/`top_stories` — treat those as stale
    # even within TTL so the new UX has data to render.
    if fresh_enough and ("themes" not in cache or "top_stories" not in cache):
        fresh_enough = False
    if fresh_enough:
        return (cache["items"], cache["themes"], cache["top_stories"],
                cache["fetched_at"])

    items = _fetch_news_live()
    themes = _fetch_themes_live()
    if items is None and not any(themes.values()):
        # Total network failure: fall back to whatever we had.
        if cache:
            print(f"  [news] using stale cache ({len(cache.get('items', []))} items)")
            return (cache.get("items", []),
                    cache.get("themes", {}),
                    cache.get("top_stories", []),
                    cache["fetched_at"])
        return [], {}, [], _dt.datetime.now(_dt.timezone.utc).isoformat()

    if items is None:
        items = []
    top_stories = _rank_top_stories_from_themes(themes)
    fetched_at = _dt.datetime.now(_dt.timezone.utc).isoformat()
    NEWS_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    NEWS_CACHE_PATH.write_text(
        json.dumps({
            "fetched_at": fetched_at,
            "items": items,
            "themes": themes,
            "top_stories": top_stories,
        }, indent=2),
        encoding="utf-8")
    theme_total = sum(len(v) for v in themes.values())
    print(f"  [news] fetched {len(items)} broad + {theme_total} across "
          f"{len(themes)} themes; top {len(top_stories)} ranked")
    return items, themes, top_stories, fetched_at


def build_news_page(items, fetched_at, videos=None, themes=None,
                    top_stories=None):
    """News page with three layers of live intel: ranked top-stories block,
    theme/state/keyword-filterable browse feed, and video coverage. Themes
    are pooled and deduped for the browse list; each item carries every
    theme bucket it appeared in so filtering picks up the union."""
    videos = videos or []
    themes = themes or {}
    top_stories = top_stories or []

    # The browse feed prefers the per-theme corpus (richer + tagged) but falls
    # back to the flat broad-query items so an offline/degraded build still
    # renders something instead of an empty list.
    theme_items = [it for bucket in themes.values() for it in bucket]
    if not theme_items and items:
        theme_items = items
    if not (theme_items or items or top_stories):
        body = """
<header>
  <div class="kicker">News</div>
  <h1>This week's data center headlines</h1>
  <p class="sub">No headlines available right now.</p>
</header>
<section><p class="muted">The news feed couldn't be fetched during this build.
Try again shortly, or browse the <a href="blog/">blog</a> for our own analysis.</p></section>
"""
        return page("News — AI GridWatch",
                    "Latest community-impact data center news, updated regularly.",
                    body, f"{SITE_URL}/news/", depth=1)

    covered = sorted({st for it in (theme_items + items + videos)
                      for st in it.get("states", [])})
    state_options = '<option value="">All states</option>' + "".join(
        f'<option value="{esc(st)}">{esc(st)}</option>' for st in covered)
    theme_options = '<option value="">All themes</option>' + "".join(
        f'<option value="{esc(name)}">{esc(name)}</option>'
        for name in themes.keys())

    def _fmt_date(iso):
        if not iso:
            return ""
        try:
            import datetime as _dt
            d = _dt.datetime.fromisoformat(iso)
            return d.strftime("%b %-d, %Y")
        except Exception:                                         # noqa: BLE001
            return ""

    def _age_label(age_days):
        if age_days is None:
            return ""
        if age_days <= 0:
            return "today"
        if age_days == 1:
            return "yesterday"
        return f"{age_days} days ago"

    # ── Top stories block ─────────────────────────────────────────────────── #
    top_html = ""
    if top_stories:
        cards = []
        for i, s in enumerate(top_stories, 1):
            meta_bits = [s.get("source", ""), _age_label(s.get("age_days"))]
            meta = " · ".join(x for x in meta_bits if x)
            cards.append(
                '<li class="top-story">'
                f'<div class="rank">{i}</div>'
                f'<div class="angle">{esc(s.get("angle_emoji", "•"))}</div>'
                '<div class="top-body">'
                f'<h3><a href="{esc(s.get("link", ""))}" rel="nofollow noopener" '
                f'target="_blank">{esc(s.get("title", ""))}</a></h3>'
                f'<p class="blurb">{esc(s.get("angle_blurb", ""))}</p>'
                f'<p class="meta">{esc(meta)}</p>'
                '</div></li>')
        top_html = (
            '<section id="topStories"><h2>Top stories this week</h2>'
            '<p class="muted">Ranked automatically from the last 7 days by '
            'freshness plus urgency keywords — lawsuits, moratoriums, and rate '
            'hikes float highest. Heuristic, not editorial.</p>'
            f'<ol class="top-stories-list">{"".join(cards)}</ol></section>')

    # ── Browse feed: dedupe by link, union theme tags per item ───────────── #
    by_link = {}
    for it in theme_items:
        link = it.get("link", "")
        if not link:
            continue
        row = by_link.setdefault(link, {**it, "themes": []})
        theme_key = it.get("theme")
        if theme_key and theme_key not in row["themes"]:
            row["themes"].append(theme_key)
    # Sort newest first (published_iso), unknown dates last.
    feed_rows = sorted(by_link.values(),
                       key=lambda r: r.get("published_iso") or "",
                       reverse=True)

    li_html = ""
    for it in feed_rows:
        states = it.get("states", [])
        item_themes = it.get("themes", [])
        data_states = esc("|".join(states)) if states else ""
        data_themes = esc("|".join(item_themes)) if item_themes else ""
        chips = "".join(
            [f'<span class="tag tag-theme">{esc(t)}</span>' for t in item_themes]
            + [f'<span class="tag">{esc(st)}</span>' for st in states])
        meta_bits = [it.get("source", ""),
                     _fmt_date(it.get("published_iso", ""))]
        meta = " · ".join(x for x in meta_bits if x)
        li_html += (
            f'<li data-states="{data_states}" data-themes="{data_themes}">'
            f'<div class="post-meta">{esc(meta)}</div>'
            f'<h3><a href="{esc(it["link"])}" rel="nofollow noopener" '
            f'target="_blank">{esc(it["title"])}</a></h3>'
            f'{"<div class=\"tags\" style=\"margin-top:6px\">" + chips + "</div>" if chips else ""}'
            f'</li>\n')

    import datetime as _dt
    try:
        fetched_display = _dt.datetime.fromisoformat(fetched_at).strftime("%b %-d, %Y %H:%M UTC")
    except Exception:                                             # noqa: BLE001
        fetched_display = fetched_at

    # ── Video cards (YouTube) ──
    video_cards = ""
    if videos:
        cards = []
        for v in videos[:24]:
            vid = v.get("video_id", "")
            thumb = f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg' if vid else ""
            placeholder = (
                '<div style="width:100%;aspect-ratio:16/9;background:'
                'linear-gradient(135deg,#1a1f2e,#2d1a3d);display:flex;'
                'align-items:center;justify-content:center;font-size:42px;'
                'color:#ff4136">▶</div>')
            states = v.get("states", [])
            data_states = esc("|".join(states)) if states else ""
            chips = " ".join(f'<span class="tag">{esc(st)}</span>' for st in states)
            when = _fmt_date(v.get("published_iso", ""))
            meta = " · ".join(x for x in (v.get("source", ""), when) if x)
            cards.append(
                f'<a class="video-card" data-states="{data_states}" '
                f'href="{esc(v["link"])}" rel="nofollow noopener" target="_blank" '
                f'style="display:block;border:1px solid rgba(255,255,255,0.08);'
                f'border-radius:12px;overflow:hidden;text-decoration:none;color:inherit">'
                f'{("<img src=" + repr(thumb) + " alt=\"\" loading=\"lazy\" style=\"width:100%;display:block;aspect-ratio:16/9;object-fit:cover\">") if thumb else placeholder}'
                f'<div style="padding:12px 14px">'
                f'<div class="post-meta" style="font-size:12px;opacity:0.75">{esc(meta)}</div>'
                f'<div style="font-weight:600;margin:4px 0 6px;line-height:1.3">'
                f'{esc(v["title"])}</div>'
                f'{"<div class=\"tags\">" + chips + "</div>" if chips else ""}'
                f'</div></a>')
        video_cards = (
            '<section id="videos"><h2>Watch: video coverage</h2>'
            '<p class="muted">From vetted channels only — PBS NewsHour, WSJ, '
            'Bloomberg, CNBC, Reuters, FT, The Verge, Vox — filtered to data '
            'center / grid topics.</p>'
            '<div class="video-grid" style="display:grid;'
            'grid-template-columns:repeat(auto-fill,minmax(280px,1fr));'
            f'gap:16px;margin-top:16px">{"".join(cards)}</div>'
            '<p id="noVideos" class="muted" style="display:none;margin-top:16px">'
            'No videos tagged for that state yet.</p></section>')

    body = f"""
<header>
  <div class="kicker">News</div>
  <h1>Live intel — data center headlines</h1>
  <p class="sub">A live, automated read on what's happening: the top stories
  of the week ranked by impact, plus a browsable feed by theme, state, and
  keyword. Headlines come from Google News — follow each link to the original
  outlet.</p>
  <p class="muted">Last updated {esc(fetched_display)} ·
  <a href="feed.xml">RSS feed</a> · <a href="../blog/feed.xml">Blog RSS</a></p>
</header>

<style>
.top-stories-list {{ list-style:none; padding:0; margin:16px 0; display:grid;
  gap:12px; }}
.top-story {{ display:grid; grid-template-columns:36px 40px 1fr; gap:12px;
  align-items:start; padding:14px 16px; background:var(--card);
  border:1px solid var(--rule); border-radius:12px; }}
.top-story .rank {{ font-size:22px; font-weight:800; color:var(--teal);
  line-height:1; text-align:center; }}
.top-story .angle {{ font-size:24px; line-height:1; }}
.top-story .top-body h3 {{ font-size:16px; margin:0 0 4px; line-height:1.35; }}
.top-story .top-body h3 a {{ text-decoration:none; }}
.top-story .blurb {{ font-size:13.5px; color:var(--muted); margin:0 0 4px; }}
.top-story .meta {{ font-size:12.5px; color:var(--muted); margin:0; }}

.feed-controls {{ display:grid; gap:12px; margin:14px 0 18px;
  background:var(--card); border:1px solid var(--rule); border-radius:12px;
  padding:14px 16px; }}
.feed-controls .row {{ display:flex; gap:14px; flex-wrap:wrap;
  align-items:center; }}
.feed-controls label {{ font-size:13.5px; color:var(--muted); display:flex;
  gap:6px; align-items:center; }}
.feed-controls select, .feed-controls input[type=search] {{
  padding:7px 11px; border-radius:8px; border:1px solid var(--rule);
  background:rgba(255,255,255,.04); color:var(--ink); font-size:14px;
  min-width:180px; }}
.feed-controls input[type=search] {{ flex:1; min-width:200px; }}
.tag-theme {{ background:rgba(45,212,191,.14); color:var(--teal);
  border:1px solid rgba(45,212,191,.28); }}
</style>

{top_html}

<section id="browse">
  <h2>Browse the feed</h2>
  <div class="feed-controls">
    <div class="row">
      <label>Theme
        <select id="themeFilter">{theme_options}</select>
      </label>
      <label>State
        <select id="stateFilter">{state_options}</select>
      </label>
      <label style="flex:1">Keyword
        <input id="keywordFilter" type="search" placeholder="e.g. Loudoun, moratorium, water">
      </label>
    </div>
    <div class="row" style="justify-content:space-between">
      <span id="filterCount" class="muted"></span>
      <button id="resetFilters" class="btn ghost" style="padding:6px 12px;font-size:13px" type="button">Reset</button>
    </div>
  </div>

  <ul class="blog-list" id="newsList">{li_html}</ul>
  <p id="noResults" class="muted" style="display:none">No stories match those filters. Try a broader theme or clear the keyword.</p>
</section>

{video_cards}

<section>
  <p class="muted" style="margin-top:24px">Headlines are an automated news
  search, unfiltered and not endorsements — follow each link to the original
  outlet. State tags are auto-detected from the headline; a story may mention
  a state without being about that state.</p>
</section>

<script>
(function() {{
  var themeSel = document.getElementById('themeFilter');
  var stateSel = document.getElementById('stateFilter');
  var kw = document.getElementById('keywordFilter');
  var list = document.getElementById('newsList');
  var count = document.getElementById('filterCount');
  var none = document.getElementById('noResults');
  var reset = document.getElementById('resetFilters');
  var items = Array.prototype.slice.call(list.querySelectorAll('li'));
  var videoCards = Array.prototype.slice.call(document.querySelectorAll('.video-card'));
  var noVideos = document.getElementById('noVideos');

  function apply() {{
    var theme = themeSel.value;
    var state = stateSel.value;
    var kwVal = (kw.value || '').trim().toLowerCase();
    var shown = 0, vShown = 0;
    items.forEach(function(li) {{
      var states = (li.getAttribute('data-states') || '').split('|').filter(Boolean);
      var themes = (li.getAttribute('data-themes') || '').split('|').filter(Boolean);
      var text = li.textContent.toLowerCase();
      var match = (!theme || themes.indexOf(theme) !== -1)
                && (!state || states.indexOf(state) !== -1)
                && (!kwVal || text.indexOf(kwVal) !== -1);
      li.style.display = match ? '' : 'none';
      if (match) shown++;
    }});
    videoCards.forEach(function(c) {{
      var states = (c.getAttribute('data-states') || '').split('|').filter(Boolean);
      var match = !state || states.indexOf(state) !== -1;
      c.style.display = match ? '' : 'none';
      if (match) vShown++;
    }});
    var parts = [];
    if (theme || state || kwVal) {{
      parts.push(shown + ' stor' + (shown === 1 ? 'y' : 'ies'));
      if (theme) parts.push('theme: ' + theme);
      if (state) parts.push('state: ' + state);
      if (kwVal) parts.push('"' + kwVal + '"');
      count.textContent = parts.join(' · ');
    }} else {{
      count.textContent = items.length + ' items · newest first';
    }}
    none.style.display = ((theme || state || kwVal) && shown === 0) ? '' : 'none';
    if (noVideos) noVideos.style.display = (state && videoCards.length && vShown === 0) ? '' : 'none';
    // Persist theme/state/keyword to URL for shareable links.
    var qs = new URLSearchParams();
    if (theme) qs.set('theme', theme);
    if (state) qs.set('state', state);
    if (kwVal) qs.set('q', kwVal);
    var qStr = qs.toString();
    history.replaceState(null, '', qStr ? ('?' + qStr) : location.pathname);
  }}

  themeSel.addEventListener('change', apply);
  stateSel.addEventListener('change', apply);
  kw.addEventListener('input', apply);
  reset.addEventListener('click', function() {{
    themeSel.value = '';
    stateSel.value = '';
    kw.value = '';
    apply();
  }});

  // Restore filters from URL (?theme=…&state=…&q=…)
  var q = new URLSearchParams(location.search);
  if (q.get('theme')) themeSel.value = q.get('theme');
  if (q.get('state')) stateSel.value = q.get('state');
  if (q.get('q')) kw.value = q.get('q');
  apply();
}})();
</script>
"""
    return page(
        "News — data center headlines by state — AI GridWatch",
        "Latest community-impact data center news — noise, water, rate hikes, "
        "moratoriums, lawsuits — updated regularly and filterable by state.",
        body, f"{SITE_URL}/news/", depth=1,
        jsonld=_breadcrumb(("Home", SITE_URL), ("News", f"{SITE_URL}/news/")))


def build_news_rss(items, fetched_at):
    parts = []
    for it in items[:40]:
        pub_raw = it.get("published", "").strip()
        # Use the raw RFC-822 date from Google News if present.
        pub_field = f"<pubDate>{esc(pub_raw)}</pubDate>" if pub_raw else ""
        parts.append(
            "    <item>\n"
            f"      <title>{esc(it['title'])}</title>\n"
            f"      <link>{esc(it['link'])}</link>\n"
            f"      <guid isPermaLink=\"true\">{esc(it['link'])}</guid>\n"
            f"      {pub_field}\n"
            f"      <source>{esc(it.get('source', ''))}</source>\n"
            f"      <description>{esc(it['title'])} — {esc(it.get('source', ''))}</description>\n"
            "    </item>\n")
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
            f'<channel>\n'
            f'  <title>AI GridWatch — Data Center News</title>\n'
            f'  <link>{SITE_URL}/news/</link>\n'
            f'  <description>Community-impact data center news: noise, water, '
            f'rate hikes, moratoriums, lawsuits.</description>\n'
            f'  <language>en-US</language>\n'
            f'  <atom:link href="{SITE_URL}/news/feed.xml" rel="self" '
            f'type="application/rss+xml"/>\n'
            f'{"".join(parts)}'
            f'</channel>\n</rss>\n')


def build_blog_index():
    posts = _sorted_posts()
    # Collect the set of states that actually appear in at least one post so
    # the dropdown doesn't offer states with zero results.
    covered_states = sorted({st for s in posts for st in _post_states(s)})
    options = '<option value="">All states</option>' + "".join(
        f'<option value="{esc(st)}">{esc(st)}</option>' for st in covered_states)
    items = ""
    for s in posts:
        title_clean = s["title"].replace("\\$", "$")
        summary_clean = s["summary"].replace("\\$", "$")
        states = _post_states(s)
        data_states = esc("|".join(states)) if states else ""
        state_chips = " ".join(
            f'<span class="tag">{esc(st)}</span>' for st in states)
        # uid must be unique per document — every post's art lives in this one
        # page, and duplicate gradient ids would all resolve to the first.
        thumb = art_svg(s, cls="thumb", uid=f"t-{s['id']}")
        items += (
            f'<li class="has-art" data-states="{data_states}">'
            f'<a href="{s["id"]}.html" aria-hidden="true" tabindex="-1">{thumb}</a>'
            f'<div>'
            f'<div class="post-meta">{s["date"].strftime("%b %-d, %Y")}</div>'
            f'<h3><a href="{s["id"]}.html">{esc(title_clean)}</a></h3>'
            f'<p class="summary">{esc(summary_clean)}</p>'
            f'{"<div class=\"tags\" style=\"margin-top:6px\">" + state_chips + "</div>" if state_chips else ""}'
            f'</div></li>\n'
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
  <div class="filter-bar" style="display:flex;gap:12px;align-items:center;margin-bottom:16px;flex-wrap:wrap">
    <label for="stateFilter" style="font-weight:600">Filter by state:</label>
    <select id="stateFilter" style="padding:8px 12px;border-radius:8px;border:1px solid #ccc;font-size:15px;background:inherit;color:inherit">{options}</select>
    <span id="filterCount" class="muted"></span>
  </div>
  <ul class="blog-list" id="blogList">{items}</ul>
  <p id="noResults" class="muted" style="display:none">No posts tagged for that state yet.</p>
</section>
<script>
(function() {{
  var sel = document.getElementById('stateFilter');
  var list = document.getElementById('blogList');
  var count = document.getElementById('filterCount');
  var none = document.getElementById('noResults');
  var items = Array.prototype.slice.call(list.querySelectorAll('li'));
  function apply() {{
    var v = sel.value;
    var shown = 0;
    items.forEach(function(li) {{
      var states = (li.getAttribute('data-states') || '').split('|').filter(Boolean);
      var match = !v || states.indexOf(v) !== -1;
      li.style.display = match ? '' : 'none';
      if (match) shown++;
    }});
    count.textContent = v ? shown + ' post' + (shown === 1 ? '' : 's') + ' for ' + v : '';
    none.style.display = (v && shown === 0) ? '' : 'none';
    if (v) {{
      history.replaceState(null, '', '?state=' + encodeURIComponent(v));
    }} else {{
      history.replaceState(null, '', location.pathname);
    }}
  }}
  sel.addEventListener('change', apply);
  var q = new URLSearchParams(location.search).get('state');
  if (q) {{
    for (var i = 0; i < sel.options.length; i++) {{
      if (sel.options[i].value === q) {{ sel.selectedIndex = i; break; }}
    }}
    apply();
  }}
}})();
</script>
"""
    return page(
        "Blog — AI GridWatch",
        "Analysis and explainers on data center development, grid impact, "
        "and community advocacy from AI GridWatch.",
        body, f"{SITE_URL}/blog/", depth=1,
        jsonld=_breadcrumb(("Home", SITE_URL), ("Blog", f"{SITE_URL}/blog/")))


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
{art_svg(story, cls="post-art")}
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
        og_type="article", og_extra=og_extra,
        jsonld=[
            _breadcrumb(("Home", SITE_URL), ("Blog", f"{SITE_URL}/blog/"), (title_clean, f"{SITE_URL}/blog/{story['id']}")),
            _article_schema(title_clean, summary_clean, f"{SITE_URL}/blog/{story['id']}", story["date"].isoformat(), story["author"]),
        ])


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
  {provenance_html("STATE_GRID_PROFILES")}
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
        body, f"{SITE_URL}/impact",
        jsonld=_breadcrumb(("Home", SITE_URL), ("Calculator", f"{SITE_URL}/impact")))


def cell(value, dash="—"):
    """Render a possibly-missing DataFrame value, escaped, or an em-dash.

    Do NOT test `str(v) != "nan"` here. Whether a missing object-column value
    arrives as None or as NaN depends on the pandas major version: 2.x keeps
    None (so str() gives "None") while 3.x coerces to NaN. Comparing against
    the *string* silently rendered the literal word "None" on five state pages
    in production, and only surfaced because CI built on a different pandas
    than the machine that generated the committed HTML. pd.isna() handles
    both.
    """
    if value is None or (not isinstance(value, str) and pd.isna(value)):
        return dash
    text = str(value).strip()
    return esc(text) if text and text.lower() != "nan" else dash


def _srcref(key):
    """Inline markdown-free source link from SOURCES, or "" if unknown."""
    if key not in SOURCES:
        return ""
    name, url = SOURCES[key]
    return f'<a href="{esc(url)}" rel="nofollow">{esc(name)}</a>'


# Composition of expenses for major U.S. investor-owned utilities, 2023
# (FERC Form 1 via EIA EPA table 8.3) per LBNL Retail Price & Cost Trends 2024.
# Ported from bills_tab's Altair chart — same numbers, drawn in CSS.
_BILL_PARTS = [
    ("Fuel &amp; purchased power", 36, "#3b82f6"),
    ("Operations &amp; maintenance", 23, "#f59e0b"),
    ("Depreciation", 16, "#ef4444"),
    ("General &amp; administrative", 13, "#a855f7"),
    ("Taxes &amp; other", 12, "#6b7280"),
]


def build_bills():
    """Utility-bill explainer — ported from src/ui/bills_tab.py.

    All prose and tables move across unchanged; the one Altair chart becomes a
    CSS bar. Streamlit's `\\$` escapes are dropped — this is HTML, not Streamlit
    markdown, so dollar signs are literal.
    """
    bar = "".join(
        f'<div style="width:{pct}%;background:{c}">{pct}%</div>'
        for _, pct, c in _BILL_PARTS)
    key = "".join(
        f'<span><i style="background:{c}"></i>{name}</span>'
        for name, _, c in _BILL_PARTS)

    body = f"""
<header>
  <div class="kicker">Explainer</div>
  <h1>Your utility bill: what's actually driving it up</h1>
  <p class="sub">How electricity bills work, why peak demand sets your annual
  cost, and what the research says about data centers and ratepayer cost
  shifts.</p>
</header>

<section>
  <h2>Anatomy of your electric bill</h2>
  <p>You see one blended rate. But every dollar splits into two very different
  things: the electricity you <strong>use</strong>, and the grid capacity that
  must <strong>exist</strong> to serve the single highest moment of demand all
  year. Data-center growth hits the second kind hardest.</p>
  <div class="billbar">{bar}</div>
  <div class="barkey">{key}</div>
  <p class="src" style="margin-top:10px">Composition of expenses for major U.S.
  investor-owned utilities in 2023, per {_srcref('lbnl_price_trends')}. Fuel and
  purchased power is the only large piece that scales with how much electricity
  you use — the rest is largely fixed: the plants, wires, people, and capital
  that must exist to run the system. On a home bill it all arrives as one
  blended per-kWh rate.</p>
  <div class="stats">
    <div class="stat"><b>~36%</b><span>tracks your usage — fuel &amp; purchased power</span></div>
    <div class="stat"><b>~64%</b><span>fixed system costs — plants, wires, staff &amp; capital</span></div>
  </div>
  <details class="more"><summary>Read more — what each charge actually is</summary>
    <h3>Fuel &amp; purchased power — what you use</h3>
    <p>The fuel and wholesale power a utility buys to serve you — the largest
    single expense (~36%) and the most volatile. It drove the 2021–22 bill spike
    as natural-gas prices surged (gas sets ~40% of U.S. generation), and eased
    as they fell back.</p>
    <h3>The grid — what must exist</h3>
    <p>Wires, substations, and their upkeep, sized for the single highest moment
    of demand, not the average. Distribution is now the largest and
    fastest-growing slice of utility investment — capital spending on it grew
    ~50% from 2019–2023, even as spending on power plants fell.</p>
    <h3>The long-run shift</h3>
    <p>Over two decades the balance has tilted from producing power toward
    delivering it: EIA finds power production fell from 69% (2006) to 54% of
    utility costs while delivery climbed to 46%. New large loads accelerate that
    grid spending — and it's recovered from everyone.</p>
  </details>
  <div class="note info"><p><strong>Key insight:</strong> The fastest-growing
  part of your bill is the grid itself. Utility capital spending on the
  distribution network grew ~50% from 2019 to 2023 — now the single largest
  category of investment (44%) — while spending on power plants fell. New peak
  loads like data centers require exactly this kind of grid buildout, and those
  costs are recovered from every ratepayer on the system.</p></div>
</section>

<section>
  <h2>Three customers, three completely different bills</h2>
  <p>Everyone pays for the same grid, but costs land radically differently:
  <strong>homes</strong> get one blended rate they can't see into or manage;
  <strong>businesses</strong> get a demand meter and actively shave peaks;
  <strong>data centers</strong> negotiate custom tariffs with dedicated energy
  teams.</p>
  <div style="overflow-x:auto">
  <table>
    <tr><th></th><th>Residential</th><th>Commercial</th><th>Industrial / data center</th></tr>
    <tr><td><strong>Sees demand charges?</strong></td><td>No — buried in kWh rate</td><td>Yes — explicit $/kW line item</td><td>Yes — negotiated and managed</td></tr>
    <tr><td><strong>Has a demand meter?</strong></td><td>Rarely</td><td>Yes — 15-min interval</td><td>Yes — 5–15 min interval</td></tr>
    <tr><td><strong>Can manage peak usage?</strong></td><td>Barely — no real-time signal</td><td>Yes — building automation</td><td>Yes — dedicated energy team</td></tr>
    <tr><td><strong>Capacity cost allocation</strong></td><td>Socialized across all ratepayers</td><td>Partly based on individual peak</td><td>Negotiated; often discounted</td></tr>
    <tr><td><strong>Benefits from curtailment?</strong></td><td>No direct savings</td><td>Yes — lower demand charge</td><td>Yes — but won't do it (SLAs)</td></tr>
    <tr><td><strong>Typical monthly bill</strong></td><td>$150–250</td><td>$5,000–50,000</td><td>$500,000–5,000,000+</td></tr>
  </table>
  </div>
  <div class="note bad"><p><strong>The core inequity:</strong> Industrial
  customers like data centers have dedicated demand meters, energy management
  teams, and negotiated rates that let them optimize their costs. Residential
  customers have none of these tools — yet when data center growth drives up
  system-wide capacity costs, those costs are socialized into the blended
  per-kWh rate that homeowners pay. The customers with the least ability to
  respond bear a disproportionate share of the cost caused by the customers
  with the most ability to respond.</p></div>
  <details class="more"><summary>How this works in different market structures</summary>
    <p><strong>Deregulated markets (PJM, ISO-NE, NYISO)</strong> — Capacity is
    procured through auctions. The cost is allocated to utilities based on their
    total load during system peak hours, then passed through to customers.
    Residential customers see it as a line item or bundled into the default
    service rate. C&amp;I customers see explicit demand and capacity charges and
    can manage them.</p>
    <p><strong>Regulated / vertically integrated markets (Duke, Southern,
    Entergy)</strong> — No separate capacity market. The utility owns generation
    and recovers costs through base rates set in rate cases. When it builds new
    capacity to serve data center growth, the capital is rate-based and
    recovered from all customers through higher per-kWh rates.</p>
    <p><strong>ERCOT (Texas)</strong> — No capacity market at all. Texas uses an
    energy-only market where scarcity pricing during peak hours is supposed to
    incentivize generation investment. Residential customers on variable-rate
    plans are directly exposed to wholesale spikes (which is why bills exploded
    during Winter Storm Uri). Data centers can negotiate bilateral PPAs that
    lock in low prices, shifting scarcity cost to the remaining pool.</p>
    <p>In all three structures the pattern holds: large industrial loads have
    tools, tariffs, and negotiating power to manage their exposure. Residential
    customers absorb socialized costs with no visibility and no control.</p>
  </details>
</section>

<section>
  <h2>Peak load: why the hottest afternoon sets your annual bill</h2>
  <div class="flow">
    <div class="step"><b>New 200 MW data center</b>Adds constant baseload</div>
    <div class="step"><b>System peak rises</b>Grid must build for the highest hour</div>
    <div class="step"><b>New capacity needed</b>Substations, transmission, plants</div>
    <div class="step end"><b>Your bill goes up $15–21/mo</b>Costs socialized to all ratepayers</div>
  </div>
  <p>Electricity can't be stored cheaply at scale, so the grid must be built for
  the single highest hour of demand each year. When a big new load raises that
  peak, every customer's capacity allocation increases.</p>
  <div class="stats">
    <div class="stat"><b>+833%</b><span>PJM capacity auction — $28.92 to $269.92/MW-day</span></div>
    <div class="stat"><b>63%</b><span>of the price increase driven by data centers</span></div>
    <div class="stat"><b>+$15–21/mo</b><span>bill impact in affected PJM zones</span></div>
  </div>
  <details class="more"><summary>Read more — how the peak drives costs</summary>
    <p><strong>Capacity obligation</strong> — grid operators run auctions years
    in advance so power plants commit to being available during peak. Those
    commitments cost money whether or not the plants run.</p>
    <p><strong>Peaker plants</strong> — gas plants that run only 50–200 hours a
    year but must be maintained year-round. Their per-MWh cost is enormous.</p>
    <p><strong>Transmission upgrades</strong> — wires are sized for the peak,
    not the average. Building for a 2 GW peak instead of 1.5 GW can mean
    billions in new lines.</p>
    <p><strong>The "coincident peak" trap</strong> — many utilities set your
    capacity charge from your usage during the single highest-demand hour across
    the grid that year. A large new load raises that peak, and every customer's
    allocation increases, even those whose own usage didn't change.</p>
  </details>
</section>

<section>
  <h2>How wholesale MW charges actually land on your bill</h2>
  <div class="flow">
    <div class="step"><b>Step 1</b>Capacity auction clears at $269.92/MW-day</div>
    <div class="step"><b>Step 2</b>Your utility buys in bulk: $800M–$1.2B</div>
    <div class="step"><b>Step 3</b>Your "capacity tag" is set by 5 peak hours</div>
    <div class="step end"><b>Step 4</b>Shows up as a line item — or buried in your rate</div>
  </div>
  <details class="more"><summary>Read more — the four-step chain, in detail</summary>
    <p><strong>Your utility buys capacity in bulk.</strong> It must procure
    enough to cover every customer's share of the system peak, plus a reserve
    margin. For a utility serving 1 million homes in PJM, the 2025/26 auction
    cost roughly $800M–$1.2B in capacity obligations alone — before a single
    electron flows.</p>
    <p><strong>Allocation via your capacity tag.</strong> In PJM every customer
    gets a Peak Load Contribution — your usage during the five highest-demand
    hours of the prior summer, averaged. Ran the AC hard on those afternoons?
    You carry a bigger share. Most customers have no idea which hours set it.</p>
    <p><strong>Line item — or buried.</strong> Deregulated utilities (Pepco,
    BGE, PECO) show an explicit capacity line item; regulated ones (Duke,
    Dominion, Southern) roll it into a blended supply rate; co-ops bury it in
    the base rate. Pepco customers got a notice in spring 2025 that capacity
    charges were rising ~$10/month.</p>
    <p><strong>Time-of-use pricing.</strong> Some utilities charge more during
    peak hours (2–7 PM summer weekdays) to push usage off-peak — your bill
    depends on when you use power, not just how much.</p>
  </details>
  <h3>A worked example: the PJM capacity cost on a typical home</h3>
  <div class="stats">
    <div class="stat"><b>2.5 kW</b><span>typical residential capacity tag (PLC)</span></div>
    <div class="stat"><b>$2.20/mo</b><span>2024/25 capacity cost — before the jump</span></div>
    <div class="stat"><b>$20.50/mo</b><span>2025/26 capacity cost — after the 833% increase</span></div>
  </div>
  <p>That <strong>$18.30/month increase</strong> — about <strong>$220 a
  year</strong> — is entirely from the capacity market. Your usage didn't
  change. Your appliances didn't change. The grid's obligation changed because
  total system peak demand grew, driven largely by data center load.</p>
  <div class="note info"><p><strong>What you can do:</strong> In PJM territory
  your capacity tag is set by usage during the ~5 hottest summer afternoons. If
  you can cut AC use during 2–6 PM on the hottest July/August weekdays — by
  pre-cooling, raising the thermostat, or using a smart thermostat's
  demand-response mode — you lower your PLC and your share of capacity costs for
  the following year. Some utilities run peak-time rebate programs paying
  $1–2/kWh for reducing usage during those hours.</p></div>
</section>

<section>
  <h2>How data centers specifically affect your bill</h2>
  <p>Data centers draw large, constant loads — often 50–300+ MW per campus,
  running 24/7. Here's how that translates into bill impacts for residential
  customers.</p>
  <div style="overflow-x:auto">
  <table>
    <tr><th>Mechanism</th><th>How it works</th><th>Estimated impact</th></tr>
    <tr><td><strong>Capacity market costs</strong></td><td>Load growth forces utilities to procure more generation capacity at auction. Costs are socialized across all ratepayers.</td><td>+$15–21/month in PJM zones (2025/26)</td></tr>
    <tr><td><strong>Transmission upgrades</strong></td><td>New substations, high-voltage lines, and interconnections to serve campuses. Costs are rate-based and recovered from all customers.</td><td>$3–7B planned in Northern Virginia alone</td></tr>
    <tr><td><strong>Rate case increases</strong></td><td>Utilities file rate cases to recover capital invested in serving new large loads. All customers share the revenue requirement.</td><td>Residential rates up 6% nationally in 2025 (2× inflation)</td></tr>
    <tr><td><strong>Reduced reserve margins</strong></td><td>Rapid load growth without matching new generation tightens supply, raising wholesale prices for everyone.</td><td>PJM wholesale prices up 76% (2026 delivery year)</td></tr>
    <tr><td><strong>Stranded asset risk</strong></td><td>If load doesn't materialize as projected, ratepayers may still pay for overbuilt infrastructure.</td><td>Under investigation by multiple PUCs</td></tr>
  </table>
  </div>
  <div class="note warn"><p><strong>The counterargument:</strong>
  Industry-funded studies (notably E3/Amazon, Dec 2025) argue that data centers
  generate surplus utility revenue — paying more than their cost to serve —
  which should benefit other ratepayers. Critics note these studies assume full
  build-out and don't account for the capacity market externalities and
  transmission costs borne by all customers.</p></div>
</section>

<section>
  <h2>Key research: Duke University on load flexibility</h2>
  <p>In February 2025 the Nicholas Institute for Energy, Environment &amp;
  Sustainability at Duke University published a landmark study led by Tyler
  Norris introducing the concept of <em>curtailment-enabled headroom</em>.</p>
  <blockquote>The existing U.S. power grid could accommodate up to 98 GW of new
  large loads — more than all data centers use globally today — if those loads
  agree to curtail usage during just 0.5% of annual hours (about 44 hours a
  year on average, with a maximum of 177 hours in the most constrained
  regions).</blockquote>
  <div class="stats">
    <div class="stat"><b>98 GW</b><span>grid headroom with flexibility — more than global DC demand today</span></div>
    <div class="stat"><b>0.5%</b><span>of annual hours curtailed — ~44 hrs/yr avg, 177 max</span></div>
    <div class="stat"><b>$150B+</b><span>avoided generation and transmission investment</span></div>
  </div>
  <p>If data centers participate in demand response — briefly reducing load
  during the handful of hours each year when the grid is most stressed — the
  need for expensive new peaker plants and transmission disappears. That means
  the capacity costs driving up your bill could be dramatically reduced.</p>
  <p><strong>The catch:</strong> most operators currently refuse curtailment
  because of strict uptime SLAs. The Duke study shows the technical potential is
  there — the barrier is contractual and commercial, not engineering.</p>
  <details class="more"><summary>Study details and methodology</summary>
    <ul>
      <li><strong>Scope:</strong> 22 of the largest U.S. balancing areas (~80% of demand)</li>
      <li><strong>Method:</strong> production cost modelling with incremental load additions and curtailment constraints</li>
      <li><strong>Key innovation:</strong> the curtailment-enabled headroom metric — how much load can be added before reliability standards are violated, at a given curtailment rate</li>
      <li><strong>Result:</strong> at 0.5% curtailment, headroom ranges from 2–15 GW per balancing area, ~98 GW nationally</li>
      <li><strong>Comparison:</strong> existing demand response programs already curtail at comparable rates (FERC Order 2222 resources average 1–3%)</li>
    </ul>
    <p class="src">Norris, T. et al. (2025). "Curtailment-Enabled Headroom: How
    Flexible Large Loads Can Accelerate Grid Integration." Nicholas Institute,
    Duke University.</p>
  </details>
</section>

<section>
  <h2>Why don't data centers voluntarily curtail?</h2>
  <p>If 44 hours a year of curtailment could save $150B in grid costs, why isn't
  it happening? Three barriers — all business and contractual, none technical:
  misaligned incentives, sacred uptime SLAs, and no regulatory mandate.</p>
  <details class="more"><summary>Read more — the three barriers, unpacked</summary>
    <h3>Misaligned incentives</h3>
    <p>When a data center drives up the system peak, the resulting capacity
    charges are spread across all ratepayers — the incremental cost it imposes
    is socialized. There's no price signal saying "your load this hour just cost
    the grid $50M in capacity obligations." And curtailing saves the operator
    nothing on its own bill, since auction prices are set months in advance,
    while every hour of curtailment risks SLA penalties and lost revenue.</p>
    <h3>Uptime SLAs are contractually sacred</h3>
    <p>Cloud contracts guarantee 99.99–99.999% uptime. Voluntary curtailment
    triggers SLA breach penalties (millions per incident), customer churn, and
    liability exposure. The irony: AI training is actually flexible — runs can
    pause and resume — but operators bundle training and inference on shared
    infrastructure and apply the strictest SLA to everything.</p>
    <h3>No regulatory mandate</h3>
    <p>Unlike power plants, data centers have no obligation to participate in
    demand response — they're treated as ordinary load.</p>
  </details>
  <div style="overflow-x:auto">
  <table>
    <tr><th>Missing mechanism</th><th>Why it matters</th></tr>
    <tr><td><strong>Marginal capacity pricing</strong></td><td>Current rates charge average cost, not the marginal cost a new load imposes. If data centers paid the true incremental capacity cost of their peak-hour consumption, curtailment would become profitable overnight.</td></tr>
    <tr><td><strong>Interruptible tariffs with teeth</strong></td><td>Some utilities offer interruptible rates, but participation is voluntary and discounts are too small to offset SLA risk. Making participation mandatory above a load threshold (say 10+ MW) would change the calculus.</td></tr>
    <tr><td><strong>Behind-the-meter flexibility markets</strong></td><td>Data centers could bid flexible workloads (training, batch processing, backups) into demand response markets, earning revenue for curtailment. PJM and ERCOT are exploring this but adoption is minimal.</td></tr>
    <tr><td><strong>Differentiated SLAs for AI training</strong></td><td>Separating training (flexible, delay-tolerant) from inference (latency-critical) would let operators curtail training load without touching customer-facing services.</td></tr>
  </table>
  </div>
  <div class="note bad"><p><strong>The core problem in one sentence:</strong>
  Data centers externalize peak-load costs onto all ratepayers, face no
  regulatory requirement to curtail, and have financial incentives that reward
  consuming as much power as possible at all hours — even when the grid is at
  its breaking point.</p></div>
</section>

<section>
  <h2>Research library</h2>
  <details class="more"><summary>LBNL / DOE — 2024 Data Center Energy Report</summary>
    <p>{_srcref('lbnl')}</p>
    <ul>
      <li>U.S. data center electricity climbed from 58 TWh (2014) to 176 TWh (2023)</li>
      <li>Projected 325–580 TWh by 2028 (6.7–12% of total U.S. electricity)</li>
      <li>Demand growth has tripled over the past decade and is projected to double or triple again by 2028</li>
      <li>In some regions AI-driven demand is outpacing capacity, forcing companies to install inefficient on-site generators</li>
    </ul>
    <p><strong>Reliability incident (Jul 2024):</strong> a voltage fluctuation in
    Northern Virginia triggered simultaneous disconnection of 60 data centers —
    a 1,500 MW surplus requiring emergency grid adjustments to prevent cascading
    outages.</p>
  </details>
  <details class="more"><summary>Harvard Belfer Center — AI, Data Centers, and the U.S. Electric Grid (2026)</summary>
    <p>{_srcref('belfer')}</p>
    <ul>
      <li>Traditional load forecasting is failing — AI demand is growing faster than any historical precedent</li>
      <li>Regional concentration creates localized reliability risks that national statistics obscure</li>
      <li>Recommends mandatory demand response for large loads and reformed interconnection processes</li>
    </ul>
  </details>
  <details class="more"><summary>E3 / Amazon — Tailored for Scale (Dec 2025), the industry counterargument</summary>
    <p>{_srcref('e3_amazon')}</p>
    <ul>
      <li>Studied Amazon facilities across four utility territories (PG&amp;E, Umatilla, Dominion, Entergy)</li>
      <li>Found data centers generate $3.4M surplus revenue per 100 MW facility (2025), rising to $6.1M by 2030</li>
      <li>Concludes data centers are net contributors, not subsidized</li>
    </ul>
    <p><strong>Important context:</strong> the study examines individual
    facilities in isolation and does not model the system-wide capacity market
    and transmission effects PJM's market monitor attributes to data center
    growth. Both findings can be true — a facility can pay more than its direct
    cost-to-serve while still driving up socialized system-wide costs.</p>
  </details>
  <details class="more"><summary>Columbia — Grid-Enhancing Technologies (2025)</summary>
    <p>{_srcref('columbia_get')}</p>
    <ul>
      <li>Dynamic line ratings, power flow controllers, and topology optimization could release 20–40% more capacity from existing transmission without new construction</li>
      <li>Combined with demand response, could ease price pressure through 2030</li>
      <li>Estimated to defer $10–30B in transmission investment nationally</li>
    </ul>
  </details>
  <details class="more"><summary>UC Berkeley Energy Institute — What will data centers do to your electric bill? (2025)</summary>
    <p>{_srcref('ucb_haas')}</p>
    <ul>
      <li>Investor-owned utilities sought $18 billion in rate increases in 2025 — the most since the mid-1980s</li>
      <li>Residential prices rose 6% nominal (2× inflation)</li>
      <li>Capacity market costs are the fastest-growing bill component in RTO markets, with data centers the primary demand driver</li>
      <li>Recommends large loads bear their full marginal cost of service, not just embedded average costs</li>
    </ul>
  </details>
</section>

<section>
  <h2>What can be done? Policy and market solutions</h2>
  <div style="overflow-x:auto">
  <table>
    <tr><th>Solution</th><th>How it helps</th><th>Status</th></tr>
    <tr><td><strong>Mandatory demand response</strong></td><td>Require data centers to curtail during peak hours, reducing the need for new peaker plants</td><td>Proposed in 5+ state legislatures (2026)</td></tr>
    <tr><td><strong>Cost-causation rate design</strong></td><td>Charge large loads for the capacity and transmission they actually cause, rather than socializing costs</td><td>Under review at FERC; several PUCs investigating</td></tr>
    <tr><td><strong>Grid-enhancing technologies</strong></td><td>Squeeze more capacity from existing wires via sensors and software</td><td>Deployed in pockets; DOE pushing broader adoption</td></tr>
    <tr><td><strong>Load flexibility contracts</strong></td><td>Offer lower rates in exchange for contractual curtailment rights</td><td>Duke and Dominion piloting programs</td></tr>
    <tr><td><strong>On-site generation requirements</strong></td><td>Require large loads to provide their own backup/peaking capacity</td><td>Proposed in NC, VA, GA</td></tr>
    <tr><td><strong>Interconnection reform</strong></td><td>Speed up queue processing; require deposits to prevent speculative capacity hoarding</td><td>FERC Order 2023 reforms underway</td></tr>
    <tr><td><strong>Moratoriums &amp; impact fees</strong></td><td>Pause construction until infrastructure catches up; charge fees to fund upgrades</td><td>14+ states with active or proposed moratoriums</td></tr>
  </table>
  </div>
  <div class="note good"><p><strong>The bottom line:</strong> The Duke research
  shows the technical solution exists — brief, modest curtailment can avoid tens
  of billions in new infrastructure costs. The challenge is creating the
  regulatory and commercial frameworks to make data centers participate. Until
  then, residential ratepayers bear the cost of keeping the grid ready for loads
  that refuse to flex.</p></div>
</section>

<section>
  <h2>Sources &amp; further reading</h2>
  <div style="overflow-x:auto">
  <table>
    <tr><th>Source</th><th>Title</th><th>Date</th></tr>
    <tr><td>Duke Nicholas Institute</td><td><a href="https://nicholasinstitute.duke.edu/publications/curtailment-enabled-headroom-how-flexible-large-loads-can-accelerate-decarbonization" rel="nofollow">Curtailment-Enabled Headroom</a></td><td>Feb 2025</td></tr>
    <tr><td>Lawrence Berkeley National Lab</td><td><a href="https://eta.lbl.gov/publications/2024-united-states-data-center-energy" rel="nofollow">2024 U.S. Data Center Energy Usage Report</a></td><td>Jan 2025</td></tr>
    <tr><td>Harvard Belfer Center</td><td><a href="https://www.belfercenter.org/publication/ai-data-centers-and-us-electric-grid" rel="nofollow">AI, Data Centers, and the U.S. Electric Grid</a></td><td>Feb 2026</td></tr>
    <tr><td>E3 / Amazon</td><td><a href="https://www.ethree.com/wp-content/uploads/2025/01/Tailored-for-Scale-Report.pdf" rel="nofollow">Tailored for Scale</a></td><td>Dec 2025</td></tr>
    <tr><td>Columbia University</td><td><a href="https://energypolicy.columbia.edu/publications/grid-enhancing-technologies/" rel="nofollow">Grid-Enhancing Technologies</a></td><td>2025</td></tr>
    <tr><td>UC Berkeley Energy Institute</td><td><a href="https://energyathaas.wordpress.com/2025/09/08/what-will-data-centers-do-to-your-electric-bill/" rel="nofollow">What will data centers do to your electric bill?</a></td><td>Sep 2025</td></tr>
    <tr><td>PJM Interconnection</td><td><a href="https://www.monitoringanalytics.com/reports/Reports/2025.shtml" rel="nofollow">Market Monitor capacity auction reports</a></td><td>2025–2026</td></tr>
    <tr><td>IEEFA</td><td><a href="https://ieefa.org/resources/projected-data-center-growth-spurs-pjm-capacity-prices-factor-10" rel="nofollow">Data center growth spurs PJM capacity prices 10×</a></td><td>2025</td></tr>
    <tr><td>DOE</td><td><a href="https://www.energy.gov/policy/articles/clean-energy-resources-meet-data-center-electricity-demand" rel="nofollow">Clean energy to meet data center demand</a></td><td>2025</td></tr>
    <tr><td>FERC</td><td><a href="https://www.ferc.gov/media/e-1-rm22-14-000" rel="nofollow">Order 2023 — interconnection queue reform</a></td><td>2023</td></tr>
  </table>
  </div>
</section>

<section>
  <h2>Take this to your utility commission</h2>
  <p>Your state PUC decides rate cases — that's where the cost-shift argument on
  this page actually gets made. Your state briefing has its contact details and
  complaint link, and the free toolkit has model CBA clauses for grid-upgrade
  cost allocation and rate caps.</p>
  <p><a class="btn" href="states/index.html">Find your state &rarr;</a>
  <a class="btn ghost" href="{APP_URL}">Open the toolkit</a></p>
</section>
"""
    return page(
        "Why your electric bill is going up: data centers, capacity markets & peak load",
        "How electricity bills work, why peak demand sets your annual cost, and "
        "what the research says about data centers shifting costs onto "
        "residential ratepayers.",
        body, f"{SITE_URL}/bills",
        jsonld=_breadcrumb(("Home", SITE_URL), ("Your bill", f"{SITE_URL}/bills")))


def hbars(rows, unit="", color="var(--teal)"):
    """Horizontal bar chart as plain CSS. rows = [(label, value, note), ...].

    Replaces the Altair charts the Streamlit tabs use. Bars are scaled to the
    largest value in the set, so the eye compares within a chart, never
    across two.
    """
    if not rows:
        return ""
    top = max(v for _, v, _ in rows) or 1
    out = []
    for label, value, note in rows:
        pct = max(2.0, value / top * 100)
        tail = f' <span class="muted">{esc(note)}</span>' if note else ""
        out.append(
            f'<div class="hbar-row">'
            f'<div class="hbar-label">{esc(label)}</div>'
            f'<div class="hbar-track"><div class="hbar-fill" '
            f'style="width:{pct:.1f}%;background:{color}"></div></div>'
            f'<div class="hbar-val">{value:,}{esc(unit)}{tail}</div>'
            f'</div>')
    return f'<div class="hbars">{"".join(out)}</div>'


def build_outlook():
    """Global & US data-center electricity outlook — ported from macro_tab.py.

    The three Altair charts become CSS bars; the Pew section reads from the
    PEW_* registries rather than the numbers that were inlined in the tab.
    """
    iea_rows = [(str(int(r.year)), int(r.twh), "")
                for r in IEA_OUTLOOK.itertuples()]
    fc_rows = [(f"{r.source} · {int(r.year)}", int(r.twh), "")
               for r in DC_FORECASTS.sort_values("twh").itertuples()]
    us_rows = [(r.source, int(r.twh), str(r.note))
               for r in DC_FORECASTS_US.sort_values("twh").itertuples()]

    pew = PEW_RURAL_2026
    pew_rows = "".join(
        f"<tr><td>{esc(r.state)}</td><td>{r.operating:,}</td>"
        f"<td>{r.planned:,}</td><td><strong>{r.total:,}</strong></td></tr>"
        for r in PEW_STATE_COUNTS.sort_values("total", ascending=False)
                                 .itertuples())

    forecasters = " · ".join(
        _srcref(k) for k in ["iea_2025", "bnef", "gartner", "sp_451",
                             "epri_pi", "lbnl", "wri_range"]
        if k in SOURCES)

    body = f"""
<header>
  <div class="kicker">Outlook</div>
  <h1>How much electricity will data centers actually use?</h1>
  <p class="sub">The global and US forecasts, side by side — and why
  credible forecasters disagree by a factor of three.</p>
</header>

<section>
  <h2>Global data-center electricity — the IEA outlook</h2>
  {hbars(iea_rows, unit=" TWh")}
  <div class="stats">
    <div class="stat"><b>415 &rarr; 945 TWh</b><span>2024 to 2030 — roughly Japan's total demand</span></div>
    <div class="stat"><b>~3%</b><span>share of global electricity by 2030</span></div>
    <div class="stat"><b>~1%</b><span>of global CO&#8322; emissions by 2030</span></div>
  </div>
  <ul>
    <li>AI's slice of data-center power is projected to climb from 5–15% recently to <strong>35–50% by 2030</strong>.</li>
    <li><strong>Inference dominates.</strong> It accounts for the majority of a model's lifetime energy — over 90% by some operator accounts. Usage, not training, is the lever.</li>
    <li><strong>Jevons paradox.</strong> Per-query efficiency keeps improving (Gemini fell ~33× in a year), but cheaper inference drives more usage, so total load still rises.</li>
  </ul>
</section>

<section>
  <h2>Forecasts disagree — a lot</h2>
  <p>Third-party projections of <strong>global</strong> data-center electricity
  vary widely by forecaster, year, and scenario. They measure the same thing,
  so they are comparable; the gap between them is honest uncertainty, not
  error.</p>
  {hbars(fc_rows, unit=" TWh", color="var(--teal)")}
  <h3>US only, 2030</h3>
  <p>The spread is the whole point: central estimates run about 2.8× from low
  to high.</p>
  {hbars(us_rows, unit=" TWh", color="var(--amber)")}
  <ul>
    <li><strong>In capacity terms:</strong> BloombergNEF sees US data-center
    power reaching ~106 GW by 2035, up from ~25 GW in 2024 — 8.6% of all US
    electricity, more than double today's 3.5%. {_srcref('bnef_106')}</li>
    <li><strong>Why the spread:</strong> forecasts hinge on how much announced
    pipeline actually gets built and powered — interconnection queues are
    heavily speculative — plus efficiency gains and utilisation assumptions.</li>
  </ul>
  <p class="src">Forecasters: {forecasters}</p>
  <div class="note info"><p>If a developer cites a single forecast at your
  hearing, ask which one and why. There is no consensus number, and the
  choice between 350 TWh and 970 TWh is doing a lot of work in any argument
  about whether the grid can absorb a new campus.</p></div>
</section>

<section>
  <h2>The rural migration</h2>
  <p>Pew Research Center analysed where new US facilities are going
  ({esc(pew['as_of'])}). The finding that matters for community advocacy: the
  build-out has moved to rural counties, most of which have never hosted a
  data center and have no zoning precedent for one.</p>
  <div class="stats">
    <div class="stat"><b>{pew['planned_rural_pct']}%</b><span>of planned facilities are rural — against {pew['operating_rural_pct']}% of those operating today</span></div>
    <div class="stat"><b>{pew['new_counties_pct']}%</b><span>are landing in counties with zero current data centers</span></div>
    <div class="stat"><b>{pew['americans_within_5mi_planned_pct']}%</b><span>of Americans will live within 5 miles of one, up from {pew['americans_within_5mi_now_pct']}%</span></div>
  </div>
  <ul>
    <li><strong>Regional drivers:</strong> the South and Midwest are capturing
    three-quarters of all planned US developments. The South alone accounts for
    {pew['south_share_pct']}% of upcoming sites.</li>
    <li><strong>Growth speed:</strong> planned developments represent a
    {pew['south_growth_pct']}% increase in total facilities for the South and
    {pew['midwest_growth_pct']}% for the Midwest, relative to current counts.</li>
    <li><strong>Tight clusters:</strong> {pew['clustered_within_5mi_pct']}% of
    all operating and planned sites are within 5 miles of another. The first
    approval in a county is rarely the last.</li>
  </ul>
  <details class="more"><summary>Top states by planned &amp; operating facilities</summary>
    <div style="overflow-x:auto">
    <table>
      <tr><th>State</th><th>Operating</th><th>Planned</th><th>Total</th></tr>
      {pew_rows}
    </table>
    </div>
    <p class="src">Pew Research Center, {esc(pew['as_of'])}; facility counts via
    DataCenterMap. Counts, not megawatts — a small network room counts the same
    as a gigawatt campus. {_srcref('pew_rural_2026')}</p>
  </details>
  <div class="note warn"><p><strong>Why this lands on you:</strong> a county
  that has never permitted a data center has no template — no zoning overlay,
  no noise ordinance, no water study, and often no staff who have read one of
  these applications before. That is the gap the toolkit is built for.</p></div>
</section>

<section>
  <h2>What this means where you live</h2>
  <p>National forecasts don't decide anything. Your state's grid, rates, and
  regulator do.</p>
  <p><a class="btn" href="states/index.html">Your state briefing &rarr;</a>
  <a class="btn ghost" href="bills.html">How this reaches your bill</a></p>
</section>
"""
    return page(
        "Data center electricity forecasts: global and US outlook to 2035",
        "IEA, BloombergNEF, LBNL and EPRI projections for data-center "
        "electricity — why they disagree by 3×, and where new US facilities "
        "are actually being built.",
        body, f"{SITE_URL}/outlook",
        jsonld=_breadcrumb(("Home", SITE_URL), ("Outlook", f"{SITE_URL}/outlook")))


def build_learn():
    """Data-center explainer — ported from src/ui/learn_tab.py.

    All prose, metrics, tables, and charts move across; the two Altair bar
    charts become hbars(). The interactive Community Siting Evaluator stays
    in the Streamlit app (needs live geocoding).
    """
    lifecycle_rows = [
        ("1. Data prep", 2, "Moderate"),
        ("2. Training", 10, "HUGE"),
        ("3. Fine-tuning", 3, "Moderate"),
        ("4. Deployment", 1, "Low"),
        ("5. Inference", 7, "Relentless"),
        ("6. Retraining", 10, "HUGE"),
    ]

    pue_rows = [
        ("Older / poorly designed", 1.80, ""),
        ("Industry average (2024)", 1.55, ""),
        ("Good modern facility", 1.20, ""),
        ("Best-in-class (Google/Meta)", 1.10, ""),
    ]

    site_rows = [
        ("1. Power availability", 10, "50–300+ MW of firm electricity"),
        ("2. Fiber connectivity", 8, "Dense fiber with low latency"),
        ("3. Tax incentives", 7, "Abatements, exemptions"),
        ("4. Permitting speed", 7, "Fast zoning & building permits"),
        ("5. Land (cheap & flat)", 6, "50–500 acres, no flood zones"),
        ("6. Water access", 6, "Reliable municipal or well supply"),
        ("7. Disaster safety", 5, "Low quake/hurricane/tornado risk"),
        ("8. Workforce", 4, "Electricians, HVAC, network engineers"),
    ]

    glossary_rows = [
        ("PUE", "Power Usage Effectiveness — ratio of total facility energy to IT energy. Lower is better."),
        ("WUE", "Water Usage Effectiveness — liters of water per kWh of IT energy. Lower is better."),
        ("CFE", "Carbon-Free Energy — electricity from zero-carbon sources (solar, wind, nuclear, hydro)."),
        ("Hyperscaler", "The largest cloud/AI companies that build their own data centers (Google, Microsoft, Amazon, Meta)."),
        ("Colocation (colo)", "A data center operator that leases space, power, and cooling to tenants."),
        ("Interconnection queue", "The list of projects waiting for grid connection approval from the regional operator (e.g., PJM, ERCOT)."),
        ("Moratorium", "A temporary ban or pause on new data-center construction, usually enacted by local or state government."),
        ("PPA", "Power Purchase Agreement — a long-term contract to buy electricity from a specific generator, often renewable."),
        ("Rack density", "The amount of power drawn per server rack, measured in kW. AI racks are 40–120+ kW vs. 5–15 kW traditional."),
        ("GPU", "Graphics Processing Unit — specialized chips (like NVIDIA H100/B200) that power AI training and inference."),
        ("Inference", "Running a trained AI model to generate responses — what happens when you use ChatGPT, Gemini, etc."),
        ("Training", "The initial process of building an AI model by processing massive datasets. Extremely energy-intensive."),
        ("Evaporative cooling", "Cooling method that evaporates water to remove heat. Effective but water-intensive."),
        ("Liquid cooling", "Piping coolant directly to server chips. More efficient for high-density AI workloads."),
        ("Marginal emissions", "The CO₂ rate of the next power plant that would turn on to serve new load. The right signal for load-shifting."),
    ]
    glossary_html = "\n".join(
        f"<tr><td><strong>{esc(term)}</strong></td><td>{esc(defn)}</td></tr>"
        for term, defn in glossary_rows)

    body = f"""
<header>
  <div class="kicker">Learn</div>
  <h1>What is a data center &mdash; and why does it matter?</h1>
  <p class="sub">A plain-language guide to the buildings behind AI: what goes
  in, what comes out, how AI facilities differ from traditional ones, and what
  companies look for when choosing where to build.</p>
</header>

<details class="more"><summary>On this page</summary>
  <ol style="font-size:14px">
    <li>What is a data center?</li>
    <li>How are AI data centers different?</li>
    <li>What happens inside an AI data center</li>
    <li>Using the right model for the task</li>
    <li>Inputs &amp; outputs</li>
    <li>Efficiency (PUE, WUE, CUE)</li>
    <li>Site selection</li>
    <li>Key terms glossary</li>
  </ol>
</details>

<section>
  <h2>1. What is a data center?</h2>
  <p>A <strong>warehouse for computing</strong> &mdash; thousands of servers
  running 24/7 behind every video stream, banking app, and AI chatbot, kept
  alive by dedicated power, cooling, and fiber.</p>
  <div class="stats">
    <div class="stat"><b>~11,000+</b><span>global facilities with 1 MW+ capacity (2025)</span></div>
    <div class="stat"><b>~485 TWh</b><span>global electricity use (2025, IEA) &mdash; ~2% of world total</span></div>
    <div class="stat"><b>~945 TWh</b><span>projected by 2030 &mdash; could double in 5 years</span></div>
  </div>
  <p class="muted">From small server rooms to 300+ MW campuses. Growth is
  driven largely by AI workloads.</p>
  <h3 style="font-size:16px; color:var(--teal); margin:22px 0 4px">How a data center connects to the grid</h3>
  <p class="muted" style="margin-bottom:0">Electricity travels from a power plant across long-distance high-voltage lines, gets stepped down at a substation, then feeds the campus &mdash; often on a dedicated tap.</p>
  {_grid_flow_svg()}
</section>

<section>
  <h2>2. How are AI data centers different?</h2>
  <div class="grid3">
    <div class="card">
      <h3>Power density</h3>
      <p><strong style="color:var(--teal)">40&ndash;120 kW/rack</strong></p>
      <p class="muted">vs 5&ndash;15 kW traditional &mdash; up to 10&times;
      more power in the same space, and far more heat.</p>
    </div>
    <div class="card">
      <h3>Cooling</h3>
      <p><strong style="color:var(--teal)">Liquid-cooled</strong></p>
      <p class="muted">Air can&rsquo;t keep up. Evaporative towers can consume
      millions of gallons a day.</p>
    </div>
    <div class="card">
      <h3>Grid draw</h3>
      <p><strong style="color:var(--teal)">50&ndash;100 MW</strong></p>
      <p class="muted">Per training cluster &mdash; the continuous load of a
      small city.</p>
    </div>
  </div>
  <div class="note info"><p><strong>In one sentence:</strong> a traditional
  data center serves millions of small, quick requests; an AI data center
  runs fewer, far heavier workloads that demand extreme power density and
  advanced cooling.</p></div>
  <details class="more"><summary>Read more &mdash; why the difference matters</summary>
    <p>Traditional data centers run <strong>general workloads</strong> &mdash;
    web hosting, email, databases, video streaming &mdash; on standard CPUs
    drawing moderate power.</p>
    <ul>
      <li><strong>Power density:</strong> AI racks packed with GPUs like
      NVIDIA&rsquo;s H100 or B200 draw <strong>40&ndash;120 kW per rack</strong>
      vs 5&ndash;15 kW for traditional servers. AI facilities need vastly more
      power per square foot and generate far more heat.</li>
      <li><strong>Cooling:</strong> Standard air cooling can&rsquo;t handle GPU
      heat loads, so AI facilities use <strong>liquid cooling</strong> (piping
      coolant to chips) or rear-door heat exchangers. Some rely on evaporative
      cooling towers that consume millions of gallons of water per day.</li>
      <li><strong>Grid impact:</strong> When dozens of 50&ndash;100 MW clusters
      concentrate in one region (Northern Virginia, Central Texas), they strain
      the grid, drive up electricity rates, and require billions in new
      transmission infrastructure.</li>
    </ul>
  </details>
</section>

<section>
  <h2>3. What actually happens inside an AI data center?</h2>
  <p>Two kinds of work with very different power profiles:
  <strong>training</strong> (building the model &mdash; one massive,
  months-long burn) and <strong>inference</strong> (using it &mdash; a smaller
  but endless drip, billions of requests a day).</p>
  <div style="overflow-x:auto">
  <table>
    <tr><th>Attribute</th><th>Training</th><th>Inference</th></tr>
    <tr><td>Duration</td><td>Weeks&ndash;months (one-time)</td><td>Forever (24/7)</td></tr>
    <tr><td>GPU usage</td><td>Thousands in lockstep</td><td>Spread across clusters</td></tr>
    <tr><td>Power profile</td><td>Steady, flat, 24/7</td><td>Spiky, follows the clock</td></tr>
    <tr><td>Total lifetime energy</td><td>~20&ndash;30%</td><td>~70&ndash;80%</td></tr>
  </table>
  </div>
  <div class="note info"><p><strong>Rule of thumb:</strong> <em>Training</em>
  is a one-time, massive, steady burst to build the model. <em>Inference</em>
  is the endless drip of everyday use. Training gets the headlines; inference
  quietly dominates the long-run footprint.</p></div>
  <details class="more"><summary>Read more &mdash; training vs inference, in depth</summary>
    <div class="grid2">
      <div>
        <h3>Training &mdash; <em>building</em> the model</h3>
        <p>Engineers feed enormous datasets &mdash; much of the public internet,
        books, code &mdash; and the model adjusts billions of internal parameters
        until it can predict language well.</p>
        <ul>
          <li><strong>Runs once per model</strong>, but for <strong>weeks or
          months</strong> without stopping.</li>
          <li><strong>Thousands of GPUs in lockstep</strong> &mdash; a 50&ndash;
          100+ MW cluster running flat-out, 24/7.</li>
          <li>A near-constant, city-sized electrical load that&rsquo;s hard for
          a grid to absorb.</li>
          <li>A single frontier model can consume <strong>tens of
          gigawatt-hours</strong> &mdash; as much electricity as thousands of
          homes use in a year.</li>
        </ul>
      </div>
      <div>
        <h3>Inference &mdash; <em>using</em> the model</h3>
        <p>Your prompt goes to a data center, runs through the trained model, and
        a response comes back &mdash; usually in under a second.</p>
        <ul>
          <li><strong>Runs constantly, forever</strong> &mdash; every chat message
          and search summary.</li>
          <li>Each request is small, but there are <strong>billions per
          day</strong> across all users.</li>
          <li>Load is <strong>spiky and follows the clock</strong> &mdash; easier
          to shift toward cleaner grid hours.</li>
          <li>Over a model&rsquo;s lifetime, <strong>inference usually dwarfs
          training</strong> in total energy.</li>
        </ul>
      </div>
    </div>
  </details>

  <h3>The full lifecycle, start to finish</h3>
  {hbars([(s, e, t) for s, e, t in lifecycle_rows],
         unit="/10", color="var(--amber)")}
  <div class="grid3">
    <div class="card"><p><strong>One-time burst:</strong> Training &amp;
    retraining are the biggest single energy draws</p></div>
    <div class="card"><p><strong>Never stops:</strong> Inference runs 24/7 for
    the life of the model</p></div>
    <div class="card"><p><strong>The cycle repeats:</strong> Each new model
    generation starts the process over</p></div>
  </div>
  <p class="muted">This is why AI facilities come in two flavors:
  <strong>training campuses</strong> built for massive, constant power, and
  <strong>inference campuses</strong> placed close to users for low latency.
  Some sites do both.</p>
</section>

<section>
  <h2>4. Using the right model for the task</h2>
  <p>A frontier model can use <strong>10&ndash;100&times; more energy per
  response</strong> than a small one &mdash; and for most everyday tasks, the
  small model answers just as well. Sending every request to the largest model
  is like taking a semi-truck to pick up groceries.</p>
  <div class="note info"><p><strong>The takeaway:</strong> the greenest AI
  request is often the one that never touches a giant model. Right-sizing
  &mdash; the <em>right</em> model, a <em>short</em> prompt, a <em>cached</em>
  answer when possible &mdash; cuts energy dramatically with no visible drop
  in quality.</p></div>
  <details class="more"><summary>How teams right-size in practice</summary>
    <ul>
      <li><strong>Model routing</strong> &mdash; a lightweight system sends easy
      questions to a small model and only escalates hard ones to a large
      model.</li>
      <li><strong>Distillation</strong> &mdash; training a small, cheap model to
      mimic a big one for a specific task, keeping most of the quality at a
      fraction of the cost.</li>
      <li><strong>Caching &amp; retrieval</strong> &mdash; reusing past answers
      or looking facts up in a database instead of re-running the model from
      scratch.</li>
      <li><strong>Shorter prompts &amp; outputs</strong> &mdash; energy scales
      with tokens processed, so concise in-and-out means less compute.</li>
    </ul>
    <p>Small &ldquo;mini&rdquo; models already handle the bulk of real traffic
    &mdash; classification, summarizing, autocomplete, simple Q&amp;A &mdash;
    at a fraction of the energy. Large frontier models shine at hard reasoning
    and complex code, but are overkill for routine requests.</p>
  </details>
</section>

<section>
  <h2>5. Inputs and outputs &mdash; what goes in, what comes out</h2>
  <div class="grid2">
    <div>
      <h3>What goes IN</h3>
      <div class="card" style="margin:8px 0"><p><strong>Electricity</strong> &mdash; 50&ndash;300+ MW</p></div>
      <div class="card" style="margin:8px 0"><p><strong>Water</strong> &mdash; 1&ndash;5M gal/day</p></div>
      <div class="card" style="margin:8px 0"><p><strong>Land</strong> &mdash; 50&ndash;500+ acres</p></div>
      <div class="card" style="margin:8px 0"><p><strong>Fiber</strong> &mdash; Redundant paths</p></div>
      <div class="card" style="margin:8px 0"><p><strong>Hardware</strong> &mdash; Refreshed every 3&ndash;5 yrs</p></div>
    </div>
    <div>
      <h3>What comes OUT</h3>
      <div class="card" style="margin:8px 0"><p><strong>Compute services</strong> &mdash; AI &amp; cloud (the product)</p></div>
      <div class="card" style="margin:8px 0"><p><strong>Waste heat</strong> &mdash; Rarely recaptured in US</p></div>
      <div class="card" style="margin:8px 0"><p><strong>Noise</strong> &mdash; 50&ndash;70+ dB at property line</p></div>
      <div class="card" style="margin:8px 0"><p><strong>CO&#8322; emissions</strong> &mdash; Varies by grid mix</p></div>
      <div class="card" style="margin:8px 0"><p><strong>Jobs</strong> &mdash; 50&ndash;150 permanent</p></div>
      <div class="card" style="margin:8px 0"><p><strong>Tax revenue</strong> &mdash; Often reduced by abatements</p></div>
    </div>
  </div>
</section>

<section>
  <h2>6. How can data centers be more efficient?</h2>
  <p>The industry uses several strategies to reduce energy, water, and carbon
  footprint. Not all operators adopt all of these &mdash; and the gap between
  the best and worst performers is wide.</p>
  <h3>PUE comparison</h3>
  {hbars(pue_rows, unit=" PUE")}
  <p class="muted">Lower is better. Every 0.1 improvement saves ~7&ndash;10%
  total energy. Theoretical perfect PUE is 1.0 (impossible).</p>
  <div class="stats">
    <div class="stat"><b>1.55</b><span>industry avg PUE &mdash; best-in-class: 1.10</span></div>
    <div class="stat"><b>12&ndash;18%</b><span>typical server utilization &mdash; could be 60%+</span></div>
    <div class="stat"><b>30&ndash;50%</b><span>liquid cooling saves this much cooling energy</span></div>
  </div>
  <details class="more"><summary>The six efficiency levers, explained</summary>
    <div class="grid2">
      <div>
        <h3>Power efficiency (PUE)</h3>
        <p>Total facility energy &divide; IT equipment energy. 1.0 = perfect
        (impossible); 1.1&ndash;1.2 = best-in-class (Google, Meta); industry
        average &asymp; 1.55 (Uptime Institute, 2024). Every 0.1 reduction saves
        ~7&ndash;10% of total energy.</p>
        <h3>Liquid cooling</h3>
        <p>Direct-to-chip cooling removes heat far more efficiently than air
        &mdash; 30&ndash;50% less cooling energy, and increasingly required for
        AI GPU racks drawing 60+ kW.</p>
        <h3>Free cooling</h3>
        <p>Cold-climate facilities (Nordics, Pacific Northwest, Ireland) use
        outside air much of the year, drastically cutting water and chiller
        energy.</p>
      </div>
      <div>
        <h3>Renewable energy</h3>
        <p>Leading operators sign PPAs for wind and solar. The gold standard is
        <strong>24/7 Carbon-Free Energy</strong> &mdash; matching consumption
        with clean energy hour-by-hour on the same grid, not just annually
        through credits.</p>
        <h3>Water efficiency (WUE)</h3>
        <p>Liters of water per kWh of IT energy. 0.0 = air-cooled;
        0.2&ndash;0.5 = efficient evaporative; 1.0&ndash;2.0 = heavy use.
        Arid-region facilities are switching to closed-loop chillers that use
        zero water at the cost of more energy.</p>
        <h3>Compute efficiency</h3>
        <p>The cheapest watt is the one you never draw: raise server utilization
        (industry average is just 12&ndash;18%), optimize models (quantization
        and distillation cut inference energy 2&ndash;10&times;), right-size
        hardware, and schedule deferrable jobs into off-peak, high-renewable
        hours.</p>
      </div>
    </div>
  </details>
</section>

<section>
  <h2>7. Where do companies build &mdash; and what do they look for?</h2>
  <p>Site selection is driven by a specific checklist of requirements.
  Understanding what companies prioritize explains why data centers cluster in
  certain regions &mdash; and why some communities are targeted more than
  others.</p>
  <h3>Site-selection factors by importance</h3>
  {hbars(site_rows, unit="/10", color="var(--amber)")}
  <p class="muted">Power is king &mdash; everything else follows. Without
  available grid capacity, no amount of tax incentives matters.</p>
  <div class="note warn"><p><strong>What&rsquo;s often missing from this
  checklist:</strong> community input, cumulative impact on local water and
  power resources, noise standards, and long-term rate impacts on existing
  ratepayers. These are the gaps this tracker aims to make visible.</p></div>
  <div class="note info"><p><strong>Could they build in your town?</strong>
  The <a href="{APP_URL}">full toolkit</a> includes a
  <strong>Community Siting Evaluator</strong> &mdash; enter your town or
  address to see how it scores on these 8 factors, with auto-populated data
  from public sources.</p></div>
</section>

<section>
  <h2>8. Key terms glossary</h2>
  <div style="overflow-x:auto">
  <table>
    <tr><th>Term</th><th>Definition</th></tr>
    {glossary_html}
  </table>
  </div>
</section>

<section>
  <h2>What to do with this</h2>
  <p>Now you know how these facilities work and what makes your community a
  target. Next steps:</p>
  <p>
    <a class="btn" href="{APP_URL}">Start here &mdash; the 5-step wizard</a>
    <a class="btn ghost" href="health-risks.html">The health risks, sourced</a>
    <a class="btn ghost" href="bills.html">How this reaches your bill</a>
  </p>
  <p class="src">Sources: IEA <em>Energy and AI</em> (2025), Uptime Institute
  Global Survey (2024), EPRI <em>Powering Intelligence</em> (2025), Google
  Environmental Report (2024), US DOE Data Center Primer.</p>
</section>
"""
    learn_ld = [
        _breadcrumb(("Home", SITE_URL), ("Learn", f"{SITE_URL}/learn")),
        _faq_schema(glossary_rows),
    ]
    return page(
        "What is a data center? A plain-language guide",
        "What goes in, what comes out, how AI data centers differ from "
        "traditional ones, and what companies look for when choosing "
        "where to build.",
        body, f"{SITE_URL}/learn", jsonld=learn_ld)


def build_puc():
    """State PUC directory — ported from officials_tab.py.

    The 51-commission table is fully static (STATE_PUCS_DF). The page adds
    context on what PUCs do and how to intervene — the kind of explainer
    content that belongs on the static site, not in the app.
    """
    n = len(STATE_PUCS_DF)

    def _puc_complaint(v):
        if has_value(v):
            return f'<a href="{esc(v)}">file complaint</a>'
        return "—"

    rows = "\n".join(
        f"<tr><td>{esc(r['state'])}</td><td>{esc(r['abbrev'])}</td>"
        f"<td>{esc(r['name'])}</td>"
        f'<td><a href="{esc(r["website"])}">website</a></td>'
        f"<td>{_puc_complaint(r['complaint'])}</td>"
        f"</tr>"
        for _, r in STATE_PUCS_DF.iterrows())

    body = f"""
<header>
  <div class="kicker">Directory</div>
  <h1>Every state Public Utility Commission (PUC)</h1>
  <p class="sub">PUCs approve rate cases, large-load tariffs, and
  interconnection rules &mdash; they decide whether data center costs land on
  residential bills. Every state has one. File a complaint or intervene in a
  rate case to make your voice heard.</p>
</header>

{provenance_html("STATE_PUCS_DF")}

<section>
  <h2>What a PUC does &mdash; and why it matters to you</h2>
  <div class="grid3">
    <div class="card">
      <h3>Rate cases</h3>
      <p class="muted">When a utility wants to raise rates &mdash; often to pay
      for grid upgrades driven by data center load &mdash; it files a rate case
      with the PUC. You can intervene.</p>
    </div>
    <div class="card">
      <h3>Large-load tariffs</h3>
      <p class="muted">PUCs set the rules for how large industrial customers
      like data centers connect to and pay for the grid. Custom tariffs can
      shift costs to residential ratepayers.</p>
    </div>
    <div class="card">
      <h3>Consumer complaints</h3>
      <p class="muted">Filing a complaint puts your concerns on the public
      record. PUCs are required to respond, and pattern complaints can trigger
      investigations.</p>
    </div>
  </div>
  <div class="note info"><p><strong>How to use this:</strong> When a data center
  developer applies for a large-load interconnection or a utility files a rate
  case to recover grid upgrade costs, you can intervene at your PUC. Filing a
  consumer complaint puts your concerns on the record. See
  <a href="bills.html">Your bill</a> for how wholesale costs flow to your
  bill.</p></div>
</section>

<section>
  <h2>All {n} commissions</h2>
  <input type="text" id="puc-search" placeholder="Search by state name..."
         autocomplete="off"
         style="width:100%;max-width:400px;background:var(--card);color:var(--ink);
         border:1px solid var(--rule);border-radius:10px;padding:10px 14px;
         font-size:15px;margin-bottom:14px">
  <div style="overflow-x:auto">
  <table id="puc-table">
    <tr><th>State</th><th>Abbrev</th><th>Commission</th><th>Website</th>
    <th>File complaint</th></tr>
    {rows}
  </table>
  </div>
  <p class="muted" id="puc-count">{n} commissions</p>
  <p class="muted">URLs are official state PUC pages. Complaint links open the
  consumer-assistance or formal-complaint portal &mdash; procedures vary by
  state. Nebraska (public power state) has a Power Review Board with no
  separate consumer-complaint portal. Texas (PUCT) has deregulated retail but
  still regulates transmission and distribution rates.</p>
</section>

<section>
  <h2>What to do next</h2>
  <p>
    <a class="btn" href="{APP_URL}">Open the toolkit &mdash; meeting prep &amp; CBA templates</a>
    <a class="btn ghost" href="bills.html">How data center costs reach your bill</a>
    <a class="btn ghost" href="states/index.html">Your state briefing</a>
  </p>
</section>

<script>
(function() {{
  var q = document.getElementById('puc-search');
  var table = document.getElementById('puc-table');
  var ct = document.getElementById('puc-count');
  var rows = Array.from(table.querySelectorAll('tr')).slice(1);
  q.addEventListener('input', function() {{
    var s = q.value.toLowerCase();
    var n = 0;
    rows.forEach(function(r) {{
      var show = !s || r.textContent.toLowerCase().indexOf(s) >= 0;
      r.style.display = show ? '' : 'none';
      if (show) n++;
    }});
    ct.textContent = n + ' commission' + (n === 1 ? '' : 's');
  }});
}})();
</script>
"""
    return page(
        "State PUC directory — every Public Utility Commission",
        "All 51 state Public Utility Commissions with official websites "
        "and complaint portals. File a complaint or intervene when data "
        "center costs hit your electric bill.",
        body, f"{SITE_URL}/puc",
        jsonld=_breadcrumb(("Home", SITE_URL), ("PUC directory", f"{SITE_URL}/puc")))


def build_executives():
    """Executives directory + megaprojects — ported from dc_tab.py.

    Both tables are pure constants data. The executives table includes
    verification status from EXEC_VERIFIED. Megaprojects is the top-10
    leaderboard.
    """
    n_exec = len(EXECUTIVES_DF)
    n_companies = EXECUTIVES_DF["company"].nunique()
    n_verified = int(EXECUTIVES_DF["verified"].apply(
        lambda v: has_value(v)).sum())
    n_mega = len(MEGA_PROJECTS_DF)

    cat_labels = {"leadership": "Leadership", "infrastructure": "Infrastructure",
                  "sustainability": "Sustainability", "policy": "Policy"}

    def _link_or_dash(url, text):
        if has_value(url):
            return f'<a href="{esc(url)}">{text}</a>'
        return "—"

    def _exec_row(r):
        status = ("&#9989; " + esc(str(r["verified"]))
                  if has_value(r["verified"]) else "&#9888;&#65039; Unverified")
        return (f"<tr><td>{esc(r['company'])}</td><td>{esc(r['name'])}</td>"
                f"<td>{esc(r['title'])}</td>"
                f"<td>{esc(cat_labels.get(r['category'], r['category']))}</td>"
                f"<td>{status}</td>"
                f"<td>{_link_or_dash(r['verified_source'], 'source')}</td>"
                f"<td>{_link_or_dash(r['linkedin'], 'search')}</td>"
                f"</tr>")

    exec_rows = "\n".join(_exec_row(r) for _, r in EXECUTIVES_DF.iterrows())

    mega_rows = "\n".join(
        f"<tr><td>{esc(r.project)}</td><td>{esc(r.company)}</td>"
        f"<td>{esc(r.location)}</td><td>{esc(r.invest)}</td>"
        f"<td>{esc(r.capacity)}</td><td>{esc(r.status)}</td></tr>"
        for r in MEGA_PROJECTS_DF.itertuples())

    # Operators table
    tier_labels = {"hyperscaler": "Hyperscaler", "ai": "AI / neocloud",
                   "colo": "Colocation / wholesale REIT"}
    op_rows = "\n".join(
        f"<tr><td>{esc(r.operator)}</td><td>{esc(tier_labels.get(r.tier, r.tier))}</td>"
        f"<td>{esc(str(r.owner))}</td><td>{esc(r.model)}</td>"
        f"<td>{cell(r.filing_llc)}</td></tr>"
        for r in OPERATORS_DF.itertuples())

    body = f"""
<header>
  <div class="kicker">Directory</div>
  <h1>Data center operators, executives &amp; megaprojects</h1>
  <p class="sub">Who builds them, who runs them, and the biggest projects under
  construction &mdash; the people and companies behind the campuses in your
  community.</p>
</header>

<section>
  <h2>Operators &amp; owners</h2>
  <p>A campus has up to three separate parties &mdash; the operator (who runs
  it), the owner (often a PE fund), and the tenant (who actually consumes the
  power). Land is bought through single-purpose <strong>shell LLCs</strong>,
  the join key back to county deed records.</p>
  <div style="overflow-x:auto">
  <table>
    <tr><th>Operator</th><th>Category</th><th>Owner / PE parent</th>
    <th>Model</th><th>Filing LLCs</th></tr>
    {op_rows}
  </table>
  </div>
  <p class="muted">Resolving a shell LLC &rarr; operator: county assessor / GIS
  parcel &rarr; grantee LLC on the deed &rarr; state Secretary-of-State business
  database &rarr; registered agent &amp; principals.</p>
</section>

<section>
  <h2>Key executives</h2>
  <p>CEO and data-center leadership at every tracked operator and mega-project
  sponsor. {n_exec} executives across {n_companies} companies &mdash;
  <strong>{n_verified} verified</strong> against the company&rsquo;s own
  leadership page, <strong>{n_exec - n_verified} unverified</strong>.</p>
  {provenance_html("EXECUTIVES_DF")}
  <input type="text" id="exec-search" placeholder="Search by name or company..."
         autocomplete="off"
         style="width:100%;max-width:400px;background:var(--card);color:var(--ink);
         border:1px solid var(--rule);border-radius:10px;padding:10px 14px;
         font-size:15px;margin-bottom:14px">
  <div style="overflow-x:auto">
  <table id="exec-table">
    <tr><th>Company</th><th>Name</th><th>Title</th><th>Category</th>
    <th>Status</th><th>Checked against</th><th>LinkedIn</th></tr>
    {exec_rows}
  </table>
  </div>
  <p class="muted" id="exec-count">{n_exec} executives</p>
  <div class="note warn"><p>Unverified rows are mostly VP- and director-level
  people who appear on no public leadership page; treat their titles as a lead
  to confirm, not a fact. LinkedIn links are search URLs &mdash; check the
  profile matches before connecting.</p></div>
</section>

<section>
  <h2>Megaprojects under construction</h2>
  <p>Top {n_mega} individual megaprojects ranked by announced investment &mdash;
  hundreds of billions in committed capital and tens of GW of new AI compute
  capacity.</p>
  {provenance_html("MEGA_PROJECTS_DF")}
  <div style="overflow-x:auto">
  <table>
    <tr><th>Project</th><th>Company</th><th>Location</th><th>Investment</th>
    <th>Power capacity</th><th>Status</th></tr>
    {mega_rows}
  </table>
  </div>
</section>

<section>
  <h2>What to do with this</h2>
  <p>Know who you&rsquo;re negotiating with. These are the decision-makers and
  the projects driving the build-out.</p>
  <p>
    <a class="btn" href="{APP_URL}">Open the toolkit &mdash; meeting prep generator</a>
    <a class="btn ghost" href="companies/index.html">Company environmental scorecards</a>
    <a class="btn ghost" href="moratoriums.html">Moratorium tracker</a>
  </p>
</section>

<script>
(function() {{
  var q = document.getElementById('exec-search');
  var table = document.getElementById('exec-table');
  var ct = document.getElementById('exec-count');
  var rows = Array.from(table.querySelectorAll('tr')).slice(1);
  q.addEventListener('input', function() {{
    var s = q.value.toLowerCase();
    var n = 0;
    rows.forEach(function(r) {{
      var show = !s || r.textContent.toLowerCase().indexOf(s) >= 0;
      r.style.display = show ? '' : 'none';
      if (show) n++;
    }});
    ct.textContent = n + ' executive' + (n === 1 ? '' : 's');
  }});
}})();
</script>
"""
    return page(
        "Data center operators, executives & megaprojects",
        "Who builds, owns, and runs US data centers — operator registry, "
        "executive directory with verification status, and the largest "
        "projects under construction.",
        body, f"{SITE_URL}/executives",
        jsonld=_breadcrumb(("Home", SITE_URL), ("Executives", f"{SITE_URL}/executives")))


def build_moratoriums():
    total = len(MORATORIUMS_DF)
    n_states = MORATORIUMS_DF["state"].nunique()
    # "In force" counts effective status, so an expired term stops inflating
    # the headline number the day it lapses.
    enacted = len(MORATORIUMS_DF[MORATORIUMS_DF["effective_status"] == "Enacted"])
    proposed = len(MORATORIUMS_DF[MORATORIUMS_DF["effective_status"] == "Proposed"])
    verified = int(MORATORIUMS_DF["verified"].sum())

    rows = "\n".join(
        f"<tr><td>{esc(str(m.locality))}</td>"
        f"<td><a href=\"states/{slugify(STATE_PUCS_DF[STATE_PUCS_DF['abbrev'] == m.state].iloc[0]['state'])}.html\">"
        f"{esc(str(m.state))}</a></td>"
        f"<td>{esc(str(m.level))}</td>"
        f"<td>{_mora_status_cell(m)}</td>"
        f"<td>{esc(str(m.when))}</td>"
        f"<td>{cell(m.note, dash='')}</td>"
        f"<td>{_mora_source_cell(m)}</td></tr>"
        for m in MORATORIUMS_DF.itertuples())

    outcomes = "\n".join(_outcome_card(o) for o in MORATORIUM_OUTCOMES)
    schema_rows = "\n".join(
        f"<tr><td><code>{esc(c)}</code></td><td>{esc(d)}</td></tr>"
        for c, d in MORATORIUM_SCHEMA)

    # Deadlines go above the table. A 900-row table is reference material;
    # "this lapses in three days" is the thing someone needs to act on, and
    # burying it under everything else is how it gets missed.
    _alerts = build_alerts()
    alerts_html = ""
    if _alerts:
        items = "\n".join(
            f'<li><strong>{esc(a["title"])}</strong><br>'
            f'<span class="muted">{esc(a["body"])}</span></li>'
            for a in _alerts)
        alerts_html = f"""
<section>
  <h2>Deadlines in the next {ALERT_LOOKAHEAD} days</h2>
  <p class="muted" style="margin-bottom:12px">Derived from documented end
  dates. Moratoriums are routinely extended, so treat these as the earliest a
  pause could end — a prompt to call the clerk, not a conclusion.
  <a href="alerts.xml">Subscribe by RSS</a> ·
  <a href="data/alerts.json">JSON</a></p>
  <ul>{items}</ul>
</section>"""

    body = f"""
<header>
  <div class="kicker">Community tracker</div>
  <h1>Data center moratoriums &amp; pushback</h1>
  <p class="sub">Every community that pressed pause on data center
  development — bans, moratoria, zoning fights, and the outcomes. Each row
  shows where it came from and when it was last checked.</p>
</header>
<div class="stats">
  <div class="stat"><b>{total}</b><span>tracked actions</span></div>
  <div class="stat"><b>{n_states}</b><span>states</span></div>
  <div class="stat"><b>{enacted}</b><span>in force today</span></div>
  <div class="stat"><b>{proposed}</b><span>proposed or pending</span></div>
  <div class="stat"><b>{verified}/{total}</b><span>source-verified</span></div>
</div>
{alerts_html}
<section>
  <h2>All tracked moratoriums</h2>
  <p class="muted" style="margin-bottom:12px">Status is what applies
  <em>today</em>: a moratorium with a documented end date flips to
  <span class="badge badge-expired">Expired</span> on its own once that date
  passes. Rows marked <span class="unverified">Unverified</span> have not been
  read against a primary source — treat them as a lead to check, not a fact to
  cite. Extensions are common, so an expiry date is the earliest a pause could
  have ended, not proof that it did.</p>
  <div style="overflow-x:auto">
  <table><tr><th>Locality</th><th>State</th><th>Level</th>
  <th>Status</th><th>When</th><th>Note</th><th>Source</th></tr>
  {rows}</table>
  </div>
  {provenance_html("MORATORIUMS_DF")}
  <p class="muted" style="margin-top:10px">See the full interactive map and
  filters in the <a href="{APP_URL}">GridWatch toolkit</a>.</p>
</section>
<section id="data">
  <h2>Use this data</h2>
  <p>The whole tracker, with per-row sources, verification dates and derived
  expiry, as a documented download. Free to reuse with attribution
  (<a href="{DATA_LICENSE_URL}" rel="license noopener">{DATA_LICENSE}</a>) —
  cite it, chart it, or load it into your own tracker.</p>
  <p><a class="btn" href="data/moratoriums.json">moratoriums.json</a>
     <a class="btn ghost" href="data/moratoriums.csv">moratoriums.csv</a></p>
  <details class="more">
    <summary>Schema — {len(MORATORIUM_SCHEMA)} fields</summary>
    <div style="overflow-x:auto">
    <table><tr><th>Field</th><th>Meaning</th></tr>
    {schema_rows}</table>
    </div>
    <p class="muted" style="margin-top:10px">Read <code>effective_status</code>,
    not <code>status</code>: a moratorium whose documented term has run out
    reads <em>Expired</em> there, and that is the field the page itself
    renders. Rows with <code>verified: false</code> have no source on record —
    they are leads to check, not facts to cite.</p>
  </details>
  <details class="more">
    <summary>Embed the tracker on your own site</summary>
    <p class="muted">Self-contained and filterable by state. It updates when
    this page does, so you are not maintaining a copy.</p>
    <pre style="overflow-x:auto"><code>&lt;iframe src="{SITE_URL}/embed/moratoriums.html"
        width="100%" height="560" style="border:0"
        title="Data center moratorium tracker"&gt;&lt;/iframe&gt;</code></pre>
    <p><a href="embed/moratoriums.html" target="_blank" rel="noopener">Preview it &rarr;</a></p>
  </details>
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
        body, f"{SITE_URL}/moratoriums",
        jsonld=_breadcrumb(("Home", SITE_URL), ("Moratoriums", f"{SITE_URL}/moratoriums")))


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
        body, f"{SITE_URL}/companies/", depth=1,
        jsonld=_breadcrumb(("Home", SITE_URL), ("Companies", f"{SITE_URL}/companies/")))


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
            f'<td>{esc(c["what"])}{_prov_links(c)}</td></tr>'
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
        body, f"{SITE_URL}/companies/{h['slug']}", depth=1,
        jsonld=_breadcrumb(("Home", SITE_URL), ("Companies", f"{SITE_URL}/companies/"), (h["name"], f"{SITE_URL}/companies/{h['slug']}")))


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
        body, f"{SITE_URL}/companies/{h['slug']}", depth=1,
        jsonld=_breadcrumb(("Home", SITE_URL), ("Companies", f"{SITE_URL}/companies/"), (h["name"], f"{SITE_URL}/companies/{h['slug']}")))


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
        body, f"{SITE_URL}/companies/{ld['slug']}", depth=1,
        jsonld=_breadcrumb(("Home", SITE_URL), ("Companies", f"{SITE_URL}/companies/"), (ld["name"], f"{SITE_URL}/companies/{ld['slug']}")))


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


def build_data_centers():
    """Data center market page — state profiles, operators, ERCOT queue, SEC
    10-K competitor analysis, demand wave, and grid-operator responses.
    """
    nat = STATE_DC_NATIONAL
    n_states = len(STATE_DC_DF)

    # -- Section 1: state facility table & top-15 bar chart ----------------
    top15 = STATE_DC_DF.nlargest(15, "twh_year")
    state_bars = hbars(
        [(r["state"], r["twh_year"], f'{r["dc_count"]} facilities')
         for _, r in top15.iterrows()],
        unit=" TWh")

    def _upcoming_mark(v):
        return "&#10003;" if v else "&mdash;"

    state_rows = "\n".join(
        f"<tr><td>{esc(r['state'])}</td><td>{esc(r['abbrev'])}</td>"
        f"<td>{r['dc_count']}</td><td>{r['twh_year']}</td>"
        f"<td>{esc(r['major_hubs'])}</td>"
        f"<td style=\"text-align:center\">{_upcoming_mark(r['upcoming'])}</td></tr>"
        for _, r in STATE_DC_DF.iterrows())

    # -- Section 2: operators table ----------------------------------------
    tier_labels = {"hyperscaler": "Hyperscaler (owns &amp; consumes)",
                   "ai": "AI / neocloud",
                   "colo": "Colocation / wholesale REIT"}

    def _tier_label(t):
        return tier_labels.get(t, esc(str(t)))

    op_rows = "\n".join(
        f"<tr><td>{esc(r['operator'])}</td>"
        f"<td>{_tier_label(r['tier'])}</td>"
        f"<td>{cell(r['owner'])}</td>"
        f"<td>{esc(r['model'])}</td>"
        f"<td>{cell(r['discloses_tenant'])}</td>"
        f"<td>{cell(r['filing_llc'])}</td></tr>"
        for _, r in OPERATORS_DF.iterrows())

    # -- Section 3: ERCOT funnel -------------------------------------------
    requested = ERCOT_LL_FUNNEL[0][1]
    live_mw = ERCOT_LL_FUNNEL[2][1]
    dc_gw = requested * ERCOT_LL_DC_SHARE / 1000

    ercot_bars = hbars(
        [(stage, mw, "") for stage, mw, _, _ in ERCOT_LL_FUNNEL],
        unit=" MW")

    ercot_bullets = "\n".join(
        f"<li><strong>{esc(stage)}</strong> ({mw:,} MW) &mdash; "
        f"{esc(blurb)} {_srcref(src)}</li>"
        for stage, mw, blurb, src in ERCOT_LL_FUNNEL)

    # -- Section 4: SEC 10-K competitor table ------------------------------
    def _names_yn(v):
        return "Yes" if v else "No"

    sec_rows = "\n".join(
        f"<tr><td>{esc(r['filer'])}</td>"
        f"<td>{_names_yn(r['names'])}</td>"
        f"<td style=\"font-size:13px;font-style:italic\">{esc(r['quote'])}</td>"
        f"<td>{cell(r['named'])}</td>"
        f"<td>{esc(r['rivals'])}</td></tr>"
        for _, r in AI_COMPETITORS_DF.iterrows())

    body = f"""
<header>
  <div class="kicker">Market data</div>
  <h1>U.S. data center market: state profiles, operators &amp; grid queue</h1>
  <p class="sub">All 50 states and D.C. &mdash; facility counts, power draw,
  operator ownership, the ERCOT large-load funnel, SEC filings, and how the
  grid is responding to the demand wave.</p>
</header>

<details class="more"><summary>On this page</summary>
  <ol style="font-size:14px">
    <li>All 50 states: facility count &amp; power draw</li>
    <li>Owners, operators &amp; shell LLCs</li>
    <li>ERCOT large-load interconnection queue</li>
    <li>SEC 10-K competitor analysis</li>
    <li>The demand wave &mdash; ERCOT &amp; PJM</li>
    <li>How the grid operators &amp; FERC are responding</li>
  </ol>
</details>

<section>
  <h2>All {n_states} states: data center facility count &amp; power draw</h2>
  <div class="stats">
    <div class="stat"><b>{nat['active_facilities']:,}</b><span>active facilities</span></div>
    <div class="stat"><b>{nat['twh_annual']} TWh/yr</b><span>{nat['pct_us_power']}% of U.S. power</span></div>
    <div class="stat"><b>~{nat['under_construction']:,}</b><span>under construction</span></div>
    <div class="stat"><b>~{nat['homes_equivalent_millions']}M</b><span>homes-equivalent</span></div>
  </div>

  <input type="text" id="dc-search" placeholder="Search by state or hub..."
         autocomplete="off"
         style="width:100%;max-width:400px;background:var(--card);color:var(--ink);
         border:1px solid var(--rule);border-radius:10px;padding:10px 14px;
         font-size:15px;margin-bottom:14px">
  <div style="overflow-x:auto">
  <table id="dc-table">
    <tr><th>State</th><th>Abbrev</th><th>Facilities</th><th>TWh/yr</th>
    <th>Major hubs</th><th>Upcoming</th></tr>
    {state_rows}
  </table>
  </div>
  <p class="muted" id="dc-count">{n_states} states</p>

  <h3 style="margin-top:24px">Top 15 states by annual power draw</h3>
  {state_bars}

  {provenance_html("STATE_DC_DF")}
  <p class="src">Sources: {_srcref('electricchoice')} &middot; {_srcref('lbnl')}</p>
</section>

<section>
  <h2>Owners, operators &amp; shell LLCs</h2>
  <p>A campus has up to three separate parties &mdash; the <strong>operator</strong>
  (who runs it), the <strong>owner</strong> (often a PE fund), and the
  <strong>tenant</strong> (who actually consumes the power). Land is bought
  through single-purpose <strong>shell LLCs</strong>, the join key back to
  county deed records.</p>
  <div style="overflow-x:auto">
  <table>
    <tr><th>Operator</th><th>Category</th><th>Owner / PE parent</th>
    <th>Model</th><th>Tenant disclosed</th><th>Filing LLCs</th></tr>
    {op_rows}
  </table>
  </div>
  {provenance_html("DC_SITES_DF")}
  <div class="note info"><p><strong>LLC resolution:</strong> county assessor /
  GIS parcel &rarr; grantee LLC on the deed &rarr; state Secretary-of-State
  business database &rarr; registered agent &amp; principals.</p></div>
  <p class="src">Sources: {_srcref('dc_ownership')} &middot;
  {_srcref('vantage_dbsl')} &middot; {_srcref('switch_dbif')} &middot;
  {_srcref('crwv_coresci')}</p>
</section>

<section>
  <h2>ERCOT large-load interconnection queue</h2>
  <p>ERCOT is the only ISO that publishes an aggregate large-load (not
  generation) interconnection picture and breaks out the data-center share.
  The story is the <strong>funnel</strong>: what&rsquo;s requested dwarfs
  what&rsquo;s approved, which dwarfs what&rsquo;s actually running.
  Data as of {esc(ERCOT_LL_VINTAGE)}.</p>
  <div class="stats">
    <div class="stat"><b>{requested / 1000:.0f} GW</b>
      <span>large load requested (~{ERCOT_LL_DC_SHARE * 100:.0f}% data centers)</span></div>
    <div class="stat"><b>{dc_gw:.0f} GW</b>
      <span>large-load DC share</span></div>
    <div class="stat"><b>{live_mw / 1000:.1f} GW</b>
      <span>actually running today ({live_mw / requested * 100:.1f}% of requested)</span></div>
  </div>

  {ercot_bars}
  <ul>
    {ercot_bullets}
  </ul>
  <div class="note warn"><p>The bar chart uses a linear scale; the
  &ldquo;seeking interconnection&rdquo; bar dwarfs the others because most of
  that capacity is speculative. Many projects never energize.</p></div>
  <p class="src">Sources: {_srcref('ercot_ll_bc')} &middot;
  {_srcref('ercot_ll_tac')} &middot; {_srcref('ercot_ll')}</p>
</section>

<section>
  <h2>SEC 10-K competitor analysis</h2>
  <p>What the six largest cloud / AI filers tell the SEC about who they compete
  with &mdash; a useful cross-reference of how these companies see each
  other.</p>
  <div style="overflow-x:auto">
  <table>
    <tr><th>Filer</th><th>Names rivals?</th><th>10-K language</th>
    <th>Named</th><th>Editorial cross-ref</th></tr>
    {sec_rows}
  </table>
  </div>
  <p class="src">Sources: {_srcref('goog_10k')} &middot; {_srcref('meta_10k')}
  &middot; {_srcref('msft_10k')} &middot; {_srcref('amzn_10k')} &middot;
  {_srcref('orcl_10k')} &middot; {_srcref('crwv_10k')}</p>
</section>

<div class="note info"><p><strong>EIA pilot survey:</strong> In March 2026 the
EIA launched its first-ever pilot survey of energy use at data centers &mdash;
the federal government&rsquo;s first attempt to measure an industry that
currently self-reports nothing.
{_srcref('eia_pilot')} &middot; {_srcref('eia930')}</p></div>

<section>
  <h2>The demand wave &mdash; ERCOT &amp; PJM</h2>
  <p>The two ISOs with the most data-center load growth tell opposite stories
  about how fast the grid can absorb it.</p>
  <div class="stats">
    <div class="stat"><b>~233 GW</b><span>ERCOT queue (72.9% DCs)</span></div>
    <div class="stat"><b>+32 GW</b><span>PJM peak-load growth (94% DCs)</span></div>
    <div class="stat"><b>23.9 GW</b><span>Dominion zone (+23% vs 2019)</span></div>
  </div>
  <div class="note info"><p><strong>ERCOT</strong> has ~233 GW of large-load
  interconnection requests, 72.9% data centers. Only a fraction will energize
  &mdash; see the funnel above.</p>
  <p><strong>PJM</strong> projects +32 GW of peak-load growth over the next
  decade, 94% from data centers. Dominion Energy Virginia&rsquo;s zone alone
  shows 23.9 GW of load, up 23% from 2019.</p></div>
  <p class="src">Sources: {_srcref('ercot_ll')} &middot; {_srcref('pjm_lf')}
  &middot; {_srcref('eia_va')}</p>
</section>

<section>
  <h2>How the grid operators &amp; FERC are responding</h2>
  <div class="stats">
    <div class="stat"><b>3 RTOs</b><span>FERC orders (PJM + MISO + SPP)</span></div>
    <div class="stat"><b>~$16.4B</b><span>PJM capacity auction (record)</span></div>
    <div class="stat"><b>$50k/MW</b><span>Texas SB 6 interconnection fee</span></div>
  </div>
  <div class="note info"><p>The through-line: <strong>co-location</strong>
  (data centers siting next to power plants to bypass grid queues) and
  <strong>cost allocation</strong> (who pays for the transmission upgrades
  these loads require).</p></div>

  <details class="more"><summary>FERC, PJM, ERCOT, MISO &amp; SPP &mdash;
  what each is doing</summary>

  <h3>FERC</h3>
  <p>In December 2025 FERC directed PJM to write co-location rules for data
  centers siting next to power plants. In June 2026 FERC issued show-cause
  orders to MISO, SPP, and other RTOs requiring them to adopt large-load
  interconnection standards. {_srcref('ferc_pjm_colo')} &middot;
  {_srcref('ferc_showcause')}</p>

  <h3>PJM</h3>
  <p>The 2025 capacity auction cleared at record prices (~$16.4B total across
  13 states), driven in large part by data-center load growth. PJM is
  developing new co-location rules per FERC&rsquo;s order.
  {_srcref('pjm_auction25')}</p>

  <h3>ERCOT / Texas SB 6</h3>
  <p>Texas SB 6 (signed 2025) authorizes ERCOT to curtail or disconnect large
  loads (&ge;75 MW) in emergencies, establishes new interconnection standards,
  and imposes a $50,000/MW fee on new large-load interconnections.
  {_srcref('tx_sb6_ll')} &middot; {_srcref('tx_sb6')}</p>

  <h3>MISO</h3>
  <p>MISO launched its Large Load Interconnection Reliability (LLIR) process,
  requiring 90-day reliability studies for loads &ge;100 MW before
  interconnection.
  {_srcref('miso_llir')}</p>

  <h3>SPP</h3>
  <p>SPP adopted its High Impact Large Load (HILL) 90-day study process for
  loads that would materially change system conditions.
  {_srcref('spp_hill')}</p>
  </details>
</section>

<section>
  <h2>What to do with this</h2>
  <p>Use the state data to benchmark your community, the operator table to
  identify who you&rsquo;re negotiating with, and the queue data to gauge
  how much more is coming.</p>
  <p>
    <a class="btn" href="{APP_URL}">Open the toolkit &mdash; meeting prep &amp; CBA templates</a>
    <a class="btn ghost" href="states/index.html">Your state briefing</a>
    <a class="btn ghost" href="executives.html">Executives &amp; megaprojects</a>
  </p>
</section>

<script>
(function() {{
  var q = document.getElementById('dc-search');
  var table = document.getElementById('dc-table');
  var ct = document.getElementById('dc-count');
  var rows = Array.from(table.querySelectorAll('tr')).slice(1);
  q.addEventListener('input', function() {{
    var s = q.value.toLowerCase();
    var n = 0;
    rows.forEach(function(r) {{
      var show = !s || r.textContent.toLowerCase().indexOf(s) >= 0;
      r.style.display = show ? '' : 'none';
      if (show) n++;
    }});
    ct.textContent = n + ' state' + (n === 1 ? '' : 's');
  }});
}})();
</script>
"""
    return page(
        "Data center market — AI GridWatch",
        "U.S. data center market by state — facility counts, power draw, "
        "operator ownership, ERCOT large-load queue, SEC 10-K filings, "
        "and grid-operator responses.",
        body, f"{SITE_URL}/data-centers",
        jsonld=_breadcrumb(("Home", SITE_URL),
                           ("Data centers", f"{SITE_URL}/data-centers")))


def build_environment():
    """Hyperscaler environmental data page — comparison, spend estimator,
    and per-company deep-dives ported from src/ui/corporate_tab.py.

    All Altair charts become CSS hbars() and HTML tables; sliders become
    static calculations with default assumptions.
    """

    g = GOOGLE_2025_HEADLINE
    m = META_2024_HEADLINE
    ms = MICROSOFT_ENV_HEADLINE
    aw = AWS_ENV_HEADLINE

    # ---- helpers for this page ------------------------------------------ #

    def _trend_table(headers, rows):
        """Render a simple HTML table with header row and data rows."""
        hdr = "".join(f"<th>{esc(h)}</th>" for h in headers)
        body_rows = "".join(f"<tr>{''.join(f'<td>{c}</td>' for c in r)}</tr>"
                           for r in rows)
        return (f'<div style="overflow-x:auto">'
                f'<table class="registry"><tr>{hdr}</tr>{body_rows}</table></div>')

    def _fmt_mt(val):
        """Format tCO2e to Mt with 2 decimals."""
        return f"{val / 1e6:.2f}"

    def _fmt_twh(mwh):
        """Convert MWh to TWh with 1 decimal."""
        return f"{mwh / 1e6:.1f}"

    # ---- Section 1: Cross-company comparison ----------------------------- #

    # Stat cards for DC electricity
    elec_cards = f"""
<div class="stats">
  <div class="stat"><b>{g['dc_twh']} TWh</b><span>Google (FY2025)</span></div>
  <div class="stat"><b>{aw['dc_twh']} TWh</b><span>AWS ({aw['report_year']}, est.)</span></div>
  <div class="stat"><b>{ms['dc_twh']} TWh</b><span>Microsoft ({ms['report_year']})</span></div>
  <div class="stat"><b>{m['dc_twh']} TWh</b><span>Meta (FY2024)</span></div>
</div>"""

    # hbars for DC electricity
    elec_bars = hbars([
        ("Google", g["dc_twh"], "FY2025"),
        ("AWS (Amazon)", aw["dc_twh"], f"{aw['report_year']} (est.)"),
        ("Microsoft", ms["dc_twh"], ms["report_year"]),
        ("Meta", m["dc_twh"], "FY2024"),
    ], unit=" TWh", color="var(--teal)")

    # Carbon emissions comparison
    g_scope2_loc = g["scope2_location_tco2e"] / 1e6
    m_scope2_loc = m["scope2_location_tco2e"] / 1e6
    carbon_bars = hbars([
        ("Google", round(g_scope2_loc, 1), "FY2025"),
        ("AWS (Amazon)", round(aw["scope2_location_mt"], 1), f"{aw['report_year']} (est.)"),
        ("Microsoft", round(ms["scope2_location_mt"], 1), ms["report_year"]),
        ("Meta", round(m_scope2_loc, 1), "FY2024"),
    ], unit=" Mt", color="var(--amber)")

    # Full comparison table
    m_water_mgal = round(m["water_consumption_ml"] * 0.264172)
    comp_rows = [
        ("Google", "FY2025",
         f"{g['dc_twh']}", f"{g_scope2_loc:.1f}",
         f"{g['scope2_market_tco2e'] / 1e6:.2f}",
         f"{g['water_dc_mgal']:,}", f"{g['global_cfe_pct']}% hourly"),
        ("Meta", "FY2024",
         f"{m['dc_twh']}", f"{m_scope2_loc:.1f}",
         f"{m['scope2_market_tco2e'] / 1e6:.2f}",
         f"{m_water_mgal:,}", f"{m['renewable_match_pct']}% annual"),
        ("Microsoft", ms["report_year"],
         f"{ms['dc_twh']}", f"{ms['scope2_location_mt']}",
         f"{ms['scope2_market_mt']}",
         f"{ms['water_consumption_mgal']:,}", f"{ms['renewable_pct']}% annual"),
        ("AWS (Amazon)", aw["report_year"],
         f"{aw['dc_twh']}", f"{aw['scope2_location_mt']}",
         f"{aw['scope2_market_mt']}",
         f"{aw['water_consumption_mgal']:,}", f"{aw['renewable_pct']}% annual"),
    ]
    comp_table_rows = "".join(
        f"<tr><td>{esc(co)}</td><td>{esc(yr)}</td><td>{twh}</td>"
        f"<td>{s2l}</td><td>{s2m}</td><td>{w}</td><td>{ren}</td></tr>"
        for co, yr, twh, s2l, s2m, w, ren in comp_rows)
    comp_table = (
        '<div style="overflow-x:auto">'
        '<table class="registry">'
        "<tr><th>Company</th><th>Report Year</th>"
        "<th>DC Electricity (TWh)</th>"
        "<th>Scope 2 Location (Mt)</th>"
        "<th>Scope 2 Market (Mt)</th>"
        "<th>Water Consumed (M gal)</th>"
        "<th>Renewable Match</th></tr>"
        f"{comp_table_rows}</table></div>")

    # ---- Section 2: Spend estimator (static, default rates) -------------- #

    dc_rate = 0.05
    res_rate = 0.16
    g_twh = g["dc_twh"]
    m_twh = m["dc_twh"]
    ms_twh = ms["dc_twh"]
    aw_twh = aw["dc_twh"]
    all_twh = g_twh + m_twh + ms_twh + aw_twh

    g_spend = g_twh * 1e9 * dc_rate
    m_spend = m_twh * 1e9 * dc_rate
    ms_spend = ms_twh * 1e9 * dc_rate
    aw_spend = aw_twh * 1e9 * dc_rate
    all_spend = g_spend + m_spend + ms_spend + aw_spend
    rate_ratio = res_rate / dc_rate
    all_equiv_homes = all_twh * 1e6 / 10.5

    # ---- Section 3: Deep-dives ------------------------------------------- #

    # 3a: Google deep-dive tables
    g_elec_rows = []
    for _, row in GOOGLE_DC_ELECTRICITY.iterrows():
        g_elec_rows.append((
            str(int(row["year"])),
            _fmt_twh(row["dc_mwh"]),
            _fmt_twh(row["total_mwh"]),
        ))
    g_elec_table = _trend_table(
        ["Year", "DC Electricity (TWh)", "Total (incl. offices) (TWh)"],
        g_elec_rows)

    g_ghg_rows = []
    for _, row in GOOGLE_GHG.iterrows():
        g_ghg_rows.append((
            str(int(row["year"])),
            _fmt_mt(row["scope2_location"]),
            _fmt_mt(row["scope2_market"]),
            _fmt_mt(row["total_ambition"]),
        ))
    g_ghg_table = _trend_table(
        ["Year", "Scope 2 Location (Mt)", "Scope 2 Market (Mt)",
         "Total Ambition (Mt)"],
        g_ghg_rows)

    g_water_rows = []
    for _, row in GOOGLE_WATER.iterrows():
        g_water_rows.append((
            str(int(row["year"])),
            f"{int(row['withdrawal']):,}",
            f"{int(row['consumption']):,}",
        ))
    g_water_table = _trend_table(
        ["Year", "Withdrawal (M gal)", "Consumption (M gal)"],
        g_water_rows)

    g_cfe_rows = []
    for _, row in GOOGLE_CFE_BY_GRID_DF.iterrows():
        g_cfe_rows.append((
            esc(str(row["grid"])),
            f"{int(row['google_cfe'])}%",
            f"{int(row['contracted_cfe'])}%",
            f"{int(row['consumed_grid_cfe'])}%",
            f"{int(row['grid_cfe'])}%",
        ))
    g_cfe_table = _trend_table(
        ["Grid Region", "Google CFE %", "Contracted %",
         "Consumed Grid %", "Grid CFE %"],
        g_cfe_rows)

    # Secondary key on `location` keeps ties (many sites share the same PUE)
    # in a deterministic order across runs — pandas' default sort is not
    # stable, and the drift was churning web/environment.html on every rebuild.
    pue_df = GOOGLE_PUE_SITES_DF.sort_values(["pue_2025", "location"])
    g_pue_rows = []
    for _, row in pue_df.iterrows():
        g_pue_rows.append((
            esc(str(row["location"])),
            esc(str(row["region"])),
            f"{row['pue_2025']:.2f}",
        ))
    g_pue_table = _trend_table(
        ["Location", "Region", "PUE (2025)"],
        g_pue_rows)

    # 3d: Meta deep-dive tables
    m_elec_rows = []
    for _, row in META_DC_ELECTRICITY.iterrows():
        m_elec_rows.append((
            str(int(row["year"])),
            _fmt_twh(row["dc_mwh"]),
            _fmt_twh(row["total_mwh"]),
        ))
    m_elec_table = _trend_table(
        ["Year", "DC Electricity (TWh)", "Total (incl. offices) (TWh)"],
        m_elec_rows)

    m_ghg_rows = []
    for _, row in META_GHG.iterrows():
        m_ghg_rows.append((
            str(int(row["year"])),
            _fmt_mt(row["scope2_location"]),
            _fmt_mt(row["scope2_market"]),
            _fmt_mt(row["scope3"]),
        ))
    m_ghg_table = _trend_table(
        ["Year", "Scope 2 Location (Mt)", "Scope 2 Market (Mt)",
         "Scope 3 (Mt)"],
        m_ghg_rows)

    m_eff_rows = []
    for _, row in META_EFFICIENCY.iterrows():
        m_eff_rows.append((
            str(int(row["year"])),
            f"{row['pue']:.2f}",
            f"{row['wue']:.2f}",
        ))
    m_eff_table = _trend_table(
        ["Year", "PUE", "WUE (L/kWh)"],
        m_eff_rows)

    campus_df = META_DC_CAMPUS_ELECTRICITY.sort_values(
        "mwh_2024", ascending=False)
    m_campus_rows = []
    for _, row in campus_df.iterrows():
        m_campus_rows.append((
            esc(str(row["campus"])),
            esc(str(row["region"])),
            f"{int(row['mwh_2024']):,}",
            f"{row['mwh_2024'] / 1e6:.3f}",
        ))
    m_campus_table = _trend_table(
        ["Campus", "Region", "MWh (2024)", "TWh (2024)"],
        m_campus_rows)

    # Meta water in M gal
    _water_restored_mgal = round(m["water_restoration_ml"] * 0.264172)

    # ---- Section 4: Revenue growth --------------------------------------- #

    _GROWTH_DATA = [
        {"Year": 2022, "Company": "Microsoft", "Revenue": 198.3},
        {"Year": 2023, "Company": "Microsoft", "Revenue": 211.9},
        {"Year": 2024, "Company": "Microsoft", "Revenue": 245.1},
        {"Year": 2025, "Company": "Microsoft", "Revenue": 280.5},
        {"Year": 2022, "Company": "Google (Alphabet)", "Revenue": 282.8},
        {"Year": 2023, "Company": "Google (Alphabet)", "Revenue": 307.4},
        {"Year": 2024, "Company": "Google (Alphabet)", "Revenue": 355.2},
        {"Year": 2025, "Company": "Google (Alphabet)", "Revenue": 400.1},
        {"Year": 2022, "Company": "NVIDIA", "Revenue": 27.0},
        {"Year": 2023, "Company": "NVIDIA", "Revenue": 27.0},
        {"Year": 2024, "Company": "NVIDIA", "Revenue": 60.9},
        {"Year": 2025, "Company": "NVIDIA", "Revenue": 120.8},
        {"Year": 2022, "Company": "Amazon", "Revenue": 514.0},
        {"Year": 2023, "Company": "Amazon", "Revenue": 574.8},
        {"Year": 2024, "Company": "Amazon", "Revenue": 630.5},
        {"Year": 2025, "Company": "Amazon", "Revenue": 685.2},
        {"Year": 2022, "Company": "Meta Platforms", "Revenue": 116.6},
        {"Year": 2023, "Company": "Meta Platforms", "Revenue": 134.9},
        {"Year": 2024, "Company": "Meta Platforms", "Revenue": 160.2},
        {"Year": 2025, "Company": "Meta Platforms", "Revenue": 185.5},
    ]
    growth_rows = "".join(
        f"<tr><td>{d['Year']}</td><td>{esc(d['Company'])}</td>"
        f"<td>${d['Revenue']:.1f}B</td></tr>"
        for d in _GROWTH_DATA)
    growth_table = (
        '<div style="overflow-x:auto">'
        '<table class="registry">'
        "<tr><th>Year</th><th>Company</th><th>Revenue</th></tr>"
        f"{growth_rows}</table></div>")

    # ---- REC gap bars for Microsoft and AWS ------------------------------ #

    ms_rec_gap = hbars([
        ("Scope 2 (location-based)", ms["scope2_location_mt"], "actual grid carbon"),
        ("Scope 2 (market-based)", ms["scope2_market_mt"], "after clean-energy contracts"),
    ], unit=" Mt", color="#00a4ef")

    aw_rec_gap = hbars([
        ("Scope 2 (location-based)", aw["scope2_location_mt"], "est. grid carbon"),
        ("Scope 2 (market-based)", aw["scope2_market_mt"], "100% renewable-matched"),
    ], unit=" Mt", color="#ff9900")

    # ---- Assemble body --------------------------------------------------- #

    body = f"""
<header>
  <div class="kicker">Environment</div>
  <h1>Hyperscaler environmental impact</h1>
  <p class="sub">Side-by-side environmental footprint of Google, Meta,
  Microsoft, and AWS &mdash; the four companies that build and operate the
  AI grid. Data from their latest sustainability reports.</p>
</header>

<details class="more"><summary>On this page</summary>
  <ol style="font-size:14px">
    <li>Hyperscaler environmental comparison</li>
    <li>What do they actually pay for electricity?</li>
    <li>Environmental deep-dives (Google, Microsoft, AWS, Meta)</li>
    <li>Revenue growth context (2022&ndash;2025)</li>
  </ol>
</details>

<section>
  <h2>1. Hyperscaler environmental comparison</h2>
  <p>Four companies consume more electricity than many countries. Here is
  how their data-center footprints compare on electricity, carbon, and
  water.</p>

  <h3>Data center electricity consumption</h3>
  {elec_cards}
  {elec_bars}

  <h3>Carbon emissions (Scope 2 location-based)</h3>
  <p class="muted">Location-based = actual grid carbon intensity at each
  facility. All four claim 100% renewable matching via certificates/PPAs
  (market-based), but that does not change what the grid actually burns.
  Google is the only one reporting hourly CFE matching (vs. annual).</p>
  {carbon_bars}

  <h3>Full comparison table</h3>
  {comp_table}
  <div class="note info"><p><strong>Caveats:</strong> AWS DC electricity is
  estimated (Amazon reports total company, not DC-only). Report years differ.
  Water measurement methods vary. Microsoft and Meta report annual renewable
  matching; Google reports hourly CFE. Market-based Scope 2 near zero for all
  four reflects certificate purchasing, not grid decarbonization.</p></div>
</section>

<section>
  <h2>2. What do they actually pay for electricity?</h2>
  <p>None of these companies disclose their utility spend or the rates they
  negotiate. But we can estimate it from their published consumption and
  public data on industrial electricity rates. The figures below use default
  assumptions of <strong>$0.05/kWh</strong> (data center rate) and
  <strong>$0.16/kWh</strong> (U.S. average residential rate).</p>

  <div class="stats">
    <div class="stat"><b>${g_spend / 1e9:.1f}B/yr</b><span>Google est. spend ({g_twh} TWh)</span></div>
    <div class="stat"><b>${aw_spend / 1e9:.1f}B/yr</b><span>AWS est. spend (~{aw_twh} TWh)</span></div>
    <div class="stat"><b>${ms_spend / 1e9:.1f}B/yr</b><span>Microsoft est. spend (~{ms_twh} TWh)</span></div>
    <div class="stat"><b>${m_spend / 1e9:.1f}B/yr</b><span>Meta est. spend ({m_twh} TWh)</span></div>
  </div>
  <div class="stats">
    <div class="stat"><b>${all_spend / 1e9:.1f}B/yr</b><span>All four combined ({all_twh:.0f} TWh)</span></div>
    <div class="stat"><b>{rate_ratio:.1f}x</b><span>Rate discount vs. residential (${res_rate:.2f} vs. ${dc_rate:.3f})</span></div>
    <div class="stat"><b>{all_equiv_homes / 1e6:.1f}M homes</b><span>Household equivalent (at 10,500 kWh/yr)</span></div>
  </div>

  <div class="note info"><p><strong>Why does this matter?</strong> Large data
  centers often negotiate rates 60&ndash;80% below what residential customers
  pay, plus tax abatements and infrastructure subsidies. When their load
  raises system peak demand, the resulting capacity charges are spread across
  <em>all</em> ratepayers. Your bill subsidizes their discount. See the
  <a href="bills.html">Your utility bill</a> page for how this works.</p></div>
  <p class="muted">These are estimates &mdash; actual rates are negotiated
  confidentially and filed under seal with state PUCs; no hyperscaler discloses
  utility spend. Consumption: {_srcref("google_env_2026")} &middot;
  {_srcref("meta_env_2025")} &middot; {_srcref("msft_env_2025")} &middot;
  {_srcref("amzn_env_2025")}</p>
</section>

<section>
  <h2>3. Environmental deep-dives</h2>
  <p>Detailed environmental data from each company&rsquo;s latest
  sustainability report. Google and Meta publish granular time-series;
  Microsoft and AWS publish headline metrics.</p>

  <details class="more"><summary>Google (FY2025)</summary>
    <p class="muted">First-party data from Google&rsquo;s 2026 Environmental
    Report (FY2025), subject to third-party limited assurance by KPMG.
    {_srcref("google_env_2026")}</p>

    <h3>Key metrics</h3>
    <div class="stats">
      <div class="stat"><b>{g['dc_twh']} TWh</b><span>DC electricity</span></div>
      <div class="stat"><b>{g['fleet_pue']}</b><span>Fleet-wide PUE</span></div>
      <div class="stat"><b>{g['global_cfe_pct']}%</b><span>Hourly CFE match</span></div>
      <div class="stat"><b>{g['water_consumption_mgal']:,}M gal</b><span>Water consumed</span></div>
    </div>
    <div class="stats">
      <div class="stat"><b>{g['scope2_market_tco2e'] / 1e6:.2f}M tCO2e</b><span>Scope 2 (market)</span></div>
      <div class="stat"><b>{g['scope2_location_tco2e'] / 1e6:.1f}M tCO2e</b><span>Scope 2 (location)</span></div>
      <div class="stat"><b>{g['clean_energy_gw_signed']} GW</b><span>Clean energy signed</span></div>
      <div class="stat"><b>{g['avoided_tco2e_m']}M tCO2e</b><span>Emissions avoided</span></div>
    </div>

    <h3>Electricity trend (2021&ndash;2025)</h3>
    <p class="muted">Google data centers grew from 17.4 TWh in 2021 to
    42.4 TWh in 2025 &mdash; a 143% increase in four years.</p>
    {g_elec_table}

    <h3>GHG emissions (2019&ndash;2025)</h3>
    <p class="muted">Location-based tracks actual grid carbon intensity &mdash;
    up 2.9x since 2019 as electricity demand surged. Market-based is far lower
    because Google retires renewable energy certificates against consumption.</p>
    {g_ghg_table}

    <h3>Water use (2021&ndash;2025)</h3>
    <p class="muted">DC water consumption reached 10.5 billion gallons in 2025.
    Google replenished 78% of freshwater consumed via 165 stewardship projects
    across 97 watersheds.</p>
    {g_water_table}

    <h3>Carbon-free energy by U.S. grid region (hourly, 2025)</h3>
    <p class="muted">Google&rsquo;s hourly CFE match per grid region.
    &ldquo;Google CFE&rdquo; = total CFE attributed (contracted + consumed
    grid). &ldquo;Grid CFE&rdquo; = the underlying grid&rsquo;s own clean
    energy share without Google&rsquo;s contracts.</p>
    {g_cfe_table}

    <h3>PUE per data center campus (2025)</h3>
    <p class="muted">Lower is better. Industry average PUE = 1.54 (Uptime
    Institute 2025). Google&rsquo;s best campus (Central Ohio Lancaster):
    1.04. Fleet average: 1.09.</p>
    {g_pue_table}
  </details>

  <details class="more"><summary>Microsoft (FY2025)</summary>
    <p class="muted">First-party data from Microsoft&rsquo;s 2025
    Environmental Sustainability Report (FY2025) and their January 2026
    Community-First AI Infrastructure initiative.
    {_srcref("msft_env_2025")} &middot; {_srcref("msft_community_2026")}</p>

    <h3>Key metrics</h3>
    <div class="stats">
      <div class="stat"><b>{ms['total_emissions_mt']}M tCO2e</b><span>Total GHG emissions</span></div>
      <div class="stat"><b>{ms['dc_twh']} TWh (est.)</b><span>DC electricity</span></div>
      <div class="stat"><b>{ms['pue']}</b><span>Fleet PUE</span></div>
      <div class="stat"><b>{ms['water_replenish_pct']}%</b><span>Water replenished</span></div>
    </div>

    <div class="note info"><p><strong>The transparency story:</strong>
    Microsoft stopped counting non-additional, unbundled RECs &mdash; and its
    market-based Scope 2 jumped from 0.26 to <strong>2.7M tCO2e</strong>,
    revealing real grid impact that certificates had masked. A rare accounting
    choice that makes a company&rsquo;s numbers look <em>worse</em> while
    being more honest.</p></div>

    <h3>The REC gap &mdash; Scope 2 location vs. market (FY2025)</h3>
    {ms_rec_gap}
    <p class="muted">Location-based (9.7 Mt) = carbon from the electrons
    actually consumed. Market-based (2.7 Mt) = after net-new clean-energy
    contracts. Because Microsoft now counts only additional carbon-free
    energy, the remaining gap reflects genuine grid impact rather than paper
    certificates. {_srcref("msft_env_2025")}</p>

    <details class="more"><summary>Accounting shift and Community-First framework</summary>
      <p><strong>Methodological shift.</strong> Microsoft paused the purchase
      of non-additional, unbundled Renewable Energy Certificates (RECs) to
      focus entirely on investing in net-new grid-decarbonizing carbon-free
      electricity (CFE). This drove reported Scope 2 emissions up from 2% to
      13% of its footprint &mdash; reflecting the raw reality of grid
      consumption. Upstream construction materials (steel, concrete) and server
      hardware manufacturing (Scope 3) remain the largest share of the total
      footprint.</p>
      <p><strong>The Community-First AI Infrastructure Framework (January
      2026).</strong> Launched by President Brad Smith to set a &ldquo;high
      bar&rdquo; for datacenter civic responsibility across five pillars:</p>
      <ol>
        <li><strong>Electricity (ratepayer protection):</strong> a pledge to
        pay their own way for grid upgrades &mdash; working with utilities and
        PUCs to set large-customer tariffs so transmission and substation
        costs are not passed to residential bills.</li>
        <li><strong>Water net-positivity:</strong> minimize draws and replenish
        more water than consumed in local basins.</li>
        <li><strong>Local employment:</strong> local construction-hiring
        mandates plus regional vocational and digital-skills programs.</li>
        <li><strong>Local tax base:</strong> property-tax revenue for municipal
        schools, hospitals, parks, and libraries.</li>
        <li><strong>Community investment:</strong> direct funding for local
        nonprofits and AI-literacy training in host counties.</li>
      </ol>
    </details>
  </details>

  <details class="more"><summary>Amazon AWS (CY2025)</summary>
    <p class="muted">First-party data from Amazon&rsquo;s 2025 Sustainability
    Report (CY2025), its June 2026 Water Stewardship disclosures, and the
    AWS in Communities program.
    {_srcref("aws_water_2026")} &middot; {_srcref("amzn_env_2025")}</p>

    <h3>Key metrics</h3>
    <div class="stats">
      <div class="stat"><b>{aw['dc_twh']} TWh (est.)</b><span>DC electricity</span></div>
      <div class="stat"><b>0.12 L/kWh</b><span>Fleet WUE (best of the four)</span></div>
      <div class="stat"><b>{aw['pue']}</b><span>Fleet PUE</span></div>
      <div class="stat"><b>{aw['water_replenish_pct']}%</b><span>Water replenished</span></div>
    </div>

    <div class="note info"><p><strong>Best-in-class cooling, first-time
    disclosure:</strong> AWS runs the lowest WUE of the four majors
    (0.12 L/kWh), and in June 2026 published its first detailed water
    footprint &mdash; 2.5B gallons of global withdrawals &mdash; after years
    of utility pressure. But its market-based Scope 2 of 0.0 Mt sits against
    an estimated 11.9 Mt of real grid carbon.</p></div>

    <h3>The REC gap &mdash; Scope 2 location vs. market (CY2025)</h3>
    {aw_rec_gap}
    <p class="muted">Market-based Scope 2 is 0.0 Mt &mdash; 100%
    renewable-matched on paper &mdash; while location-based grid impact is an
    estimated 11.9 Mt. The entire gap is certificates and PPAs, not grid
    decarbonization. Amazon does not break out DC-only figures, so the
    location-based estimate is derived from reported growth rates.
    {_srcref("amzn_env_2025")}</p>

    <details class="more"><summary>Water sourcing and community programs</summary>
      <p><strong>Recycled sourcing.</strong> AWS targets non-drinking water
      (recycled municipal wastewater) for server cooling to protect public
      aquifers &mdash; currently supplying over 100 campuses, with a goal of
      120 campuses by 2030.</p>
      <p><strong>Transparency milestone.</strong> In June 2026, AWS published
      its first detailed annual water footprint, reporting 2.5 billion gallons
      of global withdrawals and addressing long-standing utility requests.</p>
      <p><strong>AWS in Communities.</strong> Sponsors local infrastructure
      training bootcamps (fiber-optic cabling, cloud systems support) in major
      cluster metros such as Loudoun County, VA and Morrow County, OR to build
      a local operations-staff pipeline.</p>
    </details>
  </details>

  <details class="more"><summary>Meta (FY2024)</summary>
    <p class="muted">First-party data from Meta&rsquo;s 2025 Environmental
    Data Index (FY2024). Covers electricity consumption by campus, GHG
    emissions, water stewardship, PUE and WUE.
    {_srcref("meta_env_2025")}</p>

    <h3>Key metrics</h3>
    <div class="stats">
      <div class="stat"><b>{m['dc_twh']} TWh</b><span>DC electricity</span></div>
      <div class="stat"><b>{m['fleet_pue']}</b><span>Fleet-wide PUE</span></div>
      <div class="stat"><b>{m['fleet_wue']} L/kWh</b><span>Fleet-wide WUE</span></div>
      <div class="stat"><b>{m['renewable_match_pct']}%</b><span>Renewable match</span></div>
    </div>
    <div class="stats">
      <div class="stat"><b>{m['scope2_market_tco2e']:,} tCO2e</b><span>Scope 2 (market)</span></div>
      <div class="stat"><b>{m['scope2_location_tco2e'] / 1e6:.1f}M tCO2e</b><span>Scope 2 (location)</span></div>
      <div class="stat"><b>{m['scope3_tco2e'] / 1e6:.1f}M tCO2e</b><span>Scope 3 (value chain)</span></div>
      <div class="stat"><b>{_water_restored_mgal:,}M gal</b><span>Water restored</span></div>
    </div>

    <h3>Electricity trend (2020&ndash;2024)</h3>
    <p class="muted">Meta DC electricity grew from 7.0 TWh in 2020 to 18.1 TWh
    in 2024 &mdash; +159% in four years, driven by AI infrastructure buildout
    and new campus openings.</p>
    {m_elec_table}

    <h3>GHG emissions (2020&ndash;2024)</h3>
    <p class="muted">Meta&rsquo;s market-based Scope 2 is near-zero (1,358
    tCO2e in 2024) thanks to 100% REC matching. Location-based tells the real
    grid-impact story: 5.97M tCO2e from actual electrons consumed. Scope 3
    (hardware mfg., logistics, sold products) dominates the total footprint at
    8.15M tCO2e.</p>
    {m_ghg_table}

    <h3>PUE and WUE trend (2020&ndash;2024)</h3>
    <p class="muted">Meta&rsquo;s fleet PUE improved from 1.10 to 1.08 and WUE
    from 0.30 to 0.19 L/kWh, reflecting continued investment in liquid
    cooling, airside economization, and AI-optimized airflow management.</p>
    {m_eff_table}

    <h3>Electricity by data center campus (2024)</h3>
    <p class="muted">Top consumers: Prineville OR (1.73 TWh), Altoona IA
    (1.59 TWh), Sarpy NE (1.26 TWh), and leased facilities (3.07 TWh).</p>
    {m_campus_table}

    <div class="note info"><p><strong>Community grants:</strong> Since 2011,
    Meta has contributed over $74 million globally (with $24 million through
    direct local Community Action Grants) to fund technology integration and
    STEAM education in regional public schools. In 2026, the program awarded
    328 grants across data center communities, expanding to seven new host
    regions. {_srcref("meta_community_2026")}</p></div>
  </details>
</section>

<section>
  <h2>4. Revenue growth (2022&ndash;2025)</h2>
  <p>Context for the environmental figures above: the companies behind this
  infrastructure are among the largest on earth by revenue. The AI boom has
  accelerated their growth &mdash; and with it, their electricity and water
  consumption.</p>
  {growth_table}
  <p class="muted">Revenue figures from SEC 10-K filings. NVIDIA included for
  context as the dominant GPU supplier driving data center buildout.</p>
</section>

<section>
  <p><a class="btn" href="{APP_URL}">Open the toolkit &rarr;</a>
  <a class="btn ghost" href="companies/index.html">Company scorecards</a></p>
</section>
"""
    return page(
        "Environmental impact — AI GridWatch",
        "Side-by-side environmental footprint of Google, Meta, Microsoft, "
        "and AWS: electricity, carbon, water, and what they pay.",
        body, f"{SITE_URL}/environment",
        jsonld=_breadcrumb(
            ("Home", SITE_URL),
            ("Environment", f"{SITE_URL}/environment")))


def _load_ast_literal(path, var_name):
    """Read a top-level assignment target from a .py source file as a Python
    literal. Lets us reuse dict-literal data from Streamlit tab modules
    without importing streamlit here."""
    import ast
    tree = ast.parse(pathlib.Path(path).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if getattr(target, "id", None) == var_name:
                    return ast.literal_eval(node.value)
    raise KeyError(f"{var_name} not found in {path}")


def build_methodology():
    """Static twin of src/ui/method_tab.py — token-calculator methodology."""
    src_keys = [
        "google_2025", "openai_2025", "epoch_2025", "hungry_2025",
        "mlenergy", "iea_2025", "gpt5_report", "eia930", "pjm_dm2",
        "cbre_dc", "cbre_glob", "jll_dc", "cushman_dc", "google_dc",
        "meta_dc", "imasons", "bnef", "bnef_106", "gartner", "wri_range",
        "sp_451", "epri_pi", "lbnl", "ercot_ll", "ercot_ll_bc",
        "ercot_ll_tac", "pjm_lf", "eia_va", "eia_pilot",
        "ferc_pjm_colo", "ferc_showcause", "pjm_auction25", "tx_sb6_ll",
        "spp_hill", "miso_llir", "google_news", "reddit", "icap_mor",
        "dcbans", "dcopp", "dcwatch", "dcresp", "dctrack", "gjf_mor",
        "rockinst", "elmaps", "watttime", "gridstatus", "datacentermap",
        "msft_community_2026", "aws_water_2026", "meta_community_2026",
    ]
    src_html = "\n".join(
        f'<li><a href="{esc(SOURCES[k][1])}" rel="nofollow">{esc(SOURCES[k][0])}</a></li>'
        for k in src_keys if k in SOURCES)

    rows = []
    for label, v in QUERY_COEFFS.items():
        wh = f"{v['energy_wh']:.2f}"
        co2 = f"{v['co2_g']:.2f}" if v.get("co2_g") is not None else "—"
        h2o = f"{v['water_ml']:.2f}" if v.get("water_ml") is not None else "—"
        note = esc(v.get("note", ""))
        rows.append(
            f'<tr><td>{esc(label)}</td><td>{wh}</td>'
            f'<td>{co2}</td><td>{h2o}</td>'
            f'<td class="muted" style="font-size:13px">{note}</td></tr>')
    tbl_html = (
        '<div style="overflow-x:auto"><table>'
        '<tr><th>Source</th><th>Wh</th><th>gCO₂e</th>'
        '<th>mL water</th><th>Note</th></tr>'
        + "\n".join(rows) + "</table></div>")

    token_rows = "\n".join(
        f"<tr><td>{esc(k)}</td><td>{v:.4f} Wh/token</td></tr>"
        for k, v in TOKEN_COEFFS.items())
    grid_rows = "\n".join(
        f"<tr><td>{esc(k)}</td><td>{v} gCO₂/kWh</td></tr>"
        for k, v in GRID_INTENSITY.items())
    wue_rows = "\n".join(
        f"<tr><td>{esc(k)}</td><td>{v['l_per_kwh']:.2f} L/kWh</td></tr>"
        for k, v in ONSITE_WUE.items())
    off_rows = "\n".join(
        f"<tr><td>{esc(k)}</td><td>{v['l_per_kwh']:.2f} L/kWh</td></tr>"
        for k, v in OFFSITE_WATER.items())

    body = f"""
<header>
  <div class="kicker">Methodology</div>
  <h1>How the numbers on this site are calculated</h1>
  <p class="sub">Every coefficient the calculator uses, every source it cites,
  and the caveats worth reading before you quote a figure at a hearing.</p>
</header>

<section>
  <h2>Read the numbers carefully</h2>
  <ul>
    <li><strong>Scope matters most.</strong> Chip-only figures
    (~0.10 Wh/query) roughly halve full-stack (~0.24 Wh). Google's chip-only
    number excludes training, network, and end-user device energy.</li>
    <li><strong>Carbon accounting.</strong> Market-based (PPA/certificate)
    intensity can be ~⅓ of location-based grid intensity. The calculator lets
    you pick.</li>
    <li><strong>ML.ENERGY live numbers</strong> are min-energy (max-batch)
    configs on H100/B200 — a well-utilised server, so a lower bound vs.
    bursty real traffic.</li>
    <li><strong>Text only.</strong> Image, video, and reasoning prompts cost
    materially more per query.</li>
    <li><strong>Water is indirect too.</strong> Most disclosures count cooling
    water; almost none count water embedded in generating the electricity.
    Both matter — the calculator adds them.</li>
    <li><strong>Grid timing.</strong> Marginal intensity is the right signal
    for load-shifting; average (fuel-mix) intensity answers a different
    question. PJM Data Miner 2 provides marginal CO₂ live; other ISOs use
    stylized curves until a live feed is wired.</li>
  </ul>
</section>

<section>
  <h2>Per-query coefficients (median text prompt)</h2>
  {tbl_html}
</section>

<section>
  <h2>Per-token energy references</h2>
  <table>{token_rows}</table>
</section>

<section>
  <h2>Grid carbon intensity presets</h2>
  <table>{grid_rows}</table>
</section>

<section>
  <h2>Water — on-site cooling (fleet WUE)</h2>
  <p class="muted">L per kWh of IT load. Note L/kWh == mL/Wh, so these
  multiply query Wh into query mL.</p>
  <table>{wue_rows}</table>
</section>

<section>
  <h2>Water — off-site (grid generation)</h2>
  <p class="muted">Consumption (evaporated), not withdrawal — withdrawal
  figures run considerably higher.</p>
  <table>{off_rows}</table>
</section>

<section>
  <h2>Every source we cite</h2>
  <ul>{src_html}</ul>
</section>
"""
    return page(
        "Methodology — AI GridWatch",
        "Every coefficient and source used in the AI GridWatch calculators.",
        body, f"{SITE_URL}/methodology",
        jsonld=_breadcrumb(
            ("Home", SITE_URL),
            ("Methodology", f"{SITE_URL}/methodology")))


def build_studies():
    """Static twin of src/ui/studies_tab.py — state study library."""
    studies = _load_ast_literal("src/ui/studies_tab.py", "STATE_STUDIES")
    cards = []
    for state, s in studies.items():
        findings = "\n".join(f"<li>{_md_to_html(f).replace('<p>', '').replace('</p>', '')}</li>"
                             for f in s.get("findings", []))
        metrics = "\n".join(
            f"<tr><td><strong>{esc(k)}</strong></td><td>{esc(v)}</td></tr>"
            for k, v in s.get("metrics", {}).items())
        src = ""
        if s.get("src_key") in SOURCES:
            name, url = SOURCES[s["src_key"]]
            src = f' · <a href="{esc(url)}" rel="nofollow">{esc(name)}</a>'
        pdf = ""
        if s.get("pdf_url"):
            pdf = f' · <a href="{esc(s["pdf_url"])}" rel="nofollow">Read the PDF</a>'
        cards.append(f"""
<section id="{slugify(state)}">
  <h2>{esc(state)}</h2>
  <p><strong>{esc(s['title'])}</strong><br>
  <span class="muted">{esc(s['author'])}{src}{pdf}</span></p>
  <p>{esc(s['summary'])}</p>
  <h3 style="font-size:15px;color:var(--teal);margin:16px 0 6px">Key findings</h3>
  <ul>{findings}</ul>
  <h3 style="font-size:15px;color:var(--teal);margin:16px 0 6px">At a glance</h3>
  <table>{metrics}</table>
</section>""")

    toc = "\n".join(f'<li><a href="#{slugify(s)}">{esc(s)}</a></li>' for s in studies)
    body = f"""
<header>
  <div class="kicker">Studies library</div>
  <h1>Official state studies of data-center impact</h1>
  <p class="sub">A curated directory of state-commissioned reports,
  legislative audits, and PUC filings on data centers. The papers your
  planning commissioner will actually recognize.</p>
</header>
<details class="more" open><summary>On this page</summary><ol>{toc}</ol></details>
{"".join(cards)}
<section>
  <p class="muted"><em>Missing your state?</em> If your legislature, PUC, or
  audit agency has published a data-center study we should track, tell us and
  we'll add it — sources only, no press releases.</p>
</section>
"""
    return page(
        "Official state studies — AI GridWatch",
        "State-commissioned reports on data-center impact: Michigan CRC, Virginia JLARC, Georgia, Oregon, Maryland, Indiana, New Jersey.",
        body, f"{SITE_URL}/studies",
        jsonld=_breadcrumb(("Home", SITE_URL), ("Studies", f"{SITE_URL}/studies")))


def build_cba_clauses():
    """Model CBA clause library ported from src/ui/toolkit_tab.py."""
    clauses = _load_ast_literal("src/ui/toolkit_tab.py", "_MODEL_CLAUSES")
    cards = []
    for name, c in clauses.items():
        rng = ""
        if c.get("range_low"):
            unit = esc(c.get("unit") or "")
            rng = (f'<p class="muted">Typical range: <strong>'
                   f'${c["range_low"]:,}–${c["range_high"]:,}</strong> '
                   f'{unit}</p>')
        clause_text = esc(c["clause"]).replace("\\$", "$").replace("$", "&#36;")
        why_html = _md_to_html(c["why"].replace("\\$", "$"))
        cards.append(f"""
<section id="{slugify(name)}">
  <h2>{esc(c.get('icon',''))} {esc(name)}</h2>
  <div class="note info"><p><strong>Model clause:</strong></p>
    <pre style="white-space:pre-wrap;font:14px/1.55 ui-monospace,SFMono-Regular,Menlo,monospace;margin-top:8px">{clause_text}</pre>
  </div>
  <div class="prose">{why_html}</div>
  {rng}
</section>""")

    toc = "\n".join(f'<li><a href="#{slugify(n)}">{esc(n)}</a></li>' for n in clauses)
    body = f"""
<header>
  <div class="kicker">Model clauses</div>
  <h1>Model Community Benefits Agreement clauses</h1>
  <p class="sub">Copy-paste contract language for the terms communities most
  often need to secure in a data-center approval: water caps, noise limits,
  grid-cost allocation, decommissioning bonds, waste-heat recovery, and more.
  Every clause carries the reasoning and precedent behind it.</p>
</header>
<div class="note warn"><p><strong>Not legal advice.</strong> These are
starting points drafted from real precedents; a licensed attorney in your
state should tailor them before they go in front of a commission.</p></div>
<details class="more" open><summary>On this page</summary><ol>{toc}</ol></details>
{"".join(cards)}
"""
    return page(
        "Model CBA clauses — AI GridWatch",
        "Copy-paste contract language for community benefits agreements: water caps, noise limits, grid-cost allocation, decommissioning bonds, waste heat.",
        body, f"{SITE_URL}/cba-clauses",
        jsonld=_breadcrumb(
            ("Home", SITE_URL),
            ("CBA clauses", f"{SITE_URL}/cba-clauses")))


def build_officials():
    """State-level directory of Congressional + local lookup links, snapshot-only."""
    from src.local_officials import build_lookup_links
    a2f = dict(zip(STATE_PUCS_DF["abbrev"], STATE_PUCS_DF["state"]))
    cards = []
    for state in sorted(STATE_GRID_PROFILES):
        abbr = _ABBREV.get(state, "")
        senate = f"https://www.senate.gov/senators/index.htm"
        house = f"https://www.house.gov/representatives/find-your-representative"
        gov_link = f"https://duckduckgo.com/?q={html.escape(f'{state} governor site:.gov')}"
        leg_search = f"https://openstates.org/{abbr.lower()}/legislators/" if abbr else ""
        lookups = build_lookup_links(abbr, "")
        lookup_html = "\n".join(
            f'<li><a href="{esc(lk["url"])}" rel="nofollow">{esc(lk["label"])}</a>'
            f' — <span class="muted">{esc(lk["why"])}</span></li>'
            for lk in lookups)
        leg_html = (
            f' · <a href="{esc(leg_search)}" rel="nofollow">State legislators (OpenStates)</a>'
            if leg_search else "")
        cards.append(f"""
<section id="{slugify(state)}">
  <h2>{esc(state)}</h2>
  <p><strong>Federal</strong> —
    <a href="{esc(senate)}" rel="nofollow">Your senators (senate.gov)</a> ·
    <a href="{esc(house)}" rel="nofollow">Find your representative (house.gov)</a></p>
  <p><strong>State</strong> —
    <a href="{esc(gov_link)}" rel="nofollow">Governor's office</a>{leg_html}</p>
  <p><strong>Local</strong>:</p>
  <ul style="font-size:14px">{lookup_html}</ul>
</section>""")

    toc = '<div class="statelist">' + "\n".join(
        f'<a href="#{slugify(s)}">{esc(s)}</a>' for s in sorted(STATE_GRID_PROFILES)
    ) + "</div>"
    body = f"""
<header>
  <div class="kicker">Officials directory</div>
  <h1>Who to call, by state</h1>
  <p class="sub">Land-use votes happen at the county and town level, but
  federal and state officials shape the ratepayer rules. Every jump-off point
  you need — Senate, House, governor, state legislature, county government —
  in one place.</p>
</header>
<details class="more" open><summary>Jump to your state</summary>{toc}</details>
{"".join(cards)}
<section>
  <p class="muted">Sources: senate.gov, house.gov, OpenStates, NACo, USA.gov,
  state municipal leagues. Each state's PUC has its own dedicated
  <a href="puc.html">PUC directory page</a>. Curated town/county rosters for
  localities with an active fight live in the
  <a href="{APP_URL}">GridWatch toolkit</a> (they change too often for a
  static page).</p>
</section>
"""
    return page(
        "Officials directory — AI GridWatch",
        "Senate, House, governor, state legislature, and county government contact links for all 50 states plus D.C.",
        body, f"{SITE_URL}/officials",
        jsonld=_breadcrumb(
            ("Home", SITE_URL),
            ("Officials", f"{SITE_URL}/officials")))


def build_consulting():
    body = f"""
<header>
  <div class="kicker">Consulting</div>
  <h1>GridWatch Consulting</h1>
  <p class="sub">Data-driven negotiation support for communities facing data
  center development. We help you win better deals — and only get paid when
  you do.</p>
  <p><span style="display:inline-block;background:rgba(45,212,191,.14);
  border:1px solid var(--teal);border-radius:999px;padding:6px 14px;
  font-size:13px;color:var(--teal);font-weight:600">Success-fee model —
  no results, no cost</span></p>
</header>

<section>
  <h2>The problem</h2>
  <div class="grid2">
    <div class="card"><p>A hyperscaler shows up with a $2B proposal, a team
    of lawyers, and promises of "500 construction jobs." Your planning
    commission has 30 days to respond. The developer's hired consultants
    produce a glossy economic impact study. Your community has… a Facebook
    group and a lot of questions.</p></div>
    <div class="note bad"><p><strong>The asymmetry is the problem.</strong>
    The developer knows exactly what your land, water, and grid capacity are
    worth to them. You don't. That's where we come in.</p></div>
  </div>
</section>

<section>
  <h2>What we deliver</h2>
  <div class="grid3">
    <div class="card"><h3>Impact analysis</h3>
      <ul>
        <li>Energy load modeling using real grid data (PJM, EIA-930)</li>
        <li>Water consumption estimates by cooling type</li>
        <li>Residential rate impact projections</li>
        <li>Grid strain and reliability analysis</li>
        <li>Counter-analysis to the developer's economic study</li>
      </ul>
    </div>
    <div class="card"><h3>Deal structuring</h3>
      <ul>
        <li>Custom Community Benefits Agreement drafting</li>
        <li>Data Dividend fund design (the Alaska model)</li>
        <li>Tax-abatement analysis — what you're actually giving up</li>
        <li>Clawback provisions and performance guarantees</li>
        <li>Decommissioning bond sizing</li>
      </ul>
    </div>
    <div class="card"><h3>Hearing support</h3>
      <ul>
        <li>Expert testimony at planning and zoning hearings</li>
        <li>Data presentations for public comment periods</li>
        <li>Talking points for elected officials</li>
        <li>Media briefing materials</li>
        <li>Post-approval compliance monitoring</li>
      </ul>
    </div>
  </div>
</section>

<section>
  <h2>How we get paid</h2>
  <p>Communities shouldn't have to pay upfront to defend their own resources.
  We use a <strong>success-fee model</strong> that aligns our incentives with
  yours.</p>
  <div class="grid3">
    <div class="card"><h3>Free</h3><p class="muted"><strong>Initial
    consultation</strong></p>
      <ul>
        <li>60-minute situation assessment</li>
        <li>Preliminary impact estimate</li>
        <li>Recommendation on whether a CBA is achievable</li>
        <li>No obligation</li>
      </ul>
    </div>
    <div class="card"><h3>Success fee</h3><p class="muted"><strong>Full
    engagement</strong></p>
      <ul>
        <li>Small percentage of annual community benefits secured</li>
        <li>Fee only applies to <strong>new</strong> benefits we help negotiate</li>
        <li>Capped at a fair maximum — we're not the developer</li>
        <li>If we don't improve the deal, you pay nothing</li>
      </ul>
    </div>
    <div class="card"><h3>Flat fee</h3><p class="muted"><strong>Alternative
    structure</strong></p>
      <ul>
        <li>For communities that prefer fixed pricing</li>
        <li>Scoped to specific deliverables</li>
        <li>Payment milestones tied to project phases</li>
        <li>Available for grant-funded engagements</li>
      </ul>
    </div>
  </div>
</section>

<section>
  <h2>Why communities trust us</h2>
  <div class="stats">
    <div class="stat"><b>345+</b><span>active opposition groups across 37 states</span></div>
    <div class="stat"><b>$64B+</b><span>in blocked or delayed projects nationwide</span></div>
    <div class="stat"><b>300+</b><span>bills filed in 30 states (2026)</span></div>
    <div class="stat"><b>50+</b><span>CBA precedents tracked and analyzed</span></div>
  </div>
  <div class="note info"><p>We built <strong>AI GridWatch</strong> — the
  open-source platform used by communities nationwide to understand
  data-center impacts. The same data and models that power the free tool
  power our consulting analysis, with deeper customization for your specific
  situation.</p></div>
</section>

<section>
  <h2>Request a free consultation</h2>
  <p>Tell us about your situation. We'll respond within 48 hours with a
  preliminary assessment and recommended next steps.</p>
  <p><a class="btn" href="mailto:hello@aigridwatch.com?subject=Consulting%20request%20—%20AI%20GridWatch&body=Community%3A%20%0AState%3A%20%0ADeveloper%20%28if%20known%29%3A%20%0AFacility%20size%3A%20%0AStage%20of%20the%20process%3A%20%0ADescribe%20your%20situation%3A%20">Email us to start</a>
  <a class="btn ghost" href="{APP_URL}">Or use the free toolkit &rarr;</a></p>
</section>
"""
    return page(
        "Consulting — AI GridWatch",
        "Data-driven negotiation support for communities facing data-center development. Success-fee model.",
        body, f"{SITE_URL}/consulting",
        jsonld=_breadcrumb(
            ("Home", SITE_URL),
            ("Consulting", f"{SITE_URL}/consulting")))


def build_case_studies():
    """Merge MORATORIUM_OUTCOMES + CBA_BENCHMARKS + COMPANY_CONCESSIONS."""
    cat_class = {
        "CBA secured": "good",
        "Ban sustained": "info",
        "No protections": "bad",
        "Political shift": "warn",
    }
    outcome_cards = []
    for o in MORATORIUM_OUTCOMES:
        cls = cat_class.get(o["category"], "info")
        outcome_cards.append(f"""
<div class="note {cls}">
  <p><strong>{esc(o['locality'])}, {esc(o['state'])}</strong> —
  <span class="muted" style="font-size:12px;text-transform:uppercase;letter-spacing:.05em">
  {esc(o['category'])}</span></p>
  <p><strong>{esc(o['headline'])}</strong></p>
  <p>{esc(o['outcome'])}</p>
</div>""")

    bench_rows = "\n".join(
        f"<tr><td><strong>{esc(b['community'])}, {esc(b['state'])}</strong></td>"
        f"<td>{esc(b['company'])}</td>"
        f"<td>{esc(b['won'])}{_prov_links(b)}</td></tr>"
        for b in CBA_BENCHMARKS)

    concession_sections = []
    for company, info in COMPANY_CONCESSIONS.items():
        concessions = "\n".join(
            f"<li><strong>{esc(c['where'])}</strong> "
            f"({esc(c['year'])}) — {esc(c['what'])}{_prov_links(c)}</li>"
            for c in info["concessions"])
        concession_sections.append(f"""
<section id="{slugify(company)}">
  <h3 style="color:var(--teal);font-size:16px;margin-top:24px">{esc(company)}</h3>
  <p class="muted"><em>Negotiation pattern:</em> {esc(info['pattern'])}</p>
  <ul>{concessions}</ul>
</section>""")

    body = f"""
<header>
  <div class="kicker">Case studies</div>
  <h1>What communities have actually won — and lost</h1>
  <p class="sub">Documented outcomes from six moratorium fights, four
  benchmark CBAs, and every hyperscaler's documented pattern of concession.
  If you want to know what's realistic to ask for, this is where to start.</p>
</header>

<section>
  <h2>Moratorium outcomes</h2>
  <p class="muted">Six real cases; the categories reflect what the community
  ended up with, not what was originally proposed.</p>
  {"".join(outcome_cards)}
</section>

<section>
  <h2>Benchmark CBAs — what similar communities won</h2>
  <div style="overflow-x:auto"><table>
    <tr><th>Community</th><th>Developer</th><th>What they won</th></tr>
    {bench_rows}
  </table></div>
  <p class="muted">Every one of these happened <em>before</em> final approval.
  Timing is the leverage.</p>
</section>

<section>
  <h2>How each hyperscaler negotiates</h2>
  <p class="muted">Documented concessions and the pattern behind them. Use
  these to anchor your ask to what the same company has already agreed to
  elsewhere.</p>
  {"".join(concession_sections)}
</section>

<section>
  <p class="muted"><strong>See also:</strong>
  <a href="tax-breaks.html">The opportunity cost of subsidy packages</a> ·
  <a href="cba-clauses.html">Model CBA clauses</a> ·
  <a href="moratoriums.html">Full moratorium tracker</a> ·
  <a href="{APP_URL}">Generate a meeting brief with these precedents pre-loaded</a></p>
</section>
"""
    return page(
        "Case studies — AI GridWatch",
        "What communities have actually won and lost in data-center fights: moratorium outcomes, benchmark CBAs, per-hyperscaler negotiation patterns.",
        body, f"{SITE_URL}/case-studies",
        jsonld=_breadcrumb(
            ("Home", SITE_URL),
            ("Case studies", f"{SITE_URL}/case-studies")))


def build_hearing_questions():
    """Printable one-pager: questions to ask at your hearing."""
    body = f"""
<header>
  <div class="kicker">Hearing prep</div>
  <h1>Questions to ask at your next hearing</h1>
  <p class="sub">A one-page cheat sheet distilled from the wizard. Print it,
  screenshot it, hand it to a neighbor. Every question is designed to force
  a specific answer onto the record.</p>
</header>

<section>
  <h2>Power &amp; the grid</h2>
  <ol>
    <li>What is the <strong>peak MW draw</strong> at full build-out, not
    at commissioning?</li>
    <li>What transmission and substation upgrades does this project require,
    and <strong>which side of the utility fence</strong> pays for each?</li>
    <li>If any transmission goes into the utility's rate base, what is the
    <strong>projected monthly impact on residential customers</strong>, per
    the utility's own filed testimony?</li>
    <li>Will the developer accept a <strong>large-load tariff</strong>
    guaranteeing 100% of grid-upgrade costs stay off residential bills?</li>
    <li>What backup generation is planned, how many hours per year is it
    permitted to run, and are the units <strong>Tier 4 or battery</strong>
    rather than legacy diesel?</li>
  </ol>
</section>

<section>
  <h2>Water</h2>
  <ol>
    <li>What is the <strong>daily and annual water withdrawal</strong> at
    full build-out?</li>
    <li>What percentage of the municipal supply does that represent?</li>
    <li>Will the developer commit to a <strong>hard cap in gallons per
    day</strong>, with a surcharge for exceeding it, filed as a permit
    condition?</li>
    <li>If evaporative cooling is proposed, will the developer commit to
    <strong>recycled or non-potable water</strong> as Microsoft has for
    its new builds?</li>
    <li>Will water usage reports be filed as <strong>public record</strong>,
    not marked proprietary?</li>
  </ol>
</section>

<section>
  <h2>Money &amp; taxes</h2>
  <ol>
    <li>What is the <strong>total value of all tax abatements</strong>
    (property, equipment, sales) over the abatement period?</li>
    <li>What annual <strong>community benefit payment</strong> is on offer,
    in $/MW/year, and is it CPI-adjusted?</li>
    <li>Are there <strong>clawback provisions</strong> if the developer
    doesn't hit hiring or investment targets?</li>
    <li>Will data-center tax revenue be <strong>allocated to reduce
    residential property taxes</strong>, as Loudoun County does?</li>
    <li>What is the <strong>decommissioning bond</strong>, in $/MW, and when
    is it posted?</li>
  </ol>
</section>

<section>
  <h2>Noise &amp; light</h2>
  <ol>
    <li>What is the <strong>maximum modeled noise level</strong> at the
    nearest residential property line, and what limit will be recorded as
    a permit condition?</li>
    <li>Will noise be <strong>measured after commissioning</strong>, not
    just modeled beforehand, and reported publicly?</li>
    <li>Will exterior lighting be <strong>full-cutoff, shielded, and at or
    below 3000K</strong> per AMA community guidance?</li>
  </ol>
</section>

<section>
  <h2>Process &amp; transparency</h2>
  <ol>
    <li>Who is the <strong>ultimate parent</strong> of the LLC on the
    application? What is the tenant chain?</li>
    <li>Are there <strong>NDAs</strong> between the developer and any
    municipal official or utility that limit what can be disclosed at this
    hearing?</li>
    <li>What is the <strong>proposed build-out ceiling</strong> on this
    parcel — not phase one, but the full site plan?</li>
    <li>Will the developer agree to <strong>quarterly public reporting</strong>
    on water, noise, and generator hours as a permit condition?</li>
    <li>What happens if the tenant walks after <strong>year ten</strong> of
    the abatement — who owns the stranded infrastructure?</li>
  </ol>
</section>

<section>
  <div class="note info"><p><strong>Bring receipts.</strong> Every one of
  these questions has a documented precedent elsewhere. The
  <a href="case-studies.html">case studies</a> page has the citations; the
  <a href="cba-clauses.html">CBA clause library</a> has drop-in language
  to attach to any answer you're not satisfied with.</p></div>
  <p><a class="btn" href="{APP_URL}">Generate a personalized brief with your community's numbers &rarr;</a></p>
</section>
"""
    return page(
        "Questions to ask at your hearing — AI GridWatch",
        "A printable one-pager of the specific questions communities should ask a data-center developer at a planning or PUC hearing.",
        body, f"{SITE_URL}/hearing-questions",
        jsonld=_breadcrumb(
            ("Home", SITE_URL),
            ("Hearing questions", f"{SITE_URL}/hearing-questions")))


def build_glossary():
    terms = [
        ("PUE", "Power Usage Effectiveness — ratio of total facility energy to IT energy. Lower is better; hyperscalers target 1.10–1.20."),
        ("WUE", "Water Usage Effectiveness — liters of water per kWh of IT energy. Google fleet ~1.1 L/kWh; Meta claims 0.19."),
        ("CFE", "Carbon-Free Energy — electricity from zero-carbon sources (solar, wind, nuclear, hydro). Distinct from RECs."),
        ("Hyperscaler", "The largest cloud/AI companies that build their own data centers at massive scale (Google, Microsoft, Amazon, Meta)."),
        ("Colocation (colo)", "A data-center operator that leases space, power, and cooling to tenants — Equinix, Digital Realty, QTS, etc."),
        ("Interconnection queue", "The list of projects waiting for grid connection approval from the regional operator (PJM, ERCOT, MISO, etc.)."),
        ("Moratorium", "A temporary ban or pause on new data-center construction, usually enacted by local or state government."),
        ("PPA", "Power Purchase Agreement — a long-term contract to buy electricity from a specific generator, often renewable."),
        ("Rack density", "The amount of power drawn per server rack, measured in kW. AI racks are 40–120+ kW vs. 5–15 kW traditional."),
        ("GPU", "Graphics Processing Unit — specialized chips (NVIDIA H100, B200) that power AI training and inference."),
        ("Inference", "Running a trained AI model to generate responses — what happens when you use ChatGPT, Gemini, etc."),
        ("Training", "The initial process of building an AI model by processing massive datasets. Extremely energy-intensive."),
        ("Evaporative cooling", "Cooling method that evaporates water to remove heat. Effective but water-intensive."),
        ("Liquid cooling", "Piping coolant directly to server chips. More efficient for high-density AI workloads."),
        ("Marginal emissions", "The CO₂ rate of the next power plant that would turn on to serve new load. The right signal for load-shifting."),
        ("Average emissions", "The fuel-mix intensity of the whole grid. Answers a different question from marginal — used for inventory accounting."),
        ("Location-based carbon", "Carbon accounting using the actual grid mix where energy is consumed. What a data center's real footprint looks like."),
        ("Market-based carbon", "Carbon accounting after applying PPAs and certificates. Can be a fraction of location-based intensity."),
        ("Large-load tariff", "A utility rate structure requiring very large customers to pay their own grid-upgrade costs, not socialize them onto ratepayers."),
        ("Capacity market", "A market where utilities pay generators to be available on future peak days. Data-center demand is driving prices to record highs in PJM."),
        ("CBA", "Community Benefits Agreement — a binding contract between a community and a developer setting terms like water caps, noise limits, and community payments."),
        ("Data dividend", "A community fund into which per-MW annual payments are placed, distributed or reinvested locally — modelled on Alaska's oil dividend."),
        ("Clawback", "A contractual provision allowing tax abatements or incentives to be recovered if the developer fails to meet promised commitments."),
        ("Decommissioning bond", "A financial guarantee posted by the developer to cover site cleanup if the facility ceases operations."),
        ("Proffer", "In Virginia land-use practice, a voluntary condition offered by a developer as part of a rezoning application. Should be recorded as binding."),
        ("Shell LLC", "A limited-liability company (often with a fanciful name) used by hyperscalers to acquire land and file permits without revealing the parent."),
        ("Certificate of Public Convenience and Necessity (CPCN)", "A regulatory approval a utility or generator must obtain before building. Some states exempt data-center backup power."),
        ("Substation", "The facility that steps voltage down (typically from 115–765 kV transmission to 12–34 kV distribution) at the edge of a data-center campus."),
        ("RTO / ISO", "Regional Transmission Organization / Independent System Operator — the operators that run the wholesale grid (PJM, ERCOT, MISO, SPP, CAISO, NYISO, ISO-NE)."),
        ("FERC", "The Federal Energy Regulatory Commission — regulates interstate wholesale electricity and transmission. ERCOT is the notable exception (Texas-only)."),
        ("EIA-930", "The U.S. Energy Information Administration's real-time grid demand and generation dataset. What the calculator's Live Grid mode uses."),
    ]
    rows = "\n".join(
        f'<tr id="{slugify(t)}"><td><strong>{esc(t)}</strong></td>'
        f'<td>{esc(d)}</td></tr>'
        for t, d in terms)
    body = f"""
<header>
  <div class="kicker">Glossary</div>
  <h1>Data-center vocabulary — what the terms actually mean</h1>
  <p class="sub">The jargon developers use in hearings and filings, translated
  into plain English. Every term links, so you can share
  <code>/glossary#pue</code> in a comment thread.</p>
</header>
<div style="overflow-x:auto"><table>
  <tr><th style="width:26%">Term</th><th>Definition</th></tr>
  {rows}
</table></div>
<section>
  <p class="muted">Missing a term? Tell us and we'll add it. For the
  full technical background, see the <a href="learn.html">Learn</a> page.</p>
</section>
"""
    return page(
        "Glossary — AI GridWatch",
        "Plain-English definitions of the technical and legal terms used in data-center hearings and filings.",
        body, f"{SITE_URL}/glossary",
        jsonld=_breadcrumb(
            ("Home", SITE_URL),
            ("Glossary", f"{SITE_URL}/glossary")))


_ZIP3_TO_STATE = {
    # USPS zip3 → USPS state code. Ranges compressed to (lo, hi, state).
    "MA": [(10, 27)], "RI": [(28, 29)], "NH": [(30, 38)], "ME": [(39, 49)],
    "VT": [(50, 59)], "CT": [(60, 69)], "NJ": [(70, 89)],
    "NY": [(100, 149), (63, 63)],  # 005 is Holtsville NY (IRS)
    "PA": [(150, 196)], "DE": [(197, 199)],
    # Northern VA (Ashburn/Loudoun) uses the 201 prefix but neighboring 200
    # and 202-205 stay with DC. Keep the two ranges separate.
    "DC": [(200, 200), (202, 205), (569, 569)],
    "MD": [(206, 219)],
    "VA": [(201, 201), (220, 246)],
    "WV": [(247, 268)],
    "NC": [(270, 289)], "SC": [(290, 299)], "GA": [(300, 319), (398, 399)],
    "FL": [(320, 349)], "AL": [(350, 369)], "TN": [(370, 385)],
    "MS": [(386, 397)],
    "KY": [(400, 427)], "OH": [(430, 459)], "IN": [(460, 479)],
    "MI": [(480, 499)], "IA": [(500, 528)], "WI": [(530, 549)],
    "MN": [(550, 567)], "SD": [(570, 577)], "ND": [(580, 588)],
    "MT": [(590, 599)], "IL": [(600, 629)], "MO": [(630, 658)],
    "KS": [(660, 679)], "NE": [(680, 693)],
    "LA": [(700, 714)], "AR": [(716, 729)], "OK": [(730, 749)],
    "TX": [(750, 799), (885, 885)],
    "CO": [(800, 816)], "WY": [(820, 831)], "ID": [(832, 838)],
    "UT": [(840, 847)], "AZ": [(850, 865)], "NM": [(870, 884)],
    "NV": [(889, 898)], "CA": [(900, 961)], "HI": [(967, 968)],
    "OR": [(970, 979)], "WA": [(980, 994)], "AK": [(995, 999)],
}


def _siting_profiles():
    """Per-state siting scorecard, built from constants at build time and
    embedded into the /siting page as JSON. Six subscores 0-100 (higher =
    more attractive to a data-center developer)."""
    hubs = {
        # Rough proximity-to-existing-cluster scores. Fiber follows clusters.
        "VA": 100, "TX": 95, "CA": 90, "OH": 85, "GA": 85, "AZ": 85,
        "OR": 82, "WA": 82, "IL": 80, "NY": 78, "NJ": 78, "IA": 75,
        "NV": 74, "NE": 72, "IN": 70, "NC": 68, "PA": 68, "CO": 65,
        "MN": 60, "FL": 60, "SC": 58, "TN": 58, "MI": 55, "MO": 55,
        "OK": 55, "UT": 55, "LA": 55, "WI": 50, "MD": 50,
        "KY": 48, "MA": 48, "CT": 45, "NM": 45, "KS": 45,
        "AL": 42, "AR": 40, "MS": 40, "ID": 40, "SD": 38, "ND": 38,
        "MT": 35, "WY": 35, "ME": 35, "NH": 35, "VT": 30, "RI": 35,
        "DE": 40, "WV": 35, "HI": 20, "AK": 15, "DC": 55,
    }
    scores = {}
    for state, prof in STATE_GRID_PROFILES.items():
        row = STATE_DC_DF[STATE_DC_DF["state"] == state]
        abbr = _ABBREV.get(state, "")
        dc_count = int(row.iloc[0]["dc_count"]) if not row.empty else 0
        twh = float(row.iloc[0]["twh_year"]) if not row.empty else 0.0
        major_hubs = str(row.iloc[0]["major_hubs"]) if not row.empty else ""
        upcoming = bool(row.iloc[0]["upcoming"]) if not row.empty else False
        moras = MORATORIUMS_DF[MORATORIUMS_DF["state"] == abbr]

        # Power: cheap + carbon-considered. Rates and carbon both normalized.
        rate = prof.get("rate", 0.14)
        gco2 = prof.get("gco2", 400)
        power_price = max(0, min(100, int((0.30 - rate) / 0.20 * 100)))
        power_carbon = max(0, min(100, int((600 - gco2) / 400 * 100)))
        power = int(power_price * 0.65 + power_carbon * 0.35)

        # Fiber: based on cluster proximity table.
        fiber = hubs.get(abbr, 40)

        # Land: bigger existing footprint = more industrial availability,
        # but too-established markets are saturated. U-shaped scoring.
        if dc_count == 0:
            land = 20
        elif dc_count < 20:
            land = 55
        elif dc_count < 100:
            land = 80
        elif dc_count < 250:
            land = 75
        else:
            land = 60

        # Water: from stress category. High-stress states are harder now.
        stress = prof.get("water_stress", "medium")
        water = {"low": 85, "medium": 55, "high": 25}.get(stress, 50)

        # Tax climate: presence in the SALT-friendly / DC-tax-exemption cohort.
        friendly = {"VA", "TX", "GA", "OH", "OR", "AZ", "NV", "NC", "NE",
                    "IA", "OK", "SC", "TN", "MS", "IN", "KS", "PA", "MO",
                    "IL", "MI", "WI", "MN"}
        hostile = {"NY", "NJ", "CT", "MA", "RI", "VT", "CA", "HI"}
        if abbr in friendly:
            tax = 85
        elif abbr in hostile:
            tax = 35
        else:
            tax = 60

        # Politics: existing moratoriums = harder path.
        mora_count = len(moras)
        if mora_count == 0:
            politics = 80
        elif mora_count <= 2:
            politics = 55
        elif mora_count <= 5:
            politics = 35
        else:
            politics = 20

        overall = int((power * 0.28 + fiber * 0.22 + land * 0.15
                       + water * 0.14 + tax * 0.13 + politics * 0.08))
        if overall >= 80: grade = "A"
        elif overall >= 70: grade = "B"
        elif overall >= 60: grade = "C"
        elif overall >= 45: grade = "D"
        else: grade = "F"

        scores[abbr] = {
            "state": state, "abbr": abbr, "slug": slugify(state),
            "grade": grade, "overall": overall,
            "power": power, "fiber": fiber, "land": land,
            "water": water, "tax": tax, "politics": politics,
            "rate_cents": round(rate * 100, 1), "gco2": gco2,
            "water_stress": stress, "dc_count": dc_count, "twh": twh,
            "major_hubs": major_hubs, "upcoming": upcoming,
            "moratoriums": mora_count,
            "tax_class": ("friendly" if abbr in friendly
                          else "hostile" if abbr in hostile else "neutral"),
        }
    return scores


def build_siting():
    import json as _json
    profiles = _siting_profiles()
    zip_map = _json.dumps(_ZIP3_TO_STATE)
    profile_json = _json.dumps(profiles)
    body = f"""
<header>
  <div class="kicker">Siting evaluator</div>
  <h1>Would a data center want to build in your town?</h1>
  <p class="sub">Enter a zip code or pick a state. You'll get a
  six-factor siting scorecard — power, fiber, land, water, tax climate,
  political risk — plus a plain-English read on why a hyperscaler's
  site-selection team probably has your county on a spreadsheet
  somewhere.</p>
</header>

<section>
  <h2>Look up your area</h2>
  <div class="card">
    <label for="s-zip" style="display:block;font-weight:600;margin-bottom:6px">Zip code (5 digits) or town name</label>
    <input id="s-zip" type="text" placeholder="e.g. 20147 or Ashburn"
      style="width:100%;padding:10px 12px;border:1px solid var(--rule);
      border-radius:8px;background:var(--bg);color:var(--ink);
      font:15px system-ui;">
    <p style="margin:12px 0 6px;color:var(--muted);font-size:13px">…or pick a state:</p>
    <select id="s-state" style="width:100%;padding:10px 12px;
      border:1px solid var(--rule);border-radius:8px;background:var(--bg);
      color:var(--ink);font:15px system-ui">
      <option value="">— pick a state —</option>
      {"".join(f'<option value="{p["abbr"]}">{esc(p["state"])}</option>' for p in profiles.values())}
    </select>
    <p><button id="s-go" class="btn" style="margin-top:14px;border:none;cursor:pointer">Show me the report &rarr;</button></p>
    <p id="s-err" class="muted" style="color:#fca5a5;display:none;margin-top:6px"></p>
  </div>
</section>

<div id="s-report" style="display:none">
  <section id="s-summary"></section>
  <section id="s-cards"></section>
  <section id="s-narrative"></section>
  <section id="s-nextsteps">
    <h2>What to do with this</h2>
    <ul>
      <li>Read the <a href="tax-breaks.html">opportunity-cost briefing</a> before your next council meeting — the higher your score, the more leverage you have.</li>
      <li>Bring the <a href="hearing-questions.html">hearing questions</a> and the <a href="cba-clauses.html">CBA clause library</a> to any public comment period.</li>
      <li>Use the <a href="{APP_URL}">Start here wizard</a> for an interactive impact estimate at the parcel level (this page is state-level; the app can do geocoded lookups).</li>
      <li>Check the <a href="case-studies.html">case studies</a> for what similar communities won or lost.</li>
    </ul>
  </section>
  <p class="src" style="margin-top:18px">Scores are heuristic composites built
  from state-level data on the site: retail electricity rates, grid carbon,
  known data-center count and TWh, water-stress category, state tax posture
  toward data centers, and moratorium tracker counts. They describe the
  <em>state</em> a zip code sits in — actual siting decisions are made at
  the parcel level and depend on factors this tool can't see (fiber routes,
  substation capacity, land title). Treat as a starting frame, not a
  verdict.</p>
</div>

<script>
const ZIP_MAP = {zip_map};
const PROFILES = {profile_json};

function zipToState(zip) {{
  const z = parseInt(zip.substring(0,3), 10);
  if (isNaN(z)) return null;
  for (const [state, ranges] of Object.entries(ZIP_MAP)) {{
    for (const [lo, hi] of ranges) {{
      if (z >= lo && z <= hi) return state;
    }}
  }}
  return null;
}}

const NARRATIVES = {{
  power: (p) => p.power >= 75
    ? `${{p.state}}'s retail electricity is around ${{p.rate_cents}}¢/kWh — well below the coastal average — and its grid carbon runs about ${{p.gco2}} gCO₂/kWh. Cheap firm power is the single strongest signal for hyperscaler siting.`
    : p.power >= 50
    ? `${{p.state}} sits mid-pack on power: retail rates around ${{p.rate_cents}}¢/kWh and grid carbon near ${{p.gco2}} gCO₂/kWh. Attractive if a specific tariff or PPA is on the table; not a decisive advantage.`
    : `${{p.state}}'s retail power runs high (${{p.rate_cents}}¢/kWh) and the grid emissions profile (${{p.gco2}} gCO₂/kWh) puts it below the shortlist for cost-sensitive tenants. Developers who build here usually have a specific renewables deal locked.`,
  fiber: (p) => p.fiber >= 75
    ? `${{p.state}} sits on the top tier of the US fiber map — dense backbone, low latency to the coasts, and a well-worn path for permitting. Peer developers are already there, which is both a positive (proven) and a negative (competition for the best parcels).`
    : p.fiber >= 50
    ? `${{p.state}} has adequate fiber for edge and mid-tier cloud, but is not a Tier-1 backbone hub. A developer with a specific latency requirement is more likely to look at neighboring states.`
    : `${{p.state}} is fiber-thin for hyperscale. Long-haul routes exist but a new campus would likely need to co-fund fiber build-out — that shows up as an operator ask early in negotiations.`,
  land: (p) => p.dc_count >= 100
    ? `${{p.state}} already hosts ${{p.dc_count}} tracked facilities. Land in the established hubs is spoken for; new campuses tend to push into second-tier counties nearby. Expect displacement pressure.`
    : p.dc_count >= 20
    ? `${{p.state}}'s ${{p.dc_count}} tracked facilities mean the industrial land market understands data-center buyers — brokers know the drill, county assessors have templates.`
    : `${{p.state}} has only ${{p.dc_count}} tracked facilities. Land is cheaper but the local permitting apparatus is unfamiliar; expect a longer entitlement cycle.`,
  water: (p) => p.water_stress === "low"
    ? `Low water stress. Municipal or well supply is unlikely to constrain a cooling design here, which is exactly why arid-state hyperscalers are increasingly hunting parcels in states like this.`
    : p.water_stress === "high"
    ? `High water stress. Evaporative cooling is politically radioactive; expect any credible proposal to lead with air-cooling or closed-loop designs — and expect the community to still push back on both.`
    : `Medium water stress. Cooling design will be scrutinized; watershed authorities are the most likely veto point.`,
  tax: (p) => p.tax_class === "friendly"
    ? `${{p.state}} has an existing data-center sales-tax exemption or equivalent posture. That's the incentive most developers assume before they walk in. Don't treat it as a concession you got — you gave it.`
    : p.tax_class === "hostile"
    ? `${{p.state}} runs a heavier tax regime and lacks the standard data-center carve-outs. A hyperscaler looking here is doing so despite the tax bill, which means the other factors have to compensate.`
    : `${{p.state}} sits in the middle of the tax-posture pack. Custom abatements are usually still on the table for large enough projects.`,
  politics: (p) => p.moratoriums === 0
    ? `No moratoriums tracked in-state. Politically, the runway is clear — that's an argument for organizing early, not for assuming the fight isn't coming.`
    : p.moratoriums <= 2
    ? `${{p.moratoriums}} tracked moratorium(s) in-state. Precedent for pushback exists; find the organizers and read what they filed.`
    : `${{p.moratoriums}} tracked moratoriums in-state — a real political pattern. Any new proposal here will run into an experienced opposition network.`,
}};

function factorCard(label, score, narrative, key) {{
  const color = score >= 70 ? "#34d399" : score >= 50 ? "#fbbf24" : "#f87171";
  return `<div class="card" style="margin-bottom:14px">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
      <h3 style="margin:0">${{label}}</h3>
      <span style="font-size:22px;font-weight:700;color:${{color}}">${{score}}</span>
    </div>
    <div style="height:6px;border-radius:3px;background:rgba(255,255,255,.06);overflow:hidden;margin-bottom:10px">
      <div style="height:6px;width:${{score}}%;background:${{color}};border-radius:3px"></div>
    </div>
    <p class="muted" style="margin:0;font-size:14px">${{narrative}}</p>
  </div>`;
}}

function render(state) {{
  const p = PROFILES[state];
  if (!p) {{
    document.getElementById("s-err").style.display = "block";
    document.getElementById("s-err").textContent = "State not recognized.";
    return;
  }}
  document.getElementById("s-err").style.display = "none";
  document.getElementById("s-report").style.display = "block";

  const gradeColor = ({{"A":"#34d399","B":"#6ee7b7","C":"#fbbf24","D":"#f97316","F":"#ef4444"}})[p.grade] || "#93a1b5";
  document.getElementById("s-summary").innerHTML = `
    <h2>${{p.state}} — siting attractiveness</h2>
    <div class="card" style="display:grid;grid-template-columns:auto 1fr;gap:24px;align-items:center">
      <div style="text-align:center">
        <div style="font-size:64px;line-height:1;font-weight:800;color:${{gradeColor}}">${{p.grade}}</div>
        <div class="muted" style="margin-top:4px">overall</div>
      </div>
      <div>
        <p style="margin:0 0 6px"><strong>Composite score:</strong> ${{p.overall}} / 100</p>
        <p class="muted" style="margin:0">${{p.dc_count}} tracked data centers · ${{p.twh}} TWh/yr · ${{p.moratoriums}} moratorium(s) recorded · ${{p.major_hubs || "no major hubs yet"}}${{p.upcoming ? " · upcoming projects flagged" : ""}}</p>
      </div>
    </div>`;

  document.getElementById("s-cards").innerHTML = `
    <h2>The six factors</h2>
    ${{factorCard("Power (price + carbon)", p.power, NARRATIVES.power(p), "power")}}
    ${{factorCard("Fiber & cluster proximity", p.fiber, NARRATIVES.fiber(p), "fiber")}}
    ${{factorCard("Land availability", p.land, NARRATIVES.land(p), "land")}}
    ${{factorCard("Water", p.water, NARRATIVES.water(p), "water")}}
    ${{factorCard("Tax climate", p.tax, NARRATIVES.tax(p), "tax")}}
    ${{factorCard("Political risk", p.politics, NARRATIVES.politics(p), "politics")}}`;

  const leverage = p.overall >= 75
    ? "Your area is on any serious hyperscaler shortlist. That's leverage — the developer will invest months of siting cost before ever walking into your hearing. Treat the tax package as a negotiation, not a check-the-box approval."
    : p.overall >= 55
    ? "Your area is competitive but not automatic. A developer here has options; so do you. Focus on what raises your score (fiber, tariff design) as a bargaining chip in either direction."
    : "Your area is unlikely to see a hyperscale project without a specific push — a state incentive or a nearby cluster spillover. If a proposal appears anyway, ask why: something on the developer's spreadsheet is compensating for what this scorecard says is missing.";

  document.getElementById("s-narrative").innerHTML = `
    <h2>What this means for your leverage</h2>
    <div class="note info"><p>${{leverage}}</p></div>
    <p><a href="states/${{p.slug}}.html" class="btn ghost">Full ${{p.state}} state briefing &rarr;</a></p>`;
}}

function lookup() {{
  const zip = document.getElementById("s-zip").value.trim();
  const stateSel = document.getElementById("s-state").value;
  if (zip && /^\\d{{3,5}}$/.test(zip)) {{
    const state = zipToState(zip);
    if (state) return render(state);
    document.getElementById("s-err").style.display = "block";
    document.getElementById("s-err").textContent =
      "Zip prefix not recognized (military APO/FPO or a US territory outside the 50 states + DC). Try picking a state below.";
    return;
  }}
  if (stateSel) return render(stateSel);
  // Try town lookup by matching against known localities.
  if (zip) {{
    const needle = zip.toLowerCase();
    for (const p of Object.values(PROFILES)) {{
      if (p.major_hubs && p.major_hubs.toLowerCase().includes(needle)) {{
        return render(p.abbr);
      }}
    }}
  }}
  document.getElementById("s-err").style.display = "block";
  document.getElementById("s-err").textContent =
    "Enter a 5-digit US zip code, a recognizable town, or pick a state from the dropdown.";
}}

document.getElementById("s-go").addEventListener("click", lookup);
document.getElementById("s-zip").addEventListener("keydown", (e) => {{
  if (e.key === "Enter") {{ e.preventDefault(); lookup(); }}
}});
</script>
"""
    return page(
        "Siting evaluator — AI GridWatch",
        "Enter a zip code or state and get a six-factor scorecard of how attractive that area is to a data-center developer, plus what it means for your leverage.",
        body, f"{SITE_URL}/siting",
        jsonld=_breadcrumb(
            ("Home", SITE_URL),
            ("Siting evaluator", f"{SITE_URL}/siting")))


def build_tax_breaks():
    """The 'we'll build elsewhere' framing argument."""
    body = f"""
<header>
  <div class="kicker">The opportunity cost</div>
  <h1>"We'll build somewhere else." No, they won't.</h1>
  <p class="sub">The single most effective negotiating line a data-center
  developer uses is a bluff. Here's how to call it — and what stops being
  free once you do.</p>
</header>

<section>
  <h2>The threat</h2>
  <p>It arrives in every hearing, in almost the same words: <em>if you
  don't grant this abatement, this rate, this exemption, we'll build
  somewhere else.</em> It's delivered with a folder of comparative site
  data and the quiet suggestion that the neighboring county is more
  reasonable.</p>
  <div class="note bad"><p><strong>The threat is almost always a
  bluff.</strong> A company only reaches your hearing after it has already
  decided your site is competitive. Cheap and abundant power, a reliable
  grid, fiber trunks, tens of acres of flat land, water — the shortlist
  of parcels that clear all five is short, and yours is on it.</p></div>
</section>

<section>
  <h2>What actually put you on the shortlist</h2>
  <p>Data centers site around five constraints, in roughly this order:</p>
  <ol>
    <li><strong>Firm power</strong> — 50 to 500+ MW available on a
    utility that will interconnect this decade, not next.</li>
    <li><strong>Fiber</strong> — dense, redundant, low-latency backbone
    within reach.</li>
    <li><strong>Land</strong> — flat, cheap, out of flood plains, in
    an industrial or industrial-adjacent zone.</li>
    <li><strong>Water</strong> — reliable municipal or well supply, or
    a permit path to it.</li>
    <li><strong>Speed of approval</strong> — a jurisdiction that will
    say yes on the developer's schedule.</li>
  </ol>
  <p>Tax abatements sit <em>below</em> all five. They shape the last mile
  of the decision, not the shortlist. The team on the other side of the
  table has already spent months of siting analysis to conclude yours is
  one of the very few parcels that clears the technical bars. That
  analysis is a sunk cost the developer doesn't want to redo.</p>
</section>

<section>
  <h2>The revenue left on the table</h2>
  <p>Because officials treat the abatement offer as an all-or-nothing
  question, the negotiation collapses into <em>whether</em> to give it
  rather than <em>how much</em>. A different starting question changes
  the outcome:</p>
  <div class="note info"><p><strong>Start here:</strong> what's the
  full public value of this site to the developer, and what fraction of
  that value is the community capturing?</p></div>
  <p>The gap between what a hyperscaler is willing to pay for a 200 MW
  parcel and what it usually ends up paying — after abatements — is the
  opportunity cost. Loudoun County, Virginia is the counter-example that
  proves the frame: by declining the standard abatement package, its
  data-center property taxes now fund roughly a third of the county
  budget while keeping residential rates among the lowest in the state.</p>
  <p>A tax break is not a one-line item. It is one line in a much longer
  ledger the community rarely sees at once.</p>
</section>

<section>
  <h2>The full menu of giveaways</h2>
  <p>By the time a project is approved, the same community has typically
  handed over some combination of:</p>
  <div class="grid2">
    <div class="card">
      <h3>Local &amp; state</h3>
      <ul>
        <li>Property-tax abatements (often 10–20 years)</li>
        <li>Equipment / personal-property tax exemptions</li>
        <li>Sales-tax exemptions on servers and networking gear</li>
        <li>Data-center-specific sales-tax carve-outs on electricity</li>
        <li>Fee waivers on permits, impact fees, connection charges</li>
        <li>Publicly funded road, water, and sewer extensions</li>
        <li>Enterprise-zone or opportunity-zone stacking</li>
      </ul>
    </div>
    <div class="card">
      <h3>Utility &amp; federal</h3>
      <ul>
        <li>Large-load tariffs with grid-upgrade costs socialized onto
        residential ratepayers</li>
        <li>Transmission built for one tenant and placed in the general
        rate base</li>
        <li>Federal investment tax credits on on-site renewables and storage</li>
        <li>Accelerated depreciation (MACRS) on server infrastructure</li>
        <li>Federal Opportunity Zone capital-gains deferral, where applicable</li>
      </ul>
    </div>
  </div>
  <p class="muted" style="margin-top:12px">Individually each line looks
  modest. Stacked, a single hyperscale campus can extract
  <strong>billions of dollars</strong> in combined public support over
  its lifetime — from some of the most profitable companies in the world.</p>
</section>

<section>
  <h2>The right test</h2>
  <p>Before approving the next package, the question is not <em>does
  this attract the project?</em> The project is already here. The
  question is:</p>
  <blockquote style="border-left:3px solid var(--teal);margin:16px 0;
   padding:8px 16px;font-size:17px;color:var(--ink)">
    Does this deal serve the public interest — or is it padding the
    profits of some of the world's wealthiest corporations at the
    community's expense?
  </blockquote>
  <p>The answer depends on the numbers, not the rhetoric. Every hyperscaler
  publishes its revenue. Compare it to the value of the package on the
  table. If the ratio doesn't make sense on that math, it's not a good
  deal — no matter how many jobs are in the press release.</p>
</section>

<section>
  <h2>What to do with this at your next hearing</h2>
  <ol>
    <li>Ask the developer, on the record, for its
    <strong>own siting analysis</strong> — the ranked list of alternative
    parcels considered and the reasons each was scored below yours.
    They rarely produce it. That refusal is itself the answer.</li>
    <li>Ask your assessor to produce the <strong>full stacked value</strong>
    of every subsidy line — local, state, utility, and federal — over
    the life of the abatement. Insist on a single dollar figure.</li>
    <li>Ask the developer to identify <strong>which subsidy lines it
    would walk away over</strong>. If the answer is "all of them,"
    the bluff is exposed. If the answer is specific, you know what's
    negotiable.</li>
    <li>Bring the <a href="case-studies.html">case-studies</a> page.
    Loudoun County declined abatements and still hosts more data
    centers than any jurisdiction on earth. Precedent matters.</li>
    <li>Use the <a href="cba-clauses.html">CBA clause library</a> to
    trade specific tax concessions for specific written commitments,
    not soft promises.</li>
  </ol>
</section>

<section>
  <div class="note good"><p><strong>The bottom line:</strong> local
  officials rarely have leverage this concrete over Fortune-100 companies.
  A data center at your door is proof you already have it. Every subsidy
  line the community gives away without asking is money left on the
  table — from a counterparty whose next-best alternative is almost
  always worse than yours.</p></div>
  <p><a class="btn" href="{APP_URL}">Generate a meeting brief with these questions pre-loaded &rarr;</a>
  <a class="btn ghost" href="hearing-questions.html">Full hearing checklist</a></p>
</section>
"""
    return page(
        "Tax breaks & the opportunity cost — AI GridWatch",
        "\"We'll build somewhere else\" is almost always a bluff. What communities are actually leaving on the table when they hand a data center a subsidy package.",
        body, f"{SITE_URL}/tax-breaks",
        jsonld=_breadcrumb(
            ("Home", SITE_URL),
            ("Tax breaks", f"{SITE_URL}/tax-breaks")))


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
        body, f"{SITE_URL}/about",
        jsonld=_breadcrumb(("Home", SITE_URL), ("About", f"{SITE_URL}/about")))


def build_search():
    import json
    index = []
    for m in MORATORIUMS_DF.itertuples():
        # effective_status, not status — otherwise search results keep calling
        # a lapsed moratorium "Enacted" long after the page itself stopped.
        _mark = "" if m.verified else " · unverified"
        index.append({"t": str(m.locality), "k": "moratorium",
                       "d": f"{m.state} · {m.effective_status}{_mark}",
                       "u": f"moratoriums.html"})
    for _, r in OPERATORS_DF.iterrows():
        index.append({"t": r["operator"], "k": "operator",
                       "d": f"{r['tier']} · {r['model']}",
                       "u": "executives.html"})
    for _, r in EXECUTIVES_DF.iterrows():
        suffix = "" if has_value(r["verified"]) else " · unverified"
        index.append({"t": r["name"], "k": "executive",
                       "d": f"{r['company']} · {r['title']}{suffix}",
                       "u": "executives.html"})
    for _, r in DC_SITES_DF.iterrows():
        loc = str(r.get("location", ""))
        st = str(r.get("state", ""))
        index.append({"t": f"{r['operator']} — {loc}",
                       "k": "site",
                       "d": f"{st} · {cell(r.get('tenant'))}",
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
        body, f"{SITE_URL}/search",
        jsonld=_breadcrumb(("Home", SITE_URL), ("Search", f"{SITE_URL}/search")))


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
        body, f"{SITE_URL}/dividend",
        jsonld=_breadcrumb(("Home", SITE_URL), ("Dividend calculator", f"{SITE_URL}/dividend")))


def build_sitemap(paths):
    urls = "\n".join(
        f"  <url><loc>{SITE_URL}/{p}</loc></url>" for p in paths)
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f'{urls}\n</urlset>\n')


DATA_LICENSE = "CC BY 4.0"
DATA_LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"

# Column → what it means. Published with the data because a tracker without a
# stated schema is what every other data-center moratorium list already is:
# a table you cannot reuse without emailing whoever made it.
MORATORIUM_SCHEMA = [
    ("locality", "Town, city or county taking the action; 'X (statewide)' for state-level"),
    ("state", "USPS two-letter code"),
    ("level", "Local or State"),
    ("status", "As recorded: Enacted, Proposed, Rejected, Vetoed or Rescinded"),
    ("effective_status", "Status today. Equals `status`, except an Enacted row past its `expires` date reads Expired. Use this one"),
    ("expired", "true when a documented term has run out"),
    ("days_left", "Days until `expires`; negative once past, null when no end date is recorded"),
    ("when", "Human-readable date of the action, as reported"),
    ("expires", "ISO date the term lapses, or null when permanent, condition-based, or not documented"),
    ("note", "Scope, threshold, vote count and other detail"),
    ("source", "URL this row was read from, or null if unverified"),
    ("as_of", "Date the source was read, or null"),
    ("verified", "true when a source is recorded. false means nobody has checked this row — treat it as a lead"),
    ("lat", "Latitude, null for state-level rows"),
    ("lon", "Longitude, null for state-level rows"),
]


def _mora_records():
    """MORATORIUMS_DF as plain JSON-able dicts, nulls where data is missing."""
    cols = [c for c, _ in MORATORIUM_SCHEMA]
    out = []
    for r in MORATORIUMS_DF.to_dict("records"):
        rec = {}
        for c in cols:
            v = r.get(c)
            if isinstance(v, (bool, int, float)) and not isinstance(v, bool):
                rec[c] = None if pd.isna(v) else v
            elif isinstance(v, bool):
                rec[c] = v
            else:
                rec[c] = str(v) if has_value(v) else None
        out.append(rec)
    return out


def build_moratorium_data():
    """Write the tracker as JSON + CSV so it can be cited, not just read.

    The provenance work only pays off if someone else can use it. Nobody
    else publishes moratorium data with per-row sourcing and a derived
    expiry, so shipping it as a documented, licensed download is the
    cheapest distribution this project has — journalists cite what they can
    query and researchers cite what they can download.
    """
    import csv
    import datetime as _dt
    import io

    records = _mora_records()
    payload = {
        "name": "AI GridWatch data center moratorium tracker",
        "generated": _dt.date.today().isoformat(),
        "license": DATA_LICENSE,
        "license_url": DATA_LICENSE_URL,
        "attribution": f"AI GridWatch ({SITE_URL})",
        "source_page": f"{SITE_URL}/moratoriums",
        "count": len(records),
        "verified_count": sum(1 for r in records if r["verified"]),
        "caveat": (registry_provenance("MORATORIUMS_DF") or {}).get("caveat", ""),
        "schema": {c: d for c, d in MORATORIUM_SCHEMA},
        "moratoriums": records,
    }
    (WEB / "data").mkdir(parents=True, exist_ok=True)
    (WEB / "data" / "moratoriums.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=[c for c, _ in MORATORIUM_SCHEMA],
                       lineterminator="\n")
    w.writeheader()
    w.writerows(records)
    (WEB / "data" / "moratoriums.csv").write_text(buf.getvalue(),
                                                  encoding="utf-8")
    return len(records)


def build_alerts_outputs():
    """Publish the expiry alerts as JSON and RSS.

    RSS because it needs no account, no email address and no infrastructure
    this project doesn't have: a resident, a reporter or a clerk subscribes
    and gets told when a pause near them is about to lapse. Email alerts need
    a subscriber list, which is PII, which lives outside git — so this is the
    half that can ship today rather than the half that waits on a webhook.
    """
    import datetime as _dt
    from email.utils import format_datetime

    alerts = build_alerts()
    (WEB / "data").mkdir(parents=True, exist_ok=True)
    (WEB / "data" / "alerts.json").write_text(
        json.dumps({
            "generated": _dt.date.today().isoformat(),
            "lookahead_days": ALERT_LOOKAHEAD,
            "license": DATA_LICENSE,
            "license_url": DATA_LICENSE_URL,
            "attribution": f"AI GridWatch ({SITE_URL})",
            "count": len(alerts),
            "alerts": alerts,
        }, indent=2) + "\n", encoding="utf-8")

    # Both timestamps are derived, never `now()`. Two reasons, and the second
    # is the one that bites: an unchanged alert re-dated every build resurfaces
    # as new in a reader, and — worse — the file's bytes change on every build,
    # so CI would commit alerts.xml on every single run. That is exactly the
    # "web/ churning when data didn't change" failure build-site.yml warns
    # about. Per item: the day the alert entered the lookahead window, which is
    # a fixed function of its expiry. Feed-level: midnight today, so the file
    # is byte-identical across same-day rebuilds.
    def _entered(a):
        end = _dt.date.fromisoformat(a["expires"])
        return _dt.datetime.combine(
            end - _dt.timedelta(days=ALERT_LOOKAHEAD),
            _dt.time(0, 0), tzinfo=_dt.timezone.utc)

    now = _dt.datetime.combine(_dt.date.today(), _dt.time(0, 0),
                               tzinfo=_dt.timezone.utc)
    items = "\n".join(f"""  <item>
    <title>{esc(a['title'])}</title>
    <link>{SITE_URL}/moratoriums#data</link>
    <guid isPermaLink="false">{esc(a['id'])}</guid>
    <pubDate>{format_datetime(_entered(a))}</pubDate>
    <description>{esc(a['body'])}</description>
  </item>""" for a in alerts)
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <title>AI GridWatch — moratorium deadline alerts</title>
  <link>{SITE_URL}/moratoriums</link>
  <description>Data center moratoriums lapsing in the next {ALERT_LOOKAHEAD}
  days, and those that recently lapsed. Derived from documented end dates —
  moratoriums are often extended, so treat a date as the earliest a pause
  could end, not proof that it did.</description>
  <language>en-us</language>
  <lastBuildDate>{format_datetime(now)}</lastBuildDate>
{items}
</channel></rss>
"""
    (WEB / "alerts.xml").write_text(feed, encoding="utf-8")
    return len(alerts)


def build_moratorium_embed():
    """Standalone iframe-able tracker for other people's sites.

    Rendered server-side rather than fetching the JSON: an embed that depends
    on a cross-origin fetch fails silently on somebody else's page, and the
    whole point is that it keeps working somewhere we cannot see. Self-
    contained, noindex (the canonical page should rank, not this), and it
    carries attribution back — that is the deal the licence asks for.
    """
    rows = "\n".join(
        f'<tr data-state="{esc(str(m.state))}">'
        f"<td>{esc(str(m.locality))}</td><td>{esc(str(m.state))}</td>"
        f'<td><span class="s s-{esc(str(m.effective_status).lower())}">'
        f"{esc(str(m.effective_status))}</span></td>"
        f"<td>{esc(str(m.when))}</td>"
        f"<td>{'<a href=' + chr(34) + esc(str(m.source)) + chr(34) + ' target=_blank rel=noopener>source</a>' if has_value(m.source) else '<span class=u>unverified</span>'}</td>"
        f"</tr>"
        for m in MORATORIUMS_DF.itertuples())
    states = "".join(
        f'<option value="{esc(s)}">{esc(s)}</option>'
        for s in sorted(MORATORIUMS_DF["state"].unique()))
    in_force = len(MORATORIUMS_DF[MORATORIUMS_DF["effective_status"] == "Enacted"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>Data center moratorium tracker — AI GridWatch</title>
<style>
 :root {{ color-scheme: light dark; }}
 body {{ margin:0; font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
        background:#0b1220; color:#e6edf7; }}
 .wrap {{ padding:14px; }}
 h1 {{ font-size:15px; margin:0 0 2px; }}
 .sub {{ color:#93a1b5; font-size:12px; margin:0 0 10px; }}
 select {{ background:#121c30; color:#e6edf7; border:1px solid #22304a;
           border-radius:6px; padding:5px 8px; font-size:13px; margin-bottom:10px; }}
 .scroll {{ max-height:420px; overflow:auto; border:1px solid #22304a; border-radius:8px; }}
 table {{ border-collapse:collapse; width:100%; }}
 th,td {{ text-align:left; padding:7px 9px; border-bottom:1px solid #1b2740; font-size:13px; }}
 th {{ position:sticky; top:0; background:#121c30; font-size:11px;
       text-transform:uppercase; letter-spacing:.05em; color:#93a1b5; }}
 a {{ color:#2dd4bf; }}
 .u {{ color:#fca5a5; font-size:12px; }}
 .s {{ font-size:11px; font-weight:700; padding:1px 7px; border-radius:5px; }}
 .s-enacted {{ background:#065f46; color:#6ee7b7; }}
 .s-proposed {{ background:#713f12; color:#fde68a; }}
 .s-rejected {{ background:#7f1d1d; color:#fca5a5; }}
 .s-vetoed,.s-rescinded {{ background:#4c1d95; color:#c4b5fd; }}
 .s-expired {{ background:#374151; color:#d1d5db; }}
 footer {{ margin-top:9px; font-size:11px; color:#93a1b5; }}
</style></head><body><div class="wrap">
<h1>Data center moratoriums &amp; pushback</h1>
<p class="sub">{len(MORATORIUMS_DF)} tracked actions · {in_force} in force today ·
status shown is what applies now, so a lapsed term reads Expired.</p>
<select id="f" aria-label="Filter by state">
  <option value="">All states</option>{states}</select>
<div class="scroll"><table>
<tr><th>Locality</th><th>State</th><th>Status</th><th>When</th><th>Source</th></tr>
{rows}</table></div>
<footer>Data: <a href="{SITE_URL}/moratoriums" target="_blank" rel="noopener">AI
GridWatch</a> · <a href="{DATA_LICENSE_URL}" target="_blank" rel="license noopener">{DATA_LICENSE}</a>
· <a href="{SITE_URL}/data/moratoriums.json" target="_blank" rel="noopener">JSON</a></footer>
</div>
<script>
document.getElementById('f').addEventListener('change', function (e) {{
  var v = e.target.value;
  document.querySelectorAll('tr[data-state]').forEach(function (r) {{
    r.style.display = (!v || r.dataset.state === v) ? '' : 'none';
  }});
}});
</script></body></html>"""


def main():
    global _NEWS_ITEMS, _VIDEO_ITEMS
    print("  [news] loading headlines + videos…")
    _NEWS_ITEMS, news_themes, top_stories, news_fetched_at = _load_news()
    _VIDEO_ITEMS, _ = _load_youtube()

    shutil.rmtree(WEB, ignore_errors=True)
    (WEB / "states").mkdir(parents=True)
    (WEB / "blog").mkdir(parents=True)
    (WEB / "news").mkdir(parents=True)
    (WEB / "companies").mkdir(parents=True)
    (WEB / "assets").mkdir()

    shutil.copy(ROOT / "assets" / "logo.svg", WEB / "assets" / "logo.svg")
    # Default og:image for every page — social platforms won't render an SVG
    # card, so the per-post inline art can't serve double duty here.
    shutil.copy(ROOT / "assets" / "hero.png", WEB / "assets" / "hero.png")
    (WEB / "assets" / "gridwatch_health_risks.pdf").write_bytes(
        build_health_pdf(HEALTH_RISKS, SOURCES))

    (WEB / "index.html").write_text(build_index(), encoding="utf-8")
    (WEB / "health-risks.html").write_text(build_health(), encoding="utf-8")
    (WEB / "moratoriums.html").write_text(build_moratoriums(), encoding="utf-8")
    _n_data = build_moratorium_data()
    _n_alerts = build_alerts_outputs()
    print(f"  [data] {_n_alerts} deadline alerts -> alerts.json + alerts.xml")
    (WEB / "embed").mkdir(parents=True, exist_ok=True)
    (WEB / "embed" / "moratoriums.html").write_text(
        build_moratorium_embed(), encoding="utf-8")
    print(f"  [data] published {_n_data} moratoriums as JSON + CSV + embed")
    (WEB / "impact.html").write_text(build_impact_calculator(), encoding="utf-8")
    (WEB / "bills.html").write_text(build_bills(), encoding="utf-8")
    (WEB / "outlook.html").write_text(build_outlook(), encoding="utf-8")
    (WEB / "learn.html").write_text(build_learn(), encoding="utf-8")
    (WEB / "puc.html").write_text(build_puc(), encoding="utf-8")
    (WEB / "executives.html").write_text(build_executives(), encoding="utf-8")
    (WEB / "about.html").write_text(build_about(), encoding="utf-8")
    (WEB / "search.html").write_text(build_search(), encoding="utf-8")
    (WEB / "dividend.html").write_text(build_data_dividend(), encoding="utf-8")
    (WEB / "data-centers.html").write_text(build_data_centers(), encoding="utf-8")
    (WEB / "environment.html").write_text(build_environment(), encoding="utf-8")
    (WEB / "methodology.html").write_text(build_methodology(), encoding="utf-8")
    (WEB / "studies.html").write_text(build_studies(), encoding="utf-8")
    (WEB / "cba-clauses.html").write_text(build_cba_clauses(), encoding="utf-8")
    (WEB / "officials.html").write_text(build_officials(), encoding="utf-8")
    (WEB / "consulting.html").write_text(build_consulting(), encoding="utf-8")
    (WEB / "case-studies.html").write_text(build_case_studies(), encoding="utf-8")
    (WEB / "hearing-questions.html").write_text(
        build_hearing_questions(), encoding="utf-8")
    (WEB / "glossary.html").write_text(build_glossary(), encoding="utf-8")
    (WEB / "tax-breaks.html").write_text(build_tax_breaks(), encoding="utf-8")
    (WEB / "siting.html").write_text(build_siting(), encoding="utf-8")
    (WEB / "states" / "index.html").write_text(
        build_states_index(), encoding="utf-8")

    posts = _sorted_posts()
    (WEB / "blog" / "index.html").write_text(
        build_blog_index(), encoding="utf-8")
    (WEB / "blog" / "feed.xml").write_text(build_rss(), encoding="utf-8")

    (WEB / "news" / "index.html").write_text(
        build_news_page(_NEWS_ITEMS, news_fetched_at,
                        videos=_VIDEO_ITEMS,
                        themes=news_themes,
                        top_stories=top_stories),
        encoding="utf-8")
    (WEB / "news" / "feed.xml").write_text(
        build_news_rss(_NEWS_ITEMS, news_fetched_at), encoding="utf-8")

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

    paths = ["", "health-risks", "moratoriums", "impact", "bills", "outlook",
             "learn", "puc", "executives", "about", "search", "dividend",
             "data-centers", "environment", "methodology", "studies",
             "cba-clauses", "officials", "consulting", "case-studies",
             "hearing-questions", "glossary", "tax-breaks", "siting",
             "companies/", "states/", "blog/", "news/"]
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
    _blog_redirects = [
        {"source": f"/{s['id']}", "destination": f"/blog/{s['id']}",
         "permanent": True}
        for s in _sorted_posts()
    ]
    # Root-level shortcuts for the 51 state pages, so /indiana → /states/indiana.
    _state_redirects = [
        {"source": f"/{slugify(row['state'])}",
         "destination": f"/states/{slugify(row['state'])}",
         "permanent": False}
        for _, row in STATE_PUCS_DF.iterrows()
    ]
    (WEB / "vercel.json").write_text(
        '{ "cleanUrls": true, "trailingSlash": false }\n', encoding="utf-8")
    # The load-bearing config Vercel actually reads lives at the repo root.
    # Keep outputDirectory/cleanUrls/trailingSlash intact; refresh redirects.
    (ROOT / "vercel.json").write_text(
        json.dumps({
            "outputDirectory": "web",
            "cleanUrls": True,
            "trailingSlash": False,
            "redirects": _blog_redirects + _state_redirects,
        }, indent=2) + "\n",
        encoding="utf-8")

    n = len(list(WEB.rglob("*.html")))
    print(f"built web/ — {n} pages, sitemap, robots.txt, vercel.json")
    print(f"SITE_URL={SITE_URL}\nAPP_URL={APP_URL}")


if __name__ == "__main__":
    main()
