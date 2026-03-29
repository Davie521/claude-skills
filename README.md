# Claude Skills

A collection of Claude Code plugins for development workflow automation, writing assistance, and productivity tools.

## Plugins

### dev-workflow

Automated development workflows for Claude Code.

#### `/cpr` — Git PR Pipeline

One command to go from local changes to a merged-ready PR. Claude automatically:

1. Detects current git state (uncommitted changes, existing PR, CI status)
2. Commits and pushes code, creates a PR via `gh`
3. Watches CI checks with `gh pr checks --watch`
4. On failure: reads error logs, fixes code, pushes again
5. On pass: reviews Copilot comments, fixes real issues (ignores false positives)
6. Loops steps 3-5 until everything is green

No manual intervention needed — just type `/cpr` and walk away.

#### `/cl` — Copilot Lint Review

Focused CI + Copilot code review workflow. Unlike `/cpr`, this doesn't create PRs — it reviews an existing one:

- Checks CI status and fixes build/lint failures locally
- Pulls Copilot review comments from the PR
- **Critically evaluates each suggestion** — only fixes real bugs, security issues, and meaningful improvements
- Ignores over-defensive suggestions, false positives, and style-only nitpicks
- Loops until CI passes and all valid comments are addressed

#### `/impl` — Multi-Agent Implementation

Orchestrates a team of specialized agents for larger features:

| Phase | Agent | What it does |
|-------|-------|-------------|
| 0 | **Planner** | 2-3 rounds of plan iteration in plan mode before any code is written |
| 1 | **Implementer** | Writes code in an isolated git worktree following the plan |
| 2 | **Reviewer** | Code review against plan, coding standards, security, a11y |
| 3 | **Tester** | Runs tests, Playwright screenshots, fixes bugs on the spot |
| 4 | **Reviewer** | Final review of test fixes |
| 5 | **Wrap-up** | Clean commit history, create feature branch and PR |

Each agent completes → gets reviewed → issues fixed → next agent starts.

#### `browser` — Browser MCP Routing

Automatically selects the right browser tool based on your intent:

| Intent | MCP Selected |
|--------|-------------|
| Browse, fill forms, open pages | **browser-use** (Agent Browser) |
| Performance, debugging, network, console | **Chrome DevTools** |
| E2E testing, full flow testing | **Playwright** |

---

### writing

#### `vibe-writing` — AI Writing Assistant

A 4-phase co-writing workflow where you lead, AI assists:

| Phase | Trigger | What happens |
|-------|---------|-------------|
| **Learn** | Default entry | Socratic dialogue — AI asks probing questions, every 4 rounds generates a knowledge card (core insight + evidence + quotes) |
| **Structure** | Say "structure" | Aggregates cards, proposes 2-3 article structures (problem-solution, comparison, progressive, story, listicle, SCQA) |
| **Write** | Say "write" / "iterate" | Say "organize" to consolidate, "polish" to fact-check and refine language |
| **Finalize** | Say "finalize" | Chains all output cards + transitions + intro/conclusion into a complete article |

Start from any phase depending on how much you already have.

---

### document

#### `cheatsheet` — Printable A4 Cheatsheet Creator

Creates dense, exam-ready cheatsheets from Markdown:

- **A4 landscape**, 5-column layout, 6pt font — maximum information density
- Supports LaTeX math formulas, tables, highlighted blocks, notes
- Multi-page output for larger topics
- Pipeline: write Markdown → `python3 md2html.py input.md` → open HTML → print to PDF

---

### work-tools

#### `feishu` — Feishu/Lark Integration

Operates Feishu (Lark) via MCP server:

- Send messages to users or groups
- Create group chats
- Create and edit documents
- Upload files
- Query user information

Requires a Feishu MCP server to be configured.

## Installation

Install individual plugins via Claude Code CLI:

```bash
# Install all plugins from this marketplace
claude plugins add Davie521/claude-skills dev-workflow
claude plugins add Davie521/claude-skills writing
claude plugins add Davie521/claude-skills document
claude plugins add Davie521/claude-skills work-tools
```

## Usage

After installation, simply type the command in Claude Code:

```
> /cpr          # Push code through full PR pipeline
> /cl           # Review and fix Copilot lint comments
> /impl         # Multi-agent coordinated implementation
> write an article about...   # Triggers vibe-writing
> create a cheatsheet for...  # Triggers cheatsheet
```

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- GitHub CLI (`gh`) for cpr/cl workflows
- Browser MCP servers for browser skill (see skill docs for setup)
- Feishu MCP server for feishu skill

## License

MIT
