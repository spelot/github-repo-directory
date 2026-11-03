#!/usr/bin/env python3
"""Search repos.csv by keyword. Usage: ./search.sh seo audit [--status Using] [--category "Marketing & SEO"] [--any] [--json]
All words must match (AND) across name, owner, tasks, what_it_does, use_cases, purpose_category. --any = match any word.
If nothing matches every word, falls back to any-word matches ranked by hits."""
import csv, sys, json, pathlib
HERE = pathlib.Path(__file__).resolve().parent
args, status, cat, anymode, asjson = [], None, None, False, False
a = sys.argv[1:]; i = 0
while i < len(a):
    if a[i] == "--status": status = a[i+1].lower(); i += 2
    elif a[i] == "--category": cat = a[i+1].lower(); i += 2
    elif a[i] == "--any": anymode = True; i += 1
    elif a[i] == "--json": asjson = True; i += 1
    elif a[i] in ("-h", "--help"): print(__doc__); sys.exit(0)
    else: args.append(a[i].lower()); i += 1
rows = list(csv.DictReader(open(HERE / "repos.csv", newline="")))
if status: rows = [r for r in rows if r["status"].lower() == status]
if cat: rows = [r for r in rows if cat in r["purpose_category"].lower()]
def hay(r): return " ".join([r["name"], r["owner"], r["tasks"], r["what_it_does"], r.get("use_cases",""), r["purpose_category"]]).lower()
def score(r): return sum(1 for w in args if w in hay(r))
order = {"Using": 0, "Want to try": 1, "Watching": 2, "Avoid": 3}
if args:
    hits = [r for r in rows if score(r) == len(args)] if not anymode else []
    fallback = False
    if not hits:
        hits = [r for r in rows if score(r) > 0]; fallback = not anymode
    hits.sort(key=lambda r: (-score(r), order[r["status"]], -int(r["stars"] or 0)))
else:
    hits, fallback = rows, False
if asjson:
    print(json.dumps(hits, indent=1)); sys.exit(0 if hits else 1)
if not hits:
    print("No matches. Try fewer or broader words, or --any."); sys.exit(1)
if fallback: print("(No repo matched every word; showing partial matches.)\n")
for r in hits:
    flag = "  ⛔ AVOID: do not use" if r["status"] == "Avoid" else ""
    print(f"{r['name']}  [{r['purpose_category']} · {r['status']} · ★{r['stars']} · updated {r['last_updated']}]{flag}")
    print(f"  {r['url']}")
    print(f"  {r['what_it_does']}")
    print(f"  tasks: {r['tasks']}")
    print(f"  quality: {r.get('quality_note','')} (forks {r.get('forks','')}, watchers {r.get('watchers','')}, contributors {r.get('contributors','') or '?'})")
    print(f"  docs: {r.get('docs_url','')}  ·  details: repos/{r['name'].replace('/','__')}.md")
    if r["risk_notes"]: print(f"  risk: {r['risk_notes']}")
    print()
print(f"{len(hits)} match(es).")
