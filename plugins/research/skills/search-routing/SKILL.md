---
name: search-routing
description: Single decision skill for all web search needs. Routes among exa, firecrawl_search, and linkup-search based on query characteristics. Auto-selects the cheapest sufficient tool; asks user before invoking expensive deep modes. Use this BEFORE any web search call when the user has multiple search MCPs available.
origin: ECC
---

# Search Routing

Three search MCPs are typically available: **exa**, **firecrawl**, **linkup**.
This skill picks one — never run multiple by default.
Deep modes (10× cost) require explicit user confirmation.

> **First check they exist in this session.** MCP servers are scoped per config
> directory, so a server added under one is absent under another — verify, don't assume.
> If none of the three are present, routes 1/2/3/5 have nothing to route to: use the
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

### 3. Pricing / paywall / premium publisher data → linkup-search standard

Trigger when query asks for:

- Pricing, fees, subscriptions, cost comparisons
- Statista / financial data / paywall articles
- Multi-hop fact synthesis ("X company 2024 revenue vs Y")
- Product release timing where recency + cited sources matter

Linkup has content-licensing deals with publishers (Statista, Xerfi,
paywalled news) that exa can't reach.

Use `depth=standard` ($0.005). Deep needs confirmation — see §6.

### 4. Library / API docs → Context7 BEFORE search

Trigger when query is "how do I use X" / "X API syntax" / "X config options"
for a known library (React, FastAPI, Prisma, etc.).
Use `mcp__plugin_context7_context7__query-docs` first; only fall back
to exa if Context7 returns nothing relevant.

This case is ~45% of typical search volume — getting it right saves
the most tokens.

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

- `linkup-search depth=deep` ($0.05, 10× standard) — multi-hop premium
  facts where standard's raw search results aren't enough
- `mcp__exa__web_search_exa` with deep settings ($0.012) — comprehensive
  technical research
- `research:research` skill (orchestrated multi-search) — full
  research workflows

**Default behavior**: run standard first. Only suggest deep if standard
results are clearly insufficient.

**Known caveat for linkup deep**: the MCP server returns only raw
`searchResults` (link + snippet). Linkup's premium output (`sourcedAnswer`
with LLM-synthesized answer + citations, or `structured` schema output)
is NOT exposed through MCP. So the 10× cost buys mainly better source
ranking, not full deep-research value. Mention this when asking.

## Cost Reference (per call)

| Tool | Cost | When |
|---|---:|---|
| firecrawl_search | ~$0.001 | operators, Chinese SERPs, URL list |
| exa standard | $0.005 | default, ~80% of cases |
| linkup standard | $0.005 | pricing / premium publishers / multi-hop |
| exa deep | $0.012 | **confirm first** |
| linkup deep | $0.05 (10×) | **confirm first** — MCP doesn't expose sourcedAnswer |
| Context7 query-docs | free (cached) | library / API docs |

## Anti-patterns

- Don't pass `site:` / `"..."` to exa — it's neural, ignores operators
- Don't use firecrawl_search alone if you need content body —
  it returns links + descriptions only; chain with scrape if needed
- Don't auto-invoke `linkup-search depth=deep` — MCP returns only raw
  `searchResults`, not the synthesis output that justifies the 10× price
- Don't fan out searches across all three "just to be thorough" — pick one
- Don't skip Context7 for library docs and go straight to exa —
  Context7 is more accurate and free for that case

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
