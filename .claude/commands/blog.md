---
description: Research and publish one GridWatch AI blog post from the story archive
argument-hint: "[optional topic or locality to write about]"
allowed-tools: Bash, Read, Edit, Grep, Glob, WebSearch, WebFetch, TodoWrite
---

# Write and publish one blog post

Produce **one** post for the GridWatch AI blog, add it to `BLOG_STORIES` in
`src/blog_content.py`, rebuild the site, and push it live.

If `$1` is given, write about that. Otherwise pick the topic yourself from
step 1.

**Publishing nothing is a valid outcome.** If no topic clears the sourcing bar
in step 3, stop and say so. A thin post on a quiet news day is worse than a
gap — this site's whole claim is that every number links to the document it
came from.

## 1. Pick a topic

Look at what actually moved, in this order of preference:

1. **Your own registries.** A moratorium row added or changed in the last
   week, a new PA DEP permit in `data/projects.json`, a term about to expire,
   a race record just researched. These are the strongest posts because the
   underlying data is already verified and already on the site to link to.

   ```bash
   git log --since="10 days ago" --oneline -- src/constants.py data/projects.json src/senate_races.py src/house_races.py
   ```

2. **The story archive** — `data/story_candidates.json`, a running archive
   (not the 7-day news window) with `locality`, `state`, `outlet`,
   `first_seen`, `last_seen` on every headline. Look for a locality or theme
   several outlets covered in the last week, especially one where the site
   already has a community page, a moratorium row, or a project dossier to
   link to.

   ```bash
   python3 - <<'PY'
   import json, collections, datetime as dt
   d = json.load(open("data/story_candidates.json"))
   rows = d if isinstance(d, list) else next(v for v in d.values() if isinstance(v, list))
   cut = (dt.date.today() - dt.timedelta(days=10)).isoformat()
   recent = [r for r in rows if (r.get("first_seen") or "") >= cut]
   by_loc = collections.Counter(
       f'{r.get("locality") or "?"}, {r.get("state") or "?"}' for r in recent)
   print(f"{len(recent)} headlines since {cut}\n")
   for loc, n in by_loc.most_common(20):
       print(f"{n:3}  {loc}")
   PY
   ```

Then rule out anything already covered — read the existing titles and ids
before you commit to an angle:

```bash
python3 -c "from src.blog_content import BLOG_STORIES as B; [print(s['date'], s['id'], '|', s['title']) for s in sorted(B, key=lambda x: x['date'], reverse=True)[:15]]"
```

31+ posts exist. A second post on the same event needs a genuinely new
development, not a new headline about the old one.

## 2. Research it properly

The archive's `link` is usually a **Google News redirect**, not a publisher
URL. Resolve every one to its real source before you cite it, and prefer the
primary document over the article about it: the ordinance, the agenda packet,
the permit, the utility filing, the 10-K, the environmental report.

Read at least three independent sources. If three don't exist, that is the
signal the story isn't ready.

## 3. The sourcing bar

Non-negotiable, and the reason this post publishes without anyone reading it
first:

- **Every factual claim traces to a source you actually opened.** Not a
  headline, not a snippet, not a summary of a summary.
- **Every number gets an inline link** in the body markdown, to the document
  it came from.
- **Say only what the sources say.** If the outcome is ambiguous, write it as
  ambiguous. If a council "advanced" something, do not write that it passed.
- **Attribute contested claims** to whoever made them. A developer's MW figure
  is the developer's figure.
- **No invented dates, no invented dollar amounts, no invented quotes.**
- If a claim would embarrass a resident who repeated it at a hearing, cut it.

## 4. Write the entry

Add one dict at the **top** of `BLOG_STORIES` in `src/blog_content.py`:

```python
{
    "id": "kebab-case-slug-2026",     # becomes /blog/<id>.html — never reuse or rename
    "art": "moratorium",              # one of ART_THEMES; set it explicitly, don't let it guess
    "section": "stories",
    "title": "...",
    "seo_title": "...",           # <= 60 chars, keyword first, no site suffix — the <title>; the headline goes to h1/og:title
    "date": _dt.date(2026, 8, 30),    # a real date object, not a string
    "author": "GridWatch AI",
    "tags": ["...", "..."],
    "summary": "Two or three sentences. Shown on the index and in the OG card.",
    "body": """...markdown...""",
}
```

Notes that bite:

- `date` is a `datetime.date` — `build_blog_post()` calls `.strftime()` on it.
  A string crashes the build.
- Write prose with a **plain `$`**. The `\$` escapes elsewhere in the file are
  Streamlit-era residue; `_md_to_html()` strips them, but don't add new ones.
- `art` must be one of: bills, checklist, community, extraction, forecast,
  grid, land, media, money, moratorium, negotiation, oversight, queue, review,
  transmission, water.
- The `id` is the permanent URL. Renaming one orphans an indexed page.
- 900–1,600 words. Open with what happened and why it matters to someone
  living near the site; close with a "See also" linking the relevant page on
  this site (state page, moratorium tracker, community briefing, project
  dossier).
- House voice: plain, specific, unexcited. No hype, no "in today's rapidly
  evolving landscape." The reader is a resident three weeks from a zoning
  vote.

The sitemap, blog index, prev/next nav, RSS and OG card all generate from this
dict — no other file needs touching.

## 5. Build, verify, publish

```bash
python3 -m py_compile build_site.py src/blog_content.py && NEWS_FREEZE=1 python3 build_site.py
```

Confirm the post rendered and nothing else broke:

```bash
ls -la web/blog/<id>.html && grep -c "<id>" web/sitemap.xml && grep -c "blog/" web/sitemap.xml
```

Then push. `web/` is committed output, so the post and its rendered pages ship
in one commit:

```bash
git pull --rebase && git add -A src/blog_content.py web/ data/ && git commit -m "post: <title>" && git push
```

Rebase first — CI pushes to `master` daily and a diverged local branch is the
one failure mode here.

If the build fails or `git pull --rebase` conflicts, **do not force anything**.
Leave the tree as-is and report what broke.

## 6. Report

The title, the URL, the sources you cited, and anything you deliberately left
out because you couldn't source it.
