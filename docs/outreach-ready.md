# Outreach — ready to send

*Filled-in, copy-paste assets. Companion to `backlink-campaign.md`.*

---

## 1. GitHub awesome-list PRs

Same flow for each: fork → add one line in the right section → PR. Suggested
PR title and body below the entries.

**List item to add** (drop into the Energy / Environment / Politics section):
```markdown
- [U.S. Data Center Moratorium Tracker](https://aigridwatch.com/moratoriums) — 99 data center moratoriums, bans, and community actions across the U.S., each with a primary source, verification date, and derived expiry status. Open JSON/CSV, CC BY 4.0.
```

**Targets & best section:**
| Repo | Section to add under |
|---|---|
| [awesomedata/awesome-public-datasets](https://github.com/awesomedata/awesome-public-datasets) | Energy · or · Politics |
| [rebase-energy/awesome-energy-datasets](https://github.com/rebase-energy/awesome-energy-datasets) | Grid / demand |
| [open-energy-transition/Awesome-Grid-Model-Data](https://github.com/open-energy-transition/Awesome-Grid-Model-Data) | Demand / load |
| [OpenEnergyPlatform/awesome-sustainable-technology](https://github.com/OpenEnergyPlatform/awesome-sustainable-technology) | Data / Tools |

**PR title:** `Add U.S. Data Center Moratorium Tracker (open dataset)`

**PR body:**
> Adds the U.S. Data Center Moratorium Tracker — an open, sourced dataset of 99
> data center moratoriums and community actions across the U.S. Each row carries
> a primary source, a verification date, and a derived expiry status. Published
> as JSON and CSV under CC BY 4.0, with a documented schema.
>
> - Dataset page: https://aigridwatch.com/moratoriums
> - JSON: https://aigridwatch.com/data/moratoriums.json
> - CSV: https://aigridwatch.com/data/moratoriums.csv
>
> It fills a gap — there's structured, cited data on community responses to data
> center siting that isn't otherwise collected in one place. Happy to adjust
> categorization to fit the list's conventions.

**Also upload the CSV to:** [data.world](https://data.world) and
[Kaggle Datasets](https://www.kaggle.com/datasets) — set the source/homepage
field to `https://aigridwatch.com/moratoriums` and license to CC BY 4.0.

---

## 2. Show HN

**Title:**
> Show HN: Open dataset of every U.S. data center moratorium, with sources

**Text (first comment):**
> I've been tracking community responses to data center siting — moratoriums,
> bans, zoning fights — and kept hitting the same wall: the data exists in
> scattered news stories but nobody publishes it structured and sourced. So I
> built a tracker: 99 actions across the U.S., each with a primary source, a
> verification date, and a status that expires on its own once a moratorium's
> documented term runs out (so the page can't keep asserting a lapsed pause is
> still in force).
>
> It's open — JSON and CSV, CC BY 4.0, documented schema:
> https://aigridwatch.com/moratoriums
>
> The tracker is one piece of a free toolkit for communities facing a proposal —
> an impact calculator, model CBA language, a sourced health-risk briefing. The
> whole thing is deliberately not anti-development; it's built so a town can
> negotiate a better deal instead of just fighting. Every number links to its
> source (EIA, SEC, IEA). Code is MIT: https://github.com/MickB74/AIGridTracker
>
> Happy to talk about the data model — especially the "derive status, never
> store it" pattern, which turned out to matter a lot for correctness.

*Post Tue–Thu, ~8–10am ET. Reply to every comment in the first two hours.*

---

## 3. dev.to / Medium cross-post

**Title:** How I built a self-updating open dataset of U.S. data center fights

**Canonical URL (set in dev.to front-matter):** `https://aigridwatch.com/moratoriums`

**Angle / outline:**
1. The problem — community data center actions are real news but unstructured;
   no citable dataset exists.
2. The correctness bug that shaped the design: storing "Enacted" means a page
   asserts a lapsed moratorium forever. The fix — **derive time-sensitive status,
   never store it**: store the end date, compute the current state with a pure
   function, and a daily CI rebuild self-corrects with no edit.
3. Provenance as a first-class field — per-row `source` + `as_of`; unsourced
   rows render as *Unverified*, never as fact.
4. Shipping it as open data — `Dataset` schema.org markup → Google Dataset
   Search, JSON + CSV, CC BY 4.0.
5. Close with the live dataset + repo link.

*This doubles as engineering credibility and a backlink. Keep it technical —
the audience is developers, not activists.*

---

## 4. Municipal-league emails (top 5 states by active fights)

Send via each league's contact/press page (linked). Replace `[name]` with the
policy or member-services contact you find there. Keep it short.

### North Carolina — 21 tracked actions
**League:** North Carolina League of Municipalities — https://www.nclm.org/
> **Subject:** Free, sourced data-center resource for NC municipalities
>
> Hi [name],
>
> 21 North Carolina communities are already navigating data center proposals —
> more than any other state in the tracker I maintain at aigridwatch.com. It's a
> free, non-commercial resource: an impact calculator, model CBA language, and a
> sourced moratorium tracker, every number linked to a primary source.
>
> It's deliberately not anti-development — it's built to help officials
> negotiate a better deal. If it's useful to your members, would you consider
> adding it to your resources? Nothing to buy, nothing to sign up for. Happy to
> send a one-pager.
>
> Thanks for the work you do for NC towns.
> [You]

### Georgia — 8 tracked actions
**League:** Georgia Municipal Association — https://www.gacities.com/
*(Same body; open with:)* "Eight Georgia communities are already navigating data
center proposals, and GMA members are often the first to field them…"

### New York — 8 tracked actions
**League:** NY State Conference of Mayors (NYCOM) — https://www.nycom.org/
*(Open with:)* "With the state moratorium activity of the past year, NY mayors
are fielding data center questions with little staff support…"

### New Jersey — 6 tracked actions
**League:** New Jersey State League of Municipalities — https://www.njlm.org/
*(Open with:)* "Six New Jersey communities are already weighing data center
proposals…"

### Florida — 5 tracked actions
**League:** Florida League of Cities — https://www.flcities.com/
*(Open with:)* "Five Florida communities are already navigating data center
proposals, and the pace is picking up…"

*Full 49-state league list is in `STATE_MUNI_LEAGUES` (src/constants.py) when
you're ready to widen the campaign.*
