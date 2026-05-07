# Claude Skills

**English** | [中文](README.zh-CN.md)

Yifan's personal Claude Code plugin marketplace — **13 plugins, 116 skills** for development workflow automation, design, language patterns, testing, research, and more.

## Plugins Overview

| Plugin | Skills | Purpose |
|--------|--------|---------|
| [`dev-workflow`](#dev-workflow) | 15 | Git PR automation, multi-agent impl, blueprints, browser routing, **grilling, diagnosis, codebase deepening, triage** |
| [`document`](#document) | 7 | A4 cheatsheets, doc co-authoring, PDF, docs lookup, codebase onboarding |
| [`work-tools`](#work-tools) | 1 | Feishu/Lark integration |
| [`writing`](#writing) | 5 | Vibe writing, articles, content engine, crosspost, video editing |
| [`design`](#design) | 23 | UI/UX Pro Max design family — design systems, styling, animation, audits |
| [`python`](#python) | 7 | Python and Django: patterns, testing, security, verification |
| [`swift`](#swift) | 6 | Swift/iOS: SwiftUI, concurrency, persistence, on-device LLM |
| [`web`](#web) | 9 | TS frontend, Node backend, MCP servers, Docker, deployment |
| [`data`](#data) | 5 | PostgreSQL, ClickHouse, migrations, PyTorch, automated scraping |
| [`quality`](#quality) | 14 | Testing, E2E, benchmarks, security review, coding standards |
| [`research`](#research) | 8 | Deep research, prompt optimization, cost-aware LLM pipelines |
| [`skills`](#skills) | 13 | Skill management — create, audit, evolve, promote |
| [`business`](#business) | 3 | Investor outreach, pitch materials, product evaluation |

---

## dev-workflow

Automated development workflows.

#### `/cpr` — Git PR Pipeline

One command from local changes to merged-ready PR. Claude automatically:

1. Detects current git state (uncommitted changes, existing PR, CI status)
2. Commits and pushes code, creates a PR via `gh`
3. Watches CI checks with `gh pr checks --watch`
4. On failure: reads error logs, fixes code, pushes again
5. On pass: reviews Copilot comments, fixes real issues (ignores false positives)
6. Loops steps 3–5 until everything is green

#### `/cl` — Copilot Lint Review

Reviews an existing PR (does not create one):

- Checks CI status and fixes build/lint failures locally
- Pulls Copilot review comments from the PR
- **Critically evaluates each suggestion** — only fixes real bugs, security issues, meaningful improvements
- Ignores over-defensive suggestions, false positives, style-only nitpicks
- Loops until CI passes and all valid comments are addressed

#### `/impl` — Multi-Agent Implementation

Orchestrates a team of specialized agents for larger features:

| Phase | Agent | What it does |
|-------|-------|--------------|
| 0 | **Planner** | 2–3 rounds of plan iteration in plan mode |
| 1 | **Implementer** | Writes code in an isolated git worktree |
| 2 | **Reviewer** | Code review (plan, standards, security, a11y) |
| 3 | **Tester** | Runs tests, Playwright screenshots, fixes bugs |
| 4 | **Reviewer** | Final review of test fixes |
| 5 | **Wrap-up** | Clean commit history, feature branch, PR |

#### `browser` — Browser MCP Routing

Selects the right browser tool by intent:

| Intent | MCP |
|--------|-----|
| Browse, fill forms, open pages | **browser-use** |
| Performance, debugging, network, console | **Chrome DevTools** |
| E2E testing, full flow testing | **Playwright** |

#### Other dev-workflow skills

- **`blueprint`** — Turn a one-line goal into a multi-session, multi-agent construction plan with self-contained context briefs, dependency graph, and adversarial review gate
- **`git-workflow`** — Branching strategies, commit conventions, merge vs rebase, conflict resolution
- **`repo-scan`** — Cross-stack source code asset audit, classifies every file, detects embedded third-party libs
- **`grill-me`** — Get relentlessly interviewed about a plan, one question at a time, until every branch of the design tree is resolved (lite version, no doc updates)
- **`grill-with-docs`** — Same grilling, but updates `CONTEXT.md` (domain glossary) and `docs/adr/` inline as terms and decisions crystallise — the producer of `CONTEXT.md` culture
- **`diagnose`** — 6-phase debug discipline (build a feedback loop → reproduce → ranked hypotheses → instrument with `[DEBUG-xxxx]` tags → fix + regression test → cleanup) for hard bugs and perf regressions
- **`improve-codebase-architecture`** — Find deepening opportunities (Module / Interface / Depth / Seam vocabulary, "deletion test" heuristic), present candidates, drop into a grilling loop on the chosen one
- **`prototype`** — Throwaway prototype with explicit branch decision: terminal TUI for state/logic questions, multi-variant UI on one route for design questions
- **`to-prd`** — Synthesize the current conversation into a PRD without re-interviewing; publishes to GitHub issue or saves to `docs/prds/`
- **`triage`** — Issue triage state machine (needs-triage / needs-info / ready-for-agent / ready-for-human / wontfix) with `.out-of-scope/` knowledge base for rejected enhancements
- **`caveman`** — Persistent ultra-compressed response mode (~75% token cut) that strips filler while keeping technical accuracy

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
- **`docs`** — Look up current docs for any library/framework via Context7
- **`codebase-onboarding`** — Generate onboarding guide for unfamiliar codebases (architecture map, entry points, conventions, starter CLAUDE.md)
- **`architecture-decision-records`** — Capture architectural decisions during sessions as structured ADRs
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

#### Other writing skills

- **`article-writing`** — Long-form articles in a distinctive voice
- **`content-engine`** — Platform-native content for X, LinkedIn, TikTok, YouTube, newsletters
- **`crosspost`** — Multi-platform distribution adapted per platform (no identical cross-posting)
- **`video-editing`** — AI-assisted video editing pipeline (FFmpeg, Remotion, ElevenLabs, fal.ai)

---

## design

UI/UX Pro Max design family — 23 skills covering the full design lifecycle:

**Foundation (5):** `ui-ux-pro-max` (router, 67 styles, 96 palettes, 13 stacks), `ui-styling` (shadcn/ui + Tailwind), `design-system` (token architecture), `brand`, `teach-impeccable`

**Enhance (4):** `delight`, `bolder`, `colorize`, `overdrive`

**Refine (4):** `quieter`, `distill`, `normalize`, `harden`

**Targeted (7):** `optimize`, `adapt`, `arrange`, `typeset`, `clarify`, `onboard`, `extract`

**Evaluate (3):** `audit`, `critique`, `codebase-to-course`

---

## python

Python and Django patterns:

- **`python-patterns`** — Pythonic idioms, PEP 8, type hints
- **`python-testing`** — pytest, TDD, fixtures, mocking, coverage
- **`python-review`** — Comprehensive code review
- **`django-patterns`** — Django architecture, DRF, ORM, caching
- **`django-security`** — Authn/authz, CSRF, SQL injection, XSS, secure deploy
- **`django-tdd`** — pytest-django, factory_boy, DRF testing
- **`django-verification`** — Migrations, linting, tests, security scans, deploy readiness

---

## swift

Swift and iOS development:

- **`swiftui-patterns`** — SwiftUI architecture, `@Observable`, navigation, performance
- **`swift-concurrency-6-2`** — Swift 6.2 Approachable Concurrency, `@concurrent`, isolated conformances
- **`swift-actor-persistence`** — Thread-safe persistence with actors (in-memory cache + file-backed storage)
- **`swift-protocol-di-testing`** — Protocol-based dependency injection for testable Swift
- **`liquid-glass-design`** — iOS 26 Liquid Glass material (blur, reflection, morphing)
- **`foundation-models-on-device`** — Apple FoundationModels for on-device LLM (`@Generable`, tool calling, streaming)

---

## web

TypeScript/Node web stack:

- **`frontend-patterns`** — React, Next.js, state management
- **`nextjs-turbopack`** — Next.js 16+ with Turbopack
- **`bun-runtime`** — Bun as runtime, package manager, bundler, test runner
- **`backend-patterns`** — Node/Express/Next API best practices
- **`api-design`** — REST API patterns (resources, status codes, pagination, errors, versioning)
- **`mcp-server-patterns`** — Build MCP servers with TS SDK (tools, resources, Zod, stdio vs HTTP)
- **`docker-patterns`** — Docker + Compose for local dev, security, networking
- **`deployment-patterns`** — CI/CD, containerization, health checks, rollback
- **`content-hash-cache-pattern`** — SHA-256 content-hash caching for expensive file processing

---

## data

Data engineering and ML:

- **`postgres-patterns`** — Query optimization, schema design, indexing, security
- **`clickhouse-io`** — Analytics database patterns and query optimization
- **`database-migrations`** — Zero-downtime schema changes (PostgreSQL, MySQL, Prisma, Drizzle, Django)
- **`pytorch-patterns`** — Training pipelines, model architectures, data loading
- **`data-scraper-agent`** — 100% free GitHub Actions data collection agent (Gemini Flash + Notion/Sheets/Supabase)

---

## quality

Code quality, testing, and review:

**Testing (8):**
- **`tdd-workflow`** — TDD with 80%+ coverage (unit + integration + E2E)
- **`e2e`** — Generate and run Playwright E2E tests with artifacts
- **`e2e-testing`** — Page Object Model, CI/CD integration, flaky test strategies
- **`benchmark`** — Performance baselines, regression detection
- **`browser-qa`** — Visual testing and UI verification post-deploy
- **`click-path-audit`** — Trace every button through state changes (find UI inconsistencies)
- **`canary-watch`** — Monitor deployed URLs for regressions
- **`ai-regression-testing`** — Catch AI blind spots when same model writes and reviews

**Review (6):**
- **`security-review`** — Comprehensive security checklist for auth, input, secrets, APIs
- **`security-scan`** — Scan `.claude/` config for vulnerabilities (CLAUDE.md, settings, hooks, agents)
- **`coding-standards`** — Universal standards for TypeScript, JavaScript, React, Node
- **`plankton-code-quality`** — Write-time auto-format/lint/fix on every edit via hooks
- **`safety-guard`** — Prevent destructive operations on production / autonomous agents
- **`santa-method`** — Multi-agent adversarial verification (two independent reviewers must both pass)

---

## research

Research and LLM engineering:

- **`deep-research`** — Multi-source research (firecrawl + exa MCPs) with citations
- **`market-research`** — Competitive analysis, investor due diligence
- **`search-first`** — Search for existing tools/libs/patterns before writing custom code
- **`exa-search`** — Neural search via Exa MCP (web, code, company)
- **`iterative-retrieval`** — Progressive context retrieval for subagent context problems
- **`prompt-optimize`** — Analyze a draft prompt, output optimized version (advisory, doesn't execute)
- **`cost-aware-llm-pipeline`** — Model routing by complexity, budget tracking, prompt caching
- **`regex-vs-llm-structured-text`** — Decision framework: start with regex, escalate to LLM only for low-confidence edges

---

## skills

Skill and instinct management system:

- **`skill-create`** — Extract patterns from git history, generate SKILL.md
- **`skill-comply`** — Visualize whether skills/rules/agents are actually followed
- **`skill-stocktake`** — Audit Claude skills/commands quality (Quick Scan + Full modes)
- **`skill-health`** — Skill portfolio health dashboard
- **`learn-eval`** — Extract reusable patterns from session, self-evaluate, decide save scope
- **`promote`** — Promote project-scoped instincts to global
- **`prune`** — Delete pending instincts older than 30 days
- **`evolve`** — Analyze and suggest evolved instinct structures
- **`projects`** — List projects with instinct statistics
- **`rules-distill`** — Extract cross-cutting principles from skills into rules
- **`instinct-status`** — Show learned instincts (project + global) with confidence
- **`instinct-import`** / **`instinct-export`** — Sync instincts across machines

---

## business

Fundraising and product evaluation:

- **`investor-outreach`** — Cold emails, warm intros, follow-ups, monthly updates
- **`investor-materials`** — Pitch decks, one-pagers, memos, accelerator apps, financial models
- **`product-lens`** — Validate the "why" before building, product diagnostics, vague-idea-to-spec

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
claude plugin install python@yifan-personal
# ... etc
```

Or install all 13 at once:

```bash
for p in dev-workflow document work-tools writing design python swift web data quality research skills business; do
  claude plugin install "$p@yifan-personal"
done
```

## Usage

```
> /cpr                            # Push code through full PR pipeline
> /cl                             # Review and fix Copilot lint comments
> /impl                           # Multi-agent coordinated implementation
> /docs react server components   # Look up current React docs
> write an article about...       # Triggers vibe-writing
> create a cheatsheet for...      # Triggers cheatsheet
> deep research on X              # Triggers deep-research
> review this code for security   # Triggers security-review
```

Most skills auto-trigger from natural language matching their description.

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- GitHub CLI (`gh`) for cpr/cl workflows
- Browser MCP servers for `browser` skill
- Feishu MCP server for `feishu` skill
- Various API keys depending on skill (Exa, firecrawl, Context7, etc.)

## License

MIT
