# Adding a resource

For Sage, colleagues or any agent. `resources.csv` is the source of truth. `README.md`, `resources/*.md`, `llms.txt` and `ai-resources-directory.zip` are all rebuilt from it.

1. **Check it isn't already listed:** `./search.sh <name>` and `./search.sh <the task it does>`.
2. **Open the tool's own pages today.** Read the pricing page, the docs or help page, and (for connectors) the page that says which plan the MCP or API needs. Never copy prices or features from memory, a blog, a review site or another list. If the price doesn't show (blocked page, price hidden behind sign-up), write `price not verified` and say why.
3. **Read the terms and the setup steps** before you fill `risk_notes`. Look for:
   - auto-posting or auto-messaging, and platform rules (Meta, LinkedIn, X, TikTok, YouTube)
   - phone, SMS or email laws (consent, recording disclosure, cold outreach)
   - shared logins, broad OAuth scopes, a third party holding your tokens
   - credit- or usage-based billing, overages, trials that convert, fees per sale
   - client data and privacy (what it stores, whether it trains on it)
   - maker disclosures (who is promoting it and whether they own it)
4. **Videos:** add up to 2, only after you open each one and confirm it's live and about this tool (its title or channel names the tool). Format: `Title (Channel) | https://www.youtube.com/watch?v=ID`, separated by ` ;; `. Remove any `|` from titles. Leave it blank if you can't find one. Never guess.
5. **Add one row to `resources.csv`, filling in every column:**

   | Column | Rule |
   | --- | --- |
   | name | the product's own name; add "MCP" for a connector-only entry |
   | url | its home page (or the marketplace page for a bot template) |
   | type | App/Tool · Plugin/Connector · Agent/Bot template · Skill · Automation · Prompt/Framework |
   | job_category | one or more of: Run the company · Write · Create content · Build apps · Research · Serve clients · Communicate · Sell & market. `;`-separated, main one first |
   | tasks | `;`-separated plain words someone would search, e.g. `newsletter; email sequence` |
   | what_it_does | one plain sentence |
   | works_with | `;`-separated: Grok Bot, Claude, ChatGPT, Gemini, MCP, n8n, Zapier, Make, API… |
   | pricing | `free`, `freemium`, `paid`, `pay per sale` or `usage-based`, then the starting price as the page shows it, then `Checked YYYY-MM-DD.` |
   | status | Using (in Sage's stack today) · Want to try (planned or shortlisted) · Watching (known, not vetted) · Avoid (don't use; say why in risk_notes) |
   | risk_notes | the flags from step 3, or leave blank if none |
   | docs_url | the setup or help page |
   | use_cases | 1–3 short `;`-separated uses for coaches, authors, community leaders or small businesses |
   | youtube_videos | see step 4 |
   | quality_signals | only numbers you saw: user counts, ratings with review counts, GitHub stars, funding, official maker. Say "per its site" for vendor claims |
   | last_checked | the date you opened the pages, `YYYY-MM-DD` (Pacific time) |

   Leave a cell blank if you can't verify it. Don't guess.
6. **Keep it shareable.** No private notes, internal file paths, account details or personal details go in `resources.csv`. Private notes on why a status was chosen go in `.private/provenance.csv`, which is local only and never zipped or shared.
7. **Rebuild and check:** `python3 build_directory.py` (it stops on a bad type, job category, status, date or video format), then `./search.sh <a task word>`.
8. **Rules:** agents may add rows and update values. Don't delete rows; set the status to `Avoid` and say why in `risk_notes`. Ask Sage before marking anything `Using`. Re-check prices on anything with a `last_checked` older than 30 days before recommending it.
