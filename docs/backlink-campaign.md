# Backlink Campaign — AI GridWatch

*Working sheet. Check off as you go. Grounded in real, current targets (Aug 2026).*

**Honest read on link value:** self-serve links (GitHub, Reddit, forums, most
directories) are usually `nofollow` — they drive **referral traffic + discovery**
but don't pass ranking authority. The links that actually move rankings are
**editorial** (a journalist links you in a story) and **institutional**
(`.gov` / `.edu` / think-tank resource pages). Do the self-serve tier this week
because it's fast and in your control; run the outreach tier in parallel because
that's the SEO payoff.

Reusable one-liner for every submission:
> **AI GridWatch** (aigridwatch.com) — free, sourced tools for communities facing
> a data center proposal: an impact calculator, model CBA language, a health-risk
> briefing, and a moratorium tracker of 99 community actions with per-row sources,
> published as open CC BY 4.0 data.

---

## Tier 1 — Self-serve, do this week (you control these)

### Open-dataset lists (your new `Dataset` schema makes this legit)
The moratorium tracker is genuine open data now — JSON + CSV, per-row sources,
CC BY 4.0. That earns a listing on data lists that reject marketing pages.

- [ ] **awesomedata/awesome-public-datasets** — PR to the *Politics* or *Energy*
  section. https://github.com/awesomedata/awesome-public-datasets
- [ ] **rebase-energy/awesome-energy-datasets** — PR.
  https://github.com/rebase-energy/awesome-energy-datasets
- [ ] **open-energy-transition/Awesome-Grid-Model-Data** — PR.
  https://github.com/open-energy-transition/Awesome-Grid-Model-Data
- [ ] **OpenEnergyPlatform/awesome-sustainable-technology** — PR.
  https://github.com/OpenEnergyPlatform/awesome-sustainable-technology
- [ ] **data.world** and **Kaggle Datasets** — upload the moratoriums CSV with a
  description linking back to aigridwatch.com/moratoriums as the source.

**Copy-paste PR entry (markdown list item):**
```
- [U.S. Data Center Moratorium Tracker](https://aigridwatch.com/moratoriums) — 99
  data center moratoriums, bans, and community actions across the U.S., each with a
  primary source, verification date, and derived expiry status. Open JSON/CSV,
  CC BY 4.0.
```

### ~~Streamlit ecosystem~~ — DEAD, do not pursue
The Streamlit app was retired in August 2026 and the product is now a static
site, so every gallery target here (best-of-streamlit, the "Show the
Community!" forum, streamlit.io/gallery) requires a hosted Streamlit app we no
longer have. Struck rather than deleted so nobody re-adds them.

### Dev / civic-tech communities (traffic + secondary pickups)
- [ ] **Hacker News — Show HN**, framed around the *open data*, not the politics:
  "Show HN: Open dataset of every U.S. data center moratorium, with sources."
- [ ] **dev.to** / **Medium** — cross-post one build writeup ("How I built a
  self-updating open dataset of data center fights") with canonical link home.
- [ ] **Product Hunt** — launch the toolkit as a free civic tool.
- [ ] **GitHub repo** — make sure the README links aigridwatch.com prominently;
  add topics (`data-centers`, `open-data`, `civic-tech`) so it surfaces in search.

---

## Tier 2 — Outreach (this is where SEO authority comes from)

Run 5–10 sends/week. Warm targets, non-salesy, value-first. Emails below.

### A. Municipal leagues & planning associations (`.org`, high-trust)
Their "resources for members" pages are ideal — an official can adopt you
publicly. Start with states that have active fights.
- [ ] State municipal leagues (49 exist; see `STATE_MUNI_LEAGUES` in the repo)
- [ ] American Planning Association chapters
- [ ] National Association of Towns and Townships (NATaT)

### B. Established watchdogs & explainer orgs (topical authority)
They have audience + no tools; you have tools + their exact topic.
- [ ] **Good Jobs First** — subsidy/CBA watchdog. goodjobsfirst.org
- [ ] **Data Center Playbook** — datacenterplaybook.org (citizens guide)
- [ ] **NAACP "Stop Dirty Data Centers"** — naacp.org campaign

### C. Journalists on the beat (editorial = the best links)
Rapid-response is the play: when a local fight hits the news, email the reporter
*same day* with a sourced stat + the tracker link. Your news feed surfaces the
triggers daily.
- [ ] Heatmap News, Canary Media, Data Center Dynamics, Grist
- [ ] The local/regional reporter on each new proposal (from the news feed)

### D. Peer trackers — cross-links (fast, friendly)
The opposition ecosystem cross-links freely. Offer a reciprocal "related
resources" mention. These are real, active as of mid-2026:
- [ ] FloridaDataCenters.org (50-state opposition tracker)
- [ ] AsimovGrid opposition dashboard — dctracker.asimovgrid.com
- [ ] jwklee Data Center Opposition Tracker (jwklee.github.io)
- [ ] Robert Bryce's "AI Rejected" Substack series

### E. Wikipedia (nofollow, but huge referral + authority signal)
Add your tracker/methodology as a citation where it genuinely supports a claim —
never as promotion.
- [ ] "Data center" article — environmental/community-impact section
- [ ] "Environmental impact of artificial intelligence"
- [ ] State "data center" articles as they appear

---

## Email templates

### Template 1 — Municipal league / planning association
> **Subject:** Free sourced data-center resource for your members
>
> Hi [name],
>
> I run AI GridWatch (aigridwatch.com), a free, non-commercial resource for
> communities weighing a data center proposal. It's deliberately *not* anti-
> development — it's built to help officials negotiate a better deal: an impact
> calculator, model CBA language, and a tracker of 99 community actions, every
> number linked to a primary source (EIA, SEC, IEA).
>
> A lot of [state] towns are getting proposals with no staff expertise to
> evaluate them. If it's useful to your members, would you consider adding it to
> your data-center resources page? Nothing to sign up for, nothing to buy.
>
> Happy to send a one-pager. Thanks for the work you do for [state] communities.
>
> [You]

### Template 2 — Journalist rapid-response
> **Subject:** Sourced numbers on the [Town] data center fight
>
> Hi [name] — saw your piece on the [Town] proposal. I run a free tracker of
> data-center community actions (aigridwatch.com) and can save you time on the
> numbers: at [X] MW this facility would draw roughly [Y] MWh/yr and [Z] gallons
> of water — every figure sourced, and I can walk you through the rate-impact
> math on background if useful.
>
> The moratorium data is open (CC BY 4.0) if you ever want to chart it. No ask —
> just here if it helps the beat.
>
> [You]

### Template 3 — Watchdog / peer org partnership
> **Subject:** GridWatch tools + your audience?
>
> Hi [name] — big admirer of [org]'s work on [CBAs / subsidies / EJ]. I've built
> the operational layer that pairs with it: a free impact calculator, a data
> dividend model, and an open, sourced moratorium dataset. You have the audience
> and credibility; I have tools and no reach yet.
>
> Would a reciprocal resource link make sense — you point members to the tools,
> I point users to your guidance? Open to whatever's useful.
>
> [You]

---

## Track it

| Target | Tier | Status | Link live? | Date |
|---|---|---|---|---|
| awesome-public-datasets | 1 | | | |
| ~~best-of-streamlit~~ | — | n/a — app retired | | |
| Show HN | 1 | | | |
| [muni league] | 2A | | | |
| Good Jobs First | 2B | | | |
| [reporter] | 2C | | | |

**Goal (from marketing plan):** 10 citing domains in 90 days. Editorial +
institutional links count double — chase those.
