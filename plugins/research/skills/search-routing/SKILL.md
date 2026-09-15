---
name: search-routing
description: Single decision skill for all web search needs. exa is the default search backend (including `site:` and Chinese queries); firecrawl is for scraping pages exa cannot fetch, and firecrawl_search is only a fallback. Asks user before invoking expensive deep modes. Use this BEFORE any web search call when the user has multiple search MCPs available.
origin: ECC
---

# Search Routing

Two search MCPs are configured: **exa** and **firecrawl**. (linkup was removed
2026-09-15: no measured quality edge over exa, its key sat on the command line,
and ~81% of its spend went to 10×-priced deep mode.)

**exa is the search backend; firecrawl is a scraper.** In a 2026-09-13 blind
eval of 20 real queries, exa scored 54/60 against built-in `WebSearch` 47 and
`firecrawl_search` 46; exa led on Chinese cloud / payment docs, while
`firecrawl_search` once surfaced a superseded 2021 policy document. firecrawl
also runs on the Free plan (1,000 credits/month, shared by both config dirs) and
ran dry in both July and August.

Pick one tool — never run both by default.
Expensive / deep modes require explicit user confirmation.

> **First check they exist in this session.** MCP servers are scoped per config
> directory, so a server added under one is absent under another — verify, don't assume.
> If neither is present, routes 1/2/3/5 have nothing to route to: use the
> built-in `WebSearch` for those. **Route 4 (Context7) is unaffected** — it is a separate
> MCP and stays the correct choice for library/API docs regardless.

## Decision Order (apply top-down, stop at first match)

### 0. Known URL → fetch, no search

- Static page → `mcp__exa__web_fetch_exa`
- exa fetch fails or comes back empty → `curl -s https://r.jina.ai/<url>`
  (free, no key; matched firecrawl on 4 of 5 hard pages in a 2026-09-13 test)
- Needs JS rendering, clicks, a stealth proxy, or JSON-schema extraction →
  `mcp__firecrawl__firecrawl_scrape`. Ask for `formats: ["markdown"]` unless you
  truly need structured output: JSON / question formats cost +4 credits per page
  and were 80% of past scrape spend.

### 1. Operator-laden or domain-targeted → exa, operator in the query

Put `site:<domain>` directly in `query`. Verified 2026-09-15 against the remote
server: `site:v2ex.com` and `site:news.ycombinator.com` each returned 8/8 results
on that domain, versus 0/8 for the same query without the operator. Use
`objective` to say which pages should rank first or be excluded.

Other operators (`"exact phrase"`, `OR`, `-keyword`, `intitle:`, `inurl:`,
`after:`) are **untested** on exa. If the answer depends on one being honored
strictly, check the results; when they ignore it, fall back to `firecrawl_search`
(operator-aware) or built-in `WebSearch` (`allowed_domains` / `blocked_domains`).

### 2. Chinese-language queries → exa

Same tool as the default. Name the official source in `objective` (e.g. "official
docs on cloud.tencent.com should rank first") — in a 2026-09-15 check on a 腾讯云
SES question, all 8 results came from Tencent Cloud's own domains. Fall back to
`firecrawl_search` only when exa comes back thin.

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
company intel, people lookup (`category:company` / `category:people` in the
query). This covers ~80% of remaining cases.

### When firecrawl is out of credits

`402 Payment Required` or `Insufficient credits` means the month's quota is gone
(Free plan, resets on the 7th). **Do not retry, and do not let parallel subagents
each rediscover it**: switch to exa / `WebSearch` / Jina for the rest of the
session, and when dispatching subagents tell them "firecrawl credits are
exhausted, don't call it". Past logs show 478 subagents each hitting 402 on
their own.

### 6. DEEP MODES — ASK USER FIRST

**Never invoke these silently.** If the query characteristics suggest deep
is warranted, surface the decision:

> "This query likely benefits from `<tool> deep` mode (reason: <why>).
> It costs $<X>/call (<N>× normal). Use deep mode, or try standard first?"

Candidates for deep:

- `research:research` skill (orchestrated multi-search) — full
  research workflows
- `firecrawl_agent`, `firecrawl_crawl` over a large site, `firecrawl_interact`
  (billed per page or per browser-minute against the 1,000-credit month)
- Exa's advanced / deep tools (`web_search_advanced_exa`, `agent_run`) are
  **not enabled**: the exa server URL pins `tools=web_search_exa,web_fetch_exa`
  on purpose, because `agent_run` bills per run. Enabling them is a config
  change the user must approve.

**Default behavior**: run standard first. Only suggest deep if standard
results are clearly insufficient.

## Cost Reference (per call)

| Tool | Cost | When |
|---|---:|---|
| exa `web_search_exa` | $0.005 | default search, incl. `site:` and Chinese |
| Jina Reader (`r.jina.ai`) | free (rate-limited) | known URL when exa fetch fails |
| `firecrawl_scrape` | 1 credit/page, +4 for JSON / question formats | JS-heavy pages, structured extraction |
| `firecrawl_search` | 2 credits per 10 results | fallback only |
| Context7 query-docs | free: 1,000 calls/month with an account key (`CONTEXT7_API_KEY`); anonymous limits unpublished | library / API docs |

firecrawl Free plan: 1,000 credits/month, 10 requests/minute per endpoint,
2 concurrent; a failed fetch that returns a 403/404 page still costs 1 credit.

## Anti-patterns

- Don't route `site:` or Chinese queries to `firecrawl_search` by default — exa
  handles both (§1–2)
- Don't use firecrawl_search alone if you need content body —
  it returns links + descriptions only; chain with scrape if needed
- Don't keep calling firecrawl after a 402 / `Insufficient credits`
- Don't fan out the same query to both backends "just to be thorough" — pick one
- Don't skip Context7 for library docs and go straight to exa — load it via
  `ToolSearch` first. In a 2026-09-13 spot check it answered 7 of 7 doc
  questions without a factual error at 4–8× fewer tokens than exa; fall back
  only when its answer is off topic (see §4)

## Exa tool signatures (verified against the remote server, 2026-09-15)

The configured server (`https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa`)
exposes exactly two tools:

- `mcp__exa__web_search_exa(query, numResults, objective)` — `query` is a
  natural-language description of the ideal page; it honors `site:<domain>` and
  `category:company` / `category:people`. `objective` says which pages should
  rank first or be excluded and what facts to pull. There is no date filter:
  put the time frame in `query` or `objective`.
- `mcp__exa__web_fetch_exa(urls, maxCharacters)` — batch several URLs in one
  call; `maxCharacters` defaults to 3000.

Anything documented elsewhere — `get_code_context_exa` (shut down 2026-04),
`web_search_advanced_exa`, `crawling_exa` — is not available here.

Tip: the first retrieval round is often about learning the project's own
vocabulary — a search for "rate limit" may fail because the codebase calls
it "throttle". Re-search with the project's terms before concluding absence.

## Related Skills

- `research` — orchestrated exa-first research workflow (firecrawl for
  scraping), including business-research scenario checklists
  (also requires user confirmation per §6)
