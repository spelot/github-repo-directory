#!/usr/bin/env python3
"""Rebuild the shareable AI resources directory from resources.csv (the source of truth).
Writes README.md, resources/<slug>.md (one per resource), llms.txt and ai-resources-directory.zip.
Standard library only. Never reads or ships .private/ or .cache/."""
import csv, datetime, pathlib, collections, zipfile, re, json
HERE = pathlib.Path(__file__).resolve().parent
TYPES = ["App/Tool", "Plugin/Connector", "Agent/Bot template", "Skill", "Automation", "Prompt/Framework"]
CATS = ["Run the company", "Write", "Create content", "Build apps", "Research", "Serve clients", "Communicate", "Sell & market"]
STATUSES = ["Using", "Want to try", "Watching", "Avoid"]
COLS = ["name", "url", "type", "job_category", "tasks", "what_it_does", "works_with", "pricing", "status", "risk_notes",
        "docs_url", "use_cases", "youtube_videos", "quality_signals", "last_checked"]
SHAREABLE = ["README.md", "llms.txt", "resources.csv", "ADDING.md", "search.sh", "search.py", "build_directory.py"]
BADGE = {"Using": "✅ Using", "Want to try": "🧪 Want to try", "Watching": "👀 Watching", "Avoid": "⛔ Avoid"}

rows = list(csv.DictReader(open(HERE / "resources.csv", newline="")))
assert rows and list(rows[0].keys()) == COLS, f"resources.csv columns must be exactly: {COLS}"
names = collections.Counter(r["name"].lower() for r in rows)
assert all(v == 1 for v in names.values()), f"duplicate names: {[k for k, v in names.items() if v > 1]}"
split = lambda s, sep=";": [x.strip() for x in (s or "").split(sep) if x.strip()]
for r in rows:
    assert r["type"] in TYPES, f"{r['name']}: bad type {r['type']!r}"
    assert r["status"] in STATUSES, f"{r['name']}: bad status {r['status']!r}"
    cats = split(r["job_category"]); assert cats, f"{r['name']}: missing job_category"
    for c in cats: assert c in CATS, f"{r['name']}: bad job_category {c!r}"
    assert r["url"].startswith("http"), f"{r['name']}: url must be a full link"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["last_checked"]), f"{r['name']}: last_checked must be YYYY-MM-DD"
    for v in split(r["youtube_videos"], ";;"):
        assert " | https://www.youtube.com/watch?v=" in v, f"{r['name']}: video must be 'Title (Channel) | https://www.youtube.com/watch?v=ID'"

today = datetime.date.today().isoformat()
stale = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
esc = lambda s: (s or "").replace("|", "\\|").replace("\n", " ")
slug = lambda r: re.sub(r"[^a-z0-9]+", "-", r["name"].lower()).strip("-") + ".md"
primary = lambda r: split(r["job_category"])[0]
yq = lambda s: json.dumps(s, ensure_ascii=False)   # a JSON string is valid YAML
ylist = lambda xs: "[" + ", ".join(yq(x) for x in xs) + "]"
def videos(r): return [tuple(v.rsplit(" | ", 1)) for v in split(r["youtube_videos"], ";;")]
by_status = collections.Counter(r["status"] for r in rows)
by_type = collections.Counter(r["type"] for r in rows)
by_cat = collections.Counter(primary(r) for r in rows)
with_vids = sum(1 for r in rows if r["youtube_videos"])
order = lambda r: (STATUSES.index(r["status"]), TYPES.index(r["type"]), r["name"].lower())

# ---------- per-resource files ----------
rd = HERE / "resources"; rd.mkdir(exist_ok=True)
for old in rd.glob("*.md"): old.unlink()
for r in rows:
    fm = [
        "---", f"type: {yq(r['type'])}", f"title: {yq(r['name'])}", f"description: {yq(r['what_it_does'])}",
        f"resource: {r['url']}", f"name: {yq(r['name'])}", f"url: {r['url']}", f"docs_url: {r['docs_url'] or 'null'}",
        f"job_category: {ylist(split(r['job_category']))}", f"status: {yq(r['status'])}",
        f"tasks: {ylist(split(r['tasks']))}", f"works_with: {ylist(split(r['works_with']))}",
        f"pricing: {yq(r['pricing'])}", f"risk: {yq(r['risk_notes'])}", f"quality_signals: {yq(r['quality_signals'])}",
        f"last_checked: {r['last_checked']}",
        f"tags: {ylist(['ai-resource', r['type'], *split(r['job_category'])])}",
        f"generated: {{ by: agent:doogie, at: {today}T00:00:00-08:00 }}", f"stale_after: {stale}T00:00:00-08:00", "---", "",
    ]
    vids = videos(r)
    body = [
        f"# {r['name']}", "",
        r["what_it_does"], "",
        f"**Status:** {BADGE[r['status']]} · **Type:** {r['type']} · **Jobs:** {', '.join(split(r['job_category']))}  ",
        f"**Works with:** {', '.join(split(r['works_with'])) or '—'}  ",
        f"**Pricing:** {r['pricing'] or 'Not verified.'}  ",
        f"**Quality signals:** {r['quality_signals'] or '—'}  ",
        f"**Last checked:** {r['last_checked']}", "",
        "## Links", "", f"- Home: {r['url']}", f"- Docs / setup: {r['docs_url'] or '—'}", "",
        "## Use cases", "", *([f"- {u}" for u in split(r["use_cases"])] or ["- —"]), "",
        "## Videos", "", *([f"- [{t}]({u})" for t, u in vids] or ["- None verified yet."]), "",
        "## Risk notes", "",
        (("**⛔ Avoid: do not use or recommend.** " if r["status"] == "Avoid" else "") + (r["risk_notes"] or "None known.")), "",
        f"Search tasks: {', '.join(split(r['tasks']))}", "",
        "[Back to the directory index](../README.md)", "",
    ]
    (rd / slug(r)).write_text("\n".join(fm + body))

# ---------- README ----------
cnt = lambda c, keys: " · ".join(f"{k} {c[k]}" for k in keys if c[k])
out = [f"""---
type: Reference
title: Sage's AI Resources Directory
description: Plugins, connectors, bot templates, apps, skills, automations and frameworks that Grok Bot and other AI agents can use to help a person run a company, write, create content, build apps, research, serve clients, communicate and sell. Tagged by job, task, status, price and risk.
resource: resources.csv
tags: [ai-tools, agents, mcp, plugins, bot-templates, skills, automations, directory, sage-builds]
status: stable
generated: {{ by: agent:doogie, at: {today}T00:00:00-08:00 }}
sources:
  - {{ id: vendor-pages, resource: resources.csv, title: "Each tool's own pricing, docs or help page, opened on the last_checked date" }}
  - {{ id: grok-bot-marketplace, resource: https://x.ai/bot/marketplace, title: "Grok Bot Marketplace template pages" }}
  - {{ id: youtube, resource: https://www.youtube.com, title: "YouTube: each video checked live and named for its tool" }}
stale_after: {stale}T00:00:00-08:00
---

# Sage's AI Resources Directory

> **Living directory.** [`resources.csv`](resources.csv) is the source of truth. This page, the [`resources/`](resources/) detail files and [`llms.txt`](llms.txt) are rebuilt from it with `python3 build_directory.py`. Don't hand-edit them.

**Owner:** Sage Pelot (Sage Builds / sagepelot.com)  
**Resources:** {len(rows)} · {cnt(by_status, STATUSES)} · {with_vids} with verified videos  
**By type:** {cnt(by_type, TYPES)}  
**By main job:** {cnt(by_cat, CATS)}  
**Prices** were read on each tool's own page on the `last_checked` date (Pacific time). Prices change; re-check before anyone pays. A blank or "not verified" price means we couldn't confirm it.

Companion directory: [GitHub repo directory](../github-repos/README.md) for open-source repos and skill packs.

---

## How to use this (people and AI agents)

1. **Search by task**, not by name: `./search.sh newsletter` or `./search.sh client follow up`. It matches name, tasks, description, use cases, job and type. Filters: `--status Using`, `--type "Plugin/Connector"`, `--category "Sell & market"`, `--works-with Claude`, `--any`, `--json`. No search tool? Use the tables below or [`resources.csv`](resources.csv).
2. **Open the detail file** in [`resources/`](resources/) for pricing, docs, use cases, videos and risks.
3. **Check `status` before recommending.** ✅ Using = in Sage's stack today. 🧪 Want to try = planned or shortlisted. 👀 Watching = known, not vetted; say so if you suggest one. ⛔ Avoid = never recommend.
4. **Read `risk_notes` every time** and repeat any flag (auto-posting, platform terms, phone or email laws, shared logins, credit-based costs, data privacy) before anyone signs up, connects an account or pays.
5. **Check `works_with`** to see if it fits your agent (Grok Bot, Claude, ChatGPT, Gemini, MCP, n8n…). MCP means any assistant that supports the Model Context Protocol.
6. **Never send, post, buy or connect an account without the person's yes.** Bot templates here draft by default; keep it that way.
7. **Adding a resource:** follow [ADDING.md](ADDING.md).

Types: **App/Tool** (a product you sign into) · **Plugin/Connector** (MCP server or connector an assistant uses) · **Agent/Bot template** (ready-made bot) · **Skill** (reusable playbook an agent loads) · **Automation** (workflow templates) · **Prompt/Framework** (method, standard or guide).

Columns in `resources.csv`: `{', '.join(COLS)}`. Lists use `;`. `youtube_videos` holds up to 2 entries as `Title (Channel) | URL`, separated by ` ;; `.

---
"""]
for cat in CATS:
    rs = sorted([r for r in rows if primary(r) == cat], key=order)
    if not rs: continue
    out.append(f"## {cat}\n")
    out.append("| Resource | Type | What it does | Status | Works with | Pricing | Risk notes | Details |")
    out.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in rs:
        out.append(f"| [{esc(r['name'])}]({r['url']}) | {r['type']} | {esc(r['what_it_does'])} | {BADGE[r['status']]} | {esc(', '.join(split(r['works_with'])))} | {esc(r['pricing'])} | {esc(r['risk_notes'])} | [docs]({r['docs_url'] or r['url']}) · [more](resources/{slug(r)}) |")
    out.append("")

THEMES = [
 ("Run my week / delegate to a bot", ["delegate", "routine", "design a new bot", "ready-made bot", "run named", "teach a bot"]),
 ("Write in my voice / edit drafts", ["write and edit", "edit ai-sounding", "dictate", "brand voice", "voice to text", "landing-page copy", "faster writing"]),
 ("Plan and make social content", ["social", "repurpose", "schedule posts", "content ideas", "content research", "content calendar"]),
 ("Video: edit, clip, research", ["video", "clip", "youtube", "captions"]),
 ("Research a topic, niche or trend", ["research", "trend", "outlier", "mentions"]),
 ("Know what competitors do", ["competitor"]),
 ("SEO and showing up in AI answers", ["seo", "keyword", "aeo", "ai assistant recommendations"]),
 ("Newsletter and email list", ["newsletter", "email list", "email sequence"]),
 ("Leads, sales calls and follow-up", ["lead", "sales call", "outreach", "follow-up", "proposal", "discovery"]),
 ("Take payments / sell a program or book", ["payment", "sell", "checkout", "pre-order"]),
 ("Serve clients: booking, portals, proof", ["booking", "client portal", "testimonial", "case stud", "onboarding"]),
 ("Community and members", ["community", "membership", "speaking"]),
 ("Build a site or app", ["website", "landing page", "build a web app", "build an app", "host a site", "one-page"]),
 ("Automate workflows between apps", ["automate", "workflow", "connect apps", "connect ai", "connect agents"]),
 ("CRM and business data", ["crm", "database", "track leads"]),
 ("Phone and voice agents", ["phone", "voice agent", "answer calls"]),
 ("Knowledge base and notes for agents", ["notes", "second brain", "knowledge base", "wiki"]),
 ("Teach agents skills and better prompts", ["skill", "teach", "prompt", "understand mcp", "connect ai to tools"]),
]
out.append("---\n\n## Task → resource quick lookup\n")
out.append("Best pick first (Using → Want to try → Watching). ⛔ Avoid items sit in their own column so agents can spot them.\n")
out.append("| Task | Use these | Avoid |")
out.append("| --- | --- | --- |")
fmt = lambda r: f"[{esc(r['name'])}](resources/{slug(r)}) ({r['status']})"
for theme, kws in THEMES:
    hits = [r for r in rows if any(k in r["tasks"].lower() for k in kws)]
    good = sorted([r for r in hits if r["status"] != "Avoid"], key=order)[:10]
    bad = [r for r in hits if r["status"] == "Avoid"]
    out.append(f"| {theme} | {', '.join(fmt(r) for r in good) or '—'} | {', '.join(fmt(r) for r in bad) or '—'} |")
out.append("")
(HERE / "README.md").write_text("\n".join(out))

# ---------- llms.txt ----------
llms = [
 "# Sage's AI Resources Directory", "",
 "> Plugins, connectors, bot templates, apps, skills, automations and frameworks that AI agents (Grok Bot, Claude, ChatGPT, Gemini) can use to help run a company, write, create content, build apps, research, serve clients, communicate and sell. Each entry has status (Using / Want to try / Watching / Avoid), pricing with the date checked, and risk notes. Never recommend Avoid items; always repeat risk_notes; never send, post, buy or connect accounts without the person's approval.", "",
 "## Start here",
 "- [README.md](README.md): index, rules for agents, tables by job, task lookup",
 "- [resources.csv](resources.csv): source of truth, one row per resource (all columns)",
 "- [resources/](resources/): one Markdown file per resource with YAML frontmatter",
 "- [ADDING.md](ADDING.md): how to add a resource", "",
 "## Resources",
 *[f"- [{r['name']}](resources/{slug(r)}): {r['type']} · {r['status']} · {r['job_category']} · {r['what_it_does']}" for r in sorted(rows, key=order)], "",
]
(HERE / "llms.txt").write_text("\n".join(llms))

# ---------- zip (shareable files only) ----------
z = HERE / "ai-resources-directory.zip"
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
    for f in SHAREABLE: zf.write(HERE / f, f"ai-resources-directory/{f}")
    for f in sorted(rd.glob("*.md")): zf.write(f, f"ai-resources-directory/resources/{f.name}")
print(f"Rebuilt README.md, llms.txt, {len(rows)} resource files, {z.name}")
