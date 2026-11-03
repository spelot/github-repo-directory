# Adding a repo

For Sage, colleagues or any agent. `repos.csv` is the source of truth. `README.md`, `repos/*.md`, `llms.txt` and `repo-directory.zip` are all rebuilt from it.

1. **Check it isn't already listed:** `./search.sh <repo-name>`.
2. **Verify live on GitHub.** Never copy numbers from memory, a blog or another list.
   ```bash
   R=OWNER/REPO
   curl -sL https://api.github.com/repos/$R | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['full_name'],'stars',d['stargazers_count'],'forks',d['forks_count'],'watchers',d['subscribers_count'],'issues',d['open_issues_count'],d['pushed_at'],(d.get('license') or {}).get('spdx_id'),'archived' if d['archived'] else '')"
   curl -sI "https://api.github.com/repos/$R/contributors?per_page=1" | grep -i '^link'   # the number in page=N>; rel="last" is the contributor count (no link header = 1 or 0)
   curl -sIL -o /dev/null -w '%{url_effective}\n' https://github.com/$R/releases/latest  # ends in /releases/tag/<tag> if there is a release
   ```
   Use the `full_name` the API returns, because repos get renamed. Convert dates to Pacific time.
3. **Read the README** before you fill `risk_notes`. Look for scraping, reuse of your logins or cookies, auto-posting or messaging, platform terms (LinkedIn, X, Reddit, Meta, YouTube), and paid APIs or data.
4. **Videos:** add up to 2 only after you open each one and confirm it's about this repo (its title or description names the repo or links to it). Format: `Title | URL`, separated by ` ;; `. Remove any `|` from titles. Leave it blank if you can't find one. Never guess.
5. **Add one row to `repos.csv`, filling in every column:**

   | Column | Rule |
   | --- | --- |
   | name, url, owner | `owner/repo` exactly as GitHub returns it, its URL, and the part before `/` |
   | purpose_category | Build · Agents & AI tools · Content & writing · Marketing & SEO · Business ops & CRM · Learning |
   | tasks | `;`-separated plain words someone would search, e.g. `keyword research; site audit` |
   | what_it_does | one plain sentence |
   | use_cases | 1–3 short `;`-separated uses (AI consulting for coaches, authors, community leaders; content; vibe-coding) |
   | status | Using (actually used) · Want to try (planned) · Watching (known, not vetted) · Avoid (don't use) |
   | risk_notes | the flags from step 3, or `None known.` |
   | who_it_helps | `Sage`, `clients`, `developers` (separate several with `;`) |
   | license | SPDX id; `None detected` or `Other (see repo)` if GitHub has none |
   | stars, forks, watchers, open_issues, contributors | numbers from step 2 (watchers = `subscribers_count`; open_issues includes PRs) |
   | latest_release | `tag (YYYY-MM-DD)`, blank if none |
   | last_updated | last push, `YYYY-MM-DD` |
   | quality_note | short plain summary, e.g. `very active, big community, recent release` |
   | docs_url | the repo's own setup page or README install section |
   | youtube_videos | see step 4 |
   | date_added | today, `YYYY-MM-DD` |

   Leave a cell blank if you can't verify it. Don't guess.
6. **Keep it shareable.** No private notes, internal file paths or personal details go in `repos.csv`. Private notes on where a repo came from go in `.private/provenance.csv`, which is local only and never zipped or shared.
7. **Rebuild and check:** `python3 build_readme.py` (it stops on a bad category or status), then `./search.sh <a task word>`.
8. **Rules:** agents may add rows and update values. Don't delete rows; set the status to `Avoid` and say why in `risk_notes`. Ask Sage before marking anything `Using`.
