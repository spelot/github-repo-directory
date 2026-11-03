#!/usr/bin/env python3
"""Search resources.csv by keyword.
Usage: ./search.sh newsletter [--status Using] [--type "Plugin/Connector"] [--category "Sell & market"] [--works-with Claude] [--any] [--json]
All words must match (AND) across name, tasks, what_it_does, use_cases, job_category, type and works_with. --any = match any word.
If nothing matches every word, falls back to any-word matches ranked by hits."""
import csv, sys, json, pathlib
HERE = pathlib.Path(__file__).resolve().parent
args, flt, anymode, asjson = [], {}, False, False
a = sys.argv[1:]; i = 0
opts = {"--status": "status", "--type": "type", "--category": "job_category", "--works-with": "works_with"}
while i < len(a):
    if a[i] in opts and i + 1 < len(a): flt[opts[a[i]]] = a[i+1].lower(); i += 2
    elif a[i] == "--any": anymode = True; i += 1
    elif a[i] == "--json": asjson = True; i += 1
    elif a[i] in ("-h", "--help"): print(__doc__); sys.exit(0)
    else: args.append(a[i].lower()); i += 1
rows = list(csv.DictReader(open(HERE / "resources.csv", newline="")))
for col, v in flt.items():
    rows = [r for r in rows if (r[col].lower() == v if col == "status" else v in r[col].lower())]
def hay(r): return " ".join(r[c] for c in ["name", "tasks", "what_it_does", "use_cases", "job_category", "type", "works_with"]).lower()
def score(r): return sum(1 for w in args if w in hay(r))
order = {"Using": 0, "Want to try": 1, "Watching": 2, "Avoid": 3}
fallback = False
if args:
    hits = [r for r in rows if score(r) == len(args)] if not anymode else []
    if not hits:
        hits = [r for r in rows if score(r) > 0]; fallback = not anymode
    hits.sort(key=lambda r: (-score(r), order[r["status"]], r["name"].lower()))
else:
    hits = sorted(rows, key=lambda r: (order[r["status"]], r["name"].lower()))
if asjson:
    print(json.dumps(hits, indent=1, ensure_ascii=False)); sys.exit(0 if hits else 1)
if not hits:
    print("No matches. Try fewer or broader words, or --any."); sys.exit(1)
if fallback: print("(Nothing matched every word; showing partial matches.)\n")
import re
for r in hits:
    flag = "  ⛔ AVOID: do not use" if r["status"] == "Avoid" else ""
    print(f"{r['name']}  [{r['type']} · {r['status']} · {r['job_category']}]{flag}")
    print(f"  {r['url']}")
    print(f"  {r['what_it_does']}")
    print(f"  tasks: {r['tasks']}")
    print(f"  works with: {r['works_with'] or '—'}")
    print(f"  pricing: {r['pricing'] or 'not verified'}")
    if r["risk_notes"]: print(f"  risk: {r['risk_notes']}")
    slug = re.sub(r"[^a-z0-9]+", "-", r["name"].lower()).strip("-")
    print(f"  docs: {r['docs_url'] or '—'}  ·  details: resources/{slug}.md")
    print()
print(f"{len(hits)} match(es).")
