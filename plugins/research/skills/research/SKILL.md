---
name: research
description: Multi-source deep research. Prefers firecrawl/exa MCPs, falls back to the bundled /deep-research workflow or built-in WebSearch when they are absent. Searches the web, synthesizes findings, and delivers cited reports with source attribution. Use when the user wants thorough research on any topic with evidence and citations.
origin: ECC
---

# Research

Produce thorough, cited research reports from multiple web sources — using firecrawl/exa MCP tools when available, otherwise the fallbacks below.

## When to Activate

- User asks to research any topic in depth
- Competitive analysis, technology evaluation, or market sizing
- Due diligence on companies, investors, or technologies
- Any question requiring synthesis from multiple sources
- User says "research", "deep dive", "investigate", or "what's the current state of"

## Backends — check availability before planning, not mid-run

Preferred, at least one of:
- **firecrawl** — `firecrawl_search`, `firecrawl_scrape`, `firecrawl_crawl`
- **exa** — `web_search_exa`, `web_fetch_exa` (the installed server exposes exactly these two; verified signatures live in the `search-routing` skill)

Both together give the best coverage. Configure them as MCP servers (`claude mcp add`, or the `mcpServers` block of your Claude Code config / `~/.codex/config.toml` for Codex). MCP servers are scoped **per config directory** — if you run more than one, a server added under one is absent under the other, so verify from the session you actually intend to research in.

**Check first: are the tools present in this session?** If neither backend is, do NOT plan a workflow around tools that will not answer. Fall back in this order:

1. **`/deep-research`** — the bundled dynamic workflow. It already does fan-out → fetch → cross-check → cited report on top of the built-in `WebSearch`, which is closer to this skill's output contract than anything you would improvise. Prefer it whenever the ask is a full multi-source report.
2. **Built-in `WebSearch` / `WebFetch`** — always available, no configuration. Use for narrower questions, and run the workflow below by hand: same sub-questions, same deep-read step, same citation rules, substituting `WebSearch` for `*_search` and `WebFetch` for `*_scrape` / `web_fetch_exa`.
3. **Any search CLI or skill your environment provides** — if one is installed and covers more sources than `WebSearch`, use it and say which.

Whichever you land on, **name it before searching** and record it in the report's Methodology section — coverage is not interpretable without it.

## Workflow

### Step 1: Understand the Goal

Ask 1-2 quick clarifying questions:
- "What's your goal — learning, making a decision, or writing something?"
- "Any specific angle or depth you want?"

If the user says "just research it" — skip ahead with reasonable defaults.

### Step 2: Plan the Research

Break the topic into 3-5 research sub-questions. Example:
- Topic: "Impact of AI on healthcare"
  - What are the main AI applications in healthcare today?
  - What clinical outcomes have been measured?
  - What are the regulatory challenges?
  - What companies are leading this space?
  - What's the market size and growth trajectory?

**Scenario checklists** — when the topic matches one of these modes, make sure the sub-questions collect:

- **Investor / fund diligence**: fund size, stage, and typical check size; relevant portfolio companies; public thesis and recent activity; concrete fit / no-fit reasons; obvious red flags or mismatches.
- **Competitive analysis**: product reality, not marketing copy; funding and investor history if public; traction metrics if public; distribution and pricing clues; strengths, weaknesses, and positioning gaps.
- **Market sizing**: top-down estimates from reports or public datasets; bottom-up sanity checks from realistic customer-acquisition assumptions; an explicit assumption stated for every leap in logic.
- **Technology / vendor evaluation**: how it works; trade-offs and adoption signals; integration complexity; lock-in, security, compliance, and operational risk.

### Step 3: Execute Multi-Source Search

For EACH sub-question, search using available MCP tools:

**With firecrawl:**
```
firecrawl_search(query: "<sub-question keywords>", limit: 8)
```

**With exa:**
```
web_search_exa(query: "<sub-question keywords>", numResults: 8)
```

Exa has no date-filter parameter. For recency-sensitive sub-questions, put the
time constraint in the query text (e.g. "<keywords> 2025", "<keywords> latest"),
or route to `firecrawl_search` with a date operator in the query
(e.g. `<keywords> after:2025-01-01`).

**Search strategy:**
- Use 2-3 different keyword variations per sub-question
- Mix general and news-focused queries
- Aim for 15-30 unique sources total
- Prioritize: academic, official, reputable news > blogs > forums

### Step 4: Deep-Read Key Sources

For the most promising URLs, fetch full content:

**With firecrawl:**
```
firecrawl_scrape(url: "<url>")
```

**With exa:**
```
web_fetch_exa(urls: ["<url>"], maxCharacters: 20000)
```

`web_fetch_exa` handles static pages. For JS-heavy or paywalled pages, prefer
`firecrawl_scrape`; to sweep a whole site section, use `firecrawl_crawl`.

Read 3-5 key sources in full for depth. Do not rely only on search snippets.

### Step 5: Synthesize and Write Report

Structure the report:

```markdown
# [Topic]: Research Report
*Generated: [date] | Sources: [N] | Confidence: [High/Medium/Low]*

## Executive Summary
[3-5 sentence overview of key findings]

## 1. [First Major Theme]
[Findings with inline citations]
- Key point ([Source Name](url))
- Supporting data ([Source Name](url))

## 2. [Second Major Theme]
...

## 3. [Third Major Theme]
...

## Key Takeaways
- [Actionable insight 1]
- [Actionable insight 2]
- [Actionable insight 3]

## Sources
1. [Title](url) — [one-line summary]
2. ...

## Methodology
Searched [N] queries across web and news. Analyzed [M] sources.
Sub-questions investigated: [list]
```

### Step 6: Deliver

- **Short topics**: Post the full report in chat
- **Long reports**: Post the executive summary + key takeaways, save full report to a file

## Parallel Research with Subagents

For broad topics, use the Agent tool to parallelize:

```
Launch 3 research agents in parallel:
1. Agent 1: Research sub-questions 1-2
2. Agent 2: Research sub-questions 3-4
3. Agent 3: Research sub-question 5 + cross-cutting themes
```

Each agent searches, reads sources, and returns findings. The main session synthesizes into the final report.

## Quality Rules

1. **Every claim needs a source.** No unsourced assertions.
2. **Cross-reference.** If only one source says it, flag it as unverified.
3. **Recency matters.** Prefer sources from the last 12 months.
4. **Acknowledge gaps.** If you couldn't find good info on a sub-question, say so.
5. **No hallucination.** If you don't know, say "insufficient data found."
6. **Separate fact from inference.** Label estimates, projections, and opinions clearly.

## Examples

```
"Research the current state of nuclear fusion energy"
"Deep dive into Rust vs Go for backend services in 2026"
"Research the best strategies for bootstrapping a SaaS business"
"What's happening with the US housing market right now?"
"Investigate the competitive landscape for AI code editors"
```
