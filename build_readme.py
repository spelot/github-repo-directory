#!/usr/bin/env python3
"""Rebuild the shareable directory from repos.csv (the source of truth).
Writes README.md, repos/<owner>__<repo>.md (one per repo), llms.txt and repo-directory.zip.
Standard library only. Never reads or ships .private/ or .cache/."""
import csv, datetime, pathlib, collections, zipfile, re, json
HERE = pathlib.Path(__file__).resolve().parent
CATS = ["Build", "Agents & AI tools", "Content & writing", "Marketing & SEO", "Business ops & CRM", "Learning"]
STATUSES = ["Using", "Want to try", "Watching", "Avoid"]
SHAREABLE = ["README.md", "llms.txt", "repos.csv", "ADDING.md", "search.sh", "search.py", "build_readme.py"]
BADGE = {"Using": "✅ Using", "Want to try": "🧪 Want to try", "Watching": "👀 Watching", "Avoid": "⛔ Avoid"}

rows = list(csv.DictReader(open(HERE / "repos.csv", newline="")))
for r in rows:
    assert r["purpose_category"] in CATS, f"{r['name']}: bad category {r['purpose_category']}"
    assert r["status"] in STATUSES, f"{r['name']}: bad status {r['status']}"
today = datetime.date.today().isoformat()
stale = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
esc = lambda s: (s or "").replace("|", "\\|").replace("\n", " ")
fname = lambda r: r["name"].replace("/", "__") + ".md"
num = lambda v: int(v) if str(v).isdigit() else 0
def videos(r):
    out = []
    for v in filter(None, (x.strip() for x in r["youtube_videos"].split(";;"))):
        title, url = v.rsplit(" | ", 1); out.append((title, url))
    return out
def yq(s): return json.dumps(s, ensure_ascii=False)   # JSON string is valid YAML
counts = collections.Counter(r["status"] for r in rows)
with_vids = sum(1 for r in rows if r["youtube_videos"])

# ---------- per-repo files ----------
rd = HERE / "repos"; rd.mkdir(exist_ok=True)
for old in rd.glob("*.md"): old.unlink()
for r in rows:
    tasks = [t.strip() for t in r["tasks"].split(";") if t.strip()]
    fm = [
        "---", "type: GitHub Repository", f"title: {yq(r['name'])}", f"description: {yq(r['what_it_does'])}",
        f"resource: {r['url']}", f"name: {yq(r['name'])}", f"url: {r['url']}", f"category: {yq(r['purpose_category'])}",
        f"status: {yq(r['status'])}", "tasks: [" + ", ".join(yq(t) for t in tasks) + "]",
        f"stars: {num(r['stars'])}", f"forks: {num(r['forks'])}", f"watchers: {num(r['watchers'])}",
        f"contributors: {yq(r['contributors'])}", f"latest_release: {yq(r['latest_release'])}",
        f"last_updated: {r['last_updated']}", f"license: {yq(r['license'])}", f"risk: {yq(r['risk_notes'])}",
        f"tags: [github, {yq(r['purpose_category'])}]",
        f"generated: {{ by: agent:doogie, at: {today}T00:00:00-08:00 }}", f"stale_after: {stale}T00:00:00-08:00", "---", "",
    ]
    vids = videos(r)
    body = [
        f"# {r['name']}", "",
        f"{r['what_it_does']}", "",
        f"**Status:** {BADGE[r['status']]} · **Category:** {r['purpose_category']} · **Helps:** {r['who_it_helps']}  ",
        f"**Stars** {r['stars']} · **Forks** {r['forks']} · **Watchers** {r['watchers']} · **Contributors** {r['contributors'] or '—'} · **Open issues + PRs** {r['open_issues']}  ",
        f"**Latest release:** {r['latest_release'] or 'none'} · **Last push:** {r['last_updated']} · **License:** {r['license']}  ",
        f"**Quality:** {r['quality_note']}", "",
        "## Instructions", "",
        f"- Setup / docs: {r['docs_url']}",
        f"- Repo: {r['url']}", "",
        "## Use cases", "",
        *[f"- {u.strip()}" for u in r["use_cases"].split(";") if u.strip()], "",
        "## Videos", "",
        *([f"- [{t}]({u})" for t, u in vids] or ["- None verified yet."]), "",
        "## Risk notes", "",
        (("**⛔ Avoid: do not install or recommend.** " if r["status"] == "Avoid" else "") + (r["risk_notes"] or "None known.")), "",
        f"Search tasks: {', '.join(tasks)}", "",
        "[Back to the directory index](../README.md)", "",
    ]
    (rd / fname(r)).write_text("\n".join(fm + body))

# ---------- README ----------
out = [f"""---
type: Reference
title: Sage's GitHub Repo Directory
description: Searchable list of GitHub repos for AI consulting, content and vibe-coding, tagged by task, status, quality and risk. Readable by people and by AI agents (Claude, ChatGPT, Gemini).
resource: repos.csv
tags: [github, repos, tools, directory, sage-builds, agents]
status: stable
generated: {{ by: agent:doogie, at: {today}T00:00:00-08:00 }}
sources:
  - {{ id: github, resource: https://api.github.com, title: "GitHub API: stars, forks, watchers, issues, contributors, license, last push" }}
  - {{ id: youtube, resource: https://www.youtube.com, title: "YouTube: each video checked to be about its repo" }}
stale_after: {stale}T00:00:00-08:00
---

# Sage's GitHub Repo Directory

> **Living directory.** [`repos.csv`](repos.csv) is the source of truth. This page, the [`repos/`](repos/) detail files and [`llms.txt`](llms.txt) are rebuilt from it with `python3 build_readme.py`. Don't hand-edit them.

**Owner:** Sage Pelot (Sage Builds / sagepelot.com)  
**Repos:** {len(rows)} · Using {counts['Using']} · Want to try {counts['Want to try']} · Watching {counts['Watching']} · Avoid {counts['Avoid']} · {with_vids} with verified explainer videos  
**Numbers** pulled live from GitHub on {today}; dates are Pacific time. Numbers go stale, so re-check before a big decision.

---

## How to use this (people and AI agents)

1. **Search by task**, not by name: `./search.sh seo audit` matches name, tasks, use cases, description and category. Filters: `--status Using`, `--category "Marketing & SEO"`, `--any`, `--json`. No search tool? Read the tables below or [`repos.csv`](repos.csv).
2. **Open the detail file** in [`repos/`](repos/) for setup instructions, use cases, videos and risks.
3. **Check `status` before recommending.** Prefer ✅ Using, then 🧪 Want to try. 👀 Watching means known but not yet vetted; say so if you suggest one.
4. **Read `risk_notes` every time** and repeat any flag (scraping, auto-posting, login or cookie reuse, platform terms, paid API or data) before anyone installs anything.
5. **Never use or recommend ⛔ Avoid repos.** They're listed so nobody re-discovers them as "new".
6. **Judge quality with GitHub's real signals.** GitHub has no reviews or shares. The closest equivalents are:
   - **Stars** (people bookmarking it): roughly "reviews/likes".
   - **Forks** (people copying it to build on): roughly "shares" or branches of the project.
   - **Watchers** (people subscribed to updates): ongoing interest.
   - **Contributors, last push, latest release and open issues** show whether it's alive and maintained. `quality_note` sums these up in plain words.
   - Open issues on GitHub include open pull requests. A big number on a huge project is normal.
7. **Adding a repo:** follow [ADDING.md](ADDING.md).

Columns in `repos.csv`: `{', '.join(rows[0].keys())}`. `youtube_videos` holds up to 2 entries as `Title | URL`, separated by ` ;; `.

---
"""]
for cat in CATS:
    rs = sorted([r for r in rows if r["purpose_category"] == cat], key=lambda r: (STATUSES.index(r["status"]), -num(r["stars"])))
    if not rs: continue
    out.append(f"## {cat}\n")
    out.append("| Repo | What it does | Status | ★ Stars | Forks | Watchers | Contributors | Quality | Risk notes | Details |")
    out.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in rs:
        out.append(f"| [{r['name']}]({r['url']}) | {esc(r['what_it_does'])} | {BADGE[r['status']]} | {r['stars']} | {r['forks']} | {r['watchers']} | {r['contributors'] or '—'} | {esc(r['quality_note'])} | {esc(r['risk_notes'])} | [docs]({r['docs_url']}) · [more](repos/{fname(r)}) |")
    out.append("")

THEMES = [
 ("SEO, keyword research, site audit", ["seo", "keyword", "site audit", "backlink", "aeo"]),
 ("LinkedIn content and profile", ["linkedin"]),
 ("Social media / platform research", ["social media", "twitter", "reddit", "xiaohongshu"]),
 ("YouTube and video research, transcripts", ["youtube", "transcript", "subtitle", "video"]),
 ("Writing, prompts, copy", ["prompt", "writing", "long-form", "copy", "hooks"]),
 ("Offers, landing pages, marketing", ["offer", "landing page", "marketing", "link tracking", "newsletter"]),
 ("Building apps and voice agents", ["build app", "vibe coding", "voice agent", "coding agent", "github login"]),
 ("Agent skills and add-ons", ["agent skills", "claude skill", "skills list", "claude code resources"]),
 ("Automation and workflows", ["automation", "n8n", "zapier"]),
 ("CRM, database, forms, scheduling", ["crm", "airtable", "survey", "scheduling", "database"]),
 ("Second brain, knowledge base, OKF", ["second brain", "llm wiki", "okf", "knowledge base", "para", "agent memory"]),
 ("Learning AI", ["learn"]),
]
out.append("---\n\n## Task → repo quick lookup\n")
out.append("Best pick first (Using → Want to try → Watching, then by stars). ⛔ Avoid repos sit in their own column so agents can spot them.\n")
out.append("| Task | Use these | Avoid |")
out.append("| --- | --- | --- |")
fmt = lambda r: f"[{r['name'].split('/')[1]}](repos/{fname(r)}) ({r['status']})"
for theme, kws in THEMES:
    hits = [r for r in rows if any(k in (r["tasks"] + " " + r["name"]).lower() for k in kws)]
    good = sorted([r for r in hits if r["status"] != "Avoid"], key=lambda r: (STATUSES.index(r["status"]), -num(r["stars"])))
    bad = [r for r in hits if r["status"] == "Avoid"]
    out.append(f"| {theme} | {', '.join(fmt(r) for r in good) or '—'} | {', '.join(fmt(r) for r in bad) or '—'} |")
out.append("")
(HERE / "README.md").write_text("\n".join(out))

# ---------- llms.txt ----------
llms = [
 "# Sage's GitHub Repo Directory", "",
 "> A searchable list of GitHub repos for AI consulting, content and vibe-coding, tagged by task, status (Using / Want to try / Watching / Avoid), quality signals and risk. Never recommend repos with status Avoid; always repeat their risk_notes.", "",
 "## Start here",
 "- [README.md](README.md): index, rules for agents, tables by category, task lookup",
 "- [repos.csv](repos.csv): source of truth, one row per repo (all columns)",
 "- [repos/](repos/): one Markdown file per repo with YAML frontmatter: instructions, use cases, videos, risk notes",
 "- [ADDING.md](ADDING.md): how to add a repo", "",
 "## Repos",
 *[f"- [{r['name']}](repos/{fname(r)}): {r['status']} · {r['purpose_category']} · {r['what_it_does']}" for r in rows], "",
]
(HERE / "llms.txt").write_text("\n".join(llms))

# ---------- zip (shareable files only) ----------
z = HERE / "repo-directory.zip"
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
    for f in SHAREABLE: zf.write(HERE / f, f"github-repo-directory/{f}")
    for f in sorted(rd.glob("*.md")): zf.write(f, f"github-repo-directory/repos/{f.name}")
print(f"Rebuilt README.md, llms.txt, {len(rows)} repo files, {z.name}")
