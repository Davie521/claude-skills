# Claude Skills

**English** | [中文](README.zh-CN.md)

Yifan's personal Claude Code plugin marketplace — **15 plugins, 50 skills + 5 review agents + 1 review command** for development workflow automation, design, language patterns, testing, research, and more.

Every skill below names what it's for in its heading, then states how it's **triggered** and how it actually **works** inside. Where the heading isn't enough, an explicit **For** line spells the purpose out.

## Plugins Overview

| Plugin | Skills | Purpose |
|--------|--------|---------|
| [`dev-workflow`](#dev-workflow) | 10 | Git PR automation with auto-merge, deep planning, **grilling, diagnosis, codebase deepening, triage** |
| [`document`](#document) | 5 | A4 cheatsheets, doc co-authoring, PDF, visa doc translation, codebase-to-course |
| [`work-tools`](#work-tools) | 1 | Feishu/Lark integration |
| [`writing`](#writing) | 3 | Vibe writing with voice capture, multi-platform crosspost, video editing |
| [`design`](#design) | 2 | UI/UX Pro Max, UX critique |
| [`swift`](#swift) | 4 | Swift/iOS: SwiftUI + architecture patterns, concurrency, Liquid Glass, on-device LLM |
| [`web`](#web) | 6 | REST APIs, MCP servers, Docker, deployment, Bun, content-hash caching |
| [`data`](#data) | 2 | Migrations + PostgreSQL quick reference, automated scraping |
| [`quality`](#quality) | 8 | TDD, E2E, security review/scan, adversarial verification |
| [`code-review`](#code-review) | 5 agents + 1 cmd | `/code-review` auto-dispatches to language specialist (Python/TypeScript/Swift) + mandatory security review |
| [`research`](#research) | 3 | Deep research incl. market research, search routing, LLM cost discipline |
| [`skills`](#skills) | 3 | Skill management — stocktake, compliance audit, rules distillation |
| [`business`](#business) | 1 | Investor materials with outreach cadence |
| [`codex`](#codex) | 2 | Codex MCP second opinion — code review, design challenge |
| [`session-summary`](#session-summary) | hooks only | Session summary hooks and scripts (no skills) |

**Actually used, in order** (counted by skill injections, not tool calls): `deep-plan` › `/cpr` › `santa-method` › `research` › `ui-ux-pro-max`. Those five carry the daily load; the rest is reference material waiting for its topic — zero invocations doesn't mean zero value when a skill exists for one specific situation.

---

## dev-workflow

Automated development workflows. The workhorse group — `deep-plan` and `/cpr` are the two most-used skills in the repo.

### `/cpr` — Git PR Pipeline

**For**: one command from local changes to a merged PR, without stopping to ask between steps.
**Trigger**: say `cpr` or `cl` (the old Copilot Lint review workflow is absorbed here; `cl` still triggers it)

It resumes from wherever you already are — `gh pr view --json number,state`, `gh pr checks` and `git status` decide the entry point (no PR → create one; CI running → wait; CI failed → fix; CI green → check comments; all green and comments handled → merge).

1. **Branch check** — if you're on `main`, cut a branch first
2. **Commit** — `git add` + `git commit`
3. **Push + create PR** — `git push -u` + `gh pr create`
4. **Watch CI** — `gh pr checks --watch`; on `no checks reported`, confirm with `[ -d .github/workflows ]` whether the repo has no CI at all, and skip to step 6 if so
5. **On failure** — `gh run view <id> --log-failed` → fix → push
6. **Copilot comments** — request the review first if it didn't fire on its own, then read both `gh pr view --comments` *and* `gh api repos/{owner}/{repo}/pulls/$PR_NUMBER/comments` → judge each one → fix only what's necessary → push
7. **Loop 4–6** until everything is green
8. **Auto-merge** — `gh pr merge --merge --delete-branch` once all checks pass and no review is outstanding; if a review requested changes or hasn't passed, pause the merge and notify you

Step 6 is the opinionated part — **don't blindly apply every Copilot suggestion**:

| Must fix | Safe to ignore |
|----------|----------------|
| SQL injection, XSS, leaked secrets | Over-defensive suggestions |
| Bugs that actually cause problems | False positives |
| Style issues that seriously hurt readability | Pure style preference |
| Obvious performance problems | Micro-optimization, premature optimization |
| Changes with real benefit | Dogmatic advice |

The test is: is this a real problem *in this context*, does fixing it actually gain anything, does it fit the project? Each comment gets an explicit `fix: [reason]` / `ignore: [reason]` verdict.

> **Three traps it encodes.** *Comments live in two places*: Copilot's inline review comments only exist in the REST response at `repos/{owner}/{repo}/pulls/<n>/comments` — `gh pr view --comments` returns conversation-level comments only, so checking just that misses **every** code comment. *Exit 1 is ambiguous*: `gh pr checks` exits non-zero both when checks fail and when nothing reported for this head commit (`no checks reported`) — the second is not a failure and must not block the merge, though it proves only that no check ran, so confirm against `.github/workflows` before concluding the repo has no CI. *Review often needs asking*: Copilot doesn't always auto-trigger, and only the `copilot-pull-request-reviewer[bot]` slug can request it (plain `Copilot` gives "not found", the bare slug 422s); comments then take 2–3 minutes, so poll instead of checking once.

### `deep-plan` — The planning gate before any code

**For**: restate, assess risk, phase the work, and wait for your approval before touching anything. Most-used skill in the repo.
**Trigger**: automatic on new features, architectural changes, complex refactors, multi-file changes, or unclear requirements; or say deep-plan

- **Phase A (read-only)**: restate requirements and dependencies → assess risk and complexity → propose a phased plan → **hard-wait** for explicit approval. `modify:`, `different approach:`, `skip phase 2` steer the plan instead of restarting it.
- **Phase B (first action after approval)**: create an isolated worktree — a sibling `git worktree add ../<repo>_<slug>` on branch `plan-<slug>` (directory and branch are bound, not chosen independently). Nested trees can't run docker bind-mounts, so they're only a fallback for simple docker-free repos.
  - Three checks that look right and aren't: `git rev-parse --show-toplevel` cannot tell a main worktree from a linked one (both return a path); comparing `--git-dir` against `--git-common-dir` **also fails unless you add `--path-format=absolute`**, because from a subdirectory git returns one absolute and one relative path and the main worktree reads as linked; and `git symbolic-ref refs/remotes/origin/HEAD` is **fatal**, not empty, when origin/HEAD is unset — `git remote set-head origin -a` first.
- **Phase C**: implement inside the tree, then hand off to `/cpr` or code review.

> **Note**: never editing the main worktree is a hard precondition of this skill, not a suggestion.

### `cleanup` — Four-phase end-of-session cleanup

**For**: actually clearing the site, with an evidence-backed verdict per phase.
**Trigger**: say cleanup / 收尾 / 清理现场, or before handing off a long task

1. **Kill processes**: verify lineage with `ps -o pid,ppid,lstart` and `lsof` before killing — orphans reparent to launchd, so trusting PPID kills the wrong thing; Docker stacks with `restart: unless-stopped` must be torn down, killing containers just brings them back.
2. **Sync docs**: fix the docs to match the code, **never the reverse**; also re-scan the conversation for "update the README" style promises that were never executed.
3. **Drive tasks to zero**: every TaskList item, every TODO introduced this session, temp files removed with `trash` (recoverable — not `rm -rf`).
4. **Persist memory**: only knowledge that still holds next session; Global vs Project has a decision rule (when unsure, Global); merge into an existing memory file rather than creating a new one.

Ends with a four-line evidence table. **Under-reporting is the only failure** — "nothing needed here" is a legitimate verdict, silently skipping is not.

### `diagnose` — Six-phase debug discipline

**For**: hard bugs and perf regressions, with falsifiable evidence at every step.
**Trigger**: say diagnose / debug this, or describe something broken, throwing, or slow

Build a feedback loop (a fast way to verify, or everything after is guesswork) → reproduce → list 3–5 hypotheses ranked by likelihood → instrument with a unique `[DEBUG-xxxx]` prefix (one grep cleans it all up afterwards) → fix + add a regression test → remove every probe. "I think it's here, let me just change it" is precisely what it blocks.

### `grill-with-docs` — It interrogates you, and writes the docs

**For**: attacking your plan one question at a time while crystallised terms and decisions land in the project's docs — the producer of `CONTEXT.md` culture.
**Trigger**: say grill me, or ask to stress-test / challenge a plan

One question at a time, each with a recommended answer, pressed against the project's domain model (the `CONTEXT.md` glossary) until every branch of the decision tree resolves. `CONTEXT.md` and `docs/adr/` update inline as it goes. ADRs follow the bundled `ADR-FORMAT.md` and must clear three admission gates — **hard to reverse / surprising without context / the outcome of a real trade-off** — miss one and it's skipped, plus a consent gate before anything is written. That's what keeps ADR sprawl down; `docs/adr/README.md` maintains the index for reading back.

> **Note**: with no `CONTEXT.md` in the project it drops to lite mode — grilling only, no doc writes.

### `improve-codebase-architecture` — Find deepening opportunities systematically

**For**: refactoring driven by vocabulary rather than vibes.
**Trigger**: when you want better architecture, refactoring candidates, or a codebase that's easier to test and for AI to navigate

Forces the Module / Interface / Depth / Seam vocabulary onto the analysis, paired with the "deletion test" heuristic ("what breaks if this abstraction disappears?") to surface candidates. You pick one, it drops into a grilling loop to validate it, then hands off to `deep-plan` for execution.

### `prototype` — Throwaway prototypes

**For**: flushing out a design question before committing — two scenarios only.
**Trigger**: you need to compare structurally different UI approaches side by side, or step through a state machine / data model by hand

Forced branch decision: logic / state / data-model questions → a runnable terminal TUI so you drive the state machine yourself; UI questions → several **structurally different** variants on one route with a toggle bar. The output is explicitly disposable; code quality is not the goal.

> **Note**: triggers are deliberately narrow (generic phrases like "mock up a UI" were removed) so ordinary UI work doesn't land here. For a real page, use `ui-ux-pro-max` / Hallmark.

### `to-prd` — Turn the current conversation into a PRD

**For**: converting an existing discussion into a document without re-interviewing you.
**Trigger**: after the requirements discussion, say to-prd

Extracts goals, scope, decisions and constraints from conversation context and produces a PRD — saved to `docs/prds/` by default, published to a GitHub issue only on request. The key behavioural constraint is **no second interview**: it assumes the questions were already asked.

### `triage` — Issue triage state machine

**For**: sorting incoming bugs and requests to where they belong, and remembering what was rejected.
**Trigger**: creating issues, triaging incoming work, prepping issues for an AFK agent

Five states — needs-triage / needs-info / ready-for-agent / ready-for-human / wontfix — each with explicit entry conditions and a next action. Ships with an `.out-of-scope/` rejection knowledge base: a wontfix'd enhancement gets its reason recorded once, and the next similar request is answered by linking to it instead of re-arguing.

### `caveman` — Persistent compressed replies

**For**: stripping articles, filler and pleasantries while keeping all technical content.
**Trigger**: **explicit invocation only** — `/caveman` or "caveman mode"

Stays on until explicitly exited (stop caveman / normal mode / exit caveman). The compression is English-side (drops `a/an/the`, `just/really`, abbreviates DB/auth/config), so gains in Chinese conversation are limited — Chinese has no articles to drop.

> **Note**: "be brief" does *not* trigger it — a one-off style request shouldn't drop you into a persistent mode.

---

## document

### `cheatsheet` — Printable A4 cheatsheet creator

**Trigger**: making a cheatsheet, crib sheet, revision sheet, or condensed reference

A4 landscape, 5 columns, 6pt font — maximum information density. Supports LaTeX math, tables, highlight blocks, notes, multi-page output. Pipeline: write `.md` in the custom syntax → `python3 "${CLAUDE_PLUGIN_ROOT}/skills/cheatsheet/scripts/md2html.py" input.md -o output.html` → print to PDF from the browser. The converter is zero-dependency Python; the syntax spec is `references/cheatsheet_spec.md`.

### `pdf` — Full PDF toolkit

**Trigger**: processing PDFs — extracting text/tables, filling forms, splitting/merging, converting to images

9 pypdf/pdf2image/pdfplumber scripts. The form path is the complete chain: `check_fillable_fields.py` decides whether the PDF is fillable at all → `extract_form_field_info.py` pulls field info → `fill_fillable_fields.py` fills it. Non-fillable PDFs take the annotation route, which prefers exact coordinates over eyeballing: `extract_form_structure.py` (pdfplumber) reads labels, rules and checkbox squares straight out of the PDF, falling back to zoomed visual estimation only for scanned pages → `check_bounding_boxes.py` catches overlaps and undersized boxes → `fill_pdf_form_with_annotations.py` auto-detects whether your `fields.json` is in PDF points or image pixels and fills accordingly → `create_validation_image.py` renders a verification image (image-coordinate flow) so you can eyeball placement.

> **Prerequisites**: a venv (`python3 -m venv` — `--break-system-packages` is explicitly forbidden), plus system poppler for `pdf2image`.

### `doc-coauthoring` — Structured document co-authoring

**Trigger**: co-writing a real document — proposal, technical spec, decision doc

Three phases: ① gather context (clarifying questions → brainstorm → material triage loop); ② build the skeleton with Write, sections as placeholders; ③ draft and revise section by section with Edit — surgical changes confirmed one at a time, never a full-document rewrite. Can also spawn a sub-agent for **Reader Testing**: read the draft as the target reader and report where it snags.

### `visa-doc-translate` — Visa document translation

**Trigger**: translating visa application materials (images) into English

HEIC→PNG via `sips` → EXIF rotation correction → the model reads and translates the images directly → bilingual PDF laid out with PIL + reportlab. Output is an **uncertified draft** for a human translator to review and certify — it carries that disclaimer in its footer and filename, and must not be filed as-is.

> **Note**: no OCR library — in practice Claude reading the image directly beat three OCR backends that weren't even installed. Anything unreadable is marked `[illegible]`, never guessed; on visa paperwork a guessed character is a real problem.

### `codebase-to-course` — Codebase into an interactive course

**Trigger**: say "turn this into a course", or ask how a codebase works as a walkthrough

The target reader is a **vibe coder** — someone who directs AI to write code but has no CS training. Four phases: deep-read the codebase (trace data flow, identify the "characters") → design a 5–8 module outline (drill down from behaviour the user already knows) → generate one self-contained HTML file → open it in a browser and walk it. Five interaction types are mandatory: component group-chat animation, data-flow animation, code ↔ plain-English pairing, scenario quizzes, term tooltips. Content discipline: never abridge the real code, never reuse a metaphor (no restaurant analogies), at least half of every screen is visual.

---

## work-tools

### `feishu` — Feishu/Lark integration

**For**: sending messages, creating groups, importing/reading docs, looking up users. No file upload/download and no direct cloud-doc editing — official lark-mcp limitations.
**Trigger**: Feishu/Lark is mentioned, or you want to message a Feishu group / import or read a Feishu doc / find a contact

Runs on the official lark-mcp CLI MCP server (tools look like `mcp__feishu__im_v1_message_create`), covering IM, docx, drive and wiki APIs.

> **Prerequisite**: the feishu MCP server must be configured. If those tools are absent, the skill tells you to configure it rather than guessing at an API shape.

---

## writing

### `vibe-writing` — Four-phase co-writing

**For**: you lead, AI assists — and **your wording survives**.
**Trigger**: say 写作 / 写文章 / 帮我写 / vibe

| Phase | Trigger | What happens |
|-------|---------|--------------|
| **Learn** | Default | Socratic dialogue — every 4 rounds produces a knowledge card |
| **Structure** | "structure" | 2–3 article structures (problem-solution, comparison, progressive, story, listicle, SCQA) |
| **Write** | "write" / "iterate" | "organize" consolidates, "polish" fact-checks and tightens language |
| **Finalize** | "finalize" | Chains the cards with transitions, intro and conclusion |

Voice consistency has two concrete tools: a **five-dimension voice-capture checklist** (sentence rhythm, tone, recurring rhetoric, tolerance for humour, formatting habits) and a **banned AI-flavored word list** (canned openers, Moreover/Furthermore, game-changer — spotted means rewritten).

### `crosspost` — One asset, seven native versions

**For**: multi-platform distribution with per-platform adaptation. **Drafts only, never posts.**
**Trigger**: distributing or repurposing content across platforms

Covers X, LinkedIn, Threads, Bluesky, TikTok, YouTube and newsletters, each with its character limit, link handling, hashtag convention and native adaptation notes (TikTok buys attention in the first 3 seconds; YouTube leads with the result and runs on chapters; a newsletter holds one angle and stays scannable). Repurposing cascade: anchor asset → 3–7 atomic points → per-platform rewrite → dedupe → CTA matched to platform intent.

> **Note**: identical copy is never cross-posted. Publishing is yours to do; the skill suggests a staggered schedule.

### `video-editing` — AI-assisted editing pipeline for real footage

**For**: raw capture through to finished cut, in five layers.
**Trigger**: editing video, cutting footage, making vlogs, structuring raw material

Ingest (VideoDB Python SDK, desktop capture with real-time context) → FFmpeg rough cut → Remotion programmatic composition → ElevenLabs voiceover → fal.ai for generated B-roll → final polish in Descript / CapCut. Each layer gives runnable commands and code, not a concept diagram.

---

## design

Two skills. Anti-slop discipline lives in [Hallmark](https://github.com/Nutlope/hallmark);
measured a11y/perf auditing lives in the `chrome-devtools` MCP (`lighthouse_audit`).
This plugin covers what neither of those does.

### `ui-ux-pro-max` — Design knowledge base + project design system

**For**: a searchable design-selection library, plus persisting the result as a project design system. Fifth most-used skill.
**Trigger**: building a site or landing page, choosing UI style / palette / fonts / charts

67 styles, 96 palettes, 57 font pairings, 25 chart types and 13 stacks as CSV, searched with BM25 via `scripts/search.py`. `--design-system --persist` writes `design-system/<project-slug>/MASTER.md` plus per-page overrides, and drops a root `design.md` pointer so Hallmark reads the project as system-managed instead of flagging variety drift. The official design-system routing table (`reference/design-system-map.md`) covers Fluent, Material 3, Carbon, Polaris, Atlaskit, Primer, govuk-frontend and USWDS.

### `critique` — UX evaluation

**For**: answering "does this experience work", not "does this look AI-made".
**Trigger**: say review / critique / 评审这个设计

Scores 10 dimensions (visual hierarchy, information architecture, cognitive load, emotional journey including peak-end, discoverability and more), auto-picks the 2–3 most relevant of 5 user archetypes for a walkthrough, and returns a red-flag list with actionable feedback. When tone doesn't match the product, it asks whether that was deliberate before calling it a defect.

> **Division of labour**: diagnosis only — producing or changing a design is `ui-ux-pro-max`.

The 20 single-verb skills (`bolder`, `quieter`, `distill`, `audit`, …) were removed
2026-08-08: zero invocations, and their dispatcher depended on a disabled
`frontend-design` skill.

---

## swift

What's kept here is **version-specific knowledge from after the training cutoff** — the parts a model is unreliable on from memory.

### `swiftui-patterns` — SwiftUI architecture and state

**Trigger**: SwiftUI architecture, state management, navigation, performance questions

State management in the `@Observable` era (`@State` + `@Observable` view models, `@Environment` injection), navigation patterns, performance work. The Architecture Patterns section carries two worked patterns:

- `LocalRepository<T>` actor — in-memory dictionary cache + atomic JSON writes, **shipped with its own boundary warning**: every write rewrites the whole dataset, so move to GRDB/SwiftData for high write volume or large datasets
- Protocol-per-boundary dependency injection — `FileAccessor` protocol + mock + Swift Testing coverage, self-consistent and compilable

### `swift-concurrency-6-2` — Approachable Concurrency migration

**Trigger**: migrating to Swift 6.2 concurrency, adopting `@concurrent`, fighting data-race errors

The 6.2 shift: single-threaded by default (MainActor inference), explicit `@concurrent` to offload to the background, isolated conformances so main-actor types can safely conform to protocols. Includes concrete fixes for "sending X risks causing data races".

### `liquid-glass-design` — iOS 26 Liquid Glass

**Trigger**: bringing a native Apple app to the iOS 26 glass design language

Dynamic glass material — blur, reflection, interactive morphing — across SwiftUI `glassEffect`, UIKit `UIGlassEffect` and WidgetKit.

> **Not this**: web frosted glass (CSS `backdrop-filter` glassmorphism) belongs to `ui-ux-pro-max`. The disambiguating prefix in its description exists precisely to stop that misroute.

### `foundation-models-on-device` — Apple on-device LLM

**Trigger**: using the on-device model on iOS 26+ for generation, guided output, or tool calling

Sessions and `respond`, `@Generable`/`@Guide` guided generation (typed structures straight out), the `Tool` protocol (`Arguments` / `Output` associated types; `call(arguments:)` returns `Output` directly, anything `PromptRepresentable` works), and `ResponseStream` snapshot streaming (the iterated element is a snapshot — read `.content`).

> **Note**: a top-level `ToolOutput` type existed only in early iOS 26 seeds and is not in the shipping SDK (`Transcript.ToolOutput` is an unrelated struct). All 8 code blocks were run through `swiftc -typecheck` against the local Xcode 26.6 SDK — zero errors, zero warnings.

---

## web

TypeScript/Node web stack, with responsibilities split cleanly: Dockerfile detail belongs to `docker-patterns`, release strategy to `deployment-patterns`.

### `api-design` — REST API decisions

**Trigger**: designing or reviewing REST endpoints, deciding status codes / pagination / versioning

Resource naming, status code selection (**422 with field-level error detail**, **201 with a `Location` header**), offset vs cursor pagination trade-offs, filter parameter design, versioning strategy, rate-limit patterns. One TypeScript/Next.js reference implementation carries the full schema-validation → 422 → 201 chain; the shape transfers to any stack.

### `docker-patterns` — Docker and Compose

**Trigger**: writing Dockerfiles or compose files, hardening images, debugging container networking and volumes

Dev vs prod Dockerfile split, image hardening, Compose networking and volume strategy, multi-service orchestration. Two things worth the read on their own:

- `depends_on: condition: service_healthy` gates startup order on the healthcheck — bare `depends_on` waits for the container to **start**, not for the service to be **ready**
- an anonymous `/app/node_modules` volume stops a host bind-mount from shadowing the dependencies installed inside the container

### `deployment-patterns` — Everything outside the image

**Trigger**: planning a release, setting up CI/CD, preparing a rollback

Rolling / blue-green / canary trade-offs, CI/CD pipeline patterns, health endpoints and the k8s liveness / readiness / startup probe split, Zod fail-fast env validation, per-platform rollback commands, pre-launch checklist. Dockerfile questions route to `docker-patterns`.

### `mcp-server-patterns` — Building MCP servers

**Trigger**: writing, extending or debugging an MCP server

Tools / resources / prompts as three ways to expose capability, Zod argument validation, stdio vs Streamable HTTP transport selection, common registration and debugging problems. Latest API detail is looked up through Context7 or the official docs rather than hardcoded.

### `bun-runtime` — When to use Bun instead of Node

**Trigger**: choosing a runtime or migrating to Bun

Maturity and fit for each of Bun's four roles (runtime, package manager, bundler, test runner), migration notes from Node, current Vercel support.

### `content-hash-cache-pattern` — Content-hash caching

**Trigger**: caching expensive file-processing results (PDF parsing, OCR, text extraction, image analysis)

Key on the SHA-256 of file content rather than the path, composed with the processor version and its config: the cache survives moves and renames, and invalidates itself both when content changes and when the extractor does. A service-layer split keeps it invisible to calling code. Fits recurring heavy processing across runs.

---

## data

### `database-migrations` — Zero-downtime schema changes + PG quick reference

**Trigger**: writing SQL or migrations, designing schemas and indexes, chasing slow queries, implementing RLS

Expand-contract zero-downtime pattern, `CREATE INDEX CONCURRENTLY`, forward-only discipline, across native PostgreSQL / Prisma / Drizzle / Kysely / Alembic.

**The Alembic section is mostly pitfalls**: autogenerate reads a rename as drop+add (data loss — hand-write `op.rename_table`), misses ENUM value additions and views/triggers, `CONCURRENTLY` needs an `autocommit_block`, heads must stay unique.

**PostgreSQL appendix**: index selection by query shape (B-tree / GIN / BRIN), UPSERT, cursor pagination, `FOR UPDATE SKIP LOCKED` queues, wrapping `auth.uid()` in a SELECT for RLS performance, slow-query and bloat diagnostics.

> **Note**: the Django and golang-migrate sections were cut — not stacks in use here.

### `data-scraper-agent` — Zero-cost scheduled collection agent

**Trigger**: building a free automated pipeline to monitor or collect any public data (jobs, prices, news, GitHub, scores…)

GitHub Actions cron + Gemini free tier for extraction, landing in Notion / Sheets / Supabase, with a feedback loop to improve over time. A 764-line implementation guide, not a sketch. The model fallback chain is four verified IDs: `gemini-2.5-flash-lite` → `gemini-3.5-flash-lite` → `gemini-2.5-flash` → the `flash-latest` alias as a backstop.

> **Note**: the gemini-2.0 family is officially marked Shut down; Google no longer publishes fixed free-tier quotas, so the doc points at the AI Studio dashboard instead of hardcoding numbers.

---

## quality

Code quality, testing and review. `santa-method` is the third most-used skill in the repo.

### `santa-method` — Multi-agent adversarial verification

**For**: two mutually blind reviewers must both pass before anything ships.
**Trigger**: high-confidence deliverables, or when you ask for something to be verified before you see it

Two independent review agents run in parallel on the same review prompt, **neither aware the other exists**. Both must pass; if either fails, the fix goes into the next round — and that round must use brand-new agents, which is the point: it removes "it approved this last time" anchoring.

> **Division of labour**: deterministic checks (build / lint / test) run first and belong to `tdd-workflow`; santa judges only the semantic layer — accuracy, hallucination, omission.

### `tdd-workflow` — Test-driven development discipline

**Trigger**: writing new features, fixing bugs, refactoring

The core is the **RED gate anti-cheat**: while the test is red, no refactoring and no "just tweak the implementation until it passes" — the test must first fail for the *right reason*, then comes the minimal implementation. Vertical slices (one thin end-to-end user path) over horizontal layers. 80%+ coverage is a starting reference for new code, not dogma; after-the-fact regression coverage belongs to `ai-regression-testing`.

> **Note**: the Jest config key is `coverageThreshold` (singular) — pluralising it makes the coverage gate silently do nothing. The example domain objects come from an upstream project; swap in your own.

### `e2e-testing` — Playwright end-to-end

**Trigger**: writing or maintaining E2E tests, or when tests flip red and green

Page Object Model for structure; tracing via the config option `use: { trace: 'on-first-retry' }` (preferred over manual `context.tracing` calls); video via `use: { video: 'retain-on-failure' }`; CI artifact handling.

**The flakiness insight**: the race is almost never the click — both click APIs auto-wait. It's the assertion taking a one-shot snapshot. Use auto-retrying web-first assertions like `expect(locator).toHaveText()` instead of reading `textContent()` and then asserting on it.

### `ai-regression-testing` — Regression strategy for AI blind spots

**Trigger**: adding regression coverage after AI-assisted development, or worrying that the model reviewing the code is the one that wrote it

Sandbox-mode API tests with no database dependency, and a reusable `createTestRequest` harness for automated bug-checks. Opinionated: chase real bugs, not a coverage percentage. Backed by a full real case — four consecutive rounds of regressions on `notification_settings`.

### `click-path-audit` — Trace every button through its state chain

**Trigger**: systematic debugging found nothing but users still report broken buttons; or after a big refactor touched shared state

Map every user-reachable button/touchpoint from click to final state as a full sequence, and look for state updates that cancel each other out, wrong final states, and inconsistent UI leftovers — the class of bug where each function is individually correct. A complement to `diagnose`, not a replacement.

### `security-checklist` — Security review checklist

**Trigger**: adding auth, handling user input, touching secrets, exposing APIs, building payment/sensitive features

Checklists and right/wrong code pairs across authentication, input validation, secrets management, API security and OWASP staples. For example, Solana signature verification uses tweetnacl's `nacl.sign.detached.verify` with `bs58.decode(publicKey)` — Solana public keys are base58, not base64.

> **Note**: this is a **checklist reference**, a different thing from the built-in `/security-review` command — which is why it was renamed away from `security-review`.

### `security-scan` — Scan your own `.claude/` config

**Trigger**: after changing hooks / MCP / agent config, or as a periodic check-up

Runs AgentShield over CLAUDE.md, settings.json, MCP server definitions, hooks and agent definitions for injection risk and misconfiguration — **the AI config is itself an attack surface**. Full v1.4.0 capability: `--baseline` + `--gate` as a PR security gate (fails on new critical/high), `--supply-chain` to verify MCP package provenance, a PreToolUse runtime monitor for live interception, SARIF output for GitHub code scanning.

### `plankton-code-quality` — Write-time quality enforcement

**Trigger**: when you want validation on every edit (requires installing Plankton first)

A PostToolUse hook runs the per-language formatter and linter (biome / ruff / hadolint …) after every file edit, and spawns a Claude sub-process to fix whatever the agent didn't catch.

> **Prerequisite**: install manually from `github.com/alexfazio/plankton` — read the code before installing.

---

## code-review

Multi-language code review with auto-dispatch. One command (`/code-review`) detects which languages changed, runs the matching specialist agents in parallel, and always adds a security pass.

**Command:**
- **`/code-review`** — review local uncommitted changes, or `/code-review <pr>` for a GitHub PR (fetch diff, validate, post review)

**Agents (5):**
- **`code-reviewer`** — general-purpose fallback when no language specialist matches
- **`python-reviewer`** — PEP 8, Pythonic idioms, type hints, security (bandit), Django/FastAPI/Flask patterns
- **`typescript-reviewer`** — type safety, async correctness, React/Next.js patterns, Node security
- **`swift-reviewer`** — Swift 6 concurrency, value types, actor patterns, SwiftUI, Keychain/ATS security
- **`security-reviewer`** — OWASP Top 10, secrets detection, injection, unsafe crypto. **Always runs**, regardless of language

---

## research

### `search-routing` — The router for every web search

**For**: picking one search MCP by query shape — the cheapest one that suffices.
**Trigger**: when multiple search MCPs are available, **before making any web search call**

Decision order, top down:

0. Known URL → fetch it, don't search (JS-heavy / paywalled / needs rendering → `firecrawl_scrape`)
1. Operator-laden or domain-targeted (`site:`, quoted phrases) → firecrawl — **exa is a neural index and ignores operators**
2. Chinese-language SERPs → firecrawl, which reaches them better than exa's neural index
3. Pricing / paywalled / premium publisher data → linkup standard (content-licensing deals with Statista, Xerfi and others)
4. Library and API docs → **Context7 first**, fall back to exa only if it returns nothing relevant
5. Everything else → exa
6. Deep modes (~10× cost) → **always ask first**, stating the reason and the per-call price

Ships with a cost table and the verified exa tool signatures — the installed server exposes exactly `web_search_exa` and `web_fetch_exa`.

> **Retrieval heuristic worth stealing**: the first search round is often you learning the project's own vocabulary. "rate limit" finds nothing because the codebase calls it "throttle".

### `research` — Multi-source deep research

**For**: plan → collect → deep-read → synthesize with citations. Fourth most-used skill.
**Trigger**: asking for thorough research on a topic, or a report with evidence

Decomposes the research question, then follows a scenario-specific collection checklist:

- **Investor due diligence** — fund size / stage / check size / portfolio / red flags
- **Competitor analysis** — the shipped product rather than the marketing copy, funding history, pricing signals
- **Market sizing** — top-down and bottom-up cross-validated
- **Vendor evaluation** — trade-offs, lock-in, compliance

Searches with `web_search_exa`, deep-reads with `web_fetch_exa` or `firecrawl_scrape` (JS-heavy / paywalled), and synthesizes a cited report under explicit quality rules.

> **Check the backends exist before planning around them.** MCP servers are scoped per config directory, so `exa` / `firecrawl` / `linkup` can be present in one session and absent in another. The skill now verifies first and falls back to the bundled `/deep-research` workflow or built-in `WebSearch` — naming which backend it used — instead of running searches with nothing to call.

### `llm-cost-discipline` — Two layers of LLM cost control

**Trigger**: building an LLM pipeline, controlling API cost, or deciding between regex and an LLM for structured text

- **Layer 1 · avoid the call**: parse structured text with regex first, flagging low-confidence items with a fixed deduction system — **only items with a detected reason escalate to an LLM**, ordered by severity so the escalation fits a budget cap. Backed by results across 410 real samples.
- **Layer 2 · make the call cheaper**: route model tier by task size (cheap / strong tier constants), with an immutable CostTracker billing from `response.usage` in real time.

> **Pricing rule**: always look it up (the `claude-api` skill or the official pricing page); never hardcode a price into the doc — a hardcoded price is wrong within six months.

---

## skills

Skill self-management. Originally 13; the 10 instinct-related ones were deleted because the CLI and data they depended on never existed.

### `skill-stocktake` — Audit skill quality

**Trigger**: taking stock of skill/command quality

Two modes: Quick Scan looks only at recently changed skills, Full Stocktake walks everything; a quality checklist plus sequential sub-agent batch evaluation produces the verdict. `scan.sh` derives the repo root from its own location and walks the full `plugins/*/skills/*/SKILL.md` set.

### `skill-comply` — Verify skills are actually followed

**For**: written ≠ in effect — prove it with real run data.
**Trigger**: when you suspect a skill or rule is decorative

Runs target scenarios through the `claude` CLI (auto-generating prompts at 3 strictness levels), parses the stream-json output, and pairs "rule that should have fired" against "what actually happened", producing a compliance report with full tool-call timelines.

> **Note**: the only skill here with its own runnable test suite (uv + pytest); the stream-json pairing algorithm is genuine integration knowledge.

### `rules-distill` — Distill cross-cutting principles into rules

**Trigger**: when several skills keep repeating the same principle

`scan-skills.sh` walks every skill and extracts candidate principles as valid JSON (verified runnable); cluster them and promote the cross-cutting ones into rules files — appending, revising or creating. A missing `~/.claude/rules` is treated as "no existing rules" and distillation proceeds; it isn't a failure.

---

## business

### `investor-materials` — Full fundraising material set

**Trigger**: building a pitch deck, one-pager, investor memo, accelerator application, financial model, or investor outreach

Guidance for deck structure, one-pagers, memos, financial models, use-of-funds tables and milestone plans — kept numerically consistent across every asset. The outreach section is deliberately reduced to two hard numbers:

- **Follow-up cadence**: day 0 outbound → day 4–5 short follow-up **with one new data point** → day 10–12 final follow-up with a clean close, then stop
- **Warm intros**: keep the forwardable blurb under 100 words so it can be passed along as-is

---

## codex

Second opinion via Codex MCP — read-only sandbox, approvals off, **never edits**. The two split cleanly: one hunts bugs, one questions the direction.

### `codex-review` — Default code review route

**Trigger**: say code review / 审一下 / second opinion / take a look at this change

Runs the multi-language review methodology through `mcp__codex__codex` on a different model: severity matrix, `file:line` anchors, scope triage, mandatory security pass. Three-way routing:

- default here — the whole point is an **outside** opinion
- inline PR comments (`--comment`) or auto-applied fixes (`--fix`) → the built-in `/code-review`
- specifically want Claude language subagents → the `code-review` plugin

### `design-challenge` — Question the approach, not the code

**Trigger**: say challenge this design / punch holes in this / is this the right approach

Hands a formed proposal to Codex for a single-pass attack, returning **implicit assumptions / failure modes / alternatives** — explicitly not a bug list, and no severity matrix.

> **Division of labour**: want to be grilled question-by-question → `grill-with-docs`; want an external model to punch through a finished proposal in one pass → this one.

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

Most skills auto-trigger from natural language matching their description — the **Trigger** line on each skill above is its real matching surface. A few are explicit-invocation only (`caveman`, `/cpr`, `/code-review`), deliberately so.

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- GitHub CLI (`gh`) for the `cpr` workflow
- Feishu MCP server for the `feishu` skill
- Codex CLI + MCP server for the `codex` plugin
- A Python venv for the `pdf` / `cheatsheet` / `ui-ux-pro-max` / `skill-comply` scripts
- Various API keys depending on skill (Exa, firecrawl, linkup, Context7, Gemini, ElevenLabs, fal.ai, …)

## License

MIT
