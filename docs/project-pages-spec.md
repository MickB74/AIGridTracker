# Spec: one crawlable page per tracked project (`/projects/<id>`)

Written 2026-10-11 for an implementing agent. Everything you need is in this
file plus `CLAUDE.md` at the repo root. Read `CLAUDE.md` first — its rules on
`has_value()`, `NEWS_FREEZE=1`, committed `web/`, clean URLs and the build
guard all apply here and are not repeated in full.

## Why

Search Console, Aug 5 to Oct 9 2026 (3 months, Web search):

| Page | Clicks | Impressions | CTR |
|---|---|---|---|
| `/projects` | 95 | 71,568 | 0.13% |
| `/communities/grant-county-in` | 13 | 172 | 7.6% |
| `/communities/cass-county-in` | 5 | 80 | 6.3% |
| Site total | 410 | 134K | 0.3% |

More than half of all impressions land on the single `projects.html` page,
which ranks for project-name queries ("project parrot data center",
"marshalltown data center", "stack infrastructure danville va") but converts
at a tenth of a percent. A searcher sees a 285-row national table in the
result instead of their project. Community pages, which are one page per
locality, convert at 6 to 8 percent. The fix is the same shape: one page per
project, with a title, description and H1 that match the query, served at a
stable URL, and linked from everywhere the project is currently anchored.

## Scope

1. A new builder `build_project_page(p, news_group=None)` in `build_site.py`
   that renders `web/projects/<id>.html` for every row in `PROJECTS`.
2. `web/projects/index.html` is NOT created. `projects.html` stays the index
   and keeps its URL (`/projects`), because that is the URL holding the
   ranking. Vercel's `cleanUrls` serves `/projects` from `projects.html` and
   `/projects/<id>` from `projects/<id>.html` with no conflict; verify this
   locally with `scripts/serve_web.py` (see Verification).
3. Every existing `#p-<id>` anchor link on the site is repointed at the new
   page.
4. The dossier section on `projects.html` is slimmed to a card per project
   that links to the full page, so the index page stops duplicating 285 full
   dossiers (it is currently the page's bulk) and the per-project page is the
   canonical home of that content.
5. Sitemap, search index, build guard, OG image, breadcrumb and `llms.txt`
   wiring.
6. Rebuild `web/`, run the freshness check, commit `src/`, `build_site.py`,
   `data/` and `web/` together.

Out of scope: changing `data/projects.json`, the schema, `project_status()`,
or any registry. Do not add, edit or delete project rows. Do not touch the
moratorium or community builders except to change link targets.

## Where things are (verified 2026-10-11)

All line numbers are in `build_site.py` unless stated.

| Thing | Location |
|---|---|
| `build_projects()` — the index page | ~line 9887 |
| `_project_dossier(p)` — the per-project card rendered 285 times into the index | ~line 9776 |
| `_project_paper_trail(p)` — the "Find the paper trail" block | ~line 9732 |
| `_project_timeline(events)` — event log HTML | ~line 9713 |
| `_project_builder`, `_project_size`, `_project_stage_cell`, `_project_source_cell`, `_project_sort_key` | ~lines 9659 to 9704 |
| `_status_badge(stage)` | grep for `def _status_badge` |
| `_state_href(abbrev)` — `states/<slug>.html` or `""` | ~line 9806 |
| `_loc_slug(locality, state)` — community slug | ~line 8847 |
| `_local_projects_section_html(locality, state)` — community page's project section, links to `../projects.html#p-<id>` | ~line 8866, link at ~line 8915 |
| State page project table, links to `../projects.html#p-<id>` | ~line 2164 |
| Map page popup JS, links to `projects#p-<id>` | ~line 10321 |
| `build_community(m, news_group)` — the reference implementation for a per-entity page | ~line 9083; its `page()` call at ~line 9220 |
| `_story_news_section_html(group, heading)` — "Recent news" block from the story archive | ~line 8997 |
| `_groups_by_locality` — dict `(clean_locality, state) -> story group`, computed in `main()` | ~line 16721 |
| `page(title, description, body, canonical, depth, og_image, jsonld, modified, ...)` | ~line 1049 |
| `_breadcrumb(...)`, `_og_image(name)` | `_og_image` at ~line 1031 |
| `provenance_html("PROJECTS_DF")` | `src/constants.py` ~line 9215 holds the entry |
| `main()`: `projects.html` written at ~line 16785; community loop at ~lines 16832 to 16849; `paths` list for sitemap at ~line 16885; `expected_dirs` build guard at ~line 17111 |
| `build_search()` — the search index | ~line 15392 |
| `build_llms_txt()` | grep for `def build_llms_txt` |
| `project_status(row)` | `src/constants.py`, grep `def project_status` |
| `PROJECTS`, `PROJECTS_DF`, `PROJECT_EVENTS` | imported from `src/constants.py` at line ~50 |

Data facts you can rely on:

- `data/projects.json` has 285 rows under the `projects` key. Every `id` is
  unique and already matches `^[a-z0-9-]+$`, so `id` is the URL slug with no
  transformation. 284 of 285 have a `source`. 246 have at least one event.
  57 rows are `origin: "pa-dep"` (machine-synced from PA DEP, sparse notes).
- `outcome` values: `approved`, `denied`, `withdrawn`, `moratorium`, or null
  (226 rows). Stage is derived by `project_status()`; read it, never read
  `outcome` directly for display.
- Row fields: `id, name, operator, owner, tenant, filing_llc, locality,
  state, lat, lon, size_mw, acres, announced, rezoning_filed, hearing_date,
  decided_date, outcome, note, source, as_of, events, origin, pa_dep_*`.
  Any of these can be null or NaN. Use `has_value()` for every test.

## The page

### URL and file

- File: `web/projects/<id>.html`. Canonical: `{SITE_URL}/projects/<id>`.
  `depth=1` in `page()` so relative links get `../`.
- Add `"projects"` to `expected_dirs` in the build guard or the build fails.
- Do not create `web/projects/index.html`.

### `<title>` (SERP title, 60 char cap via `_seo_clip`)

Follow the fallback ladder pattern in `build_community()` (~line 9212).
Try, in order, the first form that fits in 60 characters:

1. `{name} data center — {locality}, {ST}: {stage}`
2. `{name} data center — {locality}, {ST}`
3. `{name} data center — {ST}`
4. `{name} data center`

`stage` is `project_status(p)["stage"]`. If `name` already contains the
words "data center" or "Data Center" (case-insensitive), drop the literal
"data center" from the template to avoid "X Data Center data center".

### Meta description (155 cap)

One sentence a resident would click: who is building what, where, and what
happens next. Build it from fields that exist; never emit "None" or "nan".
Example shape:

> `{builder} proposes a {size} data center in {locality}, {State}. {stage}. {next_action first clause}. Sources, timeline and where to find the permit file.`

Where `builder` is the first non-null of operator, owner, filing_llc (reuse
`_project_builder` but strip HTML, or write a plain-text twin), `size` is
"{N} MW" or "{N}-acre" or omitted, `State` is the full state name from
`_abbr_to_state()`.

### H1 and header

```
<header>
  <div class="kicker">Project dossier · {locality}, {State}</div>
  <h1>{name} {status badge}</h1>
  <p class="sub">{note, if has_value, else a generated one-liner from the same fields as the description}</p>
</header>
```

### Body sections, in order

1. **Key facts** — a `<dl>` or two-column list: Operator, Owner, Tenant,
   Filing LLC (only those with a value), Size (MW and/or acres), Location
   (locality + link to state page via `_state_href`, with `../` prefix),
   Announced, Application filed, Hearing date, Decided, Stage. Each date only
   if present. Stage uses `_status_badge`.
2. **What to do next** — `<p class="next"><strong>Next step:</strong>
   {status["next_action"]}</p>`. If `status["hearing_soon"]`, wrap in
   `<div class="note warn">`. Then one line linking to
   `../start-here.html` ("Build an action pack for this project").
3. **Source** — `_project_source_cell(p)` plus `as_of`. If no source, render
   the same *Unverified* warning block the community page uses (~line 9104),
   verbatim wording.
4. **Intelligence log** — `_project_timeline(events)` rendered OPEN, not in a
   `<details>`. On the index page it is collapsed because 285 of them stack;
   on its own page the timeline is the content and must be visible to Ctrl-F,
   print and crawlers. Heading: "What has happened so far ({n} events)". If
   no events, omit the section.
5. **Find the paper trail** — `_project_paper_trail(p)` as-is. Check that its
   hrefs are absolute or relative to root; if it emits `href="foo.html"`
   relative links, prefix `../`. Grep its body for `href="` and test one
   rendered page.
6. **Recent news** — `_story_news_section_html(news_group)` when `main()`
   can find a story group for `(story_tracker.clean_locality(locality),
   state)` in `_groups_by_locality`. Pass it the same way the community loop
   does. Omit the section when there is no group.
7. **This community** — if `MORATORIUMS_DF` has a row with the same
   `(locality, state)` (match on the base name before any `(` the way
   `_local_projects_section_html` does, both directions), link to
   `../communities/{_loc_slug(locality, state)}.html` with the moratorium's
   `effective_status`. Also link the state briefing. Also link up to five
   other tracked projects in the same state (nearest by lat/lon when both
   have coordinates, otherwise alphabetical), each to its own new page. This
   is the internal-link mesh that lets Google discover 285 new pages fast.
8. **Footer block** — `provenance_html("PROJECTS_DF")` and the "Part of the
   project tracker, open data CC BY 4.0" line linking `../projects.html`
   and `../data/projects.json`.

### `page()` call

```python
return page(
    title_full, description, body,
    f"{SITE_URL}/projects/{pid}", depth=1,
    modified=BUILD_DATE,
    og_image=_og_image(f"state-{state_slug}"),   # reuse the state card; no new PNGs
    jsonld=_breadcrumb(
        ("Home", SITE_URL),
        ("Projects", f"{SITE_URL}/projects"),
        (p["name"], f"{SITE_URL}/projects/{pid}")))
```

Do not generate new OG images. `scripts/make_og_images.py` needs Pillow,
which is deliberately absent from the build environment. The state card is
the right fallback and is what community pages already use.

### JSON-LD

`_breadcrumb` is enough. Do not add an `Event` or `Place` schema; a hearing
date is not an event listing and Google penalises mismatched event markup.

## Changes to existing code

### `build_projects()` (the index)

- Replace the full `_project_dossier(p)` per row with a compact card: name
  (linked to `projects/{id}.html`), badge, locality/state, builder, size,
  next action, source cell. No timeline, no paper trail. Keep the
  `id="p-{id}"` attribute on the card so any external deep link someone has
  bookmarked still scrolls to the right place.
- Keep the table's name cell linking to `#p-{id}` OR change it to
  `projects/{id}.html`. Change it: the table is the first thing a reader
  sees and the full page is now where the answer is.
- Keep `_project_dossier()` defined; it is still useful and deleting it is
  not in scope. If after the change nothing calls it, delete it and say so
  in the commit message.
- Update the "Project dossiers" section intro text to say each project now
  has its own page.
- Update the `#records` section's sentence "Every dossier above ends with
  **Find the paper trail**" to point at the per-project pages.

### Repoint the three `#p-` anchors

| Where | From | To |
|---|---|---|
| state page table ~line 2164 | `../projects.html#p-{id}` | `../projects/{id}.html` |
| `_local_projects_section_html` ~line 8915 | `../projects.html#p-{id}` | `../projects/{id}.html` |
| map popup JS ~line 10321 | `projects#p-'+esc(p.id)` | `projects/'+esc(p.id)` (the JS string is inside Python; the map page is at root depth; check whether the surrounding code applies `_clean_links` to JS strings — it does not, so write the extensionless form here and only here, with a comment saying why) |

Grep for any other `#p-` after that: `grep -n '#p-' build_site.py`.

### `main()`

After `projects.html` is written (~line 16785):

```python
(WEB / "projects").mkdir(parents=True, exist_ok=True)
_project_paths = []
for _p in PROJECTS:
    _pid = str(_p["id"])
    _pg = _groups_by_locality.get(
        (story_tracker.clean_locality(str(_p.get("locality", ""))), str(_p.get("state", ""))))
    (WEB / "projects" / f"{_pid}.html").write_text(
        build_project_page(_p, news_group=_pg), encoding="utf-8")
    _project_paths.append(f"projects/{_pid}")
print(f"  [pages] {len(_project_paths)} project pages -> projects/")
```

Check that `_groups_by_locality` is computed before this point in `main()`
(it is computed at ~line 16721, before the community loop; the projects
write at ~16785 is after it, so the order is fine, but confirm after you
move code).

Then `paths.extend(_project_paths)` next to `paths.extend(_community_paths)`
so every page enters the sitemap and the lastmod hash file.

### `build_search()`

Add one index entry per project:

```python
for p in PROJECTS:
    s = project_status(p)
    index.append({"t": str(p.get("name")), "k": "project",
                  "d": f"{p.get('locality')}, {p.get('state')} · {s['stage']}",
                  "u": f"projects/{p['id']}"})
```

Check how the search page renders `k` (there may be a label map) and add
"project" to it if needed.

### `build_llms_txt()`

Add one line under the projects entry saying that each project has its own
page at `/projects/<id>` and that the full list is in `/data/projects.json`.
Do not list 285 URLs in `llms.txt`.

### `data/retired_paths.json`

Nothing to retire; `/projects` stays live. The build's automatic
retirement logic compares the previous sitemap to the new one and will see
285 additions and zero removals. Confirm the build log prints no retired
paths.

### `CLAUDE.md`

Add a bullet under "Pages built" for the per-project pages and a one-line
gotcha under "Site build gotchas": `projects.html` and `projects/` coexist
under cleanUrls; never create `projects/index.html`.

## Verification

Run in this order. All must pass before committing.

1. Syntax and build:

   ```bash
   python3 -m py_compile build_site.py src/constants.py && NEWS_FREEZE=1 python3 build_site.py
   ```

   Expect the page count in the build output to rise by 285. Expect the
   build guard not to fire.

2. Spot-check three rendered pages with distinct shapes:
   - `web/projects/pw-digital-gateway-va.html` (terminal, withdrawn, many events)
   - any `origin: "pa-dep"` row (sparse: no note, no operator, permit events only)
   - the row with no `source` (find it: `python3 -c "import json;print([r['id'] for r in json.load(open('data/projects.json'))['projects'] if not r.get('source')])"`)

   For each: `<title>` is 60 chars or fewer and contains the project name;
   description contains no "None", "nan" or "—" artefacts; every `href`
   that starts with `../` resolves to a file under `web/`; the timeline is
   not inside a closed `<details>`; the breadcrumb JSON-LD has three items.

3. Link integrity across the whole output:

   ```bash
   grep -rl '#p-' web/*.html web/states web/communities web/map.html 2>/dev/null
   ```

   The only remaining hits should be `projects.html` itself (the card ids).

4. Clean-URL coexistence. Start the preview server from
   `.claude/launch.json` (`static-site`, port 8777) and fetch:
   `http://localhost:8777/projects` (must be the index) and
   `http://localhost:8777/projects/pw-digital-gateway-va` (must be the
   dossier). Both must return 200 with the right H1. If
   `scripts/serve_web.py` resolves `/projects` to the directory instead of
   the file, fix the server to prefer `<path>.html` over `<path>/` — that is
   what Vercel does.

5. Freshness gate:

   ```bash
   python3 scripts/check_site_fresh.py --strict
   ```

6. Size check: `du -sh web/projects` and `ls -la web/projects.html`. The
   index page should shrink noticeably (it currently carries every dossier).
   Report both numbers in the commit message.

## Commit

One commit containing `build_site.py`, `CLAUDE.md`, `data/sitemap_hashes.json`
(the build rewrites it), and all of `web/`. Message:

```
feat: one page per tracked project at /projects/<id>

/projects draws 53% of site impressions at 0.13% CTR; community pages
convert at 6-8%. Each of the 285 projects now has its own crawlable page
with the full dossier; projects.html keeps its URL as the index.

- build_project_page(): title ladder, key facts, open timeline, paper
  trail, story-archive news, sibling-project mesh, breadcrumb
- #p- anchors on state, community and map pages repointed
- sitemap, search index, llms.txt, build guard updated
- projects.html: <before> KB -> <after> KB

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
```

Do not push unless the user has said to. Do not refresh news
(`NEWS_REFRESH`) in this commit.

## Things that will go wrong if you skip them

- **`has_value()` on every field.** `NaN` is truthy. A `nan` in a `<title>`
  will ship. This is the single most repeated bug in this repo.
- **`depth=1`.** Every internal link in the body needs `../`. The paper trail
  and timeline helpers were written for a root-level page; test their output
  on a subpage.
- **`expected_dirs`.** The build guard raises `SystemExit` on an unknown
  directory under `web/`. Add `"projects"` before the first build.
- **`NEWS_FREEZE=1`** on every rebuild, or ~35 unrelated files churn.
- **Do not hand-edit `web/`.** It is regenerated.
- **Do not write `projects/index.html`.** It would shadow `projects.html`
  under some static servers and split the ranking URL.
- **Keep per-page `<style>` inline** if you need any; the shared `CSS`
  constant is hashed into one file and a change there rewrites every page's
  `<head>` (expected, but keep it out of this commit unless you need it).

---

# Part 2: backlinks

## Where we stand (Search Console Links report, read 2026-10-11)

| Metric | Value |
|---|---|
| External links, total | 8 |
| Linking sites | 5 |
| Internal links | 23,309 |

The five linking sites and what they are:

| Site | Links | What it is |
|---|---|---|
| streamlit.app | 3 | Our own retired app. Dead value: self-referential, and the app no longer exists. |
| globaldatacenters.net | 1 | Unknown directory. Check whether the link is live and `dofollow`. |
| gridglasses.com | 1 | Unknown. Same check. |
| note.com | 1 | Japanese blogging platform. Almost certainly `nofollow`. |
| substack.com | 1 | A newsletter cited us. Find which one; it is a warm outreach target. |

Top linked pages: `/projects` (2), `/blog`, `/companies`, `/moratoriums`,
`/senators` (1 each). Anchor text includes "ai grid watch minnesota
legislative & municipal profile", so at least one link points at a
Minnesota page.

Read plainly: after two months, effectively zero external authority. The
plan in `docs/backlink-campaign.md` and the copy in
`docs/outreach-ready.md` exist but none of the checkboxes are ticked and
nothing in the report suggests any of it was sent. All the impressions
growth so far is from content and internal linking alone, which is good
news about the content and bad news about the ceiling.

## What the implementing agent can do without a human

Everything in this list is self-serve and reversible. Do all of it. Each
item ends with how to prove it was done.

### B1. Fix the stale numbers in the outreach copy

`docs/backlink-campaign.md` and `docs/outreach-ready.md` say "99
moratoriums" six times. The README says 333. The registry has 386 rows.
Write a stdlib-only script, `scripts/outreach_counts.py`, that prints the
live counts (moratorium rows, states covered, projects tracked, community
pages, senators, house districts) from `src/constants.py` and
`data/*.json`, then replace every hard-coded count in both docs and the
README with the current values. Leave a comment line at the top of each
doc saying counts come from that script. Proof: `grep -n " 99 " docs/*.md`
returns nothing.

### B2. GitHub awesome-list pull requests

Four targets are listed in `docs/outreach-ready.md` section 1 with the
exact list item and PR body. For each: fork with `gh repo fork`, add the
line under the named section, open the PR with `gh pr create`. Use the
corrected counts from B1. Paste the four PR URLs into
`docs/backlink-campaign.md` next to their checkboxes and tick them. Proof:
the four URLs.

Do this only if the user has confirmed the agent may open public pull
requests from their GitHub account. If not confirmed, prepare the four
branches and stop before `gh pr create`, and say so.

### B3. GitHub repo hygiene

- Add repository topics with `gh repo edit --add-topic`: `data-centers`,
  `open-data`, `civic-tech`, `energy`, `moratorium`, `community-benefits`.
- Set the repo homepage to `https://aigridwatch.com` with
  `gh repo edit --homepage`.
- Add `CITATION.cff` at the repo root so GitHub shows a "Cite this
  repository" box; `url` and `repository-code` fields point at the site and
  the repo. This is what gets picked up by academic reference managers and
  is the cheapest `.edu` pathway there is.

Proof: `gh repo view --json repositoryTopics,homepageUrl`.

### B4. Dataset listings

Upload `web/data/moratoriums.csv` and `web/data/projects.csv` to
data.world and Kaggle with the homepage field set to the tracker page and
license CC BY 4.0. These need the user's accounts, so prepare the title,
description and tag text in `docs/outreach-ready.md` section 1 and leave a
checkbox for the user. Do not create accounts.

### B5. Make the per-project pages the link bait

This is why Part 1 and Part 2 are in one spec. Journalists and local
organisers link to the page about *their* project, not to a national
table. Once `/projects/<id>` exists:

- Add an "Embed or cite this page" line at the bottom of each project
  page with a ready-to-paste citation: `GridWatch AI, "<name>",
  aigridwatch.com/projects/<id>, retrieved <date>`. Copy the pattern from
  the moratoriums embed (`web/embed/moratoriums.html`) only if it is
  cheap; a plain `<p>` is enough.
- Add a `Dataset` JSON-LD entry on `projects.html` for the projects
  download, mirroring whatever `build_moratoriums()` already emits for
  the moratorium data (grep `"@type": "Dataset"` in `build_site.py`).
  Google Dataset Search is a real discovery channel and the moratorium
  tracker already qualifies.

### B6. Outreach list for the user, not for the agent

Build `docs/outreach-queue.md`: a table of the top 25 targets with, per
row, the organisation, the specific URL on our site that is most relevant
to them, the person or inbox if it is public on their own site, and the
one-sentence pitch. Prioritise in this order, because it tracks where
clicks are actually coming from:

1. The substack that already linked us (find it: search
   `site:substack.com "aigridwatch"`). Reply, thank, offer a per-project
   page for anything they cover next.
2. Local reporters who wrote the stories in `data/story_candidates.json`
   for the top-clicking localities: Grant County IN, Cass County IN,
   Marshalltown IA, Lake Elsinore CA, Danville VA, Walker County. The
   story archive has the outlet and headline; the pitch is "your readers
   are searching for this project and landing on our page; here is a
   sourced timeline you can link".
3. The three peer trackers in `docs/backlink-campaign.md` section D
   (cross-link offers are the fastest editorial links).
4. State municipal leagues for IN, VA, IA, CA, GA (from
   `STATE_MUNI_LEAGUES`).

The agent does not send any of this. Sending is the user's call; see
`docs/outreach-ready.md` for the email copy.

## What to tell the user when done

Report, in this order: the before and after `projects.html` size, the
page count, the four PR URLs or the reason they were not opened, the
`gh repo view` output, and the path to `docs/outreach-queue.md`. Then
say that the external link count is 8 and that nothing in this work
changes that number until the outreach is sent.
