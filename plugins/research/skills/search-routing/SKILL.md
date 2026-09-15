---
name: search-routing
description: Single decision skill for all web search needs. Routes between exa and firecrawl_search based on query characteristics. Auto-selects the cheapest sufficient tool; asks user before invoking expensive deep modes. Use this BEFORE any web search call when the user has multiple search MCPs available.
origin: ECC
---

# Search Routing

Two search MCPs are configured: **exa** and **firecrawl**. (linkup was removed
2026-09-15: no measured quality edge over exa, its key sat on the command line,
and ~81% of its spend went to 10×-priced deep mode.)
This skill picks one — never run both by default.
Expensive / deep modes require explicit user confirmation.

> **First check they exist in this session.** MCP servers are scoped per config
> directory, so a server added under one is absent under another — verify, don't assume.
> If neither is present, routes 1/2/3/5 have nothing to route to: use the
> built-in `WebSearch` for those. **Route 4 (Context7) is unaffected** — it is a separate
> MCP and stays the correct choice for library/API docs regardless.

## Decision Order (apply top-down, stop at first match)

### 0. Known URL → direct fetch, no search

- Static page → `mcp__exa__web_fetch_exa`
- JS-heavy / paywall / needs rendering → `mcp__firecrawl__firecrawl_scrape`

### 1. Operator-laden or domain-targeted → firecrawl_search (~$0.001)

Trigger when the query contains: `site:`, `"..."`, `OR`, `intitle:`,
`inurl:`, `-keyword`, or targets a specific domain
(e.g. `site:github.com awesome lists`).

Empirical signal: in observed usage, 100% of `site:` operator queries
went to firecrawl. Formalize this instinct.

### 2. Chinese-language SERPs → firecrawl_search

Trigger when the query is mostly Chinese characters AND targets
China-specific tools/services (微信支付 / 国内 API / 国内厂商 / 汇付斗拱 etc.).
Firecrawl reaches Chinese SERPs better than exa's neural index.

### 3. Pricing / multi-hop facts / release timing → exa, then verify at the source

Trigger when query asks for:

- Pricing, fees, subscriptions, cost comparisons
- Multi-hop fact synthesis ("X company 2024 revenue vs Y")
- Product release timing where recency + cited sources matter

Use `mcp__exa__web_search_exa`, then open the vendor's own pricing /
announcement page with `mcp__exa__web_fetch_exa` before quoting a number.
No backend configured here reaches paywalled publisher content (Statista,
paywalled news) — the old note that Linkup did was wrong: Linkup's own FAQ says
it only indexes publicly available content.

### 4. Library / API docs → Context7 BEFORE search

Trigger when query is "how do I use X" / "X API syntax" / "X config options"
for a known library (React, FastAPI, SQLAlchemy, SwiftUI, Stripe, etc.).

1. **Load the tools first** — they are deferred: `ToolSearch` with query
   `context7`. Skipping this is why Context7 went almost unused: 14 calls in
   two months (2026-07/09) while ~330 library-doc queries went straight to exa.
2. `mcp__plugin_context7_context7__resolve-library-id` →
   `mcp__plugin_context7_context7__query-docs`.
3. **Check the answer is on topic before using it.** When a library is missing
   or thinly indexed, Context7 does not error — it returns plausible but
   unrelated snippets (2026-09-13: two different 汇付 queries got the identical
   9 KB generic block; a WeasyPrint `@page` question got nothing on point).
   Off topic → fall back to exa + the official doc page.

Reading the official page when falling back: Apple docs are JS-rendered
(WebFetch returns only the title) → `https://sosumi.ai/documentation/<path>`;
very large pages get truncated → read the doc source on GitHub with
`gh api repos/<owner>/<repo>/contents/<path>`.

### 5. Default → exa web_search_exa ($0.005)

Everything else: natural-language descriptive queries, "compare X vs Y",
academic / arxiv search, engineering blogs, "how they built X",
company intel, people lookup. This covers ~80% of remaining cases.

### 6. DEEP MODES — ASK USER FIRST

**Never invoke these silently.** If the query characteristics suggest deep
is warranted, surface the decision:

> "This query likely benefits from `<tool> deep` mode (reason: <why>).
> It costs $<X>/call (<N>× normal). Use deep mode, or try standard first?"

Candidates for deep:

- `research:research` skill (orchestrated multi-search) — full
  research workflows
- Exa's advanced / deep tools (`web_search_advanced_exa`, `agent_run`) are
  **not enabled**: the exa server URL pins `tools=web_search_exa,web_fetch_exa`
  on purpose, because `agent_run` bills per run. Enabling them is a config
  change the user must approve.

**Default behavior**: run standard first. Only suggest deep if standard
results are clearly insufficient.

## Cost Reference (per call)

| Tool | Cost | When |
|---|---:|---|
| firecrawl_search | ~$0.001 | operators, Chinese SERPs, URL list |
| exa standard | $0.005 | default, ~80% of cases |
| Context7 query-docs | free: 1,000 calls/month with an account key (`CONTEXT7_API_KEY`); anonymous limits unpublished | library / API docs |

## Anti-patterns

- Don't pass `site:` / `"..."` to exa — it's neural, ignores operators
- Don't use firecrawl_search alone if you need content body —
  it returns links + descriptions only; chain with scrape if needed
- Don't fan out the same query to both backends "just to be thorough" — pick one
- Don't skip Context7 for library docs and go straight to exa — load it via
  `ToolSearch` first. In a 2026-09-13 spot check it answered 7 of 7 doc
  questions without a factual error at 4–8× fewer tokens than exa; fall back
  only when its answer is off topic (see §4)

## Exa tool signatures (verified against live server, 2026-08-08)

The installed exa-mcp-server exposes exactly two tools — anything else
documented elsewhere (get_code_context_exa, web_search_advanced_exa,
crawling_exa) does not exist:

- `mcp__exa__web_search_exa(query, numResults)` — neural search; ignores
  `site:` / quote operators
- `mcp__exa__web_fetch_exa(urls, maxCharacters)` — fetch page content

Tip: the first retrieval round is often about learning the project's own
vocabulary — a search for "rate limit" may fail because the codebase calls
it "throttle". Re-search with the project's terms before concluding absence.

## Related Skills

- `research` — orchestrated firecrawl + exa research workflow,
  including business-research scenario checklists
  (also requires user confirmation per §6)
