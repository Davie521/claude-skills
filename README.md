# Claude Skills

**English** | [中文](README.zh-CN.md)

Yifan's personal Claude Code plugin marketplace — **15 plugins, 52 skills + 5 review agents + 1 review command** for development workflow automation, design, language patterns, testing, research, and more.

## Plugins Overview

| Plugin | Skills | Purpose |
|--------|--------|---------|
| [`dev-workflow`](#dev-workflow) | 10 | Git PR automation with auto-merge, deep planning, **grilling, diagnosis, codebase deepening, triage** |
| [`document`](#document) | 4 | A4 cheatsheets, doc co-authoring, PDF, visa doc translation |
| [`work-tools`](#work-tools) | 1 | Feishu/Lark integration |
| [`writing`](#writing) | 3 | Vibe writing with voice capture, multi-platform crosspost, video editing |
| [`design`](#design) | 3 | UI/UX Pro Max, UX critique, codebase-to-course |
| [`swift`](#swift) | 4 | Swift/iOS: SwiftUI + architecture patterns, concurrency, Liquid Glass, on-device LLM |
| [`web`](#web) | 6 | REST APIs, MCP servers, Docker, deployment, Bun, content-hash caching |
| [`data`](#data) | 3 | PostgreSQL, migrations, automated scraping |
| [`quality`](#quality) | 8 | TDD, E2E, security review/scan, adversarial verification |
| [`code-review`](#code-review) | 5 agents + 1 cmd | `/code-review` auto-dispatches to language specialist (Python/TypeScript/Swift) + mandatory security review |
| [`research`](#research) | 4 | Deep research incl. market research, search routing, cost-aware LLM pipelines |
| [`skills`](#skills) | 3 | Skill management — stocktake, compliance audit, rules distillation |
| [`business`](#business) | 1 | Investor materials with outreach cadence |
| [`codex`](#codex) | 2 | Codex MCP second opinion — code review, design challenge |
| [`session-summary`](#session-summary) | hooks only | Session summary hooks and scripts (no skills) |

---

## dev-workflow

Automated development workflows.

#### `/cpr` — Git PR Pipeline

One command from local changes to merged PR. The old Copilot Lint review workflow is absorbed here — saying `cl` still triggers it. Claude automatically:

1. Detects current git state (uncommitted changes, existing PR, CI status)
2. Commits and pushes code, creates a PR via `gh`
3. Watches CI checks with `gh pr checks --watch`
4. On failure: reads error logs, fixes code, pushes again
5. On pass: pulls Copilot review comments from the PR
6. Judges each comment against a must-fix / ignorable table — fixes real bugs and security issues, ignores over-defensive suggestions, false positives, style-only nitpicks
7. Loops steps 3–6 until everything is green
8. Auto-merges once CI is fully green — pauses the merge and notifies you if any review hasn't passed

#### Other dev-workflow skills

- **`grill-with-docs`** — Get relentlessly interviewed about a plan, one question at a time, challenged against your project's domain model; updates `CONTEXT.md` (domain glossary) and `docs/adr/` (structured per its bundled `ADR-FORMAT.md`) inline as terms and decisions crystallise — the producer of `CONTEXT.md` culture. Without a `CONTEXT.md` it drops to a lite mode: grilling only, no doc writes. Saying "grill me" still triggers it
- **`diagnose`** — 6-phase debug discipline (build a feedback loop → reproduce → ranked hypotheses → instrument with `[DEBUG-xxxx]` tags → fix + regression test → cleanup) for hard bugs and perf regressions
- **`improve-codebase-architecture`** — Find deepening opportunities (Module / Interface / Depth / Seam vocabulary, "deletion test" heuristic), present candidates, drop into a grilling loop on the chosen one
- **`prototype`** — Throwaway prototype with explicit branch decision: terminal TUI for state/logic questions, multi-variant UI on one route for design questions
- **`to-prd`** — Synthesize the current conversation into a PRD without re-interviewing; publishes to GitHub issue or saves to `docs/prds/`
- **`triage`** — Issue triage state machine (needs-triage / needs-info / ready-for-agent / ready-for-human / wontfix) with `.out-of-scope/` knowledge base for rejected enhancements
- **`caveman`** — Persistent ultra-compressed response mode (~75% token cut) that strips filler while keeping technical accuracy
- **`deep-plan`** — Restate requirements, assess risks, phase-by-phase plan, WAIT for explicit confirmation; on approval the first action is a mandatory isolated git worktree, then post-implementation handoff to `/cpr` or code review
- **`cleanup`** — End-of-session cleanup: shut down every process the session started, sync stale docs against the diff, drive leftover tasks to zero (finish or explicitly report), persist lessons to memory — Phase 4 extracts reusable patterns from the session, self-evaluates, and decides save scope; every phase must end with an evidence-backed done / not-needed verdict

---

## document

#### `cheatsheet` — Printable A4 Cheatsheet Creator

Creates dense, exam-ready cheatsheets from Markdown:

- **A4 landscape**, 5-column layout, 6pt font — maximum information density
- Supports LaTeX math, tables, highlighted blocks, notes
- Multi-page output. Pipeline: Markdown → `python3 md2html.py input.md` → HTML → PDF

#### Other document skills

- **`doc-coauthoring`** — Structured workflow for co-authoring proposals, specs, decision docs
- **`pdf`** — PDF extraction, generation, forms, OCR
- **`visa-doc-translate`** — Translate visa application documents (images) to English bilingual PDF

---

## work-tools

#### `feishu` — Feishu/Lark Integration

Operates Feishu (Lark) via MCP server:

- Send messages to users or groups
- Create group chats
- Create and edit documents
- Upload files
- Query user information

Requires a Feishu MCP server.

---

## writing

#### `vibe-writing` — AI Writing Assistant

4-phase co-writing workflow where you lead, AI assists:

| Phase | Trigger | What happens |
|-------|---------|--------------|
| **Learn** | Default | Socratic dialogue — every 4 rounds generates a knowledge card |
| **Structure** | "structure" | Proposes 2–3 article structures (problem-solution, comparison, progressive, story, listicle, SCQA) |
| **Write** | "write" / "iterate" | "organize" consolidates, "polish" refines language |
| **Finalize** | "finalize" | Chains output cards + transitions + intro/conclusion |

Also owns long-form voice: a five-dimension voice-capture checklist plus a banned list of AI-flavored words.

#### Other writing skills

- **`crosspost`** — Multi-platform distribution adapted per platform (no identical cross-posting), with per-platform essentials for the three platforms and a repurposing cascade from one source asset. Drafts only — never posts
- **`video-editing`** — AI-assisted video editing pipeline (FFmpeg, Remotion, ElevenLabs, fal.ai)

---

## design

Three skills. Anti-slop discipline lives in [Hallmark](https://github.com/Nutlope/hallmark);
measured a11y/perf auditing lives in the `chrome-devtools` MCP (`lighthouse_audit`).
This plugin covers what neither of those does.

- **`ui-ux-pro-max`** — design intelligence: 67 styles, 96 palettes, 57 font pairings,
  13 stacks, searchable DB. Emits `design-system/MASTER.md` + a root `design.md`
  pointer so Hallmark sees the project as system-managed.
  See `reference/design-system-map.md` for routing to official design systems
  (Fluent, Material 3, Carbon, Polaris, Atlaskit, Primer, govuk-frontend, USWDS).
- **`critique`** — UX evaluation: cognitive load, emotional journey (peak-end),
  visual hierarchy, discoverability, persona red flags. 10 dimensions + scoring
  + 5 user archetypes. Answers "does this experience work", not "does this look AI-made".
- **`codebase-to-course`** — turn a codebase into an interactive HTML course.

The 20 single-verb skills (`bolder`, `quieter`, `distill`, `audit`, …) were removed
2026-08-08: zero invocations, and their dispatcher depended on a disabled
`frontend-design` skill.

---

## swift

Swift and iOS development:

- **`swiftui-patterns`** — SwiftUI architecture, `@Observable`, navigation, performance; includes an Architecture Patterns section (actor-based thread-safe persistence, protocol-based dependency injection for testing)
- **`swift-concurrency-6-2`** — Swift 6.2 Approachable Concurrency, `@concurrent`, isolated conformances
- **`liquid-glass-design`** — iOS 26 Liquid Glass material (blur, reflection, morphing)
- **`foundation-models-on-device`** — Apple FoundationModels for on-device LLM (`@Generable`, tool calling, streaming)

---

## web

TypeScript/Node web stack:

- **`bun-runtime`** — Bun as runtime, package manager, bundler, test runner
- **`api-design`** — REST API patterns (resources, status codes, pagination, errors, versioning)
- **`mcp-server-patterns`** — Build MCP servers with TS SDK (tools, resources, Zod, stdio vs HTTP)
- **`docker-patterns`** — Docker + Compose for local dev, security, networking
- **`deployment-patterns`** — CI/CD, containerization, health checks, rollback
- **`content-hash-cache-pattern`** — SHA-256 content-hash caching for expensive file processing

---

## data

Data engineering:

- **`postgres-patterns`** — Query optimization, schema design, indexing, security
- **`database-migrations`** — Zero-downtime schema changes (PostgreSQL, MySQL, Prisma, Drizzle, Django)
- **`data-scraper-agent`** — 100% free GitHub Actions data collection agent (Gemini Flash + Notion/Sheets/Supabase)

---

## quality

Code quality, testing, and review:

**Testing (4):**
- **`tdd-workflow`** — TDD with 80%+ coverage (unit + integration + E2E)
- **`e2e-testing`** — Page Object Model, CI/CD integration, flaky test strategies
- **`click-path-audit`** — Trace every button through state changes (find UI inconsistencies)
- **`ai-regression-testing`** — Catch AI blind spots when same model writes and reviews

**Review (4):**
- **`security-checklist`** — Comprehensive security checklist for auth, input, secrets, APIs (not the built-in `/security-review` command)
- **`security-scan`** — Scan `.claude/` config for vulnerabilities (CLAUDE.md, settings, hooks, agents)
- **`plankton-code-quality`** — Write-time auto-format/lint/fix on every edit via hooks
- **`santa-method`** — Multi-agent adversarial verification (two independent reviewers must both pass)

---

## code-review

Multi-language code review with auto-dispatch. Single command (`/code-review`) detects which languages changed and runs the matching specialist agents in parallel, plus a mandatory security pass.

**Command:**
- **`/code-review`** — Local uncommitted changes review, or `/code-review <pr>` for GitHub PR review (fetches diff, validates, posts review)

**Agents (5):**
- **`code-reviewer`** — General-purpose fallback when no language specialist matches
- **`python-reviewer`** — PEP 8, Pythonic idioms, type hints, security (bandit), Django/FastAPI/Flask patterns
- **`typescript-reviewer`** — Type safety, async correctness, React/Next.js patterns, Node security
- **`swift-reviewer`** — Swift 6 concurrency, value types, actor patterns, SwiftUI, Keychain/ATS security
- **`security-reviewer`** — OWASP Top 10, secrets detection, injection, unsafe crypto. Always invoked by `/code-review` regardless of language.

---

## research

Research and LLM engineering:

- **`search-routing`** — Pick one search MCP (exa / firecrawl / linkup) by query shape; cheapest sufficient tool, deep modes need confirmation
- **`research`** — Multi-source research (firecrawl + exa MCPs) with citations; scenario-based collection checklists for investor due diligence, competitor analysis, market sizing, and vendor evaluation
- **`cost-aware-llm-pipeline`** — Model routing by complexity, budget tracking, prompt caching
- **`regex-vs-llm-structured-text`** — Decision framework: start with regex, escalate to LLM only for low-confidence edges

---

## skills

Skill management:

- **`skill-stocktake`** — Audit Claude skills/commands quality (Quick Scan + Full modes)
- **`skill-comply`** — Visualize whether skills/rules/agents are actually followed
- **`rules-distill`** — Extract cross-cutting principles from skills into rules

---

## business

Fundraising:

- **`investor-materials`** — Pitch decks, one-pagers, memos, accelerator apps, financial models; includes an Outreach section with a day 0 → day 4–5 → day 10–12 follow-up cadence

---

## codex

Second opinion via Codex MCP — read-only, never edits:

- **`codex-review`** — Default code review route. Codex runs the multi-language review methodology (severity matrix, `file:line`, mandatory security pass). Fall back to `code-review` only when you explicitly want Claude subagents or auto-applied fixes.
- **`design-challenge`** — Challenges the approach, not the code. Returns assumptions / failure modes / alternatives instead of a bug list.

---

## session-summary

Hooks and scripts only — no skills. Session analytics dashboard printed when a session ends (15 configurable sections). Vendored from [FlorianBruniaux/claude-code-plugins](https://github.com/FlorianBruniaux/claude-code-plugins), MIT.

---

## Installation

Add this marketplace to Claude Code:

```bash
claude plugin marketplace add Davie521/claude-skills
```

Then install plugins individually:

```bash
claude plugin install dev-workflow@yifan-personal
claude plugin install design@yifan-personal
claude plugin install swift@yifan-personal
# ... etc
```

Or install all 15 at once:

```bash
for p in dev-workflow document work-tools writing design swift web data quality code-review research skills business codex session-summary; do
  claude plugin install "$p@yifan-personal"
done
```

## Usage

```
> /cpr                            # Full PR pipeline incl. auto-merge ('cl' also triggers it)
> write an article about...       # Triggers vibe-writing
> create a cheatsheet for...      # Triggers cheatsheet
> deep research on X              # Triggers research
> review this code for security   # Triggers security-checklist
```

Most skills auto-trigger from natural language matching their description.

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- GitHub CLI (`gh`) for the cpr workflow
- Feishu MCP server for `feishu` skill
- Various API keys depending on skill (Exa, firecrawl, Context7, etc.)

## License

MIT
