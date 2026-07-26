"""
Campaign micro-site generator — a self-contained single-file HTML page a
community group can host anywhere free (GitHub Pages, Netlify Drop, or any
static host). No external assets, no JS dependencies; numbers come from the
shared impact model via the caller. Pure string assembly, no Streamlit.
"""

import html


def build_campaign_site(state, mw, imp, upgrade_per_home_yr,
                        group_name="", contact_email="",
                        meeting_when="", meeting_where="", operator=""):
    """Returns a complete index.html as a string."""
    esc = html.escape
    group = esc(group_name) if group_name else f"{esc(state)} Residents"
    title = f"{group} — {mw} MW data center: get the facts"
    homes = f"{imp['homes_equiv']:,.0f}"
    twh = f"{imp['annual_twh']:.1f}"
    water = f"{imp['annual_water_mgal']:,.0f}M"
    bill = f"${upgrade_per_home_yr:,.0f}"
    cba = f"${imp['data_dividend_usd'] / 1e6:.1f}M"
    op_line = (f" The operator behind it: <strong>{esc(operator)}</strong>."
               if operator and operator != "Unknown / not listed" else "")
    when = esc(meeting_when) if meeting_when else "[DATE & TIME]"
    where = esc(meeting_where) if meeting_where else "[LOCATION]"
    contact = (
        f'<a class="btn" href="mailto:{esc(contact_email)}?subject='
        f'Count me in">Email us — count me in</a>'
        if contact_email else
        '<p class="muted">[Add your group\'s contact email when you '
        'publish this page.]</p>')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="A {mw} MW data center is proposed \
near us. Electricity of {homes} homes, {water} gallons of water/yr, and \
~{bill}/household/yr on our bills unless conditions are attached. Meeting: \
{when}.">
<style>
  :root {{
    --bg: #0b1220; --card: #121c30; --ink: #eaf0f7; --muted: #93a1b5;
    --teal: #2dd4bf; --amber: #fbbf24; --rule: #22304a;
  }}
  * {{ box-sizing: border-box; margin: 0; }}
  body {{
    background: var(--bg); color: var(--ink);
    font: 16px/1.6 system-ui, -apple-system, "Segoe UI", sans-serif;
  }}
  .wrap {{ max-width: 860px; margin: 0 auto; padding: 24px 20px 64px; }}
  header {{ padding: 40px 0 8px; }}
  .kicker {{
    color: var(--teal); font-weight: 700; letter-spacing: .12em;
    text-transform: uppercase; font-size: 13px;
  }}
  h1 {{ font-size: clamp(28px, 5vw, 42px); line-height: 1.15; margin: 10px 0; }}
  .sub {{ color: var(--muted); max-width: 640px; }}
  .stats {{
    display: grid; grid-template-columns: repeat(2, 1fr);
    gap: 14px; margin: 32px 0;
  }}
  @media (min-width: 640px) {{ .stats {{ grid-template-columns: repeat(4, 1fr); }} }}
  .stat {{
    background: var(--card); border: 1px solid var(--rule);
    border-radius: 14px; padding: 18px 16px;
  }}
  .stat b {{ display: block; font-size: 26px; color: var(--teal); }}
  .stat span {{ font-size: 13px; color: var(--muted); }}
  section {{ margin: 36px 0; }}
  h2 {{
    font-size: 20px; color: var(--teal); margin-bottom: 12px;
    border-bottom: 1px solid var(--rule); padding-bottom: 8px;
  }}
  ul {{ padding-left: 22px; }} li {{ margin: 10px 0; }}
  .meeting {{
    background: var(--card); border: 2px solid var(--teal);
    border-radius: 14px; padding: 22px; text-align: center;
  }}
  .meeting .when {{ font-size: 22px; font-weight: 700; margin: 6px 0; }}
  .btn {{
    display: inline-block; background: var(--teal); color: #06251f;
    font-weight: 700; padding: 12px 22px; border-radius: 10px;
    text-decoration: none; margin-top: 12px;
  }}
  .muted {{ color: var(--muted); font-size: 14px; }}
  .prec b {{ color: var(--amber); }}
  footer {{
    margin-top: 48px; border-top: 1px solid var(--rule);
    padding-top: 16px; font-size: 13px; color: var(--muted);
  }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="kicker">{group}</div>
    <h1>A {mw} MW data center is proposed near us.</h1>
    <p class="sub">We're not against growth — we're for conditions.
    Here's what this facility means for {esc(state)} households, using
    planning-level estimates.{op_line}</p>
  </header>

  <div class="stats">
    <div class="stat"><b>{homes}</b><span>homes' worth of electricity
    ({twh} TWh/yr)</span></div>
    <div class="stat"><b>{water}</b><span>gallons of cooling water per
    year</span></div>
    <div class="stat"><b>{bill}</b><span>per household per year if
    ratepayers fund the grid upgrades</span></div>
    <div class="stat"><b>{cba}</b><span>per year — the community benefit
    agreement we should ask for</span></div>
  </div>

  <section>
    <h2>What we're asking for — before any approval</h2>
    <ul>
      <li>A <strong>binding community benefit agreement</strong>
      (~{cba}/year), recorded as a condition of approval — not a side
      letter.</li>
      <li>The developer pays <strong>100% of grid upgrades</strong>, so
      they never appear on our electric bills.</li>
      <li>An <strong>enforceable water cap</strong>, a 45 dBA noise limit
      at homes, and quarterly public reporting.</li>
      <li>A <strong>decommissioning bond</strong> so the site isn't
      abandoned scrap if the operator leaves.</li>
    </ul>
  </section>

  <section class="prec">
    <h2>Communities that organized, won</h2>
    <ul>
      <li><b>The Dalles, OR</b> — Google funded a $29M wastewater upgrade
      and the city capped data-center water draws.</li>
      <li><b>Groton, CT</b> — a $2.5M community benefit agreement became a
      zoning condition after a year-long moratorium.</li>
      <li><b>Morrow County, OR</b> — commissioners reopened Amazon's tax
      deals and won higher annual community payments.</li>
    </ul>
    <p class="muted">Every one of these happened <em>before</em> final
    approval. Timing is the leverage.</p>
  </section>

  <section>
    <div class="meeting">
      <div class="kicker">Show up</div>
      <div class="when">{when}</div>
      <div>{where}</div>
      {contact}
    </div>
  </section>

  <footer>
    Estimates are planning-level, generated with the GridWatch AI impact
    model (grid data by state, PUE/water by cooling type). They are not
    engineering studies. Page produced by {group}.
  </footer>
</div>
</body>
</html>
"""
